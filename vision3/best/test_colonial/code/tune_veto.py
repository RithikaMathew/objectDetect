#!/usr/bin/env python3
"""Exploratory detector-veto sweep using saved full-system decisions, CPU only.

Never modifies the reference model, configuration, truth or source outputs.
"""
import argparse
import csv
import datetime as dt
import json
import math
from pathlib import Path

from eval_truth import CLIPS, read_truth, read_tracks, match, load_identity_map


def replay(a, stats, track, params, fps, height, threshold):
    """Replay fusion -> motion -> duration/night exception -> fixed quality filters.

    Audit values are rounded exports. Baseline parity is required before tuning.
    """
    c=a['xclip_label']
    if c not in ('BICYCLIST','PEDESTRIAN'):
        raise ValueError('Missing raw X-CLIP label')
    cp=float(a['det_cyclist_pct']);frames=int(stats['frames'])
    spd=float(a['speed_heights_per_s']);span=float(a['speed_span_s'])
    net=float(a['net_px']);night=bool(int(a['night_track']))
    if not all(math.isfinite(v) for v in (cp,spd,span,net)):
        raise ValueError('Non-finite audit evidence')
    if frames>=params['det_fuse_min_frames']:
        if c=='BICYCLIST' and threshold is not None and cp<threshold:
            c='PEDESTRIAN'
        elif c=='PEDESTRIAN' and params.get('det_promote_pct') is not None and cp>=params['det_promote_pct']:
            c='BICYCLIST'
    if params['speed_rule'] and span>=params['speed_min_sec']:
        lateral=not params['speed_lateral_only'] or a['direction'] in ('moving_left','moving_right')
        if lateral:
            if c=='BICYCLIST' and spd<params['walk_max_speed'] and cp<50:
                c='PEDESTRIAN'
            elif c=='PEDESTRIAN' and spd>params['ride_min_speed'] and cp>=50:
                c='BICYCLIST'
    key='bic_min_sec' if c=='BICYCLIST' else 'ped_min_sec'
    minimum=params.get('night_'+key) if night else None
    if minimum is None:
        minimum=params[key]
    duration_ok=frames>=minimum*fps
    short=(params['short_rule'] and (not params['short_rule_night_only'] or night)
           and frames>=params['short_min_sec']*fps and c=='BICYCLIST'
           and cp>=params['short_det_pct'] and float(a['weighted_bicyclist'])>=params['short_wbic'])
    static=(params['static_filter'] and span>=params['static_min_sec']
            and net<params['static_max_net_px'] and spd<params['static_max_speed'])
    quality=(float(stats['mean_conf'])>=params['person_min_conf']
             and float(track['disp_px'])>=params['person_min_disp']
             and float(stats['mean_box_h'])>=params['person_min_h']*height)
    return c,int((duration_ok or short) and not static and quality)


def read_csv(path):
    with path.open() as stream:
        return list(csv.DictReader(stream))


def load_clip(root,run,clip):
    cc=CLIPS[clip];prefix=f'Standard_SCU8OG_2019-07-10_0000.{cc["chunk"]:03d}'
    folder=root/'counts'/run
    log=json.loads((root/'logs'/run/f'{prefix}_run_log.json').read_text())
    audit={r['track_id']:r for r in read_csv(folder/f'{prefix}_rules_audit.csv')}
    # The statistics CSV has a second vehicle table after a blank row.
    stats={}
    for r in read_csv(folder/f'{prefix}_track_stats.csv'):
        if not str(r.get('person_track','')).isdigit():
            break
        stats[r['person_track']]=r
    raw={r['track_id']:r for r in read_csv(folder/f'{prefix}_tracks.csv')}
    tracks=read_tracks(folder/f'{prefix}_tracks.csv',dt.datetime.fromisoformat(cc['start']))
    truth,skipped=read_truth(root/cc['truth'])
    if skipped:
        raise ValueError(f'Incomplete truth: {clip}')
    # Refuse an approximate sweep if exported evidence cannot reproduce the source run.
    for tid,a in audit.items():
        label,counted=replay(a,stats[tid],raw[tid],log['params'],log['fps'],log['resolution'][1],log['params']['det_veto_pct'])
        if (label,counted)!=(a['final_label'],int(a['counted'])):
            raise ValueError(f'Baseline replay mismatch: {clip}/{tid}. Rounded or missing evidence; do not tune from this export.')
    return dict(truth=truth,tracks=tracks,audit=audit,stats=stats,raw=raw,log=log)


def evaluate(data,threshold,identities=None):
    tracks=[]
    for source in data['tracks']:
        t=dict(source);tid=t['id']
        if tid in data['audit']:
            log=data['log']
            label,counted=replay(data['audit'][tid],data['stats'][tid],data['raw'][tid],
                                 log['params'],log['fps'],log['resolution'][1],threshold)
            t.update(lab='cyclist' if label=='BICYCLIST' else 'pedestrian',counted=counted)
        tracks.append(t)
    matches,extras=match(data['truth'],tracks,identities)
    scored=[(p,s,t) for p,s,t in matches if s!='UNVERIFIED']
    summary=dict(correct=sum(s=='FOUND' for p,s,t in scored),total=len(scored),
        wrong_class=sum(s=='WRONG CLASS' for p,s,t in scored),
        rejected=sum(s=='DETECTED BUT NOT COUNTED' for p,s,t in scored),
        missed=sum(s=='MISSED' for p,s,t in scored),unverified=len(matches)-len(scored),
        unmatched_counted=len(extras),cyclist_correct=sum(s=='FOUND' and p['c']=='cyclist' for p,s,t in scored),
        cyclist_total=sum(p['c']=='cyclist' for p,s,t in scored),
        pedestrian_correct=sum(s=='FOUND' and p['c']=='pedestrian' for p,s,t in scored),
        pedestrian_total=sum(p['c']=='pedestrian' for p,s,t in scored))
    details=[dict(truth_id=p['id'],raw_class=p['raw'],status=s,track_id=t['id'] if t else '',
                  label=t['lab'] if t else '',counted=t['counted'] if t else 0) for p,s,t in matches]
    return summary,details


def tag(value):
    return 'off' if value is None else f'{value:g}'


def choose(rows,baseline):
    if not rows or not rows[0]['total']:
        raise ValueError('No evaluated development people; cannot select a threshold')
    # Tie policy fixed before opening checking results. Prefer the current setting on ties.
    return min(rows,key=lambda r:(-r['correct'],r['unmatched_counted'],
                                  r['threshold']!=baseline,
                                  abs(r['threshold']-baseline) if r['threshold'] is not None else math.inf,
                                  r['threshold'] if r['threshold'] is not None else math.inf))['threshold']


def write_csv(path,rows):
    with path.open('w',newline='') as stream:
        w=csv.DictWriter(stream,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def run(args):
    dev=args.development.split(',');check=args.checking.split(',')
    if len(set(dev))!=len(dev) or len(set(check))!=len(check) or set(dev)&set(check):
        raise ValueError('Development/checking clips must be unique and disjoint')
    if not dev or not check or (set(dev)|set(check))-set(CLIPS):
        raise ValueError('Unknown or empty clip split')
    values=[None if x.strip().lower() in ('off','none') else float(x) for x in args.thresholds.split(',')]
    if any(v is not None and (not math.isfinite(v) or not 0<=v<=100) for v in values):
        raise ValueError('Thresholds must be off or finite percentages0–100')
    values=list(dict.fromkeys(values))
    # Load checking evidence only after the selected threshold is frozen below.
    data={clip:load_clip(args.root,args.run,clip) for clip in dev}
    baselines={v['log']['params']['det_veto_pct'] for v in data.values()}
    if len(baselines)!=1:
        raise ValueError('Inconsistent baseline thresholds')
    baseline=baselines.pop()
    if baseline not in values:
        values.append(baseline)
    identity=load_identity_map(args.identity_map) if args.identity_map else None
    def aggregate(clips,threshold,split):
        summaries=[];details=[]
        for clip in clips:
            s,rr=evaluate(data[clip],threshold,identity.get((args.run,clip),{}) if identity is not None else None)
            summaries.append(s)
            details.extend(dict(split=split,threshold=tag(threshold),clip=clip,**r) for r in rr)
        return dict(threshold=threshold,**{k:sum(s[k] for s in summaries) for k in summaries[0]}),details
    sweep=[];details=[]
    for threshold in values:
        s,rr=aggregate(dev,threshold,'development');sweep.append(s);details.extend(rr)
    selected=choose(sweep,baseline)  # Freeze before accessing checking truth or scores.
    for clip in check:
        data[clip]=load_clip(args.root,args.run,clip)
        if data[clip]['log']['params']['det_veto_pct']!=baseline:
            raise ValueError('Checking baseline differs from development')
    checked=[]
    for threshold in dict.fromkeys([baseline,selected]):
        s,rr=aggregate(check,threshold,'checking');checked.append(s);details.extend(rr)
    args.out.mkdir(parents=True,exist_ok=False)
    write_csv(args.out/'development_sweep.csv',[dict(r,threshold=tag(r['threshold'])) for r in sweep])
    write_csv(args.out/'checking.csv',[dict(r,threshold=tag(r['threshold'])) for r in checked])
    write_csv(args.out/'per_person.csv',details)
    summary=dict(run=args.run,baseline_threshold=baseline,selected_threshold=selected,
        development_clips=dev,checking_clips=check,development=sweep,checking=checked,
        baseline_replay_parity=True,identity_policy='approved_only' if identity is not None else 'legacy_time_only',
        source_precision='rounded saved audit exports; original-setting parity required for every scored track',
        independent_validation=False,deployment_changed=False,
        selection_policy='Most correct counted truth people, then fewest unmatched counted tracks, then current threshold, then closest numeric threshold',
        limitations=['All four clips previously inspected; checking is exploratory, not independent validation.',
                     'Detector, SAHI, tracking, stitching and X-CLIP evidence frozen; only final decisions replayed.',
                     'Rounded evidence can change borderline counterfactual decisions; source-setting parity is not a guarantee at other thresholds.',
                     'Unmatched counted tracks are not confirmed false positives; identity/time matching limitations remain.',
                     'Motorcycle grouped with cyclists for compatibility; raw class preserved.'])
    (args.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    lines=['# Full-system veto threshold replay','',f'Baseline: {tag(baseline)}%. Selected using development clips only: **{tag(selected)}** (percent, or off).',
        'No deployed settings changed. No GPU inference. Source-setting labels and counted decisions reproduced for every scored track in all selected clips.',
        '', 'Order: raw weighted X-CLIP → detector veto/promotion → motion rules → class-specific duration and strict night-only cyclist exception → static/quality filters.',
        'Saved detections, SAHI, tracking/stitching and X-CLIP are frozen. This replays final saved decisions, not video inference or intermediate streamed headers.',
        '', '**Exploratory only:** all four clips have already been inspected. The checking split is not an untouched test set. Saved values are rounded; baseline parity is checked, but borderline alternative-threshold decisions can still be approximate.',
        'Identity policy: '+summary['identity_policy']+'. Motorcycle remains in the scored cyclist group; raw class is retained.',
        '', 'Development clips: '+', '.join(dev)+'. Selection: '+summary['selection_policy']+'.',
        '', '| Veto % | Correct counted people | Wrong class | Rejected | Missed | Unmatched counted |', '|---|---:|---:|---:|---:|---:|']
    for r in sweep:
        lines.append(f"| {tag(r['threshold'])} | {r['correct']}/{r['total']} | {r['wrong_class']} | {r['rejected']} | {r['missed']} | {r['unmatched_counted']} |")
    lines+=['','Checking clips: '+', '.join(check)+'. Only the frozen selection and original baseline are evaluated; checking scores do not select a new threshold.',
        '', '| Veto % | Correct counted people | Cyclist group | Pedestrians | Unmatched counted |','|---|---:|---:|---:|---:|']
    for r in checked:
        lines.append(f"| {tag(r['threshold'])} | {r['correct']}/{r['total']} | {r['cyclist_correct']}/{r['cyclist_total']} | {r['pedestrian_correct']}/{r['pedestrian_total']} | {r['unmatched_counted']} |")
    lines+=['','A tie does not establish an optimal threshold. Unmatched tracks are candidates for review, not confirmed false positives. Do not use these development results as a claim of independently validated accuracy.']
    (args.out/'RESULTS.md').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument('--run',default='b4_combo_static5');ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--development',default='night,day');ap.add_argument('--checking',default='night_holdout_2200,day_holdout_1245')
    ap.add_argument('--thresholds',default='off,5,10,15,20,30,40,50');ap.add_argument('--identity-map',type=Path)
    run(ap.parse_args())
