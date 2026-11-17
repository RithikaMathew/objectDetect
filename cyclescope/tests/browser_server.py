"""Isolated browser fixture server. Synthetic inference is NEVER used by the real app."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import os
os.environ['DATA_DIR']='/tmp/cyclescope-browser-data'
from cyclescope.service import main
import cv2
import time


def synthetic_inference(video,progress,session_start=None):
    time.sleep(.2)
    cap=cv2.VideoCapture(video)
    meta=dict(fps=cap.get(cv2.CAP_PROP_FPS),frames=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
              width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),pipeline='synthetic_browser_test')
    cap.release()
    return meta,[]

main.repository.run=synthetic_inference
if __name__=='__main__':
    import uvicorn
    uvicorn.run(main.app,host='127.0.0.1',port=8001)
