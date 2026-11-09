# Clearance pilot local validation — November 9, 2026

Prepared for the existing HiPerGator project. Kalman/RTS smoothing and distance/PET screening comparisons are included. No cluster jobs were submitted and no real-world metric clearance or near-miss counts are claimed.

Commands passed:

```bash
python3 -m unittest discover -s vision3/best/test_colonial/code -p 'test_clearance_pilot.py'
python3 -m unittest discover -s tests -p 'test_passing_clearance.py'
python3 -m py_compile vision3/best/test_colonial/code/clearance_pilot.py vision3/best/test_colonial/code/clearance_metrics.py
bash -n vision3/best/test_colonial/code/clearance_pilot.slurm
```

18 pilot tests and 4 reviewed-footprint tests passed. The pilot tests cover analytic geometry, observation gaps, coast rejection, support transfer, synthetic export-to-report processing, preservation of a user review file, Slurm GPU/afterany CPU submission with a mocked scheduler, and real FFmpeg extraction/FFprobe frame timing. The mocked job IDs in test output are not actual scheduled jobs.

Analytic fixture: a cyclist moves at 2 m/s, a car at 6 m/s from 6 m behind, with center paths 3 m apart. Assumed widths of 0.8 m and 1.8 m give lateral clearance 3−0.4−0.9 = 1.7 m. The calculator returns 1.7 m, observed overtaking-order reversal, no collision-course TTC, and no shared-space occupancy PET. A direct closing collision fixture with 10 m separation, closing speed 5 m/s and combined half-length 3 m returns TTC 1.4 s. These are synthetic algorithm checks, not validation against field measurements.

Visual input check: the existing short Colonial optical-flow review videos were inspected as a contact sheet. Cyclist/car co-occurrences appear around 12:40:23 and 12:53:54. The 12:53:13–17 cyclist sequence supplies a comparison window without presuming a passing vehicle. Optical-flow tracking had failed earlier drift checks, so those overlays supply encounter-selection evidence only; they do not supply trajectories, ground truth, speed or metric clearance in the new run. Inference reads fresh 30-second crops of the original raw source on HiPerGator.

Not exercised here: cluster Slurm policies, GPU inference, cached model loading in yolo_env, current availability of the raw Colonial source on the cluster, or validation of learned metric scale and assumed footprints. Missing assets and numerical/support failures are reported explicitly.

Read [the run guide](../../docs/CLEARANCE_PILOT_RUN.md) for the one-line submission and interpretation.

Additional checks use seeded noisy linear trajectories to verify that RTS reduces position error against a known synthetic path, verify independent resets across observation gaps and rejection of duplicate timestamps, and verify that false-flag fractions remain blank until reviewed labels exist. Zero-valued distance/PET flags and adjudication coverage are checked explicitly. No claim is made that smoothing improves performance on actual encounters before cluster results and review.

The synthetic export integration also exercises CPU-only reanalysis, preservation of prior analysis tables under analysis_history, and preservation of existing review labels.

Extraction repair checks cover supported synchronization option selection for old/new FFmpeg help formats, detailed stderr propagation into extraction diagnostics, partial-output cleanup, and real clip extraction/frame-timing verification. The exact cause of cluster job 50504800's FFmpeg failure is unconfirmed because the supplied report omitted stderr.
