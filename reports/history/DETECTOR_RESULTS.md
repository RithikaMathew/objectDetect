# Historical detector results

These are completed experiment reports, preserved for evidence. They are not a list of pending jobs.

## Contents

- [CODEX_continuation_20261019.md](#report-codex-continuation-20261019)
- [EVAL_20261007_2313.md](#report-eval-20261007-2313)
- [EVAL_20261008_0830.md](#report-eval-20261008-0830)
- [EVAL_20261009_0047.md](#report-eval-20261009-0047)
- [EVAL_20261009_0202.md](#report-eval-20261009-0202)
- [EVAL_20261010_2251.md](#report-eval-20261010-2251)
- [EVAL_20261012_0003.md](#report-eval-20261012-0003)
- [EVAL_20261015_2225.md](#report-eval-20261015-2225)
- [EVAL_20261015_2314.md](#report-eval-20261015-2314)
- [EVAL_20261019_1040.md](#report-eval-20261019-1040)
- [EVAL_batch2_20261008_1612.md](#report-eval-batch2-20261008-1612)
- [EVAL_batch3_20261010_2152.md](#report-eval-batch3-20261010-2152)
- [EVAL_batch4_20261011_1355.md](#report-eval-batch4-20261011-1355)
- [EVAL_batch4_20261011_1410.md](#report-eval-batch4-20261011-1410)
- [EVAL_batch5_codex_20261019.md](#report-eval-batch5-codex-20261019)
- [FUSION_PROBE_20261008_1612.md](#report-fusion-probe-20261008-1612)
- [FUSION_PROBE_20261009_0042.md](#report-fusion-probe-20261009-0042)
- [FUSION_PROBE_20261009_0047.md](#report-fusion-probe-20261009-0047)
- [FUSION_PROBE_20261009_0202.md](#report-fusion-probe-20261009-0202)
- [FUSION_PROBE_20261010_2251.md](#report-fusion-probe-20261010-2251)
- [FUSION_PROBE_20261010_2338.md](#report-fusion-probe-20261010-2338)
- [FUSION_PROBE_20261012_0003.md](#report-fusion-probe-20261012-0003)
- [FUSION_batch3_20261010_2152.md](#report-fusion-batch3-20261010-2152)
- [FUSION_batch4_20261011_1355.md](#report-fusion-batch4-20261011-1355)
- [FUSION_batch4_20261011_1410.md](#report-fusion-batch4-20261011-1410)
- [FUSION_cases_20261019.md](#report-fusion-cases-20261019)
- [MANIFEST_20261007_2313.md](#report-manifest-20261007-2313)
- [MANIFEST_batch2_20261008_1612.md](#report-manifest-batch2-20261008-1612)
- [NEWSITES_newsites_oct20.md](#report-newsites-newsites-oct20)
- [RF_DINO_person_validation_20261020.md](#report-rf-dino-person-validation-20261020)
- [newsites_owner_review_20261020.md](#report-newsites-owner-review-20261020)

<a id="report-codex-continuation-20261019"></a>
## CODEX_continuation_20261019.md
Original location: `vision3/best/test_colonial/exp_results/CODEX_continuation_20261019.md`.


## 41. Codex continuation (2026-10-19): batch-5 results and recovery

This section supersedes the queued-job assumptions in do.md. Local copies of the actual track tables and truth files were re-scored with eval_truth.py; they reproduce look.md. These are existing GPU results, not new inference runs.

| Settings | Correctly counted AND labelled | Interpretation |
|---|---:|---|
| Current best b4_combo_static5 | 19/21 (90.5%) | Keep this configuration |
| Without speed b5_nospeed | 17/21 (81.0%) | Speed adds two correct classifications in this comparison |
| Without detector veto b5_noveto | 18/21 (85.7%) | Veto adds one correct classification in this comparison |
| Best, night clips only | 9/11 (81.8%) | Reference for brightening |
| Gamma, night clips only | 8/11 (72.7%) | Worse by one person |
| CLAHE, night clips only | 5/11 (45.5%) | Worse by four people |
| Zero-DCE | No result | Both jobs failed before inference; do not score as zero accuracy |

No extra counted tracks were reported for the completed runs. Wrong-class people are still errors even though they are real people. FOUND means counted with the correct class; detected-not-counted means the model made a track but rejected it; missed means no matched track; extra means a counted track without a matched truth person. A 0/0 entry means that class has no truth examples in that clip, not a failure. The best run's two failures remain one pedestrian labelled cyclist and one short cyclist track rejected. Thus its totals are 8 cyclists / 12 pedestrians versus truth 8 / 13: the apparently exact cyclist total hides a missed cyclist and a wrongly included pedestrian.

These are encouraging development results, not evidence of 90.5% accuracy across sites/years. All 21 people are from one camera/day and these clips have been inspected repeatedly. The speed/veto gains are marginal contributions with other rules active; do not add them as independent gains. Speed remains image movement in body heights/second, not measured MPH. Runtime is about 42 minutes per 15-minute clip (~2.8 times video duration).

### Failures verified in logs and code fixes

* pick_busy job 46141085 failed because the default path omitted /weights/ before best.pt. Fixed pick_busy_windows.py to match the working detector path in the v19 Slurm file, support WEIGHTS, and reject a missing file before importing/loading the detector. pick_busy.slurm now stops on shell errors.
* Zero-DCE jobs 46141059_22 and 46141060_23 failed because ZERODCE_WEIGHTS was unset. run_batch5.py now requires an existing checkpoint before submission and exports it. --modes zerodce selects only those two failed jobs; gamma/CLAHE/ablation need no repeat. Submission failures now stop immediately and preserve a submission log/lock; the lock is reserved before the first job.
* The grep errors and missing busy directory in look.md were initially caused by running inside code/. They do not prove all jobs failed. The actual logs are under test_colonial/logs/.
* Bin AI is a fixed whole-bin total from the render snapshot, not a live counter. Hour so far is the frame-time live counter, which can also revise a label as evidence arrives. Changed the fixed label to AI total (AI snapshot for streamed/provisional clips), preserving GT. Old annotated videos retain old text until rendered again. Streaming snapshots may differ from final CSV totals; existing mismatch logging records that.
* undistort_fisheye.py now offers --coverage full-frame for rectangular images: the guessed FOV is interpreted diagonally instead of forcing an inscribed short-side circle. The old circular default stays available. This is not lens calibration. No original 2025 frame, both.png, or preview.png is present in this checkout, so no visual choice of FOV/pitch has been made. Encoder failure now reports an error rather than success.
* test_v19.py now resolves its source file relative to itself so it can run from test_colonial.

### Cluster recovery (after copying the changed code files to the same code/ folder)

Run from test_colonial, never code/:

```bash
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
# Retry the failed scan ONCE. This scans the four paths in videos_to_scan.txt.
sbatch code/pick_busy.slurm
# After that job completes:
cat busy/inventory.csv
cat busy/windows.txt
# Locate the existing Zero-DCE checkpoint (do not invent a path):
find /orange/xiangyan/rithika/vision -type f -name Epoch99.pth -print
```

Only if a checkpoint is found, use its full path below (replace /actual/path/Epoch99.pth). First dry-run, then submit once. --force is required only because the old bright-group submission lock already exists; check squeue before using it.

```bash
python code/run_batch5.py bright --modes zerodce --zerodce-weights /actual/path/Epoch99.pth
squeue -u "$USER"
python code/run_batch5.py bright --modes zerodce --zerodce-weights /actual/path/Epoch99.pth --go --force
```

The 14 batch-5 jobs were 8 ablations (two settings x four existing labelled windows) plus 6 brightening jobs (three modes x two existing night windows). They were NOT seven distinct videos. The separate scan list has four input paths: two 2022 Curry Ford hourly files and two 2025 Corrine camera files. A scan chooses windows; it does not run the full counting pipeline on them. No 2023/2024 file appears in this list.

### Research corrections and remaining work

BNE-DETR DOES have a public source repository: https://github.com/luy02735-lang/BNE-DETR (verified 2026-10-19; root folders benchmark, dataset, rtdetr_pytorch). The prior blanket suggestion that no implementation exists was too strong. Pretrained-weight availability, dependencies and compatibility with our person/cyclist model remain unverified; no model replacement or training was performed.

The requested technique for an object appearing in a still scene exists: background subtraction (MOG2/KNN), documented at https://docs.opencv.org/4.x/d1/dc5/tutorial_background_subtraction.html . This pipeline already has MotionDiag and --motion-diag. Its existing synthetic test confirms it flags an unexplained blob and ignores an explained one. Prior real-clip output had too many candidates (447/185); no measured improvement has been established. A changed region can be shadow/light/foliage, not necessarily a person. A next experimental version would crop/re-detect unexplained regions and evaluate recovered people AND added false tracks; it should remain separate from the best configuration until scored.

Remaining dependent steps: run the repaired scan on HiPerGator; inspect/cut its selected clips; obtain the original fisheye frame and compare full-frame previews before selecting lens settings; run and hand-label the new-year clips. Keep fine-tuning and 24/48-hour scale-up deferred per section 40. No empty truth files were created and no model weights or existing result tables were overwritten.

Validation locally: re-evaluated saved tables (matches look.md); four recovery regression tests pass (missing checkpoint, selective retry, failed-submission stop/lock, rectangular mapping); existing test_v19.py passes (slicing, merging, enhancement, speed, motion diagnostic); fisheye selftest passes (4.57/255 centre difference). No GPU inference or Slurm jobs submitted from this Mac. Synthetic mapping tests do not establish that undistortion improves real detections.


<a id="report-eval-20261007-2313"></a>
## EVAL_20261007_2313.md
Original location: `vision3/best/test_colonial/exp_results/EVAL_20261007_2313.md`.

# Experiment evaluation  (2026-10-08 03:12)

root: /orange/xiangyan/rithika/vision/vision3/best/test_colonial
runs: exp0_base, exp1_sahi, exp2_gamma, exp2_clahe, exp2_zerodce, exp3a_speed, exp3b_short

- truth night: 4 usable rows (4 cyclist incl. motorcycle, 0 pedestrian); skipped 2: n5 (start='14:23', class='NOT detected: the cyclist that was missed'); n6 (start='14:53', class='NOT detected: the last pedestrian')
- truth day: 5 usable rows (1 cyclist incl. motorcycle, 4 pedestrian); skipped 0: none

## Summary (person level; FOUND = counted with the right class; motorcycle scored as cyclist)

| run | clip | cyclists found | pedestrians found | wrong class | detected, not counted | missed | extra counted | counted bic/ped | runtime min |
|---|---|---|---|---|---|---|---|---|---|
| exp0_base | night | 0/4 | 0/0 | 0 | 4 | 0 | 0 | 0/0 | 30.1 |
| exp0_base | day | 1/1 | 2/4 | 0 | 2 | 0 | 0 | 1/2 | 30.6 |
| exp1_sahi | night | 2/4 | 0/0 | 1 | 1 | 0 | 1 | 3/1 | 42.2 |
| exp1_sahi | day | 1/1 | 2/4 | 2 | 0 | 0 | 0 | 3/2 | 43.1 |
| exp2_gamma | night | 0/4 | 0/0 | 0 | 3 | 1 | 0 | 0/0 | 30.1 |
| exp2_clahe | night | 0/4 | 0/0 | 0 | 4 | 0 | 0 | 0/0 | 31.1 |
| exp2_zerodce | night | 0/4 | 0/0 | 0 | 4 | 0 | 0 | 0/0 | 34.6 |
| exp3a_speed | night | 0/4 | 0/0 | 0 | 4 | 0 | 0 | 0/0 | 29.9 |
| exp3a_speed | day | 0/1 | 2/4 | 1 | 2 | 0 | 0 | 0/3 | 28.5 |
| exp3b_short | night | 2/4 | 0/0 | 0 | 2 | 0 | 0 | 2/0 | 29.4 |
| exp3b_short | day | 1/1 | 2/4 | 0 | 2 | 0 | 1 | 2/2 | 28.8 |

## Detail

### exp0_base - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:03-4:04 | DETECTED BUT NOT COUNTED | #1 cyclist 0.6s counted=0 det=cyclist (100.0% cyc) |
| n2 | cyclist | 7:07-7:08 | DETECTED BUT NOT COUNTED | #2 cyclist 0.43s counted=0 det=cyclist (100.0% cyc) |
| n3 | cyclist | 14:21-14:22 | DETECTED BUT NOT COUNTED | #4 cyclist 0.9s counted=0 det=cyclist (59.3% cyc) |
| n4 | cyclist | 14:29-14:30 | DETECTED BUT NOT COUNTED | #7 pedestrian 1.0s counted=0 det=cyclist (100.0% cyc) |

### exp0_base - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #3 pedestrian 3.2s counted=1 det=person (0.0% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #5 cyclist 4.04s counted=1 det=person (34.7% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #8 pedestrian 16.85s counted=1 det=person (0.2% cyc) |
| d4 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #12 pedestrian 2.07s counted=0 det=person (0.0% cyc) |
| d5 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #13 pedestrian 1.2s counted=0 det=person (0.0% cyc) |

### exp1_sahi - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:03-4:04 | DETECTED BUT NOT COUNTED | #4 cyclist 1.2s counted=0 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:07-7:08 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:22 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:29-14:30 | WRONG CLASS | #22 pedestrian 3.44s counted=1 det=cyclist (59.2% cyc) |
| EXTRA | counted cyclist | 14:44-14:59 | no truth row | #23 10.58s det=cyclist |

### exp1_sahi - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | WRONG CLASS | #2 cyclist 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | WRONG CLASS | #13 cyclist 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### exp2_gamma - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:03-4:04 | DETECTED BUT NOT COUNTED | #2 cyclist 0.4s counted=0 det=cyclist (66.7% cyc) |
| n2 | cyclist | 7:07-7:08 | MISSED |  |
| n3 | cyclist | 14:21-14:22 | DETECTED BUT NOT COUNTED | #5 cyclist 0.57s counted=0 det=cyclist (64.7% cyc) |
| n4 | cyclist | 14:29-14:30 | DETECTED BUT NOT COUNTED | #6 cyclist 0.47s counted=0 det=cyclist (92.9% cyc) |

### exp2_clahe - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:03-4:04 | DETECTED BUT NOT COUNTED | #6 cyclist 0.33s counted=0 det=cyclist (70.0% cyc) |
| n2 | cyclist | 7:07-7:08 | DETECTED BUT NOT COUNTED | #9 cyclist 0.3s counted=0 det=cyclist (100.0% cyc) |
| n3 | cyclist | 14:21-14:22 | DETECTED BUT NOT COUNTED | #14 unscored 0.2s counted=0 det=cyclist (100.0% cyc) |
| n4 | cyclist | 14:29-14:30 | DETECTED BUT NOT COUNTED | #15 unscored 0.07s counted=0 det=cyclist (100.0% cyc) |

### exp2_zerodce - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:03-4:04 | DETECTED BUT NOT COUNTED | #1 cyclist 0.4s counted=0 det=cyclist (100.0% cyc) |
| n2 | cyclist | 7:07-7:08 | DETECTED BUT NOT COUNTED | #2 cyclist 0.67s counted=0 det=cyclist (80.0% cyc) |
| n3 | cyclist | 14:21-14:22 | DETECTED BUT NOT COUNTED | #5 unscored 0.1s counted=0 det=cyclist (100.0% cyc) |
| n4 | cyclist | 14:29-14:30 | DETECTED BUT NOT COUNTED | #6 unscored 0.17s counted=0 det=cyclist (100.0% cyc) |

### exp3a_speed - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:03-4:04 | DETECTED BUT NOT COUNTED | #1 cyclist 0.6s counted=0 det=cyclist (100.0% cyc) |
| n2 | cyclist | 7:07-7:08 | DETECTED BUT NOT COUNTED | #2 cyclist 0.43s counted=0 det=cyclist (100.0% cyc) |
| n3 | cyclist | 14:21-14:22 | DETECTED BUT NOT COUNTED | #4 cyclist 0.9s counted=0 det=cyclist (59.3% cyc) |
| n4 | cyclist | 14:29-14:30 | DETECTED BUT NOT COUNTED | #7 pedestrian 1.0s counted=0 det=cyclist (100.0% cyc) |

### exp3a_speed - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #3 pedestrian 3.2s counted=1 det=person (0.0% cyc) |
| d1 | cyclist | 9:10-9:19 | WRONG CLASS | #5 pedestrian 4.04s counted=1 det=person (34.7% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #8 pedestrian 16.85s counted=1 det=person (0.2% cyc) |
| d4 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #12 pedestrian 2.07s counted=0 det=person (0.0% cyc) |
| d5 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #13 pedestrian 1.2s counted=0 det=person (0.0% cyc) |

### exp3b_short - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:03-4:04 | FOUND | #1 cyclist 0.6s counted=1 det=cyclist (100.0% cyc) |
| n2 | cyclist | 7:07-7:08 | FOUND | #2 cyclist 0.43s counted=1 det=cyclist (100.0% cyc) |
| n3 | cyclist | 14:21-14:22 | DETECTED BUT NOT COUNTED | #4 cyclist 0.9s counted=0 det=cyclist (59.3% cyc) |
| n4 | cyclist | 14:29-14:30 | DETECTED BUT NOT COUNTED | #7 pedestrian 1.0s counted=0 det=cyclist (100.0% cyc) |

### exp3b_short - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #3 pedestrian 3.2s counted=1 det=person (0.0% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #5 cyclist 4.04s counted=1 det=person (34.7% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #8 pedestrian 16.85s counted=1 det=person (0.2% cyc) |
| d4 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #12 pedestrian 2.07s counted=0 det=person (0.0% cyc) |
| d5 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #13 pedestrian 1.2s counted=0 det=person (0.0% cyc) |
| EXTRA | counted cyclist | 3:03-3:05 | no truth row | #1 0.4s det=cyclist |

## Motion-diagnostic candidates (baseline run) overlapping truth rows

**night**: 447 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth n1 (motorcycle 4:03): cand 138 (2.97s, box h 22.5), cand 139 (3.0s, box h 16.9), cand 140 (1.43s, box h 21.2)
- truth n2 (cyclist 7:07): cand 212 (2.67s, box h 52.2), cand 213 (1.7s, box h 31.8), cand 214 (1.3s, box h 50.0), cand 215 (1.5s, box h 16.6), cand 216 (1.43s, box h 23.7), cand 217 (1.4s, box h 90.6), cand 218 (1.94s, box h 86.1), cand 219 (4.9s, box h 49.8), cand 220 (1.74s, box h 94.6)
- truth n3 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4)
- truth n4 (cyclist 14:29): cand 432 (7.07s, box h 33.1), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5), cand 438 (1.0s, box h 32.6), cand 439 (1.23s, box h 154.6), cand 440 (1.2s, box h 128.1), cand 441 (3.34s, box h 22.2)

**day**: 185 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth d2 (pedestrian 3:00): cand 30 (2.57s, box h 19.2), cand 33 (12.18s, box h 71.5), cand 34 (0.87s, box h 84.7), cand 35 (1.13s, box h 19.8), cand 36 (1.13s, box h 40.9), cand 37 (1.07s, box h 34.5), cand 38 (1.97s, box h 61.7), cand 39 (1.17s, box h 43.4)
- truth d1 (cyclist 9:10): cand 108 (1.47s, box h 45.3), cand 109 (1.47s, box h 104.7), cand 110 (1.6s, box h 36.9), cand 111 (1.13s, box h 92.3), cand 112 (3.07s, box h 34.6)
- truth d3 (pedestrian 11:45): cand 142 (8.94s, box h 100.1), cand 144 (0.87s, box h 24.9), cand 145 (3.74s, box h 64.9), cand 146 (1.87s, box h 35.8), cand 147 (3.74s, box h 30.7), cand 148 (1.27s, box h 46.4), cand 149 (1.9s, box h 34.1), cand 150 (1.17s, box h 26.5), cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1)
- truth d4 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)
- truth d5 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)


<a id="report-eval-20261008-0830"></a>
## EVAL_20261008_0830.md
Original location: `vision3/best/test_colonial/exp_results/EVAL_20261008_0830.md`.

# Experiment evaluation  (2026-10-08 08:30)

root: /orange/xiangyan/rithika/vision/vision3/best/test_colonial
runs: exp0_base, exp1_sahi, exp2_clahe, exp2_gamma, exp2_zerodce, exp3a_speed, exp3b_short

- truth night: 4 usable rows (4 cyclist incl. motorcycle, 0 pedestrian); skipped 2: n5 (start='14:23', class='NOT detected: the cyclist that was missed'); n6 (start='14:53', class='NOT detected: the last pedestrian')
- truth day: 5 usable rows (1 cyclist incl. motorcycle, 4 pedestrian); skipped 0: none

## Summary (person level; FOUND = counted with the right class; motorcycle scored as cyclist)

| run | clip | cyclists found | pedestrians found | wrong class | detected, not counted | missed | extra counted | counted bic/ped | runtime min |
|---|---|---|---|---|---|---|---|---|---|
| exp0_base | night | 0/4 | 0/0 | 0 | 4 | 0 | 0 | 0/0 | 30.1 |
| exp0_base | day | 1/1 | 2/4 | 0 | 2 | 0 | 0 | 1/2 | 30.6 |
| exp1_sahi | night | 2/4 | 0/0 | 1 | 1 | 0 | 1 | 3/1 | 42.2 |
| exp1_sahi | day | 1/1 | 2/4 | 2 | 0 | 0 | 0 | 3/2 | 43.1 |
| exp2_clahe | night | 0/4 | 0/0 | 0 | 4 | 0 | 0 | 0/0 | 31.1 |
| exp2_gamma | night | 0/4 | 0/0 | 0 | 3 | 1 | 0 | 0/0 | 30.1 |
| exp2_zerodce | night | 0/4 | 0/0 | 0 | 4 | 0 | 0 | 0/0 | 34.6 |
| exp3a_speed | night | 0/4 | 0/0 | 0 | 4 | 0 | 0 | 0/0 | 29.9 |
| exp3a_speed | day | 0/1 | 2/4 | 1 | 2 | 0 | 0 | 0/3 | 28.5 |
| exp3b_short | night | 2/4 | 0/0 | 0 | 2 | 0 | 0 | 2/0 | 29.4 |
| exp3b_short | day | 1/1 | 2/4 | 0 | 2 | 0 | 1 | 2/2 | 28.8 |

## Detail

### exp0_base - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:03-4:04 | DETECTED BUT NOT COUNTED | #1 cyclist 0.6s counted=0 det=cyclist (100.0% cyc) |
| n2 | cyclist | 7:07-7:08 | DETECTED BUT NOT COUNTED | #2 cyclist 0.43s counted=0 det=cyclist (100.0% cyc) |
| n3 | cyclist | 14:21-14:22 | DETECTED BUT NOT COUNTED | #4 cyclist 0.9s counted=0 det=cyclist (59.3% cyc) |
| n4 | cyclist | 14:29-14:30 | DETECTED BUT NOT COUNTED | #7 pedestrian 1.0s counted=0 det=cyclist (100.0% cyc) |

### exp0_base - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #3 pedestrian 3.2s counted=1 det=person (0.0% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #5 cyclist 4.04s counted=1 det=person (34.7% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #8 pedestrian 16.85s counted=1 det=person (0.2% cyc) |
| d4 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #12 pedestrian 2.07s counted=0 det=person (0.0% cyc) |
| d5 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #13 pedestrian 1.2s counted=0 det=person (0.0% cyc) |

### exp1_sahi - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:03-4:04 | DETECTED BUT NOT COUNTED | #4 cyclist 1.2s counted=0 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:07-7:08 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:22 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:29-14:30 | WRONG CLASS | #22 pedestrian 3.44s counted=1 det=cyclist (59.2% cyc) |
| EXTRA | counted cyclist | 14:44-14:59 | no truth row | #23 10.58s det=cyclist |

### exp1_sahi - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | WRONG CLASS | #2 cyclist 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | WRONG CLASS | #13 cyclist 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### exp2_clahe - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:03-4:04 | DETECTED BUT NOT COUNTED | #6 cyclist 0.33s counted=0 det=cyclist (70.0% cyc) |
| n2 | cyclist | 7:07-7:08 | DETECTED BUT NOT COUNTED | #9 cyclist 0.3s counted=0 det=cyclist (100.0% cyc) |
| n3 | cyclist | 14:21-14:22 | DETECTED BUT NOT COUNTED | #14 unscored 0.2s counted=0 det=cyclist (100.0% cyc) |
| n4 | cyclist | 14:29-14:30 | DETECTED BUT NOT COUNTED | #15 unscored 0.07s counted=0 det=cyclist (100.0% cyc) |

### exp2_gamma - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:03-4:04 | DETECTED BUT NOT COUNTED | #2 cyclist 0.4s counted=0 det=cyclist (66.7% cyc) |
| n2 | cyclist | 7:07-7:08 | MISSED |  |
| n3 | cyclist | 14:21-14:22 | DETECTED BUT NOT COUNTED | #5 cyclist 0.57s counted=0 det=cyclist (64.7% cyc) |
| n4 | cyclist | 14:29-14:30 | DETECTED BUT NOT COUNTED | #6 cyclist 0.47s counted=0 det=cyclist (92.9% cyc) |

### exp2_zerodce - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:03-4:04 | DETECTED BUT NOT COUNTED | #1 cyclist 0.4s counted=0 det=cyclist (100.0% cyc) |
| n2 | cyclist | 7:07-7:08 | DETECTED BUT NOT COUNTED | #2 cyclist 0.67s counted=0 det=cyclist (80.0% cyc) |
| n3 | cyclist | 14:21-14:22 | DETECTED BUT NOT COUNTED | #5 unscored 0.1s counted=0 det=cyclist (100.0% cyc) |
| n4 | cyclist | 14:29-14:30 | DETECTED BUT NOT COUNTED | #6 unscored 0.17s counted=0 det=cyclist (100.0% cyc) |

### exp3a_speed - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:03-4:04 | DETECTED BUT NOT COUNTED | #1 cyclist 0.6s counted=0 det=cyclist (100.0% cyc) |
| n2 | cyclist | 7:07-7:08 | DETECTED BUT NOT COUNTED | #2 cyclist 0.43s counted=0 det=cyclist (100.0% cyc) |
| n3 | cyclist | 14:21-14:22 | DETECTED BUT NOT COUNTED | #4 cyclist 0.9s counted=0 det=cyclist (59.3% cyc) |
| n4 | cyclist | 14:29-14:30 | DETECTED BUT NOT COUNTED | #7 pedestrian 1.0s counted=0 det=cyclist (100.0% cyc) |

### exp3a_speed - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #3 pedestrian 3.2s counted=1 det=person (0.0% cyc) |
| d1 | cyclist | 9:10-9:19 | WRONG CLASS | #5 pedestrian 4.04s counted=1 det=person (34.7% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #8 pedestrian 16.85s counted=1 det=person (0.2% cyc) |
| d4 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #12 pedestrian 2.07s counted=0 det=person (0.0% cyc) |
| d5 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #13 pedestrian 1.2s counted=0 det=person (0.0% cyc) |

### exp3b_short - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:03-4:04 | FOUND | #1 cyclist 0.6s counted=1 det=cyclist (100.0% cyc) |
| n2 | cyclist | 7:07-7:08 | FOUND | #2 cyclist 0.43s counted=1 det=cyclist (100.0% cyc) |
| n3 | cyclist | 14:21-14:22 | DETECTED BUT NOT COUNTED | #4 cyclist 0.9s counted=0 det=cyclist (59.3% cyc) |
| n4 | cyclist | 14:29-14:30 | DETECTED BUT NOT COUNTED | #7 pedestrian 1.0s counted=0 det=cyclist (100.0% cyc) |

### exp3b_short - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #3 pedestrian 3.2s counted=1 det=person (0.0% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #5 cyclist 4.04s counted=1 det=person (34.7% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #8 pedestrian 16.85s counted=1 det=person (0.2% cyc) |
| d4 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #12 pedestrian 2.07s counted=0 det=person (0.0% cyc) |
| d5 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #13 pedestrian 1.2s counted=0 det=person (0.0% cyc) |
| EXTRA | counted cyclist | 3:03-3:05 | no truth row | #1 0.4s det=cyclist |

## Motion-diagnostic candidates (baseline run) overlapping truth rows

**night**: 447 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth n1 (motorcycle 4:03): cand 138 (2.97s, box h 22.5), cand 139 (3.0s, box h 16.9), cand 140 (1.43s, box h 21.2)
- truth n2 (cyclist 7:07): cand 212 (2.67s, box h 52.2), cand 213 (1.7s, box h 31.8), cand 214 (1.3s, box h 50.0), cand 215 (1.5s, box h 16.6), cand 216 (1.43s, box h 23.7), cand 217 (1.4s, box h 90.6), cand 218 (1.94s, box h 86.1), cand 219 (4.9s, box h 49.8), cand 220 (1.74s, box h 94.6)
- truth n3 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4)
- truth n4 (cyclist 14:29): cand 432 (7.07s, box h 33.1), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5), cand 438 (1.0s, box h 32.6), cand 439 (1.23s, box h 154.6), cand 440 (1.2s, box h 128.1), cand 441 (3.34s, box h 22.2)

**day**: 185 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth d2 (pedestrian 3:00): cand 30 (2.57s, box h 19.2), cand 33 (12.18s, box h 71.5), cand 34 (0.87s, box h 84.7), cand 35 (1.13s, box h 19.8), cand 36 (1.13s, box h 40.9), cand 37 (1.07s, box h 34.5), cand 38 (1.97s, box h 61.7), cand 39 (1.17s, box h 43.4)
- truth d1 (cyclist 9:10): cand 108 (1.47s, box h 45.3), cand 109 (1.47s, box h 104.7), cand 110 (1.6s, box h 36.9), cand 111 (1.13s, box h 92.3), cand 112 (3.07s, box h 34.6)
- truth d3 (pedestrian 11:45): cand 142 (8.94s, box h 100.1), cand 144 (0.87s, box h 24.9), cand 145 (3.74s, box h 64.9), cand 146 (1.87s, box h 35.8), cand 147 (3.74s, box h 30.7), cand 148 (1.27s, box h 46.4), cand 149 (1.9s, box h 34.1), cand 150 (1.17s, box h 26.5), cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1)
- truth d4 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)
- truth d5 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)


<a id="report-eval-20261009-0047"></a>
## EVAL_20261009_0047.md
Original location: `vision3/best/test_colonial/exp_results/EVAL_20261009_0047.md`.

# Experiment evaluation  (2026-10-09 00:47)

root: /orange/xiangyan/rithika/vision/vision3/best/test_colonial
runs: exp0_base, exp1_sahi, b2_0_base, b2_2_sahi, b2_3_sahi_fuse, b2_4_sahi_fuse_nightshort, b2_5_sahi_speed

- truth night: 6 usable rows (5 cyclist incl. motorcycle, 1 pedestrian); skipped 0: none
- truth day: 5 usable rows (1 cyclist incl. motorcycle, 4 pedestrian); skipped 0: none
- truth night_holdout_2200: 0 usable rows (0 cyclist incl. motorcycle, 0 pedestrian); skipped 2: t1 (start='10:04', class=''); t2 (start='10:12', class='')
- truth day_holdout_1245: 0 usable rows (0 cyclist incl. motorcycle, 0 pedestrian); skipped 6: h1 (start='0:40', class=''); h2 (start='8:07', class=''); h3 (start='8:46', class=''); h4 (start='9:54', class=''); h5 (start='11:17', class=''); h6 (start='', class='')

## Summary (person level; FOUND = counted with the right class; motorcycle scored as cyclist)

| run | clip | cyclists found | pedestrians found | wrong class | detected, not counted | missed | extra counted | counted bic/ped | runtime min |
|---|---|---|---|---|---|---|---|---|---|
| exp0_base | night | 0/5 | 0/1 | 0 | 4 | 2 | 0 | 0/0 | 30.1 |
| exp0_base | day | 1/1 | 2/4 | 0 | 2 | 0 | 0 | 1/2 | 30.6 |
| exp1_sahi | night | 2/5 | 0/1 | 2 | 2 | 0 | 0 | 3/1 | 42.2 |
| exp1_sahi | day | 1/1 | 2/4 | 2 | 0 | 0 | 0 | 3/2 | 43.1 |
| b2_0_base | night_holdout_2200 | 0/0 | 0/0 | 0 | 0 | 0 | 0 | 0/0 | 28.8 |
| b2_0_base | day_holdout_1245 | 0/0 | 0/0 | 0 | 0 | 0 | 5 | 4/1 | 28.7 |
| b2_2_sahi | night_holdout_2200 | 0/0 | 0/0 | 0 | 0 | 0 | 7 | 0/7 | 43.1 |
| b2_2_sahi | day_holdout_1245 | 0/0 | 0/0 | 0 | 0 | 0 | 5 | 4/1 | 42.3 |
| b2_3_sahi_fuse | night | 2/5 | 0/1 | 2 | 2 | 0 | 0 | 3/1 | 42.0 |
| b2_3_sahi_fuse | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 41.4 |
| b2_3_sahi_fuse | night_holdout_2200 | 0/0 | 0/0 | 0 | 0 | 0 | 7 | 0/7 | 42.5 |
| b2_3_sahi_fuse | day_holdout_1245 | 0/0 | 0/0 | 0 | 0 | 0 | 5 | 3/2 | 41.7 |
| b2_4_sahi_fuse_nightshort | night | 3/5 | 0/1 | 2 | 1 | 0 | 0 | 4/1 | 41.6 |
| b2_4_sahi_fuse_nightshort | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 42.1 |
| b2_4_sahi_fuse_nightshort | night_holdout_2200 | 0/0 | 0/0 | 0 | 0 | 0 | 7 | 0/7 | 41.9 |
| b2_4_sahi_fuse_nightshort | day_holdout_1245 | 0/0 | 0/0 | 0 | 0 | 0 | 5 | 3/2 | 42.2 |
| b2_5_sahi_speed | night | 3/5 | 0/1 | 1 | 2 | 0 | 0 | 4/0 | 41.9 |
| b2_5_sahi_speed | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 42.7 |
| b2_5_sahi_speed | night_holdout_2200 | 0/0 | 0/0 | 0 | 0 | 0 | 7 | 0/7 | 42.4 |
| b2_5_sahi_speed | day_holdout_1245 | 0/0 | 0/0 | 0 | 0 | 0 | 5 | 3/2 | 42.2 |

## Detail

### exp0_base - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | DETECTED BUT NOT COUNTED | #1 cyclist 0.6s counted=0 det=cyclist (100.0% cyc) |
| n2 | cyclist | 7:02-7:09 | DETECTED BUT NOT COUNTED | #2 cyclist 0.43s counted=0 det=cyclist (100.0% cyc) |
| n3 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #4 cyclist 0.9s counted=0 det=cyclist (59.3% cyc) |
| n4 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #6 unscored 0.03s counted=0 det=cyclist (100.0% cyc) |
| n5 | cyclist | 14:21-14:26 | MISSED |  |
| n6 | pedestrian | 14:47-14:58 | MISSED |  |

### exp0_base - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #3 pedestrian 3.2s counted=1 det=person (0.0% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #5 cyclist 4.04s counted=1 det=person (34.7% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #8 pedestrian 16.85s counted=1 det=person (0.2% cyc) |
| d4 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #12 pedestrian 2.07s counted=0 det=person (0.0% cyc) |
| d5 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #13 pedestrian 1.2s counted=0 det=person (0.0% cyc) |

### exp1_sahi - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | DETECTED BUT NOT COUNTED | #4 cyclist 1.2s counted=0 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | WRONG CLASS | #22 pedestrian 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### exp1_sahi - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | WRONG CLASS | #2 cyclist 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | WRONG CLASS | #13 cyclist 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b2_0_base - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|

### b2_0_base - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| EXTRA | counted cyclist | 0:40-0:57 | no truth row | #1 9.11s det=person |
| EXTRA | counted cyclist | 8:07-8:14 | no truth row | #4 3.67s det=person |
| EXTRA | counted cyclist | 8:45-8:53 | no truth row | #6 6.97s det=person |
| EXTRA | counted pedestrian | 9:53-10:04 | no truth row | #7 4.84s det=person |
| EXTRA | counted cyclist | 11:16-11:39 | no truth row | #9 18.59s det=person |

### b2_2_sahi - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| EXTRA | counted pedestrian | 6:00-6:13 | no truth row | #18 10.48s det=person |
| EXTRA | counted pedestrian | 7:50-8:27 | no truth row | #24 4.97s det=person |
| EXTRA | counted pedestrian | 8:32-9:00 | no truth row | #26 3.8s det=person |
| EXTRA | counted pedestrian | 9:05-10:15 | no truth row | #27 18.72s det=person |
| EXTRA | counted pedestrian | 10:42-11:18 | no truth row | #33 14.98s det=person |
| EXTRA | counted pedestrian | 11:05-11:16 | no truth row | #36 5.84s det=person |
| EXTRA | counted pedestrian | 11:12-11:18 | no truth row | #40 3.84s det=cyclist |

### b2_2_sahi - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| EXTRA | counted cyclist | 0:40-0:59 | no truth row | #1 15.48s det=person |
| EXTRA | counted cyclist | 8:07-8:16 | no truth row | #7 8.17s det=person |
| EXTRA | counted cyclist | 8:44-8:55 | no truth row | #9 9.68s det=cyclist |
| EXTRA | counted pedestrian | 9:53-10:05 | no truth row | #14 7.21s det=person |
| EXTRA | counted cyclist | 11:14-11:40 | no truth row | #15 23.62s det=person |

### b2_3_sahi_fuse - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | DETECTED BUT NOT COUNTED | #4 cyclist 1.2s counted=0 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | WRONG CLASS | #22 pedestrian 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### b2_3_sahi_fuse - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b2_3_sahi_fuse - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| EXTRA | counted pedestrian | 6:00-6:13 | no truth row | #18 10.48s det=person |
| EXTRA | counted pedestrian | 7:50-8:27 | no truth row | #24 4.97s det=person |
| EXTRA | counted pedestrian | 8:32-9:00 | no truth row | #26 3.8s det=person |
| EXTRA | counted pedestrian | 9:05-10:15 | no truth row | #27 18.72s det=person |
| EXTRA | counted pedestrian | 10:42-11:18 | no truth row | #33 14.98s det=person |
| EXTRA | counted pedestrian | 11:05-11:16 | no truth row | #36 5.84s det=person |
| EXTRA | counted pedestrian | 11:12-11:18 | no truth row | #40 3.84s det=cyclist |

### b2_3_sahi_fuse - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| EXTRA | counted cyclist | 0:40-0:59 | no truth row | #1 15.48s det=person |
| EXTRA | counted cyclist | 8:07-8:16 | no truth row | #7 8.17s det=person |
| EXTRA | counted cyclist | 8:44-8:55 | no truth row | #9 9.68s det=cyclist |
| EXTRA | counted pedestrian | 9:53-10:05 | no truth row | #14 7.21s det=person |
| EXTRA | counted pedestrian | 11:14-11:40 | no truth row | #15 23.62s det=person |

### b2_4_sahi_fuse_nightshort - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | FOUND | #4 cyclist 1.2s counted=1 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | WRONG CLASS | #22 pedestrian 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### b2_4_sahi_fuse_nightshort - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b2_4_sahi_fuse_nightshort - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| EXTRA | counted pedestrian | 6:00-6:13 | no truth row | #18 10.48s det=person |
| EXTRA | counted pedestrian | 7:50-8:27 | no truth row | #24 4.97s det=person |
| EXTRA | counted pedestrian | 8:32-9:00 | no truth row | #26 3.8s det=person |
| EXTRA | counted pedestrian | 9:05-10:15 | no truth row | #27 18.72s det=person |
| EXTRA | counted pedestrian | 10:42-11:18 | no truth row | #33 14.98s det=person |
| EXTRA | counted pedestrian | 11:05-11:16 | no truth row | #36 5.84s det=person |
| EXTRA | counted pedestrian | 11:12-11:18 | no truth row | #40 3.84s det=cyclist |

### b2_4_sahi_fuse_nightshort - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| EXTRA | counted cyclist | 0:40-0:59 | no truth row | #1 15.48s det=person |
| EXTRA | counted cyclist | 8:07-8:16 | no truth row | #7 8.17s det=person |
| EXTRA | counted cyclist | 8:44-8:55 | no truth row | #9 9.68s det=cyclist |
| EXTRA | counted pedestrian | 9:53-10:05 | no truth row | #14 7.21s det=person |
| EXTRA | counted pedestrian | 11:14-11:40 | no truth row | #15 23.62s det=person |

### b2_5_sahi_speed - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | DETECTED BUT NOT COUNTED | #4 cyclist 1.2s counted=0 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | FOUND | #22 cyclist 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### b2_5_sahi_speed - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b2_5_sahi_speed - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| EXTRA | counted pedestrian | 6:00-6:13 | no truth row | #18 10.48s det=person |
| EXTRA | counted pedestrian | 7:50-8:27 | no truth row | #24 4.97s det=person |
| EXTRA | counted pedestrian | 8:32-9:00 | no truth row | #26 3.8s det=person |
| EXTRA | counted pedestrian | 9:05-10:15 | no truth row | #27 18.72s det=person |
| EXTRA | counted pedestrian | 10:42-11:18 | no truth row | #33 14.98s det=person |
| EXTRA | counted pedestrian | 11:05-11:16 | no truth row | #36 5.84s det=person |
| EXTRA | counted pedestrian | 11:12-11:18 | no truth row | #40 3.84s det=cyclist |

### b2_5_sahi_speed - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| EXTRA | counted pedestrian | 0:40-0:59 | no truth row | #1 15.48s det=person |
| EXTRA | counted cyclist | 8:07-8:16 | no truth row | #7 8.17s det=person |
| EXTRA | counted cyclist | 8:44-8:55 | no truth row | #9 9.68s det=cyclist |
| EXTRA | counted pedestrian | 9:53-10:05 | no truth row | #14 7.21s det=person |
| EXTRA | counted cyclist | 11:14-11:40 | no truth row | #15 23.62s det=person |

## Motion-diagnostic candidates (baseline run) overlapping truth rows

**night**: 447 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth n1 (motorcycle 4:02): cand 138 (2.97s, box h 22.5), cand 139 (3.0s, box h 16.9), cand 140 (1.43s, box h 21.2)
- truth n2 (cyclist 7:02): cand 203 (4.54s, box h 22.8), cand 205 (3.0s, box h 41.4), cand 207 (3.5s, box h 26.3), cand 209 (1.1s, box h 20.8), cand 210 (1.2s, box h 41.2), cand 211 (0.9s, box h 36.7), cand 212 (2.67s, box h 52.2), cand 213 (1.7s, box h 31.8), cand 214 (1.3s, box h 50.0), cand 215 (1.5s, box h 16.6), cand 216 (1.43s, box h 23.7), cand 217 (1.4s, box h 90.6), cand 218 (1.94s, box h 86.1), cand 219 (4.9s, box h 49.8), cand 220 (1.74s, box h 94.6)
- truth n3 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n4 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n5 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n6 (pedestrian 14:47): cand 445 (1.3s, box h 15.0), cand 446 (7.61s, box h 31.4), cand 447 (10.78s, box h 91.9)

**day**: 185 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth d2 (pedestrian 3:00): cand 30 (2.57s, box h 19.2), cand 33 (12.18s, box h 71.5), cand 34 (0.87s, box h 84.7), cand 35 (1.13s, box h 19.8), cand 36 (1.13s, box h 40.9), cand 37 (1.07s, box h 34.5), cand 38 (1.97s, box h 61.7), cand 39 (1.17s, box h 43.4)
- truth d1 (cyclist 9:10): cand 108 (1.47s, box h 45.3), cand 109 (1.47s, box h 104.7), cand 110 (1.6s, box h 36.9), cand 111 (1.13s, box h 92.3), cand 112 (3.07s, box h 34.6)
- truth d3 (pedestrian 11:45): cand 142 (8.94s, box h 100.1), cand 144 (0.87s, box h 24.9), cand 145 (3.74s, box h 64.9), cand 146 (1.87s, box h 35.8), cand 147 (3.74s, box h 30.7), cand 148 (1.27s, box h 46.4), cand 149 (1.9s, box h 34.1), cand 150 (1.17s, box h 26.5), cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1)
- truth d4 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)
- truth d5 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)


<a id="report-eval-20261009-0202"></a>
## EVAL_20261009_0202.md
Original location: `vision3/best/test_colonial/exp_results/EVAL_20261009_0202.md`.

# Experiment evaluation  (2026-10-09 02:02)

root: /orange/xiangyan/rithika/vision/vision3/best/test_colonial
runs: exp0_base, exp1_sahi, b2_0_base, b2_2_sahi, b2_3_sahi_fuse, b2_4_sahi_fuse_nightshort, b2_5_sahi_speed

- truth night: 6 usable rows (5 cyclist incl. motorcycle, 1 pedestrian); skipped 0: none
- truth day: 5 usable rows (1 cyclist incl. motorcycle, 4 pedestrian); skipped 0: none
- truth night_holdout_2200: 0 usable rows (0 cyclist incl. motorcycle, 0 pedestrian); skipped 2: t1 (start='10:04', class=''); t2 (start='10:12', class='')
- truth day_holdout_1245: 5 usable rows (2 cyclist incl. motorcycle, 3 pedestrian); skipped 0: none

## Summary (person level; FOUND = counted with the right class; motorcycle scored as cyclist)

| run | clip | cyclists found | pedestrians found | wrong class | detected, not counted | missed | extra counted | counted bic/ped | runtime min |
|---|---|---|---|---|---|---|---|---|---|
| exp0_base | night | 0/5 | 0/1 | 0 | 4 | 2 | 0 | 0/0 | 30.1 |
| exp0_base | day | 1/1 | 2/4 | 0 | 2 | 0 | 0 | 1/2 | 30.6 |
| exp1_sahi | night | 2/5 | 0/1 | 2 | 2 | 0 | 0 | 3/1 | 42.2 |
| exp1_sahi | day | 1/1 | 2/4 | 2 | 0 | 0 | 0 | 3/2 | 43.1 |
| b2_0_base | night_holdout_2200 | 0/0 | 0/0 | 0 | 0 | 0 | 0 | 0/0 | 28.8 |
| b2_0_base | day_holdout_1245 | 2/2 | 1/3 | 2 | 0 | 0 | 0 | 4/1 | 28.7 |
| b2_2_sahi | night_holdout_2200 | 0/0 | 0/0 | 0 | 0 | 0 | 7 | 0/7 | 43.1 |
| b2_2_sahi | day_holdout_1245 | 2/2 | 1/3 | 2 | 0 | 0 | 0 | 4/1 | 42.3 |
| b2_3_sahi_fuse | night | 2/5 | 0/1 | 2 | 2 | 0 | 0 | 3/1 | 42.0 |
| b2_3_sahi_fuse | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 41.4 |
| b2_3_sahi_fuse | night_holdout_2200 | 0/0 | 0/0 | 0 | 0 | 0 | 7 | 0/7 | 42.5 |
| b2_3_sahi_fuse | day_holdout_1245 | 2/2 | 2/3 | 1 | 0 | 0 | 0 | 3/2 | 41.7 |
| b2_4_sahi_fuse_nightshort | night | 3/5 | 0/1 | 2 | 1 | 0 | 0 | 4/1 | 41.6 |
| b2_4_sahi_fuse_nightshort | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 42.1 |
| b2_4_sahi_fuse_nightshort | night_holdout_2200 | 0/0 | 0/0 | 0 | 0 | 0 | 7 | 0/7 | 41.9 |
| b2_4_sahi_fuse_nightshort | day_holdout_1245 | 2/2 | 2/3 | 1 | 0 | 0 | 0 | 3/2 | 42.2 |
| b2_5_sahi_speed | night | 3/5 | 0/1 | 1 | 2 | 0 | 0 | 4/0 | 41.9 |
| b2_5_sahi_speed | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 42.7 |
| b2_5_sahi_speed | night_holdout_2200 | 0/0 | 0/0 | 0 | 0 | 0 | 7 | 0/7 | 42.4 |
| b2_5_sahi_speed | day_holdout_1245 | 2/2 | 2/3 | 1 | 0 | 0 | 0 | 3/2 | 42.2 |

## Detail

### exp0_base - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | DETECTED BUT NOT COUNTED | #1 cyclist 0.6s counted=0 det=cyclist (100.0% cyc) |
| n2 | cyclist | 7:02-7:09 | DETECTED BUT NOT COUNTED | #2 cyclist 0.43s counted=0 det=cyclist (100.0% cyc) |
| n3 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #4 cyclist 0.9s counted=0 det=cyclist (59.3% cyc) |
| n4 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #6 unscored 0.03s counted=0 det=cyclist (100.0% cyc) |
| n5 | cyclist | 14:21-14:26 | MISSED |  |
| n6 | pedestrian | 14:47-14:58 | MISSED |  |

### exp0_base - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #3 pedestrian 3.2s counted=1 det=person (0.0% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #5 cyclist 4.04s counted=1 det=person (34.7% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #8 pedestrian 16.85s counted=1 det=person (0.2% cyc) |
| d4 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #12 pedestrian 2.07s counted=0 det=person (0.0% cyc) |
| d5 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #13 pedestrian 1.2s counted=0 det=person (0.0% cyc) |

### exp1_sahi - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | DETECTED BUT NOT COUNTED | #4 cyclist 1.2s counted=0 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | WRONG CLASS | #22 pedestrian 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### exp1_sahi - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | WRONG CLASS | #2 cyclist 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | WRONG CLASS | #13 cyclist 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b2_0_base - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|

### b2_0_base - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | WRONG CLASS | #1 cyclist 9.11s counted=1 det=person (44.7% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #4 cyclist 3.67s counted=1 det=person (46.4% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #6 cyclist 6.97s counted=1 det=person (45.0% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #7 pedestrian 4.84s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | WRONG CLASS | #9 cyclist 18.59s counted=1 det=person (6.6% cyc) |

### b2_2_sahi - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| EXTRA | counted pedestrian | 6:00-6:13 | no truth row | #18 10.48s det=person |
| EXTRA | counted pedestrian | 7:50-8:27 | no truth row | #24 4.97s det=person |
| EXTRA | counted pedestrian | 8:32-9:00 | no truth row | #26 3.8s det=person |
| EXTRA | counted pedestrian | 9:05-10:15 | no truth row | #27 18.72s det=person |
| EXTRA | counted pedestrian | 10:42-11:18 | no truth row | #33 14.98s det=person |
| EXTRA | counted pedestrian | 11:05-11:16 | no truth row | #36 5.84s det=person |
| EXTRA | counted pedestrian | 11:12-11:18 | no truth row | #40 3.84s det=cyclist |

### b2_2_sahi - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | WRONG CLASS | #1 cyclist 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | WRONG CLASS | #15 cyclist 23.62s counted=1 det=person (8.1% cyc) |

### b2_3_sahi_fuse - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | DETECTED BUT NOT COUNTED | #4 cyclist 1.2s counted=0 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | WRONG CLASS | #22 pedestrian 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### b2_3_sahi_fuse - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b2_3_sahi_fuse - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| EXTRA | counted pedestrian | 6:00-6:13 | no truth row | #18 10.48s det=person |
| EXTRA | counted pedestrian | 7:50-8:27 | no truth row | #24 4.97s det=person |
| EXTRA | counted pedestrian | 8:32-9:00 | no truth row | #26 3.8s det=person |
| EXTRA | counted pedestrian | 9:05-10:15 | no truth row | #27 18.72s det=person |
| EXTRA | counted pedestrian | 10:42-11:18 | no truth row | #33 14.98s det=person |
| EXTRA | counted pedestrian | 11:05-11:16 | no truth row | #36 5.84s det=person |
| EXTRA | counted pedestrian | 11:12-11:18 | no truth row | #40 3.84s det=cyclist |

### b2_3_sahi_fuse - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | WRONG CLASS | #1 cyclist 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | FOUND | #15 pedestrian 23.62s counted=1 det=person (8.1% cyc) |

### b2_4_sahi_fuse_nightshort - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | FOUND | #4 cyclist 1.2s counted=1 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | WRONG CLASS | #22 pedestrian 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### b2_4_sahi_fuse_nightshort - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b2_4_sahi_fuse_nightshort - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| EXTRA | counted pedestrian | 6:00-6:13 | no truth row | #18 10.48s det=person |
| EXTRA | counted pedestrian | 7:50-8:27 | no truth row | #24 4.97s det=person |
| EXTRA | counted pedestrian | 8:32-9:00 | no truth row | #26 3.8s det=person |
| EXTRA | counted pedestrian | 9:05-10:15 | no truth row | #27 18.72s det=person |
| EXTRA | counted pedestrian | 10:42-11:18 | no truth row | #33 14.98s det=person |
| EXTRA | counted pedestrian | 11:05-11:16 | no truth row | #36 5.84s det=person |
| EXTRA | counted pedestrian | 11:12-11:18 | no truth row | #40 3.84s det=cyclist |

### b2_4_sahi_fuse_nightshort - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | WRONG CLASS | #1 cyclist 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | FOUND | #15 pedestrian 23.62s counted=1 det=person (8.1% cyc) |

### b2_5_sahi_speed - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | DETECTED BUT NOT COUNTED | #4 cyclist 1.2s counted=0 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | FOUND | #22 cyclist 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### b2_5_sahi_speed - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b2_5_sahi_speed - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| EXTRA | counted pedestrian | 6:00-6:13 | no truth row | #18 10.48s det=person |
| EXTRA | counted pedestrian | 7:50-8:27 | no truth row | #24 4.97s det=person |
| EXTRA | counted pedestrian | 8:32-9:00 | no truth row | #26 3.8s det=person |
| EXTRA | counted pedestrian | 9:05-10:15 | no truth row | #27 18.72s det=person |
| EXTRA | counted pedestrian | 10:42-11:18 | no truth row | #33 14.98s det=person |
| EXTRA | counted pedestrian | 11:05-11:16 | no truth row | #36 5.84s det=person |
| EXTRA | counted pedestrian | 11:12-11:18 | no truth row | #40 3.84s det=cyclist |

### b2_5_sahi_speed - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | FOUND | #1 pedestrian 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | WRONG CLASS | #15 cyclist 23.62s counted=1 det=person (8.1% cyc) |

## Motion-diagnostic candidates (baseline run) overlapping truth rows

**night**: 447 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth n1 (motorcycle 4:02): cand 138 (2.97s, box h 22.5), cand 139 (3.0s, box h 16.9), cand 140 (1.43s, box h 21.2)
- truth n2 (cyclist 7:02): cand 203 (4.54s, box h 22.8), cand 205 (3.0s, box h 41.4), cand 207 (3.5s, box h 26.3), cand 209 (1.1s, box h 20.8), cand 210 (1.2s, box h 41.2), cand 211 (0.9s, box h 36.7), cand 212 (2.67s, box h 52.2), cand 213 (1.7s, box h 31.8), cand 214 (1.3s, box h 50.0), cand 215 (1.5s, box h 16.6), cand 216 (1.43s, box h 23.7), cand 217 (1.4s, box h 90.6), cand 218 (1.94s, box h 86.1), cand 219 (4.9s, box h 49.8), cand 220 (1.74s, box h 94.6)
- truth n3 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n4 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n5 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n6 (pedestrian 14:47): cand 445 (1.3s, box h 15.0), cand 446 (7.61s, box h 31.4), cand 447 (10.78s, box h 91.9)

**day**: 185 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth d2 (pedestrian 3:00): cand 30 (2.57s, box h 19.2), cand 33 (12.18s, box h 71.5), cand 34 (0.87s, box h 84.7), cand 35 (1.13s, box h 19.8), cand 36 (1.13s, box h 40.9), cand 37 (1.07s, box h 34.5), cand 38 (1.97s, box h 61.7), cand 39 (1.17s, box h 43.4)
- truth d1 (cyclist 9:10): cand 108 (1.47s, box h 45.3), cand 109 (1.47s, box h 104.7), cand 110 (1.6s, box h 36.9), cand 111 (1.13s, box h 92.3), cand 112 (3.07s, box h 34.6)
- truth d3 (pedestrian 11:45): cand 142 (8.94s, box h 100.1), cand 144 (0.87s, box h 24.9), cand 145 (3.74s, box h 64.9), cand 146 (1.87s, box h 35.8), cand 147 (3.74s, box h 30.7), cand 148 (1.27s, box h 46.4), cand 149 (1.9s, box h 34.1), cand 150 (1.17s, box h 26.5), cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1)
- truth d4 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)
- truth d5 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)


<a id="report-eval-20261010-2251"></a>
## EVAL_20261010_2251.md
Original location: `vision3/best/test_colonial/exp_results/EVAL_20261010_2251.md`.

# Experiment evaluation  (2026-10-10 22:51)

root: /orange/xiangyan/rithika/vision/vision3/best/test_colonial
runs: exp0_base, exp1_sahi, b2_0_base, b2_2_sahi, b2_3_sahi_fuse, b2_4_sahi_fuse_nightshort, b2_5_sahi_speed

- truth night: 6 usable rows (5 cyclist incl. motorcycle, 1 pedestrian); skipped 0: none
- truth day: 5 usable rows (1 cyclist incl. motorcycle, 4 pedestrian); skipped 0: none
- truth night_holdout_2200: 5 usable rows (0 cyclist incl. motorcycle, 5 pedestrian); skipped 0: none
- truth day_holdout_1245: 5 usable rows (2 cyclist incl. motorcycle, 3 pedestrian); skipped 0: none

## Summary (person level; FOUND = counted with the right class; motorcycle scored as cyclist)

| run | clip | cyclists found | pedestrians found | wrong class | detected, not counted | missed | extra counted | counted bic/ped | runtime min |
|---|---|---|---|---|---|---|---|---|---|
| exp0_base | night | 0/5 | 0/1 | 0 | 4 | 2 | 0 | 0/0 | 30.1 |
| exp0_base | day | 1/1 | 2/4 | 0 | 2 | 0 | 0 | 1/2 | 30.6 |
| exp1_sahi | night | 2/5 | 0/1 | 2 | 2 | 0 | 0 | 3/1 | 42.2 |
| exp1_sahi | day | 1/1 | 2/4 | 2 | 0 | 0 | 0 | 3/2 | 43.1 |
| b2_0_base | night_holdout_2200 | 0/0 | 0/5 | 0 | 2 | 3 | 0 | 0/0 | 28.8 |
| b2_0_base | day_holdout_1245 | 2/2 | 1/3 | 2 | 0 | 0 | 0 | 4/1 | 28.7 |
| b2_2_sahi | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 2 | 0/7 | 43.1 |
| b2_2_sahi | day_holdout_1245 | 2/2 | 1/3 | 2 | 0 | 0 | 0 | 4/1 | 42.3 |
| b2_3_sahi_fuse | night | 2/5 | 0/1 | 2 | 2 | 0 | 0 | 3/1 | 42.0 |
| b2_3_sahi_fuse | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 41.4 |
| b2_3_sahi_fuse | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 2 | 0/7 | 42.5 |
| b2_3_sahi_fuse | day_holdout_1245 | 2/2 | 2/3 | 1 | 0 | 0 | 0 | 3/2 | 41.7 |
| b2_4_sahi_fuse_nightshort | night | 3/5 | 0/1 | 2 | 1 | 0 | 0 | 4/1 | 41.6 |
| b2_4_sahi_fuse_nightshort | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 42.1 |
| b2_4_sahi_fuse_nightshort | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 2 | 0/7 | 41.9 |
| b2_4_sahi_fuse_nightshort | day_holdout_1245 | 2/2 | 2/3 | 1 | 0 | 0 | 0 | 3/2 | 42.2 |
| b2_5_sahi_speed | night | 3/5 | 0/1 | 1 | 2 | 0 | 0 | 4/0 | 41.9 |
| b2_5_sahi_speed | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 42.7 |
| b2_5_sahi_speed | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 2 | 0/7 | 42.4 |
| b2_5_sahi_speed | day_holdout_1245 | 2/2 | 2/3 | 1 | 0 | 0 | 0 | 3/2 | 42.2 |

## Detail

### exp0_base - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | DETECTED BUT NOT COUNTED | #1 cyclist 0.6s counted=0 det=cyclist (100.0% cyc) |
| n2 | cyclist | 7:02-7:09 | DETECTED BUT NOT COUNTED | #2 cyclist 0.43s counted=0 det=cyclist (100.0% cyc) |
| n3 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #4 cyclist 0.9s counted=0 det=cyclist (59.3% cyc) |
| n4 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #6 unscored 0.03s counted=0 det=cyclist (100.0% cyc) |
| n5 | cyclist | 14:21-14:26 | MISSED |  |
| n6 | pedestrian | 14:47-14:58 | MISSED |  |

### exp0_base - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #3 pedestrian 3.2s counted=1 det=person (0.0% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #5 cyclist 4.04s counted=1 det=person (34.7% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #8 pedestrian 16.85s counted=1 det=person (0.2% cyc) |
| d4 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #12 pedestrian 2.07s counted=0 det=person (0.0% cyc) |
| d5 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #13 pedestrian 1.2s counted=0 det=person (0.0% cyc) |

### exp1_sahi - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | DETECTED BUT NOT COUNTED | #4 cyclist 1.2s counted=0 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | WRONG CLASS | #22 pedestrian 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### exp1_sahi - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | WRONG CLASS | #2 cyclist 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | WRONG CLASS | #13 cyclist 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b2_0_base - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | MISSED |  |
| p2 | pedestrian | 10:00-10:14 | DETECTED BUT NOT COUNTED | #3 pedestrian 0.43s counted=0 det=cyclist (100.0% cyc) |
| p3 | pedestrian | 10:59-11:18 | DETECTED BUT NOT COUNTED | #6 unscored 0.17s counted=0 det=cyclist (100.0% cyc) |
| p4 | pedestrian | 10:59-11:18 | MISSED |  |
| p5 | pedestrian | 10:59-11:18 | MISSED |  |

### b2_0_base - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | WRONG CLASS | #1 cyclist 9.11s counted=1 det=person (44.7% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #4 cyclist 3.67s counted=1 det=person (46.4% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #6 cyclist 6.97s counted=1 det=person (45.0% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #7 pedestrian 4.84s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | WRONG CLASS | #9 cyclist 18.59s counted=1 det=person (6.6% cyc) |

### b2_2_sahi - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | FOUND | #18 pedestrian 10.48s counted=1 det=person (24.5% cyc) |
| p2 | pedestrian | 10:00-10:14 | FOUND | #27 pedestrian 18.72s counted=1 det=person (31.6% cyc) |
| p3 | pedestrian | 10:59-11:18 | FOUND | #33 pedestrian 14.98s counted=1 det=person (43.4% cyc) |
| p4 | pedestrian | 10:59-11:18 | FOUND | #36 pedestrian 5.84s counted=1 det=person (28.0% cyc) |
| p5 | pedestrian | 10:59-11:18 | FOUND | #40 pedestrian 3.84s counted=1 det=cyclist (76.5% cyc) |
| EXTRA | counted pedestrian | 7:50-8:27 | no truth row | #24 4.97s det=person |
| EXTRA | counted pedestrian | 8:32-9:00 | no truth row | #26 3.8s det=person |

### b2_2_sahi - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | WRONG CLASS | #1 cyclist 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | WRONG CLASS | #15 cyclist 23.62s counted=1 det=person (8.1% cyc) |

### b2_3_sahi_fuse - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | DETECTED BUT NOT COUNTED | #4 cyclist 1.2s counted=0 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | WRONG CLASS | #22 pedestrian 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### b2_3_sahi_fuse - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b2_3_sahi_fuse - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | FOUND | #18 pedestrian 10.48s counted=1 det=person (24.5% cyc) |
| p2 | pedestrian | 10:00-10:14 | FOUND | #27 pedestrian 18.72s counted=1 det=person (31.6% cyc) |
| p3 | pedestrian | 10:59-11:18 | FOUND | #33 pedestrian 14.98s counted=1 det=person (43.4% cyc) |
| p4 | pedestrian | 10:59-11:18 | FOUND | #36 pedestrian 5.84s counted=1 det=person (28.0% cyc) |
| p5 | pedestrian | 10:59-11:18 | FOUND | #40 pedestrian 3.84s counted=1 det=cyclist (76.5% cyc) |
| EXTRA | counted pedestrian | 7:50-8:27 | no truth row | #24 4.97s det=person |
| EXTRA | counted pedestrian | 8:32-9:00 | no truth row | #26 3.8s det=person |

### b2_3_sahi_fuse - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | WRONG CLASS | #1 cyclist 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | FOUND | #15 pedestrian 23.62s counted=1 det=person (8.1% cyc) |

### b2_4_sahi_fuse_nightshort - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | FOUND | #4 cyclist 1.2s counted=1 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | WRONG CLASS | #22 pedestrian 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### b2_4_sahi_fuse_nightshort - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b2_4_sahi_fuse_nightshort - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | FOUND | #18 pedestrian 10.48s counted=1 det=person (24.5% cyc) |
| p2 | pedestrian | 10:00-10:14 | FOUND | #27 pedestrian 18.72s counted=1 det=person (31.6% cyc) |
| p3 | pedestrian | 10:59-11:18 | FOUND | #33 pedestrian 14.98s counted=1 det=person (43.4% cyc) |
| p4 | pedestrian | 10:59-11:18 | FOUND | #36 pedestrian 5.84s counted=1 det=person (28.0% cyc) |
| p5 | pedestrian | 10:59-11:18 | FOUND | #40 pedestrian 3.84s counted=1 det=cyclist (76.5% cyc) |
| EXTRA | counted pedestrian | 7:50-8:27 | no truth row | #24 4.97s det=person |
| EXTRA | counted pedestrian | 8:32-9:00 | no truth row | #26 3.8s det=person |

### b2_4_sahi_fuse_nightshort - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | WRONG CLASS | #1 cyclist 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | FOUND | #15 pedestrian 23.62s counted=1 det=person (8.1% cyc) |

### b2_5_sahi_speed - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | DETECTED BUT NOT COUNTED | #4 cyclist 1.2s counted=0 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | FOUND | #22 cyclist 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### b2_5_sahi_speed - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b2_5_sahi_speed - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | FOUND | #18 pedestrian 10.48s counted=1 det=person (24.5% cyc) |
| p2 | pedestrian | 10:00-10:14 | FOUND | #27 pedestrian 18.72s counted=1 det=person (31.6% cyc) |
| p3 | pedestrian | 10:59-11:18 | FOUND | #33 pedestrian 14.98s counted=1 det=person (43.4% cyc) |
| p4 | pedestrian | 10:59-11:18 | FOUND | #36 pedestrian 5.84s counted=1 det=person (28.0% cyc) |
| p5 | pedestrian | 10:59-11:18 | FOUND | #40 pedestrian 3.84s counted=1 det=cyclist (76.5% cyc) |
| EXTRA | counted pedestrian | 7:50-8:27 | no truth row | #24 4.97s det=person |
| EXTRA | counted pedestrian | 8:32-9:00 | no truth row | #26 3.8s det=person |

### b2_5_sahi_speed - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | FOUND | #1 pedestrian 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | WRONG CLASS | #15 cyclist 23.62s counted=1 det=person (8.1% cyc) |

## Motion-diagnostic candidates (baseline run) overlapping truth rows

**night**: 447 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth n1 (motorcycle 4:02): cand 138 (2.97s, box h 22.5), cand 139 (3.0s, box h 16.9), cand 140 (1.43s, box h 21.2)
- truth n2 (cyclist 7:02): cand 203 (4.54s, box h 22.8), cand 205 (3.0s, box h 41.4), cand 207 (3.5s, box h 26.3), cand 209 (1.1s, box h 20.8), cand 210 (1.2s, box h 41.2), cand 211 (0.9s, box h 36.7), cand 212 (2.67s, box h 52.2), cand 213 (1.7s, box h 31.8), cand 214 (1.3s, box h 50.0), cand 215 (1.5s, box h 16.6), cand 216 (1.43s, box h 23.7), cand 217 (1.4s, box h 90.6), cand 218 (1.94s, box h 86.1), cand 219 (4.9s, box h 49.8), cand 220 (1.74s, box h 94.6)
- truth n3 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n4 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n5 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n6 (pedestrian 14:47): cand 445 (1.3s, box h 15.0), cand 446 (7.61s, box h 31.4), cand 447 (10.78s, box h 91.9)

**day**: 185 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth d2 (pedestrian 3:00): cand 30 (2.57s, box h 19.2), cand 33 (12.18s, box h 71.5), cand 34 (0.87s, box h 84.7), cand 35 (1.13s, box h 19.8), cand 36 (1.13s, box h 40.9), cand 37 (1.07s, box h 34.5), cand 38 (1.97s, box h 61.7), cand 39 (1.17s, box h 43.4)
- truth d1 (cyclist 9:10): cand 108 (1.47s, box h 45.3), cand 109 (1.47s, box h 104.7), cand 110 (1.6s, box h 36.9), cand 111 (1.13s, box h 92.3), cand 112 (3.07s, box h 34.6)
- truth d3 (pedestrian 11:45): cand 142 (8.94s, box h 100.1), cand 144 (0.87s, box h 24.9), cand 145 (3.74s, box h 64.9), cand 146 (1.87s, box h 35.8), cand 147 (3.74s, box h 30.7), cand 148 (1.27s, box h 46.4), cand 149 (1.9s, box h 34.1), cand 150 (1.17s, box h 26.5), cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1)
- truth d4 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)
- truth d5 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)


<a id="report-eval-20261012-0003"></a>
## EVAL_20261012_0003.md
Original location: `vision3/best/test_colonial/exp_results/EVAL_20261012_0003.md`.

# Experiment evaluation  (2026-10-12 00:03)

root: /orange/xiangyan/rithika/vision/vision3/best/test_colonial
runs: exp0_base, b2_2_sahi, b3_combo, b4_combo_static5

- truth night: 6 usable rows (5 cyclist incl. motorcycle, 1 pedestrian); skipped 0: none
- truth day: 5 usable rows (1 cyclist incl. motorcycle, 4 pedestrian); skipped 0: none
- truth night_holdout_2200: 5 usable rows (0 cyclist incl. motorcycle, 5 pedestrian); skipped 0: none
- truth day_holdout_1245: 5 usable rows (2 cyclist incl. motorcycle, 3 pedestrian); skipped 0: none

## Summary (person level; FOUND = counted with the right class; motorcycle scored as cyclist)

| run | clip | cyclists found | pedestrians found | wrong class | detected, not counted | missed | extra counted | counted bic/ped | runtime min |
|---|---|---|---|---|---|---|---|---|---|
| exp0_base | night | 0/5 | 0/1 | 0 | 4 | 2 | 0 | 0/0 | 30.1 |
| exp0_base | day | 1/1 | 2/4 | 0 | 2 | 0 | 0 | 1/2 | 30.6 |
| b2_2_sahi | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 2 | 0/7 | 43.1 |
| b2_2_sahi | day_holdout_1245 | 2/2 | 1/3 | 2 | 0 | 0 | 0 | 4/1 | 42.3 |
| b3_combo | night | 4/5 | 0/1 | 1 | 1 | 0 | 0 | 5/0 | 42.1 |
| b3_combo | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 41.9 |
| b3_combo | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 2 | 0/7 | 42.1 |
| b3_combo | day_holdout_1245 | 2/2 | 3/3 | 0 | 0 | 0 | 0 | 2/3 | 41.3 |
| b4_combo_static5 | night | 4/5 | 0/1 | 1 | 1 | 0 | 0 | 5/0 | 42.9 |
| b4_combo_static5 | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 42.0 |
| b4_combo_static5 | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 0 | 0/5 | 41.8 |
| b4_combo_static5 | day_holdout_1245 | 2/2 | 3/3 | 0 | 0 | 0 | 0 | 2/3 | 41.3 |

## Detail

### exp0_base - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | DETECTED BUT NOT COUNTED | #1 cyclist 0.6s counted=0 det=cyclist (100.0% cyc) |
| n2 | cyclist | 7:02-7:09 | DETECTED BUT NOT COUNTED | #2 cyclist 0.43s counted=0 det=cyclist (100.0% cyc) |
| n3 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #4 cyclist 0.9s counted=0 det=cyclist (59.3% cyc) |
| n4 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #6 unscored 0.03s counted=0 det=cyclist (100.0% cyc) |
| n5 | cyclist | 14:21-14:26 | MISSED |  |
| n6 | pedestrian | 14:47-14:58 | MISSED |  |

### exp0_base - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #3 pedestrian 3.2s counted=1 det=person (0.0% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #5 cyclist 4.04s counted=1 det=person (34.7% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #8 pedestrian 16.85s counted=1 det=person (0.2% cyc) |
| d4 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #12 pedestrian 2.07s counted=0 det=person (0.0% cyc) |
| d5 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #13 pedestrian 1.2s counted=0 det=person (0.0% cyc) |

### b2_2_sahi - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | FOUND | #18 pedestrian 10.48s counted=1 det=person (24.5% cyc) |
| p2 | pedestrian | 10:00-10:14 | FOUND | #27 pedestrian 18.72s counted=1 det=person (31.6% cyc) |
| p3 | pedestrian | 10:59-11:18 | FOUND | #33 pedestrian 14.98s counted=1 det=person (43.4% cyc) |
| p4 | pedestrian | 10:59-11:18 | FOUND | #36 pedestrian 5.84s counted=1 det=person (28.0% cyc) |
| p5 | pedestrian | 10:59-11:18 | FOUND | #40 pedestrian 3.84s counted=1 det=cyclist (76.5% cyc) |
| EXTRA | counted pedestrian | 7:50-8:27 | no truth row | #24 4.97s det=person |
| EXTRA | counted pedestrian | 8:32-9:00 | no truth row | #26 3.8s det=person |

### b2_2_sahi - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | WRONG CLASS | #1 cyclist 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | WRONG CLASS | #15 cyclist 23.62s counted=1 det=person (8.1% cyc) |

### b3_combo - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | FOUND | #4 cyclist 1.2s counted=1 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | FOUND | #22 cyclist 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### b3_combo - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b3_combo - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | FOUND | #18 pedestrian 10.48s counted=1 det=person (24.5% cyc) |
| p2 | pedestrian | 10:00-10:14 | FOUND | #27 pedestrian 18.72s counted=1 det=person (31.6% cyc) |
| p3 | pedestrian | 10:59-11:18 | FOUND | #33 pedestrian 14.98s counted=1 det=person (43.4% cyc) |
| p4 | pedestrian | 10:59-11:18 | FOUND | #36 pedestrian 5.84s counted=1 det=person (28.0% cyc) |
| p5 | pedestrian | 10:59-11:18 | FOUND | #40 pedestrian 3.84s counted=1 det=cyclist (76.5% cyc) |
| EXTRA | counted pedestrian | 7:50-8:27 | no truth row | #24 4.97s det=person |
| EXTRA | counted pedestrian | 8:32-9:00 | no truth row | #26 3.8s det=person |

### b3_combo - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | FOUND | #1 pedestrian 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | FOUND | #15 pedestrian 23.62s counted=1 det=person (8.1% cyc) |

### b4_combo_static5 - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | FOUND | #4 cyclist 1.2s counted=1 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | FOUND | #22 cyclist 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### b4_combo_static5 - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b4_combo_static5 - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | FOUND | #18 pedestrian 10.48s counted=1 det=person (24.5% cyc) |
| p2 | pedestrian | 10:00-10:14 | FOUND | #27 pedestrian 18.72s counted=1 det=person (31.6% cyc) |
| p3 | pedestrian | 10:59-11:18 | FOUND | #33 pedestrian 14.98s counted=1 det=person (43.4% cyc) |
| p4 | pedestrian | 10:59-11:18 | FOUND | #36 pedestrian 5.84s counted=1 det=person (28.0% cyc) |
| p5 | pedestrian | 10:59-11:18 | FOUND | #40 pedestrian 3.84s counted=1 det=cyclist (76.5% cyc) |

### b4_combo_static5 - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | FOUND | #1 pedestrian 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | FOUND | #15 pedestrian 23.62s counted=1 det=person (8.1% cyc) |

## Motion-diagnostic candidates (baseline run) overlapping truth rows

**night**: 447 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth n1 (motorcycle 4:02): cand 138 (2.97s, box h 22.5), cand 139 (3.0s, box h 16.9), cand 140 (1.43s, box h 21.2)
- truth n2 (cyclist 7:02): cand 203 (4.54s, box h 22.8), cand 205 (3.0s, box h 41.4), cand 207 (3.5s, box h 26.3), cand 209 (1.1s, box h 20.8), cand 210 (1.2s, box h 41.2), cand 211 (0.9s, box h 36.7), cand 212 (2.67s, box h 52.2), cand 213 (1.7s, box h 31.8), cand 214 (1.3s, box h 50.0), cand 215 (1.5s, box h 16.6), cand 216 (1.43s, box h 23.7), cand 217 (1.4s, box h 90.6), cand 218 (1.94s, box h 86.1), cand 219 (4.9s, box h 49.8), cand 220 (1.74s, box h 94.6)
- truth n3 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n4 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n5 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n6 (pedestrian 14:47): cand 445 (1.3s, box h 15.0), cand 446 (7.61s, box h 31.4), cand 447 (10.78s, box h 91.9)

**day**: 185 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth d2 (pedestrian 3:00): cand 30 (2.57s, box h 19.2), cand 33 (12.18s, box h 71.5), cand 34 (0.87s, box h 84.7), cand 35 (1.13s, box h 19.8), cand 36 (1.13s, box h 40.9), cand 37 (1.07s, box h 34.5), cand 38 (1.97s, box h 61.7), cand 39 (1.17s, box h 43.4)
- truth d1 (cyclist 9:10): cand 108 (1.47s, box h 45.3), cand 109 (1.47s, box h 104.7), cand 110 (1.6s, box h 36.9), cand 111 (1.13s, box h 92.3), cand 112 (3.07s, box h 34.6)
- truth d3 (pedestrian 11:45): cand 142 (8.94s, box h 100.1), cand 144 (0.87s, box h 24.9), cand 145 (3.74s, box h 64.9), cand 146 (1.87s, box h 35.8), cand 147 (3.74s, box h 30.7), cand 148 (1.27s, box h 46.4), cand 149 (1.9s, box h 34.1), cand 150 (1.17s, box h 26.5), cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1)
- truth d4 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)
- truth d5 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)


<a id="report-eval-20261015-2225"></a>
## EVAL_20261015_2225.md
Original location: `vision3/best/test_colonial/exp_results/EVAL_20261015_2225.md`.

# Experiment evaluation  (2026-10-15 22:25)

root: /orange/xiangyan/rithika/vision/vision3/best/test_colonial
runs: exp0_base, b4_combo_static5, b4_new_0815, b4_new_0930, b4_new_2320

- truth night: 6 usable rows (5 cyclist incl. motorcycle, 1 pedestrian); skipped 0: none
- truth day: 5 usable rows (1 cyclist incl. motorcycle, 4 pedestrian); skipped 0: none
- truth night_holdout_2200: 5 usable rows (0 cyclist incl. motorcycle, 5 pedestrian); skipped 0: none
- truth day_holdout_1245: 5 usable rows (2 cyclist incl. motorcycle, 3 pedestrian); skipped 0: none

## Summary (person level; FOUND = counted with the right class; motorcycle scored as cyclist)

| run | clip | cyclists found | pedestrians found | wrong class | detected, not counted | missed | extra counted | counted bic/ped | runtime min |
|---|---|---|---|---|---|---|---|---|---|
| exp0_base | night | 0/5 | 0/1 | 0 | 4 | 2 | 0 | 0/0 | 30.1 |
| exp0_base | day | 1/1 | 2/4 | 0 | 2 | 0 | 0 | 1/2 | 30.6 |
| b4_combo_static5 | night | 4/5 | 0/1 | 1 | 1 | 0 | 0 | 5/0 | 42.9 |
| b4_combo_static5 | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 42.0 |
| b4_combo_static5 | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 0 | 0/5 | 41.8 |
| b4_combo_static5 | day_holdout_1245 | 2/2 | 3/3 | 0 | 0 | 0 | 0 | 2/3 | 41.3 |

## Detail

### exp0_base - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | DETECTED BUT NOT COUNTED | #1 cyclist 0.6s counted=0 det=cyclist (100.0% cyc) |
| n2 | cyclist | 7:02-7:09 | DETECTED BUT NOT COUNTED | #2 cyclist 0.43s counted=0 det=cyclist (100.0% cyc) |
| n3 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #4 cyclist 0.9s counted=0 det=cyclist (59.3% cyc) |
| n4 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #6 unscored 0.03s counted=0 det=cyclist (100.0% cyc) |
| n5 | cyclist | 14:21-14:26 | MISSED |  |
| n6 | pedestrian | 14:47-14:58 | MISSED |  |

### exp0_base - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #3 pedestrian 3.2s counted=1 det=person (0.0% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #5 cyclist 4.04s counted=1 det=person (34.7% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #8 pedestrian 16.85s counted=1 det=person (0.2% cyc) |
| d4 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #12 pedestrian 2.07s counted=0 det=person (0.0% cyc) |
| d5 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #13 pedestrian 1.2s counted=0 det=person (0.0% cyc) |

### b4_combo_static5 - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | FOUND | #4 cyclist 1.2s counted=1 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | FOUND | #22 cyclist 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### b4_combo_static5 - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b4_combo_static5 - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | FOUND | #18 pedestrian 10.48s counted=1 det=person (24.5% cyc) |
| p2 | pedestrian | 10:00-10:14 | FOUND | #27 pedestrian 18.72s counted=1 det=person (31.6% cyc) |
| p3 | pedestrian | 10:59-11:18 | FOUND | #33 pedestrian 14.98s counted=1 det=person (43.4% cyc) |
| p4 | pedestrian | 10:59-11:18 | FOUND | #36 pedestrian 5.84s counted=1 det=person (28.0% cyc) |
| p5 | pedestrian | 10:59-11:18 | FOUND | #40 pedestrian 3.84s counted=1 det=cyclist (76.5% cyc) |

### b4_combo_static5 - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | FOUND | #1 pedestrian 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | FOUND | #15 pedestrian 23.62s counted=1 det=person (8.1% cyc) |

## Motion-diagnostic candidates (baseline run) overlapping truth rows

**night**: 447 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth n1 (motorcycle 4:02): cand 138 (2.97s, box h 22.5), cand 139 (3.0s, box h 16.9), cand 140 (1.43s, box h 21.2)
- truth n2 (cyclist 7:02): cand 203 (4.54s, box h 22.8), cand 205 (3.0s, box h 41.4), cand 207 (3.5s, box h 26.3), cand 209 (1.1s, box h 20.8), cand 210 (1.2s, box h 41.2), cand 211 (0.9s, box h 36.7), cand 212 (2.67s, box h 52.2), cand 213 (1.7s, box h 31.8), cand 214 (1.3s, box h 50.0), cand 215 (1.5s, box h 16.6), cand 216 (1.43s, box h 23.7), cand 217 (1.4s, box h 90.6), cand 218 (1.94s, box h 86.1), cand 219 (4.9s, box h 49.8), cand 220 (1.74s, box h 94.6)
- truth n3 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n4 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n5 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n6 (pedestrian 14:47): cand 445 (1.3s, box h 15.0), cand 446 (7.61s, box h 31.4), cand 447 (10.78s, box h 91.9)

**day**: 185 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth d2 (pedestrian 3:00): cand 30 (2.57s, box h 19.2), cand 33 (12.18s, box h 71.5), cand 34 (0.87s, box h 84.7), cand 35 (1.13s, box h 19.8), cand 36 (1.13s, box h 40.9), cand 37 (1.07s, box h 34.5), cand 38 (1.97s, box h 61.7), cand 39 (1.17s, box h 43.4)
- truth d1 (cyclist 9:10): cand 108 (1.47s, box h 45.3), cand 109 (1.47s, box h 104.7), cand 110 (1.6s, box h 36.9), cand 111 (1.13s, box h 92.3), cand 112 (3.07s, box h 34.6)
- truth d3 (pedestrian 11:45): cand 142 (8.94s, box h 100.1), cand 144 (0.87s, box h 24.9), cand 145 (3.74s, box h 64.9), cand 146 (1.87s, box h 35.8), cand 147 (3.74s, box h 30.7), cand 148 (1.27s, box h 46.4), cand 149 (1.9s, box h 34.1), cand 150 (1.17s, box h 26.5), cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1)
- truth d4 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)
- truth d5 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)


<a id="report-eval-20261015-2314"></a>
## EVAL_20261015_2314.md
Original location: `vision3/best/test_colonial/exp_results/EVAL_20261015_2314.md`.

# Experiment evaluation  (2026-10-15 23:14)

root: /orange/xiangyan/rithika/vision/vision3/best/test_colonial
runs: b4_combo_static5, b5_bright_gamma, b5_bright_clahe, b5_bright_zerodce

- truth night: 6 usable rows (5 cyclist incl. motorcycle, 1 pedestrian); skipped 0: none
- truth day: 5 usable rows (1 cyclist incl. motorcycle, 4 pedestrian); skipped 0: none
- truth night_holdout_2200: 5 usable rows (0 cyclist incl. motorcycle, 5 pedestrian); skipped 0: none
- truth day_holdout_1245: 5 usable rows (2 cyclist incl. motorcycle, 3 pedestrian); skipped 0: none

## Summary (person level; FOUND = counted with the right class; motorcycle scored as cyclist)

| run | clip | cyclists found | pedestrians found | wrong class | detected, not counted | missed | extra counted | counted bic/ped | runtime min |
|---|---|---|---|---|---|---|---|---|---|
| b4_combo_static5 | night | 4/5 | 0/1 | 1 | 1 | 0 | 0 | 5/0 | 42.9 |
| b4_combo_static5 | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 42.0 |
| b4_combo_static5 | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 0 | 0/5 | 41.8 |
| b4_combo_static5 | day_holdout_1245 | 2/2 | 3/3 | 0 | 0 | 0 | 0 | 2/3 | 41.3 |

## Detail

### b4_combo_static5 - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | FOUND | #4 cyclist 1.2s counted=1 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | FOUND | #22 cyclist 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### b4_combo_static5 - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b4_combo_static5 - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | FOUND | #18 pedestrian 10.48s counted=1 det=person (24.5% cyc) |
| p2 | pedestrian | 10:00-10:14 | FOUND | #27 pedestrian 18.72s counted=1 det=person (31.6% cyc) |
| p3 | pedestrian | 10:59-11:18 | FOUND | #33 pedestrian 14.98s counted=1 det=person (43.4% cyc) |
| p4 | pedestrian | 10:59-11:18 | FOUND | #36 pedestrian 5.84s counted=1 det=person (28.0% cyc) |
| p5 | pedestrian | 10:59-11:18 | FOUND | #40 pedestrian 3.84s counted=1 det=cyclist (76.5% cyc) |

### b4_combo_static5 - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | FOUND | #1 pedestrian 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | FOUND | #15 pedestrian 23.62s counted=1 det=person (8.1% cyc) |

## Motion-diagnostic candidates (baseline run) overlapping truth rows

**night**: 447 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth n1 (motorcycle 4:02): cand 138 (2.97s, box h 22.5), cand 139 (3.0s, box h 16.9), cand 140 (1.43s, box h 21.2)
- truth n2 (cyclist 7:02): cand 203 (4.54s, box h 22.8), cand 205 (3.0s, box h 41.4), cand 207 (3.5s, box h 26.3), cand 209 (1.1s, box h 20.8), cand 210 (1.2s, box h 41.2), cand 211 (0.9s, box h 36.7), cand 212 (2.67s, box h 52.2), cand 213 (1.7s, box h 31.8), cand 214 (1.3s, box h 50.0), cand 215 (1.5s, box h 16.6), cand 216 (1.43s, box h 23.7), cand 217 (1.4s, box h 90.6), cand 218 (1.94s, box h 86.1), cand 219 (4.9s, box h 49.8), cand 220 (1.74s, box h 94.6)
- truth n3 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n4 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n5 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n6 (pedestrian 14:47): cand 445 (1.3s, box h 15.0), cand 446 (7.61s, box h 31.4), cand 447 (10.78s, box h 91.9)

**day**: 185 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth d2 (pedestrian 3:00): cand 30 (2.57s, box h 19.2), cand 33 (12.18s, box h 71.5), cand 34 (0.87s, box h 84.7), cand 35 (1.13s, box h 19.8), cand 36 (1.13s, box h 40.9), cand 37 (1.07s, box h 34.5), cand 38 (1.97s, box h 61.7), cand 39 (1.17s, box h 43.4)
- truth d1 (cyclist 9:10): cand 108 (1.47s, box h 45.3), cand 109 (1.47s, box h 104.7), cand 110 (1.6s, box h 36.9), cand 111 (1.13s, box h 92.3), cand 112 (3.07s, box h 34.6)
- truth d3 (pedestrian 11:45): cand 142 (8.94s, box h 100.1), cand 144 (0.87s, box h 24.9), cand 145 (3.74s, box h 64.9), cand 146 (1.87s, box h 35.8), cand 147 (3.74s, box h 30.7), cand 148 (1.27s, box h 46.4), cand 149 (1.9s, box h 34.1), cand 150 (1.17s, box h 26.5), cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1)
- truth d4 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)
- truth d5 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)


<a id="report-eval-20261019-1040"></a>
## EVAL_20261019_1040.md
Original location: `vision3/best/test_colonial/exp_results/EVAL_20261019_1040.md`.

# Experiment evaluation  (2026-10-19 10:40)

root: /orange/xiangyan/rithika/vision/vision3/best/test_colonial
runs: b4_combo_static5, b5_bright_gamma, b5_bright_clahe, b5_bright_zerodce

- truth night: 6 usable rows (5 cyclist incl. motorcycle, 1 pedestrian); skipped 0: none
- truth day: 5 usable rows (1 cyclist incl. motorcycle, 4 pedestrian); skipped 0: none
- truth night_holdout_2200: 5 usable rows (0 cyclist incl. motorcycle, 5 pedestrian); skipped 0: none
- truth day_holdout_1245: 5 usable rows (2 cyclist incl. motorcycle, 3 pedestrian); skipped 0: none

## Summary (person level; FOUND = counted with the right class; motorcycle scored as cyclist)

| run | clip | cyclists found | pedestrians found | wrong class | detected, not counted | missed | extra counted | counted bic/ped | runtime min |
|---|---|---|---|---|---|---|---|---|---|
| b4_combo_static5 | night | 4/5 | 0/1 | 1 | 1 | 0 | 0 | 5/0 | 42.9 |
| b4_combo_static5 | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 42.0 |
| b4_combo_static5 | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 0 | 0/5 | 41.8 |
| b4_combo_static5 | day_holdout_1245 | 2/2 | 3/3 | 0 | 0 | 0 | 0 | 2/3 | 41.3 |
| b5_bright_gamma | night | 3/5 | 0/1 | 1 | 2 | 0 | 0 | 4/0 | 42.7 |
| b5_bright_gamma | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 0 | 0/5 | 42.4 |
| b5_bright_clahe | night | 1/5 | 0/1 | 2 | 3 | 0 | 0 | 2/1 | 44.7 |
| b5_bright_clahe | night_holdout_2200 | 0/0 | 4/5 | 0 | 1 | 0 | 0 | 0/4 | 43.2 |

## Detail

### b4_combo_static5 - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | FOUND | #4 cyclist 1.2s counted=1 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | FOUND | #22 cyclist 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### b4_combo_static5 - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b4_combo_static5 - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | FOUND | #18 pedestrian 10.48s counted=1 det=person (24.5% cyc) |
| p2 | pedestrian | 10:00-10:14 | FOUND | #27 pedestrian 18.72s counted=1 det=person (31.6% cyc) |
| p3 | pedestrian | 10:59-11:18 | FOUND | #33 pedestrian 14.98s counted=1 det=person (43.4% cyc) |
| p4 | pedestrian | 10:59-11:18 | FOUND | #36 pedestrian 5.84s counted=1 det=person (28.0% cyc) |
| p5 | pedestrian | 10:59-11:18 | FOUND | #40 pedestrian 3.84s counted=1 det=cyclist (76.5% cyc) |

### b4_combo_static5 - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | FOUND | #1 pedestrian 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | FOUND | #15 pedestrian 23.62s counted=1 det=person (8.1% cyc) |

### b5_bright_gamma - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | FOUND | #11 cyclist 1.07s counted=1 det=cyclist (96.9% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #19 cyclist 5.34s counted=1 det=cyclist (91.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #34 cyclist 3.57s counted=1 det=cyclist (50.5% cyc) |
| n4 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #37 cyclist 2.14s counted=0 det=person (26.6% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #38 cyclist 2.97s counted=0 det=cyclist (50.6% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #40 cyclist 10.01s counted=1 det=cyclist (74.0% cyc) |

### b5_bright_gamma - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | FOUND | #19 pedestrian 11.34s counted=1 det=person (20.9% cyc) |
| p2 | pedestrian | 10:00-10:14 | FOUND | #29 pedestrian 37.5s counted=1 det=person (15.5% cyc) |
| p3 | pedestrian | 10:59-11:18 | FOUND | #31 pedestrian 18.69s counted=1 det=person (36.8% cyc) |
| p4 | pedestrian | 10:59-11:18 | FOUND | #35 pedestrian 5.51s counted=1 det=person (8.5% cyc) |
| p5 | pedestrian | 10:59-11:18 | FOUND | #41 pedestrian 3.5s counted=1 det=cyclist (57.1% cyc) |

### b5_bright_clahe - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | DETECTED BUT NOT COUNTED | #23 cyclist 2.4s counted=0 det=person (44.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #41 cyclist 5.54s counted=1 det=cyclist (90.4% cyc) |
| n3 | cyclist | 14:21-14:26 | WRONG CLASS | #81 pedestrian 3.6s counted=1 det=person (48.1% cyc) |
| n4 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #82 pedestrian 1.8s counted=0 det=person (25.9% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #85 pedestrian 2.57s counted=0 det=person (49.4% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #88 cyclist 7.21s counted=1 det=cyclist (69.0% cyc) |

### b5_bright_clahe - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | FOUND | #34 pedestrian 11.54s counted=1 det=person (16.5% cyc) |
| p2 | pedestrian | 10:00-10:14 | FOUND | #55 pedestrian 32.63s counted=1 det=person (12.3% cyc) |
| p3 | pedestrian | 10:59-11:18 | FOUND | #72 pedestrian 15.52s counted=1 det=person (24.9% cyc) |
| p4 | pedestrian | 10:59-11:18 | FOUND | #82 pedestrian 6.91s counted=1 det=person (31.4% cyc) |
| p5 | pedestrian | 10:59-11:18 | DETECTED BUT NOT COUNTED | #89 pedestrian 1.74s counted=0 det=person (26.9% cyc) |

## Motion-diagnostic candidates (baseline run) overlapping truth rows

**night**: 447 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth n1 (motorcycle 4:02): cand 138 (2.97s, box h 22.5), cand 139 (3.0s, box h 16.9), cand 140 (1.43s, box h 21.2)
- truth n2 (cyclist 7:02): cand 203 (4.54s, box h 22.8), cand 205 (3.0s, box h 41.4), cand 207 (3.5s, box h 26.3), cand 209 (1.1s, box h 20.8), cand 210 (1.2s, box h 41.2), cand 211 (0.9s, box h 36.7), cand 212 (2.67s, box h 52.2), cand 213 (1.7s, box h 31.8), cand 214 (1.3s, box h 50.0), cand 215 (1.5s, box h 16.6), cand 216 (1.43s, box h 23.7), cand 217 (1.4s, box h 90.6), cand 218 (1.94s, box h 86.1), cand 219 (4.9s, box h 49.8), cand 220 (1.74s, box h 94.6)
- truth n3 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n4 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n5 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n6 (pedestrian 14:47): cand 445 (1.3s, box h 15.0), cand 446 (7.61s, box h 31.4), cand 447 (10.78s, box h 91.9)

**day**: 185 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth d2 (pedestrian 3:00): cand 30 (2.57s, box h 19.2), cand 33 (12.18s, box h 71.5), cand 34 (0.87s, box h 84.7), cand 35 (1.13s, box h 19.8), cand 36 (1.13s, box h 40.9), cand 37 (1.07s, box h 34.5), cand 38 (1.97s, box h 61.7), cand 39 (1.17s, box h 43.4)
- truth d1 (cyclist 9:10): cand 108 (1.47s, box h 45.3), cand 109 (1.47s, box h 104.7), cand 110 (1.6s, box h 36.9), cand 111 (1.13s, box h 92.3), cand 112 (3.07s, box h 34.6)
- truth d3 (pedestrian 11:45): cand 142 (8.94s, box h 100.1), cand 144 (0.87s, box h 24.9), cand 145 (3.74s, box h 64.9), cand 146 (1.87s, box h 35.8), cand 147 (3.74s, box h 30.7), cand 148 (1.27s, box h 46.4), cand 149 (1.9s, box h 34.1), cand 150 (1.17s, box h 26.5), cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1)
- truth d4 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)
- truth d5 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)


<a id="report-eval-batch2-20261008-1612"></a>
## EVAL_batch2_20261008_1612.md
Original location: `vision3/best/test_colonial/exp_results/EVAL_batch2_20261008_1612.md`.

# Experiment evaluation  (2026-10-08 23:36)

root: /orange/xiangyan/rithika/vision/vision3/best/test_colonial
runs: exp0_base, exp1_sahi, b2_0_base, b2_2_sahi, b2_1_fuse, b2_3_sahi_fuse, b2_4_sahi_fuse_nightshort, b2_5_sahi_speed

- truth night: 6 usable rows (5 cyclist incl. motorcycle, 1 pedestrian); skipped 0: none
- truth day: 5 usable rows (1 cyclist incl. motorcycle, 4 pedestrian); skipped 0: none
- truth night_holdout_2200: 0 usable rows (0 cyclist incl. motorcycle, 0 pedestrian); skipped 1: (missing file /orange/xiangyan/rithika/vision/vision3/best/test_colonial/truth/night_2200_truth.csv)
- truth day_holdout_1245: 0 usable rows (0 cyclist incl. motorcycle, 0 pedestrian); skipped 1: (missing file /orange/xiangyan/rithika/vision/vision3/best/test_colonial/truth/day_1245_truth.csv)

## Summary (person level; FOUND = counted with the right class; motorcycle scored as cyclist)

| run | clip | cyclists found | pedestrians found | wrong class | detected, not counted | missed | extra counted | counted bic/ped | runtime min |
|---|---|---|---|---|---|---|---|---|---|
| exp0_base | night | 0/5 | 0/1 | 0 | 4 | 2 | 0 | 0/0 | 30.1 |
| exp0_base | day | 1/1 | 2/4 | 0 | 2 | 0 | 0 | 1/2 | 30.6 |
| exp1_sahi | night | 2/5 | 0/1 | 2 | 2 | 0 | 0 | 3/1 | 42.2 |
| exp1_sahi | day | 1/1 | 2/4 | 2 | 0 | 0 | 0 | 3/2 | 43.1 |
| b2_0_base | night_holdout_2200 | 0/0 | 0/0 | 0 | 0 | 0 | 0 | 0/0 | 28.8 |
| b2_0_base | day_holdout_1245 | 0/0 | 0/0 | 0 | 0 | 0 | 5 | 4/1 | 28.7 |
| b2_2_sahi | night_holdout_2200 | 0/0 | 0/0 | 0 | 0 | 0 | 7 | 0/7 | 43.1 |
| b2_2_sahi | day_holdout_1245 | 0/0 | 0/0 | 0 | 0 | 0 | 5 | 4/1 | 42.3 |
| b2_1_fuse | night | 0/5 | 0/1 | 0 | 4 | 2 | 0 | 0/0 | 29.0 |
| b2_1_fuse | day | 1/1 | 2/4 | 0 | 2 | 0 | 0 | 1/2 | 28.6 |
| b2_1_fuse | night_holdout_2200 | 0/0 | 0/0 | 0 | 0 | 0 | 0 | 0/0 | 29.2 |
| b2_1_fuse | day_holdout_1245 | 0/0 | 0/0 | 0 | 0 | 0 | 5 | 3/2 | 28.7 |
| b2_3_sahi_fuse | night | 2/5 | 0/1 | 2 | 2 | 0 | 0 | 3/1 | 42.0 |
| b2_3_sahi_fuse | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 41.4 |
| b2_3_sahi_fuse | night_holdout_2200 | 0/0 | 0/0 | 0 | 0 | 0 | 7 | 0/7 | 42.5 |
| b2_3_sahi_fuse | day_holdout_1245 | 0/0 | 0/0 | 0 | 0 | 0 | 5 | 3/2 | 41.7 |
| b2_4_sahi_fuse_nightshort | night | 3/5 | 0/1 | 2 | 1 | 0 | 0 | 4/1 | 41.6 |
| b2_4_sahi_fuse_nightshort | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 42.1 |
| b2_4_sahi_fuse_nightshort | night_holdout_2200 | 0/0 | 0/0 | 0 | 0 | 0 | 7 | 0/7 | 41.9 |
| b2_4_sahi_fuse_nightshort | day_holdout_1245 | 0/0 | 0/0 | 0 | 0 | 0 | 5 | 3/2 | 42.2 |
| b2_5_sahi_speed | night | 3/5 | 0/1 | 1 | 2 | 0 | 0 | 4/0 | 41.9 |
| b2_5_sahi_speed | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 42.7 |
| b2_5_sahi_speed | night_holdout_2200 | 0/0 | 0/0 | 0 | 0 | 0 | 7 | 0/7 | 42.4 |
| b2_5_sahi_speed | day_holdout_1245 | 0/0 | 0/0 | 0 | 0 | 0 | 5 | 3/2 | 42.2 |

## Detail

### exp0_base - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | DETECTED BUT NOT COUNTED | #1 cyclist 0.6s counted=0 det=cyclist (100.0% cyc) |
| n2 | cyclist | 7:02-7:09 | DETECTED BUT NOT COUNTED | #2 cyclist 0.43s counted=0 det=cyclist (100.0% cyc) |
| n3 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #4 cyclist 0.9s counted=0 det=cyclist (59.3% cyc) |
| n4 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #6 unscored 0.03s counted=0 det=cyclist (100.0% cyc) |
| n5 | cyclist | 14:21-14:26 | MISSED |  |
| n6 | pedestrian | 14:47-14:58 | MISSED |  |

### exp0_base - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #3 pedestrian 3.2s counted=1 det=person (0.0% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #5 cyclist 4.04s counted=1 det=person (34.7% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #8 pedestrian 16.85s counted=1 det=person (0.2% cyc) |
| d4 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #12 pedestrian 2.07s counted=0 det=person (0.0% cyc) |
| d5 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #13 pedestrian 1.2s counted=0 det=person (0.0% cyc) |

### exp1_sahi - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | DETECTED BUT NOT COUNTED | #4 cyclist 1.2s counted=0 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | WRONG CLASS | #22 pedestrian 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### exp1_sahi - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | WRONG CLASS | #2 cyclist 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | WRONG CLASS | #13 cyclist 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b2_0_base - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|

### b2_0_base - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| EXTRA | counted cyclist | 0:40-0:57 | no truth row | #1 9.11s det=person |
| EXTRA | counted cyclist | 8:07-8:14 | no truth row | #4 3.67s det=person |
| EXTRA | counted cyclist | 8:45-8:53 | no truth row | #6 6.97s det=person |
| EXTRA | counted pedestrian | 9:53-10:04 | no truth row | #7 4.84s det=person |
| EXTRA | counted cyclist | 11:16-11:39 | no truth row | #9 18.59s det=person |

### b2_2_sahi - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| EXTRA | counted pedestrian | 6:00-6:13 | no truth row | #18 10.48s det=person |
| EXTRA | counted pedestrian | 7:50-8:27 | no truth row | #24 4.97s det=person |
| EXTRA | counted pedestrian | 8:32-9:00 | no truth row | #26 3.8s det=person |
| EXTRA | counted pedestrian | 9:05-10:15 | no truth row | #27 18.72s det=person |
| EXTRA | counted pedestrian | 10:42-11:18 | no truth row | #33 14.98s det=person |
| EXTRA | counted pedestrian | 11:05-11:16 | no truth row | #36 5.84s det=person |
| EXTRA | counted pedestrian | 11:12-11:18 | no truth row | #40 3.84s det=cyclist |

### b2_2_sahi - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| EXTRA | counted cyclist | 0:40-0:59 | no truth row | #1 15.48s det=person |
| EXTRA | counted cyclist | 8:07-8:16 | no truth row | #7 8.17s det=person |
| EXTRA | counted cyclist | 8:44-8:55 | no truth row | #9 9.68s det=cyclist |
| EXTRA | counted pedestrian | 9:53-10:05 | no truth row | #14 7.21s det=person |
| EXTRA | counted cyclist | 11:14-11:40 | no truth row | #15 23.62s det=person |

### b2_1_fuse - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | DETECTED BUT NOT COUNTED | #1 cyclist 0.6s counted=0 det=cyclist (100.0% cyc) |
| n2 | cyclist | 7:02-7:09 | DETECTED BUT NOT COUNTED | #2 cyclist 0.43s counted=0 det=cyclist (100.0% cyc) |
| n3 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #4 cyclist 0.9s counted=0 det=cyclist (59.3% cyc) |
| n4 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #6 unscored 0.03s counted=0 det=cyclist (100.0% cyc) |
| n5 | cyclist | 14:21-14:26 | MISSED |  |
| n6 | pedestrian | 14:47-14:58 | MISSED |  |

### b2_1_fuse - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #3 pedestrian 3.2s counted=1 det=person (0.0% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #5 cyclist 4.04s counted=1 det=person (34.7% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #8 pedestrian 16.85s counted=1 det=person (0.2% cyc) |
| d4 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #12 pedestrian 2.07s counted=0 det=person (0.0% cyc) |
| d5 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #13 pedestrian 1.2s counted=0 det=person (0.0% cyc) |

### b2_1_fuse - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|

### b2_1_fuse - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| EXTRA | counted cyclist | 0:40-0:57 | no truth row | #1 9.11s det=person |
| EXTRA | counted cyclist | 8:07-8:14 | no truth row | #4 3.67s det=person |
| EXTRA | counted cyclist | 8:45-8:53 | no truth row | #6 6.97s det=person |
| EXTRA | counted pedestrian | 9:53-10:04 | no truth row | #7 4.84s det=person |
| EXTRA | counted pedestrian | 11:16-11:39 | no truth row | #9 18.59s det=person |

### b2_3_sahi_fuse - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | DETECTED BUT NOT COUNTED | #4 cyclist 1.2s counted=0 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | WRONG CLASS | #22 pedestrian 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### b2_3_sahi_fuse - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b2_3_sahi_fuse - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| EXTRA | counted pedestrian | 6:00-6:13 | no truth row | #18 10.48s det=person |
| EXTRA | counted pedestrian | 7:50-8:27 | no truth row | #24 4.97s det=person |
| EXTRA | counted pedestrian | 8:32-9:00 | no truth row | #26 3.8s det=person |
| EXTRA | counted pedestrian | 9:05-10:15 | no truth row | #27 18.72s det=person |
| EXTRA | counted pedestrian | 10:42-11:18 | no truth row | #33 14.98s det=person |
| EXTRA | counted pedestrian | 11:05-11:16 | no truth row | #36 5.84s det=person |
| EXTRA | counted pedestrian | 11:12-11:18 | no truth row | #40 3.84s det=cyclist |

### b2_3_sahi_fuse - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| EXTRA | counted cyclist | 0:40-0:59 | no truth row | #1 15.48s det=person |
| EXTRA | counted cyclist | 8:07-8:16 | no truth row | #7 8.17s det=person |
| EXTRA | counted cyclist | 8:44-8:55 | no truth row | #9 9.68s det=cyclist |
| EXTRA | counted pedestrian | 9:53-10:05 | no truth row | #14 7.21s det=person |
| EXTRA | counted pedestrian | 11:14-11:40 | no truth row | #15 23.62s det=person |

### b2_4_sahi_fuse_nightshort - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | FOUND | #4 cyclist 1.2s counted=1 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | WRONG CLASS | #22 pedestrian 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### b2_4_sahi_fuse_nightshort - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b2_4_sahi_fuse_nightshort - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| EXTRA | counted pedestrian | 6:00-6:13 | no truth row | #18 10.48s det=person |
| EXTRA | counted pedestrian | 7:50-8:27 | no truth row | #24 4.97s det=person |
| EXTRA | counted pedestrian | 8:32-9:00 | no truth row | #26 3.8s det=person |
| EXTRA | counted pedestrian | 9:05-10:15 | no truth row | #27 18.72s det=person |
| EXTRA | counted pedestrian | 10:42-11:18 | no truth row | #33 14.98s det=person |
| EXTRA | counted pedestrian | 11:05-11:16 | no truth row | #36 5.84s det=person |
| EXTRA | counted pedestrian | 11:12-11:18 | no truth row | #40 3.84s det=cyclist |

### b2_4_sahi_fuse_nightshort - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| EXTRA | counted cyclist | 0:40-0:59 | no truth row | #1 15.48s det=person |
| EXTRA | counted cyclist | 8:07-8:16 | no truth row | #7 8.17s det=person |
| EXTRA | counted cyclist | 8:44-8:55 | no truth row | #9 9.68s det=cyclist |
| EXTRA | counted pedestrian | 9:53-10:05 | no truth row | #14 7.21s det=person |
| EXTRA | counted pedestrian | 11:14-11:40 | no truth row | #15 23.62s det=person |

### b2_5_sahi_speed - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | DETECTED BUT NOT COUNTED | #4 cyclist 1.2s counted=0 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | FOUND | #22 cyclist 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### b2_5_sahi_speed - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b2_5_sahi_speed - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| EXTRA | counted pedestrian | 6:00-6:13 | no truth row | #18 10.48s det=person |
| EXTRA | counted pedestrian | 7:50-8:27 | no truth row | #24 4.97s det=person |
| EXTRA | counted pedestrian | 8:32-9:00 | no truth row | #26 3.8s det=person |
| EXTRA | counted pedestrian | 9:05-10:15 | no truth row | #27 18.72s det=person |
| EXTRA | counted pedestrian | 10:42-11:18 | no truth row | #33 14.98s det=person |
| EXTRA | counted pedestrian | 11:05-11:16 | no truth row | #36 5.84s det=person |
| EXTRA | counted pedestrian | 11:12-11:18 | no truth row | #40 3.84s det=cyclist |

### b2_5_sahi_speed - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| EXTRA | counted pedestrian | 0:40-0:59 | no truth row | #1 15.48s det=person |
| EXTRA | counted cyclist | 8:07-8:16 | no truth row | #7 8.17s det=person |
| EXTRA | counted cyclist | 8:44-8:55 | no truth row | #9 9.68s det=cyclist |
| EXTRA | counted pedestrian | 9:53-10:05 | no truth row | #14 7.21s det=person |
| EXTRA | counted cyclist | 11:14-11:40 | no truth row | #15 23.62s det=person |

## Motion-diagnostic candidates (baseline run) overlapping truth rows

**night**: 447 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth n1 (motorcycle 4:02): cand 138 (2.97s, box h 22.5), cand 139 (3.0s, box h 16.9), cand 140 (1.43s, box h 21.2)
- truth n2 (cyclist 7:02): cand 203 (4.54s, box h 22.8), cand 205 (3.0s, box h 41.4), cand 207 (3.5s, box h 26.3), cand 209 (1.1s, box h 20.8), cand 210 (1.2s, box h 41.2), cand 211 (0.9s, box h 36.7), cand 212 (2.67s, box h 52.2), cand 213 (1.7s, box h 31.8), cand 214 (1.3s, box h 50.0), cand 215 (1.5s, box h 16.6), cand 216 (1.43s, box h 23.7), cand 217 (1.4s, box h 90.6), cand 218 (1.94s, box h 86.1), cand 219 (4.9s, box h 49.8), cand 220 (1.74s, box h 94.6)
- truth n3 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n4 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n5 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n6 (pedestrian 14:47): cand 445 (1.3s, box h 15.0), cand 446 (7.61s, box h 31.4), cand 447 (10.78s, box h 91.9)

**day**: 185 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth d2 (pedestrian 3:00): cand 30 (2.57s, box h 19.2), cand 33 (12.18s, box h 71.5), cand 34 (0.87s, box h 84.7), cand 35 (1.13s, box h 19.8), cand 36 (1.13s, box h 40.9), cand 37 (1.07s, box h 34.5), cand 38 (1.97s, box h 61.7), cand 39 (1.17s, box h 43.4)
- truth d1 (cyclist 9:10): cand 108 (1.47s, box h 45.3), cand 109 (1.47s, box h 104.7), cand 110 (1.6s, box h 36.9), cand 111 (1.13s, box h 92.3), cand 112 (3.07s, box h 34.6)
- truth d3 (pedestrian 11:45): cand 142 (8.94s, box h 100.1), cand 144 (0.87s, box h 24.9), cand 145 (3.74s, box h 64.9), cand 146 (1.87s, box h 35.8), cand 147 (3.74s, box h 30.7), cand 148 (1.27s, box h 46.4), cand 149 (1.9s, box h 34.1), cand 150 (1.17s, box h 26.5), cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1)
- truth d4 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)
- truth d5 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)


<a id="report-eval-batch3-20261010-2152"></a>
## EVAL_batch3_20261010_2152.md
Original location: `vision3/best/test_colonial/exp_results/EVAL_batch3_20261010_2152.md`.

# Experiment evaluation  (2026-10-10 23:25)

root: /orange/xiangyan/rithika/vision/vision3/best/test_colonial
runs: exp0_base, exp1_sahi, b2_0_base, b2_2_sahi, b2_3_sahi_fuse, b2_4_sahi_fuse_nightshort, b2_5_sahi_speed, b3_combo

- truth night: 6 usable rows (5 cyclist incl. motorcycle, 1 pedestrian); skipped 0: none
- truth day: 5 usable rows (1 cyclist incl. motorcycle, 4 pedestrian); skipped 0: none
- truth night_holdout_2200: 5 usable rows (0 cyclist incl. motorcycle, 5 pedestrian); skipped 0: none
- truth day_holdout_1245: 5 usable rows (2 cyclist incl. motorcycle, 3 pedestrian); skipped 0: none

## Summary (person level; FOUND = counted with the right class; motorcycle scored as cyclist)

| run | clip | cyclists found | pedestrians found | wrong class | detected, not counted | missed | extra counted | counted bic/ped | runtime min |
|---|---|---|---|---|---|---|---|---|---|
| exp0_base | night | 0/5 | 0/1 | 0 | 4 | 2 | 0 | 0/0 | 30.1 |
| exp0_base | day | 1/1 | 2/4 | 0 | 2 | 0 | 0 | 1/2 | 30.6 |
| exp1_sahi | night | 2/5 | 0/1 | 2 | 2 | 0 | 0 | 3/1 | 42.2 |
| exp1_sahi | day | 1/1 | 2/4 | 2 | 0 | 0 | 0 | 3/2 | 43.1 |
| b2_0_base | night_holdout_2200 | 0/0 | 0/5 | 0 | 2 | 3 | 0 | 0/0 | 28.8 |
| b2_0_base | day_holdout_1245 | 2/2 | 1/3 | 2 | 0 | 0 | 0 | 4/1 | 28.7 |
| b2_2_sahi | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 2 | 0/7 | 43.1 |
| b2_2_sahi | day_holdout_1245 | 2/2 | 1/3 | 2 | 0 | 0 | 0 | 4/1 | 42.3 |
| b2_3_sahi_fuse | night | 2/5 | 0/1 | 2 | 2 | 0 | 0 | 3/1 | 42.0 |
| b2_3_sahi_fuse | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 41.4 |
| b2_3_sahi_fuse | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 2 | 0/7 | 42.5 |
| b2_3_sahi_fuse | day_holdout_1245 | 2/2 | 2/3 | 1 | 0 | 0 | 0 | 3/2 | 41.7 |
| b2_4_sahi_fuse_nightshort | night | 3/5 | 0/1 | 2 | 1 | 0 | 0 | 4/1 | 41.6 |
| b2_4_sahi_fuse_nightshort | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 42.1 |
| b2_4_sahi_fuse_nightshort | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 2 | 0/7 | 41.9 |
| b2_4_sahi_fuse_nightshort | day_holdout_1245 | 2/2 | 2/3 | 1 | 0 | 0 | 0 | 3/2 | 42.2 |
| b2_5_sahi_speed | night | 3/5 | 0/1 | 1 | 2 | 0 | 0 | 4/0 | 41.9 |
| b2_5_sahi_speed | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 42.7 |
| b2_5_sahi_speed | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 2 | 0/7 | 42.4 |
| b2_5_sahi_speed | day_holdout_1245 | 2/2 | 2/3 | 1 | 0 | 0 | 0 | 3/2 | 42.2 |
| b3_combo | night | 4/5 | 0/1 | 1 | 1 | 0 | 0 | 5/0 | 42.1 |
| b3_combo | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 41.9 |
| b3_combo | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 2 | 0/7 | 42.1 |
| b3_combo | day_holdout_1245 | 2/2 | 3/3 | 0 | 0 | 0 | 0 | 2/3 | 41.3 |

## Detail

### exp0_base - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | DETECTED BUT NOT COUNTED | #1 cyclist 0.6s counted=0 det=cyclist (100.0% cyc) |
| n2 | cyclist | 7:02-7:09 | DETECTED BUT NOT COUNTED | #2 cyclist 0.43s counted=0 det=cyclist (100.0% cyc) |
| n3 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #4 cyclist 0.9s counted=0 det=cyclist (59.3% cyc) |
| n4 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #6 unscored 0.03s counted=0 det=cyclist (100.0% cyc) |
| n5 | cyclist | 14:21-14:26 | MISSED |  |
| n6 | pedestrian | 14:47-14:58 | MISSED |  |

### exp0_base - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #3 pedestrian 3.2s counted=1 det=person (0.0% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #5 cyclist 4.04s counted=1 det=person (34.7% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #8 pedestrian 16.85s counted=1 det=person (0.2% cyc) |
| d4 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #12 pedestrian 2.07s counted=0 det=person (0.0% cyc) |
| d5 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #13 pedestrian 1.2s counted=0 det=person (0.0% cyc) |

### exp1_sahi - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | DETECTED BUT NOT COUNTED | #4 cyclist 1.2s counted=0 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | WRONG CLASS | #22 pedestrian 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### exp1_sahi - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | WRONG CLASS | #2 cyclist 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | WRONG CLASS | #13 cyclist 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b2_0_base - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | MISSED |  |
| p2 | pedestrian | 10:00-10:14 | DETECTED BUT NOT COUNTED | #3 pedestrian 0.43s counted=0 det=cyclist (100.0% cyc) |
| p3 | pedestrian | 10:59-11:18 | DETECTED BUT NOT COUNTED | #6 unscored 0.17s counted=0 det=cyclist (100.0% cyc) |
| p4 | pedestrian | 10:59-11:18 | MISSED |  |
| p5 | pedestrian | 10:59-11:18 | MISSED |  |

### b2_0_base - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | WRONG CLASS | #1 cyclist 9.11s counted=1 det=person (44.7% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #4 cyclist 3.67s counted=1 det=person (46.4% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #6 cyclist 6.97s counted=1 det=person (45.0% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #7 pedestrian 4.84s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | WRONG CLASS | #9 cyclist 18.59s counted=1 det=person (6.6% cyc) |

### b2_2_sahi - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | FOUND | #18 pedestrian 10.48s counted=1 det=person (24.5% cyc) |
| p2 | pedestrian | 10:00-10:14 | FOUND | #27 pedestrian 18.72s counted=1 det=person (31.6% cyc) |
| p3 | pedestrian | 10:59-11:18 | FOUND | #33 pedestrian 14.98s counted=1 det=person (43.4% cyc) |
| p4 | pedestrian | 10:59-11:18 | FOUND | #36 pedestrian 5.84s counted=1 det=person (28.0% cyc) |
| p5 | pedestrian | 10:59-11:18 | FOUND | #40 pedestrian 3.84s counted=1 det=cyclist (76.5% cyc) |
| EXTRA | counted pedestrian | 7:50-8:27 | no truth row | #24 4.97s det=person |
| EXTRA | counted pedestrian | 8:32-9:00 | no truth row | #26 3.8s det=person |

### b2_2_sahi - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | WRONG CLASS | #1 cyclist 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | WRONG CLASS | #15 cyclist 23.62s counted=1 det=person (8.1% cyc) |

### b2_3_sahi_fuse - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | DETECTED BUT NOT COUNTED | #4 cyclist 1.2s counted=0 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | WRONG CLASS | #22 pedestrian 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### b2_3_sahi_fuse - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b2_3_sahi_fuse - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | FOUND | #18 pedestrian 10.48s counted=1 det=person (24.5% cyc) |
| p2 | pedestrian | 10:00-10:14 | FOUND | #27 pedestrian 18.72s counted=1 det=person (31.6% cyc) |
| p3 | pedestrian | 10:59-11:18 | FOUND | #33 pedestrian 14.98s counted=1 det=person (43.4% cyc) |
| p4 | pedestrian | 10:59-11:18 | FOUND | #36 pedestrian 5.84s counted=1 det=person (28.0% cyc) |
| p5 | pedestrian | 10:59-11:18 | FOUND | #40 pedestrian 3.84s counted=1 det=cyclist (76.5% cyc) |
| EXTRA | counted pedestrian | 7:50-8:27 | no truth row | #24 4.97s det=person |
| EXTRA | counted pedestrian | 8:32-9:00 | no truth row | #26 3.8s det=person |

### b2_3_sahi_fuse - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | WRONG CLASS | #1 cyclist 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | FOUND | #15 pedestrian 23.62s counted=1 det=person (8.1% cyc) |

### b2_4_sahi_fuse_nightshort - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | FOUND | #4 cyclist 1.2s counted=1 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | WRONG CLASS | #22 pedestrian 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### b2_4_sahi_fuse_nightshort - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b2_4_sahi_fuse_nightshort - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | FOUND | #18 pedestrian 10.48s counted=1 det=person (24.5% cyc) |
| p2 | pedestrian | 10:00-10:14 | FOUND | #27 pedestrian 18.72s counted=1 det=person (31.6% cyc) |
| p3 | pedestrian | 10:59-11:18 | FOUND | #33 pedestrian 14.98s counted=1 det=person (43.4% cyc) |
| p4 | pedestrian | 10:59-11:18 | FOUND | #36 pedestrian 5.84s counted=1 det=person (28.0% cyc) |
| p5 | pedestrian | 10:59-11:18 | FOUND | #40 pedestrian 3.84s counted=1 det=cyclist (76.5% cyc) |
| EXTRA | counted pedestrian | 7:50-8:27 | no truth row | #24 4.97s det=person |
| EXTRA | counted pedestrian | 8:32-9:00 | no truth row | #26 3.8s det=person |

### b2_4_sahi_fuse_nightshort - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | WRONG CLASS | #1 cyclist 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | FOUND | #15 pedestrian 23.62s counted=1 det=person (8.1% cyc) |

### b2_5_sahi_speed - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | DETECTED BUT NOT COUNTED | #4 cyclist 1.2s counted=0 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | FOUND | #22 cyclist 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### b2_5_sahi_speed - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b2_5_sahi_speed - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | FOUND | #18 pedestrian 10.48s counted=1 det=person (24.5% cyc) |
| p2 | pedestrian | 10:00-10:14 | FOUND | #27 pedestrian 18.72s counted=1 det=person (31.6% cyc) |
| p3 | pedestrian | 10:59-11:18 | FOUND | #33 pedestrian 14.98s counted=1 det=person (43.4% cyc) |
| p4 | pedestrian | 10:59-11:18 | FOUND | #36 pedestrian 5.84s counted=1 det=person (28.0% cyc) |
| p5 | pedestrian | 10:59-11:18 | FOUND | #40 pedestrian 3.84s counted=1 det=cyclist (76.5% cyc) |
| EXTRA | counted pedestrian | 7:50-8:27 | no truth row | #24 4.97s det=person |
| EXTRA | counted pedestrian | 8:32-9:00 | no truth row | #26 3.8s det=person |

### b2_5_sahi_speed - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | FOUND | #1 pedestrian 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | WRONG CLASS | #15 cyclist 23.62s counted=1 det=person (8.1% cyc) |

### b3_combo - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | FOUND | #4 cyclist 1.2s counted=1 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | FOUND | #22 cyclist 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### b3_combo - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b3_combo - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | FOUND | #18 pedestrian 10.48s counted=1 det=person (24.5% cyc) |
| p2 | pedestrian | 10:00-10:14 | FOUND | #27 pedestrian 18.72s counted=1 det=person (31.6% cyc) |
| p3 | pedestrian | 10:59-11:18 | FOUND | #33 pedestrian 14.98s counted=1 det=person (43.4% cyc) |
| p4 | pedestrian | 10:59-11:18 | FOUND | #36 pedestrian 5.84s counted=1 det=person (28.0% cyc) |
| p5 | pedestrian | 10:59-11:18 | FOUND | #40 pedestrian 3.84s counted=1 det=cyclist (76.5% cyc) |
| EXTRA | counted pedestrian | 7:50-8:27 | no truth row | #24 4.97s det=person |
| EXTRA | counted pedestrian | 8:32-9:00 | no truth row | #26 3.8s det=person |

### b3_combo - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | FOUND | #1 pedestrian 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | FOUND | #15 pedestrian 23.62s counted=1 det=person (8.1% cyc) |

## Motion-diagnostic candidates (baseline run) overlapping truth rows

**night**: 447 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth n1 (motorcycle 4:02): cand 138 (2.97s, box h 22.5), cand 139 (3.0s, box h 16.9), cand 140 (1.43s, box h 21.2)
- truth n2 (cyclist 7:02): cand 203 (4.54s, box h 22.8), cand 205 (3.0s, box h 41.4), cand 207 (3.5s, box h 26.3), cand 209 (1.1s, box h 20.8), cand 210 (1.2s, box h 41.2), cand 211 (0.9s, box h 36.7), cand 212 (2.67s, box h 52.2), cand 213 (1.7s, box h 31.8), cand 214 (1.3s, box h 50.0), cand 215 (1.5s, box h 16.6), cand 216 (1.43s, box h 23.7), cand 217 (1.4s, box h 90.6), cand 218 (1.94s, box h 86.1), cand 219 (4.9s, box h 49.8), cand 220 (1.74s, box h 94.6)
- truth n3 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n4 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n5 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n6 (pedestrian 14:47): cand 445 (1.3s, box h 15.0), cand 446 (7.61s, box h 31.4), cand 447 (10.78s, box h 91.9)

**day**: 185 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth d2 (pedestrian 3:00): cand 30 (2.57s, box h 19.2), cand 33 (12.18s, box h 71.5), cand 34 (0.87s, box h 84.7), cand 35 (1.13s, box h 19.8), cand 36 (1.13s, box h 40.9), cand 37 (1.07s, box h 34.5), cand 38 (1.97s, box h 61.7), cand 39 (1.17s, box h 43.4)
- truth d1 (cyclist 9:10): cand 108 (1.47s, box h 45.3), cand 109 (1.47s, box h 104.7), cand 110 (1.6s, box h 36.9), cand 111 (1.13s, box h 92.3), cand 112 (3.07s, box h 34.6)
- truth d3 (pedestrian 11:45): cand 142 (8.94s, box h 100.1), cand 144 (0.87s, box h 24.9), cand 145 (3.74s, box h 64.9), cand 146 (1.87s, box h 35.8), cand 147 (3.74s, box h 30.7), cand 148 (1.27s, box h 46.4), cand 149 (1.9s, box h 34.1), cand 150 (1.17s, box h 26.5), cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1)
- truth d4 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)
- truth d5 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)


<a id="report-eval-batch4-20261011-1355"></a>
## EVAL_batch4_20261011_1355.md
Original location: `vision3/best/test_colonial/exp_results/EVAL_batch4_20261011_1355.md`.

# Experiment evaluation  (2026-10-11 17:02)

root: /orange/xiangyan/rithika/vision/vision3/best/test_colonial
runs: exp0_base, b2_2_sahi, b3_combo, b4_combo_disp5

- truth night: 6 usable rows (5 cyclist incl. motorcycle, 1 pedestrian); skipped 0: none
- truth day: 5 usable rows (1 cyclist incl. motorcycle, 4 pedestrian); skipped 0: none
- truth night_holdout_2200: 5 usable rows (0 cyclist incl. motorcycle, 5 pedestrian); skipped 0: none
- truth day_holdout_1245: 5 usable rows (2 cyclist incl. motorcycle, 3 pedestrian); skipped 0: none

## Summary (person level; FOUND = counted with the right class; motorcycle scored as cyclist)

| run | clip | cyclists found | pedestrians found | wrong class | detected, not counted | missed | extra counted | counted bic/ped | runtime min |
|---|---|---|---|---|---|---|---|---|---|
| exp0_base | night | 0/5 | 0/1 | 0 | 4 | 2 | 0 | 0/0 | 30.1 |
| exp0_base | day | 1/1 | 2/4 | 0 | 2 | 0 | 0 | 1/2 | 30.6 |
| b2_2_sahi | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 2 | 0/7 | 43.1 |
| b2_2_sahi | day_holdout_1245 | 2/2 | 1/3 | 2 | 0 | 0 | 0 | 4/1 | 42.3 |
| b3_combo | night | 4/5 | 0/1 | 1 | 1 | 0 | 0 | 5/0 | 42.1 |
| b3_combo | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 41.9 |
| b3_combo | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 2 | 0/7 | 42.1 |
| b3_combo | day_holdout_1245 | 2/2 | 3/3 | 0 | 0 | 0 | 0 | 2/3 | 41.3 |
| b4_combo_disp5 | night | 4/5 | 0/1 | 1 | 1 | 0 | 0 | 5/0 | 41.8 |
| b4_combo_disp5 | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 43.2 |
| b4_combo_disp5 | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 0 | 0/5 | 41.9 |
| b4_combo_disp5 | day_holdout_1245 | 2/2 | 3/3 | 0 | 0 | 0 | 0 | 2/3 | 42.4 |

## Detail

### exp0_base - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | DETECTED BUT NOT COUNTED | #1 cyclist 0.6s counted=0 det=cyclist (100.0% cyc) |
| n2 | cyclist | 7:02-7:09 | DETECTED BUT NOT COUNTED | #2 cyclist 0.43s counted=0 det=cyclist (100.0% cyc) |
| n3 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #4 cyclist 0.9s counted=0 det=cyclist (59.3% cyc) |
| n4 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #6 unscored 0.03s counted=0 det=cyclist (100.0% cyc) |
| n5 | cyclist | 14:21-14:26 | MISSED |  |
| n6 | pedestrian | 14:47-14:58 | MISSED |  |

### exp0_base - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #3 pedestrian 3.2s counted=1 det=person (0.0% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #5 cyclist 4.04s counted=1 det=person (34.7% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #8 pedestrian 16.85s counted=1 det=person (0.2% cyc) |
| d4 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #12 pedestrian 2.07s counted=0 det=person (0.0% cyc) |
| d5 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #13 pedestrian 1.2s counted=0 det=person (0.0% cyc) |

### b2_2_sahi - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | FOUND | #18 pedestrian 10.48s counted=1 det=person (24.5% cyc) |
| p2 | pedestrian | 10:00-10:14 | FOUND | #27 pedestrian 18.72s counted=1 det=person (31.6% cyc) |
| p3 | pedestrian | 10:59-11:18 | FOUND | #33 pedestrian 14.98s counted=1 det=person (43.4% cyc) |
| p4 | pedestrian | 10:59-11:18 | FOUND | #36 pedestrian 5.84s counted=1 det=person (28.0% cyc) |
| p5 | pedestrian | 10:59-11:18 | FOUND | #40 pedestrian 3.84s counted=1 det=cyclist (76.5% cyc) |
| EXTRA | counted pedestrian | 7:50-8:27 | no truth row | #24 4.97s det=person |
| EXTRA | counted pedestrian | 8:32-9:00 | no truth row | #26 3.8s det=person |

### b2_2_sahi - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | WRONG CLASS | #1 cyclist 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | WRONG CLASS | #15 cyclist 23.62s counted=1 det=person (8.1% cyc) |

### b3_combo - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | FOUND | #4 cyclist 1.2s counted=1 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | FOUND | #22 cyclist 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### b3_combo - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b3_combo - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | FOUND | #18 pedestrian 10.48s counted=1 det=person (24.5% cyc) |
| p2 | pedestrian | 10:00-10:14 | FOUND | #27 pedestrian 18.72s counted=1 det=person (31.6% cyc) |
| p3 | pedestrian | 10:59-11:18 | FOUND | #33 pedestrian 14.98s counted=1 det=person (43.4% cyc) |
| p4 | pedestrian | 10:59-11:18 | FOUND | #36 pedestrian 5.84s counted=1 det=person (28.0% cyc) |
| p5 | pedestrian | 10:59-11:18 | FOUND | #40 pedestrian 3.84s counted=1 det=cyclist (76.5% cyc) |
| EXTRA | counted pedestrian | 7:50-8:27 | no truth row | #24 4.97s det=person |
| EXTRA | counted pedestrian | 8:32-9:00 | no truth row | #26 3.8s det=person |

### b3_combo - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | FOUND | #1 pedestrian 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | FOUND | #15 pedestrian 23.62s counted=1 det=person (8.1% cyc) |

### b4_combo_disp5 - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | FOUND | #4 cyclist 1.2s counted=1 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | FOUND | #22 cyclist 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### b4_combo_disp5 - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b4_combo_disp5 - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | FOUND | #18 pedestrian 10.48s counted=1 det=person (24.5% cyc) |
| p2 | pedestrian | 10:00-10:14 | FOUND | #27 pedestrian 18.72s counted=1 det=person (31.6% cyc) |
| p3 | pedestrian | 10:59-11:18 | FOUND | #33 pedestrian 14.98s counted=1 det=person (43.4% cyc) |
| p4 | pedestrian | 10:59-11:18 | FOUND | #36 pedestrian 5.84s counted=1 det=person (28.0% cyc) |
| p5 | pedestrian | 10:59-11:18 | FOUND | #40 pedestrian 3.84s counted=1 det=cyclist (76.5% cyc) |

### b4_combo_disp5 - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | FOUND | #1 pedestrian 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | FOUND | #15 pedestrian 23.62s counted=1 det=person (8.1% cyc) |

## Motion-diagnostic candidates (baseline run) overlapping truth rows

**night**: 447 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth n1 (motorcycle 4:02): cand 138 (2.97s, box h 22.5), cand 139 (3.0s, box h 16.9), cand 140 (1.43s, box h 21.2)
- truth n2 (cyclist 7:02): cand 203 (4.54s, box h 22.8), cand 205 (3.0s, box h 41.4), cand 207 (3.5s, box h 26.3), cand 209 (1.1s, box h 20.8), cand 210 (1.2s, box h 41.2), cand 211 (0.9s, box h 36.7), cand 212 (2.67s, box h 52.2), cand 213 (1.7s, box h 31.8), cand 214 (1.3s, box h 50.0), cand 215 (1.5s, box h 16.6), cand 216 (1.43s, box h 23.7), cand 217 (1.4s, box h 90.6), cand 218 (1.94s, box h 86.1), cand 219 (4.9s, box h 49.8), cand 220 (1.74s, box h 94.6)
- truth n3 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n4 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n5 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n6 (pedestrian 14:47): cand 445 (1.3s, box h 15.0), cand 446 (7.61s, box h 31.4), cand 447 (10.78s, box h 91.9)

**day**: 185 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth d2 (pedestrian 3:00): cand 30 (2.57s, box h 19.2), cand 33 (12.18s, box h 71.5), cand 34 (0.87s, box h 84.7), cand 35 (1.13s, box h 19.8), cand 36 (1.13s, box h 40.9), cand 37 (1.07s, box h 34.5), cand 38 (1.97s, box h 61.7), cand 39 (1.17s, box h 43.4)
- truth d1 (cyclist 9:10): cand 108 (1.47s, box h 45.3), cand 109 (1.47s, box h 104.7), cand 110 (1.6s, box h 36.9), cand 111 (1.13s, box h 92.3), cand 112 (3.07s, box h 34.6)
- truth d3 (pedestrian 11:45): cand 142 (8.94s, box h 100.1), cand 144 (0.87s, box h 24.9), cand 145 (3.74s, box h 64.9), cand 146 (1.87s, box h 35.8), cand 147 (3.74s, box h 30.7), cand 148 (1.27s, box h 46.4), cand 149 (1.9s, box h 34.1), cand 150 (1.17s, box h 26.5), cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1)
- truth d4 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)
- truth d5 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)


<a id="report-eval-batch4-20261011-1410"></a>
## EVAL_batch4_20261011_1410.md
Original location: `vision3/best/test_colonial/exp_results/EVAL_batch4_20261011_1410.md`.

# Experiment evaluation  (2026-10-11 17:02)

root: /orange/xiangyan/rithika/vision/vision3/best/test_colonial
runs: exp0_base, b2_2_sahi, b3_combo, b4_combo_static5

- truth night: 6 usable rows (5 cyclist incl. motorcycle, 1 pedestrian); skipped 0: none
- truth day: 5 usable rows (1 cyclist incl. motorcycle, 4 pedestrian); skipped 0: none
- truth night_holdout_2200: 5 usable rows (0 cyclist incl. motorcycle, 5 pedestrian); skipped 0: none
- truth day_holdout_1245: 5 usable rows (2 cyclist incl. motorcycle, 3 pedestrian); skipped 0: none

## Summary (person level; FOUND = counted with the right class; motorcycle scored as cyclist)

| run | clip | cyclists found | pedestrians found | wrong class | detected, not counted | missed | extra counted | counted bic/ped | runtime min |
|---|---|---|---|---|---|---|---|---|---|
| exp0_base | night | 0/5 | 0/1 | 0 | 4 | 2 | 0 | 0/0 | 30.1 |
| exp0_base | day | 1/1 | 2/4 | 0 | 2 | 0 | 0 | 1/2 | 30.6 |
| b2_2_sahi | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 2 | 0/7 | 43.1 |
| b2_2_sahi | day_holdout_1245 | 2/2 | 1/3 | 2 | 0 | 0 | 0 | 4/1 | 42.3 |
| b3_combo | night | 4/5 | 0/1 | 1 | 1 | 0 | 0 | 5/0 | 42.1 |
| b3_combo | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 41.9 |
| b3_combo | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 2 | 0/7 | 42.1 |
| b3_combo | day_holdout_1245 | 2/2 | 3/3 | 0 | 0 | 0 | 0 | 2/3 | 41.3 |
| b4_combo_static5 | night | 4/5 | 0/1 | 1 | 1 | 0 | 0 | 5/0 | 42.9 |
| b4_combo_static5 | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 42.0 |
| b4_combo_static5 | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 0 | 0/5 | 41.8 |
| b4_combo_static5 | day_holdout_1245 | 2/2 | 3/3 | 0 | 0 | 0 | 0 | 2/3 | 41.3 |

## Detail

### exp0_base - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | DETECTED BUT NOT COUNTED | #1 cyclist 0.6s counted=0 det=cyclist (100.0% cyc) |
| n2 | cyclist | 7:02-7:09 | DETECTED BUT NOT COUNTED | #2 cyclist 0.43s counted=0 det=cyclist (100.0% cyc) |
| n3 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #4 cyclist 0.9s counted=0 det=cyclist (59.3% cyc) |
| n4 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #6 unscored 0.03s counted=0 det=cyclist (100.0% cyc) |
| n5 | cyclist | 14:21-14:26 | MISSED |  |
| n6 | pedestrian | 14:47-14:58 | MISSED |  |

### exp0_base - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #3 pedestrian 3.2s counted=1 det=person (0.0% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #5 cyclist 4.04s counted=1 det=person (34.7% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #8 pedestrian 16.85s counted=1 det=person (0.2% cyc) |
| d4 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #12 pedestrian 2.07s counted=0 det=person (0.0% cyc) |
| d5 | pedestrian | 12:10-12:37 | DETECTED BUT NOT COUNTED | #13 pedestrian 1.2s counted=0 det=person (0.0% cyc) |

### b2_2_sahi - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | FOUND | #18 pedestrian 10.48s counted=1 det=person (24.5% cyc) |
| p2 | pedestrian | 10:00-10:14 | FOUND | #27 pedestrian 18.72s counted=1 det=person (31.6% cyc) |
| p3 | pedestrian | 10:59-11:18 | FOUND | #33 pedestrian 14.98s counted=1 det=person (43.4% cyc) |
| p4 | pedestrian | 10:59-11:18 | FOUND | #36 pedestrian 5.84s counted=1 det=person (28.0% cyc) |
| p5 | pedestrian | 10:59-11:18 | FOUND | #40 pedestrian 3.84s counted=1 det=cyclist (76.5% cyc) |
| EXTRA | counted pedestrian | 7:50-8:27 | no truth row | #24 4.97s det=person |
| EXTRA | counted pedestrian | 8:32-9:00 | no truth row | #26 3.8s det=person |

### b2_2_sahi - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | WRONG CLASS | #1 cyclist 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | WRONG CLASS | #15 cyclist 23.62s counted=1 det=person (8.1% cyc) |

### b3_combo - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | FOUND | #4 cyclist 1.2s counted=1 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | FOUND | #22 cyclist 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### b3_combo - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b3_combo - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | FOUND | #18 pedestrian 10.48s counted=1 det=person (24.5% cyc) |
| p2 | pedestrian | 10:00-10:14 | FOUND | #27 pedestrian 18.72s counted=1 det=person (31.6% cyc) |
| p3 | pedestrian | 10:59-11:18 | FOUND | #33 pedestrian 14.98s counted=1 det=person (43.4% cyc) |
| p4 | pedestrian | 10:59-11:18 | FOUND | #36 pedestrian 5.84s counted=1 det=person (28.0% cyc) |
| p5 | pedestrian | 10:59-11:18 | FOUND | #40 pedestrian 3.84s counted=1 det=cyclist (76.5% cyc) |
| EXTRA | counted pedestrian | 7:50-8:27 | no truth row | #24 4.97s det=person |
| EXTRA | counted pedestrian | 8:32-9:00 | no truth row | #26 3.8s det=person |

### b3_combo - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | FOUND | #1 pedestrian 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | FOUND | #15 pedestrian 23.62s counted=1 det=person (8.1% cyc) |

### b4_combo_static5 - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | FOUND | #4 cyclist 1.2s counted=1 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | FOUND | #22 cyclist 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### b4_combo_static5 - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b4_combo_static5 - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | FOUND | #18 pedestrian 10.48s counted=1 det=person (24.5% cyc) |
| p2 | pedestrian | 10:00-10:14 | FOUND | #27 pedestrian 18.72s counted=1 det=person (31.6% cyc) |
| p3 | pedestrian | 10:59-11:18 | FOUND | #33 pedestrian 14.98s counted=1 det=person (43.4% cyc) |
| p4 | pedestrian | 10:59-11:18 | FOUND | #36 pedestrian 5.84s counted=1 det=person (28.0% cyc) |
| p5 | pedestrian | 10:59-11:18 | FOUND | #40 pedestrian 3.84s counted=1 det=cyclist (76.5% cyc) |

### b4_combo_static5 - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | FOUND | #1 pedestrian 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | FOUND | #15 pedestrian 23.62s counted=1 det=person (8.1% cyc) |

## Motion-diagnostic candidates (baseline run) overlapping truth rows

**night**: 447 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth n1 (motorcycle 4:02): cand 138 (2.97s, box h 22.5), cand 139 (3.0s, box h 16.9), cand 140 (1.43s, box h 21.2)
- truth n2 (cyclist 7:02): cand 203 (4.54s, box h 22.8), cand 205 (3.0s, box h 41.4), cand 207 (3.5s, box h 26.3), cand 209 (1.1s, box h 20.8), cand 210 (1.2s, box h 41.2), cand 211 (0.9s, box h 36.7), cand 212 (2.67s, box h 52.2), cand 213 (1.7s, box h 31.8), cand 214 (1.3s, box h 50.0), cand 215 (1.5s, box h 16.6), cand 216 (1.43s, box h 23.7), cand 217 (1.4s, box h 90.6), cand 218 (1.94s, box h 86.1), cand 219 (4.9s, box h 49.8), cand 220 (1.74s, box h 94.6)
- truth n3 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n4 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n5 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n6 (pedestrian 14:47): cand 445 (1.3s, box h 15.0), cand 446 (7.61s, box h 31.4), cand 447 (10.78s, box h 91.9)

**day**: 185 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth d2 (pedestrian 3:00): cand 30 (2.57s, box h 19.2), cand 33 (12.18s, box h 71.5), cand 34 (0.87s, box h 84.7), cand 35 (1.13s, box h 19.8), cand 36 (1.13s, box h 40.9), cand 37 (1.07s, box h 34.5), cand 38 (1.97s, box h 61.7), cand 39 (1.17s, box h 43.4)
- truth d1 (cyclist 9:10): cand 108 (1.47s, box h 45.3), cand 109 (1.47s, box h 104.7), cand 110 (1.6s, box h 36.9), cand 111 (1.13s, box h 92.3), cand 112 (3.07s, box h 34.6)
- truth d3 (pedestrian 11:45): cand 142 (8.94s, box h 100.1), cand 144 (0.87s, box h 24.9), cand 145 (3.74s, box h 64.9), cand 146 (1.87s, box h 35.8), cand 147 (3.74s, box h 30.7), cand 148 (1.27s, box h 46.4), cand 149 (1.9s, box h 34.1), cand 150 (1.17s, box h 26.5), cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1)
- truth d4 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)
- truth d5 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)


<a id="report-eval-batch5-codex-20261019"></a>
## EVAL_batch5_codex_20261019.md
Original location: `vision3/best/test_colonial/exp_results/EVAL_batch5_codex_20261019.md`.

# Experiment evaluation  (2026-10-19 11:47)

root: /Users/rithika/Desktop/objectDetect/vision3/best/test_colonial
runs: b4_combo_static5, b5_nospeed, b5_noveto, b5_bright_gamma, b5_bright_clahe

- truth night: 6 usable rows (5 cyclist incl. motorcycle, 1 pedestrian); skipped 0: none
- truth day: 5 usable rows (1 cyclist incl. motorcycle, 4 pedestrian); skipped 0: none
- truth night_holdout_2200: 5 usable rows (0 cyclist incl. motorcycle, 5 pedestrian); skipped 0: none
- truth day_holdout_1245: 5 usable rows (2 cyclist incl. motorcycle, 3 pedestrian); skipped 0: none

## Summary (person level; FOUND = counted with the right class; motorcycle scored as cyclist)

| run | clip | cyclists found | pedestrians found | wrong class | detected, not counted | missed | extra counted | counted bic/ped | runtime min |
|---|---|---|---|---|---|---|---|---|---|
| b4_combo_static5 | night | 4/5 | 0/1 | 1 | 1 | 0 | 0 | 5/0 | 42.9 |
| b4_combo_static5 | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 42.0 |
| b4_combo_static5 | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 0 | 0/5 | 41.8 |
| b4_combo_static5 | day_holdout_1245 | 2/2 | 3/3 | 0 | 0 | 0 | 0 | 2/3 | 41.3 |
| b5_nospeed | night | 3/5 | 0/1 | 2 | 1 | 0 | 0 | 4/1 | 42.0 |
| b5_nospeed | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 41.5 |
| b5_nospeed | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 0 | 0/5 | 42.0 |
| b5_nospeed | day_holdout_1245 | 2/2 | 2/3 | 1 | 0 | 0 | 0 | 3/2 | 41.5 |
| b5_noveto | night | 4/5 | 0/1 | 1 | 1 | 0 | 0 | 5/0 | 41.8 |
| b5_noveto | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 42.7 |
| b5_noveto | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 0 | 0/5 | 42.1 |
| b5_noveto | day_holdout_1245 | 2/2 | 2/3 | 1 | 0 | 0 | 0 | 3/2 | 40.7 |
| b5_bright_gamma | night | 3/5 | 0/1 | 1 | 2 | 0 | 0 | 4/0 | 42.7 |
| b5_bright_gamma | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 0 | 0/5 | 42.4 |
| b5_bright_clahe | night | 1/5 | 0/1 | 2 | 3 | 0 | 0 | 2/1 | 44.7 |
| b5_bright_clahe | night_holdout_2200 | 0/0 | 4/5 | 0 | 1 | 0 | 0 | 0/4 | 43.2 |

## Detail

### b4_combo_static5 - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | FOUND | #4 cyclist 1.2s counted=1 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | FOUND | #22 cyclist 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### b4_combo_static5 - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b4_combo_static5 - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | FOUND | #18 pedestrian 10.48s counted=1 det=person (24.5% cyc) |
| p2 | pedestrian | 10:00-10:14 | FOUND | #27 pedestrian 18.72s counted=1 det=person (31.6% cyc) |
| p3 | pedestrian | 10:59-11:18 | FOUND | #33 pedestrian 14.98s counted=1 det=person (43.4% cyc) |
| p4 | pedestrian | 10:59-11:18 | FOUND | #36 pedestrian 5.84s counted=1 det=person (28.0% cyc) |
| p5 | pedestrian | 10:59-11:18 | FOUND | #40 pedestrian 3.84s counted=1 det=cyclist (76.5% cyc) |

### b4_combo_static5 - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | FOUND | #1 pedestrian 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | FOUND | #15 pedestrian 23.62s counted=1 det=person (8.1% cyc) |

### b5_nospeed - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | FOUND | #4 cyclist 1.2s counted=1 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | WRONG CLASS | #22 pedestrian 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### b5_nospeed - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b5_nospeed - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | FOUND | #18 pedestrian 10.48s counted=1 det=person (24.5% cyc) |
| p2 | pedestrian | 10:00-10:14 | FOUND | #27 pedestrian 18.72s counted=1 det=person (31.6% cyc) |
| p3 | pedestrian | 10:59-11:18 | FOUND | #33 pedestrian 14.98s counted=1 det=person (43.4% cyc) |
| p4 | pedestrian | 10:59-11:18 | FOUND | #36 pedestrian 5.84s counted=1 det=person (28.0% cyc) |
| p5 | pedestrian | 10:59-11:18 | FOUND | #40 pedestrian 3.84s counted=1 det=cyclist (76.5% cyc) |

### b5_nospeed - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | WRONG CLASS | #1 cyclist 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | FOUND | #15 pedestrian 23.62s counted=1 det=person (8.1% cyc) |

### b5_noveto - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | FOUND | #4 cyclist 1.2s counted=1 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | FOUND | #22 cyclist 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |

### b5_noveto - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | FOUND | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | FOUND | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | FOUND | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | FOUND | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | FOUND | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |

### b5_noveto - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | FOUND | #18 pedestrian 10.48s counted=1 det=person (24.5% cyc) |
| p2 | pedestrian | 10:00-10:14 | FOUND | #27 pedestrian 18.72s counted=1 det=person (31.6% cyc) |
| p3 | pedestrian | 10:59-11:18 | FOUND | #33 pedestrian 14.98s counted=1 det=person (43.4% cyc) |
| p4 | pedestrian | 10:59-11:18 | FOUND | #36 pedestrian 5.84s counted=1 det=person (28.0% cyc) |
| p5 | pedestrian | 10:59-11:18 | FOUND | #40 pedestrian 3.84s counted=1 det=cyclist (76.5% cyc) |

### b5_noveto - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | FOUND | #1 pedestrian 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | FOUND | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | FOUND | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | FOUND | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | WRONG CLASS | #15 cyclist 23.62s counted=1 det=person (8.1% cyc) |

### b5_bright_gamma - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | FOUND | #11 cyclist 1.07s counted=1 det=cyclist (96.9% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #19 cyclist 5.34s counted=1 det=cyclist (91.9% cyc) |
| n3 | cyclist | 14:21-14:26 | FOUND | #34 cyclist 3.57s counted=1 det=cyclist (50.5% cyc) |
| n4 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #37 cyclist 2.14s counted=0 det=person (26.6% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #38 cyclist 2.97s counted=0 det=cyclist (50.6% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #40 cyclist 10.01s counted=1 det=cyclist (74.0% cyc) |

### b5_bright_gamma - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | FOUND | #19 pedestrian 11.34s counted=1 det=person (20.9% cyc) |
| p2 | pedestrian | 10:00-10:14 | FOUND | #29 pedestrian 37.5s counted=1 det=person (15.5% cyc) |
| p3 | pedestrian | 10:59-11:18 | FOUND | #31 pedestrian 18.69s counted=1 det=person (36.8% cyc) |
| p4 | pedestrian | 10:59-11:18 | FOUND | #35 pedestrian 5.51s counted=1 det=person (8.5% cyc) |
| p5 | pedestrian | 10:59-11:18 | FOUND | #41 pedestrian 3.5s counted=1 det=cyclist (57.1% cyc) |

### b5_bright_clahe - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | DETECTED BUT NOT COUNTED | #23 cyclist 2.4s counted=0 det=person (44.4% cyc) |
| n2 | cyclist | 7:02-7:09 | FOUND | #41 cyclist 5.54s counted=1 det=cyclist (90.4% cyc) |
| n3 | cyclist | 14:21-14:26 | WRONG CLASS | #81 pedestrian 3.6s counted=1 det=person (48.1% cyc) |
| n4 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #82 pedestrian 1.8s counted=0 det=person (25.9% cyc) |
| n5 | cyclist | 14:21-14:26 | DETECTED BUT NOT COUNTED | #85 pedestrian 2.57s counted=0 det=person (49.4% cyc) |
| n6 | pedestrian | 14:47-14:58 | WRONG CLASS | #88 cyclist 7.21s counted=1 det=cyclist (69.0% cyc) |

### b5_bright_clahe - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | FOUND | #34 pedestrian 11.54s counted=1 det=person (16.5% cyc) |
| p2 | pedestrian | 10:00-10:14 | FOUND | #55 pedestrian 32.63s counted=1 det=person (12.3% cyc) |
| p3 | pedestrian | 10:59-11:18 | FOUND | #72 pedestrian 15.52s counted=1 det=person (24.9% cyc) |
| p4 | pedestrian | 10:59-11:18 | FOUND | #82 pedestrian 6.91s counted=1 det=person (31.4% cyc) |
| p5 | pedestrian | 10:59-11:18 | DETECTED BUT NOT COUNTED | #89 pedestrian 1.74s counted=0 det=person (26.9% cyc) |

## Motion-diagnostic candidates (baseline run) overlapping truth rows

**night**: 447 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth n1 (motorcycle 4:02): cand 138 (2.97s, box h 22.5), cand 139 (3.0s, box h 16.9), cand 140 (1.43s, box h 21.2)
- truth n2 (cyclist 7:02): cand 203 (4.54s, box h 22.8), cand 205 (3.0s, box h 41.4), cand 207 (3.5s, box h 26.3), cand 209 (1.1s, box h 20.8), cand 210 (1.2s, box h 41.2), cand 211 (0.9s, box h 36.7), cand 212 (2.67s, box h 52.2), cand 213 (1.7s, box h 31.8), cand 214 (1.3s, box h 50.0), cand 215 (1.5s, box h 16.6), cand 216 (1.43s, box h 23.7), cand 217 (1.4s, box h 90.6), cand 218 (1.94s, box h 86.1), cand 219 (4.9s, box h 49.8), cand 220 (1.74s, box h 94.6)
- truth n3 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n4 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n5 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n6 (pedestrian 14:47): cand 445 (1.3s, box h 15.0), cand 446 (7.61s, box h 31.4), cand 447 (10.78s, box h 91.9)

**day**: 185 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth d2 (pedestrian 3:00): cand 30 (2.57s, box h 19.2), cand 33 (12.18s, box h 71.5), cand 34 (0.87s, box h 84.7), cand 35 (1.13s, box h 19.8), cand 36 (1.13s, box h 40.9), cand 37 (1.07s, box h 34.5), cand 38 (1.97s, box h 61.7), cand 39 (1.17s, box h 43.4)
- truth d1 (cyclist 9:10): cand 108 (1.47s, box h 45.3), cand 109 (1.47s, box h 104.7), cand 110 (1.6s, box h 36.9), cand 111 (1.13s, box h 92.3), cand 112 (3.07s, box h 34.6)
- truth d3 (pedestrian 11:45): cand 142 (8.94s, box h 100.1), cand 144 (0.87s, box h 24.9), cand 145 (3.74s, box h 64.9), cand 146 (1.87s, box h 35.8), cand 147 (3.74s, box h 30.7), cand 148 (1.27s, box h 46.4), cand 149 (1.9s, box h 34.1), cand 150 (1.17s, box h 26.5), cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1)
- truth d4 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)
- truth d5 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)


written: /Users/rithika/Desktop/objectDetect/vision3/best/test_colonial/exp_results/EVAL_20261019_1147.md


<a id="report-fusion-probe-20261008-1612"></a>
## FUSION_PROBE_20261008_1612.md
Original location: `vision3/best/test_colonial/exp_results/FUSION_PROBE_20261008_1612.md`.

# Fusion probe

runs: exp0_base,exp1_sahi,exp3a_speed

| run | clip | truth | when | track | secs | X-CLIP | wBIC | det %cyc | speed h/s | direction | counted |
|---|---|---|---|---|---|---|---|---|---|---|---|
| exp0_base | night | n1 cyclist | 4:02 | #1 | 0.6 | bicyclist | 0.95 | 100 | 2.64 | moving_right | 0 |
| exp0_base | night | n2 cyclist | 7:02 | #2 | 0.43 | bicyclist | 0.99 | 100 | 0.79 | moving_right | 0 |
| exp0_base | night | n3 cyclist | 14:21 | #4 | 0.9 | bicyclist | 0.70 | 59 | 1.30 | toward_camera | 0 |
| exp0_base | day | d2 pedestrian | 3:00 | #3 | 3.2 | pedestrian | 0.21 | 0 | 0.15 | static | 1 |
| exp0_base | day | d1 cyclist | 9:10 | #5 | 4.04 | bicyclist | 0.92 | 35 | 0.97 | moving_left | 1 |
| exp0_base | day | d3 pedestrian | 11:45 | #8 | 16.85 | pedestrian | 0.40 | 0 | 0.24 | away_from_camera | 1 |
| exp0_base | day | d4 pedestrian | 12:10 | #12 | 2.07 | pedestrian | 0.16 | 0 | 0.18 | static | 0 |
| exp0_base | day | d5 pedestrian | 12:10 | #13 | 1.2 | pedestrian | 0.22 | 0 | 0.18 | static | 0 |
| exp1_sahi | night | n1 cyclist | 4:02 | #4 | 1.2 | bicyclist | 0.97 | 94 | 4.82 | moving_right | 0 |
| exp1_sahi | night | n2 cyclist | 7:02 | #12 | 5.24 | bicyclist | 0.91 | 88 | 0.87 | moving_right | 1 |
| exp1_sahi | night | n3 cyclist | 14:21 | #18 | 3.47 | bicyclist | 0.62 | 49 | 1.23 | moving_right | 1 |
| exp1_sahi | night | n4 cyclist | 14:21 | #22 | 3.44 | pedestrian | 0.30 | 59 | 2.23 | moving_right | 1 |
| exp1_sahi | night | n5 cyclist | 14:21 | #21 | 2.37 | pedestrian | 0.39 | 31 | 2.37 | moving_right | 0 |
| exp1_sahi | night | n6 pedestrian | 14:47 | #23 | 10.58 | bicyclist | 0.67 | 69 | 0.48 | moving_right | 1 |
| exp1_sahi | day | d2 pedestrian | 3:00 | #2 | 20.69 | bicyclist | 0.73 | 6 | 0.56 | moving_left | 1 |
| exp1_sahi | day | d1 cyclist | 9:10 | #10 | 6.74 | bicyclist | 0.91 | 54 | 1.51 | moving_left | 1 |
| exp1_sahi | day | d3 pedestrian | 11:45 | #13 | 36.57 | bicyclist | 0.53 | 2 | 0.39 | moving_left | 1 |
| exp1_sahi | day | d4 pedestrian | 12:10 | #15 | 21.96 | pedestrian | 0.24 | 6 | 0.78 | moving_left | 1 |
| exp1_sahi | day | d5 pedestrian | 12:10 | #23 | 3.47 | pedestrian | 0.22 | 0 | 0.16 | static | 1 |
| exp3a_speed | night | n1 cyclist | 4:02 | #1 | 0.6 | bicyclist | 0.95 | 100 | 2.64 | moving_right | 0 |
| exp3a_speed | night | n2 cyclist | 7:02 | #2 | 0.43 | bicyclist | 0.99 | 100 | 0.79 | moving_right | 0 |
| exp3a_speed | night | n3 cyclist | 14:21 | #4 | 0.9 | bicyclist | 0.70 | 59 | 1.30 | toward_camera | 0 |
| exp3a_speed | day | d2 pedestrian | 3:00 | #3 | 3.2 | pedestrian | 0.21 | 0 | 0.15 | static | 1 |
| exp3a_speed | day | d1 cyclist | 9:10 | #5 | 4.04 | bicyclist | 0.92 | 35 | 0.97 | moving_left | 1 |
| exp3a_speed | day | d3 pedestrian | 11:45 | #8 | 16.85 | pedestrian | 0.40 | 0 | 0.24 | away_from_camera | 1 |
| exp3a_speed | day | d4 pedestrian | 12:10 | #12 | 2.07 | pedestrian | 0.16 | 0 | 0.18 | static | 0 |
| exp3a_speed | day | d5 pedestrian | 12:10 | #13 | 1.2 | pedestrian | 0.22 | 0 | 0.18 | static | 0 |

## Rules replayed on 27 (person, run) pairs

| rule | right | of | labels it changes |
|---|---|---|---|
| X-CLIP alone (now) | 22 | 27 | |
| veto 5% | 23 | 27 | exp1_sahi/day/d3(ok) |
| veto 10% | 24 | 27 | exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok) |
| veto 15% | 24 | 27 | exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok) |
| veto 20% | 24 | 27 | exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok) |
| veto 30% | 24 | 27 | exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok) |
| veto 40% | 22 | 27 | exp0_base/day/d1(WRONG), exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok), exp3a_speed/day/d1(WRONG) |
| veto 50% | 21 | 27 | exp0_base/day/d1(WRONG), exp1_sahi/night/n3(WRONG), exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok), exp3a_speed/day/d1(WRONG) |
| promote 80% | 22 | 27 | - |
| promote 90% | 22 | 27 | - |
| promote 95% | 22 | 27 | - |
| speed lateral walk<0.8 ride>2.0 | 25 | 27 | exp1_sahi/night/n4(ok), exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok) |
| speed lateral walk<1.0 ride>2.0 | 23 | 27 | exp0_base/day/d1(WRONG), exp1_sahi/night/n4(ok), exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok), exp3a_speed/day/d1(WRONG) |
| speed lateral walk<1.2 ride>2.5 | 22 | 27 | exp0_base/day/d1(WRONG), exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok), exp3a_speed/day/d1(WRONG) |
| speed lateral walk<1.5 ride>3.0 | 21 | 27 | exp0_base/day/d1(WRONG), exp1_sahi/night/n3(WRONG), exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok), exp3a_speed/day/d1(WRONG) |

Read the per-row table first: do real riders and real walkers separate on speed (lateral tracks) or on det %cyc? A rule that only 'wins' by changing one or two rows is a coincidence.

<a id="report-fusion-probe-20261009-0042"></a>
## FUSION_PROBE_20261009_0042.md
Original location: `vision3/best/test_colonial/exp_results/FUSION_PROBE_20261009_0042.md`.

# Fusion probe

runs: exp0_base,exp1_sahi,b2_3_sahi_fuse,b2_5_sahi_speed

| run | clip | truth | when | track | secs | X-CLIP | wBIC | det %cyc | speed h/s | direction | counted |
|---|---|---|---|---|---|---|---|---|---|---|---|
| exp0_base | night | n1 cyclist | 4:02 | #1 | 0.6 | bicyclist | 0.95 | 100 | 2.64 | moving_right | 0 |
| exp0_base | night | n2 cyclist | 7:02 | #2 | 0.43 | bicyclist | 0.99 | 100 | 0.79 | moving_right | 0 |
| exp0_base | night | n3 cyclist | 14:21 | #4 | 0.9 | bicyclist | 0.70 | 59 | 1.30 | toward_camera | 0 |
| exp0_base | day | d2 pedestrian | 3:00 | #3 | 3.2 | pedestrian | 0.21 | 0 | 0.15 | static | 1 |
| exp0_base | day | d1 cyclist | 9:10 | #5 | 4.04 | bicyclist | 0.92 | 35 | 0.97 | moving_left | 1 |
| exp0_base | day | d3 pedestrian | 11:45 | #8 | 16.85 | pedestrian | 0.40 | 0 | 0.24 | away_from_camera | 1 |
| exp0_base | day | d4 pedestrian | 12:10 | #12 | 2.07 | pedestrian | 0.16 | 0 | 0.18 | static | 0 |
| exp0_base | day | d5 pedestrian | 12:10 | #13 | 1.2 | pedestrian | 0.22 | 0 | 0.18 | static | 0 |
| exp1_sahi | night | n1 cyclist | 4:02 | #4 | 1.2 | bicyclist | 0.97 | 94 | 4.82 | moving_right | 0 |
| exp1_sahi | night | n2 cyclist | 7:02 | #12 | 5.24 | bicyclist | 0.91 | 88 | 0.87 | moving_right | 1 |
| exp1_sahi | night | n3 cyclist | 14:21 | #18 | 3.47 | bicyclist | 0.62 | 49 | 1.23 | moving_right | 1 |
| exp1_sahi | night | n4 cyclist | 14:21 | #22 | 3.44 | pedestrian | 0.30 | 59 | 2.23 | moving_right | 1 |
| exp1_sahi | night | n5 cyclist | 14:21 | #21 | 2.37 | pedestrian | 0.39 | 31 | 2.37 | moving_right | 0 |
| exp1_sahi | night | n6 pedestrian | 14:47 | #23 | 10.58 | bicyclist | 0.67 | 69 | 0.48 | moving_right | 1 |
| exp1_sahi | day | d2 pedestrian | 3:00 | #2 | 20.69 | bicyclist | 0.73 | 6 | 0.56 | moving_left | 1 |
| exp1_sahi | day | d1 cyclist | 9:10 | #10 | 6.74 | bicyclist | 0.91 | 54 | 1.51 | moving_left | 1 |
| exp1_sahi | day | d3 pedestrian | 11:45 | #13 | 36.57 | bicyclist | 0.53 | 2 | 0.39 | moving_left | 1 |
| exp1_sahi | day | d4 pedestrian | 12:10 | #15 | 21.96 | pedestrian | 0.24 | 6 | 0.78 | moving_left | 1 |
| exp1_sahi | day | d5 pedestrian | 12:10 | #23 | 3.47 | pedestrian | 0.22 | 0 | 0.16 | static | 1 |
| b2_3_sahi_fuse | night | n1 cyclist | 4:02 | #4 | 1.2 | bicyclist | 0.97 | 94 | 4.82 | moving_right | 0 |
| b2_3_sahi_fuse | night | n2 cyclist | 7:02 | #12 | 5.24 | bicyclist | 0.91 | 88 | 0.87 | moving_right | 1 |
| b2_3_sahi_fuse | night | n3 cyclist | 14:21 | #18 | 3.47 | bicyclist | 0.62 | 49 | 1.23 | moving_right | 1 |
| b2_3_sahi_fuse | night | n4 cyclist | 14:21 | #22 | 3.44 | pedestrian | 0.30 | 59 | 2.23 | moving_right | 1 |
| b2_3_sahi_fuse | night | n5 cyclist | 14:21 | #21 | 2.37 | pedestrian | 0.39 | 31 | 2.37 | moving_right | 0 |
| b2_3_sahi_fuse | night | n6 pedestrian | 14:47 | #23 | 10.58 | bicyclist | 0.67 | 69 | 0.48 | moving_right | 1 |
| b2_3_sahi_fuse | day | d2 pedestrian | 3:00 | #2 | 20.69 | bicyclist | 0.73 | 6 | 0.56 | moving_left | 1 |
| b2_3_sahi_fuse | day | d1 cyclist | 9:10 | #10 | 6.74 | bicyclist | 0.91 | 54 | 1.51 | moving_left | 1 |
| b2_3_sahi_fuse | day | d3 pedestrian | 11:45 | #13 | 36.57 | bicyclist | 0.53 | 2 | 0.39 | moving_left | 1 |
| b2_3_sahi_fuse | day | d4 pedestrian | 12:10 | #15 | 21.96 | pedestrian | 0.24 | 6 | 0.78 | moving_left | 1 |
| b2_3_sahi_fuse | day | d5 pedestrian | 12:10 | #23 | 3.47 | pedestrian | 0.22 | 0 | 0.16 | static | 1 |
| b2_5_sahi_speed | night | n1 cyclist | 4:02 | #4 | 1.2 | bicyclist | 0.97 | 94 | 4.82 | moving_right | 0 |
| b2_5_sahi_speed | night | n2 cyclist | 7:02 | #12 | 5.24 | bicyclist | 0.91 | 88 | 0.87 | moving_right | 1 |
| b2_5_sahi_speed | night | n3 cyclist | 14:21 | #18 | 3.47 | bicyclist | 0.62 | 49 | 1.23 | moving_right | 1 |
| b2_5_sahi_speed | night | n4 cyclist | 14:21 | #22 | 3.44 | pedestrian | 0.30 | 59 | 2.23 | moving_right | 1 |
| b2_5_sahi_speed | night | n5 cyclist | 14:21 | #21 | 2.37 | pedestrian | 0.39 | 31 | 2.37 | moving_right | 0 |
| b2_5_sahi_speed | night | n6 pedestrian | 14:47 | #23 | 10.58 | bicyclist | 0.67 | 69 | 0.48 | moving_right | 1 |
| b2_5_sahi_speed | day | d2 pedestrian | 3:00 | #2 | 20.69 | bicyclist | 0.73 | 6 | 0.56 | moving_left | 1 |
| b2_5_sahi_speed | day | d1 cyclist | 9:10 | #10 | 6.74 | bicyclist | 0.91 | 54 | 1.51 | moving_left | 1 |
| b2_5_sahi_speed | day | d3 pedestrian | 11:45 | #13 | 36.57 | bicyclist | 0.53 | 2 | 0.39 | moving_left | 1 |
| b2_5_sahi_speed | day | d4 pedestrian | 12:10 | #15 | 21.96 | pedestrian | 0.24 | 6 | 0.78 | moving_left | 1 |
| b2_5_sahi_speed | day | d5 pedestrian | 12:10 | #23 | 3.47 | pedestrian | 0.22 | 0 | 0.16 | static | 1 |

## Rules replayed on 41 (person, run) pairs

| rule | right | of | labels it changes |
|---|---|---|---|
| X-CLIP alone (now) | 26 | 41 | |
| veto 5% | 29 | 41 | exp1_sahi/day/d3(ok), b2_3_sahi_fuse/day/d3(ok), b2_5_sahi_speed/day/d3(ok) |
| veto 10% | 32 | 41 | exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok) |
| veto 15% | 32 | 41 | exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok) |
| veto 20% | 32 | 41 | exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok) |
| veto 30% | 32 | 41 | exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok) |
| veto 40% | 31 | 41 | exp0_base/day/d1(WRONG), exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok) |
| veto 50% | 28 | 41 | exp0_base/day/d1(WRONG), exp1_sahi/night/n3(WRONG), exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok), b2_3_sahi_fuse/night/n3(WRONG), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_5_sahi_speed/night/n3(WRONG), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok) |
| promote 80% | 26 | 41 | - |
| promote 90% | 26 | 41 | - |
| promote 95% | 26 | 41 | - |
| speed lateral walk<0.8 ride>2.0 | 35 | 41 | exp1_sahi/night/n4(ok), exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok), b2_3_sahi_fuse/night/n4(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_5_sahi_speed/night/n4(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok) |
| speed lateral walk<1.0 ride>2.0 | 34 | 41 | exp0_base/day/d1(WRONG), exp1_sahi/night/n4(ok), exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok), b2_3_sahi_fuse/night/n4(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_5_sahi_speed/night/n4(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok) |
| speed lateral walk<1.2 ride>2.5 | 31 | 41 | exp0_base/day/d1(WRONG), exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok) |
| speed lateral walk<1.5 ride>3.0 | 28 | 41 | exp0_base/day/d1(WRONG), exp1_sahi/night/n3(WRONG), exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok), b2_3_sahi_fuse/night/n3(WRONG), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_5_sahi_speed/night/n3(WRONG), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok) |

Read the per-row table first: do real riders and real walkers separate on speed (lateral tracks) or on det %cyc? A rule that only 'wins' by changing one or two rows is a coincidence.

<a id="report-fusion-probe-20261009-0047"></a>
## FUSION_PROBE_20261009_0047.md
Original location: `vision3/best/test_colonial/exp_results/FUSION_PROBE_20261009_0047.md`.

# Fusion probe

runs: exp0_base,b2_0_base,b2_2_sahi,b2_3_sahi_fuse,b2_5_sahi_speed

| run | clip | truth | when | track | secs | X-CLIP | wBIC | det %cyc | speed h/s | direction | counted |
|---|---|---|---|---|---|---|---|---|---|---|---|
| exp0_base | night | n1 cyclist | 4:02 | #1 | 0.6 | bicyclist | 0.95 | 100 | 2.64 | moving_right | 0 |
| exp0_base | night | n2 cyclist | 7:02 | #2 | 0.43 | bicyclist | 0.99 | 100 | 0.79 | moving_right | 0 |
| exp0_base | night | n3 cyclist | 14:21 | #4 | 0.9 | bicyclist | 0.70 | 59 | 1.30 | toward_camera | 0 |
| exp0_base | day | d2 pedestrian | 3:00 | #3 | 3.2 | pedestrian | 0.21 | 0 | 0.15 | static | 1 |
| exp0_base | day | d1 cyclist | 9:10 | #5 | 4.04 | bicyclist | 0.92 | 35 | 0.97 | moving_left | 1 |
| exp0_base | day | d3 pedestrian | 11:45 | #8 | 16.85 | pedestrian | 0.40 | 0 | 0.24 | away_from_camera | 1 |
| exp0_base | day | d4 pedestrian | 12:10 | #12 | 2.07 | pedestrian | 0.16 | 0 | 0.18 | static | 0 |
| exp0_base | day | d5 pedestrian | 12:10 | #13 | 1.2 | pedestrian | 0.22 | 0 | 0.18 | static | 0 |
| b2_3_sahi_fuse | night | n1 cyclist | 4:02 | #4 | 1.2 | bicyclist | 0.97 | 94 | 4.82 | moving_right | 0 |
| b2_3_sahi_fuse | night | n2 cyclist | 7:02 | #12 | 5.24 | bicyclist | 0.91 | 88 | 0.87 | moving_right | 1 |
| b2_3_sahi_fuse | night | n3 cyclist | 14:21 | #18 | 3.47 | bicyclist | 0.62 | 49 | 1.23 | moving_right | 1 |
| b2_3_sahi_fuse | night | n4 cyclist | 14:21 | #22 | 3.44 | pedestrian | 0.30 | 59 | 2.23 | moving_right | 1 |
| b2_3_sahi_fuse | night | n5 cyclist | 14:21 | #21 | 2.37 | pedestrian | 0.39 | 31 | 2.37 | moving_right | 0 |
| b2_3_sahi_fuse | night | n6 pedestrian | 14:47 | #23 | 10.58 | bicyclist | 0.67 | 69 | 0.48 | moving_right | 1 |
| b2_3_sahi_fuse | day | d2 pedestrian | 3:00 | #2 | 20.69 | bicyclist | 0.73 | 6 | 0.56 | moving_left | 1 |
| b2_3_sahi_fuse | day | d1 cyclist | 9:10 | #10 | 6.74 | bicyclist | 0.91 | 54 | 1.51 | moving_left | 1 |
| b2_3_sahi_fuse | day | d3 pedestrian | 11:45 | #13 | 36.57 | bicyclist | 0.53 | 2 | 0.39 | moving_left | 1 |
| b2_3_sahi_fuse | day | d4 pedestrian | 12:10 | #15 | 21.96 | pedestrian | 0.24 | 6 | 0.78 | moving_left | 1 |
| b2_3_sahi_fuse | day | d5 pedestrian | 12:10 | #23 | 3.47 | pedestrian | 0.22 | 0 | 0.16 | static | 1 |
| b2_5_sahi_speed | night | n1 cyclist | 4:02 | #4 | 1.2 | bicyclist | 0.97 | 94 | 4.82 | moving_right | 0 |
| b2_5_sahi_speed | night | n2 cyclist | 7:02 | #12 | 5.24 | bicyclist | 0.91 | 88 | 0.87 | moving_right | 1 |
| b2_5_sahi_speed | night | n3 cyclist | 14:21 | #18 | 3.47 | bicyclist | 0.62 | 49 | 1.23 | moving_right | 1 |
| b2_5_sahi_speed | night | n4 cyclist | 14:21 | #22 | 3.44 | pedestrian | 0.30 | 59 | 2.23 | moving_right | 1 |
| b2_5_sahi_speed | night | n5 cyclist | 14:21 | #21 | 2.37 | pedestrian | 0.39 | 31 | 2.37 | moving_right | 0 |
| b2_5_sahi_speed | night | n6 pedestrian | 14:47 | #23 | 10.58 | bicyclist | 0.67 | 69 | 0.48 | moving_right | 1 |
| b2_5_sahi_speed | day | d2 pedestrian | 3:00 | #2 | 20.69 | bicyclist | 0.73 | 6 | 0.56 | moving_left | 1 |
| b2_5_sahi_speed | day | d1 cyclist | 9:10 | #10 | 6.74 | bicyclist | 0.91 | 54 | 1.51 | moving_left | 1 |
| b2_5_sahi_speed | day | d3 pedestrian | 11:45 | #13 | 36.57 | bicyclist | 0.53 | 2 | 0.39 | moving_left | 1 |
| b2_5_sahi_speed | day | d4 pedestrian | 12:10 | #15 | 21.96 | pedestrian | 0.24 | 6 | 0.78 | moving_left | 1 |
| b2_5_sahi_speed | day | d5 pedestrian | 12:10 | #23 | 3.47 | pedestrian | 0.22 | 0 | 0.16 | static | 1 |

## Rules replayed on 30 (person, run) pairs

| rule | right | of | labels it changes |
|---|---|---|---|
| X-CLIP alone (now) | 20 | 30 | |
| veto 5% | 22 | 30 | b2_3_sahi_fuse/day/d3(ok), b2_5_sahi_speed/day/d3(ok) |
| veto 10% | 24 | 30 | b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok) |
| veto 15% | 24 | 30 | b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok) |
| veto 20% | 24 | 30 | b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok) |
| veto 30% | 24 | 30 | b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok) |
| veto 40% | 23 | 30 | exp0_base/day/d1(WRONG), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok) |
| veto 50% | 21 | 30 | exp0_base/day/d1(WRONG), b2_3_sahi_fuse/night/n3(WRONG), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_5_sahi_speed/night/n3(WRONG), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok) |
| promote 80% | 20 | 30 | - |
| promote 90% | 20 | 30 | - |
| promote 95% | 20 | 30 | - |
| speed lateral walk<0.8 ride>2.0 | 26 | 30 | b2_3_sahi_fuse/night/n4(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_5_sahi_speed/night/n4(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok) |
| speed lateral walk<1.0 ride>2.0 | 25 | 30 | exp0_base/day/d1(WRONG), b2_3_sahi_fuse/night/n4(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_5_sahi_speed/night/n4(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok) |
| speed lateral walk<1.2 ride>2.5 | 23 | 30 | exp0_base/day/d1(WRONG), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok) |
| speed lateral walk<1.5 ride>3.0 | 21 | 30 | exp0_base/day/d1(WRONG), b2_3_sahi_fuse/night/n3(WRONG), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_5_sahi_speed/night/n3(WRONG), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok) |

Read the per-row table first: do real riders and real walkers separate on speed (lateral tracks) or on det %cyc? A rule that only 'wins' by changing one or two rows is a coincidence.

<a id="report-fusion-probe-20261009-0202"></a>
## FUSION_PROBE_20261009_0202.md
Original location: `vision3/best/test_colonial/exp_results/FUSION_PROBE_20261009_0202.md`.

# Fusion probe

runs: exp0_base,b2_0_base,b2_2_sahi,b2_3_sahi_fuse,b2_5_sahi_speed

| run | clip | truth | when | track | secs | X-CLIP | wBIC | det %cyc | speed h/s | direction | counted |
|---|---|---|---|---|---|---|---|---|---|---|---|
| exp0_base | night | n1 cyclist | 4:02 | #1 | 0.6 | bicyclist | 0.95 | 100 | 2.64 | moving_right | 0 |
| exp0_base | night | n2 cyclist | 7:02 | #2 | 0.43 | bicyclist | 0.99 | 100 | 0.79 | moving_right | 0 |
| exp0_base | night | n3 cyclist | 14:21 | #4 | 0.9 | bicyclist | 0.70 | 59 | 1.30 | toward_camera | 0 |
| exp0_base | day | d2 pedestrian | 3:00 | #3 | 3.2 | pedestrian | 0.21 | 0 | 0.15 | static | 1 |
| exp0_base | day | d1 cyclist | 9:10 | #5 | 4.04 | bicyclist | 0.92 | 35 | 0.97 | moving_left | 1 |
| exp0_base | day | d3 pedestrian | 11:45 | #8 | 16.85 | pedestrian | 0.40 | 0 | 0.24 | away_from_camera | 1 |
| exp0_base | day | d4 pedestrian | 12:10 | #12 | 2.07 | pedestrian | 0.16 | 0 | 0.18 | static | 0 |
| exp0_base | day | d5 pedestrian | 12:10 | #13 | 1.2 | pedestrian | 0.22 | 0 | 0.18 | static | 0 |
| b2_0_base | day_holdout_1245 | h1 pedestrian | 0:40 | #1 | 9.11 | bicyclist | 0.65 | 45 | 0.69 | moving_left | 1 |
| b2_0_base | day_holdout_1245 | h2 cyclist | 8:07 | #4 | 3.67 | bicyclist | 0.79 | 46 | 0.99 | moving_right | 1 |
| b2_0_base | day_holdout_1245 | h3 cyclist | 8:46 | #6 | 6.97 | bicyclist | 0.79 | 45 | 1.24 | moving_right | 1 |
| b2_0_base | day_holdout_1245 | h4 pedestrian | 9:54 | #7 | 4.84 | pedestrian | 0.18 | 0 | 0.17 | static | 1 |
| b2_0_base | day_holdout_1245 | h5 pedestrian | 11:17 | #9 | 18.59 | bicyclist | 0.65 | 7 | 0.51 | away_from_camera | 1 |
| b2_2_sahi | day_holdout_1245 | h1 pedestrian | 0:40 | #1 | 15.48 | bicyclist | 0.57 | 26 | 0.74 | moving_left | 1 |
| b2_2_sahi | day_holdout_1245 | h2 cyclist | 8:07 | #7 | 8.17 | bicyclist | 0.85 | 44 | 1.59 | moving_right | 1 |
| b2_2_sahi | day_holdout_1245 | h3 cyclist | 8:46 | #9 | 9.68 | bicyclist | 0.82 | 57 | 1.51 | moving_right | 1 |
| b2_2_sahi | day_holdout_1245 | h4 pedestrian | 9:54 | #14 | 7.21 | pedestrian | 0.17 | 0 | 0.18 | static | 1 |
| b2_2_sahi | day_holdout_1245 | h5 pedestrian | 11:17 | #15 | 23.62 | bicyclist | 0.64 | 8 | 0.56 | away_from_camera | 1 |
| b2_3_sahi_fuse | night | n1 cyclist | 4:02 | #4 | 1.2 | bicyclist | 0.97 | 94 | 4.82 | moving_right | 0 |
| b2_3_sahi_fuse | night | n2 cyclist | 7:02 | #12 | 5.24 | bicyclist | 0.91 | 88 | 0.87 | moving_right | 1 |
| b2_3_sahi_fuse | night | n3 cyclist | 14:21 | #18 | 3.47 | bicyclist | 0.62 | 49 | 1.23 | moving_right | 1 |
| b2_3_sahi_fuse | night | n4 cyclist | 14:21 | #22 | 3.44 | pedestrian | 0.30 | 59 | 2.23 | moving_right | 1 |
| b2_3_sahi_fuse | night | n5 cyclist | 14:21 | #21 | 2.37 | pedestrian | 0.39 | 31 | 2.37 | moving_right | 0 |
| b2_3_sahi_fuse | night | n6 pedestrian | 14:47 | #23 | 10.58 | bicyclist | 0.67 | 69 | 0.48 | moving_right | 1 |
| b2_3_sahi_fuse | day | d2 pedestrian | 3:00 | #2 | 20.69 | bicyclist | 0.73 | 6 | 0.56 | moving_left | 1 |
| b2_3_sahi_fuse | day | d1 cyclist | 9:10 | #10 | 6.74 | bicyclist | 0.91 | 54 | 1.51 | moving_left | 1 |
| b2_3_sahi_fuse | day | d3 pedestrian | 11:45 | #13 | 36.57 | bicyclist | 0.53 | 2 | 0.39 | moving_left | 1 |
| b2_3_sahi_fuse | day | d4 pedestrian | 12:10 | #15 | 21.96 | pedestrian | 0.24 | 6 | 0.78 | moving_left | 1 |
| b2_3_sahi_fuse | day | d5 pedestrian | 12:10 | #23 | 3.47 | pedestrian | 0.22 | 0 | 0.16 | static | 1 |
| b2_3_sahi_fuse | day_holdout_1245 | h1 pedestrian | 0:40 | #1 | 15.48 | bicyclist | 0.57 | 26 | 0.74 | moving_left | 1 |
| b2_3_sahi_fuse | day_holdout_1245 | h2 cyclist | 8:07 | #7 | 8.17 | bicyclist | 0.85 | 44 | 1.59 | moving_right | 1 |
| b2_3_sahi_fuse | day_holdout_1245 | h3 cyclist | 8:46 | #9 | 9.68 | bicyclist | 0.82 | 57 | 1.51 | moving_right | 1 |
| b2_3_sahi_fuse | day_holdout_1245 | h4 pedestrian | 9:54 | #14 | 7.21 | pedestrian | 0.17 | 0 | 0.18 | static | 1 |
| b2_3_sahi_fuse | day_holdout_1245 | h5 pedestrian | 11:17 | #15 | 23.62 | bicyclist | 0.64 | 8 | 0.56 | away_from_camera | 1 |
| b2_5_sahi_speed | night | n1 cyclist | 4:02 | #4 | 1.2 | bicyclist | 0.97 | 94 | 4.82 | moving_right | 0 |
| b2_5_sahi_speed | night | n2 cyclist | 7:02 | #12 | 5.24 | bicyclist | 0.91 | 88 | 0.87 | moving_right | 1 |
| b2_5_sahi_speed | night | n3 cyclist | 14:21 | #18 | 3.47 | bicyclist | 0.62 | 49 | 1.23 | moving_right | 1 |
| b2_5_sahi_speed | night | n4 cyclist | 14:21 | #22 | 3.44 | pedestrian | 0.30 | 59 | 2.23 | moving_right | 1 |
| b2_5_sahi_speed | night | n5 cyclist | 14:21 | #21 | 2.37 | pedestrian | 0.39 | 31 | 2.37 | moving_right | 0 |
| b2_5_sahi_speed | night | n6 pedestrian | 14:47 | #23 | 10.58 | bicyclist | 0.67 | 69 | 0.48 | moving_right | 1 |
| b2_5_sahi_speed | day | d2 pedestrian | 3:00 | #2 | 20.69 | bicyclist | 0.73 | 6 | 0.56 | moving_left | 1 |
| b2_5_sahi_speed | day | d1 cyclist | 9:10 | #10 | 6.74 | bicyclist | 0.91 | 54 | 1.51 | moving_left | 1 |
| b2_5_sahi_speed | day | d3 pedestrian | 11:45 | #13 | 36.57 | bicyclist | 0.53 | 2 | 0.39 | moving_left | 1 |
| b2_5_sahi_speed | day | d4 pedestrian | 12:10 | #15 | 21.96 | pedestrian | 0.24 | 6 | 0.78 | moving_left | 1 |
| b2_5_sahi_speed | day | d5 pedestrian | 12:10 | #23 | 3.47 | pedestrian | 0.22 | 0 | 0.16 | static | 1 |
| b2_5_sahi_speed | day_holdout_1245 | h1 pedestrian | 0:40 | #1 | 15.48 | bicyclist | 0.57 | 26 | 0.74 | moving_left | 1 |
| b2_5_sahi_speed | day_holdout_1245 | h2 cyclist | 8:07 | #7 | 8.17 | bicyclist | 0.85 | 44 | 1.59 | moving_right | 1 |
| b2_5_sahi_speed | day_holdout_1245 | h3 cyclist | 8:46 | #9 | 9.68 | bicyclist | 0.82 | 57 | 1.51 | moving_right | 1 |
| b2_5_sahi_speed | day_holdout_1245 | h4 pedestrian | 9:54 | #14 | 7.21 | pedestrian | 0.17 | 0 | 0.18 | static | 1 |
| b2_5_sahi_speed | day_holdout_1245 | h5 pedestrian | 11:17 | #15 | 23.62 | bicyclist | 0.64 | 8 | 0.56 | away_from_camera | 1 |

## Rules replayed on 50 (person, run) pairs

| rule | right | of | labels it changes |
|---|---|---|---|
| X-CLIP alone (now) | 32 | 50 | |
| veto 5% | 34 | 50 | b2_3_sahi_fuse/day/d3(ok), b2_5_sahi_speed/day/d3(ok) |
| veto 10% | 40 | 50 | b2_0_base/day_holdout_1245/h5(ok), b2_2_sahi/day_holdout_1245/h5(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h5(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h5(ok) |
| veto 15% | 40 | 50 | b2_0_base/day_holdout_1245/h5(ok), b2_2_sahi/day_holdout_1245/h5(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h5(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h5(ok) |
| veto 20% | 40 | 50 | b2_0_base/day_holdout_1245/h5(ok), b2_2_sahi/day_holdout_1245/h5(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h5(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h5(ok) |
| veto 30% | 43 | 50 | b2_0_base/day_holdout_1245/h5(ok), b2_2_sahi/day_holdout_1245/h1(ok), b2_2_sahi/day_holdout_1245/h5(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h1(ok), b2_3_sahi_fuse/day_holdout_1245/h5(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h1(ok), b2_5_sahi_speed/day_holdout_1245/h5(ok) |
| veto 40% | 42 | 50 | exp0_base/day/d1(WRONG), b2_0_base/day_holdout_1245/h5(ok), b2_2_sahi/day_holdout_1245/h1(ok), b2_2_sahi/day_holdout_1245/h5(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h1(ok), b2_3_sahi_fuse/day_holdout_1245/h5(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h1(ok), b2_5_sahi_speed/day_holdout_1245/h5(ok) |
| veto 50% | 36 | 50 | exp0_base/day/d1(WRONG), b2_0_base/day_holdout_1245/h1(ok), b2_0_base/day_holdout_1245/h2(WRONG), b2_0_base/day_holdout_1245/h3(WRONG), b2_0_base/day_holdout_1245/h5(ok), b2_2_sahi/day_holdout_1245/h1(ok), b2_2_sahi/day_holdout_1245/h2(WRONG), b2_2_sahi/day_holdout_1245/h5(ok), b2_3_sahi_fuse/night/n3(WRONG), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h1(ok), b2_3_sahi_fuse/day_holdout_1245/h2(WRONG), b2_3_sahi_fuse/day_holdout_1245/h5(ok), b2_5_sahi_speed/night/n3(WRONG), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h1(ok), b2_5_sahi_speed/day_holdout_1245/h2(WRONG), b2_5_sahi_speed/day_holdout_1245/h5(ok) |
| promote 80% | 32 | 50 | - |
| promote 90% | 32 | 50 | - |
| promote 95% | 32 | 50 | - |
| speed lateral walk<0.8 ride>2.0 | 42 | 50 | b2_0_base/day_holdout_1245/h1(ok), b2_2_sahi/day_holdout_1245/h1(ok), b2_3_sahi_fuse/night/n4(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h1(ok), b2_5_sahi_speed/night/n4(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h1(ok) |
| speed lateral walk<1.0 ride>2.0 | 40 | 50 | exp0_base/day/d1(WRONG), b2_0_base/day_holdout_1245/h1(ok), b2_0_base/day_holdout_1245/h2(WRONG), b2_2_sahi/day_holdout_1245/h1(ok), b2_3_sahi_fuse/night/n4(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h1(ok), b2_5_sahi_speed/night/n4(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h1(ok) |
| speed lateral walk<1.2 ride>2.5 | 38 | 50 | exp0_base/day/d1(WRONG), b2_0_base/day_holdout_1245/h1(ok), b2_0_base/day_holdout_1245/h2(WRONG), b2_2_sahi/day_holdout_1245/h1(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h1(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h1(ok) |
| speed lateral walk<1.5 ride>3.0 | 35 | 50 | exp0_base/day/d1(WRONG), b2_0_base/day_holdout_1245/h1(ok), b2_0_base/day_holdout_1245/h2(WRONG), b2_0_base/day_holdout_1245/h3(WRONG), b2_2_sahi/day_holdout_1245/h1(ok), b2_3_sahi_fuse/night/n3(WRONG), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h1(ok), b2_5_sahi_speed/night/n3(WRONG), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h1(ok) |

Read the per-row table first: do real riders and real walkers separate on speed (lateral tracks) or on det %cyc? A rule that only 'wins' by changing one or two rows is a coincidence.

<a id="report-fusion-probe-20261010-2251"></a>
## FUSION_PROBE_20261010_2251.md
Original location: `vision3/best/test_colonial/exp_results/FUSION_PROBE_20261010_2251.md`.

# Fusion probe

runs: exp0_base,b2_0_base,b2_2_sahi,b2_3_sahi_fuse,b2_5_sahi_speed

| run | clip | truth | when | track | secs | X-CLIP | wBIC | det %cyc | speed h/s | direction | counted |
|---|---|---|---|---|---|---|---|---|---|---|---|
| exp0_base | night | n1 cyclist | 4:02 | #1 | 0.6 | bicyclist | 0.95 | 100 | 2.64 | moving_right | 0 |
| exp0_base | night | n2 cyclist | 7:02 | #2 | 0.43 | bicyclist | 0.99 | 100 | 0.79 | moving_right | 0 |
| exp0_base | night | n3 cyclist | 14:21 | #4 | 0.9 | bicyclist | 0.70 | 59 | 1.30 | toward_camera | 0 |
| exp0_base | day | d2 pedestrian | 3:00 | #3 | 3.2 | pedestrian | 0.21 | 0 | 0.15 | static | 1 |
| exp0_base | day | d1 cyclist | 9:10 | #5 | 4.04 | bicyclist | 0.92 | 35 | 0.97 | moving_left | 1 |
| exp0_base | day | d3 pedestrian | 11:45 | #8 | 16.85 | pedestrian | 0.40 | 0 | 0.24 | away_from_camera | 1 |
| exp0_base | day | d4 pedestrian | 12:10 | #12 | 2.07 | pedestrian | 0.16 | 0 | 0.18 | static | 0 |
| exp0_base | day | d5 pedestrian | 12:10 | #13 | 1.2 | pedestrian | 0.22 | 0 | 0.18 | static | 0 |
| b2_0_base | night_holdout_2200 | p2 pedestrian | 10:00 | #3 | 0.43 | pedestrian | 0.12 | 100 | 0.58 | moving_right | 0 |
| b2_0_base | day_holdout_1245 | h1 pedestrian | 0:40 | #1 | 9.11 | bicyclist | 0.65 | 45 | 0.69 | moving_left | 1 |
| b2_0_base | day_holdout_1245 | h2 cyclist | 8:07 | #4 | 3.67 | bicyclist | 0.79 | 46 | 0.99 | moving_right | 1 |
| b2_0_base | day_holdout_1245 | h3 cyclist | 8:46 | #6 | 6.97 | bicyclist | 0.79 | 45 | 1.24 | moving_right | 1 |
| b2_0_base | day_holdout_1245 | h4 pedestrian | 9:54 | #7 | 4.84 | pedestrian | 0.18 | 0 | 0.17 | static | 1 |
| b2_0_base | day_holdout_1245 | h5 pedestrian | 11:17 | #9 | 18.59 | bicyclist | 0.65 | 7 | 0.51 | away_from_camera | 1 |
| b2_2_sahi | night_holdout_2200 | p1 pedestrian | 6:00 | #18 | 10.48 | pedestrian | 0.29 | 24 | 0.65 | moving_right | 1 |
| b2_2_sahi | night_holdout_2200 | p2 pedestrian | 10:00 | #27 | 18.72 | pedestrian | 0.23 | 32 | 0.15 | moving_right | 1 |
| b2_2_sahi | night_holdout_2200 | p3 pedestrian | 10:59 | #33 | 14.98 | pedestrian | 0.35 | 43 | 0.30 | moving_right | 1 |
| b2_2_sahi | night_holdout_2200 | p4 pedestrian | 10:59 | #36 | 5.84 | pedestrian | 0.05 | 28 | 0.51 | toward_camera | 1 |
| b2_2_sahi | night_holdout_2200 | p5 pedestrian | 10:59 | #40 | 3.84 | pedestrian | 0.15 | 76 | 0.96 | moving_right | 1 |
| b2_2_sahi | day_holdout_1245 | h1 pedestrian | 0:40 | #1 | 15.48 | bicyclist | 0.57 | 26 | 0.74 | moving_left | 1 |
| b2_2_sahi | day_holdout_1245 | h2 cyclist | 8:07 | #7 | 8.17 | bicyclist | 0.85 | 44 | 1.59 | moving_right | 1 |
| b2_2_sahi | day_holdout_1245 | h3 cyclist | 8:46 | #9 | 9.68 | bicyclist | 0.82 | 57 | 1.51 | moving_right | 1 |
| b2_2_sahi | day_holdout_1245 | h4 pedestrian | 9:54 | #14 | 7.21 | pedestrian | 0.17 | 0 | 0.18 | static | 1 |
| b2_2_sahi | day_holdout_1245 | h5 pedestrian | 11:17 | #15 | 23.62 | bicyclist | 0.64 | 8 | 0.56 | away_from_camera | 1 |
| b2_3_sahi_fuse | night | n1 cyclist | 4:02 | #4 | 1.2 | bicyclist | 0.97 | 94 | 4.82 | moving_right | 0 |
| b2_3_sahi_fuse | night | n2 cyclist | 7:02 | #12 | 5.24 | bicyclist | 0.91 | 88 | 0.87 | moving_right | 1 |
| b2_3_sahi_fuse | night | n3 cyclist | 14:21 | #18 | 3.47 | bicyclist | 0.62 | 49 | 1.23 | moving_right | 1 |
| b2_3_sahi_fuse | night | n4 cyclist | 14:21 | #22 | 3.44 | pedestrian | 0.30 | 59 | 2.23 | moving_right | 1 |
| b2_3_sahi_fuse | night | n5 cyclist | 14:21 | #21 | 2.37 | pedestrian | 0.39 | 31 | 2.37 | moving_right | 0 |
| b2_3_sahi_fuse | night | n6 pedestrian | 14:47 | #23 | 10.58 | bicyclist | 0.67 | 69 | 0.48 | moving_right | 1 |
| b2_3_sahi_fuse | day | d2 pedestrian | 3:00 | #2 | 20.69 | bicyclist | 0.73 | 6 | 0.56 | moving_left | 1 |
| b2_3_sahi_fuse | day | d1 cyclist | 9:10 | #10 | 6.74 | bicyclist | 0.91 | 54 | 1.51 | moving_left | 1 |
| b2_3_sahi_fuse | day | d3 pedestrian | 11:45 | #13 | 36.57 | bicyclist | 0.53 | 2 | 0.39 | moving_left | 1 |
| b2_3_sahi_fuse | day | d4 pedestrian | 12:10 | #15 | 21.96 | pedestrian | 0.24 | 6 | 0.78 | moving_left | 1 |
| b2_3_sahi_fuse | day | d5 pedestrian | 12:10 | #23 | 3.47 | pedestrian | 0.22 | 0 | 0.16 | static | 1 |
| b2_3_sahi_fuse | night_holdout_2200 | p1 pedestrian | 6:00 | #18 | 10.48 | pedestrian | 0.29 | 24 | 0.65 | moving_right | 1 |
| b2_3_sahi_fuse | night_holdout_2200 | p2 pedestrian | 10:00 | #27 | 18.72 | pedestrian | 0.23 | 32 | 0.15 | moving_right | 1 |
| b2_3_sahi_fuse | night_holdout_2200 | p3 pedestrian | 10:59 | #33 | 14.98 | pedestrian | 0.35 | 43 | 0.30 | moving_right | 1 |
| b2_3_sahi_fuse | night_holdout_2200 | p4 pedestrian | 10:59 | #36 | 5.84 | pedestrian | 0.05 | 28 | 0.51 | toward_camera | 1 |
| b2_3_sahi_fuse | night_holdout_2200 | p5 pedestrian | 10:59 | #40 | 3.84 | pedestrian | 0.15 | 76 | 0.96 | moving_right | 1 |
| b2_3_sahi_fuse | day_holdout_1245 | h1 pedestrian | 0:40 | #1 | 15.48 | bicyclist | 0.57 | 26 | 0.74 | moving_left | 1 |
| b2_3_sahi_fuse | day_holdout_1245 | h2 cyclist | 8:07 | #7 | 8.17 | bicyclist | 0.85 | 44 | 1.59 | moving_right | 1 |
| b2_3_sahi_fuse | day_holdout_1245 | h3 cyclist | 8:46 | #9 | 9.68 | bicyclist | 0.82 | 57 | 1.51 | moving_right | 1 |
| b2_3_sahi_fuse | day_holdout_1245 | h4 pedestrian | 9:54 | #14 | 7.21 | pedestrian | 0.17 | 0 | 0.18 | static | 1 |
| b2_3_sahi_fuse | day_holdout_1245 | h5 pedestrian | 11:17 | #15 | 23.62 | bicyclist | 0.64 | 8 | 0.56 | away_from_camera | 1 |
| b2_5_sahi_speed | night | n1 cyclist | 4:02 | #4 | 1.2 | bicyclist | 0.97 | 94 | 4.82 | moving_right | 0 |
| b2_5_sahi_speed | night | n2 cyclist | 7:02 | #12 | 5.24 | bicyclist | 0.91 | 88 | 0.87 | moving_right | 1 |
| b2_5_sahi_speed | night | n3 cyclist | 14:21 | #18 | 3.47 | bicyclist | 0.62 | 49 | 1.23 | moving_right | 1 |
| b2_5_sahi_speed | night | n4 cyclist | 14:21 | #22 | 3.44 | pedestrian | 0.30 | 59 | 2.23 | moving_right | 1 |
| b2_5_sahi_speed | night | n5 cyclist | 14:21 | #21 | 2.37 | pedestrian | 0.39 | 31 | 2.37 | moving_right | 0 |
| b2_5_sahi_speed | night | n6 pedestrian | 14:47 | #23 | 10.58 | bicyclist | 0.67 | 69 | 0.48 | moving_right | 1 |
| b2_5_sahi_speed | day | d2 pedestrian | 3:00 | #2 | 20.69 | bicyclist | 0.73 | 6 | 0.56 | moving_left | 1 |
| b2_5_sahi_speed | day | d1 cyclist | 9:10 | #10 | 6.74 | bicyclist | 0.91 | 54 | 1.51 | moving_left | 1 |
| b2_5_sahi_speed | day | d3 pedestrian | 11:45 | #13 | 36.57 | bicyclist | 0.53 | 2 | 0.39 | moving_left | 1 |
| b2_5_sahi_speed | day | d4 pedestrian | 12:10 | #15 | 21.96 | pedestrian | 0.24 | 6 | 0.78 | moving_left | 1 |
| b2_5_sahi_speed | day | d5 pedestrian | 12:10 | #23 | 3.47 | pedestrian | 0.22 | 0 | 0.16 | static | 1 |
| b2_5_sahi_speed | night_holdout_2200 | p1 pedestrian | 6:00 | #18 | 10.48 | pedestrian | 0.29 | 24 | 0.65 | moving_right | 1 |
| b2_5_sahi_speed | night_holdout_2200 | p2 pedestrian | 10:00 | #27 | 18.72 | pedestrian | 0.23 | 32 | 0.15 | moving_right | 1 |
| b2_5_sahi_speed | night_holdout_2200 | p3 pedestrian | 10:59 | #33 | 14.98 | pedestrian | 0.35 | 43 | 0.30 | moving_right | 1 |
| b2_5_sahi_speed | night_holdout_2200 | p4 pedestrian | 10:59 | #36 | 5.84 | pedestrian | 0.05 | 28 | 0.51 | toward_camera | 1 |
| b2_5_sahi_speed | night_holdout_2200 | p5 pedestrian | 10:59 | #40 | 3.84 | pedestrian | 0.15 | 76 | 0.96 | moving_right | 1 |
| b2_5_sahi_speed | day_holdout_1245 | h1 pedestrian | 0:40 | #1 | 15.48 | bicyclist | 0.57 | 26 | 0.74 | moving_left | 1 |
| b2_5_sahi_speed | day_holdout_1245 | h2 cyclist | 8:07 | #7 | 8.17 | bicyclist | 0.85 | 44 | 1.59 | moving_right | 1 |
| b2_5_sahi_speed | day_holdout_1245 | h3 cyclist | 8:46 | #9 | 9.68 | bicyclist | 0.82 | 57 | 1.51 | moving_right | 1 |
| b2_5_sahi_speed | day_holdout_1245 | h4 pedestrian | 9:54 | #14 | 7.21 | pedestrian | 0.17 | 0 | 0.18 | static | 1 |
| b2_5_sahi_speed | day_holdout_1245 | h5 pedestrian | 11:17 | #15 | 23.62 | bicyclist | 0.64 | 8 | 0.56 | away_from_camera | 1 |

## Rules replayed on 66 (person, run) pairs

| rule | right | of | labels it changes |
|---|---|---|---|
| X-CLIP alone (now) | 48 | 66 | |
| veto 5% | 50 | 66 | b2_3_sahi_fuse/day/d3(ok), b2_5_sahi_speed/day/d3(ok) |
| veto 10% | 56 | 66 | b2_0_base/day_holdout_1245/h5(ok), b2_2_sahi/day_holdout_1245/h5(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h5(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h5(ok) |
| veto 15% | 56 | 66 | b2_0_base/day_holdout_1245/h5(ok), b2_2_sahi/day_holdout_1245/h5(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h5(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h5(ok) |
| veto 20% | 56 | 66 | b2_0_base/day_holdout_1245/h5(ok), b2_2_sahi/day_holdout_1245/h5(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h5(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h5(ok) |
| veto 30% | 59 | 66 | b2_0_base/day_holdout_1245/h5(ok), b2_2_sahi/day_holdout_1245/h1(ok), b2_2_sahi/day_holdout_1245/h5(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h1(ok), b2_3_sahi_fuse/day_holdout_1245/h5(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h1(ok), b2_5_sahi_speed/day_holdout_1245/h5(ok) |
| veto 40% | 58 | 66 | exp0_base/day/d1(WRONG), b2_0_base/day_holdout_1245/h5(ok), b2_2_sahi/day_holdout_1245/h1(ok), b2_2_sahi/day_holdout_1245/h5(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h1(ok), b2_3_sahi_fuse/day_holdout_1245/h5(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h1(ok), b2_5_sahi_speed/day_holdout_1245/h5(ok) |
| veto 50% | 52 | 66 | exp0_base/day/d1(WRONG), b2_0_base/day_holdout_1245/h1(ok), b2_0_base/day_holdout_1245/h2(WRONG), b2_0_base/day_holdout_1245/h3(WRONG), b2_0_base/day_holdout_1245/h5(ok), b2_2_sahi/day_holdout_1245/h1(ok), b2_2_sahi/day_holdout_1245/h2(WRONG), b2_2_sahi/day_holdout_1245/h5(ok), b2_3_sahi_fuse/night/n3(WRONG), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h1(ok), b2_3_sahi_fuse/day_holdout_1245/h2(WRONG), b2_3_sahi_fuse/day_holdout_1245/h5(ok), b2_5_sahi_speed/night/n3(WRONG), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h1(ok), b2_5_sahi_speed/day_holdout_1245/h2(WRONG), b2_5_sahi_speed/day_holdout_1245/h5(ok) |
| promote 80% | 47 | 66 | b2_0_base/night_holdout_2200/p2(WRONG) |
| promote 90% | 47 | 66 | b2_0_base/night_holdout_2200/p2(WRONG) |
| promote 95% | 47 | 66 | b2_0_base/night_holdout_2200/p2(WRONG) |
| speed lateral walk<0.8 ride>2.0 | 58 | 66 | b2_0_base/day_holdout_1245/h1(ok), b2_2_sahi/day_holdout_1245/h1(ok), b2_3_sahi_fuse/night/n4(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h1(ok), b2_5_sahi_speed/night/n4(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h1(ok) |
| speed lateral walk<1.0 ride>2.0 | 56 | 66 | exp0_base/day/d1(WRONG), b2_0_base/day_holdout_1245/h1(ok), b2_0_base/day_holdout_1245/h2(WRONG), b2_2_sahi/day_holdout_1245/h1(ok), b2_3_sahi_fuse/night/n4(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h1(ok), b2_5_sahi_speed/night/n4(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h1(ok) |
| speed lateral walk<1.2 ride>2.5 | 54 | 66 | exp0_base/day/d1(WRONG), b2_0_base/day_holdout_1245/h1(ok), b2_0_base/day_holdout_1245/h2(WRONG), b2_2_sahi/day_holdout_1245/h1(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h1(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h1(ok) |
| speed lateral walk<1.5 ride>3.0 | 51 | 66 | exp0_base/day/d1(WRONG), b2_0_base/day_holdout_1245/h1(ok), b2_0_base/day_holdout_1245/h2(WRONG), b2_0_base/day_holdout_1245/h3(WRONG), b2_2_sahi/day_holdout_1245/h1(ok), b2_3_sahi_fuse/night/n3(WRONG), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h1(ok), b2_5_sahi_speed/night/n3(WRONG), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h1(ok) |

Read the per-row table first: do real riders and real walkers separate on speed (lateral tracks) or on det %cyc? A rule that only 'wins' by changing one or two rows is a coincidence.

## Counted tracks that match NO truth person (false detections, or a person missing from the truth file)

| run | clip | when | track | secs | X-CLIP | wBIC | det %cyc | speed h/s | net px | direction |
|---|---|---|---|---|---|---|---|---|---|---|
| b2_2_sahi | night_holdout_2200 | 7:50-8:27 | #24 | 4.97 | pedestrian | 0.31 | 0 | 0.01 | 0 | static |
| b2_2_sahi | night_holdout_2200 | 8:32-9:00 | #26 | 3.8 | pedestrian | 0.26 | 0 | 0.01 | 2 | static |
| b2_3_sahi_fuse | night_holdout_2200 | 7:50-8:27 | #24 | 4.97 | pedestrian | 0.31 | 0 | 0.01 | 0 | static |
| b2_3_sahi_fuse | night_holdout_2200 | 8:32-9:00 | #26 | 3.8 | pedestrian | 0.26 | 0 | 0.01 | 2 | static |
| b2_5_sahi_speed | night_holdout_2200 | 7:50-8:27 | #24 | 4.97 | pedestrian | 0.31 | 0 | 0.01 | 0 | static |
| b2_5_sahi_speed | night_holdout_2200 | 8:32-9:00 | #26 | 3.8 | pedestrian | 0.26 | 0 | 0.01 | 2 | static |

A static object (barricade, sign) tracked as a person should show a tiny net movement and speed; compare with the real people above before choosing a filter.

<a id="report-fusion-probe-20261010-2338"></a>
## FUSION_PROBE_20261010_2338.md
Original location: `vision3/best/test_colonial/exp_results/FUSION_PROBE_20261010_2338.md`.

# Fusion probe

runs: b3_combo,b2_2_sahi

| run | clip | truth | when | track | secs | X-CLIP | wBIC | det %cyc | speed h/s | net px | direction | counted |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| b3_combo | night | n1 cyclist | 4:02 | #4 | 1.2 | bicyclist | 0.97 | 94 | 4.82 | 560 | moving_right | 1 |
| b3_combo | night | n2 cyclist | 7:02 | #12 | 5.24 | bicyclist | 0.91 | 88 | 0.87 | 706 | moving_right | 1 |
| b3_combo | night | n3 cyclist | 14:21 | #18 | 3.47 | bicyclist | 0.62 | 49 | 1.23 | 499 | moving_right | 1 |
| b3_combo | night | n4 cyclist | 14:21 | #22 | 3.44 | pedestrian | 0.30 | 59 | 2.23 | 458 | moving_right | 1 |
| b3_combo | night | n5 cyclist | 14:21 | #21 | 2.37 | pedestrian | 0.39 | 31 | 2.37 | 437 | moving_right | 0 |
| b3_combo | night | n6 pedestrian | 14:47 | #23 | 10.58 | bicyclist | 0.67 | 69 | 0.48 | 526 | moving_right | 1 |
| b3_combo | day | d2 pedestrian | 3:00 | #2 | 20.69 | bicyclist | 0.73 | 6 | 0.56 | 593 | moving_left | 1 |
| b3_combo | day | d1 cyclist | 9:10 | #10 | 6.74 | bicyclist | 0.91 | 54 | 1.51 | 749 | moving_left | 1 |
| b3_combo | day | d3 pedestrian | 11:45 | #13 | 36.57 | bicyclist | 0.53 | 2 | 0.39 | 499 | moving_left | 1 |
| b3_combo | day | d4 pedestrian | 12:10 | #15 | 21.96 | pedestrian | 0.24 | 6 | 0.78 | 628 | moving_left | 1 |
| b3_combo | day | d5 pedestrian | 12:10 | #23 | 3.47 | pedestrian | 0.22 | 0 | 0.16 | 17 | static | 1 |
| b3_combo | night_holdout_2200 | p1 pedestrian | 6:00 | #18 | 10.48 | pedestrian | 0.29 | 24 | 0.65 | 518 | moving_right | 1 |
| b3_combo | night_holdout_2200 | p2 pedestrian | 10:00 | #27 | 18.72 | pedestrian | 0.23 | 32 | 0.15 | 516 | moving_right | 1 |
| b3_combo | night_holdout_2200 | p3 pedestrian | 10:59 | #33 | 14.98 | pedestrian | 0.35 | 43 | 0.30 | 526 | moving_right | 1 |
| b3_combo | night_holdout_2200 | p4 pedestrian | 10:59 | #36 | 5.84 | pedestrian | 0.05 | 28 | 0.51 | 416 | toward_camera | 1 |
| b3_combo | night_holdout_2200 | p5 pedestrian | 10:59 | #40 | 3.84 | pedestrian | 0.15 | 76 | 0.96 | 344 | moving_right | 1 |
| b3_combo | day_holdout_1245 | h1 pedestrian | 0:40 | #1 | 15.48 | bicyclist | 0.57 | 26 | 0.74 | 678 | moving_left | 1 |
| b3_combo | day_holdout_1245 | h2 cyclist | 8:07 | #7 | 8.17 | bicyclist | 0.85 | 44 | 1.59 | 730 | moving_right | 1 |
| b3_combo | day_holdout_1245 | h3 cyclist | 8:46 | #9 | 9.68 | bicyclist | 0.82 | 57 | 1.51 | 733 | moving_right | 1 |
| b3_combo | day_holdout_1245 | h4 pedestrian | 9:54 | #14 | 7.21 | pedestrian | 0.17 | 0 | 0.18 | 30 | static | 1 |
| b3_combo | day_holdout_1245 | h5 pedestrian | 11:17 | #15 | 23.62 | bicyclist | 0.64 | 8 | 0.56 | 460 | away_from_camera | 1 |
| b2_2_sahi | night_holdout_2200 | p1 pedestrian | 6:00 | #18 | 10.48 | pedestrian | 0.29 | 24 | 0.65 | 518 | moving_right | 1 |
| b2_2_sahi | night_holdout_2200 | p2 pedestrian | 10:00 | #27 | 18.72 | pedestrian | 0.23 | 32 | 0.15 | 516 | moving_right | 1 |
| b2_2_sahi | night_holdout_2200 | p3 pedestrian | 10:59 | #33 | 14.98 | pedestrian | 0.35 | 43 | 0.30 | 526 | moving_right | 1 |
| b2_2_sahi | night_holdout_2200 | p4 pedestrian | 10:59 | #36 | 5.84 | pedestrian | 0.05 | 28 | 0.51 | 416 | toward_camera | 1 |
| b2_2_sahi | night_holdout_2200 | p5 pedestrian | 10:59 | #40 | 3.84 | pedestrian | 0.15 | 76 | 0.96 | 344 | moving_right | 1 |
| b2_2_sahi | day_holdout_1245 | h1 pedestrian | 0:40 | #1 | 15.48 | bicyclist | 0.57 | 26 | 0.74 | 678 | moving_left | 1 |
| b2_2_sahi | day_holdout_1245 | h2 cyclist | 8:07 | #7 | 8.17 | bicyclist | 0.85 | 44 | 1.59 | 730 | moving_right | 1 |
| b2_2_sahi | day_holdout_1245 | h3 cyclist | 8:46 | #9 | 9.68 | bicyclist | 0.82 | 57 | 1.51 | 733 | moving_right | 1 |
| b2_2_sahi | day_holdout_1245 | h4 pedestrian | 9:54 | #14 | 7.21 | pedestrian | 0.17 | 0 | 0.18 | 30 | static | 1 |
| b2_2_sahi | day_holdout_1245 | h5 pedestrian | 11:17 | #15 | 23.62 | bicyclist | 0.64 | 8 | 0.56 | 460 | away_from_camera | 1 |

## Rules replayed on 31 (person, run) pairs

| rule | right | of | labels it changes |
|---|---|---|---|
| X-CLIP alone (now) | 22 | 31 | |
| veto 5% | 23 | 31 | b3_combo/day/d3(ok) |
| veto 10% | 26 | 31 | b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h5(ok), b2_2_sahi/day_holdout_1245/h5(ok) |
| veto 15% | 26 | 31 | b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h5(ok), b2_2_sahi/day_holdout_1245/h5(ok) |
| veto 20% | 26 | 31 | b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h5(ok), b2_2_sahi/day_holdout_1245/h5(ok) |
| veto 30% | 28 | 31 | b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b3_combo/day_holdout_1245/h5(ok), b2_2_sahi/day_holdout_1245/h1(ok), b2_2_sahi/day_holdout_1245/h5(ok) |
| veto 40% | 28 | 31 | b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b3_combo/day_holdout_1245/h5(ok), b2_2_sahi/day_holdout_1245/h1(ok), b2_2_sahi/day_holdout_1245/h5(ok) |
| veto 50% | 25 | 31 | b3_combo/night/n3(WRONG), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b3_combo/day_holdout_1245/h2(WRONG), b3_combo/day_holdout_1245/h5(ok), b2_2_sahi/day_holdout_1245/h1(ok), b2_2_sahi/day_holdout_1245/h2(WRONG), b2_2_sahi/day_holdout_1245/h5(ok) |
| promote 80% | 22 | 31 | - |
| promote 90% | 22 | 31 | - |
| promote 95% | 22 | 31 | - |
| speed lateral walk<0.8 ride>2.0 | 27 | 31 | b3_combo/night/n4(ok), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b2_2_sahi/day_holdout_1245/h1(ok) |
| speed lateral walk<1.0 ride>2.0 | 27 | 31 | b3_combo/night/n4(ok), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b2_2_sahi/day_holdout_1245/h1(ok) |
| speed lateral walk<1.2 ride>2.5 | 26 | 31 | b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b2_2_sahi/day_holdout_1245/h1(ok) |
| speed lateral walk<1.5 ride>3.0 | 25 | 31 | b3_combo/night/n3(WRONG), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b2_2_sahi/day_holdout_1245/h1(ok) |

Read the per-row table first: do real riders and real walkers separate on speed (lateral tracks) or on det %cyc? A rule that only 'wins' by changing one or two rows is a coincidence.

## Counted tracks that match NO truth person (false detections, or a person missing from the truth file)

| run | clip | when | track | secs | X-CLIP | wBIC | det %cyc | speed h/s | net px | direction |
|---|---|---|---|---|---|---|---|---|---|---|
| b3_combo | night_holdout_2200 | 7:50-8:27 | #24 | 4.97 | pedestrian | 0.31 | 0 | 0.01 | 0 | static |
| b3_combo | night_holdout_2200 | 8:32-9:00 | #26 | 3.8 | pedestrian | 0.26 | 0 | 0.01 | 2 | static |
| b2_2_sahi | night_holdout_2200 | 7:50-8:27 | #24 | 4.97 | pedestrian | 0.31 | 0 | 0.01 | 0 | static |
| b2_2_sahi | night_holdout_2200 | 8:32-9:00 | #26 | 3.8 | pedestrian | 0.26 | 0 | 0.01 | 2 | static |

A static object (barricade, sign) tracked as a person should show a tiny net movement and speed; compare with the real people above before choosing a filter.

<a id="report-fusion-probe-20261012-0003"></a>
## FUSION_PROBE_20261012_0003.md
Original location: `vision3/best/test_colonial/exp_results/FUSION_PROBE_20261012_0003.md`.

# Fusion probe

runs: b3_combo,b4_combo_static5

| run | clip | truth | when | track | secs | X-CLIP | wBIC | det %cyc | speed h/s | net px | direction | counted |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| b3_combo | night | n1 cyclist | 4:02 | #4 | 1.2 | bicyclist | 0.97 | 94 | 4.82 | 560 | moving_right | 1 |
| b3_combo | night | n2 cyclist | 7:02 | #12 | 5.24 | bicyclist | 0.91 | 88 | 0.87 | 706 | moving_right | 1 |
| b3_combo | night | n3 cyclist | 14:21 | #18 | 3.47 | bicyclist | 0.62 | 49 | 1.23 | 499 | moving_right | 1 |
| b3_combo | night | n4 cyclist | 14:21 | #22 | 3.44 | pedestrian | 0.30 | 59 | 2.23 | 458 | moving_right | 1 |
| b3_combo | night | n5 cyclist | 14:21 | #21 | 2.37 | pedestrian | 0.39 | 31 | 2.37 | 437 | moving_right | 0 |
| b3_combo | night | n6 pedestrian | 14:47 | #23 | 10.58 | bicyclist | 0.67 | 69 | 0.48 | 526 | moving_right | 1 |
| b3_combo | day | d2 pedestrian | 3:00 | #2 | 20.69 | bicyclist | 0.73 | 6 | 0.56 | 593 | moving_left | 1 |
| b3_combo | day | d1 cyclist | 9:10 | #10 | 6.74 | bicyclist | 0.91 | 54 | 1.51 | 749 | moving_left | 1 |
| b3_combo | day | d3 pedestrian | 11:45 | #13 | 36.57 | bicyclist | 0.53 | 2 | 0.39 | 499 | moving_left | 1 |
| b3_combo | day | d4 pedestrian | 12:10 | #15 | 21.96 | pedestrian | 0.24 | 6 | 0.78 | 628 | moving_left | 1 |
| b3_combo | day | d5 pedestrian | 12:10 | #23 | 3.47 | pedestrian | 0.22 | 0 | 0.16 | 17 | static | 1 |
| b3_combo | night_holdout_2200 | p1 pedestrian | 6:00 | #18 | 10.48 | pedestrian | 0.29 | 24 | 0.65 | 518 | moving_right | 1 |
| b3_combo | night_holdout_2200 | p2 pedestrian | 10:00 | #27 | 18.72 | pedestrian | 0.23 | 32 | 0.15 | 516 | moving_right | 1 |
| b3_combo | night_holdout_2200 | p3 pedestrian | 10:59 | #33 | 14.98 | pedestrian | 0.35 | 43 | 0.30 | 526 | moving_right | 1 |
| b3_combo | night_holdout_2200 | p4 pedestrian | 10:59 | #36 | 5.84 | pedestrian | 0.05 | 28 | 0.51 | 416 | toward_camera | 1 |
| b3_combo | night_holdout_2200 | p5 pedestrian | 10:59 | #40 | 3.84 | pedestrian | 0.15 | 76 | 0.96 | 344 | moving_right | 1 |
| b3_combo | day_holdout_1245 | h1 pedestrian | 0:40 | #1 | 15.48 | bicyclist | 0.57 | 26 | 0.74 | 678 | moving_left | 1 |
| b3_combo | day_holdout_1245 | h2 cyclist | 8:07 | #7 | 8.17 | bicyclist | 0.85 | 44 | 1.59 | 730 | moving_right | 1 |
| b3_combo | day_holdout_1245 | h3 cyclist | 8:46 | #9 | 9.68 | bicyclist | 0.82 | 57 | 1.51 | 733 | moving_right | 1 |
| b3_combo | day_holdout_1245 | h4 pedestrian | 9:54 | #14 | 7.21 | pedestrian | 0.17 | 0 | 0.18 | 30 | static | 1 |
| b3_combo | day_holdout_1245 | h5 pedestrian | 11:17 | #15 | 23.62 | bicyclist | 0.64 | 8 | 0.56 | 460 | away_from_camera | 1 |
| b4_combo_static5 | night | n1 cyclist | 4:02 | #4 | 1.2 | bicyclist | 0.97 | 94 | 4.82 | 560 | moving_right | 1 |
| b4_combo_static5 | night | n2 cyclist | 7:02 | #12 | 5.24 | bicyclist | 0.91 | 88 | 0.87 | 706 | moving_right | 1 |
| b4_combo_static5 | night | n3 cyclist | 14:21 | #18 | 3.47 | bicyclist | 0.62 | 49 | 1.23 | 499 | moving_right | 1 |
| b4_combo_static5 | night | n4 cyclist | 14:21 | #22 | 3.44 | pedestrian | 0.30 | 59 | 2.23 | 458 | moving_right | 1 |
| b4_combo_static5 | night | n5 cyclist | 14:21 | #21 | 2.37 | pedestrian | 0.39 | 31 | 2.37 | 437 | moving_right | 0 |
| b4_combo_static5 | night | n6 pedestrian | 14:47 | #23 | 10.58 | bicyclist | 0.67 | 69 | 0.48 | 526 | moving_right | 1 |
| b4_combo_static5 | day | d2 pedestrian | 3:00 | #2 | 20.69 | bicyclist | 0.73 | 6 | 0.56 | 593 | moving_left | 1 |
| b4_combo_static5 | day | d1 cyclist | 9:10 | #10 | 6.74 | bicyclist | 0.91 | 54 | 1.51 | 749 | moving_left | 1 |
| b4_combo_static5 | day | d3 pedestrian | 11:45 | #13 | 36.57 | bicyclist | 0.53 | 2 | 0.39 | 499 | moving_left | 1 |
| b4_combo_static5 | day | d4 pedestrian | 12:10 | #15 | 21.96 | pedestrian | 0.24 | 6 | 0.78 | 628 | moving_left | 1 |
| b4_combo_static5 | day | d5 pedestrian | 12:10 | #23 | 3.47 | pedestrian | 0.22 | 0 | 0.16 | 17 | static | 1 |
| b4_combo_static5 | night_holdout_2200 | p1 pedestrian | 6:00 | #18 | 10.48 | pedestrian | 0.29 | 24 | 0.65 | 518 | moving_right | 1 |
| b4_combo_static5 | night_holdout_2200 | p2 pedestrian | 10:00 | #27 | 18.72 | pedestrian | 0.23 | 32 | 0.15 | 516 | moving_right | 1 |
| b4_combo_static5 | night_holdout_2200 | p3 pedestrian | 10:59 | #33 | 14.98 | pedestrian | 0.35 | 43 | 0.30 | 526 | moving_right | 1 |
| b4_combo_static5 | night_holdout_2200 | p4 pedestrian | 10:59 | #36 | 5.84 | pedestrian | 0.05 | 28 | 0.51 | 416 | toward_camera | 1 |
| b4_combo_static5 | night_holdout_2200 | p5 pedestrian | 10:59 | #40 | 3.84 | pedestrian | 0.15 | 76 | 0.96 | 344 | moving_right | 1 |
| b4_combo_static5 | day_holdout_1245 | h1 pedestrian | 0:40 | #1 | 15.48 | bicyclist | 0.57 | 26 | 0.74 | 678 | moving_left | 1 |
| b4_combo_static5 | day_holdout_1245 | h2 cyclist | 8:07 | #7 | 8.17 | bicyclist | 0.85 | 44 | 1.59 | 730 | moving_right | 1 |
| b4_combo_static5 | day_holdout_1245 | h3 cyclist | 8:46 | #9 | 9.68 | bicyclist | 0.82 | 57 | 1.51 | 733 | moving_right | 1 |
| b4_combo_static5 | day_holdout_1245 | h4 pedestrian | 9:54 | #14 | 7.21 | pedestrian | 0.17 | 0 | 0.18 | 30 | static | 1 |
| b4_combo_static5 | day_holdout_1245 | h5 pedestrian | 11:17 | #15 | 23.62 | bicyclist | 0.64 | 8 | 0.56 | 460 | away_from_camera | 1 |

## Rules replayed on 42 (person, run) pairs

| rule | right | of | labels it changes |
|---|---|---|---|
| X-CLIP alone (now) | 28 | 42 | |
| veto 5% | 30 | 42 | b3_combo/day/d3(ok), b4_combo_static5/day/d3(ok) |
| veto 10% | 34 | 42 | b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h5(ok), b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h5(ok) |
| veto 15% | 34 | 42 | b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h5(ok), b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h5(ok) |
| veto 20% | 34 | 42 | b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h5(ok), b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h5(ok) |
| veto 30% | 36 | 42 | b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b3_combo/day_holdout_1245/h5(ok), b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h1(ok), b4_combo_static5/day_holdout_1245/h5(ok) |
| veto 40% | 36 | 42 | b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b3_combo/day_holdout_1245/h5(ok), b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h1(ok), b4_combo_static5/day_holdout_1245/h5(ok) |
| veto 50% | 32 | 42 | b3_combo/night/n3(WRONG), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b3_combo/day_holdout_1245/h2(WRONG), b3_combo/day_holdout_1245/h5(ok), b4_combo_static5/night/n3(WRONG), b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h1(ok), b4_combo_static5/day_holdout_1245/h2(WRONG), b4_combo_static5/day_holdout_1245/h5(ok) |
| promote 80% | 28 | 42 | - |
| promote 90% | 28 | 42 | - |
| promote 95% | 28 | 42 | - |
| speed lateral walk<0.8 ride>2.0 | 36 | 42 | b3_combo/night/n4(ok), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b4_combo_static5/night/n4(ok), b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h1(ok) |
| speed lateral walk<1.0 ride>2.0 | 36 | 42 | b3_combo/night/n4(ok), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b4_combo_static5/night/n4(ok), b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h1(ok) |
| speed lateral walk<1.2 ride>2.5 | 34 | 42 | b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h1(ok) |
| speed lateral walk<1.5 ride>3.0 | 32 | 42 | b3_combo/night/n3(WRONG), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b4_combo_static5/night/n3(WRONG), b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h1(ok) |

Read the per-row table first: do real riders and real walkers separate on speed (lateral tracks) or on det %cyc? A rule that only 'wins' by changing one or two rows is a coincidence.

## Counted tracks that match NO truth person (false detections, or a person missing from the truth file)

| run | clip | when | track | secs | X-CLIP | wBIC | det %cyc | speed h/s | net px | direction |
|---|---|---|---|---|---|---|---|---|---|---|
| b3_combo | night_holdout_2200 | 7:50-8:27 | #24 | 4.97 | pedestrian | 0.31 | 0 | 0.01 | 0 | static |
| b3_combo | night_holdout_2200 | 8:32-9:00 | #26 | 3.8 | pedestrian | 0.26 | 0 | 0.01 | 2 | static |

A static object (barricade, sign) tracked as a person should show a tiny net movement and speed; compare with the real people above before choosing a filter.

<a id="report-fusion-batch3-20261010-2152"></a>
## FUSION_batch3_20261010_2152.md
Original location: `vision3/best/test_colonial/exp_results/FUSION_batch3_20261010_2152.md`.

# Fusion probe

runs: exp0_base,exp1_sahi,b2_0_base,b2_2_sahi,b2_3_sahi_fuse,b2_4_sahi_fuse_nightshort,b2_5_sahi_speed,b3_combo

| run | clip | truth | when | track | secs | X-CLIP | wBIC | det %cyc | speed h/s | direction | counted |
|---|---|---|---|---|---|---|---|---|---|---|---|
| exp0_base | night | n1 cyclist | 4:02 | #1 | 0.6 | bicyclist | 0.95 | 100 | 2.64 | moving_right | 0 |
| exp0_base | night | n2 cyclist | 7:02 | #2 | 0.43 | bicyclist | 0.99 | 100 | 0.79 | moving_right | 0 |
| exp0_base | night | n3 cyclist | 14:21 | #4 | 0.9 | bicyclist | 0.70 | 59 | 1.30 | toward_camera | 0 |
| exp0_base | day | d2 pedestrian | 3:00 | #3 | 3.2 | pedestrian | 0.21 | 0 | 0.15 | static | 1 |
| exp0_base | day | d1 cyclist | 9:10 | #5 | 4.04 | bicyclist | 0.92 | 35 | 0.97 | moving_left | 1 |
| exp0_base | day | d3 pedestrian | 11:45 | #8 | 16.85 | pedestrian | 0.40 | 0 | 0.24 | away_from_camera | 1 |
| exp0_base | day | d4 pedestrian | 12:10 | #12 | 2.07 | pedestrian | 0.16 | 0 | 0.18 | static | 0 |
| exp0_base | day | d5 pedestrian | 12:10 | #13 | 1.2 | pedestrian | 0.22 | 0 | 0.18 | static | 0 |
| exp1_sahi | night | n1 cyclist | 4:02 | #4 | 1.2 | bicyclist | 0.97 | 94 | 4.82 | moving_right | 0 |
| exp1_sahi | night | n2 cyclist | 7:02 | #12 | 5.24 | bicyclist | 0.91 | 88 | 0.87 | moving_right | 1 |
| exp1_sahi | night | n3 cyclist | 14:21 | #18 | 3.47 | bicyclist | 0.62 | 49 | 1.23 | moving_right | 1 |
| exp1_sahi | night | n4 cyclist | 14:21 | #22 | 3.44 | pedestrian | 0.30 | 59 | 2.23 | moving_right | 1 |
| exp1_sahi | night | n5 cyclist | 14:21 | #21 | 2.37 | pedestrian | 0.39 | 31 | 2.37 | moving_right | 0 |
| exp1_sahi | night | n6 pedestrian | 14:47 | #23 | 10.58 | bicyclist | 0.67 | 69 | 0.48 | moving_right | 1 |
| exp1_sahi | day | d2 pedestrian | 3:00 | #2 | 20.69 | bicyclist | 0.73 | 6 | 0.56 | moving_left | 1 |
| exp1_sahi | day | d1 cyclist | 9:10 | #10 | 6.74 | bicyclist | 0.91 | 54 | 1.51 | moving_left | 1 |
| exp1_sahi | day | d3 pedestrian | 11:45 | #13 | 36.57 | bicyclist | 0.53 | 2 | 0.39 | moving_left | 1 |
| exp1_sahi | day | d4 pedestrian | 12:10 | #15 | 21.96 | pedestrian | 0.24 | 6 | 0.78 | moving_left | 1 |
| exp1_sahi | day | d5 pedestrian | 12:10 | #23 | 3.47 | pedestrian | 0.22 | 0 | 0.16 | static | 1 |
| b2_0_base | night_holdout_2200 | p2 pedestrian | 10:00 | #3 | 0.43 | pedestrian | 0.12 | 100 | 0.58 | moving_right | 0 |
| b2_0_base | day_holdout_1245 | h1 pedestrian | 0:40 | #1 | 9.11 | bicyclist | 0.65 | 45 | 0.69 | moving_left | 1 |
| b2_0_base | day_holdout_1245 | h2 cyclist | 8:07 | #4 | 3.67 | bicyclist | 0.79 | 46 | 0.99 | moving_right | 1 |
| b2_0_base | day_holdout_1245 | h3 cyclist | 8:46 | #6 | 6.97 | bicyclist | 0.79 | 45 | 1.24 | moving_right | 1 |
| b2_0_base | day_holdout_1245 | h4 pedestrian | 9:54 | #7 | 4.84 | pedestrian | 0.18 | 0 | 0.17 | static | 1 |
| b2_0_base | day_holdout_1245 | h5 pedestrian | 11:17 | #9 | 18.59 | bicyclist | 0.65 | 7 | 0.51 | away_from_camera | 1 |
| b2_2_sahi | night_holdout_2200 | p1 pedestrian | 6:00 | #18 | 10.48 | pedestrian | 0.29 | 24 | 0.65 | moving_right | 1 |
| b2_2_sahi | night_holdout_2200 | p2 pedestrian | 10:00 | #27 | 18.72 | pedestrian | 0.23 | 32 | 0.15 | moving_right | 1 |
| b2_2_sahi | night_holdout_2200 | p3 pedestrian | 10:59 | #33 | 14.98 | pedestrian | 0.35 | 43 | 0.30 | moving_right | 1 |
| b2_2_sahi | night_holdout_2200 | p4 pedestrian | 10:59 | #36 | 5.84 | pedestrian | 0.05 | 28 | 0.51 | toward_camera | 1 |
| b2_2_sahi | night_holdout_2200 | p5 pedestrian | 10:59 | #40 | 3.84 | pedestrian | 0.15 | 76 | 0.96 | moving_right | 1 |
| b2_2_sahi | day_holdout_1245 | h1 pedestrian | 0:40 | #1 | 15.48 | bicyclist | 0.57 | 26 | 0.74 | moving_left | 1 |
| b2_2_sahi | day_holdout_1245 | h2 cyclist | 8:07 | #7 | 8.17 | bicyclist | 0.85 | 44 | 1.59 | moving_right | 1 |
| b2_2_sahi | day_holdout_1245 | h3 cyclist | 8:46 | #9 | 9.68 | bicyclist | 0.82 | 57 | 1.51 | moving_right | 1 |
| b2_2_sahi | day_holdout_1245 | h4 pedestrian | 9:54 | #14 | 7.21 | pedestrian | 0.17 | 0 | 0.18 | static | 1 |
| b2_2_sahi | day_holdout_1245 | h5 pedestrian | 11:17 | #15 | 23.62 | bicyclist | 0.64 | 8 | 0.56 | away_from_camera | 1 |
| b2_3_sahi_fuse | night | n1 cyclist | 4:02 | #4 | 1.2 | bicyclist | 0.97 | 94 | 4.82 | moving_right | 0 |
| b2_3_sahi_fuse | night | n2 cyclist | 7:02 | #12 | 5.24 | bicyclist | 0.91 | 88 | 0.87 | moving_right | 1 |
| b2_3_sahi_fuse | night | n3 cyclist | 14:21 | #18 | 3.47 | bicyclist | 0.62 | 49 | 1.23 | moving_right | 1 |
| b2_3_sahi_fuse | night | n4 cyclist | 14:21 | #22 | 3.44 | pedestrian | 0.30 | 59 | 2.23 | moving_right | 1 |
| b2_3_sahi_fuse | night | n5 cyclist | 14:21 | #21 | 2.37 | pedestrian | 0.39 | 31 | 2.37 | moving_right | 0 |
| b2_3_sahi_fuse | night | n6 pedestrian | 14:47 | #23 | 10.58 | bicyclist | 0.67 | 69 | 0.48 | moving_right | 1 |
| b2_3_sahi_fuse | day | d2 pedestrian | 3:00 | #2 | 20.69 | bicyclist | 0.73 | 6 | 0.56 | moving_left | 1 |
| b2_3_sahi_fuse | day | d1 cyclist | 9:10 | #10 | 6.74 | bicyclist | 0.91 | 54 | 1.51 | moving_left | 1 |
| b2_3_sahi_fuse | day | d3 pedestrian | 11:45 | #13 | 36.57 | bicyclist | 0.53 | 2 | 0.39 | moving_left | 1 |
| b2_3_sahi_fuse | day | d4 pedestrian | 12:10 | #15 | 21.96 | pedestrian | 0.24 | 6 | 0.78 | moving_left | 1 |
| b2_3_sahi_fuse | day | d5 pedestrian | 12:10 | #23 | 3.47 | pedestrian | 0.22 | 0 | 0.16 | static | 1 |
| b2_3_sahi_fuse | night_holdout_2200 | p1 pedestrian | 6:00 | #18 | 10.48 | pedestrian | 0.29 | 24 | 0.65 | moving_right | 1 |
| b2_3_sahi_fuse | night_holdout_2200 | p2 pedestrian | 10:00 | #27 | 18.72 | pedestrian | 0.23 | 32 | 0.15 | moving_right | 1 |
| b2_3_sahi_fuse | night_holdout_2200 | p3 pedestrian | 10:59 | #33 | 14.98 | pedestrian | 0.35 | 43 | 0.30 | moving_right | 1 |
| b2_3_sahi_fuse | night_holdout_2200 | p4 pedestrian | 10:59 | #36 | 5.84 | pedestrian | 0.05 | 28 | 0.51 | toward_camera | 1 |
| b2_3_sahi_fuse | night_holdout_2200 | p5 pedestrian | 10:59 | #40 | 3.84 | pedestrian | 0.15 | 76 | 0.96 | moving_right | 1 |
| b2_3_sahi_fuse | day_holdout_1245 | h1 pedestrian | 0:40 | #1 | 15.48 | bicyclist | 0.57 | 26 | 0.74 | moving_left | 1 |
| b2_3_sahi_fuse | day_holdout_1245 | h2 cyclist | 8:07 | #7 | 8.17 | bicyclist | 0.85 | 44 | 1.59 | moving_right | 1 |
| b2_3_sahi_fuse | day_holdout_1245 | h3 cyclist | 8:46 | #9 | 9.68 | bicyclist | 0.82 | 57 | 1.51 | moving_right | 1 |
| b2_3_sahi_fuse | day_holdout_1245 | h4 pedestrian | 9:54 | #14 | 7.21 | pedestrian | 0.17 | 0 | 0.18 | static | 1 |
| b2_3_sahi_fuse | day_holdout_1245 | h5 pedestrian | 11:17 | #15 | 23.62 | bicyclist | 0.64 | 8 | 0.56 | away_from_camera | 1 |
| b2_4_sahi_fuse_nightshort | night | n1 cyclist | 4:02 | #4 | 1.2 | bicyclist | 0.97 | 94 | 4.82 | moving_right | 1 |
| b2_4_sahi_fuse_nightshort | night | n2 cyclist | 7:02 | #12 | 5.24 | bicyclist | 0.91 | 88 | 0.87 | moving_right | 1 |
| b2_4_sahi_fuse_nightshort | night | n3 cyclist | 14:21 | #18 | 3.47 | bicyclist | 0.62 | 49 | 1.23 | moving_right | 1 |
| b2_4_sahi_fuse_nightshort | night | n4 cyclist | 14:21 | #22 | 3.44 | pedestrian | 0.30 | 59 | 2.23 | moving_right | 1 |
| b2_4_sahi_fuse_nightshort | night | n5 cyclist | 14:21 | #21 | 2.37 | pedestrian | 0.39 | 31 | 2.37 | moving_right | 0 |
| b2_4_sahi_fuse_nightshort | night | n6 pedestrian | 14:47 | #23 | 10.58 | bicyclist | 0.67 | 69 | 0.48 | moving_right | 1 |
| b2_4_sahi_fuse_nightshort | day | d2 pedestrian | 3:00 | #2 | 20.69 | bicyclist | 0.73 | 6 | 0.56 | moving_left | 1 |
| b2_4_sahi_fuse_nightshort | day | d1 cyclist | 9:10 | #10 | 6.74 | bicyclist | 0.91 | 54 | 1.51 | moving_left | 1 |
| b2_4_sahi_fuse_nightshort | day | d3 pedestrian | 11:45 | #13 | 36.57 | bicyclist | 0.53 | 2 | 0.39 | moving_left | 1 |
| b2_4_sahi_fuse_nightshort | day | d4 pedestrian | 12:10 | #15 | 21.96 | pedestrian | 0.24 | 6 | 0.78 | moving_left | 1 |
| b2_4_sahi_fuse_nightshort | day | d5 pedestrian | 12:10 | #23 | 3.47 | pedestrian | 0.22 | 0 | 0.16 | static | 1 |
| b2_4_sahi_fuse_nightshort | night_holdout_2200 | p1 pedestrian | 6:00 | #18 | 10.48 | pedestrian | 0.29 | 24 | 0.65 | moving_right | 1 |
| b2_4_sahi_fuse_nightshort | night_holdout_2200 | p2 pedestrian | 10:00 | #27 | 18.72 | pedestrian | 0.23 | 32 | 0.15 | moving_right | 1 |
| b2_4_sahi_fuse_nightshort | night_holdout_2200 | p3 pedestrian | 10:59 | #33 | 14.98 | pedestrian | 0.35 | 43 | 0.30 | moving_right | 1 |
| b2_4_sahi_fuse_nightshort | night_holdout_2200 | p4 pedestrian | 10:59 | #36 | 5.84 | pedestrian | 0.05 | 28 | 0.51 | toward_camera | 1 |
| b2_4_sahi_fuse_nightshort | night_holdout_2200 | p5 pedestrian | 10:59 | #40 | 3.84 | pedestrian | 0.15 | 76 | 0.96 | moving_right | 1 |
| b2_4_sahi_fuse_nightshort | day_holdout_1245 | h1 pedestrian | 0:40 | #1 | 15.48 | bicyclist | 0.57 | 26 | 0.74 | moving_left | 1 |
| b2_4_sahi_fuse_nightshort | day_holdout_1245 | h2 cyclist | 8:07 | #7 | 8.17 | bicyclist | 0.85 | 44 | 1.59 | moving_right | 1 |
| b2_4_sahi_fuse_nightshort | day_holdout_1245 | h3 cyclist | 8:46 | #9 | 9.68 | bicyclist | 0.82 | 57 | 1.51 | moving_right | 1 |
| b2_4_sahi_fuse_nightshort | day_holdout_1245 | h4 pedestrian | 9:54 | #14 | 7.21 | pedestrian | 0.17 | 0 | 0.18 | static | 1 |
| b2_4_sahi_fuse_nightshort | day_holdout_1245 | h5 pedestrian | 11:17 | #15 | 23.62 | bicyclist | 0.64 | 8 | 0.56 | away_from_camera | 1 |
| b2_5_sahi_speed | night | n1 cyclist | 4:02 | #4 | 1.2 | bicyclist | 0.97 | 94 | 4.82 | moving_right | 0 |
| b2_5_sahi_speed | night | n2 cyclist | 7:02 | #12 | 5.24 | bicyclist | 0.91 | 88 | 0.87 | moving_right | 1 |
| b2_5_sahi_speed | night | n3 cyclist | 14:21 | #18 | 3.47 | bicyclist | 0.62 | 49 | 1.23 | moving_right | 1 |
| b2_5_sahi_speed | night | n4 cyclist | 14:21 | #22 | 3.44 | pedestrian | 0.30 | 59 | 2.23 | moving_right | 1 |
| b2_5_sahi_speed | night | n5 cyclist | 14:21 | #21 | 2.37 | pedestrian | 0.39 | 31 | 2.37 | moving_right | 0 |
| b2_5_sahi_speed | night | n6 pedestrian | 14:47 | #23 | 10.58 | bicyclist | 0.67 | 69 | 0.48 | moving_right | 1 |
| b2_5_sahi_speed | day | d2 pedestrian | 3:00 | #2 | 20.69 | bicyclist | 0.73 | 6 | 0.56 | moving_left | 1 |
| b2_5_sahi_speed | day | d1 cyclist | 9:10 | #10 | 6.74 | bicyclist | 0.91 | 54 | 1.51 | moving_left | 1 |
| b2_5_sahi_speed | day | d3 pedestrian | 11:45 | #13 | 36.57 | bicyclist | 0.53 | 2 | 0.39 | moving_left | 1 |
| b2_5_sahi_speed | day | d4 pedestrian | 12:10 | #15 | 21.96 | pedestrian | 0.24 | 6 | 0.78 | moving_left | 1 |
| b2_5_sahi_speed | day | d5 pedestrian | 12:10 | #23 | 3.47 | pedestrian | 0.22 | 0 | 0.16 | static | 1 |
| b2_5_sahi_speed | night_holdout_2200 | p1 pedestrian | 6:00 | #18 | 10.48 | pedestrian | 0.29 | 24 | 0.65 | moving_right | 1 |
| b2_5_sahi_speed | night_holdout_2200 | p2 pedestrian | 10:00 | #27 | 18.72 | pedestrian | 0.23 | 32 | 0.15 | moving_right | 1 |
| b2_5_sahi_speed | night_holdout_2200 | p3 pedestrian | 10:59 | #33 | 14.98 | pedestrian | 0.35 | 43 | 0.30 | moving_right | 1 |
| b2_5_sahi_speed | night_holdout_2200 | p4 pedestrian | 10:59 | #36 | 5.84 | pedestrian | 0.05 | 28 | 0.51 | toward_camera | 1 |
| b2_5_sahi_speed | night_holdout_2200 | p5 pedestrian | 10:59 | #40 | 3.84 | pedestrian | 0.15 | 76 | 0.96 | moving_right | 1 |
| b2_5_sahi_speed | day_holdout_1245 | h1 pedestrian | 0:40 | #1 | 15.48 | bicyclist | 0.57 | 26 | 0.74 | moving_left | 1 |
| b2_5_sahi_speed | day_holdout_1245 | h2 cyclist | 8:07 | #7 | 8.17 | bicyclist | 0.85 | 44 | 1.59 | moving_right | 1 |
| b2_5_sahi_speed | day_holdout_1245 | h3 cyclist | 8:46 | #9 | 9.68 | bicyclist | 0.82 | 57 | 1.51 | moving_right | 1 |
| b2_5_sahi_speed | day_holdout_1245 | h4 pedestrian | 9:54 | #14 | 7.21 | pedestrian | 0.17 | 0 | 0.18 | static | 1 |
| b2_5_sahi_speed | day_holdout_1245 | h5 pedestrian | 11:17 | #15 | 23.62 | bicyclist | 0.64 | 8 | 0.56 | away_from_camera | 1 |
| b3_combo | night | n1 cyclist | 4:02 | #4 | 1.2 | bicyclist | 0.97 | 94 | 4.82 | moving_right | 1 |
| b3_combo | night | n2 cyclist | 7:02 | #12 | 5.24 | bicyclist | 0.91 | 88 | 0.87 | moving_right | 1 |
| b3_combo | night | n3 cyclist | 14:21 | #18 | 3.47 | bicyclist | 0.62 | 49 | 1.23 | moving_right | 1 |
| b3_combo | night | n4 cyclist | 14:21 | #22 | 3.44 | pedestrian | 0.30 | 59 | 2.23 | moving_right | 1 |
| b3_combo | night | n5 cyclist | 14:21 | #21 | 2.37 | pedestrian | 0.39 | 31 | 2.37 | moving_right | 0 |
| b3_combo | night | n6 pedestrian | 14:47 | #23 | 10.58 | bicyclist | 0.67 | 69 | 0.48 | moving_right | 1 |
| b3_combo | day | d2 pedestrian | 3:00 | #2 | 20.69 | bicyclist | 0.73 | 6 | 0.56 | moving_left | 1 |
| b3_combo | day | d1 cyclist | 9:10 | #10 | 6.74 | bicyclist | 0.91 | 54 | 1.51 | moving_left | 1 |
| b3_combo | day | d3 pedestrian | 11:45 | #13 | 36.57 | bicyclist | 0.53 | 2 | 0.39 | moving_left | 1 |
| b3_combo | day | d4 pedestrian | 12:10 | #15 | 21.96 | pedestrian | 0.24 | 6 | 0.78 | moving_left | 1 |
| b3_combo | day | d5 pedestrian | 12:10 | #23 | 3.47 | pedestrian | 0.22 | 0 | 0.16 | static | 1 |
| b3_combo | night_holdout_2200 | p1 pedestrian | 6:00 | #18 | 10.48 | pedestrian | 0.29 | 24 | 0.65 | moving_right | 1 |
| b3_combo | night_holdout_2200 | p2 pedestrian | 10:00 | #27 | 18.72 | pedestrian | 0.23 | 32 | 0.15 | moving_right | 1 |
| b3_combo | night_holdout_2200 | p3 pedestrian | 10:59 | #33 | 14.98 | pedestrian | 0.35 | 43 | 0.30 | moving_right | 1 |
| b3_combo | night_holdout_2200 | p4 pedestrian | 10:59 | #36 | 5.84 | pedestrian | 0.05 | 28 | 0.51 | toward_camera | 1 |
| b3_combo | night_holdout_2200 | p5 pedestrian | 10:59 | #40 | 3.84 | pedestrian | 0.15 | 76 | 0.96 | moving_right | 1 |
| b3_combo | day_holdout_1245 | h1 pedestrian | 0:40 | #1 | 15.48 | bicyclist | 0.57 | 26 | 0.74 | moving_left | 1 |
| b3_combo | day_holdout_1245 | h2 cyclist | 8:07 | #7 | 8.17 | bicyclist | 0.85 | 44 | 1.59 | moving_right | 1 |
| b3_combo | day_holdout_1245 | h3 cyclist | 8:46 | #9 | 9.68 | bicyclist | 0.82 | 57 | 1.51 | moving_right | 1 |
| b3_combo | day_holdout_1245 | h4 pedestrian | 9:54 | #14 | 7.21 | pedestrian | 0.17 | 0 | 0.18 | static | 1 |
| b3_combo | day_holdout_1245 | h5 pedestrian | 11:17 | #15 | 23.62 | bicyclist | 0.64 | 8 | 0.56 | away_from_camera | 1 |

## Rules replayed on 119 (person, run) pairs

| rule | right | of | labels it changes |
|---|---|---|---|
| X-CLIP alone (now) | 82 | 119 | |
| veto 5% | 87 | 119 | exp1_sahi/day/d3(ok), b2_3_sahi_fuse/day/d3(ok), b2_4_sahi_fuse_nightshort/day/d3(ok), b2_5_sahi_speed/day/d3(ok), b3_combo/day/d3(ok) |
| veto 10% | 98 | 119 | exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok), b2_0_base/day_holdout_1245/h5(ok), b2_2_sahi/day_holdout_1245/h5(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h5(ok), b2_4_sahi_fuse_nightshort/day/d2(ok), b2_4_sahi_fuse_nightshort/day/d3(ok), b2_4_sahi_fuse_nightshort/day_holdout_1245/h5(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h5(ok), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h5(ok) |
| veto 15% | 98 | 119 | exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok), b2_0_base/day_holdout_1245/h5(ok), b2_2_sahi/day_holdout_1245/h5(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h5(ok), b2_4_sahi_fuse_nightshort/day/d2(ok), b2_4_sahi_fuse_nightshort/day/d3(ok), b2_4_sahi_fuse_nightshort/day_holdout_1245/h5(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h5(ok), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h5(ok) |
| veto 20% | 98 | 119 | exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok), b2_0_base/day_holdout_1245/h5(ok), b2_2_sahi/day_holdout_1245/h5(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h5(ok), b2_4_sahi_fuse_nightshort/day/d2(ok), b2_4_sahi_fuse_nightshort/day/d3(ok), b2_4_sahi_fuse_nightshort/day_holdout_1245/h5(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h5(ok), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h5(ok) |
| veto 30% | 103 | 119 | exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok), b2_0_base/day_holdout_1245/h5(ok), b2_2_sahi/day_holdout_1245/h1(ok), b2_2_sahi/day_holdout_1245/h5(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h1(ok), b2_3_sahi_fuse/day_holdout_1245/h5(ok), b2_4_sahi_fuse_nightshort/day/d2(ok), b2_4_sahi_fuse_nightshort/day/d3(ok), b2_4_sahi_fuse_nightshort/day_holdout_1245/h1(ok), b2_4_sahi_fuse_nightshort/day_holdout_1245/h5(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h1(ok), b2_5_sahi_speed/day_holdout_1245/h5(ok), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b3_combo/day_holdout_1245/h5(ok) |
| veto 40% | 102 | 119 | exp0_base/day/d1(WRONG), exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok), b2_0_base/day_holdout_1245/h5(ok), b2_2_sahi/day_holdout_1245/h1(ok), b2_2_sahi/day_holdout_1245/h5(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h1(ok), b2_3_sahi_fuse/day_holdout_1245/h5(ok), b2_4_sahi_fuse_nightshort/day/d2(ok), b2_4_sahi_fuse_nightshort/day/d3(ok), b2_4_sahi_fuse_nightshort/day_holdout_1245/h1(ok), b2_4_sahi_fuse_nightshort/day_holdout_1245/h5(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h1(ok), b2_5_sahi_speed/day_holdout_1245/h5(ok), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b3_combo/day_holdout_1245/h5(ok) |
| veto 50% | 91 | 119 | exp0_base/day/d1(WRONG), exp1_sahi/night/n3(WRONG), exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok), b2_0_base/day_holdout_1245/h1(ok), b2_0_base/day_holdout_1245/h2(WRONG), b2_0_base/day_holdout_1245/h3(WRONG), b2_0_base/day_holdout_1245/h5(ok), b2_2_sahi/day_holdout_1245/h1(ok), b2_2_sahi/day_holdout_1245/h2(WRONG), b2_2_sahi/day_holdout_1245/h5(ok), b2_3_sahi_fuse/night/n3(WRONG), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h1(ok), b2_3_sahi_fuse/day_holdout_1245/h2(WRONG), b2_3_sahi_fuse/day_holdout_1245/h5(ok), b2_4_sahi_fuse_nightshort/night/n3(WRONG), b2_4_sahi_fuse_nightshort/day/d2(ok), b2_4_sahi_fuse_nightshort/day/d3(ok), b2_4_sahi_fuse_nightshort/day_holdout_1245/h1(ok), b2_4_sahi_fuse_nightshort/day_holdout_1245/h2(WRONG), b2_4_sahi_fuse_nightshort/day_holdout_1245/h5(ok), b2_5_sahi_speed/night/n3(WRONG), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h1(ok), b2_5_sahi_speed/day_holdout_1245/h2(WRONG), b2_5_sahi_speed/day_holdout_1245/h5(ok), b3_combo/night/n3(WRONG), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b3_combo/day_holdout_1245/h2(WRONG), b3_combo/day_holdout_1245/h5(ok) |
| promote 80% | 81 | 119 | b2_0_base/night_holdout_2200/p2(WRONG) |
| promote 90% | 81 | 119 | b2_0_base/night_holdout_2200/p2(WRONG) |
| promote 95% | 81 | 119 | b2_0_base/night_holdout_2200/p2(WRONG) |
| speed lateral walk<0.8 ride>2.0 | 103 | 119 | exp1_sahi/night/n4(ok), exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok), b2_0_base/day_holdout_1245/h1(ok), b2_2_sahi/day_holdout_1245/h1(ok), b2_3_sahi_fuse/night/n4(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h1(ok), b2_4_sahi_fuse_nightshort/night/n4(ok), b2_4_sahi_fuse_nightshort/day/d2(ok), b2_4_sahi_fuse_nightshort/day/d3(ok), b2_4_sahi_fuse_nightshort/day_holdout_1245/h1(ok), b2_5_sahi_speed/night/n4(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h1(ok), b3_combo/night/n4(ok), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok) |
| speed lateral walk<1.0 ride>2.0 | 101 | 119 | exp0_base/day/d1(WRONG), exp1_sahi/night/n4(ok), exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok), b2_0_base/day_holdout_1245/h1(ok), b2_0_base/day_holdout_1245/h2(WRONG), b2_2_sahi/day_holdout_1245/h1(ok), b2_3_sahi_fuse/night/n4(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h1(ok), b2_4_sahi_fuse_nightshort/night/n4(ok), b2_4_sahi_fuse_nightshort/day/d2(ok), b2_4_sahi_fuse_nightshort/day/d3(ok), b2_4_sahi_fuse_nightshort/day_holdout_1245/h1(ok), b2_5_sahi_speed/night/n4(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h1(ok), b3_combo/night/n4(ok), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok) |
| speed lateral walk<1.2 ride>2.5 | 96 | 119 | exp0_base/day/d1(WRONG), exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok), b2_0_base/day_holdout_1245/h1(ok), b2_0_base/day_holdout_1245/h2(WRONG), b2_2_sahi/day_holdout_1245/h1(ok), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h1(ok), b2_4_sahi_fuse_nightshort/day/d2(ok), b2_4_sahi_fuse_nightshort/day/d3(ok), b2_4_sahi_fuse_nightshort/day_holdout_1245/h1(ok), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h1(ok), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok) |
| speed lateral walk<1.5 ride>3.0 | 90 | 119 | exp0_base/day/d1(WRONG), exp1_sahi/night/n3(WRONG), exp1_sahi/day/d2(ok), exp1_sahi/day/d3(ok), b2_0_base/day_holdout_1245/h1(ok), b2_0_base/day_holdout_1245/h2(WRONG), b2_0_base/day_holdout_1245/h3(WRONG), b2_2_sahi/day_holdout_1245/h1(ok), b2_3_sahi_fuse/night/n3(WRONG), b2_3_sahi_fuse/day/d2(ok), b2_3_sahi_fuse/day/d3(ok), b2_3_sahi_fuse/day_holdout_1245/h1(ok), b2_4_sahi_fuse_nightshort/night/n3(WRONG), b2_4_sahi_fuse_nightshort/day/d2(ok), b2_4_sahi_fuse_nightshort/day/d3(ok), b2_4_sahi_fuse_nightshort/day_holdout_1245/h1(ok), b2_5_sahi_speed/night/n3(WRONG), b2_5_sahi_speed/day/d2(ok), b2_5_sahi_speed/day/d3(ok), b2_5_sahi_speed/day_holdout_1245/h1(ok), b3_combo/night/n3(WRONG), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok) |

Read the per-row table first: do real riders and real walkers separate on speed (lateral tracks) or on det %cyc? A rule that only 'wins' by changing one or two rows is a coincidence.

## Counted tracks that match NO truth person (false detections, or a person missing from the truth file)

| run | clip | when | track | secs | X-CLIP | wBIC | det %cyc | speed h/s | net px | direction |
|---|---|---|---|---|---|---|---|---|---|---|
| b2_2_sahi | night_holdout_2200 | 7:50-8:27 | #24 | 4.97 | pedestrian | 0.31 | 0 | 0.01 | 0 | static |
| b2_2_sahi | night_holdout_2200 | 8:32-9:00 | #26 | 3.8 | pedestrian | 0.26 | 0 | 0.01 | 2 | static |
| b2_3_sahi_fuse | night_holdout_2200 | 7:50-8:27 | #24 | 4.97 | pedestrian | 0.31 | 0 | 0.01 | 0 | static |
| b2_3_sahi_fuse | night_holdout_2200 | 8:32-9:00 | #26 | 3.8 | pedestrian | 0.26 | 0 | 0.01 | 2 | static |
| b2_4_sahi_fuse_nightshort | night_holdout_2200 | 7:50-8:27 | #24 | 4.97 | pedestrian | 0.31 | 0 | 0.01 | 0 | static |
| b2_4_sahi_fuse_nightshort | night_holdout_2200 | 8:32-9:00 | #26 | 3.8 | pedestrian | 0.26 | 0 | 0.01 | 2 | static |
| b2_5_sahi_speed | night_holdout_2200 | 7:50-8:27 | #24 | 4.97 | pedestrian | 0.31 | 0 | 0.01 | 0 | static |
| b2_5_sahi_speed | night_holdout_2200 | 8:32-9:00 | #26 | 3.8 | pedestrian | 0.26 | 0 | 0.01 | 2 | static |
| b3_combo | night_holdout_2200 | 7:50-8:27 | #24 | 4.97 | pedestrian | 0.31 | 0 | 0.01 | 0 | static |
| b3_combo | night_holdout_2200 | 8:32-9:00 | #26 | 3.8 | pedestrian | 0.26 | 0 | 0.01 | 2 | static |

A static object (barricade, sign) tracked as a person should show a tiny net movement and speed; compare with the real people above before choosing a filter.

<a id="report-fusion-batch4-20261011-1355"></a>
## FUSION_batch4_20261011_1355.md
Original location: `vision3/best/test_colonial/exp_results/FUSION_batch4_20261011_1355.md`.

# Fusion probe

runs: exp0_base,b2_2_sahi,b3_combo,b4_combo_disp5

| run | clip | truth | when | track | secs | X-CLIP | wBIC | det %cyc | speed h/s | net px | direction | counted |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| exp0_base | night | n1 cyclist | 4:02 | #1 | 0.6 | bicyclist | 0.95 | 100 | 2.64 | 81 | moving_right | 0 |
| exp0_base | night | n2 cyclist | 7:02 | #2 | 0.43 | bicyclist | 0.99 | 100 | 0.79 | 181 | moving_right | 0 |
| exp0_base | night | n3 cyclist | 14:21 | #4 | 0.9 | bicyclist | 0.70 | 59 | 1.30 | 133 | toward_camera | 0 |
| exp0_base | day | d2 pedestrian | 3:00 | #3 | 3.2 | pedestrian | 0.21 | 0 | 0.15 | 13 | static | 1 |
| exp0_base | day | d1 cyclist | 9:10 | #5 | 4.04 | bicyclist | 0.92 | 35 | 0.97 | 347 | moving_left | 1 |
| exp0_base | day | d3 pedestrian | 11:45 | #8 | 16.85 | pedestrian | 0.40 | 0 | 0.24 | 234 | away_from_camera | 1 |
| exp0_base | day | d4 pedestrian | 12:10 | #12 | 2.07 | pedestrian | 0.16 | 0 | 0.18 | 16 | static | 0 |
| exp0_base | day | d5 pedestrian | 12:10 | #13 | 1.2 | pedestrian | 0.22 | 0 | 0.18 | 13 | static | 0 |
| b2_2_sahi | night_holdout_2200 | p1 pedestrian | 6:00 | #18 | 10.48 | pedestrian | 0.29 | 24 | 0.65 | 518 | moving_right | 1 |
| b2_2_sahi | night_holdout_2200 | p2 pedestrian | 10:00 | #27 | 18.72 | pedestrian | 0.23 | 32 | 0.15 | 516 | moving_right | 1 |
| b2_2_sahi | night_holdout_2200 | p3 pedestrian | 10:59 | #33 | 14.98 | pedestrian | 0.35 | 43 | 0.30 | 526 | moving_right | 1 |
| b2_2_sahi | night_holdout_2200 | p4 pedestrian | 10:59 | #36 | 5.84 | pedestrian | 0.05 | 28 | 0.51 | 416 | toward_camera | 1 |
| b2_2_sahi | night_holdout_2200 | p5 pedestrian | 10:59 | #40 | 3.84 | pedestrian | 0.15 | 76 | 0.96 | 344 | moving_right | 1 |
| b2_2_sahi | day_holdout_1245 | h1 pedestrian | 0:40 | #1 | 15.48 | bicyclist | 0.57 | 26 | 0.74 | 678 | moving_left | 1 |
| b2_2_sahi | day_holdout_1245 | h2 cyclist | 8:07 | #7 | 8.17 | bicyclist | 0.85 | 44 | 1.59 | 730 | moving_right | 1 |
| b2_2_sahi | day_holdout_1245 | h3 cyclist | 8:46 | #9 | 9.68 | bicyclist | 0.82 | 57 | 1.51 | 733 | moving_right | 1 |
| b2_2_sahi | day_holdout_1245 | h4 pedestrian | 9:54 | #14 | 7.21 | pedestrian | 0.17 | 0 | 0.18 | 30 | static | 1 |
| b2_2_sahi | day_holdout_1245 | h5 pedestrian | 11:17 | #15 | 23.62 | bicyclist | 0.64 | 8 | 0.56 | 460 | away_from_camera | 1 |
| b3_combo | night | n1 cyclist | 4:02 | #4 | 1.2 | bicyclist | 0.97 | 94 | 4.82 | 560 | moving_right | 1 |
| b3_combo | night | n2 cyclist | 7:02 | #12 | 5.24 | bicyclist | 0.91 | 88 | 0.87 | 706 | moving_right | 1 |
| b3_combo | night | n3 cyclist | 14:21 | #18 | 3.47 | bicyclist | 0.62 | 49 | 1.23 | 499 | moving_right | 1 |
| b3_combo | night | n4 cyclist | 14:21 | #22 | 3.44 | pedestrian | 0.30 | 59 | 2.23 | 458 | moving_right | 1 |
| b3_combo | night | n5 cyclist | 14:21 | #21 | 2.37 | pedestrian | 0.39 | 31 | 2.37 | 437 | moving_right | 0 |
| b3_combo | night | n6 pedestrian | 14:47 | #23 | 10.58 | bicyclist | 0.67 | 69 | 0.48 | 526 | moving_right | 1 |
| b3_combo | day | d2 pedestrian | 3:00 | #2 | 20.69 | bicyclist | 0.73 | 6 | 0.56 | 593 | moving_left | 1 |
| b3_combo | day | d1 cyclist | 9:10 | #10 | 6.74 | bicyclist | 0.91 | 54 | 1.51 | 749 | moving_left | 1 |
| b3_combo | day | d3 pedestrian | 11:45 | #13 | 36.57 | bicyclist | 0.53 | 2 | 0.39 | 499 | moving_left | 1 |
| b3_combo | day | d4 pedestrian | 12:10 | #15 | 21.96 | pedestrian | 0.24 | 6 | 0.78 | 628 | moving_left | 1 |
| b3_combo | day | d5 pedestrian | 12:10 | #23 | 3.47 | pedestrian | 0.22 | 0 | 0.16 | 17 | static | 1 |
| b3_combo | night_holdout_2200 | p1 pedestrian | 6:00 | #18 | 10.48 | pedestrian | 0.29 | 24 | 0.65 | 518 | moving_right | 1 |
| b3_combo | night_holdout_2200 | p2 pedestrian | 10:00 | #27 | 18.72 | pedestrian | 0.23 | 32 | 0.15 | 516 | moving_right | 1 |
| b3_combo | night_holdout_2200 | p3 pedestrian | 10:59 | #33 | 14.98 | pedestrian | 0.35 | 43 | 0.30 | 526 | moving_right | 1 |
| b3_combo | night_holdout_2200 | p4 pedestrian | 10:59 | #36 | 5.84 | pedestrian | 0.05 | 28 | 0.51 | 416 | toward_camera | 1 |
| b3_combo | night_holdout_2200 | p5 pedestrian | 10:59 | #40 | 3.84 | pedestrian | 0.15 | 76 | 0.96 | 344 | moving_right | 1 |
| b3_combo | day_holdout_1245 | h1 pedestrian | 0:40 | #1 | 15.48 | bicyclist | 0.57 | 26 | 0.74 | 678 | moving_left | 1 |
| b3_combo | day_holdout_1245 | h2 cyclist | 8:07 | #7 | 8.17 | bicyclist | 0.85 | 44 | 1.59 | 730 | moving_right | 1 |
| b3_combo | day_holdout_1245 | h3 cyclist | 8:46 | #9 | 9.68 | bicyclist | 0.82 | 57 | 1.51 | 733 | moving_right | 1 |
| b3_combo | day_holdout_1245 | h4 pedestrian | 9:54 | #14 | 7.21 | pedestrian | 0.17 | 0 | 0.18 | 30 | static | 1 |
| b3_combo | day_holdout_1245 | h5 pedestrian | 11:17 | #15 | 23.62 | bicyclist | 0.64 | 8 | 0.56 | 460 | away_from_camera | 1 |
| b4_combo_disp5 | night | n1 cyclist | 4:02 | #4 | 1.2 | bicyclist | 0.97 | 94 | 4.82 | 560 | moving_right | 1 |
| b4_combo_disp5 | night | n2 cyclist | 7:02 | #12 | 5.24 | bicyclist | 0.91 | 88 | 0.87 | 706 | moving_right | 1 |
| b4_combo_disp5 | night | n3 cyclist | 14:21 | #18 | 3.47 | bicyclist | 0.62 | 49 | 1.23 | 499 | moving_right | 1 |
| b4_combo_disp5 | night | n4 cyclist | 14:21 | #22 | 3.44 | pedestrian | 0.30 | 59 | 2.23 | 458 | moving_right | 1 |
| b4_combo_disp5 | night | n5 cyclist | 14:21 | #21 | 2.37 | pedestrian | 0.39 | 31 | 2.37 | 437 | moving_right | 0 |
| b4_combo_disp5 | night | n6 pedestrian | 14:47 | #23 | 10.58 | bicyclist | 0.67 | 69 | 0.48 | 526 | moving_right | 1 |
| b4_combo_disp5 | day | d2 pedestrian | 3:00 | #2 | 20.69 | bicyclist | 0.73 | 6 | 0.56 | 593 | moving_left | 1 |
| b4_combo_disp5 | day | d1 cyclist | 9:10 | #10 | 6.74 | bicyclist | 0.91 | 54 | 1.51 | 749 | moving_left | 1 |
| b4_combo_disp5 | day | d3 pedestrian | 11:45 | #13 | 36.57 | bicyclist | 0.53 | 2 | 0.39 | 499 | moving_left | 1 |
| b4_combo_disp5 | day | d4 pedestrian | 12:10 | #15 | 21.96 | pedestrian | 0.24 | 6 | 0.78 | 628 | moving_left | 1 |
| b4_combo_disp5 | day | d5 pedestrian | 12:10 | #23 | 3.47 | pedestrian | 0.22 | 0 | 0.16 | 17 | static | 1 |
| b4_combo_disp5 | night_holdout_2200 | p1 pedestrian | 6:00 | #18 | 10.48 | pedestrian | 0.29 | 24 | 0.65 | 518 | moving_right | 1 |
| b4_combo_disp5 | night_holdout_2200 | p2 pedestrian | 10:00 | #27 | 18.72 | pedestrian | 0.23 | 32 | 0.15 | 516 | moving_right | 1 |
| b4_combo_disp5 | night_holdout_2200 | p3 pedestrian | 10:59 | #33 | 14.98 | pedestrian | 0.35 | 43 | 0.30 | 526 | moving_right | 1 |
| b4_combo_disp5 | night_holdout_2200 | p4 pedestrian | 10:59 | #36 | 5.84 | pedestrian | 0.05 | 28 | 0.51 | 416 | toward_camera | 1 |
| b4_combo_disp5 | night_holdout_2200 | p5 pedestrian | 10:59 | #40 | 3.84 | pedestrian | 0.15 | 76 | 0.96 | 344 | moving_right | 1 |
| b4_combo_disp5 | day_holdout_1245 | h1 pedestrian | 0:40 | #1 | 15.48 | bicyclist | 0.57 | 26 | 0.74 | 678 | moving_left | 1 |
| b4_combo_disp5 | day_holdout_1245 | h2 cyclist | 8:07 | #7 | 8.17 | bicyclist | 0.85 | 44 | 1.59 | 730 | moving_right | 1 |
| b4_combo_disp5 | day_holdout_1245 | h3 cyclist | 8:46 | #9 | 9.68 | bicyclist | 0.82 | 57 | 1.51 | 733 | moving_right | 1 |
| b4_combo_disp5 | day_holdout_1245 | h4 pedestrian | 9:54 | #14 | 7.21 | pedestrian | 0.17 | 0 | 0.18 | 30 | static | 1 |
| b4_combo_disp5 | day_holdout_1245 | h5 pedestrian | 11:17 | #15 | 23.62 | bicyclist | 0.64 | 8 | 0.56 | 460 | away_from_camera | 1 |

## Rules replayed on 60 (person, run) pairs

| rule | right | of | labels it changes |
|---|---|---|---|
| X-CLIP alone (now) | 44 | 60 | |
| veto 5% | 46 | 60 | b3_combo/day/d3(ok), b4_combo_disp5/day/d3(ok) |
| veto 10% | 51 | 60 | b2_2_sahi/day_holdout_1245/h5(ok), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h5(ok), b4_combo_disp5/day/d2(ok), b4_combo_disp5/day/d3(ok), b4_combo_disp5/day_holdout_1245/h5(ok) |
| veto 15% | 51 | 60 | b2_2_sahi/day_holdout_1245/h5(ok), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h5(ok), b4_combo_disp5/day/d2(ok), b4_combo_disp5/day/d3(ok), b4_combo_disp5/day_holdout_1245/h5(ok) |
| veto 20% | 51 | 60 | b2_2_sahi/day_holdout_1245/h5(ok), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h5(ok), b4_combo_disp5/day/d2(ok), b4_combo_disp5/day/d3(ok), b4_combo_disp5/day_holdout_1245/h5(ok) |
| veto 30% | 54 | 60 | b2_2_sahi/day_holdout_1245/h1(ok), b2_2_sahi/day_holdout_1245/h5(ok), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b3_combo/day_holdout_1245/h5(ok), b4_combo_disp5/day/d2(ok), b4_combo_disp5/day/d3(ok), b4_combo_disp5/day_holdout_1245/h1(ok), b4_combo_disp5/day_holdout_1245/h5(ok) |
| veto 40% | 53 | 60 | exp0_base/day/d1(WRONG), b2_2_sahi/day_holdout_1245/h1(ok), b2_2_sahi/day_holdout_1245/h5(ok), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b3_combo/day_holdout_1245/h5(ok), b4_combo_disp5/day/d2(ok), b4_combo_disp5/day/d3(ok), b4_combo_disp5/day_holdout_1245/h1(ok), b4_combo_disp5/day_holdout_1245/h5(ok) |
| veto 50% | 48 | 60 | exp0_base/day/d1(WRONG), b2_2_sahi/day_holdout_1245/h1(ok), b2_2_sahi/day_holdout_1245/h2(WRONG), b2_2_sahi/day_holdout_1245/h5(ok), b3_combo/night/n3(WRONG), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b3_combo/day_holdout_1245/h2(WRONG), b3_combo/day_holdout_1245/h5(ok), b4_combo_disp5/night/n3(WRONG), b4_combo_disp5/day/d2(ok), b4_combo_disp5/day/d3(ok), b4_combo_disp5/day_holdout_1245/h1(ok), b4_combo_disp5/day_holdout_1245/h2(WRONG), b4_combo_disp5/day_holdout_1245/h5(ok) |
| promote 80% | 44 | 60 | - |
| promote 90% | 44 | 60 | - |
| promote 95% | 44 | 60 | - |
| speed lateral walk<0.8 ride>2.0 | 53 | 60 | b2_2_sahi/day_holdout_1245/h1(ok), b3_combo/night/n4(ok), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b4_combo_disp5/night/n4(ok), b4_combo_disp5/day/d2(ok), b4_combo_disp5/day/d3(ok), b4_combo_disp5/day_holdout_1245/h1(ok) |
| speed lateral walk<1.0 ride>2.0 | 52 | 60 | exp0_base/day/d1(WRONG), b2_2_sahi/day_holdout_1245/h1(ok), b3_combo/night/n4(ok), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b4_combo_disp5/night/n4(ok), b4_combo_disp5/day/d2(ok), b4_combo_disp5/day/d3(ok), b4_combo_disp5/day_holdout_1245/h1(ok) |
| speed lateral walk<1.2 ride>2.5 | 50 | 60 | exp0_base/day/d1(WRONG), b2_2_sahi/day_holdout_1245/h1(ok), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b4_combo_disp5/day/d2(ok), b4_combo_disp5/day/d3(ok), b4_combo_disp5/day_holdout_1245/h1(ok) |
| speed lateral walk<1.5 ride>3.0 | 48 | 60 | exp0_base/day/d1(WRONG), b2_2_sahi/day_holdout_1245/h1(ok), b3_combo/night/n3(WRONG), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b4_combo_disp5/night/n3(WRONG), b4_combo_disp5/day/d2(ok), b4_combo_disp5/day/d3(ok), b4_combo_disp5/day_holdout_1245/h1(ok) |

Read the per-row table first: do real riders and real walkers separate on speed (lateral tracks) or on det %cyc? A rule that only 'wins' by changing one or two rows is a coincidence.

## Counted tracks that match NO truth person (false detections, or a person missing from the truth file)

| run | clip | when | track | secs | X-CLIP | wBIC | det %cyc | speed h/s | net px | direction |
|---|---|---|---|---|---|---|---|---|---|---|
| b2_2_sahi | night_holdout_2200 | 7:50-8:27 | #24 | 4.97 | pedestrian | 0.31 | 0 | 0.01 | 0 | static |
| b2_2_sahi | night_holdout_2200 | 8:32-9:00 | #26 | 3.8 | pedestrian | 0.26 | 0 | 0.01 | 2 | static |
| b3_combo | night_holdout_2200 | 7:50-8:27 | #24 | 4.97 | pedestrian | 0.31 | 0 | 0.01 | 0 | static |
| b3_combo | night_holdout_2200 | 8:32-9:00 | #26 | 3.8 | pedestrian | 0.26 | 0 | 0.01 | 2 | static |

A static object (barricade, sign) tracked as a person should show a tiny net movement and speed; compare with the real people above before choosing a filter.

<a id="report-fusion-batch4-20261011-1410"></a>
## FUSION_batch4_20261011_1410.md
Original location: `vision3/best/test_colonial/exp_results/FUSION_batch4_20261011_1410.md`.

# Fusion probe

runs: exp0_base,b2_2_sahi,b3_combo,b4_combo_static5

| run | clip | truth | when | track | secs | X-CLIP | wBIC | det %cyc | speed h/s | net px | direction | counted |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| exp0_base | night | n1 cyclist | 4:02 | #1 | 0.6 | bicyclist | 0.95 | 100 | 2.64 | 81 | moving_right | 0 |
| exp0_base | night | n2 cyclist | 7:02 | #2 | 0.43 | bicyclist | 0.99 | 100 | 0.79 | 181 | moving_right | 0 |
| exp0_base | night | n3 cyclist | 14:21 | #4 | 0.9 | bicyclist | 0.70 | 59 | 1.30 | 133 | toward_camera | 0 |
| exp0_base | day | d2 pedestrian | 3:00 | #3 | 3.2 | pedestrian | 0.21 | 0 | 0.15 | 13 | static | 1 |
| exp0_base | day | d1 cyclist | 9:10 | #5 | 4.04 | bicyclist | 0.92 | 35 | 0.97 | 347 | moving_left | 1 |
| exp0_base | day | d3 pedestrian | 11:45 | #8 | 16.85 | pedestrian | 0.40 | 0 | 0.24 | 234 | away_from_camera | 1 |
| exp0_base | day | d4 pedestrian | 12:10 | #12 | 2.07 | pedestrian | 0.16 | 0 | 0.18 | 16 | static | 0 |
| exp0_base | day | d5 pedestrian | 12:10 | #13 | 1.2 | pedestrian | 0.22 | 0 | 0.18 | 13 | static | 0 |
| b2_2_sahi | night_holdout_2200 | p1 pedestrian | 6:00 | #18 | 10.48 | pedestrian | 0.29 | 24 | 0.65 | 518 | moving_right | 1 |
| b2_2_sahi | night_holdout_2200 | p2 pedestrian | 10:00 | #27 | 18.72 | pedestrian | 0.23 | 32 | 0.15 | 516 | moving_right | 1 |
| b2_2_sahi | night_holdout_2200 | p3 pedestrian | 10:59 | #33 | 14.98 | pedestrian | 0.35 | 43 | 0.30 | 526 | moving_right | 1 |
| b2_2_sahi | night_holdout_2200 | p4 pedestrian | 10:59 | #36 | 5.84 | pedestrian | 0.05 | 28 | 0.51 | 416 | toward_camera | 1 |
| b2_2_sahi | night_holdout_2200 | p5 pedestrian | 10:59 | #40 | 3.84 | pedestrian | 0.15 | 76 | 0.96 | 344 | moving_right | 1 |
| b2_2_sahi | day_holdout_1245 | h1 pedestrian | 0:40 | #1 | 15.48 | bicyclist | 0.57 | 26 | 0.74 | 678 | moving_left | 1 |
| b2_2_sahi | day_holdout_1245 | h2 cyclist | 8:07 | #7 | 8.17 | bicyclist | 0.85 | 44 | 1.59 | 730 | moving_right | 1 |
| b2_2_sahi | day_holdout_1245 | h3 cyclist | 8:46 | #9 | 9.68 | bicyclist | 0.82 | 57 | 1.51 | 733 | moving_right | 1 |
| b2_2_sahi | day_holdout_1245 | h4 pedestrian | 9:54 | #14 | 7.21 | pedestrian | 0.17 | 0 | 0.18 | 30 | static | 1 |
| b2_2_sahi | day_holdout_1245 | h5 pedestrian | 11:17 | #15 | 23.62 | bicyclist | 0.64 | 8 | 0.56 | 460 | away_from_camera | 1 |
| b3_combo | night | n1 cyclist | 4:02 | #4 | 1.2 | bicyclist | 0.97 | 94 | 4.82 | 560 | moving_right | 1 |
| b3_combo | night | n2 cyclist | 7:02 | #12 | 5.24 | bicyclist | 0.91 | 88 | 0.87 | 706 | moving_right | 1 |
| b3_combo | night | n3 cyclist | 14:21 | #18 | 3.47 | bicyclist | 0.62 | 49 | 1.23 | 499 | moving_right | 1 |
| b3_combo | night | n4 cyclist | 14:21 | #22 | 3.44 | pedestrian | 0.30 | 59 | 2.23 | 458 | moving_right | 1 |
| b3_combo | night | n5 cyclist | 14:21 | #21 | 2.37 | pedestrian | 0.39 | 31 | 2.37 | 437 | moving_right | 0 |
| b3_combo | night | n6 pedestrian | 14:47 | #23 | 10.58 | bicyclist | 0.67 | 69 | 0.48 | 526 | moving_right | 1 |
| b3_combo | day | d2 pedestrian | 3:00 | #2 | 20.69 | bicyclist | 0.73 | 6 | 0.56 | 593 | moving_left | 1 |
| b3_combo | day | d1 cyclist | 9:10 | #10 | 6.74 | bicyclist | 0.91 | 54 | 1.51 | 749 | moving_left | 1 |
| b3_combo | day | d3 pedestrian | 11:45 | #13 | 36.57 | bicyclist | 0.53 | 2 | 0.39 | 499 | moving_left | 1 |
| b3_combo | day | d4 pedestrian | 12:10 | #15 | 21.96 | pedestrian | 0.24 | 6 | 0.78 | 628 | moving_left | 1 |
| b3_combo | day | d5 pedestrian | 12:10 | #23 | 3.47 | pedestrian | 0.22 | 0 | 0.16 | 17 | static | 1 |
| b3_combo | night_holdout_2200 | p1 pedestrian | 6:00 | #18 | 10.48 | pedestrian | 0.29 | 24 | 0.65 | 518 | moving_right | 1 |
| b3_combo | night_holdout_2200 | p2 pedestrian | 10:00 | #27 | 18.72 | pedestrian | 0.23 | 32 | 0.15 | 516 | moving_right | 1 |
| b3_combo | night_holdout_2200 | p3 pedestrian | 10:59 | #33 | 14.98 | pedestrian | 0.35 | 43 | 0.30 | 526 | moving_right | 1 |
| b3_combo | night_holdout_2200 | p4 pedestrian | 10:59 | #36 | 5.84 | pedestrian | 0.05 | 28 | 0.51 | 416 | toward_camera | 1 |
| b3_combo | night_holdout_2200 | p5 pedestrian | 10:59 | #40 | 3.84 | pedestrian | 0.15 | 76 | 0.96 | 344 | moving_right | 1 |
| b3_combo | day_holdout_1245 | h1 pedestrian | 0:40 | #1 | 15.48 | bicyclist | 0.57 | 26 | 0.74 | 678 | moving_left | 1 |
| b3_combo | day_holdout_1245 | h2 cyclist | 8:07 | #7 | 8.17 | bicyclist | 0.85 | 44 | 1.59 | 730 | moving_right | 1 |
| b3_combo | day_holdout_1245 | h3 cyclist | 8:46 | #9 | 9.68 | bicyclist | 0.82 | 57 | 1.51 | 733 | moving_right | 1 |
| b3_combo | day_holdout_1245 | h4 pedestrian | 9:54 | #14 | 7.21 | pedestrian | 0.17 | 0 | 0.18 | 30 | static | 1 |
| b3_combo | day_holdout_1245 | h5 pedestrian | 11:17 | #15 | 23.62 | bicyclist | 0.64 | 8 | 0.56 | 460 | away_from_camera | 1 |
| b4_combo_static5 | night | n1 cyclist | 4:02 | #4 | 1.2 | bicyclist | 0.97 | 94 | 4.82 | 560 | moving_right | 1 |
| b4_combo_static5 | night | n2 cyclist | 7:02 | #12 | 5.24 | bicyclist | 0.91 | 88 | 0.87 | 706 | moving_right | 1 |
| b4_combo_static5 | night | n3 cyclist | 14:21 | #18 | 3.47 | bicyclist | 0.62 | 49 | 1.23 | 499 | moving_right | 1 |
| b4_combo_static5 | night | n4 cyclist | 14:21 | #22 | 3.44 | pedestrian | 0.30 | 59 | 2.23 | 458 | moving_right | 1 |
| b4_combo_static5 | night | n5 cyclist | 14:21 | #21 | 2.37 | pedestrian | 0.39 | 31 | 2.37 | 437 | moving_right | 0 |
| b4_combo_static5 | night | n6 pedestrian | 14:47 | #23 | 10.58 | bicyclist | 0.67 | 69 | 0.48 | 526 | moving_right | 1 |
| b4_combo_static5 | day | d2 pedestrian | 3:00 | #2 | 20.69 | bicyclist | 0.73 | 6 | 0.56 | 593 | moving_left | 1 |
| b4_combo_static5 | day | d1 cyclist | 9:10 | #10 | 6.74 | bicyclist | 0.91 | 54 | 1.51 | 749 | moving_left | 1 |
| b4_combo_static5 | day | d3 pedestrian | 11:45 | #13 | 36.57 | bicyclist | 0.53 | 2 | 0.39 | 499 | moving_left | 1 |
| b4_combo_static5 | day | d4 pedestrian | 12:10 | #15 | 21.96 | pedestrian | 0.24 | 6 | 0.78 | 628 | moving_left | 1 |
| b4_combo_static5 | day | d5 pedestrian | 12:10 | #23 | 3.47 | pedestrian | 0.22 | 0 | 0.16 | 17 | static | 1 |
| b4_combo_static5 | night_holdout_2200 | p1 pedestrian | 6:00 | #18 | 10.48 | pedestrian | 0.29 | 24 | 0.65 | 518 | moving_right | 1 |
| b4_combo_static5 | night_holdout_2200 | p2 pedestrian | 10:00 | #27 | 18.72 | pedestrian | 0.23 | 32 | 0.15 | 516 | moving_right | 1 |
| b4_combo_static5 | night_holdout_2200 | p3 pedestrian | 10:59 | #33 | 14.98 | pedestrian | 0.35 | 43 | 0.30 | 526 | moving_right | 1 |
| b4_combo_static5 | night_holdout_2200 | p4 pedestrian | 10:59 | #36 | 5.84 | pedestrian | 0.05 | 28 | 0.51 | 416 | toward_camera | 1 |
| b4_combo_static5 | night_holdout_2200 | p5 pedestrian | 10:59 | #40 | 3.84 | pedestrian | 0.15 | 76 | 0.96 | 344 | moving_right | 1 |
| b4_combo_static5 | day_holdout_1245 | h1 pedestrian | 0:40 | #1 | 15.48 | bicyclist | 0.57 | 26 | 0.74 | 678 | moving_left | 1 |
| b4_combo_static5 | day_holdout_1245 | h2 cyclist | 8:07 | #7 | 8.17 | bicyclist | 0.85 | 44 | 1.59 | 730 | moving_right | 1 |
| b4_combo_static5 | day_holdout_1245 | h3 cyclist | 8:46 | #9 | 9.68 | bicyclist | 0.82 | 57 | 1.51 | 733 | moving_right | 1 |
| b4_combo_static5 | day_holdout_1245 | h4 pedestrian | 9:54 | #14 | 7.21 | pedestrian | 0.17 | 0 | 0.18 | 30 | static | 1 |
| b4_combo_static5 | day_holdout_1245 | h5 pedestrian | 11:17 | #15 | 23.62 | bicyclist | 0.64 | 8 | 0.56 | 460 | away_from_camera | 1 |

## Rules replayed on 60 (person, run) pairs

| rule | right | of | labels it changes |
|---|---|---|---|
| X-CLIP alone (now) | 44 | 60 | |
| veto 5% | 46 | 60 | b3_combo/day/d3(ok), b4_combo_static5/day/d3(ok) |
| veto 10% | 51 | 60 | b2_2_sahi/day_holdout_1245/h5(ok), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h5(ok), b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h5(ok) |
| veto 15% | 51 | 60 | b2_2_sahi/day_holdout_1245/h5(ok), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h5(ok), b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h5(ok) |
| veto 20% | 51 | 60 | b2_2_sahi/day_holdout_1245/h5(ok), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h5(ok), b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h5(ok) |
| veto 30% | 54 | 60 | b2_2_sahi/day_holdout_1245/h1(ok), b2_2_sahi/day_holdout_1245/h5(ok), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b3_combo/day_holdout_1245/h5(ok), b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h1(ok), b4_combo_static5/day_holdout_1245/h5(ok) |
| veto 40% | 53 | 60 | exp0_base/day/d1(WRONG), b2_2_sahi/day_holdout_1245/h1(ok), b2_2_sahi/day_holdout_1245/h5(ok), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b3_combo/day_holdout_1245/h5(ok), b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h1(ok), b4_combo_static5/day_holdout_1245/h5(ok) |
| veto 50% | 48 | 60 | exp0_base/day/d1(WRONG), b2_2_sahi/day_holdout_1245/h1(ok), b2_2_sahi/day_holdout_1245/h2(WRONG), b2_2_sahi/day_holdout_1245/h5(ok), b3_combo/night/n3(WRONG), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b3_combo/day_holdout_1245/h2(WRONG), b3_combo/day_holdout_1245/h5(ok), b4_combo_static5/night/n3(WRONG), b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h1(ok), b4_combo_static5/day_holdout_1245/h2(WRONG), b4_combo_static5/day_holdout_1245/h5(ok) |
| promote 80% | 44 | 60 | - |
| promote 90% | 44 | 60 | - |
| promote 95% | 44 | 60 | - |
| speed lateral walk<0.8 ride>2.0 | 53 | 60 | b2_2_sahi/day_holdout_1245/h1(ok), b3_combo/night/n4(ok), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b4_combo_static5/night/n4(ok), b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h1(ok) |
| speed lateral walk<1.0 ride>2.0 | 52 | 60 | exp0_base/day/d1(WRONG), b2_2_sahi/day_holdout_1245/h1(ok), b3_combo/night/n4(ok), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b4_combo_static5/night/n4(ok), b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h1(ok) |
| speed lateral walk<1.2 ride>2.5 | 50 | 60 | exp0_base/day/d1(WRONG), b2_2_sahi/day_holdout_1245/h1(ok), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h1(ok) |
| speed lateral walk<1.5 ride>3.0 | 48 | 60 | exp0_base/day/d1(WRONG), b2_2_sahi/day_holdout_1245/h1(ok), b3_combo/night/n3(WRONG), b3_combo/day/d2(ok), b3_combo/day/d3(ok), b3_combo/day_holdout_1245/h1(ok), b4_combo_static5/night/n3(WRONG), b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h1(ok) |

Read the per-row table first: do real riders and real walkers separate on speed (lateral tracks) or on det %cyc? A rule that only 'wins' by changing one or two rows is a coincidence.

## Counted tracks that match NO truth person (false detections, or a person missing from the truth file)

| run | clip | when | track | secs | X-CLIP | wBIC | det %cyc | speed h/s | net px | direction |
|---|---|---|---|---|---|---|---|---|---|---|
| b2_2_sahi | night_holdout_2200 | 7:50-8:27 | #24 | 4.97 | pedestrian | 0.31 | 0 | 0.01 | 0 | static |
| b2_2_sahi | night_holdout_2200 | 8:32-9:00 | #26 | 3.8 | pedestrian | 0.26 | 0 | 0.01 | 2 | static |
| b3_combo | night_holdout_2200 | 7:50-8:27 | #24 | 4.97 | pedestrian | 0.31 | 0 | 0.01 | 0 | static |
| b3_combo | night_holdout_2200 | 8:32-9:00 | #26 | 3.8 | pedestrian | 0.26 | 0 | 0.01 | 2 | static |

A static object (barricade, sign) tracked as a person should show a tiny net movement and speed; compare with the real people above before choosing a filter.

<a id="report-fusion-cases-20261019"></a>
## FUSION_cases_20261019.md
Original location: `vision3/best/test_colonial/exp_results/FUSION_cases_20261019.md`.

# Fusion probe

runs: b4_combo_static5

| run | clip | truth | when | track | secs | X-CLIP | wBIC | det %cyc | speed h/s | net px | direction | counted |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| b4_combo_static5 | night | n1 cyclist | 4:02 | #4 | 1.2 | bicyclist | 0.97 | 94 | 4.82 | 560 | moving_right | 1 |
| b4_combo_static5 | night | n2 cyclist | 7:02 | #12 | 5.24 | bicyclist | 0.91 | 88 | 0.87 | 706 | moving_right | 1 |
| b4_combo_static5 | night | n3 cyclist | 14:21 | #18 | 3.47 | bicyclist | 0.62 | 49 | 1.23 | 499 | moving_right | 1 |
| b4_combo_static5 | night | n4 cyclist | 14:21 | #22 | 3.44 | pedestrian | 0.30 | 59 | 2.23 | 458 | moving_right | 1 |
| b4_combo_static5 | night | n5 cyclist | 14:21 | #21 | 2.37 | pedestrian | 0.39 | 31 | 2.37 | 437 | moving_right | 0 |
| b4_combo_static5 | night | n6 pedestrian | 14:47 | #23 | 10.58 | bicyclist | 0.67 | 69 | 0.48 | 526 | moving_right | 1 |
| b4_combo_static5 | day | d2 pedestrian | 3:00 | #2 | 20.69 | bicyclist | 0.73 | 6 | 0.56 | 593 | moving_left | 1 |
| b4_combo_static5 | day | d1 cyclist | 9:10 | #10 | 6.74 | bicyclist | 0.91 | 54 | 1.51 | 749 | moving_left | 1 |
| b4_combo_static5 | day | d3 pedestrian | 11:45 | #13 | 36.57 | bicyclist | 0.53 | 2 | 0.39 | 499 | moving_left | 1 |
| b4_combo_static5 | day | d4 pedestrian | 12:10 | #15 | 21.96 | pedestrian | 0.24 | 6 | 0.78 | 628 | moving_left | 1 |
| b4_combo_static5 | day | d5 pedestrian | 12:10 | #23 | 3.47 | pedestrian | 0.22 | 0 | 0.16 | 17 | static | 1 |
| b4_combo_static5 | night_holdout_2200 | p1 pedestrian | 6:00 | #18 | 10.48 | pedestrian | 0.29 | 24 | 0.65 | 518 | moving_right | 1 |
| b4_combo_static5 | night_holdout_2200 | p2 pedestrian | 10:00 | #27 | 18.72 | pedestrian | 0.23 | 32 | 0.15 | 516 | moving_right | 1 |
| b4_combo_static5 | night_holdout_2200 | p3 pedestrian | 10:59 | #33 | 14.98 | pedestrian | 0.35 | 43 | 0.30 | 526 | moving_right | 1 |
| b4_combo_static5 | night_holdout_2200 | p4 pedestrian | 10:59 | #36 | 5.84 | pedestrian | 0.05 | 28 | 0.51 | 416 | toward_camera | 1 |
| b4_combo_static5 | night_holdout_2200 | p5 pedestrian | 10:59 | #40 | 3.84 | pedestrian | 0.15 | 76 | 0.96 | 344 | moving_right | 1 |
| b4_combo_static5 | day_holdout_1245 | h1 pedestrian | 0:40 | #1 | 15.48 | bicyclist | 0.57 | 26 | 0.74 | 678 | moving_left | 1 |
| b4_combo_static5 | day_holdout_1245 | h2 cyclist | 8:07 | #7 | 8.17 | bicyclist | 0.85 | 44 | 1.59 | 730 | moving_right | 1 |
| b4_combo_static5 | day_holdout_1245 | h3 cyclist | 8:46 | #9 | 9.68 | bicyclist | 0.82 | 57 | 1.51 | 733 | moving_right | 1 |
| b4_combo_static5 | day_holdout_1245 | h4 pedestrian | 9:54 | #14 | 7.21 | pedestrian | 0.17 | 0 | 0.18 | 30 | static | 1 |
| b4_combo_static5 | day_holdout_1245 | h5 pedestrian | 11:17 | #15 | 23.62 | bicyclist | 0.64 | 8 | 0.56 | 460 | away_from_camera | 1 |

## Detector / X-CLIP error patterns

Classification of matched, scored tracks only; duration/counting failures and misses are separate.
Each row below is one run. Repeated people across runs are not independent examples.

| run | both right | both wrong | detector right / X-CLIP wrong | detector wrong / X-CLIP right |
|---|---|---|---|---|
| b4_combo_static5 | 11: night/n1 (moving_right, 1.2s), night/n2 (moving_right, 5.24s), day/d1 (moving_left, 6.74s), day/d4 (moving_left, 21.96s), day/d5 (static, 3.47s), night_holdout_2200/p1 (moving_right, 10.48s), night_holdout_2200/p2 (moving_right, 18.72s), night_holdout_2200/p3 (moving_right, 14.98s), night_holdout_2200/p4 (toward_camera, 5.84s), day_holdout_1245/h3 (moving_right, 9.68s), day_holdout_1245/h4 (static, 7.21s) | 2: night/n5 (moving_right, 2.37s), night/n6 (moving_right, 10.58s) | 5: night/n4 (moving_right, 3.44s), day/d2 (moving_left, 20.69s), day/d3 (moving_left, 36.57s), day_holdout_1245/h1 (moving_left, 15.48s), day_holdout_1245/h5 (away_from_camera, 23.62s) | 3: night/n3 (moving_right, 3.47s), night_holdout_2200/p5 (moving_right, 3.84s), day_holdout_1245/h2 (moving_right, 8.17s) |

Use these named cases to inspect the source video. Direction is measured image motion; it cannot prove a missed person was walking away, since missed people have no track. Missing detector shares are excluded. This comparison does not measure detector recall.

## Rules replayed on 21 (person, run) pairs

| rule | right | of | labels it changes |
|---|---|---|---|
| X-CLIP alone (now) | 14 | 21 | |
| veto 5% | 15 | 21 | b4_combo_static5/day/d3(ok) |
| veto 10% | 17 | 21 | b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h5(ok) |
| veto 15% | 17 | 21 | b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h5(ok) |
| veto 20% | 17 | 21 | b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h5(ok) |
| veto 30% | 18 | 21 | b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h1(ok), b4_combo_static5/day_holdout_1245/h5(ok) |
| veto 40% | 18 | 21 | b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h1(ok), b4_combo_static5/day_holdout_1245/h5(ok) |
| veto 50% | 16 | 21 | b4_combo_static5/night/n3(WRONG), b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h1(ok), b4_combo_static5/day_holdout_1245/h2(WRONG), b4_combo_static5/day_holdout_1245/h5(ok) |
| promote 80% | 14 | 21 | - |
| promote 90% | 14 | 21 | - |
| promote 95% | 14 | 21 | - |
| speed lateral walk<0.8 ride>2.0 | 18 | 21 | b4_combo_static5/night/n4(ok), b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h1(ok) |
| speed lateral walk<1.0 ride>2.0 | 18 | 21 | b4_combo_static5/night/n4(ok), b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h1(ok) |
| speed lateral walk<1.2 ride>2.5 | 17 | 21 | b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h1(ok) |
| speed lateral walk<1.5 ride>3.0 | 16 | 21 | b4_combo_static5/night/n3(WRONG), b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h1(ok) |

Read the per-row table first: do real riders and real walkers separate on speed (lateral tracks) or on det %cyc? A rule that only 'wins' by changing one or two rows is a coincidence.

<a id="report-manifest-20261007-2313"></a>
## MANIFEST_20261007_2313.md
Original location: `vision3/best/test_colonial/exp_results/MANIFEST_20261007_2313.md`.

# Experiment submission 20261007_2313
Submitted from: /orange/xiangyan/rithika/vision/vision3/best/test_colonial   by: rmathew1   at: Wed Oct  7 11:13:20 PM EDT 2026
Code: code/xclip_overlay_v19_colonial.py  slurm: code/run_xclip_colonial_v19.slurm   (control = rtdetr_v3 + v17 settings; see README section 22/23)
Clips: night 21:15-21:30 (chunk 22, frames 26978-53946) and day 14:00-14:15 (chunk 15, frames 1-26973)

## Jobs
exp0_base          night  job 45123979   time 02:00:00  env: MOTION_DIAG=1
exp0_base          day    job 45123980   time 02:00:00  env: MOTION_DIAG=1
exp1_sahi          night  job 45123981   time 04:00:00  env: SAHI=1
exp1_sahi          day    job 45123982   time 04:00:00  env: SAHI=1
exp2_gamma         night  job 45123983   time 02:00:00  env: ENHANCE=gamma,NIGHT_START=21:00,NIGHT_END=06:00
exp2_clahe         night  job 45123984   time 02:00:00  env: ENHANCE=clahe,NIGHT_START=21:00,NIGHT_END=06:00
exp2_zerodce       night  job 45123985   time 02:00:00  env: ENHANCE=zerodce,ZERODCE_WEIGHTS=/orange/xiangyan/rithika/vision/vision3/best/test_colonial/code/zerodce/Epoch99.pth,NIGHT_START=21:00,NIGHT_END=06:00
exp3a_speed        night  job 45123986   time 02:00:00  env: SPEED_RULE=1
exp3a_speed        day    job 45123987   time 02:00:00  env: SPEED_RULE=1
exp3b_short        night  job 45123988   time 02:00:00  env: SHORT_RULE=1
exp3b_short        day    job 45123989   time 02:00:00  env: SHORT_RULE=1

Evaluation job: 45123990 (starts when all of the above end; writes exp_results/EVAL_20261007_2313.md)

## Where everything is (run names: exp0_base,exp1_sahi,exp2_gamma,exp2_clahe,exp2_zerodce,exp3a_speed,exp3b_short)
- annotated clips : annotated/<run>/Standard_SCU8OG_2019-07-10_0000.0NN/*.mp4      (NN = 22 night, 15 day)
- counts + tables : counts/<run>/*_tracks.csv  *_rules_audit.csv  *_track_motion.csv  *_motion_candidates.csv/.png (exp0 only)  *_enhance_preview.png (exp2)
- slurm logs      : logs/slurm_<run>_<clip>_<jobid>_<chunk>.log
- run logs (json) : logs/<run>/*_run_log.json   (all flags + counts + runtime)
- truth files     : truth/night_2115_truth.csv  truth/day_1400_truth.csv   (YOU fill these in; evaluation needs them)
- evaluation      : exp_results/EVAL_20261007_2313.md  (re-create any time:  python code/eval_truth.py --root . --runs exp0_base,exp1_sahi,exp2_gamma,exp2_clahe,exp2_zerodce,exp3a_speed,exp3b_short --baseline exp0_base)

## Monitor
squeue -u $USER -o "%i %j %T %M"


<a id="report-manifest-batch2-20261008-1612"></a>
## MANIFEST_batch2_20261008_1612.md
Original location: `vision3/best/test_colonial/exp_results/MANIFEST_batch2_20261008_1612.md`.

# Batch 2 submission 20261008_1612
Submitted: Thu Oct  8 04:12:35 PM EDT 2026   by rmathew1   code: code/xclip_overlay_v19_colonial.py (updated: --det-veto-pct --det-promote-pct --short-rule-night-only)
Clips: dev night 21:15-21:30 (chunk 22) | dev day 14:00-14:15 (chunk 15) | HOLD-OUT night 22:00-22:15 (chunk 23) | HOLD-OUT day 12:45-13:00 (chunk 13)
Settings: speed rule lateral-only (walk<1.0, ride>2.0 body heights/s) in b2_5; veto=15 (X-CLIP bicyclist but detector cyclist in <15% of frames -> pedestrian), promote=90, SAHI 640/0.2, short rule 0.3 s / 90% / 0.9 at night only
## Jobs
b2_0_base                      night_2200     job 45214338   env: (none)
b2_0_base                      day_1245       job 45214339   env: (none)
b2_2_sahi                      night_2200     job 45214340   env: SAHI=1
b2_2_sahi                      day_1245       job 45214341   env: SAHI=1
b2_1_fuse                      night_2115     job 45214342   env: DET_VETO_PCT=15,DET_PROMOTE_PCT=90
b2_1_fuse                      day_1400       job 45214343   env: DET_VETO_PCT=15,DET_PROMOTE_PCT=90
b2_1_fuse                      night_2200     job 45214344   env: DET_VETO_PCT=15,DET_PROMOTE_PCT=90
b2_1_fuse                      day_1245       job 45214345   env: DET_VETO_PCT=15,DET_PROMOTE_PCT=90
b2_3_sahi_fuse                 night_2115     job 45214346   env: SAHI=1,DET_VETO_PCT=15,DET_PROMOTE_PCT=90
b2_3_sahi_fuse                 day_1400       job 45214347   env: SAHI=1,DET_VETO_PCT=15,DET_PROMOTE_PCT=90
b2_3_sahi_fuse                 night_2200     job 45214348   env: SAHI=1,DET_VETO_PCT=15,DET_PROMOTE_PCT=90
b2_3_sahi_fuse                 day_1245       job 45214349   env: SAHI=1,DET_VETO_PCT=15,DET_PROMOTE_PCT=90
b2_4_sahi_fuse_nightshort      night_2115     job 45214350   env: SAHI=1,DET_VETO_PCT=15,DET_PROMOTE_PCT=90,SHORT_RULE=1,SHORT_RULE_NIGHT_ONLY=1,NIGHT_START=21:00,NIGHT_END=06:00
b2_4_sahi_fuse_nightshort      day_1400       job 45214351   env: SAHI=1,DET_VETO_PCT=15,DET_PROMOTE_PCT=90,SHORT_RULE=1,SHORT_RULE_NIGHT_ONLY=1,NIGHT_START=21:00,NIGHT_END=06:00
b2_4_sahi_fuse_nightshort      night_2200     job 45214352   env: SAHI=1,DET_VETO_PCT=15,DET_PROMOTE_PCT=90,SHORT_RULE=1,SHORT_RULE_NIGHT_ONLY=1,NIGHT_START=21:00,NIGHT_END=06:00
b2_4_sahi_fuse_nightshort      day_1245       job 45214353   env: SAHI=1,DET_VETO_PCT=15,DET_PROMOTE_PCT=90,SHORT_RULE=1,SHORT_RULE_NIGHT_ONLY=1,NIGHT_START=21:00,NIGHT_END=06:00
b2_5_sahi_speed                night_2115     job 45214354   env: SAHI=1,SPEED_RULE=1,SPEED_LATERAL_ONLY=1,WALK_MAX_SPEED=1.0,RIDE_MIN_SPEED=2.0
b2_5_sahi_speed                day_1400       job 45214355   env: SAHI=1,SPEED_RULE=1,SPEED_LATERAL_ONLY=1,WALK_MAX_SPEED=1.0,RIDE_MIN_SPEED=2.0
b2_5_sahi_speed                night_2200     job 45214356   env: SAHI=1,SPEED_RULE=1,SPEED_LATERAL_ONLY=1,WALK_MAX_SPEED=1.0,RIDE_MIN_SPEED=2.0
b2_5_sahi_speed                day_1245       job 45214357   env: SAHI=1,SPEED_RULE=1,SPEED_LATERAL_ONLY=1,WALK_MAX_SPEED=1.0,RIDE_MIN_SPEED=2.0

Evaluation job: 45214358  -> exp_results/EVAL_batch2_20261008_1612.md  (also puts clips with explicit names into exp_results/clips/)
## Where
annotated clips: annotated/<run>/*/<run>__<day|night>_<HHMM>-<HHMM>__<test>__<date>.mp4  (and copies in exp_results/clips/)
counts: counts/<run>/*_tracks.csv *_rules_audit.csv ; slurm logs: logs/slurm_<run>_<clip>_*.log
truth: truth/night_2115_truth.csv truth/day_1400_truth.csv truth/night_2200_truth.csv truth/day_1245_truth.csv  (hold-out files must be filled in BEFORE judging)
Re-score any time:  python code/eval_truth.py --root . --runs exp0_base,exp1_sahi,b2_0_base,b2_2_sahi,b2_1_fuse,b2_3_sahi_fuse,b2_4_sahi_fuse_nightshort,b2_5_sahi_speed --baseline exp0_base


<a id="report-newsites-newsites-oct20"></a>
## NEWSITES_newsites_oct20.md
Original location: `vision3/best/test_colonial/exp_results/NEWSITES_newsites_oct20.md`.

# Two additional sites: reference-system validation

Configuration: fine-tuned RT-DETR + SAHI + ByteTrack/ID stitching + X-CLIP + detector/motion/duration/static rules. TTA and enhancement off.
No complete human truth exists for these clips: predicted counts are NOT accuracy.
These sites appear in the documented training-data recipe; do not call this an unseen-site test.
Windows are selected by a fixed daytime/noon preference, not by model performance.
Clocks are inferred from filenames, not verified against the embedded camera clock. Check before using time-based conclusions.

## Existing four labelled clips: detector versus X-CLIP
Saved track classification: detector 16/21; X-CLIP 14/21.
Provisional time-matched comparison, not detector recall or verified standalone counting accuracy.
Full comparison: `/orange/xiangyan/rithika/vision/vision3/best/test_colonial/exp_results/classifier_comparison_20261020/RESULTS.md`

## Anderson St (2021) — SUCCEEDED
Source: `/orange/xiangyan/rithika/vision/pilot_clips/MioVision Data/2021 Data/Anderson St/Standard_SCU8PM_2021-04-13_0000/Standard_SCU8PM_2021-04-13_0000.013.mp4`
Source metadata: {'fps': 29.970000084744214, 'frames': 107864, 'width': 720, 'height': 480}
Planned first-frame clock: 2021-04-13_12:00:00 (inferred)
Predicted counts only: {'bicyclists': 1, 'pedestrians': 1, 'vehicles': 137}
Runtime: 38.7 minutes
Actual processed duration: 900.0 seconds
Exact annotated video paths:
- `/orange/xiangyan/rithika/vision/vision3/best/test_colonial/annotated/newsites_oct20_anderson_2021/Standard_SCU8PM_2021-04-13_0000.013/newsites_oct20_anderson_2021__day_1200-1215__sahi640+speedrule-lateral+shortrule-night+detfuse+staticfilter__20210413.mp4`
Tracks: `/orange/xiangyan/rithika/vision/vision3/best/test_colonial/counts/newsites_oct20_anderson_2021/Standard_SCU8PM_2021-04-13_0000.013_tracks.csv`
Review every cyclist/pedestrian; report missed people, duplicate IDs, object-to-person ID jumps, e-scooter labels and clip timestamps.

## Curry Ford North (2022) — SUCCEEDED
Source: `/orange/xiangyan/rithika/vision/pilot_clips/MioVision Data/2022 Data/Curry Ford/North/Standard_SCU8OG_2022-05-17_0000/Standard_SCU8OG_2022-05-17_0000.013.mp4`
Source metadata: {'fps': 29.970000084744214, 'frames': 107864, 'width': 720, 'height': 480}
Planned first-frame clock: 2022-05-17_12:00:00 (inferred)
Predicted counts only: {'bicyclists': 0, 'pedestrians': 0, 'vehicles': 448}
Runtime: 38.5 minutes
Actual processed duration: 900.0 seconds
Exact annotated video paths:
- `/orange/xiangyan/rithika/vision/vision3/best/test_colonial/annotated/newsites_oct20_curryford_2022/Standard_SCU8OG_2022-05-17_0000.013/newsites_oct20_curryford_2022__day_1200-1215__sahi640+speedrule-lateral+shortrule-night+detfuse+staticfilter__20220517.mp4`
Tracks: `/orange/xiangyan/rithika/vision/vision3/best/test_colonial/counts/newsites_oct20_curryford_2022/Standard_SCU8OG_2022-05-17_0000.013_tracks.csv`
Review every cyclist/pedestrian; report missed people, duplicate IDs, object-to-person ID jumps, e-scooter labels and clip timestamps.

## final_review — SUCCEEDED
{'output': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/exp_results/final_review_20261020', 'requires_human_review': True}

## truth_headers — SUCCEEDED
{'output': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/annotated_gt', 'originals_preserved': True}



<a id="report-rf-dino-person-validation-20261020"></a>
## RF_DINO_person_validation_20261020.md
Original location: `vision3/best/test_colonial/exp_results/RF_DINO_person_validation_20261020.md`.

# Person-box validation on selected existing frames

Reviewed frames: 32/32. Unreviewed frames excluded.
Person proposals only, one-to-one IoU>=0.50. Cyclists/scooter riders contribute person boxes, not mode labels.
Thresholds are the saved audit thresholds. This is NOT AP, unique-person recall, continuous-video counting accuracy or an independent holdout test.

| Detector | Correct boxes TP | False boxes FP | Missed boxes FN | Precision | Recall |
|---|---:|---:|---:|---:|---:|
| rf | 4 | 10 | 16 | 0.286 | 0.200 |
| dino | 13 | 35 | 7 | 0.271 | 0.650 |


<a id="report-newsites-owner-review-20261020"></a>
## newsites_owner_review_20261020.md
Original location: `vision3/best/test_colonial/exp_results/newsites_owner_review_20261020.md`.

# Owner visual review — 2026-10-20

Reported clock times below are supplied by the owner. They are not a new exhaustive ground-truth annotation or identity audit. Preserve the existing four Colonial truth files.

| Site | Encounter | Owner observation |
|---|---|---|
| Anderson 2021 | Pedestrian, 12:01:24–12:01:32 pm | Detected |
| Anderson 2021 | Cyclist, 12:01:37–12:01:45 pm | Detected |
| Anderson 2021 | Another cyclist, 12:01:40–12:02:43 pm | Missed |
| Anderson 2021 | Motorcycle, 12:05:48–12:05:50 pm | Missed |
| Curry Ford North 2022 | Cyclist, 12:09:05–12:09:11 pm; very blurry | Missed |

The owner reports two distinct Anderson cyclists despite overlapping time intervals. Motorcycle remains a separate category here. Among reported encounters, Anderson detected one of two cyclists and one pedestrian; Curry Ford missed its reported cyclist. These are confirmed visual limitations, not whole-video recall, precision, AP, or proof of the cause. Blurriness was observed at Curry Ford; it does not establish that a specific enhancement would recover the rider. Do not claim successful generalization or start another model sweep automatically. Both sites appear in the training recipe and both tested clips are 720×480.

## Colonial lane and speed inputs

Owner approved the zone previews visually. This accepts visible polygon alignment; individual lane assignments and track identities still need their own review.

Source: `Bike Lane Study Counts/bicyclist speeds.xlsx`:

- Colonial bike lane: **35 feet**, 12 unique records including an e-bike. Example source cells: `Bike Lane!A12` / `BL Analysis!A61`.
- Colonial sidewalk: **30 feet**, 11 unique records. Example source cell: `Sidewalk!A24`.

These are measured lengths recorded in the study, not distances inferred from pixels. The workbook records do not establish the gate endpoints in this camera view, the applicable recording date, or a confirmed record-to-person mapping. Use these lengths only with the corresponding measured sections; do not substitute arbitrary polygon edges. Validated mph remains pending gate correspondence and person/record verification.

## Person-box review received

Root `person_box_review.json` preserved unchanged: 32 frames, 20 boxes, only 1 frame marked reviewed (`day_holdout_1245:106994`). The review UI clears the reviewed checkbox when drawing or undoing. Unchecked frames cannot be treated as confirmed empty or complete. Asked owner whether all 32 frames are finished; do not auto-approve them without that confirmation.

No matching local `rf_boxes/manifest.json` / prediction pack was found in this repository. Scoring requires that existing pack from `exp_results/final_review_20261020/rf_boxes` plus the completed review JSON. No new model inference or batch submission is needed.

Owner confirmation (2026-10-20): all32person-box frames, including empty frames, were inspected; unchecked boxes were accidental. Original JSON preserved. `person_box_review_confirmed_20261020.json` marks all32reviewed based on explicit owner confirmation and retains all20boxes. Prediction pack still required for scoring; no accuracy calculated yet.

Confirmed person-box scoring completed locally (2026-10-20): found existing pack at `/Users/rithika/Downloads/final_review_20261020/rf_boxes`. All32owner-confirmed frames,20human boxes, one-to-one IoU>=0.50, saved thresholds. RF-DETR:4TP/10FP/16FN, precision28.6%, recall20.0%. Grounding DINO:13TP/35FP/7FN, precision27.1%, recall65.0%. DINO finds more labelled person boxes but generates more false boxes; neither is a demonstrated replacement for the counting reference. Selected repeated frames, not unique people/AP/whole-video cyclist accuracy or an independent holdout. Report: `vision3/best/test_colonial/exp_results/RF_DINO_person_validation_20261020.md`. Earlier statements that pack was unavailable or no score existed are superseded.

Received root colonial_speed_gates.json: two facilities with35ft/30ft and720x480reference, reviewer Rithika, but measurement_source="n/a". Original preserved. No physical speed calculated: exact measured endpoint correspondence not established. Asked owner whether these are known study endpoints or visible lane ends. Added placeholder-source rejection in exporter and speed measurement plus regression test. Numeric workbook lengths must not be assigned to arbitrary scene-wide segments.

Owner clarification (2026-10-20): colonial_speed_gates.json marks visible lane ends, NOT known study measurement endpoints. Therefore it is unsuitable for mph calculation; do not replace its n/a source or accept35ft/30ft for those drawn spans. Original preserved; review decision in exp_results/colonial_speed_gate_review_20261020.json. Physical speed remains blocked pending identifiable independently measured endpoints (or appropriate metric calibration). Image-motion estimates remain available; no further GPU run needed.

Exploratory calibration attempted locally (2026-10-20) at owner request: new code/exploratory_gate_check.py checks estimated finite gates without granting physical distance. Output exp_results/exploratory_speed_calibration_20261020/{RESULTS.md,crossings.csv,summary.json}. All7actual bicycle truth rows checked, both facilities (14checks), full saved unverified candidate tracks;0complete two-line crossings. None crosses the first line. Workbook rescanned:23Colonial speed records but0verified person links; no timestamps found in these speed rows. Thus0distance fits/0held-out validation pairs, no mph/MAE. Do not pair records by nearest speed or equate study record IDs with track IDs. Future fit requires independently matched people and crossings, fixed facility distance, and different people for validation. Three crossing tests pass (clip-time interpolation, finite-line nonextension, large-gap exclusion). No inference/batch submitted; original gates/truth untouched.

