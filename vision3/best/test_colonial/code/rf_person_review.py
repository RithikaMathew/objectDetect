#!/usr/bin/env python3
"""Build raw-frame person-box review / score frozen RF-DETR and DINO proposals.

Review existing outputs, no new inference. Person recall only, not cyclist
counting. Selected encounter midpoints + fixed background frames, not an
unbiased sample or a new test set. Unreviewed frames never count as empty.
"""
import argparse
import csv
import json
from pathlib import Path
import shutil
from eval_truth import CLIPS,read_truth
from submit_research import VIDEO_DIR


def iou(a,b):
    inter=max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
    union=max(0,a[2]-a[0])*max(0,a[3]-a[1])+max(0,b[2]-b[0])*max(0,b[3]-b[1])-inter
    return inter/union if union>0 else 0


def score_frame(truth,proposals):
    # Maximum one-to-one matching, avoiding order-dependent greedy undercount.
    edges=[[j for j,t in enumerate(truth)if iou(p['box'],t)>=.5]for p in proposals]
    assigned={}
    def augment(i,seen):
        for j in edges[i]:
            if j in seen:continue
            seen.add(j)
            if j not in assigned or augment(assigned[j],seen):assigned[j]=i;return True
        return False
    tp=sum(augment(i,set())for i in range(len(proposals)))
    return tp,len(proposals)-tp,len(truth)-tp


def proposals(path,frame):
    out=[]
    with path.open()as f:
        for row in csv.DictReader(f):
            label=row['label'].strip().lower().replace('a person','person').strip('. ')
            if int(row['frame'])==frame and label=='person':
                out.append(dict(box=[float(row[k])for k in ('x1','y1','x2','y2')],score=float(row['score'])))
    return out


def build(root,out):
    import cv2
    out.mkdir(parents=True,exist_ok=False);assets=out/'frames';assets.mkdir()
    manifest=[]
    for clip,cc in CLIPS.items():
        rf=root/'logs/rfdetr_oct19'/clip;dino=root/'logs/research_oct19/grounding'/clip
        for folder in (rf,dino):
            if not(folder/'proposals.csv').is_file()or not(folder/'summary.json').is_file():raise FileNotFoundError(folder)
        truth,skipped=read_truth(root/cc['truth'])
        if skipped:raise ValueError('Incomplete truth')
        video=VIDEO_DIR/f'Standard_SCU8OG_2019-07-10_0000.{cc["chunk"]:03d}.mp4'
        cap=cv2.VideoCapture(str(video));fps=cap.get(cv2.CAP_PROP_FPS)
        if not cap.isOpened()or fps<=0:raise RuntimeError(f'Cannot open {video}')
        offset=int(cc['start'][14:16])*60
        times=sorted(set([0.,300.,600.,870.]+[round((p['s']+p['e'])/2,3)for p in truth]))
        for when in times:
            fi=round((offset+when)*fps)+1
            # The selected frame must exist in both completed audits, including zero-box frames.
            for folder in (rf,dino):
                if not list(folder.glob(f'{fi:06d}_*.jpg')):raise RuntimeError(f'No matching audit image: {folder}, frame {fi}')
            cap.set(cv2.CAP_PROP_POS_FRAMES,fi-1);ok,image=cap.read()
            if not ok:raise RuntimeError(f'Unreadable frame {fi}')
            name=f'{clip}_{fi}.jpg'
            if not cv2.imwrite(str(assets/name),image):raise RuntimeError('Image write failed')
            manifest.append(dict(id=f'{clip}:{fi}',clip=clip,frame=fi,clip_second=when,image='frames/'+name,
                width=image.shape[1],height=image.shape[0],rf=proposals(rf/'proposals.csv',fi),dino=proposals(dino/'proposals.csv',fi)))
        cap.release()
    (out/'manifest.json').write_text(json.dumps(dict(frames=manifest),indent=2))
    # Prediction boxes are deliberately absent from the labelling HTML.
    blinded=[{k:v for k,v in r.items()if k not in ('rf','dino')}for r in manifest]
    html='''<!doctype html><meta charset="utf-8"><title>Existing-frame human review</title>
<style>body{font:18px sans-serif;max-width:950px;margin:25px auto}canvas{max-width:100%;border:1px solid #888;touch-action:none}button{font:inherit;margin:8px}label{display:block}</style>
<h1>Person detection check — existing frames</h1><p>Draw one tight box around EVERY visible person, including cyclists and scooter riders. Head/body/feet; do not box bicycles separately. Drag on the raw image. Mark reviewed even when there are zero people. This tests person boxes, not cyclist counting. Predictions are hidden to reduce bias.</p>
<p id="position"></p><canvas id="canvas"></canvas><div><button id="prev">Previous</button><button id="next">Next</button><button id="undo">Undo box</button></div><label><input id="reviewed" type="checkbox"> I checked the whole frame; every visible person is boxed (or there are none).</label><button id="export">Download review JSON</button><p>Keep the whole folder together. Finish labels before viewing model annotation images. Unchecked frames will be excluded.</p>
<script>
const frames=FRAMES;let current=0,start=null;const labels=Object.fromEntries(frames.map(f=>[f.id,{reviewed:false,boxes:[]}])) ;
const canvas=document.getElementById('canvas'),ctx=canvas.getContext('2d'),pic=new Image();
const reviewed=document.getElementById('reviewed');
const storageKey='person_review_v1:'+location.pathname;try{const saved=JSON.parse(localStorage.getItem(storageKey)||'{}');for(const f of frames)if(saved[f.id])labels[f.id]=saved[f.id]}catch(e){}
function save(){try{localStorage.setItem(storageKey,JSON.stringify(labels))}catch(e){}}
function draw(){ctx.clearRect(0,0,canvas.width,canvas.height);ctx.drawImage(pic,0,0);ctx.strokeStyle='#00dd00';ctx.lineWidth=2;for(const b of labels[frames[current].id].boxes)ctx.strokeRect(b[0],b[1],b[2]-b[0],b[3]-b[1]);}
function show(){const f=frames[current];canvas.width=f.width;canvas.height=f.height;pic.onload=draw;pic.src=f.image;reviewed.checked=labels[f.id].reviewed;document.getElementById('position').textContent=`${current+1}/${frames.length}: ${f.clip}, clip second ${f.clip_second}`;}
function point(e){const r=canvas.getBoundingClientRect();return [(e.clientX-r.left)*canvas.width/r.width,(e.clientY-r.top)*canvas.height/r.height].map((x,i)=>Math.max(0,Math.min(x,i?canvas.height:canvas.width)));}
canvas.onpointerdown=e=>{start=point(e);canvas.setPointerCapture(e.pointerId)};
canvas.onpointerup=e=>{if(!start)return;const end=point(e),b=[Math.min(start[0],end[0]),Math.min(start[1],end[1]),Math.max(start[0],end[0]),Math.max(start[1],end[1])];if(b[2]-b[0]>2&&b[3]-b[1]>2){labels[frames[current].id].boxes.push(b);labels[frames[current].id].reviewed=false;reviewed.checked=false;}start=null;save();draw()};
reviewed.onchange=()=>{labels[frames[current].id].reviewed=reviewed.checked;save()};
document.getElementById('prev').onclick=()=>{current=Math.max(0,current-1);show()};document.getElementById('next').onclick=()=>{current=Math.min(frames.length-1,current+1);show()};
document.getElementById('undo').onclick=()=>{labels[frames[current].id].boxes.pop();labels[frames[current].id].reviewed=false;reviewed.checked=false;save();draw()};
document.getElementById('export').onclick=()=>{const data={protocol:'all_visible_person_boxes_v1',frames:labels},a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));a.download='person_box_review.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)};show();</script>'''.replace('FRAMES',json.dumps(blinded))
    (out/'review.html').write_text(html)
    print(f'{len(manifest)} selected frames: {out}/review.html')


def evaluate(pack,review,out):
    frames=json.loads((pack/'manifest.json').read_text())['frames'];annotations=json.loads(review.read_text())
    if annotations.get('protocol')!='all_visible_person_boxes_v1':raise ValueError('Wrong review protocol')
    known={f['id']for f in frames}
    if set(annotations['frames'])-known:raise ValueError('Unknown frame IDs')
    totals={model:[0,0,0]for model in ('rf','dino')};n=0
    for f in frames:
        annotation=annotations['frames'].get(f['id'],{})
        if annotation.get('reviewed')is not True:continue
        boxes=annotation.get('boxes',[])
        for b in boxes:
            if len(b)!=4 or not(0<=b[0]<b[2]<=f['width']and 0<=b[1]<b[3]<=f['height']):raise ValueError('Invalid truth box')
        n+=1
        for model in totals:
            score=score_frame(boxes,f[model]);totals[model]=[a+b for a,b in zip(totals[model],score)]
    if n==0:raise ValueError('No reviewed frames; no accuracy result can be calculated')
    lines=['# Person-box validation on selected existing frames','',f'Reviewed frames: {n}/{len(frames)}. Unreviewed frames excluded.',
           'Person proposals only, one-to-one IoU>=0.50. Cyclists/scooter riders contribute person boxes, not mode labels.',
           'Thresholds are the saved audit thresholds. This is NOT AP, unique-person recall, continuous-video counting accuracy or an independent holdout test.','',
           '| Detector | Correct boxes TP | False boxes FP | Missed boxes FN | Precision | Recall |','|---|---:|---:|---:|---:|---:|']
    for model,(tp,fp,fn)in totals.items():
        precision=f'{tp/(tp+fp):.3f}'if tp+fp else 'undefined';recall=f'{tp/(tp+fn):.3f}'if tp+fn else 'undefined'
        lines.append(f'| {model} | {tp} | {fp} | {fn} | {precision} | {recall} |')
    out.write_text('\n'.join(lines)+'\n');print(out)


def main():
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='mode',required=True)
    b=sub.add_parser('build');b.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);b.add_argument('--out',type=Path,required=True)
    e=sub.add_parser('score');e.add_argument('--pack',type=Path,required=True);e.add_argument('--review',type=Path,required=True);e.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    if a.mode=='build':build(a.root.resolve(),a.out.resolve())
    else:evaluate(a.pack,a.review,a.out)


if __name__=='__main__':main()
