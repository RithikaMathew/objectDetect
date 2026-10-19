"""
Triage the counted cyclist tracks from their metadata alone.

Watching 88 clips takes an evening. Most of the diagnosis does not need video:
the tracks CSVs already record duration, hit count, confidence and how far each
track travelled, and the implausible ones stand out numerically. This ranks
every counted cyclist by how suspicious it is, so clip review starts with the
tracks most likely to be wrong instead of with chunk .001.

Three failure modes it detects, each with a distinct signature:

  DUPLICATE   two counted tracks in the same chunk overlapping in time. One
              rider counted twice. Already confirmed present: #21742 and
              #21788 in chunk .011 overlap by 0.8s of a 1.2s track.

  STATIC      a "cyclist" that barely moved. A real crossing travels tens of
              box-diagonals (35.3, 97.3 in the observed sample); a track with
              an excursion of 1-3 diagonals over 15-20s is a person standing
              with a bike, a parked bike plus a pedestrian, or a stationary
              false positive.

  ID JUMP     an implausibly LARGE excursion. 97 diagonals for a ~30px box is
              ~2900px of travel in a 720px-wide frame -- crossing it four times
              in 4.5s. More likely the track identity jumped between objects,
              which inflates one track's evidence while destroying another's.

Usage:
    python audit_tracks.py --session-dir pilot_output/sessions/BL_Colonial_2019-07-10
"""

import argparse
import csv
import glob
import os
import re
from collections import defaultdict

CYCLIST_CLASSES = ("cyclist", "bicycle")
VIDEO_LIST = "data/all_videos.txt"
NIGHT_START, NIGHT_END = 21, 5

# A real crossing of this camera's field of view is tens of diagonals. These
# are triage boundaries for ranking, not confirmation thresholds -- the clip
# review decides, and the numbers here only decide what to watch first.
STATIC_EXC = 3.0
JUMP_EXC = 50.0


def load_chunk_hours(path=VIDEO_LIST):
    hours = {}
    if not os.path.exists(path):
        return hours
    with open(path, errors="replace") as f:
        for line in f:
            m = re.search(r"^\s*\d+\s+\d{2}-\d{2}-\d{4}\s+(\d{2}):\d{2}\s+(.*\.mp4)\s*$", line)
            if m:
                base = os.path.splitext(os.path.basename(m.group(2)))[0]
                hours[base] = int(m.group(1))
    return hours


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session-dir", required=True)
    ap.add_argument("--out", default="track_audit.csv")
    ap.add_argument("--static-exc", type=float, default=STATIC_EXC)
    ap.add_argument("--jump-exc", type=float, default=JUMP_EXC)
    ap.add_argument("--video-dir", default=None,
                    help="Directory holding the .mp4 chunks. Required with "
                         "--emit-clips.")
    ap.add_argument("--emit-clips", type=int, default=0, metavar="N",
                    help="Also write a clips list for the N most suspicious "
                         "tracks, plus a review sheet to fill in. This is the "
                         "review set worth watching: random sampling spends "
                         "most of its budget on tracks that are already fine.")
    ap.add_argument("--pad", type=float, default=2.5,
                    help="Seconds of context around each track in the clips.")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.session_dir, "*_tracks.csv")))
    if not files:
        raise SystemExit(f"No *_tracks.csv in {args.session_dir}")
    hours = load_chunk_hours()

    counted = []
    for path in files:
        chunk = os.path.basename(path).replace("_tracks.csv", "")
        with open(path) as f:
            for r in csv.DictReader(f):
                if r["class"] not in CYCLIST_CLASSES or r["counted"] != "yes":
                    continue
                counted.append({
                    "chunk": chunk,
                    "hour": hours.get(chunk),
                    "track_id": r["track_id"],
                    "hits": int(r["hits"]),
                    "first_t": float(r["first_t"]),
                    "last_t": float(r["last_t"]),
                    "duration": float(r["duration_s"]),
                    "max_conf": float(r["max_conf"]),
                    "mean_conf": float(r["mean_conf"]),
                    "excursion": float(r["max_excursion_diag"]),
                })

    if not counted:
        raise SystemExit("No counted cyclist tracks found.")

    # --- duplicate candidates: same chunk, overlapping in time ---
    by_chunk = defaultdict(list)
    for t in counted:
        by_chunk[t["chunk"]].append(t)
    dup_partners = defaultdict(list)
    for chunk, ts in by_chunk.items():
        ts.sort(key=lambda x: x["first_t"])
        for i in range(len(ts)):
            for j in range(i + 1, len(ts)):
                a, b = ts[i], ts[j]
                if b["first_t"] > a["last_t"]:
                    break
                ov = min(a["last_t"], b["last_t"]) - b["first_t"]
                span = min(a["duration"], b["duration"])
                if ov > 0 and span > 0 and ov / span >= 0.25:
                    dup_partners[(chunk, a["track_id"])].append(
                        (b["track_id"], ov, ov / span))
                    dup_partners[(chunk, b["track_id"])].append(
                        (a["track_id"], ov, ov / span))

    # --- score and label ---
    for t in counted:
        flags, score = [], 0.0
        key = (t["chunk"], t["track_id"])
        if key in dup_partners:
            best = max(dup_partners[key], key=lambda p: p[2])
            flags.append(f"DUPLICATE(of #{best[0]}, {best[2]:.0%} overlap)")
            score += 3.0 + best[2]
        if t["excursion"] < args.static_exc:
            flags.append(f"STATIC(exc={t['excursion']:.2f})")
            score += 2.0 + (args.static_exc - t["excursion"]) / args.static_exc
        if t["excursion"] > args.jump_exc:
            flags.append(f"ID_JUMP(exc={t['excursion']:.1f})")
            score += 2.0
        if t["hour"] is not None and (t["hour"] >= NIGHT_START or t["hour"] < NIGHT_END):
            flags.append("NIGHT")
            score += 1.0
        if t["mean_conf"] < 0.22:
            flags.append(f"LOW_MEAN_CONF({t['mean_conf']:.2f})")
            score += 0.5
        t["flags"] = " ".join(flags)
        t["suspicion"] = round(score, 2)

    counted.sort(key=lambda x: -x["suspicion"])

    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(counted[0].keys()))
        w.writeheader()
        w.writerows(counted)

    n = len(counted)
    n_dup = sum(1 for t in counted if "DUPLICATE" in t["flags"])
    n_static = sum(1 for t in counted if "STATIC" in t["flags"])
    n_jump = sum(1 for t in counted if "ID_JUMP" in t["flags"])
    n_night = sum(1 for t in counted if "NIGHT" in t["flags"])
    n_clean = sum(1 for t in counted if not t["flags"])

    print(f"{n} counted cyclist tracks across {len(files)} chunks\n")
    print(f"  DUPLICATE candidates : {n_dup:>3}  "
          f"({n_dup//2} pairs -> ~{n_dup//2} over-counts)")
    print(f"  STATIC (exc < {args.static_exc})    : {n_static:>3}")
    print(f"  ID_JUMP (exc > {args.jump_exc})  : {n_jump:>3}")
    print(f"  NIGHT (21:00-05:00)  : {n_night:>3}")
    print(f"  no flags at all      : {n_clean:>3}")

    # A total that matches ground truth while most tracks carry a flag means
    # the errors are cancelling, not absent.
    print(f"\n  tracks with at least one flag: {n - n_clean}/{n} "
          f"({100.0*(n-n_clean)/n:.0f}%)")

    def dist(key, label):
        vals = sorted(t[key] for t in counted)
        q = lambda p: vals[min(len(vals) - 1, int(p * len(vals)))]
        print(f"    {label:<12} min={vals[0]:>7.2f}  p25={q(.25):>7.2f}  "
              f"med={q(.5):>7.2f}  p75={q(.75):>7.2f}  max={vals[-1]:>7.2f}")

    print(f"\n  distributions over counted cyclists:")
    dist("excursion", "excursion")
    dist("duration", "duration s")
    dist("hits", "hits")
    dist("mean_conf", "mean_conf")

    print(f"\n  TOP 20 MOST SUSPICIOUS -- review these clips first:")
    print(f"    {'chunk':<5} {'hr':>3} {'#id':>7} {'hits':>5} {'dur':>6} "
          f"{'maxc':>5} {'meanc':>6} {'exc':>7}  flags")
    for t in counted[:20]:
        hr = f"{t['hour']:02d}" if t["hour"] is not None else "??"
        print(f"    {t['chunk'][-3:]:<5} {hr:>3} {'#'+t['track_id']:>7} "
              f"{t['hits']:>5} {t['duration']:>6.1f} {t['max_conf']:>5.2f} "
              f"{t['mean_conf']:>6.2f} {t['excursion']:>7.2f}  {t['flags']}")

    print(f"\nWrote {args.out} (sorted by suspicion; open in Excel to work through)")

    if args.emit_clips:
        if not args.video_dir:
            raise SystemExit("--emit-clips needs --video-dir")
        top = counted[:args.emit_clips]
        clip_lines, sheet = [], []
        for rank, t in enumerate(top, start=1):
            mp4 = os.path.join(args.video_dir, t["chunk"] + ".mp4")
            if not os.path.exists(mp4):
                print(f"  WARNING: {t['chunk']}.mp4 missing -- cleaned up? skipped")
                continue
            start = max(0.0, t["first_t"] - args.pad)
            end = t["last_t"] + args.pad
            label = (f"RANK{rank} #{t['track_id']} susp={t['suspicion']} "
                     f"{t['flags'] or 'no-flags'}")
            clip_lines.append(f"{mp4}|{start:.2f}|{end:.2f}|{label}")
            sheet.append({
                "rank": rank,
                "clip_file": (f"{t['chunk']}_window_{int(start)}_{int(end)}"
                              f"_annotated_h264.mp4"),
                "chunk": t["chunk"][-3:],
                "hour": t["hour"] if t["hour"] is not None else "",
                "track_id": t["track_id"],
                "hits": t["hits"],
                "duration_s": round(t["duration"], 1),
                "max_conf": t["max_conf"],
                "mean_conf": t["mean_conf"],
                "excursion": t["excursion"],
                "flags": t["flags"],
                "VERDICT": "",
                "NOTES": "",
            })

        with open("audit_clips.txt", "w") as f:
            f.write("\n".join(clip_lines) + ("\n" if clip_lines else ""))
        with open("review_sheet.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(sheet[0].keys()))
            w.writeheader()
            w.writerows(sheet)

        print(f"\nWrote audit_clips.txt  ({len(clip_lines)} clips)")
        print(f"Wrote review_sheet.csv ({len(sheet)} rows, VERDICT column blank)")
        print(f"\nRender them:")
        print(f"  CLIPS=audit_clips.txt sbatch --array=0-{len(clip_lines)-1}%12 "
              f"run_render_clips.slurm")
        print(f"\nThen fill the VERDICT column in review_sheet.csv with one of:")
        print(f"  REAL  a genuine cyclist riding through")
        print(f"  DUP   a real cyclist, but the same one another clip already counted")
        print(f"  PED   a pedestrian on foot, not riding  (class error)")
        print(f"  BIKE  a parked/stationary bicycle, nobody riding it")
        print(f"  FP    nothing cyclist-like there at all (shadow, car, cone, noise)")
        print(f"\nREAL and DUP are both 'the detector saw something real'; only")
        print(f"REAL should count. PED/BIKE/FP are three different bugs with three")
        print(f"different fixes, which is why they are not one 'wrong' bucket.")
    print(f"\nEstimated over-count from duplicates alone: ~{n_dup//2}")
    print(f"If the {n_static} STATIC tracks are also false positives, the pipeline")
    print(f"is finding ~{n - n_dup//2 - n_static} real cyclists, not {n}.")


if __name__ == "__main__":
    main()
