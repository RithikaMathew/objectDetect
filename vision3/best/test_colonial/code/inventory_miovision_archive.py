#!/usr/bin/env python3
"""Inventory every video in the ZIP central directory; no extraction or inference."""
import argparse
from collections import defaultdict
import csv
import datetime as dt
import json
from pathlib import Path,PurePosixPath
import re

VIDEO_EXTENSIONS={'.mp4','.mov','.avi','.mkv','.m4v','.mts','.m2ts'}
DATE=re.compile(r'(?<!\d)((?:19|20)\d{2})[-_]([01]\d)[-_]([0-3]\d)(?!\d)')
DEVICE=re.compile(r'(?:Standard_)?(SCU[A-Za-z0-9]+|MIOP\d+)',re.I)


def classify(name):
    parts=PurePosixPath(name).parts
    if not parts or '__MACOSX' in parts or PurePosixPath(name).name.startswith('._') or PurePosixPath(name).suffix.lower() not in VIDEO_EXTENSIONS:return None
    relative=list(parts)
    if relative[0].lower() in ('miovision data','miovision_data'):relative=relative[1:]
    category=relative[0] if len(relative)>1 else 'Archive root'
    family='Bike Lane Study' if category.lower()=='bike lane study' else 'Annual recordings' if re.fullmatch(r'20\d{2}\s+Data',category,re.I) else category
    rest=relative[1:] if len(relative)>1 else relative
    if family=='Bike Lane Study' and rest and rest[0].lower()=='miovision video':rest=rest[1:]
    session_index=next((i for i,p in enumerate(rest[:-1]) if DEVICE.search(p) and DATE.search(p)),None)
    site='/'.join(rest[:session_index]) if session_index is not None else '/'.join(rest[:-1])
    site=site or '(unresolved site folder)'
    # Video/session dates outrank category labels (e.g. a 2021 recording under 2022 Data).
    dates=[]
    filename_dates=DATE.findall(rest[-1]);session_dates=DATE.findall(rest[session_index]) if session_index is not None else []
    selected=filename_dates or session_dates
    for y,m,d in selected:
        try:dates.append(dt.date(int(y),int(m),int(d)).isoformat())
        except ValueError:pass
    years=sorted({d[:4] for d in dates})
    device_match=DEVICE.search(rest[session_index] if session_index is not None else rest[-1])
    device=device_match.group(1).upper() if device_match else 'Unknown device'
    return dict(archive_path=name,collection=family,archive_category=category,site_folder=site,device=device,
                camera_key=family+' / '+site+' / '+device,recording_years=';'.join(years),recording_dates=';'.join(sorted(set(dates))),
                date_basis='video_filename' if filename_dates and dates else 'session_directory' if session_dates and dates else 'UNKNOWN',
                session_path='/'.join(rest[:session_index+1]) if session_index is not None else '/'.join(rest[:-1]))


def write_csv(path,rows):
    if not rows:return
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)


def inventory(names):
    rows=[];seen=set()
    for name in names:
        r=classify(name)
        if r is not None and name not in seen:rows.append(r);seen.add(name)
    grouped=defaultdict(list)
    for r in rows:grouped[r['camera_key']].append(r)
    cameras=[]
    for key,rr in sorted(grouped.items()):
        years=sorted({y for r in rr for y in r['recording_years'].split(';') if y})
        dates=sorted({d for r in rr for d in r['recording_dates'].split(';') if d})
        cameras.append(dict(collection=rr[0]['collection'],site_folder=rr[0]['site_folder'],device=rr[0]['device'],
                            years=';'.join(years) or 'Unknown',video_files=len(rr),sessions=len({r['session_path'] for r in rr}),
                            unknown_date_files=sum(not r['recording_years'] for r in rr),first_session_date=dates[0] if dates else '',last_session_date=dates[-1] if dates else '',
                            source_categories=';'.join(sorted({r['archive_category'] for r in rr})),
                            duration_hours='',duration_status='NOT_MEASURED_FULL_ARCHIVE'))
    return rows,cameras


def report(cameras):
    lines=['<!-- FULL_ARCHIVE_INVENTORY_START -->','## Complete MioVision ZIP: camera folders and recording years','',
           'Scanned all video entries in the ZIP central directory. Years below come from video filenames or dated session directories, not the year-category folder. A session date is not the full date range of all hourly chunks. Camera identifiers below mean site-folder/device combinations; identical or differently spelled street names are not assumed to be the same physical view. No GPS/intersection locations were inferred.','',
           '| Collection | Site / view folder | Device identifier | Recording years | Video files | Files with unknown date |',
           '|---|---|---|---|---:|---:|']
    for r in cameras:
        cells=[r[k].replace('|','\\|') for k in ('collection','site_folder','device','years')]
        lines.append('| '+' | '.join(cells)+f" | {r['video_files']} | {r['unknown_date_files']} |")
    lines+=['','**Full-archive duration hours have not been measured by this file-list scan.** The verified 1,919-file/41-camera hours elsewhere in this README apply only to the Bike Lane Study subset. Unknown dates remain unknown rather than borrowing the category year.','<!-- FULL_ARCHIVE_INVENTORY_END -->']
    return '\n'.join(lines)+'\n'


def main():
    import zipfile
    p=argparse.ArgumentParser(description=__doc__)
    repo=Path(__file__).resolve().parents[4]
    p.add_argument('--archive',type=Path,default=Path('/orange/xiangyan/rithika/vision/MioVision_Data.zip'))
    p.add_argument('--out',type=Path,default=repo/'vision3/best/test_colonial/exp_results/MIOVISION_FULL_ARCHIVE_INVENTORY')
    p.add_argument('--update-readme',type=Path)
    a=p.parse_args()
    with zipfile.ZipFile(a.archive) as archive:rows,cameras=inventory(archive.namelist())
    if not rows:raise ValueError('No video entries found; refusing to replace report')
    a.out.mkdir(parents=True,exist_ok=True)
    write_csv(a.out/'per_video.csv',rows);write_csv(a.out/'camera_years.csv',cameras)
    md=report(cameras);(a.out/'CAMERA_YEARS.md').write_text(md)
    summary=dict(archive=str(a.archive),video_files=len(rows),site_device_groups=len(cameras),
                 recording_years=sorted({y for r in rows for y in r['recording_years'].split(';') if y}),
                 files_with_unknown_date=sum(not r['recording_years'] for r in rows),scope='Entire archive; no extraction or video-duration measurement')
    (a.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (a.out/'RESULTS.md').write_text('# Full MioVision archive inventory\n\n'+json.dumps(summary,indent=2)+'\n\n'+md)
    if a.update_readme:
        text=a.update_readme.read_text();start='<!-- FULL_ARCHIVE_INVENTORY_START -->';end='<!-- FULL_ARCHIVE_INVENTORY_END -->'
        if start in text:
            before,tail=text.split(start,1)
            if end not in tail:raise ValueError('Incomplete inventory markers in README')
            text=before+md+tail.split(end,1)[1]
        else:text=text.rstrip()+'\n\n'+md
        a.update_readme.write_text(text)
    print(json.dumps(summary,indent=2));print('Camera/year table: '+str(a.out/'CAMERA_YEARS.md'))
