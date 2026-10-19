#!/usr/bin/env python3
"""
track_truth_v1.py - measure REAL per-object accuracy of RT-DETR, X-CLIP and combined rules from a small hand-labelled set.

The human counts only give totals per 15 minutes, so they cannot say which model is right on a given person. This script:

  1) template: writes a CSV with one row per track (time, clip file, RT-DETR label, X-CLIP label, ...) and an empty
     'true_label' column. You watch the clip and fill true_label with  BICYCLIST | PEDESTRIAN | NOT_PERSON
     (NOT_PERSON = cone, shadow, sign, ... that the pipeline tracked as a person).
     For people the pipeline never tracked (missed), ADD a row: run, chunk, first_time, true_label, leave track_id empty.
  2) eval: reads the filled CSV and prints
       - tracking quality: share of tracks that are real people, recall of real people by class (missed rows count)
       - classification accuracy, confusion matrix, per-class precision/recall/F1 for: X-CLIP, RT-DETR, fused rule,
         optional speed rule - on tracks that are real people

  python code/track_truth_v1.py template --root $ROOT --run colonial_run4 --run colonial_run5 --out $ROOT/validation/track_truth_runs45.csv
  python code/track_truth_v1.py eval --file $ROOT/validation/track_truth_runs45.csv
Label at least ~40 real tracks before reading anything into the percentages; report the counts (n) with them.
"""
import argparse
import csv
import datetime as dt
import glob
import os

COLS = ["run", "chunk", "track_id", "first_time", "last_time", "secs", "bin_start", "clip_hint", "counted", "det_label",
        "det_cyclist_pct", "mean_conf", "xclip_label", "p_bic", "disp_px", "speed_px_s", "true_label", "notes"]


def template(a):
    sess = dt.datetime.strptime(a.session_start, "%Y-%m-%d %H:%M:%S")
    rows = []
    for run in a.run:
        for f in sorted(glob.glob(os.path.join(a.root, "counts", run, "*_tracks*.csv"))):
            tag = os.path.basename(f).split("_tracks")[0]
            chunk = tag.split(".")[-1]
            for r in csv.DictReader(open(f)):
                secs = float(r["secs"])
                if secs < a.min_secs and r["counted"] != "1":
                    continue
                if a.counted_only and r["counted"] != "1":
                    continue
                b0 = sess + dt.timedelta(minutes=15 * int(r["bin_index"]))
                b1 = b0 + dt.timedelta(minutes=15)
                disp = r.get("disp_px") or ""
                rows.append({"run": run, "chunk": chunk, "track_id": r["track_id"], "first_time": r["first_time"], "last_time": r["last_time"],
                             "secs": r["secs"], "bin_start": b0.strftime("%H:%M"),
                             "clip_hint": f"annotated/{run}/{tag}/{tag}_{b0:%Y%m%d_%H%M}-{b1:%H%M}.mp4", "counted": r["counted"],
                             "det_label": r.get("det_label", ""), "det_cyclist_pct": r.get("det_cyclist_pct", ""),
                             "mean_conf": r["mean_conf"], "xclip_label": r["label"], "p_bic": r["weighted_bicyclist"], "disp_px": disp,
                             "speed_px_s": f"{float(disp) / secs:.1f}" if disp and secs > 0 else "", "true_label": "", "notes": ""})
    rows.sort(key=lambda r: (r["first_time"], r["run"]))
    out = a.out
    if os.path.exists(out):
        root, ext = os.path.splitext(out)
        k = 2
        while os.path.exists(f"{root}_v{k}{ext}"):
            k += 1
        out = f"{root}_v{k}{ext}"
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {out}\nFill 'true_label' (BICYCLIST / PEDESTRIAN / NOT_PERSON). Add rows with empty track_id for people the AI never tracked.")


def prf(conf, cls):
    tp = conf[(cls, cls)]
    fp = sum(v for (t, p), v in conf.items() if p == cls and t != cls)
    fn = sum(v for (t, p), v in conf.items() if t == cls and p != cls)
    pr = tp / (tp + fp) if tp + fp else float("nan")
    rc = tp / (tp + fn) if tp + fn else float("nan")
    f1 = 2 * pr * rc / (pr + rc) if pr == pr and rc == rc and pr + rc else float("nan")
    return pr, rc, f1


def evaluate(a):
    rows = [r for r in csv.DictReader(open(a.file)) if r["true_label"].strip().upper() in ("BICYCLIST", "PEDESTRIAN", "NOT_PERSON")]
    for r in rows:
        r["true_label"] = r["true_label"].strip().upper()
    tracked = [r for r in rows if r["track_id"].strip()]
    missed = [r for r in rows if not r["track_id"].strip()]
    print(f"labelled rows: {len(rows)} ({len(tracked)} tracks, {len(missed)} missed people added by hand)\n")
    real = [r for r in tracked if r["true_label"] != "NOT_PERSON"]
    print("TRACKING / DETECTION")
    print(f"  tracks that are real people: {len(real)}/{len(tracked)} ({len(real) / max(len(tracked), 1):.0%});  NOT_PERSON tracks: {len(tracked) - len(real)}")
    cnt = [r for r in tracked if r["counted"] == "1"]
    if cnt:
        fp = sum(r["true_label"] == "NOT_PERSON" for r in cnt)
        print(f"  among the {len(cnt)} tracks the pipeline actually counted, {fp} are not people ({fp / len(cnt):.0%})")
    for c in ("BICYCLIST", "PEDESTRIAN"):
        det_n = sum(r["true_label"] == c for r in real)
        mis_n = sum(r["true_label"] == c for r in missed)
        if det_n + mis_n:
            print(f"  {c}: tracked {det_n}, missed {mis_n} -> detection recall {det_n / (det_n + mis_n):.0%} (n={det_n + mis_n})")
    print(f"\nCLASSIFICATION on the {len(real)} tracked real people (rows = truth, columns = predicted)")

    def fused(r):
        dp, pb = float(r["det_cyclist_pct"] or 0), float(r["p_bic"])
        return dp >= a.F or (pb >= 0.5 and (dp >= a.D or pb >= a.O))
    rules = {"X-CLIP": lambda r: float(r["p_bic"]) >= 0.5,
             "RT-DETR (>=50% cyclist)": lambda r: float(r["det_cyclist_pct"] or 0) >= 50,
             f"fused D={a.D:.0f} O={a.O} F={a.F:.0f}": fused}
    if a.speed:
        rules[f"speed >= {a.speed:.0f} px/s"] = lambda r: r["speed_px_s"] != "" and float(r["speed_px_s"]) >= a.speed
    for name, rule in rules.items():
        conf = {(t, p): 0 for t in ("BICYCLIST", "PEDESTRIAN") for p in ("BICYCLIST", "PEDESTRIAN")}
        for r in real:
            conf[(r["true_label"], "BICYCLIST" if rule(r) else "PEDESTRIAN")] += 1
        acc = (conf[("BICYCLIST", "BICYCLIST")] + conf[("PEDESTRIAN", "PEDESTRIAN")]) / max(len(real), 1)
        print(f"\n  {name}: accuracy {acc:.0%} (n={len(real)})")
        print("                 pred BIC   pred PED")
        print(f"    true BIC     {conf[('BICYCLIST', 'BICYCLIST')]:8d}   {conf[('BICYCLIST', 'PEDESTRIAN')]:8d}")
        print(f"    true PED     {conf[('PEDESTRIAN', 'BICYCLIST')]:8d}   {conf[('PEDESTRIAN', 'PEDESTRIAN')]:8d}")
        for c in ("BICYCLIST", "PEDESTRIAN"):
            pr, rc, f1 = prf(conf, c)
            print(f"    {c:10s} precision {pr:.0%}  recall {rc:.0%}  F1 {f1:.2f}")
    agree = [r for r in real if (float(r["p_bic"]) >= 0.5) == (float(r["det_cyclist_pct"] or 0) >= 50)]
    print(f"\nX-CLIP and RT-DETR agree on {len(agree)}/{len(real)} real tracks; when they disagree, who is right?")
    dis = [r for r in real if r not in agree]
    print(f"  disagreements {len(dis)}: X-CLIP right {sum((float(r['p_bic']) >= 0.5) == (r['true_label'] == 'BICYCLIST') for r in dis)}, "
          f"RT-DETR right {sum((float(r['det_cyclist_pct'] or 0) >= 50) == (r['true_label'] == 'BICYCLIST') for r in dis)}")


ap = argparse.ArgumentParser()
sub = ap.add_subparsers(dest="cmd", required=True)
t = sub.add_parser("template")
t.add_argument("--root", required=True)
t.add_argument("--run", action="append", required=True)
t.add_argument("--out", required=True)
t.add_argument("--min-secs", type=float, default=1.0)
t.add_argument("--counted-only", action="store_true")
t.add_argument("--session-start", default="2019-07-10 00:00:00")
e = sub.add_parser("eval")
e.add_argument("--file", required=True)
e.add_argument("--D", type=float, default=20.0)
e.add_argument("--O", type=float, default=0.95)
e.add_argument("--F", type=float, default=80.0)
e.add_argument("--speed", type=float, default=0.0, help="also score a speed-only rule (px/s)")
a = ap.parse_args()
template(a) if a.cmd == "template" else evaluate(a)
