#!/usr/bin/env python3
"""One submission command: bounded camera previews then prepared speed experiments."""
import argparse
import datetime as dt
import json
import shlex
import subprocess
from pathlib import Path
from speed_site_screen import plan,CANDIDATES
from preview_ffmpeg import resolve


def commands(root,out,screen_id=None):
    activate='/orange/xiangyan/rithika/vision/yolo_env/bin/activate'
    base=f'cd {shlex.quote(str(root))} && source {shlex.quote(activate)} && '
    cpu=base+'python code/speed_site_screen.py --extract --out '+shlex.quote(str(out/'camera_previews'))
    gpu=base+'python code/speed_research.py --video '+shlex.quote('/orange/xiangyan/rithika/vision/pilot_clips/MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/Standard_SCU8OG_2019-07-10_0000/Standard_SCU8OG_2019-07-10_0000.013.mp4')+' --frames 3000 --sample-stride 3 --device cuda --out '+shlex.quote(str(out/'speed_results'))
    common=['sbatch','--parsable','--partition=hpg-turin','--account=xiangyan','--qos=xiangyan']
    first=common+['--job-name=speed_camera_screen','--cpus-per-task=4','--mem=6G','--time=01:00:00','--output='+str(out/'screen_%j.log'),'--wrap',cpu]
    second=common+['--job-name=bicycle_speed_methods','--cpus-per-task=4','--mem=16G','--gpus=1','--time=04:00:00','--output='+str(out/'speed_%j.log')]
    if screen_id:second+=['--dependency=afterany:'+screen_id]
    second+=['--wrap',gpu]
    return first,second

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--go',action='store_true');p.add_argument('--tag',default=dt.datetime.now().strftime('%Y%m%d_%H%M%S'))
    a=p.parse_args();root=a.root.resolve()
    if not a.tag or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in a.tag):p.error('Tag must contain letters, numbers, underscores or hyphens only')
    out=root/'exp_results'/('SPEED_PILOT_'+a.tag)
    selected=plan(root,Path('/orange/xiangyan/rithika/vision/pilot_clips'))
    summary=dict(candidate_cameras=len(selected),reference_locations_with_candidates=len({r['reference_location'] for r in selected}),reference_locations_total=len(CANDIDATES),max_preview_minutes=len(selected)*3*45/60,maximum_new_extraction_gb=5,scope='CPU previews across candidate cameras; GPU calibration on Colonial only plus saved University manual comparison',all_five_papers_implemented=False)
    print(json.dumps(summary,indent=2));print('Output:',out)
    if a.go:
        # Read-only dependency check before reserving any compute or extracting data.
        probe='source /orange/xiangyan/rithika/vision/yolo_env/bin/activate && python -c '+shlex.quote('import torch, torchvision, scipy, numpy, cv2; from torchvision.models.detection import maskrcnn_resnet50_fpn')
        subprocess.run(['bash','-lc',probe],check=True)
        subprocess.run(['git','--version'],check=True,stdout=subprocess.DEVNULL)
        resolve(install=True)  # Bootstrap/check preview executable before submitting either job.
        out.mkdir(parents=True,exist_ok=False);manifest=dict(summary=summary,jobs=[])
        try:
            first,_=commands(root,out)
            job=subprocess.check_output(first,text=True).strip().split(';')[0]
            if not job.isdigit():raise ValueError('Unexpected CPU job ID: '+job)
            manifest['jobs'].append(dict(stage='camera_screen',id=job));(out/'submission.json').write_text(json.dumps(manifest,indent=2)+'\n')
            _,second=commands(root,out,job)
            job2=subprocess.check_output(second,text=True).strip().split(';')[0]
            if not job2.isdigit():raise ValueError('Unexpected GPU job ID: '+job2)
            manifest['jobs'].append(dict(stage='speed_methods',id=job2))
        finally:(out/'submission.json').write_text(json.dumps(manifest,indent=2)+'\n')
        (out/'README.md').write_text('# Bicycle speed pilot bundle\n\nRead camera_previews/RESULTS.md and speed_results/RESULTS.md after both jobs finish. Download the entire camera_previews folder and open index.html to review fixed daytime excerpts. submission.json records job IDs; logs record failures. This is a screening stage across candidate cameras plus Colonial calibration experiments, not speed inference on all locations. Later choose first eligible1–5cyclists per usable camera, without selecting by agreement with study speeds. No automatic architecture changes or all-study inference.\n')
        print('Submitted:',json.dumps(manifest['jobs']))
    else:
        print('Dry run only; add --go on HiPerGator. No jobs submitted.')
