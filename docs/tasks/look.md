--format=JobID,JobName%22,State,Elapsed | grep -v batch | tail -20
grep -L "Final counts" logs/*461410{42,48,49,50,51,52,53,54,55,56,57,58,59,60}*
ls busy
46141053_23            colonial_v19  COMPLETED   00:46:38 
46141053_23+                 extern  COMPLETED   00:46:38 
46141054_13            colonial_v19  COMPLETED   00:45:45 
46141054_13+                 extern  COMPLETED   00:45:45 
46141055_22            colonial_v19  COMPLETED   00:47:52 
46141055_22+                 extern  COMPLETED   00:47:52 
46141056_23            colonial_v19  COMPLETED   00:47:08 
46141056_23+                 extern  COMPLETED   00:47:08 
46141057_22            colonial_v19  COMPLETED   00:50:13 
46141057_22+                 extern  COMPLETED   00:50:13 
46141058_23            colonial_v19  COMPLETED   00:49:24 
46141058_23+                 extern  COMPLETED   00:49:24 
46141059_22            colonial_v19     FAILED   00:04:43 
46141059_22+                 extern  COMPLETED   00:04:43 
46141060_23            colonial_v19     FAILED   00:04:07 
46141060_23+                 extern  COMPLETED   00:04:07 
46141085                  pick_busy     FAILED   00:00:15 
46141085.ex+                 extern  COMPLETED   00:00:15 
46201725          postgres-rmathew1 CANCELLED+   01:58:21 
46201725.ex+                 extern  COMPLETED   01:58:21 
grep: logs/*46141042*: No such file or directory
grep: logs/*46141048*: No such file or directory
grep: logs/*46141049*: No such file or directory
grep: logs/*46141050*: No such file or directory
grep: logs/*46141051*: No such file or directory
grep: logs/*46141052*: No such file or directory
grep: logs/*46141053*: No such file or directory
grep: logs/*46141054*: No such file or directory
grep: logs/*46141055*: No such file or directory
grep: logs/*46141056*: No such file or directory
grep: logs/*46141057*: No such file or directory
grep: logs/*46141058*: No such file or directory
grep: logs/*46141059*: No such file or directory
grep: logs/*46141060*: No such file or directory
ls: cannot access 'busy': No such file or directory
[rmathew1@login11 code]$ python code/eval_truth.py --root . --runs exp0_base,b4_combo_static5,b5_nospeed,b5_noveto --baseline exp0_base | sed -n '/## Summary/,/## Detail/p'
python code/eval_truth.py --root . --runs b4_combo_static5,b5_bright_gamma,b5_bright_clahe,b5_bright_zerodce --baseline exp0_base | sed -n '/## Summary/,/## Detail/p'
bash: python: command not found
bash: python: command not found
[rmathew1@login11 code]$ cd /orange/xiangyan/rithika/vision
source yolo_env/bin/activate
python -c "import scipy; print('scipy OK')"
cd vision3
export ROOT=/orange/xiangyan/rithika/vision/vision3/best/test_colonial 
cd $ROOT
scipy OK
(yolo_env) [rmathew1@login11 test_colonial]$ python code/eval_truth.py --root . --runs exp0_base,b4_combo_static5,b5_nospeed,b5_noveto --baseline exp0_base | sed -n '/## Summary/,/## Detail/p'
python code/eval_truth.py --root . --runs b4_combo_static5,b5_bright_gamma,b5_bright_clahe,b5_bright_zerodce --baseline exp0_base | sed -n '/## Summary/,/## Detail/p'
## Summary (person level; FOUND = counted with the right class; motorcycle scored as cyclist)

| run | clip | cyclists found | pedestrians found | wrong class | detected, not counted | missed | extra counted | counted bic/ped | runtime min |
|---|---|---|---|---|---|---|---|---|---|
| exp0_base | night | 0/5 | 0/1 | 0 | 4 | 2 | 0 | 0/0 | 30.1 |
| exp0_base | day | 1/1 | 2/4 | 0 | 2 | 0 | 0 | 1/2 | 30.6 |
| b4_combo_static5 | night | 4/5 | 0/1 | 1 | 1 | 0 | 0 | 5/0 | 42.9 |
| b4_combo_static5 | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 42.0 |
| b4_combo_static5 | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 0 | 0/5 | 41.8 |
| b4_combo_static5 | day_holdout_1245 | 2/2 | 3/3 | 0 | 0 | 0 | 0 | 2/3 | 41.3 |
| b5_nospeed | night | 3/5 | 0/1 | 2 | 1 | 0 | 0 | 4/1 | 42.0 |
| b5_nospeed | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 41.5 |
| b5_nospeed | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 0 | 0/5 | 42.0 |
| b5_nospeed | day_holdout_1245 | 2/2 | 2/3 | 1 | 0 | 0 | 0 | 3/2 | 41.5 |
| b5_noveto | night | 4/5 | 0/1 | 1 | 1 | 0 | 0 | 5/0 | 41.8 |
| b5_noveto | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 42.7 |
| b5_noveto | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 0 | 0/5 | 42.1 |
| b5_noveto | day_holdout_1245 | 2/2 | 2/3 | 1 | 0 | 0 | 0 | 3/2 | 40.7 |

## Detail
## Summary (person level; FOUND = counted with the right class; motorcycle scored as cyclist)

| run | clip | cyclists found | pedestrians found | wrong class | detected, not counted | missed | extra counted | counted bic/ped | runtime min |
|---|---|---|---|---|---|---|---|---|---|
| b4_combo_static5 | night | 4/5 | 0/1 | 1 | 1 | 0 | 0 | 5/0 | 42.9 |
| b4_combo_static5 | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 42.0 |
| b4_combo_static5 | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 0 | 0/5 | 41.8 |
| b4_combo_static5 | day_holdout_1245 | 2/2 | 3/3 | 0 | 0 | 0 | 0 | 2/3 | 41.3 |
| b5_bright_gamma | night | 3/5 | 0/1 | 1 | 2 | 0 | 0 | 4/0 | 42.7 |
| b5_bright_gamma | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 0 | 0/5 | 42.4 |
| b5_bright_clahe | night | 1/5 | 0/1 | 2 | 3 | 0 | 0 | 2/1 | 44.7 |
| b5_bright_clahe | night_holdout_2200 | 0/0 | 4/5 | 0 | 1 | 0 | 0 | 0/4 | 43.2 |

## Detail
(yolo_env) [rmathew1@login11 test_colonial]$ 