"""Check physical projection and synthetic calibration independently of study speeds."""
import unittest
import numpy as np
from speed_research import geometry,height_residual,fit_height,university_manual_comparison,measurement_times,CarAssociation,usable_car_records

class CalibrationTests(unittest.TestCase):
    def observations(self):
        size=[720,480];params=[800.,.8,.02,7.]
        n,K,H=geometry(params,size)
        inv=np.linalg.inv(K)
        e1=np.array([1.,0,0]);e1-=n*(n@e1);e1/=np.linalg.norm(e1);e2=np.cross(n,e1)
        feet=[];heads=[]
        for x in np.linspace(-3,3,6):
            for y in np.linspace(-12,-3,5):
                foot=7*n+x*e1+y*e2;head=foot-1.7*n
                f=inv@foot;h=inv@head
                feet.append(f/f[2]);heads.append(h/h[2])
        return params,np.array(feet),np.array(heads),size

    def test_projection_physical_scale(self):
        params,feet,heads,size=self.observations()
        self.assertLess(np.max(np.abs(height_residual(params,feet,heads,size,1.7))),1e-10)

    def test_known_geometry_recovery(self):
        params,feet,heads,size=self.observations()
        H,info=fit_height(feet,heads,size)
        self.assertTrue(info['geometry_check_passed'])
        self.assertAlmostEqual(info['parameters'][3],7,places=2)

    def test_insufficient_independent_input(self):
        params,feet,heads,size=self.observations()
        with self.assertRaises(ValueError):fit_height(feet[:1],heads[:1],size)

class ManualComparisonTests(unittest.TestCase):
    def config(self):
        return dict(user_type='cyclist',site='University',facility='Sidewalk',subject='test',distance_feet=55.17,a_before_clip_seconds=422.5,a_after_clip_seconds=423.,b_before_clip_seconds=427.25,b_after_clip_seconds=427.5)

    def test_units_and_same_location_facility(self):
        refs=[dict(street='University',facility='Sidewalk',source_mph='9'),dict(street='University',facility='Sidewalk',source_mph='11'),dict(street='Colonial',facility='Sidewalk',source_mph='100')]
        r=university_manual_comparison(self.config(),refs)
        self.assertAlmostEqual(r['speed_mph'],8.13316953317)
        self.assertEqual(r['reference_cyclists'],2)
        self.assertEqual(r['reference_mean_mph'],10)
        self.assertLess(r['timing_only_low_mph'],r['speed_mph'])
        self.assertGreater(r['timing_only_high_mph'],r['speed_mph'])

    def test_wrong_user_type_rejected(self):
        c=self.config();c['user_type']='pedestrian'
        with self.assertRaises(ValueError):university_manual_comparison(c,[])

    def test_crossing_overlap_rejected(self):
        c=self.config();c['b_before_clip_seconds']=422.8
        with self.assertRaises(ValueError):university_manual_comparison(c,[])

class MeasurementTimeTests(unittest.TestCase):
    def test_disjoint_measurement_intervals_keep_actual_clocks(self):
        from datetime import datetime
        import json
        samples=[dict(frame=f,time=t) for f,t in [(1,'12:45:01'),(21,'12:45:03'),(101,'12:45:11'),(121,'12:45:13')]]
        result=measurement_times(dict(measurement_frame_intervals='[[1,21],[101,121]]'),samples,datetime(2019,7,10,12,45))
        intervals=json.loads(result['measurement_intervals'])
        self.assertEqual(len(intervals),2)
        self.assertEqual(intervals[0]['clip_start_seconds'],1)
        self.assertEqual(intervals[1]['clip_start_seconds'],11)
        self.assertEqual(result['measurement_end'],'2019-07-10 12:45:13')

    def test_unavailable_speed_has_no_fake_measurement_time(self):
        from datetime import datetime
        r=measurement_times(dict(measurement_frame_intervals='[]'),[],datetime(2019,7,10,12,45))
        self.assertEqual(r['measurement_start'],'')
        self.assertEqual(r['measurement_intervals'],'[]')

class CarTrackingTests(unittest.TestCase):
    def test_velocity_prediction_keeps_id_after_larger_step(self):
        t=CarAssociation(max_gap_frames=9)
        box=np.array([0.,0,20,20])
        first=t.update(0,[box])[0]
        self.assertEqual(t.update(3,[box+[6,0,6,0]])[0],first)
        # Twelve-pixel displacement across six frames is predicted from prior motion.
        self.assertEqual(t.update(9,[box+[18,0,18,0]])[0],first)

    def test_assignments_are_one_to_one_and_expire(self):
        t=CarAssociation(max_gap_frames=9);box=np.array([0.,0,20,20])
        first=t.update(0,[box])[0]
        ids=t.update(3,[box+[2,0,2,0],box+[3,0,3,0]])
        self.assertEqual(len(set(ids)),2)
        self.assertNotEqual(t.update(30,[box])[0],first)

    def test_static_car_not_accepted_as_scale_motion_track(self):
        mask=np.ones((14,14));box=np.array([0.,0,20,20])
        self.assertEqual(usable_car_records({1:[(i,box,mask) for i in range(5)]}),[])
        r=usable_car_records({1:[(i,box+[i*10,0,i*10,0],mask) for i in range(5)]})
        self.assertEqual(len(r),5)
        self.assertTrue(np.isfinite(r[0][-1]).all())

class ReportReuseTests(unittest.TestCase):
    def test_relative_root_rebuild_does_not_load_models(self):
        import json,subprocess,sys,tempfile
        from pathlib import Path
        folder=Path(__file__).resolve().parent;root=folder.parent
        with tempfile.TemporaryDirectory() as td:
            d=Path(td);prior=d/'previous';prior.mkdir()
            result=subprocess.run([sys.executable,str(folder/'speed_research.py'),'--root','.','--reuse-calibration',str(prior),'--out',str(d/'report')],cwd=root,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            statuses=json.loads((d/'report/method_status.json').read_text())
            self.assertEqual(next(r['state'] for r in statuses if r['method']=='university_manual_map_gates'),'CALCULATED_FROM_SAVED_TIMING')

if __name__=='__main__':unittest.main()
