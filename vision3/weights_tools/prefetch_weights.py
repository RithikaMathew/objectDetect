#!/usr/bin/env python3
"""
Download all detector weights once into a shared cache directory, so the
SLURM array job in run_compare_array.slurm never re-downloads anything
(each of its 5 tasks can start on its own GPU node without touching the
network, and without racing each other to write the same file).

Run this once, before the comparison array job:
    python prefetch_weights.py
(or via prefetch_weights.slurm, which runs it as its own short job)

NOTE: if this fails on a compute node, the most common cause on HPC
clusters is that compute nodes have no outbound internet access (only the
login node does). If step 0 below can't reach github.com/huggingface.co,
that's almost certainly it -- run this script on the login node instead of
via sbatch, or ask your cluster admins what proxy/module is needed for
outbound access from compute jobs.
"""
import os
import shutil
import socket
import sys
from pathlib import Path

WEIGHTS_DIR = Path(os.environ.get(
    "WEIGHTS_DIR", "/orange/xiangyan/rithika/vision/vision3/weights"
))


def log(msg: str):
    print(msg, flush=True)


def check_connectivity():
    log("[0/5] checking outbound network access...")
    hosts = ["github.com", "objects.githubusercontent.com",  # GitHub release assets
             "huggingface.co", "cdn-lfs.huggingface.co", "cdn-lfs-us-1.huggingface.co"]  # HF site + actual file storage
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
        log("      -> if only the cdn-lfs.* hosts failed: this cluster's compute nodes likely")
        log("         allowlist huggingface.co itself but not its file-storage CDN, which is")
        log("         where actual model weights are served from. Ask your cluster admins to")
        log("         allowlist *.huggingface.co and *.hf.co, or run this step on the login node.")
        log("      -> if github.com or objects.githubusercontent.com failed too: no outbound")
        log("         internet at all from this node — run on the login node instead of via sbatch.")
        sys.exit(1)


def fetch_ultralytics(filename: str, is_rtdetr: bool = False):
    from ultralytics import YOLO, RTDETR  # imported here so connectivity check runs first

    dest = WEIGHTS_DIR / filename
    if dest.exists():
        log(f"[skip] {dest} already present ({dest.stat().st_size / 1e6:.1f} MB)")
        return
    log(f"[fetch] {filename} -> {dest} ...")
    try:
        (RTDETR if is_rtdetr else YOLO)(str(dest))
    except Exception as e:
        log(f"[FAIL] {filename}: {type(e).__name__}: {e}")
        raise
    if not dest.exists():
        raise RuntimeError(
            f"{filename} did not land at {dest} after download call "
            f"(check ultralytics version — it may have downloaded to a different default path)"
        )
    log(f"[ok]   {filename} ({dest.stat().st_size / 1e6:.1f} MB)")


def fetch_visdrone():
    from huggingface_hub import hf_hub_download

    dest = WEIGHTS_DIR / "visdrone_yolo11x.pt"
    if dest.exists():
        log(f"[skip] {dest} already present ({dest.stat().st_size / 1e6:.1f} MB)")
        return
    log("[fetch] visdrone_yolo11x.pt (dronefreak/visdrone-yolov11x) ...")
    try:
        downloaded = hf_hub_download(repo_id="dronefreak/visdrone-yolov11x", filename="best.pt")
        shutil.copy(downloaded, dest)
    except Exception as e:
        log(f"[FAIL] visdrone_yolo11x.pt: {type(e).__name__}: {e}")
        raise
    log(f"[ok]   visdrone_yolo11x.pt ({dest.stat().st_size / 1e6:.1f} MB)")


def main():
    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    check_connectivity()

    steps = [
        ("[1/5]", lambda: fetch_ultralytics("yolov8x.pt")),
        ("[2/5]", lambda: fetch_ultralytics("yolo11x.pt")),
        ("[3/5]", lambda: fetch_ultralytics("rtdetr-l.pt", is_rtdetr=True)),
        ("[4/5]", fetch_visdrone),
    ]

    failed = []
    for tag, step in steps:
        log(f"{tag} starting...")
        try:
            step()
        except Exception:
            import traceback
            log(f"{tag} FAILED with an unhandled exception:")
            log(traceback.format_exc())
            failed.append(tag)

    log("[5/5] summary:")
    if failed:
        log(f"      FAILED steps: {failed}")
        log(f"      weights dir contents: {sorted(p.name for p in WEIGHTS_DIR.glob('*'))}")
        sys.exit(1)

    log(f"      all weights cached in {WEIGHTS_DIR}")
    for f in sorted(WEIGHTS_DIR.glob("*.pt")):
        log(f"      {f.name}  ({f.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()