import sys, types, importlib.util, math
from pathlib import Path
import numpy as np, cv2
for m in ("torch","supervision","transformers"):
    sys.modules[m]=types.ModuleType(m)
sys.modules["transformers"].XCLIPModel=object; sys.modules["transformers"].XCLIPProcessor=object
spec=importlib.util.spec_from_file_location("v19",Path(__file__).with_name("xclip_overlay_v19_colonial.py")); v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)

# 1. slice origins cover the frame and respect overlap
o=v.slice_origins(0,0,1920,1080,640,0.2)
print("slices:",len(o), o[:5])
cov=np.zeros((1080,1920),bool)
for x,y,w,h in o: cov[y:y+h,x:x+w]=True
assert cov.all(); assert all(x+w<=1920 and y+h<=1080 for x,y,w,h in o)
assert v.slice_origins(0,0,500,300,640,0.2)==[(0,0,500,300)]
print("coverage ok")

# 2. merge: duplicates removed, small-inside-big kept, different class kept
xy=np.array([[100,100,150,200],[102,101,151,199],[500,500,520,560],[490,480,600,640],[100,100,150,200]],float)
cf=np.array([.9,.6,.5,.8,.4]); cl=np.array([1,1,1,1,0])
k=v.merge_ios(xy,cf,cl); print("kept",k.tolist()); assert k.tolist()==[0,2,3,4]

# 3. sliced_detect with a fake detector that 'sees' a person at a known full-frame location in any slice that contains it whole
class R:
    def __init__(s,b,c,l):
        import types
        t=lambda a: types.SimpleNamespace(cpu=lambda: types.SimpleNamespace(numpy=lambda: a, int=lambda:None))
        s.boxes=types.SimpleNamespace(xyxy=types.SimpleNamespace(cpu=lambda: types.SimpleNamespace(numpy=lambda: b)),
                                      conf=types.SimpleNamespace(cpu=lambda: types.SimpleNamespace(numpy=lambda: c)),
                                      cls=types.SimpleNamespace(int=lambda: types.SimpleNamespace(cpu=lambda: types.SimpleNamespace(numpy=lambda: l))),
                                      __len__=None)
        s._n=len(b)
class Boxes:
    def __init__(s,b,c,l): s.b,s.c,s.l=b,c,l
    def __len__(s): return len(s.b)
    @property
    def xyxy(s): return T(s.b)
    @property
    def conf(s): return T(s.c)
    @property
    def cls(s): return T(s.l)
class T:
    def __init__(s,a): s.a=a
    def cpu(s): return s
    def numpy(s): return s.a
    def int(s): return s
class Res:
    def __init__(s,b,c,l): s.boxes=Boxes(b,c,l)
truth=[(960,500,990,560),(635,100,700,160)]   # 2nd straddles the x=640 slice edge
class FakeDet:
    calls=0
    def predict(s,img,conf,imgsz,verbose,device):
        s.calls+=1
        # image is a slice or full frame: we only know its shape; emulate by checking an embedded marker pixel pattern
        ox,oy=int(img[0,0,0])*10, int(img[0,0,1])*10   # slice origin encoded in pixel (0,0) by the test harness
        bs=[]
        for x1,y1,x2,y2 in truth:
            X1,Y1,X2,Y2=x1-ox,y1-oy,x2-ox,y2-oy
            h,w=img.shape[:2]
            if X1>=0 and Y1>=0 and X2<=w and Y2<=h: bs.append([X1,Y1,X2,Y2])
            elif X2>0 and Y2>0 and X1<w and Y1<h:    # partially visible -> truncated box (what a real detector would give)
                bs.append([max(X1,0),max(Y1,0),min(X2,w),min(Y2,h)])
        a=np.array(bs,float).reshape(-1,4)
        return [Res(a,np.full(len(a),.7),np.ones(len(a),dtype=int))]
# build a frame whose (0,0) pixel encodes its own origin by monkeypatching slicing through a wrapper
frame=np.zeros((1080,1920,3),np.uint8)
class Enc(FakeDet):
    def predict(s,img,conf,imgsz,verbose,device):
        return FakeDet.predict(s,img,conf,imgsz,verbose,device)
# encode origin: since slicing returns views, write markers into the frame at every slice origin
for x,y,w,h in v.slice_origins(0,0,1920,1080,640,0.2):
    frame[y,x]=(x//10,y//10,0)
xy,cf,cl=v.sliced_detect(Enc(),frame,0.25,"cpu",640,0.2,640)
keep=v.merge_ios(xy,cf,cl)
print("sliced found",len(xy),"after merge",len(keep))
found=sorted([tuple(np.round(b).astype(int)) for b in xy[keep]])
print(found)
assert any(abs(b[0]-960)<3 and abs(b[3]-560)<3 for b in found), "person 1 lost"
assert any(abs(b[0]-635)<3 and abs(b[2]-700)<3 for b in found), "edge-straddling person lost (should be seen whole by a neighbouring slice)"
assert len(keep)==2, f"expected exactly 2 after merge, got {len(keep)}"
print("sliced_detect + merge ok (cut-off copies dropped, straddler recovered whole)")

# 4. enhancement
dark=(np.random.rand(120,160,3)*30).astype(np.uint8)
g=v.enhance_frame(dark,"gamma",2.2); c=v.enhance_frame(dark,"clahe",3.0)
print("mean brightness dark/gamma/clahe",dark.mean().round(1),g.mean().round(1),c.mean().round(1)); assert g.mean()>dark.mean()*2 and c.shape==dark.shape and c.dtype==np.uint8

# 5. speed in body heights/s from motion_summary: walker vs rider
fps=29.97
def speed(px_per_s,h):
    fr=list(range(0,int(fps*4))); xs=[100+px_per_s*f/fps for f in fr]; ys=[500]*len(fr)
    return v.motion_summary(fr,xs,ys,h,fps,30.0)["speed_heights_per_s"]
print("walker 1.4 m/s, box h 90px(~1.7m) ->",round(speed(1.4*90/1.7,90),2),"h/s")
print("rider 5 m/s, box h 90px ->",round(speed(5*90/1.7,90),2),"h/s")
assert speed(1.4*90/1.7,90)<1.0 and speed(5*90/1.7,90)>2.0

# 6. motion diagnostic on a synthetic video: a moving white blob on a static noisy background; one blob 'explained' by a detection box
md=v.MotionDiag(fps,warm=30)
rng=np.random.default_rng(0); bgimg=(rng.random((540,960,3))*40+60).astype(np.uint8)
for f in range(1,200):
    fr=bgimg.copy()
    x=100+f*4; cv2.rectangle(fr,(x,300),(x+30,360),(230,230,230),-1)        # unexplained mover (full-res coords doubled below)
    fr=cv2.resize(fr,(1920,1080))
    md.update(fr,f,np.zeros((0,4)))
rows=md.finish(); print("candidates found:",len(rows), [(r['first'],r['last'],round(r['net_px'])) for r in rows][:3]); assert len(rows)>=1 and rows[0]['net_px']>400
md2=v.MotionDiag(fps,warm=30)
for f in range(1,200):
    fr=bgimg.copy(); x=100+f*4; cv2.rectangle(fr,(x,300),(x+30,360),(230,230,230),-1); fr=cv2.resize(fr,(1920,1080))
    box=np.array([[2*x-10,590,2*x+70,730]],float)      # detection covers the blob (full-res coords)
    md2.update(fr,f,box)
assert len(md2.finish())==0; print("motion diag ok: unexplained blob reported, explained blob ignored")
import datetime
cl_=lambda fi: datetime.datetime(2019,7,10,21,15)+datetime.timedelta(seconds=fi/fps)
print(v.MotionDiag.contact_sheet(rows,cl_,"/tmp/cs.png"))
print("ALL TESTS PASSED")
