#!/usr/bin/env python3
"""Run saved-trajectory analysis plus optional physical-scale checks and study comparisons."""
import argparse
from collections import defaultdict
import csv
import datetime as dt
import json
from pathlib import Path
import cv2
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
from speed_analysis_pass import run as trajectory_pass, ground, table


def marking_check(H, item):
    if item.get('length_kind') not in ('measured','assumed_standard') or not item.get('source'):
        raise ValueError('Marking length needs measured/assumed_standard kind and source')
    length=float(item['length_metres'])
    if not np.isfinite(length) or length<=0:raise ValueError('Invalid marking length')
    xy=ground(H,np.asarray(item['image_endpoints'],float))
    if xy.shape!=(2,2):raise ValueError('Need two image endpoints')
    mapped=float(np.linalg.norm(xy[1]-xy[0]))
    if mapped<1e-6:raise ValueError('Coincident marking endpoints')
    return dict(mapped_length_metres=mapped,reference_length_metres=length,
                implied_scale_multiplier=length/mapped,status='CONSISTENCY_ONLY_'+item['length_kind'].upper())


def wheel_curve(P, contact_xy, radius, yaw):
    angle=np.linspace(0,2*np.pi,120,endpoint=False)
    horizontal=np.array([np.cos(yaw),np.sin(yaw),0.])
    centre=np.array([*contact_xy,radius])
    world=centre+radius*np.cos(angle)[:,None]*horizontal+radius*np.sin(angle)[:,None]*np.array([0,0,1.])
    q=np.column_stack([world,np.ones(len(world))])@P.T
    if np.any(q[:,2]<=1e-7):raise ValueError('Wheel behind camera')
    return q[:,:2]/q[:,2,None]


def wheel_check(H, item):
    """Fit upright 3-D circular wheel to reviewed outline, not ground-map wheel pixels."""
    if not item.get('outline_reviewed') or not item.get('source') or not item.get('image_undistorted'):
        raise ValueError('Need reviewed wheel outline, source and undistorted-image confirmation')
    if item.get('world_convention')!='metres_Z_up':raise ValueError('Need metre Z-up camera convention')
    P=np.asarray(item['projection_matrix'],float);outline=np.asarray(item['outline_pixels'],float)
    if P.shape!=(3,4) or not np.isfinite(P).all() or outline.ndim!=2 or outline.shape[1]!=2 or len(outline)<12 or not np.isfinite(outline).all():
        raise ValueError('Need finite 3x4 projection and >=12 outline samples')
    point=np.asarray(item['contact_pixel'],float)
    offsets=np.array([[0,0],[10,0],[0,10],[-10,0],[0,-10]])
    xy=ground(H,point+offsets);q=np.column_stack([xy,np.zeros(len(xy)),np.ones(len(xy))])@P.T
    if np.any(q[:,2]<=0) or np.max(np.linalg.norm(q[:,:2]/q[:,2,None]-(point+offsets),axis=1))>2:
        raise ValueError('Projection matrix incompatible with saved ground mapping')
    contact=xy[0];tree=cKDTree(outline)
    def residual(params):
        curve=wheel_curve(P,contact,*params)
        # Symmetric outline distance prevents matching only a short arc.
        return np.r_[tree.query(curve)[0],cKDTree(curve).query(outline)[0]]
    fits=[least_squares(residual,[.335,yaw],bounds=([.05,-np.pi],[1.,np.pi]),loss='soft_l1',max_nfev=150) for yaw in (-2.,-1.,0.,1.,2.)]
    fit=min(fits,key=lambda f:np.mean(residual(f.x)**2));rmse=float(np.sqrt(np.mean(residual(fit.x)**2)))
    if not fit.success or rmse>float(item.get('max_outline_rmse_px',2)):raise ValueError('Wheel outline fit failed quality gate')
    diameter=2*float(fit.x[0]);lo,hi=map(float,item['diameter_prior_metres'])
    if not 0<lo<=hi or not np.isfinite([lo,hi]).all():raise ValueError('Invalid wheel diameter prior')
    return dict(fitted_diameter_metres=diameter,outline_rmse_px=rmse,
                implied_scale_multiplier_low=lo/diameter,implied_scale_multiplier_high=hi/diameter,
                status='EXPERIMENTAL_PRIOR_COMPARISON_NOT_VALIDATED')


def wheel_candidates(video, points, destination):
    """Find ellipse-like edges near clicked rear tyre; candidates are not verified wheels."""
    cap=cv2.VideoCapture(str(video));results=[]
    try:
        if not cap.isOpened():raise ValueError('Video unavailable')
        for k in sorted(set([0,len(points)//2,len(points)-1])):
            p=points[k];cap.set(cv2.CAP_PROP_POS_MSEC,float(p['seconds'])*1000);ok,frame=cap.read()
            if not ok:continue
            x,y=int(p['x']),int(p['y']);h,w=frame.shape[:2]
            x0,x1=max(0,x-55),min(w,x+55);y0,y1=max(0,y-90),min(h,y+12)
            if x1<=x0 or y1<=y0:continue
            crop=frame[y0:y1,x0:x1].copy();gray=cv2.cvtColor(crop,cv2.COLOR_BGR2GRAY)
            edges=cv2.Canny(gray,60,150);contours,_=cv2.findContours(edges,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
            candidates=[]
            for contour in contours:
                if len(contour)<12:continue
                ellipse=cv2.fitEllipse(contour);(cx,cy),(aa,bb),angle=ellipse
                if not 6<=min(aa,bb)<=max(aa,bb)<=90 or min(aa,bb)/max(aa,bb)<.2:continue
                if not 0<=cx<crop.shape[1] or not 0<=cy<crop.shape[0]:continue
                # Search near the contact point, not arbitrary objects throughout frame.
                if abs(cx+x0-x)>35 or abs(cy+y0-y)>60:continue
                candidates.append(dict(centre=[cx+x0,cy+y0],axes=[aa,bb],angle=angle))
                cv2.ellipse(crop,ellipse,(0,180,255),1)
            cv2.circle(crop,(x-x0,y-y0),3,(0,0,255),-1)
            cv2.imwrite(str(destination.with_name(destination.name+f'_{k}.jpg')),crop)
            results.append(dict(seconds=p['seconds'],ellipse_candidates=candidates,status='UNVERIFIED_EDGES_NOT_WHEEL_DETECTIONS'))
    finally:cap.release()
    return results


def bootstrap_difference(values, reference, rng, draws=2000):
    values=np.asarray(values,float);reference=np.asarray(reference,float)
    if len(values)<2 or len(reference)<2:return dict(difference=float(np.mean(values)-np.mean(reference)),low='',high='',status='INSUFFICIENT_SAMPLE_FOR_INTERVAL')
    differences=np.mean(rng.choice(values,(draws,len(values))),axis=1)-np.mean(rng.choice(reference,(draws,len(reference))),axis=1)
    return dict(difference=float(np.mean(values)-np.mean(reference)),low=float(np.percentile(differences,2.5)),high=float(np.percentile(differences,97.5)),status='UNMATCHED_GROUP_SAMPLING_ONLY_NOT_ACCURACY')


def extensions(a):
    normalized=json.loads((a.manual/'analysis/normalized_observations.json').read_text());pack=json.loads((a.manual/'analysis/review_inputs.json').read_text())
    entries={e['key']:e for e in pack['entries']};groups=defaultdict(list)
    for p in normalized['observations']:groups[p['encounter_id']].append(p)
    cal=json.loads((a.manual/'analysis/final_batch_export.json').read_text())
    cameras={v['camera']:v['calibration'] for v in cal['calibrations'].values()}
    evidence=json.loads(a.scale_evidence.read_text()) if a.scale_evidence else {}
    if set(evidence)-set(cameras):raise ValueError('Unknown camera in scale evidence')
    d=a.out/'scale_checks';d.mkdir();(d/'wheel_candidates').mkdir()
    checks=[];preview={}
    for camera in sorted({p['camera'] for p in normalized['observations']}):
        H=np.asarray(cameras[camera]['H'],float);items=evidence.get(camera,{})
        checks.append(dict(camera=camera,method='car_calibration',status='BASELINE_LEARNED_SCALE_NOT_INDEPENDENTLY_VALIDATED',detail='Existing calibration reused; no scale fitted to study means'))
        for name,fn in [('markings',marking_check),('wheels',wheel_check)]:
            supplied=items.get(name,[])
            if not supplied:checks.append(dict(camera=camera,method=name,status='MISSING_EVIDENCE',detail='Need identified marking and length source' if name=='markings' else 'Need full 3-D camera projection, reviewed outline and explicit wheel-size prior'))
            for item in supplied:
                try:
                    result=fn(H,item);checks.append(dict(camera=camera,method=name,status=result['status'],detail=json.dumps(result)))
                except Exception as error:checks.append(dict(camera=camera,method=name,status='REJECTED_EVIDENCE',detail=str(error)))
        table(d/'calibration_checks.csv',checks)
    for encounter,points in sorted(groups.items()):
        points=sorted(points,key=lambda p:p['seconds']);e=entries[points[0]['key']]
        try:preview[encounter]=wheel_candidates(a.videos/e['video'],points,d/'wheel_candidates'/encounter)
        except Exception as error:preview[encounter]=dict(status='UNAVAILABLE',error=str(error))
        (d/'wheel_candidates.json').write_text(json.dumps(preview,indent=2))
    refs=defaultdict(list)
    with a.references.open() as f:
        for row in csv.DictReader(f):
            value=float(row['source_mph'])
            if np.isfinite(value) and value>0:refs[row['street']].append(value)
    measured=list(csv.DictReader((a.out/'trajectory/cyclists.csv').open()));rng=np.random.default_rng(a.seed);comparisons=[]
    for site in sorted({r['location'] for r in measured}):
        for label in ('old_path_mph','endpoint_mph','robust_mph'):
            values=[float(r[label]) for r in measured if r['location']==site and r[label]!='']
            if not values or not refs[site]:continue
            result=bootstrap_difference(values,refs[site],rng)
            comparisons.append(dict(location=site,method=label,video_cyclists=len(values),study_speed_records=len(refs[site]),video_mean_mph=float(np.mean(values)),study_mean_mph=float(np.mean(refs[site])),difference_mph=result['difference'],sampling_difference_low=result['low'],sampling_difference_high=result['high'],status=result['status']))
    table(a.out/'study_group_comparisons.csv',comparisons)
    statuses=dict(trajectory_analysis='COMPLETED',timestamp_audit='SEE_TRAJECTORY_REPORT',sensitivity='ASSUMPTION_BASED',wheel_candidate_search='COMPLETED_UNVERIFIED_EDGES',metric_scale_checks='SEE_SCALE_CHECKS_CSV',study_group_comparison='COMPLETED_UNMATCHED_GROUPS',tracker='EXISTING_BYTETRACK_REUSED_NO_NEW_TRACKER_EXPERIMENT',wheel_keypoint_training='NOT_IMPLEMENTED_NEEDS_LABELLED_TRAINING_SET',camera_geolocation='NOT_AUTOMATED_UNIVERSITY_EVIDENCE_RETAINED')
    (a.out/'method_status.json').write_text(json.dumps(statuses,indent=2))
    lines=['# Bicycle speed plan results','','[Main speed comparison, times, plots and sensitivity](trajectory/RESULTS.md) is the starting report.','','Additional outputs:','', '- `study_group_comparisons.csv`: old/endpoint/robust means against study means, with sampling-only bootstrap differences. Different people/sessions and convenience sampling prevent accuracy claims. Intervals exclude shared scale error, may be unreliable for small samples and are omitted for n<2.','- `scale_checks/calibration_checks.csv`: car baseline and optional marking/3-D wheel checks. Missing evidence stays missing. No automatic scale adjustment or fusion.','- `scale_checks/wheel_candidates/`: crops around existing rear-contact clicks, with ellipse-like edges marked yellow and clicked contact red. These are candidates, not verified wheels, and never supply metric scale automatically. No need to annotate them unless this optional method is pursued.','- `method_status.json`: explicit implemented/pending method status. The current detector already uses ByteTrack with ID stitching; no new tracker or wheel-keypoint model is claimed.','','Metric wheel fitting uses an explicit 3x4 camera projection in a metre Z-up coordinate system and a reviewed outline. It never projects the vertical wheel through a ground-only homography. Candidate search, circular wheel assumptions and fitting thresholds remain experimental. Marking lengths need a real source or must be labelled assumed standards. Sources disagreeing is a consistency flag, not a calibrated uncertainty bound.','','[Projection reference](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html) · [Robust nonlinear fitting](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html).']
    (a.out/'RESULTS.md').write_text('\n'.join(lines)+'\n')


def main():
    repo=Path(__file__).resolve().parents[4];p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manual',type=Path,default=repo/'manual');p.add_argument('--videos',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--references',type=Path,default=repo/'vision3/best/test_colonial/exp_results/speed_reference_readiness_20261023/all_reference_records.csv')
    p.add_argument('--scale-evidence',type=Path);p.add_argument('--simulations',type=int,default=500);p.add_argument('--seed',type=int,default=20261026)
    p.add_argument('--click-sigma-px',type=float,default=3);p.add_argument('--scale-fraction',type=float,default=.15)
    a=p.parse_args()
    if a.simulations<20 or not 0<=a.scale_fraction<1 or a.click_sigma_px<0:p.error('Invalid simulation settings')
    a.out.mkdir(parents=True,exist_ok=False)
    if not a.references.is_file():p.error('Missing study references CSV')
    root=a.out;a.out=root/'trajectory';trajectory_pass(a);a.out=root;extensions(a)
    (root/'status.json').write_text(json.dumps(dict(state='COMPLETED',scope='saved_manual_trajectories_plus_optional_scale_evidence'),indent=2))

if __name__=='__main__':main()
