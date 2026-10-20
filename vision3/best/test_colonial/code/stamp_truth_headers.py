#!/usr/bin/env python3
"""Add a separate yellow GT line to existing videos without rerunning detection.

Original files/counts stay untouched. Default prints a plan; --go encodes copies.
"""
import argparse
import datetime as dt
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from annotation_truth import colonial_truth_bins, truth_text


def caption(video, truth_dir):
    # Only the known Colonial source receives its existing hand-labelled counts.
    m=re.search(r'__(?:day|night)_(\d{4})-(\d{4})__.*__(\d{8})(?:_v\d+)?\.mp4$', video.name)
    if not m: return truth_text(None)
    start,end,date=m.groups()
    begin=dt.datetime.strptime(date+start,'%Y%m%d%H%M')
    finish=dt.datetime.strptime(date+end,'%Y%m%d%H%M')
    if finish<begin:finish+=dt.timedelta(days=1)
    if (finish-begin).total_seconds()!=900: return truth_text(None)
    bins=colonial_truth_bins(video.parent.name+'.mp4','2019-07-10 00:00:00',15,truth_dir)
    b=int((begin-dt.datetime(2019,7,10)).total_seconds()//900)
    return truth_text(bins.get(b))


def encode(source, target, text):
    if target.exists(): raise FileExistsError(target)
    target.parent.mkdir(parents=True,exist_ok=True)
    import cv2
    import numpy as np
    cap=cv2.VideoCapture(str(source));width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));cap.release()
    if width<=0: raise RuntimeError(f'Cannot open {source}')
    strip=np.full((44,width,3),(0,255,255),dtype=np.uint8)
    font=cv2.FONT_HERSHEY_SIMPLEX
    scale=min(.65,(width-20)/max(1,cv2.getTextSize(text,font,1.,1)[0][0]))
    cv2.putText(strip,text,(10,29),font,scale,(0,0,0),1,cv2.LINE_AA)
    with tempfile.TemporaryDirectory(prefix='truth_header_') as td:
        path=Path(td)/'strip.png'
        if not cv2.imwrite(str(path),strip):raise RuntimeError('Cannot write truth strip')
        # PNG overlay works even when ffmpeg was built without drawtext/libfreetype.
        vf='[0:v]pad=iw:ih+44:0:44:color=yellow[base];[base][1:v]overlay=0:0:shortest=1[v]'
        try:
            subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-n','-i',str(source),
                            '-loop','1','-i',str(path),'-filter_complex',vf,'-map','[v]','-map','0:a?',
                            '-c:v','libx264','-crf','18','-preset','fast','-c:a','copy',str(target)],check=True)
        except BaseException:
            target.unlink(missing_ok=True)
            raise



def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument('--runs',nargs='+',required=True)
    ap.add_argument('--go',action='store_true')
    a=ap.parse_args();root=a.root.resolve();rows=[]
    if a.go and not shutil.which('ffmpeg'): raise RuntimeError('Load the ffmpeg module first')
    for run in a.runs:
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*',run):ap.error('invalid run name')
        files=sorted((root/'annotated'/run).glob('*/*.mp4'))
        files=[p for p in files if '.tmp_mp4v' not in p.name]
        if not files:raise FileNotFoundError(f'No annotated videos for {run}')
        for source in files:
            text=caption(source,root/'truth')
            target=root/'annotated_gt'/run/source.parent.name/source.name
            print(f'{text}\n{target}')
            if a.go:
                if target.exists():print('Already exists; skipped')
                else:encode(source,target,text)
            rows.append((target,text))
    if a.go:
        (root/'annotated_gt/INDEX.md').write_text('# Videos with explicit truth headers\n\n'+
            '\n'.join(f'- `{p}` — {text}'for p,text in rows)+'\n')


if __name__=='__main__':main()
