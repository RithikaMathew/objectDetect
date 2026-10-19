#!/usr/bin/env python3
"""
finetune_rtdetr.py

Fine-tunes RT-DETR-l (Method C -- your current best baseline, confirmed
clean after the ByteTrack fix in compare_detectors_v7_fixed.py) on your
own 270-image annotated set, split via split_dataset.py.

Why RT-DETR-l and not YOLO26x or RF-DETR-Large: C is the only method with
an actually-confirmed-good result on your footage right now. F (YOLO26x)
and I (RF-DETR) haven't been re-run since the tracker fix, so there's
nothing yet to justify fine-tuning a base model you don't have a clean
baseline for. If F or I turn out to beat C after re-running the array job,
this script's --base-weights flag lets you point it at a different .pt
checkpoint without any other changes -- ping me and I'll also check
whether RF-DETR needs different train() kwargs (its API differs somewhat
from ultralytics YOLO/RTDETR).

This is a thin wrapper around ultralytics' RTDETR.train(). It exists
mainly to keep the invocation, output paths, and defaults documented and
reproducible in one place rather than a bare CLI call buried in the
SLURM script.

USAGE
    python finetune_rtdetr.py \
        --data /orange/xiangyan/rithika/vision/dataset_frames/roboflow_split_v1/data.yaml \
        --base-weights /orange/xiangyan/rithika/vision/vision3/weights/rtdetr-l.pt \
        --outdir /orange/xiangyan/rithika/vision/vision3/finetune_runs/rtdetr_v1 \
        --epochs 100
"""
import argparse
import json
import os
from pathlib import Path

import torch
from ultralytics import RTDETR


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", required=True, help="Path to data.yaml from split_dataset.py")
    ap.add_argument("--base-weights", required=True,
                     help="Pretrained checkpoint to fine-tune from (e.g. weights/rtdetr-l.pt)")
    ap.add_argument("--outdir", required=True,
                     help="Directory for training run output (weights, curves, val results)")
    ap.add_argument("--epochs", type=int, default=100,
                     help="With only ~216 training images, more epochs with early "
                          "stopping (see --patience) is safer than guessing a low "
                          "number and underfitting")
    ap.add_argument("--patience", type=int, default=20,
                     help="Early-stop if val loss doesn't improve for this many epochs")
    ap.add_argument("--imgsz", type=int, default=640,
                     help="Kept at 640 to match C's inference settings -- the README's "
                          "bug #1 shows this codebase already learned the hard way that "
                          "changing IMG_SIZE has non-obvious effects; don't raise this "
                          "without re-testing inference at the same size")
    ap.add_argument("--batch", type=int, default=8,
                     help="Small default for a small dataset + single-GPU job; raise if "
                          "you confirm GPU memory headroom")
    ap.add_argument("--lr0", type=float, default=None,
                     help="Initial LR override. Left at ultralytics' default (None) unless "
                          "you have a reason to change it -- fine-tuning from a strong "
                          "COCO checkpoint on 270 images usually wants a LOWER lr0 than "
                          "training from scratch, and ultralytics' RTDETR default is "
                          "already tuned for fine-tuning, not from-scratch training")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    device = "0" if torch.cuda.is_available() else "cpu"
    print(f"[finetune_rtdetr] device={device}", flush=True)
    if device == "cpu":
        print("WARNING: no GPU visible -- check --gres/--gpus in the SLURM script. "
              "Fine-tuning RT-DETR on CPU will be extremely slow.", flush=True)

    if not Path(args.data).exists():
        raise SystemExit(f"ERROR: --data file not found: {args.data} "
                          f"(run split_dataset.py first)")
    if not Path(args.base_weights).exists():
        raise SystemExit(f"ERROR: --base-weights not found: {args.base_weights}")

    os.makedirs(args.outdir, exist_ok=True)
    outdir = Path(args.outdir)

    model = RTDETR(args.base_weights)

    train_kwargs = dict(
        data=args.data,
        epochs=args.epochs,
        patience=args.patience,
        imgsz=args.imgsz,
        batch=args.batch,
        device=device,
        seed=args.seed,
        project=str(outdir.parent),
        name=outdir.name,
        exist_ok=True,
        val=True,
        plots=True,
    )
    if args.lr0 is not None:
        train_kwargs["lr0"] = args.lr0

    print(f"[finetune_rtdetr] starting train() with: {json.dumps(train_kwargs, indent=2)}",
          flush=True)
    results = model.train(**train_kwargs)

    # Explicit val() pass on the held-out test split, since train()'s
    # built-in val only ever sees the val split, never test.
    print("[finetune_rtdetr] running final eval on the TEST split...", flush=True)
    best_weights = outdir / "weights" / "best.pt"
    if not best_weights.exists():
        print(f"[finetune_rtdetr] WARNING: expected best.pt at {best_weights} not found -- "
              f"skipping test-split eval. Check {outdir}/weights/ manually.", flush=True)
        return

    test_model = RTDETR(str(best_weights))
    test_metrics = test_model.val(data=args.data, split="test", imgsz=args.imgsz,
                                   device=device, project=str(outdir.parent),
                                   name=f"{outdir.name}_test_eval", exist_ok=True)

    summary = {
        "base_weights": args.base_weights,
        "data_yaml": args.data,
        "epochs_requested": args.epochs,
        "outdir": str(outdir),
        "best_weights": str(best_weights),
        "test_map50": float(test_metrics.box.map50) if hasattr(test_metrics, "box") else None,
        "test_map50_95": float(test_metrics.box.map) if hasattr(test_metrics, "box") else None,
    }
    summary_path = outdir / "finetune_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[finetune_rtdetr] done. Summary written to {summary_path}:", flush=True)
    print(json.dumps(summary, indent=2), flush=True)
    print(f"[finetune_rtdetr] next step: plug {best_weights} into "
          f"compare_detectors_v7_fixed.py as a new method (or swap it in for "
          f"weights/rtdetr-l.pt under Method C) and re-run against the same "
          f"test video to compare against the pretrained baseline directly.",
          flush=True)


if __name__ == "__main__":
    main()
