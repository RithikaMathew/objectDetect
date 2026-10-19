"""
A/B the old IoU tracker against the new centroid tracker on a known window.

Runs the SAME tiled detections through both association strategies, so the
only variable is the association rule. Prints a per-link table and a summary.

This is the verification that the fix works, and the source table for the
paper's tracker-ablation figure.

Usage:
  python tracker_ablation.py VIDEO --start 403 --end 415
"""

import argparse
import csv
import os

import cv2
import numpy as np
from ultralytics import YOLO

from pilot_detect_v2 import compute_tiles, detect_tiled, COCO_CLASSES
from vru_tracker import VruTracker, iou_xyxy, centroid, diagonal


class OldIouTracker:
    """Verbatim reproduction of SimpleIouTracker from pilot_detect.py."""

    def __init__(self, iou_match_thresh=0.3, max_missed=3):
        self.next_id = 1
        self.tracks = {}
        self.iou_match_thresh = iou_match_thresh
        self.max_missed = max_missed

    def update(self, detections):
        active = [tid for tid, t in self.tracks.items() if t["alive"]]
        pairs = []
        for tid in active:
            for di, det in enumerate(detections):
                v = iou_xyxy(self.tracks[tid]["bbox"], det[:4])
                if v >= self.iou_match_thresh:
                    pairs.append((v, tid, di))
        pairs.sort(reverse=True, key=lambda p: p[0])
        mt, md = set(), set()
        for v, tid, di in pairs:
            if tid in mt or di in md:
                continue
            mt.add(tid)
            md.add(di)
            t = self.tracks[tid]
            t["bbox"], t["cls"] = detections[di][:4], detections[di][5]
            t["hits"] += 1
            t["missed"] = 0
        for tid in active:
            if tid not in mt:
                self.tracks[tid]["missed"] += 1
                if self.tracks[tid]["missed"] > self.max_missed:
                    self.tracks[tid]["alive"] = False
        for di, det in enumerate(detections):
            if di not in md:
                self.tracks[self.next_id] = {"bbox": det[:4], "cls": det[5],
                                             "hits": 1, "missed": 0, "alive": True}
                self.next_id += 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video_path")
    ap.add_argument("--start", type=float, default=403.0)
    ap.add_argument("--end", type=float, default=415.0)
    ap.add_argument("--weights", default="yolov8l.pt")
    ap.add_argument("--conf", type=float, default=0.05)
    ap.add_argument("--stride", type=int, default=5,
                    help="Must match the pipeline you are auditing (old default: 5).")
    ap.add_argument("--imgsz", type=int, default=1280)
    ap.add_argument("--cls", default="bicycle")
    ap.add_argument("--outdir", default="pilot_output/ablation")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    cap = cv2.VideoCapture(args.video_path)
    if not cap.isOpened():
        raise SystemExit(f"FATAL: could not open {args.video_path} (cwd={os.getcwd()})")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    dt = args.stride / fps
    model = YOLO(args.weights)
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(args.start * fps))

    old = OldIouTracker()
    new = VruTracker(max_center_dist_frac=1.0)

    n_frames = int((args.end - args.start) * fps)
    prev_box = None
    rows = []
    tiles = None

    print(f"fps={fps:.2f}  stride={args.stride}  dt={dt:.3f}s  "
          f"window={args.start}-{args.end}s  conf={args.conf}\n")
    print(f"{'t':>8}  {'conf':>5}  {'IoU':>6} {'iou_ok':>7}  "
          f"{'cdist':>6} {'norm':>5} {'cen_ok':>7}")
    print("-" * 60)

    for i in range(n_frames):
        ok, frame = cap.read()
        if not ok:
            break
        if i % args.stride != 0:
            continue
        t = args.start + i / fps
        if tiles is None:
            tiles = compute_tiles(frame.shape)

        dets, _ = detect_tiled(model, frame, tiles, COCO_CLASSES, args.conf, args.imgsz)
        old.update(dets)
        new.update(dets, t, dt)

        target = [d for d in dets if d[5] == args.cls]
        if target:
            best = max(target, key=lambda d: d[4])
            box, conf = list(best[:4]), best[4]
            if prev_box is not None:
                v = iou_xyxy(prev_box, box)
                c1, c2 = centroid(prev_box), centroid(box)
                d = float(np.hypot(c1[0] - c2[0], c1[1] - c2[1]))
                nrm = d / max(1.0, (diagonal(prev_box) + diagonal(box)) / 2)
                print(f"{t:8.2f}  {conf:5.2f}  {v:6.3f} {'PASS' if v>=.3 else 'FAIL':>7}  "
                      f"{d:6.1f} {nrm:5.2f} {'PASS' if nrm<=1.0 else 'FAIL':>7}")
                rows.append([f"{t:.2f}", f"{conf:.3f}", f"{v:.3f}", v >= 0.3,
                             f"{d:.1f}", f"{nrm:.2f}", nrm <= 1.0])
            prev_box = box
        else:
            prev_box = None

    cap.release()

    old_best = max([t["hits"] for t in old.tracks.values()
                    if t["cls"] == args.cls] or [0])
    new_tracks = [t for t in new.tracks.values() if t.cls == args.cls]
    new_best = max([t.hits for t in new_tracks] or [0])
    min_hits = max(2, int(round(0.5 / dt)))
    old_min_hits = max(3, round((fps / args.stride) * 1.0))

    with open(os.path.join(args.outdir, "tracker_ablation.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "conf", "iou", "iou_pass", "centroid_dist",
                    "norm_dist", "centroid_pass"])
        w.writerows(rows)

    n_iou_pass = sum(1 for r in rows if r[3])
    n_cen_pass = sum(1 for r in rows if r[6])

    print("\n" + "=" * 60)
    print(f"ASSOCIATION LINKS ({args.cls}):")
    print(f"  IoU >= 0.3           : {n_iou_pass}/{len(rows)} passed")
    print(f"  norm. centroid <= 1.0: {n_cen_pass}/{len(rows)} passed")
    print(f"\nLONGEST TRACK:")
    print(f"  OLD IoU tracker : {old_best} hits   (needs {old_min_hits}) "
          f"-> {'COUNTED' if old_best >= old_min_hits else 'NOT COUNTED'}")
    print(f"  NEW centroid    : {new_best} hits   (needs {min_hits}) "
          f"-> {'COUNTED' if new_best >= min_hits else 'NOT COUNTED'}")
    print(f"\nTotal {args.cls} tracks: old={sum(1 for t in old.tracks.values() if t['cls']==args.cls)}"
          f"  new={len(new_tracks)}")
    print(f"CSV: {os.path.join(args.outdir, 'tracker_ablation.csv')}")


if __name__ == "__main__":
    main()
