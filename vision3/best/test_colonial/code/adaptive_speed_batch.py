#!/usr/bin/env python3
"""Bounded15-minute bicycle-candidate speed sampling; unmatched study comparison."""
import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import shlex
import re
import shutil
import subprocess
import sys
import traceback
from collections import defaultdict
import numpy as np
import cv2
from speed_site_screen import plan as screen_plan,CANDIDATES
from speed_research import iccv_calibration,save,write_rows,measurement_times
from metric_trajectory_speed import estimate
from study_batch import build_plan
from research_worker import execute


def quota(n):
    if n<1:raise ValueError('Positive reference sample required')
    return min(n,5,max(3,math.ceil(n/3)))


def reference_groups(root):
    path=root/'exp_results/speed_reference_readiness_20261023/all_reference_records.csv'
    groups=defaultdict(list)
    with path.open() as f:
        for row in csv.DictReader(f):groups[row['street']].append(row)
    return groups


def make_plan(root,tag,max_windows=4,extrapolate=False):
    refs=reference_groups(root);sources=screen_plan(root,Path('/orange/xiangyan/rithika/vision/pilot_clips'))
    tasks=[];skips=[]
    for street,rr in sorted(refs.items()):
        choices=[r for r in sources if r['reference_location']==street]
        if not choices:skips.append(dict(site=street,reason='no_candidate_source_in_current_mapping'));continue
        # One camera per reference group; never pool LeeNorth/South as independent coverage.
        source=min(choices,key=lambda r:(CANDIDATES[street].index(r['site']),r['clock']))
        tasks.append(dict(key='s'+str(len(tasks)).zfill(2)+'_'+re.sub(r'[^a-z0-9]+','_',source['site'].lower()).strip('_'),reference_site=street,source=source,reference_count=len(rr),reference_mean_mph=float(np.mean([float(r['source_mph']) for r in rr])),target=quota(len(rr)),reference_facilities=sorted({r['facility'] for r in rr})))
    return dict(root=str(root),tag=tag,tasks=tasks,skipped=skips,segment_seconds=900,max_windows=max_windows,exploratory_road_plane_transfer=extrapolate,created=dt.datetime.now().isoformat(),jobs=[])


def boundary_safe(first,last,start,end,margin=.5):
    return first>start+margin and last<end-margin


def clock_seconds(clock):
    t=dt.time.fromisoformat(clock);return t.hour*3600+t.minute*60+t.second+t.microsecond/1e6


def window_pipeline(root,tag,row,start,end,fps,frames):
    task=build_plan(root,tag,[row])['tasks'][0]
    task['env'].update(START_FRAME=str(round(start*fps)+1),MAX_FRAMES=str(min(int(frames),round(end*fps))),EXPORT_VEHICLE_TRAJECTORIES='0',SLURM_ARRAY_TASK_ID='1',CHUNK='1',SESSION_START=row['clock'].replace(' ','_'))
    return task


def select_chronologically(accepted,rows,target):
    eligible=sorted([r for r in rows if r['eligible']],key=lambda r:(r['track_start'],r['track_id']))
    for r in eligible[:max(0,target-len(accepted))]:r['selected_for_mean']=1;accepted.append(r)
    for r in rows:r.setdefault('selected_for_mean',0)
    return len(eligible)


def gather_window(log_path,H,hull,window_start,window_end,task,segment,extrapolate):
    log=json.loads(log_path.read_text());groups=defaultdict(list)
    with Path(log['trajectories_csv']).open() as f:
        for r in csv.DictReader(f):groups[r['track_id']].append(r)
    with Path(log['tracks_csv']).open() as f:tracks=list(csv.DictReader(f))
    t0=dt.datetime.fromisoformat(task['source']['clock']);rows=[]
    full_hull=np.array([[[0,0]],[[log['resolution'][0]-1,0]],[[log['resolution'][0]-1,log['resolution'][1]-1]],[[0,log['resolution'][1]-1]]],np.float32)
    for tr in tracks:
        if tr['label'].upper()!='BICYCLIST':continue
        samples=groups.get(tr['track_id'],[])
        observed=[r for r in samples if not int(r.get('coasted',0))]
        first=(dt.datetime.fromisoformat(tr['first_time'])-t0).total_seconds()
        last=(dt.datetime.fromisoformat(tr['last_time'])-t0).total_seconds()
        safe=boundary_safe(first,last,window_start,window_end)
        strict=estimate(samples,log['fps'],H,hull)
        result=estimate(samples,log['fps'],H,full_hull) if extrapolate else strict
        if observed:
            xy=np.asarray([[float(r['foot_x']),float(r['foot_y'])] for r in observed])
            inside=np.mean([cv2.pointPolygonTest(hull,tuple(x),False)>=0 for x in xy])
        else:inside=0.
        eligible=tr['counted']=='1' and safe and result['speed_mph']!=''
        reasons=[]
        if tr['counted']!='1':reasons.append('rejected_by_reference_count_filters')
        if not safe:reasons.append('boundary_censored_possible_duplicate')
        if result['speed_mph']=='':reasons.append(result['status'])
        rows.append(dict(site=task['reference_site'],camera=task['source']['site'],segment=segment,track_id=tr['track_id'],source_video=log['video_path'],annotated_clips=json.dumps(log.get('annotated_clips',[])),run_log=str(log_path),track_start=tr['first_time'],track_end=tr['last_time'],predicted_type='bicycle_candidate_possible_motorcycle',identity_verified=0,human_bicycle_confirmed=0,counted=tr['counted'],eligible=int(eligible),exclusion_reason=';'.join(reasons),strict_supported_speed_mph=strict['speed_mph'],fraction_observations_inside_car_support=round(float(inside),4),road_plane_transfer_enabled=extrapolate,facility_correspondence='candidate_camera_only_not_individually_verified',**result,**measurement_times(result,samples,t0)))
    return rows


def snapshot(directory,task,status):
    """Publish an independent site report without waiting for other workers."""
    out=directory/task['key']
    temporary=out/'status.json.tmp'
    save(temporary,status)
    temporary.replace(out/'status.json')
    write_rows(out/'selected_bicycle_candidates.csv',status.get('samples',[]))
    report(directory,task=task)


def worker(directory,index):
    p=json.loads((directory/'manifest.json').read_text());root=Path(p['root']);task=p['tasks'][index];out=directory/task['key'];out.mkdir(exist_ok=False)
    status=dict(site=task['reference_site'],camera=task['source']['site'],state='STARTED',target=task['target'],samples=[],windows=[],failure='')
    snapshot(directory,task,status)
    try:
        status['stage']='calibration';snapshot(directory,task,status)
        row=dict(task['source']);video=Path(row['video']);cap=cv2.VideoCapture(str(video))
        try:
            fps=cap.get(5);frames=cap.get(7);size=[int(cap.get(3)),int(cap.get(4))];ok,_=cap.read()
            if not ok or fps<=0 or frames<=0:raise ValueError('Unreadable original source; preview source extraction required')
        finally:cap.release()
        row.update(fps=fps,duration_seconds=frames/fps,frames=int(frames),width=size[0],height=size[1],probe_status='readable_metadata_not_full_decode')
        caldir=out/'calibration';caldir.mkdir()
        H,info,hull=iccv_calibration(video,Path.home()/'.cache/objectdetect/naver-cctv',size,caldir,'cuda',3000,3)
        save(caldir/'calibration.json',dict(H=H.tolist(),hull=hull.tolist(),**info))
        try:
            import torch
            torch.cuda.empty_cache()
        except ImportError:pass
        accepted=[];allrows=[]
        for segment in range(p['max_windows']):
            start=segment*900;end=min((segment+1)*900,frames/fps)
            if end-start<60:break
            tag=p['tag']+'_'+task['key']+'_w'+str(segment).zfill(2)
            pipeline=window_pipeline(root,tag,row,start,end,fps,frames)
            # No foreign camera zones/Colonial truth transferred. Fixed model/count filters.
            if (root/'counts'/pipeline['env']['RUN']).exists():raise ValueError('Existing pipeline run: '+pipeline['env']['RUN'])
            window=out/'windows'/('w'+str(segment).zfill(2));window.mkdir(parents=True)
            save(window/'pipeline_task.json',pipeline)
            status.update(stage='window_inference',active_window=segment)
            snapshot(directory,task,status)
            with (window/'pipeline.log').open('w') as log:
                subprocess.run([sys.executable,str(Path(__file__).resolve()),'window','--directory',str(directory),'--index',str(index),'--window',str(window)],stdout=log,stderr=subprocess.STDOUT,check=True)
            result=json.loads((window/'result.json').read_text())
            rawlog=Path(result['run_log']);shutil.copy2(rawlog,window/'run_log.json')
            raw=json.loads(rawlog.read_text())
            for field in ('tracks_csv','trajectories_csv','bin_counts_csv'):
                source=Path(raw.get(field,''))
                if source.is_file():shutil.copy2(source,window/source.name)
            status['stage']='speed_estimation';snapshot(directory,task,status)
            rr=gather_window(Path(result['run_log']),H,hull,start,end,task,segment,p['exploratory_road_plane_transfer'])
            eligible_count=select_chronologically(accepted,rr,task['target'])
            allrows+=rr
            status['windows'].append(dict(segment=segment,source_start_seconds=start,source_end_seconds=end,clock_start=(dt.datetime.fromisoformat(row['clock'])+dt.timedelta(seconds=start)).isoformat(sep=' '),clock_end=(dt.datetime.fromisoformat(row['clock'])+dt.timedelta(seconds=end)).isoformat(sep=' '),run_log=result['run_log'],found_candidate_tracks=len(rr),counted_candidate_tracks=sum(r['counted']=='1' for r in rr),eligible_candidates=eligible_count,cumulative_selected=len(accepted)))
            status['samples']=accepted;write_rows(out/'all_bicycle_candidates.csv',allrows);snapshot(directory,task,status)
            if len(accepted)>=task['target']:break
        status.update(state='TARGET_REACHED_PROVISIONAL' if len(accepted)>=task['target'] else 'TARGET_NOT_REACHED_WITHIN_LIMIT',samples=accepted)
        write_rows(out/'selected_bicycle_candidates.csv',accepted)
    except Exception as exc:
        status.update(state='FAILED',failure=str(exc));(out/'error.txt').write_text(traceback.format_exc())
    finally:
        status['stage']='finished';snapshot(directory,task,status)
    if status['state']=='FAILED':raise RuntimeError(status['failure'])


def report(directory,task=None):
    p=json.loads((directory/'manifest.json').read_text());rows=[];samples=[];all_candidates=[]
    destination=directory/task['key'] if task is not None else directory
    if task is not None:p['tasks']=[task]
    for task in p['tasks']:
        statusfile=directory/task['key']/'status.json';s=json.loads(statusfile.read_text()) if statusfile.exists() else dict(state='NO_STATUS',samples=[],windows=[],failure='No final worker status')
        selected=s.get('samples',[]);values=[float(r['speed_mph']) for r in selected];mean=float(np.mean(values)) if values else None
        samples+=selected
        candidate_file=directory/task['key']/'all_bicycle_candidates.csv'
        candidate_rows=None
        if candidate_file.exists():
            with candidate_file.open() as f:candidate_rows=list(csv.DictReader(f))
            all_candidates+=candidate_rows
        windows=s.get('windows',[])
        found=sum(w['found_candidate_tracks'] for w in windows) if windows and all('found_candidate_tracks' in w for w in windows) else ''
        counted=sum(w['counted_candidate_tracks'] for w in windows) if windows and all('counted_candidate_tracks' in w for w in windows) else ''
        eligible=sum(w['eligible_candidates'] for w in windows) if windows and all('eligible_candidates' in w for w in windows) else ''
        if candidate_rows is not None:
            found=len(candidate_rows);counted=sum(r.get('counted')=='1' for r in candidate_rows);eligible=sum(r.get('eligible')=='1' for r in candidate_rows)
        rows.append(dict(location=task['reference_site'],camera=task['source']['site'],study_cyclists=task['reference_count'],study_mean_mph=task['reference_mean_mph'],target=task['target'],found_candidate_tracks=found,counted_candidate_tracks=counted,speed_eligible_candidate_tracks=eligible,model_candidate_sample=len(values),model_candidate_mean_mph=mean if mean is not None else '',difference_from_study_mean_mph=mean-task['reference_mean_mph'] if mean is not None else '',state=s['state'],source_recording_date=task['source']['study_date'],source_clock_status=task['source']['clock_status'],minutes_processed=sum(w['source_end_seconds']-w['source_start_seconds'] for w in s.get('windows',[]))/60,video_intervals=json.dumps(s.get('windows',[])),failure=s.get('failure',''),interpretation='provisional_unmatched_group_comparison; identity_type_and_plane_transfer_unverified'))
    write_rows(destination/'comparison.csv',rows);write_rows(destination/'selected_candidates.csv',samples);write_rows(destination/'all_candidate_timestamps.csv',all_candidates)
    lines=['# Adaptive bicyclist-candidate speed comparison','','Each site processes consecutive15-minute windows until its candidate quota or the stated time limit. Means combine selected per-candidate speeds with equal weight, not averages of segment averages. Selection is chronological, never based on similarity to study speeds.','', '| Location | Study n | Study mean mph | Target | Found tracks | Speed-usable | Used for mean | Model mean mph | Difference mph | Minutes | State |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|']
    number=lambda x:'' if x=='' else f'{x:.2f}'
    for r in rows:lines.append(f"| {r['location']} | {r['study_cyclists']} | {r['study_mean_mph']:.2f} | {r['target']} | {r['found_candidate_tracks']} | {r['speed_eligible_candidate_tracks']} | {r['model_candidate_sample']} | {number(r['model_candidate_mean_mph'])} | {number(r['difference_from_study_mean_mph'])} | {r['minutes_processed']:.2f} | {r['state']} |")
    lines+=['','## Exact measurement times','','| Location | Window | Candidate | Used clock start | Used clock end | mph |','|---|---:|---|---|---|---:|']
    for r in samples:lines.append(f"| {r['site']} | {r['segment']} | {r['track_id']} | {r['measurement_start']} | {r['measurement_end']} | {r['speed_mph']} |")
    lines+=['', 'all_candidate_timestamps.csv includes every bicycle-labelled candidate track with first/last seen clock times, source and annotated paths, speed-measurement intervals and exclusion reasons. selected_candidates.csv contains only candidates used in the reported average. Found tracks includes rejected candidates and is not a verified unique-person count; counted tracks and speed-usable tracks are separate in comparison.csv. Unknown counts from failed/missing stages remain blank.', '', 'Missing speed is not zero. These are provisional bicycle candidates: the current detector combines bicycles/motorcycles; person identities and user types require visual checking. Boundary-censored candidates are excluded to reduce duplicate counts across segments, but fragmentation inside segments can still duplicate people. Rejected count-filter tracks do not silently become counted bicycles.','',f"Exploratory road-plane transfer enabled: {p['exploratory_road_plane_transfer']}. When enabled, out-of-car-support estimates assume the road and bicycle surface are approximately coplanar; strict_supported_speed_mph and support fractions are retained separately. No distance is fitted to workbook averages. These estimates are not independently validated physical speeds.", '', 'Camera aliases and facility correspondence remain candidate matches. No individual study records are linked to video people. Study averages lack observation timestamps. Calibration insufficiency stops a site before expensive repeated windows. No fixed full-hour processing when target is reached earlier.','', 'Colonial location-wide study mean pools bike lane and sidewalk; it is not a facility-matched validation. Only the selected source hour is sampled, not all four labelled clips. See the reference README for separate facility means.', '', 'Debugging: status.json records the current stage and completed windows; error.txt contains a worker traceback. windows/wNN/pipeline.log captures inference output, pipeline_task.json stores exact settings, result.json and run_log.json point to raw outputs and annotated videos. Calibration diagnostics are in calibration/. Slurm termination may leave the last in-progress stage; consult site_ARRAY_INDEX.log in the batch root.', '', 'Skipped: '+json.dumps(p['skipped'])]
    (destination/'RESULTS.md').write_text('\n'.join(lines)+'\n')


def submit(a):
    root=a.root.resolve();p=make_plan(root,a.tag,a.max_windows,a.exploratory_road_plane_transfer);directory=root/'exp_results'/('ADAPTIVE_SPEED_'+a.tag)
    print('Output:',directory)
    for t in p['tasks']:print(t['reference_site'],t['source']['site'],'reference',t['reference_count'],'target',t['target'])
    print('Skipped:',p['skipped']);print('Maximum footage minutes:',len(p['tasks'])*a.max_windows*15)
    if not a.go:print('Dry run; add --go on HiPerGator.');return
    if not shutil_which('sbatch'):raise RuntimeError('Submit on HiPerGator')
    for task in p['tasks']:
        if not Path(task['source']['video']).is_file():raise FileNotFoundError(task['source']['video'])
    weight=root.parent.parent/'runs/detect/finetune_runs/rtdetr_v3/weights/best.pt'
    if not weight.is_file():raise FileNotFoundError(weight)
    directory.mkdir(parents=True,exist_ok=False);save(directory/'manifest.json',p)
    env='cd '+shlex.quote(str(root))+' && source /orange/xiangyan/rithika/vision/yolo_env/bin/activate && '
    common=['sbatch','--parsable','--partition=hpg-turin','--account=xiangyan','--qos=xiangyan']
    cmd=common+['--job-name=adaptive_bicycle_speed','--array=0-'+str(len(p['tasks'])-1)+'%2','--gpus=1','--cpus-per-task=4','--mem=32G','--time=08:00:00','--output='+str(directory/'site_%A_%a.log'),'--wrap',env+'python code/adaptive_speed_batch.py worker --directory '+shlex.quote(str(directory))+' --index "$SLURM_ARRAY_TASK_ID"']
    job=subprocess.check_output(cmd,text=True).strip().split(';')[0]
    if not job.isdigit():raise ValueError('Unexpected array job ID')
    p['jobs'].append(dict(stage='site_workers',id=job));save(directory/'manifest.json',p)
    final=common+['--job-name=adaptive_speed_report','--dependency=afterany:'+job,'--cpus-per-task=1','--mem=2G','--time=00:10:00','--output='+str(directory/'report_%j.log'),'--wrap',env+'python code/adaptive_speed_batch.py report --directory '+shlex.quote(str(directory))]
    job2=subprocess.check_output(final,text=True).strip().split(';')[0]
    if not job2.isdigit():raise ValueError('Unexpected report job ID')
    p['jobs'].append(dict(stage='comparison_report',id=job2));save(directory/'manifest.json',p);print('Submitted:',p['jobs'])


def shutil_which(name):
    import shutil
    return shutil.which(name)

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='command',required=True)
    s=sub.add_parser('submit');s.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);s.add_argument('--tag',default=dt.datetime.now().strftime('%Y%m%d_%H%M%S'));s.add_argument('--max-windows',type=int,default=4);s.add_argument('--exploratory-road-plane-transfer',action='store_true');s.add_argument('--go',action='store_true')
    w=sub.add_parser('worker');w.add_argument('--directory',type=Path,required=True);w.add_argument('--index',type=int,required=True)
    v=sub.add_parser('window');v.add_argument('--directory',type=Path,required=True);v.add_argument('--index',type=int,required=True);v.add_argument('--window',type=Path,required=True)
    r=sub.add_parser('report');r.add_argument('--directory',type=Path,required=True)
    a=ap.parse_args()
    if a.command=='submit':
        if not 1<=a.max_windows<=4 or not a.tag or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in a.tag):ap.error('Tag must be simple letters/numbers/underscores; max-windows1–4')
        submit(a)
    elif a.command=='window':
        p=json.loads((a.directory/'manifest.json').read_text())
        result=execute(dict(root=p['root'],purpose='adaptive_speed_batch'),json.loads((a.window/'pipeline_task.json').read_text()),a.window)
        save(a.window/'result.json',result)
    elif a.command=='worker':worker(a.directory,a.index)
    else:report(a.directory)
