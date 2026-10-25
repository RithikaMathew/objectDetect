import unittest,tempfile,json
from pathlib import Path
from unittest.mock import patch
from manual_bicycle_review import positive_bins,prepare
class ManualReviewTests(unittest.TestCase):
 def test_zero_omitted_missing_retained(self):
  rows=[dict(user_type='cyclist',bin_start=str(i),bin_end=str(i+1),count=n,status=status) for i,n,status in [(0,0,'recorded'),(1,2,'recorded'),(2,'','missing')]]
  with patch('manual_bicycle_review.read_xml_xls',return_value={}),patch('manual_bicycle_review.extract',return_value=(rows,[])):
   self.assertEqual([b['start'] for b in positive_bins('x')],['1','2'])
 def test_real_carroll_pack_selects_positive_bin_only(self):
  books=Path('/Users/rithika/Downloads/Bike Lane Study Counts')
  if not books.exists():self.skipTest('Local source workbooks unavailable')
  with tempfile.TemporaryDirectory() as td:
   d=Path(td);batch=d/'batch';batch.mkdir();task=dict(key='s02_carroll_nbl',source=dict(site='Carroll NBL',clock='2019-09-10 12:00:00',video='/not/needed.mp4'))
   (batch/'manifest.json').write_text(json.dumps(dict(tasks=[task])))
   prepare(batch,books,d/'out')
   result=json.loads((d/'out/manifest.json').read_text());self.assertEqual(len(result['entries']),1)
   self.assertEqual(result['entries'][0]['reference']['count'],2)
   self.assertEqual(result['entries'][0]['source_start_seconds'],1800)
   self.assertFalse(result['clips_extracted'])
if __name__=='__main__':unittest.main()
