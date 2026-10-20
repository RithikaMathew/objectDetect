#!/usr/bin/env python3
"""Compare saved detector track-majority and raw weighted X-CLIP labels.

No inference. Classification on the same matched, scored tracks only; NOT
standalone detector recall, counting accuracy or verified track identities.
"""
import argparse
import csv
import datetime as dt
import json
import math
from pathlib import Path
from eval_truth import CLIPS,read_truth,read_tracks,match,load_identity_map

LABELS={'night':'Night 21:15–21:30','day':'Day 14:00–14:15',
        'night_holdout_2200':'Night 22:00–22:15','day_holdout_1245':'Day 12:45–13:00'}


def compare(root,run,out,identity_path=None):
    identity=load_identity_map(identity_path)if identity_path else None
    rows=[]
    for clip,cc in CLIPS.items():
        truth,skipped=read_truth(root/cc['truth'])
        if skipped:raise ValueError(f'Incomplete truth for {clip}')
        prefix=f'Standard_SCU8OG_2019-07-10_0000.{cc["chunk"]:03d}'
        folder=root/'counts'/run
        tracks=read_tracks(folder/(prefix+'_tracks.csv'),dt.datetime.strptime(cc['start'],'%Y-%m-%d %H:%M:%S'))
        source=folder/(prefix+'_rules_audit.csv')
        with source.open()as stream:audit={r['track_id']:r for r in csv.DictReader(stream)}
        matches,_=match(truth,tracks,identity.get((run,clip),{})if identity is not None else None)
        for person,status,track in matches:
            row=dict(clip=clip,truth_id=person['id'],truth_raw_class=person['raw'],truth_scored_class=person['c'],
                     track_id=track['id']if track else '',identity_verified=int(identity is not None and status!='UNVERIFIED'),
                     included=0,exclusion='',detector_cyclist_percent='',detector_label='',xclip_label='',
                     detector_correct='',xclip_correct='',track_counted=track['counted']if track else '',source=str(source))
            r=audit.get(track['id'])if track else None
            if identity is not None and status=='UNVERIFIED':row['exclusion']='identity not approved'
            elif r is None:row['exclusion']='no matched scored audit track'
            else:
                percent=float(r['det_cyclist_pct']);xl={'BICYCLIST':'cyclist','PEDESTRIAN':'pedestrian'}.get(r['xclip_label'])
                if not math.isfinite(percent)or not 0<=percent<=100 or xl is None:row['exclusion']='missing valid detector/X-CLIP evidence'
                else:
                    det='cyclist'if percent>=50 else'pedestrian'
                    row.update(included=1,detector_cyclist_percent=percent,detector_label=det,xclip_label=xl,
                               detector_correct=int(det==person['c']),xclip_correct=int(xl==person['c']))
            rows.append(row)
    out.mkdir(parents=True,exist_ok=False)
    with(out/'per_person.csv').open('w',newline='')as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    usable=[r for r in rows if r['included']]
    def counts(rr):return [sum(r['detector_correct']for r in rr),sum(r['xclip_correct']for r in rr),len(rr)]
    def formatted(num,den):return f'{num}/{den} ({100*num/den:.1f}%)'if den else 'not evaluated'
    total=counts(usable)
    lines=['# Detector versus X-CLIP: existing four labelled clips','',
           f'Run: {run}. No new inference or Slurm job.',
           'Detector label = cyclist in at least50%of its track observations; otherwise pedestrian. This is a track-majority classifier, not single-frame detection accuracy.',
           'X-CLIP label = argmax of the RAW box-height-weighted video probabilities from rules_audit.csv, BEFORE veto/speed fusion.',
           'Same matched, scored tracks for both methods; includes rejected tracks, so duration filtering does not bias this comparison.',
           'Motorcycle is grouped with cyclists to match the existing21-person evaluation; raw class preserved in CSV.',
           'Identity-approved subset only.'if identity is not None else 'PROVISIONAL time-only person matching; identities have not been human-verified. Simultaneous people and ID switches can affect these results.',
           f'Included: {len(usable)}/{len(rows)} truth rows. Excluded rows and reasons are in per_person.csv.',
           'This does NOT measure standalone detector recall, false-positive detection rate, continuous-video counting accuracy or performance on unseen cameras.','',
           '| Clip | Detector correct | X-CLIP correct |','|---|---:|---:|']
    for clip in CLIPS:
        a,b,n=counts([r for r in usable if r['clip']==clip]);lines.append(f'| {LABELS[clip]} | {a}/{n} | {b}/{n} |')
    lines += [f'| **Total** | **{formatted(total[0],total[2])}** | **{formatted(total[1],total[2])}** |','',
              '| Truth group | Detector correct | X-CLIP correct |','|---|---:|---:|']
    for label in ('cyclist','pedestrian'):
        a,b,n=counts([r for r in usable if r['truth_scored_class']==label]);lines.append(f'| {label}'+(' (includes1motorcycle)'if label=='cyclist'else'')+f' | {a}/{n} | {b}/{n} |')
    groups={name:[]for name in ('both_right','both_wrong','detector_only_right','xclip_only_right')}
    for r in usable:
        d,x=r['detector_correct'],r['xclip_correct']
        key='both_right'if d and x else'both_wrong'if not d and not x else'detector_only_right'if d else'xclip_only_right'
        groups[key].append(r['clip']+'/'+r['truth_id'])
    lines += ['','## Where they disagree','']+[f'- {key}: {len(ids)} — '+', '.join(ids)for key,ids in groups.items()]
    lines += ['','Interpretation: a small paired classification comparison on development clips. A two-person lead is not proof one model is universally superior. Keep both signals until identity checks and broader validation justify changing the system.']
    (out/'RESULTS.md').write_text('\n'.join(lines)+'\n')
    (out/'summary.json').write_text(json.dumps(dict(run=run,truth_rows=len(rows),included=total[2],detector_correct=total[0],
        xclip_correct=total[1],identity_policy='approved_only'if identity is not None else'legacy_time_only',
        groups=groups),indent=2))
    print('\n'.join(lines))
    return rows


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument('--run',default='b4_combo_static5');ap.add_argument('--out',type=Path,required=True);ap.add_argument('--identity-map',type=Path)
    args=ap.parse_args();compare(args.root.resolve(),args.run,args.out.resolve(),args.identity_map)
