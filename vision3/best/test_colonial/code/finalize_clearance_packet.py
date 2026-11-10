#!/usr/bin/env python3
"""Package the canonical clearance review without duplicating source videos.

The repository preview shares original returned clips. The portable ZIP rewrites
only its own HTML video links and includes copies for standalone review. Existing
analysis tables are preserved; this script does not rerun or fabricate results.
"""
import hashlib
import json
from pathlib import Path
import re
import zipfile

REPO = Path(__file__).resolve().parents[4]


def package(repo=REPO):
    folder = repo/'reports/clearance_pilot/final_review_20261109'
    inputs = repo/'reports/cluster_returns/20261109/CLEARANCE_PILOT_20261109_175030_116203/inputs'
    archive = folder.parent/'clearance_final_review_20261109.zip'
    required = ['START_HERE.md','review.html','reviewed_encounters.csv','speed_baseline_comparison.csv']
    if not all((folder/name).is_file() for name in required):
        raise ValueError('Canonical reviewed analysis is missing; restore it before packaging')
    files = {str(p.relative_to(folder)): p.read_bytes() for p in sorted(folder.rglob('*'))
             if p.is_file() and p.name != 'checksums.json'}
    manifest = {name:hashlib.sha256(data).hexdigest() for name,data in files.items()}
    (folder/'checksums.json').write_text(json.dumps(manifest,indent=2)+'\n')
    # The standalone HTML points into its ZIP, while the repository HTML keeps
    # relative links to the one preserved copy of each original clip.
    page = files['review.html'].decode()
    for stem in ('colonial_124020','colonial_125311','colonial_125350'):
        name = stem+'.mp4'
        video = inputs/name
        if not video.is_file():raise FileNotFoundError(video)
        files['videos/'+name] = video.read_bytes()
        page = re.sub(r'src="[^\"]*/'+re.escape(name)+r'"', 'src="videos/'+name+'"', page)
    files['review.html'] = page.encode()
    files['checksums.json'] = (json.dumps({name:hashlib.sha256(data).hexdigest()
                                        for name,data in files.items()},indent=2)+'\n').encode()
    temporary = archive.with_suffix('.zip.tmp')
    try:
        with zipfile.ZipFile(temporary,'w',compression=zipfile.ZIP_DEFLATED) as z:
            for name,data in files.items():z.writestr('clearance_final_review/'+name,data)
        with zipfile.ZipFile(temporary) as z:
            if z.testzip() is not None:raise ValueError('Portable review ZIP failed verification')
        temporary.replace(archive)
    finally:
        if temporary.exists():temporary.unlink()
    print(archive)


if __name__ == '__main__':
    package()
