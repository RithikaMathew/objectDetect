#!/usr/bin/env python3
"""For each hour-long video: record its resolution / fps / length, and find the busiest 15-minute window for people
(pedestrians + cyclists) by running the detector on one frame every few seconds (no SAHI, no tracking, no X-CLIP: fast).
Use it to choose ONE 15-minute window per year (2022, 2023, 2024, 2025) that actually contains people.
The 2019 Excel count files do not cover 2021+ videos, so this replaces 'look in the Excel file' for those years.

  # 1) find the videos (see the commands in the chat), put one path per line in videos_to_scan.txt
  # 2) run on a GPU node (about 3 minutes per hour of video):
  sbatch code/pick_busy.slurm
  # or directly:  python code/pick_busy_windows.py --list videos_to_scan.txt --out busy/inventory.csv
  # 3) read busy/inventory.csv and busy/windows.txt (ffmpeg cut commands for the best window of each video)

Score of a window = arrivals (a person count that goes up between two samples) + 0.2 x sampled frames with >= 1 person.
It is a rough guide to where the action is, not a count. Vehicles are ignored. Classes used: person, cyclist.
"""
import argparse, csv, os, subprocess, sys

def probe(path):
    import cv2
    cap = cv2.VideoCapture(path)
    if not cap.isOpened(): return None
    w, h = int(cap.get(3)), int(cap.get(4)); fps = cap.get(5) or 30.0; n = cap.get(7)
    cap.release(); return dict(width=w, height=h, fps=round(fps, 2), minutes=round(n / fps / 60, 1), frames=int(n))

def scan(path, model, step, conf, classes):
    import cv2
    cap = cv2.VideoCapture(path); fps = cap.get(5) or 30.0; n = int(cap.get(7)); counts = []
    for i in range(0, n, max(1, int(step * fps))):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i); ok, fr = cap.read()
        if not ok: break
        res = model.predict(fr, conf=conf, verbose=False)[0]
        k = sum(1 for b in res.boxes if res.names[int(b.cls)] in classes)
        counts.append((i / fps, k))
    cap.release(); return counts

def best_window(counts, step, win=900, hop=300):
    if not counts: return None
    end = counts[-1][0]; best = None; t = 0
    while t + win <= end + step:
        seg = [k for s, k in counts if t <= s < t + win]
        arrivals = sum(max(0, b - a) for a, b in zip(seg, seg[1:]))
        score = arrivals + 0.2 * sum(1 for k in seg if k > 0)
        if best is None or score > best[0]: best = (score, t, arrivals, sum(1 for k in seg if k > 0))
        t += hop
    return best

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", required=True, help="text file, one video path per line"); ap.add_argument("--out", default="busy/inventory.csv")
    ap.add_argument("--weights", default="/orange/xiangyan/rithika/vision/vision3/runs/detect/finetune_runs/rtdetr_v3/best.pt")
    ap.add_argument("--step", type=float, default=3.0, help="seconds between sampled frames"); ap.add_argument("--conf", type=float, default=0.3)
    ap.add_argument("--classes", default="person,cyclist"); ap.add_argument("--no-model", action="store_true", help="only record resolution/length")
    a = ap.parse_args()
    paths = [l.strip() for l in open(a.list) if l.strip() and not l.startswith("#")]
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    model = None
    if not a.no_model:
        from ultralytics import RTDETR; model = RTDETR(a.weights)
    classes = set(a.classes.split(",")); rows = []; cuts = []
    for p in paths:
        info = probe(p)
        if info is None: print("cannot open:", p); continue
        row = dict(path=p, **info, best_start_s="", best_start_mmss="", arrivals="", frames_with_people="", score="")
        if model is not None:
            counts = scan(p, model, a.step, a.conf, classes); b = best_window(counts, a.step)
            if b:
                s = int(b[1]); row.update(best_start_s=s, best_start_mmss=f"{s // 60}:{s % 60:02d}", arrivals=b[2], frames_with_people=b[3], score=round(b[0], 1))
                tag = os.path.splitext(os.path.basename(p))[0][-28:].replace(" ", "_")
                cuts.append(f'ffmpeg -nostdin -y -ss {s} -t 900 -i "{p}" -c:v libx264 -crf 20 -an newvideo/{tag}_{s // 60}m.mp4   # {info["width"]}x{info["height"]}, score {row["score"]}')
        rows.append(row); print(row)
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["path"]); w.writeheader(); w.writerows(rows)
    if cuts:
        open(os.path.join(os.path.dirname(a.out) or ".", "windows.txt"), "w").write("mkdir -p newvideo\n" + "\n".join(cuts) + "\n")
    print(f"wrote {a.out} ({len(rows)} videos)" + (" and windows.txt" if cuts else ""))

if __name__ == "__main__": main()
