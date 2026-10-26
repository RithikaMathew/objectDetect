import csv
import json
from pathlib import Path
import tempfile
import unittest
from export_manual_calibrations import export

class ExportTests(unittest.TestCase):
    def test_small_export_keeps_full_bins_and_camera_provenance(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);site=root/'s00_test';cal=site/'calibration';cal.mkdir(parents=True)
            (root/'manifest.json').write_text(json.dumps(dict(tasks=[dict(key='s00_test',reference_site='Test',source=dict(site='Test camera',clock='2019-01-01 12:00:00'))])))
            (cal/'calibration.json').write_text(json.dumps(dict(H=[[1,0,0],[0,1,0],[0,0,1]],geometry_check_passed=True,hull=['not needed'])))
            w=site/'windows/w00';w.mkdir(parents=True)
            with (w/'source_bin_counts.csv').open('w') as f:
                fields=['bin_start','bin_end','seconds_covered','bicyclists_total'];writer=csv.DictWriter(f,fields);writer.writeheader()
                for sec in (0,900):writer.writerow(dict(bin_start='2019-01-01 12:00:00',bin_end='2019-01-01 12:15:00',seconds_covered=sec,bicyclists_total=2))
            result=export(root)
            self.assertEqual(len(result['automatic_count_bins']),1)
            self.assertEqual(result['calibrations']['s00_test']['camera'],'Test camera')
            self.assertNotIn('hull',result['calibrations']['s00_test']['calibration'])
            self.assertEqual(result['automatic_comparison'],[])

if __name__=='__main__':unittest.main()
