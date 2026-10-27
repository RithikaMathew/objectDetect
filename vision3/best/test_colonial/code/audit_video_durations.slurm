#!/bin/bash
#SBATCH --job-name=video_duration_audit
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=24:00:00
#SBATCH --output=logs/video_duration_audit_%j.log
set -euo pipefail
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
module load ffmpeg 2>/dev/null || true
python code/audit_video_durations.py --out exp_results/VIDEO_DURATION_AUDIT
