#!/usr/bin/env python3
"""Build a browser tool for manually tracking an occluded road user.

The tool overlays saved detector boxes when available, accepts manual clicks for
pedestrian/car contact points, and exports a CSV for the CPU metric comparison.
It never changes the original trajectory exports.
"""
import argparse
import csv
import json
from pathlib import Path


def read_rows(path):
    with Path(path).open(newline="") as stream:
        return list(csv.DictReader(stream))


def build(batch, task_name, out):
    batch = Path(batch).resolve()
    task = batch / task_name
    manifest = json.loads((batch / "manifest.json").read_text())
    task_plan = next(item for item in manifest["tasks"] if item["key"] == task_name)
    video_name = task_plan["clip_key"] + ".mp4"
    video_rel = f"inputs/{video_name}"
    run_log = json.loads((task / "run_log.json").read_text())
    fps = float(run_log["fps"])
    trajectory_rows = read_rows(task / "trajectories_csv.csv")
    vehicle_rows = read_rows(task / "vehicle_trajectories_csv.csv")
    all_rows = trajectory_rows + vehicle_rows
    # Keep the event neighborhood small enough for a standalone HTML file.
    auto = {}
    for row in all_rows:
        frame = int(row["frame"])
        seconds = (frame - 1) / fps
        if 40 <= seconds <= 53:
            auto.setdefault(str(frame), []).append({
                "label": row.get("label", ""),
                "track_id": row["track_id"],
                "x": float(row["foot_x"]),
                "y": float(row["foot_y"]),
                "w": float(row["box_w"]),
                "h": float(row["box_h"]),
            })
    page = f'''<!doctype html>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Manual occlusion tracker</title>
<style>
body{{font:15px system-ui;max-width:1100px;margin:24px auto;padding:0 16px;color:#17231f}}
.note{{background:#eef5f1;border-left:4px solid #0b765e;padding:12px}}
.stage{{position:relative;background:#111;max-width:900px}}
video{{display:block;width:100%}}canvas{{position:absolute;inset:0;width:100%;height:100%;cursor:crosshair}}
button,input,textarea,select{{font:inherit;padding:8px;margin:4px 4px 4px 0}}textarea{{width:100%;min-height:55px}}
#readout{{font-size:18px;font-weight:700}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ccd6d1;padding:5px;text-align:left}}
</style>
<h1>Manual pedestrian/car occlusion tracker</h1>
<p class="note"><b>Goal:</b> manually mark the pedestrian and car contact points through the overlap. Green boxes are saved pedestrian detections, blue boxes are saved vehicle detections, and red/yellow dots are your manual clicks. The manual click is evidence; the reconstructed metrics remain exploratory.</p>
<div class="stage"><video id="video" controls preload="metadata" src="{video_rel}"></video><canvas id="canvas"></canvas></div>
<p id="readout">Click the frame to place a point.</p>
<button id="back">Back one frame</button><button id="forward">Forward one frame</button>
<button id="markCar">Mark clicked point as car</button><button id="markPed">Mark clicked point as pedestrian</button>
<button id="download">Download annotation CSV</button>
<label>Reviewer <input id="reviewer"></label>
<textarea id="notes" placeholder="Optional note for this frame, e.g. car partly hidden behind pedestrian."></textarea>
<h2>Manual points</h2><table id="table"><tr><th>Frame</th><th>Seconds</th><th>Object</th><th>x</th><th>y</th><th>Note</th></tr></table>
<script>
const video=document.getElementById('video'), canvas=document.getElementById('canvas'), ctx=canvas.getContext('2d');
const auto={json.dumps(auto,separators=(',',':'))}; const fps={fps}; let clicked=null; const points=[];
function frameNumber(){{return Math.max(1,Math.round(video.currentTime*fps)+1);}}
function draw(){{
  if(!video.videoWidth) return;
  canvas.width=video.videoWidth; canvas.height=video.videoHeight; ctx.clearRect(0,0,canvas.width,canvas.height);
  const observations=auto[String(frameNumber())]||[];
  for(const row of observations){{const pedestrian=row.label.toUpperCase()==='PEDESTRIAN'; ctx.strokeStyle=pedestrian?'#00dd66':'#279cff'; ctx.lineWidth=2; ctx.strokeRect(row.x-row.w/2,row.y-row.h,row.w,row.h); ctx.fillStyle=ctx.strokeStyle; ctx.font='13px sans-serif'; ctx.fillText((pedestrian?'PEDESTRIAN ':'VEHICLE ')+row.track_id,row.x-row.w/2,Math.max(14,row.y-row.h-3));}}
  for(const point of points.filter(item=>item.frame===frameNumber())){{ctx.fillStyle=point.object==='car'?'#ff3b30':'#ffd60a'; ctx.beginPath();ctx.arc(point.x,point.y,6,0,Math.PI*2);ctx.fill();}}
    const label=clicked?`click x=${{clicked.x}} y=${{clicked.y}}`:'click the image to choose a point'; document.getElementById('readout').textContent=`clip +${{video.currentTime.toFixed(3)}}s | frame ${{frameNumber()}} | ${{label}}`;
}}
function clickPoint(event){{const rect=canvas.getBoundingClientRect(); clicked={{x:Math.round((event.clientX-rect.left)*canvas.width/rect.width),y:Math.round((event.clientY-rect.top)*canvas.height/rect.height)}};draw();}}
function mark(object){{if(!clicked){{alert('Click the image first.');return;}} points.push({{frame:frameNumber(),clip_seconds:video.currentTime,object,x_px:clicked.x,y_px:clicked.y,reviewer:document.getElementById('reviewer').value,notes:document.getElementById('notes').value}}); render(); draw();}}
function render(){{const table=document.getElementById('table'); table.innerHTML='<tr><th>Frame</th><th>Seconds</th><th>Object</th><th>x</th><th>y</th><th>Note</th></tr>'; for(const p of points){{const tr=document.createElement('tr');tr.innerHTML=`<td>${{p.frame}}</td><td>${{p.clip_seconds.toFixed(3)}}</td><td>${{p.object}}</td><td>${{p.x_px}}</td><td>${{p.y_px}}</td><td>${{p.notes||''}}</td>`;table.appendChild(tr);}}}}
function csvCell(value){{return '"'+String(value??'').replaceAll('"','""')+'"';}}
document.getElementById('canvas').onclick=clickPoint; video.ontimeupdate=draw; video.onloadedmetadata=draw;
document.getElementById('back').onclick=()=>{{video.currentTime=Math.max(0,video.currentTime-1/fps);draw();}}; document.getElementById('forward').onclick=()=>{{video.currentTime=Math.min(video.duration||60,video.currentTime+1/fps);draw();}};
document.getElementById('markCar').onclick=()=>mark('car'); document.getElementById('markPed').onclick=()=>mark('pedestrian');
document.getElementById('download').onclick=()=>{{const lines=['frame,clip_seconds,object,x_px,y_px,reviewer,notes'];for(const p of points)lines.push([p.frame,p.clip_seconds.toFixed(6),p.object,p.x_px,p.y_px,p.reviewer,p.notes].map(csvCell).join(','));const blob=new Blob([lines.join('\\n')+'\\n'],{{type:'text/csv'}});const link=document.createElement('a');link.href=URL.createObjectURL(blob);link.download='manual_occlusion_points.csv';link.click();}};
</script>'''
    Path(out).write_text(page)
    print(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=Path, required=True)
    parser.add_argument("--task", default="colonial_1708_pedestrian_car_reference")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    build(args.batch, args.task, args.out)


if __name__ == "__main__":
    main()
