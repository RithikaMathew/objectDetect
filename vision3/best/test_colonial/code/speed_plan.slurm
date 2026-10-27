#!/bin/bash
#SBATCH --job-name=bicycle_speed_plan
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=02:00:00
#SBATCH --output=logs/speed_plan_%j.log
set -euo pipefail
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
module load ffmpeg 2>/dev/null || true
python code/speed_plan.py \
  --videos exp_results/MANUAL_BICYCLE_REVIEW_47586267 \
  --out "exp_results/SPEED_PLAN_${SLURM_JOB_ID}"
