"""Resolution gate for rider characteristics.

No age or gender model is trained: this footage has no demographic labels.
A cyclist whose median box height is under 40 px is marked unknown. Taller
boxes are marked estimable, which is the only hook a later classifier gets.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict

MIN_HEIGHT_PX = 40.0


def resolution_by_track(points_csv, min_height=MIN_HEIGHT_PX):
    heights = defaultdict(list)
    classes = {}
    with open(points_csv) as f:
        for r in csv.DictReader(f):
            if r["class"] not in ("cyclist", "bicycle"):
                continue
            tid = int(r["track_id"])
            classes[tid] = r["class"]
            try:
                heights[tid].append(float(r["box_h"]))
            except ValueError:
                continue
    out = {}
    for tid, hs in heights.items():
        if not hs:
            continue
        hs = sorted(hs)
        med = hs[len(hs) // 2]
        out[tid] = {
            "median_box_h": round(med, 1),
            "status": "estimable" if med >= min_height else "unknown",
        }
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("points_csv")
    ap.add_argument("--min-height", type=float, default=MIN_HEIGHT_PX)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    labels = resolution_by_track(args.points_csv, args.min_height)
    out = args.out or args.points_csv.replace("_points.csv", "_resolution.csv")
    rows = [{"track_id": tid, **info} for tid, info in sorted(labels.items())]
    if rows:
        with open(out, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    n_ok = sum(1 for r in rows if r["status"] == "estimable")
    print(f"resolution: {n_ok}/{len(rows)} cyclist tracks estimable "
          f"(height >= {args.min_height:.0f}px) -> {out}")


if __name__ == "__main__":
    main()
