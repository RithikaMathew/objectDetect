import { useEffect, useState } from "react";
export default function SpeedEditor({ track, analysis, save, busy }) {
  const current=analysis.speeds[track.id];
  const override=current?.source==='reviewed_override'?current:null;
  const [mph,setMph]=useState(override?.median_mph??''),[reason,setReason]=useState(override?.reason||''),[notice,setNotice]=useState('');
  const computed=analysis.computed_speeds?.[track.id]?.median_mph;
  useEffect(()=>{setMph(override?.median_mph??'');setReason(override?.reason||'');},[track.id,override?.median_mph,override?.reason]);
  const persist=async restore=>{
    setNotice('');
    const ok=await save(restore?{mph:null}:{mph:Number(mph),reason:reason.trim()||'Reviewer-entered speed correction; measurement source not specified'});
    if(ok)setNotice(restore?`Restored calculated speed for object #${track.id}.`:`Saved ${Number(mph)} mph for object #${track.id}. Other objects keep their own speeds.`);
  };
  return <div className="speed-review">
    <div className="speed-current"><span>Object #{track.id} speed</span><strong>{current?`${current.median_mph} mph`:'Not measured'}</strong><small>{override?'Reviewed value':current?'Calculated from trajectory':'Add calibration or enter a reviewed value'}</small></div>
    <details className="speed-editor"><summary>Edit this object’s speed</summary>
      <p className="muted">This value belongs only to object #{track.id}. Save before switching objects. Trajectory-based interaction metrics keep using the original motion.</p>
      <label>Speed (mph)<input aria-label="Reviewed speed mph" type="number" min="0" step=".1" value={mph} onChange={e=>{setMph(e.target.value);setNotice('');}}/></label>
      <label>Source / note (optional)<input aria-label="Speed measurement reason" value={reason} onChange={e=>setReason(e.target.value)}/></label>
      <div className="btns"><button className="btn primary" disabled={busy||mph===''||!Number.isFinite(Number(mph))||Number(mph)<0} onClick={()=>persist(false)}>{busy?'Saving…':'Save reviewed speed'}</button>{override&&<button className="btn" disabled={busy} onClick={()=>persist(true)}>Restore calculated speed</button>}</div>
      <p className="muted">Original calculation: {computed!=null?`${computed} mph`:'unavailable'}. Reviewed changes are retained in the export history.</p>
    </details>
    {notice&&<p className="save-notice" role="status">{notice}</p>}
  </div>;
}
