#!/bin/bash
#SBATCH --job-name=ft_v5_colonial
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --gpus=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=04:00:00
#SBATCH --output=logs/slurm_ft_v5_%j.log
# Submit ONCE from test_colonial:  sbatch code/finetune_v5.slurm   (check the partition/GPU lines against code/run_xclip_colonial_v19.slurm)
set -e
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
python code/finetune_v5.py train --data dataset_frames/merged_colonial_v5 --name rtdetr_v5_colonial
