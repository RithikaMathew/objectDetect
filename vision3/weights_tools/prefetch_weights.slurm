#!/bin/bash
#SBATCH --job-name=prefetch_weights
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --cpus-per-task=2
#SBATCH --mem=8gb
#SBATCH --time=00:30:00
#SBATCH --output=logs/prefetch_weights_%j.log

# Downloads yolov8x.pt, yolo11x.pt, rtdetr-l.pt, and the VisDrone checkpoint
# once into a shared cache dir, so comparison/run_compare_array_v5.slurm's 5 tasks never
# hit the network or race each other downloading the same file.
#
# logs/ must already exist when this is submitted (SLURM opens --output
# before the script's first line runs) — create it before submission;
# if submitting this file directly, run `mkdir -p logs` first.

set -euo pipefail
cd /orange/xiangyan/rithika/vision/vision3
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate

export WEIGHTS_DIR="${WEIGHTS_DIR:-/orange/xiangyan/rithika/vision/vision3/weights}"
mkdir -p "$WEIGHTS_DIR"

python weights_tools/prefetch_weights.py

echo "=== prefetch complete ==="
ls -la "$WEIGHTS_DIR"
