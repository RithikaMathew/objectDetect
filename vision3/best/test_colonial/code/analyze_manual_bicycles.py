#!/usr/bin/env python3
"""Audit manual clicks, split owner-confirmed reused IDs, compare separate study references."""
import argparse
from collections import defaultdict
import csv
import datetime as dt
import json
import math
from pathlib import Path
import statistics


def write_csv(path,rows):
    if not rows:return
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)


def split_encounters(points,gap=30):
    groups=[]
    for p in sorted(points,key=lambda r:r['seconds']):
        if not groups or p['seconds']-groups[-1][-1]['seconds']>gap:groups.append([])
        groups[-1].append(p)
    return groups


def project(H,p):
    x,y=float(p['x']),float(p['y']);z=H[2][0]*x+H[2][1]*y+H[2][2]
    if abs(z)<1e-8:raise ValueError('Near calibration horizon')
    result=((H[0][0]*x+H[0][1]*y+H[0][2])/z,(H[1][0]*x+H[1][1]*y+H[1][2])/z,z)
    if not all(math.isfinite(v) for v in result):raise ValueError('Nonfinite projection')
    return result


def speed(points,calibration):
    span=points[-1]['seconds']-points[0]['seconds']
    if len(points)<3 or span<1.5:return '', 'INSUFFICIENT_POINTS_OR_SPAN'
    if not calibration:return '', 'CALIBRATION_NOT_IN_REVIEW_PACK'
    if not calibration.get('geometry_check_passed'):return '', 'CALIBRATION_GEOMETRY_NOT_ACCEPTED'
    if any(b['seconds']<=a['seconds'] for a,b in zip(points,points[1:])):return '', 'DUPLICATE_TIME_REVIEW_REQUIRED'
    try:
        xy=[project(calibration['H'],p) for p in points]
        if min(p[2] for p in xy)<0<max(p[2] for p in xy):raise ValueError('Crosses horizon')
        distance=sum(math.hypot(b[0]-a[0],b[1]-a[1]) for a,b in zip(xy,xy[1:]))
        return distance/span*2.2369362921,'EXPLORATORY_UNVALIDATED_ROAD_PLANE'
    except (ValueError,KeyError,TypeError,IndexError):return '', 'INVALID_PROJECTION'


def clock(entry,seconds):
    return (dt.datetime.fromisoformat(entry['reference']['start'])+dt.timedelta(seconds=seconds)).isoformat(sep=' ',timespec='milliseconds')


def write_current_readme(input_dir, out, recordings, completed_dir):
    """Make the completed same-video comparison the main report, retaining baseline exports."""
    with (completed_dir/'combined_comparison.csv').open() as f:rows=list(csv.DictReader(f))
    hours={r['location']:r['available_hours'] for r in recordings}
    write_csv(out/'same_video_comparison.csv',rows)
    def speed(value,n=None):
        return f'{float(value):.2f}' + (f' ({n})' if n is not None else '')
    totals=[sum(int(r[k]) for r in rows) for k in ('study_count_selected','automatic_count','manual_count')]
    lines=['# Bicycle counts and speed comparison','',
           '**Updated October 27, 2026 — completed HiPerGator run on the same 18 manually annotated clips, across nine cameras.** The daytime bicycle minimum was 1.5 seconds. All selected clips were processed without stopping at a cyclist quota. Pedestrian and nighttime policies were retained.','',
           f'**Counts in these clips: study {totals[0]}, HiPerGator {totals[1]}, manual {totals[2]}.** There are 29 usable manual speeds from 30 annotated cyclists. Similar count totals do not establish accuracy: missed cyclists and extra tracks can cancel out.','',
           '**Study/validation count** is the bicycle count in these selected video intervals. **Study/validation mph** comes from a separate location-level speed sample; it is not the known speed of these same cyclists. HiPerGator is automatic detection/tracking; Manual is your rear-tire clicks. Numbers in parentheses after mph are speed sample sizes.','',
           '| Location | Available hours | Same clips: bins / nominal min | Study count | HiPerGator count | Manual count | Study mph (n) | HiPerGator mph (n) | Manual mph (n) | Robust manual mph |',
           '|---|---:|---|---:|---:|---:|---|---|---|---:|']
    for r in rows:
        lines.append(f"| {r['location']} | {hours[r['location']]} | {r['clips']} / {int(r['clips'])*15} | {r['study_count_selected']} | {r['automatic_count']} | {r['manual_count']} | {speed(r['study_mean_mph'],r['study_speed_sample'])} | {speed(r['automatic_mean_mph'],r['automatic_speed_sample'])} | {speed(r['manual_mean_mph'],r['manual_speed_sample'])} | {speed(r['robust_manual_mean_mph'])} |")
    lines += ['',
        '**Coverage:** both methods use the same selected video files (270 nominal minutes; about 269.90 processed minutes). Some files end slightly before the complete study bin. The study counts shown here cover only these 18 bins, not all 27 intervals originally offered for review. West Orange has no submitted annotations and is excluded from this same-video comparison; Baxter, Daniels and Winter Park belong to the separate broader run.','',
        '**Same clips does not mean matched people or identical measurement seconds.** Automatic tracks still need identity/type review; they can include duplicate IDs, static objects or motorcycles. Each cyclist estimate uses only its own recorded measurement seconds, not all 15 minutes. One Edgewater annotation spans 1.4 seconds and has no manual speed. No missing speed is treated as zero.','',
        '## What the results mean','',
        '- **Carroll is encouraging:** the two new automatic speed intervals overlap both annotated cyclists previously reported missed; automatic mean 12.22 mph versus manual 12.37 mph. Full-track identity still needs checking.',
        '- **Columbia has confirmed visual failures:** your review found pedestrians labelled as bicyclists and a missed bicyclist, while at least one actual bicyclist was detected. Its 7 automatic counts versus 4 study/manual are not reliable cyclist counts. Specific track IDs are needed before excluding samples from its raw mean.',
        '- **Aloma has an extra candidate:** 5 automatic versus 4 study/manual. Inspect the automatic candidate at 12:59:47 before calling it a genuine cyclist or false positive.',
        '- **Edgewater received favorable visual review:** you reported bicycle counting looked quite accurate. Earlier temporal-overlap clues do not prove duplicates or counting errors; full-track identity and physical speed remain unverified.',
        '- **Physical scale remains uncertain:** Aloma and University speed means differ substantially from the separate study averages. The robust estimator does not remove that gap. The comparison cannot tell how much comes from calibration versus different cyclists.','',
        '[Exact per-clip counts, automatic speed timestamps and review priorities](../reports/cluster_returns/20261027/completed_speed_batches/RESULTS.md) · [Combined table CSV](analysis/same_video_comparison.csv). Recording clocks are filename-inferred, not independently verified.','',
        '## How speed was calculated','',
        'You paused the video and repeatedly clicked where the same cyclist’s rear tire touched the pavement. Each point has an image position and video time. IDs are scoped to each clip; clearly separated encounters sharing an ID were split. The camera calibration, estimated from car observations, converts those clicks to estimated ground positions in metres.','',
        '**Manual mph:** add the distances between successive ground positions, divide by the time from the first to last click, and multiply by 2.23694. At least three points spanning 1.5 seconds are required. Example: 10 metres in 2 seconds = 11.18 mph. Click jitter can inflate the summed distance.','',
        '**HiPerGator mph:** use automatically tracked positions and take the median of speeds fitted over short continuous time windows. **Robust manual mph:** fit a smooth trajectory using the actual click times, reduce the influence of outliers, then fit distance against time. All site means give equal weight to available per-cyclist speed estimates; they are not averages of 15-minute-bin means. The different estimators and contact points can produce different speeds even with the same calibration.','',
        'All three depend on learned metric scale; manual annotation does not independently verify mph. Perspective, lens distortion and road-to-sidewalk height differences can affect the results. The method builds on [Revaud and Humenberger, ICCV 2021](https://openaccess.thecvf.com/content/ICCV2021/html/Revaud_Robust_Automatic_Monocular_Vehicle_Speed_Estimation_for_Traffic_Surveillance_ICCV_2021_paper.html) and their [calibration code](https://github.com/naver/cctv). Manual clicks and robust fitting are project-specific adaptations, not a complete reproduction or established cyclist-speed validation.','',
        '**Timing and sensitivity:** all 18 re-encoded review clips had regular presentation timestamps near 29.97 fps. The original hourly recordings were not audited for timing, so this does not prove there was no earlier timing error. Sensitivity ranges assume 3-pixel click noise and a uniform ±15% camera-scale scenario; those are illustrative assumptions, not measured accuracy bounds. [Per-cyclist plots, endpoint comparison and sensitivity results](speed_plan_20261027/trajectory/RESULTS.md).','',
        '**Study speed method:** Mighk Wilson stopwatch-timed cyclists while watching half-speed video and accounted for playback speed in the workbook. We use the supplied mph without doubling it again. Some corridors had separate speed-analysis visits. No study speed records have been linked to individual people/timestamps in these selected clips.','',
        '## Why Aloma has 4 selected cyclists but 26 speed records','',
        'Aloma Path has **47.99 measured playback hours**. This pilot selected the first available day’s source hour nearest noon, then its study-positive bins: October 30, 2019, 12:00–12:15, 12:30–12:45 and 12:45–13:00. These total 45 minutes and 4 study bicycles. The omitted 12:15 bin recorded zero.','',
        '| Dataset | Bicycle count |','|---|---:|',
        '| Aloma Path, full October 30–31 count period (192 fifteen-minute bins) | 191 |',
        '| Aloma Sidewalk, separate camera/count table | 19 |',
        '| Aloma Path, selected 45 minutes | 4 |',
        '| Separate Aloma speed-reference sample | 26 |','',
        'The 26 speed observations are not the number of bicycles in the full recording. Their session and individual timestamps are unknown; we cannot confirm they came from the same available recording. They are a location reference, not ground-truth speeds for the four annotated cyclists. Counts come from the Bicycles worksheets in Aloma_Path_716686_10-30-2019.xls and Aloma_Sidewalk_716692_10-30-2019.xls; speeds come from the consolidated speed workbook.','',
        '## Measured recording hours','',
        'All 1,919 inventoried files across 41 cameras were measured. Hours sum playback lengths; file counts are not hours, and summed lengths do not establish gap-free coverage. The table lists the chosen camera per speed-reference location; different camera sides are not pooled.','',
        '| Location | Camera | Source files | Measured playback hours |','|---|---|---:|---:|']
    for r in recordings:lines.append(f"| {r['location']} | {r['camera']} | {r['source_files'] or '—'} | {r['available_hours']} |")
    lines += ['',
        'Columbia’s 49 multipart files total **47.98 hours**, not 49 hours. Silver Star has no mapped source. [Full camera duration audit](../docs/VIDEO_DURATION_README.md).','',
        '## Remaining checks and earlier experiments','',
        'Review the flagged automatic tracks, then confirm University’s approximately 55.17-foot map endpoints in the video to check the learned distance scale. No new broad model sweep or repeat manual annotation is needed now. Wheel/marking checks have code but lack the necessary evidence for physical-scale results. ByteTrack is already used; a new wheel-keypoint model has not been trained.','',
        '[Broader 1.5-second run](../reports/cluster_returns/20261027/completed_speed_batches/shortday_sites.csv) uses different coverage and quota stopping; it is separate from the main table. [Earlier three-second baseline README](analysis/README_baseline_before_same_video_20261027.md) and [baseline data](analysis/site_summary.csv) are preserved. [Manual-seeded optical flow](optical_flow_20261026/RESULTS.md) passed held-out drift checks on only 2 of 30 encounters and does not replace manual tracking. [Full analysis/run guide](../docs/SPEED_PLAN_RUN.md).','',
        'Original annotation JSONs remain unchanged. [Manual measurement timestamps](analysis/DETAILS.md) · [Automatic measurement timestamps](../reports/cluster_returns/20261027/completed_speed_batches/same_video_speed_times.csv) · [Study provenance](analysis/source_provenance.md).','']
    broader_path=completed_dir/'shortday_sites.csv'
    if broader_path.exists():
        with broader_path.open() as f:broader=list(csv.DictReader(f))
        additional=['## Other locations: completed broader HiPerGator run', '',
            'These locations were processed in the separate broader run but have no submitted manual annotation clips for the same-video comparison. They are not missing jobs. Counts of candidate tracks are not verified cyclist counts. The speed mean can use fewer tracks than were speed-usable because this run stopped selection at its quota.', '',
            '| Location | Processed minutes | Candidate tracks found | Speed-usable / used for mean | Study mph (n) | HiPerGator mph (n) | Manual comparison |',
            '|---|---:|---:|---|---|---|---|']
        for r in broader:
            if r['Location'] not in ('West Orange/Park','Baxter','Daniels','Winter Park'):continue
            auto=speed(r['Model mean mph'],r['Used for mean']) if r['Model mean mph'] else 'No usable speed'
            additional.append(f"| {r['Location']} | {r['Minutes']} | {r['Found tracks']} | {r['Speed-usable']} / {r['Used for mean']} | {speed(r['Study mean mph'],r['Study n'])} | {auto} | No submitted annotations |")
        additional += ['', '**West Orange/Park** is the workbook label mapped to **West Orange Path**, not a confirmed separate Orange Park location. Its 26.12 mph mean uses five selected candidates; one is 43.489 mph and needs identity/type/geometry review. Baxter, Daniels and Winter Park completed processing but produced no speed-usable candidates; the precise rejection causes need their saved candidate diagnostics. Silver Star has no mapped source and was not processed.', '',
            '[Your Columbia/Edgewater video review](../reports/cluster_returns/20261027/completed_speed_batches/owner_video_review.md). Qualitative counting approval does not validate mph. No raw candidate speeds were deleted from the results.', '']
        pos=lines.index('## How speed was calculated')
        lines[pos:pos]=additional
    (input_dir/'README.md').write_text('\n'.join(lines))


def write_reports(input_dir,out,summaries,encounters,intervals,entries,refs,automatic,file_count,split_count):
    """Short professor-facing summary; detailed evidence remains separate."""
    fmt=lambda x:'Unavailable' if x=='' else f'{float(x):.2f}'
    duration_path=Path(__file__).resolve().parents[4]/'reports/cluster_returns/20261024/recording_lengths/by_camera.csv'
    completed=Path(__file__).resolve().parents[4]/'reports/cluster_returns/20261027/video_duration_audit/by_camera.csv'
    if completed.exists():duration_path=completed
    durations=[]
    if duration_path.exists():
        with duration_path.open() as f:durations=list(csv.DictReader(f))
    preferred={e['source']['reference_location']:e['camera'] for e in entries.values()}
    preferred.update({r['location']:r['camera'] for r in automatic.get('automatic_comparison',[]) if r.get('camera')})
    recordings=[]
    for location in sorted(refs):
        choices=[r for r in durations if r['speed_reference_candidate']==location]
        if not choices:
            recordings.append(dict(location=location,camera='No mapped source',source_files='',available_hours='Unknown',basis='No mapped recording'));continue
        r=next((r for r in choices if r['camera']==preferred.get(location)),choices[0])
        exact=r['exact_total_hours'];multipart=r['camera']=='Columbia Ave'
        hours=f'{float(exact):.2f}' if exact else 'Unverified'
        basis='Measured from all source durations' if exact else 'Full duration audit pending'
        recordings.append(dict(location=location,camera=r['camera'],source_files=r['source_files'],available_hours=hours,basis=basis))
    write_csv(out/'recording_durations.csv',recordings)
    by_location={r['location']:r for r in recordings}
    study_total=sum(r['study_cyclists_in_selected_bins'] for r in summaries)
    usable=sum(r['speed_mph']!='' for r in encounters)
    lines=['# Bicycle counts and speed comparison','',f'**{len(encounters)} manually annotated cyclists; {usable} estimated speeds.** The selected study intervals record {study_total} bicycles. Unannotated bicycles are review gaps, not automatically detector misses.','',
           '**Validation count** means the study bicycle count in the selected video intervals. **Validation speed sample** means the separate cyclists measured for speed at that location. They are different samples. HiPerGator is the automatic pipeline; Manual is your clicked positions.','',
           '| Location | Available video hours | Manual selection: bins / minutes | HiPerGator completed minutes | Validation count | HiPerGator count / validation in covered bins | Manual count | Validation mph (speed sample) | HiPerGator mph (sample) | Manual mph (sample) |',
           '|---|---|---|---:|---:|---|---:|---|---|---|']
    for r in summaries:
        coverage=f"{r['automatic_count_available_bins']} / {r['study_count_automatic_available_bins']} ({r['automatic_count_matched_bins']}/{r['positive_or_missing_bins']} bins)" if r['automatic_count_available_bins']!='' else 'Interrupted' if r['automatic_state'] in ('STARTED','NODE_FAIL') else 'Unavailable'
        a=r['automatic_mean_mph'];auto=f"{fmt(a)} ({r['automatic_speed_sample']})" if a!='' else 'Interrupted' if r['automatic_state'] in ('STARTED','NODE_FAIL') else 'All candidate tracks filtered' if str(r['automatic_counted_candidates'])=='0' else 'No qualifying trajectory'
        manual=f"{fmt(r['manual_mean_mph'])} ({r['manual_speed_sample']})" if r['manual_mean_mph']!='' else 'Cyclists not located in review' if not r['manual_annotated_encounters'] else 'Insufficient calibration/span'
        lines.append(f"| {r['location']} | {by_location[r['location']]['available_hours']} | {r['positive_or_missing_bins']} / {r['positive_or_missing_bins']*15} | {float(r['automatic_minutes']):.1f} | {r['study_cyclists_in_selected_bins']} | {coverage} | {r['manual_annotated_encounters']} | {fmt(r['study_speed_mean_mph'])} ({r['study_speed_reference_sample']}) | {auto} | {manual} |")
    lines += ['', '**Completed follow-up:** [latest same-video HiPerGator results](../reports/cluster_returns/20261027/completed_speed_batches/RESULTS.md) cover the18submitted annotation clips (nine cameras), using1.5-second daytime counting and no sample-quota early stopping. The table above retains the older three-second baseline and broader offered-bin coverage; use the linked report for the latest comparison.', '', '**Time coverage differs:** Manual selection is the positive-count intervals offered for review, not continuous annotation or measured riding time. HiPerGator completed minutes includes its finished consecutive windows, including zero-count bins, until its quota or one-hour limit. Aloma manual selection is 45 minutes; its recovery completed about 60 minutes after the original node failure. Most other sites completed about 60 minutes; Columbia stopped after 30 minutes. Speed estimates themselves use only the saved per-cyclist seconds, and may involve different people. This is not a matched-duration or matched-person speed comparison.', '', 'Numbers after mph are the number of cyclists contributing to that average. Count coverage such as **2/4 bins** means only two of the four selected intervals are included in that automatic count comparison. A missing speed is not zero.','',
              '**Why Aloma has 4 cyclists but 26 speed records:** Aloma Path has 48 source files totaling **47.99 measured playback hours**. This pilot selected the first available day’s hour nearest noon; within that hour, only intervals with positive study bicycle counts were sent for manual review. For Aloma these were 12:00–12:15, 12:30–12:45 and 12:45–13:00 on October 30, 2019: 45 minutes containing 4 study bicycles, all 4 annotated. The remaining interval recorded zero bicycles.','',
              '| Dataset | Bicycle count |','|---|---:|','| **Aloma Path, full 48-hour count period** | **191** |','| Aloma Sidewalk, separate camera/count table | **19** |','| Aloma Path, selected 45 minutes | **4** |','| Aloma speed-reference sample | **26** |','',
              'The full count period is **October 30–31, 2019**. The full counts come from the Bicycles worksheets in Aloma_Path_716686_10-30-2019.xls and Aloma_Sidewalk_716692_10-30-2019.xls (192 fifteen-minute bins each, with no missing count cells). The 26 speed observations come from the separate consolidated speed workbook; no individual timestamps link them to the counted encounters.','',
              'The **26** belongs to the broader Aloma location speed-reference dataset, not this 45-minute sample. It is not a count of every cyclist in the available recording collection. Mighk revisited some corridors for speed analysis, and the speed records have no linked video timestamps. **We cannot confirm that all 26 came from that same 48-hour recording.** Their average is a location-level reference, not the known speeds of these same four cyclists.','',
              '**Study speed method:** Mighk Wilson stopwatch-timed cyclists from half-speed video and accounted for playback speed in the workbook. We use the supplied mph values without doubling them again.','',
              '### How your manual annotations produce speed','',
              '1. You paused the original-speed video and clicked where the same cyclist’s rear tire touches the pavement, then advanced the video and clicked that same point again. Each click saves an image position and video time.','2. Those successive points form the cyclist’s **trajectory** (their path through the image). Different cyclists and different 15-minute videos are kept separate; clearly separated encounters sharing an ID were split.','3. The saved camera calibration, estimated using car observations from the same camera, converts each image point into an estimated ground position in metres. Pixel movement alone cannot give mph because perspective changes the distance represented by a pixel.','4. We add the distances between successive ground positions and divide by the time between the first and last click. We require at least three points spanning 1.5 seconds.','',
              '**Formula:** `speed (mph) = total trajectory distance (metres) / elapsed video time (seconds) × 2.23694`. Here `total distance = distance(point1, point2) + distance(point2, point3) + ...`. For example, an estimated 10 metres in 2 seconds gives 11.18 mph. Each site’s manual mean gives equal weight to its available per-cyclist estimates.','',
              'HiPerGator supplies automatically tracked positions; Manual replaces those positions with your clicks. Both still depend on learned camera calibration, so manual annotation fixes tracking gaps but does not prove the distance scale is correct. Click noise, lens distortion and raised sidewalks can affect estimated speed.','',
              '### Research basis and alternatives','',
              'Trajectory-based speed estimation is the standard position-over-time approach, not a new formula invented for this study. Revaud and Humenberger, **Robust Automatic Monocular Vehicle Speed Estimation for Traffic Surveillance**, ICCV 2021, describe detecting/tracking vehicles and converting image displacement into metric movement using camera calibration ([paper](https://openaccess.thecvf.com/content/ICCV2021/html/Revaud_Robust_Automatic_Monocular_Vehicle_Speed_Estimation_for_Traffic_Surveillance_ICCV_2021_paper.html)). Their [author implementation](https://github.com/naver/cctv) supplies the pretrained learned calibration used through our adapter. Our manual rear-tire clicks and path-distance/time calculation are a project-specific adaptation, not the paper’s exact method. Its car-speed benchmarks do not validate bicycle speeds on these cameras.','',
              '| Alternative | What it measures | What is still needed |','|---|---|---|',
              '| Two fixed lines / timed gates | Time for the same cyclist to cross a measured section; speed = known distance / travel time. Full trajectory annotation is unnecessary. | Identifiable, independently measured endpoints. This is a practical independent check of learned scale ([FHWA tripline description](https://www.fhwa.dot.gov/publications/research/operations/its/06108/02a.cfm)). |',
              '| Surveyed ground landmarks | Replace learned camera scale with a mapping from known ground positions, then measure motion. | Reliable ground measurements and matching image points. This changes calibration, not the distance/time principle. |',
              '| Optical flow | Estimate movement of image features between frames instead of repeated detector boxes or manual clicks. | Association with the same cyclist, stable visible features and a metric scale; it does not remove the need for calibration ([OpenCV documentation](https://docs.opencv.org/4.x/d4/dee/tutorial_optical_flow.html)). |',
              '| Radar, lidar or bicycle-mounted speed/GPS reference | Independently measure speed during a recording. | New synchronized measurements for the same cyclists; these cannot be recovered from old CCTV footage alone ([FHWA sensor overview](https://www.fhwa.dot.gov/publications/research/operations/its/06108/02a.cfm)). |','',
              'For existing video, a correctly measured two-line section is the simplest additional independent scale check. More tracking methods cannot, by themselves, establish correct mph when the real-world scale is wrong. The manual-seeded optical-flow and first/last endpoint comparisons are implemented separately below; surveyed ground calibration and independent sensor validation are not established by this list.','',
              '**Additional comparison run (October 26):** [manual-seeded optical flow and first/last-point timing](optical_flow_20261026/RESULTS.md) ran locally on all 30 encounters. Only the first click steered optical flow; later clicks checked drift. Two flow tracks (Pleasant Hill) passed the pixel check and yielded speeds; 27 failed drift/coverage and one was too short for speed. This simple tracker does not replace the manual results. Endpoint timing shares the same learned scale and is not independent validation.','',
              '**How to read the results:** Carroll and Columbia manual averages are close to their study references. Aloma and University differ substantially and need checking. Similar group averages do not establish per-person accuracy. Colonial’s study speed average combines bike-lane and sidewalk cyclists.','',
              '**Shorter-duration experiment prepared:** [rerun instructions](../docs/SHORT_TRACK_SPEED_RUN.md) lower the daytime bicycle minimum to1.5seconds across all13sites, reusing saved calibration. Other counting rules and nighttime policy are preserved. The completed reports are saved in reports/cluster_returns/20261027/completed_speed_batches; the table above remains the older three-second baseline.','',
              '**Aloma duration-filter finding:** all five rejected bicycle-labelled tracks lasted less than the daytime three-second minimum: 2.9, 1.6, 2.0, 2.7 and 1.7 seconds. Four had 100% detector bicycle labels and weighted bicycle scores of 0.98–1.00. The duration gate necessarily rejects these tracks; other gates may also apply. This shows that short tracked duration can exclude strongly supported cyclists. It does not prove all five are distinct real cyclists: the study count and manual review contain four, so the extra candidate needs review before relaxing filters. The baseline results above remain unchanged. [Saved audit](analysis/aloma_duration_audit_20261026.csv).','',
              '**Missing results:** Aloma’s recovery completed about 60 minutes and recorded 5 bicycle-labelled candidate tracks, all rejected by counting filters. Its automatic speed is unavailable, not zero mph. Five candidate tracks are not necessarily five different real cyclists. Carroll and Rinehart had candidates rejected by counting filters. West Orange has no located/annotated manual cyclists. One Edgewater encounter spans only 1.4 seconds, below the current 1.5-second speed safeguard. No reannotation of completed encounters is required.','',
              '### Recording hours for every speed-reference location','',
              '**Source files** counts separate MP4 video files. **Total available hours** is the sum of their playback lengths, not the number of files or time analysed. For example, 48 one-hour files total about 48 hours, but 48 shorter files would total less. **All 41 inventoried camera collections are fully measured in the October 27 audit (1,919 files). Values are summed playback hours, not proof of continuous coverage.** Other camera sides are not added together.','',
              '**Columbia is now measured:** its 49 multipart MP4s total **47.98 playback hours**, not 49 hours. The completed duration audit replaces the earlier unknown value.','',
              '| Location | Camera | Source files | Total available hours | Basis |','|---|---|---:|---|---|']
    for r in recordings:lines.append(f"| {r['location']} | {r['camera']} | {r['source_files']} | {r['available_hours']} | {r['basis']} |")
    lines += ['', 'Detailed encounter times and exclusions: [analysis/DETAILS.md](analysis/DETAILS.md). Tables: [site summaries](analysis/site_summary.csv), [15-minute counts](analysis/interval_counts.csv), [per-cyclist speeds](analysis/encounters.csv). Original annotation JSONs are unchanged.','']
    completed_report=Path(__file__).resolve().parents[4]/'reports/cluster_returns/20261027/completed_speed_batches/RESULTS.md'
    if completed_report.exists():
        lines += ['', '## Latest completed HiPerGator comparison', '', '[Study vs automatic vs manual on the same 18 clips](../reports/cluster_returns/20261027/completed_speed_batches/RESULTS.md): study35, manual30, automatic32. The table earlier in this file retains the older three-second baseline and broader offered-bin coverage. The new report contains the completed 1.5-second same-video results, speed sample sizes and priority identity checks. Count similarity is not accuracy.', '']
    if (input_dir/'speed_plan_20261027/RESULTS.md').exists():
        lines += ['', '## Latest speed plan results', '', '[Combined analysis and scale checks](speed_plan_20261027/RESULTS.md) include robust/manual/endpoint comparison, timestamps, plots, assumption-based sensitivity, study-group comparisons and optional physical-scale evidence checks. [One-pass run guide](../docs/SPEED_PLAN_RUN.md).', '']
    elif (input_dir/'speed_analysis_20261026/RESULTS.md').exists():
        lines += ['', '## New trajectory analysis', '', '[One-pass robust speed results](speed_analysis_20261026/RESULTS.md) compare the old manual, endpoint and robust estimates using the same annotations. Includes per-cyclist timestamps, plots and assumption-based sensitivity ranges. The existing table above remains the earlier baseline. [Reproduction and limitations](../docs/SPEED_ANALYSIS_ONE_PASS.md).', '']
    if (completed_report.parent/'combined_comparison.csv').exists():
        write_current_readme(input_dir,out,recordings,completed_report.parent)
    else:
        (input_dir/'README.md').write_text('\n'.join(lines))
    details=['# Encounter evidence and limitations','',f'{file_count} original JSON files; {split_count} reused-ID groups split on gaps over 30 seconds under the owner’s instruction. IDs in different source intervals always refer to different encounters. Original clicks preserved.','',
             'Speeds are path distance divided by elapsed presentation time, converted to mph. Click noise can inflate path length; learned road calibration may not transfer to raised paths/sidewalks. No extra half-speed adjustment is applied to original-video clicks or published workbook mph. Workbook time columns have varying correction conventions; supplied mph remains the reference. Camera channels and inferred recording clocks require checking.','',
             '| Camera | Interval start | Encounter | Measurement start | Measurement end | mph | Status |','|---|---|---|---|---|---:|---|']
    for r in encounters:details.append(f"| {r['camera']} | {r['bin_start']} | {r['encounter_id'].rsplit('__',1)[-1]} | {r['start']} | {r['end']} | {fmt(r['speed_mph'])} | {r['status']} |")
    details+=['','## Intervals with no submitted annotations','']
    for r in intervals:
        if r['review_status']!='ANNOTATIONS_RECEIVED':details.append(f"- {r['camera']}, {r['bin_start']}: study {r['study_bicycles_all_recorded_channels']}; reviewer could not locate/annotate cyclists. This does not prove absence.")
    details+=['','Original source timing/provenance: [source_provenance.md](source_provenance.md). Corrected IDs: normalized_observations.json and id_splits.csv. Final batch export: final_batch_export.json. Full recording inventory: ../../docs/VIDEO_DURATION_README.md.','']
    (out/'DETAILS.md').write_text('\n'.join(details))


def run(input_dir,manifest,references,out,gap=30,calibrations=None):
    out.mkdir(parents=True,exist_ok=True)
    pack=json.loads(manifest.read_text());entries={e['key']:e for e in pack['entries']}
    snapshot=out/'automatic_report_snapshot.json'
    automatic=json.loads(snapshot.read_text()) if snapshot.exists() else {}
    if calibrations:automatic.update(json.loads(calibrations.read_text()))
    updates=out/'automatic_recovery_updates.json'
    if updates.exists():
        recovered=json.loads(updates.read_text())
        site_rows={r['location']:r for r in automatic.get('automatic_comparison',[])}
        site_rows.update({r['location']:r for r in recovered.get('automatic_comparison',[])})
        automatic['automatic_comparison']=list(site_rows.values())
        covered={(r['camera'],r['bin_start']):r for r in automatic.get('automatic_count_bins',[])}
        covered.update({(r['camera'],r['bin_start']):r for r in recovered.get('automatic_count_bins',[])})
        automatic['automatic_count_bins']=list(covered.values())
    auto_by_site={r['location']:r for r in automatic.get('automatic_comparison',[])}
    auto_bins={(r['camera'],r['bin_start']):r for r in automatic.get('automatic_count_bins',[])}
    if calibrations:
        bundle=json.loads(calibrations.read_text())['calibrations']
        for e in entries.values():
            site=e['key'].rsplit('_',2)[0]
            candidate=bundle.get(site)
            if not candidate:continue
            if candidate['camera']!=e['camera'] or candidate['source_clock']!=e['source']['clock']:raise ValueError('Calibration camera/source mismatch: '+site)
            e['calibration']=candidate['calibration']
    refs=defaultdict(list)
    with references.open() as f:
        for r in csv.DictReader(f):refs[r['street']].append(r)
    groups=defaultdict(list);files=defaultdict(set);seen=set();duplicates=0
    originals=sorted(input_dir.glob('*.json'))
    for path in originals:
        data=json.loads(path.read_text())
        for r in data.get('observations',[]):
            if r['key'] not in entries:raise ValueError('Observation not in manifest: '+r['key'])
            identity=(r['key'],str(r['cyclist_id']))
            token=(*identity,r['seconds'],r['x'],r['y'])
            if token in seen:duplicates+=1;continue
            seen.add(token);groups[identity].append(r);files[identity].add(path.name)
    encounters=[];normalized=[];splitlog=[];perkey=defaultdict(list);counters=defaultdict(int)
    for (key,original_id),points in sorted(groups.items()):
        e=entries[key];pieces=split_encounters(points,gap)
        if len(pieces)>1:splitlog.append(dict(interval=key,original_id=original_id,new_encounters=len(pieces),gaps_seconds=json.dumps([round(b[0]['seconds']-a[-1]['seconds'],3) for a,b in zip(pieces,pieces[1:])]),reason='Owner says distant encounters are separate cyclists; >30-second annotation gap'))
        for piece in pieces:
            counters[key]+=1;unique=key+'__c'+str(counters[key]).zfill(2)
            mph,status=speed(piece,e.get('calibration'))
            row=dict(encounter_id=unique,location=e['source']['reference_location'],camera=e['camera'],bin_start=e['reference']['start'],bin_end=e['reference']['end'],original_id=original_id,original_id_split=len(pieces)>1,points=len(piece),start=clock(e,piece[0]['seconds']),end=clock(e,piece[-1]['seconds']),span_seconds=piece[-1]['seconds']-piece[0]['seconds'],speed_mph=mph,status=status,source_files=';'.join(sorted(files[(key,original_id)])),source_clock='filename_inferred_not_independently_verified')
            encounters.append(row);perkey[key].append(row)
            for r in piece:normalized.append({**r,'encounter_id':unique,'original_cyclist_id':str(r['cyclist_id']),'camera':e['camera'],'recording_time':clock(e,r['seconds'])})
    intervals=[]
    for key,e in sorted(entries.items()):
        rr=perkey[key];n=len(rr);study=e['reference']['count'];missing=e['reference']['missing']
        intervals.append(dict(location=e['source']['reference_location'],camera=e['camera'],bin_start=e['reference']['start'],study_bicycles_all_recorded_channels=study,study_has_missing_cells=missing,annotated_encounters=n,study_minus_annotated=study-n if not missing else '',review_status='ANNOTATIONS_RECEIVED' if n else 'NO_JSON_OWNER_COULD_NOT_FIND_CYCLISTS',speed_estimates=sum(r['speed_mph']!='' for r in rr),workbook=e['workbook'],channel_correspondence='Not visually verified; sums raw study channels'))
    summaries=[]
    for location in sorted({r['location'] for r in intervals}):
        bins=[r for r in intervals if r['location']==location];people=[r for r in encounters if r['location']==location];values=[r['speed_mph'] for r in people if r['speed_mph']!=''];reference=[float(r['source_mph']) for r in refs[location]]
        mean=statistics.mean(values) if values else '';refmean=statistics.mean(reference) if reference else ''
        study=sum(r['study_bicycles_all_recorded_channels'] for r in bins);n=len(people)
        summaries.append(dict(location=location,positive_or_missing_bins=len(bins),bins_with_json=sum(r['review_status']=='ANNOTATIONS_RECEIVED' for r in bins),study_cyclists_in_selected_bins=study,manual_annotated_encounters=n,study_minus_annotated=study-n,manual_speed_sample=len(values),manual_mean_mph=mean,study_speed_reference_sample=len(reference),study_speed_mean_mph=refmean,difference_mph=mean-refmean if mean!='' and refmean!='' else '',status='UNMATCHED_GROUP_COMPARISON_NOT_SPEED_ACCURACY'))
    for b in intervals:
        auto=auto_bins.get((b['camera'],b['bin_start']))
        b['automatic_count']=int(auto['bicyclists_total']) if auto else ''
        b['automatic_coverage']='FULL_BIN_EXPORTED' if auto else 'NO_FULL_BIN_EXPORTED'
    for r in summaries:
        a=auto_by_site.get(r['location'],{})
        r.update(automatic_speed_sample=a.get('model_candidate_sample',''),automatic_mean_mph=a.get('model_candidate_mean_mph',''),automatic_minutes=a.get('minutes_processed',''),automatic_state=a.get('state','NOT_EXPORTED'),automatic_found_candidates=a.get('found_candidate_tracks',''),automatic_counted_candidates=a.get('counted_candidate_tracks',''))
        matching=[auto_bins.get((b['camera'],b['bin_start'])) for b in intervals if b['location']==r['location']]
        r['automatic_count_matched_bins']=sum(b is not None for b in matching)
        r['automatic_count_available_bins']=sum(int(b['bicyclists_total']) for b in matching if b is not None) if any(b is not None for b in matching) else ''
        r['study_count_automatic_available_bins']=sum(b['study_bicycles_all_recorded_channels'] for b in intervals if b['location']==r['location'] and (b['camera'],b['bin_start']) in auto_bins)
        r['automatic_count_in_selected_bins']=sum(int(b['bicyclists_total']) for b in matching) if matching and all(b is not None for b in matching) else ''
    write_csv(out/'encounters.csv',encounters);write_csv(out/'interval_counts.csv',intervals);write_csv(out/'site_summary.csv',summaries);write_csv(out/'id_splits.csv',splitlog)
    (out/'normalized_observations.json').write_text(json.dumps(dict(policy='Originals unchanged; interval-local IDs split only on gaps>'+str(gap)+' seconds per owner instruction; no speed fitted to reference',observations=normalized,encounters=encounters),indent=2)+'\n')
    # Snapshot exact pack data used, so subsequent calibrations cannot silently change this report.
    (out/'review_inputs.json').write_text(json.dumps(dict(entries=pack['entries'],unavailable_count=pack.get('unavailable_count',len(pack.get('unavailable',[]))),calibration_export=str(calibrations) if calibrations else '',reference_source=str(references),original_files=[p.name for p in originals]),indent=2)+'\n')
    write_reports(input_dir,out,summaries,encounters,intervals,entries,refs,automatic,len(originals),len(splitlog))
    return summaries,encounters

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,default=Path('manual'));p.add_argument('--manifest',type=Path,required=True);p.add_argument('--references',type=Path,default=Path(__file__).resolve().parents[1]/'exp_results/speed_reference_readiness_20261023/all_reference_records.csv');p.add_argument('--out',type=Path,default=Path('manual/analysis'));p.add_argument('--calibrations',type=Path);a=p.parse_args();rows,people=run(a.input,a.manifest,a.references,a.out,calibrations=a.calibrations);print(json.dumps(rows,indent=2))
