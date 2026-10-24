# Map-free speed experiments

No model was fitted to the study speed values. Closest-study-mean ranking is exploratory; no matched-person accuracy is claimed.

| Method | State | Details |
|---|---|---|
| pedestrian_height | NOT_COMPLETED | ValueError: Need20 head/foot observations from separate qualifying tracks |
| iccv2021 | EXPERIMENT_COMPLETED | {'author_commit': '80b8bc4964eddfda32c40e6d1c8fe8b62f777f55', 'car_tracks': 28, 'car_boxes': 458, 'geometry_check_passed': True, 'validation': 'learned_scale_not_independently_speed_validated', 'sidewalk_transfer': 'unverified_road_sidewalk_height_difference', 'reused_from': '/Users/rithika/Downloads/colonial_speed_research_47545558/iccv2021'} |
| bmvc2014 | NOT_IMPLEMENTED_MISSING_COMPONENTS | Full 3D-box/vanishing-point implementation and verified vehicle-dimension priors not integrated; no paper reproduction claimed. |
| sochor2017 | NOT_IMPLEMENTED_MISSING_COMPONENTS | Requires vehicle identification and metric 3D CAD/render assets; unavailable in current repository. |
| keypoint2026 | NOT_IMPLEMENTED_MISSING_COMPONENTS | Requires trained36-keypoint detector/template assets; no verified author checkpoint integrated. |
| university_manual_map_gates | CALCULATED_FROM_SAVED_TIMING | One manually timed bicyclist; compared with separate University sidewalk study records |

Pedestrian method is a new paper-inspired implementation, not author code; assumed average height1.7m. Head/feet inferred from boxes can be wrong; physical scale is unvalidated. ICCV uses pinned author pretrained transformer with new MaskRCNN/IoU-track extraction adapter. Neither is a complete published benchmark reproduction. Speeds outside calibration hull or interrupted tracks are refused. Road calibration does not establish sidewalk-plane calibration. Day/night scale transfer assumes camera remains fixed.

Workbook reference records are exported separately. The workbook people/time/camera correspondence is unknown; exploratory_closeness_ranking.csv ranks valid methods by similarity to the study mean using the same cyclist candidate set per facility. This is a user-requested selection rule, not validated accuracy. Speed outputs are bicyclist-only (motorcycles excluded). Pedestrian detections may support height calibration and cars support learned calibration, but neither pedestrian nor car speeds are exported. No pedestrian speed references were found in the bicyclist workbook. Rejected/uncertain lane labels are not forced into reference facilities. Geometry-check failures make any diagnostic speeds unsuitable for decisions. Review per-method calibration.json and error.txt, and method_status.json.

## Bicyclist measurement times

Each row is one cyclist estimate, not a full-hour average. Only the observed intervals used in speed calculation are listed. Saved camera clocks are not independently verified; disjoint intervals remain separate in all_speed_estimates.csv.

| Method | Cyclist | Recording date | Used clock start | Used clock end | mph |
|---|---|---|---|---|---:|

## University manual map-distance method

One bicyclist: 8.13mph (timing-only range 7.52–8.85mph). Study University sidewalk: 78records, mean 9.49mph, median 9.14mph, range 4.61–17.10mph. Difference from study mean: -1.36mph.

Manual timing source: September25,2019,08:45–09:00 annotated clip; gateA at player07:02.50–07:03.00 and gateB at07:07.25–07:07.50. Generated clock approximately08:52:02.50–08:52:07.50; burned source clock about2seconds ahead. Presentation seconds/evidence identify the exact reviewed frames.

This is a single manually timed video cyclist versus a separate study group. Similarity is descriptive, not matched-person validation. The timing-only range excludes map-distance and endpoint correspondence errors. The study55ft and owner map55.17ft are separate inputs, not confirmed identical sections. This saved result needs no University GPU rerun. It is not ranked against Colonial methods because the location/people differ.
