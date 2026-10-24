# October 23 tasks — start here

This implements the new root todo.md request. Earlier “no full-day scaling” instructions describe the prior scope; the owner has now asked for broader study-video processing. No new GPU jobs have been submitted from this Mac. Do not rerun the completed October20batch.

## What is done

- Prepared a fixed-reference inventory/submit/report tool: `code/study_batch.py`.
- Local archive inventory: **1,919 unique files / 41 site/date pairs**, about1,919video-hours IF each file is one hour. Colonial North has48files (~48hours); all other recordings total1,871 nominal hours. Actual durations are not available on this Mac.
- Nominal processing estimate at2.8 GPU-hours/video-hour:5,373 GPU-hours total, ~112 days at two continuously available GPUs, excluding queues. Other-than-Colonial-North:5,239GPU-hours. These extrapolations are not throughput guarantees.
- One full Colonial North hourly source is the default pilot (chunk013, inferred12:00–13:00). Previously labelled clips total one hour across four separate windows; they are not the full recording.
- Added partial-track metric speed estimation after scene calibration. Two-line crossings are no longer required; real scene scale still is.
- Added conflict-area time-gap review and optional vehicle trajectory export for new runs. This is not confirmed near-miss detection or footprint PET/TTC.
- Wrote `reports/methodology/object_detection_study_20261023.tex`, including existing results, new workflow, limitations, research references and proposed multi-agent architecture. Compiled PDF: `output/pdf/object_detection_study_20261023.pdf`.

## Recommended next pilot: Pine Hills BL E

The owner asked for a shorter recording and an adjustable zone tool. Pine Hills BL E is the shortest matched recording: **25 nominal hourly files**, compared with Pleasant Hill Path31 and West Orange Path37. The count folder has road names/dates/directions but **no explicit camera coordinates found**; all 41count workbooks have blank Site Code fields. West Orange/Park in the speed workbook is a location clue, not a verified camera. See exp_results/study_inventory_20261023/SITE_SELECTION.md.

We do not need to process the full25 hours: start with one noon source hour. Exact GPS is not needed to draw lanes. Metric speed still needs identified image/map correspondences.

## First cluster commands

Push the repository changes from your Mac, then on HiPerGator:

```bash
cd /orange/xiangyan/rithika/vision
git pull --ff-only origin main
cd vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate

python code/study_batch.py inventory --probe \
  --out exp_results/study_inventory_live_20261023

python code/site_zone_setup.py \
  --inventory exp_results/study_inventory_live_20261023/inventory.csv \
  --site 'Pine Hills BL E' --out exp_results/pine_hills_zone_editor_oct23
```

Metadata probing is read-only apart from the new output folder; it opens each source and reads a frame, not the whole video. Missing files and unreadable metadata are listed. Change `--data-root` if videos are extracted somewhere other than `/orange/xiangyan/rithika/vision/pilot_clips`. Choose fresh output/tag names if these already exist. Submission is duplicate-guarded; if it fails partway, earlier jobs may already be running—read `logs/pine_hills_pilot_oct23/manifest.json`, do not blindly resubmit.

Download the entire `exp_results/pine_hills_zone_editor_oct23/` folder and open `index.html`. Choose the camera, click polygon vertices for road, bike lane, sidewalk, path and grass as applicable. Add another region for a separate area of the same type. Empty categories are allowed; finish or clear partial polygons. Enter your name, confirm the outlines, and export JSON. The editor autosaves drawings, supports importing a previous JSON, and shows backup JSON if downloads are blocked. Each page embeds its image, so no external frame link breaks.

Copy the exported JSON back to HiPerGator into `vision3/best/test_colonial/zones/study_20261023/`, keeping the filename. Then submit:

```bash
python code/study_batch.py submit \
  --inventory exp_results/study_inventory_live_20261023/inventory.csv \
  --scope pilot --site 'Pine Hills BL E' --pilot-chunk 13 \
  --zones-dir zones/study_20261023 --require-zones \
  --tag pine_hills_pilot_oct23 --go
```

This is one full hourly source, not the entire Pine Hills recording. Omit `--go` for a preview. For Colonial instead, omit `--site` and use another fresh tag. Read `exp_results/STUDY_pine_hills_pilot_oct23/RESULTS.md` and `outputs.csv` after completion. `outputs.csv` gives exact annotated filenames and the saved count/bin files. Check the full pilot video for missed cyclists, false detections, ID jumps and boundary fragments. Inspect actual runtime and memory via Slurm before scaling. No new truth campaign is required merely to run this pilot.

## Count and lane-use records for every processed source

Each source exports:

- `per_track_lane_use.csv`: source path, site, person/vehicle namespace, track ID, predicted user type, counted/rejected status, dominant facility, lane observation fractions, provisional visited facilities,15-minute midpoint bin and identity/zone quality flags.
- `counts_by_user_lane.csv`: one dominant-facility allocation per counted track.
- `counts_15min_by_user_lane.csv`: the same breakdown by15-minute bin.
- Existing original track/count CSVs and the structured run log; optional vehicle trajectories are enabled for study jobs.

The final study report combines sources into `all_tracks.csv`, `counts_by_site_user_lane.csv`, and `counts_15min_by_user_lane.csv`. Car/bus/truck/other vehicle classes remain separate where the model supplies them; the cyclist model category can include motorcycles/e-scooters and must not be advertised as independently verified mode truth. Lane counts are predicted track counts, not people verified across all source files. A person can move between facilities: fractions/visited-facility memberships retain this information, but they must not be summed as unique people. Dominance below70% or ambiguous/out-of-zone evidence yields uncertain; no zone file yields unassigned. Boundary fragments and identity switches require review.

Road-user lane classification is a **postprocessing step** using the user-marked zones. It does not change detection/count filtering on the new camera or pretend to have model accuracy. Colonial retains its existing inference masks. Rejected tracks remain in the per-track ledger but do not inflate counted totals. Original vehicle totals are retained even if historical vehicle histories are unavailable.

To build editors for all matched cameras, omit `--site` from the zone-setup command and download that whole editor folder. Save all exported JSONs in the same zones directory. Pass `--zones-dir ... --require-zones` to the study submit command when every selected camera must have marked lane areas.

If you change zones after inference, reclassify the saved tracks **without another GPU run** into a fresh output folder:

```bash
python code/study_batch.py lanes \
  --manifest logs/pine_hills_pilot_oct23/manifest.json \
  --zones-dir zones/study_20261023 \
  --out exp_results/pine_hills_lane_update_oct23
```

## All other study recordings

The one-hour pilot is recommended first. The full batch is prepared, not executed. Preview selection:

```bash
python code/study_batch.py submit \
  --inventory exp_results/study_inventory_live_20261023/inventory.csv \
  --scope all --exclude-site 'Colonial North' --tag study_others_oct23 \
  --zones-dir zones/study_20261023 --require-zones
```

Add `--go` to submit after sources/clocks are resolved. Use `--scope colonial` for all Colonial North files, `--scope all` without exclusion for all 41mapped site-date pairs, or `--scope all --site 'Colonial South'` for a specific study recording. At most two GPU jobs run concurrently by default; this bounds concurrency, not total cost. Jobs are source-file-sized, with a dependent final CPU report. Queuing/job-count limits can still stop a very large submission; the manifest preserves every returned job ID.

**62 multipart filenames do not encode a reliable source-start hour.** They are explicitly blocked, not assigned invented times or silently excluded. The inventory writes `clock_overrides_needed.csv`. Confirm each source's embedded first-frame clock and fill clock (`YYYY-MM-DD HH:MM:SS`), reviewer and evidence. Supply the completed CSV using `--clock-overrides /path/to/clocks.csv`. Plain hourly filenames use inferred clocks, which also require confirmation before scientific time-based comparisons. Source durations may overlap or contain gaps; verify continuous coverage and avoid double counting at file boundaries.

The mapping table's1,967 chunk sum is inflated relative to1,919 unique archived paths (Rinehart Sidewalk 96 versus 48). Lower-score mappings also need a camera/date check. Missing video extraction and unresolved mappings are not fixed by inference code. Site workbooks provide aggregate counts, not per-person truth; compare only aligned camera/channel/date/time coverage. Header GT is left unlabelled when valid person-level labels are unavailable. Other cameras do not inherit Colonial lane polygons; their own marked polygons drive the lane-use report. Study results are not automatically accuracy or unseen-site validation.

## Speed: partial trajectories with real ground scale

Current image motion is in pixels/second or body heights/second. A partial track cannot determine absolute mph without ground scale. The earlier35ft/30ftlengths belong to unidentified study segments, not the owner's drawn lane ends.

Need the exact Colonial camera/map location, then at least six identifiable persistent ground landmarks: four or more distributed fit points and at least two independent check points. All map/survey ground coordinates must share one local origin and axes, in metres. Distances from a ruler alone do not establish arbitrary 2D point coordinates. Google Maps measurements can support an estimate, not survey-grade precision. Match the historical road layout and camera view. Include a source URL/date, landmark descriptions and correspondence evidence. For fisheye footage, first establish a lens correction; a single planar mapping cannot remove lens distortion.

Template: `data/reviews/calibration/landmarks.template.csv`. Work on a copy; fill image_x/image_y in the720x480reference and local east_metres/north_metres, role fit/check, and evidence. Then:

```bash
python code/map_calibration.py \
  --landmarks /path/to/completed_landmarks.csv \
  --reviewer Rithika --source 'Map or survey reference, date and landmark evidence' \
  --out /path/to/colonial_map_estimate.json

python code/metric_trajectory_speed.py \
  --people exp_results/labelled_validation_20261020/people_lane_speed.csv \
  --calibration /path/to/colonial_map_estimate.json \
  --out exp_results/colonial_partial_track_speed.csv
```

For a new study road, fit `map_calibration.py` with `--site 'Pine Hills BL E' --date 2019-08-28` and that camera's actual reference size. Then use `metric_trajectory_speed.py --run-log /path/to/new_source_run_log.json --site 'Pine Hills BL E' --calibration /path/to/its_calibration.json --out /path/to/new_speed_estimates.csv`. This supports its counted pedestrians/cyclists and observed counted vehicles, while retaining unverified identity status. Do not reuse Colonial calibration.

These CPU commands are for **after** real landmark correspondence is supplied; the blank template is intentionally unusable. They estimate speed only for the existing seven bicycle truth candidates, preserve identity status, avoid extrapolation outside the landmark hull, reject long gaps/coasted positions, and require1.5-second continuous segments. Local one-second linear velocity fits produce median speed and dispersion. No model's counting/motion feature has been changed to these estimates.

The calibration report includes independent landmark residuals; low residuals are not proof of accurate speeds. Human identity confirmation and independent known-speed matches are still needed for speed validation. No mph has been calculated from invented distances or Excel means. Matching Excel records by nearest predicted speed is circular and prohibited.

## Conflict review without mph

A timing-based candidate method can start before mph validation: how soon does another road user enter the same small conflict area? FHWA defines PET around a common conflict location; this code is a simpler **ground-point/zone proxy**, not exact footprint PET or TTC.

Create a JSON with `ref_size`, a small camera-specific `polygon`, `reviewer` and `source`. A whole sidewalk/bike-lane polygon is too broad. Use observed entries/exits and visually check path overlap. Example fields (coordinates must be supplied, never guessed):

```json
{"ref_size":[720,480],"polygon":[],"reviewer":"Rithika","source":"Describe the observed conflict area and camera"}
```

For one source with the same frame origin and dimensions:

```bash
python code/conflict_zone_review.py \
  --people /path/to/source_trajectories.csv \
  --vehicles /path/to/source_vehicle_trajectories.csv \
  --zone /path/to/reviewed_conflict_zone.json \
  --fps 29.97 --frame-size 720x480 \
  --out exp_results/conflict_candidates_review
```

Use the actual FPS/resolution from that source's run log. Outputs are frame1-relative times, not necessarily clip-player times; account for the processed clip start. The optional3-second review window is not a validated safety cutoff. Simultaneous point occupancy is a separate flag, not proof of collision. Censored visits and missing intervals are rejected. Vehicle and person ID namespaces remain separate.

Historical files do not contain complete vehicle trajectories, so cyclist-car events cannot be recovered from them alone. New study jobs enable `EXPORT_VEHICLE_TRAJECTORIES=1`, an optional exporter in v19 that leaves detection/count decisions unchanged. Vehicle exports contain observed tracked vehicles, which can still miss stationary objects or occluded traffic. End-to-end GPU export and real conflict review are pending. Candidate counts must not be called confirmed near-miss counts.

## Multi-agent suggestions

Use agents to organize evidence, not invent geometry:

1. Data/coverage agent: verify camera, dates, channels and clock.
2. Perception-quality agent: flag occlusion, track fragments and label disagreement.
3. Calibration agent: check landmark evidence and held-out errors; stop metric claims without scale.
4. Deterministic conflict tool: calculate measures and retrieve exact source intervals.
5. Skeptical review agent: challenge ID switches and spatially unrelated paths, then send evidence to a human adjudicator.

Keep structured provenance for every event: video/frame interval, IDs, tool outputs, calibration version, uncertainty flags and reviewer. Multiple agents agreeing is not independent validation. This architecture is proposed, not an implemented or benchmarked agent system.

Research sources: [FHWA SSAM definitions](https://www.fhwa.dot.gov/publications/research/safety/08051/02.cfm), [OpenCV homography](https://docs.opencv.org/3.4.19/d9/dab/tutorial_homography.html), [BMVC traffic calibration paper](https://www.bmva-archive.org.uk/bmvc/2014/papers/paper013/index.html), [Google Maps distance measurement](https://support.google.com/maps/answer/1628031?hl=en).


## Parallel CPU speed-readiness job (while Pine Hills inference runs)

Added `code/speed_readiness.py` and `code/speed_readiness.slurm`. The full speed workbook was scanned locally:375deduplicated reference rows,23Colonial, no Pine-named street rows. This is reference availability, not new measured model speeds. An unknown street alias is not ruled out.

After push/pull, submit independently from cluster `vision3/best/test_colonial`:

```bash
mkdir -p logs
sbatch code/speed_readiness.slurm
```

This job requests2CPUs/4GB/30minutes and no GPU. It reads the original ZIP central directory and selected small JPEG/CUT companion files for41study cameras, plus ffprobe location metadata for any corresponding extracted noon videos. It does not extract whole videos, alter the detection run, communicate externally or infer physical track speeds. Candidate GPS/sidecar clues must be checked against the camera view; a camera coordinate alone is not ground-plane calibration.

The output folder is `exp_results/speed_readiness_JOBID/` (replace JOBID with the returned Slurm ID). Read `RESULTS.md`, `GPS_candidates.csv`, `camera_metadata.json`, and `reference_summary.csv`. Zero metadata clues is a possible legitimate outcome, not calibrated speed. Sampled sidecars lacking GPS do not prove the original camera had no location data. All source-speed rows/source cells are retained for future independently matched validation.

Local workbook-only report: `exp_results/speed_reference_readiness_20261023/RESULTS.md`; no new cluster results are claimed. Four new metadata/reference tests pass.


## Manual pilot reference prepared in parallel

Already run locally: `exp_results/pine_hills_manual_reference_20261023/RESULTS.md` plus raw15-minute channel counts, grouped user/side/facility counts, and worksheet coverage. For2019-08-28 12:00–13:00 the workbook records NBcyclists0bike-lane/1sidewalk, SBcyclists4bike-lane/0sidewalk, NBpedestrians0/0. SBpedestrian channels are absent, not zero. Keep raw sides separate until the actual camera side is established. Model-vs-manual comparison is pending detection results and that correspondence.

The pedestrian sheet has99quarter-hour rows (throughAug29 00:30), while bicycles has192(two days). This is a real coverage difference; do not compare full-file totals as if coverage were identical. A count total is not per-person identity/detection accuracy.

To independently regenerate on cluster after push/pull, no sbatch or GPU is needed; use a fresh output folder:

```bash
python code/study_count_reference.py \
  --workbook '/orange/xiangyan/rithika/vision/Bike Lane Study Counts/Pine_Hills_BL_E_690212_08-28-2019.xls' \
  --start '2019-08-28 12:00:00' --end '2019-08-28 13:00:00' \
  --out exp_results/pine_hills_manual_reference_repeat
```

Do not repeat this merely to occupy the queue; the saved result is ready. The useful pending work is reviewing the pilot output and returned calibration metadata.


## Speed-specific alternative: University SW Speed

Owner supplied camera_metadata.json; inspected all41camera entries locally. No readable location clues were found in sampled CUT previews (binary); explicit GPS remains0. Most sources were not extracted at the time of the audit. Raw metadata preserved at data/reviews/speed_readiness_47393224/camera_metadata.json.

A stronger speed candidate than Pine Hills is the purpose-labelled **SW Speed University** recording (September25,2019). The speed workbook contains78University sidewalk records, all55ft. This street-name match and folder label are promising, but do not establish which recording/person/segment each speed belongs to. No existing video has independently validated model mph.

Prepared one source hour08:00–09:00, chunk009. Selection uses the largest manual first-day daylight hourly cyclist count (11), earliest tie among08:00/14:00/16:00, without detector outputs. Manual data is North Sidewalk;11cyclist observations. Event-enriched selection is not an unbiased validation set. Reference records, empty person-link template and manual-hour counts: exp_results/university_speed_candidate_20261023/.

After push/pull, on HiPerGator with the environment active:

```bash
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
bash code/prepare_university_speed.sh
```

This extracts only one source file (~282MBlisted compressed/file size), probes metadata, isolates that hour's inventory, and builds a real-frame editor/manual-reference folder. No GPU or model job is submitted. It prints a fresh folder exp_results/university_speed_prepare_XXXXXX/; download its entire zone_editor subfolder. Open index.html -> University SW Speed. Send the downloaded folder/local path for image inspection and check the expected08:05clock. Endpoints, date/person links or alternate metric landmarks must be identified before claiming mph; marking area polygons alone is not speed calibration. Pine Hills detection can continue independently.


## October 24: map-free speed experiments

Run only after pushing/pulling the new code. From HiPerGator test_colonial:

```bash
sbatch code/speed_research.slurm
```

This requests one GPU for up to4hours and processes sampled original Colonial daytime frames for car-based scale estimation; it does not rerun the whole object-count study. Results: `exp_results/colonial_speed_research_JOBID/RESULTS.md`. Download the entire result folder. Dependencies include working torch/torchvision, scipy, numpy, cv2 and Git/network access for pinned author code and MaskRCNN weights. Missing dependencies/assets are reported per method, not hidden or substituted. Original raw Colonial chunk013 must exist at the configured path.

Implemented: ICCV2021 author pretrained transformer adapter (car instance masks, simple IoU association, seeded fitting); paper-inspired pedestrian head/feet average-height optimization. Local synthetic projection/recovery/input-refusal tests pass; author pretrained network loaded and inference smoke-tested. No real ICCV camera calibration executed locally: torchvision absent and original raw clip required. Existing saved Colonial data provides only1qualifying independent pedestrian track versus20required, so the local height experiment declined calibration. Three other researched methods remain NOT_IMPLEMENTED_MISSING_COMPONENTS (BMVC2014 full3D-box pipeline, Sochor2017 CAD/render assets,2026trained36-keypoint model); this command is not a claim to run all five papers.

`method_status.json` distinguishes completion/failures; `all_speed_estimates.csv` only exists when experiments yield rows. `descriptive_group_comparison.csv` compares available predicted group means to source workbook group means, explicitly not accuracy/ranking. No scale fitting or automatic winner selection uses the workbook. Distinct source people/times prevent matched validation; road-to-sidewalk plane transfer remains unverified. Geometry checks alone do not establish physical accuracy. No new Slurm job submitted by Codex.


October24 owner clarification: choose a method close to study speeds for exploratory use, not necessarily most accurate. Runner now outputs pedestrian AND bicyclist partial-track estimates from existing labelled truth candidates; car detections only estimate camera scale, no car-speed output. Workbook375speed rows across14street labels are bicycle references, not pedestrian reference speeds. `exploratory_closeness_ranking.csv` ranks available geometry-check-passing methods by absolute difference from study mean, per facility and using the same candidate set across competing methods; single-method output explicitly not a competition. No ranking when no valid estimates. This selection does not establish metric accuracy. The same one sbatch command runs the two implemented experiments and records remaining three as missing components; it does NOT implement all five. No fresh calibration job has run here.


Latest October24 scope (supersedes earlier pedestrian-output instructions): owner requests BICYCLIST SPEED OUTPUTS ONLY. `speed_research.py` now excludes pedestrian and motorcycle speed results. Calibration may still use car size or pedestrian height. Job also includes saved University manual A/B method and compares8.13mph to78University sidewalk study values (mean9.49mph; difference−1.36mph). One-person versus separate-group descriptive comparison, not matched validation. Versioned manual input in data/reviews/speed/university_manual_crossing_20261024.json; no University reinference required. Root README now contains all14reference streets,375bicycle rows, facility types, method implementation statuses and professor-facing interpretation. Existing sbatch command unchanged; upload/pull new input/code before submitting. Job isColonial automatic experiments plusUniversity savedmanual comparison, NOTall14site processing orall5paperimplementations.

Dedicated professor-facing statistics: [SPEED_REFERENCE_README.md](SPEED_REFERENCE_README.md). Future speed outputs include the exact observed measurement intervals (date, source, clock times, clip seconds and frame ranges), not just the full-hour source label. Study-reference means are across measured cyclists, not per-hour/per15-minute values; reference observation clocks are unknown.


## Latest entry point: small multi-camera speed pilot (October24)

After pushing the latest code/docs/manual inputs and pulling on HiPerGator:

```bash
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
python code/submit_speed_pilot.py --go
```

This one submission command checks key Python dependencies before submitting two jobs: CPU candidate-camera screening followed by the prepared Colonial GPU calibration experiments (afterany dependency). It prints the bundle folder `exp_results/SPEED_PILOT_TAG/` and records both job IDs in submission.json. Partial submission keeps the first job ID; do not blindly submit again if the second submission fails.

CPU screening selects15candidate camera/date sessions spanning13of14reference street labels. Silver Star has no candidate in current mapped inventory. Aliases are tentative, not independently verified reference-camera matches. First recording day, nearest-noon daylight source is fixed before looking at detector results/speeds. It extracts only needed source files from original ZIP, with a5GB cap on new extraction, and makes45-second excerpts at source05:00,20:00,35:00 plus JPG frames. At most33.75minutes across all15cameras, not hours of viewing per camera. Missing/unreadable/budget-limited sources are explicit, not zero cyclists. A resolution/sharpness table is a screening aid, not an accuracy ranking. No all-site detector/speed inference is performed in this stage.

Download the bundle after completion. Open camera_previews/index.html and speed_results/RESULTS.md. Review up to5first clearly visible bicycle encounters per usable camera, aiming for3where feasible; accept1–2with sample count disclosed. Inspect fixed intervals in chronological order, without selecting people whose estimated speeds happen to agree. Misses remain detection failures and cannot simply disappear from evaluation. No guarantee these short excerpts contain5cyclists; report fewer honestly. For later expansion choose additional intervals before inspecting their results. Prefer cameras with visible bicycles/ground contact and usable tracking, not just high pixel dimensions. Comparing model speed with separate street/facility study groups remains exploratory; cannot reconstruct hourly reference speeds from rows lacking clock times.

The GPU job still only attempts implemented Colonial methods and includes saved University manual timing; three full paper implementations/assets are pending. Screening other cameras does not automatically transfer Colonial calibration or zones. This bundle replaces the need to submit a separate screening command plus a separate speed command; do not submit the older direct speed job as well for the same purpose.4screening tests (including real synthetic-video extraction),8speed research tests and9study extension tests pass. Cluster job performance/real camera calibration remains untested here.


## Preview recovery after job47544655 (October24)

Original bundle: exp_results/SPEED_PILOT_20261024_183520. CPU job47544655 extracted2,931,198,701bytes but generated0/15previews because ffmpeg was absent fromPATH. That is an environment dependency failure, not bad camera quality. Speed job47544658 is separate; do not submit the full bundle again for preview recovery.

Push/pull the new preview_ffmpeg.py, retry_speed_previews.py, speed_site_screen.py and submit_speed_pilot.py. Activate yolo_env on the HiPerGator login node, then:

```bash
python code/retry_speed_previews.py exp_results/SPEED_PILOT_20261024_183520 --go
```

This resolves/checksFFmpeg withlibx264. If absent, installs the pinned imageio-ffmpeg0.6.0 wheel into ~/.cache/objectdetect/preview_runtime using pip --target (no changes to shared YOLO packages), then passes its absolute binary path to the CPU job. [Package source and bundled executable details](https://pypi.org/project/imageio-ffmpeg/0.6.0/). No GPU submission and no ZIP extraction. Original selected_sources.csv reused exactly; prior reports untouched. New output camera_previews_retry_TIMESTAMP under the same bundle, path and CPU jobID printed, manifest preview_retry_JOBID.json. Download that new directory when done and open index.html.

Future full submissions bootstrap/checkFFmpeg before job submission; workers also check before extraction and now exit with error if0previews, after retaining diagnostic reports. Per-camera encoder stderr appears in screening.csv/RESULTS.md. Seven screening/recovery tests, eight speed tests and nine study-extension tests pass locally. Cluster recovery still requires running above command; no retry submitted locally.

Preview retry47545063failed before processing because of a Python-version f-string quote incompatibility. Corrected and compiled all six runtime scripts on Python3.9.6; repeat CPU-only retry command after pushing/pulling this fix. No newextractionorGPU job needed for preview recovery. Speed47544658returned noautomaticestimates: read speed_results/method_status.json and iccv2021/error.txt before considering any GPU retry. SavedUniversity8.13mph does not imply automaticmethodsuccess.


## Diagnosed speed failure47544658 and targeted correction

Returned method_status.json: pedestrian-height fit lacks20independent qualifying tracks; ICCV adapter had fewer than10usable car tracks. No new automaticmph. These are implementation input guards, not proof that the published methods failed, and20/10are conservative project thresholds rather than paper-established optima. Universitymanual8.13mph is still only a saved result.

ICCV adapter previously sampled every15sourceframes (~2Hz) with last-frame greedyIoU, potentially fragmenting fast cars. Updated to every3frames (~10Hz), one-to-one HungarianIoU matching with constant-velocity box prediction and max0.3secondtrack gap. Score>=0.8, minimum boxdimension15px, >=4observations, netmotion>=30px retained; minimum10usablecartracks retained. Budget3000sampledframes (~5source minutes), early stop after20usablecartracks and15source seconds, independently of speed-reference agreement. This is a new adapter configuration, not a demonstrated improvement on real footage yet.

Always saves raw_car_observations.npz, tracking_diagnostics.json (detections/track lengths/usabletracks/sample rate/scanned seconds) and periodic annotated diagnostic_frames even when minimumtrackguard fails. Doesnotexportcar speeds. Existingpedestrian-heightmethod remainsdata-insufficient; no newgeometry orindependentspeedvalidation claimed. Afterpush/pull, a targeted GPUretry canuse `sbatch code/speed_research.slurm`; it doesnotrepeatcamera previews orZIPextraction. Newoutputexp_results/colonial_speed_research_JOBID. Do not alsoresubmitfullpilotbundle. Review preview retryresults separately. Eleven speedresearch tests andeightpreview/recoverytests pass includingPython3.9compilecoverage, plusnine studyextensionspreviouslypassed.
