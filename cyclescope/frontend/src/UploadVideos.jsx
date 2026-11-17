import { useEffect, useRef, useState } from "react";
import { api } from "./api";
const time = seconds => `${Math.floor(seconds/3600).toString().padStart(2,'0')}:${Math.floor(seconds/60%60).toString().padStart(2,'0')}:${Math.floor(seconds%60).toString().padStart(2,'0')}`;
function filenameClock(name) {
  const m=name.match(/Standard_[A-Za-z0-9]+_(\d{4}-\d{2}-\d{2})_(\d{2})(\d{2})\.(\d{3})\.(mp4|mov)$/i);
  if(!m)return '';
  const d=new Date(`${m[1]}T${m[2]}:${m[3]}:00Z`);d.setUTCHours(d.getUTCHours()+Number(m[4])-1);
  return Number.isFinite(+d)?d.toISOString().slice(0,19):'';
}
export default function UploadVideos({ onQueued, recordingLabel, jobs = [] }) {
  const [files,setFiles]=useState([]),[busy,setBusy]=useState(false),[error,setError]=useState(''),[workers,setWorkers]=useState(2);
  const urls=useRef([]),videos=useRef({});
  useEffect(()=>{api.config().then(c=>setWorkers(c.processing_workers)).catch(()=>{});return ()=>urls.current.forEach(URL.revokeObjectURL);},[]);
  const update=(id,patch)=>setFiles(rows=>rows.map(r=>r.id===id?{...r,...patch}:r));
  const choose=selected=>{const rows=Array.from(selected).map(file=>{const url=URL.createObjectURL(file);urls.current.push(url);return {id:crypto.randomUUID(),file,url,start:0,end:0,duration:0,status:'selected',clock:filenameClock(file.name),useClock:false};});setFiles(old=>[...old,...rows]);};
  const preset=(row,kind)=>{const d=row.duration;update(row.id,kind==='first'?{start:0,end:Math.min(600,d)}:kind==='last'?{start:Math.max(0,d-900),end:d}:{start:0,end:d});};
  const queue=async()=>{
    setBusy(true);setError('');
    const pending=files.filter(f=>['selected','failed'].includes(f.status));let cursor=0;
    const uploadNext=async()=>{while(cursor<pending.length){const row=pending[cursor++];update(row.id,{status:'uploading',message:''});try{const job=await api.upload(row.file,row.useClock?row.clock:undefined,{start:row.start,end:row.end});update(row.id,{status:'queued',jobId:job.id});onQueued();}catch(e){update(row.id,{status:'failed',message:e.message});}}};
    await Promise.all(Array.from({length:Math.min(3,pending.length)},uploadNext));setBusy(false);
  };
  const pending=files.filter(f=>['selected','failed'].includes(f.status));
  return <section className="upload-videos">
    <p>Select one or more local videos. Choose a portion of each video before processing. {recordingLabel}</p>
    <label className="drop"><input aria-label="Choose local videos" type="file" accept="video/*" multiple disabled={busy} onChange={e=>{choose(e.target.files);e.target.value='';}}/><strong>Choose local videos</strong><span>Batch uploads · up to {workers} videos process at once</span></label>
    <p className="muted">The timeline starts at 00:00:00 in each file. You do not need to know the real recording time to select a clip.</p>
    {files.map(row=><article className="upload-card" key={row.id}>
      <div className="toolbar"><h3>{row.file.name}</h3><span className="chip">{jobs.find(j=>j.id===row.jobId)?.status || row.status}</span>{row.jobId?<a href={`#/job/${row.jobId}`}>Open processing / review</a>:<button className="link" disabled={busy} onClick={()=>{URL.revokeObjectURL(row.url);setFiles(f=>f.filter(r=>r.id!==row.id));}}>Remove from batch</button>}</div>
      {!row.jobId&&<><video ref={v=>{videos.current[row.id]=v;}} src={row.url} controls muted preload="auto" onLoadedMetadata={e=>{const d=e.target.duration;if(Number.isFinite(d)&&d>0)update(row.id,{duration:d,end:d});else update(row.id,{message:'Unable to read video duration'});}} onError={()=>update(row.id,{message:'This browser cannot preview this format. Convert to MP4 to select a clip.'})} onTimeUpdate={e=>{if(!e.target.paused&&e.target.currentTime>=row.end)e.target.pause();}}/>
      {row.duration>0&&<fieldset disabled={busy}><legend>Portion to analyze · {time(row.duration)} total</legend><div className="btns"><button className="btn" onClick={()=>preset(row,'all')}>Entire video</button><button className="btn" onClick={()=>preset(row,'first')}>First 10 minutes</button><button className="btn" onClick={()=>preset(row,'last')}>Last 15 minutes</button><button className="btn" onClick={()=>{const v=videos.current[row.id];v.currentTime=row.start;v.play().catch(e=>setError(e.message));}}>Preview selection</button></div>
      <label className="field">Start · {time(row.start)}<input aria-label={`Clip start ${row.file.name}`} type="range" min="0" max={Math.max(0,row.end-.1)} step=".1" value={row.start} onChange={e=>update(row.id,{start:Number(e.target.value)})}/></label>
      <label className="field">End · {time(row.end)}<input aria-label={`Clip end ${row.file.name}`} type="range" min={row.start+.1} max={row.duration} step=".1" value={row.end} onChange={e=>update(row.id,{end:Number(e.target.value)})}/></label><p>Selected {time(row.start)}–{time(row.end)} · {((row.end-row.start)/60).toFixed(2)} minutes</p>
      <details><summary>Real recording clock (optional, for day/night rules)</summary><p>Example: a file starts at 2:30 PM on July 10. That clock time is different from 00:00 on its playback timeline. File metadata and names may be wrong; a burned-in camera clock should be checked manually.</p>{row.clock&&<p>Filename hint: {row.clock.replace('T',' ')}. This is inferred from session/chunk numbering, not verified capture time.</p>}<label className="field">Camera date and time at the beginning of the original file<input aria-label={`Recording clock ${row.file.name}`} type="datetime-local" step="1" value={row.clock} onChange={e=>update(row.id,{clock:e.target.value})}/></label><label className="check"><input type="checkbox" checked={row.useClock} disabled={!row.clock} onChange={e=>update(row.id,{useClock:e.target.checked})}/> I checked this camera clock; use it for day/night classification</label><p className="muted">If unchecked, processing uses elapsed time and disables day/night rules. The selected clip offset is added automatically.</p></details>
      </fieldset>}</>}
      {row.message&&<p className="error" role="alert">{row.message}</p>}
    </article>)}
    {pending.length>0&&<button className="btn primary" disabled={busy||pending.some(r=>!r.duration||r.end<=r.start||(r.useClock&&!r.clock))} onClick={queue}>{busy?'Uploading batch…':`Process ${pending.length} selected video${pending.length===1?'':'s'}`}</button>}
    {error&&<p className="error" role="alert">{error}</p>}
  </section>;
}
