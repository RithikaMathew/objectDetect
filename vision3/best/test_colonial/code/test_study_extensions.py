import copy
import csv
import tempfile
from pathlib import Path
import unittest
import numpy as np
from study_batch import inventory,select,build_plan
from map_calibration import fit
from metric_trajectory_speed import estimate
from conflict_zone_review import visits,candidates

ROOT=Path(__file__).resolve().parents[1]

class StudyExtensions(unittest.TestCase):
    def test_inventory_deduplicates_archive_and_flags_multipart_clock(self):
        with tempfile.TemporaryDirectory()as td:
            d=Path(td);prefix='MioVision Data/Bike Lane Study/MioVision Video/BL Test/Standard_SCU8OG_2019-07-10_0000'
            first=prefix+'/Standard_SCU8OG_2019-07-10_0000.001.mp4'
            extra=prefix+'.02/Standard_SCU8OG_2019-07-10_0000.02.001.mp4'
            row=dict(gt_site='Test',date='2019-07-10',example_mp4=first,match_score='1',ambiguous='no',gt_cyclist_count='5')
            with (d/'mapping.csv').open('w',newline='')as f:
                w=csv.DictWriter(f,fieldnames=list(row));w.writeheader();w.writerow(row)
            (d/'list.txt').write_text('12  01-01-2000 00:00   '+first+'\n'+first+'\n'+extra+'\n')
            rows=inventory(d/'mapping.csv',d/'list.txt',d)
            self.assertEqual(len(rows),2);self.assertEqual(sum(bool(r['clock']) for r in rows),1)
            self.assertTrue(all(r['duration_seconds']=='' for r in rows))

    def test_pilot_one_full_hour_not_full_dataset(self):
        row=dict(site='Colonial North',video='/data/Standard_SCU8OG_2019-07-10_0000.013.mp4',archive_path='x',clock='2019-07-10 12:00:00',clock_status='inferred',fps=30,duration_seconds=3600,probe_status='readable_metadata_not_full_decode')
        rows=[row,{**row,'site':'Other'}]
        chosen=select(rows,'pilot');self.assertEqual(len(chosen),1)
        task=build_plan(ROOT,'test',chosen)['tasks'][0]
        self.assertEqual(task['env']['MAX_FRAMES'],'0')
        self.assertEqual(task['env']['DET_VETO_PCT'],'15')
        self.assertEqual(task['env']['BIC_MIN_SEC'],'3')
        self.assertEqual(task['env']['EXPORT_VEHICLE_TRAJECTORIES'],'1')
        self.assertEqual(task['env']['GT_XLS'],'none')
        self.assertEqual(task['env']['CHUNK'],'13')
        self.assertEqual(task['env']['SESSION_START'],'2019-07-10_00:00:00')
        self.assertEqual(task['env']['STREAM_CLIPS'],'0')

    def test_partial_inventory_cannot_submit_as_complete(self):
        row=dict(site='Test',video='x',archive_path='x',clock='',fps='',duration_seconds='',probe_status='missing')
        with self.assertRaises(ValueError):build_plan(ROOT,'test',[row])

    def landmarks(self):
        points=[(100,100),(600,100),(600,400),(100,400),(200,200),(400,300)]
        return [dict(landmark=str(i),role='fit'if i<4 else'check',image_x=x,image_y=y,east_metres=x*.04,north_metres=y*.04,evidence='synthetic known plane')for i,(x,y)in enumerate(points)]

    def test_check_landmarks_not_used_to_fit(self):
        r=self.landmarks();r[-1]['east_metres']+=5
        c=fit(r,[720,480],'Colonial North','2019-07-10','test','synthetic measured plane')
        self.assertLess(c['fitted_landmark_rmse_metres'],1e-5)
        self.assertGreater(c['held_out_landmark_rmse_metres'],3)
        self.assertEqual(len(c['image_points']),4)

    def test_unknown_source_cannot_create_metric_calibration(self):
        with self.assertRaises(ValueError):fit(self.landmarks(),[720,480],'x','date','test','n/a')

    def test_partial_track_speed_does_not_need_full_gate_crossing(self):
        samples=[dict(frame=i+1,foot_x=i*.2,foot_y=5,coasted=0)for i in range(41)]
        hull=np.array([[[0,0]],[[20,0]],[[20,20]],[[0,20]]],np.float32)
        r=estimate(samples,10,np.eye(3),hull)
        self.assertAlmostEqual(r['speed_mph'],4.474,places=3)
        self.assertGreater(r['windows'],0)
        import json
        self.assertEqual(json.loads(r['measurement_frame_intervals']),[[1,41]])

    def test_speed_does_not_bridge_occlusion_or_extrapolate_outside_calibration(self):
        samples=[dict(frame=i,foot_x=i,foot_y=5)for i in [1,2,3,40,41,42]]
        hull=np.array([[[0,0]],[[100,0]],[[100,100]],[[0,100]]],np.float32)
        self.assertEqual(estimate(samples,10,np.eye(3),hull)['speed_mph'],'')
        samples=[dict(frame=i+1,foot_x=200+i,foot_y=5)for i in range(30)]
        self.assertEqual(estimate(samples,10,np.eye(3),hull)['speed_mph'],'')

    def test_conflict_visits_require_entry_exit_and_reject_censoring(self):
        p=[[2,0],[4,0],[4,10],[2,10]]
        samples=[dict(frame=i+1,foot_x=i/10,foot_y=5)for i in range(61)]
        event=visits(samples,p,10);self.assertEqual(len(event),1)
        self.assertAlmostEqual(event[0][0],2);self.assertAlmostEqual(event[0][1],4)
        self.assertEqual(visits(samples[30:],p,10),[])

    def test_point_gap_candidates_not_confirmed_near_misses(self):
        e=[dict(id='person:1',label='BICYCLIST',entry=2,exit=4),dict(id='vehicle:1',label='car',entry=4.4,exit=5)]
        r=candidates(e,1)[0];self.assertAlmostEqual(r['point_zone_gap_seconds'],.4)
        self.assertEqual(r['confirmed_near_miss'],0)
        self.assertEqual(candidates(e,.2),[])

if __name__=='__main__':unittest.main()
