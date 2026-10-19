> **Read README.md for the one-command submission workflow. Research code is implemented locally; cluster results are pending.**

# Task audit — 2026-10-19

Audited against [original todo.md](tasks/todo.md), saved truth/count tables, batch reports and code. “Implemented” does not mean an experiment has been validated. No new GPU runs or human labels were produced locally.

| Original task | Status | Evidence / remaining work |
|---|---|---|
| Hand-label ~40 tracked people; compare model accuracy | **Back burner — user request** | No additional 40-track labelling requested now. Existing 21-person truth remains the current evaluation. |
| Fuse RT-DETR, X-CLIP and speed | **Implemented and tested on four clips** | b4 = 19/21; no-speed = 17/21; no-veto = 18/21. Current rules are documented in Colonial README section 0/41. The paper named in the original note is not evidence that these particular thresholds were externally validated. |
| Add nighttime images and fine-tune | **Back burner — user request** | No new nighttime labelling or training requested now. Existing tools retained for later. |
| Try techniques | **Done for several techniques** | SAHI/fusion/static filtering improved saved results. Gamma and CLAHE worsened night results. Zero-DCE failed due to missing checkpoint; launcher repaired, optional retry pending. No reason to replace best settings with brightening. |
| Analyze both wrong / detector right / X-CLIP right | **Done on existing 21-person sample** | New `FUSION_cases_20261019.md`: both right 11; both wrong 2; detector-only right 5; X-CLIP-only right 3. Classification conditional on matched scored tracks, not detector recall. |
| Test higher-resolution cameras (any year) | **Initial qualitative test done; further validation pending** | Target is encoded resolution above 720x480, not a particular year. Corrine 706 is 960x540 but fisheye; 2022 files were reported as 720x480 and do not establish higher-resolution performance. Native source metadata and object detail must be checked. |
| Try 3 s versus 0.4 s; integrate tracking; choose another site | **First two done, last pending** | README section 25f/batch2 documents duration experiments; pipeline uses ByteTrack + ID stitching. resolution-aware scan must be rerun with repaired model path, then a different-site clip processed and hand-labelled. |
| Very high sensitivity + 12-minute human review | **Tools implemented; objective unproven** | `review_pack.py` can budget snippets and report review yield. A low-threshold `run_batch5.py review` launcher is now prepared (four jobs over one hour of existing labelled footage); its GPU run, independent truth including missed people, and review labels are still needed. Ranking by cyclist share alone is unsuitable for finding ALL people, since it deprioritizes pedestrians. Do not report high recall or 80% workload savings yet. |
| Explain people walking away being missed | **Partial evidence only** | Saved h5 is an away-from-camera walker: detector class right, X-CLIP wrong; fusion fixes it. Low image displacement toward/away is why speed rule is lateral-only. For undetected people, watch raw video and record missed people/times; no track statistics can diagnose a person with no track. |

## Findings from the disagreement audit

The two both-wrong cases are night n5 (short rider, both call pedestrian; rejected by duration) and n6 (walker, both call cyclist). Five detector-only wins include h5 walking away and several sideways walkers; three X-CLIP-only wins show why replacing X-CLIP with the detector alone would lose useful information. This is an observed small-sample pattern, not a general causal conclusion. Time-only matching can confuse simultaneous people, so visually verify the named night cases.

## Local fixes completed

Repaired scan path and Zero-DCE preflight/retry; clarified fixed Bin AI total without removing GT; rectangular fisheye mapping; added error-case audit; repaired review packs (raw footage option, failure handling, no pack overwrite, budget packing); labelled legacy fusion output to distinguish it from current b4; reorganized repo and removed obsolete logs/identical root copies.

## Current priorities

1. Run the resolution-aware scan (no minimum year); inspect busy/inventory.csv and busy/windows.txt. Prefer a higher-resolution conventional camera view.
2. Optional checks on existing annotated clips: night_2115 at 14:21–14:26 and 14:47–14:58; day_1245 at 9:54–10:04 and 11:17–11:38. No relabelling required. Exact paths are in VIDEO_PATHS.md.
3. Select and run one new higher-resolution clip. New truth is needed only if scoring that new clip; it is not the shelved 40-track task.
4. Evaluate the low-threshold / 12-minute review experiment using the already-labelled four clips; person-level recall must account for duplicates and entirely missed people.
5. Run the implemented TTA/Grounding audit using the root README.md suite; no measured gains here yet.

Removed from the plan: full-day scaling. Back burner: the 40-track model comparison and own-nighttime fine-tuning. These are excluded from the updated deck. Historical README sections and retained tools record past work but do not authorize active runs.

Git push/pull is appropriate. Do not use hard reset/clean to resolve a cluster pull conflict: local results or source edits may need preserving.
