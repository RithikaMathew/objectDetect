#!/bin/bash
#SBATCH --job-name=cyclist_compare_v2
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --gpus=1
#SBATCH --mem=16gb
#SBATCH --time=01:00:00
#SBATCH --array=0-6
#SBATCH --output=logs/cyclist_compare_v2_%A_%a.log

# Runs methods A-G in parallel, one per array task, each on its own GPU node.
# Uses compare_detectors_v2.py (adds Method F: YOLO26x, Method G: motion-guided
# cropping) -- v1's methods A-E are unchanged, just re-run here for a clean
# side-by-side comparison across all 7 in one aggregate_results.py table.
#
# logs/ must already exist before this is submitted (SLURM opens --output
# before the job script's first line runs): mkdir -p logs first.
#
# Before submitting, make sure yolo26x.pt is in weights/ -- run this on the
# LOGIN NODE first (not via sbatch):
#   python prefetch_weights_v2.py
#
# Override any of these at submit time, e.g.:
#   sbatch --export=VIDEO_PATH=/orange/.../myclip.mp4 run_compare_array_v2.slurm

set -euo pipefail
cd /orange/xiangyan/rithika/vision/vision3
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
module load ffmpeg 2>/dev/null || true

METHODS=(A B C D E F G)
METHOD="${METHODS[$SLURM_ARRAY_TASK_ID]}"

WEIGHTS_DIR="${WEIGHTS_DIR:-/orange/xiangyan/rithika/vision/vision3/weights}"
OUTDIR="${OUTDIR:-/orange/xiangyan/rithika/vision/vision3/pilot_output/compare_v2}"
VIDEO="${VIDEO_PATH:-$(find . -maxdepth 1 -name '*.mp4' | sort | head -1)}"

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

echo "=== method $METHOD ==="
echo "video:   $VIDEO"
echo "weights: $WEIGHTS_DIR"
echo "outdir:  $OUTDIR"

python compare_detectors_v2.py \
    --method "$METHOD" \
    --video "$VIDEO" \
    --weights-dir "$WEIGHTS_DIR" \
    --outdir "$OUTDIR"
