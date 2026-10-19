#!/usr/bin/env python3
"""
Extends the v1 weight cache with yolo26x.pt (needed for Method F).
Method G reuses rtdetr-l.pt, already fetched by prefetch_weights.py.

Run this once, on the LOGIN NODE (not via sbatch) -- see prefetch_weights.py's
comments on why: compute nodes here don't reliably reach the domains model
downloads actually need.

    python prefetch_weights_v2.py
"""
import os
import socket
import sys
from pathlib import Path

WEIGHTS_DIR = Path(os.environ.get(
    "WEIGHTS_DIR", "/orange/xiangyan/rithika/vision/vision3/weights"
))


def log(msg: str):
    print(msg, flush=True)


def check_connectivity():
    log("[0/2] checking outbound network access...")
    hosts = ["github.com", "objects.githubusercontent.com"]
    unreachable = []
    for host in hosts:
        try:
            socket.create_connection((host, 443), timeout=10)
            log(f"      OK: can reach {host}")
        except OSError as e:
            log(f"      FAIL: cannot reach {host} ({e})")
            unreachable.append(host)
    if unreachable:
        log(f"      -> unreachable: {unreachable}")
        log("      -> run this on the login node instead of via sbatch.")
        sys.exit(1)


def fetch_yolo26x():
    from ultralytics import YOLO

    dest = WEIGHTS_DIR / "yolo26x.pt"
    if dest.exists():
        log(f"[skip] {dest} already present ({dest.stat().st_size / 1e6:.1f} MB)")
        return
    log(f"[fetch] yolo26x.pt -> {dest} ...")
    try:
        YOLO(str(dest))
    except Exception:
        import traceback
        log("[FAIL] yolo26x.pt:")
        log(traceback.format_exc())
        raise
    if not dest.exists():
        raise RuntimeError(f"yolo26x.pt did not land at {dest}")
    log(f"[ok]   yolo26x.pt ({dest.stat().st_size / 1e6:.1f} MB)")


def main():
    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    check_connectivity()

    log("[1/2] starting...")
    try:
        fetch_yolo26x()
    except Exception:
        log("[2/2] FAILED — see traceback above")
        sys.exit(1)

    log("[2/2] done. rtdetr-l.pt (for Method G) should already be present from prefetch_weights.py:")
    rtdetr = WEIGHTS_DIR / "rtdetr-l.pt"
    log(f"      rtdetr-l.pt present: {rtdetr.exists()}")
    log(f"\nweights dir contents: {sorted(p.name for p in WEIGHTS_DIR.glob('*.pt'))}")


if __name__ == "__main__":
    main()
