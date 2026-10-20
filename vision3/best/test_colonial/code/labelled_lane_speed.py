#!/usr/bin/env python3
"""Provisional lane/motion analysis ONLY for the four truth-labelled clips.

No identity, zone alignment or metric speed is assumed validated. Physical
speed requires a same-camera, independently measured metric calibration.
"""
import argparse
from collections import Counter,defaultdict
import csv
import datetime as dt
import json
import math
from pathlib import Path
import re
import numpy as np
from eval_truth import CLIPS,read_truth,read_tracks,match,load_identity_map
from study_tables import read_xlsx,read_xml_xls


def inside(point,polygon):
    x,y=point;hit=False
    for i,(ax,ay)in enumerate(polygon):
        bx,by=polygon[(i+1)%len(polygon)]
        if abs((x-ax)*(by-ay)-(y-ay)*(bx-ax))<1e-7 and min(ax,bx)<=x<=max(ax,bx)and min(ay,by)<=y<=max(ay,by):return True
        if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:hit=not hit
    return hit


def zone_label(point,zones,size):
    if not(0<=point[0]<size[0]and 0<=point[1]<size[1]):return 'outside_frame'
    rw,rh=zones['ref_size'];p=(point[0]*rw/size[0],point[1]*rh/size[1])
    hits=[name for name in ('bike','sidewalk','road','grass')if zones.get(name)and inside(p,zones[name])]
    if len(hits)>1:return 'overlap'
    return {'bike':'bike_lane'}.get(hits[0],hits[0])if hits else 'unassigned'


def smooth(points,k):
    if len(points)<3:return np.array(points,float)
    k=min(int(k)|1,len(points)if len(points)%2 else len(points)-1)
    if k<3:return np.array(points,float)
    return np.column_stack([np.convolve(np.pad(np.asarray(points)[:,i],k//2,mode='edge'),np.ones(k)/k,mode='valid')for i in (0,1)])


def motion(samples,fps,H=None):
    if len(samples)<3:return dict(pixel_path_speed='',body_heights_per_s='',mph='',kmh='')
    points=np.array([[float(r['foot_x']),float(r['foot_y'])]for r in samples])
    sm=smooth(points,round(fps*.5));span=(int(samples[-1]['frame'])-int(samples[0]['frame']))/fps
    if span<=0:raise ValueError('Nonincreasing trajectory frames')
    path=float(np.linalg.norm(np.diff(sm,axis=0),axis=1).sum());height=np.mean([float(r['box_h'])for r in samples])
    result=dict(pixel_path_speed=round(path/span,3),body_heights_per_s=round(path/span/height,4)if height>0 else '',mph='',kmh='')
    if H is not None:
        raw=np.column_stack([points,np.ones(len(points))])@H.T
        if (np.abs(raw[:,2])<1e-8).any():raise ValueError('Trajectory reaches invalid homography horizon')
        xy=smooth(raw[:,:2]/raw[:,2,None],round(fps*.5))
        mps=float(np.linalg.norm(np.diff(xy,axis=0),axis=1).sum())/span
        result.update(mph=round(mps*2.2369362921,3),kmh=round(mps*3.6,3))
    return result


def load_calibration(path,size):
    import cv2
    c=json.loads(path.read_text())
    if c.get('site')!='Colonial North' or c.get('recording_date')!='2019-07-10' or c.get('units')!='metres':
        raise ValueError('Calibration must identify Colonial North, 2019-07-10 and metres')
    if not c.get('measurement_source') or not c.get('reviewer'):raise ValueError('Need independent measurement source and reviewer')
    image=np.asarray(c['image_points'],float);world=np.asarray(c['world_points_metres'],float)
    if image.shape!=world.shape or image.ndim!=2 or image.shape[1]!=2 or len(image)<4:raise ValueError('Need >=4 matching noncollinear image/metric points')
    ref=c['ref_size'];image=image*np.array([size[0]/ref[0],size[1]/ref[1]])
    if np.linalg.matrix_rank(np.column_stack([image,np.ones(len(image))]))<3 or np.linalg.matrix_rank(np.column_stack([world,np.ones(len(world))]))<3:
        raise ValueError('Calibration points must not be collinear')
    H,_=cv2.findHomography(image,world,0)
    if H is None or not np.isfinite(H).all():raise ValueError('Invalid calibration')
    return H


def speed_inventory(path):
    sheets=read_xlsx(path);result=[];colonial=[];records={}
    for name,rows in sheets.items():
        streets=set();streetcols=set()
        for row in rows:
            for cell,value in row.items():
                if value.strip().lower()=='street':streetcols.add(re.sub(r'\d','',cell))
                if 'colonial'in value.lower():colonial.append(dict(sheet=name,cell=cell,value=value))
        for row in rows:
            values={re.sub(r'\d','',k):v for k,v in row.items()}
            for cell,value in row.items():
                if re.sub(r'\d','',cell)in streetcols and value and value.lower()!='street':streets.add(value)
            if values.get('B','').strip().lower()=='colonial':
                try:
                    feet=float(values['F']);seconds=float(values['G']);mph=float(values['I'])
                    if feet<=0 or seconds<=0:continue
                except (KeyError,ValueError):continue
                key=(values.get('A'),values.get('D'),feet,seconds)
                record=records.setdefault(key,dict(record_number=values.get('A'),street='Colonial',
                    facility=values.get('D'),zone_length_feet=feet,seconds=seconds,source_mph=mph,
                    recomputed_mph=round(feet/seconds*3600/5280,6),
                    source_minus_recomputed_mph=round(mph-feet/seconds*3600/5280,6),
                    notes=values.get('K',''),source_cells=[]))
                if values.get('K'):record['notes']=values['K']
                record['source_cells'].append(name+'!'+next(iter(row)))
        result.append(dict(sheet=name,streets=sorted(streets),nonempty_rows=sum(any(v for v in row.values())for row in rows)))
    return dict(source=str(path),sheets=result,colonial_cells=colonial,unique_colonial_records=list(records.values()),
                conclusion='Colonial speed rows exist (35-ft bike-lane / 30-ft sidewalk zones), but no video timestamps or image gate endpoints are supplied. Record-to-person validation remains blocked. Source mph uses an approximate conversion; recomputation is a workbook arithmetic check, NOT model speed validation.')


def compare_speeds(people,references,links):
    people={(r['clip'],r['truth_id']):r for r in people}
    normalize=lambda s:s.lower().replace(' ','_')
    references={(str(r['record_number']),normalize(r['facility'])):r for r in references}
    used_people=set();used_records=set();pairs=[]
    with links.open(newline='')as stream:
        for link in csv.DictReader(stream):
            if not link.get('clip')or not link.get('truth_id'):continue
            if not link.get('reviewer')or not link.get('evidence'):raise ValueError('Study-to-person links require reviewer and evidence')
            pk=(link['clip'],link['truth_id']);rk=(str(link['record_number']),normalize(link['facility']))
            if pk in used_people or rk in used_records:raise ValueError('Study speed links must be one-to-one')
            if pk not in people or rk not in references:raise ValueError('Unknown person/reference in speed link')
            used_people.add(pk);used_records.add(rk);p=people[pk];ref=references[rk]
            status='READY'if p['identity_verified']and p['speed_mph']!=''else'BLOCKED_need_verified_identity_and_metric_speed'
            if p.get('metric_speed_facility')and normalize(p['metric_speed_facility'])!=rk[1]:raise ValueError('Speed-gate facility disagrees with reference')
            error=float(p['speed_mph'])-float(ref['source_mph'])if status=='READY'else''
            pairs.append(dict(clip=pk[0],truth_id=pk[1],record_number=rk[0],facility=rk[1],status=status,
                              model_mph=p['speed_mph'],study_mph=ref['source_mph'],error_mph=error,
                              reviewer=link['reviewer'],evidence=link['evidence']))
    usable=[r for r in pairs if r['status']=='READY'];n=len(usable)
    return pairs,dict(pairs=n,mae_mph=sum(abs(r['error_mph'])for r in usable)/n if n else None,
                      rmse_mph=math.sqrt(sum(r['error_mph']**2 for r in usable)/n)if n else None,
                      limitation='Human-matched same-person study comparison; small/development sample, no out-of-sample accuracy claim.')


def study_bins(path):
    sheets=read_xml_xls(path);rows=sheets['Bicycles'];channels=next(r for r in rows if r and r[0]=='Channel')
    bins=[r for r in rows if r and re.fullmatch(r'\d{1,2}:\d{2} [AP]M',r[0])]
    out={}
    for b,row in enumerate(bins):
        out[b]={name:sum(int(float(row[i]or 0))for i,ch in enumerate(channels)if i>0 and text in ch.lower()and i<len(row))for name,text in [('bike_lane','bike lane'),('sidewalk','sidewalk')]}
    return out


def write_csv(path,rows,columns=None):
    with path.open('w',newline='')as f:
        w=csv.DictWriter(f,fieldnames=columns or list(rows[0]));w.writeheader();w.writerows(rows)


def analyze(root,run,out,study_dir,zones_path,identity_path=None,calibration=None,speed_gates=None,record_links=None):
    root=root.resolve();out=out.resolve();study_dir=study_dir.resolve()
    out.mkdir(parents=True,exist_ok=False)
    zones=json.loads(zones_path.read_text());identity=load_identity_map(identity_path)if identity_path else {}
    result=[];reviews=[];comparisons=[]
    oldbins=study_bins(study_dir/'Colonial_North_676806_07-10-2019.xls')
    for clip,cc in CLIPS.items():
        prefix=f'Standard_SCU8OG_2019-07-10_0000.{cc["chunk"]:03d}'
        t0=dt.datetime.strptime(cc['start'],'%Y-%m-%d %H:%M:%S')
        truth,skipped=read_truth(root/cc['truth'])
        if skipped:raise ValueError(f'Incomplete truth {clip}')
        tracks=read_tracks(root/'counts'/run/(prefix+'_tracks.csv'),t0)
        temporal,_=match(truth,tracks)
        info=json.loads((root/'logs'/run/(prefix+'_run_log.json')).read_text());fps=info['fps'];size=info['resolution']
        H=load_calibration(calibration,size)if calibration else None
        approved=identity.get((run,clip),{})
        if approved:match(truth,tracks,approved)  # Validate all supplied IDs/overlaps before assigning verified status.
        trajectories=defaultdict(list)
        with(root/'counts'/run/(prefix+'_trajectories.csv')).open()as f:
            for row in csv.DictReader(f):
                if int(row.get('coasted','0')):continue
                when=dt.datetime.combine(t0.date(),dt.time.fromisoformat(row['time']))
                row['_s']=(when-t0).total_seconds();trajectories[row['track_id']].append(row)
        for person,status,candidate in temporal:
            tid=approved.get(person['id'],candidate['id']if candidate else '')
            track=next((t for t in tracks if t['id']==tid),None)
            samples=sorted([r for r in trajectories[tid]if person['s']<=r['_s']<=person['e']],key=lambda r:int(r['frame']))
            labels=Counter(zone_label((float(r['foot_x']),float(r['foot_y'])),zones,size)for r in samples)
            n=sum(labels.values());dominant,number=labels.most_common(1)[0]if n else ('no_observations',0)
            facility=dominant if n and number/n>=.7 and dominant not in ('overlap','unassigned','outside_frame')else 'uncertain'
            flags=[]
            if tid and track and (track['f']<person['s']-2 or track['l']>person['e']+3):flags.append('track_extends_outside_truth_window')
            for a,b in zip(samples,samples[1:]):
                elapsed=(int(b['frame'])-int(a['frame']))/fps
                jump=math.hypot(float(b['foot_x'])-float(a['foot_x']),float(b['foot_y'])-float(a['foot_y']))
                if elapsed<=.2 and jump/max(1,float(a['box_h']),float(b['box_h']))>2:flags.append('large_position_jump');break
            m=motion(samples,fps,H)
            metric_facility=''
            metric_status='estimated_from_supplied_calibration_not_speed_validated'if H is not None else 'BLOCKED_no_Colonial_metric_calibration'
            if speed_gates:
                from speed_gates import measure
                measured=measure(samples,fps,speed_gates,size);m.update(mph=measured['mph'],kmh=measured['kmh']);metric_status=measured['status'];metric_facility=measured.get('facility','')
            row=dict(clip=clip,truth_id=person['id'],truth_class=person['raw'],candidate_track_id=tid,
                     identity_verified=int(person['id']in approved),legacy_status=status,
                     lane_provisional=facility,dominant_zone_fraction=round(number/n,3)if n else '',observed_frames=n,
                     lane_frame_fractions=json.dumps({k:round(v/n,3)for k,v in labels.items()})if n else '{}',
                     image_speed_px_s=m['pixel_path_speed'],image_speed_body_heights_s=m['body_heights_per_s'],
                     speed_mph=m['mph'],speed_kmh=m['kmh'],metric_speed_facility=metric_facility,metric_speed_status=metric_status,
                     zone_status='PROVISIONAL_alignment_not_verified',identity_flags=';'.join(flags))
            result.append(row)
            reviews.append(dict(run=run,clip=clip,truth_id=person['id'],track_id=tid,decision='',full_track_reviewed='',reviewer='',evidence='',
                                truth_start_second=person['s'],truth_end_second=person['e'],identity_flags=';'.join(flags)))
        b=int((t0-dt.datetime(2019,7,10)).total_seconds()/900);old=oldbins[b]
        proposed=[r for r in result if r['clip']==clip and r['truth_class']=='cyclist']
        comparisons.append(dict(clip=clip,study_bike_lane=old['bike_lane'],study_sidewalk=old['sidewalk'],
            hand_truth_bicycles=len(proposed),hand_truth_motorcycles=sum(p['raw']=='motorcycle'for p in truth),
            provisional_bike_lane=sum(r['lane_provisional']=='bike_lane'for r in proposed),
            provisional_sidewalk=sum(r['lane_provisional']=='sidewalk'for r in proposed),
            provisional_road=sum(r['lane_provisional']=='road'for r in proposed),
            uncertain=sum(r['lane_provisional']=='uncertain'for r in proposed),
            validation='NOT_VALIDATED_independent_aggregate_counts_not_person_lane_truth'))
    write_csv(out/'people_lane_speed.csv',result);write_csv(out/'identity_review.csv',reviews);write_csv(out/'study_lane_comparison.csv',comparisons)
    inventory=speed_inventory(study_dir/'bicyclist speeds.xlsx')
    (out/'speed_reference_inventory.json').write_text(json.dumps(inventory,indent=2))
    refs=[{**r,'source_cells':';'.join(r['source_cells'])}for r in inventory['unique_colonial_records']]
    if refs:
        write_csv(out/'Colonial_study_speed_records.csv',refs)
        write_csv(out/'study_record_links.csv',[dict(record_number=r['record_number'],facility=r['facility'],clip='',truth_id='',reviewer='',evidence='')for r in refs])
    if record_links:
        pairs,metrics=compare_speeds(result,refs,record_links)
        if pairs:write_csv(out/'matched_speed_comparison.csv',pairs)
        (out/'matched_speed_metrics.json').write_text(json.dumps(metrics,indent=2))
    (out/'summary.json').write_text(json.dumps(dict(truth_rows=len(result),image_motion_rows=sum(r['image_speed_px_s']!=''for r in result),
        identity_verified_rows=sum(r['identity_verified']for r in result),provisional_lanes=dict(Counter(r['lane_provisional']for r in result)),
        metric_speed_rows=sum(r['speed_mph']!=''for r in result),unique_Colonial_speed_references=len(refs),
        zone_alignment_validated=False,matched_speed_validation=bool(record_links and metrics['pairs'])),indent=2))
    lines=['# Labelled-clips lane and speed analysis','',f'{len(result)} truth rows only; run {run}.',
      'Candidate track IDs come from legacy time matching unless explicitly human-approved. They are NOT verified person identities.',
      'Lane proposals use observed bottom-centre points only, restricted to each truth encounter; coasted frames excluded.',
      'Overlapping polygons are marked uncertain. Lane polygons / inferred reference scale still require visual alignment checking.',
      'Road/bike-lane/sidewalk/grass are examined separately. Do not treat the old bike-vs-sidewalk-only facility field as road truth.',
      'Motorcycles remain separate in this report; the older detection score groups them with cyclists.',
      'Image speed = smoothed path length / elapsed seconds / mean box height. Not mph. Restricted-window values can differ from whole-track pipeline values.',
      'Physical speed is blank without measured Colonial metric calibration; no fixed human height or other-street mean is substituted.',
      inventory['conclusion'],
      'The study count workbook supplies aggregate lane counts; it cannot verify which specific video person used a lane.',
      ('Lane accuracy is not claimed. See matched_speed_metrics.json for explicitly matched speed pairs.'if record_links else 'No lane or physical-speed accuracy statistic is claimed.'),'',
      '| Clip | Truth ID | Raw class | Candidate ID | Proposed lane | Image speed (heights/s) |',
      '|---|---|---|---|---|---|']
    lines += [f'| {r["clip"]} | {r["truth_id"]} | {r["truth_class"]} | {r["candidate_track_id"]} | {r["lane_provisional"]} | {r["image_speed_body_heights_s"]} |'for r in result]
    lines += ['','Next: confirm complete candidate tracks in identity_review.csv (approved + full_track_reviewed=yes + reviewer + evidence), check zone overlays, and supply independently measured Colonial calibration for mph.',
              'After identity review: python code/eval_truth.py --root . --runs '+run+' --require-identity --identity-map '+str(out/'identity_review.csv')+' --out '+str(out/'identity_evaluation.md')]
    (out/'RESULTS.md').write_text('\n'.join(lines)+'\n')
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--run',default='b4_combo_static5')
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--study-dir',type=Path,required=True)
    ap.add_argument('--zones',type=Path);ap.add_argument('--identity-map',type=Path);ap.add_argument('--calibration',type=Path);ap.add_argument('--speed-gates',type=Path);ap.add_argument('--record-links',type=Path)
    a=ap.parse_args();analyze(a.root,a.run,a.out,a.study_dir,a.zones or a.root/'zones/colonial_north_v2.json',a.identity_map,a.calibration,a.speed_gates,a.record_links)


if __name__=='__main__':main()
