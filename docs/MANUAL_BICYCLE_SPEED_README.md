# Manual bicycle speed review — start here

Use the original study bicycle count bins to choose review intervals, not detector counts. The existing detector thresholds remain unchanged. A zero recorded study bicycle count is omitted; missing cells remain flagged. No per-person speed labels or exact encounter frames can be recovered from an aggregate count.

After pushing/pulling the new code, from test_colonial on HiPerGator:

```bash
sbatch code/manual_bicycle_review.slurm
```

This CPU-only job uses the already selected source hour for each camera in ADAPTIVE_SPEED_20261024_195012. It extracts only positive or missing-count 15-minute bins from those hours, using original-resolution source footage. It does not rerun object detection and does not need the other site workers to finish. If their calibration is not saved yet, that site's manual pack has no mph; regenerate a new pack after calibration becomes available.

Download the whole exp_results/MANUAL_BICYCLE_REVIEW_JOBID folder. Open index.html. Select a video and cyclist ID. Pause, step and click the same ground-contact point at three or more times spanning at least1.5seconds. Use a new ID per person. Download observations before closing; send back manual_bicycle_observations.json. Browser timing is approximate.

The page estimates mean path speed from manually marked image points projected through the saved learned camera homography: sum of successive ground distances / elapsed seconds, converted to mph. It bypasses tracking and count-duration rules, but does not remove camera-scale error, click noise, road/sidewalk plane assumptions or lens distortion. Without saved numerical calibration it records points without mph. Output is exploratory, not matched validation against the separate speed workbook.

Coverage: this initial pack covers selected source hours, not every positive bin across all48hours. manifest.json explicitly lists positive/missing bins outside those hours, unmapped workbooks and calibration availability. Source workbook channels remain in the manifest; only compare channels visible in the video. The manual page displays workbook counts as review guidance, not person-level truth.

Carroll's first priority is12:30–12:45 September10: study2, model0, owner saw cyclists12:39 and12:43:53. Baxter's selected noon hour has study0and is omitted.
