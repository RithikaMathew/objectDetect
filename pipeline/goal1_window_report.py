"""Summarize a --dump-dets CSV from the 3-minute window.

Separates "the cyclist class never fired" from "it fired and the tracker or
the gates dropped it."
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("dets_csv")
    args = ap.parse_args()
    by_source = Counter()
    by_class = Counter()
    n = 0
    with open(args.dets_csv) as f:
        for r in csv.DictReader(f):
            n += 1
            by_class[r["class"]] += 1
            by_source[(r.get("source") or "primary", r["class"])] += 1
    print(f"raw VRU detections: {n}")
    for cls, k in by_class.most_common():
        print(f"  {cls}: {k}")
    print("by source:")
    for (src, cls), k in sorted(by_source.items()):
        print(f"  {src} {cls}: {k}")
    if by_class.get("cyclist", 0) + by_class.get("bicycle", 0) == 0:
        print("NO cyclist or bicycle box in this window. The miss is the detector,")
        print("not the confirmation gates.")
    else:
        print("At least one cyclist-class box was emitted. If the annotated video")
        print("still has no rider, the tracker or the gates dropped it.")


if __name__ == "__main__":
    main()
