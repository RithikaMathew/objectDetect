# Completed same-video speed comparison — October 27, 2026

These results were supplied by the owner from completed HiPerGator reports. Raw tracks and annotated video paths have not yet been returned. Baseline reports are retained. Both returned batches use a 1.5-second daytime bicycle minimum.

## Assessment

The shorter setting produces useful additional candidates, particularly the two Carroll encounters previously reported missed. Owner visual review confirms Columbia pedestrians misclassified as bicyclists and a missed cyclist, while at least one cyclist was detected. Owner reports Edgewater bicycle counting looked accurate; time-overlap clues alone do not establish duplication or misses. University still has fewer automatic than annotated tracks. Automatic mph is not ready to be called validated accuracy.

The table below uses the **same 18 submitted annotation clips** (nine cameras; nominal270minutes). Study counts are restricted to those intervals. Study speed samples are separate location-level observations with no matched-person timestamps. Manual speeds use the original path estimator; robust estimates are an additional comparison, not ground truth.

| Location | Study count in these clips | Manual count | Automatic count | Study mph (n) | Automatic mph (n) | Manual mph (n) | Robust manual mph |
|---|---:|---:|---:|---|---|---|---:|
| Aloma | 4 | 4 | 5 | 13.58 (26) | 21.45 (5) | 19.81 (4) | 19.43 |
| Carroll | 2 | 2 | 2 | 11.89 (15) | 12.22 (2) | 12.37 (2) | 12.59 |
| Colonial | 3 | 3 | 3 | 9.54 (23) | 7.35 (3) | 10.71 (3) | 10.77 |
| Columbia | 4 | 4 | 7 | 12.24 (9) | 7.35 (7) | 12.47 (4) | 12.62 |
| Edgewater | 10 | 6 | 6 | 12.02 (50) | 14.10 (6) | 14.00 (5) | 11.51 |
| Lee | 5 | 4 | 3 | 8.73 (2) | 10.17 (3) | 12.36 (4) | 12.40 |
| Pleasant Hill | 2 | 2 | 2 | 9.86 (41) | 9.12 (2) | 8.99 (2) | 8.80 |
| Rinehart/CST | 1 | 1 | 1 | 12.92 (25) | 12.06 (1) | 12.01 (1) | 12.48 |
| University | 4 | 4 | 3 | 9.49 (78) | 14.00 (3) | 16.98 (4) | 17.11 |

Totals: study 35, manual 30, automatic 32. Similar totals can hide offsetting misses and extras; neither 32/35 nor count agreement is detector accuracy. One of the six Edgewater manual encounters has no usable speed (1.4-second span). Some final clips end slightly before the full study bin; exact recording coverage remains relevant to bin comparisons.

## Priority checks

1. **Columbia:** 7 automatic counts vs4study/manual. Candidates at12:20:23–12:21:05 (0.228mph),12:21:16–12:23:31 (0.088mph), and12:34:23–12:36:19 (0.056mph) require full-track review. These may involve static objects, stops, bad contact points or identity switches; the report alone cannot identify the cause. The annotated12:27:20–12:27:22 cyclist has no overlapping selected automatic speed interval. The12:34 track overlaps a manual cyclist only initially and then continues much longer; overlap alone must not earn identity credit. Do not remove values solely to match the study mean.
2. **Aloma:** 5 automatic vs4study/manual. The additional12:59:47–12:59:48 candidate has no submitted manual time overlap; inspect before calling it a true extra cyclist or false positive.
3. **Edgewater:** two automatic speed tracks overlap the single annotated12:06 cyclist in the first bin; inspect for duplicates/different people. No selected automatic interval overlaps the manual12:32:25 cyclist or12:46:11 cyclist. Overall6automatic vs6manual is not complete recovery.
4. **Carroll:** the two new automatic measurement intervals overlap both manually annotated encounters (12:38:59 and12:43:52). This is encouraging recovery evidence; verify full-track identity before claiming recall.
5. **Full-hour batch:** Colonial41.67mph and WestOrange43.489mph need review; those values are not rejected merely for being high. Coverage/quota differs from the same-video run, so use the same-video table above for the main comparison.

## What remains

Finish identity/type review of the flagged tracks and confirm the University map/video distance endpoints. Existing time-overlap clues are in temporal_review_clues.csv, not an identity-matching accuracy score. There is no reason to launch another broad model sweep before those checks.

Evidence: user_report.txt preserves the pasted reports; same_video_intervals.csv and same_video_speed_times.csv retain exact returned bins and speed timestamps. combined_comparison.csv is the merged professor-facing table. shortday_sites.csv is the separate full-hour/quota experiment.

## Subsequent owner review

[Columbia and Edgewater visual feedback](owner_video_review.md): Columbia classification/miss problems observed; Edgewater counting reviewed favorably. Earlier temporal checks are leads, not confirmed identity errors. The main manual README now also includes West Orange/Park, Baxter, Daniels and Winter Park results from the broader run.
