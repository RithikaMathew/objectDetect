#!/bin/bash
#SBATCH --job-name=colonial_yolov8l
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

python pilot_detect_yolov8l.py "pilot_clips/MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/Standard_SCU8OG_2019-07-10_0000/Standard_SCU8OG_2019-07-10_0000.008.mp4" 2700
