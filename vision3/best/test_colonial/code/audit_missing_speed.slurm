#!/bin/bash
#SBATCH --job-name=audit_missing_speeds
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=02:00:00
#SBATCH --output=missing_speed_audit_%j.log
set -euo pipefail
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
python code/audit_missing_speed.py \
 --batch exp_results/ADAPTIVE_SPEED_20261024_195012 \
 --manual /orange/xiangyan/rithika/vision/manual \
 --out "exp_results/MISSING_SPEED_AUDIT_${SLURM_JOB_ID}" --clips
