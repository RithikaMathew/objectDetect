import ast
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from fastapi import HTTPException
from cyclescope.service import main, repository, help as guide


class RuntimeFixTests(unittest.TestCase):
    def test_api_has_one_handler_per_route_and_no_duplicate_schema_names(self):
        routes=[(method,r.path) for r in main.app.routes for method in getattr(r,'methods',[])]
        self.assertEqual(len(routes),len(set(routes)))
        tree=ast.parse(Path(main.__file__).read_text())
        names=[n.name for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))]
        self.assertEqual(len(names),len(set(names)))

    def test_normalized_upload_always_passes_explicit_chunk_and_no_camera_truth(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);weights=folder/'best.pt';weights.write_bytes(b'test only')
            with patch.dict(repository.os.environ,{'DETECTOR_WEIGHTS':str(weights)}),patch.object(repository.subprocess,'run',return_value=SimpleNamespace(returncode=1)) as run:
                with self.assertRaises(RuntimeError):repository.run(str(folder/'upload'),lambda p:None)
                cmd=run.call_args.args[0]
                self.assertEqual(cmd[cmd.index('--chunk-index')+1],'1')
                self.assertIn('--gt-truth-dir',cmd)
                self.assertNotIn('--night-start',cmd)
                self.assertEqual(run.call_args.kwargs['env']['PYTHONUNBUFFERED'],'1')

    def test_all_workbook_reference_locations_and_unknown_year_remain_honest(self):
        result=repository.dashboard()
        self.assertEqual(len(result['references']),14)
        with (repository.ROOT/result['reference_source']).open() as f:raw=list(csv.DictReader(f))
        for ref in result['references']:
            source=[r for r in raw if r['street']==ref['location']]
            self.assertEqual(ref['sample'],len(source))
            self.assertAlmostEqual(ref['mean_mph'],sum(float(r['recomputed_mph'])for r in source)/len(source))
        star=next(r for r in result['rows'] if r['id']=='reference-Silver Star')
        self.assertEqual(star['years'],[]);self.assertIsNone(star['videos']);self.assertIsNone(star['hours'])
        self.assertEqual(sum(r['videos'] or 0 for r in result['rows']),9085)
        self.assertEqual(sum(len(r['speeds']) for r in result['rows']),9)

    def test_saved_speed_is_scoped_to_one_object_across_reload(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(main,'DATA',Path(temp)):
            jid='123456abcd';(main.DATA/jid).mkdir()
            state=dict(id=jid,status='ready',name='synthetic',meta=dict(fps=30,frames=100),calibration=None,decisions={},tracks=[dict(id=i,cls='cyclist',source='manual',deleted=False,keys={'0':[0,0,10,20]},boxes=[[0,0,0,10,20]])for i in (1,2)])
            main.save(jid,state)
            main.set_speed(jid,1,main.SpeedOverride(mph=13,reason='Reviewed timing'))
            reloaded=main.get_job(jid)
            self.assertEqual(reloaded['analysis']['speeds']['1']['median_mph'],13)
            self.assertNotIn('2',reloaded['analysis']['speeds'])
            main.patch_track(jid,2,main.TrackPatch(cls='person'))
            self.assertEqual(main.get_job(jid)['analysis']['speeds']['1']['median_mph'],13)
            main.set_speed(jid,1,main.SpeedOverride(mph=None))
            self.assertNotIn('1',main.get_job(jid)['analysis']['speeds'])

    def test_guide_has_sources_and_unknown_questions_do_not_invent_answers(self):
        self.assertTrue(guide.answer('What is Ground X?')['sources'])
        self.assertIn('do not have',guide.answer('Tell me what will happen tomorrow')['answer'])
        for _,path in guide.SOURCES.values():self.assertTrue((guide.ROOT/path).is_file())
