"""Physical distance / crossing-time speed, matching the study's method."""
import json
import numpy as np


def crossing(a,b,c,d):
    """Fraction along observed motion segment a→b crossing finite gate c→d."""
    a,b,c,d=map(lambda x:np.asarray(x,float),(a,b,c,d))
    r=b-a;s=d-c;den=r[0]*s[1]-r[1]*s[0]
    if abs(den)<1e-9:return None
    q=c-a;t=(q[0]*s[1]-q[1]*s[0])/den;u=(q[0]*r[1]-q[1]*r[0])/den
    return float(t)if 0<=t<=1 and 0<=u<=1 else None


def measure(samples,fps,path,size):
    config=json.loads(path.read_text())
    if config.get('site')!='Colonial North' or config.get('recording_date')!='2019-07-10':raise ValueError('Wrong camera/date for speed gates')
    if not config.get('measurement_source')or not config.get('reviewer'):raise ValueError('Measured gate source/reviewer required')
    scale=np.array(size)/np.array(config['ref_size'])
    estimates=[]
    for gate in config['gates']:
        length=float(gate['length_feet'])
        if length<=0:raise ValueError('Gate distance must be positive')
        events={}
        for key in ('line_a','line_b'):
            line=np.asarray(gate[key],float)*scale
            if line.shape!=(2,2):raise ValueError('Gate lines need two image endpoints')
            times=[]
            for a,b in zip(samples,samples[1:]):
                if (int(b['frame'])-int(a['frame']))/fps>.5:continue
                fraction=crossing([float(a['foot_x']),float(a['foot_y'])],[float(b['foot_x']),float(b['foot_y'])],*line)
                if fraction is not None:
                    time=(int(a['frame'])+fraction*(int(b['frame'])-int(a['frame']))-1)/fps
                    if not times or time-times[-1]>.1:times.append(time)
            events[key]=times
        if len(events['line_a'])==len(events['line_b'])==1:
            seconds=abs(events['line_b'][0]-events['line_a'][0])
            if seconds>0:estimates.append(dict(facility=gate['facility'],seconds=seconds,
                mph=length/seconds*3600/5280,kmh=length*.3048/seconds*3.6))
    if len(estimates)!=1:return dict(mph='',kmh='',status='no_unique_complete_gate_crossing')
    r=estimates[0];return dict(mph=round(r['mph'],3),kmh=round(r['kmh'],3),facility=r['facility'],
                             status='measured_gates_estimate_not_matched_speed_validated')
