import unittest
from exploratory_gate_check import events

class CrossingChecks(unittest.TestCase):
    def samples(self, end_frame=4):
        return [dict(frame='1',foot_x='0',foot_y='5',_s=2.0),
                dict(frame=str(end_frame),foot_x='10',foot_y='5',_s=2.0+(end_frame-1)/10)]

    def test_crossing_uses_clip_seconds(self):
        self.assertAlmostEqual(events(self.samples(),10,[[5,0],[5,10]])[0],2.15)

    def test_finite_gate_does_not_extend_across_scene(self):
        self.assertEqual(events(self.samples(),10,[[5,20],[5,30]]),[])

    def test_missing_track_gap_is_not_interpolated(self):
        self.assertEqual(events(self.samples(20),10,[[5,0],[5,10]]),[])

if __name__=='__main__':
    unittest.main()
