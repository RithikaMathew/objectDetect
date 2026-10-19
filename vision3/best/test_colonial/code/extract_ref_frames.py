#!/usr/bin/env python3
"""extract_ref_frames.py : save CLEAN full-size frames (no boxes, no zones) to draw the road / bike lane / sidewalk on.

  cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
  # a Colonial hour file (the 2019 videos), three frames:
  python code/extract_ref_frames.py --colonial-chunk 13 --times 5:00,25:00,45:00
  # any other video, e.g. the new one:
  python code/extract_ref_frames.py --video "/path/to/new_video.mp4" --times 0:30,5:00 --out-dir zones/ref_new

Writes PNGs at the video's own resolution to zones/ref/ (or --out-dir) and prints their sizes. Pick a frame with the lane markings visible and
few cars in the way, download it, and open it in zone_annotator.html.
"""
import argparse, os, cv2

COLONIAL = ("/orange/xiangyan/rithika/vision/pilot_clips/MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/"
            "Standard_SCU8OG_2019-07-10_0000/Standard_SCU8OG_2019-07-10_0000.{n:03d}.mp4")
ap = argparse.ArgumentParser()
ap.add_argument("--video")
ap.add_argument("--colonial-chunk", type=int, help="hour number of a Colonial 2019-07-10 file (13 = 12:00-13:00)")
ap.add_argument("--times", default="1:00,10:00,30:00", help="comma list of mm:ss or h:mm:ss")
ap.add_argument("--out-dir", default="zones/ref")
a = ap.parse_args()
vid = a.video or (COLONIAL.format(n=a.colonial_chunk) if a.colonial_chunk else None)
if not vid:
    ap.error("give --video or --colonial-chunk")
cap = cv2.VideoCapture(vid)
if not cap.isOpened():
    raise SystemExit(f"cannot open {vid}")
fps, n = cap.get(cv2.CAP_PROP_FPS), int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
os.makedirs(a.out_dir, exist_ok=True)
stem = os.path.splitext(os.path.basename(vid))[0]
for t in a.times.split(","):
    parts = [float(x) for x in t.split(":")]
    sec = sum(v * 60 ** i for i, v in enumerate(reversed(parts)))
    idx = min(int(sec * fps), max(n - 1, 0))
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
    ok, fr = cap.read()
    if not ok:
        print(f"{t}: could not read frame {idx}"); continue
    out = os.path.join(a.out_dir, f"{stem}_{t.replace(':', 'm')}s.png")
    cv2.imwrite(out, fr)
    print(f"{out}   {fr.shape[1]} x {fr.shape[0]}")
cap.release()
