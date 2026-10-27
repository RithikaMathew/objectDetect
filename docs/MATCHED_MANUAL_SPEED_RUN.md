# Run HiPerGator on the exact manually annotated videos

This is the next comparison run; it has been prepared, not submitted locally. It replaces the earlier full-hour rerun plan for this comparison.

Use the **18 exact MP4 clips that have submitted manual annotation points**, across nine cameras. Reuse each camera's existing calibration. Apply the requested **1.5-second daytime bicycle minimum**, retaining pedestrian, nighttime and other counting rules. Process every selected clip, even if a speed quota has already been met; include every eligible automatic speed estimate instead of choosing just the first few. Missing/failed clips stay unavailable, never zero.

| Camera | Annotated 15-minute clips | Nominal minutes |
|---|---:|---:|
| Aloma Path | 3 | 45 |
| Carroll NBL | 1 | 15 |
| Colonial North | 2 | 30 |
| Columbia Ave | 3 | 45 |
| Edgewater N | 4 | 60 |
| Lee Road N | 2 | 30 |
| Pleasant Hill Path | 1 | 15 |
| Rinehart Path | 1 | 15 |
| University SW Speed | 1 | 15 |
| Total | 18 | 270 |

These differ from all 27 clips originally offered for manual review. Nine intervals with no submitted points are excluded; West Orange has none and is outside this run. This is a selected annotated subset, not a representative all-day evaluation. Original full-hour and three-second results remain separate; changed duration and changed coverage both matter when comparing them.

After pushing/pulling the updated code and manual analysis files, run on HiPerGator:

```bash
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
python code/adaptive_speed_batch.py match-manual \
  --directory exp_results/ADAPTIVE_SPEED_20261024_195012 \
  --manual-pack exp_results/MANUAL_BICYCLE_REVIEW_47586267 \
  --day-bicycle-min-seconds 1.5 --go
```

The corrected observations default to `manual/analysis/normalized_observations.json` at the repository root. No new annotations are required. To inspect the plan without submission, omit `--go`. Source camera/recording identities are checked, along with saved calibration and the actual clip files. Original video dimensions must match calibration dimensions. Colonial's cut clips use chunk1 and their actual interval start clock rather than the hourly source index.

Output: `exp_results/ADAPTIVE_SPEED_manualmatch_TIMESTAMP/`. Each site publishes results as it progresses. Read final `RESULTS.md`, `comparison.csv`, and **`matched_intervals.csv`**: the latter compares study count, submitted manual count, automatic count and both speed means for each identical clip. Sample sizes and all-candidate timestamps are retained. No early stop at sample quota.

Same video coverage does not establish that every automatic track matches a particular annotated cyclist. Identity matching and independent same-person reference speeds are still required for speed MAE or detector precision/recall. This run also retains the existing difference between automatic median local speed and manual path-distance average, and both share the learned metric scale.
