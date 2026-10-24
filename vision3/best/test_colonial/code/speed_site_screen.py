#!/usr/bin/env python3
"""Bounded CPU previews for candidate bicycle-speed reference cameras; no inference."""
import argparse
import csv
import html
import json
import shutil
import subprocess
import zipfile
from collections import Counter
from pathlib import Path
import cv2
from study_batch import inventory
from site_zone_setup import zone_key

# Explicit candidate aliases; never equated with verified reference camera/date.
CANDIDATES={
 'Baxter':['Baxter'],'Winter Park':['Winter Park Rd Speed'],
 'Carroll':['Carroll NBL'],'Lee':['Lee Road N','Lee Road South'],
 'Edgewater':['Edgewater N'],'Colonial':['Colonial North','Colonial South'],
 'Columbia':['Columbia Ave'],'University':['University SW Speed'],
 'West Orange/Park':['West Orange Path'],'Pleasant Hill':['Pleasant Hill Path'],
 'Rinehart/CST':['Rinehart Path'],'Aloma':['Aloma Path'],'Daniels':['Daniels Path'],
 'Silver Star':[]}
OFFSETS=(300,1200,2100)


def choose(rows,reference):
    selected=[]
    for site in CANDIDATES[reference]:
        choices=[r for r in rows if r['site']==site and r['clock'] and 8<=int(r['clock'][11:13])<17 and r['mapping_ambiguous']=='no']
        if not choices:continue
        firstday=min(r['clock'][:10] for r in choices)
        choices=[r for r in choices if r['clock'][:10]==firstday]
        # Freeze first-day noon (nearest daylight hour if missing), independent of results.
        r=min(choices,key=lambda r:(abs(int(r['clock'][11:13])-12),r['clock'],r['archive_path']))
        selected.append(dict(reference_location=reference,camera_match_status='candidate_alias_not_verified',**r))
    return selected


def plan(root,data_root):
    repo=root.parents[2]
    rows=inventory(repo/'data/video_site_mapping.csv',repo/'data/all_videos.txt',data_root)
    return [r for street in sorted(CANDIDATES) for r in choose(rows,street)]


def screen(a):
    a.out.mkdir(parents=True,exist_ok=False);rows=plan(a.root,a.data_root)
    with (a.out/'selected_sources.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    results=[];spent=0;archive=None
    for r in rows:
        dest=a.out/zone_key(r['site']);dest.mkdir();result=dict(reference_location=r['reference_location'],site=r['site'],clock=r['clock'],source=r['video'],camera_match_status=r['camera_match_status'],status='',width='',height='',median_frame_sharpness='',previews='[]',error='')
        try:
            video=Path(r['video'])
            if not video.exists():
                if not a.extract:raise ValueError('Source not extracted; rerun with --extract on cluster')
                if archive is None:archive=zipfile.ZipFile(a.archive)
                member=r['archive_path'];parts=Path(member).parts
                if Path(member).is_absolute() or '..' in parts:raise ValueError('Unsafe archive member')
                info=archive.getinfo(member)
                if spent+info.file_size>a.max_extract_gb*1024**3:raise ValueError('Extraction budget reached; not inspected')
                video.parent.mkdir(parents=True,exist_ok=True);tmp=video.with_suffix('.speed_screen_partial')
                if tmp.exists():raise ValueError('Partial extraction exists; inspect before retrying')
                try:
                    with archive.open(info) as src,tmp.open('xb') as dst:shutil.copyfileobj(src,dst,1024*1024)
                    tmp.rename(video);spent+=info.file_size
                finally:
                    if tmp.exists():tmp.unlink()
            cap=cv2.VideoCapture(str(video))
            try:
                fps=cap.get(cv2.CAP_PROP_FPS);n=cap.get(cv2.CAP_PROP_FRAME_COUNT)
                if fps<=0:raise ValueError('Unreadable source metadata')
                result.update(width=int(cap.get(3)),height=int(cap.get(4)));sharp=[];previews=[]
                for offset in OFFSETS:
                    if offset+a.preview_seconds>n/fps:continue
                    cap.set(cv2.CAP_PROP_POS_MSEC,offset*1000);ok,frame=cap.read()
                    if not ok:continue
                    sharp.append(float(cv2.Laplacian(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY),cv2.CV_64F).var()))
                    cv2.imwrite(str(dest/f'frame_{offset}.jpg'),frame)
                    preview=dest/f'preview_{offset}.mp4'
                    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-n','-ss',str(offset),'-i',str(video),'-t',str(a.preview_seconds),'-an','-vf','fps=10','-c:v','libx264','-preset','fast','-crf','24',str(preview)],check=True,timeout=180)
                    previews.append(dict(file=str(preview.relative_to(a.out)),source_start_seconds=offset,source_end_seconds=offset+a.preview_seconds,source_clock=r['clock'],clock_status=r['clock_status']))
                if not previews:raise ValueError('No readable preview interval')
                result.update(status='PREVIEWS_READY_REVIEW_REQUIRED',median_frame_sharpness=sorted(sharp)[len(sharp)//2],previews=json.dumps(previews))
            finally:cap.release()
        except Exception as e:result.update(status='NOT_SCREENED',error=str(e))
        results.append(result);print(r['site'],result['status'],result['error'],flush=True)
    if archive:archive.close()
    covered={r['reference_location'] for r in rows}
    for street in sorted(set(CANDIDATES)-covered):results.append(dict(reference_location=street,site='',clock='',source='',camera_match_status='no_verified_candidate',status='NO_CANDIDATE_SOURCE',width='',height='',median_frame_sharpness='',previews='[]',error='No candidate mapped recording in current inventory'))
    with (a.out/'screening.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
    links=[]
    for r in results:
        title=html.escape(r['reference_location']+' / '+r['site'])
        links.append('<h2>'+title+'</h2><p>'+html.escape(r['status']+' '+r['clock']+' '+r['error'])+'</p>')
        for preview in json.loads(r['previews']):
            file=html.escape(preview['file']);links.append(f'<p>Source seconds {preview["source_start_seconds"]}–{preview["source_end_seconds"]}</p><video controls preload="none" width="640" src="{file}"></video>')
    (a.out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Speed camera previews</title><h1>Bicycle speed camera previews</h1><p>Candidate camera aliases, not verified study matches. Review visibility and bicycle ground contact. These clips are not speed estimates or detector outputs.</p>'+''.join(links))
    ready=sum(r['status']=='PREVIEWS_READY_REVIEW_REQUIRED' for r in results)
    (a.out/'RESULTS.md').write_text(f'# Bicycle speed camera screening\n\nReady cameras: {ready}/{len(rows)} candidates. Missing/failed sources recorded in screening.csv. Newly extracted bytes: {spent}.\n\nDownload this entire folder and open index.html. Fixed first-day nearest-noon source per candidate; previews start at05:00,20:00,35:00 into that source. No inference, cyclist selection, lane marking or new calibration. Resolution and Laplacian sharpness describe frames, not accuracy or cyclist visibility. Do not automatically rank cameras by sharpness.\n\nAim for5clearly visible cyclists per usable camera, accepting1–4with sample size disclosed;3is a practical review target, not a statistical guarantee. Select first eligible encounters in chronological order within fixed intervals, regardless of predicted speed or label; do not stop when means match the workbook. A miss remains a detection failure, not silently excluded from detection review. If fewer cyclists appear, report insufficiency before expanding to predetermined additional intervals. Camera/reference facility/date and road-to-sidewalk calibration require review. Current mappings are candidate aliases; Silver Star has no candidate in current inventory.\n')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--data-root',type=Path,default=Path('/orange/xiangyan/rithika/vision/pilot_clips'));p.add_argument('--archive',type=Path,default=Path('/orange/xiangyan/rithika/vision/MioVision_Data.zip'));p.add_argument('--out',type=Path,required=True);p.add_argument('--extract',action='store_true');p.add_argument('--max-extract-gb',type=float,default=5);p.add_argument('--preview-seconds',type=int,default=45)
    a=p.parse_args()
    if not 1<=a.preview_seconds<=120 or a.max_extract_gb<=0:p.error('Preview1–120s, positive extraction budget required')
    screen(a)
