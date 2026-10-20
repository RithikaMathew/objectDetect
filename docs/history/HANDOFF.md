# Current handoff — 2026-10-19

This section supersedes the September handoff retained below. Start with **root README.md**; do not resubmit the completed research_oct19 suite.

## Latest evidence and interpretation

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

Latest presentation: `reports/presentations/bike_weekly_meeting_10_19_results.pptx` (12 slides, updated and visually checked). Earlier presentations remain historical.

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
