#!/bin/bash
#SBATCH --job-name=cyclist_compare_v5
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --gpus=1
#SBATCH --mem=24gb
#SBATCH --time=01:00:00
#SBATCH --output=logs/cyclist_compare_v5_%A_%a.log
#SBATCH --array=0-9

# Same as run_compare_array_v4.slurm, except:
#   - calls compare_detectors_v8_smaller_labels.py (smaller on-screen text,
#     v7_fixed's yellow counter was getting cut off at frame edge)
#   - FINETUNE_WEIGHTS default points at the CURRENT best checkpoint
#     (runs/detect/finetune_runs/rtdetr_v3/weights/best.pt), not the old
#     rtdetr_v1 path (which no longer exists -- that folder was renamed
#     to rtdetr_v2_overtriggers after retrain #2 turned out broken)
# Methods A-J still map to array indices 0-9, same as before.

set -euo pipefail
cd /orange/xiangyan/rithika/vision/vision3
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate

METHODS=(A B C D E F G H I J)
METHOD="${METHODS[$SLURM_ARRAY_TASK_ID]}"

WEIGHTS_DIR="${WEIGHTS_DIR:-/orange/xiangyan/rithika/vision/vision3/weights}"
FINETUNE_WEIGHTS="${FINETUNE_WEIGHTS:-/orange/xiangyan/rithika/vision/vision3/runs/detect/finetune_runs/rtdetr_v3/weights/best.pt}"
VIDEO="${VIDEO:-test.mp4}"
OUTDIR="${OUTDIR:-pilot_output/compare_v4}"

if [ "$METHOD" = "J" ] && [ ! -f "$FINETUNE_WEIGHTS" ]; then
    echo "ERROR: $FINETUNE_WEIGHTS missing. Run run_finetune.slurm first, or set"
    echo "FINETUNE_WEIGHTS to point at a different best.pt."
    exit 1
fi

python comparison/compare_detectors_v8_smaller_labels.py \
    --method "$METHOD" \
    --video "$VIDEO" \
    --weights-dir "$WEIGHTS_DIR" \
    --finetune-weights "$FINETUNE_WEIGHTS" \
    --outdir "$OUTDIR"
