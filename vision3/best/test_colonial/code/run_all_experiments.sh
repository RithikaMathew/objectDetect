#!/bin/bash
# ONE command that submits every experiment on the two test clips, plus an evaluation job that runs when they have all finished.
#
#   cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
#   bash code/run_all_experiments.sh            # first time
#   bash code/run_all_experiments.sh v2         # a later re-run: every run name gets the suffix _v2 (nothing is overwritten)
#
# Clips (video position = clock time minus the clip start):
#   NIGHT  21:15-21:30  chunk 22  frames 26978 .. 53946        DAY  14:00-14:15  chunk 15  frames 1 .. 26973
# Experiments (ONE change each, same clips; exp0 is the control and also checks that v19 with no flags = v18):
#   exp0_base     nothing changed (+ motion diagnostic, which never changes counts)        night + day
#   exp1_sahi     E1 sliced inference (640 px slices, 20% overlap, + full-frame pass)       night + day   (slow: several x baseline)
#   exp2_gamma    E2 brighten night frames with gamma 2.2 before the detector               night only
#   exp2_clahe    E2 local contrast (CLAHE) on night frames                                  night only
#   exp2_zerodce  E2 Zero-DCE low-light enhancement on night frames                          night only
#   exp3a_speed   E3 relabel by speed when the detector agrees against X-CLIP               night + day
#   exp3b_short   E3 count short (>=0.3 s) tracks the detector calls cyclist in >=90% frames  night + day
# Older controls that already exist (no need to rerun): sw_day (= v17 settings) and sw_switch (= v18 night rule) on the same two clips.
set -u
ROOT=/orange/xiangyan/rithika/vision/vision3/best/test_colonial
cd "$ROOT" || { echo "cannot cd to $ROOT"; exit 1; }
SUF=""; [ $# -ge 1 ] && SUF="_$1"
STAMP=$(date +%Y%m%d_%H%M)
SLURM=code/run_xclip_colonial_v19.slurm
Z=$ROOT/zones/colonial_north_v1.json
ZW=$ROOT/code/zerodce/Epoch99.pth

for f in code/xclip_overlay_v19_colonial.py "$SLURM" code/eval_truth.py; do
  [ -f "$f" ] || { echo "ERROR: missing $f (copy the bundle into $ROOT first)"; exit 1; }
done
[ -f "$Z" ] || echo "WARNING: zones file $Z not found (the slurm falls back to its default zones file)"
[ -d "counts/exp0_base$SUF" ] && { echo "ERROR: counts/exp0_base$SUF already exists. Pass a new tag: bash code/run_all_experiments.sh v2"; exit 1; }
mkdir -p exp_results truth logs
for t in night_2115 day_1400; do
  [ -f "truth/${t}_truth.csv" ] || echo "WARNING: truth/${t}_truth.csv is missing (copy it from the bundle). Evaluation needs it."
done
if [ ! -f "$ZW" ]; then
  mkdir -p code/zerodce
  curl -sL -m 60 -o "$ZW" "https://raw.githubusercontent.com/Li-Chongyi/Zero-DCE/master/Zero-DCE_code/snapshots/Epoch99.pth" || true
  [ -s "$ZW" ] || { rm -f "$ZW"; echo "WARNING: no Zero-DCE weights at $ZW -> exp2_zerodce will be skipped (copy Epoch99.pth there and re-run with a tag)"; }
fi

NIGHT="NIGHT_START=21:00,NIGHT_END=06:00"
JOBS=(); RUNS=(); TABLE=""
sub () {   # $1 experiment  $2 clip name  $3 chunk  $4 start frame  $5 stop frame  $6 time limit  $7 extra env (comma separated, may be empty)
  local run="$1$SUF" id
  id=$(sbatch --parsable --time="$6" --job-name="${run}_$2" \
        --export=ALL,RUN="$run",ZONES_JSON="$Z",START_FRAME="$4",MAX_FRAMES="$5"${7:+,$7} --array="$3" "$SLURM") || { echo "sbatch failed for $run $2"; return 1; }
  id=${id%%;*}
  JOBS+=("$id"); case " ${RUNS[*]:-} " in *" $run "*) ;; *) RUNS+=("$run");; esac
  TABLE+="$(printf '%-18s %-6s job %-10s time %s  env: %s' "$run" "$2" "$id" "$6" "${7:-(none)}")"$'\n'
  echo "submitted $run ($2) -> job $id"
}
night () { sub "$1" night 22 26978 53946 "$2" "$3"; }
day   () { sub "$1" day   15 1     26973 "$2" "$3"; }

night exp0_base    02:00:00 "MOTION_DIAG=1";                 day exp0_base    02:00:00 "MOTION_DIAG=1"
night exp1_sahi    04:00:00 "SAHI=1";                        day exp1_sahi    04:00:00 "SAHI=1"
night exp2_gamma   02:00:00 "ENHANCE=gamma,$NIGHT"
night exp2_clahe   02:00:00 "ENHANCE=clahe,$NIGHT"
[ -s "$ZW" ] && night exp2_zerodce 02:00:00 "ENHANCE=zerodce,ZERODCE_WEIGHTS=$ZW,$NIGHT"
night exp3a_speed  02:00:00 "SPEED_RULE=1";                  day exp3a_speed  02:00:00 "SPEED_RULE=1"
night exp3b_short  02:00:00 "SHORT_RULE=1";                  day exp3b_short  02:00:00 "SHORT_RULE=1"

[ ${#JOBS[@]} -gt 0 ] || { echo "nothing was submitted"; exit 1; }
DEP=$(IFS=:; echo "${JOBS[*]}")
RUNLIST=$(IFS=,; echo "${RUNS[*]}")
EVAL_OUT="exp_results/EVAL_${STAMP}${SUF}.md"
EID=$(sbatch --parsable --dependency=afterany:"$DEP" --partition=hpg-turin --account=xiangyan --qos=xiangyan --gpus=1 --mem=4gb --time=00:15:00 \
      --job-name=exp_eval --output="logs/slurm_exp_eval_%j.log" \
      --wrap "cd $ROOT && source /orange/xiangyan/rithika/vision/yolo_env/bin/activate && python code/eval_truth.py --root . --runs $RUNLIST --baseline exp0_base$SUF --out $EVAL_OUT")
EID=${EID%%;*}

MAN="exp_results/MANIFEST_${STAMP}${SUF}.md"
cat > "$MAN" <<MANEOF
# Experiment submission ${STAMP}${SUF}
Submitted from: $ROOT   by: $(whoami)   at: $(date)
Code: code/xclip_overlay_v19_colonial.py  slurm: $SLURM   (control = rtdetr_v3 + v17 settings; see README section 22/23)
Clips: night 21:15-21:30 (chunk 22, frames 26978-53946) and day 14:00-14:15 (chunk 15, frames 1-26973)

## Jobs
$TABLE
Evaluation job: $EID (starts when all of the above end; writes $EVAL_OUT)

## Where everything is (run names: ${RUNLIST})
- annotated clips : annotated/<run>/Standard_SCU8OG_2019-07-10_0000.0NN/*.mp4      (NN = 22 night, 15 day)
- counts + tables : counts/<run>/*_tracks.csv  *_rules_audit.csv  *_track_motion.csv  *_motion_candidates.csv/.png (exp0 only)  *_enhance_preview.png (exp2)
- slurm logs      : logs/slurm_<run>_<clip>_<jobid>_<chunk>.log
- run logs (json) : logs/<run>/*_run_log.json   (all flags + counts + runtime)
- truth files     : truth/night_2115_truth.csv  truth/day_1400_truth.csv   (YOU fill these in; evaluation needs them)
- evaluation      : $EVAL_OUT  (re-create any time:  python code/eval_truth.py --root . --runs $RUNLIST --baseline exp0_base$SUF)

## Monitor
squeue -u \$USER -o "%i %j %T %M"
MANEOF
echo
echo "$TABLE"
echo "evaluation job $EID will run after all of them finish and write $EVAL_OUT"
echo "manifest (for looking back later): $ROOT/$MAN"
echo "NEXT: fill in truth/night_2115_truth.csv and truth/day_1400_truth.csv while the jobs run (nano truth/day_1400_truth.csv)."
