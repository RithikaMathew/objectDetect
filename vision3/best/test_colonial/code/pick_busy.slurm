#!/bin/bash
#SBATCH --job-name=pick_busy
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --gpus=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=01:30:00
#SBATCH --output=logs/slurm_pick_busy_%j.log
# Submit ONCE from test_colonial after writing videos_to_scan.txt:  sbatch code/pick_busy.slurm
set -euo pipefail
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
python code/pick_busy_windows.py --list videos_to_scan.txt --out busy/inventory.csv --higher-res-only
