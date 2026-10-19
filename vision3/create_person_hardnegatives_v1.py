#!/usr/bin/env python3
"""
create_person_hardnegatives_v1.py

Avoids manual box-drawing entirely: track_j_diagnostic.csv already logged
the EXACT (cx, cy, w, h) box the retrained model drew around the
pedestrian at locations B (track 16) and C (tracks 21-25) -- confirmed by
visual inspection to genuinely contain the pedestrian each time. We reuse
that same box location, just correct the label to `person` (class id 4)
instead of `cyclist`. This teaches "this box is a person" using the
model's own (correctly-located, wrongly-classified) prediction as the
ground truth box.

Usage:
    python create_person_hardnegatives_v1.py \\
        --video test.mp4 \\
        --csv pilot_output/compare_v4/track_j_diagnostic.csv \\
        --split-root /orange/xiangyan/rithika/vision/dataset_frames/roboflow_split_v1 \\
        --track-ids 16 21 22 \\
        --person-class-id 4 \\
        --n-per-track 1
"""
import argparse
import csv
from collections import defaultdict
from pathlib import Path

import cv2


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--video", required=True)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--split-root", required=True)
    ap.add_argument("--split", default="train", choices=["train", "val", "test"])
    ap.add_argument("--track-ids", type=int, nargs="+", required=True,
                     help="which tracker_ids from the CSV to pull examples from, e.g. 16 21 22")
    ap.add_argument("--person-class-id", type=int, default=4)
    ap.add_argument("--n-per-track", type=int, default=1,
                     help="how many frames to sample per track (spread evenly across its range)")
    args = ap.parse_args()

    by_track = defaultdict(list)
    with open(args.csv) as f:
        for row in csv.DictReader(f):
            tid = int(row["tracker_id"])
            if tid in args.track_ids:
                by_track[tid].append(row)

    # pick n_per_track rows spread evenly across each track's detections
    chosen = []
    for tid in args.track_ids:
        rows = by_track.get(tid, [])
        if not rows:
            print(f"WARNING: no rows found for track {tid} in {args.csv}")
            continue
        rows.sort(key=lambda r: int(r["frame"]))
        step = max(1, len(rows) // args.n_per_track)
        for i in range(0, len(rows), step)[:args.n_per_track]:
            chosen.append(rows[i])

    if not chosen:
        print("No rows selected -- check --track-ids match what's in the CSV.")
        return

    images_dir = Path(args.split_root) / args.split / "images"
    labels_dir = Path(args.split_root) / args.split / "labels"
    images_dir.mkdir(parents=True, exist_ok=True)
    labels_dir.mkdir(parents=True, exist_ok=True)

    target_frames = {int(r["frame"]): r for r in chosen}
    cap = cv2.VideoCapture(args.video)
    frame_idx = 0
    max_frame = max(target_frames.keys())
    saved = []

    while frame_idx <= max_frame:
        ok, frame = cap.read()
        if not ok:
            break
        frame_idx += 1
        if frame_idx not in target_frames:
            continue

        row = target_frames[frame_idx]
        H, W = frame.shape[:2]
        cx, cy, w, h = float(row["cx"]), float(row["cy"]), float(row["w"]), float(row["h"])

        # normalize to YOLO format
        cx_n, cy_n, w_n, h_n = cx / W, cy / H, w / W, h / H

        stem = f"hardneg_person_testmp4_frame{frame_idx}_track{row['tracker_id']}"
        img_path = images_dir / f"{stem}.jpg"
        label_path = labels_dir / f"{stem}.txt"

        cv2.imwrite(str(img_path), frame)
        label_path.write_text(
            f"{args.person_class_id} {cx_n:.6f} {cy_n:.6f} {w_n:.6f} {h_n:.6f}\n"
        )
        saved.append((stem, cx, cy, w, h))

    cap.release()

    print(f"Added {len(saved)} person-labeled hard negatives to "
          f"{args.split_root}/{args.split}/:")
    for stem, cx, cy, w, h in saved:
        print(f"  {stem}  (box: cx={cx:.1f} cy={cy:.1f} w={w:.1f} h={h:.1f})")
    print("\nIMPORTANT: these frames may contain OTHER real objects (cars, "
          "etc.) elsewhere in the image that are NOT labeled by this script "
          "-- it only writes the one person box, nothing else in the frame. "
          "If this matters for training, check the frame and add other "
          "boxes by hand; leaving them unlabeled is the same convention "
          "already used for the other hard-negative frames this session, "
          "not a new problem introduced here.")
    print("\nRECOMMENDED before retraining -- verify each box visually:")
    print("  (open the saved image + overlay the box, or trust the crops "
          "you already reviewed from track_frame_crops_v2/ for these exact "
          "frame/track combinations)")


if __name__ == "__main__":
    main()
