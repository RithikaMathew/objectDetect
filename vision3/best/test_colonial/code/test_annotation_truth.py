import unittest
from pathlib import Path
from annotation_truth import colonial_truth_bins, truth_text
from stamp_truth_headers import caption


class TruthHeaderTests(unittest.TestCase):
    def test_known_four_bins_use_person_truth(self):
        result = colonial_truth_bins('Standard_SCU8OG_2019-07-10_0000.023.mp4',
                                    '2019-07-10 00:00:00', 15, Path(__file__).resolve().parents[1]/'truth')
        self.assertEqual({b:(v['bic'],v['ped']) for b,v in result.items()},
                         {85:(5,1),56:(1,4),88:(0,5),51:(2,3)})
        self.assertEqual(truth_text(result[88]), 'GT: Cyclists 0 | Pedestrians 5')

    def test_other_site_year_or_bin_never_get_colonial_truth(self):
        for video, date, duration in [('corrine_706_15min.mp4','2025-03-12 08:05:00',15),
            ('Standard_SCU8OG_2019-07-10_0000.023.mp4','2025-03-12 08:05:00',15),
            ('Standard_SCU8OG_2019-07-10_0000.023.mp4','2019-07-10 00:00:00',30)]:
            self.assertEqual(colonial_truth_bins(video,date,duration,'/nonexistent'), {})
        self.assertEqual(truth_text(None), 'GT: not labelled')

    def test_existing_video_caption_uses_date_and_source(self):
        truth=Path(__file__).resolve().parents[1]/'truth'
        file=Path('Standard_SCU8OG_2019-07-10_0000.023/run__night_2200-2215__sahi640__20190710.mp4')
        self.assertEqual(caption(file,truth),'GT: Cyclists 0 | Pedestrians 5')
        other=Path('corrine_706_15min/run__day_0805-0820__sahi864__20250312.mp4')
        self.assertEqual(caption(other,truth),'GT: not labelled')

    def test_legacy_spreadsheet_format_remains_supported(self):
        self.assertEqual(truth_text(dict(bic_bl=2,bic_sw=3,ped=4)), 'GT: Cyclists 5 | Pedestrians 4')


if __name__=='__main__': unittest.main()
