#!/usr/bin/env python3
"""
aggregate_results.py

Collects the outputs of bike_ped_compare_v1.py and xclip_overlay_v2.py into ONE
short text report you can paste into chat (also saved to --report).
Only reads existing files; runs on the login node, no GPU.

    python aggregate_results.py
    python aggregate_results.py --truth 1=pedestrian 2=bicyclist   # if you know ids
"""
import argparse
import csv
import glob
import os
import re
from collections import defaultdict

import numpy as np


def read_csv(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def latest(pattern):
    files = sorted(glob.glob(pattern), key=os.path.getmtime)
    return files[-1] if files else None


def grab(log, start, stop_re=None, max_lines=40):
    """Lines of a log from the line containing `start` until a blank line."""
    if not log:
        return []
    out, on = [], False
    with open(log, errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if start in line:
                on, out = True, []
            if on:
                if not line.strip() and out:
                    break
                out.append(line)
                if len(out) >= max_lines:
                    break
    return out


def grep(log, pat):
    if not log:
        return []
    r = re.compile(pat)
    with open(log, errors="replace") as f:
        return [l.rstrip("\n") for l in f if r.search(l)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--compare-dir",
                    default="pilot_output/compare_v4/bike_ped_compare_v1")
    ap.add_argument("--overlay-scores",
                    default="pilot_output/compare_v4/xclip_overlay_v2/overlay_scores.csv")
    ap.add_argument("--diag-csv",
                    default="pilot_output/compare_v4/track_j_diagnostic.csv")
    ap.add_argument("--logs", default="logs")
    ap.add_argument("--truth", nargs="*", default=[],
                    help="tracker_id=class for the COMPARE tracks, e.g. 1=pedestrian 2=bicyclist")
    ap.add_argument("--report", default="aggregate_report.txt")
    args = ap.parse_args()

    L = []
    P = L.append

    # ---------- 1. xclip_overlay_v2 ----------
    P("=" * 70)
    P("A. xclip_overlay_v2 (YOLO + X-CLIP)")
    P("=" * 70)
    ov_log = latest(os.path.join(args.logs, "xclip_overlay_v2_*.log"))
    P(f"log: {ov_log}")
    for l in grab(ov_log, "=== person tracks ==="):
        P(l)
    for l in grep(ov_log, r"Final counts|WARNING|ERROR|Traceback"):
        P(l)
    if os.path.exists(args.overlay_scores):
        rows = read_csv(args.overlay_scores)
        by = defaultdict(list)
        for r in rows:
            by[int(r["tracker_id"])].append(r)
        P("")
        P("per-track score summary (from overlay_scores.csv)")
        P("track | scores | first-last frame | mean bicyclist_smooth | %updates labeled BICYCLIST")
        for tid in sorted(by):
            rs = by[tid]
            sm = np.array([float(r["bicyclist_smooth"]) for r in rs])
            frs = [int(r["frame"]) for r in rs]
            P(f"{tid:5d} | {len(rs):6d} | {min(frs)}-{max(frs)} | "
              f"{sm.mean():.2f} | {100 * (sm >= 0.5).mean():.0f}%")
        long_tracks = [t for t in by if len(by[t]) >= 5]
        P(f"tracks with >=5 score updates: {sorted(long_tracks)}")
    else:
        P(f"(missing {args.overlay_scores})")

    # ---------- 2. compare_v1 ----------
    P("")
    P("=" * 70)
    P("B. bike_ped_compare_v1 (per-backend)")
    P("=" * 70)
    cmp_log = latest(os.path.join(args.logs, "bike_ped_compare_*.log"))
    P(f"log: {cmp_log}")
    for l in grep(cmp_log, r"thresholds on p_bike|matched|ERROR|Traceback"):
        P(l)
    for l in grab(cmp_log, "=== summary ==="):
        P(l)
    truth = {}
    for kv in args.truth:
        k, v = kv.split("=")
        truth[int(k)] = v.lower()
    for path in sorted(glob.glob(os.path.join(args.compare_dir, "*_scores.csv"))):
        name = os.path.basename(path).replace("_scores.csv", "")
        rows = read_csv(path)
        by = defaultdict(list)
        for r in rows:
            by[int(r["tracker_id"])].append(float(r["p_bike_smooth"]))
        P("")
        P(f"[{name}] track: n_updates, mean p_bike_smooth, %>=0.5 (thr differs per backend, see above)")
        for tid in sorted(by):
            v = np.array(by[tid])
            tag = f"  truth={truth[tid]}" if tid in truth else ""
            P(f"  {tid}: n={len(v)} mean={v.mean():.2f} min={v.min():.2f} "
              f"max={v.max():.2f} >=0.5:{100 * (v >= 0.5).mean():.0f}%{tag}")

    # ---------- 3. input tracks ----------
    P("")
    P("=" * 70)
    P("C. input CSV tracks (track_j_diagnostic.csv)")
    P("=" * 70)
    if os.path.exists(args.diag_csv):
        by = defaultdict(list)
        for r in read_csv(args.diag_csv):
            by[int(r["tracker_id"])].append(int(r["frame"]))
        P("track | rows | first-last frame")
        for tid in sorted(by):
            P(f"{tid:5d} | {len(by[tid]):4d} | {min(by[tid])}-{max(by[tid])}")
    else:
        P(f"(missing {args.diag_csv})")

    text = "\n".join(L)
    print(text)
    with open(args.report, "w") as f:
        f.write(text + "\n")
    print(f"\n[saved to {args.report} -- paste it or upload it]")


if __name__ == "__main__":
    main()
