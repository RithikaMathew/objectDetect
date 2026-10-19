#!/bin/bash
#SBATCH --job-name=colonial_v11
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --gpus=1
#SBATCH --mem=32gb
#SBATCH --time=04:00:00
#SBATCH --output=logs/slurm_%x_%A_%a.log

# xclip_overlay_v11_colonial.py : fine-tuned RT-DETR + X-CLIP, one hourly chunk per array task.
# Array task id = chunk number N (.001 = 2019-07-10 00:00, .025 = 2019-07-11 00:00).
#
# Run from the test_colonial folder so that logs/ resolves:
#   cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
#   sbatch --export=ALL,RUN=colonial_run1 --array=8     code/run_xclip_colonial_v11.slurm   # test: 07:00-08:00
#   sbatch --export=ALL,RUN=colonial_run2 --array=1-24  code/run_xclip_colonial_v11.slurm   # block 1 (07-10)
#   sbatch --export=ALL,RUN=colonial_run3 --array=25-48 code/run_xclip_colonial_v11.slurm   # block 2 (07-11)
# Quick smoke test (first 2 minutes only):  --export=ALL,RUN=smoke1,MAX_FRAMES=3600 --array=8
# A new RUN name per submission keeps every run's outputs separate (nothing is overwritten).

set -euo pipefail

ROOT=/orange/xiangyan/rithika/vision/vision3/best/test_colonial
cd "$ROOT"
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
module load ffmpeg 2>/dev/null || true      # for H.264 re-encode of the annotated clips (optional)
export HF_HUB_OFFLINE=1

CHUNK="${SLURM_ARRAY_TASK_ID:-${CHUNK:?set --array=N or CHUNK=N}}"
N=$(printf "%03d" "$CHUNK")
RUN="${RUN:?set RUN=<run name>, e.g. colonial_run1}"

VDIR="/orange/xiangyan/rithika/vision/pilot_clips/MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/Standard_SCU8OG_2019-07-10_0000"
VIDEO="$VDIR/Standard_SCU8OG_2019-07-10_0000.$N.mp4"
[ -f "$VIDEO" ] || { echo "ERROR: missing $VIDEO"; exit 1; }

WEIGHTS="${WEIGHTS:-/orange/xiangyan/rithika/vision/vision3/runs/detect/finetune_runs/rtdetr_v3/weights/best.pt}"
SESSION_START="${SESSION_START:-2019-07-10 00:00:00}"
IMGSZ="${IMGSZ:-1280}"
DET_CONF="${DET_CONF:-0.25}"
START_FRAME="${START_FRAME:-1}"
MAX_FRAMES="${MAX_FRAMES:-0}"
VEH_WEIGHTS="${VEH_WEIGHTS:-}"
# Colonial has its own camera: only use a zones file if you have made one for it.
ZONES_JSON="${ZONES_JSON:-$ROOT/zones/colonial_north.json}"

EXTRA=()
[ -n "$VEH_WEIGHTS" ] && EXTRA+=(--veh-weights "$VEH_WEIGHTS")
if [ -f "$ZONES_JSON" ]; then EXTRA+=(--zones-json "$ZONES_JSON"); else echo "NOTE: no zones file ($ZONES_JSON) -> bike-lane/sidewalk split will be 'unassigned'"; fi

echo "chunk=$N run=$RUN video=$VIDEO"
python "$ROOT/code/xclip_overlay_v11_colonial.py" \
    --video "$VIDEO" \
    --out-root "$ROOT" \
    --run "$RUN" \
    --session-start "$SESSION_START" \
    --weights "$WEIGHTS" \
    --start-frame "$START_FRAME" \
    --max-frames "$MAX_FRAMES" \
    --imgsz "$IMGSZ" \
    --det-conf "$DET_CONF" \
    ${EXTRA[@]+"${EXTRA[@]}"}
