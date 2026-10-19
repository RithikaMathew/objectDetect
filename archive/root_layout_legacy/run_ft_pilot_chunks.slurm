#!/bin/bash
#SBATCH --job-name=ft_pilot
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --gpus=1
#SBATCH --mem=16gb
#SBATCH --time=06:00:00
#SBATCH --array=0-1
#SBATCH --output=ft_pilot_%A_%a.log

# Pilot FT recount with NEW gates: one night chunk + one day chunk.
#
# Default suffixes: 018 (night ~22:00) and 010 (day). Override:
#   CHUNK_SUFFIXES=018,012 sbatch run_ft_pilot_chunks.slurm
#
# After pilots look sane (night count << old 129, day not collapsed):
#   WEIGHTS=...best.pt \
#   OUTDIR=pilot_output/sessions/BL_Colonial_2019-07-10_ft_v2 \
#   sbatch run_site_array.slurm

set -u
cd /orange/xiangyan/rithika/vision
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
module load ffmpeg 2>/dev/null || true

SITE_DIR="${SITE_DIR:-pilot_clips/MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/Standard_SCU8OG_2019-07-10_0000}"
OUTDIR="${OUTDIR:-pilot_output/sessions/BL_Colonial_2019-07-10_ft_pilot}"
WEIGHTS="${WEIGHTS:-runs/detect/sixclass_v1_yolov8l/weights/best.pt}"
CHUNK_SUFFIXES="${CHUNK_SUFFIXES:-018,010}"

IFS=',' read -r -a SUFS <<< "$CHUNK_SUFFIXES"
if [ "$SLURM_ARRAY_TASK_ID" -ge "${#SUFS[@]}" ]; then
    echo "Task $SLURM_ARRAY_TASK_ID >= ${#SUFS[@]} suffixes -- nothing to do."
    exit 0
fi

SUF=$(printf "%03d" "$((10#${SUFS[$SLURM_ARRAY_TASK_ID]}))")
# Find the matching mp4 (basename ends with .NNN.mp4)
CLIP=$(find "$SITE_DIR" -maxdepth 1 -name "*.${SUF}.mp4" | sort | head -1)
if [ -z "$CLIP" ]; then
    echo "ERROR: no *.${SUF}.mp4 under $SITE_DIR"
    exit 1
fi

echo "=== FT pilot task $SLURM_ARRAY_TASK_ID ==="
echo "suffix: .$SUF"
echo "chunk:  $CLIP"
echo "weights: $WEIGHTS"
echo "outdir: $OUTDIR"
echo "(using automatic FT confirmation + night gate from pilot_detect_v2.py)"
echo

python pilot_detect_v2.py "$CLIP" 0 \
    --weights "$WEIGHTS" \
    --stride 5 \
    --video-mode none \
    --outdir "$OUTDIR"

# Quick counted tally for this chunk
TAG=$(basename "$CLIP" .mp4)
TRACKS="$OUTDIR/${TAG}_tracks.csv"
if [ -f "$TRACKS" ]; then
    python - <<PY
import csv
path = "$TRACKS"
n = sum(1 for r in csv.DictReader(open(path))
        if r["class"] in ("cyclist", "bicycle") and r["counted"] == "yes")
print(f"COUNTED cyclists in {path}: {n}")
PY
fi
