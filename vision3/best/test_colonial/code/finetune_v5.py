#!/usr/bin/env python3
"""Fine-tune the detector on YOUR OWN hard Colonial frames (night, far / walking away, motorcycles, shadow / grass).
Three steps. Run from test_colonial (NOT from code/), env activated (ultralytics installed).

 1) pick   - cut frames from hour files, NEVER from the four scored clips, and pre-label them with the current detector
             so you only CORRECT boxes instead of drawing them (upload images + labels to Roboflow/CVAT, fix, export YOLO).
 2) build  - merge base training data + your corrected frames into one dataset (validation split by 10-minute segment,
             so near-identical neighbouring frames never sit in both train and validation).
 3) train  - fine-tune from the current detector (same recipe as the earlier run: AdamW, lr0 1e-4, imgsz 640, batch 8, seed 42).

  python code/finetune_v5.py pick  --files 22,23,24,2,3 --per-file 40 --weights /orange/xiangyan/rithika/vision/vision3/runs/detect/finetune_runs/rtdetr_v3/best.pt --out hardframes/batch1
  #   --files = hour-file numbers NNN of Standard_SCU8OG_2019-07-10_0000.NNN.mp4 (NNN-1 = hour). Night hours = files 22-24, 1-6.
  #   --times 22:3500,22:3560 = extra specific moments (file:second) you saw errors at.
  # ... correct labels, export YOLO format to hardframes/batch1_fixed/{images,labels} (same file names) ...
  python code/finetune_v5.py build --base dataset_frames/roboflow_split_v1 --new hardframes/batch1_fixed --out dataset_frames/merged_colonial_v5
  sbatch code/finetune_v5.slurm        # trains rtdetr_v5_colonial (about 1 h on one GPU)
  # then score it like every other change: change ONLY the weights in a copy of run_batch4.sh (see README section 39) and run
  #   python code/eval_truth.py --root . --runs exp0_base,b4_combo_static5,<new run> --baseline exp0_base
  # Accept only if it beats 19/21 on the four clips with no new false tracks AND on the new clips from `pick_new_windows.py`.
Class names/ids come from the base dataset's data.yaml (model class names are matched by NAME, unknown names are dropped).
Motorcycle: if you want a separate class, add it to data.yaml names yourself; the scored truth counts motorcycles as cyclists.
"""
import argparse, glob, hashlib, os, random, re, shutil, sys
import yaml

VIDEO_DIR = ("/orange/xiangyan/rithika/vision/pilot_clips/MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/"
             "Standard_SCU8OG_2019-07-10_0000")
FPS = 29.97
# the four scored clips (README section 38): file -> list of (start_frame, end_frame or None); padded by 30 s below
SCORED = {22: [(26978, 53946)], 15: [(1, 26973)], 23: [(1, 26973)], 13: [(80924, None)]}
PAD_S = 30.0

def video_path(n): return os.path.join(VIDEO_DIR, f"Standard_SCU8OG_2019-07-10_0000.{n:03d}.mp4")

def excluded(n, sec):
    for a, b in SCORED.get(n, []):
        lo = a / FPS - PAD_S; hi = (b / FPS + PAD_S) if b else 1e12
        if lo <= sec <= hi: return True
    return False

def cmd_pick(a):
    import cv2
    model = None
    if a.weights:
        from ultralytics import RTDETR
        model = RTDETR(a.weights)
    os.makedirs(os.path.join(a.out, "images"), exist_ok=True); os.makedirs(os.path.join(a.out, "labels"), exist_ok=True)
    names_map = None
    if model is not None and a.base:
        base_names = yaml.safe_load(open(os.path.join(a.base, "data.yaml")))["names"]
        base_names = dict(enumerate(base_names)) if isinstance(base_names, list) else base_names
        names_map = {v: k for k, v in base_names.items()}
    rnd = random.Random(a.seed); jobs = []
    for n in [int(x) for x in a.files.split(",") if x]:
        cap = cv2.VideoCapture(a.video if a.video else video_path(n))
        if not cap.isOpened(): print(f"file {n}: cannot open"); continue
        dur = cap.get(cv2.CAP_PROP_FRAME_COUNT) / (cap.get(cv2.CAP_PROP_FPS) or FPS); cap.release()
        secs, tries = [], 0
        while len(secs) < a.per_file and tries < 5000:
            tries += 1; s = rnd.uniform(5, dur - 5)
            if excluded(n, s) or any(abs(s - t) < a.min_gap for t in secs): continue
            secs.append(s)
        jobs += [(n, s) for s in sorted(secs)]
    for t in [x for x in (a.times or "").split(",") if x]:
        n, s = t.split(":"); n, s = int(n), float(s)
        if excluded(n, s): print(f"{t}: inside a scored clip, skipped"); continue
        jobs.append((n, s))
    kept = 0
    for n, s in jobs:
        cap = cv2.VideoCapture(a.video if a.video else video_path(n)); cap.set(cv2.CAP_PROP_POS_MSEC, s * 1000)
        ok, fr = cap.read(); cap.release()
        if not ok: continue
        stem = f"f{n:03d}_{int(s):05d}"; cv2.imwrite(os.path.join(a.out, "images", stem + ".jpg"), fr)
        lines = []
        if model is not None:
            res = model.predict(fr, conf=a.conf, verbose=False)[0]; h, w = fr.shape[:2]
            for b in res.boxes:
                nm = res.names[int(b.cls)]
                cid = names_map.get(nm) if names_map else int(b.cls)
                if cid is None: continue
                x1, y1, x2, y2 = [float(v) for v in b.xyxy[0]]
                lines.append(f"{cid} {(x1 + x2) / 2 / w:.6f} {(y1 + y2) / 2 / h:.6f} {(x2 - x1) / w:.6f} {(y2 - y1) / h:.6f}")
        open(os.path.join(a.out, "labels", stem + ".txt"), "w").write("\n".join(lines) + ("\n" if lines else ""))
        kept += 1
    print(f"wrote {kept} frames to {a.out}/images (+ pseudo-labels in labels/). Correct them, then run `build`.")

def _find(base, split):
    for img, lab in ((f"{split}/images", f"{split}/labels"), (f"images/{split}", f"labels/{split}")):
        if os.path.isdir(os.path.join(base, img)): return os.path.join(base, img), os.path.join(base, lab)
    return None, None

def _link(src, dst):
    if os.path.exists(dst): return
    try: os.symlink(os.path.abspath(src), dst)
    except OSError: shutil.copy(src, dst)

def _add(img_dir, lab_dir, out, split, repeat, prefix):
    n = 0
    for p in sorted(glob.glob(os.path.join(img_dir, "*"))):
        if not p.lower().endswith((".jpg", ".jpeg", ".png")): continue
        stem = os.path.splitext(os.path.basename(p))[0]; lab = os.path.join(lab_dir, stem + ".txt")
        for r in range(repeat):
            tag = f"{prefix}{stem}" + (f"_r{r}" if repeat > 1 else "")
            _link(p, os.path.join(out, split, "images", tag + os.path.splitext(p)[1]))
            if os.path.exists(lab): _link(lab, os.path.join(out, split, "labels", tag + ".txt"))
            else: open(os.path.join(out, split, "labels", tag + ".txt"), "w").close()
        n += 1
    return n

def cmd_build(a):
    for sp in ("train", "val"):
        for k in ("images", "labels"): os.makedirs(os.path.join(a.out, sp, k), exist_ok=True)
    cfg = yaml.safe_load(open(os.path.join(a.base, "data.yaml")))
    bi, bl = _find(a.base, "train"); vi, vl = _find(a.base, "valid") if _find(a.base, "valid")[0] else _find(a.base, "val")
    if not bi: sys.exit(f"cannot find train images under {a.base} (expected train/images or images/train)")
    nb = _add(bi, bl, a.out, "train", a.base_repeat, "base_")
    if vi: _add(vi, vl, a.out, "val", 1, "base_")
    ni, nl = os.path.join(a.new, "images"), os.path.join(a.new, "labels")
    ntr = nva = 0
    for p in sorted(glob.glob(os.path.join(ni, "*"))):
        stem = os.path.splitext(os.path.basename(p))[0]
        m = re.match(r"f(\d+)_(\d+)", stem)
        seg = f"{m.group(1)}_{int(m.group(2)) // 600}" if m else stem
        is_val = int(hashlib.md5(seg.encode()).hexdigest(), 16) % 100 < a.val_pct   # by 10-minute segment
        if is_val: nva += _add_one(p, nl, a.out, "val", 1)
        else: ntr += _add_one(p, nl, a.out, "train", a.new_repeat)
    names = cfg["names"]
    yaml.safe_dump({"path": os.path.abspath(a.out), "train": "train/images", "val": "val/images", "names": names},
                   open(os.path.join(a.out, "data.yaml"), "w"))
    print(f"base train images {nb} (x{a.base_repeat}); new frames: {ntr} train (x{a.new_repeat}), {nva} val; data.yaml written")
    if nva == 0: print("WARNING: no new frame landed in validation; add more frames or raise --val-pct")
    if ntr == 0: print("WARNING: no new frame landed in train; frames from only one 10-minute segment all go to one side. Pick frames from several files.")

def _add_one(p, lab_dir, out, split, repeat):
    stem = os.path.splitext(os.path.basename(p))[0]; lab = os.path.join(lab_dir, stem + ".txt")
    for r in range(repeat):
        tag = f"new_{stem}" + (f"_r{r}" if repeat > 1 else "")
        _link(p, os.path.join(out, split, "images", tag + os.path.splitext(p)[1]))
        dst = os.path.join(out, split, "labels", tag + ".txt")
        if os.path.exists(lab): _link(lab, dst)
        else: open(dst, "w").close()
    return 1

def cmd_train(a):
    from ultralytics import RTDETR
    m = RTDETR(a.weights)
    m.train(data=os.path.join(a.data, "data.yaml"), epochs=a.epochs, patience=a.patience, imgsz=640, batch=8,
            optimizer="AdamW", lr0=1e-4, seed=42, project="/orange/xiangyan/rithika/vision/vision3/runs/detect/finetune_runs", name=a.name, exist_ok=False)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pick"); p.add_argument("--files", default=""); p.add_argument("--times"); p.add_argument("--per-file", type=int, default=40)
    p.add_argument("--min-gap", type=float, default=20.0); p.add_argument("--weights"); p.add_argument("--base", default="dataset_frames/roboflow_split_v1")
    p.add_argument("--conf", type=float, default=0.15); p.add_argument("--out", required=True); p.add_argument("--seed", type=int, default=7)
    p.add_argument("--video", help="use this one video instead of the Colonial hour files (testing)")
    p = sub.add_parser("build"); p.add_argument("--base", required=True); p.add_argument("--new", required=True); p.add_argument("--out", required=True)
    p.add_argument("--base-repeat", type=int, default=3); p.add_argument("--new-repeat", type=int, default=3); p.add_argument("--val-pct", type=int, default=20)
    p = sub.add_parser("train"); p.add_argument("--data", default="dataset_frames/merged_colonial_v5")
    p.add_argument("--weights", default="/orange/xiangyan/rithika/vision/vision3/runs/detect/finetune_runs/rtdetr_v3/best.pt"); p.add_argument("--name", default="rtdetr_v5_colonial")
    p.add_argument("--epochs", type=int, default=50); p.add_argument("--patience", type=int, default=15)
    a = ap.parse_args(); {"pick": cmd_pick, "build": cmd_build, "train": cmd_train}[a.cmd](a)

if __name__ == "__main__": main()
