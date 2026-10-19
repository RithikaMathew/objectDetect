#!/bin/bash
#SBATCH --job-name=cyclist_compare_v4
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --gpus=1
#SBATCH --mem=24gb
#SBATCH --time=01:00:00
#SBATCH --array=0-9
#SBATCH --output=logs/cyclist_compare_v4_%A_%a.log

# Runs methods A-J in parallel, one per array task, each on its own GPU node.
# Uses compare_detectors_v7_fixed.py (the ByteTrack minimum_matching_threshold
# fix -- see that file's module docstring -- plus Method H and Method I:
# RF-DETR-Large). NOTE: this script is still named run_compare_array_v4.slurm
# (the array/job-name numbering), but the Python file it calls is v7_fixed,
# not v4 -- v4.py was an earlier, buggy ancestor. Don't let the .slurm
# filename's "v4" mislead you into thinking it runs v4.py.
#
# mem bumped 16gb -> 24gb vs. v2's array script: RF-DETR-Large's DINOv2
# backbone has a bigger memory footprint than the YOLO/RT-DETR checkpoints
# the old limit was sized for.
#
# logs/ must already exist before this is submitted (SLURM opens --output
# before the job script's first line runs): mkdir -p logs first.
#
# Before submitting, make sure yolo26x.pt is in weights/ AND rfdetr's
# weights are cached -- run these on the LOGIN NODE first (not via sbatch):
#   python prefetch_weights_v2.py
#   pip install rfdetr && python prefetch_rfdetr.py
#
# Override any of these at submit time, e.g.:
#   sbatch --export=VIDEO_PATH=/orange/.../myclip.mp4 run_compare_array_v4.slurm

set -euo pipefail
cd /orange/xiangyan/rithika/vision/vision3
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
module load ffmpeg 2>/dev/null || true

METHODS=(A B C D E F G H I J)
METHOD="${METHODS[$SLURM_ARRAY_TASK_ID]}"

WEIGHTS_DIR="${WEIGHTS_DIR:-/orange/xiangyan/rithika/vision/vision3/weights}"
OUTDIR="${OUTDIR:-/orange/xiangyan/rithika/vision/vision3/pilot_output/compare_v4}"
VIDEO="${VIDEO_PATH:-$(find . -maxdepth 1 -name '*.mp4' | sort | head -1)}"
FINETUNE_WEIGHTS="${FINETUNE_WEIGHTS:-/orange/xiangyan/rithika/vision/vision3/finetune_runs/rtdetr_v1/weights/best.pt}"

if [ -z "$VIDEO" ]; then
    echo "ERROR: no .mp4 found in $(pwd) and VIDEO_PATH not set"
    exit 1
fi

for f in yolov8x.pt yolo11x.pt rtdetr-l.pt visdrone_yolo11x.pt yolo26x.pt; do
    if [ ! -f "$WEIGHTS_DIR/$f" ]; then
        echo "ERROR: $WEIGHTS_DIR/$f missing. Run prefetch_weights.py and"
        echo "prefetch_weights_v2.py on the login node before submitting this."
        exit 1
    fi
done

if [ "$METHOD" = "I" ]; then
    python -c "import rfdetr" 2>/dev/null || {
        echo "ERROR: rfdetr not installed in this venv. On the login node:"
        echo "  pip install rfdetr && python prefetch_rfdetr.py"
        exit 1
    }
fi

if [ "$METHOD" = "J" ] && [ ! -f "$FINETUNE_WEIGHTS" ]; then
    echo "ERROR: $FINETUNE_WEIGHTS missing. Run run_finetune.slurm first, or set"
    echo "FINETUNE_WEIGHTS to point at a different best.pt."
    exit 1
fi

echo "=== method $METHOD ==="
echo "video:   $VIDEO"
echo "weights: $WEIGHTS_DIR"
echo "outdir:  $OUTDIR"

python compare_detectors_v7_fixed.py \
    --method "$METHOD" \
    --video "$VIDEO" \
    --weights-dir "$WEIGHTS_DIR" \
    --finetune-weights "$FINETUNE_WEIGHTS" \
    --outdir "$OUTDIR"
