#!/usr/bin/env python3
"""Create a local gate-marking page; never infer distances from lane polygons."""
import argparse
import json
from pathlib import Path


def build(pack,out):
    frames=json.loads((pack/'manifest.json').read_text())['frames']
    frame=next(f for f in frames if f['clip']=='day')
    relative=str(Path('rf_boxes')/frame['image'])
    html='''<!doctype html><meta charset="utf-8"><title>Colonial measured speed gates</title>
<style>body{font:18px sans-serif;max-width:950px;margin:20px auto}canvas{max-width:100%;border:1px solid #888}label{display:block;margin:12px}input,button,select{font:inherit}</style>
<h1>Mark measured speed zones</h1><p>The lane polygons identify AREAS, not measured distances. Only use this if you can identify the actual start/end lines of the measured segment for THIS Colonial North camera/date. Workbook lengths alone do not identify image endpoints.</p>
<p>Select bike lane or sidewalk. Click two endpoints for the first cross-line, then two endpoints for the second. The cyclist must cross BOTH finite lines. Record numbers are not automatically matched to people.</p>
<label>Facility <select id="facility"><option value="bike_lane">Bike lane</option><option value="sidewalk">Sidewalk</option></select></label>
<canvas id="canvas"></canvas><button id="reset">Reset selected facility</button><p id="status"></p>
<label>Bike-lane measured distance (feet): <input id="bikeLength" type="number" value="35" min="0.01" step="any"></label>
<label>Sidewalk measured distance (feet): <input id="sideLength" type="number" value="30" min="0.01" step="any"></label>
<label>Your name <input id="reviewer"></label><label>How did you identify these exact measured segments? <input id="source" size="65"></label>
<label><input id="confirmed" type="checkbox"> I confirm these image lines correspond to independently measured segments for this camera/date.</label>
<button id="download">Download gate configuration</button><p id="message"></p>
<script>
const canvas=document.getElementById('canvas'),ctx=canvas.getContext('2d'),pic=new Image(),facility=document.getElementById('facility');
canvas.width=WIDTH;canvas.height=HEIGHT;pic.src=IMAGE;const points={bike_lane:[],sidewalk:[]};
function draw(){ctx.clearRect(0,0,canvas.width,canvas.height);ctx.drawImage(pic,0,0);for(const [name,p]of Object.entries(points)){ctx.strokeStyle=name==='bike_lane'?'#00ff00':'#ff22ff';ctx.fillStyle=ctx.strokeStyle;ctx.lineWidth=3;for(const q of p){ctx.beginPath();ctx.arc(q[0],q[1],4,0,7);ctx.fill()}for(let i=0;i+1<p.length;i+=2){ctx.beginPath();ctx.moveTo(...p[i]);ctx.lineTo(...p[i+1]);ctx.stroke()}}document.getElementById('status').textContent=`Selected ${facility.value}: ${points[facility.value].length}/4 points`;}
pic.onload=draw;facility.onchange=draw;canvas.onclick=e=>{const p=points[facility.value];if(p.length>=4)return;const r=canvas.getBoundingClientRect();p.push([(e.clientX-r.left)*canvas.width/r.width,(e.clientY-r.top)*canvas.height/r.height]);draw()};document.getElementById('reset').onclick=()=>{points[facility.value]=[];draw()};
document.getElementById('download').onclick=()=>{const reviewer=document.getElementById('reviewer').value.trim(),source=document.getElementById('source').value.trim(),gates=[];for(const [name,p]of Object.entries(points)){if(p.length===4){const length=Number(document.getElementById(name==='bike_lane'?'bikeLength':'sideLength').value);if(!(length>0))return;gates.push({facility:name,length_feet:length,line_a:p.slice(0,2),line_b:p.slice(2,4)})}}if(!gates.length||!reviewer||!source||!document.getElementById('confirmed').checked){document.getElementById('message').textContent='Finish at least one pair of gate lines and provide measurement confirmation, source and reviewer.';return;}const data={site:'Colonial North',recording_date:'2019-07-10',ref_size:[canvas.width,canvas.height],measurement_source:source,reviewer,gates},a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));a.download='colonial_speed_gates.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)};</script>'''
    html=html.replace('WIDTH',str(frame['width'])).replace('HEIGHT',str(frame['height'])).replace('IMAGE',json.dumps(relative))
    out.write_text(html);print(out)


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--pack',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();build(a.pack,a.out)
