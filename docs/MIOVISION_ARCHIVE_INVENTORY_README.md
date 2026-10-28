# Entire MioVision ZIP: camera locations, years, video counts and hours

Scope: every inventoried video in `MioVision_Data.zip`, including annual collections, Bike Lane Study and Other. [Study/count and Mighk speed-reference inventory](BIKE_LANE_STUDY_INVENTORY_README.md).

**Full ZIP scan pending.** The archive is on HiPerGator, not available locally. The2019subset’s41cameras and1,919files must not be reported as the entire archive. Camera years/file counts require a full central-directory scan; full playback hours additionally require reading video duration metadata. Unknown values will not be replaced with one-hour-per-file assumptions.

## Get or refresh the full inventory

After pushing/pulling code, run directly on HiPerGator for the quick camera/year/count listing:

```bash
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
python code/prepare_full_archive_inventory.py --inventory-only
cat exp_results/MIOVISION_FULL_ARCHIVE_INVENTORY/CAMERA_YEARS.md
```

Then submit the CPU metadata audit for actual video hours:

```bash
mkdir -p logs
sbatch code/full_archive_inventory.slurm
```

The job reuses successful per-video measurements from the completed2019audit, probes existing extracted originals where available, otherwise extracts only one temporary video at a time. It deletes that temporary copy after measuring. It does not run object detection or permanently extract the entire archive. ZIP decompression may take time. Results save after each file; resubmit the same script to resume if its24hour limit is reached.

Progress: `cat exp_results/MIOVISION_FULL_ARCHIVE_INVENTORY/durations/RESULTS.md`. Final camera/year table: `exp_results/MIOVISION_FULL_ARCHIVE_INVENTORY/CAMERA_YEARS.md`. To refresh the README from partial or completed measurements: `python code/prepare_full_archive_inventory.py --inventory-only`.

The script writes both READMEs under the HiPerGator repository’s docs folder. To update local copies, paste `cat exp_results/MIOVISION_FULL_ARCHIVE_INVENTORY/camera_years_hours.csv` (or return camera_years.csv and durations/by_camera.csv); no videos need downloading. The terminal summary can also be pasted.

Playback hours measure the actual duration of files, not guaranteed continuous elapsed recording time. Occurrence-only footage may omit quiet periods. Device codes can be reused at different sites; they are not GPS coordinates. Separate years with similarly spelled streets are not automatically the same camera view.
