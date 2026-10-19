#!/usr/bin/env python3
"""
Builds a clean, pipeline-ready ground-truth CSV, one row per file's OWN
site only. Some files embed a duplicate copy of another site's channels
(confirmed: Alafaya East/West, University North/South, S Orange NB/SB) --
those embedded duplicates are dropped, not attributed to the other site,
since that site's own dedicated file already has the authoritative numbers.
"""
import csv
import re
from collections import defaultdict

FNAME_RE = re.compile(
    r'^(?P<site>.+?)_\d+_(?P<month>\d{2})-(?P<day>\d{2})-(?P<year>\d{4})\.xls(\.xlsx)?$'
)

ABBREV_ALIASES = {
    'University N': 'University North',
    'University S': 'University South',
}

def parse_filename(fname):
    m = FNAME_RE.match(fname)
    if not m:
        return None, None
    site = m.group('site').replace('_', ' ').replace('.', '').strip()
    date = f"{m.group('year')}-{m.group('month')}-{m.group('day')}"
    return site, date

def split_metric(metric):
    if not metric:
        return '', ''
    for movement in ('With', 'Facing'):
        if metric.endswith(movement):
            return metric[: -len(movement)].strip(), movement
    return metric, ''

def channel_points_elsewhere(channel_label, file_site, known_sites):
    """True if this channel's label identifies a DIFFERENT site that has
    its own dedicated file (i.e. this row is a duplicate reference, not
    this file's own data)."""
    for abbrev, real in ABBREV_ALIASES.items():
        if channel_label.startswith(abbrev + ' ') and real != file_site:
            return True
    for site in known_sites:
        if len(site.split()) < 2:
            continue  # skip bare direction codes like 'EB', 'North', 'SB'
        if channel_label.startswith(site + ' ') and site != file_site:
            return True
    return False

def main():
    rows_raw = []
    known_sites = set()

    with open('raw_counts_extracted.csv') as f:
        for row in csv.DictReader(f):
            if row['status'] != 'ok' or row['worksheet'] != 'Bicycles' or not row['channel']:
                continue
            file_site, date = parse_filename(row['file'])
            if file_site is None:
                continue
            known_sites.add(file_site)
            rows_raw.append((row, file_site, date))

    rows_out = []
    dropped_duplicates = []
    for row, file_site, date in rows_raw:
        if channel_points_elsewhere(row['channel'], file_site, known_sites):
            dropped_duplicates.append((row['file'], row['channel']))
            continue  # duplicate reference to another site's own file -- skip

        facility, movement = split_metric(row['metric'])
        count = row['total']
        try:
            count = int(float(count)) if count not in ('', None) else None
        except ValueError:
            count = None
        rows_out.append({
            'site': file_site, 'date': date, 'source_file': row['file'],
            'channel_label': row['channel'], 'direction': row['direction'],
            'facility_type': facility, 'movement': movement, 'count': count,
        })

    with open('ground_truth_bicycle_counts.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'site', 'date', 'source_file', 'channel_label', 'direction',
            'facility_type', 'movement', 'count'
        ])
        writer.writeheader()
        writer.writerows(rows_out)

    print(f"Wrote {len(rows_out)} rows ({len(dropped_duplicates)} embedded-duplicate rows dropped)")
    if dropped_duplicates:
        print("\nDropped (duplicate references to another site's own file):")
        for fn, chan in dropped_duplicates:
            print(f"  {fn}: '{chan}'")

    by_site = defaultdict(int)
    for r in rows_out:
        if r['count'] is not None:
            by_site[r['site']] += r['count']
    print("\nPer-site totals:")
    for site, total in sorted(by_site.items(), key=lambda x: -x[1]):
        print(f"  {site:30s} {total}")

if __name__ == '__main__':
    main()
