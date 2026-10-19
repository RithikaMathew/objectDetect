#!/usr/bin/env python3
"""eval_truth.py : compare every experiment run with Rithika's hand-made truth files (person level, not just counts).

  cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
  python code/eval_truth.py --root . --prefix exp          # all runs whose name starts with 'exp'
  python code/eval_truth.py --root . --runs exp0_base,exp1_sahi --out exp_results/EVAL_manual.md

Truth file (one per clip, CSV):  id,start_mmss,end_mmss,class,source,notes
  start/end = position in the 15-minute clip (what the video player shows), class = cyclist | pedestrian | motorcycle
  (motorcycle is scored as cyclist for now, as agreed). Rows with an empty class or empty start are SKIPPED and listed.
Matching is by TIME only (greedy, +-1.5 s): when two people are on screen at the same moment the match can be ambiguous.
Status per truth row:  FOUND | WRONG CLASS | DETECTED BUT NOT COUNTED | MISSED.  'EXTRA' = a counted track matching no truth row
(a false person, OR a real person missing from the truth file: complete the truth file first).
Nothing here uses the old ground-truth count file.
"""
import argparse, csv, datetime, glob, json, os, sys

CLIPS = {"night": dict(chunk=22, start="2019-07-10 21:15:00", truth="truth/night_2115_truth.csv"),
         "day": dict(chunk=15, start="2019-07-10 14:00:00", truth="truth/day_1400_truth.csv"),
         "night_holdout_2200": dict(chunk=23, start="2019-07-10 22:00:00", truth="truth/night_2200_truth.csv"),
         "day_holdout_1245": dict(chunk=13, start="2019-07-10 12:45:00", truth="truth/day_1245_truth.csv")}
TOL = 1.5


def mmss(x):
    x = (x or "").strip()
    if not x:
        return None
    p = x.split(":")
    try:
        return int(p[0]) * 60 + float(p[1]) if len(p) == 2 else float(x)
    except ValueError:
        return None


def norm_class(c, moto_as="cyclist"):
    c = (c or "").strip().lower()
    if c in ("cyclist", "bicyclist", "bike", "cyc", "bicycle"):
        return "cyclist"
    if c in ("pedestrian", "ped", "walker", "person", "pedestrian "):
        return "pedestrian"
    if c in ("motorcycle", "motorbike", "moto", "motor"):
        return moto_as
    return None


def read_truth(path):
    rows, skipped = [], []
    if not os.path.isfile(path):
        return rows, [f"(missing file {path})"]
    for r in csv.DictReader(l for l in open(path, encoding="utf-8") if not l.startswith("#")):
        s, e, c = mmss(r.get("start_mmss")), mmss(r.get("end_mmss")), norm_class(r.get("class"))
        if s is None or c is None:
            skipped.append(f"{r.get('id')} (start='{r.get('start_mmss')}', class='{r.get('class')}')")
            continue
        rows.append(dict(id=r.get("id", "?"), s=s, e=(e if e is not None else s), c=c, raw=(r.get("class") or "").strip().lower(),
                         notes=r.get("notes", "")))
    return sorted(rows, key=lambda x: x["s"]), skipped


def read_tracks(path, t0):
    out = []
    for r in csv.DictReader(open(path)):
        f = (datetime.datetime.strptime(r["first_time"], "%Y-%m-%d %H:%M:%S") - t0).total_seconds()
        l = (datetime.datetime.strptime(r["last_time"], "%Y-%m-%d %H:%M:%S") - t0).total_seconds() + 1.0
        lab = {"BICYCLIST": "cyclist", "PEDESTRIAN": "pedestrian"}.get(r["label"], "unscored")
        out.append(dict(id=r["track_id"], f=f, l=l, counted=int(r["counted"]), lab=lab, secs=float(r["secs"]), det=r.get("det_label", ""),
                        detpct=r.get("det_cyclist_pct", "")))
    return out


def fmt(sec):
    return f"{int(sec // 60)}:{int(sec % 60):02d}"


def match(truth, tracks):
    used, res = set(), []
    for t in truth:
        best, bkey = None, None
        for k in tracks:
            if k["id"] in used:
                continue
            ov = min(t["e"] + TOL, k["l"]) - max(t["s"] - TOL, k["f"])
            if ov <= 0:
                continue
            key = (k["counted"], ov)
            if bkey is None or key > bkey:
                best, bkey = k, key
        if best is None:
            res.append((t, "MISSED", None))
            continue
        used.add(best["id"])
        if best["counted"] and best["lab"] == t["c"]:
            res.append((t, "FOUND", best))
        elif best["counted"]:
            res.append((t, "WRONG CLASS", best))
        else:
            res.append((t, "DETECTED BUT NOT COUNTED", best))
    extra = [k for k in tracks if k["counted"] and k["id"] not in used]
    return res, extra


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--prefix", default="exp")
    ap.add_argument("--runs", default=None, help="comma list; default = every folder in counts/ starting with --prefix")
    ap.add_argument("--baseline", default="exp0_base")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    runs = a.runs.split(",") if a.runs else sorted(d for d in os.listdir(os.path.join(root, "counts")) if d.startswith(a.prefix))
    out = [f"# Experiment evaluation  ({datetime.datetime.now():%Y-%m-%d %H:%M})", "", f"root: {root}", f"runs: {', '.join(runs)}", ""]
    summary = []
    truths = {}
    for cname, cc in CLIPS.items():
        truths[cname] = read_truth(os.path.join(root, cc["truth"]))
        tr, sk = truths[cname]
        out.append(f"- truth {cname}: {len(tr)} usable rows ({sum(1 for x in tr if x['c']=='cyclist')} cyclist incl. motorcycle, "
                   f"{sum(1 for x in tr if x['c']=='pedestrian')} pedestrian); skipped {len(sk)}: {'; '.join(sk) if sk else 'none'}")
    out.append("")
    detail = []
    for run in runs:
        for cname, cc in CLIPS.items():
            tf = glob.glob(os.path.join(root, "counts", run, f"*.{cc['chunk']:03d}_tracks.csv"))
            if not tf:
                continue
            t0 = datetime.datetime.strptime(cc["start"], "%Y-%m-%d %H:%M:%S")
            tracks = read_tracks(sorted(tf)[0], t0)
            truth = truths[cname][0]
            res, extra = match(truth, tracks)
            cnt = lambda cls, st: sum(1 for t, s, _ in res if t["c"] == cls and s == st)
            tot = lambda cls: sum(1 for t, _, _ in res if t["c"] == cls)
            rl = glob.glob(os.path.join(root, "logs", run, f"*.{cc['chunk']:03d}_run_log.json"))
            rt = ""
            if rl:
                try:
                    rt = round(json.load(open(rl[0]))["runtime_s"] / 60.0, 1)
                except Exception:
                    pass
            bic = sum(1 for k in tracks if k["counted"] and k["lab"] == "cyclist")
            ped = sum(1 for k in tracks if k["counted"] and k["lab"] == "pedestrian")
            summary.append([run, cname, f"{cnt('cyclist','FOUND')}/{tot('cyclist')}", f"{cnt('pedestrian','FOUND')}/{tot('pedestrian')}",
                            sum(1 for _, s, _ in res if s == "WRONG CLASS"), sum(1 for _, s, _ in res if s == "DETECTED BUT NOT COUNTED"),
                            sum(1 for _, s, _ in res if s == "MISSED"), len(extra), f"{bic}/{ped}", rt])
            detail.append(f"### {run} - {cname} clip\n")
            detail.append("| truth id | class | time | status | matched track |\n|---|---|---|---|---|")
            for t, s, k in res:
                kt = "" if k is None else f"#{k['id']} {k['lab']} {k['secs']}s counted={k['counted']} det={k['det']} ({k['detpct']}% cyc)"
                detail.append(f"| {t['id']} | {t['raw']} | {fmt(t['s'])}-{fmt(t['e'])} | {s} | {kt} |")
            for k in extra:
                detail.append(f"| EXTRA | counted {k['lab']} | {fmt(max(k['f'],0))}-{fmt(k['l'])} | no truth row | #{k['id']} {k['secs']}s det={k['det']} |")
            detail.append("")
    out += ["## Summary (person level; FOUND = counted with the right class; motorcycle scored as cyclist)", "",
            "| run | clip | cyclists found | pedestrians found | wrong class | detected, not counted | missed | extra counted | counted bic/ped | runtime min |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    out += ["| " + " | ".join(str(x) for x in r) + " |" for r in summary]
    out += ["", "## Detail", ""] + detail
    # motion candidates that overlap truth rows nobody found
    bl = glob.glob(os.path.join(root, "counts", a.baseline, "*_motion_candidates.csv"))
    if bl:
        out += ["## Motion-diagnostic candidates (baseline run) overlapping truth rows", ""]
        for cname, cc in CLIPS.items():
            f_ = [p for p in bl if f".{cc['chunk']:03d}_" in p]
            if not f_:
                continue
            t0 = datetime.datetime.strptime(cc["start"], "%Y-%m-%d %H:%M:%S")
            day = t0.date()
            cands = []
            for r in csv.DictReader(open(f_[0])):
                s_ = (datetime.datetime.combine(day, datetime.datetime.strptime(r["first_time"], "%H:%M:%S").time()) - t0).total_seconds()
                e_ = (datetime.datetime.combine(day, datetime.datetime.strptime(r["last_time"], "%H:%M:%S").time()) - t0).total_seconds()
                cands.append((r["cand"], s_, e_, r["secs"], r["mean_box_h"]))
            out.append(f"**{cname}**: {len(cands)} unexplained moving blobs; contact sheet next to the csv (`*_motion_candidates.png`).")
            for t in truths[cname][0]:
                hit = [c for c in cands if min(t["e"] + TOL, c[2]) - max(t["s"] - TOL, c[1]) > 0]
                out.append(f"- truth {t['id']} ({t['raw']} {fmt(t['s'])}): " + (", ".join(f"cand {c[0]} ({c[3]}s, box h {c[4]})" for c in hit) if hit else "no motion candidate"))
            out.append("")
    txt = "\n".join(out)
    path = a.out or os.path.join(root, "exp_results", f"EVAL_{datetime.datetime.now():%Y%m%d_%H%M}.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(txt)
    print(txt)
    print(f"\nwritten: {path}")


if __name__ == "__main__":
    main()
