# Exact video paths and what needs labelling

The four files in truth/ already label the four Colonial clips. Do NOT label them again. The spot-checks below only verify identities or earlier uncertain observations. The separate 40-track sheet is on the back burner. No new higher-resolution truth is requested until a new clip is selected and processed.

These paths are read from saved run_log.json files. The videos are on HiPerGator, not in this Mac checkout; current existence has not been checked remotely.

## Already labelled: day_1245_truth.csv

```text
/orange/xiangyan/rithika/vision/vision3/best/test_colonial/annotated/b4_combo_static5/Standard_SCU8OG_2019-07-10_0000.013/b4_combo_static5__day_1245-1300__sahi640+speedrule-lateral+shortrule-night+detfuse+staticfilter__20190710.mp4
```

## Already labelled: day_1400_truth.csv

```text
/orange/xiangyan/rithika/vision/vision3/best/test_colonial/annotated/b4_combo_static5/Standard_SCU8OG_2019-07-10_0000.015/b4_combo_static5__day_1400-1415__sahi640+speedrule-lateral+shortrule-night+detfuse+staticfilter__20190710.mp4
```

## Already labelled: night_2115_truth.csv

```text
/orange/xiangyan/rithika/vision/vision3/best/test_colonial/annotated/b4_combo_static5/Standard_SCU8OG_2019-07-10_0000.022/b4_combo_static5__night_2115-2130__sahi640+speedrule-lateral+shortrule-night+detfuse+staticfilter__20190710.mp4
```

## Already labelled: night_2200_truth.csv

```text
/orange/xiangyan/rithika/vision/vision3/best/test_colonial/annotated/b4_combo_static5/Standard_SCU8OG_2019-07-10_0000.023/b4_combo_static5__night_2200-2215__sahi640+speedrule-lateral+shortrule-night+detfuse+staticfilter__20190710.mp4
```

Optional spot-checks: night_2115 at 14:21–14:26 and 14:47–14:58; day_1245 at 9:54–10:04 and 11:17–11:38. No need to relabel all 21 people.

## Existing higher-resolution qualitative test

Raw 15-minute clip recorded in the saved Corrine run log (on HiPerGator):

```text
/orange/xiangyan/rithika/vision/vision3/best/test_colonial/newvideo/corrine_706_15min.mp4
```

This is an existing candidate for inspection, not a request to label it now.

The saved Corrine 706 test is 960x540 at 15 fps versus Colonial 720x480 at 29.97 fps. That is 1.5 times as many encoded pixels, a modest increase. Fisheye geometry and scene differences confound a resolution comparison. It has no human truth file yet; watching it is a qualitative check unless you choose to score it.

```text
/orange/xiangyan/rithika/vision/vision3/best/test_colonial/annotated/nv_combo_corrine2025_706/corrine_706_15min/nv_combo_corrine2025_706__day_0805-0820__sahi853+speedrule-lateral+shortrule-night+detfuse+staticfilter__20250312.mp4
```

```text
/orange/xiangyan/rithika/vision/vision3/best/test_colonial/annotated/nv_base_corrine2025_706/corrine_706_15min/nv_base_corrine2025_706__day_0805-0820__control__20250312.mp4
```

## Higher-resolution candidate source files (not yet selected truth clips)

Year is not a selection criterion. Scan compares encoded width x height to 720x480. It cannot tell whether a file was previously upscaled. Prefer a conventional view and verify actual person size/detail; more whole-frame pixels alone need not improve detection.

The exact existing candidate list is:

```text
/orange/xiangyan/rithika/vision/pilot_clips/MioVision Data/2022 Data/Curry Ford/North/Standard_SCU8OG_2022-05-17_0000/Standard_SCU8OG_2022-05-17_0000.008.mp4
/orange/xiangyan/rithika/vision/pilot_clips/MioVision Data/2022 Data/Curry Ford/North/Standard_SCU8OG_2022-05-17_0000/Standard_SCU8OG_2022-05-17_0000.013.mp4
/orange/xiangyan/rithika/vision/pilot_clips/MioVision Data/2025 Data/Corrine Dr/MIOP000706_2025_03_12-0000/MIOP000706_2025_03_12-0000.00008.mp4
/orange/xiangyan/rithika/vision/pilot_clips/MioVision Data/2025 Data/Corrine Dr/MIOP000856_2025_03_12-0000/MIOP000856_2025_03_12-0000.00008.mp4
```

The two 2022 sources were previously reported as 720x480, so they are another-site candidates, not higher-resolution evidence unless the new metadata says otherwise. The 2025 706 file is the currently confirmed modestly higher-resolution option; inspect metadata for 856. No selected new 15-minute window path exists yet. The scan writes the exact selection and cut path to busy/inventory.csv and busy/windows.txt. No invented or placeholder video path is being requested for labels.
