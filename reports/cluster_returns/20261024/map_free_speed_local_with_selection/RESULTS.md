# Map-free speed experiments

No model was fitted to the study speed values. Closest-study-mean ranking is exploratory; no matched-person accuracy is claimed.

| Method | State |
|---|---|
| pedestrian_height | NOT_COMPLETED |
| iccv2021 | NOT_COMPLETED |
| bmvc2014 | NOT_IMPLEMENTED_MISSING_COMPONENTS |
| sochor2017 | NOT_IMPLEMENTED_MISSING_COMPONENTS |
| keypoint2026 | NOT_IMPLEMENTED_MISSING_COMPONENTS |

Pedestrian method is a new paper-inspired implementation, not author code; assumed average height1.7m. Head/feet inferred from boxes can be wrong; physical scale is unvalidated. ICCV uses pinned author pretrained transformer with new MaskRCNN/IoU-track extraction adapter. Neither is a complete published benchmark reproduction. Speeds outside calibration hull or interrupted tracks are refused. Road calibration does not establish sidewalk-plane calibration. Day/night scale transfer assumes camera remains fixed.

Workbook reference records are exported separately. The workbook people/time/camera correspondence is unknown; exploratory_closeness_ranking.csv ranks valid methods by similarity to the study mean using the same cyclist candidate set per facility. This is a user-requested selection rule, not validated accuracy. Pedestrian speeds are exported separately; no pedestrian reference speeds were found in the bicyclist workbook. Rejected/uncertain lane labels are not forced into reference facilities. Geometry-check failures make any diagnostic speeds unsuitable for decisions. Review per-method calibration.json and error.txt, and method_status.json.
