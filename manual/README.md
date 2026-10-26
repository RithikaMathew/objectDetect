# Bicycle counts and speed comparison

**30 manually annotated cyclists; 29 estimated speeds.** The selected study intervals record 50 bicycles. Unannotated bicycles are review gaps, not automatically detector misses.

**Validation count** means the study bicycle count in the selected video intervals. **Validation speed sample** means the separate cyclists measured for speed at that location. They are different samples. HiPerGator is the automatic pipeline; Manual is your clicked positions.

| Location | Available video hours | Manual selection: bins / minutes | HiPerGator completed minutes | Validation count | HiPerGator count / validation in covered bins | Manual count | Validation mph (speed sample) | HiPerGator mph (sample) | Manual mph (sample) |
|---|---|---|---:|---:|---|---:|---|---|---|
| Aloma | ~48 | 3 / 45 | 60.0 | 4 | 0 / 2 (2/3 bins) | 4 | 13.58 (26) | All candidate tracks filtered | 19.81 (4) |
| Carroll | ~48 | 1 / 15 | 60.0 | 2 | 0 / 2 (1/1 bins) | 2 | 11.89 (15) | All candidate tracks filtered | 12.37 (2) |
| Colonial | 47.99 | 2 / 30 | 60.0 | 3 | 3 / 3 (2/2 bins) | 3 | 9.54 (23) | 7.63 (3) | 10.71 (3) |
| Columbia | Unknown | 4 / 60 | 30.0 | 6 | 6 / 3 (2/4 bins) | 4 | 12.24 (9) | 3.04 (3) | 12.47 (4) |
| Edgewater | ~48 | 4 / 60 | 60.0 | 10 | 2 / 5 (3/4 bins) | 6 | 12.02 (50) | 17.57 (2) | 14.00 (5) |
| Lee | ~48 | 4 / 60 | 60.0 | 10 | 2 / 10 (4/4 bins) | 4 | 8.73 (2) | 9.88 (2) | 12.36 (4) |
| Pleasant Hill | ~31 | 1 / 15 | 60.0 | 2 | 2 / 2 (1/1 bins) | 2 | 9.86 (41) | 8.99 (2) | 8.99 (2) |
| Rinehart/CST | ~48 | 3 / 45 | 60.0 | 3 | 0 / 3 (3/3 bins) | 1 | 12.92 (25) | All candidate tracks filtered | 12.01 (1) |
| University | ~48 | 2 / 30 | 60.0 | 5 | 1 / 1 (1/2 bins) | 4 | 9.49 (78) | 11.17 (3) | 16.98 (4) |
| West Orange/Park | ~37 | 3 / 45 | 60.0 | 5 | 1 / 5 (3/3 bins) | 0 | 10.77 (25) | 11.59 (1) | Cyclists not located in review |

**Time coverage differs:** Manual selection is the positive-count intervals offered for review, not continuous annotation or measured riding time. HiPerGator completed minutes includes its finished consecutive windows, including zero-count bins, until its quota or one-hour limit. Aloma manual selection is 45 minutes; its recovery completed about 60 minutes after the original node failure. Most other sites completed about 60 minutes; Columbia stopped after 30 minutes. Speed estimates themselves use only the saved per-cyclist seconds, and may involve different people. This is not a matched-duration or matched-person speed comparison.

Numbers after mph are the number of cyclists contributing to that average. Count coverage such as **2/4 bins** means only two of the four selected intervals are included in that automatic count comparison. A missing speed is not zero.

**Why Aloma has 4 cyclists but 26 speed records:** Aloma Path has approximately 48 hours of available footage. This pilot selected the first available day’s hour nearest noon; within that hour, only intervals with positive study bicycle counts were sent for manual review. For Aloma these were 12:00–12:15, 12:30–12:45 and 12:45–13:00 on October 30, 2019: 45 minutes containing 4 study bicycles, all 4 annotated. The remaining interval recorded zero bicycles.

| Dataset | Bicycle count |
|---|---:|
| **Aloma Path, full 48-hour count period** | **191** |
| Aloma Sidewalk, separate camera/count table | **19** |
| Aloma Path, selected 45 minutes | **4** |
| Aloma speed-reference sample | **26** |

The full count period is **October 30–31, 2019**. The full counts come from the Bicycles worksheets in Aloma_Path_716686_10-30-2019.xls and Aloma_Sidewalk_716692_10-30-2019.xls (192 fifteen-minute bins each, with no missing count cells). The 26 speed observations come from the separate consolidated speed workbook; no individual timestamps link them to the counted encounters.

The **26** belongs to the broader Aloma location speed-reference dataset, not this 45-minute sample. It is not a count of every cyclist in the approximately 48-hour recording. Mighk revisited some corridors for speed analysis, and the speed records have no linked video timestamps. **We cannot confirm that all 26 came from that same 48-hour recording.** Their average is a location-level reference, not the known speeds of these same four cyclists.

**Study speed method:** Mighk Wilson stopwatch-timed cyclists from half-speed video and accounted for playback speed in the workbook. We use the supplied mph values without doubling them again.

### How your manual annotations produce speed

1. You paused the original-speed video and clicked where the same cyclist’s rear tire touches the pavement, then advanced the video and clicked that same point again. Each click saves an image position and video time.
2. Those successive points form the cyclist’s **trajectory** (their path through the image). Different cyclists and different 15-minute videos are kept separate; clearly separated encounters sharing an ID were split.
3. The saved camera calibration, estimated using car observations from the same camera, converts each image point into an estimated ground position in metres. Pixel movement alone cannot give mph because perspective changes the distance represented by a pixel.
4. We add the distances between successive ground positions and divide by the time between the first and last click. We require at least three points spanning 1.5 seconds.

**Formula:** `speed (mph) = total trajectory distance (metres) / elapsed video time (seconds) × 2.23694`. Here `total distance = distance(point1, point2) + distance(point2, point3) + ...`. For example, an estimated 10 metres in 2 seconds gives 11.18 mph. Each site’s manual mean gives equal weight to its available per-cyclist estimates.

HiPerGator supplies automatically tracked positions; Manual replaces those positions with your clicks. Both still depend on learned camera calibration, so manual annotation fixes tracking gaps but does not prove the distance scale is correct. Click noise, lens distortion and raised sidewalks can affect estimated speed.

### Research basis and alternatives

Trajectory-based speed estimation is the standard position-over-time approach, not a new formula invented for this study. Revaud and Humenberger, **Robust Automatic Monocular Vehicle Speed Estimation for Traffic Surveillance**, ICCV 2021, describe detecting/tracking vehicles and converting image displacement into metric movement using camera calibration ([paper](https://openaccess.thecvf.com/content/ICCV2021/html/Revaud_Robust_Automatic_Monocular_Vehicle_Speed_Estimation_for_Traffic_Surveillance_ICCV_2021_paper.html)). Their [author implementation](https://github.com/naver/cctv) supplies the pretrained learned calibration used through our adapter. Our manual rear-tire clicks and path-distance/time calculation are a project-specific adaptation, not the paper’s exact method. Its car-speed benchmarks do not validate bicycle speeds on these cameras.

| Alternative | What it measures | What is still needed |
|---|---|---|
| Two fixed lines / timed gates | Time for the same cyclist to cross a measured section; speed = known distance / travel time. Full trajectory annotation is unnecessary. | Identifiable, independently measured endpoints. This is a practical independent check of learned scale ([FHWA tripline description](https://www.fhwa.dot.gov/publications/research/operations/its/06108/02a.cfm)). |
| Surveyed ground landmarks | Replace learned camera scale with a mapping from known ground positions, then measure motion. | Reliable ground measurements and matching image points. This changes calibration, not the distance/time principle. |
| Optical flow | Estimate movement of image features between frames instead of repeated detector boxes or manual clicks. | Association with the same cyclist, stable visible features and a metric scale; it does not remove the need for calibration ([OpenCV documentation](https://docs.opencv.org/4.x/d4/dee/tutorial_optical_flow.html)). |
| Radar, lidar or bicycle-mounted speed/GPS reference | Independently measure speed during a recording. | New synchronized measurements for the same cyclists; these cannot be recovered from old CCTV footage alone ([FHWA sensor overview](https://www.fhwa.dot.gov/publications/research/operations/its/06108/02a.cfm)). |

For existing video, a correctly measured two-line section is the simplest additional independent scale check. More tracking methods cannot, by themselves, establish correct mph when the real-world scale is wrong. The manual-seeded optical-flow and first/last endpoint comparisons are implemented separately below; surveyed ground calibration and independent sensor validation are not established by this list.

**Additional comparison run (October 26):** [manual-seeded optical flow and first/last-point timing](optical_flow_20261026/RESULTS.md) ran locally on all 30 encounters. Only the first click steered optical flow; later clicks checked drift. Two flow tracks (Pleasant Hill) passed the pixel check and yielded speeds; 27 failed drift/coverage and one was too short for speed. This simple tracker does not replace the manual results. Endpoint timing shares the same learned scale and is not independent validation.

**How to read the results:** Carroll and Columbia manual averages are close to their study references. Aloma and University differ substantially and need checking. Similar group averages do not establish per-person accuracy. Colonial’s study speed average combines bike-lane and sidewalk cyclists.

**Shorter-duration experiment prepared:** [rerun instructions](../docs/SHORT_TRACK_SPEED_RUN.md) lower the daytime bicycle minimum to1.5seconds across all13sites, reusing saved calibration. Other counting rules and nighttime policy are preserved. Updated results are pending; the table above remains the measured three-second baseline.

**Aloma duration-filter finding:** all five rejected bicycle-labelled tracks lasted less than the daytime three-second minimum: 2.9, 1.6, 2.0, 2.7 and 1.7 seconds. Four had 100% detector bicycle labels and weighted bicycle scores of 0.98–1.00. The duration gate necessarily rejects these tracks; other gates may also apply. This shows that short tracked duration can exclude strongly supported cyclists. It does not prove all five are distinct real cyclists: the study count and manual review contain four, so the extra candidate needs review before relaxing filters. The baseline results above remain unchanged. [Saved audit](analysis/aloma_duration_audit_20261026.csv).

**Missing results:** Aloma’s recovery completed about 60 minutes and recorded 5 bicycle-labelled candidate tracks, all rejected by counting filters. Its automatic speed is unavailable, not zero mph. Five candidate tracks are not necessarily five different real cyclists. Carroll and Rinehart had candidates rejected by counting filters. West Orange has no located/annotated manual cyclists. One Edgewater encounter spans only 1.4 seconds, below the current 1.5-second speed safeguard. No reannotation of completed encounters is required.

### Recording hours for every speed-reference location

**Source files** counts separate MP4 video files. **Total available hours** is the sum of their playback lengths, not the number of files or time analysed. For example, 48 one-hour files total about 48 hours, but 48 shorter files would total less. **Only Colonial North is fully measured; ~ means an estimate assuming hourly files.** Other camera sides are not added together.

**Why Columbia is unknown:** the inventory contains 49 MP4s, including multipart recordings with names such as `0000.02.001.mp4`. Their full durations have not been measured, so 49 files cannot safely be called 49 hours. The selected noon source can still be reviewed; the unknown value concerns the complete collection’s length.

| Location | Camera | Source files | Total available hours | Basis |
|---|---|---:|---|---|
| Aloma | Aloma Path | 48 | ~48 | Estimated from hourly file count |
| Baxter | Baxter | 48 | ~48 | Estimated from hourly file count |
| Carroll | Carroll NBL | 48 | ~48 | Estimated from hourly file count |
| Colonial | Colonial North | 48 | 47.99 | Measured |
| Columbia | Columbia Ave | 49 | Unknown | Multipart files; total unverified |
| Daniels | Daniels Path | 48 | ~48 | Estimated from hourly file count |
| Edgewater | Edgewater N | 48 | ~48 | Estimated from hourly file count |
| Lee | Lee Road N | 48 | ~48 | Estimated from hourly file count |
| Pleasant Hill | Pleasant Hill Path | 31 | ~31 | Estimated from hourly file count |
| Rinehart/CST | Rinehart Path | 48 | ~48 | Estimated from hourly file count |
| Silver Star | No mapped source |  | Unknown | No mapped recording |
| University | University SW Speed | 48 | ~48 | Estimated from hourly file count |
| West Orange/Park | West Orange Path | 37 | ~37 | Estimated from hourly file count |
| Winter Park | Winter Park Rd Speed | 48 | ~48 | Estimated from hourly file count |

Detailed encounter times and exclusions: [analysis/DETAILS.md](analysis/DETAILS.md). Tables: [site summaries](analysis/site_summary.csv), [15-minute counts](analysis/interval_counts.csv), [per-cyclist speeds](analysis/encounters.csv). Original annotation JSONs are unchanged.
