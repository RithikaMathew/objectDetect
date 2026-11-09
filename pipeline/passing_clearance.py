"""Measure sampled lateral edge clearance from reviewed metric road footprints.

Input rows share a road-aligned coordinate system: s along road, l across road.
Only simultaneous observations with longitudinal overlap are paired. These are
alongside candidates; direction and completed passing require video review.
"""
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

FIELDS = ['source_id', 'cyclist_id', 'vehicle_id', 'cyclist_facility',
          'min_sampled_clearance_m', 'time_s', 'alongside_samples',
          'status', 'calibration_id']


def calculate(rows, calibration):
    if (calibration.get('units') != 'm'
            or calibration.get('axes') != 'road_aligned'
            or calibration.get('reviewed') is not True
            or not calibration.get('calibration_id')
            or not calibration.get('evidence')):
        raise ValueError('Reviewed road-aligned metric calibration and evidence are required')
    frames = defaultdict(list)
    seen = set()
    for original in rows:
        r = dict(original)
        if not r.get('source_id') or not r.get('track_id'):
            raise ValueError('source_id and track_id are required')
        if r['source_id'] != calibration.get('source_id'):
            raise ValueError('Calibration source does not match observations')
        if r.get('calibration_id') != calibration['calibration_id']:
            raise ValueError('Observation calibration_id does not match calibration')
        if r.get('geometry_reviewed') != 'yes':
            raise ValueError('Every footprint must have geometry_reviewed=yes')
        for k in ('t', 's_min', 's_max', 'l_min', 'l_max'):
            r[k] = float(r[k])
            if not math.isfinite(r[k]):
                raise ValueError('Nonfinite coordinate or timestamp')
        if r['s_min'] >= r['s_max'] or r['l_min'] >= r['l_max']:
            raise ValueError('Footprints must have positive length and width')
        key = (r['source_id'], r['t'], r['track_id'])
        if key in seen:
            raise ValueError('Duplicate track observation at a timestamp')
        seen.add(key)
        frames[key[:2]].append(r)
    pairs = {}
    for (source, t), observations in sorted(frames.items()):
        cyclists = [r for r in observations if r['class'] in ('cyclist', 'bicycle')]
        vehicles = [r for r in observations if r['class'] in ('car', 'bus', 'truck', 'other_vehicle')]
        for c in cyclists:
            for v in vehicles:
                if min(c['s_max'], v['s_max']) <= max(c['s_min'], v['s_min']):
                    continue
                gap = max(0.0, v['l_min'] - c['l_max'], c['l_min'] - v['l_max'])
                key = (source, c['track_id'], v['track_id'])
                if key not in pairs:
                    pairs[key] = dict(source_id=source, cyclist_id=c['track_id'],
                        vehicle_id=v['track_id'], cyclist_facility=c.get('facility', ''),
                        min_sampled_clearance_m=gap, time_s=t, alongside_samples=0,
                        status='alongside_candidate_requires_video_review',
                        calibration_id=calibration['calibration_id'])
                p = pairs[key]
                p['alongside_samples'] += 1
                if gap < p['min_sampled_clearance_m']:
                    p.update(min_sampled_clearance_m=gap, time_s=t)
    return list(pairs.values())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('footprints_csv')
    ap.add_argument('--calibration', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    if Path(args.out).resolve() in (Path(args.footprints_csv).resolve(), Path(args.calibration).resolve()):
        ap.error('Output must differ from input files')
    with open(args.calibration) as f:
        calibration = json.load(f)
    with open(args.footprints_csv, newline='') as f:
        results = calculate(csv.DictReader(f), calibration)
    with open(args.out, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(results)
    print(f'{len(results)} alongside candidate pairs written to {args.out}')


if __name__ == '__main__':
    main()
