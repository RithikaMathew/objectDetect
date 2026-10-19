"""
Tiled YOLO detection + VRU tracking, v2.

Changes from pilot_detect.py, each traceable to evidence in
pilot_detect_41807016.log:

  1. Tracker: IoU association (3/12 links passed on the known cyclist) replaced
     with velocity-predicted, size-normalized centroid association (12/12).
     See vru_tracker.py for the measured link-by-link comparison.

  2. Track-before-detect. Detection runs at a LOW confidence (default 0.05) and
     the accept/reject decision moves to track level (max confidence over the
     whole track). A cyclist whose per-frame confidence dips to 0.07 mid-track
     is no longer silently dropped. Per-frame thresholding is the wrong place
     to threshold rare, small objects.

  3. Motion filtering moved from per-detection to per-track net displacement.
     A bad MOG2 mask on one frame can no longer delete a real cyclist, while a
     static misclassified artifact is still rejected -- more reliably, since
     "never moved across its entire life" is much stronger evidence than
     "overlapped <15% foreground on this one frame".

  4. Per-frame funnel CSV. Every stage's surviving count is written to disk, so
     "where did recall leak" is answerable from data instead of by guessing.
     This table is also the ablation figure for the paper.

  5. Annotated video shows only accepted boxes. --render-window renders a short
      span at FULL frame rate for visual inspection.

Usage
-----
  # Full run
  python pilot_detect_v2.py VIDEO 1800

  # Render just the known-cyclist window at full frame rate, to watch
  python pilot_detect_v2.py VIDEO --render-window 400 420

  # Check the ROI/tile overlay on one frame
  python pilot_detect_v2.py VIDEO --show-roi
"""

from ultralytics import YOLO
import cv2
import numpy as np
import os
import sys
import csv
import time
import shutil
import subprocess
import argparse
import re

from vru_tracker import VruTracker, iou_xyxy, merge_redundant_tracks

# --------------------------------------------------------------------------
# ROI. Full frame by default -- every detection anywhere in the frame counts.
# Narrow this ONLY if a specific camera has a persistent false-positive source
# you cannot otherwise suppress (a parking lot, a billboard). Narrowing it to
# "just the bike lane" would be a mistake: cyclists ride on sidewalks and in
# travel lanes, and measuring that is the entire point of the study.
# --------------------------------------------------------------------------
ROI_POLYGON_FRAC = [(0.00, 0.00), (1.00, 0.00), (1.00, 1.00), (0.00, 1.00)]

TILE_GRID = (2, 2)
TILE_OVERLAP_FRAC = 0.2
TILE_MERGE_IOU_THRESH = 0.5
MAX_BOX_AREA_FRAC_OF_TILE = 0.5

COCO_CLASSES = [0, 1, 2, 3, 5, 7]  # person, bicycle, car, motorcycle, bus, truck
# Fine-tuned six-class journal taxonomy (see extract_frames.CLASS_NAMES)
FINE_TUNE_NAMES = ("person", "car", "bus", "truck", "cyclist", "other_vehicle")


def resolve_detect_classes(model):
    """Return (class_id_list_or_None, is_finetuned, do_fuse_cyclist).

    COCO baseline weights must be filtered to the VRU/vehicle subset. A
    fine-tuned six-class checkpoint already emits person/car/bus/truck/
    cyclist/other_vehicle — passing COCO indices here would DROP cyclist
    (local id 4) and request nonexistent COCO id 7.
    """
    names = model.names
    if isinstance(names, dict):
        name_list = [names[i] for i in sorted(names)]
    else:
        name_list = list(names)
    is_ft = (
        len(name_list) == len(FINE_TUNE_NAMES)
        and all(n in name_list for n in FINE_TUNE_NAMES)
        and "bicycle" not in name_list
    )
    if is_ft:
        return list(range(len(name_list))), True, False
    return COCO_CLASSES, False, True

# Per-class persistence requirements. A cyclist crosses the frame in ~2s; a car
# waiting at a light sits for 30s. One global threshold cannot serve both, and
# the old 1.0s-for-everything rule was tuned on cars.
#
# COCO path: person+bicycle fused to cyclist; confidence mass is split / noisy.
# Fine-tuned path: a dedicated cyclist head — Colonial FT recount hit 1445 vs
# GT 89 with COCO gates (night 50/h >> day 20/h). FT needs stricter confirmation.
MIN_TRACK_SECONDS = {"cyclist": 0.5, "bicycle": 0.5, "person": 0.5,
                     "motorcycle": 0.5, "other_vehicle": 0.5, "_default": 1.0}
MIN_TRACK_MAX_CONF = {"cyclist": 0.50, "bicycle": 0.50, "person": 0.50,
                      "_default": 0.55}
MIN_TRACK_MEAN_CONF = {"cyclist": 0.18, "bicycle": 0.18, "person": 0.20,
                       "_default": 0.22}

# Stricter profile applied when resolve_detect_classes() says is_finetuned.
# Clip-review v2 (gated window): real cyclist missed, ped→cyclist, a few car FPs.
# Night mean floor 0.40 + min 1.5s was killing recall. Loosen duration/peak;
# keep night mean slightly above day (0.35) so lights stay harder than day noise.
FT_MIN_TRACK_SECONDS = {"cyclist": 1.0, "bicycle": 1.0, "person": 0.5,
                        "other_vehicle": 0.5, "_default": 1.0}
FT_MIN_TRACK_MAX_CONF = {"cyclist": 0.60, "bicycle": 0.60, "person": 0.55,
                         "_default": 0.60}
FT_MIN_TRACK_MEAN_CONF = {"cyclist": 0.28, "bicycle": 0.28, "person": 0.28,
                          "_default": 0.30}
# Extra mean_conf floor for tracks whose wall-clock midpoint falls in night
# (21:00–05:00). Justified by FT Colonial night rate 50.8/h vs day 19.8/h
# and clip review (car/grass/light labeled cyclist at night).
FT_NIGHT_MEAN_CONF_EXTRA = 0.07  # cyclist night mean_conf >= 0.35
NIGHT_START_HOUR, NIGHT_END_HOUR = 21, 5


def _is_night_hour(hh):
    return hh is not None and (hh >= NIGHT_START_HOUR or hh < NIGHT_END_HOUR)


def infer_chunk_start_hour(video_path, tag, explicit_hour=None):
    """Wall-clock hour when this hourly chunk starts (for night confirmation)."""
    if explicit_hour is not None:
        return explicit_hour % 24
    # Prefer all_videos.txt timestamps when available
    try:
        from validate_counts import load_chunk_times
        times = load_chunk_times()
        if tag in times:
            return times[tag][1]
    except Exception:
        pass
    # MioVision Bike Lane Study: .001 = 05:00
    m = re.search(r"\.(\d{3})$", tag)
    if m:
        return (4 + int(m.group(1))) % 24
    return None


def track_wall_hour(chunk_start_hour, t_mid_sec):
    if chunk_start_hour is None:
        return None
    return int(chunk_start_hour + (t_mid_sec / 3600.0)) % 24


def confirmation_tables(is_finetuned):
    """Return (min_seconds, max_conf, mean_conf) dicts for the active weight set."""
    if is_finetuned:
        return FT_MIN_TRACK_SECONDS, FT_MIN_TRACK_MAX_CONF, FT_MIN_TRACK_MEAN_CONF
    return MIN_TRACK_SECONDS, MIN_TRACK_MAX_CONF, MIN_TRACK_MEAN_CONF


# A track must travel this many box-diagonals to count as a real moving object.
MIN_NET_DISPLACEMENT = 0.75


def frac_polygon_to_pixels(polygon_frac, shape):
    h, w = shape[:2]
    return [(int(round(x * w)), int(round(y * h))) for (x, y) in polygon_frac]


def point_in_roi(x, y, polygon_px):
    pts = np.array(polygon_px, dtype=np.int32)
    return cv2.pointPolygonTest(pts, (float(x), float(y)), False) >= 0


def compute_tiles(frame_shape, grid=TILE_GRID, overlap_frac=TILE_OVERLAP_FRAC):
    h, w = frame_shape[:2]
    cols, rows = grid
    bw, bh = w / cols, h / rows
    pad_w, pad_h = bw * overlap_frac, bh * overlap_frac
    tiles = []
    for r in range(rows):
        for c in range(cols):
            x0, y0 = c * bw, r * bh
            tiles.append((max(0, int(x0 - pad_w)), max(0, int(y0 - pad_h)),
                          min(w, int(x0 + bw + pad_w)), min(h, int(y0 + bh + pad_h))))
    return tiles


def merge_tile_detections(all_dets, iou_thresh=TILE_MERGE_IOU_THRESH):
    if not all_dets:
        return []
    by_class = {}
    for det in all_dets:
        by_class.setdefault(det[5], []).append(det)
    kept = []
    for _, dets in by_class.items():
        boxes = [[d[0], d[1], d[2] - d[0], d[3] - d[1]] for d in dets]
        scores = [float(d[4]) for d in dets]
        idx = cv2.dnn.NMSBoxes(boxes, scores, score_threshold=0.0, nms_threshold=iou_thresh)
        if idx is None or len(idx) == 0:
            continue
        for i in np.array(idx).flatten():
            kept.append(dets[i])
    return kept


def suppress_contained(dets, contain_thresh=0.70):
    """Drop a detection that sits almost entirely inside a higher-confidence one.

    Plain IoU-NMS cannot remove these: a 'bicycle' box nested inside a
    'bicycle+rider' box has high containment but LOW IoU (the areas differ too
    much), so both survive a 0.5 IoU threshold and each goes on to seed its own
    track. Measuring intersection against the SMALLER box's area catches the
    nesting that IoU misses.

    Cross-class by design -- the nested pair is often 'person' inside
    'bicycle', or the reverse.
    """
    if len(dets) < 2:
        return dets
    order = sorted(range(len(dets)), key=lambda i: -dets[i][4])
    dropped = set()
    for ai, i in enumerate(order):
        if i in dropped:
            continue
        a = dets[i]
        for j in order[ai + 1:]:
            if j in dropped:
                continue
            b = dets[j]
            ix1, iy1 = max(a[0], b[0]), max(a[1], b[1])
            ix2, iy2 = min(a[2], b[2]), min(a[3], b[3])
            inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
            if inter <= 0:
                continue
            area_b = max(1e-6, (b[2] - b[0]) * (b[3] - b[1]))
            area_a = max(1e-6, (a[2] - a[0]) * (a[3] - a[1]))
            if inter / min(area_a, area_b) >= contain_thresh:
                dropped.add(j)
    return [d for k, d in enumerate(dets) if k not in dropped]


VRU_CLASSES = {"person", "bicycle", "motorcycle", "other_vehicle", "cyclist"}


def remap_coco_class_name(name):
    """Map raw COCO / baseline names into the journal 6-class taxonomy.

    Fine-tuned weights emit the six names directly. COCO baseline still emits
    bicycle/motorcycle; motorcycle -> other_vehicle. Bicycle is kept through
    fusion (person+bicycle -> cyclist) and as cyclist evidence in the tracker.
    """
    if name == "motorcycle":
        return "other_vehicle"
    return name


def fuse_cyclist_dets(dets, overlap_thresh=0.25):
    """Merge an overlapping person+bicycle pair into one 'cyclist' detection.

    COCO splits a cyclist into two objects; the ground truth counts one. Fusing
    here, before tracking, means the tracker sees one object instead of two
    competing ones -- which is what produced a class label flickering between
    'person' and 'bicycle' on a single rider.
    """
    persons = [i for i, d in enumerate(dets) if d[5] == "person"]
    bikes = [i for i, d in enumerate(dets) if d[5] in ("bicycle", "motorcycle")]
    if not persons or not bikes:
        return dets
    cands = []
    for pi in persons:
        for bi in bikes:
            p, b = dets[pi], dets[bi]
            ix1, iy1 = max(p[0], b[0]), max(p[1], b[1])
            ix2, iy2 = min(p[2], b[2]), min(p[3], b[3])
            inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
            if inter <= 0:
                continue
            pa = max(1e-6, (p[2] - p[0]) * (p[3] - p[1]))
            ba = max(1e-6, (b[2] - b[0]) * (b[3] - b[1]))
            ov = inter / min(pa, ba)
            if ov >= overlap_thresh:
                cands.append((ov, pi, bi))
    if not cands:
        return dets
    cands.sort(reverse=True)
    used, fused = set(), []
    for ov, pi, bi in cands:
        if pi in used or bi in used:
            continue
        used.add(pi); used.add(bi)
        p, b = dets[pi], dets[bi]
        fused.append((min(p[0], b[0]), min(p[1], b[1]),
                      max(p[2], b[2]), max(p[3], b[3]),
                      max(p[4], b[4]), "cyclist"))
    return [d for i, d in enumerate(dets) if i not in used] + fused


def apply_class_remap(dets):
    """Remap detection class names after fusion (motorcycle -> other_vehicle)."""
    out = []
    for d in dets:
        name = remap_coco_class_name(d[5])
        out.append((d[0], d[1], d[2], d[3], d[4], name))
    return out


def detect_tiled(model, frame, tiles, classes, conf, imgsz):
    """Returns (merged_detections, n_raw_tile_detections).

    All tiles go to the GPU in ONE batched predict call rather than one call
    per tile. A 2x2 grid means 4 sequential calls otherwise, each paying full
    Python/CUDA launch overhead on a tile far smaller than the model's input
    size -- the GPU sits idle between them. Batching matters at this project's
    scale: a site-session is 48 hourly chunks, so per-frame cost multiplies by
    ~1.3 million frames.
    """
    crops, offsets = [], []
    for (xa, ya, xb, yb) in tiles:
        tile = frame[ya:yb, xa:xb]
        if tile.size == 0:
            continue
        crops.append(tile)
        offsets.append((xa, ya, tile.shape[0] * tile.shape[1]))
    if not crops:
        return [], 0

    results = model.predict(crops, classes=classes, conf=conf, imgsz=imgsz,
                            verbose=False)

    all_dets = []
    for res, (xa, ya, tile_area) in zip(results, offsets):
        boxes = res.boxes
        if boxes is None or len(boxes) == 0:
            continue
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            area = max(0.0, x2 - x1) * max(0.0, y2 - y1)
            if tile_area > 0 and (area / tile_area) > MAX_BOX_AREA_FRAC_OF_TILE:
                continue
            all_dets.append((x1 + xa, y1 + ya, x2 + xa, y2 + ya,
                             float(box.conf), model.names[int(box.cls)]))
    return suppress_contained(merge_tile_detections(all_dets)), len(all_dets)


# --------------------------------------------------------------------------
# Drawing
# --------------------------------------------------------------------------
CLASS_COLORS = {
    "cyclist": (0, 220, 255),
    "bicycle": (40, 160, 200), "person": (0, 255, 120), "car": (255, 160, 0),
    "truck": (200, 100, 255), "bus": (255, 80, 80), "motorcycle": (80, 200, 255),
    "other_vehicle": (80, 200, 255),
}


def draw_box(frame, xyxy, label, color, thick=2):
    x1, y1, x2, y2 = [int(v) for v in xyxy]
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thick)
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
    cv2.rectangle(frame, (x1, max(0, y1 - th - 6)), (x1 + tw + 4, y1), color, -1)
    cv2.putText(frame, label, (x1 + 2, max(9, y1 - 4)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (20, 20, 20), 1, cv2.LINE_AA)


def annotate(frame, drawn, t, hud=""):
    out = frame.copy()
    for (tid, x1, y1, x2, y2, cls_name, conf) in drawn:
        color = CLASS_COLORS.get(cls_name, (180, 180, 180))
        thick = 3 if cls_name in ("cyclist", "bicycle", "person") else 1
        draw_box(out, (x1, y1, x2, y2), f"#{tid} {cls_name} {conf:.2f}", color, thick)
    banner = f"t={t:7.2f}s   {hud}"
    cv2.rectangle(out, (0, 0), (out.shape[1], 20), (0, 0, 0), -1)
    cv2.putText(out, banner, (5, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                (255, 255, 255), 1, cv2.LINE_AA)
    return out


def format_assumed_clock(chunk_start_hour, t_sec):
    """HH:MM label from chunk start hour + seconds into chunk (for HUD)."""
    if chunk_start_hour is None:
        return "clock=?"
    total_m = int(chunk_start_hour * 60 + t_sec / 60.0) % (24 * 60)
    return f"assumed {total_m // 60:02d}:{total_m % 60:02d}"

# --------------------------------------------------------------------------
def encode_h264(src_path):
    """Re-encode to H.264 with the ffmpeg CLI, returning the new path or None.

    OpenCV's VideoWriter cannot be relied on for H.264 here: asked for 'avc1'
    it picked h264_v4l2m2m, a hardware encoder for embedded devices, which does
    not exist on a HiPerGator compute node ("Could not find a valid device").
    The mp4v fourcc that OpenCV falls back to writes MPEG-4 Part 2, which
    QuickTime refuses to open. Transcoding with the ffmpeg binary afterwards
    sidesteps OpenCV's encoder selection entirely.
    """
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("  note: ffmpeg not on PATH -- video is mp4v and may not play in "
              "QuickTime. Run `module load ffmpeg` and re-run, or convert by hand:")
        print(f"    ffmpeg -i '{src_path}' -c:v libx264 -pix_fmt yuv420p "
              f"'{os.path.splitext(src_path)[0]}_h264.mp4'")
        return None
    out = os.path.splitext(src_path)[0] + "_h264.mp4"
    cmd = [ffmpeg, "-y", "-loglevel", "error", "-i", src_path,
           "-c:v", "libx264", "-preset", "fast", "-crf", "23",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
    try:
        subprocess.run(cmd, check=True)
    except (subprocess.CalledProcessError, OSError) as e:
        print(f"  note: ffmpeg transcode failed ({e}); keeping mp4v file.")
        return None
    os.remove(src_path)
    return out


def open_writer(path, fps, size):
    """mp4v only. H.264 is applied afterwards by encode_h264()."""
    w = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"mp4v"), fps, size)
    if not w.isOpened():
        raise SystemExit(f"FATAL: could not open a VideoWriter for {path}")
    return w


def main():
    p = argparse.ArgumentParser()
    p.add_argument("video_path")
    p.add_argument("max_seconds", nargs="?", type=int, default=300,
                   help="Process only the first N seconds (0 = whole video)")
    p.add_argument("--weights", default="yolov8l.pt")
    p.add_argument("--conf", type=float, default=0.05,
                   help="Per-frame DETECTION confidence. Keep this low: the real "
                        "decision is made at track level.")
    p.add_argument("--stride", type=int, default=3,
                   help="Run detection every Nth raw frame.")
    p.add_argument("--imgsz", type=int, default=1280)
    p.add_argument("--center-dist", type=float, default=1.0,
                   help="Association gate, in box diagonals.")
    p.add_argument("--coast-seconds", type=float, default=0.8,
                   help="How long a track survives with no matching detection "
                        "before being retired. Specified in SECONDS so it does "
                        "not silently change meaning with --stride.")
    p.add_argument("--outdir", default="pilot_output/v2")
    p.add_argument("--show-roi", action="store_true")
    p.add_argument("--render-window", nargs=2, type=float, metavar=("START", "END"),
                   help="Process only START..END seconds, at FULL frame rate.")
    p.add_argument("--no-fuse-cyclist", action="store_true",
                   help="Keep raw person/bicycle classes instead of fusing "
                        "overlapping pairs into a single 'cyclist' detection.")
    p.add_argument("--no-merge-tracks", action="store_true",
                   help="Skip the redundant-track merge pass.")
    p.add_argument("--merge-dist", type=float, default=1.2,
                   help="Two co-occurring tracks staying within this many box "
                        "diagonals of each other are treated as one object.")
    p.add_argument("--debug-merge", action="store_true",
                   help="Print the pairwise numbers behind every merge decision "
                        "among confirmed tracks, including near-misses.")
    p.add_argument("--video-mode", choices=["highlights", "all", "none"], default=None,
                   help="highlights (default for full runs): only spans containing "
                        "a confirmed cyclist/pedestrian. all (default for "
                        "--render-window): every sampled frame. none: no video.")
    p.add_argument("--highlight-pad", type=float, default=2.0,
                   help="Seconds of context around each confirmed VRU track.")
    p.add_argument("--draw-all", action="store_true",
                   help="Draw every raw detection, including ones the pipeline "
                        "rejected, subject to --draw-conf. Off by default -- at "
                        "conf=0.05 most boxes are noise the tracker discards, "
                        "and drawing them makes the video unreadable.")
    p.add_argument("--draw-conf", type=float, default=0.25,
                   help="Do not draw boxes below this per-frame confidence, "
                        "even when --draw-all is used (default: 0.25).")
    p.add_argument("--force-coco-gates", action="store_true",
                   help="Use COCO confirmation thresholds even with fine-tuned "
                        "weights (ablation / debugging).")
    p.add_argument("--no-night-gate", action="store_true",
                   help="Disable the extra fine-tuned night mean_conf floor.")
    p.add_argument("--chunk-hour", type=int, default=None,
                   help="Wall-clock start hour (0-23) of this chunk for night "
                        "gating. If omitted, inferred from ...0000.NNN basename "
                        "(.001 => 05:00) or all_videos.txt when present.")
    p.add_argument("--debug-confirm", action="store_true",
                   help="Print per-track confirmation decisions for "
                        "cyclist/bicycle/person (why counted or rejected).")
    args = p.parse_args()

    if not os.path.isfile(args.weights):
        raise SystemExit(f"FATAL: weights not found: {args.weights}  "
                         f"(cwd={os.getcwd()})")
    os.makedirs(args.outdir, exist_ok=True)
    cap = cv2.VideoCapture(args.video_path)
    if not cap.isOpened():
        raise SystemExit(f"FATAL: could not open {args.video_path} (cwd={os.getcwd()})")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    tag = os.path.splitext(os.path.basename(args.video_path))[0]

    if args.show_roi:
        ok, frame = cap.read()
        if not ok:
            raise SystemExit("Could not read a frame.")
        prev = frame.copy()
        pts = np.array(frac_polygon_to_pixels(ROI_POLYGON_FRAC, frame.shape), dtype=np.int32)
        cv2.polylines(prev, [pts], True, (0, 0, 255), 2)
        for (xa, ya, xb, yb) in compute_tiles(frame.shape):
            cv2.rectangle(prev, (xa, ya), (xb, yb), (0, 255, 255), 1)
        out = os.path.join(args.outdir, f"{tag}_roi_preview.jpg")
        cv2.imwrite(out, prev)
        print(f"Saved {out}  (frame is {frame.shape[1]}x{frame.shape[0]})")
        return

    model = YOLO(args.weights)
    detect_classes, is_finetuned, default_fuse = resolve_detect_classes(model)
    names = model.names
    if isinstance(names, dict):
        name_list = [names[i] for i in sorted(names)]
    else:
        name_list = list(names)
    print(f"model.names ({len(name_list)}): {name_list}")
    if not is_finetuned:
        print("WARNING: not detected as six-class fine-tune — using COCO path "
              "(person/bicycle fuse). If you expected best.pt, check WEIGHTS.")
    if args.force_coco_gates:
        is_finetuned_gates = False
    else:
        is_finetuned_gates = is_finetuned
    do_fuse = (not args.no_fuse_cyclist) and default_fuse
    min_sec, max_conf_tbl, mean_conf_tbl = confirmation_tables(is_finetuned_gates)
    chunk_hour = infer_chunk_start_hour(args.video_path, tag, args.chunk_hour)
    # Compare archive listing vs explicit override (camera OSD can disagree).
    try:
        from validate_counts import load_chunk_times
        listed = load_chunk_times().get(tag)
        if listed is not None and chunk_hour is not None and listed[1] != chunk_hour:
            print(f"WARNING: all_videos.txt lists hour={listed[1]:02d}:00 for this "
                  f"chunk, but using chunk_hour={chunk_hour:02d} "
                  f"(camera OSD / --chunk-hour). Night gate follows chunk_hour.")
    except Exception:
        pass
    print(f"weights={args.weights}  finetuned={is_finetuned}  "
          f"ft_gates={is_finetuned_gates}  detect_classes={detect_classes}  "
          f"fuse_cyclist={do_fuse}  chunk_hour={chunk_hour}  "
          f"night_gate={is_finetuned_gates and not args.no_night_gate}")
    if is_finetuned_gates:
        print(f"  FT cyclist gates: max_conf>={max_conf_tbl.get('cyclist')}  "
              f"mean_conf>={mean_conf_tbl.get('cyclist')}  "
              f"min_s>={min_sec.get('cyclist')}  "
              f"night_mean+={FT_NIGHT_MEAN_CONF_EXTRA}")

    if args.render_window:
        t0, t1 = args.render_window
        # Default to every frame for a hand-inspected window, but honour an
        # explicit --stride. Matching the counting run's stride matters when the
        # point is to see what the COUNTER saw: at a different stride the
        # detections, associations and confirmations all differ, so a
        # full-frame-rate re-render can show a cyclist the counting pass never
        # had the chance to see (or miss one it did count).
        stride = args.stride if "--stride" in sys.argv else 1
        start_frame, end_frame = int(t0 * fps), int(t1 * fps)
        suffix = f"_window_{int(t0)}_{int(t1)}"
        video_mode = args.video_mode or "all"
    else:
        stride = args.stride
        start_frame = 0
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        end_frame = int(args.max_seconds * fps) if args.max_seconds > 0 else total
        suffix = ""
        video_mode = args.video_mode or "highlights"

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    dt_sample = stride / fps
    tracker = VruTracker(max_center_dist_frac=args.center_dist,
                         coast_seconds=args.coast_seconds, dt=dt_sample)

    # ---------------- PASS 1: inference ----------------
    csv_path = os.path.join(args.outdir, f"{tag}{suffix}_funnel.csv")
    fcsv = open(csv_path, "w", newline="")
    wcsv = csv.writer(fcsv)
    wcsv.writerow(["t_sec", "frame_idx", "n_raw_tile_dets", "n_after_merge",
                   "n_in_roi", "n_matched", "n_new_tracks", "n_active_tracks",
                   "n_vru_dets", "best_vru_conf"])

    annotations = {}
    roi_px, tiles = None, None
    frame_idx = start_frame
    n_sampled = 0
    t_start = time.time()

    while True:
        ok, frame = cap.read()
        if not ok or frame_idx >= end_frame:
            break
        if (frame_idx - start_frame) % stride == 0:
            t = frame_idx / fps
            if roi_px is None:
                roi_px = frac_polygon_to_pixels(ROI_POLYGON_FRAC, frame.shape)
                tiles = compute_tiles(frame.shape)

            dets, n_raw = detect_tiled(model, frame, tiles, detect_classes,
                                       args.conf, args.imgsz)
            n_merged_dets = len(dets)
            roi_dets = [d for d in dets
                        if point_in_roi((d[0] + d[2]) / 2, (d[1] + d[3]) / 2, roi_px)]
            if do_fuse:
                roi_dets = fuse_cyclist_dets(roi_dets)
            roi_dets = apply_class_remap(roi_dets)

            before = set(tracker.tracks)
            drawn = tracker.update(roi_dets, t, dt_sample)
            new_ids = set(tracker.tracks) - before
            annotations[frame_idx] = drawn

            vru = [d for d in roi_dets if d[5] in ("cyclist", "bicycle", "person")]
            wcsv.writerow([f"{t:.3f}", frame_idx, n_raw, n_merged_dets, len(roi_dets),
                           len(drawn) - len(new_ids), len(new_ids),
                           sum(1 for x in tracker.tracks.values() if x.alive),
                           len(vru),
                           f"{max(d[4] for d in vru):.3f}" if vru else ""])
            n_sampled += 1
            if n_sampled % 200 == 0:
                fcsv.flush()      # so a running job shows progress on disk
        frame_idx += 1

    cap.release()
    fcsv.close()
    infer_secs = time.time() - t_start

    # ---------------- merge + confirm ----------------
    all_tracks = list(tracker.tracks.values())
    n_absorbed, id_map = 0, {}
    if not args.no_merge_tracks:
        all_tracks, n_absorbed, id_map = merge_redundant_tracks(
            all_tracks, max_norm_dist=args.merge_dist, debug=args.debug_merge)

    per_class_min_hits = {c: max(2, int(round(s / dt_sample)))
                          for c, s in min_sec.items()}

    counts, reasons, kept = {}, {}, []
    confirm_rows = []
    for tr in all_tracks:
        mh = per_class_min_hits.get(tr.cls, per_class_min_hits["_default"])
        mc = max_conf_tbl.get(tr.cls, max_conf_tbl["_default"])
        mn = mean_conf_tbl.get(tr.cls, mean_conf_tbl["_default"])
        night_applied = False
        if (is_finetuned_gates and not args.no_night_gate
                and tr.cls in ("cyclist", "bicycle")):
            t_mid = 0.5 * (tr.first_t + tr.last_t)
            wh = track_wall_hour(chunk_hour, t_mid)
            if _is_night_hour(wh):
                mn = mn + FT_NIGHT_MEAN_CONF_EXTRA
                night_applied = True
        reject = None
        if tr.hits < mh:
            reject = "too_few_hits"
            reasons["too_few_hits"] = reasons.get("too_few_hits", 0) + 1
        elif tr.max_conf < mc:
            reject = "low_max_conf"
            reasons["low_max_conf"] = reasons.get("low_max_conf", 0) + 1
        elif tr.mean_conf < mn:
            reject = "low_mean_conf"
            reasons["low_mean_conf"] = reasons.get("low_mean_conf", 0) + 1
        elif tr.max_excursion < MIN_NET_DISPLACEMENT:
            reject = "static_object"
            reasons["static_object"] = reasons.get("static_object", 0) + 1
        else:
            counts[tr.cls] = counts.get(tr.cls, 0) + 1
            kept.append(tr)
        if tr.cls in ("cyclist", "bicycle", "person"):
            confirm_rows.append((tr, reject, mh, mc, mn, night_applied))

    if args.debug_confirm and confirm_rows:
        print("\n=== --debug-confirm (cyclist/bicycle/person) ===")
        for tr, reject, mh, mc, mn, night_applied in sorted(
                confirm_rows, key=lambda x: x[0].first_t):
            status = "COUNTED" if reject is None else f"REJECT:{reject}"
            print(f"  #{tr.id} {tr.cls:12s} t={tr.first_t:.1f}-{tr.last_t:.1f}s "
                  f"hits={tr.hits}/{mh} max={tr.max_conf:.2f}/{mc:.2f} "
                  f"mean={tr.mean_conf:.2f}/{mn:.2f} "
                  f"exc={tr.max_excursion:.1f} "
                  f"{'NIGHT' if night_applied else 'day':5s}  {status}")

    confirmed = {tr.id: tr for tr in kept}

    tracks_csv = os.path.join(args.outdir, f"{tag}{suffix}_tracks.csv")
    with open(tracks_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["track_id", "class", "hits", "first_t", "last_t", "duration_s",
                    "max_conf", "mean_conf", "net_disp_diag", "max_excursion_diag",
                    "counted", "reject_reason"])
        reject_by_id = {tr.id: (rej or "") for tr, rej, *_ in confirm_rows}
        for tr in sorted(all_tracks, key=lambda x: x.first_t):
            counted = "yes" if tr.id in confirmed else "no"
            rej = "" if counted == "yes" else reject_by_id.get(tr.id, "")
            # Non-VRU classes were not stored in confirm_rows — recompute briefly
            if counted == "no" and tr.id not in reject_by_id:
                mh = per_class_min_hits.get(tr.cls, per_class_min_hits["_default"])
                mc = max_conf_tbl.get(tr.cls, max_conf_tbl["_default"])
                mn = mean_conf_tbl.get(tr.cls, mean_conf_tbl["_default"])
                if tr.hits < mh:
                    rej = "too_few_hits"
                elif tr.max_conf < mc:
                    rej = "low_max_conf"
                elif tr.mean_conf < mn:
                    rej = "low_mean_conf"
                elif tr.max_excursion < MIN_NET_DISPLACEMENT:
                    rej = "static_object"
            w.writerow([tr.id, tr.cls, tr.hits, f"{tr.first_t:.2f}", f"{tr.last_t:.2f}",
                        f"{tr.duration:.2f}", f"{tr.max_conf:.3f}", f"{tr.mean_conf:.3f}",
                        f"{tr.net_displacement:.2f}", f"{tr.max_excursion:.2f}",
                        counted, rej])

    # ---------------- PASS 2: render ----------------
    vid_out = None
    if video_mode != "none":
        vru_spans = [(tr.first_t - args.highlight_pad, tr.last_t + args.highlight_pad)
                     for tr in kept if tr.cls in ("cyclist", "bicycle", "person", "motorcycle")]

        def wanted(t):
            if video_mode == "all":
                return True
            return any(a <= t <= b for a, b in vru_spans)

        render_idx = sorted(i for i in annotations if wanted(i / fps))
        if not render_idx:
            print("\nNo frames to render (no confirmed VRU tracks). "
                  "Use --video-mode all to write the whole span anyway.")
        else:
            vid_path = os.path.join(args.outdir, f"{tag}{suffix}_annotated.mp4")
            cap2 = cv2.VideoCapture(args.video_path)
            writer = None
            want = set(render_idx)
            out_fps = max(1.0, fps / stride) if not args.render_window else fps
            cap2.set(cv2.CAP_PROP_POS_FRAMES, render_idx[0])
            fi = render_idx[0]
            written = 0
            while fi <= render_idx[-1]:
                ok, frame = cap2.read()
                if not ok:
                    break
                if fi in want:
                    draws = []
                    for (tid, x1, y1, x2, y2, cls_name, conf) in annotations[fi]:
                        if conf < args.draw_conf:
                            continue
                        canon = id_map.get(tid, tid)
                        if not args.draw_all and canon not in confirmed:
                            continue
                        tr = confirmed.get(canon)
                        draws.append((canon, x1, y1, x2, y2,
                                      tr.cls if tr else cls_name, conf))
                    clock = format_assumed_clock(chunk_hour, fi / fps)
                    img = annotate(frame, draws, fi / fps,
                                   hud=(f"{clock}  shown={len(draws)}  "
                                        f"confirmed_total={len(kept)}"
                                        + ("" if args.draw_all else "  [confirmed only]")))
                    if writer is None:
                        h, w_ = img.shape[:2]
                        writer = open_writer(vid_path, out_fps, (w_, h))
                    writer.write(img)
                    written += 1
                fi += 1
            cap2.release()
            if writer:
                writer.release()
                vid_out = encode_h264(vid_path) or vid_path
                print(f"\nRendered {written} frames "
                      f"({'all sampled' if video_mode=='all' else 'VRU highlights'})")

    # ---------------- report ----------------
    print(f"\n=== pilot_detect_v2  |  {tag}{suffix} ===")
    print(f"weights={args.weights}  conf={args.conf}  stride={stride}  "
          f"imgsz={args.imgsz}  center_dist={args.center_dist}  "
          f"merge_dist={args.merge_dist}  coast={args.coast_seconds}s "
          f"({tracker.max_missed} samples)")
    print(f"{n_sampled} sampled frames, inference {infer_secs:.1f}s "
          f"({infer_secs/max(n_sampled,1):.2f}s/frame)")
    print(f"fps={fps:.2f}  dt between samples={dt_sample:.3f}s")
    print(f"min hits per class: {per_class_min_hits}")
    print(f"\nRaw tracks: {len(tracker.tracks)}  ->  after merge: {len(all_tracks)}"
          f"  ({n_absorbed} absorbed)")
    print(f"COUNTED TRACKS BY CLASS: {counts}")
    print(f"Rejected tracks: {reasons}")
    print(f"\nFunnel CSV : {csv_path}")
    print(f"Tracks CSV : {tracks_csv}")
    if vid_out:
        print(f"Video      : {vid_out}   <-- download this one")

    vrus = [t for t in kept if t.cls in ("cyclist", "bicycle")]
    if vrus:
        print(f"\n{len(vrus)} cyclist track(s):")
        for tr in sorted(vrus, key=lambda x: x.first_t):
            print(f"  #{tr.id}  t={tr.first_t:.1f}-{tr.last_t:.1f}s  "
                  f"hits={tr.hits}  max_conf={tr.max_conf:.2f}  "
                  f"mean_conf={tr.mean_conf:.2f}  "
                  f"travelled={tr.max_excursion:.1f} diagonals")

    # Near-miss report: the tracks that came closest to being counted. If a real
    # cyclist is sitting just under a threshold, this is where it shows up.
    near = [t for t in all_tracks if t.id not in confirmed
            and t.cls in ("cyclist", "bicycle", "person")
            and t.hits >= per_class_min_hits.get(t.cls, 99) * 0.6]
    if near:
        print(f"\nClosest rejected VRU tracks (check for missed cyclists):")
        for tr in sorted(near, key=lambda x: -x.hits)[:8]:
            mh = per_class_min_hits.get(tr.cls, per_class_min_hits["_default"])
            mc_ = MIN_TRACK_MAX_CONF.get(tr.cls, MIN_TRACK_MAX_CONF["_default"])
            mn_ = MIN_TRACK_MEAN_CONF.get(tr.cls, MIN_TRACK_MEAN_CONF["_default"])
            why = []
            if tr.hits < mh:
                why.append(f"hits {tr.hits}<{mh}")
            if tr.max_conf < mc_:
                why.append(f"max_conf {tr.max_conf:.2f}<{mc_}")
            if tr.mean_conf < mn_:
                why.append(f"mean_conf {tr.mean_conf:.2f}<{mn_}")
            if tr.max_excursion < MIN_NET_DISPLACEMENT:
                why.append(f"excursion {tr.max_excursion:.2f}<{MIN_NET_DISPLACEMENT}")
            print(f"  #{tr.id} {tr.cls:<9} t={tr.first_t:.1f}-{tr.last_t:.1f}s  "
                  f"rejected: {', '.join(why)}")


if __name__ == "__main__":
    main()
