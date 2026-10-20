# Current handoff — 2026-10-20

Start with root README.md and docs/tasks/todo.md. The owner wants to finish this bounded experiment set, not start more detector sweeps. All prior claims below are historical where they conflict with this section.


## Vision3 version pruning — 2026-10-20

Owner explicitly requested only necessary/latest files in Vision3. Deleted63superseded implementations/docs/launchers: root overlaysv1–v9, bestv10, Colonialv11–v18including nestedv17, comparison predecessors throughv7, old launchers, old aggregate readersv11/v12and duplicate preceding sweeps. Current Colonialv19and aggregatev13retained. Distinct utilities retained even if namedv1; moved root utilities into training/comparison/weights_tools/tools (26moves including report to reports/comparison). Patched retained launchers' Python paths. sweep_conf_v2 now imports aggregatev13; same parse_gt interface. No source data, truth, zones, weights, counts or results deleted. vision3/README.md explains current paths; docs/VISION3_CLEANUP_20261020.csv records removals/moves with original hashes. Old docs/recorded commands refer to historical paths and versions; tracked older versions remain in Git history. No jobs submitted.

## Repository layout update — 2026-10-20

Root README rewritten as the current entry point; entire prior guide preserved at docs/history/README_before_cleanup_20261020.md. Loose person_box_review.json, confirmed review JSON and colonial_speed_gates.json moved unchanged to data/reviews/colonial_20261020/. Root results.md and RESEARCH_research_oct19.md moved to reports/cluster_returns/20261019/. Duplicate root NEWSITES report removed only after byte equality with exp_results copy. Historical references below saying root inputs use the old paths; current paths are here. Cleanup manifest docs/REPO_CLEANUP_20261020.csv records hashes and moves/deletions. Active experiment/training paths unchanged; owner-edited deck preserved. Completed scheduler text logs removed only where structured run JSON survives; failed/incomplete logs retained as archive/diagnostics/20261019/*.txt. Cache/OS metadata removed.15%veto remains a tie-preserving choice, not uniquely best.

## Full-system veto threshold replay — 2026-10-20

Implemented `vision3/best/test_colonial/code/tune_veto.py`, CPU only. Replays raw X-CLIP → veto/promotion → motion → duration/strict night cyclist exception → static/quality checks using saved track/audit/statistics/log exports. All scored-track baseline labels and counted decisions must reproduce before reporting; parity passed on all four clips. Saved evidence is rounded, so counterfactual boundaries remain approximate. Unscored tracks remain unscored. No reference configuration changed.

Default development: night21:15 and day14:00. Checking: night22:00/day12:45, accessed only after development selection. Already-inspected clips mean exploratory checking, not independent validation. Thresholds off,5,10,15,20,30,40,50. Choose most correct counted truth people, then fewest unmatched counted tracks, then original threshold/nearest threshold. Full-system development:off through40all9/11;50gives8/11. Retains15by tie preference, NOT a unique empirical optimum. Frozen15checks10/10 (2cyclist-group/8ped), legacy time matching. Motorcycle remains scored cyclist for compatibility. Optional --identity-map restricts to approved mappings; zero development reviewed rows rejects selection. Six regression tests pass. Do not infer the veto has no effect everywhere from a development tie or conflate this with veto-only X-CLIP probes or historical separate inference runs.

Outputs: `exp_results/veto_threshold_20261020/{RESULTS.md,development_sweep.csv,checking.csv,per_person.csv,summary.json}`. No GPU/Slurm run needed; already executed locally. To repeat from cluster ROOT, use a NEW output directory:

```bash
python code/tune_veto.py --out exp_results/veto_threshold_repeat
```

All model inference, tracking and stitching remain fixed; no continuous-video rerender or stream-header replay. Independent untouched labelled footage is required for a validated threshold claim.

## Latest owner review — zones and new-site failures

See `vision3/best/test_colonial/exp_results/newsites_owner_review_20261020.md` for exact encounter times. Owner visually approved zone previews. Anderson: detected pedestrian and one cyclist; missed a second cyclist and a motorcycle. Curry Ford: missed a very blurry cyclist. This supersedes the earlier statement that no visual review was supplied. It is not exhaustive full-video truth or verified identity accuracy. Do not launch more model sweeps automatically.

Workbook Colonial lengths confirmed: bike lane35ft (12 records including e-bike), sidewalk30ft (11 records). Endpoints/camera-date applicability and person-to-record links remain unverified; do not invent gates from lane polygons. Received root person_box_review.json unchanged:32frames/20boxes, only1reviewed checkbox true. Asked whether all frames are finished; never silently approve unchecked frames. Matching RF/DINO manifest/predictions are not local; need existing downloaded review pack to score, not another inference run.

## Latest returned batch — completed, do not resubmit

Owner supplied root NEWSITES_newsites_oct20.md. Preserved input and copied to vision3/best/test_colonial/exp_results/NEWSITES_newsites_oct20.md. Four work jobs report SUCCEEDED; final report exists:

- Anderson St2021, April13 noon–12:15 inferred:900s processed,720x480@29.97fps; predicted1cyclist,1pedestrian,137vehicles; runtime38.7min.
- CurryFordNorth2022, May17 noon–12:15 inferred:900s processed,720x480@29.97fps; predicted0cyclists,0pedestrians,448vehicles; runtime38.5min.
- final_review SUCCEEDED; outputs at cluster ROOT/exp_results/final_review_20261020, now ready to download whole folder.
- truth_headers SUCCEEDED; copies under ROOT/annotated_gt, originals preserved.

Execution success is not accuracy. Owner has now supplied timestamped visual review: missed cyclists at both sites and a missed Anderson motorcycle; see latest review above. No exhaustive whole-video truth is available. Both sites appear in training recipe and neither video has more resolution than Colonial. Clocks are filename-inferred, not verified. Actual MP4 paths are recorded in returned report; use them rather than guessed paths. No repeat combined batch, new-site runs, RF full-frame audit or header job is needed.

Next: finish existing raw-frame RF/DINO review and full-track identity checks; measured speed gate endpoints and record-to-person links are still human steps. Zone preview alignment is owner-approved; no validation is completed merely by the CPU job succeeding. Older pending-submission statements below are superseded by this update.

## Detector / X-CLIP comparison completed locally

Owner requested which is more accurate on four existing truth clips. New `code/compare_classifiers.py` produced exp_results/classifier_comparison_20261020/{RESULTS.md,per_person.csv,summary.json}, no Slurm/inference. Same21matched/scored tracks, including rejectedn5; detector = cyclist if detector-cyclist share>=50%, otherwise pedestrian; X-CLIP = RAWweighted argmax from rules_audit.csv, NOT tracks.csv xclip_label (that field can already reflect rules).

Detector16/21(76.2%), X-CLIP14/21(66.7%). Byclip night21:15=3/6vs3/6;day14:00=5/5vs3/5;night22:00=4/5vs5/5;day12:45=4/5vs3/5. Cyclistgroup5/8vs6/8(includes1motorcycle);pedestrians11/13vs8/13. Bothright11,bothwrong2,detectoronly5,XCLIPonly3. No general superiority or detection-recall claim; provisional time matches still require identity review. Optional --identity-map limits analysis to approved identities and gives no percentages when none reviewed. Two local regression tests pass, including raw-label versus post-rule distinction and keeping rejected tracks. No new model sweep or change to fusion thresholds.

## Current batch entry point

Owner confirmed none of the recent pending changes have been run on HiPerGator. Use `python code/submit_final_batch.py --go` once after push/pull, not merely `sbatch code/final_review.slurm`. Combined plan has5jobs: two reference new-site pipelines, CPU review/gate/zone build, CPU GT-header copies, dependent report. Manifest logs/newsites_oct20; report exp_results/NEWSITES_newsites_oct20.md. No repeat old research suite or full-frame RF audit. CPU header walltime4h, review30min. Required audit assets, source videos, existing annotations and duplicate outputs checked before submission. Partial submission guard retains jobIDs.

Normal3s day/night; strict NIGHT cyclist exception >=0.3s, detector cyclist share>=90%, weightedXCLIP>=0.90, finalclasscyclist. NOT blanket0.4snight. New-site env explicitly pins3s and strict exception values. Reference weights/rules unchanged. Human validation and physical speed calibration remain manual after batch. No jobs submitted locally.

## Presentation and preferences

- Always create a NEW dated PowerPoint copy; never overwrite the owner's deck.
- Owner added fusion, speed and per-clip results slides. Preserve them: saved original has eight slides.
- New deliverable: reports/presentations/bike_weekly_meeting_10_20_reviewed.pptx, eight slides, reordered definitions → method → fusion → speed → development results → research results → other camera → task audit.
- Original October19 deck was read, not written by this turn. Owner saved a sensitivity-row edit during work; incorporated its “0.4 s day/night” clarification in the new copy. Do not claim the original checksum stayed fixed while the owner was editing.
- Forty-track comparison and own-night fine-tuning remain deferred. Full-day scaling remains removed.

## Current detector evidence

Reference b4_combo_static5: 19/21 under LEGACY TIME MATCHING, no extra counted tracks. Not identity-verified accuracy. TTA: same19/21 plus1extra, with owner-confirmed barricade-to-person ID jumps. Sensitive: same19/21 plus28extras. Zero-DCE:7/11 on night vs reference9/11. No promotion of those methods.

Sensitive settings were confidence/tracker thresholds0.15, minimum duration0.4s for BOTH day and night, static filterOFF. This differs from the reference: usual3s with a strict NIGHT-only0.3–3s cyclist exception. Reference and new-site runs do not enable broad sensitivity. Do not rewrite historical experiment settings or silently remove the reference's short-night exception.

Truth correction: n3/n4/n5 are cyclists at14:21–14:26; n5 legacy track21 is rejected. n6 is pedestrian at14:47–14:58, legacy track23 wrong class. Earlier notes reversed these time descriptions. Actual truth CSVs were never changed. Motorcycle n1 is grouped with cyclists only in the older count score; preserve its raw class for lane/speed analysis.

Fusion weighted score is sum(box_height * class_probability) / sum(box_heights), then fixed veto/speed rules. The motion feature is smoothed 2-D path length / elapsed seconds / mean box height; the speed RELABELLING rule is lateral-only, but the measured path itself is not just x-displacement. It is not mph.

## Completed lane and image-motion analysis

Code: code/labelled_lane_speed.py. Outputs: exp_results/labelled_validation_20261020/ under cluster ROOT / local vision3/best/test_colonial.

- Exactly21 truth rows;20 usable image-motion estimates, one insufficient candidate.
- Provisional candidate lanes:12sidewalk,3bike-lane (includes motorcycle),1road,5uncertain. NONE are yet identity/lane validated.
- Uses observed, non-coasted foot points within each truth window; v2 polygons scaled from inferred1440x960 to720x480. Multiple polygon hits are uncertain. No forced road-to-bike/sidewalk assignment.
- people_lane_speed.csv, study_lane_comparison.csv, identity_review.csv, Colonial_study_speed_records.csv, study_record_links.csv, summary.json, RESULTS.md and identity_pending.md.
- Study count workbook gives aggregate lane counts, not person-level lane truth. At21:15 its3bicycles disagree with hand truth4bicycles+motorcycle. Do not force model/human totals to agree.

## Speed reference: important correction and remaining inputs

Full workbook scan DOES find23uniqueColonial speed records:12bike-lane including one e-bike,11sidewalk. Raw and analysis-sheet copies are deduplicated by record/facility/distance/time. Initial preview-based statement “no Colonial records” was incorrect and corrected during the turn.

Colonial lengths:35ft bike lane,30ft sidewalk. Source mph uses approximate0.681 conversion; exact3600/5280 recomputation is saved separately. Arithmetic checking is NOT model-speed validation. Rows lack matching video timestamps, image gate endpoints and clear camera/date identification. Owner believes record numbers correspond; that is not an explicit mapping to n1/d1/h1/p1 truth IDs. Use study_record_links.csv with reviewer/evidence, never ordinal matching.

Owner provided zones/colonial_north_v2.json. It defines lane AREA polygons, not measured start/end cross-lines. No physical endpoint or human height is guessed. speed_gate_setup.html lets the user mark actual measured cross-lines on a raw frame and confirm source/camera/date/reviewer; code/speed_gates.py computes feet / crossing seconds only for complete unique finite-gate crossings. The empty zones/colonial_speed_gates.template.json deliberately cannot be used as a calibration.

Analyzer accepts --speed-gates, --identity-map and --record-links. Only identity-approved people with metric estimates and evidenced one-to-one study links contribute paired MAE/RMSE. No usable pairs gives null metrics, not zero error. Homography support also requires independently measured same-camera metric coordinates. MPH and matched speed validation remain UNFINISHED because endpoints and verified links have not been supplied.

## Prevent false identity credit

code/eval_truth.py --require-identity [--identity-map CSV] preserves old time-only results but gives unapproved matches UNVERIFIED, excluded from correct/reviewed denominator. Approvals require reviewer, evidence, full_track_reviewed=yes and one-to-one IDs. Check the ENTIRE track, including before/after the truth window. This prevents false verified credit; it does NOT repair ByteTrack or stitching ID switches. No extra40-track campaign or repeat time/class labels requested. Current pending report has0reviewed, not0%accuracy.

## RF-DETR / Grounding validation and one final CPU job

RF-DETR completed165frames/48proposals/9low-overlap; Grounding165/386/308. These totals cannot rank accuracy. New code/rf_person_review.py builds raw selected frames with predictions hidden, encounter midpoints plus four fixed background frames per clip, deduplicating simultaneous encounters (up to37frames). Box every visible human including riders, explicitly mark reviewed even for empty frames, export JSON. Unreviewed frames excluded. Person-only precision/recall at maximum one-to-oneIoU≥0.5, NOT cyclist-mode accuracy, AP, unique-person recall or an independent holdout.

Cluster command: sbatch code/final_review.slurm. No new inference/download. Builds exp_results/final_review_20261020/ with rf_boxes/review.html, raw frames, zone_previews and speed_gate_setup.html. Download WHOLE folder to Mac. Missing completed audit assets fail explicitly. This CPU job has not been run from this Mac; source videos/images are cluster-only. Raw-frame HTML and gate-page JavaScript smoke checks passed locally.

Existing new-site command remains code/submit_newsites.py --go, two GPU jobs plus report for Anderson2021/CurryFordNorth2022. No returned results supplied. Both sites appear in training recipe, not strict unseen-site generalization. Do not resubmit if already queued/running.

## Verification and task status

Nine new validation tests pass: no time-only identity credit; approvals require evidence; zone overlap; no silent mph conversion; synthetic measured gate speed;23deduplicatedreferences; verified speed-pair gating; one-to-one detector boxes; no empty-frame assumption for unreviewed images. Existing17recovery tests pass; header tests also pass. Source workbooks read with standard-library XML/ZIP, never edited. No Excel workbook authored.

Current task audit correctly leaves identity review, lane alignment, optional RF box validation, returned new-site results and physical speed correspondence open. Broad sensitivity's12-minute review-budget benefit is unmeasured and retired as a claim; walking-away explanation remains partial. Further model sweeps are closed. README.md has current commands; historical notes below do not authorize new experiments.

---
# Historical session notes (superseded where inconsistent)

## Latest clarification and two-site implementation

The five-slide results deck now spells out the full system and replaces ambiguous “all4”, “nightonly”, “extra counts”, “Min/clip” and “sensitive” labels. Extra counts = tracks unmatched to human-labelled encounters (may be duplicates/false objects or missing truth); processing minutes = runtime per15-minutevideo. Night-only rows repeat the same configuration on the11nighttruth people to compare brightening fairly. Time-only matching can credit a track that starts on a barricade and later follows a person, so19/21is not identity-verified accuracy. RF-DETR48boxes vs GroundingDINO386on165frames = no demonstrated counting improvement; accuracy cannot be inferred from proposal volume. Exact Corrine paths and review questions are in the final-slide speaker notes and docs/VIDEO_PATHS.md.

New launcher `code/submit_newsites.py --go` (from cluster ROOT) submits reference-system runs on AndersonSt2021 and CurryFordNorth2022 plus final report. Dry-run by default. It discovers real source files under their known dataset folders, prefers a readable noon/daytime hourly file, processes only the first900seconds, and records source/metadata/clock provenance. It refuses missing inputs before submitting and reuses the existing duplicate-guarded manifest + afterany scheduler orchestration. These sites appear in the documented TRAIN recipe, so do not claim strict unseen-site generalization. No complete new truth and no accuracy score. No resolution requirement; pixel-based parameters scale with width. No inherited Colonial zones. Source clocks are inferred from filename/hour index and explicitly marked unverified. User must confirm embedded clock when reviewing.

Command: `python code/submit_newsites.py --go`; default tag `newsites_oct20`. TwoGPUjobs, finalCPUreport `exp_results/NEWSITES_newsites_oct20.md`, actual video paths read from successful run JSONs. Do not invent exact output filenames before the cluster source selection has run. Rebuild report without resubmitting via `python code/research_worker.py logs/newsites_oct20 report`. Status/logs/manifest in logs/newsites_oct20. No jobs actually submitted from this Mac session.

Shared worker now supports `scale_pixels` even for720x480sources (old higher_resolution path still enforces its requirement). Slurm wrapper accepts CLOCK_NOTE and writes it into the run log. Tests cover source-clock parsing, fixed source selection/fallback, reference configuration, report actual paths/non-accuracy disclaimer and safe dry-run; existing17recovery tests pass. GPU execution still pending.

## Latest owner review and follow-up — 2026-10-19

This update supersedes the “RF-DETR not yet run” statements in the initial session record below.

**TTA night 22:00–22:15:** owner reports barricade labelled pedestrian around clip 04:30, IDs 10/12/20/28. ID12 later follows a real pedestrian at clock22:06:00–22:06:14 (clip06:00–06:14); ID20 follows a real pedestrian22:10:00–22:10:15 (clip10:00–10:15). Three pedestrians at22:10:58–22:11:17 have IDs28/35/31. This establishes visual ID contamination/association errors. Do not treat 19/21 from time-only evaluation as identity-verified accuracy. Do not silently change the existing truth CSVs to match predicted IDs or overwrite saved scores. The cause could be ByteTrack association or later stitching; saved trajectories require diagnosis before changing either.

**Older Corrine combination (`nv_combo_corrine2025_706`, SAHI853):** owner reports an e-scooter labelled pedestrian, two distant cyclists missed, and a distant parked car without a drawn box. Scooter mode is not an explicit current category; “person found” does not mean transport mode correct. Annotated vehicle boxes appear only for confirmed/countable vehicles, including a 40px movement requirement; no rendered parked-car box alone does not prove no raw detection. New `research_oct19_hires_combo` (SAHI864) filename was supplied WITHOUT a verdict; do not copy the old verdict onto it. Complete Corrine truth totals remain unknown.

**RF-DETR full-frame audit completed**, owner-supplied report:

| Clip | Frames | Proposals | Low overlap |
|---|---:|---:|---:|
| night | 42 | 12 | 3 |
| day | 41 | 15 | 3 |
| night_holdout_2200 | 37 | 3 | 0 |
| day_holdout_1245 | 45 | 18 | 3 |
| Total | 165 | 48 | 9 |

Pretrained Medium, threshold 0.30. Proposal quantity cannot establish accuracy or rank it against Grounding DINO. In particular37 frames / 3 boxes in the 22:00 clip is sparse output, not three unique recovered pedestrians. Visual matching remains needed. These were frames from Colonial 2019, not a new-site video run.

**Additional code, not yet run on cluster:** `python code/rfdetr_audit.py --tiled --go` submits one GPU job with full-frame + 320px tiles,25%overlap,class-awareNMS IoU.50,threshold 0.30, same 165 frames. Writes `logs/rfdetr_tiled_oct19/RESULTS.md`. Existing full-frame output stays unchanged. Intended to test small/distant boxes; not integrated cyclist counting or a promised improvement. Local tests cover edge coverage, coordinate mapping, class-aware duplicate removal and empty output.

**GT header fix:** current v19 renderer uses the existing four hand-labelled truth CSVs for the exact Colonial source/date, in preference to older aggregate spreadsheet counts. Dedicated fourth yellow header line avoids long-line clipping; unknown bins/cameras explicitly show `GT: not labelled`. Frame dimensions/writer height are updated consistently; no counting logic changed. `stamp_truth_headers.py` creates copies of existing annotated videos under `annotated_gt/<run>/...` with a new yellow truth strip; no model inference, no overwrite of originals. Old MP4s are not automatically changed by pulling code. It defaults to a plan; `--go` encodes. Do not invent Corrine counts from a partial two-cyclist observation.

Exact other-site video paths and an actual-filename listing command: `docs/VIDEO_PATHS.md`. Only Corrine 706 was processed in the higher-resolution suite; the three versions are the same site/year/clip. Source scans of other cameras/years are not completed annotated experiments.

**Presentation:** `reports/presentations/bike_weekly_meeting_10_19_results.pptx` is now five slides: definitions → system/methodology → Colonial results → other-camera/RF-DETR evidence → targeted next checks. V3 is explicitly a fine-tuned RT-DETR detector, not an unexplained “best model.” Deferred work stays out.

More research options remain (appearance-aware association, temporal detector features, camera-domain training), but prioritize the observed ID jumps and small distant cyclists. Do not imply every method has been exhausted or silently reactivate deferred training/full-day scaling.

## Earlier October batch evidence and interpretation

Sources: root `results.md` (cluster terminal output) and `RESEARCH_research_oct19.md` (report from the same run, NOT an independent replication). All 21 non-report tasks succeeded and the final report exists.

| Configuration | Correct truth people | Extra counted tracks | Mean recorded runtime / clip | Decision |
|---|---:|---:|---:|---|
| b4_combo_static5 | 19/21 | 0 | 42.0 min | Keep as current reference |
| TTA scale + flip | 19/21 | 1 | 88.5 min | No gain; review extra track |
| Sensitive settings | 19/21 | 28 | 39.7 min | Candidate review only |
| Zero-DCE, two night clips | 7/11 | 0 | 51.5 min | Leave off; night reference is 9/11 |

19/21 is a small four-clip validation set, not proof of reliability across cameras or full days. Evaluation matches by time, with ambiguity when people overlap. Both remaining reference errors are in the 21:15 night clip: a pedestrian classified as cyclist (14:21–14:26) and a 2.37-second rider rejected (14:47–14:58). No truth encounter was wholly missed under this matcher. Sensitive mode changed several settings simultaneously; it is not an isolated minimum-duration experiment. Recorded runtime comparisons are not controlled hardware benchmarks.

Grounding DINO: 165 sampled frames, 386 proposals, 308 with low overlap with saved b4 boxes. These are repeated frame boxes, NOT 308 missed people or person recall. Baseline overlays include rejected/coasted tracks. Inspect before drawing conclusions.

Higher resolution: two sources found; Corrine 706 is 960x540, 15 fps, with fisheye distortion. Three matched Corrine runs each counted 0 cyclists/1 pedestrian, but no truth exists, so accuracy remains unknown. Any year is acceptable if resolution exceeds the Colonial 720x480 footage. Zone and fisheye previews are guesses pending visual review.

Latest presentation: `reports/presentations/bike_weekly_meeting_10_19_results.pptx` (now condensed to five slides; see latest update above). Earlier presentations remain historical.

## What the owner should review

Cluster ROOT = `/orange/xiangyan/rithika/vision/vision3/best/test_colonial`.

1. `ROOT/annotated/research_oct19_tta/`: the 22:00–22:15 video (source chunk .023). Determine whether its single extra pedestrian is a duplicate, false alarm, or a real person omitted from truth. Locate the actual output with `find annotated/research_oct19_tta -type f -name '*2200-2215*.mp4'` from ROOT; no local cluster file existence has been verified.
2. Reference 21:15 video: check 14:21–14:26 (walker) and 14:47–14:58 (short rider). Exact reference video locations are documented in `docs/VIDEO_PATHS.md`. Do not relabel existing truth.
3. `ROOT/logs/research_oct19/grounding/night/`: JPGs near clip seconds 861–866 and 887–898. Left = saved b4 tracks, right = Grounding DINO. Are proposals real, and do they explain the two errors? Other four-clip audit folders: `day`, `night_holdout_2200`, `day_holdout_1245`.
4. Optional existing sensitive-candidate review pack: download the whole `ROOT/logs/research_oct19/review_12min/` directory and open `review.html`. Label b/p/n using its controls and return the exported CSV. Twelve minutes is the raw snippet budget, not a promise of human review time. This is NOT the deferred 40-track study.

## New code added this session — not yet run on GPU

`vision3/best/test_colonial/code/rfdetr_audit.py`: pretrained RF-DETR Medium (rfdetr==1.11.2), threshold .30, full-frame proposal audit on exactly the Grounding DINO sampling scheme. One GPU job creates an isolated environment, preserves the working Torch/torchvision versions through pip constraints, downloads the model, audits all four clips, and writes `logs/rfdetr_oct19/RESULTS.md`. Per-clip side-by-side JPGs/CSVs, model metadata/checkpoint hashes, package freeze, status and Slurm log remain alongside it. Baseline model, outputs and yolo_env are not changed. Package conflicts fail explicitly rather than replacing working Torch. Default is dry-run; output directory prevents duplicate submission. On failure inspect status/log before choosing a new tag.

This is a modern alternative detector benchmark, NOT a replacement counting pipeline or a claim of improved cyclist accuracy. COCO person/bicycle/motorcycle are separate categories. Low overlap is not a verified miss. No new truth boxes are requested before running; visual adjudication is needed afterward. Existing Grounding DINO audit gained an optional inference callback; its default behavior stays unchanged.

Primary method/API source: https://github.com/roboflow/rf-detr ; published package metadata: https://pypi.org/project/rfdetr/1.11.2/ . The published wheel was checked for RFDETRMedium, COCO_CLASSES and RF_HOME support. CPU tests check category filtering, dry-run behavior and tag safety; existing research tests pass. CUDA inference/package setup still require the cluster run.

After committing/pushing on the Mac, on HiPerGator:

```bash
cd /orange/xiangyan/rithika/vision
git pull --ff-only origin main
cd vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
python code/rfdetr_audit.py --go
```

Read `logs/rfdetr_oct19/RESULTS.md` after completion; failures are in `logs/rfdetr_oct19/status.json` and `job_<id>.log`. The original 22-task suite does NOT need resubmitting.

## Constraints for the next assistant

- Existing four truth CSVs under ROOT/truth total 21 people; no repeat labeling requested.
- Full-day 24/48-hour scaling removed from the active plan.
- Own-night fine-tuning and ~40-track hand-label comparison are on the back burner.
- Do not promote TTA, sensitive thresholds, Zero-DCE, Grounding DINO or RF-DETR without evidence.
- Higher resolution may be from any year; 720x480 cameras do not qualify merely because newer.
- Current pipeline: fine-tuned RT-DETR v3 + SAHI + ByteTrack/stitching + X-CLIP + rules/fusion/static filter. Current code is under vision3/best/test_colonial/code.
- Slurm partition hpg-turin, account/qos **xiangyan**. Working environment: /orange/xiangyan/rithika/vision/yolo_env. Submit GPU work with sbatch.
- Keep root README.md the single user entry point. Do not delete truth, structured results, weights or videos during cleanup.
- Git transfers code/docs, not ignored cluster videos/model weights. Preserve cluster changes if pull conflicts; never force-reset/clean results.

---

# Historical September handoff (superseded)

The text below records an earlier pipeline/dataset audit. Its 48-hour counts, next steps, file paths and account settings are historical, not the current Colonial validation status.

# Project Handoff — Cyclist Detection from Archival Traffic Video

**For:** an AI coding assistant (or new collaborator) picking this up cold.
**Written:** 2026-09-19. **Owner:** Rithika Mathew, UF (rmathew1).

Read this first, then `METHODOLOGY.md` (research design),
`PROGRESS.md` (checklist), `HIPERGATOR_COMMANDS.md` (runbook).

---

## 1. What this project is

A UF transportation-engineering study measuring cyclist behaviour from 2019
MioVision traffic-camera footage, validated against hand-collected counts.
Five goals in `goals.md`; **only Goal 1 (counting) is under way.**

Compute: HiPerGator, `/orange/xiangyan/rithika/vision`, Slurm partition
`hpg-turin`, account/qos `xilei.zhao`, venv `yolo_env` (plain
`source yolo_env/bin/activate`, not conda). Always `sbatch` — never run YOLO on
the login node.

### The dataset's two unusual properties (these drive the research design)

1. **Matched-pair natural experiment.** Every recording date deployed *two*
   cameras simultaneously — one bike-lane (BL) site and one no-bike-lane (NBL)
   control. 17 such pairs. Weather, season, day-of-week and time-of-year are
   controlled by construction. Discovered by date-joining video folders to
   ground truth (`build_site_mapping.py`); it was not documented anywhere.
2. **Facility-disaggregated human ground truth.** 41 site-sessions, 5,053
   cyclists, split by facility/direction/movement. **63% of cyclists ride on
   sidewalks**, only 22% in bike lanes. This is rare — most papers in this area
   validate against a few hundred self-drawn boxes.

---

## 2. Current status — one sentence

The detection/tracking pipeline runs end-to-end over a full 48-hour
site-session and reports **88 cyclists against a ground truth of 89 (−1.1%)**,
but an audit shows that total is **two large errors cancelling**, and the next
move is detector fine-tuning.

### The headline number is not what it looks like

Human review of the 30 most-suspicious tracks (§3b) found **50% of them
spurious** — 8 duplicates, 6 false positives, 1 pedestrian. Those 30 were
selected as the worst, so 50% is not the session-wide rate; extrapolating the
lower-suspicion remainder conservatively puts the true count somewhere around
**55-65 real cyclists against a ground truth of 89**.

That implies the pipeline is simultaneously **adding ~25-30 spurious counts and
missing ~25-30 real ones**. The reviewer confirmed misses directly: three notes
record a cyclist plainly visible with no detection box.

**Never report the −1.1% without this caveat.** A correct total is not evidence
of a correct pipeline — here it is two large errors cancelling.

---

## 3. What was fixed (do not re-litigate these)

The pipeline began at **zero cyclists tracked** on a clip where the detector
reported a cyclist at confidence 0.92. Six distinct bugs, each diagnosed from
logged evidence, all fixed and covered by a 10-test regression suite:

| Bug | Evidence | Fix |
|---|---|---|
| IoU association gate (0.3) | passed 3/12 links on the known cyclist; box height flaps 114→62→50 px so IoU collapses at 6.7 px of motion | velocity-predicted, size-normalized centroid association (`vru_tracker.py`) |
| Duplicate detections | one rider → 5 "cyclists" + 2 "motorcycles" + 3 "persons" | containment suppression + cyclist fusion + redundant-track merge |
| Merge used the wrong scale | normalized by the track's *final* box; a receding cyclist goes 160→29 px, inflating early distances ~5×, while tracks ending large merged **a car with a pedestrian** | normalize per-timestamp |
| Merge needed shared timestamps | assignment is one-to-one, so two tracks on one object interleave and share **0** timestamps | path interpolation + succession test |
| Class vote relabelled cyclists as pedestrians | a cyclist always generates person detections and the rider is easier to detect, so summed votes flip as the bike becomes unresolvable | bicycle evidence (max conf ≥ 0.40) is decisive |
| Track termination counted samples not time | `max_missed=4` = 0.13 s at stride 1; and `predict()` only extrapolated one sample ahead, so coasting could never reacquire | `--coast-seconds`; extrapolate from `last_t` |

Plus: H.264 via ffmpeg CLI (OpenCV picked `h264_v4l2m2m`, a hardware encoder
absent on compute nodes), confirmed-tracks-only two-pass rendering, trail
smoothing, tile batching.

**Tracker work is done.** The remaining errors are upstream, in the detector.

---

## 3b. CLIP REVIEW RESULTS — 30 most-suspicious tracks, human-verified

`review_sheet.csv`, scored by the owner. **This is the most important evidence
in the project** and it corrected two of my own recommendations.

| Verdict | n | % |
|---|---|---|
| REAL | 15 | 50% |
| DUP (same rider counted twice) | 8 | 27% |
| FP (nothing cyclist-like) | 6 | 20% |
| PED (pedestrian read as cyclist) | 1 | 3% |

**50% of the most-suspicious set is spurious.** Note this is the *top 30 of 88*
by suspicion score, deliberately not a random sample — do not read 50% as the
session-wide error rate.

### Mechanisms the owner identified, counted from the notes

| n | Mechanism |
|---|---|
| 9 | **false detections on grass / vegetation** |
| 4 | box jumps onto grass mid-track (contaminates otherwise-REAL tracks) |
| 3 | one cyclist split into two track IDs (typically far→near, as apparent size changes fast) |
| 3 | cyclist missed while far from camera |
| 2 | cyclist first classified as a **car**, corrected only when closer |
| 1 | **two real cyclists merged into ONE track ID** (over-merge → under-count) |
| 1 | traffic cone detected as cyclist |
| 1 | pedestrian detected as cyclist |

**Grass is the dominant false-positive source** — 5 of 6 FPs are grass or cone,
and all 6 have `mean_conf` between 0.18 and 0.28. It is a texture/appearance
problem in specific frame regions, not a tracking problem.

### ⚠️ Two earlier recommendations are now WITHDRAWN

These were my hypotheses; the review data contradicts both. Do not implement
them:

1. **Do NOT raise `MIN_NET_DISPLACEMENT` (0.75).** I predicted low-excursion
   "STATIC" tracks would be false positives. They are not: tracks flagged
   STATIC were 47% spurious versus 54% for un-flagged ones — no predictive
   power. REAL cyclists have a *median* excursion of 2.85 and a minimum of
   0.97, identical to the FP minimum. A cyclist riding toward or away from the
   camera, or clipping a frame edge, legitimately covers very little
   image-plane distance. Raising this threshold would delete real cyclists.
2. **Do NOT add a night-specific confidence penalty.** I predicted night false
   positives from the rate anomaly (night 2.12/h > day 1.69/h). The review says
   the opposite: night-flagged tracks were 36% spurious versus 62% for daytime
   ones. The rate anomaly is more likely explained by *daytime misses* (more
   traffic, more occlusion) than by night FPs.

**What survives:** the `DUPLICATE` flag is a *necessary* condition — all 8 DUPs
were flagged, 0 unflagged tracks were DUP — but only 47% precise. Keep it as a
triage signal, not a filter.

---

## 4. Known issue the owner observed directly

> *"the object detection is very glitchy and only detects bicyclists and not
> cars very well"*

Partly a rendering artifact, partly a real configuration problem:

1. **Clips draw confirmed tracks only** (`--draw-all` defaults off), so
   anything rejected is invisible. Cars that don't clear confirmation simply
   don't appear.
2. **Vehicles are held to a STRICTER standard than cyclists.** In
   `pilot_detect_v2.py`: `_default` (car/truck/bus) needs 1.0 s persistence,
   max_conf 0.55, mean_conf 0.22; `cyclist` needs 0.5 s, 0.50, 0.18. Those
   thresholds were tuned for the cyclist problem. **Goal 1 is explicitly
   "Cyclist + Vehicle Counting", so this is a real defect, not just optics.**
3. **Clips render at `--stride 5`** (6 fps) to match the counting run, which
   looks choppy. Deliberate: rendering at full frame rate would show a
   *different* pipeline's output than the one that produced the counts.

To see what the detector actually does, unfiltered:

```bash
python pilot_detect_v2.py "$CLIP" --render-window 400 420 --stride 1 --draw-all
```

**Action for whoever picks this up:** tune vehicle thresholds separately
against vehicle ground truth before claiming anything about vehicle counts.
There is no vehicle ground truth in the Excel files — the hand counts are
cyclists and pedestrians only. So vehicle counting needs its own validation
plan, or should be dropped from Goal 1's scope. Raise this with the owner.

---

## 5. NEXT STEP: fine-tune the detector

**Recommendation: yes, now.** The argument is evidential, not preference —
each of the three audited failure modes traces to the detector's *concept*
mismatch, not to the tracker:

Every mechanism in the verified review (§3b) is an *appearance* failure, not an
association failure:

| Verified mechanism | n | Why fine-tuning is the fix |
|---|---|---|
| Grass / vegetation detected as cyclist | 9 | pure appearance error. COCO never saw 2019-compression grass at this scale. Mine these exact frames as **hard negatives** — they are already located, with timestamps |
| Box jumps onto grass mid-track | 4 | same root cause: grass produces competing detections the tracker then associates to |
| ID split far→near | 3 | the detector's box is unstable as scale changes, so association has nothing stable to track. A single trained `cyclist` class emits one consistent box |
| Missed while far from camera | 3 | domain gap on 30-px riders — exactly what sliced fine-tuning targets |
| Cyclist classified as car at distance | 2 | class confusion, fixed by training on this domain. **Also worth knowing:** the semantic-group constraint in `merge_redundant_tracks` blocks car↔cyclist merges by design, so this splits one rider into two un-mergeable tracks |
| Pedestrian read as cyclist | 1 | `fuse_cyclist_dets` cannot tell standing-beside from riding; a trained model can |
| Two cyclists merged into one ID | 1 | over-merge → under-count. Rarer than under-merging (8 DUPs), so do not tighten merge globally |

Tracker tuning is exhausted; six bugs in, and every remaining mechanism the
human reviewer identified is upstream in the detector.

### 5.1 Mining strategy — use the pipeline's own uncertainty

The originally-planned mining pass needed 15-minute interval ground truth,
which **does not exist** (see §7). There is now a better source that sidesteps
that blocker entirely:

The full-session run produced **88 counted + 821 rejected** cyclist-class
tracks, each with a chunk and timestamp. Those 909 tracks are a *curated pool
of hard cases* — every one is somewhere the detector saw something
cyclist-like and the pipeline had to make a close call. That is exactly the
distribution worth annotating, and far better than uniform sampling where
>99.99% of frames contain no cyclist.

Build `mine_frames_from_tracks.py`:
- read `*_tracks.csv` for a session
- for every cyclist-class track (counted **and** rejected, `hits >= ~5`),
  sample 2–3 frames spread across `first_t`..`last_t`
- extract those frames from the chunk `.mp4`
- run the detector on each to produce pre-filled YOLO labels (reuse
  `process_frame_detections` from `extract_frames.py`, which already applies
  `fuse_cyclists`)
- write `images/`, `labels/`, `previews/` in the existing dataset layout

Expected yield: ~2,000 frames, heavily enriched for cyclists — roughly the
target annotation budget in one pass.

**Add the grass false positives as hard negatives.** The review located 9 of
them with chunk and timestamp. Frames where the model fires on grass, labelled
with no cyclist box, are the single most targeted training signal available —
and `mine_frames_from_tracks.py` already extracts rejected tracks, which is
where most grass detections live. When annotating, resist the urge to skip a
frame because "there is nothing in it": a frame with a confident wrong box and
an empty label is exactly what teaches the model to stop.

**Critical:** the tracks CSV does **not** store bounding boxes, only track-level
statistics. Pre-labels must come from re-running the detector on the extracted
frames. Do not try to reconstruct boxes from the CSV.

### 5.2 Annotation

Free tools; do **not** hand-draw from scratch.

- **CVAT** (`app.cvat.ai`, free tier) — has box interpolation across video
  frames, the single biggest annotation multiplier here. Roboflow's free tier
  lacks it and makes projects public (check the MioVision data licence before
  uploading anywhere).
- **FiftyOne** for curation if the pool needs narrowing.
- Classes (already wired into `extract_frames.py`, `cyclist` appended at index
  6 so existing label files stay valid):
  `person, bicycle, car, motorcycle, bus, truck, cyclist`
  — `cyclist` = person visibly riding; `bicycle` = unridden/parked.
- Target **1,500–3,000 images**. Do not attempt the whole dataset.
- Box the *whole* cyclist (rider + bike) as one rectangle. Include tiny and
  partly occluded riders — those are the hard cases the model currently misses,
  and skipping them teaches the model to skip them.

### 5.3 Training

- **Split by SITE, never by frame.** Adjacent frames are near-duplicates; a
  random split leaks and inflates mAP badly. This is the most common fatal
  flaw in transportation-CV papers. `build_dataset.slurm` already enforces
  site-based splitting — preserve that.
- **Train on tiles matching inference geometry.** The pipeline tiles 2×2 with
  20% overlap at inference but the model was trained on full frames. SAHI
  reports +12–14 AP cumulative for fixing exactly this mismatch. Likely the
  single largest available win.
- `imgsz=640` for tile training (tiles are already crops).
- Before rebuilding the dataset: `mv dataset_frames/split
  dataset_frames/split_OLD_unfused` — the resume check skips existing frames,
  so otherwise you get a mix of fused and unfused labels.
- Model: YOLOv8-L is the current baseline. Run YOLO11-L / YOLO26-L as an
  ablation *after* the pipeline is correct, not before. `pilot_detect_v2.py`
  takes `--weights`.

### 5.4 Re-validate

Re-run the full BL Colonial session with the fine-tuned model and compare:
counted, duplicates, static tracks, misses, day/night ratio. **The success
criterion is not a better total — it is fewer flagged tracks at a similar
total.** Then extend to Edgewater (GT 228), NBL Pine Hills (GT 317, 98%
sidewalk), Aloma Path (GT 191).

---

## 6. Goals status (`goals.md`)

| Goal | Status | Notes |
|---|---|---|
| **1. Cyclist + vehicle counting** | 🔶 cyclists working but over/under-counting; **vehicles not validated at all** | no vehicle ground truth exists in the Excel data — scope question for the owner |
| **2. Infrastructure type** | ⬜ not started, but **much more tractable than assumed** | `facility_type` ground truth now recovered (63% sidewalk / 22% bike lane / 11% path / 5% travel lane) across 41 sessions. Combined with the matched BL/NBL pairs this is the strongest goal after counting. Approach: `METHODOLOGY.md` Idea C (unsupervised facility-zone induction from trajectory clustering) |
| **3. Cyclist speed** | ⬜ not started | hand-timed speed ground truth exists by facility (Travel Lane 14.5 mph mean, Bike Lane 11.8, Sidewalk 9.3). `METHODOLOGY.md` Idea A proposes distribution-matching self-calibration — no field measurements needed, which matters because the 2019 cameras are gone |
| **4. Near-miss / TTC / PET** | ⬜ not started | needs Goal 1 + Goal 3 first; no ground truth exists, will need a manually-reviewed validation sample |
| **5. Age / gender** | ⚠️ **recommend cutting** | no ground truth, ethics-review magnet, invites reviewer hostility out of proportion to what it adds. A limitations paragraph explaining the omission reads better than the results would. Owner's call |

---

## 7. Blockers and open questions

1. **15-minute interval counts were discarded.** `parse_raw_counts.py` calls
   `find_total_row()` and keeps only that row, so ground truth is daily totals
   with no time-of-day resolution. Blocks per-interval validation (a daily
   total can be right for the wrong reasons). Needs modifying to emit every
   interval row between `data_start` and the total row, keeping the timestamp
   column. **Requires 2–3 raw `.xls` files to inspect the row structure.**
   (No longer blocks mining — see §5.1.)
2. **`review_sheet.csv` verdicts not yet readable.** The owner filled it in but
   saved as `.numbers` (compressed protobuf). Ask for a CSV export
   (Numbers → File → Export To → CSV). Once available, the REAL/DUP/PED/BIKE/FP
   tally sets `MIN_NET_DISPLACEMENT` and the confidence floors from evidence
   rather than guesswork.
3. **Vehicle counting has no ground truth.** See §4.
4. **Day/night cross-check not done.** `Bike lane study counts day v night.xlsx`
   Totals sheet has a % night column per corridor. If it says Colonial North is
   ~15% night against the pipeline's 39%, that confirms the night over-count
   without watching a single clip. Cheap and high-value.
5. **Hour-boundary double-counting.** Chunks are tracked independently, so a
   crossing spanning an hour boundary counts twice. Expected < 1 per session;
   unmeasured.
6. **Disk.** All 41 sessions extracted = 325 GB vs ~314 GB free on a shared
   filesystem at 85%. `extract → count → delete` is mandatory; use
   `cleanup_session.sh` (refuses to delete unless every chunk has results).

---

## 8. File map

**Active pipeline**
| File | Role |
|---|---|
| `pilot_detect_v2.py` | main detector+tracker; tiling, fusion, confirmation, rendering |
| `vru_tracker.py` | association, track merging, class resolution |
| `extract_frames.py` | dataset builder (has `fuse_cyclists`, `cyclist` class) |
| `build_site_mapping.py` | video ↔ ground-truth join → `video_site_mapping.csv` |
| `validate_counts.py` | counts vs ground truth, day/night analysis |
| `audit_tracks.py` | flags duplicates/static/ID-jumps; emits review sheet |
| `plan_cyclist_clips.py` | builds clip render lists |
| `tracker_ablation.py` | old-vs-new association comparison (paper figure) |
| `Bike Lane Study Counts/fix_ground_truth.py` | recovers facility_type/movement |

**Slurm:** `run_site_array.slurm` (48-chunk array), `extract_session.slurm`,
`run_render_clips.slurm`, `run_v2_window.slurm`, `run_v2_full.slurm`,
`run_ablation.slurm`, `build_dataset.slurm`
**Shell:** `cleanup_session.sh`, `organize_repo.sh`

**Key data**
- `Bike Lane Study Counts/ground_truth_bicycle_counts_v2.csv` — **use `_v2`**;
  the original has empty `facility_type`/`movement` in all 202 rows
- `video_site_mapping.csv` — 41/41 matched
- `all_videos.txt` — archive inventory **and** the source of chunk→wall-clock
  times (`.001` = 05:00)
- `pilot_output/sessions/<SITE>_<DATE>/*_tracks.csv` — per-track results
- `pilot_detect_41807016.log` — cited evidence for the tracker diagnosis; keep
- `MioVision_Data.zip` — irreplaceable source; never delete

---

## 9. Conventions that matter

- Never run YOLO on the login node; always `sbatch`.
- Check on-disk chunk count against `n_mp4_chunks` **before** counting. A
  session with 2 of 48 chunks extracted produced 48 `COMPLETED` Slurm tasks and
  a plausible-looking −88% "error" — doing nothing is not an error.
- Detection runs at `conf=0.05` on purpose (track-before-detect). Do **not**
  raise it to clean up the video; that reintroduces the original zero-cyclists
  bug. Change the *rendering*, not the detection.
- ROI is deliberately the full frame. Cropping to the bike lane would discard
  78% of cyclists, who ride on sidewalks.
- Array ranges: most sessions are 48 chunks but Rinehart Road SW is 96, two are
  49, three are under 40. Under-provisioning silently biases counts **down**.

Owner confirmation (2026-10-20): all32person-box frames, including empty frames, were inspected; unchecked boxes were accidental. Original JSON preserved. `person_box_review_confirmed_20261020.json` marks all32reviewed based on explicit owner confirmation and retains all20boxes. Prediction pack still required for scoring; no accuracy calculated yet.

Confirmed person-box scoring completed locally (2026-10-20): found existing pack at `/Users/rithika/Downloads/final_review_20261020/rf_boxes`. All32owner-confirmed frames,20human boxes, one-to-one IoU>=0.50, saved thresholds. RF-DETR:4TP/10FP/16FN, precision28.6%, recall20.0%. Grounding DINO:13TP/35FP/7FN, precision27.1%, recall65.0%. DINO finds more labelled person boxes but generates more false boxes; neither is a demonstrated replacement for the counting reference. Selected repeated frames, not unique people/AP/whole-video cyclist accuracy or an independent holdout. Report: `vision3/best/test_colonial/exp_results/RF_DINO_person_validation_20261020.md`. Earlier statements that pack was unavailable or no score existed are superseded.

Received root colonial_speed_gates.json: two facilities with35ft/30ft and720x480reference, reviewer Rithika, but measurement_source="n/a". Original preserved. No physical speed calculated: exact measured endpoint correspondence not established. Asked owner whether these are known study endpoints or visible lane ends. Added placeholder-source rejection in exporter and speed measurement plus regression test. Numeric workbook lengths must not be assigned to arbitrary scene-wide segments.

Owner clarification (2026-10-20): colonial_speed_gates.json marks visible lane ends, NOT known study measurement endpoints. Therefore it is unsuitable for mph calculation; do not replace its n/a source or accept35ft/30ft for those drawn spans. Original preserved; review decision in exp_results/colonial_speed_gate_review_20261020.json. Physical speed remains blocked pending identifiable independently measured endpoints (or appropriate metric calibration). Image-motion estimates remain available; no further GPU run needed.

Exploratory calibration attempted locally (2026-10-20) at owner request: new code/exploratory_gate_check.py checks estimated finite gates without granting physical distance. Output exp_results/exploratory_speed_calibration_20261020/{RESULTS.md,crossings.csv,summary.json}. All7actual bicycle truth rows checked, both facilities (14checks), full saved unverified candidate tracks;0complete two-line crossings. None crosses the first line. Workbook rescanned:23Colonial speed records but0verified person links; no timestamps found in these speed rows. Thus0distance fits/0held-out validation pairs, no mph/MAE. Do not pair records by nearest speed or equate study record IDs with track IDs. Future fit requires independently matched people and crossings, fixed facility distance, and different people for validation. Three crossing tests pass (clip-time interpolation, finite-line nonextension, large-gap exclusion). No inference/batch submitted; original gates/truth untouched.
