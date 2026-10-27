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
