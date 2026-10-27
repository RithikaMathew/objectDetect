> October 26 correction: only Colonial North has a fully measured total. File-count estimates are not verified hours. Run `sbatch code/audit_video_durations.slurm` on HiPerGator to measure all 1,919 inventoried originals across 41 cameras. Outputs are incremental and resumable in `exp_results/VIDEO_DURATION_AUDIT/`.

# Video lengths: previews, source files and full camera recordings

Updated October24,2026. No new object detection or cluster processing was run to produce this table.

## Three different lengths

- **Preview:**45seconds. Three previews per camera total2minutes15seconds. Those short excerpts cannot establish the full-hour cyclist count.
- **Source file:** generally about60minutes in the files whose metadata was checked. We can process a short excerpt from it; selecting a source does not require processing the full hour.
- **Full camera recording:** many source files together, often roughly48hours. Choosing the shortest recording is different from choosing the shortest source file.

## Cameras used for speed-reference screening, shortest first

The file counts are confirmed from the archive inventory. **Estimated hours assume one hour per file.** Only Colonial North has complete duration metadata in the downloaded inventory; do not present other estimates as actual measured totals. Columbia has multipart filenames, making its estimated total particularly uncertain.

| Candidate camera | Source files | Full recording duration |
|---|---:|---|
| Pleasant Hill Path | 31 | Unverified; full duration audit pending |
| West Orange Path | 37 | Unverified; full duration audit pending |
| Aloma Path | 48 | Unverified; full duration audit pending |
| Baxter | 48 | Unverified; full duration audit pending |
| Carroll NBL | 48 | Unverified; full duration audit pending |
| Colonial North | 48 | **47.99 hours measured** |
| Colonial South | 48 | Unverified; full duration audit pending |
| Daniels Path | 48 | Unverified; full duration audit pending |
| Edgewater N | 48 | Unverified; full duration audit pending |
| Lee Road N | 48 | Unverified; full duration audit pending |
| Lee Road South | 48 | Unverified; full duration audit pending |
| Rinehart Path | 48 | Unverified; full duration audit pending |
| University SW Speed | 48 | Unverified; full duration audit pending |
| Winter Park Rd Speed | 48 | Unverified; full duration audit pending |
| Columbia Ave | 49 | Unknown; multipart sources need duration audit |

**Pleasant Hill Path has the fewest files (31), followed by West Orange Path (37); their actual playback hours and duration ranking are unverified.** All other screened cameras have48files except Columbia with49. Silver Star has no mapped source. These are candidate street/camera matches, not verified correspondence to individual speed observations.

Pine Hills BL E has the fewest files in the entire inventory (25); its duration is unverified, but the speed workbook has no Pine-named reference rows. Therefore it does not currently meet the request for a location with bicycle-speed reference measurements.

## Verify full playback hours

After pushing these changes and pulling on HiPerGator, run from `vision3/best/test_colonial`:

```bash
mkdir -p logs
sbatch code/audit_video_durations.slurm
```

This CPU-only job measures all 1,919 inventoried original files, including Columbia's multipart files. It reads existing extracted originals when present; otherwise it temporarily extracts one archive member, reads its duration and deletes that temporary copy. It does not run detection or decode full videos. Reading compressed archive members may still take time. It saves `per_source.csv`, `by_camera.csv` and `RESULTS.md` after every file in `exp_results/VIDEO_DURATION_AUDIT/`. Repeating the submission resumes measured files and retries errors. A camera's full total stays blank until every inventoried source is measured. Summed playback hours do not establish gap-free recording coverage.

Check progress with:

```bash
cat exp_results/VIDEO_DURATION_AUDIT/RESULTS.md
```

The full archive is on HiPerGator and is unavailable locally; this job has been prepared and tested, not submitted here.

## Latest Colonial speed run47545558

The improved adapter collected28usable car calibration tracks from about70seconds of original footage (674car detections). It saved a learned calibration. All7labelled bicycle candidates still lacked sufficiently continuous observations inside that calibrated region;0automatic bicycle mph estimates were produced. This is not a success in bicycle-speed validation. Download lacked final report/status files; root-relative report-path handling was corrected and its report rebuilt locally using saved calibration, without rerunning detection or GPU work.

[Rebuilt speed report](../reports/cluster_returns/20261024/colonial_speed_47545558_report_rebuilt/RESULTS.md).

## Complete camera inventory

| Camera | Source files | Fully measured total hours | Measured files |
|---|---:|---:|---:|
| Pine Hills BL E | 25 | Unknown | 1 |
| Pleasant Hill Path | 31 | Unknown | 0 |
| West Orange Path | 37 | Unknown | 0 |
| Alafaya East | 48 | Unknown | 0 |
| Alafaya West | 48 | Unknown | 0 |
| Aloma Path | 48 | Unknown | 0 |
| Aloma Sidewalk | 48 | Unknown | 0 |
| Baxter | 48 | Unknown | 0 |
| Carroll NBL | 48 | Unknown | 0 |
| Clay Ave | 48 | Unknown | 0 |
| Colonial North | 48 | 47.99 | 48 |
| Colonial South | 48 | Unknown | 0 |
| Curry Ford North | 48 | Unknown | 0 |
| Daniels Path | 48 | Unknown | 0 |
| Daniels Sidewalk | 48 | Unknown | 0 |
| Edgewater | 48 | Unknown | 0 |
| Edgewater N | 48 | Unknown | 0 |
| Glenridge | 48 | Unknown | 0 |
| Kaley | 48 | Unknown | 0 |
| Lakemont Pathway | 48 | Unknown | 0 |
| Lee Road N | 48 | Unknown | 0 |
| Lee Road South | 48 | Unknown | 0 |
| Livingston | 48 | Unknown | 0 |
| N Orange | 48 | Unknown | 0 |
| Par Street | 48 | Unknown | 0 |
| Pine Hills BL | 48 | Unknown | 0 |
| Pine Hills NBL | 48 | Unknown | 0 |
| Pine Hils NBL E | 48 | Unknown | 0 |
| Rinehart Path | 48 | Unknown | 0 |
| Rinehart Sidewalk | 48 | Unknown | 0 |
| S Orange NB | 48 | Unknown | 0 |
| S Orange SB | 48 | Unknown | 0 |
| Summerlin | 48 | Unknown | 0 |
| University North | 48 | Unknown | 2 |
| University SW Speed | 48 | Unknown | 1 |
| University South | 48 | Unknown | 0 |
| West Orange Sidewalk | 48 | Unknown | 0 |
| Winter Park Rd Speed | 48 | Unknown | 0 |
| Winter Park Road | 48 | Unknown | 0 |
| Columbia Ave | 49 | Unknown | 0 |
| Curry Ford South | 49 | Unknown | 0 |

[Per-camera CSV](../reports/cluster_returns/20261024/recording_lengths/by_camera.csv) · [Every individual source file, including known measured durations](../reports/cluster_returns/20261024/recording_lengths/per_source.csv). Sourcefile inventory and metadata are preserved; unknown durations remain blank, never zero.

