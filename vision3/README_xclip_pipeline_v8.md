# X-CLIP overlay pipeline — session summary (updated through v8)

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
- **v8** (current) — see below.

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

## Open questions / next steps

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
- `xclip_overlay_v8.py` / `run_xclip_overlay_v8.slurm` — **current**
- `zones/camera_A.json` — polygons for `test.mp4`'s camera
- `extract_frame.py` — grab a still frame for picking polygon corners

## How to run v8

```bash
FR=/orange/xiangyan/rithika/vision/vision3
mkdir -p logs zones   # copy zones/camera_A.json next to the script
sbatch --export=ALL,WEIGHTS=$FR/runs/detect/finetune_runs/rtdetr_v3/weights/best.pt,VEH_WEIGHTS=$FR/weights/rtdetr-l.pt,OUT=pilot_output/compare_v4/xclip_overlay_v8/overlay.mp4 run_xclip_overlay_v8.slurm
```

Different camera: `ZONES_JSON=zones/camera_B.json`. Slurm account/qos are
`xiangyan`/`xiangyan`.

Nothing past v2 has been run by Claude — all fixes are based on the logs and
screenshots you pasted back, untested against your real video/weights.
