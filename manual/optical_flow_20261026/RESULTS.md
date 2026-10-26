# Manual-seeded optical flow and endpoint comparison

Only the first click seeds flow. Later clicks are held out to measure pixel drift; they never steer/reseed the tracker. Pyramidal Lucas–Kanade tracks a patch of wheel/body features; median coherent displacement moves the contact-point estimate. This can follow background or wheel rotation instead of the cyclist, hence drift checks and review.

Provisional acceptance requires every later click to be reached with error <= 20px. This is an engineering diagnostic threshold, not a calibrated speed-accuracy guarantee. Failed tracking speeds remain diagnostic-only and are excluded from accepted flow means.

Endpoint mph uses the first-to-last calibrated straight-line distance/time, not a known measured gate distance; it also requires at least1.5seconds to match the existing manual time safeguard. Manual path mph uses successive clicked distances/time; optical flow mph uses median local velocity windows like the automatic estimator. All share learned metric scale and are not independent ground-truth measurements. Sample/time windows may differ; do not call their differences speed accuracy.

| Location | Validation mph | HiPerGator mph | Manual path mph | Endpoint mph | Accepted flow mph | Flow accepted / attempted |
|---|---:|---|---:|---:|---:|---|
| Aloma | 13.58 | All 5 candidate tracks filtered | 19.81 | 17.36 | Unavailable | 0/4 |
| Carroll | 11.89 | No accepted speed | 12.37 | 12.19 | Unavailable | 0/2 |
| Colonial | 9.54 | 7.63 | 10.71 | 10.64 | Unavailable | 0/3 |
| Columbia | 12.24 | 3.04 | 12.47 | 12.34 | Unavailable | 0/4 |
| Edgewater | 12.02 | 17.57 | 14.00 | 8.54 | Unavailable | 0/6 |
| Lee | 8.73 | 9.88 | 12.36 | 12.31 | Unavailable | 0/4 |
| Pleasant Hill | 9.86 | 8.99 | 8.99 | 8.51 | 9.57 | 2/2 |
| Rinehart/CST | 12.92 | No accepted speed | 12.01 | 11.89 | Unavailable | 0/1 |
| University | 9.49 | 11.17 | 16.98 | 16.97 | Unavailable | 0/4 |

See comparison.csv for per-encounter status and diagnostic speeds; drift_checks.json records each held-out pixel error; flow_trajectories.csv contains predicted points. Optional *_flow.mp4 are review overlays, not confirmed identities. Missing videos are explicit failures, not zero speeds. Source timestamps are rounded to the nearest decoded frame; browser click times were approximate.

[Optical-flow reference: OpenCV Lucas–Kanade documentation](https://docs.opencv.org/4.x/d4/dee/tutorial_optical_flow.html). Calibration provenance remains the ICCV2021 author-model adapter documented in the manual README.

Main count/time comparison: [../README.md](../README.md). HiPerGator and study means are context from the main analysis; they may use different cyclists and intervals. Optical flow reads only the short annotated encounter spans, not the whole15-minute clip.
