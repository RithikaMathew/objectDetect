# Historical project notes

Superseded plans and handoff notes are preserved below verbatim apart from repaired links. Current status is in the root README. Historical claims are not promoted to validated results.

## Contents

- [HANDOFF.md](#note-1)
- [METHODOLOGY.md](#note-2)
- [README_colonial_validation_v31.md](#note-3)
- [README_colonial_validation.md](#note-4)
- [STUDY_NEXT_STEPS.md](#note-5)
- [RESEARCH_METHODS.md](#note-6)
- [SPEED_REFERENCE_README.md](#note-7)

<a id="note-1"></a>
## HANDOFF.md
Original location: `docs/history/HANDOFF.md`.

# Current handoff — 2026-10-20

Start with root README.md and docs/TODO.md. The owner wants to finish this bounded experiment set, not start more detector sweeps. All prior claims below are historical where they conflict with this section.


## Returned speed-readiness job47393224

Owner pasted cluster RESULTS.md:41sessions audited,0explicitGPS candidates,375deduplicated reference rows,0Pine-named rows. Audit completed successfully but did not establish camera location/scale. Report-only capture exp_results/speed_readiness_47393224/RETURNED_RESULTS.md; fullcamera_metadata.json/sidecars notdownloaded/notreviewedlocally. Do not imply alloriginalfileslackGPS; sampledsidecars/availabletags only. Physicalmph/independentspeedvalidation remainblocked. Lane/countpilot cancontinue; no repeatmetadatajobrequired. Nextinspectrawtextcluesifdownloaded, otherwise needindependently identifiablegroundlandmarks/distance. Neverusearbitrarylaneenddistances or nearest-speedrecord matching.

## Owner follow-up: shorter road, count/lane ledger and zone editor — October23

Owner does not know Colonial coordinates; asks to search workbooks, choose shorter road with identifiable coordinates, record all users/counts/lanes and provide zone marking. Audited41SpreadsheetMLcountworkbooks: Site Code allblank; no explicitGPS/intersection fieldsfound in searchedXLS/XLSXtables. ShortestarchivecandidatePineHillsBLE25files; PleasantHillPath31;WestOrangePath37. SpeedworkbookWestOrange/Park (29ftPath rows) supplieslocationclue, NOT verifiedcamera. OfficialtrailmapshowsmultipleParkAvecontexts; do notguesscoordinates. Researchandexactpaths in exp_results/study_inventory_20261023/SITE_SELECTION.md and workbook_location_audit.csv. RecommendonehourPineHillsBLEchunk013, notall25hours; GPSstillunverified, unknownuntilsourceframecanbematched. No sources locally and no newclusterjobsrun.

Added site_zone_setup.py: actualdayframefrominventory, embeddedJPEGofflineper-siteHTML/index, multiplefacilitypolygons, undo/reset/import/autosave, confirmation/exportJSONbackup. Oneexportfilenameperzone_key(site) slug+hash. --site filters setup. Futurebatch --scope pilot --site 'Pine Hills BL E' --pilot-chunk13 choosesnewroad. --zones-dir and --require-zones attachandcheckownsite/date/ownerconfirmation; unknowncamerasneverinheritColonialzones. Extraarea regions supported in postprocessing; masksforothercamerasremainoff so markingareasdoesnotchange detectorcounts.

Added lane_use_report.py: personandvehicleper-trackrecords, count/rejectedstatus, predictedtype, dominantfacility>=70%, laneobservationfractions and provisionalvisitedtypes, trackmidpoint15minbin, identitiesunverified. Same-typepolygonoverlapdedup; mixedfacilityoverlapuncertain. NewvehicleCSVaddscountedfield. Workerautomaticlanereportforstudybatch; finalmergedall_tracks/counts_by_site_user_lane/counts_15min_by_user_lane.Cyclistmodelcategorycanincludemotorcycle/scooter; do notclaimnewmodeaccuracy. SourceIDsresetandboundaryduplicatesnotresolved. study_batch.py lanes supportsCPUreclassificationaftereditsintoNEWoutdirectory usingexistingmanifest; originalinferenceunchanged. metric_trajectory_speed.py --run-log --site supportsnewcamera'scountedpeople/vehicleswithsamecamera/datecalibration; no GPS/scale invented. All15testmodules passed (including15new tests across study/site extensions), generatededitor JavaScript smoke test passed, all Python parsed, Slurm wrapper syntax passed. Nine-page report compiled without TeX warnings and visually inspected. Maininstructions docs/runs/STUDY_NEXT_STEPS.md nowleadwithnewroadeditorworkflow.

## New root todo request — October23,2026

Owner explicitly asks to execute root todo.md (new file, not only docs/TODO.md). New scope: partial-track speed/map calibration, best model on all matched study footage + hours, comprehensive .tex report/limitations, multi-agent ideas. This reopens broader study processing previously excluded; keep night fine-tuning/40-track campaign deferred. Read docs/runs/STUDY_NEXT_STEPS.md.

Implemented code/study_batch.py: local archive inventory1919unique files /41site-date pairs, ColonialNorth48nominalhours, other-than-ColonialNorth1871hours, total1919nominalhours; NOT exact durations. Oldmapping1967inflated by Rinehart96vs48.62multipartfilename clocks blocked pending evidence overrides. DefaultpilotonefullColonialhour chunk013; all/colonial/site scopes; cluster probe required, per-file GPUjobs, boundedconcurrency, duplicateguards and final report via research_worker dispatch. No source videos/sbatch locally; NO new inference submitted. Fullscopemissingclocks prevents partialcoverage masqueradingasall. Nominal2.8x factor=>5373GPUhours/~112days2GPUsexcludingqueues, uncertain. Pilot before scaling. NewsetsGTnoneothercameras, no inheritedColonialzones; knownColonialsessionbasis preserves applicable existing truth headerbins. Final rendering avoids provisional streamed headers.

Added map_calibration.py: >=4fit/>=2independentchecklandmarks, CSVtemplate data/reviews/calibration, provenance and checkRMSE. Added metric_trajectory_speed.py: existing7actualbicycles only, truth-window candidate tracks, partialcontinuoussegments>=1.5s, no coasting/gaps>.5s, noextrapolationoutsidefitpointshull, rolling1sOLSvelocitymedian/MAD. No maplocation/realcorrespondences supplied; asked owner asynchronously for exactColonialcamera/maplink. NO physicalspeeds calculated. CalibrationcheckRMSE not independent speedvalidation; identities stillunapproved.

Added conflict_zone_review.py: completepointoccupancyvisits in userpolygon with interpolation over short observation gaps; candidate timegaps/overlap only, not footprintPET/TTC or confirmednearmisses;3sreviewwindowheuristic. ExistingpeopleCSVdoesnotcontainvehicles. Added optional --export-vehicle-trajectories to v19, wrapper EXPORT_VEHICLE_TRAJECTORIES=1; futurestudyjobs enable it. Saves observedvehicleCSV and runlogpath, no detection/countchanges. NotrealGPUvalidated yet. Historicalmissingcarscannotberecoveredfrompeopletrajectories. Userzoneforconflictsnotprovided; no realconflictresults claimed.

Report reports/methodology/object_detection_study_20261023.tex compiled to output/pdf/object_detection_study_20261023.pdf. Contains methods, allqualifiedpriorresults, lanetable, heuristics, veto ties, alternativeboxaudit, other-sites/fisheye failures, speed/near-miss limits, costs and proposedmultiagentrolearchitecture. Primaryreferences FHWA SSAM, OpenCVhomography, BMVC2014calibration, GoogleMapsmeasurement. Multiagentarchitecture proposed only, not deployed. Root todo.md status annotated without deleting originalrequest; rootREADME/currentdocs updated.14testmodules passed including9newtests; finalchecks documented in task handoff. No old truth,userinputs,existingresults,orPPTX overwritten.

## Vision3 version pruning — 2026-10-20

Owner explicitly requested only necessary/latest files in Vision3. Deleted63superseded implementations/docs/launchers: root overlaysv1–v9, bestv10, Colonialv11–v18including nestedv17, comparison predecessors throughv7, old launchers, old aggregate readersv11/v12and duplicate preceding sweeps. Current Colonialv19and aggregatev13retained. Distinct utilities retained even if namedv1; moved root utilities into training/comparison/weights_tools/tools (26moves including report to reports/comparison). Patched retained launchers' Python paths. sweep_conf_v2 now imports aggregatev13; same parse_gt interface. No source data, truth, zones, weights, counts or results deleted. vision3/README.md explains current paths; docs/VISION3_CLEANUP_20261020.csv records removals/moves with original hashes. Old docs/recorded commands refer to historical paths and versions; tracked older versions remain in Git history. No jobs submitted.

## Repository layout update — 2026-10-20

Root README rewritten as the current entry point; entire prior guide preserved at docs/history/README_before_cleanup_20261020.md. Loose person_box_review.json, confirmed review JSON and colonial_speed_gates.json moved unchanged to data/reviews/colonial_20261020/. Root results.md and RESEARCH_research_oct19.md moved to reports/cluster_returns/20261019/. Duplicate root NEWSITES report removed only after byte equality with exp_results copy. Historical references below saying root inputs use the old paths; current paths are here. Cleanup manifest docs/REPO_CLEANUP_20261020.csv records hashes and moves/deletions. Active experiment/training paths unchanged; owner-edited deck preserved. Completed scheduler text logs removed only where structured run JSON survives; failed/incomplete logs retained as archive/diagnostics/20261019/*.txt. Cache/OS metadata removed.15%veto remains a tie-preserving choice, not uniquely best.

## Full-system veto threshold replay — 2026-10-20

Implemented `vision3/best/test_colonial/code/tune_veto.py`, CPU only. Replays raw X-CLIP → veto/promotion → motion → duration/strict night cyclist exception → static/quality checks using saved track/audit/statistics/log exports. All scored-track baseline labels and counted decisions must reproduce before reporting; parity passed on all four clips. Saved evidence is rounded, so counterfactual boundaries remain approximate. Unscored tracks remain unscored. No reference configuration changed.

Default development: night21:15 and day14:00. Checking: night22:00/day12:45, accessed only after development selection. Already-inspected clips mean exploratory checking, not independent validation. Thresholds off,5,10,15,20,30,40,50. Choose most correct counted truth people, then fewest unmatched counted tracks, then original threshold/nearest threshold. Full-system development:off through40all9/11;50gives8/11. Retains15by tie preference, NOT a unique empirical optimum. Frozen15checks10/10 (2cyclist-group/8ped), legacy time matching. Motorcycle remains scored cyclist for compatibility. Optional --identity-map restricts to approved mappings; zero development reviewed rows rejects selection. Six regression tests pass. Do not infer the veto has no effect everywhere from a development tie or conflate this with veto-only X-CLIP probes or historical separate inference runs.

Outputs: `exp_results/veto_threshold_20261020/{RESULTS.md,development_sweep.csv,checking.csv,per_person.csv,summary.json}`. No GPU/Slurm run needed; already executed locally. To repeat from cluster ROOT, use a NEW output directory:

```bash
python code/tune_veto.py --out exp_results/veto_threshold_repeat
```

All model inference, tracking and stitching remain fixed; no continuous-video rerender or stream-header replay. Independent untouched labelled footage is required for a validated threshold claim.

## Latest owner review — zones and new-site failures

See `vision3/best/test_colonial/exp_results/newsites_owner_review_20261020.md` for exact encounter times. Owner visually approved zone previews. Anderson: detected pedestrian and one cyclist; missed a second cyclist and a motorcycle. Curry Ford: missed a very blurry cyclist. This supersedes the earlier statement that no visual review was supplied. It is not exhaustive full-video truth or verified identity accuracy. Do not launch more model sweeps automatically.

Workbook Colonial lengths confirmed: bike lane35ft (12 records including e-bike), sidewalk30ft (11 records). Endpoints/camera-date applicability and person-to-record links remain unverified; do not invent gates from lane polygons. Received root person_box_review.json unchanged:32frames/20boxes, only1reviewed checkbox true. Asked whether all frames are finished; never silently approve unchecked frames. Matching RF/DINO manifest/predictions are not local; need existing downloaded review pack to score, not another inference run.

## Latest returned batch — completed, do not resubmit

Owner supplied root NEWSITES_newsites_oct20.md. Preserved input and copied to vision3/best/test_colonial/exp_results/NEWSITES_newsites_oct20.md. Four work jobs report SUCCEEDED; final report exists:

- Anderson St2021, April13 noon–12:15 inferred:900s processed,720x480@29.97fps; predicted1cyclist,1pedestrian,137vehicles; runtime38.7min.
- CurryFordNorth2022, May17 noon–12:15 inferred:900s processed,720x480@29.97fps; predicted0cyclists,0pedestrians,448vehicles; runtime38.5min.
- final_review SUCCEEDED; outputs at cluster ROOT/exp_results/final_review_20261020, now ready to download whole folder.
- truth_headers SUCCEEDED; copies under ROOT/annotated_gt, originals preserved.

Execution success is not accuracy. Owner has now supplied timestamped visual review: missed cyclists at both sites and a missed Anderson motorcycle; see latest review above. No exhaustive whole-video truth is available. Both sites appear in training recipe and neither video has more resolution than Colonial. Clocks are filename-inferred, not verified. Actual MP4 paths are recorded in returned report; use them rather than guessed paths. No repeat combined batch, new-site runs, RF full-frame audit or header job is needed.

Next: finish existing raw-frame RF/DINO review and full-track identity checks; measured speed gate endpoints and record-to-person links are still human steps. Zone preview alignment is owner-approved; no validation is completed merely by the CPU job succeeding. Older pending-submission statements below are superseded by this update.

## Detector / X-CLIP comparison completed locally

Owner requested which is more accurate on four existing truth clips. New `code/compare_classifiers.py` produced exp_results/classifier_comparison_20261020/{RESULTS.md,per_person.csv,summary.json}, no Slurm/inference. Same21matched/scored tracks, including rejectedn5; detector = cyclist if detector-cyclist share>=50%, otherwise pedestrian; X-CLIP = RAWweighted argmax from rules_audit.csv, NOT tracks.csv xclip_label (that field can already reflect rules).

Detector16/21(76.2%), X-CLIP14/21(66.7%). Byclip night21:15=3/6vs3/6;day14:00=5/5vs3/5;night22:00=4/5vs5/5;day12:45=4/5vs3/5. Cyclistgroup5/8vs6/8(includes1motorcycle);pedestrians11/13vs8/13. Bothright11,bothwrong2,detectoronly5,XCLIPonly3. No general superiority or detection-recall claim; provisional time matches still require identity review. Optional --identity-map limits analysis to approved identities and gives no percentages when none reviewed. Two local regression tests pass, including raw-label versus post-rule distinction and keeping rejected tracks. No new model sweep or change to fusion thresholds.

## Current batch entry point

Owner confirmed none of the recent pending changes have been run on HiPerGator. Use `python code/submit_final_batch.py --go` once after push/pull, not merely `sbatch code/final_review.slurm`. Combined plan has5jobs: two reference new-site pipelines, CPU review/gate/zone build, CPU GT-header copies, dependent report. Manifest logs/newsites_oct20; report exp_results/NEWSITES_newsites_oct20.md. No repeat old research suite or full-frame RF audit. CPU header walltime4h, review30min. Required audit assets, source videos, existing annotations and duplicate outputs checked before submission. Partial submission guard retains jobIDs.

Normal3s day/night; strict NIGHT cyclist exception >=0.3s, detector cyclist share>=90%, weightedXCLIP>=0.90, finalclasscyclist. NOT blanket0.4snight. New-site env explicitly pins3s and strict exception values. Reference weights/rules unchanged. Human validation and physical speed calibration remain manual after batch. No jobs submitted locally.

## Presentation and preferences

- Always create a NEW dated PowerPoint copy; never overwrite the owner's deck.
- Owner added fusion, speed and per-clip results slides. Preserve them: saved original has eight slides.
- New deliverable: reports/presentations/bike_weekly_meeting_10_20_reviewed.pptx, eight slides, reordered definitions → method → fusion → speed → development results → research results → other camera → task audit.
- Original October19 deck was read, not written by this turn. Owner saved a sensitivity-row edit during work; incorporated its “0.4 s day/night” clarification in the new copy. Do not claim the original checksum stayed fixed while the owner was editing.
- Forty-track comparison and own-night fine-tuning remain deferred. Full-day scaling remains removed.

## Current detector evidence

Reference b4_combo_static5: 19/21 under LEGACY TIME MATCHING, no extra counted tracks. Not identity-verified accuracy. TTA: same19/21 plus1extra, with owner-confirmed barricade-to-person ID jumps. Sensitive: same19/21 plus28extras. Zero-DCE:7/11 on night vs reference9/11. No promotion of those methods.

Sensitive settings were confidence/tracker thresholds0.15, minimum duration0.4s for BOTH day and night, static filterOFF. This differs from the reference: usual3s with a strict NIGHT-only0.3–3s cyclist exception. Reference and new-site runs do not enable broad sensitivity. Do not rewrite historical experiment settings or silently remove the reference's short-night exception.

Truth correction: n3/n4/n5 are cyclists at14:21–14:26; n5 legacy track21 is rejected. n6 is pedestrian at14:47–14:58, legacy track23 wrong class. Earlier notes reversed these time descriptions. Actual truth CSVs were never changed. Motorcycle n1 is grouped with cyclists only in the older count score; preserve its raw class for lane/speed analysis.

Fusion weighted score is sum(box_height * class_probability) / sum(box_heights), then fixed veto/speed rules. The motion feature is smoothed 2-D path length / elapsed seconds / mean box height; the speed RELABELLING rule is lateral-only, but the measured path itself is not just x-displacement. It is not mph.

## Completed lane and image-motion analysis

Code: code/labelled_lane_speed.py. Outputs: exp_results/labelled_validation_20261020/ under cluster ROOT / local vision3/best/test_colonial.

- Exactly21 truth rows;20 usable image-motion estimates, one insufficient candidate.
- Provisional candidate lanes:12sidewalk,3bike-lane (includes motorcycle),1road,5uncertain. NONE are yet identity/lane validated.
- Uses observed, non-coasted foot points within each truth window; v2 polygons scaled from inferred1440x960 to720x480. Multiple polygon hits are uncertain. No forced road-to-bike/sidewalk assignment.
- people_lane_speed.csv, study_lane_comparison.csv, identity_review.csv, Colonial_study_speed_records.csv, study_record_links.csv, summary.json, RESULTS.md and identity_pending.md.
- Study count workbook gives aggregate lane counts, not person-level lane truth. At21:15 its3bicycles disagree with hand truth4bicycles+motorcycle. Do not force model/human totals to agree.

## Speed reference: important correction and remaining inputs

Full workbook scan DOES find23uniqueColonial speed records:12bike-lane including one e-bike,11sidewalk. Raw and analysis-sheet copies are deduplicated by record/facility/distance/time. Initial preview-based statement “no Colonial records” was incorrect and corrected during the turn.

Colonial lengths:35ft bike lane,30ft sidewalk. Source mph uses approximate0.681 conversion; exact3600/5280 recomputation is saved separately. Arithmetic checking is NOT model-speed validation. Rows lack matching video timestamps, image gate endpoints and clear camera/date identification. Owner believes record numbers correspond; that is not an explicit mapping to n1/d1/h1/p1 truth IDs. Use study_record_links.csv with reviewer/evidence, never ordinal matching.

Owner provided zones/colonial_north_v2.json. It defines lane AREA polygons, not measured start/end cross-lines. No physical endpoint or human height is guessed. speed_gate_setup.html lets the user mark actual measured cross-lines on a raw frame and confirm source/camera/date/reviewer; code/speed_gates.py computes feet / crossing seconds only for complete unique finite-gate crossings. The empty zones/colonial_speed_gates.template.json deliberately cannot be used as a calibration.

Analyzer accepts --speed-gates, --identity-map and --record-links. Only identity-approved people with metric estimates and evidenced one-to-one study links contribute paired MAE/RMSE. No usable pairs gives null metrics, not zero error. Homography support also requires independently measured same-camera metric coordinates. MPH and matched speed validation remain UNFINISHED because endpoints and verified links have not been supplied.

## Prevent false identity credit

code/eval_truth.py --require-identity [--identity-map CSV] preserves old time-only results but gives unapproved matches UNVERIFIED, excluded from correct/reviewed denominator. Approvals require reviewer, evidence, full_track_reviewed=yes and one-to-one IDs. Check the ENTIRE track, including before/after the truth window. This prevents false verified credit; it does NOT repair ByteTrack or stitching ID switches. No extra40-track campaign or repeat time/class labels requested. Current pending report has0reviewed, not0%accuracy.

## RF-DETR / Grounding validation and one final CPU job

RF-DETR completed165frames/48proposals/9low-overlap; Grounding165/386/308. These totals cannot rank accuracy. New code/rf_person_review.py builds raw selected frames with predictions hidden, encounter midpoints plus four fixed background frames per clip, deduplicating simultaneous encounters (up to37frames). Box every visible human including riders, explicitly mark reviewed even for empty frames, export JSON. Unreviewed frames excluded. Person-only precision/recall at maximum one-to-oneIoU≥0.5, NOT cyclist-mode accuracy, AP, unique-person recall or an independent holdout.

Cluster command: sbatch code/final_review.slurm. No new inference/download. Builds exp_results/final_review_20261020/ with rf_boxes/review.html, raw frames, zone_previews and speed_gate_setup.html. Download WHOLE folder to Mac. Missing completed audit assets fail explicitly. This CPU job has not been run from this Mac; source videos/images are cluster-only. Raw-frame HTML and gate-page JavaScript smoke checks passed locally.

Existing new-site command remains code/submit_newsites.py --go, two GPU jobs plus report for Anderson2021/CurryFordNorth2022. No returned results supplied. Both sites appear in training recipe, not strict unseen-site generalization. Do not resubmit if already queued/running.

## Verification and task status

Nine new validation tests pass: no time-only identity credit; approvals require evidence; zone overlap; no silent mph conversion; synthetic measured gate speed;23deduplicatedreferences; verified speed-pair gating; one-to-one detector boxes; no empty-frame assumption for unreviewed images. Existing17recovery tests pass; header tests also pass. Source workbooks read with standard-library XML/ZIP, never edited. No Excel workbook authored.

Current task audit correctly leaves identity review, lane alignment, optional RF box validation, returned new-site results and physical speed correspondence open. Broad sensitivity's12-minute review-budget benefit is unmeasured and retired as a claim; walking-away explanation remains partial. Further model sweeps are closed. README.md has current commands; historical notes below do not authorize new experiments.

---
# Historical session notes (superseded where inconsistent)

## Latest clarification and two-site implementation

The five-slide results deck now spells out the full system and replaces ambiguous “all4”, “nightonly”, “extra counts”, “Min/clip” and “sensitive” labels. Extra counts = tracks unmatched to human-labelled encounters (may be duplicates/false objects or missing truth); processing minutes = runtime per15-minutevideo. Night-only rows repeat the same configuration on the11nighttruth people to compare brightening fairly. Time-only matching can credit a track that starts on a barricade and later follows a person, so19/21is not identity-verified accuracy. RF-DETR48boxes vs GroundingDINO386on165frames = no demonstrated counting improvement; accuracy cannot be inferred from proposal volume. Exact Corrine paths and review questions are in the final-slide speaker notes and docs/VIDEO_PATHS.md.

New launcher `code/submit_newsites.py --go` (from cluster ROOT) submits reference-system runs on AndersonSt2021 and CurryFordNorth2022 plus final report. Dry-run by default. It discovers real source files under their known dataset folders, prefers a readable noon/daytime hourly file, processes only the first900seconds, and records source/metadata/clock provenance. It refuses missing inputs before submitting and reuses the existing duplicate-guarded manifest + afterany scheduler orchestration. These sites appear in the documented TRAIN recipe, so do not claim strict unseen-site generalization. No complete new truth and no accuracy score. No resolution requirement; pixel-based parameters scale with width. No inherited Colonial zones. Source clocks are inferred from filename/hour index and explicitly marked unverified. User must confirm embedded clock when reviewing.

Command: `python code/submit_newsites.py --go`; default tag `newsites_oct20`. TwoGPUjobs, finalCPUreport `exp_results/NEWSITES_newsites_oct20.md`, actual video paths read from successful run JSONs. Do not invent exact output filenames before the cluster source selection has run. Rebuild report without resubmitting via `python code/research_worker.py logs/newsites_oct20 report`. Status/logs/manifest in logs/newsites_oct20. No jobs actually submitted from this Mac session.

Shared worker now supports `scale_pixels` even for720x480sources (old higher_resolution path still enforces its requirement). Slurm wrapper accepts CLOCK_NOTE and writes it into the run log. Tests cover source-clock parsing, fixed source selection/fallback, reference configuration, report actual paths/non-accuracy disclaimer and safe dry-run; existing17recovery tests pass. GPU execution still pending.

## Latest owner review and follow-up — 2026-10-19

This update supersedes the “RF-DETR not yet run” statements in the initial session record below.

**TTA night 22:00–22:15:** owner reports barricade labelled pedestrian around clip 04:30, IDs 10/12/20/28. ID12 later follows a real pedestrian at clock22:06:00–22:06:14 (clip06:00–06:14); ID20 follows a real pedestrian22:10:00–22:10:15 (clip10:00–10:15). Three pedestrians at22:10:58–22:11:17 have IDs28/35/31. This establishes visual ID contamination/association errors. Do not treat 19/21 from time-only evaluation as identity-verified accuracy. Do not silently change the existing truth CSVs to match predicted IDs or overwrite saved scores. The cause could be ByteTrack association or later stitching; saved trajectories require diagnosis before changing either.

**Older Corrine combination (`nv_combo_corrine2025_706`, SAHI853):** owner reports an e-scooter labelled pedestrian, two distant cyclists missed, and a distant parked car without a drawn box. Scooter mode is not an explicit current category; “person found” does not mean transport mode correct. Annotated vehicle boxes appear only for confirmed/countable vehicles, including a 40px movement requirement; no rendered parked-car box alone does not prove no raw detection. New `research_oct19_hires_combo` (SAHI864) filename was supplied WITHOUT a verdict; do not copy the old verdict onto it. Complete Corrine truth totals remain unknown.

**RF-DETR full-frame audit completed**, owner-supplied report:

| Clip | Frames | Proposals | Low overlap |
|---|---:|---:|---:|
| night | 42 | 12 | 3 |
| day | 41 | 15 | 3 |
| night_holdout_2200 | 37 | 3 | 0 |
| day_holdout_1245 | 45 | 18 | 3 |
| Total | 165 | 48 | 9 |

Pretrained Medium, threshold 0.30. Proposal quantity cannot establish accuracy or rank it against Grounding DINO. In particular37 frames / 3 boxes in the 22:00 clip is sparse output, not three unique recovered pedestrians. Visual matching remains needed. These were frames from Colonial 2019, not a new-site video run.

**Additional code, not yet run on cluster:** `python code/rfdetr_audit.py --tiled --go` submits one GPU job with full-frame + 320px tiles,25%overlap,class-awareNMS IoU.50,threshold 0.30, same 165 frames. Writes `logs/rfdetr_tiled_oct19/RESULTS.md`. Existing full-frame output stays unchanged. Intended to test small/distant boxes; not integrated cyclist counting or a promised improvement. Local tests cover edge coverage, coordinate mapping, class-aware duplicate removal and empty output.

**GT header fix:** current v19 renderer uses the existing four hand-labelled truth CSVs for the exact Colonial source/date, in preference to older aggregate spreadsheet counts. Dedicated fourth yellow header line avoids long-line clipping; unknown bins/cameras explicitly show `GT: not labelled`. Frame dimensions/writer height are updated consistently; no counting logic changed. `stamp_truth_headers.py` creates copies of existing annotated videos under `annotated_gt/<run>/...` with a new yellow truth strip; no model inference, no overwrite of originals. Old MP4s are not automatically changed by pulling code. It defaults to a plan; `--go` encodes. Do not invent Corrine counts from a partial two-cyclist observation.

Exact other-site video paths and an actual-filename listing command: `docs/VIDEO_PATHS.md`. Only Corrine 706 was processed in the higher-resolution suite; the three versions are the same site/year/clip. Source scans of other cameras/years are not completed annotated experiments.

**Presentation:** `reports/presentations/bike_weekly_meeting_10_19_results.pptx` is now five slides: definitions → system/methodology → Colonial results → other-camera/RF-DETR evidence → targeted next checks. V3 is explicitly a fine-tuned RT-DETR detector, not an unexplained “best model.” Deferred work stays out.

More research options remain (appearance-aware association, temporal detector features, camera-domain training), but prioritize the observed ID jumps and small distant cyclists. Do not imply every method has been exhausted or silently reactivate deferred training/full-day scaling.

## Earlier October batch evidence and interpretation

Sources: root `results.md` (cluster terminal output) and `RESEARCH_research_oct19.md` (report from the same run, NOT an independent replication). All 21 non-report tasks succeeded and the final report exists.

| Configuration | Correct truth people | Extra counted tracks | Mean recorded runtime / clip | Decision |
|---|---:|---:|---:|---|
| b4_combo_static5 | 19/21 | 0 | 42.0 min | Keep as current reference |
| TTA scale + flip | 19/21 | 1 | 88.5 min | No gain; review extra track |
| Sensitive settings | 19/21 | 28 | 39.7 min | Candidate review only |
| Zero-DCE, two night clips | 7/11 | 0 | 51.5 min | Leave off; night reference is 9/11 |

19/21 is a small four-clip validation set, not proof of reliability across cameras or full days. Evaluation matches by time, with ambiguity when people overlap. Both remaining reference errors are in the 21:15 night clip: a pedestrian classified as cyclist (14:21–14:26) and a 2.37-second rider rejected (14:47–14:58). No truth encounter was wholly missed under this matcher. Sensitive mode changed several settings simultaneously; it is not an isolated minimum-duration experiment. Recorded runtime comparisons are not controlled hardware benchmarks.

Grounding DINO: 165 sampled frames, 386 proposals, 308 with low overlap with saved b4 boxes. These are repeated frame boxes, NOT 308 missed people or person recall. Baseline overlays include rejected/coasted tracks. Inspect before drawing conclusions.

Higher resolution: two sources found; Corrine 706 is 960x540, 15 fps, with fisheye distortion. Three matched Corrine runs each counted 0 cyclists/1 pedestrian, but no truth exists, so accuracy remains unknown. Any year is acceptable if resolution exceeds the Colonial 720x480 footage. Zone and fisheye previews are guesses pending visual review.

Latest presentation: `reports/presentations/bike_weekly_meeting_10_19_results.pptx` (now condensed to five slides; see latest update above). Earlier presentations remain historical.

## What the owner should review

Cluster ROOT = `/orange/xiangyan/rithika/vision/vision3/best/test_colonial`.

1. `ROOT/annotated/research_oct19_tta/`: the 22:00–22:15 video (source chunk .023). Determine whether its single extra pedestrian is a duplicate, false alarm, or a real person omitted from truth. Locate the actual output with `find annotated/research_oct19_tta -type f -name '*2200-2215*.mp4'` from ROOT; no local cluster file existence has been verified.
2. Reference 21:15 video: check 14:21–14:26 (walker) and 14:47–14:58 (short rider). Exact reference video locations are documented in `docs/VIDEO_PATHS.md`. Do not relabel existing truth.
3. `ROOT/logs/research_oct19/grounding/night/`: JPGs near clip seconds 861–866 and 887–898. Left = saved b4 tracks, right = Grounding DINO. Are proposals real, and do they explain the two errors? Other four-clip audit folders: `day`, `night_holdout_2200`, `day_holdout_1245`.
4. Optional existing sensitive-candidate review pack: download the whole `ROOT/logs/research_oct19/review_12min/` directory and open `review.html`. Label b/p/n using its controls and return the exported CSV. Twelve minutes is the raw snippet budget, not a promise of human review time. This is NOT the deferred 40-track study.

## New code added this session — not yet run on GPU

`vision3/best/test_colonial/code/rfdetr_audit.py`: pretrained RF-DETR Medium (rfdetr==1.11.2), threshold .30, full-frame proposal audit on exactly the Grounding DINO sampling scheme. One GPU job creates an isolated environment, preserves the working Torch/torchvision versions through pip constraints, downloads the model, audits all four clips, and writes `logs/rfdetr_oct19/RESULTS.md`. Per-clip side-by-side JPGs/CSVs, model metadata/checkpoint hashes, package freeze, status and Slurm log remain alongside it. Baseline model, outputs and yolo_env are not changed. Package conflicts fail explicitly rather than replacing working Torch. Default is dry-run; output directory prevents duplicate submission. On failure inspect status/log before choosing a new tag.

This is a modern alternative detector benchmark, NOT a replacement counting pipeline or a claim of improved cyclist accuracy. COCO person/bicycle/motorcycle are separate categories. Low overlap is not a verified miss. No new truth boxes are requested before running; visual adjudication is needed afterward. Existing Grounding DINO audit gained an optional inference callback; its default behavior stays unchanged.

Primary method/API source: https://github.com/roboflow/rf-detr ; published package metadata: https://pypi.org/project/rfdetr/1.11.2/ . The published wheel was checked for RFDETRMedium, COCO_CLASSES and RF_HOME support. CPU tests check category filtering, dry-run behavior and tag safety; existing research tests pass. CUDA inference/package setup still require the cluster run.

After committing/pushing on the Mac, on HiPerGator:

```bash
cd /orange/xiangyan/rithika/vision
git pull --ff-only origin main
cd vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
python code/rfdetr_audit.py --go
```

Read `logs/rfdetr_oct19/RESULTS.md` after completion; failures are in `logs/rfdetr_oct19/status.json` and `job_<id>.log`. The original 22-task suite does NOT need resubmitting.

## Constraints for the next assistant

- Existing four truth CSVs under ROOT/truth total 21 people; no repeat labeling requested.
- Full-day 24/48-hour scaling removed from the active plan.
- Own-night fine-tuning and ~40-track hand-label comparison are on the back burner.
- Do not promote TTA, sensitive thresholds, Zero-DCE, Grounding DINO or RF-DETR without evidence.
- Higher resolution may be from any year; 720x480 cameras do not qualify merely because newer.
- Current pipeline: fine-tuned RT-DETR v3 + SAHI + ByteTrack/stitching + X-CLIP + rules/fusion/static filter. Current code is under vision3/best/test_colonial/code.
- Slurm partition hpg-turin, account/qos **xiangyan**. Working environment: /orange/xiangyan/rithika/vision/yolo_env. Submit GPU work with sbatch.
- Keep root README.md the single user entry point. Do not delete truth, structured results, weights or videos during cleanup.
- Git transfers code/docs, not ignored cluster videos/model weights. Preserve cluster changes if pull conflicts; never force-reset/clean results.

---

# Historical September handoff (superseded)

The text below records an earlier pipeline/dataset audit. Its 48-hour counts, next steps, file paths and account settings are historical, not the current Colonial validation status.

# Project Handoff — Cyclist Detection from Archival Traffic Video

**For:** an AI coding assistant (or new collaborator) picking this up cold.
**Written:** 2026-09-19. **Owner:** Rithika Mathew, UF (rmathew1).

Read this first, then `METHODOLOGY.md` (research design),
`PROGRESS.md` (checklist), `HIPERGATOR_COMMANDS.md` (runbook).

---

## 1. What this project is

A UF transportation-engineering study measuring cyclist behaviour from 2019
MioVision traffic-camera footage, validated against hand-collected counts.
Five goals in `goals.md`; **only Goal 1 (counting) is under way.**

Compute: HiPerGator, `/orange/xiangyan/rithika/vision`, Slurm partition
`hpg-turin`, account/qos `xilei.zhao`, venv `yolo_env` (plain
`source yolo_env/bin/activate`, not conda). Always `sbatch` — never run YOLO on
the login node.

### The dataset's two unusual properties (these drive the research design)

1. **Matched-pair natural experiment.** Every recording date deployed *two*
   cameras simultaneously — one bike-lane (BL) site and one no-bike-lane (NBL)
   control. 17 such pairs. Weather, season, day-of-week and time-of-year are
   controlled by construction. Discovered by date-joining video folders to
   ground truth (`build_site_mapping.py`); it was not documented anywhere.
2. **Facility-disaggregated human ground truth.** 41 site-sessions, 5,053
   cyclists, split by facility/direction/movement. **63% of cyclists ride on
   sidewalks**, only 22% in bike lanes. This is rare — most papers in this area
   validate against a few hundred self-drawn boxes.

---

## 2. Current status — one sentence

The detection/tracking pipeline runs end-to-end over a full 48-hour
site-session and reports **88 cyclists against a ground truth of 89 (−1.1%)**,
but an audit shows that total is **two large errors cancelling**, and the next
move is detector fine-tuning.

### The headline number is not what it looks like

Human review of the 30 most-suspicious tracks (§3b) found **50% of them
spurious** — 8 duplicates, 6 false positives, 1 pedestrian. Those 30 were
selected as the worst, so 50% is not the session-wide rate; extrapolating the
lower-suspicion remainder conservatively puts the true count somewhere around
**55-65 real cyclists against a ground truth of 89**.

That implies the pipeline is simultaneously **adding ~25-30 spurious counts and
missing ~25-30 real ones**. The reviewer confirmed misses directly: three notes
record a cyclist plainly visible with no detection box.

**Never report the −1.1% without this caveat.** A correct total is not evidence
of a correct pipeline — here it is two large errors cancelling.

---

## 3. What was fixed (do not re-litigate these)

The pipeline began at **zero cyclists tracked** on a clip where the detector
reported a cyclist at confidence 0.92. Six distinct bugs, each diagnosed from
logged evidence, all fixed and covered by a 10-test regression suite:

| Bug | Evidence | Fix |
|---|---|---|
| IoU association gate (0.3) | passed 3/12 links on the known cyclist; box height flaps 114→62→50 px so IoU collapses at 6.7 px of motion | velocity-predicted, size-normalized centroid association (`vru_tracker.py`) |
| Duplicate detections | one rider → 5 "cyclists" + 2 "motorcycles" + 3 "persons" | containment suppression + cyclist fusion + redundant-track merge |
| Merge used the wrong scale | normalized by the track's *final* box; a receding cyclist goes 160→29 px, inflating early distances ~5×, while tracks ending large merged **a car with a pedestrian** | normalize per-timestamp |
| Merge needed shared timestamps | assignment is one-to-one, so two tracks on one object interleave and share **0** timestamps | path interpolation + succession test |
| Class vote relabelled cyclists as pedestrians | a cyclist always generates person detections and the rider is easier to detect, so summed votes flip as the bike becomes unresolvable | bicycle evidence (max conf ≥ 0.40) is decisive |
| Track termination counted samples not time | `max_missed=4` = 0.13 s at stride 1; and `predict()` only extrapolated one sample ahead, so coasting could never reacquire | `--coast-seconds`; extrapolate from `last_t` |

Plus: H.264 via ffmpeg CLI (OpenCV picked `h264_v4l2m2m`, a hardware encoder
absent on compute nodes), confirmed-tracks-only two-pass rendering, trail
smoothing, tile batching.

**Tracker work is done.** The remaining errors are upstream, in the detector.

---

## 3b. CLIP REVIEW RESULTS — 30 most-suspicious tracks, human-verified

`review_sheet.csv`, scored by the owner. **This is the most important evidence
in the project** and it corrected two of my own recommendations.

| Verdict | n | % |
|---|---|---|
| REAL | 15 | 50% |
| DUP (same rider counted twice) | 8 | 27% |
| FP (nothing cyclist-like) | 6 | 20% |
| PED (pedestrian read as cyclist) | 1 | 3% |

**50% of the most-suspicious set is spurious.** Note this is the *top 30 of 88*
by suspicion score, deliberately not a random sample — do not read 50% as the
session-wide error rate.

### Mechanisms the owner identified, counted from the notes

| n | Mechanism |
|---|---|
| 9 | **false detections on grass / vegetation** |
| 4 | box jumps onto grass mid-track (contaminates otherwise-REAL tracks) |
| 3 | one cyclist split into two track IDs (typically far→near, as apparent size changes fast) |
| 3 | cyclist missed while far from camera |
| 2 | cyclist first classified as a **car**, corrected only when closer |
| 1 | **two real cyclists merged into ONE track ID** (over-merge → under-count) |
| 1 | traffic cone detected as cyclist |
| 1 | pedestrian detected as cyclist |

**Grass is the dominant false-positive source** — 5 of 6 FPs are grass or cone,
and all 6 have `mean_conf` between 0.18 and 0.28. It is a texture/appearance
problem in specific frame regions, not a tracking problem.

### ⚠️ Two earlier recommendations are now WITHDRAWN

These were my hypotheses; the review data contradicts both. Do not implement
them:

1. **Do NOT raise `MIN_NET_DISPLACEMENT` (0.75).** I predicted low-excursion
   "STATIC" tracks would be false positives. They are not: tracks flagged
   STATIC were 47% spurious versus 54% for un-flagged ones — no predictive
   power. REAL cyclists have a *median* excursion of 2.85 and a minimum of
   0.97, identical to the FP minimum. A cyclist riding toward or away from the
   camera, or clipping a frame edge, legitimately covers very little
   image-plane distance. Raising this threshold would delete real cyclists.
2. **Do NOT add a night-specific confidence penalty.** I predicted night false
   positives from the rate anomaly (night 2.12/h > day 1.69/h). The review says
   the opposite: night-flagged tracks were 36% spurious versus 62% for daytime
   ones. The rate anomaly is more likely explained by *daytime misses* (more
   traffic, more occlusion) than by night FPs.

**What survives:** the `DUPLICATE` flag is a *necessary* condition — all 8 DUPs
were flagged, 0 unflagged tracks were DUP — but only 47% precise. Keep it as a
triage signal, not a filter.

---

## 4. Known issue the owner observed directly

> *"the object detection is very glitchy and only detects bicyclists and not
> cars very well"*

Partly a rendering artifact, partly a real configuration problem:

1. **Clips draw confirmed tracks only** (`--draw-all` defaults off), so
   anything rejected is invisible. Cars that don't clear confirmation simply
   don't appear.
2. **Vehicles are held to a STRICTER standard than cyclists.** In
   `pilot_detect_v2.py`: `_default` (car/truck/bus) needs 1.0 s persistence,
   max_conf 0.55, mean_conf 0.22; `cyclist` needs 0.5 s, 0.50, 0.18. Those
   thresholds were tuned for the cyclist problem. **Goal 1 is explicitly
   "Cyclist + Vehicle Counting", so this is a real defect, not just optics.**
3. **Clips render at `--stride 5`** (6 fps) to match the counting run, which
   looks choppy. Deliberate: rendering at full frame rate would show a
   *different* pipeline's output than the one that produced the counts.

To see what the detector actually does, unfiltered:

```bash
python pilot_detect_v2.py "$CLIP" --render-window 400 420 --stride 1 --draw-all
```

**Action for whoever picks this up:** tune vehicle thresholds separately
against vehicle ground truth before claiming anything about vehicle counts.
There is no vehicle ground truth in the Excel files — the hand counts are
cyclists and pedestrians only. So vehicle counting needs its own validation
plan, or should be dropped from Goal 1's scope. Raise this with the owner.

---

## 5. NEXT STEP: fine-tune the detector

**Recommendation: yes, now.** The argument is evidential, not preference —
each of the three audited failure modes traces to the detector's *concept*
mismatch, not to the tracker:

Every mechanism in the verified review (§3b) is an *appearance* failure, not an
association failure:

| Verified mechanism | n | Why fine-tuning is the fix |
|---|---|---|
| Grass / vegetation detected as cyclist | 9 | pure appearance error. COCO never saw 2019-compression grass at this scale. Mine these exact frames as **hard negatives** — they are already located, with timestamps |
| Box jumps onto grass mid-track | 4 | same root cause: grass produces competing detections the tracker then associates to |
| ID split far→near | 3 | the detector's box is unstable as scale changes, so association has nothing stable to track. A single trained `cyclist` class emits one consistent box |
| Missed while far from camera | 3 | domain gap on 30-px riders — exactly what sliced fine-tuning targets |
| Cyclist classified as car at distance | 2 | class confusion, fixed by training on this domain. **Also worth knowing:** the semantic-group constraint in `merge_redundant_tracks` blocks car↔cyclist merges by design, so this splits one rider into two un-mergeable tracks |
| Pedestrian read as cyclist | 1 | `fuse_cyclist_dets` cannot tell standing-beside from riding; a trained model can |
| Two cyclists merged into one ID | 1 | over-merge → under-count. Rarer than under-merging (8 DUPs), so do not tighten merge globally |

Tracker tuning is exhausted; six bugs in, and every remaining mechanism the
human reviewer identified is upstream in the detector.

### 5.1 Mining strategy — use the pipeline's own uncertainty

The originally-planned mining pass needed 15-minute interval ground truth,
which **does not exist** (see §7). There is now a better source that sidesteps
that blocker entirely:

The full-session run produced **88 counted + 821 rejected** cyclist-class
tracks, each with a chunk and timestamp. Those 909 tracks are a *curated pool
of hard cases* — every one is somewhere the detector saw something
cyclist-like and the pipeline had to make a close call. That is exactly the
distribution worth annotating, and far better than uniform sampling where
>99.99% of frames contain no cyclist.

Build `mine_frames_from_tracks.py`:
- read `*_tracks.csv` for a session
- for every cyclist-class track (counted **and** rejected, `hits >= ~5`),
  sample 2–3 frames spread across `first_t`..`last_t`
- extract those frames from the chunk `.mp4`
- run the detector on each to produce pre-filled YOLO labels (reuse
  `process_frame_detections` from `extract_frames.py`, which already applies
  `fuse_cyclists`)
- write `images/`, `labels/`, `previews/` in the existing dataset layout

Expected yield: ~2,000 frames, heavily enriched for cyclists — roughly the
target annotation budget in one pass.

**Add the grass false positives as hard negatives.** The review located 9 of
them with chunk and timestamp. Frames where the model fires on grass, labelled
with no cyclist box, are the single most targeted training signal available —
and `mine_frames_from_tracks.py` already extracts rejected tracks, which is
where most grass detections live. When annotating, resist the urge to skip a
frame because "there is nothing in it": a frame with a confident wrong box and
an empty label is exactly what teaches the model to stop.

**Critical:** the tracks CSV does **not** store bounding boxes, only track-level
statistics. Pre-labels must come from re-running the detector on the extracted
frames. Do not try to reconstruct boxes from the CSV.

### 5.2 Annotation

Free tools; do **not** hand-draw from scratch.

- **CVAT** (`app.cvat.ai`, free tier) — has box interpolation across video
  frames, the single biggest annotation multiplier here. Roboflow's free tier
  lacks it and makes projects public (check the MioVision data licence before
  uploading anywhere).
- **FiftyOne** for curation if the pool needs narrowing.
- Classes (already wired into `extract_frames.py`, `cyclist` appended at index
  6 so existing label files stay valid):
  `person, bicycle, car, motorcycle, bus, truck, cyclist`
  — `cyclist` = person visibly riding; `bicycle` = unridden/parked.
- Target **1,500–3,000 images**. Do not attempt the whole dataset.
- Box the *whole* cyclist (rider + bike) as one rectangle. Include tiny and
  partly occluded riders — those are the hard cases the model currently misses,
  and skipping them teaches the model to skip them.

### 5.3 Training

- **Split by SITE, never by frame.** Adjacent frames are near-duplicates; a
  random split leaks and inflates mAP badly. This is the most common fatal
  flaw in transportation-CV papers. `build_dataset.slurm` already enforces
  site-based splitting — preserve that.
- **Train on tiles matching inference geometry.** The pipeline tiles 2×2 with
  20% overlap at inference but the model was trained on full frames. SAHI
  reports +12–14 AP cumulative for fixing exactly this mismatch. Likely the
  single largest available win.
- `imgsz=640` for tile training (tiles are already crops).
- Before rebuilding the dataset: `mv dataset_frames/split
  dataset_frames/split_OLD_unfused` — the resume check skips existing frames,
  so otherwise you get a mix of fused and unfused labels.
- Model: YOLOv8-L is the current baseline. Run YOLO11-L / YOLO26-L as an
  ablation *after* the pipeline is correct, not before. `pilot_detect_v2.py`
  takes `--weights`.

### 5.4 Re-validate

Re-run the full BL Colonial session with the fine-tuned model and compare:
counted, duplicates, static tracks, misses, day/night ratio. **The success
criterion is not a better total — it is fewer flagged tracks at a similar
total.** Then extend to Edgewater (GT 228), NBL Pine Hills (GT 317, 98%
sidewalk), Aloma Path (GT 191).

---

## 6. Goals status (`goals.md`)

| Goal | Status | Notes |
|---|---|---|
| **1. Cyclist + vehicle counting** | 🔶 cyclists working but over/under-counting; **vehicles not validated at all** | no vehicle ground truth exists in the Excel data — scope question for the owner |
| **2. Infrastructure type** | ⬜ not started, but **much more tractable than assumed** | `facility_type` ground truth now recovered (63% sidewalk / 22% bike lane / 11% path / 5% travel lane) across 41 sessions. Combined with the matched BL/NBL pairs this is the strongest goal after counting. Approach: `METHODOLOGY.md` Idea C (unsupervised facility-zone induction from trajectory clustering) |
| **3. Cyclist speed** | ⬜ not started | hand-timed speed ground truth exists by facility (Travel Lane 14.5 mph mean, Bike Lane 11.8, Sidewalk 9.3). `METHODOLOGY.md` Idea A proposes distribution-matching self-calibration — no field measurements needed, which matters because the 2019 cameras are gone |
| **4. Near-miss / TTC / PET** | ⬜ not started | needs Goal 1 + Goal 3 first; no ground truth exists, will need a manually-reviewed validation sample |
| **5. Age / gender** | ⚠️ **recommend cutting** | no ground truth, ethics-review magnet, invites reviewer hostility out of proportion to what it adds. A limitations paragraph explaining the omission reads better than the results would. Owner's call |

---

## 7. Blockers and open questions

1. **15-minute interval counts were discarded.** `parse_raw_counts.py` calls
   `find_total_row()` and keeps only that row, so ground truth is daily totals
   with no time-of-day resolution. Blocks per-interval validation (a daily
   total can be right for the wrong reasons). Needs modifying to emit every
   interval row between `data_start` and the total row, keeping the timestamp
   column. **Requires 2–3 raw `.xls` files to inspect the row structure.**
   (No longer blocks mining — see §5.1.)
2. **`review_sheet.csv` verdicts not yet readable.** The owner filled it in but
   saved as `.numbers` (compressed protobuf). Ask for a CSV export
   (Numbers → File → Export To → CSV). Once available, the REAL/DUP/PED/BIKE/FP
   tally sets `MIN_NET_DISPLACEMENT` and the confidence floors from evidence
   rather than guesswork.
3. **Vehicle counting has no ground truth.** See §4.
4. **Day/night cross-check not done.** `Bike lane study counts day v night.xlsx`
   Totals sheet has a % night column per corridor. If it says Colonial North is
   ~15% night against the pipeline's 39%, that confirms the night over-count
   without watching a single clip. Cheap and high-value.
5. **Hour-boundary double-counting.** Chunks are tracked independently, so a
   crossing spanning an hour boundary counts twice. Expected < 1 per session;
   unmeasured.
6. **Disk.** All 41 sessions extracted = 325 GB vs ~314 GB free on a shared
   filesystem at 85%. `extract → count → delete` is mandatory; use
   `cleanup_session.sh` (refuses to delete unless every chunk has results).

---

## 8. File map

**Active pipeline**
| File | Role |
|---|---|
| `pilot_detect_v2.py` | main detector+tracker; tiling, fusion, confirmation, rendering |
| `vru_tracker.py` | association, track merging, class resolution |
| `extract_frames.py` | dataset builder (has `fuse_cyclists`, `cyclist` class) |
| `build_site_mapping.py` | video ↔ ground-truth join → `video_site_mapping.csv` |
| `validate_counts.py` | counts vs ground truth, day/night analysis |
| `audit_tracks.py` | flags duplicates/static/ID-jumps; emits review sheet |
| `plan_cyclist_clips.py` | builds clip render lists |
| `tracker_ablation.py` | old-vs-new association comparison (paper figure) |
| `Bike Lane Study Counts/fix_ground_truth.py` | recovers facility_type/movement |

**Slurm:** `run_site_array.slurm` (48-chunk array), `extract_session.slurm`,
`run_render_clips.slurm`, `run_v2_window.slurm`, `run_v2_full.slurm`,
`run_ablation.slurm`, `build_dataset.slurm`
**Shell:** `cleanup_session.sh`, `organize_repo.sh`

**Key data**
- `Bike Lane Study Counts/ground_truth_bicycle_counts_v2.csv` — **use `_v2`**;
  the original has empty `facility_type`/`movement` in all 202 rows
- `video_site_mapping.csv` — 41/41 matched
- `all_videos.txt` — archive inventory **and** the source of chunk→wall-clock
  times (`.001` = 05:00)
- `pilot_output/sessions/<SITE>_<DATE>/*_tracks.csv` — per-track results
- `pilot_detect_41807016.log` — cited evidence for the tracker diagnosis; keep
- `MioVision_Data.zip` — irreplaceable source; never delete

---

## 9. Conventions that matter

- Never run YOLO on the login node; always `sbatch`.
- Check on-disk chunk count against `n_mp4_chunks` **before** counting. A
  session with 2 of 48 chunks extracted produced 48 `COMPLETED` Slurm tasks and
  a plausible-looking −88% "error" — doing nothing is not an error.
- Detection runs at `conf=0.05` on purpose (track-before-detect). Do **not**
  raise it to clean up the video; that reintroduces the original zero-cyclists
  bug. Change the *rendering*, not the detection.
- ROI is deliberately the full frame. Cropping to the bike lane would discard
  78% of cyclists, who ride on sidewalks.
- Array ranges: most sessions are 48 chunks but Rinehart Road SW is 96, two are
  49, three are under 40. Under-provisioning silently biases counts **down**.

Owner confirmation (2026-10-20): all32person-box frames, including empty frames, were inspected; unchecked boxes were accidental. Original JSON preserved. `person_box_review_confirmed_20261020.json` marks all32reviewed based on explicit owner confirmation and retains all20boxes. Prediction pack still required for scoring; no accuracy calculated yet.

Confirmed person-box scoring completed locally (2026-10-20): found existing pack at `/Users/rithika/Downloads/final_review_20261020/rf_boxes`. All32owner-confirmed frames,20human boxes, one-to-one IoU>=0.50, saved thresholds. RF-DETR:4TP/10FP/16FN, precision28.6%, recall20.0%. Grounding DINO:13TP/35FP/7FN, precision27.1%, recall65.0%. DINO finds more labelled person boxes but generates more false boxes; neither is a demonstrated replacement for the counting reference. Selected repeated frames, not unique people/AP/whole-video cyclist accuracy or an independent holdout. Report: `vision3/best/test_colonial/exp_results/RF_DINO_person_validation_20261020.md`. Earlier statements that pack was unavailable or no score existed are superseded.

Received root colonial_speed_gates.json: two facilities with35ft/30ft and720x480reference, reviewer Rithika, but measurement_source="n/a". Original preserved. No physical speed calculated: exact measured endpoint correspondence not established. Asked owner whether these are known study endpoints or visible lane ends. Added placeholder-source rejection in exporter and speed measurement plus regression test. Numeric workbook lengths must not be assigned to arbitrary scene-wide segments.

Owner clarification (2026-10-20): colonial_speed_gates.json marks visible lane ends, NOT known study measurement endpoints. Therefore it is unsuitable for mph calculation; do not replace its n/a source or accept35ft/30ft for those drawn spans. Original preserved; review decision in exp_results/colonial_speed_gate_review_20261020.json. Physical speed remains blocked pending identifiable independently measured endpoints (or appropriate metric calibration). Image-motion estimates remain available; no further GPU run needed.

Exploratory calibration attempted locally (2026-10-20) at owner request: new code/exploratory_gate_check.py checks estimated finite gates without granting physical distance. Output exp_results/exploratory_speed_calibration_20261020/{RESULTS.md,crossings.csv,summary.json}. All7actual bicycle truth rows checked, both facilities (14checks), full saved unverified candidate tracks;0complete two-line crossings. None crosses the first line. Workbook rescanned:23Colonial speed records but0verified person links; no timestamps found in these speed rows. Thus0distance fits/0held-out validation pairs, no mph/MAE. Do not pair records by nearest speed or equate study record IDs with track IDs. Future fit requires independently matched people and crossings, fixed facility distance, and different people for validation. Three crossing tests pass (clip-time interpolation, finite-line nonextension, large-gap exclusion). No inference/batch submitted; original gates/truth untouched.

October23zone-editor failure: owner downloaded /Users/rithika/Downloads/pine_hills_zone_editor_oct23/ containing only index.html/status.csv, no camera HTML. Status PineHillsBLE MISSING_OR_UNREADABLE, No local readable source. No image generated; not browser failure. Updated generator to display source errors/expected paths prominently and fail explicitly if0editors. Updated downloaded index to explain blockage. Need locate/extract actual raw videos on cluster or correct inventory data-root; requested find command output. Do not tell owner to click nonexistent camera link.

Pine Hills zone input received: root pine_hills_bl_e_45bfdf.json, sitePineHillsBLE,date2019-08-28,720x480,reviewerRithika,area_alignment_confirmed=true. Validated finite in-bounds vertices;7regions total:road,bike,sidewalkand4grassregions. Copied byte-identically to zones/study_20261023/pine_hills_bl_e_45bfdf.json (root original/archive copy untouched). Raw embedded frame from downloaded ready editor shows2019-08-28 12:05:01PM, consistent with plannednoon sourcehour. Preview reports/review/pine_hills_zones_20261023.png. Ready for pilot after push/pull using inventory exp_results/pine_hills_inventory_ready_oct23/inventory.csv, scopepilot/sitePineHillsBLE/chunk13/zones-dirzones/study_20261023/require-zones/tagpine_hills_pilot_oct23. Nojobsubmittedlocally. This areafile is not speedcalibration or GPS confirmation.

Owner requested parallel progress while Pine Hills detection runs. Added code/speed_readiness.py/slurm: independent CPU2/mem4G/30min/noGPU job, output exp_results/speed_readiness_JOBID. Audits original ZIP selected small JPG/CUT sidecars across41mapped cameras (max2MB each), PIL EXIF GPS, explicit sidecar GPS/text clues and ffprobe location tags on extracted noon MP4s. Does not extract full videos, alter model/run, communicate externally, or assign mph. GPS candidates explicitly camera_position_verified=0; coordinates alone are not calibration. Supports default knownZIP/project paths. No newjobsubmittedlocally.
FullspeedworkbookA–Itables scanned/dedup375referencerows across14streetnames;23Colonial,0streetnamescontainingPine. Local exp_results/speed_reference_readiness_20261023/{RESULTS.md,all_reference_records.csv}. No matchedmodel-speed accuracy. Aliasuncertainty disclosed. Fournewtests pass: explicitGPSformat/ranges, smallsidecarpreservation/noMP4extract, oversizedsidecar exclusion, wholeworkbookcounts. docs/runs/STUDY_NEXT_STEPS.md hasparalleljobcommand; root todo status updated. Read returned cluster RESULTS.md before claiminglocationfound or physicalspeedready.

Parallel follow-up: owner asks what else to run. Added and ran CPU study_count_reference.py locally for Pine Hills BLE workbook,2019-08-28 12:00–13:00. Output exp_results/pine_hills_manual_reference_20261023/{RESULTS.md,channel_counts_15min.csv,counts_by_user_side_lane.csv,reference_coverage.csv}. Raw labelled channels only; derived totals excluded, blanks notzero, date rollover preserved. NBbicycles0bike/1sidewalk;SBbicycles4bike/0sidewalk;NBpedestrians0/0. SBpedestrian channels absent, not0. Camera-side correspondence NOT yet verified—do not equate137full-sheet bicycle counts or sum5pilot cyclists to this one-side view. Pedestrians99bins throughAug29 00:30;Bicycles192bins throughAug29 23:45. Four meaningful parser tests pass: rollover/derived totals, blanks, intervalend exclusivity, noninteger rejection. No clusterjob needed for manual reference; docs have optionalCPUregeneration command. Wait for actualmodelresults/metadata rather than redundantGPU sweeps.

Owner supplied root camera_metadata.json and asks to use footage with existing speed validation. Inspected JSON41entries: no textual location clues in CUT previews (binary),0explicitGPS, onlyUniversityNorth/ColonialNorth/PineHillsBLE noonMP4s probed at audit time; others unextracted. Preserved identical JSON under data/reviews/speed_readiness_47393224/. No video has independently validated MODEL mph; spreadsheet study speeds are reference measurements with unresolved recording/person/endpoints.
Prepared UniversitySWspeed candidate: source SCU8PM2019-09-25 chunk00908:00–09:00inferred, sourcefolderSW Speed University. Workbook78UniversitySidewalkspeedrecords all55ft; date/camera correspondence notproven. Manual University_SW_Speed workbook11NorthSidewalkcyclistsin08hour. Selectionmaxfirstday8–17manualhourcount, earliesttie08/14/16all11, not basedonmodel and notunbiasedholdout. exp_results/university_speed_candidate_20261023 stores78refs, emptyrecord/personlinktemplate, manualcounts, RESULTS caveats. Added code/prepare_university_speed.sh (bashsyntaxchecked) to extractone282MBsource, probe/isolatehour, buildzoneeditor/manualcounts into mktemp workdir; noGPUorjobsubmission. Needdownloadactualeditorimage to inspectmeasuredmarkers/landmarksbeforechoosingcalibration. Neverassign55fttolaneendsorclosest-speedmatch. PineHills counting continues. Mainrunbookupdated.

University prep folder downloaded at /Users/rithika/Downloads/university_speed_prepare_pYuzTj/. Inspected embedded real frame in zone_editor/university_sw_speed_9dc0b1.html:720x480, overlay2019-09-25 08:05:02AM, consistent withselected08hour. Visible sidewalk runs throughmiddle, roadright, grassonbothsides; no positively identified55ftstudyendpointmarkers, streetnames or readablelocationclues. Sidewalkjointsvisiblebutspacingunknown—do notassumefivefeetoridentifyarbitraryjointsas55ft. Rawframecopy reports/review/university_speed_source_20261023.jpg. Downloadedmanualcounts confirms11NorthSidewalkcyclists08–09. Nextowner canmarkactualsidewalk/road/grass inexistingeditor; noGPSneededforareas. Tracking/countspossibleafterzones, butphysicalspeed/calibration and78reference-record links remainunverified. No newGPUsubmittedlocally.

University owner zones received (2026-10-23): original university_sw_speed_9dc0b1.json preserved; byte-identical canonical copy in vision3/best/test_colonial/zones/study_20261023/. Six finite in-bounds polygons: three road, one sidewalk, two grass; bike/path empty. Site University SW Speed, date2019-09-25,720x480,reviewer r,alignment confirmed. Overlay reports/review/university_speed_zones_20261023.png visually checked. Areas provide no metric distance. Next push/pull canonical JSON, submit study_batch.py with exp_results/university_speed_prepare_pYuzTj/selected_hour.csv, scope pilot, site University SW Speed, pilot-chunk9, zones-dir zones/study_20261023, require-zones, tag university_speed_pilot_oct23. No job submitted locally; measured endpoints and speed-reference/person links remain unverified.

2026-10-24: Owner downloaded both completed study pilot folders; preserved under reports/cluster_returns/20261024/. Both outputs.csv state SUCCEEDED, ~1hour each. Pine Hills:1cyclist_or_motorcycle,6pedestrians,492vehicles; counted pedestrian lanes1bike,3grass,1sidewalk,1uncertain; cyclist road. University:0cyclists,5pedestrians,2075vehicles; pedestrians1road,2sidewalk,2uncertain. University manual reference11NorthSidewalk cyclist observations is a warning, not established matched accuracy: confirm source/camera side and review missed/misclassified users. Neither ready for scaling/validated speed. Downloads contain per-track summaries but not raw trajectories/videos. Next download counts and annotated run directories for both saved run tags; inspect videos and raw tracks to distinguish detection, classification/filter, duplication and alignment issues. No new inference submitted.

2026-10-24 raw counts downloaded and preserved under reports/cluster_returns/20261024/<run_tag>/. Audit PILOT_TRACK_AUDIT.md and university_bicycle_candidates.csv. University109track rows;5final BICYCLIST tracks (IDs57,61,66,88,132), all fail3second observed-duration check,0counted. Audit confirms XCLIP bicycle -> pedestrian changes e.g.ID14,16,105,161 with detector cyclist share below15%; all also failduration. Observed duration is not first-last elapsed span; intermittent detections matter. Need visual adjudication before filter/model changes or claiming missed true cyclists. No newGPUrun needed to inspect saved outputs. Speed gates are still not configured from owner marked screenshot; no mph calculated.

2026-10-24 speed calculation requested and attempted: added reusable map_gate_speed.py plus University map_speed_gates JSON,55.17ft owner map distance, pixel transcription1600x1070->720x480. Checked109person tracks, noncoasted finite gates and max0.5s gaps including interior:0complete automatic crossings;7tracks touch at leastone gate. Downloaded annotated0845-0900 video available locally. Manual front-wheel video review of red-top cyclist around08:52: A bracket422.5–423.0clipseconds,B427.25–427.5; midpoint4.625s =>8.13mph; timing-only7.52–8.85mph, excludes map/endpoints error, no Excel link. Sourceburnclock~2s ahead header; evidence usespresentationseconds. Report reports/cluster_returns/20261024/university_map_speeds/RESULTS.md,manual_video_speed.csv,evidenceJPEGs. No precise actual/validated speed claim; automatic0 and manual1 kept separate. Four meaningful crossing/gap checks passed.

Owner requested speed comparison at a location with existing study speed records. Rechecked original bicyclist speeds.xlsx shared fields and23Colonial refs:12bike35ft,11sidewalk30ft; no recording date/timestamp/person links found, bike directions blank. Selected Colonial comparison packet reports/cluster_returns/20261024/colonial_speed_comparison/ contains reference rows, facility summaries and7bicycle truth comparison rows with unknown links/speeds intentionally blank. No site with confirmed matched model-speed validation established. Need original speed timing notes/reference footage identifying people and measured endpoints, or exact mapcalibration plus explicitly descriptive distributioncomparison. Do not reuse Universitydistance or assign workbooklengthtoestimated Colonialgates.

2026-10-24 owner finds map/gate workflow hard and explicitly requests research first. Researched primary papers and author code, saved docs/research/CCTV_TRAJECTORY_SPEED_20261024.md. Corrected prior overrestriction: Maps/gates optional; partial trajectories yieldmph after automatic camera/scalecalibration from vehicle dimension/shape priors (BMVC2014,ICCV2021 naver/cctv), pedestrianheight calibration another approximate route,2026keypoint-template preprint option. Recommend feasibility/adaptation ofICCV2021 onColonial daytime; NOTimplemented/runtested. Needscale fromsomewhere,35ftmustmaptoactualsegment, no workbookindividualvalidationwithoutpersonlinks. Road->sidewalktransfer conditionalonplaneheight; sharedcalibrationmanualtimingnotindependentscalevalidation. Owner needsno furtherMapinput for automatic experiment.

2026-10-24 owner asked apply all speed methods and choose closest reference. Implemented code/speed_research.py and speed_research.slurm for separate ICCV2021 pretrained-author car-mask calibration adapter and paper-inspired pedestrianheight optimization. Pinned naver/cctv commit80b8bc4964eddfda32c40e6d1c8fe8b62f777f55, original MaskRCNN masks (no bounding-box-as-mask substitution), IoU track association, seed, finite H checks, hull-limited gap-filtered existing7truth candidate trajectories. New test_speed_research.py three tests pass: physical projection, synthetic scale recovery, insufficientdata rejection. Author weights actual CPUload/forward passed. Local data only1qualifyingped track; height fit refuses instead of inventing scale. Local torchvision missing; realcarcalibration mustrunHPGoriginalrawvideo. Methodstatuses retain BMVC2014/Sochor2017/2026keypoint as NOT_IMPLEMENTED_MISSING_COMPONENTS; NOT allfivepapersimplemented, no newSlurmjobsubmitted. One job command sbatch code/speed_research.slurm, result exp_results/colonial_speed_research_JOBID. Local finalreport reports/cluster_returns/20261024/map_free_speed_local_final/RESULTS.md. ComparisonCSV descriptivegroupmeans only, notrankedwinner or matchedaccuracy; workbooknotusedinfitting. Mainrunbookupdated. Limits: carplane->sidewalkheightunverified, learned/assumedscaleunvalidated, headfootboxerrors, identityunverified. Additionalpapers needfullpipeline/assets; don'tclaimappliedthem.

October24 owner accepts exploratory closeness selection and asks other sites, ped/bike-only andallpapersonerun. Confirmed375BICYCLEspeedrefs across14streetlabels; counts stored reports/cluster_returns/20261024/speed_reference_locations.csv. Updated speed_research.py outputs bothpedestrian/cyclist truth candidates, nevercarspeeds; onlycyclists comparedtobicyclistworkbook. New exploratoryclosenessranking per facility oncommoncandidateintersection ofavailablemethods, singlemethodexplicitno competition; nofittingworkbookorvalidatedaccuracyclaim. Tests3pass plus localrunner endtoend statusoutput. Latestlocalreports map_free_speed_local_with_selection. Still2methodsimplemented,3missingcomponents (notall5); noHiPerGatorjobrun. Needcommunicate ICCV usescarsasrulers only andpapermethodsforcarsdon'tdirectlyestimatebicyclisttypes; road/sidewalkplaneriskremains.

October24 owner confirmed bicycle-only speed scope and requested professor-facingREADME/reference sites +Universitymanualcomparison. RootREADME updated:14streetlabels375bicycle speedrows/facilities/sourcecellCSV, no ped/car speedreferences; implementationstatus andsinglejobscope. Updated runner truthfilter backto cyclistONLY (notmotorcycles/peds), whileped/car observations maycalibrate. Added university_manual_comparison purefunction and sourceinput data/reviews/speed/university_manual_crossing_20261024.json; jobreport UniversitymanualcomparisonCSV recalculates8.133mph from55.17ft/4.625s vs78sidewalkstudyrecordsmean9.493mph approx, difference−1.36mph, timingrange7.52–8.85excludesdistanceerror; no matchedvalidation/rankacrosssites. Localreport reports/cluster_returns/20261024/bicyclist_speed_comparison/RESULTS.md. Savedmanualinputversioned, no hardcodedMacdownloadsdependency forcluster. Runner no video locally:bothautomaticmethodsnotcompleted(currentpeddata1track),Universitysavedtimingcomparisoncalculated. NoSlurmsubmission. Addedtestsmanualunitconversion,site/facilityfilter,wronguserrejection,invalidbracketrejection;6tests total.

October24 owner requested dedicated location-speedREADME and exactfuturemeasurementtimes. Created docs/SPEED_REFERENCE_README.md with14location means/medians/minmax/samplecounts,facility-specificmeans andmeasuredlengths, explanatory arithmeticmeanofindividualsource_mph NOTperhour/15min (reference rowslacktimeofday), sourceCSVcellprovenance. RootREADMElinksitprominently. statsCSV reports/cluster_returns/20261024/speed_reference_summary.csv. Updated metric_trajectory_speed.estimate toreturn exact measurement_frame_intervals spanning observed samplesusedbyacceptedvelocitywindows (gapsseparate). speed_research.py addsdate,sourcevideo,clipstart,measurementclockstart/end,disjointintervalJSONandclipseconds,clockqualification,speedstatistic to rowsandreport. ManualUniversityrowsalsoincludepresentationcrossingbrackets andclockbasis/sourcevideo; report07:02.50–07:07.50 playerportion,sourceburnclock~2saheadgeneratedclock. Tests8speedresearch+9studyextensionspass; localtimedreport reports/cluster_returns/20261024/bicyclist_speed_timed_report/RESULTS.md. No newinferenceorvalidatedmph. Supersedes earlier docs claiming pedoutputs. Singlejobunchangedbutrequiresnewcodepushpull.

October24 user wantsfinishonepass, questionsone-to-fivecyclistsperreference site/higherqualityalternatives. Added speed_site_screen.py +submit_speed_pilot.py +4tests. Plan dryrun15candidatecameras/13reference streetlabels;SilverStarno mappedcandidate. Candidatealiasesdocumentednotverified, facilitymatching curated(e.g.pathref->pathcam). Fixedfirstdaynearestnoon source,45secondpreviewsat300/1200/2100,33.75mintotalmax,5GBnewextractioncapZIP, noallhourdetectorinference. HTMLindex,JPGs,sourceclock/dimensions/Laplacian table/status, notqualityaccuracyranking. One command python code/submit_speed_pilot.py --go preflightsPythondeps thenCPU1h/4cpus/6G screen followedGPU4h/1gpu16G Colonialexperiment afterany. Bundleroot exp_results/SPEED_PILOT_TAG withsubmissionJSONpartialIDsretained+logs/README, camera_previews/,speed_results/. Nojobsubmittedlocally. Preferfirsteligibleup-to5cyclistsperusablecamera,target3practicalnotpower guarantee; don'tstopwhenspeedmeanmatches/workbook,don'tsilentlydropdetectionmisses. No automaticallsitecalibration, no3missingpaperimplementations. UpdatedmainREADME/speedREADME/runbooklatestentrypoint; olderdirectsbatchnotalso needed. Tests4realpreview/sourcereadonly+8speed+9extensionspass. Needuserpush/pull newfiles beforeonecommand. No physicalvalidationsupplied.


## Preview recovery after job47544655 (October24)

Original bundle: exp_results/SPEED_PILOT_20261024_183520. CPU job47544655 extracted2,931,198,701bytes but generated0/15previews because ffmpeg was absent fromPATH. That is an environment dependency failure, not bad camera quality. Speed job47544658 is separate; do not submit the full bundle again for preview recovery.

Push/pull the new preview_ffmpeg.py, retry_speed_previews.py, speed_site_screen.py and submit_speed_pilot.py. Activate yolo_env on the HiPerGator login node, then:

```bash
python code/retry_speed_previews.py exp_results/SPEED_PILOT_20261024_183520 --go
```

This resolves/checksFFmpeg withlibx264. If absent, installs the pinned imageio-ffmpeg0.6.0 wheel into ~/.cache/objectdetect/preview_runtime using pip --target (no changes to shared YOLO packages), then passes its absolute binary path to the CPU job. [Package source and bundled executable details](https://pypi.org/project/imageio-ffmpeg/0.6.0/). No GPU submission and no ZIP extraction. Original selected_sources.csv reused exactly; prior reports untouched. New output camera_previews_retry_TIMESTAMP under the same bundle, path and CPU jobID printed, manifest preview_retry_JOBID.json. Download that new directory when done and open index.html.

Future full submissions bootstrap/checkFFmpeg before job submission; workers also check before extraction and now exit with error if0previews, after retaining diagnostic reports. Per-camera encoder stderr appears in screening.csv/RESULTS.md. Seven screening/recovery tests, eight speed tests and nine study-extension tests pass locally. Cluster recovery still requires running above command; no retry submitted locally.

October24 returnedGPU47544658producednoautomaticmph (pedheight/ICCVNOT_COMPLETED),Universitymanual8.13savedcomparisononly. Needremote method_status.json oriccv2021/error.txt beforedecidingGPUretry. CPUretry47545063failedbeforework with SyntaxError fstring expecting}: same-single-quote expression error_summary or 'None.' inside singlequotedfstring, acceptedlocalPython3.13/PEP701 butinvalidpre3.12. Correctedprecompute fallback, simpleinterpolation. All6runtime scripts verifiedcompileactual/usr/bin/python3=3.9.6; addedregressionportableparsertest, realpreviewtestsretain. GPUreportnowincludesmethodfailure detail column forfutureease. No recoveryjob submittedlocally. Needpush/pullfixandCPU-onlyretry existingbundle. DoNOTresubmitfullbundleorGPUwithoutdiagnosingactualICCVerror.


## Diagnosed speed failure47544658 and targeted correction

Returned method_status.json: pedestrian-height fit lacks20independent qualifying tracks; ICCV adapter had fewer than10usable car tracks. No new automaticmph. These are implementation input guards, not proof that the published methods failed, and20/10are conservative project thresholds rather than paper-established optima. Universitymanual8.13mph is still only a saved result.

ICCV adapter previously sampled every15sourceframes (~2Hz) with last-frame greedyIoU, potentially fragmenting fast cars. Updated to every3frames (~10Hz), one-to-one HungarianIoU matching with constant-velocity box prediction and max0.3secondtrack gap. Score>=0.8, minimum boxdimension15px, >=4observations, netmotion>=30px retained; minimum10usablecartracks retained. Budget3000sampledframes (~5source minutes), early stop after20usablecartracks and15source seconds, independently of speed-reference agreement. This is a new adapter configuration, not a demonstrated improvement on real footage yet.

Always saves raw_car_observations.npz, tracking_diagnostics.json (detections/track lengths/usabletracks/sample rate/scanned seconds) and periodic annotated diagnostic_frames even when minimumtrackguard fails. Doesnotexportcar speeds. Existingpedestrian-heightmethod remainsdata-insufficient; no newgeometry orindependentspeedvalidation claimed. Afterpush/pull, a targeted GPUretry canuse `sbatch code/speed_research.slurm`; it doesnotrepeatcamera previews orZIPextraction. Newoutputexp_results/colonial_speed_research_JOBID. Do not alsoresubmitfullpilotbundle. Review preview retryresults separately. Eleven speedresearch tests andeightpreview/recoverytests pass includingPython3.9compilecoverage, plusnine studyextensionspreviouslypassed.

October24 owner sayssuccessfulpreviewsareinDownloads. Located Downloads/SPEED_PILOT_20261024_183520/camera_previews_retry_20261024_184801_864715 with45clips15cams. Systematicsampled1,4,...43seccontactframeinspectionall45;NOTcontinuousframebyframereview. Motioncandidatehelper0.5sproducedmanycars/shadow/vegetation;onlysubsetofmotionsheetsvisuallyinspected,doNOTclaimexhaustiveabsence. ConfirmedbicycleColumbiaAve preview_300.mp4 player1–3s, denseframes1.5–2.5bicyclevisible,sourceSep10,2019nominal12:05:01–03,burnclock~2sahead. Cyclistnear-camerabikelanevisualprovisional,rightward,poleoccludesstart;rightsidepedestrianseparate. Nootherbikeconfirmedinitialsampledreview;notzeroGT. Evidence+CSV+0–5secclip+coverageledger reports/cluster_returns/20261024/preview_visual_review/. Yellowtransversemarksvisibleseveralviewsbutnotverifiedknownworkbookspans. Initialspeed_resultsdownloadstillNOT_COMPLETEDbaseline;improvedGPUretryunknown. No newinferenceorspeedcalculated. Donotaskownertowatchallagainorclaim3–5percamfound.

October24 owner supplied Downloads/colonial_speed_research_47545558 and wants full recording durations before choosing shortest, no full-hour inference. Inspected downloadedcalib:28usablecartracks/458boxesfrom674detections,700samples,stride3,69.97scoverage; learnedHsaved. All7bicycle candidate outputs lack sufficientcontinuousin-hull observations,0mph. Downloadmissingmethod_status/RESULTS; foundrelative-root bug(rootPath('.')parents[2]outside try) in report stage, fixed root.resolve and added --reuse-calibration for CPU-onlyreportrebuild. Rebuilt locally reports/cluster_returns/20261024/colonial_speed_47545558_report_rebuilt/RESULTS.md from actualsavedH, no newGPU/detection; statusICCVEXPERIMENT_COMPLETED doesnotmeanbike-speed success.
Created docs/VIDEO_DURATION_README.md with15screenedcamera lengths andall41inventorytable, sourcefileCSV1919rows andbycameraCSV underreports/cluster_returns/20261024/recording_lengths/. Downloaded Universityprepinventory has52measuredsources:48ColonialNorth=>47.99hcomplete,2UniversityNorth~2hpartial,1PineHillsBLE~1hpartial,1UniversitySWSpeed~1hpartial. Otherfilecounts are nominalhourassumptions, NOTactualauditeddurations;Columbia49filesincludesmultipartuncertainty. ShortestrefcandidatePleasantHillPath31files(~31h),WestOrangePath37(~37h),others48exceptColumbia49. PineHillsBLE25shortestoverallbutnoPinespeedrefs. RecommendrespectshortestchoicePleasantHill yetonlyshortfixedexcerptneeded; totalrecordinghoursnotrequiredinferencebudget. Do notsubmitnewjobsuntiluserchooses. RootREADMElinkeddurationguide. AddedCPUrebuildrelative-rootregressiontest; no newphysicalcalibrationvalidated.

OwnerOctober24requests adaptive15-minsegments eachspeedreferencelocation,combineuntilsamplequota,skipColonial. Implemented adaptive_speed_batch.py submit/worker/report, selected12sites(LeeNorthonly,notpoolNorth/South), skipColonialownerchoice(notcompletedmph) andSilverStarunmapped. quota=min(n,5,max(3,ceil(n/3))):Lee2Columbia3Daniels4other5. Max4windows/site=60min,12hmaxfootage,2GPUconcurrent array +afteranyCPUreport. EachsitecarcalibICCVfirst(no alternate3papers), fixedb4envstudy_batch.build_plan, existingresearch_worker.execute15minabsoluteSTART/MAXframebounds, overrideSLURM_ARRAY_TASK_ID=1 withinpipelineenv topreventouterarrayindexchangingclockchunk. Failedcalibrationstopssitewithoutinference; failurespersiststatusandworkerexitnonzero. QuotaeligiblecountedBICYCLISTwithcontinuousmph andnonboundarycensored;labelincludespossiblemotorcycle,identityunverified,reviewneeded. Firsteligiblechronologicalonly, no speedagreementselection. Pooledper-personmean/CSV exacttimes+annotatedpaths+exclusions+failurestate. Explicit --exploratory-road-plane-transfer allowsfullframehomography outsidecarhull, coplanarityunverified; strict speed andsupportfractionseparate, no accuracyclaim. Paperhorizoncheckexistingestimator; nofitstudymeans. AvoidconcurrentgitcheckoutbyonlycheckingoutifcacheHEADdiffers. New7tests:quota,12-siteexclusions, boundary,personweightedmean,missingnot0,segmentnonoverlap/clockarrayoverride,chronologicalunbiasedselection. DocsrootREADME+speedREADMEtopupdatedcurrententrypoint. Dryrunprinted12tasksand720mincap; noSlurmjobsubmitted,norealspeedresults. Needfinishverificationbeforefinalcommands.

Adaptive speed batch final verification:36tests passed together (7adaptive+12speed+8preview/recovery+9studyextensions), Python3.9compilepass, gitdiffcheckclean. No actual cluster adaptivejobs submitted. Ready for user push/pull then python code/adaptive_speed_batch.py submit --max-windows 4 --exploratory-road-plane-transfer --go.

Owner asksfoundcyclistcountsandtimestampspluswhetherColonialrerunneeded. Adaptiveworkerwindowstatsnowstorefound/countedspeedeligible;comparisonCSVreportsallthreeandselectedsample. Aggregateall_candidate_timestamps.csvreadsper-siteCSV(all candidates),canbackfillolderworkerswithoutnewcounterfields,plusselectedtimestampsexistingMD. Addedtestfound2/counted1/eligible1/selected0andtimestamps,now8adaptivetests. ColonialtruthCSVverified7bicycles13ped1moto;legacy6bikesFOUND,1DETECTEDBUTNOTCOUNTED. Existingcounts/timesneedNOdetectorrerun;Colonialmphnotvalidatedandstillnotcomplete,remainexcludednewbatch.


## Latest update: independent site reports and Colonial included (October 24)

The adaptive speed batch now includes Colonial North: 13 candidate locations, Silver Star still unmapped. Each site writes RESULTS.md/comparison.csv/status.json at startup, after every completed 15-minute window, and on caught failure. Human-readable site folders contain calibration diagnostics and windows/wNN inference logs/settings/raw output references. No waiting for other sites. Global aggregation remains an afterany job. Colonial source clocks now use the selected source hour with chunk 1, independent of array index. Colonial pooled study mean is explicitly not facility-matched validation. Code prepared locally; not submitted here.

Run after pushing and pulling updated code:
```bash
python code/adaptive_speed_batch.py submit --max-windows 4 --exploratory-road-plane-transfer --go
```

Tests: 39 local checks passed. GPU model execution has not been run locally.


October 24 owner video review and original count check: reports/cluster_returns/20261024/count_review_baxter_carroll/ saves owner observations and original per-channel count rows. Carroll 12:30–12:45 study total 2 versus model0; owner saw cyclists12:39 and12:43:53, latter overlaps rejected track34. Baxter all noon-hour study bins0 versus model0; owner short review saw no cyclist. Count bins cannot identify exact seconds or link speed references.

Manual alternative prepared October24: [manual bicycle speed review](../../docs/SPEED_WORKFLOWS.md#workflow-1). CPU-only workbook-positive interval clips and browser manual point marking; thresholds unchanged, saved learned calibration gives exploratory mph. Initial scope selected adaptive source hours; outside-hour positive bins listed, not silently covered. Two tests passed; extraction not run locally.


## October25 manual annotations analysed

manual/README.md is the current plain-language result. 18 original JSONs preserved; four reused IDs split at >30sec gaps per owner statement; IDs scoped to source interval. 30 encounters against50raw-channel study bicycles across27selected positive bins (20not represented in annotations, not automatic detector misses).13speeds from pack calibration: Aloma19.81vs13.58, Carroll12.37vs11.89, Colonial10.71vs9.54, Columbia12.47vs12.24mph. Five other annotated sites lack bundled calibration: Edgewater, Lee, PleasantHill, Rinehart, University. No missing speed treated as zero; missing JSON owner could not find cyclists, not proven absence. manual/analysis contains corrected observations, per-encounter clocks, interval coverage, site summaries, ID split audit and source pack snapshot. code/analyze_manual_bicycles.py reproduces output; code/export_manual_calibrations.py exports small final HPG calibration metadata to finish without reannotation/GPU/videos. Compare unmatched study speed means only, not person-linked accuracy. Seven focused manual checks passed; Python3.9 compile and JS-free report generation checked.


October25 follow-up: manual/README.md now compares automatic vs manual vs study means in the same site table. automatic_report_snapshot.json preserves rounded values previously pasted by owner; Carroll same-bin automatic zero comes from downloaded bin-count CSVs. Automatic sample n is not bicycle count. export_manual_calibrations.py now exports small matrices plus original automatic comparison/selected candidates and complete-window count rows, enabling pending manual mph and matched-bin count comparison. No reannotation or video transfers required. Same calibration is shared by manual and automatic methods, so manual comparison is not independent speed validation.


October25 final export applied: sofar.md JSON extracted to manual/analysis/final_batch_export.json (13calibrations,13automatic summaries,43complete bin rows). Existing30manualencounters now yield29speeds; oneEdgewater1.4second span excluded. Manual means: Edgewater14.00, Lee12.36, PleasantHill8.99, Rinehart12.01, University16.98mph; earlier13speeds unchanged. README combines automatic/manual/study means and coverage-aware automatic/study counts. Columbia6automaticvs3study across2/4selected bins suggests overcounting (not per-person false-positive proof); Carroll0/2, Colonial3/3, Lee2/10, Rinehart0/3. Partial/missing bin exports not zero. No rerun/reannotation required. 8focused tests passed.


October25 column wording and Aloma recovery: manual README uses Validation (study count/reference mph), HiPerGator (automatic), Manual (annotations/mph). Aloma unavailable now explicitly run interrupted (sacct NODE_FAIL), not no usable bicycle speeds. adaptive_speed_batch.py recover --directory exp_results/ADAPTIVE_SPEED_20261024_195012 --index0 --go creates new single-site plan, reuses checked saved H/hull, restarts inference with unique tag, and submits worker+afterany report. Does not rerun other sites or overwrite old outputs. Prepared only; not submitted here.20focused tests passed plus Python3.9 compilation. Recovery output needs later merging into comparison; old nodefail remains historical.


October25 all missing values follow-up: owner already submitted Aloma recovery47763750/report47763751 to ADAPTIVE_SPEED_recovery_20261025_231145. Do not duplicate it. Added CPU audit_missing_speed.py and .slurm to audit every missing speed/annotation/partial count using saved source tracks/rules, export partial counts rather than drop them, and produce up to6raw12-second candidate clips per missing manual interval. No threshold change/inference rerun/promotion of rejected tracks. index.html is clue viewer; annotation remains in original manual editor with full-source timestamps. Expanded export now supplies candidate/rule audits and partial bins. README labels Carroll12/Rinehart3 candidates rejected by counting gates, WestOrange5study bicycles unlocated in manual review, Columbia early quota30min coverage, Edgewater1.4smanual exclusion, AlomaNODE_FAIL. Reason for invisibility cannot be inferred as blur without review.21focused tests passed; GPU/CPU audit job not submitted locally.


October25 sampling clarification: manual README/report generator now explicitly explains firstday nearest-noon source-hour selection (practical fixed daylight pilot, not quota/representative speed matching), then study-positive15min bins. Aloma12:00/12:30/12:45 onOct30 =>45min and1+1+2=4bicycles;12:15 zero omitted.26speed-workbook records cannot be timestamp-linked, including no proof they occurred during supplied48hours. Added recording_durations.csv and14location table from existing by_camera.csv: Colonial47.99h measured, most~48h estimates, PleasantHill~31h, WestOrange~37h, Columbia49multipartfiles unknown total, SilverStar no mappedsource. No code/actions needed from owner now; exact other durations require unavailable source metadata and are not invented.


October25 critical reference provenance correction: owner supplied Mighk Wilson email saying speed observations were stopwatch-timed FROM VIDEO at HALF-SPEED, accounted for in calculations (not in-person timing). Some corridors recorded with2cameras, others revisited specifically for speed; Baxter speed-only to increase travel-lane cyclists. Do not double cached workbookmph. Read-only workbook formula spot check: primaryH=F/G,I=H*.681; SilverStarH=F/(G/2). Exact per-row video/time/endpoint matching still absent. Updated generator/manual README/SPEED_REFERENCE_README; source evidence summary manual/analysis/source_provenance.md. No existingmph/counts altered. Aggregate tables are not per-frame box labels.


October25 README simplified: manual/README.md now53lines with single combined count/speed/duration table, concise Aloma4vs26 explanation, half-speed provenance, limitations, and14location recording-hours table. Long encounter evidence moved to manual/analysis/DETAILS.md; per-encounterCSV unchanged. Report generator refactored to preserve concise layout. No speed-engine factor change: source_mph already uses supplied corrected workbook values; applying2xwouldbe wrong. Do not assert26Aloma speedobservations cover same48h: corridor-level sample with unmatched session/timestamps; author mentions speed-specific revisit.21focused tests passed and30encounters/29speeds/14durationrows unchanged.


October25 manual-method explanation added to concise README/generator: rear-tire ground clicks plus original-video times form per-cyclist trajectory; saved learned camera homography converts image coordinates to estimated metres; sum successive distances / first-to-last elapsed time *2.2369362921 givesmph; site mean weights each available cyclist equally. Shared unvalidated metric scale/clicknoise/raisedplane caveats retained. Sourcefiles=MP4count vs hours=sumdurations explained. Columbia49MP4s includes multipart0000.02.001 etc, full lengths unprobed, so not49hours; noonselectedsource remainsusable. No calculations changed.


October26 research citations verified and added to concise README/generator: Revaud & Humenberger ICCV2021 paper + official naver/cctv authorcode for calibration/tracking-metricdisplacement basis. Manual tireclick/pathdistance-time is our adaptation, not exact publishedmethod nor bicyclevalidated paper result. FHWA TrafficDetectorHandbook chapter2 supports known-distance timedtriplines and radar/lidarsensors; OpenCV opticalflow officialdocs support alternativeimage-motion collection. Added alternatives table: measuredgates, surveyedcalibration, opticalflow, independent synchronizedsensors; none claimed newlyimplemented. Metric scale requirement remains. No speedvalues changed/no newrun.


October26 implemented/run manual_flow_speed.py: actual27localmanualpack MP4s available,30normalizedencountersprocessedCPU. First-click seed only, LucasKanade patchfeatures with forward/backcheck, coherentmedian translation; futureclicks heldout, no re-seedfromtruth.20pxmaxheldout drift engineeringthreshold preselectednotstudymeanfit.2PleasantHilltracksaccepted provisional9.507/9.636mph (mean9.5715),27drift/coveragefail,1Edgewater1.4sno metricspan. Saves perpersoncomparison/rawflow/driftchecks/reviewMP4/siteCSV/RESULTS to manual/optical_flow_20261026. Failedflow speeds diagnostic-only. Alsoendpointfirstlastdistance/time(>=1.5s) using sameH; not independentmetricvalidation. Existingmanual29speeds unchanged.5synthetic tests including actualencoded movingtexture video passed; visualreviewonePleasantHilloverlay. CodecompilesPython3.9. Owner neednotrerunHPG. MainREADMEgenerator linksresults; faileddevelopmentoutput replacedbyfinalcheckedrunonly.


October26 coverage clarification: user viewed opticalflowreport lackingHPGcolumn, mainmanualREADME stillhadit. Added Validation andHiPerGator means toflowreport+generator, contextonlynotmatchedsample. MainREADME nowexplicit Manualselectedbins/minutes vsHPGcompletedminutes: Aloma45review/0completed originalNODE_FAIL (recoverypending), mostsites60HPG,Columbia30HPGquota. Manualselecteddurationnotcontinuousannotations (meanusesperpersonshortspans). No flow/inference rerun needed for formatting; table regenerated fromexistingCSV.


October26 Aloma recovery47763750/47763751 COMPLETED0:0 confirmed owner sofar. Fourwindows59.97553min,5bicyclelabelled candidatetracks (1,0,1,3),allcounted0andeligible0. No auto speed, TARGET_NOT_REACHED_WITHIN_LIMIT is finishednotcrash. Savedsource manual/analysis/aloma_recovery_47763750.json and automatic_recovery_updates.json; generator overlays recovery site/windowcounts after oldbatch export so rerenderdoesnotrestoreinterrupted. Lastwindow898.5318556sec partial; full-bin export comparatoronly2of3positivebins,0vsstudy2,thoughall4manualcyclists occurwellbeforeending. ManualAloma19.81mph4andstudy13.58mph26unchanged. MainREADMEcoverage60minutes and rejection reasonupdated; flowreportAloma referencecontextupdatedwithoutflowrerun. No thresholdchange/modelrerun/reannotation.


October26 Aloma printedtrack audit: owner sofar has5rejectedBICtracks, durations2.9,1.6,2.0,2.7,1.7sec, allbelow3sec gate;4have100%detectorbike andweightedBIC .98–1.00 (w0id2,w2id1,w3id1,w3id8). w3id2=.66conf,.92weighted,46%detbike,31pxheight. Saved manual/analysis/aloma_duration_audit_20261026.csv;READMEgenerationnoteadded. Three-secondgate isdefiniteblockingcondition; othergatesunproven withoutaudit. Manual4/study4 vs5candidates meanscannotclaimall5true/improvedaccuracy. Baselineunchanged; recommendseparatecachedshort-trackassessment withmotion/typeverification, notzero-durationunconditionalacceptance or3sec->.3globally.


October26 user authorized counting fix to include shorttracks/update mph. Implemented optional --day-bicycle-min-seconds in adaptive_speed_batch submit/recover; recommended1.5s (capturesfiveAloma1.6–2.9s duration) vsbaseline3. Explicit NIGHT_BIC_MIN_SEC retains former3s fallback; existing night-only.3exception/PED/confidence/motion/static/vetounchanged. Added recover --all-sites tocloneall13originaltasks withsavedcalibrationreuse, unique shortdaytag,2GPUconcurrentarray, afteranyreport andper-site snapshots. NeedHPGactualnewdetectionrun, not locallysubmitted. docs/runs/SHORT_TRACK_SPEED_RUN.md exactonecommand all13; mainREADMElinkpendingexperiment.14adaptive tests passed including allsitecalreuse andunchangednight/ped/static/veto; Python3.9compile checked. ExtraAlomacandidateunreviewed, noforceaccept/claimaccuracy/speedguarantee;1.5minmetriccontinuity independent. Baseline3s results unchanged.


October26 weekly presentation created NEWcopy reports/presentations/bike_weekly_meeting_2026_10_26_speed.pptx,5slides, using latestOct20revieweddeck as visualreference only. Currentweekscope/method+formula+Mighkprovenance/twodata-table slides covering10sites/flow+durationfinding+pending1.5srun. Currentbaseline3s data includes Aloma recovery0accepted, notnewshortdayresults. Priorweek21persondetectorrankings omitted. Paper/authorcode citations inmethodnotes+visibleauthor/year; fullmetrics/timecoveragenotes. All5rendersvisuallyreviewed;fidelity0issues,XMLplaceholder/data checks passed. Originalpresentationunchanged. Scratchoutside repo /var/folders/7s/gt6p8xjd3hd_vxt2c2xv71d40000gs/T/codex-presentations/weekly-20261026/tmp includeseditablebuilder andQA.


October26 user authorized rerunHPGsamevideosasmanual. New adaptive_speed_batch.py match-manual selects only18submittedannotation clips across9cameras270nominalminutes, exactMP4sfrom MANUAL_BICYCLE_REVIEW_47586267. NoJSON9intervalsexcludedinclWestOrange; scoped notall27reviewclips. p.force_all_intervals preventsquotaearlystop; includesALLeligiblespeeds. ReusesfullsavedH/hull fromoriginalbatch; defaultdaymin1.5night/pedunchanged. Sourcecamera/clock/archive checked. Eachclipprobeenforcesdimensions; clippedColonial supports chunk_index_override1 in study_batch.build_plan andclockrealintervalstart. Cachedbaselineoriginalsunchanged. Matchedreportperinterval study/manual/automaticcounts+means to matched_intervals.csv; per-site snapshots maintained. docs/runs/MATCHED_MANUAL_SPEED_RUN.md command. PreparedonlynotHPGsubmitted. Localactualcoverage dryplan verified9/18/30people.25tests passed inclColonialcutclock/selection; additional workercoverageintegration check pending.

Matched-video implementation completed:26targeted tests pass, including mockedfullworker proving2selectedclipsareprocessed despitequota1, savedcalibrationreused, correctMANUAL_INTERVALS_COMPLETED_PROVISIONALstate andmatchedCSV. Actualannotationselectionvalidated9cameras18clips30encounters270nominalminutes. Clipdurationcheckedagainstoriginalsourceintervalto.25sec, dimensions+clockmustmatch. Newcommandmatch-manual in docs/runs/MATCHED_MANUAL_SPEED_RUN.md supersedes oldfullhourrerunplan; priorjobsnotcancelled orsubmittedlocally.


## October 26: verified video-hours correction
Only Colonial North has complete existing metadata (47.99 h). Other main manual report hours changed from file-count estimates to Unverified. Added audit_video_durations.py/.slurm: all 1,919 inventoried originals, 41 cameras, incremental resumable CSVs, temporary single-member ZIP extraction, CPU only. Not submitted: archive only on HPG. Eight duration/manual tests pass. See VIDEO_DURATION_README.md for command and download exp_results/VIDEO_DURATION_AUDIT after completion before updating exact totals.

## October 26: one-pass robust speed analysis implemented and run

Added code/speed_analysis_pass.py and .slurm, with four synthetic checks (known speed with irregular times, outlier robustness, scale multiplication, invalid time/horizon guards). Local execution on downloaded manual pack finished all 30 encounters: 29 usable, one Edgewater span<1.5s. All 18 review-clip packet PTS audits regular ~29.97fps; original hourly PTS not audited. manual/speed_analysis_20261026 contains comparison, 29 plots, per-encounter CSV, packet timestamps and sensitivity scenarios (3px SD, uniform±15% shared camera scale,500 draws,seed20261026). Defaults illustrative, not measured accuracy; study means never used to tune. Old manual and robust estimates same encounter sets; HPG column prior unmatched context. GPU same-manual-video batch separate and may still be running. User needs no new annotations or detector rerun for this analysis; optional one-command HPG reproduction in docs/runs/SPEED_ANALYSIS_ONE_PASS.md. Main manual report links new output without replacing prior results. No wheel/marking calibration claimed.

## October 27: completed hours and expanded speed plan

User pasted complete VIDEO_DURATION_AUDIT/by_camera.csv: 41 cameras/1919 measured originals, counts match previous inventory. Saved verbatim numbers in reports/cluster_returns/20261027/video_duration_audit/by_camera.csv; per-source completed export not local. Report generator now prefers this audit and manual/README.md + docs/VIDEO_DURATION_README.md show actual playback totals (Columbia47.98, Aloma47.99, PleasantHill30.01, WestOrangePath36.12). SilverStar remains unmapped. Other camera sides not pooled.

Added speed_plan.py/.slurm wrapping prior speed_analysis_pass plus scale checks, wheel-edge candidates and sampling-only group bootstrap comparisons. Synthetic tests cover vertical-wheel projection/radius, marking scale, insufficient sample/sign; combined12 tests pass. Full local run manual/speed_plan_20261027 completed30encounters,29usable,18timingclips,90wheelcandidateframes. Ellipses are unverified edge contours, not detected wheels. No real full3D projection/outline or marking evidence supplied: metric scale checks explicitly missing. Optional evidence functions genuinely fit3Dverticalcircle via projection+least_squares and comparegroundmarking lengths; never automatically rescale/fuse. ByteTrack already exists, no new tracker/keypointmodel/geolocation implemented. Latest command sbatch code/speed_plan.slurm supersedes older CPU analysis command. GPU manualmatch batch independent/pending returns. Guide docs/runs/SPEED_PLAN_RUN.md and source literature-plan status updated. No new user annotation required for default pass; no independent speed-accuracy claim.

## October 27 completed GPU returns

Owner says all sbatchfinished; pasted same-video and shortday reports preserved reports/cluster_returns/20261027/completed_speed_batches/user_report.txt. Parsed9samevideosites/18intervals/32selectedspeedtracks and13shortdaysites. Exact sameclips study35/manual30/auto32,9of18bin counts agree (not accuracy). Combined table with reference sample n, same-videoauto mean/n, manualmean/n and robustmanual mean in RESULTS.md/combined_comparison.csv. Keep previous manual baseline table historical; generator links latest report and removes pending wording for completed batches.

Carroll2auto intervals overlap2manual misses12:38:59/12:43:52 (identitynotconfirmed). Aloma5vs4 extra12:59:47 has no manualtimeoverlap. Columbia7vs4 includes .228,.088,.056mphlongtracks;12:27:20manual cyclist no selectedspeedtimeoverlap,12:34longtrack initiallyoverlaps manualperson thencontinues~116s. Edgewater6auto/manual6 but two selectedspeedtracks overlap single12:06manual and nooverlap12:32:25/12:46:11manual. Need fullID/type review; noautomaticfalsepositive/recallclaimsfromtiming. FullhourColonial41.67/WestOrange43.489mph review needed, no blanket deletion. Real annotatedpaths absent frompastedMD: ask cat exp_results/ADAPTIVE_SPEED_manualmatch_*/selected_candidates.csv for metadata before exactpathreview. No new broadbatch needed. docs/TODO.md updated currentpriorities. Root todo.md usernotes preserved.

## October 27 main manual README promoted to latest results

Owner explicitly requested updated manual/README.md. Main table now shows completed18sameclips/9sites1.5srun: study35/auto32/manual30; availablemeasuredhours, clips/nominalminutes, study/auto/manual counts, study/auto/manualmphwithspeedn and robustmanualmph all in one table. Older three-second broad-offeredbin README saved analysis/README_baseline_before_same_video_20261027.md (links adjusted), originalsite_summary.csv remains baseline for reproducibility; newanalysis/same_video_comparison.csv captures latest. Updated reportgenerator producescurrentREADMEwhenever completedcombinedcomparisonexists; no stalefiltered/pendingmainresulttext. Exacttime evidence links, methods, Aloma191/19/4/26explanation, all14locationdurations and unresolvedidentity/scalechecks retained. Verified9sites18clips35/32/30counts;5manualunitchecks pass; no rerun/newannotationsrequired. User originals untouched.

## October 27 owner visual feedback and additional locations

Owner reports Columbia many pedestrians asbicyclists, missedpassingcyclist, butatleastoneactualcyclistdetected. Edgewatercountinglookedquiteaccurate. Savedowner_video_review.md; do not treattemporaloverlapaloneasconfirmedduplicatesorEdgewatermisses. Noexhaustiveidentitylabels/times, nospeedaccuracyapproval, norawmeanschanged. manualREADMEandgeneratorupdatedwithfeedbackplusbroader-runmissinglocationtable: WestOrange/Park(aliasWestOrangePath)59.99min11candidates6speedusable5selectedmean26.12vsstudy10.77n25;43.489mphcandidatependingreview. Baxter5candidates/Daniels5/WinterPark2 all0speedusable, ~60mincompleted; noexactrejectioncausewithoutdiagnostics. These fourhave nosubmittedmanualclips, excludedfromsame-videomaincomparisonbutnotmissingjobs. SilverStarunmapped. NotaseparatelyconfirmedOrangeParkcitylocation. Rawreportsretained.

## October 27 missing-speed diagnostics requested

Owner asks currentsecondsandwhyBaxter/Daniels/WinterParknou­sablespeed. VerifieddayBIC1.5s, PED3s,nightfallback3s+existingstrictnightonly0.3sexception; detectionboxescanappearbeforecounteligibility. Metricestimatorseparate1.5scontinuoussupport, gaps<=.5s,>=5points/localwindow. Savedcounteligibility, boundarysafetyandmetriccontinuityallrequired. Newcode/diagnose_speed_rejections.py readsshortdaylatest(all_candidate_timestamps,rawtracks,rulesaudit,trajectories,pipelinetask), printscompactpertrackreasonsandcontinuity, savesmissing_speed_diagnostics.json. DefaultsitesBaxter/Daniels/WinterPark. NeeduseronHPGrunafterpushpullbecausecompletedrawfilesnotlocal; noGPU/sbatch/rerun/thresholdchange. Testedcontinuitygap/coasting exclusion;py3.9compilepassed. Do notclaimexactrejectionreasonfromaggregate0samples.

## October 27 exact missing-speed diagnostic return

Owner sofar.md diagnostic12candidates from shortday_20261026_095645 saved reports/cluster_returns/20261027/missing_speed_diagnostics/terminal_output.txt,candidates.json,RESULTS.md. ALL12longestobservedcontinuousspan<1.5s (Baxtermax1.3013,Daniels.9343,WinterPark.7341), provingcontinuityfailurebeforehull. ALL12counted0;11durationauditfail. Baxtertrack4w1 at12:24:17passesduration1.8observedframeequivalentbutlongestcontinuous1.1011s,gap1.001,net.4px; preciseothercountgateunknown. MostDanielsnearstationarynet.3–2.1pxand0detcyclistvotes (spuriousclassificationplausiblenotproven). Threebriefmovingcandidateclues:Baxter2019-09-18 12:25:34track8 secs.43det100span.5339;12:52:16track4 secs.37det100span.3337;WinterPark2019-09-25 12:10:32track1 secs.77det91.3span.7341. Needvisualidentity/typeandactualvisibilityspan;noglobalminloweringorrepeatfullhour. MainmanualREADME/generatornowgivesdefinitereasonsanddiagnosticlink. Countduration=sumobservedframes/fps, speedcontinuousframe-time span;coastedexcluded. Rootsofarleftunchanged.

## Owner candidate review: Baxter cars, Winter Park scooter

Owner reviewed Baxter2019-09-18 12:25:34/12:52:16 and saw cars,nobicycles. WinterPark2019-09-25 12:10:32–33 wasascooter(typeunspecified),notbicycle. Savedmissing_speed_diagnostics/owner_candidate_review.csv;updateddiagnosticreport/mainmanualREADMEandgenerator. These3candidatesalreadyexcluded; no count/meanschanged. No needlowerdurationthreshold orre-reviewsame3. Othertracks/fullhoursremainunverified; no claimnobicyclesentirehour. Scooterspeedoutsidecurrentbicyclist-onlyscopeunlessownerexpandsit.

## October 28 full MioVision ZIP scope correction

Owner clarifies camera/year request covers entireMioVision_Data.zip,notonlyBikeLaneStudy. Prior41camera1919videoinventory+measuredhoursare2019subsetonly. FullZIPnotlocal; existing docs/history/MioVision Pilot Dataset… describes annual2021–2026 collections, Other2020/2023 and2019BikeLaneStudy, but not freshlyverified per-camera data. Do notassertallarchive2019orwholearchivehoursmeasured.

Addedcode/inventory_miovision_archive.py stdlibcentral-directoryscan allvideotypes, groupssite/viewfolder+device, extractsactualfilename/sessionyears(categoryyearnotused), combinesexactsite/deviceacrossannualcollectionswithoutfuzzyphysical-siteassertions,flagsunknown, handles2019nestedfoldersandmultipart/newMIOP. Fourtests passandpy3.9compile. CLI directlyonHPG(noGPU/sbatch): python code/inventory_miovision_archive.py --update-readme /orange/xiangyan/rithika/vision/docs/VIDEO_DURATION_README.md. Outputs exp_results/MIOVISION_FULL_ARCHIVE_INVENTORY/{CAMERA_YEARS.md,camera_years.csv,per_video.csv,summary.json,RESULTS.md}. READMEpendingsection auto-replacedwithtable, existingmeasuredsubsethoursretained. Localdocs/VIDEO_DURATION_READMEcorrectedscopeandpendingfullinventorysection; awaituserpasteCAMERA_YEARS.md/returncamera_years.csvbeforeclaimcompletefullcamerayearslist. Usermustpush/pullnewcodefirst. Noarchiveextractiondurationprobingorspeedinferenceperformed.

## October 28 two requested inventory READMEs and complete ZIP hours

Owner explicitlyrequests twoREADMEscount/speedstudyvsentireMiovisionZIPwithperlocationhours,nvideos,actualyears. Createddocs/BIKE_LANE_STUDY_INVENTORY_README.md(completed41studyworkbook/cameralabelswith2019years,nfiles,measuredhours;14Mighkhandtimedspeedlocationswithn/meansandcandidatevideocoverage). docs/MIOVISION_ARCHIVE_INVENTORY_README.mdcurrentlypendingactualfullZIPdata;docs/VIDEO_DURATION_README.mdnowanindexbetweenthetwo. Noallarchive2019or41camerasclaim.

Addedbuild_video_inventory_readmes.py andprepare_full_archive_inventory.py +full_archive_inventory.slurm. QuickdirectCLI --inventory-onlyscanswholecentraldirnoextraction,updatesbothHPGREADMEsandfullcamera/year/nfiletable. CPU24hjobaddsdurationmetadataallvideos,reusesmeasuredper-source2019VIDEO_DURATION_AUDIT/per_source.csvbyexactarchivepath,probesalreadyextractedfilesorextractsonetemporarymemberthenremovesit; noGPU/detectionorpermanentfullextraction. Repeatedsubmissionsresume. Metadataoperationscans report/exportfilenamesonlypossible_report_exports.csv(nativeMiovisionspeedsnotconfirmed). fulloutfixedexp_results/MIOVISION_FULL_ARCHIVE_INVENTORY;incrementaldurationsCSV/RESULTS;camera_years_hours.csvcompactcombinedoutputforuserpaste afterfinish(toupdatelocalREADME). JobwritesHPGREADMEaftercompletion; --inventory-onlyrefreshespartialdocswithoutreprobing. Readgroupingrules:sitefolder/deviceidentitynotphysicaladdresses;annualcollectionsmergeonlyexactsamefolder/device;filename/sessionyearsoutrankcategoryyear.Unknownyear/hoursneverassumed.

Modifiedaudit_video_durations.main(argv=None)forreuseandclosedCSVhandles.Tests8passincludingfakeZIP2019+2021under2022category,reuseoneoldmeasuredfile,onlynewfileprobed,actual.5/.25hours,nonvideoexportslisting,resumeretention. FullZIPnotlocal;realjobnotrun/submitted. Usermustpushpullthenpythoncode/prepare_full_archive_inventory.py --inventory-only;sbatchcode/full_archive_inventory.slurm;afterfinishcatcamera_years_hours.csv. No existingvideodataaltered.

## October28 full ZIP camera/year return, hours job submitted

Owner submittedfull_archive_inventory.slurm; didpreviousquickPythoninventory andpastedCAMERA_YEARS.md in sofar.md. Parsedandpreservedreports/cluster_returns/20261028/full_archive_inventory/{owner_camera_years_output.txt,camera_years.csv,summary_from_owner.json,PROVENANCE.md}. Actual9085videos,179site/view/devicegroups,years2019through2026,no unknowndates. Annual6648videos135groups;BikeLaneStudy2279videos39groups;Other158videos5groups. IMPORTANT1919mappedcountstudyfiles/41semanticlabelsareonlysubsetof2279BikeLaneStudyarchivefiles;rawsite/devicegroupsmerge recording sessions,notphysicalcameracount. UpdatedfullREADMEwithall179groups/year/filecounts,hourspending. FirstREADME remainsmapped41+14refs;scopeclarified. Defaultreadmebuildernowpreserveslatestreturnedfullinventorywhenregeneratedlocally.

Ownerasksnewbatchchecksallfiles/speedexports: currentprepare_full_archive_inventoryreadswholecentraldir, inventoriesallvideoextensionsandlistsselectednonvideoCSV/XLS/XLSX/JSON/XML/TXT/PDFfilenames/sizesinpossible_report_exports.csvwithspeed/velocity/calibrat/setupPATHkeywordflag. DoesNOTparsecontents/provenanceorconfirmnativeMiovisioncyclistspeeds,norlistallotherfiletypes(e.g.CUT). Askcatpossible_report_exports.csv(alreadygeneratedbeforelongdurationphase)and/orsummary.json. Do notclaimfullcontentinspectionornativespeedabsence. No needcancel/resubmitrunningdurationjob. Fullhoursnotreturnedyet.

## October28 Word conversion requested

Createdreports/documents/VIDEO_DURATION_README_2026_10_28.docx asself-containedconversionofdurationindex+bothinventoryREADMEs. OriginalMDspreserved.17pages,portraitstudy41rows+14speedlocations,landscapefullarchive179groupssplitbycollection(135annual39study5other),pendinghoursnotinvented. Verified9085fullarchivevideocountsum. UsedDocumentsskillcompact_reference_guide withlandscapewide-tableoverride,exactDXAtablegeometry/repeatedheaders,nosplitrows;bundledruntimePython/docx+bundledLibreOfficerender. All17finalpagePNGsvisuallyinspectedcleantables/nooverflow. Scratchbuilder/renders /tmp/video_duration_word_GrSVEQ; finaldeliverableonlyDOCX. Includescurrentfullhourspendingstatus,notnewdurationreturn. NativeMiovisionspeedfilecontentsstillawaituser4txtoutput.

## October28 corrected Word scope: Counts folder only

Owner rejectsfullZIPcombinedWord; wants onlyBikeLaneStudyCountscameras withspeedreferenceavailabilityandyears. CreatedNEWreports/documents/BIKE_LANE_STUDY_COUNTS_CAMERA_INVENTORY_2026_10_28.docx,3pages,one41rowtable:camera/year/video count/measuredhours/speedreference location+facility. All2019. Candidate vs same-street-only vs no-reference distinctions avoidclaimingexactcamera/personvalidation. SpeedrefsMighkhumanhalf-speedtiming,notconfirmednativeMiovision. ExcludesSilverStarascamera(noindividualcountworkbook),full179archivegroupsnotincluded. VerifiedlocalCounts folder41xls plus2convertedxlsxduplicateexistingPineHilsNBLE/SOrangeNB labels(confirmXMLsharedStrings),summaryworkbooksnotextracameras. DOCX41rows1919videototalchecked;all3finalPNGpagesvisuallyreviewed. OldercombinedWordleftunchanged. Scratchstudy_only.pyandrendersunder/tmp/video_duration_word_GrSVEQ. FinaldeliveronlynewDOCX.

## October28 Aloma two one-minute views requested

Owner wants two~1minvideoscompareAlomaPathvsSidewalk. Sourceinventoryconfirmsdifferentmembers/devices; noon.013 PathSCU8PM vsAlomaSWSCU8OG. OnlyPathclipslocal,Sidewalk/fullZIPonHPGnotdirectlyaccessible. Addedcode/aloma_view_comparison.py/.slurm:CPU2threads30minjob,exact2sources,cuts210–270secfromfilename-inferred12noonOct30,2019 =>12:03:30–12:04:30;nooverlay/inference. Usesexistingextractedoriginalorone-temporaryhourlymemberthenremoves,originalsunchanged. Outexp_results/ALOMA_VIEW_COMPARISON_JOBID/{aloma_path_2019-10-30_120330-120430.mp4,aloma_sidewalk_2019-10-30_120330-120430.mp4,index.html,JPGs,sources.json,README.md}. Browserpageletsownercompareboth;notindependentsynchronizationproof. Preparedonly,notrunorHPGsubmitted. Python3.9syntax/shellsyntax/source-selectionchecked. Needpushpullthen sbatch code/aloma_view_comparison.slurm;ownerdownloadjustthatoutputfolderviaOnDemand. No claimthatdifferentdevicesruleoutduplicatedviews.

## October28 full ZIP duration audit COMPLETE

Owner sofar.md containsfull179rowcamera_years_hours.csv andreport9085/9085files179/179groupsCOMPLETE. Savedverbatimcompleted_duration_terminal_output.txt andparsedcamera_years_hours.csv/durations/by_camera.csv underreports/cluster_returns/20261028/full_archive_inventory. Exactkeys,recordingyearsandvideocountsmatchpreviousfullscan;allpositivefinitehoursandallmeasuredcountschecked. Aggregate9057.33588141playbackhours (9057.34),Annual6648files6625.199047h135groups;BikeLane2279files2274.183900h39groups;Other158files157.952934h5groups. Theseareview/devicegroupsandplaybackhoursnotphysicalsites,nondeduplicatedcontentorcontinuouscoverage.

BuildernowwritesallactualhoursintoMIOVISION_ARCHIVE_INVENTORY_README.md, marksCOMPLETE/removesnewsubmissionsinstructions, addscompletionstatusVIDEO_DURATION_READMEindex. Keepsstudy41cameracountfolder/1919filesseparatelyandstudy-onlyWordunchanged(scopeandhoursalreadyvalid). completed_totals.json+updatedPROVENANCE.md retained. No needrepeatjob. StillawaitAlomaone-minuteclipsandnative4mac.txtcontents;hourauditdoesnotconfirmMiovisionspeedexports.

## October28 inventory glossary/device/file-content clarification

OwnerasksSCU8OGvsSCU8PM,10thStrepeated45vs48,quality,times,annualvsOther,nativeexports. UpdatedfullREADMEbuilderwithglossary:identifiersfromsessionnamesnotverifiedmodels/quality/directions/AMPM;officialMiovisionScoutchecklistdocumentsSCU IDs,butexactequipmentunknown.10thSt2023twoIDs45/44.75367hvs48/47.98278h(~3.23hdifference),noprovenangle/synchronization/missingvshortdeploymentcausewithoutsessionlistframes. Annual=2021Data–2026Datafoldergroupingnotyearlong;OtheractualSunRail/Longwood2020/2023. Existingselectednonvideoextensionlisting4mac.txt1350bytes,noconventionalCSVExcelJSONXMLPDFentriesreturned;contentsstillawaiting,proprietaryCUT/JPG/nestedarchivesnotcontentaudited. SavedownerCSVreports/cluster_returns/20261028/archive_report_files/ withprovenance. NoMiovisionnativespeedresultconfirmed;notclaimZIPvideosonly.

Addedarchive_contents_summary.py stdlibread-onlywholeZIPallentrytypecounts+all_files.csv,10thStsessions/date/pathsummary andalltxt<=8KiBcontents;noextraction/GPU/sbatchorhourrerun. Usercanrunafterpushpullandpasteterminalsummarytoresolveexactdatesand4textcontents. Fullarchive/firstinventoryREADMEsregenerated,originalscopesretained. Officialsourcehttps://miovision.com/wp-content/uploads/2024/01/miovision_scout_tune-up_checklist_EN_2022.pdf verifiedweb;donotassumeScoutPlusresolutionsforSCU8OG/PM.


## Repository cleanup — October 28, 2026

Owner requested removal of unnecessary files. Deleted five byte-identical redundant input/review copies, keeping canonical metadata, zones and review sheet; removed obsolete full-archive Word export (the requested study-only Word inventory remains), OS metadata and Python caches. Earlier presentation originals moved unchanged into reports/presentations/history/. Research note moved into docs/research/. Root README now provides current report navigation; prior root README retained under docs/history/README_before_cleanup_20261028.md. Manifest docs/REPO_CLEANUP_20261028.csv. Manual annotations, workbooks, experiment outputs, code and HiperGator paths preserved. No remote changes/jobs or commits performed.


## Thorough documentation cleanup — October 29, 2026

Owner explicitly requested deletion of do.md/look.md and more thorough cleanup. Removed 48 obsolete files: docs/tasks chat/task notes, stale progress/next-step/terminal-output files and README snapshots, archived superseded code/launchers/diagnostic logs, obsolete missing-target slurm/run_pilot_detect.slurm and redundant cleanup CSVs. Preserved unresolved identity/lane checks in docs/TODO.md. Five reproduction guides moved to docs/runs with corrected links/status banners; generated links in analyze_manual_bicycles.py updated. Combined maintenance records in reports/maintenance/cleanup_log.csv. Original annotation/data/result inputs preserved. Checked current navigation links, updated Python syntax and git diff whitespace. No jobs, commits or remote mutation.


<a id="note-2"></a>
## METHODOLOGY.md
Original location: `docs/history/METHODOLOGY.md`.

# Methodology Guide — Archival Cyclist Vision Study

Working plan for turning ~40 sessions of 2019 MioVision footage + hand-collected
ground truth into a publishable paper. Written 2026-09-17.

---

## 0. What you actually have (the asset)

State this plainly in the paper, because it is the moat:

- **202 rows of independent, human-collected cyclist counts** — **5,053
  cyclists** across **41 site-sessions** — disaggregated by **facility type**,
  **direction**, and **movement** (With / Facing traffic).
- **Hand-timed speed distributions by facility type** (Travel Lane 14.5 mean /
  18.4 p85, Bike Lane 11.8 / 15.7, Sidewalk 9.3 / 12.4).
- **A day/night exposure-risk model** already computed per corridor.
- **The matching raw video** — 41/41 site-sessions joined to video folders
  (`video_site_mapping.csv`), zero orphans on either side.

### 0.1 It is a matched-pair natural experiment, not a convenience sample

The date join (`build_site_mapping.py`) revealed the study's design, which
nothing in the project documentation had recorded:

> **Every recording date deployed exactly TWO cameras simultaneously — one at a
> BL (bike lane) site, one at an NBL (no bike lane) control site.**

```
2019-05-22   BL Livingston  n=170   +   NBL Summerlin      n=169
2019-06-26   BL Glenridge   n=151   +   NBL Kaley          n=36
2019-08-07   BL Edgewater   n=228   +   NBL N Orange       n=130
2019-09-10   BL Columbia    n=243   +   NBL Carroll        n=31
```

with the same structure for path/sidewalk pairs (Aloma Path + Aloma SW,
Rinehart Path + Rinehart SW, Daniels, WORT) and the speed sub-study
(SW Speed University + TL Speed Winter Park; BL Speed Edgewater + TL Speed
Baxter). The folder prefixes decode as `BL` = bike lane, `NBL` = no bike lane,
`SW` = sidewalk, `TL` = travel lane.

This also answers the question left open in the earlier session notes — *"which
files are genuine two-camera-same-session pairs vs. count+later-speed-redo
pairs."* **They are same-session treatment/control pairs.**

**Why this is worth a great deal:** because each pair is recorded on the *same
day*, weather, season, day-of-week and time-of-year are controlled **by
construction**. You are not comparing bike-lane sites to control sites across a
noisy observational sample — you have 17 matched pairs. That supports causal
language most observational cycling-safety papers cannot use, and it is the
strongest single fact about this dataset. Lead with it.

### 0.2 Headline finding, previously locked in an unusable column

`facility_type` and `movement` were declared in the ground-truth CSV and
documented as populated, but were **empty in 202 of 202 rows**. Both are
recoverable from `channel_label` (`fix_ground_truth.py`, cross-checked against
all three hand-verified site totals). Once filled:

| Facility | Cyclists | Share |
|---|---|---|
| **Sidewalk** | **3,160** | **63%** |
| Bike lane | 1,125 | 22% |
| Path | 531 | 11% |
| Travel lane | 237 | 5% |

**Nearly two thirds of observed cyclists ride on the sidewalk**, roughly 3× the
bike-lane share. Individual sites are starker still — Pine Hils NBL E is 311
sidewalk vs 6 travel lane. That is a substantive transportation finding on its
own, and it has direct methodological consequences: any pipeline that assumes
cyclists appear in the bike lane will miss most of them, and ROI-cropping to the
bike lane would discard 78% of the data.

Almost every cyclist-detection paper validates against a few hundred hand-drawn
boxes on frames the authors labeled themselves. You have *independent*,
*facility-resolved*, *multi-site*, *paired-design* ground truth collected by
people who had never heard of your model. That is a stronger validation protocol
than the field's norm, and it is the thing to build the contribution around —
not the detector.

**Corollary:** do not frame this as "we detect cyclists with YOLO." That is
unpublishable in 2026. Frame it as a *measurement instrument* paper.

### 0.3 Known gap: no time-of-day resolution

`parse_raw_counts.py` locates each sheet's **total row** and discards the
15-minute interval rows beneath it. So the ground truth is currently *daily
totals per channel*, not a time series.

This blocks two things: per-interval count validation (Tier 1's stated gate),
and ground-truth-guided frame mining (§3.2), which needs to know *which
15-minute windows* contain cyclists. The interval data exists in the raw `.xls`
files and in `Bike lane study counts.xlsx` — it simply was not carried through.
**Re-extracting it is a P0 task** (§1.4).

---

## 1. Immediate engineering tasks (P0 — nothing else matters until these clear)

### 1.1 The zero-tracked-bicycles bug — SOLVED

**Root cause: `TRACK_IOU_MATCH_THRESH = 0.3` in `SimpleIouTracker`.**

Diagnosed directly from the boxes logged in `pilot_detect_41807016.log`, not by
hypothesis. Ruled out first:

- **Detection is fine.** The cyclist at t≈407–409 s is detected in every frame.
- **Frame stride is fine.** At 30 fps with `TRACK_EVERY_N_FRAMES=5`, the cyclist
  lands in **13 sampled frames**, against `min_track_hits = 6`.
- **Confidence threshold is fine.** All 13 sampled frames exceed `conf=0.2`
  (0.28, 0.34, 0.77, 0.92, 0.38, 0.76, 0.77, 0.47, 0.62, 0.49, 0.33, 0.36, 0.54).

What actually fails is association between those 13 frames. Measured IoU on
each of the 12 consecutive links:

| link | IoU | ≥0.3? | ‖Δcentroid‖ / diag | ≤1.0? |
|---|---|---|---|---|
| 407.40→407.57 | 0.259 | ✗ | 0.33 | ✓ |
| 407.57→407.74 | 0.000 | ✗ | 0.95 | ✓ |
| 407.74→407.90 | 0.287 | ✗ | 0.08 | ✓ |
| 407.90→408.07 | 0.233 | ✗ | 0.39 | ✓ |
| 408.07→408.24 | 0.270 | ✗ | 0.36 | ✓ |
| 408.24→408.41 | 0.311 | ✓ | 0.32 | ✓ |
| 408.41→408.57 | 0.230 | ✗ | 0.38 | ✓ |
| 408.57→408.74 | 0.238 | ✗ | 0.29 | ✓ |
| 408.74→408.91 | 0.361 | ✓ | 0.28 | ✓ |
| 408.91→409.07 | 0.274 | ✗ | 0.34 | ✓ |
| 409.07→409.24 | 0.287 | ✗ | 0.33 | ✓ |
| 409.24→409.41 | 0.355 | ✓ | 0.28 | ✓ |

**IoU@0.3 passes 3/12.** The track shatters into fragments of length
`[1,1,1,1,1,2,1,2,1,2]` — longest = **2 hits**, against a requirement of 6. Zero
counted. **Size-normalized centroid distance passes 12/12** → one clean 13-hit
track.

Mean IoU is 0.28, sitting *just* below the 0.3 gate — which is why this
produced a clean zero rather than erratic undercounting.

**Two compounding causes, both specific to small VRUs:**

1. Displacement per sample is large relative to box size. IoU collapses once
   the shift approaches the box dimension, and for a ~40 px cyclist at a
   5-frame stride it does.
2. **Box geometry is unstable.** The detector alternates between boxing the
   bicycle alone and the bicycle+rider; height swings 114→62→50 px across three
   samples. IoU punishes that even when the object barely moved — see
   407.74→407.90, where the centroid moves 6.7 px yet IoU is only 0.287.

Cars are immune to both (large, stable boxes), which is exactly why the same
clip tracked 85 cars and 0 bicycles. **The asymmetry was the clue.**

**This is a publishable finding, not just a bug.** "IoU association silently
zeroes out the rare class while appearing to work on the common class" is a
failure mode that transportation-CV papers using off-the-shelf trackers are
likely hitting without knowing. See Idea E in §4.

### 1.2 What was changed (code in this repo)

| File | What it does |
|---|---|
| `vru_tracker.py` | Velocity-predicted, size-normalized centroid association. IoU demoted to a tie-breaker in the cost, never a rejection gate. |
| `pilot_detect_v2.py` | Rewritten pipeline: track-before-detect, per-track motion filtering, funnel CSV, real annotated video. |
| `tracker_ablation.py` | Runs identical detections through old and new association. The paper's ablation table. |

Three further changes, each independently defensible:

**Track-before-detect.** Detection now runs at `conf=0.05` and the accept/reject
decision moves to *track* level (max confidence across the track). Per-frame
thresholding is the wrong place to threshold rare small objects — in the logged
window, per-frame confidence dips to 0.07 and 0.09 mid-track on a cyclist that
peaks at 0.92. Thresholding per frame discards exactly the marginal evidence
that tracking exists to accumulate.

**Motion filtering moved from per-detection to per-track.** The old
`MOTION_OVERLAP_THRESH=0.15` MOG2 check could delete a real cyclist whenever the
foreground mask was poor on one frame, and could not be loosened without
readmitting static false positives. Judging at track level is strictly better:
one decision with all the evidence. The metric is **max excursion from origin**,
in box diagonals — *not* total path length, because a static object's per-frame
jitter accumulates path length linearly with duration (a 60-frame static box
jittering ±1.5 px accumulates 2.79 diagonals of "path" and would pass any fixed
threshold given enough time). Max excursion stays flat at 0.09 for that same
track. This is verified by a unit test.

**Per-class persistence.** `MIN_TRACK_SECONDS` was 1.0 s for everything, tuned
on cars. A cyclist crosses the frame in ~2 s; a car waits at a light for 30 s.
Now `{bicycle: 0.5, person: 0.5, _default: 1.0}`.

### 1.3 Funnel logging (now built in)

`pilot_detect_v2.py` writes a per-frame CSV:

```
t_sec, frame_idx, n_raw_tile_dets, n_after_merge, n_in_roi,
n_matched, n_new_tracks, n_active_tracks, n_bicycle_dets, best_bicycle_conf
```

plus a per-track CSV with each track's hits, duration, max/mean confidence, net
displacement, max excursion, and whether it was counted. "Where does recall
leak" is now answerable from data. This is also the ablation table for the paper.

### 1.3 Stop chasing the YOLO26-vs-v8 car/truck discrepancy

`yolo26l` reporting car 13 vs `yolov8l` car 85 at the same `conf=0.2` is **not a
bug and not a calibration defect worth investigating.** YOLO26 is *NMS-free*: it
uses one-to-one label assignment, so it emits one box per object instead of a
cloud of near-duplicates that NMS later collapses. Its confidence scores live on
a different scale entirely. Comparing the two at a shared threshold is invalid.
If you want a real comparison, sweep the threshold and compare
**precision–recall curves / mAP**, never raw counts at a fixed `conf`. Drop this
thread; it costs you nothing to close.

---

## 2. Model choice: YOLOv8 vs YOLO26

**Short answer: use YOLO26-L as the primary, keep YOLOv8-L as the baseline row
in an ablation table. But this decision matters far less than fine-tuning.**

Reasoning:

| Factor | Verdict |
|---|---|
| Small objects | YOLO26 adds ProgLoss + STAL (Small-Target-Aware Label assignment), targeted at exactly your regime (30-px cyclists in a wide intersection view). Real gains reported on VisDrone-class data. |
| NMS-free | Removes one entire class of tile-merge pathology from your pipeline. You still need cross-tile dedup, but intra-tile duplicate suppression stops being a tunable you can get wrong. |
| Ecosystem / baselines | YOLOv8 has vastly more published transportation baselines. Reviewers know it. This is why it stays as the baseline row, not the primary. |
| Reviewer optics | "We used the newest model" is worth nothing. "We report v8-L / v11-L / 26-L under identical sliced fine-tuning and held-out-site evaluation" is worth a table. |

Do **not** spend weeks on model selection. Once you fine-tune on your own
domain, the architecture delta shrinks to a couple of mAP points, while the
fine-tuning delta is 20–40 points. Run the comparison *once*, as an ablation,
after the pipeline works.

---

## 3. Fine-tuning: yes, definitely — and not the way you were thinking

### 3.1 Why fine-tuning is non-optional here

1. **COCO's `bicycle` class is the wrong concept.** It is trained largely on
   ground-level, close-range, often *parked* bicycles. You need *cyclists*:
   small, overhead-oblique, motion-blurred, JPEG-compressed 2019 traffic-camera
   objects.
2. **COCO splits `person` and `bicycle` into two classes.** Your ground truth
   counts *cyclists*, a single rigid person+bike unit. Every downstream count
   requires you to fuse two COCO classes with a heuristic. Define a single
   `cyclist` class instead and the fusion heuristic — and its error mode —
   disappears from your pipeline.
3. **Your own evidence already shows the gap**: a cyclist at conf 0.84 in one
   frame and absent in the next is classic domain mismatch, not model capacity.

Recommended class set: `cyclist`, `pedestrian`, `car`, `truck/bus`,
`motorcycle`. Five classes. Resist adding more.

### 3.2 Don't hand-label from scratch. The modern loop:

**Step 1 — Ground-truth-guided mining (this is your unfair advantage).**
Your interval counts tell you *which 15-minute windows at which sites contain
how many cyclists*. That is a targeted search space. Instead of sampling frames
uniformly across 500+ hours of footage — where >99.99% of frames contain no
cyclist — mine only inside windows where ground truth says cyclists exist.
Estimated efficiency gain: 2–3 orders of magnitude of annotator time.
Worth writing up as a method subsection in its own right.

**Step 2 — Model-assisted pre-labels, not blank canvases.**
Run an open-vocabulary detector over mined frames with a text prompt
(`"a person riding a bicycle"`): GroundingDINO, OWLv2, YOLO-World, or
Grounded-SAM-2. These produce candidate boxes zero-shot. Humans then *verify and
correct*, which is roughly 5–10× faster than drawing. Ultralytics ships
`auto_annotate` for this.

**Step 3 — Exploit video, don't treat frames as independent.**
Label one frame per track and **interpolate boxes across the track**. CVAT does
this natively and it is the single biggest annotation multiplier available to
you — a 60-frame track costs 2 keyframes, not 60 boxes.

**Step 4 — Sliced fine-tuning (SAHI-style). Probably fixes part of your bug.**
Your pipeline **tiles at inference** but you are running a model **trained on
full frames**. That is a train/inference distribution mismatch: the model has
never seen a cyclist at the apparent scale a tile presents. The SAHI paper
reports +6.8/5.1/5.3 AP from sliced inference alone, rising to +12.7/13.4/14.5
AP *cumulative* when you also fine-tune on slices. Generate your training set as
**slices matching your inference tile geometry exactly** (same tile size, same
overlap). This is cheap and it is very likely worth more than any architecture
choice on this list.

**Step 5 — Active learning, 2–3 rounds.**
Round N: run the fine-tuned model over held-out sites → mine (a) low-confidence
detections, (b) **count-disagreement windows** where your tracked count differs
most from the hand count → label those → retrain. Stop when the count error on a
validation site stops improving. Two or three rounds is usually where the curve
flattens.

### 3.3 Tooling — what to use instead of "Roboflow or something"

Roboflow is a perfectly good *annotation UI and dataset host*, and if you're
already comfortable there, keep it. But it is not a curation engine, and
curation is your actual bottleneck at this scale.

| Job | Tool |
|---|---|
| Curation / mining / "which of my 500k frames should I label?" | **FiftyOne (Voxel51)** — built for exactly this: embeddings, uniqueness sampling, mistakenness ranking, side-by-side model-vs-GT views. This is the tool for "the dataset is huge and I'm lost." |
| Video annotation with track interpolation | **CVAT** (free, self-hostable on HiPerGator) |
| Hosted annotation + versioning + easy YOLO export | **Roboflow** (fine, keep it) |
| Sliced training/inference | **SAHI** (`obss/sahi`) |
| Experiment tracking | **Weights & Biases** or MLflow — you will run dozens of configs; do not track them in filenames |

### 3.4 Splits — the thing reviewers will attack

**Split by SITE, never by frame, and never randomly.**

Adjacent video frames are near-identical. A random frame split leaks the test set
into training and inflates mAP by a huge margin. It is the single most common
fatal flaw in transportation-CV papers and a competent reviewer looks for it
first.

Proposed protocol:

- **Train:** ~10 sites
- **Val (tuning):** 3 sites
- **Test (touch once, at the end):** 3 sites, chosen to span all facility types
  and including at least one night-heavy and one path site.
- Report **held-out-site** performance as the headline number. Report
  random-split numbers only if you want to *demonstrate* the inflation — which
  is itself a nice half-page contribution.

---

## 4. The research contribution — four candidate ideas

You need algorithmic significance, not a pipeline report. These are ranked by
how defensible the novelty claim is. **A and B together make a strong paper; C is
the highest-risk/highest-reward.**

### Idea A — Distribution-matching self-calibration from speed priors ★ strongest

**Problem.** Speed estimation from a monocular fixed camera needs a homography.
Standard practice requires manual reference points measured in the field. Your
footage is from **2019**; the cameras are gone, the sites have changed. You
physically cannot go measure. Existing auto-calibration methods rely on vanishing
points from lane markings or known vehicle dimensions — both fragile on
sidewalk/path cameras with no lane markings at all.

**The idea.** You have the hand-timed cyclist speed distribution per facility
type. Solve for the homography scale by **matching distributions**: find the
calibration parameters under which the observed *pixel* speed distribution of
tracked cyclists maps onto the known *MPH* distribution for that facility type.
No reference points, no site visit, no lane markings. The ground truth becomes
the calibration target rather than only the evaluation target.

**Why it's novel.** Auto-calibration literature uses geometric cues (vanishing
points, GNN homography estimation, known object sizes). Using a *behavioral prior
distribution* of the target class itself as the calibration signal is, as far as
the searches above surface, not established. And it generalizes far beyond
cycling — any archival traffic video with historical speed studies.

**Why it's tractable.** One scalar per camera in the simplest form. Validate by
holding out sites: calibrate on Site A's distribution, predict Site B's mean and
p85 speeds, compare to hand-timed truth.

**Risk.** Confounded if the speed distribution genuinely differs by site (it
does, somewhat). Mitigation: hierarchical model with a per-site random effect,
and report sensitivity.

### Idea B — Count-supervised calibration ("counts as labels") ★ strongest pairing

**Problem.** Your supervision is *aggregate* (15-min interval counts), not
per-frame boxes. The field's default response is to go label boxes.

**The idea.** Treat the interval counts as the *direct* training/calibration
signal. Learn the tracking hyperparameters — confidence threshold,
`min_track_hits`, motion gate, dedup IoU, line-crossing logic — by minimizing
count error against the hand counts, rather than hand-tuning them (which is what
you are doing now, and which produced the current bug). Formulate as a
calibration objective over interval counts, optimized with a derivative-free
method or a Bayesian/differentiable surrogate.

**Why this matters beyond your project.** Transportation agencies hold *decades*
of hand-collected interval count sheets sitting next to archival video. If those
count sheets can supervise a vision pipeline directly, an enormous latent
training corpus becomes usable without a single new bounding box. That framing
sells the paper to a transportation venue immediately.

**Bonus.** It makes the current bug part of the story: hand-tuned thresholds
catastrophically failed (zero cyclists at `min_track_hits=6`) while
count-supervised calibration recovers them. Your failure becomes Figure 1.

### Idea C — Unsupervised facility-zone induction

**Problem.** Assigning each cyclist to bike lane / sidewalk / travel lane
currently requires hand-drawn ROI polygons per camera. That does not scale to
16 sites × 40 sessions, and it is the hidden manual cost in every paper that
claims automated facility analysis.

**The idea.** Induce the facility polygons from the traffic itself. Accumulate
every trajectory (all classes) over hours; cluster in a feature space of
(lateral position, heading, speed, class mixture). The clusters *are* the
facilities: car-dominant + fast = travel lane; pedestrian-dominant + slow +
narrow = sidewalk; intermediate speed + bike-dominant + between the other two =
bike lane. Zero manual ROIs, and it self-adapts to camera moves between sessions.

**Validation — and this is the strong part.** Your ground truth is
facility-disaggregated. You can validate induced zones against hand-labeled
channel counts per facility, at 16 sites. Essentially nobody has facility-level
count ground truth to validate an unsupervised segmentation against. You do.

**Risk.** Sidewalk-vs-bike-lane separation may be weak where cyclists ride on the
sidewalk (which is precisely the behavior the study is about — your Sidewalk
counts dwarf Bike Lane counts at several sites). Handle it: that ambiguity is a
*finding*, not a failure. "Facility geometry is not recoverable from cyclist
behavior alone because cyclists systematically use the wrong facility" is a
publishable sentence.

### Idea D — Rare-event cascade (efficiency contribution)

Cyclists are ~0.001% of frames. Running a large tiled detector on all of it is
absurd. Propose a cascade: cheap background-subtraction/motion proposals →
tiled detector only on candidate regions → track. Report the compute reduction
and the recall cost. This is the least novel of the four, but it is the easiest
to demonstrate rigorously and it makes the full-dataset run actually feasible on
your Slurm allocation. Good as a secondary contribution or a systems section.

### Idea E — Rare-class association failure in multi-object tracking ★ new, and you have the data

**Discovered in your own pipeline (§1.1).** IoU-based association — the default
in the trackers most transportation-CV papers use off the shelf — fails
systematically for small vulnerable road users, while continuing to work on
vehicles in the same frames. On the BL Colonial clip it passed 3/12 links for a
cyclist and produced **zero** counted cyclists against 85 counted cars.

**Why it's a contribution, not just a bug report.** The failure is *silent and
class-selective*. A pipeline reporting plausible vehicle counts looks healthy;
nothing in its output reveals that the rare class has been zeroed. Any study
that reports cyclist counts from an IoU-associated tracker without per-class
validation may be under-reporting by an unknown factor. You can quantify that:
sweep the IoU threshold and show counted-cyclist yield vs. counted-car yield
diverging, then show the centroid formulation closing the gap. Two mechanisms
to separate and measure independently:

1. displacement-to-box-size ratio (scales with frame stride — sweep it), and
2. **box aspect instability**, which is the more interesting one: a
   bicycle/rider box flips between two valid interpretations frame to frame, so
   IoU drops even at near-zero displacement (your 407.74→407.90 link: 6.7 px of
   motion, IoU 0.287).

Mechanism 2 is not a tuning problem — no IoU threshold fixes it, because
lowering the gate enough to catch it admits false associations everywhere else.
That argues the metric itself is wrong for this class, which is a real claim.

**Validation.** Your facility-disaggregated hand counts let you measure the
resulting count error per class, per site — which is precisely the evidence a
reviewer would demand and almost nobody can supply.

### Suggested paper framing

> **Auditing cycling infrastructure from archival traffic video with
> count-supervised, self-calibrating vision.**
> Contributions: (1) count-level weak supervision for calibrating a
> detection–tracking pipeline, eliminating per-frame annotation;
> (2) distribution-matching self-calibration for speed estimation on cameras
> that no longer exist; (3) validation against 203 independent hand-collected,
> facility-disaggregated observations across 16 sites — a stronger protocol than
> the field's norm; (4) findings on sidewalk riding and day/night exposure risk.

---

## 5. Phased execution plan

Do not touch the full dataset. Work in tiers; each tier has a gate.

**Tier 0 — One clip, fully understood.** (target: days)
BL Colonial .008, the clip you already know. Gate: the pipeline tracks the
t≈408 s cyclist, and the reject-reason CSV explains every frame where it
doesn't. Nothing proceeds until this gate clears.

**Tier 1 — One session, count-validated.** (target: 1–2 weeks)
One full site-day against its hand counts, at 15-min resolution. Gate: count
error and a per-interval scatter plot vs. ground truth. Expect this to be bad
at first; that is the calibration signal for Idea B.

**Tier 2 — Three sites spanning facility types.** (target: 3–4 weeks)
Pick one bike-lane-heavy (Edgewater: BL With 146), one sidewalk-dominant
(Pine Hils NBL E: SW 168/143, almost no travel lane), one path
(Lakemont Pathway). Gate: fine-tuned model beats COCO baseline on held-out
sites; calibration transfers across sites.

**Tier 3 — All 16 sites.** Only after Tier 2's numbers are stable. This is the
paper's results table.

**Tier 4 — Goals 3–5.** Speed (Idea A), then near-miss, then demographics.

**On Goal 5 (age/gender):** think hard before including it. No ground truth
exists in your data for it, inferring demographics from surveillance video is an
ethics-review magnet, and it will attract reviewer hostility disproportionate to
what it adds. Recommendation: cut it, or reduce it to a short limitations
discussion of *why* it was cut. That is itself a defensible and increasingly
well-regarded position.

---

## 6. Things to fix in the write-up regardless

- `min_track_hits=6 ≈ 1s` in the session notes implies ~6 fps sampling. The
  continuity log ran at 30 fps. **Pin down the actual sampling rate and state it
  explicitly everywhere** — this ambiguity is probably the bug.
- Both consolidated spreadsheets have *different* tab-mislabeling shifts. Keep
  the two mapping tables strictly separate in code, with a unit test asserting a
  known site total (Alafaya West = 496) so a future edit can't silently
  reintroduce the swap.
- The 3 unparsed `Bicycles (2)` sheets — document as intentionally skipped with
  the reason, so it doesn't read as an unexplained gap in the methods section.


<a id="note-3"></a>
## README_colonial_validation_v31.md
Original location: `docs/colonial/README_colonial_validation_v31.md`.

> **Current submission instructions: read the root README.md only. One command submits the active research suite and final report. Historical commands below are reference, not additional jobs to submit.**

# Colonial North: validating the fine-tuned RT-DETR + X-CLIP bicyclist counter

**Current priorities (2026-10-19 user update):** higher-resolution footage from ANY year, comparison against existing truth, additional detection research, and the high-sensitivity review experiment. Full-day scaling is removed from the plan. The 40-track comparison and own-night fine-tuning are on the back burner and excluded from the updated PowerPoint. Existing truth clips do not need relabelling. See `docs/TODO.md`, `docs/VIDEO_PATHS.md` and `docs/RESEARCH_METHODS.md` from the repo root. Older sections below retain historical plans, not current instructions.

Status as of 2026-10-15 evening (README v31: adds section 40, requests of the evening, batch-5 / scan scripts; adds section 39, tools for the pending work, not yet run on the cluster; README v30: CORRECTS section 37c: the new zone polygons belong to the COLONIAL 2019 camera, not the 2025 video; README v29: hand-off version for a new chat session; adds the 2025 fisheye video outcome and the zone polygons in section 37; batch 4 results in section 35). The long list of per-version notes that used to sit in this line is kept at the very end (section 36). **Start with section 0.**

## 0. START HERE (2026-10-11): where things stand
**Goal.** Count bicyclists and pedestrians at the Colonial North camera (2019-07-10 footage) with the fine-tuned RT-DETR (`rtdetr_v3`) + X-CLIP, and fix the failures found by watching clips.
**Best configuration so far = `b3_combo`** (SAHI-style sliced detection + fusion of X-CLIP, detector and speed + night-only short-track rule). Person-level scores against Rithika's own hand-made truth, 4 clips, 21 people (2 dev clips + 2 hold-outs whose settings were not tuned on them):
| clip | baseline (`exp0_base`) | SAHI alone | **`b3_combo`** |
|---|---|---|---|
| night 21:15-21:30 (6 people) | 0 | 2 | 4 |
| day 14:00-14:15 (5) | 3 | 3 | 5 |
| night 22:00-22:15 hold-out (5 pedestrians) | 0 | 5 | 5 (but 2 extra false tracks on a barricade) |
| day 12:45-13:00 hold-out (2 cyclists + 3 pedestrians) | 3 | 3 | 5 |
| total found | 6 / 21 | 13 / 21 | **19 / 21** |
**Batch 4 (run 2026-10-12): `b4_combo_static5` = `b3_combo` + static-object filter = THE CURRENT BEST.** Same 19 / 21 people found (night 4/6, day 5/5, 22:00 5/5, 12:45 5/5) and 0 false counted tracks on all four clips: the two barricade tracks at 22:00 are gone and nothing else changed (counted 0 cyclists / 5 pedestrians at 22:00). Details in section 35.
Strong hint, not a measured accuracy: one camera, one day, four 15-minute windows, 21 people, thresholds partly chosen on the first two clips.
**What the configuration is (details: sections 23, 25, 29, 32).** Detector with SAHI slicing (640 px, 20% overlap, plus the full frame); tracking; X-CLIP label per track; 3 s minimum on screen; FUSION = the final label comes from three opinions (X-CLIP, the detector's cyclist share of frames, speed in body heights/s) via: veto (X-CLIP bicyclist but detector cyclist < 15% of frames -> pedestrian), lateral speed rule (walk < 0.8, ride > 2.0 body heights/s), night-only short-track rule (21:00-06:00, 0.3-3 s tracks count as bicyclist if detector cyclist >= 90% and weighted X-CLIP >= 0.9). Dropped because no gain: image enhancement (gamma, CLAHE, Zero-DCE), motion-blob diagnostic, promote 90%, speed thresholds of 1.0.
**Still wrong in `b4_combo_static5`:** (the 2 barricade tracks of `b3_combo` at 22:00, `#24`, `#26`, are removed; the third long track `#27` is a real pedestrian whose track also covers the barricade) night 14:47 pedestrian called a cyclist; night 14:21 rider (2.4 s) under the 3 s minimum.
**Verified truth files** (video position mm:ss, one row per person, motorcycle scored as cyclist; on the cluster in `truth/`, copies in the outputs folder): `day_1400_truth.csv` (1 cyclist + 4 pedestrians), `night_2115_truth.csv` (1 motorcycle + 4 cyclists + 1 pedestrian), `day_1245_truth.csv` (2 cyclists + 3 pedestrians; 9:54 not re-checked), `night_2200_truth.csv` (5 pedestrians; barricade = not a person).
**Tools for the open items (2026-10-15, section 39, not yet run):** `scale_up.py`, `pick_new_windows.py`, `finetune_v5.py`, `review_pack.py`, `undistort_fisheye.py` (tarball `colonial_pending_tools.tar.gz`).
**Open / next.** (1) DONE 2026-10-12 (section 35): `b4_combo_static5` = `b3_combo` + static-object filter (net < 5 px AND path speed < 0.05 h/s, track >= 3 s): `bash code/run_batch4.sh` (4 jobs + evaluation). Expected: 22:00 barricade tracks gone, nothing else changes. DUPLICATE SUBMISSION CHECK: running the command twice creates the same jobs twice (the guard only sees a `counts/` folder after a job starts); keep one set. (2) Zones for Colonial: new polygons received (`colonial_north_v2.json`, ref_size 1440x960 inferred), to be verified with `draw_zones_preview.py` (section 37c); person counts and all scores are unaffected by zones. (3) 2025 video test: DONE as a qualitative run (section 37): runs `nv_base_corrine2025_706` and `nv_combo_corrine2025_706`; Rithika watched the 2025 videos and judged them not good for this pipeline (fisheye camera: cars right below the camera are not detected, objects farther away are); not scored, no truth file; the MioVision Data folder holds nothing newer than 2022 (all 720x480); the 2025 video came from elsewhere (path to be asked); no truth file exists for it. (4) Before any claim: label 2-3 NEW 15-minute windows (one night, two day, other hours): the four current clips have been looked at. (5) Not done: fine-tuning on her own hard frames (her stated fallback), temporal detector, BNE-DETR, SAMURAI.
**Statements in older sections that were later corrected (newest wins):** section 15m/21 (the short 14:03 tracks are a PEDESTRIAN, not a lost cyclist); section 26/27 (draft truth, verified in 28); section 28/29 ('three false barricade tracks' is two, see 30); section 30 ('closest real person 30 px' is 19 px, see 31); expectations in sections 22-23 (results are in 23h, 25h, 29).
**Rules of thumb for running things.** Always from `/orange/xiangyan/rithika/vision/vision3/best/test_colonial` (never from inside `code/`); activate the environment first (`source /orange/xiangyan/rithika/vision/yolo_env/bin/activate`); unpack tarballs from that folder (`tar xzf <file>`); the newest complete code set is `colonial_code_latest.tar.gz` (script, slurm, evaluator, probes, all batch scripts, Zero-DCE weights).
**After a batch finishes:** `squeue -u $USER -o "%i %j %T %M"`; `grep -L "Final counts" logs/slurm_b4_combo*.log` (should print nothing); `python code/eval_truth.py --root . --runs exp0_base,b2_2_sahi,b3_combo,b4_combo_static5 --baseline exp0_base | head -60`; `python code/fusion_probe.py --root . --runs b3_combo,b4_combo_static5 | tail -40`.

## 1. Goal
Apply the existing bicyclist/pedestrian counting model (fine-tuned RT-DETR detector + zero-shot X-CLIP video-text classifier) to the
**Colonial North** camera and check, per 15 minutes, whether its counts agree with the human ground-truth counts.

## 2. Data and what was verified before any code was run
| Item | Finding |
|---|---|
| Camera / video | BL Colonial, camera SCU8OG, 720x480, 29.97 fps. 48 hourly mp4 files (about 3600 s each) = a 48-hour recording |
| Clock | Verified from the on-screen clock: file `.001` = 2019-07-10 00:00, `.008` = 07:00, `.025` = 2019-07-11 00:00. So file N starts at hour N-1 (the old pilot code assumed a different offset) |
| Ground truth | `Colonial_North_676806_07-10-2019.xls` (SpreadsheetML XML, not a real .xls). 192 fifteen-minute bins = 48 h. **89 bicyclists in total over the 48 h** (45 on day 1, 44 on day 2), bike lane + sidewalk. The 89 matches the GT CSV and `video_site_mapping.csv` |
| Mapping | video file N covers GT bins (N-1)*4 .. (N-1)*4+3 |
| Videos merged | None. Each hourly file is processed on its own and results are joined by clock time |

## 3. Method
1. **Detector:** fine-tuned RT-DETR (`rtdetr_v3`), classes: person, cyclist, car, truck, bus, other_vehicle.
2. **Tracker:** ByteTrack, with ID stitching across short gaps.
3. **Classifier:** X-CLIP (`microsoft/xclip-base-patch32`), zero-shot, applied to **person tracks only**; it chooses between *bicyclist* and *pedestrian*. It is not run on vehicles.
4. **Final label = X-CLIP's label.** The detector's own label (person/cyclist) is shown next to it for comparison.
5. A track counts once. It is assigned to the 15-minute bin of its midpoint frame, and must be visible at least 3 s (default).
6. Optional zones (road / bike lane / sidewalk) filter vehicles and give the bike-lane vs sidewalk split. The zones file exists on the cluster:
   `zones/colonial_north_v1.json` (ref_size 720x480; polygons `road`, `bike`, `sidewalk`; pixel coordinates). It has NOT yet been used in a verified run (see section 14, task 4).
7. **Detector training data (for context):** `rtdetr_v3` was fine-tuned on about 200 annotated daytime images. Train sites: Anderson St (2021), Church Ave (2021),
   Curry Ford North (2022), BL Colonial (2019), NBL University (2019). Validation site: Corrine Dr (2025, newest camera hardware, not used in training).
   No night frames were in the training set, which is the likely reason for the night failure (not yet tested).

## 4. Validation design
- One job per hourly video. Tracking runs across the whole hour (no cuts at bin boundaries), then counts are split into 15-minute bins.
- **Outputs per run** (all under `test_colonial/`, nothing is overwritten): annotated clips (one per 15-min bin, each box shows the RT-DETR label and the X-CLIP label), per-bin counts, per-track table, run log, and an Excel workbook with sheets `Per_15min`, `Per_hour`, `Metrics`, `Tracks`, `Run_Log`.
- **Metrics:** per-bin bias (AI - GT), MAE, RMSE, WAPE, share of bins within +-1 and +-2, Pearson r; approximate count-matched precision/recall. The last two are *approximations*: ground truth is counts only, with no per-person labels. Hourly totals are reported too.
- Pipeline checks: GT total vs GT CSV vs mapping file, 15-min labels consecutive, chunk durations about 3600 s, chunks present.

## 5. Results

### Per hour (AI / ground truth)
| Hour | Run | Bicyclists | Pedestrians | Notes |
|---|---|---|---|---|
| 07:00 | run2 | 3 / 4 | 15 / 4 | construction cones counted as pedestrians (about 7 times) |
| 10:00 | run4 | 3 / 3 | 1 / 9 | |
| 12:00 | run5 | 5 / 3 | 1 / 2 | 12:45 bin over-counts (4 vs 2) |
| 13:00 | run5 | 1 / 3 | 5 / 6 | |
| 14:00 | run4 | 3 / 3 | 4 / 10 | bin-by-bin exact for bicyclists |
| 16:00 | run4 | 3 / 5 | 4 / 4 | bin-by-bin exact for pedestrians |
| 21:00 (night) | run5 | **0 / 3** | 1 / 7 | detector nearly blind in the dark |

Settings: runs 2 and 4 used defaults; run5 used a 1.0 s pedestrian minimum (see below). **Zones were not applied in any run** (the zones file was not on the cluster).

### Summary
| | Bicyclists | Pedestrians |
|---|---|---|
| Daytime hours (07,10,12,13,14,16) | 18 AI vs 21 GT | 15 vs 31 over the 5 daytime hours excluding 07:00 (07:00 is cone-contaminated) |
| Night hour (21:00) | 0 vs 3 | 1 vs 7 |
| Run4 (3 hours, 12 bins) | 9 vs 11, MAE 0.50/bin, 92% of bins within +-1, r = 0.71 | 9 vs 23, MAE 1.17/bin, count-matched precision 100%, recall 39% |
| Run5 (3 hours, 12 bins) | 6 vs 9, MAE 0.75/bin | 7 vs 15, MAE 1.00/bin |

Note: excluding the 07:00 cone hour, pedestrians over the other six hours including night are 16 AI vs 38 GT (about 42%).

**Reading:** bicyclists in daylight are counted within roughly 15% overall, with misses and some extras in individual bins. Pedestrians are heavily **under**-counted (about 40% recall). Night is a failure for both classes.

### Parameter experiments (offline, no re-run)
- **Minimum track duration, pedestrians:** shortening 3.0 s to 1.0 s raised pedestrian recall from 39% to 61% on run4 alone (precision stayed 100%), but on run5 the two extra tracks moved 269 and 336 px in 1-2 s (rider speeds, not walking speeds), and one of them had detector label 'cyclist'; they were most likely **cyclists labelled as pedestrians** (not yet confirmed clip by clip). X-CLIP is unreliable on tracks of 1-2 s. Pooled over 24 bins: 1.0 s gives recall 50% / precision 90% vs 34% / 93% at 3.0 s. Not a clean win.
- **Movement filter for static objects (cones):** rejects cones but would also reject real pedestrians who walk toward/away from the camera (only 21-29 px of net movement in some real tracks). Kept off.
- **Detector confidence cutoff:** helped only the 07:00 cone hour; on the other hours it only removed true tracks. Kept off.

## 6. Error analysis from watching the annotated clips
**Detector misses (never boxed):**
- 10:00-10:15: a go-kart and a bicyclist passing in the opposite direction, a second bicyclist later, and a pedestrian in shadow.
- 21:15-21:30: a cyclist approaching the camera, and 3 cyclists on the sidewalk of which only the last was detected. A cyclist clearly visible in the dark frame at 21:22:10 had no box.
- A person walking on the grass is not tracked until reaching the sidewalk.

**Classification errors (X-CLIP):**
- A pedestrian crossing the road was labelled bicyclist (twice).
- Labels change as a person approaches the camera: far away = pedestrian, close = cyclist (and the reverse).
- On short tracks X-CLIP is near a coin flip (e.g. 0.53 vs 0.47).

**The two labels fail in different places** (screenshots from the clips):
| Case | RT-DETR | X-CLIP | Truth |
|---|---|---|---|
| Real cyclist, daylight | person 0.57 (46% cyclist) | bicyclist 1.00 | bicyclist: X-CLIP right |
| Pedestrian crossing | person 0.72 (7% cyclist) | bicyclist 0.78 | pedestrian: detector right |
| Night, sidewalk rider | cyclist 0.61 (100%) | 0.53 / 0.47 | bicyclist: detector right |

This is the main finding for the label question. It motivates combining the two (see next steps).

**Ground truth is not perfect.** In the 07:00-07:15 clip the reviewer counted 2 riders where the GT bin has 1. Exact bin-by-bin matches in other hours show no global time offset, so differences are individual disagreements, not a clock shift.

## 7. What changed along the way (code versions)
| Version | Change |
|---|---|
| v10 | original sample script (untouched) |
| v11 | wall-clock aware; 15-min bins; one annotated clip per bin; per-bin CSV, track CSV, JSON run log; nothing overwritten |
| v12 | clips written as soon as each bin ends (header marked provisional) |
| v13 | optional static-object filter (`--person-min-disp`) |
| v14 | both labels on every person box; `Tracks` sheet in the Excel; detector-vs-X-CLIP agreement table |
| v15 | separate minimum durations for pedestrians and bicyclists |
| v16 | ground truth of the bin printed in the clip header; vehicle boxes state "X-CLIP: n/a (people only)" |
| v17 | adds outputs only (counts unchanged, diff vs v16 is additions plus the title line): per-frame trajectories, per-track motion/direction, split-track candidates, trails on the annotated clips. See section 15 |
| v18 | (written 2026-10-06, not yet run on the cluster) optional time-of-day settings: `--night-start/--night-end` plus `--night-det-conf`, `--night-bic-min-sec`, `--night-ped-min-sec`. All off by default, so counts equal v17 unless set. See section 20 |

Bugs found by testing on a stand-in pipeline (fake detector/tracker on a synthetic video): the run log was saved under the wrong filename and the clip list got overwritten by a variable-name collision, both fixed. A mistaken `MAX_FRAMES` setting produced a 1-second test clip (it is a stop frame, not a count).

## 8. Limitations
- **Small sample:** 7 of 48 hours (about 14%), 28 bins, 24 bicyclists in the ground truth. One missed rider moves a bin by 100%.
- **Tuning and testing overlap:** thresholds were explored on the same hours they are reported on.
- **No zones in runs 2, 4 and 5**, so bike-lane/sidewalk results are not reported and vehicles were not filtered. A zones run (`zones_test`, chunk 15) is pending.
- **One camera, one site.** Night video only from one hour.
- **Ground truth is counts only** (no per-person labels), so precision/recall are approximations. Human counters can disagree with the video.

## 9. Next steps (in priority order)
1. **Zones:** `zones/colonial_north_v1.json` now exists. Run it on one hour (`zones_test`, chunk 15), confirm "zones loaded" in the log, verify the facility column and the vehicle filter. (Pending, section 14 task 4.)
2. **Night:** DONE. `night_dc015` (detector confidence 0.15 on 21:15-21:30) did not help (night bicyclists 0 vs 3, pedestrians 0 vs 7), so night frames need to go into fine-tuning.
3. **Combine the two labels:** run `sweep_fusion_v1.py` on runs 4 and 5 to see if a rule using the detector's cyclist share plus X-CLIP's probability beats X-CLIP alone. Implement only if it holds on other hours.
4. **Revert the pedestrian minimum to 3.0 s** unless step 3 makes short tracks reliable.
5. **Fine-tune RT-DETR on Colonial frames** (day and night): sample frames around the missed events, label boxes, train, evaluate on whole hours held out of training. This is the real fix for recall; cost is mainly labeling time.
6. **Scale up** to block 1 (24 hours, about 46 GPU-hours) only after steps 1-5, reporting hourly totals, per-bin metrics and day/night separately.

## 10. How to reproduce
```bash
export ROOT=/orange/xiangyan/rithika/vision/vision3/best/test_colonial
cd $ROOT && source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
# one hour (array id = chunk number; 8 = 07:00-08:00):
sbatch --time=05:00:00 --export=ALL,RUN=myrun,ZONES_JSON=$ROOT/zones/colonial_north_v1.json --array=8 code/run_xclip_colonial_v16.slurm
# Excel + log:
python code/aggregate_colonial_v13.py --root $ROOT --run myrun --expect-chunks 8 \
  --gt-csv ground_truth/ground_truth_bicycle_counts_v2.csv --mapping-csv ground_truth/video_site_mapping.csv
# per-bin table / pedestrian tracks / offline sweeps:
python code/diag_colonial_v1.py --root $ROOT --mode bins --run myrun
python code/sweep_secs_v1.py --root $ROOT --run myrun --label PEDESTRIAN
python code/sweep_fusion_v2.py --root $ROOT --run myrun
# per-object accuracy (needs hand labels): template, fill true_label, eval
python code/track_truth_v1.py template --root $ROOT --run myrun --out $ROOT/validation/track_truth_myrun.csv
python code/track_truth_v1.py eval --file $ROOT/validation/track_truth_myrun.csv
```
v17 (trajectories + trails + split report; same counts as v16 with the same settings):
```bash
# whole hour, same as v16 but with the v17 script/slurm (new env vars: TRACK_THR LOST_SEC STITCH_SEC STITCH_PX TRAIL_SEC SPLIT_GAP_SEC SPLIT_PX)
sbatch --time=05:00:00 --export=ALL,RUN=myrun,ZONES_JSON=$ROOT/zones/colonial_north_v1.json --array=8 code/run_xclip_colonial_v17.slurm
# one 15-min window of an hour file: START_FRAME = first frame (+5 margin), MAX_FRAMES = STOP frame (0 = to end). 900 s = 26973 frames at 29.97 fps
bash code/submit_traj_tests_v1.sh     # the test windows below; edit it to drop windows/settings
```
Folder layout: `code/` scripts, `zones/`, `ground_truth/`, `counts/<run>/`, `annotated/<run>/<chunk>/`, `logs/<run>/`, `validation/`.

## 11. What the metrics measure (and do not)
| Metric | Measures | Limit |
|---|---|---|
| Per-bin MAE / bias / within +-1 | how close the AI count is to the human count in each 15 min | counts only: an AI miss and an AI false positive in the same bin cancel out |
| Count-matched precision / recall | approximate, from min(AI, GT) per bin | not per-object |
| X-CLIP vs RT-DETR vs combined, **count level** (`sweep_fusion_v2.py`) | which labelling rule gives counts closest to the human counts | same limit |
| **Per-object accuracy** (`track_truth_v1.py`) | accuracy, confusion matrix, precision/recall/F1 of RT-DETR, X-CLIP and the combined rule on tracks a person has labelled; detection recall including people the AI missed | needs a hand-labelled set (target 40+ real tracks); **not done yet** |

The ground truth has no per-person labels, so true per-object accuracy cannot be computed from it. Any accuracy figure for the two models
must come from the hand-labelled track set.

## 12. Is this the best approach? (brief literature check, not a systematic review)
- The overall structure (detect, track, classify, count) is the standard design for video-based bicycle/pedestrian counting. Examples:
  Kocamaz et al., "Vision-based counting of pedestrians and cyclists", WACV 2016 (a detector followed by a second stage that separates
  cyclists from pedestrians, with foreground, geometry and optical-flow cues); Shahraki et al., "A Trajectory Based Method of Automatic
  Counting of Cyclist in Traffic Video Data", Int. J. Artificial Intelligence Tools 26(4), 2017; a Louisiana DOT-funded study
  (HOG detection, tracking, classification; https://www.itskrs.its.dot.gov/node/209776).
- The unusual part here is the **zero-shot X-CLIP** classification stage (Ni et al., "Expanding Language-Image Pretrained Models for General
  Video Recognition", ECCV 2022, https://arxiv.org/abs/2208.02816). X-CLIP was built and evaluated for general action recognition,
  and its paper reports large gains in the few-shot setting when only a handful of labelled examples exist. Our clips are tiny, low-resolution
  person tracks of a few seconds, which is far from those benchmarks.
- The literature repeatedly names lighting and viewpoint as the main source of error and recommends training data covering varied
  conditions (Louisiana study above; Elshebli et al., YOLO-SORT under weather/lighting/viewpoint, ETASR). Night-time work fine-tunes
  detectors on night or infrared data (e.g. Yoshihara et al. 2024, RGB+FIR fusion with transfer learning). This matches our night failure.
- Reported accuracies are not comparable with ours: different sites, cameras and conditions. Examples for context only: an embedded
  cyclist counter reports counting accuracy of 78-82% in a real urban setting (JBCS 2026); a Pittsburgh-style classical system
  reported bicycle count error under 13% on its test sites (PBTC, SWOV record).

**Assessment, based on our own measurements:** the detector's missed riders (especially at night) are the largest loss, and the zero-shot
X-CLIP label is the second weakest link (it mislabels crossing pedestrians and flips with distance). The evidence points to
(1) fine-tuning the detector on Colonial day and night frames, (2) replacing or supplementing zero-shot X-CLIP with a classifier trained or
few-shot adapted on a small set of labelled Colonial tracks (possibly using simple physical features such as speed), and (3) reporting
per-object metrics from a hand-labelled set. These are recommendations to test, not results.

## 13. Verified results (run on the cluster 2026-10-05)

### 13a. Headline counting metric (`headline_metrics_v1.py`, runs 2+4+5, 28 bins = 7 hours; processed bins hold 27% of the 89 GT bicyclists)
| | AI vs GT | AI/GT | bias/bin | MAE/bin | within +-1 | WAPE/hour | r | approx prec / rec |
|---|---|---|---|---|---|---|---|---|
| Bicyclists, all | 18 vs 24 | 75% | -0.21 | 0.64 | 82% | 42% | 0.47 | 67% / 50% |
| Bicyclists, day (6 h) | 18 vs 21 | 86% | -0.12 | 0.62 | 83% | 33% | 0.54 | 67% / 57% |
| Bicyclists, night (1 h) | 0 vs 3 | 0% | -0.75 | 0.75 | 75% | 100% | nan | nan / 0% |
| Pedestrians, all | 31 vs 42 | 74% | -0.39 | 1.32 | 71% | 79% | 0.23 | 58% / 43% |
| Pedestrians, day | 30 vs 35 | 86% | -0.21 | 1.29 | 71% | 77% | 0.26 | 57% / 49% |
| Pedestrians, night | 1 vs 7 | 14% | -1.50 | 1.50 | 75% | 86% | 0.17 | 100% / 14% |

Pedestrian AI/GT ratio looks better than it is: the 07:00 cone hour inflates the AI count. Quote WAPE/hour and recall for pedestrians, not the ratio.

### 13b. Labelling rules at count level (`sweep_fusion_v2.py`, runs 4+5, 24 bins, 29 tracks >= 3 s; GT bic 20, ped 38)
| rule | AI bic | MAE bic | AI ped | MAE ped | MAE sum |
|---|---|---|---|---|---|
| X-CLIP only (current) | 15 | 0.62 | 14 | 1.08 | 1.71 |
| RT-DETR only (>=50% cyclist) | 5 | 0.71 | 24 | 1.00 | 1.71 |
| fused D=20 O=0.95 F=80 | 12 | 0.50 | 17 | 0.96 | 1.46 |
| X-CLIP + speed >= 40 px/s | 12 | 0.50 | 17 | 0.96 | 1.46 |
| speed only >= 40 px/s | 12 | 0.50 | 17 | 0.96 | 1.46 |

Net speed of tracks X-CLIP calls BICYCLIST: median 67 px/s; PEDESTRIAN: median 8 px/s. The fused rule differs from X-CLIP-only on 3 tracks
(chunk 011 10:43:46, chunk 013 12:56:16, chunk 014 13:17:45), all bicyclist -> pedestrian. Suggestive only (3 tracks, 24 bins). Caveat: net image
speed is low for people moving toward/away from the camera.

## 14. PENDING TASKS (not done)
1. **Hand-label the tracks (per-object accuracy). Blocked on a human, ~30-45 min.** Without it there is NO per-object accuracy for X-CLIP / RT-DETR / fused.
   The file is `validation/track_truth_runs45_v2.csv` (45 rows; the template did not overwrite the old `track_truth_runs45.csv`, which is unlabelled; always use `_v2`).
   `true_label` is currently EMPTY for all rows (any earlier labels were placeholders and were cleared; never trust a run of `eval` before real labels exist).
   How to label:
   a. Print clip + seek time per row:
      ```bash
      python - <<'EOF'
      import csv,os
      from datetime import datetime as D
      f=os.environ['ROOT']+'/validation/track_truth_runs45_v2.csv'
      for i,r in enumerate(csv.DictReader(open(f)),1):
          t=D.strptime(r['first_time'],'%Y-%m-%d %H:%M:%S')
          b=D.strptime(r['first_time'][:11]+r['bin_start']+':00','%Y-%m-%d %H:%M:%S')
          s=int((t-b).total_seconds())
          print(i, os.path.basename(r['clip_hint']), "seek", f"{s//60:02d}:{s%60:02d}" if s>=0 else "previous clip", "for", r['secs'], "s")
      EOF
      ```
   b. Watch ~10 s at each seek time. Decide from the video only: BICYCLIST, PEDESTRIAN or NOT_PERSON. Do NOT copy the model labels or GT-implied labels
      (that inflates accuracy). GT bin counts may be used as a hint only.
   c. Write labels by row number (batches OK; only listed rows change):
      ```bash
      python - <<'EOF'
      import csv,os
      f=os.environ['ROOT']+'/validation/track_truth_runs45_v2.csv'
      labels={5:'...', 15:'...'}   # row number -> BICYCLIST / PEDESTRIAN / NOT_PERSON
      rows=list(csv.DictReader(open(f))); cols=list(rows[0].keys())
      for i,l in labels.items(): rows[i-1]['true_label']=l
      w=csv.DictWriter(open(f,'w',newline=''),fieldnames=cols); w.writeheader(); w.writerows(rows)
      EOF
      ```
   d. Priority order: rows 5, 15, 17 (fused-rule flips), 20, 45 (model/speed disagreement), 16, 26, 34 (long tracks), then the rest.
   e. For each person the AI never tracked, append a row with empty `track_id` (fills detection recall); optional, do last.
   f. `python code/track_truth_v1.py eval --file $ROOT/validation/track_truth_runs45_v2.csv`. Need >= 40 labelled tracks before quoting accuracy.
2. DONE 2026-10-05: `night_dc015` (detector confidence 0.15 on 21:15-21:30) did NOT help. Night bicyclists still 0 vs 3; night pedestrians 0 vs 7
   (was 1 vs 7). Overall pedestrian recall 43% -> 40% (31 -> 30 AI vs 42 GT). One 15-min bin only, but a lower threshold does not recover riders
   the detector cannot see; this supports fine-tuning on night frames (task 5).
3. `bin2_v14b` (07:15-07:30, static filter + lower threshold): no output exists in `counts/` and no job was queued. Low priority; rerun only if the cone question matters.
4. Zones verification. The file `zones/colonial_north_v1.json` exists. Job `zones_test` (chunk 15 = 14:00-15:00) was submitted 2026-10-05 with
   `sbatch --time=05:00:00 --export=ALL,RUN=zones_test,ZONES_JSON=$ROOT/zones/colonial_north_v1.json --array=15 code/run_xclip_colonial_v16.slurm`
   (an earlier submission, job 44854360, was cancelled by mistake; check `squeue -u $USER` that the resubmission is running). When done:
   a. `grep -i zones $(ls -t $ROOT/logs/*.log | head -1)` must show "zones loaded".
   b. Run `aggregate_colonial_v13.py` with `--run zones_test --expect-chunks 15` (section 10) and check the facility column (bike lane vs sidewalk) is filled
      and vehicles outside the road zone are filtered.
   c. Compare the 14:00 hour with run4 (bicyclists 3 vs 3 GT, pedestrians 4 vs 10) to confirm zones did not remove true tracks.
   Note: the pedestrian minimum is already 3.0 s by default in the slurm script (`PED_MIN_SEC=3`); never pass `PED_MIN_SEC=1` (run5 did).
   UPDATE 2026-10-05: zones_test finished. Person counts equal run4 (bicyclists 3 vs 3 GT, pedestrians 4 vs 10 GT), so zones did not remove true person tracks (4c). 4a/4b still open: see item 13 and 15g.
5. Other strategies to test (from the literature check, section 12), in order of expected value:
   - Fine-tune RT-DETR with NIGHT frames added (current ~200-image training set is daytime only, section 3 item 7), plus more Colonial frames
     around the missed events (biggest recall loss; evaluate on whole held-out hours).
   - Replace or supplement zero-shot X-CLIP with a few-shot/trained classifier on the hand-labelled tracks, optionally with a speed feature
     (needs the labels from task 1, and more than 45 tracks to hold out a test set).
   - Optional: run X-CLIP on vehicles (car/truck/bus prompts); extra compute, low priority.
6. Fill the final comparison (X-CLIP vs RT-DETR vs fused, per-object) into this section once task 1 is done.
7. DONE 2026-10-05 (partly): v17 tracking tests read (15g). Base and lowconf gave identical counts at 12:45 and 21:15; 0 split pairs at 12:45. The tracking-id-break hypothesis is NOT supported in these two windows. Not done: any test on a pedestrian-heavy window (the 14:00 hour has 4 vs 10 pedestrians; see item 12).
8. Add direction/speed (body-heights/s, sideways motion only) as a feature for the cyclist/pedestrian decision, after task 1 labels exist to check it against. Combine with the fusion rule in section 13b.
9. Optional second detector test: `VEH_WEIGHTS=<COCO rtdetr-l.pt>` on the same windows.
10. Night: collect Colonial night frames (+ optionally NightOwls images) for fine-tuning (task 5, first bullet).
11. DONE 2026-10-05: night min-duration re-run `traj17_night_min04` (job 44875534, 36 min). Results in 15l. Short night tracks are real riders; the detector box disappears as riders get close to the camera.
12. Pedestrians at 14:00 (4 counted vs 10 in the ground truth): five pedestrian-labelled tracks of 1.2-2.4 s were filtered (15g). v16 saved no speed/direction for them. To tell walkers from riders, re-run chunk 15 with the v17 script/slurm (same settings, about 1.9 h) and read `_track_motion.csv`. README section 5 warns that short pedestrian tracks may be cyclists.
13. Finish zones verification (task 4): the log tail does not show a "zones loaded" line, the facility column or the vehicle-filter effect. Check: `grep -i zone logs/slurm_colonial_v16_44855081_15.log | head` and the facility column of `counts/zones_test/*_tracks.csv`.
14. PARTLY DONE 2026-10-05: 12:45 clip watched (15h). Still open: which of tracks 1/4/6/9 are the 2 real riders, and which pedestrian was counted twice. Use the check in 15h on `counts/traj17_base/*013*_trajectories.csv` / `_track_motion.csv`.
15. Watch the `zones_test` clips at 14:03:03, 14:26:09 and 14:27:30 (the three 100%-detector-cyclist short tracks, 15m). Real riders -> the short-track rule has support; not riders -> it needs another condition.
16. Night fine-tuning: first attempt (NightOwls mix) FAILED, see section 19. Next candidates: own Colonial night/close-to-camera frames (hand-labelled, from hours other than 21:00), and the v18 short-track rule (15m). UPDATE 2026-10-06: the night-only short-minimum setting is now implemented as v18 day/night settings (section 20); results pending (item 17).

17. **v18 day/night test (pending, not run yet).** Copy `xclip_overlay_v18_colonial.py`, `run_xclip_colonial_v18.slurm`, `submit_day_night_v1.sh` to `code/`, run `bash code/submit_day_night_v1.sh` (10 jobs, about 5 GPU-hours), then read section 20c. Never tried before: low detector confidence AND short minimum together at night; day and night settings in one run.

18. **Detector-improvement experiments (planned, NOT started).** Read section 22, answer the questions in 22h, then code gets written. Test clips proposed: night 21:15-21:30 and day 14:00-14:15.

19. **Run the v19 experiment batch (written, not yet run).** Copy the bundle, `bash code/run_all_experiments.sh`, fill in both truth files, read `exp_results/EVAL_*.md` and watch the clips. Commands in section 23c.

## 15. Session 2026-10-05: trajectories and tracking tests (v17)

### 15a. Why
Open questions from this session: (1) are some of the pedestrian misses caused by tracking-ID breaks (a walker whose track splits into two pieces, each shorter than the 3 s minimum, is never counted)? (2) can we output where each cyclist/pedestrian goes (trajectory), and use direction/speed as an extra signal? (3) is it worth switching to another detector/dataset?

### 15b. What was built (new files, nothing overwritten; v16 files untouched)
| File | Purpose |
|---|---|
| `code/xclip_overlay_v17_colonial.py` | v16 + new outputs below. Detector, tracker, X-CLIP and counting logic unchanged |
| `code/run_xclip_colonial_v17.slurm` | v16 slurm + env vars `TRACK_THR` (0.25) `LOST_SEC` (3.0) `STITCH_SEC` (5.0) `STITCH_PX` (150) `TRAIL_SEC` (5.0) `SPLIT_GAP_SEC` (8.0) `SPLIT_PX` (120). Defaults equal the script defaults |
| `code/submit_traj_tests_v1.sh` | submits the 15-min test windows (see 15d) with two tracking settings |

New outputs per video file, in `counts/<run>/`:
- `<tag>_trajectories.csv`: one row per track per frame (ground point = bottom-centre of the box, box, `coasted` flag, final label, counted). Coasted frames (optical-flow guesses) are flagged and are not used for speed/direction.
- `<tag>_track_motion.csv`: per track path and net distance (px), speed in px/s and in body-heights/s, direction (`toward_camera`, `away_from_camera`, `moving_left`, `moving_right`, `static`).
- `<tag>_split_candidates.csv`: pairs (A ends, B starts within 8 s and 120 px of where A was heading) that probably are one person whose id broke. Columns include `a_or_b_alone_passes_min` and `joined_passes_min`; rows with 0/1 are tracks that would be counted only if joined. Nothing is merged or recounted; this is a measurement.
- Annotated clips: fading trail (last `TRAIL_SEC` seconds, 0 = whole history) + arrow per **counted** person, coloured like the box. Short tracks that fail the minimum duration get no box and no trail but are in the CSVs.

### 15c. How it was tested, and limits
- Run end to end on a synthetic video with a stub detector and a stub X-CLIP (no real model, no GPU). Verified: all new CSVs written, trail drawn, a track broken by a 7 s detector blackout was reported as a split candidate, and a stationary/one-point track gives `static`. Unit tests of the motion/split helpers: a walker moving toward the camera gives `toward_camera`; a rider gives `moving_right`.
- **Not tested** with the real RT-DETR + X-CLIP on the cluster. The first real run is the real test; send the last 20 lines of a log if a job fails.
- Direction assumes larger image y = closer to the camera. Not checked against the Colonial view.
- Speed in body-heights/s is perspective-robust for sideways motion only: the synthetic walker moving toward the camera gave 0.21 body-heights/s despite moving. Do not use it for toward/away motion.
- A 15-min window starts tracking from empty at its first frame, so people already in view get new ids and edge counts can differ slightly from the whole-hour runs.

### 15d. Test windows and jobs
| Window | Hour file (chunk) | Frames (START_FRAME / MAX_FRAMES) | Why |
|---|---|---|---|
| 10:00-10:15 | 011 | 1 / 26973 | day, cyclists + pedestrians (run4) |
| 12:45-13:00 | 013 | 80924 / 0 (to end) | day; this bin over-counts (4 vs 2) in earlier runs |
| 21:15-21:30 | 022 | 26978 / 53946 | night; riders missed |

Two settings per window (RUN names):
- `traj17_base`: run4 settings (det conf 0.25, track thr 0.25, lost 3 s, stitch 5 s / 150 px).
- `traj17_lowconf`: `DET_CONF=0.10 TRACK_THR=0.30 LOST_SEC=5 STITCH_SEC=8 STITCH_PX=200`.

Submitted 2026-10-05 (job ids 44860619-44860624, order: base 011/013/022, then lowconf 011/013/022). The two chunk-011 jobs (44860619, 44860622) were cancelled on purpose (log: SIGNAL Terminated at frame ~7100), so there is NO 10:00-10:15 result. Chunks 013 and 022 finished with both settings (runtime 1703-1722 s each, about 29 min, as estimated). The earlier `zones_test` job (44855081, chunk 15) also finished (runtime 6884 s, about 1.9 h). Results: section 15g.

### 15e. Findings from reading the code (not yet measured)
- **ByteTrack's low-confidence pass was effectively off in all earlier runs.** supervision's ByteTrack matches leftover tracks against detections with confidence between 0.1 and the activation threshold. The runs used detector conf 0.25 and track threshold 0.25, so that band was empty. `traj17_lowconf` opens the band (0.10-0.30). `night_dc015` (conf 0.15, threshold 0.25) opened only a thin band and did not help at night, so expect this to help daytime fragmentation, not night blindness. Hypothesis; tested in 15g: no change in counts in the two windows, so the lowconf settings were not adopted.
- **BoT-SORT is not recommended for now.** Its camera-motion compensation has no effect with a fixed camera, and as far as I know its appearance matching is not available with RT-DETR in ultralytics (not verified here). ByteTrack parameters and the stitcher are the first things to tune.
- **Pretrained models / datasets (quick search, nothing tested):** nothing found that clearly beats the fine-tuned RT-DETR on this fixed camera. Hugging Face: one undocumented cyclist detector (`Quantum-Analytics/cyclists_detector`), not usable as evidence. NightOwls (night pedestrian dataset: 279k frames, 40 sequences, 3 countries, tracking ids, bicycle-driver class; Roboflow Universe has a ~1,500-image subset, CC BY 4.0) is the only relevant lead, for extra NIGHT training data, not as a drop-in model. Its annotations cover people higher than 50 px only, and the camera differs from Colonial. GitHub results were generic YOLO+SORT demos.
- A second, COCO-trained person detector can already be merged with the fine-tuned one: pass `VEH_WEIGHTS=<path to rtdetr-l.pt>` to the slurm (download the weights on a login node first; compute nodes may have no internet). Not run yet.

### 15f. What to read when the jobs finish
```bash
ls counts/traj17_base/ counts/traj17_lowconf/
tail -n 25 logs/slurm_colonial_v17_*.log
```
1. `Split candidates:` line in each log: how many pairs, and how many "would pass the minimum only if joined". Compare base vs lowconf. If base has several and lowconf fewer, tracking breaks matter and the lowconf settings help.
2. Compare counts of base vs lowconf and vs the old runs (run4 for 10:00, run5 for 12:00-13:00 and 21:00; note run5 used the 1.0 s pedestrian minimum, which must not be reused).
3. Watch the annotated clips: do trails follow one person without jumps? Do the pedestrian trails in 12:45 break?
4. `_track_motion.csv`: check direction against what you see in the clip.

### 15g. Results read from the logs (2026-10-05)

Only the summary lines of each log were read; the v17 CSVs were not opened (not yet shared). Facts first, then interpretation.

**Counts, v17 windows** (GT = ground truth for that 15-min bin from section 5; the 12:45 bin number comes from the earlier 4-vs-2 comparison, the night numbers from the `night_dc015` comparison):

| Window | Setting | Bicyclists | Pedestrians | Vehicles | Split pairs (would newly pass min) | GT bic / ped |
|---|---|---|---|---|---|---|
| 12:45-13:00 | base | 4 | 1 | 589 | 0 | 2 / not stated |
| 12:45-13:00 | lowconf | 4 | 1 | 552 | 0 | |
| 21:15-21:30 | base | 0 | 0 | 285 | 1 (0) | 3 / 7 |
| 21:15-21:30 | lowconf | 0 | 0 | 253 | 0 | |

- lowconf made tracks about 10-15% longer in frames at 12:45 and merged the two night fragments (frames 52789-52821 and 53020-53045 of the base run) into one 2.2 s track, still under the 3 s minimum. It lowered the vehicle count by 6-11%; which vehicle count is right was not checked (no vehicle ground truth was looked at).
- **Interpretation:** broken ids do not explain the 12:45 over-count or the night misses in these two windows; the lowconf settings gave no count benefit. Two windows only.

**12:45-13:00, four bicyclist tracks vs GT 2 (base run).** Times are clock times from the frame numbers (29.97 fps), all inside the 12:45 clip.

| Track | Time | Secs | wtd X-CLIP bicyclist | % scores detector says cyclist |
|---|---|---|---|---|
| 1 | 12:45:40-12:45:56 | 9.1 | 0.65 | 45% |
| 4 | 12:53:07-12:53:13 | 3.7 | 0.79 | 46% |
| 6 | 12:53:45-12:53:52 | 7.0 | 0.79 | 45% |
| 9 | 12:56:17-12:56:38 | 18.6 | 0.65 | 7% |
Pedestrian track 7: 12:54:53-12:55:03, 4.8 s, box 24 px tall, direction `static`. Track 9 is the first suspect for a pedestrian labelled bicyclist (detector says person 93% of the time, X-CLIP says bicyclist 0.60 unweighted); this is a suspicion from the log, not confirmed. Speeds are in `_track_motion.csv` (chunk 13), not yet read.

**Night 21:15-21:30 (base run), tracks removed by the 3 s minimum:**

| Track | Time | Secs | X-CLIP bicyclist | Detector says cyclist |
|---|---|---|---|---|
| 1 | 21:19:03 | 0.6 | 0.96 | 100% |
| 2 | 21:22:07-08 | 0.4 | 0.99 | 100% |
| 4 | 21:29:21 | 0.9 | 0.68 | 59% |
| 7 (pedestrian-labelled) | 21:29:29 | 1.0 | ped 0.59 | 100% |
The detector sees riders at night but only for under a second, and the minimum duration removes them. Track 2 is within a few seconds of the 21:22:10 rider that section 6 says had no box. Three candidates vs GT 3 bicyclists may be a coincidence: see the 14:00 evidence below. Filtered tracks are not drawn in the annotated clip, so none of this has been checked by eye.

**zones_test, chunk 15 (14:00-15:00, run 6884 s):** bicyclists 3 (GT 3), pedestrians 4 (GT 10), vehicles 2268. Person counts are the same as run4, so the zones file did not remove true person tracks. Not visible in the log tail: the "zones loaded" line, the facility column, and the effect on vehicles (task 4a/4b open).
- Filtered bicyclist-labelled tracks at 14:00: five tracks of 0.4-1.1 s with X-CLIP 0.82-0.97 (14:03:03, 14:03:05-08, 14:20:26-31, 14:26:09, 14:27:30), although the 3 counted tracks already match the GT of 3. A short bicyclist minimum would therefore add up to five bicyclists in that hour. Evidence against lowering the bicyclist minimum globally, and a reason not to read the night match too strongly.
- Filtered pedestrian-labelled tracks of 1.2-2.4 s: tracks 12 (14:12:29-33), 13 (14:12:32-34, overlaps track 12 in time), 21 (14:26:03-11), 30 (14:40:23-25), 34 (14:49:27-36). No speed or direction exists for them (v16). These could be the missing pedestrians or riders (section 5).

**Watch list (clips in `annotated/traj17_base/...0.013/` and, after item 11, the night re-run):**
- 12:45 clip at 12:45:40, 12:53:07, 12:53:45, 12:56:17: which boxes are really bicyclists (GT says 2 of 4); does each trail follow one person.
- Night re-run clip at 21:19:03, 21:22:07, 21:29:21, 21:29:29: real riders or false boxes.

### 15h. What was seen in the 12:45-13:00 clip (watched by hand, 2026-10-05)
From the screenshots of the clip (base run): **3 pedestrians and 2 bicyclists** are really in the bin. The ground truth (2 bicyclists) is right; the AI counted 4 bicyclists and 1 pedestrian.
- 1 pedestrian was **never detected**: the person walked on the grass (same miss as in section 6).
- The **last pedestrian was counted as both a pedestrian and a bicyclist** (two tracks or two labels for one person; not yet confirmed which).
- Reading: the over-count (4 vs 2) is a **labelling / duplicate-track error, not a missed-rider or tracking-break problem**. This fits 15g (0 split pairs, lowconf unchanged) and the fused rule in 13b, which flips the 12:56:16 track from bicyclist to pedestrian.
- Not yet known: which of the four bicyclist tracks (12:45:40, 12:53:07, 12:53:45, 12:56:17) are the 2 real riders. Check (speeds + direction; riders move faster, `static`/slow = walker):
```bash
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial && python - <<'PY'
import csv,glob
f=glob.glob('counts/traj17_base/*013*track_motion.csv')[0]
for r in csv.DictReader(open(f)): print(r)
PY
```
(Print first, then pick columns; do not assume field names.) If two tracks overlap in time at 12:56 with one pedestrian and one bicyclist label, that is the double-counted person.

### 15i. Are the v17 results better than the old ones?
**No, not for counts.** v17 only adds outputs (trajectories, motion, split report, trails); counts equal v16 with the same settings. Evidence: base at 12:45 = 4 bicyclists (same 4-vs-2 over-count as run5); lowconf = same counts (4 / 1) and 0 split pairs; night = 0 vs 3 in both settings; zones_test person counts = run4 (3 vs 3, 4 vs 10). What v17 gave us is **diagnosis**: it ruled out tracking-id breaks as the cause in these two windows and pointed at X-CLIP labelling and detector misses. The lowconf settings were not adopted (no count benefit; vehicle count dropped 6-11%, unchecked).

### 15j. Why the last sbatch was run
Each job answers one question and none was expected to improve counts:
- `traj17_base` / `traj17_lowconf` (chunks 13, 22): do tracking breaks or ByteTrack's low-confidence pass explain the 12:45 over-count and the night misses? Answer: no (15g).
- `traj17_night_min04` (item 11, only if you submitted it): are the sub-second night boxes real riders? It is a **probe** (bicyclist minimum 0.4 s, pedestrian 1.0 s), not a candidate setting: at 14:00 a 0.4 s minimum would add up to 5 false bicyclists. Read it by watching 21:19:03, 21:22:07, 21:29:21, 21:29:29.
- Chunk 15 re-run with v17 (item 12): only to get speed/direction for the 5 filtered short pedestrian tracks at 14:00.
If you submitted something else, check with `squeue -u $USER -o "%i %j %T %M"` and the `--export` line in your shell history.

### 15k. All v17 window counts in one table (AI counts; GT = ground truth; "seen" = counted by eye in the clip)
| Window | Run (settings) | Bicyclists | Pedestrians | Vehicles | GT bic / ped | Seen in clip (bic / ped) |
|---|---|---|---|---|---|---|
| 12:45-13:00 | old run5 (min ped 1.0 s) | 4 | not stated per bin | n/a | 2 / not stated | |
| 12:45-13:00 | `traj17_base` (run4 settings, min 3 s) | 4 | 1 | 589 | 2 / not stated | 2 / 3 (1 ped on grass never detected; last ped counted as both ped and bicyclist) |
| 12:45-13:00 | `traj17_lowconf` | 4 | 1 | 552 | | |
| 21:15-21:30 | old `night_dc015` (det conf 0.15, min 3 s) | 0 | 0 | n/a | 3 / 7 | |
| 21:15-21:30 | `traj17_base` (min 3 s) | 0 | 0 | 285 | 3 / 7 | 5 / not counted |
| 21:15-21:30 | `traj17_lowconf` | 0 | 0 | 253 | | |
| 21:15-21:30 | `traj17_night_min04` (bic min 0.4 s, ped min 1.0 s) | 3 | 1 | 285 | 3 / 7 | 5 / not counted |
| 10:00-10:15 | not run (jobs cancelled on purpose) | | | | | |
| 14:00-15:00 (whole hour, v16, zones) | `zones_test` | 3 | 4 | 2268 | 3 / 10 | |

Reading: with the same settings v17 counts equal v16/run4/run5 (no count improvement; v17 adds outputs). The only setting that changed counts is the short night minimum (0 -> 3 bicyclists). Vehicle counts differ between base and lowconf (589 vs 552, 285 vs 253) and were not checked against any truth.

### 15l. Night re-run `traj17_night_min04` (21:15-21:30; clip watched 2026-10-05)
Counted tracks (log): bicyclists 3, pedestrians 1, vehicles 285. Split candidates: 1 pair, 0 would pass the 0.4 s minimum only if joined. Counted tracks by (X-CLIP label, direction): bicyclist/moving_right 2, bicyclist/toward_camera 1, pedestrian/moving_right 1.

| Track | Frames | Secs | Mean box h (px) | wtd X-CLIP bic / ped | Detector says cyclist | Final label | What the clip shows |
|---|---|---|---|---|---|---|---|
| 1 | 34263-34272 | 0.6 | 54 | 0.95 / 0.05 | 100% | BICYCLIST | real rider (9:19:05) |
| 2 | 39790-39810 | 0.4 | 93 | 0.99 / 0.01 | 100% | BICYCLIST | real rider (9:22:09) |
| 4 | 52789-52821 | 0.9 | 76 | 0.70 / 0.30 | 59% | BICYCLIST | real rider on sidewalk (9:29:24) |
| 7 | 53020-53045 | 1.0 | 75 | 0.41 / 0.59 | 100% | PEDESTRIAN | rider (clip label at 9:29:31 reads BICYCLIST, X-CLIP 0.62 / 0.38 on that frame; the final label uses the whole-track weighted score) |

Findings:
- The 3 bicyclist-labelled short tracks (1, 2, 4) are real riders, so the 3 s minimum was hiding real night riders. Track 7 is also a rider but was finally labelled pedestrian by weighted X-CLIP; the detector's 100% cyclist share was right. With track 7 counted as a rider the AI finds 4 bicyclists.
- **The clip shows 5 cyclists; the AI finds 4 at best, so at least 1 is still missed.** The detector draws a box at night but loses it as the rider gets close to the camera, so the track lasts about 1 s (screenshot 9:29:26: rider visible, no box). A tracker cannot join across a gap in which the detector sees nothing.
- The ground truth (3) is below what is visible (5). "AI 3 vs GT 3" is therefore not evidence of agreement; compare with what is seen in the video.
- Guess, not tested: close-up, top-down views are rare in the roughly 200 daytime training images.

### 15m. 14:00 short bicyclist-labelled tracks, detector share (from the `zones_test` log; filtered by the 3 s minimum)
| Track | Frames | Secs | wtd X-CLIP bic | Detector says cyclist | Watched? |
|---|---|---|---|---|---|
| 1 | 5514-5517 | 0.4 | 0.92 | 100% | no (14:03:03) |
| 2 | 5557-5655 | 1.1 | 0.85 | 3% | no (14:03:05-08) |
| 15 | 36766-36899 | 1.1 | 0.90 | 3% | no (14:20:26-31) |
| 24 | 47035-47044 | 0.6 | 0.82 | 100% | no (14:26:09) |
| 28 | 49476-49479 | 0.4 | 0.97 | 100% | no (14:27:30) |
Tracks 1 and 28 have only 2 X-CLIP scores each, so their X-CLIP values carry almost no information.

**Candidate rule (hypothesis, not implemented, not validated):** count a bicyclist track shorter than 3 s only if the detector calls it a cyclist at least about 90% of the time (and let the detector share override X-CLIP on such short tracks). Applied to the data above:
- Night: keeps tracks 1, 2 and 7 (7 becomes a bicyclist); drops track 4 (59%), which is a real rider. Net: 3 of 4 real short riders.
- 14:00: keeps tracks 1, 24 and 28 (100%), drops 2 and 15 (3%). Those three would raise 14:00 from 3 to 6 bicyclists against a GT of 3. Whether they are real riders (the GT may under-count as at night) is **unknown until the clip is watched**.
Do not implement before watching 14:03:03, 14:26:09 and 14:27:30 in the `zones_test` clip(s).

## 16. Estimated time to run all 48 hours (v17 script, current settings)
**Basis (measured, not extrapolated from guesses):**
| Measurement | Value |
|---|---|
| One full hourly file (`zones_test`, chunk 15, 14:00, 2268 vehicles) | 6884 s = 1.91 h on 1 GPU |
| One 15-min window (`traj17_*`, chunks 13 and 22, day and night) | 1703-1722 s = 28.7 min, i.e. about 1.9 h per hour |
| Frames per hour file | about 107,850 (29.97 fps) |
Runtime is nearly the same at day and night (night window 285 vehicles, day 589, both about 29 min), so cost is dominated by per-frame detection, not by how many objects are tracked.

**Total compute:** 48 h x 1.9 h = **about 92 GPU-hours** (about 3.8 GPU-days). This matches the earlier "block 1, 24 hours, about 46 GPU-hours". Allow +-20%: only 4 distinct hours were timed and X-CLIP time grows with the number of person tracks (busier hours, e.g. rush hour, may run longer).

**Wall-clock time depends only on how many GPUs run at once** (array tasks), plus queue wait:
| Concurrent GPUs | Wall time (approx.) |
|---|---|
| 48 (whole array at once) | about 2 h |
| 24 | about 4 h |
| 12 | about 8 h |
| 8 | about 12 h |
| 4 | about 23 h |
| 1 | about 3.8 days |
Not included: queue wait, the aggregation step (`aggregate_colonial_v13.py`, minutes), and the time to watch clips. `--time=05:00:00` per task leaves 2.6x margin over the 1.9 h measured. Disk use of 48 hours of annotated clips plus the new v17 CSVs (`_trajectories.csv` has one row per track per frame) was **not measured**; check `du -sh annotated/traj17_base counts/traj17_base` first.

**Recommendation (unchanged from section 9):** do not run all 48 hours yet. The result would be a larger version of the same night and pedestrian failures. Run block 1 (24 h, about 46 GPU-hours) only after the hand labels, the night fine-tuning and the label-fusion decision. Command when ready (new RUN name, v17 files, zones on):
```bash
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
sbatch --time=05:00:00 --export=ALL,RUN=full_b1,ZONES_JSON=$PWD/zones/colonial_north_v1.json --array=1-24 code/run_xclip_colonial_v17.slurm
sbatch --time=05:00:00 --export=ALL,RUN=full_b2,ZONES_JSON=$PWD/zones/colonial_north_v1.json --array=25-48 code/run_xclip_colonial_v17.slurm
```
To cap concurrency (fair-share), append `%8` to the array, e.g. `--array=1-24%8`.

## 17. Wording: "trajectory" (past vs future)
In tracking literature a **trajectory (track)** is the *recorded past path* of an object: the sequence of positions from first to latest frame. What we draw (fading trail behind the person, arrow head and dot at the newest point) is exactly that, so it is correct to see the line following the person. **Trajectory prediction** is a different task: forecasting future positions; it is not implemented here and the arrow is not a prediction. In this project: `_trajectories.csv` = past positions per frame; `_track_motion.csv` = summary of that path (net distance, speed, direction).

## 18. Fine-tuning plan (night + close-to-camera); nothing trained yet
Goal: fix the two detector losses seen in 15l: no box at night, and the box vanishing as a rider nears the camera.
**Data, in order of expected value:**
1. **Colonial frames, labelled by hand** (same camera, same view): night frames and close-to-camera frames of riders and pedestrians. Take them from hours **other than 21:00**, so that the 21:00 hour stays a clean held-out test (the only night hour validated so far).
2. **NightOwls** (night pedestrian dataset; Roboflow Universe has a ~1,500-image subset under CC BY 4.0; the full set needs registration on its site). Limits: people taller than 50 px only, different cameras, and **no car/truck/bus labels**.
**Risks to handle:**
- Training only on NightOwls would teach the detector that cars/trucks/buses in those images are background and could hurt vehicle detection. Always train on NightOwls **mixed with the existing rtdetr_v3 training set** (which has vehicle labels), starting from the `rtdetr_v3` weights, and re-check vehicle counts afterwards.
- Class mapping needed (pedestrian -> person, bicycledriver -> cyclist, others dropped); check the exported class names before mapping.
- Test on whole held-out hours, day and night, so that daytime does not get worse.
**Blocked on:** `args.yaml` of the `rtdetr_v3` run and the dataset yaml (so the new training reuses the same settings), and a GPU job on HiPerGator (no training can run in this chat).
```bash
cat /orange/xiangyan/rithika/vision/vision3/runs/detect/finetune_runs/rtdetr_v3/args.yaml
```

## 19. Experiment: fine-tune with NightOwls (`rtdetr_v4_night`), result: worse, not adopted
**What was done (new files only; `rtdetr_v3`, v17 script and slurm untouched):**
- `code/build_merged_dataset_v1.py`: base `roboflow_split_v1` train (437 images, repeated x3) + 400 random NightOwls images (Roboflow `nightowls-koyno`, YOLOv8 export, licence CC BY 4.0 per its data.yaml; classes bicycledriver->cyclist, pedestrian->person, `ignore` dropped) -> `dataset_frames/merged_night_v1/`. Train boxes per class: car 3390, person 759, cyclist 164, truck 102, bus 24, other_vehicle 24.
- `code/train_rtdetr_night_v1.py` + `.slurm`: start from `rtdetr_v3/best.pt`, AdamW lr0 1e-4, imgsz 640, batch 8, seed 42, up to 50 epochs, patience 15 -> `runs/detect/finetune_runs/rtdetr_v4_night` (stopped at epoch 47, 55 min).

**Daytime validation (54 images, 218 instances; only 8 cyclists, 8 persons, 6 trucks, so noisy):** car mAP50-95 0.763 -> 0.758, cyclist 0.947 -> 0.945, person 0.345 -> 0.312, truck 0.074 -> 0.230, all 0.532 -> 0.561 (gain comes from 6 truck instances). Conclusion: this val set cannot show a night effect and showed no daytime damage.

**Real windows (same settings as the reference runs; only WEIGHTS changed):**
| Window | rtdetr_v3 reference | rtdetr_v4_night |
|---|---|---|
| 21:15-21:30, bicyclists / pedestrians / vehicles (min 0.4 s / 1.0 s) | 3 / 1 / 285 (`traj17_night_min04`) | 0 / 0 / 141 (`traj17_night_v4`, job 44890080) |
| 12:45-13:00, bicyclists / pedestrians / vehicles (min 3 s) | 4 / 1 / 589 (`traj17_base`) | 1 / 1 / 350 (`traj17_day_v4`, job 44890081) |
Seen by eye: night 5 cyclists (GT 3), day 2 bicyclists + 3 pedestrians (GT 2 bicyclists).

**Why it failed at night (log of `traj17_night_v4`):** the person-track table has a single track of 2 frames (0.1 s, never scored). Raw detector detections (conf >= 0.25): car 10620, cyclist 18, truck 74, person 1, other_vehicle 5. So the **detector itself stopped finding the riders** (tracker/filters are not the cause). Same line from the v3 run (`traj17_night_min04`, job 44875534), raw detections (conf >= 0.25, counted per frame) v3 -> v4: car 82472 -> 10620 (-87%), truck 1947 -> 74 (-96%), person 106 -> 1 (-99%), cyclist 132 -> 18 (-86%), bus 14 -> 0, other_vehicle 5 -> 5. **Every class collapsed, not only riders.** Counted vehicles fell less (285 -> 141) because tracks persist across frames. A drop this uniform looks like a general loss of detector confidence at night (scores below 0.25) rather than a class-specific problem; untested way to check: rerun `traj17_night_v4` with `DET_CONF=0.10` and see whether the riders reappear (even if they do, v4 is still not better than v3 at the 0.25 setting).
**Vehicles dropped 41-51%.** Hypothesis (not proven): NightOwls images have no car/truck/bus labels, so the model learned to treat unlabelled vehicles as background. The rider loss is not explained by that hypothesis; a domain gap (NightOwls camera angle, rider size, lighting) is another possibility. Not tested.

**Decision:** v4 is not used. Pseudo-labelling vehicles on NightOwls (run v3 on the images and add its car/truck/bus boxes) would address only the vehicle part and does not address the rider loss, so it is not the next step. Next: (a) the v18 short-track rule on v3 (needs the 14:03:03, 14:26:09, 14:27:30 clips watched first), (b) hand-label Colonial night and close-to-camera frames from hours other than 21:00 (same camera view), then retrain from v3 on base + those frames only, test on 21:15 and 12:45.

## 20. v18: separate day and night settings (code written and run 2026-10-06)
**Why.** Section 15l: a 0.4 s bicyclist minimum finds the real night riders (0 -> 3), but section 15m: the same minimum at 14:00 could add up to 5 unchecked short tracks to 3 counted (GT 3). So the short minimum should apply only at night, and 3 s should stay by day. Tried before: lower detector confidence alone (`night_dc015`, no change), looser tracking (`traj17_lowconf`, no change), short minimum alone (`traj17_night_min04`, 3 cyclists). Never tried: low confidence + short minimum together, or both settings in one run.

**20a. What was built (new files; v17 untouched).**
| File | What |
|---|---|
| `code/xclip_overlay_v18_colonial.py` | v17 + options `--night-start HH:MM --night-end HH:MM` (may cross midnight) and `--night-det-conf`, `--night-bic-min-sec`, `--night-ped-min-sec`. Omitted night values fall back to the day values. All unset = identical to v17 |
| `code/run_xclip_colonial_v18.slurm` | v17 slurm + env vars `NIGHT_START NIGHT_END NIGHT_DET_CONF NIGHT_BIC_MIN_SEC NIGHT_PED_MIN_SEC` (only passed if `NIGHT_START` is set) |
| `code/submit_day_night_v1.sh` | submits the test below |
How it works: detector confidence switches per frame by the clock time of that frame. A track counts as night if the clock time of its MIDDLE frame is in the night period; then the night minimum seconds apply (bicyclist or pedestrian, by X-CLIP's label). The night log line `night mode ON ...` is printed at the start of a run.
Checked: `py_compile` of the script, `bash -n` of both shell files, and the night-period logic at the boundaries (20:59 day, 21:00 night, 06:00 day, crossing midnight). **Not tested with the real RT-DETR + X-CLIP on the cluster.** If a job fails, send the last 20 lines of its log.

**20b. The test (10 jobs, about 30 min each, about 5 GPU-hours).** Two runs on the same five 15-minute windows:
- `sw_day`: no night mode (3 s, detector conf 0.25 everywhere; same as `traj17_base`).
- `sw_switch`: night mode 21:00-06:00 with `NIGHT_DET_CONF=0.15`, `NIGHT_BIC_MIN_SEC=0.4`, `NIGHT_PED_MIN_SEC=1.0`; day settings outside that period.
| Window | Chunk | Frames (START / STOP) | Purpose |
|---|---|---|---|
| 10:00-10:15 | 11 | 1 / 26973 | day, cyclists + pedestrians |
| 12:45-13:00 | 13 | 80924 / 0 | day, the 4-vs-2 over-count bin |
| 14:00-14:15 | 15 | 1 / 26973 | day, contains the short 'cyclist' tracks at 14:03 |
| 21:15-21:30 | 22 | 26978 / 53946 | night; the window the night settings were picked on (a gain here is not proof) |
| 22:00-22:15 | 23 | 1 / 26973 | night; NOT used to pick the settings (the fair test; GT for this bin is not in this README, compare with the GT file) |
Night settings are my picks from the earlier probes, not tuned together. Only 21:00 has been verified as dark; dusk and dawn are unchecked (`NIGHT_START/NIGHT_END` can be changed). Lower confidence also applies to vehicle detections at night, so night vehicle counts can change (not checked against any truth).

**20c. How to read it (when the jobs finish).**
```bash
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
grep -i "night mode" logs/slurm_colonial_v18_*.log      # sw_switch logs only
tail -n 25 logs/slurm_colonial_v18_*.log                 # counts and Split candidates lines
ls counts/sw_day counts/sw_switch; ls annotated/sw_day annotated/sw_switch
```
1. **Day windows (10:00, 12:45, 14:00): counts must be identical in `sw_day` and `sw_switch`.** If not, the switch is leaking into day: stop and debug.
2. **Night windows:** compare bicyclists / pedestrians / vehicles, `sw_day` vs `sw_switch`, against GT and against what is seen in the clip (21:15 clip shows 5 cyclists, GT 3). Watch the 21:15 and 22:00 clips in both runs.
3. **22:00 is the test that counts.** Judge by eye in the clip plus the GT; false boxes at night would show as boxes on non-people.
4. Report what was seen in the clips, not only GT agreement: GT is imperfect (section 6, 15l).

**20d. Results (runs finished 2026-10-06; counts from the slurm logs, each run 29-30 min).**
| Window | `sw_day` bic / ped / veh | `sw_switch` bic / ped / veh |
|---|---|---|
| 10:00-10:15 | 0 / 0 / 441 | 0 / 0 / 441 |
| 12:45-13:00 | 4 / 1 / 589 | 4 / 1 / 589 |
| 14:00-14:15 | 1 / 2 / 612 | 1 / 2 / 612 |
| 21:15-21:30 | 0 / 0 / 285 | 3 / 1 / 279 |
| 22:00-22:15 | 0 / 0 / 467 | 0 / 0 / 464 |
- **Day stays at 3 s:** the three day windows have identical counts AND identical person-track tables in both runs (the switch does not leak into day). At 14:00 the 0.4 s and 1.1 s 'cyclist' tracks (frames 5514-5517 and 5557-5655) are still filtered.
- **21:15:** `sw_switch` counted 3 bicyclists (tracks of 0.6, 0.5, 1.0 s) + 1 pedestrian (1.1 s, detector says cyclist in 100% of frames). Same as the earlier `traj17_night_min04` probe. **Section 21 shows one of the 3 'bicyclists' is a motorcycle, so '3 vs 3 human' is partly a coincidence, not a clean match.**
- **22:00:** 0 in both runs; two short tracks (0.4 s, 0.5 s) were labelled pedestrian and filtered by the 1.0 s pedestrian minimum; one of them has detector = cyclist in 100% of frames. Visual truth for this window: see section 21 (not yet reviewed if not listed there).
- **Detector confidence 0.15 did little for people**: person tracks at 21:15 are almost the same as baseline; raw car detections rose from 82k to 140k, final vehicles 285 -> 279. The short minimum did the work.
- **Log label bug (not fixed yet):** in night mode the line 'Raw detector detections by class (conf>=0.25)' actually counts detections down to 0.15.

## 21. Rithika's own observations from watching the annotated clips (2026-10-06): VISUAL GROUND TRUTH
**Use this section as the ground truth for these clips; do not ask for it again.** These come from watching the mp4s by eye (the human counts in the GT file are known to be inconsistent, section 6 and 15l). Where this conflicts with my earlier notes from reading logs (15l, 15m), this section wins. Wording is hers, lightly tidied; nothing here was inferred from logs unless marked.
| Clip | What she saw |
|---|---|
| `sw_day` 12:45-13:00 (same for `sw_switch`, identical counts) | 2 cyclists and 3 pedestrians really present. The model called **2 pedestrians cyclists** (so the 4 counted bicyclists = 2 real + 2 pedestrians). A pedestrian walking on the grass was not counted. Screenshot of id 1: 'FINAL: BICYCLIST', RT-DETR person 0.55 (45% cyclist) DISAGREE, X-CLIP bicy 0.74 / pede 0.26, a person walking on foot near the road edge. (The 45% cyclist, id 1 matches the 12:45:40 track in the log; that matching is mine.) This resolves the 'which 2 of the 4 are real' question left open earlier: the 2 mislabelled ones are pedestrians. |
| `sw_day` 14:00-14:15 | A pedestrian walking away from the camera was not counted. 1 cyclist seen. 1 pedestrian was counted as a cyclist. 2 pedestrians were not detected at all. (Her follow-up, 2026-10-06: yes, the real cyclist AND a pedestrian were both labelled cyclist. The log has only ONE counted bicyclist (track 5, 4.0 s, frames 16521-16717, about 9:11 in the clip) plus two FILTERED 'was BICYCLIST' tracks at 14:03 (0.4 s frames 5514-5517 and 1.1 s frames 5557-5655, about 3:04-3:09). So most likely the real cyclist = the short filtered 14:03 tracks (dropped by the 3 s minimum, i.e. a fast rider can be lost by day too) and counted track 5 = the pedestrian labelled cyclist. That mapping is MY inference from her answer, not something she stated: verify at those two times.) **CORRECTION 2026-10-08 (her truth file): that inference was WRONG.** Her truth file says the 4.0 s track at 9:11-9:17 (counted BICYCLIST) IS the real cyclist (correct), and the short 0.4 s + 1.1 s tracks at 3:04-3:08 are a PEDESTRIAN that the model called a bicyclist. Her totals for the 14:00 clip: 4 pedestrians + 1 cyclist (a pedestrian walking away at 3:02, the pedestrian above at 3:04-3:08, and 2 pedestrians never detected at about 12:12). So there is NO evidence at 14:00 that the 3 s minimum loses a real fast cyclist; and the two model-counted pedestrians (3:15-3:18 and 11:45-12:17) are not in her total: unresolved (false detections, or the same people?) **RESOLVED 2026-10-08 (her answer): both are real.** FINAL 14:00 TRUTH (video position, also in `truth/day_1400_truth.csv`): (1) cyclist 9:10-9:19 = the 4.0 s track, counted correctly; (2) pedestrian 3:00-3:25, walking away and VERY far from the camera = the 0.4 s + 1.1 s tracks at 3:04-3:08 (called BICYCLIST, filtered, so no false count) AND the 3.2 s track at 3:15-3:18 (counted PEDESTRIAN); (3) pedestrian 11:45-12:14 = the 16.9 s track (counted PEDESTRIAN); (4) and (5) two pedestrians arriving together 12:10-12:37, mostly not detected; the two filtered 2.1 s and 1.2 s PEDESTRIAN tracks at 12:29-12:35 probably belong to them. So the `sw_day` baseline at 14:00 = cyclist 1/1 found, pedestrians 2/4 found, 2 detected but dropped by the 3 s minimum, 0 false people (preview computed from the log times, +-1 s). |
| `sw_day` 21:15-21:30 (she wrote '1215-1230'; CONFIRMED by her 2026-10-06: it is 21:15-21:30) | 3 cyclists, 1 motorcycle and 1 pedestrian present; **none were detected/counted** (log: 0 / 0). |
| `sw_switch` night clip (window not stated, presumably 21:15-21:30) | A **motorcycle was detected but labelled cyclist**. A cyclist was detected but the box did not follow the cyclist throughout. A cyclist was missed. A cyclist was counted. A cyclist was detected but labelled pedestrian. The last pedestrian was not detected. |
What this changes:
- At 21:15 the 3 'bicyclists' of `sw_switch` include a motorcycle, so the short-minimum rule can let a motorcycle in as a cyclist (a new error type, not seen before).
- At 21:15 the people present are 3 cyclists + 1 motorcycle + 1 pedestrian (the older '5 cyclists' note counted the motorcycle and pedestrian as cyclists).
- Pedestrian misses are mostly **detector** misses (never detected), not tracking or label misses: grass at 12:45, walking away from camera at 14:00, last pedestrian at night.
- Pedestrians labelled cyclist is the main daytime error at 12:45 (2 of 4 'cyclists').
- 14:00 final (see the correction above): the two late pedestrians (12:29-12:35) ARE tracked but only for 2.1 s and 1.2 s, so the 3 s PEDESTRIAN minimum drops them. No experiment in v19 tests a shorter pedestrian minimum (`exp3b_short` is cyclist-only): candidate for a later run.
- Not yet reviewed: `sw_day` 10:00-10:15 and `sw_switch` 22:00-22:15 (22:00 counted 0 in both runs; is there a real rider at about 10:04 / 10:12 in the clip?).

## 22. PLAN: experiments to fix the failures seen in section 21 (written 2026-10-06 for review; NO CODE WRITTEN YET)
Source: Rithika's request to try several SOTA ideas on two 15-minute clips (one night, one day), combining (a) an outside plan she pasted (SAHI, temporal detector, low-light enhancement, fine-tuning, BNE-DETR) and (b) my own suggestions (motion candidates, speed-based relabelling, motorcycle guard, tracker gap-bridging, night augmentation). Fallback she stated: if nothing works, add her annotated images (fine-tuning, experiment E4).

**22a. Principle.** `rtdetr_v3` + the current v17 pipeline is the CONTROL. Change ONE thing at a time, run it on exactly the same clips, record which failure from section 21 it fixes or breaks. Only after that, combine the winners. Reason: so far every result has been a count; a count can look right for the wrong reason (21:15 'bicyclists 3 vs 3 human' included a motorcycle).

**22b. Test clips.**
| Role | Clip | Why | Status |
|---|---|---|---|
| Night | 21:15-21:30 (chunk 22, frames 26978 / 53946) | full visual truth known (3 cyclists, 1 motorcycle, 1 pedestrian, section 21) | proposed, confirm |
| Day | 14:00-14:15 (chunk 15, frames 1 / 26973) | contains: pedestrian walking away (missed), 2 pedestrians never detected, a pedestrian labelled cyclist, [older note, WRONG, see section 21 correction: the 14:03 short tracks are a pedestrian, not a lost cyclist] | proposed, confirm (alternative: 12:45-13:00, which has the grass pedestrian and 2 pedestrians labelled cyclist) |
- **Controls already run, no need to rerun:** `sw_day` (= v17 settings) and `sw_switch` (= v18 night rule) on both clips (counts in 20d).
- **Overfitting warning:** two clips that were studied by eye are a development set, not a test set. Anything that wins is 'promising', not 'proven'. Keep untouched windows for a later check: 22:00-22:15 (already exists, unreviewed) and one more day window (to choose, e.g. 10:00 or 16:00).
- **Rule for E4 (fine-tuning):** never train on frames from the two test clips (or the hold-out windows). Take training frames from other hours/days. If the only labelled frames are from the test clips, say so and report the result as 'trained on the test clip', not as a test.

**22c. Truth file and metrics (new).** One file per clip, `truth/<clip>_truth.csv`, one row per real person/vehicle, written by Rithika from watching the clip:
`id, start_mmss, end_mmss, class (cyclist | pedestrian | motorcycle), where/direction, notes`
- Pre-fill from section 21. 21:15: 3 cyclists + 1 motorcycle + 1 pedestrian (times to add). 14:00: only partial (walking-away pedestrian, 2 undetected pedestrians, 1 cyclist, 1 pedestrian labelled cyclist, counted pedestrians): she must complete the list.
- For every run record, per clip: true people found (by class), missed, wrong class, motorcycles counted as cyclists, false boxes (non-people), and the counts. Precision/recall only once the truth file is complete. A time-overlap matcher (`eval_truth.py`, to be written) compares `*_tracks.csv` with the truth file; no mAP needed.
- Record GPU time per run (baseline: about 29-30 min for one 15-min window).

**22d. Experiments.** Order is by cost and by how directly it hits a section 21 failure.
| ID | What changes | Question | Training | Notes / risk |
|---|---|---|---|---|
| E0 | nothing (`rtdetr_v3`, v17 settings) | what are the current errors? | no | CONTROL. Also keep `sw_switch` as control 0b |
| E1 | SAHI: slice each frame, detect per slice, merge (with the full-frame pass kept) | does slicing recover small/far people (walking away, grass, night)? | no | Wrapper around the same weights; SAHI documents an RT-DETR mode and a full-image pass in addition to the slices. Cost: several times more forward passes per frame, so runtime goes up by roughly the number of slices (restrict to the road zones to cut it). Risk: duplicate boxes / more false boxes; check big close cyclists are not hurt |
| E2 | low-light enhancement before the same detector, night clip only | does brightening recover night people? | no at first | Order: gamma/contrast (CLAHE) as a sanity test, then Zero-DCE/Zero-DCE++ (as suggested in the pasted plan; not checked by me). Judge by 'were missed people boxed', NOT by how the video looks. Risk: noise and headlight glare create false boxes |
| E3 | motion candidates + post-rules (my addition) | can motion and speed fix wrong labels and find moving people the detector misses? | no | (a) frame-difference / background-subtraction blobs inside the road zones as extra candidates; (b) R1: relabel by speed/direction from `track_motion.csv` (walker slow, rider faster, motorcycle fastest); (c) R2: motorcycle guard (speed/size ceiling before a night short-track counts as a cyclist); (d) R3: day exception for short, fast, high-confidence cyclist tracks (the 14:03 case). Literature: motion-difference maps fused into a detector (YOLOMG, 2025), flow-aligned multi-frame features for micromobility (Montréal, 2024). Limit: weak for slow walkers and for walking AWAY from the camera. Needs a calibration of speed thresholds on hand-labelled tracks (small sample) |
| E4 | fine-tune `rtdetr_v3` on Colonial hard cases | can the model learn this camera? | YES | Output `rtdetr_v5_colonial`. Add a motorcycle class. Hard cases: DAY: walking away, tiny/far pedestrian, tiny/far cyclist, close cyclist, motorcycle, pedestrian mistaken for cyclist, shadow/grass. NIGHT: cyclist, pedestrian, motorcycle, far, close, partially visible. Optional night augmentation of day frames (training-free NightAug-style, or day-to-night translation that keeps the labels). Lesson from the NightOwls attempt (section 19): train on THIS camera's failures, not other cameras. Highest expected value, and the stated fallback |
| E5 | temporal detector on stacks of frames | does history keep people from 'disappearing'? | YES (heavy) | Corsel et al., WACV Workshops 2023: YOLOv5-based, processes frame sequences from static cameras, two-stream variant uses frame differences; they report tiny moving objects down to 4x4 px. A separate branch, not a replacement. Needs labelled sequences, so do after E4. Context R-CNN (per-camera memory) is an alternative. I did not verify the other numbers in the pasted plan (Temporal-YOLOv8 '+0.21 mAP', FAIM '87.9% mAP'): do not quote them |
| E6 | BNE-DETR (night RT-DETR variant) vs best model, night only | does a night-specific architecture beat ours? | YES | MDPI Sensors 2026, 26(1):260, visible light, tested on LLVIP: +1.9 precision, +2.5 recall, +1.9 mAP50 over RT-DETR-R18. LLVIP is a pedestrian-only, night-only dataset; ours is multi-class (pedestrian, cyclist, motorcycle, vehicles), so treat it as a research benchmark, not a drop-in. To be fair it must be trained on our data like E4 |
| E7 | tracker gap-bridging with a mask tracker (my addition) | can lost boxes be continued (the cyclist whose box did not follow)? | no | SAMURAI (SAM 2 + motion-aware memory, zero-shot). Made for single-object tracking benchmarks; not tested on tiny night video. Trial only |
| E8 | COMBINE only the winners | do gains stack? | depends | LAST. Possibly different pipelines for day and night |

**22e. Phases.**
1. No training: E0 (already run), E1 SAHI, E2 enhancement (night), E3 motion + rules.
2. Data/model: build the hard-case annotations, E4 fine-tune, test on untouched windows.
3. Temporal: E5 (and E7 if still needed).
4. Night architecture benchmark: E6 vs the best of E4.
5. Ablation and combination (E8), with the untouched windows.

**22f. What counts as a win.** Per clip, compare to the control with the truth file: more true people found without more false boxes or class errors. With two clips this is anecdotal, so report results as 'promising' until the hold-out windows agree. Report failures too (what got worse).

**22g. Honest caveats.** (1) Only two clips, both studied by eye. (2) The v18 night rule may be redundant if E4/E5 recovers the people. (3) SAHI and enhancement may add false boxes at night (headlights, noise). (4) Walking-away pedestrians are small, slow and low-resolution; motion cues may not help them, only SAHI or fine-tuning might. (5) The human counts are known to be inconsistent (section 6), so judge by the truth file, not the count file.

**22h. Questions to confirm before any code is written.**
1. Day clip: 14:00-14:15 (proposed) or 12:45-13:00?
2. Night clip: 21:15-21:30 (proposed). OK to keep 22:00-22:15 as an untouched hold-out?
3. Will you fill in the truth files for both clips (time + class per person)? 21:15 is almost complete, 14:00 is not.
4. SAHI: OK to start with 640x640 slices, 20% overlap, plus the full-frame pass, limited to the road zones?
5. Count motorcycles as their own class in outputs from now on (they are neither cyclists nor vehicles in the counts)?
6. GPU budget: E1 will take several times the baseline 30 min per clip.
7. Name/version for the code: new files (e.g. `xclip_overlay_v19_colonial.py` with SAHI/enhancement flags, `eval_truth.py`, one submit script per experiment); v17 and v18 stay untouched.

**22i. What gets written after approval (nothing yet).** v19 script with `--sahi`, `--enhance {none,clahe,zerodce}` and an optional motion-candidate/rule module (all off by default so counts equal v17/v18); `eval_truth.py`; `submit_exp_v1.sh` running E1-E3 on the two clips; later the E4 training script and dataset-export script that excludes the test clips.

## 23. v19: experiment code for E1-E3 (written 2026-10-08; unit-tested off-cluster only, NOT yet run on the cluster)
**23a. Decisions taken for Rithika (she said: if unsure, do what research suggests).**
- Clips: NIGHT 21:15-21:30 (chunk 22, frames 26978-53946) and DAY 14:00-14:15 (chunk 15, frames 1-26973). 22:00-22:15 stays an untouched hold-out and is NOT in this batch.
- Motorcycles count as cyclists for now: truth class `motorcycle` is scored as `cyclist`; no motorcycle guard is applied (the audit file only records speed so one can be added later).
- SAHI is implemented in the script itself (slice + full-frame pass + duplicate merge), not through the `sahi` package: same method, no new dependency, identical output format. 640 px slices, 20% overlap over the WHOLE frame (people also walk on grass outside the zones), 8 slices + 1 full pass per frame = about 3x the baseline detector cost. People only: vehicles still come from the full-frame pass, so vehicle counts are not confounded.
- Enhancement is applied to the frame given to the DETECTOR only, and only to night frames. X-CLIP crops stay original (add `ENHANCE_CROPS=1` to change that). Zero-DCE uses the official `Epoch99.pth` (320 KB, shipped in the bundle; layer names checked against the checkpoint).
- Speed rule thresholds are my physical estimates, NOT calibrated: walker < 1.0 body heights/s, rider > 2.0 (a synthetic check gave a 1.4 m/s walker 0.8 and a 5 m/s rider 2.9). The rule only relabels when the DETECTOR also disagrees with X-CLIP, and only for tracks visible >= 1.5 s. `*_rules_audit.csv` prints every track's real speed so the thresholds can be corrected from data.
- Short rule (NOTE 2026-10-08: at 14:00 the 14:03 short tracks are a PEDESTRIAN labelled cyclist, so `exp3b_short` is expected to ADD a false bicyclist there; that is now a test of whether the rule is safe, not an expected gain): a track under the minimum duration is counted as BICYCLIST if it lasted >= 0.3 s, the detector calls it cyclist in >= 90% of its frames and the weighted X-CLIP bicyclist probability is >= 0.9. (From the 14:03 and night tracks in section 15; applies day and night.)
- Motion diagnostic (MOG2 background subtraction at half resolution): blobs of person/vehicle size that NO detection box explains, grouped over time (>= 0.7 s). Diagnostic only; it never changes a count. Headlight beams and shadows will show up too: look at the contact sheet.

**23b. NOT in this batch.** E4 fine-tuning (needs the hard-case annotations; fallback she named), E5 temporal detector, E6 BNE-DETR, E7 SAMURAI, E8 combination. These need labelled data, training or other repositories. Next step for E4: label hard-case frames from OTHER hours/days (never from the two test clips), then the training script is written.

**23c. What to run (single command, then look back).** Files: `colonial_v19_bundle.tar.gz` (contains code/ and truth/).
```bash
# on your own computer (replace YOURUSER):
scp colonial_v19_bundle.tar.gz YOURUSER@hpg.rc.ufl.edu:/orange/xiangyan/rithika/vision/vision3/best/test_colonial/
# on HiPerGator:
ssh YOURUSER@hpg.rc.ufl.edu
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
tar xzf colonial_v19_bundle.tar.gz            # puts files in code/ , code/zerodce/ , truth/  (truth files are overwritten only if you re-extract!)
bash code/run_all_experiments.sh              # submits 11 jobs + 1 evaluation job, writes exp_results/MANIFEST_<time>.md
squeue -u $USER -o "%i %j %T %M"              # watch them
nano truth/night_2115_truth.csv ; nano truth/day_1400_truth.csv      # fill in while the jobs run
# when everything has finished (the evaluation job also does this by itself, but the truth files must be filled in first):
python code/eval_truth.py --root . --prefix exp
```
Re-run later without overwriting: `bash code/run_all_experiments.sh v2` (run names get `_v2`). Optional self-test of the helper functions (no GPU): `python code/test_v19.py`.

**23d. The jobs (11, each one change on the same clips).** exp0_base (night+day, + motion diagnostic) - exp1_sahi (night+day, 4 h limit) - exp2_gamma, exp2_clahe, exp2_zerodce (night only) - exp3a_speed, exp3b_short (night+day). Expected runtime: about 30 min each, SAHI longer; about 8-10 GPU-hours in total. Controls that already exist: `sw_day` (v17 settings) and `sw_switch` (v18 night rule) on the same clips. REGRESSION CHECK: `exp0_base` must reproduce `sw_day`: night 0 / 0 / 285 (bic / ped / veh), day 1 / 2 / 612. If not, v19 has a bug: stop and report.

**23e. Where to look.**
- Clips: `annotated/<run>/Standard_SCU8OG_2019-07-10_0000.022/` (night) and `.015/` (day), one mp4 per run.
- Per run, in `counts/<run>/`: `*_tracks.csv`, `*_rules_audit.csv` (per track: X-CLIP label, detector %, speed in body heights/s, what each rule would do), `*_track_motion.csv`; exp0 also `*_motion_candidates.csv` and `.png`; exp2 also `*_enhance_preview.png` (original | enhanced).
- `exp_results/EVAL_<time>.md`: per run and clip, per truth person FOUND / WRONG CLASS / DETECTED BUT NOT COUNTED / MISSED, plus EXTRA counted tracks, plus which motion candidates overlap the people nobody found.
- `exp_results/MANIFEST_<time>.md`: job ids, flags, paths (for looking back).

**23f. What was and was not checked.** Checked off-cluster: Python syntax and undefined names; slice coverage; duplicate merge (cut-off copies dropped, a person straddling a slice edge kept whole); gamma/CLAHE brighten a dark frame; speed in body heights/s for a walker and a rider; the motion diagnostic on a synthetic video; the evaluator on synthetic tracks; the submit script with a fake `sbatch`; the Zero-DCE checkpoint's layer names and shapes. NOT checked (no GPU/torch/ultralytics here): a real run of the detector with slicing, the Zero-DCE forward pass on real frames, real MOG2 behaviour on this camera, and every number above. If a job crashes, send the last 20 lines of its slurm log.

**23g. Honest caveats.** (2026-10-08: with the final 14:00 truth the expected baseline score is cyclist 1/1, pedestrians 2/4, 0 extra; the two missed late pedestrians are DETECTED BUT NOT COUNTED because of the 3 s minimum, and none of the E1-E3 runs targets pedestrians' minimum duration.) Two clips studied by eye are a development set; any win is 'promising' until the 22:00 hold-out and another day window agree. Evaluation matches by TIME only; two people on screen at once can be confused. The truth files must list EVERY person, otherwise real people show up as EXTRA. SAHI and enhancement can add false boxes at night (headlights, noise). The speed thresholds are unverified.

**23h. Results of the v19 batch (run 2026-10-08, evaluator output `exp_results/EVAL_20261008_0830.md`).**
Regression check PASSED: `exp0_base` reproduces `sw_day` (night 0 bic / 0 ped; day 1 bic / 2 ped). Runtimes: baseline about 30 min, SAHI 42-43 min (+40%, far less than the 3x I estimated), others 28-35 min.
**Truth files at the time of the run.** DAY (final, 1 cyclist + 4 pedestrians): complete. NIGHT: only 4 usable rows, all scored as cyclist (n1 = motorcycle at 4:03, n2 7:07, n3 14:21, n4 14:29); rows n5 (14:23, the missed cyclist) and n6 (14:53, the undetected last pedestrian) were SKIPPED because the end-time column was left out. Night results are therefore incomplete (no pedestrian row at all). Also unresolved: the 4 scored rows + n5 would be 5 cyclist/motorcycle, but her earlier note says 3 cyclists + 1 motorcycle (= 4) + 1 pedestrian. Fix the two rows, then re-run only `python code/eval_truth.py --root . --prefix exp` (no GPU).
| run | night: cyclists found (of 4) / wrong class / not counted / extra | day: cyclist found (of 1), pedestrians found (of 4) / wrong class / not counted / extra | counted bic/ped night, day |
|---|---|---|---|
| exp0_base | 0 / 0 / 4 / 0 | 1, 2 / 0 / 2 / 0 | 0/0, 1/2 |
| exp1_sahi | **2** / 1 / 1 / **1** | 1, 2 (the two LATE pedestrians d4 and d5) / **2** / 0 / 0 | 3/1, 3/2 |
| exp2_gamma | 0 / 0 / 3 / 0 (+1 missed) | not run | 0/0 |
| exp2_clahe | 0 / 0 / 4 / 0 | not run | 0/0 |
| exp2_zerodce | 0 / 0 / 4 / 0 | not run | 0/0 |
| exp3a_speed | 0 / 0 / 4 / 0 | **0** (the real cyclist relabelled PEDESTRIAN), 2 / **1** / 2 / 0 | 0/0, 0/3 |
| exp3b_short | **2** / 0 / 2 / 0 | 1, 2 / 0 / 2 / **1** | 2/0, 2/2 |
What each run showed (all on 2 clips; 'promising', not proven):
- **E1 SAHI:** makes tracks much longer. Night: the riders' tracks went from 0.43-0.9 s to 5.24 s and 3.47 s, so two now pass the 3 s minimum with no rule. Day: the two late pedestrians (2.1 s and 1.2 s before) become 22 s and 3.5 s tracks and are counted. BUT the labels get worse: on the day clip two pedestrians (3:00-3:25 and 11:45-12:14, detector says person in 94-98% of frames) are now counted as BICYCLIST (X-CLIP), so day counts go 1/2 -> 3/2 against a truth of 1/4. Night: one rider labelled pedestrian, and one EXTRA counted cyclist at 14:44-14:59 (10.6 s; may be the undetected pedestrian of row n6 at 14:53, to be checked once n6 is fixed). So SAHI moves the bottleneck from detection and duration to the X-CLIP label.
- **E2 enhancement (gamma, CLAHE, Zero-DCE):** no gain. Night tracks stayed under a second, CLAHE and Zero-DCE made them shorter (0.07-0.67 s) and gamma lost one rider entirely. Not adopted. (Single clip, single threshold.)
- **E3a speed rule (defaults 1.0 / 2.0 body heights/s, UNcalibrated): harmful.** It turned the real 9:10 cyclist (detector: cyclist in 34.7% of frames) into a pedestrian; it fixed nothing. Needs calibration from `counts/exp3a_speed/*_rules_audit.csv` (speed per track) before any further use.
- **E3b short-track rule:** night: found the motorcycle (0.6 s) and one rider (0.43 s) with no false person, 2/4. Day: counted the 0.4 s track at 3:03-3:05 as a cyclist, a FALSE cyclist (it is the far pedestrian). As predicted: helps at night, hurts by day, so it should be night-only.
- **Motion diagnostic:** 447 unexplained moving blobs in the night clip and 185 in the day clip: far too many to be informative (almost every truth row overlaps dozens). Useless without filtering (minimum net movement, size, zone, brightness): no evidence it helps yet.
- **Detector vs X-CLIP, again:** at day, wherever X-CLIP said BICYCLIST for a pedestrian, the detector said person in 94-98% of frames (SAHI run), while the real cyclist had 34.7% (baseline) and 54% (SAHI). A detector veto (X-CLIP says bicyclist but detector says cyclist in < about 10-15% of frames -> pedestrian) would fix both wrong-class pedestrians and keep the real cyclist, but it is derived from these two clips and is untested elsewhere (earlier 12:45 pedestrians had 45% detector-cyclist, which it would NOT fix).
**Suggested next batch (NOT coded yet, awaiting go-ahead):** (1) fix the night truth rows and re-score; (2) `--short-rule` restricted to night frames; (3) `--det-veto-pct`; (4) combination SAHI + night-only short rule + detector veto, run on the SAME two clips AND on the untouched windows (22:00-22:15 night and 12:45-13:00 day) to see whether it generalises; (5) calibrate or drop the speed rule from `rules_audit.csv`.

## 24. Batch 2 and clip naming (written 2026-10-08; code NOT yet run on the cluster)
**24a. Which clip gave 'bicyclists 3, pedestrians 2'?** `exp1_sahi` on the DAY clip 14:00-14:15 (annotated/exp1_sahi/.../*1400-1415.mp4). It is NOT a good result against the truth (1 cyclist + 4 pedestrians): 3 bicyclists = the real cyclist + two pedestrians (3:00-3:25 and 11:45-12:14) that X-CLIP called bicyclist; the 2 counted pedestrians are the two LATE pedestrians that SAHI recovered (the real gain). The closest thing to a good night result is `exp1_sahi` night (counted 3/1: 2 of 4 riders found, 1 wrong class, 1 extra).
**24b. Clip names (from now on).** New runs write `<run>__<day|night>_<HHMM>-<HHMM>__<test>__<date>.mp4`, e.g. `b2_3_sahi_fuse__night_2115-2130__sahi640+detfuse__20190710.mp4`. `<test>` = `control`, `sahi640`, `enh-<mode>`, `speedrule`, `shortrule` / `shortrule-night`, `detfuse`, `nightswitch`, `motiondiag` joined by `+`. Old clips (sw_*, exp*) can be given the same kind of name with `python code/collect_clips.py --root .` (hard links in `exp_results/clips/`, plus `INDEX.md`).
**24c. New options in `xclip_overlay_v19_colonial.py` (all off by default).** `--short-rule-night-only` (short-track rule only for tracks whose middle frame is in the night period; needs `--night-start/--night-end`); `--det-veto-pct P` (X-CLIP says BICYCLIST but the detector calls the track cyclist in < P% of its frames -> PEDESTRIAN); `--det-promote-pct P` (X-CLIP says PEDESTRIAN but detector cyclist in >= P% -> BICYCLIST); `--det-fuse-min-frames N` (default 20 detector frames needed). Slurm env: `SHORT_RULE_NIGHT_ONLY=1 DET_VETO_PCT DET_PROMOTE_PCT DET_FUSE_MIN_FRAMES`. The label code was tested in isolation (real code text, stub data): veto flips a 6%-cyclist track and keeps a 54% one; promote flips a night 100%-cyclist pedestrian label; too few detector frames = no change; night-only short rule blocked by day and allowed at night.
**24d. Settings chosen (from batch-1 results, i.e. fitted on the two dev clips, so they MUST be checked on the hold-outs):** veto 15%, promote 90%, SAHI 640 px / 20% overlap, short rule 0.3 s / detector >= 90% / weighted BIC >= 0.9, night 21:00-06:00. Known weak spot: earlier 12:45 pedestrians called cyclist had detector 45% cyclist, which the veto at 15% would NOT fix.
**24e. The run: `bash code/run_batch2.sh` (16 jobs + 1 evaluation job).** Clips: dev night 21:15-21:30, dev day 14:00-14:15, HOLD-OUT night 22:00-22:15 (chunk 23, frames 1-26973), HOLD-OUT day 12:45-13:00 (chunk 13, frames 80924-end). Runs: `b2_0_base` and `b2_2_sahi` (hold-outs only; the dev clips already have `exp0_base`, `exp1_sahi`), `b2_1_fuse` (veto+promote), `b2_3_sahi_fuse`, `b2_4_sahi_fuse_nightshort` (all four clips). Evaluation: `exp_results/EVAL_batch2_<time>.md` compares them with `exp0_base` and `exp1_sahi`, and copies the clips with explicit names into `exp_results/clips/`.
**24f. Truth files needed BEFORE judging batch 2:** `truth/night_2115_truth.csv` (fix rows n5, n6: they lack the END column; see `night_rows_fix.txt`; confirm the total: her older note said 3 cyclists + 1 motorcycle + 1 pedestrian), `truth/night_2200_truth.csv` and `truth/day_1245_truth.csv` (new templates; the hold-out files list the model's tracks with approximate times, she must fill in the classes and add every person not listed), `truth/day_1400_truth.csv` (final). Templates: `colonial_v19_1_truth_templates.tar.gz`; do NOT re-extract the older bundle over filled-in files.
**24g. How to judge it.** A combination is 'promising' only if on BOTH the dev clips and the hold-outs it finds more true people than `exp0_base` without more wrong-class or extra tracks. If it only wins on the dev clips, the settings were over-fitted to them. Honest limits: 4 clips, one camera, one day; the thresholds come from 2 clips.
**24h. Results of batch 2.** (empty: fill in after the jobs finish.)

## 25. Night truth, how a track gets its label, speed rule (2026-10-08)
**25a. FINAL night 21:15-21:30 truth (her words, `truth/night_2115_truth.csv`):** motorcycle 4:02-4:04; bicyclist 7:02-7:09; THREE bicyclists together 14:21-14:26; pedestrian 14:47-14:58. Total = 1 motorcycle + 4 cyclists + 1 pedestrian (an older note said 3 cyclists). Motorcycle is scored as cyclist. Consequences: (1) the model's 14:29 track (labelled pedestrian by X-CLIP, detector 100% cyclist, 1.0 s) lies OUTSIDE her 14:21-14:26 range; if she meant it to be one of the three, widen the rows to 14:30. (2) Three rows share one time, so a time-only match can find at most the tracks that exist; the rest show as MISSED, which is correct. (3) SAHI's night EXTRA track at 14:44-14:59 (10.6 s, labelled cyclist) overlaps the pedestrian at 14:47-14:58: probably that pedestrian with the wrong label.
**25b. How a person track gets counted and labelled (the pipeline as it is, defaults).** (1) RT-DETR box per frame, conf >= 0.25. (2) Tracker + id stitching make a track. (3) Every `--stride` (3) frames the track's crop goes into a window of frames to X-CLIP, which outputs P(bicyclist) vs P(pedestrian); a track needs at least one X-CLIP score. (4) The track's label = whichever class has the higher box-height-weighted mean of those probabilities. THE DETECTOR'S OWN LABEL (person vs cyclist) IS NOT USED for the label unless the v19 fuse flags are on. (5) The track must stay on screen >= 3.0 s (`--person-min-sec`, also `--bic-min-sec` / `--ped-min-sec`) to be counted; zones decide road / bike lane / sidewalk. So SAHI makes tracks longer (they pass the 3 s rule) but then X-CLIP, which was never trained on this camera, makes the label.
**25c. Is the speed number right?** What is computed: path length of the smoothed ground point (bottom centre of the box) in IMAGE pixels per second, divided by the track's mean box height = 'body heights per second'. Checked only on synthetic left/right motion (walker 0.8, rider 2.9). Not verified on real tracks. Known weak points: (a) a rider moving TOWARD or AWAY from the camera moves little in the image whatever the real speed (perspective), so it looks slow: a likely reason the speed rule turned the real 9:10 cyclist into a pedestrian in `exp3a_speed`; (b) path length adds up jitter for small far boxes; (c) thresholds 1.0 / 2.0 were guesses. Remedy built: `--speed-lateral-only` (rule only for tracks moving left/right). Proper fix would be ground-plane (metric) speed from a camera calibration, not available. Data check: `python code/fusion_probe.py --root . --runs exp0_base,exp1_sahi,exp3a_speed` prints, for every truth person, X-CLIP label, detector %cyclist, speed, direction, and replays veto / promote / speed rules on them.
**25d. Run `b2_5_sahi_speed`** added to `code/run_batch2.sh` (SAHI + lateral-only speed rule, thresholds in the `SPEEDENV` line at the top of the script); batch 2 is now 20 jobs + evaluation. Update bundle: `colonial_v19_2_code.tar.gz` (code only); truth files are separate and must not be overwritten once filled in.
**25e. Annotated folders.** Each run has one sub-folder per clip (`annotated/<run>/Standard_SCU8OG_2019-07-10_0000.015` = day 14:00, `.022` = night 21:15, `.013` = day 12:45, `.023` = night 22:00). Runs `exp2_gamma / exp2_clahe / exp2_zerodce` were NIGHT-only by design (no day clip). If a night clip is missing elsewhere, list what exists: `find annotated -name "*.mp4" -printf "%p %s\n" | sort` (a file ending `.tmp_mp4v.mp4` means the final conversion did not finish).
**25f. Night minimum: what was and was not tested (2026-10-08).** `sw_switch` (v18) = flat night minimums 0.4 s bicyclist / 1.0 s pedestrian (+ detector conf 0.15, which did little). `exp3b_short` = a conditional short rule (>= 0.3 s, detector cyclist >= 90% of frames, weighted BIC >= 0.9): stricter, it missed the 0.9 s rider whose detector share was 59%. Batch 2 as first written only had the conditional rule at night (`b2_4`). Added: `b2_6_night04` (flat minimums, no SAHI) and `b2_7_sahi_fuse_night04` (SAHI + veto/promote + flat minimums), on the two NIGHT clips only (day clips would equal existing runs). Batch 2 = 24 jobs + evaluation. With SAHI the night tracks are already 3.4-5.2 s long, so a night minimum matters much less there.
**25g. What to run after the jobs finish (from the project folder `test_colonial`, NOT from `code/`).**
```bash
squeue -u $USER -o "%i %j %T %M"                    # nothing left = finished
grep -L "Final counts" logs/slurm_b2_*.log          # logs WITHOUT 'Final counts' = a job that failed; send me tail -20 of those
ls exp_results/                                     # the evaluation job writes EVAL_batch2_*.md and exp_results/clips/
less exp_results/EVAL_batch2_*.md                   # q to quit
python code/fusion_probe.py --root . --runs exp0_base,exp1_sahi,b2_3_sahi_fuse,b2_5_sahi_speed
```
If the evaluation job ran before the hold-out truth files were filled in, re-score (no GPU): `python code/eval_truth.py --root . --runs exp0_base,exp1_sahi,b2_0_base,b2_2_sahi,b2_1_fuse,b2_3_sahi_fuse,b2_4_sahi_fuse_nightshort,b2_5_sahi_speed,b2_6_night04,b2_7_sahi_fuse_night04 --baseline exp0_base`. Clips with explicit names: `python code/collect_clips.py --root .` then `ls exp_results/clips`. If only the first 20-job version of batch 2 was submitted, add the missing night runs with `bash code/run_night04_only.sh` (4 jobs, works with the code already on the cluster).
**25h. Results of batch 2 (20-job version; evaluator output `exp_results/EVAL_batch2_20261008_1612.md`; all jobs finished, 28-43 min each) and the fusion probe (2026-10-09).**
HOLD-OUT TRUTH WAS NOT FILLED IN: `truth/night_2200_truth.csv` and `truth/day_1245_truth.csv` were missing on the cluster, so the two hold-out clips only have counts (every counted track shows as EXTRA). They must be copied to `truth/` and filled in; everything below about generalisation is still open.
Dev clips (truth complete: night 6 people = 5 cyclist/motorcycle + 1 pedestrian; day 5 people = 1 cyclist + 4 pedestrians):
| run | night: cyclists found (of 5) / ped found (of 1) / wrong class / not counted | day: cyclist (of 1), pedestrians (of 4) / wrong class / not counted | counted bic/ped night, day |
|---|---|---|---|
| exp0_base | 0 / 0 / 0 / 4 (+2 missed) | 1, 2 / 0 / 2 | 0/0, 1/2 |
| exp1_sahi | 2 / 0 / 2 / 2 | 1, 2 / 2 / 0 | 3/1, 3/2 |
| b2_1_fuse (veto+promote, no SAHI) | same as exp0_base | same as exp0_base | 0/0, 1/2 |
| b2_3_sahi_fuse (SAHI + veto + promote) | 2 / 0 / 2 / 2 | **1, 4 / 0 / 0 (all 5 right)** | 3/1, 1/4 |
| b2_4_sahi_fuse_nightshort (+ short rule at night only) | **3** / 0 / 2 / 1 (the motorcycle is now found) | 1, 4 / 0 / 0 | 4/1, 1/4 |
| b2_5_sahi_speed (SAHI + lateral speed rule 1.0/2.0) | 3 / 0 / 1 / 2 | 1, 4 / 0 / 0 | 4/0, 1/4 |
Hold-out clips, COUNTS ONLY (no truth yet; earlier notes say 12:45 has 2 cyclists + 3 pedestrians): 12:45 day: base 4/1, SAHI 4/1, veto 3/2, SAHI+veto 3/2, SAHI+speed 3/2. 22:00 night: base 0/0, but every SAHI run counts 7 pedestrians (0/7): real people SAHI found, or false detections? Unknown until someone watches the clip (annotated/b2_2_sahi/*0.023/).
What the data say (dev clips = where the settings were chosen, so optimistic):
- SAHI is the one change that adds true detections (night riders, late pedestrians); it needs a label fix on top. The detector veto (15%) turned both SAHI wrong-class pedestrians on the day clip right (detector said person in 94-98% of frames) and left the real cyclist (detector 35-54%): day clip 5/5. Without SAHI the veto changes nothing on the dev clips.
- The short-track rule at night only found the motorcycle (1.2 s track, detector 94%, weighted bicyclist 0.97) with no new false person.
- Speed (fusion probe, 41 (person, run) pairs, but only about 11 different people): X-CLIP alone right in 26; veto 10-30% right in 32; lateral speed rule walk < 0.8 / ride > 2.0 right in 35 and flips only wrong labels (night n4 rider X-CLIP called pedestrian: speed 2.23 h/s; day d2 and d3: speed 0.56 and 0.39). At walk < 1.0 it flips the real day cyclist (0.97 h/s, moving left, detector 35%): wrong. So the usable window is thin: slowest real cyclists 0.79-0.97 h/s vs fastest walker 0.78 h/s. Speed in the image is NOT a clean separator; the det %cyclist condition protects the night rider (0.87 h/s, detector 88%).
- Still wrong at night: n6, the 14:47-14:58 pedestrian (10.6 s, moving right, speed 0.48 h/s) is called bicyclist by X-CLIP (0.67) AND the detector (69% cyclist); only a speed-alone rule would catch it. n5 (a rider called pedestrian, detector 31%, 2.37 s) stays under the 3 s minimum.
- `exp0_base` vs `b2_1_fuse` are identical on the dev clips: veto/promote do nothing without the longer SAHI tracks.
- The first batch had no failed jobs (the only log without 'Final counts' is the evaluation job's own).
**25i. Next (batch 3).** `bash code/run_batch3.sh`: ONE combined run `b3_combo` (SAHI + veto 15/promote 90 + short rule at night only + lateral speed rule 0.8/2.0) on all four clips; its evaluation job also runs `fusion_probe.py`. Before it can be judged: (1) fill the two hold-out truth files, (2) watch the 22:00 SAHI clip (7 pedestrians), (3) re-score with the commands in 25g. If the hold-outs disagree with the dev clips, the thresholds are over-fitted.

## 26. Hold-out truth status (2026-10-09)
The hold-out files were created on the cluster on 2026-10-09 but the CLASS column was left empty, so the evaluator still skipped every row (0 usable rows for both hold-outs); counts in the batch-2 report are therefore the only hold-out evidence so far. DRAFT for `truth/day_1245_truth.csv` (inferred, to be CHECKED by Rithika): h1 0:40-0:56 pedestrian (her screenshot of id 1: a walking person called BICYCLIST), h2 8:07-8:13 cyclist, h3 8:46-8:53 cyclist, h4 9:54-10:04 pedestrian, h5 11:17-11:38 pedestrian (detector: person in 93% of frames) = 2 cyclists + 3 pedestrians, matching her earlier note; her extra 'pedestrian on the grass, not counted' may be one of these or a 4th person (unresolved). Counts-only evidence on that clip (from `EVAL_20261009_0047.md`): `b2_3_sahi_fuse` (veto) changes only #15 (11:14-11:40) to pedestrian; `b2_5_sahi_speed` changes only #1 (0:40-0:59) to pedestrian; both give 3 cyclists / 2 pedestrians; the two fixes are on DIFFERENT tracks, so the combined `b3_combo` should give 2 / 3, IF the draft is right. 22:00 night: SAHI runs count 7 pedestrians that the baseline missed (windows 6:00-6:13, 7:50-8:27, 8:32-9:00, 9:05-10:15, 10:42-11:18, 11:05-11:16, 11:12-11:18); nobody has checked whether they are real people.

## 27. First hold-out scoring: day 12:45-13:00 (2026-10-09), against the DRAFT truth in section 26
IMPORTANT: Rithika pasted the draft classes as given, so they are NOT yet verified by her eyes (the notes still say CHECK). h1 = pedestrian is independent (her own screenshot of id 1: a walking person called BICYCLIST; detector 45% cyclist in the base run). h5 = pedestrian was inferred from the DETECTOR (7-8% cyclist), so any rule that uses the detector looks right on it by construction (circular). h2 and h3 = cyclist are by elimination. The base-run detector shares were 45 / 46 / 45 / 7 % cyclist for h1 / h2 / h3 / h5, so the second 'pedestrian called cyclist' could be h2 or h3 instead of h5; if so the veto would be WRONG on h5.
Scores against the draft (2 cyclists + 3 pedestrians): base 4/1 counted (cyclists 2/2 found, pedestrians 1/3, 2 wrong class); SAHI alone same; SAHI + veto 15% (`b2_3_sahi_fuse`) 3/2: fixes h5 only; SAHI + lateral speed 0.8-ish rule (`b2_5_sahi_speed`, run with 1.0/2.0) 3/2: fixes h1 only (h1: speed 0.74 h/s, moving left, detector 26%); h5 is moving AWAY from the camera so the lateral-only speed rule does not touch it. The two fixes are complementary, so the combination (`b3_combo`, not yet run) should reach 2/3.
Fusion probe on 50 (person, run) pairs (about 16 different people, dev + the 12:45 hold-out): X-CLIP alone right in 32; veto 10-20% right in 40; veto 30% right in 43 (flips h1 too; its margin is thin: h1 26% vs the real day cyclist 34.7%); veto 40% already flips the real day cyclist (wrong); veto 50% flips real cyclists h2, h3, n3 (wrong); promote never fires; lateral speed walk < 0.8 / ride > 2.0 right in 42 with NO wrong flips; walk < 1.0 flips the real day cyclist and h2 (wrong). Conclusion so far: veto about 15% and speed 0.8 / 2.0 (lateral only) are the settings with no wrong flips on any people seen; both windows are narrow and rest on very few people.
Still open: (1) which of h2, h3, h5 is the second pedestrian called cyclist (watch 8:07, 8:46, 11:17); (2) the 22:00 night hold-out has no truth yet (SAHI counts 7 pedestrians); (3) night remains weak: the 14:47-14:58 pedestrian is called cyclist by both X-CLIP and the detector (69%) and a 2.4 s rider stays under the 3 s minimum.

## 28. VERIFIED hold-out truth (her answers, 2026-10-09) and what it shows
**12:45-13:00 (day) = 2 cyclists + 3 pedestrians, confirmed:** 8:07 bicyclist (h2), 8:46 bicyclist (h3), 11:17 walking (h5), 0:40 pedestrian (h1, her screenshot); 9:54 (h4, counted pedestrian) not re-checked. So the draft of section 26/27 was right, including h5 = pedestrian; the veto decision on h5 is no longer circular, and the second 'pedestrian called cyclist' is h5, not h2/h3.
**22:00-22:15 (night) = 5 pedestrians, 0 cyclists:** pedestrian 6:00-6:13; pedestrian 10:00-10:14; THREE pedestrians walking together 10:59-11:18. NOT people: a BARRICADE tracked as a pedestrian at 7:50-8:27, 8:32-9:00 and 9:05-10:15. Against the SAHI runs' 7 counted pedestrians (tracks #18, #24, #26, #27, #33, #36, #40): 4 are real (#18 at 6:00, #33 / #36 / #40 at about 10:42-11:18) and 3 are FALSE (#24, #26, #27 = the barricade), i.e. SAHI found 4 of the 5 real pedestrians that the baseline missed completely (0 counted) but added 3 static false people. Caveat: the 10:00-10:14 pedestrian overlaps in time with the barricade track #27 (9:05-10:15); the time-only evaluator will score it FOUND by that track although the track is the barricade: whether the real pedestrian was boxed at all is unknown. Expected evaluator output for SAHI at 22:00 with the new truth: 5/5 found, 2 EXTRA (#24, #26).
**What it means.** SAHI also creates false people on STATIC objects at night (3 tracks of 3.8-18.7 s on a barricade). The veto/promote/speed rules do not touch this (the tracks are labelled pedestrian already). Candidate fix, NOT coded: a static-object filter (tiny net movement AND tiny speed AND long duration, perhaps night only or on a persistent location); it must not remove real standing pedestrians (day clip d4, d5 were static real pedestrians), so first look at the features of the false tracks: `python code/fusion_probe.py ...` now prints a second table of counted tracks that match no truth person (secs, X-CLIP, detector %cyclist, speed, net px, direction).
**Next.** (1) Put the two new truth files in `truth/` (below), (2) re-run `eval_truth.py` and the updated `fusion_probe.py` on exp0_base, b2_0_base, b2_2_sahi, b2_3_sahi_fuse, b2_5_sahi_speed (and `b3_combo` once it has run), (3) send the two outputs; the features of tracks #24/#26/#27 decide the static filter.

## 29. Batch 3 results: `b3_combo` (2026-10-10; evaluator output `EVAL_batch3_*.md`, 4 jobs of about 42 min)
Setting: SAHI 640/20% + detector veto 15% + promote 90% + short rule at NIGHT only (0.3 s / detector >= 90% / weighted bicyclist >= 0.9) + lateral speed rule walk < 0.8 / ride > 2.0 body heights/s. The speed and veto thresholds were chosen from the two dev clips BEFORE the 12:45 and 22:00 truth existed, so those two clips are a genuine (if small) hold-out. Truth is verified by her eyes for all four clips (section 28). 21 people in total.
| clip (people) | exp0_base (control) | SAHI alone | **b3_combo** |
|---|---|---|---|
| night 21:15 dev (6) | 0 found | 2 found | **4 found** (n1 motorcycle, n2, n3, n4); not counted: n5 (2.4 s, labelled pedestrian); wrong class: n6 (pedestrian called cyclist) |
| day 14:00 dev (5) | 3 found, 2 not counted | 3 found, 2 wrong class | **5 / 5** |
| night 22:00 HOLD-OUT (5 pedestrians) | 0 found (3 missed, 2 detected but not counted) | 5 found | 5 found, **but 2 EXTRA + the barricade track #27 = 3 false people** |
| day 12:45 HOLD-OUT (2 cyclists + 3 pedestrians) | 3 found, 2 wrong class | 3 found, 2 wrong class | **5 / 5** (counts 2 cyclists / 3 pedestrians = truth) |
| TOTAL found | **6 / 21** | 13 / 21 | **19 / 21** |
Honest reading: (1) the 12:45 hold-out is passed: the veto fixed h5 and the speed rule fixed h1, as predicted before it ran. (2) At 22:00 no label rule was involved: the gain there is SAHI's detection alone (0 -> 5 pedestrians), paid for with 3 false static people. (3) Only about 4 hours' worth of 15-minute windows, one camera, one day, 21 people: a strong hint, not a measured accuracy. (4) The p2 person at 22:00 (10:00-10:14) overlaps in time with the barricade track #27; the time-only matcher scores it FOUND, so true recall there may be 4/5.
Remaining errors: (a) barricade tracks (#24 4.97 s, #26 3.8 s, #27 18.7 s): static, speed 0.01 body heights/s, net movement 0-2 px, detector 0% cyclist: they cannot be fixed by the label rules (already labelled pedestrian). The existing `--person-min-disp` (v13: rejects static look-alikes by net movement, env `PERSON_MIN_DISP`) is the candidate fix; BEFORE using it check that real standing pedestrians (day clip static tracks, speeds 0.15-0.18) have a larger net movement: the updated `fusion_probe.py` now prints a `net px` column for every truth person and for every false track. (b) night n6, the 14:47-14:58 pedestrian, called bicyclist by X-CLIP (0.67) and by the detector (69% cyclist); its speed is 0.48 h/s, slower than every real cyclist seen (>= 0.87), but fixing it means a speed-only rule fitted on ONE example: do not do it without more data. (c) night n5, a rider labelled pedestrian by X-CLIP, 2.4 s, below the 3 s minimum.
Promote (90%): never right, one wrong flip on the baseline (`b2_0_base` 22:00 p2, an uncounted 0.43 s track): it adds nothing, leave it off in future runs. Detector veto: right on every flip it made (d2, d3, h5). Speed lateral 0.8 / 2.0: right on every flip (n4, d2, d3, h1); 1.0 flips real cyclists (d1, h2): keep 0.8.
Not worth pursuing from these data: enhancement (no gain), motion diagnostic (447 / 185 blobs, no discrimination).
Next: (1) run `python code/fusion_probe.py --root . --runs b3_combo,b2_2_sahi` and send the table (net px of real people vs the barricade), (2) choose PERSON_MIN_DISP from it and run ONE confirmation job set (`b3_combo` + static filter), (3) before any claim, label 2-3 NEW windows (one more night, two day, different hours) as a fresh hold-out; the current four clips have now been looked at.

## 30. Net-movement check of the 22:00 barricade tracks (2026-10-10) and a CORRECTION
Fusion probe on `b3_combo` and `b2_2_sahi`, new `net px` column (motion_summary net movement of the smoothed ground point):
- Counted tracks matching no truth person (the false people): #24 (7:50-8:27, 4.97 s) net 0 px, speed 0.01 h/s, static, detector 0% cyclist; #26 (8:32-9:00, 3.8 s) net 2 px, speed 0.01, static, detector 0%. Only these TWO.
- #27 (9:05-10:15, 18.72 s), which sections 28 and 29 counted as a third barricade track, is NOT static: net 516 px, speed 0.15 h/s, moving right, matched to the real pedestrian p2 (10:00-10:14). So it is probably one track that started on the barricade and ended up following the real pedestrian (or the barricade box merged with the person): a real person with a contaminated track, not a third false person. CORRECTION: false people at 22:00 = 2, not 3; real recall there 5/5 is plausible, but the track's early part (9:05-10:00) sits on the barricade.
- Real static pedestrians for comparison: day 12:45 h4 (7.2 s) speed 0.18, net 30 px (static); all other real people: net 344-733 px.
So a net-movement filter below about 10 px would remove #24 and #26 and keep every real person seen so far; the closest real person is h4 at 30 px, a margin of 3x on a very small sample. `PERSON_MIN_DISP` (v13) filters by `disp_px` (first-to-last ground point, written to tracks.csv), which can differ slightly from the net px above: check it with `python code/disp_check.py --root . --runs b3_combo --below 60`, which lists every counted track under 60 px with clip, time, length and label (only #24 and #26 should be under about 10). Then `bash code/run_batch4.sh` runs b3_combo + `PERSON_MIN_DISP=10` (promote off) on all four clips (`DISP=15 bash code/run_batch4.sh` to change). Open: how the filter treats a standing pedestrian who really stands still for several seconds (none among the 21 people so far has less than 30 px).

## 31. `disp_check.py` on b3_combo (2026-10-10): counted tracks under 60 px of net movement (`disp_px`, the number `PERSON_MIN_DISP` uses)
| disp px | clip | track | from | secs | label |
|---|---|---|---|---|---|
| 1 | night 22:00 (hold-out) | #24 | 22:07:50 | 4.97 | PEDESTRIAN (barricade, false) |
| 1 | night 22:00 (hold-out) | #26 | 22:08:32 | 3.8 | PEDESTRIAN (barricade, false) |
| 19 | day 14:00 | #23 | 14:12:30 | 3.47 | PEDESTRIAN (real: d5, standing) |
| 30 | day 12:45 (hold-out) | #14 | 12:54:53 | 7.21 | PEDESTRIAN (real: h4, standing) |
Nothing else is below 60 px. CORRECTION of section 30: the closest real person is 19 px (d5), not 30; the 30 px figure was the other standing pedestrian (h4). The two false tracks are at 1 px. Cutoff choice: 10 px would remove both barricade tracks but sits only 1.9x below the real 19 px standing pedestrian; **5 px** is the better balance on a log scale (5x above the barricade, 3.8x below the real person). Use `DISP=5 bash code/run_batch4.sh` (run name `b4_combo_disp5`). Caveat: 4 tracks under 60 px in total, 2 real standing pedestrians; a pedestrian standing still for several seconds could go below 5 px, and a barricade that jitters more could exceed it: the choice is a guess supported by very few numbers.

## 32. Static-object filter v2, and what 'fusion' means here (2026-10-10)
**32a. A person waiting to cross, then crossing.** `PERSON_MIN_DISP` (v13) judges a track only by net movement first -> last frame of its WHOLE life. A person who waits and then crosses has a large net movement, so that track is kept. Where it can go wrong: a person who only stands still for the whole track, and a tracker that splits waiting and crossing into two tracks (the waiting piece could be dropped, the crossing piece still counts the person once). A net-only filter would also drop a person who sways in place with a net movement under the cutoff. New, safer rule `--static-filter` (env `STATIC_FILTER=1`, `STATIC_MAX_NET_PX=5`, `STATIC_MAX_SPEED=0.05`, `STATIC_MIN_SEC=3`): a track of at least 3 s is dropped as a STATIC OBJECT only if BOTH its net movement is under 5 px AND its ground-point PATH speed is under 0.05 body heights/s. The path speed counts box jitter and body sway: the barricade tracks have 0.01 h/s, the real standing pedestrians 0.15-0.18 h/s. It is never more aggressive than the net-only filter. Tested on the real code text with the known tracks (barricade #24, #26 dropped; standing pedestrians d5 and h4 kept; a track with 516 px net kept; a 2 s track not judged; a person moving in place at 0.5 h/s kept). Not yet run on the cluster. A person standing PERFECTLY still for >= 3 s (both numbers tiny) would still be dropped: no such person among the 21 labelled. Possible later refinements (not coded): a persistent-location map of objects that stay in the same place for minutes or hours (a barricade does, a waiting person does not); a lower box-jitter bound.
**32b. Best configuration so far = `b3_combo` (19/21 people found on 4 labelled clips, baseline 6/21, SAHI alone 13/21).** Pieces: (1) detector `rtdetr_v3` (fine-tuned RT-DETR) run with SAHI-style sliced inference (640 px slices, 20% overlap, plus the full-frame pass, duplicates merged; people only); (2) tracker + id stitching; (3) X-CLIP video classifier on each person track (P(bicyclist) vs P(pedestrian), weighted by box height); (4) minimum 3 s on screen to count; (5) FUSION RULES, i.e. the final label no longer comes from X-CLIP alone but from three opinions about the same track: X-CLIP (how it looks over time), the detector (its per-frame person/cyclist call, summarised as the % of frames called cyclist) and the motion (speed in body heights per second and direction). Rules: veto (X-CLIP says bicyclist but the detector calls it cyclist in < 15% of frames -> pedestrian); speed rule for left/right-moving tracks seen >= 1.5 s (slower than 0.8 h/s and detector < 50% cyclist -> pedestrian; faster than 2.0 h/s and detector >= 50% -> bicyclist); promote 90% (never fired usefully, to be dropped); night-only short-track rule (21:00-06:00: a track of 0.3-3 s counts as bicyclist if the detector says cyclist in >= 90% of frames and the weighted bicyclist probability is >= 0.9). Next candidate: b3_combo + static-object filter = `bash code/run_batch4.sh` (run name `b4_combo_static5`). Tried and dropped: image enhancement (gamma, CLAHE, Zero-DCE), motion-blob diagnostic, flat 0.4 s night minimum (not yet evaluated if run), the first speed rule thresholds (1.0). Not done: fine-tuning on her own frames, temporal detector, BNE-DETR, SAMURAI.

## 33. Zones re-annotation, a new higher-resolution video, batch-4 housekeeping (2026-10-11)
**33a. Batch 4.** Two versions exist: the first `run_batch4.sh` (net-only filter, `PERSON_MIN_DISP`, run name `b4_combo_disp5`) is superseded by the second (`--static-filter`: net movement < 5 px AND path speed < 0.05 body heights/s, run name `b4_combo_static5`). If the first is still queued or running, cancel it and its evaluation job (`squeue -u $USER -o "%i %j %T %M %E"`, `scancel <ids>`); keep the second. Both would give the same result on the known tracks, so nothing is lost.
**33b. What the zones do (read from the code).** `road` polygon: vehicles whose ground point is outside it are dropped. `sidewalk` polygon: vehicles inside it are dropped. `bike` polygon: drawn for reference and used for the bike-lane vs sidewalk split of PEOPLE (the facility column); it does not filter anything. PEOPLE are never removed by the zones (zones_test, 2026-10-05: same person counts as without zones). So a wrong bike-lane polygon affects only the facility column and the drawn overlay, NOT the person counts and none of the batch 1-4 scores. A wrong road polygon would affect vehicle counts (not evaluated). The pipeline reads ONE polygon per zone, in the file `{"ref_size":[W,H],"road":[[x,y],..],"bike":[..],"sidewalk":[..]}`; coordinates are scaled by (video size / ref_size), so a file drawn on a frame of the same shape works at another resolution only if the camera view and aspect ratio are the same.
**33c. Re-annotating.** `python code/extract_ref_frames.py --colonial-chunk 13 --times 5:00,25:00,45:00` writes CLEAN full-size PNGs to `zones/ref/`; the current polygons can be seen in `counts/<run>/*_zones_preview.png`. `zone_annotator.html` (open locally in a browser, works offline): load the frame, optionally load the current zones JSON (scaled to the frame), draw/move points, click 'Download zones JSON' (file `colonial_north_v2.json`, `ref_size` = the frame's size), copy it to `zones/` on the cluster. Test status: the scaling/export logic was tested in node; the page was NOT tested in a real browser. The old zones file says ref_size 720x480: check the real video size (`probe_video.py` or the 'zone coords scaled' log line).
**33d. New video (2025 or later, higher resolution).** `python code/probe_video.py "<video>"` prints size, fps, length and the ffmpeg command to cut a 15-minute clip; `VIDEO=<clip> START="YYYY-MM-DD HH:MM:SS" [ZONES=<new zones json>] bash code/run_new_video.sh` runs two jobs: `nv_base_<date>` (control) and `nv_combo_<date>` (SAHI + veto + night short rule + lateral speed rule + static filter). The slurm now accepts `VIDEO_OVERRIDE` (+ `SESSION_START`), switches the 2019 ground-truth file off for it and sets `--chunk-index 1`. There is NO truth file for it, so nothing is scored automatically: judge by watching the two clips and (if wanted) by writing a truth file like the others. Open questions: is it the same camera and the same view (the Colonial zones and the fine-tuned detector were made for the 2019 footage)? Pixel-based settings were chosen on the old resolution and should be scaled by the width ratio: static filter (5 px), stitch/split distances (150/120 px), the 30 px 'static direction' cutoff, SAHI slice (640 px); the body-heights speed thresholds are resolution-free. Dry-run tested with a fake `sbatch`; not run on the cluster.

## 35. Batch 4 results, and tools for the new video and the zones (2026-10-12)
**35a. Batch 4 result.** `b4_combo_static5` vs `b3_combo` (same truth, evaluator `EVAL_batch4_*.md`; all 4 jobs finished, 41-43 min; the `Final counts` check printed no failed logs): night 21:15 4/5 cyclists found, 0/1 pedestrian, 1 wrong class, 1 not counted, 0 extra (identical to b3); day 14:00 5/5 (identical); night 22:00 hold-out 5/5 pedestrians, **extra counted 2 -> 0**, counted 0/5 (was 0/7); day 12:45 hold-out 5/5 (identical). Fusion probe: no counted track without a truth person remains for `b4_combo_static5`. Caveats unchanged: 21 people, 4 clips, one camera and day, thresholds partly set on the first two clips, the static filter set from 4 tracks under 60 px (2 real standing pedestrians at 19 and 30 px). The filter's both conditions (net < 5 px AND path speed < 0.05 h/s) were not triggered by any real person.
**35b. Which tarball.** `colonial_code_latest.tar.gz` is the complete current code set (a superset of v19_2, v19_3 and v19_4 tarballs); unpack it from `test_colonial` (`tar xzf colonial_code_latest.tar.gz`); it does not touch `truth/`. The new video / zones scripts need the updated slurm from it (`VIDEO_OVERRIDE`, safe for the old runs).
**35c. Picking a 2025+ video without knowing the path.** `python code/find_new_videos.py` walks `/orange/xiangyan/rithika/vision/pilot_clips/MioVision Data` (override with `--root`), lists files whose path contains a date >= 2025 with their resolution, picks the highest-resolution one (`--pick random` for a random one) and prints the exact commands (ffmpeg 15-minute cut, `probe_video.py`, `extract_ref_frames.py`, `run_new_video.sh`). The suggested START assumes the 2019 naming (file number NNN = hour NNN-1): confirm it. It was tested on a synthetic folder tree only; if the date is not in the file names it finds nothing (`--min-year 0` lists everything). A different site means different zones and a detector fine-tuned on Colonial footage: the result is a robustness test, not a like-for-like score.
**35d. Roboflow for the zones.** Upload a clean frame (`extract_ref_frames.py` output), create a polygon (instance segmentation) project with classes road, bike, sidewalk, ONE polygon per class, export COCO, then `python code/roboflow_to_zones.py --coco _annotations.coco.json --out zones/colonial_north_v2.json`. The converter recognises names containing road / bike / side, keeps the largest polygon per class, writes `ref_size` from the export (so resizing in Roboflow is fine if the aspect ratio is kept). Tested on a synthetic COCO file only.

## 37. The 2025 video (fisheye) and the zone polygons for it (2026-10-12)
**37a. What was run.** On a 15-minute clip of a 2025 video (the file path is not recorded here: ask Rithika): `SLICE=853 bash code/run_new_video.sh` with TAG `corrine2025_706`, jobs `nv_base_corrine2025_706` (control) and `nv_combo_corrine2025_706` (SAHI slice 853 + veto 15 + night short rule + lateral speed rule + static filter; no zones file). The first search of `/orange/xiangyan/rithika/vision/pilot_clips/MioVision Data` found 55 files: 2019 (BL Colonial), 2021 (Anderson St, Church Ave), 2022 (Curry Ford North), ALL 720x480 at 30 fps, nothing from 2023 or later. Results (counts, clips) were not sent back to this chat; check `counts/nv_*_corrine2025_706/` and `annotated/nv_*_corrine2025_706/` (clips with explicit names after `python code/collect_clips.py --root . --prefix nv_`, copies in `exp_results/clips/`).
**37b. Her verdict after watching the 2025 videos:** not good for this pipeline. The camera is a FISHEYE: cars directly below the camera are not detected; things are detected when they are not too close to the camera. The detector (`rtdetr_v3`) was fine-tuned on rectilinear 720x480 footage of the 2019 Colonial camera, so a fisheye view is a different domain (strong distortion, perspective, scale). Consequences: the 2025 clip is NOT a like-for-like test of anything in sections 0-35; the pixel-based settings (static filter 5 px, stitch / split distances, the 30 px static-direction cutoff, SAHI slice) and the speed-in-body-heights rule were set for the old view and are not validated there; the veto/speed rules depend on box height and ground-point movement that fisheye distortion changes. Possible directions (not started): undistort the fisheye frames before detection if the lens parameters are known; fine-tune on labelled fisheye frames; or treat the 2025 clips as a limitation to report (the better resolution does not help if the geometry is the problem).
**37c. Zone polygons for the COLONIAL 2019 camera (new zones file, 2026-10-12; CORRECTION: an earlier version of this README wrongly said they were for the 2025 video).** Given by Rithika, re-drawn because the bike lane in `colonial_north_v1.json` was wrong. Saved as `colonial_north_v2.json` (in the outputs folder; goes to `zones/colonial_north_v2.json` next to `colonial_north_v1.json`):
bikelane = [[107,71],[925,407],[1422,698],[1418,953],[1230,945],[64,81]]
sidewalk = [[1228,947],[674,947],[431,760],[206,502],[23,116],[60,83]]
grass = [[21,119],[206,506],[435,764],[682,951],[16,951],[4,123]]
main road = [[99,71],[616,273],[925,407],[1420,694],[1418,71],[1340,40],[107,40]]
Mapping: bikelane -> `bike`, main road -> `road`, sidewalk -> `sidewalk`; `grass` is kept in the file but the pipeline reads only road, bike and sidewalk (extra keys such as `grass` and `_note` are ignored by the loader). The frame size they were drawn on was not stated. The coordinates reach (1422, 953), and the aspect ratio matches 2x the 720x480 video, so `ref_size` is set to [1440, 960] as an INFERENCE (the pipeline scales every polygon by video size / ref_size, so with this value the 720x480 video gets the points halved). VERIFY before trusting it: `python code/extract_ref_frames.py --colonial-chunk 13 --times 5:00` then `python code/draw_zones_preview.py --zones zones/colonial_north_v2.json --image zones/ref/<frame>.png --out zones/ref/preview_v2.png` and look at the picture (road green, bike lane yellow, sidewalk magenta, grass cyan). If the shapes do not sit on the real road / lane / sidewalk, the drawing size was different: tell the assistant what size the image had when drawn. To use the file in a run, set `ZONES_JSON=$ROOT/zones/colonial_north_v2.json`; the `run_batch*.sh` scripts hard-code `colonial_north_v1.json` (change with `sed -i 's#colonial_north_v1.json#colonial_north_v2.json#' code/run_batch4.sh`). Effect on results: person counts and every score in this README are unaffected by zones (zones never remove people); the road polygon changes vehicle counts, the bike polygon changes the bike-lane vs sidewalk column. `grass` could later be used to study pedestrians walking on grass (one 12:45 pedestrian was never counted), but nothing reads it yet. `stamp_zone_size.py` (writes ref_size from a video and checks all points are inside the frame) is available for files whose drawing size equals the video size.
**37d. Colonial zones: status.** Done (polygons given, section 37c); still to verify with `draw_zones_preview.py`. The Roboflow route (`roboflow_to_zones.py`, section 35) and `zone_annotator.html` remain available if a polygon needs redrawing. No zones file exists for the 2025 fisheye video.

## 38. HAND-OFF for a new chat session (written 2026-10-12)
**Give the new session:** this README (v29), `colonial_code_latest.tar.gz` (all current code; unpack from the `test_colonial` folder), and the four truth files (`colonial_truth_final.tar.gz`). Tell it to read section 0 first, then sections 35, 37 and this section; older sections hold superseded guesses (list of corrections in section 0).
**Cluster facts.** Project folder (`ROOT`): `/orange/xiangyan/rithika/vision/vision3/best/test_colonial`. Always run commands from there, never from inside `code/`. Environment: `source /orange/xiangyan/rithika/vision/yolo_env/bin/activate`. Slurm: one GPU per job, partition `hpg-turin`, account and qos `xiangyan`; the job script is `code/run_xclip_colonial_v19.slurm` (all options are environment variables, listed at its top); jobs are submitted by the `run_*.sh` scripts. Folders: `counts/<run>/` (tables), `annotated/<run>/` (clips), `logs/`, `truth/` (hand-made truth), `zones/`, `exp_results/` (reports, `clips/`). Old Colonial videos: `/orange/xiangyan/rithika/vision/pilot_clips/MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/Standard_SCU8OG_2019-07-10_0000/Standard_SCU8OG_2019-07-10_0000.NNN.mp4` (NNN-1 = hour). Clips used for scoring (video position = clock minus clip start): night 21:15-21:30 (hour file 22, frames 26978-53946), day 14:00-14:15 (file 15, frames 1-26973), night 22:00-22:15 hold-out (file 23, frames 1-26973), day 12:45-13:00 hold-out (file 13, frames 80924-end).
**The best pipeline in one paragraph.** `rtdetr_v3` detector + SAHI slicing (640 px) + tracker + X-CLIP per track + 3 s minimum; fusion rules (detector veto 15%, lateral speed rule 0.8 / 2.0 body heights/s, night-only short-track rule 21:00-06:00); static-object filter (net < 5 px and path speed < 0.05 h/s). The exact settings of each named run are in the `ENVV` line of the matching `run_batch*.sh` and in each run's `logs/<run>/*_run_log.json`. Current best run: `b4_combo_static5` (19 of 21 people found, 0 false tracks on the four labelled clips).
**Scripts.** `eval_truth.py` (person-level scoring against `truth/`), `fusion_probe.py` (features of truth people and false tracks, rules replayed), `disp_check.py`, `collect_clips.py` (explicit clip names), `extract_ref_frames.py`, `probe_video.py`, `find_new_videos.py`, `run_new_video.sh`, `stamp_zone_size.py`, `roboflow_to_zones.py`, `zone_annotator.html`, `test_v19.py` (helper tests), batch scripts `run_all_experiments.sh`, `run_batch2.sh` ... `run_batch4.sh`, `run_night04_only.sh`. After any batch: `grep -L "Final counts" logs/slurm_<run>*.log` (prints nothing if all jobs worked), then `python code/eval_truth.py --root . --runs ... --baseline exp0_base` and `python code/fusion_probe.py --root . --runs ...`.
**How Rithika works (so the next session does not repeat mistakes).** She runs commands in a terminal on HiPerGator and pastes the output back; give exact copy-paste commands, from the `test_colonial` folder. Several times a command was run from inside `code/` or a tarball unpacked in the wrong folder (so `code/code/` appeared): say where to run. Running a submit script twice submits the jobs twice. She wants every result and decision recorded in the README, and corrections stated plainly (a few earlier statements were wrong and were corrected later: see section 0). Ground truth = her own hand-made person lists from watching the clips; the old count file is unreliable. She has a professor who asked for a higher-resolution 2025 test (done, see 37).
**Open work, in order of value.** (1) Fresh evidence: label 2-3 NEW 15-minute windows (one night, two day, other hours of the 2019 Colonial day or the 2021 / 2022 videos) and score `b4_combo_static5` on them; the four current clips have all been looked at. (2) Remaining errors: night pedestrian called a cyclist (14:47), night 2.4 s rider under the 3 s minimum. (3) Fine-tune the detector on her own hard frames (night, walking away, far, motorcycle class): her stated fallback, not done; frames must come from clips other than the four scored ones. (4) Fisheye 2025 video: only with undistortion or fisheye fine-tuning (37b). (5) Verify the new Colonial zones file `colonial_north_v2.json` with `draw_zones_preview.py` (37c). Not started and probably not worth it: enhancement, motion-blob diagnostic, promote rule (no gain), temporal detector, BNE-DETR, SAMURAI.

## 39. Tools for the pending work (written 2026-10-15; NOT yet run on the cluster)
**What this is.** Code for the open items of section 38 / the 10/15 weekly deck, written off-cluster with the README only (the code tarballs were not available), tested on synthetic files (fake videos, fake model module, fake `sbatch`). Nothing here changes `b4_combo_static5` or any score. Unpack from `test_colonial`: `tar xzf colonial_pending_tools.tar.gz` (adds files to `code/`, touches nothing else). Run everything from `test_colonial`, never from inside `code/`. Submit each `sbatch` once.
**Things assumed from this README and to VERIFY on first use (each tool prints what it read before doing anything):** (a) `run_batch4.sh` has a line starting `ENVV=` holding the settings of the run (`scale_up.py`, `pick_new_windows.py` copy it; RUN / START_FRAME / MAX_FRAMES are stripped and replaced); if the format differs, pass `--envv "A=1,B=2"`. (b) The slurm file is `code/run_xclip_colonial_v19.slurm` and the array id is the hour-file number. (c) Track tables have the columns of `track_truth_runs45_v2.csv` (`clip_hint`, `first_time`, `bin_start`, `secs`); `review_pack.py inspect` shows what is missing. (d) The base training set is `dataset_frames/roboflow_split_v1` in YOLO layout with a `data.yaml`. (e) `finetune_v5.slurm` copies the partition / account lines from section 38: compare with the v19 slurm.
**39a. 24 h / 48 h scale-up: `code/scale_up.py`.** `python code/scale_up.py plan --run b4_full_block1 --chunks 1-24 --from-batch code/run_batch4.sh` prints the sbatch line (dry run, about 46 GPU-hours; 48 h about 92). Add `--go` to submit once; it refuses a second submission of the same run name (checks `counts/<run>` and `logs/.scale_<run>.lock`). `python code/scale_up.py check --run b4_full_block1 --chunks 1-24` lists chunks without output and prints the resubmit command. Recommended order unchanged (section 16, 38): only after new clips (39b) and, ideally, fine-tuning (39c).
**39b. New clips: `code/pick_new_windows.py`.** `python code/pick_new_windows.py --like truth/day_1400_truth.csv --from-batch code/run_batch4.sh` picks 2 day + 1 night 15-minute windows outside the clip hours already checked (default hours 8:15, 9:30, 23:20; change with `--windows 17:00,...`), prints the ffmpeg cut command (`new_clips/`), writes truth templates (`truth/new_HHMM_truth_TEMPLATE.csv`, header copied from an existing truth file) and the sbatch line running the SAME settings as `b4_combo_static5` on exactly that window (`START_FRAME` = offset x 29.97 + 5, `MAX_FRAMES` = stop). Watch each clip, fill the truth file (one row per person, motorcycle = cyclist), rename it without `_TEMPLATE`, then `python code/eval_truth.py --root . --runs exp0_base,b4_combo_static5,b4_new_0815,... --baseline exp0_base`. Check the night window really is dark. A different site (2021 / 2022 videos, all 720x480) needs its own zones and video folder: not covered.
**39c. Fine-tune on own hard frames: `code/finetune_v5.py` + `code/finetune_v5.slurm`.** (1) `pick`: random frames from the hour files you name, NEVER inside the four scored clips (+/- 30 s) and 20 s apart, pre-labelled by the current detector (`--weights`), class names matched by name to the base `data.yaml`. Night = files 22-24 and 1-6. `--times 22:3500` adds specific moments. (2) Correct the boxes yourself (Roboflow / CVAT), export YOLO to `<out>_fixed/{images,labels}` with the same file names. Boxes the detector never drew (the whole point) must be added by hand. (3) `build`: base train x3 + your frames x3, validation by 10-minute segment (a segment never sits in both train and val); warns if one side gets nothing. (4) `sbatch code/finetune_v5.slurm` trains `rtdetr_v5_colonial` from `rtdetr_v3/best.pt` (AdamW, lr0 1e-4, imgsz 640, batch 8, seed 42, patience 15). (5) Test like every other change: copy `run_batch4.sh`, change only the weights (the earlier NightOwls test changed only `WEIGHTS`) and the run name, run on the four clips and on the 39b windows. Accept only if it beats 19/21 with no new false tracks on both. Motorcycle stays inside cyclist unless you add a class to `data.yaml` yourself. The earlier outside-dataset fine-tune made every class worse (section 19), so check vehicle counts too. `ultralytics` calls are untested here (no GPU, no package): if `train` or `pick --weights` errors, send the traceback.
**39d. Labelling + high-sensitivity review: `code/review_pack.py`.** One tool, two uses. PER-TRACK ACCURACY: `inspect`, then `build --table validation/track_truth_runs45_v2.csv --out review/pack1` cuts a 3 s-padded clip per track and writes `review.html` (download the folder, open it in a browser, keys b / p / n, `Download labels CSV`), then `merge` writes a NEW labelled csv (never overwrites) and `python code/track_truth_v1.py eval --file <that csv>` gives per-object accuracy (needs >= 40 labelled tracks; label from the video only). HUMAN REVIEW WITH HIGH SENSITIVITY: run the pipeline with a low threshold (more candidates), then `build ... --rank-col <a 0-1 column such as the detector cyclist share> --budget-min 12` keeps only the best-ranked candidates that fit 12 minutes of clips per hour; after labelling, `curve --pack ... --labels ... --truth-count N` prints review minutes vs real people found vs false candidates, i.e. where the review should stop. It cannot see people the pipeline never tracked. The browser page was syntax-checked (node) but NOT opened in a real browser.
**39e. Fisheye 2025: `code/undistort_fisheye.py`.** Lens parameters are unknown, so it works from a field-of-view guess (equidistant model, others available): `preview --image frame.png --out p.png --fovs 150,180,200 --out-fov 110 --pitch 40` shows guesses side by side (choose where straight lines look straight), `video --video in.mp4 --out out.mp4 --fov 180 --out-fov 110 --pitch 40` converts a clip, `selftest` runs a synthetic round trip (passes: mean difference 4.6 of 255 in the centre). A flat view cannot show 180 degrees and anything straight below the camera is stretched hard (the 'cars right below' problem stays): use `--pitch` and possibly two views. Whether the detector then works is untested: score the converted clip against a hand truth file; fine-tuning on labelled fisheye frames (39c with fisheye frames) is the alternative; reporting it as a limitation is the third. Decide with the professor.
**39f. NOT coded, and why.** (1) Fixing the two remaining errors (night pedestrian called a cyclist at 14:47; the 2.4 s night rider under the 3 s minimum): any new threshold would be set on the same two clips; do it only after 39b windows exist and judge on them. (2) Why people walking away are missed: no new tool needed; label the walking-away people in the 14:00 and new clips, then `eval_truth.py` + `fusion_probe.py` show which stage (detector, track, label) lost each one. (3) Temporal detector, BNE-DETR, SAMURAI: section 38 rates them probably not worth it before fine-tuning. (4) Another site: needs zones and a truth file for that site.

## 40. Requests of 2026-10-15 (evening) and what was written (NOT yet run on the cluster)
**Decisions by Rithika.** (1) Do NOT create new truth files for the three `b4_new_*` windows; use existing videos that already have truth; delete the empty `truth/new_*_truth.csv`. (The runs `b4_new_0815/0930/2320` finished (47 min each; counts 0/0, 0/3, 0/1 bicyclists/pedestrians, unscored, no truth) and are ignored. `new_clips/new_0815.mp4` is corrupt (cut was interrupted): delete the folder.) (2) Fine-tuning on own images and 24 h / 48 h scale-up are LATER (future work), not on the to-do list. (3) Never overwrite `rtdetr_v3`; fine-tunes get a new name. (4) The weekly deck must explain everything in plain language (audience: her professor), state the tracker by name (ByteTrack + ID stitching) and the exact fusion rules with thresholds (no equation exists: if-then rules), and give statistics on what speed contributed. (5) Plan for evidence beyond the 4 labelled clips: one 15-minute video each from 2022, 2023, 2024, 2025 (better resolution), chosen where people actually appear; she will write the truth for those after the model has run. Do NOT reuse the Colonial zone polygons for other locations or years.
**What the facts are.** `find_new_videos.py --min-year 0` (55 files) shows only 2019 Colonial (35 files), 2021 Anderson St, Church Ave and 2022 Curry Ford North (all 720x480). No 2023 / 2024 / 2025 video exists under `MioVision Data`; the 2025 Corrine Dr video is somewhere else (path unknown). The Excel files in `/orange/xiangyan/rithika/vision/Bike Lane Study Counts` are 2019 counts, so they cannot choose windows for 2022+.
**Speed statistics (from section 29, 21 people):** lateral speed rule 0.8 / 2.0 changed 4 tracks (n4, d2, d3, h1), all correct; the 1.0 / 2.0 version wrongly changed 2 real cyclists (d1, h2). Detector veto 15% changed 3 tracks (d2, d3, h5), all correct. The two rules overlap (d2, d3) and no run removes speed from the final combo: the ablation below measures it. Speed = sideways movement of the smoothed foot point (px/s) divided by box height (px) = body heights per second, only for left/right-moving tracks seen >= 1.5 s; thresholds were estimated by hand (synthetic: 1.4 m/s walker 0.8, 5 m/s rider 2.9), NOT calibrated, NOT in km/h, NOT checked against the speed Excel files. The standard method (camera calibration / homography to metres on the road) is not done.
**40a. `code/run_batch5.py ablation`**: runs `b5_nospeed` (SPEED_RULE=0) and `b5_noveto` (DET_VETO_PCT=0) on the four labelled clips (8 jobs, ~6 GPU-hours), settings read from `run_batch4.sh` (NETPX 5). Score: `python code/eval_truth.py --root . --runs exp0_base,b4_combo_static5,b5_nospeed,b5_noveto --baseline exp0_base`.
**40b. `code/run_batch5.py bright`**: brightening retest done fairly: night clips 21:15 and 22:00, with SAHI and all current rules, brightening on BOTH the detector input and the X-CLIP crops (`ENHANCE_CROPS=1`), modes gamma / clahe / zerodce (only those found in the script). The first test used the plain detector, no SAHI, detector input only, one night clip. It checks that the slurm has the variable (searched as `ENHANCE*`) and stops with a grep command if not. Score: `python code/eval_truth.py --root . --runs b4_combo_static5,b5_bright_gamma,b5_bright_clahe,b5_bright_zerodce --baseline exp0_base`.
**40c. `code/pick_busy_windows.py` + `pick_busy.slurm`**: for a list of videos (`videos_to_scan.txt`) records resolution / fps / length and finds the busiest 15-minute window (detector on one frame per 3 s, `person` + `cyclist`, no SAHI) and writes ffmpeg cut commands to `busy/windows.txt` and `busy/inventory.csv`. After the cut: run the pipeline with `run_new_video.sh` WITHOUT zones, scale pixel settings (`STATIC_MAX_NET_PX` x width/720) if the resolution is higher, then she labels people, then score.
**40d. Fisheye 2025:** `undistort_fisheye.py` (section 39e) is the tool; sequence: find the video path, extract one frame, `preview`, choose fov / out-fov / pitch by eye, `video`, run `run_new_video.sh` on the flat clip, compare with her hand list. A flat view cannot show what is straight below the lens; if cars there stay undetected, fisheye fine-tuning or reporting a limitation remain.
**40e. Not coded.** (1) Change detection for objects that appear in a still scene: the first version (`*_motion_candidates`) gave 447 / 185 blobs, no discrimination; a usable version needs a background model, size and zone filters, and re-detection on an upscaled crop of every unexplained blob; design only. A person under an umbrella with the face hidden is a hard case that more likely needs fine-tuning on such examples. (2) Night-specific detector (BNE-DETR): no ready-made implementation known to me; re-implementing from the paper is research-size; the cheap alternative is a night fine-tune of RT-DETR (later). (3) Speed validation against the Excel speed files: needs the file contents (`bicyclist speeds.xlsx`, `Colonial_North_676806_07-10-2019.xls`) and a pixel-to-metre calibration. (4) Removing a label from the annotated video overlay: needs the overlay code; the yellow line 'AI n vs GT m' = the model's count vs the human count from the 2019 Excel for that bin (human counts are unreliable and do not exist for 2021+); ask for `grep -n "GT" code/xclip_overlay_v19_colonial.py`.

## 36. README change log (old header text, versions v7-v18)
Status as of 2026-10-09 (v18 of this README: 25h = batch-2 results + fusion probe, 25i = batch 3; v17 notes: 25g = commands for after the runs, `run_night04_only.sh`; v16 notes: adds runs b2_6/b2_7 (flat 0.4 s night minimum) in 25f; v15 notes: section 25 = FINAL night 21:15 truth, how the labels are decided now, speed-rule problem + `--speed-lateral-only`, `fusion_probe.py`, run `b2_5_sahi_speed`; v14 notes: adds section 24 = BATCH 2 (code written + dry-run, NOT yet run on the cluster) and the new clip naming; v13 notes: section 23h now holds the RESULTS of the v19 batch (all 11 jobs ran, 30-43 min each); v12 notes: section 21 now holds her FINAL 14:00 truth (1 cyclist + 4 pedestrians, with times); v11 notes: CORRECTS my wrong inference about the 14:00 clip (section 21 and 22b/23a notes) after her truth file; v10 notes: adds section 23 = v19 experiment code (E1 SAHI, E2 enhancement, E3 rules + motion diagnostic) written and unit-tested but NOT yet run on the cluster, plus the one-command run and the truth-file evaluation; E4-E7 are NOT coded yet. v9 notes: adds section 22 = PLAN for detector-improvement experiments, written for review BEFORE any code; no code for it exists yet. v8 notes: section 20 = v18 day/night settings, now RUN, results in 20d; adds section 21 = Rithika's own watch-the-clip observations, which are the visual ground truth to use from now on; v7, v6, v5, v4, v3, v2 untouched). `rtdetr_v3` and the v17 script/slurm are unchanged and remain the working setup (v18 is a new file; with no night options it counts exactly like v17). Everything measured in sections 5-13 is on 7 of the 48 recorded hours; read the caveats before quoting numbers. The v17 tests in 15g-15m and section 19 cover only two 15-minute windows and one zones hour: treat them as leads, not conclusions.

## 41. Codex continuation (2026-10-19): batch-5 results and recovery

This section supersedes the queued-job assumptions in do.md. Local copies of the actual track tables and truth files were re-scored with eval_truth.py; they reproduce look.md. These are existing GPU results, not new inference runs.

| Settings | Correctly counted AND labelled | Interpretation |
|---|---:|---|
| Current best b4_combo_static5 | 19/21 (90.5%) | Keep this configuration |
| Without speed b5_nospeed | 17/21 (81.0%) | Speed adds two correct classifications in this comparison |
| Without detector veto b5_noveto | 18/21 (85.7%) | Veto adds one correct classification in this comparison |
| Best, night clips only | 9/11 (81.8%) | Reference for brightening |
| Gamma, night clips only | 8/11 (72.7%) | Worse by one person |
| CLAHE, night clips only | 5/11 (45.5%) | Worse by four people |
| Zero-DCE | No result | Both jobs failed before inference; do not score as zero accuracy |

No extra counted tracks were reported for the completed runs. Wrong-class people are still errors even though they are real people. FOUND means counted with the correct class; detected-not-counted means the model made a track but rejected it; missed means no matched track; extra means a counted track without a matched truth person. A 0/0 entry means that class has no truth examples in that clip, not a failure. The best run's two failures remain one pedestrian labelled cyclist and one short cyclist track rejected. Thus its totals are 8 cyclists / 12 pedestrians versus truth 8 / 13: the apparently exact cyclist total hides a missed cyclist and a wrongly included pedestrian.

These are encouraging development results, not evidence of 90.5% accuracy across sites/years. All 21 people are from one camera/day and these clips have been inspected repeatedly. The speed/veto gains are marginal contributions with other rules active; do not add them as independent gains. Speed remains image movement in body heights/second, not measured MPH. Runtime is about 42 minutes per 15-minute clip (~2.8 times video duration).

### Failures verified in logs and code fixes

* pick_busy job 46141085 failed because the default path omitted /weights/ before best.pt. Fixed pick_busy_windows.py to match the working detector path in the v19 Slurm file, support WEIGHTS, and reject a missing file before importing/loading the detector. pick_busy.slurm now stops on shell errors.
* Zero-DCE jobs 46141059_22 and 46141060_23 failed because ZERODCE_WEIGHTS was unset. run_batch5.py now requires an existing checkpoint before submission and exports it. --modes zerodce selects only those two failed jobs; gamma/CLAHE/ablation need no repeat. Submission failures now stop immediately and preserve a submission log/lock; the lock is reserved before the first job.
* The grep errors and missing busy directory in look.md were initially caused by running inside code/. They do not prove all jobs failed. The actual logs are under test_colonial/logs/.
* Bin AI is a fixed whole-bin total from the render snapshot, not a live counter. Hour so far is the frame-time live counter, which can also revise a label as evidence arrives. Changed the fixed label to AI total (AI snapshot for streamed/provisional clips), preserving GT. Old annotated videos retain old text until rendered again. Streaming snapshots may differ from final CSV totals; existing mismatch logging records that.
* undistort_fisheye.py now offers --coverage full-frame for rectangular images: the guessed FOV is interpreted diagonally instead of forcing an inscribed short-side circle. The old circular default stays available. This is not lens calibration. No original 2025 frame, both.png, or preview.png is present in this checkout, so no visual choice of FOV/pitch has been made. Encoder failure now reports an error rather than success.
* test_v19.py now resolves its source file relative to itself so it can run from test_colonial.

### Cluster recovery (after copying the changed code files to the same code/ folder)

Run from test_colonial, never code/:

```bash
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
# Retry the failed scan ONCE. This scans the four paths in videos_to_scan.txt.
sbatch code/pick_busy.slurm
# After that job completes:
cat busy/inventory.csv
cat busy/windows.txt
# Locate the existing Zero-DCE checkpoint (do not invent a path):
find /orange/xiangyan/rithika/vision -type f -name Epoch99.pth -print
```

Only if a checkpoint is found, use its full path below (replace /actual/path/Epoch99.pth). First dry-run, then submit once. --force is required only because the old bright-group submission lock already exists; check squeue before using it.

```bash
python code/run_batch5.py bright --modes zerodce --zerodce-weights /actual/path/Epoch99.pth
squeue -u "$USER"
python code/run_batch5.py bright --modes zerodce --zerodce-weights /actual/path/Epoch99.pth --go --force
```

The 14 batch-5 jobs were 8 ablations (two settings x four existing labelled windows) plus 6 brightening jobs (three modes x two existing night windows). They were NOT seven distinct videos. The separate scan list has four input paths: two 2022 Curry Ford hourly files and two 2025 Corrine camera files. A scan chooses windows; it does not run the full counting pipeline on them. No 2023/2024 file appears in this list.

### Research corrections and remaining work

BNE-DETR DOES have a public source repository: https://github.com/luy02735-lang/BNE-DETR (verified 2026-10-19; root folders benchmark, dataset, rtdetr_pytorch). The prior blanket suggestion that no implementation exists was too strong. Pretrained-weight availability, dependencies and compatibility with our person/cyclist model remain unverified; no model replacement or training was performed.

The requested technique for an object appearing in a still scene exists: background subtraction (MOG2/KNN), documented at https://docs.opencv.org/4.x/d1/dc5/tutorial_background_subtraction.html . This pipeline already has MotionDiag and --motion-diag. Its existing synthetic test confirms it flags an unexplained blob and ignores an explained one. Prior real-clip output had too many candidates (447/185); no measured improvement has been established. A changed region can be shadow/light/foliage, not necessarily a person. A next experimental version would crop/re-detect unexplained regions and evaluate recovered people AND added false tracks; it should remain separate from the best configuration until scored.

Remaining dependent steps: run the repaired scan on HiPerGator; inspect/cut its selected clips; obtain the original fisheye frame and compare full-frame previews before selecting lens settings; run and hand-label the new-year clips. Keep fine-tuning and 24/48-hour scale-up deferred per section 40. No empty truth files were created and no model weights or existing result tables were overwritten.

Validation locally: re-evaluated saved tables (matches look.md); four recovery regression tests pass (missing checkpoint, selective retry, failed-submission stop/lock, rectangular mapping); existing test_v19.py passes (slicing, merging, enhancement, speed, motion diagnostic); fisheye selftest passes (4.57/255 centre difference). No GPU inference or Slurm jobs submitted from this Mac. Synthetic mapping tests do not establish that undistortion improves real detections.


## 42. Task audit and repository organization (2026-10-19)

Current task status is in `docs/TODO.md` from the repository root, with exact sync/run/review steps in `docs/HIPERGATOR_RUNBOOK.md`. Original do/look/todo notes are preserved in `docs/tasks/`. This README moved to `docs/colonial/`; current inference remains at `vision3/best/test_colonial/code/` unchanged in location. 435 old plain-text logs and 15 identical root duplicates were removed; differing root sources were archived. Structured JSON run records, saved counts, truth and 15 batch-5/scan logs remain. The obsolete recovery tarball was removed because Git push/pull now transfers the source changes.

The requested detector/X-CLIP case audit is in `vision3/best/test_colonial/exp_results/FUSION_cases_20261019.md`: both right 11, both wrong 2, detector-only right 5, X-CLIP-only right 3, on the same 21 matched people. The 45-track sheets have NO human labels yet; review_pack.slurm now prepares raw-footage snippets to avoid model-label bias. review_pack refuses overwriting completed packs and stops on cut errors. track_truth labels its old fusion formula explicitly; it is not b4. scale_up now resolves the static pixel threshold and requires exact chunk track/bin tables when checking output. No training, new inference, human labels or scale-up was performed locally.


## 43. Scope correction and presentation update (2026-10-19)

The request for 2025 cameras means a video with more actual detail than the 720x480 Colonial truth source, regardless of year. There is no requirement for one video per year. Corrine 706 is confirmed 960x540 at 15 fps (1.5x encoded pixels), but its fisheye lens and different scene confound a pure resolution comparison. The 2022 Curry Ford files previously reported at 720x480 do not establish higher-resolution evidence. `pick_busy.slurm` now passes --higher-res-only; the inventory records all candidate dimensions and scan_status while skipping detection scans on sources not exceeding 720x480 pixels. A higher encoded pixel count cannot prove footage was never upscaled or that people contain more usable detail.

No relabelling of the existing four truth clips is required. Exact annotated paths were recovered from saved run JSON and recorded in docs/VIDEO_PATHS.md. These refer to cluster videos; the Mac has no copy of them. The optional night/day spot-checks verify identities and prior uncertainty. The existing Corrine clip has no truth; new truth is needed only if a new higher-resolution test is scored. The separate 40-track task and own-night fine-tuning are on the back burner; full-day scaling is removed from the plan. Historical tools are retained without active run instructions.

The new presentation is reports/presentations/history/bike_weekly_meeting_10_19.pptx and follows active todo items. Research primary sources and limits are in docs/RESEARCH_METHODS.md: multi-scale/flip test-time inference and Grounding DINO are newly shortlisted frozen-model experiments; temporal feature aggregation was already discussed and remains a larger integration. BNE-DETR public source exists, correcting the older deck. No new method has measured project gains yet.


## 44. One-command research suite (2026-10-19; written locally, NOT yet run)

User has not pushed/pulled or submitted yet. README.md at the repository root is the single entry point. New files: submit_research.py, research_job.slurm, research_worker.py, research_detection.py, grounding_audit.py, test_research_recovery.py. Optional --tta / TTA=1 adds 960/1280 full-frame scale and horizontal-flip person proposals, maps flips to source coordinates, merges before tracking, and preserves the existing SAHI/full-frame vehicle path. The suite uses unique run names and existing truth to test TTA and sensitive candidates; a separate pinned Transformers environment runs Grounding DINO sampled-frame audits against saved b4 tracks. It does not convert bicycle boxes into counts.

The suite also runs the resolution-aware scan, matched baseline/combo/TTA on the known Corrine clip if present, zone/fisheye previews, a 12-minute raw review pack, conditional Zero-DCE retries if its checkpoint exists, and an afterany-dependent final report. Up to 22 tasks (normally 20 without Zero-DCE), four simultaneous GPU tasks maximum within this suite. Preparation downloads model files and performs an actual GPU smoke check on the cluster. Local tests cannot establish cluster/network/model compatibility or improved accuracy. Failed/skipped/incomplete tasks are recorded and incomplete experiment groups excluded from person-level score summaries. Full-day scaling, 40-track labels, own-night training, temporal detector integration and BNE replacement are excluded.


<a id="note-4"></a>
## README_colonial_validation.md
Original location: `vision3/best/test_colonial/code/README_colonial_validation.md`.

# Colonial North: validating the fine-tuned RT-DETR + X-CLIP bicyclist counter

Status as of 2026-10-05. Everything below is measured on 7 of the 48 recorded hours; read the caveats before quoting numbers.

## 1. Goal
Apply the existing bicyclist/pedestrian counting model (fine-tuned RT-DETR detector + zero-shot X-CLIP video-text classifier) to the
**Colonial North** camera and check, per 15 minutes, whether its counts agree with the human ground-truth counts.

## 2. Data and what was verified before any code was run
| Item | Finding |
|---|---|
| Camera / video | BL Colonial, camera SCU8OG, 720x480, 29.97 fps. 48 hourly mp4 files (about 3600 s each) = a 48-hour recording |
| Clock | Verified from the on-screen clock: file `.001` = 2019-07-10 00:00, `.008` = 07:00, `.025` = 2019-07-11 00:00. So file N starts at hour N-1 (the old pilot code assumed a different offset) |
| Ground truth | `Colonial_North_676806_07-10-2019.xls` (SpreadsheetML XML, not a real .xls). 192 fifteen-minute bins = 48 h. **89 bicyclists in total over the 48 h** (45 on day 1, 44 on day 2), bike lane + sidewalk. The 89 matches the GT CSV and `video_site_mapping.csv` |
| Mapping | video file N covers GT bins (N-1)*4 .. (N-1)*4+3 |
| Videos merged | None. Each hourly file is processed on its own and results are joined by clock time |

## 3. Method
1. **Detector:** fine-tuned RT-DETR (`rtdetr_v3`), classes: person, cyclist, car, truck, bus, other_vehicle.
2. **Tracker:** ByteTrack, with ID stitching across short gaps.
3. **Classifier:** X-CLIP (`microsoft/xclip-base-patch32`), zero-shot, applied to **person tracks only**; it chooses between *bicyclist* and *pedestrian*. It is not run on vehicles.
4. **Final label = X-CLIP's label.** The detector's own label (person/cyclist) is shown next to it for comparison.
5. A track counts once. It is assigned to the 15-minute bin of its midpoint frame, and must be visible at least 3 s (default).
6. Optional zones (road / bike lane / sidewalk) filter vehicles and give the bike-lane vs sidewalk split.

## 4. Validation design
- One job per hourly video. Tracking runs across the whole hour (no cuts at bin boundaries), then counts are split into 15-minute bins.
- **Outputs per run** (all under `test_colonial/`, nothing is overwritten): annotated clips (one per 15-min bin, each box shows the RT-DETR label and the X-CLIP label), per-bin counts, per-track table, run log, and an Excel workbook with sheets `Per_15min`, `Per_hour`, `Metrics`, `Tracks`, `Run_Log`.
- **Metrics:** per-bin bias (AI - GT), MAE, RMSE, WAPE, share of bins within +-1 and +-2, Pearson r; approximate count-matched precision/recall. The last two are *approximations*: ground truth is counts only, with no per-person labels. Hourly totals are reported too.
- Pipeline checks: GT total vs GT CSV vs mapping file, 15-min labels consecutive, chunk durations about 3600 s, chunks present.

## 5. Results

### Per hour (AI / ground truth)
| Hour | Run | Bicyclists | Pedestrians | Notes |
|---|---|---|---|---|
| 07:00 | run2 | 3 / 4 | 15 / 4 | construction cones counted as pedestrians (about 7 times) |
| 10:00 | run4 | 3 / 3 | 1 / 9 | |
| 12:00 | run5 | 5 / 3 | 1 / 2 | 12:45 bin over-counts (4 vs 2) |
| 13:00 | run5 | 1 / 3 | 5 / 6 | |
| 14:00 | run4 | 3 / 3 | 4 / 10 | bin-by-bin exact for bicyclists |
| 16:00 | run4 | 3 / 5 | 4 / 4 | bin-by-bin exact for pedestrians |
| 21:00 (night) | run5 | **0 / 3** | 1 / 7 | detector nearly blind in the dark |

Settings: runs 2 and 4 used defaults; run5 used a 1.0 s pedestrian minimum (see below). **Zones were not applied in any run** (the zones file was not on the cluster).

### Summary
| | Bicyclists | Pedestrians |
|---|---|---|
| Daytime hours (07,10,12,13,14,16) | 18 AI vs 21 GT | 15 vs 31 over the 5 daytime hours excluding 07:00 (07:00 is cone-contaminated) |
| Night hour (21:00) | 0 vs 3 | 1 vs 7 |
| Run4 (3 hours, 12 bins) | 9 vs 11, MAE 0.50/bin, 92% of bins within +-1, r = 0.71 | 9 vs 23, MAE 1.17/bin, count-matched precision 100%, recall 39% |
| Run5 (3 hours, 12 bins) | 6 vs 9, MAE 0.75/bin | 7 vs 15, MAE 1.00/bin |

Note: excluding the 07:00 cone hour, pedestrians over the other six hours including night are 16 AI vs 38 GT (about 42%).

**Reading:** bicyclists in daylight are counted within roughly 15% overall, with misses and some extras in individual bins. Pedestrians are heavily **under**-counted (about 40% recall). Night is a failure for both classes.

### Parameter experiments (offline, no re-run)
- **Minimum track duration, pedestrians:** shortening 3.0 s to 1.0 s raised pedestrian recall from 39% to 61% on run4 alone (precision stayed 100%), but on run5 the two extra tracks moved 269 and 336 px in 1-2 s (rider speeds, not walking speeds), and one of them had detector label 'cyclist'; they were most likely **cyclists labelled as pedestrians** (not yet confirmed clip by clip). X-CLIP is unreliable on tracks of 1-2 s. Pooled over 24 bins: 1.0 s gives recall 50% / precision 90% vs 34% / 93% at 3.0 s. Not a clean win.
- **Movement filter for static objects (cones):** rejects cones but would also reject real pedestrians who walk toward/away from the camera (only 21-29 px of net movement in some real tracks). Kept off.
- **Detector confidence cutoff:** helped only the 07:00 cone hour; on the other hours it only removed true tracks. Kept off.

## 6. Error analysis from watching the annotated clips
**Detector misses (never boxed):**
- 10:00-10:15: a go-kart and a bicyclist passing in the opposite direction, a second bicyclist later, and a pedestrian in shadow.
- 21:15-21:30: a cyclist approaching the camera, and 3 cyclists on the sidewalk of which only the last was detected. A cyclist clearly visible in the dark frame at 21:22:10 had no box.
- A person walking on the grass is not tracked until reaching the sidewalk.

**Classification errors (X-CLIP):**
- A pedestrian crossing the road was labelled bicyclist (twice).
- Labels change as a person approaches the camera: far away = pedestrian, close = cyclist (and the reverse).
- On short tracks X-CLIP is near a coin flip (e.g. 0.53 vs 0.47).

**The two labels fail in different places** (screenshots from the clips):
| Case | RT-DETR | X-CLIP | Truth |
|---|---|---|---|
| Real cyclist, daylight | person 0.57 (46% cyclist) | bicyclist 1.00 | bicyclist: X-CLIP right |
| Pedestrian crossing | person 0.72 (7% cyclist) | bicyclist 0.78 | pedestrian: detector right |
| Night, sidewalk rider | cyclist 0.61 (100%) | 0.53 / 0.47 | bicyclist: detector right |

This is the main finding for the label question. It motivates combining the two (see next steps).

**Ground truth is not perfect.** In the 07:00-07:15 clip the reviewer counted 2 riders where the GT bin has 1. Exact bin-by-bin matches in other hours show no global time offset, so differences are individual disagreements, not a clock shift.

## 7. What changed along the way (code versions)
| Version | Change |
|---|---|
| v10 | original sample script (untouched) |
| v11 | wall-clock aware; 15-min bins; one annotated clip per bin; per-bin CSV, track CSV, JSON run log; nothing overwritten |
| v12 | clips written as soon as each bin ends (header marked provisional) |
| v13 | optional static-object filter (`--person-min-disp`) |
| v14 | both labels on every person box; `Tracks` sheet in the Excel; detector-vs-X-CLIP agreement table |
| v15 | separate minimum durations for pedestrians and bicyclists |
| v16 | ground truth of the bin printed in the clip header; vehicle boxes state "X-CLIP: n/a (people only)" |

Bugs found by testing on a stand-in pipeline (fake detector/tracker on a synthetic video): the run log was saved under the wrong filename and the clip list got overwritten by a variable-name collision, both fixed. A mistaken `MAX_FRAMES` setting produced a 1-second test clip (it is a stop frame, not a count).

## 8. Limitations
- **Small sample:** 7 of 48 hours (about 14%), 28 bins, 24 bicyclists in the ground truth. One missed rider moves a bin by 100%.
- **Tuning and testing overlap:** thresholds were explored on the same hours they are reported on.
- **No zones in any run**, so bike-lane/sidewalk results are not reported and vehicles were not filtered.
- **One camera, one site.** Night video only from one hour.
- **Ground truth is counts only** (no per-person labels), so precision/recall are approximations. Human counters can disagree with the video.

## 9. Next steps (in priority order)
1. **Zones:** create `zones/colonial_north_v1.json`, confirm "zones loaded" in the log, verify the facility column and the vehicle filter on one hour.
2. **Night:** check the pending `night_dc015` test (detector confidence 0.15 on 21:15-21:30). If the detector still misses visible riders in the dark, night frames need to go into fine-tuning.
3. **Combine the two labels:** run `sweep_fusion_v1.py` on runs 4 and 5 to see if a rule using the detector's cyclist share plus X-CLIP's probability beats X-CLIP alone. Implement only if it holds on other hours.
4. **Revert the pedestrian minimum to 3.0 s** unless step 3 makes short tracks reliable.
5. **Fine-tune RT-DETR on Colonial frames** (day and night): sample frames around the missed events, label boxes, train, evaluate on whole hours held out of training. This is the real fix for recall; cost is mainly labeling time.
6. **Scale up** to block 1 (24 hours, about 46 GPU-hours) only after steps 1-5, reporting hourly totals, per-bin metrics and day/night separately.

## 10. How to reproduce
```bash
export ROOT=/orange/xiangyan/rithika/vision/vision3/best/test_colonial
cd $ROOT && source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
# one hour (array id = chunk number; 8 = 07:00-08:00):
sbatch --time=05:00:00 --export=ALL,RUN=myrun,ZONES_JSON=$ROOT/zones/colonial_north_v1.json --array=8 code/run_xclip_colonial_v16.slurm
# Excel + log:
python code/aggregate_colonial_v13.py --root $ROOT --run myrun --expect-chunks 8 \
  --gt-csv ground_truth/ground_truth_bicycle_counts_v2.csv --mapping-csv ground_truth/video_site_mapping.csv
# per-bin table / pedestrian tracks / offline sweeps:
python code/diag_colonial_v1.py --root $ROOT --mode bins --run myrun
python code/sweep_secs_v1.py --root $ROOT --run myrun --label PEDESTRIAN
python code/sweep_fusion_v2.py --root $ROOT --run myrun
# per-object accuracy (needs hand labels): template, fill true_label, eval
python code/track_truth_v1.py template --root $ROOT --run myrun --out $ROOT/validation/track_truth_myrun.csv
python code/track_truth_v1.py eval --file $ROOT/validation/track_truth_myrun.csv
```
Folder layout: `code/` scripts, `zones/`, `ground_truth/`, `counts/<run>/`, `annotated/<run>/<chunk>/`, `logs/<run>/`, `validation/`.

## 11. What the metrics measure (and do not)
| Metric | Measures | Limit |
|---|---|---|
| Per-bin MAE / bias / within +-1 | how close the AI count is to the human count in each 15 min | counts only: an AI miss and an AI false positive in the same bin cancel out |
| Count-matched precision / recall | approximate, from min(AI, GT) per bin | not per-object |
| X-CLIP vs RT-DETR vs combined, **count level** (`sweep_fusion_v2.py`) | which labelling rule gives counts closest to the human counts | same limit |
| **Per-object accuracy** (`track_truth_v1.py`) | accuracy, confusion matrix, precision/recall/F1 of RT-DETR, X-CLIP and the combined rule on tracks a person has labelled; detection recall including people the AI missed | needs a hand-labelled set (target 40+ real tracks); **not done yet** |

The ground truth has no per-person labels, so true per-object accuracy cannot be computed from it. Any accuracy figure for the two models
must come from the hand-labelled track set.

## 12. Is this the best approach? (brief literature check, not a systematic review)
- The overall structure (detect, track, classify, count) is the standard design for video-based bicycle/pedestrian counting. Examples:
  Kocamaz et al., "Vision-based counting of pedestrians and cyclists", WACV 2016 (a detector followed by a second stage that separates
  cyclists from pedestrians, with foreground, geometry and optical-flow cues); Shahraki et al., "A Trajectory Based Method of Automatic
  Counting of Cyclist in Traffic Video Data", Int. J. Artificial Intelligence Tools 26(4), 2017; a Louisiana DOT-funded study
  (HOG detection, tracking, classification; https://www.itskrs.its.dot.gov/node/209776).
- The unusual part here is the **zero-shot X-CLIP** classification stage (Ni et al., "Expanding Language-Image Pretrained Models for General
  Video Recognition", ECCV 2022, https://arxiv.org/abs/2208.02816). X-CLIP was built and evaluated for general action recognition,
  and its paper reports large gains in the few-shot setting when only a handful of labelled examples exist. Our clips are tiny, low-resolution
  person tracks of a few seconds, which is far from those benchmarks.
- The literature repeatedly names lighting and viewpoint as the main source of error and recommends training data covering varied
  conditions (Louisiana study above; Elshebli et al., YOLO-SORT under weather/lighting/viewpoint, ETASR). Night-time work fine-tunes
  detectors on night or infrared data (e.g. Yoshihara et al. 2024, RGB+FIR fusion with transfer learning). This matches our night failure.
- Reported accuracies are not comparable with ours: different sites, cameras and conditions. Examples for context only: an embedded
  cyclist counter reports counting accuracy of 78-82% in a real urban setting (JBCS 2026); a Pittsburgh-style classical system
  reported bicycle count error under 13% on its test sites (PBTC, SWOV record).

**Assessment, based on our own measurements:** the detector's missed riders (especially at night) are the largest loss, and the zero-shot
X-CLIP label is the second weakest link (it mislabels crossing pedestrians and flips with distance). The evidence points to
(1) fine-tuning the detector on Colonial day and night frames, (2) replacing or supplementing zero-shot X-CLIP with a classifier trained or
few-shot adapted on a small set of labelled Colonial tracks (possibly using simple physical features such as speed), and (3) reporting
per-object metrics from a hand-labelled set. These are recommendations to test, not results.

## 13. Still to fill in
- Result of `night_dc015` (detector threshold at night).
- Result of `bin2_v14b` (07:15-07:30 with static filter and lower detector threshold).
- Hand-labelled track set and the resulting per-object accuracy (`track_truth_v1.py`).
- Fusion sweep (colonial_run4 + colonial_run5): replace with the `sweep_fusion_v2.py` table.


<a id="note-5"></a>
## STUDY_NEXT_STEPS.md
Original location: `docs/runs/STUDY_NEXT_STEPS.md`.

> Reproduction guide for previously completed work. Start with [current results](../../manual/README.md) and [current tasks](../../README.md); no resubmission is required for repository cleanup.

# October 23 tasks — start here

This implements the new root todo.md request. Earlier “no full-day scaling” instructions describe the prior scope; the owner has now asked for broader study-video processing. No new GPU jobs have been submitted from this Mac. Do not rerun the completed October20batch.

## What is done

- Prepared a fixed-reference inventory/submit/report tool: `code/study_batch.py`.
- Local archive inventory: **1,919 unique files / 41 site/date pairs**, about1,919video-hours IF each file is one hour. Colonial North has48files (~48hours); all other recordings total1,871 nominal hours. Actual durations are not available on this Mac.
- Nominal processing estimate at2.8 GPU-hours/video-hour:5,373 GPU-hours total, ~112 days at two continuously available GPUs, excluding queues. Other-than-Colonial-North:5,239GPU-hours. These extrapolations are not throughput guarantees.
- One full Colonial North hourly source is the default pilot (chunk013, inferred12:00–13:00). Previously labelled clips total one hour across four separate windows; they are not the full recording.
- Added partial-track metric speed estimation after scene calibration. Two-line crossings are no longer required; real scene scale still is.
- Added conflict-area time-gap review and optional vehicle trajectory export for new runs. This is not confirmed near-miss detection or footprint PET/TTC.
- Wrote `reports/methodology/object_detection_study_20261023.tex`, including existing results, new workflow, limitations, research references and proposed multi-agent architecture. Compiled PDF: `output/pdf/object_detection_study_20261023.pdf`.

## Recommended next pilot: Pine Hills BL E

The owner asked for a shorter recording and an adjustable zone tool. Pine Hills BL E is the shortest matched recording: **25 nominal hourly files**, compared with Pleasant Hill Path31 and West Orange Path37. The count folder has road names/dates/directions but **no explicit camera coordinates found**; all 41count workbooks have blank Site Code fields. West Orange/Park in the speed workbook is a location clue, not a verified camera. See exp_results/study_inventory_20261023/SITE_SELECTION.md.

We do not need to process the full25 hours: start with one noon source hour. Exact GPS is not needed to draw lanes. Metric speed still needs identified image/map correspondences.

## First cluster commands

Push the repository changes from your Mac, then on HiPerGator:

```bash
cd /orange/xiangyan/rithika/vision
git pull --ff-only origin main
cd vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate

python code/study_batch.py inventory --probe \
  --out exp_results/study_inventory_live_20261023

python code/site_zone_setup.py \
  --inventory exp_results/study_inventory_live_20261023/inventory.csv \
  --site 'Pine Hills BL E' --out exp_results/pine_hills_zone_editor_oct23
```

Metadata probing is read-only apart from the new output folder; it opens each source and reads a frame, not the whole video. Missing files and unreadable metadata are listed. Change `--data-root` if videos are extracted somewhere other than `/orange/xiangyan/rithika/vision/pilot_clips`. Choose fresh output/tag names if these already exist. Submission is duplicate-guarded; if it fails partway, earlier jobs may already be running—read `logs/pine_hills_pilot_oct23/manifest.json`, do not blindly resubmit.

Download the entire `exp_results/pine_hills_zone_editor_oct23/` folder and open `index.html`. Choose the camera, click polygon vertices for road, bike lane, sidewalk, path and grass as applicable. Add another region for a separate area of the same type. Empty categories are allowed; finish or clear partial polygons. Enter your name, confirm the outlines, and export JSON. The editor autosaves drawings, supports importing a previous JSON, and shows backup JSON if downloads are blocked. Each page embeds its image, so no external frame link breaks.

Copy the exported JSON back to HiPerGator into `vision3/best/test_colonial/zones/study_20261023/`, keeping the filename. Then submit:

```bash
python code/study_batch.py submit \
  --inventory exp_results/study_inventory_live_20261023/inventory.csv \
  --scope pilot --site 'Pine Hills BL E' --pilot-chunk 13 \
  --zones-dir zones/study_20261023 --require-zones \
  --tag pine_hills_pilot_oct23 --go
```

This is one full hourly source, not the entire Pine Hills recording. Omit `--go` for a preview. For Colonial instead, omit `--site` and use another fresh tag. Read `exp_results/STUDY_pine_hills_pilot_oct23/RESULTS.md` and `outputs.csv` after completion. `outputs.csv` gives exact annotated filenames and the saved count/bin files. Check the full pilot video for missed cyclists, false detections, ID jumps and boundary fragments. Inspect actual runtime and memory via Slurm before scaling. No new truth campaign is required merely to run this pilot.

## Count and lane-use records for every processed source

Each source exports:

- `per_track_lane_use.csv`: source path, site, person/vehicle namespace, track ID, predicted user type, counted/rejected status, dominant facility, lane observation fractions, provisional visited facilities,15-minute midpoint bin and identity/zone quality flags.
- `counts_by_user_lane.csv`: one dominant-facility allocation per counted track.
- `counts_15min_by_user_lane.csv`: the same breakdown by15-minute bin.
- Existing original track/count CSVs and the structured run log; optional vehicle trajectories are enabled for study jobs.

The final study report combines sources into `all_tracks.csv`, `counts_by_site_user_lane.csv`, and `counts_15min_by_user_lane.csv`. Car/bus/truck/other vehicle classes remain separate where the model supplies them; the cyclist model category can include motorcycles/e-scooters and must not be advertised as independently verified mode truth. Lane counts are predicted track counts, not people verified across all source files. A person can move between facilities: fractions/visited-facility memberships retain this information, but they must not be summed as unique people. Dominance below70% or ambiguous/out-of-zone evidence yields uncertain; no zone file yields unassigned. Boundary fragments and identity switches require review.

Road-user lane classification is a **postprocessing step** using the user-marked zones. It does not change detection/count filtering on the new camera or pretend to have model accuracy. Colonial retains its existing inference masks. Rejected tracks remain in the per-track ledger but do not inflate counted totals. Original vehicle totals are retained even if historical vehicle histories are unavailable.

To build editors for all matched cameras, omit `--site` from the zone-setup command and download that whole editor folder. Save all exported JSONs in the same zones directory. Pass `--zones-dir ... --require-zones` to the study submit command when every selected camera must have marked lane areas.

If you change zones after inference, reclassify the saved tracks **without another GPU run** into a fresh output folder:

```bash
python code/study_batch.py lanes \
  --manifest logs/pine_hills_pilot_oct23/manifest.json \
  --zones-dir zones/study_20261023 \
  --out exp_results/pine_hills_lane_update_oct23
```

## All other study recordings

The one-hour pilot is recommended first. The full batch is prepared, not executed. Preview selection:

```bash
python code/study_batch.py submit \
  --inventory exp_results/study_inventory_live_20261023/inventory.csv \
  --scope all --exclude-site 'Colonial North' --tag study_others_oct23 \
  --zones-dir zones/study_20261023 --require-zones
```

Add `--go` to submit after sources/clocks are resolved. Use `--scope colonial` for all Colonial North files, `--scope all` without exclusion for all 41mapped site-date pairs, or `--scope all --site 'Colonial South'` for a specific study recording. At most two GPU jobs run concurrently by default; this bounds concurrency, not total cost. Jobs are source-file-sized, with a dependent final CPU report. Queuing/job-count limits can still stop a very large submission; the manifest preserves every returned job ID.

**62 multipart filenames do not encode a reliable source-start hour.** They are explicitly blocked, not assigned invented times or silently excluded. The inventory writes `clock_overrides_needed.csv`. Confirm each source's embedded first-frame clock and fill clock (`YYYY-MM-DD HH:MM:SS`), reviewer and evidence. Supply the completed CSV using `--clock-overrides /path/to/clocks.csv`. Plain hourly filenames use inferred clocks, which also require confirmation before scientific time-based comparisons. Source durations may overlap or contain gaps; verify continuous coverage and avoid double counting at file boundaries.

The mapping table's1,967 chunk sum is inflated relative to1,919 unique archived paths (Rinehart Sidewalk 96 versus 48). Lower-score mappings also need a camera/date check. Missing video extraction and unresolved mappings are not fixed by inference code. Site workbooks provide aggregate counts, not per-person truth; compare only aligned camera/channel/date/time coverage. Header GT is left unlabelled when valid person-level labels are unavailable. Other cameras do not inherit Colonial lane polygons; their own marked polygons drive the lane-use report. Study results are not automatically accuracy or unseen-site validation.

## Speed: partial trajectories with real ground scale

Current image motion is in pixels/second or body heights/second. A partial track cannot determine absolute mph without ground scale. The earlier35ft/30ftlengths belong to unidentified study segments, not the owner's drawn lane ends.

Need the exact Colonial camera/map location, then at least six identifiable persistent ground landmarks: four or more distributed fit points and at least two independent check points. All map/survey ground coordinates must share one local origin and axes, in metres. Distances from a ruler alone do not establish arbitrary 2D point coordinates. Google Maps measurements can support an estimate, not survey-grade precision. Match the historical road layout and camera view. Include a source URL/date, landmark descriptions and correspondence evidence. For fisheye footage, first establish a lens correction; a single planar mapping cannot remove lens distortion.

Template: `data/reviews/calibration/landmarks.template.csv`. Work on a copy; fill image_x/image_y in the720x480reference and local east_metres/north_metres, role fit/check, and evidence. Then:

```bash
python code/map_calibration.py \
  --landmarks /path/to/completed_landmarks.csv \
  --reviewer Rithika --source 'Map or survey reference, date and landmark evidence' \
  --out /path/to/colonial_map_estimate.json

python code/metric_trajectory_speed.py \
  --people exp_results/labelled_validation_20261020/people_lane_speed.csv \
  --calibration /path/to/colonial_map_estimate.json \
  --out exp_results/colonial_partial_track_speed.csv
```

For a new study road, fit `map_calibration.py` with `--site 'Pine Hills BL E' --date 2019-08-28` and that camera's actual reference size. Then use `metric_trajectory_speed.py --run-log /path/to/new_source_run_log.json --site 'Pine Hills BL E' --calibration /path/to/its_calibration.json --out /path/to/new_speed_estimates.csv`. This supports its counted pedestrians/cyclists and observed counted vehicles, while retaining unverified identity status. Do not reuse Colonial calibration.

These CPU commands are for **after** real landmark correspondence is supplied; the blank template is intentionally unusable. They estimate speed only for the existing seven bicycle truth candidates, preserve identity status, avoid extrapolation outside the landmark hull, reject long gaps/coasted positions, and require1.5-second continuous segments. Local one-second linear velocity fits produce median speed and dispersion. No model's counting/motion feature has been changed to these estimates.

The calibration report includes independent landmark residuals; low residuals are not proof of accurate speeds. Human identity confirmation and independent known-speed matches are still needed for speed validation. No mph has been calculated from invented distances or Excel means. Matching Excel records by nearest predicted speed is circular and prohibited.

## Conflict review without mph

A timing-based candidate method can start before mph validation: how soon does another road user enter the same small conflict area? FHWA defines PET around a common conflict location; this code is a simpler **ground-point/zone proxy**, not exact footprint PET or TTC.

Create a JSON with `ref_size`, a small camera-specific `polygon`, `reviewer` and `source`. A whole sidewalk/bike-lane polygon is too broad. Use observed entries/exits and visually check path overlap. Example fields (coordinates must be supplied, never guessed):

```json
{"ref_size":[720,480],"polygon":[],"reviewer":"Rithika","source":"Describe the observed conflict area and camera"}
```

For one source with the same frame origin and dimensions:

```bash
python code/conflict_zone_review.py \
  --people /path/to/source_trajectories.csv \
  --vehicles /path/to/source_vehicle_trajectories.csv \
  --zone /path/to/reviewed_conflict_zone.json \
  --fps 29.97 --frame-size 720x480 \
  --out exp_results/conflict_candidates_review
```

Use the actual FPS/resolution from that source's run log. Outputs are frame1-relative times, not necessarily clip-player times; account for the processed clip start. The optional3-second review window is not a validated safety cutoff. Simultaneous point occupancy is a separate flag, not proof of collision. Censored visits and missing intervals are rejected. Vehicle and person ID namespaces remain separate.

Historical files do not contain complete vehicle trajectories, so cyclist-car events cannot be recovered from them alone. New study jobs enable `EXPORT_VEHICLE_TRAJECTORIES=1`, an optional exporter in v19 that leaves detection/count decisions unchanged. Vehicle exports contain observed tracked vehicles, which can still miss stationary objects or occluded traffic. End-to-end GPU export and real conflict review are pending. Candidate counts must not be called confirmed near-miss counts.

## Multi-agent suggestions

Use agents to organize evidence, not invent geometry:

1. Data/coverage agent: verify camera, dates, channels and clock.
2. Perception-quality agent: flag occlusion, track fragments and label disagreement.
3. Calibration agent: check landmark evidence and held-out errors; stop metric claims without scale.
4. Deterministic conflict tool: calculate measures and retrieve exact source intervals.
5. Skeptical review agent: challenge ID switches and spatially unrelated paths, then send evidence to a human adjudicator.

Keep structured provenance for every event: video/frame interval, IDs, tool outputs, calibration version, uncertainty flags and reviewer. Multiple agents agreeing is not independent validation. This architecture is proposed, not an implemented or benchmarked agent system.

Research sources: [FHWA SSAM definitions](https://www.fhwa.dot.gov/publications/research/safety/08051/02.cfm), [OpenCV homography](https://docs.opencv.org/3.4.19/d9/dab/tutorial_homography.html), [BMVC traffic calibration paper](https://www.bmva-archive.org.uk/bmvc/2014/papers/paper013/index.html), [Google Maps distance measurement](https://support.google.com/maps/answer/1628031?hl=en).


## Parallel CPU speed-readiness job (while Pine Hills inference runs)

Added `code/speed_readiness.py` and `code/speed_readiness.slurm`. The full speed workbook was scanned locally:375deduplicated reference rows,23Colonial, no Pine-named street rows. This is reference availability, not new measured model speeds. An unknown street alias is not ruled out.

After push/pull, submit independently from cluster `vision3/best/test_colonial`:

```bash
mkdir -p logs
sbatch code/speed_readiness.slurm
```

This job requests2CPUs/4GB/30minutes and no GPU. It reads the original ZIP central directory and selected small JPEG/CUT companion files for41study cameras, plus ffprobe location metadata for any corresponding extracted noon videos. It does not extract whole videos, alter the detection run, communicate externally or infer physical track speeds. Candidate GPS/sidecar clues must be checked against the camera view; a camera coordinate alone is not ground-plane calibration.

The output folder is `exp_results/speed_readiness_JOBID/` (replace JOBID with the returned Slurm ID). Read `RESULTS.md`, `GPS_candidates.csv`, `camera_metadata.json`, and `reference_summary.csv`. Zero metadata clues is a possible legitimate outcome, not calibrated speed. Sampled sidecars lacking GPS do not prove the original camera had no location data. All source-speed rows/source cells are retained for future independently matched validation.

Local workbook-only report: `exp_results/speed_reference_readiness_20261023/RESULTS.md`; no new cluster results are claimed. Four new metadata/reference tests pass.


## Manual pilot reference prepared in parallel

Already run locally: `exp_results/pine_hills_manual_reference_20261023/RESULTS.md` plus raw15-minute channel counts, grouped user/side/facility counts, and worksheet coverage. For2019-08-28 12:00–13:00 the workbook records NBcyclists0bike-lane/1sidewalk, SBcyclists4bike-lane/0sidewalk, NBpedestrians0/0. SBpedestrian channels are absent, not zero. Keep raw sides separate until the actual camera side is established. Model-vs-manual comparison is pending detection results and that correspondence.

The pedestrian sheet has99quarter-hour rows (throughAug29 00:30), while bicycles has192(two days). This is a real coverage difference; do not compare full-file totals as if coverage were identical. A count total is not per-person identity/detection accuracy.

To independently regenerate on cluster after push/pull, no sbatch or GPU is needed; use a fresh output folder:

```bash
python code/study_count_reference.py \
  --workbook '/orange/xiangyan/rithika/vision/Bike Lane Study Counts/Pine_Hills_BL_E_690212_08-28-2019.xls' \
  --start '2019-08-28 12:00:00' --end '2019-08-28 13:00:00' \
  --out exp_results/pine_hills_manual_reference_repeat
```

Do not repeat this merely to occupy the queue; the saved result is ready. The useful pending work is reviewing the pilot output and returned calibration metadata.


## Speed-specific alternative: University SW Speed

Owner supplied camera_metadata.json; inspected all41camera entries locally. No readable location clues were found in sampled CUT previews (binary); explicit GPS remains0. Most sources were not extracted at the time of the audit. Raw metadata preserved at data/reviews/speed_readiness_47393224/camera_metadata.json.

A stronger speed candidate than Pine Hills is the purpose-labelled **SW Speed University** recording (September25,2019). The speed workbook contains78University sidewalk records, all55ft. This street-name match and folder label are promising, but do not establish which recording/person/segment each speed belongs to. No existing video has independently validated model mph.

Prepared one source hour08:00–09:00, chunk009. Selection uses the largest manual first-day daylight hourly cyclist count (11), earliest tie among08:00/14:00/16:00, without detector outputs. Manual data is North Sidewalk;11cyclist observations. Event-enriched selection is not an unbiased validation set. Reference records, empty person-link template and manual-hour counts: exp_results/university_speed_candidate_20261023/.

After push/pull, on HiPerGator with the environment active:

```bash
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
bash code/prepare_university_speed.sh
```

This extracts only one source file (~282MBlisted compressed/file size), probes metadata, isolates that hour's inventory, and builds a real-frame editor/manual-reference folder. No GPU or model job is submitted. It prints a fresh folder exp_results/university_speed_prepare_XXXXXX/; download its entire zone_editor subfolder. Open index.html -> University SW Speed. Send the downloaded folder/local path for image inspection and check the expected08:05clock. Endpoints, date/person links or alternate metric landmarks must be identified before claiming mph; marking area polygons alone is not speed calibration. Pine Hills detection can continue independently.


## October 24: map-free speed experiments

Run only after pushing/pulling the new code. From HiPerGator test_colonial:

```bash
sbatch code/speed_research.slurm
```

This requests one GPU for up to4hours and processes sampled original Colonial daytime frames for car-based scale estimation; it does not rerun the whole object-count study. Results: `exp_results/colonial_speed_research_JOBID/RESULTS.md`. Download the entire result folder. Dependencies include working torch/torchvision, scipy, numpy, cv2 and Git/network access for pinned author code and MaskRCNN weights. Missing dependencies/assets are reported per method, not hidden or substituted. Original raw Colonial chunk013 must exist at the configured path.

Implemented: ICCV2021 author pretrained transformer adapter (car instance masks, simple IoU association, seeded fitting); paper-inspired pedestrian head/feet average-height optimization. Local synthetic projection/recovery/input-refusal tests pass; author pretrained network loaded and inference smoke-tested. No real ICCV camera calibration executed locally: torchvision absent and original raw clip required. Existing saved Colonial data provides only1qualifying independent pedestrian track versus20required, so the local height experiment declined calibration. Three other researched methods remain NOT_IMPLEMENTED_MISSING_COMPONENTS (BMVC2014 full3D-box pipeline, Sochor2017 CAD/render assets,2026trained36-keypoint model); this command is not a claim to run all five papers.

`method_status.json` distinguishes completion/failures; `all_speed_estimates.csv` only exists when experiments yield rows. `descriptive_group_comparison.csv` compares available predicted group means to source workbook group means, explicitly not accuracy/ranking. No scale fitting or automatic winner selection uses the workbook. Distinct source people/times prevent matched validation; road-to-sidewalk plane transfer remains unverified. Geometry checks alone do not establish physical accuracy. No new Slurm job submitted by Codex.


October24 owner clarification: choose a method close to study speeds for exploratory use, not necessarily most accurate. Runner now outputs pedestrian AND bicyclist partial-track estimates from existing labelled truth candidates; car detections only estimate camera scale, no car-speed output. Workbook375speed rows across14street labels are bicycle references, not pedestrian reference speeds. `exploratory_closeness_ranking.csv` ranks available geometry-check-passing methods by absolute difference from study mean, per facility and using the same candidate set across competing methods; single-method output explicitly not a competition. No ranking when no valid estimates. This selection does not establish metric accuracy. The same one sbatch command runs the two implemented experiments and records remaining three as missing components; it does NOT implement all five. No fresh calibration job has run here.


Latest October24 scope (supersedes earlier pedestrian-output instructions): owner requests BICYCLIST SPEED OUTPUTS ONLY. `speed_research.py` now excludes pedestrian and motorcycle speed results. Calibration may still use car size or pedestrian height. Job also includes saved University manual A/B method and compares8.13mph to78University sidewalk study values (mean9.49mph; difference−1.36mph). One-person versus separate-group descriptive comparison, not matched validation. Versioned manual input in data/reviews/speed/university_manual_crossing_20261024.json; no University reinference required. Root README now contains all14reference streets,375bicycle rows, facility types, method implementation statuses and professor-facing interpretation. Existing sbatch command unchanged; upload/pull new input/code before submitting. Job isColonial automatic experiments plusUniversity savedmanual comparison, NOTall14site processing orall5paperimplementations.

Dedicated professor-facing statistics: [SPEED_REFERENCE_README.md](PROJECT_NOTES.md#note-7). Future speed outputs include the exact observed measurement intervals (date, source, clock times, clip seconds and frame ranges), not just the full-hour source label. Study-reference means are across measured cyclists, not per-hour/per15-minute values; reference observation clocks are unknown.


## Latest entry point: small multi-camera speed pilot (October24)

After pushing the latest code/docs/manual inputs and pulling on HiPerGator:

```bash
cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
source /orange/xiangyan/rithika/vision/yolo_env/bin/activate
python code/submit_speed_pilot.py --go
```

This one submission command checks key Python dependencies before submitting two jobs: CPU candidate-camera screening followed by the prepared Colonial GPU calibration experiments (afterany dependency). It prints the bundle folder `exp_results/SPEED_PILOT_TAG/` and records both job IDs in submission.json. Partial submission keeps the first job ID; do not blindly submit again if the second submission fails.

CPU screening selects15candidate camera/date sessions spanning13of14reference street labels. Silver Star has no candidate in current mapped inventory. Aliases are tentative, not independently verified reference-camera matches. First recording day, nearest-noon daylight source is fixed before looking at detector results/speeds. It extracts only needed source files from original ZIP, with a5GB cap on new extraction, and makes45-second excerpts at source05:00,20:00,35:00 plus JPG frames. At most33.75minutes across all15cameras, not hours of viewing per camera. Missing/unreadable/budget-limited sources are explicit, not zero cyclists. A resolution/sharpness table is a screening aid, not an accuracy ranking. No all-site detector/speed inference is performed in this stage.

Download the bundle after completion. Open camera_previews/index.html and speed_results/RESULTS.md. Review up to5first clearly visible bicycle encounters per usable camera, aiming for3where feasible; accept1–2with sample count disclosed. Inspect fixed intervals in chronological order, without selecting people whose estimated speeds happen to agree. Misses remain detection failures and cannot simply disappear from evaluation. No guarantee these short excerpts contain5cyclists; report fewer honestly. For later expansion choose additional intervals before inspecting their results. Prefer cameras with visible bicycles/ground contact and usable tracking, not just high pixel dimensions. Comparing model speed with separate street/facility study groups remains exploratory; cannot reconstruct hourly reference speeds from rows lacking clock times.

The GPU job still only attempts implemented Colonial methods and includes saved University manual timing; three full paper implementations/assets are pending. Screening other cameras does not automatically transfer Colonial calibration or zones. This bundle replaces the need to submit a separate screening command plus a separate speed command; do not submit the older direct speed job as well for the same purpose.4screening tests (including real synthetic-video extraction),8speed research tests and9study extension tests pass. Cluster job performance/real camera calibration remains untested here.


## Preview recovery after job47544655 (October24)

Original bundle: exp_results/SPEED_PILOT_20261024_183520. CPU job47544655 extracted2,931,198,701bytes but generated0/15previews because ffmpeg was absent fromPATH. That is an environment dependency failure, not bad camera quality. Speed job47544658 is separate; do not submit the full bundle again for preview recovery.

Push/pull the new preview_ffmpeg.py, retry_speed_previews.py, speed_site_screen.py and submit_speed_pilot.py. Activate yolo_env on the HiPerGator login node, then:

```bash
python code/retry_speed_previews.py exp_results/SPEED_PILOT_20261024_183520 --go
```

This resolves/checksFFmpeg withlibx264. If absent, installs the pinned imageio-ffmpeg0.6.0 wheel into ~/.cache/objectdetect/preview_runtime using pip --target (no changes to shared YOLO packages), then passes its absolute binary path to the CPU job. [Package source and bundled executable details](https://pypi.org/project/imageio-ffmpeg/0.6.0/). No GPU submission and no ZIP extraction. Original selected_sources.csv reused exactly; prior reports untouched. New output camera_previews_retry_TIMESTAMP under the same bundle, path and CPU jobID printed, manifest preview_retry_JOBID.json. Download that new directory when done and open index.html.

Future full submissions bootstrap/checkFFmpeg before job submission; workers also check before extraction and now exit with error if0previews, after retaining diagnostic reports. Per-camera encoder stderr appears in screening.csv/RESULTS.md. Seven screening/recovery tests, eight speed tests and nine study-extension tests pass locally. Cluster recovery still requires running above command; no retry submitted locally.

Preview retry47545063failed before processing because of a Python-version f-string quote incompatibility. Corrected and compiled all six runtime scripts on Python3.9.6; repeat CPU-only retry command after pushing/pulling this fix. No newextractionorGPU job needed for preview recovery. Speed47544658returned noautomaticestimates: read speed_results/method_status.json and iccv2021/error.txt before considering any GPU retry. SavedUniversity8.13mph does not imply automaticmethodsuccess.


## Diagnosed speed failure47544658 and targeted correction

Returned method_status.json: pedestrian-height fit lacks20independent qualifying tracks; ICCV adapter had fewer than10usable car tracks. No new automaticmph. These are implementation input guards, not proof that the published methods failed, and20/10are conservative project thresholds rather than paper-established optima. Universitymanual8.13mph is still only a saved result.

ICCV adapter previously sampled every15sourceframes (~2Hz) with last-frame greedyIoU, potentially fragmenting fast cars. Updated to every3frames (~10Hz), one-to-one HungarianIoU matching with constant-velocity box prediction and max0.3secondtrack gap. Score>=0.8, minimum boxdimension15px, >=4observations, netmotion>=30px retained; minimum10usablecartracks retained. Budget3000sampledframes (~5source minutes), early stop after20usablecartracks and15source seconds, independently of speed-reference agreement. This is a new adapter configuration, not a demonstrated improvement on real footage yet.

Always saves raw_car_observations.npz, tracking_diagnostics.json (detections/track lengths/usabletracks/sample rate/scanned seconds) and periodic annotated diagnostic_frames even when minimumtrackguard fails. Doesnotexportcar speeds. Existingpedestrian-heightmethod remainsdata-insufficient; no newgeometry orindependentspeedvalidation claimed. Afterpush/pull, a targeted GPUretry canuse `sbatch code/speed_research.slurm`; it doesnotrepeatcamera previews orZIPextraction. Newoutputexp_results/colonial_speed_research_JOBID. Do not alsoresubmitfullpilotbundle. Review preview retryresults separately. Eleven speedresearch tests andeightpreview/recoverytests pass includingPython3.9compilecoverage, plusnine studyextensionspreviouslypassed.

Owner now requests choosing shortest recording before further inference. See [duration guide](../../docs/VIDEO_DURATION_README.md): Pleasant Hill31sourcefiles is shortest speed-reference candidate, estimated31h—not a fully measured total. ColonialNorth48sourcesmeasured47.99h. Only short excerpts are needed; no new job submitted. Latest47545558learnedcalibration exists but0bicyclemph; report rebuilt locally withoutGPU.


Latestownerrequest: adaptive15-minute bicycle speedcomparison across12reference locations, Colonialexcluded/SilverStarunmapped. Maininstructions now at SPEED_REFERENCE_README.md top. Submit with python code/adaptive_speed_batch.py submit --max-windows4 --exploratory-road-plane-transfer --go (separate --max-windows and4 tokens when typing). Onejobarray12sites/concurrency2 +CPUfinalreport. Targetsone-thirdreferencecapped5/min3andboundedbystudyn=>Lee2,Columbia3,Daniels4,others5. Up to4consecutive15minwindows/site,stoponchronologicaleligiblecandidatequota,groupmeanpooledindividualspeeds. Provisionalbicycle/motorcyclelabels,identityunverified,road-planeextrapolationexplicitandstrictresultsretained. Nojobsubmittedlocally; exactREADMEcommandusesproper spaces.


## Latest update: independent site reports and Colonial included (October 24)

The adaptive speed batch now includes Colonial North: 13 candidate locations, Silver Star still unmapped. Each site writes RESULTS.md/comparison.csv/status.json at startup, after every completed 15-minute window, and on caught failure. Human-readable site folders contain calibration diagnostics and windows/wNN inference logs/settings/raw output references. No waiting for other sites. Global aggregation remains an afterany job. Colonial source clocks now use the selected source hour with chunk 1, independent of array index. Colonial pooled study mean is explicitly not facility-matched validation. Code prepared locally; not submitted here.

Run after pushing and pulling updated code:
```bash
python code/adaptive_speed_batch.py submit --max-windows 4 --exploratory-road-plane-transfer --go
```

Tests: 39 local checks passed. GPU model execution has not been run locally.


<a id="note-6"></a>
## RESEARCH_METHODS.md
Original location: `docs/RESEARCH_METHODS.md`.

> **Implementation update:** TTA is now an optional pipeline flag; Grounding DINO is implemented as a separate sampled-frame proposal audit. Both are submitted by code/submit_research.py. Local code tests pass; no new GPU experiment result exists yet. Read the root README.md for submission. Temporal feature aggregation remains unimplemented.

# Additional detection methods — primary-source review, 2026-10-19

Scope: improve detection before wider application; no own-night training or 40-track labelling campaign is active. Search of the project README/code found no implemented multi-scale/flip test-time augmentation or Grounding DINO. Temporal detection was already discussed, so it is not presented as a newly discovered idea. None of the ideas below has a measured gain on these clips yet.

## First experiment: multi-scale and horizontal-flip inference (TTA)

Run the same frozen detector on resized and left/right-flipped views, map boxes back into the original frame, then merge duplicates before tracking. This is different from the existing tile-only approach. It could recover detections sensitive to scale or pose, but adds computation and may add false boxes. The [official YOLOv5 TTA guide](https://docs.ultralytics.com/yolov5/tutorials/test-time-augmentation/) documents this approach and a speed/accuracy trade-off for YOLOv5. That benchmark is NOT evidence of a gain for this RT-DETR model. RT-DETR integration needs explicit transforms and inverse box mapping; do not assume augment=True implements it. Keep the original image view in the union and test with/without the same fusion rules.

## Second experiment: an independent pretrained proposal detector

[Grounding DINO's official repository](https://github.com/IDEA-Research/GroundingDINO) provides code and pretrained models for text-prompted detection. Use prompts such as person / bicycle / motorcycle to inspect hard frames that RT-DETR missed. A bicycle box alone is not proof of a cyclist; preserve the current class semantics and verify rider association. First compare proposal recall and extra false regions offline, before any union into the counting pipeline. Our recommendation to try it is an inference from its different training/model, not a demonstrated advantage on night/fisheye traffic. This differs from the existing optional COCO-person ensemble; no new model was installed or substituted.

## Larger option already discussed: temporal feature aggregation

[Flow-Guided Feature Aggregation (ICCV 2017)](https://arxiv.org/abs/1703.10025) aligns and combines neighbouring-frame features for detection under degraded appearance. ByteTrack links detections AFTER they occur; temporal feature aggregation can improve the detector input/features themselves. It is not the existing optical-flow box coasting. Research code exists, but the old architecture is not a drop-in RT-DETR flag; porting and validation are substantial work. Consider only after cheaper frozen-model experiments.

## Clarification: BNE-DETR and background proposals

[Public BNE-DETR code exists](https://github.com/luy02735-lang/BNE-DETR). The old deck's no-ready-made-code claim is corrected. Available pretrained weights, supported classes and environment compatibility still need verification; no claim that it is ready to replace this pipeline. Background subtraction plus crop re-detection was already proposed in the README; it is not new research here, and basic MotionDiag already generated too many candidates.

## Evaluation that makes a useful conclusion

Use the existing four truth-labelled clips first, so no relabelling is required. Compare counted-and-correct people, entirely missed people, wrong class, rejected short tracks, extra counted tracks and runtime against b4_combo_static5. More boxes alone is not success. Freeze any selected settings, then score a NEW higher-resolution clip from any year; only that new clip needs its own human truth. Do not tune on the two known errors and then call improvement on those same examples independent validation.

Higher-resolution screening uses encoded width x height > 720x480, not year. Inspect lens distortion, compression and the pixel height of people as well: a larger frame does not guarantee more useful person detail, and upscaled footage does not create evidence.


<a id="note-7"></a>
## SPEED_REFERENCE_README.md
Original location: `docs/SPEED_REFERENCE_README.md`.

# Bicyclist speed references — plain-language guide

## Reading the count and speed samples correctly (October 25 clarification)

The current [manual comparison](../../manual/README.md) explains the sampling and lists available recording hours for all 14 speed-reference locations. A fixed first-day hour nearest noon was selected before looking at results; the manual pack retains positive study-count bins within that hour. Aloma therefore has 45 minutes of selected footage and 4 study-count cyclists. Its separate 26-record speed sample has no linked clock times. Mighk Wilson confirms that speeds were measured from study video at half-speed and corrected in the calculation; some corridors had separate speed-analysis visits. The exact source recordings/clock times for the26Aloma speed rows remain unmatched;26is neither a detector total nor a48-hour count. Most full-recording lengths are inventory estimates; only Colonial North has complete measured duration metadata locally.


## Latest run: adaptive15-minute bicycle speed comparison

Updated October24,2026. This is prepared code, not a completed result. The owner requested combining consecutive15-minute segments until a small target sample is collected. Colonial North is included in this latest batch because its automatic bicycle speeds remain unfinished; Silver Star has no mapped footage. Thirteen candidate reference locations are planned, using one camera each.

### Sample targets

Target = min(study sample,5,max(3,ceil(study sample/3))). This is a practical exploratory quota, not a statistically powered validation sample. It gives2forLee,3forColumbia,4forDaniels and5forotherlocations.

| Reference location | Study cyclists | Study mean mph | Target candidates | Camera |
|---|---:|---:|---:|---|
| Aloma | 26 | 13.58 | 5 | Aloma Path |
| Baxter | 14 | 16.77 | 5 | Baxter |
| Carroll | 15 | 11.89 | 5 | Carroll NBL |
| Colonial | 23 | 9.54 | 5 | Colonial North |
| Columbia | 9 | 12.24 | 3 | Columbia Ave |
| Daniels | 11 | 11.95 | 4 | Daniels Path |
| Edgewater | 50 | 12.02 | 5 | Edgewater N |
| Lee | 2 | 8.73 | 2 | Lee Road N |
| Pleasant Hill | 41 | 9.86 | 5 | Pleasant Hill Path |
| Rinehart/CST | 25 | 12.92 | 5 | Rinehart Path |
| University | 78 | 9.49 | 5 | University SW Speed |
| West Orange/Park | 25 | 10.77 | 5 | West Orange Path |
| Winter Park | 13 | 16.08 | 5 | Winter Park Rd Speed |

### How the run works

1. Estimate a separate camera calibration from cars for each source. Cars supply scale; no car or pedestrian speeds are output. If calibration fails, stop that site and report the cause rather than process an hour without usable scale.
2. Run the fixed reference detector/tracker/count filters on12:00–12:15 of the selected source, then12:15–12:30, etc. Source clocks are filename-based and exact saved measurement intervals are retained. The selected noon hour is fixed beforehand and is not chosen by speed agreement.
3. Accumulate chronological bicycle candidates with counted status and sufficient continuous trajectory observations. Reject boundary-censored tracks to reduce cross-segment duplication; within-segment fragmentation can still duplicate people.
4. Stop as soon as the quota is reached, after the completed15-minute segment. If a segment has extra candidates, select earliest eligible ones, not those closest to study speed. Mean = sum of selected per-candidate speeds divided by candidate count, not mean of segment means.
5. Maximum4segments/60minutes per location in this first run. If the target is not met, preserve the smaller sample and label it incomplete. Maximum13hours of source footage across13locations; actual processing time is model/GPU-dependent. Only2GPUsite jobs run concurrently.

### Interpretation

The current model combines bicycle/motorcycle categories; these are provisional bicycle candidates until visually checked, not confirmed distinct bicyclists. Cars may calibrate the road, but sidewalks/paths can be elevated. The explicit exploratory transfer flag below permits applying that road-plane mapping outside its car-observation support. Each estimate records this assumption, fraction of observations inside support, and strict supported speed separately. No distance is tuned to the workbook, no missing speed becomes0mph, and no accuracy claim is made. Candidate camera/facility aliases and recording correspondence remain unverified. A close group mean is the requested exploratory comparison, not matched-person validation.

### One submission command

After pushing/pulling updated files, from vision3/best/test_colonial with yolo_env active:

```bash
python code/adaptive_speed_batch.py submit \
  --max-windows 4 --exploratory-road-plane-transfer --go
```

Without --go it only prints the plan. The command submits one12-task GPUarray (concurrency2) plus a CPUfinal report dependent on all site jobs finishing, including failed ones. It does not repeat the preview-screening jobs. Requires already-extracted source files, cached detector/XCLIP dependencies and model weights; missing sources/weights stop submission. Runtime and data-success are not yet verified on cluster. Partial job submissions are recorded in manifest.json; do not blindly resubmit if the final-report submission fails.

Output folder: `exp_results/ADAPTIVE_SPEED_TAG/`. Read `RESULTS.md` and `comparison.csv` for study mean, model-candidate mean, difference, sample size, quota, minutes and incomplete/failure status. `selected_candidates.csv` lists exact individual measurement intervals, source/annotation video paths and transfer/identity qualifications. Each site also retains calibration diagnostics, candidate exclusions and all processed-window records. The three other researched full-paper implementations remain pending; this batch uses the implemented ICCV2021 adapter.


Updated October 24, 2026. **These are speeds measured in the original study, not model predictions.** All 375 deduplicated records concern bicyclists across 14 workbook location labels. The labels do not identify exact camera coordinates.

## What does an average mean here?

Each record is one bicyclist timed through a measured section. Its speed is calculated from **distance ÷ travel time**, converted to miles per hour. For example,35 feet travelled in 2 seconds is about 11.93 mph. The stopwatch duration (such as 2 seconds) is not the time of day.

The table average is **the sum of individual recorded mph values divided by the number of cyclists measured**. It is **not per hour or per 15 minutes**. The speed rows do not provide a recording time of day or a time-bin assignment, so hourly or15-minute speed averages cannot be reconstructed from these references. Separate count workbooks have 15-minute counts, but those bins cannot automatically be assigned to these speed observations.

Median means the middle speed after sorting the observations; it is less affected by one unusually fast cyclist. Range means the slowest to fastest recorded value. These statistics describe the sampled cyclists, not necessarily all-day traffic.

## Average speed by location

| Workbook location | Cyclists measured | Average mph | Median mph | Observed range mph | Facility |
|---|---:|---:|---:|---:|---|
| Aloma | 26 | 13.58 | 13.96 | 8.30–17.92 | Path |
| Baxter | 14 | 16.77 | 15.99 | 11.50–26.36 | Travel Lane |
| Carroll | 15 | 11.89 | 10.80 | 8.34–16.18 | Travel Lane |
| Colonial | 23 | 9.54 | 8.81 | 5.29–19.86 | Bike Lane, Sidewalk |
| Colonial | 23 | 9.54 | 5 | Colonial North |
| Columbia | 9 | 12.24 | 11.42 | 9.63–15.13 | Bike Lane |
| Daniels | 11 | 11.95 | 12.68 | 8.59–14.36 | Path |
| Edgewater | 50 | 12.02 | 11.03 | 6.10–21.22 | Bike Lane |
| Lee | 2 | 8.73 | 8.73 | 6.49–10.96 | Travel Lane |
| Pleasant Hill | 41 | 9.86 | 8.96 | 5.17–19.57 | Path |
| Rinehart/CST | 25 | 12.92 | 13.53 | 5.04–18.92 | Path |
| Silver Star | 43 | 13.63 | 13.38 | 6.60–22.58 | Sidewalk |
| University | 78 | 9.49 | 9.14 | 4.61–17.10 | Sidewalk |
| West Orange/Park | 25 | 10.77 | 9.54 | 6.65–21.24 | Path |
| Winter Park | 13 | 16.08 | 16.02 | 10.14–23.69 | Travel Lane |

Locations with few observations, particularly Lee with 2, provide a limited reference. Different facilities should be compared separately; Colonial combines bike lane and sidewalk in the location-wide row.

## Facility-specific comparisons

| Location | Facility | Cyclists measured | Average mph | Measured section length, feet |
|---|---|---:|---:|---|
| Aloma | Path | 26 | 13.58 | 25 |
| Baxter | Travel Lane | 14 | 16.77 | 25, 48 |
| Carroll | Travel Lane | 15 | 11.89 | 12, 24, 39 |
| Colonial | Bike Lane | 12 | 11.11 | 35 |
| Colonial | Sidewalk | 11 | 7.82 | 30 |
| Columbia | Bike Lane | 9 | 12.24 | 28, 30 |
| Daniels | Path | 11 | 11.95 | 27 |
| Edgewater | Bike Lane | 50 | 12.02 | 24, 43 |
| Lee | Travel Lane | 2 | 8.73 | 47 |
| Pleasant Hill | Path | 41 | 9.86 | 25 |
| Rinehart/CST | Path | 25 | 12.92 | 30 |
| Silver Star | Sidewalk | 43 | 13.63 | 63, 83.5 |
| University | Sidewalk | 78 | 9.49 | 55 |
| West Orange/Park | Path | 25 | 10.77 | 29 |
| Winter Park | Travel Lane | 13 | 16.08 | 32, 67 |

The recorded section lengths come from the workbook; they are not distances between arbitrary video endpoints. The same lengths do not establish which part of the camera view was measured. The average uses original source_mph values. The source workbook uses a slightly rounded unit conversion, so exact recomputation may differ slightly; such arithmetic differences are not model errors.

## University: our manually timed example

- Subject: one red-top bicyclist travelling toward the camera in the September 25, 2019 University SW Speed video.
- Clip: 08:45–09:00.
- GateA crossing: player **07:02.50–07:03.00** (422.50–423.00seconds into the clip).
- GateB crossing: player **07:07.25–07:07.50** (427.25–427.50seconds into the clip).
- Generated clock approximately **08:52:02.50–08:52:07.50**. Burned source-video clock is roughly 2 seconds ahead; use player positions/evidence rather than treating those clocks as interchangeable.
- Owner map distance: 55.17 feet. Midpoint travel time: 4.625 seconds.
- Our manual result: **8.13 mph**, timing-only range 7.52–8.85 mph; map-distance/endpoint errors are additional.
- Study University sidewalk group: 78 cyclists, average **9.49 mph**, median 9.14 mph, range 4.61–17.10 mph.
- Our one-person estimate is **1.36 mph below** the study group average. This is a descriptive comparison, not the same cyclist measured twice and not automatic tracker validation.

## What HiPerGator reports will show

The speed experiment exports bicyclist speeds only. Calibration may use cars or human height, but car/pedestrian speeds and motorcycles are excluded from the speed output. Current automatic experiment covers existing Colonial bicycle candidates, not all 14 locations; the University manual example is included without repeating GPU inference.

For each estimate, the report and CSV record:

1. Method, location/source video, recording date, cyclist/track identity and facility.
2. Exact saved-video clock intervals actually used for measurement, plus clip-relative seconds and frame intervals. Missing/occluded portions are not silently included.
3. The estimated mph and calculation type. Partial-trajectory methods report the median of local velocity windows of approximately 1 second, within usable continuous track segments; the manual gate method reports average speed over one A–B journey.
4. Whether an estimate was unavailable because calibration or tracks were insufficient. A missing speed is not 0 mph.

If several cyclists are summarized together, their count and contributing measurement times must accompany the group average. These results are not automatically hourly averages. Current exploratory rankings compare the same cyclist candidate set across methods within a facility. The separate study reference group has unknown observation times; closeness is not matched-person accuracy.

After pushing/pulling updated files, run from vision3/best/test_colonial:

```bash
python code/submit_speed_pilot.py --go
```

The command submits a CPU preview job for15candidate cameras (13reference locations; Silver Star unmatched), then the prepared Colonial GPU experiments. Download `exp_results/SPEED_PILOT_TAG/` and open `camera_previews/index.html` to screen fixed short daytime excerpts. It does not calculate speeds across all locations yet. Read `speed_results/RESULTS.md`, `all_speed_estimates.csv` (if any estimates succeeded), `university_manual_comparison.csv` and `method_status.json`. Three researched methods still lack full implementations/assets; the report explicitly marks them pending.

## Sources and calculation files

- Original workbook:`bicyclist speeds.xlsx` in Bike Lane Study Counts. Original file is unchanged.
- [Extracted individual reference records and workbook cell addresses](../../vision3/best/test_colonial/exp_results/speed_reference_readiness_20261023/all_reference_records.csv).
- [Calculated per-location statistics](../cluster_returns/20261024/speed_reference_summary.csv).
- [University manual crossing inputs](../../data/reviews/speed/university_manual_crossing_20261024.json).
- [University video evidence and calculation](../cluster_returns/20261024/university_map_speeds/RESULTS.md).
- [Current command guide](PROJECT_NOTES.md#note-5).


Preview generation dependency: FFmpeg withlibx264 is checked before extraction. The launcher can install an isolated bundled binary if needed; see [preview recovery instructions](PROJECT_NOTES.md#note-5). The October24initial0/15preview result was missingFFmpeg, not evidence that all15cameras had unusable images.


### Counts and timestamps in adaptive results

comparison.csv now distinguishes all bicycle-labelled candidate tracks found, candidates counted by the fixed pipeline, speed-eligible candidates and the smaller chronological sample selected for the average. Candidate tracks are not verified unique cyclists; possible motorcycles/fragmentation require review. all_candidate_timestamps.csv records every candidate with track first/last-seen clocks, source/annotated-video paths, measurement intervals and rejection reasons; selected_candidates.csv identifies those used in the average. The final README summary shows found/usable/used counts and selected measurement times. Existing per-site candidate exports can regenerate these report fields without new inference.

Colonial already has four hand-labelled clips and saved detections:7actual bicyclists,13pedestrians,1motorcycle. The saved legacy evaluation counted6of7bicyclists; the remaining bicyclist was detected but rejected from counting. Counts/timestamps exist; physical bicyclemph is still not successfully validated. Do not rerun Colonial object detection solely to recover those counts/timestamps; reuse saved tracks and truth files. The latest owner request includes Colonial North in this adaptive batch; the selected noon hour is sampled, not all four labelled clips. Its location-wide 9.54mph study mean pools two facilities: bike lane 11.11mph (12 records), sidewalk 7.82mph (11 records). This pooled comparison is not facility-matched validation.

### Results saved separately as each site progresses

Under `exp_results/ADAPTIVE_SPEED_TAG/`, open a site folder such as `s03_colonial_north/RESULTS.md`. Use the exact folder names in `manifest.json`. Site reports appear at startup, update after every completed 15-minute window, and record failures immediately. You do not need to wait for the final combined report.

- `comparison.csv`: study mean, provisional model mean, found/countable/speed-usable/selected candidate counts and processed intervals.
- `all_bicycle_candidates.csv` and `all_candidate_timestamps.csv`: candidate timestamps, exclusions, speed intervals and annotated video paths, once candidates exist.
- `selected_candidates.csv`: candidates used in the mean, once any are selected.
- `status.json`: current stage, active window, completed windows and failure message. A stopped Slurm job may retain its last in-progress stage.
- `calibration/`: calibration geometry and diagnostics.
- `windows/w00/`, etc.: `pipeline_task.json`, `pipeline.log`, successful `result.json`, copied `run_log.json` and available raw track CSVs. Videos remain in their original annotated folders; the run log records their paths.
- `error.txt`: worker traceback on a caught failure. Slurm array logs remain in the batch root as `site_ARRAY_INDEX.log`, including calibration output or termination messages.

The combined root report is generated after all site workers finish. Empty or failed stages do not become zero-speed measurements. Existing submitted jobs retain their old manifest; inclusion of Colonial applies to a newly submitted batch using this updated code.

## Annotator provenance: Mighk Wilson (message supplied October 25)

Mighk explains that the consolidated **bicyclist speeds.xlsx** contains speeds he measured by stopwatch while watching video at half playback speed; he accounted for that playback rate in the calculation. Some corridors have multiple files because they used two cameras, and others because he returned later for speed analysis. Baxter was a speed-specific recording to increase the travel-lane cycling sample on two-lane streets without bike lanes.

This corrects the earlier working assumption that reference speeds were timed in person. The reference speeds are video-derived, but the message does not supply individual source filenames, clock times, measured endpoints or person identities. We must still match those before reporting per-person speed error. Do not multiply workbook mph by two again. Local formula inspection found distance/time formulas in primary sheets and explicit distance/(time/2) on Silver Star, so raw stopwatch-time conventions should not be assumed identical across sheets. We retain supplied mph values.

The count/speed records are useful human annotations for validation, but aggregate tables are not per-frame bounding-box training labels. See manual/README.md and manual/analysis/source_provenance.md for the current interpretation.

