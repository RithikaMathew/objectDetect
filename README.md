# Object detection study — start here

**October23 request:** follow [STUDY_NEXT_STEPS.md](docs/STUDY_NEXT_STEPS.md) for the new partial-track speed/calibration tools, study-footage inventory, optional conflict review, and one-hour Colonial pilot. [Methodology LaTeX](reports/methodology/object_detection_study_20261023.tex) and [compiled report](output/pdf/object_detection_study_20261023.pdf). Wider study processing is newly requested and prepared, not run. The earlier completed October20batch below must not be resubmitted.

Latest follow-up: shortest listed camera recording is Pine Hills BL E (~25hours). A one-hour pilot and per-camera zone editor are prepared. Counts are recorded by source, user type, facility and15-minute bin, with a per-track lane ledger; new site coordinates still need identification. Follow the same next-steps guide above.

The final experiment batch is complete. **Do not resubmit it.** Remaining work is checking track identities and individual lane assignments; physical speed is blocked by missing calibration and person-to-study links.

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
