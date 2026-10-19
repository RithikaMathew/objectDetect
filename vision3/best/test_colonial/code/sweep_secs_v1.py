#!/usr/bin/env python3
"""
sweep_secs_v1.py - what if the minimum track duration were shorter?  (no GPU, no re-run)

xclip_overlay_v14 writes EVERY track to tracks.csv (also the ones dropped by --person-min-sec, default 3 s), together with
its X-CLIP label, duration, detector confidence and net movement. This script re-counts per 15-min bin using only tracks
that last at least S seconds, for several S, and compares with the ground truth.

  python code/sweep_secs_v1.py --root $ROOT --run colonial_run4 --label PEDESTRIAN
  python code/sweep_secs_v1.py --root $ROOT --run colonial_run4 --label BICYCLIST --secs 0.5 1 1.5 2 3

Reading it: the right S is where the bias gets close to 0 while 'precision~' stays high. precision~ = sum(min(AI,GT))/sum(AI):
if it falls a lot, the extra tracks are mostly junk (the AI is counting more than the counters in those bins).
Caveat: tracks also dropped for other reasons (tiny boxes, --person-min-conf) are included here, so S=3 can be a little
above the real counted number. Confirm any choice on hours you did not tune on, then re-run with --person-min-sec S.
"""
import argparse
import collections
import csv
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aggregate_colonial_v13 import parse_gt  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--root", required=True)
ap.add_argument("--run", action="append", required=True)
ap.add_argument("--label", choices=["PEDESTRIAN", "BICYCLIST"], default="PEDESTRIAN")
ap.add_argument("--secs", type=float, nargs="+", default=[0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
ap.add_argument("--min-conf", type=float, default=0.0, help="also require this mean detector confidence")
ap.add_argument("--min-disp", type=float, default=0.0, help="also require this net movement in px (0 = no limit)")
ap.add_argument("--xls", default=None)
a = ap.parse_args()

xls = a.xls or os.path.join(a.root, "ground_truth", "Colonial_North_676806_07-10-2019.xls")
gt, _ = parse_gt(xls, [1, 2, 3, 4])
gt_of = (lambda b: gt[b]["ped"]) if a.label == "PEDESTRIAN" else (lambda b: gt[b]["bic_bl"] + gt[b]["bic_sw"])
tracks, bins = [], set()
for run in a.run:
    for f in glob.glob(os.path.join(a.root, "counts", run, "*_tracks*.csv")):
        for r in csv.DictReader(open(f)):
            if r["label"] == a.label:
                tracks.append((int(r["bin_index"]), float(r["secs"]), float(r["mean_conf"]),
                               float(r["disp_px"]) if r.get("disp_px") else float("inf")))
    for f in glob.glob(os.path.join(a.root, "counts", run, "*_bin_counts*.csv")):
        for r in csv.DictReader(open(f)):
            if float(r["seconds_covered"]) >= 882:
                bins.add(int(r["bin_index"]))
bins = sorted(bins)
if not bins:
    sys.exit("no fully covered bins found")
gtot = sum(gt_of(b) for b in bins)
print(f"{a.label}: {len(bins)} full bins from {a.run}; GT total = {gtot}; min conf {a.min_conf}; min net movement {a.min_disp} px")
print(f"all {a.label} tracks in these runs (any duration): {sum(1 for t in tracks if t[0] in set(bins))}\n")
print(f"{'min secs':>8} | {'AI total':>8} | {'bias/bin':>8} | {'MAE/bin':>7} | {'within+-1':>9} | {'precision~':>10} | {'recall~':>7}")
for s in a.secs:
    c = collections.Counter(b for b, sec, cf, d in tracks if sec >= s and cf >= a.min_conf and d >= a.min_disp and b in set(bins))
    err = [c[b] - gt_of(b) for b in bins]
    n, tot = len(bins), sum(c[b] for b in bins)
    m = sum(min(c[b], gt_of(b)) for b in bins)
    print(f"{s:8.1f} | {tot:8d} | {sum(err) / n:+8.2f} | {sum(abs(e) for e in err) / n:7.2f} | "
          f"{sum(abs(e) <= 1 for e in err) / n:9.0%} | {(m / tot if tot else float('nan')):10.0%} | {(m / gtot if gtot else float('nan')):7.0%}")
