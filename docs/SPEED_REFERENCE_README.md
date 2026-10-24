# Bicyclist speed references — plain-language guide

## Latest run: adaptive15-minute bicycle speed comparison

Updated October24,2026. This is prepared code, not a completed result. The owner requested combining consecutive15-minute segments until a small target sample is collected. Colonial North is included in this latest batch because its automatic bicycle speeds remain unfinished; Silver Star has no mapped footage. Thirteen candidate reference locations are planned, using one camera each.

### Sample targets

Target = min(study sample,5,max(3,ceil(study sample/3))). This is a practical exploratory quota, not a statistically powered validation sample. It gives2forLee,3forColumbia,4forDaniels and5forotherlocations.

| Reference location | Study cyclists | Study mean mph | Target candidates | Camera |
|---|---:|---:|---:|---|
| Aloma | 26 | 13.58 | 5 | Aloma Path |
| Baxter | 14 | 16.77 | 5 | Baxter |
| Carroll | 15 | 11.89 | 5 | Carroll NBL |
| Colonial | 23 | 9.54 | 5 | Colonial North |
| Columbia | 9 | 12.24 | 3 | Columbia Ave |
| Daniels | 11 | 11.95 | 4 | Daniels Path |
| Edgewater | 50 | 12.02 | 5 | Edgewater N |
| Lee | 2 | 8.73 | 2 | Lee Road N |
| Pleasant Hill | 41 | 9.86 | 5 | Pleasant Hill Path |
| Rinehart/CST | 25 | 12.92 | 5 | Rinehart Path |
| University | 78 | 9.49 | 5 | University SW Speed |
| West Orange/Park | 25 | 10.77 | 5 | West Orange Path |
| Winter Park | 13 | 16.08 | 5 | Winter Park Rd Speed |

### How the run works

1. Estimate a separate camera calibration from cars for each source. Cars supply scale; no car or pedestrian speeds are output. If calibration fails, stop that site and report the cause rather than process an hour without usable scale.
2. Run the fixed reference detector/tracker/count filters on12:00–12:15 of the selected source, then12:15–12:30, etc. Source clocks are filename-based and exact saved measurement intervals are retained. The selected noon hour is fixed beforehand and is not chosen by speed agreement.
3. Accumulate chronological bicycle candidates with counted status and sufficient continuous trajectory observations. Reject boundary-censored tracks to reduce cross-segment duplication; within-segment fragmentation can still duplicate people.
4. Stop as soon as the quota is reached, after the completed15-minute segment. If a segment has extra candidates, select earliest eligible ones, not those closest to study speed. Mean = sum of selected per-candidate speeds divided by candidate count, not mean of segment means.
5. Maximum4segments/60minutes per location in this first run. If the target is not met, preserve the smaller sample and label it incomplete. Maximum13hours of source footage across13locations; actual processing time is model/GPU-dependent. Only2GPUsite jobs run concurrently.

### Interpretation

The current model combines bicycle/motorcycle categories; these are provisional bicycle candidates until visually checked, not confirmed distinct bicyclists. Cars may calibrate the road, but sidewalks/paths can be elevated. The explicit exploratory transfer flag below permits applying that road-plane mapping outside its car-observation support. Each estimate records this assumption, fraction of observations inside support, and strict supported speed separately. No distance is tuned to the workbook, no missing speed becomes0mph, and no accuracy claim is made. Candidate camera/facility aliases and recording correspondence remain unverified. A close group mean is the requested exploratory comparison, not matched-person validation.

### One submission command

After pushing/pulling updated files, from vision3/best/test_colonial with yolo_env active:

```bash
python code/adaptive_speed_batch.py submit \
  --max-windows 4 --exploratory-road-plane-transfer --go
```

Without --go it only prints the plan. The command submits one12-task GPUarray (concurrency2) plus a CPUfinal report dependent on all site jobs finishing, including failed ones. It does not repeat the preview-screening jobs. Requires already-extracted source files, cached detector/XCLIP dependencies and model weights; missing sources/weights stop submission. Runtime and data-success are not yet verified on cluster. Partial job submissions are recorded in manifest.json; do not blindly resubmit if the final-report submission fails.

Output folder: `exp_results/ADAPTIVE_SPEED_TAG/`. Read `RESULTS.md` and `comparison.csv` for study mean, model-candidate mean, difference, sample size, quota, minutes and incomplete/failure status. `selected_candidates.csv` lists exact individual measurement intervals, source/annotation video paths and transfer/identity qualifications. Each site also retains calibration diagnostics, candidate exclusions and all processed-window records. The three other researched full-paper implementations remain pending; this batch uses the implemented ICCV2021 adapter.


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
| Colonial | 23 | 9.54 | 5 | Colonial North |
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


### Counts and timestamps in adaptive results

comparison.csv now distinguishes all bicycle-labelled candidate tracks found, candidates counted by the fixed pipeline, speed-eligible candidates and the smaller chronological sample selected for the average. Candidate tracks are not verified unique cyclists; possible motorcycles/fragmentation require review. all_candidate_timestamps.csv records every candidate with track first/last-seen clocks, source/annotated-video paths, measurement intervals and rejection reasons; selected_candidates.csv identifies those used in the average. The final README summary shows found/usable/used counts and selected measurement times. Existing per-site candidate exports can regenerate these report fields without new inference.

Colonial already has four hand-labelled clips and saved detections:7actual bicyclists,13pedestrians,1motorcycle. The saved legacy evaluation counted6of7bicyclists; the remaining bicyclist was detected but rejected from counting. Counts/timestamps exist; physical bicyclemph is still not successfully validated. Do not rerun Colonial object detection solely to recover those counts/timestamps; reuse saved tracks and truth files. The latest owner request includes Colonial North in this adaptive batch; the selected noon hour is sampled, not all four labelled clips. Its location-wide 9.54mph study mean pools two facilities: bike lane 11.11mph (12 records), sidewalk 7.82mph (11 records). This pooled comparison is not facility-matched validation.

### Results saved separately as each site progresses

Under `exp_results/ADAPTIVE_SPEED_TAG/`, open a site folder such as `s03_colonial_north/RESULTS.md`. Use the exact folder names in `manifest.json`. Site reports appear at startup, update after every completed 15-minute window, and record failures immediately. You do not need to wait for the final combined report.

- `comparison.csv`: study mean, provisional model mean, found/countable/speed-usable/selected candidate counts and processed intervals.
- `all_bicycle_candidates.csv` and `all_candidate_timestamps.csv`: candidate timestamps, exclusions, speed intervals and annotated video paths, once candidates exist.
- `selected_candidates.csv`: candidates used in the mean, once any are selected.
- `status.json`: current stage, active window, completed windows and failure message. A stopped Slurm job may retain its last in-progress stage.
- `calibration/`: calibration geometry and diagnostics.
- `windows/w00/`, etc.: `pipeline_task.json`, `pipeline.log`, successful `result.json`, copied `run_log.json` and available raw track CSVs. Videos remain in their original annotated folders; the run log records their paths.
- `error.txt`: worker traceback on a caught failure. Slurm array logs remain in the batch root as `site_ARRAY_INDEX.log`, including calibration output or termination messages.

The combined root report is generated after all site workers finish. Empty or failed stages do not become zero-speed measurements. Existing submitted jobs retain their old manifest; inclusion of Colonial applies to a newly submitted batch using this updated code.
