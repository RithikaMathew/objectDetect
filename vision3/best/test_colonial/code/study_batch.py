#!/usr/bin/env python3
"""Inventory study-matched footage and submit the fixed reference; CPU dry-run default."""
import argparse
import csv
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import sys
from submit_newsites import source_clock
from submit_research import submit
from run_batch5 import parse_envv

REPO=Path(__file__).resolve().parents[4]


def read_csv(path):
    with path.open() as f:return list(csv.DictReader(f))


def write_csv(path, rows):
    if not rows:raise ValueError('No rows to write')
    with path.open('w',newline='')as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def archive_paths(path):
    result=set()
    for line in path.read_text().splitlines():
        index=line.find('MioVision Data/')
        if index>=0 and line.lower().endswith('.mp4'):result.add(line[index:])
    return sorted(result)


def inventory(mapping,listing,data_root,inspect=False):
    paths=archive_paths(listing);rows=[];seen={}
    for entry in read_csv(mapping):
        example=Path(entry['example_mp4'])
        prefix=re.match(r'(Standard_[A-Za-z0-9]+_\d{4}-\d{2}-\d{2}_\d{4})',example.name)
        if prefix is None:raise ValueError('Unrecognised mapping '+str(example))
        for relative in paths:
            if not relative.startswith(str(example.parent.parent)+'/') or not Path(relative).name.startswith(prefix[1]+'.'):continue
            if relative in seen:raise ValueError('Video assigned to multiple sites: '+relative)
            seen[relative]=entry['gt_site'];video=data_root/relative
            try:clock=source_clock(relative).isoformat(sep=' ');clock_status='filename_inferred_not_verified'
            except ValueError:clock='';clock_status='BLOCKED_multipart_filename_needs_clock_override'
            row=dict(site=entry['gt_site'],study_date=entry['date'],mapping_score=entry['match_score'],
                mapping_ambiguous=entry['ambiguous'],archive_path=relative,video=str(video),
                exists=int(video.is_file()),clock=clock,clock_status=clock_status,
                duration_seconds='',fps='',frames='',width='',height='',probe_status='not_probed',
                nominal_hours=1,gt_cyclist_count=entry['gt_cyclist_count'])
            if inspect:
                if not video.is_file():row['probe_status']='missing'
                else:
                    import cv2
                    cap=cv2.VideoCapture(str(video))
                    try:
                        fps=cap.get(cv2.CAP_PROP_FPS);frames=cap.get(cv2.CAP_PROP_FRAME_COUNT)
                        width=cap.get(cv2.CAP_PROP_FRAME_WIDTH);height=cap.get(cv2.CAP_PROP_FRAME_HEIGHT);ok,_=cap.read()
                        if not ok or not all(math.isfinite(x) and x>0 for x in (fps,frames,width,height)):raise ValueError('unreadable metadata/frame')
                        row.update(duration_seconds=frames/fps,fps=fps,frames=int(frames),width=int(width),height=int(height),probe_status='readable_metadata_not_full_decode')
                    except Exception as exc:row['probe_status']='unreadable: '+str(exc)
                    finally:cap.release()
            rows.append(row)
    if not rows:raise ValueError('No matching archive paths')
    return rows


def inventory_report(rows,out):
    out.mkdir(parents=True,exist_ok=False);write_csv(out/'inventory.csv',rows)
    missing_clocks=[dict(archive_path=r['archive_path'],clock='',reviewer='',evidence='') for r in rows if not r['clock']]
    if missing_clocks:write_csv(out/'clock_overrides_needed.csv',missing_clocks)
    sites=sorted({r['site']for r in rows});site_rows=[]
    for site in sites:
        rr=[r for r in rows if r['site']==site]
        measured=[float(r['duration_seconds']) for r in rr if r['duration_seconds']!='']
        site_rows.append(dict(site=site,files=len(rr),nominal_video_hours=len(rr),
            measured_hours=sum(measured)/3600 if measured else '',probed_files=len(measured),
            clock_blocked=sum(not r['clock']for r in rr),mapping_score=rr[0]['mapping_score']))
    write_csv(out/'by_site.csv',site_rows)
    total=len(rows);cn=[r for r in site_rows if r['site']=='Colonial North'][0]
    summary=dict(site_date_pairs=len(sites),listed_video_files=total,nominal_video_hours=total,
        nominal_other_than_Colonial_North_hours=total-cn['files'],Colonial_North=cn,
        measured_hours=sum(float(r['duration_seconds']) for r in rows if r['duration_seconds']!='')/3600,
        probed_files=sum(r['duration_seconds']!=''for r in rows),clock_blocked_files=sum(not r['clock']for r in rows),
        assumed_gpu_hours_at_2_8x=total*2.8,nominal_two_gpu_days=total*2.8/2/24,
        exact_total_known=all(r['duration_seconds']!=''for r in rows))
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    text=['# Study footage inventory','',f'{total} unique listed files across {len(sites)} mapped site/date pairs.',
        f'Nominal footage: {total} hours IF each chunk is one hour. Colonial North: {cn["files"]} files, approximately {cn["files"]} hours; not one hour total.',
        f'Other than Colonial North: {total-cn["files"]} nominal hours.',
        f'At the illustrative measured-development processing factor2.8GPU-hours/video-hour: {total*2.8:.1f}GPU-hours, or {total*2.8/48:.1f}days on two continuously available GPUs, excluding queueing. This is NOT a runtime guarantee.',
        f'Probed files: {summary["probed_files"]}/{total}; measured duration: {summary["measured_hours"]:.3f}hours (only probed files). Exact total known: {summary["exact_total_known"]}.',
        f'Clock-blocked multipart filenames: {summary["clock_blocked_files"]}. Their hour index cannot be inferred reliably; explicit clock overrides required.',
        'Old mapping chunk totals summed to1967; actual unique matching archive paths total1919. Rinehart Sidewalk was listed as96chunks in mapping but has48matching archive paths. Do not double-count the mapping total.',
        '', 'Recommend one full Colonial North source chunk first (default chunk013,12:00–13:00 inferred), not a full48-hour run immediately. Review counting, boundary fragmentation, runtime/memory and storage. Then use scope colonial or all if desired.',
        'A one-hour pilot is expected around2.8GPU-hours using the development ratio. Four existing truth clips together span one hour but are four separate15-minute windows, not one continuous recorded hour.',
        '', 'Mappings are inherited candidate site/date mappings, not independently verified ground truth alignment. Aggregate study counts do not measure detector accuracy. Outputs are segmented by source file; IDs reset at file boundaries. Counts may duplicate people crossing boundaries. No camera-specific lane claims without that camera’s zones. No physical speed claim.']
    (out/'RESULTS.md').write_text('\n'.join(text)+'\n');print('\n'.join(text))
    return summary


def select(rows,scope,site=None,exclude=None,pilot_chunk=13):
    result=[dict(r)for r in rows if (not site or r['site']==site) and (not exclude or r['site']!=exclude)]
    if scope=='colonial' or (scope=='pilot' and not site):result=[r for r in result if r['site']=='Colonial North']
    if scope=='pilot':result=[r for r in result if re.search(r'\.'+f'{pilot_chunk:03d}'+r'\.mp4$',Path(r['video']).name)]
    if not result:raise ValueError('No files selected')
    if scope=='pilot' and len(result)!=1:raise ValueError('Pilot must resolve to exactly one source; multipart hour is ambiguous')
    return result


def build_plan(root,tag,rows,zones_dir=None,require_zones=False):
    base=dict(parse_envv(root/'code/run_batch4.sh','5'));tasks=[];seen_clocks=set()
    for i,row in enumerate(rows):
        if not row['clock']:raise ValueError('Missing source clock: '+row['video'])
        identity=(row['site'],row['clock'])
        if identity in seen_clocks:raise ValueError('Duplicate source-start time for one camera; verify duplicate coverage: '+str(identity))
        seen_clocks.add(identity)
        fps=float(row['fps']);duration=float(row['duration_seconds'])
        if row['probe_status']!='readable_metadata_not_full_decode' or fps<=0 or duration<=0:raise ValueError('Probe inventory on cluster first: '+row['video'])
        key=f'v{i:04d}_'+hashlib.sha256(row['archive_path'].encode()).hexdigest()[:8]
        env={**base,'RUN':f'{tag}_{key}','VIDEO_OVERRIDE':row['video'],'CHUNK':'1','START_FRAME':'1','MAX_FRAMES':'0',
            'SESSION_START':row['clock'].replace(' ','_'),'BIC_MIN_SEC':'3','PED_MIN_SEC':'3','SHORT_MIN_SEC':'0.3',
            'SHORT_DET_PCT':'90','SHORT_WBIC':'0.9','STREAM_CLIPS':'0',
            'WEIGHTS':str(root.parent.parent/'runs/detect/finetune_runs/rtdetr_v3/weights/best.pt'),
            'ZONES_JSON':'/nonexistent_zones.json','GT_XLS':'none','EXPORT_VEHICLE_TRAJECTORIES':'1',
            'CLOCK_NOTE':row['clock_status']+'; verify embedded camera clock before study comparison'}
        # Only this known camera/date may inherit its existing area polygons.
        if row['site']=='Colonial North':
            env['ZONES_JSON']=str(root/'zones/colonial_north_v1.json')
            chunk=int(re.search(r'\.(\d{3})\.mp4$',row['video'])[1])
            env['CHUNK']=str(chunk)
            env['SESSION_START']=(dt.datetime.fromisoformat(row['clock'])-dt.timedelta(hours=chunk-1)).strftime('%Y-%m-%d_%H:%M:%S')
        wall_seconds=max(3600,math.ceil(duration*4+1800));hours=math.ceil(wall_seconds/3600)
        if hours>12:raise ValueError('Source too long for planned job; split it first: '+row['video'])
        lane_zones=None
        if row['site']=='Colonial North':lane_zones=root/'zones/colonial_north_v2.json'
        if zones_dir:
            from site_zone_setup import zone_key
            candidate=zones_dir/(zone_key(row['site'])+'.json')
            if candidate.is_file():
                z=json.loads(candidate.read_text())
                if z.get('site')!=row['site'] or z.get('recording_date')!=row['study_date'] or not z.get('area_alignment_confirmed') or not z.get('reviewer'):raise ValueError('Wrong or unconfirmed camera zones: '+str(candidate))
                lane_zones=candidate.resolve()
        if require_zones and lane_zones is None:raise ValueError('Mark zones first for '+row['site'])
        tasks.append(dict(key=key,kind='pipeline',gpu=True,deps=[],env=env,scale_pixels=True,
            site=row['site'],inventory=row,lane_zones=str(lane_zones)if lane_zones else None,walltime=f'{hours:02}:00:00'))
    tasks.append(dict(key='final_report',kind='report',gpu=False,deps=[t['key']for t in tasks]))
    return dict(root=str(root),tag=tag,purpose='study_batch',tasks=tasks,jobs={},created=dt.datetime.now().isoformat())


def write_report(directory,plan,final=False):
    root=Path(plan['root']);out=root/'exp_results'/f'STUDY_{plan["tag"]}';out.mkdir(parents=True,exist_ok=True)
    results=[]
    for task in plan['tasks']:
        if task['kind']=='report':continue
        statusfile=directory/(task['key']+'.json');s=json.loads(statusfile.read_text()) if statusfile.exists() else {}
        row=dict(site=task['site'],source=task['env']['VIDEO_OVERRIDE'],state=s.get('state','NO_FINAL_STATUS'),
            source_clock=task['inventory']['clock'],clock_status=task['inventory']['clock_status'],
            duration_seconds='',runtime_seconds='',cyclists='',pedestrians='',vehicles='',tracks='',annotated='',bin_counts='')
        if row['state']=='SUCCEEDED':
            log=json.loads(Path(s['result']['run_log']).read_text())
            row.update(duration_seconds=log['duration_s_processed'],runtime_seconds=log['runtime_s'],
                cyclists=log['final_counts']['bicyclists'],pedestrians=log['final_counts']['pedestrians'],
                vehicles=log['final_counts']['vehicles'],tracks=log['tracks_csv'],
                annotated=json.dumps(log['annotated_clips']),bin_counts=log['bin_counts_csv'])
        results.append(row)
    write_csv(out/'outputs.csv',results)
    from lane_use_report import merge
    folders=[out/'per_source'/t['key'] for t in plan['tasks'] if t['kind']=='pipeline']
    merge(folders,out)
    lines=['# Study batch outputs','',f'Completed sources: {sum(r["state"]=="SUCCEEDED" for r in results)}/{len(results)}.',
        'outputs.csv contains actual counts and exact annotated paths from completed jobs. Failed/missing statuses are not scored as zero people.',
        'all_tracks.csv records each user/vehicle track, predicted type, count status, dominant lane, observed lane fractions and midpoint15-minute bin. counts_by_site_user_lane.csv and counts_15min_by_user_lane.csv summarize counted tracks. Unmarked cameras remain unassigned; no lane accuracy claimed.',
        'Predicted counts are not accuracy. No per-person truth, camera calibration or new lane boundaries are invented. Source-file IDs reset; boundary duplicates need review. Clocks are filename-inferred unless independently confirmed.',
        'Do not compare partial/misaligned source coverage against full-study totals as an accuracy result. Use saved15-minute bin_counts files and confirm camera, channels, recording day and clock first.',
        'Yellow headers say GT not labelled unless hand-labelled bins are applicable; aggregate workbook totals are not substituted as person-level truth.']
    (out/'RESULTS.md').write_text('\n'.join(lines)+'\n');return dict(report=str(out/'RESULTS.md'))


def main():
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='command',required=True)
    inv=sub.add_parser('inventory');inv.add_argument('--mapping',type=Path,default=REPO/'data/video_site_mapping.csv')
    inv.add_argument('--listing',type=Path,default=REPO/'data/all_videos.txt')
    inv.add_argument('--data-root',type=Path,default=Path('/orange/xiangyan/rithika/vision/pilot_clips'))
    inv.add_argument('--probe',action='store_true');inv.add_argument('--out',type=Path,required=True)
    go=sub.add_parser('submit');go.add_argument('--inventory',type=Path,required=True)
    go.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);go.add_argument('--tag',required=True)
    go.add_argument('--scope',choices=['pilot','colonial','all'],default='pilot');go.add_argument('--site');go.add_argument('--exclude-site')
    go.add_argument('--clock-overrides',type=Path,help='CSV archive_path,clock,reviewer,evidence; independently confirmed source-start times')
    go.add_argument('--concurrency',type=int,default=2);go.add_argument('--go',action='store_true')
    go.add_argument('--pilot-chunk',type=int,default=13)
    go.add_argument('--zones-dir',type=Path);go.add_argument('--require-zones',action='store_true')
    lane=sub.add_parser('lanes');lane.add_argument('--manifest',type=Path,required=True)
    lane.add_argument('--zones-dir',type=Path,required=True);lane.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    if a.command=='lanes':
        from lane_use_report import report,merge
        from site_zone_setup import zone_key
        plan=json.loads(a.manifest.read_text());a.out.mkdir(parents=True,exist_ok=False);folders=[]
        for task in plan['tasks']:
            if task['kind']!='pipeline':continue
            status=a.manifest.parent/(task['key']+'.json')
            if not status.is_file():continue
            record=json.loads(status.read_text())
            if record.get('state')!='SUCCEEDED':continue
            zone=a.zones_dir/(zone_key(task['site'])+'.json')
            folder=a.out/'per_source'/task['key']
            if not zone.is_file():raise FileNotFoundError('Missing camera zones: '+str(zone))
            report(Path(record['result']['run_log']),folder,zone,task['site']);folders.append(folder)
        merge(folders,a.out);print(a.out);return
    if a.command=='inventory':inventory_report(inventory(a.mapping,a.listing,a.data_root,a.probe),a.out);return
    if not re.fullmatch(r'[A-Za-z0-9_]{1,32}',a.tag):ap.error('Tag must be1–32letters/digits/underscores')
    if not 1<=a.concurrency<=8:ap.error('Concurrency must be1–8')
    rows=select(read_csv(a.inventory),a.scope,a.site,a.exclude_site,a.pilot_chunk)
    if a.clock_overrides:
        override={r['archive_path']:r for r in read_csv(a.clock_overrides)}
        for r in rows:
            if r['archive_path'] in override:
                o=override[r['archive_path']]
                if not o.get('reviewer') or not o.get('evidence'):raise ValueError('Clock override needs reviewer and evidence')
                r.update(clock=dt.datetime.fromisoformat(o['clock']).isoformat(sep=' '),clock_status='human_verified: '+o['evidence'])
    print(f'Selected {len(rows)}files. Pilot uses one hourly source (default Colonial North; --site selects another study camera).')
    blocked=[r['video']for r in rows if not r['clock'] or not r['duration_seconds'] or not r['probe_status'].startswith('readable_')]
    if blocked:print(f'{len(blocked)}files need successful cluster metadata probe or verified clock override; submission will refuse partial coverage.')
    if not a.go:print('DRY RUN: no jobs submitted. Add --go after probing.');return
    if blocked:raise ValueError('Cannot submit selected coverage; unresolved files:\n'+'\n'.join(blocked[:20]))
    if not shutil.which('sbatch'):raise RuntimeError('Submit on HiPerGator with yolo_env activated')
    plan=build_plan(a.root.resolve(),a.tag,rows,a.zones_dir,a.require_zones)
    if not (Path(sys.executable).parent/'activate').is_file():raise RuntimeError('Activate yolo_env before submission')
    for task in plan['tasks'][:-1]:
        for path in (Path(task['env']['VIDEO_OVERRIDE']),Path(task['env']['WEIGHTS']),a.root/'code/research_job.slurm'):
            if not path.is_file():raise FileNotFoundError(path)
        if (a.root/'counts'/task['env']['RUN']).exists():raise FileExistsError(task['env']['RUN'])
    submit(plan,a.root/'logs'/a.tag,a.concurrency)
    print('Report:',a.root/'exp_results'/f'STUDY_{a.tag}'/'RESULTS.md')

if __name__=='__main__':main()
