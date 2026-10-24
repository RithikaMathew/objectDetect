# Study batch outputs

Completed sources: 1/1.
outputs.csv contains actual counts and exact annotated paths from completed jobs. Failed/missing statuses are not scored as zero people.
all_tracks.csv records each user/vehicle track, predicted type, count status, dominant lane, observed lane fractions and midpoint15-minute bin. counts_by_site_user_lane.csv and counts_15min_by_user_lane.csv summarize counted tracks. Unmarked cameras remain unassigned; no lane accuracy claimed.
Predicted counts are not accuracy. No per-person truth, camera calibration or new lane boundaries are invented. Source-file IDs reset; boundary duplicates need review. Clocks are filename-inferred unless independently confirmed.
Do not compare partial/misaligned source coverage against full-study totals as an accuracy result. Use saved15-minute bin_counts files and confirm camera, channels, recording day and clock first.
Yellow headers say GT not labelled unless hand-labelled bins are applicable; aggregate workbook totals are not substituted as person-level truth.
