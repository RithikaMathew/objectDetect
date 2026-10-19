"""
Build a render list: one short clip per counted cyclist in a session.

The counting array runs with --video-mode none, because 48 hours of annotated
video is ~6 GB per session, cannot be watched end to end, and doubles decode
cost on a filesystem that is already near its quota. But every counted cyclist
still needs to be eyeballed -- that is how you find out whether an error is
false positives, missed riders, or duplicates, and eyeballing is the only way
to tell those apart.

So: read the tracks CSVs the array already wrote, and emit one (chunk, start,
end) window per confirmed cyclist track. A session with ~90 cyclists becomes
~90 clips of a few seconds each -- minutes to review, ~50 MB total, instead of
6 GB.

Output is a plain text file, one `chunk_path|start|end|label` per line, consumed
by run_render_clips.slurm as a job array.

Usage:
    python plan_cyclist_clips.py \
        --session-dir pilot_output/sessions/BL_Colonial_2019-07-10 \
        --video-dir "pilot_clips/MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/Standard_SCU8OG_2019-07-10_0000"

    # include rejected tracks too, to look for MISSED cyclists
    python plan_cyclist_clips.py ... --include-rejected --min-hits 8
"""

import argparse
import csv
import glob
import os
import random
import re

CYCLIST_CLASSES = ("cyclist", "bicycle")

# When hunting for MISSED cyclists, a rejected 'person' track is the case most
# worth looking at, not the least. A cyclist whose bicycle never cleared the
# decisive-evidence threshold is labelled 'person' and then rejected -- it is
# invisible in both the counted set and the cyclist-class rejects. Every
# marginal track in the real BL Colonial run was exactly this: 'person', 15-20s
# long, rejected on mean_conf by 0.01-0.05.
REVIEW_CLASSES = ("cyclist", "bicycle", "person", "motorcycle")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session-dir", required=True,
                    help="Directory holding the *_tracks.csv files.")
    ap.add_argument("--video-dir", required=True,
                    help="Directory holding the matching .mp4 chunks.")
    ap.add_argument("--out", default="cyclist_clips.txt")
    ap.add_argument("--pad", type=float, default=2.5,
                    help="Seconds of context before and after each track.")
    ap.add_argument("--include-rejected", action="store_true",
                    help="Also render cyclist-class tracks that FAILED "
                         "confirmation. Use this to hunt for missed riders -- "
                         "a real cyclist sitting just under a threshold is "
                         "invisible in the counted set by definition.")
    ap.add_argument("--min-hits", type=int, default=5,
                    help="With --include-rejected, skip rejected tracks below "
                         "this many hits (they are overwhelmingly noise).")
    ap.add_argument("--hours", default=None,
                    help="Restrict to chunks recorded in these wall-clock "
                         "hours, e.g. --hours 21-5 for night or --hours 7-9 "
                         "for the morning peak. Ranges wrap past midnight. "
                         "Needs all_videos.txt.")
    ap.add_argument("--sample", type=int, default=0,
                    help="Randomly sample this many clips instead of rendering "
                         "all. Reviewing 25 of 88 estimates the false-positive "
                         "rate to about +/-8%% -- enough to decide what to fix, "
                         "and 3.5x less to watch.")
    ap.add_argument("--seed", type=int, default=0,
                    help="Sampling seed, so a review is reproducible.")
    args = ap.parse_args()

    hour_filter = None
    if args.hours:
        m = re.match(r"^(\d{1,2})-(\d{1,2})$", args.hours)
        if not m:
            raise SystemExit("--hours must look like 21-5 or 7-9")
        h0, h1 = int(m.group(1)), int(m.group(2))
        hour_filter = ({h % 24 for h in range(h0, h1)} if h0 < h1
                       else {h % 24 for h in list(range(h0, 24)) + list(range(0, h1))})

    chunk_hour = {}
    if hour_filter is not None:
        if not os.path.exists("all_videos.txt"):
            raise SystemExit("--hours needs all_videos.txt in the current directory")
        with open("all_videos.txt", errors="replace") as f:
            for line in f:
                m = re.search(r"^\s*\d+\s+\d{2}-\d{2}-\d{4}\s+(\d{2}):\d{2}\s+(.*\.mp4)\s*$", line)
                if m:
                    base = os.path.splitext(os.path.basename(m.group(2)))[0]
                    chunk_hour[base] = int(m.group(1))

    files = sorted(glob.glob(os.path.join(args.session_dir, "*_tracks.csv")))
    if not files:
        raise SystemExit(f"No *_tracks.csv in {args.session_dir}")

    lines, n_counted, n_rejected = [], 0, 0
    for path in files:
        chunk = os.path.basename(path).replace("_tracks.csv", "")
        mp4 = os.path.join(args.video_dir, chunk + ".mp4")
        if not os.path.exists(mp4):
            print(f"  WARNING: no video for {chunk} -- "
                  f"already cleaned up? skipping")
            continue
        if hour_filter is not None:
            hh = chunk_hour.get(chunk)
            if hh is None or hh not in hour_filter:
                continue
        with open(path) as f:
            for r in csv.DictReader(f):
                counted = r["counted"] == "yes"
                if counted:
                    # Counted set: only cyclist classes -- these are the counts
                    # being validated, so this is the false-positive review.
                    if r["class"] not in CYCLIST_CLASSES:
                        continue
                else:
                    if not args.include_rejected:
                        continue
                    # Rejected set: widen to person/motorcycle, because that is
                    # where a missed cyclist hides (see REVIEW_CLASSES).
                    if r["class"] not in REVIEW_CLASSES:
                        continue
                    if int(r["hits"]) < args.min_hits:
                        continue
                start = max(0.0, float(r["first_t"]) - args.pad)
                end = float(r["last_t"]) + args.pad
                tag = "COUNTED" if counted else "REJECTED"
                label = (f"{tag} #{r['track_id']} {r['class']} "
                         f"hits={r['hits']} maxc={r['max_conf']} "
                         f"meanc={r['mean_conf']} exc={r['max_excursion_diag']}")
                lines.append(f"{mp4}|{start:.2f}|{end:.2f}|{label}")
                if counted:
                    n_counted += 1
                else:
                    n_rejected += 1

    n_before = len(lines)
    if args.sample and args.sample < len(lines):
        random.seed(args.seed)
        lines = sorted(random.sample(lines, args.sample))
        print(f"Sampled {len(lines)} of {n_before} clips (seed={args.seed})")

    with open(args.out, "w") as f:
        f.write("\n".join(lines) + ("\n" if lines else ""))

    total_s = sum(float(l.split("|")[2]) - float(l.split("|")[1]) for l in lines)
    print(f"Chunks with results : {len(files)}")
    print(f"Clips planned       : {len(lines)}  "
          f"({n_counted} counted, {n_rejected} rejected)")
    print(f"Total footage        : {total_s:.0f}s  "
          f"(~{total_s * 0.9:.0f} MB annotated, rough)")
    print(f"Wrote {args.out}")
    if lines:
        print(f"\nSubmit with:")
        print(f"  sbatch --array=0-{len(lines)-1}%12 run_render_clips.slurm")
        print(f"\nFirst few:")
        for l in lines[:5]:
            p, s, e, lab = l.split("|")
            print(f"  {os.path.basename(p)}  {s}-{e}s  {lab}")


if __name__ == "__main__":
    main()
