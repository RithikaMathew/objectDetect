# Passing clearance and MetroPlan clarification — November 9, 2026

Source: correspondence supplied by Rithika in chat. MetroPlan describes speed calibration with two marked locations and their known separation within one camera view. They also describe occurrence-based recordings rather than continuous 48-hour footage. Apply that recording description to confirmed sources; retain existing archive playback totals as summed file durations, not continuous observation exposure.

The requested analysis uses movement within each camera view. It does not require identifying a cyclist at two camera sites. Camera latitude/longitude helps locate sites and request field dimensions, but does not by itself calibrate image distances. Request the deployment IDs and dates, view direction, original calibration screenshots/marked endpoints and measured distances, frame/time metadata, and occurrence recording rules and coverage logs. Obtain road-plane control points spanning the lateral area of interest for clearance. Two longitudinal speed gates alone do not establish lateral scale across the image.

## Speed reference coverage

Treat Mighk's measurements as a selected facility-specific sample until the recorded lateral positions are verified at each site. Do not assume all workbook entries are bike-lane-only: the existing Colonial reference summary identifies 12 bike-lane and 11 sidewalk observations. Verify each site's facilities, source recordings and measurement locations with Mighk. Estimate additional travel-lane, bike-lane, sidewalk and path cyclist speeds only where the relevant geometry and timestamps support them. Report these separately; an aggregate workbook mean is not a reference for every lateral position. Elevated sidewalks and sidepaths need their own geometry checks.

## Clearance first

The target is lateral edge-to-edge separation between cyclist (including rider) and passing motor vehicle at the same instant while alongside. Image horizontal distance, center-to-center distance, and legacy `goal4_conflict.py` minimum point separation are different quantities. Its speed-prior scale must not be used as physical clearance calibration.

`pipeline/passing_clearance.py` provides a separate calculation for reviewed metric footprints in road-aligned coordinates. It pairs simultaneous cyclist/vehicle observations only when their longitudinal intervals overlap, and reports the minimum sampled lateral interval gap per pair. It includes every cyclist facility. It does not infer footprints from detection rectangles: projecting elevated rectangle corners onto a road plane is not sufficient. Footprints must bound road-plane positions of the actual cyclist/rider and vehicle extents, with independent calibration and review. Use local road axes on curves. Wide or angled footprints represented as intervals are approximations requiring review.

Input CSV columns:

```text
source_id,track_id,class,t,s_min,s_max,l_min,l_max,facility,calibration_id,geometry_reviewed
```

`t` is source playback time in seconds; all four bounds are meters. `s` runs along the road and `l` across it. Each source must identify one uninterrupted clip and camera configuration; track IDs must remain unique within it. Use identical frame timestamps for paired objects; no interpolation across missing frames occurs. `geometry_reviewed` must be `yes` on every row.

Calibration JSON schema example (illustrative, not an existing calibration):

```json
{
  "source_id": "reviewed_clip_id",
  "calibration_id": "survey_v1",
  "units": "m",
  "axes": "road_aligned",
  "reviewed": true,
  "evidence": "Path to independently checked control points, geometry, and footprint review"
}
```

Run after preparing those inputs:

```bash
python3 pipeline/passing_clearance.py footprints.csv --calibration calibration.json --out clearance.csv
```

Outputs retain IDs, facility, calibration ID, minimum sampled clearance, its timestamp and alongside sample count. Every pair is an alongside candidate requiring video review: confirm same-direction overtaking, track identity, visibility, complete event coverage and separation by barriers before calling it a passing event. Zero indicates overlapping lateral intervals, not a confirmed collision. The minimum over observed frames can exceed the true continuous-time minimum. No uncertainty bound is currently computed; record calibration and footprint uncertainty during review before threshold interpretation.

No real clearance measurements have been produced. Existing point tracks alone lack reviewed lateral object extents and independent metric calibration. This module is an input-ready calculation, not an automatic video extraction pipeline. Next work is to obtain calibration, review a pilot clip containing alongside cars/cyclists, prepare footprints, and validate against manual measurements before batch processing.

Report clearance distributions as a separate interaction outcome; clearance alone does not establish a near miss. Keep TTC/PET exploratory and secondary. Occurrence-triggered clips may truncate passes or omit interactions; report observed eligible encounters and coverage rather than extrapolating to 48-hour rates.

## Draft response to MetroPlan (not sent)

Thank you for clarifying. We intend to estimate cyclist and vehicle movement within each individual camera view, rather than match people between separate camera sites. In addition to speed, we would like to measure lateral clearance between a cyclist and a vehicle passing alongside them. Could you share the site coordinates and deployment IDs, calibration screenshots showing the marked points and known distances, any available lane-width or road-plane measurements, and recording/frame-time metadata? Could you also clarify how occurrences are triggered, whether those clips preserve original timing, and whether recording coverage logs or longer source recordings are available? These details will help us determine which speeds and passing clearances can be measured reliably.
