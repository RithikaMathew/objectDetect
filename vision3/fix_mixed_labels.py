#!/usr/bin/env python3
"""
fix_mixed_labels.py

count_class_instances.py found that 225/432 train label files (52%) mix
plain YOLO detection rows (`class xc yc w h`, 5 values) with YOLO
segmentation rows (`class x1 y1 x2 y2 ... xn yn`, a flattened polygon,
variable length) in the SAME .txt file -- e.g. one object in an image was
boxed, another in the same image was polygon-annotated. Ultralytics'
loader doesn't partially recover from this: it discards the ENTIRE image
the moment it hits one malformed row, per the "ignoring corrupt
image/label" messages you saw during training and val.

This script recovers those images instead of leaving them dropped: any
row that isn't exactly 5 values is treated as a flattened normalized
polygon and converted to its tight bounding box (min/max of the x's and
y's). Plain 5-value rows are copied through unchanged. Images with zero
valid rows either way are left alone (not fabricated).

This does NOT touch the original export -- it writes a full copy to
--out, images included, so roboflow_raw_v1 stays untouched as your source
of truth. Run this BEFORE split_dataset.py, on the ORIGINAL flat export,
so the (now larger) recovered pool gets split fresh -- don't run this on
an already-split directory.

USAGE
    python fix_mixed_labels.py \
        --src /orange/xiangyan/rithika/vision/dataset_frames/roboflow_raw_v1 \
        --out /orange/xiangyan/rithika/vision/dataset_frames/roboflow_raw_v1_fixed
"""
import argparse
import shutil
from pathlib import Path

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}


def polygon_row_to_bbox_row(parts):
    """parts = ['<class_id>', 'x1', 'y1', 'x2', 'y2', ...] (all strings).
    Returns a 5-value bbox row string, or None if the row can't be parsed
    as a polygon (odd number of coordinate values, non-numeric, etc.)."""
    try:
        cls_id = int(parts[0])
        coords = [float(p) for p in parts[1:]]
    except ValueError:
        return None
    if len(coords) < 6 or len(coords) % 2 != 0:
        # fewer than 3 points, or an unpaired coordinate -- not a valid
        # polygon either; can't recover this row
        return None

    xs = coords[0::2]
    ys = coords[1::2]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    xc = (xmin + xmax) / 2
    yc = (ymin + ymax) / 2
    w = xmax - xmin
    h = ymax - ymin
    return f"{cls_id} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True, help="Original flat Roboflow export root")
    ap.add_argument("--out", required=True, help="Output root for the fixed copy (created fresh)")
    args = ap.parse_args()

    src = Path(args.src)
    out = Path(args.out)
    src_images = src / "train" / "images"
    src_labels = src / "train" / "labels"

    if not src_images.is_dir() or not src_labels.is_dir():
        raise SystemExit(f"ERROR: expected {src_images} and {src_labels} to exist")

    out_images = out / "train" / "images"
    out_labels = out / "train" / "labels"
    out_images.mkdir(parents=True, exist_ok=True)
    out_labels.mkdir(parents=True, exist_ok=True)

    # Carry data.yaml through unchanged if present
    if (src / "data.yaml").exists():
        shutil.copy2(src / "data.yaml", out / "data.yaml")

    n_files = 0
    n_had_polygon_rows = 0
    n_rows_converted = 0
    n_rows_unrecoverable = 0
    n_images_recovered = 0  # files that WOULD have been dropped entirely, now aren't

    for lbl_file in sorted(src_labels.glob("*.txt")):
        n_files += 1
        lines = [l.strip() for l in lbl_file.read_text().splitlines() if l.strip()]

        was_corrupt = False
        out_lines = []
        file_had_conversion = False

        for line in lines:
            parts = line.split()
            if len(parts) == 5:
                out_lines.append(line)
                continue

            was_corrupt = True
            bbox_row = polygon_row_to_bbox_row(parts)
            if bbox_row is not None:
                out_lines.append(bbox_row)
                n_rows_converted += 1
                file_had_conversion = True
            else:
                n_rows_unrecoverable += 1
                # drop just this one row, not the whole file

        if was_corrupt:
            n_had_polygon_rows += 1
        if was_corrupt and out_lines:
            n_images_recovered += 1

        (out_labels / lbl_file.name).write_text("\n".join(out_lines) + ("\n" if out_lines else ""))

        # copy the matching image regardless (even if this label ends up
        # empty -- an empty label is a valid "no objects" background frame,
        # matching split_dataset.py's own handling)
        img = next((p for p in src_images.glob(f"{lbl_file.stem}.*") if p.suffix.lower() in IMG_EXTS), None)
        if img is not None:
            shutil.copy2(img, out_images / img.name)

    # images with no matching label file at all -- copy through untouched
    labeled_stems = {p.stem for p in src_labels.glob("*.txt")}
    for img in src_images.iterdir():
        if img.suffix.lower() in IMG_EXTS and img.stem not in labeled_stems:
            shutil.copy2(img, out_images / img.name)

    print(f"[fix_mixed_labels] {n_files} label files processed")
    print(f"[fix_mixed_labels] {n_had_polygon_rows} files had at least one non-5-value row")
    print(f"[fix_mixed_labels] {n_rows_converted} polygon rows converted to bboxes")
    print(f"[fix_mixed_labels] {n_rows_unrecoverable} rows unrecoverable (dropped individually, "
          f"not the whole image)")
    print(f"[fix_mixed_labels] {n_images_recovered} images that would have been ENTIRELY "
          f"dropped by ultralytics now have at least one valid box")
    print(f"[fix_mixed_labels] wrote fixed copy to {out}")
    print(f"[fix_mixed_labels] next: re-run count_class_instances.py against a fresh split of "
          f"THIS directory to confirm cyclist's real recovered count before re-splitting/retraining")


if __name__ == "__main__":
    main()
