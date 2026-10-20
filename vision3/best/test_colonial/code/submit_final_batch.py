#!/usr/bin/env python3
"""One submission for pending new sites, final review and GT-header copies.

Default is a dry-run. Reuses completed detector audits; no new model sweep.
Human identity, lane and measured-speed confirmation remain manual steps.
"""
import argparse
from pathlib import Path
import re
import shutil
import sys
from eval_truth import CLIPS
from submit_newsites import TARGETS,DATA_ROOT,choose_source,build_plan
from submit_research import submit,VIDEO_DIR

HEADER_RUNS=['b4_combo_static5','research_oct19_tta','research_oct19_hires_base',
             'research_oct19_hires_combo','research_oct19_hires_tta']


def extend_plan(plan):
    tasks=[t for t in plan['tasks']if t['kind']!='report']
    tasks += [dict(key='final_review',kind='final_review',gpu=False,deps=[],walltime='00:30:00'),
              dict(key='truth_headers',kind='truth_headers',gpu=False,deps=[],walltime='04:00:00',runs=HEADER_RUNS)]
    tasks.append(dict(key='final_report',kind='report',gpu=False,deps=[t['key']for t in tasks]))
    plan['tasks']=tasks
    return plan


def preflight(root,tag):
    if not shutil.which('sbatch'):raise RuntimeError('Submit on HiPerGator')
    if not(Path(sys.executable).parent/'activate').is_file():raise RuntimeError('Activate yolo_env first')
    if(root/'logs'/tag).exists():raise FileExistsError(f'Batch already has a manifest: logs/{tag}; inspect it before retrying')
    if(root/'exp_results/final_review_20261020').exists():raise FileExistsError('Final review output exists; do not submit it again')
    required=[root.parent.parent/'runs/detect/finetune_runs/rtdetr_v3/weights/best.pt',root/'code/research_job.slurm',root/'code/final_review.slurm']
    for clip,cc in CLIPS.items():
        required.append(VIDEO_DIR/f'Standard_SCU8OG_2019-07-10_0000.{cc["chunk"]:03d}.mp4')
        for folder in (root/'logs/rfdetr_oct19'/clip,root/'logs/research_oct19/grounding'/clip):
            required += [folder/'proposals.csv',folder/'summary.json']
            if not any(folder.glob('*.jpg')):raise FileNotFoundError(f'Completed audit JPGs missing: {folder}')
    missing=[str(p)for p in required if not p.is_file()]
    if missing:raise FileNotFoundError('\n'.join(missing))
    for run in HEADER_RUNS:
        if not any((root/'annotated'/run).glob('*/*.mp4')):raise FileNotFoundError(f'No existing annotated videos for {run}')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--data-root',type=Path,default=DATA_ROOT)
    ap.add_argument('--tag',default='newsites_oct20');ap.add_argument('--go',action='store_true')
    a=ap.parse_args();root=a.root.resolve()
    if not re.fullmatch(r'[A-Za-z0-9_]{1,40}',a.tag):ap.error('invalid tag')
    print('5 jobs: Anderson2021 + CurryFordNorth2022 (reference system), existing-frame review, GT-header copies, final report.')
    print('Reference: normal3s day/night; strict NIGHT-only cyclist exception >=0.3s, detector cyclist >=90%, weighted X-CLIP cyclist >=0.90.')
    print('No broad0.4s setting, TTA or brightening. No rerun of completed research suite or full-frame RF-DETR audit.')
    if not a.go:print('DRY RUN: no files changed or jobs submitted. Add --go on HiPerGator.');return
    preflight(root,a.tag)
    selections=[(t,*choose_source(a.data_root/t['folder'],t['year']))for t in TARGETS]
    plan=extend_plan(build_plan(root,a.tag,selections))
    for task in plan['tasks']:
        if task.get('env')and(root/'counts'/task['env']['RUN']).exists():raise FileExistsError(task['env']['RUN'])
    submit(plan,root/'logs'/a.tag,concurrency=2)
    print(f'Final report: {root}/exp_results/NEWSITES_{a.tag}.md')
    print('Review materials: exp_results/final_review_20261020/; existing-video copies: annotated_gt/')
    print('Identity approvals, person-box labels, lane checks and measured speed-gate confirmation still require human review.')


if __name__=='__main__':main()
