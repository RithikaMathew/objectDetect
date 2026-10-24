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
| Pleasant Hill Path | 31 | Approximately 31 hours; not fully measured |
| West Orange Path | 37 | Approximately 37 hours; not fully measured |
| Aloma Path | 48 | Approximately 48 hours; not fully measured |
| Baxter | 48 | Approximately 48 hours; not fully measured |
| Carroll NBL | 48 | Approximately 48 hours; not fully measured |
| Colonial North | 48 | **47.99 hours measured** |
| Colonial South | 48 | Approximately 48 hours; not fully measured |
| Daniels Path | 48 | Approximately 48 hours; not fully measured |
| Edgewater N | 48 | Approximately 48 hours; not fully measured |
| Lee Road N | 48 | Approximately 48 hours; not fully measured |
| Lee Road South | 48 | Approximately 48 hours; not fully measured |
| Rinehart Path | 48 | Approximately 48 hours; not fully measured |
| University SW Speed | 48 | Approximately 48 hours; not fully measured |
| Winter Park Rd Speed | 48 | Approximately 48 hours; not fully measured |
| Columbia Ave | 49 | Unknown; multipart sources need duration audit |

**Shortest listed speed-reference candidate: Pleasant Hill Path,31source files (~31hours if hourly). Next: West Orange Path,37files (~37hours).** All other screened cameras have48files except Columbia with49. Silver Star has no mapped source. These are candidate street/camera matches, not verified correspondence to individual speed observations.

Pine Hills BL E is the shortest recording in the entire inventory with25files (~25hours), but the speed workbook has no Pine-named reference rows. Therefore it does not currently meet the request for a location with bicycle-speed reference measurements.

## Practical recommendation

You do not need to watch or process31–48hours. Respecting the preference for the shortest source collection, start with Pleasant Hill Path and inspect a fixed short daytime segment; extend only as needed to find1–5cyclists. Total session length does not predict how quickly cyclists appear. A fifteen-minute excerpt costs about the same processing time whether it comes from a31-hour or48-hour recording. The existing45-second previews are a quality screen, not a representative speed sample. No new submission is required just to choose the site.

If exact full-session duration is required before choosing, original MP4 metadata must be audited on HiPerGator for all files, including those still inside the ZIP. That would be a metadata task, not object detection; current partial local metadata cannot establish those totals.

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

