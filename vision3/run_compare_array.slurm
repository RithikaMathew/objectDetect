#!/bin/bash
#SBATCH --job-name=cyclist_compare
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --gpus=1
#SBATCH --mem=16gb
#SBATCH --time=01:00:00
#SBATCH --array=0-4
#SBATCH --output=logs/cyclist_compare_%A_%a.log

# Runs methods A-E in parallel, one per array task, each on its own GPU node.
# Submit AFTER prefetch_weights.slurm has completed (see submit_all.sh),
# so no task tries to download weights itself.
#
# logs/ must already exist when this is submitted (SLURM opens --output
# before the script's first line runs) — submit_all.sh creates it for you;
# if submitting this file directly, run `mkdir -p logs` first.
#
# Override any of these at submit time, e.g.:
#   sbatch --export=VIDEO_PATH=/orange/.../myclip.mp4 run_compare_array.slurm

set -euo pipefail
cd /orange/xiangyan/rithika/vision/vision3
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
module load ffmpeg 2>/dev/null || true

METHODS=(A B C D E)
METHOD="${METHODS[$SLURM_ARRAY_TASK_ID]}"

WEIGHTS_DIR="${WEIGHTS_DIR:-/orange/xiangyan/rithika/vision/vision3/weights}"
OUTDIR="${OUTDIR:-/orange/xiangyan/rithika/vision/vision3/pilot_output/compare}"
VIDEO="${VIDEO_PATH:-$(find . -maxdepth 1 -name '*.mp4' | sort | head -1)}"

if [ -z "$VIDEO" ]; then
    echo "ERROR: no .mp4 found in $(pwd) and VIDEO_PATH not set"
    exit 1
fi

# submit_all.sh uses an afterany dependency (afterok is unreliable on some
# clusters' dependency accounting), which does NOT guarantee prefetch
# actually succeeded -- check explicitly so a real prefetch failure fails
# loudly here instead of each of the 5 tasks trying (and racing) to
# re-download weights themselves.
for f in yolov8x.pt yolo11x.pt rtdetr-l.pt visdrone_yolo11x.pt; do
    if [ ! -f "$WEIGHTS_DIR/$f" ]; then
        echo "ERROR: $WEIGHTS_DIR/$f missing -- prefetch_weights.slurm did not complete successfully."
        echo "Check its log (prefetch_weights_<jobid>.log) before resubmitting."
        exit 1
    fi
done

echo "=== method $METHOD ==="
echo "video:   $VIDEO"
echo "weights: $WEIGHTS_DIR"
echo "outdir:  $OUTDIR"

python compare_detectors.py \
    --method "$METHOD" \
    --video "$VIDEO" \
    --weights-dir "$WEIGHTS_DIR" \
    --outdir "$OUTDIR"
