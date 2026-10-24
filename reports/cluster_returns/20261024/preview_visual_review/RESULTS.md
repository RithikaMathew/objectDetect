# Downloaded preview visual screen — October24,2026

Located successful folder in Downloads/SPEED_PILOT_20261024_183520/camera_previews_retry_20261024_184801_864715. All45clips across15cameras exist. Original downloaded videos unchanged.

## Confirmed bicycle encounter

**Columbia Ave — preview_300.mp4 — player00:01–00:03**, September10,2019, nominal source12:05:01–12:05:03; burned video clock approximately2seconds ahead. A rider and bicycle are visible in original frames around1.5–2.5seconds, travelling toward the right in the near-camera bicycle lane (visual facility assignment provisional). A sidewalk pedestrian visible at the right is a separate person. Foreground pole occludes the beginning and the cyclist exits rapidly, so this is not guaranteed to support stable speed estimation. No mph or reference-person match claimed.

Evidence: verified_encounters.csv, columbia_cyclist_*s.jpg, columbia_first_encounter_0-5s.mp4. Start with this encounter for detector/track review. Do not assign any source workbook length to an arbitrary lane-marking span.

## Review coverage and limits

Inspected systematic contact-sheet frames at player1,4,7,...43seconds from all45previews. Additional dense original frames inspected for the Columbia encounter. Motion-based candidate-frame generation at0.5second sampling was also attempted (not a trained person/bicycle detector); its selected frames include many cars, vegetation and shadows. Only a subset of motion sheets was visually inspected, so they do not establish exhaustive absence elsewhere. No other bicycle encounter confirmed in this initial sampled screen. That is not a verified zero count or completed frame-by-frame review. Short/distant/occluded cyclists can occur between sampled frames. camera_review_scope.csv records these limits for every camera.

Several cameras (including Aloma, Baxter, Edgewater, Pleasant Hill, Rinehart, West Orange and Winter Park) visibly show yellow transverse marks. They are candidate measurement markers, not yet confirmed to correspond to workbook segment lengths. They may reduce manual endpoint work if independently identified. Camera dimensions/quality alone do not solve physical scale or track continuity.

The fixed short excerpts did not establish a sample of3–5verifiedcyclists per camera. No speed or new GPU inference performed locally. Existing downloaded speed_results/method_status.json still reports initial insufficient calibration observations; it is not the improved tracking retry result. Next use the saved Columbia encounter and already-known Colonial/University bicycle encounters for targeted checks; do not claim all locations validated or ask owner to label all45clips as though empty samples contain cyclists.
