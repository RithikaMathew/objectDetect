#!/usr/bin/env python3
"""
sweep_fusion_v1.py - what if the final label used BOTH the RT-DETR detector label and X-CLIP?  (no GPU, no re-run)

Today the final label is X-CLIP alone (bicyclist if P(bicyclist) >= 0.5). The clip reviews show the two models fail in
different places: the detector is right when X-CLIP calls a walking person a bicyclist, X-CLIP is right when the detector
says 'person' for a real rider. tracks.csv (v14+) has, per track, X-CLIP's weighted probability and the % of detections the
detector classed 'cyclist' (det_cyclist_pct), so alternative rules can be scored against the ground truth offline.

Rule tested for each row:
    BICYCLIST  if  det_cyclist_pct >= --force-det                              (detector very sure it is a cyclist)
               or  ( P(bicyclist) >= 0.5  and  ( det_cyclist_pct >= D  or  P(bicyclist) >= O ) )
    PEDESTRIAN otherwise
D = detector cyclist % needed to back X-CLIP; O = X-CLIP probability high enough to be trusted on its own.
The first row (D=0) is the current behaviour. Only tracks lasting >= --min-secs and labelled by X-CLIP are used.

  python code/sweep_fusion_v1.py --root $ROOT --run colonial_run4 --run colonial_run5
  python code/sweep_fusion_v1.py --root $ROOT --run colonial_run4 --run colonial_run5 --show 20,0.95

CAUTION: ~24 bins, a handful of riders. Use this to see whether the idea is worth building, then confirm on different hours.
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
ap.add_argument("--min-secs", type=float, default=3.0)
ap.add_argument("--det-pct", type=float, nargs="+", default=[0, 10, 20, 30, 40, 50])
ap.add_argument("--override", type=float, nargs="+", default=[0.80, 0.90, 0.95, 1.01])
ap.add_argument("--force-det", type=float, default=80.0, help="detector cyclist %% that forces BICYCLIST (101 = never)")
ap.add_argument("--show", default=None, help="'D,O' -> list the tracks whose label changes vs the current rule")
ap.add_argument("--xls", default=None)
a = ap.parse_args()

xls = a.xls or os.path.join(a.root, "ground_truth", "Colonial_North_676806_07-10-2019.xls")
gt, _ = parse_gt(xls, [1, 2, 3, 4])
tracks, bins = [], set()
for run in a.run:
    for f in glob.glob(os.path.join(a.root, "counts", run, "*_tracks*.csv")):
        for r in csv.DictReader(open(f)):
            if r["label"] in ("BICYCLIST", "PEDESTRIAN") and r.get("det_cyclist_pct") not in (None, "") \
                    and float(r["secs"]) >= a.min_secs:
                tracks.append({"bin": int(r["bin_index"]), "pb": float(r["weighted_bicyclist"]), "dp": float(r["det_cyclist_pct"]),
                               "t": r["first_time"][11:], "secs": float(r["secs"]), "run": run,
                               "chunk": os.path.basename(f).split(".")[1][:3], "det": r.get("det_label", "?")})
    for f in glob.glob(os.path.join(a.root, "counts", run, "*_bin_counts*.csv")):
        for r in csv.DictReader(open(f)):
            if float(r["seconds_covered"]) >= 882:
                bins.add(int(r["bin_index"]))
bins = sorted(bins)
if not bins or not tracks:
    sys.exit("no tracks with det_cyclist_pct (need v14+ runs) or no full bins")
gb = {b: gt[b]["bic_bl"] + gt[b]["bic_sw"] for b in bins}
gp = {b: gt[b]["ped"] for b in bins}
print(f"{len(bins)} full bins, {len(tracks)} tracks >= {a.min_secs}s; GT totals: bicyclists {sum(gb.values())}, pedestrians {sum(gp.values())}\n")


def is_bic(t, D, O):
    if t["dp"] >= a.force_det:
        return True
    return t["pb"] >= 0.5 and (t["dp"] >= D or t["pb"] >= O)


def score(D, O):
    cb, cp = collections.Counter(), collections.Counter()
    for t in tracks:
        if t["bin"] in set(bins):
            (cb if is_bic(t, D, O) else cp)[t["bin"]] += 1
    mb = sum(abs(cb[b] - gb[b]) for b in bins) / len(bins)
    mp = sum(abs(cp[b] - gp[b]) for b in bins) / len(bins)
    return sum(cb[b] for b in bins), mb, sum(cp[b] for b in bins), mp


print(f"{'D (det%)':>8} {'O (xclip)':>9} | {'AI bic':>6} {'MAE bic':>7} | {'AI ped':>6} {'MAE ped':>7} | {'MAE sum':>7}")
base_rule = lambda t: t["pb"] >= 0.5
cb, cp = collections.Counter(), collections.Counter()
for t in tracks:
    if t["bin"] in set(bins):
        (cb if base_rule(t) else cp)[t["bin"]] += 1
mb = sum(abs(cb[b] - gb[b]) for b in bins) / len(bins)
mp = sum(abs(cp[b] - gp[b]) for b in bins) / len(bins)
print(f"{'current':>8} {'(X-CLIP only)':>9} | {sum(cb[b] for b in bins):6d} {mb:7.2f} | {sum(cp[b] for b in bins):6d} {mp:7.2f} | {mb + mp:7.2f}")
for D in a.det_pct:
    for O in a.override:
        sb, mb, sp, mp = score(D, O)
        print(f"{D:8.0f} {O:9.2f} | {sb:6d} {mb:7.2f} | {sp:6d} {mp:7.2f} | {mb + mp:7.2f}")

if a.show:
    D, O = map(float, a.show.split(","))
    print(f"\ntracks whose label changes under D={D}, O={O} (force-det {a.force_det}):")
    print("run chunk  first_seen  secs | det%cyclist  P(bic) | current -> fused")
    for t in tracks:
        cur, new = base_rule(t), is_bic(t, D, O)
        if cur != new:
            print(f"{t['run']} {t['chunk']}  {t['t']}  {t['secs']:5.1f} | {t['dp']:9.0f}  {t['pb']:6.2f} | "
                  f"{'BICYCLIST' if cur else 'PEDESTRIAN'} -> {'BICYCLIST' if new else 'PEDESTRIAN'}")
