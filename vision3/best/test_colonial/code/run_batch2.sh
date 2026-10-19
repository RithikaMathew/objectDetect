#!/bin/bash
# BATCH 2: combine what helped in batch 1 and test it on clips that were NOT used to choose the settings.
#   cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
#   bash code/run_batch2.sh            (a re-run: bash code/run_batch2.sh v2)
# Clips: dev night 21:15-21:30 (chunk 22), dev day 14:00-14:15 (chunk 15), HOLD-OUT night 22:00-22:15 (chunk 23), HOLD-OUT day 12:45-13:00 (chunk 13)
# Runs (all names start with b2_, every clip name carries the test it covers):
#   b2_0_base         control on the two hold-out clips (the dev clips already have exp0_base)
#   b2_2_sahi         SAHI alone on the two hold-out clips (dev clips already have exp1_sahi)
#   b2_1_fuse         detector veto (<15% cyclist frames -> pedestrian) + promote (>=90% -> cyclist), no SAHI     all 4 clips
#   b2_3_sahi_fuse    SAHI + veto + promote                                                                       all 4 clips
#   b2_4_sahi_fuse_nightshort   SAHI + veto + promote + short-track rule at NIGHT only                            all 4 clips
#   b2_6_night04      flat night minimums (bicyclist 0.4 s, pedestrian 1.0 s) at night only, no SAHI           NIGHT clips only
#   b2_7_sahi_fuse_night04   SAHI + veto + promote + the flat night minimums                              NIGHT clips only
#   b2_5_sahi_speed   SAHI + speed rule for left/right-moving tracks only (thresholds in SPEEDENV below)           all 4 clips
set -u
ROOT=/orange/xiangyan/rithika/vision/vision3/best/test_colonial
cd "$ROOT" || { echo "cannot cd to $ROOT"; exit 1; }
SUF=""; [ $# -ge 1 ] && SUF="_$1"
STAMP=$(date +%Y%m%d_%H%M)
SLURM=code/run_xclip_colonial_v19.slurm
Z=$ROOT/zones/colonial_north_v1.json
for f in code/xclip_overlay_v19_colonial.py "$SLURM" code/eval_truth.py; do [ -f "$f" ] || { echo "ERROR: missing $f"; exit 1; }; done
grep -q "speed-lateral-only" code/xclip_overlay_v19_colonial.py && grep -q "short-rule-night-only" code/xclip_overlay_v19_colonial.py || { echo "ERROR: code/xclip_overlay_v19_colonial.py is the OLD version (no --short-rule-night-only / --speed-lateral-only). Copy the updated one."; exit 1; }
[ -d "counts/b2_0_base$SUF" ] && { echo "ERROR: counts/b2_0_base$SUF exists. Pass a new tag: bash code/run_batch2.sh v2"; exit 1; }
mkdir -p exp_results truth logs
for t in night_2115 day_1400 night_2200 day_1245; do [ -f "truth/${t}_truth.csv" ] || echo "WARNING: truth/${t}_truth.csv missing"; done

NIGHT="NIGHT_START=21:00,NIGHT_END=06:00"
FUSE="DET_VETO_PCT=15,DET_PROMOTE_PCT=90"
# speed rule: only tracks moving left/right (toward/away motion looks slow in the image). Change the numbers after reading fusion_probe.py output.
SPEEDENV="SPEED_RULE=1,SPEED_LATERAL_ONLY=1,WALK_MAX_SPEED=1.0,RIDE_MIN_SPEED=2.0"
JOBS=(); RUNS=(); TABLE=""
sub () {   # $1 run  $2 clip  $3 chunk  $4 start  $5 stop  $6 time  $7 extra env
  local run="$1$SUF" id
  id=$(sbatch --parsable --time="$6" --job-name="${run}_$2" \
        --export=ALL,RUN="$run",ZONES_JSON="$Z",START_FRAME="$4",MAX_FRAMES="$5"${7:+,$7} --array="$3" "$SLURM") || { echo "sbatch failed: $run $2"; return 1; }
  id=${id%%;*}; JOBS+=("$id"); case " ${RUNS[*]:-} " in *" $run "*) ;; *) RUNS+=("$run");; esac
  TABLE+="$(printf '%-30s %-14s job %-10s env: %s' "$run" "$2" "$id" "${7:-(none)}")"$'\n'
  echo "submitted $run ($2) -> job $id"
}
devnight () { sub "$1" night_2115 22 26978 53946 "$2" "$3"; }
devday   () { sub "$1" day_1400   15 1     26973 "$2" "$3"; }
hoNight  () { sub "$1" night_2200 23 1     26973 "$2" "$3"; }
hoDay    () { sub "$1" day_1245   13 80924 0     "$2" "$3"; }
all4 () { devnight "$1" "$2" "$3"; devday "$1" "$2" "$3"; hoNight "$1" "$2" "$3"; hoDay "$1" "$2" "$3"; }

hoNight b2_0_base 02:00:00 "";                   hoDay b2_0_base 02:00:00 ""
hoNight b2_2_sahi 04:00:00 "SAHI=1";             hoDay b2_2_sahi 04:00:00 "SAHI=1"
all4 b2_1_fuse 02:00:00 "$FUSE"
all4 b2_3_sahi_fuse 04:00:00 "SAHI=1,$FUSE"
all4 b2_4_sahi_fuse_nightshort 04:00:00 "SAHI=1,$FUSE,SHORT_RULE=1,SHORT_RULE_NIGHT_ONLY=1,$NIGHT"
all4 b2_5_sahi_speed 04:00:00 "SAHI=1,$SPEEDENV"
NIGHT04="$NIGHT,NIGHT_BIC_MIN_SEC=0.4,NIGHT_PED_MIN_SEC=1.0"
devnight b2_6_night04 02:00:00 "$NIGHT04";                       hoNight b2_6_night04 02:00:00 "$NIGHT04"
devnight b2_7_sahi_fuse_night04 04:00:00 "SAHI=1,$FUSE,$NIGHT04"; hoNight b2_7_sahi_fuse_night04 04:00:00 "SAHI=1,$FUSE,$NIGHT04"

[ ${#JOBS[@]} -gt 0 ] || { echo "nothing submitted"; exit 1; }
DEP=$(IFS=:; echo "${JOBS[*]}")
# evaluation compares the new runs with the batch-1 runs on the same clips
EVALRUNS="exp0_base,exp1_sahi,$(IFS=,; echo "${RUNS[*]}")"
EVAL_OUT="exp_results/EVAL_batch2_${STAMP}${SUF}.md"
EID=$(sbatch --parsable --dependency=afterany:"$DEP" --partition=hpg-turin --account=xiangyan --qos=xiangyan --gpus=1 --mem=4gb --time=00:15:00 \
      --job-name=b2_eval --output="logs/slurm_b2_eval_%j.log" \
      --wrap "cd $ROOT && source /orange/xiangyan/rithika/vision/yolo_env/bin/activate && python code/eval_truth.py --root . --runs $EVALRUNS --baseline exp0_base --out $EVAL_OUT && python code/collect_clips.py --root . --prefix b2_")
EID=${EID%%;*}
MAN="exp_results/MANIFEST_batch2_${STAMP}${SUF}.md"
cat > "$MAN" <<MANEOF
# Batch 2 submission ${STAMP}${SUF}
Submitted: $(date)   by $(whoami)   code: code/xclip_overlay_v19_colonial.py (updated: --det-veto-pct --det-promote-pct --short-rule-night-only)
Clips: dev night 21:15-21:30 (chunk 22) | dev day 14:00-14:15 (chunk 15) | HOLD-OUT night 22:00-22:15 (chunk 23) | HOLD-OUT day 12:45-13:00 (chunk 13)
Settings: speed rule lateral-only (walk<1.0, ride>2.0 body heights/s) in b2_5; veto=15 (X-CLIP bicyclist but detector cyclist in <15% of frames -> pedestrian), promote=90, SAHI 640/0.2, short rule 0.3 s / 90% / 0.9 at night only
## Jobs
$TABLE
Evaluation job: $EID  -> $EVAL_OUT  (also puts clips with explicit names into exp_results/clips/)
## Where
annotated clips: annotated/<run>/*/<run>__<day|night>_<HHMM>-<HHMM>__<test>__<date>.mp4  (and copies in exp_results/clips/)
counts: counts/<run>/*_tracks.csv *_rules_audit.csv ; slurm logs: logs/slurm_<run>_<clip>_*.log
truth: truth/night_2115_truth.csv truth/day_1400_truth.csv truth/night_2200_truth.csv truth/day_1245_truth.csv  (hold-out files must be filled in BEFORE judging)
Re-score any time:  python code/eval_truth.py --root . --runs $EVALRUNS --baseline exp0_base
MANEOF
echo; echo "$TABLE"; echo "evaluation job $EID -> $EVAL_OUT"; echo "manifest: $ROOT/$MAN"
echo "NEXT: fill in truth/night_2200_truth.csv and truth/day_1245_truth.csv, and fix rows n5/n6 in truth/night_2115_truth.csv"
