#!/usr/bin/env python3
"""
check_bl_colonial_corruption_v1.py

img.verify() (used in the last check) only validates JPEG structural
markers -- it can pass even when scan/pixel data is scrambled, which is
what the garbled, rainbow-static val_batch mosaics actually look like.
This does two stronger checks per file:

  1. Full decode via PIL .load() (forces reading every scanline, not just
     headers) AND a separate OpenCV cv2.imread() (different decoder --
     catches issues one library tolerates and the other doesn't).
  2. Re-reads each file TWICE, a few seconds apart. If a file decodes fine
     one time and fails/differs the next, that points at flaky network
     reads off /orange (matches the training log's read-speed warning)
     rather than a permanently corrupt file on disk -- those need very
     different fixes (retry/local-copy vs. re-exporting the frame).

Usage:
    python check_bl_colonial_corruption_v1.py \\
        --root /orange/xiangyan/rithika/vision/dataset_frames/roboflow_split_v1 \\
        --pattern "*BL-Colonial*.jpg"
"""
import argparse
import glob
import hashlib
import os
import time

import cv2
import numpy as np
from PIL import Image


def decode_check(path):
    """Returns (ok: bool, reason: str, pixel_hash: str or None)."""
    try:
        with Image.open(path) as img:
            img.load()  # forces full decode, not just header parse
            arr = np.asarray(img.convert("RGB"))
    except Exception as e:
        return False, f"PIL load failed: {e}", None

    cv_img = cv2.imread(path)
    if cv_img is None:
        return False, "cv2.imread returned None", None

    # Cheap corruption signal: real photos rarely have huge flat blocks of
    # identical pixel value; heavy pixel-level corruption often does.
    flat_frac = np.mean(arr == arr[0, 0])
    if flat_frac > 0.5:
        return False, f"suspiciously flat ({flat_frac:.0%} identical pixels)", None

    h = hashlib.md5(arr.tobytes()).hexdigest()
    return True, "ok", h


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", required=True)
    ap.add_argument("--pattern", default="*BL-Colonial*.jpg")
    ap.add_argument("--reread-delay", type=float, default=3.0,
                     help="seconds to wait before the second read (default 3s)")
    args = ap.parse_args()

    paths = sorted(glob.glob(os.path.join(args.root, "*", "images", args.pattern)))
    print(f"Found {len(paths)} files matching {args.pattern!r} under {args.root}\n")

    permanent_bad, flaky, clean = [], [], []

    for path in paths:
        ok1, reason1, hash1 = decode_check(path)
        time.sleep(args.reread_delay)
        ok2, reason2, hash2 = decode_check(path)

        if ok1 and ok2 and hash1 == hash2:
            clean.append(path)
        elif not ok1 and not ok2:
            permanent_bad.append((path, reason1, reason2))
            print(f"PERMANENTLY BAD: {path}\n    read1: {reason1}\n    read2: {reason2}")
        else:
            # succeeded once, failed or gave different pixels the other time
            flaky.append((path, ok1, reason1, ok2, reason2))
            print(f"FLAKY (inconsistent across reads): {path}\n"
                  f"    read1: ok={ok1} ({reason1})\n"
                  f"    read2: ok={ok2} ({reason2})")

    print(f"\n=== summary ===")
    print(f"clean:           {len(clean)}")
    print(f"flaky (retry-able, likely network/mount issue): {len(flaky)}")
    print(f"permanently bad (same failure both times):       {len(permanent_bad)}")

    if flaky:
        print("\nFlaky files point at network/mount read issues (matches the "
              "'Slow image access' warning from your training log) -- consider "
              "copying the split to local/scratch disk before training rather "
              "than reading directly off /orange.")
    if permanent_bad:
        print("\nPermanently bad files need re-exporting from the original "
              "source video/Roboflow export -- retrying reads won't help these.")


if __name__ == "__main__":
    main()
