#!/usr/bin/env python3
"""
sweep_conf_v2.py  -  re-count a finished run at different minimum track confidences, NO GPU / re-run needed.

Reads counts/<run>/*_tracks.csv written by xclip_overlay_v12_colonial.py (one row per track, with mean_conf)
and compares per-15-min counts with the ground truth for several thresholds.

  python code/sweep_conf_v2.py --root $ROOT --run colonial_run2 --label PEDESTRIAN
  python code/sweep_conf_v2.py --root $ROOT --run colonial_run2 --label BICYCLIST --thresholds 0 0.4 0.5 0.6

IMPORTANT: choose a threshold on some hours and CONFIRM it on different hours. Picking the value that happens to
fit the same few bins you are scoring is overfitting. Pass several runs with --run a --run b to pool hours.
"""
import argparse
import collections
import csv
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aggregate_colonial_v12 import parse_gt  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--run", action="append", required=True, help="repeat to pool several runs")
    ap.add_argument("--label", choices=["PEDESTRIAN", "BICYCLIST"], default="PEDESTRIAN")
    ap.add_argument("--thresholds", type=float, nargs="+", default=[0.0, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6])
    ap.add_argument("--min-disp", type=float, default=0.0, help="also require net movement >= this many px (needs disp_px in tracks.csv, i.e. v13 runs)")
    ap.add_argument("--xls", default=None)
    ap.add_argument("--ped-cols", default="1,2,3,4")
    a = ap.parse_args()

    xls = a.xls or os.path.join(a.root, "ground_truth", "Colonial_North_676806_07-10-2019.xls")
    gt, _ = parse_gt(xls, [int(c) for c in a.ped_cols.split(",")])
    gt_of = (lambda b: gt[b]["ped"]) if a.label == "PEDESTRIAN" else (lambda b: gt[b]["bic_bl"] + gt[b]["bic_sw"])

    tracks, bins = [], set()
    for run in a.run:
        for f in glob.glob(os.path.join(a.root, "counts", run, "*_tracks.csv")):
            for r in csv.DictReader(open(f)):
                if r["counted"] == "1" and r["label"] == a.label:
                    tracks.append((int(r["bin_index"]), float(r["mean_conf"]), float(r["disp_px"]) if r.get("disp_px") else float("inf")))
        for f in glob.glob(os.path.join(a.root, "counts", run, "*_bin_counts.csv")):
            for r in csv.DictReader(open(f)):
                if float(r["seconds_covered"]) >= 0.98 * 900:      # only fully processed bins
                    bins.add(int(r["bin_index"]))
    bins = sorted(bins)
    if not bins:
        sys.exit("no fully covered bins found")
    gtot = sum(gt_of(b) for b in bins)
    print(f"{a.label}: {len(bins)} full bins from runs {a.run}; GT total = {gtot}; min net movement = {a.min_disp} px\n")
    print(f"{'min conf':>8} | {'AI total':>8} | {'bias/bin':>8} | {'MAE/bin':>7} | {'within+-1':>9} | {'tracks kept':>11}")
    for thr in a.thresholds:
        c = collections.Counter(b for b, m, d in tracks if m >= thr and d >= a.min_disp and b in set(bins))
        err = [c[b] - gt_of(b) for b in bins]
        n = len(bins)
        print(f"{thr:8.2f} | {sum(c[b] for b in bins):8d} | {sum(err) / n:+8.2f} | {sum(abs(e) for e in err) / n:7.2f} | "
              f"{sum(abs(e) <= 1 for e in err) / n:9.0%} | {sum(1 for _, m, d in tracks if m >= thr and d >= a.min_disp):11d}")


if __name__ == "__main__":
    main()
