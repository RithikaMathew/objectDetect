# Vision3 — current files

Use **best/test_colonial/** for the current system. The only retained overlay implementation is `best/test_colonial/code/xclip_overlay_v19_colonial.py`, launched by `code/run_xclip_colonial_v19.slurm`. It contains the duration, fusion, motion and static-filter rules used in the current reference. The aggregate reader is `aggregate_colonial_v13.py`.

| Folder | Purpose |
|---|---|
| `best/test_colonial/code/` | Current pipeline, experiment launchers, review/analysis tools and tests. |
| `best/test_colonial/truth/`, `zones/` | Existing ground truth and camera definitions. |
| `best/test_colonial/exp_results/`, `counts/`, `logs/` | Research results, saved predictions and structured run records. |
| `training/` | Retained training and dataset preparation utilities. |
| `comparison/` | Latest detector comparison v8, its v5 launcher, aggregate tool and distinct bicycle/pedestrian comparison. |
| `weights_tools/` | Weight cache/download helpers. |
| `tools/` | Distinct label audits, frame extraction and diagnostic utilities; some have v1 names because no newer replacement exists. |
| `finetune_runs/` | Existing training artifacts, preserved. |
| `zones/` | Other camera definitions, preserved. |

Superseded overlays v1–v18, preceding detector comparison versions, obsolete launchers, aggregate readers v11/v12 and preceding duplicate sweeps were removed. Existing experiment outputs and truth remain intact. Earlier versions that were tracked are recoverable from Git history; do not resurrect their launch commands as the current workflow.

For retained secondary launchers, submit from the `vision3` working directory, e.g. `sbatch comparison/run_compare_array_v5.slurm`. Training launcher: `sbatch training/run_finetune.slurm`. These are optional tools, not outstanding jobs. No model/download/training jobs were submitted during cleanup. Weight and data directory paths remain unchanged.

The completed final batch does not need resubmission. Start with the root README and docs/tasks/todo.md for current validation status. Cleanup details: docs/VISION3_CLEANUP_20261020.csv (paths relative to repo root).
