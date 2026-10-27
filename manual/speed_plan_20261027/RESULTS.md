# Bicycle speed plan results

[Main speed comparison, times, plots and sensitivity](trajectory/RESULTS.md) is the starting report.

Additional outputs:

- `study_group_comparisons.csv`: old/endpoint/robust means against study means, with sampling-only bootstrap differences. Different people/sessions and convenience sampling prevent accuracy claims. Intervals exclude shared scale error, may be unreliable for small samples and are omitted for n<2.
- `scale_checks/calibration_checks.csv`: car baseline and optional marking/3-D wheel checks. Missing evidence stays missing. No automatic scale adjustment or fusion.
- `scale_checks/wheel_candidates/`: crops around existing rear-contact clicks, with ellipse-like edges marked yellow and clicked contact red. These are candidates, not verified wheels, and never supply metric scale automatically. No need to annotate them unless this optional method is pursued.
- `method_status.json`: explicit implemented/pending method status. The current detector already uses ByteTrack with ID stitching; no new tracker or wheel-keypoint model is claimed.

Metric wheel fitting uses an explicit 3x4 camera projection in a metre Z-up coordinate system and a reviewed outline. It never projects the vertical wheel through a ground-only homography. Candidate search, circular wheel assumptions and fitting thresholds remain experimental. Marking lengths need a real source or must be labelled assumed standards. Sources disagreeing is a consistency flag, not a calibrated uncertainty bound.

[Projection reference](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html) · [Robust nonlinear fitting](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html).
