#!/usr/bin/env python3
"""
extract_frame.py

Saves one still frame from a video as a PNG so you can figure out the pixel
coordinates of the road/bike-lane corners for --road-zone in
xclip_overlay_v6.py. Download the PNG to your own machine and open it in any
image viewer/editor that shows cursor position (Preview, GIMP, even most
browsers via a small script) -- hover the corners of the road area and note
the x,y it reports. Then build the --road-zone string as:
    "x1,y1;x2,y2;x3,y3;x4,y4"
going around the polygon in order (clockwise or counter-clockwise, doesn't
matter). Coordinates are in the ORIGINAL video's pixel space (this script
prints the frame's width/height to confirm).

USAGE
    python extract_frame.py --video test.mp4 --frame 600 --out frame600.png
"""
import argparse
import sys

import cv2

ap = argparse.ArgumentParser(description=__doc__,
                             formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--video", required=True)
ap.add_argument("--frame", type=int, default=1, help="1-indexed frame number to grab")
ap.add_argument("--out", default="frame.png")
args = ap.parse_args()

cap = cv2.VideoCapture(args.video)
if not cap.isOpened():
    sys.exit(f"ERROR: cannot open {args.video}")
cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, args.frame - 1))
ok, frame = cap.read()
if not ok:
    sys.exit(f"ERROR: could not read frame {args.frame} (video may be shorter)")

h, w = frame.shape[:2]
cv2.imwrite(args.out, frame)
print(f"wrote {args.out}  ({w}x{h})")
print("Download this file and hover the road/bike-lane corners in an image "
      "viewer to read off x,y, then build --road-zone \"x1,y1;x2,y2;...\"")
