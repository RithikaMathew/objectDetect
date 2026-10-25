#!/usr/bin/env python3
"""CPU-only, workbook-positive interval review; manual trajectories bypass count filters."""
import argparse
import csv
import datetime as dt
import html
import json
from pathlib import Path
import re
import subprocess
from study_count_reference import extract
from study_tables import read_xml_xls
from preview_ffmpeg import resolve


def normalized(s):
    return re.sub('[^a-z0-9]','',s.lower())


def positive_bins(workbook):
    rows,_=extract(read_xml_xls(workbook));bins={}
    for r in rows:
        if r['user_type']!='cyclist':continue
        b=bins.setdefault(r['bin_start'],dict(start=r['bin_start'],end=r['bin_end'],count=0,missing=False,channels=[]))
        b['channels'].append(r)
        if r['status']=='missing':b['missing']=True
        else:b['count']+=r['count']
    return [b for b in bins.values() if b['count']>0 or b['missing']]


def prepare(batch,workbooks,out,go=False):
    if not workbooks.is_dir():raise FileNotFoundError('Count workbook directory missing: '+str(workbooks))
    p=json.loads((batch/'manifest.json').read_text());out.mkdir(parents=True,exist_ok=False)
    entries=[];unavailable=[]
    exe=resolve() if go else None
    for task in p['tasks']:
        source=task['source'];camera=source['site']
        matches=[w for w in workbooks.glob('*.xls') if normalized(w.stem).startswith(normalized(camera))]
        if len(matches)!=1:
            unavailable.append(dict(camera=camera,reason='Workbook mapping missing or ambiguous',matches=[str(w) for w in matches]));continue
        workbook=matches[0];t0=dt.datetime.fromisoformat(source['clock'])
        for b in positive_bins(workbook):
            start=(dt.datetime.fromisoformat(b['start'])-t0).total_seconds()
            if not 0<=start<3600:
                unavailable.append(dict(camera=camera,bin_start=b['start'],study_count=b['count'],reason='Outside selected source hour; another source recording required'));continue
            key=task['key']+'_'+b['start'].replace(':','').replace(' ','_')
            entry=dict(key=key,camera=camera,source=source,workbook=str(workbook),reference=b,source_start_seconds=start,calibration=None,video=key+'.mp4')
            cal=batch/task['key']/'calibration/calibration.json'
            if cal.exists():entry['calibration']=json.loads(cal.read_text())
            entries.append(entry)
            if go:
                with (out/(key+'.log')).open('w') as log:
                    subprocess.run([exe,'-nostdin','-hide_banner','-loglevel','error','-ss',str(start),'-i',source['video'],'-t','900','-an','-c:v','libx264','-preset','fast','-crf','20','-movflags','+faststart',str(out/entry['video'])],stdout=log,stderr=subprocess.STDOUT,check=True)
    (out/'manifest.json').write_text(json.dumps(dict(entries=entries,unavailable=unavailable,clips_extracted=go),indent=2))
    (out/'index.html').write_text(PAGE.replace('__DATA__',json.dumps(entries).replace('<','\\u003c')))
    (out/'RESULTS.md').write_text('# Manual bicycle speed review\n\n'+str(len(entries))+' workbook-positive or missing-count bins in the selected source hours. No detector inference. Clips are extracted only with --go; no automatic submission.\n\nOpen index.html after downloading this entire folder. Select a cyclist ID, pause and click the same ground-contact point at three or more distinct times; use a separate ID for every person. Verify bicycle identity yourself. Download observations before closing. Manual points bypass detector/count filters.\n\nSpeeds use saved learned camera calibration, not the workbook average or its measurement distance. They remain exploratory, especially off the road calibration plane. Missing calibration means pixel motion only, no mph. At least 1.5 seconds and three points are required here as a practical review safeguard, not a validated threshold. Canvas uses original source image coordinates. Browser stepping/seek timing is approximate, not frame-exact.\n\nThe study total sums raw worksheet channels; check which channels are visible before comparing. A positive bin supplies no per-person timestamp or speed link. Zero-count bins are omitted; missing cells are never treated as zero. manifest.json lists positive/missing bins outside the selected source hour and mapping failures. This first pack does not cover every recording hour.\n')
    print('Output:',out,'review bins:',len(entries),'unavailable bins/mappings:',len(unavailable),'extracted:',go)


PAGE='''<!doctype html><meta charset="utf-8"><title>Manual bicycle trajectories</title>
<style>body{font:17px system-ui;margin:24px;max-width:1100px}canvas{max-width:100%;cursor:crosshair}video{width:100%;max-height:500px}button,input,select{font-size:17px;margin:5px}pre{white-space:pre-wrap}</style>
<h1>Manual bicycle speed review</h1><p>Only workbook-positive intervals (or missing counts). Confirm visible channels. Saved calibration gives exploratory mph, not validated speed.</p>
<select id="choose"></select><p id="info"></p><video id="v" controls preload="metadata"></video><br>
<button id="back">Back 0.1 s</button><button id="forward">Forward 0.1 s</button>
<label>Cyclist ID <input id="person" value="1" size="5"></label><button id="undo">Undo last point</button><button id="download">Download observations + speeds</button>
<p>Pause, then click on the canvas below at the same ground-contact point (for example rear tire touching pavement) at ≥3 times spanning ≥1.5 seconds. Do not connect different people. Clicks save in browser memory only: download before closing.</p><canvas id="c"></canvas><pre id="result"></pre>
<script>
const entries=__DATA__, records=[], choose=document.querySelector('#choose'),v=document.querySelector('#v'),c=document.querySelector('#c'),ctx=c.getContext('2d');
let active=0;
entries.forEach((e,i)=>choose.add(new Option(e.camera+' '+e.reference.start+' study total '+e.reference.count,i)));
function load(){active=Number(choose.value);const e=entries[active];if(!e)return;v.src=e.video;document.querySelector('#info').textContent=e.workbook+' | '+e.reference.start+' | calibration '+(e.calibration?'available, unvalidated':'missing: no mph');}
choose.onchange=load;load();
function draw(){if(v.readyState>=2){c.width=v.videoWidth;c.height=v.videoHeight;ctx.drawImage(v,0,0);records.filter(r=>r.key===entries[active].key&&Math.abs(r.seconds-v.currentTime)<.15).forEach(r=>{ctx.beginPath();ctx.arc(r.x,r.y,6,0,7);ctx.strokeStyle='red';ctx.lineWidth=3;ctx.stroke();});}requestAnimationFrame(draw);}draw();
document.querySelector('#back').onclick=()=>{v.pause();v.currentTime=Math.max(0,v.currentTime-.1)};
document.querySelector('#forward').onclick=()=>{v.pause();v.currentTime=Math.min(v.duration,v.currentTime+.1)};
c.onclick=ev=>{if(!v.paused||v.readyState<2)return;const b=c.getBoundingClientRect(),e=entries[active];records.push({key:e.key,cyclist_id:document.querySelector('#person').value,seconds:v.currentTime,source_seconds:e.source_start_seconds+v.currentTime,x:(ev.clientX-b.left)*c.width/b.width,y:(ev.clientY-b.top)*c.height/b.height,width:c.width,height:c.height});show();};
function project(H,p){let z=H[2][0]*p.x+H[2][1]*p.y+H[2][2];if(Math.abs(z)<1e-8)return null;return [(H[0][0]*p.x+H[0][1]*p.y+H[0][2])/z,(H[1][0]*p.x+H[1][1]*p.y+H[1][2])/z];}
function speeds(){const groups={};for(const r of records)(groups[r.key+'|'+r.cyclist_id]??=[]).push(r);return Object.values(groups).map(points=>{points.sort((a,b)=>a.seconds-b.seconds);const e=entries.find(e=>e.key===points[0].key),span=points.at(-1).seconds-points[0].seconds;let status='NEED_3_POINTS_AND_1.5_SECONDS',mph=null;if(points.length>=3&&span>=1.5){status='NO_CALIBRATION';if(e.calibration&&e.calibration.geometry_check_passed){const xy=points.map(p=>project(e.calibration.H,p));if(xy.every(p=>p&&p.every(Number.isFinite))){let distance=0;for(let i=1;i<xy.length;i++)distance+=Math.hypot(xy[i][0]-xy[i-1][0],xy[i][1]-xy[i-1][1]);mph=distance/span*2.2369362921;status='EXPLORATORY_UNVALIDATED_ROAD_PLANE';}}}return {camera:e.camera,cyclist_id:points[0].cyclist_id,bin_start:e.reference.start,study_bin_count:e.reference.count,start_seconds:points[0].seconds,end_seconds:points.at(-1).seconds,clock_basis:e.reference.start+' plus listed seconds; source clock unverified',points:points.length,mph,status};});}
function show(){document.querySelector('#result').textContent=JSON.stringify(speeds(),null,2)}
document.querySelector('#undo').onclick=()=>{records.pop();show()};
document.querySelector('#download').onclick=()=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify({observations:records,speeds:speeds(),policy:'manual ground points; browser times approximate; learned scale unvalidated'},null,2)],{type:'application/json'}));a.download='manual_bicycle_observations.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)};
</script>'''

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',type=Path,required=True);p.add_argument('--workbooks',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--go',action='store_true');a=p.parse_args();prepare(a.batch,a.workbooks,a.out,a.go)
