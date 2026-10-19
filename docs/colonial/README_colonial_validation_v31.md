> **Current submission instructions: read the root README.md only. One command submits the active research suite and final report. Historical commands below are reference, not additional jobs to submit.**

# Colonial North: validating the fine-tuned RT-DETR + X-CLIP bicyclist counter

**Current priorities (2026-10-19 user update):** higher-resolution footage from ANY year, comparison against existing truth, additional detection research, and the high-sensitivity review experiment. Full-day scaling is removed from the plan. The 40-track comparison and own-night fine-tuning are on the back burner and excluded from the updated PowerPoint. Existing truth clips do not need relabelling. See `docs/tasks/todo.md`, `docs/VIDEO_PATHS.md` and `docs/RESEARCH_METHODS.md` from the repo root. Older sections below retain historical plans, not current instructions.

Status as of 2026-10-15 evening (README v31: adds section 40, requests of the evening, batch-5 / scan scripts; adds section 39, tools for the pending work, not yet run on the cluster; README v30: CORRECTS section 37c: the new zone polygons belong to the COLONIAL 2019 camera, not the 2025 video; README v29: hand-off version for a new chat session; adds the 2025 fisheye video outcome and the zone polygons in section 37; batch 4 results in section 35). The long list of per-version notes that used to sit in this line is kept at the very end (section 36). **Start with section 0.**

## 0. START HERE (2026-10-11): where things stand
**Goal.** Count bicyclists and pedestrians at the Colonial North camera (2019-07-10 footage) with the fine-tuned RT-DETR (`rtdetr_v3`) + X-CLIP, and fix the failures found by watching clips.
**Best configuration so far = `b3_combo`** (SAHI-style sliced detection + fusion of X-CLIP, detector and speed + night-only short-track rule). Person-level scores against Rithika's own hand-made truth, 4 clips, 21 people (2 dev clips + 2 hold-outs whose settings were not tuned on them):
| clip | baseline (`exp0_base`) | SAHI alone | **`b3_combo`** |
|---|---|---|---|
| night 21:15-21:30 (6 people) | 0 | 2 | 4 |
| day 14:00-14:15 (5) | 3 | 3 | 5 |
| night 22:00-22:15 hold-out (5 pedestrians) | 0 | 5 | 5 (but 2 extra false tracks on a barricade) |
| day 12:45-13:00 hold-out (2 cyclists + 3 pedestrians) | 3 | 3 | 5 |
| total found | 6 / 21 | 13 / 21 | **19 / 21** |
**Batch 4 (run 2026-10-12): `b4_combo_static5` = `b3_combo` + static-object filter = THE CURRENT BEST.** Same 19 / 21 people found (night 4/6, day 5/5, 22:00 5/5, 12:45 5/5) and 0 false counted tracks on all four clips: the two barricade tracks at 22:00 are gone and nothing else changed (counted 0 cyclists / 5 pedestrians at 22:00). Details in section 35.
Strong hint, not a measured accuracy: one camera, one day, four 15-minute windows, 21 people, thresholds partly chosen on the first two clips.
**What the configuration is (details: sections 23, 25, 29, 32).** Detector with SAHI slicing (640 px, 20% overlap, plus the full frame); tracking; X-CLIP label per track; 3 s minimum on screen; FUSION = the final label comes from three opinions (X-CLIP, the detector's cyclist share of frames, speed in body heights/s) via: veto (X-CLIP bicyclist but detector cyclist < 15% of frames -> pedestrian), lateral speed rule (walk < 0.8, ride > 2.0 body heights/s), night-only short-track rule (21:00-06:00, 0.3-3 s tracks count as bicyclist if detector cyclist >= 90% and weighted X-CLIP >= 0.9). Dropped because no gain: image enhancement (gamma, CLAHE, Zero-DCE), motion-blob diagnostic, promote 90%, speed thresholds of 1.0.
**Still wrong in `b4_combo_static5`:** (the 2 barricade tracks of `b3_combo` at 22:00, `#24`, `#26`, are removed; the third long track `#27` is a real pedestrian whose track also covers the barricade) night 14:47 pedestrian called a cyclist; night 14:21 rider (2.4 s) under the 3 s minimum.
**Verified truth files** (video position mm:ss, one row per person, motorcycle scored as cyclist; on the cluster in `truth/`, copies in the outputs folder): `day_1400_truth.csv` (1 cyclist + 4 pedestrians), `night_2115_truth.csv` (1 motorcycle + 4 cyclists + 1 pedestrian), `day_1245_truth.csv` (2 cyclists + 3 pedestrians; 9:54 not re-checked), `night_2200_truth.csv` (5 pedestrians; barricade = not a person).
**Tools for the open items (2026-10-15, section 39, not yet run):** `scale_up.py`, `pick_new_windows.py`, `finetune_v5.py`, `review_pack.py`, `undistort_fisheye.py` (tarball `colonial_pending_tools.tar.gz`).
**Open / next.** (1) DONE 2026-10-12 (section 35): `b4_combo_static5` = `b3_combo` + static-object filter (net < 5 px AND path speed < 0.05 h/s, track >= 3 s): `bash code/run_batch4.sh` (4 jobs + evaluation). Expected: 22:00 barricade tracks gone, nothing else changes. DUPLICATE SUBMISSION CHECK: running the command twice creates the same jobs twice (the guard only sees a `counts/` folder after a job starts); keep one set. (2) Zones for Colonial: new polygons received (`colonial_north_v2.json`, ref_size 1440x960 inferred), to be verified with `draw_zones_preview.py` (section 37c); person counts and all scores are unaffected by zones. (3) 2025 video test: DONE as a qualitative run (section 37): runs `nv_base_corrine2025_706` and `nv_combo_corrine2025_706`; Rithika watched the 2025 videos and judged them not good for this pipeline (fisheye camera: cars right below the camera are not detected, objects farther away are); not scored, no truth file; the MioVision Data folder holds nothing newer than 2022 (all 720x480); the 2025 video came from elsewhere (path to be asked); no truth file exists for it. (4) Before any claim: label 2-3 NEW 15-minute windows (one night, two day, other hours): the four current clips have been looked at. (5) Not done: fine-tuning on her own hard frames (her stated fallback), temporal detector, BNE-DETR, SAMURAI.
**Statements in older sections that were later corrected (newest wins):** section 15m/21 (the short 14:03 tracks are a PEDESTRIAN, not a lost cyclist); section 26/27 (draft truth, verified in 28); section 28/29 ('three false barricade tracks' is two, see 30); section 30 ('closest real person 30 px' is 19 px, see 31); expectations in sections 22-23 (results are in 23h, 25h, 29).
**Rules of thumb for running things.** Always from `/orange/xiangyan/rithika/vision/vision3/best/test_colonial` (never from inside `code/`); activate the environment first (`source /orange/xiangyan/rithika/vision/yolo_env/bin/activate`); unpack tarballs from that folder (`tar xzf <file>`); the newest complete code set is `colonial_code_latest.tar.gz` (script, slurm, evaluator, probes, all batch scripts, Zero-DCE weights).
**After a batch finishes:** `squeue -u $USER -o "%i %j %T %M"`; `grep -L "Final counts" logs/slurm_b4_combo*.log` (should print nothing); `python code/eval_truth.py --root . --runs exp0_base,b2_2_sahi,b3_combo,b4_combo_static5 --baseline exp0_base | head -60`; `python code/fusion_probe.py --root . --runs b3_combo,b4_combo_static5 | tail -40`.

## 1. Goal
Apply the existing bicyclist/pedestrian counting model (fine-tuned RT-DETR detector + zero-shot X-CLIP video-text classifier) to the
**Colonial North** camera and check, per 15 minutes, whether its counts agree with the human ground-truth counts.

## 2. Data and what was verified before any code was run
| Item | Finding |
|---|---|
| Camera / video | BL Colonial, camera SCU8OG, 720x480, 29.97 fps. 48 hourly mp4 files (about 3600 s each) = a 48-hour recording |
| Clock | Verified from the on-screen clock: file `.001` = 2019-07-10 00:00, `.008` = 07:00, `.025` = 2019-07-11 00:00. So file N starts at hour N-1 (the old pilot code assumed a different offset) |
| Ground truth | `Colonial_North_676806_07-10-2019.xls` (SpreadsheetML XML, not a real .xls). 192 fifteen-minute bins = 48 h. **89 bicyclists in total over the 48 h** (45 on day 1, 44 on day 2), bike lane + sidewalk. The 89 matches the GT CSV and `video_site_mapping.csv` |
| Mapping | video file N covers GT bins (N-1)*4 .. (N-1)*4+3 |
| Videos merged | None. Each hourly file is processed on its own and results are joined by clock time |

## 3. Method
1. **Detector:** fine-tuned RT-DETR (`rtdetr_v3`), classes: person, cyclist, car, truck, bus, other_vehicle.
2. **Tracker:** ByteTrack, with ID stitching across short gaps.
3. **Classifier:** X-CLIP (`microsoft/xclip-base-patch32`), zero-shot, applied to **person tracks only**; it chooses between *bicyclist* and *pedestrian*. It is not run on vehicles.
4. **Final label = X-CLIP's label.** The detector's own label (person/cyclist) is shown next to it for comparison.
5. A track counts once. It is assigned to the 15-minute bin of its midpoint frame, and must be visible at least 3 s (default).
6. Optional zones (road / bike lane / sidewalk) filter vehicles and give the bike-lane vs sidewalk split. The zones file exists on the cluster:
   `zones/colonial_north_v1.json` (ref_size 720x480; polygons `road`, `bike`, `sidewalk`; pixel coordinates). It has NOT yet been used in a verified run (see section 14, task 4).
7. **Detector training data (for context):** `rtdetr_v3` was fine-tuned on about 200 annotated daytime images. Train sites: Anderson St (2021), Church Ave (2021),
   Curry Ford North (2022), BL Colonial (2019), NBL University (2019). Validation site: Corrine Dr (2025, newest camera hardware, not used in training).
   No night frames were in the training set, which is the likely reason for the night failure (not yet tested).

## 4. Validation design
- One job per hourly video. Tracking runs across the whole hour (no cuts at bin boundaries), then counts are split into 15-minute bins.
- **Outputs per run** (all under `test_colonial/`, nothing is overwritten): annotated clips (one per 15-min bin, each box shows the RT-DETR label and the X-CLIP label), per-bin counts, per-track table, run log, and an Excel workbook with sheets `Per_15min`, `Per_hour`, `Metrics`, `Tracks`, `Run_Log`.
- **Metrics:** per-bin bias (AI - GT), MAE, RMSE, WAPE, share of bins within +-1 and +-2, Pearson r; approximate count-matched precision/recall. The last two are *approximations*: ground truth is counts only, with no per-person labels. Hourly totals are reported too.
- Pipeline checks: GT total vs GT CSV vs mapping file, 15-min labels consecutive, chunk durations about 3600 s, chunks present.

## 5. Results

### Per hour (AI / ground truth)
| Hour | Run | Bicyclists | Pedestrians | Notes |
|---|---|---|---|---|
| 07:00 | run2 | 3 / 4 | 15 / 4 | construction cones counted as pedestrians (about 7 times) |
| 10:00 | run4 | 3 / 3 | 1 / 9 | |
| 12:00 | run5 | 5 / 3 | 1 / 2 | 12:45 bin over-counts (4 vs 2) |
| 13:00 | run5 | 1 / 3 | 5 / 6 | |
| 14:00 | run4 | 3 / 3 | 4 / 10 | bin-by-bin exact for bicyclists |
| 16:00 | run4 | 3 / 5 | 4 / 4 | bin-by-bin exact for pedestrians |
| 21:00 (night) | run5 | **0 / 3** | 1 / 7 | detector nearly blind in the dark |

Settings: runs 2 and 4 used defaults; run5 used a 1.0 s pedestrian minimum (see below). **Zones were not applied in any run** (the zones file was not on the cluster).

### Summary
| | Bicyclists | Pedestrians |
|---|---|---|
| Daytime hours (07,10,12,13,14,16) | 18 AI vs 21 GT | 15 vs 31 over the 5 daytime hours excluding 07:00 (07:00 is cone-contaminated) |
| Night hour (21:00) | 0 vs 3 | 1 vs 7 |
| Run4 (3 hours, 12 bins) | 9 vs 11, MAE 0.50/bin, 92% of bins within +-1, r = 0.71 | 9 vs 23, MAE 1.17/bin, count-matched precision 100%, recall 39% |
| Run5 (3 hours, 12 bins) | 6 vs 9, MAE 0.75/bin | 7 vs 15, MAE 1.00/bin |

Note: excluding the 07:00 cone hour, pedestrians over the other six hours including night are 16 AI vs 38 GT (about 42%).

**Reading:** bicyclists in daylight are counted within roughly 15% overall, with misses and some extras in individual bins. Pedestrians are heavily **under**-counted (about 40% recall). Night is a failure for both classes.

### Parameter experiments (offline, no re-run)
- **Minimum track duration, pedestrians:** shortening 3.0 s to 1.0 s raised pedestrian recall from 39% to 61% on run4 alone (precision stayed 100%), but on run5 the two extra tracks moved 269 and 336 px in 1-2 s (rider speeds, not walking speeds), and one of them had detector label 'cyclist'; they were most likely **cyclists labelled as pedestrians** (not yet confirmed clip by clip). X-CLIP is unreliable on tracks of 1-2 s. Pooled over 24 bins: 1.0 s gives recall 50% / precision 90% vs 34% / 93% at 3.0 s. Not a clean win.
- **Movement filter for static objects (cones):** rejects cones but would also reject real pedestrians who walk toward/away from the camera (only 21-29 px of net movement in some real tracks). Kept off.
- **Detector confidence cutoff:** helped only the 07:00 cone hour; on the other hours it only removed true tracks. Kept off.

## 6. Error analysis from watching the annotated clips
**Detector misses (never boxed):**
- 10:00-10:15: a go-kart and a bicyclist passing in the opposite direction, a second bicyclist later, and a pedestrian in shadow.
- 21:15-21:30: a cyclist approaching the camera, and 3 cyclists on the sidewalk of which only the last was detected. A cyclist clearly visible in the dark frame at 21:22:10 had no box.
- A person walking on the grass is not tracked until reaching the sidewalk.

**Classification errors (X-CLIP):**
- A pedestrian crossing the road was labelled bicyclist (twice).
- Labels change as a person approaches the camera: far away = pedestrian, close = cyclist (and the reverse).
- On short tracks X-CLIP is near a coin flip (e.g. 0.53 vs 0.47).

**The two labels fail in different places** (screenshots from the clips):
| Case | RT-DETR | X-CLIP | Truth |
|---|---|---|---|
| Real cyclist, daylight | person 0.57 (46% cyclist) | bicyclist 1.00 | bicyclist: X-CLIP right |
| Pedestrian crossing | person 0.72 (7% cyclist) | bicyclist 0.78 | pedestrian: detector right |
| Night, sidewalk rider | cyclist 0.61 (100%) | 0.53 / 0.47 | bicyclist: detector right |

This is the main finding for the label question. It motivates combining the two (see next steps).

**Ground truth is not perfect.** In the 07:00-07:15 clip the reviewer counted 2 riders where the GT bin has 1. Exact bin-by-bin matches in other hours show no global time offset, so differences are individual disagreements, not a clock shift.

## 7. What changed along the way (code versions)
| Version | Change |
|---|---|
| v10 | original sample script (untouched) |
| v11 | wall-clock aware; 15-min bins; one annotated clip per bin; per-bin CSV, track CSV, JSON run log; nothing overwritten |
| v12 | clips written as soon as each bin ends (header marked provisional) |
| v13 | optional static-object filter (`--person-min-disp`) |
| v14 | both labels on every person box; `Tracks` sheet in the Excel; detector-vs-X-CLIP agreement table |
| v15 | separate minimum durations for pedestrians and bicyclists |
| v16 | ground truth of the bin printed in the clip header; vehicle boxes state "X-CLIP: n/a (people only)" |
| v17 | adds outputs only (counts unchanged, diff vs v16 is additions plus the title line): per-frame trajectories, per-track motion/direction, split-track candidates, trails on the annotated clips. See section 15 |
| v18 | (written 2026-10-06, not yet run on the cluster) optional time-of-day settings: `--night-start/--night-end` plus `--night-det-conf`, `--night-bic-min-sec`, `--night-ped-min-sec`. All off by default, so counts equal v17 unless set. See section 20 |

Bugs found by testing on a stand-in pipeline (fake detector/tracker on a synthetic video): the run log was saved under the wrong filename and the clip list got overwritten by a variable-name collision, both fixed. A mistaken `MAX_FRAMES` setting produced a 1-second test clip (it is a stop frame, not a count).

## 8. Limitations
- **Small sample:** 7 of 48 hours (about 14%), 28 bins, 24 bicyclists in the ground truth. One missed rider moves a bin by 100%.
- **Tuning and testing overlap:** thresholds were explored on the same hours they are reported on.
- **No zones in runs 2, 4 and 5**, so bike-lane/sidewalk results are not reported and vehicles were not filtered. A zones run (`zones_test`, chunk 15) is pending.
- **One camera, one site.** Night video only from one hour.
- **Ground truth is counts only** (no per-person labels), so precision/recall are approximations. Human counters can disagree with the video.

## 9. Next steps (in priority order)
1. **Zones:** `zones/colonial_north_v1.json` now exists. Run it on one hour (`zones_test`, chunk 15), confirm "zones loaded" in the log, verify the facility column and the vehicle filter. (Pending, section 14 task 4.)
2. **Night:** DONE. `night_dc015` (detector confidence 0.15 on 21:15-21:30) did not help (night bicyclists 0 vs 3, pedestrians 0 vs 7), so night frames need to go into fine-tuning.
3. **Combine the two labels:** run `sweep_fusion_v1.py` on runs 4 and 5 to see if a rule using the detector's cyclist share plus X-CLIP's probability beats X-CLIP alone. Implement only if it holds on other hours.
4. **Revert the pedestrian minimum to 3.0 s** unless step 3 makes short tracks reliable.
5. **Fine-tune RT-DETR on Colonial frames** (day and night): sample frames around the missed events, label boxes, train, evaluate on whole hours held out of training. This is the real fix for recall; cost is mainly labeling time.
6. **Scale up** to block 1 (24 hours, about 46 GPU-hours) only after steps 1-5, reporting hourly totals, per-bin metrics and day/night separately.

## 10. How to reproduce
```bash
export ROOT=/orange/xiangyan/rithika/vision/vision3/best/test_colonial
cd $ROOT && source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
# one hour (array id = chunk number; 8 = 07:00-08:00):
sbatch --time=05:00:00 --export=ALL,RUN=myrun,ZONES_JSON=$ROOT/zones/colonial_north_v1.json --array=8 code/run_xclip_colonial_v16.slurm
# Excel + log:
python code/aggregate_colonial_v13.py --root $ROOT --run myrun --expect-chunks 8 \
  --gt-csv ground_truth/ground_truth_bicycle_counts_v2.csv --mapping-csv ground_truth/video_site_mapping.csv
# per-bin table / pedestrian tracks / offline sweeps:
python code/diag_colonial_v1.py --root $ROOT --mode bins --run myrun
python code/sweep_secs_v1.py --root $ROOT --run myrun --label PEDESTRIAN
python code/sweep_fusion_v2.py --root $ROOT --run myrun
# per-object accuracy (needs hand labels): template, fill true_label, eval
python code/track_truth_v1.py template --root $ROOT --run myrun --out $ROOT/validation/track_truth_myrun.csv
python code/track_truth_v1.py eval --file $ROOT/validation/track_truth_myrun.csv
```
v17 (trajectories + trails + split report; same counts as v16 with the same settings):
```bash
# whole hour, same as v16 but with the v17 script/slurm (new env vars: TRACK_THR LOST_SEC STITCH_SEC STITCH_PX TRAIL_SEC SPLIT_GAP_SEC SPLIT_PX)
sbatch --time=05:00:00 --export=ALL,RUN=myrun,ZONES_JSON=$ROOT/zones/colonial_north_v1.json --array=8 code/run_xclip_colonial_v17.slurm
# one 15-min window of an hour file: START_FRAME = first frame (+5 margin), MAX_FRAMES = STOP frame (0 = to end). 900 s = 26973 frames at 29.97 fps
bash code/submit_traj_tests_v1.sh     # the test windows below; edit it to drop windows/settings
```
Folder layout: `code/` scripts, `zones/`, `ground_truth/`, `counts/<run>/`, `annotated/<run>/<chunk>/`, `logs/<run>/`, `validation/`.

## 11. What the metrics measure (and do not)
| Metric | Measures | Limit |
|---|---|---|
| Per-bin MAE / bias / within +-1 | how close the AI count is to the human count in each 15 min | counts only: an AI miss and an AI false positive in the same bin cancel out |
| Count-matched precision / recall | approximate, from min(AI, GT) per bin | not per-object |
| X-CLIP vs RT-DETR vs combined, **count level** (`sweep_fusion_v2.py`) | which labelling rule gives counts closest to the human counts | same limit |
| **Per-object accuracy** (`track_truth_v1.py`) | accuracy, confusion matrix, precision/recall/F1 of RT-DETR, X-CLIP and the combined rule on tracks a person has labelled; detection recall including people the AI missed | needs a hand-labelled set (target 40+ real tracks); **not done yet** |

The ground truth has no per-person labels, so true per-object accuracy cannot be computed from it. Any accuracy figure for the two models
must come from the hand-labelled track set.

## 12. Is this the best approach? (brief literature check, not a systematic review)
- The overall structure (detect, track, classify, count) is the standard design for video-based bicycle/pedestrian counting. Examples:
  Kocamaz et al., "Vision-based counting of pedestrians and cyclists", WACV 2016 (a detector followed by a second stage that separates
  cyclists from pedestrians, with foreground, geometry and optical-flow cues); Shahraki et al., "A Trajectory Based Method of Automatic
  Counting of Cyclist in Traffic Video Data", Int. J. Artificial Intelligence Tools 26(4), 2017; a Louisiana DOT-funded study
  (HOG detection, tracking, classification; https://www.itskrs.its.dot.gov/node/209776).
- The unusual part here is the **zero-shot X-CLIP** classification stage (Ni et al., "Expanding Language-Image Pretrained Models for General
  Video Recognition", ECCV 2022, https://arxiv.org/abs/2208.02816). X-CLIP was built and evaluated for general action recognition,
  and its paper reports large gains in the few-shot setting when only a handful of labelled examples exist. Our clips are tiny, low-resolution
  person tracks of a few seconds, which is far from those benchmarks.
- The literature repeatedly names lighting and viewpoint as the main source of error and recommends training data covering varied
  conditions (Louisiana study above; Elshebli et al., YOLO-SORT under weather/lighting/viewpoint, ETASR). Night-time work fine-tunes
  detectors on night or infrared data (e.g. Yoshihara et al. 2024, RGB+FIR fusion with transfer learning). This matches our night failure.
- Reported accuracies are not comparable with ours: different sites, cameras and conditions. Examples for context only: an embedded
  cyclist counter reports counting accuracy of 78-82% in a real urban setting (JBCS 2026); a Pittsburgh-style classical system
  reported bicycle count error under 13% on its test sites (PBTC, SWOV record).

**Assessment, based on our own measurements:** the detector's missed riders (especially at night) are the largest loss, and the zero-shot
X-CLIP label is the second weakest link (it mislabels crossing pedestrians and flips with distance). The evidence points to
(1) fine-tuning the detector on Colonial day and night frames, (2) replacing or supplementing zero-shot X-CLIP with a classifier trained or
few-shot adapted on a small set of labelled Colonial tracks (possibly using simple physical features such as speed), and (3) reporting
per-object metrics from a hand-labelled set. These are recommendations to test, not results.

## 13. Verified results (run on the cluster 2026-10-05)

### 13a. Headline counting metric (`headline_metrics_v1.py`, runs 2+4+5, 28 bins = 7 hours; processed bins hold 27% of the 89 GT bicyclists)
| | AI vs GT | AI/GT | bias/bin | MAE/bin | within +-1 | WAPE/hour | r | approx prec / rec |
|---|---|---|---|---|---|---|---|---|
| Bicyclists, all | 18 vs 24 | 75% | -0.21 | 0.64 | 82% | 42% | 0.47 | 67% / 50% |
| Bicyclists, day (6 h) | 18 vs 21 | 86% | -0.12 | 0.62 | 83% | 33% | 0.54 | 67% / 57% |
| Bicyclists, night (1 h) | 0 vs 3 | 0% | -0.75 | 0.75 | 75% | 100% | nan | nan / 0% |
| Pedestrians, all | 31 vs 42 | 74% | -0.39 | 1.32 | 71% | 79% | 0.23 | 58% / 43% |
| Pedestrians, day | 30 vs 35 | 86% | -0.21 | 1.29 | 71% | 77% | 0.26 | 57% / 49% |
| Pedestrians, night | 1 vs 7 | 14% | -1.50 | 1.50 | 75% | 86% | 0.17 | 100% / 14% |

Pedestrian AI/GT ratio looks better than it is: the 07:00 cone hour inflates the AI count. Quote WAPE/hour and recall for pedestrians, not the ratio.

### 13b. Labelling rules at count level (`sweep_fusion_v2.py`, runs 4+5, 24 bins, 29 tracks >= 3 s; GT bic 20, ped 38)
| rule | AI bic | MAE bic | AI ped | MAE ped | MAE sum |
|---|---|---|---|---|---|
| X-CLIP only (current) | 15 | 0.62 | 14 | 1.08 | 1.71 |
| RT-DETR only (>=50% cyclist) | 5 | 0.71 | 24 | 1.00 | 1.71 |
| fused D=20 O=0.95 F=80 | 12 | 0.50 | 17 | 0.96 | 1.46 |
| X-CLIP + speed >= 40 px/s | 12 | 0.50 | 17 | 0.96 | 1.46 |
| speed only >= 40 px/s | 12 | 0.50 | 17 | 0.96 | 1.46 |

Net speed of tracks X-CLIP calls BICYCLIST: median 67 px/s; PEDESTRIAN: median 8 px/s. The fused rule differs from X-CLIP-only on 3 tracks
(chunk 011 10:43:46, chunk 013 12:56:16, chunk 014 13:17:45), all bicyclist -> pedestrian. Suggestive only (3 tracks, 24 bins). Caveat: net image
speed is low for people moving toward/away from the camera.

## 14. PENDING TASKS (not done)
1. **Hand-label the tracks (per-object accuracy). Blocked on a human, ~30-45 min.** Without it there is NO per-object accuracy for X-CLIP / RT-DETR / fused.
   The file is `validation/track_truth_runs45_v2.csv` (45 rows; the template did not overwrite the old `track_truth_runs45.csv`, which is unlabelled; always use `_v2`).
   `true_label` is currently EMPTY for all rows (any earlier labels were placeholders and were cleared; never trust a run of `eval` before real labels exist).
   How to label:
   a. Print clip + seek time per row:
      ```bash
      python - <<'EOF'
      import csv,os
      from datetime import datetime as D
      f=os.environ['ROOT']+'/validation/track_truth_runs45_v2.csv'
      for i,r in enumerate(csv.DictReader(open(f)),1):
          t=D.strptime(r['first_time'],'%Y-%m-%d %H:%M:%S')
          b=D.strptime(r['first_time'][:11]+r['bin_start']+':00','%Y-%m-%d %H:%M:%S')
          s=int((t-b).total_seconds())
          print(i, os.path.basename(r['clip_hint']), "seek", f"{s//60:02d}:{s%60:02d}" if s>=0 else "previous clip", "for", r['secs'], "s")
      EOF
      ```
   b. Watch ~10 s at each seek time. Decide from the video only: BICYCLIST, PEDESTRIAN or NOT_PERSON. Do NOT copy the model labels or GT-implied labels
      (that inflates accuracy). GT bin counts may be used as a hint only.
   c. Write labels by row number (batches OK; only listed rows change):
      ```bash
      python - <<'EOF'
      import csv,os
      f=os.environ['ROOT']+'/validation/track_truth_runs45_v2.csv'
      labels={5:'...', 15:'...'}   # row number -> BICYCLIST / PEDESTRIAN / NOT_PERSON
      rows=list(csv.DictReader(open(f))); cols=list(rows[0].keys())
      for i,l in labels.items(): rows[i-1]['true_label']=l
      w=csv.DictWriter(open(f,'w',newline=''),fieldnames=cols); w.writeheader(); w.writerows(rows)
      EOF
      ```
   d. Priority order: rows 5, 15, 17 (fused-rule flips), 20, 45 (model/speed disagreement), 16, 26, 34 (long tracks), then the rest.
   e. For each person the AI never tracked, append a row with empty `track_id` (fills detection recall); optional, do last.
   f. `python code/track_truth_v1.py eval --file $ROOT/validation/track_truth_runs45_v2.csv`. Need >= 40 labelled tracks before quoting accuracy.
2. DONE 2026-10-05: `night_dc015` (detector confidence 0.15 on 21:15-21:30) did NOT help. Night bicyclists still 0 vs 3; night pedestrians 0 vs 7
   (was 1 vs 7). Overall pedestrian recall 43% -> 40% (31 -> 30 AI vs 42 GT). One 15-min bin only, but a lower threshold does not recover riders
   the detector cannot see; this supports fine-tuning on night frames (task 5).
3. `bin2_v14b` (07:15-07:30, static filter + lower threshold): no output exists in `counts/` and no job was queued. Low priority; rerun only if the cone question matters.
4. Zones verification. The file `zones/colonial_north_v1.json` exists. Job `zones_test` (chunk 15 = 14:00-15:00) was submitted 2026-10-05 with
   `sbatch --time=05:00:00 --export=ALL,RUN=zones_test,ZONES_JSON=$ROOT/zones/colonial_north_v1.json --array=15 code/run_xclip_colonial_v16.slurm`
   (an earlier submission, job 44854360, was cancelled by mistake; check `squeue -u $USER` that the resubmission is running). When done:
   a. `grep -i zones $(ls -t $ROOT/logs/*.log | head -1)` must show "zones loaded".
   b. Run `aggregate_colonial_v13.py` with `--run zones_test --expect-chunks 15` (section 10) and check the facility column (bike lane vs sidewalk) is filled
      and vehicles outside the road zone are filtered.
   c. Compare the 14:00 hour with run4 (bicyclists 3 vs 3 GT, pedestrians 4 vs 10) to confirm zones did not remove true tracks.
   Note: the pedestrian minimum is already 3.0 s by default in the slurm script (`PED_MIN_SEC=3`); never pass `PED_MIN_SEC=1` (run5 did).
   UPDATE 2026-10-05: zones_test finished. Person counts equal run4 (bicyclists 3 vs 3 GT, pedestrians 4 vs 10 GT), so zones did not remove true person tracks (4c). 4a/4b still open: see item 13 and 15g.
5. Other strategies to test (from the literature check, section 12), in order of expected value:
   - Fine-tune RT-DETR with NIGHT frames added (current ~200-image training set is daytime only, section 3 item 7), plus more Colonial frames
     around the missed events (biggest recall loss; evaluate on whole held-out hours).
   - Replace or supplement zero-shot X-CLIP with a few-shot/trained classifier on the hand-labelled tracks, optionally with a speed feature
     (needs the labels from task 1, and more than 45 tracks to hold out a test set).
   - Optional: run X-CLIP on vehicles (car/truck/bus prompts); extra compute, low priority.
6. Fill the final comparison (X-CLIP vs RT-DETR vs fused, per-object) into this section once task 1 is done.
7. DONE 2026-10-05 (partly): v17 tracking tests read (15g). Base and lowconf gave identical counts at 12:45 and 21:15; 0 split pairs at 12:45. The tracking-id-break hypothesis is NOT supported in these two windows. Not done: any test on a pedestrian-heavy window (the 14:00 hour has 4 vs 10 pedestrians; see item 12).
8. Add direction/speed (body-heights/s, sideways motion only) as a feature for the cyclist/pedestrian decision, after task 1 labels exist to check it against. Combine with the fusion rule in section 13b.
9. Optional second detector test: `VEH_WEIGHTS=<COCO rtdetr-l.pt>` on the same windows.
10. Night: collect Colonial night frames (+ optionally NightOwls images) for fine-tuning (task 5, first bullet).
11. DONE 2026-10-05: night min-duration re-run `traj17_night_min04` (job 44875534, 36 min). Results in 15l. Short night tracks are real riders; the detector box disappears as riders get close to the camera.
12. Pedestrians at 14:00 (4 counted vs 10 in the ground truth): five pedestrian-labelled tracks of 1.2-2.4 s were filtered (15g). v16 saved no speed/direction for them. To tell walkers from riders, re-run chunk 15 with the v17 script/slurm (same settings, about 1.9 h) and read `_track_motion.csv`. README section 5 warns that short pedestrian tracks may be cyclists.
13. Finish zones verification (task 4): the log tail does not show a "zones loaded" line, the facility column or the vehicle-filter effect. Check: `grep -i zone logs/slurm_colonial_v16_44855081_15.log | head` and the facility column of `counts/zones_test/*_tracks.csv`.
14. PARTLY DONE 2026-10-05: 12:45 clip watched (15h). Still open: which of tracks 1/4/6/9 are the 2 real riders, and which pedestrian was counted twice. Use the check in 15h on `counts/traj17_base/*013*_trajectories.csv` / `_track_motion.csv`.
15. Watch the `zones_test` clips at 14:03:03, 14:26:09 and 14:27:30 (the three 100%-detector-cyclist short tracks, 15m). Real riders -> the short-track rule has support; not riders -> it needs another condition.
16. Night fine-tuning: first attempt (NightOwls mix) FAILED, see section 19. Next candidates: own Colonial night/close-to-camera frames (hand-labelled, from hours other than 21:00), and the v18 short-track rule (15m). UPDATE 2026-10-06: the night-only short-minimum setting is now implemented as v18 day/night settings (section 20); results pending (item 17).

17. **v18 day/night test (pending, not run yet).** Copy `xclip_overlay_v18_colonial.py`, `run_xclip_colonial_v18.slurm`, `submit_day_night_v1.sh` to `code/`, run `bash code/submit_day_night_v1.sh` (10 jobs, about 5 GPU-hours), then read section 20c. Never tried before: low detector confidence AND short minimum together at night; day and night settings in one run.

18. **Detector-improvement experiments (planned, NOT started).** Read section 22, answer the questions in 22h, then code gets written. Test clips proposed: night 21:15-21:30 and day 14:00-14:15.

19. **Run the v19 experiment batch (written, not yet run).** Copy the bundle, `bash code/run_all_experiments.sh`, fill in both truth files, read `exp_results/EVAL_*.md` and watch the clips. Commands in section 23c.

## 15. Session 2026-10-05: trajectories and tracking tests (v17)

### 15a. Why
Open questions from this session: (1) are some of the pedestrian misses caused by tracking-ID breaks (a walker whose track splits into two pieces, each shorter than the 3 s minimum, is never counted)? (2) can we output where each cyclist/pedestrian goes (trajectory), and use direction/speed as an extra signal? (3) is it worth switching to another detector/dataset?

### 15b. What was built (new files, nothing overwritten; v16 files untouched)
| File | Purpose |
|---|---|
| `code/xclip_overlay_v17_colonial.py` | v16 + new outputs below. Detector, tracker, X-CLIP and counting logic unchanged |
| `code/run_xclip_colonial_v17.slurm` | v16 slurm + env vars `TRACK_THR` (0.25) `LOST_SEC` (3.0) `STITCH_SEC` (5.0) `STITCH_PX` (150) `TRAIL_SEC` (5.0) `SPLIT_GAP_SEC` (8.0) `SPLIT_PX` (120). Defaults equal the script defaults |
| `code/submit_traj_tests_v1.sh` | submits the 15-min test windows (see 15d) with two tracking settings |

New outputs per video file, in `counts/<run>/`:
- `<tag>_trajectories.csv`: one row per track per frame (ground point = bottom-centre of the box, box, `coasted` flag, final label, counted). Coasted frames (optical-flow guesses) are flagged and are not used for speed/direction.
- `<tag>_track_motion.csv`: per track path and net distance (px), speed in px/s and in body-heights/s, direction (`toward_camera`, `away_from_camera`, `moving_left`, `moving_right`, `static`).
- `<tag>_split_candidates.csv`: pairs (A ends, B starts within 8 s and 120 px of where A was heading) that probably are one person whose id broke. Columns include `a_or_b_alone_passes_min` and `joined_passes_min`; rows with 0/1 are tracks that would be counted only if joined. Nothing is merged or recounted; this is a measurement.
- Annotated clips: fading trail (last `TRAIL_SEC` seconds, 0 = whole history) + arrow per **counted** person, coloured like the box. Short tracks that fail the minimum duration get no box and no trail but are in the CSVs.

### 15c. How it was tested, and limits
- Run end to end on a synthetic video with a stub detector and a stub X-CLIP (no real model, no GPU). Verified: all new CSVs written, trail drawn, a track broken by a 7 s detector blackout was reported as a split candidate, and a stationary/one-point track gives `static`. Unit tests of the motion/split helpers: a walker moving toward the camera gives `toward_camera`; a rider gives `moving_right`.
- **Not tested** with the real RT-DETR + X-CLIP on the cluster. The first real run is the real test; send the last 20 lines of a log if a job fails.
- Direction assumes larger image y = closer to the camera. Not checked against the Colonial view.
- Speed in body-heights/s is perspective-robust for sideways motion only: the synthetic walker moving toward the camera gave 0.21 body-heights/s despite moving. Do not use it for toward/away motion.
- A 15-min window starts tracking from empty at its first frame, so people already in view get new ids and edge counts can differ slightly from the whole-hour runs.

### 15d. Test windows and jobs
| Window | Hour file (chunk) | Frames (START_FRAME / MAX_FRAMES) | Why |
|---|---|---|---|
| 10:00-10:15 | 011 | 1 / 26973 | day, cyclists + pedestrians (run4) |
| 12:45-13:00 | 013 | 80924 / 0 (to end) | day; this bin over-counts (4 vs 2) in earlier runs |
| 21:15-21:30 | 022 | 26978 / 53946 | night; riders missed |

Two settings per window (RUN names):
- `traj17_base`: run4 settings (det conf 0.25, track thr 0.25, lost 3 s, stitch 5 s / 150 px).
- `traj17_lowconf`: `DET_CONF=0.10 TRACK_THR=0.30 LOST_SEC=5 STITCH_SEC=8 STITCH_PX=200`.

Submitted 2026-10-05 (job ids 44860619-44860624, order: base 011/013/022, then lowconf 011/013/022). The two chunk-011 jobs (44860619, 44860622) were cancelled on purpose (log: SIGNAL Terminated at frame ~7100), so there is NO 10:00-10:15 result. Chunks 013 and 022 finished with both settings (runtime 1703-1722 s each, about 29 min, as estimated). The earlier `zones_test` job (44855081, chunk 15) also finished (runtime 6884 s, about 1.9 h). Results: section 15g.

### 15e. Findings from reading the code (not yet measured)
- **ByteTrack's low-confidence pass was effectively off in all earlier runs.** supervision's ByteTrack matches leftover tracks against detections with confidence between 0.1 and the activation threshold. The runs used detector conf 0.25 and track threshold 0.25, so that band was empty. `traj17_lowconf` opens the band (0.10-0.30). `night_dc015` (conf 0.15, threshold 0.25) opened only a thin band and did not help at night, so expect this to help daytime fragmentation, not night blindness. Hypothesis; tested in 15g: no change in counts in the two windows, so the lowconf settings were not adopted.
- **BoT-SORT is not recommended for now.** Its camera-motion compensation has no effect with a fixed camera, and as far as I know its appearance matching is not available with RT-DETR in ultralytics (not verified here). ByteTrack parameters and the stitcher are the first things to tune.
- **Pretrained models / datasets (quick search, nothing tested):** nothing found that clearly beats the fine-tuned RT-DETR on this fixed camera. Hugging Face: one undocumented cyclist detector (`Quantum-Analytics/cyclists_detector`), not usable as evidence. NightOwls (night pedestrian dataset: 279k frames, 40 sequences, 3 countries, tracking ids, bicycle-driver class; Roboflow Universe has a ~1,500-image subset, CC BY 4.0) is the only relevant lead, for extra NIGHT training data, not as a drop-in model. Its annotations cover people higher than 50 px only, and the camera differs from Colonial. GitHub results were generic YOLO+SORT demos.
- A second, COCO-trained person detector can already be merged with the fine-tuned one: pass `VEH_WEIGHTS=<path to rtdetr-l.pt>` to the slurm (download the weights on a login node first; compute nodes may have no internet). Not run yet.

### 15f. What to read when the jobs finish
```bash
ls counts/traj17_base/ counts/traj17_lowconf/
tail -n 25 logs/slurm_colonial_v17_*.log
```
1. `Split candidates:` line in each log: how many pairs, and how many "would pass the minimum only if joined". Compare base vs lowconf. If base has several and lowconf fewer, tracking breaks matter and the lowconf settings help.
2. Compare counts of base vs lowconf and vs the old runs (run4 for 10:00, run5 for 12:00-13:00 and 21:00; note run5 used the 1.0 s pedestrian minimum, which must not be reused).
3. Watch the annotated clips: do trails follow one person without jumps? Do the pedestrian trails in 12:45 break?
4. `_track_motion.csv`: check direction against what you see in the clip.

### 15g. Results read from the logs (2026-10-05)

Only the summary lines of each log were read; the v17 CSVs were not opened (not yet shared). Facts first, then interpretation.

**Counts, v17 windows** (GT = ground truth for that 15-min bin from section 5; the 12:45 bin number comes from the earlier 4-vs-2 comparison, the night numbers from the `night_dc015` comparison):

| Window | Setting | Bicyclists | Pedestrians | Vehicles | Split pairs (would newly pass min) | GT bic / ped |
|---|---|---|---|---|---|---|
| 12:45-13:00 | base | 4 | 1 | 589 | 0 | 2 / not stated |
| 12:45-13:00 | lowconf | 4 | 1 | 552 | 0 | |
| 21:15-21:30 | base | 0 | 0 | 285 | 1 (0) | 3 / 7 |
| 21:15-21:30 | lowconf | 0 | 0 | 253 | 0 | |

- lowconf made tracks about 10-15% longer in frames at 12:45 and merged the two night fragments (frames 52789-52821 and 53020-53045 of the base run) into one 2.2 s track, still under the 3 s minimum. It lowered the vehicle count by 6-11%; which vehicle count is right was not checked (no vehicle ground truth was looked at).
- **Interpretation:** broken ids do not explain the 12:45 over-count or the night misses in these two windows; the lowconf settings gave no count benefit. Two windows only.

**12:45-13:00, four bicyclist tracks vs GT 2 (base run).** Times are clock times from the frame numbers (29.97 fps), all inside the 12:45 clip.

| Track | Time | Secs | wtd X-CLIP bicyclist | % scores detector says cyclist |
|---|---|---|---|---|
| 1 | 12:45:40-12:45:56 | 9.1 | 0.65 | 45% |
| 4 | 12:53:07-12:53:13 | 3.7 | 0.79 | 46% |
| 6 | 12:53:45-12:53:52 | 7.0 | 0.79 | 45% |
| 9 | 12:56:17-12:56:38 | 18.6 | 0.65 | 7% |
Pedestrian track 7: 12:54:53-12:55:03, 4.8 s, box 24 px tall, direction `static`. Track 9 is the first suspect for a pedestrian labelled bicyclist (detector says person 93% of the time, X-CLIP says bicyclist 0.60 unweighted); this is a suspicion from the log, not confirmed. Speeds are in `_track_motion.csv` (chunk 13), not yet read.

**Night 21:15-21:30 (base run), tracks removed by the 3 s minimum:**

| Track | Time | Secs | X-CLIP bicyclist | Detector says cyclist |
|---|---|---|---|---|
| 1 | 21:19:03 | 0.6 | 0.96 | 100% |
| 2 | 21:22:07-08 | 0.4 | 0.99 | 100% |
| 4 | 21:29:21 | 0.9 | 0.68 | 59% |
| 7 (pedestrian-labelled) | 21:29:29 | 1.0 | ped 0.59 | 100% |
The detector sees riders at night but only for under a second, and the minimum duration removes them. Track 2 is within a few seconds of the 21:22:10 rider that section 6 says had no box. Three candidates vs GT 3 bicyclists may be a coincidence: see the 14:00 evidence below. Filtered tracks are not drawn in the annotated clip, so none of this has been checked by eye.

**zones_test, chunk 15 (14:00-15:00, run 6884 s):** bicyclists 3 (GT 3), pedestrians 4 (GT 10), vehicles 2268. Person counts are the same as run4, so the zones file did not remove true person tracks. Not visible in the log tail: the "zones loaded" line, the facility column, and the effect on vehicles (task 4a/4b open).
- Filtered bicyclist-labelled tracks at 14:00: five tracks of 0.4-1.1 s with X-CLIP 0.82-0.97 (14:03:03, 14:03:05-08, 14:20:26-31, 14:26:09, 14:27:30), although the 3 counted tracks already match the GT of 3. A short bicyclist minimum would therefore add up to five bicyclists in that hour. Evidence against lowering the bicyclist minimum globally, and a reason not to read the night match too strongly.
- Filtered pedestrian-labelled tracks of 1.2-2.4 s: tracks 12 (14:12:29-33), 13 (14:12:32-34, overlaps track 12 in time), 21 (14:26:03-11), 30 (14:40:23-25), 34 (14:49:27-36). No speed or direction exists for them (v16). These could be the missing pedestrians or riders (section 5).

**Watch list (clips in `annotated/traj17_base/...0.013/` and, after item 11, the night re-run):**
- 12:45 clip at 12:45:40, 12:53:07, 12:53:45, 12:56:17: which boxes are really bicyclists (GT says 2 of 4); does each trail follow one person.
- Night re-run clip at 21:19:03, 21:22:07, 21:29:21, 21:29:29: real riders or false boxes.

### 15h. What was seen in the 12:45-13:00 clip (watched by hand, 2026-10-05)
From the screenshots of the clip (base run): **3 pedestrians and 2 bicyclists** are really in the bin. The ground truth (2 bicyclists) is right; the AI counted 4 bicyclists and 1 pedestrian.
- 1 pedestrian was **never detected**: the person walked on the grass (same miss as in section 6).
- The **last pedestrian was counted as both a pedestrian and a bicyclist** (two tracks or two labels for one person; not yet confirmed which).
- Reading: the over-count (4 vs 2) is a **labelling / duplicate-track error, not a missed-rider or tracking-break problem**. This fits 15g (0 split pairs, lowconf unchanged) and the fused rule in 13b, which flips the 12:56:16 track from bicyclist to pedestrian.
- Not yet known: which of the four bicyclist tracks (12:45:40, 12:53:07, 12:53:45, 12:56:17) are the 2 real riders. Check (speeds + direction; riders move faster, `static`/slow = walker):
```bash
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial && python - <<'PY'
import csv,glob
f=glob.glob('counts/traj17_base/*013*track_motion.csv')[0]
for r in csv.DictReader(open(f)): print(r)
PY
```
(Print first, then pick columns; do not assume field names.) If two tracks overlap in time at 12:56 with one pedestrian and one bicyclist label, that is the double-counted person.

### 15i. Are the v17 results better than the old ones?
**No, not for counts.** v17 only adds outputs (trajectories, motion, split report, trails); counts equal v16 with the same settings. Evidence: base at 12:45 = 4 bicyclists (same 4-vs-2 over-count as run5); lowconf = same counts (4 / 1) and 0 split pairs; night = 0 vs 3 in both settings; zones_test person counts = run4 (3 vs 3, 4 vs 10). What v17 gave us is **diagnosis**: it ruled out tracking-id breaks as the cause in these two windows and pointed at X-CLIP labelling and detector misses. The lowconf settings were not adopted (no count benefit; vehicle count dropped 6-11%, unchecked).

### 15j. Why the last sbatch was run
Each job answers one question and none was expected to improve counts:
- `traj17_base` / `traj17_lowconf` (chunks 13, 22): do tracking breaks or ByteTrack's low-confidence pass explain the 12:45 over-count and the night misses? Answer: no (15g).
- `traj17_night_min04` (item 11, only if you submitted it): are the sub-second night boxes real riders? It is a **probe** (bicyclist minimum 0.4 s, pedestrian 1.0 s), not a candidate setting: at 14:00 a 0.4 s minimum would add up to 5 false bicyclists. Read it by watching 21:19:03, 21:22:07, 21:29:21, 21:29:29.
- Chunk 15 re-run with v17 (item 12): only to get speed/direction for the 5 filtered short pedestrian tracks at 14:00.
If you submitted something else, check with `squeue -u $USER -o "%i %j %T %M"` and the `--export` line in your shell history.

### 15k. All v17 window counts in one table (AI counts; GT = ground truth; "seen" = counted by eye in the clip)
| Window | Run (settings) | Bicyclists | Pedestrians | Vehicles | GT bic / ped | Seen in clip (bic / ped) |
|---|---|---|---|---|---|---|
| 12:45-13:00 | old run5 (min ped 1.0 s) | 4 | not stated per bin | n/a | 2 / not stated | |
| 12:45-13:00 | `traj17_base` (run4 settings, min 3 s) | 4 | 1 | 589 | 2 / not stated | 2 / 3 (1 ped on grass never detected; last ped counted as both ped and bicyclist) |
| 12:45-13:00 | `traj17_lowconf` | 4 | 1 | 552 | | |
| 21:15-21:30 | old `night_dc015` (det conf 0.15, min 3 s) | 0 | 0 | n/a | 3 / 7 | |
| 21:15-21:30 | `traj17_base` (min 3 s) | 0 | 0 | 285 | 3 / 7 | 5 / not counted |
| 21:15-21:30 | `traj17_lowconf` | 0 | 0 | 253 | | |
| 21:15-21:30 | `traj17_night_min04` (bic min 0.4 s, ped min 1.0 s) | 3 | 1 | 285 | 3 / 7 | 5 / not counted |
| 10:00-10:15 | not run (jobs cancelled on purpose) | | | | | |
| 14:00-15:00 (whole hour, v16, zones) | `zones_test` | 3 | 4 | 2268 | 3 / 10 | |

Reading: with the same settings v17 counts equal v16/run4/run5 (no count improvement; v17 adds outputs). The only setting that changed counts is the short night minimum (0 -> 3 bicyclists). Vehicle counts differ between base and lowconf (589 vs 552, 285 vs 253) and were not checked against any truth.

### 15l. Night re-run `traj17_night_min04` (21:15-21:30; clip watched 2026-10-05)
Counted tracks (log): bicyclists 3, pedestrians 1, vehicles 285. Split candidates: 1 pair, 0 would pass the 0.4 s minimum only if joined. Counted tracks by (X-CLIP label, direction): bicyclist/moving_right 2, bicyclist/toward_camera 1, pedestrian/moving_right 1.

| Track | Frames | Secs | Mean box h (px) | wtd X-CLIP bic / ped | Detector says cyclist | Final label | What the clip shows |
|---|---|---|---|---|---|---|---|
| 1 | 34263-34272 | 0.6 | 54 | 0.95 / 0.05 | 100% | BICYCLIST | real rider (9:19:05) |
| 2 | 39790-39810 | 0.4 | 93 | 0.99 / 0.01 | 100% | BICYCLIST | real rider (9:22:09) |
| 4 | 52789-52821 | 0.9 | 76 | 0.70 / 0.30 | 59% | BICYCLIST | real rider on sidewalk (9:29:24) |
| 7 | 53020-53045 | 1.0 | 75 | 0.41 / 0.59 | 100% | PEDESTRIAN | rider (clip label at 9:29:31 reads BICYCLIST, X-CLIP 0.62 / 0.38 on that frame; the final label uses the whole-track weighted score) |

Findings:
- The 3 bicyclist-labelled short tracks (1, 2, 4) are real riders, so the 3 s minimum was hiding real night riders. Track 7 is also a rider but was finally labelled pedestrian by weighted X-CLIP; the detector's 100% cyclist share was right. With track 7 counted as a rider the AI finds 4 bicyclists.
- **The clip shows 5 cyclists; the AI finds 4 at best, so at least 1 is still missed.** The detector draws a box at night but loses it as the rider gets close to the camera, so the track lasts about 1 s (screenshot 9:29:26: rider visible, no box). A tracker cannot join across a gap in which the detector sees nothing.
- The ground truth (3) is below what is visible (5). "AI 3 vs GT 3" is therefore not evidence of agreement; compare with what is seen in the video.
- Guess, not tested: close-up, top-down views are rare in the roughly 200 daytime training images.

### 15m. 14:00 short bicyclist-labelled tracks, detector share (from the `zones_test` log; filtered by the 3 s minimum)
| Track | Frames | Secs | wtd X-CLIP bic | Detector says cyclist | Watched? |
|---|---|---|---|---|---|
| 1 | 5514-5517 | 0.4 | 0.92 | 100% | no (14:03:03) |
| 2 | 5557-5655 | 1.1 | 0.85 | 3% | no (14:03:05-08) |
| 15 | 36766-36899 | 1.1 | 0.90 | 3% | no (14:20:26-31) |
| 24 | 47035-47044 | 0.6 | 0.82 | 100% | no (14:26:09) |
| 28 | 49476-49479 | 0.4 | 0.97 | 100% | no (14:27:30) |
Tracks 1 and 28 have only 2 X-CLIP scores each, so their X-CLIP values carry almost no information.

**Candidate rule (hypothesis, not implemented, not validated):** count a bicyclist track shorter than 3 s only if the detector calls it a cyclist at least about 90% of the time (and let the detector share override X-CLIP on such short tracks). Applied to the data above:
- Night: keeps tracks 1, 2 and 7 (7 becomes a bicyclist); drops track 4 (59%), which is a real rider. Net: 3 of 4 real short riders.
- 14:00: keeps tracks 1, 24 and 28 (100%), drops 2 and 15 (3%). Those three would raise 14:00 from 3 to 6 bicyclists against a GT of 3. Whether they are real riders (the GT may under-count as at night) is **unknown until the clip is watched**.
Do not implement before watching 14:03:03, 14:26:09 and 14:27:30 in the `zones_test` clip(s).

## 16. Estimated time to run all 48 hours (v17 script, current settings)
**Basis (measured, not extrapolated from guesses):**
| Measurement | Value |
|---|---|
| One full hourly file (`zones_test`, chunk 15, 14:00, 2268 vehicles) | 6884 s = 1.91 h on 1 GPU |
| One 15-min window (`traj17_*`, chunks 13 and 22, day and night) | 1703-1722 s = 28.7 min, i.e. about 1.9 h per hour |
| Frames per hour file | about 107,850 (29.97 fps) |
Runtime is nearly the same at day and night (night window 285 vehicles, day 589, both about 29 min), so cost is dominated by per-frame detection, not by how many objects are tracked.

**Total compute:** 48 h x 1.9 h = **about 92 GPU-hours** (about 3.8 GPU-days). This matches the earlier "block 1, 24 hours, about 46 GPU-hours". Allow +-20%: only 4 distinct hours were timed and X-CLIP time grows with the number of person tracks (busier hours, e.g. rush hour, may run longer).

**Wall-clock time depends only on how many GPUs run at once** (array tasks), plus queue wait:
| Concurrent GPUs | Wall time (approx.) |
|---|---|
| 48 (whole array at once) | about 2 h |
| 24 | about 4 h |
| 12 | about 8 h |
| 8 | about 12 h |
| 4 | about 23 h |
| 1 | about 3.8 days |
Not included: queue wait, the aggregation step (`aggregate_colonial_v13.py`, minutes), and the time to watch clips. `--time=05:00:00` per task leaves 2.6x margin over the 1.9 h measured. Disk use of 48 hours of annotated clips plus the new v17 CSVs (`_trajectories.csv` has one row per track per frame) was **not measured**; check `du -sh annotated/traj17_base counts/traj17_base` first.

**Recommendation (unchanged from section 9):** do not run all 48 hours yet. The result would be a larger version of the same night and pedestrian failures. Run block 1 (24 h, about 46 GPU-hours) only after the hand labels, the night fine-tuning and the label-fusion decision. Command when ready (new RUN name, v17 files, zones on):
```bash
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
sbatch --time=05:00:00 --export=ALL,RUN=full_b1,ZONES_JSON=$PWD/zones/colonial_north_v1.json --array=1-24 code/run_xclip_colonial_v17.slurm
sbatch --time=05:00:00 --export=ALL,RUN=full_b2,ZONES_JSON=$PWD/zones/colonial_north_v1.json --array=25-48 code/run_xclip_colonial_v17.slurm
```
To cap concurrency (fair-share), append `%8` to the array, e.g. `--array=1-24%8`.

## 17. Wording: "trajectory" (past vs future)
In tracking literature a **trajectory (track)** is the *recorded past path* of an object: the sequence of positions from first to latest frame. What we draw (fading trail behind the person, arrow head and dot at the newest point) is exactly that, so it is correct to see the line following the person. **Trajectory prediction** is a different task: forecasting future positions; it is not implemented here and the arrow is not a prediction. In this project: `_trajectories.csv` = past positions per frame; `_track_motion.csv` = summary of that path (net distance, speed, direction).

## 18. Fine-tuning plan (night + close-to-camera); nothing trained yet
Goal: fix the two detector losses seen in 15l: no box at night, and the box vanishing as a rider nears the camera.
**Data, in order of expected value:**
1. **Colonial frames, labelled by hand** (same camera, same view): night frames and close-to-camera frames of riders and pedestrians. Take them from hours **other than 21:00**, so that the 21:00 hour stays a clean held-out test (the only night hour validated so far).
2. **NightOwls** (night pedestrian dataset; Roboflow Universe has a ~1,500-image subset under CC BY 4.0; the full set needs registration on its site). Limits: people taller than 50 px only, different cameras, and **no car/truck/bus labels**.
**Risks to handle:**
- Training only on NightOwls would teach the detector that cars/trucks/buses in those images are background and could hurt vehicle detection. Always train on NightOwls **mixed with the existing rtdetr_v3 training set** (which has vehicle labels), starting from the `rtdetr_v3` weights, and re-check vehicle counts afterwards.
- Class mapping needed (pedestrian -> person, bicycledriver -> cyclist, others dropped); check the exported class names before mapping.
- Test on whole held-out hours, day and night, so that daytime does not get worse.
**Blocked on:** `args.yaml` of the `rtdetr_v3` run and the dataset yaml (so the new training reuses the same settings), and a GPU job on HiPerGator (no training can run in this chat).
```bash
cat /orange/xiangyan/rithika/vision/vision3/runs/detect/finetune_runs/rtdetr_v3/args.yaml
```

## 19. Experiment: fine-tune with NightOwls (`rtdetr_v4_night`), result: worse, not adopted
**What was done (new files only; `rtdetr_v3`, v17 script and slurm untouched):**
- `code/build_merged_dataset_v1.py`: base `roboflow_split_v1` train (437 images, repeated x3) + 400 random NightOwls images (Roboflow `nightowls-koyno`, YOLOv8 export, licence CC BY 4.0 per its data.yaml; classes bicycledriver->cyclist, pedestrian->person, `ignore` dropped) -> `dataset_frames/merged_night_v1/`. Train boxes per class: car 3390, person 759, cyclist 164, truck 102, bus 24, other_vehicle 24.
- `code/train_rtdetr_night_v1.py` + `.slurm`: start from `rtdetr_v3/best.pt`, AdamW lr0 1e-4, imgsz 640, batch 8, seed 42, up to 50 epochs, patience 15 -> `runs/detect/finetune_runs/rtdetr_v4_night` (stopped at epoch 47, 55 min).

**Daytime validation (54 images, 218 instances; only 8 cyclists, 8 persons, 6 trucks, so noisy):** car mAP50-95 0.763 -> 0.758, cyclist 0.947 -> 0.945, person 0.345 -> 0.312, truck 0.074 -> 0.230, all 0.532 -> 0.561 (gain comes from 6 truck instances). Conclusion: this val set cannot show a night effect and showed no daytime damage.

**Real windows (same settings as the reference runs; only WEIGHTS changed):**
| Window | rtdetr_v3 reference | rtdetr_v4_night |
|---|---|---|
| 21:15-21:30, bicyclists / pedestrians / vehicles (min 0.4 s / 1.0 s) | 3 / 1 / 285 (`traj17_night_min04`) | 0 / 0 / 141 (`traj17_night_v4`, job 44890080) |
| 12:45-13:00, bicyclists / pedestrians / vehicles (min 3 s) | 4 / 1 / 589 (`traj17_base`) | 1 / 1 / 350 (`traj17_day_v4`, job 44890081) |
Seen by eye: night 5 cyclists (GT 3), day 2 bicyclists + 3 pedestrians (GT 2 bicyclists).

**Why it failed at night (log of `traj17_night_v4`):** the person-track table has a single track of 2 frames (0.1 s, never scored). Raw detector detections (conf >= 0.25): car 10620, cyclist 18, truck 74, person 1, other_vehicle 5. So the **detector itself stopped finding the riders** (tracker/filters are not the cause). Same line from the v3 run (`traj17_night_min04`, job 44875534), raw detections (conf >= 0.25, counted per frame) v3 -> v4: car 82472 -> 10620 (-87%), truck 1947 -> 74 (-96%), person 106 -> 1 (-99%), cyclist 132 -> 18 (-86%), bus 14 -> 0, other_vehicle 5 -> 5. **Every class collapsed, not only riders.** Counted vehicles fell less (285 -> 141) because tracks persist across frames. A drop this uniform looks like a general loss of detector confidence at night (scores below 0.25) rather than a class-specific problem; untested way to check: rerun `traj17_night_v4` with `DET_CONF=0.10` and see whether the riders reappear (even if they do, v4 is still not better than v3 at the 0.25 setting).
**Vehicles dropped 41-51%.** Hypothesis (not proven): NightOwls images have no car/truck/bus labels, so the model learned to treat unlabelled vehicles as background. The rider loss is not explained by that hypothesis; a domain gap (NightOwls camera angle, rider size, lighting) is another possibility. Not tested.

**Decision:** v4 is not used. Pseudo-labelling vehicles on NightOwls (run v3 on the images and add its car/truck/bus boxes) would address only the vehicle part and does not address the rider loss, so it is not the next step. Next: (a) the v18 short-track rule on v3 (needs the 14:03:03, 14:26:09, 14:27:30 clips watched first), (b) hand-label Colonial night and close-to-camera frames from hours other than 21:00 (same camera view), then retrain from v3 on base + those frames only, test on 21:15 and 12:45.

## 20. v18: separate day and night settings (code written and run 2026-10-06)
**Why.** Section 15l: a 0.4 s bicyclist minimum finds the real night riders (0 -> 3), but section 15m: the same minimum at 14:00 could add up to 5 unchecked short tracks to 3 counted (GT 3). So the short minimum should apply only at night, and 3 s should stay by day. Tried before: lower detector confidence alone (`night_dc015`, no change), looser tracking (`traj17_lowconf`, no change), short minimum alone (`traj17_night_min04`, 3 cyclists). Never tried: low confidence + short minimum together, or both settings in one run.

**20a. What was built (new files; v17 untouched).**
| File | What |
|---|---|
| `code/xclip_overlay_v18_colonial.py` | v17 + options `--night-start HH:MM --night-end HH:MM` (may cross midnight) and `--night-det-conf`, `--night-bic-min-sec`, `--night-ped-min-sec`. Omitted night values fall back to the day values. All unset = identical to v17 |
| `code/run_xclip_colonial_v18.slurm` | v17 slurm + env vars `NIGHT_START NIGHT_END NIGHT_DET_CONF NIGHT_BIC_MIN_SEC NIGHT_PED_MIN_SEC` (only passed if `NIGHT_START` is set) |
| `code/submit_day_night_v1.sh` | submits the test below |
How it works: detector confidence switches per frame by the clock time of that frame. A track counts as night if the clock time of its MIDDLE frame is in the night period; then the night minimum seconds apply (bicyclist or pedestrian, by X-CLIP's label). The night log line `night mode ON ...` is printed at the start of a run.
Checked: `py_compile` of the script, `bash -n` of both shell files, and the night-period logic at the boundaries (20:59 day, 21:00 night, 06:00 day, crossing midnight). **Not tested with the real RT-DETR + X-CLIP on the cluster.** If a job fails, send the last 20 lines of its log.

**20b. The test (10 jobs, about 30 min each, about 5 GPU-hours).** Two runs on the same five 15-minute windows:
- `sw_day`: no night mode (3 s, detector conf 0.25 everywhere; same as `traj17_base`).
- `sw_switch`: night mode 21:00-06:00 with `NIGHT_DET_CONF=0.15`, `NIGHT_BIC_MIN_SEC=0.4`, `NIGHT_PED_MIN_SEC=1.0`; day settings outside that period.
| Window | Chunk | Frames (START / STOP) | Purpose |
|---|---|---|---|
| 10:00-10:15 | 11 | 1 / 26973 | day, cyclists + pedestrians |
| 12:45-13:00 | 13 | 80924 / 0 | day, the 4-vs-2 over-count bin |
| 14:00-14:15 | 15 | 1 / 26973 | day, contains the short 'cyclist' tracks at 14:03 |
| 21:15-21:30 | 22 | 26978 / 53946 | night; the window the night settings were picked on (a gain here is not proof) |
| 22:00-22:15 | 23 | 1 / 26973 | night; NOT used to pick the settings (the fair test; GT for this bin is not in this README, compare with the GT file) |
Night settings are my picks from the earlier probes, not tuned together. Only 21:00 has been verified as dark; dusk and dawn are unchecked (`NIGHT_START/NIGHT_END` can be changed). Lower confidence also applies to vehicle detections at night, so night vehicle counts can change (not checked against any truth).

**20c. How to read it (when the jobs finish).**
```bash
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
grep -i "night mode" logs/slurm_colonial_v18_*.log      # sw_switch logs only
tail -n 25 logs/slurm_colonial_v18_*.log                 # counts and Split candidates lines
ls counts/sw_day counts/sw_switch; ls annotated/sw_day annotated/sw_switch
```
1. **Day windows (10:00, 12:45, 14:00): counts must be identical in `sw_day` and `sw_switch`.** If not, the switch is leaking into day: stop and debug.
2. **Night windows:** compare bicyclists / pedestrians / vehicles, `sw_day` vs `sw_switch`, against GT and against what is seen in the clip (21:15 clip shows 5 cyclists, GT 3). Watch the 21:15 and 22:00 clips in both runs.
3. **22:00 is the test that counts.** Judge by eye in the clip plus the GT; false boxes at night would show as boxes on non-people.
4. Report what was seen in the clips, not only GT agreement: GT is imperfect (section 6, 15l).

**20d. Results (runs finished 2026-10-06; counts from the slurm logs, each run 29-30 min).**
| Window | `sw_day` bic / ped / veh | `sw_switch` bic / ped / veh |
|---|---|---|
| 10:00-10:15 | 0 / 0 / 441 | 0 / 0 / 441 |
| 12:45-13:00 | 4 / 1 / 589 | 4 / 1 / 589 |
| 14:00-14:15 | 1 / 2 / 612 | 1 / 2 / 612 |
| 21:15-21:30 | 0 / 0 / 285 | 3 / 1 / 279 |
| 22:00-22:15 | 0 / 0 / 467 | 0 / 0 / 464 |
- **Day stays at 3 s:** the three day windows have identical counts AND identical person-track tables in both runs (the switch does not leak into day). At 14:00 the 0.4 s and 1.1 s 'cyclist' tracks (frames 5514-5517 and 5557-5655) are still filtered.
- **21:15:** `sw_switch` counted 3 bicyclists (tracks of 0.6, 0.5, 1.0 s) + 1 pedestrian (1.1 s, detector says cyclist in 100% of frames). Same as the earlier `traj17_night_min04` probe. **Section 21 shows one of the 3 'bicyclists' is a motorcycle, so '3 vs 3 human' is partly a coincidence, not a clean match.**
- **22:00:** 0 in both runs; two short tracks (0.4 s, 0.5 s) were labelled pedestrian and filtered by the 1.0 s pedestrian minimum; one of them has detector = cyclist in 100% of frames. Visual truth for this window: see section 21 (not yet reviewed if not listed there).
- **Detector confidence 0.15 did little for people**: person tracks at 21:15 are almost the same as baseline; raw car detections rose from 82k to 140k, final vehicles 285 -> 279. The short minimum did the work.
- **Log label bug (not fixed yet):** in night mode the line 'Raw detector detections by class (conf>=0.25)' actually counts detections down to 0.15.

## 21. Rithika's own observations from watching the annotated clips (2026-10-06): VISUAL GROUND TRUTH
**Use this section as the ground truth for these clips; do not ask for it again.** These come from watching the mp4s by eye (the human counts in the GT file are known to be inconsistent, section 6 and 15l). Where this conflicts with my earlier notes from reading logs (15l, 15m), this section wins. Wording is hers, lightly tidied; nothing here was inferred from logs unless marked.
| Clip | What she saw |
|---|---|
| `sw_day` 12:45-13:00 (same for `sw_switch`, identical counts) | 2 cyclists and 3 pedestrians really present. The model called **2 pedestrians cyclists** (so the 4 counted bicyclists = 2 real + 2 pedestrians). A pedestrian walking on the grass was not counted. Screenshot of id 1: 'FINAL: BICYCLIST', RT-DETR person 0.55 (45% cyclist) DISAGREE, X-CLIP bicy 0.74 / pede 0.26, a person walking on foot near the road edge. (The 45% cyclist, id 1 matches the 12:45:40 track in the log; that matching is mine.) This resolves the 'which 2 of the 4 are real' question left open earlier: the 2 mislabelled ones are pedestrians. |
| `sw_day` 14:00-14:15 | A pedestrian walking away from the camera was not counted. 1 cyclist seen. 1 pedestrian was counted as a cyclist. 2 pedestrians were not detected at all. (Her follow-up, 2026-10-06: yes, the real cyclist AND a pedestrian were both labelled cyclist. The log has only ONE counted bicyclist (track 5, 4.0 s, frames 16521-16717, about 9:11 in the clip) plus two FILTERED 'was BICYCLIST' tracks at 14:03 (0.4 s frames 5514-5517 and 1.1 s frames 5557-5655, about 3:04-3:09). So most likely the real cyclist = the short filtered 14:03 tracks (dropped by the 3 s minimum, i.e. a fast rider can be lost by day too) and counted track 5 = the pedestrian labelled cyclist. That mapping is MY inference from her answer, not something she stated: verify at those two times.) **CORRECTION 2026-10-08 (her truth file): that inference was WRONG.** Her truth file says the 4.0 s track at 9:11-9:17 (counted BICYCLIST) IS the real cyclist (correct), and the short 0.4 s + 1.1 s tracks at 3:04-3:08 are a PEDESTRIAN that the model called a bicyclist. Her totals for the 14:00 clip: 4 pedestrians + 1 cyclist (a pedestrian walking away at 3:02, the pedestrian above at 3:04-3:08, and 2 pedestrians never detected at about 12:12). So there is NO evidence at 14:00 that the 3 s minimum loses a real fast cyclist; and the two model-counted pedestrians (3:15-3:18 and 11:45-12:17) are not in her total: unresolved (false detections, or the same people?) **RESOLVED 2026-10-08 (her answer): both are real.** FINAL 14:00 TRUTH (video position, also in `truth/day_1400_truth.csv`): (1) cyclist 9:10-9:19 = the 4.0 s track, counted correctly; (2) pedestrian 3:00-3:25, walking away and VERY far from the camera = the 0.4 s + 1.1 s tracks at 3:04-3:08 (called BICYCLIST, filtered, so no false count) AND the 3.2 s track at 3:15-3:18 (counted PEDESTRIAN); (3) pedestrian 11:45-12:14 = the 16.9 s track (counted PEDESTRIAN); (4) and (5) two pedestrians arriving together 12:10-12:37, mostly not detected; the two filtered 2.1 s and 1.2 s PEDESTRIAN tracks at 12:29-12:35 probably belong to them. So the `sw_day` baseline at 14:00 = cyclist 1/1 found, pedestrians 2/4 found, 2 detected but dropped by the 3 s minimum, 0 false people (preview computed from the log times, +-1 s). |
| `sw_day` 21:15-21:30 (she wrote '1215-1230'; CONFIRMED by her 2026-10-06: it is 21:15-21:30) | 3 cyclists, 1 motorcycle and 1 pedestrian present; **none were detected/counted** (log: 0 / 0). |
| `sw_switch` night clip (window not stated, presumably 21:15-21:30) | A **motorcycle was detected but labelled cyclist**. A cyclist was detected but the box did not follow the cyclist throughout. A cyclist was missed. A cyclist was counted. A cyclist was detected but labelled pedestrian. The last pedestrian was not detected. |
What this changes:
- At 21:15 the 3 'bicyclists' of `sw_switch` include a motorcycle, so the short-minimum rule can let a motorcycle in as a cyclist (a new error type, not seen before).
- At 21:15 the people present are 3 cyclists + 1 motorcycle + 1 pedestrian (the older '5 cyclists' note counted the motorcycle and pedestrian as cyclists).
- Pedestrian misses are mostly **detector** misses (never detected), not tracking or label misses: grass at 12:45, walking away from camera at 14:00, last pedestrian at night.
- Pedestrians labelled cyclist is the main daytime error at 12:45 (2 of 4 'cyclists').
- 14:00 final (see the correction above): the two late pedestrians (12:29-12:35) ARE tracked but only for 2.1 s and 1.2 s, so the 3 s PEDESTRIAN minimum drops them. No experiment in v19 tests a shorter pedestrian minimum (`exp3b_short` is cyclist-only): candidate for a later run.
- Not yet reviewed: `sw_day` 10:00-10:15 and `sw_switch` 22:00-22:15 (22:00 counted 0 in both runs; is there a real rider at about 10:04 / 10:12 in the clip?).

## 22. PLAN: experiments to fix the failures seen in section 21 (written 2026-10-06 for review; NO CODE WRITTEN YET)
Source: Rithika's request to try several SOTA ideas on two 15-minute clips (one night, one day), combining (a) an outside plan she pasted (SAHI, temporal detector, low-light enhancement, fine-tuning, BNE-DETR) and (b) my own suggestions (motion candidates, speed-based relabelling, motorcycle guard, tracker gap-bridging, night augmentation). Fallback she stated: if nothing works, add her annotated images (fine-tuning, experiment E4).

**22a. Principle.** `rtdetr_v3` + the current v17 pipeline is the CONTROL. Change ONE thing at a time, run it on exactly the same clips, record which failure from section 21 it fixes or breaks. Only after that, combine the winners. Reason: so far every result has been a count; a count can look right for the wrong reason (21:15 'bicyclists 3 vs 3 human' included a motorcycle).

**22b. Test clips.**
| Role | Clip | Why | Status |
|---|---|---|---|
| Night | 21:15-21:30 (chunk 22, frames 26978 / 53946) | full visual truth known (3 cyclists, 1 motorcycle, 1 pedestrian, section 21) | proposed, confirm |
| Day | 14:00-14:15 (chunk 15, frames 1 / 26973) | contains: pedestrian walking away (missed), 2 pedestrians never detected, a pedestrian labelled cyclist, [older note, WRONG, see section 21 correction: the 14:03 short tracks are a pedestrian, not a lost cyclist] | proposed, confirm (alternative: 12:45-13:00, which has the grass pedestrian and 2 pedestrians labelled cyclist) |
- **Controls already run, no need to rerun:** `sw_day` (= v17 settings) and `sw_switch` (= v18 night rule) on both clips (counts in 20d).
- **Overfitting warning:** two clips that were studied by eye are a development set, not a test set. Anything that wins is 'promising', not 'proven'. Keep untouched windows for a later check: 22:00-22:15 (already exists, unreviewed) and one more day window (to choose, e.g. 10:00 or 16:00).
- **Rule for E4 (fine-tuning):** never train on frames from the two test clips (or the hold-out windows). Take training frames from other hours/days. If the only labelled frames are from the test clips, say so and report the result as 'trained on the test clip', not as a test.

**22c. Truth file and metrics (new).** One file per clip, `truth/<clip>_truth.csv`, one row per real person/vehicle, written by Rithika from watching the clip:
`id, start_mmss, end_mmss, class (cyclist | pedestrian | motorcycle), where/direction, notes`
- Pre-fill from section 21. 21:15: 3 cyclists + 1 motorcycle + 1 pedestrian (times to add). 14:00: only partial (walking-away pedestrian, 2 undetected pedestrians, 1 cyclist, 1 pedestrian labelled cyclist, counted pedestrians): she must complete the list.
- For every run record, per clip: true people found (by class), missed, wrong class, motorcycles counted as cyclists, false boxes (non-people), and the counts. Precision/recall only once the truth file is complete. A time-overlap matcher (`eval_truth.py`, to be written) compares `*_tracks.csv` with the truth file; no mAP needed.
- Record GPU time per run (baseline: about 29-30 min for one 15-min window).

**22d. Experiments.** Order is by cost and by how directly it hits a section 21 failure.
| ID | What changes | Question | Training | Notes / risk |
|---|---|---|---|---|
| E0 | nothing (`rtdetr_v3`, v17 settings) | what are the current errors? | no | CONTROL. Also keep `sw_switch` as control 0b |
| E1 | SAHI: slice each frame, detect per slice, merge (with the full-frame pass kept) | does slicing recover small/far people (walking away, grass, night)? | no | Wrapper around the same weights; SAHI documents an RT-DETR mode and a full-image pass in addition to the slices. Cost: several times more forward passes per frame, so runtime goes up by roughly the number of slices (restrict to the road zones to cut it). Risk: duplicate boxes / more false boxes; check big close cyclists are not hurt |
| E2 | low-light enhancement before the same detector, night clip only | does brightening recover night people? | no at first | Order: gamma/contrast (CLAHE) as a sanity test, then Zero-DCE/Zero-DCE++ (as suggested in the pasted plan; not checked by me). Judge by 'were missed people boxed', NOT by how the video looks. Risk: noise and headlight glare create false boxes |
| E3 | motion candidates + post-rules (my addition) | can motion and speed fix wrong labels and find moving people the detector misses? | no | (a) frame-difference / background-subtraction blobs inside the road zones as extra candidates; (b) R1: relabel by speed/direction from `track_motion.csv` (walker slow, rider faster, motorcycle fastest); (c) R2: motorcycle guard (speed/size ceiling before a night short-track counts as a cyclist); (d) R3: day exception for short, fast, high-confidence cyclist tracks (the 14:03 case). Literature: motion-difference maps fused into a detector (YOLOMG, 2025), flow-aligned multi-frame features for micromobility (Montréal, 2024). Limit: weak for slow walkers and for walking AWAY from the camera. Needs a calibration of speed thresholds on hand-labelled tracks (small sample) |
| E4 | fine-tune `rtdetr_v3` on Colonial hard cases | can the model learn this camera? | YES | Output `rtdetr_v5_colonial`. Add a motorcycle class. Hard cases: DAY: walking away, tiny/far pedestrian, tiny/far cyclist, close cyclist, motorcycle, pedestrian mistaken for cyclist, shadow/grass. NIGHT: cyclist, pedestrian, motorcycle, far, close, partially visible. Optional night augmentation of day frames (training-free NightAug-style, or day-to-night translation that keeps the labels). Lesson from the NightOwls attempt (section 19): train on THIS camera's failures, not other cameras. Highest expected value, and the stated fallback |
| E5 | temporal detector on stacks of frames | does history keep people from 'disappearing'? | YES (heavy) | Corsel et al., WACV Workshops 2023: YOLOv5-based, processes frame sequences from static cameras, two-stream variant uses frame differences; they report tiny moving objects down to 4x4 px. A separate branch, not a replacement. Needs labelled sequences, so do after E4. Context R-CNN (per-camera memory) is an alternative. I did not verify the other numbers in the pasted plan (Temporal-YOLOv8 '+0.21 mAP', FAIM '87.9% mAP'): do not quote them |
| E6 | BNE-DETR (night RT-DETR variant) vs best model, night only | does a night-specific architecture beat ours? | YES | MDPI Sensors 2026, 26(1):260, visible light, tested on LLVIP: +1.9 precision, +2.5 recall, +1.9 mAP50 over RT-DETR-R18. LLVIP is a pedestrian-only, night-only dataset; ours is multi-class (pedestrian, cyclist, motorcycle, vehicles), so treat it as a research benchmark, not a drop-in. To be fair it must be trained on our data like E4 |
| E7 | tracker gap-bridging with a mask tracker (my addition) | can lost boxes be continued (the cyclist whose box did not follow)? | no | SAMURAI (SAM 2 + motion-aware memory, zero-shot). Made for single-object tracking benchmarks; not tested on tiny night video. Trial only |
| E8 | COMBINE only the winners | do gains stack? | depends | LAST. Possibly different pipelines for day and night |

**22e. Phases.**
1. No training: E0 (already run), E1 SAHI, E2 enhancement (night), E3 motion + rules.
2. Data/model: build the hard-case annotations, E4 fine-tune, test on untouched windows.
3. Temporal: E5 (and E7 if still needed).
4. Night architecture benchmark: E6 vs the best of E4.
5. Ablation and combination (E8), with the untouched windows.

**22f. What counts as a win.** Per clip, compare to the control with the truth file: more true people found without more false boxes or class errors. With two clips this is anecdotal, so report results as 'promising' until the hold-out windows agree. Report failures too (what got worse).

**22g. Honest caveats.** (1) Only two clips, both studied by eye. (2) The v18 night rule may be redundant if E4/E5 recovers the people. (3) SAHI and enhancement may add false boxes at night (headlights, noise). (4) Walking-away pedestrians are small, slow and low-resolution; motion cues may not help them, only SAHI or fine-tuning might. (5) The human counts are known to be inconsistent (section 6), so judge by the truth file, not the count file.

**22h. Questions to confirm before any code is written.**
1. Day clip: 14:00-14:15 (proposed) or 12:45-13:00?
2. Night clip: 21:15-21:30 (proposed). OK to keep 22:00-22:15 as an untouched hold-out?
3. Will you fill in the truth files for both clips (time + class per person)? 21:15 is almost complete, 14:00 is not.
4. SAHI: OK to start with 640x640 slices, 20% overlap, plus the full-frame pass, limited to the road zones?
5. Count motorcycles as their own class in outputs from now on (they are neither cyclists nor vehicles in the counts)?
6. GPU budget: E1 will take several times the baseline 30 min per clip.
7. Name/version for the code: new files (e.g. `xclip_overlay_v19_colonial.py` with SAHI/enhancement flags, `eval_truth.py`, one submit script per experiment); v17 and v18 stay untouched.

**22i. What gets written after approval (nothing yet).** v19 script with `--sahi`, `--enhance {none,clahe,zerodce}` and an optional motion-candidate/rule module (all off by default so counts equal v17/v18); `eval_truth.py`; `submit_exp_v1.sh` running E1-E3 on the two clips; later the E4 training script and dataset-export script that excludes the test clips.

## 23. v19: experiment code for E1-E3 (written 2026-10-08; unit-tested off-cluster only, NOT yet run on the cluster)
**23a. Decisions taken for Rithika (she said: if unsure, do what research suggests).**
- Clips: NIGHT 21:15-21:30 (chunk 22, frames 26978-53946) and DAY 14:00-14:15 (chunk 15, frames 1-26973). 22:00-22:15 stays an untouched hold-out and is NOT in this batch.
- Motorcycles count as cyclists for now: truth class `motorcycle` is scored as `cyclist`; no motorcycle guard is applied (the audit file only records speed so one can be added later).
- SAHI is implemented in the script itself (slice + full-frame pass + duplicate merge), not through the `sahi` package: same method, no new dependency, identical output format. 640 px slices, 20% overlap over the WHOLE frame (people also walk on grass outside the zones), 8 slices + 1 full pass per frame = about 3x the baseline detector cost. People only: vehicles still come from the full-frame pass, so vehicle counts are not confounded.
- Enhancement is applied to the frame given to the DETECTOR only, and only to night frames. X-CLIP crops stay original (add `ENHANCE_CROPS=1` to change that). Zero-DCE uses the official `Epoch99.pth` (320 KB, shipped in the bundle; layer names checked against the checkpoint).
- Speed rule thresholds are my physical estimates, NOT calibrated: walker < 1.0 body heights/s, rider > 2.0 (a synthetic check gave a 1.4 m/s walker 0.8 and a 5 m/s rider 2.9). The rule only relabels when the DETECTOR also disagrees with X-CLIP, and only for tracks visible >= 1.5 s. `*_rules_audit.csv` prints every track's real speed so the thresholds can be corrected from data.
- Short rule (NOTE 2026-10-08: at 14:00 the 14:03 short tracks are a PEDESTRIAN labelled cyclist, so `exp3b_short` is expected to ADD a false bicyclist there; that is now a test of whether the rule is safe, not an expected gain): a track under the minimum duration is counted as BICYCLIST if it lasted >= 0.3 s, the detector calls it cyclist in >= 90% of its frames and the weighted X-CLIP bicyclist probability is >= 0.9. (From the 14:03 and night tracks in section 15; applies day and night.)
- Motion diagnostic (MOG2 background subtraction at half resolution): blobs of person/vehicle size that NO detection box explains, grouped over time (>= 0.7 s). Diagnostic only; it never changes a count. Headlight beams and shadows will show up too: look at the contact sheet.

**23b. NOT in this batch.** E4 fine-tuning (needs the hard-case annotations; fallback she named), E5 temporal detector, E6 BNE-DETR, E7 SAMURAI, E8 combination. These need labelled data, training or other repositories. Next step for E4: label hard-case frames from OTHER hours/days (never from the two test clips), then the training script is written.

**23c. What to run (single command, then look back).** Files: `colonial_v19_bundle.tar.gz` (contains code/ and truth/).
```bash
# on your own computer (replace YOURUSER):
scp colonial_v19_bundle.tar.gz YOURUSER@hpg.rc.ufl.edu:/orange/xiangyan/rithika/vision/vision3/best/test_colonial/
# on HiPerGator:
ssh YOURUSER@hpg.rc.ufl.edu
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
tar xzf colonial_v19_bundle.tar.gz            # puts files in code/ , code/zerodce/ , truth/  (truth files are overwritten only if you re-extract!)
bash code/run_all_experiments.sh              # submits 11 jobs + 1 evaluation job, writes exp_results/MANIFEST_<time>.md
squeue -u $USER -o "%i %j %T %M"              # watch them
nano truth/night_2115_truth.csv ; nano truth/day_1400_truth.csv      # fill in while the jobs run
# when everything has finished (the evaluation job also does this by itself, but the truth files must be filled in first):
python code/eval_truth.py --root . --prefix exp
```
Re-run later without overwriting: `bash code/run_all_experiments.sh v2` (run names get `_v2`). Optional self-test of the helper functions (no GPU): `python code/test_v19.py`.

**23d. The jobs (11, each one change on the same clips).** exp0_base (night+day, + motion diagnostic) - exp1_sahi (night+day, 4 h limit) - exp2_gamma, exp2_clahe, exp2_zerodce (night only) - exp3a_speed, exp3b_short (night+day). Expected runtime: about 30 min each, SAHI longer; about 8-10 GPU-hours in total. Controls that already exist: `sw_day` (v17 settings) and `sw_switch` (v18 night rule) on the same clips. REGRESSION CHECK: `exp0_base` must reproduce `sw_day`: night 0 / 0 / 285 (bic / ped / veh), day 1 / 2 / 612. If not, v19 has a bug: stop and report.

**23e. Where to look.**
- Clips: `annotated/<run>/Standard_SCU8OG_2019-07-10_0000.022/` (night) and `.015/` (day), one mp4 per run.
- Per run, in `counts/<run>/`: `*_tracks.csv`, `*_rules_audit.csv` (per track: X-CLIP label, detector %, speed in body heights/s, what each rule would do), `*_track_motion.csv`; exp0 also `*_motion_candidates.csv` and `.png`; exp2 also `*_enhance_preview.png` (original | enhanced).
- `exp_results/EVAL_<time>.md`: per run and clip, per truth person FOUND / WRONG CLASS / DETECTED BUT NOT COUNTED / MISSED, plus EXTRA counted tracks, plus which motion candidates overlap the people nobody found.
- `exp_results/MANIFEST_<time>.md`: job ids, flags, paths (for looking back).

**23f. What was and was not checked.** Checked off-cluster: Python syntax and undefined names; slice coverage; duplicate merge (cut-off copies dropped, a person straddling a slice edge kept whole); gamma/CLAHE brighten a dark frame; speed in body heights/s for a walker and a rider; the motion diagnostic on a synthetic video; the evaluator on synthetic tracks; the submit script with a fake `sbatch`; the Zero-DCE checkpoint's layer names and shapes. NOT checked (no GPU/torch/ultralytics here): a real run of the detector with slicing, the Zero-DCE forward pass on real frames, real MOG2 behaviour on this camera, and every number above. If a job crashes, send the last 20 lines of its slurm log.

**23g. Honest caveats.** (2026-10-08: with the final 14:00 truth the expected baseline score is cyclist 1/1, pedestrians 2/4, 0 extra; the two missed late pedestrians are DETECTED BUT NOT COUNTED because of the 3 s minimum, and none of the E1-E3 runs targets pedestrians' minimum duration.) Two clips studied by eye are a development set; any win is 'promising' until the 22:00 hold-out and another day window agree. Evaluation matches by TIME only; two people on screen at once can be confused. The truth files must list EVERY person, otherwise real people show up as EXTRA. SAHI and enhancement can add false boxes at night (headlights, noise). The speed thresholds are unverified.

**23h. Results of the v19 batch (run 2026-10-08, evaluator output `exp_results/EVAL_20261008_0830.md`).**
Regression check PASSED: `exp0_base` reproduces `sw_day` (night 0 bic / 0 ped; day 1 bic / 2 ped). Runtimes: baseline about 30 min, SAHI 42-43 min (+40%, far less than the 3x I estimated), others 28-35 min.
**Truth files at the time of the run.** DAY (final, 1 cyclist + 4 pedestrians): complete. NIGHT: only 4 usable rows, all scored as cyclist (n1 = motorcycle at 4:03, n2 7:07, n3 14:21, n4 14:29); rows n5 (14:23, the missed cyclist) and n6 (14:53, the undetected last pedestrian) were SKIPPED because the end-time column was left out. Night results are therefore incomplete (no pedestrian row at all). Also unresolved: the 4 scored rows + n5 would be 5 cyclist/motorcycle, but her earlier note says 3 cyclists + 1 motorcycle (= 4) + 1 pedestrian. Fix the two rows, then re-run only `python code/eval_truth.py --root . --prefix exp` (no GPU).
| run | night: cyclists found (of 4) / wrong class / not counted / extra | day: cyclist found (of 1), pedestrians found (of 4) / wrong class / not counted / extra | counted bic/ped night, day |
|---|---|---|---|
| exp0_base | 0 / 0 / 4 / 0 | 1, 2 / 0 / 2 / 0 | 0/0, 1/2 |
| exp1_sahi | **2** / 1 / 1 / **1** | 1, 2 (the two LATE pedestrians d4 and d5) / **2** / 0 / 0 | 3/1, 3/2 |
| exp2_gamma | 0 / 0 / 3 / 0 (+1 missed) | not run | 0/0 |
| exp2_clahe | 0 / 0 / 4 / 0 | not run | 0/0 |
| exp2_zerodce | 0 / 0 / 4 / 0 | not run | 0/0 |
| exp3a_speed | 0 / 0 / 4 / 0 | **0** (the real cyclist relabelled PEDESTRIAN), 2 / **1** / 2 / 0 | 0/0, 0/3 |
| exp3b_short | **2** / 0 / 2 / 0 | 1, 2 / 0 / 2 / **1** | 2/0, 2/2 |
What each run showed (all on 2 clips; 'promising', not proven):
- **E1 SAHI:** makes tracks much longer. Night: the riders' tracks went from 0.43-0.9 s to 5.24 s and 3.47 s, so two now pass the 3 s minimum with no rule. Day: the two late pedestrians (2.1 s and 1.2 s before) become 22 s and 3.5 s tracks and are counted. BUT the labels get worse: on the day clip two pedestrians (3:00-3:25 and 11:45-12:14, detector says person in 94-98% of frames) are now counted as BICYCLIST (X-CLIP), so day counts go 1/2 -> 3/2 against a truth of 1/4. Night: one rider labelled pedestrian, and one EXTRA counted cyclist at 14:44-14:59 (10.6 s; may be the undetected pedestrian of row n6 at 14:53, to be checked once n6 is fixed). So SAHI moves the bottleneck from detection and duration to the X-CLIP label.
- **E2 enhancement (gamma, CLAHE, Zero-DCE):** no gain. Night tracks stayed under a second, CLAHE and Zero-DCE made them shorter (0.07-0.67 s) and gamma lost one rider entirely. Not adopted. (Single clip, single threshold.)
- **E3a speed rule (defaults 1.0 / 2.0 body heights/s, UNcalibrated): harmful.** It turned the real 9:10 cyclist (detector: cyclist in 34.7% of frames) into a pedestrian; it fixed nothing. Needs calibration from `counts/exp3a_speed/*_rules_audit.csv` (speed per track) before any further use.
- **E3b short-track rule:** night: found the motorcycle (0.6 s) and one rider (0.43 s) with no false person, 2/4. Day: counted the 0.4 s track at 3:03-3:05 as a cyclist, a FALSE cyclist (it is the far pedestrian). As predicted: helps at night, hurts by day, so it should be night-only.
- **Motion diagnostic:** 447 unexplained moving blobs in the night clip and 185 in the day clip: far too many to be informative (almost every truth row overlaps dozens). Useless without filtering (minimum net movement, size, zone, brightness): no evidence it helps yet.
- **Detector vs X-CLIP, again:** at day, wherever X-CLIP said BICYCLIST for a pedestrian, the detector said person in 94-98% of frames (SAHI run), while the real cyclist had 34.7% (baseline) and 54% (SAHI). A detector veto (X-CLIP says bicyclist but detector says cyclist in < about 10-15% of frames -> pedestrian) would fix both wrong-class pedestrians and keep the real cyclist, but it is derived from these two clips and is untested elsewhere (earlier 12:45 pedestrians had 45% detector-cyclist, which it would NOT fix).
**Suggested next batch (NOT coded yet, awaiting go-ahead):** (1) fix the night truth rows and re-score; (2) `--short-rule` restricted to night frames; (3) `--det-veto-pct`; (4) combination SAHI + night-only short rule + detector veto, run on the SAME two clips AND on the untouched windows (22:00-22:15 night and 12:45-13:00 day) to see whether it generalises; (5) calibrate or drop the speed rule from `rules_audit.csv`.

## 24. Batch 2 and clip naming (written 2026-10-08; code NOT yet run on the cluster)
**24a. Which clip gave 'bicyclists 3, pedestrians 2'?** `exp1_sahi` on the DAY clip 14:00-14:15 (annotated/exp1_sahi/.../*1400-1415.mp4). It is NOT a good result against the truth (1 cyclist + 4 pedestrians): 3 bicyclists = the real cyclist + two pedestrians (3:00-3:25 and 11:45-12:14) that X-CLIP called bicyclist; the 2 counted pedestrians are the two LATE pedestrians that SAHI recovered (the real gain). The closest thing to a good night result is `exp1_sahi` night (counted 3/1: 2 of 4 riders found, 1 wrong class, 1 extra).
**24b. Clip names (from now on).** New runs write `<run>__<day|night>_<HHMM>-<HHMM>__<test>__<date>.mp4`, e.g. `b2_3_sahi_fuse__night_2115-2130__sahi640+detfuse__20190710.mp4`. `<test>` = `control`, `sahi640`, `enh-<mode>`, `speedrule`, `shortrule` / `shortrule-night`, `detfuse`, `nightswitch`, `motiondiag` joined by `+`. Old clips (sw_*, exp*) can be given the same kind of name with `python code/collect_clips.py --root .` (hard links in `exp_results/clips/`, plus `INDEX.md`).
**24c. New options in `xclip_overlay_v19_colonial.py` (all off by default).** `--short-rule-night-only` (short-track rule only for tracks whose middle frame is in the night period; needs `--night-start/--night-end`); `--det-veto-pct P` (X-CLIP says BICYCLIST but the detector calls the track cyclist in < P% of its frames -> PEDESTRIAN); `--det-promote-pct P` (X-CLIP says PEDESTRIAN but detector cyclist in >= P% -> BICYCLIST); `--det-fuse-min-frames N` (default 20 detector frames needed). Slurm env: `SHORT_RULE_NIGHT_ONLY=1 DET_VETO_PCT DET_PROMOTE_PCT DET_FUSE_MIN_FRAMES`. The label code was tested in isolation (real code text, stub data): veto flips a 6%-cyclist track and keeps a 54% one; promote flips a night 100%-cyclist pedestrian label; too few detector frames = no change; night-only short rule blocked by day and allowed at night.
**24d. Settings chosen (from batch-1 results, i.e. fitted on the two dev clips, so they MUST be checked on the hold-outs):** veto 15%, promote 90%, SAHI 640 px / 20% overlap, short rule 0.3 s / detector >= 90% / weighted BIC >= 0.9, night 21:00-06:00. Known weak spot: earlier 12:45 pedestrians called cyclist had detector 45% cyclist, which the veto at 15% would NOT fix.
**24e. The run: `bash code/run_batch2.sh` (16 jobs + 1 evaluation job).** Clips: dev night 21:15-21:30, dev day 14:00-14:15, HOLD-OUT night 22:00-22:15 (chunk 23, frames 1-26973), HOLD-OUT day 12:45-13:00 (chunk 13, frames 80924-end). Runs: `b2_0_base` and `b2_2_sahi` (hold-outs only; the dev clips already have `exp0_base`, `exp1_sahi`), `b2_1_fuse` (veto+promote), `b2_3_sahi_fuse`, `b2_4_sahi_fuse_nightshort` (all four clips). Evaluation: `exp_results/EVAL_batch2_<time>.md` compares them with `exp0_base` and `exp1_sahi`, and copies the clips with explicit names into `exp_results/clips/`.
**24f. Truth files needed BEFORE judging batch 2:** `truth/night_2115_truth.csv` (fix rows n5, n6: they lack the END column; see `night_rows_fix.txt`; confirm the total: her older note said 3 cyclists + 1 motorcycle + 1 pedestrian), `truth/night_2200_truth.csv` and `truth/day_1245_truth.csv` (new templates; the hold-out files list the model's tracks with approximate times, she must fill in the classes and add every person not listed), `truth/day_1400_truth.csv` (final). Templates: `colonial_v19_1_truth_templates.tar.gz`; do NOT re-extract the older bundle over filled-in files.
**24g. How to judge it.** A combination is 'promising' only if on BOTH the dev clips and the hold-outs it finds more true people than `exp0_base` without more wrong-class or extra tracks. If it only wins on the dev clips, the settings were over-fitted to them. Honest limits: 4 clips, one camera, one day; the thresholds come from 2 clips.
**24h. Results of batch 2.** (empty: fill in after the jobs finish.)

## 25. Night truth, how a track gets its label, speed rule (2026-10-08)
**25a. FINAL night 21:15-21:30 truth (her words, `truth/night_2115_truth.csv`):** motorcycle 4:02-4:04; bicyclist 7:02-7:09; THREE bicyclists together 14:21-14:26; pedestrian 14:47-14:58. Total = 1 motorcycle + 4 cyclists + 1 pedestrian (an older note said 3 cyclists). Motorcycle is scored as cyclist. Consequences: (1) the model's 14:29 track (labelled pedestrian by X-CLIP, detector 100% cyclist, 1.0 s) lies OUTSIDE her 14:21-14:26 range; if she meant it to be one of the three, widen the rows to 14:30. (2) Three rows share one time, so a time-only match can find at most the tracks that exist; the rest show as MISSED, which is correct. (3) SAHI's night EXTRA track at 14:44-14:59 (10.6 s, labelled cyclist) overlaps the pedestrian at 14:47-14:58: probably that pedestrian with the wrong label.
**25b. How a person track gets counted and labelled (the pipeline as it is, defaults).** (1) RT-DETR box per frame, conf >= 0.25. (2) Tracker + id stitching make a track. (3) Every `--stride` (3) frames the track's crop goes into a window of frames to X-CLIP, which outputs P(bicyclist) vs P(pedestrian); a track needs at least one X-CLIP score. (4) The track's label = whichever class has the higher box-height-weighted mean of those probabilities. THE DETECTOR'S OWN LABEL (person vs cyclist) IS NOT USED for the label unless the v19 fuse flags are on. (5) The track must stay on screen >= 3.0 s (`--person-min-sec`, also `--bic-min-sec` / `--ped-min-sec`) to be counted; zones decide road / bike lane / sidewalk. So SAHI makes tracks longer (they pass the 3 s rule) but then X-CLIP, which was never trained on this camera, makes the label.
**25c. Is the speed number right?** What is computed: path length of the smoothed ground point (bottom centre of the box) in IMAGE pixels per second, divided by the track's mean box height = 'body heights per second'. Checked only on synthetic left/right motion (walker 0.8, rider 2.9). Not verified on real tracks. Known weak points: (a) a rider moving TOWARD or AWAY from the camera moves little in the image whatever the real speed (perspective), so it looks slow: a likely reason the speed rule turned the real 9:10 cyclist into a pedestrian in `exp3a_speed`; (b) path length adds up jitter for small far boxes; (c) thresholds 1.0 / 2.0 were guesses. Remedy built: `--speed-lateral-only` (rule only for tracks moving left/right). Proper fix would be ground-plane (metric) speed from a camera calibration, not available. Data check: `python code/fusion_probe.py --root . --runs exp0_base,exp1_sahi,exp3a_speed` prints, for every truth person, X-CLIP label, detector %cyclist, speed, direction, and replays veto / promote / speed rules on them.
**25d. Run `b2_5_sahi_speed`** added to `code/run_batch2.sh` (SAHI + lateral-only speed rule, thresholds in the `SPEEDENV` line at the top of the script); batch 2 is now 20 jobs + evaluation. Update bundle: `colonial_v19_2_code.tar.gz` (code only); truth files are separate and must not be overwritten once filled in.
**25e. Annotated folders.** Each run has one sub-folder per clip (`annotated/<run>/Standard_SCU8OG_2019-07-10_0000.015` = day 14:00, `.022` = night 21:15, `.013` = day 12:45, `.023` = night 22:00). Runs `exp2_gamma / exp2_clahe / exp2_zerodce` were NIGHT-only by design (no day clip). If a night clip is missing elsewhere, list what exists: `find annotated -name "*.mp4" -printf "%p %s\n" | sort` (a file ending `.tmp_mp4v.mp4` means the final conversion did not finish).
**25f. Night minimum: what was and was not tested (2026-10-08).** `sw_switch` (v18) = flat night minimums 0.4 s bicyclist / 1.0 s pedestrian (+ detector conf 0.15, which did little). `exp3b_short` = a conditional short rule (>= 0.3 s, detector cyclist >= 90% of frames, weighted BIC >= 0.9): stricter, it missed the 0.9 s rider whose detector share was 59%. Batch 2 as first written only had the conditional rule at night (`b2_4`). Added: `b2_6_night04` (flat minimums, no SAHI) and `b2_7_sahi_fuse_night04` (SAHI + veto/promote + flat minimums), on the two NIGHT clips only (day clips would equal existing runs). Batch 2 = 24 jobs + evaluation. With SAHI the night tracks are already 3.4-5.2 s long, so a night minimum matters much less there.
**25g. What to run after the jobs finish (from the project folder `test_colonial`, NOT from `code/`).**
```bash
squeue -u $USER -o "%i %j %T %M"                    # nothing left = finished
grep -L "Final counts" logs/slurm_b2_*.log          # logs WITHOUT 'Final counts' = a job that failed; send me tail -20 of those
ls exp_results/                                     # the evaluation job writes EVAL_batch2_*.md and exp_results/clips/
less exp_results/EVAL_batch2_*.md                   # q to quit
python code/fusion_probe.py --root . --runs exp0_base,exp1_sahi,b2_3_sahi_fuse,b2_5_sahi_speed
```
If the evaluation job ran before the hold-out truth files were filled in, re-score (no GPU): `python code/eval_truth.py --root . --runs exp0_base,exp1_sahi,b2_0_base,b2_2_sahi,b2_1_fuse,b2_3_sahi_fuse,b2_4_sahi_fuse_nightshort,b2_5_sahi_speed,b2_6_night04,b2_7_sahi_fuse_night04 --baseline exp0_base`. Clips with explicit names: `python code/collect_clips.py --root .` then `ls exp_results/clips`. If only the first 20-job version of batch 2 was submitted, add the missing night runs with `bash code/run_night04_only.sh` (4 jobs, works with the code already on the cluster).
**25h. Results of batch 2 (20-job version; evaluator output `exp_results/EVAL_batch2_20261008_1612.md`; all jobs finished, 28-43 min each) and the fusion probe (2026-10-09).**
HOLD-OUT TRUTH WAS NOT FILLED IN: `truth/night_2200_truth.csv` and `truth/day_1245_truth.csv` were missing on the cluster, so the two hold-out clips only have counts (every counted track shows as EXTRA). They must be copied to `truth/` and filled in; everything below about generalisation is still open.
Dev clips (truth complete: night 6 people = 5 cyclist/motorcycle + 1 pedestrian; day 5 people = 1 cyclist + 4 pedestrians):
| run | night: cyclists found (of 5) / ped found (of 1) / wrong class / not counted | day: cyclist (of 1), pedestrians (of 4) / wrong class / not counted | counted bic/ped night, day |
|---|---|---|---|
| exp0_base | 0 / 0 / 0 / 4 (+2 missed) | 1, 2 / 0 / 2 | 0/0, 1/2 |
| exp1_sahi | 2 / 0 / 2 / 2 | 1, 2 / 2 / 0 | 3/1, 3/2 |
| b2_1_fuse (veto+promote, no SAHI) | same as exp0_base | same as exp0_base | 0/0, 1/2 |
| b2_3_sahi_fuse (SAHI + veto + promote) | 2 / 0 / 2 / 2 | **1, 4 / 0 / 0 (all 5 right)** | 3/1, 1/4 |
| b2_4_sahi_fuse_nightshort (+ short rule at night only) | **3** / 0 / 2 / 1 (the motorcycle is now found) | 1, 4 / 0 / 0 | 4/1, 1/4 |
| b2_5_sahi_speed (SAHI + lateral speed rule 1.0/2.0) | 3 / 0 / 1 / 2 | 1, 4 / 0 / 0 | 4/0, 1/4 |
Hold-out clips, COUNTS ONLY (no truth yet; earlier notes say 12:45 has 2 cyclists + 3 pedestrians): 12:45 day: base 4/1, SAHI 4/1, veto 3/2, SAHI+veto 3/2, SAHI+speed 3/2. 22:00 night: base 0/0, but every SAHI run counts 7 pedestrians (0/7): real people SAHI found, or false detections? Unknown until someone watches the clip (annotated/b2_2_sahi/*0.023/).
What the data say (dev clips = where the settings were chosen, so optimistic):
- SAHI is the one change that adds true detections (night riders, late pedestrians); it needs a label fix on top. The detector veto (15%) turned both SAHI wrong-class pedestrians on the day clip right (detector said person in 94-98% of frames) and left the real cyclist (detector 35-54%): day clip 5/5. Without SAHI the veto changes nothing on the dev clips.
- The short-track rule at night only found the motorcycle (1.2 s track, detector 94%, weighted bicyclist 0.97) with no new false person.
- Speed (fusion probe, 41 (person, run) pairs, but only about 11 different people): X-CLIP alone right in 26; veto 10-30% right in 32; lateral speed rule walk < 0.8 / ride > 2.0 right in 35 and flips only wrong labels (night n4 rider X-CLIP called pedestrian: speed 2.23 h/s; day d2 and d3: speed 0.56 and 0.39). At walk < 1.0 it flips the real day cyclist (0.97 h/s, moving left, detector 35%): wrong. So the usable window is thin: slowest real cyclists 0.79-0.97 h/s vs fastest walker 0.78 h/s. Speed in the image is NOT a clean separator; the det %cyclist condition protects the night rider (0.87 h/s, detector 88%).
- Still wrong at night: n6, the 14:47-14:58 pedestrian (10.6 s, moving right, speed 0.48 h/s) is called bicyclist by X-CLIP (0.67) AND the detector (69% cyclist); only a speed-alone rule would catch it. n5 (a rider called pedestrian, detector 31%, 2.37 s) stays under the 3 s minimum.
- `exp0_base` vs `b2_1_fuse` are identical on the dev clips: veto/promote do nothing without the longer SAHI tracks.
- The first batch had no failed jobs (the only log without 'Final counts' is the evaluation job's own).
**25i. Next (batch 3).** `bash code/run_batch3.sh`: ONE combined run `b3_combo` (SAHI + veto 15/promote 90 + short rule at night only + lateral speed rule 0.8/2.0) on all four clips; its evaluation job also runs `fusion_probe.py`. Before it can be judged: (1) fill the two hold-out truth files, (2) watch the 22:00 SAHI clip (7 pedestrians), (3) re-score with the commands in 25g. If the hold-outs disagree with the dev clips, the thresholds are over-fitted.

## 26. Hold-out truth status (2026-10-09)
The hold-out files were created on the cluster on 2026-10-09 but the CLASS column was left empty, so the evaluator still skipped every row (0 usable rows for both hold-outs); counts in the batch-2 report are therefore the only hold-out evidence so far. DRAFT for `truth/day_1245_truth.csv` (inferred, to be CHECKED by Rithika): h1 0:40-0:56 pedestrian (her screenshot of id 1: a walking person called BICYCLIST), h2 8:07-8:13 cyclist, h3 8:46-8:53 cyclist, h4 9:54-10:04 pedestrian, h5 11:17-11:38 pedestrian (detector: person in 93% of frames) = 2 cyclists + 3 pedestrians, matching her earlier note; her extra 'pedestrian on the grass, not counted' may be one of these or a 4th person (unresolved). Counts-only evidence on that clip (from `EVAL_20261009_0047.md`): `b2_3_sahi_fuse` (veto) changes only #15 (11:14-11:40) to pedestrian; `b2_5_sahi_speed` changes only #1 (0:40-0:59) to pedestrian; both give 3 cyclists / 2 pedestrians; the two fixes are on DIFFERENT tracks, so the combined `b3_combo` should give 2 / 3, IF the draft is right. 22:00 night: SAHI runs count 7 pedestrians that the baseline missed (windows 6:00-6:13, 7:50-8:27, 8:32-9:00, 9:05-10:15, 10:42-11:18, 11:05-11:16, 11:12-11:18); nobody has checked whether they are real people.

## 27. First hold-out scoring: day 12:45-13:00 (2026-10-09), against the DRAFT truth in section 26
IMPORTANT: Rithika pasted the draft classes as given, so they are NOT yet verified by her eyes (the notes still say CHECK). h1 = pedestrian is independent (her own screenshot of id 1: a walking person called BICYCLIST; detector 45% cyclist in the base run). h5 = pedestrian was inferred from the DETECTOR (7-8% cyclist), so any rule that uses the detector looks right on it by construction (circular). h2 and h3 = cyclist are by elimination. The base-run detector shares were 45 / 46 / 45 / 7 % cyclist for h1 / h2 / h3 / h5, so the second 'pedestrian called cyclist' could be h2 or h3 instead of h5; if so the veto would be WRONG on h5.
Scores against the draft (2 cyclists + 3 pedestrians): base 4/1 counted (cyclists 2/2 found, pedestrians 1/3, 2 wrong class); SAHI alone same; SAHI + veto 15% (`b2_3_sahi_fuse`) 3/2: fixes h5 only; SAHI + lateral speed 0.8-ish rule (`b2_5_sahi_speed`, run with 1.0/2.0) 3/2: fixes h1 only (h1: speed 0.74 h/s, moving left, detector 26%); h5 is moving AWAY from the camera so the lateral-only speed rule does not touch it. The two fixes are complementary, so the combination (`b3_combo`, not yet run) should reach 2/3.
Fusion probe on 50 (person, run) pairs (about 16 different people, dev + the 12:45 hold-out): X-CLIP alone right in 32; veto 10-20% right in 40; veto 30% right in 43 (flips h1 too; its margin is thin: h1 26% vs the real day cyclist 34.7%); veto 40% already flips the real day cyclist (wrong); veto 50% flips real cyclists h2, h3, n3 (wrong); promote never fires; lateral speed walk < 0.8 / ride > 2.0 right in 42 with NO wrong flips; walk < 1.0 flips the real day cyclist and h2 (wrong). Conclusion so far: veto about 15% and speed 0.8 / 2.0 (lateral only) are the settings with no wrong flips on any people seen; both windows are narrow and rest on very few people.
Still open: (1) which of h2, h3, h5 is the second pedestrian called cyclist (watch 8:07, 8:46, 11:17); (2) the 22:00 night hold-out has no truth yet (SAHI counts 7 pedestrians); (3) night remains weak: the 14:47-14:58 pedestrian is called cyclist by both X-CLIP and the detector (69%) and a 2.4 s rider stays under the 3 s minimum.

## 28. VERIFIED hold-out truth (her answers, 2026-10-09) and what it shows
**12:45-13:00 (day) = 2 cyclists + 3 pedestrians, confirmed:** 8:07 bicyclist (h2), 8:46 bicyclist (h3), 11:17 walking (h5), 0:40 pedestrian (h1, her screenshot); 9:54 (h4, counted pedestrian) not re-checked. So the draft of section 26/27 was right, including h5 = pedestrian; the veto decision on h5 is no longer circular, and the second 'pedestrian called cyclist' is h5, not h2/h3.
**22:00-22:15 (night) = 5 pedestrians, 0 cyclists:** pedestrian 6:00-6:13; pedestrian 10:00-10:14; THREE pedestrians walking together 10:59-11:18. NOT people: a BARRICADE tracked as a pedestrian at 7:50-8:27, 8:32-9:00 and 9:05-10:15. Against the SAHI runs' 7 counted pedestrians (tracks #18, #24, #26, #27, #33, #36, #40): 4 are real (#18 at 6:00, #33 / #36 / #40 at about 10:42-11:18) and 3 are FALSE (#24, #26, #27 = the barricade), i.e. SAHI found 4 of the 5 real pedestrians that the baseline missed completely (0 counted) but added 3 static false people. Caveat: the 10:00-10:14 pedestrian overlaps in time with the barricade track #27 (9:05-10:15); the time-only evaluator will score it FOUND by that track although the track is the barricade: whether the real pedestrian was boxed at all is unknown. Expected evaluator output for SAHI at 22:00 with the new truth: 5/5 found, 2 EXTRA (#24, #26).
**What it means.** SAHI also creates false people on STATIC objects at night (3 tracks of 3.8-18.7 s on a barricade). The veto/promote/speed rules do not touch this (the tracks are labelled pedestrian already). Candidate fix, NOT coded: a static-object filter (tiny net movement AND tiny speed AND long duration, perhaps night only or on a persistent location); it must not remove real standing pedestrians (day clip d4, d5 were static real pedestrians), so first look at the features of the false tracks: `python code/fusion_probe.py ...` now prints a second table of counted tracks that match no truth person (secs, X-CLIP, detector %cyclist, speed, net px, direction).
**Next.** (1) Put the two new truth files in `truth/` (below), (2) re-run `eval_truth.py` and the updated `fusion_probe.py` on exp0_base, b2_0_base, b2_2_sahi, b2_3_sahi_fuse, b2_5_sahi_speed (and `b3_combo` once it has run), (3) send the two outputs; the features of tracks #24/#26/#27 decide the static filter.

## 29. Batch 3 results: `b3_combo` (2026-10-10; evaluator output `EVAL_batch3_*.md`, 4 jobs of about 42 min)
Setting: SAHI 640/20% + detector veto 15% + promote 90% + short rule at NIGHT only (0.3 s / detector >= 90% / weighted bicyclist >= 0.9) + lateral speed rule walk < 0.8 / ride > 2.0 body heights/s. The speed and veto thresholds were chosen from the two dev clips BEFORE the 12:45 and 22:00 truth existed, so those two clips are a genuine (if small) hold-out. Truth is verified by her eyes for all four clips (section 28). 21 people in total.
| clip (people) | exp0_base (control) | SAHI alone | **b3_combo** |
|---|---|---|---|
| night 21:15 dev (6) | 0 found | 2 found | **4 found** (n1 motorcycle, n2, n3, n4); not counted: n5 (2.4 s, labelled pedestrian); wrong class: n6 (pedestrian called cyclist) |
| day 14:00 dev (5) | 3 found, 2 not counted | 3 found, 2 wrong class | **5 / 5** |
| night 22:00 HOLD-OUT (5 pedestrians) | 0 found (3 missed, 2 detected but not counted) | 5 found | 5 found, **but 2 EXTRA + the barricade track #27 = 3 false people** |
| day 12:45 HOLD-OUT (2 cyclists + 3 pedestrians) | 3 found, 2 wrong class | 3 found, 2 wrong class | **5 / 5** (counts 2 cyclists / 3 pedestrians = truth) |
| TOTAL found | **6 / 21** | 13 / 21 | **19 / 21** |
Honest reading: (1) the 12:45 hold-out is passed: the veto fixed h5 and the speed rule fixed h1, as predicted before it ran. (2) At 22:00 no label rule was involved: the gain there is SAHI's detection alone (0 -> 5 pedestrians), paid for with 3 false static people. (3) Only about 4 hours' worth of 15-minute windows, one camera, one day, 21 people: a strong hint, not a measured accuracy. (4) The p2 person at 22:00 (10:00-10:14) overlaps in time with the barricade track #27; the time-only matcher scores it FOUND, so true recall there may be 4/5.
Remaining errors: (a) barricade tracks (#24 4.97 s, #26 3.8 s, #27 18.7 s): static, speed 0.01 body heights/s, net movement 0-2 px, detector 0% cyclist: they cannot be fixed by the label rules (already labelled pedestrian). The existing `--person-min-disp` (v13: rejects static look-alikes by net movement, env `PERSON_MIN_DISP`) is the candidate fix; BEFORE using it check that real standing pedestrians (day clip static tracks, speeds 0.15-0.18) have a larger net movement: the updated `fusion_probe.py` now prints a `net px` column for every truth person and for every false track. (b) night n6, the 14:47-14:58 pedestrian, called bicyclist by X-CLIP (0.67) and by the detector (69% cyclist); its speed is 0.48 h/s, slower than every real cyclist seen (>= 0.87), but fixing it means a speed-only rule fitted on ONE example: do not do it without more data. (c) night n5, a rider labelled pedestrian by X-CLIP, 2.4 s, below the 3 s minimum.
Promote (90%): never right, one wrong flip on the baseline (`b2_0_base` 22:00 p2, an uncounted 0.43 s track): it adds nothing, leave it off in future runs. Detector veto: right on every flip it made (d2, d3, h5). Speed lateral 0.8 / 2.0: right on every flip (n4, d2, d3, h1); 1.0 flips real cyclists (d1, h2): keep 0.8.
Not worth pursuing from these data: enhancement (no gain), motion diagnostic (447 / 185 blobs, no discrimination).
Next: (1) run `python code/fusion_probe.py --root . --runs b3_combo,b2_2_sahi` and send the table (net px of real people vs the barricade), (2) choose PERSON_MIN_DISP from it and run ONE confirmation job set (`b3_combo` + static filter), (3) before any claim, label 2-3 NEW windows (one more night, two day, different hours) as a fresh hold-out; the current four clips have now been looked at.

## 30. Net-movement check of the 22:00 barricade tracks (2026-10-10) and a CORRECTION
Fusion probe on `b3_combo` and `b2_2_sahi`, new `net px` column (motion_summary net movement of the smoothed ground point):
- Counted tracks matching no truth person (the false people): #24 (7:50-8:27, 4.97 s) net 0 px, speed 0.01 h/s, static, detector 0% cyclist; #26 (8:32-9:00, 3.8 s) net 2 px, speed 0.01, static, detector 0%. Only these TWO.
- #27 (9:05-10:15, 18.72 s), which sections 28 and 29 counted as a third barricade track, is NOT static: net 516 px, speed 0.15 h/s, moving right, matched to the real pedestrian p2 (10:00-10:14). So it is probably one track that started on the barricade and ended up following the real pedestrian (or the barricade box merged with the person): a real person with a contaminated track, not a third false person. CORRECTION: false people at 22:00 = 2, not 3; real recall there 5/5 is plausible, but the track's early part (9:05-10:00) sits on the barricade.
- Real static pedestrians for comparison: day 12:45 h4 (7.2 s) speed 0.18, net 30 px (static); all other real people: net 344-733 px.
So a net-movement filter below about 10 px would remove #24 and #26 and keep every real person seen so far; the closest real person is h4 at 30 px, a margin of 3x on a very small sample. `PERSON_MIN_DISP` (v13) filters by `disp_px` (first-to-last ground point, written to tracks.csv), which can differ slightly from the net px above: check it with `python code/disp_check.py --root . --runs b3_combo --below 60`, which lists every counted track under 60 px with clip, time, length and label (only #24 and #26 should be under about 10). Then `bash code/run_batch4.sh` runs b3_combo + `PERSON_MIN_DISP=10` (promote off) on all four clips (`DISP=15 bash code/run_batch4.sh` to change). Open: how the filter treats a standing pedestrian who really stands still for several seconds (none among the 21 people so far has less than 30 px).

## 31. `disp_check.py` on b3_combo (2026-10-10): counted tracks under 60 px of net movement (`disp_px`, the number `PERSON_MIN_DISP` uses)
| disp px | clip | track | from | secs | label |
|---|---|---|---|---|---|
| 1 | night 22:00 (hold-out) | #24 | 22:07:50 | 4.97 | PEDESTRIAN (barricade, false) |
| 1 | night 22:00 (hold-out) | #26 | 22:08:32 | 3.8 | PEDESTRIAN (barricade, false) |
| 19 | day 14:00 | #23 | 14:12:30 | 3.47 | PEDESTRIAN (real: d5, standing) |
| 30 | day 12:45 (hold-out) | #14 | 12:54:53 | 7.21 | PEDESTRIAN (real: h4, standing) |
Nothing else is below 60 px. CORRECTION of section 30: the closest real person is 19 px (d5), not 30; the 30 px figure was the other standing pedestrian (h4). The two false tracks are at 1 px. Cutoff choice: 10 px would remove both barricade tracks but sits only 1.9x below the real 19 px standing pedestrian; **5 px** is the better balance on a log scale (5x above the barricade, 3.8x below the real person). Use `DISP=5 bash code/run_batch4.sh` (run name `b4_combo_disp5`). Caveat: 4 tracks under 60 px in total, 2 real standing pedestrians; a pedestrian standing still for several seconds could go below 5 px, and a barricade that jitters more could exceed it: the choice is a guess supported by very few numbers.

## 32. Static-object filter v2, and what 'fusion' means here (2026-10-10)
**32a. A person waiting to cross, then crossing.** `PERSON_MIN_DISP` (v13) judges a track only by net movement first -> last frame of its WHOLE life. A person who waits and then crosses has a large net movement, so that track is kept. Where it can go wrong: a person who only stands still for the whole track, and a tracker that splits waiting and crossing into two tracks (the waiting piece could be dropped, the crossing piece still counts the person once). A net-only filter would also drop a person who sways in place with a net movement under the cutoff. New, safer rule `--static-filter` (env `STATIC_FILTER=1`, `STATIC_MAX_NET_PX=5`, `STATIC_MAX_SPEED=0.05`, `STATIC_MIN_SEC=3`): a track of at least 3 s is dropped as a STATIC OBJECT only if BOTH its net movement is under 5 px AND its ground-point PATH speed is under 0.05 body heights/s. The path speed counts box jitter and body sway: the barricade tracks have 0.01 h/s, the real standing pedestrians 0.15-0.18 h/s. It is never more aggressive than the net-only filter. Tested on the real code text with the known tracks (barricade #24, #26 dropped; standing pedestrians d5 and h4 kept; a track with 516 px net kept; a 2 s track not judged; a person moving in place at 0.5 h/s kept). Not yet run on the cluster. A person standing PERFECTLY still for >= 3 s (both numbers tiny) would still be dropped: no such person among the 21 labelled. Possible later refinements (not coded): a persistent-location map of objects that stay in the same place for minutes or hours (a barricade does, a waiting person does not); a lower box-jitter bound.
**32b. Best configuration so far = `b3_combo` (19/21 people found on 4 labelled clips, baseline 6/21, SAHI alone 13/21).** Pieces: (1) detector `rtdetr_v3` (fine-tuned RT-DETR) run with SAHI-style sliced inference (640 px slices, 20% overlap, plus the full-frame pass, duplicates merged; people only); (2) tracker + id stitching; (3) X-CLIP video classifier on each person track (P(bicyclist) vs P(pedestrian), weighted by box height); (4) minimum 3 s on screen to count; (5) FUSION RULES, i.e. the final label no longer comes from X-CLIP alone but from three opinions about the same track: X-CLIP (how it looks over time), the detector (its per-frame person/cyclist call, summarised as the % of frames called cyclist) and the motion (speed in body heights per second and direction). Rules: veto (X-CLIP says bicyclist but the detector calls it cyclist in < 15% of frames -> pedestrian); speed rule for left/right-moving tracks seen >= 1.5 s (slower than 0.8 h/s and detector < 50% cyclist -> pedestrian; faster than 2.0 h/s and detector >= 50% -> bicyclist); promote 90% (never fired usefully, to be dropped); night-only short-track rule (21:00-06:00: a track of 0.3-3 s counts as bicyclist if the detector says cyclist in >= 90% of frames and the weighted bicyclist probability is >= 0.9). Next candidate: b3_combo + static-object filter = `bash code/run_batch4.sh` (run name `b4_combo_static5`). Tried and dropped: image enhancement (gamma, CLAHE, Zero-DCE), motion-blob diagnostic, flat 0.4 s night minimum (not yet evaluated if run), the first speed rule thresholds (1.0). Not done: fine-tuning on her own frames, temporal detector, BNE-DETR, SAMURAI.

## 33. Zones re-annotation, a new higher-resolution video, batch-4 housekeeping (2026-10-11)
**33a. Batch 4.** Two versions exist: the first `run_batch4.sh` (net-only filter, `PERSON_MIN_DISP`, run name `b4_combo_disp5`) is superseded by the second (`--static-filter`: net movement < 5 px AND path speed < 0.05 body heights/s, run name `b4_combo_static5`). If the first is still queued or running, cancel it and its evaluation job (`squeue -u $USER -o "%i %j %T %M %E"`, `scancel <ids>`); keep the second. Both would give the same result on the known tracks, so nothing is lost.
**33b. What the zones do (read from the code).** `road` polygon: vehicles whose ground point is outside it are dropped. `sidewalk` polygon: vehicles inside it are dropped. `bike` polygon: drawn for reference and used for the bike-lane vs sidewalk split of PEOPLE (the facility column); it does not filter anything. PEOPLE are never removed by the zones (zones_test, 2026-10-05: same person counts as without zones). So a wrong bike-lane polygon affects only the facility column and the drawn overlay, NOT the person counts and none of the batch 1-4 scores. A wrong road polygon would affect vehicle counts (not evaluated). The pipeline reads ONE polygon per zone, in the file `{"ref_size":[W,H],"road":[[x,y],..],"bike":[..],"sidewalk":[..]}`; coordinates are scaled by (video size / ref_size), so a file drawn on a frame of the same shape works at another resolution only if the camera view and aspect ratio are the same.
**33c. Re-annotating.** `python code/extract_ref_frames.py --colonial-chunk 13 --times 5:00,25:00,45:00` writes CLEAN full-size PNGs to `zones/ref/`; the current polygons can be seen in `counts/<run>/*_zones_preview.png`. `zone_annotator.html` (open locally in a browser, works offline): load the frame, optionally load the current zones JSON (scaled to the frame), draw/move points, click 'Download zones JSON' (file `colonial_north_v2.json`, `ref_size` = the frame's size), copy it to `zones/` on the cluster. Test status: the scaling/export logic was tested in node; the page was NOT tested in a real browser. The old zones file says ref_size 720x480: check the real video size (`probe_video.py` or the 'zone coords scaled' log line).
**33d. New video (2025 or later, higher resolution).** `python code/probe_video.py "<video>"` prints size, fps, length and the ffmpeg command to cut a 15-minute clip; `VIDEO=<clip> START="YYYY-MM-DD HH:MM:SS" [ZONES=<new zones json>] bash code/run_new_video.sh` runs two jobs: `nv_base_<date>` (control) and `nv_combo_<date>` (SAHI + veto + night short rule + lateral speed rule + static filter). The slurm now accepts `VIDEO_OVERRIDE` (+ `SESSION_START`), switches the 2019 ground-truth file off for it and sets `--chunk-index 1`. There is NO truth file for it, so nothing is scored automatically: judge by watching the two clips and (if wanted) by writing a truth file like the others. Open questions: is it the same camera and the same view (the Colonial zones and the fine-tuned detector were made for the 2019 footage)? Pixel-based settings were chosen on the old resolution and should be scaled by the width ratio: static filter (5 px), stitch/split distances (150/120 px), the 30 px 'static direction' cutoff, SAHI slice (640 px); the body-heights speed thresholds are resolution-free. Dry-run tested with a fake `sbatch`; not run on the cluster.

## 35. Batch 4 results, and tools for the new video and the zones (2026-10-12)
**35a. Batch 4 result.** `b4_combo_static5` vs `b3_combo` (same truth, evaluator `EVAL_batch4_*.md`; all 4 jobs finished, 41-43 min; the `Final counts` check printed no failed logs): night 21:15 4/5 cyclists found, 0/1 pedestrian, 1 wrong class, 1 not counted, 0 extra (identical to b3); day 14:00 5/5 (identical); night 22:00 hold-out 5/5 pedestrians, **extra counted 2 -> 0**, counted 0/5 (was 0/7); day 12:45 hold-out 5/5 (identical). Fusion probe: no counted track without a truth person remains for `b4_combo_static5`. Caveats unchanged: 21 people, 4 clips, one camera and day, thresholds partly set on the first two clips, the static filter set from 4 tracks under 60 px (2 real standing pedestrians at 19 and 30 px). The filter's both conditions (net < 5 px AND path speed < 0.05 h/s) were not triggered by any real person.
**35b. Which tarball.** `colonial_code_latest.tar.gz` is the complete current code set (a superset of v19_2, v19_3 and v19_4 tarballs); unpack it from `test_colonial` (`tar xzf colonial_code_latest.tar.gz`); it does not touch `truth/`. The new video / zones scripts need the updated slurm from it (`VIDEO_OVERRIDE`, safe for the old runs).
**35c. Picking a 2025+ video without knowing the path.** `python code/find_new_videos.py` walks `/orange/xiangyan/rithika/vision/pilot_clips/MioVision Data` (override with `--root`), lists files whose path contains a date >= 2025 with their resolution, picks the highest-resolution one (`--pick random` for a random one) and prints the exact commands (ffmpeg 15-minute cut, `probe_video.py`, `extract_ref_frames.py`, `run_new_video.sh`). The suggested START assumes the 2019 naming (file number NNN = hour NNN-1): confirm it. It was tested on a synthetic folder tree only; if the date is not in the file names it finds nothing (`--min-year 0` lists everything). A different site means different zones and a detector fine-tuned on Colonial footage: the result is a robustness test, not a like-for-like score.
**35d. Roboflow for the zones.** Upload a clean frame (`extract_ref_frames.py` output), create a polygon (instance segmentation) project with classes road, bike, sidewalk, ONE polygon per class, export COCO, then `python code/roboflow_to_zones.py --coco _annotations.coco.json --out zones/colonial_north_v2.json`. The converter recognises names containing road / bike / side, keeps the largest polygon per class, writes `ref_size` from the export (so resizing in Roboflow is fine if the aspect ratio is kept). Tested on a synthetic COCO file only.

## 37. The 2025 video (fisheye) and the zone polygons for it (2026-10-12)
**37a. What was run.** On a 15-minute clip of a 2025 video (the file path is not recorded here: ask Rithika): `SLICE=853 bash code/run_new_video.sh` with TAG `corrine2025_706`, jobs `nv_base_corrine2025_706` (control) and `nv_combo_corrine2025_706` (SAHI slice 853 + veto 15 + night short rule + lateral speed rule + static filter; no zones file). The first search of `/orange/xiangyan/rithika/vision/pilot_clips/MioVision Data` found 55 files: 2019 (BL Colonial), 2021 (Anderson St, Church Ave), 2022 (Curry Ford North), ALL 720x480 at 30 fps, nothing from 2023 or later. Results (counts, clips) were not sent back to this chat; check `counts/nv_*_corrine2025_706/` and `annotated/nv_*_corrine2025_706/` (clips with explicit names after `python code/collect_clips.py --root . --prefix nv_`, copies in `exp_results/clips/`).
**37b. Her verdict after watching the 2025 videos:** not good for this pipeline. The camera is a FISHEYE: cars directly below the camera are not detected; things are detected when they are not too close to the camera. The detector (`rtdetr_v3`) was fine-tuned on rectilinear 720x480 footage of the 2019 Colonial camera, so a fisheye view is a different domain (strong distortion, perspective, scale). Consequences: the 2025 clip is NOT a like-for-like test of anything in sections 0-35; the pixel-based settings (static filter 5 px, stitch / split distances, the 30 px static-direction cutoff, SAHI slice) and the speed-in-body-heights rule were set for the old view and are not validated there; the veto/speed rules depend on box height and ground-point movement that fisheye distortion changes. Possible directions (not started): undistort the fisheye frames before detection if the lens parameters are known; fine-tune on labelled fisheye frames; or treat the 2025 clips as a limitation to report (the better resolution does not help if the geometry is the problem).
**37c. Zone polygons for the COLONIAL 2019 camera (new zones file, 2026-10-12; CORRECTION: an earlier version of this README wrongly said they were for the 2025 video).** Given by Rithika, re-drawn because the bike lane in `colonial_north_v1.json` was wrong. Saved as `colonial_north_v2.json` (in the outputs folder; goes to `zones/colonial_north_v2.json` next to `colonial_north_v1.json`):
bikelane = [[107,71],[925,407],[1422,698],[1418,953],[1230,945],[64,81]]
sidewalk = [[1228,947],[674,947],[431,760],[206,502],[23,116],[60,83]]
grass = [[21,119],[206,506],[435,764],[682,951],[16,951],[4,123]]
main road = [[99,71],[616,273],[925,407],[1420,694],[1418,71],[1340,40],[107,40]]
Mapping: bikelane -> `bike`, main road -> `road`, sidewalk -> `sidewalk`; `grass` is kept in the file but the pipeline reads only road, bike and sidewalk (extra keys such as `grass` and `_note` are ignored by the loader). The frame size they were drawn on was not stated. The coordinates reach (1422, 953), and the aspect ratio matches 2x the 720x480 video, so `ref_size` is set to [1440, 960] as an INFERENCE (the pipeline scales every polygon by video size / ref_size, so with this value the 720x480 video gets the points halved). VERIFY before trusting it: `python code/extract_ref_frames.py --colonial-chunk 13 --times 5:00` then `python code/draw_zones_preview.py --zones zones/colonial_north_v2.json --image zones/ref/<frame>.png --out zones/ref/preview_v2.png` and look at the picture (road green, bike lane yellow, sidewalk magenta, grass cyan). If the shapes do not sit on the real road / lane / sidewalk, the drawing size was different: tell the assistant what size the image had when drawn. To use the file in a run, set `ZONES_JSON=$ROOT/zones/colonial_north_v2.json`; the `run_batch*.sh` scripts hard-code `colonial_north_v1.json` (change with `sed -i 's#colonial_north_v1.json#colonial_north_v2.json#' code/run_batch4.sh`). Effect on results: person counts and every score in this README are unaffected by zones (zones never remove people); the road polygon changes vehicle counts, the bike polygon changes the bike-lane vs sidewalk column. `grass` could later be used to study pedestrians walking on grass (one 12:45 pedestrian was never counted), but nothing reads it yet. `stamp_zone_size.py` (writes ref_size from a video and checks all points are inside the frame) is available for files whose drawing size equals the video size.
**37d. Colonial zones: status.** Done (polygons given, section 37c); still to verify with `draw_zones_preview.py`. The Roboflow route (`roboflow_to_zones.py`, section 35) and `zone_annotator.html` remain available if a polygon needs redrawing. No zones file exists for the 2025 fisheye video.

## 38. HAND-OFF for a new chat session (written 2026-10-12)
**Give the new session:** this README (v29), `colonial_code_latest.tar.gz` (all current code; unpack from the `test_colonial` folder), and the four truth files (`colonial_truth_final.tar.gz`). Tell it to read section 0 first, then sections 35, 37 and this section; older sections hold superseded guesses (list of corrections in section 0).
**Cluster facts.** Project folder (`ROOT`): `/orange/xiangyan/rithika/vision/vision3/best/test_colonial`. Always run commands from there, never from inside `code/`. Environment: `source /orange/xiangyan/rithika/vision/yolo_env/bin/activate`. Slurm: one GPU per job, partition `hpg-turin`, account and qos `xiangyan`; the job script is `code/run_xclip_colonial_v19.slurm` (all options are environment variables, listed at its top); jobs are submitted by the `run_*.sh` scripts. Folders: `counts/<run>/` (tables), `annotated/<run>/` (clips), `logs/`, `truth/` (hand-made truth), `zones/`, `exp_results/` (reports, `clips/`). Old Colonial videos: `/orange/xiangyan/rithika/vision/pilot_clips/MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/Standard_SCU8OG_2019-07-10_0000/Standard_SCU8OG_2019-07-10_0000.NNN.mp4` (NNN-1 = hour). Clips used for scoring (video position = clock minus clip start): night 21:15-21:30 (hour file 22, frames 26978-53946), day 14:00-14:15 (file 15, frames 1-26973), night 22:00-22:15 hold-out (file 23, frames 1-26973), day 12:45-13:00 hold-out (file 13, frames 80924-end).
**The best pipeline in one paragraph.** `rtdetr_v3` detector + SAHI slicing (640 px) + tracker + X-CLIP per track + 3 s minimum; fusion rules (detector veto 15%, lateral speed rule 0.8 / 2.0 body heights/s, night-only short-track rule 21:00-06:00); static-object filter (net < 5 px and path speed < 0.05 h/s). The exact settings of each named run are in the `ENVV` line of the matching `run_batch*.sh` and in each run's `logs/<run>/*_run_log.json`. Current best run: `b4_combo_static5` (19 of 21 people found, 0 false tracks on the four labelled clips).
**Scripts.** `eval_truth.py` (person-level scoring against `truth/`), `fusion_probe.py` (features of truth people and false tracks, rules replayed), `disp_check.py`, `collect_clips.py` (explicit clip names), `extract_ref_frames.py`, `probe_video.py`, `find_new_videos.py`, `run_new_video.sh`, `stamp_zone_size.py`, `roboflow_to_zones.py`, `zone_annotator.html`, `test_v19.py` (helper tests), batch scripts `run_all_experiments.sh`, `run_batch2.sh` ... `run_batch4.sh`, `run_night04_only.sh`. After any batch: `grep -L "Final counts" logs/slurm_<run>*.log` (prints nothing if all jobs worked), then `python code/eval_truth.py --root . --runs ... --baseline exp0_base` and `python code/fusion_probe.py --root . --runs ...`.
**How Rithika works (so the next session does not repeat mistakes).** She runs commands in a terminal on HiPerGator and pastes the output back; give exact copy-paste commands, from the `test_colonial` folder. Several times a command was run from inside `code/` or a tarball unpacked in the wrong folder (so `code/code/` appeared): say where to run. Running a submit script twice submits the jobs twice. She wants every result and decision recorded in the README, and corrections stated plainly (a few earlier statements were wrong and were corrected later: see section 0). Ground truth = her own hand-made person lists from watching the clips; the old count file is unreliable. She has a professor who asked for a higher-resolution 2025 test (done, see 37).
**Open work, in order of value.** (1) Fresh evidence: label 2-3 NEW 15-minute windows (one night, two day, other hours of the 2019 Colonial day or the 2021 / 2022 videos) and score `b4_combo_static5` on them; the four current clips have all been looked at. (2) Remaining errors: night pedestrian called a cyclist (14:47), night 2.4 s rider under the 3 s minimum. (3) Fine-tune the detector on her own hard frames (night, walking away, far, motorcycle class): her stated fallback, not done; frames must come from clips other than the four scored ones. (4) Fisheye 2025 video: only with undistortion or fisheye fine-tuning (37b). (5) Verify the new Colonial zones file `colonial_north_v2.json` with `draw_zones_preview.py` (37c). Not started and probably not worth it: enhancement, motion-blob diagnostic, promote rule (no gain), temporal detector, BNE-DETR, SAMURAI.

## 39. Tools for the pending work (written 2026-10-15; NOT yet run on the cluster)
**What this is.** Code for the open items of section 38 / the 10/15 weekly deck, written off-cluster with the README only (the code tarballs were not available), tested on synthetic files (fake videos, fake model module, fake `sbatch`). Nothing here changes `b4_combo_static5` or any score. Unpack from `test_colonial`: `tar xzf colonial_pending_tools.tar.gz` (adds files to `code/`, touches nothing else). Run everything from `test_colonial`, never from inside `code/`. Submit each `sbatch` once.
**Things assumed from this README and to VERIFY on first use (each tool prints what it read before doing anything):** (a) `run_batch4.sh` has a line starting `ENVV=` holding the settings of the run (`scale_up.py`, `pick_new_windows.py` copy it; RUN / START_FRAME / MAX_FRAMES are stripped and replaced); if the format differs, pass `--envv "A=1,B=2"`. (b) The slurm file is `code/run_xclip_colonial_v19.slurm` and the array id is the hour-file number. (c) Track tables have the columns of `track_truth_runs45_v2.csv` (`clip_hint`, `first_time`, `bin_start`, `secs`); `review_pack.py inspect` shows what is missing. (d) The base training set is `dataset_frames/roboflow_split_v1` in YOLO layout with a `data.yaml`. (e) `finetune_v5.slurm` copies the partition / account lines from section 38: compare with the v19 slurm.
**39a. 24 h / 48 h scale-up: `code/scale_up.py`.** `python code/scale_up.py plan --run b4_full_block1 --chunks 1-24 --from-batch code/run_batch4.sh` prints the sbatch line (dry run, about 46 GPU-hours; 48 h about 92). Add `--go` to submit once; it refuses a second submission of the same run name (checks `counts/<run>` and `logs/.scale_<run>.lock`). `python code/scale_up.py check --run b4_full_block1 --chunks 1-24` lists chunks without output and prints the resubmit command. Recommended order unchanged (section 16, 38): only after new clips (39b) and, ideally, fine-tuning (39c).
**39b. New clips: `code/pick_new_windows.py`.** `python code/pick_new_windows.py --like truth/day_1400_truth.csv --from-batch code/run_batch4.sh` picks 2 day + 1 night 15-minute windows outside the clip hours already checked (default hours 8:15, 9:30, 23:20; change with `--windows 17:00,...`), prints the ffmpeg cut command (`new_clips/`), writes truth templates (`truth/new_HHMM_truth_TEMPLATE.csv`, header copied from an existing truth file) and the sbatch line running the SAME settings as `b4_combo_static5` on exactly that window (`START_FRAME` = offset x 29.97 + 5, `MAX_FRAMES` = stop). Watch each clip, fill the truth file (one row per person, motorcycle = cyclist), rename it without `_TEMPLATE`, then `python code/eval_truth.py --root . --runs exp0_base,b4_combo_static5,b4_new_0815,... --baseline exp0_base`. Check the night window really is dark. A different site (2021 / 2022 videos, all 720x480) needs its own zones and video folder: not covered.
**39c. Fine-tune on own hard frames: `code/finetune_v5.py` + `code/finetune_v5.slurm`.** (1) `pick`: random frames from the hour files you name, NEVER inside the four scored clips (+/- 30 s) and 20 s apart, pre-labelled by the current detector (`--weights`), class names matched by name to the base `data.yaml`. Night = files 22-24 and 1-6. `--times 22:3500` adds specific moments. (2) Correct the boxes yourself (Roboflow / CVAT), export YOLO to `<out>_fixed/{images,labels}` with the same file names. Boxes the detector never drew (the whole point) must be added by hand. (3) `build`: base train x3 + your frames x3, validation by 10-minute segment (a segment never sits in both train and val); warns if one side gets nothing. (4) `sbatch code/finetune_v5.slurm` trains `rtdetr_v5_colonial` from `rtdetr_v3/best.pt` (AdamW, lr0 1e-4, imgsz 640, batch 8, seed 42, patience 15). (5) Test like every other change: copy `run_batch4.sh`, change only the weights (the earlier NightOwls test changed only `WEIGHTS`) and the run name, run on the four clips and on the 39b windows. Accept only if it beats 19/21 with no new false tracks on both. Motorcycle stays inside cyclist unless you add a class to `data.yaml` yourself. The earlier outside-dataset fine-tune made every class worse (section 19), so check vehicle counts too. `ultralytics` calls are untested here (no GPU, no package): if `train` or `pick --weights` errors, send the traceback.
**39d. Labelling + high-sensitivity review: `code/review_pack.py`.** One tool, two uses. PER-TRACK ACCURACY: `inspect`, then `build --table validation/track_truth_runs45_v2.csv --out review/pack1` cuts a 3 s-padded clip per track and writes `review.html` (download the folder, open it in a browser, keys b / p / n, `Download labels CSV`), then `merge` writes a NEW labelled csv (never overwrites) and `python code/track_truth_v1.py eval --file <that csv>` gives per-object accuracy (needs >= 40 labelled tracks; label from the video only). HUMAN REVIEW WITH HIGH SENSITIVITY: run the pipeline with a low threshold (more candidates), then `build ... --rank-col <a 0-1 column such as the detector cyclist share> --budget-min 12` keeps only the best-ranked candidates that fit 12 minutes of clips per hour; after labelling, `curve --pack ... --labels ... --truth-count N` prints review minutes vs real people found vs false candidates, i.e. where the review should stop. It cannot see people the pipeline never tracked. The browser page was syntax-checked (node) but NOT opened in a real browser.
**39e. Fisheye 2025: `code/undistort_fisheye.py`.** Lens parameters are unknown, so it works from a field-of-view guess (equidistant model, others available): `preview --image frame.png --out p.png --fovs 150,180,200 --out-fov 110 --pitch 40` shows guesses side by side (choose where straight lines look straight), `video --video in.mp4 --out out.mp4 --fov 180 --out-fov 110 --pitch 40` converts a clip, `selftest` runs a synthetic round trip (passes: mean difference 4.6 of 255 in the centre). A flat view cannot show 180 degrees and anything straight below the camera is stretched hard (the 'cars right below' problem stays): use `--pitch` and possibly two views. Whether the detector then works is untested: score the converted clip against a hand truth file; fine-tuning on labelled fisheye frames (39c with fisheye frames) is the alternative; reporting it as a limitation is the third. Decide with the professor.
**39f. NOT coded, and why.** (1) Fixing the two remaining errors (night pedestrian called a cyclist at 14:47; the 2.4 s night rider under the 3 s minimum): any new threshold would be set on the same two clips; do it only after 39b windows exist and judge on them. (2) Why people walking away are missed: no new tool needed; label the walking-away people in the 14:00 and new clips, then `eval_truth.py` + `fusion_probe.py` show which stage (detector, track, label) lost each one. (3) Temporal detector, BNE-DETR, SAMURAI: section 38 rates them probably not worth it before fine-tuning. (4) Another site: needs zones and a truth file for that site.

## 40. Requests of 2026-10-15 (evening) and what was written (NOT yet run on the cluster)
**Decisions by Rithika.** (1) Do NOT create new truth files for the three `b4_new_*` windows; use existing videos that already have truth; delete the empty `truth/new_*_truth.csv`. (The runs `b4_new_0815/0930/2320` finished (47 min each; counts 0/0, 0/3, 0/1 bicyclists/pedestrians, unscored, no truth) and are ignored. `new_clips/new_0815.mp4` is corrupt (cut was interrupted): delete the folder.) (2) Fine-tuning on own images and 24 h / 48 h scale-up are LATER (future work), not on the to-do list. (3) Never overwrite `rtdetr_v3`; fine-tunes get a new name. (4) The weekly deck must explain everything in plain language (audience: her professor), state the tracker by name (ByteTrack + ID stitching) and the exact fusion rules with thresholds (no equation exists: if-then rules), and give statistics on what speed contributed. (5) Plan for evidence beyond the 4 labelled clips: one 15-minute video each from 2022, 2023, 2024, 2025 (better resolution), chosen where people actually appear; she will write the truth for those after the model has run. Do NOT reuse the Colonial zone polygons for other locations or years.
**What the facts are.** `find_new_videos.py --min-year 0` (55 files) shows only 2019 Colonial (35 files), 2021 Anderson St, Church Ave and 2022 Curry Ford North (all 720x480). No 2023 / 2024 / 2025 video exists under `MioVision Data`; the 2025 Corrine Dr video is somewhere else (path unknown). The Excel files in `/orange/xiangyan/rithika/vision/Bike Lane Study Counts` are 2019 counts, so they cannot choose windows for 2022+.
**Speed statistics (from section 29, 21 people):** lateral speed rule 0.8 / 2.0 changed 4 tracks (n4, d2, d3, h1), all correct; the 1.0 / 2.0 version wrongly changed 2 real cyclists (d1, h2). Detector veto 15% changed 3 tracks (d2, d3, h5), all correct. The two rules overlap (d2, d3) and no run removes speed from the final combo: the ablation below measures it. Speed = sideways movement of the smoothed foot point (px/s) divided by box height (px) = body heights per second, only for left/right-moving tracks seen >= 1.5 s; thresholds were estimated by hand (synthetic: 1.4 m/s walker 0.8, 5 m/s rider 2.9), NOT calibrated, NOT in km/h, NOT checked against the speed Excel files. The standard method (camera calibration / homography to metres on the road) is not done.
**40a. `code/run_batch5.py ablation`**: runs `b5_nospeed` (SPEED_RULE=0) and `b5_noveto` (DET_VETO_PCT=0) on the four labelled clips (8 jobs, ~6 GPU-hours), settings read from `run_batch4.sh` (NETPX 5). Score: `python code/eval_truth.py --root . --runs exp0_base,b4_combo_static5,b5_nospeed,b5_noveto --baseline exp0_base`.
**40b. `code/run_batch5.py bright`**: brightening retest done fairly: night clips 21:15 and 22:00, with SAHI and all current rules, brightening on BOTH the detector input and the X-CLIP crops (`ENHANCE_CROPS=1`), modes gamma / clahe / zerodce (only those found in the script). The first test used the plain detector, no SAHI, detector input only, one night clip. It checks that the slurm has the variable (searched as `ENHANCE*`) and stops with a grep command if not. Score: `python code/eval_truth.py --root . --runs b4_combo_static5,b5_bright_gamma,b5_bright_clahe,b5_bright_zerodce --baseline exp0_base`.
**40c. `code/pick_busy_windows.py` + `pick_busy.slurm`**: for a list of videos (`videos_to_scan.txt`) records resolution / fps / length and finds the busiest 15-minute window (detector on one frame per 3 s, `person` + `cyclist`, no SAHI) and writes ffmpeg cut commands to `busy/windows.txt` and `busy/inventory.csv`. After the cut: run the pipeline with `run_new_video.sh` WITHOUT zones, scale pixel settings (`STATIC_MAX_NET_PX` x width/720) if the resolution is higher, then she labels people, then score.
**40d. Fisheye 2025:** `undistort_fisheye.py` (section 39e) is the tool; sequence: find the video path, extract one frame, `preview`, choose fov / out-fov / pitch by eye, `video`, run `run_new_video.sh` on the flat clip, compare with her hand list. A flat view cannot show what is straight below the lens; if cars there stay undetected, fisheye fine-tuning or reporting a limitation remain.
**40e. Not coded.** (1) Change detection for objects that appear in a still scene: the first version (`*_motion_candidates`) gave 447 / 185 blobs, no discrimination; a usable version needs a background model, size and zone filters, and re-detection on an upscaled crop of every unexplained blob; design only. A person under an umbrella with the face hidden is a hard case that more likely needs fine-tuning on such examples. (2) Night-specific detector (BNE-DETR): no ready-made implementation known to me; re-implementing from the paper is research-size; the cheap alternative is a night fine-tune of RT-DETR (later). (3) Speed validation against the Excel speed files: needs the file contents (`bicyclist speeds.xlsx`, `Colonial_North_676806_07-10-2019.xls`) and a pixel-to-metre calibration. (4) Removing a label from the annotated video overlay: needs the overlay code; the yellow line 'AI n vs GT m' = the model's count vs the human count from the 2019 Excel for that bin (human counts are unreliable and do not exist for 2021+); ask for `grep -n "GT" code/xclip_overlay_v19_colonial.py`.

## 36. README change log (old header text, versions v7-v18)
Status as of 2026-10-09 (v18 of this README: 25h = batch-2 results + fusion probe, 25i = batch 3; v17 notes: 25g = commands for after the runs, `run_night04_only.sh`; v16 notes: adds runs b2_6/b2_7 (flat 0.4 s night minimum) in 25f; v15 notes: section 25 = FINAL night 21:15 truth, how the labels are decided now, speed-rule problem + `--speed-lateral-only`, `fusion_probe.py`, run `b2_5_sahi_speed`; v14 notes: adds section 24 = BATCH 2 (code written + dry-run, NOT yet run on the cluster) and the new clip naming; v13 notes: section 23h now holds the RESULTS of the v19 batch (all 11 jobs ran, 30-43 min each); v12 notes: section 21 now holds her FINAL 14:00 truth (1 cyclist + 4 pedestrians, with times); v11 notes: CORRECTS my wrong inference about the 14:00 clip (section 21 and 22b/23a notes) after her truth file; v10 notes: adds section 23 = v19 experiment code (E1 SAHI, E2 enhancement, E3 rules + motion diagnostic) written and unit-tested but NOT yet run on the cluster, plus the one-command run and the truth-file evaluation; E4-E7 are NOT coded yet. v9 notes: adds section 22 = PLAN for detector-improvement experiments, written for review BEFORE any code; no code for it exists yet. v8 notes: section 20 = v18 day/night settings, now RUN, results in 20d; adds section 21 = Rithika's own watch-the-clip observations, which are the visual ground truth to use from now on; v7, v6, v5, v4, v3, v2 untouched). `rtdetr_v3` and the v17 script/slurm are unchanged and remain the working setup (v18 is a new file; with no night options it counts exactly like v17). Everything measured in sections 5-13 is on 7 of the 48 recorded hours; read the caveats before quoting numbers. The v17 tests in 15g-15m and section 19 cover only two 15-minute windows and one zones hour: treat them as leads, not conclusions.

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


## 42. Task audit and repository organization (2026-10-19)

Current task status is in `docs/TODO.md` from the repository root, with exact sync/run/review steps in `docs/HIPERGATOR_RUNBOOK.md`. Original do/look/todo notes are preserved in `docs/tasks/`. This README moved to `docs/colonial/`; current inference remains at `vision3/best/test_colonial/code/` unchanged in location. 435 old plain-text logs and 15 identical root duplicates were removed; differing root sources were archived. Structured JSON run records, saved counts, truth and 15 batch-5/scan logs remain. The obsolete recovery tarball was removed because Git push/pull now transfers the source changes.

The requested detector/X-CLIP case audit is in `vision3/best/test_colonial/exp_results/FUSION_cases_20261019.md`: both right 11, both wrong 2, detector-only right 5, X-CLIP-only right 3, on the same 21 matched people. The 45-track sheets have NO human labels yet; review_pack.slurm now prepares raw-footage snippets to avoid model-label bias. review_pack refuses overwriting completed packs and stops on cut errors. track_truth labels its old fusion formula explicitly; it is not b4. scale_up now resolves the static pixel threshold and requires exact chunk track/bin tables when checking output. No training, new inference, human labels or scale-up was performed locally.


## 43. Scope correction and presentation update (2026-10-19)

The request for 2025 cameras means a video with more actual detail than the 720x480 Colonial truth source, regardless of year. There is no requirement for one video per year. Corrine 706 is confirmed 960x540 at 15 fps (1.5x encoded pixels), but its fisheye lens and different scene confound a pure resolution comparison. The 2022 Curry Ford files previously reported at 720x480 do not establish higher-resolution evidence. `pick_busy.slurm` now passes --higher-res-only; the inventory records all candidate dimensions and scan_status while skipping detection scans on sources not exceeding 720x480 pixels. A higher encoded pixel count cannot prove footage was never upscaled or that people contain more usable detail.

No relabelling of the existing four truth clips is required. Exact annotated paths were recovered from saved run JSON and recorded in docs/VIDEO_PATHS.md. These refer to cluster videos; the Mac has no copy of them. The optional night/day spot-checks verify identities and prior uncertainty. The existing Corrine clip has no truth; new truth is needed only if a new higher-resolution test is scored. The separate 40-track task and own-night fine-tuning are on the back burner; full-day scaling is removed from the plan. Historical tools are retained without active run instructions.

The new presentation is reports/presentations/bike_weekly_meeting_10_19.pptx and follows active todo items. Research primary sources and limits are in docs/RESEARCH_METHODS.md: multi-scale/flip test-time inference and Grounding DINO are newly shortlisted frozen-model experiments; temporal feature aggregation was already discussed and remains a larger integration. BNE-DETR public source exists, correcting the older deck. No new method has measured project gains yet.


## 44. One-command research suite (2026-10-19; written locally, NOT yet run)

User has not pushed/pulled or submitted yet. README.md at the repository root is the single entry point. New files: submit_research.py, research_job.slurm, research_worker.py, research_detection.py, grounding_audit.py, test_research_recovery.py. Optional --tta / TTA=1 adds 960/1280 full-frame scale and horizontal-flip person proposals, maps flips to source coordinates, merges before tracking, and preserves the existing SAHI/full-frame vehicle path. The suite uses unique run names and existing truth to test TTA and sensitive candidates; a separate pinned Transformers environment runs Grounding DINO sampled-frame audits against saved b4 tracks. It does not convert bicycle boxes into counts.

The suite also runs the resolution-aware scan, matched baseline/combo/TTA on the known Corrine clip if present, zone/fisheye previews, a 12-minute raw review pack, conditional Zero-DCE retries if its checkpoint exists, and an afterany-dependent final report. Up to 22 tasks (normally 20 without Zero-DCE), four simultaneous GPU tasks maximum within this suite. Preparation downloads model files and performs an actual GPU smoke check on the cluster. Local tests cannot establish cluster/network/model compatibility or improved accuracy. Failed/skipped/incomplete tasks are recorded and incomplete experiment groups excluded from person-level score summaries. Full-day scaling, 40-track labels, own-night training, temporal detector integration and BNE replacement are excluded.
