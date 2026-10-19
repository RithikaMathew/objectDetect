# Current to-do — updated 2026-10-19

## Active

- [x] Combine RT-DETR, X-CLIP and speed; measure speed/veto contribution.
- [x] Try techniques and record gains/failures (SAHI, fusion, static filtering, gamma/CLAHE).
- [x] Analyze both-wrong, detector-only-right and X-CLIP-only-right cases on existing truth.
- [ ] Test a genuinely higher-resolution video than Colonial 2019 (720x480), from ANY year. Prefer a non-fisheye view. Inspect metadata first; no per-year quota.
- [x] Compare track-duration settings and integrate ByteTrack + ID stitching.
- [ ] Validate at another site, ideally using the higher-resolution test above.
- [ ] Test high-sensitivity candidates plus a maximum 12-minute review budget per hour; benefit not established yet.
- [ ] Investigate walking-away failures using the existing labelled clips and targeted spot-checks.
- [x] Implement multi-scale/flip inference and a Grounding DINO proposal audit; both are now in the one-command suite.
- [ ] Run that suite and evaluate results; temporal feature aggregation remains a larger integration, not included.

## Back burner — excluded from the current PowerPoint and immediate commands

- Hand-label approximately 40 tracked people and compare each model's per-track accuracy.
- Add own nighttime images and fine-tune the detector.

Existing truth/ labels remain valid. Do not relabel those four clips. Only a selected NEW higher-resolution clip would need new truth to produce a scored result; no new clip has been selected yet. Exact existing video paths: ../VIDEO_PATHS.md.
