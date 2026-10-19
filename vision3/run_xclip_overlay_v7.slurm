#!/bin/bash
#SBATCH --job-name=xclip_overlay_v7
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --gpus=1
#SBATCH --mem=24gb
#SBATCH --time=01:30:00
#SBATCH --output=logs/xclip_overlay_v7_%j.log

# xclip_overlay_v7.py: fine-tuned RT-DETR + X-CLIP. logs/ must exist.
# Override e.g.: sbatch --export=ALL,START_FRAME=550,MAX_FRAMES=900 run_xclip_overlay_v7.slurm

set -euo pipefail
cd /orange/xiangyan/rithika/vision/vision3
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
export HF_HUB_OFFLINE=1

VIDEO="${VIDEO:-test.mp4}"
OUT="${OUT:-pilot_output/compare_v4/xclip_overlay_v7/overlay.mp4}"
WEIGHTS="${WEIGHTS:-/orange/xiangyan/rithika/vision/vision3/runs/detect/finetune_runs/rtdetr_v3/weights/best.pt}"
START_FRAME="${START_FRAME:-1}"
MAX_FRAMES="${MAX_FRAMES:-0}"
IMGSZ="${IMGSZ:-1280}"
DET_CONF="${DET_CONF:-0.25}"
VEH_WEIGHTS="${VEH_WEIGHTS:-}"
ROAD_ZONE="${ROAD_ZONE:-53,14;104,1;617,1;714,35;715,475;636,477;34,45}"
BIKE_ZONE="${BIKE_ZONE:-44,33;416,184;707,346;716,444;36,41}"
SIDEWALK_ZONE="${SIDEWALK_ZONE:-32,49;11,57;37,247;285,477;632,476}"
# size of the image the polygons were drawn on (Roboflow Polygon Zone canvas). Set to "" if coords are already in video pixels.
ZONE_REF_SIZE="${ZONE_REF_SIZE-716x477}"
VEH_ARG=()
[ -n "$VEH_WEIGHTS" ] && VEH_ARG=(--veh-weights "$VEH_WEIGHTS")
[ -n "$ROAD_ZONE" ] && VEH_ARG+=(--road-zone "$ROAD_ZONE")
[ -n "$BIKE_ZONE" ] && VEH_ARG+=(--bike-zone "$BIKE_ZONE")
[ -n "$SIDEWALK_ZONE" ] && VEH_ARG+=(--sidewalk-zone "$SIDEWALK_ZONE")
[ -n "$ZONE_REF_SIZE" ] && VEH_ARG+=(--zone-ref-size "$ZONE_REF_SIZE")

python xclip_overlay_v7.py \
    --video "$VIDEO" \
    --out "$OUT" \
    --weights "$WEIGHTS" \
    --start-frame "$START_FRAME" \
    --max-frames "$MAX_FRAMES" \
    --imgsz "$IMGSZ" \
    --det-conf "$DET_CONF" \
    ${VEH_ARG[@]+"${VEH_ARG[@]}"}
