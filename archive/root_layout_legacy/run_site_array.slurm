#!/bin/bash
#SBATCH --job-name=site_count
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --gpus=1
#SBATCH --mem=16gb
#SBATCH --time=06:00:00
#SBATCH --array=0-47%12
#SBATCH --output=site_count_%A_%a.log

# ONE SITE-SESSION, ALL HOURLY CHUNKS, IN PARALLEL.
#
# A session is ~48 hourly .mp4 chunks. Run serially that is ~2h/chunk = 4 days.
# As a Slurm array each chunk is its own task, so wall-clock is set by the
# slowest chunk plus queue time. %12 caps concurrency at 12 tasks so this does
# not monopolise the group's GPU allocation -- raise it if the partition is
# quiet, lower it if others are queued.
#
# Set SITE_DIR to a session folder from video_site_mapping.csv. Defaults to
# BL Colonial 2019-07-10 (ground truth: Colonial North, 89 cyclists).
#
# Override weights for fine-tuned model, e.g.:
#   WEIGHTS=runs/detect/sixclass_v1_yolov8l/weights/best.pt \
#   OUTDIR=pilot_output/sessions/BL_Colonial_2019-07-10_ft_v2 \
#   sbatch run_site_array.slurm
#
# (Keep the failed COCO-gated FT run under ..._ft for comparison.)
# FT confirmation gates auto-apply when best.pt class names are six-class;
# COCO yolov8l.pt keeps the original gates.
# The array range must cover the chunk count. Most sessions are 48, but a few
# differ -- Rinehart Road SW has 96, Pine Hills BL E has 25 (see
# video_site_mapping.csv, column n_mp4_chunks). Tasks beyond the chunk count
# exit cleanly, so over-provisioning is harmless; under-provisioning silently
# drops footage and quietly biases the count DOWN. Override at submit time:
#     sbatch --array=0-95%12 run_site_array.slurm
# Always check the printed "task N / TOTAL" line against n_mp4_chunks.

set -u

cd /orange/xiangyan/rithika/vision
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
module load ffmpeg 2>/dev/null || true

SITE_DIR="${SITE_DIR:-pilot_clips/MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/Standard_SCU8OG_2019-07-10_0000}"
OUTDIR="${OUTDIR:-pilot_output/sessions/BL_Colonial_2019-07-10}"
WEIGHTS="${WEIGHTS:-yolov8l.pt}"

# Deterministic chunk ordering, so array index N always maps to the same file
mapfile -t CHUNKS < <(find "$SITE_DIR" -maxdepth 1 -name "*.mp4" | sort)
N=${#CHUNKS[@]}

if [ "$SLURM_ARRAY_TASK_ID" -ge "$N" ]; then
    echo "Task $SLURM_ARRAY_TASK_ID >= $N chunks -- nothing to do."
    exit 0
fi

CLIP="${CHUNKS[$SLURM_ARRAY_TASK_ID]}"
echo "=== task $SLURM_ARRAY_TASK_ID / $N ==="
echo "chunk: $CLIP"
echo "weights: $WEIGHTS"
echo "outdir: $OUTDIR"

# --video-mode none: at this scale video is a liability, not a diagnostic.
# The per-track CSV is what validation reads. Render video only for the
# specific windows you want to inspect, via run_v2_window.slurm.
python pilot_detect_v2.py "$CLIP" 0 \
    --weights "$WEIGHTS" \
    --stride 5 \
    --video-mode none \
    --outdir "$OUTDIR"
