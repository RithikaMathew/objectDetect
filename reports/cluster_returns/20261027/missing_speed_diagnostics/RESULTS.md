# Why three locations have no usable speed — October 27, 2026

Source: completed shortday batch ADAPTIVE_SPEED_shortday_20261026_095645, saved diagnostic output supplied in sofar.md. No new inference or threshold change.

**All 12 candidates fail the speed continuity requirement:** none has 1.5 seconds of observed positions with gaps no longer than 0.5 seconds. All12also failed counting;11of12fail the duration gate. Numerical camera calibration is not the demonstrated bottleneck for these tracks: the observation spans are already insufficient even before spatial support checks. This does not establish that every candidate is a real cyclist.

| Location | Candidates | Below count-duration minimum | Longest continuous observed span | Finding |
|---|---:|---:|---:|
| Baxter | 5 | 4 | 1.30 s | Owner saw cars and no bicycles at the two brief moving candidate times; other candidates remain unreviewed. |
| Daniels | 5 | 5 | 0.93 s | No detector cyclist votes on any candidate and only 0.3–2.1 pixels net motion; likely unreliable classifications, requiring visual confirmation. |
| Winter Park | 2 | 2 | 0.73 s | Owner identified the brief moving candidate as a scooter, not a bicycle; the nearly stationary candidate remains unreviewed. |

## Completed owner review

- **Baxter,2019-09-18 12:25:34**,track8:0.43seconds of observed detection-frame duration,100%detector cyclist votes,0.534second maximum continuous observed span.
- **Baxter,2019-09-18 12:52:16**,track4:0.37seconds,100%detector cyclist votes,0.334second continuous observed span.
- **Winter Park,2019-09-25 12:10:32–12:10:33**,track1:0.77seconds,91.3%detector cyclist votes,0.734second continuous observed span.

Owner reviewed both Baxter moments and saw cars rather than bicycles. The Winter Park moving candidate was a scooter. These three reviewed candidates are not approved bicycles; strong bicycle scores were misleading. They were already excluded from counts/speed, so no reported mean changes. This does not prove the remaining candidates or full hours contain no bicycles. [Recorded review](owner_candidate_review.csv).

## Why one Baxter track passes duration but is still unusable

Baxtertrack4 at12:24:17–12:24:21 has1.8seconds worth of observed detection frames and passes the duration audit. Those frames are interrupted: its longest qualifying continuous span is1.1011seconds, with a1.001second gap. It moves only0.4pixels net. Its failed count gate beyond duration is not identified by the partial audit; static/motion rejection is plausible but not proven. The speed continuity failure is definite.

## How seconds are measured

The count duration is observed track-frame count divided by fps, not simply last-seen minus first-seen time. The speed estimator instead uses the timestamps of observed positions, excludes coasted predictions and splits on gaps over0.5seconds. Thus a track can persist on screen for several seconds but still lack a continuous1.5second measurement. The daytime counting threshold remains1.5seconds, pedestrians3seconds and nighttime policy unchanged.

Do not lower all daytime thresholds again: Columbia already shows pedestrian-to-bicycle errors. The three brief moving candidates have now been reviewed and were not bicycles; do not admit them by lowering duration thresholds. There is no need for another identical full-hour run.
