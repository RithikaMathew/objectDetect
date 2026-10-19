"""
Extract frames from your pilot clips for labeling in Roboflow.

Four modes:

1. UNIFORM SAMPLING (`uniform`) — grabs one frame every N seconds from a
   video, for general variety (background, lighting, typical traffic).

2. HAND-PICKED TIMESTAMPS (`picks`) — grab specific moments you've already
   found by scrubbing through footage (e.g. every cyclist/pedestrian
   sighting, a foliage false-positive patch, a misclassified truck).

3. AUTO-MINING (`auto`) — confidence-gated candidate mining across many
   videos at once, with pre-filled YOLO-format boxes for Roboflow.

4. DATASET BUILD (`build`) — the recommended entry point for a paper-ready
   pilot dataset. Runs uniform + confidence-gated mining over a TRAIN set
   of videos and uniform-only sampling over a separate VAL set of videos,
   writing directly into dataset_frames/<out>/train/ and .../val/. See the
   docstring on cmd_build() below for why train and val are sampled
   differently and why no video may appear in both.

Usage:

    # Uniform sampling: one frame every 12 seconds, first 30 minutes
    python extract_frames.py uniform "<video_path>" --interval 12 --max-seconds 1800 --out dataset_frames/routine

    # Hand-picked timestamps: put one "video_path,timestamp_seconds,label" per
    # line in a text file (label is just for your own filename tracking —
    # doesn't need to match Roboflow class names)
    python extract_frames.py picks picks.txt --out dataset_frames/handpicked

    # Auto-mining across many videos
    python extract_frames.py auto --videos-dir "pilot_clips/MioVision Data" --max-seconds 0 --frame-conf 0.5 --out dataset_frames/candidates

    # One-shot, leakage-safe train/val dataset build
    python extract_frames.py build \
        --train-videos-dir "pilot_clips/.../Anderson St" "pilot_clips/.../Church Ave" \
        --val-videos-dir "pilot_clips/.../Corrine Dr" \
        --out dataset_frames/split

    # Same, with explicit per-class instance quotas for the mining pass
    # (global cap AND an even per-site share, so no single site can
    # consume a whole class's quota -- see QuotaTracker below). These are
    # also the defaults for `build`, so you only need to pass them if you
    # want different numbers, or --no-quotas to turn quotas off entirely.
    python extract_frames.py build \
        --train-videos-dir "pilot_clips/.../Anderson St" "pilot_clips/.../Church Ave" \
        --val-videos-dir "pilot_clips/.../Corrine Dr" \
        --quota-car 400 --quota-truck 120 --quota-bus 100 \
        --quota-person 150 --quota-other-vehicle 100 \
        --out dataset_frames/split

Example picks.txt:
    pilot_clips/.../Standard_SCU8PM_2021-04-13_0000.013.mp4,66,cyclist
    pilot_clips/.../Standard_SCU8PM_2021-04-13_0000.013.mp4,186,foliage_false_positive
    pilot_clips/.../Standard_SCU8PM_2021-04-13_0000.026.mp4,1567,truck
"""
import cv2
import os
import re
import sys
import math
import csv
import argparse


def save_frame(cap, timestamp_seconds, fps, out_dir, tag):
    frame_num = int(round(timestamp_seconds * fps))
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
    ret, frame = cap.read()
    if not ret:
        print(f"  WARNING: could not read frame at {timestamp_seconds}s (tag={tag})")
        return None
    fname = f"{tag}_t{int(timestamp_seconds)}s.jpg"
    out_path = os.path.join(out_dir, fname)
    cv2.imwrite(out_path, frame)
    return out_path


def cmd_uniform(args):
    os.makedirs(args.out, exist_ok=True)
    total_saved = 0
    for video_path in args.video_paths:
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps else 0
        max_seconds = args.max_seconds if args.max_seconds > 0 else duration

        video_tag = os.path.splitext(os.path.basename(video_path))[0]
        saved = 0
        t = 0.0
        while t < max_seconds and t < duration:
            path = save_frame(cap, t, fps, args.out, f"{video_tag}_uniform")
            if path:
                saved += 1
            t += args.interval

        cap.release()
        print(f"  {video_path}: saved {saved} frames")
        total_saved += saved

    print(f"Saved {total_saved} uniformly-sampled frames total to {args.out}")


def cmd_picks(args):
    os.makedirs(args.out, exist_ok=True)
    if not os.path.exists(args.picks_file):
        print(f"Picks file not found: {args.picks_file}")
        sys.exit(1)

    # cache one VideoCapture per video path so we don't reopen repeatedly
    caps = {}
    saved = 0
    with open(args.picks_file) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 2:
                print(f"  Skipping malformed line {line_num}: {line}")
                continue
            video_path, ts_str = parts[0], parts[1]
            label = parts[2] if len(parts) > 2 else "pick"
            try:
                timestamp = float(ts_str)
            except ValueError:
                print(f"  Skipping line {line_num}, bad timestamp: {line}")
                continue

            if video_path not in caps:
                caps[video_path] = cv2.VideoCapture(video_path)
            cap = caps[video_path]
            fps = cap.get(cv2.CAP_PROP_FPS)

            video_tag = os.path.splitext(os.path.basename(video_path))[0]
            path = save_frame(cap, timestamp, fps, args.out, f"{video_tag}_{label}")
            if path:
                saved += 1

    for cap in caps.values():
        cap.release()
    print(f"Saved {saved} hand-picked frames to {args.out}")


# Six-class journal taxonomy (0..5). Pre-labels come from COCO detections
# remapped into this space. Unfused COCO bicycles are dropped (out of scope);
# motorcycle maps to other_vehicle. Archive any older 7-class dataset_frames/
# before remine -- indices are not compatible.
#
# COCO query ids: person=0, bicycle=1, car=2, motorcycle=3, bus=5, truck=7
COCO_QUERY_CLASSES = [0, 1, 2, 3, 5, 7]
COCO_PERSON, COCO_BICYCLE, COCO_CAR, COCO_MOTORCYCLE, COCO_BUS, COCO_TRUCK = (
    0, 1, 2, 3, 5, 7)

CLASS_NAMES = ["person", "car", "bus", "truck", "cyclist", "other_vehicle"]
CLS_PERSON, CLS_CAR, CLS_BUS, CLS_TRUCK, CLS_CYCLIST, CLS_OTHER_VEHICLE = (
    0, 1, 2, 3, 4, 5)
# Temporary local id for COCO bicycle during person+bicycle fusion only.
# Never written to label files.
CLS_TEMP_BICYCLE = -1

# Direct COCO -> local for everything except bicycle (handled via temp + fuse).
COCO_TO_LOCAL = {
    COCO_PERSON: CLS_PERSON,
    COCO_CAR: CLS_CAR,
    COCO_BUS: CLS_BUS,
    COCO_TRUCK: CLS_TRUCK,
    COCO_MOTORCYCLE: CLS_OTHER_VEHICLE,
}

# A person box and a bicycle box are fused into one 'cyclist' box when the
# smaller of the two is at least this covered by the intersection. Overlap-over-
# smaller-area is used rather than IoU because a rider's box and a bike's box
# are very different sizes, which pushes IoU low even when the bike is entirely
# beneath the rider.
CYCLIST_FUSE_OVERLAP = 0.25


def fuse_cyclists(keep_boxes, overlap_thresh=CYCLIST_FUSE_OVERLAP):
    """Merge overlapping person+temp-bicycle detections into 'cyclist' boxes.

    WHY: COCO splits a cyclist into two objects, but the ground-truth counts
    one. Without fusing, every downstream count needs a person/bicycle fusion
    heuristic, and that heuristic becomes a permanent error source -- in the BL
    Colonial diagnostic the tracker's class label flipped between 'person' and
    'bicycle' on the same rider from frame to frame. Fusing at label-creation
    time removes the ambiguity from the dataset instead of deferring it to
    inference.

    Unfused COCO bicycle boxes (parked bikes, racks) are DROPPED -- the
    journal taxonomy has no standalone bicycle class.

    Greedy highest-overlap-first matching; each box is used at most once.
    """
    persons = [(i, b) for i, b in enumerate(keep_boxes) if b[0] == CLS_PERSON]
    bikes = [(i, b) for i, b in enumerate(keep_boxes) if b[0] == CLS_TEMP_BICYCLE]
    if not persons or not bikes:
        return [b for b in keep_boxes if b[0] != CLS_TEMP_BICYCLE]

    cands = []
    for pi, pb in persons:
        for bi, bb in bikes:
            ix1, iy1 = max(pb[1], bb[1]), max(pb[2], bb[2])
            ix2, iy2 = min(pb[3], bb[3]), min(pb[4], bb[4])
            inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
            if inter <= 0:
                continue
            pa = max(1e-6, (pb[3] - pb[1]) * (pb[4] - pb[2]))
            ba = max(1e-6, (bb[3] - bb[1]) * (bb[4] - bb[2]))
            ov = inter / min(pa, ba)
            if ov >= overlap_thresh:
                cands.append((ov, pi, bi))
    if not cands:
        return [b for b in keep_boxes if b[0] != CLS_TEMP_BICYCLE]

    cands.sort(reverse=True)
    used = set()
    fused = []
    for ov, pi, bi in cands:
        if pi in used or bi in used:
            continue
        used.add(pi)
        used.add(bi)
        pb, bb = keep_boxes[pi], keep_boxes[bi]
        fused.append((CLS_CYCLIST,
                      min(pb[1], bb[1]), min(pb[2], bb[2]),
                      max(pb[3], bb[3]), max(pb[4], bb[4]),
                      max(pb[5], bb[5])))

    kept = [b for i, b in enumerate(keep_boxes)
            if i not in used and b[0] != CLS_TEMP_BICYCLE]
    return kept + fused


class QuotaTracker:
    """Enforces a global-per-class cap AND a per-site-per-class cap, so
    the confidence-gated mining pass can't let one busy site consume an
    entire class's quota while other sites contribute nothing.

    Fairness is keyed by SITE (camera/intersection location), not by
    individual .mp4 file. MioVision recordings are chunked into many
    files per site (e.g. one .mp4 per hour, across multiple dated
    subfolders) -- all chunks belonging to the same site share one
    quota bucket, using the same `site_label` already computed by
    find_videos_with_site() and used in output filenames.

    - `global_quotas`: dict[local_cls_idx] -> max total instances for
      that class across the whole train split. Classes not present here
      are treated as unlimited.
    - `site_labels`: the distinct site labels this tracker applies to
      (used only to compute each site's fair share: ceil(global / N)).

    A frame is ACCEPTED if at least one of its detected classes still
    has room under both its global count and its owning site's share.
    Once accepted, every box in that frame is counted — quotas are a
    frame-level admission gate, not a per-box truncator, so totals can
    overshoot slightly within a single frame. Because each site's cap
    is a hard ceiling, a quiet site that never reaches its share will
    leave the global quota under-filled rather than letting a busier
    site backfill it — treat these numbers as minimums to reach, not
    exact targets.
    """

    def __init__(self, global_quotas, site_labels):
        self.global_quotas = dict(global_quotas)
        n_sites = max(1, len(set(site_labels)))
        self.per_site_quotas = {
            cls_id: math.ceil(q / n_sites) for cls_id, q in self.global_quotas.items()
        }
        self.global_counts = {cls_id: 0 for cls_id in self.global_quotas}
        self.per_site_counts = {}  # (site_label, cls_id) -> count
        self.frames_skipped = 0

    def would_accept(self, site_label, keep_boxes):
        if not keep_boxes:
            # No detections at all -- not what quotas are gating, let the
            # confidence gate (gate_conf) decide instead.
            return True
        for (cls_id, *_rest) in keep_boxes:
            if cls_id not in self.global_quotas:
                return True  # unquota'd class (e.g. motorcycle by default)
            if self.global_counts[cls_id] >= self.global_quotas[cls_id]:
                continue
            scount = self.per_site_counts.get((site_label, cls_id), 0)
            if scount < self.per_site_quotas[cls_id]:
                return True
        return False

    def record(self, site_label, keep_boxes):
        for (cls_id, *_rest) in keep_boxes:
            if cls_id not in self.global_quotas:
                continue
            self.global_counts[cls_id] += 1
            key = (site_label, cls_id)
            self.per_site_counts[key] = self.per_site_counts.get(key, 0) + 1

    def summary_lines(self):
        lines = []
        for cls_id, quota in sorted(self.global_quotas.items()):
            name = CLASS_NAMES[cls_id]
            got = self.global_counts[cls_id]
            per_site_share = self.per_site_quotas[cls_id]
            lines.append(f"  {name:<12} {got:>5} / {quota:<5}  (per-site share: {per_site_share})")
        lines.append(f"  frames skipped by quota (mining pass): {self.frames_skipped}")
        return lines


def find_videos(videos_dir):
    matches = []
    for root, _, files in os.walk(videos_dir):
        for fname in files:
            if fname.lower().endswith(".mp4"):
                matches.append(os.path.join(root, fname))
    return sorted(matches)


def find_videos_multi(videos_dirs):
    """Recursively find .mp4 files under each of several directories,
    de-duplicated and sorted."""
    matches = set()
    for d in videos_dirs:
        matches.update(find_videos(d))
    return sorted(matches)


# Generic wrapper folder names that carry no site information — stripped
# out when building a human-readable site label from a --*-videos-dir path.
_SITE_LABEL_STOPWORDS = {"pilot_clips", "MioVision Data", "MioVision Video"}


def _derive_site_label(dir_path):
    """Turn a --train-videos-dir / --val-videos-dir path like
    'pilot_clips/MioVision Data/2022 Data/Curry Ford/North' into a
    compact, human-readable site label like 'CurryFord-North', so output
    filenames are traceable back to a site without opening the file.
    """
    parts = [p for p in dir_path.strip("/").split("/") if p]
    site_parts = []
    for p in parts:
        if p in _SITE_LABEL_STOPWORDS:
            continue
        if re.match(r"^\d{4}\s*Data$", p):
            continue
        site_parts.append(p)
    label = "-".join(site_parts) if site_parts else "site"
    return re.sub(r"\s+", "", label)


def _derive_year_label(video_path):
    """Pull a 4-digit year out of the video's own full path (its filename
    or a dated subfolder), independent of the --*-videos-dir argument —
    this is what lets 'CorrineDr' correctly get tagged 2025 and 'BL
    Colonial' correctly get tagged 2019, even though neither top-level
    directory name contains a year itself."""
    m = re.search(r"(19|20)\d{2}", video_path)
    return m.group(0) if m else "unknownyear"


def find_videos_with_site(videos_dirs):
    """Recursively find .mp4 files under each of several directories,
    tagging each with a (site_label, year_label) pair for traceable
    output filenames.

    Returns a list of (video_path, site_label, year_label) tuples,
    de-duplicated and sorted by video_path.
    """
    found = {}
    for d in videos_dirs:
        site_label = _derive_site_label(d)
        for video_path in find_videos(d):
            if video_path not in found:
                found[video_path] = (site_label, _derive_year_label(video_path))
    return [(vp, found[vp][0], found[vp][1]) for vp in sorted(found)]


def draw_box(frame, xyxy, label, color):
    x1, y1, x2, y2 = [int(v) for v in xyxy]
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
    cv2.rectangle(frame, (x1, max(0, y1 - th - 8)), (x1 + tw + 4, y1), color, -1)
    cv2.putText(frame, label, (x1 + 2, max(12, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    return frame


def cmd_auto(args):
    # Imported here, not at module level, so `uniform` / `picks` modes
    # (which don't need YOLO at all) don't require ultralytics installed.
    from ultralytics import YOLO

    images_dir = os.path.join(args.out, "images")
    labels_dir = os.path.join(args.out, "labels")
    previews_dir = os.path.join(args.out, "previews")
    for d in (images_dir, labels_dir, previews_dir):
        os.makedirs(d, exist_ok=True)

    with open(os.path.join(args.out, "classes.txt"), "w") as f:
        f.write("\n".join(CLASS_NAMES) + "\n")

    if args.videos_dir:
        video_paths = find_videos(args.videos_dir)
        print(f"Found {len(video_paths)} .mp4 files under {args.videos_dir}")
    else:
        video_paths = args.video_paths

    if not video_paths:
        print("No videos to process — pass video paths directly or use --videos-dir.")
        sys.exit(1)

    model = YOLO(args.model)
    coco_classes = list(COCO_QUERY_CLASSES)

    total_saved = 0
    for video_path in video_paths:
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps else 0
        max_seconds = args.max_seconds if args.max_seconds > 0 else duration
        video_tag = os.path.splitext(os.path.basename(video_path))[0]

        saved_this_video = 0
        t = 0.0
        while t < max_seconds and t < duration:
            frame_num = int(round(t * fps))
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            if not ret:
                t += args.interval
                continue

            keep_boxes, best_conf = process_frame_detections(
                frame, model, coco_classes, args.min_label_conf
            )

            if best_conf >= args.frame_conf:
                base_name = f"{video_tag}_t{int(t)}s"
                write_frame_outputs(frame, keep_boxes, images_dir, labels_dir, previews_dir, base_name)
                saved_this_video += 1

            t += args.interval

        cap.release()
        print(f"  {video_path}: saved {saved_this_video} candidate frames")
        total_saved += saved_this_video

    print(f"\nSaved {total_saved} candidate frames total.")
    print(f"  Images:   {images_dir}")
    print(f"  Labels:   {labels_dir}  (YOLO format, for Roboflow pre-annotation)")
    print(f"  Previews: {previews_dir}  (boxes drawn in, for quick visual scanning)")
    print(f"  classes.txt written to {args.out} — class order matches label indices")


def process_frame_detections(frame, model, coco_classes, min_label_conf,
                             fuse_cyclist=True):
    """Run detection on a single frame.

    Returns (keep_boxes, best_conf) where keep_boxes is a list of
    (local_cls, x1, y1, x2, y2, conf) for every detection at or above
    min_label_conf, and best_conf is the highest confidence among them
    (0.0 if nothing detected). Local class ids follow CLASS_NAMES
    (person/car/bus/truck/cyclist/other_vehicle).

    fuse_cyclist: merge overlapping person+COCO-bicycle pairs into 'cyclist'
    and drop unfused bicycles (see fuse_cyclists). Pass False to skip fusion;
    unfused bicycle boxes are still dropped (no bicycle class in taxonomy).
    """
    results = model.predict(frame, classes=coco_classes, conf=min_label_conf,
                             imgsz=1280, verbose=False)
    boxes = results[0].boxes
    best_conf = 0.0
    keep_boxes = []
    if boxes is not None and len(boxes) > 0:
        for box in boxes:
            conf = float(box.conf)
            coco_cls = int(box.cls)
            best_conf = max(best_conf, conf)
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            if coco_cls == COCO_BICYCLE:
                keep_boxes.append((CLS_TEMP_BICYCLE, x1, y1, x2, y2, conf))
            elif coco_cls in COCO_TO_LOCAL:
                keep_boxes.append((COCO_TO_LOCAL[coco_cls], x1, y1, x2, y2, conf))
    if fuse_cyclist:
        keep_boxes = fuse_cyclists(keep_boxes)
    else:
        keep_boxes = [b for b in keep_boxes if b[0] != CLS_TEMP_BICYCLE]
    return keep_boxes, best_conf


def write_frame_outputs(frame, keep_boxes, images_dir, labels_dir, previews_dir, base_name):
    """Write the raw image, YOLO-format label file, and boxed preview for
    one kept frame."""
    h, w = frame.shape[:2]

    img_path = os.path.join(images_dir, base_name + ".jpg")
    cv2.imwrite(img_path, frame)

    label_path = os.path.join(labels_dir, base_name + ".txt")
    with open(label_path, "w") as lf:
        for (cls_id, x1, y1, x2, y2, conf) in keep_boxes:
            cx = ((x1 + x2) / 2) / w
            cy = ((y1 + y2) / 2) / h
            bw = (x2 - x1) / w
            bh = (y2 - y1) / h
            lf.write(f"{cls_id} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}\n")

    preview = frame.copy()
    for (cls_id, x1, y1, x2, y2, conf) in keep_boxes:
        label = f"{CLASS_NAMES[cls_id]} {conf:.2f}"
        draw_box(preview, (x1, y1, x2, y2), label, (255, 140, 0))
    cv2.imwrite(os.path.join(previews_dir, base_name + ".jpg"), preview)


def _read_label_boxes(label_path):
    """Parse a previously-written YOLO label file back into the minimal
    (cls_id,) tuples QuotaTracker.record() needs. Used on resume, so a
    frame that was already extracted (and counted against quota) in an
    earlier, interrupted run gets its quota contribution restored
    instead of double-counted or silently dropped."""
    boxes = []
    try:
        with open(label_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                boxes.append((int(line.split()[0]),))
    except FileNotFoundError:
        pass
    return boxes


def sample_video(video_path, site_label, year_label, interval, max_seconds, model, coco_classes,
                  min_label_conf, images_dir, labels_dir, previews_dir, tag, gate_conf=None,
                  quota_tracker=None, fuse_cyclist=True, max_frames=0,
                  sampling_method=None, split=None, manifest_rows=None,
                  seen_keys=None):
    """Walk a video at `interval` seconds, run detection on each sampled
    frame, and save the ones that pass the gate.

    gate_conf=None  -> UNIFORM sampling: every sampled frame is kept
                        regardless of what the model finds. This is the
                        only mode used for validation, and is also used
                        for the "routine coverage / hard negative" bucket
                        in training — because inclusion doesn't depend on
                        the model's own confidence, it introduces no
                        selection bias. quota_tracker is ignored here
                        even if passed, so this bucket's coverage stays
                        unbiased by per-class targets too.
    gate_conf=X     -> CONFIDENCE-GATED mining: a frame is kept only if
                        the model's best detection reaches X. This is an
                        efficient way to bootstrap training labels, but
                        it selects for frames the model already handles
                        reasonably well — using it for validation would
                        inflate apparent performance. Train only.

    quota_tracker   -> Optional QuotaTracker, only meaningful when
                        gate_conf is set (the mining pass). On top of the
                        confidence gate, a frame must also contain at
                        least one class that still has room under both
                        its global and per-site quota (fairness is keyed
                        by site_label, since one site can span many
                        chunked .mp4 files). See QuotaTracker for why
                        this is a frame-level gate, not a per-box
                        truncator.

    max_frames      -> Stop after this many NEW saves in this call (0 = no
                        limit). Used to hit the journal frame recipe caps.
    seen_keys       -> Optional set of (source_video, frame_number) already
                        taken; duplicates are skipped (uniform vs mined).
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps else 0
    stop_at = max_seconds if max_seconds > 0 else duration
    video_tag = os.path.splitext(os.path.basename(video_path))[0]
    source_video = os.path.abspath(video_path)
    method = sampling_method or tag

    saved = 0
    resumed = 0
    t = 0.0
    while t < stop_at and t < duration:
        if max_frames > 0 and saved >= max_frames:
            break

        # RESUME CHECK: if this frame's image+label were already written by
        # an earlier (interrupted) run, skip the seek/decode/YOLO entirely --
        # that's the expensive part, and this is what makes an sbatch re-run
        # after a timeout/crash pick up where it left off instead of
        # reprocessing everything. Quota bookkeeping is restored from the
        # existing label file so per-class caps stay correct on resume.
        base_name = f"{site_label}_{year_label}_{video_tag}_{tag}_t{int(t)}s"
        img_path = os.path.join(images_dir, base_name + ".jpg")
        label_path = os.path.join(labels_dir, base_name + ".txt")
        frame_num = int(round(t * fps))
        dedupe_key = (source_video, frame_num)

        if os.path.exists(img_path) and os.path.exists(label_path):
            if seen_keys is not None and dedupe_key in seen_keys:
                t += interval
                continue
            saved += 1
            resumed += 1
            if seen_keys is not None:
                seen_keys.add(dedupe_key)
            if gate_conf is not None and quota_tracker is not None:
                quota_tracker.record(site_label, _read_label_boxes(label_path))
            if manifest_rows is not None:
                manifest_rows.append({
                    "path": img_path,
                    "source_video": source_video,
                    "timestamp": round(t, 3),
                    "frame_number": frame_num,
                    "site": site_label,
                    "sampling_method": method,
                    "split": split or "",
                })
            t += interval
            continue

        if seen_keys is not None and dedupe_key in seen_keys:
            t += interval
            continue

        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        if not ret:
            t += interval
            continue

        keep_boxes, best_conf = process_frame_detections(
            frame, model, coco_classes, min_label_conf, fuse_cyclist=fuse_cyclist)

        keep_this_frame = True if gate_conf is None else (best_conf >= gate_conf)
        if keep_this_frame and gate_conf is not None and quota_tracker is not None:
            if not quota_tracker.would_accept(site_label, keep_boxes):
                keep_this_frame = False
                quota_tracker.frames_skipped += 1

        if keep_this_frame:
            write_frame_outputs(frame, keep_boxes, images_dir, labels_dir, previews_dir, base_name)
            saved += 1
            if seen_keys is not None:
                seen_keys.add(dedupe_key)
            if gate_conf is not None and quota_tracker is not None:
                quota_tracker.record(site_label, keep_boxes)
            if manifest_rows is not None:
                manifest_rows.append({
                    "path": os.path.join(images_dir, base_name + ".jpg"),
                    "source_video": source_video,
                    "timestamp": round(t, 3),
                    "frame_number": frame_num,
                    "site": site_label,
                    "sampling_method": method,
                    "split": split or "",
                })

        t += interval

    cap.release()
    if resumed:
        print(f"    (resumed: {resumed}/{saved} frames already existed on disk, skipped re-decoding/inference)")
    return saved


def _allocate_per_site(global_budget, site_labels):
    """Split a global frame budget evenly across distinct sites.

    Returns dict site_label -> int share. Remainder frames go to the first
    sites in sorted order so the total always equals global_budget.
    global_budget <= 0 means unlimited (empty dict; caller treats as no cap).
    """
    sites = sorted(set(site_labels))
    if not sites or global_budget <= 0:
        return {}
    n = len(sites)
    base, rem = divmod(global_budget, n)
    return {s: base + (1 if i < rem else 0) for i, s in enumerate(sites)}


def _group_videos_by_site(videos):
    """videos: list of (video_path, site_label, year_label) -> dict site -> list."""
    by_site = {}
    for video_path, site_label, year_label in videos:
        by_site.setdefault(site_label, []).append((video_path, year_label))
    return by_site


def _count_label_instances(labels_dir):
    """Return dict class_name -> instance count from YOLO label files."""
    counts = {name: 0 for name in CLASS_NAMES}
    if not os.path.isdir(labels_dir):
        return counts
    for fname in os.listdir(labels_dir):
        if not fname.endswith(".txt"):
            continue
        with open(os.path.join(labels_dir, fname)) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                cls_id = int(line.split()[0])
                if 0 <= cls_id < len(CLASS_NAMES):
                    counts[CLASS_NAMES[cls_id]] += 1
    return counts


def _write_manifest(path, rows):
    fields = ["path", "source_video", "timestamp", "frame_number",
              "site", "sampling_method", "split"]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})


def cmd_build(args):
    """One-shot, leakage-safe dataset build for a paper-ready pilot set.

    Design, and why it's built this way:

    - SPLIT IS BY VIDEO, NOT BY FRAME. Every video passed via
      --train-videos-dir or --val-videos-dir contributes ALL of its
      sampled frames to that split and only that split. Frames a couple
      seconds apart from the same hour of the same camera are near-
      duplicates (same background, same lighting, often the same car
      still in frame) — splitting those across train/val would let the
      model partially memorize rather than generalize, and would make
      validation performance look better than it is. This function
      refuses to run (loud error) if the same video path shows up in
      both lists.

    - VALIDATION IS SAMPLED UNIFORMLY, NEVER CONFIDENCE-GATED. Frames are
      only ever included in val by fixed time interval. If val inclusion
      depended on the model's own detection confidence, val would be
      biased toward frames the model already handles well — an inflated,
      not-defensible performance estimate. Uniform sampling is used for
      ALL of val and for one bucket of train (see below); confidence-
      gated mining is used ONLY for train.

    - TRAIN GETS TWO SAMPLING PASSES:
        1. Uniform (gate_conf=None) at --uniform-interval — routine
           coverage: background variety, lighting variety, and true
           negatives, unbiased by what the model currently detects.
        2. Confidence-gated mining (gate_conf=--frame-conf) at
           --mine-interval — an efficient way to bootstrap pre-filled
           boxes for frames containing something detectable.

    - Frame caps (--max-uniform-frames / --max-mined-frames /
      --max-val-frames) enforce the journal 550-frame recipe when set.
    """
    from ultralytics import YOLO

    train_videos = find_videos_with_site(args.train_videos_dir)
    val_videos = find_videos_with_site(args.val_videos_dir)

    overlap = {vp for vp, _, _ in train_videos} & {vp for vp, _, _ in val_videos}
    if overlap:
        print("ERROR: the following video(s) appear in BOTH --train-videos-dir and --val-videos-dir:")
        for v in sorted(overlap):
            print(f"  {v}")
        print("A video must belong to exactly one split — otherwise you leak near-duplicate frames")
        print("across train/val and your reported validation numbers won't be defensible.")
        sys.exit(1)

    if not train_videos:
        print("No training videos found under --train-videos-dir — check the path(s).")
        sys.exit(1)
    if not val_videos:
        print("No validation videos found under --val-videos-dir — check the path(s).")
        print("A model without a held-out validation set has no defensible way to report")
        print("performance; this is not optional for a paper.")
        sys.exit(1)

    model = YOLO(args.model)
    coco_classes = list(COCO_QUERY_CLASSES)

    name_to_idx = {name: i for i, name in enumerate(CLASS_NAMES)}
    quota_args = {
        "person": args.quota_person,
        "car": args.quota_car,
        "bus": args.quota_bus,
        "truck": args.quota_truck,
        "other_vehicle": args.quota_other_vehicle,
        # Defaults to None (unlimited). Cyclists are the rare class this study
        # exists to measure -- roughly 0.001% of frames -- so capping them is
        # the opposite of what you want.
        "cyclist": args.quota_cyclist,
    }
    global_quotas = {
        name_to_idx[name]: q for name, q in quota_args.items() if q is not None and q > 0
    }
    quota_tracker = None
    if global_quotas and not args.no_quotas:
        train_site_labels = sorted({sl for _, sl, _ in train_videos})
        quota_tracker = QuotaTracker(global_quotas, train_site_labels)
        print("Per-class quotas active for the mining pass (train only, fairness keyed by site):")
        for cls_id, q in sorted(global_quotas.items()):
            per_site = quota_tracker.per_site_quotas[cls_id]
            print(f"  {CLASS_NAMES[cls_id]:<14} global<= {q:<5}  per-site share<= {per_site}"
                  f"  (across {len(train_site_labels)} sites: {', '.join(train_site_labels)})")

    summary = []  # (split, site_label, year_label, video_path, bucket, n_saved)
    manifest_rows = []
    seen_keys = set()  # (source_video, frame_number) across all passes

    train_sites = sorted({sl for _, sl, _ in train_videos})
    val_sites = sorted({sl for _, sl, _ in val_videos})
    print("=== Source inventory (fail loud if a listed dir is empty) ===")
    train_by_site = _group_videos_by_site(train_videos)
    val_by_site = _group_videos_by_site(val_videos)
    for sl in train_sites:
        print(f"  [train] {sl}: {len(train_by_site[sl])} video(s)")
    for sl in val_sites:
        print(f"  [val]   {sl}: {len(val_by_site[sl])} video(s)")
    if len(train_sites) < len(args.train_videos_dir):
        print("WARNING: fewer train sites than --train-videos-dir paths — "
              "a directory may be empty or missing. Check paths.")

    # --- VAL (Corrine): denser uniform (+ optional rare-class mine top-up) ---
    # Never enters train. Caps and intervals are independent of the train pass.
    val_images = os.path.join(args.out, "val", "images")
    val_labels = os.path.join(args.out, "val", "labels")
    val_previews = os.path.join(args.out, "val", "previews")
    for d in (val_images, val_labels, val_previews):
        os.makedirs(d, exist_ok=True)
    with open(os.path.join(args.out, "val", "classes.txt"), "w") as f:
        f.write("\n".join(CLASS_NAMES) + "\n")

    val_interval = args.val_uniform_interval
    val_site_budgets = _allocate_per_site(args.max_val_frames, val_sites)
    if val_site_budgets:
        print(f"\nVal uniform budgets (per site, denser interval={val_interval}s):")
        for sl, b in val_site_budgets.items():
            print(f"  {sl}: {b}")
    val_site_remaining = dict(val_site_budgets)

    for site_label in val_sites:
        remaining = val_site_remaining.get(site_label)
        # remaining None/missing with empty budgets => unlimited (max_val_frames=0)
        unlimited = not val_site_budgets
        if not unlimited and remaining is not None and remaining <= 0:
            continue
        for video_path, year_label in val_by_site[site_label]:
            if not unlimited and remaining <= 0:
                break
            cap_here = 0 if unlimited else remaining
            n_uniform = sample_video(
                video_path, site_label, year_label, val_interval, args.max_seconds,
                model, coco_classes, args.min_label_conf, val_images, val_labels, val_previews,
                tag="uniform", gate_conf=None, fuse_cyclist=not args.no_fuse_cyclist,
                max_frames=cap_here, sampling_method="val_uniform", split="val",
                manifest_rows=manifest_rows, seen_keys=seen_keys,
            )
            print(f"  [val] {site_label} ({year_label}) {video_path}: "
                  f"uniform pass saved {n_uniform} frames")
            summary.append(("val", site_label, year_label, video_path, "val_uniform", n_uniform))
            if not unlimited:
                remaining -= n_uniform
        if not unlimited:
            val_site_remaining[site_label] = remaining

    # Optional Corrine-only detection-guided top-up for rare classes (still val).
    val_mine_budget = args.max_val_mined_frames
    if val_mine_budget > 0:
        print(f"\nVal detection-guided top-up (rare-class densify, never train): "
              f"{val_mine_budget} frames @ conf>={args.frame_conf}")
        # Prefer frames that contain bus / truck / other_vehicle / cyclist / person
        # via the existing QuotaTracker keyed on val sites.
        rare_quotas = {
            name_to_idx["bus"]: max(20, val_mine_budget),
            name_to_idx["truck"]: max(20, val_mine_budget),
            name_to_idx["other_vehicle"]: max(20, val_mine_budget),
            name_to_idx["cyclist"]: max(20, val_mine_budget),
            name_to_idx["person"]: max(20, val_mine_budget),
        }
        val_quota = QuotaTracker(rare_quotas, val_sites)
        val_mine_remaining = val_mine_budget
        for site_label in val_sites:
            if val_mine_remaining <= 0:
                break
            for video_path, year_label in val_by_site[site_label]:
                if val_mine_remaining <= 0:
                    break
                n_mined = sample_video(
                    video_path, site_label, year_label, args.mine_interval, args.max_seconds,
                    model, coco_classes, args.min_label_conf, val_images, val_labels, val_previews,
                    tag="vmined", gate_conf=args.frame_conf, quota_tracker=val_quota,
                    fuse_cyclist=not args.no_fuse_cyclist,
                    max_frames=val_mine_remaining,
                    sampling_method="val_detection_guided", split="val",
                    manifest_rows=manifest_rows, seen_keys=seen_keys,
                )
                print(f"  [val] {site_label} ({year_label}) {video_path}: "
                      f"rare-class mine saved {n_mined} frames")
                summary.append(("val", site_label, year_label, video_path,
                                "val_detection_guided", n_mined))
                val_mine_remaining -= n_mined

    # --- TRAIN: uniform then mined, budgets split EVENLY across sites ---
    train_images = os.path.join(args.out, "train", "images")
    train_labels = os.path.join(args.out, "train", "labels")
    train_previews = os.path.join(args.out, "train", "previews")
    for d in (train_images, train_labels, train_previews):
        os.makedirs(d, exist_ok=True)
    with open(os.path.join(args.out, "train", "classes.txt"), "w") as f:
        f.write("\n".join(CLASS_NAMES) + "\n")

    uniform_site_budgets = _allocate_per_site(args.max_uniform_frames, train_sites)
    if uniform_site_budgets:
        print(f"\nTrain uniform budgets (per site, total={args.max_uniform_frames}):")
        for sl, b in uniform_site_budgets.items():
            print(f"  {sl}: {b}")
    else:
        print("\nTrain uniform: unlimited (no --max-uniform-frames)")

    for site_label in train_sites:
        unlimited = not uniform_site_budgets
        remaining = uniform_site_budgets.get(site_label, 0)
        if not unlimited and remaining <= 0:
            continue
        for video_path, year_label in train_by_site[site_label]:
            if not unlimited and remaining <= 0:
                break
            cap_here = 0 if unlimited else remaining
            n_uniform = sample_video(
                video_path, site_label, year_label, args.uniform_interval, args.max_seconds,
                model, coco_classes, args.min_label_conf, train_images, train_labels, train_previews,
                tag="uniform", gate_conf=None, fuse_cyclist=not args.no_fuse_cyclist,
                max_frames=cap_here, sampling_method="uniform", split="train",
                manifest_rows=manifest_rows, seen_keys=seen_keys,
            )
            print(f"  [train] {site_label} ({year_label}) {video_path}: "
                  f"uniform pass saved {n_uniform} frames")
            summary.append(("train", site_label, year_label, video_path, "uniform", n_uniform))
            if not unlimited:
                remaining -= n_uniform

    mined_site_budgets = _allocate_per_site(args.max_mined_frames, train_sites)
    if mined_site_budgets:
        print(f"\nTrain detection-guided budgets (per site, total={args.max_mined_frames}):")
        for sl, b in mined_site_budgets.items():
            print(f"  {sl}: {b}")
    else:
        print("\nTrain detection-guided: unlimited (no --max-mined-frames)")

    for site_label in train_sites:
        unlimited = not mined_site_budgets
        remaining = mined_site_budgets.get(site_label, 0)
        if not unlimited and remaining <= 0:
            continue
        for video_path, year_label in train_by_site[site_label]:
            if not unlimited and remaining <= 0:
                break
            cap_here = 0 if unlimited else remaining
            n_mined = sample_video(
                video_path, site_label, year_label, args.mine_interval, args.max_seconds,
                model, coco_classes, args.min_label_conf, train_images, train_labels, train_previews,
                tag="mined", gate_conf=args.frame_conf, quota_tracker=quota_tracker,
                fuse_cyclist=not args.no_fuse_cyclist,
                max_frames=cap_here, sampling_method="detection_guided", split="train",
                manifest_rows=manifest_rows, seen_keys=seen_keys,
            )
            print(f"  [train] {site_label} ({year_label}) {video_path}: "
                  f"mined pass saved {n_mined} frames")
            summary.append(("train", site_label, year_label, video_path,
                            "detection_guided", n_mined))
            if not unlimited:
                remaining -= n_mined

    # Per-site frame totals for the methods section
    site_totals = {}
    for split, site_label, year_label, video_path, bucket, n in summary:
        if split != "train":
            continue
        site_totals[site_label] = site_totals.get(site_label, 0) + n
    print("\n=== Train frames per site (must be roughly even) ===")
    for sl in train_sites:
        print(f"  {sl}: {site_totals.get(sl, 0)}")
    if site_totals:
        vals = list(site_totals.values())
        if max(vals) > 2 * max(1, min(vals)):
            print("WARNING: one train site has >2x another — check empty dirs or resume leftovers.")

    manifest_path = os.path.join(args.out, "pool_manifest.csv")
    _write_manifest(manifest_path, manifest_rows)

    print("\n=== Dataset build summary (keep this for your methods section) ===")
    print(f"{'split':<6} {'site':<20} {'year':<6} {'bucket':<22} {'frames':>7}")
    for split, site_label, year_label, video_path, bucket, n in summary:
        print(f"{split:<6} {site_label:<20} {year_label:<6} {bucket:<22} {n:>7}")
    total_train = sum(n for s, _, _, _, _, n in summary if s == "train")
    total_val = sum(n for s, _, _, _, _, n in summary if s == "val")
    print(f"\nTotal train frames: {total_train}  ({len(train_videos)} source videos, "
          f"{len(train_sites)} sites)")
    print(f"Total val frames:   {total_val}  ({len(val_videos)} source videos, "
          f"{len(val_sites)} sites)")
    print(f"Manifest: {manifest_path}  ({len(manifest_rows)} rows)")

    if quota_tracker is not None:
        print("\n=== Per-class instance quotas (mining pass, train only) ===")
        for line in quota_tracker.summary_lines():
            print(line)

    # Rare-class coverage check on Corrine (val) — never move these into train.
    val_counts = _count_label_instances(val_labels)
    print("\n=== Corrine / val per-class instance counts (pre-labels) ===")
    for name in CLASS_NAMES:
        print(f"  {name:<14} {val_counts[name]}")
    rare = ("bus", "truck", "other_vehicle", "cyclist")
    thin = [c for c in rare if val_counts[c] < 5]
    if thin:
        print("\nWARNING: val has thin coverage for:", ", ".join(thin))
        print("  Report per-class mAP only for classes with adequate val support,")
        print("  or raise --max-val-frames / --max-val-mined-frames / denser")
        print("  --val-uniform-interval on Corrine ONLY (never train on Corrine).")
    else:
        print("\nVal rare-class coverage looks adequate (>=5 instances for "
              "bus/truck/other_vehicle/cyclist).")

    print(f"\nOutput:")
    print(f"  {args.out}/train/  (images/, labels/, previews/, classes.txt)")
    print(f"  {args.out}/val/    (images/, labels/, previews/, classes.txt)")
    print(f"  {manifest_path}")
    print("\nDo NOT let Roboflow / CVAT re-shuffle splits — site membership defines train/val.")
    print("Next: merge with Colonial track mine via assemble_annotation_pool.py")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="mode", required=True)

    p_uniform = sub.add_parser("uniform", help="Sample frames evenly across one or more videos")
    p_uniform.add_argument("video_paths", nargs="+", help="One or more video file paths")
    p_uniform.add_argument("--interval", type=float, default=12.0, help="Seconds between sampled frames (default 12)")
    p_uniform.add_argument("--max-seconds", type=float, default=0, help="Stop after this many seconds per video (0 = whole video)")
    p_uniform.add_argument("--out", required=True, help="Output directory for saved frames")
    p_uniform.set_defaults(func=cmd_uniform)

    p_picks = sub.add_parser("picks", help="Grab specific hand-picked timestamps from a text file")
    p_picks.add_argument("picks_file", help="Text file: video_path,timestamp_seconds,label (one per line)")
    p_picks.add_argument("--out", required=True, help="Output directory for saved frames")
    p_picks.set_defaults(func=cmd_picks)

    p_auto = sub.add_parser("auto", help="Auto-mine candidate frames using the current model, with pre-filled boxes for Roboflow")
    p_auto.add_argument("video_paths", nargs="*", help="Video file paths (omit if using --videos-dir)")
    p_auto.add_argument("--videos-dir", default=None, help="Recursively scan this folder for .mp4 files instead of listing them by hand")
    p_auto.add_argument("--interval", type=float, default=2.0, help="Seconds between checked frames (default 2)")
    p_auto.add_argument("--max-seconds", type=float, default=300, help="Stop after this many seconds per video (default 300 = 5 min; 0 = whole video)")
    p_auto.add_argument("--frame-conf", type=float, default=0.5, help="Save the frame if any detection reaches this confidence (default 0.5)")
    p_auto.add_argument("--min-label-conf", type=float, default=0.25, help="Include a box in the pre-filled label if it reaches this confidence (default 0.25, lower than --frame-conf so borderline real objects aren't dropped)")
    p_auto.add_argument("--model", default="yolov8l.pt", help="Ultralytics model weights to use for mining (default yolov8l.pt)")
    p_auto.add_argument("--out", required=True, help="Output directory (creates images/, labels/, previews/ inside it)")
    p_auto.set_defaults(func=cmd_auto)

    p_build = sub.add_parser(
        "build",
        help="One-shot, leakage-safe train/val dataset build (recommended for a paper)",
    )
    p_build.add_argument("--train-videos-dir", nargs="+", required=True,
                          help="One or more directories to scan recursively for training videos")
    p_build.add_argument("--val-videos-dir", nargs="+", required=True,
                          help="One or more directories to scan recursively for validation videos "
                               "(must not overlap with --train-videos-dir)")
    p_build.add_argument("--uniform-interval", type=float, default=15.0,
                          help="Seconds between uniformly-sampled TRAIN frames (default 15)")
    p_build.add_argument("--val-uniform-interval", type=float, default=5.0,
                          help="Seconds between Corrine/val uniform frames (default 5, denser "
                               "than train so rare classes are more likely to appear). "
                               "Val never enters train.")
    p_build.add_argument("--mine-interval", type=float, default=2.0,
                          help="Seconds between checked frames for the confidence-gated train mining "
                               "pass (default 2)")
    p_build.add_argument("--max-seconds", type=float, default=0,
                          help="Stop after this many seconds per video (0 = whole video, default)")
    p_build.add_argument("--frame-conf", type=float, default=0.5,
                          help="Train mining pass keeps a frame if any detection reaches this "
                               "confidence (default 0.5). Also used for optional val rare-class "
                               "top-up. Never moves val frames into train.")
    p_build.add_argument("--min-label-conf", type=float, default=0.25,
                          help="Include a box in the pre-filled label if it reaches this confidence "
                               "(default 0.25)")
    p_build.add_argument("--model", default="yolov8l.pt",
                          help="Ultralytics model weights to use (default yolov8l.pt)")
    p_build.add_argument("--out", required=True,
                          help="Output directory (creates train/ and val/ subfolders, each with "
                               "images/, labels/, previews/, classes.txt)")
    p_build.add_argument("--quota-car", type=int, default=400,
                          help="Max car instances across the train mining pass (default 400). "
                               "Also divided evenly across train sites as a per-site cap.")
    p_build.add_argument("--quota-truck", type=int, default=120,
                          help="Max truck instances across the train mining pass (default 120).")
    p_build.add_argument("--quota-bus", type=int, default=100,
                          help="Max bus instances across the train mining pass (default 100).")
    p_build.add_argument("--quota-person", type=int, default=150,
                          help="Max person instances across the train mining pass (default 150).")
    p_build.add_argument("--quota-other-vehicle", type=int, default=100,
                          help="Max other_vehicle instances (motorcycle/scooter/etc.) "
                               "across the train mining pass (default 100).")
    p_build.add_argument("--quota-cyclist", type=int, default=None,
        help="Max 'cyclist' (fused person+bicycle) instances; default unlimited. "
             "This is the rare class the study measures -- capping it is almost "
             "never right.")
    p_build.add_argument("--no-fuse-cyclist", action="store_true",
        help="Skip person+bicycle fusion; unfused bicycle boxes are still dropped "
             "(no bicycle class in the 6-class taxonomy).")
    p_build.add_argument("--no-quotas", action="store_true",
                          help="Disable all per-class quotas and fall back to pure confidence-gated "
                               "mining (old behavior).")
    p_build.add_argument("--max-uniform-frames", type=int, default=120,
                          help="Cap on train uniform frames, split EVENLY across train sites "
                               "(default 120; 0 = unlimited). Prevents one site eating the budget.")
    p_build.add_argument("--max-mined-frames", type=int, default=180,
                          help="Cap on train detection-guided frames, split EVENLY across train "
                               "sites (default 180; 0 = unlimited).")
    p_build.add_argument("--max-val-frames", type=int, default=150,
                          help="Cap on Corrine/val uniform frames (default 150 densified; "
                               "0 = unlimited). Never enters train.")
    p_build.add_argument("--max-val-mined-frames", type=int, default=50,
                          help="Optional Corrine-only detection-guided top-up for rare classes "
                               "(default 50; 0 = skip). Still val-only — never train.")
    p_build.set_defaults(func=cmd_build)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
