# Run and targeted review

```sh
cd /Users/rithika/Desktop/objectDetect
python3 pipeline/near_miss_next.py --out reports/near_miss_next/20261110_v1
open reports/near_miss_next/20261110_v1/review_validation.html
```

The HTML is self-contained: all three original MP4 clips, source hashes, PTS, tracks, annotations, styles and scripts are embedded. It works offline by double-clicking; no server/account/network/CDN is required. Missing source assets cause an explicit generator error, never fabricated frames. Browser decode failures show a visible error. Existing assets total 120 seconds (two 30 s cyclist clips and one 60 s pedestrian clip); no new inference or video experiment occurs.

1. Select an event. Play/pause; step ±1 decoded frame; type a frame or scrub. Wheel/zoom controls zoom around the cursor; use Pan mode to drag. Reset restores image coordinates. Right panel shows image trajectories, nearest synchronized approach, manual/detector differences and gate diagnostics.
2. Toggle boxes, histories, manual points/edge rulers, assumed footprint overlays, calibration support or reconstructed segments. Reconstruction is labeled and off by default. Missing automatic car boxes/track-loss spans do not mean no vehicle. PTS time and one-based frame appear prominently; absolute source clocks remain unresolved.
3. Cyclists: all six usable edge frames are preloaded. Click a saved-frame chip to inspect. Only if checking the continuous visible-pass minimum, select Edge mode, mark cyclist and near-side car x coordinates, set visibility/uncertainty and save. Existing annotations remain unless explicitly replaced at the same frame. Exports retain original records and an edit history for replacements. Vertical rulers encode x only.
4. Pedestrian PET (the only necessary new annotation if PET is wanted): select Zone mode, click at least three vertices, finish polygon. Verify that it corresponds to the same physical road-space zone for both users; record why, reviewer name and confirmation. Drawing image overlap is insufficient. Capture last pedestrian occupied / first car occupied frames, independently check neighboring frames, and check each boundary-supported box. Broaden frame brackets with evidence if occluded and record notes. Unsupported boundaries produce N/A; negative differences show temporal overlap; overlapping time brackets show uncertain order. No surveyed dimensions are required.
5. Optional per-frame footprint polygons can be marked and saved for either object, with visibility. They are manual image annotations, not automatically metric road footprints. Evasive action remains unknown unless a reviewer supplies visible evidence and notes.
6. Save annotations JSON for regeneration; CSV exports are also provided. Export reviewed event CSV and validation summary directly in the browser. Nothing is uploaded or written back to original sources. Import a saved JSON to restore edits; source-video hash/schema checks reject mismatched files. Unsaved changes prompt before leaving. Exports use the current review state; no automatic confirmed label exists.

To regenerate tables from a downloaded JSON (replace the file path):

```sh
python3 pipeline/near_miss_next.py --annotations /path/to/near_miss_annotations.json --out reports/near_miss_next/20261110_reviewed_v2
python3 -m pytest tests vision3/best/test_colonial/code/test_clearance_pilot.py -q
node --test tests/near_miss_validation_engine.test.cjs
```

Optionally pass `--config /path/to/screening_settings.json`, with e.g. `{"adopted_ttc_s": 1.5, "adopted_pet_s": 5.0}`. These are opt-in context-limited exploratory comparisons, never confirmed labels. Defaults stay null; metre screens are rejected.

Use a new output version to retain snapshots. Browser JSON edits do not modify CSV files already on disk; run regeneration or download current event CSV explicitly. Existing evidence suffices for selected-frame gaps; do not repeat those six annotations. No new occupancy/physical-zone labels are inferred from older manual car clicks. Unresolved PET needs this targeted visual judgment, not a new calibration survey or GPU run.
