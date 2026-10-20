#!/bin/bash
#SBATCH --job-name=cyclist_finetune_v1
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --gpus=1
#SBATCH --mem=24gb
#SBATCH --time=04:00:00
#SBATCH --output=logs/cyclist_finetune_v1_%j.log

# Standard fine-tune of RT-DETR-l (Method C's base checkpoint) on your own
# 270-image Roboflow annotation set. Splits the flat export into
# train/val/test, then fine-tunes and evaluates on the held-out test split.
#
# This is the STANDARD variant only -- no IPM warping. A separate
# run_finetune_ipm.slurm + finetune_rtdetr_ipm.py will do the IPM-augmented
# A/B variant, kept in separate files on purpose so this baseline run isn't
# entangled with that experiment.
#
# logs/ must already exist before this is submitted (mkdir -p logs).
#
# Time budget: 4 hours is a guess for ~216 training images at batch=8 on
# one GPU -- if RTDETR.train() finishes well under that, lower it on the
# next submission so you're not holding a GPU node longer than needed;
# if it's not enough (unlikely at this dataset size), raise it and resubmit
# with --resume in finetune_rtdetr.py args (not currently wired up -- ask
# if you hit this and I'll add a --resume flag).
#
# Override any of these at submit time, e.g.:
#   sbatch --export=EPOCHS=150 run_finetune.slurm

set -euo pipefail
cd /orange/xiangyan/rithika/vision/vision3
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
module load ffmpeg 2>/dev/null || true

RAW_DATA="${RAW_DATA:-/orange/xiangyan/rithika/vision/dataset_frames/roboflow_raw_v1}"
SPLIT_DATA="${SPLIT_DATA:-/orange/xiangyan/rithika/vision/dataset_frames/roboflow_split_v1}"
WEIGHTS_DIR="${WEIGHTS_DIR:-/orange/xiangyan/rithika/vision/vision3/weights}"
OUTDIR="${OUTDIR:-/orange/xiangyan/rithika/vision/vision3/finetune_runs/rtdetr_v1}"
EPOCHS="${EPOCHS:-100}"

if [ ! -f "$WEIGHTS_DIR/rtdetr-l.pt" ]; then
    echo "ERROR: $WEIGHTS_DIR/rtdetr-l.pt missing. Run prefetch_weights.py on the login node first."
    exit 1
fi

echo "=== split ==="
echo "raw data:   $RAW_DATA"
echo "split data: $SPLIT_DATA"

# Only re-split if the split doesn't already exist, so re-submitting this
# job after a crash (e.g. to bump --time) doesn't reshuffle the split and
# quietly change what's in train vs. val vs. test between runs.
if [ -f "$SPLIT_DATA/data.yaml" ]; then
    echo "split already exists at $SPLIT_DATA/data.yaml -- reusing it as-is."
    echo "(delete $SPLIT_DATA and resubmit if you actually want to re-split, "
    echo "e.g. after adding more annotated images.)"
else
    python training/split_dataset.py \
        --src "$RAW_DATA" \
        --out "$SPLIT_DATA" \
        --ratios 0.8 0.1 0.1 \
        --seed 42
fi

echo "=== fine-tune ==="
echo "base weights: $WEIGHTS_DIR/rtdetr-l.pt"
echo "outdir:       $OUTDIR"
echo "epochs:       $EPOCHS"

python training/finetune_rtdetr.py \
    --data "$SPLIT_DATA/data.yaml" \
    --base-weights "$WEIGHTS_DIR/rtdetr-l.pt" \
    --outdir "$OUTDIR" \
    --epochs "$EPOCHS"
