---
title: MioVision Pilot Dataset — Zip Structure & Extraction Methodology

---

# MioVision Pilot Dataset — Zip Structure & Extraction Methodology

## 1. What's in `MioVision_Data.zip`

The archive is organized **by year, then by site (intersection/camera location), then
by recording session**. A recording session folder (e.g.
`Standard_SCU8PM_2021-04-13_0000/`) doesn't hold one video file — it holds many
small **hourly `.mp4` chunks**, each paired with a `.cut` marker and a `.jpg`
thumbnail:

```
MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/Standard_SCU8OG_2019-07-10_0000/
├── Standard_SCU8OG_2019-07-10_0000.001.mp4   (05:00 hour)
├── Standard_SCU8OG_2019-07-10_0000.001.jpg
├── Standard_SCU8OG_2019-07-10_0000.001.cut
├── Standard_SCU8OG_2019-07-10_0000.002.mp4   (06:00 hour)
├── Standard_SCU8OG_2019-07-10_0000.002.jpg
├── Standard_SCU8OG_2019-07-10_0000.002.cut
└── ... (one .mp4/.jpg/.cut triplet per hour of footage)
```

This is why the extraction pipeline treats **site**, not individual `.mp4` file, as
the unit of "one video" for fairness/quota purposes — a single site like `BL
Colonial` can expand to dozens of chunk files across multiple dated sessions.

### Site counts by year / category

| Group | Distinct sites | Years covered |
|---|---|---|
| 2021 Data | 26 | 2021 |
| 2022 Data | 24 | 2021–2022 |
| 2023 Data | 22 | 2023 |
| 2024 Data | 12 | 2024 |
| 2025 Data | 17 | 2025 |
| 2026 Data | 4 | 2026 |
| Bike Lane Study / MioVision Video | 34 | 2019 |
| Other | 2 (SunRail, SunRail Longwood) | 2020, 2023 |

**~139 distinct camera sites** total across the archive, each with one or more
dated recording sessions, each session chunked into hourly `.mp4` files.

### Full directory tree

```
MioVision Data/
├── 2021 Data/                          (26 sites)
│   ├── Anderson St/
│   │   └── Standard_SCU8PM_2021-04-13_0000/
│   ├── Celery Ave/
│   │   └── Standard_SCU8OG_2021-04-06_0000/
│   ├── Central Blvd/
│   │   └── Standard_SCU8PM_2021-05-25_0000/
│   ├── Central North/
│   │   ├── Standard_SCU8PM_2021-04-27_0000/
│   │   └── Standard_SCU8PM_2021-04-27_0000.02/
│   ├── Central South/
│   │   └── Standard_SCU8OG_2021-04-27_0000/
│   ├── Church Ave/                     <- used in current TRAIN split
│   │   └── Standard_SCU8PM_2021-03-23_0000/
│   ├── Clarcona-Ocoee/
│   │   ├── Standard_SCU8OG_2021-02-09_0000/
│   │   └── Standard_SCU8PM_2021-02-09_0000/
│   ├── Corrine/
│   │   ├── North Side Facing West Bound Traffic/
│   │   │   └── Standard_SCU8OG_2021-03-10_0000/
│   │   └── South Side Facing East Bound Traffic/
│   │       └── Standard_SCU8PM_2021-03-10_0000/
│   ├── Denning Path/ ... Dillard/ ... Division/ ... EE Williamson/ ...
│   ├── Fortune Road/ ... Gore/ ... Little Econ Trail/ ... NOBT CS/ ...
│   ├── Orange Blvd/ ... Pine St/ ... Princeton Packing District/ ...
│   ├── Robinson/ ... Sligh/ ... South St/ ... Sunset Dr/ ... US 192/ ...
│   └── Virginia (East of Mills)/ ... Virginia (West of Mills)/
│
├── 2022 Data/                          (24 sites)
│   ├── Conway Rd/ ... Corrine Pop-Up/ ...
│   ├── Curry Ford/
│   │   ├── North/                      <- used in current TRAIN split
│   │   │   └── Standard_SCU8OG_2022-05-17_0000/
│   │   └── South/
│   │       └── Standard_SCU8PM_2022-05-17_0000/
│   ├── Emory Path/ ... George Ave & US 17-92/ ... Goldsboro Path/ ...
│   ├── Lake Fran Trail/ ... Livingston/ ... Maitland Ave Crossing/ ...
│   ├── Maitland SunRail Station/ ... Neptune Road Path/ ...
│   ├── Neptune SunRail/ ... New folder/ ... Packwood Crossing/ ...
│   ├── Riverwalk/ ... Sandspur & Maitland Ave/ ...
│   ├── Shingle Creek MetroWest/ ... Shingle Creek S Orange/ ...
│   ├── Silver Star/ (North Side, South Side) ... SOBT/ ... SR 436/ ...
│   └── W Colonial/ ... Washington St/ ... Westmoreland Path/
│
├── 2023 Data/                          (22 sites)
│   ├── 10th St/ ... Aloma East/ ... Aloma West/ ... Anderson/ ...
│   ├── Buenaventura/ ... Church Ave/ ... Church St/ ... Cross Seminole/ ...
│   ├── Division Ave/ ... E Colonial/ ... E Silver Star/ ... Kirkman/ ...
│   ├── Maitland Interchange Overpass/ ... Mercy/ ... N Orange/ ...
│   ├── Pine Hills Trail/ (Balboa, Indialantic) ... Powers/ ...
│   ├── Seminole Wekiva/ ... Slavia Road/ ... SOBT/ ... South St/ ...
│   └── West Orange Trail/
│
├── 2024 Data/                          (12 sites)
│   ├── EE Williamson/ ... Fern Creek North/ ... Fern Creek South/ ...
│   ├── Ivey Lane/ ... Keller Road/ ... North St/ ... Rio Grande/ ...
│   ├── SOBT/ ... Spring Lake Path/ ... St Andrews/ ... Sunset Dr/ ...
│   └── US 17-92 Fern Park/
│
├── 2025 Data/                          (17 sites)
│   ├── Corrine Dr/                     <- used in current VAL split (held out)
│   │   ├── MIOP000706_2025_03_12-0000/
│   │   └── MIOP000856_2025_03_12-0000/
│   ├── Denning/ ... Edgewater Dr/ ...
│   ├── Kissimmee Trail at Hoagland/ ... North St E/ ...
│   ├── Orlando Urban Trail/ ... Pine Hills Center/ ... Pine Hills North/ ...
│   ├── Rinehart/ ... Rock Springs Rd/ ...
│   ├── S Semoran/ (East, West) ... Semoran Separated/ ...
│   ├── Shingle Creek/ (At Destination Pkwy, At Oak Ridge) ...
│   ├── University East/ ... University West/ ...
│   └── US 17-92/ ... W Colonial/
│
├── 2026 Data/                          (4 sites)
│   ├── Casselberry Connector/ ... Fortune Road/ ...
│   └── Lake Apopka Connector/ ... Winter Park Dr/
│
├── Bike Lane Study/MioVision Video/    (34 sites, all 2019)
│   ├── Aloma Path/ ... Aloma SW/ ... BL Alafaya/ ...
│   ├── BL Colonial/                    <- used in current TRAIN split
│   │   ├── Standard_SCU8OG_2019-07-10_0000/
│   │   └── Standard_SCU8OG_2019-07-16_0000/
│   ├── BL Columbia/ ... BL Edgewater/ ... BL Glenridge/ ... BL Lakemont/ ...
│   ├── BL Livingston/ ... BL Par/ ... BL Pine Hills/ ... BL S Orange/ ...
│   ├── BL Speed Edgewater/ ... Daniels Path/ ... Daniels SW/ ...
│   ├── NBL Carroll/ ... NBL Clay/ ... NBL Curry Ford/ ... NBL Kaley/ ...
│   ├── NBL Lee Road/ ... NBL N Orange/ ... NBL Pine Hills/ ...
│   ├── NBL Summerlin/ ...
│   ├── NBL University/                 <- used in current TRAIN split
│   │   ├── Standard_SCU8OG_2019-04-24_0000/
│   │   └── Standard_SCU8PM_2019-04-17_0000/
│   ├── NBL Winter Park Road/ ... New folder/ ... Pleasant Hill Path/ ...
│   ├── Rinehart Road Path/ ... Rinehart Road SW/ ... SW Speed University/ ...
│   ├── TL Speed Baxter/ ... TL Speed Winter Park/ ...
│   └── WORT Path/ ... WORT Sidewalk/
│
├── Other/
│   ├── SunRail/Standard_SCU8PM_2020-10-20_1200/
│   └── SunRail Longwood/ (Longwood SunRail Upload/, 2023 sessions)
│
└── Temp/                               (empty)
```

*(Sites currently wired into `build_dataset.slurm` are flagged inline. The
remaining ~130 sites are unused — a large reserve for later expansion, or for
constructing a proper held-out **test** set at a later stage, kept separate from
the train/val split described below.)*

---

## 2. Current extraction methodology

### 2.1 Site-based train/val split

Videos are split **by site, never by frame**. Every chunk belonging to a site
goes entirely to one side of the split:

| Split | Sites | Why |
|---|---|---|
| **Train** | Anderson St (2021), Church Ave (2021), Curry Ford North (2022), BL Colonial (2019), NBL University (2019) | 5 sites, mixed years/cameras for variety |
| **Val** | Corrine Dr (2025) | Newest camera hardware, never touched during training |

Splitting by site (not by frame) matters because frames a few seconds apart from
the same camera/hour are near-duplicates — letting them land on both sides of the
split would leak information and inflate validation performance. `cmd_build`
refuses to run if any site path appears in both `--train-videos-dir` and
`--val-videos-dir`.

A separate **test set**, at a different location entirely, is being kept out of
this pipeline and isn't touched by any of the ~139 sites above.

### 2.2 Two sampling passes (train only gets both)

| Pass | Applies to | Trigger | Purpose |
|---|---|---|---|
| **Uniform** | Train + Val | Every `--uniform-interval` seconds (default 15s), frame kept regardless of detections | Unbiased background/lighting/traffic variety, plus true negatives. The *only* sampling used for val, so validation performance isn't inflated by cherry-picking easy frames. |
| **Confidence-gated mining** | Train only | Every `--mine-interval` seconds (default 2s), frame kept only if a detection reaches `--frame-conf` (default 0.5) | Efficiently bootstraps pre-filled YOLO boxes for Roboflow, so you're correcting boxes instead of drawing every one from scratch. Never used for val — it would select for frames the model already handles well, inflating apparent performance. |

### 2.3 Per-class instance quotas (mining pass only)

On top of the confidence gate, the mining pass enforces two caps per class:

- **Global cap** — total instances across the whole train mining pass.
- **Per-site cap** — `ceil(global_cap / num_train_sites)`, so no single busy site
  (e.g. one intersection's dozens of hourly chunks) can consume an entire class's
  global quota while other sites contribute nothing.

A frame is kept if **at least one** of its detected classes still has room under
both caps; once kept, *every* box in that frame counts (quotas gate whole frames,
not individual boxes — so totals can slightly overshoot within one frame).

Current defaults (5 train sites → per-site share is global ÷ 5):

| Class | Global cap | Per-site share |
|---|---|---|
| car | 3000 | 600 |
| truck | 1500 | 300 |
| bus | 1000 | 200 |
| bicycle | 1000 | 200 |
| person | 1000 | 200 |
| motorcycle | unlimited | — |

These caps are **minimums to reach, not exact targets** — a quiet site that never
sees a bus won't be backfilled by a busier one; the global cap may end up
under-filled for that class.

### 2.4 Output layout

```
dataset_frames/split/
├── train/
│   ├── images/    <site>_<year>_<video_tag>_{uniform,mined}_t<seconds>s.jpg
│   ├── labels/     ... .txt   (YOLO format, pre-filled boxes)
│   ├── previews/   ... .jpg   (boxes drawn in, for quick visual QA)
│   └── classes.txt
└── val/
    ├── images/ (uniform pass only)
    ├── labels/
    ├── previews/
    └── classes.txt
```

`classes.txt` / label indices: `person, bicycle, car, motorcycle, bus, truck`
(compact 0–5 range, remapped from COCO indices for a clean Roboflow project).
