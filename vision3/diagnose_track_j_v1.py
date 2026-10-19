#!/usr/bin/env python3
"""
diagnose_track_j_v1.py

PURPOSE
-------
compare_detectors_v7_fixed.py's process_video() only ever accumulates
aggregate stage totals (post_fuse / post_conf / post_tracker counts and a
single max_hit_count) into summary_J.json. It never records WHERE each
tracker_id actually was, frame by frame -- so right now there is no way to
tell, from existing outputs, whether Method J's "7 unique cyclists" is:

  (a) real hallucination -- 7 spatially/temporally unrelated false
      positives, or
  (b) track fragmentation -- one genuine (finally-visible!) distant
      cyclist whose track keeps dying and respawning because gaps between
      low-confidence detections exceed lost_track_buffer, exactly the
      documented benign pattern already seen on methods H and old-F (see
      compare_detectors_v7_fixed.py's own docstring, section on "benign
      double-count").

This script does NOT change or replace compare_detectors_v7_fixed.py --
it imports build_finetuned_detector and reuses the identical tracker
config from it, then just adds the missing per-track logging on top, and
writes a CSV. Run this instead of (or alongside) a normal Method J run
when you specifically want to answer the fragmentation-vs-hallucination
question.

USAGE
-----
    python diagnose_track_j_v1.py \\
        --video /orange/xiangyan/rithika/vision/vision3/test.mp4 \\
        --finetune-weights /orange/xiangyan/rithika/vision/vision3/finetune_runs/rtdetr_v1/weights/best.pt \\
        --outdir /orange/xiangyan/rithika/vision/vision3/pilot_output/compare_v4

Writes: <outdir>/track_j_diagnostic.csv with columns:
    frame, tracker_id, cx, cy, w, h, conf, hit_count_so_far

Then also prints a same-second summary per track: first_frame, last_frame,
n_detections, mean centroid, mean confidence -- and, for every pair of
tracks, the frame-gap between one ending and the next starting plus the
centroid distance between them (this is the actual fragmentation check:
a small gap + small distance strongly suggests re-fragmentation of the
same rider rather than 7 independent detections).

Requires compare_detectors_v7_fixed.py to be importable (same directory,
or on PYTHONPATH) since it reuses build_finetuned_detector from there
rather than reimplementing the fine-tuned-model inference path.
"""
import argparse
import csv
import os
from pathlib import Path

import numpy as np
import supervision as sv
import torch

# Reuse the real detector + real tracker config -- do not reimplement.
from compare_detectors_v7_fixed import (
    build_finetuned_detector,
    TRACK_ACTIVATION_THRESHOLD,
    MIN_MATCHING_THRESHOLD,
    MIN_TRACK_HITS,
)


def run_diagnostic(video_path: str, finetune_weights: str, outdir: str, device: str):
    os.makedirs(outdir, exist_ok=True)
    csv_path = os.path.join(outdir, "track_j_diagnostic.csv")

    detect_fn, label = build_finetuned_detector(finetune_weights, device)
    video_info = sv.VideoInfo.from_video_path(video_path)

    tracker = sv.ByteTrack(
        frame_rate=video_info.fps,
        track_activation_threshold=TRACK_ACTIVATION_THRESHOLD,
        lost_track_buffer=int(video_info.fps * 3),
        minimum_matching_threshold=MIN_MATCHING_THRESHOLD,
    )

    hit_counts = {}
    rows = []
    frame_count = 0

    print(f"[{label}] logging per-track detections to {csv_path}", flush=True)

    for frame in sv.get_video_frames_generator(source_path=video_path):
        frame_count += 1
        detections = detect_fn(frame)
        if len(detections) > 0:
            detections = detections[detections.confidence >= 0.25]
        detections = tracker.update_with_detections(detections)

        if detections.tracker_id is not None:
            for i, tid in enumerate(detections.tracker_id.tolist()):
                hit_counts[tid] = hit_counts.get(tid, 0) + 1
                x1, y1, x2, y2 = detections.xyxy[i]
                cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                w, h = x2 - x1, y2 - y1
                conf = float(detections.confidence[i])
                rows.append([frame_count, tid, round(float(cx), 1), round(float(cy), 1),
                             round(float(w), 1), round(float(h), 1), round(conf, 3),
                             hit_counts[tid]])

        if frame_count % 500 == 0:
            print(f"[{label}] frame {frame_count}/{video_info.total_frames} "
                  f"-- tracks seen so far: {sorted(hit_counts.keys())}", flush=True)

    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["frame", "tracker_id", "cx", "cy", "w", "h", "conf", "hit_count_so_far"])
        w.writerows(rows)

    print(f"\n[{label}] wrote {len(rows)} detection rows across "
          f"{len(hit_counts)} tracker_ids to {csv_path}\n", flush=True)

    # --- Per-track summary ---
    by_track = {}
    for r in rows:
        frame, tid, cx, cy, w_, h_, conf, hit = r
        by_track.setdefault(tid, []).append((frame, cx, cy, conf))

    summaries = {}
    for tid, pts in sorted(by_track.items()):
        frames = [p[0] for p in pts]
        cxs = [p[1] for p in pts]
        cys = [p[2] for p in pts]
        confs = [p[3] for p in pts]
        summaries[tid] = {
            "first_frame": min(frames),
            "last_frame": max(frames),
            "n_detections": len(pts),
            "mean_cx": round(float(np.mean(cxs)), 1),
            "mean_cy": round(float(np.mean(cys)), 1),
            "mean_conf": round(float(np.mean(confs)), 3),
        }
        print(f"track {tid}: frames {summaries[tid]['first_frame']}-"
              f"{summaries[tid]['last_frame']} ({summaries[tid]['n_detections']} dets), "
              f"mean centroid ({summaries[tid]['mean_cx']}, {summaries[tid]['mean_cy']}), "
              f"mean conf {summaries[tid]['mean_conf']}")

    # --- Pairwise adjacency check: does track B start near where A ended? ---
    print("\n--- fragmentation check: consecutive track pairs ordered by time ---")
    ordered = sorted(summaries.items(), key=lambda kv: kv[1]["first_frame"])
    fps = video_info.fps
    for (tid_a, sa), (tid_b, sb) in zip(ordered, ordered[1:]):
        frame_gap = sb["first_frame"] - sa["last_frame"]
        dist = ((sb["mean_cx"] - sa["mean_cx"]) ** 2 +
                (sb["mean_cy"] - sa["mean_cy"]) ** 2) ** 0.5
        gap_seconds = frame_gap / fps if fps else 0
        verdict = "LIKELY SAME RIDER (re-fragmented)" if (0 <= frame_gap < fps * 5 and dist < 150) \
            else "looks independent"
        print(f"track {tid_a} -> track {tid_b}: gap={frame_gap} frames "
              f"({gap_seconds:.1f}s), centroid dist={dist:.0f}px -> {verdict}")

    print(f"\nCSV written to: {csv_path}")
    print("Pull this file back for closer inspection if any verdict above is ambiguous.")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--video", required=True)
    ap.add_argument("--finetune-weights", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"device={device}")
    run_diagnostic(args.video, args.finetune_weights, args.outdir, device)


if __name__ == "__main__":
    main()
