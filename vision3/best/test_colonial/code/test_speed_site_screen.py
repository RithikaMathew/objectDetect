import argparse
import csv
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import cv2
import numpy as np
from speed_site_screen import choose,screen
from submit_speed_pilot import commands
from preview_ffmpeg import resolve
from retry_speed_previews import retry_command

class SpeedScreenTests(unittest.TestCase):
    def row(self,clock,site='University SW Speed'):
        return dict(site=site,clock=clock,study_date='2019-09-25',mapping_ambiguous='no',archive_path=clock+'.mp4',video='source.mp4',clock_status='inferred')

    def test_first_day_selection_not_next_day_noon(self):
        rows=[self.row('2019-09-25 13:00:00'),self.row('2019-09-26 12:00:00')]
        self.assertEqual(choose(rows,'University')[0]['clock'],'2019-09-25 13:00:00')

    def test_ambiguous_and_missing_alias_not_silently_selected(self):
        row=self.row('2019-09-25 12:00:00');row['mapping_ambiguous']='yes'
        self.assertEqual(choose([row],'University'),[])
        self.assertEqual(choose([row],'Silver Star'),[])

    def test_gpu_dependency_and_shell_quoting(self):
        first,second=commands(Path('/tmp/project space'),Path('/tmp/out space'),'12345')
        self.assertIn('--dependency=afterany:12345',second)
        self.assertIn("cd '/tmp/project space'",second[-1])
        self.assertNotIn('--gpus=1',first)

    def test_missing_ffmpeg_fails_before_extraction_or_output_creation(self):
        with tempfile.TemporaryDirectory() as td:
            d=Path(td);args=argparse.Namespace(out=d/'screen',root=d,data_root=d)
            with patch('speed_site_screen.resolve',side_effect=RuntimeError('missing ffmpeg')),patch('speed_site_screen.plan') as planner:
                with self.assertRaisesRegex(RuntimeError,'missing ffmpeg'):screen(args)
                planner.assert_not_called()
            self.assertFalse(args.out.exists())

    def test_recovery_is_cpu_only_and_reuses_selection_without_extraction(self):
        cmd=retry_command(Path('/tmp/root space'),Path('/tmp/bundle'),Path('/tmp/retry'),'/tmp/ffmpeg binary')
        self.assertNotIn('--gpus=1',cmd)
        self.assertNotIn('--extract',cmd[-1])
        self.assertIn('--selected-sources',cmd[-1])
        self.assertIn("FFMPEG_BINARY='/tmp/ffmpeg binary'",cmd[-1])

    @unittest.skipUnless(shutil.which('ffmpeg'),'ffmpeg required to exercise isolated binary fallback')
    def test_cached_binary_works_without_path_ffmpeg(self):
        exe=shutil.which('ffmpeg')
        with tempfile.TemporaryDirectory() as td:
            cache=Path(td);binaries=cache/'imageio_ffmpeg/binaries';binaries.mkdir(parents=True)
            (binaries/'ffmpeg-test').symlink_to(exe)
            with patch('preview_ffmpeg.shutil.which',return_value=None),patch.dict('os.environ',{'FFMPEG_BINARY':''}):
                self.assertEqual(resolve(False,cache),str(Path(exe).resolve()))

    @unittest.skipUnless(shutil.which('ffmpeg'),'ffmpeg required for preview smoke test')
    def test_real_short_preview_and_source_preservation(self):
        with tempfile.TemporaryDirectory() as td:
            d=Path(td);source=d/'source.mp4';v=cv2.VideoWriter(str(source),cv2.VideoWriter_fourcc(*'mp4v'),10,(64,48))
            for i in range(80):v.write(np.full((48,64,3),i,np.uint8))
            v.release();original=source.read_bytes()
            row=self.row('2019-09-25 12:00:00');row.update(video=str(source),reference_location='University',camera_match_status='candidate')
            args=argparse.Namespace(out=d/'screen',root=d,data_root=d,extract=False,archive=d/'absent.zip',max_extract_gb=1,preview_seconds=1)
            with patch('speed_site_screen.plan',return_value=[row]),patch('speed_site_screen.OFFSETS',(1,3,5)):
                screen(args)
            with (args.out/'screening.csv').open() as f:result=next(csv.DictReader(f))
            self.assertEqual(result['status'],'PREVIEWS_READY_REVIEW_REQUIRED')
            self.assertEqual(len(json.loads(result['previews'])),3)
            self.assertEqual(source.read_bytes(),original)
            self.assertTrue((args.out/'index.html').exists())

if __name__=='__main__':unittest.main()
