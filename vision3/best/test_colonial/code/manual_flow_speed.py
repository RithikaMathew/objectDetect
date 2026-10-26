#!/usr/bin/env python3
"""First-click-seeded optical flow, checked against held-out clicks; no detector rerun."""
import argparse
from collections import defaultdict
import csv
import json
import math
from pathlib import Path
import statistics
import cv2
import numpy as np
from analyze_manual_bicycles import project,write_csv
from metric_trajectory_speed import estimate


def endpoint_speed(points,calibration):
    if len(points)<2 or not calibration or not calibration.get('geometry_check_passed'):return ''
    seconds=points[-1]['seconds']-points[0]['seconds']
    if seconds<1.5:return ''
    try:
        a,b=project(calibration['H'],points[0]),project(calibration['H'],points[-1])
        if a[2]*b[2]<=0:return ''
        return math.hypot(b[0]-a[0],b[1]-a[1])/seconds*2.2369362921
    except (KeyError,ValueError,TypeError):return ''


def patch_features(gray,point,radius=35):
    x,y=map(float,point);mask=np.zeros_like(gray)
    # Prefer the wheel/body above the clicked contact point; never use future clicks.
    x0,x1=max(0,int(x-radius)),min(gray.shape[1],int(x+radius+1))
    y0,y1=max(0,int(y-radius*1.7)),min(gray.shape[0],int(y+8))
    if x1<=x0 or y1<=y0:return None
    mask[y0:y1,x0:x1]=255
    return cv2.goodFeaturesToTrack(gray,maxCorners=50,qualityLevel=.02,minDistance=4,mask=mask,blockSize=5)


def flow_step(previous,current,features,point,fb_limit=1.5,max_step=80):
    if features is None or len(features)<3:return None,None,'insufficient_features'
    lk=dict(winSize=(25,25),maxLevel=3,criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,30,.01))
    nxt,ok,_=cv2.calcOpticalFlowPyrLK(previous,current,features,None,**lk)
    if nxt is None:return None,None,'forward_flow_failed'
    back,back_ok,_=cv2.calcOpticalFlowPyrLK(current,previous,nxt,None,**lk)
    if back is None:return None,None,'backward_flow_failed'
    a=features.reshape(-1,2);b=nxt.reshape(-1,2)
    valid=(ok.ravel()>0)&(back_ok.ravel()>0)&np.isfinite(b).all(axis=1)&(np.linalg.norm(back.reshape(-1,2)-a,axis=1)<=fb_limit)
    if valid.sum()<3:return None,None,'forward_backward_check_failed'
    delta=b[valid]-a[valid];median=np.median(delta,axis=0)
    coherent=np.linalg.norm(delta-median,axis=1)<=max(2.5,.25*float(np.linalg.norm(median)))
    if coherent.sum()<3:return None,None,'incoherent_patch_motion'
    move=np.median(delta[coherent],axis=0)
    if np.linalg.norm(move)>max_step:return None,None,'implausible_frame_jump'
    new=np.asarray(point)+move
    if not 0<=new[0]<current.shape[1] or not 0<=new[1]<current.shape[0]:return None,None,'point_left_image'
    return new,b[valid][coherent].reshape(-1,1,2).astype(np.float32),'ok'


def track(video,points,output,make_video=False):
    cap=cv2.VideoCapture(str(video));writer=None
    try:
        fps=cap.get(cv2.CAP_PROP_FPS);width=int(cap.get(3));height=int(cap.get(4))
        if not cap.isOpened() or fps<=0:raise ValueError('Video unreadable')
        if any(int(p['width'])!=width or int(p['height'])!=height for p in points):raise ValueError('Annotation/video image dimensions differ')
        first=round(points[0]['seconds']*fps);last=round(points[-1]['seconds']*fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES,first);ok,frame=cap.read()
        if not ok:raise ValueError('Seed frame unreadable')
        point=np.array([points[0]['x'],points[0]['y']],dtype=float);gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY);features=patch_features(gray,point)
        samples=[dict(frame=first,seconds=first/fps,foot_x=float(point[0]),foot_y=float(point[1]),coasted=0)]
        status='complete'
        if make_video:
            writer=cv2.VideoWriter(str(output),cv2.VideoWriter_fourcc(*'mp4v'),fps,(width,height))
            if not writer.isOpened():raise ValueError('Review video writer failed')
        for index in range(first+1,last+1):
            ok,frame=cap.read()
            if not ok:status='video_ended';break
            current=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            point,features,reason=flow_step(gray,current,features,point)
            if point is None:status=reason;break
            gray=current
            samples.append(dict(frame=index,seconds=index/fps,foot_x=float(point[0]),foot_y=float(point[1]),coasted=0))
            if len(features)<12:features=patch_features(gray,point)
            if writer:
                xy=np.array([[round(r['foot_x']),round(r['foot_y'])] for r in samples],np.int32)
                cv2.polylines(frame,[xy],False,(0,255,255),2);cv2.circle(frame,tuple(xy[-1]),6,(0,0,255),2)
                cv2.putText(frame,'OPTICAL FLOW: verify cyclist identity',(10,25),cv2.FONT_HERSHEY_SIMPLEX,.55,(0,255,255),2)
                writer.write(frame)
        return samples,dict(fps=fps,width=width,height=height,tracking_stop=status,requested_first_frame=first,requested_last_frame=last)
    finally:
        cap.release()
        if writer:writer.release()


def check_drift(samples,points,fps,max_error=20):
    by_frame={r['frame']:r for r in samples};checks=[]
    for p in points[1:]:
        frame=round(p['seconds']*fps);r=by_frame.get(frame)
        error=math.hypot(r['foot_x']-p['x'],r['foot_y']-p['y']) if r else None
        checks.append(dict(seconds=p['seconds'],frame=frame,error_px=error))
    measured=[r['error_px'] for r in checks if r['error_px'] is not None]
    accepted=bool(checks) and len(measured)==len(checks) and max(measured)<=max_error
    return accepted,checks


def run(manual,videos,out,max_error=20,make_videos=False,limit=None):
    out.mkdir(parents=True,exist_ok=False)
    pack=json.loads((manual/'analysis/review_inputs.json').read_text());entries={e['key']:e for e in pack['entries']}
    data=json.loads((manual/'analysis/normalized_observations.json').read_text());groups=defaultdict(list)
    for p in data['observations']:groups[p['encounter_id']].append(p)
    original={r['encounter_id']:r for r in data['encounters']};rows=[];trajectories=[];audits=[]
    for number,(encounter,points) in enumerate(sorted(groups.items())):
        if limit is not None and number>=limit:break
        points.sort(key=lambda p:p['seconds']);key=points[0]['key'];entry=entries[key];cal=entry.get('calibration');saved=original[encounter]
        row=dict(encounter_id=encounter,location=saved['location'],bin_start=entry['reference']['start'],manual_start=saved['start'],manual_end=saved['end'],manual_path_mean_mph=saved['speed_mph'],manual_endpoint_mean_mph=endpoint_speed(points,cal),optical_flow_median_mph='',optical_flow_diagnostic_mph='',status='',heldout_clicks=0,max_drift_px='',tracking_stop='',video=str(videos/entry['video']),scale_validation='same_learned_scale_not_independent_validation')
        try:
            video=videos/entry['video']
            if not video.is_file():raise FileNotFoundError('Missing local review video: '+str(video))
            samples,info=track(video,points,out/(encounter+'_flow.mp4'),make_videos)
            passed,checks=check_drift(samples,points,info['fps'],max_error)
            errors=[r['error_px'] for r in checks if r['error_px'] is not None]
            row.update(heldout_clicks=len(errors),max_drift_px=max(errors) if errors else '',tracking_stop=info['tracking_stop'])
            diagnostic=''
            if cal and cal.get('geometry_check_passed'):
                # Same exploratory extension beyond car support as the existing manual result.
                hull=np.array([[[0,0]],[[info['width']-1,0]],[[info['width']-1,info['height']-1]],[[0,info['height']-1]]],np.float32)
                projected=[project(cal['H'],dict(x=r['foot_x'],y=r['foot_y'])) for r in samples]
                if min(p[2] for p in projected)<0<max(p[2] for p in projected):raise ValueError('Flow crosses calibration horizon')
                diagnostic=estimate(samples,info['fps'],np.array(cal['H']),hull)['speed_mph']
            row['optical_flow_diagnostic_mph']=diagnostic
            row['status']='DRIFT_OR_COVERAGE_CHECK_FAILED' if not passed else 'NO_USABLE_METRIC_SPAN' if diagnostic=='' else 'PROVISIONAL_PASSED_PIXEL_CHECK_NOT_SPEED_VALIDATED'
            if passed and diagnostic!='':row['optical_flow_median_mph']=diagnostic
            trajectories.extend(dict(encounter_id=encounter,**r) for r in samples)
            audits.append(dict(encounter_id=encounter,metadata=info,heldout_click_checks=checks))
        except Exception as exc:row['status']='FAILED: '+str(exc)
        rows.append(row);write_csv(out/'comparison.csv',rows)
        (out/'status.json').write_text(json.dumps(dict(completed=len(rows),requested=min(len(groups),limit) if limit is not None else len(groups),latest_encounter=encounter,latest_status=row['status']),indent=2)+'\n')
        print(encounter,row['status'],flush=True)
    write_csv(out/'flow_trajectories.csv',trajectories);(out/'drift_checks.json').write_text(json.dumps(audits,indent=2)+'\n')
    sites=[]
    for location in sorted({r['location'] for r in rows}):
        rr=[r for r in rows if r['location']==location]
        values=lambda k:[float(r[k]) for r in rr if r[k]!='']
        mean=lambda k:statistics.mean(values(k)) if values(k) else ''
        sites.append(dict(location=location,annotated_encounters=len(rr),manual_path_sample=len(values('manual_path_mean_mph')),manual_path_mean_mph=mean('manual_path_mean_mph'),manual_endpoint_sample=len(values('manual_endpoint_mean_mph')),manual_endpoint_mean_mph=mean('manual_endpoint_mean_mph'),flow_accepted_sample=len(values('optical_flow_median_mph')),flow_mean_mph=mean('optical_flow_median_mph'),flow_failed_or_unusable=sum(r['optical_flow_median_mph']=='' for r in rr)))
    write_csv(out/'site_summary.csv',sites)
    with (manual/'analysis/site_summary.csv').open() as f:baseline={r['location']:r for r in csv.DictReader(f)}
    lines=['# Manual-seeded optical flow and endpoint comparison','','Only the first click seeds flow. Later clicks are held out to measure pixel drift; they never steer/reseed the tracker. Pyramidal Lucas–Kanade tracks a patch of wheel/body features; median coherent displacement moves the contact-point estimate. This can follow background or wheel rotation instead of the cyclist, hence drift checks and review.','',f'Provisional acceptance requires every later click to be reached with error <= {max_error}px. This is an engineering diagnostic threshold, not a calibrated speed-accuracy guarantee. Failed tracking speeds remain diagnostic-only and are excluded from accepted flow means.','', 'Endpoint mph uses the first-to-last calibrated straight-line distance/time, not a known measured gate distance; it also requires at least1.5seconds to match the existing manual time safeguard. Manual path mph uses successive clicked distances/time; optical flow mph uses median local velocity windows like the automatic estimator. All share learned metric scale and are not independent ground-truth measurements. Sample/time windows may differ; do not call their differences speed accuracy.','', '| Location | Validation mph | HiPerGator mph | Manual path mph | Endpoint mph | Accepted flow mph | Flow accepted / attempted |','|---|---:|---|---:|---:|---:|---|']
    fmt=lambda x:'Unavailable' if x=='' else f'{x:.2f}'
    for r in sites:
        base=baseline.get(r['location'],{});a=base.get('automatic_mean_mph','')
        automatic=fmt(float(a)) if a!='' else 'Interrupted' if base.get('automatic_state') in ('STARTED','NODE_FAIL') else 'No accepted speed'
        study=base.get('study_speed_mean_mph','');study=fmt(float(study)) if study!='' else 'Unavailable'
        lines.append(f"| {r['location']} | {study} | {automatic} | {fmt(r['manual_path_mean_mph'])} | {fmt(r['manual_endpoint_mean_mph'])} | {fmt(r['flow_mean_mph'])} | {r['flow_accepted_sample']}/{r['annotated_encounters']} |")
    lines+=['','Main count/time comparison: [../README.md](../README.md). HiPerGator and study means are reference context copied from the main analysis; they may use different people and intervals than the manually seeded experiments. Optical flow reads only the short annotated encounter spans, not the entire15-minute clips.','', 'See comparison.csv for per-encounter status and diagnostic speeds; drift_checks.json records each held-out pixel error; flow_trajectories.csv contains predicted points. Optional *_flow.mp4 are review overlays, not confirmed identities. Missing videos are explicit failures, not zero speeds. Source timestamps are rounded to the nearest decoded frame; browser click times were approximate.','', '[Optical-flow reference: OpenCV Lucas–Kanade documentation](https://docs.opencv.org/4.x/d4/dee/tutorial_optical_flow.html). Calibration provenance remains the ICCV2021 author-model adapter documented in the manual README.','']
    (out/'RESULTS.md').write_text('\n'.join(lines))
    (out/'status.json').write_text(json.dumps(dict(state='FINISHED',completed=len(rows),accepted_flow_speeds=sum(r['optical_flow_median_mph']!='' for r in rows),policy='failed pixel/coverage checks excluded; shared scale not independently validated'),indent=2)+'\n')
    return rows

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manual',type=Path,default=Path(__file__).resolve().parents[4]/'manual');p.add_argument('--videos',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--max-error-px',type=float,default=20);p.add_argument('--review-videos',action='store_true');p.add_argument('--limit',type=int);a=p.parse_args()
    if a.max_error_px<=0 or (a.limit is not None and a.limit<1):p.error('Positive drift threshold and limit required')
    run(a.manual,a.videos,a.out,a.max_error_px,a.review_videos,a.limit)
