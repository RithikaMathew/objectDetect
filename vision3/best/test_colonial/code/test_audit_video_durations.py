import unittest
from unittest.mock import patch
from subprocess import CompletedProcess
from audit_video_durations import probe, summaries

class DurationTests(unittest.TestCase):
    def test_partial_is_not_total(self):
        cameras=[dict(camera='Columbia',speed_reference_candidate='Columbia')]
        rows=[dict(site='Columbia',audit_status='MEASURED',duration_seconds=1800),dict(site='Columbia',audit_status='ERROR',duration_seconds='')]
        self.assertEqual(summaries(rows,cameras)[0]['exact_total_hours'],'')
        rows[1].update(audit_status='MEASURED',duration_seconds=900)
        self.assertEqual(summaries(rows,cameras)[0]['exact_total_hours'],.75)

    def test_readers(self):
        with patch('audit_video_durations.subprocess.run',return_value=CompletedProcess([],0,'{"format":{"duration":"123.456"}}','')):
            self.assertEqual(probe('clip','ffprobe',True),123.456)
        with patch('audit_video_durations.subprocess.run',return_value=CompletedProcess([],1,'','Duration: 01:02:03.45, start: 0')):
            self.assertEqual(probe('clip','ffmpeg',False),3723.45)

    def test_invalid_refused(self):
        with patch('audit_video_durations.subprocess.run',return_value=CompletedProcess([],0,'{"format":{"duration":"NaN"}}','')):
            with self.assertRaises(ValueError):probe('clip','ffprobe',True)
