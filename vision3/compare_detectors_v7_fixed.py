#!/usr/bin/env python3
"""
compare_detectors_v7_fixed.py

ROOT CAUSE FOUND (confirmed against installed supervision==0.30.5 source,
not guessed from docs): `minimum_matching_threshold` is passed as `thresh`
into a Hungarian assignment over an IoU-*distance* matrix (1 - IoU), so it
caps how much mismatch is tolerated between frames -- LOWER means STRICTER.
v3 set it to 0.3 believing that "loosened" matching (the name reads like a
floor to clear); it actually required IoU >= 0.7 frame-to-frame just to
keep the same track alive, which a small, jittery, distant box essentially
never achieves. That's the actual explanation for the whole v2->v5 arc:
phantom double-counts before the hit-count gate existed (every frame
fragmenting into a "new" track), then total collapse to 0 once the gate
was added (no track ever survives 2+ frames to clear it) -- regardless of
which detector architecture was behind it, which is why C and F died
together.

FIX: minimum_matching_threshold restored to 0.8 (the supervision library
default -- reverting to a known-good baseline rather than guessing a new
number). track_activation_threshold=0.25 and MIN_TRACK_HITS=2 (the v5
values) are left as-is; nothing pointed at those being wrong.

Diagnostic instrumentation from the previous build (per-fuse-call
person/bicycle pass-conf counts, per-500-frame stage totals, final
max_hit_count) is left in place -- keep watching it on this run to confirm
tracks now actually persist past 1-2 frames.

Provenance: built on v4.py (in hand) + the v5 tracker diff + this fix.
compare_detectors_v5.py itself still hasn't been received intact, so if
your real v5 differs from this in ways beyond the tracker constants, that
divergence is still unverified -- worth a diff once you have a moment.

Everything below (fusion logic, all nine method builders) is otherwise
unchanged from v4 -- see v4.py's own docstring for that history.

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

Method I: RF-DETR-Large + fusion
  A genuinely different architecture family from everything else here
  (DINOv2 backbone, not COCO-YOLO-family or RT-DETR). Specifically
  benchmarked (RF100-VL) for generalizing to new camera domains from
  limited fine-tuning data, which matters given your ~270-image set.
  Requires `pip install rfdetr` and the weights cached ahead of time
  -- see prefetch_rfdetr.py, run on the LOGIN NODE first, same reason
  as prefetch_weights_v2.py (compute nodes here don't reliably reach
  every domain a model download needs).

Usage: identical to compare_detectors_v2.py, with methods A-I.
    python compare_detectors_v7_fixed.py --method F \
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

# --- Tracker tuning ---
# minimum_matching_threshold is the ACTUAL fix (see module docstring) --
# it's a max-distance cap fed into Hungarian assignment on (1-IoU), so
# LOWER = STRICTER. v3's 0.3 required ~IoU>=0.7 frame-to-frame and is why
# everything collapsed to 0. Restored to the supervision library default.
TRACK_ACTIVATION_THRESHOLD = 0.25   # v5 value; not implicated in the 0-collapse
MIN_MATCHING_THRESHOLD = 0.8        # v3: 0.8->0.3 (backwards -- see docstring)
                                     # v7: reverted to library default 0.8
MIN_TRACK_HITS = 2                  # v5 value; not implicated in the 0-collapse


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


_FUSE_CALL_COUNT = 0  # module-level, shared across every call site


def fuse_person_bicycle(detections: sv.Detections, person_id: int, bicycle_id: int,
                         person_conf_thresh: float = 0.25,
                         bicycle_conf_thresh: float = 0.35,
                         iou_thresh: float = 0.05,
                         max_area_ratio: float = 8.0) -> sv.Detections:
    global _FUSE_CALL_COUNT
    _FUSE_CALL_COUNT += 1
    debug = (_FUSE_CALL_COUNT % 500 == 1)

    if len(detections) == 0:
        if debug:
            print(f"[fuse call {_FUSE_CALL_COUNT}] raw model returned 0 detections "
                  f"of any class this frame", flush=True)
        return detections[np.array([], dtype=bool)]

    person_idx = np.where((detections.class_id == person_id) &
                           (detections.confidence >= person_conf_thresh))[0]
    bike_idx = np.where((detections.class_id == bicycle_id) &
                         (detections.confidence >= bicycle_conf_thresh))[0]

    if debug:
        all_person = int(np.sum(detections.class_id == person_id))
        all_bike = int(np.sum(detections.class_id == bicycle_id))
        print(f"[fuse call {_FUSE_CALL_COUNT}] raw_dets={len(detections)} "
              f"person_any_conf={all_person} person_pass_conf={len(person_idx)} "
              f"(thresh={person_conf_thresh}) | bicycle_any_conf={all_bike} "
              f"bicycle_pass_conf={len(bike_idx)} (thresh={bicycle_conf_thresh})",
              flush=True)

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
                   method_label: str, conf_threshold: float = 0.25,
                   diag_every: int = 500):
    import supervision
    print(f"[{method_label}] supervision version: {supervision.__version__}", flush=True)

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
    # Running totals across the whole video, for the end-of-run diagnostic
    # summary -- separate from the per-500-frame prints, which show the
    # *current* frame's stage counts (mostly 0,0,0,0 on an empty frame,
    # which is normal -- watch for cumulative totals instead).
    # Raw pre-fusion person/bicycle counts print separately from
    # fuse_person_bicycle itself (every 500 calls) -- see its own debug
    # block. These totals start from *after* fusion.
    totals = {"post_fuse": 0, "post_conf": 0, "post_tracker": 0}
    t0 = time.time()

    with sv.VideoSink(target_path=output_path, video_info=video_info) as sink:
        for frame in sv.get_video_frames_generator(source_path=video_path):
            frame_count += 1
            detections = get_detections_fn(frame)
            n_post_fuse = len(detections)
            totals["post_fuse"] += n_post_fuse

            if len(detections) > 0:
                detections = detections[detections.confidence >= conf_threshold]
            n_post_conf = len(detections)
            totals["post_conf"] += n_post_conf

            detections = tracker.update_with_detections(detections)
            n_post_tracker = len(detections)
            totals["post_tracker"] += n_post_tracker

            if detections.tracker_id is not None:
                for tid in detections.tracker_id.tolist():
                    hit_counts[tid] = hit_counts.get(tid, 0) + 1
                    if hit_counts[tid] >= MIN_TRACK_HITS:
                        seen_ids.add(tid)

            if frame_count % diag_every == 0:
                print(f"[{method_label}] frame {frame_count}/{video_info.total_frames} "
                      f"| CUMULATIVE since start -> post_fuse={totals['post_fuse']} "
                      f"post_conf={totals['post_conf']} post_tracker={totals['post_tracker']} "
                      f"| unique_cyclists_so_far={len(seen_ids)} "
                      f"| active_track_hit_counts={hit_counts}", flush=True)

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
    print(f"[{method_label}] FINAL STAGE TOTALS -> {totals} "
          f"| max hit-count reached by any track: "
          f"{max(hit_counts.values()) if hit_counts else 0} "
          f"(needs >= {MIN_TRACK_HITS} to count)", flush=True)
    return {
        "method": method_label,
        "output_path": output_path,
        "unique_cyclists": len(seen_ids),
        "frames": frame_count,
        "seconds": round(elapsed, 1),
        "fps": round(frame_count / elapsed, 2) if elapsed > 0 else 0,
        "stage_totals": totals,
        "max_hit_count": max(hit_counts.values()) if hit_counts else 0,
    }


# ---------------------------------------------------------------------------
# Per-method detector builders
# ---------------------------------------------------------------------------

def build_detector(method: str, weights_dir: str, device: str, finetune_weights: str = None):
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

        # supervision>=0.27 removed the ratio-based overlap_ratio_wh in favor
        # of pixel-based overlap_wh (see supervision.roboflow.com/deprecated).
        # 0.2 ratio on a 640x640 slice = 128px; converting by hand here
        # rather than computing it at runtime so the actual pixel value is
        # visible and doesn't silently drift if slice_wh is ever changed
        # without updating this line too.
        slicer = sv.InferenceSlicer(
            callback=tile_fn,
            slice_wh=(640, 640),
            overlap_wh=(128, 128),
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

    if method == "I":
        return build_rfdetr_detector(device)

    if method == "J":
        return build_finetuned_detector(finetune_weights, device)

    raise ValueError(f"unknown method: {method!r} (expected one of A/B/C/D/E/F/G/H/I/J)")


def build_finetuned_detector(finetune_weights: str, device: str):
    """Method J: your own RT-DETR-l fine-tuned on the 270-image Roboflow
    set (see split_dataset.py + finetune_rtdetr.py). Direct cyclist class
    output, like Method D -- no person+bicycle fusion needed, since the
    fine-tuned model was trained to predict `cyclist` as its own class.

    CYCLIST_CLASS_ID is fixed at 2 to match the class order written by
    split_dataset.py's data.yaml: ['bus','car','cyclist','other_vehicle',
    'person','truck']. If you retrain with different data.yaml class
    ordering, update this to match -- it is NOT re-derived from the
    checkpoint automatically.
    """
    if not finetune_weights:
        raise ValueError("Method J requires --finetune-weights (path to best.pt "
                          "from finetune_rtdetr.py)")
    CYCLIST_CLASS_ID = 2
    model = RTDETR(finetune_weights)

    def fn(frame):
        r = model.predict(frame, classes=[CYCLIST_CLASS_ID], conf=0.15,
                           imgsz=IMG_SIZE, device=device, verbose=False)[0]
        dets = sv.Detections.from_ultralytics(r)
        dets.class_id = np.zeros(len(dets), dtype=int)
        return dets
    return fn, "J: RT-DETR-l fine-tuned (direct cyclist class)"


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

    # Same supervision>=0.27 overlap_wh migration as Method E above --
    # H_OVERLAP is kept as a ratio constant for readability/tuning, and
    # converted to pixels here at the point of use.
    h_overlap_px = (int(H_OVERLAP[0] * H_SLICE_WH[0]), int(H_OVERLAP[1] * H_SLICE_WH[1]))
    slicer = sv.InferenceSlicer(
        callback=tile_fn,
        slice_wh=H_SLICE_WH,
        overlap_wh=h_overlap_px,
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


def build_rfdetr_detector(device: str):
    """Method I: RF-DETR-Large, same fusion pipeline as A/B/C/F. Lazy
    import so rfdetr is only required when this method is actually run.
    Weights must already be cached -- run prefetch_rfdetr.py on the
    login node first (see module docstring).
    """
    from rfdetr import RFDETRLarge
    # rfdetr moved this module (rfdetr.util.coco_classes -> rfdetr.assets.
    # coco_classes) as of a recent release -- see rfdetr's migration guide.
    # Try the current path first, fall back to the old one so this keeps
    # working either way rather than needing another mid-run fix.
    try:
        from rfdetr.assets.coco_classes import COCO_CLASSES
    except ImportError:
        from rfdetr.util.coco_classes import COCO_CLASSES

    model = RFDETRLarge()

    # COCO_CLASSES has been a plain list in some rfdetr versions and a
    # {id: name} dict in others (seen in current docs/cookbooks) -- handle
    # both rather than assuming, since .index() only works on the list form.
    if isinstance(COCO_CLASSES, dict):
        name_to_id = {name: cid for cid, name in COCO_CLASSES.items()}
        person_id = name_to_id["person"]
        bicycle_id = name_to_id["bicycle"]
    else:
        person_id = COCO_CLASSES.index("person")
        bicycle_id = COCO_CLASSES.index("bicycle")

    def fn(frame: np.ndarray) -> sv.Detections:
        rgb = np.ascontiguousarray(frame[:, :, ::-1])  # BGR->RGB; .copy() via
        # ascontiguousarray because the plain [::-1] slice is a negative-
        # stride VIEW, which torch.from_numpy (used inside rfdetr's
        # predict()) can't wrap directly -- confirmed from the traceback.
        dets = model.predict(rgb, threshold=0.15)
        return fuse_person_bicycle(dets, person_id, bicycle_id)

    return fn, "I: RF-DETR-Large+fusion"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--method", required=True, choices=list("ABCDEFGHIJ"))
    ap.add_argument("--video", required=True, help="Path to input video")
    ap.add_argument("--weights-dir", required=True,
                     help="Shared cache dir containing yolov8x.pt, yolo11x.pt, "
                          "rtdetr-l.pt, visdrone_yolo11x.pt, yolo26x.pt "
                          "(see prefetch_weights_v2.py)")
    ap.add_argument("--finetune-weights", default=None,
                     help="Path to best.pt from finetune_rtdetr.py -- required for --method J only")
    ap.add_argument("--outdir", required=True,
                     help="Directory for the annotated output video + summary JSON")
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[method {args.method}] device={device}")
    if device == "cpu":
        print("WARNING: no GPU visible to this job — check --gres/--gpus in the SLURM script.")

    os.makedirs(args.outdir, exist_ok=True)
    detect_fn, label = build_detector(args.method, args.weights_dir, device, args.finetune_weights)
    out_video = os.path.join(args.outdir, f"output_{args.method}.mp4")

    summary = process_video(args.video, out_video, detect_fn, label)

    summary_path = os.path.join(args.outdir, f"summary_{args.method}.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
