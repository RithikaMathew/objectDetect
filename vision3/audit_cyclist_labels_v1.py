#!/usr/bin/env python3
"""
audit_cyclist_labels_v1.py

Hypothesis to test: some of the 60 "cyclist" ground-truth instances in
roboflow_split_v1 are actually mislabeled cones/pedestrians/other objects
-- either from the original Roboflow annotation, or introduced by
fix_mixed_labels.py's polygon-to-bounding-box conversion (18 -> 60
instances came from recovering previously-dropped polygon rows; if any of
those conversions grabbed the wrong region or the original polygon was
mislabeled, the model would have been trained to call that object
"cyclist" -- which would explain a STATIC, high-confidence, persistent
false-positive track far better than generic model confusion does).

This script does NOT touch training or run any model. It just crops every
ground-truth `cyclist`-class YOLO-format label box, across train/val/test,
tight with padding, and saves them with a filename that tells you exactly
which label file + line to go fix if it turns out to be wrong.

Usage:
    python audit_cyclist_labels_v1.py \\
        --split-root /orange/xiangyan/rithika/vision/dataset_frames/roboflow_split_v1 \\
        --outdir pilot_output/compare_v4/cyclist_label_audit \\
        --cyclist-class-id 2

CYCLIST_CLASS_ID defaults to 2 to match split_dataset.py's documented
class order (['bus','car','cyclist','other_vehicle','person','truck']) --
same constant used in compare_detectors_v7_fixed.py's build_finetuned_detector.
Check your data.yaml if this was ever changed.
"""
import argparse
import os
from pathlib import Path

import cv2


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--split-root", required=True,
                     help="roboflow_split_v1 dir containing train/val/test subdirs")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--cyclist-class-id", type=int, default=2)
    ap.add_argument("--pad-frac", type=float, default=0.6,
                     help="padding around each box as a fraction of box size (default 0.6)")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    root = Path(args.split_root)
    total_found = 0

    for split in ["train", "val", "test"]:
        labels_dir = root / split / "labels"
        images_dir = root / split / "images"
        if not labels_dir.exists():
            print(f"skip: {labels_dir} does not exist")
            continue

        label_files = sorted(labels_dir.glob("*.txt"))
        print(f"[{split}] scanning {len(label_files)} label files...")

        for label_path in label_files:
            lines = label_path.read_text().strip().splitlines()
            cyclist_lines = []
            for line_no, line in enumerate(lines):
                parts = line.split()
                if not parts:
                    continue
                cls_id = int(float(parts[0]))
                if cls_id == args.cyclist_class_id:
                    cyclist_lines.append((line_no, parts))

            if not cyclist_lines:
                continue

            img_path = images_dir / (label_path.stem + ".jpg")
            if not img_path.exists():
                # try common alternate extensions
                for ext in [".png", ".jpeg"]:
                    alt = images_dir / (label_path.stem + ext)
                    if alt.exists():
                        img_path = alt
                        break
            if not img_path.exists():
                print(f"  WARNING: no image found for {label_path.name}")
                continue

            img = cv2.imread(str(img_path))
            if img is None:
                print(f"  WARNING: cv2 could not read {img_path}")
                continue
            H, W = img.shape[:2]

            for line_no, parts in cyclist_lines:
                _, cx, cy, w, h = parts[:5]
                cx, cy, w, h = float(cx) * W, float(cy) * H, float(w) * W, float(h) * H
                pad_w, pad_h = w * args.pad_frac, h * args.pad_frac
                x1 = max(0, int(cx - w / 2 - pad_w))
                y1 = max(0, int(cy - h / 2 - pad_h))
                x2 = min(W, int(cx + w / 2 + pad_w))
                y2 = min(H, int(cy + h / 2 + pad_h))
                crop = img[y1:y2, x1:x2]

                out_name = f"{split}_{label_path.stem}_line{line_no}.jpg"
                cv2.imwrite(os.path.join(args.outdir, out_name), crop)
                total_found += 1

    print(f"\nSaved {total_found} cyclist-labeled ground-truth crops to {args.outdir}")
    print("Look through these -- any that show a cone, a pedestrian with no "
          "bike, a car, or anything else are mislabeled ground truth. The "
          "filename tells you exactly which label file + line to fix:")
    print("  <split>_<image_stem>_line<N>.jpg")


if __name__ == "__main__":
    main()
