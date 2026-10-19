#!/bin/bash
# Delete a session's extracted .mp4 chunks -- but ONLY after verifying that
# every chunk has a corresponding tracks CSV.
#
# WHY THE CHECK: extracting the whole Bike Lane Study needs ~325 GB and
# /orange/xiangyan has ~314 GB free on a filesystem already 85% full and shared
# with the group, so video has to be deleted as you go. That makes deletion
# routine, and routine deletion of source data needs a guard -- the counts must
# exist before the footage goes. Re-extracting is an hour; discovering months
# later that a session was deleted un-counted is worse.
#
# The tracks CSVs and funnel CSVs are kept: they are small and they are the
# actual result. The .mp4s are reproducible from MioVision_Data.zip.
#
# Usage:
#   ./cleanup_session.sh "MioVision Data/.../Standard_SCU8OG_2019-07-10_0000" \
#                        pilot_output/sessions/BL_Colonial_2019-07-10
#   ./cleanup_session.sh ... --force     # skip the confirmation prompt

set -u
SESSION="${1:?usage: cleanup_session.sh <session-path-under-pilot_clips> <results-dir> [--force]}"
RESULTS="${2:?need the results dir containing *_tracks.csv}"
FORCE="${3:-}"

VIDDIR="pilot_clips/$SESSION"

if [ ! -d "$VIDDIR" ]; then
    echo "Nothing to do: $VIDDIR does not exist."
    exit 0
fi

n_mp4=$(find "$VIDDIR" -maxdepth 1 -name "*.mp4" | wc -l)
n_csv=$(find "$RESULTS" -maxdepth 1 -name "*_tracks.csv" 2>/dev/null | wc -l)

echo "video chunks on disk : $n_mp4   ($VIDDIR)"
echo "tracks CSVs written  : $n_csv   ($RESULTS)"

if [ "$n_mp4" -eq 0 ]; then
    echo "Already cleaned."
    exit 0
fi

if [ "$n_csv" -lt "$n_mp4" ]; then
    echo
    echo "REFUSING TO DELETE: $n_csv CSVs for $n_mp4 chunks."
    echo "Some chunks have not been counted yet. Finish the array first:"
    echo "  squeue -u rmathew1"
    echo "Chunks with no matching CSV:"
    for f in "$VIDDIR"/*.mp4; do
        b=$(basename "$f" .mp4)
        [ -f "$RESULTS/${b}_tracks.csv" ] || echo "    $b"
    done
    exit 1
fi

size=$(du -sh "$VIDDIR" | cut -f1)
echo
echo "All $n_mp4 chunks have results. About to free $size."

if [ "$FORCE" != "--force" ]; then
    read -r -p "Delete the .mp4 files in $VIDDIR? [y/N] " ans
    case "$ans" in
        y|Y) ;;
        *) echo "Aborted."; exit 0 ;;
    esac
fi

find "$VIDDIR" -maxdepth 1 -name "*.mp4" -delete
echo "Deleted. Results kept in $RESULTS."
echo "Re-extract any time with: SESSION=\"$SESSION\" sbatch extract_session.slurm"
df -h /orange/xiangyan | tail -1
