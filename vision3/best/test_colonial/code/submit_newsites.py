#!/usr/bin/env python3
"""Submit the reference configuration on two additional sites/years; dry-run default.

Anderson St (2021) and Curry Ford North (2022) are new to this validation,
not guaranteed unseen training sites. One fixed 15-minute daytime window per
site, preferably noon, selected without using detections or apparent success.
"""
import argparse
import datetime as dt
import json
from pathlib import Path
import re
import shutil
import sys
from run_batch5 import parse_envv
from submit_research import submit

DATA_ROOT=Path('/orange/xiangyan/rithika/vision/pilot_clips/MioVision Data')
TARGETS=[dict(key='anderson_2021',site='Anderson St',year=2021,folder='2021 Data/Anderson St'),
         dict(key='curryford_2022',site='Curry Ford North',year=2022,folder='2022 Data/Curry Ford/North')]


def source_clock(path):
    m=re.fullmatch(r'Standard_[A-Za-z0-9]+_(\d{4}-\d{2}-\d{2})_(\d{4})\.(\d{3})\.mp4',Path(path).name)
    if not m: raise ValueError(f'Cannot infer source clock: {path}')
    date,clock,chunk=m.groups()
    if int(chunk)<1: raise ValueError('Chunk indices must begin at one')
    return dt.datetime.strptime(date+clock,'%Y-%m-%d%H%M')+dt.timedelta(hours=int(chunk)-1)


def probe(path):
    import cv2
    cap=cv2.VideoCapture(str(path))
    try:
        if not cap.isOpened(): raise RuntimeError(f'Cannot open {path}')
        fps=cap.get(cv2.CAP_PROP_FPS);frames=cap.get(cv2.CAP_PROP_FRAME_COUNT)
        width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        ok,_=cap.read()
        if not ok or fps<=0 or frames/fps<900 or min(width,height)<=0:
            raise RuntimeError(f'Need readable >=15-minute source: {path}')
        return dict(fps=fps,frames=int(frames),width=width,height=height)
    finally:cap.release()


def choose_source(folder, year, inspect=probe):
    candidates=[]
    for path in folder.rglob('*.mp4'):
        try:clock=source_clock(path)
        except ValueError:continue
        if clock.year==year and 7<=clock.hour<=16:
            candidates.append((abs(clock.hour-12),str(path),path,clock))
    errors=[]
    for _,_,path,clock in sorted(candidates):
        try:return path,clock,inspect(path)
        except RuntimeError as exc:errors.append(str(exc))
    raise FileNotFoundError(f'No readable 15-minute daytime source under {folder}. Extract the source footage first. '+ '; '.join(errors[:3]))


def build_plan(root,tag,selections):
    base=dict(parse_envv(root/'code/run_batch4.sh','5'))
    tasks=[]
    for target,video,clock,metadata in selections:
        env={**base,'BIC_MIN_SEC':'3','PED_MIN_SEC':'3','SHORT_MIN_SEC':'0.3',
             'SHORT_DET_PCT':'90','SHORT_WBIC':'0.9','RUN':f'{tag}_{target["key"]}','VIDEO_OVERRIDE':str(video),
             'CHUNK':'1','START_FRAME':'1','MAX_FRAMES':str(round(900*metadata['fps'])),
             'SESSION_START':clock.strftime('%Y-%m-%d_%H:%M:%S'),'STREAM_CLIPS':'0',
             'WEIGHTS':str(root.parent.parent/'runs/detect/finetune_runs/rtdetr_v3/weights/best.pt'),
             'ZONES_JSON':'/nonexistent_zones.json','GT_XLS':'none',
             'CLOCK_NOTE':'Inferred from filename and hourly chunk index; verify embedded camera clock.'}
        tasks.append(dict(key=target['key'],kind='pipeline',gpu=True,deps=[],env=env,scale_pixels=True,
                          site=target['site'],year=target['year'],metadata=metadata,
                          training_overlap='Site appears in documented training-data recipe; this is not a strict unseen-site test.'))
    tasks.append(dict(key='final_report',kind='report',gpu=False,deps=[t['key']for t in tasks]))
    return dict(tag=tag,root=str(root),purpose='two_new_sites',created=dt.datetime.now().isoformat(),tasks=tasks,jobs={})


def write_report(directory,plan,final=False):
    root=Path(plan['root']);out=root/'exp_results'/f'NEWSITES_{plan["tag"]}.md'
    out.parent.mkdir(parents=True,exist_ok=True)
    lines=['# Two additional sites: reference-system validation','','Configuration: fine-tuned RT-DETR + SAHI + ByteTrack/ID stitching + X-CLIP + detector/motion/duration/static rules. TTA and enhancement off.',
           'No complete human truth exists for these clips: predicted counts are NOT accuracy.',
           'These sites appear in the documented training-data recipe; do not call this an unseen-site test.',
           'Windows are selected by a fixed daytime/noon preference, not by model performance.',
           'Clocks are inferred from filenames, not verified against the embedded camera clock. Check before using time-based conclusions.','']
    comparison=root/'exp_results/classifier_comparison_20261020/summary.json'
    if comparison.is_file():
        existing=json.loads(comparison.read_text())
        lines += ['## Existing four labelled clips: detector versus X-CLIP',
                  f'Saved track classification: detector {existing["detector_correct"]}/{existing["included"]}; X-CLIP {existing["xclip_correct"]}/{existing["included"]}.',
                  'Provisional time-matched comparison, not detector recall or verified standalone counting accuracy.',
                  f'Full comparison: `{comparison.parent / "RESULTS.md"}`','']
    for task in plan['tasks']:
        if task['kind']=='report':continue
        path=directory/f'{task["key"]}.json'
        status=json.loads(path.read_text())if path.exists()else{}
        state=status.get('state','NO_FINAL_STATUS')
        if final and state=='RUNNING':state='NO_FINAL_STATUS'
        if task['kind']!='pipeline':
            lines += [f'## {task["key"]} — {state}',str(status.get('result',{})) if state=='SUCCEEDED' else status.get('error','Check job log; no complete output claimed.'),'']
            continue
        lines += [f'## {task["site"]} ({task["year"]}) — {state}',
                  f'Source: `{task["env"]["VIDEO_OVERRIDE"]}`',
                  f'Source metadata: {task["metadata"]}',f'Planned first-frame clock: {task["env"]["SESSION_START"]} (inferred)']
        result=status.get('result',{})
        if state=='SUCCEEDED' and result.get('run_log'):
            log=json.loads(Path(result['run_log']).read_text())
            lines += [f'Predicted counts only: {log["final_counts"]}',
                      f'Runtime: {log["runtime_s"]/60:.1f} minutes',
                      f'Actual processed duration: {log["duration_s_processed"]} seconds',
                      'Exact annotated video paths:']
            lines += [f'- `{p}`'for p in log['annotated_clips']]
            lines += [f'Tracks: `{log["tracks_csv"]}`',
                      'Review every cyclist/pedestrian; report missed people, duplicate IDs, object-to-person ID jumps, e-scooter labels and clip timestamps.']
        else:lines += ['No completed results are claimed. '+status.get('error','Check job/status logs.')]
        lines += ['']
    if plan.get('submission_error'):lines += ['Submission stopped part-way: '+str(plan['submission_error'])]
    temp=out.with_suffix('.tmp');temp.write_text('\n'.join(lines)+'\n');temp.replace(out)
    print(out,flush=True);return dict(report=str(out))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument('--data-root',type=Path,default=DATA_ROOT)
    ap.add_argument('--tag',default='newsites_oct20');ap.add_argument('--go',action='store_true')
    a=ap.parse_args();root=a.root.resolve()
    if not re.fullmatch(r'[A-Za-z0-9_]{1,40}',a.tag):ap.error('invalid tag')
    for t in TARGETS:print(f'{t["site"]} ({t["year"]}): {a.data_root/t["folder"]}')
    print('Reference system; first 15 minutes of a daytime hourly file, preferably noon. No TTA/enhancement. No new human truth. Training-site overlap disclosed.')
    if not a.go:print('DRY RUN: no files changed or jobs submitted. Add --go on HiPerGator.');return
    if not shutil.which('sbatch'):raise RuntimeError('Submit on HiPerGator')
    if not (Path(sys.executable).parent/'activate').is_file():raise RuntimeError('Activate yolo_env first')
    selections=[(t,*choose_source(a.data_root/t['folder'],t['year']))for t in TARGETS]
    plan=build_plan(root,a.tag,selections);directory=root/'logs'/a.tag
    weights=Path(plan['tasks'][0]['env']['WEIGHTS'])
    for p in (weights,root/'code/research_job.slurm'):
        if not p.is_file():raise FileNotFoundError(p)
    for task in plan['tasks']:
        if task.get('env')and(root/'counts'/task['env']['RUN']).exists():raise FileExistsError(task['env']['RUN'])
    submit(plan,directory,concurrency=2)
    print(f'Read {root}/exp_results/NEWSITES_{a.tag}.md after completion.')


if __name__=='__main__':main()
