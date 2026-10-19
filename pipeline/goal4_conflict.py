"""Cyclist-vehicle pairs: minimum separation, constant-velocity TTC, and PET.

Thresholds follow the literature review: TTC under 1.5 s, PET under 1.0 s.
Meters use Goal 3's prior-calibrated scale when a facility scale exists.
Otherwise distance is left in pixels and meters are blank.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict

import numpy as np

TTC_S = 1.5
PET_S = 1.0
# PET is only a conflict when the paths actually come this close.
CONFLICT_RADIUS_M = 5.0
CONFLICT_RADIUS_PX = 120.0


def _load(points_csv):
    by = defaultdict(list)
    cls = {}
    with open(points_csv) as f:
        for r in csv.DictReader(f):
            tid = int(r["track_id"])
            cls[tid] = r["class"]
            by[tid].append((float(r["t"]), float(r["x"]), float(r["y"])))
    for tid in by:
        by[tid].sort()
    return by, cls


def _at(samples, t):
    if t < samples[0][0] or t > samples[-1][0]:
        return None
    for i in range(1, len(samples)):
        t0, x0, y0 = samples[i - 1]
        t1, x1, y1 = samples[i]
        if t0 <= t <= t1:
            a = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
            return (x0 + a * (x1 - x0), y0 + a * (y1 - y0))
    return None


def _vel(samples, t):
    for i in range(1, len(samples)):
        if samples[i - 1][0] <= t <= samples[i][0]:
            dt = samples[i][0] - samples[i - 1][0]
            if dt <= 1e-3:
                return (0.0, 0.0)
            return ((samples[i][1] - samples[i - 1][1]) / dt,
                    (samples[i][2] - samples[i - 1][2]) / dt)
    return (0.0, 0.0)


def write_conflicts(points_csv, facility_by_id, speed_by_id, out_path):
    paths, cls = _load(points_csv)
    cyclists = [i for i, c in cls.items() if c in ("cyclist", "bicycle")]
    vehicles = [i for i, c in cls.items() if c in ("car", "bus", "truck", "other_vehicle")]
    rows = []
    for cid in cyclists:
        cp = paths[cid]
        if len(cp) < 2:
            continue
        for vid in vehicles:
            vp = paths[vid]
            if len(vp) < 2:
                continue
            lo = max(cp[0][0], vp[0][0])
            hi = min(cp[-1][0], vp[-1][0])
            if hi - lo < 0.2:
                continue
            times = [t for t, _x, _y in cp if lo <= t <= hi]
            best = None
            min_ttc = None
            for t in times:
                p = _at(vp, t)
                if p is None:
                    continue
                dist = float(np.hypot(cp_x(cp, t)[0] - p[0], cp_x(cp, t)[1] - p[1]))
                if best is None or dist < best[0]:
                    best = (dist, t)
                cv, vv = _vel(cp, t), _vel(vp, t)
                cx, cy = cp_x(cp, t)
                rel = np.array([p[0] - cx, p[1] - cy])
                rel_v = np.array([vv[0] - cv[0], vv[1] - cv[1]])
                rn = float(np.linalg.norm(rel))
                if rn < 1.0:
                    min_ttc = 0.0
                    continue
                closing = -float(np.dot(rel, rel_v)) / rn
                if closing > 1.0:
                    ttc = rn / closing
                    if min_ttc is None or ttc < min_ttc:
                        min_ttc = ttc
            if best is None:
                continue
            dist_px, t_c = best
            # PET: when the vehicle is closest to where the cyclist was at t_c.
            cx, cy = cp_x(cp, t_c)
            t_v, d_v = None, None
            for t, x, y in vp:
                d = float(np.hypot(x - cx, y - cy))
                if d_v is None or d < d_v:
                    d_v, t_v = d, t
            pet = abs(t_v - t_c) if t_v is not None else None
            info = speed_by_id.get(cid) or {}
            m = info.get("m_per_px")
            dist_m = dist_px * m if m else None
            if m:
                pet_close = d_v is not None and d_v * m <= CONFLICT_RADIUS_M
            else:
                pet_close = d_v is not None and d_v <= CONFLICT_RADIUS_PX
            fac = (facility_by_id.get(cid) or {}).get("facility", "")
            rows.append({
                "cyclist_id": cid,
                "vehicle_id": vid,
                "facility": fac,
                "min_dist_px": f"{dist_px:.1f}",
                "min_dist_m": "" if dist_m is None else f"{dist_m:.2f}",
                "min_ttc_s": "" if min_ttc is None else f"{min_ttc:.2f}",
                "pet_s": "" if pet is None else f"{pet:.2f}",
                "high_risk": "yes" if (
                    (min_ttc is not None and min_ttc < TTC_S)
                    or (pet is not None and pet < PET_S and pet_close)
                ) else "no",
            })
    fields = ["cyclist_id", "vehicle_id", "facility", "min_dist_px", "min_dist_m",
              "min_ttc_s", "pet_s", "high_risk"]
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    n_risk = sum(1 for r in rows if r["high_risk"] == "yes")
    print(f"conflicts: {len(rows)} pairs, {n_risk} under TTC<{TTC_S}s or PET<{PET_S}s -> {out_path}")
    return rows


def cp_x(samples, t):
    p = _at(samples, t)
    return p if p is not None else (samples[0][1], samples[0][2])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("points_csv")
    ap.add_argument("--facility-csv", default=None)
    ap.add_argument("--speed-csv", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    fac, spd = {}, {}
    if args.facility_csv:
        with open(args.facility_csv) as f:
            for r in csv.DictReader(f):
                fac[int(r["track_id"])] = r
    if args.speed_csv:
        with open(args.speed_csv) as f:
            for r in csv.DictReader(f):
                m = r.get("m_per_px") or ""
                spd[int(r["track_id"])] = {
                    "m_per_px": float(m) if m not in ("", "None") else None
                }
    out = args.out or args.points_csv.replace("_points.csv", "_conflicts.csv")
    write_conflicts(args.points_csv, fac, spd, out)


if __name__ == "__main__":
    main()
