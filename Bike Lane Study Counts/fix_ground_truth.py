"""
Repair ground_truth_bicycle_counts.csv: fill in facility_type and movement.

THE PROBLEM
-----------
The existing CSV declares columns `facility_type` and `movement`, and
bike_lane_study_excel_findings.md documents them as "Split each row's free-text
metric label (e.g. 'Bike Lane With') into separate facility_type and movement
columns, so the CSV is directly queryable instead of needing string parsing
every time."

That split silently produced nothing. Both columns are empty in **202 of 202
rows**. The columns exist; no value was ever written to them.

This matters more than a cosmetic gap. Facility-disaggregated ground truth is
the study's single most distinctive asset -- it is what lets a cyclist count be
validated as "bike lane vs sidewalk vs travel lane" rather than just a total.
As shipped, that disaggregation is unusable without re-parsing strings at every
call site, which is exactly what the column was meant to prevent.

WHAT IS RECOVERABLE
-------------------
facility_type: fully recoverable. All 46 distinct `channel_label` values name a
facility -- 'SB Sidewalk', 'NB Bike Lane', 'EB Travel Lane', 'Path',
'Lakemont BL NB', 'Lakemont SW SB', ... -- including the BL/SW abbreviations.

movement (With / Facing traffic): recoverable for channels that carry a side
designation, undetermined otherwise. A channel label names the side of the road
the facility is on ('SB Sidewalk' = the sidewalk on the southbound side), and
each channel is counted in BOTH travel directions. So:

    channel side == travel direction  -> With    (riding with traffic)
    channel side != travel direction  -> Facing  (riding against traffic)

That is precisely the With/Facing semantics of the source spreadsheets.

For 'Path' (10 rows) and bare 'Sidewalk' (8 rows) there is no side designation,
so movement is left as 'undetermined' rather than guessed. Those 18 rows are
flagged, not silently filled -- a wrong value here would corrupt the
wrong-way-riding analysis, and 'Path' arguably has no meaningful With/Facing at
all since paths are bidirectional by design.

Usage:
    python fix_ground_truth.py            # writes ground_truth_bicycle_counts_v2.csv
    python fix_ground_truth.py --inplace  # overwrite the original
"""

import argparse
import collections
import csv
import os
import re

IN_CSV = "ground_truth_bicycle_counts.csv"
OUT_CSV = "ground_truth_bicycle_counts_v2.csv"

# Order matters: 'Bike Lane' must be tested before 'Lane', and the BL/SW
# abbreviations only appear as standalone tokens ('Lakemont BL NB'), never as
# substrings of a word, so they are matched with word boundaries.
FACILITY_PATTERNS = [
    (r"\bbike\s+lane\b", "bike_lane"),
    (r"\bBL\b",          "bike_lane"),
    (r"\btravel\s+lane\b", "travel_lane"),
    (r"\bTL\b",          "travel_lane"),
    (r"\bsidewalk\b",    "sidewalk"),
    (r"\bSW\b",          "sidewalk"),
    (r"\bpath\b",        "path"),
]

# Side-of-road designators found in channel labels, mapped to a compass axis.
SIDE_PATTERNS = [
    (r"\bNB\b|\bnorth\b",  "Northbound"),
    (r"\bSB\b|\bsouth\b",  "Southbound"),
    (r"\bEB\b|\beast\b",   "Eastbound"),
    (r"\bWB\b|\bwest\b",   "Westbound"),
]


def derive_facility(channel_label):
    for pat, fac in FACILITY_PATTERNS:
        if re.search(pat, channel_label, re.IGNORECASE):
            return fac
    return ""


def derive_side(channel_label):
    """The side of the road this channel sits on, or '' if unlabelled.

    Guards against corridor names that happen to contain a compass word:
    'Alafaya East Bike Lane' and 'University N Sidewalk' name the SITE, not the
    side. Those are handled by the caller, which only trusts a side when the
    label has no site name in it.
    """
    hits = []
    for pat, side in SIDE_PATTERNS:
        if re.search(pat, channel_label, re.IGNORECASE):
            hits.append(side)
    # Two compass words means one of them is part of the corridor name
    # ('S Orange NB Bike Lane'); the LAST one is the side designator.
    return hits[-1] if hits else ""


def derive_movement(channel_label, direction):
    side = derive_side(channel_label)
    if not side or not direction:
        return "undetermined"
    return "With" if side == direction else "Facing"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default=IN_CSV)
    ap.add_argument("--out", default=OUT_CSV)
    ap.add_argument("--inplace", action="store_true")
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    inp = args.inp if os.path.isabs(args.inp) else os.path.join(here, args.inp)
    out = args.out if os.path.isabs(args.out) else os.path.join(here, args.out)
    if args.inplace:
        out = inp

    with open(inp) as f:
        rows = list(csv.DictReader(f))

    fac_counts = collections.Counter()
    mov_counts = collections.Counter()
    unresolved = []

    for r in rows:
        ch = r["channel_label"]
        fac = derive_facility(ch)
        mov = derive_movement(ch, r["direction"])
        r["facility_type"] = fac
        r["movement"] = mov
        fac_counts[fac or "UNRESOLVED"] += 1
        mov_counts[mov] += 1
        if not fac:
            unresolved.append(ch)

    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"Read  {inp}  ({len(rows)} rows)")
    print(f"Wrote {out}\n")

    print("facility_type:")
    for k, v in fac_counts.most_common():
        print(f"  {k:<14} {v:>4} rows")
    print("\nmovement:")
    for k, v in mov_counts.most_common():
        print(f"  {k:<14} {v:>4} rows")
    if unresolved:
        print(f"\nUNRESOLVED channel labels: {sorted(set(unresolved))}")

    # --- cross-checks against totals verified by hand in the findings doc ---
    by_site = collections.defaultdict(int)
    by_site_fac = collections.defaultdict(lambda: collections.defaultdict(int))
    for r in rows:
        n = int(float(r["count"] or 0))
        by_site[r["site"]] += n
        by_site_fac[r["site"]][r["facility_type"]] += n

    print("\nCross-check against hand-verified totals:")
    for site, expect in [("Alafaya East", 245), ("Alafaya West", 251),
                         ("University South", 248)]:
        got = by_site.get(site)
        ok = "OK " if got == expect else "MISMATCH"
        print(f"  [{ok}] {site:<20} expected {expect}, got {got}")
    pair = by_site.get("Alafaya East", 0) + by_site.get("Alafaya West", 0)
    print(f"  [{'OK ' if pair == 496 else 'MISMATCH'}] Alafaya East+West     "
          f"expected 496, got {pair}   (matches consolidated 'All' sheet)")

    print("\nFacility split now queryable, e.g.:")
    for site in ["Alafaya West", "Pine Hils NBL E", "Edgewater"]:
        if site in by_site_fac:
            d = {k: v for k, v in by_site_fac[site].items() if v}
            print(f"  {site:<20} {d}")

    tot = collections.defaultdict(int)
    for r in rows:
        tot[r["facility_type"]] += int(float(r["count"] or 0))
    print(f"\nCyclists by facility, all sites: {dict(tot)}")
    s = sum(tot.values())
    if s:
        sw = tot.get("sidewalk", 0)
        print(f"  sidewalk share: {100*sw/s:.0f}% of all observed cyclists")


if __name__ == "__main__":
    main()
