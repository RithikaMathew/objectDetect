#!/usr/bin/env python3
"""Choose 3 NEW 15-minute windows (1 night, 2 day) that are not among the clips already looked at, and print
copy-paste commands: cut the clip to watch, a truth-file template to fill in, and the sbatch line that runs the current
best setup on exactly that window. Prints only; submits nothing. Run from test_colonial (NOT from code/).

  python code/pick_new_windows.py --like truth/day_1400_truth.csv --from-batch code/run_batch4.sh
  python code/pick_new_windows.py --windows 8:15,17:00,23:30 ...    # your own picks (hour:minute, 2019-07-10 clock)

How the numbers work (README section 38): hour file NNN = clock hour NNN-1; START_FRAME = first frame (+5 margin);
MAX_FRAMES = STOP frame (0 = to end); 900 s = 26973 frames at 29.97 fps.
Looked-at hours (default list from the README, edit with --seen): the four scored clips and the first week's checked hours.
After labelling: python code/eval_truth.py --root . --runs exp0_base,b4_combo_static5,<new runs> --baseline exp0_base
(the new runs must use the SAME settings as b4_combo_static5, which is what the printed sbatch line does).
"""
import argparse, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
FPS = 29.97
VIDEO = ("/orange/xiangyan/rithika/vision/pilot_clips/MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/"
         "Standard_SCU8OG_2019-07-10_0000/Standard_SCU8OG_2019-07-10_0000.{n:03d}.mp4")
SEEN_HOURS = [7, 10, 12, 13, 14, 16, 21, 22]          # clock hours already checked or scored

def default_windows(seen):
    day = [h for h in (8, 9, 11, 15, 17, 18, 19) if h not in seen]
    night = [h for h in (23, 0, 1, 2, 3, 4, 5) if h not in seen]
    return [f"{day[0]}:15", f"{day[1] if len(day) > 1 else day[0]}:45".replace(":45", ":30") if len(day) > 1 else f"{day[0]}:45",
            f"{night[0]}:20"]

def window(hhmm):
    h, m = [int(x) for x in hhmm.split(":")]; off = m * 60.0
    n = h + 1; start = int(round(off * FPS)) + 5; stop = start + int(900 * FPS) - 5
    return h, m, n, off, start, stop

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--windows"); ap.add_argument("--seen", default=",".join(map(str, SEEN_HOURS)))
    ap.add_argument("--like", help="an existing truth CSV: its header is copied into the templates")
    ap.add_argument("--from-batch", help="code/run_batch4.sh: its ENVV line = the settings of the current best")
    ap.add_argument("--run-prefix", default="b4_new"); ap.add_argument("--throttle", default="3")
    a = ap.parse_args()
    if os.path.basename(os.getcwd()) == "code": sys.exit("run from test_colonial, not from inside code/")
    seen = [int(x) for x in a.seen.split(",") if x]
    wins = (a.windows.split(",") if a.windows else default_windows(seen))
    header = open(a.like).readline().strip() if a.like else "time_mmss,label,note"
    envv = ""
    if a.from_batch:
        from scale_up import envv_from_batch; import re as _re
        envv = _re.sub(r"(^|,)(RUN|START_FRAME|MAX_FRAMES)=[^,]*", "", envv_from_batch(a.from_batch)).lstrip(",")
    os.makedirs("truth", exist_ok=True); os.makedirs("new_clips", exist_ok=True)
    print("# 1) cut the clips to watch (video position = clock minus window start):")
    for w in wins:
        h, m, n, off, start, stop = window(w); tag = f"{h:02d}{m:02d}"
        print(f'ffmpeg -ss {int(off)} -t 900 -i "{VIDEO.format(n=n)}" -c:v libx264 -crf 23 -an new_clips/new_{tag}.mp4')
    print("\n# 2) truth templates written (fill ONE ROW PER PERSON from watching the clip; motorcycle = cyclist):")
    for w in wins:
        h, m, n, *_ = window(w); tag = f"{h:02d}{m:02d}"; p = f"truth/new_{tag}_truth_TEMPLATE.csv"
        if os.path.exists(p): print("  exists, kept:", p); continue
        open(p, "w").write(header + "\n"); print("  ", p)
    print("\n# 3) run the current best setup on exactly these windows (check the settings line first):")
    if not envv: print("#   (give --from-batch code/run_batch4.sh to print the real sbatch lines)")
    for w in wins:
        h, m, n, off, start, stop = window(w); tag = f"{h:02d}{m:02d}"
        print(f"sbatch --time=02:00:00 --export=ALL,RUN={a.run_prefix}_{tag},{envv + ',' if envv else ''}START_FRAME={start},MAX_FRAMES={stop}"
              f" --array={n} code/run_xclip_colonial_v19.slurm")
    print("\n# Submit each line ONCE (running it twice submits twice). Night windows: file numbers 24 and 1-6 are hours 23-05;"
          " check the clip really is dark before calling it a night window.")

if __name__ == "__main__": main()
