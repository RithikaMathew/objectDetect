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

## Final checks still open — do not claim these finished

- [ ] Review saved reference tracks against the existing truth IDs; approve FULL-track identity in identity_review.csv. Inspect barricade-to-person switches; keeping TTA off does not prove all reference IDs clean.
- [ ] Check v2 lane polygons on actual raw-frame overlays; provisional road/bike/sidewalk/grass assignments are not human lane truth.
- [ ] Validate existing RF/DINO person boxes on selected raw frames, or explicitly close them as unvalidated exploratory audits. No extra inference is required. Review build: code/final_review.slurm.
- [ ] Finish additional-site/year runs (Anderson 2021, Curry Ford North 2022) if not yet submitted; results have not been supplied. Both appear in training recipe, so not strict unseen-site validation.
- [ ] Physical cyclist speed: identify actual measured 35-ft / 30-ft gate lines for this camera/date and link study record numbers to the clip/person. Lane polygons alone cannot supply this. Code supports measured crossing speeds; mph and paired speed errors are pending those inputs.

## Closed with limitations / no further experiment required now

- High-sensitivity run completed with 28 extras. A 12-minute raw-snippet review pack exists, but recall/workload benefit was not measured. Do not claim workflow savings; no requirement to pursue this failed route now.
- Walking-away evidence is partial: h5 has detector-right/X-CLIP-wrong classification fixed by fusion. This does not establish the cause of every undetected away-moving person. Report the limitation rather than promise a universal fix.
- A conventional higher-resolution camera, temporal feature aggregation and new architectures are not necessary to finish this bounded experiment set; no claim that all possible detection methods have been exhausted.

## Back burner / excluded

- ~40-track comparison and own-night fine-tuning remain deferred.
- Full-day 24/48-hour scaling remains removed.
- Never overwrite an existing PowerPoint. Preserve owner-added slides and create a new dated copy.
