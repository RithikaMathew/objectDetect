#!/usr/bin/env python3
"""
Cyclist detector comparison v2 — adds Method F (YOLO26x) and Method G
(motion-guided crop detection) on top of the v1 methods (A-E, unchanged).

Standalone file: does not import from compare_detectors.py, so v1's
comparison run keeps working untouched even if this file has a bug.

Method F: YOLO26x + fusion
  Same fusion pipeline as A/B, just a newer checkpoint. YOLO26 (Ultralytics,
  Jan 2026) adds STAL (Small-Target-Aware Label Assignment) and ProgLoss,
  both aimed specifically at the "distant/tiny object gets starved out"
  problem this whole comparison is about.

Method G: RT-DETR-l + fusion + motion-guided cropping
  Addresses the "empty road vs. new object" idea directly: since the camera
  is fixed, background subtraction (MOG2) flags *where* something changed
  frame-to-frame. Instead of running the detector on the whole (downsampled)
  frame, or tiling the whole frame like Method E, we only run it on a padded
  crop around each moving blob, at that crop's native resolution. A distant
  rider that's a handful of pixels in the full frame becomes a much larger
  fraction of a small crop, without paying Method E's cost of tiling static,
  motionless background over and over.
  Requires MOG2_WARMUP_FRAMES of "no detections" at the start of the video
  while the background model builds up — expected, not a bug.

Usage: identical to compare_detectors.py, with methods A-G instead of A-E.
    python compare_detectors_v2.py --method G \
        --video /orange/xiangyan/rithika/vision/vision3/test.mp4 \
        --weights-dir /orange/xiangyan/rithika/vision/vision3/weights \
        --outdir /orange/xiangyan/rithika/vision/vision3/pilot_output/compare_v2
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

# --- Method G tuning knobs ---
MOG2_WARMUP_FRAMES = 30      # frames spent building the background model before trusting it
MOG2_HISTORY = 500
MOG2_VAR_THRESHOLD = 16
MIN_BLOB_AREA = 150          # ignore motion specks smaller than this (px^2) -- noise, not a rider
PAD_FRAC = 1.0               # expand each motion blob's crop by 100% of its own size on each side
MIN_CROP_SIZE = 320          # floor crop size so a tiny blob still gets a workable-resolution crop
MAX_CROPS_PER_FRAME = 6      # cap compute if a frame has lots of simultaneous motion
NMS_IOU_THRESH = 0.5         # merge duplicate detections where two crops overlap the same rider


# ---------------------------------------------------------------------------
# Person + bicycle -> "cyclist" fusion (identical to v1 -- see compare_detectors.py
# for the rationale behind the size-plausibility check and per-class thresholds)
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
# Generic video-processing pipeline (identical to v1)
# ---------------------------------------------------------------------------

def process_video(video_path: str, output_path: str, get_detections_fn,
                   method_label: str, conf_threshold: float = 0.25):
    video_info = sv.VideoInfo.from_video_path(video_path)

    tracker = sv.ByteTrack(
        frame_rate=video_info.fps,
        track_activation_threshold=0.15,
        lost_track_buffer=int(video_info.fps * 3),
        minimum_matching_threshold=0.8,
    )
    box_annotator = sv.BoxAnnotator(thickness=2)
    label_annotator = sv.LabelAnnotator(text_scale=0.5, text_thickness=1)

    seen_ids = set()
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
                seen_ids.update(detections.tracker_id.tolist())

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
        # YOLO26x: newer checkpoint, same fusion pipeline as A/B. STAL +
        # ProgLoss target exactly the "small object gets starved out"
        # problem this comparison is about -- see module docstring.
        model = YOLO(str(wd / "yolo26x.pt"))

        def fn(frame):
            r = model.predict(frame, classes=[COCO_PERSON, COCO_BICYCLE], conf=0.15,
                               imgsz=IMG_SIZE, device=device, verbose=False)[0]
            return fuse_person_bicycle(sv.Detections.from_ultralytics(r), COCO_PERSON, COCO_BICYCLE)
        return fn, "F: YOLO26x+fusion"

    if method == "G":
        return build_motion_guided_detector(wd, device)

    raise ValueError(f"unknown method: {method!r} (expected one of A/B/C/D/E/F/G)")


def build_motion_guided_detector(wd: Path, device: str):
    """Method G: background subtraction picks out moving regions; the
    detector only runs on padded crops around those regions, at native
    resolution, instead of the whole (downsampled) frame. See module
    docstring for the rationale.
    """
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

        # Cap compute: only chase the largest motion regions if there are many.
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
        # Two overlapping crops can both catch the same rider near their shared
        # border -- collapse duplicates before handing off to the tracker.
        if hasattr(merged, "with_nms"):
            merged = merged.with_nms(threshold=NMS_IOU_THRESH)
        return merged

    return fn, "G: RT-DETR-l+fusion+motion-guided-crop"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--method", required=True, choices=list("ABCDEFG"))
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
