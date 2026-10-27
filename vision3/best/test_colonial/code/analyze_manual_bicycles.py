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
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


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


def write_reports(input_dir,out,summaries,encounters,intervals,entries,refs,automatic,file_count,split_count):
    """Short professor-facing summary; detailed evidence remains separate."""
    fmt=lambda x:'Unavailable' if x=='' else f'{float(x):.2f}'
    duration_path=Path(__file__).resolve().parents[4]/'reports/cluster_returns/20261024/recording_lengths/by_camera.csv'
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
    lines += ['', '**Next comparison:** [same-video HiPerGator rerun](../docs/MATCHED_MANUAL_SPEED_RUN.md) is prepared for the18submitted annotation clips (nine cameras), using the new1.5-second daytime setting and no sample-quota early stopping. It reads the exact manual MP4s. Results are pending; this table still shows the earlier baseline coverage.', '', '**Time coverage differs:** Manual selection is the positive-count intervals offered for review, not continuous annotation or measured riding time. HiPerGator completed minutes includes its finished consecutive windows, including zero-count bins, until its quota or one-hour limit. Aloma manual selection is 45 minutes; its recovery completed about 60 minutes after the original node failure. Most other sites completed about 60 minutes; Columbia stopped after 30 minutes. Speed estimates themselves use only the saved per-cyclist seconds, and may involve different people. This is not a matched-duration or matched-person speed comparison.', '', 'Numbers after mph are the number of cyclists contributing to that average. Count coverage such as **2/4 bins** means only two of the four selected intervals are included in that automatic count comparison. A missing speed is not zero.','',
              '**Why Aloma has 4 cyclists but 26 speed records:** Aloma Path has 48 source files; their total playback hours are not yet verified. This pilot selected the first available day’s hour nearest noon; within that hour, only intervals with positive study bicycle counts were sent for manual review. For Aloma these were 12:00–12:15, 12:30–12:45 and 12:45–13:00 on October 30, 2019: 45 minutes containing 4 study bicycles, all 4 annotated. The remaining interval recorded zero bicycles.','',
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
              '**Shorter-duration experiment prepared:** [rerun instructions](../docs/SHORT_TRACK_SPEED_RUN.md) lower the daytime bicycle minimum to1.5seconds across all13sites, reusing saved calibration. Other counting rules and nighttime policy are preserved. Updated results are pending; the table above remains the measured three-second baseline.','',
              '**Aloma duration-filter finding:** all five rejected bicycle-labelled tracks lasted less than the daytime three-second minimum: 2.9, 1.6, 2.0, 2.7 and 1.7 seconds. Four had 100% detector bicycle labels and weighted bicycle scores of 0.98–1.00. The duration gate necessarily rejects these tracks; other gates may also apply. This shows that short tracked duration can exclude strongly supported cyclists. It does not prove all five are distinct real cyclists: the study count and manual review contain four, so the extra candidate needs review before relaxing filters. The baseline results above remain unchanged. [Saved audit](analysis/aloma_duration_audit_20261026.csv).','',
              '**Missing results:** Aloma’s recovery completed about 60 minutes and recorded 5 bicycle-labelled candidate tracks, all rejected by counting filters. Its automatic speed is unavailable, not zero mph. Five candidate tracks are not necessarily five different real cyclists. Carroll and Rinehart had candidates rejected by counting filters. West Orange has no located/annotated manual cyclists. One Edgewater encounter spans only 1.4 seconds, below the current 1.5-second speed safeguard. No reannotation of completed encounters is required.','',
              '### Recording hours for every speed-reference location','',
              '**Source files** counts separate MP4 video files. **Total available hours** is the sum of their playback lengths, not the number of files or time analysed. For example, 48 one-hour files total about 48 hours, but 48 shorter files would total less. **Only Colonial North is fully measured. Other totals remain unverified until every source duration has been read.** Other camera sides are not added together.','',
              '**Why Columbia is unknown:** the inventory contains 49 MP4s, including multipart recordings with names such as `0000.02.001.mp4`. Their full durations have not been measured, so 49 files cannot safely be called 49 hours. The selected noon source can still be reviewed; the unknown value concerns the complete collection’s length.','',
              '| Location | Camera | Source files | Total available hours | Basis |','|---|---|---:|---|---|']
    for r in recordings:lines.append(f"| {r['location']} | {r['camera']} | {r['source_files']} | {r['available_hours']} | {r['basis']} |")
    lines += ['', 'Detailed encounter times and exclusions: [analysis/DETAILS.md](analysis/DETAILS.md). Tables: [site summaries](analysis/site_summary.csv), [15-minute counts](analysis/interval_counts.csv), [per-cyclist speeds](analysis/encounters.csv). Original annotation JSONs are unchanged.','']
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
