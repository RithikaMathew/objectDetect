import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from research_detection import tta_people, audit_times
from grounding_audit import max_iou
from submit_research import build_plan, submit
from research_worker import report, execute


class DetectionTests(unittest.TestCase):
    def test_flip_boxes_return_to_source_and_vehicles_are_excluded(self):
        image=np.zeros((40,100,3),np.uint8);image[:,0]=255
        calls=[]
        def predict(det,fr,conf,size,device):
            calls.append((size,fr.flags.c_contiguous))
            flip=bool(fr[0,-1,0])
            box=[70,5,90,25] if flip else [10,5,30,25]
            return np.array([box,[0,0,50,30]],float),np.array([.8,.9]),np.array([0,2])
        boxes,scores,classes=tta_people(None,image,.25,1280,[960,1280],None,[0,1],predict)
        self.assertEqual(len(calls),3)
        np.testing.assert_allclose(boxes,np.tile([10,5,30,25],(3,1)))
        self.assertTrue(all(contiguous for _,contiguous in calls))
        self.assertTrue((classes==0).all())

    def test_base_scale_does_not_repeat_original_pass(self):
        fn=lambda *args:(np.zeros((0,4)),np.zeros(0),np.zeros(0,int))
        boxes,_,_=tta_people(None,np.zeros((4,4,3)),.2,1280,[],None,[0],fn)
        self.assertEqual(boxes.shape,(0,4))

    def test_audit_covers_short_encounters_not_only_regular_samples(self):
        times=audit_times([dict(s=7.1,e=8.3)])
        self.assertIn(7.1,times);self.assertIn(7.7,times);self.assertIn(8.3,times)
        self.assertEqual(max_iou([10,10,30,30],[dict(box_cx=20,box_cy=20,box_w=20,box_h=20)]),1)


class SubmissionTests(unittest.TestCase):
    def test_setup_installs_only_into_per_suite_environment(self):
        with tempfile.TemporaryDirectory() as tmp,contextlib.redirect_stdout(io.StringIO()):
            root=Path(tmp);directory=root/'logs/demo';directory.mkdir(parents=True)
            venv=root/'.research_env/demo';(venv/'bin').mkdir(parents=True)
            (venv/'bin/python').touch();site=venv/'lib/site-packages';site.mkdir(parents=True)
            (directory/'grounding_ready.json').write_text('{"model_path":"snapshot"}')
            commands=[]
            with patch('research_worker.run',side_effect=lambda cmd,**kw:commands.append(cmd)), \
                 patch('research_worker.subprocess.check_output',return_value=str(site)+'\n'):
                execute(dict(root=tmp,tag='demo'),dict(key='grounding_setup',kind='setup'),directory)
            pip=next(c for c in commands if 'pip' in c)
            self.assertEqual(pip[0],venv/'bin/python')
            self.assertTrue((site/'working_yolo_environment.pth').is_file())
            self.assertIn('transformers==4.49.0',pip)

    def test_plan_excludes_deferred_work_and_reuses_existing_truth(self):
        root=Path(__file__).resolve().parent.parent
        plan=build_plan(root,'demo')
        self.assertEqual(len(plan['tasks']),22)
        self.assertEqual(sum(t.get('group')=='tta' for t in plan['tasks']),4)
        self.assertEqual(sum(t['kind']=='grounding' for t in plan['tasks']),4)
        self.assertEqual(len([t for t in plan['tasks'] if t.get('group')=='sensitive']),4)
        self.assertFalse(any(t['kind'] in ('train','scale') for t in plan['tasks']))
        for t in plan['tasks']:
            if t.get('env'):
                self.assertNotIn('$',t['env'].get('STATIC_MAX_NET_PX',''))

    def test_dependencies_finish_even_when_setup_fails_and_limit_gpu_lanes(self):
        with tempfile.TemporaryDirectory() as tmp,contextlib.redirect_stdout(io.StringIO()):
            tasks=[dict(key='setup',kind='setup',gpu=True,deps=[]),
                   dict(key='audit',kind='grounding',gpu=True,deps=['setup']),
                   dict(key='final_report',kind='report',gpu=False,deps=['setup','audit'])]
            plan=dict(root=tmp,tag='demo',tasks=tasks,jobs={});cmds=[]
            def sbatch(cmd,**kw):
                cmds.append(cmd)
                return subprocess.CompletedProcess(cmd,0,str(100+len(cmds))+'\n','')
            out=Path(tmp)/'suite';submit(plan,out,1,sbatch)
            self.assertIn('--dependency=afterany:101',cmds[1])
            self.assertIn('--dependency=afterany:101:102',cmds[2])
            self.assertFalse(any('afterok' in arg for cmd in cmds for arg in cmd))
            with self.assertRaises(FileExistsError):submit(plan,out,1,sbatch)

    def test_submission_failure_preserves_ids_and_stops(self):
        with tempfile.TemporaryDirectory() as tmp,contextlib.redirect_stdout(io.StringIO()):
            plan=dict(root=tmp,tag='demo',jobs={},tasks=[dict(key=k,kind='scan',gpu=True,deps=[]) for k in ['a','b','c']])
            calls=[]
            def sbatch(cmd,**kw):
                calls.append(cmd)
                return subprocess.CompletedProcess(cmd,0 if len(calls)==1 else 1,'123\n' if len(calls)==1 else '', 'queue error')
            out=Path(tmp)/'suite'
            with self.assertRaises(RuntimeError):submit(plan,out,2,sbatch)
            saved=json.loads((out/'manifest.json').read_text())
            self.assertEqual(saved['jobs'],{'a':'123'});self.assertEqual(len(calls),2)
            self.assertEqual(saved['submission_error']['task'],'b')

    def test_failed_and_missing_tasks_do_not_produce_accuracy_claim(self):
        with tempfile.TemporaryDirectory() as tmp,contextlib.redirect_stdout(io.StringIO()):
            d=Path(tmp)/'logs/demo';d.mkdir(parents=True)
            plan=dict(root=tmp,tag='demo',jobs={'a':'1'},tasks=[dict(key='a',kind='scan'),dict(key='b',kind='scan')])
            (d/'manifest.json').write_text(json.dumps(plan));(d/'a.json').write_text(json.dumps(dict(state='FAILED',error='download failed')))
            result=report(d);text=Path(result['report']).read_text()
            self.assertIn('FAILED',text);self.assertIn('NO_FINAL_STATUS',text)
            self.assertIn('No complete new scored group',text)


if __name__=='__main__':unittest.main()
