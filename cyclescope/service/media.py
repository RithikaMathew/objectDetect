"""Media timing and exact, decoded clip selection; no camera-clock guessing."""
import json
import math
from pathlib import Path
import re
import subprocess
from datetime import datetime, timedelta


def probe(path):
    result = subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries',
        'stream=width,height,avg_frame_rate,duration:stream_tags=creation_time:format=duration:format_tags=creation_time',
        '-of','json',str(path)],capture_output=True,text=True,check=True)
    data=json.loads(result.stdout)
    if not data.get('streams'):raise ValueError('The file contains no readable video stream')
    stream=data['streams'][0]
    duration=float(stream.get('duration') or data.get('format',{}).get('duration') or 0)
    if not math.isfinite(duration) or duration<=0:raise ValueError('Video duration is unavailable')
    return dict(duration_s=duration,width=stream['width'],height=stream['height'],
        metadata_creation_time=stream.get('tags',{}).get('creation_time') or data.get('format',{}).get('tags',{}).get('creation_time'),
        clock_note='File creation metadata can describe an export; it is not verified camera capture time.')


def clock_hint(filename):
    match=re.search(r'Standard_[A-Za-z0-9]+_(\d{4}-\d{2}-\d{2})_(\d{2})(\d{2})\.(\d{3})\.(?:mp4|mov)$',Path(filename or '').name,re.I)
    if not match:return None
    try:
        start=datetime.fromisoformat(f'{match[1]}T{match[2]}:{match[3]}:00')+timedelta(hours=int(match[4])-1)
    except ValueError:return None
    return dict(value=start.isoformat(),source='Filename session/chunk convention; inferred, not verified against the camera clock')


def clip_range(duration,start=0,end=None):
    end=duration if end is None else end
    if not all(math.isfinite(x) for x in (duration,start,end)) or start<0 or end<=start or start>=duration or end>duration+.1:
        raise ValueError('Choose a start/end within the video, with end later than start')
    return start,min(end,duration)


def extract(source,destination,start,end):
    # Seek after decoding input for an exact selection, then reset the clip clock.
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(source),'-ss',str(start),'-t',str(end-start),
        '-an','-vf','setpts=PTS-STARTPTS','-fps_mode','passthrough','-c:v','libx264','-crf','18',
        '-pix_fmt','yuv420p','-movflags','+faststart',str(destination)],check=True,capture_output=True)
