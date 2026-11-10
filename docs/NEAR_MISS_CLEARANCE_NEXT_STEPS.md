# Near-miss and passing-clearance next steps

Updated November 9, 2026.

## Decision

The primary outcome should be **minimum lateral passing clearance**, not a
verified near-miss count. A near miss is a rare, thresholded interpretation of
an interaction; clearance is available for ordinary passing events too. TTC and
PET should remain secondary surrogate measures and should never be used to
declare a near miss without visual review.

The current Colonial pilot is a feasibility study. It found two visible
same-direction passes and one bicycle-wheel false vehicle detection, but it did
not establish physical distances in metres. The existing outputs are enough to
design and test the workflow; they are not enough to report a site clearance
distribution.

## What to calculate

For each cyclist-car pair that is confirmed by video as a same-direction pass:

1. Define the passing interval: the car approaches from behind, is alongside,
   and clears the cyclist. Exclude parked cars, oncoming cars, barriers and
   detections that are actually part of the cyclist.
2. At each reviewed frame in that interval, record the cyclist's near-side
   outer contact/body edge and the car's cyclist-side outer edge. Use the
   smallest horizontal road-plane separation, not center-to-center distance and
   not the gap between detector boxes.
3. Report the minimum clearance and the number of usable frames. Also retain an
   image-space clearance in pixels and a confidence/quality flag so a failed
   metric projection cannot become a plausible-looking number.
4. Record facility position (bike lane, sidewalk/sidepath, or travel lane) and
   direction separately. Mighk's site speed samples should be compared only to
   the matching facility and direction, if that information is available.

The metric calculation requires a road-plane mapping whose control points span
the cyclist and car lateral positions in the image. Two longitudinal speed gates
are not sufficient. If that mapping is unavailable, the honest interim result
is reviewed pixel clearance plus a ranked set of passing events, not metres.

## Validation plan

### A. Use existing speed work as kinematic quality control

The manual and automatic speeds are useful for checking that a selected pair is
temporally aligned, continuously tracked, and moving in the expected direction.
For each manually annotated cyclist, compare:

- manual click time span versus automatic observed span;
- direction and monotonic progress along the road axis;
- speed from manual rear-tire points versus the automatic trajectory;
- track gaps, identity switches and frame coverage.

The current three Colonial comparisons show 90--98% automatic coverage and
automatic-minus-manual speeds of about -0.84 to +0.37 mph, depending on the
smoother. That supports trajectory continuity for these examples. It does **not**
validate lateral scale: both methods use the same learned calibration matrix,
and the cyclist points are outside the car-calibration support hull. Do not fit
clearance scale to the workbook means.

### B. Validate clearance geometry separately

Before processing a larger sample, obtain one of these, in descending order of
preference:

1. surveyed or image-matched road-plane control points spanning the bicycle
   facility and adjacent motor-vehicle lane;
2. a calibration scene with measured lateral marks visible in the same camera
   view and the same camera configuration;
3. reviewed manual contact points and a clearly documented, bounded sensitivity
   analysis, reported as exploratory only.

The MetroPlan site coordinates are useful for mapping camera sites and checking
which facility each camera sees, but coordinates alone do not calibrate lateral
image geometry. Adjacent cameras are also unnecessary for one-camera clearance;
they would matter only for cross-camera travel-time or identity matching.

### C. Establish annotation agreement

For a pilot sample, have two reviewers independently label the same frames for:

- cyclist/car identity and pass direction;
- passing interval start/end;
- near-side cyclist and car edge/contact;
- occlusion, truncation and geometry usability.

Resolve disagreements before calculating a summary. Keep rejected and uncertain
events in the denominator and publish the reason; do not silently turn them
into zero clearance or no event.

## Literature-based interpretation

FHWA's Surrogate Safety Assessment Model defines TTC from projected trajectories
and PET as the time between one road user's occupation of a location and the
next user's arrival. Its commonly cited 1.5-second TTC setting is a screening
convention, not a universal cyclist near-miss threshold. Use TTC/PET as
explicitly labeled sensitivity screens, with thresholds such as 1.0, 1.5 and
2.0 seconds, and report the threshold and eligible denominator.

Recent experimental work by Liu, Saunier and Bilodeau (2025) found that tested
automated detection/tracking methods systematically overestimated interactions
and underestimated TTC. That finding is directly relevant here: the wheel false
detection in the Colonial pilot is an observed example, not merely a theoretical
limitation. Identity review, track continuity, road-user type and physical edge
review therefore precede any near-miss count.

Sources:

- [FHWA SSAM report: TTC, PET and conflict workflow](https://www.fhwa.dot.gov/publications/research/safety/08051/02.cfm)
- [Liu, Saunier and Bilodeau, 2025 preprint](https://arxiv.org/abs/2503.09807)

## Concrete next run

The interactive edge review is **optional**. You can skip it without changing
the existing detector/speed results. Keep it if you want a human-reviewed,
image-space record of the two visible passes, or if you may later obtain a
lateral calibration and convert those labels to metres. It does not create
calibration by itself and is not required for the exploratory model output.

The tool is here:

[Interactive edge annotation tool](../reports/clearance_pilot/final_review_20261109/clearance_edge_annotation_tool.html)

If you prefer the CSV template rather than the click interface, the local
command is:

```bash
python3 pipeline/build_clearance_annotation_template.py \
   --packet reports/clearance_pilot/final_review_20261109 \
   --out reports/clearance_pilot/final_review_20261109/clearance_edge_annotations.csv
```

Review the nine rows against the linked images/video. Fill the visible
cyclist-side and car-side edge columns, `frame_usable`, `edge_confidence` and
the pass/occlusion fields. Leave `road_plane_clearance_m` blank until a
reviewed lateral calibration exists. The automatic box coordinates in the
sheet are orientation references, not edge measurements.

1. Request/collect the site coordinates and document camera view, facility and
   direction for each location. Do not treat this as lateral calibration.
2. Use the existing Colonial review packet to finalize labels for the two real
   passes and the wheel false alarm; retain the middle clip as a no-adjacent-pass
   control, not as evidence of no near miss.
3. Create a small, manually reviewed clearance table with pixel gaps, frame
   timestamps, edge definitions, pass status and geometry usability.
4. Test the metric projection only after lateral control points are identified;
   compare its results with the pixel table and sensitivity bounds.
5. Expand to a stratified sample of the existing 18 annotated clips: facility,
   direction, cyclist speed and visibility should be represented. Run inference
   only after the manual review schema and calibration gate pass.
6. Report clearance distributions and reviewed-event counts separately. Report
   TTC/PET as secondary sensitivity analyses, never as a replacement for the
   clearance outcome.

No new GPU sweep is justified by the current evidence. The immediate work is
manual edge/event labeling and geometry acquisition; the saved pilot outputs
already support that work.

### HiPerGator command

Do not submit a new GPU job now. After a reviewed lateral calibration is
available, a CPU-only reanalysis of the existing returned trajectories can be
run from `test_colonial`:

```bash
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
sbatch --gpus=0 --mem=8G --time=00:30:00 \
   --output=clearance_reanalysis_%j.log \
   code/clearance_pilot.slurm \
   /absolute/path/to/CLEARANCE_PILOT_20261109_175030_116203 reanalyze
```

Replace the final path with the existing batch directory on HiPerGator. This
recomputes model-based metrics from saved trajectories; it does not create
physical calibration or replace manual edge annotation. A new GPU submission
is justified only if additional clips are selected after the annotation schema
and lateral calibration pass review.