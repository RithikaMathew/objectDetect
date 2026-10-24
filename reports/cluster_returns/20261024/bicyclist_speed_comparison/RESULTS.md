# Map-free speed experiments

No model was fitted to the study speed values. Closest-study-mean ranking is exploratory; no matched-person accuracy is claimed.

| Method | State |
|---|---|
| pedestrian_height | NOT_COMPLETED |
| iccv2021 | NOT_COMPLETED |
| bmvc2014 | NOT_IMPLEMENTED_MISSING_COMPONENTS |
| sochor2017 | NOT_IMPLEMENTED_MISSING_COMPONENTS |
| keypoint2026 | NOT_IMPLEMENTED_MISSING_COMPONENTS |
| university_manual_map_gates | CALCULATED_FROM_SAVED_TIMING |

Pedestrian method is a new paper-inspired implementation, not author code; assumed average height1.7m. Head/feet inferred from boxes can be wrong; physical scale is unvalidated. ICCV uses pinned author pretrained transformer with new MaskRCNN/IoU-track extraction adapter. Neither is a complete published benchmark reproduction. Speeds outside calibration hull or interrupted tracks are refused. Road calibration does not establish sidewalk-plane calibration. Day/night scale transfer assumes camera remains fixed.

Workbook reference records are exported separately. The workbook people/time/camera correspondence is unknown; exploratory_closeness_ranking.csv ranks valid methods by similarity to the study mean using the same cyclist candidate set per facility. This is a user-requested selection rule, not validated accuracy. Speed outputs are bicyclist-only (motorcycles excluded). Pedestrian detections may support height calibration and cars support learned calibration, but neither pedestrian nor car speeds are exported. No pedestrian speed references were found in the bicyclist workbook. Rejected/uncertain lane labels are not forced into reference facilities. Geometry-check failures make any diagnostic speeds unsuitable for decisions. Review per-method calibration.json and error.txt, and method_status.json.

## University manual map-distance method

One bicyclist: 8.13mph (timing-only range 7.52–8.85mph). Study University sidewalk: 78records, mean 9.49mph, median 9.14mph, range 4.61–17.10mph. Difference from study mean: -1.36mph.

This is a single manually timed video cyclist versus a separate study group. Similarity is descriptive, not matched-person validation. The timing-only range excludes map-distance and endpoint correspondence errors. The study55ft and owner map55.17ft are separate inputs, not confirmed identical sections. This saved result needs no University GPU rerun. It is not ranked against Colonial methods because the location/people differ.
