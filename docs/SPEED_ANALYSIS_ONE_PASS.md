# One-pass bicycle speed analysis

The first local run is complete: [results](../manual/speed_analysis_20261026/RESULTS.md). It processed 30 annotated encounters across nine cameras, produced estimates for 29, and audited all 18 annotated review clips. One Edgewater encounter remains excluded because its span is only 1.4 seconds. No original annotation or previous result was replaced.

This pass includes time-aware robust trajectory fitting (Huber regression plus Theil–Sen slope), old path and endpoint comparisons on identical annotations, a video packet timestamp audit, 29 trajectory plots, and Monte Carlo sensitivity ranges. The fit is a project implementation, not a complete reproduction of a published paper.

The timestamp audit checks presentation packet timestamps in the re-encoded review clips. All 18 local clips had regular ~29.97 fps timestamps. It does not verify the original hourly recording's timing, frame-accurate manual seeking, or the burned clock. Manual browser seconds remain unchanged. No half-speed multiplier is applied.

Sensitivity defaults are **assumptions**, not measured errors: 3-pixel click standard deviation and a uniform ±15% camera-scale scenario, with 500 simulations. One scale factor is shared by a camera's cyclists per simulation. These ranges omit unknown distortion, identity errors and sampling uncertainty; they are not verified accuracy bounds. The ±15% is configurable and is not derived from validation or used to accept/reject a cyclist. Old manual and new manual estimates use the same usable encounters. The prior HiPerGator column is contextual: its people and coverage can differ. The same-video GPU comparison remains a separate job.

## Optional HiPerGator rerun

No rerun is needed to view the local results. To reproduce the full analysis on HiPerGator after pushing/pulling the new code and manual inputs:

```bash
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
mkdir -p logs
sbatch code/speed_analysis_pass.slurm
```

This single CPU job runs all four stages. It can run alongside the GPU jobs and does not submit another detector run. It requires NumPy, SciPy, Matplotlib and ffprobe (the wrapper attempts the ffmpeg module). Input videos are the existing `exp_results/MANUAL_BICYCLE_REVIEW_47586267` pack. Output is a new `exp_results/SPEED_ANALYSIS_JOBID/` folder. Requeue/resubmission creates a different job-ID folder; existing results are never overwritten.

Read `RESULTS.md` first. `cyclists.csv` gives each encounter's saved clock interval, all three speeds, sensitivity limits and rejection/quality flags; `sites.csv` summarizes locations. `plots/` contains accepted encounter diagnostics; `timestamp_audit.json` and `timestamps/` contain timing evidence; `config.json` records assumptions. `status.json` and `cyclists.csv` update after each encounter.

To change assumptions without editing code, invoke `python code/speed_analysis_pass.py --videos PATH --out NEW_FOLDER --click-sigma-px 3 --scale-fraction 0.15 --simulations 500`. A new output folder is required. Wheel-size/road-marking calibration and measured University endpoint confirmation remain outside this pass.
