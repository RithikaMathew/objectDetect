# Project handoff — November 16, 2026

## Current status

CycleScope uses the repository RT-DETR + X-CLIP pipeline and original speed and
interaction routines. Local weights and X-CLIP assets are available. The downloaded
Colonial calibration is preserved with provenance, but its learned scale is not
independently validated. **No new HiPerGator job is required for current app use.**

## Start and use CycleScope

From `/Users/rithika/Desktop/objectDetect`, run `bash cyclescope/start.sh` and open
http://localhost:5173. The launcher starts missing services and reuses running
CycleScope services on API port 8000 and frontend port 5173. Stop manually started
services in their terminals before restarting after code/dependency updates.
An unrelated port occupant is reported, not terminated.

[Application workflow](cyclescope/README.md) documents clip selection, batch uploads,
review, exports and setup. [HiPerGator transfers and remaining inputs](cyclescope/HIPERGATOR_NEXT_STEPS.md)
contains commands with GatorLink `rmathew1`. Dependencies, model weights, uploads
and build outputs are excluded from Git; a fresh checkout needs setup and weights.

## Latest application results

- Removed the duplicate backend; HTTP/storage service imports the existing scientific routines.
- Fixed upload inference with explicit `--chunk-index 1`, preserved reference rules,
  and prevented unrelated automatic Colonial truth loading. Runtime pins Supervision
  0.25.0 and one OpenCV 4.11 distribution; optional PyAV is unnecessary.
- Dashboard uses 179 archive groups, 9,085 videos and 9,057.33588141 summed playback
  hours across 2019–2026. It joins 41 study mappings / 5,053 bicycle counts, nine
  saved same-video speed comparisons and all 14 workbook reference locations.
  Silver Star has an additional reference-only row. Unknowns stay blank with reasons;
  combined-year hours are not invented per year. Camera aliases remain unverified.
- Review controls stay visible above scrolling lists. Selected drawing classes,
  video deletion, per-object speed edits, calculated-speed restoration and audit
  exports are supported. Overrides do not change trajectory interaction metrics.
- Clip sliders/presets select elapsed video intervals; the optional confirmed camera
  clock enables time-of-day rules. Two local processing workers are the default.
- Calibration supports arbitrary paired landmarks and separately colored named
  facility polygons. Regions label facilities; image clicks do not create metres.
- Ask CycleScope is a fixed source-backed local guide, not an external LLM.

`cyclescope/INFERENCE_SMOKE_TEST.json` records a real 36-frame CPU inference:
411.1 seconds, four imported tracks, no duplicate Objective-C warning. This validates
execution only, not study counts, full-video performance or speed accuracy. Longer
inference belongs on the existing HiPerGator GPU workflow. The prior verification
record is 19 CycleScope Python tests, frontend build, isolated Chrome workflows
and dashboard source audit. Cleanup verification also passed 19 CycleScope tests, 48 research Python tests,
10 JavaScript calculation tests, the frontend build, dashboard audit and
`git diff --check`. No Git candidate file exceeds 50 MB.

## Current scientific results and corrected interpretation

The latest offline package is [reports/near_miss_next/README.md](reports/near_miss_next/README.md).
Use its [results](reports/near_miss_next/20261110_v1/PROFESSOR_RESULTS_UPDATED.md),
[methods](reports/near_miss_next/20261110_v1/METHODS_AND_THRESHOLDS.md),
[review instructions](reports/near_miss_next/20261110_v1/RUN_AND_REVIEW.md) and
[validation record](reports/near_miss_next/20261110_v1/VALIDATION.md).

- Three unique reviewed interactions: two cyclist passes and one close pedestrian crossing.
- Selected cyclist image gaps: 6 px and 20 px, each from three annotated frames.
  These are neither continuous minima nor physical lateral clearance.
- Pedestrian conditional TTC: 0.371804 s; conditional CV sensitivity range
  0.347697–0.398111 s. It depends on an unvalidated reconstruction/footprint model.
- **0.294117647 is 5/17 observation coverage, not PET.** Earlier handoff/report
  claims calling it PET are superseded. Occupancy-based PET remains unavailable
  without supported entry/exit boundaries in the same physical conflict zone.
- No validated metre clearance or confirmed near miss under a validated protocol
  is established. This does not establish absence of near misses or a population rate.
- The wheel labelled as a car remains an excluded false detection. Repeated detector
  and smoothing scenarios are not separate physical encounters.

The November 10 validation record reports 48 Python tests, 10 JavaScript calculation
tests, nine offline browser checks and 216 unchanged evidence hashes. It is a saved
verification record, not a claim of newly rerunning browser analysis during cleanup.
Original returned reports remain historical evidence and may contain superseded interpretations.

[Manual speed results](manual/README.md) retain 18 same-video clips across nine cameras:
35 study / 32 automatic / 30 manual counts, with 29 eligible manual speed encounters.
Manual and automatic speeds share a learned camera mapping; agreement does not
independently validate scale. Workbook references use a separate sample and must
not be treated as person-level truth or used to fit camera scale.

## Downloaded calibration and remaining inputs

`cyclescope/data/calibrations/colonial_north/calibration.json` was downloaded from
the `ADAPTIVE_SPEED_manualmatch_20261026_233356/s03_colonial_north` run.
Adjacent `source.json` records its remote path and checksum. It contains H and a
support hull from 28 car tracks / 458 boxes. It explicitly labels learned scale
unvalidated and sidewalk transfer unverified. Image dimensions and measured
landmark pairs are absent. Copying it does not automatically apply it in the UI.

No retraining, detector sweep or repeated inventory audit is needed now. Retrieve
only selected source videos and their matching camera/resolution calibration and
run provenance when needed. Long clips can use the existing GPU workflow. A
per-video duration export is only needed to resolve combined-year hour splits.
Physical metre clearance still requires defensible lateral geometry and visible
object-edge evidence. Targeted pedestrian occupancy review may support PET; if
occlusion prevents it, keep PET unavailable or bounded with its assumptions.

## Repository cleanup and working preferences

The November 16 cleanup consolidated transfer instructions, removed obsolete root
task prompts, the transient terminal transcript and an empty root npm lockfile,
and excluded local dependency/build/upload directories from Git. Per-experiment
results, original workbooks, annotations, source data and scientific programs are
retained because they document distinct evidence. See
[cleanup manifest](reports/maintenance/cleanup_20261116.json). Removed files and
pre-edit summaries are backed up outside the repository at
`/Users/rithika/Desktop/objectDetect-cleanup-backup-20261116`.

Pre-existing code edits and deleted presentations were not reverted or staged.
No commit or push was performed. Keep video experiments at most 15 minutes,
prefer shorter clips, and do not contact MetroPlan. Prefer autonomous follow-through
and concise explanations; preserve original inputs and evidence.
