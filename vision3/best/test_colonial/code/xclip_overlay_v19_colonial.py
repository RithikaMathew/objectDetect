#!/usr/bin/env python3
"""
xclip_overlay_v19_colonial.py  (derived from xclip_overlay_v10 via v11-v15; earlier versions are left untouched)

v19 changes (ALL OFF by default: with none of the new options the counts are identical to v18/v17). One experiment = one flag:
  E1  --sahi                 sliced inference (SAHI idea, own implementation, no extra package): slice the frame, detect in each slice, add the
                             full-frame pass, merge duplicates. --sahi-people-only (default on) keeps vehicles from the full-frame pass only.
  E2  --enhance gamma|clahe|zerodce   brighten the frame BEFORE the detector (X-CLIP crops stay original unless --enhance-crops).
                             --enhance-when night (default) needs --night-start/--night-end only to define which frames are night.
  E3  --speed-rule           relabel a track by speed (body heights per second) ONLY when the detector agrees against X-CLIP.
      --short-rule           count a very short track as a bicyclist if the detector calls it a cyclist in >= --short-det-pct % of frames.
      --motion-diag          NO effect on counts: background-subtraction blobs that no detection explains -> *_motion_candidates.csv + contact sheet.
  Always written: *_rules_audit.csv (per track: X-CLIP label, detector %, speed, what each rule WOULD do).

v18 changes (OFF by default: with none of the --night-* options the counts are identical to v17):
  * time-of-day settings. Between --night-start and --night-end (clock time, HH:MM, may cross midnight; e.g. 21:00 .. 06:00) the script can use
      --night-det-conf     detector confidence for frames in that period       (day: --det-conf)
      --night-bic-min-sec  minimum seconds to count a BICYCLIST                (day: --bic-min-sec)
      --night-ped-min-sec  minimum seconds to count a PEDESTRIAN               (day: --ped-min-sec)
    A track counts as 'night' if the clock time of its MIDDLE frame is in the night period. Omitted night values fall back to the day values.
    So one run can keep 3 s / conf 0.25 by day and a short minimum / lower confidence at night.

v17 changes (detector / tracker / X-CLIP scoring and the counts are UNCHANGED from v16; only outputs were added):
  * <tag>_trajectories.csv : one row per track per frame (ground point = bottom-centre of the box, box, coasted flag, final label)
  * <tag>_track_motion.csv : per track: path / net distance, speed in px/s and in body-heights/s (perspective-robust), heading, direction
  * <tag>_split_candidates.csv : pairs of tracks that look like ONE person whose id broke (flags pairs that would only pass the minimum
    duration if joined) -> a direct measurement of the 'tracking id breaks' hypothesis. Nothing is merged or recounted.
  * annotated clips get a fading trail + arrow per counted person (--trail-sec, --no-trails)

v11+v12 changes (detector / tracker / X-CLIP scoring logic is UNCHANGED from v10):
  * wall-clock aware: --session-start + chunk number -> clock time of every frame
    (verified from the on-screen clock: .001=00:00, .008=07:00, .025=next day 00:00)
  * every counted track is assigned to a 15-minute bin (by its midpoint frame)
  * annotated video is split into one clip per 15-min bin (tracking itself is NOT cut)
  * outputs go to <out-root>/{counts,annotated,logs}/<run>/ ; nothing is overwritten
    (an existing file gets _v2, _v3 ... instead)
  * per-bin CSV, per-track CSV and a JSON run log are written for the aggregator
  * v16: clip header shows the GROUND TRUTH of the bin next to the AI count (--gt-xls); vehicle boxes say X-CLIP n/a
  * v15: --ped-min-sec / --bic-min-sec: minimum visible time judged per X-CLIP class (default: both = --person-min-sec)
  * v14: every person box shows BOTH labels: the RT-DETR detector label (person/cyclist, mean conf, % frames as cyclist)
         and the X-CLIP label with its two probabilities; tracks.csv gets det_label / det_cyclist_pct / labels_agree
  * v13: --person-min-disp rejects static 'people' (cones, signs) by net movement; tracks.csv gets disp_px
  * v12: --stream-clips writes each 15-min clip right after its bin ends (header says "prov.")

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
import bisect
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

from annotation_truth import colonial_truth_bins, truth_text

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


def draw_person(img, box, tid, cls, probs, scale, det=None):
    """det = (detector_label, detector_mean_conf, pct_frames_detected_as_cyclist) from the fine-tuned RT-DETR detector;
    probs = X-CLIP [P(bicyclist), P(pedestrian)]. Both labels are written on the box."""
    cx, cy, w, h = box
    x1, y1, x2, y2 = int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2)
    thick = max(1, int(round(scale * 2)))
    det_txt = None
    if det is not None:
        det_txt = f"RT-DETR: {det[0]} {det[1]:.2f} ({det[2]:.0f}% cyclist)"
    if cls is None:
        color, lines = (255, 255, 255), [f"id {tid} (X-CLIP scoring...)"]
        if det_txt:
            lines.append(det_txt)
    else:
        color = CLASSES[cls][1]
        lines = [f"id {tid} FINAL: {CLASSES[cls][0]}"]
        if det_txt:
            agree = (det[0] == "cyclist") == (cls == 0)
            lines.append(det_txt + (" [agree]" if agree else " [DISAGREE]"))
        lines.append(f"X-CLIP: bicy {probs[0]:.2f} | pede {probs[1]:.2f}")
    cv2.rectangle(img, (x1, y1), (x2, y2), color, thick)
    line_h = int(22 * scale) + 6
    y = max(line_h, y1 - 4 - line_h * (len(lines) - 1))
    for i, t in enumerate(lines):
        _tag(img, x1, y + i * line_h, t, scale * (0.7 if i == 0 else 0.55), thick,
             color if i == 0 else (255, 255, 255))


def draw_vehicle(img, box, tid, name, scale):
    cx, cy, w, h = box
    thick = max(1, int(round(scale * 2)))
    cv2.rectangle(img, (int(cx - w / 2), int(cy - h / 2)), (int(cx + w / 2), int(cy + h / 2)),
                  VEH_COLOR, thick)
    _tag(img, int(cx - w / 2), max(int(22 * scale), int(cy - h / 2) - 4), f"RT-DETR: {name} #{tid} | X-CLIP: n/a (people only)",
         scale * 0.6, thick, VEH_COLOR)


def add_header(img, scale, counts, fi, total, clock="", binline="", gtline="GT: not labelled"):
    bar = int(140 * scale)
    out = cv2.copyMakeBorder(img, bar, 0, 0, 0, cv2.BORDER_CONSTANT, value=HEADER_COLOR)
    thick, fs = max(1, int(round(scale * 2))), scale * 0.7
    lines = [f"{clock}   |   frame {fi}/{total if total > 0 else '?'}",
             f"Hour so far (live count) - Bic: {counts[0]}  Ped: {counts[1]}  Veh: {counts[2]}",
             binline, gtline]
    for i, t in enumerate(lines):
        cv2.putText(out, t, (10, int(bar * (0.19 + 0.24 * i))), cv2.FONT_HERSHEY_SIMPLEX,
                    min(fs, max(.15, (out.shape[1]-20) / max(1, cv2.getTextSize(t, cv2.FONT_HERSHEY_SIMPLEX, 1., thick)[0][0]))),
                    (0, 0, 0), thick, cv2.LINE_AA)
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


def draw_trail(img, pts, color, thick):
    """pts: [(x, y), ...] ground points, oldest first. Fading polyline, arrow head and dot at the newest point."""
    n = len(pts)
    if n < 2:
        return
    for i in range(1, n):
        a = 0.35 + 0.65 * i / (n - 1)
        cv2.line(img, (int(pts[i - 1][0]), int(pts[i - 1][1])), (int(pts[i][0]), int(pts[i][1])),
                 tuple(int(v * a) for v in color), thick, cv2.LINE_AA)
    p0, p1 = pts[max(0, n - 8)], pts[-1]
    if math.hypot(p1[0] - p0[0], p1[1] - p0[1]) >= 8:
        cv2.arrowedLine(img, (int(p0[0]), int(p0[1])), (int(p1[0]), int(p1[1])), color, thick, cv2.LINE_AA, tipLength=0.5)
    cv2.circle(img, (int(p1[0]), int(p1[1])), thick + 2, color, -1, cv2.LINE_AA)


def smooth_xy(xs, ys, k):
    """Centered moving average (odd window k, edges padded) to take the box jitter out of the ground point."""
    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    k = int(k) | 1
    if len(xs) < 3 or k < 3:
        return xs, ys
    k = min(k, len(xs) if len(xs) % 2 else len(xs) - 1)
    ker = np.ones(k) / k
    pad = k // 2
    f = lambda a: np.convolve(np.pad(a, pad, mode="edge"), ker, mode="valid")
    return f(xs), f(ys)


def motion_summary(frames, xs, ys, mean_h, fps, min_net_px):
    """Per-track motion from the ground-point history. Image axes: x right, y DOWN.
    Assumption (check against your camera): larger y = closer to the camera, so dy > 0 = 'toward_camera'."""
    sx, sy = smooth_xy(xs, ys, round(fps * 0.5))
    dxs, dys = np.diff(sx), np.diff(sy)
    path = float(np.hypot(dxs, dys).sum()) if len(dxs) else 0.0
    dx, dy = (float(sx[-1] - sx[0]), float(sy[-1] - sy[0])) if len(sx) else (0.0, 0.0)
    net = math.hypot(dx, dy)
    span = max((frames[-1] - frames[0]) / fps, 1e-6) if len(frames) > 1 else 0.0
    if net < min_net_px:
        direction = "static"
    elif abs(dy) >= abs(dx):
        direction = "toward_camera" if dy > 0 else "away_from_camera"
    else:
        direction = "moving_right" if dx > 0 else "moving_left"
    pspd = path / span if span else 0.0
    return {"path_px": path, "net_px": net, "dx": dx, "dy": dy, "span_s": span,
            "path_speed_pxs": pspd, "net_speed_pxs": net / span if span else 0.0,
            "speed_heights_per_s": pspd / mean_h if mean_h > 0 else float("nan"), "direction": direction}


def split_candidates(info, fps, max_gap_s, max_px, min_sec, thr_sec):
    """info: tid -> dict(first, last, n, p0, p1, v(px/frame), label). A track A that ends and a track B that starts
    soon after, near where A was heading, are probably one person whose id broke. Mutual-best matches only.
    Returns rows; does NOT merge anything."""
    cands = []
    for a, A in info.items():
        for b, B in info.items():
            if a == b or A["n"] < min_sec * fps or B["n"] < min_sec * fps:
                continue
            gap = B["first"] - A["last"]
            if not (0 < gap <= max_gap_s * fps):
                continue
            pred = (A["p1"][0] + A["v"][0] * gap, A["p1"][1] + A["v"][1] * gap)
            d = min(math.hypot(B["p0"][0] - pred[0], B["p0"][1] - pred[1]),
                    math.hypot(B["p0"][0] - A["p1"][0], B["p0"][1] - A["p1"][1]))
            if d <= max_px:
                cands.append((d, a, b, gap))
    best_a, best_b = {}, {}
    for d, a, b, gap in sorted(cands):
        if a not in best_a and b not in best_b:
            best_a[a], best_b[b] = b, a
    rows = []
    for d, a, b, gap in sorted(cands, key=lambda c: c[1]):
        if best_a.get(a) != b:
            continue
        A, B = info[a], info[b]
        sa, sb = A["n"] / fps, B["n"] / fps
        rows.append([a, b, round(gap / fps, 2), round(d, 1), round(sa, 2), round(sb, 2), round(sa + sb, 2),
                     A["label"], B["label"], int(sa >= thr_sec or sb >= thr_sec), int(sa + sb >= thr_sec)])
    return rows


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


# ======================================================================================================
# v19 additions: sliced inference, enhancement, motion diagnostic
# ======================================================================================================
def predict_arrays(det, img, conf, imgsz, device):
    r = det.predict(img, conf=conf, imgsz=imgsz, verbose=False, device=device)[0]
    n = len(r.boxes)
    if not n:
        return np.zeros((0, 4)), np.zeros(0), np.zeros(0, dtype=int)
    return r.boxes.xyxy.cpu().numpy(), r.boxes.conf.cpu().numpy(), r.boxes.cls.int().cpu().numpy()


def slice_origins(x0, y0, x1, y1, size, overlap):
    """Overlapping square-ish slices that cover the box (x0,y0,x1,y1). Returns [(x, y, w, h), ...]."""
    def starts(a, b):
        L = b - a
        if L <= size:
            return [a], L
        stride = max(1, int(size * (1.0 - overlap)))
        st = list(range(a, b - size + 1, stride))
        if st[-1] + size < b:
            st.append(b - size)
        return st, size
    xs, sw = starts(x0, x1)
    ys, sh = starts(y0, y1)
    return [(x, y, sw, sh) for y in ys for x in xs]


def merge_ios(xyxy, conf, cls, ios_thr=0.6, iou_min=0.3):
    """Greedy same-class duplicate removal, highest confidence first. A box is a duplicate if it overlaps a kept box by
    >= ios_thr of the SMALLER box's area AND IoU >= iou_min (so a small person inside a big box of the same class is kept)."""
    n = len(xyxy)
    if n < 2:
        return np.arange(n)
    x1, y1, x2, y2 = xyxy[:, 0], xyxy[:, 1], xyxy[:, 2], xyxy[:, 3]
    area = np.maximum(x2 - x1, 0) * np.maximum(y2 - y1, 0)
    order = np.argsort(-conf)
    sup = np.zeros(n, dtype=bool)
    keep = []
    for i in order:
        if sup[i]:
            continue
        keep.append(i)
        iw = np.maximum(0, np.minimum(x2[i], x2) - np.maximum(x1[i], x1))
        ih = np.maximum(0, np.minimum(y2[i], y2) - np.maximum(y1[i], y1))
        inter = iw * ih
        ios = inter / np.maximum(np.minimum(area[i], area), 1e-6)
        iou = inter / np.maximum(area[i] + area - inter, 1e-6)
        dup = (ios >= ios_thr) & (iou >= iou_min) & (cls == cls[i])
        dup[i] = False
        sup |= dup
    return np.array(sorted(keep), dtype=int)


def sliced_detect(det, frame, conf, device, size, overlap, imgsz, roi=None, margin=3):
    """Detections from overlapping slices only (boxes in full-frame coordinates). Boxes that touch a slice edge which is NOT
    the edge of the search area are dropped (they are cut-off copies of an object that the neighbouring slice sees whole)."""
    Hf, Wf = frame.shape[:2]
    rx0, ry0, rx1, ry1 = roi if roi else (0, 0, Wf, Hf)
    rx0, ry0, rx1, ry1 = max(0, int(rx0)), max(0, int(ry0)), min(Wf, int(rx1)), min(Hf, int(ry1))
    ax, ac, acl = [], [], []
    for (sx0, sy0, sw, sh) in slice_origins(rx0, ry0, rx1, ry1, size, overlap):
        xy, cf, cl = predict_arrays(det, frame[sy0:sy0 + sh, sx0:sx0 + sw], conf, imgsz, device)
        if not len(xy):
            continue
        xy = xy + np.array([sx0, sy0, sx0, sy0], dtype=float)
        bad = np.zeros(len(xy), dtype=bool)
        if sx0 > rx0:
            bad |= xy[:, 0] <= sx0 + margin
        if sx0 + sw < rx1:
            bad |= xy[:, 2] >= sx0 + sw - margin
        if sy0 > ry0:
            bad |= xy[:, 1] <= sy0 + margin
        if sy0 + sh < ry1:
            bad |= xy[:, 3] >= sy0 + sh - margin
        ax.append(xy[~bad]); ac.append(cf[~bad]); acl.append(cl[~bad])
    if not ax:
        return np.zeros((0, 4)), np.zeros(0), np.zeros(0, dtype=int)
    return np.concatenate(ax), np.concatenate(ac), np.concatenate(acl)


def make_zerodce(weights, device):
    """Zero-DCE (Guo et al., CVPR 2020) curve-estimation network. Layer names match the official Epoch99.pth checkpoint."""
    import torch.nn as nn

    class DCE(nn.Module):
        def __init__(self):
            super().__init__()
            self.relu = nn.ReLU(inplace=True)
            nf = 32
            self.e_conv1 = nn.Conv2d(3, nf, 3, 1, 1, bias=True)
            self.e_conv2 = nn.Conv2d(nf, nf, 3, 1, 1, bias=True)
            self.e_conv3 = nn.Conv2d(nf, nf, 3, 1, 1, bias=True)
            self.e_conv4 = nn.Conv2d(nf, nf, 3, 1, 1, bias=True)
            self.e_conv5 = nn.Conv2d(nf * 2, nf, 3, 1, 1, bias=True)
            self.e_conv6 = nn.Conv2d(nf * 2, nf, 3, 1, 1, bias=True)
            self.e_conv7 = nn.Conv2d(nf * 2, 24, 3, 1, 1, bias=True)

        def forward(self, x):
            x1 = self.relu(self.e_conv1(x)); x2 = self.relu(self.e_conv2(x1))
            x3 = self.relu(self.e_conv3(x2)); x4 = self.relu(self.e_conv4(x3))
            x5 = self.relu(self.e_conv5(torch.cat([x3, x4], 1)))
            x6 = self.relu(self.e_conv6(torch.cat([x2, x5], 1)))
            xr = torch.tanh(self.e_conv7(torch.cat([x1, x6], 1)))
            for r in torch.split(xr, 3, dim=1):          # 8 iterations of the light-enhancement curve LE(x) = x + r (x^2 - x)
                x = x + r * (torch.pow(x, 2) - x)
            return x

    net = DCE().to(device).eval()
    try:
        sd = torch.load(weights, map_location=device)
    except Exception:                       # newer torch defaults to weights_only=True; the official file is an old-style checkpoint
        sd = torch.load(weights, map_location=device, weights_only=False)
    net.load_state_dict(sd)
    return net


def enhance_frame(frame, mode, gamma=2.2, clahe_clip=3.0, dce=None, device="cpu"):
    """BGR uint8 in, BGR uint8 out."""
    if mode == "gamma":
        lut = (255.0 * (np.arange(256) / 255.0) ** (1.0 / gamma)).clip(0, 255).astype(np.uint8)
        return cv2.LUT(frame, lut)
    if mode == "clahe":
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        lab[:, :, 0] = cv2.createCLAHE(clipLimit=clahe_clip, tileGridSize=(8, 8)).apply(lab[:, :, 0])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    if mode == "zerodce":
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        t = torch.from_numpy(rgb).to(device).permute(2, 0, 1).unsqueeze(0).float() / 255.0
        with torch.no_grad():
            o = dce(t).clamp(0, 1)
        out = (o.squeeze(0).permute(1, 2, 0).cpu().numpy() * 255.0 + 0.5).astype(np.uint8)
        return cv2.cvtColor(out, cv2.COLOR_RGB2BGR)
    return frame


class MotionDiag:
    """Diagnostic only (never changes a count). Background subtraction finds things that MOVE; blobs that no detector box explains are
    grouped over time. A long unexplained moving blob = a person/vehicle the detector may have missed (or a headlight beam / shadow:
    look at the contact sheet before trusting it)."""

    def __init__(self, fps, scale=0.5, warm=90, min_area=150, max_area=30000, gap=15, link_px=70):
        self.bg = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=36, detectShadows=False)
        self.fps, self.s, self.warm, self.n = fps, scale, warm, 0
        self.min_area, self.max_area, self.gap, self.link_px = min_area, max_area, gap, link_px
        self.k = np.ones((3, 3), np.uint8)
        self.tracks = []     # dicts: obs [(fi, cx, cy, w, h)], crops [(fi, img)]

    def update(self, frame, fi, det_xyxy):
        small = cv2.resize(frame, None, fx=self.s, fy=self.s, interpolation=cv2.INTER_AREA)
        fg = self.bg.apply(small)
        self.n += 1
        if self.n <= self.warm:
            return 0
        fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, self.k)
        fg = cv2.dilate(fg, self.k, iterations=2)
        nl, _lab, st, _c = cv2.connectedComponentsWithStats(fg, connectivity=8)
        cands = []
        for i in range(1, nl):
            x, y, w, h, a = st[i]
            if a < self.min_area * self.s ** 2 or a > self.max_area * self.s ** 2:
                continue
            X1, Y1, X2, Y2 = x / self.s, y / self.s, (x + w) / self.s, (y + h) / self.s
            cx, cy = (X1 + X2) / 2, (Y1 + Y2) / 2
            if len(det_xyxy):
                bw, bh = det_xyxy[:, 2] - det_xyxy[:, 0], det_xyxy[:, 3] - det_xyxy[:, 1]
                inside = ((cx >= det_xyxy[:, 0] - 0.15 * bw) & (cx <= det_xyxy[:, 2] + 0.15 * bw) &
                          (cy >= det_xyxy[:, 1] - 0.15 * bh) & (cy <= det_xyxy[:, 3] + 0.15 * bh))
                if inside.any():
                    continue                       # explained by a detection
            cands.append((cx, cy, X2 - X1, Y2 - Y1, (X1, Y1, X2, Y2)))
        used = set()
        for cx, cy, w, h, bb in cands:
            best, bd = None, 1e9
            for ti, t in enumerate(self.tracks):
                if ti in used:
                    continue
                lf, lx, ly, _lw, _lh = t["obs"][-1]
                if fi - lf > self.gap:
                    continue
                d = math.hypot(cx - lx, cy - ly)
                if d < bd and d <= self.link_px:
                    best, bd = ti, d
            if best is None:
                self.tracks.append({"obs": [], "crops": []})
                best = len(self.tracks) - 1
            used.add(best)
            t = self.tracks[best]
            t["obs"].append((fi, cx, cy, w, h))
            if len(t["obs"]) % 20 == 1 and len(t["crops"]) < 4:
                X1, Y1, X2, Y2 = bb
                px, py = 0.25 * (X2 - X1) + 8, 0.25 * (Y2 - Y1) + 8
                a0, b0 = int(max(0, Y1 - py)), int(max(0, X1 - px))
                crop = frame[a0:int(min(frame.shape[0], Y2 + py)), b0:int(min(frame.shape[1], X2 + px))]
                if crop.size:
                    sc = 110.0 / max(crop.shape[:2])
                    t["crops"].append((fi, cv2.resize(crop, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)))
        return len(cands)

    def finish(self, min_sec=0.7):
        out = []
        for t in self.tracks:
            ob = t["obs"]
            if len(ob) < max(8, int(min_sec * self.fps)):
                continue
            dur = (ob[-1][0] - ob[0][0]) / self.fps
            if dur < min_sec:
                continue
            net = math.hypot(ob[-1][1] - ob[0][1], ob[-1][2] - ob[0][2])
            mh = float(np.mean([o[4] for o in ob])); mw = float(np.mean([o[3] for o in ob]))
            out.append({"t": t, "first": ob[0][0], "last": ob[-1][0], "secs": dur, "n": len(ob), "net_px": net,
                        "mean_h": mh, "mean_w": mw, "x": float(np.mean([o[1] for o in ob])), "y": float(np.mean([o[2] for o in ob]))})
        return sorted(out, key=lambda r: r["first"])

    @staticmethod
    def contact_sheet(rows, clock_of, path, max_rows=40):
        if not rows:
            return None
        rows = sorted(rows, key=lambda r: -r["n"])[:max_rows]
        rows = sorted(rows, key=lambda r: r["first"])
        cell = 120
        sheet = np.full((len(rows) * (cell + 4), 4 * cell + 260, 3), 30, np.uint8)
        for i, r in enumerate(rows):
            y0 = i * (cell + 4)
            txt = [f"cand {i + 1}  {clock_of(r['first']):%H:%M:%S}-{clock_of(r['last']):%H:%M:%S}",
                   f"{r['secs']:.1f}s  n={r['n']}  net={r['net_px']:.0f}px", f"box {r['mean_w']:.0f}x{r['mean_h']:.0f}  at ({r['x']:.0f},{r['y']:.0f})"]
            for k, tx in enumerate(txt):
                cv2.putText(sheet, tx, (6, y0 + 24 + 22 * k), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            for j, (_f, cr) in enumerate(r["t"]["crops"][:4]):
                h_, w_ = cr.shape[:2]
                sheet[y0:y0 + h_, 260 + j * cell:260 + j * cell + w_] = cr[:cell, :cell] if (h_ > cell or w_ > cell) else cr
        cv2.imwrite(path, sheet)
        return path


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
    ap.add_argument("--stream-clips", action="store_true",
                    help="write each bin's annotated clip as soon as the bin is over (+ --stream-delay-sec) instead of "
                         "all at the end. The clip header then shows PROVISIONAL counts (decided with the tracks seen so far); "
                         "any difference from the final per-bin counts is logged in the run log.")
    ap.add_argument("--stream-delay-sec", type=float, default=10.0,
                    help="wait this long after a bin ends before rendering it, so boundary tracks can finish/stitch")
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
    ap.add_argument("--gt-truth-dir", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "truth"),
                    help="hand-labelled Colonial CSVs for headers; guarded by exact source name/date")
    ap.add_argument("--gt-xls", default=None,
                    help="counter .xls (SpreadsheetML): print the ground truth of each 15-min bin in the clip header")
    ap.add_argument("--zones-json", default=None,
                    help="per-camera zone file: {\"ref_size\":[W,H], \"road\":[[x,y],..], \"bike\":[..], \"sidewalk\":[..]}. "
                         "Explicit --road-zone/--bike-zone/--sidewalk-zone flags override it.")
    ap.add_argument("--zone-alpha", type=float, default=0.07, help="zone fill opacity on the video (0=off)")
    ap.add_argument("--person-min-sec", type=float, default=3.0,
                    help="a person track must be visible this many seconds to be drawn-as-confirmed/counted")
    ap.add_argument("--person-min-conf", type=float, default=0.0,
                    help="min MEAN detector confidence over a person track (0=off; see track_stats.csv to pick a value)")
    ap.add_argument("--ped-min-sec", type=float, default=None,
                    help="min seconds a track must be visible to count as a PEDESTRIAN (default: --person-min-sec)")
    ap.add_argument("--bic-min-sec", type=float, default=None,
                    help="min seconds a track must be visible to count as a BICYCLIST (default: --person-min-sec)")
    ap.add_argument("--person-min-disp", type=float, default=0.0,
                    help="min NET movement (px, ground point, first->last frame of the track) for a person track to count; "
                         "rejects static look-alikes such as cones/signs that the detector keeps calling 'person' (0=off)")
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
    ap.add_argument("--trail-sec", type=float, default=5.0,
                    help="length of the trail drawn behind each counted person in the annotated clips (0 = whole history)")
    ap.add_argument("--no-trails", action="store_true", help="do not draw trails/arrows")
    ap.add_argument("--min-net-px", type=float, default=30.0,
                    help="net movement below this (px, smoothed ground point) = direction 'static'")
    ap.add_argument("--split-gap-sec", type=float, default=8.0, help="split-candidate search: max gap between end of A and start of B")
    ap.add_argument("--split-px", type=float, default=120.0, help="split-candidate search: max distance from where A was heading to where B starts")
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
    ap.add_argument("--night-start", default=None, help="start of the night period, clock time HH:MM (e.g. 21:00); needs --night-end")
    ap.add_argument("--night-end", default=None, help="end of the night period, HH:MM (e.g. 06:00); may be earlier than start (crosses midnight)")
    ap.add_argument("--night-det-conf", type=float, default=None, help="detector confidence used in night frames (default: --det-conf)")
    ap.add_argument("--night-bic-min-sec", type=float, default=None, help="min seconds to count a bicyclist whose track is at night (default: day value)")
    ap.add_argument("--night-ped-min-sec", type=float, default=None, help="min seconds to count a pedestrian whose track is at night (default: day value)")
    ap.add_argument("--sahi", action="store_true", help="E1: sliced inference + full-frame pass, merged")
    ap.add_argument("--sahi-slice", type=int, default=640, help="slice size in px")
    ap.add_argument("--sahi-overlap", type=float, default=0.2)
    ap.add_argument("--sahi-imgsz", type=int, default=None, help="detector input size for slices (default = slice size)")
    ap.add_argument("--sahi-ios", type=float, default=0.6, help="duplicate threshold (overlap / smaller box)")
    ap.add_argument("--sahi-roi", default=None, help="x1,y1,x2,y2 in frame pixels: only slice this region (default whole frame)")
    ap.add_argument("--sahi-all-classes", action="store_true", help="also use slice detections for vehicles (default: people only)")
    ap.add_argument("--tta", action="store_true", help="research: add full-frame scale/flip person detections before tracking")
    ap.add_argument("--tta-sizes", type=int, nargs="+", default=[960, 1280])
    ap.add_argument("--enhance", choices=["none", "gamma", "clahe", "zerodce"], default="none", help="E2: enhance the frame before the detector")
    ap.add_argument("--enhance-when", choices=["night", "always"], default="night")
    ap.add_argument("--gamma", type=float, default=2.2)
    ap.add_argument("--clahe-clip", type=float, default=3.0)
    ap.add_argument("--zerodce-weights", default=None, help="Zero-DCE Epoch99.pth")
    ap.add_argument("--enhance-crops", action="store_true", help="also feed the enhanced frame to X-CLIP")
    ap.add_argument("--speed-rule", action="store_true", help="E3: relabel by speed when the detector agrees against X-CLIP")
    ap.add_argument("--walk-max-speed", type=float, default=1.0, help="body heights per second: slower than this = walker")
    ap.add_argument("--ride-min-speed", type=float, default=2.0, help="body heights per second: faster than this = rider")
    ap.add_argument("--speed-min-sec", type=float, default=1.5, help="speed rule only for tracks visible at least this long")
    ap.add_argument("--speed-lateral-only", action="store_true", help="speed rule only for tracks moving left/right: toward/away motion looks slow in the image whatever the real speed")
    ap.add_argument("--short-rule", action="store_true", help="E3: count short, detector-sure cyclist tracks")
    ap.add_argument("--short-min-sec", type=float, default=0.3)
    ap.add_argument("--short-det-pct", type=float, default=90.0, help="detector must say cyclist in >= this %% of the track's frames")
    ap.add_argument("--short-wbic", type=float, default=0.9, help="and the weighted X-CLIP bicyclist probability must be >= this")
    ap.add_argument("--short-rule-night-only", action="store_true", help="with --short-rule: apply it only to tracks whose middle frame is in the night period")
    ap.add_argument("--det-veto-pct", type=float, default=None, help="detector veto: X-CLIP says BICYCLIST but the detector calls the track cyclist in < this %% of its frames -> PEDESTRIAN")
    ap.add_argument("--det-promote-pct", type=float, default=None, help="detector promote: X-CLIP says PEDESTRIAN but the detector calls it cyclist in >= this %% of frames -> BICYCLIST")
    ap.add_argument("--det-fuse-min-frames", type=int, default=20, help="the veto/promote rules need at least this many detector frames on the track")
    ap.add_argument("--static-filter", action="store_true", help="drop a track (>= --static-min-sec) that is a STATIC OBJECT: net movement < --static-max-net-px AND path speed < --static-max-speed")
    ap.add_argument("--static-max-net-px", type=float, default=5.0)
    ap.add_argument("--static-max-speed", type=float, default=0.05, help="body heights per second of ground-point PATH (box jitter and body sway count: real standing people stay above this)")
    ap.add_argument("--static-min-sec", type=float, default=3.0)
    ap.add_argument("--motion-diag", action="store_true", help="E3: write unexplained-motion candidates (does not change counts)")
    ap.add_argument("--export-vehicle-trajectories", action="store_true", help="Save observed vehicle tracks for later conflict review; counting unchanged")
    args = ap.parse_args()
    if args.tta and any(v <= 0 or v % 32 for v in args.tta_sizes):
        ap.error("--tta-sizes must be positive multiples of 32")
    if args.ped_min_sec is None:
        args.ped_min_sec = args.person_min_sec
    if args.bic_min_sec is None:
        args.bic_min_sec = args.person_min_sec
    if (args.night_start is None) != (args.night_end is None):
        sys.exit("ERROR: pass both --night-start and --night-end (or neither)")
    night_on = args.night_start is not None
    if night_on:
        def _hm(x):
            h_, m_ = x.split(":")
            return int(h_) * 60 + int(m_)
        try:
            ns_min, ne_min = _hm(args.night_start), _hm(args.night_end)
        except ValueError:
            sys.exit("ERROR: --night-start/--night-end must look like 21:00")
    _tb = []
    if args.sahi:
        _tb.append(f"sahi{args.sahi_slice}")
    if args.tta:
        _tb.append("tta-scale-flip")
    if args.enhance != "none":
        _tb.append(f"enh-{args.enhance}")
    if args.speed_rule:
        _tb.append("speedrule-lateral" if args.speed_lateral_only else "speedrule")
    if args.short_rule:
        _tb.append("shortrule-night" if args.short_rule_night_only else "shortrule")
    if args.det_veto_pct is not None or args.det_promote_pct is not None:
        _tb.append("detfuse")
    if args.night_start is not None and (args.night_det_conf is not None or args.night_bic_min_sec is not None or args.night_ped_min_sec is not None):
        _tb.append("nightswitch")
    if args.static_filter:
        _tb.append("staticfilter")
    if args.motion_diag:
        _tb.append("motiondiag")
    test_tag = "+".join(_tb) if _tb else "control"      # goes into every annotated clip's file name
    if args.short_rule_night_only and args.night_start is None:
        sys.exit("ERROR: --short-rule-night-only needs --night-start/--night-end")
    if args.short_rule_night_only and not args.short_rule:
        sys.exit("ERROR: --short-rule-night-only only makes sense together with --short-rule")
    if args.enhance != "none" and args.enhance_when == "night" and args.night_start is None:
        sys.exit("ERROR: --enhance with --enhance-when night needs --night-start/--night-end to say which frames are night")
    if args.enhance == "zerodce" and not (args.zerodce_weights and os.path.isfile(args.zerodce_weights)):
        sys.exit("ERROR: --enhance zerodce needs --zerodce-weights /path/Epoch99.pth")
    night_det_conf = args.det_conf if args.night_det_conf is None else args.night_det_conf
    night_bic_sec = args.bic_min_sec if args.night_bic_min_sec is None else args.night_bic_min_sec
    night_ped_sec = args.ped_min_sec if args.night_ped_min_sec is None else args.night_ped_min_sec

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
    bar = int(140 * scale)

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

    def is_night_frame(frame_idx):
        if not night_on:
            return False
        c_ = clock_of(frame_idx)
        mins = c_.hour * 60 + c_.minute
        if ns_min <= ne_min:
            return ns_min <= mins < ne_min
        return mins >= ns_min or mins < ne_min      # period crosses midnight

    def is_night_track(t):
        if not night_on or t not in first_fi:
            return False
        return is_night_frame(int(round((first_fi[t] + last_fi[t]) / 2)))

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
    gt_bins = {}
    if args.gt_xls and args.bin_minutes == 15:
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from aggregate_colonial_v13 import parse_gt
            gt_bins, _ = parse_gt(args.gt_xls, [1, 2, 3, 4])
            print(f"ground truth loaded for the clip headers: {len(gt_bins)} bins")
        except Exception as e_:   # header only: never stop the run for this
            print(f"WARNING: could not load ground truth for the headers ({e_})")
    gt_bins.update(colonial_truth_bins(args.video, args.session_start, args.bin_minutes, args.gt_truth_dir))
    if night_on:
        print(f"night mode ON {args.night_start}-{args.night_end}: det conf {args.det_conf}->{night_det_conf}, "
              f"bicyclist min {args.bic_min_sec}->{night_bic_sec} s, pedestrian min {args.ped_min_sec}->{night_ped_sec} s", flush=True)
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
    p_first_xy, p_last_xy = {}, {}
    first_fi, last_fi, zone_hits = {}, {}, defaultdict(lambda: [0, 0])   # zone_hits: [bike, sidewalk] frames
    veh_first_fi, veh_last_fi = {}, {}
    veh_len, veh_counted = defaultdict(int), set()
    veh_first_xy, veh_max_disp = {}, defaultdict(float)
    veh_last_xy, veh_path_len = {}, defaultdict(float)
    det_hist = defaultdict(int)   # detector class name -> raw detections over the video
    score_log = []
    pconf_sum, pconf_n, ph_sum = defaultdict(float), defaultdict(int), defaultdict(float)
    veh_conf_sum = defaultdict(float)
    foot_fr, foot_pt = defaultdict(list), defaultdict(list)   # tid -> frames / (x, y) ground points (detected frames only)
    vehicle_traj_rows = []
    traj_rows = []                                             # one row per track per frame (coasted frames flagged)

    sbox, last_seen = {}, {}
    coast_state, coast_dead = {}, set()
    frame_rec = {}      # frame idx -> what to draw; rendered in a 2nd pass once final decisions exist
    prev_gray = None
    prob_w, prob_wn, bike_hi = defaultdict(lambda: np.zeros(2)), defaultdict(float), defaultdict(int)

    def wmean(t):   # box-height-weighted mean: big/close crops count more than tiny far ones
        return prob_w[t] / prob_wn[t]
    coast_frames = int(args.coast_sec * fps)

    def disp_of(tid):
        a, b = p_first_xy.get(tid), p_last_xy.get(tid)
        return float("inf") if a is None or b is None else math.hypot(b[0] - a[0], b[1] - a[1])

    def det_info(tid):
        """Detector-side view of a track: (label, mean detector conf, % of its detections classed 'cyclist')."""
        n = max(pconf_n[tid], 1)
        frac = 100.0 * cyc_frames[tid] / n
        return ("cyclist" if frac >= 50.0 else "person", pconf_sum[tid] / n, frac)

    _spd_cache = {}

    def speed_of(t):
        """(speed in body heights per second, seconds visible, net px) from the ground-point history (detected frames only)."""
        fr_, pts_ = foot_fr.get(t, []), foot_pt.get(t, [])
        key = len(fr_)
        c_ = _spd_cache.get(t)
        if c_ and c_[0] == key:
            return c_[1]
        if len(fr_) < 3:
            v_ = (0.0, 0.0, 0.0, "")
        else:
            m_ = motion_summary(fr_, [p[0] for p in pts_], [p[1] for p in pts_], ph_sum[t] / max(track_len[t], 1), fps, args.min_net_px)
            v_ = (float(m_["speed_heights_per_s"]), float(m_["span_s"]), float(m_["net_px"]), m_["direction"])
        _spd_cache[t] = (key, v_)
        return v_

    def xclip_label(t):
        return int(np.argmax(wmean(t)))

    def speed_vote(t, c=None):
        """What the speed rule would make of this track: 0 (bicyclist), 1 (pedestrian) or None (no change)."""
        c = xclip_label(t) if c is None else c
        spd, span, _net, dr_ = speed_of(t)
        if span < args.speed_min_sec or not math.isfinite(spd):
            return None
        if args.speed_lateral_only and dr_ not in ("moving_left", "moving_right"):
            return None
        cp = 100.0 * cyc_frames[t] / max(pconf_n[t], 1)
        if c == 0 and spd < args.walk_max_speed and cp < 50.0:
            return 1
        if c == 1 and spd > args.ride_min_speed and cp >= 50.0:
            return 0
        return None

    def label_of(t):
        c = xclip_label(t)
        if prob_n[t] > 0 and (args.det_veto_pct is not None or args.det_promote_pct is not None) and pconf_n[t] >= args.det_fuse_min_frames:
            cp_ = 100.0 * cyc_frames[t] / max(pconf_n[t], 1)
            if c == 0 and args.det_veto_pct is not None and cp_ < args.det_veto_pct:
                c = 1                       # the detector says person almost all the time: trust it over X-CLIP
            elif c == 1 and args.det_promote_pct is not None and cp_ >= args.det_promote_pct:
                c = 0                       # the detector says cyclist almost all the time
        if args.speed_rule and prob_n[t] > 0:
            v = speed_vote(t, c)
            if v is not None:
                return v
        return c

    def is_static_object(t):
        """A barricade/sign: the ground point neither goes anywhere (net) nor even jitters or sways (path speed). A person waiting to
        cross still sways and shifts, and a person who then crosses has a large net movement, so both stay."""
        spd, span, net, _dr = speed_of(t)
        return span >= args.static_min_sec and net < args.static_max_net_px and spd < args.static_max_speed

    def short_vote(t, n):
        """Would the short-track rule count this track although it is under the minimum duration?"""
        if prob_n[t] == 0 or n < args.short_min_sec * fps or label_of(t) != 0:
            return False
        if args.short_rule_night_only and not is_night_track(t):
            return False
        cp = 100.0 * cyc_frames[t] / max(pconf_n[t], 1)
        return cp >= args.short_det_pct and wmean(t)[0] >= args.short_wbic

    def person_ok(tid, need_len=True):
        n = track_len[tid]
        if n == 0:
            return False
        if need_len:
            nt_ = is_night_track(tid)
            b_sec, p_sec = (night_bic_sec, night_ped_sec) if nt_ else (args.bic_min_sec, args.ped_min_sec)
            if prob_n[tid] > 0:     # X-CLIP has labelled it: judge against its own class's minimum duration
                thr = b_sec if label_of(tid) == 0 else p_sec
            else:
                thr = min(b_sec, p_sec)
            if n < thr * fps:
                if not (args.short_rule and short_vote(tid, n)):
                    return False
        if need_len and args.static_filter and is_static_object(tid):
            return False
        if pconf_n[tid] and pconf_sum[tid] / pconf_n[tid] < args.person_min_conf:
            return False
        if need_len and args.person_min_disp > 0 and disp_of(tid) < args.person_min_disp:
            return False
        return ph_sum[tid] / n >= args.person_min_h * H

    zprev = base + "_zones_preview.png"

    # ---- bin bookkeeping + clip rendering, shared by streaming (during pass 1) and the final render ----
    bin_span, streamed, clip_paths = {}, {}, []       # bin -> [first_frame, last_frame] ; bin -> counts shown in streamed header
    cap2 = cv2.VideoCapture(args.video)          # render reader: advances sequentially, never seeks mid-run
    r2 = {"fi": 0}
    if args.start_frame > 1:
        cap2.set(cv2.CAP_PROP_POS_FRAMES, args.start_frame - 1)
        r2["fi"] = args.start_frame - 1

    def mid_bin(t):
        return bin_of(int(round((first_fi[t] + last_fi[t]) / 2)))

    def fac_of(t):
        hb, hs = zone_hits[t] if t in zone_hits else (0, 0)
        if hb + hs == 0:
            return "unassigned"
        return "bike_lane" if hb >= hs else "sidewalk"

    def snapshot():
        """Decisions with everything seen so far: counted people, their class, and per-bin AI counts."""
        good = {t for t in track_len if person_ok(t)}
        cls_ = {t: label_of(t) for t in good if prob_n[t] > 0}   # == the counted people
        ai = {b: {"bic": 0, "ped": 0, "veh": 0, "bic_bl": 0, "bic_sw": 0, "bic_na": 0}
              for b in range(first_bin, last_bin + 1)}
        for t, c in cls_.items():
            d_ = ai[mid_bin(t)]
            if c == 0:
                d_["bic"] += 1
                d_[{"bike_lane": "bic_bl", "sidewalk": "bic_sw", "unassigned": "bic_na"}[fac_of(t)]] += 1
            else:
                d_["ped"] += 1
        for v in veh_counted:
            ai[bin_of(int(round((veh_first_fi[v] + veh_last_fi[v]) / 2)))]["veh"] += 1
        return good, cls_, ai

    def render_bin(b, good, ai, provisional):
        sp = bin_span.get(b)
        if not sp:
            return
        s0, s1 = bin_start(b), bin_start(b + 1)
        _dn = "night" if (s0.hour >= 20 or s0.hour < 6) else "day"
        final = unique_path(os.path.join(adir, f"{args.run}__{_dn}_{s0:%H%M}-{s1:%H%M}__{test_tag}__{s0:%Y%m%d}.mp4"))
        tmp = os.path.splitext(final)[0] + ".tmp_mp4v.mp4"
        wr = cv2.VideoWriter(tmp, cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H + bar))
        if not wr.isOpened():
            sys.exit(f"ERROR: cannot open VideoWriter for {tmp}")
        d_ = ai[b]
        g_ = gt_bins.get(b)
        gtline = truth_text(g_)
        binline = (f"Bin {s0:%I:%M}-{s1:%I:%M %p} AI {'snapshot' if provisional else 'total'}: "
                   f"Bic {d_['bic']} Ped {d_['ped']} Veh {d_['veh']}")
        while r2["fi"] < sp[1]:
            ok, frame = cap2.read()
            if not ok:
                break
            r2["fi"] += 1
            if r2["fi"] < sp[0]:
                continue
            rec = frame_rec.get(r2["fi"])
            if rec is None:
                break
            if zone_draw and not args.no_draw_zones:
                draw_zones(frame, zone_draw, args.zone_alpha)
                if not os.path.exists(zprev):
                    cv2.imwrite(zprev, frame)
            for vid, name, cx, cy, w, h in rec["veh"]:
                if vid in veh_counted:
                    draw_vehicle(frame, (cx, cy, w, h), vid, name, scale)
            if not args.no_trails:
                cur = r2["fi"]
                lo = cur - int(args.trail_sec * fps) if args.trail_sec > 0 else 0
                for tid, cx, cy, w, h, pr in rec["ppl"]:
                    if tid in good and tid in foot_fr:
                        i0, i1 = bisect.bisect_left(foot_fr[tid], lo), bisect.bisect_right(foot_fr[tid], cur)
                        draw_trail(frame, foot_pt[tid][i0:i1], CLASSES[label_of(tid)][1] if pr is not None else (255, 255, 255),
                                   max(1, int(round(scale * 2))))
            for tid, cx, cy, w, h, pr in rec["ppl"]:
                if tid in good:
                    draw_person(frame, (cx, cy, w, h), tid, None if pr is None else label_of(tid), pr, scale, det_info(tid))
            wr.write(add_header(frame, scale, rec["counts"], r2["fi"], total,
                                f"{clock_of(r2['fi']):%Y-%m-%d %I:%M:%S %p}", binline, gtline))
        wr.release()
        clip_paths.append(finalize_clip(tmp, final))
        print(f"clip written: {clip_paths[-1]}", flush=True)

    dce_net = make_zerodce(args.zerodce_weights, device) if args.enhance == "zerodce" else None
    sahi_roi = tuple(int(float(v)) for v in args.sahi_roi.split(",")) if args.sahi_roi else None
    sahi_imgsz = args.sahi_imgsz or args.sahi_slice
    motion = MotionDiag(fps) if args.motion_diag else None
    enh_preview = {"done": False}
    if args.sahi:
        print(f"E1 SAHI on: slice {args.sahi_slice}px overlap {args.sahi_overlap} imgsz {sahi_imgsz} roi {sahi_roi or 'whole frame'} "
              f"people-only={not args.sahi_all_classes}", flush=True)
    if args.enhance != "none":
        print(f"E2 enhancement on: {args.enhance} when={args.enhance_when} crops={args.enhance_crops}", flush=True)
    if args.speed_rule or args.short_rule or args.motion_diag:
        print(f"E3 on: speed_rule={args.speed_rule} (walk<{args.walk_max_speed}, ride>{args.ride_min_speed} h/s, >= {args.speed_min_sec}s) "
              f"short_rule={args.short_rule} (>= {args.short_min_sec}s, det>={args.short_det_pct}%, wBIC>={args.short_wbic}) motion_diag={args.motion_diag}", flush=True)

    def maybe_enhance(fr, fidx):
        if args.enhance == "none" or (args.enhance_when == "night" and not is_night_frame(fidx)):
            return fr
        out = enhance_frame(fr, args.enhance, args.gamma, args.clahe_clip, dce_net, device)
        if not enh_preview["done"]:
            enh_preview["done"] = True
            cv2.imwrite(base + "_enhance_preview.png", np.concatenate([fr, out], axis=1))
        return out

    def detect_all(img, conf_):
        xy0, cf0, cl0 = predict_arrays(det, img, conf_, args.imgsz, device)
        if args.tta:
            from research_detection import tta_people
            tx, tc, tl = tta_people(det, img, conf_, args.imgsz, args.tta_sizes,
                                    device, people_ids, predict_arrays)
            xy0, cf0, cl0 = np.concatenate([xy0, tx]), np.concatenate([cf0, tc]), np.concatenate([cl0, tl])
            keep = merge_ios(xy0, cf0, cl0, args.sahi_ios)
            xy0, cf0, cl0 = xy0[keep], cf0[keep], cl0[keep]
        if not args.sahi:
            return xy0, cf0, cl0
        sx_, sc_, scl_ = sliced_detect(det, img, conf_, device, args.sahi_slice, args.sahi_overlap, sahi_imgsz, sahi_roi)
        if not args.sahi_all_classes and len(sx_):
            pm_ = np.isin(scl_, people_ids)
            sx_, sc_, scl_ = sx_[pm_], sc_[pm_], scl_[pm_]
        ax = np.concatenate([xy0, sx_]) if len(sx_) else xy0
        ac = np.concatenate([cf0, sc_]) if len(sx_) else cf0
        acl = np.concatenate([cl0, scl_]) if len(sx_) else cl0
        kp = merge_ios(ax, ac, acl, args.sahi_ios)
        return ax[kp], ac[kp], acl[kp]

    next_b = None
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

        det_frame = maybe_enhance(frame, fi)
        xyxy, conf, cls = detect_all(det_frame, night_det_conf if is_night_frame(fi) else args.det_conf)

        for c_ in cls.tolist():
            det_hist[names[c_]] += 1

        if vdet is not None:
            rv = vdet.predict(det_frame, conf=args.det_conf, imgsz=args.veh_imgsz or args.imgsz, verbose=False, device=device)[0]
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
        if motion is not None:
            motion.update(frame, fi, xyxy)

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
            if args.export_vehicle_trajectories:
                vehicle_traj_rows.append([tid, fi, f"{clock_of(fi):%H:%M:%S.%f}", float(cx), float(cy+h/2), float(cx), float(cy), float(w), float(h), 0, vnames[c]])
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
            p_first_xy.setdefault(tid, (float(cx), float(cy + h / 2)))
            p_last_xy[tid] = (float(cx), float(cy + h / 2))
            foot_fr[tid].append(fi)
            foot_pt[tid].append((float(cx), float(cy + h / 2)))
            traj_rows.append([tid, fi, round(float(cx), 1), round(float(cy + h / 2), 1), round(float(cx), 1), round(float(cy), 1),
                              round(float(w), 1), round(float(h), 1), 0])
            for zi, zp in enumerate((bike_poly, side_poly)):
                if zp is not None and cv2.pointPolygonTest(zp, (float(cx), float(cy + h / 2)), False) >= 0:
                    zone_hits[tid][zi] += 1
            crop = crop_square(det_frame if args.enhance_crops else frame, cx, cy, w, h, args.pad)
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
            traj_rows.append([tid, fi, round(float(px), 1), round(float(py + st["box"][3] / 2), 1), round(float(px), 1), round(float(py), 1),
                              round(float(st["box"][2]), 1), round(float(st["box"][3]), 1), 1])

        live_labels = [label_of(t) for t in prob_n if person_ok(t)]
        live_counts = (live_labels.count(0), live_labels.count(1))
        frame_rec[fi] = {"veh": vehicles, "ppl": rec_p,
                         "counts": (live_counts[0], live_counts[1], len(veh_counted))}
        prev_gray = gray
        bsp = bin_span.setdefault(bin_of(fi), [fi, fi])
        bsp[1] = fi
        if args.stream_clips:
            if next_b is None:
                next_b = bin_of(fi)
            t_abs = (fi - 1) / fps + (chunk_idx - 1) * 3600
            while next_b < last_bin and t_abs >= (next_b + 1) * bin_sec + args.stream_delay_sec:
                good_s, _cls_s, ai_s = snapshot()
                streamed[next_b] = {k: ai_s[next_b][k] for k in ("bic", "ped", "veh")}
                render_bin(next_b, good_s, ai_s, provisional=True)
                next_b += 1
        if fi % 100 == 0:
            print(f"frame {fi}/{total if total > 0 else '?'}", flush=True)

    cap.release()
    if fi <= max(0, args.start_frame - 1):
        sys.exit("ERROR: read 0 frames from video")

    # ---- final render: bins not already streamed, drawn with the final decisions
    print("rendering remaining annotated clips ...", flush=True)
    good_p, final_cls, bin_ai = snapshot()
    for b in range(first_bin, last_bin + 1):
        if b not in streamed:
            render_bin(b, good_p, bin_ai, provisional=False)
    cap2.release()
    stream_mismatch = {b: {"clip_header": streamed[b], "final": {k: bin_ai[b][k] for k in ("bic", "ped", "veh")}}
                       for b in streamed if streamed[b] != {k: bin_ai[b][k] for k in ("bic", "ped", "veh")}}
    if args.stream_clips:
        print(f"streamed bins: {sorted(streamed)}; bins whose streamed header differs from the final counts: "
              f"{sorted(stream_mismatch) if stream_mismatch else 'none'}")

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
            final = label_of(tid)   # X-CLIP box-height-weighted mean (+ speed rule if on)
            fl = f"{min(by_tid[tid])}-{max(by_tid[tid])}"
            ok_ = person_ok(tid)
            if ok_:
                counted[final].add(tid)
            label_txt = CLASSES[final][0] if ok_ else f"(filtered: was {CLASSES[final][0]}, not counted)"
            print(f"{tid:5d} | {track_len[tid]:6d} | {secs:4.1f} | {prob_n[tid]:6d} | {fl:>13s} | {mc:.2f} | {mh:6.0f} | {m[0]:.2f} | {m[1]:.2f} | {mw[0]:.2f} | {mw[1]:.2f} | {100.0 * bike_hi[tid] / prob_n[tid]:.0f}% | {cf:.0f}% | {label_txt}")
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
    print(f"Annotated clips ({len(clip_paths)}): {adir}\nScores: {log_path}")

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
                     "facility", "secs", "mean_conf", "weighted_bicyclist", "weighted_pedestrian", "disp_px",
                     "det_label", "det_cyclist_pct", "xclip_label", "labels_agree"])
        for t in sorted(track_len):
            lab = CLASSES[label_of(t)][0] if prob_n[t] > 0 else "unscored"
            wb, wp = (wmean(t) if prob_n[t] > 0 else (float("nan"), float("nan")))
            w_.writerow([t, lab, int(t in final_cls), f"{clock_of(first_fi[t]):%Y-%m-%d %H:%M:%S}",
                         f"{clock_of(last_fi[t]):%Y-%m-%d %H:%M:%S}", mid_bin(t), fac_of(t),
                         round(track_len[t] / fps, 2), round(pconf_sum[t] / max(pconf_n[t], 1), 3),
                         round(float(wb), 3), round(float(wp), 3), round(min(disp_of(t), 99999.0), 1),
                         det_info(t)[0], round(det_info(t)[2], 1), lab,
                         (int((det_info(t)[0] == "cyclist") == (lab == "BICYCLIST")) if lab != "unscored" else "")])
    # ---- v17 outputs: trajectories, motion summary, split candidates (nothing here changes the counts) ----
    lab_of = {t: (CLASSES[label_of(t)][0] if prob_n[t] > 0 else "unscored") for t in track_len}
    traj_path = unique_path(base + "_trajectories.csv")
    with open(traj_path, "w", newline="") as f:
        w_ = csv.writer(f)
        w_.writerow(["track_id", "frame", "time", "foot_x", "foot_y", "box_cx", "box_cy", "box_w", "box_h", "coasted",
                     "label", "counted"])
        for tid, fr_, fx_, fy_, bx_, by_, bw_, bh_, co_ in traj_rows:
            w_.writerow([tid, fr_, f"{clock_of(fr_):%H:%M:%S}.{int(clock_of(fr_).microsecond / 1000):03d}", fx_, fy_, bx_, by_, bw_, bh_, co_,
                         lab_of.get(tid, ""), int(tid in final_cls)])
    mot_path = unique_path(base + "_track_motion.csv")
    info, dir_n = {}, defaultdict(int)
    with open(mot_path, "w", newline="") as f:
        w_ = csv.writer(f)
        w_.writerow(["track_id", "label", "counted", "facility", "first_time", "last_time", "secs_visible", "start_x", "start_y",
                     "end_x", "end_y", "path_px", "net_px", "dx", "dy", "path_speed_px_s", "net_speed_px_s",
                     "speed_heights_per_s", "direction", "det_label", "mean_box_h"])
        for t in sorted(foot_fr):
            fr_, pts_ = foot_fr[t], foot_pt[t]
            mh_ = ph_sum[t] / max(track_len[t], 1)
            m_ = motion_summary(fr_, [p[0] for p in pts_], [p[1] for p in pts_], mh_, fps, args.min_net_px)
            if t in final_cls:
                dir_n[(lab_of[t], m_["direction"])] += 1
            vk = max(3, min(len(fr_) - 1, int(fps * 0.5)))
            v_ = ((pts_[-1][0] - pts_[-1 - vk][0]) / (fr_[-1] - fr_[-1 - vk]), (pts_[-1][1] - pts_[-1 - vk][1]) / (fr_[-1] - fr_[-1 - vk])) if len(fr_) > vk else (0.0, 0.0)
            info[t] = {"first": fr_[0], "last": fr_[-1], "n": track_len[t], "p0": pts_[0], "p1": pts_[-1], "v": v_, "label": lab_of[t]}
            w_.writerow([t, lab_of[t], int(t in final_cls), fac_of(t), f"{clock_of(fr_[0]):%H:%M:%S}", f"{clock_of(fr_[-1]):%H:%M:%S}",
                         round(track_len[t] / fps, 2), round(pts_[0][0], 1), round(pts_[0][1], 1), round(pts_[-1][0], 1),
                         round(pts_[-1][1], 1), round(m_["path_px"], 1), round(m_["net_px"], 1), round(m_["dx"], 1),
                         round(m_["dy"], 1), round(m_["path_speed_pxs"], 1), round(m_["net_speed_pxs"], 1),
                         round(m_["speed_heights_per_s"], 2), m_["direction"], det_info(t)[0], round(mh_, 1)])
    split_path = unique_path(base + "_split_candidates.csv")
    thr_ = min(args.ped_min_sec, args.bic_min_sec)
    srows = split_candidates(info, fps, args.split_gap_sec, args.split_px, 0.5, thr_)
    with open(split_path, "w", newline="") as f:
        w_ = csv.writer(f)
        w_.writerow(["track_a", "track_b", "gap_s", "dist_px", "secs_a", "secs_b", "secs_a_plus_b", "label_a", "label_b",
                     "a_or_b_alone_passes_min", "joined_passes_min"])
        w_.writerows(srows)
    n_new = sum(1 for r_ in srows if not r_[9] and r_[10])
    print(f"Trajectories: {traj_path}\nTrack motion: {mot_path}\nSplit candidates: {split_path} "
          f"({len(srows)} pairs; {n_new} would pass the {thr_:g} s minimum only if joined)")
    print(f"Counted tracks by (X-CLIP label, direction): {dict(dir_n)}")

    # ---- v19 outputs: rules audit (always) and motion candidates (--motion-diag) ----
    audit_path = unique_path(base + "_rules_audit.csv")
    with open(audit_path, "w", newline="") as f:
        w_ = csv.writer(f)
        w_.writerow(["track_id", "first_time", "last_time", "secs", "xclip_label", "weighted_bicyclist", "det_cyclist_pct", "speed_heights_per_s",
                     "speed_span_s", "net_px", "direction", "night_track", "final_label", "counted", "speed_rule_vote", "short_rule_would_count",
                     "passes_min_duration"])
        for t in sorted(track_len):
            if prob_n[t] == 0:
                continue
            spd_, span_, net_, _dr = speed_of(t)
            fr_, pts_ = foot_fr.get(t, []), foot_pt.get(t, [])
            dir_ = motion_summary(fr_, [p[0] for p in pts_], [p[1] for p in pts_], ph_sum[t] / max(track_len[t], 1), fps, args.min_net_px)["direction"] if len(fr_) > 2 else ""
            sv_ = speed_vote(t)
            xl_ = xclip_label(t)
            thr_x = (night_bic_sec if xl_ == 0 else night_ped_sec) if is_night_track(t) else (args.bic_min_sec if xl_ == 0 else args.ped_min_sec)
            cp_ = 100.0 * cyc_frames[t] / max(pconf_n[t], 1)
            would_short = int(prob_n[t] > 0 and track_len[t] < thr_x * fps and track_len[t] >= args.short_min_sec * fps
                              and xl_ == 0 and cp_ >= args.short_det_pct and wmean(t)[0] >= args.short_wbic)
            w_.writerow([t, f"{clock_of(first_fi[t]):%H:%M:%S}", f"{clock_of(last_fi[t]):%H:%M:%S}", round(track_len[t] / fps, 2), CLASSES[xl_][0],
                         round(float(wmean(t)[0]), 3), round(cp_, 1), round(spd_, 2), round(span_, 1), round(net_, 1), dir_, int(is_night_track(t)),
                         CLASSES[label_of(t)][0], int(t in final_cls), "" if sv_ is None else CLASSES[sv_][0], would_short,
                         int(track_len[t] >= thr_x * fps)])
    print(f"Rules audit: {audit_path}")
    if motion is not None:
        mrows = motion.finish()
        mpath = unique_path(base + "_motion_candidates.csv")
        with open(mpath, "w", newline="") as f:
            w_ = csv.writer(f)
            w_.writerow(["cand", "first_time", "last_time", "secs", "n_frames", "net_px", "mean_box_w", "mean_box_h", "mean_x", "mean_y"])
            for i, r_ in enumerate(mrows, 1):
                w_.writerow([i, f"{clock_of(r_['first']):%H:%M:%S}", f"{clock_of(r_['last']):%H:%M:%S}", round(r_["secs"], 2), r_["n"],
                             round(r_["net_px"], 1), round(r_["mean_w"], 1), round(r_["mean_h"], 1), round(r_["x"], 1), round(r_["y"], 1)])
        cs = MotionDiag.contact_sheet(mrows, clock_of, base + "_motion_candidates.png")
        print(f"Motion candidates: {len(mrows)} unexplained moving blobs >= 0.7 s -> {mpath}  contact sheet: {cs}")

    vehicle_traj_path = None
    if args.export_vehicle_trajectories:
        vehicle_traj_path = unique_path(base + "_vehicle_trajectories.csv")
        with open(vehicle_traj_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["track_id", "frame", "time", "foot_x", "foot_y", "box_cx", "box_cy", "box_w", "box_h", "coasted", "label", "counted"])
            writer.writerows(row + [int(row[0] in veh_counted)] for row in vehicle_traj_rows)
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
        "stream_clips": bool(args.stream_clips), "streamed_bins": sorted(streamed),
        "stream_header_mismatch_bins": {str(k): v for k, v in stream_mismatch.items()},
        "annotated_clips": clip_paths, "bin_counts_csv": bin_path, "tracks_csv": trk_path,
        "scores_csv": log_path, "track_stats_csv": stats_path,
        "vehicle_trajectories_csv": vehicle_traj_path,
        "trajectories_csv": traj_path, "track_motion_csv": mot_path, "split_candidates_csv": split_path,
        "runtime_s": round(time.time() - t_start, 1),
        "finished": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    rl_path = unique_path(os.path.join(ldir, f"{tag}_run_log.json"))
    with open(rl_path, "w") as f:
        json.dump(runlog, f, indent=2, default=str)
    print(f"Bin counts: {bin_path}\nTracks: {trk_path}\nRun log: {rl_path}\nRuntime: {runlog['runtime_s']} s")


if __name__ == "__main__":
    main()
