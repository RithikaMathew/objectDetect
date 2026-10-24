#!/usr/bin/env python3
"""CPU audit of speed references, MP4 tags and small ZIP sidecars; no inference.

Checks for evidence that might locate cameras, not automatic calibration.
Never extracts full videos or assigns physical speeds to tracked people.
"""
import argparse
import csv
import datetime as dt
import io
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import zipfile
from study_tables import read_xlsx
from site_zone_setup import zone_key


def read_csv(path):
    with path.open()as f:return list(csv.DictReader(f))


def write_csv(path,rows,fields):
    with path.open('w',newline='')as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)


def workbook_references(path):
    records={}
    for sheet,rows in read_xlsx(path).items():
        for row in rows:
            values={re.sub(r'\d','',key):value for key,value in row.items()}
            try:
                number=str(int(float(values['A'])));street=values['B'].strip();facility=values['D'].strip()
                feet=float(values['F']);seconds=float(values['G']);source=float(values['I'])
            except (ValueError,KeyError):continue
            if not street or facility not in ('Bike Lane','Sidewalk','Travel Lane','Path') or not all(math.isfinite(x)and x>0 for x in (feet,seconds,source)):continue
            key=(street,number,facility,feet,seconds)
            record=records.setdefault(key,dict(street=street,record_number=number,facility=facility,
                direction=values.get('C',''),relative_direction=values.get('E',''),
                zone_length_feet=feet,seconds=seconds,source_mph=source,
                recomputed_mph=feet/seconds*3600/5280,
                source_minus_recomputed_mph=source-feet/seconds*3600/5280,
                notes=values.get('K',''),source_cells=[]))
            record['source_cells'].append(sheet+'!'+next(iter(row)))
    return [dict(r,source_cells=';'.join(r['source_cells']))for r in records.values()]


def parse_location(value):
    """Only accept explicit paired ISO6709 or named latitude/longitude text."""
    text=str(value)
    match=re.search(r'([+-]\d{2}\.\d+)([+-]\d{2,3}\.\d+)(?:[+-]\d+(?:\.\d+)?)?/?',text)
    if match:latitude,longitude=map(float,match.groups())
    else:
        lat=re.search(r'\blatitude\s*[:=]\s*([+-]?\d+(?:\.\d+)?)',text,re.I)
        lon=re.search(r'\blongitude\s*[:=]\s*([+-]?\d+(?:\.\d+)?)',text,re.I)
        if not lat or not lon:return None
        latitude,longitude=float(lat[1]),float(lon[1])
    if not -90<=latitude<=90 or not -180<=longitude<=180:return None
    return latitude,longitude


def gps_from_exif(data):
    try:
        from PIL import Image
        image=Image.open(io.BytesIO(data));exif=image.getexif();gps=exif.get_ifd(34853)
        if not gps:return None
        def degree(value):return sum(float(x)/scale for x,scale in zip(value,(1,60,3600)))
        lat=degree(gps[2]);lon=degree(gps[4]);lat=-lat if gps[1]in ('S',b'S')else lat;lon=-lon if gps[3]in ('W',b'W')else lon
        if not -90<=lat<=90 or not -180<=lon<=180:return None
        return lat,lon
    except (KeyError,ValueError,TypeError,ImportError,AttributeError,OSError):return None


def inspect_sidecars(archive,entry,out,limit=2*1024*1024):
    names=archive.namelist();example=Path(entry['example_mp4']);folder=str(example.parent)+'/'
    candidates=[]
    for chunk in ('013','001'):
        stem=re.sub(r'\.\d{3}\.mp4$','.'+chunk,example.name)
        for suffix in ('.jpg','.jpeg','.cut'):
            name=folder+stem+suffix
            if name in names and name not in candidates:candidates.append(name)
    if not candidates:
        candidates=[n for n in names if n.startswith(folder) and n.lower().endswith(('.jpg','.jpeg','.cut'))][:6]
    results=[];gps=[];out.mkdir(parents=True,exist_ok=True)
    for name in candidates:
        info=archive.getinfo(name)
        record=dict(member=name,uncompressed_bytes=info.file_size,gps=None,text_clues=[],status='')
        if info.file_size>limit:record['status']='SKIPPED_large_sidecar';results.append(record);continue
        data=archive.read(name)
        target=out/Path(name).name;target.write_bytes(data)
        if name.lower().endswith(('.jpg','.jpeg')):
            coords=gps_from_exif(data);record['status']='EXIF_GPS_found'if coords else'no_readable_EXIF_GPS'
            if coords:record['gps']=coords;gps.append(dict(site=entry['gt_site'],latitude=coords[0],longitude=coords[1],source=name,evidence_type='EXIF_GPS',camera_position_verified=0))
        else:
            # Text clues remain evidence, not executable instructions or inferred coordinates.
            text=data.decode('utf-8',errors='replace')
            for line in text.splitlines():
                if re.search(r'latitude|longitude|\bGPS\b|location|address|intersection|calibrat|distance|metres|meters|feet',line,re.I):record['text_clues'].append(line[:500])
            coords=parse_location(text)
            if coords:
                record['gps']=coords;gps.append(dict(site=entry['gt_site'],latitude=coords[0],longitude=coords[1],source=name,evidence_type='sidecar_explicit_location',camera_position_verified=0))
            record['status']='sidecar_read';record['text_clues']=record['text_clues'][:30]
            record['preview_text']=text[:1500] if '\x00'not in text[:1500] else 'Binary sidecar: '+data[:64].hex()
        results.append(record)
    return results,gps


def inspect_video(path):
    if not path.is_file():return dict(status='not_extracted',path=str(path))
    if not shutil.which('ffprobe'):return dict(status='ffprobe_unavailable',path=str(path))
    try:
        p=subprocess.run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)],capture_output=True,text=True,timeout=45)
        if p.returncode:return dict(status='probe_failed',error=p.stderr[-1000:],path=str(path))
        data=json.loads(p.stdout);return dict(status='probed',path=str(path),metadata=data)
    except (subprocess.TimeoutExpired,json.JSONDecodeError)as exc:return dict(status='probe_failed',path=str(path),error=str(exc))


def run(archive_path,mapping,workbook,data_root,out,only_site=None):
    if not archive_path.is_file():raise FileNotFoundError(archive_path)
    entries=[r for r in read_csv(mapping)if not only_site or r['gt_site']==only_site]
    if not entries:raise ValueError('No matching mapped cameras')
    refs=workbook_references(workbook);out.mkdir(parents=True,exist_ok=False)
    fields=['street','record_number','facility','direction','relative_direction','zone_length_feet','seconds','source_mph','recomputed_mph','source_minus_recomputed_mph','notes','source_cells']
    write_csv(out/'study_speed_references.csv',refs,fields)
    summary=[]
    for street in sorted({r['street']for r in refs}):
        for facility in sorted({r['facility']for r in refs if r['street']==street}):
            rr=[r for r in refs if r['street']==street and r['facility']==facility]
            summary.append(dict(street=street,facility=facility,records=len(rr),lengths_feet=';'.join(str(x)for x in sorted({r['zone_length_feet']for r in rr})),
                source_min_mph=min(r['source_mph']for r in rr),source_max_mph=max(r['source_mph']for r in rr),
                mean_absolute_arithmetic_difference_mph=sum(abs(r['source_minus_recomputed_mph'])for r in rr)/len(rr)))
    write_csv(out/'reference_summary.csv',summary,['street','facility','records','lengths_feet','source_min_mph','source_max_mph','mean_absolute_arithmetic_difference_mph'])
    cameras=[];gps=[]
    with zipfile.ZipFile(archive_path)as archive:
        for entry in entries:
            sidecars,coords=inspect_sidecars(archive,entry,out/'sidecars'/zone_key(entry['gt_site']));gps.extend(coords)
            # Noon source already used for the pilot, if extracted.
            noon=re.sub(r'\.\d{3}\.mp4$','.013.mp4',entry['example_mp4']);path=data_root/noon
            video=inspect_video(path)
            if video['status']=='probed':
                metadata=video['metadata'];tags=[('format',metadata.get('format',{}).get('tags',{}))]
                tags += [(f'stream{i}',stream.get('tags',{}))for i,stream in enumerate(metadata.get('streams',[]))]
                for group,values in tags:
                    for key,value in values.items():
                        if any(x in key.lower()for x in ('location','gps','coordinate')):
                            coords=parse_location(value)
                            if coords:gps.append(dict(site=entry['gt_site'],latitude=coords[0],longitude=coords[1],source=str(path)+':'+group+'/'+key,evidence_type='MP4_location_tag',camera_position_verified=0))
            cameras.append(dict(site=entry['gt_site'],sidecars=sidecars,video=video))
    write_csv(out/'GPS_candidates.csv',gps,['site','latitude','longitude','source','evidence_type','camera_position_verified'])
    (out/'camera_metadata.json').write_text(json.dumps(cameras,indent=2,default=str)+'\n')
    pine=[r for r in refs if 'pine' in r['street'].lower()]
    stats=dict(cameras_audited=len(cameras),gps_candidates=len(gps),unique_reference_rows=len(refs),pine_named_reference_rows=len(pine),
        physical_track_speeds_calculated=0,calibration_validated=False,new_inference=False)
    (out/'summary.json').write_text(json.dumps(stats,indent=2)+'\n')
    lines=['# Parallel speed readiness audit','',f'Camera sessions audited: {len(cameras)}. Explicit GPS candidates: {len(gps)}.',
        'GPS tags, if found, require matching the camera view. A camera location does not provide road-plane distances or replace landmark calibration.',
        f'Speed reference rows after deduplicating primary A–I tables: {len(refs)}. Rows whose street contains Pine: {len(pine)}.',
        'reference_summary.csv lists measured lengths and reference-speed ranges by street/facility. These are source measurements, not model speeds or matched accuracy.',
        'study_speed_references.csv retains record numbers, source cells and exact-unit recomputation. Arithmetic differences are not detector speed errors.',
        'No Pine-named reference rows means the workbook does not currently provide a matched Pine Hills validation set; an unrecognized street alias cannot be ruled out.',
        'camera_metadata.json includes sidecar clues, readable text previews and available MP4 metadata. sidecars/ stores only bounded small JPEG/CUT files; full videos are not extracted.',
        'No GPS found in sampled sidecars does not prove that the original camera had no GPS or that other files lack location evidence.',
        '', 'Next: inspect any GPS/sidecar clue against the actual camera image, then establish independent ground landmarks and check points. If no location clues exist, physical speed remains pending; lane/count processing can continue independently.',
        'This job performs no inference, model change, arbitrary-distance fitting, upload or communication with external services.']
    (out/'RESULTS.md').write_text('\n'.join(lines)+'\n');print('\n'.join(lines));return stats


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);repo=Path(__file__).resolve().parents[4]
    ap.add_argument('--archive',type=Path,default=Path('/orange/xiangyan/rithika/vision/MioVision_Data.zip'))
    ap.add_argument('--mapping',type=Path,default=repo/'data/video_site_mapping.csv')
    ap.add_argument('--workbook',type=Path,default=repo/'Bike Lane Study Counts/bicyclist speeds.xlsx')
    ap.add_argument('--data-root',type=Path,default=Path('/orange/xiangyan/rithika/vision/pilot_clips'))
    ap.add_argument('--site');ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();run(a.archive,a.mapping,a.workbook,a.data_root,a.out,a.site)
