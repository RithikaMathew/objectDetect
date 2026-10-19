#!/usr/bin/env python3
"""train_rtdetr_night_v1.py: continue fine-tuning rtdetr_v3 on the merged dataset (new run name, nothing overwritten).
Same image size / batch / seed as rtdetr_v3 (args.yaml); lower learning rate so the daytime skill is kept."""
import argparse
from pathlib import Path
from ultralytics import RTDETR

ap = argparse.ArgumentParser()
ap.add_argument("--data", required=True, help="data.yaml from build_merged_dataset_v1.py")
ap.add_argument("--weights", default="/orange/xiangyan/rithika/vision/vision3/runs/detect/finetune_runs/rtdetr_v3/weights/best.pt")
ap.add_argument("--name", default="rtdetr_v4_night")
ap.add_argument("--epochs", type=int, default=50)
ap.add_argument("--lr0", type=float, default=1e-4)
a = ap.parse_args()

project = "/orange/xiangyan/rithika/vision/vision3/runs/detect/finetune_runs"
if (Path(project) / a.name).exists():
    raise SystemExit(f"ERROR: {project}/{a.name} exists; pick another --name (no overwrite)")
if not Path(a.weights).is_file():
    raise SystemExit(f"ERROR: weights not found: {a.weights}")

model = RTDETR(a.weights)
model.train(data=a.data, epochs=a.epochs, patience=15, batch=8, imgsz=640, device="0", workers=8, seed=42, deterministic=True,
            optimizer="AdamW", lr0=a.lr0, lrf=0.1, warmup_epochs=1.0, close_mosaic=10, amp=True, hsv_v=0.6,
            project=project, name=a.name, exist_ok=False, plots=True)
print("best weights:", f"{project}/{a.name}/weights/best.pt")
