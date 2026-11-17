#!/usr/bin/env python3
"""Versioned, video-only near-miss diagnostics and offline manual validation.

No GPU, new inference, physical calibration, or source-file writes.
"""
from __future__ import annotations
import argparse
import base64
import copy
import csv
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'pipeline'))
from generate_near_miss_report import load_task, read, write, digest, BATCH, FINAL, serial
from clearance_metrics import local_motion, project, dimensions
from manual_occlusion_metrics import manual_samples, with_velocity, interpolate_method, observed_method, filtered_method, metrics_for

VERSION='20261110_v1'
EVENTS=[('white_suv','cyclist_pass','colonial_124020','9'),('dark_car','cyclist_pass','colonial_125350','18'),('pedestrian_car','pedestrian_crossing','colonial_1708_pedestrian_car','68')]
SOURCES=[dict(title='FHWA-HRT-08-051, Chapter 2 (2008)',url='https://www.fhwa.dot.gov/publications/research/safety/08051/02.cfm',verified='2026-11-10',supports='SSAM vehicle-to-vehicle simulation context; configurable default TTC 1.5 s'),dict(title='FHWA-HRT-10-038, Chapter 3 (2010)',url='https://www.fhwa.dot.gov/publications/research/safety/10038/003.cfm',verified='2026-11-10',supports='This SSAM vehicle-simulation application uses TTC <=1.5 s / PET <=5.0 s; not cyclist/pedestrian ground truth')]
CONFIG=dict(adopted_ttc_s=None,adopted_pet_s=None,physical_clearance_m=None,proposed_literature_context=dict(ttc_s=1.5,pet_s=5.0,context='SSAM vehicle simulation defaults only; opt-in exploratory comparison after metric eligibility; not validated here'),sweep_ttc_s=[.25,.375,.5,1.,1.5,2.],sweep_pet_s=[.25,.5,1.,1.5,5.],comparison='strict less-than; differs from <= in cited SSAM application',policy='Screens never change review labels; missing metrics never become zero')

def pts_for(path):
    proc=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time:stream=width,height','-of','json',str(path)],capture_output=True,text=True,check=True)
    probe=json.loads(proc.stdout)
    if not probe.get('streams') or any((s.get('width'),s.get('height'))!=(720,480) for s in probe['streams']):raise ValueError('Viewer expects original 720x480 source geometry: '+str(path))
    values=[float(r['best_effort_timestamp_time']) for r in probe['frames']]
    if not values or not all(math.isfinite(v) for v in values) or any(b<=a for a,b in zip(values,values[1:])):raise ValueError('Frame PTS must be present, finite and strictly increasing: '+str(path))
    return np.array(values)-values[0]

def longest_missing(present,lo,hi,pts):
    missing=[i for i in range(lo,hi+1) if i not in present];runs=[]
    for f in missing:
        if runs and f==runs[-1][-1]+1:runs[-1].append(f)
        else:runs.append([f])
    if not runs:return 0,0.,[]
    dt=float(np.median(np.diff(pts)));best=max(runs,key=len)
    return len(best),float(pts[best[-1]-1]-pts[best[0]-1]+dt),[dict(first_frame=r[0],last_frame=r[-1],missing_frames=len(r),duration_s=float(pts[r[-1]-1]-pts[r[0]-1]+dt)) for r in runs]

def polygon_valid(points):
    if not isinstance(points,list) or len(points)<3:return False
    if any(not isinstance(p,list) or len(p)!=2 or any(not isinstance(v,(float,int)) or not math.isfinite(v) or v<0 for v in p) or p[0]>720 or p[1]>480 for p in points):return False
    return abs(sum(p[0]*points[(i+1)%len(points)][1]-points[(i+1)%len(points)][0]*p[1] for i,p in enumerate(points)))>1

def reviewed_pet(event,annotation):
    result=dict(pet_s=None,pet_lower_s=None,pet_upper_s=None,signed_time_difference_lower_s=None,signed_time_difference_upper_s=None,pet_units='s',pet_eligibility='not_observable',pet_reason='Shared physical conflict zone and supported occupancy boundaries not yet annotated')
    if event['event_type']!='pedestrian_crossing':return {**result,'pet_eligibility':'not_applicable','pet_reason':'Parallel passing has no established shared physical occupancy region'}
    z=annotation.get('zone',{});o=annotation.get('occupancy',{})
    if not polygon_valid(z.get('points')) or z.get('physical_identity_confirmed') is not True or not z.get('justification','').strip() or not annotation.get('reviewer','').strip():return result
    p,c=o.get('pedestrian_exit'),o.get('car_entry')
    if not p or not c:return result
    for q in (p,c):
        lo,hi=q.get('frame_low'),q.get('frame_high')
        if q.get('boundary_supported') is not True or q.get('visibility') not in ('visible','occluded','uncertain') or type(lo) is not int or type(hi) is not int or not 1<=lo<=hi<=len(event['pts']):return {**result,'pet_reason':'Invalid or unsupported boundary bracket; verify neighboring frames and visibility'}
        if q['visibility']!='visible' and not q.get('notes','').strip():return {**result,'pet_reason':'Occluded/uncertain boundary needs explicit evidence bounding its interval'}
    def interval(q):
        low,high=event['pts'][q['frame_low']-1],event['pts'][q['frame_high']-1]
        if q['frame_low']==q['frame_high']:low,high=max(0,low-event['frame_interval_s']/2),high+event['frame_interval_s']/2
        return low,high
    pl,ph=interval(p);cl,ch=interval(c);low,high=cl-ph,ch-pl
    result.update(signed_time_difference_lower_s=low,signed_time_difference_upper_s=high)
    if high<0:return {**result,'pet_eligibility':'temporal_overlap','pet_reason':'Car entry precedes pedestrian exit under supported brackets; negative difference is overlap, not positive PET'}
    if low<0:return {**result,'pet_eligibility':'order_uncertain','pet_reason':'Boundary brackets allow both occupancy overlap and sequential occupancy; PET is N/A'}
    return {**result,'pet_lower_s':low,'pet_upper_s':high,'pet_eligibility':'supported_interval','pet_reason':'Reviewer-supported physical-zone occupancy brackets; frame quantization retained; not independently validated adjudication'}

def validate_annotations(data,events):
    if data.get('schema_version')!=1 or not isinstance(data.get('events'),list):raise ValueError('Expected annotation schema_version 1 and events array')
    known={e['event_id']:e for e in events};seen=set()
    for a in data['events']:
        e=known.get(a.get('event_id'))
        if not e or a['event_id'] in seen:raise ValueError('Unknown or duplicate event ID')
        seen.add(a['event_id'])
        if not isinstance(a.get('edges',[]),list) or not isinstance(a.get('footprints',[]),list) or not isinstance(a.get('occupancy',{}),dict) or not isinstance(a.get('zone',{}),dict):raise ValueError('Invalid annotation collection types')
        if not isinstance(a.get('reviewer',''),str) or not isinstance(a.get('notes',''),str):raise ValueError('Reviewer and notes must be text')
        for footprint in a.get('footprints',[]):
            if type(footprint.get('frame')) is not int or not 1<=footprint['frame']<=len(e['pts']) or not polygon_valid(footprint.get('points')):raise ValueError('Invalid footprint polygon/frame')
        if a.get('source_sha256')!=e['source_sha256']:raise ValueError('Source video hash mismatch')
        frames=set()
        for r in a.get('edges',[]):
            if type(r.get('frame')) is not int or not 1<=r['frame']<=len(e['pts']) or r['frame'] in frames:raise ValueError('Invalid or duplicate edge frame')
            frames.add(r['frame'])
            if any(type(r.get(k)) not in (int,float) or not math.isfinite(r[k]) or not 0<=r[k]<=720 for k in ('cyclist_x_px','car_x_px')):raise ValueError('Invalid edge coordinate')
        if a.get('zone',{}).get('points') and not polygon_valid(a['zone']['points']):raise ValueError('Conflict zone must be a non-degenerate image polygon')
    return data

def edge_minimum(a):
    rows=[r for r in a.get('edges',[]) if r.get('visibility')=='visible' and all(isinstance(r.get(k),(int,float)) and math.isfinite(r[k]) for k in ('cyclist_x_px','car_x_px'))]
    best=min(rows,key=lambda r:abs(r['cyclist_x_px']-r['car_x_px'])) if rows else None
    return dict(selected_min_edge_gap_px=abs(best['cyclist_x_px']-best['car_x_px']) if best else None,selected_min_edge_gap_frame=best['frame'] if best else None,edge_eligible_count=len(rows))

def json_write(path,value):Path(path).write_text(json.dumps(value,default=serial,indent=2,allow_nan=False)+'\n')
def norm_path(path,root):return str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
def plain_sample(r,pts):
    return dict(frame=r['frame'],t_s=float(pts[r['frame']-1]),x_px=float(r['pixel'][0]),y_px=float(r['pixel'][1]),box_w_px=r['box_w'],box_h_px=r['box_h'],status='automatic_observed_contact_proxy',inside_saved_support=bool(r['inside']))

def fit_velocity(rr,pts):
    if len(rr)<3:return None
    times=np.array([pts[r['frame']-1] for r in rr]);points=np.array([r['pixel'] for r in rr]);return np.polyfit(times-times.mean(),points,1)[0]

def make_events(repo):
    previous=repo/'reports/near_miss';old={e['event_id']:e for e in read(previous/'event_metrics.csv')};edges=read(repo/'clearance_edge_annotations_completed.csv');manual=read(repo/'manual_occlusion_points.csv')
    frame_gate=read(previous/'frame_eligibility.csv');models=read(previous/'reconstruction_inputs.csv')
    events=[];defaults=[];coverage=[];timing=[];provenance=[]
    for eid,kind,clip,vid in EVENTS:
        ped=kind=='pedestrian_crossing';task=previous/'inputs/pedestrian' if ped else repo/BATCH/(clip+'_reference')
        video=previous/'inputs'/(clip+'.mp4') if ped else repo/BATCH/'inputs'/(clip+'.mp4')
        # Refuse fake placeholders; assets must exist before embedding/measurement.
        if not video.is_file():raise FileNotFoundError(f'Missing original video asset: {video}')
        pts=pts_for(video);dt=float(np.median(np.diff(pts)));g,log,paths=load_task(task)
        subject=paths[('pedestrian' if ped else 'cyclist','1')]
        if ped:
            _,_,vp=load_task(previous/'inputs/pedestrian_sensitive');car=vp[('car',vid)]
        else:car=paths[('car',vid)]
        if any(r['frame']<1 or r['frame']>len(pts) for r in subject+car):raise ValueError('Trajectory frame outside decoded PTS')
        manual_rows=[dict(frame=int(r['frame']),t_s=float(pts[int(r['frame'])-1]),object=r['object'],x_px=float(r['x_px']),y_px=float(r['y_px']),status='manual_contact_proxy_visibility_unverified',original_click_time_s=float(r['clip_seconds']),source='manual_occlusion_points.csv') for r in manual] if ped else []
        annotation_edges=[dict(frame=int(r['frame_zero_based'])+1,original_frame_zero_based=int(r['frame_zero_based']),original_clip_seconds=float(r['clip_seconds']),t_s=float(pts[int(r['frame_zero_based'])]),cyclist_x_px=float(r['cyclistEdge']),car_x_px=float(r['carEdge']),visibility='visible',uncertainty_px=None,method='existing_manual_horizontal_x_only',reviewer=r['reviewer'],notes=r['notes'],source='clearance_edge_annotations_completed.csv') for r in edges if r['clip']==clip and r['usable']=='yes']
        lo,hi=(min(r['frame'] for r in manual_rows if r['object']=='car'),max(r['frame'] for r in manual_rows if r['object']=='car')) if ped else (car[0]['frame'],car[-1]['frame'])
        aa={r['frame']:r for r in subject if lo<=r['frame']<=hi};bb={r['frame']:r for r in car if lo<=r['frame']<=hi};common=sorted(aa.keys()&bb.keys());expected=hi-lo+1
        closest=min(common,key=lambda f:np.linalg.norm(aa[f]['pixel']-bb[f]['pixel'])) if common else None
        proxy_distance=float(np.linalg.norm(aa[closest]['pixel']-bb[closest]['pixel'])) if closest else None
        vv=None;along=None;image_axis=None
        if len(common)>=3:
            times=np.array([pts[f-1] for f in common]);ap=np.array([aa[f]['pixel'] for f in common]);bp=np.array([bb[f]['pixel'] for f in common]);rv=np.polyfit(times-times.mean(),bp-ap,1)[0];vv=float(np.linalg.norm(rv))
            disp=ap[-1]-ap[0]
            if np.linalg.norm(disp)>0:image_axis=disp/np.linalg.norm(disp);along=float(rv@image_axis)
        sub_missing,sub_gap,sub_spans=longest_missing(set(aa),lo,hi,pts);car_missing,car_gap,car_spans=longest_missing(set(bb),lo,hi,pts)
        manualcar={r['frame'] for r in manual_rows if r['object']=='car' and lo<=r['frame']<=hi};manualsub={r['frame'] for r in manual_rows if r['object']=='pedestrian' and lo<=r['frame']<=hi}
        recon=[r for r in models if r['method']=='constant_velocity'] if ped else []
        recon_count=sum(lo<=int(r['frame'])<=hi for r in recon)
        # Conditional benchmark remains from saved model. New PTS-based fit below is separate.
        metric=dict(event_id=eid,event_type=kind,nominal_timestamp=old[eid]['start_time'],absolute_clock_status='unresolved_burned_in_vs_manifest; no fixed correction',analysis_first_frame=lo,analysis_last_frame=hi,analysis_start_pts_s=float(pts[lo-1]),analysis_end_pts_s=float(pts[hi-1]),frame_index_units='one-based decoded frame',object_ids=old[eid]['object_ids'],source_video=norm_path(video,repo),subject_namespace='reference',car_namespace='sensitive' if ped else 'reference',
            expected_frame_count=expected,subject_observed_count=len(aa),car_observed_count=len(bb),synchronized_observed_count=len(common),synchronized_observed_pct=100*len(common)/expected,subject_observed_pct=100*len(aa)/expected,car_observed_pct=100*len(bb)/expected,manual_subject_count=len(manualsub),manual_subject_pct=100*len(manualsub)/expected,manual_edge_count=len(annotation_edges),manual_edge_pct=100*len(annotation_edges)/expected,manual_car_count=len(manualcar),manual_car_pct=100*len(manualcar)/expected,reconstructed_car_count=recon_count,reconstructed_car_pct=100*recon_count/expected,verified_visible_frame_count=None,verified_visible_reason='No exhaustive visibility annotation; detected/manual/model counts overlap and are not a partition',
            subject_longest_missing_frames=sub_missing,subject_longest_missing_s=sub_gap,car_longest_missing_frames=car_missing,car_longest_missing_s=car_gap,car_last_observed_frame=car[-1]['frame'],car_last_observed_pts_s=float(pts[car[-1]['frame']-1]),tracking_loss_reason=('automatic track missing during visually documented occlusion; hidden-contact interval not directly observed' if ped else 'local missing observations; cause unverified, geometric rejection is separate' if car_missing else 'no missing vehicle observations inside defined analysis window'),
            estimated_speed=float(old[eid]['estimated_speed']) if old[eid]['estimated_speed'] else None,speed_units=old[eid]['speed_units'] or 'N/A; unvalidated physical scale',relative_image_velocity_px_s=vv,relative_along_image_axis_px_s=along,relative_velocity_units='px/s; fitted over synchronized frames in analysis window; image axis follows subject displacement',image_proxy_distance_px=proxy_distance,image_proxy_frame=closest,image_proxy_pts_s=float(pts[closest-1]) if closest else None,image_proxy_method='Euclidean synchronized detector bottom-centres; not actual edges',
            historical_conditional_ttc_s=float(old[eid]['reproduced_surrogate_ttc_s']) if old[eid]['reproduced_surrogate_ttc_s'] else None,conditional_ttc_s=None,conditional_ttc_units='s',conditional_ttc_eligibility='not_applicable_parallel_pass' if not ped else 'conditional_unvalidated_learned_plane',physical_ttc_s=None,conditional_ttc_assumptions='N/A for same-direction pass; no justified image collision model' if not ped else 'CV fitted manual car + automatic pedestrian; assumed fixed road-axis rectangles; 5 s horizon; existing learned mapping unvalidated',
            physical_clearance_m=None,physical_clearance_units='m',clearance_eligibility='not_calibrated_lateral_scale_or_physical_edges',review_label=old[eid]['reviewed_classification'],visual_relationship='reviewed_pass' if not ped else 'reviewed_close_crossing',evasive_action='unknown',confirmed_under_protocol=False,screening_flag='visual_review_candidate_only',provenance=f'{norm_path(task,repo)}; original annotations; reports/near_miss benchmark outputs')
        annotation=dict(event_id=eid,source_sha256=digest(video),reviewer='',notes='',evasive_action='unknown',edges=annotation_edges,zone=dict(points=[],physical_identity_confirmed=False,justification=''),occupancy={},footprints=[])
        gates=[r for r in frame_gate if r['event_id']==eid]
        footprints={};cm=local_motion(subject,.5);vm=local_motion(car,.5);axis=np.array(g['road_axis']);basis=np.column_stack((axis,[-axis[1],axis[0]]));inv=np.linalg.inv(g['H'])
        if not ped:
            for f in sorted(cm.keys()&vm.keys()):
                polys=[]
                for r,dim in [(cm[f],dimensions('cyclist',.8)),(vm[f],dimensions('car',.8))]:
                    offsets=np.array([[-1,-1],[1,-1],[1,1],[-1,1]])*np.array(dim)/2
                    world=r['xy']+offsets@basis.T;polys.append(project(inv,world).tolist())
                footprints[str(f)]=polys
        model_pixels=[]
        for r in recon:
            xy=project(inv,[[float(r['car_x_unvalidated']),float(r['car_y_unvalidated'])]])[0]
            model_pixels.append(dict(frame=int(r['frame']),t_s=float(pts[int(r['frame'])-1]),x_px=xy[0],y_px=xy[1],status=r['observation_status']))
        event=dict(event_id=eid,event_type=kind,clip_id=clip,source_video=norm_path(video,repo),source_sha256=annotation['source_sha256'],pts=pts.tolist(),frame_interval_s=dt,initial_frame=1405 if ped else annotation_edges[0]['frame'] if eid=='white_suv' else annotation_edges[1]['frame'],subject=[plain_sample(r,pts) for r in subject],car=[plain_sample(r,pts) for r in car],manual=manual_rows,model=model_pixels,gates=gates,assumed_footprints=footprints,calibration_hull=np.asarray(g['hull']).reshape(-1,2).tolist(),car_missing_spans=car_spans,subject_missing_spans=sub_spans,metrics=metric,image_axis=image_axis.tolist() if image_axis is not None else None)
        if ped:
            conditional,scenarios=conditional_sensitivity(repo,pts,g,paths)
            event['conditional_scenarios']=scenarios;metric['conditional_ttc_s']=conditional
        else:event['conditional_scenarios']=[]
        manual_by={r['frame']:r for r in manual_rows if r['object']=='pedestrian'}
        contact_pairs=[(r,manual_by[r['frame']]) for r in manual_rows if r['object']=='car' and r['frame'] in manual_by]
        closest_manual=min(contact_pairs,key=lambda pair:math.hypot(pair[0]['x_px']-pair[1]['x_px'],pair[0]['y_px']-pair[1]['y_px'])) if contact_pairs else None
        metric.update(manual_contact_proxy_min_px=math.hypot(closest_manual[0]['x_px']-closest_manual[1]['x_px'],closest_manual[0]['y_px']-closest_manual[1]['y_px']) if closest_manual else None,manual_contact_proxy_min_frame=closest_manual[0]['frame'] if closest_manual else None,manual_synchronized_contact_count=len(contact_pairs))
        metric.update({**edge_minimum(annotation),**reviewed_pet(event,annotation)});event['metrics']=metric
        events.append(event);defaults.append(annotation)
        coverage.append(dict(event_id=eid,window_first_frame=lo,window_last_frame=hi,denominator=expected,subject_missing_spans=json.dumps(sub_spans),car_missing_spans=json.dumps(car_spans),counts_are_overlapping_not_mutually_exclusive=True))
        delta=np.diff(pts);timing.append(dict(event_id=eid,source_video=norm_path(video,repo),decoded_frames=len(pts),first_pts_s=pts[0],last_pts_s=pts[-1],median_interval_s=dt,min_interval_s=float(delta.min()),max_interval_s=float(delta.max()),nonpositive_intervals=int(sum(delta<=0)),intervals_above_1_5_median=int(sum(delta>1.5*dt)),max_nominal_fps_time_difference_s=float(np.max(np.abs(pts-np.arange(len(pts))/float(log['fps'])))),status='Decoded clip PTS audited; cannot establish dropped frames in original recording; absolute clock disagreement preserved'))
        provenance.append(video)
    return events,dict(schema_version=1,version=VERSION,events=defaults),coverage,timing,provenance

def conditional_sensitivity(repo,pts,g,paths):
    """Reuse saved model as an assumption experiment, not required physical calibration."""
    clicked=read(repo/'manual_occlusion_points.csv');fps=1/float(np.median(np.diff(pts)));manual=manual_samples(clicked,np.array(g['H']),fps)
    for r in manual:r['t']=float(pts[r['frame']-1])
    original=[{**r,'t':float(pts[r['frame']-1])} for r in paths[('pedestrian','1')] if manual[0]['frame']<=r['frame']<=manual[-1]['frame']]
    axis=np.array(g['road_axis']);scenarios=[];baseline=None
    settings=[('baseline','baseline',0),('click_x_minus3','x',-3),('click_x_plus3','x',3),('click_y_minus3','y',-3),('click_y_plus3','y',3),('timing_minus_frame','time',-1),('timing_plus_frame','time',1),('footprints_0.8','dim',.8),('footprints_1.2','dim',1.2),('acceleration_minus2','acc',-2),('acceleration_plus2','acc',2),('lateral_map_0.8','map',.8),('lateral_map_1.2','map',1.2),('first_half_fit','fit',.5)]
    for name,kind,val in settings:
        mm=copy.deepcopy(manual);subject=with_velocity(copy.deepcopy(original));scale=val if kind=='dim' else 1
        if kind in ('x','y'):
            for r in mm:r['pixel'][0 if kind=='x' else 1]+=val;r['xy']=project(g['H'],[r['pixel']])[0]
        if kind=='time':
            for r in mm:r['t']+=val*float(np.median(np.diff(pts)))
        if kind=='map':
            transform=np.outer(axis,axis)+val*np.outer([-axis[1],axis[0]],[-axis[1],axis[0]])
            for r in mm+subject:r['xy']=r['xy']@transform
            subject=with_velocity(subject)
        if kind=='fit':mm=mm[:max(3,len(mm)//2)]
        methods=dict(manual_observed=observed_method(mm,subject),linear_interpolation=interpolate_method(mm,subject,'linear'),constant_velocity=interpolate_method(mm,subject,'constant_velocity'),kalman=filtered_method(mm,subject,False),rts=filtered_method(mm,subject,True))
        if kind=='acc':
            for r in methods['constant_velocity']:
                t=r['t']-mm[0]['t'];r['xy']=r['xy']+.5*val*t*t*axis;r['velocity']=r['velocity']+val*t*axis
        for method,car in methods.items():
            r=metrics_for(subject,car,axis,method,dimension_scale=scale)
            # No arbitrary grid PET is emitted in the video-only workflow.
            scenarios.append(dict(event_id='pedestrian_car',scenario=name,method=method,conditional_ttc_s=r['min_ttc_s'] if r['min_ttc_s']!='' else None,ttc_units='s',eligible_physical_ttc=False,common_samples=r['samples'],assumption=f'{kind}={val}',pet_s=None,pet_eligibility='not_observable_without_shared_physical_zone',interpretation='Conditional model sensitivity; not calibrated error range, confidence interval or near-miss probability'))
            if name=='baseline' and method=='constant_velocity':baseline=None if r['min_ttc_s']=='' else r['min_ttc_s']
    return baseline,scenarios


def apply_annotations(events,annotations):
    validate_annotations(annotations,events);by={a['event_id']:a for a in annotations['events']}
    for e in events:
        a=by.get(e['event_id'],{})
        edge_window=[r for r in a.get('edges',[]) if e['metrics']['analysis_first_frame']<=r['frame']<=e['metrics']['analysis_last_frame']]
        e['metrics'].update({**edge_minimum(a),**reviewed_pet(e,a)},manual_edge_total_count=len(a.get('edges',[])),manual_edge_count=len(edge_window),manual_edge_pct=100*len(edge_window)/e['metrics']['expected_frame_count'],reviewer=a.get('reviewer',''),reviewer_notes=a.get('notes',''),evasive_action=a.get('evasive_action','unknown'))
        e['metrics']['missing_reason']=json.dumps(dict(physical_clearance='unverified lateral scale and physical edges',pet=e['metrics']['pet_reason'],physical_ttc='unvalidated model/footprints' if e['event_type']=='pedestrian_crossing' else 'no justified collision course for parallel pass',independent_validation='No new independent occupancy/contact labels until reviewer supplies them'))
    return events


def comparisons(events,annotations):
    by={a['event_id']:a for a in annotations['events']};rows=[]
    for e in events:
        aa={r['frame']:r for r in e['subject']};bb={r['frame']:r for r in e['car']};a=by[e['event_id']]
        for r in a.get('edges',[]):
            f=r['frame'];x,y=aa.get(f),bb.get(f);manual=abs(r['cyclist_x_px']-r['car_x_px']);auto=max(0,abs(x['x_px']-y['x_px'])-(x['box_w_px']+y['box_w_px'])/2) if x and y else None
            rows.append(dict(event_id=e['event_id'],comparison='manual_horizontal_edges_vs_detector_box_gap',manual_frame=f,automatic_frame=f if auto is not None else None,frame_difference=0 if auto is not None else None,time_difference_s=0. if auto is not None else None,manual_value_px=manual,automatic_value_px=auto,difference_px=auto-manual if auto is not None else None,interpretation='Different spatial proxies; difference is not measurement accuracy or physical-clearance error' if auto is not None else 'No simultaneous automatic vehicle point; do not substitute nearby frame',independent_reference=False,source=r.get('source','downloaded_review_annotations')))
        if e['event_type']=='pedestrian_crossing':
            for r in e['manual']:
                if r['object']!='car':continue
                auto=bb.get(r['frame']);dist=math.hypot(r['x_px']-auto['x_px'],r['y_px']-auto['y_px']) if auto else None
                rows.append(dict(event_id=e['event_id'],comparison='manual_car_contact_proxy_vs_sensitive_car68_bottom_center',manual_frame=r['frame'],capture_playback_time_s=r['original_click_time_s'],capture_playback_frame_delta=int(np.searchsorted(e['pts'],r['original_click_time_s'],side='right'))-r['frame'],automatic_frame=r['frame'] if auto else None,frame_difference=0 if auto else None,time_difference_s=0. if auto else None,manual_value_px=None,automatic_value_px=None,difference_px=dist,interpretation='Different contact proxies, not independently validated accuracy' if auto else 'Automatic car track unavailable at exact manual frame',independent_reference=False,source=r['source']))
            for key in ('pedestrian_exit','car_entry'):
                q=a.get('occupancy',{}).get(key,{})
                rows.append(dict(event_id=e['event_id'],comparison=key+'_manual_vs_automatic',manual_frame=q.get('frame_low'),automatic_frame=None,frame_difference=None,time_difference_s=None,manual_value_px=None,automatic_value_px=None,difference_px=None,interpretation='Automatic physical-zone occupancy not established; no frame error can be computed',independent_reference=False,reviewer_supplied=bool(a.get('reviewer')),source='review_annotations.json'))
    return rows


def sensitivity(events,annotations):
    rows=[];all_scenarios=[r for e in events for r in e['conditional_scenarios']]
    for e in events:
        for method in ('manual_observed','linear_interpolation','constant_velocity','kalman','rts') if e['event_type']=='pedestrian_crossing' else []:
            rr=[r for r in all_scenarios if r['method']==method];vals=[r['conditional_ttc_s'] for r in rr if r['conditional_ttc_s'] is not None]
            rows.append(dict(event_id=e['event_id'],metric='conditional_ttc',method=method,units='s',scenario_count=len(rr),available_scenarios=len(vals),ineligible_scenarios=len(rr)-len(vals),minimum=min(vals) if vals else None,maximum=max(vals) if vals else None,physical_metric_eligible=False,note='Conditional geometry/fit assumptions; not probability or calibrated uncertainty'))
        a=next(a for a in annotations['events'] if a['event_id']==e['event_id']);minimum=edge_minimum(a)['selected_min_edge_gap_px']
        if minimum is not None:rows.append(dict(event_id=e['event_id'],metric='selected_horizontal_edge_gap',method='each of two edge x positions ±3 px, independent worst-case; engineering assumption',units='px',scenario_count=4,available_scenarios=4,ineligible_scenarios=0,minimum=max(0,minimum-6),maximum=minimum+6,physical_metric_eligible=False,note='Selected frames only; not measured annotation error'))
        pet=reviewed_pet(e,a)
        rows.append(dict(event_id=e['event_id'],metric='reviewed_zone_pet',method='frame brackets; ±1-frame expansion sensitivity',units='s',scenario_count=1,available_scenarios=int(pet['pet_eligibility']=='supported_interval'),ineligible_scenarios=int(pet['pet_eligibility']!='supported_interval'),minimum=pet['pet_lower_s'],maximum=pet['pet_upper_s'],physical_metric_eligible=pet['pet_eligibility']=='supported_interval',note=pet['pet_reason']))
        if pet['pet_eligibility']=='supported_interval':
            dt=e['frame_interval_s'];low=pet['pet_lower_s']-2*dt;high=pet['pet_upper_s']+2*dt
            rows.append(dict(event_id=e['event_id'],metric='reviewed_zone_pet',method='both boundary times ±1 frame; worst-case difference ±2 frames',units='s',scenario_count=4,available_scenarios=4 if low>=0 else 0,ineligible_scenarios=0 if low>=0 else 4,minimum=low if low>=0 else None,maximum=high if low>=0 else None,physical_metric_eligible=low>=0,note='Uncertain order if expanded interval spans zero; signed lower/upper '+str(low)+'/'+str(high)))
    return rows,all_scenarios


def sweeps(events,config=CONFIG):
    rows=[]
    for metric in ('ttc','pet'):
        for cutoff in config['sweep_'+metric+'_s']:
            if metric=='ttc':
                conditional=[e['metrics']['conditional_ttc_s'] for e in events if e['metrics']['conditional_ttc_s'] is not None];eligible=[]
            else:conditional=[];eligible=[e['metrics'] for e in events if e['metrics']['pet_eligibility']=='supported_interval']
            rows.append(dict(metric=metric,threshold_s=cutoff,unique_event_denominator=len(events),eligible_metric_denominator=len(eligible),eligible_flags=sum(r['pet_upper_s']<cutoff for r in eligible),eligible_possible_flags=sum(r['pet_lower_s']<cutoff for r in eligible),conditional_metric_denominator=len(conditional),conditional_flags=sum(v<cutoff for v in conditional),review_labels_changed=False,interpretation='Strict <; interval flags guaranteed/possible; only conditional TTC available; no near-miss classification'))
    return rows


def build(repo,out,annotation_path=None,config_path=None):
    repo=repo.resolve();out=out.resolve()
    if out==repo/'reports/near_miss' or (repo/'reports/near_miss') in out.parents:raise ValueError('Use new versioned output folder; preserve prior reports')
    out.mkdir(parents=True,exist_ok=True)
    annotation_input=json.loads(annotation_path.read_text()) if annotation_path else None
    active_config=copy.deepcopy(CONFIG)
    if annotation_input and annotation_input.get('screening_config'):
        inherited=annotation_input['screening_config']
        if not isinstance(inherited,dict) or set(inherited)-set(CONFIG):raise ValueError('Unknown saved screening configuration')
        active_config.update(inherited)
    if config_path:
        supplied=json.loads(config_path.read_text())
        if set(supplied)-set(CONFIG):raise ValueError('Unknown screening configuration key')
        active_config.update(supplied)
    for key in ('adopted_ttc_s','adopted_pet_s'):
        v=active_config[key]
        if v is not None and (type(v) not in (int,float) or not math.isfinite(v) or v<=0):raise ValueError('Screening cutoffs must be positive seconds or null')
    if active_config['physical_clearance_m'] is not None:raise ValueError('Metre screening disabled: physical scale unverified')
    for key in ('ttc','pet'):
        vals=active_config['sweep_'+key+'_s']
        if not isinstance(vals,list) or any(type(v) not in (int,float) or not math.isfinite(v) or v<=0 for v in vals):raise ValueError('Sweep values must be positive finite seconds')
        if active_config['adopted_'+key+'_s'] is not None:active_config['sweep_'+key+'_s']=sorted(set(vals+[active_config['adopted_'+key+'_s']]))
    previous=repo/'reports/near_miss'
    preserved=[p for base in (previous,repo/BATCH,repo/FINAL) for p in base.rglob('*') if p.is_file()]
    preserved += [repo/'HANDOFF.md',repo/'clearance_edge_annotations_completed.csv',repo/'manual_occlusion_points.csv']
    before={str(p):digest(p) for p in preserved}
    events,defaults,coverage,timing,videos=make_events(repo)
    annotations=annotation_input if annotation_input is not None else defaults
    # Partial imports retain untouched existing edge evidence for other events.
    validate_annotations(annotations,events)
    provided={a['event_id']:a for a in annotations['events']}
    merged=[]
    for original in defaults['events']:
        incoming=provided.get(original['event_id'],{})
        merged.append({**original,**incoming,'zone':{**original['zone'],**incoming.get('zone',{})}})
    annotations={**defaults,'events':merged}
    apply_annotations(events,annotations)
    for e in events:
        m=e['metrics'];m['screening_ttc_s']=active_config['adopted_ttc_s'];m['screening_pet_s']=active_config['adopted_pet_s']
        m['supported_ttc_screen_flag']=False
        m['conditional_ttc_screen_flag']=(m['conditional_ttc_s']<m['screening_ttc_s']) if m['conditional_ttc_s'] is not None and m['screening_ttc_s'] is not None else None
        m['supported_pet_screen_flag']=(m['pet_upper_s']<m['screening_pet_s']) if m['pet_eligibility']=='supported_interval' and m['screening_pet_s'] is not None else None
        m['possible_pet_screen_flag']=(m['pet_lower_s']<m['screening_pet_s']) if m['pet_eligibility']=='supported_interval' and m['screening_pet_s'] is not None else None
    write(out/'event_metrics.csv',[e['metrics'] for e in events]);write(out/'observation_coverage.csv',coverage);write(out/'timing_audit.csv',timing)
    alignment=[]
    for e in events:
        for r in e['manual']:
            decoded_frame=int(np.searchsorted(e['pts'],r['original_click_time_s'],side='right'))
            alignment.append(dict(event_id=e['event_id'],object=r['object'],saved_frame=r['frame'],original_playback_time_s=r['original_click_time_s'],selected_frame_pts_s=e['pts'][r['frame']-1],playback_time_decoded_frame=decoded_frame,frame_delta=decoded_frame-r['frame'],status='frame_ID_and_playback_time_agree' if decoded_frame==r['frame'] else 'capture_frame_ambiguity; do_not_silently_relabel; ±1-frame_sensitivity_applies'))
    write(out/'annotation_alignment_audit.csv',alignment)
    write(out/'validation_comparison.csv',comparisons(events,annotations));summary,scenarios=sensitivity(events,annotations);write(out/'sensitivity_summary.csv',summary);write(out/'conditional_scenarios.csv',scenarios);write(out/'threshold_sweep.csv',sweeps(events,active_config))
    json_write(out/'validation_summary.json',dict(unique_events=len(events),visually_reviewed_passes=2,reviewed_crossings=1,potential_conflicts=sum(e['metrics']['review_label']=='potential_conflict' for e in events),confirmed_under_validated_protocol=0,calibrated_clearances=0,conditional_ttc_events=sum(e['metrics']['conditional_ttc_s'] is not None for e in events),supported_pet_intervals=sum(e['metrics']['pet_eligibility']=='supported_interval' for e in events),negative_controls=2,policy='Selected sample; no population rate or near-miss probability; zero confirmed does not prove zero occurred'))
    json_write(out/'review_annotations.json',annotations);json_write(out/'screening_config.json',active_config);json_write(out/'literature_sources.json',SOURCES)
    write(out/'negative_controls.csv',read(previous/'excluded_candidates.csv'))
    for p in ('pair_eligibility.csv','frame_eligibility.csv','thresholds.csv','threshold_source_inventory.csv','effective_task_configuration.csv','clock_alignment_audit.csv'):
        shutil.copy2(previous/p,out/p)
    payload=dict(schema_version=1,version=VERSION,events=events,annotations=annotations,config=active_config)
    # Compact data also supports regeneration and tests without parsing embedded videos.
    json_write(out/'review_data.json',payload)
    template=(repo/'pipeline/near_miss_validation_viewer.html').read_text();engine=(repo/'pipeline/near_miss_validation_engine.js').read_text()
    embedded=[]
    for e,video in zip(events,videos):
        embedded.append({**e,'video_data_url':'data:video/mp4;base64,'+base64.b64encode(video.read_bytes()).decode('ascii')})
    embedded_payload={**payload,'events':embedded}
    html=template.replace('__ENGINE__',engine).replace('__REVIEW_DATA__',json.dumps(embedded_payload,default=serial,separators=(',',':'),allow_nan=False).replace('</','<\\/'))
    (out/'review_validation.html').write_text(html)
    make_docs(repo,out,events,timing,summary,annotations,active_config)
    after={p:digest(p) for p in before}
    if before!=after:raise RuntimeError('Source evidence changed during generation')
    write(out/'provenance.csv',[dict(path=norm_path(Path(p),repo),sha256=h,unchanged=True) for p,h in before.items()])
    json_write(out/'build_manifest.json',dict(version=VERSION,annotation_input=str(annotation_path) if annotation_path else 'existing annotations only; no new user occupancy labels',annotation_input_sha256=digest(annotation_path) if annotation_path else None,config_input=str(config_path) if config_path else None,source_files_checked=len(before),source_files_unchanged=True,generated_files=[p.name for p in out.iterdir() if p.is_file()],code_sha256={n:digest(repo/'pipeline'/n) for n in ('near_miss_next.py','near_miss_validation_engine.js','near_miss_validation_viewer.html')},video_sha256={norm_path(p,repo):digest(p) for p in videos},limitations=['Original recording timing is not independently validated','Physical scale, collision model and conflict-zone boundaries unverified','Independent manual occupancy reference not yet supplied']))
    print('Built',out)
    for e in events:
        m=e['metrics'];print(e['event_id'],'synchronized=',m['synchronized_observed_count'],'edge_px=',m['selected_min_edge_gap_px'],'proxy_px=',m['image_proxy_distance_px'],'conditional_TTC_s=',m['conditional_ttc_s'],'PET=',m['pet_eligibility'])


def make_docs(repo,out,events,timing,summary,annotations,active_config=CONFIG):
    from generate_near_miss_report import table
    rows=[]
    for e in events:
        m=e['metrics'];rows.append(dict(event=e['event_id'],frames=f"{m['analysis_first_frame']}–{m['analysis_last_frame']}",sync=f"{m['synchronized_observed_count']}/{m['expected_frame_count']} ({m['synchronized_observed_pct']:.1f}%)",selected_edge_px='N/A' if m['selected_min_edge_gap_px'] is None else f"{m['selected_min_edge_gap_px']:.0f} @ frame {m['selected_min_edge_gap_frame']}",detector_proxy_px=f"{m['image_proxy_distance_px']:.3f} @ frame {m['image_proxy_frame']}",manual_proxy_px=f"{m['manual_contact_proxy_min_px']:.3f} @ frame {m['manual_contact_proxy_min_frame']}" if m['manual_contact_proxy_min_px'] is not None else 'N/A',relative_px_s=f"{m['relative_image_velocity_px_s']:.3f}" if m['relative_image_velocity_px_s'] is not None else 'N/A',conditional_TTC_s=f"{m['conditional_ttc_s']:.6f}" if m['conditional_ttc_s'] is not None else 'N/A',reviewed_zone_PET_s=f"[{m['pet_lower_s']:.6f}, {m['pet_upper_s']:.6f}]" if m['pet_lower_s'] is not None else 'N/A',review=m['review_label']))
    cv=next(r for r in summary if r['method']=='constant_velocity');pet=events[-1]['metrics']
    report=f'''# Video-only near-miss results — {VERSION}

- **3 unique reviewed interactions:** 2 cyclist passes and 1 close pedestrian crossing. Repeated detector/scenario rows are not encounters.
- Selected cyclist horizontal image gaps remain **6 px** and **20 px**, each from 3 existing annotated frames. These are not continuous minima or physical lateral clearance.
- Approximate cyclist speeds remain **9.709555 mph** and **11.515719 mph**, using the same unvalidated learned mapping; agreement with manual speeds does not validate scale.
- Pedestrian historical conditional TTC **0.371804 s** is preserved. The PTS-based recomputation is **{pet['conditional_ttc_s']:.6f} s** under the existing unvalidated CV/footprint model; conditional CV assumption range **{cv['minimum']:.6f}–{cv['maximum']:.6f} s** across {cv['scenario_count']} scenarios.
- **0.294117647 is 5/17 observation coverage, not PET.** No occupancy-based PET is available from the original annotations. Current imported review status: **{pet['pet_eligibility']}**; supported reviewer intervals appear below only if actually supplied.
- **0 validated metre clearances; 0 confirmed near misses under a validated protocol.** This does not mean no near misses occurred. The sample cannot estimate a population rate.

{table(rows,list(rows[0]))}

## What was checked

- Decoded clip frame PTS are audited directly with ffprobe; frame stepping uses each decoded frame, not only detection samples. Counts/percentages use each explicitly listed analysis window. Detected/manual/reconstructed coverage categories overlap; true visibility coverage remains unknown without per-frame visibility review.
- The 58/98 cyclist synchronized samples remain diagnosed: all fail the assumed alongside gate (3.15 learned units); no strict supported pair. Along-track ranges are −18.803 to −5.817 and −21.874 to −4.105 learned units. Gate failures are geometric; local detection gaps are reported separately.
- All six pre-existing cyclist edge annotations are loaded automatically. Manual-versus-detector comparisons are same-frame differences between distinct image proxies, **not independently measured accuracy**. Three pedestrian car-click/detector comparisons are 29.14, 37.61 and 72.69 px; car namespace is sensitive 68, not unrelated reference 68.
- The original click tool rounded playback time to a frame ID; pedestrian car click saved as frame1382 has playback time 46.072939 s, which lies in decoded frame1381. This one-frame capture ambiguity is preserved in `annotation_alignment_audit.csv`; no automatic relabeling or certified same-frame accuracy is claimed. ±1-frame sensitivity remains required.
- No independent occupancy entry/exit labels were invented. `validation_comparison.csv` leaves unavailable automatic physical-zone boundary errors null. The interactive viewer accepts targeted review and preserves provenance.
- Sensitive track21 (wheel false car) and the middle no-pass comparison remain excluded. Review labels remain two indeterminate safety classifications and one potential conflict.

## Limitations and smallest next evidence

- For PET, mark one shared physical road-space zone and bound pedestrian exit/car entry using visible neighboring frames. Where occluded, supply defensible interval brackets and notes; if the order cannot be established, leave PET N/A. Surveyed dimensions are unnecessary for this timing task. Drawing a polygon or overlapping image boxes alone does not establish shared physical occupancy.
- To check cyclist continuous minima, inspect additional visible passing frames; retain 6/20 px as selected-frame results until then. No mandatory re-annotation of the six existing frames.
- Physical clearance and physical TTC remain unavailable without validated geometry/footprints or a validated alternative collision model. Evasive action is unknown; noisy pixel derivatives do not establish hard braking.
- Absolute clocks remain unresolved: white frame391 nominal 12:40:21.013 vs burned-in 12:40:23; dark frame445 nominal 12:53:52.815 vs 12:53:54; pedestrian frame1405 nominal 17:08:46.847 vs 17:08:49. Saved pedestrian raw CSV labels also have a five-hour mismatch. No fixed clock correction is applied. Frame-relative PTS drive new metrics; source recording drop/loss cannot be certified from re-encoded clips.

Open [offline viewer](review_validation.html). Data: [event metrics](event_metrics.csv), [manual/automatic comparisons](validation_comparison.csv), [sensitivity](sensitivity_summary.csv), [timing](timing_audit.csv), [methods and references](METHODS_AND_THRESHOLDS.md), [run/review instructions](RUN_AND_REVIEW.md).
'''
    (out/'PROFESSOR_RESULTS_UPDATED.md').write_text(report)
    methods='''# Methods, eligibility and thresholds

Implementation: `pipeline/near_miss_next.py` (`make_events`, `pts_for`, `conditional_sensitivity`, `reviewed_pet`, `comparisons`, `sweeps`); offline calculations: `pipeline/near_miss_validation_engine.js` (`pet`, `edgeMinimum`, `reviewedEvents`). Rendering/annotation: `pipeline/near_miss_validation_viewer.html`. Original path audit and exact existing code/config lines are preserved in `thresholds.csv`, `threshold_source_inventory.csv`, `effective_task_configuration.csv` and the prior `reports/near_miss/CODE_PATH_MAP.md`. No original evidence or earlier report was overwritten. New configurable cutoffs live in CONFIG near the top of `pipeline/near_miss_next.py`; `--config` accepts JSON overrides for adopted_ttc_s/adopted_pet_s (seconds), and rejects non-null physical_clearance_m. Exported screening_config.json records effective settings. Values change screen flags only; physical TTC remains ineligible.

## Relative timing and observation coverage

Frame IDs are one-based decoded video frames. `pts_for` reads best_effort_timestamp_time via ffprobe, requires strictly increasing finite values, and subtracts the first timestamp. The analysis window is each cyclist car track's first-to-last observed frame; pedestrian window is the first-to-last manual car frame (1382–1411). Synchronization is exact frame-ID intersection, never nearest-time substitution. Coverage = count / number of decoded frame slots in that window. Categories overlap and are not percentages of verified visibility. A missing run duration includes one median frame interval; before/after outside the window is not counted. PTS intervals >1.5×median are flagged as possible decoded timing gaps (engineering audit, not proof of source frame drops). Original raw recordings are not independently audited. `annotation_alignment_audit.csv` compares old click playback times to selected frame PTS. The old tool used round(time×fps)+1; one car click (saved 1382) lies in decoded frame1381 at its stored playback time. Saved IDs are retained for benchmark reproducibility; this ambiguity is not silently corrected and same-ID proxy comparisons are not certified frame-accurate reference errors.

## Image diagnostics (pixels and seconds)

Selected edge gap = abs(car_edge_x − cyclist_edge_x) at a manually annotated frame. Minimum is over visible annotated frames only. Existing edge records store x only, so viewer vertical rulers do not manufacture y coordinates. Automated proxy distance = Euclidean distance between synchronized detector bottom-centres; boxes are detector envelopes, not measured physical footprints. Relative image velocity is the least-squares slope of (car pixel position − subject pixel position) against PTS over synchronized samples in the analysis window. Its magnitude is px/s. Along-image-axis relative speed is its signed dot product with the subject endpoint-displacement unit vector, also px/s, not a perspective-correct road speed. The closest proxy frame minimizes observed synchronized proxy distance; no metric extrapolation is used for that result.

## Occupancy-based PET, requiring no surveyed dimensions

One reviewer-defined image polygon must identify a shared **physical** road-space region, with reviewer name, explicit physical-identity confirmation and justification. No detector overlap/grid substitutes for that confirmation. A pedestrian last-occupied frame creates an exit bracket from that frame to the next frame; a car first-occupied frame creates an entry bracket from the previous frame to that frame. Each bracket needs independent support: check neighboring frames or give explicit bounded-occlusion evidence and notes. Drawing the polygon alone produces N/A.

For exit interval [pL,pH] and entry interval [cL,cH], signed difference interval = [cL−pH, cH−pL]. Nonnegative intervals are provisional reviewer-supported PET intervals, in seconds; no point estimate is invented. If wholly negative, label temporal overlap; if spanning zero, label uncertain order and leave conventional positive PET N/A. If a user selects a single boundary frame, expand by half the median frame interval on either side to retain quantization. Zero is not a missing-value placeholder. `coverage_fraction` is never an input to this formula. A real PET could coincidentally have the same numerical value as coverage; the test verifies provenance/formula independence, not a forbidden floating-point equality.

No existing annotations identify the conflict zone or entry/exit occupancy boundaries. Thus original-data PET remains N/A. The older shared learned-grid PET method is not used for new PET exports or screens.

## Conditional TTC and alongside assumptions

The historical saved benchmark (0.371803710 s, rounded 0.371804) remains distinct from the new PTS-based conditional recomputation. Reuse saved H only for this historical model/sensitivity comparison; no new calibration or survey is required to run video diagnostics. Manual car clicks are projected using the saved unvalidated map, a constant-velocity trajectory is fitted, pedestrian velocities use synchronized observed positions, and fixed road-axis rectangles are swept continuously for common future occupancy up to 5 s (`clearance_metrics.collision_ttc`). Assumed pedestrian/car dimensions are 0.7×0.6 / 4.5×1.8 learned units. Geometry/scale/physical footprint validity is unverified; the result cannot screen as an eligible physical TTC. Image-space TTC is N/A because no validated alternative projective collision model is available. Generic pixel distance / mph is never used.

Cyclist gate: absolute along-axis offset <= (1.8+4.5)/2 = 3.15 learned units. Saved bottom-centre footprints never reach this interval for either known pass. These overlays illustrate assumptions, not ground truth. Direction evidence and visual passes survive metric failure. Parallel passing has no supported TTC/PET collision-course model here. Physical clearance_m remains null regardless of annotations/screens.

## Sensitivity and screening

New PTS-based TTC sensitivity uses 14 one-factor settings × five reconstruction methods: car click x/y ±3 px, boundary timing ±1 median frame, dimensions 0.8/1.2, lateral mapping 0.8/1.2, acceleration ±2 learned units/s² for CV only, first-half car fit, and baseline. These perturbations are engineering choices, not empirically calibrated error bars. Unsupported methods remain N/A. Old 16-scenario results remain unchanged in `reports/near_miss/`. Selected horizontal edge gap worst-case range uses each of two x positions ±3 px (gap ±6 px, floor at zero). Reviewed PET uses occupancy brackets; optional expansion of both times ±1 frame changes gap bounds by ±2 frame intervals. Missing/uncertain ordering is retained.

Default adopted numerical cutoffs are **unset**, and metre thresholds disabled. Effective settings, including any explicit --config or saved-JSON overrides, are recorded in screening_config.json. Optional literature-context settings TTC 1.5 s / PET 5.0 s are proposed only for transparent exploratory comparison when metrics become eligible; they are vehicle-simulation defaults, not validated pedestrian/cyclist criteria. Sweeps use strict `<` and report separately: 3 unique events, eligible metric denominator, conditional metric denominator, and guaranteed/possible interval flags. Cited SSAM applications use their own logic (including <=), which is not silently reproduced as a local adjudication rule. Screens never alter two `indeterminate` labels or the pedestrian `potential_conflict`. No validated confirmed-under-protocol rule exists.

## Primary references verified 2026-11-10

- [FHWA-HRT-08-051, Chapter 2 (June 2008)](https://www.fhwa.dot.gov/publications/research/safety/08051/02.cfm): describes SSAM vehicle-to-vehicle simulation conflict analysis and a configurable 1.5-second TTC default.
- [FHWA-HRT-10-038, Chapter 3 (October 2010)](https://www.fhwa.dot.gov/publications/research/safety/10038/003.cfm): its SSAM simulation application uses TTC <=1.5 s and PET <=5.0 s. This context does not validate either value for these video events.

Existing hard-coded legacy 1 m / 1 s screens and prior 0.5/1/1.5 learned-clearance sweeps are documented in preserved source inventories; they remain historical and are not adopted. A close visual event, short conditional TTC, or fraction of sensitivity settings below threshold is not a collision/near-miss probability.
'''
    settings=[
        ('near_miss_next.py','CONFIG=dict','Default screening thresholds null; optional SSAM-context TTC 1.5 s / PET 5 s, no metre threshold'),
        ('near_miss_next.py','if not probe.get','Source dimensions must be 720x480 to match stored annotation coordinates'),
        ('near_miss_next.py','delta>1.5*dt','Decoded PTS gap audit >1.5 median interval; not a safety screen'),
        ('near_miss_next.py',"settings=[('baseline'",'14 assumption settings: ±3 px clicks, ±1 frame timing, .8/1.2 footprint/lateral scale, ±2 learned-unit acceleration, first-half fit'),
        ('near_miss_next.py',"if not polygon_valid",'PET requires reviewer, nondegenerate shared-zone polygon, physical identity justification, supported boundary brackets'),
        ('near_miss_validation_engine.js','lo-dt/2','Single-frame occupancy boundaries expanded by half median PTS interval'),
        ('near_miss_validation_engine.js','function polygonValid','Polygon shoelace magnitude >1 (area >0.5 px²); numerical degeneracy check only'),
        ('near_miss_validation_viewer.html','Math.min(.001','Seek +min(0.001 s, 0.1 frame interval) inside intended frame; overlay uses original frame PTS'),
        ('near_miss_validation_viewer.html','a[mid]<=t+1e-6','Playback frame lookup tolerance 1e-6 s; not a metric threshold')]
    inventory=[]
    for name,needle,meaning in settings:
        source=repo/'pipeline'/name;lines=source.read_text().splitlines();hits=[i for i,line in enumerate(lines,1) if needle in line and not line.strip().startswith("('")]
        inventory.append(dict(source=f'pipeline/{name}:{hits[0]}' if hits else f'pipeline/{name}',setting=meaning,status='new diagnostic/configuration assumption; not validated safety ground truth'))
    write(out/'new_threshold_inventory.csv',inventory)
    methods+='\n## New code settings and exact source locations\n\n'+table(inventory,['setting','source','status'])+'\n'
    (out/'METHODS_AND_THRESHOLDS.md').write_text(methods)
    relative=norm_path(out,repo)
    (out/'RUN_AND_REVIEW.md').write_text(f'''# Run and targeted review

```sh
cd /Users/rithika/Desktop/objectDetect
python3 pipeline/near_miss_next.py --out {relative}
open {relative}/review_validation.html
```

The HTML is self-contained: all three original MP4 clips, source hashes, PTS, tracks, annotations, styles and scripts are embedded. It works offline by double-clicking; no server/account/network/CDN is required. Missing source assets cause an explicit generator error, never fabricated frames. Browser decode failures show a visible error. Existing assets total 120 seconds (two 30 s cyclist clips and one 60 s pedestrian clip); no new inference or video experiment occurs.

1. Select an event. Play/pause; step ±1 decoded frame; type a frame or scrub. Wheel/zoom controls zoom around the cursor; use Pan mode to drag. Reset restores image coordinates. Right panel shows image trajectories, nearest synchronized approach, manual/detector differences and gate diagnostics.
2. Toggle boxes, histories, manual points/edge rulers, assumed footprint overlays, calibration support or reconstructed segments. Reconstruction is labeled and off by default. Missing automatic car boxes/track-loss spans do not mean no vehicle. PTS time and one-based frame appear prominently; absolute source clocks remain unresolved.
3. Cyclists: all six usable edge frames are preloaded. Click a saved-frame chip to inspect. Only if checking the continuous visible-pass minimum, select Edge mode, mark cyclist and near-side car x coordinates, set visibility/uncertainty and save. Existing annotations remain unless explicitly replaced at the same frame. Exports retain original records and an edit history for replacements. Vertical rulers encode x only.
4. Pedestrian PET (the only necessary new annotation if PET is wanted): select Zone mode, click at least three vertices, finish polygon. Verify that it corresponds to the same physical road-space zone for both users; record why, reviewer name and confirmation. Drawing image overlap is insufficient. Capture last pedestrian occupied / first car occupied frames, independently check neighboring frames, and check each boundary-supported box. Broaden frame brackets with evidence if occluded and record notes. Unsupported boundaries produce N/A; negative differences show temporal overlap; overlapping time brackets show uncertain order. No surveyed dimensions are required.
5. Optional per-frame footprint polygons can be marked and saved for either object, with visibility. They are manual image annotations, not automatically metric road footprints. Evasive action remains unknown unless a reviewer supplies visible evidence and notes.
6. Save annotations JSON for regeneration; CSV exports are also provided. Export reviewed event CSV and validation summary directly in the browser. Nothing is uploaded or written back to original sources. Import a saved JSON to restore edits; source-video hash/schema checks reject mismatched files. Unsaved changes prompt before leaving. Exports use the current review state; no automatic confirmed label exists.

To regenerate tables from a downloaded JSON (replace the file path):

```sh
python3 pipeline/near_miss_next.py --annotations /path/to/near_miss_annotations.json --out reports/near_miss_next/20261110_reviewed_v2
python3 -m pytest tests vision3/best/test_colonial/code/test_clearance_pilot.py -q
node --test tests/near_miss_validation_engine.test.cjs
```

Optionally pass `--config /path/to/screening_settings.json`, with e.g. `{{"adopted_ttc_s": 1.5, "adopted_pet_s": 5.0}}`. These are opt-in context-limited exploratory comparisons, never confirmed labels. Defaults stay null; metre screens are rejected.

Use a new output version to retain snapshots. Browser JSON edits do not modify CSV files already on disk; run regeneration or download current event CSV explicitly. Existing evidence suffices for selected-frame gaps; do not repeat those six annotations. No new occupancy/physical-zone labels are inferred from older manual car clicks. Unresolved PET needs this targeted visual judgment, not a new calibration survey or GPU run.
''')
    (out/'CHANGELOG.md').write_text('''# Before / after and limits

Before: read-only historical viewer, sampled-frame stepping, external videos, no annotation round trip, limited coverage/PTS exports. After: self-contained offline original-video review, exact decoded-frame stepping, zoom/pan, overlays/trajectories/gate display, preloaded six cyclist edges, physical-zone occupancy bracket review, footprint annotation, JSON/CSV export and JSON re-import/regeneration. Existing numerical reports and evidence remain intact.

New code: pipeline/near_miss_next.py, pipeline/near_miss_validation_engine.js, pipeline/near_miss_validation_viewer.html. New regression and browser tests accompany the versioned output. No original pipeline source or historical results are changed by this task. Code/source hashes are in build_manifest.json and provenance.csv.

Numerical additions: explicit coverage denominators, longest missing runs, decoded PTS audit, closest synchronized image proxies, signed relative image-axis speed, manual/detector comparison missingness, PTS-based conditional TTC sensitivity, reviewed PET interval engine. No unsupported physical distance, image TTC, occupancy boundaries, evasive action, independent ground truth, confirmed near miss or population rate is invented. The historical PET=0.294 error stays corrected.
''')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,default=ROOT);p.add_argument('--out',type=Path,default=ROOT/'reports/near_miss_next'/VERSION);p.add_argument('--annotations',type=Path);p.add_argument('--config',type=Path);a=p.parse_args();build(a.repo,a.out,a.annotations,a.config)
if __name__=='__main__':main()
