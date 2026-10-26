# Manual bicycle review: what the results mean

Analysed 18 JSON files: **30 separate annotated cyclist encounters**, with **29 provisional speed estimates**. Original files are unchanged. 4 exports reused IDs across widely separated encounters; those encounters are now separated. Reusing ID1 in another 15-minute interval is always treated as a new person.

## Counts and speeds together

The selected positive/missing study intervals contain 50 recorded bicycles across workbook channels; your files annotate 30 encounters. The difference (20) means **study bicycles not represented in the submitted annotations**, not automatically detector misses or your mistakes. Missing JSONs mean you could not find/annotate cyclists, and remain unconfirmed. Video/channel/clock correspondence still matters.

Each selected bin is 15 minutes. Selected bins (JSONs) shows the total intervals followed by how many have submitted annotations. Count references cover those selected intervals; study speed references are a separate group of cyclists, with no matching video timestamps. Speed averages are per cyclist, not per hour. Pending speeds are not zero.

| Location | Selected 15-min bins (JSONs) | Validation: study cyclist count | HiPerGator: cyclist count / validation in covered bins | Manual: annotated cyclists | Not annotated | Validation: mean mph (sample) | HiPerGator: mean mph (sample) | Manual: mean mph (sample) |
|---|---:|---:|---|---:|---:|---|---|---|
| Aloma | 3 (3) | 4 | Unavailable: run interrupted | 4 | 0 | 13.58 (26) | Unavailable: run interrupted | 19.81 (4) |
| Carroll | 1 (1) | 2 | 0 / 2 (1/1 bins) | 2 | 0 | 11.89 (15) | All 12 candidate tracks rejected by counting filters | 12.37 (2) |
| Colonial | 2 (2) | 3 | 3 / 3 (2/2 bins) | 3 | 0 | 9.54 (23) | 7.63 (3) | 10.71 (3) |
| Columbia | 4 (3) | 6 | 6 / 3 (2/4 bins) | 4 | 2 | 12.24 (9) | 3.04 (3) | 12.47 (4) |
| Edgewater | 4 (4) | 10 | 2 / 5 (3/4 bins) | 6 | 4 | 12.02 (50) | 17.57 (2) | 14.00 (5) |
| Lee | 4 (2) | 10 | 2 / 10 (4/4 bins) | 4 | 6 | 8.73 (2) | 9.88 (2) | 12.36 (4) |
| Pleasant Hill | 1 (1) | 2 | 2 / 2 (1/1 bins) | 2 | 0 | 9.86 (41) | 8.99 (2) | 8.99 (2) |
| Rinehart/CST | 3 (1) | 3 | 0 / 3 (3/3 bins) | 1 | 2 | 12.92 (25) | All 3 candidate tracks rejected by counting filters | 12.01 (1) |
| University | 2 (1) | 5 | 1 / 1 (1/2 bins) | 4 | 1 | 9.49 (78) | 11.17 (3) | 16.98 (4) |
| West Orange/Park | 3 (0) | 5 | 1 / 5 (3/3 bins) | 0 | 5 | 10.77 (25) | 11.59 (1) | Not measurable: 5 study cyclists not located in manual review |

Automatic mph comes from the finished automatic batch; manual mph uses your repaired clicks. The two means may use different cyclists and intervals, so their difference is not tracking error or accuracy. Both use learned camera scale; manual clicking does not independently validate that scale. Numbers in parentheses after mph are cyclist speed samples, not total cyclist counts. Validation count is the study count reference; Validation mph is the separate study speed reference, not known per-person speeds for these clips. Automatic counts are compared only when the same full selected bins have been exported. Until then they remain unavailable, not zero. The final exported batch values are used when supplied. HiPerGator cyclist count / validation compares only the same exported complete bins; its parentheses show how many selected bins are included. Missing bins are not counted as zero. Aloma was interrupted by NODE_FAIL despite its stale STARTED status.

Not represented = study count minus annotated encounters, conditional on matching camera coverage. Study mph is from separate speed observations, not person-linked ground-truth speeds for these clips. A small speed difference is descriptive agreement, not validated accuracy.

Manual positions are projected with the saved learned camera calibration, updated from the final batch export when supplied. Speed = sum of successive ground distances / elapsed seconds, converted from metres/second to mph. This matches the page method after repairing IDs. Clicking noise can inflate path length. Physical scale, lens distortion and transfers from road to raised paths/sidewalks remain unvalidated. Numerical geometry checks do not prove correct real-world scale.

Colonial study averages combine bike lane and sidewalk. Separate references: bike lane12cyclists, mean11.11mph; sidewalk11cyclists, mean7.82mph. No lane was supplied with your manual clicks, so we cannot claim a facility-matched comparison.

## Interpretation: good or bad?

Carroll and Columbia show descriptive agreement with the separate study means. Colonial is moderately higher, with unresolved bike-lane/sidewalk matching. Aloma is substantially higher and needs a calibration/point-placement check before use. None establishes matched-person speed accuracy. Pleasant Hill and Rinehart are also close to the separate study averages. Edgewater is higher; Lee and University show larger differences and need review. West Orange has no submitted manual annotations. Similar group means still do not validate a shared learned camera scale.

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
| Edgewater N | 2019-09-18 12:00:00 | c01 | 1 | 2019-09-18 12:06:04.166 | 2019-09-18 12:06:07.166 | 16 | 8.97 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |
| Edgewater N | 2019-09-18 12:15:00 | c01 | 2 | 2019-09-18 12:21:51.261 | 2019-09-18 12:21:52.661 | 8 | pending | INSUFFICIENT_POINTS_OR_SPAN |
| Edgewater N | 2019-09-18 12:15:00 | c02 | 2 | 2019-09-18 12:27:49.861 | 2019-09-18 12:27:52.161 | 12 | 9.84 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |
| Edgewater N | 2019-09-18 12:30:00 | c01 | 6 | 2019-09-18 12:32:25.912 | 2019-09-18 12:32:29.412 | 18 | 21.45 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |
| Edgewater N | 2019-09-18 12:45:00 | c01 | 6 | 2019-09-18 12:46:11.059 | 2019-09-18 12:46:16.059 | 22 | 15.59 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |
| Edgewater N | 2019-09-18 12:45:00 | c02 | 7 | 2019-09-18 12:50:03.264 | 2019-09-18 12:50:08.864 | 20 | 14.13 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |
| Lee Road N | 2019-07-10 12:00:00 | c01 | 1 | 2019-07-10 12:09:19.436 | 2019-07-10 12:09:22.736 | 14 | 12.22 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |
| Lee Road N | 2019-07-10 12:00:00 | c02 | 2 | 2019-07-10 12:12:56.454 | 2019-07-10 12:12:58.854 | 8 | 14.64 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |
| Lee Road N | 2019-07-10 12:15:00 | c01 | 4 | 2019-07-10 12:25:59.047 | 2019-07-10 12:26:02.447 | 10 | 10.59 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |
| Lee Road N | 2019-07-10 12:15:00 | c02 | 4 | 2019-07-10 12:27:55.161 | 2019-07-10 12:27:59.061 | 13 | 11.97 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |
| Pleasant Hill Path | 2019-11-12 12:45:00 | c01 | 1 | 2019-11-12 12:58:33.057 | 2019-11-12 12:58:36.457 | 11 | 8.77 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |
| Pleasant Hill Path | 2019-11-12 12:45:00 | c02 | 2 | 2019-11-12 12:58:33.195 | 2019-11-12 12:58:36.595 | 12 | 9.22 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |
| Rinehart Path | 2019-10-02 12:00:00 | c01 | 1 | 2019-10-02 12:11:43.636 | 2019-10-02 12:11:46.036 | 9 | 12.01 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |
| University SW Speed | 2019-09-25 12:45:00 | c01 | 1 | 2019-09-25 12:45:44.129 | 2019-09-25 12:45:48.729 | 13 | 15.61 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |
| University SW Speed | 2019-09-25 12:45:00 | c02 | 2 | 2019-09-25 12:46:32.107 | 2019-09-25 12:46:35.107 | 8 | 14.84 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |
| University SW Speed | 2019-09-25 12:45:00 | c03 | 3 | 2019-09-25 12:50:56.685 | 2019-09-25 12:50:59.685 | 8 | 19.77 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |
| University SW Speed | 2019-09-25 12:45:00 | c04 | 4 | 2019-09-25 12:51:55.737 | 2019-09-25 12:51:59.937 | 14 | 17.72 | EXPLORATORY_UNVALIDATED_ROAD_PLANE |

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

- Final calibration export has been applied to the saved clicks; no reannotation was needed. Check encounters.csv for any remaining short-span or geometry exclusions.
- Count comparisons cover only selected source-hour bins in the review manifest, not full study totals. No positive review bins were included for Baxter, Daniels or Winter Park in this pack; Silver Star had no mapped source.
- Raw worksheet channel counts may cover more than the visible camera area. The differences above are conditional until visible channels and clocks are confirmed.
- Automatic detector misses cannot be inferred from manual counts alone. Known Carroll evidence remains study2, manual2, automatic counted0 in12:30–12:45. Its second cyclist had a raw track rejected by filters. Exported same-bin count totals are included where complete coverage is available. They cannot alone distinguish detector misses from filtered tracks or confirm individual identities.

Files: site_summary.csv compares means and coverage; interval_counts.csv preserves each bin; encounters.csv records per-person times/speeds; normalized_observations.json contains corrected IDs with original IDs retained; id_splits.csv explains each repair; review_inputs.json snapshots the source manifest and calibration. Repeated exact observations across exports were deduplicated: 2.

## Calibration update complete

Applied the final batch calibration export to the existing annotations. No new GPU processing or manual annotations were required. One Edgewater encounter has only1.4seconds of clicked observations and is excluded by the current1.5-second safeguard; this is not a missing-calibration problem. Any shorter-span exploratory result would need a separately disclosed policy.

Automatic and manual methods share learned camera scale. Both remain exploratory, and their means may use different cyclists and time windows. No matched-person mph accuracy is claimed.

## Why values are missing — all locations

- Aloma automatic: confirmed compute-node failure before the first segment completed. Recovery worker47763750 and report47763751 were submitted by the owner; do not submit a duplicate.
- Carroll automatic:12bicycle-labelled candidates were recorded, but0passed counting filters. Saved track34 lasted2.47seconds, below the daytime3-second minimum; exact additional rejection gates require the saved rules audit. Repeating unchanged inference is not a fix.
- Rinehart automatic:3bicycle-labelled candidates,0accepted by counting filters. This is not zero detector proposals. The saved rules audit is needed to identify duration/static/confidence/size rejection details; no specific gate is assumed.
- West Orange manual: study5in selected bins, no submitted cyclist positions. Owner could not identify bicycles in the footage. Possible small/blurry riders or camera-channel coverage mismatch remain unresolved. An automatic speed cannot be copied into the manual column. Short candidate clips from saved tracks can help locate them.
- Edgewater individual manual speed: one encounter has1.4seconds of clicked positions, below the current1.5-second safeguard. Site mean uses the other5encounters. No missing calibration remains.
- Columbia automatic coverage: the worker reached its provisional speed quota after30minutes, so later selected study bins were not processed. Its early stop is different from a detection failure.
- Edgewater/University complete-bin coverage: final export omitted some rows under899seconds. Counts from those partial rows can be recovered by the expanded audit, but remain labelled partial, not full-bin truth comparisons.

After pushing/pulling updated code, run `sbatch code/audit_missing_speed.slurm` from test_colonial. Output: exp_results/MISSING_SPEED_AUDIT_JOBID/. To inspect every missing value and create small review clues on HiPerGator, use code/audit_missing_speed.py. It reads saved tracks/rules and extracts at most six12-second clips per missing manual interval; no detector run, threshold change or invented label. If no candidate exists for a missed cyclist, no clip can prove its absence. Clips are for locating encounters; return to the original manual editor for annotations with correct source time.

## Recover Aloma automatic results

Aloma calibration completed, but Slurm reported NODE_FAIL during its first inference window. Its automatic result is unavailable because of that interruption; it is not a completed zero-cyclist result. Manual Aloma speeds are already calculated.

After pushing/pulling updated code, from test_colonial on HiPerGator:

```bash
python code/adaptive_speed_batch.py recover --directory exp_results/ADAPTIVE_SPEED_20261024_195012 --index 0 --go
```

This submits one Aloma worker plus its report, reuses the saved original calibration, and writes a new ADAPTIVE_SPEED_recovery_TIMESTAMP folder. Original interrupted files and other site results are preserved. It restarts inference from the first segment; partial frame state is not resumable. Recovery results are separate and must be reviewed/merged into this comparison after the job completes. This recovery has been prepared and tested locally, not submitted here.
