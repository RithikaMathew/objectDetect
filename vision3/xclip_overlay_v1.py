#!/usr/bin/env python3
"""
xclip_overlay_v1.py

Draws each track's zero-shot X-CLIP label and score onto the video so you can
watch it: BICYCLIST vs PEDESTRIAN.

Single streaming pass over the video. For every tracker_id in the diagnostic
CSV it keeps a rolling buffer of the last `--window` crops (square, 224x224).
Every `--stride` frames, once a track has at least `--min-frames` crops, it
samples 8 crops from the buffer, scores them with X-CLIP against the text
prompts, smooths the probabilities (EMA), and draws the result on that track's
box until the next update. The label is causal: it reflects the recent past of
the track, so it needs a moment to appear when a track starts.

Usage:
    python xclip_overlay_v1.py \\
        --video test.mp4 \\
        --csv pilot_output/compare_v4/track_j_diagnostic.csv \\
        --out pilot_output/compare_v4/xclip_overlay_v1/overlay.mp4

    # only some tracks:
    ... --track-ids 1 2 5

CSV columns required: tracker_id, frame (1-based), cx, cy, w, h.
Model is downloaded on first use; run once on the login node (internet).
"""
import argparse
import csv
import os
import sys
from collections import defaultdict, deque

import cv2
import numpy as np
import torch
from transformers import XCLIPModel, XCLIPProcessor

MODEL_NAME = "microsoft/xclip-base-patch32"
N_FRAMES = 8
REQUIRED_COLS = ["tracker_id", "frame", "cx", "cy", "w", "h"]

# (short name, text prompt, BGR color)
DEFAULT_CLASSES = [
    ("BICYCLIST", "a person riding a bicycle", (0, 200, 0)),
    ("PEDESTRIAN", "a person walking", (0, 140, 255)),
]


def load_rows(csv_path, track_ids):
    """Return {frame: [(tid, cx, cy, w, h), ...]} and set of tids seen."""
    by_frame = defaultdict(list)
    seen = set()
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLS if c not in (reader.fieldnames or [])]
        if missing:
            sys.exit(f"ERROR: CSV {csv_path} is missing columns {missing}; "
                     f"found {reader.fieldnames}")
        for row in reader:
            tid = int(row["tracker_id"])
            if track_ids is not None and tid not in track_ids:
                continue
            by_frame[int(row["frame"])].append(
                (tid, float(row["cx"]), float(row["cy"]),
                 float(row["w"]), float(row["h"])))
            seen.add(tid)
    return by_frame, seen


def crop_square(frame, cx, cy, w, h, pad, out=224):
    H, W = frame.shape[:2]
    side = max(max(w, h) * (1 + pad), 48)
    x1, y1 = int(cx - side / 2), int(cy - side / 2)
    x2, y2 = int(cx + side / 2), int(cy + side / 2)
    x1, x2 = max(0, x1), min(W, x2)
    y1, y2 = max(0, y1), min(H, y2)
    crop = frame[y1:y2, x1:x2]
    if crop.size == 0:
        return None
    return cv2.resize(crop, (out, out), interpolation=cv2.INTER_CUBIC)


def draw_label(img, box, tid, cls, probs, classes, scale):
    cx, cy, w, h = box
    x1, y1 = int(cx - w / 2), int(cy - h / 2)
    x2, y2 = int(cx + w / 2), int(cy + h / 2)
    thick = max(1, int(round(scale * 2)))
    if cls is None:
        color = (255, 255, 255)
        cv2.rectangle(img, (x1, y1), (x2, y2), color, thick)
        text = f"id {tid} ..."
        lines = [text]
    else:
        color = classes[cls][2]
        cv2.rectangle(img, (x1, y1), (x2, y2), color, thick)
        lines = [f"id {tid} {classes[cls][0]} {probs[cls]:.2f}"]
        lines += [f"{c[0][:4].lower()} {p:.2f}" for c, p in zip(classes, probs)]
    line_h = int(22 * scale) + 6
    y = max(line_h, y1 - 4 - line_h * (len(lines) - 1))
    for i, t in enumerate(lines):
        fs = scale * (0.7 if i == 0 else 0.5)
        (tw, th), _ = cv2.getTextSize(t, cv2.FONT_HERSHEY_SIMPLEX, fs, thick)
        yy = y + i * line_h
        cv2.rectangle(img, (x1, yy - th - 3), (x1 + tw + 4, yy + 3), (0, 0, 0), -1)
        cv2.putText(img, t, (x1 + 2, yy), cv2.FONT_HERSHEY_SIMPLEX, fs,
                    color if i == 0 else (255, 255, 255), thick, cv2.LINE_AA)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--video", required=True)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out", required=True, help="output .mp4 path")
    ap.add_argument("--track-ids", type=int, nargs="+", default=None,
                    help="only these tracker_ids (default: all in the CSV)")
    ap.add_argument("--window", type=int, default=30,
                    help="rolling buffer length in frames (default 30)")
    ap.add_argument("--min-frames", type=int, default=8,
                    help="crops needed before a track is first scored (default 8)")
    ap.add_argument("--stride", type=int, default=5,
                    help="re-score each track every N frames (default 5)")
    ap.add_argument("--pad", type=float, default=0.6,
                    help="context around the box, fraction of box size (default 0.6)")
    ap.add_argument("--ema", type=float, default=0.5,
                    help="weight of the new score in the smoothed score; "
                         "1.0 = no smoothing (default 0.5)")
    ap.add_argument("--prompts", nargs=2, default=None,
                    metavar=("BIKE", "WALK"),
                    help="override the two text prompts, in that order")
    ap.add_argument("--max-frames", type=int, default=0,
                    help="stop after N frames (0 = whole video)")
    args = ap.parse_args()

    if not (0 < args.ema <= 1):
        sys.exit("ERROR: --ema must be in (0, 1]")
    if args.min_frames < 2 or args.min_frames > args.window:
        sys.exit("ERROR: need 2 <= --min-frames <= --window")

    classes = list(DEFAULT_CLASSES)
    if args.prompts:
        classes = [(c[0], p, c[2]) for c, p in zip(classes, args.prompts)]
    prompts = [c[1] for c in classes]

    track_ids = set(args.track_ids) if args.track_ids else None
    by_frame, seen = load_rows(args.csv, track_ids)
    if not seen:
        sys.exit("ERROR: no matching tracks in CSV")
    if track_ids:
        missing = sorted(track_ids - seen)
        if missing:
            print(f"WARNING: track ids not found in CSV: {missing}")
    print(f"Tracks: {sorted(seen)}")

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        sys.exit(f"ERROR: cannot open video {args.video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    writer = cv2.VideoWriter(args.out, cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H))
    if not writer.isOpened():
        sys.exit(f"ERROR: cannot open VideoWriter for {args.out}")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading {MODEL_NAME} on {device} ...")
    processor = XCLIPProcessor.from_pretrained(MODEL_NAME)
    model = XCLIPModel.from_pretrained(MODEL_NAME).to(device).eval()

    scale = max(0.6, H / 1080.0 * 0.9)
    buffers = defaultdict(lambda: deque(maxlen=args.window))
    last_scored = {}          # tid -> frame index of last inference
    smooth = {}               # tid -> smoothed probs (np.ndarray)
    score_log = []            # rows for CSV
    skipped_empty = 0

    fi = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        fi += 1  # 1-based, matches the diagnostic CSV
        if args.max_frames and fi > args.max_frames:
            break

        present = by_frame.get(fi, [])

        # 1. update buffers
        for tid, cx, cy, w, h in present:
            crop = crop_square(frame, cx, cy, w, h, args.pad)
            if crop is None:
                skipped_empty += 1
                continue
            buffers[tid].append(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))

        # 2. which tracks are due for scoring
        due = []
        for tid, *_ in present:
            buf = buffers[tid]
            if len(buf) < args.min_frames:
                continue
            if tid not in last_scored or fi - last_scored[tid] >= args.stride:
                due.append(tid)

        if due:
            clips = []
            for tid in due:
                buf = list(buffers[tid])
                idx = np.linspace(0, len(buf) - 1, N_FRAMES).round().astype(int)
                clips.append([buf[i] for i in idx])
            inputs = processor(text=prompts, videos=clips,
                               return_tensors="pt", padding=True)
            inputs = {k: v.to(device) for k, v in inputs.items()}
            with torch.no_grad():
                logits = model(**inputs).logits_per_video
            probs = logits.softmax(dim=1).cpu().numpy()
            if probs.shape != (len(due), len(classes)):
                sys.exit(f"ERROR: unexpected logits shape {probs.shape}, "
                         f"expected {(len(due), len(classes))}")
            for tid, p in zip(due, probs):
                smooth[tid] = p if tid not in smooth else \
                    args.ema * p + (1 - args.ema) * smooth[tid]
                last_scored[tid] = fi
                score_log.append([tid, fi] + [round(float(x), 3) for x in p] +
                                 [round(float(x), 3) for x in smooth[tid]])

        # 3. draw
        for tid, cx, cy, w, h in present:
            if tid in smooth:
                p = smooth[tid]
                draw_label(frame, (cx, cy, w, h), tid, int(np.argmax(p)), p,
                           classes, scale)
            else:
                draw_label(frame, (cx, cy, w, h), tid, None, None, classes, scale)

        writer.write(frame)
        if fi % 100 == 0:
            print(f"frame {fi}/{total if total > 0 else '?'}")

    cap.release()
    writer.release()

    if fi == 0:
        sys.exit("ERROR: read 0 frames from video")
    if not score_log:
        sys.exit("ERROR: no track was ever scored; check --min-frames, "
                 "track lengths and that CSV frame numbers match the video")
    if skipped_empty:
        print(f"WARNING: {skipped_empty} empty crops skipped (box outside frame)")

    log_path = os.path.splitext(args.out)[0] + "_scores.csv"
    with open(log_path, "w", newline="") as f:
        wtr = csv.writer(f)
        wtr.writerow(["tracker_id", "frame"] +
                     [c[0].lower() for c in classes] +
                     [c[0].lower() + "_smooth" for c in classes])
        wtr.writerows(score_log)

    print("\n=== average smoothed score per track ===")
    print("track | scores | " + " | ".join(c[0] for c in classes))
    by_tid = defaultdict(list)
    for r in score_log:
        by_tid[r[0]].append(r[2 + len(classes):])
    for tid in sorted(by_tid):
        m = np.mean(by_tid[tid], axis=0)
        print(f"{tid:5d} | {len(by_tid[tid]):6d} | " + " | ".join(f"{x:.2f}" for x in m))

    print(f"\nVideo: {args.out}")
    print(f"Scores: {log_path}")


if __name__ == "__main__":
    main()
