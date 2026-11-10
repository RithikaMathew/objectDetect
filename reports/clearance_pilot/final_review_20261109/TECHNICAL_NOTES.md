# Clearance audit details

Earlier audit and visual review notes are consolidated here. START_HERE.md is the short current conclusion.

## Contents

- [RESULTS.md](#returned_audit_20261109)
- [RESULTS.md](#reviewed_passes_20261109)

<a id="returned_audit_20261109"></a>
## RESULTS.md
Original location: `reports/clearance_pilot/returned_audit_20261109/RESULTS.md`.

# Returned clearance pilot audit — November 9, 2026

All six cluster tasks completed. This audit reads the original downloaded exports; original results remain unchanged in reports/cluster_returns/20261109/CLEARANCE_PILOT_20261109_175030_116203/. No additional GPU job was run.

## Main findings

- Every observed cyclist contact point in all six detector tasks is outside the saved car-calibration support hull (0% supported). The manual rear-tire clicks are also outside it. This explains the zero strict-baseline pairs; it is not a detector failure or evidence that no cars passed.
- All 47 interaction rows use exploratory support transfer: 19 local-fit, 14 Kalman and 14 RTS. They repeat pairs across methods and detector settings and are not 47 independent encounters. Metric clearance is not independently validated.
- The sole row with zero clearance, TTC and PET is colonial_125350_sensitive / cyclist 1 / vehicle 21 / strict_False. Visual inspection of its saved snapshot shows that the supposed car is the cyclist’s front wheel. This is a detection false alarm, not a real cyclist–car near miss. The specific exclusion and evidence are preserved separately.
- This spurious pair has five simultaneous observations spanning 0.133 seconds. It is absent from Kalman/RTS outputs because their warmup leaves fewer than three usable simultaneous samples. This absence does not establish that smoothing correctly detected the false object.
- The current automatic facility label is sidewalk for all three candidates, but the visual position and rear-tire versus box-bottom definitions need review. Do not adopt that label as confirmed facility truth.

## Speed baseline from the prior manual work

The same three annotated encounters are present. The earlier manual calibration matrix is numerically identical to the clearance run’s matrix (maximum coefficient difference 0). The manual and automatic estimates share scale uncertainty. These are within-encounter comparisons over the earlier manual time windows, not independent speed-accuracy tests. We did not fit or rescale any method to the old speeds.

| Encounter | Manual path mph | Prior robust manual mph | Local-fit automatic mph | Kalman mph | RTS mph |
|---|---:|---:|---:|---:|---:|
| 12:40 cyclist | 10.51 | 10.29 | 9.71 | 9.67 | 9.85 |
| 12:53:11 cyclist | 10.47 | 10.43 | 9.74 | 10.22 | 10.11 |
| 12:53:50 cyclist | 11.15 | 11.58 | 11.52 | 11.52 | 11.27 |

Automatic estimates retain only observed trajectory frames within each manual measurement window; coverage is approximately 90–98% (see speed_baseline_comparison.csv for actual spans). The manual path and robust values use the original complete click intervals. One candidate per window and matching source times support a comparison, but person identity, contact definition and exact frame alignment are not independently established. Do not report these differences as person-level speed error.

The prior Colonial group means were manual 10.71 mph and older automatic 7.35 mph. The 7.35 mph came from a different earlier track/window estimator and is historical context; it is not the target speed for new tracks. The new local-fit automatic estimates over the manual windows average about 10.32 mph. Similarity does not validate the shared physical scale.

## Clearance interpretation

The smallest local-fit non-wheel clearance estimates are approximately 1.81 m (first window, reference detector) and 1.34 m (third window, reference detector). Their saved minimum snapshots are at distant positions outside the calibration hull, and dimensions/ground contacts are assumed. These values are diagnostic only; do not present them as measured passing clearances or compare them with legal limits. The second window produced no eligible interaction estimates. That does not establish absence of all interactions.

false_alarm_review.csv describes the single manually adjudicated flag. It is a reviewed-subset fraction, not a population false-positive rate or validation of the user-supplied 84% claim. The filtered CSV excludes only the specifically reviewed wheel false detection; all other rows remain unreviewed, not confirmed real events.

## Files

- speed_baseline_comparison.csv: all six tasks and three smoothing methods, prior encounter IDs, exact windows, speeds and coverage.
- calibration_support.csv: support fractions and equality of earlier/new calibration matrices.
- manual_automatic_position_offsets.csv: approximate same-time rear-click versus box-bottom offsets; not identity/accuracy labels.
- review_labels.csv and false_car_is_cyclist_wheel.jpg: specific visual false-alarm decision and evidence.
- false_alarm_review.csv / screening_comparison.csv: raw-screen review accounting with missing/unreviewed denominators retained.
- interactions_excluding_reviewed_wheel_false_detection.csv: separately filtered 46-row diagnostic export.

## Next step

Use the manual rear-tire points as the cyclist contact baseline and inspect the passing car’s ground-plane contact and visible side boundary in the same frames. This can be done locally from the three downloaded clips, without another detector sweep. A physically interpretable clearance estimate additionally needs defensible lateral geometry/scale for those positions; the existing learned map and assumed vehicle centers do not establish it. Do not increase HiPerGator video volume to address this geometry problem.

Reproduce the speed/support audit in a new output folder:

```bash
python3 vision3/best/test_colonial/code/audit_clearance_baseline.py --batch reports/cluster_returns/20261109/CLEARANCE_PILOT_20261109_175030_116203 --out reports/clearance_pilot/new_baseline_audit
```

The explicit visual adjudication is recorded separately in review_labels.csv; the generic audit script does not invent review labels.


<a id="reviewed_passes_20261109"></a>
## RESULTS.md
Original location: `reports/clearance_pilot/reviewed_passes_20261109/RESULTS.md`.

# Local review: plain-language result

- Two clear same-direction car passes are visible in the reviewed cyclist sequences: white SUV in the first clip and dark car in the third.
- No nearby car passes in the reviewed manual-click interval of the middle clip. This is a comparison sequence, not a claim about the entire site or all 30 seconds.
- The sole zero-clearance/TTC/PET alarm was a car detection on a bicycle wheel. It is a false object.
- **No physical passing clearance in meters is ready to report.** Existing values remain exploratory model estimates.

[Open the illustrated review](review.html). Green = existing manual rear-tire points; yellow = automatic bottom-center; blue = car detection box. Original annotation files and cluster returns were not changed.

## What was checked

The review inspected half-second frame sequences from +11.0 to +16.5 seconds of each short clip, finer passing frames around +13 seconds (white SUV) / +14.8 seconds (dark car), and enlarged vehicle crops. This is sampled visual review, not a full-frame exhaustive safety adjudication. Before/after frames show the two overtakes. The middle interval has no nearby passing vehicle. Near-miss severity is not established from these observations.

The previously annotated reference points (intended rear-tire contacts) were interpolated only between existing clicks and placed on exact decoded frames. Some green markers do not land precisely on the visible pavement contact in these new frames; contact choice and alignment remain uncertain, so they are a reference for comparison, not verified ground truth. A yellow box-bottom point can sit ahead of/below the clicked rear contact; it must not silently replace that tire point when estimating a physical gap. See contact_point_checks.csv for actual image offsets.

Both reviewed passing cars are in the reference detector outputs: white SUV track 9, dark car track 18. The current modeled alongside gate returns zero alongside samples for each, even though their passing sequence is visible. That is a geometry/footprint failure, not proof that the pass did not occur. reviewed_pair_model_diagnostics.csv preserves these outputs as diagnostics, not measurements.

Vehicle crops are too blurry to mark reliable near-side tire/ground/body edges. All cyclist tire points also lie outside the car-calibration support region. Membership outside the hull alone does not prove the mapping wrong, but it makes transfer unvalidated. A bounding rectangle is not the physical car side; assumed dimensions and projected contact centers do not resolve it. The manual and automatic speeds use the same learned matrix, so matching speeds cannot independently validate clearance geometry.

## What is usable

- Visual evidence that two actual cars pass the cyclists in these selected sequences.
- The prior manual cyclist contacts as a reference for cyclist image position and the existing exploratory speed comparison.
- The specific bicycle-wheel false detection as an exclusion with image evidence.

## What is not usable yet

- Meter-valued passing gaps as measured physical clearances.
- Automated near-miss counts or false-alarm rates for the site.
- Comparing Kalman/RTS output counts as proof of improved safety accuracy.

## Next action

No additional GPU processing is indicated. Within the current files, the defensible deliverable is this reviewed passing-event evidence and diagnostic report. To turn it into physical clearance, a trusted lateral road-plane scale/geometry and visible or otherwise defensible car/cyclist outer edges are still needed. The current files do not establish those. Do not substitute the old speed mean or nominal lane/car widths as ground truth.

