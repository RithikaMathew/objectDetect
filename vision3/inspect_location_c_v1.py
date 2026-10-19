#!/usr/bin/env python3
"""
inspect_location_c_v1.py

Location C (tracks 21-25, ~(643, 22)) hasn't been identified yet -- the
earlier tight crop was too small/blurry to tell if it's catching a passing
car, a person, or something else, and the full frame at frame5000 showed
multiple real cars on the road nearby. This pulls larger, less-padded
crops across several frames spanning track 21-25's actual active range
(4498-5619) so we can actually tell what's there.

Usage:
    python inspect_location_c_v1.py --video test.mp4 \\
        --outdir pilot_output/compare_v4/location_c_check
"""
import argparse
import os

import cv2

# wider crop than before, less padding relative to size so the object
# fills more of the frame
CX, CY = 643, 22
CROP_HALF_W, CROP_HALF_H = 150, 100


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--video", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--frames", type=int, nargs="+",
                     default=[4498, 4600, 4700, 4800, 4931, 4976, 5072,
                               5241, 5340, 5411, 5510, 5619])
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    cap = cv2.VideoCapture(args.video)
    frame_idx = 0
    targets = set(args.frames)
    max_frame = max(targets)

    while frame_idx <= max_frame:
        ok, frame = cap.read()
        if not ok:
            break
        frame_idx += 1
        if frame_idx not in targets:
            continue

        H, W = frame.shape[:2]
        x1, y1 = max(0, CX - CROP_HALF_W), max(0, CY - CROP_HALF_H)
        x2, y2 = min(W, CX + CROP_HALF_W), min(H, CY + CROP_HALF_H)
        crop = frame[y1:y2, x1:x2]
        cv2.imwrite(os.path.join(args.outdir, f"locC_frame{frame_idx}.jpg"), crop)

    cap.release()
    print(f"Saved location-C crops for frames {sorted(targets)} to {args.outdir}")
    print("These span track 21-25's full active range (4498-5619) so "
          "whatever's triggering it should be visible in at least a few.")


if __name__ == "__main__":
    main()
