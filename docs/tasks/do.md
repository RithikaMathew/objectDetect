All 14 jobs and the video scan are queued, and nothing went wrong this time. The 2025 clip is 960×540 at 15 fps, which is only modestly higher resolution than the old 720×480.

1. Wait for the jobs. Each takes about 45 minutes once running, and the queue may delay the start. Check the queue:

bash
squeue -u $USER

When it shows nothing, check that every job finished cleanly (this should print nothing, and the ls and sacct lines are only for a final look):

bash
sacct -u $USER -S 2026-10-15 --format=JobID,JobName%22,State,Elapsed | grep -v batch | tail -20
grep -L "Final counts" logs/*461410{42,48,49,50,51,52,53,54,55,56,57,58,59,60}*
ls busy

2. Score both groups and paste the output here. Paste only the Summary tables, not the long motion-candidate lists at the bottom:

bash
python code/eval_truth.py --root . --runs exp0_base,b4_combo_static5,b5_nospeed,b5_noveto --baseline exp0_base | sed -n '/## Summary/,/## Detail/p'
python code/eval_truth.py --root . --runs b4_combo_static5,b5_bright_gamma,b5_bright_clahe,b5_bright_zerodce --baseline exp0_base | sed -n '/## Summary/,/## Detail/p'

That gives the speed and veto numbers for the slide, and the fair brightening result. The brightening runs cover only the two night clips, so only those rows can change.

3. Scan result. When the scan job is done (it was submitted after the others), paste this:

bash
cat busy/inventory.csv
cat busy/windows.txt

It lists each video’s resolution and the 15-minute window with the most people. For 2023 and 2024 there are no videos yet.

4. Fisheye preview. Download fisheye_test/preview.png and fisheye_test/corrine_706_15min_0m30s.png, or upload them here and I’ll look at them. I need to know two things:

Does the original frame have a black circular border, or does the picture fill the whole rectangle? My tool assumes a circle that touches the short side (540 px). If your picture fills the frame, I’ll change the settings.
In the preview, which tile (150°, 180° or 200°) makes straight things like the curb or road lines look straight?

Then I’ll give you the exact commands to convert the clip and rerun it.

Two things to keep in mind for the 2025 and other-year runs

Pixel settings: at 960×540 the static-object limit of 5 px should scale to about 7 px (5 × 960/720), and I’ll set that when I write the run commands.
Frame rate: the 2025 video runs at 15 fps against 29.97 fps in 2019. Most rules are in seconds or in speed per second, so they should carry over, but that is untested.
Colonial_North_676806_07-10-2019.xls
XLS
bicyclist speeds.xlsx
XLSX

no dont remove the GT from the ai label that should be there im saying the ai label doesnt seem to be incrementing but only the text above it (hour so far) does so im not sure what the purpose of the Bin AI is

are u sure there is no premade Night-specific detector (BNE-DETR)?

also are u sure there is no  technique for “an object just appeared in a still scene” 

so this sbatch has 7 videos right? including the older ground truth ones?

I’ll check the overlay description in the README, search for a ready-made BNE-DETR, look at your two Excel files, and try better fisheye settings on your frame.

Continue

I’m now trying better fisheye settings on your actual frame. The first preview assumed a circular image, but yours fills the whole rectangle.

--format=JobID,JobName%22,State,Elapsed | grep -v batch | tail -20 grep -L "Final counts" logs/*461410{42,48,49,50,51,52,53,54,55,56,57,58,59,60}* ls busy 46141053_23 colonial_v19 COMPLETED 00:46:38 46141053_23+ extern COMPLETED 00:46:38 46141054_13 colo

PASTED

continue

Look at undistortion previews for the rectangular frame
both.png
Paused: Your free usage returns at 3:40 PM. Continue then.

---
2026-10-19 continuation: the jobs have finished; the old wait instructions above are historical. See README_colonial_validation_v31.md section 41 for reproduced scores, fixed launchers, exact retry commands, and remaining tasks. Keep b4_combo_static5. Do not repeat completed ablation/gamma/CLAHE jobs. Scan and Zero-DCE failed for verified configuration reasons, now fixed locally; cluster reruns are still pending.
