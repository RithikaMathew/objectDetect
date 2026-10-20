#!/usr/bin/env python3
"""
count_class_instances.py

Two diagnostics the per-class AP table can't show:
  1. Real class balance (instance counts, not just image counts) across
     ALL splits combined -- to see how few cyclist examples the model
     actually had to learn from.
  2. How many label files are "corrupt" per ultralytics' definition
     (mixing segmentation-polygon rows with plain detection-box rows) --
     the val run showed 10/54 dropped in test alone; this checks whether
     train/val have the same problem, since those silently-dropped images
     also don't get used in training, not just eval.

A normal YOLO detection row is exactly 5 space-separated numbers:
    <class_id> <x_center> <y_center> <width> <height>
A segmentation row has a variable, usually much longer, odd-length tail
(flattened polygon coordinates). This script flags any row that isn't
exactly 5 values as suspect, per-file and per-split.

USAGE
    python count_class_instances.py \
        --root /orange/xiangyan/rithika/vision/dataset_frames/roboflow_split_v1
"""
import argparse
from collections import Counter
from pathlib import Path

import yaml


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", required=True,
                     help="Split dataset root containing data.yaml + train/val/test")
    args = ap.parse_args()

    root = Path(args.root)
    yaml_path = root / "data.yaml"
    if not yaml_path.exists():
        raise SystemExit(f"ERROR: {yaml_path} not found")

    with open(yaml_path) as f:
        data = yaml.safe_load(f)
    names = data["names"]
    print(f"Classes: {list(enumerate(names))}\n")

    grand_total = Counter()
    for split in ["train", "val", "test"]:
        labels_dir = root / split / "labels"
        if not labels_dir.is_dir():
            print(f"[{split}] labels dir not found, skipping")
            continue

        split_counts = Counter()
        n_files = 0
        n_empty = 0
        n_mixed_format = 0
        mixed_examples = []

        for lbl_file in sorted(labels_dir.glob("*.txt")):
            n_files += 1
            lines = [l.strip() for l in lbl_file.read_text().splitlines() if l.strip()]
            if not lines:
                n_empty += 1
                continue

            file_is_mixed = False
            for line in lines:
                parts = line.split()
                if len(parts) != 5:
                    file_is_mixed = True
                    continue
                try:
                    cls_id = int(parts[0])
                    split_counts[cls_id] += 1
                    grand_total[cls_id] += 1
                except ValueError:
                    file_is_mixed = True

            if file_is_mixed:
                n_mixed_format += 1
                if len(mixed_examples) < 5:
                    mixed_examples.append(lbl_file.name)

        print(f"=== {split} ===")
        print(f"  {n_files} label files ({n_empty} empty/background)")
        print(f"  {n_mixed_format} files contain non-5-value rows "
              f"(likely segmentation/detection mix -- these get silently "
              f"dropped by ultralytics, including during training)")
        if mixed_examples:
            print(f"  example mixed files: {mixed_examples}")
        for cid in sorted(split_counts):
            print(f"  {names[cid]:16s} {split_counts[cid]}")
        print()

    print("=== combined across train+val+test ===")
    for cid in sorted(grand_total):
        print(f"  {names[cid]:16s} {grand_total[cid]}")
    total_instances = sum(grand_total.values())
    if total_instances:
        cyclist_id = names.index("cyclist") if "cyclist" in names else None
        if cyclist_id is not None:
            pct = 100 * grand_total.get(cyclist_id, 0) / total_instances
            print(f"\ncyclist is {pct:.1f}% of all labeled instances "
                  f"({grand_total.get(cyclist_id, 0)}/{total_instances})")


if __name__ == "__main__":
    main()
