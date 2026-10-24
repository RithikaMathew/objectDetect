#!/bin/bash
#SBATCH --job-name=speed_readiness
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:30:00
#SBATCH --output=logs/speed_readiness_%j.log
set -euo pipefail
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
module load ffmpeg 2>/dev/null || true
# SLURM_JOB_ID gives each submission a fresh report folder.
python code/speed_readiness.py --out "exp_results/speed_readiness_${SLURM_JOB_ID}"
