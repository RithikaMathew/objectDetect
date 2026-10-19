#!/usr/bin/env python3
"""Run one suite task, record an atomic status, and collect a final report."""
import csv
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import sysconfig
import traceback


def atomic_json(path, data):
    tmp=path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data,indent=2))
    tmp.replace(path)


def run(cmd, **kw):
    print('RUN:',repr([str(c) for c in cmd]),flush=True)
    return subprocess.run([str(c) for c in cmd],check=True,**kw)


def execute(plan, task, directory):
    root=Path(plan['root']); code=root/'code'; key=task['key']
    env=os.environ.copy()
    if task['kind']=='pipeline':
        # Remove inherited experiment switches so each named test is controlled.
        for name in re.findall(r'\$\{([A-Z][A-Z0-9_]*)', (code/'run_xclip_colonial_v19.slurm').read_text()):
            env.pop(name,None)
        env.update(task['env'])
        if task.get('higher_resolution'):
            import cv2
            cap=cv2.VideoCapture(env['VIDEO_OVERRIDE']);w=cap.get(3);h=cap.get(4);fps=cap.get(5);cap.release()
            if w*h<=720*480 or fps<=0:raise RuntimeError('higher-resolution clip is unreadable or not above 720x480')
            scale=w/720
            env.update(STITCH_PX=str(150*scale),SPLIT_PX=str(120*scale),
                       SAHI_SLICE=str(max(32,round(640*scale/32)*32)),STATIC_MAX_NET_PX=str(5*scale))
        run(['bash',code/'run_xclip_colonial_v19.slurm'],cwd=root,env=env)
        records=list((root/'logs'/env['RUN']).glob('*_run_log.json'))
        if task.get('eval_clip'):
            records=[p for p in records if f'.{int(env["CHUNK"]):03d}_run_log.json' in p.name]
        if len(records)!=1:raise RuntimeError('no unique final run JSON; task is incomplete')
        result=json.loads(records[0].read_text())
        if result['frames_processed']<=0:raise RuntimeError('pipeline processed no frames')
        for field in ('tracks_csv','bin_counts_csv'):
            if not Path(result[field]).is_file():raise RuntimeError(f'missing final {field}')
        return dict(run_log=str(records[0]),final_counts=result['final_counts'],runtime_s=result['runtime_s'])
    if task['kind']=='setup':
        venv=root/'.research_env'/plan['tag']; python=venv/'bin/python'
        if not python.exists():run([sys.executable,'-m','venv','--system-site-packages',venv])
        # A nested venv does not automatically inherit the parent venv's Torch.
        # Append the working environment's packages after this env's own paths.
        site=Path(subprocess.check_output([str(python),'-c',
            'import sysconfig; print(sysconfig.get_path("purelib"))'],text=True).strip())
        (site/'working_yolo_environment.pth').write_text('\n'.join(dict.fromkeys(
            sysconfig.get_path(k) for k in ('purelib','platlib')))+'\n')
        run([python,'-m','pip','install','--disable-pip-version-check','transformers==4.49.0'])
        # Network allowed only in this preparation process; subsequent DINO tasks are offline.
        env.update(HF_HUB_OFFLINE='0',TRANSFORMERS_OFFLINE='0')
        run([python,code/'grounding_audit.py','prepare','--root',root,'--ready',directory/'grounding_ready.json'],env=env)
        return json.loads((directory/'grounding_ready.json').read_text())
    if task['kind']=='grounding':
        ready=directory/'grounding_ready.json'
        if not ready.is_file():raise RuntimeError('Grounding setup failed or did not finish; see grounding_setup log')
        out=directory/'grounding'/task['clip']
        env.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
        run([root/'.research_env'/plan['tag']/'bin/python',code/'grounding_audit.py','audit','--root',root,'--ready',ready,
             '--clip',task['clip'],'--video',task['video'],'--out',out],env=env)
        return dict(output=str(out),**json.loads((out/'summary.json').read_text()))
    if task['kind']=='scan':
        out=directory/'busy/inventory.csv';out.parent.mkdir(parents=True,exist_ok=True)
        run([sys.executable,code/'pick_busy_windows.py','--list',root/'videos_to_scan.txt',
             '--out',out,'--higher-res-only'],cwd=root)
        with out.open() as f:rows=list(csv.DictReader(f))
        if not rows:raise RuntimeError('no readable scan videos; inspect input paths')
        return dict(inventory=str(out),windows=str(out.with_name('windows.txt')),
                    higher_resolution_sources=sum(r['higher_resolution']=='True' for r in rows))
    if task['kind']=='previews':
        import cv2
        from submit_research import VIDEO_DIR
        out=directory/'previews';out.mkdir(parents=True,exist_ok=True)
        source=VIDEO_DIR/'Standard_SCU8OG_2019-07-10_0000.013.mp4'
        cap=cv2.VideoCapture(str(source));cap.set(cv2.CAP_PROP_POS_MSEC,300000);ok,frame=cap.read();cap.release()
        if not ok:raise RuntimeError('could not extract Colonial zone-check frame')
        raw=out/'colonial.png'
        if not cv2.imwrite(str(raw),frame):raise RuntimeError('could not write zone frame')
        run([sys.executable,code/'draw_zones_preview.py','--zones',root/'zones/colonial_north_v2.json',
             '--image',raw,'--out',out/'colonial_zones_v2.png'])
        higher=root/'newvideo/corrine_706_15min.mp4'
        if higher.is_file():
            cap=cv2.VideoCapture(str(higher));cap.set(cv2.CAP_PROP_POS_MSEC,30000);ok,frame=cap.read();cap.release()
            if not ok:raise RuntimeError('could not extract Corrine fisheye preview frame')
            raw=out/'corrine_original.png';cv2.imwrite(str(raw),frame)
            for coverage in ('circular','full-frame'):
                run([sys.executable,code/'undistort_fisheye.py','preview','--image',raw,'--out',out/f'fisheye_{coverage}.png',
                     '--coverage',coverage,'--fovs','150,180,200','--pitch','40'])
        return dict(output=str(out),limitation='Preview guesses only. Lens settings and zones still require visual checking.')
    if task['kind']=='review':
        for dep in task['deps']:
            status=directory/f'{dep}.json'
            if not status.is_file() or json.loads(status.read_text()).get('state')!='SUCCEEDED':
                raise RuntimeError(f'candidate run incomplete: {dep}; refusing partial review pack')
        source=next(t['env']['RUN'] for t in plan['tasks'] if t.get('group')=='sensitive')
        table=directory/'review_candidates.csv';pack=directory/'review_12min'
        run([sys.executable,code/'track_truth_v1.py','template','--root',root,'--run',source,
             '--min-secs','0','--out',table])
        from submit_research import VIDEO_DIR
        run([sys.executable,code/'review_pack.py','build','--table',table,'--source-dir',VIDEO_DIR,
             '--budget-min','12','--out',pack])
        return dict(table=str(table),pack=str(pack),limitation='12-minute candidate pack over one source hour; human review and deduplication still required.')
    raise RuntimeError(f'unknown task kind: {task["kind"]}')


def report(directory, final=False):
    plan=json.loads((directory/'manifest.json').read_text());root=Path(plan['root'])
    out=root/f'exp_results/RESEARCH_{plan["tag"]}.md';out.parent.mkdir(parents=True,exist_ok=True)
    lines=[f'# Research suite: {plan["tag"]}','', 'This report concerns the new suite only. Existing b4 remains the reference; no automatic model promotion.','',
           '| Task | Job | Status | Detail |','|---|---|---|---|']
    states={}
    for task in plan['tasks']:
        if task['kind']=='report':continue
        key=task['key'];p=directory/f'{key}.json'
        status=json.loads(p.read_text()) if p.exists() else {}
        state='SKIPPED' if task.get('skipped') else status.get('state','NO_FINAL_STATUS')
        if final and state=='RUNNING':state='NO_FINAL_STATUS'
        states[key]=state
        detail=task.get('skipped') or status.get('error') or str(status.get('result',{}))
        detail=detail.replace('|','/').replace('\n',' ')[:900]
        lines.append(f'| {key} | {plan["jobs"].get(key,"not submitted")} | {state} | {detail} |')
    complete=all(s in ('SUCCEEDED','FAILED','SKIPPED') for s in states.values())
    unfinished=('Scheduler dependencies have ended, but some tasks lack final status: check for timeout, cancellation or startup failure.'
                if final else 'Some tasks lack final status: they may be queued/running, killed, timed out, or never submitted. Check job IDs/logs.')
    lines+=['', 'All tasks have final status records.' if complete else unfinished]
    runs=['b4_combo_static5']
    for group in ('tta','sensitive','zerodce'):
        tasks=[t for t in plan['tasks'] if t.get('group')==group]
        if tasks and all(states.get(t['key'])=='SUCCEEDED' for t in tasks):runs.append(tasks[0]['env']['RUN'])
    if len(runs)>1:
        evaluation=directory/'person_evaluation.md'
        cmd=[sys.executable,str(root/'code/eval_truth.py'),'--root',str(root),'--runs',','.join(runs),
             '--baseline','b4_combo_static5','--out',str(evaluation)]
        r=subprocess.run(cmd,capture_output=True,text=True)
        if r.returncode:lines+=['','Evaluation failed: '+r.stderr[-1200:]]
        else:
            text=evaluation.read_text();summary=text.split('## Summary',1)[1].split('## Detail',1)[0]
            lines+=['','## Existing-truth comparison', '## Summary'+summary,
                    f'Full details: {evaluation}']
    else:lines+=['','No complete new scored group is available. Failed/partial runs are not presented as accuracy results.']
    lines+=['','## What to inspect',
            f'- Annotated TTA videos: {root}/annotated/{plan["tag"]}_tta/',
            f'- Grounding side-by-side frames: {directory}/grounding/',
            f'- Twelve-minute raw-video review pack: {directory}/review_12min/review.html',
            f'- Camera metadata / cuts: {directory}/busy/inventory.csv and windows.txt',
            f'- Zone / fisheye previews: {directory}/previews/',
            '- Grounding proposals are not counts or confirmed misses. Its frame selection is encounter-targeted, not unbiased recall.',
            '- Higher-resolution runs have no truth yet: qualitative outputs only; no accuracy claim.',
            '- New thresholds are experimental; do not accept them solely because they fit the existing four clips.',
            '- No own-night fine-tuning, 40-track campaign, full-day scaling, temporal detector retraining or BNE model substitution is included.']
    if plan.get('submission_error'):lines+=['','Submission stopped part-way: '+str(plan['submission_error'])]
    tmp=out.with_name(out.name+f'.{os.getpid()}.tmp')
    tmp.write_text('\n'.join(lines)+'\n');tmp.replace(out);print(out,flush=True)
    return dict(report=str(out))


def main():
    directory=Path(sys.argv[1]).resolve();key=sys.argv[2]
    if key=='report':report(directory);return
    plan=json.loads((directory/'manifest.json').read_text())
    task=next(t for t in plan['tasks'] if t['key']==key)
    status=dict(state='RUNNING',started=dt.datetime.now().isoformat())
    target=directory/f'{key}.json';atomic_json(target,status)
    try:
        status['result']=report(directory,final=True) if task['kind']=='report' else execute(plan,task,directory)
        status['state']='SUCCEEDED'
    except BaseException as exc:
        status.update(state='FAILED',error=str(exc));traceback.print_exc();raise
    finally:
        status['finished']=dt.datetime.now().isoformat();atomic_json(target,status)


if __name__=='__main__':main()
