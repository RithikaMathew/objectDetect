# Start here: submit the active research batch

**This is the one Markdown file to use now.** The other MD files are background/reference. You have not submitted this batch yet. Push/pull once, then run the single submission command below. There is no need to run the earlier individual submission commands.

Current measured reference: **b4_combo_static5 = 19/21 people correctly counted and labelled, with zero extra counted tracks**, across four 15-minute Colonial clips. Existing truth files remain valid; no repeat labelling is requested. New research code is implemented and locally tested, but has not run on HiPerGator yet.

## 1. On your Mac: commit and push

```bash
cd /Users/rithika/Desktop/objectDetect
git status --short
git add -A
git diff --cached --stat
git commit -m "Organize repo and add one-command research experiments"
git push origin main
```

The many deletions are mostly old text logs and duplicate root files from the authorized cleanup. Differing source versions are in archive/. Truth, saved count tables, structured run records and current Colonial paths are preserved. No model weights or source videos are transferred by Git.

## 2. On HiPerGator: pull and submit ONCE

Use your existing checkout at /orange/xiangyan/rithika/vision. Check that it is on main and that old jobs using removed root-level scripts have finished. If pull reports local conflicts, preserve those files and send the error; do not force-reset or clean your cluster results.

```bash
cd /orange/xiangyan/rithika/vision
git status --short
git branch --show-current
git pull --ff-only origin main
cd vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
python code/submit_research.py --tag research_oct19 --go
```

That last command submits the whole suite. Submit once; the manifest folder prevents duplicates. To preview without submission, omit --go. A genuinely new batch needs a new --tag. The launcher checks required video, model, baseline table and truth paths before submitting. It stops and records job IDs if submission fails part-way; do not blindly re-run with a new tag in that case.

## What the suite runs

| Experiment | Outputs / meaning |
|---|---|
| Multi-scale + horizontal-flip inference (TTA), four labelled clips | Full RT-DETR + SAHI + tracking + X-CLIP pipeline with extra full-frame person detections, merged before tracking; scored against existing truth |
| High-sensitivity candidates, four labelled clips | Detector/tracker thresholds 0.15; 0.4 s minimum; no static rejection; scored separately from b4 |
| Grounding DINO setup and four frame audits | Downloads a pretrained model into a separate cache; creates an isolated environment; GPU smoke-check; side-by-side frames and proposal CSVs against saved b4 tracks |
| Higher-resolution search, any year | Encoded resolution above 720x480; inventory and busy-window cut commands |
| Existing Corrine higher-resolution clip, if present | Three matched runs: baseline, best configuration, best + TTA; correctly scaled pixel settings; qualitative until it has truth |
| Zone / fisheye preview images | Generates zone alignment image and both circular/full-frame lens guesses; does not guess a final calibration |
| Twelve-minute raw-video review pack | Automatically built after all four sensitive runs succeed; this is the active sensitivity experiment, not the deferred 40-track campaign |
| Zero-DCE, only if checkpoint exists | Retries the two failed night tests; missing weights are explicitly recorded as SKIPPED |
| Final report | Runs person-level evaluation for complete successful experiment groups; lists failures, skipped inputs and review-file locations |

There are **22 possible tasks, normally 20 if the Corrine clip exists and Zero-DCE weights do not**. At most four GPU jobs from this suite run at once. This cap is local to the suite, not your entire account. Pipeline jobs have a six-hour limit; elapsed completion time depends on queue and inference time. The old ablation/gamma/CLAHE runs are reused as evidence rather than resubmitted.

Grounding DINO is an independent **proposal audit**, not integrated cyclist counting: a bicycle box does not prove a cyclist. Its images are sampled at labelled encounter start/middle/end and regular background intervals; proposal totals are not person recall. TTA uses 960/1280 input sizes and horizontal flips in addition to the unchanged base/SAHI passes; added views supply people only, not extra vehicle detections. Default pipeline behavior is unchanged unless TTA is enabled.

Grounding setup uses a per-suite environment under .research_env/ and a .pth link to the working yolo_env packages to reuse GPU Torch, while local research packages take precedence. It pins Transformers 4.49.0. It does not modify yolo_env. Downloaded safetensors are cached in .research_models/ and the exact model revision is recorded. Compute-node network/package compatibility is checked by the setup job; failures are written to the report while independent experiments continue. Dependencies use afterany and explicit success checks, so a failed setup cannot strand the final report behind never-started jobs.

**Excluded:** own-night fine-tuning, the 40-track comparison, full-day scaling. Temporal feature aggregation and BNE-DETR model replacement are not promised in this batch: those require a compatible detector implementation/checkpoint rather than the frozen-model experiments implemented here. Existing model weights and saved results are not overwritten. No automatic promotion of experimental settings occurs.

## 3. Come back and read ONE result file

```bash
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
squeue -u "$USER"
cat exp_results/RESEARCH_research_oct19.md
```

The final report is created automatically after the suite dependencies finish. A timeout/cancelled task without a success record is not scored as a successful experiment. If jobs are still running or the automatic report was interrupted, regenerate a current status report without submitting anything:

```bash
python code/research_worker.py logs/research_oct19 report
```

Send the contents of exp_results/RESEARCH_research_oct19.md. It contains the exact new annotated-video, Grounding-image, preview and review-pack locations. Do not label anything else before seeing those results. Model experiments run unattended; human checking, lens selection and a scored new-camera truth file cannot be automated away.

## Reference only

- [Exact previously generated video paths](docs/VIDEO_PATHS.md)
- [Latest results PowerPoint](reports/presentations/bike_weekly_meeting_10_19.pptx) — measured results predate the newly implemented research batch.
- [Task detail](docs/tasks/todo.md)
- [Research rationale and primary sources](docs/RESEARCH_METHODS.md)
- [Long validation history](docs/colonial/README_colonial_validation_v31.md)
- [Cleanup manifest](docs/REPO_CLEANUP_MANIFEST.csv)

Repository map: current code/results in vision3/best/test_colonial/; shared older code in pipeline/; shared launchers in slurm/; utilities in scripts/; reference notes in docs/; presentation artifacts in reports/; inventories/review tables in data/; originals in Bike Lane Study Counts/; historical sources in archive/. Avoid older runbook commands unless debugging a specific task.
