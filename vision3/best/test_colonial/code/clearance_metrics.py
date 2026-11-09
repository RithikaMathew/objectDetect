"""Exploratory fixed-camera interaction metrics; no verified near-miss labels.

All metric footprints are assumed rectangles centered on projected bottom-center
contacts. They are dimension-model estimates, not recovered 3-D object surfaces.
"""
from collections import defaultdict
import numpy as np
import cv2


def project(H, xy):
    xy = np.asarray(xy, dtype=float)
    q = np.column_stack((xy, np.ones(len(xy)))) @ np.asarray(H).T
    if not np.isfinite(q).all() or (np.abs(q[:, 2]) < 1e-8).any():
        raise ValueError('Invalid projection')
    return q[:, :2] / q[:, 2:]


def prepare(rows, H, hull, fps, labels=None):
    """Keep observed samples only; frame IDs are 1-based in the existing pipeline."""
    by = defaultdict(list)
    for r in rows:
        if int(r.get('coasted', 0)):
            continue
        tid = str(r['track_id'])
        info = (labels or {}).get(tid, {})
        label = r.get('label', '').upper()
        kind = ('cyclist' if label == 'BICYCLIST' else
                label.lower() if label.lower() in ('car', 'bus', 'truck', 'vehicle', 'other_vehicle') else None)
        # Retain detector-backed candidates rejected by count/classification rules,
        # but never silently call them confirmed cyclists.
        if kind is None and info.get('det_label', '').lower() == 'cyclist':
            kind = 'cyclist'
        if kind is None:
            continue
        pixel = np.array([float(r['foot_x']), float(r['foot_y'])])
        world = project(H, [pixel])[0]
        inside = cv2.pointPolygonTest(np.asarray(hull, np.float32).reshape(-1, 1, 2), tuple(pixel), False) >= 0
        by[(kind, tid)].append(dict(frame=int(r['frame']), t=(int(r['frame'])-1)/fps,
            pixel=pixel, xy=world, inside=inside, box_w=float(r['box_w']), box_h=float(r['box_h']),
            facility=info.get('facility', 'unassigned'), counted=info.get('counted', r.get('counted', '')),
            identity_status='classifier_cyclist_candidate' if label == 'BICYCLIST' else 'detector_candidate_requires_review'))
    for key, samples in by.items():
        samples.sort(key=lambda r: r['frame'])
        if len({r['frame'] for r in samples}) != len(samples):
            raise ValueError('Duplicate observed track/frame')
    return dict(by)


def road_axis(paths):
    """Dominant vehicle displacement axis; never fit it to reference speeds."""
    vectors = []
    for (kind, _), rr in paths.items():
        if kind == 'cyclist' or len(rr) < 5:
            continue
        v = rr[-1]['xy']-rr[0]['xy']
        n = np.linalg.norm(v)
        if n > 2:
            vectors.append(v/n)
    if len(vectors) < 2:
        raise ValueError('Need at least two moving vehicle tracks to estimate road direction')
    _, vec = np.linalg.eigh(np.asarray(vectors).T @ np.asarray(vectors))
    axis = vec[:, -1]
    if axis[0] < 0:
        axis = -axis
    return axis


def local_motion(samples, window, scale=1.0):
    """Local line fits, split at >0.20s observation gaps; no coast interpolation."""
    t = np.array([r['t'] for r in samples])
    xy = np.array([r['xy'] for r in samples])*scale
    cuts = np.r_[0, np.flatnonzero(np.diff(t) > .20)+1, len(t)]
    out = {}
    for start, stop in zip(cuts[:-1], cuts[1:]):
        for i in range(start, stop):
            mask = np.flatnonzero(np.abs(t[start:stop]-t[i]) <= window/2)+start
            if len(mask) < 3 or np.ptp(t[mask]) < .10:
                continue
            fit = np.linalg.lstsq(np.column_stack((np.ones(len(mask)), t[mask]-t[i])), xy[mask], rcond=None)[0]
            out[samples[i]['frame']] = {**samples[i], 'xy': fit[0], 'velocity': fit[1]}
    return out


def kalman_motion(samples, scale=1., rts=False, position_sigma=.25, acceleration_sigma=2.):
    """CV Kalman filter and optional offline Rauch–Tung–Striebel backward pass.

    State is [x,y,vx,vy]. Noise values are engineering assumptions in learned
    metric coordinates, not fitted uncertainties. Restart across >0.20s gaps;
    output only actual observations after a 0.10s/3-observation warmup.
    """
    if position_sigma <= 0 or acceleration_sigma <= 0 or scale <= 0:
        raise ValueError('Positive noise scales and metric scale required')
    if not samples:return {}
    times=np.array([r['t'] for r in samples],float)
    if not np.isfinite(times).all() or (np.diff(times)<=0).any():
        raise ValueError('Filter timestamps must be finite and strictly increasing')
    points=np.array([r['xy'] for r in samples],float)*scale
    if not np.isfinite(points).all():raise ValueError('Nonfinite filter observation')
    cuts=np.r_[0,np.flatnonzero(np.diff(times)>.20)+1,len(times)]
    observe=np.array([[1.,0.,0.,0.],[0.,1.,0.,0.]])
    noise=np.eye(2)*(position_sigma*scale)**2
    identity=np.eye(4);out={}
    for start,stop in zip(cuts[:-1],cuts[1:]):
        if stop-start<3 or times[stop-1]-times[start]<.10:continue
        filtered=[];covariances=[];predicted=[];predicted_cov=[];transitions=[]
        state=np.r_[points[start],0.,0.]
        covariance=np.diag([(position_sigma*scale)**2]*2+[(5.*scale)**2]*2)
        for i in range(start,stop):
            step=times[i]-times[i-1] if i>start else 0.
            transition=identity.copy();transition[0,2]=step;transition[1,3]=step
            forcing=np.vstack((np.eye(2)*step**2/2,np.eye(2)*step))
            prior=transition@state
            prior_cov=transition@covariance@transition.T+forcing@forcing.T*(acceleration_sigma*scale)**2
            innovation_cov=observe@prior_cov@observe.T+noise
            gain=np.linalg.solve(innovation_cov,(prior_cov@observe.T).T).T
            state=prior+gain@(points[i]-observe@prior)
            remainder=identity-gain@observe
            covariance=remainder@prior_cov@remainder.T+gain@noise@gain.T
            filtered.append(state.copy());covariances.append(covariance.copy())
            predicted.append(prior);predicted_cov.append(prior_cov);transitions.append(transition)
        estimates=np.array(filtered)
        if rts:
            smooth_cov=covariances[-1].copy()
            for k in range(len(filtered)-2,-1,-1):
                gain=np.linalg.solve(predicted_cov[k+1],(covariances[k]@transitions[k+1].T).T).T
                estimates[k]=filtered[k]+gain@(estimates[k+1]-predicted[k+1])
                smooth_cov=covariances[k]+gain@(smooth_cov-predicted_cov[k+1])@gain.T
        for k,i in enumerate(range(start,stop)):
            if k<2 or times[i]-times[start]<.10:continue
            out[samples[i]['frame']]={**samples[i],'xy':estimates[k,:2],
                                      'velocity':estimates[k,2:]}
    return out


def collision_ttc(relative, velocity, half_extents, horizon=5.):
    """Continuous swept axis-aligned rectangle TTC in road coordinates.

    Constant velocity/orientation; both axes must overlap at the SAME future time.
    A converging but laterally separated parallel pass has no collision TTC.
    """
    enter, leave = 0., horizon
    for p, v, h in zip(relative, velocity, half_extents):
        if abs(v) < 1e-9:
            if abs(p) > h:
                return None
            continue
        a, b = sorted(((-h-p)/v, (h-p)/v))
        enter, leave = max(enter, a), min(leave, b)
        if enter > leave:
            return None
    return float(enter) if leave >= 0 and enter <= horizon else None


def closest_approach(relative, velocity, horizon=5.):
    vv = float(np.dot(velocity, velocity))
    tau = max(0., min(horizon, -float(np.dot(relative, velocity))/vv)) if vv > 1e-9 else 0.
    return tau, float(np.linalg.norm(relative + velocity*tau))


def pet_cells(cyclist, vehicle, dimensions, basis, cell=.5, max_gap=.20):
    """Sampled occupancy PET on shared metric cells, not nearest-time matching.

    Rasterize road-aligned assumed footprints; merge consecutive occupancy per
    track/cell. PET is the smallest later entry minus earlier exit in shared cells.
    Return 0 for sampled simultaneous occupancy; spatial/temporal quantization is
    explicitly retained in outputs. No occupancy interval spans missing frames.
    """
    def occupancy(samples, length, width):
        cells = defaultdict(list)
        for r in samples.values():
            s, l = r['xy'] @ basis
            low = np.floor((np.array([s, l])-np.array([length, width])/2)/cell).astype(int)
            high = np.floor((np.array([s, l])+np.array([length, width])/2)/cell).astype(int)
            if np.prod(high-low+1) > 2000:
                raise ValueError('Implausibly large PET footprint grid')
            for i in range(low[0], high[0]+1):
                for j in range(low[1], high[1]+1):
                    cells[(i, j)].append(r['t'])
        result = {}
        for k, times in cells.items():
            times.sort(); spans = [[times[0], times[0]]]
            for t in times[1:]:
                if t-spans[-1][1] > max_gap:
                    spans.append([t, t])
                else:
                    spans[-1][1] = t
            result[k] = spans
        return result
    c = occupancy(cyclist, *dimensions[0]); v = occupancy(vehicle, *dimensions[1])
    best = None
    for key in c.keys() & v.keys():
        for a, b in c[key]:
            for x, y in v[key]:
                gap = max(0., x-b, a-y)
                if best is None or gap < best:
                    best = gap
    return best


def dimensions(kind, cyclist_width):
    # Assumptions for sensitivity, not measured vehicle dimensions.
    if kind == 'cyclist': return (1.8, cyclist_width)
    if kind == 'bus': return (12., 2.5)
    if kind == 'truck': return (8., 2.5)
    return (4.5, 1.8)


def pair_metrics(c, v, vehicle_kind, axis, H, width=.8, window=.5, scale=1., strict=True, motion='local'):
    if motion=='local':
        cm, vm = local_motion(c, window, scale), local_motion(v, window, scale)
    elif motion in ('kalman','rts'):
        cm, vm = [kalman_motion(rr,scale,rts=motion=='rts') for rr in (c,v)]
    else:raise ValueError('Unknown trajectory smoothing method: '+motion)
    if strict:
        cm = {k:r for k,r in cm.items() if r['inside']}
        vm = {k:r for k,r in vm.items() if r['inside']}
    common = sorted(cm.keys() & vm.keys())
    if len(common) < 3:
        return None
    basis = np.column_stack((axis, [-axis[1], axis[0]]))
    cd, vd = dimensions('cyclist', width), dimensions(vehicle_kind, width)
    half = (np.array(cd)+vd)/2
    samples = []
    for frame in common:
        a, b = cm[frame], vm[frame]
        rel = (b['xy']-a['xy']) @ basis
        vel = (b['velocity']-a['velocity']) @ basis
        cv, vv = a['velocity'] @ basis, b['velocity'] @ basis
        alongside = abs(rel[0]) <= half[0]
        gap = max(0., abs(rel[1])-half[1]) if alongside else None
        ttc = collision_ttc(rel, vel, half)
        tau, dca = closest_approach(rel, vel)
        # Image proxy: project the bottom box edges. This is NOT a footprint.
        edges = []
        for r in (a,b):
            x,y = r['pixel']; w = r['box_w']
            edges.append(project(H, [[x-w/2,y],[x+w/2,y]])*scale @ basis)
        intervals = [(float(e[:,1].min()),float(e[:,1].max())) for e in edges]
        edge_proxy = max(0., intervals[0][0]-intervals[1][1], intervals[1][0]-intervals[0][1]) if alongside else None
        samples.append(dict(frame=frame,t=a['t'],s_relative=rel[0],l_relative=rel[1],
            center_distance_m=float(np.linalg.norm(rel)),clearance_m=gap,
            cyclist_x_m=float(a['xy'][0]),cyclist_y_m=float(a['xy'][1]),
            vehicle_x_m=float(b['xy'][0]),vehicle_y_m=float(b['xy'][1]),
            footprint_distance_m=float(np.linalg.norm(np.maximum(np.abs(rel)-half,0.))),
            projected_box_edge_proxy_m=edge_proxy,ttc_s=ttc,time_to_closest_s=tau,
            closest_center_distance_m=dca,cyclist_speed_mps=float(np.linalg.norm(cv)),
            vehicle_speed_mps=float(np.linalg.norm(vv)),same_direction=bool(cv[0]*vv[0]>0 and abs(cv[0])>.5 and abs(vv[0])>.5)))
    # Broad candidate cutoff saves PET work without using a near-miss threshold.
    if min(r['center_distance_m'] for r in samples) > 20:
        return None
    alongside = [r for r in samples if r['clearance_m'] is not None]
    best = min(alongside,key=lambda r:r['clearance_m']) if alongside else None
    ttcs = [r['ttc_s'] for r in samples if r['ttc_s'] is not None]
    pet = pet_cells(cm, vm, (cd,vd), basis)
    # Only call an observed overtake candidate if relative ordering reverses in
    # cyclist travel direction, with same-direction samples around the crossing.
    shared_same = [r for r in samples if r['same_direction']]
    sign = np.sign(np.median([cm[r['frame']]['velocity'] @ axis for r in shared_same])) if shared_same else 0
    # Require a continuous observation span for a before/after claim.
    runs = []; current = []
    for r in shared_same:
        if current and r['t']-current[-1]['t']>.20:
            runs.append(current);current=[]
        current.append(r)
    if current:runs.append(current)
    overtake = any(rr[0]['s_relative']*sign < -half[0] and rr[-1]['s_relative']*sign > half[0] for rr in runs)
    return dict(min_center_distance_m=min(r['center_distance_m'] for r in samples),
        min_footprint_distance_m=min(r['footprint_distance_m'] for r in samples),
        min_sampled_clearance_m=best['clearance_m'] if best else None,
        clearance_time_s=best['t'] if best else None,
        min_box_edge_proxy_m=min((r['projected_box_edge_proxy_m'] for r in alongside),default=None),
        min_collision_ttc_s=min(ttcs) if ttcs else None, sampled_occupancy_pet_s=pet,
        min_predicted_center_distance_m=min(r['closest_center_distance_m'] for r in samples),
        alongside_samples=len(alongside), simultaneous_samples=len(samples),
        same_direction_fraction=sum(r['same_direction'] for r in samples)/len(samples),
        observed_overtake_candidate=int(overtake),
        cyclist_speed_at_clearance_mps=best['cyclist_speed_mps'] if best else None,
        vehicle_speed_at_clearance_mps=best['vehicle_speed_mps'] if best else None,
        first_pair_time_s=samples[0]['t'],last_pair_time_s=samples[-1]['t'],
        samples=samples)


def scenarios():
    """One-factor-at-a-time comparisons keep interpretation and CPU cost bounded."""
    baseline=dict(window=.5,width=.8,scale=1.,strict=True,motion='local')
    yield 'baseline',baseline
    for key, values in [('window',(.25,1.)),('width',(.6,1.)),('scale',(.8,1.2)),('strict',(False,))]:
        for value in values:
            yield f'{key}_{value}',{**baseline,key:value}
    for motion in ('kalman','rts'):
        yield motion,{**baseline,'motion':motion}
        yield motion+'_transfer',{**baseline,'motion':motion,'strict':False}
