# Validation record — 20261110_v1

- **48 Python tests passed**, including prior clearance tests and new coverage, PTS, conditional TTC, occupancy PET, source-preservation, negative-control and JSON regeneration tests.
- **10 dependency-free JavaScript calculation tests passed**, including PET missingness, timing intervals, overlap/uncertain order, quantization, occlusion bounds, coverage independence, edge visibility, provenance and separate reviewed labels.
- **9 offline Chrome workflow checks passed** (Chrome 157.0.8103.50): original embedded video playback, exact frame stepping, typed seeking, toggles, wheel zoom and drag pan, new edge annotation without losing the original six frames, JSON download/import, annotation/event CSV and summary downloads, zone/occupancy PET controls, and playback time progression. No JavaScript errors or HTTP requests were observed. Detailed record: BROWSER_VALIDATION.json; inspected screenshot: browser_initial.png.
- All **216 preserved input/evidence files** matched their before/after SHA-256 hashes. The prior reports, raw videos, original annotations, returned detector exports and user edits remain intact. Build/code/video hashes: build_manifest.json and provenance.csv.
- Decoded MP4 PTS have no nonpositive intervals and no intervals >1.5×median across 900, 899 and 1799 decoded frames. This does not validate original-recording frame loss or fix absolute clock discrepancies.
- One manual car click (saved frame1382) has playback time in decoded frame1381; it remains explicitly ambiguous. No automatic relabeling was applied. Comparisons sharing a saved frame ID are not certified independent timing/measurement errors.
- Generated report links resolve; `git diff --check` passes.

Commands run from `/Users/rithika/Desktop/objectDetect`:

```sh
python3 pipeline/near_miss_next.py
python3 -m pytest tests vision3/best/test_colonial/code/test_clearance_pilot.py -q
node --test tests/near_miss_validation_engine.test.cjs
NODE_PATH=/Users/rithika/.npm/_npx/a8a7eec953f1f314/node_modules node tests/near_miss_validation_browser.cjs
```

The browser regression uses the already-cached Playwright package and installed Google Chrome in an isolated headless session, with networking disabled. The in-app browser connection was unavailable. The delivered HTML needs neither Playwright nor a server: open the HTML directly. Browser-test synthetic occupancy/edge annotations were saved only in temporary test directories and are **not** event evidence or shipped review labels.

The generated event table has 3 unique reviewed candidates, 2 real cyclist passes and 1 close pedestrian crossing. Selected cyclist gaps remain 6 and 20 px; manual pedestrian contact-proxy minimum is 33.838 px at frame1405, a different spatial proxy. Conditional TTC recomputes to 0.371804 s; the CV sensitivity range is 0.347697–0.398111 s. Original-data occupancy PET remains N/A. No physical metres, independent measurement accuracy, real-world probability, confirmed near miss or population rate is validated by successful execution.

Only targeted additional visual review is needed to attempt PET: identify the same physical conflict zone, then support both occupancy boundary brackets. If occlusion prevents this, keep PET interval/N/A and state the evidence limitation. The six existing cyclist annotations need not be repeated. No new GPU run, camera calibration, road survey, outreach or video experiment was performed.
