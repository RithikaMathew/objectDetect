# Cyclist speed (mph) from monocular fixed cameras: feasibility, literature, and plan

*Prepared Oct 26, 2026 for Rithika. Scope note: this is a focused literature pass (a handful of targeted searches this session), not a systematic review. Items marked **\[verified\]** were confirmed against a source page in this session; items marked **\[from memory\]** are well-known works I did not re-open here, so check the DOI/arXiv link before citing. I did not extract accuracy numbers I could not see.*

## Implementation status — October 27, 2026

The latest combined CPU entry point is `sbatch code/speed_plan.slurm` from `vision3/best/test_colonial`; see [run guide](docs/SPEED_PLAN_RUN.md). It includes robust time-aware fitting, the old/endpoint comparison on the same annotations, review-clip packet timestamp audit, per-cyclist plots, assumption-based sensitivity scenarios, sampling-only study-group comparisons, and unverified wheel-edge candidate crops. The current detector already uses ByteTrack and ID stitching.

Marking and full 3-D wheel geometry checks are implemented as optional evidence-driven functions; actual scale evidence is still missing, so no metric wheel or marking result is claimed. A compact ground homography cannot recover vertical wheel scale. No new tracker/keypoint training or automatic camera location search is included. University map/video endpoint correspondence remains unconfirmed. The roadmap below is research context, not a claim that all papers have been reproduced.

Original-file duration audit is complete for all 1,919 files/41 cameras. Columbia's 49 parts sum to 47.98 playback hours; Aloma Path's 48 sources sum to 47.99. See [verified hours](docs/VIDEO_DURATION_README.md). These lengths do not identify the timestamp-less speed-study cyclists.

## 1. Executive summary

**Is metric speed identifiable from monocular pixel trajectories alone? No.** A single camera cannot distinguish a small, slow scene from a large, fast one: scaling every 3D point by *s* produces the identical image, so pixel tracks fix speed only up to an unknown scale factor. To get mph you must inject at least one metric fact, and it must be *measured or assumed*, never inferred from pixels.

What the scene does give you:

- If the cyclist moves on a plane (the road), the image-to-ground mapping is a homography H, recoverable from vanishing points or landmarks **up to a single global scale**. Straightness, angles and ratios are recovered; absolute length is not.
- One metric anchor fixes that scale: a known distance on the ground, a known object size (car, bicycle wheel, lane stripe), camera height, or a map measurement.

Three consequences for your project:

1. **Scale is a per-camera multiplicative bias**, not random noise. If a camera's scale is off by 15%, every cyclist from that camera is off by 15%, and no amount of better tracking fixes it. Your README already says this correctly.
2. **Your 2.56 vs 3.39 mph MAE cannot rank manual vs automated.** With validation means around 9-14 mph, 2.5 mph is roughly 20%, comparable to plausible scale error, and the comparison is location-mean vs a few different cyclists (n = 1-6 per site for your side).
3. **Metric-depth foundation models are not yet a defensible scale source** for fixed traffic cameras. I found no peer-reviewed cyclist-speed validation for them, and their errors behave like exactly the per-camera scale bias above.

**Revised constraints:** you have only the CCTV videos. There are no start or end points, no measured distances, no coordinates, and the location names are vague (for example "Colonial Road" without a position along it). That removes map-anchored calibration as a starting point. **Recommendation in one line:** a hybrid pipeline that takes scale from priors visible in the video itself (your car-based calibration, bicycle wheel size, standard markings), reports how closely they agree (agreement is not full uncertainty, since they can share a bias), and uses a robust slope-based speed estimator. With no independent distance for any camera, this can show a method is less noisy and internally consistent; it cannot prove absolute mph accuracy.

## 2. Three separate problems

| Problem | What it determines | Typical error type | Fixed by |
| --- | --- | --- | --- |
| A. Metric scale / ground mapping | pixels to metres | systematic, per camera | better anchors, multiple independent anchors |
| B. Trajectory | where the contact point is at each time | random + occlusion + bias from wrong point | better detector/tracker, contact-point choice, smoothing |
| C. Validation | whether mph is right | n/a | independent per-cyclist reference |

A good tracker (B) with wrong scale (A) gives precise, wrong speeds. Evaluate each separately.

## 3. Mathematics: from image trajectory to mph

**Pinhole model.** A world point X projects to x \~ K \[R | t\] X, with K = \[\[f,0,cx\],\[0,f,cy\],\[0,0,1\]\].

**Ground plane (Z = 0).** x \~ H X\_g with H = K \[r1 r2 t\] (3x3). Inverting gives ground coordinates (X, Y) from pixels. Scaling t by s scales ground coordinates by s and leaves the image unchanged: that is the scale ambiguity.

**Vanishing points.** For two orthogonal ground directions with vanishing points v1, v2, and principal point p at the image centre with square pixels:

```
(v1 - p) . (v2 - p) + f^2 = 0   ->   f
```

The horizon line gives pitch and roll. Everything is then known except camera height h (equivalently, global scale). One known ground length L (image length l mapped through H) gives scale = L / (measured length under unit-scale H).

**Speed from a smoothed trajectory.** With ground positions P\_i = H^-1 x\_i at timestamps t\_i:

```
v = d s / d t   (fit s(t) along the path, not sum of segment lengths)
mph = v[m/s] x 2.23694
```

**Important for your current formula.** `total distance = sum of segment lengths` is biased **upward** with click or box jitter: noise adds spurious path length (a zig-zag is always longer than the line). Fit a low-order curve (or robust linear fit) to along-track position vs time and use its slope. Use the chord (net displacement / time) as a sanity bound. Your automatic estimator already fits short windows and takes their median, so this change mainly affects the manual calculation.

**Sensitivity to contact-point error.** For a camera at height h with focal length f (pixels), a vertical pixel error dv at ground distance Y gives ground error roughly dY = Y^2 dv / (f h). Errors grow quadratically with distance from the camera, which is why oblique views and far-field tracks are the worst. Bounding-box bottom-centre is not the tyre contact point (it can sit on the shadow, foot, or pedal, and shifts with posture); rear-wheel contact points are better, and wheel keypoints are the principled fix.

**Timing.** Use the container's presentation timestamps (PTS), not nominal fps, because variable-frame-rate CCTV makes nominal-fps timing a hidden speed error. Also record the playback factor.

## 4. Literature review

### 4.1 Comparison table

| Method / Paper | Year | Calibration required? | Known distance required? | Metric scale source | Reported accuracy | Dataset | Code available? | Suitability for your project |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Revaud & Humenberger, *Robust Automatic Monocular Vehicle Speed Estimation for Traffic Surveillance*, ICCV 2021 \[verified\] | 2021 | Yes, but automatic from detector outputs | No | Car 3D shape with normalised dimensions | "Excellent" per abstract; numbers not extracted here | Own CCTV dataset + 2 other benchmarks | naver/cctv (per your README) | Medium: automated scale source, but cars, not bikes; scale inherits a car-size prior |
| Sochor et al., *Comprehensive Data Set for Automatic Single Camera Visual Speed Measurement* (BrnoCompSpeed), IEEE T-ITS 2018, DOI 10.1109/TITS.2018.2825609 \[verified\] | 2018 | Reviews methods | Used for reference (LIDAR gates, GPS checks) | n/a (dataset) | Reference speeds from optical gates; 20,865 vehicles | BrnoCompSpeed | Dataset and metadata released | High as methodology model for validation (gates) |
| Sochor et al., *Traffic surveillance camera calibration by 3D model bounding box alignment*, CVIU 2017 \[verified page, numbers from snippet\] | 2017 | Automatic (2 vanishing points + scale inference) | No | Vehicle 3D models | Snippet indicates about 1.10 km/h mean error for best automatic variant; confirm in paper | BrnoCompSpeed | Check paper | Medium (vehicle-based scale) |
| WSDOT-sponsored *Self Calibrating Monocular Camera Measurement of Traffic Parameters* \[verified page\] | n/a | Self-calibration from lane stripes | Standard marking dimensions | Lane-stripe spacing | Not extracted | Freeway cameras | Not checked | Idea is useful (marking-based scale); vehicles, freeways |
| Dubska et al., automatic roadside camera calibration via vanishing points, IEEE T-ITS 2015 \[from memory\] | 2015 | Automatic | No | Needs scale prior | Not extracted | Brno | Check | Foundational for VP calibration |
| Criminisi et al., *Single View Metrology*, IJCV 2000 \[from memory\] | 2000 | Reference plane + vanishing line | One reference length | Known reference length | Theory | n/a | n/a | Foundational for homography + one anchor |
| Depth Pro, ICLR 2025 \[verified\] | 2025 | No (estimates focal length) | No | Learned metric prior | Benchmarks only (AbsRel, etc.); no speed accuracy | Many depth sets | github.com/apple/ml-depth-pro | Low as primary scale source; useful as a sanity check |
| UniDepth, CVPR 2024 \[verified\] | 2024 | No | No | Learned prior with self-prompted camera | Depth benchmarks only | 10 zero-shot sets | github.com/lpiccinelli-eth/unidepth | Same as above |
| Metric3D / v2 \[from memory: ICCV 2023, arXiv 2404.15506\] | 2023-24 | No | No | Canonical camera space transform | Depth benchmarks only | Large mixed | Yes (check) | Same as above |
| Depth Anything V2 \[from memory: arXiv 2406.09414\] | 2024 | No | No | Relative depth by default | Relative depth benchmarks | Large mixed | Yes | Relative only: cannot give mph |
| Semi-automated micromobility tool, *Sensors* 2026, DOI 10.3390/s26185713 \[verified abstract only\] | 2026 | Single bird's-eye camera | Not reviewed | Not reviewed | Not reviewed | Not reviewed | Not reviewed | Closest cyclist-specific paper I found; overhead view, so less oblique distortion. Read the full text before relying on it |
| Ponte et al., ACRS 2014 conference paper \[verified\] | 2014 | Not reviewed | Not reviewed | GPS and laser gun as references | Reports good correlation; no numbers extracted | Four real-world sites | Not found | Rare example of cyclist speeds checked against GPS/laser |
| Osowski & Waterson, Procedia CS 2015 \[verified\] | 2015 | Homography | Yes (surveyed) | Ground landmarks | Not extracted | Cyclist video | Not found | Shows landmark-homography for cyclists |
| ByteTrack (ECCV 2022), OC-SORT (CVPR 2023), BoT-SORT (arXiv 2022), RT-DETR (CVPR 2024) \[from memory\] | 2022-24 | n/a | n/a | n/a | MOT benchmarks, not speed | MOT17/20 etc. | Yes | Improve problem B only |

### 4.2 Reading the evidence honestly

- **Vehicle vs cyclist.** Everything with rigorous speed ground truth (BrnoCompSpeed with LIDAR gates, GPS) is for **vehicles**. The cyclist-specific work I found is older, uses GPS or laser spot checks, or (the 2026 *Sensors* paper) uses overhead cameras. I did not find a peer-reviewed validation of **cyclist mph from an uncalibrated oblique CCTV camera**. Treat that as a gap and as your contribution, not as something you can cite as solved.
- **Car-based scale transfers with risk.** Car-based calibration works because car dimensions are standardised and numerous. It gives you scale **with the uncertainty of the car-size prior** (US vehicle lengths vary a lot by class). Pooling many cars per camera helps if the class mix is representative.
- **Metric depth models** predict an absolute scale from learned priors. Their published numbers are depth errors on benchmarks; none of them translate directly to a speed bias. For a fixed camera the error is the same systematic scale error for every cyclist. Use them only as an independent plausibility check (e.g., does implied camera height look sane?).
- **Optical flow** helps problem B but not A. Your 2/30 drift-check result is consistent with the known limits of generic flow on small, fast, low-contrast cyclists.

## 5. Approaches ranked for your situation

### #1. Scale from priors inside the video + robust slope estimator (implement first)

- **Scale sources, all from the video:** (a) your existing car-based calibration (naver/cctv) as the baseline; (b) bicycle wheel size (experimental): on close, side-on cyclists, fit an ellipse to the wheel and compare its pixel size with a prior of roughly 0.65-0.70 m (an assumption; tyre and bike type vary). A wheel is a vertical object, so the ground homography cannot convert it to metres; this needs a camera model with the vertical scale and viewing angle, and it will often return "insufficient evidence"; (c) standard markings where visible (dashed lane-line length and gap, crosswalk bars, bike symbols, lane width). Confirm the standard for each site rather than assuming it, since you do not know exactly where the camera is.
- **What it gives you:** a check on whether the car-based scale is internally consistent. How closely the sources agree is a consistency check, not an uncertainty bound, because they can share the same bias. None of them is a measurement.
- **Annotation:** none new for cars and wheels (automated); a few clicks per camera for markings.
- **Why first:** it works now with only your MP4s and clicks, it produces intervals instead of single numbers, and it flags cameras whose sources disagree.
- **Limits:** all sources are priors and can share the same bias. Agreement is a consistency result, not validation. Wheel fits fail on distant, blurred or end-on cyclists.

### #2. Locate each camera, then anchor with imagery (optional upgrade)

You have no coordinates, but frames often show clues: street signs, business names, bus stops, signal-pole layout, distinctive buildings. Use them to find the exact spot in a web map and Street View. For a camera you can pin down with certainty, read the positions of features visible in both the frame and the imagery in a local metric frame, fit H from those image-to-ground correspondences (distances alone do not define the mapping), and hold out some landmark pairs. Cameras you cannot pin down stay on #1 with their wider interval. Imagery dates may differ from the video date, so avoid features that may have been repainted or moved.

**University exception (from your note):** you have a map location and an approximately 55.17 ft measurement for University. Its correspondence to two points in the video still needs confirming. If confirmed, it is the one place a distance-based check is possible, so keep that evidence.

### #3. Better detection/tracking with wheel keypoints, plus robust estimation

Swap in BoT-SORT/ByteTrack/OC-SORT on RT-DETR boxes, add a wheel or tyre-contact keypoint model (fine-tune a pose head on a few hundred of your existing clicks), and use a state-space smoother (Kalman/RTS) or spline slope. This reduces problem B noise and fragmentation. It cannot fix scale. Worth doing because your automated pipeline loses or fragments tracks, but it ranks third because it does not touch the dominant bias.

**Hybrid vs end-to-end.** A hybrid is more defensible: each stage has a physical interpretation, can be tested in isolation, and its uncertainty can be propagated. An end-to-end network regressing mph would need per-camera mph ground truth that you do not have, and any apparent accuracy would be unverifiable.

## 6. Experimental design

### 6.1 Extract per video

Frames with PTS timestamps, fps and variable-frame-rate check, image size, RT-DETR boxes, track IDs, your manual contact clicks, camera ID, date and time, lens distortion estimate if available.

### 6.2 Recover metric scale

Per camera: (1) run the existing car-based calibration and record its scale, (2) estimate scale from wheel size on usable tracks and from any standard markings in view, (3) record how closely the sources agree (an agreement measure, not a full uncertainty), (4) where the camera can be located (see #2), also fit H from image-to-ground correspondences and hold out at least two landmark pairs, (5) flag any camera whose sources disagree by more than a threshold you set before looking at results.

### 6.3 Distance and speed

Map each contact point through H to metres; fit along-track position vs time with a robust slope (Huber or RANSAC) or a smoothing spline; also report chord speed. Handle diagonal and curved paths by using arc-length along a smoothed path (do not use the x-axis only).

### 6.4 Perspective, occlusion, tracking failure

Down-weight points near the horizon (far ground, where one pixel spans many metres); drop points inside the lens-distortion margin; interpolate only across short gaps (state the maximum gap); split tracks at ID switches and require a minimum ground distance and duration; flag any track that was gap-filled.

### 6.5 Uncertainty and invalid-speed detection

Monte Carlo: jitter contact points by the empirical click/keypoint error (several pixels, estimate it from repeated clicks), vary the assumed scale over a plausible range, recompute speed 500-1000 times, and report the median and 5th-95th percentile as a sensitivity range. It shows how assumed errors move mph; it is not a verified accuracy interval. Reject or flag if: interval wider than a chosen fraction of the speed, segment speeds vary implausibly (change greater than a physical acceleration bound), speed outside a plausible cyclist range, ground distance small relative to jitter, or H is ill-conditioned (near-horizon points).

### 6.6 Comparison with existing results

Run old manual, old automated, and new method on the **same trajectories**. Report cyclist-level and location-level numbers in separate tables.

### 6.7 Validation without pretending averages are ground truth

- **Do not** compute per-cyclist error against a location mean. Compare **distributions**: difference of means with a bootstrap or Welch interval that includes **both** samples' variability. With your n of 1-6 per site, intervals will be wide; say so.
- **Independent per-cyclist reference from the same video:** gate timing needs a measured distance, which you do not have, so it is not available now. It becomes possible per camera only if the camera is located (see #2) and the line separation can be read from imagery. Even then it is independent of the learned calibration but not of the imagery.
- **Strongest independent reference:** new recordings with a GPS/bike-computer rider or radar/laser at a camera. Even 10-20 passes at one or two cameras gives a true scale-bias estimate.

### 6.8 Metrics

For paired cyclist-level references: bias (mean signed error, mph), MAE, RMSE, mean absolute percentage error, and **per-camera bias** (the quantity that scale error drives), each with bootstrap 95% intervals. For location level: signed difference in means with CI. Always report signed error, because MAE hides a consistent over- or under-estimate.

### 6.9 How many cyclists?

Half-width of a 95% interval on bias is about 1.96 x SD(error) / sqrt(n). If the SD of paired errors is about 2 mph (an assumption; estimate it from a pilot), n = 30 gives about +/-0.7 mph overall and n = 100 gives about +/-0.4. Because scale bias is per camera, you need roughly **10+ independently referenced cyclists per camera** to estimate that camera's bias, and at least a few cameras to say anything general. Your current 30 annotated cyclists over 10 sites (about 3 per site) can illustrate the method, not validate it. These sample sizes only matter once some independent reference exists.

### 6.10 Preventing leakage

- Split by **camera** (calibrate on some, test on others) and, within a camera, by **cyclist**: landmarks used to fit scale must not be the ones used to score; hold out landmark pairs.
- Freeze all thresholds (minimum duration, smoothing window, gap length) on a development subset before touching the test set. The 3 s to 1.5 s duration change is exactly the kind of tuning to do on dev data only.
- Do not tune H or the scale to make the Wilson location averages match; that turns the validation set into a training set.

## 7. Implementation roadmap (Python / OpenCV / PyTorch)

1. **Ingest:** read PTS with PyAV or ffprobe; undistort if lens parameters exist.
2. **Detect/track:** RT-DETR boxes to BoT-SORT or ByteTrack; keep your X-CLIP cyclist/pedestrian filter; optionally a small keypoint head for rear-wheel contact.
3. **Calibrate per camera:** car-based calibration plus wheel and marking checks; save the scale and its spread as JSON per camera (add a landmark homography with held-out error only where the camera can be located).
4. **Speed:** project, smooth, estimate slope, Monte Carlo interval.
5. **QA report:** per cyclist, a plot of ground path, along-track position vs time with the fit, and the interval.

Core snippets:

```python
import numpy as np, cv2
from scipy.stats import theilslopes

def fit_homography(px, ground_m):
    # px: clicked image points; ground_m: their coordinates in a local metric frame
    H, _ = cv2.findHomography(px.astype(np.float32), ground_m.astype(np.float32), cv2.RANSAC, 0.05)
    return H

def to_ground(H, px):
    p = cv2.perspectiveTransform(px.reshape(-1, 1, 2).astype(np.float32), H)
    return p.reshape(-1, 2)

def robust_speed_mph(t, xy):
    # t: click/frame times in seconds (need not be evenly spaced); xy: ground positions in metres.
    t = np.asarray(t, float); xy = np.asarray(xy, float)
    n = len(t)
    if n < 3:
        return np.nan, np.nan
    deg = 1 if n <= 4 else 2
    tc = t - t.mean()
    # 1) time-aware smoothing: low-order polynomial in t for each coordinate
    xs = np.column_stack([np.polyval(np.polyfit(tc, xy[:, k], deg), tc) for k in range(2)])
    # 2) arc length of the smoothed path
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(xs, axis=0), axis=1))]
    # 3) outlier-resistant slope of s(t); Theil-Sen uses the actual times
    v = theilslopes(s, t)[0]
    chord = np.linalg.norm(xs[-1] - xs[0]) / (t[-1] - t[0])
    return v * 2.23694, chord * 2.23694

def mc_sensitivity(t, px, H_sampler, jitter_px, n=500):
    out = []
    for _ in range(n):
        H = H_sampler()                                  # draws H over an assumed scale range
        p = px + np.random.normal(0, jitter_px, px.shape)
        out.append(robust_speed_mph(t, to_ground(H, p))[0])
    return np.nanpercentile(out, [5, 50, 95])
```

Compare the arc-length speed with the chord speed: a ratio well above 1 means residual jitter or a genuinely curved path. The polynomial degree is a tuning choice (a polynomial fit over a short track can mis-fit sharp turns); set it on development data only. This is a starting sketch, not validated code.

## 8. Final recommendation

**Implement #1 first:** the car-based calibration with wheel and marking checks, the robust slope estimator, and Monte Carlo intervals that include the scale spread. It works with only your MP4s and clicks. Then try #2 on the cameras you can pin down, and do #3 to reduce fragmentation and jitter.

With no measured distance for any camera, you can show that the new estimator is less noisy and more internally consistent, and report mph with an interval. You cannot show it is more accurate in absolute terms. Say so, and treat Wilson's location averages as a rough distributional check only. A real accuracy claim needs at least one independent per-cyclist reference: GPS or radar passes at a camera, or a located camera with an imagery-measured gate.

## Sources checked this session

- Revaud & Humenberger, ICCV 2021: https://openaccess.thecvf.com/content/ICCV2021/html/Revaud\_Robust\_Automatic\_Monocular\_Vehicle\_Speed\_Estimation\_for\_Traffic\_Surveillance\_ICCV\_2021\_paper.html
- Sochor et al., BrnoCompSpeed: https://arxiv.org/abs/1702.06441 and https://fit.vut.cz/research/publication/11701 (DOI 10.1109/TITS.2018.2825609)
- Sochor et al., CVIU 2017: https://fit.vut.cz/research/publication-file/c144444/279739/2017-CVIU-SpeedMeasurement.pdf
- Depth Pro, ICLR 2025: https://proceedings.iclr.cc/paper\_files/paper/2025/hash/bc8b2058fd96978a4146f18298cb2d39-Abstract-Conference.html ; arXiv 2410.02073
- UniDepth, CVPR 2024: https://cvpr.thecvf.com/virtual/2024/poster/31417
- Micromobility semi-automated tool, Sensors 2026: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC13611163/ (DOI 10.3390/s26185713)
- Ponte et al., ACRS 2014: https://hdl.handle.net/2440/107947
- Osowski & Waterson 2015: https://eprints.soton.ac.uk/377977
- WSDOT self-calibrating monocular measurement: https://rosap.ntl.bts.gov/view/dot/17447/dot\_17447\_DS1.pdf
