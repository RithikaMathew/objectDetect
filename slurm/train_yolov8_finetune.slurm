#!/bin/bash
#SBATCH --job-name=yolo_ft
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --gpus=1
#SBATCH --mem=32gb
#SBATCH --time=08:00:00
#SBATCH --output=yolo_ft_%j.log
#SBATCH --requeue

# Fine-tune YOLOv8-L on the site-held-out six-class dataset.
# Prerequisite on the cluster:
#   1. Copy vision2.v1-...yolov8.zip (or already-split yolo_sixclass_v1/) up
#   2. python pipeline/split_roboflow_by_site.py --zip ... --out dataset_frames/yolo_sixclass_v1
#
# imgsz=1280 matches pilot_detect_v2 full-frame path. Tile-matched training
# (2x2 @ 640) is a follow-up ablation — see HANDOFF §5.3.

set -u
cd /orange/xiangyan/rithika/vision
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate

DATA_DIR="${DATA_DIR:-dataset_frames/yolo_sixclass_v1}"
DATA="${DATA:-$DATA_DIR/data.yaml}"
WEIGHTS="${WEIGHTS:-yolov8l.pt}"
RUN_NAME="${RUN_NAME:-sixclass_v1_yolov8l}"
EPOCHS="${EPOCHS:-80}"
IMGSZ="${IMGSZ:-1280}"
BATCH="${BATCH:-4}"

if [[ ! -f "$DATA" ]]; then
  echo "ERROR: missing $DATA"
  echo "Run: python pipeline/split_roboflow_by_site.py --zip data/vision2.v1-six-class-corrected-v1.yolov8.zip --out dataset_frames/yolo_sixclass_v1"
  exit 1
fi

echo "=== Fine-tune ==="
echo "  data:    $DATA"
echo "  weights: $WEIGHTS"
echo "  name:    $RUN_NAME"
echo "  epochs:  $EPOCHS  imgsz=$IMGSZ  batch=$BATCH"
cat "$DATA"
echo

# data.yaml uses path: .  — run from the dataset directory
# model weights live in the vision root / ultralytics cache
cd "$DATA_DIR"
MODEL_PATH="$WEIGHTS"
if [[ "$WEIGHTS" != /* ]]; then
  MODEL_PATH="/orange/xiangyan/rithika/vision/$WEIGHTS"
fi
# fall back to cwd weight name if not found (ultralytics will download)
[[ -f "$MODEL_PATH" ]] || MODEL_PATH="$WEIGHTS"

yolo detect train \
  model="$MODEL_PATH" \
  data=data.yaml \
  epochs="$EPOCHS" \
  imgsz="$IMGSZ" \
  batch="$BATCH" \
  workers=4 \
  project=/orange/xiangyan/rithika/vision/runs/detect \
  name="$RUN_NAME" \
  exist_ok=True \
  patience=20 \
  save=True \
  plots=True

BEST="/orange/xiangyan/rithika/vision/runs/detect/${RUN_NAME}/weights/best.pt"
echo
echo "Done. Best weights: $BEST"
echo "Val metrics under runs/detect/${RUN_NAME}/"
echo
echo "Next — recount with fine-tuned weights:"
echo "  python pipeline/pilot_detect_v2.py ... --weights $BEST"
echo "  python pipeline/validate_counts.py ..."
