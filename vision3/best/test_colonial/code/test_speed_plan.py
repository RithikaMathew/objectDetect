import unittest
import numpy as np
from speed_plan import marking_check,wheel_check,wheel_curve,bootstrap_difference

class PlanTests(unittest.TestCase):
    def test_marking_scale(self):
        result=marking_check(np.eye(3),dict(image_endpoints=[[0,0],[3,4]],length_metres=10,length_kind='assumed_standard',source='synthetic'))
        self.assertEqual(result['implied_scale_multiplier'],2)
        with self.assertRaises(ValueError):marking_check(np.eye(3),dict())

    def test_vertical_wheel(self):
        P=np.array([[100.,0,0,0],[0,0,-100,1000],[0,1,0,10]])
        H=np.linalg.inv(P[:,[0,1,3]]);contact=np.array([2.,10.]);q=P@np.r_[contact,0,1]
        item=dict(outline_reviewed=True,source='synthetic known wheel',image_undistorted=True,world_convention='metres_Z_up',projection_matrix=P.tolist(),contact_pixel=(q[:2]/q[2]).tolist(),outline_pixels=wheel_curve(P,contact,.335,.7).tolist(),diameter_prior_metres=[.65,.70])
        result=wheel_check(H,item)
        self.assertAlmostEqual(result['fitted_diameter_metres'],.67,delta=.02)
        item['outline_reviewed']=False
        with self.assertRaises(ValueError):wheel_check(H,item)

    def test_small_sample_and_sign(self):
        r=bootstrap_difference([2],[4,5],np.random.default_rng(1))
        self.assertEqual(r['low'],'');self.assertLess(r['difference'],0)
        r=bootstrap_difference([2,2],[4,4],np.random.default_rng(1))
        self.assertEqual(r['low'],-2);self.assertEqual(r['high'],-2)
