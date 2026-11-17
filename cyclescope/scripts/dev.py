"""Start local development servers without duplicating already running instances."""
from pathlib import Path
import json
import os
import signal
import socket
import subprocess
import sys
import time
from urllib.request import urlopen

ROOT=Path(__file__).resolve().parents[2]


def listening(port):
    try:
        with socket.create_connection(('localhost',port),timeout=1):return True
    except OSError:return False


def existing_api():
    try:
        with urlopen('http://127.0.0.1:8000/openapi.json',timeout=2) as r:return json.load(r)['info']['title']=='CycleScope'
    except Exception:return False


def existing_frontend():
    try:
        with urlopen('http://localhost:5173',timeout=2) as r:return 'CycleScope' in r.read().decode()
    except Exception:return False


def main():
    owned=[]
    try:
        for port,label,match,command,cwd in [
            (8000,'API',existing_api,[sys.executable,'-m','uvicorn','cyclescope.service.main:app','--reload','--port','8000'],ROOT),
            (5173,'frontend',existing_frontend,['npm','run','dev','--','--host','localhost','--strictPort'],ROOT/'cyclescope/frontend')]:
            if listening(port):
                if not match():raise RuntimeError(f'Port {port} belongs to another service. Stop that service or change ports explicitly.')
                print(f'Reusing existing CycleScope {label} on {port}.',flush=True)
            else:
                owned.append(subprocess.Popen(command,cwd=cwd,start_new_session=True))
                print(f'Starting CycleScope {label} on {port}.',flush=True)
        print('Open http://localhost:5173 . Press Ctrl+C to stop servers started by this launcher.',flush=True)
        if not owned:return
        while all(p.poll() is None for p in owned):time.sleep(.5)
    except KeyboardInterrupt:pass
    except RuntimeError as exc:
        print(str(exc),file=sys.stderr)
        raise SystemExit(1)
    finally:
        for p in owned:
            if p.poll() is None:os.killpg(p.pid,signal.SIGTERM)
        for p in owned:
            try:p.wait(timeout=8)
            except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL)

if __name__=='__main__':main()
