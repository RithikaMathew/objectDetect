#!/usr/bin/env python3
"""Submit (or just print) the full-day run of the current best setup, with a duplicate-submission guard.

Run from test_colonial (NOT from code/). Default is a DRY RUN: it prints the sbatch line and submits nothing.

  # 1) see what would be submitted for the 24-hour block (chunks 1-24); settings copied from run_batch4.sh
  python code/scale_up.py plan --run b4_full_block1 --chunks 1-24 --from-batch code/run_batch4.sh
  # 2) when the printed line looks right (check the settings!), submit ONCE:
  python code/scale_up.py plan --run b4_full_block1 --chunks 1-24 --from-batch code/run_batch4.sh --go
  # 3) later: which chunks have output, and the array string to resubmit the missing ones
  python code/scale_up.py check --run b4_full_block1 --chunks 1-24
  # then 48 hours: --chunks 25-48 with a NEW run name (b4_full_block2), or --chunks 1-48 for a single run.

Time: ~1.9 GPU-hours per hourly chunk (README section 16): 24 h = ~46 GPU-h, 48 h = ~92 GPU-h.
Assumption to verify: `--from-batch` takes the first line that starts with ENVV= in that script. If its format differs,
pass the settings yourself: --envv "SAHI=1,STATIC_FILTER=1,..." (comma separated, no spaces).
"""
import argparse, glob, os, re, shlex, subprocess, sys, time
from run_batch5 import parse_envv, with_overrides

def parse_chunks(s):
    out = []
    for part in s.split(","):
        a, _, b = part.partition("-")
        out += list(range(int(a), int(b or a) + 1))
    return sorted(set(out))

def compress(ch):
    """[1,2,3,5] -> '1-3,5' (sbatch array syntax)"""
    parts, i = [], 0
    while i < len(ch):
        j = i
        while j + 1 < len(ch) and ch[j + 1] == ch[j] + 1: j += 1
        parts.append(str(ch[i]) if i == j else f"{ch[i]}-{ch[j]}"); i = j + 1
    return ",".join(parts)

def envv_from_batch(path):
    return with_overrides(parse_envv(path, os.environ.get("NETPX", "5")), {})

def done_chunks(root, run, chunks):
    d = os.path.join(root, "counts", run)
    files = os.listdir(d) if os.path.isdir(d) else []
    return [c for c in chunks if any(f.endswith(f".{c:03d}_tracks.csv") for f in files)
            and any(f.endswith(f".{c:03d}_bin_counts.csv") for f in files)]

def cmd_plan(a):
    if os.path.basename(os.getcwd()) == "code": sys.exit("run from test_colonial, not from inside code/")
    chunks = parse_chunks(a.chunks)
    envv = a.envv or (envv_from_batch(a.from_batch) if a.from_batch else None)
    if not envv: sys.exit("give --from-batch code/run_batch4.sh or --envv ...")
    if re.search(r"(^|,)RUN=", envv): envv = re.sub(r"(^|,)RUN=[^,]*", "", envv).lstrip(",")  # run name comes from --run
    lock = os.path.join("logs", f".scale_{a.run}.lock")
    existing = os.path.isdir(os.path.join("counts", a.run)) or os.path.exists(lock)
    cmd = ["sbatch", f"--time={a.time}", f"--export=ALL,RUN={a.run},{envv}",
           f"--array={compress(chunks)}%{a.throttle}", a.slurm]
    hours = len(chunks); print(f"run {a.run}: {hours} hourly chunk(s) x ~1.9 GPU-h = ~{hours * 1.9:.0f} GPU-hours, "
                               f"{a.throttle} at a time")
    print("settings used:", envv)
    print("command:\n  " + " ".join(shlex.quote(c) for c in cmd))
    if not a.go: print("\nDRY RUN: nothing submitted. Add --go to submit."); return
    if existing and not a.force:
        sys.exit(f"REFUSED: counts/{a.run} or {lock} already exists, so this run was probably submitted. "
                 "Check `squeue -u $USER`; use a new --run name, or --force only if you are sure.")
    os.makedirs("logs", exist_ok=True)
    out = subprocess.run(cmd, capture_output=True, text=True); print(out.stdout, out.stderr)
    if out.returncode == 0: open(lock, "w").write(f"{time.ctime()}\n{' '.join(cmd)}\n{out.stdout}")

def cmd_check(a):
    chunks = parse_chunks(a.chunks)
    ok = done_chunks(".", a.run, chunks); miss = [c for c in chunks if c not in ok]
    print(f"{a.run}: output found for {len(ok)}/{len(chunks)} chunks")
    if miss:
        print("missing chunks:", compress(miss))
        print("to resubmit only those (after `squeue -u $USER` shows none of them running):\n  "
              f"python code/scale_up.py plan --run {a.run} --chunks {compress(miss)} --from-batch code/run_batch4.sh --go --force")
    print("then check logs: grep -L \"Final counts\" logs/slurm_*.log   (prints nothing if every job finished)")

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan"); p.add_argument("--run", required=True); p.add_argument("--chunks", default="1-24")
    p.add_argument("--from-batch"); p.add_argument("--envv"); p.add_argument("--time", default="05:00:00")
    p.add_argument("--throttle", type=int, default=6, help="max array tasks running at once")
    p.add_argument("--slurm", default="code/run_xclip_colonial_v19.slurm"); p.add_argument("--go", action="store_true")
    p.add_argument("--force", action="store_true")
    p = sub.add_parser("check"); p.add_argument("--run", required=True); p.add_argument("--chunks", default="1-24")
    a = ap.parse_args(); {"plan": cmd_plan, "check": cmd_check}[a.cmd](a)

if __name__ == "__main__": main()
