# Fusion probe

runs: b4_combo_static5

| run | clip | truth | when | track | secs | X-CLIP | wBIC | det %cyc | speed h/s | net px | direction | counted |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| b4_combo_static5 | night | n1 cyclist | 4:02 | #4 | 1.2 | bicyclist | 0.97 | 94 | 4.82 | 560 | moving_right | 1 |
| b4_combo_static5 | night | n2 cyclist | 7:02 | #12 | 5.24 | bicyclist | 0.91 | 88 | 0.87 | 706 | moving_right | 1 |
| b4_combo_static5 | night | n3 cyclist | 14:21 | #18 | 3.47 | bicyclist | 0.62 | 49 | 1.23 | 499 | moving_right | 1 |
| b4_combo_static5 | night | n4 cyclist | 14:21 | #22 | 3.44 | pedestrian | 0.30 | 59 | 2.23 | 458 | moving_right | 1 |
| b4_combo_static5 | night | n5 cyclist | 14:21 | #21 | 2.37 | pedestrian | 0.39 | 31 | 2.37 | 437 | moving_right | 0 |
| b4_combo_static5 | night | n6 pedestrian | 14:47 | #23 | 10.58 | bicyclist | 0.67 | 69 | 0.48 | 526 | moving_right | 1 |
| b4_combo_static5 | day | d2 pedestrian | 3:00 | #2 | 20.69 | bicyclist | 0.73 | 6 | 0.56 | 593 | moving_left | 1 |
| b4_combo_static5 | day | d1 cyclist | 9:10 | #10 | 6.74 | bicyclist | 0.91 | 54 | 1.51 | 749 | moving_left | 1 |
| b4_combo_static5 | day | d3 pedestrian | 11:45 | #13 | 36.57 | bicyclist | 0.53 | 2 | 0.39 | 499 | moving_left | 1 |
| b4_combo_static5 | day | d4 pedestrian | 12:10 | #15 | 21.96 | pedestrian | 0.24 | 6 | 0.78 | 628 | moving_left | 1 |
| b4_combo_static5 | day | d5 pedestrian | 12:10 | #23 | 3.47 | pedestrian | 0.22 | 0 | 0.16 | 17 | static | 1 |
| b4_combo_static5 | night_holdout_2200 | p1 pedestrian | 6:00 | #18 | 10.48 | pedestrian | 0.29 | 24 | 0.65 | 518 | moving_right | 1 |
| b4_combo_static5 | night_holdout_2200 | p2 pedestrian | 10:00 | #27 | 18.72 | pedestrian | 0.23 | 32 | 0.15 | 516 | moving_right | 1 |
| b4_combo_static5 | night_holdout_2200 | p3 pedestrian | 10:59 | #33 | 14.98 | pedestrian | 0.35 | 43 | 0.30 | 526 | moving_right | 1 |
| b4_combo_static5 | night_holdout_2200 | p4 pedestrian | 10:59 | #36 | 5.84 | pedestrian | 0.05 | 28 | 0.51 | 416 | toward_camera | 1 |
| b4_combo_static5 | night_holdout_2200 | p5 pedestrian | 10:59 | #40 | 3.84 | pedestrian | 0.15 | 76 | 0.96 | 344 | moving_right | 1 |
| b4_combo_static5 | day_holdout_1245 | h1 pedestrian | 0:40 | #1 | 15.48 | bicyclist | 0.57 | 26 | 0.74 | 678 | moving_left | 1 |
| b4_combo_static5 | day_holdout_1245 | h2 cyclist | 8:07 | #7 | 8.17 | bicyclist | 0.85 | 44 | 1.59 | 730 | moving_right | 1 |
| b4_combo_static5 | day_holdout_1245 | h3 cyclist | 8:46 | #9 | 9.68 | bicyclist | 0.82 | 57 | 1.51 | 733 | moving_right | 1 |
| b4_combo_static5 | day_holdout_1245 | h4 pedestrian | 9:54 | #14 | 7.21 | pedestrian | 0.17 | 0 | 0.18 | 30 | static | 1 |
| b4_combo_static5 | day_holdout_1245 | h5 pedestrian | 11:17 | #15 | 23.62 | bicyclist | 0.64 | 8 | 0.56 | 460 | away_from_camera | 1 |

## Detector / X-CLIP error patterns

Classification of matched, scored tracks only; duration/counting failures and misses are separate.
Each row below is one run. Repeated people across runs are not independent examples.

| run | both right | both wrong | detector right / X-CLIP wrong | detector wrong / X-CLIP right |
|---|---|---|---|---|
| b4_combo_static5 | 11: night/n1 (moving_right, 1.2s), night/n2 (moving_right, 5.24s), day/d1 (moving_left, 6.74s), day/d4 (moving_left, 21.96s), day/d5 (static, 3.47s), night_holdout_2200/p1 (moving_right, 10.48s), night_holdout_2200/p2 (moving_right, 18.72s), night_holdout_2200/p3 (moving_right, 14.98s), night_holdout_2200/p4 (toward_camera, 5.84s), day_holdout_1245/h3 (moving_right, 9.68s), day_holdout_1245/h4 (static, 7.21s) | 2: night/n5 (moving_right, 2.37s), night/n6 (moving_right, 10.58s) | 5: night/n4 (moving_right, 3.44s), day/d2 (moving_left, 20.69s), day/d3 (moving_left, 36.57s), day_holdout_1245/h1 (moving_left, 15.48s), day_holdout_1245/h5 (away_from_camera, 23.62s) | 3: night/n3 (moving_right, 3.47s), night_holdout_2200/p5 (moving_right, 3.84s), day_holdout_1245/h2 (moving_right, 8.17s) |

Use these named cases to inspect the source video. Direction is measured image motion; it cannot prove a missed person was walking away, since missed people have no track. Missing detector shares are excluded. This comparison does not measure detector recall.

## Rules replayed on 21 (person, run) pairs

| rule | right | of | labels it changes |
|---|---|---|---|
| X-CLIP alone (now) | 14 | 21 | |
| veto 5% | 15 | 21 | b4_combo_static5/day/d3(ok) |
| veto 10% | 17 | 21 | b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h5(ok) |
| veto 15% | 17 | 21 | b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h5(ok) |
| veto 20% | 17 | 21 | b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h5(ok) |
| veto 30% | 18 | 21 | b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h1(ok), b4_combo_static5/day_holdout_1245/h5(ok) |
| veto 40% | 18 | 21 | b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h1(ok), b4_combo_static5/day_holdout_1245/h5(ok) |
| veto 50% | 16 | 21 | b4_combo_static5/night/n3(WRONG), b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h1(ok), b4_combo_static5/day_holdout_1245/h2(WRONG), b4_combo_static5/day_holdout_1245/h5(ok) |
| promote 80% | 14 | 21 | - |
| promote 90% | 14 | 21 | - |
| promote 95% | 14 | 21 | - |
| speed lateral walk<0.8 ride>2.0 | 18 | 21 | b4_combo_static5/night/n4(ok), b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h1(ok) |
| speed lateral walk<1.0 ride>2.0 | 18 | 21 | b4_combo_static5/night/n4(ok), b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h1(ok) |
| speed lateral walk<1.2 ride>2.5 | 17 | 21 | b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h1(ok) |
| speed lateral walk<1.5 ride>3.0 | 16 | 21 | b4_combo_static5/night/n3(WRONG), b4_combo_static5/day/d2(ok), b4_combo_static5/day/d3(ok), b4_combo_static5/day_holdout_1245/h1(ok) |

Read the per-row table first: do real riders and real walkers separate on speed (lateral tracks) or on det %cyc? A rule that only 'wins' by changing one or two rows is a coincidence.