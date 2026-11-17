import copy
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
from fastapi import HTTPException
from cyclescope.service import repository as repo
from cyclescope.service import main


class RepositoryTests(unittest.TestCase):
    def state(self):
        observations = [dict(frame=i+1, foot_x=10+i/3, foot_y=50, box_w=6, box_h=12, coasted=0) for i in range(91)]
        return dict(meta={'fps':30, 'frames':100}, calibration=dict(image_points=[[0,0],[100,0],[100,100],[0,100],[50,50]],
            world_points_metres=[[0,0],[100,0],[100,100],[0,100],[50,50]], regions=[dict(name='sidewalk',points=[[0,0],[100,0],[100,100],[0,100]])], measurement_source='synthetic'),
            decisions={}, tracks=[dict(id=1,cls='cyclist',deleted=False,source='repository', observations=observations)])

    def test_speed_matches_actual_estimator_and_region(self):
        state=self.state()
        result=repo.analyze(state)
        H,hull=repo.homography(state['calibration'])
        expected=repo.estimate(state['tracks'][0]['observations'],30,H,hull)
        self.assertEqual(result['speeds']['1']['median_mph'],expected['speed_mph'])
        self.assertAlmostEqual(expected['speed_mph'],22.369,places=3)
        self.assertEqual(result['facilities']['1'],'sidewalk')

    def test_legacy_and_single_manual_frame_never_fabricate_speed(self):
        state=self.state();state['tracks'][0].pop('observations');state['tracks'][0]['source']='model'
        self.assertEqual(repo.analyze(state)['speeds'],{})
        state['tracks'][0].update(source='manual',keys={'0':[0,0,10,10]})
        self.assertEqual(repo.analyze(state)['speeds'],{})
        self.assertEqual(len(repo.boxes_from_keys({'0':[0,0,10,10]},30)),1)

    def test_import_keeps_person_vehicle_ids_separate(self):
        base=repo.ROOT/'reports/cluster_returns/20261109/CLEARANCE_PILOT_20261109_175030_116203/colonial_125311_reference'
        log=json.loads((base/'run_log.json').read_text())
        for key in ('tracks_csv','trajectories_csv','vehicle_trajectories_csv'): log[key]=str(base/(key+'.csv'))
        meta,tracks=repo.import_run(log)
        self.assertEqual(len({t['id'] for t in tracks}),len(tracks))
        self.assertEqual(meta['fps'],29.97)
        person=next(t for t in tracks if t['pipeline_stream']=='person')
        self.assertEqual(person['boxes'][0][0],int(person['observations'][0]['frame'])-1)

    def test_degenerate_calibration_rejected(self):
        with self.assertRaises(ValueError): repo.homography(dict(image_points=[[i,0] for i in range(5)],world_points_metres=[[i,0] for i in range(5)]))

    def test_classes_calibration_delete_and_path_guard(self):
        with tempfile.TemporaryDirectory() as temp:
            original=main.DATA;main.DATA=Path(temp)
            try:
                jid='123456abcd';(main.DATA/jid).mkdir()
                state=self.state();state.update(id=jid,status='ready',name='synthetic',tracks=[],analysis={'speeds':{'old':{'median_mph':999}},'events':[]})
                main.save(jid,state)
                self.assertEqual(main.export(jid,'json')['speeds'],{})
                for cls in ('person','car','cyclist','truck','bus','motorcycle'):
                    updated=main.add_track(jid,main.NewTrack(cls=cls,frame=0,box=[1,2,10,20]))
                    self.assertEqual(updated['tracks'][-1]['cls'],cls)
                updated=main.patch_track(jid,1,main.TrackPatch(cls='bus'))
                self.assertEqual(updated['tracks'][0]['cls'],'bus')
                main.set_calibration(jid,main.Calibration(**state['calibration']))
                saved=main.load(jid)['calibration']
                self.assertEqual(len(saved['image_points']),5)
                self.assertEqual(saved['regions'][0]['name'],'sidewalk')
                for invalid in ('..','../123456abcd','/tmp','123'):
                    with self.assertRaises(HTTPException): main.jdir(invalid)
                updated['status']='processing';main.save(jid,updated)
                with self.assertRaises(HTTPException):main.delete_job(jid)
                updated['status']='ready';main.save(jid,updated)
                main.delete_job(jid)
                self.assertFalse((main.DATA/jid).exists())
            finally:main.DATA=original

    def test_no_calibration_no_metrics_and_deletion_changes_counts(self):
        state=self.state();state['calibration']=None
        result=repo.analyze(state)
        self.assertFalse(result['calibrated']);self.assertFalse(result['speeds']);self.assertFalse(result['events'])
        state['tracks'][0]['deleted']=True
        self.assertEqual(repo.analyze(state)['counts'],{})

    def test_dashboard_real_years_and_totals(self):
        result=repo.dashboard()
        self.assertEqual({y for r in result['rows'] for y in r['years']},{str(y) for y in range(2019,2027)})
        self.assertEqual(sum(r['videos'] or 0 for r in result['rows']),9085)
        self.assertAlmostEqual(sum(r['hours'] or 0 for r in result['rows']),9057.33588141,places=6)
        self.assertEqual(sum(r['bicycles'] or 0 for r in result['rows']),5053)
        self.assertTrue(all(r['bicycles'] is None and not r['speeds'] for r in result['rows'] if '2019' not in r['years']))
        self.assertTrue(any('2019' in r['years'] and r['speeds'] for r in result['rows']))
        self.assertTrue(any(s['date']=='2023-05-02' and s['location']=='10th St' for s in result['sessions']))
        alafaya=next(r for r in result['rows'] if 'Alafaya East' in r['study_sites'])
        self.assertEqual(alafaya['bicycles'],245)
        self.assertEqual(sum(alafaya['facilities'].values()),245)

if __name__=='__main__':unittest.main()
