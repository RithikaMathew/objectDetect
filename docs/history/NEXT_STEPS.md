# Next Steps — exact commands

Companion to `METHODOLOGY.md`. Everything here is copy-pasteable.

---

## 1. Upload the new files to HiPerGator

Run this **on your Mac**, in Terminal:

```bash
cd /Users/rithika/Desktop/vision2

scp vru_tracker.py pilot_detect_v2.py tracker_ablation.py \
    run_ablation.slurm run_v2_window.slurm run_v2_full.slurm \
    rmathew1@hpg.rc.ufl.edu:/orange/xiangyan/rithika/vision/
```

---

## 2. Run the fix (on HiPerGator)

```bash
ssh rmathew1@hpg.rc.ufl.edu
cd /orange/xiangyan/rithika/vision
```

**Never run YOLO on the login node.** Everything below goes through `sbatch`.
(This is what killed your earlier session — the login node has no GPU and gets
your process reaped.)

### 2a. Prove the fix works (~10 min)

```bash
sbatch run_ablation.slurm
```

Watch it:

```bash
squeue -u rmathew1
```

When it disappears from the queue, read the result:

```bash
ls -t ablation_*.log | head -1 | xargs cat
```

**What you should see:** `IoU >= 0.3` passing roughly 3/12 links and
`norm. centroid <= 1.0` passing 12/12, with `OLD IoU tracker -> NOT COUNTED` and
`NEW centroid -> COUNTED`.

If the new tracker says NOT COUNTED, something else is wrong — send me that log.

### 2b. Make a video you can actually watch (~10 min)

```bash
sbatch run_v2_window.slurm
squeue -u rmathew1
```

This renders **t=400–420 s at full 30 fps** with boxes, track IDs and
trajectory trails. Then, **on your Mac**:

```bash
scp 'rmathew1@hpg.rc.ufl.edu:/orange/xiangyan/rithika/vision/pilot_output/v2/*_window_*_annotated.mp4' ~/Desktop/
open ~/Desktop/*_window_400_420_annotated.mp4
```

The cyclist should carry **one stable `#id bicycle`** label with a trail behind
it, from about t=407 to t=409.5.

### 2c. Full 45-minute chunk (~2–4 h)

```bash
sbatch run_v2_full.slurm
```

Outputs into `pilot_output/v2/`:

| File | What it is |
|---|---|
| `*_funnel.csv` | Per-frame survivor counts at every pipeline stage |
| `*_tracks.csv` | Every track: hits, duration, confidence, displacement, counted y/n |
| `*_annotated.mp4` | Full annotated video |

Quick look at what got counted:

```bash
cd /orange/xiangyan/rithika/vision/pilot_output/v2
awk -F, '$2=="bicycle"' *_tracks.csv | head -40
awk -F, '$11=="yes"{c[$2]++} END{for(k in c) print k, c[k]}' *_tracks.csv
```

### Tuning knobs, if needed

```bash
# Looser association (use if one cyclist fragments into several tracks)
python pilot_detect_v2.py "$CLIP" 600 --center-dist 1.5

# Denser sampling — the real fix for fast objects
python pilot_detect_v2.py "$CLIP" 600 --stride 2

# Compare YOLO26 against v8l on identical settings
python pilot_detect_v2.py "$CLIP" 600 --weights yolo26l.pt
```

---

## 3. Your ROI question — yes, and it already does

`ROI_POLYGON_FRAC` is set to all four corners, i.e. the **entire frame**. The
filter is a no-op today and nothing is being cropped out. That's correct and I
kept it that way in v2.

Keep it full-frame. The temptation is to draw a polygon around "the bike lane,"
but that would destroy the study: **your own ground truth shows cyclists ride on
sidewalks far more than in bike lanes** (Pine Hils NBL E: 168+143 sidewalk vs. 6+10
travel lane). Where cyclists ride is the measurement, so it cannot be an input
assumption. Narrow the ROI only if one camera has a persistent false-positive
source you can't otherwise suppress.

---

## 4. Your fine-tuning approach — it's good, keep it

I read `MioVision Pilot Dataset — Zip Structure & Extraction Methodology.md`.
Three things in it are already right, and they're the things people usually get
wrong:

- **Site-based splitting, with a programmatic check** that no site appears on
  both sides. This is the single most common fatal flaw in this literature and
  you've already handled it.
- **Val gets the uniform pass only.** Mining into val would inflate your numbers
  with frames the model already handles. Correct call, correctly reasoned.
- **Per-site quotas** so one busy intersection can't consume a class's whole
  global budget.

That's a better starting point than I assumed. Four specific changes:

### 4.1 Lower `--frame-conf` from 0.5 to ~0.15 for the mining pass

At 0.5 you mine only frames the model **already gets right**, so fine-tuning
teaches it mostly what it knows. The valuable training frames are the ones it
currently gets *wrong* — the 0.07 and 0.09-confidence cyclists in your log. Those
are invisible at 0.5.

This matters more than it sounds: at conf 0.5, your bicycle class fills its
1000-instance quota with easy, large, well-lit cyclists, and the fine-tuned
model stays bad at exactly the hard cases that made you lose count.

### 4.2 Add a third sampling pass: ground-truth-guided mining

Your hand counts say which 15-min windows at which sites contain cyclists. Mine
those windows at a *very* low confidence (0.05) with no quota. This is the
highest-value annotation time you can possibly spend, and it's an advantage
essentially no one else in this literature has. (Methods subsection in its own
right — see `METHODOLOGY.md` §3.2.)

### 4.3 Merge `person` + `bicycle` into one `cyclist` class

Your `classes.txt` is `person, bicycle, car, motorcycle, bus, truck`. The
problem: a cyclist produces a `person` box AND a `bicycle` box, and your ground
truth counts **one cyclist**. Every count needs a fusion heuristic, and that
heuristic is a permanent error source. Worse, in the logged window the tracker's
class flips between the two.

Add a 7th class `cyclist` (person visibly riding a bicycle), and keep `person`
for pedestrians only. Annotators find this easy to judge, and it removes a whole
failure mode from the pipeline. Where a bicycle is parked with no rider, it
stays `bicycle`.

### 4.4 Train on tiles, not full frames

You run tiled inference (2×2, 20% overlap) but fine-tune on full frames. The
model never sees a cyclist at the scale a tile actually presents. Slice your
training images with the **same geometry** as `compute_tiles()`. The SAHI paper
reports +12–14 AP cumulative for fixing exactly this mismatch — likely the
largest single win available to you, and it's nearly free.

---

## 5. Annotation: exactly what to do, with free tools

### 5.1 Do NOT annotate the whole dataset

Your instinct is right and this is the most important answer here.

You have ~139 sites × many hours. **You will annotate a few thousand frames,
not all of them.** Concretely: target **1,500–3,000 images total**, ~10–20%
of them containing cyclists. That is enough to fine-tune YOLO well, and it's
2–4 weeks of part-time annotation, not a year.

**The train/val/test split applies to the annotated subset only.** The full
dataset is used for *inference* (running the finished model to produce counts),
which needs no labels at all — you validate those counts against the hand counts
you already have. The two things are separate:

| Purpose | How much data | Labels needed? |
|---|---|---|
| Fine-tuning the detector | ~2,000 frames from ~10 sites | Yes, hand-corrected |
| Producing the paper's counts | All 40 corridor sessions | **No** — validated against Excel ground truth |

This is why the count-supervised framing (Idea B) is so valuable: the expensive
thing (boxes) stays small, and the cheap thing (existing hand counts) does the
heavy validation.

### 5.2 Recommended free stack

| Job | Tool | Cost |
|---|---|---|
| Annotation UI | **CVAT** (`app.cvat.ai`) | Free tier, no card |
| Dataset curation | **FiftyOne** (`pip install fiftyone`) | Free, open source |
| Sliced training | **SAHI** (`pip install sahi`) | Free |

Roboflow's free tier caps public projects at 10,000 images and makes your data
**publicly visible** — check whether your MioVision data license permits that
before uploading. CVAT has no such condition and does box interpolation across
video frames, which Roboflow's free tier does not. That interpolation is worth
more to you than anything else in the comparison.

### 5.3 CVAT walkthrough — start to finish

**Step 1 — account.** Go to `app.cvat.ai`, sign up free.

**Step 2 — get frames onto your Mac.** Your `extract_frames.py` already produces
`dataset_frames/split/train/images` with pre-filled YOLO labels. Pull them down:

```bash
scp -r 'rmathew1@hpg.rc.ufl.edu:/orange/xiangyan/rithika/vision/dataset_frames/split' ~/Desktop/annotate/
```

**Step 3 — create the task.** In CVAT: *Projects → + → Create new project*.
Name it `miovision-vru`. Add labels, exactly these, as rectangles:

```
cyclist        (person riding a bicycle -- ONE box around rider+bike)
pedestrian
bicycle        (parked/unridden bicycle only)
car
motorcycle
bus
truck
```

Then *+ → Create new task*, select the project, upload your images.

**Step 4 — upload your pre-filled boxes** so you're correcting, not drawing.
In the task menu: *Actions → Upload annotations → YOLO 1.1*, and give it a zip
of your `labels/` folder plus `classes.txt` ordered to match the label list
above. If the class order doesn't line up, CVAT will map them wrong — verify on
a handful of frames before doing anything else.

**Step 5 — annotate.** Keys worth knowing: `N` new box, `F` next frame,
`D` previous, `Ctrl+S` save. Rules to hold to:

- Box the **whole** cyclist: rider and bike as one rectangle.
- Box every cyclist you can see, including tiny and partly occluded ones. Small
  hard examples are the entire point — skipping them teaches the model to skip
  them too.
- If you genuinely cannot tell whether something is a cyclist, mark the frame
  with a tag and move on. Don't guess; ambiguous labels are worse than missing ones.
- Be consistent above all. A consistent wrong convention beats an inconsistent
  right one.

**Step 6 — export.** *Actions → Export task dataset → YOLOv8*. You get
`images/` + `labels/` + `data.yaml`.

### 5.4 Making the train/val/test split

**Do not use a random split.** Split by site. Your `build_dataset.slurm` already
separates sites at extraction time, so the cleanest approach is to keep three
separate CVAT tasks — one per split — and never mix them.

Target layout:

```
dataset/
├── train/images/  train/labels/     ~10 sites
├── val/images/    val/labels/       ~3 sites   (tuning)
└── test/images/   test/labels/      ~3 sites   (touch ONCE, at the very end)
```

`data.yaml`:

```yaml
path: /orange/xiangyan/rithika/vision/dataset
train: train/images
val: val/images
test: test/images
names:
  0: cyclist
  1: pedestrian
  2: bicycle
  3: car
  4: motorcycle
  5: bus
  6: truck
```

Pick test sites to span facility types — at minimum one bike-lane site
(Edgewater), one sidewalk-dominant (Pine Hils NBL E), one path (Lakemont
Pathway) — and include a night-heavy site if you can.

**Verify no site leaks across splits before training:**

```bash
cd /orange/xiangyan/rithika/vision/dataset
for s in train val test; do ls $s/images | sed 's/_[0-9]*_.*//' | sort -u > /tmp/$s.txt; done
comm -12 /tmp/train.txt /tmp/val.txt    # must print nothing
comm -12 /tmp/train.txt /tmp/test.txt   # must print nothing
```

If either prints a site name, your validation numbers are inflated. Fix it
before you train, not after.

### 5.5 Training

```bash
# on HiPerGator, via sbatch
yolo detect train data=dataset/data.yaml model=yolov8l.pt \
     epochs=100 imgsz=640 batch=16 patience=20 \
     project=runs/finetune name=v1
```

`imgsz=640` here, not 1280, because you're training on **tiles** — each tile is
already a crop, so it doesn't need the full-frame resolution.

---

## 6. Do the same sites recur across years?

**Both — and the overlap is a research opportunity you should not miss.**

Reading the site tree, these names appear in more than one year:

| Site | Years |
|---|---|
| SOBT | 2022, 2023, 2024 |
| EE Williamson | 2021, 2024 |
| Sunset Dr | 2021, 2024 |
| Fortune Road | 2021, 2026 |
| South St | 2021, 2023 |
| Church Ave | 2021, 2023 |
| Division / Division Ave | 2021, 2023 |
| Anderson St / Anderson | 2021, 2023 |
| W Colonial | 2022, 2025 |
| Shingle Creek | 2022, 2025 |

Plus several **2019 Bike Lane Study sites re-recorded later** under renamed
folders: `BL Edgewater` (2019) → `Edgewater Dr` (2025); `NBL University` (2019)
→ `University East/West` (2025); `Rinehart Road Path` (2019) → `Rinehart`
(2025); `NBL Curry Ford` (2019) → `Curry Ford N/S` (2022); `BL Livingston`
(2019) → `Livingston` (2022); Pine Hills and Aloma variants across 2019/2023/2025.

**Why this matters:** if any of those are genuinely the same camera position,
you have **before/after pairs spanning up to 7 years** at locations where
infrastructure changed. Paired with your 2019 hand counts as the "before"
baseline, that supports a longitudinal claim — *"cyclist volume and facility
choice at site X after the bike lane was installed"* — which is considerably
more interesting to a transportation journal than any single-year count.

**Caveat: matching folder names do not prove matching camera placement.**
Verify before claiming anything. Compare thumbnails:

```bash
cd "/orange/xiangyan/rithika/vision/pilot_clips/MioVision Data"
find . -iname "*edgewater*" -name "*.jpg" | head -20
```

Pull a few down and eyeball whether it's the same viewpoint:

```bash
scp 'rmathew1@hpg.rc.ufl.edu:/orange/.../BL*Edgewater*/*.001.jpg' ~/Desktop/check/
```

---

## 7. Should you focus purely on detection accuracy now?

**Mostly yes — but be careful what you measure, because detection accuracy was
never the problem here.**

Your detector produced a **0.92-confidence** cyclist and the pipeline still
counted zero. Optimizing mAP would not have surfaced that; only an end-to-end
count comparison did. So:

**Primary metric: count error against your hand counts**, per site, per 15-min
interval. That is what the paper reports and what catches whole-pipeline
failures.

**Secondary metric: detection mAP** on the held-out sites, to guide fine-tuning
choices.

Order of work:

1. ✅ Tracker fixed — verify with §2a and §2b.
2. Run a full site-day, compare against ground truth at 15-min resolution (Tier 1).
3. *Then* fine-tune, using the count errors from step 2 to decide what to mine.

Step 2 before step 3 matters: it tells you where to spend annotation effort
instead of guessing.

---

## 8. What I found in the files you just added

### 8.1 Video↔ground-truth mapping is now built ✅

```bash
python3 build_site_mapping.py          # writes video_site_mapping.csv
```

**41/41 site-sessions matched, 0 unmatched, 0 ambiguous.** Joins on session
date, disambiguates same-date pairs by facility token. This was the blocker for
Tier 1 count validation; it's gone.

### 8.2 The study is a matched-pair design — this is the biggest finding

Every date deployed **two cameras at once: one BL (bike lane) site, one NBL (no
bike lane) control.** 17 such pairs. Weather, season, day-of-week and
time-of-year are controlled by construction. See `METHODOLOGY.md` §0.1 — this
should be the framing of the paper, and it also settles the old open question
about which files are two-camera-same-session pairs.

### 8.3 Your ground truth had an empty column — fixed

`facility_type` and `movement` were **empty in 202/202 rows**, despite
`bike_lane_study_excel_findings.md` documenting them as populated. The split
that was supposed to fill them never wrote a value.

```bash
cd "Bike Lane Study Counts"
python3 fix_ground_truth.py            # writes ground_truth_bicycle_counts_v2.csv
```

Recovers both from `channel_label`, verified against all three hand-checked
totals (Alafaya East 245, West 251, University South 248, East+West 496 ✓).

**The result is a headline finding: 63% of your 5,053 cyclists ride on
sidewalks** — 3,160 sidewalk vs 1,125 bike lane vs 531 path vs 237 travel lane.
Use `_v2.csv` from here on.

26 rows are `movement: undetermined` — `Path` and bare `Sidewalk` channels carry
no side designation, so With/Facing isn't derivable. Flagged rather than guessed;
a wrong value there would corrupt any wrong-way-riding analysis.

### 8.4 P0: the 15-minute interval data was discarded

`parse_raw_counts.py` calls `find_total_row()` and keeps only that row — the
15-minute interval rows underneath are dropped. Your ground truth is therefore
**daily totals per channel, with no time-of-day resolution.**

That blocks two things you need:

- **Per-interval count validation** — Tier 1's gate is "count error at 15-min
  resolution," which is currently impossible. A daily total can be right for the
  wrong reasons (misses at 8am cancelling false positives at 5pm); interval-level
  comparison is what makes the validation credible.
- **Ground-truth-guided mining** (§4.2) — needs to know *which windows* contain
  cyclists, which is the whole point.

The data exists in the raw `.xls` files (and in `Bike lane study counts.xlsx`).
It needs re-extraction: modify `parse_raw_counts.py` to emit every interval row
between `data_start` and the total row, keeping the timestamp column, rather
than only the total. Send me `parse_raw_counts.py`'s output on one file plus a
couple of raw `.xls` files and I'll write it.

**Do this before the fine-tuning work** — it determines which frames are worth
annotating, so doing it after means annotating the wrong frames.

### 8.5 Two smaller notes

- `Pine Hills BL E` (2019-08-28) has only **25 mp4 chunks** where every other
  session has 48. Possibly a truncated recording — check before relying on that
  session's 137 counts for validation.
- `Rinehart Road SW` has 96 chunks (two sessions under one folder). Fine, just
  be aware when selecting a time window.

---

## 9. Files I'd still like from HiPerGator

```bash
cd /orange/xiangyan/rithika/vision
tar czf for_review.tar.gz \
    extract_frames.py build_dataset.slurm \
    "Bike Lane Study Counts/parse_raw_counts.py" \
    pilot_detect_yolo26.py debug_frame.py pull_site_samples.sh all_videos.txt
```

Then on your Mac:

```bash
scp rmathew1@hpg.rc.ufl.edu:/orange/xiangyan/rithika/vision/for_review.tar.gz ~/Desktop/vision2/
cd ~/Desktop/vision2 && tar xzf for_review.tar.gz
```

Most useful: **`extract_frames.py`** (so I can wire in §4.1–4.3 — the conf
threshold, the ground-truth-guided pass, and the `cyclist` class) and
**`build_dataset.slurm`**.

Also useful — the mapping from video files to ground-truth sites, which nothing
in the repo currently records:

```bash
cd /orange/xiangyan/rithika/vision
find "pilot_clips/MioVision Data/Bike Lane Study" -name "*.mp4" \
  | sed 's|.*/MioVision Video/||' | cut -d/ -f1 | sort | uniq -c | sort -rn
```

That tells us which of the 34 Bike Lane Study video folders line up with the 16
sites in `ground_truth_bicycle_counts.csv` — needed before any Tier 1
count validation can run.
