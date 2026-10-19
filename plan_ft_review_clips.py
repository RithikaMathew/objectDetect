"""
Plan short render windows for FT overcount clip review.

Priority chunks from the Colonial FT recount (1445 vs 89):
  .018 (~22:00, n=129), .022 / .046 (~02:00), one day chunk (.010).

For each chunk, pick the densest ~window_sec span of counted cyclist
first_t starts, then emit clip lines for run_ft_review.slurm.

Also writes a blank score sheet (REAL / FP / notes) for ~15–20 tracks.

Usage:
    python plan_ft_review_clips.py \\
        --session-dir pilot_output/sessions/BL_Colonial_2019-07-10_ft \\
        --video-dir "pilot_clips/MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/Standard_SCU8OG_2019-07-10_0000"
"""

from __future__ import annotations

import argparse
import csv
import glob
import os
import re
from collections import defaultdict

DEFAULT_CHUNKS = ("018", "022", "046", "010")  # night peaks + day sanity
CYCLIST_CLASSES = ("cyclist", "bicycle")


def _chunk_suffix(name):
    m = re.search(r"\.(\d{3})$", name)
    return m.group(1) if m else None


def densest_window(starts, window_sec):
    """Return (start, end) covering the most track start times."""
    if not starts:
        return 0.0, float(window_sec)
    xs = sorted(starts)
    best_i, best_n = 0, 0
    j = 0
    for i, t0 in enumerate(xs):
        while j < len(xs) and xs[j] < t0 + window_sec:
            j += 1
        n = j - i
        if n > best_n:
            best_n, best_i = n, i
    t0 = xs[best_i]
    return max(0.0, t0 - 5.0), t0 + window_sec + 5.0


def load_counted(session_dir, suffixes):
    by_suf = defaultdict(list)
    for path in sorted(glob.glob(os.path.join(session_dir, "*_tracks.csv"))):
        chunk = os.path.basename(path).replace("_tracks.csv", "")
        suf = _chunk_suffix(chunk)
        if suf not in suffixes:
            continue
        with open(path) as f:
            for r in csv.DictReader(f):
                if r["class"] not in CYCLIST_CLASSES or r["counted"] != "yes":
                    continue
                by_suf[suf].append({
                    "chunk": chunk,
                    "track_id": r["track_id"],
                    "first_t": float(r["first_t"]),
                    "last_t": float(r["last_t"]),
                    "mean_conf": float(r["mean_conf"]),
                    "max_conf": float(r["max_conf"]),
                    "hits": int(r["hits"]),
                })
    return by_suf


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--session-dir", required=True)
    ap.add_argument("--video-dir", required=True)
    ap.add_argument("--chunks", default=",".join(DEFAULT_CHUNKS),
                    help="Comma-separated chunk suffixes, e.g. 018,022,046,010")
    ap.add_argument("--window-sec", type=float, default=180.0,
                    help="Render window length around densest starts (default 3 min).")
    ap.add_argument("--tracks-per-chunk", type=int, default=5,
                    help="How many counted tracks to list on the score sheet / "
                         "per-track clip lines (default 5 → ~20 total).")
    ap.add_argument("--out", default="ft_review_clips.txt")
    ap.add_argument("--score-sheet", default="ft_review_score_sheet.csv")
    args = ap.parse_args()

    suffixes = tuple(s.strip().zfill(3) for s in args.chunks.split(",") if s.strip())
    by_suf = load_counted(args.session_dir, set(suffixes))

    window_lines = []   # one dense window per chunk (watch these first)
    track_lines = []    # optional per-track pads
    score_rows = []

    for suf in suffixes:
        tracks = by_suf.get(suf, [])
        if not tracks:
            print(f"  WARNING: no counted cyclists for .{suf}")
            continue
        chunk = tracks[0]["chunk"]
        mp4 = os.path.join(args.video_dir, chunk + ".mp4")
        if not os.path.exists(mp4):
            print(f"  WARNING: missing video {mp4}")
            continue

        starts = [t["first_t"] for t in tracks]
        w0, w1 = densest_window(starts, args.window_sec)
        in_win = [t for t in tracks if w0 <= t["first_t"] <= w1]
        label = (f"FT_REVIEW .{suf} dense_window n_counted={len(tracks)} "
                 f"in_window={len(in_win)}")
        window_lines.append(f"{mp4}|{w0:.2f}|{w1:.2f}|{label}")
        print(f"  .{suf}: {len(tracks)} counted → window "
              f"{w0:.0f}-{w1:.0f}s ({len(in_win)} starts)")

        # Score the highest-mean_conf tracks that start in the window
        ranked = sorted(in_win or tracks, key=lambda t: -t["mean_conf"])
        for t in ranked[: args.tracks_per_chunk]:
            pad0 = max(0.0, t["first_t"] - 2.5)
            pad1 = t["last_t"] + 2.5
            tlab = (f"TRACK .{suf} #{t['track_id']} mean={t['mean_conf']:.2f} "
                    f"max={t['max_conf']:.2f} hits={t['hits']}")
            track_lines.append(f"{mp4}|{pad0:.2f}|{pad1:.2f}|{tlab}")
            score_rows.append({
                "chunk": chunk,
                "suffix": suf,
                "track_id": t["track_id"],
                "first_t": f"{t['first_t']:.1f}",
                "last_t": f"{t['last_t']:.1f}",
                "mean_conf": f"{t['mean_conf']:.3f}",
                "max_conf": f"{t['max_conf']:.3f}",
                "hits": t["hits"],
                "verdict": "",  # REAL / FP_light / FP_grass / FP_car / FP_other / UNSURE
                "notes": "",
            })

    # Dense windows first (4 clips), then optional per-track (reviewer choice)
    lines = window_lines + track_lines
    with open(args.out, "w") as f:
        f.write("\n".join(lines) + ("\n" if lines else ""))

    fields = ["chunk", "suffix", "track_id", "first_t", "last_t",
              "mean_conf", "max_conf", "hits", "verdict", "notes"]
    with open(args.score_sheet, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(score_rows)

    print(f"\nWrote {args.out}  ({len(window_lines)} dense windows + "
          f"{len(track_lines)} track clips)")
    print(f"Wrote {args.score_sheet}  ({len(score_rows)} rows to score)")
    print("Verdict codes: REAL | FP_light | FP_grass | FP_car | FP_other | UNSURE")
    if lines:
        n = len(lines) - 1
        print(f"\nSubmit dense windows only (recommended first):")
        print(f"  CLIPS={args.out} OUTDIR=pilot_output/ft_review \\")
        print(f"    sbatch --array=0-{len(window_lines)-1} run_ft_review.slurm")
        print(f"  # or all lines: --array=0-{n}")


if __name__ == "__main__":
    main()
