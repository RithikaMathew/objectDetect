import tempfile
from pathlib import Path
import unittest
import cv2
import numpy as np
from manual_flow_speed import endpoint_speed,flow_step,patch_features,check_drift,track

class FlowTests(unittest.TestCase):
    def test_known_translation_tracks_seed_without_future_points(self):
        gray=np.random.default_rng(17).integers(0,256,(160,200),dtype=np.uint8)
        moved=cv2.warpAffine(gray,np.float32([[1,0,3],[0,1,2]]),(200,160))
        seed=np.array([90.,95.]);features=patch_features(gray,seed)
        point,_,status=flow_step(gray,moved,features,seed)
        self.assertEqual(status,'ok');np.testing.assert_allclose(point,[93,97],atol=.2)

    def test_future_clicks_only_check_and_reject_drift(self):
        samples=[dict(frame=f,foot_x=float(f),foot_y=0.) for f in range(4)]
        points=[dict(seconds=0,x=0,y=0),dict(seconds=1,x=20,y=0)]
        accepted,checks=check_drift(samples,points,3,max_error=5)
        self.assertFalse(accepted);self.assertEqual(checks[0]['error_px'],17)
        accepted,_=check_drift(samples,[points[0],dict(seconds=2,x=6,y=0)],3)
        self.assertFalse(accepted)

    def test_endpoint_distance_uses_time_and_scale_not_workbook(self):
        points=[dict(seconds=0,x=0,y=0),dict(seconds=2,x=4,y=0)]
        cal=dict(H=[[1,0,0],[0,1,0],[0,0,1]],geometry_check_passed=True)
        self.assertAlmostEqual(endpoint_speed(points,cal),4.4738725842)
        self.assertEqual(endpoint_speed(points,None),'')

    def test_textureless_image_fails_instead_of_inventing_motion(self):
        image=np.zeros((100,100),np.uint8);features=patch_features(image,[50,50])
        point,_,reason=flow_step(image,image,features,[50,50])
        self.assertIsNone(point);self.assertEqual(reason,'insufficient_features')

    def test_real_video_decode_translation_and_drift_check(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'synthetic.mp4';writer=cv2.VideoWriter(str(path),cv2.VideoWriter_fourcc(*'mp4v'),20,(200,160))
            texture=np.random.default_rng(27).integers(0,256,(160,200),dtype=np.uint8)
            for f in range(41):
                image=cv2.warpAffine(texture,np.float32([[1,0,f],[0,1,0]]),(200,160));writer.write(cv2.cvtColor(image,cv2.COLOR_GRAY2BGR))
            writer.release()
            points=[dict(seconds=t,x=70+20*t,y=95,width=200,height=160) for t in (0,1,2)]
            samples,info=track(path,points,Path(td)/'unused.mp4')
            self.assertEqual(info['tracking_stop'],'complete')
            self.assertTrue(check_drift(samples,points,20,max_error=2)[0])

if __name__=='__main__':unittest.main()
