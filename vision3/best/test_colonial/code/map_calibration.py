#!/usr/bin/env python3
"""Fit an estimated ground-plane mapping from identified image/map landmarks.

Map-derived distances are estimates, not survey measurements. Check landmarks
must not be used in the fit. No synthetic/blank coordinates are substituted.
"""
import argparse
import csv
import json
from pathlib import Path
import numpy as np
import cv2


def fit(rows,ref_size,site,date,reviewer,source):
    if not reviewer.strip() or source.strip().lower() in ('','n/a','unknown','none'):raise ValueError('Reviewer and actual landmark source required')
    image=[];world=[];roles=[]
    for row in rows:
        if row['role'] not in ('fit','check') or not row.get('landmark') or not row.get('evidence'):raise ValueError('Every landmark needs role, name and matching evidence')
        image.append([float(row['image_x']),float(row['image_y'])]);world.append([float(row['east_metres']),float(row['north_metres'])]);roles.append(row['role'])
    image=np.asarray(image);world=np.asarray(world);mask=np.array(roles)=='fit'
    if mask.sum()<4 or (~mask).sum()<2:raise ValueError('Need at least4fit and2independent check landmarks')
    if not np.isfinite(image).all() or not np.isfinite(world).all():raise ValueError('Finite coordinates required')
    if ((image<0) | (image>=np.asarray(ref_size))).any():raise ValueError('Image landmark outside reference frame')
    if np.linalg.matrix_rank(np.column_stack([image[mask],np.ones(mask.sum())]))<3 or np.linalg.matrix_rank(np.column_stack([world[mask],np.ones(mask.sum())]))<3:raise ValueError('Fit landmarks must not be collinear')
    H,_=cv2.findHomography(image[mask],world[mask],0)
    if H is None or abs(np.linalg.det(H))<1e-12:raise ValueError('Degenerate mapping')
    points=np.column_stack([image,np.ones(len(image))])@H.T
    if (np.abs(points[:,2])<1e-8).any():raise ValueError('Landmark at invalid perspective horizon')
    residual=np.linalg.norm(points[:,:2]/points[:,2,None]-world,axis=1)
    return dict(site=site,recording_date=date,units='metres',ref_size=ref_size,
        measurement_source=source,reviewer=reviewer,image_points=image[mask].tolist(),world_points_metres=world[mask].tolist(),
        check_image_points=image[~mask].tolist(),check_world_points_metres=world[~mask].tolist(),
        held_out_landmark_rmse_metres=float(np.sqrt(np.mean(residual[~mask]**2))),
        fitted_landmark_rmse_metres=float(np.sqrt(np.mean(residual[mask]**2))),
        calibration_status='map_estimate_not_independently_speed_validated',
        limitation='Map accuracy, landmark correspondence, road planarity and lens distortion affect speed. Ground-plane mapping is camera/date specific; check landmarks are not speed validation.',
        landmarks=rows)

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--landmarks',type=Path,required=True)
    ap.add_argument('--ref-size',default='720x480');ap.add_argument('--site',default='Colonial North');ap.add_argument('--date',default='2019-07-10')
    ap.add_argument('--reviewer',required=True);ap.add_argument('--source',required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    with a.landmarks.open()as f:rows=list(csv.DictReader(f))
    data=fit(rows,[int(x)for x in a.ref_size.split('x')],a.site,a.date,a.reviewer,a.source)
    with a.out.open('x')as f:json.dump(data,f,indent=2)
    print('Held-out landmark RMSE (metres):',data['held_out_landmark_rmse_metres']);print(a.out)
