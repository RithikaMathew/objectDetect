i want to get the Speed =can u estimate using trajectory of object instead if only partial track is hard cuz really trial and error? add reference lines and get precise measurements via google maps​ ? i need to get speed solid in order to do like near miss cases right unless u have another method to find near miss cases?

do object detection using best model for all other videos​ that are in the bike lane study counts folder so i can validate and tell me how many hours total this would be? do u suggest doing colonial first cuz that whole thing is 1 hr right?

create a .tex file that documents this whole process, methodology, results we have so far etc. Add limitations section​

also give me suggestions to how i can incorporate Multiagent system into this object detection-like near miss cases​ etc

---

# Status — October 23, 2026

Start with [docs/STUDY_NEXT_STEPS.md](docs/STUDY_NEXT_STEPS.md) for the exact commands and remaining inputs.

- [x] Implement speed estimation from partial trajectories after ground-plane calibration: `map_calibration.py` and `metric_trajectory_speed.py`. No full gate crossing needed. Calibration uses independent check landmarks; estimates remain explicitly unvalidated.
- [ ] Obtain exact camera/map location and real landmark correspondences, then calculate physical speeds. Question sent to owner; map location not yet supplied. Do not invent distance from visible lane ends. Excel-person links and independent speed validation remain open.
- [x] Research an alternative near-miss review method and add conflict-zone timing screening. Optional vehicle trajectory export added to new reference runs. This is a point/zone candidate proxy, not confirmed footprint PET/TTC or validated near-miss detection.
- [x] Inventory archived study footage:1,919unique listed files /41site-date pairs; Colonial North48files, not1hourtotal. Nominal1,919video-hours; other-than-Colonial-North1,871hours. Old1967mapping total inflated by a duplicated Rinehart count. Actual durations need cluster probing.
- [x] Prepare one-command fixed-reference pilot/study submission plus final report. Default pilot processes one full Colonial North hourly source. Full-study scopes available; no new architecture sweeps.
- [ ] Run cluster metadata probe and pilot. This Mac has neither source footage nor Slurm.62multipart clocks need verification for full coverage. No study detection jobs have been submitted; prepared code is not completed inference.
- [ ] Execute wider requested recordings after the pilot/source clocks are resolved. All-source scope explicitly refuses missing metadata or unresolved clocks instead of silently dropping files. Predicted counts are not accuracy; cross-file duplicate identities and study coverage still require review.
- [x] Create methodology/results/limitations LaTeX report: [source](reports/methodology/object_detection_study_20261023.tex), [PDF](output/pdf/object_detection_study_20261023.pdf).
- [x] Document concrete multi-agent roles for data checks, perception quality, calibration, deterministic conflict calculations, skeptical evidence review and human adjudication. This is a proposed architecture, not a deployed agent system.

Estimate: at2.8GPU-hours per video-hour, full nominal footage requires5,373GPU-hours (~112days on2continuously available GPUs, excluding queues). This extrapolation is uncertain; benchmark one hour first. No validated mph or confirmed near-miss results are claimed.


## Follow-up incorporated: shorter road and lane records

- [x] Audit count workbooks for location fields:41count workbooks examined; Site Code blank throughout; no explicit GPS/intersection found in searched XLS/XLSX tables. Street names and directions are available.
- [x] Identify shorter candidates: Pine Hills BL E25nominal files (shortest), Pleasant Hill Path31, West Orange Path37. Prepare one-hour Pine Hills noon pilot; source durations and exact camera coordinates remain unverified. West Orange/Park is a workbook location clue, not a geolocation.
- [x] Add offline per-camera area editor: site_zone_setup.py. Supports road, bike lane, sidewalk, shared-use path, grass, multiple same-type regions, undo/reset, autosave, import and JSON export with confirmation/backup. Actual new-site frames must be extracted on the cluster.
- [x] Add per-source/per-site/per15-minute user-type and lane-use ledgers, including individual track records and uncertain/unassigned status. Optional vehicle export retains counted status. Postprocess edited zones without rerunning detection.
- [x] Extend partial-track speed CLI to counted users/vehicles from a new-camera run log with its own valid scene calibration.
- [x] Extract Pine Hills source frame and receive owner-confirmed zones. Validated and copied to vision3/best/test_colonial/zones/study_20261023/pine_hills_bl_e_45bfdf.json; preview checked.
- [ ] Establish map/landmark correspondence for physical speed; camera coordinates remain unknown. Area outlines do not supply metric calibration.
- [ ] Run the prepared one-hour Pine Hills pilot on HiPerGator, then inspect predicted counts and lane summaries before larger processing. No new GPU jobs submitted locally.

Verification: all15test modules pass; generated zone-editor JavaScript checks pass; nine-page LaTeX report compiled and visually inspected. No new source inference, physical speed measurement or confirmed near-miss result is claimed.

- [x] Add independent CPU speed-readiness job to audit source JPG/CUT GPS/location clues and MP4 metadata while detection runs. Full workbook scan completed locally:375deduplicated reference rows; no Pine-named street speed records.
- [x] Run speed_readiness.slurm on HiPerGator: job47393224completed; returned report shows41cameras audited,0explicit GPS candidates,375reference rows and0Pine-named rows.
- [x] Inspect supplied camera_metadata.json/textual clues locally: no usable location clues found. Metric calibration remains unresolved; the successful audit did not supply supported mph.

- [x] Prepare exact Pine Hills pilot-hour manual count reference, preserving raw channel sides, quarter-hour bins and missing values. Source worksheets differ in coverage (pedestrians99bins vsbicycles192); NB/SB bicycle counts must not be merged into a one-sided camera comparison. Detector comparison remains pending actualresults/camera-side correspondence.

- [x] Inspect supplied camera_metadata.json: no usable textual location clues in sampled CUT previews; GPS remainsunresolved. Prepare University SW Speed as an alternative with78University sidewalk speed references (55ft), one08:00–09:00source hour and11manual cyclist observations. Recording/person/measurement-segment correspondence still requires verification.
- [x] University preparation completed on cluster; real frame and owner zones visually checked. Canonical JSON saved in zones/study_20261023. No identifiable measured endpoints found.
- [ ] Submit University SW Speed 08:00–09:00 pilot after pushing/pulling the zone JSON; inspect counts, lanes and trajectories. Physical speeds and matched reference validation remain pending.

- [x] Prepare map-free speed research runner: ICCV2021 pretrained car-based adapter and paper-inspired pedestrian-height calibration; three synthetic tests passed.
- [ ] Run real Colonial car-based calibration on HiPerGator with sbatch code/speed_research.slurm. Existing saved pedestrian inputs insufficient (1qualifyingtrack); no new mph produced. Three other researched pipelines still need implementations/assets; aggregate workbook closeness cannot establish an independently validated winner.

- [x] Document14locations/375bicycle speed reference records in rootREADME; make speedexperiment outputs bicycle-only and add University manual8.13mph comparison versus9.49mph study mean. No new automatic calibration or matched-person speed validation claimed.
