# Labelled-clips lane and speed analysis

21 truth rows only; run b4_combo_static5.
Candidate track IDs come from legacy time matching unless explicitly human-approved. They are NOT verified person identities.
Lane proposals use observed bottom-centre points only, restricted to each truth encounter; coasted frames excluded.
Overlapping polygons are marked uncertain. Lane polygons / inferred reference scale still require visual alignment checking.
Road/bike-lane/sidewalk/grass are examined separately. Do not treat the old bike-vs-sidewalk-only facility field as road truth.
Motorcycles remain separate in this report; the older detection score groups them with cyclists.
Image speed = smoothed path length / elapsed seconds / mean box height. Not mph. Restricted-window values can differ from whole-track pipeline values.
Physical speed is blank without measured Colonial metric calibration; no fixed human height or other-street mean is substituted.
Colonial speed rows exist (35-ft bike-lane / 30-ft sidewalk zones), but no video timestamps or image gate endpoints are supplied. Record-to-person validation remains blocked. Source mph uses an approximate conversion; recomputation is a workbook arithmetic check, NOT model speed validation.
The study count workbook supplies aggregate lane counts; it cannot verify which specific video person used a lane.
No lane or physical-speed accuracy statistic is claimed.

| Clip | Truth ID | Raw class | Candidate ID | Proposed lane | Image speed (heights/s) |
|---|---|---|---|---|---|
| night | n1 | motorcycle | 4 | bike_lane | 3.2595 |
| night | n2 | cyclist | 12 | bike_lane | 1.4421 |
| night | n3 | cyclist | 18 | sidewalk | 2.2502 |
| night | n4 | cyclist | 22 | uncertain |  |
| night | n5 | cyclist | 21 | sidewalk | 2.3657 |
| night | n6 | pedestrian | 23 | sidewalk | 0.5388 |
| day | d2 | pedestrian | 2 | sidewalk | 0.5573 |
| day | d1 | cyclist | 10 | uncertain | 1.3944 |
| day | d3 | pedestrian | 13 | sidewalk | 0.2567 |
| day | d4 | pedestrian | 15 | sidewalk | 0.7623 |
| day | d5 | pedestrian | 23 | sidewalk | 0.1619 |
| night_holdout_2200 | p1 | pedestrian | 18 | sidewalk | 0.6538 |
| night_holdout_2200 | p2 | pedestrian | 27 | sidewalk | 0.4955 |
| night_holdout_2200 | p3 | pedestrian | 33 | sidewalk | 0.492 |
| night_holdout_2200 | p4 | pedestrian | 36 | uncertain | 0.5117 |
| night_holdout_2200 | p5 | pedestrian | 40 | sidewalk | 0.962 |
| day_holdout_1245 | h1 | pedestrian | 1 | uncertain | 0.8353 |
| day_holdout_1245 | h2 | cyclist | 7 | uncertain | 0.9167 |
| day_holdout_1245 | h3 | cyclist | 9 | bike_lane | 1.3669 |
| day_holdout_1245 | h4 | pedestrian | 14 | sidewalk | 0.1692 |
| day_holdout_1245 | h5 | pedestrian | 15 | road | 0.5418 |

Next: confirm complete candidate tracks in identity_review.csv (approved + full_track_reviewed=yes + reviewer + evidence), check zone overlays, and supply independently measured Colonial calibration for mph.
After identity review: python code/eval_truth.py --root . --runs b4_combo_static5 --require-identity --identity-map /Users/rithika/Desktop/objectDetect/vision3/best/test_colonial/exp_results/labelled_validation_20261020/identity_review.csv --out /Users/rithika/Desktop/objectDetect/vision3/best/test_colonial/exp_results/labelled_validation_20261020/identity_evaluation.md

Reference extraction: **23 unique Colonial speed records** (12 bike-lane, including one e-bike; 11 sidewalk). Duplicated analysis-sheet rows were merged by record/facility/distance/time. `Colonial_study_speed_records.csv` preserves source-cell provenance and original mph plus exact-unit recomputation. Arithmetic agreement is not model-speed validation.

`study_record_links.csv` is intentionally blank for clip/person links: worksheet record numbers are not the truth IDs and no timestamps are supplied. The owner believes they correspond; verify that mapping before calculating paired speed errors.

The supplied v2 JSON defines lane areas, not measured segment endpoints. On HiPerGator run `sbatch code/final_review.slurm`; the resulting folder includes zone previews and a gate-marking HTML page. Mark the actual measured segment start/end lines, confirm the camera/date, and download the gate JSON. Re-run this script with `--speed-gates /path/colonial_speed_gates.json` and a NEW output folder. Only complete unique gate crossings receive mph estimates. A separate matched reference link is still needed for speed accuracy.
