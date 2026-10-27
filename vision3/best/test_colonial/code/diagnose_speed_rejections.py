#!/usr/bin/env python3
"""Read saved candidate, rule and trajectory files; no inference or threshold changes."""
import argparse
from collections import Counter,defaultdict
import csv
import json
from pathlib import Path


def read(path):
    if not path.is_file():return []
    with path.open() as f:return list(csv.DictReader(f))


def continuous_observations(samples,fps):
    observed=sorted((r for r in samples if not int(r.get('coasted') or 0)),key=lambda r:int(r['frame']))
    longest=0.;begin=None;previous=None;maxgap=0.
    for row in observed:
        frame=int(row['frame'])
        gap=(frame-previous)/fps if previous is not None else 0
        maxgap=max(maxgap,gap)
        if begin is None or gap<=0 or gap>.5:begin=frame
        longest=max(longest,(frame-begin)/fps);previous=frame
    return dict(observed_rows=len(observed),coasted_rows=len(samples)-len(observed),longest_observed_span_with_gaps_at_most_0_5s=round(longest,4),maximum_observed_gap_seconds=round(maxgap,4))


def diagnose(batch,sites):
    manifest=json.loads((batch/'manifest.json').read_text())
    allrows=read(batch/'all_candidate_timestamps.csv');results=[]
    for task in manifest['tasks']:
        if task['reference_site'] not in sites:continue
        location=task['reference_site'];candidates=[r for r in allrows if r['site']==location]
        print('\n'+location+': '+str(len(candidates))+' bicycle-labelled candidates',flush=True)
        reasons=Counter(r.get('exclusion_reason') or 'no_exclusion_recorded' for r in candidates)
        print('Saved exclusion groups: '+json.dumps(dict(reasons)),flush=True)
        for r in candidates:
            log_path=Path(r['run_log'])
            result=dict(location=location,segment=r['segment'],track_id=r['track_id'],counted=r['counted'],eligible=r['eligible'],speed_mph=r.get('speed_mph'),exclusion_reason=r['exclusion_reason'],start=r['track_start'],end=r['track_end'],annotated_clips=r.get('annotated_clips','[]'))
            try:
                log=json.loads(log_path.read_text());track_path=Path(log['tracks_csv']);audit_path=track_path.with_name(track_path.name.replace('_tracks.csv','_rules_audit.csv'))
                result['track']=next((t for t in read(track_path) if t['track_id']==r['track_id']),{})
                result['rules_audit']=next((t for t in read(audit_path) if t['track_id']==r['track_id']),{})
                samples=[t for t in read(Path(log['trajectories_csv'])) if t['track_id']==r['track_id']]
                result['observation_continuity']=continuous_observations(samples,float(log['fps']))
                # Saved task is alongside the site's copied run log, not necessarily original raw log.
                pipeline=batch/task['key']/'windows'/('w'+str(int(r['segment'])).zfill(2))/'pipeline_task.json'
                if pipeline.is_file():
                    saved=json.loads(pipeline.read_text());env=saved.get('env',{})
                    result['saved_thresholds']={k:env.get(k) for k in ('BIC_MIN_SEC','PED_MIN_SEC','NIGHT_BIC_MIN_SEC','SHORT_MIN_SEC','SHORT_RULE_NIGHT_ONLY','PERSON_MIN_CONF','PERSON_MIN_H','PERSON_MIN_DISP','STATIC_FILTER')}
            except Exception as error:result['diagnostic_error']=str(error)
            results.append(result)
            concise={k:result[k] for k in ('segment','track_id','counted','eligible','exclusion_reason','start','end')}
            rules=result.get('rules_audit',{})
            concise['rule_observations']={k:rules.get(k) for k in ('secs','passes_min_duration','night_track','xclip_label','final_label','det_cyclist_pct','weighted_bicyclist','speed_heights_per_s','net_px')}
            concise['continuity']=result.get('observation_continuity',{})
            if 'diagnostic_error' in result:concise['error']=result['diagnostic_error']
            print(json.dumps(concise),flush=True)
    return results


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',type=Path);p.add_argument('--sites',nargs='+',default=['Baxter','Daniels','Winter Park']);a=p.parse_args()
    if a.batch is None:
        matches=list((Path(__file__).resolve().parents[1]/'exp_results').glob('ADAPTIVE_SPEED_shortday_*'))
        if not matches:p.error('No shortday batch found; supply --batch')
        a.batch=max(matches,key=lambda d:d.stat().st_mtime)
    print('Reading '+str(a.batch),flush=True)
    results=diagnose(a.batch,a.sites)
    output=a.batch/'missing_speed_diagnostics.json';output.write_text(json.dumps(dict(batch=str(a.batch),candidates=results,limitation='Rules audit is partial evidence. Multiple count filters can reject a track; continuity ignores spatial calibration support, so it is an upper bound on usable continuity.'),indent=2)+'\n')
    print('\nFull saved evidence: '+str(output))
