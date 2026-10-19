from ultralytics import YOLO
import cv2
import numpy as np
import sys
import os
import time
import argparse

# ---------------------------------------------------------------------------
# ROI (Region of Interest) definition
# ---------------------------------------------------------------------------
# Define the road/sidewalk/bike-lane polygon ONCE per camera, as FRACTIONS
# of frame width/height (x, y each in [0.0, 1.0]) — NOT absolute pixels.
# Using fractions means the same polygon definition works correctly
# regardless of each camera's actual video resolution (MioVision cameras
# are not all the same resolution, and hardcoding pixels silently breaks
# on any camera that doesn't match the resolution you tuned against).
#
# Points go around the region you want to KEEP. Detections whose box
# CENTER falls outside this polygon are discarded after detection runs.
#
# NOTE: we deliberately do NOT black out pixels outside the ROI before
# detection. Doing that creates a hard, sharp edge in the image (road vs.
# solid black) which YOLO can itself mistake for an object boundary,
# producing large spurious boxes that trace the ROI shape. Running
# detection on the untouched frame and filtering afterward avoids that
# artifact entirely.
#
# Easiest way to build this: run with --show-roi on one frame of a new
# camera's video, eyeball the overlay, and adjust the fractions until the
# polygon hugs the road/sidewalk/bike lane area.
#
# Below is set to the FULL FRAME (all four corners) — i.e. the ROI filter
# is effectively disabled and every detection anywhere in the frame counts.
# If you want to restrict to road/sidewalk only later, replace this with a
# tighter polygon and re-tune with --show-roi.
ROI_POLYGON_FRAC = [
    (0.00, 0.00),
    (1.00, 0.00),
    (1.00, 1.00),
    (0.00, 1.00),
]

# How often (in raw video frames) to run detection+tracking. The tracker
# matches objects between consecutive samples based on how little they
# moved, so this needs to be frequent enough that a car/cyclist hasn't
# moved too far between samples. Every 5 frames is a speed/accuracy
# balance; lower this further (e.g. 2-3) for more reliable tracking at the
# cost of runtime, or raise it if tracking still looks solid and you need
# more speed.
TRACK_EVERY_N_FRAMES = 5

# A track must persist for at least this many REAL-TIME SECONDS before it
# counts as a genuine object, rather than a one-off false positive. This is
# expressed in seconds (not raw hit count) so it stays meaningful regardless
# of TRACK_EVERY_N_FRAMES — changing the sampling rate no longer silently
# changes how forgiving the noise filter is.
MIN_TRACK_SECONDS = 1.0

# ---------------------------------------------------------------------------
# Tiled inference
# ---------------------------------------------------------------------------
# Debug on the Anderson St footage showed the native video is only 720x480,
# and a real vehicle at typical distance is only ~15-20 pixels wide — too
# small for YOLO to detect confidently even though it's clearly trying
# (low-confidence boxes cluster right on top of the real object). Feeding
# the model a smaller CROP of the frame (rather than the whole frame) makes
# that same object a much larger fraction of what the model looks at,
# which is the standard fix for small/distant objects in aerial or
# elevated CCTV footage (the technique behind tools like SAHI).
#
# TILE_GRID = (cols, rows): how many tiles to split each frame into.
# (1, 1) disables tiling entirely (equivalent to the old whole-frame
# behavior) — use that if you want to dial back runtime.
# (2, 2) is a reasonable starting point for 720x480 footage.
TILE_GRID = (2, 2)

# Tiles overlap by this fraction of their own size, so an object sitting
# right on a tile boundary still appears whole in at least one tile.
TILE_OVERLAP_FRAC = 0.2

# When merging detections from overlapping tiles, boxes of the same class
# with IoU above this are treated as the same real object (keep only the
# highest-confidence one).
TILE_MERGE_IOU_THRESH = 0.5

# Discard any detection whose box area exceeds this fraction of its tile's
# area. No real car/person/bicycle at this camera's distance should fill
# most of a tile — a box this big is almost always an artifact of the tile
# crop edge or the gray letterbox padding Ultralytics adds internally to
# fit a non-square tile into a square model input, not a real object.
MAX_BOX_AREA_FRAC_OF_TILE = 0.5

# ---------------------------------------------------------------------------
# Custom tracker
# ---------------------------------------------------------------------------
# A lightweight greedy IoU tracker, used instead of Ultralytics' built-in
# ByteTrack integration. The built-in .track() only accepts one whole frame
# at a time, so it can't directly consume our tiled+merged detections
# without reaching into undocumented internal classes that vary between
# ultralytics versions. This tracker is simpler, fully visible here, and
# easy to debug — appropriate for a research pilot script.
TRACK_IOU_MATCH_THRESH = 0.3
TRACK_MAX_MISSED_SAMPLES = 3

# ---------------------------------------------------------------------------
# Motion filtering
# ---------------------------------------------------------------------------
# A cheap, no-labeling-required filter: build a background model of the
# (mostly static) scene, and require that a detection actually overlaps
# with real per-frame motion before it's trusted. Static texture — grass,
# rooftop patterns, tile-edge artifacts — never moves, so this should cut
# a large share of the false positives we've been seeing without touching
# the model at all.
#
# TRADE-OFF: a vehicle that's stopped (parked, waiting at a light) for a
# while will stop registering as "moving" and can get filtered out too.
# For a moving-traffic pilot count this is usually the right trade, but
# keep it in mind if you start caring about stationary/parked vehicles.
USE_MOTION_FILTER = True

# Minimum fraction of a detection's box area that must overlap the
# foreground/motion mask for the detection to be kept.
MOTION_OVERLAP_THRESH = 0.15


def motion_overlap_fraction(fg_mask, box):
    """Fraction of the box's area that is 'moving' according to the
    background subtractor's foreground mask."""
    h, w = fg_mask.shape[:2]
    x1, y1, x2, y2 = [int(round(v)) for v in box]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)
    if x2 <= x1 or y2 <= y1:
        return 0.0
    region = fg_mask[y1:y2, x1:x2]
    box_area = region.shape[0] * region.shape[1]
    if box_area == 0:
        return 0.0
    moving_pixels = int(np.count_nonzero(region))
    return moving_pixels / box_area


def frac_polygon_to_pixels(polygon_frac, shape):
    """Convert a list of (x_frac, y_frac) in [0,1] to absolute (x, y) pixel
    coordinates for a frame of the given shape (h, w, ...)."""
    h, w = shape[:2]
    return [(int(round(x * w)), int(round(y * h))) for (x, y) in polygon_frac]


def point_in_roi(x, y, polygon_px):
    """True if pixel point (x, y) falls inside the ROI polygon."""
    pts = np.array(polygon_px, dtype=np.int32)
    return cv2.pointPolygonTest(pts, (float(x), float(y)), False) >= 0


def draw_roi_outline(frame, polygon_px):
    """Draw a thin outline (not filled) of the ROI on a frame, for visual
    confirmation on the annotated output video."""
    pts = np.array(polygon_px, dtype=np.int32)
    cv2.polylines(frame, [pts], isClosed=True, color=(0, 0, 255), thickness=2)
    return frame


def draw_roi_overlay(frame, polygon_frac):
    overlay = frame.copy()
    pts = np.array(frac_polygon_to_pixels(polygon_frac, frame.shape), dtype=np.int32)
    cv2.polylines(overlay, [pts], isClosed=True, color=(0, 0, 255), thickness=3)
    cv2.fillPoly(overlay, [pts], color=(0, 0, 255))
    return cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)


def draw_box(frame, xyxy, label, color):
    x1, y1, x2, y2 = [int(v) for v in xyxy]
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
    cv2.rectangle(frame, (x1, y1 - th - 8), (x1 + tw + 4, y1), color, -1)
    cv2.putText(frame, label, (x1 + 2, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    return frame


def compute_tiles(frame_shape, grid=TILE_GRID, overlap_frac=TILE_OVERLAP_FRAC):
    """Return a list of (x1, y1, x2, y2) pixel rectangles covering the whole
    frame, in a cols x rows grid, each expanded by overlap_frac of its own
    size on every side (clipped to the frame) so objects near a boundary
    still land fully inside at least one tile."""
    h, w = frame_shape[:2]
    cols, rows = grid
    base_tile_w = w / cols
    base_tile_h = h / rows
    pad_w = base_tile_w * overlap_frac
    pad_h = base_tile_h * overlap_frac

    tiles = []
    for r in range(rows):
        for c in range(cols):
            x0, y0 = c * base_tile_w, r * base_tile_h
            x1, y1 = x0 + base_tile_w, y0 + base_tile_h
            xa = max(0, int(x0 - pad_w))
            ya = max(0, int(y0 - pad_h))
            xb = min(w, int(x1 + pad_w))
            yb = min(h, int(y1 + pad_h))
            tiles.append((xa, ya, xb, yb))
    return tiles


def draw_tile_outlines(frame, tiles):
    for (xa, ya, xb, yb) in tiles:
        cv2.rectangle(frame, (xa, ya), (xb, yb), (0, 255, 255), 1)
    return frame


def detect_tiled(model, frame, tiles, classes, conf, imgsz):
    """Run detection on each tile separately (so small/distant objects
    occupy a larger fraction of what the model sees), translate every box
    back to full-frame coordinates, then merge duplicate detections that
    show up in more than one overlapping tile.

    Returns a list of (x1, y1, x2, y2, conf, cls_name) in full-frame pixel
    coordinates.
    """
    all_dets = []
    for (xa, ya, xb, yb) in tiles:
        tile_img = frame[ya:yb, xa:xb]
        if tile_img.size == 0:
            continue
        tile_area = tile_img.shape[0] * tile_img.shape[1]
        results = model.predict(tile_img, classes=classes, conf=conf, imgsz=imgsz, verbose=False)
        boxes = results[0].boxes
        if boxes is None or len(boxes) == 0:
            continue
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            # Sanity check: no real car/person/bicycle at this camera's
            # distance should ever come close to filling an entire tile.
            # A box this large is almost always a tile-edge or letterbox-
            # padding artifact (the model mistaking the crop boundary or
            # internal gray padding for an object edge), not a real
            # detection — discard it before it ever reaches tracking.
            box_area = max(0.0, x2 - x1) * max(0.0, y2 - y1)
            if tile_area > 0 and (box_area / tile_area) > MAX_BOX_AREA_FRAC_OF_TILE:
                continue

            cls_name = model.names[int(box.cls)]
            score = float(box.conf)
            # translate from tile-local to full-frame coordinates
            all_dets.append((x1 + xa, y1 + ya, x2 + xa, y2 + ya, score, cls_name))

    return merge_tile_detections(all_dets)


def iou_xyxy(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def merge_tile_detections(all_dets, iou_thresh=TILE_MERGE_IOU_THRESH):
    """Per-class NMS across all tiles' detections, so an object sitting in
    the overlap between two tiles (and therefore detected twice) is only
    counted once — keeping the higher-confidence box."""
    if not all_dets:
        return []

    by_class = {}
    for det in all_dets:
        by_class.setdefault(det[5], []).append(det)

    kept = []
    for cls_name, dets in by_class.items():
        boxes = [[d[0], d[1], d[2] - d[0], d[3] - d[1]] for d in dets]  # x,y,w,h for NMSBoxes
        scores = [d[4] for d in dets]
        indices = cv2.dnn.NMSBoxes(boxes, scores, score_threshold=0.0, nms_threshold=iou_thresh)
        if indices is None or len(indices) == 0:
            continue
        for i in np.array(indices).flatten():
            kept.append(dets[i])
    return kept


class SimpleIouTracker:
    """Greedy IoU-matching tracker. Each call to update() takes this
    sample's merged detections and either extends an existing track or
    starts a new one. Tracks that go too long without a match are retired
    (but kept in self.tracks so their final hit count is still countable)."""

    def __init__(self, iou_match_thresh=TRACK_IOU_MATCH_THRESH, max_missed=TRACK_MAX_MISSED_SAMPLES):
        self.next_id = 1
        self.tracks = {}  # id -> {"bbox", "cls", "hits", "missed", "alive"}
        self.iou_match_thresh = iou_match_thresh
        self.max_missed = max_missed

    def update(self, detections):
        """detections: list of (x1, y1, x2, y2, conf, cls_name).
        Returns list of (track_id, x1, y1, x2, y2, cls_name, conf) for
        detections matched or newly created this sample (for drawing)."""
        active_ids = [tid for tid, t in self.tracks.items() if t["alive"]]

        candidate_pairs = []
        for tid in active_ids:
            for di, det in enumerate(detections):
                iou_val = iou_xyxy(self.tracks[tid]["bbox"], det[:4])
                if iou_val >= self.iou_match_thresh:
                    candidate_pairs.append((iou_val, tid, di))
        candidate_pairs.sort(reverse=True, key=lambda p: p[0])

        matched_tracks, matched_dets = set(), set()
        drawn = []
        for iou_val, tid, di in candidate_pairs:
            if tid in matched_tracks or di in matched_dets:
                continue
            matched_tracks.add(tid)
            matched_dets.add(di)
            det = detections[di]
            t = self.tracks[tid]
            t["bbox"], t["cls"] = det[:4], det[5]
            t["hits"] += 1
            t["missed"] = 0
            drawn.append((tid, *det[:4], det[5], det[4]))

        for tid in active_ids:
            if tid not in matched_tracks:
                self.tracks[tid]["missed"] += 1
                if self.tracks[tid]["missed"] > self.max_missed:
                    self.tracks[tid]["alive"] = False

        for di, det in enumerate(detections):
            if di not in matched_dets:
                tid = self.next_id
                self.next_id += 1
                self.tracks[tid] = {"bbox": det[:4], "cls": det[5], "hits": 1, "missed": 0, "alive": True}
                drawn.append((tid, *det[:4], det[5], det[4]))

        return drawn


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("video_path", nargs="?",
        default="pilot_clips/MioVision Data/2021 Data/Anderson St/Standard_SCU8PM_2021-04-13_0000/Standard_SCU8PM_2021-04-13_0000.013.mp4")
    parser.add_argument("max_seconds", nargs="?", type=int, default=300,
        help="Only process first N seconds (0 = full video)")
    parser.add_argument("--show-roi", action="store_true",
        help="Save a single frame with the ROI polygon (and tile grid) overlaid, then exit. "
             "Use this to check/tune ROI_POLYGON_FRAC / TILE_GRID before a full run.")
    args = parser.parse_args()

    VIDEO_PATH = args.video_path
    MAX_SECONDS = args.max_seconds
    OUTPUT_DIR = "pilot_output/pilot_run"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    cap = cv2.VideoCapture(VIDEO_PATH)

    if args.show_roi:
        ret, frame = cap.read()
        if not ret:
            print("Could not read a frame to preview ROI.")
            return
        preview = draw_roi_overlay(frame, ROI_POLYGON_FRAC)
        draw_tile_outlines(preview, compute_tiles(frame.shape))
        preview_path = os.path.join(OUTPUT_DIR, "roi_preview.jpg")
        cv2.imwrite(preview_path, preview)
        print(f"Preview (ROI in red, tiles in yellow) saved to {preview_path}.")
        print("Adjust ROI_POLYGON_FRAC / TILE_GRID / TILE_OVERLAP_FRAC and re-run until it looks right.")
        cap.release()
        return

    # yolov8l (large) instead of yolov8m: meaningfully better recall on
    # small/thin objects like cyclists and pedestrians, at a real but more
    # moderate speed cost than yolov8x. Ultralytics auto-downloads the
    # weights the first time this runs.
    model = YOLO("yolo26l.pt")

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_skip = TRACK_EVERY_N_FRAMES
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    max_frames = int(MAX_SECONDS * fps) if MAX_SECONDS > 0 else total_frames

    samples_per_second = fps / frame_skip if frame_skip else fps
    min_track_hits = max(3, round(samples_per_second * MIN_TRACK_SECONDS))

    out_path = os.path.join(OUTPUT_DIR, "annotated.mp4")
    writer = None
    writer_fps = max(1, round(samples_per_second))
    frame_idx = 0
    sampled_frames = 0
    start_time = time.time()

    roi_polygon_px = None  # built lazily once we know frame size
    tiles = None
    tracker = SimpleIouTracker()

    # MOG2 background subtractor: fed EVERY raw frame (not just sampled
    # ones) so its model of the static background stays current at the
    # video's real frame rate, independent of our detection sampling rate.
    bg_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=False) if USE_MOTION_FILTER else None
    fg_mask = None
    dropped_static = 0

    while True:
        ret, frame = cap.read()
        if not ret or frame_idx >= max_frames:
            break

        if bg_subtractor is not None:
            # Update the background model on every raw frame so it tracks
            # the video's actual motion, independent of our sampling rate.
            fg_mask = bg_subtractor.apply(frame)

        if frame_idx % frame_skip == 0:
            if roi_polygon_px is None:
                roi_polygon_px = frac_polygon_to_pixels(ROI_POLYGON_FRAC, frame.shape)
                tiles = compute_tiles(frame.shape)

            dets = detect_tiled(model, frame, tiles, classes=[0, 1, 2, 3, 5, 7], conf=0.2, imgsz=1280)

            # keep only detections whose center falls inside the ROI
            roi_dets = []
            for (x1, y1, x2, y2, conf, cls_name) in dets:
                cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                if point_in_roi(cx, cy, roi_polygon_px):
                    roi_dets.append((x1, y1, x2, y2, conf, cls_name))

            # discard detections that don't correspond to actual motion —
            # static texture (grass, tile-edge artifacts) never moves, so
            # this should cut a large share of false positives without
            # needing any labeled data or model changes.
            if bg_subtractor is not None and fg_mask is not None:
                motion_dets = []
                for det in roi_dets:
                    if motion_overlap_fraction(fg_mask, det[:4]) >= MOTION_OVERLAP_THRESH:
                        motion_dets.append(det)
                    else:
                        dropped_static += 1
                roi_dets = motion_dets

            drawn = tracker.update(roi_dets)

            annotated = frame.copy()
            draw_roi_outline(annotated, roi_polygon_px)
            for (tid, x1, y1, x2, y2, cls_name, conf) in drawn:
                draw_box(annotated, (x1, y1, x2, y2), f"#{tid} {cls_name} {conf:.2f}", (255, 140, 0))

            if writer is None:
                h, w = annotated.shape[:2]
                writer = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*"mp4v"), writer_fps, (w, h))
            writer.write(annotated)

            sampled_frames += 1

        frame_idx += 1

    elapsed = time.time() - start_time
    cap.release()
    if writer:
        writer.release()

    # Count each track once, but only if it persisted long enough (in real
    # time) to be trusted as a real object rather than a one-off false
    # positive or a fragment of a track that briefly lost association.
    class_counts = {}
    dropped_short_tracks = 0
    for tid, info in tracker.tracks.items():
        if info["hits"] >= min_track_hits:
            class_counts[info["cls"]] = class_counts.get(info["cls"], 0) + 1
        else:
            dropped_short_tracks += 1

    n_tiles = TILE_GRID[0] * TILE_GRID[1]
    print(f"Processed {sampled_frames} sampled frames x {n_tiles} tiles each "
          f"({frame_idx} raw frames, capped at {MAX_SECONDS}s) in {elapsed:.1f}s")
    print(f"That's ~{elapsed/max(sampled_frames,1):.2f}s per sampled frame (all tiles combined)")
    print(f"Min hits to count as real (~{MIN_TRACK_SECONDS}s of persistence): {min_track_hits}")
    print(f"Tracked objects by class: {class_counts}")
    print(f"Dropped {dropped_short_tracks} short-lived tracks (likely false positives or lost tracks)")
    if bg_subtractor is not None:
        print(f"Dropped {dropped_static} individual detections for showing no real motion (static texture)")
    print(f"Annotated video saved to {out_path}")


if __name__ == "__main__":
    main()