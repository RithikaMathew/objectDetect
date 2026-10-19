#!/bin/bash
# BATCH 3: ONE combined setting, run on the 2 dev clips and the 2 hold-out clips (4 jobs + evaluation).
#   cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
#   bash code/run_batch3.sh            (re-run: bash code/run_batch3.sh v2)
# b3_combo = SAHI (640 px, 20% overlap)
#          + detector veto 15% / promote 90%          (X-CLIP says bicyclist but detector says person almost always -> pedestrian)
#          + short-track rule at NIGHT only           (>= 0.3 s, detector cyclist >= 90%, weighted bicyclist >= 0.9)
#          + speed rule, left/right-moving tracks only, walk < 0.8, ride > 2.0 body heights/s   (best value of the fusion_probe on batch-1/2 data)
# These numbers were chosen on the two dev clips (about 11 people), so the hold-outs (22:00 night, 12:45 day) are the real test.
set -u
ROOT=/orange/xiangyan/rithika/vision/vision3/best/test_colonial
cd "$ROOT" || { echo "cannot cd to $ROOT"; exit 1; }
SUF=""; [ $# -ge 1 ] && SUF="_$1"
SLURM=code/run_xclip_colonial_v19.slurm
Z=$ROOT/zones/colonial_north_v1.json
grep -q "speed-lateral-only" code/xclip_overlay_v19_colonial.py || { echo "ERROR: old code (no --speed-lateral-only)"; exit 1; }
[ -d "counts/b3_combo$SUF" ] && { echo "ERROR: counts/b3_combo$SUF exists; pass a tag: bash code/run_batch3.sh v2"; exit 1; }
RUN="b3_combo$SUF"
ENVV="SAHI=1,DET_VETO_PCT=15,DET_PROMOTE_PCT=90,SHORT_RULE=1,SHORT_RULE_NIGHT_ONLY=1,NIGHT_START=21:00,NIGHT_END=06:00,SPEED_RULE=1,SPEED_LATERAL_ONLY=1,WALK_MAX_SPEED=0.8,RIDE_MIN_SPEED=2.0"
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
RUNS="exp0_base,exp1_sahi,b2_0_base,b2_2_sahi,b2_3_sahi_fuse,b2_4_sahi_fuse_nightshort,b2_5_sahi_speed,$RUN"
EID=$(sbatch --parsable --dependency=afterany:"$DEP" --partition=hpg-turin --account=xiangyan --qos=xiangyan --gpus=1 --mem=4gb --time=00:15:00 \
      --job-name=b3_eval --output="logs/slurm_b3_eval_%j.log" \
      --wrap "cd $ROOT && source /orange/xiangyan/rithika/vision/yolo_env/bin/activate && python code/eval_truth.py --root . --runs $RUNS --baseline exp0_base --out exp_results/EVAL_batch3_${STAMP}${SUF}.md && python code/fusion_probe.py --root . --runs $RUNS --out exp_results/FUSION_batch3_${STAMP}${SUF}.md && python code/collect_clips.py --root . --prefix b3_")
echo "evaluation job ${EID%%;*} -> exp_results/EVAL_batch3_${STAMP}${SUF}.md and FUSION_batch3_${STAMP}${SUF}.md (hold-out truth files must be filled in before this finishes, or re-run the two python commands by hand)"
