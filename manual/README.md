# Bicycle counts and speed comparison

**Updated October 27, 2026 — completed HiPerGator run on the same 18 manually annotated clips, across nine cameras.** The daytime bicycle minimum was 1.5 seconds. All selected clips were processed without stopping at a cyclist quota. Pedestrian and nighttime policies were retained.

**Counts in these clips: study 35, HiPerGator 32, manual 30.** There are 29 usable manual speeds from 30 annotated cyclists. Similar count totals do not establish accuracy: missed cyclists and extra tracks can cancel out.

**Study/validation count** is the bicycle count in these selected video intervals. **Study/validation mph** comes from a separate location-level speed sample; it is not the known speed of these same cyclists. HiPerGator is automatic detection/tracking; Manual is your rear-tire clicks. Numbers in parentheses after mph are speed sample sizes.

| Location | Available hours | Same clips: bins / nominal min | Study count | HiPerGator count | Manual count | Study mph (n) | HiPerGator mph (n) | Manual mph (n) | Robust manual mph |
|---|---:|---|---:|---:|---:|---|---|---|---:|
| Aloma | 47.99 | 3 / 45 | 4 | 5 | 4 | 13.58 (26) | 21.45 (5) | 19.81 (4) | 19.43 |
| Carroll | 47.99 | 1 / 15 | 2 | 2 | 2 | 11.89 (15) | 12.22 (2) | 12.37 (2) | 12.59 |
| Colonial | 47.99 | 2 / 30 | 3 | 3 | 3 | 9.54 (23) | 7.35 (3) | 10.71 (3) | 10.77 |
| Columbia | 47.98 | 3 / 45 | 4 | 7 | 4 | 12.24 (9) | 7.35 (7) | 12.47 (4) | 12.62 |
| Edgewater | 47.98 | 4 / 60 | 10 | 6 | 6 | 12.02 (50) | 14.10 (6) | 14.00 (5) | 11.51 |
| Lee | 47.99 | 2 / 30 | 5 | 3 | 4 | 8.73 (2) | 10.17 (3) | 12.36 (4) | 12.40 |
| Pleasant Hill | 30.01 | 1 / 15 | 2 | 2 | 2 | 9.86 (41) | 9.12 (2) | 8.99 (2) | 8.80 |
| Rinehart/CST | 47.99 | 1 / 15 | 1 | 1 | 1 | 12.92 (25) | 12.06 (1) | 12.01 (1) | 12.48 |
| University | 47.99 | 1 / 15 | 4 | 3 | 4 | 9.49 (78) | 14.00 (3) | 16.98 (4) | 17.11 |

**Coverage:** both methods use the same selected video files (270 nominal minutes; about 269.90 processed minutes). Some files end slightly before the complete study bin. The study counts shown here cover only these 18 bins, not all 27 intervals originally offered for review. West Orange has no submitted annotations and is excluded from this same-video comparison; Baxter, Daniels and Winter Park belong to the separate broader run.

**Same clips does not mean matched people or identical measurement seconds.** Automatic tracks still need identity/type review; they can include duplicate IDs, static objects or motorcycles. Each cyclist estimate uses only its own recorded measurement seconds, not all 15 minutes. One Edgewater annotation spans 1.4 seconds and has no manual speed. No missing speed is treated as zero.

## What the results mean

- **Carroll is encouraging:** the two new automatic speed intervals overlap both annotated cyclists previously reported missed; automatic mean 12.22 mph versus manual 12.37 mph. Full-track identity still needs checking.
- **Columbia has confirmed visual failures:** your review found pedestrians labelled as bicyclists and a missed bicyclist, while at least one actual bicyclist was detected. Its 7 automatic counts versus 4 study/manual are not reliable cyclist counts. Specific track IDs are needed before excluding samples from its raw mean.
- **Aloma has an extra candidate:** 5 automatic versus 4 study/manual. Inspect the automatic candidate at 12:59:47 before calling it a genuine cyclist or false positive.
- **Edgewater received favorable visual review:** you reported bicycle counting looked quite accurate. Earlier temporal-overlap clues do not prove duplicates or counting errors; full-track identity and physical speed remain unverified.
- **Physical scale remains uncertain:** Aloma and University speed means differ substantially from the separate study averages. The robust estimator does not remove that gap. The comparison cannot tell how much comes from calibration versus different cyclists.

[Exact per-clip counts, automatic speed timestamps and review priorities](../reports/cluster_returns/20261027/completed_speed_batches/RESULTS.md) · [Combined table CSV](analysis/same_video_comparison.csv). Recording clocks are filename-inferred, not independently verified.

## Other locations: completed broader HiPerGator run

These locations were processed in the separate broader run but have no submitted manual annotation clips for the same-video comparison. They are not missing jobs. Counts of candidate tracks are not verified cyclist counts. The speed mean can use fewer tracks than were speed-usable because this run stopped selection at its quota.

| Location | Processed minutes | Candidate tracks found | Speed-usable / used for mean | Study mph (n) | HiPerGator mph (n) | Manual comparison |
|---|---:|---:|---|---|---|---|
| Baxter | 59.99 | 5 | 0 / 0 | 16.77 (14) | No usable speed | No submitted annotations |
| Daniels | 59.98 | 5 | 0 / 0 | 11.95 (11) | No usable speed | No submitted annotations |
| West Orange/Park | 59.99 | 11 | 6 / 5 | 10.77 (25) | 26.12 (5) | No submitted annotations |
| Winter Park | 59.99 | 2 | 0 / 0 | 16.08 (13) | No usable speed | No submitted annotations |

**West Orange/Park** is the workbook label mapped to **West Orange Path**, not a confirmed separate Orange Park location. Its 26.12 mph mean uses five selected candidates; one is 43.489 mph and needs identity/type/geometry review. Baxter, Daniels and Winter Park completed processing but produced no speed-usable candidates; the precise rejection causes need their saved candidate diagnostics. Silver Star has no mapped source and was not processed.

[Your Columbia/Edgewater video review](../reports/cluster_returns/20261027/completed_speed_batches/owner_video_review.md). Qualitative counting approval does not validate mph. No raw candidate speeds were deleted from the results.

## How speed was calculated

You paused the video and repeatedly clicked where the same cyclist’s rear tire touched the pavement. Each point has an image position and video time. IDs are scoped to each clip; clearly separated encounters sharing an ID were split. The camera calibration, estimated from car observations, converts those clicks to estimated ground positions in metres.

**Manual mph:** add the distances between successive ground positions, divide by the time from the first to last click, and multiply by 2.23694. At least three points spanning 1.5 seconds are required. Example: 10 metres in 2 seconds = 11.18 mph. Click jitter can inflate the summed distance.

**HiPerGator mph:** use automatically tracked positions and take the median of speeds fitted over short continuous time windows. **Robust manual mph:** fit a smooth trajectory using the actual click times, reduce the influence of outliers, then fit distance against time. All site means give equal weight to available per-cyclist speed estimates; they are not averages of 15-minute-bin means. The different estimators and contact points can produce different speeds even with the same calibration.

All three depend on learned metric scale; manual annotation does not independently verify mph. Perspective, lens distortion and road-to-sidewalk height differences can affect the results. The method builds on [Revaud and Humenberger, ICCV 2021](https://openaccess.thecvf.com/content/ICCV2021/html/Revaud_Robust_Automatic_Monocular_Vehicle_Speed_Estimation_for_Traffic_Surveillance_ICCV_2021_paper.html) and their [calibration code](https://github.com/naver/cctv). Manual clicks and robust fitting are project-specific adaptations, not a complete reproduction or established cyclist-speed validation.

**Timing and sensitivity:** all 18 re-encoded review clips had regular presentation timestamps near 29.97 fps. The original hourly recordings were not audited for timing, so this does not prove there was no earlier timing error. Sensitivity ranges assume 3-pixel click noise and a uniform ±15% camera-scale scenario; those are illustrative assumptions, not measured accuracy bounds. [Per-cyclist plots, endpoint comparison and sensitivity results](speed_plan_20261027/trajectory/RESULTS.md).

**Study speed method:** Mighk Wilson stopwatch-timed cyclists while watching half-speed video and accounted for playback speed in the workbook. We use the supplied mph without doubling it again. Some corridors had separate speed-analysis visits. No study speed records have been linked to individual people/timestamps in these selected clips.

## Why Aloma has 4 selected cyclists but 26 speed records

Aloma Path has **47.99 measured playback hours**. This pilot selected the first available day’s source hour nearest noon, then its study-positive bins: October 30, 2019, 12:00–12:15, 12:30–12:45 and 12:45–13:00. These total 45 minutes and 4 study bicycles. The omitted 12:15 bin recorded zero.

| Dataset | Bicycle count |
|---|---:|
| Aloma Path, full October 30–31 count period (192 fifteen-minute bins) | 191 |
| Aloma Sidewalk, separate camera/count table | 19 |
| Aloma Path, selected 45 minutes | 4 |
| Separate Aloma speed-reference sample | 26 |

The 26 speed observations are not the number of bicycles in the full recording. Their session and individual timestamps are unknown; we cannot confirm they came from the same available recording. They are a location reference, not ground-truth speeds for the four annotated cyclists. Counts come from the Bicycles worksheets in Aloma_Path_716686_10-30-2019.xls and Aloma_Sidewalk_716692_10-30-2019.xls; speeds come from the consolidated speed workbook.

## Measured recording hours

All 1,919 inventoried files across 41 cameras were measured. Hours sum playback lengths; file counts are not hours, and summed lengths do not establish gap-free coverage. The table lists the chosen camera per speed-reference location; different camera sides are not pooled.

| Location | Camera | Source files | Measured playback hours |
|---|---|---:|---:|
| Aloma | Aloma Path | 48 | 47.99 |
| Baxter | Baxter | 48 | 47.99 |
| Carroll | Carroll NBL | 48 | 47.99 |
| Colonial | Colonial North | 48 | 47.99 |
| Columbia | Columbia Ave | 49 | 47.98 |
| Daniels | Daniels Path | 48 | 47.99 |
| Edgewater | Edgewater N | 48 | 47.98 |
| Lee | Lee Road N | 48 | 47.99 |
| Pleasant Hill | Pleasant Hill Path | 31 | 30.01 |
| Rinehart/CST | Rinehart Path | 48 | 47.99 |
| Silver Star | No mapped source | — | Unknown |
| University | University SW Speed | 48 | 47.99 |
| West Orange/Park | West Orange Path | 37 | 36.12 |
| Winter Park | Winter Park Rd Speed | 48 | 47.98 |

Columbia’s 49 multipart files total **47.98 hours**, not 49 hours. Silver Star has no mapped source. [Full camera duration audit](../docs/VIDEO_DURATION_README.md).

## Remaining checks and earlier experiments

Review the flagged automatic tracks, then confirm University’s approximately 55.17-foot map endpoints in the video to check the learned distance scale. No new broad model sweep or repeat manual annotation is needed now. Wheel/marking checks have code but lack the necessary evidence for physical-scale results. ByteTrack is already used; a new wheel-keypoint model has not been trained.

[Broader 1.5-second run](../reports/cluster_returns/20261027/completed_speed_batches/shortday_sites.csv) uses different coverage and quota stopping; it is separate from the main table. [Earlier three-second baseline README](analysis/README_baseline_before_same_video_20261027.md) and [baseline data](analysis/site_summary.csv) are preserved. [Manual-seeded optical flow](optical_flow_20261026/RESULTS.md) passed held-out drift checks on only 2 of 30 encounters and does not replace manual tracking. [Full analysis/run guide](../docs/SPEED_PLAN_RUN.md).

Original annotation JSONs remain unchanged. [Manual measurement timestamps](analysis/DETAILS.md) · [Automatic measurement timestamps](../reports/cluster_returns/20261027/completed_speed_batches/same_video_speed_times.csv) · [Study provenance](analysis/source_provenance.md).
