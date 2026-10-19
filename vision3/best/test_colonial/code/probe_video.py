#!/usr/bin/env python3
"""probe_video.py : size, frame rate and length of a video, plus the commands to cut a 15-minute test clip.

  python code/probe_video.py "/path/to/new_video.mp4"
"""
import sys, cv2

if len(sys.argv) < 2:
    sys.exit(__doc__)
p = sys.argv[1]
cap = cv2.VideoCapture(p)
if not cap.isOpened():
    sys.exit(f"cannot open {p}")
w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps, n = cap.get(cv2.CAP_PROP_FPS), int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
cap.release()
dur = n / fps if fps else 0
print(f"file     : {p}\nsize     : {w} x {h}  (aspect {w / h:.3f}; the Colonial zones file was drawn on 720 x 480 = 1.500)\n"
      f"frame rate: {fps:.3f}\nframes   : {n}\nlength   : {dur / 60:.1f} min ({dur:.0f} s)")
print("\nTo cut a 15-minute test clip (no re-encoding; start where you like, here 5 minutes in):")
print(f'  module load ffmpeg\n  ffmpeg -ss 00:05:00 -i "{p}" -t 900 -c copy "/orange/xiangyan/rithika/vision/vision3/best/test_colonial/newvideo/clip_15min.mp4"')
print("Set the clip's real start time (clock) when you run it: START=\"YYYY-MM-DD HH:MM:SS\".")
