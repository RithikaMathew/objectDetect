#!/bin/bash
#SBATCH --job-name=colonial_v19
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --gpus=1
#SBATCH --mem=32gb
#SBATCH --time=04:00:00
#SBATCH --output=logs/slurm_%x_%A_%a.log

# xclip_overlay_v19_colonial.py : fine-tuned RT-DETR + X-CLIP, one hourly chunk per array task (v19 = v18 + experiment switches E1-E3).
# v19 experiment env vars (all unset = identical to v18/v17):
#   SAHI=1 [SAHI_SLICE=640 SAHI_OVERLAP=0.2 SAHI_IOS=0.6 SAHI_ROI=x1,y1,x2,y2]       E1 sliced inference
#   ENHANCE=gamma|clahe|zerodce [ENHANCE_WHEN=night|always GAMMA=2.2 CLAHE_CLIP=3 ZERODCE_WEIGHTS=... ENHANCE_CROPS=1]   E2 (needs NIGHT_START/NIGHT_END for 'night')
#   SPEED_RULE=1 [WALK_MAX_SPEED=1.0 RIDE_MIN_SPEED=2.0 SPEED_MIN_SEC=1.5]           E3 relabel by speed when the detector agrees
#   SHORT_RULE=1 [SHORT_MIN_SEC=0.3 SHORT_DET_PCT=90 SHORT_WBIC=0.9]                 E3 count short, detector-sure cyclist tracks
#   SHORT_RULE_NIGHT_ONLY=1 (with SHORT_RULE=1, needs NIGHT_START/NIGHT_END)   DET_VETO_PCT=15  DET_PROMOTE_PCT=90  [DET_FUSE_MIN_FRAMES=20]   detector veto/promote
#   MOTION_DIAG=1                                                                    E3 diagnostic only (no change to counts)
# NEW optional env vars (all unset = identical to v17): NIGHT_START=21:00 NIGHT_END=06:00 (clock time, may cross midnight)
#   NIGHT_DET_CONF  NIGHT_BIC_MIN_SEC  NIGHT_PED_MIN_SEC  -> used only inside the night period; day keeps DET_CONF / BIC_MIN_SEC / PED_MIN_SEC.
# New optional env vars (defaults = the script's own defaults, so counts are identical to v16 unless you change them):
#   TRACK_THR (ByteTrack activation conf)  LOST_SEC (track buffer, s)  STITCH_SEC / STITCH_PX (id stitcher)  TRAIL_SEC  SPLIT_GAP_SEC  SPLIT_PX
# Test only part of the hour: START_FRAME=<first frame>  MAX_FRAMES=<STOP frame, not a count>  (see submit_traj_tests_v1.sh)
# Array task id = chunk number N (.001 = 2019-07-10 00:00, .025 = 2019-07-11 00:00).
#
# Run from the test_colonial folder so that logs/ resolves:
#   cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
#   sbatch --export=ALL,RUN=colonial_run1 --array=8     code/run_xclip_colonial_v16.slurm   # test: 07:00-08:00
#   sbatch --export=ALL,RUN=colonial_run2 --array=1-24  code/run_xclip_colonial_v16.slurm   # block 1 (07-10)
#   sbatch --export=ALL,RUN=colonial_run3 --array=25-48 code/run_xclip_colonial_v16.slurm   # block 2 (07-11)
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
# NEW VIDEO: VIDEO_OVERRIDE=/full/path.mp4 (use --array=1 and SESSION_START="YYYY-MM-DD HH:MM:SS" = the clock time at the first frame; the ground-truth file is switched off)
[ -n "${VIDEO_OVERRIDE:-}" ] && VIDEO="$VIDEO_OVERRIDE"
[ -f "$VIDEO" ] || { echo "ERROR: missing $VIDEO"; exit 1; }

WEIGHTS="${WEIGHTS:-/orange/xiangyan/rithika/vision/vision3/runs/detect/finetune_runs/rtdetr_v3/weights/best.pt}"
SESSION_START="${SESSION_START:-2019-07-10 00:00:00}"
SESSION_START="${SESSION_START//_/ }"      # run_new_video.sh passes it with an underscore (sbatch --export dislikes spaces)
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

TRACK_THR="${TRACK_THR:-0.25}"; LOST_SEC="${LOST_SEC:-3.0}"; STITCH_SEC="${STITCH_SEC:-5.0}"; STITCH_PX="${STITCH_PX:-150.0}"
TRAIL_SEC="${TRAIL_SEC:-5.0}"; SPLIT_GAP_SEC="${SPLIT_GAP_SEC:-8.0}"; SPLIT_PX="${SPLIT_PX:-120.0}"

STREAM_CLIPS="${STREAM_CLIPS:-1}"           # 1 = write each 15-min clip as soon as its bin is over (+10 s); 0 = all clips at the end
GT_XLS="${GT_XLS:-$ROOT/ground_truth/Colonial_North_676806_07-10-2019.xls}"   # ground truth shown in the clip headers
EXTRA=()
[ -n "${CLOCK_NOTE:-}" ] && EXTRA+=(--clock-note "$CLOCK_NOTE")
[ "${TTA:-0}" = "1" ] && EXTRA+=(--tta --tta-sizes 960 1280)
NIGHT_START="${NIGHT_START:-}"; NIGHT_END="${NIGHT_END:-}"
if [ -n "$NIGHT_START" ]; then
  EXTRA+=(--night-start "$NIGHT_START" --night-end "${NIGHT_END:?set NIGHT_END with NIGHT_START}")
  [ -n "${NIGHT_DET_CONF:-}" ]     && EXTRA+=(--night-det-conf "$NIGHT_DET_CONF")
  [ -n "${NIGHT_BIC_MIN_SEC:-}" ]  && EXTRA+=(--night-bic-min-sec "$NIGHT_BIC_MIN_SEC")
  [ -n "${NIGHT_PED_MIN_SEC:-}" ]  && EXTRA+=(--night-ped-min-sec "$NIGHT_PED_MIN_SEC")
fi
if [ "${SAHI:-0}" = "1" ]; then
  EXTRA+=(--sahi --sahi-slice "${SAHI_SLICE:-640}" --sahi-overlap "${SAHI_OVERLAP:-0.2}" --sahi-ios "${SAHI_IOS:-0.6}")
  [ -n "${SAHI_ROI:-}" ] && EXTRA+=(--sahi-roi "$SAHI_ROI")
fi
if [ "${ENHANCE:-none}" != "none" ]; then
  EXTRA+=(--enhance "$ENHANCE" --enhance-when "${ENHANCE_WHEN:-night}" --gamma "${GAMMA:-2.2}" --clahe-clip "${CLAHE_CLIP:-3.0}")
  [ -n "${ZERODCE_WEIGHTS:-}" ] && EXTRA+=(--zerodce-weights "$ZERODCE_WEIGHTS")
  [ "${ENHANCE_CROPS:-0}" = "1" ] && EXTRA+=(--enhance-crops)
fi
[ "${SPEED_LATERAL_ONLY:-0}" = "1" ] && EXTRA+=(--speed-lateral-only)
[ "${SPEED_RULE:-0}" = "1" ] && EXTRA+=(--speed-rule --walk-max-speed "${WALK_MAX_SPEED:-1.0}" --ride-min-speed "${RIDE_MIN_SPEED:-2.0}" --speed-min-sec "${SPEED_MIN_SEC:-1.5}")
[ "${SHORT_RULE:-0}" = "1" ] && EXTRA+=(--short-rule --short-min-sec "${SHORT_MIN_SEC:-0.3}" --short-det-pct "${SHORT_DET_PCT:-90}" --short-wbic "${SHORT_WBIC:-0.9}")
[ "${STATIC_FILTER:-0}" = "1" ] && EXTRA+=(--static-filter --static-max-net-px "${STATIC_MAX_NET_PX:-5}" --static-max-speed "${STATIC_MAX_SPEED:-0.05}" --static-min-sec "${STATIC_MIN_SEC:-3}")
[ "${MOTION_DIAG:-0}" = "1" ] && EXTRA+=(--motion-diag)
[ "${SHORT_RULE_NIGHT_ONLY:-0}" = "1" ] && EXTRA+=(--short-rule-night-only)
[ -n "${DET_VETO_PCT:-}" ] && EXTRA+=(--det-veto-pct "$DET_VETO_PCT")
[ -n "${DET_PROMOTE_PCT:-}" ] && EXTRA+=(--det-promote-pct "$DET_PROMOTE_PCT")
[ -n "${DET_FUSE_MIN_FRAMES:-}" ] && EXTRA+=(--det-fuse-min-frames "$DET_FUSE_MIN_FRAMES")
[ -n "${VIDEO_OVERRIDE:-}" ] && { GT_XLS=none; EXTRA+=(--chunk-index "$CHUNK"); }
[ -f "$GT_XLS" ] && EXTRA+=(--gt-xls "$GT_XLS")
[ "$STREAM_CLIPS" = "1" ] && EXTRA+=(--stream-clips)
[ -n "$VEH_WEIGHTS" ] && EXTRA+=(--veh-weights "$VEH_WEIGHTS")
if [ -f "$ZONES_JSON" ]; then EXTRA+=(--zones-json "$ZONES_JSON"); else echo "NOTE: no zones file ($ZONES_JSON) -> bike-lane/sidewalk split will be 'unassigned'"; fi

echo "chunk=$N run=$RUN video=$VIDEO"
python "$ROOT/code/xclip_overlay_v19_colonial.py" \
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
    --track-thr "$TRACK_THR" \
    --lost-sec "$LOST_SEC" \
    --stitch-sec "$STITCH_SEC" \
    --stitch-px "$STITCH_PX" \
    --trail-sec "$TRAIL_SEC" \
    --split-gap-sec "$SPLIT_GAP_SEC" \
    --split-px "$SPLIT_PX" \
    ${EXTRA[@]+"${EXTRA[@]}"}
