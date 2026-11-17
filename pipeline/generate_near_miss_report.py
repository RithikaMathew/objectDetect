#!/usr/bin/env python3
"""CPU-only evidence audit and event report. Never calibrates physical scale.

python3 pipeline/generate_near_miss_report.py --repo . --out reports/near_miss
"""
from __future__ import annotations
import argparse
import ast
import copy
import csv
import hashlib
import html
import json
from collections import Counter
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'vision3/best/test_colonial/code'))
sys.path.insert(0, str(ROOT / 'pipeline'))
from clearance_metrics import prepare, local_motion, diagnose_pair, project, road_axis, pet_cells
from manual_occlusion_metrics import manual_samples, with_velocity, observed_method, interpolate_method, filtered_method, metrics_for

BATCH = 'reports/cluster_returns/20261109/CLEARANCE_PILOT_20261109_175030_116203'
FINAL = 'reports/clearance_pilot/final_review_20261109'
FIELDS = '''event_id event_type clip_id start_time end_time object_ids track_source observation_status tracking_quality calibration_status calibration_support estimated_speed speed_units relative_speed_est relative_speed_units min_image_gap_px min_clearance_m ttc_s pet_s ttc_method pet_method metric_eligibility null_reason screening_flags threshold_config reviewed_classification review_evidence uncertainty_notes historical_ttc_s historical_pet_s reproduced_surrogate_ttc_s reproduced_surrogate_pet_s image_gap_method event_window_basis'''.split()

def read(path):
    with Path(path).open(newline='') as f: return list(csv.DictReader(f))

def write(path, rows, fields=None):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    fields = fields or sorted({k for r in rows for k in r})
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

def diagnostic_rows(rows):
    # Historical API names used metres despite learned scale; new exports name the assumption.
    names={'min_center_distance_m':'min_center_distance_unvalidated_learned_units',
           'min_lateral_gap_m':'assumed_axis_gap_unvalidated_not_crossing_clearance'}
    return [{names.get(k,k):v for k,v in r.items()} for r in rows]

def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def serial(value):
    if isinstance(value, np.ndarray): return value.tolist()
    if isinstance(value, np.generic): return value.item()
    raise TypeError(type(value).__name__)
def finite(value): return value is not None and value != '' and np.isfinite(float(value))
def fmt(value): return f'{float(value):.6f}' if finite(value) else 'N/A'
def table(rows, fields):
    return '| ' + ' | '.join(fields) + ' |\n|' + '|'.join(['---']*len(fields)) + '|\n' + '\n'.join('| ' + ' | '.join(str(r.get(k, 'N/A') if r.get(k) not in ('',None) else 'N/A').replace('|',';') for k in fields) + ' |' for r in rows)

def load_task(task):
    g=json.loads((task/'geometry.json').read_text()); log=json.loads((task/'run_log.json').read_text())
    labels={r['track_id']:r for r in read(task/'tracks_csv.csv')}
    paths=prepare(read(task/'trajectories_csv.csv')+read(task/'vehicle_trajectories_csv.csv'),g['H'],g['hull'],float(log['fps']),labels)
    return g,log,paths

def screening(event, config):
    """Only eligible metrics screen; reviewed classification is never changed."""
    flags=['visual_interaction_candidate'] if event.get('event_id') else []
    for field,key in [('min_image_gap_px','image_horizontal_gap_px'),('ttc_s','ttc_s'),('pet_s','pet_s'),('min_clearance_m','physical_clearance_m')]:
        cutoff=config.get(key)
        if cutoff is not None and finite(event.get(field)) and float(event[field]) < cutoff:
            flags.append(f'{field}_below_{cutoff}')
    return '|'.join(flags)

def pixel_motion(a,b):
    common=sorted({r['frame'] for r in a}&{r['frame'] for r in b})
    aa={r['frame']:r for r in a};bb={r['frame']:r for r in b}
    if len(common)<3:return None
    times=np.array([aa[f]['t'] for f in common]);rel=np.array([bb[f]['pixel']-aa[f]['pixel'] for f in common])
    return float(np.linalg.norm(np.polyfit(times-times.mean(),rel,1)[0]))

def trajectory_plot(path, title, a, b, manual=None):
    fig,ax=plt.subplots(figsize=(8,5))
    for samples,label,color in [(a,'automatic subject','#008859'),(b,'automatic vehicle','#2166ac')]:
        if samples:
            xy=np.array([r['pixel'] for r in samples]);ax.plot(xy[:,0],xy[:,1],'.-',label=label,color=color,ms=3)
    if manual:
        for kind,color in [('car','#e34a33'),('pedestrian','#d5a000')]:
            rr=[r for r in manual if r['object']==kind];ax.scatter([float(r['x_px']) for r in rr],[float(r['y_px']) for r in rr],marker='x',color=color,label='manual '+kind)
            for r in rr:ax.annotate(r['frame'],(float(r['x_px']),float(r['y_px'])),fontsize=6)
    aa={r['frame']:r for r in a};bb={r['frame']:r for r in b};common=aa.keys()&bb.keys()
    if common:
        f=min(common,key=lambda f:np.linalg.norm(aa[f]['pixel']-bb[f]['pixel']))
        for item,color in [(aa[f],'#008859'),(bb[f],'#2166ac')]:
            x,y=item['pixel'];ax.add_patch(plt.Rectangle((x-item['box_w']/2,y-item['box_h']),item['box_w'],item['box_h'],fill=False,color=color,lw=2))
        ax.set_title(f'{title}\nClosest synchronized bottom centres: frame {f}, clip +{aa[f]["t"]:.3f}s',fontsize=10)
    else:ax.set_title(title,fontsize=10)
    ax.set(xlabel='Image x (px)',ylabel='Image y (px)');ax.invert_yaxis();ax.legend(fontsize=8);ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(path,dpi=150);plt.close(fig)

def cyclist_events(repo,out):
    edges=read(repo/'clearance_edge_annotations_completed.csv');speeds=read(repo/FINAL/'speed_baseline_comparison.csv')
    events=[];summaries=[];frames=[];edge_comparison=[]
    for clip,vid,name in [('colonial_124020','9','white_suv'),('colonial_125350','18','dark_car')]:
        g,log,paths=load_task(repo/BATCH/(clip+'_reference'))
        a,b=paths[('cyclist','1')],paths[('car',vid)]
        summary,rr=diagnose_pair(a,b,'car',np.array(g['road_axis']))
        summary.update(event_id=name,task=clip+'_reference');summaries.append(summary)
        frames.extend(dict(event_id=name,**r) for r in rr)
        ee=[r for r in edges if r['clip']==clip and r['usable']=='yes']
        for e in ee:
            frame=int(e['frame_zero_based'])+1
            r=next(r for r in rr if r['frame']==frame)
            edge_comparison.append(dict(event_id=name,frame=frame,source_annotation='clearance_edge_annotations_completed.csv',manual_horizontal_edge_gap_px=e['pixelGap'],detector_horizontal_box_gap_px=r.get('horizontal_box_gap_px'),bottom_center_distance_px=r.get('bottom_center_distance_px'),interpretation='different_image_proxies_neither_is_road_plane_clearance'))
        speed=next(r for r in speeds if r['task']==clip+'_reference' and r['method']=='local')['automatic_median_mph']
        from datetime import datetime,timedelta
        clock=lambda sec:(datetime(2019,7,10,12)+timedelta(seconds=sec)).isoformat(sep=' ',timespec='milliseconds')
        event=dict.fromkeys(FIELDS,'')
        event.update(event_id=name,event_type='cyclist_pass',clip_id=clip,
            start_time=clock(min(float(r['source_seconds_inferred']) for r in ee)),end_time=clock(max(float(r['source_seconds_inferred']) for r in ee)),
            object_ids=f'cyclist 1 / car {vid} (reference namespace)',track_source=f'{BATCH}/{clip}_reference',
            observation_status='observed_pass_selected_frames',tracking_quality=f'{summary["simultaneous_samples"]} synchronized samples; tracks exist',
            calibration_status='not_calibrated_lateral_scale',calibration_support=f'{summary["supported_samples"]} supported shared samples',
            estimated_speed=speed,speed_units='mph; exploratory learned-map cyclist speed over prior manual window',
            relative_speed_est=pixel_motion(a,b),relative_speed_units='px/s; magnitude of fitted image relative velocity over shared observations',
            min_image_gap_px=min(float(r['pixelGap']) for r in ee),image_gap_method='minimum of 3 manually annotated horizontal edge gaps; selected frames only',
            ttc_method='not applicable to observed parallel pass; assumed-plane swept rectangles yield no collision course',
            pet_method='not observable: no independently established shared physical conflict region',
            metric_eligibility='image diagnostics eligible; physical metrics ineligible',
            null_reason=json.dumps(dict(min_clearance_m='not_calibrated: lateral scale unverified; outside support; unreliable physical footprint',ttc_s='not_applicable: no collision course in assumed-plane model; physical model unvalidated',pet_s='not_observable: no established shared physical conflict region')),
            threshold_config=json.dumps(config_global,sort_keys=True),reviewed_classification='indeterminate',
            review_evidence=f'{FINAL}/reviewed_encounters.csv; clearance_edge_annotations_completed.csv; frame_eligibility.csv',
            uncertainty_notes='Visual pass established; near-miss status indeterminate. Pixel gap is view-dependent, not a continuous minimum or perpendicular distance. Speeds share learned H.',
            event_window_basis='selected edge-annotation interval; source clock filename-inferred')
        event['screening_flags']=screening(event,config_global);events.append(event)
        trajectory_plot(out/'assets'/f'{name}_trajectory.png',name.replace('_',' '),a,b)
    write(out/'pair_eligibility.csv',summaries);write(out/'frame_eligibility.csv',frames);write(out/'edge_proxy_comparison.csv',edge_comparison)
    return events,summaries

def reconstruction(repo,out):
    task=out/'inputs/pedestrian';g,log,paths=load_task(task);fps=float(log['fps']);axis=road_axis(paths,('pedestrian',))
    annotations=read(repo/'manual_occlusion_points.csv')
    # Reproduce historical implementation exactly before repairing timestamps/clamping.
    historical_manual=manual_samples(annotations,np.array(g['H']),fps,'historical_click_time')
    def subject_window(manual):
        return with_velocity([{**r,'observation_status':'observed'} for r in paths[('pedestrian','1')] if manual[0]['t']<=r['t']<=manual[-1]['t']])
    def methods(manual,subject):
        return {'manual_observed':observed_method(manual,subject),'linear_interpolation':interpolate_method(manual,subject,'linear'),'constant_velocity':interpolate_method(manual,subject,'constant_velocity'),'kalman':filtered_method(manual,subject,False),'rts':filtered_method(manual,subject,True)}
    hs=subject_window(historical_manual);hm=methods(historical_manual,hs)
    # Old np.interp clamped filter endpoints; retain only here as a historical baseline.
    from clearance_metrics import kalman_motion
    for name in ('kalman','rts'):
        known=sorted(kalman_motion(historical_manual,rts=name=='rts').values(),key=lambda r:r['t'])
        if known:
            target=np.array([r['t'] for r in hs]); xy=np.array([r['xy'] for r in known]);times=[r['t'] for r in known]
            coords=np.column_stack([np.interp(target,times,xy[:,i]) for i in (0,1)])
            hm[name]=with_velocity([{**r,'xy':p,'observation_status':'historical_clamped_filter_not_directly_observed'} for r,p in zip(hs,coords)])
    historical=[metrics_for(hs,car,axis,name) for name,car in hm.items()]
    write(out/'historical_reproduction.csv',historical)
    manual=manual_samples(annotations,np.array(g['H']),fps);subject=subject_window(manual);mm=methods(manual,subject)
    repaired=[metrics_for(subject,car,axis,name) for name,car in mm.items()];write(out/'reconstruction_methods.csv',diagnostic_rows(repaired))
    # Exact rows sufficient to reproduce every fitted coordinate and velocity.
    observations=[]
    for method,car in {**{'historical_'+k:v for k,v in hm.items()},**mm}.items():
        subj={r['frame']:r for r in (hs if method.startswith('historical_') else subject)}
        for r in car:
            a=subj[r['frame']]
            observations.append(dict(method=method,frame=r['frame'],car_t_s=r['t'],subject_t_s=a['t'],
                car_x_unvalidated=r['xy'][0],car_y_unvalidated=r['xy'][1],car_vx_unvalidated=r['velocity'][0],car_vy_unvalidated=r['velocity'][1],
                subject_x_unvalidated=a['xy'][0],subject_y_unvalidated=a['xy'][1],subject_vx_unvalidated=a['velocity'][0],subject_vy_unvalidated=a['velocity'][1],
                observation_status=r.get('observation_status','manual_observed_contact_proxy_visibility_unverified'),
                physical_status='unvalidated_learned_plane_assumed_footprints'))
    write(out/'reconstruction_inputs.csv',observations)
    # Timestamp mismatch audit; playback click times never override selected frame.
    write(out/'clock_alignment_audit.csv',[dict(event_id='white_suv',frame=391,nominal_source_time='2019-07-10 12:40:21.013',burned_in_source_clock_visual='2019-07-10 12:40:23',status='absolute_alignment_unresolved'),dict(event_id='dark_car',frame=445,nominal_source_time='2019-07-10 12:53:52.815',burned_in_source_clock_visual='2019-07-10 12:53:54',status='absolute_alignment_unresolved'),dict(event_id='pedestrian_car',frame=1405,nominal_clip_s=1404/fps,nominal_source_time='2019-07-10 17:08:46.847',burned_in_source_clock_visual='2019-07-10 17:08:49',raw_csv_clock_basis='12:08 from saved run log; inconsistent with source hour',status='absolute_alignment_unresolved; camera label second-resolution; no automatic correction applied')])
    write(out/'timestamp_audit.csv',[dict(frame=r['frame'],object=r['object'],click_time_s=r['clip_seconds'],frame_time_s=(int(r['frame'])-1)/fps,delta_s=float(r['clip_seconds'])-(int(r['frame'])-1)/fps) for r in annotations])
    _,_,sensitive_paths=load_task(out/'inputs/pedestrian_sensitive')
    car_auto=sensitive_paths.get(('car','68'),[]);ca={r['frame']:r for r in car_auto}
    comparisons=[]
    for r in manual:
        auto=ca.get(r['frame']);nearest=min(car_auto,key=lambda a:abs(a['frame']-r['frame'])) if car_auto else None
        comparisons.append(dict(frame=r['frame'],manual_x_px=r['pixel'][0],manual_y_px=r['pixel'][1],automatic_same_frame=auto is not None,
            same_frame_point_difference_px=np.linalg.norm(auto['pixel']-r['pixel']) if auto else None,
            nearest_auto_frame=nearest['frame'] if nearest else None,nearest_auto_time_offset_s=nearest['t']-r['t'] if nearest else None,
            status='comparable_contact_proxies_only' if auto else 'no_synchronized_car68_point_do_not_compare_different_times'))
    write(out/'manual_auto_comparison.csv',comparisons)
    speed_context=[]
    for name,rr in [('pedestrian1_reference',[r for r in paths[('pedestrian','1')] if 42<=r['t']<=48]),('car68_sensitive_pre_loss',car_auto)]:
        tt=np.array([r['t'] for r in rr]);pp=np.array([r['pixel'] for r in rr])
        speed_context.append(dict(object=name,estimate=float(np.linalg.norm(np.polyfit(tt-tt.mean(),pp,1)[0])),units='px/s; fitted image velocity magnitude',start_clip_s=tt.min(),end_clip_s=tt.max(),samples=len(rr),validity='image context only; perspective dependent; not physical speed'))
    write(out/'object_speed_context.csv',speed_context)
    visibility=[]
    for r in paths[('pedestrian','1')]:
        if 42<=r['t']<=48:
            visibility.append(dict(frame=r['frame'],t_s=r['t'],pedestrian_status='observed',car68_status='observed' if r['frame'] in ca else 'not_observable_automatic_track_lost',manual_car_status='manual_observed_contact_proxy_visibility_unverified' if r['frame'] in {q['frame'] for q in manual} else 'not_observed',occlusion_note='track loss is not proof of no car; hidden trajectory is model-based'))
    write(out/'occlusion_observations.csv',visibility)
    # Conditional engineering perturbations, NOT calibrated uncertainty distributions.
    scenarios=[('baseline',None,0),('click_x_minus3','x',-3),('click_x_plus3','x',3),('click_y_minus3','y',-3),('click_y_plus3','y',3),('dimension_0.8','dim',.8),('dimension_1.2','dim',1.2),('lateral_map_0.8','map',.8),('lateral_map_1.2','map',1.2),('acceleration_minus2','acc',-2),('acceleration_plus2','acc',2),('pet_cell_0.25','cell',.25),('pet_cell_1.0','cell',1.),('car_time_minus_frame','time',-1/fps),('car_time_plus_frame','time',1/fps),('fit_first_half','fit',.5)]
    sensitivity=[]
    for name,kind,value in scenarios:
        sample=copy.deepcopy(manual);ss=copy.deepcopy(subject);dims=1.;cell=.5
        if kind in ('x','y'):
            for r in sample:r['pixel'][0 if kind=='x' else 1]+=value;r['xy']=project(g['H'],[r['pixel']])[0]
        if kind=='time':
            for r in sample:r['t']+=value
        if kind=='dim':dims=value
        if kind=='cell':cell=value
        if kind=='map':
            transform=np.outer(axis,axis)+value*np.outer([-axis[1],axis[0]],[-axis[1],axis[0]])
            for r in sample+ss:r['xy']=r['xy']@transform
            ss=with_velocity(ss)
        if kind=='fit':sample=sample[:max(3,len(sample)//2)]
        variants=methods(sample,ss)
        if kind=='acc':
            for label,car in variants.items():
                if label!='constant_velocity':continue
                for r in car:
                    dt=r['t']-sample[0]['t'];r['xy']=r['xy']+.5*value*dt**2*axis;r['velocity']=r['velocity']+value*dt*axis
        for label,car in variants.items():
            result=metrics_for(ss,car,axis,label,dimension_scale=dims,cell=cell)
            sensitivity.append(dict(scenario=name,assumption=f'{kind}={value}',**result))
    write(out/'sensitivity_metrics.csv',diagnostic_rows(sensitivity))
    trajectory_plot(out/'assets/pedestrian_trajectory.png','Pedestrian 1 / car 68; manual clicks after automatic track loss',
        [r for r in paths[('pedestrian','1')] if 42<=r['t']<=48],car_auto,annotations)
    # Manual image point distance: exact selected frame only, no interpolated pixels.
    ap={r['frame']:r for r in annotations if r['object']=='pedestrian'}
    point_rows=[dict(frame=r['frame'],distance_px=np.hypot(float(r['x_px'])-float(ap[r['frame']]['x_px']),float(r['y_px'])-float(ap[r['frame']]['y_px']))) for r in annotations if r['object']=='car' and r['frame'] in ap]
    write(out/'pedestrian_pixel_separation.csv',point_rows)
    event=dict.fromkeys(FIELDS,'');cv=next(r for r in repaired if r['method']=='constant_velocity');oldcv=next(r for r in historical if r['method']=='constant_velocity');oldobs=historical[0]
    event.update(event_id='pedestrian_car',event_type='pedestrian_crossing',clip_id='colonial_1708_pedestrian_car',
        start_time='2019-07-10 17:08:46.535',end_time='2019-07-10 17:08:46.836',object_ids='pedestrian 1 reference / car 68 sensitive (same clip)',
        track_source='inputs/pedestrian reference pedestrian + inputs/pedestrian_sensitive car68 + manual_occlusion_points.csv',observation_status='automatic pedestrian observed; manual car contact proxies; interpolated/modelled through occlusion',
        tracking_quality=f'sensitive car68 {len(car_auto)} pre-loss observations; pedestrian 9 observations in selected historical event interval',
        calibration_status='not_calibrated_lateral_scale',calibration_support='learned-plane transfer; physical overlap not established',
        min_image_gap_px=min(r['distance_px'] for r in point_rows),image_gap_method=f'minimum manual contact-proxy Euclidean distance at {len(point_rows)} identical frame IDs; not edge clearance',
        ttc_method='physical TTC unavailable; optional surrogate is constant-velocity fit + swept assumed road-aligned rectangles; horizon 5 s',
        pet_method='sampled assumed-footprint shared cells 0.5 learned units; max gap 0.20 s; no shared cells found',
        metric_eligibility='pixel diagnostic eligible; surrogate TTC conditional only; physical TTC/PET ineligible',
        historical_ttc_s='.375',historical_pet_s='.294',reproduced_surrogate_ttc_s=cv['min_ttc_s'],reproduced_surrogate_pet_s='',
        null_reason=json.dumps(dict(min_clearance_m='not_calibrated: scale/footprints unverified; crossing is not lateral passing',ttc_s='failed_eligibility: surrogate model uses unvalidated mapping and assumed dimensions',pet_s='failed_eligibility: no shared occupancy cells; historical 0.294 is coverage fraction',estimated_speed='not_calibrated: manual/automatic car proxies not matched; no independent scale',relative_speed_est='not_observable: no synchronized car68 track in event interval')),
        screening_flags='visual_interaction_candidate',threshold_config=json.dumps(config_global,sort_keys=True),reviewed_classification='potential_conflict',
        review_evidence='HANDOFF.md; inputs/pedestrian; manual_occlusion_points.csv; historical_reproduction.csv; reconstruction_inputs.csv',
        uncertainty_notes='Close interaction from prior visual review; no evasive-action adjudication. Manual clicks lack per-frame visibility labels. Historical PET 0.294 misreads coverage 5/17; no eligible reproduced PET. Conditional sensitivity is not a near-miss probability.',event_window_basis='prior visual event selection; filename-inferred clock')
    return event,historical,repaired,sensitivity,oldobs,oldcv


def audit_sources(repo,out):
    """Exhaustive numeric comparison/default expressions, with exact source lines.

    Includes non-threshold numerical constants; human map explains active paths.
    """
    names=['clearance_metrics.py','clearance_pilot.py','clearance_review.py','run_batch4.sh','run_batch5.py','research_worker.py','run_xclip_colonial_v19.slurm','xclip_overlay_v19_colonial.py','speed_research.py']
    sources=[repo/'vision3/best/test_colonial/code'/n for n in names]
    sources += [repo/'pipeline'/n for n in ('manual_occlusion_metrics.py','passing_clearance.py','vru_tracker.py','goal4_conflict.py')]
    # Actual inference worker selected by execute/imports, not the similarly named standalone tracker.
    worker=repo/'vision3/best/test_colonial/code/research_worker.py'
    if worker.exists():
        import re
        for name in re.findall(r'[\w.-]+\.py',worker.read_text()):
            p=worker.parent/name
            if p.is_file():sources.append(p)
    sources=list(dict.fromkeys(p for p in sources if p.exists()));rows=[]
    for p in sources:
        lines=p.read_text().splitlines()
        if p.suffix=='.py':
            tree=ast.parse(p.read_text())
            for n in ast.walk(tree):
                if isinstance(n,(ast.Compare,ast.Assign,ast.AnnAssign,ast.FunctionDef,ast.Call)):
                    text=ast.get_source_segment(p.read_text(),n) or ''
                    if isinstance(n,ast.FunctionDef):text=lines[n.lineno-1]
                    if len(text)>600 and not isinstance(n,(ast.FunctionDef,ast.Call)):continue
                    if len(text)>2000:continue
                    if any(c.isdigit() for c in text):rows.append(dict(source=str(p.relative_to(repo)),line=n.lineno,expression=text.replace('\n',' '),status='existing_source_expression; includes defaults/constants not only thresholds'))
        else:
            rows.extend(dict(source=str(p.relative_to(repo)),line=i,expression=line,status='existing_shell_configuration') for i,line in enumerate(lines,1) if any(c.isdigit() for c in line) and not line.lstrip().startswith('#'))
    write(out/'threshold_source_inventory.csv',rows)
    return sources


def build_code_map(repo,out):
    code='vision3/best/test_colonial/code/'
    entries=[
        ('clearance_pilot.py','BIC_MIN_SEC','Detector/task overrides: reference DET_CONF/TRACK_THR .25, sensitive .15; BIC_MIN_SEC 1.5/.3 s, PED_MIN_SEC 3 s, STITCH_SEC .5 s, STITCH_PX 60 px, LOST_SEC .3 s'),
        ('xclip_overlay_v19_colonial.py','minimum_matching_threshold=0.8','ByteTrack matching .8, buffer=int(fps*lost_sec)'),
        ('xclip_overlay_v19_colonial.py','--veh-min"','Vehicle defaults: 15 observations, displacement 40 px; see adjacent argument lines and inventory for all class filters'),
        ('xclip_overlay_v19_colonial.py','--veh-min-mean-conf','Vehicle mean confidence .45, aspect ratio .35–4.5, straightness .35; detector candidates still require visual identity validation'),
        ('xclip_overlay_v19_colonial.py','--coast-sec','Person optical-flow coast 2 s, eligible after .7 s, box EMA .5; prepare excludes coasted metric samples'),
        ('xclip_overlay_v19_colonial.py','--confirm','Classification defaults: confirm 2, window 30 frames, min-frames 8, stride 3, pad .6, EMA .5; all additional CLI defaults in inventory'),
        ('clearance_metrics.py',"abs(q[:, 2]) < 1e-8",'Projection denominator epsilon 1e-8'),
        ('clearance_metrics.py',"pointPolygonTest",'Inside/on support hull: polygon test >=0'),
        ('clearance_metrics.py','len(rr) < 5','Road axis: >=5 vehicle points, displacement >2 learned units, >=2 moving tracks'),
        ('clearance_metrics.py','cuts = np.r_','Local fit: split gaps >.20 s; >=3 points, >=.10 s; default window .5 s'),
        ('clearance_metrics.py','def kalman_motion','Kalman: position sigma .25, acceleration sigma 2, initial velocity sigma 5; >.20 s restarts and .10 s/3-point warmup; engineering assumptions'),
        ('clearance_metrics.py','def collision_ttc','TTC horizon 5 s; per-axis stationary epsilon 1e-9; simultaneous future rectangle overlap required'),
        ('clearance_metrics.py','def pet_cells','PET cell .5 learned units, max occupancy gap .20 s, grid cap 2000 cells; sampled interval endpoints, no interpolation'),
        ('clearance_metrics.py','def dimensions','Assumed rectangles: cyclist 1.8×.8 baseline (width .6/1 sensitivity), pedestrian .7×.6, car 4.5×1.8, bus 12×2.5, truck 8×2.5 learned units'),
        ('clearance_metrics.py','alongside = abs(rel','Alongside abs(along-track separation) <= summed half lengths; no validated physical edge recovery'),
        ('clearance_metrics.py',"same_direction=bool",'Same direction: same along-axis velocity sign and each abs velocity >.5 learned units/s'),
        ('clearance_metrics.py',"for r in samples) > 20",'Broad candidate cutoff centre separation >20 learned units; not a near-miss cutoff'),
        ('clearance_metrics.py','overtake = any','Overtake requires order reversal from below -half-length to above +half-length in a same-direction run, split >.20 s'),
        ('clearance_metrics.py','baseline=dict','12 scenarios: window .25/.5/1 s, width .6/.8/1, scale .8/1/1.2, strict/transfer and local/Kalman/RTS'),
        ('clearance_pilot.py',"for metric,values in",'Historical threshold sweep: clearance .5/1/1.5 learned m; TTC 1/1.5/2 s; PET .5/1/1.5 s, strict <. Historical only, not adopted'),
        ('clearance_review.py',"if rule=='distance'",'Historical distance/PET and lateral screens <1 learned m / <1 s; not adopted physical criteria'),
    ]
    rows=[]
    for name,needle,meaning in entries:
        lines=(repo/code/name).read_text().splitlines();matches=[i for i,l in enumerate(lines,1) if needle in l]
        rows.append(dict(setting=meaning,source=f'{code}{name}:{matches[0]}' if matches else f'{code}{name} (see inventory)',status='existing; historical safety thresholds not adopted'))
    rows.extend([
        dict(setting='New active numerical screens: all null/unset; no adopted TTC/PET or metre near-miss cutoff',source='pipeline/near_miss_screening.json',status='new configuration'),
        dict(setting='Sensitivity TTC .25/.375/.5 s; PET .25/.5/1 s; strict <; engineering examples only',source='pipeline/near_miss_screening.json',status='new conditional sensitivity, not validated safety thresholds'),
        dict(setting='Click offsets ±3 px, time ±1 frame, dimensions .8/1.2, lateral map .8/1.2, acceleration ±2 learned units/s², PET cells .25/1, first-half fit',source='pipeline/generate_near_miss_report.py:reconstruction',status='new assumption scenarios; not measured uncertainty')])
    write(out/'thresholds.csv',rows)
    effective=[]
    for task in (repo/BATCH).glob('*_reference'):
        for detector in ('reference','sensitive'):
            p=task.parent/(task.name.rsplit('_',1)[0]+'_'+detector)/'pipeline_task.json'
            if p.exists():
                d=json.loads(p.read_text())
                effective.extend(dict(task=p.parent.name,setting=k,value=v,source=str(p.relative_to(repo))) for k,v in d['env'].items())
    for folder in ('pedestrian','pedestrian_sensitive'):
        p=out/'inputs'/folder/'pipeline_task.json'
        if p.exists():
            d=json.loads(p.read_text())
            effective.extend(dict(task=d['key'],setting=k,value=v,source=str(p)) for k,v in d['env'].items())
    write(out/'effective_task_configuration.csv',effective)
    text="""# Code-path audit and exact thresholds

The active Colonial pilot calls `clearance_pilot.infer` → `research_worker.execute` → `run_xclip_colonial_v19.slurm` → `xclip_overlay_v19_colonial.main`. RT-DETR detections are class filtered, then separate person/vehicle ByteTrack instances run with `make_tracker`; `IdStitcher.resolve_frame` stitches person IDs, X-CLIP and detector voting determine person identity. `init_flow`/`flow_step` coast person boxes across short loss. Vehicle trajectories export detector-backed boxes with bottom-centre contacts. `pipeline/vru_tracker.py` and `pipeline/goal4_conflict.py` are alternate legacy paths, not the code that produced these pilot returns. The latter has unsourced hard-coded TTC 1.5 s / PET 1 s and 5 m /120 px radii; those settings are audited, not adopted here.

`clearance_metrics.prepare` drops coasted rows, resolves candidate classes from track metadata, projects bottom-centres with saved H, tests support hull, and uses one-based frame time `(frame-1)/fps`. `local_motion` splits gaps rather than interpolating; `kalman_motion` optionally smooths observed samples with RTS. `road_axis` estimates the dominant vehicle axis. `pair_metrics` synchronizes frames, applies strict hull support, assumes rectangles, computes alongside and direction tests, swept TTC, predicted closest approach and sampled shared-cell PET. Alongside and direction are different tests: the original function reports direction/overtake but does not make direction a prerequisite for all distance diagnostics.

`pair_metrics` previously returned None with no reason for <3 synchronized eligible points or >20 learned-unit separation. `diagnose_pair` now exports raw-frame and pair eligibility before those gates; `clearance_pilot.analyze` writes both tables. None remains part of the legacy metric API; candidates in the repaired event export no longer disappear with metric failures. The bottom box-edge projection is explicitly a proxy, not a physical footprint. No axis/sign bug was found that would justify removing the alongside gate. Real passes fail because projected contact/assumed footprint geometry does not represent the visible passing edges: 58/98 shared samples, same direction throughout, no modeled longitudinal overlap, all outside cyclist support.

Calibration comes from `speed_research.iccv_calibration`, reused in `reports/cluster_returns/20261024/colonial_speed_47545558_report_rebuilt/iccv2021/calibration.json`: author commit 80b8bc4964eddfda32c40e6d1c8fe8b62f777f55, 28 car tracks, 458 boxes; `geometry_check_passed` checks numerical geometry, not independent physical lateral accuracy. Sidewalk/road plane transfer is unverified. No surveyed matched lateral control points or validated lateral error bounds exist. H and its digest are saved in each task's geometry.json. Prior speed agreement shares H and does not establish scale.

`manual_occlusion_metrics` uses saved pedestrian 1 and manual car clicks. Repaired default uses selected-frame timestamps; historical click-time replay is explicit. `filtered_method` now removes targets outside the filtered support instead of silently clamping np.interp endpoints. Model/interpolated outputs have explicit status; manual clicks are contact proxies with unverified visibility, never ground truth of hidden surfaces. Historical reference pedestrian reconstruction reproduces TTC .3745297 s; claimed PET .294 is actually coverage 5/17. The relevant visible car68 is in the sensitive detector namespace; reference car68 occurs around clip +58.8 s and is unrelated. Saved raw pedestrian CSV clocks are five hours earlier than source manifest inference; report clocks come from the manifest/selection and calculations use frame time.

`clearance_pilot.report`, `review_pairs`, `clearance_review.screening_reports` historically compare scenario/detector rows, not unique physical events. The new `generate_near_miss_report` emits exactly two reviewed visual passes and one reviewed crossing, with explicit exclusions for sensitive wheel track21 and the middle no-pass sequence. This is a bounded reviewed-pilot event register, not an unvalidated cross-camera automatic identity merger. New unseen footage requires identity review before event registration. Numerical screening is configured separately and never edits reviewed classifications. Review protocol: verified pass with unresolved hazard → indeterminate; prior visually close crossing with unresolved occlusion → potential_conflict; no confirmed label without an independent documented safety adjudication rule. Evasive action/barrier geometry have not been fully adjudicated.

## Threshold table

All existing settings remain distinguished from new settings. Units called 'learned' below are not validated metres. The exhaustive companion `threshold_source_inventory.csv` contains numeric comparison/assignment/default expressions with exact file and line, including all detector/classification arguments and alternate legacy paths. `effective_task_configuration.csv` records saved detector task overrides (defaults may differ from effective values). No published near-miss threshold was adopted; no new research cutoff is asserted.

"""+table(rows,['setting','source','status'])+"""

## Exports and tests

`event_metrics.csv` uses empty CSV cells for null and metric-specific JSON reasons: not_applicable, not_observable, not_calibrated, failed_eligibility; frame/pair tables separately expose not_enough_track_overlap. Zero is retained only for actual modeled overlap (e.g. sensitivity), never for missing values. `min_image_gap_px` is accompanied by image_gap_method; pedestrian point separation and cyclist horizontal edges are different proxies. `historical_*` fields preserve earlier reported numbers; `reproduced_surrogate_*` fields remain distinct from physically eligible times. `reconstruction_inputs.csv` preserves exact model rows and methods. `occlusion_observations.csv` describes observed/missing car states, `timestamp_audit.csv` audits click timing. Visual review has automatic/manual markers, time labels and support hull.

`tests/test_near_miss_pipeline.py` regenerates outputs from saved evidence and covers the two retained passes, excluded wheel/no-car sequences, namespace/occlusion, physical nulls, PET column error, exact TTC inputs, frame alignment, clamped endpoints, non-collision course TTC, unique event count, separate screen/review, conditional sensitivity and input digests. Original annotations, returned workbooks/CSV outputs and HANDOFF.md are preserved.
"""
    (out/'CODE_PATH_MAP.md').write_text(text)


def visuals(out,events):
    fig,axes=plt.subplots(1,2,figsize=(11,4))
    names=[e['event_id'] for e in events];vals=[float(e['min_image_gap_px']) for e in events]
    axes[0].set_ylim(0,max(vals)*1.2)
    axes[0].bar(names,vals,color=['#2166ac','#2166ac','#d6604d']);axes[0].set(ylabel='Selected-frame separation (px)',title='Image proxies: different definitions, view-dependent')
    for i,v in enumerate(vals):axes[0].text(i,v+1,f'{v:.2f}',ha='center')
    axes[1].set(xlim=(-.5,2.5),ylim=(0,.6),xticks=range(3),xticklabels=names,ylabel='Surrogate time (s)',title='Physical TTC / PET: missing for all events')
    for i,e in enumerate(events):
        if finite(e['reproduced_surrogate_ttc_s']):
            axes[1].scatter(i,float(e['reproduced_surrogate_ttc_s']),marker='D',color='#d6604d',label='Conditional CV TTC (unvalidated plane)')
            axes[1].text(i,.52,'PET: missing',ha='center',fontsize=8)
        else:axes[1].text(i,.25,'TTC: N/A\nPET: N/A',ha='center',fontsize=8)
    axes[1].legend(fontsize=7,loc='lower center')
    for ax in axes:ax.tick_params(axis='x',labelrotation=15);ax.grid(axis='y',alpha=.2)
    fig.tight_layout();fig.savefig(out/'assets/event_metrics.png',dpi=160);plt.close(fig)


def build_report(repo,out,config):
    global config_global
    config_global=config
    out.mkdir(parents=True,exist_ok=True);(out/'assets').mkdir(exist_ok=True)
    if not (out/'inputs/pedestrian').is_dir():
        raise FileNotFoundError('Preserved pedestrian inputs required at '+str(out/'inputs/pedestrian'))
    evidence=list((repo/BATCH).rglob('*'));evidence += list((repo/FINAL).rglob('*'))
    evidence += [repo/'HANDOFF.md',repo/'clearance_edge_annotations_completed.csv',repo/'manual_occlusion_points.csv']
    evidence += list((out/'inputs').rglob('*'))
    evidence=[p for p in evidence if p.is_file()];before={str(p):digest(p) for p in evidence}
    events,pairs=cyclist_events(repo,out)
    ped,historical,repaired,sensitivity,oldobs,oldcv=reconstruction(repo,out);events.append(ped)
    write(out/'event_metrics.csv',events,FIELDS)
    summary=[]
    def add(metric,value,denominator,reason):summary.append(dict(metric=metric,value=value,denominator=denominator,reason=reason))
    add('unique_candidate_encounters',3,'3 reviewed interactions','2 real cyclist passes + 1 pedestrian crossing; variants collapsed using explicit visual event IDs')
    add('visually_verified_passes',2,3,'Selected pilot, not a population rate')
    add('visually_reviewed_crossings',1,3,'Prior review evidence; partly occluded')
    for key,label in [('ttc_s','eligible_physical_ttc'),('pet_s','eligible_physical_pet'),('min_image_gap_px','image_diagnostic'),('min_clearance_m','calibrated_metre_clearance'),('reproduced_surrogate_ttc_s','conditional_surrogate_ttc')]:add(label,sum(finite(e[key]) for e in events),3,'Eligibility and units in event_metrics.csv')
    add('reproduced_surrogate_pet',0,3,'No shared assumed-footprint occupancy cells; historical .294 was coverage')
    add('potential_conflict',1,3,'Pedestrian: prior visible close interaction, no calibrated safety adjudication')
    add('confirmed_under_defined_protocol',0,3,'No validated adjudication rule; zero confirmed does not establish no near misses occurred')
    add('indeterminate',2,3,'Cyclist passes established; near-miss status indeterminate')
    add('reviewed_false_car_detections',1,'1 specifically reviewed wheel alarm','Track 21 sensitive namespace; selected false-positive regression, not population false-alarm rate')
    add('middle_cyclist_no_pass',1,'1 reviewed comparison sequence','Not an event row')
    add('historical_diagnostic_rows',len(read(repo/BATCH/'all_interactions.csv')),'6 detector tasks','Repeated scenarios, not physical events')
    for field in ('min_clearance_m','ttc_s','pet_s'):
        counts=Counter(json.loads(e['null_reason'])[field] for e in events if not finite(e[field]))
        for reason,n in counts.items():add('missing_'+field,n,3,reason)
    threshold_rows=[]
    for key in ('ttc_s','pet_s'):
        for value in config['sensitivity_'+key]:
            for e in events:
                surrogate=e['reproduced_surrogate_'+key]
                threshold_rows.append(dict(event_id=e['event_id'],metric=key,threshold_s=value,supported_flag=False,
                    conditional_surrogate_flag=float(surrogate)<value if finite(surrogate) else '',
                    reviewed_classification=e['reviewed_classification'],policy='strict less-than; engineering sensitivity only; unvalidated surrogates cannot trigger supported screening'))
            add(f'supported_{key}_below_{value}',0,3,'No eligible physical times; conditional surrogate flags listed separately')
            add(f'conditional_surrogate_{key}_below_{value}',sum(finite(e['reproduced_surrogate_'+key]) and float(e['reproduced_surrogate_'+key])<value for e in events),sum(finite(e['reproduced_surrogate_'+key]) for e in events),'Engineering example only, not confirmed near miss')
    write(out/'threshold_sensitivity.csv',threshold_rows);write(out/'summary_metrics.csv',summary)
    exclusions=[dict(clip_id='colonial_125350',detector='sensitive',vehicle_id='21',decision='excluded_false_object',reason='visual review: car box on bicycle wheel; never a separate vehicle event'),dict(clip_id='colonial_125311',detector='reference_and_sensitive',vehicle_id='',decision='not_a_pass_in_reviewed_interval',reason='three unusable manual edge rows: no nearby passing car')]
    write(out/'excluded_candidates.csv',exclusions)
    sources=audit_sources(repo,out);build_code_map(repo,out);visuals(out,events)
    comparisons=[]
    for e in events[:2]:comparisons.append(dict(event=e['event_id'],previous='0 strict eligible pairs; pass omitted by geometry gate',repaired='retained visual interaction candidate; metre/TTC/PET N/A',why='candidate identity separated from physical metric eligibility',status='observed selected pass; exploratory speed'))
    comparisons.append(dict(event='pedestrian_car',previous='reported PET .294 s; CV TTC .375 s',repaired=f'PET N/A; historical CV TTC {fmt(oldcv["min_ttc_s"])} s; frame-aligned CV TTC {fmt(ped["reproduced_surrogate_ttc_s"])} s conditional',why=f'.294117647 is coverage {oldobs["samples"]}/17, not PET; frame time replaces click playback time; filtered endpoint clamping removed',status='reconstructed diagnostic, physical validity unverified'))
    write(out/'before_after.csv',comparisons)
    ranges=[]
    for method in sorted({r['method'] for r in sensitivity}):
        rr=[r for r in sensitivity if r['method']==method]
        for key in ('min_ttc_s','pet_s'):
            vals=[float(r[key]) for r in rr if finite(r[key])]
            ranges.append(dict(method=method,metric=key,eligible_scenarios=len(vals),scenario_count=len(rr),minimum_s=min(vals) if vals else '',maximum_s=max(vals) if vals else '',interpretation='conditional engineering perturbations; missing scenarios remain missing; not statistical confidence interval'))
    write(out/'sensitivity_summary.csv',ranges)
    # Every input digest is verified again after all computation.
    provenance=[dict(path=str(Path(p).relative_to(repo)) if Path(p).is_relative_to(repo) else p,sha256=h,unchanged=digest(p)==h) for p,h in before.items()]
    assert all(r['unchanged'] for r in provenance)
    write(out/'provenance.csv',provenance)
    origin=[]
    download=Path('/Users/rithika/Downloads/CLEARANCE_PILOT_20261109_203226_368050')
    for folder,task_name in [('pedestrian','colonial_1708_pedestrian_car_reference'),('pedestrian_sensitive','colonial_1708_pedestrian_car_sensitive')]:
        for p in (out/'inputs'/folder).iterdir():
            original=download/task_name/p.name
            origin.append(dict(copy=str(p),original=str(original),sha256=digest(p),matches_original=digest(original)==digest(p) if original.exists() else 'original_not_available'))
    write(out/'input_origins.csv',origin)
    (out/'run_config.json').write_text(json.dumps(dict(config=config,fps=json.loads((out/'inputs/pedestrian/run_log.json').read_text())['fps'],road_axis=json.loads((out/'inputs/pedestrian/geometry.json').read_text())['road_axis'],python=sys.version,numpy=np.__version__,source_sha256={str(p.relative_to(repo)):digest(p) for p in sources+[repo/'pipeline/generate_near_miss_report.py',repo/'pipeline/near_miss_screening.json']}),indent=2))
    event_table=[dict(event=e['event_id'],time=e['start_time'],IDs=e['object_ids'],speed_mph=fmt(e['estimated_speed']),relative_px_s=fmt(e['relative_speed_est']),image_px=fmt(e['min_image_gap_px']),clearance_m='N/A',physical_TTC_s='N/A',physical_PET_s='N/A',conditional_TTC_s=fmt(e['reproduced_surrogate_ttc_s']),review=e['reviewed_classification']) for e in events]
    report=f'''# Colonial near-miss pilot: numerical results

Two visually reviewed cyclist passes and one pedestrian crossing are retained as **3 unique interaction candidates**. Physical metre clearance is unavailable for all three. No confirmed near miss is established under a validated adjudication protocol; this does not show that no near misses occurred. This selected sample cannot estimate a population rate.

{table(event_table,list(event_table[0]))}

Image values have different meanings: cyclist minima are **6 px and 20 px among three selected horizontal edge annotations each**, not continuous minima or perpendicular passing clearance. The pedestrian value is a selected-frame Euclidean contact-proxy distance, not edge clearance. Relative px/s values are image velocity fits over synchronized observations, not road speeds. Approximate cyclist mph values share the learned map with manual speed estimates and do not validate physical scale. Event timestamps are inferred from source filenames and selected annotation windows, not independently verified clocks.

## Pedestrian discrepancy and reproducibility

The historical **reported** PET **0.294 s** remains recorded in `historical_pet_s` for provenance, but it is **not reproduced**. Running the saved algorithm and observations gives **blank PET** for all five methods. **0.294117647 = 5/17 is the manual-observed coverage_fraction**, immediately after the blank PET column. Historical CV TTC reproduces as **{fmt(oldcv['min_ttc_s'])} s**. Frame-aligned reconstruction gives **{fmt(ped['reproduced_surrogate_ttc_s'])} s**, conditional on the same unvalidated mapping and assumed footprints. It is exported separately from eligible physical `ttc_s`, which remains null. Manual clicks carry no reliable per-frame hidden/visible labels; a contact proxy during overlap is not verified observation of hidden ground contact.

{table(repaired,['method','samples','min_ttc_s','pet_s','coverage_fraction','first_common_s','last_common_s'])}

Historical exact reproduction: `historical_reproduction.csv`. Exact input positions, velocities, timestamps and observation status: `reconstruction_inputs.csv`. PET uses 0.5 learned-unit shared cells and occupancy spans split at gaps >0.20 s; no sub-frame entry/exit interpolation. TTC sweeps road-aligned rectangles with constant velocity/orientation over 5 s; pedestrian 0.7×0.6 and car 4.5×1.8 learned-unit dimensions are assumptions, not calibrated physical footprints. No crossing lateral-passing clearance is reported.

Manual car clicks and sensitive car68 detector bottom-centres have three identical-frame comparisons: **29.14, 37.61 and 72.69 px** differences. These compare different contact proxies and do not validate reconstruction accuracy. The car track ends at one-based frame **1395** (clip +46.513 s); later manually reconstructed positions are not automatic observations. Approximate image speeds over the saved pre-loss/subject context windows are in `object_speed_context.csv`, with units and frame windows; road speed is unavailable.

## Before and after

{table(comparisons,list(comparisons[0]))}

Both cyclist pairs have actual synchronized tracks, **{pairs[0]['simultaneous_samples']} and {pairs[1]['simultaneous_samples']}** shared observations, all same-direction under the existing learned-plane test, **zero alongside samples and zero supported shared samples**. The assumed rectangles around projected detector bottom-centres reject the visual passes; this is geometric eligibility failure, not a blanket tracking failure. `edge_proxy_comparison.csv` shows how annotated visible edges differ from detector box proxies; white-SUV selected frame 409 lacks a simultaneous saved vehicle point despite the manually visible edge, a local observation gap distinct from the pair-wide geometry rejection. The alongside limit is **3.15 learned units**; fitted along-track offsets range **−18.803 to −5.817** (white SUV) and **−21.874 to −4.105** (dark car), so neither reaches the assumed overlap interval. These are diagnostic coordinates, not validated metres. Gates are preserved for physical metrics while evidence-based candidates survive.

## Conditional sensitivity (seconds)

{table(ranges,['method','metric','eligible_scenarios','scenario_count','minimum_s','maximum_s'])}

Sixteen one-factor scenarios include car-click offsets ±3 px, frame-time shifts ±1 frame, dimension factors 0.8/1.2, lateral mapping factors 0.8/1.2, constant-velocity acceleration perturbations ±2 learned units/s², first-half fit, and PET cells 0.25/1.0. These are explicit engineering assumptions, not empirically calibrated uncertainty or real-world near-miss probabilities. PET may appear only under changed assumptions; missing values are retained. See `sensitivity_metrics.csv` for each row and `sensitivity_summary.csv` for conditional ranges. Automatic/manual car comparison has no permission to compare points at different times; see `manual_auto_comparison.csv`. The automatic track-loss span is explicit in `occlusion_observations.csv`. Reference car68 is an unrelated late track; the relevant car68 namespace is sensitive. Saved pedestrian CSV clocks incorrectly read 12:08 while the source manifest identifies 17:08; frame times drive calculations and filename-inferred source times drive this report. Visual inspection of pedestrian source frame 1405 shows burned-in camera clock **17:08:49**, whereas nominal manifest+frame timing gives **17:08:46.847**. Selected cyclist frames also have nominal/burned-in clock disagreement (white frame 391: 12:40:21.013 versus 12:40:23; dark frame 445: 12:53:52.815 versus 12:53:54). Absolute clock alignment is therefore unresolved (not a validated 2.153 s correction, because the burned-in label is second-resolution). Relative TTC calculations do not use these absolute clock labels. See `clock_alignment_audit.csv`.

## Aggregate counts and screening

{table(summary,['metric','value','denominator','reason'])}

Default numerical screening thresholds are **unset** (`pipeline/near_miss_screening.json`). Visual evidence retains these candidates. No fixed metre screen is enabled. The time thresholds in `threshold_sensitivity.csv` are labeled engineering examples only, with strict `<` comparisons. Changing settings changes screening fields only, never reviewed labels. Conditional surrogate flags are distinct from supported flags. Review labels use `indeterminate` for the two real passes and `potential_conflict` for the close pedestrian crossing based on prior visual evidence; no validated confirmation rule or evasive-action finding is asserted. Track 21 is excluded as a false car on a wheel; the middle cyclist is excluded as a no-pass comparison. The 47 historical scenario rows are not 47 events.

## Visuals and trace

![White SUV selected closest annotated edge frame](assets/white_suv_selected_frame.jpg)
![Dark car selected closest annotated edge frame](assets/dark_car_selected_frame.jpg)
![Pedestrian closest manual point frame](assets/pedestrian_car_selected_frame.jpg)

![White SUV synchronized trajectory and closest sample](assets/white_suv_trajectory.png)
![Dark car synchronized trajectory and closest sample](assets/dark_car_trajectory.png)
![Pedestrian automatic/manual trajectory and track loss](assets/pedestrian_trajectory.png)
![Available event metrics with missing times marked](assets/event_metrics.png)

Open [interactive review](review.html) for synchronized track boxes, timestamp labels, manual clicks, support hull and occlusion diagnostics. Original cyclist frame review remains at `reports/clearance_pilot/final_review_20261109/review.html`. Full frame/pair rejection tables, selected manual-edge comparisons and source file hashes accompany this report.

## Interpretation and smallest additional evidence

The defensible findings are two real cyclist passes with selected image gaps, and a close pedestrian crossing with automatic car track loss and a reproducible conditional TTC diagnostic. Neither the image proximity nor the reconstructed TTC proves a near miss. PET 0.294 s was a reporting error, not measured occupancy timing. No eligible physical clearance, TTC/PET-based safety rate, or collision probability is established.

To unlock physical clearance, reconcile original recording PTS against the burned-in clock for absolute event timestamps; supply independent road-plane control geometry with image correspondences spanning the cyclist paths and lateral direction, with measurement error, plus reviewed ground/near-side object edges. Existing 35-foot and 30-foot longitudinal zone lengths lack matched image endpoints and do not validate lateral scale. No surveyed width is needed to retain candidates or review video. For pedestrian occupancy timing, identify the same physical conflict region for both objects and label visible contact proxies versus hidden positions; a second view or defensible bounded occlusion model would reduce reconstruction uncertainty. More detector/smoothing variants alone cannot supply missing geometry.

## Reproduction and files

From `/Users/rithika/Desktop/objectDetect`:

```sh
python3 pipeline/generate_near_miss_report.py --repo . --out reports/near_miss
python3 -m pytest tests -q
```

Primary exports: `reports/near_miss/event_metrics.csv`, `summary_metrics.csv`, `PROFESSOR_RESULTS.md`, `review.html`, `CODE_PATH_MAP.md`, `threshold_source_inventory.csv`, `provenance.csv`. Pedestrian saved inputs were copied, unchanged, from `/Users/rithika/Downloads/CLEARANCE_PILOT_20261109_203226_368050/colonial_1708_pedestrian_car_reference/` into `reports/near_miss/inputs/pedestrian/`; matching sensitive exports were also preserved in `inputs/pedestrian_sensitive/`. No inference/GPU work or new video experiment is required. Source evidence hashes were checked before and after generation; all {len(provenance)} checked files remained unchanged.
'''
    (out/'PROFESSOR_RESULTS.md').write_text(report)
    build_viewer(repo,out,events)
    print(table(event_table,list(event_table[0])))
    print(f'Wrote {out}; {len(provenance)} evidence hashes unchanged.')


def build_viewer(repo,out,events):
    edges=read(repo/'clearance_edge_annotations_completed.csv');manual=read(repo/'manual_occlusion_points.csv');sections=[]
    for event in events:
        ped=event['event_type']=='pedestrian_crossing';task=out/'inputs/pedestrian' if ped else repo/BATCH/(event['clip_id']+'_reference')
        g,log,paths=load_task(task)
        if ped:
            _,_,sensitive_paths=load_task(out/'inputs/pedestrian_sensitive')
            paths[('car','68')]=sensitive_paths[('car','68')]
        kind='pedestrian' if ped else 'cyclist';vid='68' if ped else '9' if event['event_id']=='white_suv' else '18'
        a=paths[(kind,'1')];b=paths.get(('car',vid),[])
        samples={}
        for name,rr in [('subject',a),('car',b)]:
            for r in rr:
                samples.setdefault(str(r['frame']),{})[name]=dict(x=r['pixel'][0],y=r['pixel'][1],w=r['box_w'],h=r['box_h'],t=r['t'])
        mid=[dict(frame=int(r['frame']),x=float(r['x_px']),y=float(r['y_px']),object=r['object']) for r in manual] if ped else []
        clip=event['clip_id'];video=repo/BATCH/'inputs'/(clip+'.mp4')
        if ped:video=Path('/Users/rithika/Downloads/CLEARANCE_PILOT_20261109_203226_368050/inputs')/(clip+'.mp4')
        # Relative original input path for cyclists; pedestrian video copied for portable review.
        if video.is_file() and ped:
            import shutil
            target=out/'inputs'/video.name
            if not target.exists():shutil.copy2(video,target)
            video=target
        import os
        src=os.path.relpath(video,out)
        if video.is_file():
            import cv2
            frame=1405 if ped else 391 if event['event_id']=='white_suv' else 445
            cap=cv2.VideoCapture(str(video));cap.set(cv2.CAP_PROP_POS_FRAMES,frame-1);ok,img=cap.read();cap.release()
            if ok:
                for name,color in [('subject',(40,220,40)),('car',(255,150,30))]:
                    r=samples.get(str(frame),{}).get(name)
                    if r:
                        x,y,w,h=[r[k] for k in ('x','y','w','h')]
                        cv2.rectangle(img,(round(x-w/2),round(y-h)),(round(x+w/2),round(y)),color,2)
                for r in mid:
                    if r['frame']==frame:cv2.drawMarker(img,(round(r['x']),round(r['y'])),(0,0,255) if r['object']=='car' else (0,180,255),cv2.MARKER_CROSS,15,2)
                if not ped:
                    e=next(e for e in edges if e['clip']==event['clip_id'] and int(e['frame_zero_based'])==frame-1)
                    for key,col in [('cyclistEdge',(40,220,40)),('carEdge',(255,150,30))]:
                        xx=round(float(e[key]));cv2.line(img,(xx,380),(xx,435),col,2)
                    # Annotation stores horizontal x coordinates only; bottom rulers do not assert a physical edge point.
                    label=f'Selected manual horizontal gap {e["pixelGap"]} px; x-only ruler'
                else:label='Car68 track lost; red manual car proxy, not hidden ground truth'
                cv2.rectangle(img,(0,0),(720,50),(20,20,20),-1)
                cv2.putText(img,f'{event["event_id"]} frame {frame} clip +{(frame-1)/log["fps"]:.3f}s',(8,19),cv2.FONT_HERSHEY_SIMPLEX,.44,(255,255,255),1)
                cv2.putText(img,label,(8,39),cv2.FONT_HERSHEY_SIMPLEX,.40,(255,255,255),1)
                cv2.imwrite(str(out/'assets'/(event['event_id']+'_selected_frame.jpg')),img)
        sections.append(dict(event=event,samples=samples,manual=mid,hull=np.asarray(g['hull']).reshape(-1,2).tolist(),fps=log['fps'],video=src))
    data=json.dumps(sections,default=serial).replace('</','<\\/')
    page='''<!doctype html><meta charset="utf-8"><title>Near-miss event review</title>
<style>body{font:15px system-ui;max-width:1100px;margin:24px auto;color:#182d2c}section{border-top:2px solid #bbb;margin-top:24px;padding-top:16px}canvas{max-width:100%;background:#f5f5ef}video{max-width:100%;width:720px}pre{white-space:pre-wrap}button,input{font:inherit;margin:8px}table{border-collapse:collapse}td{border:1px solid #aaa;padding:5px}</style>
<h1>Three unique reviewed interactions</h1><p>Image coordinates in pixels. Yellow hull is saved calibration support. Green subject and blue car boxes/contacts are automatic observations; red car and orange pedestrian crosses are manual contact proxies. Missing blue box means lost/unobserved automatic car, never proof of no vehicle. Hidden positions are not observed. Metre clearance is unavailable. Screen flags and reviewed classification are separate.</p>
<p><a href="PROFESSOR_RESULTS.md">Numerical report</a> · <a href="event_metrics.csv">Event CSV</a> · <a href="frame_eligibility.csv">Per-frame rejections</a> · <a href="reconstruction_inputs.csv">Reconstructed samples</a></p><main id="main"></main><script>
const data=DATA;
for(const d of data){const s=document.createElement('section');main.append(s);const e=d.event;s.innerHTML=`<h2>${e.event_id}</h2><p>${e.object_ids} | ${e.start_time}–${e.end_time}</p><p>Screen: ${e.screening_flags}; reviewed: ${e.reviewed_classification}</p><video controls preload="metadata" src="${d.video}"></video><br><button>Previous sample</button><button>Next sample</button><input type="range"><p class="time"></p><canvas width="720" height="480"></canvas><details><summary>Metric eligibility and missing reasons</summary><pre></pre></details>`;s.querySelector('pre').textContent=JSON.stringify(e,null,2);
const c=s.querySelector('canvas'),ctx=c.getContext('2d'),v=s.querySelector('video'),slider=s.querySelector('input'),time=s.querySelector('.time');const frames=Object.keys(d.samples).map(Number).filter(f=>d.event.event_type!=='pedestrian_crossing'||f>1250&&f<1440).sort((a,b)=>a-b);slider.min=0;slider.max=frames.length-1;slider.value=Math.floor(frames.length/2);
function draw(seek){let f=frames[+slider.value],r=d.samples[f];if(seek)v.currentTime=(f-1)/d.fps;ctx.clearRect(0,0,720,480);if(v.readyState>=2)ctx.drawImage(v,0,0,720,480);ctx.strokeStyle='#d9ac00';ctx.beginPath();d.hull.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.closePath();ctx.stroke();for(const [name,color] of [['subject','#00b850'],['car','#2196ff']]){const p=r[name];if(!p)continue;ctx.strokeStyle=color;ctx.lineWidth=2;ctx.strokeRect(p.x-p.w/2,p.y-p.h,p.w,p.h);ctx.fillStyle=color;ctx.beginPath();ctx.arc(p.x,p.y,4,0,7);ctx.fill();ctx.fillText(name,p.x,p.y-p.h-4);}for(const p of d.manual.filter(p=>p.frame===f)){ctx.strokeStyle=p.object==='car'?'red':'orange';ctx.beginPath();ctx.moveTo(p.x-6,p.y-6);ctx.lineTo(p.x+6,p.y+6);ctx.moveTo(p.x-6,p.y+6);ctx.lineTo(p.x+6,p.y-6);ctx.stroke();}time.textContent=`One-based frame ${f} | clip +${((f-1)/d.fps).toFixed(3)} s | car: ${r.car?'automatic observed':'not observable / track absent'} | physical clearance: N/A`;}
slider.oninput=()=>draw(true);s.querySelectorAll('button').forEach((b,i)=>b.onclick=()=>{slider.value=Math.max(0,Math.min(frames.length-1,+slider.value+(i?1:-1)));draw(true)});v.onseeked=()=>draw(false);v.ontimeupdate=()=>{const f=Math.round(v.currentTime*d.fps)+1;slider.value=frames.reduce((best,x,i)=>Math.abs(x-f)<Math.abs(frames[best]-f)?i:best,0);draw(false)};draw(false);}
</script>'''.replace('DATA',data)
    (out/'review.html').write_text(page)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,default=ROOT);p.add_argument('--out',type=Path);p.add_argument('--config',type=Path,default=ROOT/'pipeline/near_miss_screening.json');a=p.parse_args();build_report(a.repo.resolve(),(a.out or a.repo/'reports/near_miss').resolve(),json.loads(a.config.read_text()))
if __name__=='__main__':main()
