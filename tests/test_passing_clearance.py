import unittest
from pipeline.passing_clearance import calculate


class ClearanceTests(unittest.TestCase):
    def setUp(self):
        self.cal = dict(units='m', axes='road_aligned', reviewed=True,
                        calibration_id='c1', source_id='clip', evidence='survey + reviewed footprint markings')

    def row(self, track, cls, t=0, s_min=0, s_max=2, l_min=0, l_max=1):
        return dict(source_id='clip', track_id=str(track), calibration_id='c1',
                    geometry_reviewed='yes', facility='sidewalk',
                    **{'class': cls}, t=t, s_min=s_min, s_max=s_max, l_min=l_min, l_max=l_max)

    def test_edges_and_sample_minimum_all_facilities(self):
        rows = [self.row(1, 'cyclist'), self.row(2, 'car', l_min=2, l_max=4),
                self.row(1, 'cyclist', t=1), self.row(2, 'car', t=1, l_min=1.5, l_max=3.5)]
        result = calculate(rows, self.cal)[0]
        self.assertEqual(result['min_sampled_clearance_m'], .5)
        self.assertEqual(result['alongside_samples'], 2)
        self.assertEqual(result['cyclist_facility'], 'sidewalk')

    def test_no_pair_across_time_or_longitudinal_gap(self):
        self.assertEqual(calculate([self.row(1, 'bicycle'), self.row(2, 'car', t=1)], self.cal), [])
        self.assertEqual(calculate([self.row(1, 'bicycle'), self.row(2, 'car', s_min=3, s_max=5)], self.cal), [])

    def test_overlap_is_zero_not_collision_claim(self):
        result = calculate([self.row(1, 'cyclist'), self.row(2, 'car')], self.cal)[0]
        self.assertEqual(result['min_sampled_clearance_m'], 0)
        self.assertIn('requires_video_review', result['status'])

    def test_reject_unreviewed_or_wrong_source(self):
        for change in ({'reviewed': False}, {'source_id': 'other'}, {'units': 'px'}):
            with self.assertRaises(ValueError):
                calculate([self.row(1, 'cyclist')], {**self.cal, **change})
        row = self.row(1, 'cyclist')
        with self.assertRaises(ValueError):
            calculate([row, row], self.cal)


if __name__ == '__main__':
    unittest.main()
