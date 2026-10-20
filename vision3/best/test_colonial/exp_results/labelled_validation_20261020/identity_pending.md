# Experiment evaluation  (2026-10-20 00:13)

root: /Users/rithika/Desktop/objectDetect/vision3/best/test_colonial
runs: b4_combo_static5

Identity policy: HUMAN APPROVAL REQUIRED. UNVERIFIED rows excluded from correct/reviewed denominators; unmatched counted tracks are unverified, not proven false positives.

- truth night: 6 usable rows (5 cyclist incl. motorcycle, 1 pedestrian); skipped 0: none
- truth day: 5 usable rows (1 cyclist incl. motorcycle, 4 pedestrian); skipped 0: none
- truth night_holdout_2200: 5 usable rows (0 cyclist incl. motorcycle, 5 pedestrian); skipped 0: none
- truth day_holdout_1245: 5 usable rows (2 cyclist incl. motorcycle, 3 pedestrian); skipped 0: none

## Summary (verified correct / identity-reviewed; no accuracy claim for unreviewed rows; motorcycle scored as cyclist)

| run | clip | cyclists found | pedestrians found | wrong class | detected, not counted | missed | unmatched counted (unverified) | counted bic/ped | runtime min |
|---|---|---|---|---|---|---|---|---|---|
| b4_combo_static5 | night | 0/0 | 0/0 | 0 | 0 | 0 | 5 | 5/0 | 42.9 |
| b4_combo_static5 | day | 0/0 | 0/0 | 0 | 0 | 0 | 5 | 1/4 | 42.0 |
| b4_combo_static5 | night_holdout_2200 | 0/0 | 0/0 | 0 | 0 | 0 | 5 | 0/5 | 41.8 |
| b4_combo_static5 | day_holdout_1245 | 0/0 | 0/0 | 0 | 0 | 0 | 5 | 2/3 | 41.3 |

## Detail

### b4_combo_static5 - night clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| n1 | motorcycle | 4:02-4:04 | UNVERIFIED | #4 cyclist 1.2s counted=1 det=cyclist (94.4% cyc) |
| n2 | cyclist | 7:02-7:09 | UNVERIFIED | #12 cyclist 5.24s counted=1 det=cyclist (87.9% cyc) |
| n3 | cyclist | 14:21-14:26 | UNVERIFIED | #18 cyclist 3.47s counted=1 det=person (49.0% cyc) |
| n4 | cyclist | 14:21-14:26 | UNVERIFIED | #22 cyclist 3.44s counted=1 det=cyclist (59.2% cyc) |
| n5 | cyclist | 14:21-14:26 | UNVERIFIED | #21 pedestrian 2.37s counted=0 det=person (31.0% cyc) |
| n6 | pedestrian | 14:47-14:58 | UNVERIFIED | #23 cyclist 10.58s counted=1 det=cyclist (68.8% cyc) |
| UNREVIEWED TRACK | counted cyclist | 4:02-4:05 | no truth row | #4 1.2s det=cyclist |
| UNREVIEWED TRACK | counted cyclist | 6:58-7:10 | no truth row | #12 5.24s det=cyclist |
| UNREVIEWED TRACK | counted cyclist | 14:17-14:24 | no truth row | #18 3.47s det=person |
| UNREVIEWED TRACK | counted cyclist | 14:26-14:31 | no truth row | #22 3.44s det=cyclist |
| UNREVIEWED TRACK | counted cyclist | 14:44-14:59 | no truth row | #23 10.58s det=cyclist |

### b4_combo_static5 - day clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| d2 | pedestrian | 3:00-3:25 | UNVERIFIED | #2 pedestrian 20.69s counted=1 det=person (6.1% cyc) |
| d1 | cyclist | 9:10-9:19 | UNVERIFIED | #10 cyclist 6.74s counted=1 det=cyclist (54.0% cyc) |
| d3 | pedestrian | 11:45-12:14 | UNVERIFIED | #13 pedestrian 36.57s counted=1 det=person (2.1% cyc) |
| d4 | pedestrian | 12:10-12:37 | UNVERIFIED | #15 pedestrian 21.96s counted=1 det=person (5.5% cyc) |
| d5 | pedestrian | 12:10-12:37 | UNVERIFIED | #23 pedestrian 3.47s counted=1 det=person (0.0% cyc) |
| UNREVIEWED TRACK | counted pedestrian | 2:59-3:23 | no truth row | #2 20.69s det=person |
| UNREVIEWED TRACK | counted cyclist | 9:09-9:19 | no truth row | #10 6.74s det=cyclist |
| UNREVIEWED TRACK | counted pedestrian | 11:37-12:22 | no truth row | #13 36.57s det=person |
| UNREVIEWED TRACK | counted pedestrian | 12:08-12:35 | no truth row | #15 21.96s det=person |
| UNREVIEWED TRACK | counted pedestrian | 12:30-12:37 | no truth row | #23 3.47s det=person |

### b4_combo_static5 - night_holdout_2200 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| p1 | pedestrian | 6:00-6:13 | UNVERIFIED | #18 pedestrian 10.48s counted=1 det=person (24.5% cyc) |
| p2 | pedestrian | 10:00-10:14 | UNVERIFIED | #27 pedestrian 18.72s counted=1 det=person (31.6% cyc) |
| p3 | pedestrian | 10:59-11:18 | UNVERIFIED | #33 pedestrian 14.98s counted=1 det=person (43.4% cyc) |
| p4 | pedestrian | 10:59-11:18 | UNVERIFIED | #36 pedestrian 5.84s counted=1 det=person (28.0% cyc) |
| p5 | pedestrian | 10:59-11:18 | UNVERIFIED | #40 pedestrian 3.84s counted=1 det=cyclist (76.5% cyc) |
| UNREVIEWED TRACK | counted pedestrian | 6:00-6:13 | no truth row | #18 10.48s det=person |
| UNREVIEWED TRACK | counted pedestrian | 9:05-10:15 | no truth row | #27 18.72s det=person |
| UNREVIEWED TRACK | counted pedestrian | 10:42-11:18 | no truth row | #33 14.98s det=person |
| UNREVIEWED TRACK | counted pedestrian | 11:05-11:16 | no truth row | #36 5.84s det=person |
| UNREVIEWED TRACK | counted pedestrian | 11:12-11:18 | no truth row | #40 3.84s det=cyclist |

### b4_combo_static5 - day_holdout_1245 clip

| truth id | class | time | status | matched track |
|---|---|---|---|---|
| h1 | pedestrian | 0:40-0:56 | UNVERIFIED | #1 pedestrian 15.48s counted=1 det=person (25.6% cyc) |
| h2 | cyclist | 8:07-8:13 | UNVERIFIED | #7 cyclist 8.17s counted=1 det=person (44.5% cyc) |
| h3 | cyclist | 8:46-8:53 | UNVERIFIED | #9 cyclist 9.68s counted=1 det=cyclist (57.2% cyc) |
| h4 | pedestrian | 9:54-10:04 | UNVERIFIED | #14 pedestrian 7.21s counted=1 det=person (0.0% cyc) |
| h5 | pedestrian | 11:17-11:38 | UNVERIFIED | #15 pedestrian 23.62s counted=1 det=person (8.1% cyc) |
| UNREVIEWED TRACK | counted pedestrian | 0:40-0:59 | no truth row | #1 15.48s det=person |
| UNREVIEWED TRACK | counted cyclist | 8:07-8:16 | no truth row | #7 8.17s det=person |
| UNREVIEWED TRACK | counted cyclist | 8:44-8:55 | no truth row | #9 9.68s det=cyclist |
| UNREVIEWED TRACK | counted pedestrian | 9:53-10:05 | no truth row | #14 7.21s det=person |
| UNREVIEWED TRACK | counted pedestrian | 11:14-11:40 | no truth row | #15 23.62s det=person |

## Motion-diagnostic candidates (baseline run) overlapping truth rows

**night**: 447 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth n1 (motorcycle 4:02): cand 138 (2.97s, box h 22.5), cand 139 (3.0s, box h 16.9), cand 140 (1.43s, box h 21.2)
- truth n2 (cyclist 7:02): cand 203 (4.54s, box h 22.8), cand 205 (3.0s, box h 41.4), cand 207 (3.5s, box h 26.3), cand 209 (1.1s, box h 20.8), cand 210 (1.2s, box h 41.2), cand 211 (0.9s, box h 36.7), cand 212 (2.67s, box h 52.2), cand 213 (1.7s, box h 31.8), cand 214 (1.3s, box h 50.0), cand 215 (1.5s, box h 16.6), cand 216 (1.43s, box h 23.7), cand 217 (1.4s, box h 90.6), cand 218 (1.94s, box h 86.1), cand 219 (4.9s, box h 49.8), cand 220 (1.74s, box h 94.6)
- truth n3 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n4 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n5 (cyclist 14:21): cand 425 (2.7s, box h 27.9), cand 426 (6.34s, box h 19.7), cand 427 (3.6s, box h 16.9), cand 428 (6.54s, box h 21.7), cand 429 (2.2s, box h 26.9), cand 430 (0.9s, box h 32.5), cand 431 (1.2s, box h 97.1), cand 432 (7.07s, box h 33.1), cand 433 (3.1s, box h 66.4), cand 434 (0.83s, box h 31.4), cand 435 (1.17s, box h 57.6), cand 436 (3.87s, box h 90.8), cand 437 (1.33s, box h 33.5)
- truth n6 (pedestrian 14:47): cand 445 (1.3s, box h 15.0), cand 446 (7.61s, box h 31.4), cand 447 (10.78s, box h 91.9)

**day**: 185 unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).
- truth d2 (pedestrian 3:00): cand 30 (2.57s, box h 19.2), cand 33 (12.18s, box h 71.5), cand 34 (0.87s, box h 84.7), cand 35 (1.13s, box h 19.8), cand 36 (1.13s, box h 40.9), cand 37 (1.07s, box h 34.5), cand 38 (1.97s, box h 61.7), cand 39 (1.17s, box h 43.4)
- truth d1 (cyclist 9:10): cand 108 (1.47s, box h 45.3), cand 109 (1.47s, box h 104.7), cand 110 (1.6s, box h 36.9), cand 111 (1.13s, box h 92.3), cand 112 (3.07s, box h 34.6)
- truth d3 (pedestrian 11:45): cand 142 (8.94s, box h 100.1), cand 144 (0.87s, box h 24.9), cand 145 (3.74s, box h 64.9), cand 146 (1.87s, box h 35.8), cand 147 (3.74s, box h 30.7), cand 148 (1.27s, box h 46.4), cand 149 (1.9s, box h 34.1), cand 150 (1.17s, box h 26.5), cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1)
- truth d4 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)
- truth d5 (pedestrian 12:10): cand 151 (1.1s, box h 29.2), cand 152 (4.6s, box h 121.1), cand 153 (8.31s, box h 69.5), cand 154 (1.7s, box h 97.0), cand 155 (1.1s, box h 15.3), cand 156 (3.44s, box h 59.7), cand 157 (2.07s, box h 20.1), cand 158 (6.17s, box h 39.0), cand 159 (1.94s, box h 19.8), cand 160 (1.4s, box h 16.5), cand 161 (1.47s, box h 14.7), cand 162 (1.7s, box h 20.7), cand 163 (0.77s, box h 22.4), cand 164 (5.41s, box h 21.8), cand 165 (0.87s, box h 29.8), cand 166 (1.0s, box h 19.5), cand 169 (1.53s, box h 36.7)
