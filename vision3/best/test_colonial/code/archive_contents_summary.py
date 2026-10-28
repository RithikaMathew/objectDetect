#!/usr/bin/env python3
"""Read every archive entry name/type and small text files; no video extraction/inference."""
import argparse
from collections import Counter,defaultdict
import csv
import json
from pathlib import Path,PurePosixPath
import zipfile
from inventory_miovision_archive import classify


def write(path,rows,fields):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive',type=Path,default=Path('/orange/xiangyan/rithika/vision/MioVision_Data.zip'))
    p.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]/'exp_results/MIOVISION_ARCHIVE_CONTENTS')
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    counts=Counter();allfiles=[];smalltexts=[];ten=defaultdict(list)
    with zipfile.ZipFile(a.archive) as z:
        for info in z.infolist():
            if info.is_dir():continue
            ext=PurePosixPath(info.filename).suffix.lower() or '(no extension)';counts[ext]+=1
            allfiles.append(dict(archive_path=info.filename,extension=ext,bytes=info.file_size,compressed_bytes=info.compress_size))
            r=classify(info.filename)
            if r and r['site_folder']=='10th St':ten[r['device']].append(r)
            if ext=='.txt' and info.file_size<=8192:
                raw=z.read(info);encoding='utf-16' if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig'
                smalltexts.append(dict(archive_path=info.filename,bytes=info.file_size,content=raw.decode(encoding,errors='replace')))
    write(a.out/'all_files.csv',allfiles,['archive_path','extension','bytes','compressed_bytes'])
    write(a.out/'file_types.csv',[dict(extension=k,files=v) for k,v in sorted(counts.items())],['extension','files'])
    (a.out/'small_text_contents.json').write_text(json.dumps(smalltexts,indent=2)+'\n')
    summary=[]
    for device,rows in sorted(ten.items()):
        summary.append(dict(device=device,videos=len(rows),recording_session_dates=sorted({d for r in rows for d in r['recording_dates'].split(';') if d}),session_directories=sorted({r['session_path'] for r in rows}),first_video_filename=min(r['archive_path'] for r in rows),last_video_filename=max(r['archive_path'] for r in rows)))
    (a.out/'10th_st_sources.json').write_text(json.dumps(summary,indent=2)+'\n')
    print('ALL ZIP FILE TYPES');print(json.dumps(dict(sorted(counts.items())),indent=2))
    print('\n10TH STREET RECORDING SESSIONS');print(json.dumps(summary,indent=2))
    print('\nSMALL TEXT FILE CONTENTS');print(json.dumps(smalltexts,indent=2))
    print('\nSaved full file list: '+str(a.out/'all_files.csv'))
    print('File types and text content do not independently establish device model, viewing angle, original recording continuity or native speed results.')

if __name__=='__main__':main()
