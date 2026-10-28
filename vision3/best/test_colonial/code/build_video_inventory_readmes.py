#!/usr/bin/env python3
"""Write two separate inventory READMEs using verified sources, never file-count hours."""
import argparse
from collections import defaultdict
import csv
from pathlib import Path


def read(path):
    if not path.is_file():return []
    with path.open() as f:return list(csv.DictReader(f))


def first_readme(repo):
    verified=read(repo/'reports/cluster_returns/20261027/video_duration_audit/by_camera.csv')
    source=read(repo/'reports/cluster_returns/20261024/recording_lengths/per_source.csv')
    workbooks=read(repo/'vision3/best/test_colonial/exp_results/study_inventory_20261023/workbook_location_audit.csv')
    references=read(repo/'vision3/best/test_colonial/exp_results/speed_reference_readiness_20261023/all_reference_records.csv')
    years=defaultdict(set)
    for r in source:
        if r['study_date']:years[r['site']].add(r['study_date'][:4])
    lines=['# Bike Lane Study count cameras and Mighk’s speed-reference locations','','This README covers the study/count-workbook collection and the separate human speed-reference dataset. It does not describe all locations in the MioVision ZIP. [Entire archive inventory](MIOVISION_ARCHIVE_INVENTORY_README.md).','','## Cameras represented in the study/count-workbook folder','','41 camera/session labels are represented in the workbook audit. Playback hours below are the measured video lengths for the mapped camera collection, not hours inside the spreadsheets. Labels are dataset names, not verified addresses. A workbook can be speed-focused (for example Baxter); its presence does not imply a nonzero bicycle-count sample.','','| Camera / study label | Recording years | Number of years | Video files | Measured playback hours |','|---|---|---:|---:|---:|']
    for r in verified:
        ys=sorted(years[r['camera']]);lines.append(f"| {r['camera']} | {', '.join(ys) or 'Unknown'} | {len(ys)} | {r['source_files']} | {float(r['exact_total_hours']):.2f} |")
    lines += ['', 'These 1,919 files are the mapped2019study/count-workbook subset; the entire Bike Lane Study archive section can contain additional sessions/files. A summed playback duration does not guarantee uninterrupted wall-clock coverage, especially if footage is occurrence-only. Camera sides are not pooled.', '', '## Locations in Mighk Wilson’s consolidated bicycle-speed workbook', '', 'These are **human stopwatch measurements from half-speed video**, corrected in the workbook. They are not confirmed Miovision-generated speeds. The 375 speed records across 14 reference locations have no linked person/video timestamps. Camera aliases below are candidate mappings; the speed records may come from separate sessions. The associated video years/hours are not verified recording provenance for each speed record.', '', '| Speed-reference location | Speed observations | Study mean mph | Associated camera | Available video years | Video files | Available playback hours |', '|---|---:|---:|---|---|---:|---:|']
    grouped=defaultdict(list)
    for r in references:grouped[r['street']].append(float(r['source_mph']))
    for loc,values in sorted(grouped.items()):
        candidates=[r for r in verified if r['speed_reference_candidate']==loc]
        preferred={'Colonial':'Colonial North','Lee':'Lee Road N'}
        chosen=next((r for r in candidates if r['camera']==preferred.get(loc)),candidates[0] if candidates else None)
        if chosen:
            camera=chosen['camera'];ys=', '.join(sorted(years[camera]));n=chosen['source_files'];hours=f"{float(chosen['exact_total_hours']):.2f}"
        else:camera='No mapped source';ys='Unknown';n='Unknown';hours='Unknown'
        lines.append(f'| {loc} | {len(values)} | {sum(values)/len(values):.2f} | {camera} | {ys} | {n} | {hours} |')
    lines += ['', '**Counts and speed samples differ.** For example, Aloma Path has 191 study bicycles across the full two-day count period, four in the selected 45 minutes, and 26 separate speed observations. The 26 are not a count of all bicycles in its47.99hours of footage. Silver Star has reference speeds but no matched2019source in the present mapping; a same-named site in another ZIP collection would not prove it is the correct camera/session.', '', '[Workbook camera labels](../vision3/best/test_colonial/exp_results/study_inventory_20261023/workbook_location_audit.csv) · [Measured video-hour evidence](../reports/cluster_returns/20261027/video_duration_audit/by_camera.csv) · [Speed records](../vision3/best/test_colonial/exp_results/speed_reference_readiness_20261023/all_reference_records.csv) · [Current model/manual comparison](../manual/README.md).']
    (repo/'docs/BIKE_LANE_STUDY_INVENTORY_README.md').write_text('\n'.join(lines)+'\n')
    return len(workbooks),len(verified)


def second_readme(repo,full):
    cameras=read(full/'camera_years.csv') if full else []
    durations={r['camera']:r for r in read(full/'durations/by_camera.csv')} if full else {}
    combined=[]
    lines=['# Entire MioVision ZIP: camera locations, years, video counts and hours','','Scope: every inventoried video in `MioVision_Data.zip`, including annual collections, Bike Lane Study and Other. [Study/count and Mighk speed-reference inventory](BIKE_LANE_STUDY_INVENTORY_README.md).','']
    if not cameras:
        lines += ['**Full ZIP scan pending.** The archive is on HiPerGator, not available locally. The2019subset’s41cameras and1,919files must not be reported as the entire archive. Camera years/file counts require a full central-directory scan; full playback hours additionally require reading video duration metadata. Unknown values will not be replaced with one-hour-per-file assumptions.']
    else:
        lines += ['Years are taken from video filenames or dated recording sessions, not category labels. Site/view folders and device identifiers are kept distinct; aliases are not automatically merged into physical locations. “Unknown” means no parseable recording date, not zero years.', '', '| Collection | Location / view folder | Device | Recording years | Known year count | Videos | Measured / total files | Total playback hours |', '|---|---|---|---|---:|---:|---|---:|']
        for r in cameras:
            key=r['collection']+' / '+r['site_folder']+' / '+r['device'];d=durations.get(key,{})
            n_years=len([y for y in r['years'].split(';') if y and y!='Unknown'])
            complete=d.get('duration_status')=='COMPLETE';hours=f"{float(d['exact_total_hours']):.2f}" if complete else 'Pending'
            combined.append(dict(collection=r['collection'],site_folder=r['site_folder'],device=r['device'],recording_years=r['years'],known_year_count=n_years,video_files=r['video_files'],measured_video_files=d.get('measured_source_files','0'),total_playback_hours=d.get('exact_total_hours','') if complete else '',duration_status='COMPLETE' if complete else 'PENDING'))
            cells=[r[k].replace('|','\\|') for k in ('collection','site_folder','device','years')]
            lines.append('| '+' | '.join(cells)+f" | {n_years if r['years']!='Unknown' else 'Unknown'} | {r['video_files']} | {d.get('measured_source_files','0')} / {r['video_files']} | {hours} |")
        lines += ['', f"Inventory contains {sum(int(r['video_files']) for r in cameras)} video files across {len(cameras)} site/view/device groups. These groups are not a verified count of unique physical street locations. Unknown-date file counts and category paths are retained in camera_years.csv. Hours are shown only when every video for that group has measured metadata; partial subtotals stay in durations/by_camera.csv. Every duration row is measured or pending, never an estimate from file count."]
    lines += ['', '## Get or refresh the full inventory', '', 'After pushing/pulling code, run directly on HiPerGator for the quick camera/year/count listing:', '', '```bash', 'cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial', 'python code/prepare_full_archive_inventory.py --inventory-only', 'cat exp_results/MIOVISION_FULL_ARCHIVE_INVENTORY/CAMERA_YEARS.md', '```', '', 'Then submit the CPU metadata audit for actual video hours:', '', '```bash', 'mkdir -p logs', 'sbatch code/full_archive_inventory.slurm', '```', '', 'The job reuses successful per-video measurements from the completed2019audit, probes existing extracted originals where available, otherwise extracts only one temporary video at a time. It deletes that temporary copy after measuring. It does not run object detection or permanently extract the entire archive. ZIP decompression may take time. Results save after each file; resubmit the same script to resume if its24hour limit is reached.', '', 'Progress: `cat exp_results/MIOVISION_FULL_ARCHIVE_INVENTORY/durations/RESULTS.md`. Final camera/year table: `exp_results/MIOVISION_FULL_ARCHIVE_INVENTORY/CAMERA_YEARS.md`. To refresh the README from partial or completed measurements: `python code/prepare_full_archive_inventory.py --inventory-only`.', '', 'The script writes both READMEs under the HiPerGator repository’s docs folder. To update local copies, paste `cat exp_results/MIOVISION_FULL_ARCHIVE_INVENTORY/camera_years_hours.csv` (or return camera_years.csv and durations/by_camera.csv); no videos need downloading. The terminal summary can also be pasted.', '', 'Playback hours measure the actual duration of files, not guaranteed continuous elapsed recording time. Occurrence-only footage may omit quiet periods. Device codes can be reused at different sites; they are not GPS coordinates. Separate years with similarly spelled streets are not automatically the same camera view.']
    if combined and full:
        with (full/'camera_years_hours.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(combined[0]),lineterminator='\n');w.writeheader();w.writerows(combined)
    (repo/'docs/MIOVISION_ARCHIVE_INVENTORY_README.md').write_text('\n'.join(lines)+'\n')


def build(repo,full=None):
    first_readme(repo);second_readme(repo,full)
    (repo/'docs/VIDEO_DURATION_README.md').write_text('# Camera locations, recording years and video hours\n\nThe inventories are separated by scope:\n\n1. [Bike Lane Study count cameras and Mighk’s speed-reference locations](BIKE_LANE_STUDY_INVENTORY_README.md):41mapped2019camera/session collections, verified video hours, plus14separate speed-reference locations.\n2. [Entire MioVision ZIP](MIOVISION_ARCHIVE_INVENTORY_README.md):allcollections, site/view/device groups, recording years, video counts and measured playback hours where available. Full-archive scan/measurement status is shown there.\n\nThe completed1,919file/41camera duration audit applies only to the2019study subset. File counts are not hours. Playback hours are not guaranteed continuous recording coverage.\n')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[4]);p.add_argument('--full',type=Path);a=p.parse_args();returned=a.repo/'reports/cluster_returns/20261028/full_archive_inventory';build(a.repo,a.full or (returned if (returned/'camera_years.csv').is_file() else None))
