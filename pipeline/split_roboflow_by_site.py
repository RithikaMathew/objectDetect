"""
Split a Roboflow YOLOv8 export (100% train) into site-held-out train/val.

CorrineDr_* -> val (never train). All other sites -> train.
Matches the journal protocol: split by SITE, not by random frames.

Roboflow 2x augmentation creates two files per source that share a stem
before `.rf.<hash>`. For val we keep ONE copy per stem (val should not be
augmented). For train we keep ALL copies (2x is intentional).

Usage:
    python split_roboflow_by_site.py \\
        --zip vision2.v1-six-class-corrected-v1.yolov8.zip \\
        --out dataset_frames/yolo_sixclass_v1

    # or from an already-extracted folder:
    python split_roboflow_by_site.py \\
        --src dataset_frames/roboflow_raw_v1 \\
        --out dataset_frames/yolo_sixclass_v1
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import zipfile
from collections import Counter, defaultdict

CLASS_NAMES = ["person", "car", "bus", "truck", "cyclist", "other_vehicle"]
VAL_SITE_PREFIXES = ("CorrineDr", "Corrine")

# Roboflow sorts class names alphabetically in the export, which SILENTLY
# renumbers every label. Map RF index -> our canonical index before training.
# RF names: ['bus', 'car', 'cyclist', 'other_vehicle', 'person', 'truck']
ROBOFLOW_TO_CANONICAL = {
    0: 2,  # bus
    1: 1,  # car
    2: 4,  # cyclist
    3: 5,  # other_vehicle
    4: 0,  # person
    5: 3,  # truck
}


def _is_val(filename: str) -> bool:
    return filename.startswith(VAL_SITE_PREFIXES) or "_val_" in filename[:80]


def _aug_stem(filename: str) -> str:
    """Strip Roboflow `.rf.<hash>` so 2x augs of the same source share a key."""
    base = os.path.splitext(filename)[0]
    return re.sub(r"\.rf\.[a-f0-9]+$", "", base, flags=re.I)


def _site_of(filename: str) -> str:
    return filename.split("_")[0]


def _mapping_from_roboflow_yaml(src_root: str) -> dict:
    """Build RF-index -> canonical-index from the export's data.yaml names."""
    yaml_path = os.path.join(src_root, "data.yaml")
    if not os.path.isfile(yaml_path):
        print("WARNING: no data.yaml in export; using hardcoded ROBOFLOW_TO_CANONICAL")
        return dict(ROBOFLOW_TO_CANONICAL)
    text = open(yaml_path).read()
    # names: ['bus', 'car', ...]  or names:\n  0: bus
    rf_names = None
    m = re.search(r"names:\s*\[([^\]]+)\]", text)
    if m:
        rf_names = [x.strip().strip("'\"") for x in m.group(1).split(",")]
    if not rf_names:
        raise SystemExit(f"Could not parse names from {yaml_path}")
    canon = {n: i for i, n in enumerate(CLASS_NAMES)}
    mapping = {}
    for rf_i, name in enumerate(rf_names):
        if name not in canon:
            raise SystemExit(f"Unexpected Roboflow class '{name}' in {yaml_path}")
        mapping[rf_i] = canon[name]
    print("Roboflow class order -> canonical:")
    for rf_i, name in enumerate(rf_names):
        print(f"  RF {rf_i} {name:<14} -> {mapping[rf_i]} {CLASS_NAMES[mapping[rf_i]]}")
    return mapping


def _remap_label_file(src_lbl: str, dest_lbl: str, mapping: dict):
    """Rewrite YOLO label class ids through mapping (Roboflow -> canonical)."""
    lines_out = []
    if os.path.isfile(src_lbl):
        with open(src_lbl) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                old_id = int(parts[0])
                if old_id not in mapping:
                    raise SystemExit(
                        f"Unknown class id {old_id} in {src_lbl} — "
                        f"check Roboflow names vs mapping")
                parts[0] = str(mapping[old_id])
                lines_out.append(" ".join(parts))
    with open(dest_lbl, "w") as f:
        f.write("\n".join(lines_out) + ("\n" if lines_out else ""))


def _copy_pair(src_img, src_lbl, dest_img_dir, dest_lbl_dir, name, mapping):
    os.makedirs(dest_img_dir, exist_ok=True)
    os.makedirs(dest_lbl_dir, exist_ok=True)
    shutil.copy2(src_img, os.path.join(dest_img_dir, name))
    lbl_name = os.path.splitext(name)[0] + ".txt"
    dest_lbl = os.path.join(dest_lbl_dir, lbl_name)
    _remap_label_file(src_lbl, dest_lbl, mapping)


def _count_classes(labels_dir):
    counts = Counter()
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


def split_export(src_root: str, out_root: str, dedupe_val: bool = True):
    train_img = os.path.join(src_root, "train", "images")
    train_lbl = os.path.join(src_root, "train", "labels")
    if not os.path.isdir(train_img):
        raise SystemExit(f"No train/images under {src_root}")

    mapping = _mapping_from_roboflow_yaml(src_root)

    # Fresh output
    if os.path.isdir(out_root):
        shutil.rmtree(out_root)

    out_train_img = os.path.join(out_root, "train", "images")
    out_train_lbl = os.path.join(out_root, "train", "labels")
    out_val_img = os.path.join(out_root, "valid", "images")  # Ultralytics/Roboflow name
    out_val_lbl = os.path.join(out_root, "valid", "labels")
    # Also write val/ alias for convenience
    out_val_img_alias = os.path.join(out_root, "val", "images")
    out_val_lbl_alias = os.path.join(out_root, "val", "labels")

    site_counts = defaultdict(lambda: Counter())
    val_stems_kept = set()
    n_train = n_val = n_val_skipped_aug = 0

    for fname in sorted(os.listdir(train_img)):
        if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        src_i = os.path.join(train_img, fname)
        src_l = os.path.join(train_lbl, os.path.splitext(fname)[0] + ".txt")
        site = _site_of(fname)

        if _is_val(fname):
            stem = _aug_stem(fname)
            if dedupe_val and stem in val_stems_kept:
                n_val_skipped_aug += 1
                continue
            val_stems_kept.add(stem)
            _copy_pair(src_i, src_l, out_val_img, out_val_lbl, fname, mapping)
            _copy_pair(src_i, src_l, out_val_img_alias, out_val_lbl_alias, fname, mapping)
            n_val += 1
            site_counts[site]["val"] += 1
        else:
            _copy_pair(src_i, src_l, out_train_img, out_train_lbl, fname, mapping)
            n_train += 1
            site_counts[site]["train"] += 1

    # data.yaml for Ultralytics — CANONICAL order (not Roboflow alphabetical)
    yaml_path = os.path.join(out_root, "data.yaml")
    names_block = "\n".join(f"  {i}: {n}" for i, n in enumerate(CLASS_NAMES))
    with open(yaml_path, "w") as f:
        f.write(
            f"# Site-held-out split: CorrineDr -> valid; all other sites -> train\n"
            f"# Labels remapped from Roboflow alphabetical order to canonical:\n"
            f"#   {CLASS_NAMES}\n"
            f"# path is relative — run yolo from this directory OR pass absolute data=...\n"
            f"path: .\n"
            f"train: train/images\n"
            f"val: valid/images\n"
            f"nc: {len(CLASS_NAMES)}\n"
            f"names:\n{names_block}\n"
        )

    with open(os.path.join(out_root, "classes.txt"), "w") as f:
        f.write("\n".join(CLASS_NAMES) + "\n")

    print("=== Site-held-out split complete ===")
    print(f"  out:   {out_root}")
    print(f"  train: {n_train} images")
    print(f"  valid: {n_val} images  (skipped {n_val_skipped_aug} extra Roboflow augs on val)")
    print("\n=== Frames by site ===")
    print(f"{'site':<32} {'train':>6} {'val':>6}")
    for site in sorted(site_counts):
        print(f"{site:<32} {site_counts[site]['train']:>6} {site_counts[site]['val']:>6}")

    tr_c = _count_classes(out_train_lbl)
    va_c = _count_classes(out_val_lbl)
    print("\n=== Class instances (train) ===")
    for n in CLASS_NAMES:
        print(f"  {n:<14} {tr_c[n]}")
    print("\n=== Class instances (valid / Corrine) ===")
    for n in CLASS_NAMES:
        print(f"  {n:<14} {va_c[n]}")
    thin = [n for n in ("bus", "truck", "other_vehicle", "cyclist") if va_c[n] < 5]
    if thin:
        print("\nWARNING: thin val support for:", ", ".join(thin))
        print("  Report per-class mAP only where supported.")

    print(f"\nWrote {yaml_path}")
    print("Next: sbatch train_yolov8_finetune.slurm")
    return yaml_path


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--zip", default=None, help="Roboflow YOLOv8 zip path")
    ap.add_argument("--src", default=None,
                    help="Already-extracted export dir (with train/images)")
    ap.add_argument("--out", default="dataset_frames/yolo_sixclass_v1")
    ap.add_argument("--keep-val-augs", action="store_true",
                    help="Keep all 2x Roboflow augs in val (default: dedupe val stems)")
    args = ap.parse_args()

    if args.zip:
        extract_dir = args.src or (os.path.splitext(args.zip)[0] + "_extracted")
        if os.path.isdir(extract_dir):
            shutil.rmtree(extract_dir)
        os.makedirs(extract_dir, exist_ok=True)
        print(f"Extracting {args.zip} -> {extract_dir}")
        with zipfile.ZipFile(args.zip) as zf:
            zf.extractall(extract_dir)
        src = extract_dir
    elif args.src:
        src = args.src
    else:
        raise SystemExit("Pass --zip or --src")

    split_export(src, args.out, dedupe_val=not args.keep_val_augs)


if __name__ == "__main__":
    main()
