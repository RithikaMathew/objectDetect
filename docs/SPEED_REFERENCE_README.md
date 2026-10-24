# Bicyclist speed references — plain-language guide

Updated October 24, 2026. **These are speeds measured in the original study, not model predictions.** All 375 deduplicated records concern bicyclists across 14 workbook location labels. The labels do not identify exact camera coordinates.

## What does an average mean here?

Each record is one bicyclist timed through a measured section. Its speed is calculated from **distance ÷ travel time**, converted to miles per hour. For example,35 feet travelled in 2 seconds is about 11.93 mph. The stopwatch duration (such as 2 seconds) is not the time of day.

The table average is **the sum of individual recorded mph values divided by the number of cyclists measured**. It is **not per hour or per 15 minutes**. The speed rows do not provide a recording time of day or a time-bin assignment, so hourly or15-minute speed averages cannot be reconstructed from these references. Separate count workbooks have 15-minute counts, but those bins cannot automatically be assigned to these speed observations.

Median means the middle speed after sorting the observations; it is less affected by one unusually fast cyclist. Range means the slowest to fastest recorded value. These statistics describe the sampled cyclists, not necessarily all-day traffic.

## Average speed by location

| Workbook location | Cyclists measured | Average mph | Median mph | Observed range mph | Facility |
|---|---:|---:|---:|---:|---|
| Aloma | 26 | 13.58 | 13.96 | 8.30–17.92 | Path |
| Baxter | 14 | 16.77 | 15.99 | 11.50–26.36 | Travel Lane |
| Carroll | 15 | 11.89 | 10.80 | 8.34–16.18 | Travel Lane |
| Colonial | 23 | 9.54 | 8.81 | 5.29–19.86 | Bike Lane, Sidewalk |
| Columbia | 9 | 12.24 | 11.42 | 9.63–15.13 | Bike Lane |
| Daniels | 11 | 11.95 | 12.68 | 8.59–14.36 | Path |
| Edgewater | 50 | 12.02 | 11.03 | 6.10–21.22 | Bike Lane |
| Lee | 2 | 8.73 | 8.73 | 6.49–10.96 | Travel Lane |
| Pleasant Hill | 41 | 9.86 | 8.96 | 5.17–19.57 | Path |
| Rinehart/CST | 25 | 12.92 | 13.53 | 5.04–18.92 | Path |
| Silver Star | 43 | 13.63 | 13.38 | 6.60–22.58 | Sidewalk |
| University | 78 | 9.49 | 9.14 | 4.61–17.10 | Sidewalk |
| West Orange/Park | 25 | 10.77 | 9.54 | 6.65–21.24 | Path |
| Winter Park | 13 | 16.08 | 16.02 | 10.14–23.69 | Travel Lane |

Locations with few observations, particularly Lee with 2, provide a limited reference. Different facilities should be compared separately; Colonial combines bike lane and sidewalk in the location-wide row.

## Facility-specific comparisons

| Location | Facility | Cyclists measured | Average mph | Measured section length, feet |
|---|---|---:|---:|---|
| Aloma | Path | 26 | 13.58 | 25 |
| Baxter | Travel Lane | 14 | 16.77 | 25, 48 |
| Carroll | Travel Lane | 15 | 11.89 | 12, 24, 39 |
| Colonial | Bike Lane | 12 | 11.11 | 35 |
| Colonial | Sidewalk | 11 | 7.82 | 30 |
| Columbia | Bike Lane | 9 | 12.24 | 28, 30 |
| Daniels | Path | 11 | 11.95 | 27 |
| Edgewater | Bike Lane | 50 | 12.02 | 24, 43 |
| Lee | Travel Lane | 2 | 8.73 | 47 |
| Pleasant Hill | Path | 41 | 9.86 | 25 |
| Rinehart/CST | Path | 25 | 12.92 | 30 |
| Silver Star | Sidewalk | 43 | 13.63 | 63, 83.5 |
| University | Sidewalk | 78 | 9.49 | 55 |
| West Orange/Park | Path | 25 | 10.77 | 29 |
| Winter Park | Travel Lane | 13 | 16.08 | 32, 67 |

The recorded section lengths come from the workbook; they are not distances between arbitrary video endpoints. The same lengths do not establish which part of the camera view was measured. The average uses original source_mph values. The source workbook uses a slightly rounded unit conversion, so exact recomputation may differ slightly; such arithmetic differences are not model errors.

## University: our manually timed example

- Subject: one red-top bicyclist travelling toward the camera in the September 25, 2019 University SW Speed video.
- Clip: 08:45–09:00.
- GateA crossing: player **07:02.50–07:03.00** (422.50–423.00seconds into the clip).
- GateB crossing: player **07:07.25–07:07.50** (427.25–427.50seconds into the clip).
- Generated clock approximately **08:52:02.50–08:52:07.50**. Burned source-video clock is roughly 2 seconds ahead; use player positions/evidence rather than treating those clocks as interchangeable.
- Owner map distance: 55.17 feet. Midpoint travel time: 4.625 seconds.
- Our manual result: **8.13 mph**, timing-only range 7.52–8.85 mph; map-distance/endpoint errors are additional.
- Study University sidewalk group: 78 cyclists, average **9.49 mph**, median 9.14 mph, range 4.61–17.10 mph.
- Our one-person estimate is **1.36 mph below** the study group average. This is a descriptive comparison, not the same cyclist measured twice and not automatic tracker validation.

## What HiPerGator reports will show

The speed experiment exports bicyclist speeds only. Calibration may use cars or human height, but car/pedestrian speeds and motorcycles are excluded from the speed output. Current automatic experiment covers existing Colonial bicycle candidates, not all 14 locations; the University manual example is included without repeating GPU inference.

For each estimate, the report and CSV record:

1. Method, location/source video, recording date, cyclist/track identity and facility.
2. Exact saved-video clock intervals actually used for measurement, plus clip-relative seconds and frame intervals. Missing/occluded portions are not silently included.
3. The estimated mph and calculation type. Partial-trajectory methods report the median of local velocity windows of approximately 1 second, within usable continuous track segments; the manual gate method reports average speed over one A–B journey.
4. Whether an estimate was unavailable because calibration or tracks were insufficient. A missing speed is not 0 mph.

If several cyclists are summarized together, their count and contributing measurement times must accompany the group average. These results are not automatically hourly averages. Current exploratory rankings compare the same cyclist candidate set across methods within a facility. The separate study reference group has unknown observation times; closeness is not matched-person accuracy.

After pushing/pulling updated files, run from vision3/best/test_colonial:

```bash
python code/submit_speed_pilot.py --go
```

The command submits a CPU preview job for15candidate cameras (13reference locations; Silver Star unmatched), then the prepared Colonial GPU experiments. Download `exp_results/SPEED_PILOT_TAG/` and open `camera_previews/index.html` to screen fixed short daytime excerpts. It does not calculate speeds across all locations yet. Read `speed_results/RESULTS.md`, `all_speed_estimates.csv` (if any estimates succeeded), `university_manual_comparison.csv` and `method_status.json`. Three researched methods still lack full implementations/assets; the report explicitly marks them pending.

## Sources and calculation files

- Original workbook:`bicyclist speeds.xlsx` in Bike Lane Study Counts. Original file is unchanged.
- [Extracted individual reference records and workbook cell addresses](../vision3/best/test_colonial/exp_results/speed_reference_readiness_20261023/all_reference_records.csv).
- [Calculated per-location statistics](../reports/cluster_returns/20261024/speed_reference_summary.csv).
- [University manual crossing inputs](../data/reviews/speed/university_manual_crossing_20261024.json).
- [University video evidence and calculation](../reports/cluster_returns/20261024/university_map_speeds/RESULTS.md).
- [Current command guide](STUDY_NEXT_STEPS.md).


Preview generation dependency: FFmpeg withlibx264 is checked before extraction. The launcher can install an isolated bundled binary if needed; see [preview recovery instructions](STUDY_NEXT_STEPS.md#preview-recovery-after-job47544655-october24). The October24initial0/15preview result was missingFFmpeg, not evidence that all15cameras had unusable images.
