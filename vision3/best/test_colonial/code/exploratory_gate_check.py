#!/usr/bin/env python3
"""Check estimated gate crossings without assigning an unknown physical distance."""
import argparse
import csv
import datetime as dt
import json
from collections import defaultdict
from pathlib import Path

from eval_truth import CLIPS, read_truth, read_tracks, match
from speed_gates import crossing


def events(samples, fps, line, max_gap=.5):
    """Observed finite-line crossings in clip seconds; never bridge long gaps."""
    times=[]
    for a,b in zip(samples,samples[1:]):
        gap=(int(b['frame'])-int(a['frame']))/fps
        if not 0 < gap <= max_gap:
            continue
        fraction=crossing([float(a['foot_x']),float(a['foot_y'])],
                          [float(b['foot_x']),float(b['foot_y'])],*line)
        if fraction is not None:
            time=a['_s']+fraction*(b['_s']-a['_s'])
            if not times or time-times[-1]>.1:
                times.append(time)
    return times


def run(root, gates_path, out, study_dir, run_name='b4_combo_static5'):
    config=json.loads(gates_path.read_text())
    if config.get('site')!='Colonial North' or config.get('recording_date')!='2019-07-10':
        raise ValueError('Expected Colonial North 2019-07-10 gate coordinates')
    out.mkdir(parents=True,exist_ok=False)
    results=[]
    for clip,c in CLIPS.items():
        prefix=f'Standard_SCU8OG_2019-07-10_0000.{c["chunk"]:03d}'
        info=json.loads((root/'logs'/run_name/f'{prefix}_run_log.json').read_text())
        fps=info['fps'];scale=[a/b for a,b in zip(info['resolution'],config['ref_size'])]
        t0=dt.datetime.fromisoformat(c['start']);trajectories=defaultdict(list)
        with (root/'counts'/run_name/f'{prefix}_trajectories.csv').open() as stream:
            for row in csv.DictReader(stream):
                if int(row.get('coasted','0')):
                    continue
                row['_s']=(dt.datetime.combine(t0.date(),dt.time.fromisoformat(row['time']))-t0).total_seconds()
                trajectories[row['track_id']].append(row)
        truth,skipped=read_truth(root/c['truth'])
        if skipped:
            raise ValueError(f'Incomplete truth: {clip}')
        tracks=read_tracks(root/'counts'/run_name/f'{prefix}_tracks.csv',t0)
        for person,status,candidate in match(truth,tracks)[0]:
            if person['raw']!='cyclist':
                continue  # Do not calibrate bicycle speed with motorcycles or pedestrians.
            tid=candidate['id'] if candidate else ''
            samples=sorted(trajectories[tid],key=lambda r:int(r['frame']))
            # Full candidate track is a diagnostic only, never identity approval.
            for gate in config['gates']:
                crossings=[]
                for key in ('line_a','line_b'):
                    line=[[x*scale[0],y*scale[1]] for x,y in gate[key]]
                    crossings.append(events(samples,fps,line))
                complete=all(len(x)==1 for x in crossings)
                seconds=abs(crossings[1][0]-crossings[0][0]) if complete else None
                results.append(dict(clip=clip,truth_id=person['id'],candidate_track_id=tid,
                    identity_verified=0,scope='full_unverified_candidate_track',facility=gate['facility'],
                    line_a_crossings=len(crossings[0]),line_b_crossings=len(crossings[1]),
                    line_a_clip_seconds=json.dumps([round(t,4) for t in crossings[0]]),
                    line_b_clip_seconds=json.dumps([round(t,4) for t in crossings[1]]),
                    complete_crossing=int(complete and seconds>0),
                    crossing_seconds=round(seconds,6) if seconds is not None and seconds>0 else '',
                    speed_mph='',status='unknown_distance_and_no_verified_record_link' if complete else 'no_unique_complete_crossing'))
    with (out/'crossings.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(results[0]));writer.writeheader();writer.writerows(results)
    from labelled_lane_speed import speed_inventory
    inventory=speed_inventory(study_dir/'bicyclist speeds.xlsx')
    refs=inventory['unique_colonial_records']
    summary=dict(bicycle_truth_rows=len({(r['clip'],r['truth_id']) for r in results}),
        facility_checks=len(results),complete_crossings=sum(r['complete_crossing'] for r in results),
        workbook_Colonial_records=len(refs),verified_record_links=0,
        calibrated_facility_distances=0,held_out_speed_validation_pairs=0,
        mph_calculated=False,mae_mph=None,
        reason='No complete crossings and no verified record-to-person links; no distance fitted or speed validated.')
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    lines=['# Exploratory speed calibration — crossing feasibility','',
        f"Checked {summary['bicycle_truth_rows']} existing bicycle truth rows against both drawn facilities using their full saved candidate tracks.",
        'These candidate identities are time-matched, not human-approved. Motorcycles and pedestrians are excluded.',
        '',f"**Complete two-line crossings: {summary['complete_crossings']}. No mph or distance fit is possible with these tracks and lines.**",'',
        '| Clip | Truth | Candidate | Facility | First-line crossings | Second-line crossings |',
        '|---|---|---|---|---:|---:|']
    lines += [f"| {r['clip']} | {r['truth_id']} | {r['candidate_track_id']} | {r['facility']} | {r['line_a_crossings']} | {r['line_b_crossings']} |" for r in results]
    lines += ['',
        'Crossings use consecutive observed foot positions, finite lines, scaled image coordinates, and gaps no longer than0.5seconds. Lines are not extended; missing track segments are not extrapolated. Times in crossings.csv are relative to each15-minute clip.',
        '',f'Workbook scan found {len(refs)} unique Colonial speed records, but no verified links to these truth people. Record numbers are study identifiers, not detector track IDs. Do not pair people by whichever speed gives the closest answer.',
        '', 'To proceed: identify two lines inside a segment where the SAME cyclist is tracked continuously, and establish that cyclist’s Excel record using independent timestamp/identity evidence. Fit one fixed distance per facility from calibration people: distance_ft = recorded_mph ×5280/3600 ×crossing_seconds. Freeze it, then evaluate speed on DIFFERENT matched people. Keep all observations of one person in the same split. Fit and held-out people must use the same lines and facility; independently measured line spacing is an alternative.',
        '', 'Do not assign the workbook35ft/30ft to arbitrary visible lane spans. No new detector/GPU batch was submitted. Source gate JSON and existing truth files remain unchanged.']
    (out/'RESULTS.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument('--gates',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--study-dir',type=Path,required=True)
    a=ap.parse_args();run(a.root,a.gates,a.out,a.study_dir)
