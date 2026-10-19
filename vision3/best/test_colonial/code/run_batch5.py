#!/usr/bin/env python3
"""Batch 5: (1) ABLATION to measure what speed and the detector veto really contribute, (2) BRIGHTENING retest done properly.
Prints the sbatch lines (dry run). Add --go to submit ONCE. Run from test_colonial (NOT from code/).

  python code/run_batch5.py ablation                 # dry run: 8 jobs  (b5_nospeed, b5_noveto on the 4 labelled clips)
  python code/run_batch5.py ablation --go            # submit once
  python code/run_batch5.py bright                   # dry run: up to 6 jobs (gamma/clahe/zerodce on the 2 night clips)
  python code/run_batch5.py bright --go
  # after the jobs finish (squeue -u $USER shows nothing):
  python code/eval_truth.py --root . --runs exp0_base,b4_combo_static5,b5_nospeed,b5_noveto --baseline exp0_base      # ablation
  python code/eval_truth.py --root . --runs b4_combo_static5,b5_bright_gamma,b5_bright_clahe,b5_bright_zerodce --baseline exp0_base   # brightening

What each run changes relative to the current best (b4_combo_static5, settings read from run_batch4.sh):
  b5_nospeed : SPEED_RULE=0                       -> everything else identical; the difference = what the speed rule contributes
  b5_noveto  : DET_VETO_PCT=0                     -> veto can never fire (cyclist share < 0% is impossible)
  b5_bright_<mode> : brightening (night frames only) on BOTH the detector input AND the X-CLIP crops, together with SAHI and all
                     current rules. The first test used the plain detector, no SAHI, detector input only, ONE night clip.
Run names are the same for all clips of one run (like run_batch4.sh), so eval_truth.py finds each clip by its hour-file number.
Assumptions to verify (the script checks the first two and stops with a message):
  - code/run_xclip_colonial_v19.slurm mentions the brightening variable (searched as ENHANCE*) and the modes exist in
    code/xclip_overlay_v19_colonial.py ('gamma', 'clahe', 'zerodce').
  - run_batch4.sh has the ENVV= line (NETPX defaults to 5 as in that script; --netpx to change).
"""
import argparse, os, re, shlex, subprocess, sys, time

CLIPS = {  # name: (hour-file number = array id, START_FRAME, MAX_FRAMES (0 = to end))  README section 38
    "night2115": (22, 26978, 53946), "day1400": (15, 1, 26973),
    "night2200": (23, 1, 26973), "day1245": (13, 80924, 0)}
NIGHT = ["night2115", "night2200"]

def parse_envv(path, netpx):
    for line in open(path):
        m = re.match(r"\s*ENVV=(.*)$", line)
        if m:
            v = m.group(1).strip().strip("'\"").replace("$NETPX", str(netpx)).replace("${NETPX}", str(netpx))
            pairs = []
            for kv in v.replace(" ", ",").split(","):
                if "=" in kv:
                    k, _, val = kv.partition("="); pairs.append([k, val])
            return pairs
    sys.exit(f"no ENVV= line in {path}")

def with_overrides(pairs, over):
    d = [p[:] for p in pairs if p[0] not in ("RUN", "START_FRAME", "MAX_FRAMES")]
    for k, v in over.items():
        for p in d:
            if p[0] == k: p[1] = v; break
        else: d.append([k, v])
    return ",".join(f"{k}={v}" for k, v in d)

def find_enhance_vars(slurm, py):
    st = open(slurm).read() if os.path.exists(slurm) else ""
    toks = sorted(set(re.findall(r"\bENHANCE[A-Z_]*\b", st)))
    if not toks:
        sys.exit(f"{slurm} has no ENHANCE* variable. Run:  grep -n -i enhance {slurm} code/run_exp*.sh code/submit_exp*.sh | head\n"
                 "and paste the output; I will set the right name.")
    crops = "ENHANCE_CROPS" if "ENHANCE_CROPS" in toks else None
    mode = "ENHANCE" if "ENHANCE" in toks else next((t for t in toks if t != crops), None)
    pytxt = open(py).read() if os.path.exists(py) else ""
    modes = [m for m in ("gamma", "clahe", "zerodce") if m in pytxt] or ["clahe", "zerodce"]
    return mode, crops, modes

def jobs_for(group, a):
    pairs = parse_envv(a.from_batch, a.netpx); jobs = []
    if group == "ablation":
        for run, over in (("b5_nospeed", {"SPEED_RULE": "0"}), ("b5_noveto", {"DET_VETO_PCT": "0"})):
            for c in CLIPS: jobs.append((run, c, with_overrides(pairs, over)))
    else:
        mode_var, crops_var, modes = find_enhance_vars(a.slurm, a.script)
        print(f"brightening variable: {mode_var}, crops variable: {crops_var}, modes found in script: {modes}")
        for m in modes:
            over = {mode_var: m}
            if crops_var: over[crops_var] = "1"
            for c in NIGHT: jobs.append((f"b5_bright_{m}", c, with_overrides(pairs, over)))
    return jobs

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("group", choices=["ablation", "bright"]); ap.add_argument("--go", action="store_true")
    ap.add_argument("--from-batch", default="code/run_batch4.sh"); ap.add_argument("--netpx", default="5")
    ap.add_argument("--slurm", default="code/run_xclip_colonial_v19.slurm"); ap.add_argument("--script", default="code/xclip_overlay_v19_colonial.py")
    ap.add_argument("--time", default="02:00:00"); ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if os.path.basename(os.getcwd()) == "code": sys.exit("run from test_colonial, not from inside code/")
    jobs = jobs_for(a.group, a); cmds = []
    for run, c, envv in jobs:
        arr, start, stop = CLIPS[c]
        cmds.append(["sbatch", f"--time={a.time}", f"--export=ALL,RUN={run},{envv},START_FRAME={start},MAX_FRAMES={stop}", f"--array={arr}", a.slurm])
    print(f"{len(cmds)} jobs, about 0.7 GPU-hours each ({len(cmds) * 0.7:.0f} GPU-hours)\n")
    for c in cmds: print(" ".join(shlex.quote(x) for x in c))
    lock = os.path.join("logs", f".batch5_{a.group}.lock")
    if not a.go: print("\nDRY RUN: nothing submitted. Check the settings above, then add --go."); return
    if os.path.exists(lock) and not a.force: sys.exit(f"REFUSED: {lock} exists, so this group was already submitted (squeue -u $USER). --force to override.")
    os.makedirs("logs", exist_ok=True); out = []
    for c in cmds:
        r = subprocess.run(c, capture_output=True, text=True); print(r.stdout.strip(), r.stderr.strip()); out.append(r.stdout.strip())
    open(lock, "w").write(time.ctime() + "\n" + "\n".join(out) + "\n")

if __name__ == "__main__": main()
