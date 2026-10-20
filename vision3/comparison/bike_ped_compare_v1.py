#!/usr/bin/env python3
"""
bike_ped_compare_v1.py

Run several BICYCLIST-vs-PEDESTRIAN classifiers on the same tracks and write
one annotated mp4 per model, so you can watch them side by side and compare.

Every backend reduces to one number per track: p_bike in [0, 1]. A track is
drawn as BICYCLIST if its smoothed p_bike >= that backend's threshold, else
PEDESTRIAN. One streaming pass over the video; each track keeps a rolling
buffer of its last --window crops (224x224) and box history. Every --stride
frames (once a track has --min-frames crops) every backend re-scores it.
Labels are causal (they reflect the recent past of the track).

Backends (--backends, default: xclip clip siglip videomae speed):
  xclip      zero-shot video-text (microsoft/xclip-base-patch32)
  clip       zero-shot image-text on sampled crops (--clip-model)
  siglip     same, with SigLIP (--siglip-model)
  videomae   Kinetics-400 fine-tuned action classifier; p_bike = summed
             probability of every class whose name contains bike/bicycle/cycling
             (matched classes are printed at startup, check them)
  speed      no model: median box-height-normalised speed from the CSV
  yolo_bike  needs --yolo-weights (COCO weights); p_bike = how much of the
             nearest detected bicycle box lies inside the person box
  vlm        needs --vlm-url and --vlm-model (OpenAI-compatible server, e.g.
             vLLM serving Qwen2.5-VL); answers "bicyclist" / "pedestrian"

Accuracy: pass --truth 1=pedestrian 2=bicyclist 5=pedestrian (tracker_id=class)
and a per-track / macro accuracy table is printed and written to summary.csv.
Accuracy only counts frames where the backend already has a label.

Usage:
    python bike_ped_compare_v1.py \\
        --video test.mp4 \\
        --csv pilot_output/compare_v4/track_j_diagnostic.csv \\
        --outdir pilot_output/compare_v4/bike_ped_compare_v1 \\
        --truth 1=pedestrian 2=bicyclist 5=pedestrian

CSV columns required: tracker_id, frame (1-based), cx, cy, w, h.
HF models download on first use; run once on the login node (internet).
"""
import argparse
import base64
import csv
import json
import math
import os
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict, deque
from types import SimpleNamespace

import cv2
import numpy as np
import torch

LABELS = ["BICYCLIST", "PEDESTRIAN"]
COLORS = {"BICYCLIST": (0, 200, 0), "PEDESTRIAN": (0, 140, 255)}
REQUIRED_COLS = ["tracker_id", "frame", "cx", "cy", "w", "h"]
ALL_BACKENDS = ["xclip", "clip", "siglip", "videomae", "speed", "yolo_bike", "vlm"]
DEFAULT_BACKENDS = ["xclip", "clip", "siglip", "videomae", "speed"]
N_XCLIP = 8


# --------------------------------------------------------------------------
# data helpers
# --------------------------------------------------------------------------
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


def sample(seq, n):
    idx = np.linspace(0, len(seq) - 1, n).round().astype(int)
    return [seq[i] for i in idx]


def draw_track(img, box, tid, label, p, scale):
    cx, cy, w, h = box
    x1, y1 = int(cx - w / 2), int(cy - h / 2)
    x2, y2 = int(cx + w / 2), int(cy + h / 2)
    thick = max(1, int(round(scale * 2)))
    if label is None:
        color, text = (255, 255, 255), f"id {tid} ..."
    else:
        color, text = COLORS[label], f"id {tid} {label} {p:.2f}"
    cv2.rectangle(img, (x1, y1), (x2, y2), color, thick)
    fs = scale * 0.7
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, fs, thick)
    yy = max(th + 6, y1 - 6)
    cv2.rectangle(img, (x1, yy - th - 4), (x1 + tw + 4, yy + 4), (0, 0, 0), -1)
    cv2.putText(img, text, (x1 + 2, yy), cv2.FONT_HERSHEY_SIMPLEX, fs, color,
                thick, cv2.LINE_AA)


def draw_banner(img, text, scale):
    thick = max(1, int(round(scale * 2)))
    fs = scale * 0.9
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, fs, thick)
    cv2.rectangle(img, (0, 0), (tw + 16, th + 16), (0, 0, 0), -1)
    cv2.putText(img, text, (8, th + 8), cv2.FONT_HERSHEY_SIMPLEX, fs,
                (255, 255, 255), thick, cv2.LINE_AA)


# --------------------------------------------------------------------------
# backends: predict(items) -> list of p_bike (float) or None (no answer)
# item fields: tid, frame_idx, frame (BGR full), box (cx,cy,w,h),
#              crops (list of RGB 224x224), hist (list of (f,cx,cy,w,h))
# --------------------------------------------------------------------------
class Backend:
    name = "base"
    thr = 0.5

    def predict(self, items):
        raise NotImplementedError


class XCLIPBackend(Backend):
    name = "xclip"

    def __init__(self, args, device):
        from transformers import XCLIPModel, XCLIPProcessor
        self.device = device
        self.prompts = [args.prompt_bike, args.prompt_walk]
        print(f"[xclip] loading {args.xclip_model}")
        self.proc = XCLIPProcessor.from_pretrained(args.xclip_model)
        self.model = XCLIPModel.from_pretrained(args.xclip_model).to(device).eval()

    def predict(self, items):
        clips = [sample(it.crops, N_XCLIP) for it in items]
        inputs = self.proc(text=self.prompts, videos=clips,
                           return_tensors="pt", padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            logits = self.model(**inputs).logits_per_video
        if tuple(logits.shape) != (len(items), 2):
            sys.exit(f"ERROR [xclip]: logits shape {tuple(logits.shape)}, "
                     f"expected {(len(items), 2)}")
        return [float(x) for x in logits.softmax(dim=1)[:, 0].cpu()]


class ImageTextBackend(Backend):
    """CLIP / SigLIP: score sampled crops, average p_bike over them."""

    def __init__(self, name, model_id, args, device):
        from transformers import AutoModel, AutoProcessor
        self.name = name
        self.device = device
        self.n_img = args.img_frames
        self.prompts = [args.prompt_bike, args.prompt_walk]
        self.pad = "max_length" if "siglip" in model_id.lower() else True
        print(f"[{name}] loading {model_id}")
        self.proc = AutoProcessor.from_pretrained(model_id)
        self.model = AutoModel.from_pretrained(model_id).to(device).eval()

    def predict(self, items):
        out = []
        for it in items:
            imgs = sample(it.crops, self.n_img)
            inputs = self.proc(text=self.prompts, images=imgs,
                               padding=self.pad, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with torch.no_grad():
                logits = self.model(**inputs).logits_per_image
            if tuple(logits.shape) != (len(imgs), 2):
                sys.exit(f"ERROR [{self.name}]: logits shape "
                         f"{tuple(logits.shape)}, expected {(len(imgs), 2)}")
            out.append(float(logits.softmax(dim=1)[:, 0].mean().cpu()))
        return out


class VideoMAEBackend(Backend):
    name = "videomae"
    thr = 0.3  # bike mass is spread over few of 400 classes; tune with --thr

    def __init__(self, args, device):
        from transformers import (VideoMAEForVideoClassification,
                                  VideoMAEImageProcessor)
        self.device = device
        print(f"[videomae] loading {args.videomae_model}")
        self.proc = VideoMAEImageProcessor.from_pretrained(args.videomae_model)
        self.model = VideoMAEForVideoClassification.from_pretrained(
            args.videomae_model).to(device).eval()
        self.n = self.model.config.num_frames
        id2label = self.model.config.id2label
        self.bike_ids = [int(i) for i, l in id2label.items()
                         if any(k in l.lower() for k in ("bike", "bicycle", "cycling"))]
        if not self.bike_ids:
            sys.exit("ERROR [videomae]: no class names containing bike/bicycle/"
                     "cycling in this model's id2label")
        print("[videomae] bike classes: " +
              ", ".join(id2label[i] for i in self.bike_ids))

    def predict(self, items):
        out = []
        for it in items:
            frames = sample(it.crops, self.n)
            inputs = self.proc(frames, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with torch.no_grad():
                logits = self.model(**inputs).logits
            probs = logits.softmax(dim=-1)[0]
            out.append(float(probs[self.bike_ids].sum().cpu()))
        return out


class SpeedBackend(Backend):
    """No model: cyclists move faster (in box-heights per frame) than walkers.
    Threshold is a starting guess, tune with --speed-thr."""
    name = "speed"

    def __init__(self, args):
        self.s_thr = args.speed_thr

    def predict(self, items):
        out = []
        for it in items:
            h = it.hist
            if len(h) < 2:
                out.append(None)
                continue
            v = []
            for (f0, x0, y0, _, h0), (f1, x1, y1, _, h1) in zip(h[:-1], h[1:]):
                dist = math.hypot(x1 - x0, y1 - y0) / max(f1 - f0, 1)
                v.append(dist / max((h0 + h1) / 2.0, 1.0))
            s = float(np.median(v))
            z = (s - self.s_thr) / (self.s_thr * 0.25)
            out.append(1.0 / (1.0 + math.exp(-max(min(z, 50.0), -50.0))))
        return out


class YoloBikeBackend(Backend):
    """p_bike = max over detected bicycles of (bike box area inside person box)
    / (bike box area). Needs COCO-style weights that have a 'bicycle' class."""
    name = "yolo_bike"
    thr = 0.3

    def __init__(self, args):
        try:
            from ultralytics import YOLO
        except ImportError:
            sys.exit("ERROR [yolo_bike]: ultralytics is not installed")
        self.model = YOLO(args.yolo_weights)
        self.conf = args.yolo_conf
        ids = [i for i, n in self.model.names.items() if n == "bicycle"]
        if not ids:
            sys.exit("ERROR [yolo_bike]: weights have no class named 'bicycle'")
        self.cls = ids[0]
        self._frame = None
        self._bikes = None

    def _get_bikes(self, it):
        if it.frame_idx != self._frame:
            r = self.model.predict(it.frame, conf=self.conf, classes=[self.cls],
                                   verbose=False)[0]
            self._bikes = r.boxes.xyxy.cpu().numpy()
            self._frame = it.frame_idx
        return self._bikes

    def predict(self, items):
        out = []
        for it in items:
            cx, cy, w, h = it.box
            px1, py1, px2, py2 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
            best = 0.0
            for bx1, by1, bx2, by2 in self._get_bikes(it):
                iw = max(0.0, min(px2, bx2) - max(px1, bx1))
                ih = max(0.0, min(py2, by2) - max(py1, by1))
                area = max((bx2 - bx1) * (by2 - by1), 1e-6)
                best = max(best, float(iw * ih / area))
            out.append(best)
        return out


class VLMBackend(Backend):
    """OpenAI-compatible chat endpoint (e.g. vLLM). Answer is hard: 1.0 / 0.0.
    Unparseable answers return None and are counted."""
    name = "vlm"
    PROMPT = ("These are consecutive crops of one road user from a traffic "
              "camera. Is this person a bicyclist (riding a bicycle) or a "
              "pedestrian (on foot)? Answer with exactly one word: "
              "bicyclist or pedestrian.")

    def __init__(self, args):
        self.url = args.vlm_url.rstrip("/") + "/chat/completions"
        self.model = args.vlm_model
        self.n_img = args.vlm_frames
        self.unparsed = 0

    def _ask(self, crops):
        content = [{"type": "text", "text": self.PROMPT}]
        for c in crops:
            ok, buf = cv2.imencode(".jpg", cv2.cvtColor(c, cv2.COLOR_RGB2BGR))
            if not ok:
                sys.exit("ERROR [vlm]: jpeg encode failed")
            b64 = base64.b64encode(buf.tobytes()).decode()
            content.append({"type": "image_url",
                            "image_url": {"url": "data:image/jpeg;base64," + b64}})
        payload = {"model": self.model, "max_tokens": 8, "temperature": 0,
                   "messages": [{"role": "user", "content": content}]}
        req = urllib.request.Request(
            self.url, data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.loads(r.read())
        except urllib.error.HTTPError as e:
            sys.exit(f"ERROR [vlm]: HTTP {e.code}: {e.read().decode()[:500]}")
        except urllib.error.URLError as e:
            sys.exit(f"ERROR [vlm]: cannot reach {self.url}: {e}")
        return data["choices"][0]["message"]["content"].lower()

    def predict(self, items):
        out = []
        for it in items:
            ans = self._ask(sample(it.crops, self.n_img))
            b, p = "bicyclist" in ans, "pedestrian" in ans
            if b and not p:
                out.append(1.0)
            elif p and not b:
                out.append(0.0)
            else:
                self.unparsed += 1
                out.append(None)
        return out


def build_backends(names, args, device):
    out = []
    for n in names:
        if n == "xclip":
            out.append(XCLIPBackend(args, device))
        elif n == "clip":
            out.append(ImageTextBackend("clip", args.clip_model, args, device))
        elif n == "siglip":
            out.append(ImageTextBackend("siglip", args.siglip_model, args, device))
        elif n == "videomae":
            out.append(VideoMAEBackend(args, device))
        elif n == "speed":
            out.append(SpeedBackend(args))
        elif n == "yolo_bike":
            if not args.yolo_weights:
                sys.exit("ERROR: yolo_bike needs --yolo-weights")
            out.append(YoloBikeBackend(args))
        elif n == "vlm":
            if not (args.vlm_url and args.vlm_model):
                sys.exit("ERROR: vlm needs --vlm-url and --vlm-model")
            out.append(VLMBackend(args))
        else:
            sys.exit(f"ERROR: unknown backend {n}")
    return out


# --------------------------------------------------------------------------
def parse_kv(items, what, valid=None, cast=str):
    d = {}
    for s in items or []:
        if "=" not in s:
            sys.exit(f"ERROR: {what} entry '{s}' must look like key=value")
        k, v = s.split("=", 1)
        try:
            v = cast(v)
        except ValueError:
            sys.exit(f"ERROR: bad value in {what} entry '{s}'")
        if valid is not None and v not in valid:
            sys.exit(f"ERROR: {what} value '{v}' must be one of {sorted(valid)}")
        d[k] = v
    return d


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--video", required=True)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--backends", nargs="+", choices=ALL_BACKENDS,
                    default=DEFAULT_BACKENDS)
    ap.add_argument("--track-ids", type=int, nargs="+", default=None)
    ap.add_argument("--truth", nargs="*", default=[],
                    help="tracker_id=bicyclist|pedestrian, e.g. 1=pedestrian 2=bicyclist")
    ap.add_argument("--thr", nargs="*", default=[],
                    help="per-backend threshold on p_bike, e.g. videomae=0.2")
    ap.add_argument("--window", type=int, default=30)
    ap.add_argument("--min-frames", type=int, default=8)
    ap.add_argument("--stride", type=int, default=5)
    ap.add_argument("--pad", type=float, default=0.6)
    ap.add_argument("--ema", type=float, default=0.5,
                    help="weight of new score in smoothed p_bike (1.0 = none)")
    ap.add_argument("--max-frames", type=int, default=0)
    ap.add_argument("--prompt-bike", default="a person riding a bicycle")
    ap.add_argument("--prompt-walk", default="a person walking")
    ap.add_argument("--xclip-model", default="microsoft/xclip-base-patch32")
    ap.add_argument("--clip-model", default="openai/clip-vit-base-patch32")
    ap.add_argument("--siglip-model", default="google/siglip-base-patch16-224")
    ap.add_argument("--videomae-model",
                    default="MCG-NJU/videomae-base-finetuned-kinetics")
    ap.add_argument("--img-frames", type=int, default=5,
                    help="crops per track scored by clip/siglip (default 5)")
    ap.add_argument("--speed-thr", type=float, default=0.06,
                    help="box-heights/frame separating walk from ride (guess, tune)")
    ap.add_argument("--yolo-weights", default=None)
    ap.add_argument("--yolo-conf", type=float, default=0.15)
    ap.add_argument("--vlm-url", default=None, help="e.g. http://localhost:8000/v1")
    ap.add_argument("--vlm-model", default=None)
    ap.add_argument("--vlm-frames", type=int, default=3)
    args = ap.parse_args()

    if not (0 < args.ema <= 1):
        sys.exit("ERROR: --ema must be in (0, 1]")
    if args.min_frames < 2 or args.min_frames > args.window:
        sys.exit("ERROR: need 2 <= --min-frames <= --window")

    truth = {int(k): v.lower() for k, v in
             parse_kv(args.truth, "--truth",
                      valid={"bicyclist", "pedestrian"},
                      cast=lambda s: s.lower()).items()}
    thr_over = parse_kv(args.thr, "--thr", cast=float)

    track_ids = set(args.track_ids) if args.track_ids else None
    by_frame, seen = load_rows(args.csv, track_ids)
    if not seen:
        sys.exit("ERROR: no matching tracks in CSV")
    bad_truth = sorted(set(truth) - seen)
    if bad_truth:
        sys.exit(f"ERROR: --truth ids not in CSV (or filtered out): {bad_truth}")
    print(f"Tracks: {sorted(seen)}")

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        sys.exit(f"ERROR: cannot open video {args.video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    scale = max(0.6, H / 1080.0 * 0.9)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"device: {device}")
    backends = build_backends(args.backends, args, device)
    for name in thr_over:
        if name not in [b.name for b in backends]:
            sys.exit(f"ERROR: --thr names backend '{name}' which is not running")
    thr = {b.name: thr_over.get(b.name, b.thr) for b in backends}
    print("thresholds on p_bike: " + ", ".join(f"{k}={v}" for k, v in thr.items()))

    os.makedirs(args.outdir, exist_ok=True)
    writers = {}
    for b in backends:
        path = os.path.join(args.outdir, f"{b.name}.mp4")
        wr = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H))
        if not wr.isOpened():
            sys.exit(f"ERROR: cannot open VideoWriter for {path}")
        writers[b.name] = wr

    buffers = defaultdict(lambda: deque(maxlen=args.window))
    hist = defaultdict(lambda: deque(maxlen=args.window))
    last_scored = {}
    smooth = {}                       # (backend, tid) -> smoothed p_bike
    logs = defaultdict(list)          # backend -> rows
    infer_time = defaultdict(float)
    infer_n = defaultdict(int)
    unknown = defaultdict(int)
    correct = defaultdict(int)        # (backend, tid)
    labeled = defaultdict(int)        # (backend, tid)
    skipped_empty = 0

    fi = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        fi += 1  # 1-based, matches the diagnostic CSV
        if args.max_frames and fi > args.max_frames:
            break

        present = by_frame.get(fi, [])
        pres = {tid: (cx, cy, w, h) for tid, cx, cy, w, h in present}

        for tid, cx, cy, w, h in present:
            hist[tid].append((fi, cx, cy, w, h))
            crop = crop_square(frame, cx, cy, w, h, args.pad)
            if crop is None:
                skipped_empty += 1
                continue
            buffers[tid].append(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))

        due = [tid for tid in pres
               if len(buffers[tid]) >= args.min_frames
               and (tid not in last_scored or fi - last_scored[tid] >= args.stride)]

        if due:
            items = [SimpleNamespace(tid=tid, frame_idx=fi, frame=frame,
                                     box=pres[tid], crops=list(buffers[tid]),
                                     hist=list(hist[tid])) for tid in due]
            for b in backends:
                t0 = time.perf_counter()
                ps = b.predict(items)
                if device == "cuda":
                    torch.cuda.synchronize()
                infer_time[b.name] += time.perf_counter() - t0
                infer_n[b.name] += len(items)
                if len(ps) != len(items):
                    sys.exit(f"ERROR [{b.name}]: returned {len(ps)} scores "
                             f"for {len(items)} items")
                for it, p in zip(items, ps):
                    if p is None:
                        unknown[b.name] += 1
                        continue
                    key = (b.name, it.tid)
                    smooth[key] = p if key not in smooth else \
                        args.ema * p + (1 - args.ema) * smooth[key]
                    logs[b.name].append([it.tid, fi, round(p, 3),
                                         round(smooth[key], 3)])
            for tid in due:
                last_scored[tid] = fi

        for b in backends:
            img = frame.copy()
            for tid, box in pres.items():
                key = (b.name, tid)
                if key in smooth:
                    p = smooth[key]
                    label = LABELS[0] if p >= thr[b.name] else LABELS[1]
                    draw_track(img, box, tid, label, p, scale)
                    if tid in truth:
                        labeled[key] += 1
                        correct[key] += int(label.lower() == truth[tid])
                else:
                    draw_track(img, box, tid, None, None, scale)
            draw_banner(img, b.name, scale)
            writers[b.name].write(img)

        if fi % 100 == 0:
            print(f"frame {fi}/{total if total > 0 else '?'}")

    cap.release()
    for wr in writers.values():
        wr.release()

    if fi == 0:
        sys.exit("ERROR: read 0 frames from video")
    if skipped_empty:
        print(f"WARNING: {skipped_empty} empty crops skipped (box outside frame)")

    # ---- write per-backend score logs
    failed = []
    for b in backends:
        if not logs[b.name]:
            failed.append(b.name)
            continue
        with open(os.path.join(args.outdir, f"{b.name}_scores.csv"), "w",
                  newline="") as f:
            wtr = csv.writer(f)
            wtr.writerow(["tracker_id", "frame", "p_bike", "p_bike_smooth"])
            wtr.writerows(logs[b.name])

    # ---- summary
    tids_t = sorted(truth)
    header = ["backend", "sec_per_call", "unanswered"] + \
             [f"acc_id{t}({truth[t][:4]})" for t in tids_t] + \
             (["macro_acc"] if tids_t else []) + ["mean_p_bike_by_track"]
    rows = []
    for b in backends:
        n = infer_n[b.name]
        row = [b.name, f"{infer_time[b.name] / n:.4f}" if n else "n/a",
               unknown[b.name]]
        accs = []
        for t in tids_t:
            k = (b.name, t)
            if labeled[k]:
                a = correct[k] / labeled[k]
                accs.append(a)
                row.append(f"{a:.2f}")
            else:
                row.append("n/a")
        if tids_t:
            row.append(f"{np.mean(accs):.2f}" if len(accs) == len(tids_t) else "n/a")
        means = []
        for t in sorted(seen):
            vals = [r[3] for r in logs[b.name] if r[0] == t]
            if vals:
                means.append(f"{t}:{np.mean(vals):.2f}")
        row.append(" ".join(means))
        rows.append(row)

    print("\n=== summary ===")
    print(" | ".join(header))
    for r in rows:
        print(" | ".join(str(x) for x in r))
    with open(os.path.join(args.outdir, "summary.csv"), "w", newline="") as f:
        wtr = csv.writer(f)
        wtr.writerow(header)
        wtr.writerows(rows)
    if not tids_t:
        print("(no --truth given: no accuracy computed; watch the videos)")
    print(f"\nVideos and CSVs in {args.outdir}")

    if failed:
        sys.exit(f"ERROR: backends never produced a score: {failed}")


if __name__ == "__main__":
    main()
