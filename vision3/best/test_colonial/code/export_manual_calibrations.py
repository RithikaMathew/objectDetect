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
    bins=[]
    for task in manifest['tasks']:
        for path in (batch/task['key']/'windows').glob('w*/*_bin_counts.csv'):
            for row in read_csv(path):
                if float(row.get('seconds_covered') or 0)<899:continue
                bins.append(dict(location=task['reference_site'],camera=task['source']['site'],bin_start=row['bin_start'],bin_end=row['bin_end'],seconds_covered=row['seconds_covered'],bicyclists_total=row['bicyclists_total']))
    return dict(batch=str(batch),calibrations=calibrations,automatic_comparison=read_csv(batch/'comparison.csv'),automatic_selected_candidates=read_csv(batch/'selected_candidates.csv'),automatic_count_bins=bins)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',type=Path,required=True);p.add_argument('--out',type=Path);a=p.parse_args();payload=json.dumps(export(a.batch),indent=2)
    if a.out:a.out.write_text(payload+'\n');print(a.out)
    else:print(payload)
