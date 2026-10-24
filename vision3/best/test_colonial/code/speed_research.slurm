#!/bin/bash
#SBATCH --job-name=colonial_speed_research
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --gpus=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=04:00:00
#SBATCH --output=logs/colonial_speed_research_%j.log
set -euo pipefail
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
# Original source, not annotated/header-added video. No full study/model rerun.
SOURCE_VIDEO='/orange/xiangyan/rithika/vision/pilot_clips/MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/Standard_SCU8OG_2019-07-10_0000/Standard_SCU8OG_2019-07-10_0000.013.mp4'
python code/speed_research.py --root . --video "$SOURCE_VIDEO" \
  --frames 3000 --sample-stride 3 --device cuda \
  --out "exp_results/colonial_speed_research_${SLURM_JOB_ID}"
