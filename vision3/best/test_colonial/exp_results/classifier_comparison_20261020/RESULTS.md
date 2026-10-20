# Detector versus X-CLIP: existing four labelled clips

Run: b4_combo_static5. No new inference or Slurm job.
Detector label = cyclist in at least50%of its track observations; otherwise pedestrian. This is a track-majority classifier, not single-frame detection accuracy.
X-CLIP label = argmax of the RAW box-height-weighted video probabilities from rules_audit.csv, BEFORE veto/speed fusion.
Same matched, scored tracks for both methods; includes rejected tracks, so duration filtering does not bias this comparison.
Motorcycle is grouped with cyclists to match the existing21-person evaluation; raw class preserved in CSV.
PROVISIONAL time-only person matching; identities have not been human-verified. Simultaneous people and ID switches can affect these results.
Included: 21/21 truth rows. Excluded rows and reasons are in per_person.csv.
This does NOT measure standalone detector recall, false-positive detection rate, continuous-video counting accuracy or performance on unseen cameras.

| Clip | Detector correct | X-CLIP correct |
|---|---:|---:|
| Night 21:15–21:30 | 3/6 | 3/6 |
| Day 14:00–14:15 | 5/5 | 3/5 |
| Night 22:00–22:15 | 4/5 | 5/5 |
| Day 12:45–13:00 | 4/5 | 3/5 |
| **Total** | **16/21 (76.2%)** | **14/21 (66.7%)** |

| Truth group | Detector correct | X-CLIP correct |
|---|---:|---:|
| cyclist (includes1motorcycle) | 5/8 | 6/8 |
| pedestrian | 11/13 | 8/13 |

## Where they disagree

- both_right: 11 — night/n1, night/n2, day/d1, day/d4, day/d5, night_holdout_2200/p1, night_holdout_2200/p2, night_holdout_2200/p3, night_holdout_2200/p4, day_holdout_1245/h3, day_holdout_1245/h4
- both_wrong: 2 — night/n5, night/n6
- detector_only_right: 5 — night/n4, day/d2, day/d3, day_holdout_1245/h1, day_holdout_1245/h5
- xclip_only_right: 3 — night/n3, night_holdout_2200/p5, day_holdout_1245/h2

Interpretation: a small paired classification comparison on development clips. A two-person lead is not proof one model is universally superior. Keep both signals until identity checks and broader validation justify changing the system.
