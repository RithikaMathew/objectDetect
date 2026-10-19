#!/bin/bash
#SBATCH --job-name=pilot_detect
#SBATCH --partition=hpg-turin
#SBATCH --account=xilei.zhao
#SBATCH --qos=xilei.zhao
#SBATCH --gpus=1
#SBATCH --mem=16gb
#SBATCH --time=04:00:00
#SBATCH --output=pilot_detect_%j.log

# Run from the same directory you'd normally cd into before running python
cd /orange/xiangyan/rithika/vision

source /orange/xiangyan/rithika/vision/yolo_env/bin/activate

python pilot_detect.py "pilot_clips/MioVision Data/2021 Data/Anderson St/Standard_SCU8PM_2021-04-13_0000/Standard_SCU8PM_2021-04-13_0000.013.mp4" 1800
