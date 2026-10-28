import unittest
from inventory_miovision_archive import inventory,classify

class FullArchiveTests(unittest.TestCase):
    def test_actual_year_not_category(self):
        r=classify('MioVision Data/2022 Data/Corrine/North/Standard_SCU8PM_2021-04-13_0000/Standard_SCU8PM_2021-04-13_0000.001.mp4')
        self.assertEqual(r['recording_years'],'2021');self.assertEqual(r['site_folder'],'Corrine/North')

    def test_new_hardware_and_crossyear(self):
        names=['MioVision Data/2025 Data/Corrine Dr/MIOP000706_2025_03_12-0000/MIOP000706_2025_03_12-0000.001.mp4','MioVision Data/2026 Data/Corrine Dr/MIOP000706_2026_03_12-0000/MIOP000706_2026_03_12-0000.001.mp4']
        _,groups=inventory(names)
        self.assertEqual(len(groups),1);self.assertEqual(groups[0]['years'],'2025;2026')

    def test_unknown_and_nonvideos(self):
        rows,groups=inventory(['MioVision Data/2025 Data/Unknown/clip.mp4','MioVision Data/2025 Data/Unknown/clip.jpg'])
        self.assertEqual(len(rows),1);self.assertEqual(groups[0]['years'],'Unknown')
        self.assertEqual(groups[0]['unknown_date_files'],1)

    def test_bike_lane_nested_multipart(self):
        r=classify('MioVision Data/Bike Lane Study/MioVision Video/BL Columbia/Standard_SCU8PM_2019-09-10_0000.02/Standard_SCU8PM_2019-09-10_0000.02.001.mp4')
        self.assertEqual(r['site_folder'],'BL Columbia');self.assertEqual(r['recording_years'],'2019')
