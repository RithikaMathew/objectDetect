import unittest
from analyze_manual_bicycles import split_encounters,speed

class ManualAnalysisTests(unittest.TestCase):
    def test_owner_reused_ids_split_only_distant_encounters(self):
        points=[dict(seconds=t) for t in (540,540.2,540.4,833,833.2)]
        self.assertEqual([len(p) for p in split_encounters(points)],[3,2])
        self.assertEqual(len(split_encounters([dict(seconds=t) for t in (1,2,3)])),1)

    def test_known_metric_speed_does_not_use_workbook(self):
        points=[dict(seconds=t,x=2*t,y=0) for t in (0,1,2)]
        cal=dict(H=[[1,0,0],[0,1,0],[0,0,1]],geometry_check_passed=True)
        mph,status=speed(points,cal)
        self.assertAlmostEqual(mph,4.4738725842)
        self.assertEqual(status,'EXPLORATORY_UNVALIDATED_ROAD_PLANE')

    def test_missing_calibration_not_zero(self):
        points=[dict(seconds=t,x=t,y=0) for t in (0,1,2)]
        self.assertEqual(speed(points,None),('','CALIBRATION_NOT_IN_REVIEW_PACK'))

    def test_duplicate_timestamps_and_short_tracks_refused(self):
        cal=dict(H=[[1,0,0],[0,1,0],[0,0,1]],geometry_check_passed=True)
        self.assertEqual(speed([dict(seconds=t,x=t,y=0) for t in (0,0,2)],cal)[1],'DUPLICATE_TIME_REVIEW_REQUIRED')
        self.assertEqual(speed([dict(seconds=t,x=t,y=0) for t in (0,.2,.4)],cal)[0],'')

    def test_crossing_horizon_refused(self):
        cal=dict(H=[[1,0,0],[0,1,0],[1,0,-1]],geometry_check_passed=True)
        self.assertEqual(speed([dict(seconds=t,x=t,y=1) for t in (0,.5,2)],cal)[1],'INVALID_PROJECTION')

if __name__=='__main__':unittest.main()
