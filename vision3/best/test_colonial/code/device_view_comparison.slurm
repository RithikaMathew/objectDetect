#!/bin/bash
#SBATCH --job-name=10th_device_views
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:30:00
#SBATCH --output=logs/device_views_%j.log
set -euo pipefail
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
module load ffmpeg 2>/dev/null || true
python code/archive_contents_summary.py
python code/device_view_comparison.py --out "exp_results/10TH_DEVICE_COMPARISON_${SLURM_JOB_ID}"
