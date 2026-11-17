import { useState } from "react";
import Stage from "./Stage";
import { api } from "./api";

const regionColor = index => `hsl(${index*137.508%360} 70% 42%)`;
const nextColor = regions => { let index=0; const used=new Set(regions.map(r=>r.color)); while(used.has(regionColor(index))) index++; return regionColor(index); };

export default function Calibrate({ job, setJob, done }) {
  const c = job.calibration;
  const [pts, setPts] = useState(c?.image_points || []);
  const [world, setWorld] = useState(c?.world_points_metres || (c?.image_points || []).map(() => ["", ""]));
  const [regions, setRegions] = useState((job.regions || c?.regions || []).map((r,i)=>({...r,color:r.color||regionColor(i)})));
  const [regionType, setRegionType] = useState("main road");
  const [draft, setDraft] = useState([]), [tool, setTool] = useState("landmarks"), [name, setName] = useState("main road");
  const [source, setSource] = useState(c?.measurement_source || ""), [err, setErr] = useState(""), [busy, setBusy] = useState(false);
  const render = (ctx, _f, sx, sy) => {
    ctx.font = "600 13px system-ui";
    for (const [index,r] of [...regions, {name, points:draft, color:nextColor(regions)}].entries()) {
      if (!r.points.length) continue;
      ctx.beginPath(); r.points.forEach(([x,y],i) => i ? ctx.lineTo(x*sx,y*sy) : ctx.moveTo(x*sx,y*sy));
      if (r.points.length >= 3) ctx.closePath();
      const color=r.color || `hsl(${index*137.508%360} 70% 42%)`;
      ctx.fillStyle=color;ctx.globalAlpha=.18;ctx.fill();ctx.globalAlpha=1;ctx.strokeStyle=color;ctx.lineWidth=3;ctx.stroke();
      ctx.fillStyle = "white"; ctx.fillText(r.name, r.points[0][0]*sx+8, r.points[0][1]*sy+16);
    }
    pts.forEach(([x,y],i) => {ctx.beginPath();ctx.arc(x*sx,y*sy,5,0,Math.PI*2);ctx.fillStyle="#FFB000";ctx.fill();ctx.fillText(`${i+1} · ${Math.round(x)}, ${Math.round(y)} px`,x*sx+8,y*sy-8);});
  };
  const add = point => {
    if (!point.every(Number.isFinite)) return;
    if (tool === "regions") setDraft(p => [...p,point]);
    else {setPts(p => [...p,point]);setWorld(p => [...p,p.length===0?[0,0]:["", ""]]);}
  };
  const finish = () => {
    if (draft.length < 3 || !name.trim()) return;
    setRegions(r => [...r,{name:name.trim(),type:regionType,points:draft,color:nextColor(r)}]);setDraft([]);
  };
  const save = async () => {
    setBusy(true);setErr("");
    try {setJob(await api.setCalibration(job.id,{image_points:pts,world_points_metres:world.map(p=>p.map(Number)),regions,measurement_source:source.trim()}));done();}
    catch(e){setErr(e.message);}finally{setBusy(false);}
  };
  const saveRegions = async () => {
    setBusy(true);setErr('');
    try { setJob(await api.setRegions(job.id,regions));done(); }
    catch(e){setErr(e.message);}finally{setBusy(false);}
  };
  const valid = pts.length>=4 && world.every(p => p.every(v=>v!=="" && Number.isFinite(Number(v)))) && source.trim() && !draft.length;
  return <div className="split">
    <Stage src={api.videoUrl(job.id)} fps={job.meta.fps} render={render} onPoint={add}/>
    <aside className="panel calibration-panel">
      <h2>Landmarks and road regions</h2>
      <p className="hint"><strong>Landmarks set the scale.</strong> Each click records image X/Y in pixels. Enter the corresponding measured ground X/Y in metres to calculate speed and distance.<br/><strong>Regions label areas.</strong> Outline a sidewalk, bike lane or road; these polygons do not measure distance.</p>
      <details className="calibration-guide"><summary>What do Ground X and Ground Y mean?</summary><p>They are real distances along the ground, measured in metres from an origin you choose. The first clicked landmark is set to (0, 0). X can run across the road; Y can run along it. Other points stay empty because clicking a picture cannot tell us real distances.</p><p>Example only: if measured landmarks form a 4 m wide, 10 m long area, their coordinates could be (0,0), (4,0), (4,10), (0,10). Use your actual measurements; do not copy these example dimensions. Additional landmarks can be anywhere with known coordinates.</p><p>If you do not know real distances, you can still review objects and label regions. Metric speed/distance needs measured calibration or a reviewed speed from another source.</p></details>
      <div className="seg"><button className={tool==='landmarks'?'on':''} onClick={()=>setTool('landmarks')}>Landmarks</button><button className={tool==='regions'?'on':''} onClick={()=>setTool('regions')}>Regions</button></div>
      {tool==='landmarks' ? <><p>{pts.length} landmarks. Click the video to add another.</p><table><thead><tr><th>Point / image px</th><th>Ground X (m)</th><th>Ground Y (m)</th><th/></tr></thead><tbody>{pts.map((p,i)=><tr key={i}><td>{i+1}<small className="facility">X {p[0].toFixed(1)}<br/>Y {p[1].toFixed(1)}</small></td>{[0,1].map(axis=><td key={axis}><input aria-label={`Point ${i+1} ${axis?'Y':'X'} metres`} type="number" step="any" value={world[i]?.[axis]??''} placeholder="Measured" onChange={e=>setWorld(w=>w.map((v,j)=>j===i?v.map((n,a)=>a===axis?e.target.value:n):v))}/></td>)}<td><button className="link" onClick={()=>{setPts(p=>p.filter((_,j)=>i!==j));setWorld(p=>p.filter((_,j)=>i!==j));}}>Remove</button></td></tr>)}</tbody></table></> : <>
        <p>Click any number of polygon vertices to outline a sidewalk, main road, bike lane or crosswalk.</p>
        <label className="field">Region type<select aria-label="Region type" value={regionType} onChange={e=>{setRegionType(e.target.value);setName(e.target.value==='other'?'':e.target.value);}}>{['main road','sidewalk','bike lane','crosswalk','shared path','grass','parking','other'].map(n=><option key={n} value={n}>{n}</option>)}</select></label>
        <label className="field">Region name<input aria-label="Region name" value={name} onChange={e=>setName(e.target.value)} placeholder="e.g. north sidewalk"/></label>
        <div className="btns"><button className="btn" onClick={finish} disabled={draft.length<3||!name.trim()}>Finish polygon ({draft.length} points)</button><button className="btn" onClick={()=>setDraft(p=>p.slice(0,-1))}>Undo point</button><button className="btn" onClick={()=>setDraft([])}>Clear draft</button></div>
      </>}
      <ul>{regions.map((r,i)=><li key={i}><i className="region-swatch" style={{background:r.color||`hsl(${i*137.508%360} 70% 42%)`}}/>{r.name} · {r.points.length} vertices <button className="link" onClick={()=>setRegions(r=>r.filter((_,j)=>j!==i))}>Remove</button></li>)}</ul>
      <p className="muted">Regions label facilities. Metric estimates stay inside the landmark hull and assume a shared ground plane; a raised or sloped sidewalk needs its own measured calibration. Polygon outlines alone do not establish scale.</p>
      <label className="field">Measurement source<input value={source} onChange={e=>setSource(e.target.value)} placeholder="e.g. surveyed ground landmarks"/></label>
      {err&&<p className="error" role="alert">{err}</p>}
      <button className="btn" disabled={busy||Boolean(draft.length)} onClick={saveRegions}>Save regions only</button>
      <p className="muted">Save regions without ground coordinates. Speed and distance stay unavailable until metric calibration is complete.</p>
      <button className="btn primary" disabled={!valid||busy} onClick={save}>{busy?'Recomputing…':'Save and recompute'}</button>
    </aside>
  </div>;
}
