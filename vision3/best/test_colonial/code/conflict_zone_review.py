#!/usr/bin/env python3
"""Screen point-occupancy time gaps in a user-defined conflict polygon.

Not footprint PET, calibrated TTC, confirmed near misses or safety validation.
No mph or metric scene scale is needed; camera-specific zone/IDs still matter.
"""
import argparse
from collections import defaultdict
import csv
import json
from pathlib import Path
from labelled_lane_speed import inside
from speed_gates import crossing


def visits(samples,polygon,fps,max_gap=.5):
    segments=[];segment=[]
    for r in sorted(samples,key=lambda r:int(r['frame'])):
        if int(r.get('coasted','0')):continue
        f=int(r['frame'])
        if segment and not 0<(f-segment[-1][0])/fps<=max_gap:
            segments.append(segment);segment=[]
        segment.append((f,(float(r['foot_x']),float(r['foot_y']))))
    if segment:segments.append(segment)
    complete=[]
    for segment in segments:
        raw=[]
        for (fa,a),(fb,b) in zip(segment,segment[1:]):
            cuts=[0.,1.]
            for i,c in enumerate(polygon):
                f=crossing(a,b,c,polygon[(i+1)%len(polygon)])
                if f is not None:cuts.append(f)
            cuts=sorted(set(round(x,10)for x in cuts))
            for lo,hi in zip(cuts,cuts[1:]):
                mid=(lo+hi)/2;point=[a[j]+mid*(b[j]-a[j])for j in (0,1)]
                if hi>lo and inside(point,polygon):raw.append(((fa+lo*(fb-fa)-1)/fps,(fa+hi*(fb-fa)-1)/fps))
        merged=[]
        for start,end in raw:
            if merged and abs(start-merged[-1][1])<1e-7:merged[-1]=(merged[-1][0],end)
            else:merged.append((start,end))
        if not segment:continue
        first=(segment[0][0]-1)/fps;last=(segment[-1][0]-1)/fps
        for start,end in merged:
            if abs(start-first)<1e-7 or abs(end-last)<1e-7:continue # Censored visit: entry/exit unknown.
            complete.append((start,end))
    return complete


def candidates(events,max_gap):
    rows=[];events=sorted(events,key=lambda e:e['entry'])
    for i,a in enumerate(events):
        for b in events[i+1:]:
            if b['entry']-a['exit']>max_gap:break
            if a['id']==b['id']:continue
            overlap=b['entry']<a['exit']
            rows.append(dict(first_id=a['id'],first_label=a['label'],second_id=b['id'],second_label=b['label'],
                first_exit=a['exit'],second_entry=b['entry'],point_zone_gap_seconds='' if overlap else round(b['entry']-a['exit'],4),
                status='simultaneous_point_occupancy_review' if overlap else 'short_point_zone_gap_review',
                confirmed_near_miss=0,identity_verified=0))
    return rows


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--people',type=Path,required=True)
    ap.add_argument('--vehicles',type=Path);ap.add_argument('--zone',type=Path,required=True)
    ap.add_argument('--fps',type=float,required=True);ap.add_argument('--frame-size',required=True,help='WxH for these trajectories')
    ap.add_argument('--max-gap-seconds',type=float,default=3,help='Candidate review window only; not a validated safety cutoff')
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    if a.fps<=0 or a.max_gap_seconds<=0:ap.error('FPS and candidate window must be positive')
    config=json.loads(a.zone.read_text());size=[float(x)for x in a.frame_size.split('x')]
    if not config.get('reviewer')or not config.get('source') or len(config.get('polygon',[]))<3:raise ValueError('Need a camera-specific reviewed conflict polygon with source')
    if a.out.exists():raise FileExistsError(a.out)
    polygon=[[p[i]*size[i]/config['ref_size'][i]for i in (0,1)]for p in config['polygon']]
    tracks=defaultdict(list);labels={}
    for prefix,path in [('person',a.people),('vehicle',a.vehicles)]:
        if path is None:continue
        with path.open()as f:
            for row in csv.DictReader(f):
                key=prefix+':'+row['track_id'];tracks[key].append(row);labels[key]=row.get('label','unknown')
    events=[]
    for key,rr in tracks.items():
        for entry,exit in visits(rr,polygon,a.fps):events.append(dict(id=key,label=labels[key],entry=entry,exit=exit))
    rows=candidates(events,a.max_gap_seconds);a.out.mkdir(parents=True)
    fields=['first_id','first_label','second_id','second_label','first_exit','second_entry','point_zone_gap_seconds','status','confirmed_near_miss','identity_verified']
    with (a.out/'candidates.csv').open('w',newline='')as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    summary=dict(candidate_pairs=len(rows),complete_point_visits=len(events),vehicle_trajectories_supplied=a.vehicles is not None,
        frame_time_basis='seconds from full source frame1, not necessarily relative to processed clip start',
        metric_speed_needed=False,confirmed_near_misses=0,
        limitation='Point proxy, not road-user footprints or exact common-point PET. IDs and zone geometry require visual review. Overlap is not proof of collision. Missing vehicles prevent cyclist-vehicle assessment. Missed detections, occlusion, perspective and censoring cause missed candidates. No universal safety threshold.')
    (a.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
