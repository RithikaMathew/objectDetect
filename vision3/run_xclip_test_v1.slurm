#!/bin/bash
#SBATCH --job-name=xclip_track_test
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --gpus=1
#SBATCH --mem=16gb
#SBATCH --time=00:30:00
#SBATCH --output=logs/xclip_track_test_%j.log

# Runs xclip_track_test_v1.py as a batch job so it survives closing the terminal.
# Compute nodes may have no internet, so cache the model on the login node FIRST
# (see the README lines below), then this job runs fully offline.
#
# logs/ must already exist before this is submitted (mkdir -p logs).
#
# Override at submit time, e.g.:
#   sbatch --export=ALL,TRACK_IDS="1 2 5" run_xclip_test_v1.slurm

set -euo pipefail
cd /orange/xiangyan/rithika/vision/vision3
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate

export HF_HUB_OFFLINE=1   # use the cached model, do not try to reach the internet

VIDEO="${VIDEO:-test.mp4}"
CSV="${CSV:-pilot_output/compare_v4/track_j_diagnostic.csv}"
TRACK_IDS="${TRACK_IDS:-1 2 5}"
OUTDIR="${OUTDIR:-pilot_output/compare_v4/xclip_test_v1}"

python xclip_track_test_v1.py \
    --video "$VIDEO" \
    --csv "$CSV" \
    --track-ids $TRACK_IDS \
    --outdir "$OUTDIR" \
    --save-crops
