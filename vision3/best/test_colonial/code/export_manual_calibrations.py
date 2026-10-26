#!/usr/bin/env python3
"""Export only small saved calibration metadata; no inference or video transfer."""
import argparse
import csv
import json
from pathlib import Path


def export(batch):
    manifest=json.loads((batch/'manifest.json').read_text());calibrations={}
    for task in manifest['tasks']:
        path=batch/task['key']/'calibration/calibration.json'
        if path.exists():
            saved=json.loads(path.read_text())
            calibrations[task['key']]=dict(camera=task['source']['site'],source_clock=task['source']['clock'],calibration={k:saved[k] for k in ('H','geometry_check_passed','validation','sidewalk_transfer') if k in saved})
    def read_csv(path):
        if not path.exists():return []
        with path.open() as f:return list(csv.DictReader(f))
    bins=[];partial_bins=[];diagnostics=[];candidates=[]
    for task in manifest['tasks']:
        for path in (batch/task['key']/'windows').glob('w*/*_bin_counts.csv'):
            for row in read_csv(path):
                seconds=float(row.get('seconds_covered') or 0)
                if seconds<=0:continue
                result=dict(location=task['reference_site'],camera=task['source']['site'],bin_start=row['bin_start'],bin_end=row['bin_end'],seconds_covered=row['seconds_covered'],bicyclists_total=row['bicyclists_total'])
                (bins if seconds>=899 else partial_bins).append(result)
        status_path=batch/task['key']/'status.json'
        if status_path.exists():
            status=json.loads(status_path.read_text())
            diagnostics.append(dict(location=task['reference_site'],camera=task['source']['site'],state=status['state'],stage=status.get('stage'),windows=status.get('windows',[]),failure=status.get('failure','')))
        for log_path in (batch/task['key']/'windows').glob('w*/run_log.json'):
            log=json.loads(log_path.read_text());tracks=Path(log.get('tracks_csv',''))
            if not tracks.is_file():
                matches=list(log_path.parent.glob('*_tracks.csv'));tracks=matches[0] if matches else tracks
            if not tracks.is_file():continue
            audit_path=tracks.with_name(tracks.name.replace('_tracks.csv','_rules_audit.csv'))
            audit={r['track_id']:r for r in read_csv(audit_path)}
            for row in read_csv(tracks):
                if not any(row.get(k,'').upper() in ('BICYCLIST','CYCLIST') for k in ('label','xclip_label','det_label')):continue
                reasons=[];rules=audit.get(row['track_id'],{})
                if row.get('counted')!='1':
                    if rules.get('passes_min_duration')=='0':reasons.append('rules_audit_duration_below_minimum')
                    if not reasons:reasons.append('rejected_count_filters_exact_gate_needs_review')
                candidates.append(dict(location=task['reference_site'],camera=task['source']['site'],source_clock=task['source']['clock'],video=task['source']['video'],segment=log_path.parent.name,annotated_clips=log.get('annotated_clips',[]),track=row,rules_audit=rules,reasons=reasons))
    return dict(batch=str(batch),calibrations=calibrations,automatic_comparison=read_csv(batch/'comparison.csv'),automatic_selected_candidates=read_csv(batch/'selected_candidates.csv'),automatic_count_bins=bins,automatic_partial_count_bins=partial_bins,site_diagnostics=diagnostics,candidate_audit=candidates)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',type=Path,required=True);p.add_argument('--out',type=Path);a=p.parse_args();payload=json.dumps(export(a.batch),indent=2)
    if a.out:a.out.write_text(payload+'\n');print(a.out)
    else:print(payload)
