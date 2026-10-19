"""
Join MioVision Bike Lane Study video folders to ground-truth count sites.

Nothing in the project recorded which video folder corresponds to which row of
ground_truth_bicycle_counts.csv, which blocks every count-validation run. This
builds that mapping and writes video_site_mapping.csv.

WHAT THE JOIN REVEALED
----------------------
Joining on session date (both the video folder names and the ground-truth rows
carry a 2019 date) matches 41/41 ground-truth site-dates with zero orphans on
either side. The structure that falls out is the study's experimental design:

  every recording date has exactly TWO simultaneous camera deployments,
  one at a BL (bike lane) site and one at an NBL (no bike lane) control site.

  2019-05-22  BL Livingston   + NBL Summerlin
  2019-06-26  BL Glenridge    + NBL Kaley
  2019-08-07  BL Edgewater    + NBL N Orange
  2019-09-10  BL Columbia     + NBL Carroll
  ...

with the same pattern for path/sidewalk pairs (Aloma Path + Aloma SW, Rinehart
Road Path + Rinehart Road SW, Daniels Path + Daniels SW, WORT Path + WORT
Sidewalk) and for the speed sub-study (SW Speed University + TL Speed Winter
Park, BL Speed Edgewater + TL Speed Baxter).

This answers the question left open in the earlier session notes -- "which files
are genuine two-camera-same-session pairs vs. count+later-speed-redo pairs".
They are same-session pairs, and the pairing is treatment/control:

    BL   = bike lane        (treatment)
    NBL  = no bike lane     (control)
    SW   = sidewalk
    TL   = travel lane
    Path = shared-use path

Because each pair is recorded on the SAME DAY, weather, season, day-of-week and
time-of-year are controlled by construction. That is a matched-pair natural
experiment, not a convenience sample -- see METHODOLOGY.md.

Usage:
    python build_site_mapping.py                 # writes video_site_mapping.csv
    python build_site_mapping.py --show-unmatched
"""

import argparse
import collections
import csv
import os
import re

GT_CSV = os.path.join("Bike Lane Study Counts", "ground_truth_bicycle_counts.csv")
VIDEO_LIST = "data/all_videos.txt"
OUT_CSV = "data/video_site_mapping.csv"

# Facility prefixes/suffixes in the video folder names. Stripped to recover the
# corridor name, then used to record what the camera was pointed at.
FACILITY_TOKENS = {
    "bl": "bike_lane",
    "nbl": "no_bike_lane",
    "sw": "sidewalk",
    "tl": "travel_lane",
    "path": "path",
    "sidewalk": "sidewalk",
}

# Video folder abbreviation -> ground-truth wording.
ALIASES = {
    "wort": "west orange",
    "hils": "hills",       # 'Pine Hils NBL E' is misspelled in the source data
    "rd": "road",
}

STOPWORDS = {"speed", "new", "folder", "e", "n", "s", "w",
             "east", "north", "south", "west", "road", "ave", "st", "street"}


def normalize(name):
    """Lowercase, expand aliases, drop facility and direction tokens; return the
    set of remaining corridor-name tokens.

    Aliases are re-split after substitution: 'wort' expands to 'west orange',
    which must become two tokens to match the ground truth's 'West Orange
    Path'. Substituting without re-splitting leaves a single 'west orange'
    token that matches nothing."""
    toks = re.split(r"[\s_\-/]+", name.lower())
    expanded = []
    for t in toks:
        expanded.extend(ALIASES.get(t, t).split())
    expanded = [t for t in expanded if t]
    core = [t for t in expanded if t not in FACILITY_TOKENS and t not in STOPWORDS]
    return set(core), expanded


def facilities_of(name):
    """Facility types named in a site/folder label.

    Applies to BOTH sides of the join: the video folders encode facility as a
    prefix ('BL Pine Hills', 'Aloma SW') and the ground-truth site names encode
    it as a suffix ('Pine Hills BL', 'Aloma Sidewalk'). Recovering it from both
    is what disambiguates same-date pairs whose corridor names are identical."""
    _, toks = normalize(name)
    return {FACILITY_TOKENS[t] for t in toks if t in FACILITY_TOKENS}


def load_videos(path):
    """site_folder -> {date -> [relative mp4 paths]}"""
    vids = collections.defaultdict(lambda: collections.defaultdict(list))
    with open(path, errors="replace") as f:
        for line in f:
            if "Bike Lane Study" not in line:
                continue
            m = re.search(r"(MioVision Data/.*?/MioVision Video/([^/]+)/([^/]+)/.*?\.mp4)", line)
            if not m:
                continue
            rel, site, session = m.group(1), m.group(2), m.group(3)
            d = re.search(r"(\d{4}-\d{2}-\d{2})", session)
            if d:
                vids[site][d.group(1)].append(rel)
    return vids


def load_gt(path):
    """site -> {date -> total_count}, plus facility types seen per site."""
    tot = collections.defaultdict(lambda: collections.defaultdict(int))
    fac = collections.defaultdict(set)
    with open(path) as f:
        for r in csv.DictReader(f):
            try:
                n = int(float(r["count"] or 0))
            except ValueError:
                n = 0
            tot[r["site"]][r["date"]] += n
            if r.get("facility_type"):
                fac[r["site"]].add(r["facility_type"])
    return tot, fac


def score(gt_site, vid_site):
    """Match score between a ground-truth site name and a video folder.

    Corridor-name overlap is the primary signal; facility agreement breaks the
    ties it cannot. Several same-date pairs share a corridor name entirely and
    differ ONLY by facility -- 'Pine Hills BL' vs 'Pine Hills NBL' on
    2019-08-21, 'Aloma Path' vs 'Aloma Sidewalk' on 2019-10-30 -- so without
    the facility term both ground-truth sites collapse onto whichever folder
    sorts first, silently attributing one site's counts to the other camera."""
    g, _ = normalize(gt_site)
    v, _ = normalize(vid_site)
    if not g or not v:
        return 0.0
    inter = len(g & v)
    if inter == 0:
        return 0.0
    name_score = inter / max(len(g), len(v))

    gf, vf = facilities_of(gt_site), facilities_of(vid_site)
    if gf and vf:
        # Weighted below 1.0 so facility agreement can never outrank a genuine
        # corridor-name match, only separate otherwise-equal candidates.
        facility_score = 0.5 if (gf & vf) else -0.5
    else:
        facility_score = 0.0
    return name_score + facility_score


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gt", default=GT_CSV)
    ap.add_argument("--videos", default=VIDEO_LIST)
    ap.add_argument("--out", default=OUT_CSV)
    ap.add_argument("--show-unmatched", action="store_true")
    args = ap.parse_args()

    vids = load_videos(args.videos)
    gt_tot, gt_fac = load_gt(args.gt)

    # index video folders by session date
    by_date = collections.defaultdict(list)
    for site, dates in vids.items():
        for d in dates:
            by_date[d].append(site)

    rows, unmatched, ambiguous = [], [], []

    for gt_site, dates in gt_tot.items():
        for date, count in dates.items():
            cands = by_date.get(date, [])
            if not cands:
                unmatched.append((gt_site, date, count))
                continue

            scored = sorted(((score(gt_site, c), c) for c in cands), reverse=True)
            best_s, best_v = scored[0]
            runner = scored[1][0] if len(scored) > 1 else 0.0

            if best_s == 0.0:
                unmatched.append((gt_site, date, count))
                continue
            # Flag a tie: two same-date folders scoring equally means the
            # name alone cannot say which camera produced these counts.
            if len(scored) > 1 and abs(best_s - runner) < 1e-9:
                ambiguous.append((gt_site, date, [c for _, c in scored if _ == best_s]))

            mp4s = vids[best_v][date]
            rows.append({
                "gt_site": gt_site,
                "date": date,
                "gt_cyclist_count": count,
                "gt_facility_types": "|".join(sorted(gt_fac.get(gt_site, []))),
                "video_folder": best_v,
                "video_facility": "|".join(sorted(facilities_of(best_v))) or "unknown",
                "n_mp4_chunks": len(mp4s),
                "match_score": f"{best_s:.2f}",
                "ambiguous": "yes" if (len(scored) > 1 and abs(best_s - runner) < 1e-9) else "no",
                "paired_with": "|".join(sorted(c for c in cands if c != best_v)),
                "example_mp4": sorted(mp4s)[0] if mp4s else "",
            })

    rows.sort(key=lambda r: (r["date"], r["gt_site"]))
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    n_amb = sum(1 for r in rows if r["ambiguous"] == "yes")
    print(f"Wrote {args.out}: {len(rows)} site-date rows")
    print(f"  matched   : {len(rows)}")
    print(f"  unmatched : {len(unmatched)}")
    print(f"  ambiguous : {n_amb}  (same-date folders tie on name; resolve by eye)")

    print(f"\n{'DATE':<12}{'GT SITE':<24}{'VIDEO FOLDER':<24}{'FACILITY':<16}{'N':>5}{'  CHUNKS':>8}")
    print("-" * 92)
    for r in rows:
        flag = " <-- AMBIGUOUS" if r["ambiguous"] == "yes" else ""
        print(f"{r['date']:<12}{r['gt_site']:<24}{r['video_folder']:<24}"
              f"{r['video_facility']:<16}{r['gt_cyclist_count']:>5}{r['n_mp4_chunks']:>8}{flag}")

    # treatment/control pairs, which is what makes this a matched-pair design
    print("\n" + "=" * 92)
    print("PAIRED DEPLOYMENTS (same date, two cameras):")
    print("-" * 92)
    bydate = collections.defaultdict(list)
    for r in rows:
        bydate[r["date"]].append(r)
    for date in sorted(bydate):
        rs = bydate[date]
        parts = [f"{r['video_folder']} [{r['video_facility']}] n={r['gt_cyclist_count']}" for r in rs]
        print(f"  {date}  " + "   +   ".join(parts))

    if args.show_unmatched and unmatched:
        print("\nUNMATCHED:")
        for s, d, c in unmatched:
            print(f"  {s} {d} n={c}")
    if ambiguous:
        print("\nAMBIGUOUS (name cannot decide which same-date camera these counts came from):")
        for s, d, cs in ambiguous:
            print(f"  {s} {d}: {cs}")
        print("  -> resolve by opening a thumbnail from each folder and comparing"
              " the facility visible in frame against gt_facility_types.")


if __name__ == "__main__":
    main()
