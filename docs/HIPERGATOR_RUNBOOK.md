> **Superseded for normal submission:** use the root README.md only. The new submit_research.py command schedules the active experiments and automatic report together. Do not also run the individual submission commands below; they are retained for debugging/reference.

# Sync, run and review — 2026-10-19

## 1. On your Mac: commit and push

```bash
cd /Users/rithika/Desktop/objectDetect
git status --short
git diff --stat
git add -A
git diff --cached --stat
git commit -m "Organize repository and repair Colonial validation workflow"
git push origin main
```

The many deletions are mainly historical job logs and redundant root files. The cleanup manifest records moved/deleted file names and hashes. Do not run the obsolete organize_repo.sh; this cleanup has already happened. The old recovery tarball is unnecessary when using Git.

## 2. On HiPerGator: update the checkout

Wait for jobs using old root-level scripts to finish before pulling. The current Colonial directory was preserved, but older root-level scripts were removed in favor of pipeline/, slurm/, scripts/ and archive/.

```bash
cd /orange/xiangyan/rithika/vision
git rev-parse --show-toplevel
git status --short
git branch --show-current
squeue -u "$USER"
```

The checkout should be this project and the branch main. If you cloned elsewhere, use the repository directory printed above. If tracked files have local edits or deletion conflicts, preserve them and resolve before pulling; do not run reset --hard or clean. New untracked CSV/video results do not need to be deleted. If the checkout is clean and old root-script jobs have finished:

```bash
git pull --ff-only origin main
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
mkdir -p logs
```

A pull can refuse if the cluster has modified historical logs that this commit deletes, or untracked files collide with newly tracked files. Stop and preserve those files; send the exact message rather than forcing the pull. Git does not copy ignored videos, model weights, or environments; those must already exist on the cluster. No tar extraction is required with this workflow.

## 3. Current job to submit ONCE

From test_colonial with the environment active:

```bash
# Scan only candidates above 720x480; record metadata for every year (GPU).
sbatch code/pick_busy.slurm
squeue -u "$USER" -o "%i %j %T %M"
```

After the scan job finishes:

```bash
cat busy/inventory.csv
cat busy/windows.txt
```

Share both files before selecting the higher-resolution test. A year does not qualify a camera: compare actual encoded dimensions against 720x480. Upscaling an old video does not supply new detail. The 40-track review job is on the back burner; do not submit it now. No extra truth labels are needed for the four existing clips.

## 4. Annotated videos worth checking

Use b4_combo_static5 first. No need to watch every brightening or ablation video again.

| Clip | Position in 15-minute video | What to verify |
|---|---|---|
| Night 21:15–21:30 | 14:21–14:26 | Several riders together. Is short track #21 / truth n5 a distinct rider rejected by duration? Confirm identity because matching is time-only. |
| Night 21:15–21:30 | 14:47–14:58 | Truth n6: is the person walking while both models say cyclist? |
| Day 12:45–13:00 | 9:54–10:04 | h4 was not rechecked in prior notes; confirm it is a real pedestrian and confirm the track identity. |
| Day 12:45–13:00 | 11:17–11:38 | h5: walking away; check whether the detector box is present while X-CLIP mislabels it. |

Locate the actual saved file names on HiPerGator:

```bash
find annotated/b4_combo_static5 -type f -name '*.mp4' -print
```

The night file includes `night_2115-2130`; the day file includes `day_1245-1300` in newer names. Use clock/bin labels to identify older names. Send observations in the form clip / position / real class / box missing versus wrong label versus not counted. Also record any entirely unboxed people, including people on the grass; track tables cannot reveal them.

The next whole video to watch should be a busy genuinely higher-resolution window, from any year AFTER the scan and full pipeline runs. Share inventory.csv and windows.txt first so the selected source, start clock time, resolution and frame-rate settings can be checked. Do not use Colonial zones at these other cameras. The original fisheye frame/preview is still needed before choosing undistortion parameters.

## 5. Optional failed Zero-DCE retry

Not a prerequisite for keeping b4: gamma/CLAHE already worsened the results. If completing the experiment, locate the checkpoint first:

```bash
find /orange/xiangyan/rithika/vision -type f -name Epoch99.pth -print
```

Replace /actual/path/Epoch99.pth with a real path printed above; do not paste the placeholder unchanged:

```bash
python code/run_batch5.py bright --modes zerodce --zerodce-weights /actual/path/Epoch99.pth
squeue -u "$USER"
python code/run_batch5.py bright --modes zerodce --zerodce-weights /actual/path/Epoch99.pth --go --force
```

--force bypasses the old whole-bright-group submission lock; use only after verifying no duplicate Zero-DCE jobs are running. It submits exactly two jobs, not the already-completed experiments. If no checkpoint exists, leave this experiment unscored.

## 6. Local helper checks

No GPU needed for these helper checks (they do not load real models):

```bash
python -m unittest discover -s code -p 'test_*recovery.py'
python code/test_v19.py
python code/undistort_fisheye.py selftest
python code/fusion_probe.py --root . --runs b4_combo_static5 --out exp_results/FUSION_cases_latest.md
```

## 7. Optional high-sensitivity / 12-minute review experiment

A new `review` group prepares four jobs over the existing four labelled 15-minute windows (one hour total). It keeps SAHI/fusion, lowers detector/tracker thresholds to 0.15, allows 0.4-second tracks and disables static rejection so humans can inspect candidates. It is an experiment, not a guarantee of high recall and not a replacement for b4. First dry-run:

```bash
python code/run_batch5.py review --time 04:00:00
```

If running this experiment, submit ONCE:

```bash
python code/run_batch5.py review --time 04:00:00 --go
```

After all four jobs finish, from test_colonial:

```bash
python code/eval_truth.py --root . --runs b4_combo_static5,b6_review_candidates --baseline b4_combo_static5 --out exp_results/EVAL_review_candidates.md
python code/track_truth_v1.py template --root . --run b6_review_candidates --min-secs 0 --out validation/review_candidates.csv
```

Build the 12-minute pack via Slurm after those tables exist:

```bash
sbatch --export=ALL,PACK=review/sensitive12_20261019,TABLE=validation/review_candidates.csv,BUDGET_MIN=12 code/review_pack.slurm
```

Download and label this separate pack as above. After copying labels.csv back:

```bash
python code/review_pack.py curve --pack review/sensitive12_20261019 --labels review/sensitive12_20261019/labels.csv
```

For these four windows together, 12 minutes is a single total budget against one hour of source footage. Do not use detector cyclist share as an all-person ranking score. This initial version uses chronological order, not an optimized selection policy. The labels and complete truth must establish people recovered, duplicates, false candidates and review time. The curve's track count can double-count a real person split across tracks; manually resolve duplicates and compare with the 21-person truth before claiming person recall. This is a lower-threshold experiment, not a proven guarantee of catching everyone.
