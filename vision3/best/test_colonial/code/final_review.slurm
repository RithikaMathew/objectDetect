#!/bin/bash
#SBATCH --job-name=colonial_final_review
#SBATCH --partition=hpg-turin
#SBATCH --account=xiangyan
#SBATCH --qos=xiangyan
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:30:00
#SBATCH --output=logs/final_review_%j.log
set -euo pipefail
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
# Existing saved detector audits only: no downloads, inference or new model sweeps.
python code/rf_person_review.py build --root . --out exp_results/final_review_20261020/rf_boxes
python - <<'PY'
import json,subprocess,sys
from pathlib import Path
pack=Path('exp_results/final_review_20261020/rf_boxes')
frames=json.loads((pack/'manifest.json').read_text())['frames']
out=pack.parent/'zone_previews';out.mkdir()
for clip in sorted({r['clip']for r in frames}):
    image=next(r['image']for r in frames if r['clip']==clip)
    subprocess.run([sys.executable,'code/draw_zones_preview.py','--zones','zones/colonial_north_v2.json',
                    '--image',str(pack/image),'--out',str(out/(clip+'_zones.png'))],check=True)
print('Review folder:',pack.parent.resolve())
PY
python code/speed_gate_setup.py --pack exp_results/final_review_20261020/rf_boxes --out exp_results/final_review_20261020/speed_gate_setup.html
