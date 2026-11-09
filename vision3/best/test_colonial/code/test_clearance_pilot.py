"""Analytic geometry and failure-path checks; no GPU/model downloads."""
import csv
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from clearance_metrics import (collision_ttc, closest_approach, pet_cells,
    local_motion, pair_metrics, prepare, road_axis, scenarios)
import clearance_pilot as pilot


def path(vx=2., vy=0., x=0., y=0., inside=True, n=91):
    return [dict(frame=i+1,t=i/30,xy=np.array([x+vx*i/30,y+vy*i/30]),
        pixel=np.array([x+vx*i/30,y+vy*i/30]),inside=inside,box_w=.8,box_h=1.8,
        facility='bike_lane',counted='1',identity_status='candidate') for i in range(n)]


class MetricsTests(unittest.TestCase):
    def test_swept_collision_requires_lateral_overlap(self):
        self.assertIsNone(collision_ttc([10,4],[-5,0],[3,1.3]))
        self.assertAlmostEqual(collision_ttc([10,0],[-5,0],[3,1.3]),1.4)
        self.assertEqual(collision_ttc([0,0],[0,0],[3,1.3]),0)
        self.assertIsNone(collision_ttc([10,0],[5,0],[3,1.3]))
        self.assertIsNone(collision_ttc([10,0],[-1,0],[3,1.3]))

    def test_closest_approach(self):
        t,d=closest_approach(np.array([10.,4.]),np.array([-5.,0.]))
        self.assertEqual(t,2);self.assertEqual(d,4)

    def test_known_pass_edge_gap_and_order_reversal(self):
        # Vehicle goes from 6m behind to 6m ahead, 3m laterally apart.
        r=pair_metrics(path(vx=2),path(vx=6,x=-6,y=3),'car',np.array([1.,0.]),np.eye(3))
        self.assertAlmostEqual(r['min_sampled_clearance_m'],1.7,places=6)
        self.assertIsNone(r['min_collision_ttc_s'])
        self.assertEqual(r['observed_overtake_candidate'],1)
        self.assertIsNone(r['sampled_occupancy_pet_s'])

    def test_support_transfer_is_explicit(self):
        self.assertIsNone(pair_metrics(path(inside=False),path(y=3),'car',np.array([1.,0.]),np.eye(3)))
        self.assertIsNotNone(pair_metrics(path(inside=False),path(y=3),'car',np.array([1.,0.]),np.eye(3),strict=False))

    def test_motion_no_bridge_across_gap(self):
        samples=path(n=10)+[{**r,'frame':r['frame']+100,'t':r['t']+10} for r in path(n=10)]
        motion=local_motion(samples,1.)
        for r in motion.values():np.testing.assert_allclose(r['velocity'],[2,0],atol=1e-10)

    def test_pet_requires_shared_space_not_just_close_times(self):
        def obs(t,x,y):return {1:dict(t=t,xy=np.array([x,y]))}
        self.assertIsNone(pet_cells(obs(0,0,0),obs(.1,10,0),((.1,.1),(.1,.1)),np.eye(2)))
        self.assertAlmostEqual(pet_cells(obs(0,0,0),obs(1.25,0,0),((.1,.1),(.1,.1)),np.eye(2)),1.25)
        self.assertEqual(pet_cells(obs(0,0,0),obs(0,0,0),((.1,.1),(.1,.1)),np.eye(2)),0)

    def test_prepare_filters_coasted_and_retains_rejected_candidates(self):
        row=dict(track_id='1',frame='1',foot_x='1',foot_y='1',box_w='1',box_h='2',coasted='0',label='PEDESTRIAN')
        hull=np.array([[0,0],[10,0],[10,10],[0,10]])
        labels={'1':dict(det_label='cyclist',counted='0',facility='sidewalk')}
        result=prepare([row,{**row,'frame':'2','coasted':'1'}],np.eye(3),hull,30,labels)
        self.assertEqual(len(result[('cyclist','1')]),1)
        self.assertEqual(result[('cyclist','1')][0]['counted'],'0')

    def test_road_axis_and_variations(self):
        a=road_axis({('car','1'):path(),('car','2'):path(vx=-2)})
        np.testing.assert_allclose(a,[1,0])
        self.assertEqual(len(list(scenarios())),12)


class WorkflowTests(unittest.TestCase):
    def test_no_gpu_needed_for_help_or_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);(out/'manifest.json').write_text(json.dumps(dict(tasks=[dict(key='a',clip_key='clip')])) )
            pilot.report(out)
            self.assertIn('0/1',(out/'RESULTS.md').read_text())
            self.assertIn('NO_FINAL_STATUS',(out/'task_status.csv').read_text())
            (out/'review_labels.csv').write_text('retain user edits\n')
            pilot.report(out)
            self.assertEqual((out/'review_labels.csv').read_text(),'retain user edits\n')

    def test_inference_exports_and_env(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);task=dict(key='case',clip_key='clip',start_s=3179,detector='reference');(out/'case').mkdir()
            files={}
            for key in ('tracks_csv','trajectories_csv','vehicle_trajectories_csv'):
                p=out/(key+'.csv');p.write_text('header\n');files[key]=str(p)
            log=out/'result.json';log.write_text(json.dumps(files))
            def execute(plan,item,directory):
                self.assertEqual(item['env']['EXPORT_VEHICLE_TRAJECTORIES'],'1')
                self.assertEqual(item['env']['SESSION_START'],'2019-07-10_12:52:59')
                self.assertEqual(item['env']['STITCH_SEC'],'0.5')
                return dict(run_log=str(log))
            import types
            worker=types.ModuleType('research_worker');worker.execute=execute
            with patch.dict('sys.modules',{'research_worker':worker}):
                pilot.infer(dict(source_clock='2019-07-10 12:00:00',weights='w'),task,Path('clip.mp4'),out)
            self.assertTrue((out/'case'/'vehicle_trajectories_csv.csv').exists())

    def test_end_to_end_synthetic_exports(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);folder=out/'task';folder.mkdir()
            cal=out/'cal.json';cal.write_text(json.dumps(dict(H=np.eye(3).tolist(),hull=[[0,-20],[100,-20],[100,20],[0,20]],geometry_check_passed=True,validation='synthetic')))
            def rows(samples,tid,label):
                return [dict(track_id=tid,frame=r['frame'],foot_x=r['xy'][0],foot_y=r['xy'][1],box_w=.8,box_h=1.8,coasted=0,label=label,counted=1) for r in samples]
            pilot.table(folder/'trajectories_csv.csv',rows(path(x=20),'1','BICYCLIST'))
            pilot.table(folder/'vehicle_trajectories_csv.csv',rows(path(vx=6,x=14,y=3),'1','car')+rows(path(vx=6,x=35,y=8),'2','car'))
            pilot.table(folder/'tracks_csv.csv',[dict(track_id='1',facility='bike_lane',counted='1',det_label='cyclist')])
            plan=dict(calibration=str(cal),calibration_sha256=pilot.checksum(cal),source_clock='2019-07-10 12:00:00')
            task=dict(key='task',clip_key='clip',detector='reference',start_s=3179)
            result=pilot.analyze(plan,task,out,dict(fps=30))
            self.assertGreater(result['interaction_rows'],0)
            results=pilot.read(folder/'interactions.csv')
            baseline=[r for r in results if r['scenario']=='baseline' and r['vehicle_id']=='1'][0]
            self.assertAlmostEqual(float(baseline['min_sampled_clearance_m']),1.7)
            self.assertEqual(baseline['verified_near_miss'],'')
            (out/'manifest.json').write_text(json.dumps(dict(tasks=[task])))
            (folder/'status.json').write_text(json.dumps(dict(state='SUCCEEDED',result=result)))
            pilot.report(out)
            self.assertIn('1/1',(out/'RESULTS.md').read_text())
            self.assertTrue((out/'threshold_sensitivity.csv').exists())
            (folder/'run_log.json').write_text(json.dumps(dict(fps=30)))
            plan['tasks']=[task]
            (out/'manifest.json').write_text(json.dumps(plan))
            (out/'review_labels.csv').write_text('preserve labels\n')
            pilot.reanalyze(out)
            self.assertTrue(list((folder/'analysis_history').glob('*/interactions.csv')))
            self.assertEqual((out/'review_labels.csv').read_text(),'preserve labels\n')
            self.assertTrue((out/'smoothing_comparison.csv').exists())


class SubmissionTests(unittest.TestCase):
    def test_submit_one_gpu_and_afterany_report(self):
        import argparse
        import types
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);commands=[]
            def launch(cmd,**kwargs):
                commands.append(cmd)
                return types.SimpleNamespace(returncode=0,stdout='123\n' if len(commands)==1 else '124\n',stderr='')
            with patch.object(pilot,'ROOT',root),patch.object(pilot,'make_plan',return_value={'jobs':[]}),patch.object(pilot.shutil,'which',return_value='/bin/sbatch'),patch.object(pilot.subprocess,'run',side_effect=launch):
                pilot.submit(argparse.Namespace(go=True))
            self.assertEqual(len(commands),2)
            self.assertIn('--dependency=afterany:123',commands[1])
            self.assertIn('--gpus=0',commands[1])
            self.assertEqual(commands[1][-1],'report')
            manifest=next(root.glob('exp_results/*/manifest.json'))
            self.assertEqual(json.loads(manifest.read_text())['jobs'],['123','124'])

    def test_extract_timing_with_real_ffmpeg(self):
        import shutil
        import subprocess
        if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
            self.skipTest('ffmpeg is unavailable')
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);video=out/'source.mp4'
            subprocess.run(['ffmpeg','-nostdin','-v','error','-f','lavfi','-i','color=c=gray:s=720x480:r=6:d=31',
                            '-c:v','libx264','-preset','ultrafast',str(video)],check=True)
            result,audit=pilot.extract(dict(source=str(video),resolution=[720,480]),dict(clip_key='toy',start_s=0),out)
            self.assertTrue(result.exists())
            self.assertAlmostEqual(audit['fps_from_pts'],6,places=3)
            self.assertEqual(audit['irregular_fraction'],0)


class SmoothingReviewTests(unittest.TestCase):
    def test_rts_reduces_known_trajectory_position_error(self):
        from clearance_metrics import kalman_motion
        rng=np.random.default_rng(19)
        truth=path(vx=3,vy=.2,n=180)
        noisy=[{**r,'xy':r['xy']+rng.normal(0,.25,2)} for r in truth]
        filtered=kalman_motion(noisy);smooth=kalman_motion(noisy,rts=True)
        common=filtered.keys() & smooth.keys()
        def error(data):return np.mean([np.sum((data[k]['xy']-truth[k-1]['xy'])**2) for k in common])
        self.assertLess(error(smooth),error(filtered))
        self.assertLess(error(smooth),error({r['frame']:r for r in noisy}))
        self.assertTrue(all(np.isfinite(r['velocity']).all() for r in smooth.values()))

    def test_filter_restarts_and_does_not_invent_frames(self):
        from clearance_metrics import kalman_motion
        first=path(n=30)
        second=[{**r,'frame':r['frame']+1000,'t':r['t']+10,'xy':r['xy']+100} for r in path(n=30)]
        for rts in (False,True):
            alone=kalman_motion(second,rts=rts);together=kalman_motion(first+second,rts=rts)
            self.assertLessEqual(together.keys(),{r['frame'] for r in first+second})
            for k in alone:np.testing.assert_allclose(alone[k]['xy'],together[k]['xy'])
        with self.assertRaises(ValueError):kalman_motion([first[0],first[0]])

    def test_false_flags_require_adjudication_and_preserve_zero(self):
        from clearance_review import screening_reports
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            rows=[dict(task='t',detector='reference',scenario='baseline',cyclist_id='1',vehicle_id=str(i),
                min_footprint_distance_m=0,min_sampled_clearance_m=0,sampled_occupancy_pet_s=0) for i in range(3)]
            screening_reports(out,rows)
            result=pilot.read(out/'false_alarm_review.csv')[0]
            self.assertEqual(result['flagged_pairs'],'3')
            self.assertEqual(result['false_fraction_among_adjudicated_flags'],'')
            pilot.table(out/'review_labels.csv',[
                dict(task='t',cyclist_id='1',vehicle_id='0',near_miss_review='no',reviewer='reviewer'),
                dict(task='t',cyclist_id='1',vehicle_id='1',near_miss_review='yes',reviewer='reviewer')])
            screening_reports(out,rows)
            result=pilot.read(out/'false_alarm_review.csv')[0]
            self.assertEqual(result['reviewed_false_flags'],'1')
            self.assertEqual(result['unadjudicated_flags'],'1')
            self.assertEqual(float(result['false_fraction_among_adjudicated_flags']),.5)


class ExtractionFailureTests(unittest.TestCase):
    def test_selects_supported_sync_option(self):
        from types import SimpleNamespace
        for help_text,expected in [('-fps_mode mode',['-fps_mode','passthrough']),('-vsync parameter',['-vsync','0'])]:
            with patch.object(pilot.subprocess,'run',return_value=SimpleNamespace(stdout=help_text,stderr='')):
                self.assertEqual(pilot.ffmpeg_sync_arguments('fake'),expected)

    def test_legacy_flag_stderr_and_partial_cleanup(self):
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            def fail(command,**kwargs):
                self.assertIn('-vsync',command)
                self.assertNotIn('-fps_mode',command)
                Path(command[-1]).write_bytes(b'partial')
                return SimpleNamespace(returncode=1,stdout='',stderr='test encoder failure details')
            with patch('cv2.VideoCapture') as capture,patch.object(pilot.subprocess,'run',side_effect=fail):
                capture.return_value.get.side_effect=[30,100000,720,480]
                with self.assertRaisesRegex(RuntimeError,'test encoder failure details'):
                    pilot.extract(dict(source='source',resolution=[720,480],ffmpeg='fake',ffmpeg_sync_args=['-vsync','0']),
                                  dict(clip_key='test',start_s=0),out)
            self.assertFalse((out/'inputs/test.mp4').exists())
            self.assertFalse((out/'inputs/test.partial.mp4').exists())
            self.assertIn('test encoder failure details',(out/'inputs/test_extraction.json').read_text())


if __name__=='__main__':unittest.main()
