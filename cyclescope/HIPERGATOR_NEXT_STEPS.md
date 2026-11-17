# HiPerGator: what is still needed

No new GPU job is needed to repair CycleScope, audit the returned inventory, display
existing workbook references, or review already processed tracks.

The fine-tuned RT-DETR `best.pt` is now present in this checkout at:
`vision3/runs/detect/finetune_runs/rtdetr_v3/weights/best.pt`.
CycleScope uses the existing v19 entrypoint with `--chunk-index 1` for normalized
upload filenames, the saved b4 reference rules, and compatible Supervision 0.25.
X-CLIP is a separate pretrained model, not contained in `best.pt`.

## Files to bring from HiPerGator when needed

1. **Original videos for the dates you want to process.** The Mac has an archive
   listing, not all 9,085 videos. Select/download only the source files you need.
2. **Saved numeric calibration for the same camera, resolution and recording.**
   Keep calibration JSON, reference size, measurement/method provenance and
   associated run log together. A different camera's homography cannot be reused.
   The existing learned camera scale is exploratory, not independently validated.
3. **Completed run logs and exports** if you have newer results: `_run_log.json`,
   tracks, observed person/vehicle trajectories and speed reports. They can support
   future imports without rerunning inference; this app currently processes uploads.
4. **X-CLIP cache only if local model downloads are unavailable.** If the cluster
   uses another `HF_HOME`, find the cache there rather than assuming a home path.
5. **Per-video or per-year duration export** if you want to split a combined
   multi-year archive row. Existing combined totals are already measured; do not
   estimate the split from file counts or repeat the full audit without a reason.

## Read-only checks on HiPerGator

From your Mac, enter your normal SSH authentication:

```sh
ssh rmathew1@hpg.rc.ufl.edu
```

On HiPerGator, these only locate existing files; they submit no jobs:

```sh
ls -lh /orange/xiangyan/rithika/vision/vision3/runs/detect/finetune_runs/rtdetr_v3/weights/best.pt
find /orange/xiangyan/rithika/vision/vision3/best/test_colonial/exp_results \
  -type f -iname '*calibration*.json' -print
find "${HF_HOME:-$HOME/.cache/huggingface}/hub" \
  -maxdepth 1 -type d -name 'models--microsoft--xclip-base-patch32' -print
```

The quoted `HOME` variable above is read only; do not overwrite it.
The November 16 terminal listing confirmed these calibration files exist. For example,
copy the Colonial North manual-match calibration from your **Mac terminal**:

```sh
cd /Users/rithika/Desktop/objectDetect
mkdir -p cyclescope/data/calibrations/ADAPTIVE_SPEED_manualmatch_20261026_233356/s03_colonial_north
scp rmathew1@hpg.rc.ufl.edu:/orange/xiangyan/rithika/vision/vision3/best/test_colonial/exp_results/ADAPTIVE_SPEED_manualmatch_20261026_233356/s03_colonial_north/calibration/calibration.json \
  cyclescope/data/calibrations/ADAPTIVE_SPEED_manualmatch_20261026_233356/s03_colonial_north/calibration.json
```

This is a confirmed existing path, not a claim that this calibration is suitable
for every Colonial recording. Its contents, units, camera/resolution and method
must be checked against the selected video before use. Copying the file does not
automatically load it into CycleScope. Other locations and run variants listed in
the different site/run directories must remain separate; do not overwrite them as one `calibration.json`.

If X-CLIP was cached under the usual home cache, copy it with symlinks preserved:

```sh
mkdir -p "$HOME/.cache/huggingface/hub"
rsync -av rmathew1@hpg.rc.ufl.edu:.cache/huggingface/hub/models--microsoft--xclip-base-patch32/ \
  "$HOME/.cache/huggingface/hub/models--microsoft--xclip-base-patch32/"
```

If there are no local source videos or no valid same-camera metric calibration,
those are genuine missing inputs. Counts/speeds for unprocessed recordings remain
unavailable; no statistics are generated to fill gaps.

## Mac runtime fixes

Use `bash cyclescope/start.sh` from the repository root. It reuses a running
CycleScope API/frontend rather than launching duplicates on ports 8000/5173.
If an unrelated application owns either port, it reports that conflict without
stopping it. A failed video can be retried from its error page after the fix.

Runtime packages are pinned in `cyclescope/requirements.txt`. OpenCV is installed
once, not as overlapping GUI/headless distributions. PyAV is not required by this
OpenCV-frame pipeline; its optional video libraries can collide with OpenCV on macOS.
No bundled `.dylib` files should be renamed or deleted manually.

## Current local calibration

Downloaded successfully to `data/calibrations/colonial_north/calibration.json`.
Its `source.json` records the exact remote path and local checksum. The file has
an H matrix and support hull, with 28 car tracks / 458 boxes. It explicitly says
`learned_scale_not_independently_speed_validated` and sidewalk transfer unverified.
It has no image dimensions or measured landmark pairs; it is not automatically
loaded by the app and does not resolve the physical-clearance limitation.

## RT-DETR checkpoint transfer (only for a fresh checkout)

The checkpoint and X-CLIP cache are already available on this Mac. To restore the
checkpoint on another checkout, run from its repository root on the Mac:

```sh
mkdir -p vision3/runs/detect/finetune_runs/rtdetr_v3/weights
scp rmathew1@hpg.rc.ufl.edu:/orange/xiangyan/rithika/vision/vision3/runs/detect/finetune_runs/rtdetr_v3/weights/best.pt \
  vision3/runs/detect/finetune_runs/rtdetr_v3/weights/best.pt
```

RT-DETR weights and the pretrained `microsoft/xclip-base-patch32` cache are separate.
Model files, caches and local uploaded jobs are intentionally excluded from Git.
