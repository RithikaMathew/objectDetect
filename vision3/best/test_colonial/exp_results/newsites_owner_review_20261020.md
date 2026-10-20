# Owner visual review — 2026-10-20

Reported clock times below are supplied by the owner. They are not a new exhaustive ground-truth annotation or identity audit. Preserve the existing four Colonial truth files.

| Site | Encounter | Owner observation |
|---|---|---|
| Anderson 2021 | Pedestrian, 12:01:24–12:01:32 pm | Detected |
| Anderson 2021 | Cyclist, 12:01:37–12:01:45 pm | Detected |
| Anderson 2021 | Another cyclist, 12:01:40–12:02:43 pm | Missed |
| Anderson 2021 | Motorcycle, 12:05:48–12:05:50 pm | Missed |
| Curry Ford North 2022 | Cyclist, 12:09:05–12:09:11 pm; very blurry | Missed |

The owner reports two distinct Anderson cyclists despite overlapping time intervals. Motorcycle remains a separate category here. Among reported encounters, Anderson detected one of two cyclists and one pedestrian; Curry Ford missed its reported cyclist. These are confirmed visual limitations, not whole-video recall, precision, AP, or proof of the cause. Blurriness was observed at Curry Ford; it does not establish that a specific enhancement would recover the rider. Do not claim successful generalization or start another model sweep automatically. Both sites appear in the training recipe and both tested clips are 720×480.

## Colonial lane and speed inputs

Owner approved the zone previews visually. This accepts visible polygon alignment; individual lane assignments and track identities still need their own review.

Source: `Bike Lane Study Counts/bicyclist speeds.xlsx`:

- Colonial bike lane: **35 feet**, 12 unique records including an e-bike. Example source cells: `Bike Lane!A12` / `BL Analysis!A61`.
- Colonial sidewalk: **30 feet**, 11 unique records. Example source cell: `Sidewalk!A24`.

These are measured lengths recorded in the study, not distances inferred from pixels. The workbook records do not establish the gate endpoints in this camera view, the applicable recording date, or a confirmed record-to-person mapping. Use these lengths only with the corresponding measured sections; do not substitute arbitrary polygon edges. Validated mph remains pending gate correspondence and person/record verification.

## Person-box review received

Root `person_box_review.json` preserved unchanged: 32 frames, 20 boxes, only 1 frame marked reviewed (`day_holdout_1245:106994`). The review UI clears the reviewed checkbox when drawing or undoing. Unchecked frames cannot be treated as confirmed empty or complete. Asked owner whether all 32 frames are finished; do not auto-approve them without that confirmation.

No matching local `rf_boxes/manifest.json` / prediction pack was found in this repository. Scoring requires that existing pack from `exp_results/final_review_20261020/rf_boxes` plus the completed review JSON. No new model inference or batch submission is needed.

Owner confirmation (2026-10-20): all32person-box frames, including empty frames, were inspected; unchecked boxes were accidental. Original JSON preserved. `person_box_review_confirmed_20261020.json` marks all32reviewed based on explicit owner confirmation and retains all20boxes. Prediction pack still required for scoring; no accuracy calculated yet.

Confirmed person-box scoring completed locally (2026-10-20): found existing pack at `/Users/rithika/Downloads/final_review_20261020/rf_boxes`. All32owner-confirmed frames,20human boxes, one-to-one IoU>=0.50, saved thresholds. RF-DETR:4TP/10FP/16FN, precision28.6%, recall20.0%. Grounding DINO:13TP/35FP/7FN, precision27.1%, recall65.0%. DINO finds more labelled person boxes but generates more false boxes; neither is a demonstrated replacement for the counting reference. Selected repeated frames, not unique people/AP/whole-video cyclist accuracy or an independent holdout. Report: `vision3/best/test_colonial/exp_results/RF_DINO_person_validation_20261020.md`. Earlier statements that pack was unavailable or no score existed are superseded.

Received root colonial_speed_gates.json: two facilities with35ft/30ft and720x480reference, reviewer Rithika, but measurement_source="n/a". Original preserved. No physical speed calculated: exact measured endpoint correspondence not established. Asked owner whether these are known study endpoints or visible lane ends. Added placeholder-source rejection in exporter and speed measurement plus regression test. Numeric workbook lengths must not be assigned to arbitrary scene-wide segments.

Owner clarification (2026-10-20): colonial_speed_gates.json marks visible lane ends, NOT known study measurement endpoints. Therefore it is unsuitable for mph calculation; do not replace its n/a source or accept35ft/30ft for those drawn spans. Original preserved; review decision in exp_results/colonial_speed_gate_review_20261020.json. Physical speed remains blocked pending identifiable independently measured endpoints (or appropriate metric calibration). Image-motion estimates remain available; no further GPU run needed.

Exploratory calibration attempted locally (2026-10-20) at owner request: new code/exploratory_gate_check.py checks estimated finite gates without granting physical distance. Output exp_results/exploratory_speed_calibration_20261020/{RESULTS.md,crossings.csv,summary.json}. All7actual bicycle truth rows checked, both facilities (14checks), full saved unverified candidate tracks;0complete two-line crossings. None crosses the first line. Workbook rescanned:23Colonial speed records but0verified person links; no timestamps found in these speed rows. Thus0distance fits/0held-out validation pairs, no mph/MAE. Do not pair records by nearest speed or equate study record IDs with track IDs. Future fit requires independently matched people and crossings, fixed facility distance, and different people for validation. Three crossing tests pass (clip-time interpolation, finite-line nonextension, large-gap exclusion). No inference/batch submitted; original gates/truth untouched.
