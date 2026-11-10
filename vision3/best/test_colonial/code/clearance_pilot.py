#!/usr/bin/env python3
"""One-command, bounded Colonial clearance/interaction research pilot."""
import argparse
import csv
import datetime as dt
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import traceback
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
CAL = 'reports/cluster_returns/20261024/colonial_speed_47545558_report_rebuilt/iccv2021/calibration.json'
SOURCE = 'MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/Standard_SCU8OG_2019-07-10_0000/Standard_SCU8OG_2019-07-10_0000.013.mp4'
# Existing manual cyclist encounters, fixed before looking at risk metrics.
WINDOWS = [('colonial_124020',2408.,30.,'manual/s03_colonial_north_2019-07-10_123000_manual_bicycle_observations.json'),
           ('colonial_125311',3179.,30.,'manual/s03_colonial_north_2019-07-10_124500_manual_bicycle_observations.json'),
           ('colonial_125350',3218.,30.,'manual/s03_colonial_north_2019-07-10_124500_manual_bicycle_observations.json')]


def save(path,data):
    path=Path(path);tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n');tmp.replace(path)


def table(path,rows,fields=None):
    if fields is None:fields=list(rows[0]) if rows else ['status']
    with Path(path).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)


def read(path):
    with Path(path).open(newline='') as f:return list(csv.DictReader(f))


def checksum(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def timestamp_audit(video):
    result=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries',
        'frame=best_effort_timestamp_time','-of','json',str(video)],capture_output=True,text=True,check=True)
    times=[float(r['best_effort_timestamp_time']) for r in json.loads(result.stdout)['frames'] if 'best_effort_timestamp_time' in r]
    import numpy as np
    delta=np.diff(times)
    if len(delta)<3 or not np.isfinite(delta).all() or (delta<=0).any():raise ValueError('Invalid/nonmonotonic frame timestamps')
    step=float(np.median(delta));irregular=float(np.mean(np.abs(delta-step)>max(.001,step*.05)))
    if irregular>.01:raise ValueError('Variable timing: refusing frame-index metric timing')
    return dict(frames=len(times),first_pts=times[0],last_pts=times[-1],median_step_s=step,
                fps_from_pts=1/step,irregular_fraction=irregular,max_step_s=float(delta.max()),
                scope='extracted pilot clip only; original source timing not independently verified')


def make_plan(a):
    # No detector imports or GPU work on login node.
    source=(a.source or a.data_root/SOURCE).resolve()
    calibration=(a.calibration or REPO/CAL).resolve()
    if not source.is_file():raise FileNotFoundError('Original camera source missing: '+str(source))
    if not calibration.is_file():raise FileNotFoundError('Saved Colonial calibration missing: '+str(calibration))
    weights=(a.weights or REPO/'vision3/runs/detect/finetune_runs/rtdetr_v3/weights/best.pt').resolve()
    if not weights.is_file():raise FileNotFoundError('Existing fine-tuned detector missing: '+str(weights))
    # This calibration has known camera/date/720x480 provenance. A different source
    # must be explicitly configured in code; basename equality alone is insufficient.
    if not source.name.endswith('.mp4'):raise ValueError('Pilot source must be an mp4 file')
    custom = a.start_s is not None
    if custom and a.duration <= 0:raise ValueError('Custom event duration must be positive')
    windows = ([(a.event_name, a.start_s, a.duration, 'custom_event')]
               if custom else WINDOWS)
    tasks=[]
    for key,start,duration,evidence in windows:
        for detector in ('reference','sensitive'):
            tasks.append(dict(key=key+'_'+detector,clip_key=key,start_s=start,duration_s=30.,
                              detector=detector,selection_evidence=evidence,
                              subject_kind=a.subject_kind))
            tasks[-1]['duration_s'] = duration
    stat=source.stat()
    chunk_match=re.search(r'\.(\d{3})\.mp4$',source.name)
    chunk_hour=int(chunk_match.group(1))-1 if chunk_match else 12
    source_clock=(dt.datetime(2019,7,10)+dt.timedelta(hours=chunk_hour)).isoformat(sep=' ')
    return dict(schema=1,root=str(ROOT),repo=str(REPO),source=str(source),source_bytes=stat.st_size,
        source_mtime_ns=stat.st_mtime_ns,source_sha256='not_hashed_large_original',
        calibration=str(calibration),calibration_sha256=checksum(calibration),
        weights=str(weights),weights_sha256=checksum(weights),tasks=tasks,
        unique_video_seconds=sum(t['duration_s'] for t in tasks[::2]),
        detector_video_seconds=sum(t['duration_s'] for t in tasks),
        subject_kind=a.subject_kind,
        source_clock=source_clock,clock_status='filename_inferred_not_independently_verified',
        camera='Colonial North',resolution=[720,480],jobs=[],
        interpretation='exploratory_assumed_footprints_learned_scale_not_verified_near_misses')


def submit(a):
    plan=make_plan(a)
    if not a.go:
        print(json.dumps(plan,indent=2));print('Dry run only. Add --go to submit one GPU job.');return
    if shutil.which('sbatch') is None:raise RuntimeError('sbatch is unavailable; submit from HiPerGator')
    tag=dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    directory=ROOT/'exp_results'/('CLEARANCE_PILOT_'+tag)
    directory.mkdir(parents=True,exist_ok=False)
    save(directory/'manifest.json',plan);save(directory/'status.json',dict(state='PREPARED'))
    cmd=['sbatch','--parsable','--output',str(directory/'slurm_%j.log'),
         '--chdir',str(ROOT),str(ROOT/'code/clearance_pilot.slurm'),str(directory)]
    # Record intent before submission; do not retry automatically if response is lost.
    save(directory/'submission.json',dict(command=cmd,state='SUBMITTING'))
    result=subprocess.run(cmd,capture_output=True,text=True)
    if result.returncode:
        save(directory/'submission.json',dict(command=cmd,state='FAILED',stderr=result.stderr))
        raise RuntimeError(result.stderr)
    job=result.stdout.strip().split(';')[0]
    if not job.isdigit():raise RuntimeError('Unexpected sbatch response; inspect scheduler before retrying: '+result.stdout)
    plan['jobs']=[job];save(directory/'manifest.json',plan)
    final_cmd=['sbatch','--parsable','--dependency=afterany:'+job,'--gpus=0',
        '--mem=4G','--time=00:10:00','--job-name=clearance_report',
        '--output',str(directory/'report_%j.log'),'--chdir',str(ROOT),
        str(ROOT/'code/clearance_pilot.slurm'),str(directory),'report']
    final=subprocess.run(final_cmd,capture_output=True,text=True)
    if final.returncode:
        save(directory/'report_submission.json',dict(state='FAILED',command=final_cmd,stderr=final.stderr))
        print('GPU job is already submitted. Finalizer submission failed: '+final.stderr, file=sys.stderr)
    else:
        final_id=final.stdout.strip().split(';')[0]
        plan['jobs'].append(final_id);save(directory/'manifest.json',plan)
        save(directory/'report_submission.json',dict(state='SUBMITTED',job_id=final_id,command=final_cmd))
    save(directory/'submission.json',dict(command=cmd,state='SUBMITTED',job_id=job))
    print('Submitted job '+job+'\nResults: '+str(directory/'RESULTS.md')+'\nReview: '+str(directory/'review.html'))


def ffmpeg_sync_arguments(executable):
    help_text=subprocess.run([executable,'-hide_banner','-h','full'],capture_output=True,text=True,check=True)
    options=help_text.stdout+'\n'+help_text.stderr
    if '-fps_mode' in options:return ['-fps_mode','passthrough']
    if '-vsync' in options:return ['-vsync','0']
    raise RuntimeError('FFmpeg has neither fps_mode nor vsync; cannot preserve frame timing')


def extract(plan,task,directory):
    import cv2
    source=Path(plan['source']);cap=cv2.VideoCapture(str(source))
    try:
        fps=cap.get(5);frames=cap.get(7);size=[int(cap.get(3)),int(cap.get(4))]
        duration = float(task.get('duration_s', 30.))
        if size!=plan['resolution'] or fps<=0 or frames/fps<task['start_s']+duration:raise ValueError('Wrong resolution, timing, or source too short')
    finally:cap.release()
    clips=directory/'inputs';clips.mkdir(exist_ok=True)
    video=clips/(task['clip_key']+'.mp4')
    if not video.exists():
        from preview_ffmpeg import resolve
        executable=plan.get('ffmpeg') or resolve()
        sync=plan.get('ffmpeg_sync_args') or ffmpeg_sync_arguments(executable)
        partial=video.with_name(video.stem+'.partial.mp4')
        command=[executable,'-nostdin','-y','-v','error','-ss',str(task['start_s']),'-i',str(source),
            '-t',str(task.get('duration_s',30.)),'-map','0:v:0','-an','-c:v','libx264','-preset','fast','-crf','18',
            *sync,'-movflags','+faststart',str(partial)]
        try:
            result=subprocess.run(command,capture_output=True,text=True)
            diagnostic=dict(command=command,returncode=result.returncode,
                            stdout=result.stdout,stderr=result.stderr)
            save(clips/(task['clip_key']+'_extraction.json'),diagnostic)
            if result.returncode:
                raise RuntimeError('FFmpeg extraction failed: '+(result.stderr.strip() or 'no stderr')[-3000:])
            if not partial.is_file() or partial.stat().st_size==0:
                raise RuntimeError('FFmpeg returned success but produced no clip')
            # Audit before publication so another detector never reuses an
            # incomplete/invalid extraction as a completed input.
            timestamp_audit(partial)
            partial.replace(video)
        finally:
            if partial.exists():partial.unlink()
    audit=timestamp_audit(video)
    audit['sha256']=checksum(video)
    save(clips/(task['clip_key']+'_timing.json'),audit)
    duration = float(task.get('duration_s', 30.))
    if not duration - 2 <= audit['last_pts']-audit['first_pts']<=duration + .1:raise ValueError('Incomplete extracted clip')
    if abs(audit['fps_from_pts']/fps-1)>.005:raise ValueError('Extracted timing differs from source metadata')
    return video,audit


def infer(plan,task,video,directory):
    from run_batch5 import parse_envv
    from research_worker import execute
    base=dict(parse_envv(ROOT/'code/run_batch4.sh','5'))
    clock=dt.datetime.fromisoformat(plan['source_clock'])+dt.timedelta(seconds=task['start_s'])
    run=directory.name.lower()+'_'+task['key']
    env={**base,'RUN':run,'VIDEO_OVERRIDE':str(video),'CHUNK':'1','SLURM_ARRAY_TASK_ID':'1',
         'START_FRAME':'1','MAX_FRAMES':'0','SESSION_START':clock.strftime('%Y-%m-%d_%H:%M:%S'),
         'WEIGHTS':plan['weights'],'ZONES_JSON':str(ROOT/'zones/colonial_north_v1.json'),
         'EXPORT_VEHICLE_TRAJECTORIES':'1','STREAM_CLIPS':'0','GT_XLS':'none',
         'CLOCK_NOTE':'30-second crop; source clock inferred; exploratory clearance pilot',
         'BIC_MIN_SEC':'1.5','PED_MIN_SEC':'3','STITCH_SEC':'0.5','STITCH_PX':'60',
         'LOST_SEC':'0.3','DET_CONF':'0.25','TRACK_THR':'0.25'}
    if task['detector']=='sensitive':
        env.update(DET_CONF='0.15',TRACK_THR='0.15',BIC_MIN_SEC='0.3',STATIC_FILTER='0')
    item=dict(key=task['key'],kind='pipeline',env=env)
    save(directory/task['key']/'pipeline_task.json',item)
    with (directory/task['key']/'pipeline.log').open('w') as output:
        # Existing execute uses subprocess inheriting fd 1/2. Route them without
        # shell interpolation; restore even on failure.
        one,two=os.dup(1),os.dup(2)
        try:
            sys.stdout.flush();sys.stderr.flush();os.dup2(output.fileno(),1);os.dup2(output.fileno(),2)
            result=execute(dict(root=str(ROOT),tag=directory.name),item,directory)
        finally:
            sys.stdout.flush();sys.stderr.flush();os.dup2(one,1);os.dup2(two,2);os.close(one);os.close(two)
    log=json.loads(Path(result['run_log']).read_text())
    # Copy small outputs next to the report for a self-contained download.
    for key in ('tracks_csv','trajectories_csv','vehicle_trajectories_csv'):
        path=Path(log.get(key) or '')
        if not path.is_file():raise ValueError('Required inference export missing: '+key)
        shutil.copy2(path,directory/task['key']/(key+'.csv'))
    save(directory/task['key']/'run_log.json',log)
    return log


def review_pairs(rows):
    chosen={}
    for r in rows:
        if r['scenario'] not in ('baseline','strict_False'):continue
        key=(r['task'],r['cyclist_id'],r['vehicle_id'])
        if key not in chosen or r['scenario']=='baseline':chosen[key]=r
    return list(chosen.values())


def write_event_selector(directory, plan):
        """Write a full-window browser tool for selecting a known event time."""
        task = plan['tasks'][0]
        clip = task['clip_key']
        source_clock = plan.get('source_clock', '')
        page = f'''<!doctype html>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Select interaction time</title>
<style>body{{font:16px system-ui;max-width:1000px;margin:24px auto;padding:0 16px;color:#17231f}}video{{width:100%;background:#111}}button,input,textarea{{font:inherit;padding:8px;margin:4px 4px 4px 0}}.note{{background:#eef5f1;padding:12px;border-left:4px solid #0b765e}}#readout{{font-size:20px;font-weight:700}}textarea{{width:100%;min-height:60px}}</style>
<h1>Select the pedestrian-car interaction time</h1>
<p class="note">Play or scrub the complete 60-second clip. Pause when the pedestrian and car are closest or when the crossing/near-miss occurs. Then click <b>Mark selected time</b>. This records a timestamp for later TTC/PET and edge review; it does not decide whether the event is a near miss.</p>
<video id="video" controls preload="metadata" src="inputs/{html.escape(clip)}.mp4"></video>
<p id="readout">Current clip time: 0.000 s</p>
<button id="back">Back one frame</button><button id="forward">Forward one frame</button><button id="mark">Mark selected time</button><button id="download">Download selections</button>
<label>Reviewer: <input id="reviewer"></label>
<textarea id="notes" placeholder="Describe what happens at the selected time, if useful."></textarea>
<h2>Selected times</h2><table id="table"><tr><th>Clip seconds</th><th>Inferred source clock</th><th>Notes</th></tr></table>
<script>
const video=document.getElementById('video'), readout=document.getElementById('readout');
const selections=[]; const sourceClock={json.dumps(source_clock)}; const fps=29.97;
function clockAt(offset){{
    if(!sourceClock) return '';
    const parts=sourceClock.split(' '), time=parts[1].split(':').map(Number);
    let seconds=time[0]*3600+time[1]*60+time[2]+offset; seconds=((seconds%86400)+86400)%86400;
    const h=String(Math.floor(seconds/3600)).padStart(2,'0'), m=String(Math.floor(seconds%3600/60)).padStart(2,'0'), s=(seconds%60).toFixed(3).padStart(6,'0');
    return parts[0]+' '+h+':'+m+':'+s;
}}
function update(){{readout.textContent='Current clip time: '+video.currentTime.toFixed(3)+' s | inferred source: '+clockAt(video.currentTime);}}
function render(){{const table=document.getElementById('table'); table.innerHTML='<tr><th>Clip seconds</th><th>Inferred source clock</th><th>Notes</th></tr>'; selections.forEach(row=>{{const tr=document.createElement('tr'); tr.innerHTML='<td>'+row.seconds.toFixed(3)+'</td><td>'+row.clock+'</td><td>'+row.notes+'</td>'; table.appendChild(tr);}});}}
video.ontimeupdate=update; document.getElementById('back').onclick=()=>{{video.currentTime=Math.max(0,video.currentTime-1/fps);update();}}; document.getElementById('forward').onclick=()=>{{video.currentTime=Math.min(video.duration||60,video.currentTime+1/fps);update();}};
document.getElementById('mark').onclick=()=>{{selections.push({{seconds:video.currentTime,clock:clockAt(video.currentTime),notes:document.getElementById('notes').value,reviewer:document.getElementById('reviewer').value}});render();}};
document.getElementById('download').onclick=()=>{{const lines=['clip_seconds,inferred_source_clock,reviewer,notes']; selections.forEach(row=>lines.push([row.seconds.toFixed(3),row.clock,row.reviewer,row.notes].map(value=>'"'+String(value).replaceAll('"','""')+'"').join(','))); const blob=new Blob([lines.join('\\n')+'\\n'],{{type:'text/csv'}}); const link=document.createElement('a'); link.href=URL.createObjectURL(blob); link.download='pedestrian_event_selections.csv'; link.click();}};
update();
</script>'''
        (directory/'event_time_selector.html').write_text(page)


def analyze(plan,task,directory,log):
    import numpy as np
    from clearance_metrics import prepare,road_axis,pair_metrics,scenarios
    out=directory/task['key']
    if checksum(plan['calibration'])!=plan['calibration_sha256']:raise ValueError('Calibration changed since submission')
    cal=json.loads(Path(plan['calibration']).read_text());H=np.asarray(cal['H'],float);hull=np.asarray(cal['hull'],np.float32)
    if cal.get('geometry_check_passed') is not True or H.shape!=(3,3) or not np.isfinite(H).all() or abs(np.linalg.det(H))<1e-12:
        raise ValueError('Saved calibration failed checks')
    labels={r['track_id']:r for r in read(out/'tracks_csv.csv')}
    paths=prepare(read(out/'trajectories_csv.csv')+read(out/'vehicle_trajectories_csv.csv'),H,hull,log['fps'],labels)
    subject_kind=plan.get('subject_kind','cyclist')
    vehicle_kinds=('car','bus','truck','vehicle','other_vehicle')
    axis_paths={k:v for k,v in paths.items() if k[0] == subject_kind or k[0] in vehicle_kinds}
    axis=road_axis(axis_paths, (subject_kind,))
    save(out/'geometry.json',dict(H=H.tolist(),hull=hull.tolist(),road_axis=axis.tolist(),
        calibration_source=plan['calibration'],calibration_sha256=plan['calibration_sha256'],
        validation=cal.get('validation'),footprints='assumed_dimensions_centered_on_projected_bottom_center'))
    subjects=[k for k in paths if k[0]==subject_kind];vehicles=[k for k in paths if k[0] in vehicle_kinds]
    rows=[];series=[];transfer_series=[];smoother_series=[]
    for name,scenario in scenarios():
        print(task['key'],name,flush=True)
        for ck in subjects:
            for vk in vehicles:
                r=pair_metrics(paths[ck],paths[vk],vk[0],axis,H,subject_kind=subject_kind,**scenario)
                if r is None:continue
                samples=r.pop('samples')
                record=dict(task=task['key'],clip=task['clip_key'],detector=task['detector'],
                    cyclist_id=ck[1],subject_kind=subject_kind,vehicle_id=vk[1],vehicle_type=vk[0],source_start_s=task['start_s'],
                    facility=paths[ck][0]['facility'],cyclist_identity=paths[ck][0]['identity_status'],
                    counted=paths[ck][0]['counted'],scenario=name,**scenario,**r,
                    calibration_validation=cal.get('validation','unvalidated'),
                    metric_status='exploratory_assumed_footprints',pet_cell_m=.5,
                    review_status='unreviewed',verified_near_miss='')
                record['source_clearance_time_s'] = task['start_s']+r['clearance_time_s'] if r['clearance_time_s'] is not None else None
                record['clearance_clock_inferred'] = (dt.datetime.fromisoformat(plan['source_clock'])+dt.timedelta(seconds=record['source_clearance_time_s'])).isoformat(sep=' ') if record['source_clearance_time_s'] is not None else ''
                rows.append(record)
                if scenario['motion'] in ('kalman','rts'):
                    smoother_series.extend(dict(scenario=name,cyclist_id=ck[1],vehicle_id=vk[1],**s) for s in samples)
                if name=='strict_False':
                    transfer_series.extend(dict(cyclist_id=ck[1],vehicle_id=vk[1],**s) for s in samples)
                if name=='baseline':
                    series.extend(dict(cyclist_id=ck[1],vehicle_id=vk[1],**s) for s in samples)
    table(out/'interactions.csv',rows);table(out/'baseline_timeseries.csv',series);table(out/'transfer_timeseries.csv',transfer_series)
    table(out/'kalman_rts_timeseries.csv',smoother_series)
    # Export review images at baseline closest approach / minimum clearance.
    cap=None
    try:
        import cv2
        video=directory/'inputs'/(task['clip_key']+'.mp4')
        cap=cv2.VideoCapture(str(video)) if video.is_file() else None
        for r in review_pairs(rows)[:12]:
            if cap is None:break
            t=r['clearance_time_s']
            if t is None:
                ss=[s for s in (series if r['scenario']=='baseline' else transfer_series) if s['cyclist_id']==r['cyclist_id'] and s['vehicle_id']==r['vehicle_id']]
                t=min(ss,key=lambda s:s['center_distance_m'])['t']
            frame_id=round(t*log['fps'])+1;cap.set(cv2.CAP_PROP_POS_FRAMES,frame_id-1);ok,image=cap.read()
            if not ok:continue
            for k,color in [((subject_kind,r['cyclist_id']),(0,255,255)),((r['vehicle_type'],r['vehicle_id']),(255,160,0))]:
                obs=min(paths[k],key=lambda x:abs(x['frame']-frame_id))
                x,y=obs['pixel'];w,h=obs['box_w'],obs['box_h']
                cv2.rectangle(image,(round(x-w/2),round(y-h)),(round(x+w/2),round(y)),color,2)
                cv2.putText(image,k[0]+' '+k[1],(round(x),max(30,round(y-h))),cv2.FONT_HERSHEY_SIMPLEX,.4,color,1)
            cv2.putText(image,'EXPLORATORY: verify IDs, geometry and pass',(8,18),cv2.FONT_HERSHEY_SIMPLEX,.45,(0,255,255),1)
            cv2.imwrite(str(out/f"c{r['cyclist_id']}_v{r['vehicle_id']}.jpg"),image)
    finally:
        if cap:cap.release()
    return dict(subject_candidates=len(subjects),subject_kind=subject_kind,vehicle_tracks=len(vehicles),interaction_rows=len(rows),
                baseline_pairs=sum(r['scenario']=='baseline' for r in rows))


def report(directory):
    plan=json.loads((directory/'manifest.json').read_text());rows=[];statuses=[]
    for task in plan['tasks']:
        out=directory/task['key'];status=out/'status.json'
        state=json.loads(status.read_text()) if status.exists() else dict(state='NO_FINAL_STATUS')
        statuses.append(dict(task=task['key'],**state))
        if state['state']=='SUCCEEDED' and (out/'interactions.csv').exists():rows.extend(read(out/'interactions.csv'))
    table(directory/'all_interactions.csv',rows)
    # Thresholds are sensitivity screens, not validated near-miss classifiers.
    thresholds=[]
    groups=defaultdict(list)
    for r in rows:groups[(r['detector'],r['scenario'])].append(r)
    for (detector,scenario),rr in groups.items():
        for metric,values in [('min_sampled_clearance_m',(.5,1.,1.5)),('min_collision_ttc_s',(1.,1.5,2.)),('sampled_occupancy_pet_s',(.5,1.,1.5))]:
            valid=[float(r[metric]) for r in rr if r[metric]!='']
            for threshold in values:
                thresholds.append(dict(detector=detector,scenario=scenario,metric=metric,threshold=threshold,
                    eligible_pairs=len(valid),pairs_below=sum(v<threshold for v in valid),
                    interpretation='screening_only_not_verified_near_miss_count'))
    table(directory/'threshold_sensitivity.csv',thresholds)
    from clearance_review import screening_reports
    screening_reports(directory,rows)
    table(directory/'task_status.csv',[dict(task=r['task'],state=r['state'],error=r.get('error','')) for r in statuses])
    baseline=[r for r in rows if r['scenario']=='baseline']
    review_rows=review_pairs(rows)
    lines=['# Colonial passing-clearance pilot','',
        f"Tasks succeeded: {sum(r['state']=='SUCCEEDED' for r in statuses)}/{len(statuses)}. Subject kind: {plan.get('subject_kind','cyclist')}. Unique footage and detector seconds are recorded in manifest.json.",
        '', 'Clearance is the primary output. Metric estimates use the existing learned camera mapping and assumed object dimensions centered on projected box bottom-centers. They are exploratory estimates, not independently calibrated measurements. Box-edge output is a projection proxy, not recovered physical clearance.',
        '', 'Open review.html, all_interactions.csv, threshold_sensitivity.csv and task_status.csv. Copy review_candidates.csv to review_labels.csv before adding your review; the generated candidate template updates as tasks finish. Each task contains raw exports, geometry, baseline_timeseries.csv, transfer_timeseries.csv, pipeline log and diagnostic snapshots. inputs/ contains original-view 30-second review clips and timing audits. IDs reset across clips and detector settings; do not sum variants as distinct people/events.',
        '', f'Baseline pair rows: {len(baseline)} across detector settings. Failed tasks do not become zero interactions. Candidate selection was based on existing manual cyclist times, not low TTC or small clearance. Visible cyclists are documented; a completed pass in these short windows is not presumed.',
        '', 'Methods: assumed-footprint lateral edge gap while longitudinally alongside; center distance; projected bottom-box-edge proxy; continuous swept-rectangle collision TTC (5-second horizon); predicted closest center approach; sampled shared-cell occupancy PET (0.5m grid). PET and TTC are based on assumed road-aligned rectangles and constant local velocity. This is a paper-informed implementation, not a reproduction of a published benchmark.',
        '', 'Variations: reference versus sensitive detector; local velocity/smoothing windows 0.25/0.5/1.0s; cyclist envelope width 0.6/0.8/1.0m; learned scale multipliers 0.8/1.0/1.2; strict car-support versus exploratory plane transfer; constant-velocity Kalman filtering and offline RTS smoothing, each with strict and transfer support. Twelve scenarios per detector use the same inference. These are one-factor-at-a-time sensitivity tests, not a full factorial experiment or confidence intervals. Car dimensions 4.5x1.8m, truck 8x2.5m, bus 12x2.5m, bicycle length 1.8m are explicit assumptions.',
        '', 'smoothing_comparison.csv compares minimum footprint distance, lateral clearance, TTC and PET against local-fit baselines on matched IDs/support settings. screening_comparison.csv compares distance/PET alone and AND/OR screens; it does not claim an optimal predictor. false_alarm_review.csv reports adjudicated false flags / adjudicated flags only when review_labels.csv contains yes/no near_miss_review and reviewer. Unreviewed flags and adjudication coverage remain explicit; this is not a population false-positive rate. No LiDAR/radar observations exist in this workflow. The user-supplied 84% false-alarm figure has no verified source and is not treated as this pilot\'s rate.',
        '', 'Every outcome requires video review of subject identity, track continuity, alongside geometry, direction, occlusion, barriers and truncation. The observed_overtake_candidate flag requires relative order reversal during a continuous same-direction span; alongside alone does not establish overtaking. A zero gap/TTC/PET is model overlap, not evidence of collision. No verified near-miss classification is generated.',
        '', 'Strict support means projected contact points are inside the existing car-calibration hull; it does not verify sidewalks, edge extents or true dimensions. Plane transfer assumes coplanarity and is diagnostic. Review pages use a strict baseline pair where available, otherwise an explicitly labelled plane-transfer pair. The road axis comes from vehicle motion in each crop; curves/lane changes violate fixed-road-axis assumptions. Shared-cell PET is spatially and temporally quantized and can overstate conflicts. Velocities do not bridge observation gaps >0.20s. Timing audit covers extracted clips only. Clip-edge censoring and incomplete coverage require review; no 48-hour rates are calculated.',
        '', 'Research sources: [FHWA definitions of TTC/PET](https://www.fhwa.dot.gov/publications/research/safety/08051/02.cfm); [2025 experimental analysis of automated video safety errors](https://arxiv.org/abs/2503.09807); [existing ICCV2021 calibration author implementation](https://github.com/naver/cctv); [trajectory study using RTS smoothing](https://tsr.international/TSR/article/download/27904/24728?inline=1). Recent safety research supports checking tracking and calibration rather than interpreting automated flags as verified conflicts.',
        '', '| Task | State | Detail |','|---|---|---|']
    for r in statuses:lines.append(f"| {r['task']} | {r['state']} | {str(r.get('error',r.get('result',''))).replace('|','/')} |")
    (directory/'RESULTS.md').write_text('\n'.join(lines)+'\n')
    sections=['<!doctype html><meta charset="utf-8"><title>Clearance pilot review</title><style>body{font:16px system-ui;max-width:1100px;margin:30px auto}video,img{max-width:720px;width:100%}section{border-top:1px solid #ccc;padding:20px 0}td,th{padding:6px;border:1px solid #ddd}table{border-collapse:collapse}</style>',
        '<h1>Exploratory clearance pilot</h1><p>Verify identity, passing direction, barriers, geometry and truncation. These are candidates; no verified near misses. Read RESULTS.md and all_interactions.csv.</p>']
    for task in plan['tasks']:
        sections.append('<section><h2>'+html.escape(task['key'])+'</h2>')
        sections.append(f'<video controls preload="metadata" src="inputs/{task["clip_key"]}.mp4"></video>')
        for r in review_rows:
            if r['task']!=task['key']:continue
            sections.append('<p>'+html.escape(f"Scenario {r['scenario']}: {r.get('subject_kind',plan.get('subject_kind','cyclist'))} {r['cyclist_id']} / vehicle {r['vehicle_id']}: estimated clearance {r['min_sampled_clearance_m'] or 'unavailable'} m; TTC {r['min_collision_ttc_s'] or 'no collision course'} s; PET {r['sampled_occupancy_pet_s'] or 'no shared cells'} s; overtake candidate {r['observed_overtake_candidate']}")+'</p>')
            snap=f"{task['key']}/c{r['cyclist_id']}_v{r['vehicle_id']}.jpg"
            if (directory/snap).exists():sections.append(f'<img loading="lazy" src="{html.escape(snap)}">')
        # A known event timestamp deserves a direct still image; candidate
        # selection alone can omit a real crossing from the snapshot list.
        event_offset = task.get('review_offset_s')
        if event_offset is None and plan.get('subject_kind') == 'pedestrian' and task.get('duration_s') == 60.:
            event_offset = 48.
        if event_offset is not None:
            video = directory/'inputs'/(task['clip_key']+'.mp4')
            event_image = directory/task['key']/f'event_at_{event_offset:g}s.jpg'
            if video.is_file():
                import cv2
                cap = cv2.VideoCapture(str(video)); fps = cap.get(cv2.CAP_PROP_FPS) or 29.97
                cap.set(cv2.CAP_PROP_POS_FRAMES, round(float(event_offset)*fps))
                ok, image = cap.read(); cap.release()
                if ok and cv2.imwrite(str(event_image), image):
                    relative = f"{task['key']}/{event_image.name}"
                    sections.append(f'<h3>Known event time: crop +{float(event_offset):g}s</h3><p>This is the requested pedestrian crossing time. Review identity and visible edges here before interpreting metrics.</p><img loading="lazy" src="{html.escape(relative)}">')
        sections.append('</section>')
    (directory/'review.html').write_text('\n'.join(sections))
    write_event_selector(directory, plan)
    review=[dict(task=r['task'],scenario=r['scenario'],cyclist_id=r['cyclist_id'],vehicle_id=r['vehicle_id'],cyclist_confirmed='',
        car_passing_confirmed='',same_direction='',barrier_present='',occlusion='',truncated='',
        clearance_geometry_usable='',near_miss_review='',reviewer='',notes='') for r in review_rows]
    # Preserve user review edits when regenerating reports.
    table(directory/'review_candidates.csv',review)


def run(directory):
    directory=directory.resolve();plan=json.loads((directory/'manifest.json').read_text())
    save(directory/'status.json',dict(state='RUNNING',stage='preflight'))
    try:
        if any((directory/t['key']).exists() for t in plan['tasks']):raise ValueError('Run already started; refusing duplicate inference')
        if shutil.which('ffprobe') is None:raise RuntimeError('ffprobe is required; load the cluster ffmpeg module')
        from preview_ffmpeg import resolve
        plan['ffmpeg']=resolve()
        plan['ffmpeg_sync_args']=ffmpeg_sync_arguments(plan['ffmpeg'])
        save(directory/'ffmpeg_runtime.json',dict(executable=plan['ffmpeg'],sync_args=plan['ffmpeg_sync_args'],
            version=subprocess.run([plan['ffmpeg'],'-version'],capture_output=True,text=True,check=True).stdout))
        import torch
        if not torch.cuda.is_available():raise RuntimeError('GPU unavailable in the scheduled job')
        for name in ('ultralytics','supervision','transformers','cv2','numpy'):
            __import__(name)
        if checksum(plan['calibration'])!=plan['calibration_sha256'] or checksum(plan['weights'])!=plan['weights_sha256']:
            raise ValueError('Calibration or model changed after submission')
        stat=Path(plan['source']).stat()
        if (stat.st_size,stat.st_mtime_ns)!=(plan['source_bytes'],plan['source_mtime_ns']):raise ValueError('Source changed after submission')
        for task in plan['tasks']:
            out=directory/task['key'];out.mkdir()
            save(out/'status.json',dict(state='RUNNING',stage='extract'))
            save(directory/'status.json',dict(state='RUNNING',task=task['key']))
            try:
                video,audit=extract(plan,task,directory)
                save(out/'status.json',dict(state='RUNNING',stage='inference'))
                log=infer(plan,task,video,directory)
                save(out/'status.json',dict(state='RUNNING',stage='metrics'))
                result=analyze(plan,task,directory,log)
                save(out/'status.json',dict(state='SUCCEEDED',result=result))
            except Exception as exc:
                (out/'error.txt').write_text(traceback.format_exc())
                save(out/'status.json',dict(state='FAILED',error=str(exc)))
            report(directory)
        states=[json.loads((directory/t['key']/'status.json').read_text())['state'] for t in plan['tasks']]
        save(directory/'status.json',dict(state='FINISHED' if all(s=='SUCCEEDED' for s in states) else 'FINISHED_WITH_FAILURES'))
        if any(s!='SUCCEEDED' for s in states):raise RuntimeError('Some tasks failed; see RESULTS.md and per-task error.txt')
    except Exception as exc:
        save(directory/'status.json',dict(state='FAILED',error=str(exc)))
        (directory/'error.txt').write_text(traceback.format_exc())
        raise
    finally:
        report(directory)


def reanalyze(directory):
    """CPU-only method update from saved raw exports; preserve prior analyses."""
    directory=directory.resolve();plan=json.loads((directory/'manifest.json').read_text())
    stamp=dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    for task in plan['tasks']:
        out=directory/task['key']
        required=['run_log.json','tracks_csv.csv','trajectories_csv.csv','vehicle_trajectories_csv.csv']
        if not all((out/name).is_file() for name in required):continue
        backup=out/'analysis_history'/stamp;backup.mkdir(parents=True)
        for path in out.glob('*.csv'):
            if path.name not in required:shutil.copy2(path,backup/path.name)
        for name in ('geometry.json','status.json'):
            if (out/name).exists():shutil.copy2(out/name,backup/name)
        try:
            result=analyze(plan,task,directory,json.loads((out/'run_log.json').read_text()))
            save(out/'status.json',dict(state='SUCCEEDED',result=result,reanalyzed=stamp))
        except Exception as exc:
            (out/'analysis_error.txt').write_text(traceback.format_exc())
            save(out/'status.json',dict(state='FAILED',error=str(exc),reanalyzed=stamp))
    report(directory)


def main():
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='command',required=True)
    a=s.add_parser('submit');a.add_argument('--go',action='store_true');a.add_argument('--source',type=Path)
    a.add_argument('--data-root',type=Path,default=Path('/orange/xiangyan/rithika/vision/pilot_clips'))
    a.add_argument('--calibration',type=Path);a.add_argument('--weights',type=Path)
    a.add_argument('--subject-kind',choices=('cyclist','pedestrian'),default='cyclist')
    a.add_argument('--event-name',default='custom_event')
    a.add_argument('--start-s',type=float,default=None)
    a.add_argument('--duration',type=float,default=30.)
    a=s.add_parser('run');a.add_argument('directory',type=Path)
    a=s.add_parser('report');a.add_argument('directory',type=Path)
    a=s.add_parser('reanalyze');a.add_argument('directory',type=Path)
    a=p.parse_args()
    if a.command=='submit':submit(a)
    elif a.command=='run':run(a.directory)
    elif a.command=='reanalyze':reanalyze(a.directory)
    else:report(a.directory.resolve())


if __name__=='__main__':main()
