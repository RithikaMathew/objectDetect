# Speed analysis workflows

These workflows reproduce completed work. Start with manual/README.md for results. No run is currently required.

## Contents

- [MANUAL_BICYCLE_SPEED_README.md](#workflow-1)
- [MATCHED_MANUAL_SPEED_RUN.md](#workflow-2)
- [SHORT_TRACK_SPEED_RUN.md](#workflow-3)
- [SPEED_ANALYSIS_ONE_PASS.md](#workflow-4)
- [SPEED_PLAN_RUN.md](#workflow-5)

<a id="workflow-1"></a>
## MANUAL_BICYCLE_SPEED_README.md
Original location: `docs/MANUAL_BICYCLE_SPEED_README.md`.

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


<a id="workflow-2"></a>
## MATCHED_MANUAL_SPEED_RUN.md
Original location: `docs/runs/MATCHED_MANUAL_SPEED_RUN.md`.

> Reproduction guide for previously completed work. Start with [current results](../manual/README.md) and [current tasks](../README.md); no resubmission is required for repository cleanup.

# Run HiPerGator on the exact manually annotated videos

This comparison run completed; returned results are included in manual/README.md. The commands below are retained for reproduction. It replaces the earlier full-hour rerun plan for this comparison.

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


<a id="workflow-3"></a>
## SHORT_TRACK_SPEED_RUN.md
Original location: `docs/runs/SHORT_TRACK_SPEED_RUN.md`.

> Reproduction guide for previously completed work. Start with [current results](../manual/README.md) and [current tasks](../README.md); no resubmission is required for repository cleanup.

# Daytime short-track counting and speed rerun

This is a separate experiment; the saved three-second baseline is preserved. The run completed and its returned results are included in manual/README.md. The commands below are retained for reproduction.

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


<a id="workflow-4"></a>
## SPEED_ANALYSIS_ONE_PASS.md
Original location: `docs/runs/SPEED_ANALYSIS_ONE_PASS.md`.

> Reproduction guide for previously completed work. Start with [current results](../manual/README.md) and [current tasks](../README.md); no resubmission is required for repository cleanup.

# One-pass bicycle speed analysis

The first local run is complete: [results](../manual/speed_analysis_20261026/RESULTS.md). It processed 30 annotated encounters across nine cameras, produced estimates for 29, and audited all 18 annotated review clips. One Edgewater encounter remains excluded because its span is only 1.4 seconds. No original annotation or previous result was replaced.

This pass includes time-aware robust trajectory fitting (Huber regression plus Theil–Sen slope), old path and endpoint comparisons on identical annotations, a video packet timestamp audit, 29 trajectory plots, and Monte Carlo sensitivity ranges. The fit is a project implementation, not a complete reproduction of a published paper.

The timestamp audit checks presentation packet timestamps in the re-encoded review clips. All 18 local clips had regular ~29.97 fps timestamps. It does not verify the original hourly recording's timing, frame-accurate manual seeking, or the burned clock. Manual browser seconds remain unchanged. No half-speed multiplier is applied.

Sensitivity defaults are **assumptions**, not measured errors: 3-pixel click standard deviation and a uniform ±15% camera-scale scenario, with 500 simulations. One scale factor is shared by a camera's cyclists per simulation. These ranges omit unknown distortion, identity errors and sampling uncertainty; they are not verified accuracy bounds. The ±15% is configurable and is not derived from validation or used to accept/reject a cyclist. Old manual and new manual estimates use the same usable encounters. The prior HiPerGator column is contextual: its people and coverage can differ. The same-video GPU comparison remains a separate job.

## Optional HiPerGator rerun

No rerun is needed to view the local results. To reproduce the full analysis on HiPerGator after pushing/pulling the new code and manual inputs:

```bash
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
mkdir -p logs
sbatch code/speed_analysis_pass.slurm
```

This single CPU job runs all four stages. It can run alongside the GPU jobs and does not submit another detector run. It requires NumPy, SciPy, Matplotlib and ffprobe (the wrapper attempts the ffmpeg module). Input videos are the existing `exp_results/MANUAL_BICYCLE_REVIEW_47586267` pack. Output is a new `exp_results/SPEED_ANALYSIS_JOBID/` folder. Requeue/resubmission creates a different job-ID folder; existing results are never overwritten.

Read `RESULTS.md` first. `cyclists.csv` gives each encounter's saved clock interval, all three speeds, sensitivity limits and rejection/quality flags; `sites.csv` summarizes locations. `plots/` contains accepted encounter diagnostics; `timestamp_audit.json` and `timestamps/` contain timing evidence; `config.json` records assumptions. `status.json` and `cyclists.csv` update after each encounter.

To change assumptions without editing code, invoke `python code/speed_analysis_pass.py --videos PATH --out NEW_FOLDER --click-sigma-px 3 --scale-fraction 0.15 --simulations 500`. A new output folder is required. Wheel-size/road-marking calibration and measured University endpoint confirmation remain outside this pass.


<a id="workflow-5"></a>
## SPEED_PLAN_RUN.md
Original location: `docs/runs/SPEED_PLAN_RUN.md`.

> Reproduction guide for previously completed work. Start with [current results](../manual/README.md) and [current tasks](../README.md); no resubmission is required for repository cleanup.

# Latest one-pass speed plan

Use this instead of submitting the earlier `speed_analysis_pass.slurm` again. Existing detector jobs can continue. This CPU job runs robust manual trajectory estimation, packet timestamp auditing, sensitivity scenarios, plots, study-group distribution comparisons, wheel-candidate inspection crops and optional physical-scale checks.

```bash
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
mkdir -p logs
sbatch code/speed_plan.slurm
```

Push/pull changes first. Output is `exp_results/SPEED_PLAN_JOBID/RESULTS.md`. The first section links the main results in `trajectory/RESULTS.md`. Read that speed table first. Per-cyclist results, exact saved intervals, flags, plots and timing evidence remain under `trajectory/`. Results save incrementally there; `status.json` at the root marks completion of the full plan. No new detections, training, measurements or validation labels are invented.

A full local run is saved in [manual/speed_plan_20261027/RESULTS.md](../manual/speed_plan_20261027/RESULTS.md). No cluster rerun is necessary to read those results.

## Scale checks

`scale_checks/calibration_checks.csv` reports the existing car calibration and missing marking/wheel evidence separately for each annotated camera. The automatic wheel search only finds ellipse-like edges around saved tyre clicks; it does not establish that an ellipse is a wheel. The crops are optional research diagnostics, not a required new annotation task.

Actual marking and 3-D wheel fitting code is available through optional `--scale-evidence evidence.json` on `speed_plan.py`. It does not change any mph or fuse estimates automatically. Evidence uses camera names exactly as in `final_batch_export.json`:

```json
{
  "Camera name": {
    "markings": [
      {
        "image_endpoints": [[100, 200], [300, 250]],
        "length_metres": 3,
        "length_kind": "assumed_standard",
        "source": "REPLACE with the actual standard/measurement and feature identity"
      }
    ],
    "wheels": []
  }
}
```

These coordinates and length are an **illustration only**, not real evidence. Do not submit them as camera measurements. Marking endpoints must use the saved calibration image coordinate system. `length_kind` is `measured` or `assumed_standard`.

A wheel item requires: `outline_reviewed: true`, `image_undistorted: true`, `source`, `world_convention: "metres_Z_up"`, a matching 3×4 `projection_matrix`, `contact_pixel: [x,y]`, at least 12 `outline_pixels: [[x,y],...]`, and an explicit `diameter_prior_metres: [lower,upper]`. It fits a vertical 3-D circle with radius and heading to the reviewed outline, checks compatibility with the ground mapping, and returns diameter/scale ratios under that camera model. It is experimental and subject to wheel-type, projection and outline ambiguity. Ground homography alone is insufficient; current compact exports lack the required full projection. The fit returns missing/rejected evidence instead of estimating a made-up wheel diameter. Synthetic geometry checks are not real-world validation.

## Comparisons and limits

`study_group_comparisons.csv` contains study and video sample sizes, means, signed differences, and sampling-only bootstrap bounds using both samples. It omits intervals with fewer than two video cyclists; small-sample intervals remain fragile. It is not matched-person MAE and does not account for unknown scale bias or differing recording sessions. The prior HiPerGator column in the trajectory report is still historical context while the same-video GPU batch is pending.

Sensitivity defaults remain illustrative: 3-pixel clicking SD and uniform ±15% shared camera-scale variation, 500 draws. The range is not calibrated accuracy. The timing audit concerns re-encoded review clips, not all original hourly videos.

ByteTrack is already part of the detector with ID stitching. BoT-SORT/OC-SORT experiments, a trained wheel-keypoint network, automatic camera geolocation, and complete reproductions of the other research papers are **not implemented in this job**. They require separate development/data, not a different speed formula. Existing map-landmark fitting is in `code/map_calibration.py`; University still needs confirmation that the map endpoints match the video.

