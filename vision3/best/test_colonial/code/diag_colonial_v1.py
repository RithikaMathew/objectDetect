#!/usr/bin/env python3
"""
diag_colonial_v1.py  -  quick terminal diagnostics on finished runs (no GPU).

  python code/diag_colonial_v1.py --root $ROOT --mode bins --run colonial_run4
      per-15-min table: AI vs ground truth for bicyclists and pedestrians (same numbers as the Excel Per_15min sheet)
  python code/diag_colonial_v1.py --root $ROOT --mode peds --run colonial_run4
      every counted PEDESTRIAN track: time seen, detector label/conf, seconds visible, net movement, zone
"""
import argparse
import csv
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aggregate_colonial_v13 import parse_gt  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--root", required=True)
ap.add_argument("--run", action="append", required=True)
ap.add_argument("--mode", choices=["bins", "peds"], required=True)
ap.add_argument("--xls", default=None)
a = ap.parse_args()

if a.mode == "bins":
    xls = a.xls or os.path.join(a.root, "ground_truth", "Colonial_North_676806_07-10-2019.xls")
    gt, _ = parse_gt(xls, [1, 2, 3, 4])
    print("run          bin start   | AI bic  GT bic | AI ped  GT ped | secs")
    for run in a.run:
        for f in sorted(glob.glob(os.path.join(a.root, "counts", run, "*_bin_counts*.csv"))):
            for r in csv.DictReader(open(f)):
                g = gt[int(r["bin_index"])]
                part = "" if float(r["seconds_covered"]) >= 882 else "  (partial)"
                print(f"{run:12s} {r['bin_start'][5:16]} | {r['bicyclists_total']:>6}  {g['bic_bl'] + g['bic_sw']:>6} | "
                      f"{r['pedestrians']:>6}  {g['ped']:>6} | {r['seconds_covered']}{part}")
else:
    print("run          chunk | first_seen last_seen | det_label  det_conf  secs  net_px  zone")
    for run in a.run:
        for f in sorted(glob.glob(os.path.join(a.root, "counts", run, "*_tracks*.csv"))):
            n = os.path.basename(f).split(".")[1][:3]
            for r in csv.DictReader(open(f)):
                if r["counted"] == "1" and r["label"] == "PEDESTRIAN":
                    print(f"{run:12s} {n}   | {r['first_time'][11:]} {r['last_time'][11:]} | {r.get('det_label', '?'):>9} "
                          f"{float(r['mean_conf']):8.2f} {float(r['secs']):5.1f} {r.get('disp_px', ''):>7}  {r['facility']}")
