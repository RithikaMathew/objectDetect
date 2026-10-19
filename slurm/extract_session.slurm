#!/bin/bash
#SBATCH --job-name=extract_sess
#SBATCH --partition=hpg-turin
#SBATCH --account=xilei.zhao
#SBATCH --qos=xilei.zhao
#SBATCH --cpus-per-task=2
#SBATCH --mem=8gb
#SBATCH --time=02:00:00
#SBATCH --output=extract_sess_%j.log

# Extract ONE full site-session's .mp4 chunks out of MioVision_Data.zip.
#
# WHY THIS IS NEEDED: video_site_mapping.csv reports chunk counts read from
# all_videos.txt, which inventories the ZIP. pilot_clips/ on disk only ever
# held a few sample chunks, so a "48 chunk" session had 2 files present and the
# count array silently processed 2 hours instead of 48 -- every task reported
# COMPLETED, because doing nothing is not an error. Extract before counting,
# and always check the on-disk count against n_mp4_chunks.
#
# No GPU requested: this is pure I/O.

set -u
cd /orange/xiangyan/rithika/vision

SESSION="${SESSION:-MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/Standard_SCU8OG_2019-07-10_0000}"

echo "=== session: $SESSION ==="
echo "in zip:"
unzip -l MioVision_Data.zip "$SESSION/*.mp4" | tail -3
echo
echo "on disk before:"
find "pilot_clips/$SESSION" -maxdepth 1 -name "*.mp4" 2>/dev/null | wc -l
echo
df -h /orange/xiangyan | tail -1

# -n: never overwrite an existing file, so re-running is safe and resumable.
# Only .mp4 is extracted; the .jpg thumbnails and .cut markers are not needed
# for counting and would roughly double the transfer.
unzip -n -q MioVision_Data.zip "$SESSION/*.mp4" -d pilot_clips/

echo
echo "on disk after:"
find "pilot_clips/$SESSION" -maxdepth 1 -name "*.mp4" | wc -l
du -sh "pilot_clips/$SESSION"
echo
echo "Now confirm this matches n_mp4_chunks in video_site_mapping.csv before"
echo "submitting run_site_array.slurm, and set --array to cover that count."
