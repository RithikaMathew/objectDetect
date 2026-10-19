#!/bin/bash
#SBATCH --job-name=compare_30s
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --gpus=1
#SBATCH --mem=16gb
#SBATCH --time=01:30:00
#SBATCH --output=compare_30s_%j.log

# Controlled 30-second comparison on the known cyclist window and v2 pipeline.
# Models: YOLOv8l COCO, YOLO26l COCO, and the six-class fine-tune.
# Keep all inference settings identical so differences are attributable to weights.

set -euo pipefail
cd /orange/xiangyan/rithika/vision
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
module load ffmpeg 2>/dev/null || true

SITE_DIR="${SITE_DIR:-pilot_clips/MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/Standard_SCU8OG_2019-07-10_0000}"
SUF="${SUF:-018}"
OUTROOT="${OUTROOT:-pilot_output/compare_30s}"
CHUNK_HOUR="${CHUNK_HOUR:-17}"
START="${START:-377}"
END="${END:-407}"
CLIP=$(find "$SITE_DIR" -maxdepth 1 -name "*.${SUF}.mp4" | sort | head -1)

if [ -z "$CLIP" ]; then
    echo "ERROR: no *.${SUF}.mp4 under $SITE_DIR"
    exit 1
fi

run_model() {
    local label="$1"
    local weights="$2"
    local outdir="$OUTROOT/$label"
    if [ ! -f "$weights" ]; then
        echo "FATAL: weights missing for $label: $weights"
        exit 1
    fi
    echo "=== $label ==="
    echo "weights: $weights"
    echo "clip: $CLIP"
    echo "window: ${START}-${END}s"
    mkdir -p "$outdir"
    python pilot_detect_v2.py "$CLIP" 0 \
        --weights "$weights" \
        --stride 1 \
        --render-window "$START" "$END" \
        --chunk-hour "$CHUNK_HOUR" \
        --outdir "$outdir" \
        --debug-confirm
}

run_model yolov8l_coco yolov8l.pt
run_model yolo26l_coco yolo26l.pt
run_model yolov8l_finetuned runs/detect/sixclass_v1_yolov8l/weights/best.pt

echo "=== comparison complete ==="
echo "Outputs: $OUTROOT"
