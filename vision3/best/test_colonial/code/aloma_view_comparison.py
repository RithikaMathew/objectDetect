#!/usr/bin/env python3
"""Export two matching one-minute Aloma views; no detection or permanent source extraction."""
import argparse
import csv
import datetime as dt
import html
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile
from preview_ffmpeg import resolve


def select_sources(inventory):
    with inventory.open() as f:rows=list(csv.DictReader(f))
    result=[]
    for name in ('Aloma Path','Aloma Sidewalk'):
        matches=[r for r in rows if r['site']==name and r['clock']=='2019-10-30 12:00:00']
        if len(matches)!=1:raise ValueError('Need exactly one noon source for '+name)
        result.append(matches[0])
    if result[0]['archive_path']==result[1]['archive_path']:raise ValueError('Both views resolve to same source')
    return result


def export(archive,inventory,out,data_root):
    exe=resolve();sources=select_sources(inventory)
    out.mkdir(parents=True,exist_ok=False);records=[]
    with zipfile.ZipFile(archive) as z:
        for row in sources:
            slug=row['site'].lower().replace(' ','_');name=slug+'_2019-10-30_120330-120430.mp4'
            local=data_root/row['archive_path']
            with tempfile.TemporaryDirectory(prefix='aloma_preview_',dir=out) as td:
                if local.is_file():source=local
                else:
                    info=z.getinfo(row['archive_path'])
                    if shutil.disk_usage(out).free<info.file_size+512*1024**2:raise RuntimeError('Insufficient temporary disk space')
                    source=Path(td)/'source.mp4'
                    with z.open(info) as inp,source.open('wb') as dest:shutil.copyfileobj(inp,dest,8*1024**2)
                log=out/(slug+'_ffmpeg.log')
                with log.open('w') as f:
                    subprocess.run([exe,'-nostdin','-hide_banner','-loglevel','error','-ss','210','-i',str(source),'-t','60','-map','0:v:0','-an','-c:v','libx264','-preset','fast','-crf','22','-pix_fmt','yuv420p','-threads','2','-movflags','+faststart',str(out/name)],stdout=f,stderr=subprocess.STDOUT,check=True)
                subprocess.run([exe,'-nostdin','-hide_banner','-loglevel','error','-ss','0','-i',str(out/name),'-frames:v','1','-threads','1',str(out/(slug+'.jpg'))],check=True)
            records.append(dict(camera=row['site'],archive_path=row['archive_path'],source_hour=row['clock'],source_start_seconds=210,requested_duration_seconds=60,clip=name))
            (out/'sources.json').write_text(json.dumps(records,indent=2)+'\n')
            print('Saved '+str(out/name),flush=True)
    body=['<!doctype html><meta charset="utf-8"><title>Aloma view comparison</title><style>body{font:18px system-ui;margin:24px}main{display:flex;flex-wrap:wrap;gap:20px}section{flex:1;min-width:300px}video{width:100%}</style><h1>Aloma: Path versus Sidewalk</h1><p>Same filename-inferred interval: October30,2019,12:03:30–12:04:30. No detection overlays. Burned camera clocks and actual synchronization are not independently verified.</p><main>']
    for r in records:body.append(f'<section><h2>{html.escape(r["camera"])}</h2><video controls preload="metadata" src="{r["clip"]}"></video></section>')
    body.append('</main>');(out/'index.html').write_text('\n'.join(body))
    (out/'README.md').write_text('# Aloma view comparison\n\nTwo one-minute clips: Aloma Path (SCU8PM) and Aloma Sidewalk/Aloma SW (SCU8OG),October30,2019. Both use source seconds210–270fromthefilename-inferrednoonhour. Compare the scene, direction, visible path/sidewalk and burned timestamp. Different device IDs do not alone prove different visual coverage. Open index.html or the two MP4s. No inference or speed calculation. Original source files unchanged; temporary extracted hourly copies removed.\n')

if __name__=='__main__':
    repo=Path(__file__).resolve().parents[4];p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive',type=Path,default=Path('/orange/xiangyan/rithika/vision/MioVision_Data.zip'))
    p.add_argument('--inventory',type=Path,default=repo/'reports/cluster_returns/20261024/recording_lengths/per_source.csv')
    p.add_argument('--data-root',type=Path,default=Path('/orange/xiangyan/rithika/vision/pilot_clips'))
    p.add_argument('--out',type=Path,required=True);a=p.parse_args();export(a.archive,a.inventory,a.out,a.data_root)
