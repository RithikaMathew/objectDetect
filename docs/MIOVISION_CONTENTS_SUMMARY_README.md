# MioVision archive: one consolidated summary

Updated October 28, 2026. This document combines the downloaded MIOVISION_ARCHIVE_CONTENTS folder, the completed video-duration inventory, and the returned 10th Street duplicate checks.

## Main findings

**The archive contains videos plus supporting files. No confirmed Miovision-generated bicyclist speed estimates or measured calibration distances have been identified.** The four inspected TXT files do not contain identifiable speed records. Proprietary sidecars, compressed files and the nested ZIP have not been content-audited, so speed information cannot be ruled out in those files.

- **28,583 non-directory archive entries**: 9,085 MP4 videos and 19,498 other files.
- **9,057.34 hours of measured video playback**, across 179 site/view/device groups and recording years **2019–2026**.
- Hours are summed playback, not proof of continuous coverage or unique footage. Simultaneous camera views must not be added as distinct elapsed survey hours.
- Mighk’s separate bicyclist-speed workbook contains human video-stopwatch measurements, corrected for half-speed viewing. It is not a confirmed Miovision-generated speed export.

## All file types in the ZIP

| File extension | Files | What this tells us |
|---|---:|---|
| .0 | 401 | Numbered suffixes, including rotated .log.0 files; not a distinct confirmed data format. |
| .1 | 321 | Numbered suffixes, including rotated .log.1 files; not a distinct confirmed data format. |
| .bz2 | 1,281 | Compressed files; contents not opened by this audit. |
| .cut | 7,585 | Recording sidecars; contents not interpreted. |
| .db | 42 | Database-named files (all 42 are named Thumbs.db). |
| .jpg | 8,523 | JPEG image files; individual purpose not inspected. |
| .log | 495 | Log-named files; contents not inspected. |
| .mio | 200 | Miovision-named sidecars; contents not interpreted. |
| .mp4 | 9,085 | Video recordings. |
| .pastschedule | 167 | Past-schedule-named files; contents not inspected. |
| .schedule | 167 | Schedule-named files; contents not inspected. |
| .syslog | 167 | System-log-named files; contents not inspected. |
| .txt | 4 | Four small text files; all four contents inspected. |
| .upgradelog | 144 | Upgrade-log-named files; contents not inspected. |
| .zip | 1 | One nested ZIP; internal contents not inventoried. |

No direct CSV, XLS, XLSX, JSON, XML or PDF entries appear in this file list. Some TXT contents are comma-separated despite their .txt extension. Files inside compressed containers were not included as separately inspected entries.

**Nested archive:** MioVision Data/Temp/MetroPlan Miovision.zip. Its internal files have not been inspected; the totals above describe entries directly inside the supplied outer ZIP.

## What the four TXT files contain

All four are named with an _mac.txt suffix. Their rows contain a long identifier, a numeric timestamp, a readable timestamp, and a negative numeric value. There are no explicit cyclist IDs, speed units, measured distances or calibration endpoints. The meaning of the negative values is unverified; they must not be treated as mph.

| Recording folder | TXT bytes | Nonempty rows |
|---|---:|---:|
| 2021 Data / Central North | 600 | 8 |
| 2023 Data / N Orange | 300 | 4 |
| Bike Lane Study / MioVision Video / BL Columbia | 150 | 2 |
| Bike Lane Study / MioVision Video / NBL Curry Ford | 300 | 4 |

These four plain-text files do not establish what is inside the 1,281 .bz2 files.

## Why a street can appear more than once

**SCU8OG and SCU8PM are recording identifiers in filenames.** Their names alone do not establish device model, resolution, image quality, direction or AM/PM. A repeated street may have separate device-labelled recording sets; that does not by itself prove separate viewpoints or duplicates.

| 10th Street recording set | Session date | Video files | Numbered source files | Measured playback hours |
|---|---|---:|---|---:|
| SCU8OG | May 2, 2023 | 45 | .001–.045 | 44.75 |
| SCU8PM | May 2, 2023 | 48 | .001–.048 | 47.98 |

The roughly 3.23-hour difference does not explain why the sets differ. Deployment times, omitted files, recording interruptions or occurrence clipping remain possible; file counts do not distinguish them.

**Returned duplicate check:** the two selected original .023 files have different SHA-256 hashes. No cross-device 10th Street files share both size and CRC. This found no exact-duplicate candidates by that screen; it does not exclude re-encoded copies, overlapping scenes or clock offsets. Only the two sampled original files received SHA-256 comparison.

One-minute MP4 samples and JPGs were exported under HiperGator folder exp_results/10TH_DEVICE_COMPARISON_48154321/. Open its index.html to compare the scene, burned clock and moving objects. The samples use source seconds 60–120 of matching dated/chunk-labelled files; synchronization and relative camera quality have not been established.

## What the collection labels mean

- **Annual recordings:** archive folders named 2021 Data through 2026 Data. This does not mean a year of continuous video. Actual filename/session dates determine the years below.
- **Bike Lane Study:** the separate 2019 study-video branch. The full branch has 2,279 videos; the previously matched count-workbook subset has 1,919. These are different scopes.
- **Other:** the archive’s Other branch, including SunRail/SunRail Longwood recordings from 2020 and 2023. It is not a quality rating.
- **Site/view/device group:** a folder/device combination, not necessarily a unique street or physical camera. The 179 groups must not be described as 179 unique locations.

## Every recording group: years, video files and measured hours

All 9,085 video durations were measured. These totals exclude the uninspected contents of the nested ZIP. Multiple groups can overlap in time or view.

| Collection | Location / view folder | Device | Recording years | Known year count | Videos | Measured / total files | Total playback hours |
|---|---|---|---|---:|---:|---|---:|
| Annual recordings | 10th St | SCU8OG | 2023 | 1 | 45 | 45 / 45 | 44.75 |
| Annual recordings | 10th St | SCU8PM | 2023 | 1 | 48 | 48 / 48 | 47.98 |
| Annual recordings | Aloma East | SCU8OG | 2023 | 1 | 46 | 46 / 46 | 45.03 |
| Annual recordings | Aloma East | SCU8PM | 2023 | 1 | 48 | 48 / 48 | 47.98 |
| Annual recordings | Aloma West | SCU8OG | 2023 | 1 | 47 | 47 / 47 | 46.08 |
| Annual recordings | Aloma West | SCU8PM | 2023 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Anderson | SCU8PM | 2023 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Anderson St | SCU8PM | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Buenaventura | SCU8OG | 2023 | 1 | 44 | 44 / 44 | 43.83 |
| Annual recordings | Buenaventura | SCU8PM | 2023 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Casselberry Connector | MIOP000706 | 2026 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | Celery Ave | SCU8OG | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Central Blvd | SCU8PM | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Central North | SCU8PM | 2021 | 1 | 66 | 66 / 66 | 64.84 |
| Annual recordings | Central South | SCU8OG | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Church Ave | SCU8OG | 2023 | 1 | 46 | 46 / 46 | 45.03 |
| Annual recordings | Church Ave | SCU8PM | 2021 | 1 | 48 | 48 / 48 | 47.98 |
| Annual recordings | Church St | SCU8PM | 2023 | 1 | 48 | 48 / 48 | 47.98 |
| Annual recordings | Clarcona-Ocoee | SCU8OG | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Clarcona-Ocoee | SCU8PM | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Conway Rd | SCU8OG | 2022 | 1 | 44 | 44 / 44 | 43.48 |
| Annual recordings | Corrine Dr | MIOP000706 | 2025 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | Corrine Dr | MIOP000856 | 2025 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | Corrine Pop-Up | SCU8OG | 2022 | 1 | 48 | 48 / 48 | 47.19 |
| Annual recordings | Corrine/North Side Facing West Bound Traffic | SCU8OG | 2021 | 1 | 48 | 48 / 48 | 47.98 |
| Annual recordings | Corrine/South Side Facing East Bound Traffic | SCU8PM | 2021 | 1 | 48 | 48 / 48 | 47.98 |
| Annual recordings | Cross Seminole | SCU8OG | 2023 | 1 | 47 | 47 / 47 | 46.05 |
| Annual recordings | Curry Ford/North | SCU8OG | 2022 | 1 | 47 | 47 / 47 | 46.52 |
| Annual recordings | Curry Ford/South | SCU8PM | 2022 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Denning | MIOP000706 | 2025 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | Denning Path | SCU8OG | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Dillard | SCU8OG | 2021 | 1 | 48 | 48 / 48 | 47.98 |
| Annual recordings | Dillard | SCU8PM | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Division | SCU8PM | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Division Ave | SCU8OG | 2023 | 1 | 46 | 46 / 46 | 45.36 |
| Annual recordings | Division Ave | SCU8PM | 2023 | 1 | 96 | 96 / 96 | 95.98 |
| Annual recordings | E Colonial | SCU8PM | 2023 | 1 | 48 | 48 / 48 | 47.98 |
| Annual recordings | E Silver Star | SCU8OG | 2023 | 1 | 48 | 48 / 48 | 47.98 |
| Annual recordings | EE Williamson | SCU8PM | 2021;2024 | 2 | 96 | 96 / 96 | 95.98 |
| Annual recordings | Edgewater Dr | MIOP000706 | 2025 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | Emory Path | SCU8OG | 2022 | 1 | 46 | 46 / 46 | 45.01 |
| Annual recordings | Fern Creek North | SCU8OG | 2024 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Fern Creek South | SCU8PM | 2024 | 1 | 48 | 48 / 48 | 47.98 |
| Annual recordings | Fortune Road | MIOP000706 | 2026 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | Fortune Road | MIOP000856 | 2026 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | Fortune Road | SCU8OG | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Fortune Road | SCU8PM | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | George Ave & US 17-92 | SCU8OG | 2021 | 1 | 48 | 48 / 48 | 47.98 |
| Annual recordings | Goldsboro Path | SCU8PM | 2022 | 1 | 48 | 48 / 48 | 47.98 |
| Annual recordings | Gore | SCU8PM | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Ivey Lane | SCU8OG | 2024 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Keller Road | SCU8OG | 2024 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Kirkman | SCU8OG | 2023 | 1 | 48 | 48 / 48 | 47.98 |
| Annual recordings | Kirkman | SCU8PM | 2023 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Kissimmee Trail at Hoagland | MIOP000706 | 2025 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | Kissimmee Trail at Hoagland | MIOP000856 | 2025 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | Lake Fran Trail | SCU8OG | 2022 | 1 | 48 | 48 / 48 | 47.31 |
| Annual recordings | Little Econ Trail | SCU8OG | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Livingston | SCU8PM | 2022 | 1 | 48 | 48 / 48 | 47.98 |
| Annual recordings | Maitland Ave Crossing | SCU8OG | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Maitland Interchange Overpass | SCU8OG | 2023 | 1 | 47 | 47 / 47 | 46.92 |
| Annual recordings | Maitland SunRail Station | SCU8OG | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Mercy | SCU8PM | 2023 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | N Orange | SCU8OG | 2023 | 1 | 46 | 46 / 46 | 45.55 |
| Annual recordings | N Orange | SCU8PM | 2023 | 1 | 49 | 49 / 49 | 47.98 |
| Annual recordings | NOBT CS | SCU8OG | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | NOBT CS | SCU8PM | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Neptune Road Path | SCU8PM | 2022 | 1 | 48 | 48 / 48 | 47.98 |
| Annual recordings | Neptune SunRail | SCU8PM | 2022 | 1 | 48 | 48 / 48 | 47.98 |
| Annual recordings | North St | SCU8PM | 2024 | 1 | 48 | 48 / 48 | 47.98 |
| Annual recordings | North St E | MIOP000856 | 2025 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | Orange Blvd | SCU8OG | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Orlando Urban Trail | MIOP000706 | 2025 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | Orlando Urban Trail | MIOP000856 | 2025 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | Packwood Crossing | SCU8PM | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Pine Hills Center | MIOP000706 | 2025 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | Pine Hills Center | MIOP000856 | 2025 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | Pine Hills North | MIOP000706 | 2025 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | Pine Hills North | MIOP000856 | 2025 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | Pine Hills Trail/Balboa | SCU8OG | 2023 | 1 | 47 | 47 / 47 | 46.84 |
| Annual recordings | Pine Hills Trail/Indialantic | SCU8PM | 2023 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Pine St | SCU8OG | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Powers | SCU8OG | 2023 | 1 | 45 | 45 / 45 | 44.02 |
| Annual recordings | Princeton Packing District | SCU8OG | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Princeton Packing District | SCU8PM | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Rinehart | MIOP000706 | 2025 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | Rinehart | MIOP000856 | 2025 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | Rio Grande | SCU8PM | 2024 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Riverwalk | SCU8OG | 2022 | 1 | 47 | 47 / 47 | 46.66 |
| Annual recordings | Robinson | SCU8OG | 2021 | 1 | 37 | 37 / 37 | 36.10 |
| Annual recordings | Rock Springs Rd | MIOP000706 | 2025 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | Rock Springs Rd | MIOP000856 | 2025 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | S Semoran/S Semoran East | MIOP000856 | 2025 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | S Semoran/S Semoran West | MIOP000706 | 2025 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | SOBT | SCU8OG | 2023;2024 | 2 | 94 | 94 / 94 | 93.86 |
| Annual recordings | SOBT | SCU8PM | 2022;2024 | 2 | 96 | 96 / 96 | 95.97 |
| Annual recordings | SR 436 | SCU8OG | 2022 | 1 | 44 | 44 / 44 | 43.11 |
| Annual recordings | SR 436 | SCU8PM | 2022 | 1 | 38 | 38 / 38 | 37.31 |
| Annual recordings | Sandspur & Maitland Ave | SCU8PM | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Seminole Wekiva | SCU8PM | 2023 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Semoran Separated | MIOP000706 | 2025 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | Semoran Separated | MIOP000856 | 2025 | 1 | 49 | 49 / 49 | 47.99 |
| Annual recordings | Shingle Creek MetroWest | SCU8PM | 2022 | 1 | 49 | 49 / 49 | 47.76 |
| Annual recordings | Shingle Creek S Orange | SCU8OG | 2022 | 1 | 45 | 45 / 45 | 44.95 |
| Annual recordings | Shingle Creek S Orange | SCU8PM | 2022 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Shingle Creek/At Destination Pkwy | MIOP000706 | 2025 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | Silver Star/North Side | SCU8PM | 2022 | 1 | 48 | 48 / 48 | 47.98 |
| Annual recordings | Silver Star/South Side | SCU8OG | 2022 | 1 | 47 | 47 / 47 | 46.37 |
| Annual recordings | Slavia Road | SCU8PM | 2023 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Sligh | SCU8OG | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | South St | SCU8OG | 2021;2023 | 2 | 92 | 92 / 92 | 91.28 |
| Annual recordings | Spring Lake Path | SCU8OG | 2024 | 1 | 48 | 48 / 48 | 47.98 |
| Annual recordings | St Andrews | SCU8OG | 2024 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Sunset Dr | SCU8OG | 2024 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Sunset Dr | SCU8PM | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | US 17-92 | MIOP000706 | 2025 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | US 17-92 | MIOP000856 | 2025 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | US 17-92 Fern Park | SCU8OG | 2024 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | US 17-92 Fern Park | SCU8PM | 2024 | 1 | 48 | 48 / 48 | 47.98 |
| Annual recordings | US 192 | SCU8OG | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | US 192 | SCU8PM | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | University East | MIOP000706 | 2025 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | University West | SCU8OG | 2025 | 1 | 48 | 48 / 48 | 47.98 |
| Annual recordings | University West | SCU8PM | 2025 | 1 | 48 | 48 / 48 | 47.98 |
| Annual recordings | Virginia (East of Mills)/North Side Facing West Bound Traffic | SCU8PM | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Virginia (East of Mills)/South Side Facing East Bound Traffic | SCU8OG | 2021 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Virginia (West of Mills) | SCU8PM | 2021 | 1 | 25 | 25 / 25 | 24.71 |
| Annual recordings | W Colonial | MIOP000706 | 2025 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | W Colonial | MIOP000856 | 2025 | 1 | 48 | 48 / 48 | 48.00 |
| Annual recordings | W Colonial | SCU8OG | 2022 | 1 | 47 | 47 / 47 | 46.21 |
| Annual recordings | W Colonial | SCU8PM | 2022 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | Washington St | SCU8PM | 2022 | 1 | 48 | 48 / 48 | 47.99 |
| Annual recordings | West Orange Trail | SCU8OG | 2023 | 1 | 45 | 45 / 45 | 44.03 |
| Annual recordings | Westmoreland Path | SCU8OG | 2022 | 1 | 47 | 47 / 47 | 46.08 |
| Annual recordings | Winter Park Dr | MIOP000856 | 2026 | 1 | 48 | 48 / 48 | 48.00 |
| Bike Lane Study | Aloma Path | SCU8PM | 2019 | 1 | 48 | 48 / 48 | 47.99 |
| Bike Lane Study | Aloma SW | SCU8OG | 2019 | 1 | 48 | 48 / 48 | 47.98 |
| Bike Lane Study | BL Alafaya | SCU8OG | 2019 | 1 | 48 | 48 / 48 | 47.99 |
| Bike Lane Study | BL Alafaya | SCU8PM | 2019 | 1 | 48 | 48 / 48 | 47.99 |
| Bike Lane Study | BL Colonial | SCU8OG | 2019 | 1 | 96 | 96 / 96 | 95.98 |
| Bike Lane Study | BL Columbia | SCU8PM | 2019 | 1 | 49 | 49 / 49 | 47.98 |
| Bike Lane Study | BL Edgewater | SCU8OG | 2019 | 1 | 48 | 48 / 48 | 47.99 |
| Bike Lane Study | BL Glenridge | SCU8PM | 2019 | 1 | 48 | 48 / 48 | 47.99 |
| Bike Lane Study | BL Lakemont | SCU8OG | 2019 | 1 | 96 | 96 / 96 | 95.98 |
| Bike Lane Study | BL Livingston | SCU8PM | 2019 | 1 | 48 | 48 / 48 | 47.99 |
| Bike Lane Study | BL Par | SCU8OG | 2019 | 1 | 48 | 48 / 48 | 47.99 |
| Bike Lane Study | BL Pine Hills | SCU8OG | 2019 | 1 | 25 | 25 / 25 | 24.66 |
| Bike Lane Study | BL Pine Hills | SCU8PM | 2019 | 1 | 48 | 48 / 48 | 47.99 |
| Bike Lane Study | BL S Orange | SCU8OG | 2019 | 1 | 156 | 156 / 156 | 155.95 |
| Bike Lane Study | BL Speed Edgewater | SCU8OG | 2019 | 1 | 48 | 48 / 48 | 47.98 |
| Bike Lane Study | Daniels Path | SCU8PM | 2019 | 1 | 48 | 48 / 48 | 47.99 |
| Bike Lane Study | Daniels SW | SCU8OG | 2019 | 1 | 48 | 48 / 48 | 47.99 |
| Bike Lane Study | NBL Carroll | SCU8OG | 2019 | 1 | 48 | 48 / 48 | 47.99 |
| Bike Lane Study | NBL Clay | SCU8PM | 2019 | 1 | 96 | 96 / 96 | 95.97 |
| Bike Lane Study | NBL Curry Ford | SCU8PM | 2019 | 1 | 157 | 157 / 157 | 155.96 |
| Bike Lane Study | NBL Kaley | SCU8OG | 2019 | 1 | 48 | 48 / 48 | 47.99 |
| Bike Lane Study | NBL Lee Road | SCU8PM | 2019 | 1 | 96 | 96 / 96 | 95.97 |
| Bike Lane Study | NBL N Orange | SCU8PM | 2019 | 1 | 48 | 48 / 48 | 47.98 |
| Bike Lane Study | NBL Pine Hills | SCU8OG | 2019 | 1 | 48 | 48 / 48 | 47.99 |
| Bike Lane Study | NBL Pine Hills | SCU8PM | 2019 | 1 | 48 | 48 / 48 | 47.98 |
| Bike Lane Study | NBL Summerlin | SCU8OG | 2019 | 1 | 48 | 48 / 48 | 47.98 |
| Bike Lane Study | NBL University | SCU8OG | 2019 | 1 | 48 | 48 / 48 | 47.98 |
| Bike Lane Study | NBL University | SCU8PM | 2019 | 1 | 48 | 48 / 48 | 47.99 |
| Bike Lane Study | NBL Winter Park Road | SCU8PM | 2019 | 1 | 96 | 96 / 96 | 95.97 |
| Bike Lane Study | New folder | SCU8PM | 2019 | 1 | 48 | 48 / 48 | 47.99 |
| Bike Lane Study | Pleasant Hill Path | SCU8OG | 2019 | 1 | 31 | 31 / 31 | 30.01 |
| Bike Lane Study | Rinehart Road Path | SCU8PM | 2019 | 1 | 48 | 48 / 48 | 47.99 |
| Bike Lane Study | Rinehart Road SW | SCU8OG | 2019 | 1 | 48 | 48 / 48 | 47.99 |
| Bike Lane Study | Rinehart Road SW | SCU8PM | 2019 | 1 | 48 | 48 / 48 | 47.99 |
| Bike Lane Study | SW Speed University | SCU8PM | 2019 | 1 | 48 | 48 / 48 | 47.99 |
| Bike Lane Study | TL Speed Baxter | SCU8PM | 2019 | 1 | 48 | 48 / 48 | 47.99 |
| Bike Lane Study | TL Speed Winter Park | SCU8OG | 2019 | 1 | 48 | 48 / 48 | 47.98 |
| Bike Lane Study | WORT Path | SCU8OG | 2019 | 1 | 37 | 37 / 37 | 36.12 |
| Bike Lane Study | WORT Sidewalk | SCU8PM | 2019 | 1 | 48 | 48 / 48 | 47.99 |
| Other | SunRail | SCU8PM | 2020 | 1 | 48 | 48 / 48 | 47.99 |
| Other | SunRail Longwood | SCU8OG | 2023 | 1 | 48 | 48 / 48 | 47.98 |
| Other | SunRail Longwood | SCU8PM | 2023 | 1 | 48 | 48 / 48 | 47.98 |
| Other | SunRail Longwood/Longwood SunRail Upload | SCU8OG | 2023 | 1 | 7 | 7 / 7 | 7.00 |
| Other | SunRail Longwood/Longwood SunRail Upload | SCU8PM | 2023 | 1 | 7 | 7 / 7 | 7.00 |

## What was in the downloaded summary folder

| File | Role |
|---|---|
| all_files.csv | Complete direct-entry list: archive path, extension, uncompressed bytes and compressed bytes. |
| file_types.csv | Counts of every file extension; verified against all_files.csv. |
| small_text_contents.json | Full contents of the four small plain-text files. |
| 10th_st_sources.json | Device identifiers, session date, source counts and first/last source filenames for 10th Street. |

The downloaded folder is an inventory, not the original recordings. The 9,057.34-hour duration totals come from the separate completed duration audit; the duplicate results come from the owner-returned job output. No inference or new speed calculation was performed for this summary.
