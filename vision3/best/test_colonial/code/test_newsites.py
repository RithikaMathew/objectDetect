import contextlib
import datetime as dt
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from submit_newsites import source_clock,choose_source,build_plan,write_report,main,TARGETS


class NewSiteTests(unittest.TestCase):
    def test_clock_hourly_index_and_date(self):
        self.assertEqual(source_clock('Standard_SCU8PM_2021-04-13_0000.013.mp4'),dt.datetime(2021,4,13,12))
        self.assertEqual(source_clock('Standard_SCU8PM_2021-04-13_0000.025.mp4'),dt.datetime(2021,4,14))
        with self.assertRaises(ValueError):source_clock('random.mp4')

    def test_fixed_noon_preference_skips_unreadable_and_night(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)
            for n in (1,8,13,14):(folder/f'Standard_SCU8PM_2021-04-13_0000.{n:03}.mp4').touch()
            def inspect(p):
                if '.013.' in p.name:raise RuntimeError('broken noon file')
                return dict(width=720,height=480,fps=30,frames=108000)
            path,clock,metadata=choose_source(folder,2021,inspect)
            self.assertEqual(clock.hour,13)
            self.assertEqual(metadata['width'],720)

    def test_reference_plan_has_two_sites_and_no_augmented_or_training_runs(self):
        root=Path(__file__).resolve().parents[1]
        selections=[(t,Path('/data')/f'{t["key"]}.mp4',dt.datetime(t['year'],5,17,12),
                     dict(width=720,height=480,fps=30,frames=108000))for t in TARGETS]
        plan=build_plan(root,'demo',selections)
        self.assertEqual(len(plan['tasks']),3)
        self.assertEqual(plan['tasks'][-1]['deps'],['anderson_2021','curryford_2022'])
        for task in plan['tasks'][:-1]:
            self.assertTrue(task['scale_pixels'])
            self.assertEqual(task['env']['SAHI'],'1')
            self.assertEqual(task['env']['STATIC_FILTER'],'1')
            self.assertEqual(task['env']['MAX_FRAMES'],'27000')
            self.assertNotIn('TTA',task['env']);self.assertNotIn('ENHANCE',task['env'])
            self.assertIn('Inferred',task['env']['CLOCK_NOTE'])

    def test_report_includes_actual_video_paths_and_never_calls_counts_accuracy(self):
        with tempfile.TemporaryDirectory() as td,contextlib.redirect_stdout(io.StringIO()):
            root=Path(td);directory=root/'logs/demo';directory.mkdir(parents=True)
            task=dict(key='site',kind='pipeline',site='Anderson',year=2021,metadata={},
                      env=dict(VIDEO_OVERRIDE='/raw/hour.mp4',SESSION_START='2021-04-13_12:00:00'))
            log=directory/'run.json';log.write_text(json.dumps(dict(final_counts={'bicyclists':2},runtime_s=60,
                duration_s_processed=900,annotated_clips=['/actual/video.mp4'],tracks_csv='/actual/tracks.csv')))
            (directory/'site.json').write_text(json.dumps(dict(state='SUCCEEDED',result=dict(run_log=str(log)))))
            result=write_report(directory,dict(root=td,tag='demo',tasks=[task]))
            text=Path(result['report']).read_text()
            self.assertIn('/actual/video.mp4',text)
            self.assertIn('NOT accuracy',text)
            self.assertIn('do not call this an unseen-site test',text)

    def test_mac_dryrun_does_not_submit(self):
        with tempfile.TemporaryDirectory() as td,patch('sys.argv',['submit_newsites.py','--root',td]), \
             patch('submit_newsites.submit')as submit,contextlib.redirect_stdout(io.StringIO()):
            main();submit.assert_not_called();self.assertFalse((Path(td)/'logs').exists())


if __name__=='__main__':unittest.main()
