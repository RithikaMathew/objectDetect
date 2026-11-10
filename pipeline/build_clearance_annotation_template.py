#!/usr/bin/env python3
"""Build a manual road-edge annotation sheet from a reviewed clearance packet.

The output is intentionally a blank measurement form. Existing automatic box
coordinates and manual cyclist contacts are references only; a reviewer must
enter the visible cyclist-side edges and mark whether the frame is usable.
"""
import argparse
import csv
from pathlib import Path


FIELDS = [
    'clip', 'frame_zero_based', 'clip_seconds', 'source_seconds_inferred',
    'cyclist_id', 'vehicle_id', 'vehicle_status',
    'manual_rear_tire_x', 'manual_rear_tire_y',
    'automatic_box_bottom_x', 'automatic_box_bottom_y',
    'cyclist_near_side_x_px', 'car_cyclist_side_x_px',
    'pixel_clearance_x_px', 'road_plane_clearance_m',
    'pass_interval', 'same_direction', 'occlusion', 'frame_usable',
    'edge_confidence', 'reviewer', 'notes'
]


def read_rows(path):
    with Path(path).open(newline='') as stream:
        return list(csv.DictReader(stream))


def build(packet):
    points = read_rows(packet / 'contact_point_checks.csv')
    encounters = {
        (row['clip'], row['cyclist_id'], row['vehicle_id']): row
        for row in read_rows(packet / 'reviewed_encounters.csv')
    }
    output = []
    for point in points:
        cyclist_id = '1'
        key = (point['clip'], cyclist_id, point['vehicle_id'])
        encounter = encounters.get(key)
        if encounter is None:
            raise ValueError(f'No reviewed encounter for {key}')
        output.append({
            'clip': point['clip'],
            'frame_zero_based': point['frame_zero_based'],
            'clip_seconds': point['clip_seconds'],
            'source_seconds_inferred': point['source_seconds_inferred'],
            'cyclist_id': cyclist_id,
            'vehicle_id': point['vehicle_id'],
            'vehicle_status': point['vehicle_status'],
            'manual_rear_tire_x': point['manual_rear_tire_x'],
            'manual_rear_tire_y': point['manual_rear_tire_y'],
            'automatic_box_bottom_x': point['automatic_box_bottom_x'],
            'automatic_box_bottom_y': point['automatic_box_bottom_y'],
            'cyclist_near_side_x_px': '',
            'car_cyclist_side_x_px': '',
            'pixel_clearance_x_px': '',
            'road_plane_clearance_m': '',
            'pass_interval': encounter['visual_review'],
            'same_direction': '',
            'occlusion': '',
            'frame_usable': '',
            'edge_confidence': '',
            'reviewer': '',
            'notes': '',
        })
    if not output:
        raise ValueError('No contact-point rows found')
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packet', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    rows = build(args.packet.resolve())
    with args.out.resolve().open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f'Wrote {len(rows)} annotation rows to {args.out}')


if __name__ == '__main__':
    main()