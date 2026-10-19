#!/usr/bin/env python3
"""
xclip_overlay_v11_colonial.py  (derived from xclip_overlay_v10; v10 is left untouched)

v11 changes (detector / tracker / X-CLIP scoring logic is UNCHANGED from v10):
  * wall-clock aware: --session-start + chunk number -> clock time of every frame
    (verified from the on-screen clock: .001=00:00, .008=07:00, .025=next day 00:00)
  * every counted track is assigned to a 15-minute bin (by its midpoint frame)
  * annotated video is split into one clip per 15-min bin (tracking itself is NOT cut)
  * outputs go to <out-root>/{counts,annotated,logs}/<run>/ ; nothing is overwritten
    (an existing file gets _v2, _v3 ... instead)
  * per-bin CSV, per-track CSV and a JSON run log are written for the aggregator

X-CLIP classification of people tracked with your FINE-TUNED RT-DETR
(replaces YOLO from v2), plus ID stitching so a standing pedestrian keeps one id.

Detector: RT-DETR (rtdetr_v3 best.pt). Classes are looked up by NAME from the
model, so class order doesn't matter:
  person + cyclist  -> "people" (one shared tracker, X-CLIP decides the label;
                        the detector's own cyclist fraction is logged only as a
                        sanity check, it does not vote)
  car/bus/truck/other_vehicle -> vehicles (own tracker, running count)

Tracking: supervision ByteTrack with a long lost_track_buffer (same idea as your
Method J config), then an ID stitcher: when a brand-new track id appears within
--stitch-sec seconds and --stitch-px pixels of where a now-absent person track
was last seen, it inherits the old id (and therefore its crop buffer + X-CLIP
history). This is what stops a standing person from getting a new id.

X-CLIP scoring/counting is unchanged from v2.
"""
import argparse
import csv
import datetime
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from collections import defaultdict, deque

import cv2
import numpy as np
import supervision as sv
import torch
from transformers import XCLIPModel, XCLIPProcessor

MODEL_NAME = "microsoft/xclip-base-patch32"
N_FRAMES = 8
CLASSES = [("BICYCLIST", (0, 200, 0)), ("PEDESTRIAN", (0, 140, 255))]
PEOPLE_NAMES = {"person", "cyclist"}
VEHICLE_NAMES = {"car", "bus", "truck", "other_vehicle"}
VEH_COLOR = (255, 120, 0)
HEADER_COLOR = (0, 255, 255)


def parse_zone(spec, sx=1.0, sy=1.0):
    """'x1,y1;x2,y2;x3,y3;...' -> int32 Nx2 array (scaled by sx,sy), or None."""
    if not spec:
        return None
    pts = [tuple(map(float, p.split(","))) for p in spec.split(";") if p.strip()]
    if len(pts) < 3:
        sys.exit("ERROR: a zone needs at least 3 points")
    return np.array([(x * sx, y * sy) for x, y in pts]).round().astype(np.int32)


def draw_zones(img, zones, alpha=0.07):
    """zones: list of (poly, BGR color, label). Faint fill + outline."""
    ov = img.copy()
    for poly, col, _ in zones:
        cv2.fillPoly(ov, [poly], col)
    cv2.addWeighted(ov, alpha, img, 1 - alpha, 0, img)
    for poly, col, label in zones:
        cv2.polylines(img, [poly], True, col, 2)
        x, y = poly[:, 0].min(), poly[:, 1].min()
        cv2.putText(img, label, (int(x) + 6, int(y) + 22), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, col, 2, cv2.LINE_AA)


def in_zone(xyxy, poly):
    if poly is None or len(xyxy) == 0:
        return np.ones(len(xyxy), dtype=bool)
    gx = (xyxy[:, 0] + xyxy[:, 2]) / 2.0
    gy = xyxy[:, 3]  # bottom-center = where the object touches the ground
    return np.array([cv2.pointPolygonTest(poly, (float(x), float(y)), False) >= 0
                      for x, y in zip(gx, gy)])


def iou_matrix(a, b):
    """a: (N,4), b: (M,4) xyxy -> (N,M) IoU."""
    if len(a) == 0 or len(b) == 0:
        return np.zeros((len(a), len(b)))
    x1 = np.maximum(a[:, None, 0], b[None, :, 0]); y1 = np.maximum(a[:, None, 1], b[None, :, 1])
    x2 = np.minimum(a[:, None, 2], b[None, :, 2]); y2 = np.minimum(a[:, None, 3], b[None, :, 3])
    inter = np.clip(x2 - x1, 0, None) * np.clip(y2 - y1, 0, None)
    aa = (a[:, 2] - a[:, 0]) * (a[:, 3] - a[:, 1]); ab = (b[:, 2] - b[:, 0]) * (b[:, 3] - b[:, 1])
    return inter / (aa[:, None] + ab[None, :] - inter + 1e-9)


def drop_contained(xyxy, thr):
    """Boolean keep-mask: drop a box if >= thr of its area lies inside a clearly larger box
    (e.g. a rider-only box inside a rider+bike box)."""
    n = len(xyxy)
    keep = np.ones(n, dtype=bool)
    if n < 2 or thr <= 0:
        return keep
    area = (xyxy[:, 2] - xyxy[:, 0]) * (xyxy[:, 3] - xyxy[:, 1])
    x1 = np.maximum(xyxy[:, None, 0], xyxy[None, :, 0]); y1 = np.maximum(xyxy[:, None, 1], xyxy[None, :, 1])
    x2 = np.minimum(xyxy[:, None, 2], xyxy[None, :, 2]); y2 = np.minimum(xyxy[:, None, 3], xyxy[None, :, 3])
    inter = np.clip(x2 - x1, 0, None) * np.clip(y2 - y1, 0, None)
    frac_of_i = inter / np.maximum(area[:, None], 1e-9)          # share of box i inside box j
    bigger = area[None, :] > 1.15 * area[:, None]                # j clearly larger than i
    keep[((frac_of_i >= thr) & bigger).any(axis=1)] = False
    return keep


def init_flow(prev_gray, box):
    """Pick feature points inside `box` (cx,cy,w,h) so the box can be followed by optical flow."""
    cx, cy, w, h = box
    Hh, Ww = prev_gray.shape
    x1, y1 = max(0, int(cx - w / 2)), max(0, int(cy - h / 2))
    x2, y2 = min(Ww, int(cx + w / 2)), min(Hh, int(cy + h / 2))
    if x2 - x1 < 4 or y2 - y1 < 4:
        return None
    mask = np.zeros_like(prev_gray)
    mask[y1:y2, x1:x2] = 255
    pts = cv2.goodFeaturesToTrack(prev_gray, 40, 0.01, 3, mask=mask)
    if pts is None or len(pts) < 4:
        return None
    return {"pts": pts.astype(np.float32), "box": np.array([cx, cy, w, h], dtype=float)}


def flow_step(prev_gray, gray, st):
    """Move the coasting box by the median optical-flow shift of its points. False = lost it."""
    pts = st["pts"]
    nxt, ok_, _ = cv2.calcOpticalFlowPyrLK(prev_gray, gray, pts, None, winSize=(21, 21), maxLevel=3)
    if nxt is None:
        return False
    good = ok_.ravel() == 1
    if good.sum() < 4:
        return False
    st["box"][:2] += np.median((nxt - pts)[good].reshape(-1, 2), axis=0)
    st["pts"] = nxt[good].reshape(-1, 1, 2).astype(np.float32)
    return True


def crop_square(frame, cx, cy, w, h, pad, out=224):
    H, W = frame.shape[:2]
    side = max(max(w, h) * (1 + pad), 48)
    x1, y1 = max(0, int(cx - side / 2)), max(0, int(cy - side / 2))
    x2, y2 = min(W, int(cx + side / 2)), min(H, int(cy + side / 2))
    crop = frame[y1:y2, x1:x2]
    if crop.size == 0:
        return None
    return cv2.resize(crop, (out, out), interpolation=cv2.INTER_CUBIC)


def _tag(img, x1, y, text, fs, thick, color):
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, fs, thick)
    cv2.rectangle(img, (x1, y - th - 3), (x1 + tw + 4, y + 3), (0, 0, 0), -1)
    cv2.putText(img, text, (x1 + 2, y), cv2.FONT_HERSHEY_SIMPLEX, fs, color, thick, cv2.LINE_AA)


def draw_person(img, box, tid, cls, probs, scale):
    cx, cy, w, h = box
    x1, y1, x2, y2 = int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2)
    thick = max(1, int(round(scale * 2)))
    if cls is None:
        color, lines = (255, 255, 255), [f"id {tid} ..."]
    else:
        color = CLASSES[cls][1]
        lines = [f"id {tid} {CLASSES[cls][0]} {probs[cls]:.2f}"]
        lines += [f"{c[0][:4].lower()} {p:.2f}" for c, p in zip(CLASSES, probs)]
    cv2.rectangle(img, (x1, y1), (x2, y2), color, thick)
    line_h = int(22 * scale) + 6
    y = max(line_h, y1 - 4 - line_h * (len(lines) - 1))
    for i, t in enumerate(lines):
        _tag(img, x1, y + i * line_h, t, scale * (0.7 if i == 0 else 0.5), thick,
             color if i == 0 else (255, 255, 255))


def draw_vehicle(img, box, tid, name, scale):
    cx, cy, w, h = box
    thick = max(1, int(round(scale * 2)))
    cv2.rectangle(img, (int(cx - w / 2), int(cy - h / 2)), (int(cx + w / 2), int(cy + h / 2)),
                  VEH_COLOR, thick)
    _tag(img, int(cx - w / 2), max(int(22 * scale), int(cy - h / 2) - 4), f"{name} {tid}",
         scale * 0.6, thick, VEH_COLOR)


def add_header(img, scale, counts, fi, total, clock="", binline=""):
    bar = int(100 * scale)
    out = cv2.copyMakeBorder(img, bar, 0, 0, 0, cv2.BORDER_CONSTANT, value=HEADER_COLOR)
    thick, fs = max(1, int(round(scale * 2))), scale * 0.7
    lines = [f"{clock}   |   frame {fi}/{total if total > 0 else '?'}",
             f"Running (whole chunk) - Bicyclists: {counts[0]}  Pedestrians: {counts[1]}  Vehicles: {counts[2]}",
             binline]
    for i, t in enumerate(lines):
        cv2.putText(out, t, (10, int(bar * (0.28 + 0.31 * i))), cv2.FONT_HERSHEY_SIMPLEX,
                    fs, (0, 0, 0), thick, cv2.LINE_AA)
    return out


def unique_path(path):
    """Never overwrite: if path exists, return path with _v2, _v3, ... before the extension."""
    if not os.path.exists(path):
        return path
    root, ext = os.path.splitext(path)
    k = 2
    while os.path.exists(f"{root}_v{k}{ext}"):
        k += 1
    return f"{root}_v{k}{ext}"


def finalize_clip(tmp, final):
    """Re-encode the mp4v temp clip to browser-playable H.264; keep mp4v if ffmpeg is unavailable."""
    if shutil.which("ffmpeg"):
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-c:v", "libx264",
                            "-pix_fmt", "yuv420p", "-crf", "23", "-preset", "fast", final],
                           capture_output=True)
        if r.returncode == 0 and os.path.exists(final):
            os.remove(tmp)
            return final
        print(f"WARNING: ffmpeg re-encode failed for {final}; keeping mp4v file")
    os.replace(tmp, final)
    return final


class IdStitcher:
    """New raw tracker id near a recently-vanished person track -> reuse the old id."""

    def __init__(self, max_gap, max_px):
        self.max_gap, self.max_px = max_gap, max_px
        self.map = {}    # raw id -> canonical id
        self.last = {}   # canonical id -> (frame, cx, cy)

    def resolve_frame(self, fi, dets):
        """dets: list of (raw, cx, cy, w, h). Returns list of (canon, cx, cy, w, h)."""
        out, active, new = [], set(), []
        for d in dets:
            if d[0] in self.map:
                c = self.map[d[0]]
                active.add(c)
                out.append((c,) + d[1:])
            else:
                new.append(d)
        for raw, cx, cy, w, h in new:
            best = None
            for c, (lf, lx, ly) in self.last.items():
                if c in active or not (0 < fi - lf <= self.max_gap):
                    continue
                d = math.hypot(cx - lx, cy - ly)
                if d <= max(self.max_px, 2 * max(w, h)) and (best is None or d < best[0]):
                    best = (d, c)
            c = best[1] if best else raw
            self.map[raw] = c
            active.add(c)
            out.append((c, cx, cy, w, h))
        for c, cx, cy, w, h in out:
            self.last[c] = (fi, cx, cy)
        return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--video", required=True)
    ap.add_argument("--out-root", required=True,
                    help="test_colonial root; writes counts/<run>/, annotated/<run>/<tag>/, logs/<run>/")
    ap.add_argument("--run", required=True, help="run name (sub-folder), e.g. colonial_run1")
    ap.add_argument("--session-start", default="2019-07-10 00:00:00",
                    help="wall-clock time at the start of chunk .001 (verified on-screen: 2019-07-10 12:00:00 AM)")
    ap.add_argument("--chunk-index", type=int, default=0,
                    help="hourly chunk number N (1-based). Default: parsed from the .NNN in the filename")
    ap.add_argument("--bin-minutes", type=int, default=15)
    ap.add_argument("--clock-note", default="session start verified from camera on-screen clock on chunks .001/.008/.025")
    ap.add_argument("--weights", required=True, help="fine-tuned RT-DETR best.pt")
    ap.add_argument("--veh-weights", default=None,
                    help="optional separate detector for vehicles (e.g. COCO rtdetr-l.pt); "
                         "if set, --weights is used for people only")
    ap.add_argument("--imgsz", type=int, default=1280)
    ap.add_argument("--det-conf", type=float, default=0.25)
    ap.add_argument("--track-thr", type=float, default=0.25, help="ByteTrack activation thr")
    ap.add_argument("--lost-sec", type=float, default=3.0, help="ByteTrack lost_track_buffer (s)")
    ap.add_argument("--stitch-sec", type=float, default=5.0)
    ap.add_argument("--stitch-px", type=float, default=150.0)
    ap.add_argument("--veh-min", type=int, default=15)
    ap.add_argument("--veh-min-disp", type=float, default=40.0,
                    help="min net centroid displacement (px) over the track life to count as a real vehicle, not a static object like a cone")
    ap.add_argument("--road-zone", default=None,
                    help='polygon "x1,y1;x2,y2;x3,y3;..." (pixel coords, original frame, before '
                         'the header bar) -- a vehicle only counts if its ground point (bottom-center '
                         'of its box) falls inside this polygon. Use extract_frame.py to grab a still '
                         'and read off corner coordinates. Leave unset to disable (no zone filtering).')
    ap.add_argument("--bike-zone", default=None,
                    help="bike-lane polygon (drawn for reference only, not used to filter)")
    ap.add_argument("--sidewalk-zone", default=None,
                    help="sidewalk polygon: vehicles whose ground point falls in it are dropped")
    ap.add_argument("--zone-ref-size", default=None,
                    help='"WxH" of the image the zone coords were picked on (e.g. 716x477); '
                         "polygons are scaled to the real video size. Omit if coords are already in video pixels.")
    ap.add_argument("--zones-json", default=None,
                    help="per-camera zone file: {\"ref_size\":[W,H], \"road\":[[x,y],..], \"bike\":[..], \"sidewalk\":[..]}. "
                         "Explicit --road-zone/--bike-zone/--sidewalk-zone flags override it.")
    ap.add_argument("--zone-alpha", type=float, default=0.07, help="zone fill opacity on the video (0=off)")
    ap.add_argument("--person-min-sec", type=float, default=3.0,
                    help="a person track must be visible this many seconds to be drawn-as-confirmed/counted")
    ap.add_argument("--person-min-conf", type=float, default=0.0,
                    help="min MEAN detector confidence over a person track (0=off; see track_stats.csv to pick a value)")
    ap.add_argument("--person-min-h", type=float, default=0.0,
                    help="min mean person box height as a fraction of frame height (0=off)")
    ap.add_argument("--veh-min-mean-conf", type=float, default=0.45,
                    help="min MEAN detector confidence over a vehicle track (lane markings/junk are usually low-conf)")
    ap.add_argument("--veh-aspect-min", type=float, default=0.35, help="min box w/h for a vehicle detection")
    ap.add_argument("--veh-aspect-max", type=float, default=4.5, help="max box w/h for a vehicle detection")
    ap.add_argument("--veh-imgsz", type=int, default=None,
                    help="inference size for the vehicle detector (default: same as --imgsz). Larger can split side-by-side cars.")
    ap.add_argument("--person-contain", type=float, default=0.7,
                    help="drop a person box if this fraction of it lies inside a clearly larger person box (0=off)")
    ap.add_argument("--coast-sec", type=float, default=2.0,
                    help="keep drawing a confirmed person box (followed by optical flow) this long after the detector loses it")
    ap.add_argument("--coast-min-sec", type=float, default=0.7,
                    help="a person track must have been seen this long before it is allowed to coast")
    ap.add_argument("--box-ema", type=float, default=0.5,
                    help="weight of the newest detection in the drawn person box (lower = steadier, 1 = raw)")
    ap.add_argument("--no-draw-zones", action="store_true", help="do not draw zones on the output video")
    ap.add_argument("--veh-min-straightness", type=float, default=0.35,
                    help="min (net displacement / total path length) -- filters jittering-in-place boxes; real driving is close to a straight line")
    ap.add_argument("--confirm", type=int, default=2)
    ap.add_argument("--window", type=int, default=30)
    ap.add_argument("--min-frames", type=int, default=8)
    ap.add_argument("--stride", type=int, default=3)
    ap.add_argument("--pad", type=float, default=0.6)
    ap.add_argument("--ema", type=float, default=0.5)
    ap.add_argument("--bike-prompts", nargs="+",
                    default=["a person riding a bicycle", "a person riding a bike on the road"])
    ap.add_argument("--walk-prompts", nargs="+",
                    default=["a person walking", "a person standing still"])
    ap.add_argument("--start-frame", type=int, default=1)
    ap.add_argument("--max-frames", type=int, default=0)
    args = ap.parse_args()

    if args.min_frames < 2 or args.min_frames > args.window:
        sys.exit("ERROR: need 2 <= --min-frames <= --window")

    nb = len(args.bike_prompts)
    prompts = list(args.bike_prompts) + list(args.walk_prompts)

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        sys.exit(f"ERROR: cannot open video {args.video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    W, H = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    scale = max(0.6, H / 1080.0 * 0.9)
    bar = int(100 * scale)

    t_start = time.time()
    tag = os.path.splitext(os.path.basename(args.video))[0]
    m_ = re.search(r"\.(\d{3})$", tag)
    chunk_idx = args.chunk_index or (int(m_.group(1)) if m_ else None)
    if chunk_idx is None:
        sys.exit("ERROR: cannot infer chunk number from filename; pass --chunk-index N")
    sess = datetime.datetime.strptime(args.session_start, "%Y-%m-%d %H:%M:%S")
    clip_t0 = sess + datetime.timedelta(hours=chunk_idx - 1)
    bin_sec = args.bin_minutes * 60
    bins_per_chunk = 3600 // bin_sec
    first_bin = (chunk_idx - 1) * bins_per_chunk
    last_bin = first_bin + bins_per_chunk - 1

    def clock_of(frame_idx):
        return clip_t0 + datetime.timedelta(seconds=(frame_idx - 1) / fps)

    def bin_of(frame_idx):
        b = int(((frame_idx - 1) / fps + (chunk_idx - 1) * 3600) // bin_sec)
        return min(max(b, first_bin), last_bin)   # the extra ~0.3 s of the hour stays in the last bin

    def bin_start(b):
        return sess + datetime.timedelta(seconds=b * bin_sec)

    cdir = os.path.join(args.out_root, "counts", args.run)
    adir = os.path.join(args.out_root, "annotated", args.run, tag)
    ldir = os.path.join(args.out_root, "logs", args.run)
    for d_ in (cdir, adir, ldir):
        os.makedirs(d_, exist_ok=True)
    base = os.path.join(cdir, tag)
    print(f"chunk {chunk_idx}: clip starts {clip_t0}  bins {first_bin}..{last_bin}  fps={fps:.3f}  {W}x{H}")

    from ultralytics import RTDETR
    det = RTDETR(args.weights)
    names = det.names
    people_ids = [i for i, n in names.items() if n in PEOPLE_NAMES]
    veh_ids = [i for i, n in names.items() if n in VEHICLE_NAMES]
    cyc_ids = {i for i, n in names.items() if n == "cyclist"}
    print(f"detector classes: {names}\n people={people_ids} vehicles={veh_ids}")
    if not people_ids:
        sys.exit("ERROR: no person/cyclist class in detector names")

    vdet, vnames = None, names
    coco_person_ids = []
    fallback_person_id = next(i for i, n in names.items() if n == "person") if "person" in names.values() else people_ids[0]
    if args.veh_weights:
        vdet = RTDETR(args.veh_weights)
        vnames = vdet.names
        veh_ids = [i for i, n in vnames.items() if n in {"car", "bus", "truck"}]  # no motorcycle: was mislabeling the cyclist
        coco_person_ids = [i for i, n in vnames.items() if n == "person"]
        print(f"vehicle detector classes used: {[vnames[i] for i in veh_ids]}")

    def make_tracker():
        return sv.ByteTrack(track_activation_threshold=args.track_thr,
                            lost_track_buffer=int(fps * args.lost_sec),
                            minimum_matching_threshold=0.8, frame_rate=int(round(fps)))

    ptrack, vtrack = make_tracker(), make_tracker()
    if args.zones_json:
        zj = json.load(open(args.zones_json))
        _s = lambda k: ";".join(f"{x},{y}" for x, y in zj[k]) if zj.get(k) else None
        args.road_zone = args.road_zone or _s("road")
        args.bike_zone = args.bike_zone or _s("bike")
        args.sidewalk_zone = args.sidewalk_zone or _s("sidewalk")
        if not args.zone_ref_size and zj.get("ref_size"):
            args.zone_ref_size = f"{zj['ref_size'][0]}x{zj['ref_size'][1]}"
        print(f"zones loaded from {args.zones_json}")
    sx = sy = 1.0
    if args.zone_ref_size:
        rw, rh = map(float, args.zone_ref_size.lower().split("x"))
        sx, sy = W / rw, H / rh
        print(f"zone coords scaled from {args.zone_ref_size} to {W}x{H} (x{sx:.3f}, y{sy:.3f})")
    road_poly = parse_zone(args.road_zone, sx, sy)
    bike_poly = parse_zone(args.bike_zone, sx, sy)
    side_poly = parse_zone(args.sidewalk_zone, sx, sy)
    if road_poly is not None:
        print("road zone active: vehicles outside it are dropped")
    if side_poly is not None:
        print("sidewalk zone active: vehicles inside it are dropped")
    zone_draw = [(p, c, l) for p, c, l in [(road_poly, (0, 200, 0), "ROAD"),
                                           (bike_poly, (0, 200, 255), "BIKE LANE"),
                                           (side_poly, (255, 0, 200), "SIDEWALK")] if p is not None]
    stitch = IdStitcher(int(fps * args.stitch_sec), args.stitch_px)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading {MODEL_NAME} on {device} ...")
    processor = XCLIPProcessor.from_pretrained(MODEL_NAME)
    model = XCLIPModel.from_pretrained(MODEL_NAME).to(device).eval()

    buffers = defaultdict(lambda: deque(maxlen=args.window))
    last_scored, smooth, streak = {}, {}, {}
    prob_sum, prob_n = defaultdict(lambda: np.zeros(2)), defaultdict(int)  # running mean per track, drives both the header and the final tally
    track_len, cyc_frames = defaultdict(int), defaultdict(int)
    first_fi, last_fi, zone_hits = {}, {}, defaultdict(lambda: [0, 0])   # zone_hits: [bike, sidewalk] frames
    veh_first_fi, veh_last_fi = {}, {}
    veh_len, veh_counted = defaultdict(int), set()
    veh_first_xy, veh_max_disp = {}, defaultdict(float)
    veh_last_xy, veh_path_len = {}, defaultdict(float)
    det_hist = defaultdict(int)   # detector class name -> raw detections over the video
    score_log = []
    pconf_sum, pconf_n, ph_sum = defaultdict(float), defaultdict(int), defaultdict(float)
    veh_conf_sum = defaultdict(float)

    sbox, last_seen = {}, {}
    coast_state, coast_dead = {}, set()
    frame_rec = {}      # frame idx -> what to draw; rendered in a 2nd pass once final decisions exist
    prev_gray = None
    prob_w, prob_wn, bike_hi = defaultdict(lambda: np.zeros(2)), defaultdict(float), defaultdict(int)

    def wmean(t):   # box-height-weighted mean: big/close crops count more than tiny far ones
        return prob_w[t] / prob_wn[t]
    coast_frames = int(args.coast_sec * fps)

    def person_ok(tid, need_len=True):
        n = track_len[tid]
        if n == 0:
            return False
        if need_len and n < args.person_min_sec * fps:
            return False
        if pconf_n[tid] and pconf_sum[tid] / pconf_n[tid] < args.person_min_conf:
            return False
        return ph_sum[tid] / n >= args.person_min_h * H

    zprev = base + "_zones_preview.png"
    fi = 0
    if args.start_frame > 1:
        cap.set(cv2.CAP_PROP_POS_FRAMES, args.start_frame - 1)
        fi = args.start_frame - 1
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        fi += 1
        if args.max_frames and fi > args.max_frames:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        r = det.predict(frame, conf=args.det_conf, imgsz=args.imgsz, verbose=False, device=device)[0]
        xyxy = r.boxes.xyxy.cpu().numpy() if len(r.boxes) else np.zeros((0, 4))
        conf = r.boxes.conf.cpu().numpy() if len(r.boxes) else np.zeros(0)
        cls = r.boxes.cls.int().cpu().numpy() if len(r.boxes) else np.zeros(0, dtype=int)

        for c_ in cls.tolist():
            det_hist[names[c_]] += 1

        if vdet is not None:
            rv = vdet.predict(frame, conf=args.det_conf, imgsz=args.veh_imgsz or args.imgsz, verbose=False, device=device)[0]
            n = len(rv.boxes)
            vxyxy = rv.boxes.xyxy.cpu().numpy() if n else np.zeros((0, 4))
            vconf = rv.boxes.conf.cpu().numpy() if n else np.zeros(0)
            vcls = rv.boxes.cls.int().cpu().numpy() if n else np.zeros(0, dtype=int)
        else:
            vxyxy, vconf, vcls = xyxy, conf, cls

        # ensemble: merge fine-tuned person/cyclist boxes with COCO "person" boxes into
        # ONE set of person candidates, then NMS across sources so a single person never
        # reaches the tracker as two simultaneous boxes (that was causing id churn).
        pm = np.isin(cls, people_ids)
        p_xyxy, p_conf, p_cls = xyxy[pm], conf[pm], cls[pm]
        if vdet is not None and coco_person_ids:
            cm = np.isin(vcls, coco_person_ids)
            c_xyxy, c_conf = vxyxy[cm], vconf[cm]
            c_cls = np.full(len(c_xyxy), fallback_person_id, dtype=int)
            p_xyxy = np.concatenate([p_xyxy, c_xyxy]) if len(p_xyxy) or len(c_xyxy) else p_xyxy
            p_conf = np.concatenate([p_conf, c_conf]) if len(p_conf) or len(c_conf) else p_conf
            p_cls = np.concatenate([p_cls, c_cls]) if len(p_cls) or len(c_cls) else p_cls
        if len(p_xyxy) > 1:
            kc = drop_contained(p_xyxy, args.person_contain)
            p_xyxy, p_conf, p_cls = p_xyxy[kc], p_conf[kc], p_cls[kc]
        if len(p_xyxy) > 1:
            order = np.argsort(-p_conf)
            keep = []
            ious = iou_matrix(p_xyxy, p_xyxy)
            suppressed = np.zeros(len(p_xyxy), dtype=bool)
            for i in order:
                if suppressed[i]:
                    continue
                keep.append(i)
                suppressed |= ious[i] > 0.4
                suppressed[i] = False
            keep = sorted(keep)
            p_xyxy, p_conf, p_cls = p_xyxy[keep], p_conf[keep], p_cls[keep]
        non_people = ~np.isin(cls, people_ids)
        xyxy = np.concatenate([xyxy[non_people], p_xyxy])
        conf = np.concatenate([conf[non_people], p_conf])
        cls = np.concatenate([cls[non_people], p_cls])

        def run(tracker, keep, xyxy, conf, cls, zone=None, exclude=None, aspect=None):
            m = np.isin(cls, keep)
            if aspect is not None and len(xyxy):
                ar = (xyxy[:, 2] - xyxy[:, 0]) / np.maximum(xyxy[:, 3] - xyxy[:, 1], 1.0)
                m = m & (ar >= aspect[0]) & (ar <= aspect[1])
            if zone is not None:
                m = m & in_zone(xyxy, zone)
            if exclude is not None:
                m = m & ~in_zone(xyxy, exclude)
            d = sv.Detections(xyxy=xyxy[m], confidence=conf[m], class_id=cls[m])
            d = tracker.update_with_detections(d)
            res = []
            if d.tracker_id is not None:
                for k, tid in enumerate(d.tracker_id.tolist()):
                    x1, y1, x2, y2 = d.xyxy[k]
                    c = int(d.class_id[k]) if d.class_id is not None else -1
                    cf = float(d.confidence[k]) if d.confidence is not None else 1.0
                    res.append((tid, (x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1, c, cf))
            return res

        praw = run(ptrack, people_ids, xyxy, conf, cls)
        present = stitch.resolve_frame(fi, [p[:5] for p in praw])
        # detector class of each raw det (for the cyclist-fraction sanity log)
        for p in praw:
            pconf_sum[stitch.map[p[0]]] += p[6]
            pconf_n[stitch.map[p[0]]] += 1
        for p in praw:
            if p[5] in cyc_ids:
                cyc_frames[stitch.map[p[0]]] += 1

        vehicles = []
        for tid, cx, cy, w, h, c, cf in run(vtrack, veh_ids, vxyxy, vconf, vcls, zone=road_poly,
                                            exclude=side_poly, aspect=(args.veh_aspect_min, args.veh_aspect_max)):
            vehicles.append((tid, vnames[c], cx, cy, w, h))
            veh_len[tid] += 1
            veh_conf_sum[tid] += cf
            veh_first_fi.setdefault(tid, fi)
            veh_last_fi[tid] = fi
            if tid not in veh_first_xy:
                veh_first_xy[tid] = (cx, cy)
                veh_last_xy[tid] = (cx, cy)
            fx, fy = veh_first_xy[tid]
            veh_max_disp[tid] = max(veh_max_disp[tid], math.hypot(cx - fx, cy - fy))
            lx, ly = veh_last_xy[tid]
            veh_path_len[tid] += math.hypot(cx - lx, cy - ly)
            veh_last_xy[tid] = (cx, cy)
            net_disp = math.hypot(cx - fx, cy - fy)
            straightness = net_disp / veh_path_len[tid] if veh_path_len[tid] > 1e-6 else 0.0
            if (veh_len[tid] >= args.veh_min and veh_max_disp[tid] >= args.veh_min_disp
                    and straightness >= args.veh_min_straightness
                    and veh_conf_sum[tid] / veh_len[tid] >= args.veh_min_mean_conf):
                veh_counted.add(tid)

        for tid, cx, cy, w, h in present:
            track_len[tid] += 1
            ph_sum[tid] += h
            first_fi.setdefault(tid, fi)
            last_fi[tid] = fi
            for zi, zp in enumerate((bike_poly, side_poly)):
                if zp is not None and cv2.pointPolygonTest(zp, (float(cx), float(cy + h / 2)), False) >= 0:
                    zone_hits[tid][zi] += 1
            crop = crop_square(frame, cx, cy, w, h, args.pad)
            if crop is not None:
                buffers[tid].append(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))

        hnow = {t_: h_ for t_, _cx, _cy, _w, h_ in present}
        due = [tid for tid, *_ in present
               if len(buffers[tid]) >= args.min_frames
               and (tid not in last_scored or fi - last_scored[tid] >= args.stride)]
        if due:
            clips = []
            for tid in due:
                buf = list(buffers[tid])
                idx = np.linspace(0, len(buf) - 1, N_FRAMES).round().astype(int)
                clips.append([buf[i] for i in idx])
            inputs = processor(text=prompts, videos=clips, return_tensors="pt", padding=True)
            inputs = {k: v.to(device) for k, v in inputs.items()}
            with torch.no_grad():
                allp = model(**inputs).logits_per_video.softmax(dim=1).cpu().numpy()
            probs = np.stack([allp[:, :nb].sum(1), allp[:, nb:].sum(1)], axis=1)
            for tid, p in zip(due, probs):
                smooth[tid] = p if tid not in smooth else args.ema * p + (1 - args.ema) * smooth[tid]
                last_scored[tid] = fi
                lab = int(np.argmax(smooth[tid]))
                prev, run_len = streak.get(tid, (None, 0))
                run_len = run_len + 1 if prev == lab else 1
                streak[tid] = (lab, run_len)
                prob_sum[tid] += p
                prob_n[tid] += 1
                wgt = max(float(hnow.get(tid, 1.0)), 1.0)
                prob_w[tid] += p * wgt
                prob_wn[tid] += wgt
                bike_hi[tid] += int(p[0] >= 0.9)
                score_log.append([tid, fi] + [round(float(x), 3) for x in p] +
                                 [round(float(x), 3) for x in smooth[tid]] + [round(wgt, 1)])

        rec_p, seen_now = [], set()
        for tid, cx, cy, w, h in present:
            seen_now.add(tid)
            coast_state.pop(tid, None)
            coast_dead.discard(tid)
            last_seen[tid] = (fi, cx, cy)
            new_box = np.array([cx, cy, w, h], dtype=float)
            sbox[tid] = new_box if tid not in sbox else args.box_ema * new_box + (1 - args.box_ema) * sbox[tid]
            rec_p.append((tid, *sbox[tid], smooth[tid].copy() if tid in smooth else None))
        # coast: detector dropped a track for a few frames -> follow the rider with optical flow
        # until the points are lost, it leaves the frame, or --coast-sec passes
        for tid, (lf, lx, ly) in last_seen.items():
            gap = fi - lf
            if tid in seen_now or gap > coast_frames or tid in coast_dead or prev_gray is None:
                continue
            if track_len[tid] < args.coast_min_sec * fps or not person_ok(tid, need_len=False):
                continue
            st = coast_state.get(tid)
            if st is None:
                st = init_flow(prev_gray, sbox[tid]) if gap == 1 else None
                if st is None:
                    coast_dead.add(tid)
                    continue
                coast_state[tid] = st
            if not flow_step(prev_gray, gray, st):
                coast_state.pop(tid, None)
                coast_dead.add(tid)
                continue
            px, py = st["box"][:2]
            if not (0 <= px < W and 0 <= py < H):
                coast_state.pop(tid, None)
                coast_dead.add(tid)
                continue
            rec_p.append((tid, px, py, st["box"][2], st["box"][3], smooth[tid].copy() if tid in smooth else None))

        live_labels = [int(np.argmax(wmean(t))) for t in prob_n if person_ok(t)]
        live_counts = (live_labels.count(0), live_labels.count(1))
        frame_rec[fi] = {"veh": vehicles, "ppl": rec_p,
                         "counts": (live_counts[0], live_counts[1], len(veh_counted))}
        prev_gray = gray
        if fi % 100 == 0:
            print(f"frame {fi}/{total if total > 0 else '?'}", flush=True)

    cap.release()
    if fi <= max(0, args.start_frame - 1):
        sys.exit("ERROR: read 0 frames from video")

    # ---- pass 2: render. Now that every track's fate is known, draw only tracks that were
    # counted (from their FIRST frame), so filtered junk never shows and real objects are not delayed.
    print("rendering annotated clips, one per bin (pass 2) ...", flush=True)
    good_p = {t for t in track_len if person_ok(t)}
    final_cls = {t: int(np.argmax(wmean(t))) for t in good_p if prob_n[t] > 0}   # == the counted people

    def mid_bin(t):
        return bin_of(int(round((first_fi[t] + last_fi[t]) / 2)))

    def fac_of(t):
        hb, hs = zone_hits[t] if t in zone_hits else (0, 0)
        if hb + hs == 0:
            return "unassigned"
        return "bike_lane" if hb >= hs else "sidewalk"

    bin_ai = {b: {"bic": 0, "ped": 0, "veh": 0, "bic_bl": 0, "bic_sw": 0, "bic_na": 0}
              for b in range(first_bin, last_bin + 1)}
    for t, c in final_cls.items():
        d_ = bin_ai[mid_bin(t)]
        if c == 0:
            d_["bic"] += 1
            d_[{"bike_lane": "bic_bl", "sidewalk": "bic_sw", "unassigned": "bic_na"}[fac_of(t)]] += 1
        else:
            d_["ped"] += 1
    for v in veh_counted:
        bin_ai[bin_of(int(round((veh_first_fi[v] + veh_last_fi[v]) / 2)))]["veh"] += 1

    cap2 = cv2.VideoCapture(args.video)
    fi2 = 0
    if args.start_frame > 1:
        cap2.set(cv2.CAP_PROP_POS_FRAMES, args.start_frame - 1)
        fi2 = args.start_frame - 1
    writer, cur_b, cur_final, cur_tmp, clips = None, None, None, None, []

    def close_clip():
        nonlocal writer
        if writer is not None:
            writer.release()
            writer = None
            clips.append(finalize_clip(cur_tmp, cur_final))

    while True:
        ok, frame = cap2.read()
        if not ok:
            break
        fi2 += 1
        rec = frame_rec.get(fi2)
        if rec is None:
            break
        b = bin_of(fi2)
        if b != cur_b:
            close_clip()
            cur_b = b
            s0, s1 = bin_start(b), bin_start(b + 1)
            cur_final = unique_path(os.path.join(adir, f"{tag}_{s0:%Y%m%d_%H%M}-{s1:%H%M}.mp4"))
            cur_tmp = os.path.splitext(cur_final)[0] + ".tmp_mp4v.mp4"
            writer = cv2.VideoWriter(cur_tmp, cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H + bar))
            if not writer.isOpened():
                sys.exit(f"ERROR: cannot open VideoWriter for {cur_tmp}")
        if zone_draw and not args.no_draw_zones:
            draw_zones(frame, zone_draw, args.zone_alpha)
            if not os.path.exists(zprev):
                cv2.imwrite(zprev, frame)
        for vid, name, cx, cy, w, h in rec["veh"]:
            if vid in veh_counted:
                draw_vehicle(frame, (cx, cy, w, h), vid, name, scale)
        for tid, cx, cy, w, h, pr in rec["ppl"]:
            if tid in good_p:
                draw_person(frame, (cx, cy, w, h), tid, None if pr is None else int(np.argmax(pr)), pr, scale)
        d_ = bin_ai[b]
        binline = (f"AI, this bin {bin_start(b):%I:%M}-{bin_start(b + 1):%I:%M %p}: "
                   f"Bicyclists {d_['bic']}  Pedestrians {d_['ped']}  Vehicles {d_['veh']}")
        writer.write(add_header(frame, scale, rec["counts"], fi2, total,
                                f"{clock_of(fi2):%Y-%m-%d %I:%M:%S %p}", binline))
    cap2.release()
    close_clip()

    log_path = unique_path(base + "_scores.csv")
    with open(log_path, "w", newline="") as f:
        wtr = csv.writer(f)
        wtr.writerow(["tracker_id", "frame", "bicyclist", "pedestrian",
                      "bicyclist_smooth", "pedestrian_smooth", "box_h"])
        wtr.writerows(score_log)

    print("\n=== person tracks (after id stitching) ===")
    print("track | frames | secs | scores | first-last frame | mean conf | mean box h | plain BIC | plain PED | wtd BIC | wtd PED | %scores bic>=.9 | %det=cyclist | FINAL LABEL")
    by_tid = defaultdict(list)
    for row in score_log:
        by_tid[row[0]].append(row[1])
    counted = [set(), set()]
    pstats = []
    for tid in sorted(track_len):
        cf = 100.0 * cyc_frames[tid] / track_len[tid]
        mc = pconf_sum[tid] / max(pconf_n[tid], 1)
        mh = ph_sum[tid] / track_len[tid]
        secs = track_len[tid] / fps
        if prob_n[tid] > 0:
            m = prob_sum[tid] / prob_n[tid]
            mw = wmean(tid)
            final = int(np.argmax(mw))   # decided from the box-height-weighted mean
            fl = f"{min(by_tid[tid])}-{max(by_tid[tid])}"
            ok_ = person_ok(tid)
            if ok_:
                counted[final].add(tid)
            tag = CLASSES[final][0] if ok_ else f"(filtered: was {CLASSES[final][0]}, not counted)"
            print(f"{tid:5d} | {track_len[tid]:6d} | {secs:4.1f} | {prob_n[tid]:6d} | {fl:>13s} | {mc:.2f} | {mh:6.0f} | {m[0]:.2f} | {m[1]:.2f} | {mw[0]:.2f} | {mw[1]:.2f} | {100.0 * bike_hi[tid] / prob_n[tid]:.0f}% | {cf:.0f}% | {tag}")
            pstats.append([tid, track_len[tid], round(secs, 2), prob_n[tid], fl, round(mc, 3), round(mh, 1),
                           round(float(m[0]), 3), round(float(m[1]), 3), round(float(mw[0]), 3), round(float(mw[1]), 3),
                           round(100.0 * bike_hi[tid] / prob_n[tid], 1), CLASSES[final][0], int(ok_)])
        else:
            print(f"{tid:5d} | {track_len[tid]:6d} | {secs:4.1f} |      0 | never scored | {mc:.2f} | {mh:6.0f} | | | {cf:.0f}% | (unscored, not counted)")
    stats_path = unique_path(base + "_track_stats.csv")
    with open(stats_path, "w", newline="") as f:
        wtr = csv.writer(f)
        wtr.writerow(["person_track", "frames", "secs", "scores", "first_last", "mean_conf", "mean_box_h",
                      "plain_bicyclist", "plain_pedestrian", "weighted_bicyclist", "weighted_pedestrian",
                      "pct_scores_bicyclist_ge_0.9", "label", "counted"])
        wtr.writerows(pstats)
        wtr.writerow([])
        wtr.writerow(["vehicle_track", "frames", "max_disp_px", "straightness", "mean_conf", "counted"])
        for vid in sorted(veh_len):
            fx, fy = veh_first_xy[vid]; lx, ly = veh_last_xy[vid]
            st = math.hypot(lx - fx, ly - fy) / veh_path_len[vid] if veh_path_len[vid] > 1e-6 else 0.0
            wtr.writerow([vid, veh_len[vid], round(veh_max_disp[vid], 1), round(st, 3),
                          round(veh_conf_sum[vid] / veh_len[vid], 3), int(vid in veh_counted)])
    print(f"Per-track quality stats (persons + vehicles): {stats_path}")
    print(f"\nRaw detector detections by class (conf>={args.det_conf}): {dict(det_hist)}")
    print(f"Stitched raw->canonical merges: "
          f"{sum(1 for k, v in stitch.map.items() if k != v)}")
    print(f"Final counts: bicyclists={len(counted[0])} pedestrians={len(counted[1])} "
          f"vehicles={len(veh_counted)}")
    print(f"Annotated clips ({len(clips)}): {adir}\nScores: {log_path}")

    # ---- v11 outputs for the aggregator: per-bin counts, per-track table, JSON run log ----
    cov = defaultdict(int)
    for f_ in frame_rec:
        cov[bin_of(f_)] += 1
    bin_path = unique_path(base + "_bin_counts.csv")
    with open(bin_path, "w", newline="") as f:
        w_ = csv.writer(f)
        w_.writerow(["video_file", "chunk", "bin_index", "bin_start", "bin_end", "seconds_covered",
                     "bicyclists_total", "bicyclists_bike_lane", "bicyclists_sidewalk",
                     "bicyclists_unassigned", "pedestrians", "vehicles"])
        for b in range(first_bin, last_bin + 1):
            d_ = bin_ai[b]
            w_.writerow([os.path.basename(args.video), chunk_idx, b,
                         bin_start(b).isoformat(sep=" "), bin_start(b + 1).isoformat(sep=" "),
                         round(cov[b] / fps, 1), d_["bic"], d_["bic_bl"], d_["bic_sw"], d_["bic_na"],
                         d_["ped"], d_["veh"]])
    trk_path = unique_path(base + "_tracks.csv")
    with open(trk_path, "w", newline="") as f:
        w_ = csv.writer(f)
        w_.writerow(["track_id", "label", "counted", "first_time", "last_time", "bin_index",
                     "facility", "secs", "mean_conf", "weighted_bicyclist", "weighted_pedestrian"])
        for t in sorted(track_len):
            lab = CLASSES[int(np.argmax(wmean(t)))][0] if prob_n[t] > 0 else "unscored"
            wb, wp = (wmean(t) if prob_n[t] > 0 else (float("nan"), float("nan")))
            w_.writerow([t, lab, int(t in final_cls), f"{clock_of(first_fi[t]):%Y-%m-%d %H:%M:%S}",
                         f"{clock_of(last_fi[t]):%Y-%m-%d %H:%M:%S}", mid_bin(t), fac_of(t),
                         round(track_len[t] / fps, 2), round(pconf_sum[t] / max(pconf_n[t], 1), 3),
                         round(float(wb), 3), round(float(wp), 3)])
    runlog = {
        "video_file": os.path.basename(args.video), "video_path": args.video, "chunk_index": chunk_idx,
        "n_input_videos_merged": 1,
        "clip_start_clock": clip_t0.isoformat(sep=" "), "clock_basis": args.clock_note,
        "fps": round(fps, 4), "resolution": [W, H],
        "frames_in_container_header": total, "frames_processed": len(frame_rec),
        "first_frame": min(frame_rec) if frame_rec else None, "last_frame": max(frame_rec) if frame_rec else None,
        "duration_s_container": round(total / fps, 2), "duration_s_processed": round(len(frame_rec) / fps, 2),
        "partial_run": bool(args.start_frame > 1 or args.max_frames),
        "weights": args.weights, "device": device, "params": vars(args),
        "final_counts": {"bicyclists": len(counted[0]), "pedestrians": len(counted[1]), "vehicles": len(veh_counted)},
        "raw_detections_by_class": dict(det_hist),
        "id_stitch_merges": sum(1 for k, v in stitch.map.items() if k != v),
        "annotated_clips": clips, "bin_counts_csv": bin_path, "tracks_csv": trk_path,
        "scores_csv": log_path, "track_stats_csv": stats_path,
        "runtime_s": round(time.time() - t_start, 1),
        "finished": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    rl_path = unique_path(os.path.join(ldir, f"{tag}_run_log.json"))
    with open(rl_path, "w") as f:
        json.dump(runlog, f, indent=2, default=str)
    print(f"Bin counts: {bin_path}\nTracks: {trk_path}\nRun log: {rl_path}\nRuntime: {runlog['runtime_s']} s")


if __name__ == "__main__":
    main()
