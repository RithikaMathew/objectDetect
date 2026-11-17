# Colonial near-miss pilot: numerical results

Two visually reviewed cyclist passes and one pedestrian crossing are retained as **3 unique interaction candidates**. Physical metre clearance is unavailable for all three. No confirmed near miss is established under a validated adjudication protocol; this does not show that no near misses occurred. This selected sample cannot estimate a population rate.

| event | time | IDs | speed_mph | relative_px_s | image_px | clearance_m | physical_TTC_s | physical_PET_s | conditional_TTC_s | review |
|---|---|---|---|---|---|---|---|---|---|---|
| white_suv | 2019-07-10 12:40:21.013 | cyclist 1 / car 9 (reference namespace) | 9.709555 | 67.980487 | 6.000000 | N/A | N/A | N/A | N/A | indeterminate |
| dark_car | 2019-07-10 12:53:52.414 | cyclist 1 / car 18 (reference namespace) | 11.515719 | 29.401363 | 20.000000 | N/A | N/A | N/A | N/A | indeterminate |
| pedestrian_car | 2019-07-10 17:08:46.535 | pedestrian 1 reference / car 68 sensitive (same clip) | N/A | N/A | 33.837849 | N/A | N/A | N/A | 0.371804 | potential_conflict |

Image values have different meanings: cyclist minima are **6 px and 20 px among three selected horizontal edge annotations each**, not continuous minima or perpendicular passing clearance. The pedestrian value is a selected-frame Euclidean contact-proxy distance, not edge clearance. Relative px/s values are image velocity fits over synchronized observations, not road speeds. Approximate cyclist mph values share the learned map with manual speed estimates and do not validate physical scale. Event timestamps are inferred from source filenames and selected annotation windows, not independently verified clocks.

## Pedestrian discrepancy and reproducibility

The historical **reported** PET **0.294 s** remains recorded in `historical_pet_s` for provenance, but it is **not reproduced**. Running the saved algorithm and observations gives **blank PET** for all five methods. **0.294117647 = 5/17 is the manual-observed coverage_fraction**, immediately after the blank PET column. Historical CV TTC reproduces as **0.374530 s**. Frame-aligned reconstruction gives **0.371804 s**, conditional on the same unvalidated mapping and assumed footprints. It is exported separately from eligible physical `ttc_s`, which remains null. Manual clicks carry no reliable per-frame hidden/visible labels; a contact proxy during overlap is not verified observation of hidden ground contact.

| method | samples | min_ttc_s | pet_s | coverage_fraction | first_common_s | last_common_s |
|---|---|---|---|---|---|---|
| manual_observed | 5 | N/A | N/A | 0.29411764705882354 | 46.07941274607941 | 47.04704704704705 |
| linear_interpolation | 17 | N/A | N/A | 1.0 | 46.07941274607941 | 47.04704704704705 |
| constant_velocity | 17 | 0.3718037100975292 | N/A | 1.0 | 46.07941274607941 | 47.04704704704705 |
| kalman | 8 | N/A | N/A | 0.47058823529411764 | 46.37971304637971 | 47.04704704704705 |
| rts | 8 | N/A | N/A | 0.47058823529411764 | 46.37971304637971 | 47.04704704704705 |

Historical exact reproduction: `historical_reproduction.csv`. Exact input positions, velocities, timestamps and observation status: `reconstruction_inputs.csv`. PET uses 0.5 learned-unit shared cells and occupancy spans split at gaps >0.20 s; no sub-frame entry/exit interpolation. TTC sweeps road-aligned rectangles with constant velocity/orientation over 5 s; pedestrian 0.7×0.6 and car 4.5×1.8 learned-unit dimensions are assumptions, not calibrated physical footprints. No crossing lateral-passing clearance is reported.

Manual car clicks and sensitive car68 detector bottom-centres have three identical-frame comparisons: **29.14, 37.61 and 72.69 px** differences. These compare different contact proxies and do not validate reconstruction accuracy. The car track ends at one-based frame **1395** (clip +46.513 s); later manually reconstructed positions are not automatic observations. Approximate image speeds over the saved pre-loss/subject context windows are in `object_speed_context.csv`, with units and frame windows; road speed is unavailable.

## Before and after

| event | previous | repaired | why | status |
|---|---|---|---|---|
| white_suv | 0 strict eligible pairs; pass omitted by geometry gate | retained visual interaction candidate; metre/TTC/PET N/A | candidate identity separated from physical metric eligibility | observed selected pass; exploratory speed |
| dark_car | 0 strict eligible pairs; pass omitted by geometry gate | retained visual interaction candidate; metre/TTC/PET N/A | candidate identity separated from physical metric eligibility | observed selected pass; exploratory speed |
| pedestrian_car | reported PET .294 s; CV TTC .375 s | PET N/A; historical CV TTC 0.374530 s; frame-aligned CV TTC 0.371804 s conditional | .294117647 is coverage 5/17, not PET; frame time replaces click playback time; filtered endpoint clamping removed | reconstructed diagnostic, physical validity unverified |

Both cyclist pairs have actual synchronized tracks, **58 and 98** shared observations, all same-direction under the existing learned-plane test, **zero alongside samples and zero supported shared samples**. The assumed rectangles around projected detector bottom-centres reject the visual passes; this is geometric eligibility failure, not a blanket tracking failure. `edge_proxy_comparison.csv` shows how annotated visible edges differ from detector box proxies; white-SUV selected frame 409 lacks a simultaneous saved vehicle point despite the manually visible edge, a local observation gap distinct from the pair-wide geometry rejection. The alongside limit is **3.15 learned units**; fitted along-track offsets range **−18.803 to −5.817** (white SUV) and **−21.874 to −4.105** (dark car), so neither reaches the assumed overlap interval. These are diagnostic coordinates, not validated metres. Gates are preserved for physical metrics while evidence-based candidates survive.

## Conditional sensitivity (seconds)

| method | metric | eligible_scenarios | scenario_count | minimum_s | maximum_s |
|---|---|---|---|---|---|
| constant_velocity | min_ttc_s | 16 | 16 | 0.34769660340290454 | 0.3981078045921077 |
| constant_velocity | pet_s | 0 | 16 | N/A | N/A |
| kalman | min_ttc_s | 0 | 16 | N/A | N/A |
| kalman | pet_s | 0 | 16 | N/A | N/A |
| linear_interpolation | min_ttc_s | 2 | 16 | 0.024225303574851028 | 0.030631229442697527 |
| linear_interpolation | pet_s | 1 | 16 | 0.0 | 0.0 |
| manual_observed | min_ttc_s | 2 | 16 | 0.024225303574850636 | 0.03063122944269728 |
| manual_observed | pet_s | 1 | 16 | 0.0 | 0.0 |
| rts | min_ttc_s | 0 | 16 | N/A | N/A |
| rts | pet_s | 0 | 16 | N/A | N/A |

Sixteen one-factor scenarios include car-click offsets ±3 px, frame-time shifts ±1 frame, dimension factors 0.8/1.2, lateral mapping factors 0.8/1.2, constant-velocity acceleration perturbations ±2 learned units/s², first-half fit, and PET cells 0.25/1.0. These are explicit engineering assumptions, not empirically calibrated uncertainty or real-world near-miss probabilities. PET may appear only under changed assumptions; missing values are retained. See `sensitivity_metrics.csv` for each row and `sensitivity_summary.csv` for conditional ranges. Automatic/manual car comparison has no permission to compare points at different times; see `manual_auto_comparison.csv`. The automatic track-loss span is explicit in `occlusion_observations.csv`. Reference car68 is an unrelated late track; the relevant car68 namespace is sensitive. Saved pedestrian CSV clocks incorrectly read 12:08 while the source manifest identifies 17:08; frame times drive calculations and filename-inferred source times drive this report. Visual inspection of pedestrian source frame 1405 shows burned-in camera clock **17:08:49**, whereas nominal manifest+frame timing gives **17:08:46.847**. Selected cyclist frames also have nominal/burned-in clock disagreement (white frame 391: 12:40:21.013 versus 12:40:23; dark frame 445: 12:53:52.815 versus 12:53:54). Absolute clock alignment is therefore unresolved (not a validated 2.153 s correction, because the burned-in label is second-resolution). Relative TTC calculations do not use these absolute clock labels. See `clock_alignment_audit.csv`.

## Aggregate counts and screening

| metric | value | denominator | reason |
|---|---|---|---|
| unique_candidate_encounters | 3 | 3 reviewed interactions | 2 real cyclist passes + 1 pedestrian crossing; variants collapsed using explicit visual event IDs |
| visually_verified_passes | 2 | 3 | Selected pilot, not a population rate |
| visually_reviewed_crossings | 1 | 3 | Prior review evidence; partly occluded |
| eligible_physical_ttc | 0 | 3 | Eligibility and units in event_metrics.csv |
| eligible_physical_pet | 0 | 3 | Eligibility and units in event_metrics.csv |
| image_diagnostic | 3 | 3 | Eligibility and units in event_metrics.csv |
| calibrated_metre_clearance | 0 | 3 | Eligibility and units in event_metrics.csv |
| conditional_surrogate_ttc | 1 | 3 | Eligibility and units in event_metrics.csv |
| reproduced_surrogate_pet | 0 | 3 | No shared assumed-footprint occupancy cells; historical .294 was coverage |
| potential_conflict | 1 | 3 | Pedestrian: prior visible close interaction, no calibrated safety adjudication |
| confirmed_under_defined_protocol | 0 | 3 | No validated adjudication rule; zero confirmed does not establish no near misses occurred |
| indeterminate | 2 | 3 | Cyclist passes established; near-miss status indeterminate |
| reviewed_false_car_detections | 1 | 1 specifically reviewed wheel alarm | Track 21 sensitive namespace; selected false-positive regression, not population false-alarm rate |
| middle_cyclist_no_pass | 1 | 1 reviewed comparison sequence | Not an event row |
| historical_diagnostic_rows | 47 | 6 detector tasks | Repeated scenarios, not physical events |
| missing_min_clearance_m | 2 | 3 | not_calibrated: lateral scale unverified; outside support; unreliable physical footprint |
| missing_min_clearance_m | 1 | 3 | not_calibrated: scale/footprints unverified; crossing is not lateral passing |
| missing_ttc_s | 2 | 3 | not_applicable: no collision course in assumed-plane model; physical model unvalidated |
| missing_ttc_s | 1 | 3 | failed_eligibility: surrogate model uses unvalidated mapping and assumed dimensions |
| missing_pet_s | 2 | 3 | not_observable: no established shared physical conflict region |
| missing_pet_s | 1 | 3 | failed_eligibility: no shared occupancy cells; historical 0.294 is coverage fraction |
| supported_ttc_s_below_0.25 | 0 | 3 | No eligible physical times; conditional surrogate flags listed separately |
| conditional_surrogate_ttc_s_below_0.25 | 0 | 1 | Engineering example only, not confirmed near miss |
| supported_ttc_s_below_0.375 | 0 | 3 | No eligible physical times; conditional surrogate flags listed separately |
| conditional_surrogate_ttc_s_below_0.375 | 1 | 1 | Engineering example only, not confirmed near miss |
| supported_ttc_s_below_0.5 | 0 | 3 | No eligible physical times; conditional surrogate flags listed separately |
| conditional_surrogate_ttc_s_below_0.5 | 1 | 1 | Engineering example only, not confirmed near miss |
| supported_pet_s_below_0.25 | 0 | 3 | No eligible physical times; conditional surrogate flags listed separately |
| conditional_surrogate_pet_s_below_0.25 | 0 | 0 | Engineering example only, not confirmed near miss |
| supported_pet_s_below_0.5 | 0 | 3 | No eligible physical times; conditional surrogate flags listed separately |
| conditional_surrogate_pet_s_below_0.5 | 0 | 0 | Engineering example only, not confirmed near miss |
| supported_pet_s_below_1.0 | 0 | 3 | No eligible physical times; conditional surrogate flags listed separately |
| conditional_surrogate_pet_s_below_1.0 | 0 | 0 | Engineering example only, not confirmed near miss |

Default numerical screening thresholds are **unset** (`pipeline/near_miss_screening.json`). Visual evidence retains these candidates. No fixed metre screen is enabled. The time thresholds in `threshold_sensitivity.csv` are labeled engineering examples only, with strict `<` comparisons. Changing settings changes screening fields only, never reviewed labels. Conditional surrogate flags are distinct from supported flags. Review labels use `indeterminate` for the two real passes and `potential_conflict` for the close pedestrian crossing based on prior visual evidence; no validated confirmation rule or evasive-action finding is asserted. Track 21 is excluded as a false car on a wheel; the middle cyclist is excluded as a no-pass comparison. The 47 historical scenario rows are not 47 events.

## Visuals and trace

![White SUV selected closest annotated edge frame](assets/white_suv_selected_frame.jpg)
![Dark car selected closest annotated edge frame](assets/dark_car_selected_frame.jpg)
![Pedestrian closest manual point frame](assets/pedestrian_car_selected_frame.jpg)

![White SUV synchronized trajectory and closest sample](assets/white_suv_trajectory.png)
![Dark car synchronized trajectory and closest sample](assets/dark_car_trajectory.png)
![Pedestrian automatic/manual trajectory and track loss](assets/pedestrian_trajectory.png)
![Available event metrics with missing times marked](assets/event_metrics.png)

Open [interactive review](review.html) for synchronized track boxes, timestamp labels, manual clicks, support hull and occlusion diagnostics. Original cyclist frame review remains at `reports/clearance_pilot/final_review_20261109/review.html`. Full frame/pair rejection tables, selected manual-edge comparisons and source file hashes accompany this report.

## Interpretation and smallest additional evidence

The defensible findings are two real cyclist passes with selected image gaps, and a close pedestrian crossing with automatic car track loss and a reproducible conditional TTC diagnostic. Neither the image proximity nor the reconstructed TTC proves a near miss. PET 0.294 s was a reporting error, not measured occupancy timing. No eligible physical clearance, TTC/PET-based safety rate, or collision probability is established.

To unlock physical clearance, reconcile original recording PTS against the burned-in clock for absolute event timestamps; supply independent road-plane control geometry with image correspondences spanning the cyclist paths and lateral direction, with measurement error, plus reviewed ground/near-side object edges. Existing 35-foot and 30-foot longitudinal zone lengths lack matched image endpoints and do not validate lateral scale. No surveyed width is needed to retain candidates or review video. For pedestrian occupancy timing, identify the same physical conflict region for both objects and label visible contact proxies versus hidden positions; a second view or defensible bounded occlusion model would reduce reconstruction uncertainty. More detector/smoothing variants alone cannot supply missing geometry.

## Reproduction and files

From `/Users/rithika/Desktop/objectDetect`:

```sh
python3 pipeline/generate_near_miss_report.py --repo . --out reports/near_miss
python3 -m pytest tests -q
```

Primary exports: `reports/near_miss/event_metrics.csv`, `summary_metrics.csv`, `PROFESSOR_RESULTS.md`, `review.html`, `CODE_PATH_MAP.md`, `threshold_source_inventory.csv`, `provenance.csv`. Pedestrian saved inputs were copied, unchanged, from `/Users/rithika/Downloads/CLEARANCE_PILOT_20261109_203226_368050/colonial_1708_pedestrian_car_reference/` into `reports/near_miss/inputs/pedestrian/`; matching sensitive exports were also preserved in `inputs/pedestrian_sensitive/`. No inference/GPU work or new video experiment is required. Source evidence hashes were checked before and after generation; all 175 checked files remained unchanged.
