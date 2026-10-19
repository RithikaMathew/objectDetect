#!/bin/bash
#SBATCH --job-name=review_pack
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=01:00:00
#SBATCH --output=logs/slurm_review_pack_%j.log
# CPU-only cuts from raw footage so model overlays cannot influence labels.
set -euo pipefail
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
module load ffmpeg 2>/dev/null || true
command -v ffmpeg >/dev/null
SOURCE_DIR="${SOURCE_DIR:-/orange/xiangyan/rithika/vision/pilot_clips/MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/Standard_SCU8OG_2019-07-10_0000}"
PACK="${PACK:-review/raw_tracks_${SLURM_JOB_ID}}"
python code/review_pack.py build \
    --table "${TABLE:-validation/track_truth_runs45_v2.csv}" \
    --budget-min "${BUDGET_MIN:-0}" \
    --source-dir "$SOURCE_DIR" --out "$PACK"
echo "Download $PACK and open review.html. Label from the raw video, then download labels.csv."
