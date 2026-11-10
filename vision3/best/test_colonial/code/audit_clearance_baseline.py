#!/usr/bin/env python3
"""CPU-only comparison of returned clearance tracks with prior manual speeds.

Published manual speeds are comparison values sharing learned scale, not truth.
Read original exports without changing them. Audit products go in a new folder.
"""
import argparse
import csv
import datetime as dt
import json
from pathlib import Path
import numpy as np
import cv2
from clearance_metrics import prepare, local_motion, kalman_motion
from clearance_review import screening_reports

REPO=Path(__file__).resolve().parents[4]
MPH=2.23694


def read(path):
    with Path(path).open(newline='') as f:return list(csv.DictReader(f))


def write(path,rows):
    with Path(path).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else ['status']);w.writeheader();w.writerows(rows)


def support(hull,points):
    return float(np.mean([cv2.pointPolygonTest(np.asarray(hull,np.float32).reshape(-1,1,2),tuple(map(float,p)),False)>=0 for p in points])) if len(points) else None


def audit(batch,out,repo=REPO):
    out.mkdir(parents=True,exist_ok=False)
    plan=json.loads((batch/'manifest.json').read_text())
    encounters=read(repo/'manual/analysis/encounters.csv')
    robust={r['encounter_id']:r for r in read(repo/'manual/speed_plan_20261027/trajectory/cyclists.csv')}
    prior=json.loads((repo/'manual/analysis/final_batch_export.json').read_text())
    previous_H=np.asarray(prior['calibrations']['s03_colonial_north']['calibration']['H'])
    comparisons=[];supports=[];positions=[]
    for task in plan['tasks']:
        d=batch/task['key'];g=json.loads((d/'geometry.json').read_text());log=json.loads((d/'run_log.json').read_text())
        H=np.asarray(g['H']);hull=g['hull']
        labels={r['track_id']:r for r in read(d/'tracks_csv.csv')}
        paths=prepare(read(d/'trajectories_csv.csv'),H,hull,log['fps'],labels)
        annotations=json.loads((repo/task['selection_evidence']).read_text())['observations']
        clicks=[r for r in annotations if task['start_s']<=r['source_seconds']<=task['start_s']+task['duration_s']]
        if not clicks:continue
        lo=min(r['source_seconds'] for r in clicks);hi=max(r['source_seconds'] for r in clicks)
        candidates=[r for r in encounters if r['camera']=='Colonial North' and r['source_files']==Path(task['selection_evidence']).name
                    and abs((dt.datetime.fromisoformat(r['start'])-dt.datetime.fromisoformat(plan['source_clock'])).total_seconds()-lo)<.01]
        if len(candidates)!=1:raise ValueError('Ambiguous prior manual encounter')
        manual=candidates[0];rob=robust[manual['encounter_id']]
        for (kind,tid),samples in paths.items():
            if kind!='cyclist':continue
            supports.append(dict(task=task['key'],cyclist_id=tid,observations=len(samples),
                automatic_contact_support_fraction=support(hull,[r['pixel'] for r in samples]),
                manual_contact_support_fraction=support(hull,[[r['x'],r['y']] for r in clicks]),
                maximum_H_difference_from_manual=float(np.max(abs(H-previous_H))),
                facility=labels[tid]['facility'],facility_status='provisional_geometry_label'))
            for click in clicks:
                t=click['source_seconds']-task['start_s'];nearest=min(samples,key=lambda r:abs(r['t']-t))
                if abs(nearest['t']-t)>.05:continue
                delta=nearest['pixel']-np.array([click['x'],click['y']])
                positions.append(dict(task=task['key'],cyclist_id=tid,source_seconds=click['source_seconds'],
                    manual_x=click['x'],manual_y=click['y'],automatic_x=nearest['pixel'][0],automatic_y=nearest['pixel'][1],
                    sample_time_offset_s=nearest['t']-t,pixel_offset=float(np.linalg.norm(delta)),
                    interpretation='different_contact_definitions_not_person_identity_or_accuracy_test'))
            for method in ('local','kalman','rts'):
                motion=local_motion(samples,.5) if method=='local' else kalman_motion(samples,rts=method=='rts')
                chosen=[r for r in motion.values() if lo<=task['start_s']+r['t']<=hi]
                mph=[float(np.linalg.norm(r['velocity']))*MPH for r in chosen]
                times=sorted(r['t'] for r in chosen)
                observed=sum(b-a for a,b in zip(times[:-1],times[1:]) if b-a<=.20)
                value=float(np.median(mph)) if mph else None
                comparisons.append(dict(task=task['key'],detector=task['detector'],cyclist_id=tid,
                    prior_encounter_id=manual['encounter_id'],method=method,manual_path_mph=float(manual['speed_mph']),
                    prior_robust_manual_mph=float(rob['robust_mph']),automatic_median_mph=value,
                    difference_from_manual_mph=value-float(manual['speed_mph']) if value is not None else None,
                    manual_source_start_s=lo,manual_source_end_s=hi,manual_span_s=hi-lo,
                    automatic_observed_span_s=observed,coverage_fraction=observed/(hi-lo),automatic_samples=len(chosen),
                    scale_status='identical_learned_H_not_independent_ground_truth',
                    identity_status='same_window_single_candidate_visual_identity_provisional'))
    write(out/'speed_baseline_comparison.csv',comparisons)
    write(out/'calibration_support.csv',supports)
    write(out/'manual_automatic_position_offsets.csv',positions)
    interactions=read(batch/'all_interactions.csv')
    screening_reports(out,interactions)
    return comparisons,supports


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--repo',type=Path,default=REPO)
    a=p.parse_args();audit(a.batch.resolve(),a.out.resolve(),a.repo.resolve())


if __name__=='__main__':main()
