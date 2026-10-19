#!/bin/bash
#SBATCH --job-name=xclip_overlay
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --gpus=1
#SBATCH --mem=16gb
#SBATCH --time=01:00:00
#SBATCH --output=logs/xclip_overlay_%j.log

# Runs xclip_overlay_v1.py as a batch job so it survives closing the terminal.
# Model must be cached on the login node first (job runs offline).
# logs/ must exist before submitting (mkdir -p logs).
#
# Override at submit time, e.g.:
#   sbatch --export=ALL,TRACK_IDS="1 2 5" run_xclip_overlay_v1.slurm
#   sbatch --export=ALL,MAX_FRAMES=300 run_xclip_overlay_v1.slurm

set -euo pipefail
cd /orange/xiangyan/rithika/vision/vision3
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate

export HF_HUB_OFFLINE=1

VIDEO="${VIDEO:-test.mp4}"
CSV="${CSV:-pilot_output/compare_v4/track_j_diagnostic.csv}"
OUT="${OUT:-pilot_output/compare_v4/xclip_overlay_v1/overlay.mp4}"
TRACK_IDS="${TRACK_IDS:-}"      # empty = all tracks in the CSV
MAX_FRAMES="${MAX_FRAMES:-0}"   # 0 = whole video

EXTRA=()
if [ -n "$TRACK_IDS" ]; then
    EXTRA+=(--track-ids $TRACK_IDS)
fi

python xclip_overlay_v1.py \
    --video "$VIDEO" \
    --csv "$CSV" \
    --out "$OUT" \
    --max-frames "$MAX_FRAMES" \
    "${EXTRA[@]}"
