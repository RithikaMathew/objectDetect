#!/bin/bash
#SBATCH --job-name=build_dataset
#SBATCH --partition=hpg-turin
#SBATCH --account=xilei.zhao
#SBATCH --qos=xilei.zhao
#SBATCH --gpus=1
#SBATCH --mem=16gb
#SBATCH --time=08:00:00
#SBATCH --output=build_dataset_%j.log
#SBATCH --requeue

# Journal annotation pool — buckets B / C / D (Colonial track = bucket A, separate)
#   B: 120 uniform train  — split EVENLY across the 4 train sites (~30 each)
#   C: 180 detection-guided train — split EVENLY (~45 each) + per-class quotas
#   D: Corrine densify — 150 uniform @ 5s + 50 rare-class mine top-up (val ONLY)
#
# Colonial is EXCLUDED here — it enters only via run_mining.slurm (bucket A).
# Edgewater / Pine Hills NBL / Aloma Path are never listed (counting-only).
#
# IMPORTANT: move/delete the old unbalanced split before re-running, or the
# resume check will keep Anderson-heavy frames:
#   mv dataset_frames/split dataset_frames/split_OLD_anderson_heavy

cd /orange/xiangyan/rithika/vision

source /orange/xiangyan/rithika/vision/yolo_env/bin/activate

# Sanity: print how many mp4s each train dir contributes (catch empty paths)
echo "=== Video counts per train/val dir ==="
for d in \
    "pilot_clips/MioVision Data/2021 Data/Anderson St" \
    "pilot_clips/MioVision Data/2021 Data/Church Ave" \
    "pilot_clips/MioVision Data/2022 Data/Curry Ford/North" \
    "pilot_clips/MioVision Data/Bike Lane Study/MioVision Video/NBL University" \
    "pilot_clips/MioVision Data/2025 Data/Corrine Dr"
do
    n=$(find "$d" -type f -name '*.mp4' 2>/dev/null | wc -l)
    echo "  $n  $d"
done
echo

python pipeline/extract_frames.py build \
    --train-videos-dir \
        "pilot_clips/MioVision Data/2021 Data/Anderson St" \
        "pilot_clips/MioVision Data/2021 Data/Church Ave" \
        "pilot_clips/MioVision Data/2022 Data/Curry Ford/North" \
        "pilot_clips/MioVision Data/Bike Lane Study/MioVision Video/NBL University" \
    --val-videos-dir \
        "pilot_clips/MioVision Data/2025 Data/Corrine Dr" \
    --uniform-interval 15 \
    --val-uniform-interval 5 \
    --mine-interval 2 \
    --max-seconds 0 \
    --frame-conf 0.15 \
    --min-label-conf 0.10 \
    --max-uniform-frames 120 \
    --max-mined-frames 180 \
    --max-val-frames 150 \
    --max-val-mined-frames 50 \
    --quota-car 400 \
    --quota-truck 120 \
    --quota-bus 100 \
    --quota-person 150 \
    --quota-other-vehicle 100 \
    --out dataset_frames/split

echo
echo "Expect ~4 train sites in the per-site totals (roughly even)."
echo "Corrine val stays val-only. Then:"
echo "  rm -rf dataset_frames/annotation_pool"
echo "  python pipeline/assemble_annotation_pool.py \\"
echo "    --colonial-dir dataset_frames/colonial_track \\"
echo "    --build-dir dataset_frames/split \\"
echo "    --out dataset_frames/annotation_pool \\"
echo "    --zip --finalize"
