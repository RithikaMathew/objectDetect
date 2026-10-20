#!/usr/bin/env python3
"""
extract_track_frames_v1.py

Pulls specific frames from test.mp4 for visual inspection -- the first,
middle, and last detected frame of every tracker_id found by
diagnose_track_j_v1.py, cropped tight around the detection box (plus
padding) so you can actually see what triggered it, rather than a full
1920x1080 frame with a tiny distant box.

Reads pilot_output/compare_v4/track_j_diagnostic.csv directly -- run
diagnose_track_j_v1.py first if that file doesn't exist yet.

Usage:
    python extract_track_frames_v1.py \\
        --video test.mp4 \\
        --csv pilot_output/compare_v4/track_j_diagnostic.csv \\
        --outdir pilot_output/compare_v4/track_frame_crops
"""
import argparse
import csv
import os
from collections import defaultdict

import cv2


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--video", required=True)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--pad", type=int, default=100,
                     help="pixels of padding around the detection box (default 100)")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    rows_by_track = defaultdict(list)
    with open(args.csv) as f:
        for row in csv.DictReader(f):
            rows_by_track[int(row["tracker_id"])].append(row)

    # pick first, middle, last row per track (dedup if track has <3 rows)
    wanted = {}  # frame_num -> list of (tid, cx, cy, w, h, tag)
    for tid, rows in rows_by_track.items():
        rows = sorted(rows, key=lambda r: int(r["frame"]))
        picks = {rows[0]["frame"]: "first", rows[len(rows) // 2]["frame"]: "mid",
                 rows[-1]["frame"]: "last"}
        for frame_str, tag in picks.items():
            row = next(r for r in rows if r["frame"] == frame_str)
            wanted.setdefault(int(frame_str), []).append(
                (tid, float(row["cx"]), float(row["cy"]),
                 float(row["w"]), float(row["h"]), tag))

    print(f"Extracting {sum(len(v) for v in wanted.values())} crops across "
          f"{len(wanted)} distinct frames for {len(rows_by_track)} tracks...")

    cap = cv2.VideoCapture(args.video)
    frame_idx = 0
    saved = 0
    target_frames = set(wanted.keys())
    max_frame = max(target_frames)

    while frame_idx <= max_frame:
        ok, frame = cap.read()
        if not ok:
            break
        frame_idx += 1
        if frame_idx not in target_frames:
            continue

        H, W = frame.shape[:2]
        for tid, cx, cy, w, h, tag in wanted[frame_idx]:
            x1 = max(0, int(cx - w / 2 - args.pad))
            y1 = max(0, int(cy - h / 2 - args.pad))
            x2 = min(W, int(cx + w / 2 + args.pad))
            y2 = min(H, int(cy + h / 2 + args.pad))
            crop = frame[y1:y2, x1:x2]
            out_name = f"track{tid}_{tag}_frame{frame_idx}.jpg"
            cv2.imwrite(os.path.join(args.outdir, out_name), crop)
            saved += 1

    cap.release()
    print(f"Saved {saved} crops to {args.outdir}")


if __name__ == "__main__":
    main()
