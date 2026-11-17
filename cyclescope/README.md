# CycleScope

Review UI for this repository's RT-DETR + X-CLIP pipeline. The old `backend/`
implementation and its duplicate speed/near-miss formulas have been removed.
`service/` provides storage and HTTP transport; scientific calculations import the
existing repository modules directly.

Run from the repository root (existing environment):

```sh
bash cyclescope/start.sh
```

The launcher starts missing services and reuses matching running services on
8000/5173. It reports unrelated port conflicts. For a fresh checkout, first run:

```sh
python3 -m venv cyclescope/.venv
cyclescope/.venv/bin/python -m pip install -r cyclescope/requirements.txt
(cd cyclescope/frontend && npm install)
```

Restore the checkpoint using [HiPerGator setup](HIPERGATOR_NEXT_STEPS.md).
The default checkpoint path is `vision3/runs/detect/finetune_runs/rtdetr_v3/weights/best.pt`;
`DETECTOR_WEIGHTS` can override it.

Open http://localhost:5173. `PIPELINE_PYTHON` can point to your existing inference
Python environment with Torch, Transformers, Supervision, Ultralytics and cached
`microsoft/xclip-base-patch32` assets. Inference logs and the exact command are
saved in each video's `inference/` directory. Missing weights cause an explicit
failure, never a fallback to another detector. The fine-tuned weights have now been downloaded to their default local path.

- **Dashboard:** the full-archive inventory adds 179 site/view/device groups,
  9,085 videos and 9,057.34 measured playback hours across 2019–2026. Study counts
  join by the saved site/date/device mapping; the nine available same-video speed
  comparisons join through the camera mapping. One table shows counts, hours,
  devices, dates, speed samples and missing-data reasons. Multi-year groups retain
  combined duration rather than inventing per-year hours. Dates come from the
  partial saved archive listing, not the filesystem modification dates. Recording
  and date selectors guide local uploads; remote archive entries do not stream.
- **Detection:** calls `vision3/best/test_colonial/code/xclip_overlay_v19_colonial.py`
  directly, with the reference profile parsed from `run_batch4.sh` (static5).
  This retains SAHI, tracking, stitching, X-CLIP and detector/motion/static rules.
  Supply the video recording start to enable the existing time-of-day rules;
  without it, night-specific and short-night rules are disabled explicitly.
  The original upload is used for inference, not its browser transcode.
- **Speed:** calls `metric_trajectory_speed.estimate` with its existing defaults:
  at least 1.5 seconds of continuous calibrated observation, a one-second local
  fit window and no coasted samples. Every object row shows its speed or N/A
  with a reason. Explicit manual keyframes are observations; display interpolation
  never becomes measurement evidence. Speeds are estimates, not validated truth.
- **Interactions:** calls `clearance_metrics.prepare`, `road_axis` and
  `pair_metrics`, including footprint clearance, collision TTC and sampled PET.
  The existing routine needs two moving vehicle tracks to establish the road axis.
  Missing eligibility is shown, not replaced with invented metrics. Candidates
  are not automatically labelled near misses; the repository adopts no automatic
  threshold. Confirm/reject decisions remain available.
- **Calibration:** four or more arbitrary paired image/world landmarks in metres,
  fit with the same `findHomography` approach as `metric_trajectory_speed.run_source`.
  Add unlimited named facility polygons with three or more vertices. Regions label
  facilities; they do not establish metric scale or independent ground planes.
  Raised/sloped surfaces require separate measured calibration before trusting speed.
- **Corrections:** drawing creates the chosen class. Extending a selected manual
  track is an explicit checkbox, with the track and class shown. Edits recompute
  results through the repository routines. Legacy standalone detections have no
  eligible scientific observations; reprocess an unedited legacy video or upload
  a new copy when review edits must be preserved.
- **Deletion:** previous videos can be deleted with an inline confirmation. This
  removes only that upload and its job directory; repository evidence stays intact.
  Active jobs cannot be deleted.

Data defaults to `cyclescope/data/jobs` independently of the launch directory.
Override with `DATA_DIR` for an isolated review/test session. Storage is local JSON,
with serialized mutations; this development service has no authentication.

Build: `cd cyclescope/frontend && npm run build`.
Tests: `cyclescope/.venv/bin/python -m unittest discover -s cyclescope/tests`.

Transfers and missing inputs: [HIPERGATOR_NEXT_STEPS.md](HIPERGATOR_NEXT_STEPS.md).

Review tabs, object actions, interaction decisions and summary downloads remain above separately scrolling content. Calibration lists clicked image coordinates in pixels separately from measured ground coordinates in metres; named regions retain distinct saved colors.


### Clip selection, batches and camera clocks

Choose multiple local videos, preview each file and set its start/end with sliders.
Presets select the first 10 minutes or last 15 minutes (clamped to shorter files).
The service validates against the actual probed duration, decodes the selected
interval and resets the review timeline to zero. Original-file offsets are retained
in job metadata and exports. This selection needs no real recording-clock time.

A filename can offer an inferred session/chunk clock hint. It is never enabled
silently. The optional recording-clock disclosure requires reviewer confirmation;
creation metadata is not treated as verified capture time. The selected clip's
start offset is added to a supplied clock before applying day/night rules. Missing
clock time disables those rules, not ordinary clip selection.

Uploads enqueue independently and a bounded executor processes two jobs concurrently
by default. Set `PROCESSING_WORKERS=1` through `4` before starting the API to change
that limit. Use one API process; each process otherwise owns its own worker pool.
The dashboard polls the job list so a batch need not wait on an individual review
page. This is an in-process development queue, not a durable cluster scheduler.

### Reviewed speeds and interaction evidence

Select an object and open **Edit speed** to save a nonnegative mph value and a
measurement/reason. A reviewed override is labelled in the object list. Calculated
speeds, override history and reasons remain separately available in JSON/CSV.
Restore calculated speed removes the active override. Overrides never alter the
observed trajectory, TTC/PET or clearance calculations. Reprocessing reviewed
objects requires a new upload so review values cannot migrate to unrelated IDs.

The interaction panel explains center distance, assumed-footprint clearance,
collision TTC and sampled occupancy PET, with missing eligibility reasons and
explicit confirm/reject status. These are screening/review candidates, not
validated automatic near-miss labels.

Ground X/Y are measured metre coordinates in a reviewer-chosen ground coordinate
system, not image pixels. The first landmark defaults to the arbitrary origin
(0,0); other coordinates need measurements and are not guessed. **Save regions
only** works without metric calibration and does not produce metric speeds.

### Dashboard source audit

**Only locations with bicycle counts** excludes unavailable counts and keeps valid
zeros. The dashboard exposes source SHA-256 fingerprints and uncertain mapping
notes. Run `cyclescope/.venv/bin/python cyclescope/scripts/audit_dashboard.py` to
rebuild `DASHBOARD_DATA_AUDIT.json`. It checks every inventory video/hour/year value,
41 mapped study sessions, all nine speed comparisons and all 14 workbook references against saved source files.
This is source consistency checking; it does not independently validate the original
study measurements or remote video duration audit.

Browser regression checks use an isolated synthetic-inference server:
`cyclescope/.venv/bin/python cyclescope/tests/browser_server.py` (port 8001), Vite on
5173, then `NODE_PATH=/path/to/playwright/node_modules node cyclescope/tests/browser.cjs`.
Synthetic inference exists only in that test server and is never used by the app.

## Runtime repair and workspace update

Run `bash cyclescope/start.sh` to reuse the existing API/frontend or start them on
8000/5173 without duplicate listeners. Failed uploads have a retry action. The
adapter always supplies `--chunk-index 1` for upload/clip filenames, prevents
unrelated automatic Colonial truth loading, and saves unbuffered inference logs.
Dependencies use Supervision 0.25.0 (the required ByteTrack API) and a single
OpenCV 4.11 distribution. Optional PyAV is not used by this OpenCV-frame pipeline.

The workspace now distinguishes all **14 workbook reference locations** from the
**nine saved same-video comparisons**. The workbook mean is computed from the
existing exact-unit `recomputed_mph` records; prior source-conversion means remain
in each comparison's evidence details. Camera aliases remain explicitly unverified.
Silver Star is a reference-only row with no invented year/hours. Existing inventory
totals still cover 179 archive groups; the reference-only row is additional.

Reviewed speed saves show an object-specific confirmation, survive object switches
and reloads, and retain original computations. Source notes are optional in the UI;
if omitted, the audit explicitly records that no measurement source was specified.

The local **Ask CycleScope** guide provides fixed, source-backed workflow answers
and links to project notes. It makes no external model requests and does not
generate missing results. Unknown questions get an explicit unavailable answer.

`INFERENCE_SMOKE_TEST.json` records an actual 36-frame local RT-DETR/X-CLIP run,
not a synthetic test. It passed on CPU and imported four tracks. Runtime was
411.1 seconds; longer inference is better done on the existing HiPerGator GPU
workflow. See `HIPERGATOR_NEXT_STEPS.md` for which source files/calibrations are
still needed and read-only transfer commands. No new training or inventory audit
is required for these application fixes.
