#!/usr/bin/env python3
"""
Parses all per-corridor Miovision .xls (SpreadsheetML) and .xls.xlsx files
in this directory into one clean CSV: raw_counts_extracted.csv

Handles:
- SpreadsheetML's sparse ss:Index attribute (skips blank cells)
- xlsx's real column-letter cell refs (same sparse-cell issue, different mechanism)
- Header row found by content ('Channel' label), not a fixed row number
- Grand-total row found by taking the last row, then walking backward if it
  doesn't look numeric (defensive against trailing stats-block rows like we
  saw in Livingston)
"""
import re
import csv
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

SS_NS = {'ss': 'urn:schemas-microsoft-com:office:spreadsheet'}
XLSX_NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def read_ss_row(row, ns):
    """SpreadsheetML row -> list of values, respecting ss:Index gaps."""
    sparse, max_idx = {}, -1
    next_idx = 0
    for cell in row.findall('ss:Cell', ns):
        idx_attr = cell.get('{urn:schemas-microsoft-com:office:spreadsheet}Index')
        idx = (int(idx_attr) - 1) if idx_attr else next_idx
        data = cell.find('ss:Data', ns)
        val = data.text if data is not None else ''
        sparse[idx] = val
        next_idx = idx + 1
        max_idx = max(max_idx, idx)
    return [sparse.get(i, '') for i in range(max_idx + 1)]


def parse_ss_xls(path):
    """Old-format Miovision .xls (SpreadsheetML). Returns {worksheet_name: [[row...], ...]}"""
    tree = ET.parse(path)
    root = tree.getroot()
    out = {}
    for ws in root.findall('ss:Worksheet', SS_NS):
        name = ws.get('{urn:schemas-microsoft-com:office:spreadsheet}Name')
        table = ws.find('ss:Table', SS_NS)
        if table is None:
            continue
        rows = [read_ss_row(r, SS_NS) for r in table.findall('ss:Row', SS_NS)]
        out[name] = rows
    return out


def col_idx(ref):
    letters = re.match(r'[A-Z]+', ref).group(0)
    idx = 0
    for ch in letters:
        idx = idx * 26 + (ord(ch) - ord('A') + 1)
    return idx - 1


def get_shared_strings(z):
    shared = []
    if 'xl/sharedStrings.xml' in z.namelist():
        root = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in root.findall('m:si', XLSX_NS):
            shared.append(''.join(t.text or '' for t in si.findall('.//m:t', XLSX_NS)))
    return shared


def read_xlsx_row(row, shared):
    sparse, max_idx = {}, -1
    for c in row.findall('m:c', XLSX_NS):
        ref = c.get('r')
        idx = col_idx(ref) if ref else len(sparse)
        v = c.find('m:v', XLSX_NS)
        val = v.text if v is not None else ''
        if c.get('t') == 's' and val != '':
            val = shared[int(val)]
        sparse[idx] = val
        max_idx = max(max_idx, idx)
    return [sparse.get(i, '') for i in range(max_idx + 1)]


def parse_true_xlsx(path):
    """Real xlsx (the two .xls.xlsx outliers). Returns {sheet_name: [[row...],...]}"""
    out = {}
    with zipfile.ZipFile(path) as z:
        shared = get_shared_strings(z)
        wb_root = ET.fromstring(z.read('xl/workbook.xml'))
        sheet_names = [s.get('name') for s in wb_root.findall('.//m:sheet', XLSX_NS)]
        sheet_files = sorted(n for n in z.namelist()
                              if n.startswith('xl/worksheets/sheet') and n.endswith('.xml'))
        for idx, sf in enumerate(sheet_files):
            name = sheet_names[idx] if idx < len(sheet_names) else sf
            root = ET.fromstring(z.read(sf))
            rows = [read_xlsx_row(r, shared) for r in root.findall('.//m:sheetData/m:row', XLSX_NS)]
            out[name] = rows
    return out


def find_header_block(rows):
    """Find Channel row, Direction row, and metric-subheader row (if present)
    by content, not fixed position. Returns (channel_idx, direction_idx,
    metric_idx_or_None, data_start_idx)."""
    channel_idx = None
    for i, row in enumerate(rows[:20]):
        if row and row[0] == 'Channel':
            channel_idx = i
            break
    if channel_idx is None:
        return None
    direction_idx = channel_idx + 1 if (channel_idx + 1 < len(rows) and rows[channel_idx + 1] and rows[channel_idx + 1][0] == 'Direction') else None
    metric_idx = None
    data_start = (direction_idx + 1) if direction_idx is not None else channel_idx + 1
    # a metric-subheader row has no leading label and contains words like
    # 'With'/'Facing'/'Total' rather than a timestamp
    if data_start < len(rows):
        candidate = rows[data_start]
        if candidate and any(kw in (candidate[0] or '') for kw in ('With', 'Facing', 'Total', 'Lane', 'Sidewalk')):
            metric_idx = data_start
            data_start += 1
    return channel_idx, direction_idx, metric_idx, data_start


def find_total_row(rows, data_start):
    """Walk backward from the end until a row looks like a real numeric total
    (first cell blank/None, rest mostly numeric), skipping trailing stats blocks."""
    for i in range(len(rows) - 1, data_start - 1, -1):
        row = rows[i]
        if not row:
            continue
        rest = row[1:] if len(row) > 1 else []
        numeric_count = sum(1 for v in rest if v not in ('', None) and _is_number(v))
        if numeric_count >= max(2, len(rest) // 2):
            return i, row
    return None, None


def _is_number(v):
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False


def process_workbook(path, sheets):
    results = []
    for sheet_name, rows in sheets.items():
        block = find_header_block(rows)
        if block is None:
            results.append({
                'file': path.name, 'worksheet': sheet_name,
                'status': 'NO_CHANNEL_ROW_FOUND', 'channel': '', 'direction': '',
                'metric': '', 'total': ''
            })
            continue
        channel_idx, direction_idx, metric_idx, data_start = block
        channels = rows[channel_idx][1:] if channel_idx is not None else []
        directions = rows[direction_idx][1:] if direction_idx is not None else []
        metrics = rows[metric_idx][1:] if metric_idx is not None else []

        total_idx, total_row = find_total_row(rows, data_start)
        if total_row is None:
            results.append({
                'file': path.name, 'worksheet': sheet_name,
                'status': 'NO_TOTAL_ROW_FOUND', 'channel': '', 'direction': '',
                'metric': '', 'total': ''
            })
            continue
        totals = total_row[1:]

        n = max(len(channels), len(directions), len(metrics), len(totals))
        for i in range(n):
            results.append({
                'file': path.name,
                'worksheet': sheet_name,
                'status': 'ok',
                'channel': channels[i] if i < len(channels) else '',
                'direction': directions[i] if i < len(directions) else '',
                'metric': metrics[i] if i < len(metrics) else '',
                'total': totals[i] if i < len(totals) else '',
            })
    return results


def main():
    folder = Path('.')
    all_results = []
    xls_files = sorted(folder.glob('*.xls'))
    xlsx_files = sorted(folder.glob('*.xls.xlsx'))

    for path in xls_files:
        try:
            sheets = parse_ss_xls(path)
        except ET.ParseError as e:
            all_results.append({'file': path.name, 'worksheet': '', 'status': f'XML_PARSE_ERROR: {e}',
                                 'channel': '', 'direction': '', 'metric': '', 'total': ''})
            continue
        all_results.extend(process_workbook(path, sheets))

    for path in xlsx_files:
        try:
            sheets = parse_true_xlsx(path)
        except Exception as e:
            all_results.append({'file': path.name, 'worksheet': '', 'status': f'XLSX_PARSE_ERROR: {e}',
                                 'channel': '', 'direction': '', 'metric': '', 'total': ''})
            continue
        all_results.extend(process_workbook(path, sheets))

    out_path = 'raw_counts_extracted.csv'
    with open(out_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['file', 'worksheet', 'status', 'channel', 'direction', 'metric', 'total'])
        writer.writeheader()
        writer.writerows(all_results)

    ok = sum(1 for r in all_results if r['status'] == 'ok')
    problems = [r for r in all_results if r['status'] != 'ok']
    print(f"Wrote {len(all_results)} rows to {out_path}")
    print(f"  {ok} ok rows")
    print(f"  {len(problems)} problem rows (need manual check):")
    seen_files = set()
    for r in problems:
        key = (r['file'], r['status'])
        if key not in seen_files:
            seen_files.add(key)
            print(f"    {r['file']}: {r['status']}")

if __name__ == '__main__':
    main()
