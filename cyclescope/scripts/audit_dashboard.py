"""Check dashboard values against saved evidence; does not remeasure source video."""
from pathlib import Path
import csv
import hashlib
import json
import math
import sys
from collections import defaultdict

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from cyclescope.service.repository import dashboard
from inventory_miovision_archive import classify


def read(path):
    with (ROOT/path).open() as f:return list(csv.DictReader(f))


def audit():
    output=dashboard()
    archive=read(output['archive_source'])
    by={(r['collection'],r['location'],r['device']):r for r in output['rows'] if r['id'].startswith('archive-')}
    for r in archive:
        actual=by[(r['collection'],r['site_folder'],r['device'])]
        assert actual['videos']==int(r['video_files'])
        assert math.isclose(actual['hours'],float(r['total_playback_hours']),abs_tol=1e-9)
        assert actual['years']==r['recording_years'].split(';')
    raw=read(output['source']);counts=defaultdict(int)
    for r in raw:
        if r['count'].strip():counts[(r['site'],r['date'])]+=int(r['count'])
    expected=defaultdict(int);covered=set()
    for m in read('data/video_site_mapping.csv'):
        info=classify(m['example_mp4']);key=(m['gt_site'],m['date'])
        if info and key in counts:
            group=(info['collection'],info['site_folder'],info['device'])
            if group in by:
                assert key not in covered,'Repeated study mapping would double count'
                covered.add(key);expected[group]+=counts[key]
    for key,value in expected.items():assert by[key]['bicycles']==value
    assert covered==set(counts),'Unmapped count records require explicit inspection'
    speeds={r['location']:r for r in read(output['speed_source'])}
    seen=[]
    for row in output['rows']:
        for speed in row['speeds']:
            seen.append(speed['location'])
            for key,value in speeds[speed['location']].items():assert speed[key]==value
    assert sorted(seen)==sorted(speeds),'Every supplied speed comparison should appear once'
    ref_records=read(output['reference_source'])
    grouped=defaultdict(list)
    for record in ref_records:grouped[record['street']].append(float(record['recomputed_mph']))
    assert {r['location'] for r in output['references']}==set(grouped)
    for ref in output['references']:
        values=grouped[ref['location']]
        assert ref['sample']==len(values)
        assert math.isclose(ref['mean_mph'],sum(values)/len(values),abs_tol=1e-9)
    for row in output['rows']:
        for ref in row['references']:assert ref in output['references']
    summary=json.loads((ROOT/'reports/cluster_returns/20261028/full_archive_inventory/completed_totals.json').read_text())
    assert sum(r['videos'] for r in archive_as_numbers(archive))==summary['total_files']
    actual_hours=sum(r['hours'] for r in archive_as_numbers(archive))
    assert math.isclose(actual_hours,summary['total_playback_hours'],abs_tol=1e-6)
    return dict(status='passed',scope='Matches saved source files; not an independent re-audit of remote video or study truth',
        archive_groups=len(archive),videos=summary['total_files'],playback_hours=actual_hours,
        mapped_study_sessions=len(covered),study_bicycles=sum(counts.values()),speed_comparisons=len(seen),reference_locations=len(grouped),
        source_manifest=output['source_manifest'])


def archive_as_numbers(rows):return [dict(videos=int(r['video_files']),hours=float(r['total_playback_hours'])) for r in rows]

if __name__=='__main__':
    result=audit()
    target=ROOT/'cyclescope/DASHBOARD_DATA_AUDIT.json';target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='source_manifest'},indent=2))
