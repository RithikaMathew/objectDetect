import unittest
import numpy as np
from speed_analysis_pass import robust_fit,ground

class SpeedPassTests(unittest.TestCase):
    def test_irregular_times_known_speed(self):
        t=np.array([0,.1,.4,.8,1.2,1.8,2.1]);xy=np.column_stack([3*t,4*t])
        self.assertAlmostEqual(robust_fit(t,xy)['speed'],5*2.2369362921,places=5)

    def test_outlier_resistance(self):
        t=np.linspace(0,4,25);xy=np.column_stack([4*t,t*0]);xy[12]+=[0,15]
        fit=robust_fit(t,xy)
        self.assertLess(abs(fit['speed']-4*2.2369362921),.3)
        self.assertGreater(fit['old'],fit['speed']*1.5)
        self.assertLess(fit['weights'][12],.5)

    def test_scale_shared_multiplicative(self):
        t=np.linspace(0,2,10);px=np.column_stack([t,2*t]);H=np.eye(3)
        a=robust_fit(t,ground(H,px))['speed'];H[:2]*=1.2
        self.assertAlmostEqual(robust_fit(t,ground(H,px))['speed']/a,1.2)

    def test_guards(self):
        for t in ([0,0,2],[0,.5,1],[0,.1,4]):
            with self.assertRaises(ValueError):robust_fit(np.array(t),np.zeros((3,2)))
        H=np.eye(3);H[2]=[1,0,0]
        with self.assertRaises(ValueError):ground(H,np.array([[-1,0],[1,0]]))
