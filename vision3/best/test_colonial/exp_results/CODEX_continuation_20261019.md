
## 41. Codex continuation (2026-10-19): batch-5 results and recovery

This section supersedes the queued-job assumptions in do.md. Local copies of the actual track tables and truth files were re-scored with eval_truth.py; they reproduce look.md. These are existing GPU results, not new inference runs.

| Settings | Correctly counted AND labelled | Interpretation |
|---|---:|---|
| Current best b4_combo_static5 | 19/21 (90.5%) | Keep this configuration |
| Without speed b5_nospeed | 17/21 (81.0%) | Speed adds two correct classifications in this comparison |
| Without detector veto b5_noveto | 18/21 (85.7%) | Veto adds one correct classification in this comparison |
| Best, night clips only | 9/11 (81.8%) | Reference for brightening |
| Gamma, night clips only | 8/11 (72.7%) | Worse by one person |
| CLAHE, night clips only | 5/11 (45.5%) | Worse by four people |
| Zero-DCE | No result | Both jobs failed before inference; do not score as zero accuracy |

No extra counted tracks were reported for the completed runs. Wrong-class people are still errors even though they are real people. FOUND means counted with the correct class; detected-not-counted means the model made a track but rejected it; missed means no matched track; extra means a counted track without a matched truth person. A 0/0 entry means that class has no truth examples in that clip, not a failure. The best run's two failures remain one pedestrian labelled cyclist and one short cyclist track rejected. Thus its totals are 8 cyclists / 12 pedestrians versus truth 8 / 13: the apparently exact cyclist total hides a missed cyclist and a wrongly included pedestrian.

These are encouraging development results, not evidence of 90.5% accuracy across sites/years. All 21 people are from one camera/day and these clips have been inspected repeatedly. The speed/veto gains are marginal contributions with other rules active; do not add them as independent gains. Speed remains image movement in body heights/second, not measured MPH. Runtime is about 42 minutes per 15-minute clip (~2.8 times video duration).

### Failures verified in logs and code fixes

* pick_busy job 46141085 failed because the default path omitted /weights/ before best.pt. Fixed pick_busy_windows.py to match the working detector path in the v19 Slurm file, support WEIGHTS, and reject a missing file before importing/loading the detector. pick_busy.slurm now stops on shell errors.
* Zero-DCE jobs 46141059_22 and 46141060_23 failed because ZERODCE_WEIGHTS was unset. run_batch5.py now requires an existing checkpoint before submission and exports it. --modes zerodce selects only those two failed jobs; gamma/CLAHE/ablation need no repeat. Submission failures now stop immediately and preserve a submission log/lock; the lock is reserved before the first job.
* The grep errors and missing busy directory in look.md were initially caused by running inside code/. They do not prove all jobs failed. The actual logs are under test_colonial/logs/.
* Bin AI is a fixed whole-bin total from the render snapshot, not a live counter. Hour so far is the frame-time live counter, which can also revise a label as evidence arrives. Changed the fixed label to AI total (AI snapshot for streamed/provisional clips), preserving GT. Old annotated videos retain old text until rendered again. Streaming snapshots may differ from final CSV totals; existing mismatch logging records that.
* undistort_fisheye.py now offers --coverage full-frame for rectangular images: the guessed FOV is interpreted diagonally instead of forcing an inscribed short-side circle. The old circular default stays available. This is not lens calibration. No original 2025 frame, both.png, or preview.png is present in this checkout, so no visual choice of FOV/pitch has been made. Encoder failure now reports an error rather than success.
* test_v19.py now resolves its source file relative to itself so it can run from test_colonial.

### Cluster recovery (after copying the changed code files to the same code/ folder)

Run from test_colonial, never code/:

```bash
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
# Retry the failed scan ONCE. This scans the four paths in videos_to_scan.txt.
sbatch code/pick_busy.slurm
# After that job completes:
cat busy/inventory.csv
cat busy/windows.txt
# Locate the existing Zero-DCE checkpoint (do not invent a path):
find /orange/xiangyan/rithika/vision -type f -name Epoch99.pth -print
```

Only if a checkpoint is found, use its full path below (replace /actual/path/Epoch99.pth). First dry-run, then submit once. --force is required only because the old bright-group submission lock already exists; check squeue before using it.

```bash
python code/run_batch5.py bright --modes zerodce --zerodce-weights /actual/path/Epoch99.pth
squeue -u "$USER"
python code/run_batch5.py bright --modes zerodce --zerodce-weights /actual/path/Epoch99.pth --go --force
```

The 14 batch-5 jobs were 8 ablations (two settings x four existing labelled windows) plus 6 brightening jobs (three modes x two existing night windows). They were NOT seven distinct videos. The separate scan list has four input paths: two 2022 Curry Ford hourly files and two 2025 Corrine camera files. A scan chooses windows; it does not run the full counting pipeline on them. No 2023/2024 file appears in this list.

### Research corrections and remaining work

BNE-DETR DOES have a public source repository: https://github.com/luy02735-lang/BNE-DETR (verified 2026-10-19; root folders benchmark, dataset, rtdetr_pytorch). The prior blanket suggestion that no implementation exists was too strong. Pretrained-weight availability, dependencies and compatibility with our person/cyclist model remain unverified; no model replacement or training was performed.

The requested technique for an object appearing in a still scene exists: background subtraction (MOG2/KNN), documented at https://docs.opencv.org/4.x/d1/dc5/tutorial_background_subtraction.html . This pipeline already has MotionDiag and --motion-diag. Its existing synthetic test confirms it flags an unexplained blob and ignores an explained one. Prior real-clip output had too many candidates (447/185); no measured improvement has been established. A changed region can be shadow/light/foliage, not necessarily a person. A next experimental version would crop/re-detect unexplained regions and evaluate recovered people AND added false tracks; it should remain separate from the best configuration until scored.

Remaining dependent steps: run the repaired scan on HiPerGator; inspect/cut its selected clips; obtain the original fisheye frame and compare full-frame previews before selecting lens settings; run and hand-label the new-year clips. Keep fine-tuning and 24/48-hour scale-up deferred per section 40. No empty truth files were created and no model weights or existing result tables were overwritten.

Validation locally: re-evaluated saved tables (matches look.md); four recovery regression tests pass (missing checkpoint, selective retry, failed-submission stop/lock, rectangular mapping); existing test_v19.py passes (slicing, merging, enhancement, speed, motion diagnostic); fisheye selftest passes (4.57/255 centre difference). No GPU inference or Slurm jobs submitted from this Mac. Synthetic mapping tests do not establish that undistortion improves real detections.
