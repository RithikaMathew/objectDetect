#!/bin/bash
#SBATCH --job-name=diag_track_j
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --gpus=1
#SBATCH --mem=16gb
#SBATCH --time=00:30:00
#SBATCH --output=logs/diag_track_j_%j.log

# One-off diagnostic job: does Method J's "7 (now 8) unique cyclists" come
# from real hallucination or from one genuine distant rider whose track
# keeps dying/respawning (same benign pattern already documented for
# methods H and old-F)? See diagnose_track_j_v1.py's own docstring.
#
# logs/ must already exist before this is submitted (mkdir -p logs) --
# matches run_finetune.slurm's convention.

set -euo pipefail
cd /orange/xiangyan/rithika/vision/vision3
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate

FINETUNE_WEIGHTS="${FINETUNE_WEIGHTS:-finetune_runs/rtdetr_v1/weights/best.pt}"
VIDEO="${VIDEO:-test.mp4}"
OUTDIR="${OUTDIR:-pilot_output/compare_v4}"

python diagnose_track_j_v1.py \
    --video "$VIDEO" \
    --finetune-weights "$FINETUNE_WEIGHTS" \
    --outdir "$OUTDIR"
