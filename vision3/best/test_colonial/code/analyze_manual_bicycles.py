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


def run(input_dir,manifest,references,out,gap=30,calibrations=None):
    out.mkdir(parents=True,exist_ok=True)
    pack=json.loads(manifest.read_text());entries={e['key']:e for e in pack['entries']}
    snapshot=out/'automatic_report_snapshot.json'
    automatic=json.loads(snapshot.read_text()) if snapshot.exists() else {}
    if calibrations:automatic.update(json.loads(calibrations.read_text()))
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
    for r in summaries:
        a=auto_by_site.get(r['location'],{})
        r.update(automatic_speed_sample=a.get('model_candidate_sample',''),automatic_mean_mph=a.get('model_candidate_mean_mph',''),automatic_minutes=a.get('minutes_processed',''),automatic_state=a.get('state','NOT_EXPORTED'))
        matching=[auto_bins.get((b['camera'],b['bin_start'])) for b in intervals if b['location']==r['location']]
        r['automatic_count_matched_bins']=sum(b is not None for b in matching)
        r['automatic_count_in_selected_bins']=sum(int(b['bicyclists_total']) for b in matching) if matching and all(b is not None for b in matching) else ''
    write_csv(out/'encounters.csv',encounters);write_csv(out/'interval_counts.csv',intervals);write_csv(out/'site_summary.csv',summaries);write_csv(out/'id_splits.csv',splitlog)
    (out/'normalized_observations.json').write_text(json.dumps(dict(policy='Originals unchanged; interval-local IDs split only on gaps>'+str(gap)+' seconds per owner instruction; no speed fitted to reference',observations=normalized,encounters=encounters),indent=2)+'\n')
    # Snapshot exact pack data used, so subsequent calibrations cannot silently change this report.
    (out/'review_inputs.json').write_text(json.dumps(dict(entries=pack['entries'],unavailable_count=len(pack.get('unavailable',[])),reference_source=str(references),original_files=[p.name for p in originals]),indent=2)+'\n')
    fmt=lambda n:'pending' if n=='' else f'{n:.2f}'
    totalstudy=sum(r['study_cyclists_in_selected_bins'] for r in summaries);totalmanual=len(encounters);usable=sum(r['speed_mph']!='' for r in encounters)
    lines=['# Manual bicycle review: what the results mean','',f'Analysed {len(originals)} JSON files: **{totalmanual} separate annotated cyclist encounters**, with **{usable} provisional speed estimates**. Original files are unchanged. {len(splitlog)} exports reused IDs across widely separated encounters; those encounters are now separated. Reusing ID1 in another 15-minute interval is always treated as a new person.','', '## Counts and speeds together','',f'The selected positive/missing study intervals contain {totalstudy} recorded bicycles across workbook channels; your files annotate {totalmanual} encounters. The difference ({totalstudy-totalmanual}) means **study bicycles not represented in the submitted annotations**, not automatically detector misses or your mistakes. Missing JSONs mean you could not find/annotate cyclists, and remain unconfirmed. Video/channel/clock correspondence still matters.','', 'Each selected bin is 15 minutes. Bins with JSON shows how many selected intervals have submitted annotations. Count references cover those selected intervals; study speed references are a separate group of cyclists, with no matching video timestamps. Speed averages are per cyclist, not per hour. Pending speeds are not zero.','', '| Location | Selected bins (JSONs) | Study count | Manual count | Not represented | Automatic count, same bins | Automatic speed n | Automatic mph | Manual speed n | Manual mph | Study speed n | Study mph |','|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|']
    for r in summaries:
        ac=r['automatic_count_in_selected_bins'] if r['automatic_count_in_selected_bins']!='' else 'awaiting bin export'
        am=r['automatic_mean_mph'];automatic_mean='no usable speed' if am=='' else f'{float(am):.2f}'
        manual_mean=fmt(r['manual_mean_mph']) if r['manual_annotated_encounters'] else 'no annotations'
        if manual_mean=='pending':manual_mean='waiting for calibration / sufficient span'
        lines.append(f"| {r['location']} | {r['positive_or_missing_bins']} ({r['bins_with_json']}) | {r['study_cyclists_in_selected_bins']} | {r['manual_annotated_encounters']} | {r['study_minus_annotated']} | {ac} | {r['automatic_speed_sample']} | {automatic_mean} | {r['manual_speed_sample']} | {manual_mean} | {r['study_speed_reference_sample']} | {fmt(r['study_speed_mean_mph'])} |")
    lines+=['', 'Automatic mph comes from the finished automatic batch; manual mph uses your repaired clicks. The two means may use different cyclists and intervals, so their difference is not tracking error or accuracy. Both use learned camera scale; manual clicking does not independently validate that scale. Automatic speed n is the selected speed sample, not the total bicycle count. Automatic counts are compared only when the same full selected bins have been exported. Until then they remain unavailable, not zero. The automatic summary currently available locally is a rounded transcription of the owner-pasted batch report; final export supplies original values.', '', 'Not represented = study count minus annotated encounters, conditional on matching camera coverage. Study mph is from separate speed observations, not person-linked ground-truth speeds for these clips. A small speed difference is descriptive agreement, not validated accuracy.']
    lines+=['','Manual positions are projected with the learned camera calibration bundled in the review page. Speed = sum of successive ground distances / elapsed seconds, converted from metres/second to mph. This matches the page method after repairing IDs. Clicking noise can inflate path length. Physical scale, lens distortion and transfers from road to raised paths/sidewalks remain unvalidated. Numerical geometry checks do not prove correct real-world scale.','', 'Colonial study averages combine bike lane and sidewalk. Separate references: bike lane12cyclists, mean11.11mph; sidewalk11cyclists, mean7.82mph. No lane was supplied with your manual clicks, so we cannot claim a facility-matched comparison.','', '## Interpretation: good or bad?', '', 'Carroll and Columbia show descriptive agreement with the separate study means. Colonial is moderately higher, with unresolved bike-lane/sidewalk matching. Aloma is substantially higher and needs a calibration/point-placement check before use. None establishes matched-person speed accuracy. Pending sites have no speed conclusion yet.', '', '## Every annotated cyclist and time used','','Times are inferred source clock times, not independently verified. A different cyclist ID in each interval is a separate encounter; no repeat-person identity is assumed.','', '| Camera | Video interval starts | Encounter | Original ID | Measurement start | Measurement end | Points | mph | Status |','|---|---|---|---|---|---|---:|---|']
    for r in encounters:lines.append(f"| {r['camera']} | {r['bin_start']} | {r['encounter_id'].rsplit('__',1)[-1]} | {r['original_id']} | {r['start']} | {r['end']} | {r['points']} | {fmt(r['speed_mph'])} | {r['status']} |")
    lines+=['','## Missing JSONs / cyclists not found by the reviewer','','These are review coverage gaps, not confirmed absence:','']
    for r in intervals:
        if r['review_status']!='ANNOTATIONS_RECEIVED':lines.append(f"- {r['camera']}, {r['bin_start']}: study{r['study_bicycles_all_recorded_channels']}, no annotations received.")
    lines+=['','## What needs checking next','','- Obtain the final saved calibration JSONs for Edgewater, Lee, Pleasant Hill, Rinehart and University. These were absent when the manual pack was generated. Existing clicks can be reused without reannotation. Some short encounters may still lack the1.5-second minimum required by this workflow.','- Count comparisons cover only selected source-hour bins in the review manifest, not full study totals. No positive review bins were included for Baxter, Daniels or Winter Park in this pack; Silver Star had no mapped source.','- Raw worksheet channel counts may cover more than the visible camera area. The differences above are conditional until visible channels and clocks are confirmed.','- Automatic detector misses cannot be inferred from manual counts alone. Known Carroll evidence remains study2, manual2, automatic counted0 in12:30–12:45. Its second cyclist had a raw track rejected by filters. For all sites, matched automatic bin counts are needed to separate detector misses from filtered tracks.','', 'Files: site_summary.csv compares means and coverage; interval_counts.csv preserves each bin; encounters.csv records per-person times/speeds; normalized_observations.json contains corrected IDs with original IDs retained; id_splits.csv explains each repair; review_inputs.json snapshots the source manifest and calibration. Repeated exact observations across exports were deduplicated: '+str(duplicates)+'.','']
    lines += ['## Finish the pending speed calculations', '', 'No reannotation or GPU run is required. The final adaptive batch has newer calibration files than the review pack. On HiPerGator, after pulling the new helper, run:', '', '```bash', 'python code/export_manual_calibrations.py --batch exp_results/ADAPTIVE_SPEED_20261024_195012', '```', '', 'Paste that small JSON output into sofar.md, or export it with --out manual_calibrations.json. This transfers matrices, automatic speed summaries and same-bin count data, not videos. The analysis supports --calibrations FILE and checks camera and source clock before applying them.', '']
    (input_dir/'README.md').write_text('\n'.join(lines))
    return summaries,encounters

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,default=Path('manual'));p.add_argument('--manifest',type=Path,required=True);p.add_argument('--references',type=Path,default=Path(__file__).resolve().parents[1]/'exp_results/speed_reference_readiness_20261023/all_reference_records.csv');p.add_argument('--out',type=Path,default=Path('manual/analysis'));p.add_argument('--calibrations',type=Path);a=p.parse_args();rows,people=run(a.input,a.manifest,a.references,a.out,calibrations=a.calibrations);print(json.dumps(rows,indent=2))
