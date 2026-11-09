#!/bin/bash
#SBATCH --job-name=clearance_pilot
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --gpus=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=02:00:00
set -euo pipefail
ROOT=/orange/xiangyan/rithika/vision/vision3/best/test_colonial
cd "$ROOT"
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
module load ffmpeg 2>/dev/null || true
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
python -u code/clearance_pilot.py "${2:-run}" "$1"
