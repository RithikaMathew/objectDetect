#!/bin/bash
#SBATCH --job-name=trk_ablation
#SBATCH --partition=hpg-turin
#SBATCH --account=xilei.zhao
#SBATCH --qos=xilei.zhao
#SBATCH --gpus=1
#SBATCH --mem=16gb
#SBATCH --time=00:30:00
#SBATCH --output=ablation_%j.log

cd /orange/xiangyan/rithika/vision
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate

CLIP="pilot_clips/MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/Standard_SCU8OG_2019-07-10_0000/Standard_SCU8OG_2019-07-10_0000.008.mp4"

# Proves old-vs-new association on the cyclist we know is at t=407-409s.
python tracker_ablation.py "$CLIP" --start 403 --end 415 --stride 5
