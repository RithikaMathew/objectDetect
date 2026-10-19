#!/bin/bash
#SBATCH --job-name=v2_full
#SBATCH --partition=hpg-turin
#SBATCH --account=xilei.zhao
#SBATCH --qos=xilei.zhao
#SBATCH --gpus=1
#SBATCH --mem=16gb
#SBATCH --time=04:00:00
#SBATCH --output=v2_full_%j.log

cd /orange/xiangyan/rithika/vision
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
module load ffmpeg 2>/dev/null || echo "note: no ffmpeg module; video stays mp4v"

CLIP="pilot_clips/MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/Standard_SCU8OG_2019-07-10_0000/Standard_SCU8OG_2019-07-10_0000.008.mp4"

# Whole 45-min chunk. Video defaults to --video-mode highlights: only the spans
# containing a confirmed cyclist/pedestrian are rendered, +/- 2s of context.
# The previous full run produced a 132 MB unwatchable file covering 45 minutes
# of mostly empty road; this writes seconds of video instead of an hour.
python pilot_detect_v2.py "$CLIP" 0 \
    --weights yolov8l.pt \
    --stride 3
