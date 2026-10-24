#!/usr/bin/env python3
"""Retry only failed preview stage, preserving original reports and speed job."""
import argparse
import datetime as dt
import json
import shlex
import subprocess
from pathlib import Path
from preview_ffmpeg import resolve


def retry_command(root,bundle,out,ffmpeg):
    activate='/orange/xiangyan/rithika/vision/yolo_env/bin/activate'
    program=['python','code/speed_site_screen.py','--selected-sources',str(bundle/'camera_previews/selected_sources.csv'),'--out',str(out)]
    wrap='cd '+shlex.quote(str(root))+' && source '+shlex.quote(activate)+' && FFMPEG_BINARY='+shlex.quote(ffmpeg)+' '+shlex.join(program)
    return ['sbatch','--parsable','--partition=hpg-turin','--account=xiangyan','--qos=xiangyan','--cpus-per-task=4','--mem=6G','--time=01:00:00','--job-name=speed_preview_retry','--output='+str(bundle/'preview_retry_%j.log'),'--wrap',wrap]

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('bundle',type=Path);p.add_argument('--go',action='store_true');a=p.parse_args()
    root=Path(__file__).resolve().parents[1];bundle=a.bundle.resolve()
    selected=bundle/'camera_previews/selected_sources.csv'
    if not selected.is_file():p.error('Original source selection missing: '+str(selected))
    out=bundle/('camera_previews_retry_'+dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    print('Recovery folder:',out)
    print('CPU preview job only. Reuses extracted source videos and original source selection; no ZIP extraction or GPU submission.')
    if a.go:
        ffmpeg=resolve(install=True)
        job=subprocess.check_output(retry_command(root,bundle,out,ffmpeg),text=True).strip().split(';')[0]
        if not job.isdigit():raise RuntimeError('Unexpected job ID: '+job)
        manifest=bundle/('preview_retry_'+job+'.json')
        manifest.write_text(json.dumps(dict(job_id=job,output=str(out),original_selection=str(selected),ffmpeg=ffmpeg,stage='camera_previews_only'),indent=2)+'\n')
        print('Submitted CPU preview retry:',job)
    else:print('Dry run; add --go on HiPerGator.')
