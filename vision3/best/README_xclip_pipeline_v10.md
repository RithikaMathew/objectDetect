# X-CLIP overlay pipeline — session summary (updated through v10)

Goal: classify tracked people in `test.mp4` as BICYCLIST or PEDESTRIAN with
X-CLIP, count vehicles, and fix a string of detector/tracker problems along
the way. `test.mp4` ground truth: **1 pedestrian, 1 bicyclist**.

> The original `README_xclip_pipeline.md` is left untouched; this file is the
> updated version. New versions never overwrite old files (v7/v8 are copies).

## Version history (what each fixed, in order)

- **v2** (given) — YOLO detector + X-CLIP. YOLO never found the distant
  cyclist; a standing pedestrian kept getting new tracker ids.
- **v3** — switched to fine-tuned RT-DETR (`rtdetr_v3`), added an ID stitcher
  (a new track near a just-vanished person track inherits the old id), added
  `--veh-weights` for a separate vehicle detector. Problem: `rtdetr_v3`
  over-triggers "car" massively (22k+ raw car detections).
- **v4** — fine-tuned RT-DETR for people/cyclists + COCO `rtdetr-l.pt` for
  vehicles; static-object filter (`--veh-min-disp`). Problem: both detectors
  could box the same person -> id flicker; COCO called the cyclist
  "motorcycle".
- **v5** — cross-source NMS on person boxes; dropped "motorcycle"; vehicle
  must move roughly straight (`--veh-min-straightness`); bicyclist/pedestrian
  tally became **one vote per track** from the track's mean score.
- **v6** — header counter and final tally use the same running-mean logic;
  person table shows first–last frame; `--road-zone` polygon gate for
  vehicles (ground point = bottom-center of box); `extract_frame.py` to grab
  a still for picking polygon corners (Roboflow Polygon Zone,
  polygonzone.roboflow.com).
- **v7** — three polygons (road, bike lane, sidewalk). Vehicles must be in
  the road polygon and NOT in the sidewalk polygon; bike lane is drawn only.
  Polygons are drawn on the video and a `_zones_preview.png` is saved.
  `--zone-ref-size WxH` scales polygons picked on a different-size image
  (Roboflow canvas was 716x477) up to the real video size.
- **v8** — quality gates + track stats + zone JSON (see below).
- **v9** — containment NMS, box smoothing/coasting, only-counted vehicles drawn, `--veh-imgsz`.
- **v9b** — hotfix for v9: a variable named `nb` (number of bicyclist prompts) was overwritten by the drawing code, crashing X-CLIP scoring at the first person track. Renamed.
- **v10** (current) — see "v9b / v10 results and changes" below.

## v7 results (what you observed)

```
track | frames | scores | first-last frame | mean BICYCLIST | mean PEDESTRIAN | %det=cyclist | FINAL
    1 |    230 |     82 |       301-589    | 0.44 | 0.56 | 0%  | PEDESTRIAN
    2 |     99 |     40 |       435-803    | 0.50 | 0.50 | 10% | BICYCLIST
   12 |   2610 |    888 |      2690-5679   | 0.17 | 0.83 | 0%  | PEDESTRIAN
   13 |     18 |      5 |      4136-4150   | 0.04 | 0.96 | 0%  | PEDESTRIAN
   14 |     81 |     29 |      4821-4930   | 0.05 | 0.95 | 0%  | PEDESTRIAN
Final counts: bicyclists=1 pedestrians=4 vehicles=175   (truth: 1 / 1)
```

Reading of it:
- Big improvement: bicyclists 3 -> 1, and the header now matches the tally.
- Track 12 (2610 frames, 2690-5679) is the real standing pedestrian.
- Tracks 13 (18 frames) and 14 (81 frames, screenshot shows it on the
  sidewalk next to the cone) are false-positive person tracks; X-CLIP is
  confidently wrong on them (0.96/0.95 pedestrian), so it cannot be trusted
  to reject non-people — the filter has to happen before X-CLIP.
- Tracks 1 (301-589) and 2 (435-803) OVERLAP in time (435-589), so they are
  not one rider whose track broke and restarted — they were alive at the same
  time (likely the rider plus a duplicate/ghost box, or rider + something
  else). Both sit near 50/50, i.e. X-CLIP is unsure on the distant rider.
- Some vehicle detections are still the white road line.

## v8 changes

- **Person-track quality gates** (`--person-min-sec`, default 3.0 s;
  `--person-min-conf`, `--person-min-h`, default off). A person track is only
  drawn/counted if it persists long enough (and, if enabled, has high enough
  mean detector confidence and box size). This is the "must be seen across
  many frames, not once" filter. Filtered tracks appear in the table as
  `(filtered: ..., not counted)` instead of vanishing.
- **Vehicle quality gates**: per-detection box aspect ratio limits
  (`--veh-aspect-min/max`, 0.35–4.5) and per-track mean confidence
  (`--veh-min-mean-conf`, 0.45) on top of the existing displacement and
  straightness tests — aimed at thin, low-confidence "cars" like a lane line.
- **`<out>_track_stats.csv`**: per person track (frames, secs, mean conf,
  mean box height, scores, label, counted) and per vehicle track (frames,
  displacement, straightness, mean conf, counted). Use it to pick thresholds
  from real numbers instead of guessing.
- **Per-camera zone files** (`--zones-json`, e.g. `zones/camera_A.json`)
  holding `ref_size`, `road`, `bike`, `sidewalk`. Explicit `--road-zone` etc.
  flags still override. The slurm script takes `ZONES_JSON=...`.
- **Zone fill much more transparent** (`--zone-alpha`, default 0.07).


## v8 results

```
track | frames | secs | first-last | mean conf | mean box h | BICYC | PED | FINAL
    1 |    230 |  7.7 |    301-589 | 0.48 |  24 | 0.44 | 0.56 | PEDESTRIAN
    2 |     99 |  3.3 |    435-803 | 0.37 |  52 | 0.50 | 0.50 | BICYCLIST
   12 |   2610 | 87.1 |  2690-5679 | 0.58 |  87 | 0.17 | 0.83 | PEDESTRIAN
   13 |     18 |  0.6 |  4136-4150 | 0.32 |  27 | 0.04 | 0.96 | (filtered)
   14 |     81 |  2.7 |  4821-4930 | 0.37 |  25 | 0.05 | 0.95 | (filtered)
Final: bicyclists=1 pedestrians=2 vehicles=149   (truth 1 / 1)
```
- The 3 s minimum removed the cone tracks (13, 14). Vehicles 175 -> 149.
- Remaining extra pedestrian is track 1: almost certainly the SAME rider as
  track 2 seen earlier/farther (you saw "pedestrian first, then cyclist").
  The two tracks overlap in time (435-589). Likely cause: the fine-tuned
  "cyclist" box (rider+bike) and the COCO "person" box (rider only) had
  IoU < 0.4, so NMS kept both.
- Lane-marking boxes were drawn but not counted; two side-by-side cars got
  one box/id (the detector itself emitted one merged box); the cyclist box
  flickered on/off as the detector's confidence dipped.

## v9 changes

- Only vehicles that pass every filter (i.e. are counted) are drawn.
- `--person-contain 0.7`: a person box mostly inside a clearly larger person
  box is dropped before NMS (rider-only inside rider+bike) so one rider =
  one track.
- Person boxes are smoothed (`--box-ema`) and "coast" for up to `--coast-sec`
  (3 s) after the detector loses a confirmed track, moving on its last
  velocity, and stop when the box centre leaves the frame. Coasted frames do
  not feed X-CLIP or the counts.
- `--veh-imgsz` (env `VEH_IMGSZ`) to run the vehicle detector at a larger
  size; the attempt to split side-by-side cars. Not guaranteed — if it still
  merges them, the detector needs to change (bigger model / fine-tune).


## v9b results (what you observed)

```
    1 |    242 |  8.1 | 90 | 301-767 | plain 0.48/0.52 | PEDESTRIAN   <- the rider, not counted as bicyclist
    2 |     33 |  1.1 | filtered (cone)
    8 |   2599 | 86.7 | PEDESTRIAN (real pedestrian)
Final: bicyclists=0 pedestrians=2 vehicles=149
```
- Id 1 was the rider all along: labelled PEDESTRIAN 0.56 while tiny/far, later
  BICYCLIST 0.97. The plain mean over the whole track (0.48/0.52) called it a
  pedestrian, so bicyclists=0.
- The coasted box (moving on last velocity) drifted off the rider when he sped up.
- Cone tracks were still drawn for their first seconds (only excluded from counts).
- Two cars overlapping in view still got one box: the detector emits a single box.

## v10 changes

- **Box-height-weighted label** per track (`weighted mean`, weight = box height at
  each X-CLIP score): close/large crops count more than tiny far ones. The table
  prints plain mean, weighted mean and % of scores with bicyclist >= 0.9.
- **Optical-flow coasting**: when the detector drops a confirmed person, the box
  follows the rider with Lucas-Kanade flow (not blind extrapolation), up to
  `--coast-sec` (2 s), stopping if points are lost or it leaves the frame.
- **Two-pass render**: pass 1 detects/tracks/scores; pass 2 re-reads the video
  and draws only tracks that were finally counted (people and vehicles), from
  their first frame. Filtered junk (cone, lane markings) never appears.
- `overlay_scores.csv` now has a `box_h` column; `_track_stats.csv` has plain and
  weighted means.

## v10 results (final, current best)

```
    1 |  242 | 8.1  | 90  | 301-767   | plain 0.48/0.52 | wtd 0.55/0.45 | 6% bic>=.9 | BICYCLIST
    2 |   33 | 1.1  | filtered (was PEDESTRIAN, cone)
    8 | 2599 | 86.7 | 888 | 2690-5679 | plain 0.17/0.83 | wtd 0.16/0.84 | PEDESTRIAN
    9 |   18 | 0.6  | filtered
   10 |   81 | 2.7  | filtered
Final counts: bicyclists=1 pedestrians=1 vehicles=149   (truth: 1 / 1)
```
Matches ground truth for people. Caveat: the bicyclist call is thin
(weighted 0.55 vs 0.45; only 6% of scores >= 0.9), so it is sensitive to the
weighting rule. Vehicles: 149 (was 182 -> 175 -> 149); no ground truth for
vehicles yet.

## Open questions / next steps

- Bicyclist margin is narrow; on other videos consider an evidence-based rule
  (e.g. label bicyclist if a sustained stretch of high-confidence bicyclist
  scores exists) and check with `overlay_scores.csv`.
- Overlapping cars still get one box (detector limitation). Try a stronger
  vehicle detector via `--veh-weights` (e.g. `rtdetr-x.pt`, downloaded from a
  login node since the job runs with `HF_HUB_OFFLINE=1`). Video is only
  720x480, so `--veh-imgsz` larger than the source does not help.
- Zones are per fixed camera (`zones/camera_A.json`); new cameras need their
  own JSON or automatic segmentation.
- Vehicle count of 149 is unverified against a manual count.

## (older) Open questions / next steps

- v8 is untested on the cluster. Defaults are educated guesses: a 3 s
  minimum may not separate track 14 (81 frames ≈ 2.7–3.2 s depending on fps)
  from the real rider (track 2, 99 frames) — check `_track_stats.csv`
  (`mean_conf`, `mean_box_h`) for tracks 13/14 vs 1/2/12, then set
  `--person-min-conf` / `--person-min-h` from the gap between them.
- The distant rider scores ~50/50 for bicyclist vs pedestrian; the detector
  rarely says "cyclist" (0–10% of frames). That is a detector-training and
  X-CLIP-on-tiny-crops limitation, not something filters fix.
- Zone scaling: confirm `_zones_preview.png` lines up with road/bike
  lane/sidewalk; if not, `ref_size` in the JSON is wrong.
- Zones are per fixed camera. A new camera needs its own JSON (or automatic
  segmentation — see chat notes). Moving/PTZ cameras break the zone approach.

## Weights inventory

- Fine-tuned RT-DETR:
  - `/orange/xiangyan/rithika/vision/vision3/runs/detect/finetune_runs/rtdetr_v3/weights/best.pt`
  - `/orange/xiangyan/rithika/vision/vision3/finetune_runs/rtdetr_v2_overtriggers/weights/best.pt`
    (heavy false-positive "car")
  - No `rtdetr_v1` weights exist on disk.
- COCO pretrained: `/orange/xiangyan/rithika/vision/vision3/weights/rtdetr-l.pt`

## Files (in /mnt/user-data/outputs/)

- `xclip_overlay_v3.py` … `xclip_overlay_v7.py` with matching
  `run_xclip_overlay_v*.slurm` (all preserved)
- `xclip_overlay_v8.py` / `run_xclip_overlay_v8.slurm`
- `xclip_overlay_v9.py` / `run_xclip_overlay_v9.slurm` (has the `nb` bug — use v9b or later)
- `xclip_overlay_v9b.py` / `run_xclip_overlay_v9b.slurm`
- `xclip_overlay_v10.py` / `run_xclip_overlay_v10.slurm` — **current**
- `zones/camera_A.json` — polygons for `test.mp4`'s camera
- `extract_frame.py` — grab a still frame for picking polygon corners

## How to run v10

```bash
cd /orange/xiangyan/rithika/vision/vision3
mkdir -p logs zones   # copy zones/camera_A.json next to the script
sbatch --export=ALL,WEIGHTS=/orange/xiangyan/rithika/vision/vision3/runs/detect/finetune_runs/rtdetr_v3/weights/best.pt,VEH_WEIGHTS=/orange/xiangyan/rithika/vision/vision3/weights/rtdetr-l.pt,OUT=pilot_output/compare_v4/xclip_overlay_v10/overlay.mp4 run_xclip_overlay_v10.slurm
```

Different camera: `ZONES_JSON=zones/camera_B.json`. Slurm account/qos are
`xiangyan`/`xiangyan`.

Note: use full paths (an empty `$FR` once produced `/runs/detect/...`). Nothing has been run by Claude itself — all fixes are based on the logs and
screenshots you pasted back, untested against your real video/weights.
