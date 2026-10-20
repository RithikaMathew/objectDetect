# Exact video paths and what needs labelling

The four files in truth/ already label the four Colonial clips. Do NOT label them again. The spot-checks below only verify identities or earlier uncertain observations. The separate 40-track sheet is on the back burner. The Corrine review is a qualitative check; its complete human truth is still unavailable.

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

## Two additional sites / years — submitted only when you run the new launcher

`python code/submit_newsites.py --go` uses the best full system on **Anderson St (2021)** and **Curry Ford North (2022)**. Source roots:

```text
/orange/xiangyan/rithika/vision/pilot_clips/MioVision Data/2021 Data/Anderson St
/orange/xiangyan/rithika/vision/pilot_clips/MioVision Data/2022 Data/Curry Ford/North
```

The launcher picks a real readable daytime hourly file per root (preferring noon), records its exact path, and processes its first15minutes. These runs have not been submitted from the Mac, so no actual new output path is claimed yet. When complete, `exp_results/NEWSITES_newsites_oct20.md` lists the exact MP4 paths from the run logs. Expected output directories:

```text
/orange/xiangyan/rithika/vision/vision3/best/test_colonial/annotated/newsites_oct20_anderson_2021/
/orange/xiangyan/rithika/vision/vision3/best/test_colonial/annotated/newsites_oct20_curryford_2022/
```

For each new video, check whether every cyclist/pedestrian is detected, labelled correctly and counted once; note timestamps/IDs for misses, duplicates or ID jumps. This does not require the deferred40-track exercise. No complete truth totals exist yet. Both sites appear in the training-data recipe, so they are additional validation sites, not proof of unseen-site generalization.

## Latest other-site / other-year annotated videos: Corrine 706 (2025)

All three research videos use the SAME 08:05–08:20 clip from March 12, 2025, at the Corrine site. These are three settings, not three different sites. These expected original paths follow the submitted code’s naming; the combination filename is also confirmed by the owner. Remote existence and any `_v2` suffix have not been checked from this Mac. Use the `find` command below to list the files actually present.

**research_oct19_hires_base**

```text
/orange/xiangyan/rithika/vision/vision3/best/test_colonial/annotated/research_oct19_hires_base/corrine_706_15min/research_oct19_hires_base__day_0805-0820__control__20250312.mp4
```

**research_oct19_hires_combo**

```text
/orange/xiangyan/rithika/vision/vision3/best/test_colonial/annotated/research_oct19_hires_combo/corrine_706_15min/research_oct19_hires_combo__day_0805-0820__sahi864+speedrule-lateral+shortrule-night+detfuse+staticfilter__20250312.mp4
```

**research_oct19_hires_tta**

```text
/orange/xiangyan/rithika/vision/vision3/best/test_colonial/annotated/research_oct19_hires_tta/corrine_706_15min/research_oct19_hires_tta__day_0805-0820__sahi864+tta-scale-flip+speedrule-lateral+shortrule-night+detfuse+staticfilter__20250312.mp4
```

List actual cluster filenames:

```bash
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
find annotated/research_oct19_hires_base annotated/research_oct19_hires_combo annotated/research_oct19_hires_tta -type f -name '*.mp4'
```

Check the same two distant cyclists and e-scooter in each version; report video-player timestamps and whether a box, ID and final count appear. The newer combination’s filename was supplied without a review verdict, so it remains unreviewed. The older `nv_combo_corrine2025_706` review found two missed cyclists and an e-scooter labelled pedestrian. A `(1)` in a downloaded Mac filename is not part of the original cluster path.

No annotated second Corrine camera (856) or Curry Ford 2022 run is established by the completed suite. They are source candidates only; do not mistake scan inventory for completed annotation. RF-DETR outputs are sampled JPGs, not annotated videos: `logs/rfdetr_oct19/{night,day,night_holdout_2200,day_holdout_1245}/`.

## Earlier higher-resolution qualitative test

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
