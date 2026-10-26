#!/usr/bin/env python3
"""Explain every missing speed/coverage value; optionally make short review clues."""
import argparse
import csv
import datetime as dt
import html
import json
from pathlib import Path
import subprocess
from export_manual_calibrations import export
from preview_ffmpeg import resolve


def make_audit(batch,review_inputs,observations,out,clips=False):
    bundle=export(batch);pack=json.loads(review_inputs.read_text());manual=json.loads(observations.read_text());out.mkdir(parents=True,exist_ok=False)
    annotated={r['key'] for r in manual['observations']};missing=[e for e in pack['entries'] if e['key'] not in annotated]
    (out/'batch_diagnostics.json').write_text(json.dumps(bundle,indent=2)+'\n')
    summary={r['location']:r for r in bundle['automatic_comparison']};rows=[]
    for location,r in summary.items():
        if r.get('model_candidate_mean_mph','')!='':continue
        counted=r.get('counted_candidate_tracks','');found=r.get('found_candidate_tracks','')
        reason='No complete inference window; interrupted or unreported job' if r.get('state') in ('STARTED','NO_STATUS') else 'All bicycle-labelled candidates rejected by counting filters' if str(counted)=='0' and str(found) not in ('','0') else 'No eligible metric trajectories; inspect candidate exclusions'
        rows.append(dict(location=location,missing_value='HiPerGator speed',reason=reason,next_action='Existing Aloma recovery job already submitted; do not submit duplicate' if location=='Aloma' else 'Inspect saved candidate audit and rules; rerunning identical settings will not fix rejection'))
    for e in missing:rows.append(dict(location=e['source']['reference_location'],missing_value='Manual annotation '+e['reference']['start'],reason='Owner could not visually identify/annotate a cyclist; no JSON submitted. Blur, tiny objects, channel mismatch or missed encounters unresolved.',next_action='Review short saved-track candidate clues below; absence of clues does not prove no bicycle'))
    for e in pack['entries']:
        for b in bundle['automatic_partial_count_bins']:
            if b['camera']==e['camera'] and b['bin_start']==e['reference']['start']:
                rows.append(dict(location=e['source']['reference_location'],missing_value='Complete-bin count '+b['bin_start'],reason='Only '+b['seconds_covered']+' seconds exported; full-bin comparison withheld',next_action='Partial counts retained in batch_diagnostics.json; do not present as full15-minute accuracy'))
    for e in manual.get('encounters',[]):
        if e.get('speed_mph','')=='':rows.append(dict(location=e['location'],missing_value='Manual speed '+e['encounter_id'],reason=e['status']+'; click span '+str(e['span_seconds'])+'seconds',next_action='Short-span diagnostic requires separately disclosed policy; no invented speed'))
    if rows:
        with (out/'missing_values.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    clues=[];exe=resolve() if clips else None
    for e in missing:
        matches=[]
        for candidate in bundle['candidate_audit']:
            if candidate['camera']!=e['camera']:continue
            first=dt.datetime.fromisoformat(candidate['track']['first_time'])
            if not dt.datetime.fromisoformat(e['reference']['start'])<=first<dt.datetime.fromisoformat(e['reference']['end']):continue
            matches.append(candidate)
        # Counted candidates first, then earliest rejected candidates; no selection by speed.
        matches.sort(key=lambda c:(c['track'].get('counted')!='1',c['track']['first_time']))
        for i,c in enumerate(matches[:6]):
            first=dt.datetime.fromisoformat(c['track']['first_time']);start=max(0,(first-dt.datetime.fromisoformat(c['source_clock'])).total_seconds()-3)
            key=e['key']+'_candidate_'+str(i+1);clue=dict(interval=e['key'],study_count=e['reference']['count'],first_time=c['track']['first_time'],last_time=c['track']['last_time'],track_id=c['track']['track_id'],counted=c['track']['counted'],reasons=c['reasons'],clip=key+'.mp4',annotated_paths=c['annotated_clips']);clues.append(clue)
            if clips:
                with (out/(key+'.log')).open('w') as log:
                    subprocess.run([exe,'-nostdin','-hide_banner','-loglevel','error','-ss',str(start),'-i',c['video'],'-t','12','-an','-c:v','libx264','-preset','fast','-crf','22','-movflags','+faststart',str(out/clue['clip'])],stdout=log,stderr=subprocess.STDOUT,check=True)
    (out/'review_clues.json').write_text(json.dumps(clues,indent=2)+'\n')
    body=['<!doctype html><meta charset="utf-8"><title>Missing annotation review clues</title><h1>Review clues, not confirmed bicycles</h1><p>Raw12-second source clips near saved tracks. Check person type yourself. No marks on the source; a detector miss may have no candidate clue. Up to6candidates per missing interval. Existing thresholds unchanged.</p>']
    for c in clues:body.append('<h2>'+html.escape(c['interval']+' '+c['first_time']+' track '+c['track_id'])+'</h2><video controls preload="none" width="720" src="'+html.escape(c['clip'],quote=True)+'"></video>')
    (out/'index.html').write_text('\n'.join(body))
    (out/'RESULTS.md').write_text('# Missing values audit\n\nAll interrupted, filtered, partially covered and unannotated cells are listed in missing_values.csv. batch_diagnostics.json preserves rules and source metadata. Existing detection thresholds are unchanged. No full detection reruns were submitted. '+str(len(clues))+' candidate clues for missing manual intervals; clips extracted: '+str(clips)+'. Zero clues does not prove zero bicycles.\n')
    print('Output:',out,'missing cells:',len(rows),'review clues:',len(clues),'clips:',clips)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',type=Path,required=True);p.add_argument('--manual',type=Path,default=Path(__file__).resolve().parents[4]/'manual');p.add_argument('--out',type=Path,required=True);p.add_argument('--clips',action='store_true');a=p.parse_args();make_audit(a.batch,a.manual/'analysis/review_inputs.json',a.manual/'analysis/normalized_observations.json',a.out,a.clips)
