#!/usr/bin/env python3
"""Per-track, class/facility and15-minute lane-use records; predicted counts only."""
import argparse
from collections import Counter,defaultdict
import csv
import datetime as dt
import json
from pathlib import Path
import numpy as np
from labelled_lane_speed import inside

FACILITIES=('road','bike_lane','sidewalk','path','grass')


def read(path):
    with Path(path).open()as f:return list(csv.DictReader(f))


def regions(z):
    result=[(name,p) for key,name in [('road','road'),('bike','bike_lane'),('sidewalk','sidewalk'),('path','path'),('grass','grass')] if (p:=z.get(key))]
    return result+[(r['facility'],r['polygon']) for r in z.get('extra_regions',[])]


def facility(point,z,size):
    if z is None:return 'unassigned'
    x,y=point
    if not(0<=x<size[0] and 0<=y<size[1]):return 'outside_frame'
    p=[x*z['ref_size'][0]/size[0],y*z['ref_size'][1]/size[1]]
    hits={name for name,poly in regions(z) if inside(p,poly)}
    return next(iter(hits)) if len(hits)==1 else 'overlap' if hits else 'unassigned'


def summarize_track(samples,z,size,dominance=.7):
    counts=Counter(facility((float(r['foot_x']),float(r['foot_y'])),z,size)for r in samples if not int(r.get('coasted','0')))
    total=sum(counts.values());name,n=counts.most_common(1)[0] if total else ('unassigned',0)
    if z is None:label='unassigned'
    elif not total:label='uncertain'
    elif name in FACILITIES and n/total>=dominance:label=name
    else:label='uncertain'
    return label,total,{key:round(value/total,6)for key,value in counts.items()} if total else {}


def write(path,rows,fields):
    with path.open('w',newline='')as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)


def report(run_log,out,zones=None,site='unknown'):
    log=json.loads(Path(run_log).read_text());z=json.loads(Path(zones).read_text()) if zones else None
    if z is not None:
        if z.get('site') and z['site']!=site:raise ValueError('Wrong site zone file')
        if not regions(z):raise ValueError('Zone file contains no usable polygons')
        for name,poly in regions(z):
            if name not in FACILITIES or len(poly)<3 or not np.isfinite(poly).all():raise ValueError('Invalid polygon')
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    people=read(log['tracks_csv']);person_samples=defaultdict(list)
    for r in read(log['trajectories_csv']):person_samples[r['track_id']].append(r)
    vehicles=defaultdict(list)
    if log.get('vehicle_trajectories_csv'):
        for r in read(log['vehicle_trajectories_csv']):vehicles[r['track_id']].append(r)
    rows=[];source_start=dt.datetime.fromisoformat(log['clip_start_clock'])
    def add(kind,tid,label,counted,samples):
        assigned,n,fractions=summarize_track(samples,z,log['resolution'])
        observed=[r for r in samples if not int(r.get('coasted','0'))]
        frames=[int(r['frame'])for r in observed]
        when=source_start+dt.timedelta(seconds=((min(frames)+max(frames))/2-1)/log['fps']) if frames else None
        bin_start=when.replace(minute=when.minute//15*15,second=0,microsecond=0).isoformat(sep=' ') if when else ''
        rows.append(dict(site=site,source=log['video_path'],run=log['params']['run'],object_kind=kind,
            track_id=tid,user_type=label,counted=counted,dominant_facility=assigned,observations=n,
            facility_frame_fractions=json.dumps(fractions,sort_keys=True),
            visited_facilities_provisional=';'.join(sorted(k for k in FACILITIES if fractions.get(k,0)>=.1)),
            midpoint_15min_bin=bin_start,identity_verified=0,zone_status='owner_marked_not_per_person_validated' if z else 'no_camera_zones',
            count_scope='source_file_unique_track_not_cross_file_unique_person'))
    for p in people:
        label={'BICYCLIST':'cyclist_or_motorcycle','PEDESTRIAN':'pedestrian'}.get(p['label'],'unscored_person')
        add('person',p['track_id'],label,int(p['counted']),person_samples[p['track_id']])
    for tid,samples in vehicles.items():
        label=Counter(r['label']for r in samples).most_common(1)[0][0]
        counted=int(samples[0]['counted']) if 'counted' in samples[0] else ''
        add('vehicle',tid,label,counted,samples)
    fields=['site','source','run','object_kind','track_id','user_type','counted','dominant_facility','observations','facility_frame_fractions','visited_facilities_provisional','midpoint_15min_bin','identity_verified','zone_status','count_scope']
    write(out/'per_track_lane_use.csv',rows,fields)
    groups=Counter((r['user_type'],r['dominant_facility'])for r in rows if r['counted']==1)
    agg=[dict(site=site,user_type=user,facility=lane,predicted_count=n)for (user,lane),n in sorted(groups.items())]
    write(out/'counts_by_user_lane.csv',agg,['site','user_type','facility','predicted_count'])
    bins=Counter((r['midpoint_15min_bin'],r['user_type'],r['dominant_facility'])for r in rows if r['counted']==1)
    br=[dict(site=site,bin_start=bin,user_type=user,facility=lane,predicted_count=n)for (bin,user,lane),n in sorted(bins.items())]
    write(out/'counts_15min_by_user_lane.csv',br,['site','bin_start','user_type','facility','predicted_count'])
    metadata=dict(site=site,source=log['video_path'],rows=len(rows),predicted_counts=log['final_counts'],
        zone_file=str(zones)if zones else None,vehicle_tracks_available=bool(log.get('vehicle_trajectories_csv')),
        limitation='Track midpoint allocates one count to one15-minute bin. Dominant lane requires70%of observed points. Separate visited facility memberships can overlap and must not be summed as unique people. Boundary jitter and ID switches remain. Cyclist model label includes possible motorcycles/e-scooters; no new mode accuracy claim. Original vehicle total kept even when no vehicle histories exist. No zones=>unassigned, not inferred facility. Counts reset per source.')
    (out/'summary.json').write_text(json.dumps(metadata,indent=2)+'\n');return dict(output=str(out),**metadata)

def merge(folders,out):
    """Stream source-level reports into a batch ledger; never deduplicate identities across sources."""
    out=Path(out);out.mkdir(parents=True,exist_ok=True);totals=Counter();bins=Counter();writer=None
    with (out/'all_tracks.csv').open('w',newline='')as f:
        for folder in folders:
            path=Path(folder)/'per_track_lane_use.csv'
            if not path.is_file():continue
            with path.open()as stream:
                reader=csv.DictReader(stream)
                if writer is None:writer=csv.DictWriter(f,fieldnames=reader.fieldnames);writer.writeheader()
                for row in reader:
                    writer.writerow(row)
                    if row['counted']=='1':
                        totals[(row['site'],row['user_type'],row['dominant_facility'])]+=1
                        bins[(row['site'],row['midpoint_15min_bin'],row['user_type'],row['dominant_facility'])]+=1
    write(out/'counts_by_site_user_lane.csv',[dict(site=site,user_type=user,facility=lane,predicted_count=n) for (site,user,lane),n in sorted(totals.items())],['site','user_type','facility','predicted_count'])
    write(out/'counts_15min_by_user_lane.csv',[dict(site=site,bin_start=bin,user_type=user,facility=lane,predicted_count=n) for (site,bin,user,lane),n in sorted(bins.items())],['site','bin_start','user_type','facility','predicted_count'])


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--run-log',type=Path,required=True)
    ap.add_argument('--zones',type=Path);ap.add_argument('--site',required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();print(json.dumps(report(a.run_log,a.out,a.zones,a.site),indent=2))
