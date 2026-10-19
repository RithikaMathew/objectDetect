#!/bin/bash
#SBATCH --job-name=colonial_v15
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --gpus=1
#SBATCH --mem=32gb
#SBATCH --time=04:00:00
#SBATCH --output=logs/slurm_%x_%A_%a.log

# xclip_overlay_v15_colonial.py : fine-tuned RT-DETR + X-CLIP, one hourly chunk per array task.
# Array task id = chunk number N (.001 = 2019-07-10 00:00, .025 = 2019-07-11 00:00).
#
# Run from the test_colonial folder so that logs/ resolves:
#   cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
#   sbatch --export=ALL,RUN=colonial_run1 --array=8     code/run_xclip_colonial_v15.slurm   # test: 07:00-08:00
#   sbatch --export=ALL,RUN=colonial_run2 --array=1-24  code/run_xclip_colonial_v15.slurm   # block 1 (07-10)
#   sbatch --export=ALL,RUN=colonial_run3 --array=25-48 code/run_xclip_colonial_v15.slurm   # block 2 (07-11)
# Quick smoke test (first 2 minutes only):  --export=ALL,RUN=smoke1,MAX_FRAMES=3600 --array=8
# Clips stream by default (STREAM_CLIPS=0 to turn off). Streamed headers say "(prov.)": counts decided with the tracks seen so far.
# Zones: pass ZONES_JSON=$ROOT/zones/colonial_north_v1.json in --export once you have approved the preview.
# Optional filters (all default OFF): PERSON_MIN_CONF=0.45  PERSON_MIN_DISP=60  DET_CONF=0.15
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
PERSON_MIN_CONF="${PERSON_MIN_CONF:-0}"     # min MEAN detector conf of a person track (0 = off); cones sat at ~0.3, real people at 0.58-0.67
PED_MIN_SEC="${PED_MIN_SEC:-3}"               # min seconds visible to count a PEDESTRIAN (offline sweep on 3 hours suggested ~1.0)
BIC_MIN_SEC="${BIC_MIN_SEC:-3}"               # min seconds visible to count a BICYCLIST (sweep suggested keeping 2-3)
PERSON_MIN_DISP="${PERSON_MIN_DISP:-0}"     # min net movement in px of a person track (0 = off); rejects static cones
START_FRAME="${START_FRAME:-1}"
MAX_FRAMES="${MAX_FRAMES:-0}"
VEH_WEIGHTS="${VEH_WEIGHTS:-}"
# Colonial has its own camera: only use a zones file if you have made one for it.
ZONES_JSON="${ZONES_JSON:-$ROOT/zones/colonial_north.json}"

STREAM_CLIPS="${STREAM_CLIPS:-1}"           # 1 = write each 15-min clip as soon as its bin is over (+10 s); 0 = all clips at the end
EXTRA=()
[ "$STREAM_CLIPS" = "1" ] && EXTRA+=(--stream-clips)
[ -n "$VEH_WEIGHTS" ] && EXTRA+=(--veh-weights "$VEH_WEIGHTS")
if [ -f "$ZONES_JSON" ]; then EXTRA+=(--zones-json "$ZONES_JSON"); else echo "NOTE: no zones file ($ZONES_JSON) -> bike-lane/sidewalk split will be 'unassigned'"; fi

echo "chunk=$N run=$RUN video=$VIDEO"
python "$ROOT/code/xclip_overlay_v15_colonial.py" \
    --video "$VIDEO" \
    --out-root "$ROOT" \
    --run "$RUN" \
    --session-start "$SESSION_START" \
    --weights "$WEIGHTS" \
    --start-frame "$START_FRAME" \
    --max-frames "$MAX_FRAMES" \
    --imgsz "$IMGSZ" \
    --det-conf "$DET_CONF" \
    --person-min-conf "$PERSON_MIN_CONF" \
    --person-min-disp "$PERSON_MIN_DISP" \
    --ped-min-sec "$PED_MIN_SEC" \
    --bic-min-sec "$BIC_MIN_SEC" \
    ${EXTRA[@]+"${EXTRA[@]}"}
