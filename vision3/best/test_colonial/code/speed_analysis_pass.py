#!/usr/bin/env python3
"""One CPU pass over saved manual trajectories: robust fits, PTS audit, sensitivity, plots."""
import argparse
from collections import defaultdict
import csv
import datetime as dt
import json
from pathlib import Path
import shutil
import subprocess
import numpy as np
from scipy.stats import theilslopes
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

MPH = 2.2369362921


def table(path, rows):
    if not rows:return
    with path.open('w', newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)


def ground(H, pixels):
    q=np.column_stack([pixels,np.ones(len(pixels))])@H.T
    if not np.isfinite(q).all() or np.min(abs(q[:,2]))<1e-7 or np.any(q[:,2]*q[0,2]<=0):
        raise ValueError('unstable_projection_or_horizon_crossing')
    return q[:,:2]/q[:,2,None]


def robust_fit(t, xy):
    """Huber IRLS trajectory regression in actual elapsed time, not point index."""
    t=np.asarray(t,float);xy=np.asarray(xy,float)
    if len(t)<3 or not np.isfinite(t).all() or not np.isfinite(xy).all():raise ValueError('insufficient_or_nonfinite_points')
    if np.any(np.diff(t)<=0):raise ValueError('nonincreasing_times')
    span=np.ptp(t)
    if span<1.5:raise ValueError('span_below_1.5_seconds')
    if np.max(np.diff(t))>2:raise ValueError('gap_above_2_seconds')
    z=(t-t[0])/span
    degree=1 if len(t)<6 else 2
    A=np.vander(z,degree+1,increasing=True);weights=np.ones(len(t))
    for _ in range(30):
        coef=np.linalg.lstsq(A*np.sqrt(weights[:,None]),xy*np.sqrt(weights[:,None]),rcond=None)[0]
        residual=np.linalg.norm(xy-A@coef,axis=1)
        scale=max(float(np.median(residual))/.67449,1e-6)
        new=np.minimum(1,1.345*scale/np.maximum(residual,1e-12))
        if np.max(abs(new-weights))<1e-5:break
        weights=new
    grid=np.linspace(0,1,101);curve=np.vander(grid,degree+1,increasing=True)@coef
    lengths=np.r_[0,np.cumsum(np.linalg.norm(np.diff(curve,axis=0),axis=1))]
    s=np.interp(z,grid,lengths)
    speed=float(theilslopes(s,t)[0])*MPH
    chord=float(np.linalg.norm(xy[-1]-xy[0])/span)*MPH
    old=float(np.linalg.norm(np.diff(xy,axis=0),axis=1).sum()/span)*MPH
    return dict(speed=speed,chord=chord,old=old,curve=curve,s=s,weights=weights,degree=degree)


def timestamp_audit(video, out):
    exe=shutil.which('ffprobe')
    if not exe:raise RuntimeError('ffprobe_missing: load ffmpeg module')
    r=subprocess.run([exe,'-v','error','-select_streams','v:0','-show_packets','-show_streams',
                      '-show_entries','packet=pts_time,duration_time:stream=avg_frame_rate,r_frame_rate,time_base',
                      '-of','json',str(video)],capture_output=True,text=True,check=True,timeout=180)
    data=json.loads(r.stdout)
    pts=np.array(sorted(float(p['pts_time']) for p in data.get('packets',[]) if p.get('pts_time') not in (None,'N/A')))
    if len(pts)<3:raise ValueError('insufficient_packet_PTS')
    delta=np.diff(pts);positive=delta[delta>0]
    if not len(positive):raise ValueError('no_positive_PTS_steps')
    median=float(np.median(positive));fraction=float(np.mean(abs(delta-median)>max(.0001,median*.01)))
    fps=data['streams'][0].get('avg_frame_rate','0/0');a,b=map(float,fps.split('/'));nominal=a/b if b and a else None
    elapsed=pts-pts[0]
    drift=float(np.max(abs(elapsed-np.arange(len(pts))/nominal))) if nominal else ''
    table(out,[dict(packet=i,pts_seconds=p,elapsed_seconds=p-pts[0]) for i,p in enumerate(pts)])
    return dict(status='AUDITED_PACKET_PTS',packets=len(pts),median_step_seconds=median,
                irregular_step_fraction=fraction,duplicate_pts=int(np.sum(delta==0)),
                nominal_fps=nominal,max_index_over_avgfps_difference_seconds=drift,
                note='Sorted presentation packet timestamps; packet index is not guaranteed decoded frame index. Manual browser seconds retained; no automatic retiming.')


def run(a):
    manual=a.manual;pack=json.loads((manual/'analysis/review_inputs.json').read_text())
    entries={e['key']:e for e in pack['entries']}
    normalized=json.loads((manual/'analysis/normalized_observations.json').read_text())
    exported=json.loads((manual/'analysis/final_batch_export.json').read_text())
    calibrations={v['camera']:v['calibration'] for v in exported['calibrations'].values()}
    groups=defaultdict(list)
    for p in normalized['observations']:groups[p['encounter_id']].append(p)
    references=list(csv.DictReader((manual/'analysis/site_summary.csv').open()))
    refs={r['location']:r for r in references}
    a.out.mkdir(parents=True,exist_ok=False);(a.out/'plots').mkdir();(a.out/'timestamps').mkdir()
    config=dict(seed=a.seed,simulations=a.simulations,click_sigma_px=a.click_sigma_px,
                scale_uniform_fraction=a.scale_fraction,min_span_seconds=1.5,max_gap_seconds=2,
                scale_policy='One multiplicative draw per camera per simulation, shared by its cyclists; illustrative assumptions, not measured errors.',
                timing_policy='Manual browser seconds retained. Packet PTS audited separately; no playback factor applied.',
                fit_policy='Time-aware Huber IRLS, degree 1 below 6 points else 2; Theil-Sen slope of fitted arc length. Engineering defaults, not validated optimal settings.')
    (a.out/'config.json').write_text(json.dumps(config,indent=2))
    rng=np.random.default_rng(a.seed)
    scale_draws={camera:rng.uniform(1-a.scale_fraction,1+a.scale_fraction,a.simulations) for camera in calibrations}
    audits={};rows=[];draws_by_site=defaultdict(list)
    for encounter,points in sorted(groups.items()):
        points=sorted(points,key=lambda p:p['seconds']);entry=entries[points[0]['key']];camera=points[0]['camera'];loc=entry['source']['reference_location']
        if entry['key'] not in audits:
            try:audits[entry['key']]=timestamp_audit(a.videos/entry['video'],a.out/'timestamps'/f'{entry["key"]}.csv')
            except Exception as error:audits[entry['key']]=dict(status='UNAVAILABLE',error=str(error))
            (a.out/'timestamp_audit.json').write_text(json.dumps(audits,indent=2))
        row=dict(encounter_id=encounter,location=loc,camera=camera,clip=entry['video'],
                 start=points[0]['recording_time'],end=points[-1]['recording_time'],points=len(points),
                 old_path_mph='',endpoint_mph='',robust_mph='',sensitivity_p05_mph='',sensitivity_p95_mph='',
                 valid_simulations=0,downweighted_points=0,status='',flags='',timestamp_status=audits[entry['key']]['status'])
        try:
            cal=calibrations[camera]
            if not cal.get('geometry_check_passed'):raise ValueError('calibration_geometry_not_passed')
            H=np.asarray(cal['H'],float)
            t=np.array([p['seconds'] for p in points]);px=np.array([[p['x'],p['y']] for p in points],float)
            # Exact duplicate timestamps are allowed only with identical positions.
            keep=np.r_[True,np.diff(t)>0]
            for i in np.flatnonzero(~keep):
                if not np.array_equal(px[i],px[i-1]):raise ValueError('conflicting_duplicate_timestamp')
            t=t[keep];px=px[keep];xy=ground(H,px);fit=robust_fit(t,xy)
            values=np.full(a.simulations,np.nan)
            for j in range(a.simulations):
                try:values[j]=robust_fit(t,ground(H,px+rng.normal(0,a.click_sigma_px,px.shape)))['speed']*scale_draws[camera][j]
                except ValueError:pass
            valid=np.isfinite(values)
            if valid.sum()<.9*a.simulations:raise ValueError('too_many_invalid_sensitivity_draws')
            row.update(old_path_mph=fit['old'],endpoint_mph=fit['chord'],robust_mph=fit['speed'],
                       sensitivity_p05_mph=float(np.nanpercentile(values,5)),sensitivity_p95_mph=float(np.nanpercentile(values,95)),
                       valid_simulations=int(valid.sum()),downweighted_points=int(np.sum(fit['weights']<.5)),status='EXPLORATORY_SHARED_UNVALIDATED_SCALE')
            flags=['scale_not_independently_validated']
            if audits[entry['key']]['status']=='UNAVAILABLE':flags.append('timestamp_audit_unavailable')
            elif audits[entry['key']]['irregular_step_fraction']>.01:flags.append('irregular_PTS_review')
            if fit['chord']>0 and fit['old']/fit['chord']>1.2:flags.append('curvature_or_click_jitter')
            row['flags']=';'.join(flags);draws_by_site[loc].append(values)
            fig,axes=plt.subplots(1,2,figsize=(10,4))
            axes[0].scatter(xy[:,0],xy[:,1],c=fit['weights'],vmin=0,vmax=1)
            axes[0].plot(fit['curve'][:,0],fit['curve'][:,1]);axes[0].set(xlabel='Ground X (m, assumed scale)',ylabel='Ground Y (m, assumed scale)');axes[0].axis('equal')
            axes[1].plot(t-t[0],fit['s'],'o-');axes[1].set(xlabel='Elapsed browser video seconds',ylabel='Fitted path distance (m)')
            fig.suptitle(f'{loc}: {fit["speed"]:.2f} mph | sensitivity {row["sensitivity_p05_mph"]:.2f}–{row["sensitivity_p95_mph"]:.2f}\n{row["start"]} to {row["end"]}',fontsize=10)
            fig.tight_layout();fig.savefig(a.out/'plots'/f'{encounter}.png',dpi=120);plt.close(fig)
        except Exception as error:row['status']='REJECTED';row['flags']=str(error)
        rows.append(row);table(a.out/'cyclists.csv',rows)
        (a.out/'status.json').write_text(json.dumps(dict(completed=len(rows),total=len(groups),state='RUNNING')))
        print(f'{len(rows)}/{len(groups)} {loc}: {row["status"]}',flush=True)
    sites=[]
    for loc in sorted({r['location'] for r in rows}):
        rr=[r for r in rows if r['location']==loc];ok=[r for r in rr if r['robust_mph']!=''];ref=refs[loc]
        means=np.nanmean(draws_by_site[loc],axis=0) if ok else None
        sites.append(dict(location=loc,annotated=len(rr),usable=len(ok),study_reference_mean_mph=ref['study_speed_mean_mph'],
                          prior_HiPerGator_mean_mph=ref['automatic_mean_mph'],old_manual_mean_mph=np.mean([r['old_path_mph'] for r in ok]) if ok else '',
                          endpoint_mean_mph=np.mean([r['endpoint_mph'] for r in ok]) if ok else '',robust_mean_mph=np.mean([r['robust_mph'] for r in ok]) if ok else '',
                          sensitivity_p05_mean_mph=np.nanpercentile(means,5) if ok else '',sensitivity_p95_mean_mph=np.nanpercentile(means,95) if ok else ''))
    table(a.out/'sites.csv',sites)
    def fmt(x):return f'{float(x):.2f}' if x!='' else 'Unavailable'
    lines=['# Bicycle speed analysis pass','','All speeds remain estimates using the existing learned camera calibration. No scale was fitted to study means. Sensitivity bounds use assumed errors; they are not verified accuracy intervals. Prior HiPerGator coverage/people may differ; it is context, not a paired comparison.','','| Location | Usable / annotated | Study reference mph | Prior HiPerGator mph | Old manual mph | Endpoint mph | Robust mph | Sensitivity range mph |','|---|---:|---:|---:|---:|---:|---:|---|']
    for s in sites:lines.append(f'| {s["location"]} | {s["usable"]}/{s["annotated"]} | {fmt(s["study_reference_mean_mph"])} | {fmt(s["prior_HiPerGator_mean_mph"])} | {fmt(s["old_manual_mean_mph"])} | {fmt(s["endpoint_mean_mph"])} | {fmt(s["robust_mean_mph"])} | {fmt(s["sensitivity_p05_mean_mph"])}–{fmt(s["sensitivity_p95_mean_mph"])} |')
    lines+=['',f'Assumptions: click noise SD {a.click_sigma_px:g} pixels; uniform camera scale ±{100*a.scale_fraction:g}%; {a.simulations} simulations. These are illustrative engineering choices, not measured error bounds. Site ranges average all usable cyclists in each simulation with shared camera scale. They omit unknown geometric distortion, identity errors and sampling uncertainty.','',
            'The three manual estimators use identical points/times and calibration for each usable encounter. Robust fitting reduces sensitivity to some outliers but does not guarantee better accuracy. Endpoint speed can underestimate curved travel. Rejected encounters stay in cyclists.csv with reasons.','',
            f'Timestamp audit: {sum(v["status"]!="UNAVAILABLE" for v in audits.values())}/{len(audits)} review clips audited. This checks the re-encoded review clips, not the original hourly recordings; it cannot rule out timing problems introduced earlier in extraction.','',
            'cyclists.csv contains exact saved recording times (filename-inferred clocks), statuses, flags and per-cyclist estimates. plots/ shows each accepted trajectory and fitted distance over time. timestamp_audit.json and timestamps/ retain packet PTS evidence. Browser annotation seconds remain unchanged; packet index is not assumed to equal decoded frame index. No extra half-speed factor is applied.','',
            '[Robust slope reference](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.theilslopes.html). This is a project-specific estimator, not a paper reproduction.']
    (a.out/'RESULTS.md').write_text('\n'.join(lines)+'\n')
    (a.out/'status.json').write_text(json.dumps(dict(state='COMPLETED',encounters=len(rows),usable=sum(r['robust_mph']!='' for r in rows),timestamp_clips_audited=sum(v['status']!='UNAVAILABLE' for v in audits.values()),timestamp_clips_total=len(audits)),indent=2))


def main():
    repo=Path(__file__).resolve().parents[4];p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manual',type=Path,default=repo/'manual');p.add_argument('--videos',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--simulations',type=int,default=500);p.add_argument('--seed',type=int,default=20261026)
    p.add_argument('--click-sigma-px',type=float,default=3);p.add_argument('--scale-fraction',type=float,default=.15)
    a=p.parse_args()
    if a.simulations<20 or not 0<=a.scale_fraction<1 or a.click_sigma_px<0:p.error('Need >=20 simulations, 0<=scale fraction<1 and nonnegative click sigma')
    run(a)

if __name__=='__main__':main()
