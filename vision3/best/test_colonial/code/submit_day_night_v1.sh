#!/bin/bash
# Day vs night settings test (v18). Run from anywhere:
#   bash code/submit_day_night_v1.sh
# Needs code/xclip_overlay_v18_colonial.py and code/run_xclip_colonial_v18.slurm (new files; v17 untouched).
#
# Two runs on the same 15-minute windows:
#   sw_day    = no night mode: 3 s minimum and detector conf 0.25 everywhere (same as traj17_base)
#   sw_switch = night mode 21:00-06:00 -> detector conf 0.15, bicyclist min 0.4 s, pedestrian min 1.0 s; outside that period the day settings
# Expected: day windows give IDENTICAL counts in both runs (proves day keeps 3 s); the night windows can differ.
# Frames at 29.97 fps: 15 min = 26973 frames. MAX_FRAMES is the STOP frame (0 = to end of the hour file).
ROOT=/orange/xiangyan/rithika/vision/vision3/best/test_colonial
cd "$ROOT" || exit 1
Z=$ROOT/zones/colonial_north_v1.json
COMMON="--time=02:00:00"
NIGHT=",NIGHT_START=21:00,NIGHT_END=06:00,NIGHT_DET_CONF=0.15,NIGHT_BIC_MIN_SEC=0.4,NIGHT_PED_MIN_SEC=1.0"

submit () {  # $1 RUN, $2 extra env (may be empty)
  # day windows
  sbatch $COMMON --export=ALL,RUN=$1,ZONES_JSON=$Z,START_FRAME=1,MAX_FRAMES=26973$2      --array=11 code/run_xclip_colonial_v18.slurm   # 10:00-10:15
  sbatch $COMMON --export=ALL,RUN=$1,ZONES_JSON=$Z,START_FRAME=80924,MAX_FRAMES=0$2       --array=13 code/run_xclip_colonial_v18.slurm   # 12:45-13:00
  sbatch $COMMON --export=ALL,RUN=$1,ZONES_JSON=$Z,START_FRAME=1,MAX_FRAMES=26973$2      --array=15 code/run_xclip_colonial_v18.slurm   # 14:00-14:15 (has the short 'cyclist' tracks at 14:03)
  # night windows
  sbatch $COMMON --export=ALL,RUN=$1,ZONES_JSON=$Z,START_FRAME=26978,MAX_FRAMES=53946$2  --array=22 code/run_xclip_colonial_v18.slurm   # 21:15-21:30 (used to find the settings)
  sbatch $COMMON --export=ALL,RUN=$1,ZONES_JSON=$Z,START_FRAME=1,MAX_FRAMES=26973$2      --array=23 code/run_xclip_colonial_v18.slurm   # 22:00-22:15 (NOT used to pick the settings: the fair test)
}

submit sw_day ""
submit sw_switch "$NIGHT"
