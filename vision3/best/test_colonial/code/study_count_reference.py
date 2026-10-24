#!/usr/bin/env python3
"""Export manual15-minute counts without mixing camera sides or treating blanks as zero."""
import argparse
from collections import Counter
import csv
import datetime as dt
import json
from pathlib import Path
import re
from study_tables import read_xml_xls

TIME=re.compile(r'^\d{1,2}:\d{2} [AP]M$')


def facility(label):
    s=label.lower()
    if 'bike lane'in s:return 'bike_lane'
    if 'sidewalk'in s:return 'sidewalk'
    if 'travel lane'in s or 'road'in s:return 'road'
    if 'path'in s:return 'path'
    return 'unknown'


def side(label):
    m=re.search(r'\b(NB|SB|EB|WB|North|South|East|West)\b',label,re.I)
    return m[1].upper()if m else 'not_specified'


def extract(sheets,start=None,end=None):
    records=[];coverage=[]
    for sheet,rows in sheets.items():
        if sheet not in ('Bicycles','Pedestrians'):continue
        header=next((r for r in rows if r and r[0]=='Channel'),None)
        directions=next((r for r in rows if r and r[0]=='Direction'),[])
        date=next((r[1]for r in rows if r and r[0]=='Start Date'and len(r)>1),None)
        if not header or not date:raise ValueError('Missing channel/date metadata for '+sheet)
        day=dt.datetime.strptime(date,'%m/%d/%Y').date();previous=None;times=[];missing=0;selected=set()
        for raw_index,row in enumerate(rows,1):
            if not row or not TIME.fullmatch(row[0].strip()):continue
            clock=dt.datetime.strptime(row[0].strip(),'%I:%M %p').time()
            if previous is not None and clock<previous:day+=dt.timedelta(days=1)
            when=dt.datetime.combine(day,clock);previous=clock;times.append(when)
            if start and when<start or end and when>=end:continue
            selected.add(when)
            # Only labelled raw channels; derived totals beyond these columns are excluded.
            for column,label in enumerate(header[1:],1):
                if not label.strip():continue
                value=row[column]if column<len(row)else''
                if value=='':count='';status='missing';missing+=1
                else:
                    try:n=float(value)
                    except ValueError:raise ValueError(f'Non-numeric count {sheet} row{raw_index} column{column}')
                    if n<0 or not n.is_integer():raise ValueError('Counts must be nonnegative integers')
                    count=int(n);status='recorded'
                records.append(dict(worksheet=sheet,user_type='cyclist'if sheet=='Bicycles'else'pedestrian',
                    bin_start=when.isoformat(sep=' '),bin_end=(when+dt.timedelta(minutes=15)).isoformat(sep=' '),
                    camera_side_label=side(label),channel_label=label,
                    direction=directions[column]if column<len(directions)else'',facility=facility(label),
                    count=count,status=status,source_row=raw_index,source_column=column+1))
        gaps=sum((b-a).total_seconds()!=900 for a,b in zip(times,times[1:]))
        coverage.append(dict(worksheet=sheet,first_bin=times[0].isoformat(sep=' ')if times else'',last_bin=times[-1].isoformat(sep=' ')if times else'',
            all_time_bins=len(times),selected_time_bins=len(selected),missing_selected_cells=missing,non_15min_steps=gaps,
            channels=json.dumps(header[1:])))
    return records,coverage


def write(path,rows,fields):
    with path.open('w',newline='')as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)


def run(workbook,out,start=None,end=None):
    if start and end and end<=start:raise ValueError('End must be after start')
    rows,coverage=extract(read_xml_xls(workbook),start,end)
    if not rows:raise ValueError('No manual counts in requested interval')
    out.mkdir(parents=True,exist_ok=False)
    write(out/'channel_counts_15min.csv',rows,list(rows[0]));write(out/'reference_coverage.csv',coverage,list(coverage[0]))
    grouped=Counter();missing=Counter()
    for r in rows:
        key=(r['user_type'],r['camera_side_label'],r['facility'])
        if r['status']=='recorded':grouped[key]+=r['count']
        else:missing[key]+=1
    groups=[dict(user_type=u,camera_side_label=s,facility=f,recorded_count=grouped[(u,s,f)],missing_cells=missing[(u,s,f)])for u,s,f in sorted(set(grouped)|set(missing))]
    write(out/'counts_by_user_side_lane.csv',groups,list(groups[0]))
    lines=['# Manual study count reference','',f'Source: {workbook}',f'Interval: {start or "all source bins"} to {end or "end of source"} (end exclusive).',
        'Raw channel counts only. Camera sides remain separate; no comparison with model counts or accuracy is claimed.',
        'A missing channel or empty cell is not zero. Different worksheet coverage is not silently reconciled.',
        '', '| User | Side label | Facility | Recorded count | Missing cells |','|---|---|---|---:|---:|']
    lines += [f"| {r['user_type']} | {r['camera_side_label']} | {r['facility']} | {r['recorded_count']} | {r['missing_cells']} |"for r in groups]
    lines+=['','Reference worksheet coverage:']
    lines += [f"- {r['worksheet']}: {r['all_time_bins']}source bins, {r['selected_time_bins']}selected bins; first{r['first_bin']}, last{r['last_bin']}; channels{r['channels']}."for r in coverage]
    lines+=['','Next: confirm which raw channels correspond to the visible side of the pilot camera, then compare identical covered bins with the model output. Do not sum both sides when the video covers one. These are manual aggregate counts, not per-person boxes, identity truth or measured speeds.']
    (out/'RESULTS.md').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--workbook',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--start',type=dt.datetime.fromisoformat);ap.add_argument('--end',type=dt.datetime.fromisoformat)
    a=ap.parse_args();run(a.workbook,a.out,a.start,a.end)
