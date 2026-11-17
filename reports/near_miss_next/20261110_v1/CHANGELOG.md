# Before / after and limits

Before: read-only historical viewer, sampled-frame stepping, external videos, no annotation round trip, limited coverage/PTS exports. After: self-contained offline original-video review, exact decoded-frame stepping, zoom/pan, overlays/trajectories/gate display, preloaded six cyclist edges, physical-zone occupancy bracket review, footprint annotation, JSON/CSV export and JSON re-import/regeneration. Existing numerical reports and evidence remain intact.

New code: pipeline/near_miss_next.py, pipeline/near_miss_validation_engine.js, pipeline/near_miss_validation_viewer.html. New regression and browser tests accompany the versioned output. No original pipeline source or historical results are changed by this task. Code/source hashes are in build_manifest.json and provenance.csv.

Numerical additions: explicit coverage denominators, longest missing runs, decoded PTS audit, closest synchronized image proxies, signed relative image-axis speed, manual/detector comparison missingness, PTS-based conditional TTC sensitivity, reviewed PET interval engine. No unsupported physical distance, image TTC, occupancy boundaries, evasive action, independent ground truth, confirmed near miss or population rate is invented. The historical PET=0.294 error stays corrected.
