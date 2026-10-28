#!/usr/bin/env python3
"""Measure every inventoried MP4; resume per file, never infer duration from names."""
import argparse
import csv
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile
from preview_ffmpeg import resolve


def write_csv(path, rows):
    tmp = path.with_suffix('.tmp')
    with tmp.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    tmp.replace(path)


def probe(path, executable, ffprobe):
    if ffprobe:
        r = subprocess.run([executable, '-v', 'error', '-show_entries', 'format=duration',
                            '-of', 'json', str(path)], capture_output=True, text=True, timeout=120, check=True)
        seconds = float(json.loads(r.stdout)['format']['duration'])
    else:
        r = subprocess.run([executable, '-hide_banner', '-i', str(path)],
                           capture_output=True, text=True, timeout=120)
        m = re.search(r'Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)', r.stderr)
        if not m:
            raise ValueError('No readable duration: ' + r.stderr[-500:])
        seconds = int(m[1])*3600 + int(m[2])*60 + float(m[3])
    if not math.isfinite(seconds) or seconds <= 0:
        raise ValueError('Nonpositive or invalid duration')
    return seconds


def summaries(rows, cameras):
    result = []
    for camera in cameras:
        source = [r for r in rows if r['site'] == camera['camera']]
        measured = [r for r in source if r.get('audit_status') == 'MEASURED']
        hours = sum(float(r['duration_seconds']) for r in measured)/3600
        result.append(dict(camera=camera['camera'], speed_reference_candidate=camera['speed_reference_candidate'],
                           source_files=len(source), measured_source_files=len(measured),
                           measured_subtotal_hours=hours if measured else '',
                           exact_total_hours=hours if source and len(source) == len(measured) else '',
                           duration_status='COMPLETE' if source and len(source) == len(measured) else 'INCOMPLETE'))
    return result


def main(argv=None):
    repo = Path(__file__).resolve().parents[4]
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inventory-dir', type=Path, default=repo/'reports/cluster_returns/20261024/recording_lengths')
    p.add_argument('--archive', type=Path, default=Path('/orange/xiangyan/rithika/vision/MioVision_Data.zip'))
    p.add_argument('--data-root', type=Path, default=Path('/orange/xiangyan/rithika/vision/pilot_clips'))
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args(argv)
    exe = shutil.which('ffprobe')
    use_probe = bool(exe)
    exe = exe or resolve()
    with (a.inventory_dir/'per_source.csv').open() as f:rows = list(csv.DictReader(f))
    with (a.inventory_dir/'by_camera.csv').open() as f:cameras = list(csv.DictReader(f))
    if len({r['archive_path'] for r in rows}) != len(rows):
        raise ValueError('Duplicate archive paths in inventory')
    a.out.mkdir(parents=True, exist_ok=True)
    saved = a.out/'per_source.csv'
    previous = {}
    if saved.exists():
        with saved.open() as f:previous = {r['archive_path']: r for r in csv.DictReader(f)}
    for r in rows:
        old = previous.get(r['archive_path'], {})
        r.update(duration_seconds=old.get('duration_seconds', ''),
                 audit_status=old.get('audit_status', 'PENDING'), error=old.get('error', ''),
                 duration_reader=old.get('duration_reader', ''), measurement_source=old.get('measurement_source', ''))
    archive = None
    try:
        for i, row in enumerate(rows):
            if row['audit_status'] == 'MEASURED':
                continue
            try:
                member = Path(row['archive_path'])
                if member.is_absolute() or '..' in member.parts:
                    raise ValueError('Unsafe archive path')
                local = a.data_root/member
                with tempfile.TemporaryDirectory(prefix='duration_', dir=str(a.out)) as scratch:
                    if local.is_file():
                        source = local
                        origin = 'extracted_original'
                    else:
                        if archive is None:
                            archive = zipfile.ZipFile(a.archive)
                        info = archive.getinfo(row['archive_path'])
                        if shutil.disk_usage(a.out).free < info.file_size + 1024**3:
                            raise RuntimeError('Insufficient scratch space for one source plus 1 GiB reserve')
                        source = Path(scratch)/'source.mp4'
                        with archive.open(info) as inp, source.open('wb') as dest:
                            shutil.copyfileobj(inp, dest, 8*1024*1024)
                        origin = 'archive_original'
                    seconds = probe(source, exe, use_probe)
                row.update(duration_seconds=seconds, audit_status='MEASURED', error='',
                           duration_reader='ffprobe' if use_probe else 'ffmpeg_header_0.01s', measurement_source=origin)
            except Exception as error:
                row.update(duration_seconds='', audit_status='ERROR', error=str(error))
            write_csv(saved, rows)
            totals = summaries(rows, cameras)
            write_csv(a.out/'by_camera.csv', totals)
            complete = sum(r['duration_status'] == 'COMPLETE' for r in totals)
            (a.out/'RESULTS.md').write_text(
                '# Original-video duration audit\n\n'
                f'Measured {sum(r["audit_status"] == "MEASURED" for r in rows)}/{len(rows)} files; '
                f'{complete}/{len(totals)} camera collections complete.\n\n'
                'by_camera.csv gives total hours only when every inventoried file for that camera was measured. '
                'Incomplete totals remain blank; measured subtotals are not full totals. '
                'These are summed playback hours, not proof of gap-free coverage or distinct synchronized camera hours. '
                'No inference or speed calculation. One temporary archive member at a time is deleted after probing. '
                'Rerunning the same command resumes successful measurements and retries failures.\n')
            print(f'{i+1}/{len(rows)} {row["site"]}: {row["audit_status"]} {row["error"]}', flush=True)
    finally:
        if archive is not None:
            archive.close()


if __name__ == '__main__':
    main()
