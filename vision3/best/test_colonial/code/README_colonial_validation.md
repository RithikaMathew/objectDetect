# Colonial North: validating the fine-tuned RT-DETR + X-CLIP bicyclist counter

Status as of 2026-10-05. Everything below is measured on 7 of the 48 recorded hours; read the caveats before quoting numbers.

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
6. Optional zones (road / bike lane / sidewalk) filter vehicles and give the bike-lane vs sidewalk split.

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

Bugs found by testing on a stand-in pipeline (fake detector/tracker on a synthetic video): the run log was saved under the wrong filename and the clip list got overwritten by a variable-name collision, both fixed. A mistaken `MAX_FRAMES` setting produced a 1-second test clip (it is a stop frame, not a count).

## 8. Limitations
- **Small sample:** 7 of 48 hours (about 14%), 28 bins, 24 bicyclists in the ground truth. One missed rider moves a bin by 100%.
- **Tuning and testing overlap:** thresholds were explored on the same hours they are reported on.
- **No zones in any run**, so bike-lane/sidewalk results are not reported and vehicles were not filtered.
- **One camera, one site.** Night video only from one hour.
- **Ground truth is counts only** (no per-person labels), so precision/recall are approximations. Human counters can disagree with the video.

## 9. Next steps (in priority order)
1. **Zones:** create `zones/colonial_north_v1.json`, confirm "zones loaded" in the log, verify the facility column and the vehicle filter on one hour.
2. **Night:** check the pending `night_dc015` test (detector confidence 0.15 on 21:15-21:30). If the detector still misses visible riders in the dark, night frames need to go into fine-tuning.
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

## 13. Still to fill in
- Result of `night_dc015` (detector threshold at night).
- Result of `bin2_v14b` (07:15-07:30 with static filter and lower detector threshold).
- Hand-labelled track set and the resulting per-object accuracy (`track_truth_v1.py`).
- Fusion sweep (colonial_run4 + colonial_run5): replace with the `sweep_fusion_v2.py` table.
