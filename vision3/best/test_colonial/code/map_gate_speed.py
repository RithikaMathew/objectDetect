#!/usr/bin/env python3
"""Approximate map-distance speeds from observed finite-gate crossings."""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def intersection(a,b,c,d):
    r=[b[i]-a[i] for i in (0,1)];s=[d[i]-c[i] for i in (0,1)]
    cross=lambda u,v:u[0]*v[1]-u[1]*v[0]
    den=cross(r,s)
    if abs(den)<1e-9:return None
    q=[c[i]-a[i] for i in (0,1)]
    t,u=cross(q,s)/den,cross(q,r)/den
    return t if 0<=t<=1 and 0<=u<=1 else None


def seconds(clock):
    h,m,s=map(float,clock.split(':'));return h*3600+m*60+s


def measure(samples,lines,max_gap=.5):
    samples=sorted(samples,key=lambda r:r['_t'])
    events=[]
    for line in lines:
        hits=[]
        for a,b in zip(samples,samples[1:]):
            gap=b['_t']-a['_t']
            if not 0<gap<=max_gap:continue
            f=intersection(a['_xy'],b['_xy'],*line)
            if f is not None:
                t=a['_t']+f*gap
                if not hits or t-hits[-1]>.1:hits.append(t)
        events.append(hits)
    result=dict(a_crossings=len(events[0]),b_crossings=len(events[1]),crossing_seconds='',mph='',kmh='',status='no_unique_complete_crossing')
    if not all(len(x)==1 for x in events):return result
    lo,hi=sorted(x[0] for x in events)
    if hi-lo<=0:return result
    gaps=[b['_t']-a['_t'] for a,b in zip(samples,samples[1:]) if a['_t']<hi and b['_t']>lo]
    if max(gaps,default=0)>max_gap:
        result['status']='gap_inside_measured_segment';return result
    result.update(crossing_seconds=round(hi-lo,6),status='map_based_estimate_identity_unverified')
    return result


def run(trajectories,tracks,config,out):
    c=json.loads(config.read_text());out.mkdir(parents=True,exist_ok=False)
    metadata={r['track_id']:r for r in csv.DictReader(tracks.open())}
    groups=defaultdict(list)
    for r in csv.DictReader(trajectories.open()):
        if r['track_id'] not in metadata or int(r.get('coasted','0')):continue
        r['_t']=seconds(r['time']);r['_xy']=[float(r['foot_x']),float(r['foot_y'])]
        groups[r['track_id']].append(r)
    scale=[c['trajectory_size'][i]/c['ref_size'][i] for i in (0,1)]
    lines=[[[p[i]*scale[i] for i in (0,1)] for p in c[k]] for k in ('line_a','line_b')]
    results=[]
    for tid,meta in metadata.items():
        result=measure(groups[tid],lines,c['max_gap_seconds'])
        if result['crossing_seconds']!='':
            ftps=c['distance_feet']/result['crossing_seconds']
            result.update(mph=round(ftps*3600/5280,2),kmh=round(ftps*.3048*3.6,2))
        results.append(dict(track_id=tid,label=meta['label'],counted=meta['counted'],first_time=meta['first_time'],last_time=meta['last_time'],**result))
    with (out/'speeds.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
    shutil_config=out/'gates.json';shutil_config.write_text(json.dumps(c,indent=2)+'\n')
    valid=[r for r in results if r['mph']!='']
    text=['# University map-based segment speeds','',f'Distance: {c["distance_feet"]} feet. Tracks checked: {len(results)}. Complete gap-checked estimates: {len(valid)}.','',
          'Owner supplied map distance and marked endpoints; gate pixels transcribed approximately from the 1600×1070 screenshot and scaled to720×480. These are map-based estimates, not surveyed or Excel-validated speeds. Track identity and user type remain unverified. Includes rejected person tracks to avoid hiding potential cyclists. No vehicle speeds: the distance applies only to this sidewalk segment.','',
          '| Track | Label | Counted | Clock start | Seconds | mph |','|---|---|---|---|---:|---:|']
    text += [f'| {r["track_id"]} | {r["label"]} | {r["counted"]} | {r["first_time"]} | {r["crossing_seconds"]} | {r["mph"]} |' for r in valid]
    text += ['','Finite crossing lines, observed footpoints only; no gap above0.5seconds at either crossing or between gates; repeated crossings excluded. Distance is not fitted to workbook speeds. Missing complete tracks receive no mph.']
    (out/'RESULTS.md').write_text('\n'.join(text)+'\n')
    print('\n'.join(text))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('trajectories','tracks','config','out'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();run(a.trajectories,a.tracks,a.config,a.out)
