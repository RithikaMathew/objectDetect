#!/bin/bash
# Tidy /orange/xiangyan/rithika/vision.
#
# DRY RUN BY DEFAULT. Prints what it would do and changes nothing. Re-run with
# --apply once the plan looks right.
#
#   ./organize_repo.sh            # show the plan
#   ./organize_repo.sh --apply    # do it
#
# DESIGN CHOICE: active code and .slurm files STAY AT THE TOP LEVEL. It would
# look tidier in src/ and slurm/, but every .slurm script, the
# `from vru_tracker import ...` in pilot_detect_v2.py, and every command in
# HIPERGATOR_COMMANDS.md assume the flat layout. Moving them mid-project buys
# cosmetics and costs a day of debugging paths. Only logs, superseded files and
# junk get moved.
#
# NEVER TOUCHED: MioVision_Data.zip (the irreplaceable source), yolo_env/,
# *.pt weights, pilot_clips/, pilot_output/, dataset_frames/, site_samples/,
# "Bike Lane Study Counts"/.

set -u
cd /orange/xiangyan/rithika/vision || exit 1

APPLY=0
[ "${1:-}" = "--apply" ] && APPLY=1

run() {
    if [ "$APPLY" = "1" ]; then
        eval "$@"
    else
        echo "    would: $*"
    fi
}

count() { ls -1 $1 2>/dev/null | wc -l | tr -d ' '; }
size()  { du -sh $1 2>/dev/null | cut -f1; }

echo "======================================================================"
if [ "$APPLY" = "1" ]; then
    echo "APPLYING CHANGES"
else
    echo "DRY RUN -- nothing will change. Re-run with --apply to execute."
fi
echo "======================================================================"
echo "files at top level now: $(ls -1 | wc -l | tr -d ' ')"
echo

# ----------------------------------------------------------------------
echo "1. ARCHIVE COMPLETED JOB LOGS  ->  logs/"
echo "   Kept, not deleted: these are the run record for the methods section."
echo "   pilot_detect_41807016.log stays at top level -- METHODOLOGY.md cites it"
echo "   by name as the evidence for the tracker diagnosis."
run "mkdir -p logs/site_count logs/render_clips logs/window logs/misc"
for pat in "site_count_*.log:logs/site_count" \
           "render_clips_*.log:logs/render_clips" \
           "v2_window_*.log:logs/window" \
           "v2_full_*.log:logs/window" \
           "ablation_*.log:logs/misc" \
           "extract_sess_*.log:logs/misc"; do
    g="${pat%%:*}"; d="${pat##*:}"
    n=$(count "$g")
    [ "$n" = "0" ] && continue
    echo "   $g -> $d/   ($n files)"
    run "mv $g $d/ 2>/dev/null"
done
echo

# ----------------------------------------------------------------------
echo "2. ARCHIVE SUPERSEDED CODE  ->  archive/"
echo "   Replaced by pilot_detect_v2.py + vru_tracker.py. Archived rather than"
echo "   deleted because tracker_ablation.py reproduces the OLD IoU tracker for"
echo "   the paper's comparison, and the originals are the reference for that."
run "mkdir -p archive/superseded_code archive/old_logs"
for f in pilot_detect.py pilot_detect_yolo26.py pilot_detect_yolov8l.py \
         bicycle_continuity_check.py tiled_continuity_check.py \
         run_continuity_check.slurm run_pilot_detect.slurm \
         run_pilot_detect_colonial_yolo26.slurm \
         run_pilot_detect_colonial_yolov8l.slurm; do
    [ -e "$f" ] || continue
    echo "   $f"
    run "mv '$f' archive/superseded_code/"
done
echo

# ----------------------------------------------------------------------
echo "3. ARCHIVE OBSOLETE LOGS  ->  archive/old_logs/"
echo "   Runs from before the pipeline worked. No longer informative, but small."
for f in build_dataset_40581396.log build_dataset_40583416.log \
         pilot_detect_40537357.log pilot_detect_40539288.log \
         pilot_detect_41740953.log pilot_detect_41740954.log \
         pilot_detect_41795969.log bicycle_continuity_check.log; do
    [ -e "$f" ] || continue
    echo "   $f"
    run "mv '$f' archive/old_logs/"
done
echo

# ----------------------------------------------------------------------
echo "4. DELETE JUNK (safe -- regenerable or duplicate)"
if [ -d __pycache__ ]; then
    echo "   __pycache__/            (Python bytecode, regenerates)"
    run "rm -rf __pycache__"
fi
for f in for_review.tar.gz vision_files.tar.gz; do
    [ -e "$f" ] || continue
    echo "   $f      ($(size $f), transfer artifact -- contents already on disk)"
    run "rm -f '$f'"
done
if [ -e dataset_structure_and_methodology.md ]; then
    echo "   dataset_structure_and_methodology.md"
    echo "     (byte-identical duplicate of 'MioVision Pilot Dataset — Zip"
    echo "      Structure & Extraction Methodology.md')"
    run "rm -f dataset_structure_and_methodology.md"
fi
echo

# ----------------------------------------------------------------------
echo "5. REGENERABLE WORKING FILES  ->  archive/  (kept, just out of the way)"
echo "   Each is reproducible: plan_cyclist_clips.py / audit_tracks.py rebuild"
echo "   them in seconds from the tracks CSVs."
for f in cyclist_clips.txt night_clips.txt sample25.txt audit_clips.txt; do
    [ -e "$f" ] || continue
    echo "   $f"
    run "mv '$f' archive/"
done
echo

# ----------------------------------------------------------------------
echo "6. NEEDS YOUR DECISION -- not touched"
if [ -d runs ]; then
    echo "   runs/                 $(size runs)"
    echo "     Ultralytics' default output dir from early experiments. Probably"
    echo "     dead, but check for anything you want before: ls -R runs | head"
fi
if [ -e output.md ]; then
    echo "   output.md             your terminal scratch file -- yours to keep"
fi
if [ -e sample_thumb.jpg ]; then
    echo "   sample_thumb.jpg      single test frame"
fi
echo "   dataset_frames/       $(size dataset_frames)"
echo "     Contains the OLD pre-fused labels (6 classes, no 'cyclist'). Phase 5"
echo "     needs this moved aside before rebuilding -- see PROGRESS.md. Do it"
echo "     deliberately, not as part of a cleanup:"
echo "       mv dataset_frames/split dataset_frames/split_OLD_unfused"
echo

# ----------------------------------------------------------------------
echo "======================================================================"
echo "RESULT"
echo "======================================================================"
if [ "$APPLY" = "1" ]; then
    echo "top level now: $(ls -1 | wc -l | tr -d ' ') entries"
    echo
    ls -1
else
    echo "Nothing changed. Run again with --apply to execute:"
    echo "    ./organize_repo.sh --apply"
fi
echo
echo "Disk:"
df -h /orange/xiangyan | tail -1
