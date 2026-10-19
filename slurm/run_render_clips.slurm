#!/bin/bash
#SBATCH --job-name=render_clips
#SBATCH --partition=hpg-turin
#SBATCH --account=xilei.zhao
#SBATCH --qos=xilei.zhao
#SBATCH --gpus=1
#SBATCH --mem=16gb
#SBATCH --time=01:00:00
#SBATCH --array=0-0
#SBATCH --output=render_clips_%A_%a.log

# Render one short annotated clip per counted cyclist.
#
# Submit with the range plan_cyclist_clips.py prints, e.g.
#     sbatch --array=0-88%12 run_render_clips.slurm
# The 0-0 default above is a placeholder so a bare sbatch does something safe
# rather than silently rendering nothing.
#
# --stride 5 matches the counting run. That is deliberate: rendering at full
# frame rate would show the video a DIFFERENT pipeline saw, with different
# detections, associations and confirmations, so a clip could show a cyclist
# the counting pass never had the chance to see. Matching the stride means what
# you watch is what was counted -- 6 fps and choppy, but honest.

set -u
cd /orange/xiangyan/rithika/vision
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
module load ffmpeg 2>/dev/null || true

CLIPS="${CLIPS:-cyclist_clips.txt}"
OUTDIR="${OUTDIR:-pilot_output/cyclist_clips}"

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

echo "=== clip $SLURM_ARRAY_TASK_ID / $N ==="
echo "video : $CLIP"
echo "window: ${START}s - ${END}s"
echo "track : $LABEL"
echo

python pipeline/pilot_detect_v2.py "$CLIP" \
    --render-window "$START" "$END" \
    --stride 5 \
    --weights yolov8l.pt \
    --outdir "$OUTDIR"
