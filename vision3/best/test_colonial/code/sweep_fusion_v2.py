#!/usr/bin/env python3
"""
sweep_fusion_v2.py - how good is each labelling rule at getting the per-15-min COUNTS right?  (no GPU, no re-run)

Rules compared, using the per-track data in tracks.csv (v14+ runs):
  X-CLIP only        BICYCLIST if P(bicyclist) >= 0.5                       (what the pipeline does today)
  RT-DETR only       BICYCLIST if the detector called >= 50% of its detections 'cyclist'
  both agree         BICYCLIST only if both say bicyclist
  either             BICYCLIST if either says bicyclist
  fused (D,O,F)      see below
  speed only         BICYCLIST if net movement / duration >= S px/s  (cyclists are much faster than walkers)
  X-CLIP + speed     BICYCLIST if X-CLIP says bicyclist AND speed >= S
fused: BICYCLIST if det% >= F, or (P(bic) >= 0.5 and (det% >= D or P(bic) >= O)).

IMPORTANT: this scores COUNTS per 15-min bin against the human counts. It is not per-object accuracy (the ground truth has
no per-person labels). For real accuracy, label tracks with track_truth_v1.py.

  python code/sweep_fusion_v2.py --root $ROOT --run colonial_run4 --run colonial_run5
  python code/sweep_fusion_v2.py --root $ROOT --run colonial_run4 --run colonial_run5 --speeds 20 40 80 --show-fused
"""
import argparse
import collections
import csv
import glob
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aggregate_colonial_v13 import parse_gt  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--root", required=True)
ap.add_argument("--run", action="append", required=True)
ap.add_argument("--min-secs", type=float, default=3.0)
ap.add_argument("--D", type=float, default=20.0)
ap.add_argument("--O", type=float, default=0.95)
ap.add_argument("--F", type=float, default=80.0)
ap.add_argument("--speeds", type=float, nargs="+", default=[20.0, 40.0, 80.0, 120.0], help="px/s thresholds for the speed rules")
ap.add_argument("--show-fused", action="store_true", help="list tracks whose label differs between X-CLIP only and fused")
ap.add_argument("--xls", default=None)
a = ap.parse_args()

xls = a.xls or os.path.join(a.root, "ground_truth", "Colonial_North_676806_07-10-2019.xls")
gt, _ = parse_gt(xls, [1, 2, 3, 4])
T, bins = [], set()
for run in a.run:
    for f in glob.glob(os.path.join(a.root, "counts", run, "*_tracks*.csv")):
        for r in csv.DictReader(open(f)):
            if r["label"] in ("BICYCLIST", "PEDESTRIAN") and r.get("det_cyclist_pct") not in (None, "") and float(r["secs"]) >= a.min_secs:
                secs = float(r["secs"])
                disp = float(r["disp_px"]) if r.get("disp_px") else None
                T.append({"bin": int(r["bin_index"]), "pb": float(r["weighted_bicyclist"]), "dp": float(r["det_cyclist_pct"]),
                          "speed": (disp / secs) if disp is not None and secs > 0 else None, "xl": r["label"], "secs": secs,
                          "t": r["first_time"][11:], "run": run, "chunk": os.path.basename(f).split(".")[1][:3]})
    for f in glob.glob(os.path.join(a.root, "counts", run, "*_bin_counts*.csv")):
        for r in csv.DictReader(open(f)):
            if float(r["seconds_covered"]) >= 882:
                bins.add(int(r["bin_index"]))
bins = sorted(bins)
bset = set(bins)
if not bins or not T:
    sys.exit("no tracks with det_cyclist_pct (need v14+ runs) or no full bins")
gb = {b: gt[b]["bic_bl"] + gt[b]["bic_sw"] for b in bins}
gp = {b: gt[b]["ped"] for b in bins}
print(f"{len(bins)} full bins, {len(T)} tracks >= {a.min_secs}s; ground-truth totals: bicyclists {sum(gb.values())}, pedestrians {sum(gp.values())}\n")

sp = {"BICYCLIST": sorted(round(t["speed"]) for t in T if t["xl"] == "BICYCLIST" and t["speed"] is not None),
      "PEDESTRIAN": sorted(round(t["speed"]) for t in T if t["xl"] == "PEDESTRIAN" and t["speed"] is not None)}
for k, v in sp.items():
    if v:
        print(f"net speed px/s of tracks X-CLIP calls {k} (n={len(v)}, median {statistics.median(v):.0f}): {v}")
print()


def evaluate(rule):
    cb, cp = collections.Counter(), collections.Counter()
    for t in T:
        if t["bin"] in bset:
            (cb if rule(t) else cp)[t["bin"]] += 1
    n = len(bins)
    return (sum(cb[b] for b in bins), sum(abs(cb[b] - gb[b]) for b in bins) / n, sum(abs(cb[b] - gb[b]) <= 1 for b in bins) / n,
            sum(cp[b] for b in bins), sum(abs(cp[b] - gp[b]) for b in bins) / n)


xclip = lambda t: t["pb"] >= 0.5
det = lambda t: t["dp"] >= 50
rules = [("X-CLIP only (current)", xclip), ("RT-DETR only (>=50% cyclist)", det),
         ("both agree", lambda t: xclip(t) and det(t)), ("either", lambda t: xclip(t) or det(t)),
         (f"fused D={a.D:.0f} O={a.O} F={a.F:.0f}",
          lambda t: t["dp"] >= a.F or (t["pb"] >= 0.5 and (t["dp"] >= a.D or t["pb"] >= a.O)))]
if any(t["speed"] is not None for t in T):
    for s in a.speeds:
        rules.append((f"speed only >= {s:.0f} px/s", lambda t, s=s: t["speed"] is not None and t["speed"] >= s))
    for s in a.speeds:
        rules.append((f"X-CLIP + speed >= {s:.0f}", lambda t, s=s: xclip(t) and t["speed"] is not None and t["speed"] >= s))
print(f"{'rule':34s} | {'AI bic':>6} {'MAE bic':>7} {'bins+-1':>7} | {'AI ped':>6} {'MAE ped':>7} | {'MAE sum':>7}")
for name, rule in rules:
    sb, mb, w1, spd, mp = evaluate(rule)
    print(f"{name:34s} | {sb:6d} {mb:7.2f} {w1:7.0%} | {spd:6d} {mp:7.2f} | {mb + mp:7.2f}")

if a.show_fused:
    f_rule = rules[4][1]
    print("\ntracks whose label differs between X-CLIP only and the fused rule:")
    print("run chunk first_seen  secs | det% P(bic) speed | X-CLIP only -> fused")
    for t in T:
        if xclip(t) != f_rule(t):
            sv = "n/a" if t["speed"] is None else f"{t['speed']:.0f}"
            print(f"{t['run']} {t['chunk']}  {t['t']} {t['secs']:5.1f} | {t['dp']:4.0f} {t['pb']:6.2f} {sv:>5} | "
                  f"{'BICYCLIST' if xclip(t) else 'PEDESTRIAN'} -> {'BICYCLIST' if f_rule(t) else 'PEDESTRIAN'}")
