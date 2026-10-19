#!/usr/bin/env python3
"""
xclip_overlay_v2.py

v1 + (a) YOLO detection/tracking so people and vehicles are found by the script
itself, (b) vehicle boxes (car/bus/truck) with a running count, (c) a yellow
header bar with the method name and running counts, (d) multiple text prompts
per class so a STANDING person still lands on PEDESTRIAN.

People source:
  * no --csv      : people come from YOLO + ByteTrack (--detector weights)
  * with --csv    : people come from the CSV exactly like v1 (columns:
                    tracker_id, frame (1-based), cx, cy, w, h); YOLO is only
                    used for vehicles (skip that with --no-vehicles)

Per person track: rolling buffer of the last --window square crops; every
--stride frames (once --min-frames crops exist) 8 crops are sampled and scored
with X-CLIP against all prompts. Softmax is taken over ALL prompts, then the
probabilities of each class's prompts are summed (bike prompts -> BICYCLIST,
walk prompts -> PEDESTRIAN), then EMA-smoothed. Causal, like v1.

Counting ("so far"): a person track is counted as a bicyclist / pedestrian once
its smoothed label has been the same for --confirm consecutive score updates
(each track counts once per class, so ID switches can inflate counts).
Vehicles are counted once a track has been seen for --veh-min frames.

Usage:
    python xclip_overlay_v2.py --video test.mp4 \
        --out pilot_output/compare_v4/xclip_overlay_v2/overlay.mp4
    # people from an existing CSV, YOLO only for cars:
    python xclip_overlay_v2.py --video test.mp4 --csv track_j_diagnostic.csv \
        --out .../overlay.mp4

Models download on first use; cache X-CLIP on the login node first.
"""
import argparse
import csv
import os
import sys
from collections import defaultdict, deque

import cv2
import numpy as np
import torch
from transformers import XCLIPModel, XCLIPProcessor

MODEL_NAME = "microsoft/xclip-base-patch32"
N_FRAMES = 8
REQUIRED_COLS = ["tracker_id", "frame", "cx", "cy", "w", "h"]

CLASSES = [("BICYCLIST", (0, 200, 0)), ("PEDESTRIAN", (0, 140, 255))]
VEHICLE_CLS = {2: "car", 5: "bus", 7: "truck"}   # COCO ids
VEH_COLOR = (255, 120, 0)                         # BGR (blue-ish)
HEADER_COLOR = (0, 255, 255)                      # BGR yellow


def load_rows(csv_path, track_ids):
    by_frame = defaultdict(list)
    seen = set()
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLS if c not in (reader.fieldnames or [])]
        if missing:
            sys.exit(f"ERROR: CSV {csv_path} is missing columns {missing}; "
                     f"found {reader.fieldnames}")
        for row in reader:
            tid = int(row["tracker_id"])
            if track_ids is not None and tid not in track_ids:
                continue
            by_frame[int(row["frame"])].append(
                (tid, float(row["cx"]), float(row["cy"]),
                 float(row["w"]), float(row["h"])))
            seen.add(tid)
    return by_frame, seen


def crop_square(frame, cx, cy, w, h, pad, out=224):
    H, W = frame.shape[:2]
    side = max(max(w, h) * (1 + pad), 48)
    x1, y1 = int(cx - side / 2), int(cy - side / 2)
    x2, y2 = int(cx + side / 2), int(cy + side / 2)
    x1, x2 = max(0, x1), min(W, x2)
    y1, y2 = max(0, y1), min(H, y2)
    crop = frame[y1:y2, x1:x2]
    if crop.size == 0:
        return None
    return cv2.resize(crop, (out, out), interpolation=cv2.INTER_CUBIC)


def _tag(img, x1, y, text, fs, thick, color):
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, fs, thick)
    cv2.rectangle(img, (x1, y - th - 3), (x1 + tw + 4, y + 3), (0, 0, 0), -1)
    cv2.putText(img, text, (x1 + 2, y), cv2.FONT_HERSHEY_SIMPLEX, fs,
                color, thick, cv2.LINE_AA)


def draw_person(img, box, tid, cls, probs, scale):
    cx, cy, w, h = box
    x1, y1 = int(cx - w / 2), int(cy - h / 2)
    x2, y2 = int(cx + w / 2), int(cy + h / 2)
    thick = max(1, int(round(scale * 2)))
    if cls is None:
        color = (255, 255, 255)
        lines = [f"id {tid} ..."]
    else:
        color = CLASSES[cls][1]
        lines = [f"id {tid} {CLASSES[cls][0]} {probs[cls]:.2f}"]
        lines += [f"{c[0][:4].lower()} {p:.2f}" for c, p in zip(CLASSES, probs)]
    cv2.rectangle(img, (x1, y1), (x2, y2), color, thick)
    line_h = int(22 * scale) + 6
    y = max(line_h, y1 - 4 - line_h * (len(lines) - 1))
    for i, t in enumerate(lines):
        fs = scale * (0.7 if i == 0 else 0.5)
        _tag(img, x1, y + i * line_h, t, fs, thick,
             color if i == 0 else (255, 255, 255))


def draw_vehicle(img, box, tid, name, scale):
    cx, cy, w, h = box
    x1, y1 = int(cx - w / 2), int(cy - h / 2)
    x2, y2 = int(cx + w / 2), int(cy + h / 2)
    thick = max(1, int(round(scale * 2)))
    cv2.rectangle(img, (x1, y1), (x2, y2), VEH_COLOR, thick)
    _tag(img, x1, max(int(22 * scale), y1 - 4), f"{name} {tid}",
         scale * 0.6, thick, VEH_COLOR)


def add_header(img, scale, counts, fi, total):
    """Pad a yellow bar on top of the frame (does not cover the video)."""
    bar = int(70 * scale)
    out = cv2.copyMakeBorder(img, bar, 0, 0, 0, cv2.BORDER_CONSTANT,
                             value=HEADER_COLOR)
    thick = max(1, int(round(scale * 2)))
    fs = scale * 0.7
    l1 = "Zero-shot X-CLIP (video-text) classification of tracked people"
    l2 = (f"Bicyclists: {counts[0]}   Pedestrians: {counts[1]}   "
          f"Vehicles: {counts[2]}   |   frame {fi}/{total if total > 0 else '?'}")
    cv2.putText(out, l1, (10, int(bar * 0.42)), cv2.FONT_HERSHEY_SIMPLEX, fs,
                (0, 0, 0), thick, cv2.LINE_AA)
    cv2.putText(out, l2, (10, int(bar * 0.85)), cv2.FONT_HERSHEY_SIMPLEX, fs,
                (0, 0, 0), thick, cv2.LINE_AA)
    return out, bar


def detect(model, frame, args):
    """One YOLO track step -> (people, vehicles)."""
    res = model.track(frame, persist=True, tracker=args.tracker,
                      conf=args.det_conf, imgsz=args.imgsz,
                      classes=[0] + list(VEHICLE_CLS), verbose=False)[0]
    people, vehicles = [], []
    if res.boxes is None or res.boxes.id is None:
        return people, vehicles
    xyxy = res.boxes.xyxy.cpu().numpy()
    ids = res.boxes.id.int().cpu().tolist()
    cls = res.boxes.cls.int().cpu().tolist()
    for (x1, y1, x2, y2), i, c in zip(xyxy, ids, cls):
        cx, cy, w, h = (x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1
        if c == 0:
            people.append((i, float(cx), float(cy), float(w), float(h)))
        else:
            vehicles.append((i, VEHICLE_CLS[c], float(cx), float(cy),
                             float(w), float(h)))
    return people, vehicles


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--video", required=True)
    ap.add_argument("--out", required=True, help="output .mp4 path")
    ap.add_argument("--csv", default=None,
                    help="tracks CSV for people (default: detect people with YOLO)")
    ap.add_argument("--track-ids", type=int, nargs="+", default=None,
                    help="only these person tracker_ids")
    ap.add_argument("--detector", default="yolo11x.pt", help="ultralytics weights")
    ap.add_argument("--tracker", default="bytetrack.yaml")
    ap.add_argument("--det-conf", type=float, default=0.15,
                    help="YOLO confidence; low helps distant/standing people")
    ap.add_argument("--imgsz", type=int, default=1280)
    ap.add_argument("--no-vehicles", action="store_true",
                    help="with --csv: skip YOLO and vehicle detection")
    ap.add_argument("--veh-min", type=int, default=5,
                    help="frames a vehicle track must live before it is counted")
    ap.add_argument("--confirm", type=int, default=2,
                    help="consecutive same-label score updates to count a person")
    ap.add_argument("--window", type=int, default=30)
    ap.add_argument("--min-frames", type=int, default=8)
    ap.add_argument("--stride", type=int, default=5)
    ap.add_argument("--pad", type=float, default=0.6)
    ap.add_argument("--ema", type=float, default=0.5)
    ap.add_argument("--bike-prompts", nargs="+",
                    default=["a person riding a bicycle",
                             "a person riding a bike on the road"])
    ap.add_argument("--walk-prompts", nargs="+",
                    default=["a person walking", "a person standing still"])
    ap.add_argument("--start-frame", type=int, default=1,
                    help="first frame to process (1-based); frame numbers stay "
                         "absolute so they still match a CSV")
    ap.add_argument("--max-frames", type=int, default=0,
                    help="last frame index to process (absolute, 0 = to the end)")
    args = ap.parse_args()

    if not (0 < args.ema <= 1):
        sys.exit("ERROR: --ema must be in (0, 1]")
    if args.min_frames < 2 or args.min_frames > args.window:
        sys.exit("ERROR: need 2 <= --min-frames <= --window")
    if args.no_vehicles and not args.csv:
        sys.exit("ERROR: --no-vehicles needs --csv (otherwise nothing is detected)")

    nb = len(args.bike_prompts)
    prompts = list(args.bike_prompts) + list(args.walk_prompts)

    by_frame = None
    if args.csv:
        track_ids = set(args.track_ids) if args.track_ids else None
        by_frame, seen = load_rows(args.csv, track_ids)
        if not seen:
            sys.exit("ERROR: no matching tracks in CSV")
        print(f"CSV tracks: {sorted(seen)}")

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        sys.exit(f"ERROR: cannot open video {args.video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    scale = max(0.6, H / 1080.0 * 0.9)
    bar = int(70 * scale)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    writer = cv2.VideoWriter(args.out, cv2.VideoWriter_fourcc(*"mp4v"),
                             fps, (W, H + bar))
    if not writer.isOpened():
        sys.exit(f"ERROR: cannot open VideoWriter for {args.out}")

    yolo = None
    if not args.no_vehicles:
        from ultralytics import YOLO
        print(f"Loading detector {args.detector} ...")
        yolo = YOLO(args.detector)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading {MODEL_NAME} on {device} ...")
    processor = XCLIPProcessor.from_pretrained(MODEL_NAME)
    model = XCLIPModel.from_pretrained(MODEL_NAME).to(device).eval()

    buffers = defaultdict(lambda: deque(maxlen=args.window))
    last_scored, smooth = {}, {}
    streak = {}                                  # tid -> (label, run length)
    counted = [set(), set()]                     # bicyclist ids, pedestrian ids
    track_len = defaultdict(int)                 # frames each person track lived
    veh_len = defaultdict(int)
    veh_counted = set()
    score_log = []
    skipped_empty = 0

    fi = 0
    if args.start_frame > 1:
        cap.set(cv2.CAP_PROP_POS_FRAMES, args.start_frame - 1)
        fi = args.start_frame - 1
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        fi += 1
        if args.max_frames and fi > args.max_frames:
            break

        vehicles = []
        if yolo is not None:
            det_people, vehicles = detect(yolo, frame, args)
        if by_frame is not None:
            present = by_frame.get(fi, [])
        else:
            present = det_people
            if args.track_ids:
                present = [p for p in present if p[0] in set(args.track_ids)]

        for vid, name, *_ in vehicles:
            veh_len[vid] += 1
            if veh_len[vid] >= args.veh_min:
                veh_counted.add(vid)

        for tid, cx, cy, w, h in present:
            track_len[tid] += 1
            crop = crop_square(frame, cx, cy, w, h, args.pad)
            if crop is None:
                skipped_empty += 1
                continue
            buffers[tid].append(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))

        due = []
        for tid, *_ in present:
            if len(buffers[tid]) < args.min_frames:
                continue
            if tid not in last_scored or fi - last_scored[tid] >= args.stride:
                due.append(tid)

        if due:
            clips = []
            for tid in due:
                buf = list(buffers[tid])
                idx = np.linspace(0, len(buf) - 1, N_FRAMES).round().astype(int)
                clips.append([buf[i] for i in idx])
            inputs = processor(text=prompts, videos=clips,
                               return_tensors="pt", padding=True)
            inputs = {k: v.to(device) for k, v in inputs.items()}
            with torch.no_grad():
                logits = model(**inputs).logits_per_video
            allp = logits.softmax(dim=1).cpu().numpy()
            if allp.shape != (len(due), len(prompts)):
                sys.exit(f"ERROR: unexpected logits shape {allp.shape}, "
                         f"expected {(len(due), len(prompts))}")
            probs = np.stack([allp[:, :nb].sum(1), allp[:, nb:].sum(1)], axis=1)
            for tid, p in zip(due, probs):
                smooth[tid] = p if tid not in smooth else \
                    args.ema * p + (1 - args.ema) * smooth[tid]
                last_scored[tid] = fi
                lab = int(np.argmax(smooth[tid]))
                prev, run = streak.get(tid, (None, 0))
                run = run + 1 if prev == lab else 1
                streak[tid] = (lab, run)
                if run >= args.confirm:
                    counted[lab].add(tid)
                score_log.append([tid, fi] + [round(float(x), 3) for x in p] +
                                 [round(float(x), 3) for x in smooth[tid]])

        for vid, name, cx, cy, w, h in vehicles:
            draw_vehicle(frame, (cx, cy, w, h), vid, name, scale)
        for tid, cx, cy, w, h in present:
            if tid in smooth:
                p = smooth[tid]
                draw_person(frame, (cx, cy, w, h), tid, int(np.argmax(p)), p, scale)
            else:
                draw_person(frame, (cx, cy, w, h), tid, None, None, scale)

        out, _ = add_header(frame, scale,
                            (len(counted[0]), len(counted[1]), len(veh_counted)),
                            fi, total)
        writer.write(out)
        if fi % 100 == 0:
            print(f"frame {fi}/{total if total > 0 else '?'}")

    cap.release()
    writer.release()

    if fi <= max(0, args.start_frame - 1):
        sys.exit("ERROR: read 0 frames from video")
    if skipped_empty:
        print(f"WARNING: {skipped_empty} empty crops skipped (box outside frame)")

    log_path = os.path.splitext(args.out)[0] + "_scores.csv"
    with open(log_path, "w", newline="") as f:
        wtr = csv.writer(f)
        wtr.writerow(["tracker_id", "frame"] +
                     [c[0].lower() for c in CLASSES] +
                     [c[0].lower() + "_smooth" for c in CLASSES])
        wtr.writerows(score_log)

    print("\n=== person tracks ===")
    print("track | frames | scores | mean BICYCLIST | mean PEDESTRIAN")
    by_tid = defaultdict(list)
    for r in score_log:
        by_tid[r[0]].append(r[2 + len(CLASSES):])
    for tid in sorted(track_len):
        if tid in by_tid:
            m = np.mean(by_tid[tid], axis=0)
            print(f"{tid:5d} | {track_len[tid]:6d} | {len(by_tid[tid]):6d} | "
                  f"{m[0]:.2f} | {m[1]:.2f}")
        else:
            print(f"{tid:5d} | {track_len[tid]:6d} |      0 | never scored "
                  f"(track shorter than --min-frames={args.min_frames}?)")

    print(f"\nFinal counts: bicyclists={len(counted[0])} "
          f"pedestrians={len(counted[1])} vehicles={len(veh_counted)}")
    print(f"Video: {args.out}")
    print(f"Scores: {log_path}")


if __name__ == "__main__":
    main()
