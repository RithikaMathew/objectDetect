# Start here: final validation

The detector experiments have results; the remaining work is checking identities, lanes and physical speed—not another model sweep. Current reference: b4_combo_static5, **19/21 under legacy time matching**, with no extra counted tracks on the four labelled clips. This is not identity-verified or general accuracy. TTA, broad sensitivity and brightening did not improve the reference.

## Detector versus X-CLIP — already compared, no Slurm required

[Saved comparison](vision3/best/test_colonial/exp_results/classifier_comparison_20261020/RESULTS.md) and [per-person rows](vision3/best/test_colonial/exp_results/classifier_comparison_20261020/per_person.csv): on the SAME21 matched/scored tracks, detector track-majority labels are correct16/21(76.2%), raw weighted X-CLIP labels14/21(66.7%). Detector wins overall here; X-CLIP labels more cyclists correctly6/8vs5/8 (includes one motorcycle in both denominators). Detector labels more pedestrians correctly11/13vs8/13. Both right11, both wrong2, detector-onlyright5, X-CLIP-onlyright3.

This is provisional TIME-MATCHED track classification, not independent detector recall or standalone counting accuracy. It includes the rejected short rider and uses raw rules-audit X-CLIP labels BEFORE fusion; the misleading post-rule tracks.csv field is not used. No new inference or threshold tuning. Keep both signals pending identity review. `code/compare_classifiers.py` regenerates the report into a NEW output folder and optionally accepts `--identity-map` to evaluate only human-approved identities.

## One command for ALL pending batch jobs

After pushing these changes on your Mac, pull on HiPerGator and submit **once**:

```bash
cd /orange/xiangyan/rithika/vision
git pull --ff-only origin main
cd vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
python code/submit_final_batch.py --go
```

This submits **five jobs**: reference-system Anderson2021, reference-system CurryFordNorth2022, existing-frame review/zone/speed-gate pages, GT-header copies of existing videos, and a final report after all four jobs end. It reuses the completed RF/DINO audits; no new detector sweep. Default without `--go` is a dry-run. Required inputs and duplicate manifest/output paths are checked before submission. If submission stops part-way, inspect `logs/newsites_oct20/manifest.json`; do not blindly resubmit.

Read **`exp_results/NEWSITES_newsites_oct20.md`** afterward. Review materials: `exp_results/final_review_20261020/`; header copies: `annotated_gt/`. Human identity approvals, box labels, lane checks, actual speed-gate endpoints and study-record links cannot be completed by submitting jobs alone. This batch does not invent validated mph.

**Exact best-system duration rules:** normal minimum **3 seconds for cyclists and pedestrians during both day and night**. During21:00–06:00 only, a cyclist can use an exception down to **0.3 seconds** if its final class is cyclist, at least90%of detector observations are cyclist, and weighted X-CLIP cyclist probability is at least0.90. This is NOT a blanket0.4-second night minimum. These settings are explicitly pinned in new-site manifests. Broad sensitive0.4-second settings remain off.

Do **not** also submit the standalone new-site, final-review or header commands below if you use this combined launcher; those sections explain the individual tools.

## Final validation — updated October 20

**Stop additional detector/model sweeps.** Completed experiments are documented; [current to-do audit](docs/tasks/todo.md) identifies the final checks still open. Code implementation is not the same as validation.

Latest presentation is a **new copy**, preserving your added fusion, speed and per-clip results slides: [October20 reviewed deck](reports/presentations/bike_weekly_meeting_10_20_reviewed.pptx). The saved October19 owner deck is unchanged. Future presentation edits must always create a new copy.

**Relaxed/sensitive = confidence 0.15 (rather than 0.25), 0.4 s minimum BOTH day/night, static rejection OFF.** That failed experiment is not enabled in the reference or new-site runs. Reference remains normal 3 s, with its existing strict night-only short-cyclist exception. Historical experiment code/results stay reproducible.

### Existing labelled people: lanes and speed

[Analysis](vision3/best/test_colonial/exp_results/labelled_validation_20261020/RESULTS.md) and [21-row table](vision3/best/test_colonial/exp_results/labelled_validation_20261020/people_lane_speed.csv): candidate track lanes and image motion only. Twelve sidewalk, three bike-lane (one is the motorcycle grouped with cyclists in the old evaluation), one road, five uncertain; **none is yet lane/identity validated**. Twenty candidates have enough samples for image speed; one does not. Metric mph is blank.

[23 extracted Colonial speed records](vision3/best/test_colonial/exp_results/labelled_validation_20261020/Colonial_study_speed_records.csv) include35-foot bike-lane and30-foot sidewalk lengths. Duplicate analysis-sheet records were merged; one e-bike is explicitly flagged. Source mph and exact-unit recomputation are retained. These ARE Colonial rows; an earlier initial-preview statement that no Colonial records existed was incorrect.

The supplied `zones/colonial_north_v2.json` defines lane AREA polygons; it does not identify the measured segment start/end cross-lines. Source record numbers are not the existing n1/d1/h1/p1 truth IDs and have no video timestamps. Believed correspondence still needs a recorded link. Do not infer metric speed from assumed person height or fit it to the workbook means. [Study aggregate lane-count comparison](vision3/best/test_colonial/exp_results/labelled_validation_20261020/study_lane_comparison.csv) is a contextual comparison, not person-level lane validation; historical counts disagree with hand truth in the21:15bin.

### One final CPU review build (no new inference)

After push/pull, from cluster `vision3/best/test_colonial` with yolo_env activated:

```bash
sbatch code/final_review.slurm
```

Download the **whole** `exp_results/final_review_20261020/` directory to your Mac:

- `rf_boxes/review.html`: draw tight boxes around EVERY human on selected raw frames, including riders; tick reviewed even for empty frames; export `person_box_review.json`. This uses existing audit outputs, not another detector run. Simultaneous encounters share a frame; at most37selectedframes, rather than all165.
- `zone_previews/*.png`: check v2 bike/sidewalk/road boundaries against the actual image. Do not approve a lane solely from a CSV.
- `speed_gate_setup.html`: if you know the actual measured35-foot/30-foot segments, click the two cross-lines per facility, confirm the camera/date, enter evidence/reviewer, and download `colonial_speed_gates.json`. No geometry or distance is guessed.

Score the person-box review on either machine with the whole pack and exported JSON available:

```bash
python code/rf_person_review.py score --pack exp_results/final_review_20261020/rf_boxes --review /path/to/person_box_review.json --out exp_results/RF_DINO_person_validation.md
```

This computes person-box precision and recall at one-to-oneIoU≥0.5 on explicitly reviewed frames. It does **not** validate cyclist labels, continuous-video counts, AP or unseen-site accuracy. Unreviewed frames are excluded, never treated as zero people. You may instead close these audits as unvalidated exploratory results; no claim of detector improvement is required.

### Prevent false credit from ID switches

The old19/21score remains labelled time-only. New strict mode gives unreviewed matches **UNVERIFIED**, not FOUND. Review the complete track, including before/after the person's truth window, before approving. Fill [identity_review.csv](vision3/best/test_colonial/exp_results/labelled_validation_20261020/identity_review.csv): correcttrack_id, decision=approved, full_track_reviewed=yes, reviewer and evidence. No extra40-track campaign or repeat class/time labels are requested. Rejected/switching tracks must not be approved; fixing tracker association is distinct from fixing evaluation credit.

```bash
python code/eval_truth.py --root . --runs b4_combo_static5 --require-identity --identity-map exp_results/labelled_validation_20261020/identity_review.csv --out exp_results/EVAL_identity_reviewed.md
```

**Speed after gate measurements:** re-run `code/labelled_lane_speed.py` with the study-directory path, a NEW `--out` directory, approved `--identity-map` if available and `--speed-gates /path/to/colonial_speed_gates.json`. Only tracks crossing both measured finite gates get mph estimates. Fill `study_record_links.csv` with explicit record-to-person matches and pass `--record-links /path/to/study_record_links.csv` to compute paired speed errors/MAE/RMSE. Only identity-approved people with measured mph and evidenced study links contribute; estimates and validation are different outputs. Original sources/results stay untouched.

## New request: best system on two additional sites / years

After committing/pushing on the Mac and pulling on HiPerGator, submit **once**:

```bash
cd /orange/xiangyan/rithika/vision
git pull --ff-only origin main
cd vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
python code/submit_newsites.py --go
```

This submits two GPU jobs plus a dependent CPU report: **Anderson St (2021)** and **Curry Ford North (2022)**, one 15-minute daytime window each. It uses the full reference system: fine-tuned RT-DETR (“V3”) + SAHI + ByteTrack/ID stitching + X-CLIP + detector/motion/duration/static rules. No TTA or brightening. Pixel settings scale to video width; no Colonial zone polygons are transferred. Selection prefers noon among readable existing hourly files, independent of detector success; no full-day inference. Missing source folders cause an explicit pre-submission error, not substitute videos.

Read **`exp_results/NEWSITES_newsites_oct20.md`** after completion. It prints the actual annotated video paths, predicted counts, duration, runtime and failures. Sources/clocks are recorded in `logs/newsites_oct20/manifest.json`; first-frame clock is inferred from source naming and must be checked against the embedded camera clock. Jobs have not been run from this Mac. Omit `--go` to preview without submission. Existing manifest/output folders prevent duplicate submissions.

These sites are new to this validation, but both appear in the documented training-data recipe; this is **not a strictly unseen-site evaluation**. It is also not a higher-resolution experiment. Complete human truth is unavailable, so predicted totals are not accuracy and the video headers say `GT: not labelled`.

For Corrine, use the exact paths in [video paths](docs/VIDEO_PATHS.md), also included in the presentation’s final-slide notes. At each of the same two distant cyclists/e-scooter timestamps, compare baseline, combination and TTA: box present, label correct, ID stays on that person, counted once? Return the video-player timestamp and ID for each problem. A parked-car annotation may be suppressed by the moving-vehicle filters.


Source results: [completed batch report](RESEARCH_research_oct19.md), [terminal results](results.md), [exact video paths](docs/VIDEO_PATHS.md), [current handoff](docs/history/HANDOFF.md). Historical commands/docs are background; do not resubmit the old research suite.

Once the measured gates and human links are ready, you can run physical-speed analysis on the Mac (no GPU):

```bash
cd /Users/rithika/Desktop/objectDetect
python3 vision3/best/test_colonial/code/labelled_lane_speed.py \
  --study-dir "Bike Lane Study Counts" \
  --out vision3/best/test_colonial/exp_results/labelled_speed_measured_20261020 \
  --identity-map vision3/best/test_colonial/exp_results/labelled_validation_20261020/identity_review.csv \
  --speed-gates "$HOME/Downloads/colonial_speed_gates.json" \
  --record-links vision3/best/test_colonial/exp_results/labelled_validation_20261020/study_record_links.csv
```

Use a new output-folder name for a later repeat. An empty or unverified correspondence file cannot produce validated speed errors.
