#!/usr/bin/env python3
"""Build an evidence packet for visually selected returned Colonial passes.

Reviewed car IDs and frame times are explicit human/assistant visual selections,
not a new passing detector. Green points interpolate the existing rear-tire
clicks, only inside their time range. Boxes do not claim 3-D vehicle footprints.
"""
import argparse
import csv
import html
import json
from pathlib import Path
import cv2
import numpy as np
from clearance_metrics import prepare, pair_metrics

REPO=Path(__file__).resolve().parents[4]
CASES=[dict(key='colonial_124020',car='9',name='White SUV pass',times=[13.0,13.3,13.6],
            observed='same_direction_pass_visible',reason='Visible vehicle overtakes cyclist; ground-side tire and body edges too blurred for defensible edge measurement'),
       dict(key='colonial_125311',car=None,name='Middle cyclist: comparison',times=[13.,14.5,15.5],
            observed='no_adjacent_pass_in_reviewed_click_sequence',reason='No nearby passing car in the reviewed cyclist click interval; not a whole-site absence claim'),
       dict(key='colonial_125350',car='18',name='Dark car pass',times=[14.4,14.8,15.0],
            observed='same_direction_pass_visible',reason='Visible vehicle overtakes cyclist; dark near-side tire/body boundary and perspective prevent verified edge clearance')]


def read(path):
    with Path(path).open(newline='') as f:return list(csv.DictReader(f))


def write(path,rows):
    with Path(path).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def build(batch,out,repo=REPO):
    out.mkdir(parents=True,exist_ok=False)
    plan=json.loads((batch/'manifest.json').read_text())
    ledger=[];points=[];diagnostics=[];cards=[]
    for case in CASES:
        task=next(t for t in plan['tasks'] if t['key']==case['key']+'_reference')
        folder=batch/task['key'];log=json.loads((folder/'run_log.json').read_text());fps=log['fps']
        g=json.loads((folder/'geometry.json').read_text())
        cyclists=read(folder/'trajectories_csv.csv');cars=read(folder/'vehicle_trajectories_csv.csv')
        labels={r['track_id']:r for r in read(folder/'tracks_csv.csv')}
        paths=prepare(cyclists+cars,g['H'],g['hull'],fps,labels)
        clicks=json.loads((repo/task['selection_evidence']).read_text())['observations']
        clicks=sorted([r for r in clicks if task['start_s']<=r['source_seconds']<=task['start_s']+30],key=lambda r:r['source_seconds'])
        ts=np.array([r['source_seconds']-task['start_s'] for r in clicks])
        if case['car'] is not None:
            r=pair_metrics(paths[('cyclist','1')],paths[('car',case['car'])],'car',np.array(g['road_axis']),g['H'],strict=False)
            if r is None:raise ValueError('Reviewed pair lacks diagnostic motion')
            diagnostics.append(dict(clip=case['key'],cyclist_id='1',vehicle_id=case['car'],
                visual_pass_status=case['observed'],automatic_alongside_samples=r['alongside_samples'],
                automatic_min_center_distance_m=r['min_center_distance_m'],
                automatic_min_lateral_clearance_m=r['min_sampled_clearance_m'],
                interpretation='unsupported_model_diagnostics_not_physical_measurements'))
        cap=cv2.VideoCapture(str(batch/'inputs'/(case['key']+'.mp4')));images=[]
        for seconds in case['times']:
            fi=round(seconds*fps);cap.set(cv2.CAP_PROP_POS_FRAMES,fi);ok,image=cap.read()
            if not ok:raise ValueError('Cannot read selected frame')
            seconds=fi/fps
            if not ts[0]<=seconds<=ts[-1]:raise ValueError('Selected frame outside manual click interval')
            manual=np.array([np.interp(seconds,ts,[r['x'] for r in clicks]),np.interp(seconds,ts,[r['y'] for r in clicks])])
            point=min(paths[('cyclist','1')],key=lambda r:abs(r['frame']-(fi+1)))
            auto=point['pixel']
            cv2.circle(image,tuple(np.round(manual).astype(int)),5,(0,255,0),2)
            cv2.circle(image,tuple(np.round(auto).astype(int)),5,(0,255,255),2)
            cv2.line(image,tuple(np.round(manual).astype(int)),tuple(np.round(auto).astype(int)),(0,255,255),1)
            vehicle_status='no_reviewed_car'
            if case['car']:
                observations=paths[('car',case['car'])]
                car=min(observations,key=lambda r:abs(r['frame']-(fi+1)))
                if abs(car['frame']-(fi+1))<=2:
                    x,y=car['pixel'];w,h=car['box_w'],car['box_h']
                    cv2.rectangle(image,(round(x-w/2),round(y-h)),(round(x+w/2),round(y)),(255,180,0),2)
                    cv2.putText(image,'car '+case['car']+' BOX ONLY',(round(x-w/2),max(40,round(y-h)-4)),cv2.FONT_HERSHEY_SIMPLEX,.38,(255,180,0),1)
                    vehicle_status='box_visible_not_ground_footprint'
                else:vehicle_status='no_nearby_observed_car_sample'
            cv2.putText(image,'GREEN: prior rear-tire click | YELLOW: automatic box bottom',(7,17),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,255,255),1)
            filename=f"{case['key']}_{fi:04d}_review.jpg"
            cv2.imwrite(str(out/filename),image);images.append(filename)
            points.append(dict(clip=case['key'],frame_zero_based=fi,clip_seconds=seconds,
                source_seconds_inferred=task['start_s']+seconds,
                manual_rear_tire_x=manual[0],manual_rear_tire_y=manual[1],
                automatic_box_bottom_x=auto[0],automatic_box_bottom_y=auto[1],
                offset_pixels=float(np.linalg.norm(manual-auto)),vehicle_id=case['car'] or '',vehicle_status=vehicle_status,
                annotation='rear_tire_interpolated_between_existing_clicks_no_extrapolation'))
        cap.release()
        ledger.append(dict(clip=case['key'],cyclist_id='1',vehicle_id=case['car'] or '',visual_review=case['observed'],
            reviewed_clip_start_s=case['times'][0],reviewed_clip_end_s=case['times'][-1],
            primary_review='0.5s contact sheets over +11 to +16.5s plus finer selected passing frames',
            measured_clearance_m='',measurement_status='not_reportable_as_physical_clearance',
            near_miss_status='not_established',reason=case['reason'],
            calibration_support='all_cyclist_contacts_outside_car_hull',reviewer='Codex_visual_frame_review'))
        cards.append(dict(title=case['name'],key=case['key'],images=images,reason=case['reason']))
    ledger.append(dict(clip='colonial_125350',cyclist_id='1',vehicle_id='21_sensitive',visual_review='false_vehicle_on_cyclist_wheel',
        reviewed_clip_start_s=15.5488822155,reviewed_clip_end_s=15.6823490157,
        primary_review='saved snapshot c1_v21.jpg and five-frame track span',measured_clearance_m='',
        measurement_status='exclude_false_object',near_miss_status='false_alarm_not_separate_vehicle',
        reason='Supposed car detection encloses cyclist front wheel; no separate car there',
        calibration_support='irrelevant_false_object',reviewer='Codex_visual_frame_review'))
    write(out/'reviewed_encounters.csv',ledger);write(out/'contact_point_checks.csv',points)
    write(out/'reviewed_pair_model_diagnostics.csv',diagnostics)
    # Relative links keep the page usable within the repository; copied images
    # and CSVs are self-contained. Original videos remain at the batch path.
    import os
    source_rel=os.path.relpath(batch,out)
    page=['<!doctype html><meta charset="utf-8"><title>Reviewed Colonial passes</title>',
        '<style>body{font:17px system-ui;max-width:1100px;margin:28px auto;line-height:1.5}img{max-width:100%;width:350px}video{max-width:720px;width:100%}section{border-top:1px solid #bbb;padding:20px 0}.note{background:#fff3cd;padding:15px}</style>',
        '<h1>What the local review found</h1><p class="note"><b>Two clear car passes in the reviewed cyclist sequences. No confirmed near miss. No passing gap is ready to report in meters.</b></p>',
        '<p>Green circles show your earlier rear-tire clicks, interpolated to each frame. Yellow circles show automatic box-bottom points. Blue rectangles locate the car; they do not identify its ground footprint or nearest physical side.</p>']
    for card in cards:
        page.extend(['<section><h2>'+html.escape(card['title'])+'</h2><p>'+html.escape(card['reason'])+'</p>'])
        page.extend(f'<a href="{name}"><img src="{name}"></a>' for name in card['images'])
        page.append(f'<p><video controls preload="metadata" src="{html.escape(source_rel)}/inputs/{card["key"]}.mp4"></video></p></section>')
    page.append('<h2>Why no usable meter measurement?</h2><p>The cyclist and car contact points are different from box centers, the vehicle side/wheel contacts are blurry, and the learned road calibration has no support at the cyclist positions. Earlier manual speeds use the same calibration, so they do not independently fix lateral scale. The automatic alongside check also rejected both visually reviewed passing pairs. Repeated model variations cannot validate that geometry.</p>')
    page.append('<p>The separate zero-gap alarm is a car label on the bicycle wheel. It is excluded as a false object. Visual review establishes that these two cars pass the cyclists; it does not establish validated near-miss thresholds or absence of all conflicts.</p>')
    (out/'review.html').write_text('\n'.join(page))
    (out/'RESULTS.md').write_text('''# Local review: plain-language result

- Two clear same-direction car passes are visible in the reviewed cyclist sequences: white SUV in the first clip and dark car in the third.
- No nearby car passes in the reviewed manual-click interval of the middle clip. This is a comparison sequence, not a claim about the entire site or all 30 seconds.
- The sole zero-clearance/TTC/PET alarm was a car detection on a bicycle wheel. It is a false object.
- **No physical passing clearance in meters is ready to report.** Existing values remain exploratory model estimates.

[Open the illustrated review](review.html). Green = existing manual rear-tire points; yellow = automatic bottom-center; blue = car detection box. Original annotation files and cluster returns were not changed.

## What was checked

The review inspected half-second frame sequences from +11.0 to +16.5 seconds of each short clip, finer passing frames around +13 seconds (white SUV) / +14.8 seconds (dark car), and enlarged vehicle crops. This is sampled visual review, not a full-frame exhaustive safety adjudication. Before/after frames show the two overtakes. The middle interval has no nearby passing vehicle. Near-miss severity is not established from these observations.

The previously annotated reference points (intended rear-tire contacts) were interpolated only between existing clicks and placed on exact decoded frames. Some green markers do not land precisely on the visible pavement contact in these new frames; contact choice and alignment remain uncertain, so they are a reference for comparison, not verified ground truth. A yellow box-bottom point can sit ahead of/below the clicked rear contact; it must not silently replace that tire point when estimating a physical gap. See contact_point_checks.csv for actual image offsets.

Both reviewed passing cars are in the reference detector outputs: white SUV track 9, dark car track 18. The current modeled alongside gate returns zero alongside samples for each, even though their passing sequence is visible. That is a geometry/footprint failure, not proof that the pass did not occur. reviewed_pair_model_diagnostics.csv preserves these outputs as diagnostics, not measurements.

Vehicle crops are too blurry to mark reliable near-side tire/ground/body edges. All cyclist tire points also lie outside the car-calibration support region. Membership outside the hull alone does not prove the mapping wrong, but it makes transfer unvalidated. A bounding rectangle is not the physical car side; assumed dimensions and projected contact centers do not resolve it. The manual and automatic speeds use the same learned matrix, so matching speeds cannot independently validate clearance geometry.

## What is usable

- Visual evidence that two actual cars pass the cyclists in these selected sequences.
- The prior manual cyclist contacts as a reference for cyclist image position and the existing exploratory speed comparison.
- The specific bicycle-wheel false detection as an exclusion with image evidence.

## What is not usable yet

- Meter-valued passing gaps as measured physical clearances.
- Automated near-miss counts or false-alarm rates for the site.
- Comparing Kalman/RTS output counts as proof of improved safety accuracy.

## Next action

No additional GPU processing is indicated. Within the current files, the defensible deliverable is this reviewed passing-event evidence and diagnostic report. To turn it into physical clearance, a trusted lateral road-plane scale/geometry and visible or otherwise defensible car/cyclist outer edges are still needed. The current files do not establish those. Do not substitute the old speed mean or nominal lane/car widths as ground truth.
''')
    (out/'provenance.json').write_text(json.dumps(dict(batch=str(batch.resolve()),manual_sources=[t['selection_evidence'] for t in plan['tasks'] if t['detector']=='reference'],
        selected_cases=CASES,geometry='existing_learned_H_no_refit',new_gpu_inference=False,
        method='visual_sampled_review_and_interpolation_of_prior_manual_points'),indent=2)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();build(a.batch.resolve(),a.out.resolve())


if __name__=='__main__':main()
