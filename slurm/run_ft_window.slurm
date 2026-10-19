#!/bin/bash
#SBATCH --job-name=ft_window
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --gpus=1
#SBATCH --mem=16gb
#SBATCH --time=00:45:00
#SBATCH --output=ft_window_%j.log

# ~3 min gated FT window for visual QA (iterate here before any full-hour run).
# Default: Colonial .018, 377–567s.
#
# CAMERA OSD on this clip reads ~17:00 (5 PM), but all_videos.txt lists 22:00.
# We pass --chunk-hour from CHUNK_HOUR so the night gate follows the camera.
# Default CHUNK_HOUR=17. Compare top banner "assumed HH:MM" to the burn-in.
#
#   sbatch run_ft_window.slurm
#   CHUNK_HOUR=22 sbatch run_ft_window.slurm   # force all_videos time (old)
#   DRAW_ALL=1 sbatch run_ft_window.slurm

set -u
cd /orange/xiangyan/rithika/vision
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
module load ffmpeg 2>/dev/null || true

SITE_DIR="${SITE_DIR:-pilot_clips/MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/Standard_SCU8OG_2019-07-10_0000}"
OUTDIR="${OUTDIR:-pilot_output/ft_window_v2}"
WEIGHTS="${WEIGHTS:-runs/detect/sixclass_v1_yolov8l/weights/best.pt}"
SUF="${SUF:-018}"
START="${START:-377}"
END="${END:-567}"
DRAW_ALL="${DRAW_ALL:-0}"
# Camera burn-in on .018 showed 5 PM; all_videos said 22:00.
CHUNK_HOUR="${CHUNK_HOUR:-17}"

if [ ! -f "$WEIGHTS" ]; then
    echo "FATAL: weights missing: $WEIGHTS"
    ls -la runs/detect/sixclass_v1_yolov8l/weights/ 2>/dev/null || true
    exit 1
fi

CLIP=$(find "$SITE_DIR" -maxdepth 1 -name "*.${SUF}.mp4" | sort | head -1)
if [ -z "$CLIP" ]; then
    echo "ERROR: no *.${SUF}.mp4 under $SITE_DIR"
    exit 1
fi

DRAW_FLAG=""
if [ "$DRAW_ALL" = "1" ]; then
    DRAW_FLAG="--draw-all"
fi
COCO_FLAG=""
if [ -f "${COCO_WEIGHTS:-yolov8l.pt}" ]; then
    COCO_FLAG="--also-coco --coco-weights ${COCO_WEIGHTS:-yolov8l.pt}"
fi
ZONES="${ZONES:-data/zones/colonial.json}"

echo "=== FT short window QA (3 min only) ==="
echo "chunk: $CLIP"
echo "window: ${START}s - ${END}s  (~$(( END - START ))s)"
echo "weights: $WEIGHTS"
ls -la "$WEIGHTS"
echo "chunk_hour (camera/override): $CHUNK_HOUR"
echo "outdir: $OUTDIR"
echo "zones: $ZONES"
echo "coco union: ${COCO_FLAG:-off}"
echo

# shellcheck disable=SC2086
python pipeline/pilot_detect_v2.py "$CLIP" 0 \
    --weights "$WEIGHTS" \
    --stride 1 \
    --render-window "$START" "$END" \
    --chunk-hour "$CHUNK_HOUR" \
    --outdir "$OUTDIR" \
    --debug-confirm \
    --dump-dets \
    --zones "$ZONES" \
    $COCO_FLAG \
    $DRAW_FLAG

echo
echo "Download the annotated mp4 in $OUTDIR (look for _h264.mp4)."
DETS=$(ls -1 "$OUTDIR"/*_dets.csv 2>/dev/null | head -1 || true)
if [ -n "$DETS" ]; then
    python pipeline/goal1_window_report.py "$DETS"
fi
