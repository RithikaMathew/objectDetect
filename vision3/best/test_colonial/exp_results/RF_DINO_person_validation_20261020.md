# Person-box validation on selected existing frames

Reviewed frames: 32/32. Unreviewed frames excluded.
Person proposals only, one-to-one IoU>=0.50. Cyclists/scooter riders contribute person boxes, not mode labels.
Thresholds are the saved audit thresholds. This is NOT AP, unique-person recall, continuous-video counting accuracy or an independent holdout test.

| Detector | Correct boxes TP | False boxes FP | Missed boxes FN | Precision | Recall |
|---|---:|---:|---:|---:|---:|
| rf | 4 | 10 | 16 | 0.286 | 0.200 |
| dino | 13 | 35 | 7 | 0.271 | 0.650 |
