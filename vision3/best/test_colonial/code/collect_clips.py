#!/usr/bin/env python3
"""collect_clips.py : give the annotated clips of OLD runs self-explaining names, in one flat folder.

  cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
  python code/collect_clips.py                      # annotated/<run>/<video>/*.mp4  ->  exp_results/clips/
  python code/collect_clips.py --prefix exp1        # only runs starting with exp1
Name pattern:  <run>__<day|night>_<HHMM>-<HHMM>__<what the test covers>__<date>.mp4   e.g.
  exp1_sahi__day_1400-1415__sahi-slicing__20190710.mp4
Files are hard-linked (no extra disk space); the originals stay where they are. INDEX.md lists everything.
(New runs made with the updated xclip_overlay_v19_colonial.py already write this name themselves.)
"""
import argparse, glob, os, re, shutil

WHAT = [("exp0", "control"), ("exp1", "sahi-slicing"), ("exp2_gamma", "night-gamma-enhance"), ("exp2_clahe", "night-clahe-enhance"),
        ("exp2_zerodce", "night-zerodce-enhance"), ("exp3a", "speed-rule"), ("exp3b", "short-track-rule"),
        ("sw_day", "v17-day-settings-3s"), ("sw_switch", "v18-night-switch")]


def what(run):
    for pre, w in WHAT:
        if run.startswith(pre):
            return w
    return "other"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--prefix", default="")
    ap.add_argument("--dst", default=None)
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    dst = a.dst or os.path.join(root, "exp_results", "clips")
    os.makedirs(dst, exist_ok=True)
    rows = []
    for f in sorted(glob.glob(os.path.join(root, "annotated", "*", "*", "*.mp4"))):
        if ".tmp_mp4v" in f:
            continue
        run = f.split(os.sep)[-3]
        if not run.startswith(a.prefix):
            continue
        base = os.path.basename(f)
        m = re.search(r"_(\d{8})_(\d{2})(\d{2})-(\d{2})(\d{2})\.mp4$", base)
        if base.startswith(run + "__"):
            new = base                                           # already a self-explaining name
        elif m:
            date, h0, m0, h1, m1 = m.groups()
            dn = "night" if (int(h0) >= 20 or int(h0) < 6) else "day"
            new = f"{run}__{dn}_{h0}{m0}-{h1}{m1}__{what(run)}__{date}.mp4"
        else:
            new = f"{run}__{base}"
        out = os.path.join(dst, new)
        if not os.path.exists(out):
            try:
                os.link(f, out)
            except OSError:
                shutil.copy2(f, out)
        rows.append((new, os.path.relpath(f, root)))
    with open(os.path.join(dst, "INDEX.md"), "w") as fh:
        fh.write("| clip (new name) | original |\n|---|---|\n" + "\n".join(f"| {n} | {o} |" for n, o in rows) + "\n")
    print(f"{len(rows)} clips -> {dst}\n  index: {os.path.join(dst, 'INDEX.md')}")
    for n, _ in rows:
        print("  " + n)


if __name__ == "__main__":
    main()
