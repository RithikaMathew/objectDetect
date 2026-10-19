"""
Assemble the journal annotation pool from Colonial track mine + multi-site build.

Merges:
  A. dataset_frames/colonial_track   (150 track hard cases, train)
  B/C. dataset_frames/split/train    (120 uniform + 180 detection-guided)
  D. dataset_frames/split/val        (100 Corrine uniform)

Writes:
  <out>/images, labels, previews, classes.txt
  <out>/pool_manifest.csv   (source_video, timestamp, frame_number, site,
                             sampling_method, split, path)
  <out>/train/ and <out>/val/  (site-strict copies after optional --finalize)
  site × method × class histograms for the methods section
  optional CVAT zip

Dedup key: (source_video, frame_number). First occurrence wins.

Usage:
    python assemble_annotation_pool.py \\
        --colonial-dir dataset_frames/colonial_track \\
        --build-dir dataset_frames/split \\
        --out dataset_frames/annotation_pool \\
        --zip

After CVAT export of corrected labels into the pool labels/, re-run with
--finalize to rebuild train/val by site (Corrine -> val; all else -> train).
"""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import zipfile
from collections import Counter, defaultdict

from extract_frames import CLASS_NAMES

REQUIRED = [
    "path", "source_video", "timestamp", "frame_number",
    "site", "sampling_method", "split",
]

CORRINE_SITE_TOKENS = ("corrine",)


def _is_corrine(site: str) -> bool:
    s = (site or "").lower()
    return any(tok in s for tok in CORRINE_SITE_TOKENS)


def _read_manifest(path):
    if not os.path.isfile(path):
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _label_class_counts(label_path):
    counts = Counter()
    if not os.path.isfile(label_path):
        return counts
    with open(label_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            cls_id = int(line.split()[0])
            if 0 <= cls_id < len(CLASS_NAMES):
                counts[CLASS_NAMES[cls_id]] += 1
    return counts


def _copy_triplet(src_img, dest_images, dest_labels, dest_previews, dest_name):
    """Copy image + matching label (+ preview if present) under dest_name."""
    base = os.path.splitext(os.path.basename(src_img))[0]
    img_dir = os.path.dirname(src_img)
    # Standard layout: <root>/{images,labels,previews}/
    if os.path.basename(img_dir) == "images":
        root = os.path.dirname(img_dir)
        label_src = os.path.join(root, "labels", base + ".txt")
        preview_src = os.path.join(root, "previews", base + ".jpg")
    else:
        label_src = os.path.join(img_dir, base + ".txt")
        preview_src = os.path.join(img_dir, base + "_preview.jpg")

    os.makedirs(dest_images, exist_ok=True)
    os.makedirs(dest_labels, exist_ok=True)
    os.makedirs(dest_previews, exist_ok=True)

    dest_img = os.path.join(dest_images, dest_name + ".jpg")
    dest_lbl = os.path.join(dest_labels, dest_name + ".txt")
    shutil.copy2(src_img, dest_img)
    if os.path.isfile(label_src):
        shutil.copy2(label_src, dest_lbl)
    else:
        open(dest_lbl, "w").close()
    if os.path.isfile(preview_src):
        shutil.copy2(preview_src, os.path.join(dest_previews, dest_name + ".jpg"))
    return dest_img, dest_lbl


def _unique_dest_name(site, sampling_method, frame_number, base_hint, used):
    raw = f"{site}_{sampling_method}_f{frame_number}_{base_hint}"
    # sanitize
    name = "".join(c if c.isalnum() or c in "-_" else "_" for c in raw)
    if name not in used:
        used.add(name)
        return name
    i = 2
    while f"{name}_{i}" in used:
        i += 1
    name_i = f"{name}_{i}"
    used.add(name_i)
    return name_i


def assemble(colonial_dir, build_dir, out_dir, do_zip=False, finalize=False):
    os.makedirs(out_dir, exist_ok=True)
    images_dir = os.path.join(out_dir, "images")
    labels_dir = os.path.join(out_dir, "labels")
    previews_dir = os.path.join(out_dir, "previews")
    for d in (images_dir, labels_dir, previews_dir):
        os.makedirs(d, exist_ok=True)

    with open(os.path.join(out_dir, "classes.txt"), "w") as f:
        f.write("\n".join(CLASS_NAMES) + "\n")

    sources = []
    col_manifest = os.path.join(colonial_dir, "pool_manifest.csv")
    # legacy name from earlier mining runs
    if not os.path.isfile(col_manifest):
        col_manifest = os.path.join(colonial_dir, "mining_manifest.csv")
    sources.append(("colonial", colonial_dir, _read_manifest(col_manifest)))

    build_manifest = os.path.join(build_dir, "pool_manifest.csv")
    sources.append(("build", build_dir, _read_manifest(build_manifest)))

    # If colonial manifest is empty/missing, invent rows from images/
    for tag, root, rows in list(sources):
        if rows:
            continue
        img_root = os.path.join(root, "images")
        if not os.path.isdir(img_root):
            # build uses train/images and val/images
            continue
        print(f"WARNING: no manifest under {root}; scanning images/ "
              f"(missing source_video/timestamp — re-run mining/build)")
        invented = []
        for fname in sorted(os.listdir(img_root)):
            if not fname.endswith(".jpg"):
                continue
            invented.append({
                "path": os.path.join(img_root, fname),
                "source_video": "",
                "timestamp": "",
                "frame_number": "",
                "site": "UNKNOWN",
                "sampling_method": "unknown",
                "split": "train",
            })
        sources.append((tag + "_scan", root, invented))

    # Also pull build train/val images via their manifests; if build manifest
    # lists paths, use those. If missing, scan train/ and val/.
    build_rows = sources[1][2]
    if not build_rows and os.path.isdir(build_dir):
        invented = []
        for split, method in (("train", "uniform"), ("val", "val_uniform")):
            img_root = os.path.join(build_dir, split, "images")
            if not os.path.isdir(img_root):
                continue
            for fname in sorted(os.listdir(img_root)):
                if not fname.endswith(".jpg"):
                    continue
                # Infer sampling from filename tag if present
                sm = "detection_guided" if "_mined_" in fname else (
                    "val_detection_guided" if "_vmined_" in fname else (
                    "val_uniform" if split == "val" else "uniform"))
                # site is the prefix before first year-like token — best effort
                site = fname.split("_")[0]
                invented.append({
                    "path": os.path.join(img_root, fname),
                    "source_video": "",
                    "timestamp": "",
                    "frame_number": "",
                    "site": site,
                    "sampling_method": sm,
                    "split": split,
                })
        sources[1] = ("build_scan", build_dir, invented)

    seen = set()
    out_rows = []
    used_names = set()
    skipped_dup = 0
    site_method = Counter()
    class_by_site = defaultdict(Counter)
    class_by_method = defaultdict(Counter)
    split_counts = Counter()

    for tag, root, rows in sources:
        for row in rows:
            src_video = (row.get("source_video") or "").strip()
            frame_s = (row.get("frame_number") or "").strip()
            if src_video and frame_s != "":
                key = (os.path.abspath(src_video), int(float(frame_s)))
                if key in seen:
                    skipped_dup += 1
                    continue
                seen.add(key)

            src_img = row.get("path") or ""
            if not src_img or not os.path.isfile(src_img):
                # try resolve relative to root/images
                base = os.path.basename(src_img) if src_img else ""
                alt = os.path.join(root, "images", base) if base else ""
                if not os.path.isfile(alt):
                    print(f"  missing image, skip: {src_img}")
                    continue
                src_img = alt

            site = row.get("site") or "UNKNOWN"
            method = row.get("sampling_method") or "unknown"
            split = row.get("split") or ("val" if _is_corrine(site) else "train")
            # Enforce site-strict split: Corrine always val
            if _is_corrine(site):
                split = "val"
            elif split not in ("train", "val"):
                split = "train"

            base_hint = os.path.splitext(os.path.basename(src_img))[0]
            frame_number = row.get("frame_number") or "0"
            dest_name = _unique_dest_name(site, method, frame_number, base_hint, used_names)
            dest_img, dest_lbl = _copy_triplet(
                src_img, images_dir, labels_dir, previews_dir, dest_name)

            out_row = {
                "path": dest_img,
                "source_video": src_video,
                "timestamp": row.get("timestamp", ""),
                "frame_number": frame_number,
                "site": site,
                "sampling_method": method,
                "split": split,
            }
            out_rows.append(out_row)
            site_method[(site, method)] += 1
            split_counts[split] += 1
            for cls_name, n in _label_class_counts(dest_lbl).items():
                class_by_site[site][cls_name] += n
                class_by_method[method][cls_name] += n

    manifest_path = os.path.join(out_dir, "pool_manifest.csv")
    with open(manifest_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=REQUIRED)
        w.writeheader()
        w.writerows(out_rows)

    print("=== Annotation pool assembled ===")
    print(f"  frames: {len(out_rows)}  (skipped duplicates: {skipped_dup})")
    print(f"  train:  {split_counts['train']}   val: {split_counts['val']}")
    print(f"  manifest: {manifest_path}")
    print(f"  classes: {', '.join(CLASS_NAMES)}")

    print("\n=== Site × sampling_method frame counts ===")
    print(f"{'site':<24} {'method':<20} {'n':>5}")
    for (site, method), n in sorted(site_method.items()):
        print(f"{site:<24} {method:<20} {n:>5}")

    print("\n=== Class instances by site (pre-labels) ===")
    print(f"{'site':<24} " + " ".join(f"{c[:6]:>6}" for c in CLASS_NAMES))
    for site in sorted(class_by_site):
        counts = class_by_site[site]
        print(f"{site:<24} " + " ".join(
            f"{counts.get(c, 0):>6}" for c in CLASS_NAMES))

    print("\n=== Class instances by sampling_method ===")
    for method in sorted(class_by_method):
        counts = class_by_method[method]
        parts = ", ".join(f"{c}={counts.get(c, 0)}" for c in CLASS_NAMES)
        print(f"  {method}: {parts}")

    # Corrine rare-class note
    corrine_sites = [s for s in class_by_site if _is_corrine(s)]
    if corrine_sites:
        print("\n=== Corrine val rare-class coverage ===")
        agg = Counter()
        for s in corrine_sites:
            agg.update(class_by_site[s])
        for c in ("bus", "truck", "other_vehicle", "cyclist", "person", "car"):
            print(f"  {c:<14} {agg.get(c, 0)}")
        thin = [c for c in ("bus", "truck", "other_vehicle") if agg.get(c, 0) < 5]
        if thin:
            print("  WARNING: thin val coverage for", ", ".join(thin))
            print("  Report per-class mAP only where supported, or densify Corrine")
            print("  sampling — never move Corrine into train.")

    if finalize:
        _finalize_splits(out_dir, out_rows)

    if do_zip:
        zip_path = os.path.join(out_dir, "for_cvat.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for sub in ("images", "labels"):
                d = os.path.join(out_dir, sub)
                for fname in os.listdir(d):
                    zf.write(os.path.join(d, fname), arcname=f"{sub}/{fname}")
            zf.write(os.path.join(out_dir, "classes.txt"), arcname="classes.txt")
        print(f"\nCVAT zip: {zip_path}")

    print("\nAnnotation rules reminder:")
    print("  - Label EVERY relevant object of the six classes in every frame")
    print("  - Keep empty frames (hard negatives)")
    print("  - Untouched counting sites: Edgewater, Pine Hills NBL, Aloma Path")
    return manifest_path


def _finalize_splits(out_dir, rows):
    """Copy pool images/labels into train/ and val/ by site (Corrine -> val)."""
    for split in ("train", "val"):
        for sub in ("images", "labels", "previews"):
            d = os.path.join(out_dir, split, sub)
            if os.path.isdir(d):
                shutil.rmtree(d)
            os.makedirs(d, exist_ok=True)
        with open(os.path.join(out_dir, split, "classes.txt"), "w") as f:
            f.write("\n".join(CLASS_NAMES) + "\n")

    n = {"train": 0, "val": 0}
    for row in rows:
        split = row["split"]
        src = row["path"]
        base = os.path.splitext(os.path.basename(src))[0]
        lbl = os.path.join(out_dir, "labels", base + ".txt")
        prev = os.path.join(out_dir, "previews", base + ".jpg")
        shutil.copy2(src, os.path.join(out_dir, split, "images", base + ".jpg"))
        if os.path.isfile(lbl):
            shutil.copy2(lbl, os.path.join(out_dir, split, "labels", base + ".txt"))
        if os.path.isfile(prev):
            shutil.copy2(prev, os.path.join(out_dir, split, "previews", base + ".jpg"))
        n[split] += 1
    print(f"\nFinalized site-strict splits: train={n['train']}  val={n['val']}")
    print(f"  {out_dir}/train/  {out_dir}/val/")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--colonial-dir", default="dataset_frames/colonial_track")
    ap.add_argument("--build-dir", default="dataset_frames/split")
    ap.add_argument("--out", default="dataset_frames/annotation_pool")
    ap.add_argument("--zip", action="store_true", help="Write for_cvat.zip")
    ap.add_argument("--finalize", action="store_true",
                    help="Also write train/ and val/ by site membership")
    args = ap.parse_args()
    assemble(args.colonial_dir, args.build_dir, args.out,
             do_zip=args.zip, finalize=args.finalize)


if __name__ == "__main__":
    main()
