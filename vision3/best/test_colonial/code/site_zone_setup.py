#!/usr/bin/env python3
"""Build offline per-camera polygon editors from real study frames; no inference."""
import argparse
import base64
import csv
import hashlib
import html
import json
from pathlib import Path
import re


def zone_key(site):
    return re.sub(r'[^a-z0-9]+','_',site.lower()).strip('_')+'_'+hashlib.sha256(site.encode()).hexdigest()[:6]


def page(site,date,video,frame,image_uri,width,height,seed=None):
    data=dict(site=site,recording_date=date,source_video=str(video),source_frame=frame,ref_size=[width,height])
    text='''<!doctype html><meta charset="utf-8"><title>Camera zone editor</title>
<style>body{font:17px sans-serif;max-width:1100px;margin:20px auto}canvas{width:100%;touch-action:none;border:1px solid #777}button,input,select{font:inherit;margin:5px}textarea{width:100%}#message{white-space:pre-line}</style>
<h1>Mark camera areas</h1><p id="camera"></p><p>Click vertices around an area. Select a region to edit it. Use Add region for separate areas of the same type. Draw exclusive areas: do not include the bike lane inside the road polygon. Road = motor-vehicle travel area; bike lane, sidewalk and shared-use path are separate. Points in overlapping types remain uncertain.</p>
<select id="region"></select><select id="type"><option value="road">Road</option><option value="bike_lane">Bike lane</option><option value="sidewalk">Sidewalk</option><option value="path">Shared-use path</option><option value="grass">Grass / other</option></select><button id="add">Add region of selected type</button><button id="undo">Undo point</button><button id="reset">Clear selected region</button>
<canvas id="canvas"></canvas><p id="status"></p>
<label>Your name <input id="reviewer"></label><label><input id="confirmed" type="checkbox">I checked these area outlines against this camera image.</label><button id="export">Download zones JSON</button><label>Import previous zones JSON <input id="import" type="file" accept=".json"></label><p id="message" role="status"></p><textarea id="json" rows="10" readonly placeholder="Backup JSON appears here after export"></textarea>
<p>Areas do not provide measured distances, mph, or confirmed conflict locations. Keep the JSON filename unchanged and collect exports in one zones directory before running the lane report.</p>
<script>
const meta=METADATA,seed=SEED,imageURI=IMAGE,filename=FILENAME;
const $=id=>document.getElementById(id),canvas=$('canvas'),ctx=canvas.getContext('2d'),pic=new Image();canvas.width=meta.ref_size[0];canvas.height=meta.ref_size[1];
const keys={road:'road',bike_lane:'bike',sidewalk:'sidewalk',path:'path',grass:'grass'},colors={road:'#39e75f',bike_lane:'#ffdc35',sidewalk:'#ff4fe8',path:'#34e5ed',grass:'#efaa56'};
let regions=Object.keys(keys).map((facility,i)=>({id:String(i),facility,polygon:[]})),active=0;
function imported(d){if(d.site&&d.site!==meta.site)throw Error('Wrong camera/site');if(d.source_video&&d.source_video!==meta.source_video)throw Error('Source camera view differs: inspect before reuse');const scale=meta.ref_size.map((v,i)=>v/d.ref_size[i]);let rr=Object.entries(keys).map(([facility,key],i)=>({id:String(i),facility,polygon:(d[key]||[]).map(p=>p.map((v,i)=>v*scale[i]))}));for(const r of d.extra_regions||[])rr.push({id:String(rr.length),facility:r.facility,polygon:r.polygon.map(p=>p.map((v,i)=>v*scale[i]))});for(const r of rr)if(!keys[r.facility]||r.polygon.some(p=>p.length!==2||p.some((v,i)=>!Number.isFinite(v)||v<0||v>=meta.ref_size[i])))throw Error('Invalid region coordinates');return rr;}
const storage='camera_zones_v1:'+meta.site+':'+meta.source_video;
try{const saved=JSON.parse(localStorage.getItem(storage)||'null');if(saved){regions=imported(saved);$('reviewer').value=saved.reviewer||''}else if(seed)regions=imported(seed)}catch(e){$('message').textContent=e.message}
function data(){const d={...meta,reviewer:$('reviewer').value.trim(),source:'Owner-marked areas on source frame',extra_regions:[]};for(const r of regions){const key=keys[r.facility];if(!d[key])d[key]=r.polygon;else if(r.polygon.length)d.extra_regions.push(r)}return d}
function save(){try{localStorage.setItem(storage,JSON.stringify(data()))}catch(e){}}
function changed(){ $('confirmed').checked=false;save();draw() }
function options(){const sel=$('region');sel.replaceChildren();for(const [i,r]of regions.entries()){const o=document.createElement('option');o.value=i;o.textContent=`${i+1}: ${r.facility}`;sel.appendChild(o)}sel.value=active;}
function draw(){if(pic.complete&&pic.naturalWidth){ctx.clearRect(0,0,canvas.width,canvas.height);ctx.drawImage(pic,0,0)}for(const [i,r]of regions.entries()){if(!r.polygon.length)continue;ctx.strokeStyle=colors[r.facility];ctx.fillStyle=colors[r.facility];ctx.lineWidth=i===active?4:2;ctx.beginPath();r.polygon.forEach((p,j)=>j?ctx.lineTo(...p):ctx.moveTo(...p));if(r.polygon.length>=3){ctx.closePath();ctx.globalAlpha=.15;ctx.fill();ctx.globalAlpha=1}ctx.stroke();for(const p of r.polygon){ctx.beginPath();ctx.arc(...p,4,0,Math.PI*2);ctx.fill()}}$('status').textContent=`Selected ${regions[active].facility}: ${regions[active].polygon.length} vertices; at least3 needed. Edits clear confirmation.`;}
$('camera').textContent=meta.site+' / '+meta.recording_date+' / '+meta.source_video;
$('region').onchange=()=>{active=Number($('region').value);draw()};$('add').onclick=()=>{regions.push({id:String(regions.length),facility:$('type').value,polygon:[]});active=regions.length-1;options();changed()};
canvas.onclick=e=>{const r=canvas.getBoundingClientRect();regions[active].polygon.push([Math.min(canvas.width-1,Math.max(0,(e.clientX-r.left)*canvas.width/r.width)),Math.min(canvas.height-1,Math.max(0,(e.clientY-r.top)*canvas.height/r.height))]);changed()};$('undo').onclick=()=>{regions[active].polygon.pop();changed()};$('reset').onclick=()=>{regions[active].polygon=[];changed()};$('reviewer').onchange=save;
$('import').onchange=async()=>{try{const d=JSON.parse(await $('import').files[0].text());regions=imported(d);$('reviewer').value=d.reviewer||'';active=0;options();changed();$('message').textContent='Imported. Inspect outlines and confirm again.'}catch(e){$('message').textContent='Import failed: '+e.message}};
$('export').onclick=()=>{const errors=[];if(!regions.some(r=>r.polygon.length>=3))errors.push('Draw at least one region.');if(regions.some(r=>r.polygon.length>0&&r.polygon.length<3))errors.push('Finish or clear partial regions.');if(!$('reviewer').value.trim())errors.push('Enter your name.');if(!$('confirmed').checked)errors.push('Check the outline confirmation.');if(errors.length){$('message').textContent=errors.join(String.fromCharCode(10));return;}const d=data();d.area_alignment_confirmed=true;const text=JSON.stringify(d,null,2);$('json').value=text;save();const a=document.createElement('a'),url=URL.createObjectURL(new Blob([text],{type:'application/json'}));a.href=url;a.download=filename;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),10000);$('message').textContent='Download requested: '+filename+'. If blocked, save the backup JSON below using this filename.';};
options();pic.onload=draw;pic.src=imageURI;
</script>'''
    return text.replace('METADATA',json.dumps(data)).replace('SEED',json.dumps(seed)).replace('IMAGE',json.dumps(image_uri)).replace('FILENAME',json.dumps(zone_key(site)+'.json'))


def build(inventory,out,sites=None):
    import cv2
    from submit_newsites import source_clock
    with inventory.open()as f:rows=list(csv.DictReader(f))
    selected=sorted({r['site']for r in rows if not sites or r['site']in sites})
    if not selected:raise ValueError('No selected sites')
    out.mkdir(parents=True,exist_ok=False);links=[];status=[]
    for site in selected:
        choices=[]
        for r in [x for x in rows if x['site']==site]:
            if not Path(r['video']).is_file() or not r['clock']:continue
            hour=int(r['clock'][11:13]);choices.append((abs(hour-12),r['video'],r))
        errors=[];completed=False
        for _,video,r in sorted(choices):
            cap=cv2.VideoCapture(video)
            try:
                fps=cap.get(cv2.CAP_PROP_FPS);count=cap.get(cv2.CAP_PROP_FRAME_COUNT)
                if fps<=0:raise ValueError('Invalid FPS')
                frame=min(round(300*fps),max(0,int(count)-1));cap.set(cv2.CAP_PROP_POS_FRAMES,frame);ok,img=cap.read()
                if not ok:raise ValueError('Frame decode failed')
                h,w=img.shape[:2];ok,encoded=cv2.imencode('.jpg',img)
                if not ok:raise ValueError('JPEG failed')
                image='data:image/jpeg;base64,'+base64.b64encode(encoded).decode()
                filename=zone_key(site)+'.html';(out/filename).write_text(page(site,r['study_date'],video,frame+1,image,w,h))
                links.append('<li><a href="'+filename+'">'+html.escape(site)+'</a></li>')
                status.append(dict(site=site,status='READY',video=video,page=filename,error=''));completed=True;break
            except Exception as exc:errors.append(str(exc))
            finally:cap.release()
        if not completed:status.append(dict(site=site,status='MISSING_OR_UNREADABLE',video='',page='',error='; '.join(errors)or'No local readable source'))
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><h1>Study camera zone editors</h1><p>Open a camera, draw its areas and save the downloaded JSON files in one directory. Missing source cameras are listed in status.csv.</p><ul>'+''.join(links)+'</ul>')
    with (out/'status.csv').open('w',newline='')as f:
        w=csv.DictWriter(f,fieldnames=list(status[0]));w.writeheader();w.writerows(status)
    print(out/'index.html')

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--inventory',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--site',action='append')
    a=ap.parse_args();build(a.inventory,a.out,a.site)
