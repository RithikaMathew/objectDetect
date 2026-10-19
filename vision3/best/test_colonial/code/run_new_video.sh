#!/bin/bash
# Run the pipeline on ONE new video (e.g. a 15-minute clip from 2025 with better resolution): the control and the best configuration so far.
#   cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
#   python code/probe_video.py "/path/to/new_video.mp4"            # size, fps, length, and the ffmpeg cut command
#   VIDEO="/path/to/clip_15min.mp4" START="2025-03-12 14:20:00" bash code/run_new_video.sh
# Optional:  ZONES=zones/colonial_north_v2.json   (a zones file drawn ON THE NEW VIDEO's frame; none = no zone filtering)
#            SLICE=640   (SAHI slice size in pixels; for a much larger frame try 960)   TAG=name   (default: today's date)
#            STATIC_NET=5  (static-object filter, in PIXELS: it was set on the old video; multiply by new width / old width, e.g. 10 for twice the width)
#            STIT_PX / pixel settings in the slurm were also set for the old resolution (STITCH_PX=150, SPLIT_PX=120): scale them the same way
# START is the real clock time of the first frame (the night rules use it: 21:00-06:00 counts as night). No truth file is needed to run it;
# the human counts shown in the clip header are switched off for new videos.
set -u
ROOT=/orange/xiangyan/rithika/vision/vision3/best/test_colonial
cd "$ROOT" || { echo "cannot cd to $ROOT"; exit 1; }
VIDEO="${VIDEO:?set VIDEO=/full/path/to/clip.mp4}"
START="${START:?set START=\"YYYY-MM-DD HH:MM:SS\" (clock time of the first frame)}"
[ -f "$VIDEO" ] || { echo "ERROR: cannot find $VIDEO"; exit 1; }
TAG="${TAG:-$(date +%Y%m%d)}"
SLICE="${SLICE:-640}"
STATIC_NET="${STATIC_NET:-5}"
SLURM=code/run_xclip_colonial_v19.slurm
ZONES_ENV=""; [ -n "${ZONES:-}" ] && { [ -f "$ZONES" ] || { echo "ERROR: zones file $ZONES not found"; exit 1; }; ZONES_ENV="$ROOT/$ZONES"; case "$ZONES" in /*) ZONES_ENV="$ZONES";; esac; }
for r in "nv_base_$TAG" "nv_combo_$TAG"; do [ -d "counts/$r" ] && { echo "ERROR: counts/$r exists; use TAG=other"; exit 1; }; done
mkdir -p logs
COMMON="VIDEO_OVERRIDE=$VIDEO,SESSION_START=${START// /_}"
[ -n "$ZONES_ENV" ] && COMMON="$COMMON,ZONES_JSON=$ZONES_ENV" || COMMON="$COMMON,ZONES_JSON=/nonexistent_zones.json"
NIGHT="NIGHT_START=21:00,NIGHT_END=06:00"
COMBO="SAHI=1,SAHI_SLICE=$SLICE,DET_VETO_PCT=15,SHORT_RULE=1,SHORT_RULE_NIGHT_ONLY=1,$NIGHT,SPEED_RULE=1,SPEED_LATERAL_ONLY=1,WALK_MAX_SPEED=0.8,RIDE_MIN_SPEED=2.0,STATIC_FILTER=1,STATIC_MAX_NET_PX=$STATIC_NET,STATIC_MAX_SPEED=0.05"
J1=$(sbatch --parsable --time=04:00:00 --job-name="nv_base_$TAG" --export=ALL,RUN="nv_base_$TAG",$COMMON --array=1 "$SLURM") || exit 1
J2=$(sbatch --parsable --time=06:00:00 --job-name="nv_combo_$TAG" --export=ALL,RUN="nv_combo_$TAG",$COMMON,$COMBO --array=1 "$SLURM") || exit 1
echo "submitted nv_base_$TAG -> job ${J1%%;*}   (control: defaults)"
echo "submitted nv_combo_$TAG -> job ${J2%%;*}  (SAHI $SLICE + veto 15 + night short rule + lateral speed rule + static filter)"
echo "clips (when done): annotated/nv_base_$TAG/*/  annotated/nv_combo_$TAG/*/   counts: counts/nv_*_$TAG/*_tracks.csv"
echo "watch:  squeue -u \$USER -o \"%i %j %T %M\""
