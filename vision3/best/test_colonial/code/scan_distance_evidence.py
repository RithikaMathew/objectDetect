#!/usr/bin/env python3
"""Read-only distance-evidence inventory for XML-XLS and XLSX study workbooks.

Standard-library XML/ZIP parsing preserves source cell addresses and formulas.
A keyword hit is a candidate, not verified scene correspondence or a measurement.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import posixpath
import re
import xml.etree.ElementTree as ET
import zipfile

LEGACY='urn:schemas-microsoft-com:office:spreadsheet'
MAIN='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
REL='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PATTERN=re.compile(r'\b(width|length|distance|feet|foot|metres?|meters?|calibration|latitude|longitude|survey|35\s*ft|30\s*ft)\b',re.I)


def column(n):
    result=''
    while n:n,k=divmod(n-1,26);result=chr(65+k)+result
    return result


def cells(path):
    if path.suffix.lower()=='.xls':
        root=ET.parse(path).getroot();n={'s':LEGACY}
        for sheet in root.findall('s:Worksheet',n):
            row_index=0
            for row in sheet.findall('s:Table/s:Row',n):
                row_index=int(row.get('{'+LEGACY+'}Index',row_index+1));col=0
                for cell in row.findall('s:Cell',n):
                    col=int(cell.get('{'+LEGACY+'}Index',col+1));data=cell.find('s:Data',n)
                    text=''.join(data.itertext()) if data is not None else ''
                    yield sheet.get('{'+LEGACY+'}Name'),column(col)+str(row_index),text,cell.get('{'+LEGACY+'}Formula','')
        return
    with zipfile.ZipFile(path) as archive:
        n={'s':MAIN};shared=[]
        if 'xl/sharedStrings.xml' in archive.namelist():
            shared=[''.join(si.itertext()) for si in ET.fromstring(archive.read('xl/sharedStrings.xml')).findall('s:si',n)]
        mapping={r.get('Id'):r.get('Target') for r in ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))}
        workbook=ET.fromstring(archive.read('xl/workbook.xml'))
        for sheet in workbook.findall('s:sheets/s:sheet',n):
            target=mapping[sheet.get('{'+REL+'}id')]
            target=target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target)
            data=ET.fromstring(archive.read(target))
            for cell in data.findall('.//s:sheetData/s:row/s:c',n):
                value=cell.find('s:v',n);formula=cell.find('s:f',n)
                text=value.text if value is not None and value.text is not None else ''
                if cell.get('t')=='s':text=shared[int(text)]
                if cell.get('t')=='inlineStr':text=''.join(cell.find('s:is',n).itertext())
                yield sheet.get('name'),cell.get('r'),text,formula.text or '' if formula is not None else ''


def scan(directory,out):
    inventory=[];hits=[]
    for path in sorted(directory.iterdir()):
        if path.suffix.lower() not in ('.xls','.xlsx'):continue
        data=list(cells(path))
        media=[]
        if path.suffix=='.xlsx':
            with zipfile.ZipFile(path) as z:media=[p for p in z.namelist() if p.startswith('xl/media/')]
        inventory.append(dict(file=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),sheets=len({r[0] for r in data}),nonempty_cells=sum(bool(r[2] or r[3]) for r in data),embedded_media_files=len(media),status='READ_ALL_CELLS'))
        for sheet,address,value,formula in data:
            if PATTERN.search(str(value)):
                row=int(re.search(r'\d+',address)[0])
                nearby=[dict(cell=a,value=v,formula=f) for s,a,v,f in data if s==sheet and abs(int(re.search(r'\d+',a)[0])-row)<=1 and (v or f)]
                hits.append(dict(file=path.name,sheet=sheet,cell=address,value=value,formula=formula,nearby_cells=nearby,
                                 evidence_status='KEYWORD_CANDIDATE_NOT_VERIFIED_SCENE_DISTANCE'))
    out.mkdir(parents=True,exist_ok=True)
    with (out/'workbook_inventory.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(inventory[0]));w.writeheader();w.writerows(inventory)
    (out/'workbook_distance_candidates.json').write_text(json.dumps(hits,indent=2)+'\n')
    print(json.dumps(dict(workbooks=len(inventory),sheets=sum(r['sheets'] for r in inventory),nonempty_cells=sum(r['nonempty_cells'] for r in inventory),keyword_hits=len(hits),embedded_media_files=sum(r['embedded_media_files'] for r in inventory)),indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();scan(a.directory,a.out)
