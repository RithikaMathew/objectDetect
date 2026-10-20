#!/usr/bin/env python3
"""
split_dataset.py

Splits the flat Roboflow YOLO export (currently all 270 images lumped into
one `train/` split, per README) into proper train/val/test sets for
fine-tuning.

ASSUMPTIONS (check these against your actual export before running --
print a listing of the source dir first if unsure):
  - Source layout is the standard Roboflow YOLOv8 export:
        <src>/train/images/*.jpg (or .png)
        <src>/train/labels/*.txt
        <src>/data.yaml            (optional; if present, its `nc` and
                                     `names` are carried over unchanged)
  - Every image has a matching label file with the same stem. Images with
    no matching label are treated as background/negative frames and are
    still split and copied (not dropped) -- if that's wrong for your case,
    say so and I'll change it to drop or warn instead.

WHAT IT DOES
  - Reads all image/label stems from <src>/train/.
  - Shuffles with a fixed seed (reproducible -- same split every re-run
    unless you pass --seed).
  - Splits into train/val/test by --ratios (default 80/10/10). With only
    270 images that's ~216/27/27 -- small val/test sets, but enough to
    catch gross overfitting; revisit if results look noisy.
  - COPIES (not symlinks, since /orange is a shared filesystem and you may
    want to hand the split off independent of the source export existing)
    files into <out>/{train,val,test}/{images,labels}/.
  - Writes <out>/data.yaml pointing at the new split, preserving class
    names from the source data.yaml if found, else defaulting to a single
    `cyclist` class (0) -- CHECK THIS: if your Roboflow project actually
    has separate person/bicycle classes rather than one fused `cyclist`
    class, the fallback below is wrong for you and you should tell me.

USAGE
    python split_dataset.py \
        --src /orange/xiangyan/rithika/vision/dataset_frames/roboflow_raw_v1 \
        --out /orange/xiangyan/rithika/vision/dataset_frames/roboflow_split_v1 \
        --ratios 0.8 0.1 0.1 \
        --seed 42
"""
import argparse
import random
import shutil
import sys
from collections import Counter
from pathlib import Path

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}


def find_stems(images_dir: Path):
    stems = sorted(p.stem for p in images_dir.iterdir() if p.suffix.lower() in IMG_EXTS)
    return stems


def load_source_yaml_classes(src: Path):
    """Best-effort read of nc/names from an existing data.yaml. Falls back
    to a single 'cyclist' class if not found or unparseable -- printed
    loudly either way so it's never a silent guess."""
    yaml_path = src / "data.yaml"
    if not yaml_path.exists():
        print(f"[split_dataset] no data.yaml found at {yaml_path} -- "
              f"defaulting to a single class: 0='cyclist'. If your "
              f"annotations actually use different/multiple classes, "
              f"stop and fix this before fine-tuning on it.", flush=True)
        return 1, ["cyclist"]

    try:
        import yaml
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        names = data.get("names")
        if isinstance(names, dict):
            names = [names[k] for k in sorted(names, key=lambda x: int(x))]
        nc = data.get("nc", len(names) if names else 1)
        if not names:
            raise ValueError("no 'names' key found")
        print(f"[split_dataset] read classes from {yaml_path}: nc={nc} names={names}",
              flush=True)
        return nc, names
    except Exception as e:
        print(f"[split_dataset] FAILED to parse {yaml_path} ({e}) -- "
              f"defaulting to a single class: 0='cyclist'. Fix data.yaml "
              f"or pass classes manually if this default is wrong.",
              flush=True)
        return 1, ["cyclist"]


def group_key(stem: str) -> str:
    """Roboflow names duplicate/augmented copies of the same source frame
    as <original>_jpg.rf.<hash> -- confirmed via `ls` that every frame in
    this export appears exactly twice this way, hash differing, everything
    else identical. Group by the part before '.rf.' so all copies of one
    frame move together as a single split-atomic unit and never end up
    split across train/val/test (which would leak near-duplicate images
    across the split boundary)."""
    if ".rf." in stem:
        return stem.split(".rf.")[0]
    return stem  # no .rf. suffix -- not a Roboflow-style duplicate, its own group


def load_classes_per_image(labels_dir: Path, stems):
    """Returns {stem: set(class_ids present)}, parsing only well-formed
    5-value rows (this script assumes fix_mixed_labels.py has already run
    if the source had segmentation/detection mixing -- a malformed row
    here is just skipped for class-membership purposes, matching what
    ultralytics itself would eventually see)."""
    classes_per_image = {}
    for stem in stems:
        lbl = labels_dir / f"{stem}.txt"
        classes = set()
        if lbl.exists():
            for line in lbl.read_text().splitlines():
                parts = line.split()
                if len(parts) == 5:
                    try:
                        classes.add(int(parts[0]))
                    except ValueError:
                        pass
        classes_per_image[stem] = classes
    return classes_per_image


def stratified_split(groups, group_classes, class_counts, ratios, rng, rare_threshold):
    """Splits GROUPS (each a list of stems that are duplicate/augmented
    copies of the same source frame -- see group_key()) into train/val/
    test, atomically: every stem in a group goes to the same split. Also
    guarantees rare classes (total instance count < rare_threshold) get
    representation in every split, proportional to the split ratios --
    instead of one plain random shuffle, which for an 18-instance class
    can (and did, in practice) put zero examples into val by chance.

    Approach: groups containing >=1 rare-class instance are split as their
    own pool first (so a rare class's frames are spread across train/val/
    test using the SAME ratios as everything else); the remaining "common"
    groups are split as a second pool. The two pools' splits are then
    merged. This doesn't guarantee a non-empty val/test for a class with
    fewer distinct FRAMES than there are splits (impossible to guarantee
    with, say, 2 frames and 3-way split) -- the printed report below makes
    any remaining gap visible instead of silent.
    """
    rare_class_ids = {cid for cid, count in class_counts.items() if count < rare_threshold}

    group_ids = list(groups.keys())
    rare_groups = [g for g in group_ids if group_classes[g] & rare_class_ids]
    common_groups = [g for g in group_ids if g not in set(rare_groups)]

    def split_pool(pool_group_ids, local_rng):
        local_rng.shuffle(pool_group_ids)
        n = len(pool_group_ids)
        n_train = round(n * ratios[0])
        n_val = round(n * ratios[1])
        return {
            "train": pool_group_ids[:n_train],
            "val": pool_group_ids[n_train:n_train + n_val],
            "test": pool_group_ids[n_train + n_val:],
        }

    rare_split_groups = split_pool(list(rare_groups), rng)
    common_split_groups = split_pool(list(common_groups), rng)

    merged_groups = {
        split: rare_split_groups[split] + common_split_groups[split]
        for split in ("train", "val", "test")
    }
    # Flatten groups back to individual stems for the copy step
    merged_stems = {
        split: [stem for g in merged_groups[split] for stem in groups[g]]
        for split in ("train", "val", "test")
    }

    if rare_class_ids:
        print(f"[split_dataset] rare classes (< {rare_threshold} total instances): "
              f"{sorted(rare_class_ids)} -- {len(rare_groups)} distinct frames (groups) "
              f"contain at least one", flush=True)
        for split in ("train", "val", "test"):
            split_classes = set()
            for g in merged_groups[split]:
                split_classes |= group_classes[g]
            missing = rare_class_ids - split_classes
            if missing:
                print(f"[split_dataset] WARNING: {split} split still has ZERO instances of "
                      f"class id(s) {sorted(missing)} -- not enough distinct frames containing "
                      f"that class exist to guarantee representation in every split. Consider "
                      f"annotating more examples of that class.", flush=True)
            else:
                print(f"[split_dataset] {split}: all rare classes represented", flush=True)

    return merged_stems


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True,
                     help="Roboflow export root, containing train/images + train/labels")
    ap.add_argument("--out", required=True,
                     help="Output root for the split dataset (created if missing)")
    ap.add_argument("--ratios", type=float, nargs=3, default=[0.8, 0.1, 0.1],
                     metavar=("TRAIN", "VAL", "TEST"),
                     help="Split ratios, must sum to 1.0 (default: 0.8 0.1 0.1)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--rare-threshold", type=int, default=50,
                     help="Classes with fewer than this many total instances get "
                          "stratified representation across splits instead of relying "
                          "on plain random chance (default: 50)")
    args = ap.parse_args()

    if abs(sum(args.ratios) - 1.0) > 1e-6:
        sys.exit(f"ERROR: --ratios must sum to 1.0, got {args.ratios} (sum={sum(args.ratios)})")

    src = Path(args.src)
    out = Path(args.out)
    src_images = src / "train" / "images"
    src_labels = src / "train" / "labels"

    if not src_images.is_dir() or not src_labels.is_dir():
        sys.exit(f"ERROR: expected {src_images} and {src_labels} to exist. "
                  f"Run `ls {src}` yourself and check the actual layout if "
                  f"this doesn't match your Roboflow export -- the assumed "
                  f"layout is documented at the top of this script.")

    nc, names = load_source_yaml_classes(src)

    stems = find_stems(src_images)
    if not stems:
        sys.exit(f"ERROR: no images found in {src_images} (checked extensions: {IMG_EXTS})")

    n_no_label = sum(1 for s in stems if not (src_labels / f"{s}.txt").exists())
    if n_no_label:
        print(f"[split_dataset] WARNING: {n_no_label}/{len(stems)} images have no "
              f"matching .txt label file -- treated as background frames and "
              f"still copied into the split. Tell me if these should be dropped instead.",
              flush=True)

    rng = random.Random(args.seed)

    classes_per_image = load_classes_per_image(src_labels, stems)
    class_counts = Counter()
    for classes in classes_per_image.values():
        class_counts.update(classes)
    print(f"[split_dataset] instance counts across all {len(stems)} images: "
          f"{ {names[c] if c < len(names) else c: n for c, n in sorted(class_counts.items())} }",
          flush=True)

    groups = {}
    for stem in stems:
        groups.setdefault(group_key(stem), []).append(stem)
    n_dupe_groups = sum(1 for members in groups.values() if len(members) > 1)
    print(f"[split_dataset] {len(stems)} images grouped into {len(groups)} distinct frames "
          f"({n_dupe_groups} frames have >1 copy -- these are kept together in the same "
          f"split so duplicates/augmentations never leak across train/val/test)", flush=True)

    group_classes = {
        g: set().union(*(classes_per_image[s] for s in members))
        for g, members in groups.items()
    }

    splits = stratified_split(groups, group_classes, class_counts, args.ratios,
                               rng, args.rare_threshold)

    print(f"[split_dataset] {len(stems)} total images -> "
          f"train={len(splits['train'])} val={len(splits['val'])} test={len(splits['test'])}",
          flush=True)

    for split_name, split_stems in splits.items():
        img_out = out / split_name / "images"
        lbl_out = out / split_name / "labels"
        img_out.mkdir(parents=True, exist_ok=True)
        lbl_out.mkdir(parents=True, exist_ok=True)

        for stem in split_stems:
            src_img = next((p for p in src_images.glob(f"{stem}.*") if p.suffix.lower() in IMG_EXTS), None)
            if src_img is None:
                print(f"[split_dataset] WARNING: image for stem '{stem}' disappeared "
                      f"between listing and copying -- skipping", flush=True)
                continue
            shutil.copy2(src_img, img_out / src_img.name)

            src_lbl = src_labels / f"{stem}.txt"
            if src_lbl.exists():
                shutil.copy2(src_lbl, lbl_out / src_lbl.name)
            else:
                # Empty label file = valid "no objects in this frame" for
                # YOLO-format training; write one so the split is complete.
                (lbl_out / f"{stem}.txt").touch()

    yaml_out = out / "data.yaml"
    with open(yaml_out, "w") as f:
        f.write(f"path: {out.resolve()}\n")
        f.write("train: train/images\n")
        f.write("val: val/images\n")
        f.write("test: test/images\n")
        f.write(f"nc: {nc}\n")
        f.write(f"names: {names}\n")

    print(f"[split_dataset] done. Wrote split dataset + {yaml_out}", flush=True)
    print(f"[split_dataset] sanity check before fine-tuning: "
          f"`cat {yaml_out}` and spot-check a few images/labels in "
          f"{out}/val/ to confirm boxes look right.", flush=True)


if __name__ == "__main__":
    main()