#!/usr/bin/env python3
"""
headline_metrics_v1.py - ONE table that says how well the counting works, per class, against the human ground truth.

Pools every fully processed 15-minute bin from the runs you name (counts/<run>/*_bin_counts*.csv) and compares with the
Colonial North counter .xls (North channels; bicyclists = bike lane + sidewalk). Reports, for BICYCLISTS and PEDESTRIANS:
  total AI vs total GT (and AI/GT), signed bias per bin, MAE per bin, WAPE per bin and per hour (= sum|err| / sum GT),
  share of bins exact / within +-1, MAE per hour, Pearson r, and approximate count-matched precision/recall.
  Per-bin WAPE is harsh when bins hold only 0-4 people (a rider counted one bin early is an error twice); the hourly
  numbers and the AI/GT ratio are the fairer headline. Also split into day and night, and how much of the 48-hour ground truth the processed bins cover.

  python code/headline_metrics_v1.py --root $ROOT --run colonial_run2 --run colonial_run4 --run colonial_run5

Note: if two runs contain the same bin, the LAST --run given is used. Per-object accuracy needs track_truth_v1.py.
"""
import argparse
import csv
import glob
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aggregate_colonial_v13 import parse_gt  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--root", required=True)
ap.add_argument("--run", action="append", required=True)
ap.add_argument("--xls", default=None)
ap.add_argument("--night-from", type=int, default=20, help="bins starting at/after this hour are 'night'")
ap.add_argument("--night-to", type=int, default=6, help="bins starting before this hour are 'night'")
a = ap.parse_args()

xls = a.xls or os.path.join(a.root, "ground_truth", "Colonial_North_676806_07-10-2019.xls")
gt, _ = parse_gt(xls, [1, 2, 3, 4])
ai = {}
for run in a.run:
    for f in glob.glob(os.path.join(a.root, "counts", run, "*_bin_counts*.csv")):
        for r in csv.DictReader(open(f)):
            if float(r["seconds_covered"]) >= 882:
                ai[int(r["bin_index"])] = (int(r["bicyclists_total"]), int(r["pedestrians"]), run)
bins = sorted(ai)
if not bins:
    sys.exit("no fully processed bins found")
is_night = lambda b: (b // 4) % 24 >= a.night_from or (b // 4) % 24 < a.night_to
GTALL = {"BICYCLISTS": sum(g["bic_bl"] + g["bic_sw"] for g in gt.values()), "PEDESTRIANS": sum(g["ped"] for g in gt.values())}


def pearson(x, y):
    n = len(x)
    if n < 3:
        return float("nan")
    mx, my = sum(x) / n, sum(y) / n
    d = math.sqrt(sum((p - mx) ** 2 for p in x) * sum((q - my) ** 2 for q in y))
    return sum((p - mx) * (q - my) for p, q in zip(x, y)) / d if d else float("nan")


def block(name, sel, k):
    A = [ai[b][k] for b in sel]
    G = [(gt[b]["bic_bl"] + gt[b]["bic_sw"]) if k == 0 else gt[b]["ped"] for b in sel]
    n, sa, sg = len(sel), sum(A), sum(G)
    if n == 0:
        return
    err = [x - y for x, y in zip(A, G)]
    mae = sum(abs(e) for e in err) / n
    wape = sum(abs(e) for e in err) / sg if sg else float("nan")
    m = sum(min(x, y) for x, y in zip(A, G))
    hours = sorted({b // 4 for b in sel})
    hsum = [abs(sum(ai[b][k] - ((gt[b]["bic_bl"] + gt[b]["bic_sw"]) if k == 0 else gt[b]["ped"]) for b in sel if b // 4 == h)) for h in hours]
    hmae = sum(hsum) / len(hours)
    hwape = sum(hsum) / sg if sg else float("nan")
    print(f"  {name:7s} bins {n:3d} hours {len(hours):2d} | AI {sa:3d} vs GT {sg:3d} ({(sa / sg if sg else float('nan')):4.0%}) | bias/bin {sum(err) / n:+5.2f} | "
          f"MAE/bin {mae:4.2f} | WAPE/bin {wape:4.0%} | exact {sum(e == 0 for e in err) / n:3.0%} | "
          f"+-1 {sum(abs(e) <= 1 for e in err) / n:3.0%} | MAE/hour {hmae:4.2f} | WAPE/hour {hwape:4.0%} | r {pearson(A, G):5.2f} | "
          f"prec~ {(m / sa if sa else float('nan')):3.0%} rec~ {(m / sg if sg else float('nan')):3.0%}")


print(f"processed bins: {len(bins)} ({len(bins) // 4} hours) from runs {a.run}; hours (chunk numbers): {sorted({b // 4 + 1 for b in bins})}")
for k, cls in ((0, "BICYCLISTS"), (1, "PEDESTRIANS")):
    covered = sum(((gt[b]["bic_bl"] + gt[b]["bic_sw"]) if k == 0 else gt[b]["ped"]) for b in bins)
    print(f"\n{cls}  (ground truth over the full 48 h = {GTALL[cls]}; the processed bins hold {covered} of them = {covered / GTALL[cls]:.0%})")
    block("ALL", bins, k)
    block("DAY", [b for b in bins if not is_night(b)], k)
    block("NIGHT", [b for b in bins if is_night(b)], k)
