# Exploratory speed calibration — crossing feasibility

Checked 7 existing bicycle truth rows against both drawn facilities using their full saved candidate tracks.
These candidate identities are time-matched, not human-approved. Motorcycles and pedestrians are excluded.

**Complete two-line crossings: 0. No mph or distance fit is possible with these tracks and lines.**

| Clip | Truth | Candidate | Facility | First-line crossings | Second-line crossings |
|---|---|---|---|---:|---:|
| night | n2 | 12 | bike_lane | 0 | 0 |
| night | n2 | 12 | sidewalk | 0 | 0 |
| night | n3 | 18 | bike_lane | 0 | 0 |
| night | n3 | 18 | sidewalk | 0 | 1 |
| night | n4 | 22 | bike_lane | 0 | 0 |
| night | n4 | 22 | sidewalk | 0 | 1 |
| night | n5 | 21 | bike_lane | 0 | 0 |
| night | n5 | 21 | sidewalk | 0 | 1 |
| day | d1 | 10 | bike_lane | 0 | 0 |
| day | d1 | 10 | sidewalk | 0 | 0 |
| day_holdout_1245 | h2 | 7 | bike_lane | 0 | 0 |
| day_holdout_1245 | h2 | 7 | sidewalk | 0 | 1 |
| day_holdout_1245 | h3 | 9 | bike_lane | 0 | 1 |
| day_holdout_1245 | h3 | 9 | sidewalk | 0 | 0 |

Crossings use consecutive observed foot positions, finite lines, scaled image coordinates, and gaps no longer than0.5seconds. Lines are not extended; missing track segments are not extrapolated. Times in crossings.csv are relative to each15-minute clip.

Workbook scan found 23 unique Colonial speed records, but no verified links to these truth people. Record numbers are study identifiers, not detector track IDs. Do not pair people by whichever speed gives the closest answer.

To proceed: identify two lines inside a segment where the SAME cyclist is tracked continuously, and establish that cyclist’s Excel record using independent timestamp/identity evidence. Fit one fixed distance per facility from calibration people: distance_ft = recorded_mph ×5280/3600 ×crossing_seconds. Freeze it, then evaluate speed on DIFFERENT matched people. Keep all observations of one person in the same split. Fit and held-out people must use the same lines and facility; independently measured line spacing is an alternative.

Do not assign the workbook35ft/30ft to arbitrary visible lane spans. No new detector/GPU batch was submitted. Source gate JSON and existing truth files remain unchanged.
