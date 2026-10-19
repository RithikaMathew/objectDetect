#!/bin/bash
#SBATCH --job-name=diag_track_j
#SBATCH --output=logs/diag_track_j_%j.log
#SBATCH --error=logs/diag_track_j_%j.log
#SBATCH --partition=gpu
#SBATCH --gpus=1
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --cpus-per-task=4

# Adjust --partition / --gres / --account above to match whatever
# run_compare_array_v4.slurm uses on your allocation -- this mirrors the
# same style so it should slot in next to it.

cd /orange/xiangyan/rithika/vision/vision3
mkdir -p logs

module load conda 2>/dev/null || true
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate

python diagnose_track_j_v1.py \
    --video test.mp4 \
    --finetune-weights finetune_runs/rtdetr_v1/weights/best.pt \
    --outdir pilot_output/compare_v4
