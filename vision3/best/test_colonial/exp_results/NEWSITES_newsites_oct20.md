# Two additional sites: reference-system validation

Configuration: fine-tuned RT-DETR + SAHI + ByteTrack/ID stitching + X-CLIP + detector/motion/duration/static rules. TTA and enhancement off.
No complete human truth exists for these clips: predicted counts are NOT accuracy.
These sites appear in the documented training-data recipe; do not call this an unseen-site test.
Windows are selected by a fixed daytime/noon preference, not by model performance.
Clocks are inferred from filenames, not verified against the embedded camera clock. Check before using time-based conclusions.

## Existing four labelled clips: detector versus X-CLIP
Saved track classification: detector 16/21; X-CLIP 14/21.
Provisional time-matched comparison, not detector recall or verified standalone counting accuracy.
Full comparison: `/orange/xiangyan/rithika/vision/vision3/best/test_colonial/exp_results/classifier_comparison_20261020/RESULTS.md`

## Anderson St (2021) — SUCCEEDED
Source: `/orange/xiangyan/rithika/vision/pilot_clips/MioVision Data/2021 Data/Anderson St/Standard_SCU8PM_2021-04-13_0000/Standard_SCU8PM_2021-04-13_0000.013.mp4`
Source metadata: {'fps': 29.970000084744214, 'frames': 107864, 'width': 720, 'height': 480}
Planned first-frame clock: 2021-04-13_12:00:00 (inferred)
Predicted counts only: {'bicyclists': 1, 'pedestrians': 1, 'vehicles': 137}
Runtime: 38.7 minutes
Actual processed duration: 900.0 seconds
Exact annotated video paths:
- `/orange/xiangyan/rithika/vision/vision3/best/test_colonial/annotated/newsites_oct20_anderson_2021/Standard_SCU8PM_2021-04-13_0000.013/newsites_oct20_anderson_2021__day_1200-1215__sahi640+speedrule-lateral+shortrule-night+detfuse+staticfilter__20210413.mp4`
Tracks: `/orange/xiangyan/rithika/vision/vision3/best/test_colonial/counts/newsites_oct20_anderson_2021/Standard_SCU8PM_2021-04-13_0000.013_tracks.csv`
Review every cyclist/pedestrian; report missed people, duplicate IDs, object-to-person ID jumps, e-scooter labels and clip timestamps.

## Curry Ford North (2022) — SUCCEEDED
Source: `/orange/xiangyan/rithika/vision/pilot_clips/MioVision Data/2022 Data/Curry Ford/North/Standard_SCU8OG_2022-05-17_0000/Standard_SCU8OG_2022-05-17_0000.013.mp4`
Source metadata: {'fps': 29.970000084744214, 'frames': 107864, 'width': 720, 'height': 480}
Planned first-frame clock: 2022-05-17_12:00:00 (inferred)
Predicted counts only: {'bicyclists': 0, 'pedestrians': 0, 'vehicles': 448}
Runtime: 38.5 minutes
Actual processed duration: 900.0 seconds
Exact annotated video paths:
- `/orange/xiangyan/rithika/vision/vision3/best/test_colonial/annotated/newsites_oct20_curryford_2022/Standard_SCU8OG_2022-05-17_0000.013/newsites_oct20_curryford_2022__day_1200-1215__sahi640+speedrule-lateral+shortrule-night+detfuse+staticfilter__20220517.mp4`
Tracks: `/orange/xiangyan/rithika/vision/vision3/best/test_colonial/counts/newsites_oct20_curryford_2022/Standard_SCU8OG_2022-05-17_0000.013_tracks.csv`
Review every cyclist/pedestrian; report missed people, duplicate IDs, object-to-person ID jumps, e-scooter labels and clip timestamps.

## final_review — SUCCEEDED
{'output': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/exp_results/final_review_20261020', 'requires_human_review': True}

## truth_headers — SUCCEEDED
{'output': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/annotated_gt', 'originals_preserved': True}

