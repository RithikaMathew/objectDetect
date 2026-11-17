"""CycleScope API.  Run:  python -m uvicorn cyclescope.service.main:app --reload --port 8000"""
import csv
import io
import json
import os
import shutil
import subprocess
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal, Optional

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel, Field

from . import repository, media, help as project_help

DATA = Path(os.getenv("DATA_DIR", str(Path(__file__).resolve().parents[1] / "data/jobs")))
DATA.mkdir(parents=True, exist_ok=True)
lock = threading.Lock()
WORKERS = max(1, min(4, int(os.getenv("PROCESSING_WORKERS", "2"))))
workers = ThreadPoolExecutor(max_workers=WORKERS, thread_name_prefix="cyclescope")

def enqueue(jid):
    return workers.submit(process, jid)

app = FastAPI(title="CycleScope")
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
                   allow_methods=["*"], allow_headers=["*"])


# ---------- storage (one folder + state.json per job; swap for a DB in production) ----------
def jdir(jid: str) -> Path:
    if not jid.isalnum() or len(jid) != 10:
        raise HTTPException(404, "Job not found")
    d = DATA / jid
    if not d.is_dir():
        raise HTTPException(404, "Job not found")
    return d


def load(jid: str) -> dict:
    return json.loads((jdir(jid) / "state.json").read_text())


def save(jid: str, state: dict):
    p = DATA / jid / "state.json"
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(state))
    tmp.replace(p)


def refresh(jid: str, state: dict) -> dict:
    """Recompute speeds + near misses from the (possibly corrected) tracks, then persist."""
    state["analysis"] = repository.analyze(state)
    save(jid, state)
    return state


def get_track(state: dict, tid: int) -> dict:
    for t in state["tracks"]:
        if t["id"] == tid:
            return t
    raise HTTPException(404, "Track not found")


# ---------- background processing ----------
def process(jid: str):
    from . import repository as pipeline
    d = DATA / jid
    s = load(jid)
    try:
        s["status"] = "processing"
        save(jid, s)
        raw, out = d / "upload", d / "video.mp4"
        info = s.get('source_media') or media.probe(raw)
        start,end = media.clip_range(info['duration_s'],s.get('clip_start_s',0),s.get('clip_end_s'))
        media.extract(raw,out,start,end)
        clip_clock = None
        if s.get('session_start'):
            clip_clock=(datetime.fromisoformat(s['session_start'])+timedelta(seconds=start)).strftime('%Y-%m-%d %H:%M:%S')
        last = [0.0]

        def progress(p):
            if p - last[0] >= 0.02:
                last[0] = p
                s["progress"] = round(p, 3)
                save(jid, s)

        clipped = start>0 or end<info['duration_s']-.01
        meta, tracks = pipeline.run(str(out if clipped else raw), progress, clip_clock)
        meta.update(source_offset_s=start, selected_duration_s=end-start, source_duration_s=info['duration_s'],
                    clip_camera_clock=clip_clock, clock_source='reviewer_supplied' if clip_clock else 'unknown')
        s.update(meta=meta, tracks=tracks, status="ready", progress=1.0)
        s["analysis"] = repository.analyze(s)
    except Exception as e:  # surface the reason in the UI
        s["status"], s["error"] = "failed", str(e)
    save(jid, s)


# ---------- schemas ----------
class Calibration(BaseModel):
    image_points: list[list[float]] = Field(min_length=4)
    world_points_metres: list[list[float]] = Field(min_length=4)
    regions: list[dict] = Field(default_factory=list)
    measurement_source: str = Field(min_length=1)


class KeyBox(BaseModel):
    frame: int = Field(ge=0)
    box: list[float] = Field(min_length=4, max_length=4)


class NewTrack(KeyBox):
    cls: Literal["cyclist", "person", "car", "truck", "bus", "motorcycle"]


class TrackPatch(BaseModel):
    cls: Optional[Literal["cyclist", "person", "car", "truck", "bus", "motorcycle"]] = None
    deleted: Optional[bool] = None
    suppressed: Optional[bool] = None
    reviewed: Optional[bool] = None






class Regions(BaseModel):
    regions: list[dict]


class SpeedOverride(BaseModel):
    mph: Optional[float] = Field(default=None, ge=0, allow_inf_nan=False)
    reason: str = ""


class EventDecision(BaseModel):
    status: Literal["auto", "confirmed", "rejected"]


class HelpQuestion(BaseModel):
    question: str = Field(min_length=1,max_length=2000)
    job_id: Optional[str] = None


@app.post('/api/help')
def ask_help(body: HelpQuestion):
    return project_help.answer(body.question,load(body.job_id) if body.job_id else None)


@app.get('/api/help/sources/{key}')
def help_source(key: str):
    if key not in project_help.SOURCES:raise HTTPException(404,'Source not found')
    return PlainTextResponse((project_help.ROOT/project_help.SOURCES[key][1]).read_text())


# ---------- routes ----------
@app.get("/api/jobs")
def list_jobs():
    rows = []
    for d in sorted(DATA.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if (d / "state.json").exists():
            s = json.loads((d / "state.json").read_text())
            rows.append({"id": d.name, "name": s.get("name"), "status": s.get("status"), "progress":s.get("progress",0), "clip_start_s":s.get("clip_start_s",0), "clip_end_s":s.get("clip_end_s")})
    return rows




@app.get("/api/config")
def config():
    return {"processing_workers": WORKERS}


@app.get("/api/dashboard")
def dashboard():
    return repository.dashboard()


@app.delete("/api/jobs/{jid}")
def delete_job(jid: str):
    with lock:
        s = load(jid)
        if s['status'] in ('queued', 'processing'):
            raise HTTPException(409, 'Wait for processing to finish before deleting this video')
        shutil.rmtree(jdir(jid))
    return {'id': jid, 'deleted': True}


@app.post("/api/jobs/{jid}/reprocess")
def reprocess(jid: str, bg: BackgroundTasks):
    with lock:
        s = load(jid)
        if s['status'] in ('queued', 'processing'):
            raise HTTPException(409, 'Video is already processing')
        if any(t.get('reviewed') or t.get('source') == 'manual' for t in s['tracks']):
            raise HTTPException(409, 'This video has review edits. Upload a new copy to preserve those edits.')
        # Retain an audit snapshot; analysis is never silently carried across models.
        (jdir(jid) / ('before_reprocess_' + uuid.uuid4().hex + '.json')).write_text(json.dumps(s))
        s.update(status='queued', progress=0, tracks=[], analysis={}, decisions={})
        s.pop('error',None)
        save(jid, s)
    bg.add_task(enqueue, jid)
    return s


@app.post("/api/jobs")
def create_job(bg: BackgroundTasks, file: UploadFile = File(...), session_start: Optional[str] = Form(None),
               clip_start_s: float = Form(0), clip_end_s: Optional[float] = Form(None)):
    if session_start:
        try:
            clock=datetime.fromisoformat(session_start)
            if clock.tzinfo: raise ValueError('Use the camera local clock without a timezone')
        except ValueError: raise HTTPException(422, 'Recording start must be a local ISO date and time')
    jid = uuid.uuid4().hex[:10]
    (DATA / jid).mkdir(parents=True)
    try:
        with open(DATA / jid / "upload", "wb") as f:
            shutil.copyfileobj(file.file, f)
        info=media.probe(DATA / jid / "upload")
        start,end=media.clip_range(info['duration_s'],clip_start_s,clip_end_s)
    except (ValueError, subprocess.CalledProcessError, FileNotFoundError) as exc:
        shutil.rmtree(DATA / jid)
        raise HTTPException(422, 'Cannot prepare video; ffmpeg and ffprobe are required. ' + str(exc))
    save(jid, {"id": jid, "name": file.filename, "status": "queued", "progress": 0.0, "tracks": [],
               "calibration": None, "session_start": session_start, "source_media": info,
               "clock_hint": media.clock_hint(file.filename), "clip_start_s": start, "clip_end_s": end,
               "speed_overrides": {}, "speed_audit": [], "decisions": {}, "analysis": {}, "meta": None})
    bg.add_task(enqueue, jid)
    return {"id": jid, "status": "queued", "clip_start_s": start, "clip_end_s": end}


@app.get("/api/jobs/{jid}")
def get_job(jid: str):
    s = load(jid)
    if s.get('status') == 'ready':
        s['analysis'] = repository.analyze(s)
    return s


@app.get("/api/jobs/{jid}/video")
def get_video(jid: str):
    return FileResponse(jdir(jid) / "video.mp4", media_type="video/mp4")  # Starlette serves Range requests


def validate_regions(regions):
    import cv2
    import numpy as np
    for region in regions:
        points=np.asarray(region.get('points'),dtype=float)
        if not region.get('name') or points.ndim!=2 or points.shape[1]!=2 or len(points)<3 or not np.isfinite(points).all() or abs(cv2.contourArea(points.astype(np.float32)))<1:
            raise ValueError('Each named region needs at least three points forming a valid polygon')


@app.put("/api/jobs/{jid}/regions")
def set_regions(jid: str, body: Regions):
    try: validate_regions(body.regions)
    except (ValueError,TypeError,KeyError) as exc:raise HTTPException(422,str(exc))
    with lock:
        s=load(jid);s['regions']=body.regions
        if s.get('calibration'):s['calibration']['regions']=body.regions
        return refresh(jid,s)


@app.put("/api/jobs/{jid}/calibration")
def set_calibration(jid: str, c: Calibration):
    try:
        repository.homography(c.model_dump())
        for p in c.image_points + c.world_points_metres:
            if len(p) != 2: raise ValueError('Each point needs two coordinates')
        validate_regions(c.regions)
    except (ValueError, TypeError, KeyError) as exc:
        raise HTTPException(422, str(exc))
    with lock:
        s = load(jid)
        s["calibration"] = c.model_dump()
        s["regions"] = c.regions
        return refresh(jid, s)


@app.post("/api/jobs/{jid}/tracks")
def add_track(jid: str, body: NewTrack):
    """Human adds an object the detector missed."""
    with lock:
        s = load(jid)
        if body.frame >= s['meta'].get('frames', float('inf')) or body.box[2] <= body.box[0] or body.box[3] <= body.box[1]:
            raise HTTPException(422, 'Choose a valid frame and a box with positive area')
        tid = max([t["id"] for t in s["tracks"]], default=0) + 1
        keys = {str(body.frame): body.box}
        s["tracks"].append({"id": tid, "cls": body.cls, "orig_cls": None, "source": "manual", "deleted": False,
                            "suppressed": False, "reviewed": True, "conf": 1.0, "keys": keys,
                            "boxes": repository.boxes_from_keys(keys, s["meta"]["fps"])})
        return refresh(jid, s)


@app.post("/api/jobs/{jid}/tracks/{tid}/keyframes")
def add_keyframe(jid: str, tid: int, body: KeyBox):
    with lock:
        s = load(jid)
        t = get_track(s, tid)
        if t["source"] != "manual":
            raise HTTPException(400, "Keyframes can only be added to manual objects")
        t["keys"][str(body.frame)] = body.box
        t["boxes"] = repository.boxes_from_keys(t["keys"], s["meta"]["fps"])
        return refresh(jid, s)


@app.patch("/api/jobs/{jid}/tracks/{tid}")
def patch_track(jid: str, tid: int, body: TrackPatch):
    with lock:
        s = load(jid)
        t = get_track(s, tid)
        for k, v in body.model_dump(exclude_none=True).items():
            t[k] = v
        if body.cls or body.deleted is not None:
            t["reviewed"] = True
        return refresh(jid, s)




@app.put("/api/jobs/{jid}/tracks/{tid}/speed")
def set_speed(jid: str, tid: int, body: SpeedOverride):
    if body.mph is not None and not body.reason.strip():
        raise HTTPException(422, 'Describe the measurement or reason for the reviewed speed')
    with lock:
        s=load(jid)
        if s['status']!='ready': raise HTTPException(409, 'Wait for processing before reviewing speed')
        get_track(s,tid)['reviewed']=True
        overrides=s.setdefault('speed_overrides',{})
        previous=overrides.get(str(tid))
        stamp=datetime.now(timezone.utc).isoformat()
        if body.mph is None: overrides.pop(str(tid),None)
        else: overrides[str(tid)]=dict(mph=body.mph,reason=body.reason.strip(),updated_at=stamp)
        s.setdefault('speed_audit',[]).append(dict(track_id=tid,previous=previous,value=overrides.get(str(tid)),updated_at=stamp))
        return refresh(jid,s)


@app.put("/api/jobs/{jid}/events/{key}")
def set_event(jid: str, key: str, body: EventDecision):
    with lock:
        s = load(jid)
        s["decisions"][key] = body.status
        return refresh(jid, s)


@app.get("/api/jobs/{jid}/export/{fmt}")
def export(jid: str, fmt: Literal["json", "csv"]):
    s = load(jid)
    a = repository.analyze(s)
    if fmt == "json":
        keep = [t for t in s["tracks"] if not t["deleted"] and not t.get("suppressed")]
        return {"video": s["name"], "meta": s["meta"], "calibration": s["calibration"], "regions": s.get("regions", []),
                "tracks": keep, "speeds": a["speeds"], "computed_speeds":a["computed_speeds"],
                "speed_audit":s.get('speed_audit',[]), "clip_range":{k:s.get(k) for k in ('clip_start_s','clip_end_s','session_start')},
                "provenance": a["provenance"],
                "interaction_candidates": a["events"],
                "near_misses": [e for e in a["events"] if e["status"] == "confirmed"]}
    buf = io.StringIO()
    fields = ["type", "object_id", "other_id", "other_class", "time_s", "median_mph", "fit_windows", "speed_source", "computed_mph", "speed_reason",
              "min_center_distance_m", "assumed_footprint_clearance_m", "collision_ttc_s", "sampled_pet_s", "status"]
    w = csv.DictWriter(buf, fieldnames=fields)
    w.writeheader()
    for tid, sp in a["speeds"].items():
        w.writerow(dict(type="speed", object_id=tid, median_mph=sp["median_mph"], fit_windows=sp["samples"], status=sp["status"], speed_source=sp.get("source","computed"), computed_mph=sp.get("computed_mph",sp["median_mph"]), speed_reason=sp.get("reason","")))
    for e in a["events"]:
        m = e["metrics"]
        w.writerow(dict(type="interaction_candidate", object_id=e["cyclist_id"], other_id=e["other_id"],
            other_class=e["other_cls"], time_s=e["time_s"], min_center_distance_m=e["min_dist_m"],
            assumed_footprint_clearance_m=m["min_sampled_clearance_m"], collision_ttc_s=e["min_ttc_s"],
            sampled_pet_s=m["sampled_occupancy_pet_s"], status=e["status"]))
    return PlainTextResponse(buf.getvalue(), media_type="text/csv")
