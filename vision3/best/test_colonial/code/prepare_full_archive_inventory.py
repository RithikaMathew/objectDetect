#!/usr/bin/env python3
"""Full ZIP years/counts first, resumable playback-duration audit second; no inference."""
import argparse
import csv
import json
from pathlib import Path
import zipfile
from inventory_miovision_archive import inventory,write_csv,report
from build_video_inventory_readmes import build,read
from audit_video_durations import main as duration_audit


def prepare(archive,out,repo,inventory_only=False):
    with zipfile.ZipFile(archive) as z:
        rows,cameras=inventory(z.namelist())
        metadata=[dict(archive_path=i.filename,bytes=i.file_size,possible_speed_or_calibration_export=bool(any(s in i.filename.lower() for s in ('speed','velocity','calibrat','setup')))) for i in z.infolist() if Path(i.filename).suffix.lower() in ('.csv','.xls','.xlsx','.json','.xml','.txt','.pdf') and not i.filename.startswith('__MACOSX/')]
    if not rows:raise ValueError('No video entries in archive')
    out.mkdir(parents=True,exist_ok=True)
    write_csv(out/'per_video.csv',rows);write_csv(out/'camera_years.csv',cameras)
    write_csv(out/'possible_report_exports.csv',metadata)
    (out/'CAMERA_YEARS.md').write_text(report(cameras))
    compat=out/'duration_inputs';compat.mkdir(exist_ok=True)
    source=[dict(site=r['camera_key'],archive_path=r['archive_path'],video=str(Path('/orange/xiangyan/rithika/vision/pilot_clips')/r['archive_path'])) for r in rows]
    groups=[dict(camera=r['collection']+' / '+r['site_folder']+' / '+r['device'],speed_reference_candidate='') for r in cameras]
    write_csv(compat/'per_source.csv',source);write_csv(compat/'by_camera.csv',groups)
    durations=out/'durations';durations.mkdir(exist_ok=True)
    # Per-video evidence only: never spread a camera aggregate evenly over its files.
    old=repo/'vision3/best/test_colonial/exp_results/VIDEO_DURATION_AUDIT/per_source.csv'
    prior={r['archive_path']:r for r in read(old) if r.get('audit_status')=='MEASURED'}
    prior.update({r['archive_path']:r for r in read(durations/'per_source.csv') if r.get('audit_status')=='MEASURED'})
    seed=[]
    for r in source:
        previous=prior.get(r['archive_path'],{})
        seed.append(dict(r,duration_seconds=previous.get('duration_seconds',''),audit_status=previous.get('audit_status','PENDING'),error='',duration_reader=previous.get('duration_reader',''),measurement_source=previous.get('measurement_source','')))
    write_csv(durations/'per_source.csv',seed)
    summary=dict(video_files=len(rows),site_device_groups=len(cameras),years=sorted({y for r in rows for y in r['recording_years'].split(';') if y}),reused_measured_files=len([r for r in seed if r['audit_status']=='MEASURED']),scope='Entire ZIP',export_candidate_files=len(metadata),export_status='File names only; no native speed result confirmed')
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    build(repo,out)
    print(json.dumps(summary,indent=2),flush=True)
    if not inventory_only:
        try:duration_audit(['--archive',str(archive),'--inventory-dir',str(compat),'--out',str(durations)])
        finally:build(repo,out)
    print('Full inventory README: '+str(repo/'docs/MIOVISION_ARCHIVE_INVENTORY_README.md'),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);repo=Path(__file__).resolve().parents[4]
    p.add_argument('--archive',type=Path,default=Path('/orange/xiangyan/rithika/vision/MioVision_Data.zip'))
    p.add_argument('--repo',type=Path,default=repo)
    p.add_argument('--out',type=Path,default=repo/'vision3/best/test_colonial/exp_results/MIOVISION_FULL_ARCHIVE_INVENTORY')
    p.add_argument('--inventory-only',action='store_true');a=p.parse_args();prepare(a.archive,a.out,a.repo,a.inventory_only)
