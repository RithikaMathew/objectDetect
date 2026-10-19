"""Review packs must use raw video offsets and reject failed snippet cuts."""
import contextlib
import csv
import io
import json
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import review_pack
import scale_up


class ReviewTests(unittest.TestCase):
    def fixture(self, tmp):
        root = Path(tmp)
        raw = root / 'raw'
        raw.mkdir()
        (raw / 'colonial.015.mp4').touch()
        table = root / 'tracks.csv'
        with table.open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=['chunk', 'first_time', 'bin_start', 'secs', 'clip_hint'])
            w.writeheader()
            w.writerow(dict(chunk='015', first_time='2019-07-10 14:18:30', bin_start='14:15',
                            secs='4', clip_hint='annotated/biased.mp4'))
        return SimpleNamespace(table=str(table), out=str(root / 'pack'), source_dir=str(raw),
                               time_col='first_time', bin_col='bin_start', secs_col='secs',
                               video_col='clip_hint', seek_col=None, rank_col=None, pad=3,
                               max_clip=20, budget_min=0, no_ffmpeg=True)

    def test_raw_hour_offset_and_no_pack_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
            a = self.fixture(tmp)
            review_pack.cmd_build(a)
            items = json.loads((Path(a.out) / 'index.json').read_text())
            self.assertEqual(items[0]['seek'], 1107)
            self.assertTrue(items[0]['video'].endswith('colonial.015.mp4'))
            with self.assertRaises(SystemExit): review_pack.cmd_build(a)

    def test_failed_cut_does_not_publish_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = self.fixture(tmp)
            a.no_ffmpeg = False
            with patch.object(review_pack.subprocess, 'run', return_value=subprocess.CompletedProcess([], 1, '', 'bad video')):
                with self.assertRaises(SystemExit): review_pack.cmd_build(a)
            self.assertFalse((Path(a.out) / 'index.json').exists())

    def test_scaleup_resolves_static_threshold(self):
        with patch.dict('os.environ', {'NETPX': '7'}):
            env = scale_up.envv_from_batch(Path(__file__).with_name('run_batch4.sh'))
        self.assertIn('STATIC_MAX_NET_PX=7', env)
        self.assertNotIn('$', env)

    def test_scaleup_requires_both_tables_and_exact_chunk(self):
        with tempfile.TemporaryDirectory() as tmp:
            counts = Path(tmp) / 'counts' / 'test'
            counts.mkdir(parents=True)
            (counts / 'video2019.013_tracks.csv').touch()
            self.assertEqual(scale_up.done_chunks(tmp, 'test', [13, 19]), [])
            (counts / 'video2019.013_bin_counts.csv').touch()
            self.assertEqual(scale_up.done_chunks(tmp, 'test', [13, 19]), [13])


if __name__ == '__main__':
    unittest.main()
