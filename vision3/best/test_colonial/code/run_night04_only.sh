#!/bin/bash
# Submits ONLY the two runs that the first version of run_batch2.sh did not have (flat night minimums 0.4 s / 1.0 s), on the two NIGHT clips.
#   cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
#   bash code/run_night04_only.sh
# Works with the code you already have (it only sets NIGHT_BIC_MIN_SEC / NIGHT_PED_MIN_SEC, which exist since v18).
set -u
ROOT=/orange/xiangyan/rithika/vision/vision3/best/test_colonial
cd "$ROOT" || { echo "cannot cd to $ROOT"; exit 1; }
SLURM=code/run_xclip_colonial_v19.slurm
Z=$ROOT/zones/colonial_north_v1.json
[ -f "$SLURM" ] || { echo "ERROR: missing $SLURM"; exit 1; }
[ -d counts/b2_6_night04 ] && { echo "ERROR: counts/b2_6_night04 already exists"; exit 1; }
NIGHT04="NIGHT_START=21:00,NIGHT_END=06:00,NIGHT_BIC_MIN_SEC=0.4,NIGHT_PED_MIN_SEC=1.0"
FUSE="DET_VETO_PCT=15,DET_PROMOTE_PCT=90"
JOBS=()
sub () {   # run clipname chunk start stop time extra
  local id
  id=$(sbatch --parsable --time="$6" --job-name="$1_$2" --export=ALL,RUN="$1",ZONES_JSON="$Z",START_FRAME="$4",MAX_FRAMES="$5",$7 --array="$3" "$SLURM") || { echo "sbatch failed: $1 $2"; return 1; }
  id=${id%%;*}; JOBS+=("$id"); echo "submitted $1 ($2) -> job $id"
}
sub b2_6_night04 night_2115 22 26978 53946 02:00:00 "$NIGHT04"
sub b2_6_night04 night_2200 23 1     26973 02:00:00 "$NIGHT04"
sub b2_7_sahi_fuse_night04 night_2115 22 26978 53946 04:00:00 "SAHI=1,$FUSE,$NIGHT04"
sub b2_7_sahi_fuse_night04 night_2200 23 1     26973 04:00:00 "SAHI=1,$FUSE,$NIGHT04"
DEP=$(IFS=:; echo "${JOBS[*]}")
STAMP=$(date +%Y%m%d_%H%M)
RUNS="exp0_base,exp1_sahi,b2_0_base,b2_2_sahi,b2_1_fuse,b2_3_sahi_fuse,b2_4_sahi_fuse_nightshort,b2_5_sahi_speed,b2_6_night04,b2_7_sahi_fuse_night04"
EID=$(sbatch --parsable --dependency=afterany:"$DEP" --partition=hpg-turin --account=xiangyan --qos=xiangyan --gpus=1 --mem=4gb --time=00:15:00 \
      --job-name=b2n_eval --output="logs/slurm_b2n_eval_%j.log" \
      --wrap "cd $ROOT && source /orange/xiangyan/rithika/vision/yolo_env/bin/activate && python code/eval_truth.py --root . --runs $RUNS --baseline exp0_base --out exp_results/EVAL_batch2_all_${STAMP}.md && python code/collect_clips.py --root . --prefix b2_")
echo "evaluation job ${EID%%;*} -> exp_results/EVAL_batch2_all_${STAMP}.md (after these 4 jobs; it scores ALL batch-2 runs together)"
