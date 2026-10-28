import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import zipfile
from prepare_full_archive_inventory import prepare
from build_video_inventory_readmes import read

class FullDurationTests(unittest.TestCase):
    def test_full_scope_resume_and_actual_hours(self):
        with tempfile.TemporaryDirectory() as td:
            repo=Path(td);(repo/'docs').mkdir();out=repo/'results'
            first='MioVision Data/Bike Lane Study/MioVision Video/BL Example/Standard_SCU8PM_2019-01-01_0000/Standard_SCU8PM_2019-01-01_0000.001.mp4'
            second='MioVision Data/2022 Data/New St/Standard_SCU8OG_2021-01-01_0000/Standard_SCU8OG_2021-01-01_0000.001.mp4'
            archive=repo/'test.zip'
            with zipfile.ZipFile(archive,'w') as z:
                z.writestr(first,b'fake_video');z.writestr(second,b'fake_video');z.writestr('MioVision Data/Reports/speeds.csv','id,mph\n1,12\n')
            old=repo/'vision3/best/test_colonial/exp_results/VIDEO_DURATION_AUDIT/per_source.csv';old.parent.mkdir(parents=True)
            with old.open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=['archive_path','audit_status','duration_seconds']);w.writeheader();w.writerow(dict(archive_path=first,audit_status='MEASURED',duration_seconds=1800))
            with patch('audit_video_durations.shutil.which',return_value='/fake/ffprobe'),patch('audit_video_durations.probe',return_value=900) as probe:
                prepare(archive,out,repo,False)
                self.assertEqual(probe.call_count,1)
            totals=read(out/'durations/by_camera.csv')
            self.assertEqual(sorted(float(r['exact_total_hours']) for r in totals),[.25,.5])
            self.assertTrue(all(r['duration_status']=='COMPLETE' for r in totals))
            text=(repo/'docs/MIOVISION_ARCHIVE_INVENTORY_README.md').read_text()
            self.assertIn('New St',text);self.assertIn('2021',text);self.assertIn('0.25',text)
            with patch('audit_video_durations.probe') as probe:
                prepare(archive,out,repo,True)
                probe.assert_not_called()
            self.assertEqual(len(read(out/'possible_report_exports.csv')),1)
            self.assertEqual(len(read(out/'durations/per_source.csv')),2)
