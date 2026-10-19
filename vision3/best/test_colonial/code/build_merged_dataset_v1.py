#!/usr/bin/env python3
"""build_merged_dataset_v1.py

Merge the existing rtdetr_v3 training set with one or more extra YOLO-format datasets (NightOwls export, hand-labelled Colonial night frames, ...)
into a NEW folder + data.yaml. Nothing in the source datasets is modified (images are symlinked, labels are rewritten).

 * Class ids come from the base data.yaml. Extra class NAMES are matched to base names (exact match), or via --map extra=base. Names listed in --drop are
   removed. Any other unmatched name stops the script with an error (no silent guessing).
 * Extra images only go into TRAIN (plus an optional --val-frac share into an extra VAL set). The base val set stays as it is.
 * Base training images are repeated --base-repeat times so a large extra set does not swamp the ~270 base images.
 * Extra labels must be YOLO boxes (5 numbers per line); polygon labels stop the script.
"""
import argparse, os, random, shutil, sys
from collections import Counter
from pathlib import Path
import yaml

IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def die(msg):
    sys.exit("ERROR: " + msg)


def load_cfg(p):
    p = Path(p).resolve()
    if not p.is_file():
        die(f"missing yaml: {p}")
    return p, yaml.safe_load(open(p))


def names_of(cfg, where):
    n = cfg.get("names")
    if n is None:
        die(f"no 'names' in {where}")
    if isinstance(n, dict):
        return {int(k): str(v) for k, v in n.items()}
    return {i: str(v) for i, v in enumerate(n)}


def entry_dirs(cfg_path, cfg, key):
    root = Path(cfg.get("path") or cfg_path.parent)
    if not root.is_absolute():
        root = (cfg_path.parent / root).resolve()
    e = cfg.get(key)
    if e is None:
        die(f"'{key}' missing in {cfg_path}")
    out = []
    for x in (e if isinstance(e, list) else [e]):
        p = Path(x)
        p = (p if p.is_absolute() else root / p).resolve()
        if not p.is_dir():
            die(f"{key} entry is not a directory: {p}")
        out.append(p)
    return out


def label_dir_for(img_dir):
    parts = list(img_dir.parts)
    for i in range(len(parts) - 1, -1, -1):
        if parts[i] == "images":
            lab = Path(*parts[:i], "labels", *parts[i + 1:])
            if not lab.is_dir():
                die(f"labels folder not found for {img_dir}: expected {lab}")
            return lab
    die(f"no 'images' folder in path, cannot find labels for {img_dir}")


def list_pairs(img_dir, lab_dir):
    pairs = []
    for im in sorted(img_dir.rglob("*")):
        if im.suffix.lower() in IMG_EXT:
            pairs.append((im, lab_dir / im.relative_to(img_dir).with_suffix(".txt")))
    return pairs


def read_boxes(lab, where):
    if not lab.is_file():
        return None  # no label file
    rows = []
    for ln, line in enumerate(open(lab).read().splitlines(), 1):
        if not line.strip():
            continue
        t = line.split()
        if len(t) != 5:
            die(f"{lab}:{ln} has {len(t)} fields, expected 5 (YOLO box). Polygon/segmentation labels are not handled.")
        rows.append((int(float(t[0])), t[1:]))
    return rows


def link(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        dst.unlink()
    os.symlink(str(src.resolve()), str(dst))


def write_label(dst, rows):
    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(dst, "w") as f:
        for c, box in rows:
            f.write(f"{c} {' '.join(box)}\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base-yaml", required=True)
    ap.add_argument("--extra", action="append", required=True, help="YOLO-format dataset folder containing data.yaml (repeatable)")
    ap.add_argument("--out", required=True, help="NEW output folder (must not exist)")
    ap.add_argument("--map", action="append", default=[], help="extra_name=base_name (repeatable), e.g. pedestrian=person")
    ap.add_argument("--drop", action="append", default=[], help="extra class name to remove (repeatable)")
    ap.add_argument("--max-extra", type=int, default=400, help="max images taken per extra folder (random, seeded)")
    ap.add_argument("--val-frac", type=float, default=0.0, help="share of each extra folder put into an extra val set (keep 0 for NightOwls: its cars are unlabelled and would count as false positives)")
    ap.add_argument("--base-repeat", type=int, default=3)
    ap.add_argument("--keep-empty", action="store_true", help="keep extra images that end up with zero boxes")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()

    out = Path(a.out).resolve()
    if out.exists():
        die(f"{out} already exists; choose a new --out (nothing is overwritten)")
    rng = random.Random(a.seed)

    bpath, bcfg = load_cfg(a.base_yaml)
    bnames = names_of(bcfg, bpath)
    name2id = {v: k for k, v in bnames.items()}
    print("base classes:", bnames)
    mapping = {}
    for m in a.map:
        if "=" not in m:
            die(f"--map needs extra=base, got {m}")
        k, v = m.split("=", 1)
        if v not in name2id:
            die(f"--map target '{v}' is not a base class {sorted(name2id)}")
        mapping[k] = v
    drop = set(a.drop)

    # base train + val
    btrain = entry_dirs(bpath, bcfg, "train")
    bval = entry_dirs(bpath, bcfg, "val")
    n_base = 0
    box_count = Counter()
    for d in btrain:
        lab_dir = label_dir_for(d)
        for im, lab in list_pairs(d, lab_dir):
            rows = read_boxes(lab, "base") or []
            for r in range(a.base_repeat):
                stem = f"{im.stem}__b{r}"
                link(im, out / "images" / "train_base" / f"{d.name}_{stem}{im.suffix}")
                write_label(out / "labels" / "train_base" / f"{d.name}_{stem}.txt", rows)
            n_base += 1
            for c, _ in rows:
                box_count[bnames.get(c, c)] += a.base_repeat
    print(f"base train: {n_base} images x{a.base_repeat}")

    extra_train_dirs, extra_val_dirs = [], []
    for ex in a.extra:
        exd = Path(ex).resolve()
        ecfg_path, ecfg = load_cfg(exd / "data.yaml")
        enames = names_of(ecfg, ecfg_path)
        print(f"extra {exd.name} classes:", enames)
        cls_to_base = {}
        for cid, nm in enames.items():
            if nm in drop:
                cls_to_base[cid] = None
                continue
            tgt = mapping.get(nm, nm)
            if tgt not in name2id:
                die(f"extra class '{nm}' ({exd.name}) has no base class. Use --map {nm}=<base class> or --drop {nm}. Base classes: {sorted(name2id)}")
            cls_to_base[cid] = name2id[tgt]
        pairs = []
        for imgs in sorted(p for p in exd.rglob("images") if p.is_dir()):
            lab_dir = imgs.parent / "labels"
            if lab_dir.is_dir():
                pairs += list_pairs(imgs, lab_dir)
        if not pairs:
            die(f"no images/labels pairs found under {exd}")
        rng.shuffle(pairs)
        kept = []
        for im, lab in pairs:
            rows = read_boxes(lab, exd.name)
            if rows is None:
                rows = []
            new = []
            for c, box in rows:
                if c not in cls_to_base:
                    die(f"{lab}: class id {c} not in {exd.name}/data.yaml")
                if cls_to_base[c] is not None:
                    new.append((cls_to_base[c], box))
            if new or a.keep_empty:
                kept.append((im, new))
            if len(kept) >= a.max_extra:
                break
        n_val = int(round(len(kept) * a.val_frac))
        for i, (im, rows) in enumerate(kept):
            part = "val_extra" if i < n_val else "train_extra"
            stem = f"{exd.name}_{im.stem}"
            link(im, out / "images" / part / f"{stem}{im.suffix}")
            write_label(out / "labels" / part / f"{stem}.txt", rows)
            if part == "train_extra":
                for c, _ in rows:
                    box_count[bnames[c]] += 1
        print(f"extra {exd.name}: {len(kept)} images kept ({n_val} to val_extra) of {len(pairs)} scanned")

    train = [str(out / "images" / "train_base")]
    val = [str(p) for p in bval]
    if (out / "images" / "train_extra").is_dir():
        train.append(str(out / "images" / "train_extra"))
    if (out / "images" / "val_extra").is_dir():
        val.append(str(out / "images" / "val_extra"))
    data = {"path": str(out), "train": train, "val": val, "nc": len(bnames), "names": {k: bnames[k] for k in sorted(bnames)}}
    with open(out / "data.yaml", "w") as f:
        yaml.safe_dump(data, f, sort_keys=False)
    print("train boxes per class (after repeat):", dict(box_count))
    print("wrote", out / "data.yaml")


if __name__ == "__main__":
    main()
