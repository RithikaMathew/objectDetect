# Current to-do — audited 2026-10-20

Read root README.md for current commands. Further detector/model sweeps are closed; finish validation of the existing work. Existing four truth files stay unchanged.

## Completed experiments / analysis

- [x] Combine fine-tuned RT-DETR, SAHI, ByteTrack + ID stitching, X-CLIP and fixed fusion/motion/count rules.
- [x] Measure contribution: reference 19/21, no speed 17/21, no detector veto 18/21 (legacy time matching; not identity-verified).
- [x] Analyze both-wrong / detector-only / X-CLIP-only cases; paired classification comparison now exported: detector16/21 vs raw X-CLIP14/21, conditional on legacy time matches.
- [x] Test SAHI, fusion, static rejection, gamma, CLAHE, TTA, sensitivity and Zero-DCE; completed research suite. No improvement from TTA/sensitive/brightening; retain reference.
- [x] Test duration settings; reference uses normal 3 s plus strict night-only 0.3–3 s cyclist exception. Failed broad-sensitive 0.4 s applied BOTH day/night and is OFF in reference/new-site runs.
- [x] Run full-frame RF-DETR and Grounding DINO proposal audits. Proposal totals are not accuracy.
- [x] Run a higher-resolution other-site video: Corrine 706 (2025), 960x540 fisheye. Visual review found missed distant cyclists. This records a limitation, not successful generalization.
- [x] Extract provisional lanes and image-motion speeds for ONLY the 21 existing truth rows: 20 usable motion estimates; one candidate insufficient. Outputs in exp_results/labelled_validation_20261020. Not validated mph.
- [x] Inspect study workbooks: 23 unique Colonial speed records found (12 bike-lane incl. one e-bike; 11 sidewalk). Count workbook aggregate facility comparison exported. Physical record-to-person matches unverified.
- [x] Add identity-required evaluation: unreviewed time matches cannot receive verified accuracy credit.

- [x] Add and run full-system veto threshold replay: source-setting parity passed; development off–40%tie9/11,50%8/11; retains15%by tie rule, checking10/10. Exploratory only, all clips previously inspected; no deployed threshold changed. Results exp_results/veto_threshold_20261020.

## Final checks still open — do not claim these finished

- [ ] Review saved reference tracks against the existing truth IDs; approve FULL-track identity in identity_review.csv. Inspect barricade-to-person switches; keeping TTA off does not prove all reference IDs clean.
- [x] Owner visually approved v2 zone previews (2026-10-20). Individual road/bike/sidewalk/grass assignments remain provisional, not human lane truth.
- [x] Score owner-confirmed person boxes on all32selected frames (20human boxes): RF-DETR precision28.6%/recall20.0%; Grounding DINO27.1%/65.0%. Report exp_results/RF_DINO_person_validation_20261020.md. Selected-frame person-box validation only; not cyclist/counting accuracy or AP.
- [x] Run reference system on Anderson 2021 and Curry Ford North 2022: both SUCCEEDED for900seconds. Anderson1cyclist/1pedestrian; CurryFord0/0. Both720x480.
- [x] Obtain owner visual review of both new-site videos: Anderson misses a cyclist and motorcycle; Curry Ford misses a blurry cyclist. Exact times in exp_results/newsites_owner_review_20261020.md. This documents failures, not exhaustive accuracy. Both sites appear in training recipe.
- [ ] Physical cyclist speed: identify actual measured gate endpoints for this camera/date and link study records to people. Owner confirmed colonial_speed_gates.json uses visible lane ends, not known measured endpoints; do not apply workbook35ft/30ft to these spans. Exploratory calibration attempted:0complete crossings across7bicycle candidate tracks and no verified Excel-person links (exp_results/exploratory_speed_calibration_20261020). Physical mph and paired speed errors remain blocked; image-motion estimates are available.

## Closed with limitations / no further experiment required now

- High-sensitivity run completed with 28 extras. A 12-minute raw-snippet review pack exists, but recall/workload benefit was not measured. Do not claim workflow savings; no requirement to pursue this failed route now.
- Walking-away evidence is partial: h5 has detector-right/X-CLIP-wrong classification fixed by fusion. This does not establish the cause of every undetected away-moving person. Report the limitation rather than promise a universal fix.
- A conventional higher-resolution camera, temporal feature aggregation and new architectures are not necessary to finish this bounded experiment set; no claim that all possible detection methods have been exhausted.

## Back burner / excluded

- ~40-track comparison and own-night fine-tuning remain deferred.
- Full-day 24/48-hour scaling remains removed.
- Never overwrite an existing PowerPoint. Preserve owner-added slides and create a new dated copy.
