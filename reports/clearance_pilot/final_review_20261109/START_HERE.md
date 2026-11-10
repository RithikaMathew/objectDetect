# Clearance pilot — final result with current files

**The local pilot review and distance-reference check are finished. No further command or annotation is needed from you for this packet.**

- Two real car passes are visible in the reviewed cyclist sequences.
- The only zero-gap/TTC/PET alarm is a bicycle wheel mistaken for a car.
- **No passing distance in meters is reliable enough to present as a measured result.**

Open **review.html** for the short videos and marked images. **PROFESSOR_SUMMARY.txt** is a ready-to-use methods/results paragraph; it has not been sent anywhere.

## What was completed

1. Processed three 30-second clips under two detector settings; all six tasks completed.
2. Compared 12 geometry/trajectory scenarios per detector, including Kalman and RTS; evaluated lateral gap, minimum distance, collision-course TTC and spatial occupancy PET.
3. Matched the three cyclist sequences to prior manual annotations for exploratory speed comparison without fitting scale to old speeds.
4. Reviewed sampled frame sequences, finer passing frames, manual-click overlays and enlarged car crops; identified white SUV track 9 and dark car track 18, plus the wheel false detection.
5. Read all cell data from 46 study workbooks / 141 sheets (243,531 nonempty cells), preserving candidate source cells and formulas. Checked saved gate provenance, calibration metadata and prior marking checks. Source spreadsheets were not modified.
6. Verified the only Colonial workbook distances are speed-zone lengths: 35ft bike-lane / 30ft sidewalk, with 23 unique records (including the e-bike row retained only in BL Analysis). The drawn gates were explicitly rejected in October as unknown measured endpoint matches. No verified lateral dimension tied to these frames was identified.
7. Saved original and separately filtered results, visual adjudication, calibration-support audit and this self-contained review packet.

## Why the earlier speed baseline cannot fix clearance

Manual and automatic speeds use the same learned map. Agreement does not independently check scale. A geometric sensitivity demonstration that keeps longitudinal scale fixed while doubling lateral scale changes these cyclist path speeds by at most about 2.1%. It changes lateral distances by a factor of two. This illustrates why nearly matching speeds do not constrain lateral clearance. The demonstration is not a new calibration or estimated uncertainty interval.

## What the professor can use

The method comparison, two reviewed passing-event sequences, and the specific detector false alarm can be reported as a feasibility pilot. Distances remain exploratory model outputs, not validated measurements. No absence of all near misses, population false-alarm percentage, legal passing-distance compliance or 48-hour event rate is established.

## What is unresolved

A trustworthy lateral geometry/scale and defensible cyclist/car outer edges are not established by the current files. The exact pavement contact/frame alignment of some prior manual markers is also uncertain. Extra detector sweeps or smoothing cannot establish these missing references. This is a data/geometry limit, not a pending HiPerGator job. No email, new account access or external measurement was requested or performed.

## Evidence and reproducibility

- distance_evidence_register.csv and colonial_workbook_distances.csv: source decisions and exact original cells.
- workbook_inventory.csv and workbook_distance_candidates.json: read-only workbook inventory/hashes and candidate context, not automatic measurement approval.
- reviewed_encounters.csv, contact_point_checks.csv, reviewed_pair_model_diagnostics.csv: reviewed events, overlays and diagnostic model failures.
- speed_baseline_comparison.csv and calibration_support.csv: same-window speed comparisons and support checks.
- review_labels.csv and false_alarm_review.csv: the single adjudicated false flag with unreviewed cases retained.
- interactions_excluding_reviewed_wheel_false_detection.csv: 46 remaining diagnostic rows, not 46 independent or verified events.
- original_run_manifest.json and prior_gate_rejection.json: model/run settings and preserved prior provenance.

Original full cluster results are retained under reports/cluster_returns/20261109/CLEARANCE_PILOT_20261109_175030_116203/. The repository preview shares the three preserved original videos through relative links; no cluster access is needed. The portable ZIP includes copies for standalone viewing.
