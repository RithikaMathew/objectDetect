#!/bin/bash
#SBATCH --job-name=v2_window
#SBATCH --partition=hpg-turin
#SBATCH --account=xilei.zhao
#SBATCH --qos=xilei.zhao
#SBATCH --gpus=1
#SBATCH --mem=16gb
#SBATCH --time=00:30:00
#SBATCH --output=v2_window_%j.log

cd /orange/xiangyan/rithika/vision
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate

# ffmpeg is needed to produce an H.264 file QuickTime will open. OpenCV cannot
# be relied on for this: asked for 'avc1' it selects h264_v4l2m2m, a hardware
# encoder that does not exist on a compute node.
module load ffmpeg 2>/dev/null || echo "note: no ffmpeg module; video stays mp4v"

CLIP="pilot_clips/MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/Standard_SCU8OG_2019-07-10_0000/Standard_SCU8OG_2019-07-10_0000.008.mp4"

# Full-frame-rate annotated clip of the known cyclist window.
# --debug-merge prints the pairwise numbers behind every merge decision.
python pilot_detect_v2.py "$CLIP" \
    --render-window 400 420 \
    --weights yolov8l.pt \
    --debug-merge
