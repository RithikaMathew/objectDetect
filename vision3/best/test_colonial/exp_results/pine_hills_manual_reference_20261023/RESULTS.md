# Manual study count reference

Source: Bike Lane Study Counts/Pine_Hills_BL_E_690212_08-28-2019.xls
Interval: 2019-08-28 12:00:00 to 2019-08-28 13:00:00 (end exclusive).
Raw channel counts only. Camera sides remain separate; no comparison with model counts or accuracy is claimed.
A missing channel or empty cell is not zero. Different worksheet coverage is not silently reconciled.

| User | Side label | Facility | Recorded count | Missing cells |
|---|---|---|---:|---:|
| cyclist | NB | bike_lane | 0 | 0 |
| cyclist | NB | sidewalk | 1 | 0 |
| cyclist | SB | bike_lane | 4 | 0 |
| cyclist | SB | sidewalk | 0 | 0 |
| pedestrian | NB | bike_lane | 0 | 0 |
| pedestrian | NB | sidewalk | 0 | 0 |

Reference worksheet coverage:
- Pedestrians: 99source bins, 4selected bins; first2019-08-28 00:00:00, last2019-08-29 00:30:00; channels["NB Bike Lane", "NB Sidewalk", "NB Bike Lane", "NB Sidewalk"].
- Bicycles: 192source bins, 4selected bins; first2019-08-28 00:00:00, last2019-08-29 23:45:00; channels["NB Bike Lane", "NB Sidewalk", "NB Bike Lane", "NB Sidewalk", "SB Bike Lane", "SB Sidewalk", "SB Bike Lane", "SB Sidewalk"].

Next: confirm which raw channels correspond to the visible side of the pilot camera, then compare identical covered bins with the model output. Do not sum both sides when the video covers one. These are manual aggregate counts, not per-person boxes, identity truth or measured speeds.
