"""Resolve and check FFmpeg; optional install is isolated from the YOLO environment."""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

CACHE=Path.home()/'.cache/objectdetect/preview_runtime'


def resolve(install=False,cache=CACHE):
    candidates=[]
    explicit=os.environ.get('FFMPEG_BINARY')
    if explicit:candidates.append(explicit)
    system=shutil.which('ffmpeg')
    if system:candidates.append(system)
    # Discover the packaged executable directly: no import-path or environment mutation.
    candidates += [str(p) for p in sorted((cache/'imageio_ffmpeg/binaries').glob('ffmpeg*')) if p.is_file() and os.access(p,os.X_OK)]
    errors=[]
    for exe in candidates:
        try:
            result=subprocess.run([exe,'-hide_banner','-encoders'],capture_output=True,text=True,timeout=15,check=True)
            if 'libx264' not in result.stdout:raise RuntimeError('libx264 encoder unavailable')
            return str(Path(exe).resolve())
        except (OSError,subprocess.SubprocessError,RuntimeError) as error:errors.append(str(error))
    if install:
        cache.mkdir(parents=True,exist_ok=True)
        subprocess.run([sys.executable,'-m','pip','install','--disable-pip-version-check','--only-binary=:all:','--no-deps','--target',str(cache),'imageio-ffmpeg==0.6.0'],check=True)
        return resolve(False,cache)
    raise RuntimeError('No working FFmpeg with libx264. Run python code/preview_ffmpeg.py --install once on the login node. '+ '; '.join(errors))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--install',action='store_true');a=p.parse_args();print(resolve(a.install))
