# Progress Checklist

Running record of what's done and what's next. Updated 2026-09-19.

**New here? Read [HANDOFF.md](HANDOFF.md) first** — full context, current
state, and the reasoning behind the next step.

Companion docs: [METHODOLOGY.md](METHODOLOGY.md) (the why),
[HIPERGATOR_COMMANDS.md](HIPERGATOR_COMMANDS.md) (the commands),
[NEXT_STEPS.md](NEXT_STEPS.md) (decisions and reasoning).

---

## Phase 1 — Ground truth  ✅ COMPLETE

- [x] Parse all ~40 raw corridor `.xls` files → `raw_counts_extracted.csv`
- [x] Build `ground_truth_bicycle_counts.csv` (202 rows, 41 site-sessions, 5,053 cyclists)
- [x] Catch and remove embedded duplicate data (Alafaya West, University North, S Orange NB)
- [x] Catch and remove two fully duplicate files
- [x] Cross-validate against hand-derived totals (Alafaya E 245, W 251, Univ S 248, E+W 496)
- [x] **Fix empty `facility_type` / `movement` columns** — were blank in 202/202 rows
      → `ground_truth_bicycle_counts_v2.csv` (`fix_ground_truth.py`)
- [x] Finding: **63% of cyclists ride on sidewalks** (3,160 sw / 1,125 bl / 531 path / 237 tl)
- [ ] **Extract 15-minute interval counts** — `parse_raw_counts.py` keeps only total
      rows, so there is no time-of-day ground truth. **BLOCKS interval-level
      validation and ground-truth-guided frame mining.** Needs 2-3 raw `.xls`
      files to write.

## Phase 2 — Video ↔ ground truth join  ✅ COMPLETE

- [x] `build_site_mapping.py` → `video_site_mapping.csv`
- [x] **41/41 site-sessions matched, 0 unmatched, 0 ambiguous**
- [x] Disambiguate same-date pairs by facility token (BL/NBL/SW/TL)
- [x] **Discovered the study is a matched-pair design** — every date deployed two
      cameras, one bike-lane site + one no-bike-lane control. 17 pairs. Settles
      the old open question about two-camera-same-session pairs.
- [x] Map chunk index → wall-clock hour from `all_videos.txt` (`.001` = 05:00)

## Phase 3 — Fix the pipeline  ✅ COMPLETE

Started at **0 cyclists tracked** on a clip containing a cyclist detected at
conf 0.92. Six distinct bugs, each found from logged evidence:

- [x] **IoU association gate** (`TRACK_IOU_MATCH_THRESH=0.3`) — passed only 3/12
      links on the known cyclist; box aspect flaps 114→62→50 px so IoU collapses
      even at 6.7 px of motion. Replaced with velocity-predicted,
      size-normalized centroid association. → `vru_tracker.py`
- [x] **Duplicate detections** — one rider produced 5 "cyclists" + 2
      "motorcycles" + 3 "persons". Added containment suppression (IoU-NMS
      structurally cannot remove a nested box), cyclist fusion before tracking,
      and redundant-track merging.
- [x] **Merge normalized by the wrong scale** — used the track's *final* box, so
      a receding cyclist (160 px → 29 px) had early distances inflated ~5×,
      while tracks ending large had them deflated and **a car merged with a
      pedestrian**. Now normalized per-timestamp.
- [x] **Merge required exactly-shared timestamps** — but assignment is
      one-to-one, so two tracks on one object *interleave* and share **0**
      timestamps. Added path interpolation + a succession test for fragments
      split across a gap.
- [x] **Class vote relabelled cyclists as pedestrians** — a cyclist always
      generates person detections and the rider is easier to detect, so summed
      votes flip to 'person' as the bike becomes unresolvable with distance.
      Bicycle evidence (max conf ≥ 0.40) is now decisive.
- [x] **Track termination counted samples, not time** — `max_missed=4` = 0.13 s
      at stride 1, killing a distant cyclist mid-crossing. And `predict()` only
      extrapolated one sample ahead, so coasting could never reacquire. Both
      fixed; now `--coast-seconds`.
- [x] Video: OpenCV picked `h264_v4l2m2m` (a hardware encoder absent on compute
      nodes) → now writes mp4v and transcodes with the ffmpeg binary
- [x] Video: renders **confirmed tracks only**, two-pass; `--video-mode
      highlights` for long runs
- [x] Trail smoothing (the "yellow squiggly line" was raw per-frame centroids)
- [x] Tile batching — 4 tiles in one GPU call instead of 4 sequential calls
- [x] 10-test regression suite covering every fix plus guards against
      over-merging (two opposing riders, two parallel riders, car+pedestrian)

**Result on the test window: 1 cyclist, correctly classified, one stable ID.**

## Phase 4 — Tier 1 validation  🔶 IN PROGRESS

- [x] `extract_session.slurm` — pull one session out of `MioVision_Data.zip`
- [x] `run_site_array.slurm` — Slurm job array, 48 chunks in parallel (~4.5 h
      vs ~4 days serially)
- [x] `cleanup_session.sh` — delete video only after every chunk has results
      (all 41 sessions = 325 GB vs 314 GB free, so extract→count→delete is
      mandatory)
- [x] `validate_counts.py` — join tracked output to ground truth
- [x] **BL Colonial 2019-07-10 counted: 88 vs ground truth 89 (−1.1%)**
- [x] `audit_tracks.py` — flag duplicate / static / ID-jump / night tracks
- [x] ⚠️ **CONFIRMED: the −1.1% is compensating errors.** 74% of the 88 tracks
      carry a red flag. ~8 duplicate over-counts + 23 static tracks ⇒ **~57
      plausibly real vs 89 ground truth ⇒ ~32 missed cyclists.** Night rate
      (2.12/h) exceeds day rate (1.69/h), which for a strongly diurnal
      behaviour indicates night false positives.
- [x] Render review clips (25 random + 34 night + 30 most-suspicious)
- [x] **Clip review done — 30 most-suspicious tracks scored by hand.**
      REAL 15 / DUP 8 / FP 6 / PED 1. **50% of the suspicious set is spurious.**
      Dominant FP mechanism: **9 false detections on grass/vegetation**.
      Also: 3 ID splits far→near, 3 misses at distance, 2 cyclists first read
      as cars, 1 over-merge of two riders into one ID.
- [x] ⚠️ **Two hypotheses DISPROVED by the review — do not implement:**
      (a) raising `MIN_NET_DISPLACEMENT` — STATIC does not predict spurious
      (47% vs 54%), and REAL cyclists have median excursion 2.85, min 0.97;
      (b) a night confidence penalty — NIGHT tracks were *less* spurious than
      day ones (36% vs 62%). The day/night rate anomaly is more likely daytime
      misses than night false positives.
- [ ] Cross-check the day/night split against
      `Bike lane study counts day v night.xlsx` (Totals sheet, % night per corridor)
- [ ] Review a 25-clip random sample of all counted cyclists (`--sample 25`)
- [ ] BL Edgewater 2019-08-07 (GT 228, bike-lane dominant)
- [ ] NBL Pine Hills 2019-08-28 (GT 317, sidewalk dominant — 311 of 317)
- [ ] Aloma Path 2019-10-30 (GT 191, shared-use path)
- [ ] `validate_counts.py --all` → first results table

## Phase 5 — Fine-tuning  🔶 NEXT — this is where the remaining error lives

Phase 4 established that tracker tuning is exhausted: six tracker bugs fixed,
and all three remaining failure modes trace to the detector's concept mismatch
rather than to association. See HANDOFF.md §5 for the evidence table.

- [x] `mine_frames_from_tracks.py` — mine annotation frames from the 88
      confirmed + 821 rejected cyclist tracks. Sidesteps the 15-min interval
      blocker: those 909 tracks are a curated pool of hard cases, and the
      rejected ones are exactly what the current model gets wrong.

- [x] `cyclist` class added to `extract_frames.py` (index 6, appended so
      existing labels stay valid) + fusion of overlapping person/bicycle
- [x] `--frame-conf` dropped 0.5 → 0.15 (at 0.5 you mine only what the model
      already gets right)
- [ ] Re-run `build_dataset.slurm` with the new class (move
      `dataset_frames/split` aside first — the resume check skips existing frames)
- [ ] Run `mine_frames_from_tracks.py` on BL Colonial (~2,000 frames expected)
- [ ] Annotate ~1,500–3,000 frames in CVAT (track interpolation; model-assisted
      pre-labels)
- [ ] Sliced fine-tuning matching inference tile geometry (SAHI-style)
- [ ] Held-out-**site** evaluation (never a random frame split)
- [ ] Model ablation: YOLOv8-L vs YOLO11-L vs YOLO26-L, identical settings

## Phase 6 — Paper  ⬜ NOT STARTED

- [ ] Tracker ablation figure (`tracker_ablation.py` — 7/11 vs 10/11 links,
      old 13 fragments vs new 3)
- [ ] 2×2 ablation: association (IoU / centroid) × dedup (on / off), against hand counts
- [ ] Count-supervised calibration (Idea B)
- [ ] Distribution-matching speed self-calibration (Idea A)
- [ ] Decide on Goal 5 (age/gender) — current recommendation: **cut it**
- [ ] Choose venue (transportation vs vision — changes framing substantially)

---

## Current numbers

| Metric | Value |
|---|---|
| Ground-truth sessions available | 41 (5,053 cyclists) |
| Sessions counted | 1 of 41 |
| BL Colonial 2019-07-10 | **88 vs 89 (−1.1%)** |
| Rejected cyclist-class tracks, that session | 821 (90% of candidates) |
| Night rate vs day rate | **2.12/h vs 1.69/h ← indicates night false positives** |
| Tracks carrying a red flag | **65 of 88 (74%)** |
| Estimated real cyclists found | **~55-65 of 89** (from verified review) |
| Spurious rate, 30 most-suspicious | **50%** (8 DUP + 6 FP + 1 PED) |
| Dominant FP mechanism | **grass / vegetation (9 of the notes)** |
| Sidewalk share of ground-truth cyclists | 63% |

## Known open questions

1. ~~Is the −1.1% real?~~ **Answered: compensating errors.** ~31 spurious
   counts offsetting ~32 misses.
2. Do the 821 rejected tracks contain real cyclists? They are now the mining
   pool for fine-tuning either way.
3. **Vehicle counting is unvalidated.** Goal 1 says "Cyclist + Vehicle
   Counting", but the Excel ground truth covers cyclists and pedestrians only.
   Vehicles are also held to stricter confirmation thresholds than cyclists
   (1.0s / 0.55 / 0.22 vs 0.5s / 0.50 / 0.18), which is why they look
   under-detected in the clips. Needs a scope decision.
3. Chunk `.013` had a surviving duplicate pair (`#31390`/`#31435`) and three
   near-static "cyclist" tracks (excursion 1.0–2.2 diagonals vs 32.8 for a
   clear crossing). Is `MIN_NET_DISPLACEMENT=0.75` too low?
4. Hour-boundary double-counting: chunks are tracked independently, so a
   crossing that spans an hour boundary counts twice. Expected < 1 per session,
   unmeasured.
