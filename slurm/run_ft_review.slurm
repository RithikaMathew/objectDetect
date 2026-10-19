#!/bin/bash
#SBATCH --job-name=ft_review
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --gpus=1
#SBATCH --mem=16gb
#SBATCH --time=00:45:00
#SBATCH --array=0-3
#SBATCH --output=ft_review_%A_%a.log

# Render short FT overcount review clips (night peaks + day).
#
# Prerequisites:
#   python plan_ft_review_clips.py \
#     --session-dir pilot_output/sessions/BL_Colonial_2019-07-10_ft \
#     --video-dir "pilot_clips/MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/Standard_SCU8OG_2019-07-10_0000"
#
# Then:
#   CLIPS=ft_review_clips.txt OUTDIR=pilot_output/ft_review \
#     sbatch --array=0-3 run_ft_review.slurm
#
# Uses best.pt. Default: NEW FT gates (post clip-review). To replay the
# overcounting 1445 behavior: GATE_FLAGS=--force-coco-gates
# Omit --draw-all (DRAW_ALL=0) to see only confirmed tracks (less flicker).

set -u
cd /orange/xiangyan/rithika/vision
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
module load ffmpeg 2>/dev/null || true

CLIPS="${CLIPS:-ft_review_clips.txt}"
OUTDIR="${OUTDIR:-pilot_output/ft_review}"
WEIGHTS="${WEIGHTS:-runs/detect/sixclass_v1_yolov8l/weights/best.pt}"
# Empty = automatic FT confirmation + night gate in pilot_detect_v2.py
GATE_FLAGS="${GATE_FLAGS:-}"
DRAW_ALL="${DRAW_ALL:-0}"

N=$(wc -l < "$CLIPS")
if [ "$SLURM_ARRAY_TASK_ID" -ge "$N" ]; then
    echo "Task $SLURM_ARRAY_TASK_ID >= $N clips -- nothing to do."
    exit 0
fi

LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$CLIPS")
CLIP=$(echo "$LINE" | cut -d'|' -f1)
START=$(echo "$LINE" | cut -d'|' -f2)
END=$(echo "$LINE" | cut -d'|' -f3)
LABEL=$(echo "$LINE" | cut -d'|' -f4)

DRAW_FLAG=""
if [ "$DRAW_ALL" = "1" ]; then
    DRAW_FLAG="--draw-all"
fi

echo "=== FT review clip $SLURM_ARRAY_TASK_ID / $N ==="
echo "video : $CLIP"
echo "window: ${START}s - ${END}s"
echo "label : $LABEL"
echo "weights: $WEIGHTS"
echo "gates: ${GATE_FLAGS:-"(FT auto)"}"
echo "draw_all: $DRAW_ALL"
echo

# shellcheck disable=SC2086
python pipeline/pilot_detect_v2.py "$CLIP" 0 \
    --weights "$WEIGHTS" \
    --stride 1 \
    --render-window "$START" "$END" \
    --outdir "$OUTDIR" \
    $DRAW_FLAG \
    $GATE_FLAGS
