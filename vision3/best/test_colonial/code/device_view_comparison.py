#!/usr/bin/env python3
"""Export 10th St device samples and check exact-file duplicate candidates."""
import argparse
from collections import defaultdict
import hashlib
import html
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile
from inventory_miovision_archive import classify
from preview_ffmpeg import resolve


def choose(groups):
    devices = ('SCU8OG', 'SCU8PM')
    indexed = {}
    for device in devices:
        indexed[device] = {}
        for info, row in groups[device]:
            # Pair dated session + numbered source chunk, not merely list position.
            match = re.search(r'[._](\d+)\.[^.]+$', info.filename)
            if match:
                key = (row['recording_dates'], int(match.group(1)))
                indexed[device].setdefault(key, []).append((info, row))
    common = sorted(set(indexed[devices[0]]) & set(indexed[devices[1]]))
    common = [k for k in common if all(len(indexed[d][k]) == 1 for d in devices)]
    if not common:
        raise ValueError('No unambiguous common session date/chunk. Inspect archive_contents_summary.py output before choosing samples.')
    key = common[len(common)//2]
    return key, [indexed[d][key][0] for d in devices]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive', type=Path, default=Path('/orange/xiangyan/rithika/vision/MioVision_Data.zip'))
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    exe = resolve()
    a.out.mkdir(parents=True, exist_ok=False)
    groups = defaultdict(list)
    with zipfile.ZipFile(a.archive) as z:
        for info in z.infolist():
            row = classify(info.filename)
            if row and row['site_folder'] == '10th St' and row['device'] in ('SCU8OG', 'SCU8PM'):
                groups[row['device']].append((info, row))
        key, selected = choose(groups)
        candidates = []
        for left, _ in groups['SCU8OG']:
            for right, _ in groups['SCU8PM']:
                if (left.file_size, left.CRC) == (right.file_size, right.CRC):
                    candidates.append(dict(left=left.filename, right=right.filename, bytes=left.file_size, crc32=left.CRC))
        records = []
        for info, row in selected:
            device = row['device']
            print('Extracting selected source: ' + info.filename, flush=True)
            with tempfile.TemporaryDirectory(prefix='device_sample_', dir=a.out) as td:
                if shutil.disk_usage(a.out).free < info.file_size + 512*1024**2:
                    raise RuntimeError('Insufficient temporary disk space')
                source = Path(td)/'source.mp4'
                digest = hashlib.sha256()
                with z.open(info) as inp, source.open('wb') as dest:
                    while True:
                        block = inp.read(8*1024**2)
                        if not block: break
                        digest.update(block); dest.write(block)
                clip = device + '_one_minute.mp4'
                with (a.out/(device+'_ffmpeg.log')).open('w') as log:
                    subprocess.run([exe,'-nostdin','-hide_banner','-loglevel','error','-ss','60','-i',str(source),'-t','60','-map','0:v:0','-an','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-threads','2','-movflags','+faststart',str(a.out/clip)], stdout=log, stderr=subprocess.STDOUT, check=True)
                for second in (0,30):
                    subprocess.run([exe,'-nostdin','-hide_banner','-loglevel','error','-ss',str(second),'-i',str(a.out/clip),'-frames:v','1','-threads','1',str(a.out/(device+'_'+str(second)+'.jpg'))],check=True)
                records.append(dict(device=device, archive_path=info.filename, bytes=info.file_size, sha256=digest.hexdigest(), source_start_seconds=60, requested_duration_seconds=60, clip=clip))
                (a.out/'sources.json').write_text(json.dumps(records,indent=2)+'\n')
        result = dict(paired_session_and_chunk=key, selected_source_files_byte_identical=records[0]['sha256']==records[1]['sha256'], cross_device_same_size_crc_candidates=candidates, scope='CRC/size screening across all 10th St files; SHA256 comparison only for two sampled original files. Different bytes do not rule out re-encoded or overlapping footage. Matching chunks do not prove clock synchronization.')
        (a.out/'duplicate_checks.json').write_text(json.dumps(result,indent=2)+'\n')
        body = '<!doctype html><meta charset="utf-8"><title>10th Street device comparison</title><style>body{font:18px system-ui;margin:24px}video,img{max-width:100%}section{max-width:800px;display:inline-block;vertical-align:top}</style><h1>10th Street: SCU8OG and SCU8PM</h1><p>Same dated session/chunk labels; source seconds 60–120. Verify burned timestamps and landmarks. No resizing; exported clips are re-encoded, so visual comparison does not establish original camera specifications.</p>'
        for r in records:
            body += '<section><h2>'+r['device']+'</h2><video controls src="'+r['clip']+'"></video><p>'+html.escape(r['archive_path'])+'</p><img src="'+r['device']+'_0.jpg"></section>'
        (a.out/'index.html').write_text(body)
        (a.out/'README.md').write_text('# 10th Street sample comparison\n\nOpen index.html, the two MP4s or JPGs. Each requested clip is one minute, starting 60 seconds into its selected original source. sources.json records exact originals. Compare landmarks, view direction, burned clock and moving objects. A different viewpoint establishes different views for these samples, not non-overlap of all recordings. Identical SHA256 establishes byte-identical sampled source files; different SHA256 only establishes different file bytes. All-file size/CRC matches are candidates, not cryptographic proof. Re-encoded duplicates require visual/frame alignment across the relevant footage. Device model and original resolution differences are not established by these exports. Originals unchanged; temporary sources removed.\n')
        print(json.dumps(result,indent=2)); print('Download folder: '+str(a.out),flush=True)

if __name__ == '__main__': main()
