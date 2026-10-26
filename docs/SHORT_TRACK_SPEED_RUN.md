# Daytime short-track counting and speed rerun

This is a separate experiment; the saved three-second baseline is preserved. It is prepared, not yet submitted here.

The daytime bicycle counting minimum changes from **3.0 to 1.5 seconds**. Aloma's five rejected bicycle-labelled tracks lasted 1.6–2.9 seconds, so this removes their duration barrier. It does not prove all five are genuine cyclists or that every track has a usable continuous metric trajectory. There are four study/manual cyclists in the selected Aloma intervals, so the extra candidate needs review.

Pedestrian duration, detector confidence, class fusion/veto, movement/static filters and nighttime policy are preserved. Where nighttime duration previously inherited three seconds, that value is explicitly retained; the existing nighttime-only 0.3-second exception remains unchanged. Metric speed still requires sufficient continuous trajectory observations; shortening the count threshold does not force a missing speed to become zero or a valid estimate.

After pushing and pulling the updated code, on HiPerGator:

```bash
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
python code/adaptive_speed_batch.py recover \
  --directory exp_results/ADAPTIVE_SPEED_20261024_195012 \
  --all-sites --day-bicycle-min-seconds 1.5 --go
```

This submits all 13 mapped sites, at most two GPU workers concurrently, reusing each camera's saved calibration. Detection/tracking/counting is rerun with the new daytime setting; it does not reuse old counted/not-counted decisions. Each site gets up to four consecutive 15-minute windows and can stop after its original sample quota. Thus sample/time coverage may differ from baseline and must be reported.

Outputs: `exp_results/ADAPTIVE_SPEED_shortday_TIMESTAMP/`. Each site writes its progress and results separately; the combined report runs after all workers end. Exact settings are saved in each `windows/wNN/pipeline_task.json`, with the daytime minimum also stated in RESULTS.md. Original results remain unchanged. Compare newly accepted tracks visually and check false counts, not only whether the mean approaches the study mean.

For an Aloma-only check instead of the full run, replace `--all-sites` with `--index 0`. Do not submit both unless intentionally doing duplicate processing.
