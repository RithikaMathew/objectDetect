"""Assign each track a facility from the ground-contact point.

Zones are fractional polygons (one static mask per camera). A hit counts for
the zone that contains (x_frac, y_frac). The track label is the zone with at
least `majority` of its hits (default 0.85). A second zone with a real share
is recorded as a transition.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict


def _inside(x, y, poly):
    n = len(poly)
    c = False
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-9) + xi):
            c = not c
        j = i
    return c


def load_zones(path):
    with open(path) as f:
        spec = json.load(f)
    return spec["zones"], float(spec.get("majority", 0.85))


def label_tracks(points_csv, zones_path):
    zones, majority = load_zones(zones_path)
    by_id = defaultdict(list)
    cls = {}
    with open(points_csv) as f:
        for r in csv.DictReader(f):
            tid = int(r["track_id"])
            cls[tid] = r["class"]
            by_id[tid].append((float(r["x_frac"]), float(r["y_frac"]), float(r["t"])))
    out = {}
    for tid, pts in by_id.items():
        if cls.get(tid) not in ("cyclist", "bicycle"):
            continue
        hits = Counter()
        for x, y, _t in pts:
            for z in zones:
                if _inside(x, y, z["polygon"]):
                    hits[z["name"]] += 1
                    break
            else:
                hits["unknown"] += 1
        n = sum(hits.values()) or 1
        ranked = hits.most_common()
        top, top_n = ranked[0]
        frac = top_n / n
        facility = top if frac >= majority else "mixed"
        transition = ""
        if len(ranked) > 1 and ranked[1][1] / n >= (1.0 - majority):
            transition = ranked[1][0]
        out[tid] = {"facility": facility, "fraction": round(frac, 3),
                    "transition": transition, "n": n}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("points_csv")
    ap.add_argument("--zones", default="data/zones/colonial.json")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    labels = label_tracks(args.points_csv, args.zones)
    rows = [{"track_id": tid, **info} for tid, info in sorted(labels.items())]
    out = args.out or args.points_csv.replace("_points.csv", "_facility.csv")
    if rows:
        with open(out, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    print(f"facility labels: {len(rows)} cyclist tracks -> {out}")
    for r in rows[:12]:
        print(f"  #{r['track_id']} {r['facility']} ({r['fraction']})"
              + (f" transition->{r['transition']}" if r["transition"] else ""))


if __name__ == "__main__":
    main()
