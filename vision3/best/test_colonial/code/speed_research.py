#!/usr/bin/env python3
"""Separate map-free calibration experiments; workbook speeds never fit the models."""
import argparse
import csv
import json
import subprocess
import sys
import traceback
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.optimize import least_squares
import cv2
from metric_trajectory_speed import estimate

AUTHOR_COMMIT='80b8bc4964eddfda32c40e6d1c8fe8b62f777f55'


def save(path,data):
    path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')


def write_rows(path,rows):
    if not rows:return
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)


def geometry(params,size):
    focal,pitch,roll,height=params
    n=np.array([np.sin(roll)*np.sin(pitch),np.cos(roll)*np.sin(pitch),np.cos(pitch)])
    Kinv=np.array([[1/focal,0,-size[0]/2/focal],[0,1/focal,-size[1]/2/focal],[0,0,1]])
    e=np.array([1.,0,0]);e-=n*np.dot(n,e);e/=np.linalg.norm(e)
    e2=np.cross(n,e)
    H=np.vstack([height*e@Kinv,height*e2@Kinv,n@Kinv])
    return n,Kinv,H


def height_residual(params,feet,heads,size,person_height):
    n,K,H=geometry(params,size);foot=feet@K.T;head=heads@K.T
    df=foot@n;dh=head@n
    safe=lambda x:np.where(abs(x)>1e-5,x,np.where(x>=0,1e-5,-1e-5))
    delta=params[3]*foot/safe(df)[:,None]-(params[3]-person_height)*head/safe(dh)[:,None]-person_height*n
    # Penalize rays above the assumed ground horizon.
    return np.r_[delta.ravel(),np.minimum(df-.001,0)*100,np.minimum(dh-.001,0)*100]


def fit_height(feet,heads,size,person_height=1.7):
    if len(feet)<20:raise ValueError('Need20 head/foot observations from separate qualifying tracks')
    fit=np.arange(len(feet))%4!=0
    starts=[[size[0],.7,0,6],[size[0]*1.8,.4,.1,10],[size[0]*.7,1.,-.1,4]]
    solutions=[]
    for start in starts:
        sol=least_squares(height_residual,start,args=(feet[fit],heads[fit],size,person_height),bounds=([size[0]*.25,.03,-.5,person_height+.2],[size[0]*5,1.55,.5,30]),loss='soft_l1',f_scale=.1,max_nfev=1200)
        error=float(np.sqrt(np.mean(height_residual(sol.x,feet[~fit],heads[~fit],size,person_height)**2)))
        solutions.append((error,sol.x))
    solutions.sort(key=lambda x:x[0]);error,params=solutions[0]
    n,K,H=geometry(params,size)
    # Multiple similar minima with different camera heights indicate poor identifiability.
    near=[p[3] for err,p in solutions if err<=error*1.25+.01]
    stable=max(near)/min(near)<1.2 and error<.3
    return H,dict(parameters=params.tolist(),assumed_person_height_metres=person_height,held_out_headfoot_residual_metres=error,multistart_heights_metres=near,geometry_check_passed=stable,validation='not_independently_metric_or_speed_validated')


def height_calibration(root,size,out):
    feet=[];heads=[];provenance=[]
    for path in sorted((root/'counts/b4_combo_static5').glob('*_tracks.csv')):
        stats={r['track_id']:r for r in csv.DictReader(path.open())}
        traj=path.with_name(path.name.replace('_tracks.csv','_trajectories.csv'))
        if not traj.exists():continue
        candidates=defaultdict(list)
        for r in csv.DictReader(traj.open()):
            s=stats.get(r['track_id'],{})
            if int(r.get('coasted','0')) or float(r['box_h'])<30 or not float(s.get('weighted_pedestrian') or 0)>=.9:continue
            if float(s.get('secs') or 0)<3:continue
            candidates[r['track_id']].append(r)
        for tid,rr in candidates.items():
            # One observation per identity avoids pretending thousands of frames are independent.
            r=rr[len(rr)//2];cx=float(r['box_cx']);cy=float(r['box_cy']);h=float(r['box_h'])
            feet.append([cx,cy+h/2,1]);heads.append([cx,cy-h/2,1]);provenance.append(dict(source=traj.name,track_id=tid))
    save(out/'height_observations.json',dict(feet=feet,heads=heads,provenance=provenance))
    H,info=fit_height(np.asarray(feet),np.asarray(heads),size)
    return H,info,cv2.convexHull(np.asarray(feet,np.float32)[:,:2])


def iccv_calibration(video,author,size,out,device='cpu',frames=160):
    import torch
    from torchvision.models.detection import maskrcnn_resnet50_fpn,MaskRCNN_ResNet50_FPN_Weights
    if not author.exists():
        subprocess.run(['git','clone','https://github.com/naver/cctv.git',str(author)],check=True)
    subprocess.run(['git','-C',str(author),'checkout',AUTHOR_COMMIT],check=True,capture_output=True)
    actual=subprocess.check_output(['git','-C',str(author),'rev-parse','HEAD'],text=True).strip()
    if actual!=AUTHOR_COMMIT:raise ValueError('Author revision mismatch')
    sys.path.insert(0,str(author))
    from archs.transformer import Transformer
    from tools.speed import homography_from_transformer
    import tools.speed as author_speed
    def no_debugger(*args,**kwargs):
        raise RuntimeError('Author calibration encountered a degenerate configuration')
    author_speed.bb=no_debugger
    net=Transformer(embdim=64,outdim=8,nlayers=8,nhead=4,nhid=256)
    weights=torch.load(author/'models/trained_transformer.pt',map_location='cpu',weights_only=True)
    net.load_state_dict(weights['weights']);net.eval()
    detector=maskrcnn_resnet50_fpn(weights=MaskRCNN_ResNet50_FPN_Weights.DEFAULT).eval().to(device)
    v=cv2.VideoCapture(str(video))
    if not v.isOpened():raise ValueError('Cannot open raw source video')
    if [int(v.get(3)),int(v.get(4))]!=size:raise ValueError('Use original720x480 source, not annotated video with header')
    fps=v.get(cv2.CAP_PROP_FPS);total=int(v.get(cv2.CAP_PROP_FRAME_COUNT))
    previous=[];groups=defaultdict(list);nextid=0
    def iou(a,b):
        lt=np.maximum(a[:2],b[:2]);rb=np.minimum(a[2:],b[2:]);inter=np.maximum(rb-lt,0).prod()
        return inter/((a[2:]-a[:2]).prod()+(b[2:]-b[:2]).prod()-inter+1e-8)
    for fi in range(0,min(total,frames*15),15):
        v.set(cv2.CAP_PROP_POS_FRAMES,fi);ok,image=v.read()
        if not ok:break
        rgb=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        tensor=torch.from_numpy(rgb.copy()).permute(2,0,1).float().to(device)/255
        with torch.no_grad():pred=detector([tensor])[0]
        boxes=pred['boxes'].cpu().numpy();scores=pred['scores'].cpu().numpy();labels=pred['labels'].cpu().numpy()
        masks=pred['masks'].cpu().numpy()[:,0];current=[];used=set()
        for box,score,label,mask in zip(boxes,scores,labels,masks):
            if label!=3 or score<.8 or min(box[2:]-box[:2])<15:continue
            ranked=sorted([(iou(box,b),tid) for b,tid in previous if tid not in used],reverse=True)
            if ranked and ranked[0][0]>.2:tid=ranked[0][1]
            else:nextid+=1;tid=nextid
            used.add(tid);current.append((box,tid))
            x1,y1,x2,y2=np.round(box).astype(int);x1=max(x1,0);y1=max(y1,0);x2=min(x2,size[0]);y2=min(y2,size[1])
            if x2<=x1 or y2<=y1:continue
            crop=cv2.resize(mask[y1:y2,x1:x2],(14,14))
            groups[tid].append((fi,box,crop))
        previous=current
        if fi%300==0:print('Mask calibration frame',fi,flush=True)
    v.release();records=[]
    for tid,rows in groups.items():
        if len(rows)<4:continue
        centers=np.array([(r[1][:2]+r[1][2:])/2 for r in rows])
        if np.linalg.norm(centers[-1]-centers[0])<30:continue
        ts=np.array([r[0] for r in rows]);motion=np.column_stack([np.gradient(centers[:,i],ts) for i in (0,1)])
        for (fi,box,mask),c,m in zip(rows,centers,motion):
            if np.linalg.norm(m)>1e-5:records.append((tid,fi,box,mask,c,m))
    if len({r[0] for r in records})<10:raise ValueError('Fewer than10 usable car tracks; calibration refused')
    tracks={k:np.asarray([r[i] for r in records]) for i,k in enumerate(['track_ids','timestamps','boxes','masks','centers','motion'])}
    np.savez_compressed(out/'car_calibration_observations.npz',**tracks)
    from types import SimpleNamespace
    np.random.seed(20261024);torch.manual_seed(20261024)
    H=homography_from_transformer(SimpleNamespace(imsize=size),tracks,net,sampling_iters=100,ransac_iters=512)
    if not np.isfinite(H).all() or abs(np.linalg.det(H))<1e-15:raise ValueError('Invalid learned homography')
    hull=cv2.convexHull(np.asarray(tracks['centers'],np.float32))
    return H,dict(author_commit=actual,car_tracks=len(set(tracks['track_ids'].tolist())),car_boxes=len(records),geometry_check_passed=True,validation='learned_scale_not_independently_speed_validated',sidewalk_transfer='unverified_road_sidewalk_height_difference'),hull


def measurement_times(result,samples,clip_start):
    """Report observed time spans actually used, never the full source hour."""
    from datetime import datetime,time
    clocks={int(r['frame']):r['time'] for r in samples}
    intervals=json.loads(result.get('measurement_frame_intervals','[]'))
    times=[]
    for first,last in intervals:
        a=datetime.combine(clip_start.date(),time.fromisoformat(clocks[first]))
        b=datetime.combine(clip_start.date(),time.fromisoformat(clocks[last]))
        times.append(dict(start=a.isoformat(sep=' '),end=b.isoformat(sep=' '),clip_start_seconds=round((a-clip_start).total_seconds(),3),clip_end_seconds=round((b-clip_start).total_seconds(),3)))
    return dict(recording_date=str(clip_start.date()),measurement_start=times[0]['start'] if times else '',measurement_end=times[-1]['end'] if times else '',measurement_intervals=json.dumps(times),clock_basis='saved_trajectory_clock_not_independently_verified',speed_statistic='median_of_approximately_one_second_velocity_windows')


def trajectory_results(root,H,hull,method):
    rows=[]
    people=list(csv.DictReader((root/'exp_results/labelled_validation_20261020/people_lane_speed.csv').open()))
    from eval_truth import CLIPS,read_truth
    from datetime import datetime,time
    for clip,c in CLIPS.items():
        prefix=f'Standard_SCU8OG_2019-07-10_0000.{c["chunk"]:03d}'
        log=json.loads((root/'logs/b4_combo_static5'/f'{prefix}_run_log.json').read_text())
        truth={r['id']:r for r in read_truth(root/c['truth'])[0]}
        t0=datetime.fromisoformat(c['start']);groups=defaultdict(list)
        for r in csv.DictReader((root/'counts/b4_combo_static5'/f'{prefix}_trajectories.csv').open()):groups[r['track_id']].append(r)
        for p in people:
            if p['clip']!=clip or p['truth_class']!='cyclist':continue
            tr=truth[p['truth_id']];samples=[]
            for r in groups[p['candidate_track_id']]:
                sec=(datetime.combine(t0.date(),time.fromisoformat(r['time']))-t0).total_seconds()
                if tr['s']<=sec<=tr['e']:samples.append(r)
            result=estimate(samples,log['fps'],H,hull)
            result.update(measurement_times(result,samples,t0))
            rows.append(dict(method=method,user_type=p['truth_class'],clip=clip,truth_id=p['truth_id'],candidate_track_id=p['candidate_track_id'],source_video=log['video_path'],clip_start=c['start'],identity_verified=p['identity_verified'],facility=p['lane_provisional'],**result))
    return rows


def university_manual_comparison(config,reference_rows):
    """Compare a documented bicycle crossing with separate study observations."""
    if config['user_type']!='cyclist':raise ValueError('Bicycle speed comparison only')
    a0,a1,b0,b1=[float(config[k]) for k in ('a_before_clip_seconds','a_after_clip_seconds','b_before_clip_seconds','b_after_clip_seconds')]
    if not (a0<=a1<b0<=b1):raise ValueError('Invalid ordered crossing brackets')
    distance=float(config['distance_feet'])
    if not np.isfinite(distance) or distance<=0:raise ValueError('Positive finite map distance required')
    seconds=((b0+b1)-(a0+a1))/2
    factor=distance*3600/5280
    speed=factor/seconds
    values=np.asarray([float(r['source_mph']) for r in reference_rows if r['street']==config['site'] and r['facility']==config['facility']])
    if len(values)==0 or not np.isfinite(values).all():raise ValueError('Missing or invalid same-site/facility references')
    return dict(method='manual_map_gates',site=config['site'],facility=config['facility'],user_type='cyclist',subject=config['subject'],estimated_cyclists=1,distance_feet=distance,travel_seconds=seconds,recording_date=config.get('recording_date',''),video=config.get('video',''),a_crossing_clip_seconds=json.dumps([a0,a1]),b_crossing_clip_seconds=json.dumps([b0,b1]),clock_basis='video_presentation_seconds; generated_header_0845; source_burned_clock_approximately_2s_ahead',speed_statistic='average_over_one_A_to_B_journey',speed_mph=speed,timing_only_low_mph=factor/(b1-a0),timing_only_high_mph=factor/(b0-a1),reference_cyclists=len(values),reference_mean_mph=float(values.mean()),reference_median_mph=float(np.median(values)),reference_min_mph=float(values.min()),reference_max_mph=float(values.max()),difference_from_reference_mean_mph=speed-float(values.mean()),within_reference_observed_range=bool(values.min()<=speed<=values.max()),interpretation='one_video_cyclist_vs_separate_study_group_not_matched_accuracy')


def run(a):
    out=a.out;out.mkdir(parents=True,exist_ok=False);root=a.root
    status=[];allrows=[]
    save(out/'experiment_policy.json',dict(selection='closest_study_group_mean_exploratory_not_accuracy',output_user_types=['cyclist'],reference_used_for_fitting=False,person_height_prior_metres=1.7,iccv_author_commit=AUTHOR_COMMIT,source_video=str(a.video) if a.video else None,frames=a.frames))
    for name,fn in [('pedestrian_height',lambda d:height_calibration(root,[720,480],d)),('iccv2021',lambda d:iccv_calibration(a.video,a.author_dir,[720,480],d,a.device,a.frames))]:
        d=out/name;d.mkdir()
        try:
            if name=='iccv2021' and a.video is None:raise ValueError('Original Colonial daytime video required; not available in this invocation')
            H,info,hull=fn(d);save(d/'calibration.json',dict(H=H.tolist(),hull=hull.tolist(),**info))
            rows=trajectory_results(root,H,hull,name)
            for r in rows:r['calibration_geometry_check_passed']=info['geometry_check_passed']
            write_rows(d/'speeds.csv',rows);allrows+=rows
            status.append(dict(method=name,state='EXPERIMENT_COMPLETED',detail=info))
        except Exception as e:
            (d/'error.txt').write_text(traceback.format_exc());status.append(dict(method=name,state='NOT_COMPLETED',detail=str(e)))
    for name,reason in [('bmvc2014','Full 3D-box/vanishing-point implementation and verified vehicle-dimension priors not integrated; no paper reproduction claimed.'),('sochor2017','Requires vehicle identification and metric 3D CAD/render assets; unavailable in current repository.'),('keypoint2026','Requires trained36-keypoint detector/template assets; no verified author checkpoint integrated.')]:
        status.append(dict(method=name,state='NOT_IMPLEMENTED_MISSING_COMPONENTS',detail=reason))
    write_rows(out/'all_speed_estimates.csv',allrows)
    refs=list(csv.DictReader((root/'exp_results/speed_reference_readiness_20261023/all_reference_records.csv').open()))
    university_result=None
    manual_input=root.parents[2]/'data/reviews/speed/university_manual_crossing_20261024.json'
    try:
        config=json.loads(manual_input.read_text())
        university_result=university_manual_comparison(config,refs)
        write_rows(out/'university_manual_comparison.csv',[university_result])
        save(out/'university_manual_inputs.json',config)
        write_rows(out/'university_reference_records.csv',[r for r in refs if r['street']=='University'])
        status.append(dict(method='university_manual_map_gates',state='CALCULATED_FROM_SAVED_TIMING',detail='One manually timed bicyclist; compared with separate University sidewalk study records'))
    except Exception as e:
        status.append(dict(method='university_manual_map_gates',state='NOT_COMPLETED',detail=str(e)))
    save(out/'method_status.json',status)
    refs=[r for r in refs if r['street']=='Colonial'];write_rows(out/'colonial_reference_records.csv',refs)
    comparisons=[]
    for method in ('pedestrian_height','iccv2021'):
        for facility,reference_facility in [('bike_lane','Bike Lane'),('sidewalk','Sidewalk')]:
            measured=[float(r['speed_mph']) for r in allrows if r['method']==method and r['user_type']=='cyclist' and r['facility']==facility and r['speed_mph']!='' and r['calibration_geometry_check_passed']]
            reference=[float(r['source_mph']) for r in refs if r['facility']==reference_facility]
            comparisons.append(dict(method=method,facility=facility,estimated_people=len(measured),reference_records=len(reference),estimated_mean_mph=float(np.mean(measured)) if measured else '',reference_mean_mph=float(np.mean(reference)),absolute_difference_of_group_means_mph=abs(float(np.mean(measured))-float(np.mean(reference))) if measured else '',interpretation='exploratory_closeness_to_unmatched_study_mean_not_accuracy'))
    write_rows(out/'descriptive_group_comparison.csv',comparisons)
    # Rank on identical cyclist candidates only; different accepted populations can
    # otherwise change the mean without improving any speed estimate.
    rank_rows=[]
    for facility in ('bike_lane','sidewalk'):
        eligible={}
        for method in ('pedestrian_height','iccv2021'):
            eligible[method]={(r['clip'],r['truth_id']):float(r['speed_mph']) for r in allrows if r['method']==method and r['user_type']=='cyclist' and r['facility']==facility and r['speed_mph']!='' and r['calibration_geometry_check_passed']}
        active={k:v for k,v in eligible.items() if v}
        common=set.intersection(*(set(v) for v in active.values())) if active else set()
        reference_facility={'bike_lane':'Bike Lane','sidewalk':'Sidewalk'}[facility]
        target=float(np.mean([float(r['source_mph']) for r in refs if r['facility']==reference_facility]))
        candidates=[]
        for method,values in active.items():
            if not common:continue
            mean=float(np.mean([values[key] for key in sorted(common)]))
            candidates.append(dict(method=method,facility=facility,common_cyclist_candidates=len(common),estimated_mean_mph=mean,study_mean_mph=target,absolute_group_mean_difference_mph=abs(mean-target),interpretation='exploratory_group_similarity_not_matched_accuracy'))
        candidates.sort(key=lambda r:(r['absolute_group_mean_difference_mph'],r['method']))
        for i,r in enumerate(candidates,1):
            r['closeness_rank']=i;r['comparison_status']='multiple_methods_same_candidate_set' if len(candidates)>1 else 'only_one_method_no_competitive_selection'
        rank_rows+=candidates
    write_rows(out/'exploratory_closeness_ranking.csv',rank_rows)
    save(out/'selection_status.json',dict(valid_comparison_rows=len(rank_rows),purpose='closest_study_mean_not_accuracy',has_competing_methods=any(r['comparison_status']=='multiple_methods_same_candidate_set' for r in rank_rows),pedestrian_reference_speeds_available=False))
    lines=['# Map-free speed experiments','','No model was fitted to the study speed values. Closest-study-mean ranking is exploratory; no matched-person accuracy is claimed.','', '| Method | State |','|---|---|']
    lines += [f'| {r["method"]} | {r["state"]} |' for r in status]
    lines += ['','Pedestrian method is a new paper-inspired implementation, not author code; assumed average height1.7m. Head/feet inferred from boxes can be wrong; physical scale is unvalidated. ICCV uses pinned author pretrained transformer with new MaskRCNN/IoU-track extraction adapter. Neither is a complete published benchmark reproduction. Speeds outside calibration hull or interrupted tracks are refused. Road calibration does not establish sidewalk-plane calibration. Day/night scale transfer assumes camera remains fixed.','','Workbook reference records are exported separately. The workbook people/time/camera correspondence is unknown; exploratory_closeness_ranking.csv ranks valid methods by similarity to the study mean using the same cyclist candidate set per facility. This is a user-requested selection rule, not validated accuracy. Speed outputs are bicyclist-only (motorcycles excluded). Pedestrian detections may support height calibration and cars support learned calibration, but neither pedestrian nor car speeds are exported. No pedestrian speed references were found in the bicyclist workbook. Rejected/uncertain lane labels are not forced into reference facilities. Geometry-check failures make any diagnostic speeds unsuitable for decisions. Review per-method calibration.json and error.txt, and method_status.json.']
    lines+=['','## Bicyclist measurement times','','Each row is one cyclist estimate, not a full-hour average. Only the observed intervals used in speed calculation are listed. Saved camera clocks are not independently verified; disjoint intervals remain separate in all_speed_estimates.csv.','', '| Method | Cyclist | Recording date | Used clock start | Used clock end | mph |','|---|---|---|---|---|---:|']
    for r in allrows:
        if r['speed_mph']=='':continue
        lines.append(f"| {r['method']} | {r['clip']}/{r['truth_id']} | {r['recording_date']} | {r['measurement_start']} | {r['measurement_end']} | {r['speed_mph']} |")
    if university_result is not None:
        u=university_result
        lines+=['', '## University manual map-distance method', '', f"One bicyclist: {u['speed_mph']:.2f}mph (timing-only range {u['timing_only_low_mph']:.2f}–{u['timing_only_high_mph']:.2f}mph). Study University sidewalk: {u['reference_cyclists']}records, mean {u['reference_mean_mph']:.2f}mph, median {u['reference_median_mph']:.2f}mph, range {u['reference_min_mph']:.2f}–{u['reference_max_mph']:.2f}mph. Difference from study mean: {u['difference_from_reference_mean_mph']:+.2f}mph.", '', 'Manual timing source: September25,2019,08:45–09:00 annotated clip; gateA at player07:02.50–07:03.00 and gateB at07:07.25–07:07.50. Generated clock approximately08:52:02.50–08:52:07.50; burned source clock about2seconds ahead. Presentation seconds/evidence identify the exact reviewed frames.', '', 'This is a single manually timed video cyclist versus a separate study group. Similarity is descriptive, not matched-person validation. The timing-only range excludes map-distance and endpoint correspondence errors. The study55ft and owner map55.17ft are separate inputs, not confirmed identical sections. This saved result needs no University GPU rerun. It is not ranked against Colonial methods because the location/people differ.']
    (out/'RESULTS.md').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--out',type=Path,required=True);p.add_argument('--video',type=Path);p.add_argument('--author-dir',type=Path,default=Path.home()/'.cache/objectdetect/naver-cctv');p.add_argument('--device',default='cpu');p.add_argument('--frames',type=int,default=160)
    run(p.parse_args())
