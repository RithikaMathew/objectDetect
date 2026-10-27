import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from adaptive_speed_batch import quota,boundary_safe,make_plan,report,gather_window,window_pipeline,select_chronologically,snapshot,recovery_plan,checked_saved_calibration,matched_manual_plan,worker
ROOT=Path(__file__).resolve().parents[1]

class AdaptiveSpeedTests(unittest.TestCase):
    def test_requested_targets_and_cap(self):
        self.assertEqual(quota(2),2)
        self.assertEqual(quota(9),3)
        self.assertEqual(quota(11),4)
        self.assertEqual(quota(78),5)
        with self.assertRaises(ValueError):quota(0)

    def test_plan_includes_colonial_excludes_unmapped_and_pools_one_lee_camera(self):
        p=make_plan(ROOT,'test')
        self.assertEqual(len(p['tasks']),13)
        self.assertEqual(len([t for t in p['tasks'] if t['reference_site']=='Lee']),1)
        self.assertIn('Colonial',[t['reference_site'] for t in p['tasks']])
        self.assertIn('Silver Star',[s['site'] for s in p['skipped']])

    def test_site_snapshot_available_before_batch_finishes(self):
        with tempfile.TemporaryDirectory() as td:
            d=Path(td);p=make_plan(ROOT,'test');t=p['tasks'][0]
            (d/'manifest.json').write_text(json.dumps(p));(d/t['key']).mkdir()
            status=dict(state='FAILED',stage='finished',samples=[],windows=[],failure='calibration insufficient')
            snapshot(d,t,status)
            self.assertTrue((d/t['key']/'RESULTS.md').exists())
            self.assertIn('calibration insufficient',(d/t['key']/'comparison.csv').read_text())
            self.assertFalse((d/'RESULTS.md').exists())

    def test_colonial_clock_uses_source_hour(self):
        t=next(t for t in make_plan(ROOT,'test')['tasks'] if t['reference_site']=='Colonial')
        row=dict(t['source'],fps=30,duration_seconds=3600,probe_status='readable_metadata_not_full_decode')
        task=window_pipeline(ROOT,'test_colonial_clock',row,900,1800,30,108000)
        self.assertEqual(task['env']['CHUNK'],'1')
        self.assertEqual(task['env']['SESSION_START'],row['clock'].replace(' ','_'))

    def test_recovery_keeps_only_failed_site_and_reuses_calibration(self):
        with tempfile.TemporaryDirectory() as td:
            d=Path(td);p=make_plan(ROOT,'original');(d/'manifest.json').write_text(json.dumps(p))
            cal=d/p['tasks'][0]['key']/'calibration';cal.mkdir(parents=True)
            (cal/'calibration.json').write_text(json.dumps(dict(H=[[1,0,0],[0,1,0],[0,0,1]],hull=[[[0,0]],[[20,0]],[[0,20]]],geometry_check_passed=True)))
            recovered=recovery_plan(d,0,'recovered')
            self.assertEqual(len(recovered['tasks']),1)
            self.assertEqual(recovered['tasks'][0]['source']['site'],'Aloma Path')
            self.assertEqual(recovered['tag'],'recovered')
            self.assertTrue(Path(recovered['tasks'][0]['reuse_calibration']).exists())
            self.assertNotIn('reuse_calibration',json.loads((d/'manifest.json').read_text())['tasks'][0])

    def test_all_site_short_run_reuses_every_camera_calibration(self):
        with tempfile.TemporaryDirectory() as td:
            d=Path(td);p=make_plan(ROOT,'original');(d/'manifest.json').write_text(json.dumps(p))
            for t in p['tasks']:
                cal=d/t['key']/'calibration';cal.mkdir(parents=True)
                (cal/'calibration.json').write_text(json.dumps(dict(H=[[1,0,0],[0,1,0],[0,0,1]],hull=[[[0,0]],[[20,0]],[[0,20]]],geometry_check_passed=True)))
            new=recovery_plan(d,0,'shortday',all_sites=True)
            self.assertEqual(len(new['tasks']),13)
            self.assertEqual({t['source']['site'] for t in new['tasks']},{t['source']['site'] for t in p['tasks']})
            self.assertTrue(all(Path(t['reuse_calibration']).is_file() for t in new['tasks']))

    def test_manual_matching_uses_only_submitted_intervals_without_quota(self):
        with tempfile.TemporaryDirectory() as td:
            d=Path(td);p=make_plan(ROOT,'original');(d/'manifest.json').write_text(json.dumps(p));pack=d/'pack';pack.mkdir()
            t=p['tasks'][0];source=t['source'];e=[]
            for segment in (0,2,3):
                start=__import__('datetime').datetime.fromisoformat(source['clock'])+__import__('datetime').timedelta(seconds=segment*900)
                e.append(dict(key=t['key']+'_'+str(segment),camera=source['site'],source=source,reference=dict(start=start.isoformat(sep=' '),count=1),video='clip'+str(segment)+'.mp4'))
            (pack/'manifest.json').write_text(json.dumps(dict(entries=e)))
            obs=d/'points.json';obs.write_text(json.dumps(dict(observations=[dict(key=e[0]['key']),dict(key=e[1]['key'])])))
            cal=d/t['key']/'calibration';cal.mkdir(parents=True)
            (cal/'calibration.json').write_text(json.dumps(dict(H=[[1,0,0],[0,1,0],[0,0,1]],hull=[[[0,0]],[[20,0]],[[0,20]]],geometry_check_passed=True)))
            plan=matched_manual_plan(d,pack,obs,'match')
            self.assertEqual(len(plan['tasks']),1)
            self.assertEqual([w['segment'] for w in plan['tasks'][0]['manual_intervals']],[0,2])
            self.assertTrue(plan['force_all_intervals'])
            self.assertEqual(plan['day_bicycle_min_seconds'],1.5)
            self.assertEqual(plan['tasks'][0]['manual_intervals'][1]['clock'],e[1]['reference']['start'])

    def test_cut_colonial_clip_has_chunk_one_and_correct_clock(self):
        t=next(t for t in make_plan(ROOT,'test')['tasks'] if t['reference_site']=='Colonial')
        row=dict(t['source'],video='/tmp/manual_colonial_123000.mp4',clock='2019-07-10 12:30:00',fps=30,duration_seconds=900,chunk_index_override=1,probe_status='readable_metadata_not_full_decode')
        pipeline=window_pipeline(ROOT,'matched_colonial',row,0,900,30,27000,1.5)
        self.assertEqual(pipeline['env']['CHUNK'],'1')
        self.assertEqual(pipeline['env']['SESSION_START'],'2019-07-10_12:30:00')
        self.assertEqual(pipeline['env']['VIDEO_OVERRIDE'],row['video'])
        self.assertEqual(pipeline['env']['START_FRAME'],'1')
        self.assertEqual(pipeline['env']['MAX_FRAMES'],'27000')

    def test_matched_worker_processes_later_clip_after_target_already_reached(self):
        class Capture:
            def __init__(self,path):self.clip=Path(path).name.startswith('clip')
            def get(self,k):return {3:720,4:480,5:30,7:27000 if self.clip else 108000}[k]
            def read(self):return True,np.zeros((480,720,3),np.uint8)
            def release(self):pass
        with tempfile.TemporaryDirectory() as td:
            d=Path(td);p=make_plan(ROOT,'matched_worker_test');t=p['tasks'][0];p['tasks']=[t];p['force_all_intervals']=True;t['target']=1
            t['manual_intervals']=[dict(key='clip'+str(i),segment=i,video='/tmp/clip'+str(i)+'.mp4',clock='2019-10-30 '+clock,study_count=1,manual_count=1,manual_mean_mph=10,manual_speed_sample=1) for i,clock in [(0,'12:00:00'),(2,'12:30:00')]]
            cal=d/'saved.json';cal.write_text(json.dumps(dict(H=[[1,0,0],[0,1,0],[0,0,1]],hull=[[[0,0]],[[20,0]],[[0,20]]],geometry_check_passed=True)));t['reuse_calibration']=str(cal)
            (d/'manifest.json').write_text(json.dumps(p))
            def child(args,**kwargs):
                w=Path(args[args.index('--window')+1]);raw=w/'raw_run_log.json';raw.write_text('{}');(w/'result.json').write_text(json.dumps(dict(run_log=str(raw))))
            def candidates(log,H,hull,start,end,task,segment,extrapolate):
                return [dict(track_id=str(segment),eligible=1,counted='1',track_start=task['source']['clock'],speed_mph=10,site=task['reference_site'],segment=segment,measurement_start=task['source']['clock'],measurement_end=task['source']['clock'])]
            with patch('adaptive_speed_batch.cv2.VideoCapture',Capture),patch('adaptive_speed_batch.subprocess.run',child),patch('adaptive_speed_batch.gather_window',candidates),patch('adaptive_speed_batch.window_pipeline',return_value=dict(env=dict(RUN='unit_matched_never_existing'))),patch('adaptive_speed_batch.iccv_calibration',side_effect=AssertionError('Must reuse calibration')):
                worker(d,0)
            status=json.loads((d/t['key']/'status.json').read_text())
            self.assertEqual([w['segment'] for w in status['windows']],[0,2])
            self.assertEqual(len(status['samples']),2)
            self.assertEqual(status['state'],'MANUAL_INTERVALS_COMPLETED_PROVISIONAL')
            self.assertTrue((d/t['key']/'matched_intervals.csv').exists())

    def test_recovery_refuses_invalid_saved_scale(self):
        with self.assertRaises(ValueError):
            checked_saved_calibration(dict(H=[[0,0,0],[0,0,0],[0,0,0]],hull=[[[0,0]],[[1,0]],[[0,1]]],geometry_check_passed=True))

    def test_boundary_censoring_avoids_quota_duplicates(self):
        self.assertFalse(boundary_safe(900,910,900,1800))
        self.assertFalse(boundary_safe(1780,1800,900,1800))
        self.assertTrue(boundary_safe(910,920,900,1800))

    def test_report_is_person_weighted_not_segment_mean(self):
        with tempfile.TemporaryDirectory() as td:
            d=Path(td);p=make_plan(ROOT,'test');p['tasks']=p['tasks'][:1]
            (d/'manifest.json').write_text(json.dumps(p));t=p['tasks'][0];(d/t['key']).mkdir()
            # One10mph person in segment0, two20mph people in segment1 ->16.67mph.
            samples=[dict(site=t['reference_site'],segment=i,track_id=str(n),measurement_start='2019-01-01 12:00:10',measurement_end='2019-01-01 12:00:12',speed_mph=v) for n,(i,v) in enumerate([(0,10),(1,20),(1,20)])]
            (d/t['key']/'status.json').write_text(json.dumps(dict(state='TARGET_NOT_REACHED_WITHIN_LIMIT',samples=samples,windows=[dict(source_start_seconds=0,source_end_seconds=900),dict(source_start_seconds=900,source_end_seconds=1800)],failure='')))
            report(d)
            import csv
            with (d/'comparison.csv').open() as f:r=next(csv.DictReader(f))
            self.assertAlmostEqual(float(r['model_candidate_mean_mph']),50/3)
            self.assertEqual(float(r['minutes_processed']),30)

    def test_windows_are_nonoverlapping_and_array_clock_is_not_camera_index(self):
        row=dict(site='Baxter',video='/tmp/source.013.mp4',archive_path='source.013.mp4',clock='2019-09-18 12:00:00',clock_status='filename_inferred',fps=30,duration_seconds=3600,probe_status='readable_metadata_not_full_decode')
        a=window_pipeline(ROOT,'adaptive_test',row,0,900,30,108000)
        b=window_pipeline(ROOT,'adaptive_test2',row,900,1800,30,108000)
        self.assertEqual(a['env']['MAX_FRAMES'],'27000')
        self.assertEqual(b['env']['START_FRAME'],'27001')
        self.assertEqual(b['env']['SLURM_ARRAY_TASK_ID'],'1')
        self.assertEqual(b['env']['CHUNK'],'1')
        self.assertEqual(b['env']['SESSION_START'],'2019-09-18_12:00:00')

    def test_short_day_option_preserves_pedestrian_night_and_other_filters(self):
        row=dict(site='Baxter',video='/tmp/source.013.mp4',archive_path='source.013.mp4',clock='2019-09-18 12:00:00',clock_status='filename_inferred',fps=30,duration_seconds=3600,probe_status='readable_metadata_not_full_decode')
        original=window_pipeline(ROOT,'baseline',row,0,900,30,108000)
        short=window_pipeline(ROOT,'short',row,0,900,30,108000,1.5)
        self.assertEqual(short['env']['BIC_MIN_SEC'],'1.5')
        self.assertEqual(short['env']['PED_MIN_SEC'],'3')
        self.assertEqual(short['env']['NIGHT_BIC_MIN_SEC'],'3')
        self.assertEqual(short['env']['SHORT_MIN_SEC'],'0.3')
        for key in ('STATIC_FILTER','DET_VETO_PCT','SHORT_RULE_NIGHT_ONLY'):
            self.assertEqual(short['env'].get(key),original['env'].get(key))
        self.assertEqual(original['env']['BIC_MIN_SEC'],'3')
        with self.assertRaises(ValueError):window_pipeline(ROOT,'bad',row,0,900,30,108000,0)

    def test_selection_combines_windows_and_ignores_speed_agreement(self):
        accepted=[]
        make=lambda tid,time,speed,eligible=1:dict(track_id=tid,track_start=time,speed_mph=speed,eligible=eligible)
        select_chronologically(accepted,[make('1','12:01',40)],3)
        second=[make('4','12:19',9),make('2','12:16',3),make('3','12:17',30),make('5','12:15',10,0)]
        select_chronologically(accepted,second,3)
        self.assertEqual([r['track_id'] for r in accepted],['1','2','3'])
        self.assertEqual(second[0]['selected_for_mean'],0)

    def test_all_found_counts_and_timestamps_are_separate_from_selected(self):
        import csv
        with tempfile.TemporaryDirectory() as td:
            d=Path(td);p=make_plan(ROOT,'test');p['tasks']=p['tasks'][:1];t=p['tasks'][0]
            (d/'manifest.json').write_text(json.dumps(p));site=d/t['key'];site.mkdir()
            (site/'status.json').write_text(json.dumps(dict(state='TARGET_NOT_REACHED_WITHIN_LIMIT',samples=[],windows=[dict(source_start_seconds=0,source_end_seconds=900)],failure='')))
            candidates=[dict(track_id='1',track_start='2019-01-01 12:01:01',track_end='2019-01-01 12:01:04',counted='1',eligible='1'),dict(track_id='2',track_start='2019-01-01 12:02:01',track_end='2019-01-01 12:02:02',counted='0',eligible='0')]
            with (site/'all_bicycle_candidates.csv').open('w') as f:
                w=csv.DictWriter(f,fieldnames=list(candidates[0]));w.writeheader();w.writerows(candidates)
            report(d)
            with (d/'comparison.csv').open() as f:r=next(csv.DictReader(f))
            self.assertEqual(r['found_candidate_tracks'],'2')
            self.assertEqual(r['counted_candidate_tracks'],'1')
            self.assertEqual(r['speed_eligible_candidate_tracks'],'1')
            self.assertEqual(r['model_candidate_sample'],'0')
            with (d/'all_candidate_timestamps.csv').open() as f:times=list(csv.DictReader(f))
            self.assertEqual(times[1]['track_start'],'2019-01-01 12:02:01')

    def test_missing_worker_status_is_not_zero_mph(self):
        with tempfile.TemporaryDirectory() as td:
            d=Path(td);p=make_plan(ROOT,'test');p['tasks']=p['tasks'][:1];(d/'manifest.json').write_text(json.dumps(p));report(d)
            import csv
            with (d/'comparison.csv').open() as f:r=next(csv.DictReader(f))
            self.assertEqual(r['state'],'NO_STATUS');self.assertEqual(r['model_candidate_mean_mph'],'')

if __name__=='__main__':unittest.main()
