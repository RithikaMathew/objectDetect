#!/usr/bin/env python3
"""Submit the active research suite once; default is a read-only dry run."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
from run_batch5 import CLIPS, parse_envv

VIDEO_DIR = Path('/orange/xiangyan/rithika/vision/pilot_clips/MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/Standard_SCU8OG_2019-07-10_0000')
EVAL_CLIP = dict(night2115='night',day1400='day',night2200='night_holdout_2200',day1245='day_holdout_1245')


def save_plan(path, plan):
    tmp=path.with_suffix('.tmp')
    tmp.write_text(json.dumps(plan,indent=2))
    tmp.replace(path)


def build_plan(root, tag):
    base = dict(parse_envv(root/'code/run_batch4.sh', '5'))
    tasks=[]
    def add(key,kind,gpu=False,deps=None,**kw):
        tasks.append(dict(key=key,kind=kind,gpu=gpu,deps=deps or [],**kw))
    add('grounding_setup','setup',True)
    add('higher_resolution_scan','scan',True)
    for mode in ('tta','sensitive'):
        for clip,(chunk,start,stop) in CLIPS.items():
            env={**base,'RUN':f'{tag}_{mode}','CHUNK':str(chunk),'START_FRAME':str(start),
                 'MAX_FRAMES':str(stop),'STREAM_CLIPS':'0','WEIGHTS':str(root.parent.parent/'runs/detect/finetune_runs/rtdetr_v3/weights/best.pt'),
                 'ZONES_JSON':str(root/'zones/colonial_north_v1.json')}
            if mode=='tta':env['TTA']='1'
            else:env.update(DET_CONF='0.15',TRACK_THR='0.15',BIC_MIN_SEC='0.4',PED_MIN_SEC='0.4',STATIC_FILTER='0')
            add(f'{mode}_{clip}','pipeline',True,env=env,eval_clip=EVAL_CLIP[clip],group=mode)
    for clip,(chunk,_,_) in CLIPS.items():
        add(f'grounding_{clip}','grounding',True,['grounding_setup'],clip=EVAL_CLIP[clip],video=str(VIDEO_DIR/f'Standard_SCU8OG_2019-07-10_0000.{chunk:03d}.mp4'))
    # Known higher-resolution clip with a clock previously verified in saved logs.
    higher=root/'newvideo/corrine_706_15min.mp4'
    for mode in ('base','combo','tta'):
        env={**({} if mode=='base' else base),'RUN':f'{tag}_hires_{mode}','CHUNK':'1',
             'START_FRAME':'1','MAX_FRAMES':'0','VIDEO_OVERRIDE':str(higher),'SESSION_START':'2025-03-12_08:05:00',
             'ZONES_JSON':'/nonexistent_zones.json','GT_XLS':'none','STREAM_CLIPS':'0',
             'WEIGHTS':str(root.parent.parent/'runs/detect/finetune_runs/rtdetr_v3/weights/best.pt')}
        if mode=='tta':env['TTA']='1'
        add(f'hires_{mode}','pipeline',True,env=env,higher_resolution=True,optional_file=str(higher))
    # Complete the prior failed Zero-DCE test only if its checkpoint is present.
    dce=Path(os.environ.get('ZERODCE_WEIGHTS',str(root/'code/zerodce/Epoch99.pth')))
    for clip in ('night2115','night2200'):
        chunk,start,stop=CLIPS[clip]
        env={**base,'RUN':f'{tag}_zerodce','CHUNK':str(chunk),'START_FRAME':str(start),'MAX_FRAMES':str(stop),
             'ENHANCE':'zerodce','ENHANCE_CROPS':'1','ZERODCE_WEIGHTS':str(dce),'STREAM_CLIPS':'0',
             'WEIGHTS':str(root.parent.parent/'runs/detect/finetune_runs/rtdetr_v3/weights/best.pt')}
        add(f'zerodce_{clip}','pipeline',True,env=env,optional_file=str(dce),group='zerodce',eval_clip=EVAL_CLIP[clip])
    add('zone_fisheye_previews','previews')
    add('sensitive_review_pack','review',deps=[t['key'] for t in tasks if t.get('group')=='sensitive'])
    add('final_report','report',deps=[t['key'] for t in tasks])
    return dict(tag=tag,root=str(root),created=dt.datetime.now().isoformat(),tasks=tasks,jobs={})


def preflight(plan):
    root=Path(plan['root'])
    if not shutil.which('sbatch'):raise RuntimeError('sbatch not found; submit on HiPerGator, not your Mac')
    if not (Path(sys.executable).parent/'activate').exists():raise RuntimeError('activate yolo_env before submission')
    weights=Path(next(t['env']['WEIGHTS'] for t in plan['tasks'] if t['kind']=='pipeline'))
    required=[weights,root/'code/research_job.slurm',root/'videos_to_scan.txt']
    for _,(chunk,_,_) in CLIPS.items():
        required.append(VIDEO_DIR/f'Standard_SCU8OG_2019-07-10_0000.{chunk:03d}.mp4')
        for suffix in ('tracks.csv','bin_counts.csv','trajectories.csv'):
            required.append(root/f'counts/b4_combo_static5/Standard_SCU8OG_2019-07-10_0000.{chunk:03d}_{suffix}')
    from eval_truth import CLIPS as ECLIPS, read_truth
    for cc in ECLIPS.values():
        rows,skipped=read_truth(root/cc['truth'])
        if not rows or skipped:raise RuntimeError(f'incomplete truth: {cc["truth"]}')
    missing=[str(p) for p in required if not p.is_file()]
    if missing:raise RuntimeError('missing required inputs:\n'+'\n'.join(missing))
    for t in plan['tasks']:
        if t['kind']=='pipeline' and (root/'counts'/t['env']['RUN']).exists():
            raise RuntimeError(f'run output already exists for {t["env"]["RUN"]}; choose a new --tag')


def submit(plan, directory, concurrency=4, runner=subprocess.run):
    manifest=directory/'manifest.json'
    directory.mkdir(parents=True,exist_ok=False)
    plan['gpu_concurrency']=concurrency
    save_plan(manifest,plan)
    lanes=[None]*concurrency;lane=0
    for t in plan['tasks']:
        if t.get('optional_file') and not Path(t['optional_file']).is_file():
            t['skipped']=f'optional input missing: {t["optional_file"]}'
            save_plan(manifest,plan);continue
        deps=[plan['jobs'][k] for k in t['deps'] if k in plan['jobs']]
        if t['gpu'] and lanes[lane]:deps.append(lanes[lane])
        cmd=['sbatch','--parsable',f'--job-name={plan["tag"]}_{t["key"]}',
             f'--output={directory}/{t["key"]}_%j.log',
             '--time='+t.get('walltime','06:00:00' if t['gpu'] else '01:00:00')]
        if t['gpu']:cmd.append('--gpus=1')
        # afterany ensures failed setup doesn't strand dependents forever.
        if deps:cmd.append('--dependency=afterany:'+':'.join(dict.fromkeys(deps)))
        cmd += [str(Path(plan['root'])/'code/research_job.slurm'),str(directory),t['key']]
        r=runner(cmd,capture_output=True,text=True)
        if r.returncode:
            plan['submission_error']=dict(task=t['key'],stderr=r.stderr,stdout=r.stdout)
            save_plan(manifest,plan)
            raise RuntimeError(f'sbatch failed for {t["key"]}; earlier jobs may be running. Manifest: {manifest}')
        job=r.stdout.strip().split(';')[0]
        if not job.isdigit():
            plan['submission_error']=dict(task=t['key'],stdout=r.stdout,stderr=r.stderr,
                                          reason='unparseable job ID; check queue before retrying')
            save_plan(manifest,plan)
            raise RuntimeError(f'cannot parse sbatch job ID: {r.stdout!r}')
        plan['jobs'][t['key']]=job
        if t['gpu']:lanes[lane]=job;lane=(lane+1)%concurrency
        save_plan(manifest,plan)
        print(f'{t["key"]}: {job}',flush=True)
    return plan


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--tag',default='research_oct19');ap.add_argument('--go',action='store_true')
    ap.add_argument('--concurrency',type=int,default=4)
    a=ap.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_]{1,40}',a.tag):ap.error('tag must be 1-40 letters/digits/underscores')
    if not 1<=a.concurrency<=8:ap.error('concurrency must be 1-8')
    root=Path(__file__).resolve().parent.parent
    directory=root/'logs'/a.tag
    if directory.exists():ap.error(f'{directory} exists; already submitted/planned. See its manifest; choose a new tag for a new batch.')
    plan=build_plan(root,a.tag)
    print(f'{len(plan["tasks"])} tasks including optional inputs; at most {a.concurrency} GPU jobs at once.')
    for t in plan['tasks']:print(t['key'], 'GPU' if t['gpu'] else 'CPU', ('optional: '+t['optional_file']) if t.get('optional_file') else '')
    if not a.go:
        print('DRY RUN: nothing submitted, installed or downloaded. Add --go on HiPerGator.');return
    preflight(plan)
    submit(plan,directory,a.concurrency)
    print(f'Report: {root}/exp_results/RESEARCH_{a.tag}.md')
    print(f'Check later: python code/research_worker.py {directory} report')


if __name__=='__main__':main()
