#!/usr/bin/env python3
"""
xclip_overlay_v3.py

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
import json
import math
import os
import sys
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


def add_header(img, scale, counts, fi, total):
    bar = int(70 * scale)
    out = cv2.copyMakeBorder(img, bar, 0, 0, 0, cv2.BORDER_CONSTANT, value=HEADER_COLOR)
    thick, fs = max(1, int(round(scale * 2))), scale * 0.7
    cv2.putText(out, "Fine-tuned RT-DETR + zero-shot X-CLIP (video-text) classification",
                (10, int(bar * 0.42)), cv2.FONT_HERSHEY_SIMPLEX, fs, (0, 0, 0), thick, cv2.LINE_AA)
    cv2.putText(out, f"Bicyclists: {counts[0]}   Pedestrians: {counts[1]}   Vehicles: {counts[2]}"
                     f"   |   frame {fi}/{total if total > 0 else '?'}",
                (10, int(bar * 0.85)), cv2.FONT_HERSHEY_SIMPLEX, fs, (0, 0, 0), thick, cv2.LINE_AA)
    return out


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
    ap.add_argument("--out", required=True)
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
    bar = int(70 * scale)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    writer = cv2.VideoWriter(args.out, cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H + bar))
    if not writer.isOpened():
        sys.exit(f"ERROR: cannot open VideoWriter for {args.out}")

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
    veh_len, veh_counted = defaultdict(int), set()
    veh_first_xy, veh_max_disp = {}, defaultdict(float)
    veh_last_xy, veh_path_len = {}, defaultdict(float)
    det_hist = defaultdict(int)   # detector class name -> raw detections over the video
    score_log = []
    pconf_sum, pconf_n, ph_sum = defaultdict(float), defaultdict(int), defaultdict(float)
    veh_conf_sum = defaultdict(float)

    def person_ok(tid, need_len=True):
        n = track_len[tid]
        if n == 0:
            return False
        if need_len and n < args.person_min_sec * fps:
            return False
        if pconf_n[tid] and pconf_sum[tid] / pconf_n[tid] < args.person_min_conf:
            return False
        return ph_sum[tid] / n >= args.person_min_h * H

    zprev = os.path.splitext(args.out)[0] + "_zones_preview.png"
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

        r = det.predict(frame, conf=args.det_conf, imgsz=args.imgsz, verbose=False, device=device)[0]
        xyxy = r.boxes.xyxy.cpu().numpy() if len(r.boxes) else np.zeros((0, 4))
        conf = r.boxes.conf.cpu().numpy() if len(r.boxes) else np.zeros(0)
        cls = r.boxes.cls.int().cpu().numpy() if len(r.boxes) else np.zeros(0, dtype=int)

        for c_ in cls.tolist():
            det_hist[names[c_]] += 1

        if vdet is not None:
            rv = vdet.predict(frame, conf=args.det_conf, imgsz=args.imgsz, verbose=False, device=device)[0]
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
            crop = crop_square(frame, cx, cy, w, h, args.pad)
            if crop is not None:
                buffers[tid].append(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))

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
                score_log.append([tid, fi] + [round(float(x), 3) for x in p] +
                                 [round(float(x), 3) for x in smooth[tid]])

        if zone_draw and not args.no_draw_zones:
            draw_zones(frame, zone_draw, args.zone_alpha)
            if not os.path.exists(zprev):
                cv2.imwrite(zprev, frame)
        for vid, name, cx, cy, w, h in vehicles:
            draw_vehicle(frame, (cx, cy, w, h), vid, name, scale)
        for tid, cx, cy, w, h in present:
            if not person_ok(tid, need_len=False):
                continue  # low-conf / tiny track: don't draw it
            if tid in smooth:
                p = smooth[tid]
                draw_person(frame, (cx, cy, w, h), tid, int(np.argmax(p)), p, scale)
            else:
                draw_person(frame, (cx, cy, w, h), tid, None, None, scale)

        live_labels = [int(np.argmax(prob_sum[t] / prob_n[t])) for t in prob_n if person_ok(t)]
        live_counts = (live_labels.count(0), live_labels.count(1))
        writer.write(add_header(frame, scale, (live_counts[0], live_counts[1], len(veh_counted)),
                                fi, total))
        if fi % 100 == 0:
            print(f"frame {fi}/{total if total > 0 else '?'}", flush=True)

    cap.release()
    writer.release()
    if fi <= max(0, args.start_frame - 1):
        sys.exit("ERROR: read 0 frames from video")

    log_path = os.path.splitext(args.out)[0] + "_scores.csv"
    with open(log_path, "w", newline="") as f:
        wtr = csv.writer(f)
        wtr.writerow(["tracker_id", "frame", "bicyclist", "pedestrian",
                      "bicyclist_smooth", "pedestrian_smooth"])
        wtr.writerows(score_log)

    print("\n=== person tracks (after id stitching) ===")
    print("track | frames | secs | scores | first-last frame | mean conf | mean box h | mean BICYCLIST | mean PEDESTRIAN | %det=cyclist | FINAL LABEL")
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
            final = int(np.argmax(m))
            fl = f"{min(by_tid[tid])}-{max(by_tid[tid])}"
            ok_ = person_ok(tid)
            if ok_:
                counted[final].add(tid)
            tag = CLASSES[final][0] if ok_ else f"(filtered: was {CLASSES[final][0]}, not counted)"
            print(f"{tid:5d} | {track_len[tid]:6d} | {secs:4.1f} | {prob_n[tid]:6d} | {fl:>13s} | {mc:.2f} | {mh:6.0f} | {m[0]:.2f} | {m[1]:.2f} | {cf:.0f}% | {tag}")
            pstats.append([tid, track_len[tid], round(secs, 2), prob_n[tid], fl, round(mc, 3), round(mh, 1),
                           round(float(m[0]), 3), round(float(m[1]), 3), CLASSES[final][0], int(ok_)])
        else:
            print(f"{tid:5d} | {track_len[tid]:6d} | {secs:4.1f} |      0 | never scored | {mc:.2f} | {mh:6.0f} | | | {cf:.0f}% | (unscored, not counted)")
    stats_path = os.path.splitext(args.out)[0] + "_track_stats.csv"
    with open(stats_path, "w", newline="") as f:
        wtr = csv.writer(f)
        wtr.writerow(["person_track", "frames", "secs", "scores", "first_last", "mean_conf", "mean_box_h",
                      "mean_bicyclist", "mean_pedestrian", "label", "counted"])
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
    print(f"Video: {args.out}\nScores: {log_path}")


if __name__ == "__main__":
    main()
