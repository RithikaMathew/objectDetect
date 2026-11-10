# Project handoff — November 9, 2026

## Current status

The speed-analysis batches and the small passing-clearance pilot have completed. We have exploratory speed estimates, two visually reviewed car passes, and a documented false near-miss alarm. **We do not yet have validated physical passing distances or a verified near-miss count. No new HiPerGator job is pending.**

## 1. Cyclist speed: what was done

- Processed the same 18 selected video clips across nine cameras: about 270 minutes.
- Compared study counts, automatic detector/tracker results, and Rithika’s manual cyclist annotations. Counts were **35 study / 32 automatic / 30 manual**; 29 manual encounters had sufficient observations for speed.
- Estimated speed from manual rear-tire clicks and automatic trajectories using a camera mapping learned from cars. Also calculated robust manual fits, endpoint speeds, timing audits and sensitivity scenarios.
- The 18 re-encoded review clips had regular timestamps near 29.97 fps. Original hourly recordings were not independently audited for timing.

The main results and all nine locations are in [manual/README.md](manual/README.md). Important examples: Carroll automatic/manual means were 12.22/12.37 mph; Colonial 7.35/10.71 mph; University 14.00/16.98 mph. These are exploratory comparisons, not verified person-level speed errors.

**Reference distinction:** Mighk’s workbook speeds come from a separate video/stopwatch sample, with half-speed playback already accounted for. They are not linked to the same individual cyclists or exact times. Do not double the supplied mph, fit camera scale to workbook averages, or interpret similar group means as accuracy.

## 2. Passing clearance and near misses: what was done

The professor requested lateral clearance between a cyclist and a passing car as the primary outcome, because true near misses may be rare.

We processed **three 30-second Colonial clips**: 90 seconds of unique footage, with two detector settings. All six tasks succeeded in HiPerGator job **50509198**; report job **50509199** completed. The earlier job 50504800 failed during extraction and produced no usable analysis.

The pilot compared 12 scenarios per detector using:

- Lateral gap between assumed object envelopes, minimum separation and a projected box-edge diagnostic.
- Collision-course time to collision (TTC), closest predicted approach and sampled shared-space post-encroachment time (PET).
- Local trajectory fits, Kalman filtering and offline RTS smoothing.
- Variations in smoothing window, cyclist width, learned scale and calibration-support restrictions.

### What the local visual review found

| Reviewed sequence | Finding |
|---|---|
| First cyclist, around 12:40 | A white SUV visibly passes the cyclist; reference vehicle track 9. |
| Middle cyclist, around 12:53:11 | No nearby passing car in the reviewed manual-click sequence. |
| Third cyclist, around 12:53:50 | A dark car visibly passes the cyclist; reference vehicle track 18. |
| Sole zero-clearance/TTC/PET alarm | Sensitive-detector vehicle track 21 was a box on the cyclist’s front wheel, not a separate car. Exclude this specific false detection. |

This was sampled frame review, not exhaustive safety adjudication. **Do not interpret these findings as proof that the footage contains no near misses.**

## 3. Earlier manual speeds used as a baseline

The clearance clips contain the same three Colonial cyclist sequences previously annotated. We compared automatic speeds over the manual measurement windows, without changing scale:

| Cyclist sequence | Earlier manual path mph | New local-fit automatic mph | Kalman mph | RTS mph |
|---|---:|---:|---:|---:|
| 12:40 | 10.51 | 9.71 | 9.67 | 9.85 |
| 12:53:11 | 10.47 | 9.74 | 10.22 | 10.11 |
| 12:53:50 | 11.15 | 11.52 | 11.52 | 11.27 |

The new local-fit mean is about 10.32 mph versus manual 10.71 mph. Automatic observations cover approximately 90–98% of the manual intervals. The older 7.35 mph Colonial automatic mean used earlier tracks/measurement windows; it is historical context, not a calibration target.

**Both methods use the identical learned camera matrix.** Agreement does not independently verify speed or lateral distance. Some prior manual markers also have uncertain pavement-contact/frame alignment.

## 4. Why physical clearance remains unresolved

- Every observed cyclist contact point is outside the saved car-calibration support hull. This explains the zero strict-baseline pairs; it is not evidence that no cars passed. Outside-hull transfer is unvalidated, not automatically proven wrong.
- The assumed footprint/alongside calculation rejected both visually identified passing pairs. Car boxes and bottom-centers are not reliable physical side/ground footprints.
- The near-side tire/body boundaries are blurry. Prior manual tire points and automatic box-bottom points also differ visibly.
- We inspected **46 workbooks / 141 sheets** and checked saved calibration/gate provenance. Colonial’s recorded 35-foot bike-lane and 30-foot sidewalk distances are longitudinal speed-zone lengths. Their matching image endpoints are unknown. Rithika previously confirmed that the drawn gates marked visible lane ends, not known measured endpoints.
- No verified lateral dimension tied to these frames was identified. A geometric demonstration showed that doubling lateral scale could change the cyclist path speeds by only about 2%; matching speed cannot fix lateral scale.

The raw output has 47 interaction rows across methods/detectors, not 47 independent encounters. All use exploratory support transfer. The separately filtered export excludes the wheel false detection and retains 46 **unverified diagnostic rows**. No physical gap, legal passing-distance compliance, population false-alarm rate or 48-hour event rate is established. The unsourced “84% false alarms” note is not a result of this pilot.

## 5. Files to use

- [Final short summary](reports/clearance_pilot/final_review_20261109/START_HERE.md).
- [Illustrated review: short videos and marked frames](reports/clearance_pilot/final_review_20261109/review.html).
- [Professor-ready paragraph](reports/clearance_pilot/final_review_20261109/PROFESSOR_SUMMARY.txt).
- [Speed comparisons](reports/clearance_pilot/final_review_20261109/speed_baseline_comparison.csv), [reviewed encounters](reports/clearance_pilot/final_review_20261109/reviewed_encounters.csv), and [distance evidence register](reports/clearance_pilot/final_review_20261109/distance_evidence_register.csv).
- [Original returned clearance results](reports/cluster_returns/20261109/CLEARANCE_PILOT_20261109_175030_116203/RESULTS.md).
- [Portable final packet](reports/clearance_pilot/clearance_final_review_20261109.zip).
- [Clearance reproduction guide](docs/CLEARANCE_PILOT_RUN.md) and [speed workflows](docs/SPEED_WORKFLOWS.md). These are not pending jobs.

## 6. Continuing the work

The current-file review is finished. More detector sweeps, larger videos or smoothing variations will not independently establish the missing metric geometry. Physical clearance requires defensible lateral calibration and object-edge/contact positions. Do not substitute nominal lane widths, assumed car dimensions or workbook speed averages as measured truth.

Rithika prefers autonomous follow-through, short explanations and no repeated requests to proceed. Use existing files first; she currently does not want emails to MetroPlan. Keep video experiments at 15 minutes maximum, preferably much shorter. Preserve original workbooks, annotations and returned evidence.

The repository was cleaned: Markdown files were consolidated from 106 to 58 before adding this requested handoff. Historical findings are retained in [detector results](reports/history/DETECTOR_RESULTS.md) and [project notes](reports/history/PROJECT_NOTES.md); historical commands are not current instructions. Data/runtime preservation checks, link checks and 23 relevant tests passed. The [cleanup manifest](reports/maintenance/cleanup_20261109.csv) records the changes and a recovery backup is stored outside the project.
