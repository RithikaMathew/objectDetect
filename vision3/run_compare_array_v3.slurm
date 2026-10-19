#!/bin/bash
#SBATCH --job-name=cyclist-cmp-v3
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --partition=gpu
#SBATCH --gpus=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32gb
#SBATCH --time=01:00:00
#SBATCH --array=0-7
#SBATCH --output=logs/cmp_v3_%A_%a.out
#SBATCH --error=logs/cmp_v3_%A_%a.err

# Same weights-file existence check pattern as v2's array job (bug #3 fix:
# afterany + explicit check, since afterok dependency checking isn't
# reliable on this cluster's accounting setup).
WEIGHTS_DIR="/orange/xiangyan/rithika/vision/vision3/weights"
for f in yolov8x.pt yolo11x.pt rtdetr-l.pt visdrone_yolo11x.pt yolo26x.pt; do
  if [ ! -f "${WEIGHTS_DIR}/${f}" ]; then
    echo "ERROR: missing ${WEIGHTS_DIR}/${f} -- prefetch step didn't finish" >&2
    exit 1
  fi
done

METHODS=(A B C D E F G H)
METHOD=${METHODS[$SLURM_ARRAY_TASK_ID]}

source /orange/xiangyan/rithika/vision/yolo_env/bin/activate

cd /orange/xiangyan/rithika/vision/vision3

python compare_detectors_v3.py \
    --method "${METHOD}" \
    --video test.mp4 \
    --weights-dir "${WEIGHTS_DIR}" \
    --outdir pilot_output/compare_v3
