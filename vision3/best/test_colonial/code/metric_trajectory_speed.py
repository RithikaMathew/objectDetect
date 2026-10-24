#!/usr/bin/env python3
"""Estimate partial-track speed after metric calibration; no complete gate crossing needed."""
import argparse
import csv
import json
from pathlib import Path
import numpy as np
import cv2
from labelled_lane_speed import load_calibration
from eval_truth import CLIPS


def estimate(samples,fps,H,calibration_hull,min_span=1.5,max_gap=.5,window=1.0):
    segments=[];current=[]
    for r in sorted(samples,key=lambda r:int(r['frame'])):
        if int(r.get('coasted','0')):continue
        xy=np.array([float(r['foot_x']),float(r['foot_y'])]);frame=int(r['frame'])
        inside=cv2.pointPolygonTest(calibration_hull,tuple(xy),False)>=0
        if not inside:
            if current:segments.append(current);current=[]
            continue
        if current and not 0<(frame-current[-1][0])/fps<=max_gap:
            segments.append(current);current=[]
        v=H@np.array([*xy,1])
        if not np.isfinite(v).all() or abs(v[2])<1e-8:
            if current:segments.append(current);current=[]
            continue
        current.append((frame,*(v[:2]/v[2])))
    if current:segments.append(current)
    speeds=[];used=0;measurement_intervals=[]
    for segment in segments:
        a=np.asarray(segment)
        if len(a)<5 or (a[-1,0]-a[0,0])/fps<min_span:continue
        used+=1;t=a[:,0]/fps;used_frames=[]
        for i in np.linspace(0,len(a)-1,min(200,len(a)),dtype=int):
            mask=np.abs(t-t[i])<=window/2
            if mask.sum()<5 or np.ptp(t[mask])<window*.6:continue
            tc=t[mask]-t[mask].mean();den=float(tc@tc)
            if den<=0:continue
            velocity=tc@a[mask,1:]/den;speeds.append(float(np.linalg.norm(velocity)))
            used_frames.extend(a[mask,0].astype(int).tolist())
        if used_frames:measurement_intervals.append([min(used_frames),max(used_frames)])
    if not speeds:return dict(speed_mph='',speed_kmh='',windows=0,segments=used,measurement_frame_intervals='[]',status='no_sufficient_continuous_in_calibration_segment')
    median=float(np.median(speeds));mad=float(np.median(np.abs(np.array(speeds)-median)))
    return dict(speed_mph=round(median*2.2369362921,3),speed_kmh=round(median*3.6,3),
        windows=len(speeds),segments=used,measurement_frame_intervals=json.dumps(measurement_intervals),window_speed_MAD_mph=round(mad*2.2369362921,3),
        status='map_or_metric_calibrated_partial_track_estimate_not_speed_validated')


def run(root,run_name,people_path,calibration_path,out):
    if out.exists():raise FileExistsError(out)
    calibration=json.loads(calibration_path.read_text())
    if calibration.get('measurement_source','').strip().lower()in ('','n/a','unknown','none'):raise ValueError('Actual metric landmark measurement source required')
    with people_path.open()as f:people=[r for r in csv.DictReader(f)if r['truth_class']=='cyclist']
    results=[]
    for clip,c in CLIPS.items():
        prefix=f'Standard_SCU8OG_2019-07-10_0000.{c["chunk"]:03d}'
        log=json.loads((root/'logs'/run_name/f'{prefix}_run_log.json').read_text());size=log['resolution']
        H=load_calibration(calibration_path,size)
        scale=np.array(size)/np.array(calibration['ref_size'])
        hull=cv2.convexHull((np.asarray(calibration['image_points'])*scale).astype(np.float32))
        with (root/'counts'/run_name/f'{prefix}_trajectories.csv').open()as f:rows=list(csv.DictReader(f))
        import datetime as dt
        t0=dt.datetime.fromisoformat(c['start'])
        from eval_truth import read_truth
        truth={r['id']:r for r in read_truth(root/c['truth'])[0]}
        for person in [p for p in people if p['clip']==clip]:
            p=truth[person['truth_id']];samples=[]
            for r in rows:
                if r['track_id']!=person['candidate_track_id']:continue
                sec=(dt.datetime.combine(t0.date(),dt.time.fromisoformat(r['time']))-t0).total_seconds()
                if p['s']<=sec<=p['e']:samples.append(r)
            result=estimate(samples,log['fps'],H,hull)
            results.append(dict(clip=clip,truth_id=person['truth_id'],track_id=person['candidate_track_id'],
                identity_verified=person['identity_verified'],**result))
    fields=list(dict.fromkeys(k for r in results for k in r))
    with out.open('x',newline='')as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(results)
    print(out)

def run_source(run_log,site,calibration_path,out):
    """Apply the same partial-track estimator to a new study-camera source."""
    log=json.loads(run_log.read_text());c=json.loads(calibration_path.read_text())
    if c.get('site')!=site or c.get('units')!='metres':raise ValueError('Wrong camera or ground units')
    if not c.get('reviewer') or c.get('measurement_source','').strip().lower()in ('','n/a','unknown','none'):raise ValueError('Measured landmark evidence required')
    import re
    date=re.search(r'_(\d{4}-\d{2}-\d{2})_',Path(log['video_path']).name)
    if date is None or c.get('recording_date')!=date[1]:raise ValueError('Calibration recording date differs from source session')
    image=np.asarray(c['image_points'],float);world=np.asarray(c['world_points_metres'],float)
    if image.shape!=world.shape or image.ndim!=2 or image.shape[1]!=2 or len(image)<4:raise ValueError('Need four or more metric correspondences')
    image=image*np.array(log['resolution'])/np.array(c['ref_size'])
    H,_=cv2.findHomography(image,world,0)
    if H is None or not np.isfinite(H).all():raise ValueError('Invalid homography')
    hull=cv2.convexHull(image.astype(np.float32));samples={}
    def read_csv(path):
        with Path(path).open()as f:return list(csv.DictReader(f))
    tracks=read_csv(log['tracks_csv'])
    for r in read_csv(log['trajectories_csv']):samples.setdefault(r['track_id'],[]).append(r)
    results=[]
    for track in tracks:
        if not int(track['counted']):continue
        r=estimate(samples.get(track['track_id'],[]),log['fps'],H,hull)
        results.append(dict(site=site,source=log['video_path'],object_kind='person',track_id=track['track_id'],
            user_type=track['label'],identity_verified=0,**r))
    if log.get('vehicle_trajectories_csv'):
        from collections import defaultdict,Counter
        vehicles=defaultdict(list)
        for r in read_csv(log['vehicle_trajectories_csv']):vehicles[r['track_id']].append(r)
        for tid,rr in vehicles.items():
            if not int(rr[0].get('counted',0)):continue
            r=estimate(rr,log['fps'],H,hull)
            results.append(dict(site=site,source=log['video_path'],object_kind='vehicle',track_id=tid,
                user_type=Counter(x['label']for x in rr).most_common(1)[0][0],identity_verified=0,**r))
    fields=list(dict.fromkeys(k for r in results for k in r))or['site','source','track_id','speed_mph','status']
    with out.open('x',newline='')as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(results)
    print(out)


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument('--run',default='b4_combo_static5');ap.add_argument('--people',type=Path)
    ap.add_argument('--run-log',type=Path,help='For a new study camera, evaluate its counted tracks');ap.add_argument('--site')
    ap.add_argument('--calibration',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    if a.run_log:
        if not a.site:ap.error('--site required with --run-log')
        run_source(a.run_log,a.site,a.calibration,a.out)
    elif a.people:run(a.root,a.run,a.people,a.calibration,a.out)
    else:ap.error('Supply --people (existing Colonial truth candidates) or --run-log and --site (new camera)')
