#!/bin/bash
# CPU preparation only: one University speed-study source hour, no model job.
set -euo pipefail
ROOT=/orange/xiangyan/rithika/vision/vision3/best/test_colonial
cd "$ROOT"
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
ARCHIVE=/orange/xiangyan/rithika/vision/MioVision_Data.zip
MEMBER='MioVision Data/Bike Lane Study/MioVision Video/SW Speed University/Standard_SCU8PM_2019-09-25_0000/Standard_SCU8PM_2019-09-25_0000.009.mp4'
[ -f "$ARCHIVE" ] || { echo "Missing original ZIP: $ARCHIVE"; exit 1; }
WORK=$(mktemp -d "$ROOT/exp_results/university_speed_prepare_XXXXXX")
unzip -n "$ARCHIVE" "$MEMBER" -d /orange/xiangyan/rithika/vision/pilot_clips
python code/study_batch.py inventory --probe --out "$WORK/inventory"
python - "$WORK/inventory/inventory.csv" "$WORK/selected_hour.csv" <<'PY'
import csv,sys
from pathlib import Path
with open(sys.argv[1])as f:
    reader=csv.DictReader(f);fields=reader.fieldnames
    rows=[r for r in reader if r['site']=='University SW Speed'and Path(r['video']).name=='Standard_SCU8PM_2019-09-25_0000.009.mp4']
if len(rows)!=1 or not rows[0]['probe_status'].startswith('readable_'):
    raise RuntimeError('Selected source is not uniquely readable; inspect inventory before continuing')
with open(sys.argv[2],'x',newline='')as f:
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
PY
python code/site_zone_setup.py --inventory "$WORK/selected_hour.csv" \
  --site 'University SW Speed' --out "$WORK/zone_editor"
python code/study_count_reference.py \
  --workbook '/orange/xiangyan/rithika/vision/Bike Lane Study Counts/University_SW_Speed_701118_09-25-2019.xls' \
  --start '2019-09-25 08:00:00' --end '2019-09-25 09:00:00' --out "$WORK/manual_counts"
cat > "$WORK/NEXT_STEPS.txt" <<'TXT'
Preparation complete. No GPU or detector job was submitted.
Download the zone_editor folder and open index.html -> University SW Speed.
The frame is from source chunk009, expected08:05 by filename-based clock; verify the visible clock.
Inspect whether the measured reference segment/landmarks are identifiable. Mark areas if desired.
The78University sidewalk speed records list55feet, but recording-date/record-person/endpoint links remain unverified.
Do NOT assign55feet to arbitrary visible lane ends or match records by whichever speeds agree.
Send the editor folder or source image for visual assessment; existing Pine Hills detection can continue independently.
Selected_hour.csv can later drive a one-hour pilot using --site 'University SW Speed' --pilot-chunk9 and marked zones.
TXT
cat "$WORK/NEXT_STEPS.txt"
echo "Preparation folder: $WORK"
echo "Download this editor folder: $WORK/zone_editor"
