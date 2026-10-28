# Entire MioVision ZIP: camera locations, years, video counts and hours

Scope: every inventoried video in `MioVision_Data.zip`, including annual collections, Bike Lane Study and Other. [Study/count and Mighk speed-reference inventory](BIKE_LANE_STUDY_INVENTORY_README.md).

**Completed duration audit: 9,085/9,085 videos measured; 179/179 site/view/device groups complete. Total summed playback: 9,057.34 hours.** All listed years, video counts and playback hours now have returned inventory evidence. No new duration job is needed.

## What the labels mean

**Device identifier:** SCU8OG and SCU8PM are different identifiers appearing in recording-session names. We use them to separate recordings, not to rank camera quality. They are not established model names, resolution labels, north/south indicators or AM/PM recording labels. Miovision documents SCU IDs on its Scout control units, but the exact equipment configuration behind these two IDs has not been supplied. [Manufacturer checklist](https://miovision.com/wp-content/uploads/2024/01/miovision_scout_tune-up_checklist_EN_2022.pdf).

**Repeated street names:** 10th St appears twice because its folder contains recordings under both device IDs. This is not proven duplicated video. It also does not establish different viewpoints or simultaneous coverage; source sessions, images and clocks must be compared.

**10th Street coverage:** SCU8OG has45files totaling44.75playbackhours; SCU8PM has48files totaling47.98hours, both dated2023. The difference is about3.23playbackhours. We have not yet established whether this reflects a shorter deployment, missing chunks, different start/end times or occurrence-only recording. File count alone cannot distinguish those explanations or show which device has better quality. Exact session-date/chunk lists can be checked without rerunning the duration audit. Resolution/FPS needs original video metadata; we have not compared those two recordings.

**Annual recordings:** our grouping of archive folders named2021Data through2026Data. It is a folder category, not proof of continuous year-long recordings, repeated annual surveys, a shared physical camera or uniform camera specifications. The Recording years column comes from actual file/session dates; a2022folder can contain2021recordings.

**Bike Lane Study:** the separate2019study-video archive branch. **Other:** the actual Other archive branch, containing SunRail/SunRail Longwood folders with2020and2023recordings. It does not mean unusable or poor-quality footage.

## Non-video files and native speed information

The returned report-file listing contains four _mac.txt files (1,350bytes total). It lists no CSV, XLS, XLSX, JSON, XML or PDF entries. Therefore the ZIP is not videos only, but no conventional spreadsheet/CSV speed export has been identified by this scan. We have not yet inspected those four text contents; their filenames do not establish their purpose. Other sidecar formats and any nested archives were not content-audited by that selected-extension listing. The separate Bike Lane Study Counts spreadsheets are a different supplied dataset.

There are **no confirmed Miovision-generated cyclist speed records** in the inspected evidence. This is not proof that every proprietary sidecar lacks speed/calibration information. Mighk’s consolidated workbook contains human stopwatch-derived reference speeds, not confirmed native Miovision output. A device supporting speed studies does not establish that speed was measured or exported for these recordings.

A lightweight read-only check is available: `python code/archive_contents_summary.py`. It lists all ZIP file extensions,10thStsession dates/paths and the contents of text files up to8KiB. It extracts no videos, changes no recordings and needs no sbatch/GPU job. The resulting all_files.csv retains every non-directory archive member for follow-up, including file types omitted from the earlier report listing.

Years are taken from video filenames or dated recording sessions, not category labels. Site/view folders and device identifiers are kept distinct; aliases are not automatically merged into physical locations. “Unknown” means no parseable recording date, not zero years.

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

Inventory contains 9085 video files across 179 site/view/device groups. These groups are not a verified count of unique physical street locations. Unknown-date file counts and category paths are retained in camera_years.csv. Hours are shown only when every video for that group has measured metadata; partial subtotals stay in durations/by_camera.csv. Every duration row is measured or pending, never an estimate from file count.

## Measurement evidence

The owner returned the complete camera/year/hour summary from HiPerGator. Per-group totals are in camera_years_hours.csv; full per-video audit files remain in exp_results/MIOVISION_FULL_ARCHIVE_INVENTORY/durations/ on HiPerGator. Re-running the completed audit is unnecessary.

The archive contains 2,279 Bike Lane Study videos; the study/count-workbook mapping covers 1,919 of them. Those are different scopes, not conflicting totals. Site/view/device groups are retained separately even when they share a street name. Similar names or equal durations do not prove identical footage.

Playback hours measure the actual duration of files, not guaranteed continuous elapsed recording time. Occurrence-only footage may omit quiet periods. Device codes can be reused at different sites; they are not GPS coordinates. Separate years with similarly spelled streets are not automatically the same camera view.
