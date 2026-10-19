#!/usr/bin/env python3
"""
threshold_sweep_v1.py

Cheap, no-retraining check: track_j_diagnostic.csv already logged the raw
confidence of every detection for every track on the NEW checkpoint. The
persistent false-positive tracks (6, 16, 21-25) all sit at low-to-mid mean
confidence (0.32-0.43); the real cyclist (track 7) sits at 0.757. Before
spending time on more data collection or retraining, check whether simply
raising the confidence threshold at inference time (in process_video's
`detections[detections.confidence >= conf_threshold]` filter) already
separates them well enough on its own.

This does NOT re-run the tracker (that would require re-simulating
ByteTrack's frame-by-frame association, which this script doesn't
attempt) -- it's an approximation: for each candidate threshold, it
re-counts, per original track_id, how many of that track's already-logged
detections survive the higher threshold, and flags tracks that would
likely have failed to ever reach MIN_TRACK_HITS (=2) under that threshold.
This tells you directionally whether a threshold bump helps, fast --
final confirmation still needs an actual re-run through
compare_detectors_v7_fixed.py at the chosen threshold.

Usage:
    python threshold_sweep_v1.py --csv pilot_output/compare_v4/track_j_diagnostic.csv
"""
import argparse
import csv
from collections import defaultdict


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--min-track-hits", type=int, default=2,
                     help="must match MIN_TRACK_HITS in compare_detectors_v7_fixed.py (default 2)")
    ap.add_argument("--thresholds", type=float, nargs="+",
                     default=[0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6, 0.7])
    args = ap.parse_args()

    by_track = defaultdict(list)
    with open(args.csv) as f:
        for row in csv.DictReader(f):
            by_track[int(row["tracker_id"])].append(
                (int(row["frame"]), float(row["cx"]), float(row["cy"]), float(row["conf"])))

    print(f"Loaded {sum(len(v) for v in by_track.values())} detections across "
          f"{len(by_track)} tracks from {args.csv}\n")

    # per-track summary at the original (lowest) threshold, for reference
    print("--- original per-track stats ---")
    for tid, dets in sorted(by_track.items()):
        confs = [d[3] for d in dets]
        mean_cx = sum(d[1] for d in dets) / len(dets)
        mean_cy = sum(d[2] for d in dets) / len(dets)
        print(f"track {tid}: n={len(dets)} mean_conf={sum(confs)/len(confs):.3f} "
              f"max_conf={max(confs):.3f} centroid=({mean_cx:.1f},{mean_cy:.1f})")

    print("\n--- threshold sweep: surviving tracks (approx, no re-tracking) ---")
    for thresh in args.thresholds:
        survivors = []
        for tid, dets in by_track.items():
            n_pass = sum(1 for d in dets if d[3] >= thresh)
            if n_pass >= args.min_track_hits:
                survivors.append((tid, n_pass, len(dets)))
        survivors.sort()
        print(f"\nthreshold={thresh}: {len(survivors)} tracks would likely survive "
              f"(of {len(by_track)} original)")
        for tid, n_pass, n_total in survivors:
            print(f"  track {tid}: {n_pass}/{n_total} detections pass")

    print("\nLook for the threshold where the real cyclist track survives but "
          "the persistent-location tracks (the ones with very high n_total in "
          "the original stats above, at low mean_conf) drop out. That's a "
          "candidate operating threshold to test with a real re-run.")


if __name__ == "__main__":
    main()
