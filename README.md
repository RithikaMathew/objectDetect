# Object detection study — start here

**Latest requested experiment:** [adaptive15-minute bicycle speed comparison](docs/SPEED_REFERENCE_README.md#latest-run-adaptive15-minute-bicycle-speed-comparison). It processes consecutive15-minute windows until each site reaches its sample target, capped at60minutes/site. Colonial North included;13candidate locations. Each site publishes its own results after every completed segment and on failure. Prepared, not run.

[Video duration guide—source-file counts, confirmed versus estimated recording hours, and shortest candidates](docs/VIDEO_DURATION_README.md).

**Bicyclist speed statistics:** [Speed reference README—average, median and range for every location](docs/SPEED_REFERENCE_README.md). These are averages across measured cyclists, not hourly or15-minute averages. Future speed reports include the exact video measurement intervals.

**October23 request:** follow [STUDY_NEXT_STEPS.md](docs/STUDY_NEXT_STEPS.md) for the new partial-track speed/calibration tools, study-footage inventory, optional conflict review, and one-hour Colonial pilot. [Methodology LaTeX](reports/methodology/object_detection_study_20261023.tex) and [compiled report](output/pdf/object_detection_study_20261023.pdf). Wider study processing is newly requested and prepared, not run. The earlier completed October20batch below must not be resubmitted.

Latest follow-up: shortest listed camera recording is Pine Hills BL E (~25hours). A one-hour pilot and per-camera zone editor are prepared. Counts are recorded by source, user type, facility and15-minute bin, with a per-track lane ledger; new site coordinates still need identification. Follow the same next-steps guide above.

The final experiment batch is complete. **Do not resubmit it.** Remaining work is checking track identities and individual lane assignments; automatic physical-speed estimation remains pending calibration; the University manual map-based estimate below is exploratory, not independently validated.

## Bicyclist speed study — information for review (October 24, 2026)

**All 375 speed-reference records below describe bicyclists, across 14 street labels.** They come from `bicyclist speeds.xlsx` in the Bike Lane Study Counts folder. They are speed observations, not total traffic counts, video-hours, pedestrian speeds or car speeds. Location labels below reproduce the workbook; aliases and exact camera/date correspondence are not established for every street.

| Workbook location | Bicycle speed records | Facilities measured |
|---|---:|---|
| Aloma | 26 | Path |
| Baxter | 14 | Travel Lane |
| Carroll | 15 | Travel Lane |
| Colonial | 23 | Bike Lane, Sidewalk |
| Columbia | 9 | Bike Lane |
| Daniels | 11 | Path |
| Edgewater | 50 | Bike Lane |
| Lee | 2 | Travel Lane |
| Pleasant Hill | 41 | Path |
| Rinehart/CST | 25 | Path |
| Silver Star | 43 | Sidewalk |
| University | 78 | Sidewalk |
| West Orange/Park | 25 | Path |
| Winter Park | 13 | Travel Lane |

Source: [deduplicated reference records with workbook cell addresses](vision3/best/test_colonial/exp_results/speed_reference_readiness_20261023/all_reference_records.csv). Counts include all primary A–I table records, with repeated analysis-sheet copies deduplicated. They include the Colonial e-bike record retained in the analysis table.

**What can be compared:** estimated bicyclist speeds can be compared with the study speed distribution for the same street and facility (for example, University sidewalk versus University sidewalk). Matching recording, people and endpoints is still needed for individual speed-error validation. Selecting the method closest to the study average is an exploratory selection rule, not proof of accuracy. The study observations may have been timed in person separately from the videos.

### University: manual distance/time comparison already calculated

The owner measured **55.17 feet** on Google Maps and marked A/B crossing lines on the University video. A red-top bicyclist around08:52 was manually reviewed using front-wheel ground contact at both lines. Crossing brackets give a midpoint travel time of **4.625seconds**.

| Quantity | Result |
|---|---:|
| Manual map-distance estimate: one video bicyclist | **8.13 mph** |
| Range from crossing-time uncertainty alone | 7.52–8.85 mph |
| Study University sidewalk records | 78 |
| Mean study speed | 9.49 mph |
| Median study speed | 9.14 mph |
| Study observed speed range | 4.61–17.10 mph |
| Estimate minus study mean | −1.36 mph |

The estimate lies inside the study range. It is a **single-person versus group comparison**, not a matched-person accuracy result. The timing-only range excludes map-distance, endpoint placement and perspective errors. The workbook55-foot section and the owner55.17-foot map segment are not confirmed as identical. None of109saved University person tracks provided a reliable complete automatic A–B crossing, so8.13mph is a manual video estimate, not automatic tracker output.

[Calculated comparison](reports/cluster_returns/20261024/bicyclist_speed_comparison/RESULTS.md) · [Original video evidence and crossing timing](reports/cluster_returns/20261024/university_map_speeds/RESULTS.md) · [Reproducible manual timing input](data/reviews/speed/university_manual_crossing_20261024.json).

### Single HiPerGator speed experiment

**Bicyclist speeds only are exported; motorcycles, pedestrian speeds and car speeds are excluded.** Cars may act as approximate measuring sticks for camera calibration; pedestrian heads/feet may support the separate height-based calibration experiment. Those calibration inputs do not change the requested speed-output scope. The job currently applies map-free methods to existing Colonial bicycle candidates and includes the saved University manual-method comparison in its final report. It does not process all14locations.

After pushing/pulling the latest code, from `vision3/best/test_colonial`:

```bash
python code/submit_speed_pilot.py --go
```

Download `exp_results/SPEED_PILOT_TAG/` afterward. The entry point submits CPU previews for15candidate cameras across13reference locations, then the prepared Colonial GPU experiments. Other-camera previews require review before speed inference; Silver Star has no mapped candidate. Read reports under `camera_previews/` and `speed_results/`. Read `RESULTS.md`, `method_status.json`, `university_manual_comparison.csv` and, if enough valid estimates exist, `exploratory_closeness_ranking.csv`. Methods are compared within the same street/facility; the University example is not ranked against Colonial samples. No additional University GPU run is needed to reproduce the saved manual comparison.

| Method | Implementation / current result |
|---|---|
| University A–B map distance and manual timing | Calculated locally:8.13mph; included in the job report. |
| ICCV2021 pretrained car-based camera calibration | Author-model adapter implemented; real Colonial calibration pending HiPerGator run. |
| Pedestrian-height camera calibration | Paper-inspired implementation; current saved inputs insufficient (1qualifying independent track,20required). No speed result produced. |
| BMVC2014 automatic3D-box/vanishing-point calibration | Full pipeline not implemented. |
| Sochor2017 CAD vehicle-model calibration | Required CAD/render pipeline and assets not integrated. |
| 2026vehicle keypoint-template method | Required trained36-keypoint model/assets not integrated. |

No claim that all five papers have been implemented or run. Synthetic geometry tests and author-network loading checks passed; these are software checks, not real-world speed validation. [Research sources and limitations](docs/research/CCTV_TRAJECTORY_SPEED_20261024.md).

## Current results

- Reference system: fine-tuned RT-DETR V3 + SAHI + ByteTrack/stitching + X-CLIP + detector veto, motion, duration and static filters. It scores19/21with0unmatched counted tracks on four Colonial clips under legacy time matching. This is not identity-verified or general accuracy.
- Veto replay: off–40%tie9/11on development;50%gives8/11. **15%is retained by a tie rule, not established as uniquely best.** Frozen15%checks10/10on the other two already-inspected clips. [Threshold report](vision3/best/test_colonial/exp_results/veto_threshold_20261020/RESULTS.md).
- Owner review confirms missed cyclists at Anderson2021and Curry Ford2022, plus a missed Anderson motorcycle. [Encounter details](vision3/best/test_colonial/exp_results/newsites_owner_review_20261020.md).
- RF-DETR person-box precision28.6%/recall20.0%; Grounding DINO27.1%/65.0%on32owner-reviewed frames. Neither establishes a better counting system. [Box review results](vision3/best/test_colonial/exp_results/RF_DINO_person_validation_20261020.md).
- Provisional lanes: cyclists2sidewalk/2bike lane/3uncertain; pedestrians10sidewalk/1road/2uncertain; motorcycle1bike lane. Zone outlines are owner-approved; individual assignments and identities remain provisional. [Per-person table](vision3/best/test_colonial/exp_results/labelled_validation_20261020/people_lane_speed.csv).
- Twenty image-motion estimates exist; validated mph does not. Workbook35ft/30ftsegments are not established as the owner's drawn lane-end spans. None of the seven bicycle candidate tracks crosses both drawn lines. [Calibration feasibility](vision3/best/test_colonial/exp_results/exploratory_speed_calibration_20261020/RESULTS.md).

Normal duration is3seconds for both classes, day and night. A strict night-only cyclist exception allows0.3seconds with detector cyclist share≥90%and weighted X-CLIP≥0.90. Broad0.4-second sensitivity is off.

## Where things belong

| Folder | Contents |
|---|---|
| `vision3/best/test_colonial/` | Active experiment: code, truth, zones, counts, structured run logs and results. Paths retained for HiPerGator compatibility. |
| `data/reviews/colonial_20261020/` | Original and confirmed owner box labels; estimated, uncalibrated gate coordinates. |
| `reports/presentations/` | PowerPoints. Always create a new copy when editing. |
| `reports/cluster_returns/20261019/` | Original returned terminal output and research report. |
| `Bike Lane Study Counts/` | Original study workbooks and extraction tools. |
| `docs/` | Current checklist, video paths, runbook and handoff. |
| `pipeline/`, `slurm/`, `scripts/` | Shared pipeline and launch utilities. |
| `vision3/`, `vision2.v1-six-class-corrected-v1.yolov8_extracted/`, `data/` | Current training, dataset and experiment assets. Superseded Vision3 implementations removed; see vision3/README.md. |
| `archive/` | Historical sources and old failure diagnostics. |

Start with the [current checklist](docs/tasks/todo.md), [handoff](docs/history/HANDOFF.md), and [video paths](docs/VIDEO_PATHS.md). The [latest presentation](reports/presentations/bike_weekly_meeting_10_20_reviewed.pptx) is preserved; see current reports for results added after it was authored.

## CPU tools — already run locally

No new GPU submission is required. To repeat the veto comparison from `vision3/best/test_colonial`, with the project Python environment active, use a fresh output folder:

```bash
python code/tune_veto.py --out exp_results/veto_threshold_repeat
```

The threshold is frozen using development clips before checking clips are evaluated. Source-setting parity must pass; saved exports are rounded. Optional `--identity-map` restricts evaluation to approved tracks. The reference configuration is never changed.

Confirmed32-frame person labels are in [person_box_review_confirmed_20261020.json](data/reviews/colonial_20261020/person_box_review_confirmed_20261020.json); the original export is beside it. The [gate coordinates](data/reviews/colonial_20261020/colonial_speed_gates.json) are uncalibrated and must not be supplied as measured gates for mph.

## Repository cleanup

Loose review inputs and returned reports were moved into folders; an identical root batch-report copy, completed scheduler text logs with surviving structured records, Python caches and Finder metadata were removed. Failed/incomplete job diagnostics were retained in `archive/diagnostics/20261019/`. Source data, models, annotations, experiment tables, structured JSON run logs and edited decks were preserved.

[Cleanup manifest](docs/REPO_CLEANUP_20261020.csv) records moves/deletions with hashes. [Earlier command guide](docs/history/README_before_cleanup_20261020.md) is historical and must not be treated as a request to resubmit jobs. Future HiPerGator pulls keep the active experiment paths intact; the moved review inputs now use the paths above.

Vision3 was also pruned:63superseded files removed,26retained files grouped into training/comparison/weights_tools/tools (and an aggregate report moved to reports). See [Vision3 guide](vision3/README.md) and [file manifest](docs/VISION3_CLEANUP_20261020.csv). Current v19 pipeline paths and saved experiment outputs are unchanged.

Manual alternative prepared October24: [manual bicycle speed review](docs/MANUAL_BICYCLE_SPEED_README.md). CPU-only workbook-positive interval clips and browser manual point marking; thresholds unchanged, saved learned calibration gives exploratory mph. Initial scope selected adaptive source hours; outside-hour positive bins listed, not silently covered. Two tests passed; extraction not run locally.
