#!/usr/bin/env python3
"""
cyclist_label_coords_v1.py

Tests the "positional memorization" hypothesis: with a static camera, a
small dataset, and temporally-correlated cyclist instances (one bike ride
= many near-identical consecutive frames, not independent examples), the
model may have learned "cyclist tends to appear around THIS region of the
frame" rather than an actual visual bicycle concept. That would explain
why the retrained checkpoint fires persistently at fixed pixel locations
on test.mp4 -- same camera as training, so if those false-positive
locations land near where real training cyclists were annotated, that's
strong evidence for this over generic "not enough data."

Prints (split, image_stem, line_no, cx_px, cy_px, w_px, h_px) for every
ground-truth cyclist box across train/val/test -- plain pixel coordinates,
directly comparable to track_j_diagnostic.csv's centroid columns from the
new-checkpoint diagnostic run.

Usage:
    python cyclist_label_coords_v1.py \\
        --split-root /orange/xiangyan/rithika/vision/dataset_frames/roboflow_split_v1 \\
        --cyclist-class-id 2
"""
import argparse
import csv
from pathlib import Path

import cv2


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--split-root", required=True)
    ap.add_argument("--cyclist-class-id", type=int, default=2)
    ap.add_argument("--out-csv", default="cyclist_label_coords.csv")
    args = ap.parse_args()

    root = Path(args.split_root)
    rows = []

    for split in ["train", "val", "test"]:
        labels_dir = root / split / "labels"
        images_dir = root / split / "images"
        if not labels_dir.exists():
            continue

        for label_path in sorted(labels_dir.glob("*.txt")):
            lines = label_path.read_text().strip().splitlines()
            cyclist_lines = []
            for line_no, line in enumerate(lines):
                parts = line.split()
                if not parts:
                    continue
                if int(float(parts[0])) == args.cyclist_class_id:
                    cyclist_lines.append((line_no, parts))
            if not cyclist_lines:
                continue

            img_path = images_dir / (label_path.stem + ".jpg")
            if not img_path.exists():
                for ext in [".png", ".jpeg"]:
                    alt = images_dir / (label_path.stem + ext)
                    if alt.exists():
                        img_path = alt
                        break
            if not img_path.exists():
                continue
            img = cv2.imread(str(img_path))
            if img is None:
                continue
            H, W = img.shape[:2]

            for line_no, parts in cyclist_lines:
                _, cx, cy, w, h = parts[:5]
                cx_px, cy_px = float(cx) * W, float(cy) * H
                w_px, h_px = float(w) * W, float(h) * H
                rows.append([split, label_path.stem, line_no,
                             round(cx_px, 1), round(cy_px, 1),
                             round(w_px, 1), round(h_px, 1)])
                print(f"{split:5s} {label_path.stem[:50]:50s} line{line_no} "
                      f"cx={cx_px:.1f} cy={cy_px:.1f} w={w_px:.1f} h={h_px:.1f}")

    with open(args.out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["split", "image_stem", "line", "cx", "cy", "w", "h"])
        w.writerows(rows)

    print(f"\nWrote {len(rows)} rows to {args.out_csv}")
    print("\nCompare these (cx, cy) against the new checkpoint's persistent "
          "false-positive track centroids from track_j_diagnostic.csv:")
    print("  track 6:  (74.7, 113.4)  -- 4832 detections, frames 689-5694")
    print("  track 16: (263.8, 305.6) -- 1438 detections, frames 2667-4352")
    print("  track 21-25: (~643, ~22) -- several hundred detections combined")
    print("If real cyclist ground-truth boxes cluster near any of these, "
          "that's evidence of positional memorization rather than a true "
          "visual cyclist detector.")


if __name__ == "__main__":
    main()
