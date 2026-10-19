#!/usr/bin/env python3
"""
Caches RF-DETR-Large's weights (needed for Method I in compare_detectors_v4.py).

Run this once, on the LOGIN NODE (not via sbatch) -- same reason as
prefetch_weights_v2.py: compute nodes here don't reliably reach every
domain a model download needs.

First run this on the login node:
    pip install rfdetr
    python prefetch_rfdetr.py

Unlike the YOLO/RT-DETR weights, rfdetr doesn't take a --weights-dir path --
it manages its own cache directory internally. This script's job is just to
force that download to happen now, on the login node, so the array job's
compute-node tasks find it already cached instead of trying (and failing)
to fetch it themselves.
"""
import sys

import numpy as np


def main():
    print("[1/2] importing rfdetr and instantiating RFDETRLarge "
          "(this triggers the weight download if not already cached)...",
          flush=True)
    try:
        from rfdetr import RFDETRLarge
        model = RFDETRLarge()
    except Exception:
        import traceback
        print("[FAIL] could not load RFDETRLarge:", flush=True)
        print(traceback.format_exc(), flush=True)
        print("-> if this is a connection error, confirm you're running "
              "on the login node, not via sbatch.", flush=True)
        sys.exit(1)

    print("[2/2] running one dummy forward pass to confirm it actually works...",
          flush=True)
    dummy = np.zeros((640, 640, 3), dtype=np.uint8)
    try:
        _ = model.predict(dummy, threshold=0.5)
    except Exception:
        import traceback
        print("[FAIL] RFDETRLarge loaded but predict() failed:", flush=True)
        print(traceback.format_exc(), flush=True)
        sys.exit(1)

    print("[ok] RF-DETR-Large is cached and working. "
          "Safe to submit the v4 array job now.", flush=True)


if __name__ == "__main__":
    main()
