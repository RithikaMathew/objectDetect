#!/bin/bash
#SBATCH --job-name=mine_frames
#SBATCH --partition=hpg-turin
#SBATCH --account=xilei.zhao
#SBATCH --qos=xilei.zhao
#SBATCH --gpus=1
#SBATCH --mem=16gb
#SBATCH --time=02:00:00
#SBATCH --output=mine_frames_%j.log

# Bucket A of the journal 550-frame recipe: 150 Colonial track hard cases.
#
# RUN THIS BEFORE cleanup_session.sh -- mining reads the .mp4 chunks, and
# cleanup deletes them. Re-extracting a session from the zip is ~30 min.

set -u
cd /orange/xiangyan/rithika/vision
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate

SESSION_DIR="${SESSION_DIR:-pilot_output/sessions/BL_Colonial_2019-07-10}"
VIDEO_DIR="${VIDEO_DIR:-pilot_clips/MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/Standard_SCU8OG_2019-07-10_0000}"
OUT="${OUT:-dataset_frames/colonial_track}"

python pipeline/mine_frames_from_tracks.py \
    --session-dir "$SESSION_DIR" \
    --video-dir "$VIDEO_DIR" \
    --out "$OUT" \
    --site BL-Colonial \
    --split train \
    --per-track 2 \
    --max-frames 150 \
    --min-hits 5 \
    --min-label-conf 0.10

echo
echo "Next: sbatch build_dataset.slurm  (buckets B/C/D), then"
echo "  python pipeline/assemble_annotation_pool.py \\"
echo "    --colonial-dir $OUT \\"
echo "    --build-dir dataset_frames/split \\"
echo "    --out dataset_frames/annotation_pool"
