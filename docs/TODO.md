# Current next steps — October 29, 2026

Start with [latest same-video results](../reports/cluster_returns/20261027/completed_speed_batches/RESULTS.md). Root todo.md contains the owner's timing/calibration assessment notes. Superseded task/chat lists have been removed.

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

## Remaining checks retained from the earlier detector checklist

- [ ] Confirm complete track identity against the existing four truth clips, including barricade-to-person switches; temporal matches alone do not verify identity.
- [ ] Treat lane assignments as provisional until individually reviewed.
- [ ] Keep detector proposal-box scores separate from cyclist/count accuracy. No new model sweep is required.

## Archive inventory completed

- [x] Full ZIP video-duration audit: 9,085 videos across 179 site/view/device groups, 9,057.34 summed playback hours.
- [x] Consolidated archive contents, years, hours and speed-export findings in [one summary](MIOVISION_CONTENTS_SUMMARY_README.md). Compressed/proprietary file contents remain uninspected; no native speed export confirmed.

## November 9: clearance and camera calibration

- [x] Added [MetroPlan interpretation, clearance method and draft reply](PASSING_CLEARANCE.md); draft has not been sent.
- [x] Added separate metric-footprint clearance calculator with synthetic verification; actual video extraction and measurement remain pending.
- [ ] Obtain deployment coordinates, original marked-point calibration and distances, lateral road geometry, timing metadata and occurrence coverage rules/logs.
- [ ] Verify Mighk's sampled lateral positions per site; retain Colonial's documented bike-lane/sidewalk distinction.
- [ ] Prepare independently calibrated, reviewed cyclist/vehicle footprints for a pilot passing clip, validate clearance, then extend to more encounters. Report all eligible facilities separately.

## Bounded clearance pilot prepared

- [x] Prepared [one-command HiPerGator pilot](CLEARANCE_PILOT_RUN.md): three 30-second Colonial encounters, two detector settings, eight geometry/motion scenarios, automatic report and review packet. Uses current files only.
- [x] Local analytic, synthetic integration, extraction/timing and mocked submission checks passed. Cluster GPU inference is not yet run.
- [ ] Transfer the bundle/new files, submit the pilot once, then review clearance estimates and candidate IDs before interpreting threshold counts.
