# Video-only near-miss results — 20261110_v1

- **3 unique reviewed interactions:** 2 cyclist passes and 1 close pedestrian crossing. Repeated detector/scenario rows are not encounters.
- Selected cyclist horizontal image gaps remain **6 px** and **20 px**, each from 3 existing annotated frames. These are not continuous minima or physical lateral clearance.
- Approximate cyclist speeds remain **9.709555 mph** and **11.515719 mph**, using the same unvalidated learned mapping; agreement with manual speeds does not validate scale.
- Pedestrian historical conditional TTC **0.371804 s** is preserved. The PTS-based recomputation is **0.371804 s** under the existing unvalidated CV/footprint model; conditional CV assumption range **0.347697–0.398111 s** across 14 scenarios.
- **0.294117647 is 5/17 observation coverage, not PET.** No occupancy-based PET is available from the original annotations. Current imported review status: **not_observable**; supported reviewer intervals appear below only if actually supplied.
- **0 validated metre clearances; 0 confirmed near misses under a validated protocol.** This does not mean no near misses occurred. The sample cannot estimate a population rate.

| event | frames | sync | selected_edge_px | detector_proxy_px | manual_proxy_px | relative_px_s | conditional_TTC_s | reviewed_zone_PET_s | review |
|---|---|---|---|---|---|---|---|---|---|
| white_suv | 351–411 | 58/61 (95.1%) | 6 @ frame 391 | 62.535 @ frame 398 | N/A | 67.981 | N/A | N/A | indeterminate |
| dark_car | 356–453 | 98/98 (100.0%) | 20 @ frame 445 | 89.811 @ frame 356 | N/A | 29.401 | N/A | N/A | indeterminate |
| pedestrian_car | 1382–1411 | 10/30 (33.3%) | N/A | 110.189 @ frame 1394 | 33.838 @ frame 1405 | 285.299 | 0.371804 | N/A | potential_conflict |

## What was checked

- Decoded clip frame PTS are audited directly with ffprobe; frame stepping uses each decoded frame, not only detection samples. Counts/percentages use each explicitly listed analysis window. Detected/manual/reconstructed coverage categories overlap; true visibility coverage remains unknown without per-frame visibility review.
- The 58/98 cyclist synchronized samples remain diagnosed: all fail the assumed alongside gate (3.15 learned units); no strict supported pair. Along-track ranges are −18.803 to −5.817 and −21.874 to −4.105 learned units. Gate failures are geometric; local detection gaps are reported separately.
- All six pre-existing cyclist edge annotations are loaded automatically. Manual-versus-detector comparisons are same-frame differences between distinct image proxies, **not independently measured accuracy**. Three pedestrian car-click/detector comparisons are 29.14, 37.61 and 72.69 px; car namespace is sensitive 68, not unrelated reference 68.
- The original click tool rounded playback time to a frame ID; pedestrian car click saved as frame1382 has playback time 46.072939 s, which lies in decoded frame1381. This one-frame capture ambiguity is preserved in `annotation_alignment_audit.csv`; no automatic relabeling or certified same-frame accuracy is claimed. ±1-frame sensitivity remains required.
- No independent occupancy entry/exit labels were invented. `validation_comparison.csv` leaves unavailable automatic physical-zone boundary errors null. The interactive viewer accepts targeted review and preserves provenance.
- Sensitive track21 (wheel false car) and the middle no-pass comparison remain excluded. Review labels remain two indeterminate safety classifications and one potential conflict.

## Limitations and smallest next evidence

- For PET, mark one shared physical road-space zone and bound pedestrian exit/car entry using visible neighboring frames. Where occluded, supply defensible interval brackets and notes; if the order cannot be established, leave PET N/A. Surveyed dimensions are unnecessary for this timing task. Drawing a polygon or overlapping image boxes alone does not establish shared physical occupancy.
- To check cyclist continuous minima, inspect additional visible passing frames; retain 6/20 px as selected-frame results until then. No mandatory re-annotation of the six existing frames.
- Physical clearance and physical TTC remain unavailable without validated geometry/footprints or a validated alternative collision model. Evasive action is unknown; noisy pixel derivatives do not establish hard braking.
- Absolute clocks remain unresolved: white frame391 nominal 12:40:21.013 vs burned-in 12:40:23; dark frame445 nominal 12:53:52.815 vs 12:53:54; pedestrian frame1405 nominal 17:08:46.847 vs 17:08:49. Saved pedestrian raw CSV labels also have a five-hour mismatch. No fixed clock correction is applied. Frame-relative PTS drive new metrics; source recording drop/loss cannot be certified from re-encoded clips.

Open [offline viewer](review_validation.html). Data: [event metrics](event_metrics.csv), [manual/automatic comparisons](validation_comparison.csv), [sensitivity](sensitivity_summary.csv), [timing](timing_audit.csv), [methods and references](METHODS_AND_THRESHOLDS.md), [run/review instructions](RUN_AND_REVIEW.md).
