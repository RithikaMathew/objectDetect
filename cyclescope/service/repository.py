"""Adapters to the repository's scientific code; no duplicate metric formulas."""
import csv
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid
from collections import defaultdict, Counter

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CODE = ROOT / 'vision3/best/test_colonial/code'
sys.path.insert(0, str(CODE))
from metric_trajectory_speed import estimate
from clearance_metrics import prepare, road_axis, pair_metrics


def read(path):
    with Path(path).open() as stream:
        return list(csv.DictReader(stream))


def recording_sessions():
    """Session dates from the saved archive listing; file timestamps are not camera clocks."""
    from inventory_miovision_archive import classify
    groups = {}
    for line in (ROOT / 'data/all_videos.txt').read_text().splitlines():
        at = line.find('MioVision Data/')
        if at < 0: continue
        path = line[at:]
        info = classify(path)
        if not info: continue
        import re
        match = re.search(r'_(20\d{2}-\d{2}-\d{2})_', path)
        if not match: continue
        key = (info['collection'], info['site_folder'], info['device'], match[1])
        group = groups.setdefault(key, dict(collection=key[0], location=key[1], device=key[2], date=key[3], listed_files=0))
        group['listed_files'] += 1
    return sorted(groups.values(), key=lambda r:(r['location'],r['date'],r['device']))


def dashboard():
    source = 'Bike Lane Study Counts/ground_truth_bicycle_counts_v2.csv'
    archive_source = 'reports/cluster_returns/20261028/full_archive_inventory/camera_years_hours.csv'
    manual_cameras = {r['location']:r['camera'] for r in read(ROOT / 'manual/analysis/recording_durations.csv')}
    speed_by_site = {manual_cameras.get(r['location']):r for r in read(ROOT / 'manual/analysis/same_video_comparison.csv')}
    counts = {}
    for row in read(ROOT / source):
        key = row['site'], row['date']
        g = counts.setdefault(key, dict(location=key[0], date=key[1], bicycles=0, missing=0, facilities={}))
        try: count = int(row['count'])
        except (ValueError, TypeError):
            g['missing'] += 1
            continue
        g['bicycles'] += count
        facility = row['facility_type'] or 'unassigned'
        g['facilities'][facility] = g['facilities'].get(facility,0) + count
    rows = []
    by_key = {}
    for i, r in enumerate(read(ROOT / archive_source)):
        years = r['recording_years'].split(';')
        g = dict(id='archive-'+str(i), location=r['site_folder'], year=r['recording_years'], years=years,
                 collection=r['collection'], device=r['device'], videos=int(r['video_files']),
                 hours=float(r['total_playback_hours']) if r['total_playback_hours'] else None,
                 bicycles=None, missing=0, facilities={}, study_sites=[], speeds=[], dates=[],
                 notes=['Counts and speed estimates unavailable for this recording group.'])
        if len(years)>1: g['notes'].append('Hours are combined across the listed years; per-year durations were not returned.')
        rows.append(g);by_key[(r['collection'],r['site_folder'],r['device'])]=g
    from inventory_miovision_archive import classify
    mapped = set()
    for mapping in read(ROOT / 'data/video_site_mapping.csv'):
        key = (mapping['gt_site'],mapping['date'])
        if key not in counts: continue
        info = classify(mapping['example_mp4'])
        if not info: continue
        g = by_key.get((info['collection'],info['site_folder'],info['device']))
        if not g or key[1][:4] not in g['years']: continue
        mapped.add(key);c=counts[key]
        g['bicycles']=(g['bicycles'] or 0)+c['bicycles'];g['missing']+=c['missing']
        g['study_sites'].append(c['location'])
        g.setdefault('count_evidence',[]).append(dict(site=key[0],date=key[1],source=source,mapping='data/video_site_mapping.csv',example_mp4=mapping['example_mp4'],match_score=mapping['match_score'],ambiguous=mapping['ambiguous']))
        for k,v in c['facilities'].items():g['facilities'][k]=g['facilities'].get(k,0)+v
        g['notes']=['Study counts join via saved site/date/device mapping; playback hours cover the full archive group.']
        if any(float(e.get('match_score') or 0)<1 or e.get('ambiguous')!='no' for e in g['count_evidence']):
            g['notes'].append('Camera mapping has a low match score or ambiguity; physical correspondence needs verification.')
        if c['location'] in speed_by_site:
            g['speeds'].append(dict(camera=c['location'],**speed_by_site[c['location']]))
    for key,c in counts.items():
        if key in mapped:continue
        rows.append(dict(**c,id='study-'+str(len(rows)),year=key[1][:4],years=[key[1][:4]],
            collection='Study count only',device='',videos=None,hours=None,study_sites=[c['location']],
            speeds=[dict(camera=c['location'],**speed_by_site[c['location']])] if c['location'] in speed_by_site else [],
            dates=[key[1]],notes=['No reliable archive group match; video hours are left blank.']))
    # Workbook reference rows are a broader dataset than the nine matched-clip comparisons.
    # Keep both scopes visible rather than implying missing comparisons mean no references.
    reference_source='vision3/best/test_colonial/exp_results/speed_reference_readiness_20261023/all_reference_records.csv'
    from speed_site_screen import CANDIDATES
    from statistics import mean
    reference_groups=defaultdict(list)
    for record in read(ROOT/reference_source):reference_groups[record['street']].append(record)
    references=[]
    for street,records in sorted(reference_groups.items()):
        ref=dict(location=street,sample=len(records),mean_mph=mean(float(r['recomputed_mph']) for r in records),
                 source_mean_mph=mean(float(r['source_mph']) for r in records),source=reference_source,
                 candidate_cameras=CANDIDATES.get(street,[]),mapping_status='candidate_alias_not_verified',
                 facilities=sorted({r['facility'] for r in records}))
        references.append(ref)
        matches=[r for r in rows if any(site in ref['candidate_cameras'] for site in r['study_sites'])]
        if not matches:
            rows.append(dict(id='reference-'+street,location=street,year='Unknown',years=[],collection='Speed reference only',
                device='',videos=None,hours=None,bicycles=None,missing=0,facilities={},study_sites=[],speeds=[],dates=[],
                references=[ref],notes=['Workbook reference exists, but no mapped recording is established. No recording year or hours are assigned.']))
        for r in matches:
            r.setdefault('references',[]).append(ref)
            r['notes'].append('Workbook-to-camera association is a candidate alias, not verified person-level validation.')
    for r in rows:r.setdefault('references',[])
    sessions=recording_sessions()
    for session in sessions:
        g=by_key.get((session['collection'],session['location'],session['device']))
        if g and session['date'] not in g['dates']:g['dates'].append(session['date'])
    for g in rows:
        if any(float(e['match_score'] or 0)<1 or e['ambiguous']!='no' for e in g.get('count_evidence',[])):
            g['notes'].append('Study-to-video mapping has a low score or ambiguity; camera correspondence is not verified.')
        if not g['speeds']:g['notes'].append('No same-video speed comparison for this group.')
    import hashlib
    paths=[reference_source,source,archive_source,'data/video_site_mapping.csv','manual/analysis/recording_durations.csv','manual/analysis/same_video_comparison.csv','data/all_videos.txt']
    manifest=[dict(path=path,sha256=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()) for path in paths]
    return dict(rows=sorted(rows,key=lambda r:(r['location'],r['year'],r['device'])), sessions=sessions,source_manifest=manifest,references=references,reference_source=reference_source,
                source=source, archive_source=archive_source,
                speed_source='manual/analysis/same_video_comparison.csv',
                session_source='data/all_videos.txt (partial saved listing; not every audited video is listed)')


def run(video, progress, session_start=None):
    """Run the actual RT-DETR + X-CLIP entrypoint in an isolated job directory."""
    weights = Path(os.environ.get('DETECTOR_WEIGHTS', str(ROOT / 'vision3/runs/detect/finetune_runs/rtdetr_v3/weights/best.pt')))
    if not weights.is_file():
        raise RuntimeError('Fine-tuned RT-DETR weights unavailable. Set DETECTOR_WEIGHTS to your existing best.pt; no substitute model is used.')
    destination = Path(video).parent / 'inference' / uuid.uuid4().hex
    destination.mkdir(parents=True)
    command = [os.environ.get('PIPELINE_PYTHON', sys.executable), str(CODE / 'xclip_overlay_v19_colonial.py'),
               '--video', str(Path(video).resolve()), '--out-root', str(destination.resolve()), '--run', 'cyclescope',
               '--weights', str(weights.resolve()), '--chunk-index', '1', '--export-vehicle-trajectories',
               '--gt-truth-dir', str(destination / 'no_automatic_truth'),
               '--clock-note', 'Uploaded clip; recording clock supplied by reviewer' if session_start else 'Uploaded clip; recording clock unverified; time-of-day rules disabled']
    if session_start: command.extend(['--session-start', session_start])
    # Reuse the saved reference profile rather than reconstructing detector rules.
    from run_batch5 import parse_envv
    # CLI defaults alone are not the active b4 reference configuration.
    profile = dict(parse_envv(CODE / 'run_batch4.sh', '5'))
    switches = {'SAHI': '--sahi', 'STATIC_FILTER': '--static-filter', 'SHORT_RULE': '--short-rule',
                'SHORT_RULE_NIGHT_ONLY': '--short-rule-night-only', 'SPEED_RULE': '--speed-rule', 'SPEED_LATERAL_ONLY': '--speed-lateral-only'}
    values = {'DET_VETO_PCT':'--det-veto-pct', 'DET_PROMOTE_PCT':'--det-promote-pct',
              'NIGHT_START':'--night-start', 'NIGHT_END':'--night-end', 'NIGHT_BIC_MIN_SEC':'--night-bic-min-sec',
              'NIGHT_PED_MIN_SEC':'--night-ped-min-sec', 'BIC_MIN_SEC':'--bic-min-sec', 'PED_MIN_SEC':'--ped-min-sec',
              'DET_CONF':'--det-conf', 'TRACK_THR':'--track-thr', 'LOST_SEC':'--lost-sec',
              'STITCH_SEC':'--stitch-sec', 'STITCH_PX':'--stitch-px', 'WALK_MAX_SPEED':'--walk-max-speed',
              'RIDE_MIN_SPEED':'--ride-min-speed', 'STATIC_MAX_NET_PX':'--static-max-net-px',
              'STATIC_MAX_SPEED':'--static-max-speed'}
    if not session_start:
        for key in ('NIGHT_START', 'NIGHT_END', 'SHORT_RULE', 'SHORT_RULE_NIGHT_ONLY', 'NIGHT_BIC_MIN_SEC', 'NIGHT_PED_MIN_SEC'):
            profile.pop(key, None)
    for key, flag in switches.items():
        if profile.get(key) == '1': command.append(flag)
    for key, flag in values.items():
        if profile.get(key): command.extend([flag, profile[key]])
    (destination / 'command.json').write_text(json.dumps(command, indent=2))
    progress(.05)
    env={**os.environ,'PYTHONUNBUFFERED':'1'}
    with (destination / 'pipeline.log').open('w') as output:
        result = subprocess.run(command, stdout=output, stderr=subprocess.STDOUT, env=env)
    if result.returncode:
        raise RuntimeError('RT-DETR/X-CLIP failed. See inference/pipeline.log: ' + (destination / 'pipeline.log').read_text()[-1500:])
    logs = list(destination.glob('logs/cyclescope/*_run_log.json'))
    if len(logs) != 1: raise RuntimeError('Expected one complete repository pipeline run log')
    log = json.loads(logs[0].read_text())
    return import_run(log)


def import_run(log):
    tracks = []
    labels = {r['track_id']: r for r in read(log['tracks_csv'])}
    for stream, field in [('person', 'trajectories_csv'), ('vehicle', 'vehicle_trajectories_csv')]:
        groups = defaultdict(list)
        for row in read(log[field]): groups[row['track_id']].append(row)
        for original_id, rows in groups.items():
            info = labels.get(original_id, {}) if stream == 'person' else {}
            label = info.get('label') or Counter(r['label'] for r in rows).most_common(1)[0][0]
            cls = {'BICYCLIST': 'cyclist', 'PEDESTRIAN': 'person'}.get(label, label.lower())
            boxes = []
            for r in rows:
                x, y, w, h = [float(r[k]) for k in ('box_cx','box_cy','box_w','box_h')]
                boxes.append([int(r['frame']) - 1, x-w/2, y-h/2, x+w/2, y+h/2])
            tracks.append(dict(id=len(tracks)+1, pipeline_id=original_id, pipeline_stream=stream,
                cls=cls, orig_cls=cls, source='repository', deleted=False, suppressed=False, reviewed=False,
                conf=float(info.get('mean_conf', 0)), boxes=sorted(boxes), observations=rows,
                facility=info.get('facility', 'unassigned'), counted=info.get('counted', rows[0].get('counted'))))
    return dict(fps=log['fps'], width=log['resolution'][0], height=log['resolution'][1],
                pipeline='xclip_overlay_v19_colonial.py', frames=log['frames_processed']), tracks


def boxes_from_keys(keys, fps):
    """Interpolation is for display only; metric estimates use explicit keyframes."""
    keys = sorted((int(f), b) for f, b in keys.items())
    if len(keys) == 1: return [[keys[0][0], *keys[0][1]]]
    out = []
    for (f0, a), (f1, b) in zip(keys, keys[1:]):
        for f in range(f0, f1):
            u = (f-f0)/(f1-f0)
            out.append([f, *[x+(y-x)*u for x, y in zip(a,b)]])
    return out + [[keys[-1][0], *keys[-1][1]]]


def homography(c):
    src = np.asarray(c['image_points'], dtype=np.float64)
    dst = np.asarray(c['world_points_metres'], dtype=np.float64)
    if src.ndim != 2 or src.shape[1] != 2 or src.shape != dst.shape or len(src) < 4 or not np.isfinite(src).all() or not np.isfinite(dst).all():
        raise ValueError('Provide at least four finite paired image and world points')
    H, _ = cv2.findHomography(src, dst, 0)
    if H is None or not np.isfinite(H).all() or np.linalg.matrix_rank(H) < 3:
        raise ValueError('Calibration points are degenerate; choose spread-out measured landmarks')
    return H, cv2.convexHull(src.astype(np.float32))


def _analyze(state):
    active = [t for t in state['tracks'] if not t['deleted'] and not t.get('suppressed')]
    counts = dict(Counter(t['cls'] for t in active))
    out = dict(counts=counts, speeds={}, speed_status={}, events=[], calibrated=False,
               provenance=dict(speed='metric_trajectory_speed.estimate', interactions='clearance_metrics.pair_metrics'),
               note='Interaction candidates require review; no automatic near-miss threshold is adopted.')
    c = state.get('calibration')
    regions=state.get('regions', (c or {}).get('regions',[]))
    facilities={}
    for track in active:
        pixels=[(float(r['foot_x']),float(r['foot_y'])) for r in track.get('observations',[]) if not int(r.get('coasted',0))]
        if not pixels:pixels=[((b[1]+b[3])/2,b[4])for b in track.get('boxes',[])]
        hits=[next((z['name'] for z in regions if cv2.pointPolygonTest(np.asarray(z['points'],np.float32),point,False)>=0),'unassigned') for point in pixels]
        facilities[str(track['id'])]=Counter(hits).most_common(1)[0][0] if hits else track.get('facility','unassigned')
    out['facilities']=facilities
    if not c or not c.get('world_points_metres'): return out
    H, hull = homography(c)
    out['calibrated'] = True
    fps = state['meta']['fps']
    rows = []
    for track in active:
        tid = str(track['id'])
        label = {'cyclist':'BICYCLIST','person':'PEDESTRIAN'}.get(track['cls'], track['cls'])
        # Old standalone-model results have no scientific observation provenance.
        observed = track.get('observations', [])
        if track['source'] == 'manual':
            observed = [dict(frame=int(f)+1, foot_x=(b[0]+b[2])/2, foot_y=b[3],
                             box_w=b[2]-b[0], box_h=b[3]-b[1], coasted=0) for f,b in track['keys'].items()]
        samples = [{**r, 'track_id':tid, 'label':label} for r in observed]
        regions = state.get('regions', c.get('regions', []))
        for r in samples:
            point = float(r['foot_x']), float(r['foot_y'])
            r['facility'] = next((z['name'] for z in regions if cv2.pointPolygonTest(np.asarray(z['points'], np.float32), point, False)>=0), 'unassigned')
        rows.extend(samples)
        speed = estimate(samples, fps, H, hull)
        out['speed_status'][tid] = speed['status'] if samples else 'No repository observations; reprocess this legacy video'
        if speed['speed_mph'] != '':
            out['speeds'][tid] = {**speed, 'median_mph':speed['speed_mph'], 'samples':speed['windows']}
    facilities = {str(t['id']): {'facility':t.get('facility','unassigned')} for t in active}
    for tid in facilities:
        hit = [r.get('facility','unassigned') for r in rows if r['track_id']==tid]
        if hit: facilities[tid]['facility'] = Counter(hit).most_common(1)[0][0]
    out['facilities'] = {tid:r['facility'] for tid,r in facilities.items()}
    paths = prepare(rows, H, hull, fps, facilities)
    try: axis = road_axis(paths)
    except ValueError as exc:
        out['interaction_status'] = str(exc)
        return out
    for (kind, tid), subject in paths.items():
        if kind not in ('cyclist','pedestrian'): continue
        for (other, oid), vehicle in paths.items():
            if other not in ('car','bus','truck','vehicle','other_vehicle'): continue
            metric = pair_metrics(subject, vehicle, other, axis, H, subject_kind=kind)
            if metric is None: continue
            frame = min(metric['samples'], key=lambda r:r['center_distance_m'])['frame'] - 1
            key = f'{tid}-{oid}'
            out['events'].append(dict(key=key, cyclist_id=int(tid), subject_cls='person' if kind=='pedestrian' else kind,
                other_id=int(oid), other_cls=other, frame=frame, time_s=round(frame/fps,2),
                min_dist_m=round(metric['min_center_distance_m'],3), min_ttc_s=metric['min_collision_ttc_s'],
                severity='unclassified candidate', status=state.get('decisions',{}).get(key,'auto'),
                metrics={k:v for k,v in metric.items() if k!='samples'}))
    return out


def analyze(state):
    """Preserve computed evidence; reviewed values affect displayed speeds only."""
    import copy
    out=_analyze(state)
    out['computed_speeds']=copy.deepcopy(out['speeds'])
    active={str(t['id']) for t in state['tracks'] if not t.get('deleted') and not t.get('suppressed')}
    for tid,entry in state.get('speed_overrides',{}).items():
        if tid not in active:continue
        computed=out['computed_speeds'].get(tid,{}).get('median_mph')
        out['speeds'][tid]=dict(median_mph=entry['mph'],samples=None,source='reviewed_override',
            reason=entry['reason'],computed_mph=computed,status='reviewed_override_not_trajectory_measurement')
        out['speed_status'][tid]='Reviewed speed override; trajectory-based interaction metrics remain unchanged'
    return out
