#!/bin/bash
#SBATCH --job-name=xclip_overlay_v2
#SBATCH --partition=hpg-turin
#SBATCH --account=xilei.zhao
#SBATCH --qos=xilei.zhao
#SBATCH --gpus=1
#SBATCH --mem=24gb
#SBATCH --time=01:30:00
#SBATCH --output=logs/xclip_overlay_v2_%j.log

# xclip_overlay_v2.py: YOLO people+vehicles, X-CLIP labels, yellow header w/ counts.
# X-CLIP must be cached on the login node first. yolo11x.pt is fetched from GitHub
# (works on compute nodes); or put the .pt in vision3 / pass a full path via DETECTOR.
# logs/ must exist before submitting.
#
# Override at submit time, e.g.:
#   sbatch --export=ALL,CSV=pilot_output/compare_v4/track_j_diagnostic.csv run_xclip_overlay_v2.slurm
#   sbatch --export=ALL,START_FRAME=4300,MAX_FRAMES=4600,MIN_FRAMES=4,STRIDE=3 run_xclip_overlay_v2.slurm

set -euo pipefail
cd /orange/xiangyan/rithika/vision/vision3
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate

export HF_HUB_OFFLINE=1

VIDEO="${VIDEO:-test.mp4}"
OUT="${OUT:-pilot_output/compare_v4/xclip_overlay_v2/overlay.mp4}"
DETECTOR="${DETECTOR:-yolo11x.pt}"
CSV="${CSV:-}"                  # empty = detect people with YOLO
START_FRAME="${START_FRAME:-1}"
MAX_FRAMES="${MAX_FRAMES:-0}"   # last frame (absolute), 0 = end
MIN_FRAMES="${MIN_FRAMES:-8}"
STRIDE="${STRIDE:-5}"

EXTRA=()
if [ -n "$CSV" ]; then
    EXTRA+=(--csv "$CSV")
fi

python xclip_overlay_v2.py \
    --video "$VIDEO" \
    --out "$OUT" \
    --detector "$DETECTOR" \
    --start-frame "$START_FRAME" \
    --max-frames "$MAX_FRAMES" \
    --min-frames "$MIN_FRAMES" \
    --stride "$STRIDE" \
    "${EXTRA[@]}"
