import copy
import io
import json
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from fastapi import BackgroundTasks, HTTPException, UploadFile
from pydantic import ValidationError
from cyclescope.service import main, media, repository


class ProcessingTests(unittest.TestCase):
    def test_clip_bounds_and_filename_clock_is_only_a_hint(self):
        self.assertEqual(media.clip_range(120,10,30),(10,30))
        self.assertEqual(media.clip_range(120,0,None),(0,120))
        for a,b in [(-1,10),(10,10),(0,121),(float('nan'),10)]:
            with self.assertRaises(ValueError): media.clip_range(120,a,b)
        self.assertEqual(media.clock_hint('Standard_SCU8OG_2019-07-10_0000.013.mp4')['value'],'2019-07-10T12:00:00')
        self.assertIsNone(media.clock_hint('my_video.mp4'))

    def test_real_extraction_duration_dimensions_and_zero_clock(self):
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp)/'source.mp4';out=Path(temp)/'clip.mp4'
            subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','testsrc2=size=160x120:rate=30:duration=3','-c:v','libx264',str(source)],check=True)
            media.extract(source,out,.5,1.5)
            info=media.probe(out)
            self.assertAlmostEqual(info['duration_s'],1,places=1)
            self.assertEqual((info['width'],info['height']),(160,120))
            import cv2
            cap=cv2.VideoCapture(str(source));cap.set(cv2.CAP_PROP_POS_FRAMES,15);ok,a=cap.read();cap.release()
            cap=cv2.VideoCapture(str(out));valid,b=cap.read();cap.release()
            self.assertTrue(ok and valid)
            self.assertLess(abs(a.astype(float)-b.astype(float)).mean(),4)

    def test_two_jobs_actually_overlap(self):
        barrier=threading.Barrier(2);seen=[]
        def task(jid):
            seen.append(jid);barrier.wait(timeout=3)
        with ThreadPoolExecutor(max_workers=2) as executor,patch.object(main,'workers',executor),patch.object(main,'process',task):
            futures=[main.enqueue('first'),main.enqueue('second')]
            for future in futures:future.result(timeout=4)
        self.assertEqual(set(seen),{'first','second'})

    def state(self):
        def track(tid,cls,x,y):
            return dict(id=tid,cls=cls,deleted=False,source='repository',observations=[dict(frame=i+1,foot_x=x+i/3,foot_y=y,box_w=6,box_h=12,coasted=0)for i in range(91)])
        return dict(status='ready',id='123456abcd',name='synthetic',meta=dict(fps=30,frames=100),
            tracks=[track(1,'cyclist',10,50),track(2,'car',20,50),track(3,'truck',25,60)],decisions={},
            calibration=dict(image_points=[[0,0],[100,0],[100,100],[0,100]],world_points_metres=[[0,0],[100,0],[100,100],[0,100]],regions=[],measurement_source='synthetic'))

    def test_reviewed_speed_retains_computed_and_interaction_evidence(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(main,'DATA',Path(temp)):
            jid='123456abcd';(main.DATA/jid).mkdir();state=self.state();main.save(jid,state)
            before=repository.analyze(state)
            self.assertTrue(before['events'])
            with self.assertRaises(HTTPException):main.set_speed(jid,1,main.SpeedOverride(mph=12))
            after=main.set_speed(jid,1,main.SpeedOverride(mph=12,reason='Independent reviewed timing'))
            self.assertEqual(after['analysis']['speeds']['1']['median_mph'],12)
            self.assertEqual(after['analysis']['computed_speeds'],before['computed_speeds'])
            self.assertEqual(after['analysis']['events'],before['events'])
            self.assertEqual(len(after['speed_audit']),1)
            exported=main.export(jid,'json')
            self.assertEqual(exported['speeds']['1']['source'],'reviewed_override')
            self.assertEqual(exported['computed_speeds']['1']['median_mph'],before['speeds']['1']['median_mph'])
            restored=main.set_speed(jid,1,main.SpeedOverride(mph=None))
            self.assertEqual(restored['analysis']['speeds'],before['speeds'])
            self.assertEqual(len(restored['speed_audit']),2)
        for invalid in [-1,float('nan'),float('inf')]:
            with self.assertRaises(ValidationError):main.SpeedOverride(mph=invalid)

    def test_processing_adds_clip_offset_to_confirmed_clock(self):
        state=self.state();state.update(clip_start_s=600,clip_end_s=1200,session_start='2019-07-10T12:00:00',source_media=dict(duration_s=1800))
        with tempfile.TemporaryDirectory() as temp,patch.object(main,'DATA',Path(temp)),patch.object(main.media,'extract') as extract,patch.object(main.repository,'run',return_value=(state['meta'],state['tracks'])) as run:
            jid=state['id'];(main.DATA/jid).mkdir();main.save(jid,state)
            main.process(jid)
            done=main.load(jid)
            self.assertEqual(done['status'],'ready',done.get('error'))
            self.assertEqual(run.call_args.args[2],'2019-07-10 12:10:00')
            self.assertEqual(done['meta']['source_offset_s'],600)
            self.assertEqual(extract.call_args.args[2:],(600,1200))

    def test_regions_can_be_saved_without_metric_scale(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(main,'DATA',Path(temp)):
            state=self.state();state['calibration']=None;jid=state['id'];(main.DATA/jid).mkdir();main.save(jid,state)
            region=dict(name='sidewalk',points=[[0,0],[100,0],[100,100],[0,100]],color='#aabbcc')
            updated=main.set_regions(jid,main.Regions(regions=[region]))
            self.assertEqual(updated['analysis']['facilities']['1'],'sidewalk')
            self.assertFalse(updated['analysis']['calibrated'])
            self.assertEqual(updated['analysis']['speeds'],{})

    def test_create_queues_without_waiting_and_invalid_clip_does_not_leave_job(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(main,'DATA',Path(temp)),patch.object(main.media,'probe',return_value=dict(duration_s=120)):
            bg=BackgroundTasks()
            created=main.create_job(bg,UploadFile(file=io.BytesIO(b'synthetic'),filename='clip.mp4'),None,10,20)
            self.assertEqual(created['status'],'queued')
            self.assertEqual(len(bg.tasks),1)
            self.assertEqual(main.load(created['id'])['clip_end_s'],20)
            with self.assertRaises(HTTPException):main.create_job(BackgroundTasks(),UploadFile(file=io.BytesIO(b'synthetic'),filename='clip.mp4'),None,50,30)
            self.assertEqual(len(list(main.DATA.iterdir())),1)
