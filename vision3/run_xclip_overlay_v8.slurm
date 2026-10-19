#!/bin/bash
#SBATCH --job-name=xclip_overlay_v8
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --gpus=1
#SBATCH --mem=24gb
#SBATCH --time=01:30:00
#SBATCH --output=logs/xclip_overlay_v8_%j.log

# xclip_overlay_v8.py: fine-tuned RT-DETR + X-CLIP. logs/ must exist.
# Override e.g.: sbatch --export=ALL,START_FRAME=550,MAX_FRAMES=900 run_xclip_overlay_v8.slurm

set -euo pipefail
cd /orange/xiangyan/rithika/vision/vision3
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
export HF_HUB_OFFLINE=1

VIDEO="${VIDEO:-test.mp4}"
OUT="${OUT:-pilot_output/compare_v4/xclip_overlay_v8/overlay.mp4}"
WEIGHTS="${WEIGHTS:-/orange/xiangyan/rithika/vision/vision3/runs/detect/finetune_runs/rtdetr_v3/weights/best.pt}"
START_FRAME="${START_FRAME:-1}"
MAX_FRAMES="${MAX_FRAMES:-0}"
IMGSZ="${IMGSZ:-1280}"
DET_CONF="${DET_CONF:-0.25}"
VEH_WEIGHTS="${VEH_WEIGHTS:-}"
# per-camera zone file (see zones/). Override with ZONES_JSON=zones/other_camera.json
ZONES_JSON="${ZONES_JSON:-zones/camera_A.json}"
VEH_ARG=()
[ -n "$VEH_WEIGHTS" ] && VEH_ARG=(--veh-weights "$VEH_WEIGHTS")
[ -n "$ZONES_JSON" ] && VEH_ARG+=(--zones-json "$ZONES_JSON")

python xclip_overlay_v8.py \
    --video "$VIDEO" \
    --out "$OUT" \
    --weights "$WEIGHTS" \
    --start-frame "$START_FRAME" \
    --max-frames "$MAX_FRAMES" \
    --imgsz "$IMGSZ" \
    --det-conf "$DET_CONF" \
    ${VEH_ARG[@]+"${VEH_ARG[@]}"}
