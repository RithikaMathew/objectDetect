#!/usr/bin/env python3
"""
Cyclist detector comparison v3 — fixes tracker tuning that caused double
counting, and adds Method H (upscale + tiling) on top of v2 (A-G unchanged).
Standalone file: does not import from compare_detectors.py or
compare_detectors_v2.py, so those keep working untouched.

WHAT CHANGED FROM v2 AND WHY
-----------------------------
Method F counted the cyclist twice with no code bug in the fusion logic —
the ByteTrack config was mistuned for a target this small:

  - track_activation_threshold=0.15 is far too low. In ByteTrack, this is
    the bar a detection must clear to START a brand-new track (as opposed
    to only being allowed to extend an existing one). At 0.15, almost any
    detection can spawn a "new" cyclist. Raised to 0.45 here.
  - minimum_matching_threshold=0.8 (IoU) is too strict for a tiny,
    jittery box — a couple pixels of frame-to-frame movement is enough
    to drop IoU below 0.8 and break the match, forcing a new track on
    the next hit. Loosened to 0.3.
  - There was no minimum-hit-count gate: a track was counted into
    seen_ids the instant it existed, even from a single flickery frame.
    Added MIN_TRACK_HITS below — a track only counts once it's been
    matched on at least this many frames.

Method H: RT-DETR-l + 2x bicubic upscale + tiling
  Methods E and G already tested "look in the right place" fixes
  (tiling, motion-guided cropping) and neither recovered distance
  recall. That points at a different failure mode: not enough pixels
  on target, not a bad search strategy. H tests that directly by
  upscaling each tile 2x (bicubic, zero new dependencies) before
  detection — the cheapest version of the super-resolution-then-tile
  approach used in recent traffic-surveillance small-object work.
  If this helps, it's worth trying a real SR model (e.g. Real-ESRGAN)
  next; if it doesn't, the bottleneck is more likely the detector's
  training distribution than raw pixel count, which argues for
  prioritizing fine-tuning over further inference-time tricks.

Usage: identical to compare_detectors_v2.py, with methods A-H.
    python compare_detectors_v3.py --method F \
        --video /orange/xiangyan/rithika/vision/vision3/test.mp4 \
        --weights-dir /orange/xiangyan/rithika/vision/vision3/weights \
        --outdir /orange/xiangyan/rithika/vision/vision3/pilot_output/compare_v3
"""
import argparse
import json
import os
import time
from pathlib import Path

import cv2
import numpy as np
import supervision as sv
import torch
from ultralytics import YOLO, RTDETR

COCO_PERSON, COCO_BICYCLE = 0, 1
VISDRONE_BICYCLE = 2
IMG_SIZE = 640

# --- Method G tuning knobs (unchanged from v2) ---
MOG2_WARMUP_FRAMES = 30
MOG2_HISTORY = 500
MOG2_VAR_THRESHOLD = 16
MIN_BLOB_AREA = 150
PAD_FRAC = 1.0
MIN_CROP_SIZE = 320
MAX_CROPS_PER_FRAME = 6
NMS_IOU_THRESH = 0.5

# --- Method H tuning knobs ---
UPSCALE_FACTOR = 2.0          # bicubic upscale applied before tiling
H_SLICE_WH = (640, 640)       # tile size, applied to the *upscaled* frame
H_OVERLAP = (0.2, 0.2)

# --- Tracker tuning (fixes the F double-count bug — see module docstring) ---
TRACK_ACTIVATION_THRESHOLD = 0.45   # was 0.15 -- bar for starting a NEW track
MIN_MATCHING_THRESHOLD = 0.3        # was 0.8 -- bar for matching an existing track
MIN_TRACK_HITS = 5                  # a track must be matched this many frames
                                     # before it counts as a real cyclist
                                     # (~0.15-0.2s at typical traffic-cam fps;
                                     #  filters one-off flicker, not real riders)


# ---------------------------------------------------------------------------
# Person + bicycle -> "cyclist" fusion (identical to v1/v2)
# ---------------------------------------------------------------------------

def _iou(box_a, box_b):
    xa1, ya1, xa2, ya2 = box_a
    xb1, yb1, xb2, yb2 = box_b
    inter_x1, inter_y1 = max(xa1, xb1), max(ya1, yb1)
    inter_x2, inter_y2 = min(xa2, xb2), min(ya2, yb2)
    inter_w, inter_h = max(0, inter_x2 - inter_x1), max(0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h
    area_a = max(0, xa2 - xa1) * max(0, ya2 - ya1)
    area_b = max(0, xb2 - xb1) * max(0, yb2 - yb1)
    union = area_a + area_b - inter_area
    return inter_area / union if union > 0 else 0.0


def _center_in_box(box_inner, box_outer, pad_frac=0.15):
    cx = (box_inner[0] + box_inner[2]) / 2
    cy = (box_inner[1] + box_inner[3]) / 2
    x1, y1, x2, y2 = box_outer
    w, h = x2 - x1, y2 - y1
    x1, x2 = x1 - w * pad_frac, x2 + w * pad_frac
    y1, y2 = y1 - h * pad_frac, y2 + h * pad_frac
    return x1 <= cx <= x2 and y1 <= cy <= y2


def _area(box):
    return max(0, box[2] - box[0]) * max(0, box[3] - box[1])


def fuse_person_bicycle(detections: sv.Detections, person_id: int, bicycle_id: int,
                         person_conf_thresh: float = 0.25,
                         bicycle_conf_thresh: float = 0.35,
                         iou_thresh: float = 0.05,
                         max_area_ratio: float = 8.0) -> sv.Detections:
    if len(detections) == 0:
        return detections[np.array([], dtype=bool)]

    person_idx = np.where((detections.class_id == person_id) &
                           (detections.confidence >= person_conf_thresh))[0]
    bike_idx = np.where((detections.class_id == bicycle_id) &
                         (detections.confidence >= bicycle_conf_thresh))[0]

    if len(person_idx) == 0 or len(bike_idx) == 0:
        return detections[np.array([], dtype=bool)]

    pairs = []
    for p_i in person_idx:
        for b_i in bike_idx:
            area_a, area_b = _area(detections.xyxy[p_i]), _area(detections.xyxy[b_i])
            if area_a == 0 or area_b == 0:
                continue
            ratio = max(area_a, area_b) / min(area_a, area_b)
            if ratio > max_area_ratio:
                continue

            score = _iou(detections.xyxy[p_i], detections.xyxy[b_i])
            if score < iou_thresh:
                if _center_in_box(detections.xyxy[b_i], detections.xyxy[p_i]) or \
                   _center_in_box(detections.xyxy[p_i], detections.xyxy[b_i]):
                    score = max(score, iou_thresh)
            if score >= iou_thresh:
                pairs.append((score, p_i, b_i))

    pairs.sort(key=lambda t: t[0], reverse=True)
    used_p, used_b = set(), set()
    matched = []
    for score, p_i, b_i in pairs:
        if p_i in used_p or b_i in used_b:
            continue
        used_p.add(p_i)
        used_b.add(b_i)
        matched.append((p_i, b_i))

    if not matched:
        return detections[np.array([], dtype=bool)]

    boxes, confs = [], []
    for p_i, b_i in matched:
        px1, py1, px2, py2 = detections.xyxy[p_i]
        bx1, by1, bx2, by2 = detections.xyxy[b_i]
        boxes.append([min(px1, bx1), min(py1, by1), max(px2, bx2), max(py2, by2)])
        confs.append(float((detections.confidence[p_i] + detections.confidence[b_i]) / 2))

    return sv.Detections(
        xyxy=np.array(boxes, dtype=np.float32),
        confidence=np.array(confs, dtype=np.float32),
        class_id=np.zeros(len(boxes), dtype=int),
    )


# ---------------------------------------------------------------------------
# Generic video-processing pipeline (tracker tuning + hit-count gate fixed)
# ---------------------------------------------------------------------------

def process_video(video_path: str, output_path: str, get_detections_fn,
                   method_label: str, conf_threshold: float = 0.25):
    video_info = sv.VideoInfo.from_video_path(video_path)

    tracker = sv.ByteTrack(
        frame_rate=video_info.fps,
        track_activation_threshold=TRACK_ACTIVATION_THRESHOLD,
        lost_track_buffer=int(video_info.fps * 3),
        minimum_matching_threshold=MIN_MATCHING_THRESHOLD,
    )
    box_annotator = sv.BoxAnnotator(thickness=2)
    label_annotator = sv.LabelAnnotator(text_scale=0.5, text_thickness=1)

    hit_counts = {}     # tracker_id -> number of frames matched so far
    seen_ids = set()    # tracker_ids that have cleared MIN_TRACK_HITS
    frame_count = 0
    t0 = time.time()

    with sv.VideoSink(target_path=output_path, video_info=video_info) as sink:
        for frame in sv.get_video_frames_generator(source_path=video_path):
            frame_count += 1
            detections = get_detections_fn(frame)
            if len(detections) > 0:
                detections = detections[detections.confidence >= conf_threshold]
            detections = tracker.update_with_detections(detections)

            if detections.tracker_id is not None:
                for tid in detections.tracker_id.tolist():
                    hit_counts[tid] = hit_counts.get(tid, 0) + 1
                    if hit_counts[tid] >= MIN_TRACK_HITS:
                        seen_ids.add(tid)

            labels = [f"cyclist #{tid} {conf:.2f}"
                      for tid, conf in zip(detections.tracker_id, detections.confidence)] \
                if detections.tracker_id is not None else []

            annotated = box_annotator.annotate(scene=frame.copy(), detections=detections)
            annotated = label_annotator.annotate(annotated, detections=detections, labels=labels)

            cv2.putText(annotated, f"{method_label} | unique cyclists so far: {len(seen_ids)}",
                        (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 4, cv2.LINE_AA)
            cv2.putText(annotated, f"{method_label} | unique cyclists so far: {len(seen_ids)}",
                        (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)

            sink.write_frame(annotated)

    elapsed = time.time() - t0
    return {
        "method": method_label,
        "output_path": output_path,
        "unique_cyclists": len(seen_ids),
        "frames": frame_count,
        "seconds": round(elapsed, 1),
        "fps": round(frame_count / elapsed, 2) if elapsed > 0 else 0,
    }


# ---------------------------------------------------------------------------
# Per-method detector builders
# ---------------------------------------------------------------------------

def build_detector(method: str, weights_dir: str, device: str):
    wd = Path(weights_dir)

    if method == "A":
        model = YOLO(str(wd / "yolov8x.pt"))

        def fn(frame):
            r = model.predict(frame, classes=[COCO_PERSON, COCO_BICYCLE], conf=0.15,
                               imgsz=IMG_SIZE, device=device, verbose=False)[0]
            return fuse_person_bicycle(sv.Detections.from_ultralytics(r), COCO_PERSON, COCO_BICYCLE)
        return fn, "A: YOLOv8x+fusion"

    if method == "B":
        model = YOLO(str(wd / "yolo11x.pt"))

        def fn(frame):
            r = model.predict(frame, classes=[COCO_PERSON, COCO_BICYCLE], conf=0.15,
                               imgsz=IMG_SIZE, device=device, verbose=False)[0]
            return fuse_person_bicycle(sv.Detections.from_ultralytics(r), COCO_PERSON, COCO_BICYCLE)
        return fn, "B: YOLO11x+fusion"

    if method == "C":
        model = RTDETR(str(wd / "rtdetr-l.pt"))

        def fn(frame):
            r = model.predict(frame, classes=[COCO_PERSON, COCO_BICYCLE], conf=0.15,
                               imgsz=IMG_SIZE, device=device, verbose=False)[0]
            return fuse_person_bicycle(sv.Detections.from_ultralytics(r), COCO_PERSON, COCO_BICYCLE)
        return fn, "C: RT-DETR-l+fusion"

    if method == "D":
        model = YOLO(str(wd / "visdrone_yolo11x.pt"))

        def fn(frame):
            r = model.predict(frame, classes=[VISDRONE_BICYCLE], conf=0.15,
                               imgsz=IMG_SIZE, device=device, verbose=False)[0]
            dets = sv.Detections.from_ultralytics(r)
            dets.class_id = np.zeros(len(dets), dtype=int)
            return dets
        return fn, "D: YOLO11x-VisDrone (direct)"

    if method == "E":
        model = RTDETR(str(wd / "rtdetr-l.pt"))

        def tile_fn(image_slice: np.ndarray) -> sv.Detections:
            r = model.predict(image_slice, classes=[COCO_PERSON, COCO_BICYCLE], conf=0.15,
                               device=device, verbose=False)[0]
            return fuse_person_bicycle(sv.Detections.from_ultralytics(r), COCO_PERSON, COCO_BICYCLE)

        slicer = sv.InferenceSlicer(
            callback=tile_fn,
            slice_wh=(640, 640),
            overlap_ratio_wh=(0.2, 0.2),
            iou_threshold=0.3,
        )

        def fn(frame):
            return slicer(image=frame)
        return fn, "E: RT-DETR-l+fusion+tiling"

    if method == "F":
        model = YOLO(str(wd / "yolo26x.pt"))

        def fn(frame):
            r = model.predict(frame, classes=[COCO_PERSON, COCO_BICYCLE], conf=0.15,
                               imgsz=IMG_SIZE, device=device, verbose=False)[0]
            return fuse_person_bicycle(sv.Detections.from_ultralytics(r), COCO_PERSON, COCO_BICYCLE)
        return fn, "F: YOLO26x+fusion"

    if method == "G":
        return build_motion_guided_detector(wd, device)

    if method == "H":
        return build_upscale_tile_detector(wd, device)

    raise ValueError(f"unknown method: {method!r} (expected one of A/B/C/D/E/F/G/H)")


def build_motion_guided_detector(wd: Path, device: str):
    """Method G (unchanged from v2)."""
    model = RTDETR(str(wd / "rtdetr-l.pt"))
    bg_sub = cv2.createBackgroundSubtractorMOG2(
        history=MOG2_HISTORY, varThreshold=MOG2_VAR_THRESHOLD, detectShadows=False
    )
    morph_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    state = {"frame_idx": 0}

    def fn(frame: np.ndarray) -> sv.Detections:
        state["frame_idx"] += 1
        fg_mask = bg_sub.apply(frame)

        if state["frame_idx"] <= MOG2_WARMUP_FRAMES:
            return sv.Detections.empty()

        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, morph_kernel, iterations=1)
        fg_mask = cv2.dilate(fg_mask, morph_kernel, iterations=2)
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        blobs = []
        for c in contours:
            area = cv2.contourArea(c)
            if area < MIN_BLOB_AREA:
                continue
            x, y, w, h = cv2.boundingRect(c)
            blobs.append((x, y, x + w, y + h))

        if not blobs:
            return sv.Detections.empty()

        blobs.sort(key=lambda b: (b[2] - b[0]) * (b[3] - b[1]), reverse=True)
        blobs = blobs[:MAX_CROPS_PER_FRAME]

        H, W = frame.shape[:2]
        all_xyxy, all_conf = [], []

        for (x1, y1, x2, y2) in blobs:
            bw, bh = x2 - x1, y2 - y1
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            half_w = max(bw * (1 + PAD_FRAC) / 2, MIN_CROP_SIZE / 2)
            half_h = max(bh * (1 + PAD_FRAC) / 2, MIN_CROP_SIZE / 2)
            cx1, cy1 = int(max(0, cx - half_w)), int(max(0, cy - half_h))
            cx2, cy2 = int(min(W, cx + half_w)), int(min(H, cy + half_h))
            if cx2 <= cx1 or cy2 <= cy1:
                continue

            crop = frame[cy1:cy2, cx1:cx2]
            r = model.predict(crop, classes=[COCO_PERSON, COCO_BICYCLE], conf=0.15,
                               device=device, verbose=False)[0]
            dets = sv.Detections.from_ultralytics(r)
            fused = fuse_person_bicycle(dets, COCO_PERSON, COCO_BICYCLE)
            if len(fused) == 0:
                continue

            xyxy = fused.xyxy.copy()
            xyxy[:, [0, 2]] += cx1
            xyxy[:, [1, 3]] += cy1
            all_xyxy.append(xyxy)
            all_conf.append(fused.confidence)

        if not all_xyxy:
            return sv.Detections.empty()

        xyxy = np.concatenate(all_xyxy, axis=0).astype(np.float32)
        conf = np.concatenate(all_conf, axis=0).astype(np.float32)
        merged = sv.Detections(xyxy=xyxy, confidence=conf, class_id=np.zeros(len(xyxy), dtype=int))
        if hasattr(merged, "with_nms"):
            merged = merged.with_nms(threshold=NMS_IOU_THRESH)
        return merged

    return fn, "G: RT-DETR-l+fusion+motion-guided-crop"


def build_upscale_tile_detector(wd: Path, device: str):
    """Method H: bicubic upscale the whole frame before tiling. Tests
    whether the bottleneck is raw pixel count on target (fixable at
    inference time) vs. training distribution (needs fine-tuning) --
    see module docstring for why this test is informative either way.
    """
    model = RTDETR(str(wd / "rtdetr-l.pt"))

    def tile_fn(image_slice: np.ndarray) -> sv.Detections:
        r = model.predict(image_slice, classes=[COCO_PERSON, COCO_BICYCLE], conf=0.15,
                           device=device, verbose=False)[0]
        return fuse_person_bicycle(sv.Detections.from_ultralytics(r), COCO_PERSON, COCO_BICYCLE)

    slicer = sv.InferenceSlicer(
        callback=tile_fn,
        slice_wh=H_SLICE_WH,
        overlap_ratio_wh=H_OVERLAP,
        iou_threshold=0.3,
    )

    def fn(frame):
        upscaled = cv2.resize(frame, None, fx=UPSCALE_FACTOR, fy=UPSCALE_FACTOR,
                               interpolation=cv2.INTER_CUBIC)
        dets = slicer(image=upscaled)
        if len(dets) > 0:
            dets.xyxy = dets.xyxy / UPSCALE_FACTOR  # back to original frame coords
        return dets

    return fn, f"H: RT-DETR-l+fusion+{UPSCALE_FACTOR:.0f}x-upscale+tiling"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--method", required=True, choices=list("ABCDEFGH"))
    ap.add_argument("--video", required=True, help="Path to input video")
    ap.add_argument("--weights-dir", required=True,
                     help="Shared cache dir containing yolov8x.pt, yolo11x.pt, "
                          "rtdetr-l.pt, visdrone_yolo11x.pt, yolo26x.pt "
                          "(see prefetch_weights_v2.py)")
    ap.add_argument("--outdir", required=True,
                     help="Directory for the annotated output video + summary JSON")
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[method {args.method}] device={device}")
    if device == "cpu":
        print("WARNING: no GPU visible to this job — check --gres/--gpus in the SLURM script.")

    os.makedirs(args.outdir, exist_ok=True)
    detect_fn, label = build_detector(args.method, args.weights_dir, device)
    out_video = os.path.join(args.outdir, f"output_{args.method}.mp4")

    summary = process_video(args.video, out_video, detect_fn, label)

    summary_path = os.path.join(args.outdir, f"summary_{args.method}.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
