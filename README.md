# Object detection and bicycle study

The current pilot is complete. Two car passes were visually reviewed; the only zero-clearance/TTC/PET alarm was a bicycle wheel labelled as a car. Physical passing distances remain unvalidated because the existing files do not establish the needed lateral geometry. **No new HiPerGator run is pending.**

## Results

- [Current handoff: speed, clearance and near misses](HANDOFF.md).

- [Clearance pilot: short summary](reports/clearance_pilot/final_review_20261109/START_HERE.md) · [Illustrated review](reports/clearance_pilot/final_review_20261109/review.html).
- [Count and speed results](manual/README.md): original manual annotations, same-video comparisons and limitations.
- [MioVision archive summary](docs/MIOVISION_CONTENTS_SUMMARY_README.md) · [Study camera inventory](docs/BIKE_LANE_STUDY_INVENTORY_README.md) · [Full archive inventory](docs/MIOVISION_ARCHIVE_INVENTORY_README.md).

## Workflows and reference

- [Clearance workflow and HiPerGator commands](docs/CLEARANCE_PILOT_RUN.md). Commands are for reproduction, not pending jobs.
- [Near-miss and passing-clearance next steps](docs/NEAR_MISS_CLEARANCE_NEXT_STEPS.md).
- [Speed workflows](docs/SPEED_WORKFLOWS.md) · [Saved video locations](docs/VIDEO_PATHS.md).
- [Research notes](<docs/research/Cyclist speed (mph) from monocular fixed cameras feasibility, literature, and pl.md>).
- [Historical detector results](reports/history/DETECTOR_RESULTS.md) · [Historical project notes](reports/history/PROJECT_NOTES.md).

## Folders

| Folder | Contents |
|---|---|
| `vision3/best/test_colonial/code/` | Current analysis/pipeline scripts, launchers and tests; HiPerGator paths preserved. |
| `vision3/best/test_colonial/counts/`, `truth/`, `zones/`, `logs/`, `exp_results/` | Detector outputs, truth, camera definitions and experiment evidence. |
| `manual/` | Original tire-click annotations and manual/automatic speed analyses. |
| `Bike Lane Study Counts/` | Original study workbooks and extracted count tables. |
| `data/` | Site mappings, camera metadata and review/calibration inputs. |
| `reports/cluster_returns/` | Original returned results, grouped by date. |
| `reports/clearance_pilot/` | One final clearance packet and portable ZIP. |
| `reports/presentations/`, `reports/documents/`, `reports/review/`, `reports/methodology/`, `output/` | Presentation/document artifacts and supporting research outputs. |
| `docs/` | Current workflow, inventory and research references. |
| `pipeline/`, `slurm/`, `scripts/`, `tests/` | Shared code, utilities and tests. |

Source data, scientific evidence, model assets and runtime paths were preserved. `resume.tex` is a separate personal file and remains unchanged. The [cleanup manifest](reports/maintenance/cleanup_20261109.csv) records removals and consolidation.
