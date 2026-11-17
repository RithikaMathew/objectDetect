# Repair handoff and validation

Changed code: `pipeline/generate_near_miss_report.py`, `pipeline/manual_occlusion_metrics.py`, `pipeline/near_miss_screening.json`, `vision3/best/test_colonial/code/clearance_metrics.py`, `vision3/best/test_colonial/code/clearance_pilot.py`, and `tests/test_near_miss_pipeline.py`. Existing user edits to HANDOFF.md and look.md were left intact.

- Export per-frame/pair geometric rejection reasons before support gates discard metrics; retain the two reviewed real passing candidates separately from metric eligibility.
- Replace hard-coded event report metrics with saved-data calculations, source traces, unit/method/null-reason fields, 3 unique event rows and separate review/screening fields.
- Align manual positions to selected frame timestamps; remove filtered endpoint clamping; distinguish manual contact proxies, interpolation and model extrapolation.
- Correct historical PET column-reading error: 0.294117647 was coverage 5/17, not PET. Preserve the old reported PET and TTC in historical fields. Reproduce CV TTC 0.374529713 s; aligned result 0.371803710 s, conditional CV sensitivity range 0.347696603–0.398107805 s. Baseline PET remains missing.
- Correct pedestrian car68 namespace to sensitive; reference car68 is an unrelated late object. Compare synchronized manual/detector contacts without pretending that different proxies establish accuracy.
- Record nominal/burned-in absolute clock discrepancies; no unverified clock correction applied.
- Disable adopted numerical safety thresholds by leaving them unset. Engineering sensitivity settings remain separate from supported screening and reviewed classifications. Exact old/new settings and source lines: CODE_PATH_MAP.md, thresholds.csv, threshold_source_inventory.csv and effective_task_configuration.csv.

Before: two real visual passes were absent from strict metric outputs; pedestrian report claimed PET 0.294 s / TTC 0.375 s. After: 3 unique candidates, 2 verified passes, 1 reviewed crossing; 3 image diagnostics, 0 eligible metre clearances, 1 conditional surrogate TTC, 0 baseline surrogate PET, 1 potential conflict, 2 indeterminate safety classifications, 0 confirmed under a validated protocol. One reviewed wheel false detection and one no-pass comparison remain excluded. Pixel minima are selected-frame proxies, not continuous physical clearance.

Validation:

```sh
python3 pipeline/generate_near_miss_report.py --repo . --out reports/near_miss
python3 -m pytest tests vision3/best/test_colonial/code/test_clearance_pilot.py -q
```

36 tests passed. All 175 input evidence hashes matched before/after generation. All 12 preserved pedestrian input copies match downloaded originals. Eight report artifact links resolve. Generated review JavaScript passes `node --check`; `git diff --check` passes. Annotated frames and the event plot were visually inspected. Interactive browser execution was unavailable (`iab` connection unavailable), so browser interaction has not been certified.

No GPU inference, new video experiment, outreach or source-evidence edits were performed. Required additional evidence is documented in PROFESSOR_RESULTS.md: independent lateral control geometry and reviewed physical edges, visibility/conflict-region evidence for crossing PET, and source recording/camera clock alignment. No additional click annotation was requested.

The older assets named `image_gap_summary.svg` and `ttc_pet_summary.svg` predate this repair and are retained as historical outputs; their fixed PET labels are superseded by the new report and `assets/event_metrics.png`.
