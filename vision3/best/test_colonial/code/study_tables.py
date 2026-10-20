"""Read source study tables without changing the workbooks (stdlib only)."""
from pathlib import PurePosixPath
import xml.etree.ElementTree as ET
import zipfile


def read_xlsx(path):
    ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(path) as z:
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            strings=[''.join(t.text or ''for t in s.findall('.//m:t',ns))
                     for s in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns)]
        rel={r.get('Id'):r.get('Target')for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        result={}
        for sheet in ET.fromstring(z.read('xl/workbook.xml')).findall('m:sheets/m:sheet',ns):
            target=rel[sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
            target=target.lstrip('/')if target.startswith('/')else str(PurePosixPath('xl')/target)
            rows=[]
            for row in ET.fromstring(z.read(target)).findall('m:sheetData/m:row',ns):
                cells={}
                for c in row.findall('m:c',ns):
                    value=c.findtext('m:v',default='',namespaces=ns)
                    if c.get('t')=='s' and value:value=strings[int(value)]
                    if c.get('t')=='inlineStr':value=''.join(t.text or ''for t in c.findall('.//m:t',ns))
                    cells[c.get('r')]=value
                rows.append(cells)
            result[sheet.get('name')]=rows
        return result


def read_xml_xls(path):
    ns={'s':'urn:schemas-microsoft-com:office:spreadsheet'};result={}
    for sh in ET.parse(path).getroot().findall('s:Worksheet',ns):
        rows=[]
        for row in sh.findall('s:Table/s:Row',ns):
            vals=[]
            for c in row.findall('s:Cell',ns):
                index=int(c.get('{'+ns['s']+'}Index',len(vals)+1))
                vals+=['']*(index-len(vals)-1)
                vals.append(c.findtext('s:Data',default='',namespaces=ns))
            rows.append(vals)
        result[sh.get('{'+ns['s']+'}Name')]=rows
    return result
