import csv
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from audit_missing_speed import make_audit

class MissingAuditTests(unittest.TestCase):
    def test_missing_manual_gets_short_clue_without_model_or_video_read(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);inputs=root/'inputs.json';points=root/'points.json'
            entry=dict(key='s11_west_orange_2019-10-15_121500',camera='West Orange Path',source=dict(reference_location='West Orange/Park'),reference=dict(start='2019-10-15 12:15:00',end='2019-10-15 12:30:00',count=2))
            inputs.write_text(json.dumps(dict(entries=[entry])));points.write_text(json.dumps(dict(observations=[],encounters=[])))
            candidate=dict(camera='West Orange Path',source_clock='2019-10-15 12:00:00',video='missing_not_opened.mp4',track=dict(first_time='2019-10-15 12:20:00',last_time='2019-10-15 12:20:04',track_id='7',counted='1'),reasons=[],annotated_clips=[])
            bundle=dict(automatic_comparison=[dict(location='Rinehart/CST',model_candidate_mean_mph='',state='TARGET_NOT_REACHED_WITHIN_LIMIT',counted_candidate_tracks='0',found_candidate_tracks='3')],automatic_partial_count_bins=[],candidate_audit=[candidate])
            with patch('audit_missing_speed.export',return_value=bundle),patch('audit_missing_speed.resolve',side_effect=AssertionError('No video extraction requested')):
                make_audit(root,inputs,points,root/'out')
            self.assertEqual(len(json.loads((root/'out/review_clues.json').read_text())),1)
            with (root/'out/missing_values.csv').open() as f:rows=list(csv.DictReader(f))
            self.assertIn('rejected',rows[0]['reason']);self.assertIn('no JSON',rows[1]['reason'])
            self.assertFalse(list((root/'out').glob('*.mp4')))

if __name__=='__main__':unittest.main()
