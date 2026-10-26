# Manual bicycle review: what the results mean

Analysed 18 JSON files: **30 separate annotated cyclist encounters**, with **13 provisional speed estimates**. Original files are unchanged. 4 exports reused IDs across widely separated encounters; those encounters are now separated. Reusing ID1 in another 15-minute interval is always treated as a new person.

## Counts and speeds together

The selected positive/missing study intervals contain 50 recorded bicycles across workbook channels; your files annotate 30 encounters. The difference (20) means **study bicycles not represented in the submitted annotations**, not automatically detector misses or your mistakes. Missing JSONs mean you could not find/annotate cyclists, and remain unconfirmed. Video/channel/clock correspondence still matters.

Each selected bin is 15 minutes. Bins with JSON shows how many selected intervals have submitted annotations. Count references cover those selected intervals; study speed references are a separate group of cyclists, with no matching video timestamps. Speed averages are per cyclist, not per hour. Pending speeds are not zero.

| Location | Selected bins (JSONs) | Study count | Manual count | Not represented | Automatic count, same bins | Automatic speed n | Automatic mph | Manual speed n | Manual mph | Study speed n | Study mph |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|
| Aloma | 3 (3) | 4 | 4 | 0 | awaiting bin export | 0 | no usable speed | 4 | 19.81 | 26 | 13.58 |
| Carroll | 1 (1) | 2 | 2 | 0 | 0 | 0 | no usable speed | 2 | 12.37 | 15 | 11.89 |
| Colonial | 2 (2) | 3 | 3 | 0 | awaiting bin export | 3 | 7.63 | 3 | 10.71 | 23 | 9.54 |
| Columbia | 4 (3) | 6 | 4 | 2 | awaiting bin export | 3 | 3.04 | 4 | 12.47 | 9 | 12.24 |
| Edgewater | 4 (4) | 10 | 6 | 4 | awaiting bin export | 2 | 17.57 | 0 | waiting for calibration / sufficient span | 50 | 12.02 |
| Lee | 4 (2) | 10 | 4 | 6 | awaiting bin export | 2 | 9.88 | 0 | waiting for calibration / sufficient span | 2 | 8.73 |
| Pleasant Hill | 1 (1) | 2 | 2 | 0 | awaiting bin export | 2 | 8.99 | 0 | waiting for calibration / sufficient span | 41 | 9.86 |
| Rinehart/CST | 3 (1) | 3 | 1 | 2 | awaiting bin export | 0 | no usable speed | 0 | waiting for calibration / sufficient span | 25 | 12.92 |
| University | 2 (1) | 5 | 4 | 1 | awaiting bin export | 3 | 11.17 | 0 | waiting for calibration / sufficient span | 78 | 9.49 |
| West Orange/Park | 3 (0) | 5 | 0 | 5 | awaiting bin export | 1 | 11.59 | 0 | no annotations | 25 | 10.77 |

Automatic mph comes from the finished automatic batch; manual mph uses your repaired clicks. The two means may use different cyclists and intervals, so their difference is not tracking error or accuracy. Both use learned camera scale; manual clicking does not independently validate that scale. Automatic speed n is the selected speed sample, not the total bicycle count. Automatic counts are compared only when the same full selected bins have been exported. Until then they remain unavailable, not zero. The automatic summary currently available locally is a rounded transcription of the owner-pasted batch report; final export supplies original values.

Not represented = study count minus annotated encounters, conditional on matching camera coverage. Study mph is from separate speed observations, not person-linked ground-truth speeds for these clips. A small speed difference is descriptive agreement, not validated accuracy.

Manual positions are projected with the learned camera calibration bundled in the review page. Speed = sum of successive ground distances / elapsed seconds, converted from metres/second to mph. This matches the page method after repairing IDs. Clicking noise can inflate path length. Physical scale, lens distortion and transfers from road to raised paths/sidewalks remain unvalidated. Numerical geometry checks do not prove correct real-world scale.

Colonial study averages combine bike lane and sidewalk. Separate references: bike lane12cyclists, mean11.11mph; sidewalk11cyclists, mean7.82mph. No lane was supplied with your manual clicks, so we cannot claim a facility-matched comparison.

## Interpretation: good or bad?

Carroll and Columbia show descriptive agreement with the separate study means. Colonial is moderately higher, with unresolved bike-lane/sidewalk matching. Aloma is substantially higher and needs a calibration/point-placement check before use. None establishes matched-person speed accuracy. Pending sites have no speed conclusion yet.

## Every annotated cyclist and time used

Times are inferred source clock times, not independently verified. A different cyclist ID in each interval is a separate encounter; no repeat-person identity is assumed.

| Camera | Video interval starts | Encounter | Original ID | Measurement start | Measurement end | Points | mph | Status |
|---|---|---|---|---|---|---:|---|
| Aloma Path | 2019-10-30 12:00:00 | c01 | 1 | 2019-10-30 12:03:58.380 | 2019-10-30 12:04:01.180 | 15 | 15.66 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |
| Aloma Path | 2019-10-30 12:30:00 | c01 | 1 | 2019-10-30 12:32:30.679 | 2019-10-30 12:32:32.679 | 11 | 21.12 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |
| Aloma Path | 2019-10-30 12:45:00 | c01 | 1 | 2019-10-30 12:45:37.713 | 2019-10-30 12:45:39.513 | 10 | 21.33 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |
| Aloma Path | 2019-10-30 12:45:00 | c02 | 1 | 2019-10-30 12:50:46.933 | 2019-10-30 12:50:51.133 | 22 | 21.15 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |
| Carroll NBL | 2019-09-10 12:30:00 | c01 | 1 | 2019-09-10 12:38:59.468 | 2019-09-10 12:39:01.468 | 11 | 12.96 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |
| Carroll NBL | 2019-09-10 12:30:00 | c02 | 2 | 2019-09-10 12:43:52.716 | 2019-09-10 12:43:54.916 | 12 | 11.78 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |
| Colonial North | 2019-07-10 12:30:00 | c01 | 1 | 2019-07-10 12:40:20.689 | 2019-07-10 12:40:24.789 | 21 | 10.51 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |
| Colonial North | 2019-07-10 12:45:00 | c01 | 1 | 2019-07-10 12:53:11.586 | 2019-07-10 12:53:15.586 | 20 | 10.47 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |
| Colonial North | 2019-07-10 12:45:00 | c02 | 2 | 2019-07-10 12:53:50.690 | 2019-07-10 12:53:54.090 | 16 | 11.15 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |
| Columbia Ave | 2019-09-10 12:00:00 | c01 | 1 | 2019-09-10 12:02:32.678 | 2019-09-10 12:02:36.278 | 14 | 8.26 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |
| Columbia Ave | 2019-09-10 12:00:00 | c02 | 1 | 2019-09-10 12:05:01.191 | 2019-09-10 12:05:03.691 | 13 | 16.80 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |
| Columbia Ave | 2019-09-10 12:15:00 | c01 | 3 | 2019-09-10 12:27:20.984 | 2019-09-10 12:27:22.884 | 9 | 11.68 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |
| Columbia Ave | 2019-09-10 12:30:00 | c01 | 4 | 2019-09-10 12:34:23.077 | 2019-09-10 12:34:24.877 | 10 | 13.16 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |
| Edgewater N | 2019-09-18 12:00:00 | c01 | 1 | 2019-09-18 12:06:04.166 | 2019-09-18 12:06:07.166 | 16 | pending | CALIBRATION_NOT_IN_REVIEW_PACK |
| Edgewater N | 2019-09-18 12:15:00 | c01 | 2 | 2019-09-18 12:21:51.261 | 2019-09-18 12:21:52.661 | 8 | pending | INSUFFICIENT_POINTS_OR_SPAN |
| Edgewater N | 2019-09-18 12:15:00 | c02 | 2 | 2019-09-18 12:27:49.861 | 2019-09-18 12:27:52.161 | 12 | pending | CALIBRATION_NOT_IN_REVIEW_PACK |
| Edgewater N | 2019-09-18 12:30:00 | c01 | 6 | 2019-09-18 12:32:25.912 | 2019-09-18 12:32:29.412 | 18 | pending | CALIBRATION_NOT_IN_REVIEW_PACK |
| Edgewater N | 2019-09-18 12:45:00 | c01 | 6 | 2019-09-18 12:46:11.059 | 2019-09-18 12:46:16.059 | 22 | pending | CALIBRATION_NOT_IN_REVIEW_PACK |
| Edgewater N | 2019-09-18 12:45:00 | c02 | 7 | 2019-09-18 12:50:03.264 | 2019-09-18 12:50:08.864 | 20 | pending | CALIBRATION_NOT_IN_REVIEW_PACK |
| Lee Road N | 2019-07-10 12:00:00 | c01 | 1 | 2019-07-10 12:09:19.436 | 2019-07-10 12:09:22.736 | 14 | pending | CALIBRATION_NOT_IN_REVIEW_PACK |
| Lee Road N | 2019-07-10 12:00:00 | c02 | 2 | 2019-07-10 12:12:56.454 | 2019-07-10 12:12:58.854 | 8 | pending | CALIBRATION_NOT_IN_REVIEW_PACK |
| Lee Road N | 2019-07-10 12:15:00 | c01 | 4 | 2019-07-10 12:25:59.047 | 2019-07-10 12:26:02.447 | 10 | pending | CALIBRATION_NOT_IN_REVIEW_PACK |
| Lee Road N | 2019-07-10 12:15:00 | c02 | 4 | 2019-07-10 12:27:55.161 | 2019-07-10 12:27:59.061 | 13 | pending | CALIBRATION_NOT_IN_REVIEW_PACK |
| Pleasant Hill Path | 2019-11-12 12:45:00 | c01 | 1 | 2019-11-12 12:58:33.057 | 2019-11-12 12:58:36.457 | 11 | pending | CALIBRATION_NOT_IN_REVIEW_PACK |
| Pleasant Hill Path | 2019-11-12 12:45:00 | c02 | 2 | 2019-11-12 12:58:33.195 | 2019-11-12 12:58:36.595 | 12 | pending | CALIBRATION_NOT_IN_REVIEW_PACK |
| Rinehart Path | 2019-10-02 12:00:00 | c01 | 1 | 2019-10-02 12:11:43.636 | 2019-10-02 12:11:46.036 | 9 | pending | CALIBRATION_NOT_IN_REVIEW_PACK |
| University SW Speed | 2019-09-25 12:45:00 | c01 | 1 | 2019-09-25 12:45:44.129 | 2019-09-25 12:45:48.729 | 13 | pending | CALIBRATION_NOT_IN_REVIEW_PACK |
| University SW Speed | 2019-09-25 12:45:00 | c02 | 2 | 2019-09-25 12:46:32.107 | 2019-09-25 12:46:35.107 | 8 | pending | CALIBRATION_NOT_IN_REVIEW_PACK |
| University SW Speed | 2019-09-25 12:45:00 | c03 | 3 | 2019-09-25 12:50:56.685 | 2019-09-25 12:50:59.685 | 8 | pending | CALIBRATION_NOT_IN_REVIEW_PACK |
| University SW Speed | 2019-09-25 12:45:00 | c04 | 4 | 2019-09-25 12:51:55.737 | 2019-09-25 12:51:59.937 | 14 | pending | CALIBRATION_NOT_IN_REVIEW_PACK |

## Missing JSONs / cyclists not found by the reviewer

These are review coverage gaps, not confirmed absence:

- Columbia Ave, 2019-09-10 12:45:00: study2, no annotations received.
- Lee Road N, 2019-07-10 12:30:00: study2, no annotations received.
- Lee Road N, 2019-07-10 12:45:00: study3, no annotations received.
- Rinehart Path, 2019-10-02 12:15:00: study1, no annotations received.
- Rinehart Path, 2019-10-02 12:45:00: study1, no annotations received.
- University SW Speed, 2019-09-25 12:00:00: study1, no annotations received.
- West Orange Path, 2019-10-15 12:15:00: study2, no annotations received.
- West Orange Path, 2019-10-15 12:30:00: study2, no annotations received.
- West Orange Path, 2019-10-15 12:45:00: study1, no annotations received.

## What needs checking next

- Obtain the final saved calibration JSONs for Edgewater, Lee, Pleasant Hill, Rinehart and University. These were absent when the manual pack was generated. Existing clicks can be reused without reannotation. Some short encounters may still lack the1.5-second minimum required by this workflow.
- Count comparisons cover only selected source-hour bins in the review manifest, not full study totals. No positive review bins were included for Baxter, Daniels or Winter Park in this pack; Silver Star had no mapped source.
- Raw worksheet channel counts may cover more than the visible camera area. The differences above are conditional until visible channels and clocks are confirmed.
- Automatic detector misses cannot be inferred from manual counts alone. Known Carroll evidence remains study2, manual2, automatic counted0 in12:30–12:45. Its second cyclist had a raw track rejected by filters. For all sites, matched automatic bin counts are needed to separate detector misses from filtered tracks.

Files: site_summary.csv compares means and coverage; interval_counts.csv preserves each bin; encounters.csv records per-person times/speeds; normalized_observations.json contains corrected IDs with original IDs retained; id_splits.csv explains each repair; review_inputs.json snapshots the source manifest and calibration. Repeated exact observations across exports were deduplicated: 2.

## Finish the pending speed calculations

No reannotation or GPU run is required. The final adaptive batch has newer calibration files than the review pack. On HiPerGator, after pulling the new helper, run:

```bash
python code/export_manual_calibrations.py --batch exp_results/ADAPTIVE_SPEED_20261024_195012
```

Paste that small JSON output into sofar.md, or export it with --out manual_calibrations.json. This transfers matrices, automatic speed summaries and same-bin count data, not videos. The analysis supports --calibrations FILE and checks camera and source clock before applying them.
