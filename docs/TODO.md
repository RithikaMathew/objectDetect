# Current next steps — October 27, 2026

Start with [latest same-video results](../reports/cluster_returns/20261027/completed_speed_batches/RESULTS.md). Root todo.md contains the owner's timing/calibration assessment notes; docs/tasks/todo.md retains the older detector audit.

## Completed

- [x] Original duration audit:1919files/41cameras, totals saved and README updated.
- [x] Robust manual speed, review-clip packet timing, plots and sensitivity analysis:30encounters/29speeds/18clips.
- [x] Optional marking/3-Dwheel evidence checks and candidate-edge crops implemented. Real metric evidence absent; no wheel/marking scale result claimed.
- [x] HiPerGator1.5-second full-hour/quota run and exact18manual-clip run completed; returned reports preserved and merged with manual results.
- [x] Same-clip aggregate comparison:35study,30manual,32automatic; no accuracy percentage claimed.

## Finish before more experiments

- [ ] Obtain selected_candidates.csv from same-video batch for exact annotated paths and track metadata. Review Columbia near-stationary/long tracks, Aloma12:59:47 extra candidate, Edgewater overlapping/missing encounters. Carroll time recovery is encouraging but still needs full identity review.
- [ ] Confirm University map-distance endpoints in the video; compare learned distance with the55.17ft map estimate. Review timing/geometry evidence without fitting scale to the workbook mean.
- [ ] Report per-person detection/speed errors only if identity/type and independent same-person speed references exist. Otherwise keep count discrepancies and unmatched group speed differences.
- [ ] Incorporate reviewed results into a new presentation copy if requested; older decks remain historical.

## Optional / deferred

No further broad detector sweep is required to finish this study. Other trackers/keypoint training remain possible; existing tracker is already ByteTrack. Real wheel/marking calibration needs evidence, automatic camera location is not implemented. No24/48hour scaling,40trackannotation or nightfine-tuning reintroduced.
