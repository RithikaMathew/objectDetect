# Methodology Guide — Archival Cyclist Vision Study

Working plan for turning ~40 sessions of 2019 MioVision footage + hand-collected
ground truth into a publishable paper. Written 2026-09-17.

---

## 0. What you actually have (the asset)

State this plainly in the paper, because it is the moat:

- **202 rows of independent, human-collected cyclist counts** — **5,053
  cyclists** across **41 site-sessions** — disaggregated by **facility type**,
  **direction**, and **movement** (With / Facing traffic).
- **Hand-timed speed distributions by facility type** (Travel Lane 14.5 mean /
  18.4 p85, Bike Lane 11.8 / 15.7, Sidewalk 9.3 / 12.4).
- **A day/night exposure-risk model** already computed per corridor.
- **The matching raw video** — 41/41 site-sessions joined to video folders
  (`video_site_mapping.csv`), zero orphans on either side.

### 0.1 It is a matched-pair natural experiment, not a convenience sample

The date join (`build_site_mapping.py`) revealed the study's design, which
nothing in the project documentation had recorded:

> **Every recording date deployed exactly TWO cameras simultaneously — one at a
> BL (bike lane) site, one at an NBL (no bike lane) control site.**

```
2019-05-22   BL Livingston  n=170   +   NBL Summerlin      n=169
2019-06-26   BL Glenridge   n=151   +   NBL Kaley          n=36
2019-08-07   BL Edgewater   n=228   +   NBL N Orange       n=130
2019-09-10   BL Columbia    n=243   +   NBL Carroll        n=31
```

with the same structure for path/sidewalk pairs (Aloma Path + Aloma SW,
Rinehart Path + Rinehart SW, Daniels, WORT) and the speed sub-study
(SW Speed University + TL Speed Winter Park; BL Speed Edgewater + TL Speed
Baxter). The folder prefixes decode as `BL` = bike lane, `NBL` = no bike lane,
`SW` = sidewalk, `TL` = travel lane.

This also answers the question left open in the earlier session notes — *"which
files are genuine two-camera-same-session pairs vs. count+later-speed-redo
pairs."* **They are same-session treatment/control pairs.**

**Why this is worth a great deal:** because each pair is recorded on the *same
day*, weather, season, day-of-week and time-of-year are controlled **by
construction**. You are not comparing bike-lane sites to control sites across a
noisy observational sample — you have 17 matched pairs. That supports causal
language most observational cycling-safety papers cannot use, and it is the
strongest single fact about this dataset. Lead with it.

### 0.2 Headline finding, previously locked in an unusable column

`facility_type` and `movement` were declared in the ground-truth CSV and
documented as populated, but were **empty in 202 of 202 rows**. Both are
recoverable from `channel_label` (`fix_ground_truth.py`, cross-checked against
all three hand-verified site totals). Once filled:

| Facility | Cyclists | Share |
|---|---|---|
| **Sidewalk** | **3,160** | **63%** |
| Bike lane | 1,125 | 22% |
| Path | 531 | 11% |
| Travel lane | 237 | 5% |

**Nearly two thirds of observed cyclists ride on the sidewalk**, roughly 3× the
bike-lane share. Individual sites are starker still — Pine Hils NBL E is 311
sidewalk vs 6 travel lane. That is a substantive transportation finding on its
own, and it has direct methodological consequences: any pipeline that assumes
cyclists appear in the bike lane will miss most of them, and ROI-cropping to the
bike lane would discard 78% of the data.

Almost every cyclist-detection paper validates against a few hundred hand-drawn
boxes on frames the authors labeled themselves. You have *independent*,
*facility-resolved*, *multi-site*, *paired-design* ground truth collected by
people who had never heard of your model. That is a stronger validation protocol
than the field's norm, and it is the thing to build the contribution around —
not the detector.

**Corollary:** do not frame this as "we detect cyclists with YOLO." That is
unpublishable in 2026. Frame it as a *measurement instrument* paper.

### 0.3 Known gap: no time-of-day resolution

`parse_raw_counts.py` locates each sheet's **total row** and discards the
15-minute interval rows beneath it. So the ground truth is currently *daily
totals per channel*, not a time series.

This blocks two things: per-interval count validation (Tier 1's stated gate),
and ground-truth-guided frame mining (§3.2), which needs to know *which
15-minute windows* contain cyclists. The interval data exists in the raw `.xls`
files and in `Bike lane study counts.xlsx` — it simply was not carried through.
**Re-extracting it is a P0 task** (§1.4).

---

## 1. Immediate engineering tasks (P0 — nothing else matters until these clear)

### 1.1 The zero-tracked-bicycles bug — SOLVED

**Root cause: `TRACK_IOU_MATCH_THRESH = 0.3` in `SimpleIouTracker`.**

Diagnosed directly from the boxes logged in `pilot_detect_41807016.log`, not by
hypothesis. Ruled out first:

- **Detection is fine.** The cyclist at t≈407–409 s is detected in every frame.
- **Frame stride is fine.** At 30 fps with `TRACK_EVERY_N_FRAMES=5`, the cyclist
  lands in **13 sampled frames**, against `min_track_hits = 6`.
- **Confidence threshold is fine.** All 13 sampled frames exceed `conf=0.2`
  (0.28, 0.34, 0.77, 0.92, 0.38, 0.76, 0.77, 0.47, 0.62, 0.49, 0.33, 0.36, 0.54).

What actually fails is association between those 13 frames. Measured IoU on
each of the 12 consecutive links:

| link | IoU | ≥0.3? | ‖Δcentroid‖ / diag | ≤1.0? |
|---|---|---|---|---|
| 407.40→407.57 | 0.259 | ✗ | 0.33 | ✓ |
| 407.57→407.74 | 0.000 | ✗ | 0.95 | ✓ |
| 407.74→407.90 | 0.287 | ✗ | 0.08 | ✓ |
| 407.90→408.07 | 0.233 | ✗ | 0.39 | ✓ |
| 408.07→408.24 | 0.270 | ✗ | 0.36 | ✓ |
| 408.24→408.41 | 0.311 | ✓ | 0.32 | ✓ |
| 408.41→408.57 | 0.230 | ✗ | 0.38 | ✓ |
| 408.57→408.74 | 0.238 | ✗ | 0.29 | ✓ |
| 408.74→408.91 | 0.361 | ✓ | 0.28 | ✓ |
| 408.91→409.07 | 0.274 | ✗ | 0.34 | ✓ |
| 409.07→409.24 | 0.287 | ✗ | 0.33 | ✓ |
| 409.24→409.41 | 0.355 | ✓ | 0.28 | ✓ |

**IoU@0.3 passes 3/12.** The track shatters into fragments of length
`[1,1,1,1,1,2,1,2,1,2]` — longest = **2 hits**, against a requirement of 6. Zero
counted. **Size-normalized centroid distance passes 12/12** → one clean 13-hit
track.

Mean IoU is 0.28, sitting *just* below the 0.3 gate — which is why this
produced a clean zero rather than erratic undercounting.

**Two compounding causes, both specific to small VRUs:**

1. Displacement per sample is large relative to box size. IoU collapses once
   the shift approaches the box dimension, and for a ~40 px cyclist at a
   5-frame stride it does.
2. **Box geometry is unstable.** The detector alternates between boxing the
   bicycle alone and the bicycle+rider; height swings 114→62→50 px across three
   samples. IoU punishes that even when the object barely moved — see
   407.74→407.90, where the centroid moves 6.7 px yet IoU is only 0.287.

Cars are immune to both (large, stable boxes), which is exactly why the same
clip tracked 85 cars and 0 bicycles. **The asymmetry was the clue.**

**This is a publishable finding, not just a bug.** "IoU association silently
zeroes out the rare class while appearing to work on the common class" is a
failure mode that transportation-CV papers using off-the-shelf trackers are
likely hitting without knowing. See Idea E in §4.

### 1.2 What was changed (code in this repo)

| File | What it does |
|---|---|
| `vru_tracker.py` | Velocity-predicted, size-normalized centroid association. IoU demoted to a tie-breaker in the cost, never a rejection gate. |
| `pilot_detect_v2.py` | Rewritten pipeline: track-before-detect, per-track motion filtering, funnel CSV, real annotated video. |
| `tracker_ablation.py` | Runs identical detections through old and new association. The paper's ablation table. |

Three further changes, each independently defensible:

**Track-before-detect.** Detection now runs at `conf=0.05` and the accept/reject
decision moves to *track* level (max confidence across the track). Per-frame
thresholding is the wrong place to threshold rare small objects — in the logged
window, per-frame confidence dips to 0.07 and 0.09 mid-track on a cyclist that
peaks at 0.92. Thresholding per frame discards exactly the marginal evidence
that tracking exists to accumulate.

**Motion filtering moved from per-detection to per-track.** The old
`MOTION_OVERLAP_THRESH=0.15` MOG2 check could delete a real cyclist whenever the
foreground mask was poor on one frame, and could not be loosened without
readmitting static false positives. Judging at track level is strictly better:
one decision with all the evidence. The metric is **max excursion from origin**,
in box diagonals — *not* total path length, because a static object's per-frame
jitter accumulates path length linearly with duration (a 60-frame static box
jittering ±1.5 px accumulates 2.79 diagonals of "path" and would pass any fixed
threshold given enough time). Max excursion stays flat at 0.09 for that same
track. This is verified by a unit test.

**Per-class persistence.** `MIN_TRACK_SECONDS` was 1.0 s for everything, tuned
on cars. A cyclist crosses the frame in ~2 s; a car waits at a light for 30 s.
Now `{bicycle: 0.5, person: 0.5, _default: 1.0}`.

### 1.3 Funnel logging (now built in)

`pilot_detect_v2.py` writes a per-frame CSV:

```
t_sec, frame_idx, n_raw_tile_dets, n_after_merge, n_in_roi,
n_matched, n_new_tracks, n_active_tracks, n_bicycle_dets, best_bicycle_conf
```

plus a per-track CSV with each track's hits, duration, max/mean confidence, net
displacement, max excursion, and whether it was counted. "Where does recall
leak" is now answerable from data. This is also the ablation table for the paper.

### 1.3 Stop chasing the YOLO26-vs-v8 car/truck discrepancy

`yolo26l` reporting car 13 vs `yolov8l` car 85 at the same `conf=0.2` is **not a
bug and not a calibration defect worth investigating.** YOLO26 is *NMS-free*: it
uses one-to-one label assignment, so it emits one box per object instead of a
cloud of near-duplicates that NMS later collapses. Its confidence scores live on
a different scale entirely. Comparing the two at a shared threshold is invalid.
If you want a real comparison, sweep the threshold and compare
**precision–recall curves / mAP**, never raw counts at a fixed `conf`. Drop this
thread; it costs you nothing to close.

---

## 2. Model choice: YOLOv8 vs YOLO26

**Short answer: use YOLO26-L as the primary, keep YOLOv8-L as the baseline row
in an ablation table. But this decision matters far less than fine-tuning.**

Reasoning:

| Factor | Verdict |
|---|---|
| Small objects | YOLO26 adds ProgLoss + STAL (Small-Target-Aware Label assignment), targeted at exactly your regime (30-px cyclists in a wide intersection view). Real gains reported on VisDrone-class data. |
| NMS-free | Removes one entire class of tile-merge pathology from your pipeline. You still need cross-tile dedup, but intra-tile duplicate suppression stops being a tunable you can get wrong. |
| Ecosystem / baselines | YOLOv8 has vastly more published transportation baselines. Reviewers know it. This is why it stays as the baseline row, not the primary. |
| Reviewer optics | "We used the newest model" is worth nothing. "We report v8-L / v11-L / 26-L under identical sliced fine-tuning and held-out-site evaluation" is worth a table. |

Do **not** spend weeks on model selection. Once you fine-tune on your own
domain, the architecture delta shrinks to a couple of mAP points, while the
fine-tuning delta is 20–40 points. Run the comparison *once*, as an ablation,
after the pipeline works.

---

## 3. Fine-tuning: yes, definitely — and not the way you were thinking

### 3.1 Why fine-tuning is non-optional here

1. **COCO's `bicycle` class is the wrong concept.** It is trained largely on
   ground-level, close-range, often *parked* bicycles. You need *cyclists*:
   small, overhead-oblique, motion-blurred, JPEG-compressed 2019 traffic-camera
   objects.
2. **COCO splits `person` and `bicycle` into two classes.** Your ground truth
   counts *cyclists*, a single rigid person+bike unit. Every downstream count
   requires you to fuse two COCO classes with a heuristic. Define a single
   `cyclist` class instead and the fusion heuristic — and its error mode —
   disappears from your pipeline.
3. **Your own evidence already shows the gap**: a cyclist at conf 0.84 in one
   frame and absent in the next is classic domain mismatch, not model capacity.

Recommended class set: `cyclist`, `pedestrian`, `car`, `truck/bus`,
`motorcycle`. Five classes. Resist adding more.

### 3.2 Don't hand-label from scratch. The modern loop:

**Step 1 — Ground-truth-guided mining (this is your unfair advantage).**
Your interval counts tell you *which 15-minute windows at which sites contain
how many cyclists*. That is a targeted search space. Instead of sampling frames
uniformly across 500+ hours of footage — where >99.99% of frames contain no
cyclist — mine only inside windows where ground truth says cyclists exist.
Estimated efficiency gain: 2–3 orders of magnitude of annotator time.
Worth writing up as a method subsection in its own right.

**Step 2 — Model-assisted pre-labels, not blank canvases.**
Run an open-vocabulary detector over mined frames with a text prompt
(`"a person riding a bicycle"`): GroundingDINO, OWLv2, YOLO-World, or
Grounded-SAM-2. These produce candidate boxes zero-shot. Humans then *verify and
correct*, which is roughly 5–10× faster than drawing. Ultralytics ships
`auto_annotate` for this.

**Step 3 — Exploit video, don't treat frames as independent.**
Label one frame per track and **interpolate boxes across the track**. CVAT does
this natively and it is the single biggest annotation multiplier available to
you — a 60-frame track costs 2 keyframes, not 60 boxes.

**Step 4 — Sliced fine-tuning (SAHI-style). Probably fixes part of your bug.**
Your pipeline **tiles at inference** but you are running a model **trained on
full frames**. That is a train/inference distribution mismatch: the model has
never seen a cyclist at the apparent scale a tile presents. The SAHI paper
reports +6.8/5.1/5.3 AP from sliced inference alone, rising to +12.7/13.4/14.5
AP *cumulative* when you also fine-tune on slices. Generate your training set as
**slices matching your inference tile geometry exactly** (same tile size, same
overlap). This is cheap and it is very likely worth more than any architecture
choice on this list.

**Step 5 — Active learning, 2–3 rounds.**
Round N: run the fine-tuned model over held-out sites → mine (a) low-confidence
detections, (b) **count-disagreement windows** where your tracked count differs
most from the hand count → label those → retrain. Stop when the count error on a
validation site stops improving. Two or three rounds is usually where the curve
flattens.

### 3.3 Tooling — what to use instead of "Roboflow or something"

Roboflow is a perfectly good *annotation UI and dataset host*, and if you're
already comfortable there, keep it. But it is not a curation engine, and
curation is your actual bottleneck at this scale.

| Job | Tool |
|---|---|
| Curation / mining / "which of my 500k frames should I label?" | **FiftyOne (Voxel51)** — built for exactly this: embeddings, uniqueness sampling, mistakenness ranking, side-by-side model-vs-GT views. This is the tool for "the dataset is huge and I'm lost." |
| Video annotation with track interpolation | **CVAT** (free, self-hostable on HiPerGator) |
| Hosted annotation + versioning + easy YOLO export | **Roboflow** (fine, keep it) |
| Sliced training/inference | **SAHI** (`obss/sahi`) |
| Experiment tracking | **Weights & Biases** or MLflow — you will run dozens of configs; do not track them in filenames |

### 3.4 Splits — the thing reviewers will attack

**Split by SITE, never by frame, and never randomly.**

Adjacent video frames are near-identical. A random frame split leaks the test set
into training and inflates mAP by a huge margin. It is the single most common
fatal flaw in transportation-CV papers and a competent reviewer looks for it
first.

Proposed protocol:

- **Train:** ~10 sites
- **Val (tuning):** 3 sites
- **Test (touch once, at the end):** 3 sites, chosen to span all facility types
  and including at least one night-heavy and one path site.
- Report **held-out-site** performance as the headline number. Report
  random-split numbers only if you want to *demonstrate* the inflation — which
  is itself a nice half-page contribution.

---

## 4. The research contribution — four candidate ideas

You need algorithmic significance, not a pipeline report. These are ranked by
how defensible the novelty claim is. **A and B together make a strong paper; C is
the highest-risk/highest-reward.**

### Idea A — Distribution-matching self-calibration from speed priors ★ strongest

**Problem.** Speed estimation from a monocular fixed camera needs a homography.
Standard practice requires manual reference points measured in the field. Your
footage is from **2019**; the cameras are gone, the sites have changed. You
physically cannot go measure. Existing auto-calibration methods rely on vanishing
points from lane markings or known vehicle dimensions — both fragile on
sidewalk/path cameras with no lane markings at all.

**The idea.** You have the hand-timed cyclist speed distribution per facility
type. Solve for the homography scale by **matching distributions**: find the
calibration parameters under which the observed *pixel* speed distribution of
tracked cyclists maps onto the known *MPH* distribution for that facility type.
No reference points, no site visit, no lane markings. The ground truth becomes
the calibration target rather than only the evaluation target.

**Why it's novel.** Auto-calibration literature uses geometric cues (vanishing
points, GNN homography estimation, known object sizes). Using a *behavioral prior
distribution* of the target class itself as the calibration signal is, as far as
the searches above surface, not established. And it generalizes far beyond
cycling — any archival traffic video with historical speed studies.

**Why it's tractable.** One scalar per camera in the simplest form. Validate by
holding out sites: calibrate on Site A's distribution, predict Site B's mean and
p85 speeds, compare to hand-timed truth.

**Risk.** Confounded if the speed distribution genuinely differs by site (it
does, somewhat). Mitigation: hierarchical model with a per-site random effect,
and report sensitivity.

### Idea B — Count-supervised calibration ("counts as labels") ★ strongest pairing

**Problem.** Your supervision is *aggregate* (15-min interval counts), not
per-frame boxes. The field's default response is to go label boxes.

**The idea.** Treat the interval counts as the *direct* training/calibration
signal. Learn the tracking hyperparameters — confidence threshold,
`min_track_hits`, motion gate, dedup IoU, line-crossing logic — by minimizing
count error against the hand counts, rather than hand-tuning them (which is what
you are doing now, and which produced the current bug). Formulate as a
calibration objective over interval counts, optimized with a derivative-free
method or a Bayesian/differentiable surrogate.

**Why this matters beyond your project.** Transportation agencies hold *decades*
of hand-collected interval count sheets sitting next to archival video. If those
count sheets can supervise a vision pipeline directly, an enormous latent
training corpus becomes usable without a single new bounding box. That framing
sells the paper to a transportation venue immediately.

**Bonus.** It makes the current bug part of the story: hand-tuned thresholds
catastrophically failed (zero cyclists at `min_track_hits=6`) while
count-supervised calibration recovers them. Your failure becomes Figure 1.

### Idea C — Unsupervised facility-zone induction

**Problem.** Assigning each cyclist to bike lane / sidewalk / travel lane
currently requires hand-drawn ROI polygons per camera. That does not scale to
16 sites × 40 sessions, and it is the hidden manual cost in every paper that
claims automated facility analysis.

**The idea.** Induce the facility polygons from the traffic itself. Accumulate
every trajectory (all classes) over hours; cluster in a feature space of
(lateral position, heading, speed, class mixture). The clusters *are* the
facilities: car-dominant + fast = travel lane; pedestrian-dominant + slow +
narrow = sidewalk; intermediate speed + bike-dominant + between the other two =
bike lane. Zero manual ROIs, and it self-adapts to camera moves between sessions.

**Validation — and this is the strong part.** Your ground truth is
facility-disaggregated. You can validate induced zones against hand-labeled
channel counts per facility, at 16 sites. Essentially nobody has facility-level
count ground truth to validate an unsupervised segmentation against. You do.

**Risk.** Sidewalk-vs-bike-lane separation may be weak where cyclists ride on the
sidewalk (which is precisely the behavior the study is about — your Sidewalk
counts dwarf Bike Lane counts at several sites). Handle it: that ambiguity is a
*finding*, not a failure. "Facility geometry is not recoverable from cyclist
behavior alone because cyclists systematically use the wrong facility" is a
publishable sentence.

### Idea D — Rare-event cascade (efficiency contribution)

Cyclists are ~0.001% of frames. Running a large tiled detector on all of it is
absurd. Propose a cascade: cheap background-subtraction/motion proposals →
tiled detector only on candidate regions → track. Report the compute reduction
and the recall cost. This is the least novel of the four, but it is the easiest
to demonstrate rigorously and it makes the full-dataset run actually feasible on
your Slurm allocation. Good as a secondary contribution or a systems section.

### Idea E — Rare-class association failure in multi-object tracking ★ new, and you have the data

**Discovered in your own pipeline (§1.1).** IoU-based association — the default
in the trackers most transportation-CV papers use off the shelf — fails
systematically for small vulnerable road users, while continuing to work on
vehicles in the same frames. On the BL Colonial clip it passed 3/12 links for a
cyclist and produced **zero** counted cyclists against 85 counted cars.

**Why it's a contribution, not just a bug report.** The failure is *silent and
class-selective*. A pipeline reporting plausible vehicle counts looks healthy;
nothing in its output reveals that the rare class has been zeroed. Any study
that reports cyclist counts from an IoU-associated tracker without per-class
validation may be under-reporting by an unknown factor. You can quantify that:
sweep the IoU threshold and show counted-cyclist yield vs. counted-car yield
diverging, then show the centroid formulation closing the gap. Two mechanisms
to separate and measure independently:

1. displacement-to-box-size ratio (scales with frame stride — sweep it), and
2. **box aspect instability**, which is the more interesting one: a
   bicycle/rider box flips between two valid interpretations frame to frame, so
   IoU drops even at near-zero displacement (your 407.74→407.90 link: 6.7 px of
   motion, IoU 0.287).

Mechanism 2 is not a tuning problem — no IoU threshold fixes it, because
lowering the gate enough to catch it admits false associations everywhere else.
That argues the metric itself is wrong for this class, which is a real claim.

**Validation.** Your facility-disaggregated hand counts let you measure the
resulting count error per class, per site — which is precisely the evidence a
reviewer would demand and almost nobody can supply.

### Suggested paper framing

> **Auditing cycling infrastructure from archival traffic video with
> count-supervised, self-calibrating vision.**
> Contributions: (1) count-level weak supervision for calibrating a
> detection–tracking pipeline, eliminating per-frame annotation;
> (2) distribution-matching self-calibration for speed estimation on cameras
> that no longer exist; (3) validation against 203 independent hand-collected,
> facility-disaggregated observations across 16 sites — a stronger protocol than
> the field's norm; (4) findings on sidewalk riding and day/night exposure risk.

---

## 5. Phased execution plan

Do not touch the full dataset. Work in tiers; each tier has a gate.

**Tier 0 — One clip, fully understood.** (target: days)
BL Colonial .008, the clip you already know. Gate: the pipeline tracks the
t≈408 s cyclist, and the reject-reason CSV explains every frame where it
doesn't. Nothing proceeds until this gate clears.

**Tier 1 — One session, count-validated.** (target: 1–2 weeks)
One full site-day against its hand counts, at 15-min resolution. Gate: count
error and a per-interval scatter plot vs. ground truth. Expect this to be bad
at first; that is the calibration signal for Idea B.

**Tier 2 — Three sites spanning facility types.** (target: 3–4 weeks)
Pick one bike-lane-heavy (Edgewater: BL With 146), one sidewalk-dominant
(Pine Hils NBL E: SW 168/143, almost no travel lane), one path
(Lakemont Pathway). Gate: fine-tuned model beats COCO baseline on held-out
sites; calibration transfers across sites.

**Tier 3 — All 16 sites.** Only after Tier 2's numbers are stable. This is the
paper's results table.

**Tier 4 — Goals 3–5.** Speed (Idea A), then near-miss, then demographics.

**On Goal 5 (age/gender):** think hard before including it. No ground truth
exists in your data for it, inferring demographics from surveillance video is an
ethics-review magnet, and it will attract reviewer hostility disproportionate to
what it adds. Recommendation: cut it, or reduce it to a short limitations
discussion of *why* it was cut. That is itself a defensible and increasingly
well-regarded position.

---

## 6. Things to fix in the write-up regardless

- `min_track_hits=6 ≈ 1s` in the session notes implies ~6 fps sampling. The
  continuity log ran at 30 fps. **Pin down the actual sampling rate and state it
  explicitly everywhere** — this ambiguity is probably the bug.
- Both consolidated spreadsheets have *different* tab-mislabeling shifts. Keep
  the two mapping tables strictly separate in code, with a unit test asserting a
  known site total (Alafaya West = 496) so a future edit can't silently
  reintroduce the swap.
- The 3 unparsed `Bicycles (2)` sheets — document as intentionally skipped with
  the reason, so it doesn't read as an unexplained gap in the methods section.
