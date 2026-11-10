# Short clearance pilot: one HiPerGator submission command

This run uses existing files only. No email, new field measurements, new trained models, or manual inputs are required to launch. It reuses the existing fine-tuned RT-DETR + X-CLIP/ByteTrack pipeline and the saved Colonial learned calibration. The output is exploratory clearance and interaction estimates requiring review, not verified near misses.

## Submit

**Completed:** the pilot, local review and distance-reference audit are saved in the final packet linked from the project README. No rerun is required. To reproduce intentionally after syncing with Git, use:

```bash
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial && source /orange/xiangyan/rithika/vision/yolo_env/bin/activate && python code/clearance_pilot.py submit --go
```

This submits one GPU job plus a small CPU report job using `afterany`, so a report is generated even if GPU processing times out or fails. No full-hour speed jobs or old experiment batches are submitted. Each new invocation creates a separate run; submit once and retain its printed job IDs/results path. Without `--go`, it prints the plan and does not submit. Queue delay and GPU runtime are unknown; the GPU job requests a maximum two hours, not a prediction that it takes two hours.

## Fixed short windows

| Colonial source playback | Approximate inferred clock | Duration | Existing evidence |
|---|---|---|---|
| 2408–2438 s | 12:40:08–12:40:38 | 30 s | Manually clicked cyclist; local review shows cyclist and adjacent white car around 12:40:23 |
| 3179–3209 s | 12:52:59–12:53:29 | 30 s | Manually clicked cyclist, useful comparison/control encounter |
| 3218–3248 s | 12:53:38–12:54:08 | 30 s | Manually clicked cyclist; local review shows cyclist and adjacent dark car around 12:53:54 |

Total: **90 seconds unique footage**, processed under two detector settings (**180 seconds detector input**). The source is the existing original Colonial `Standard_SCU8OG_2019-07-10_0000.013.mp4` under `pilot_clips/MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/Standard_SCU8OG_2019-07-10_0000/`. Only the three crops are decoded for inference. FFmpeg seeks into the larger source; no whole-source inference or archive scan occurs. Existing optical-flow overlays were inspected to select encounters; annotated overlays are not used as model inputs. Source clocks are filename inferred; original embedded clock and source timing are not independently verified. The crop timestamps are audited before inference. A completed overtake or near miss in a window is not presumed.

## Methods and variations

| Output | Meaning |
|---|---|
| `min_sampled_clearance_m` | Primary: lateral edge gap of assumed metric envelopes while longitudinally alongside |
| `min_box_edge_proxy_m` | Projected lower box-edge interval gap; image-derived diagnostic, not physical object edges |
| `min_footprint_distance_m` | Minimum 2-D edge distance between assumed road-aligned rectangles, including non-alongside encounters |
| `min_center_distance_m` | Simultaneous projected contact-point separation |
| `min_collision_ttc_s` | Constant-velocity swept-rectangle collision-course TTC, up to 5 seconds; separated parallel passes have no TTC |
| `min_predicted_center_distance_m` | Closest predicted contact-point approach within 5 seconds |
| `sampled_occupancy_pet_s` | Time between assumed footprints occupying the same raster cell; 0.5 m grid and observed timestamps |

Every window has a reference and a sensitive detector run. Each uses twelve CPU scenarios: baseline; 0.25 or 1.0 s smoothing/velocity windows (baseline 0.5 s); 0.6 or 1.0 m cyclist widths (baseline 0.8 m); scale factors 0.8 or 1.2 (baseline 1.0); exploratory support transfer instead of strict contact-point support; and Kalman filtering / RTS smoothing each under strict and transfer support. These are **24 detector/scenario combinations per window**, using one-factor-at-a-time tests to keep work bounded. Several metrics share the same inference, avoiding separate GPU runs per metric.

The reference configuration retains the established SAHI and classification rules with 1.5 s minimum cycling count duration. Both runs shorten the stitch window to 0.5 s/60 px and tracker loss buffer to 0.3 s for interaction analysis. The sensitive run lowers detector/tracker thresholds from 0.25 to 0.15, lowers count duration to 0.3 s and disables static rejection. It is an experimental comparison, not a copy of historical count results. Classification-backed and detector-backed cyclist candidates rejected by counting can still be analyzed, with identity/count status retained.

Threshold screening compares clearance cutoffs of 0.5/1.0/1.5 m, TTC cutoffs of 1.0/1.5/2.0 s, and PET cutoffs of 0.5/1.0/1.5 s. These are sensitivity screens, not legal thresholds or validated cyclist near-miss definitions. IDs and people overlap across detector/scenario variations; do not sum these rows as independent events. No method is selected because it produces more near misses or agrees with workbook speeds.

Kalman and RTS use a constant-velocity state `[x,y,vx,vy]`, variable observation intervals, assumed observation standard deviation 0.25 m and acceleration standard deviation 2 m/s² in the learned metric plane. RTS runs an offline backward pass within each continuous track segment. Both restart at gaps over 0.20 s, discard the first 0.10 s / fewer than three observations of each segment, and emit observed frames only. Initial velocity is zero with 5 m/s standard deviation. The noise assumptions scale with the metric sensitivity factor; they are not inferred calibration uncertainties. The local-fit `window` parameter is unused by Kalman/RTS. Smoothing can suppress genuine evasive movement and cannot fix wrong identities, geometry or assumed dimensions.

Additional comparisons screen minimum 2-D assumed-footprint distance <1 m and sampled occupancy PET <1 s separately, with AND and OR combinations. Lateral clearance <1 m remains a separate primary-outcome screen. These cutoffs are explicit engineering screens, not published optimal prediction rules. Missing PET is retained as unavailable rather than zero. No claim is made that distance/PET predicts near misses best on this dataset.

The user supplied an unsourced note that 84% of flags were false alarms. The exact study and denominator could not be verified; it is not this pilot's measured false-alarm rate and is not used to set thresholds. After review, `false_alarm_review.csv` computes false flags / adjudicated flags with adjudication coverage and unreviewed flags retained. This fraction differs from a false-positive rate among actual negative encounters. Do not pool variants or extrapolate this selected reviewed subset. The pilot uses video only; no LiDAR or radar measurements are synthesized.

## Results

Download the printed `exp_results/CLEARANCE_PILOT_<tag>/` directory. Start with:

- `RESULTS.md`: task states, interpretation, assumptions and limitations.
- `review.html`: original-view 30-second videos, candidate snapshots and metric values. Uses baseline pairs where available; otherwise labels exploratory transfer explicitly.
- `all_interactions.csv`: every eligible pair/scenario with IDs, facilities, source-relative times and inferred clocks.
- `threshold_sensitivity.csv`: threshold counts and their eligible denominators.
- `smoothing_comparison.csv`: Kalman/RTS versus local-fit baseline, matched by pair IDs and support setting.
- `screening_comparison.csv`: distance, PET, AND/OR, and lateral clearance screen counts.
- `false_alarm_review.csv`: reviewed false-flag fractions and coverage; blank until adjudication exists.
- `task_status.csv`, `status.json`, `slurm_<job>.log`: completion/failure diagnostics. The report finalizer exposes missing final status after termination.
- `review_candidates.csv`: generated review template. Copy it to `review_labels.csv` before editing. It updates as tasks complete; your review file is preserved.

Each task contains `interactions.csv`, baseline, transfer and `kalman_rts_timeseries.csv` time series (including projected positions), copied raw cyclist/vehicle trajectories, calibration geometry, snapshots, the run log and the inference log. `inputs/` contains three short videos with frame-timing audits and SHA-256 hashes. Source size/mtime, model/calibration hashes, task parameters and model paths are recorded. Original annotated pipeline outputs remain at the paths in the run logs; the self-contained review pack uses the short original-view crops instead.

To adjudicate flags, copy `review_candidates.csv` to `review_labels.csv`, fill `near_miss_review` with `yes` or `no` only after reviewing the encounter, and supply `reviewer`. Uncertain or blank judgments remain unadjudicated. Conflicting labels for the same task/cyclist/vehicle are ignored pending resolution. Labels describe the physical encounter and apply to its smoothing scenarios; distinct detector tracks still need independent identity matching. Regenerate reports with the report command below to calculate reviewed false-flag fractions. No detection rerun is needed for report regeneration.

If a GPU task is killed, the finalizer can mark it `RUNNING`/`NO_FINAL_STATUS`; this means incomplete, not zero interactions. If finalizer submission fails, the GPU job is already submitted: do not resubmit the whole pilot. Regenerate the report with `python code/clearance_pilot.py report <printed-results-directory>` after checking that the GPU job has ended.

## Interpretation

The existing calibration is learned from cars and is not independently validated metric geometry. Bottom-center contact points are approximate. Rectangular envelope dimensions are assumptions: bicycle/rider 1.8 m long and 0.6–1.0 m wide; car 4.5×1.8 m; truck 8×2.5 m; bus 12×2.5 m. They are centered on projected bottom-center points, which need not be true vehicle centers. Width/scale variations show sensitivity, not calibrated uncertainty bounds. Do not treat box bottom edges as true ground-plane silhouettes or interpret projected vertical corners as physical widths.

All facilities are retained when the pipeline supplies a label. Sidewalk/sidepath plane transfer is unverified; car hull membership alone does not establish coplanarity or reliable footprint edges. Existing lane polygons and type/identity assignments require review. Occlusion, temporal fragmentation, vehicle dimensions, barrier separation and clipped events can dominate differences. Velocities never bridge observation gaps above 0.20 s. The fixed road axis assumes locally straight parallel movement; lane changes and curves need additional geometry. Sampled clearance can exceed the continuous-time minimum. PET rasterization can create false shared space and its timing is sampled. Zero gap, TTC or PET is model overlap, not a verified collision.

Review the car passing the cyclist, same-direction status, actual envelope edges, continuity and event boundaries before deciding which encounters support clearance reporting. There is no automatic `verified_near_miss` output. No full 48-hour exposure or event rate is inferred.

## Research basis and validation

[FHWA's TTC/PET definitions](https://www.fhwa.dot.gov/publications/research/safety/08051/02.cfm) distinguish projected collision time from successive occupancy of a common location. Our swept-rectangle and raster occupancy routines implement those concepts with explicit approximations. [Liu, Saunier and Bilodeau (2025 preprint)](https://arxiv.org/abs/2503.09807) found the tested automated methods could overestimate interactions and underestimate TTC; this supports identity/geometry review and method sensitivity. The existing calibration comes from an adapter to the [ICCV2021 author implementation](https://github.com/naver/cctv). These are custom paper-informed methods, not a claimed latest-model benchmark reproduction.

Local verification covers known parallel-pass gaps, collision-course versus separated trajectories, order reversal, support transfer, no interpolation across gaps, shared-space PET, coasted observations, synthetic CSV-to-report processing, mocked Slurm submission and real FFmpeg extraction/timing. GPU inference and actual HiPerGator scheduler execution have not been run locally. The cluster needs its existing working `yolo_env`, cached X-CLIP assets, fine-tuned weights, raw Colonial source and FFmpeg/FFprobe. Missing resources produce explicit failure reports; no new model is downloaded by this workflow.

RTS reference: [Investigation on road traffic safety in rural areas using trajectory data](https://tsr.international/TSR/article/download/27904/24728?inline=1) applies RTS smoothing in its trajectory preprocessing. Our constant-velocity implementation and noise settings are custom; no reproduction of that study or its sensor suite is claimed.

If you already completed the earlier version of this pilot, pull the updated source with Git after that job ends and reuse its saved raw exports. From `test_colonial`, submit a CPU-only analysis update (replace the results path with the actual printed directory):

```bash
sbatch --gpus=0 --mem=8G --time=00:30:00 --output=clearance_reanalysis_%j.log code/clearance_pilot.slurm /absolute/path/to/CLEARANCE_PILOT_existing reanalyze
```

This adds the new method/scoring tables without GPU detection. Previous per-task analysis tables and statuses are preserved under `analysis_history/`; raw exports and your `review_labels.csv` remain intact. Only tasks with all required raw exports are reanalyzed. Do not run this against an active pilot directory.




## Sync to HiPerGator

The current pilot and local review are complete. No new job is pending. For an intentional reproduction, sync the relevant committed files with Git, activate the existing yolo_env, and use the submission command above. Do not rerun old detector batches simply because this guide lists reproduction commands. Model weights and original source videos must already be on the cluster; Git does not transfer them.

```bash
cd /orange/xiangyan/rithika/vision
git pull --ff-only origin main
source yolo_env/bin/activate
```

## Reviewed footprints interface

`pipeline/passing_clearance.py` is a separate calculator for reviewed metric footprints, not a raw-video extractor. CSV columns: source_id,track_id,class,t,s_min,s_max,l_min,l_max,facility,calibration_id,geometry_reviewed. Road-aligned bounds must be meters; geometry_reviewed must be yes. Calibration JSON requires source_id, calibration_id, units=m, axes=road_aligned, reviewed=true and evidence. It reports sampled lateral edge gaps for simultaneous longitudinally overlapping footprints, with passing identity still requiring review.

```bash
python3 pipeline/passing_clearance.py footprints.csv --calibration calibration.json --out clearance.csv
```

## Local validation

The local validation covers analytic pass/collision geometry, PET shared-space occupancy, support transfer, gap resets, Kalman/RTS behavior, synthetic CSV-to-report processing, mocked Slurm submission, extraction diagnostics and real FFmpeg timing. The final current-file packet additionally verifies workbook source cells, artifact checksums and all linked media. Cluster job 50509198 completed all six tasks. The prior failed extraction run produced no detection data. These checks do not establish physical clearance accuracy.
