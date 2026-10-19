#!/bin/bash
# Submits prefetch_weights.slurm, then run_compare_array.slurm to start only
# after prefetch succeeds (afterok dependency) — one command, no manual
# job-ID copying.
#
# Usage:
#   ./submit_all.sh
#   VIDEO_PATH=/orange/.../myclip.mp4 ./submit_all.sh   # override video

set -euo pipefail
cd "$(dirname "$0")"
mkdir -p logs   # must exist before sbatch — SLURM opens --output before the job script runs

PREFETCH_ID=$(sbatch --parsable prefetch_weights.slurm)
echo "prefetch job:  $PREFETCH_ID"


# afterok (not afternotok) is used deliberately with an "any" fallback: some
# clusters' dependency accounting lags or mis-resolves afterok even when the
# upstream job exited 0, which manifests as DependencyNeverSatisfied forever.
# afterany avoids that failure mode; run_compare_array.slurm's own
# weights-dir check below catches a genuinely failed prefetch instead.
ARRAY_ID=$(sbatch --parsable --dependency=afterany:"$PREFETCH_ID" run_compare_array.slurm)
echo "compare array: $ARRAY_ID (5 tasks, waits on $PREFETCH_ID)"

echo ""
echo "Monitor with: squeue -u \$USER"
echo "Once all 5 tasks finish, aggregate results with:"
echo "  python aggregate_results.py /orange/xiangyan/rithika/vision/vision3/pilot_output/compare"
