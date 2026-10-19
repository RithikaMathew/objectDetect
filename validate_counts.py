"""
Compare pipeline cyclist counts against the hand-collected ground truth.

This is the study's actual headline metric. Detection mAP is a proxy; what the
paper reports is how closely an automated count reproduces a count made by a
person watching the same footage.

Reads the per-track CSVs written by pilot_detect_v2.py across all hourly chunks
of a site-session, sums the confirmed cyclist tracks, and joins to
ground_truth_bicycle_counts_v2.csv through video_site_mapping.csv.

Usage:
    # one session
    python validate_counts.py --session-dir pilot_output/sessions/BL_Colonial_2019-07-10 \\
                              --video-folder "BL Colonial" --date 2019-07-10

    # every session processed so far
    python validate_counts.py --all pilot_output/sessions
"""

import argparse
import csv
import glob
import os
import re
from collections import defaultdict

GT_CSV = os.path.join("Bike Lane Study Counts", "ground_truth_bicycle_counts_v2.csv")
MAP_CSV = "video_site_mapping.csv"
VIDEO_LIST = "all_videos.txt"
CYCLIST_CLASSES = ("cyclist", "bicycle")

# Night defined as 21:00-05:00. Chosen to match how the day/night ground truth
# in "Bike lane study counts day v night.xlsx" is built; adjust if that file
# uses different boundaries.
NIGHT_START, NIGHT_END = 21, 5


def load_chunk_times(path=VIDEO_LIST):
    """chunk basename -> (datetime string, hour int), read from all_videos.txt.

    Wall-clock time per chunk is what makes an hourly profile interpretable.
    Chunk index alone does not: .001 is 05:00 here, so index N is hour N+4, and
    guessing that offset wrong moves every conclusion about day-vs-night by an
    hour. The archive listing records the real timestamps, so use those.
    """
    times = {}
    if not os.path.exists(path):
        return times
    with open(path, errors="replace") as f:
        for line in f:
            m = re.search(r"^\s*\d+\s+(\d{2}-\d{2}-\d{4})\s+(\d{2}):(\d{2})\s+(.*\.mp4)\s*$", line)
            if not m:
                continue
            date, hh, mm, p = m.group(1), int(m.group(2)), m.group(3), m.group(4)
            times[os.path.splitext(os.path.basename(p))[0]] = (f"{date} {hh:02d}:{mm}", hh)
    return times


def load_tracks(session_dir):
    """Sum confirmed cyclist tracks across every *_tracks.csv in a session.

    Each hourly chunk is tracked independently, so a cyclist crossing an hour
    boundary is counted in both chunks. That is a real (small) source of
    over-count and it is reported rather than silently corrected -- with ~48
    boundaries a day and crossings lasting ~3s, the expected inflation is well
    under one cyclist per session, but it should be stated, not assumed away.
    """
    per_chunk, total, rejected = {}, 0, 0
    files = sorted(glob.glob(os.path.join(session_dir, "*_tracks.csv")))
    if not files:
        raise SystemExit(f"No *_tracks.csv found in {session_dir}")
    for path in files:
        chunk = os.path.basename(path).replace("_tracks.csv", "")
        n = 0
        with open(path) as f:
            for r in csv.DictReader(f):
                if r["class"] not in CYCLIST_CLASSES:
                    continue
                if r["counted"] == "yes":
                    n += 1
                else:
                    rejected += 1
        per_chunk[chunk] = n
        total += n
    return per_chunk, total, rejected, len(files)


def load_ground_truth():
    """(video_folder, date) -> {'site':…, 'total':…, 'by_facility':{…}}"""
    if not os.path.exists(MAP_CSV):
        raise SystemExit(f"{MAP_CSV} missing -- run build_site_mapping.py first")
    if not os.path.exists(GT_CSV):
        raise SystemExit(f"{GT_CSV} missing -- run "
                         f"'Bike Lane Study Counts/fix_ground_truth.py' first")

    gt_rows = defaultdict(lambda: defaultdict(int))
    gt_fac = defaultdict(lambda: defaultdict(int))
    with open(GT_CSV) as f:
        for r in csv.DictReader(f):
            n = int(float(r["count"] or 0))
            gt_rows[r["site"]][r["date"]] += n
            gt_fac[(r["site"], r["date"])][r["facility_type"]] += n

    out = {}
    with open(MAP_CSV) as f:
        for r in csv.DictReader(f):
            site, date = r["gt_site"], r["date"]
            out[(r["video_folder"], date)] = {
                "site": site,
                "total": gt_rows[site][date],
                "by_facility": dict(gt_fac[(site, date)]),
                "n_chunks": int(r["n_mp4_chunks"]),
            }
    return out


def report(video_folder, date, session_dir, gt_index):
    per_chunk, total, rejected, n_files = load_tracks(session_dir)
    key = (video_folder, date)
    gt = gt_index.get(key)

    print(f"\n{'='*66}")
    print(f"{video_folder}  {date}")
    print(f"{'='*66}")
    print(f"chunks processed : {n_files}" +
          (f" of {gt['n_chunks']} in the session" if gt else ""))
    print(f"PIPELINE count   : {total} cyclist tracks")
    print(f"  (rejected      : {rejected} cyclist-class tracks failed confirmation)")

    if not gt:
        print(f"\n  No ground-truth row for {key}. Check the video_folder spelling "
              f"against video_site_mapping.csv.")
        return None

    print(f"GROUND TRUTH     : {gt['total']} cyclists  (site '{gt['site']}')")
    print(f"  by facility    : {gt['by_facility']}")

    err = total - gt["total"]
    pct = (100.0 * err / gt["total"]) if gt["total"] else float("nan")

    if n_files < gt["n_chunks"]:
        # A partial run's raw error is not just imprecise, it is misleading in a
        # specific direction: it always looks like a large UNDER-count, because
        # most of the footage has not been counted yet. Comparing PER-CHUNK
        # RATES instead gives a signal that is usable now and can point the
        # opposite way -- which is the case worth catching early.
        pipe_rate = total / n_files
        gt_rate = gt["total"] / gt["n_chunks"]
        print(f"\n  ** PARTIAL: {n_files}/{gt['n_chunks']} chunks processed. "
              f"Ignore the raw error below -- it counts un-processed footage as "
              f"missed cyclists. **")
        print(f"\n  RATE COMPARISON (usable now):")
        print(f"    pipeline     : {pipe_rate:.2f} cyclists per chunk")
        print(f"    ground truth : {gt_rate:.2f} cyclists per chunk (session average)")
        if gt_rate > 0:
            ratio = pipe_rate / gt_rate
            print(f"    ratio        : {ratio:.2f}x")
            # Cycling is strongly diurnal, so a couple of daytime chunks
            # legitimately exceed the session average. Treat this as a flag for
            # where to look, never as a measurement.
            if ratio > 2.0:
                print(f"    -> pipeline rate is {ratio:.1f}x the session average. "
                      f"Some of that is diurnal (these may be peak hours), but a "
                      f"ratio this high usually means OVER-counting. Check the "
                      f"tracks CSV for fragments counted twice.")
            elif ratio < 0.5:
                print(f"    -> pipeline rate is well below the session average, "
                      f"suggesting missed cyclists even allowing for off-peak hours.")
            else:
                print(f"    -> in a plausible range; finish the session for a real number.")
        print(f"\n  (raw error, not meaningful yet: {err:+d})")
    else:
        print(f"\nERROR            : {err:+d}  ({pct:+.1f}%)")

    # Hourly profile: a plausible total can hide compensating errors, so show
    # where counts land in time. Chunk .NNN is one hour of footage.
    times = load_chunk_times()
    print(f"\nper-chunk counts (chunk: n):")
    items = sorted(per_chunk.items())
    line = ""
    for chunk, n in items:
        m = re.search(r"\.(\d{3})$", chunk)
        label = m.group(1) if m else chunk[-3:]
        line += f"  {label}:{n:<3}"
        if len(line) > 88:
            print(line)
            line = ""
    if line:
        print(line)

    # --- DAY / NIGHT, the check that catches compensating errors ---
    # A total that matches ground truth is not evidence the pipeline is right:
    # night false positives can offset daytime misses exactly. Cyclist volume
    # is strongly diurnal, so a night rate at or above the day rate is a
    # positive indication of false positives regardless of how good the total
    # looks.
    day_n = night_n = day_h = night_h = 0
    hourly = {}
    missing_times = 0
    for chunk, n in items:
        info = times.get(chunk)
        if not info:
            missing_times += 1
            continue
        _, hh = info
        hourly[chunk] = hh
        if hh >= NIGHT_START or hh < NIGHT_END:
            night_n += n
            night_h += 1
        else:
            day_n += n
            day_h += 1

    if missing_times:
        print(f"\n  ({missing_times} chunks had no timestamp in {VIDEO_LIST}; "
              f"day/night split covers the rest)")

    if day_h and night_h:
        d_rate, n_rate = day_n / day_h, night_n / night_h
        print(f"\nDAY / NIGHT  (night = {NIGHT_START:02d}:00-{NIGHT_END:02d}:00)")
        print(f"  daytime : {day_n:>4} over {day_h:>2} h = {d_rate:.2f}/h")
        print(f"  night   : {night_n:>4} over {night_h:>2} h = {n_rate:.2f}/h")
        share = 100.0 * night_n / max(1, day_n + night_n)
        print(f"  night is {share:.0f}% of counts but "
              f"{100.0*night_h/(day_h+night_h):.0f}% of hours")
        if n_rate >= d_rate:
            print(f"  ** WARNING: night rate >= day rate. Cycling is strongly "
                  f"diurnal, so this is a strong indicator of NIGHT FALSE "
                  f"POSITIVES (headlights, reflections, shadows under "
                  f"streetlights). Review night clips before trusting the "
                  f"total -- night FPs can offset daytime misses and leave the "
                  f"daily total looking correct. **")
        elif n_rate > 0.5 * d_rate:
            print(f"  night rate is {100*n_rate/d_rate:.0f}% of the day rate -- "
                  f"high for cycling; worth reviewing night clips.")
        print(f"\n  Cross-check against 'Bike lane study counts day v night.xlsx'"
              f" (Totals sheet has a % night column per corridor).")

        busiest = sorted(items, key=lambda kv: -kv[1])[:6]
        print(f"\n  busiest hours:")
        for chunk, n in busiest:
            hh = hourly.get(chunk)
            if hh is None:
                continue
            ni = hh >= NIGHT_START or hh < NIGHT_END
            print(f"    {chunk[-3:]}  {hh:02d}:00  n={n}"
                  f"{'   <-- NIGHT' if ni else ''}")

    return {"video_folder": video_folder, "date": date, "site": gt["site"],
            "pipeline": total, "ground_truth": gt["total"], "error": err,
            "pct_error": pct, "chunks_done": n_files,
            "chunks_total": gt["n_chunks"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session-dir")
    ap.add_argument("--video-folder")
    ap.add_argument("--date")
    ap.add_argument("--all", metavar="SESSIONS_ROOT",
                    help="Scan a directory of session folders named "
                         "<Video_Folder>_<YYYY-MM-DD>.")
    ap.add_argument("--out", default="count_validation.csv")
    args = ap.parse_args()

    gt_index = load_ground_truth()
    rows = []

    if args.all:
        for d in sorted(glob.glob(os.path.join(args.all, "*"))):
            if not os.path.isdir(d):
                continue
            base = os.path.basename(d)
            m = re.match(r"(.+)_(\d{4}-\d{2}-\d{2})$", base)
            if not m:
                print(f"skip {base}: expected <Video_Folder>_<YYYY-MM-DD>")
                continue
            folder = m.group(1).replace("_", " ")
            r = report(folder, m.group(2), d, gt_index)
            if r:
                rows.append(r)
    else:
        if not (args.session_dir and args.video_folder and args.date):
            raise SystemExit("Need --session-dir, --video-folder and --date "
                             "(or use --all).")
        r = report(args.video_folder, args.date, args.session_dir, gt_index)
        if r:
            rows.append(r)

    if rows:
        with open(args.out, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"\n{'='*66}")
        complete = [r for r in rows if r["chunks_done"] >= r["chunks_total"]]
        if complete:
            tp = sum(r["pipeline"] for r in complete)
            tg = sum(r["ground_truth"] for r in complete)
            mape = sum(abs(r["pct_error"]) for r in complete) / len(complete)
            print(f"{len(complete)} complete session(s): pipeline {tp} vs "
                  f"ground truth {tg}  ({100.0*(tp-tg)/max(tg,1):+.1f}%)")
            print(f"mean absolute percentage error per session: {mape:.1f}%")
        print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
