# Object detection and bicycle speed study

## Start here

- [Latest count and speed results](manual/README.md): study reference, automatic detection and manual annotations in one comparison.
- [MioVision archive summary](docs/MIOVISION_CONTENTS_SUMMARY_README.md): file types, camera years, video hours, duplicate checks and speed-information findings.
- [Bike Lane Study camera inventory](docs/BIKE_LANE_STUDY_INVENTORY_README.md): cameras associated with the count workbooks and speed-reference locations.
- [Current tasks](docs/TODO.md) and [HiperGator runbook](docs/HIPERGATOR_RUNBOOK.md).

The completed batches do not need resubmitting for this cleanup. Automatic and manual speed estimates are exploratory; comparing location averages with Mighk’s workbook does not establish person-level speed accuracy.

## Repository layout

| Folder | Contents |
|---|---|
| `vision3/best/test_colonial/code/` | Current experiment, reporting and submission scripts; paths preserved for HiperGator. |
| `vision3/best/test_colonial/zones/` | Canonical reviewed camera-zone JSON files. |
| `vision3/best/test_colonial/counts/`, `validation/`, `exp_results/` | Saved experiments, validation inputs and results used by reports. |
| `manual/` | Original manual annotations, latest comparison and trajectory analyses. |
| `Bike Lane Study Counts/` | Original count and human-measured speed workbooks. |
| `data/` | Camera mappings, metadata and review inputs. |
| `docs/` | Guides and summaries; `research/` holds research notes, `runs/` holds reproduction guides, and `history/` holds the handoff and methodology context. |
| `reports/cluster_returns/` | Evidence returned from HiperGator, grouped by date. |
| `reports/presentations/` | Latest presentation; earlier decks are in `history/`. |
| `reports/documents/` | Current Word camera inventory. |
| `reports/review/`, `reports/methodology/`, `output/pdf/` | Review artifacts and methodology reports. |
| `pipeline/`, `slurm/`, `scripts/` | Shared pipeline and cluster utilities. |

`sofar.md` and `todo.md` are your working notes. `resume.tex` remains at the root. Source datasets and older experiment evidence are retained because reports and comparisons still use them.

[Cleanup record](README.md) lists removals and moves.
