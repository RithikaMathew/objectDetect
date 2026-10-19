#!/bin/bash
# Submit the three 15-minute test windows with v17. Run from the test_colonial folder:
#   cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial && bash code/submit_traj_tests_v1.sh
# Needs code/xclip_overlay_v17_colonial.py and code/run_xclip_colonial_v17.slurm (new files, v16 untouched).
# Frame numbers at 29.97 fps: 900 s = 26973 frames. START_FRAME has +5 frames of margin so the first frame lands inside the bin.
# MAX_FRAMES is the STOP frame (not a count); 0 = until the end of the hour file.
ROOT=/orange/xiangyan/rithika/vision/vision3/best/test_colonial
cd "$ROOT" || exit 1
Z=$ROOT/zones/colonial_north_v1.json
COMMON="--time=02:00:00"

submit () {  # $1 = RUN name, $2 = extra env (may be empty)
  # chunk 011: 10:00-10:15 (day, cyclists + pedestrians)
  sbatch $COMMON --export=ALL,RUN=$1,ZONES_JSON=$Z,START_FRAME=1,MAX_FRAMES=26973$2     --array=11 code/run_xclip_colonial_v17.slurm
  # chunk 013: 12:45-13:00 (day; 12:45 bin over-counts 4 vs 2 in earlier runs)
  sbatch $COMMON --export=ALL,RUN=$1,ZONES_JSON=$Z,START_FRAME=80924,MAX_FRAMES=0$2      --array=13 code/run_xclip_colonial_v17.slurm
  # chunk 022: 21:15-21:30 (night)
  sbatch $COMMON --export=ALL,RUN=$1,ZONES_JSON=$Z,START_FRAME=26978,MAX_FRAMES=53946$2  --array=22 code/run_xclip_colonial_v17.slurm
}

# A: same settings as run4 (baseline). Counts should match the old runs up to edge effects of starting mid-hour.
submit traj17_base ""

# B: let ByteTrack use its low-confidence second pass (detector 0.10, activation 0.30) and keep lost tracks longer.
submit traj17_lowconf ",DET_CONF=0.10,TRACK_THR=0.30,LOST_SEC=5.0,STITCH_SEC=8.0,STITCH_PX=200"
