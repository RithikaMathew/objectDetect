#!/usr/bin/env python3
"""
Cyclist detector comparison — HPC version of the Colab notebook.

Fixes applied vs. the last Colab run (which regressed):
  1. IMG_SIZE reverted to 640 for methods A/B/C/D. Raising it to 1280 didn't
     help distant recall — it pushed these COCO/VisDrone checkpoints outside
     the scale they were calibrated at and broke close-range detection
     entirely (that's why A/B/C went to 0 unique_cyclists). The distance
     problem is handled by Method E's tiling instead, which doesn't have
     this side effect because each tile is still processed near its native
     scale.
  2. fuse_person_bicycle() now requires per-class confidence thresholds
     (bicycle detections are noisier than person, so they need a higher bar)
     AND a size-plausibility check between the matched person/bicycle boxes.
     The previous version paired ANY person+bicycle with iou >= 0.03 or a
     loose containment fallback, with no sanity check on relative size —
     which is exactly how a spurious "bicycle" hit on grass got glued to an
     unrelated pedestrian and counted as a cyclist.

Usage (single method, single video):
    python compare_detectors.py --method A \
        --video /orange/xiangyan/rithika/vision/vision3/test.mp4 \
        --weights-dir /orange/xiangyan/rithika/vision/vision3/weights \
        --outdir /orange/xiangyan/rithika/vision/vision3/pilot_output/compare

Run once per method (A-E); see run_compare_array.slurm for running all five
in parallel across GPUs via a SLURM job array.
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
IMG_SIZE = 640  # reverted from 1280 — see module docstring, point 1


# ---------------------------------------------------------------------------
# Person + bicycle -> "cyclist" fusion
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
    """Greedily pair person & bicycle boxes into 'cyclist' detections.

    Two guards added vs. the original version:
      - per-class confidence floor (bicycle_conf_thresh is stricter, since
        bicycle is the noisier class and the one most prone to false
        positives on grass/background clutter)
      - max_area_ratio: rejects a pair whose boxes are wildly different
        sizes (e.g. a tiny spurious "bicycle" box paired with a normal-sized
        but unrelated person far away) even if the IoU/containment check
        would otherwise accept it.
    """
    if len(detections) == 0:
        return detections[np.array([], dtype=bool)]

    person_idx = np.where((detections.class_id == person_id) &
                           (detections.confidence >= person_conf_thresh))[0]
    bike_idx = np.where((detections.class_id == bicycle_id) &
                         (detections.confidence >= bicycle_conf_thresh))[0]

    if len(person_idx) == 0 or len(bike_idx) == 0:
        return detections[np.array([], dtype=bool)]

    pairs = []  # (score, p_i, b_i)
    for p_i in person_idx:
        for b_i in bike_idx:
            area_a, area_b = _area(detections.xyxy[p_i]), _area(detections.xyxy[b_i])
            if area_a == 0 or area_b == 0:
                continue
            ratio = max(area_a, area_b) / min(area_a, area_b)
            if ratio > max_area_ratio:
                continue  # implausible pair size — skip regardless of IoU

            score = _iou(detections.xyxy[p_i], detections.xyxy[b_i])
            if score < iou_thresh:
                if _center_in_box(detections.xyxy[b_i], detections.xyxy[p_i]) or \
                   _center_in_box(detections.xyxy[p_i], detections.xyxy[b_i]):
                    score = max(score, iou_thresh)  # accept via containment fallback
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
# Generic video-processing pipeline (unchanged from the notebook)
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
            dets.class_id = np.zeros(len(dets), dtype=int)  # normalize to 'cyclist'
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

    raise ValueError(f"unknown method: {method!r} (expected one of A/B/C/D/E)")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--method", required=True, choices=list("ABCDE"))
    ap.add_argument("--video", required=True, help="Path to input video")
    ap.add_argument("--weights-dir", required=True,
                     help="Shared cache dir containing yolov8x.pt, yolo11x.pt, "
                          "rtdetr-l.pt, visdrone_yolo11x.pt (see prefetch_weights.py)")
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
