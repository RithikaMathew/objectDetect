#!/bin/bash
#SBATCH --job-name=rtdetr_night
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --gpus=1
#SBATCH --mem=32gb
#SBATCH --time=08:00:00
#SBATCH --output=logs/slurm_%x_%j.log
# usage: sbatch --export=ALL,DATA=<merged data.yaml>,NAME=rtdetr_v4_night code/train_rtdetr_night_v1.slurm   (run from test_colonial/)
set -euo pipefail
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
export HF_HUB_OFFLINE=1
python code/train_rtdetr_night_v1.py --data "${DATA:?set DATA=<data.yaml>}" --name "${NAME:-rtdetr_v4_night}"
