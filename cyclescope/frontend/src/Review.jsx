import { useMemo, useState } from "react";
import Stage from "./Stage";
import SpeedEditor from "./SpeedEditor";
import { api } from "./api";

export const COLORS = { cyclist: "#FFB000", person: "#3DDC97", car: "#4FA3FF", truck: "#8E7CFF", bus: "#D17CFF", motorcycle: "#FF6B6B" };
const CLASSES = Object.keys(COLORS);
const clock = (s) => `${Math.floor(s / 60)}:${(s % 60).toFixed(1).padStart(4, "0")}`;

export default function Review({ job, setJob, onCalibrate }) {
  const { tracks, analysis, meta } = job;
  const [eventKey, setEventKey] = useState(null);
  const [tab, setTab] = useState("objects");
  const [sel, setSel] = useState(null);
  const [mode, setMode] = useState("view");
  const [extend, setExtend] = useState(false);
  const [saving, setSaving] = useState(false);
  const [newCls, setNewCls] = useState("cyclist");
  const [showHidden, setShowHidden] = useState(false);
  const [seekTo, setSeekTo] = useState(null);
  const [err, setErr] = useState("");

  const byId = useMemo(() => new Map(tracks.map((t) => [t.id, t])), [tracks]);
  const boxes = useMemo(() => new Map(tracks.map((t) => [t.id, new Map(t.boxes.map((b) => [b[0], b]))])), [tracks]);
  const hidden = (t) => t.deleted || t.suppressed;
  const shown = (t) => showHidden || !hidden(t);
  const events = analysis.events.filter((e) => e.status !== "rejected");
  const selectedEvent = analysis.events.find(e => e.key === eventKey) || analysis.events[0];
  const jump = (frame) => setSeekTo({ frame, n: Math.random() });
  const run = async (p) => { setSaving(true); try { setErr(""); setJob(await p); return true; } catch (e) { setErr(e.message); return false; } finally { setSaving(false); } };
  const t = sel != null ? byId.get(sel) : null;

  const render = (ctx, frame, sx, sy) => {
    ctx.font = "600 12px IBM Plex Sans, sans-serif"; ctx.textBaseline = "top";
    for (const tr of tracks) {
      const b = shown(tr) && boxes.get(tr.id).get(frame);
      if (!b) continue;
      const col = COLORS[tr.cls], off = hidden(tr), x = b[1] * sx, y = b[2] * sy;
      ctx.globalAlpha = off ? 0.4 : 1; ctx.setLineDash(off ? [5, 4] : []);
      ctx.strokeStyle = col; ctx.lineWidth = tr.id === sel ? 4 : 2;
      ctx.strokeRect(x, y, (b[3] - b[1]) * sx, (b[4] - b[2]) * sy);
      const sp = analysis.speeds[tr.id];
      const label = `#${tr.id} ${tr.cls}${sp ? ` ${sp.median_mph} mph` : ""}${tr.source === "manual" ? " (manual)" : ""}`;
      ctx.fillStyle = col; ctx.fillRect(x, y - 18, ctx.measureText(label).width + 8, 18);
      ctx.fillStyle = "#111"; ctx.fillText(label, x + 4, y - 15);
    }
    ctx.globalAlpha = 1; ctx.setLineDash([]);
    for (const e of events) {
      if (Math.abs(frame - e.frame) > meta.fps * 0.75) continue;
      const a = boxes.get(e.cyclist_id)?.get(frame), o = boxes.get(e.other_id)?.get(frame);
      if (!a || !o) continue;
      ctx.strokeStyle = "#FF3B30"; ctx.lineWidth = 3;
      ctx.beginPath(); ctx.moveTo(((a[1] + a[3]) / 2) * sx, a[4] * sy); ctx.lineTo(((o[1] + o[3]) / 2) * sx, o[4] * sy); ctx.stroke();
      ctx.fillStyle = "#FF3B30"; ctx.fillText(`Interaction ${e.min_dist_m} m`, ((a[1] + o[1]) / 2) * sx, (Math.min(a[2], o[2]) - 34) * sy);
    }
  };

  const pick = ([x, y], frame) => {
    let best = null, area = Infinity;
    for (const tr of tracks) {
      const b = shown(tr) && boxes.get(tr.id).get(frame);
      if (!b || x < b[1] || x > b[3] || y < b[2] || y > b[4]) continue;
      const a = (b[3] - b[1]) * (b[4] - b[2]);
      if (a < area) { area = a; best = tr.id; }
    }
    setSel(best);
    if (best != null) setTab("objects");
  };

  const onBox = (box, frame) => {
    if (saving) return;
    if (extend && t && t.source === "manual") return run(api.addKeyframe(job.id, t.id, { frame, box }));
    run(api.addTrack(job.id, { cls: newCls, frame, box })).then(() => setSel(null));
  };

  return (
    <div className="split">
      <div>
        {!analysis.calibrated && (
          <div className="banner">Metric estimates need measured calibration. Legacy videos must be reprocessed with RT-DETR + X-CLIP.{" "}
            <button className="link" onClick={onCalibrate}>Calibrate now</button></div>
        )}
        <div className="toolbar">
          <div className="seg" role="group" aria-label="Tool">
            <button className={mode === "view" ? "on" : ""} onClick={() => setMode("view")}>Select</button>
            <button className={mode === "draw" ? "on" : ""} onClick={() => { setMode("draw"); setExtend(false); }}>Add missing object</button>
          </div>
          {mode === "draw" && (
            <label>New object class{" "}
              <select aria-label="New object class" disabled={extend || saving} value={newCls} onChange={(e) => setNewCls(e.target.value)}>{CLASSES.map((c) => <option key={c}>{c}</option>)}</select>
            </label>
          )}
          <label className="check"><input type="checkbox" checked={showHidden} onChange={(e) => setShowHidden(e.target.checked)} /> Show deleted and hidden</label>
        </div>
        {mode === "draw" && t?.source === "manual" && <label className="check"><input type="checkbox" checked={extend} onChange={e => setExtend(e.target.checked)} /> Add keyframes to #{t.id} ({t.cls}) instead of a new object</label>}
        {saving && <p role="status">Saving correction…</p>}
        {mode === "draw" && (
          <p className="hint">Pause on a frame and drag a box around the object.
            {extend && t?.source === "manual" ? ` Dragging now adds a keyframe to #${t.id}; the box is interpolated between keyframes.` : " Each drag creates a new object with the chosen class."}</p>
        )}
        {err && <p className="error" role="alert">{err}</p>}
        <Stage src={api.videoUrl(job.id)} fps={meta.fps} render={render} mode={saving ? "view" : mode} onPoint={pick} onBox={onBox} seekTo={seekTo} />
      </div>

      <aside className="panel review-panel">
        <nav className="tabs" aria-label="Panels">
          {[["objects", `Objects (${tracks.filter((x) => !hidden(x)).length})`], ["events", `Interactions (${events.length})`], ["summary", "Summary"]].map(([k, label]) => (
            <button key={k} className={tab === k ? "on" : ""} onClick={() => setTab(k)}>{label}</button>
          ))}
        </nav>

        {tab === "objects" && (
          <>
            {!t && <section className="editor"><p className="muted">Select an object to review it.</p><div className="btns"><button className="btn danger" disabled>Delete object</button><button className="btn" disabled>Mark reviewed</button><button className="btn" disabled>Go to start</button></div></section>}
            {t && (
              <section className="editor">
                <h3>Object #{t.id} <small className="muted">{t.cls}</small></h3>
                <label className="field">Class
                  <select value={t.cls} onChange={(e) => run(api.patchTrack(job.id, t.id, { cls: e.target.value }))}>
                    {CLASSES.map((c) => <option key={c}>{c}</option>)}
                  </select>
                </label>
                {t.orig_cls && t.orig_cls !== t.cls && <p className="muted">Detector said {t.orig_cls}.</p>}
                <div className="btns">
                  {hidden(t)
                    ? <button className="btn" onClick={() => run(api.patchTrack(job.id, t.id, { deleted: false, suppressed: false }))}>Restore</button>
                    : <button className="btn danger" onClick={() => run(api.patchTrack(job.id, t.id, { deleted: true }))}>Delete: not a real object</button>}
                  <button className="btn" onClick={() => run(api.patchTrack(job.id, t.id, { reviewed: !t.reviewed }))}>
                    {t.reviewed ? "Reviewed ✓" : "Mark reviewed"}</button>
                  <button className="btn" onClick={() => jump(t.boxes[0][0])}>Go to start</button>
                </div>
                <SpeedEditor key={t.id} track={t} analysis={analysis} busy={saving} save={body=>run(api.setSpeed(job.id,t.id,body))}/>
                {t.suppressed && <p className="muted">Auto-hidden: this person is riding a bicycle.</p>}
              </section>
            )}
            <ul className="list">
              {tracks.filter(shown).map((x) => {
                const sp = analysis.speeds[x.id];
                return (
                  <li key={x.id}>
                    <button className={x.id === sel ? "row on" : "row"} disabled={saving} onClick={() => { setSel(x.id); jump(x.boxes[0][0]); }}>
                      <i style={{ background: COLORS[x.cls] }} />
                      <span>#{x.id} {x.cls}<small className="facility">{analysis.facilities?.[x.id] || x.facility || "unassigned"}</small></span>
                      <span className="meta" title={analysis.speed_status?.[x.id] || "Calibration and sufficient observed samples required"}>
                        {sp ? `${sp.median_mph} mph${sp.source==='reviewed_override'?' · reviewed':''}` : "Not measured"}{x.source === "manual" ? " manual" : ""}
                        {hidden(x) ? " hidden" : ""}{x.reviewed ? " ✓" : ""}
                      </span>
                    </button>
                  </li>
                );
              })}
            </ul>
          </>
        )}

        {tab === "events" && <section className="editor frozen-actions">
          <h3>Interaction controls</h3><p className="muted interaction-help">Review moments when a cyclist or pedestrian is near a vehicle. Select a pair, jump to that moment, then confirm or reject it after watching the video. A candidate is not an automatically proven near miss.</p>
          {selectedEvent ? <>
            <label className="field">Selected interaction<select aria-label="Selected interaction" value={selectedEvent.key} onChange={e=>setEventKey(e.target.value)}>{analysis.events.map(e=><option key={e.key} value={e.key}>#{e.cyclist_id} with #{e.other_id} · {clock(e.time_s)}</option>)}</select></label>
            <div className="btns"><button className="btn" onClick={()=>jump(selectedEvent.frame)}>Go to interaction</button><button className="btn" disabled={saving} onClick={()=>run(api.setEvent(job.id,selectedEvent.key,selectedEvent.status==='confirmed'?'auto':'confirmed'))}>{selectedEvent.status==='confirmed'?'Confirmed near miss ✓':'Confirm near miss'}</button><button className="btn" disabled={saving} onClick={()=>run(api.setEvent(job.id,selectedEvent.key,selectedEvent.status==='rejected'?'auto':'rejected'))}>{selectedEvent.status==='rejected'?'Rejected ✓':'Not a near miss'}</button></div>
          </> : <p className="muted">No eligible interactions to review. Metric comparisons need measured calibration, observed tracks and enough moving vehicles to establish road direction.</p>}
        </section>}
        {tab === "summary" && <section className="editor frozen-actions"><h3>Summary exports</h3><div className="btns"><a className="btn" href={api.exportUrl(job.id,"csv")}>Download CSV</a><a className="btn" href={api.exportUrl(job.id,"json")}>Download JSON</a></div></section>}
        {tab === "events" && (
          <ul className="list">
            <li className="muted pad">Closest distance is between ground-contact centers. Clearance uses assumed object dimensions. TTC predicts collision under current motion; PET estimates the gap between occupying a shared area. Missing values mean insufficient evidence, not zero. {analysis.note} {analysis.interaction_status}</li>
            {analysis.events.length === 0 && <li className="muted pad">{analysis.calibrated ? "No eligible interaction candidates found." : "Calibrate the ground to inspect interactions."}</li>}
            {analysis.events.map((e) => (
              <li key={e.key} className={`event ${e.status}`}>
                <span className="chip">{e.status==='confirmed'?'Confirmed by reviewer':e.status==='rejected'?'Rejected by reviewer':'Unreviewed candidate'}</span>
                <button className={selectedEvent?.key===e.key?"row on":"row"} onClick={() => { jump(e.frame); setSel(e.cyclist_id); setEventKey(e.key); }}>
                  <span>{e.subject_cls || "cyclist"} #{e.cyclist_id} and {e.other_cls} #{e.other_id}</span>
                  <span className="meta">{clock(e.time_s)} · {e.status==='auto'?'Unreviewed':e.status==='confirmed'?'Confirmed near miss':'Rejected'}</span>
                </button>
                <p className="muted pad">{e.min_dist_m} m closest{e.min_ttc_s != null ? `, predicted collision time ${e.min_ttc_s} s` : ""}. {e.metrics?.min_sampled_clearance_m != null ? `Assumed footprint clearance: ${e.metrics.min_sampled_clearance_m.toFixed(2)} m.` : "Footprint clearance unavailable."} {e.metrics?.sampled_occupancy_pet_s != null ? `Sampled PET: ${e.metrics.sampled_occupancy_pet_s.toFixed(2)} s.` : "Sampled PET unavailable."}</p>

              </li>
            ))}
          </ul>
        )}

        {tab === "summary" && (
          <div className="summary">
            <h3>Road users</h3>
            <p>{Object.entries(analysis.counts).map(([c, n]) => `${n} ${c}`).join(", ") || "None"}</p>
            <h3>Object speeds</h3>
            {Object.keys(analysis.speeds).length === 0
              ? <p className="muted">{analysis.calibrated ? "No object was tracked long enough inside the calibrated area." : "Calibrate the road to measure speed."}</p>
              : <table><thead><tr><th>Object</th><th>Median</th><th>Fit windows</th></tr></thead>
                  <tbody>{Object.entries(analysis.speeds).map(([id, s]) => (
                    <tr key={id}><td>#{id}</td><td>{s.median_mph} mph</td><td>{s.source==='reviewed_override'?'Reviewed override':s.samples}</td></tr>))}</tbody></table>}
            <h3>Reviewed interactions</h3>
            <p>{events.length} candidates retained ({analysis.events.filter((e) => e.status === "confirmed").length} confirmed)</p>

          </div>
        )}
      </aside>
    </div>
  );
}
