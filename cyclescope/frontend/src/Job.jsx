import { useEffect, useState } from "react";
import { api } from "./api";
import Review from "./Review";
import Calibrate from "./Calibrate";

export default function Job({ id }) {
  const [job, setJob] = useState(null);
  const [view, setView] = useState("review");
  const [err, setErr] = useState("");

  // Poll while the backend is detecting + tracking.
  useEffect(() => {
    let stop = false, timer;
    const tick = async () => {
      try {
        const j = await api.get(id);
        if (stop) return;
        setJob(j);
        if (j.status === "queued" || j.status === "processing") timer = setTimeout(tick, 1500);
      } catch (e) { setErr(e.message); }
    };
    tick();
    return () => { stop = true; clearTimeout(timer); };
  }, [id]);

  const reprocess = async () => {
    try { await api.reprocess(id); location.reload(); }
    catch(e){setErr(e.message);}
  };
  if (err) return <p className="error" role="alert">{err}</p>;
  if (!job) return <p className="muted">Loading…</p>;
  if (job.status === "failed") return <section className="failure-card"><p className="eyebrow">PROCESSING INTERRUPTED</p><h1>Let’s get this video running.</h1><p>{job.name}</p><p className="muted">The upload is preserved. You can retry with the updated pipeline without uploading again.</p><div className="btns"><button className="btn primary" onClick={reprocess}>Retry processing</button><a className="btn" href="#/">Back to dashboard</a></div><details><summary>Technical error details</summary><pre>{job.error}</pre></details></section>;
  if (job.status !== "ready")
    return (
      <div className="progress-wrap">
        <h2>{job.status==='queued'?'Queued: ':'Analyzing: '}{job.name}</h2>
        <a href="#/">Back to dashboard / queue more videos</a>
        <progress value={job.progress} max="1" />
        <p className="muted">{Math.round(job.progress * 100)}%. {job.status==='queued'?'Waiting for a processing slot. Other videos can run in parallel.':'Detecting and tracking road users.'}</p>
      </div>
    );

  const legacy = job.meta?.pipeline !== 'xclip_overlay_v19_colonial.py';
  return (
    <>
      {legacy && <div className="banner">This video was processed by the old standalone model. Existing metric results are excluded. <button className="btn" onClick={reprocess}>Reprocess with RT-DETR + X-CLIP</button></div>}
      {job.meta?.source_offset_s != null && <p className="muted">Review timeline starts at 0. Selected original-file interval: {job.meta.source_offset_s.toFixed(1)}–{(job.meta.source_offset_s+job.meta.selected_duration_s).toFixed(1)} seconds. Camera clock: {job.meta.clip_camera_clock || "unknown; elapsed time is used"}.</p>}
      <nav className="tabs main" aria-label="Workflow">
        <button className={view === "review" ? "on" : ""} onClick={() => setView("review")}>Review</button>
        <button className={view === "calibrate" ? "on" : ""} onClick={() => setView("calibrate")}>
          Calibrate{job.analysis.calibrated ? "" : " (needed)"}
        </button>
        <span className="file">{job.name}</span>
      </nav>
      {view === "review"
        ? <Review job={job} setJob={setJob} onCalibrate={() => setView("calibrate")} />
        : <Calibrate job={job} setJob={setJob} done={() => setView("review")} />}
    </>
  );
}
