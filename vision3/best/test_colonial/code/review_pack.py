#!/usr/bin/env python3
"""Cut short clips for a table of tracks and label them fast in a browser (offline). Two uses:
  (a) PER-TRACK ACCURACY: label ~40+ model tracks (BICYCLIST / PEDESTRIAN / NOT_PERSON), then `code/track_truth_v1.py eval`.
  (b) HIGH-SENSITIVITY REVIEW (human-in-the-loop): run the pipeline with a low threshold, rank the candidates, cut only the
      top ones that fit a review budget (e.g. 12 minutes per hour of video), label them, then `curve` shows how many real
      people each extra review minute finds.

Run on the cluster from test_colonial (NOT from code/):
  python code/review_pack.py inspect --table validation/track_truth_runs45_v2.csv
  python code/review_pack.py build --table validation/track_truth_runs45_v2.csv --out review/pack1
       [--rank-col det_cyclist_frac] [--budget-min 12] [--pad 3]      # columns: see `inspect`
  -> download the folder review/pack1 to your computer, open review.html, label (keys: b / p / n, arrows = next/back),
     click 'Download labels CSV' (file labels.csv), copy it back to review/pack1/ on the cluster, then:
  python code/review_pack.py merge --table validation/track_truth_runs45_v2.csv --labels review/pack1/labels.csv --out validation/track_truth_runs45_v2_labelled.csv
  python code/review_pack.py curve --pack review/pack1 --labels review/pack1/labels.csv [--truth-count 21]

Table columns used (defaults match the track-truth file; change with the flags): --video-col clip_hint, --time-col first_time
('YYYY-MM-DD HH:MM:SS'), --bin-col bin_start ('HH:MM', start of the hour-file piece), --secs-col secs. If the table has a
column with the seek position inside the video (seconds or mm:ss) pass --seek-col instead of time/bin.
Decide from the video only; do not look at the model labels while labelling.
"""
import argparse, csv, html, json, os, subprocess, sys
from datetime import datetime as D

def read(path):
    with open(path, newline="") as f: return list(csv.DictReader(f))

def to_secs(v):
    v = str(v).strip()
    if ":" in v:
        p = [float(x) for x in v.split(":")]; return sum(x * 60 ** i for i, x in enumerate(reversed(p)))
    return float(v)

def seek_of(r, a):
    if a.seek_col: return to_secs(r[a.seek_col])
    t = D.strptime(r[a.time_col].strip()[:19], "%Y-%m-%d %H:%M:%S")
    b = D.strptime(r[a.time_col].strip()[:11] + r[a.bin_col].strip() + ":00", "%Y-%m-%d %H:%M:%S")
    return (t - b).total_seconds()

def cmd_inspect(a):
    rows = read(a.table); print(f"{a.table}: {len(rows)} rows\ncolumns: {list(rows[0].keys())}\nfirst row: {rows[0]}")
    need = [a.video_col, a.secs_col] + ([a.seek_col] if a.seek_col else [a.time_col, a.bin_col])
    miss = [c for c in need if c not in rows[0]]
    print("MISSING columns (use the flags):" if miss else "all needed columns found", miss or "")

def cmd_build(a):
    rows = read(a.table); items = []
    for i, r in enumerate(rows, 1):
        try:
            seek = seek_of(r, a); secs = float(r.get(a.secs_col) or 0)
        except (KeyError, ValueError) as e:
            sys.exit(f"row {i}: cannot read time columns ({e}); run `inspect`")
        if seek < 0: print(f"row {i}: starts in the previous hour file; skipped"); continue
        score = float(r[a.rank_col]) if a.rank_col and r.get(a.rank_col) not in (None, "") else 0.0
        items.append(dict(row_id=i, video=r[a.video_col], seek=max(0.0, seek - a.pad), secs=secs,
                          dur=min(secs + 2 * a.pad, a.max_clip), score=score))
    if a.rank_col: items.sort(key=lambda x: -x["score"])
    if a.budget_min:
        keep, tot = [], 0.0
        for it in items:
            if tot + it["dur"] > a.budget_min * 60: break
            keep.append(it); tot += it["dur"]
        print(f"budget {a.budget_min} min: keeping {len(keep)} of {len(items)} candidates ({tot / 60:.1f} min of clips)")
        items = keep
    os.makedirs(os.path.join(a.out, "snippets"), exist_ok=True)
    for k, it in enumerate(items, 1):
        it["rank"] = k; it["file"] = f"snippets/{k:03d}_row{it['row_id']}.mp4"
        if a.no_ffmpeg: continue
        out = os.path.join(a.out, it["file"])
        if os.path.exists(out): continue
        p = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{it['seek']:.2f}", "-i", it["video"],
                            "-t", f"{it['dur']:.2f}", "-an", "-vf", "scale=720:-2", "-c:v", "libx264", "-crf", "26", out],
                           capture_output=True, text=True)
        if p.returncode: print(f"row {it['row_id']}: ffmpeg failed: {p.stderr[:150]}")
    json.dump(items, open(os.path.join(a.out, "index.json"), "w"), indent=1)
    open(os.path.join(a.out, "review.html"), "w").write(HTML.replace("__ITEMS__", json.dumps(items)))
    print(f"wrote {len(items)} snippets + review.html + index.json in {a.out}")

def read_labels(path):
    return {int(r["row_id"]): r["true_label"] for r in read(path) if r.get("true_label")}

def cmd_merge(a):
    rows = read(a.table); cols = list(rows[0].keys()); lab = read_labels(a.labels)
    if "true_label" not in cols: cols.append("true_label")
    n = 0
    for i, r in enumerate(rows, 1):
        if i in lab: r["true_label"] = lab[i]; n += 1
        r.setdefault("true_label", "")
    if os.path.abspath(a.out) == os.path.abspath(a.table): sys.exit("--out must be a NEW file")
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    print(f"merged {n} labels into {a.out} ({len(rows)} rows)")

def cmd_curve(a):
    items = json.load(open(os.path.join(a.pack, "index.json"))); lab = read_labels(a.labels)
    cum_min = hit = bad = 0; print("rank  minutes  real_people  not_person  recall" if a.truth_count else "rank  minutes  real_people  not_person")
    for it in items:
        if it["row_id"] not in lab: continue
        cum_min += it["dur"] / 60
        if lab[it["row_id"]] == "NOT_PERSON": bad += 1
        else: hit += 1
        print(f"{it['rank']:4d}  {cum_min:7.1f}  {hit:11d}  {bad:10d}" + (f"  {hit / a.truth_count:6.0%}" if a.truth_count else ""))
    print("Read: the review minute where 'real_people' stops growing is the cutoff worth reviewing. "
          "Recall assumes each real person appears once; people the pipeline never tracked are not in the table.")

HTML = """<!doctype html><meta charset=utf-8><title>Review</title>
<style>body{font-family:Arial;margin:20px;max-width:900px}video{width:100%;background:#000}button{font-size:16px;margin:4px;padding:8px 14px}
.sel{background:#ff0;font-weight:bold}</style>
<h2 id=h></h2><video id=v controls autoplay loop muted></video>
<div id=b><button data-l=BICYCLIST>b: BICYCLIST (incl. motorcycle)</button><button data-l=PEDESTRIAN>p: PEDESTRIAN</button>
<button data-l=NOT_PERSON>n: NOT_PERSON</button></div>
<p><button id=prev>&larr; back</button><button id=next>next &rarr;</button> <button id=dl>Download labels CSV</button></p>
<p id=s></p><script>
const items=__ITEMS__;let i=0;const K='review_labels_'+items.map(x=>x.row_id).join('_').slice(0,60);
let lab=JSON.parse(localStorage.getItem(K)||'{}');
function show(){const it=items[i];document.getElementById('h').textContent=`Clip ${i+1} / ${items.length} (row ${it.row_id}, ~${it.secs.toFixed(1)} s on screen, in the middle of the clip)`;
v.src=it.file;[...b.children].forEach(x=>x.className=lab[it.row_id]==x.dataset.l?'sel':'');
s.textContent=`Labelled ${Object.keys(lab).length} of ${items.length}`}
function set(l){lab[items[i].row_id]=l;localStorage.setItem(K,JSON.stringify(lab));show();if(i<items.length-1){i++;show()}}
[...b.children].forEach(x=>x.onclick=()=>set(x.dataset.l));
prev.onclick=()=>{if(i>0){i--;show()}};next.onclick=()=>{if(i<items.length-1){i++;show()}};
document.onkeydown=e=>{if(e.key=='b')set('BICYCLIST');if(e.key=='p')set('PEDESTRIAN');if(e.key=='n')set('NOT_PERSON');
if(e.key=='ArrowRight')next.onclick();if(e.key=='ArrowLeft')prev.onclick()};
dl.onclick=()=>{let t='row_id,true_label\\n'+Object.entries(lab).map(([k,l])=>k+','+l).join('\\n')+'\\n';
const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([t],{type:'text/csv'}));a.download='labels.csv';a.click()};
show();</script>"""

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    def cols(p):
        p.add_argument("--table", required=True); p.add_argument("--video-col", default="clip_hint")
        p.add_argument("--time-col", default="first_time"); p.add_argument("--bin-col", default="bin_start")
        p.add_argument("--secs-col", default="secs"); p.add_argument("--seek-col")
    p = sub.add_parser("inspect"); cols(p)
    p = sub.add_parser("build"); cols(p); p.add_argument("--out", required=True); p.add_argument("--rank-col")
    p.add_argument("--budget-min", type=float, default=0, help="total minutes of clips to keep (0 = all)")
    p.add_argument("--pad", type=float, default=3.0); p.add_argument("--max-clip", type=float, default=20.0)
    p.add_argument("--no-ffmpeg", action="store_true")
    p = sub.add_parser("merge"); p.add_argument("--table", required=True); p.add_argument("--labels", required=True); p.add_argument("--out", required=True)
    p = sub.add_parser("curve"); p.add_argument("--pack", required=True); p.add_argument("--labels", required=True); p.add_argument("--truth-count", type=int, default=0)
    a = ap.parse_args(); {"inspect": cmd_inspect, "build": cmd_build, "merge": cmd_merge, "curve": cmd_curve}[a.cmd](a)

if __name__ == "__main__": main()
