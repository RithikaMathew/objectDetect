[rmathew1@login11 vision]$ cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
squeue -u "$USER"
cat exp_results/RESEARCH_research_oct19.md
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
# Research suite: research_oct19

This report concerns the new suite only. Existing b4 remains the reference; no automatic model promotion.

| Task | Job | Status | Detail |
|---|---|---|---|
| grounding_setup | 46692072 | SUCCEEDED | {'model_path': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/.research_models/models--IDEA-Research--grounding-dino-tiny/snapshots/a2bb814dd30d776dcf7e30523b00659f4f141c71', 'revision': 'a2bb814dd30d776dcf7e30523b00659f4f141c71', 'transformers': '4.49.0', 'torch': '2.13.0+cu130'} |
| higher_resolution_scan | 46692073 | SUCCEEDED | {'inventory': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/logs/research_oct19/busy/inventory.csv', 'windows': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/logs/research_oct19/busy/windows.txt', 'higher_resolution_sources': 2} |
| tta_night2115 | 46692074 | SUCCEEDED | {'run_log': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/logs/research_oct19_tta/Standard_SCU8OG_2019-07-10_0000.022_run_log.json', 'final_counts': {'bicyclists': 5, 'pedestrians': 0, 'vehicles': 221}, 'runtime_s': 5300.9} |
| tta_day1400 | 46692075 | SUCCEEDED | {'run_log': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/logs/research_oct19_tta/Standard_SCU8OG_2019-07-10_0000.015_run_log.json', 'final_counts': {'bicyclists': 1, 'pedestrians': 4, 'vehicles': 445}, 'runtime_s': 5197.7} |
| tta_night2200 | 46692076 | SUCCEEDED | {'run_log': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/logs/research_oct19_tta/Standard_SCU8OG_2019-07-10_0000.023_run_log.json', 'final_counts': {'bicyclists': 0, 'pedestrians': 6, 'vehicles': 345}, 'runtime_s': 5489.0} |
| tta_day1245 | 46692077 | SUCCEEDED | {'run_log': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/logs/research_oct19_tta/Standard_SCU8OG_2019-07-10_0000.013_run_log.json', 'final_counts': {'bicyclists': 2, 'pedestrians': 3, 'vehicles': 437}, 'runtime_s': 5242.3} |
| sensitive_night2115 | 46692078 | SUCCEEDED | {'run_log': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/logs/research_oct19_sensitive/Standard_SCU8OG_2019-07-10_0000.022_run_log.json', 'final_counts': {'bicyclists': 5, 'pedestrians': 5, 'vehicles': 228}, 'runtime_s': 2388.3} |
| sensitive_day1400 | 46692079 | SUCCEEDED | {'run_log': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/logs/research_oct19_sensitive/Standard_SCU8OG_2019-07-10_0000.015_run_log.json', 'final_counts': {'bicyclists': 2, 'pedestrians': 5, 'vehicles': 446}, 'runtime_s': 2391.0} |
| sensitive_night2200 | 46692080 | SUCCEEDED | {'run_log': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/logs/research_oct19_sensitive/Standard_SCU8OG_2019-07-10_0000.023_run_log.json', 'final_counts': {'bicyclists': 0, 'pedestrians': 26, 'vehicles': 350}, 'runtime_s': 2370.1} |
| sensitive_day1245 | 46692081 | SUCCEEDED | {'run_log': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/logs/research_oct19_sensitive/Standard_SCU8OG_2019-07-10_0000.013_run_log.json', 'final_counts': {'bicyclists': 2, 'pedestrians': 4, 'vehicles': 437}, 'runtime_s': 2378.9} |
| grounding_night2115 | 46692082 | SUCCEEDED | {'output': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/logs/research_oct19/grounding/night', 'frames': 42, 'proposals': 113, 'low_overlap_proposals': 91, 'model': {'model_path': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/.research_models/models--IDEA-Research--grounding-dino-tiny/snapshots/a2bb814dd30d776dcf7e30523b00659f4f141c71', 'revision': 'a2bb814dd30d776dcf7e30523b00659f4f141c71', 'transformers': '4.49.0', 'torch': '2.13.0+cu130'}, 'limitation': 'Frame-selected proposal audit only; low overlap is not a confirmed missed person. Bicycle/motorcycle proposals are not cyclist counts.'} |
| grounding_day1400 | 46692083 | SUCCEEDED | {'output': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/logs/research_oct19/grounding/day', 'frames': 41, 'proposals': 85, 'low_overlap_proposals': 69, 'model': {'model_path': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/.research_models/models--IDEA-Research--grounding-dino-tiny/snapshots/a2bb814dd30d776dcf7e30523b00659f4f141c71', 'revision': 'a2bb814dd30d776dcf7e30523b00659f4f141c71', 'transformers': '4.49.0', 'torch': '2.13.0+cu130'}, 'limitation': 'Frame-selected proposal audit only; low overlap is not a confirmed missed person. Bicycle/motorcycle proposals are not cyclist counts.'} |
| grounding_night2200 | 46692084 | SUCCEEDED | {'output': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/logs/research_oct19/grounding/night_holdout_2200', 'frames': 37, 'proposals': 101, 'low_overlap_proposals': 85, 'model': {'model_path': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/.research_models/models--IDEA-Research--grounding-dino-tiny/snapshots/a2bb814dd30d776dcf7e30523b00659f4f141c71', 'revision': 'a2bb814dd30d776dcf7e30523b00659f4f141c71', 'transformers': '4.49.0', 'torch': '2.13.0+cu130'}, 'limitation': 'Frame-selected proposal audit only; low overlap is not a confirmed missed person. Bicycle/motorcycle proposals are not cyclist counts.'} |
| grounding_day1245 | 46692085 | SUCCEEDED | {'output': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/logs/research_oct19/grounding/day_holdout_1245', 'frames': 45, 'proposals': 87, 'low_overlap_proposals': 63, 'model': {'model_path': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/.research_models/models--IDEA-Research--grounding-dino-tiny/snapshots/a2bb814dd30d776dcf7e30523b00659f4f141c71', 'revision': 'a2bb814dd30d776dcf7e30523b00659f4f141c71', 'transformers': '4.49.0', 'torch': '2.13.0+cu130'}, 'limitation': 'Frame-selected proposal audit only; low overlap is not a confirmed missed person. Bicycle/motorcycle proposals are not cyclist counts.'} |
| hires_base | 46692086 | SUCCEEDED | {'run_log': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/logs/research_oct19_hires_base/corrine_706_15min_run_log.json', 'final_counts': {'bicyclists': 0, 'pedestrians': 1, 'vehicles': 574}, 'runtime_s': 815.0} |
| hires_combo | 46692087 | SUCCEEDED | {'run_log': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/logs/research_oct19_hires_combo/corrine_706_15min_run_log.json', 'final_counts': {'bicyclists': 0, 'pedestrians': 1, 'vehicles': 491}, 'runtime_s': 1455.2} |
| hires_tta | 46692088 | SUCCEEDED | {'run_log': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/logs/research_oct19_hires_tta/corrine_706_15min_run_log.json', 'final_counts': {'bicyclists': 0, 'pedestrians': 1, 'vehicles': 491}, 'runtime_s': 3120.6} |
| zerodce_night2115 | 46692089 | SUCCEEDED | {'run_log': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/logs/research_oct19_zerodce/Standard_SCU8OG_2019-07-10_0000.022_run_log.json', 'final_counts': {'bicyclists': 4, 'pedestrians': 1, 'vehicles': 185}, 'runtime_s': 3309.1} |
| zerodce_night2200 | 46692090 | SUCCEEDED | {'run_log': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/logs/research_oct19_zerodce/Standard_SCU8OG_2019-07-10_0000.023_run_log.json', 'final_counts': {'bicyclists': 0, 'pedestrians': 4, 'vehicles': 301}, 'runtime_s': 2875.1} |
| zone_fisheye_previews | 46692091 | SUCCEEDED | {'output': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/logs/research_oct19/previews', 'limitation': 'Preview guesses only. Lens settings and zones still require visual checking.'} |
| sensitive_review_pack | 46692092 | SUCCEEDED | {'table': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/logs/research_oct19/review_candidates.csv', 'pack': '/orange/xiangyan/rithika/vision/vision3/best/test_colonial/logs/research_oct19/review_12min', 'limitation': '12-minute candidate pack over one source hour; human review and deduplication still required.'} |

All tasks have final status records.

## Existing-truth comparison
## Summary (person level; FOUND = counted with the right class; motorcycle scored as cyclist)

| run | clip | cyclists found | pedestrians found | wrong class | detected, not counted | missed | extra counted | counted bic/ped | runtime min |
|---|---|---|---|---|---|---|---|---|---|
| b4_combo_static5 | night | 4/5 | 0/1 | 1 | 1 | 0 | 0 | 5/0 | 42.9 |
| b4_combo_static5 | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 42.0 |
| b4_combo_static5 | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 0 | 0/5 | 41.8 |
| b4_combo_static5 | day_holdout_1245 | 2/2 | 3/3 | 0 | 0 | 0 | 0 | 2/3 | 41.3 |
| research_oct19_tta | night | 4/5 | 0/1 | 1 | 1 | 0 | 0 | 5/0 | 88.3 |
| research_oct19_tta | day | 1/1 | 4/4 | 0 | 0 | 0 | 0 | 1/4 | 86.6 |
| research_oct19_tta | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 1 | 0/6 | 91.5 |
| research_oct19_tta | day_holdout_1245 | 2/2 | 3/3 | 0 | 0 | 0 | 0 | 2/3 | 87.4 |
| research_oct19_sensitive | night | 4/5 | 0/1 | 2 | 0 | 0 | 4 | 5/5 | 39.8 |
| research_oct19_sensitive | day | 1/1 | 4/4 | 0 | 0 | 0 | 2 | 2/5 | 39.9 |
| research_oct19_sensitive | night_holdout_2200 | 0/0 | 5/5 | 0 | 0 | 0 | 21 | 0/26 | 39.5 |
| research_oct19_sensitive | day_holdout_1245 | 2/2 | 3/3 | 0 | 0 | 0 | 1 | 2/4 | 39.6 |
| research_oct19_zerodce | night | 3/5 | 0/1 | 2 | 1 | 0 | 0 | 4/1 | 55.2 |
| research_oct19_zerodce | night_holdout_2200 | 0/0 | 4/5 | 0 | 0 | 1 | 0 | 0/4 | 47.9 |


Full details: /orange/xiangyan/rithika/vision/vision3/best/test_colonial/logs/research_oct19/person_evaluation.md

## What to inspect
- Annotated TTA videos: /orange/xiangyan/rithika/vision/vision3/best/test_colonial/annotated/research_oct19_tta/
- Grounding side-by-side frames: /orange/xiangyan/rithika/vision/vision3/best/test_colonial/logs/research_oct19/grounding/
- Twelve-minute raw-video review pack: /orange/xiangyan/rithika/vision/vision3/best/test_colonial/logs/research_oct19/review_12min/review.html
- Camera metadata / cuts: /orange/xiangyan/rithika/vision/vision3/best/test_colonial/logs/research_oct19/busy/inventory.csv and windows.txt
- Zone / fisheye previews: /orange/xiangyan/rithika/vision/vision3/best/test_colonial/logs/research_oct19/previews/
- Grounding proposals are not counts or confirmed misses. Its frame selection is encounter-targeted, not unbiased recall.
- Higher-resolution runs have no truth yet: qualitative outputs only; no accuracy claim.
- New thresholds are experimental; do not accept them solely because they fit the existing four clips.
- No own-night fine-tuning, 40-track campaign, full-day scaling, temporal detector retraining or BNE model substitution is included.
(yolo_env) [rmathew1@login11 test_colonial]$ python code/research_worker.py logs/research_oct19 report
/orange/xiangyan/rithika/vision/vision3/best/test_colonial/exp_results/RESEARCH_research_oct19.md
(yolo_env) [rmathew1@login11 test_colonial]$ 