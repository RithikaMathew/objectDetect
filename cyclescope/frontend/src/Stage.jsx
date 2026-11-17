import { useEffect, useRef, useState } from "react";

/**
 * Video + canvas overlay + frame-accurate controls.
 *  render(ctx, frame, sx, sy)  called every animation frame; sx/sy convert video px -> canvas px
 *  mode "draw": drag to create a box -> onBox([x1,y1,x2,y2], frame)   (video px)
 *  any mode:    click -> onPoint([x,y], frame)                         (video px)
 *  seekTo: {frame, n} object; change it to jump to a frame
 */
export default function Stage({ src, fps, render, mode = "view", onPoint, onBox, seekTo }) {
  const video = useRef(null), canvas = useRef(null), drag = useRef(null), renderRef = useRef(render);
  renderRef.current = render;
  const [frame, setFrame] = useState(0), [playing, setPlaying] = useState(false), [dur, setDur] = useState(0);

  useEffect(() => {
    let raf;
    const tick = () => {
      const v = video.current, c = canvas.current;
      if (v && c && v.videoWidth) {
        const w = v.clientWidth, h = v.clientHeight;
        if (c.width !== w || c.height !== h) { c.width = w; c.height = h; }
        const f = Math.max(0, Math.floor(v.currentTime * fps + 1e-3));
        setFrame((p) => (p === f ? p : f));
        const ctx = c.getContext("2d");
        ctx.clearRect(0, 0, w, h);
        renderRef.current?.(ctx, f, w / v.videoWidth, h / v.videoHeight);
        const d = drag.current;
        if (d) {
          ctx.strokeStyle = "#fff"; ctx.lineWidth = 2; ctx.setLineDash([6, 4]);
          ctx.strokeRect(d.x0, d.y0, d.x1 - d.x0, d.y1 - d.y0); ctx.setLineDash([]);
        }
      }
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [fps]);

  const seek = (f) => { const v = video.current; v.pause(); v.currentTime = Math.max(0, (f + 0.5) / fps); };
  useEffect(() => { if (seekTo && video.current) seek(seekTo.frame); }, [seekTo]);

  const pos = (e) => { const r = canvas.current.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; };
  const toVideo = ([x, y]) => { const v = video.current; return [x * v.videoWidth / v.clientWidth, y * v.videoHeight / v.clientHeight]; };
  const round = (a) => a.map((n) => Math.round(n * 10) / 10);

  const down = (e) => { video.current.pause(); const [x, y] = pos(e); drag.current = { x0: x, y0: y, x1: x, y1: y }; canvas.current.setPointerCapture(e.pointerId); };
  const move = (e) => { if (drag.current) [drag.current.x1, drag.current.y1] = pos(e); };
  const up = () => {
    const d = drag.current; drag.current = null;
    if (!d || Math.hypot(d.x1 - d.x0, d.y1 - d.y0) < 8) return;
    const [ax, ay] = toVideo([Math.min(d.x0, d.x1), Math.min(d.y0, d.y1)]);
    const [bx, by] = toVideo([Math.max(d.x0, d.x1), Math.max(d.y0, d.y1)]);
    onBox?.(round([ax, ay, bx, by]), frame);
  };
  const total = Math.max(1, Math.round(dur * fps));
  const key = (e) => {
    if (e.target.tagName === "SELECT" || e.target.tagName === "INPUT" && e.target.type !== "range") return;
    if (e.key === "ArrowLeft") { e.preventDefault(); seek(frame - 1); }
    if (e.key === "ArrowRight") { e.preventDefault(); seek(frame + 1); }
    if (e.key === " ") { e.preventDefault(); playing ? video.current.pause() : video.current.play(); }
  };

  return (
    <div className="stage" tabIndex={0} onKeyDown={key}>
      <div className="stage-view">
        <div className="wrap">
          <video ref={video} src={src} muted playsInline preload="auto"
                 onLoadedMetadata={(e) => setDur(e.target.duration)}
                 onPlay={() => setPlaying(true)} onPause={() => setPlaying(false)} />
          <canvas ref={canvas} className={mode === "draw" ? "draw" : ""} aria-label="Video overlay"
                  onClick={(e) => { if (mode !== "draw" && video.current?.videoWidth) { video.current.pause(); onPoint?.(toVideo(pos(e)), frame); } }}
                  onPointerDown={mode === "draw" ? down : undefined}
                  onPointerMove={mode === "draw" ? move : undefined}
                  onPointerCancel={() => { drag.current = null; }}
                  onPointerUp={mode === "draw" ? up : undefined} />
        </div>
      </div>
      <div className="controls">
        <button onClick={() => seek(frame - 1)} aria-label="Previous frame">◀</button>
        <button onClick={() => (playing ? video.current.pause() : video.current.play())}>{playing ? "Pause" : "Play"}</button>
        <button onClick={() => seek(frame + 1)} aria-label="Next frame">▶</button>
        <input type="range" min="0" max={total - 1} value={Math.min(frame, total - 1)}
               onChange={(e) => seek(+e.target.value)} aria-label="Timeline" />
        <span className="time">frame {frame} · {(frame / fps).toFixed(2)} s</span>
      </div>
    </div>
  );
}
