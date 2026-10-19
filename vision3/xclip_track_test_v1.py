#!/usr/bin/env python3
"""
xclip_track_test_v1.py

Cheap experiment: can zero-shot X-CLIP (a video-text model) separate the
real cyclist from the pedestrian / worker that the detector keeps calling
"cyclist"?

For each chosen tracker_id in track_j_diagnostic.csv, this:
  1. splits the track's frames into windows (default 30 frames),
  2. samples 8 frames per window (X-CLIP base expects 8),
  3. crops a square around that track's box in each frame and resizes to 224,
  4. asks X-CLIP to score text labels ("riding a bike", "walking", ...),
  5. prints the average probability per label per track.

If the cyclist track scores high on "riding a bike" and the pedestrian/worker
tracks score low, X-CLIP is a usable second check. If everything looks the
same, the distant crops are too small/blurry for it and it is not worth
pursuing. It does NOT train anything and does not touch your detector.

Requires: pip install transformers   (torch, opencv already in yolo_env)
First run downloads the model (~600 MB) from Hugging Face, so run it once on
the login node (internet) before any sbatch use.

Usage:
    python xclip_track_test_v1.py \\
        --video test.mp4 \\
        --csv pilot_output/compare_v4/track_j_diagnostic.csv \\
        --track-ids 1 2 5 \\
        --outdir pilot_output/compare_v4/xclip_test_v1

Track ids come from whichever diagnostic run wrote the CSV. For the rtdetr_v3
run: 1 = worker at the cones, 2 = real cyclist, 5 = pedestrian. If you have
re-run the diagnostic since, check the ids again first.
"""
import argparse
import csv
import os
from collections import defaultdict

import cv2
import numpy as np
import torch
from transformers import XCLIPModel, XCLIPProcessor

MODEL_NAME = "microsoft/xclip-base-patch32"
N_FRAMES = 8  # this X-CLIP variant takes 8 frames per clip


def load_tracks(csv_path, track_ids):
    tracks = defaultdict(list)
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            tid = int(row["tracker_id"])
            if tid in track_ids:
                tracks[tid].append((int(row["frame"]), float(row["cx"]),
                                    float(row["cy"]), float(row["w"]), float(row["h"])))
    for tid in tracks:
        tracks[tid].sort()
    return tracks


def nearest_box(rows, frame):
    return min(rows, key=lambda r: abs(r[0] - frame))


def make_windows(rows, window, min_frames):
    """Split a track into windows of `window` frames; sample N_FRAMES per window."""
    first, last = rows[0][0], rows[-1][0]
    windows = []
    start = first
    while start <= last:
        end = min(start + window - 1, last)
        # skip tiny leftovers, but keep a short track as one window
        if end - start + 1 >= min_frames or (start == first and end == last):
            idxs = np.linspace(start, end, N_FRAMES).round().astype(int).tolist()
            windows.append((start, end, idxs))
        start += window
    return windows


def crop_square(frame, cx, cy, w, h, pad, out=224):
    H, W = frame.shape[:2]
    side = max(w, h) * (1 + pad)
    side = max(side, 48)  # never crop absurdly small
    x1, y1 = int(cx - side / 2), int(cy - side / 2)
    x2, y2 = int(cx + side / 2), int(cy + side / 2)
    # clamp by shifting, keep it square where possible
    x1, x2 = max(0, x1), min(W, x2)
    y1, y2 = max(0, y1), min(H, y2)
    crop = frame[y1:y2, x1:x2]
    crop = cv2.resize(crop, (out, out), interpolation=cv2.INTER_CUBIC)
    return crop


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--video", required=True)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--track-ids", type=int, nargs="+", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--labels", nargs="+",
                    default=["riding a bike", "walking", "standing still"],
                    help="text labels X-CLIP scores (default: riding a bike / walking / standing still)")
    ap.add_argument("--window", type=int, default=30, help="frames per window (default 30)")
    ap.add_argument("--min-frames", type=int, default=8,
                    help="drop leftover windows shorter than this (default 8)")
    ap.add_argument("--pad", type=float, default=0.6,
                    help="extra context around the box, as a fraction of box size (default 0.6)")
    ap.add_argument("--save-crops", action="store_true",
                    help="save each window's 8 crops side by side so you can look at them")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    tracks = load_tracks(args.csv, set(args.track_ids))
    missing = [t for t in args.track_ids if t not in tracks]
    if missing:
        print(f"WARNING: track ids not found in CSV: {missing}")
    if not tracks:
        print("Nothing to do.")
        return

    # plan every window, and collect every frame number we need to read
    plan = {}
    needed = set()
    for tid, rows in tracks.items():
        plan[tid] = make_windows(rows, args.window, args.min_frames)
        for _, _, idxs in plan[tid]:
            needed.update(idxs)

    print(f"Reading {len(needed)} frames from {args.video} ...")
    frames = {}
    cap = cv2.VideoCapture(args.video)
    fi, max_needed = 0, max(needed)
    while fi <= max_needed:
        ok, frame = cap.read()
        if not ok:
            break
        fi += 1  # 1-based, matches the diagnostic CSV
        if fi in needed:
            frames[fi] = frame
    cap.release()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading {MODEL_NAME} on {device} ...")
    processor = XCLIPProcessor.from_pretrained(MODEL_NAME)
    model = XCLIPModel.from_pretrained(MODEL_NAME).to(device).eval()

    per_window = []
    summary = {}

    for tid in sorted(plan):
        rows = tracks[tid]
        probs_all = []
        for (start, end, idxs) in plan[tid]:
            crops_bgr = []
            for f in idxs:
                if f not in frames:
                    continue
                _, cx, cy, w, h = nearest_box(rows, f)
                crops_bgr.append(crop_square(frames[f], cx, cy, w, h, args.pad))
            if len(crops_bgr) != N_FRAMES:
                continue

            crops_rgb = [cv2.cvtColor(c, cv2.COLOR_BGR2RGB) for c in crops_bgr]
            inputs = processor(text=args.labels, videos=[crops_rgb],
                               return_tensors="pt", padding=True)
            inputs = {k: v.to(device) for k, v in inputs.items()}
            with torch.no_grad():
                logits = model(**inputs).logits_per_video
            probs = logits.softmax(dim=1)[0].cpu().numpy()
            probs_all.append(probs)
            per_window.append([tid, start, end] + [round(float(p), 3) for p in probs])
            print(f"track {tid} frames {start}-{end}: " +
                  ", ".join(f"{l}={p:.2f}" for l, p in zip(args.labels, probs)))

            if args.save_crops:
                strip = np.hstack(crops_bgr)
                cv2.imwrite(os.path.join(args.outdir, f"track{tid}_f{start}-{end}.jpg"), strip)

        if probs_all:
            summary[tid] = np.mean(probs_all, axis=0)

    print("\n=== average per track ===")
    print("track | windows | " + " | ".join(args.labels))
    for tid in sorted(summary):
        n = sum(1 for r in per_window if r[0] == tid)
        print(f"{tid:5d} | {n:7d} | " + " | ".join(f"{p:.2f}" for p in summary[tid]))

    out_csv = os.path.join(args.outdir, "xclip_window_scores.csv")
    with open(out_csv, "w", newline="") as f:
        wtr = csv.writer(f)
        wtr.writerow(["tracker_id", "start_frame", "end_frame"] + args.labels)
        wtr.writerows(per_window)
    print(f"\nPer-window scores written to {out_csv}")
    print("Read it like this: the real cyclist track should score clearly higher on "
          f"'{args.labels[0]}' than the pedestrian/worker tracks. If all tracks look "
          "alike, the crops are too small for X-CLIP and it is not a useful check here.")


if __name__ == "__main__":
    main()
