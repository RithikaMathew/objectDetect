#!/bin/bash
#SBATCH --job-name=bike_ped_compare
#SBATCH --partition=hpg-turin
#SBATCH --account=xilei.zhao
#SBATCH --qos=xilei.zhao
#SBATCH --gpus=1
#SBATCH --mem=32gb
#SBATCH --time=02:00:00
#SBATCH --output=logs/bike_ped_compare_%j.log

# Runs bike_ped_compare_v1.py (xclip, clip, siglip, videomae, speed) as a batch job.
# All HF models must be cached on the login node first (job runs offline).
# logs/ must exist before submitting (mkdir -p logs).
#
# Override at submit time, e.g.:
#   sbatch --export=ALL,BACKENDS="xclip speed" run_bike_ped_compare_v1.slurm
#   sbatch --export=ALL,TRUTH="1=pedestrian 2=bicyclist" run_bike_ped_compare_v1.slurm

set -euo pipefail
cd /orange/xiangyan/rithika/vision/vision3
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate

export HF_HUB_OFFLINE=1

VIDEO="${VIDEO:-test.mp4}"
CSV="${CSV:-pilot_output/compare_v4/track_j_diagnostic.csv}"
OUTDIR="${OUTDIR:-pilot_output/compare_v4/bike_ped_compare_v1}"
BACKENDS="${BACKENDS:-xclip clip siglip videomae speed}"
TRUTH="${TRUTH:-1=pedestrian 2=bicyclist 5=pedestrian}"
MAX_FRAMES="${MAX_FRAMES:-0}"

python comparison/bike_ped_compare_v1.py \
    --video "$VIDEO" \
    --csv "$CSV" \
    --outdir "$OUTDIR" \
    --backends $BACKENDS \
    --truth $TRUTH \
    --max-frames "$MAX_FRAMES"
