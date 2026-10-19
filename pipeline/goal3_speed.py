"""Ground-contact speed, scaled so the sample median matches the stopwatch prior.

Priors are the hand-timed means (mph) by facility. The scale is meters per
pixel, fit per facility. Both px/s and mph are reported. mph is prior-calibrated,
not a surveyed homography.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict

import numpy as np

PRIORS_MPH = {
    "bike_lane": 11.8,
    "sidewalk": 9.3,
    "travel_lane": 14.5,
    "path": 11.8,
}
MPH_PER_MPS = 2.23694
# Savitzky-Golay, window 5, polynomial 2.
_SG = np.array([-3, 12, 17, 12, -3], dtype=float) / 35.0


def _smooth(xs):
    if len(xs) < 5:
        return list(xs)
    out = []
    for i in range(len(xs)):
        if i < 2 or i >= len(xs) - 2:
            out.append(float(xs[i]))
        else:
            out.append(float(np.dot(_SG, xs[i - 2:i + 3])))
    return out


def _tracks(points_csv):
    by = defaultdict(list)
    with open(points_csv) as f:
        for r in csv.DictReader(f):
            if r["class"] not in ("cyclist", "bicycle"):
                continue
            by[int(r["track_id"])].append(
                (float(r["t"]), float(r["x"]), float(r["y"])))
    return by


def _px_per_s(samples):
    samples = sorted(samples)
    if len(samples) < 2:
        return None
    ts = [s[0] for s in samples]
    xs = _smooth([s[1] for s in samples])
    ys = _smooth([s[2] for s in samples])
    speeds = []
    for i in range(1, len(samples)):
        dt = ts[i] - ts[i - 1]
        if dt <= 1e-3:
            continue
        speeds.append(float(np.hypot(xs[i] - xs[i - 1], ys[i] - ys[i - 1]) / dt))
    if not speeds:
        return None
    return float(np.median(speeds))


def speed_by_track(points_csv, facility_by_id):
    raw = {}
    for tid, samples in _tracks(points_csv).items():
        v = _px_per_s(samples)
        if v is None or v < 1.0:
            continue
        fac = (facility_by_id.get(tid) or {}).get("facility", "unknown")
        raw[tid] = {"px_s": v, "facility": fac, "mph": None, "m_per_px": None}
    by_fac = defaultdict(list)
    for tid, info in raw.items():
        if info["facility"] in PRIORS_MPH:
            by_fac[info["facility"]].append(info["px_s"])
    scale = {}
    for fac, speeds in by_fac.items():
        med = float(np.median(speeds))
        if med > 1.0:
            scale[fac] = PRIORS_MPH[fac] / (med * MPH_PER_MPS)
    for info in raw.values():
        m = scale.get(info["facility"])
        if m:
            info["m_per_px"] = m
            info["mph"] = info["px_s"] * m * MPH_PER_MPS
    return raw


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("points_csv")
    ap.add_argument("--facility-csv", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    fac = {}
    if args.facility_csv:
        with open(args.facility_csv) as f:
            for r in csv.DictReader(f):
                fac[int(r["track_id"])] = r
    speeds = speed_by_track(args.points_csv, fac)
    out = args.out or args.points_csv.replace("_points.csv", "_speed.csv")
    rows = [{"track_id": tid, **{k: (f"{v:.3f}" if isinstance(v, float) else v)
                                 for k, v in info.items()}}
            for tid, info in sorted(speeds.items())]
    if rows:
        with open(out, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    print(f"speeds: {len(rows)} tracks -> {out}")
    for r in rows[:12]:
        print(f"  #{r['track_id']} {r['facility']} {r['px_s']} px/s  mph={r['mph']}")


if __name__ == "__main__":
    main()
