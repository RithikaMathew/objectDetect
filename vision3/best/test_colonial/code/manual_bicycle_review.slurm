#!/bin/bash
#SBATCH --job-name=manual_bicycle_pack
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=04:00:00
#SBATCH --output=manual_bicycle_pack_%j.log
set -euo pipefail
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
python code/manual_bicycle_review.py \
 --batch "${BATCH:-exp_results/ADAPTIVE_SPEED_20261024_195012}" \
 --workbooks '/orange/xiangyan/rithika/vision/Bike Lane Study Counts' \
 --out "exp_results/MANUAL_BICYCLE_REVIEW_${SLURM_JOB_ID}" --go
