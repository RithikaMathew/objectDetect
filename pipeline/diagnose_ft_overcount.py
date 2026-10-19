"""
Diagnose fine-tuned Colonial overcount vs COCO baseline from existing track CSVs.

No GPU needed — reads pilot_output/sessions/*/ *_tracks.csv and prints
confidence / excursion / day-night tables for the methods section.

Usage:
    python diagnose_ft_overcount.py \\
        --ft-dir pilot_output/sessions/BL_Colonial_2019-07-10_ft \\
        --coco-dir pilot_output/sessions/BL_Colonial_2019-07-10

    # FT only if baseline dir missing:
    python diagnose_ft_overcount.py --ft-dir pilot_output/sessions/BL_Colonial_2019-07-10_ft
"""

from __future__ import annotations

import argparse
import csv
import glob
import os
import re
import statistics as st
from collections import Counter, defaultdict

from validate_counts import NIGHT_END, NIGHT_START, VIDEO_LIST, load_chunk_times

CYCLIST_CLASSES = ("cyclist", "bicycle")


def _pctile(xs, p):
    if not xs:
        return float("nan")
    ys = sorted(xs)
    i = min(len(ys) - 1, max(0, int(round(p * (len(ys) - 1)))))
    return ys[i]


def _summarize(xs, label):
    if not xs:
        print(f"  {label}: (none)")
        return
    print(f"  {label}: n={len(xs)}  median={st.median(xs):.3f}  "
          f"mean={st.mean(xs):.3f}  p10={_pctile(xs, 0.10):.3f}  "
          f"p90={_pctile(xs, 0.90):.3f}")


def _is_night_hour(hh):
    return hh >= NIGHT_START or hh < NIGHT_END


def load_counted_cyclists(session_dir, chunk_times):
    """Return list of dicts for counted cyclist tracks with wall-clock hour if known."""
    rows = []
    files = sorted(glob.glob(os.path.join(session_dir, "*_tracks.csv")))
    for path in files:
        chunk = os.path.basename(path).replace("_tracks.csv", "")
        hour = None
        if chunk in chunk_times:
            hour = chunk_times[chunk][1]
        else:
            # Fallback: ...0000.018 -> assume .001 = 05:00 => hour = 4 + index
            m = re.search(r"\.(\d{3})$", chunk)
            if m:
                hour = (4 + int(m.group(1))) % 24
        with open(path) as f:
            for r in csv.DictReader(f):
                if r["class"] not in CYCLIST_CLASSES:
                    continue
                counted = r["counted"] == "yes"
                rows.append({
                    "chunk": chunk,
                    "hour": hour,
                    "night": _is_night_hour(hour) if hour is not None else None,
                    "counted": counted,
                    "track_id": r["track_id"],
                    "mean_conf": float(r["mean_conf"]),
                    "max_conf": float(r["max_conf"]),
                    "excursion": float(r["max_excursion_diag"]),
                    "hits": int(r["hits"]),
                    "first_t": float(r["first_t"]),
                    "last_t": float(r["last_t"]),
                })
    return rows


# Mirror of pilot_detect_v2 FT gates (keep in sync when retuning).
# Window QA: 0.65/0.32/1.5s missed the real cyclist → loosened for recall.
FT_GATE = {
    "min_seconds": 1.0,
    "max_conf": 0.60,
    "mean_conf": 0.28,
    "night_mean_extra": 0.07,
    "min_excursion": 0.75,
}
# Counting runs use --stride 5; duration from first_t/last_t is enough offline.


def simulate_ft_gates(counted, gate=None, label="FT-gate"):
    """Apply FT gates to previously counted tracks (upper bound on new total)."""
    g = gate or FT_GATE
    keep, reasons = [], Counter()
    for r in counted:
        ok, why = would_pass_ft_gates(r, g)
        if ok:
            keep.append(r)
        else:
            reasons[why] += 1
    day = sum(1 for r in keep if r["night"] is False)
    night = sum(1 for r in keep if r["night"] is True)
    print(f"  offline {label} simulation on current counted set:")
    print(f"    would keep {len(keep)} / {len(counted)}  "
          f"(day={day} night={night})")
    if reasons:
        print(f"    reject reasons: {dict(reasons)}")
    print(f"    (approx — real re-run also changes fusion/track formation; "
          f"gates: max>={g['max_conf']} mean>={g['mean_conf']} "
          f"night_mean>={g['mean_conf']+g['night_mean_extra']} "
          f"min_s>={g['min_seconds']})")
    return len(keep), day, night


def sweep_ft_gates(counted):
    """Try a few gate combos so methods can cite the chosen operating point."""
    combos = [
        {"min_seconds": 1.0, "max_conf": 0.60, "mean_conf": 0.28,
         "night_mean_extra": 0.07, "min_excursion": 0.75},  # default after miss
        {"min_seconds": 1.5, "max_conf": 0.65, "mean_conf": 0.32,
         "night_mean_extra": 0.08, "min_excursion": 0.75},  # missed cyclist
        {"min_seconds": 1.0, "max_conf": 0.70, "mean_conf": 0.40,
         "night_mean_extra": 0.10, "min_excursion": 0.75},
    ]
    print("  gate sweep (offline on counted set; target ~89, night < day):")
    print(f"    {'max':>5} {'mean':>5} {'nite+':>5} {'keep':>5} "
          f"{'day':>4} {'night':>5}  note")
    for g in combos:
        n, d, ni = 0, 0, 0
        for r in counted:
            ok, _ = would_pass_ft_gates(r, g)
            if ok:
                n += 1
                if r["night"] is False:
                    d += 1
                elif r["night"] is True:
                    ni += 1
        mark = ""
        if (g["max_conf"] == FT_GATE["max_conf"]
                and g["mean_conf"] == FT_GATE["mean_conf"]
                and g["night_mean_extra"] == FT_GATE["night_mean_extra"]
                and g["min_seconds"] == FT_GATE["min_seconds"]):
            mark = " <-- default"
        elif g["max_conf"] == 0.65:
            mark = " (missed cyclist on window)"
        elif g["mean_conf"] == 0.40:
            mark = " (first draft, too strict)"
        print(f"    {g['max_conf']:5.2f} {g['mean_conf']:5.2f} "
              f"{g['night_mean_extra']:5.2f} {n:5d} {d:4d} {ni:5d}{mark}")


def would_pass_ft_gates(r, gate=None):
    """Offline: would this already-counted track pass the new FT profile?"""
    g = gate or FT_GATE
    dur = max(0.0, r["last_t"] - r["first_t"])
    if dur < g["min_seconds"]:
        return False, "too_short"
    if r["max_conf"] < g["max_conf"]:
        return False, "low_max_conf"
    mean_floor = g["mean_conf"]
    if r["night"]:
        mean_floor += g["night_mean_extra"]
    if r["mean_conf"] < mean_floor:
        return False, "low_mean_conf"
    if r["excursion"] < g["min_excursion"]:
        return False, "static"
    return True, "ok"


def diagnose_session(name, session_dir, chunk_times, top_chunks=8,
                     simulate_gates=False):
    if not os.path.isdir(session_dir):
        print(f"\n=== {name} === MISSING {session_dir}")
        return None
    rows = load_counted_cyclists(session_dir, chunk_times)
    counted = [r for r in rows if r["counted"]]
    rejected = [r for r in rows if not r["counted"]]
    print(f"\n=== {name} ({session_dir}) ===")
    print(f"  cyclist-class tracks: {len(rows)}  "
          f"counted={len(counted)}  rejected={len(rejected)}")

    _summarize([r["mean_conf"] for r in counted], "counted mean_conf")
    _summarize([r["max_conf"] for r in counted], "counted max_conf")
    _summarize([r["excursion"] for r in counted], "counted max_excursion")

    day = [r for r in counted if r["night"] is False]
    night = [r for r in counted if r["night"] is True]
    print(f"  counted day={len(day)}  night={len(night)}")
    _summarize([r["mean_conf"] for r in day], "day mean_conf")
    _summarize([r["mean_conf"] for r in night], "night mean_conf")

    # Suggested gate: sit above night FP mass if night mean is high
    if night:
        night_means = sorted(r["mean_conf"] for r in night)
        print(f"  suggested FT MIN_TRACK_MEAN_CONF >= "
              f"{_pctile(night_means, 0.50):.2f} (night median) to "
              f"{_pctile(night_means, 0.75):.2f} (night p75) — tune after clip review")

    if simulate_gates and counted:
        simulate_ft_gates(counted)
        sweep_ft_gates(counted)

    by_chunk = Counter(r["chunk"] for r in counted)
    print(f"  top counted chunks:")
    for chunk, n in by_chunk.most_common(top_chunks):
        hh = next((r["hour"] for r in counted if r["chunk"] == chunk), None)
        tag = ""
        if hh is not None:
            tag = f"  hour={hh:02d}:00" + ("  NIGHT" if _is_night_hour(hh) else "  day")
        print(f"    {chunk}: n={n}{tag}")

    # Sample tracks for clip review: densest night chunks, mid-span first_t
    review = []
    night_chunks = [c for c, _ in by_chunk.most_common(20)
                    if any(r["chunk"] == c and r["night"] for r in counted)]
    for chunk in night_chunks[:3]:
        cand = [r for r in counted if r["chunk"] == chunk]
        cand.sort(key=lambda r: -r["mean_conf"])
        review.extend(cand[:5])
    if review:
        print(f"  clip-review candidates (high mean_conf counted, night-heavy):")
        for r in review[:15]:
            print(f"    {r['chunk']} id={r['track_id']}  "
                  f"t={r['first_t']:.0f}-{r['last_t']:.0f}s  "
                  f"mean={r['mean_conf']:.2f} max={r['max_conf']:.2f}  "
                  f"exc={r['excursion']:.1f}")
    return {
        "counted": len(counted),
        "day": len(day),
        "night": len(night),
        "mean_conf_median": st.median([r["mean_conf"] for r in counted]) if counted else None,
        "night_mean_median": st.median([r["mean_conf"] for r in night]) if night else None,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ft-dir", default="pilot_output/sessions/BL_Colonial_2019-07-10_ft")
    ap.add_argument("--coco-dir", default="pilot_output/sessions/BL_Colonial_2019-07-10")
    ap.add_argument("--video-list", default=VIDEO_LIST)
    ap.add_argument("--simulate-ft-gates", action="store_true",
                    help="Apply proposed FT confirmation gates to the FT counted "
                         "set (offline upper-bound estimate of the recount).")
    args = ap.parse_args()

    chunk_times = load_chunk_times(args.video_list)
    print(f"Loaded {len(chunk_times)} chunk wall-clock times from {args.video_list}")
    print(f"Night window: {NIGHT_START}:00–{NIGHT_END:02d}:00")

    ft = diagnose_session("FINE-TUNED", args.ft_dir, chunk_times,
                          simulate_gates=args.simulate_ft_gates)
    coco = diagnose_session("COCO baseline", args.coco_dir, chunk_times)

    print("\n=== Comparison ===")
    if ft and coco:
        print(f"  counted  FT={ft['counted']}  COCO={coco['counted']}  "
              f"(GT Colonial North = 89)")
        print(f"  night share  FT={ft['night']}/{ft['counted']}  "
              f"COCO={coco['night']}/{coco['counted']}")
        if ft["mean_conf_median"] is not None and coco["mean_conf_median"] is not None:
            print(f"  counted mean_conf median  FT={ft['mean_conf_median']:.3f}  "
                  f"COCO={coco['mean_conf_median']:.3f}")
    print("\nNEXT: render night peak chunks (.018 / .022 / .046) with "
          "plan_ft_review_clips.py + run_ft_review.slurm, score REAL vs FP, "
          "then pilot with run_ft_pilot_chunks.slurm and full OUTDIR=_ft_v2.")


if __name__ == "__main__":
    main()
