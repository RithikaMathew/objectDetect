#!/usr/bin/env python3
"""disp_check.py : which COUNTED tracks have a small net movement?  (what --person-min-disp / PERSON_MIN_DISP would remove)

  cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
  python code/disp_check.py --root . --runs b3_combo --below 60

Prints every counted person track whose disp_px (ground-point movement from its first to its last frame, the number the filter uses)
is below --below, with its clip, time, length and label, so you can see which ones are real standing people and which are barricades.
"""
import argparse, csv, glob, os

CLIPS = {22: "night 21:15", 15: "day 14:00", 23: "night 22:00 (hold-out)", 13: "day 12:45 (hold-out)"}

ap = argparse.ArgumentParser()
ap.add_argument("--root", default=".")
ap.add_argument("--runs", default="b3_combo")
ap.add_argument("--below", type=float, default=60.0)
a = ap.parse_args()
rows = []
for run in a.runs.split(","):
    for f in sorted(glob.glob(os.path.join(a.root, "counts", run, "*_tracks.csv"))):
        chunk = int(os.path.basename(f).split("0000.")[1][:3]) if "0000." in os.path.basename(f) else -1
        for r in csv.DictReader(open(f)):
            if r.get("counted") != "1":
                continue
            try:
                d = float(r["disp_px"])
            except (KeyError, ValueError):
                continue
            if d < a.below:
                rows.append((d, run, CLIPS.get(chunk, str(chunk)), r["track_id"], r["first_time"][11:], r["secs"], r["label"], r.get("det_label", "")))
print(f"counted tracks with disp_px < {a.below:g}:\n")
print("| disp px | run | clip | track | from | secs | label | detector |\n|---|---|---|---|---|---|---|---|")
for d, run, clip, tid, t0, secs, lab, det in sorted(rows):
    print(f"| {d:.0f} | {run} | {clip} | #{tid} | {t0} | {secs} | {lab} | {det} |")
if not rows:
    print("(none)")
