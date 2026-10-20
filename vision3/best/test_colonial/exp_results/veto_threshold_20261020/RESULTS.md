# Full-system veto threshold replay

Baseline: 15%. Selected using development clips only: **15** (percent, or off).
No deployed settings changed. No GPU inference. Source-setting labels and counted decisions reproduced for every scored track in all selected clips.

Order: raw weighted X-CLIP → detector veto/promotion → motion rules → class-specific duration and strict night-only cyclist exception → static/quality filters.
Saved detections, SAHI, tracking/stitching and X-CLIP are frozen. This replays final saved decisions, not video inference or intermediate streamed headers.

**Exploratory only:** all four clips have already been inspected. The checking split is not an untouched test set. Saved values are rounded; baseline parity is checked, but borderline alternative-threshold decisions can still be approximate.
Identity policy: legacy_time_only. Motorcycle remains in the scored cyclist group; raw class is retained.

Development clips: night, day. Selection: Most correct counted truth people, then fewest unmatched counted tracks, then current threshold, then closest numeric threshold.

| Veto % | Correct counted people | Wrong class | Rejected | Missed | Unmatched counted |
|---|---:|---:|---:|---:|---:|
| off | 9/11 | 1 | 1 | 0 | 0 |
| 5 | 9/11 | 1 | 1 | 0 | 0 |
| 10 | 9/11 | 1 | 1 | 0 | 0 |
| 15 | 9/11 | 1 | 1 | 0 | 0 |
| 20 | 9/11 | 1 | 1 | 0 | 0 |
| 30 | 9/11 | 1 | 1 | 0 | 0 |
| 40 | 9/11 | 1 | 1 | 0 | 0 |
| 50 | 8/11 | 2 | 1 | 0 | 0 |

Checking clips: night_holdout_2200, day_holdout_1245. Only the frozen selection and original baseline are evaluated; checking scores do not select a new threshold.

| Veto % | Correct counted people | Cyclist group | Pedestrians | Unmatched counted |
|---|---:|---:|---:|---:|
| 15 | 10/10 | 2/2 | 8/8 | 0 |

A tie does not establish an optimal threshold. Unmatched tracks are candidates for review, not confirmed false positives. Do not use these development results as a claim of independently validated accuracy.
