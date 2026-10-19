#!/bin/bash
#SBATCH --job-name=continuity_check
#SBATCH --partition=hpg-turin
#SBATCH --account=xilei.zhao
#SBATCH --qos=xilei.zhao
#SBATCH --gpus=1
#SBATCH --mem=16gb
#SBATCH --time=00:15:00
#SBATCH --output=pilot_detect_%j.log

# Run from the same directory you'd normally cd into before running python
cd /orange/xiangyan/rithika/vision

source /orange/xiangyan/rithika/vision/yolo_env/bin/activate

python tiled_continuity_check.py
