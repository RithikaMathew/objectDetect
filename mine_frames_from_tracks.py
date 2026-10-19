"""
Mine annotation frames from the pipeline's own cyclist tracks.

WHY THIS, RATHER THAN UNIFORM SAMPLING
--------------------------------------
Cyclists are ~0.001% of frames. Sampling uniformly across 48 hours spends
essentially the whole annotation budget on empty road.

A full-session run produces every place the detector saw something
cyclist-like: BL Colonial gave 88 confirmed and 821 rejected cyclist-class
tracks. Those 909 are a curated pool of hard cases. The rejected ones are
the most valuable: by construction, exactly the cases the current model
handles badly.

JOURNAL RECIPE (bucket A)
-------------------------
Cap at --max-frames 150 (default), --per-track 2, stratified across
counted + rejected tracks so grass FPs survive. Writes the full
reproducibility manifest fields used by assemble_annotation_pool.py.

Pre-labels come from re-running the detector (6-class remap in
extract_frames.process_frame_detections). Tracks CSV has no boxes.

Usage:
    python mine_frames_from_tracks.py \\
        --session-dir pilot_output/sessions/BL_Colonial_2019-07-10 \\
        --video-dir "pilot_clips/MioVision Data/.../Standard_SCU8OG_2019-07-10_0000" \\
        --out dataset_frames/colonial_track \\
        --site BL-Colonial \\
        --max-frames 150 --per-track 2
"""

import argparse
import csv
import glob
import os
import random
import sys

import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_frames import (CLASS_NAMES, COCO_QUERY_CLASSES,
                            process_frame_detections, write_frame_outputs)
from ultralytics import YOLO

CYCLIST_CLASSES = ("cyclist", "bicycle")
MANIFEST_FIELDS = [
    "path", "source_video", "timestamp", "frame_number", "site",
    "sampling_method", "split",
    # Extra provenance (kept alongside the required fields)
    "track_id", "counted", "cls", "hits", "max_conf", "mean_conf", "excursion",
]


def _stratified_subsample(targets, max_frames, seed=0):
    """Keep up to max_frames, preserving counted/rejected mix when possible."""
    if max_frames <= 0 or len(targets) <= max_frames:
        return targets
    rng = random.Random(seed)
    counted = [t for t in targets if t["counted"] == "yes"]
    rejected = [t for t in targets if t["counted"] != "yes"]
    # Aim for ~40% confirmed / 60% rejected (rejected = higher-value hard cases)
    n_c = min(len(counted), max(1, int(round(max_frames * 0.40))))
    n_r = min(len(rejected), max_frames - n_c)
    # If rejected pool is short, fill from counted
    if n_c + n_r < max_frames:
        n_c = min(len(counted), max_frames - n_r)
    picked = rng.sample(counted, n_c) if n_c else []
    picked += rng.sample(rejected, n_r) if n_r else []
    # Stable order by chunk then time for reproducible extraction
    picked.sort(key=lambda t: (t["chunk"], t["t"], t["track_id"]))
    return picked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session-dir", required=True)
    ap.add_argument("--video-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--site", default="BL-Colonial",
                    help="Site label written to the manifest (default BL-Colonial).")
    ap.add_argument("--split", default="train",
                    help="Split label for the manifest (Colonial track frames are train).")
    ap.add_argument("--per-track", type=int, default=2,
                    help="Frames sampled per track, spread across its span (default 2).")
    ap.add_argument("--max-frames", type=int, default=150,
                    help="Hard cap on frames written (journal recipe: 150). 0 = no cap.")
    ap.add_argument("--seed", type=int, default=0,
                    help="RNG seed for stratified subsample when over max-frames.")
    ap.add_argument("--min-hits", type=int, default=5,
                    help="Skip tracks shorter than this. Below ~5 hits the "
                         "rejected pool is overwhelmingly noise.")
    ap.add_argument("--include-rejected", action="store_true", default=True,
                    help="Include tracks that failed confirmation (default on).")
    ap.add_argument("--counted-only", action="store_true",
                    help="Only confirmed tracks. Usually the wrong choice.")
    ap.add_argument("--weights", default="yolov8l.pt")
    ap.add_argument("--min-label-conf", type=float, default=0.10)
    ap.add_argument("--imgsz", type=int, default=1280)
    ap.add_argument("--limit", type=int, default=0,
                    help="Deprecated alias for --max-frames (0 = use --max-frames).")
    args = ap.parse_args()

    max_frames = args.max_frames
    if args.limit > 0:
        max_frames = args.limit

    images_dir = os.path.join(args.out, "images")
    labels_dir = os.path.join(args.out, "labels")
    previews_dir = os.path.join(args.out, "previews")
    for d in (images_dir, labels_dir, previews_dir):
        os.makedirs(d, exist_ok=True)
    with open(os.path.join(args.out, "classes.txt"), "w") as f:
        f.write("\n".join(CLASS_NAMES) + "\n")

    # --- collect target (chunk, timestamp) pairs ---
    targets = []
    for path in sorted(glob.glob(os.path.join(args.session_dir, "*_tracks.csv"))):
        chunk = os.path.basename(path).replace("_tracks.csv", "")
        with open(path) as f:
            for r in csv.DictReader(f):
                if r["class"] not in CYCLIST_CLASSES:
                    continue
                counted = r["counted"] == "yes"
                if args.counted_only and not counted:
                    continue
                if int(r["hits"]) < args.min_hits:
                    continue
                t0, t1 = float(r["first_t"]), float(r["last_t"])
                n = max(1, args.per_track)
                for k in range(n):
                    frac = 0.5 if n == 1 else k / (n - 1)
                    targets.append({
                        "chunk": chunk,
                        "t": t0 + frac * (t1 - t0),
                        "track_id": r["track_id"],
                        "counted": "yes" if counted else "no",
                        "cls": r["class"],
                        "hits": r["hits"],
                        "max_conf": r["max_conf"],
                        "mean_conf": r["mean_conf"],
                        "excursion": r["max_excursion_diag"],
                    })

    if not targets:
        raise SystemExit("No matching tracks found.")

    n_counted = sum(1 for t in targets if t["counted"] == "yes")
    print(f"{len(targets)} candidate frames from "
          f"{len(set((t['chunk'], t['track_id']) for t in targets))} tracks "
          f"({n_counted} from confirmed, {len(targets)-n_counted} from rejected)")

    targets = _stratified_subsample(targets, max_frames, seed=args.seed)
    print(f"After stratified subsample: {len(targets)} frames "
          f"(max-frames={max_frames or 'none'})")

    model = YOLO(args.weights)
    manifest = []
    seen_keys = set()
    by_chunk = {}
    for t in targets:
        by_chunk.setdefault(t["chunk"], []).append(t)

    saved = skipped = 0
    for chunk, items in sorted(by_chunk.items()):
        mp4 = os.path.join(args.video_dir, chunk + ".mp4")
        if not os.path.exists(mp4):
            print(f"  missing video for {chunk} -- cleaned up? skipping "
                  f"{len(items)} frames")
            skipped += len(items)
            continue
        source_video = os.path.abspath(mp4)
        cap = cv2.VideoCapture(mp4)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        for it in sorted(items, key=lambda x: x["t"]):
            if max_frames > 0 and saved >= max_frames:
                break
            frame_num = int(round(it["t"] * fps))
            dedupe_key = (source_video, frame_num)
            if dedupe_key in seen_keys:
                skipped += 1
                continue
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ok, frame = cap.read()
            if not ok:
                skipped += 1
                continue
            base = (f"{args.site}_{chunk}_trk{it['track_id']}_"
                    f"{'C' if it['counted']=='yes' else 'R'}_"
                    f"t{it['t']:.1f}s".replace(".", "p"))
            img_path = os.path.join(images_dir, base + ".jpg")
            if os.path.exists(img_path):
                # Resume: record manifest row if missing, count as saved
                seen_keys.add(dedupe_key)
                manifest.append({
                    "path": img_path,
                    "source_video": source_video,
                    "timestamp": round(it["t"], 3),
                    "frame_number": frame_num,
                    "site": args.site,
                    "sampling_method": "colonial_track",
                    "split": args.split,
                    "track_id": it["track_id"],
                    "counted": it["counted"],
                    "cls": it["cls"],
                    "hits": it["hits"],
                    "max_conf": it["max_conf"],
                    "mean_conf": it["mean_conf"],
                    "excursion": it["excursion"],
                })
                saved += 1
                continue
            boxes, _ = process_frame_detections(
                frame, model, COCO_QUERY_CLASSES, args.min_label_conf,
                fuse_cyclist=True)
            write_frame_outputs(frame, boxes, images_dir, labels_dir,
                                previews_dir, base)
            seen_keys.add(dedupe_key)
            n_cyc = sum(1 for b in boxes if CLASS_NAMES[b[0]] == "cyclist")
            manifest.append({
                "path": img_path,
                "source_video": source_video,
                "timestamp": round(it["t"], 3),
                "frame_number": frame_num,
                "site": args.site,
                "sampling_method": "colonial_track",
                "split": args.split,
                "track_id": it["track_id"],
                "counted": it["counted"],
                "cls": it["cls"],
                "hits": it["hits"],
                "max_conf": it["max_conf"],
                "mean_conf": it["mean_conf"],
                "excursion": it["excursion"],
                "n_boxes": len(boxes),
                "n_cyclist_boxes": n_cyc,
            })
            saved += 1
            if saved % 50 == 0:
                print(f"  {saved} frames written...")
        cap.release()
        if max_frames > 0 and saved >= max_frames:
            break

    manifest_path = os.path.join(args.out, "pool_manifest.csv")
    # Write required fields first; extra keys allowed in rows but only
    # required + provenance columns are standardized for assemble.
    write_fields = list(MANIFEST_FIELDS)
    extra = sorted({k for row in manifest for k in row} - set(write_fields))
    write_fields.extend(extra)
    with open(manifest_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=write_fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(manifest)

    n_with_cyc = sum(1 for m in manifest if int(m.get("n_cyclist_boxes", 0) or 0) > 0)
    print(f"\nWrote {saved} frames to {args.out}  ({skipped} skipped)")
    print(f"  frames with at least one pre-filled 'cyclist' box: {n_with_cyc} "
          f"({100.0*n_with_cyc/max(saved,1):.0f}%)")
    print(f"  classes: {', '.join(CLASS_NAMES)}")
    print(f"  manifest: {manifest_path}")
    print(f"\nNEXT: run extract_frames.py build for buckets B/C/D, then")
    print(f"  python assemble_annotation_pool.py ...")


if __name__ == "__main__":
    main()
