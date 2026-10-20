#!/usr/bin/env python3
"""
prepare_hard_negatives_v1.py

Two-stage script for the three persistent false-positive locations found
in the retrained checkpoint's diagnostic run:
    location A (track 1/3/5/6 cluster): ~(75, 112)
    location B (track 16):              ~(264, 306)
    location C (track 21-25 cluster):   ~(643, 22)

STAGE 1 (--mode inspect, default): pulls a few full frames + tight crops
around each location so you can visually confirm what's actually there
(cone, sign, whatever) before anything gets added to training data.
Writes to <outdir>/inspect/.

STAGE 2 (--mode prepare): once you've confirmed via stage 1, copies the
chosen full frames into the training split's images/ folder and writes a
matching EMPTY label file (0 objects) for each -- teaching the model
"nothing here is a cyclist." Does NOT touch existing training images or
labels; only adds new files.

IMPORTANT CAVEAT stage 2 does not handle automatically: if these frames
also contain other real objects (cars, a person, etc. elsewhere in frame)
that belong to your other classes (bus/car/other_vehicle/person/truck),
an empty label file would incorrectly teach the model those aren't
objects either. Check the frame yourself first -- if it contains other
real objects, label those manually instead of using a fully empty file.
This script only ever writes fully-empty label files; it does not
attempt to auto-detect and label other classes.

Usage:
    # Stage 1 -- look first
    python prepare_hard_negatives_v1.py --mode inspect \\
        --video test.mp4 --outdir pilot_output/compare_v4/hard_negative_check

    # Stage 2 -- after confirming, add chosen frames as hard negatives.
    # --frames takes explicit frame numbers you picked from stage 1 output.
    python prepare_hard_negatives_v1.py --mode prepare \\
        --video test.mp4 \\
        --frames 1000 2500 4000 \\
        --split-root /orange/xiangyan/rithika/vision/dataset_frames/roboflow_split_v1 \\
        --split train
"""
import argparse
import os
from pathlib import Path

import cv2

LOCATIONS = {
    "A_cone_cluster": (75, 112, 60, 90),    # cx, cy, approx w, h from tracks 1/3/5/6
    "B_track16": (264, 306, 60, 90),
    "C_track21-25": (643, 22, 40, 60),
}


def stage_inspect(video_path: str, outdir: str, sample_frames):
    os.makedirs(outdir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    frame_idx = 0
    targets = set(sample_frames)
    max_frame = max(targets)

    print(f"Pulling frames {sorted(targets)} for inspection...")
    while frame_idx <= max_frame:
        ok, frame = cap.read()
        if not ok:
            break
        frame_idx += 1
        if frame_idx not in targets:
            continue

        full_path = os.path.join(outdir, f"frame{frame_idx}_full.jpg")
        cv2.imwrite(full_path, frame)

        for name, (cx, cy, w, h) in LOCATIONS.items():
            pad = 40
            x1, y1 = max(0, int(cx - w / 2 - pad)), max(0, int(cy - h / 2 - pad))
            x2, y2 = int(cx + w / 2 + pad), int(cy + h / 2 + pad)
            crop = frame[y1:y2, x1:x2]
            crop_path = os.path.join(outdir, f"frame{frame_idx}_{name}.jpg")
            cv2.imwrite(crop_path, crop)

    cap.release()
    print(f"Saved full frames + per-location crops to {outdir}")
    print("Look at the *_A_cone_cluster / *_B_track16 / *_C_track21-25 crops "
          "to confirm what's actually at each location, and check the "
          "*_full.jpg frames for any OTHER real objects (cars, people) "
          "elsewhere in frame before using --mode prepare on these frame numbers.")


def stage_prepare(video_path: str, frame_numbers, split_root: str, split: str):
    images_dir = Path(split_root) / split / "images"
    labels_dir = Path(split_root) / split / "labels"
    images_dir.mkdir(parents=True, exist_ok=True)
    labels_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    frame_idx = 0
    targets = set(frame_numbers)
    max_frame = max(targets)
    saved = []

    while frame_idx <= max_frame:
        ok, frame = cap.read()
        if not ok:
            break
        frame_idx += 1
        if frame_idx not in targets:
            continue

        stem = f"hardneg_testmp4_frame{frame_idx}"
        img_path = images_dir / f"{stem}.jpg"
        label_path = labels_dir / f"{stem}.txt"

        cv2.imwrite(str(img_path), frame)
        label_path.write_text("")  # empty = no objects of any class
        saved.append(stem)

    cap.release()
    print(f"Added {len(saved)} hard-negative frames (image + EMPTY label) to "
          f"{split_root}/{split}/:")
    for s in saved:
        print(f"  {s}")
    print("\nREMINDER: these label files are fully empty. If any of these "
          "frames contain other real objects (cars, people, etc.), edit "
          "those .txt files by hand to add the correct boxes for those "
          "classes before retraining -- otherwise the model will also be "
          "taught those objects don't exist.")
    print("\nNext: re-run split_dataset.py's data.yaml is unaffected (same "
          "classes), so you can go straight to:\n  sbatch run_finetune.slurm")
    print("(delete or rename the existing finetune_runs/rtdetr_v1 dir first "
          "if you want a clean run rather than resuming/overwriting)")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=["inspect", "prepare"], default="inspect")
    ap.add_argument("--video", required=True)
    ap.add_argument("--outdir", help="required for --mode inspect")
    ap.add_argument("--sample-frames", type=int, nargs="+",
                     default=[1000, 2500, 4000, 4600, 5000],
                     help="frame numbers to pull for inspect mode")
    ap.add_argument("--frames", type=int, nargs="+",
                     help="required for --mode prepare: exact frame numbers to add")
    ap.add_argument("--split-root", help="required for --mode prepare")
    ap.add_argument("--split", default="train", choices=["train", "val", "test"])
    args = ap.parse_args()

    if args.mode == "inspect":
        if not args.outdir:
            ap.error("--outdir required for --mode inspect")
        stage_inspect(args.video, args.outdir, args.sample_frames)
    else:
        if not args.frames or not args.split_root:
            ap.error("--frames and --split-root required for --mode prepare")
        stage_prepare(args.video, args.frames, args.split_root, args.split)


if __name__ == "__main__":
    main()
