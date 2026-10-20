#!/usr/bin/env python3
"""One-job RF-DETR Medium matched-frame audit. Dry-run unless --go.

Pretrained COCO proposals only, not end-to-end cyclist accuracy. Reuses the
Grounding DINO frame selection and baseline overlays. Never modifies yolo_env.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import sysconfig
import traceback

VERSION = '1.11.2'


def selected_proposals(detections, names):
    """Resolve COCO names rather than assuming contiguous numeric category IDs."""
    labels = [names[int(i)] for i in detections.class_id]
    keep = [i for i, label in enumerate(labels) if label in ('person', 'bicycle', 'motorcycle')]
    return dict(boxes=detections.xyxy[keep], scores=detections.confidence[keep],
                text_labels=[labels[i] for i in keep])


def inputs(root):
    from eval_truth import CLIPS
    from submit_research import VIDEO_DIR
    return [(clip, VIDEO_DIR / f'Standard_SCU8OG_2019-07-10_0000.{cc["chunk"]:03d}.mp4')
            for clip, cc in CLIPS.items()]


def audit_all(root, out, tiled=False):
    import importlib.metadata
    import torch
    from PIL import Image
    from rfdetr import RFDETRMedium
    from rfdetr.assets.coco_classes import COCO_CLASSES
    from grounding_audit import audit
    if not torch.cuda.is_available():
        raise RuntimeError('An allocated CUDA GPU is required')
    cache = root / '.research_models/rfdetr'
    os.environ['RF_HOME'] = str(cache)
    model = RFDETRMedium(device='cuda')
    base_infer = lambda image: selected_proposals(model.predict(image, threshold=.3), COCO_CLASSES)
    from proposal_tiling import tiled_proposals
    infer = (lambda image: tiled_proposals(image, base_infer)) if tiled else base_infer
    infer(Image.new('RGB', (720, 480)))
    checkpoints = {}
    for path in cache.rglob('*'):
        if path.is_file() and path.suffix in ('.pth', '.pt', '.safetensors'):
            digest = hashlib.sha256()
            with path.open('rb') as stream:
                for block in iter(lambda: stream.read(1024*1024), b''): digest.update(block)
            checkpoints[str(path)] = digest.hexdigest()
    info = dict(display_name='RF-DETR Medium '+('full + tiled proposals' if tiled else 'proposals'),
                tiling=dict(size=320,overlap=.25,nms_iou=.5) if tiled else None, package=importlib.metadata.version('rfdetr'),
                torch=torch.__version__, threshold=.3, checkpoint_sha256=checkpoints)
    ready = out / 'model.json'
    ready.write_text(json.dumps(info, indent=2))
    summaries = {}
    for clip, video in inputs(root):
        target = out / clip
        audit(root, ready, clip, video, target, backend=infer)
        summaries[clip] = json.loads((target / 'summary.json').read_text())
    rows = ['# RF-DETR matched-frame audit', '',
            'Pretrained Medium, threshold 0.30. Same encounter/background frames as Grounding DINO.',
            ('Full-frame + 320px tiles, overlap .25, class-aware NMS IoU .50.' if tiled else
             'Full-frame inference only; the saved b4 comparator includes SAHI/tracking.'), '',
            '| Clip | Frames | Proposals | Low overlap with saved b4 tracks |',
            '|---|---:|---:|---:|']
    for clip, s in summaries.items():
        rows.append(f'| {clip} | {s["frames"]} | {s["proposals"]} | {s["low_overlap_proposals"]} |')
    rows += ['', 'Open each clip folder for side-by-side JPGs and proposals.csv.',
             'Low overlap is NOT a confirmed miss; repeated boxes are NOT unique people.',
             'Person, bicycle and motorcycle are separate COCO categories; bicycle boxes do not prove riders.',
             'No cyclist accuracy, AP or improvement claim is possible without box/visual adjudication.',
             'Inspect night 14:21–14:26 and 14:47–14:58 first; compare the existing Grounding DINO images.',
             'Keep b4_combo_static5 as the counting reference pending review.']
    (out / 'RESULTS.md').write_text('\n'.join(rows)+'\n')


def worker(root, out, tiled=False):
    status = out / 'status.json'
    status.write_text(json.dumps(dict(state='RUNNING')))
    try:
        venv = root / '.research_env' / out.name
        subprocess.run([sys.executable, '-m', 'venv', '--system-site-packages', str(venv)], check=True)
        python = venv / 'bin/python'
        site = Path(subprocess.check_output([str(python), '-c',
                    'import sysconfig; print(sysconfig.get_path("purelib"))'], text=True).strip())
        (site / 'working_yolo_environment.pth').write_text('\n'.join(dict.fromkeys(
            sysconfig.get_path(k) for k in ('purelib','platlib'))) + '\n')
        # Preserve the working CUDA Torch and torchvision versions in this isolated environment.
        constraints = out / 'constraints.txt'
        import importlib.metadata
        constraints.write_text('\n'.join(f'{p}=={importlib.metadata.version(p)}'
                                         for p in ('torch','torchvision'))+'\n')
        subprocess.run([str(python), '-m', 'pip', 'install', '-c', str(constraints),
                        f'rfdetr=={VERSION}'], check=True)
        with (out / 'packages.txt').open('w') as f:
            subprocess.run([str(python), '-m', 'pip', 'freeze'], stdout=f, check=True)
        subprocess.run([str(python), str(Path(__file__).resolve()), '--root', str(root),
                        '--out', str(out), '--audit-all'] + (['--tiled'] if tiled else []), check=True)
    except BaseException:
        status.write_text(json.dumps(dict(state='FAILED', error=traceback.format_exc()), indent=2))
        raise
    status.write_text(json.dumps(dict(state='SUCCEEDED', report=str(out/'RESULTS.md')), indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument('--tag', default='rfdetr_oct19')
    ap.add_argument('--go', action='store_true')
    ap.add_argument('--tiled', action='store_true', help='full-frame plus 320px tiles; default tag rfdetr_tiled_oct19')
    ap.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    ap.add_argument('--audit-all', action='store_true', help=argparse.SUPPRESS)
    ap.add_argument('--out', type=Path, help=argparse.SUPPRESS)
    a = ap.parse_args(); root = a.root.resolve()
    if a.audit_all: return audit_all(root, a.out, a.tiled)
    if a.worker: return worker(root, a.out, a.tiled)
    if a.tiled and a.tag == "rfdetr_oct19": a.tag = "rfdetr_tiled_oct19"
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', a.tag): ap.error('invalid tag')
    out = root / 'logs' / a.tag
    print(f'One GPU job: isolated rfdetr=={VERSION}, four matched-frame audits (tiled={a.tiled}), final RESULTS.md at {out}')
    if not a.go: return
    from eval_truth import CLIPS
    required = []
    for clip, video in inputs(root):
        required.extend([video, root / CLIPS[clip]['truth']])
        matches = list((root/'counts/b4_combo_static5').glob(f'*.{CLIPS[clip]["chunk"]:03d}_trajectories.csv'))
        if len(matches) != 1: raise RuntimeError(f'Need one baseline trajectories file for {clip}')
        required.extend(matches)
    activation = root.parents[2] / 'yolo_env/bin/activate'
    required.append(activation)
    missing = [str(p) for p in required if not p.is_file()]
    if missing: raise FileNotFoundError('\n'.join(missing))
    out.mkdir(parents=True, exist_ok=False)  # Prevent duplicate submissions.
    command = 'set -euo pipefail\nsource '+shlex.quote(str(activation))+'\n'+shlex.join([
        'python', str(Path(__file__).resolve()), '--root', str(root), '--out', str(out), '--worker'] + (['--tiled'] if a.tiled else []))
    (out / 'job.sh').write_text('#!/bin/bash\n'+command+'\n')
    try:
        result = subprocess.run(['sbatch','--parsable','--partition=hpg-turin','--account=xiangyan',
            '--qos=xiangyan','--gpus=1','--cpus-per-task=4','--mem=48G','--time=06:00:00',
            '--job-name='+a.tag,'--output='+str(out/'job_%j.log'), str(out/'job.sh')],
            check=True, capture_output=True, text=True)
    except BaseException:
        (out/'status.json').write_text(json.dumps(dict(state='SUBMISSION_FAILED', error=traceback.format_exc())))
        raise
    job = result.stdout.strip()
    (out/'submission.json').write_text(json.dumps(dict(job_id=job, root=str(root), version=VERSION),indent=2))
    print('Submitted', job)


if __name__ == '__main__': main()
