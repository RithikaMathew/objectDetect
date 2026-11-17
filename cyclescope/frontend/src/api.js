// Thin client for the FastAPI backend. Every mutation returns the full, recomputed job.
const parse = async (r) => {
  if (!r.ok) {
    const body = await r.json().catch(() => ({}));
    throw new Error(typeof body.detail === "string" ? body.detail : r.statusText);
  }
  return r.json();
};
const send = (method, url, body) =>
  fetch(url, { method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }).then(parse);

export const api = {
  config: () => fetch("/api/config").then(parse),
  setSpeed: (id, tid, body) => send("PUT", `/api/jobs/${id}/tracks/${tid}/speed`, body),
  dashboard: () => fetch('/api/dashboard').then(parse),
  remove: (id) => send('DELETE', `/api/jobs/${id}`),
  reprocess: (id) => send('POST', `/api/jobs/${id}/reprocess`),
  list: () => fetch("/api/jobs").then(parse),
  get: (id) => fetch(`/api/jobs/${id}`).then(parse),
  upload: (file, sessionStart, clip = {}) => {
    const f = new FormData();
    f.append("file", file);
    if (clip.start != null) f.append("clip_start_s", clip.start);
    if (clip.end != null) f.append("clip_end_s", clip.end);
    if (sessionStart) f.append("session_start", sessionStart);
    return fetch("/api/jobs", { method: "POST", body: f }).then(parse);
  },
  videoUrl: (id) => `/api/jobs/${id}/video`,
  exportUrl: (id, fmt) => `/api/jobs/${id}/export/${fmt}`,
  setRegions: (id, regions) => send("PUT", `/api/jobs/${id}/regions`, {regions}),
  setCalibration: (id, body) => send("PUT", `/api/jobs/${id}/calibration`, body),
  addTrack: (id, body) => send("POST", `/api/jobs/${id}/tracks`, body),
  addKeyframe: (id, tid, body) => send("POST", `/api/jobs/${id}/tracks/${tid}/keyframes`, body),
  patchTrack: (id, tid, body) => send("PATCH", `/api/jobs/${id}/tracks/${tid}`, body),
  setEvent: (id, key, status) => send("PUT", `/api/jobs/${id}/events/${encodeURIComponent(key)}`, { status }),
};
