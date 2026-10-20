import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from submit_final_batch import extend_plan,main
from submit_newsites import build_plan,write_report,TARGETS
from submit_research import submit
import datetime as dt


class FinalBatchTests(unittest.TestCase):
    def plan(self,root):
        selections=[(t,Path('/data')/f'{t["key"]}.mp4',dt.datetime(t['year'],5,17,12),dict(fps=30,width=720,height=480,frames=108000))for t in TARGETS]
        return extend_plan(build_plan(root,'demo',selections))

    def test_all_pending_jobs_and_exact_duration_rules(self):
        p=self.plan(Path(__file__).resolve().parents[1])
        self.assertEqual(len(p['tasks']),5)
        self.assertEqual(len(p['tasks'][-1]['deps']),4)
        for task in p['tasks'][:2]:
            self.assertEqual(task['env']['BIC_MIN_SEC'],'3');self.assertEqual(task['env']['PED_MIN_SEC'],'3')
            self.assertEqual(task['env']['SHORT_MIN_SEC'],'0.3');self.assertEqual(task['env']['SHORT_RULE_NIGHT_ONLY'],'1')
        self.assertEqual(p['tasks'][3]['walltime'],'04:00:00')

    def test_custom_cpu_walltime_and_final_dependency(self):
        with tempfile.TemporaryDirectory()as td,contextlib.redirect_stdout(io.StringIO()):
            p=dict(root=td,tag='demo',jobs={},tasks=[dict(key='headers',kind='truth_headers',gpu=False,deps=[],walltime='04:00:00'),dict(key='report',kind='report',gpu=False,deps=['headers'])])
            commands=[]
            def runner(cmd,**kw):commands.append(cmd);return subprocess.CompletedProcess(cmd,0,str(100+len(commands)),'')
            submit(p,Path(td)/'jobs',2,runner)
            self.assertIn('--time=04:00:00',commands[0]);self.assertIn('--dependency=afterany:101',commands[1])

    def test_auxiliary_tasks_report_without_site_fields(self):
        with tempfile.TemporaryDirectory()as td,contextlib.redirect_stdout(io.StringIO()):
            d=Path(td)/'logs/demo';d.mkdir(parents=True)
            (d/'review.json').write_text(json.dumps(dict(state='SUCCEEDED',result=dict(output='/actual/review'))))
            p=dict(root=td,tag='demo',tasks=[dict(key='review',kind='final_review')])
            report=write_report(d,p);self.assertIn('/actual/review',Path(report['report']).read_text())

    def test_default_is_dryrun(self):
        with patch('sys.argv',['submit_final_batch.py']),patch('submit_final_batch.submit')as run,contextlib.redirect_stdout(io.StringIO()):
            main();run.assert_not_called()


if __name__=='__main__':unittest.main()
