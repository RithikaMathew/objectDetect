(yolo_env) [rmathew1@login7 vision]$ python validate_counts.py \
    --session-dir pilot_output/sessions/BL_Colonial_2019-07-10 \
    --video-folder "BL Colonial" --date 2019-07-10

==================================================================
BL Colonial  2019-07-10
==================================================================
chunks processed : 48 of 48 in the session
PIPELINE count   : 88 cyclist tracks
  (rejected      : 821 cyclist-class tracks failed confirmation)
GROUND TRUTH     : 89 cyclists  (site 'Colonial North')
  by facility    : {'bike_lane': 47, 'sidewalk': 42}

ERROR            : -1  (-1.1%)

per-chunk counts (chunk: n):
  001:1    002:2    003:1    004:0    005:1    006:2    007:1    008:4    009:0    010:1  
  011:7    012:1    013:7    014:7    015:6    016:0    017:5    018:0    019:3    020:1  
  021:1    022:1    023:0    024:0    025:0    026:0    027:0    028:0    029:1    030:0  
  031:1    032:1    033:0    034:1    035:2    036:0    037:4    038:1    039:1    040:1  
  041:5    042:4    043:2    044:7    045:3    046:2    047:0    048:0  

==================================================================
1 complete session(s): pipeline 88 vs ground truth 89  (-1.1%)
mean absolute percentage error per session: 1.1%
Wrote count_validation.csv
(yolo_env) [rmathew1@login7 vision]$ python plan_cyclist_clips.py \
  --session-dir pilot_output/sessions/BL_Colonial_2019-07-10 \
  --video-dir "pilot_clips/MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/Standard_SCU8OG_2019-07-10_0000"

sbatch --array=0-<N>%12 run_render_clips.slurm     # <N> printed by the line above
Chunks with results : 48
Clips planned       : 88  (88 counted, 0 rejected)
Total footage        : 1025s  (~923 MB annotated, rough)
Wrote cyclist_clips.txt

Submit with:
  sbatch --array=0-87%12 run_render_clips.slurm

First few:
  Standard_SCU8OG_2019-07-10_0000.001.mp4  1595.60-1607.94s  COUNTED #2756 cyclist hits=47 maxc=0.853 meanc=0.420 exc=10.96
  Standard_SCU8OG_2019-07-10_0000.002.mp4  840.51-848.18s  COUNTED #1215 cyclist hits=16 maxc=0.848 meanc=0.425 exc=16.74
  Standard_SCU8OG_2019-07-10_0000.002.mp4  1607.44-1616.61s  COUNTED #2318 cyclist hits=22 maxc=0.601 meanc=0.217 exc=2.72
  Standard_SCU8OG_2019-07-10_0000.003.mp4  2947.95-2954.45s  COUNTED #3897 cyclist hits=7 maxc=0.561 meanc=0.293 exc=1.77
  Standard_SCU8OG_2019-07-10_0000.005.mp4  20.86-27.86s  COUNTED #31 cyclist hits=12 maxc=0.676 meanc=0.349 exc=3.24
bash: N: No such file or directory
(yolo_env) [rmathew1@login7 vision]$ 