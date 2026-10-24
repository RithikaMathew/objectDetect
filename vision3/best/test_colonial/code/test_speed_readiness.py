import csv
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from speed_readiness import parse_location,inspect_sidecars,workbook_references

class SpeedReadinessTests(unittest.TestCase):
    def test_explicit_location_formats_and_invalid_ranges(self):
        self.assertEqual(parse_location('+28.1234-081.4567/'),(28.1234,-81.4567))
        self.assertEqual(parse_location('Latitude: 28.1234\nLongitude=-81.4567'),(28.1234,-81.4567))
        self.assertIsNone(parse_location('2019-08-28 12:05:01'))
        self.assertIsNone(parse_location('+99.0000-181.0000/'))
        self.assertIsNone(parse_location('Distance=35 feet'))

    def test_small_sidecar_preserved_gps_not_verified_and_video_not_extracted(self):
        with tempfile.TemporaryDirectory()as td:
            d=Path(td);entry=dict(gt_site='Test',example_mp4='MioVision Data/Test/Standard_SCU8OG_2019-07-10_0000.001.mp4')
            stem='MioVision Data/Test/Standard_SCU8OG_2019-07-10_0000.013'
            with zipfile.ZipFile(d/'source.zip','w')as z:
                z.writestr(stem+'.cut','Latitude: 28.1234\nLongitude: -81.4567\n')
                z.writestr(stem+'.mp4',b'not a real movie')
            with zipfile.ZipFile(d/'source.zip')as z:records,gps=inspect_sidecars(z,entry,d/'out')
            self.assertEqual(len(gps),1);self.assertEqual(gps[0]['camera_position_verified'],0)
            self.assertEqual(len(list((d/'out').glob('*.cut'))),1)
            self.assertFalse(list((d/'out').glob('*.mp4')))

    def test_oversized_sidecar_not_decompressed(self):
        with tempfile.TemporaryDirectory()as td:
            d=Path(td);entry=dict(gt_site='Test',example_mp4='Data/Test.001.mp4')
            with zipfile.ZipFile(d/'s.zip','w')as z:z.writestr('Data/Test.013.cut','latitude:28\nlongitude:-81\n')
            with zipfile.ZipFile(d/'s.zip')as z:rows,gps=inspect_sidecars(z,entry,d/'out',limit=1)
            self.assertEqual(rows[0]['status'],'SKIPPED_large_sidecar');self.assertEqual(gps,[])
            self.assertFalse(list((d/'out').iterdir()))

    def test_whole_workbook_has_no_pine_named_speed_reference(self):
        root=Path(__file__).resolve().parents[4];rr=workbook_references(root/'Bike Lane Study Counts/bicyclist speeds.xlsx')
        self.assertEqual(len(rr),375)
        self.assertEqual(sum('pine' in r['street'].lower()for r in rr),0)
        self.assertEqual(sum(r['street']=='Colonial'for r in rr),23)
        self.assertTrue(any(r['street']=='West Orange/Park'for r in rr))

if __name__=='__main__':unittest.main()
