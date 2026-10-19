#!/usr/bin/env python3
"""find_new_videos.py : find MioVision videos from 2025 or later, show their resolution, pick one and print the exact commands to run it.

  cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
  python code/find_new_videos.py                          # looks under the MioVision Data folder, picks the highest-resolution 2025+ file
  python code/find_new_videos.py --pick random            # a random one instead
  python code/find_new_videos.py --min-year 0 --limit 60  # the date is not in the file names? list everything with its resolution

The year is read from the file or folder names (YYYY-MM-DD). The start time it suggests assumes the 2019 naming (file ...NNN.mp4 = hour NNN-1);
CHECK IT against the video before trusting the clock time (the night rules use it).
"""
import argparse, os, random, re, cv2

ap = argparse.ArgumentParser()
ap.add_argument("--root", default="/orange/xiangyan/rithika/vision/pilot_clips/MioVision Data")
ap.add_argument("--min-year", type=int, default=2025)
ap.add_argument("--pick", choices=["best", "random"], default="best")
ap.add_argument("--limit", type=int, default=40, help="probe at most this many candidate files")
a = ap.parse_args()
if not os.path.isdir(a.root):
    raise SystemExit(f"folder not found: {a.root}\nFind the real one with:  ls /orange/xiangyan/rithika/vision/pilot_clips/")
date_re = re.compile(r"(20\d{2})-(\d{2})-(\d{2})")
cands = []
for d, _dirs, files in os.walk(a.root):
    for f in files:
        if not f.lower().endswith((".mp4", ".avi", ".mov", ".mkv")):
            continue
        p = os.path.join(d, f)
        m = date_re.search(p)
        if m and int(m.group(1)) >= a.min_year:
            cands.append((p, "-".join(m.groups())))
cands.sort()
print(f"{len(cands)} video files with a date >= {a.min_year} under {a.root}")
if not cands:
    print("None. The date may not be in the names. Try:  python code/find_new_videos.py --min-year 0 --limit 60\n"
          f'or list the folders:  ls "{a.root}"')
    raise SystemExit(0)
rows = []
step = max(1, len(cands) // a.limit)
for p, dt in cands[::step][:a.limit]:
    cap = cv2.VideoCapture(p)
    if not cap.isOpened():
        continue
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps, n = cap.get(cv2.CAP_PROP_FPS), int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    rows.append(dict(path=p, date=dt, w=w, h=h, fps=fps, minutes=(n / fps / 60 if fps else 0)))
print("\n| date | size | fps | minutes | file |\n|---|---|---|---|---|")
for r in rows:
    print(f"| {r['date']} | {r['w']}x{r['h']} | {r['fps']:.1f} | {r['minutes']:.0f} | {r['path']} |")
if not rows:
    raise SystemExit("none of them could be opened with OpenCV")
pick = random.choice(rows) if a.pick == "random" else max(rows, key=lambda r: (r["w"] * r["h"], r["minutes"]))
m = re.search(r"\.(\d{3})\.[A-Za-z0-9]+$", pick["path"])
hour = int(m.group(1)) - 1 if m else 0
off_min = 5 if pick["minutes"] > 20 else 0
start = f"{pick['date']} {hour:02d}:{off_min:02d}:00"
clip = f"newvideo/clip_{pick['date']}_h{hour:02d}_15min.mp4"
print(f"\nPICKED ({a.pick}): {pick['path']}   {pick['w']}x{pick['h']}  {pick['fps']:.1f} fps  {pick['minutes']:.0f} min")
print("\nRun, in order (from test_colonial):")
print('  mkdir -p newvideo && module load ffmpeg')
print(f'  ffmpeg -ss 00:{off_min:02d}:00 -i "{pick["path"]}" -t 900 -c copy "{clip}"')
print(f'  python code/probe_video.py "{clip}"')
print(f'  python code/extract_ref_frames.py --video "{clip}" --times 0:30,5:00 --out-dir zones/ref_new     # frames to draw zones on')
print(f'  VIDEO="$PWD/{clip}" START="{start}" bash code/run_new_video.sh')
print(f"\nSTART is a guess ({'hour taken from the file number' if m else 'no file number in the name, midnight assumed'} + {off_min} min offset): confirm the real clock time of the first frame.")
