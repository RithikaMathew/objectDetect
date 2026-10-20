#!/usr/bin/env python3
"""
eval_per_class.py

finetune_rtdetr.py only saved the AGGREGATE test_map50 / test_map50_95 --
averaged across all 6 classes (bus, car, cyclist, other_vehicle, person,
truck). That number is not informative on its own: it's dominated by
however common/easy the other 5 classes are, and says nothing about
whether the class you actually care about -- cyclist -- improved.

This re-runs val() on the already-trained best.pt (cheap: ~27 test images,
no training) and prints/saves the per-class breakdown so you can read off
cyclist's AP50 / AP50-95 specifically.

USAGE
    python eval_per_class.py \
        --weights /orange/xiangyan/rithika/vision/vision3/finetune_runs/rtdetr_v1/weights/best.pt \
        --data /orange/xiangyan/rithika/vision/dataset_frames/roboflow_split_v1/data.yaml
"""
import argparse
import json

import torch
from ultralytics import RTDETR


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--weights", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--imgsz", type=int, default=640)
    ap.add_argument("--split", default="test", choices=["val", "test"])
    args = ap.parse_args()

    device = "0" if torch.cuda.is_available() else "cpu"
    model = RTDETR(args.weights)
    metrics = model.val(data=args.data, split=args.split, imgsz=args.imgsz,
                         device=device, verbose=True)

    names = metrics.names  # {class_id: name}
    ap_class_idx = metrics.box.ap_class_index  # which classes actually appeared
    ap50 = metrics.box.ap50
    ap5095 = metrics.box.ap

    print(f"\n=== per-class results on {args.split} split ===")
    per_class = {}
    for i, cid in enumerate(ap_class_idx):
        name = names[int(cid)]
        per_class[name] = {"ap50": float(ap50[i]), "ap50_95": float(ap5095[i])}
        flag = "  <-- the one that matters" if name == "cyclist" else ""
        print(f"  {name:16s} AP50={ap50[i]:.3f}  AP50-95={ap5095[i]:.3f}{flag}")

    if "cyclist" not in per_class:
        print("\nWARNING: 'cyclist' didn't appear in the metrics at all -- this "
              "usually means there were zero cyclist instances in the test "
              "split's ground truth. With only 270 images total and a "
              "held-out test split of ~27, it's plausible the split ended up "
              "with no (or very few) cyclist examples in test/val by chance. "
              "Check: grep -l ' 2 ' <split>/labels/*.txt (class id 2 = "
              "cyclist per data.yaml) to count how many test/val labels "
              "actually contain a cyclist box.")

    out_path = args.weights.rsplit("/weights/", 1)[0] + f"/per_class_{args.split}_metrics.json"
    with open(out_path, "w") as f:
        json.dump(per_class, f, indent=2)
    print(f"\nSaved -> {out_path}")


if __name__ == "__main__":
    main()
