#!/bin/bash
# BATCH 4: b3_combo + static-OBJECT filter (--static-filter: net movement < 5 px AND path speed < 0.05 body heights/s, track >= 3 s). 4 jobs + evaluation.
# Promote is left OFF (it never helped). A person who waits and then crosses has a large net movement, and a person who stands still still sways (real standing people: 0.15-0.18 h/s), so both stay.
#   cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
#   bash code/run_batch4.sh            (net cutoff 5 px; change with:  NETPX=8 bash code/run_batch4.sh)
set -u
ROOT=/orange/xiangyan/rithika/vision/vision3/best/test_colonial
cd "$ROOT" || { echo "cannot cd to $ROOT"; exit 1; }
NETPX="${NETPX:-5}"
SUF=""; [ $# -ge 1 ] && SUF="_$1"
SLURM=code/run_xclip_colonial_v19.slurm
Z=$ROOT/zones/colonial_north_v1.json
RUN="b4_combo_static${NETPX}$SUF"
[ -d "counts/$RUN" ] && { echo "ERROR: counts/$RUN exists; pass a tag: bash code/run_batch4.sh v2"; exit 1; }
ENVV="SAHI=1,DET_VETO_PCT=15,SHORT_RULE=1,SHORT_RULE_NIGHT_ONLY=1,NIGHT_START=21:00,NIGHT_END=06:00,SPEED_RULE=1,SPEED_LATERAL_ONLY=1,WALK_MAX_SPEED=0.8,RIDE_MIN_SPEED=2.0,STATIC_FILTER=1,STATIC_MAX_NET_PX=$NETPX,STATIC_MAX_SPEED=0.05"
JOBS=()
sub () {
  local id
  id=$(sbatch --parsable --time=04:00:00 --job-name="${RUN}_$1" --export=ALL,RUN="$RUN",ZONES_JSON="$Z",START_FRAME="$3",MAX_FRAMES="$4",$ENVV --array="$2" "$SLURM") || { echo "sbatch failed: $1"; return 1; }
  id=${id%%;*}; JOBS+=("$id"); echo "submitted $RUN ($1) -> job $id"
}
sub night_2115 22 26978 53946
sub day_1400   15 1     26973
sub night_2200 23 1     26973
sub day_1245   13 80924 0
DEP=$(IFS=:; echo "${JOBS[*]}")
STAMP=$(date +%Y%m%d_%H%M)
RUNS="exp0_base,b2_2_sahi,b3_combo,$RUN"
EID=$(sbatch --parsable --dependency=afterany:"$DEP" --partition=hpg-turin --account=xiangyan --qos=xiangyan --gpus=1 --mem=4gb --time=00:15:00 \
      --job-name=b4_eval --output="logs/slurm_b4_eval_%j.log" \
      --wrap "cd $ROOT && source /orange/xiangyan/rithika/vision/yolo_env/bin/activate && python code/eval_truth.py --root . --runs $RUNS --baseline exp0_base --out exp_results/EVAL_batch4_${STAMP}.md && python code/fusion_probe.py --root . --runs $RUNS --out exp_results/FUSION_batch4_${STAMP}.md && python code/collect_clips.py --root . --prefix b4_")
echo "evaluation job ${EID%%;*} -> exp_results/EVAL_batch4_${STAMP}.md"
