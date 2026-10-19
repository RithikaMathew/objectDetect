#!/usr/bin/env python3
"""fusion_probe.py : which label rule would have been RIGHT on the people in your truth files?  (no GPU, takes seconds)

  cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
  python code/fusion_probe.py --root . --runs exp0_base,exp1_sahi,exp3a_speed

For every truth person it finds the model track (by time, like eval_truth.py) and prints that track's features from *_rules_audit.csv:
X-CLIP label and weighted bicyclist probability, detector %cyclist, speed in body heights/s, direction, seconds on screen.
Then it replays simple rules on those tracks and counts how many labels each rule gets right:
  veto P      X-CLIP BICYCLIST but detector cyclist < P%  -> pedestrian
  promote Q   X-CLIP PEDESTRIAN but detector cyclist >= Q% -> bicyclist
  speed       lateral tracks only (moving left/right), >= 1.5 s: slow + detector < 50% cyclist -> pedestrian; fast + detector >= 50% -> bicyclist
Only tracks that X-CLIP scored are used. The same person appears once per run, so the totals count them several times: look at the
per-row table too. With so few people this is a hint for choosing thresholds, never a proof (and the numbers are fitted on these clips).
"""
import argparse, csv, datetime, glob, importlib.util, os


def load_eval(root):
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eval_truth.py")
    spec = importlib.util.spec_from_file_location("eval_truth", p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def fnum(x, d=float("nan")):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--runs", default="exp0_base,exp1_sahi")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    ev = load_eval(a.root)
    root = os.path.abspath(a.root)
    rows, extras = [], []
    for run in a.runs.split(","):
        for cname, cc in ev.CLIPS.items():
            tf = glob.glob(os.path.join(root, "counts", run, f"*.{cc['chunk']:03d}_tracks.csv"))
            af = glob.glob(os.path.join(root, "counts", run, f"*.{cc['chunk']:03d}_rules_audit.csv"))
            if not tf or not af:
                continue
            truth = ev.read_truth(os.path.join(root, cc["truth"]))[0]
            t0 = datetime.datetime.strptime(cc["start"], "%Y-%m-%d %H:%M:%S")
            tracks = ev.read_tracks(sorted(tf)[0], t0)
            aud = {r["track_id"]: r for r in csv.DictReader(open(sorted(af)[0]))}
            res, extra_tr = ev.match(truth, tracks)
            if truth:
                for k in extra_tr:
                    r = aud.get(k["id"])
                    if r:
                        extras.append(dict(run=run, clip=cname, track=k["id"], when=f"{ev.fmt(max(k['f'], 0))}-{ev.fmt(k['l'])}", secs=r["secs"],
                                           xl=r["xclip_label"].lower(), wbic=fnum(r["weighted_bicyclist"]), det=fnum(r["det_cyclist_pct"]),
                                           spd=fnum(r["speed_heights_per_s"]), net=fnum(r["net_px"]), dir=r["direction"]))
            for t, status, k in res:
                if k is None or k["id"] not in aud:
                    continue
                r = aud[k["id"]]
                rows.append(dict(run=run, clip=cname, tid=t["id"], truth=t["c"], when=ev.fmt(t["s"]), track=k["id"], secs=r["secs"], xl=r["xclip_label"].lower(),
                                 wbic=fnum(r["weighted_bicyclist"]), det=fnum(r["det_cyclist_pct"]), spd=fnum(r["speed_heights_per_s"]),
                                 span=fnum(r["speed_span_s"]), net=fnum(r["net_px"]), dir=r["direction"], counted=r["counted"]))
    out = ["# Fusion probe", "", f"runs: {a.runs}", ""]
    if not rows:
        out.append("No truth person matched a scored track (are the truth files filled in and the runs finished?).")
    else:
        out += ["| run | clip | truth | when | track | secs | X-CLIP | wBIC | det %cyc | speed h/s | net px | direction | counted |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            out.append(f"| {r['run']} | {r['clip']} | {r['tid']} {r['truth']} | {r['when']} | #{r['track']} | {r['secs']} | {r['xl']} | {r['wbic']:.2f} | {r['det']:.0f} | {r['spd']:.2f} | {r['net']:.0f} | {r['dir']} | {r['counted']} |")
        want = lambda r: "cyclist" if r["truth"] == "cyclist" else "pedestrian"
        xl = lambda r: "cyclist" if r["xl"].startswith("bic") else "pedestrian"
        out += ["", "## Detector / X-CLIP error patterns", "",
                "Classification of matched, scored tracks only; duration/counting failures and misses are separate.",
                "Each row below is one run. Repeated people across runs are not independent examples.", "",
                "| run | both right | both wrong | detector right / X-CLIP wrong | detector wrong / X-CLIP right |",
                "|---|---|---|---|---|"]
        for run in a.runs.split(","):
            rr = [r for r in rows if r["run"] == run]
            groups = [[], [], [], []]
            for r in rr:
                if not 0 <= r["det"] <= 100:
                    continue
                dr = ("cyclist" if r["det"] >= 50 else "pedestrian") == want(r)
                xr = xl(r) == want(r)
                groups[0 if dr and xr else 1 if not dr and not xr else 2 if dr else 3].append(
                    f"{r['clip']}/{r['tid']} ({r['dir']}, {r['secs']}s)")
            out.append(f"| {run} | " + " | ".join(f"{len(g)}: {', '.join(g) or '-'}" for g in groups) + " |")
        out += ["", "Use these named cases to inspect the source video. Direction is measured image motion; "
                "it cannot prove a missed person was walking away, since missed people have no track. "
                "Missing detector shares are excluded. This comparison does not measure detector recall."]

        def score(fn):
            ok = sum(1 for r in rows if fn(r) == want(r))
            flips = [f"{r['run']}/{r['clip']}/{r['tid']}({'ok' if fn(r) == want(r) else 'WRONG'})" for r in rows if fn(r) != xl(r)]
            return ok, flips

        def veto(P, Q=None):
            def f(r):
                c = xl(r)
                if c == "cyclist" and r["det"] < P:
                    return "pedestrian"
                if Q is not None and c == "pedestrian" and r["det"] >= Q:
                    return "cyclist"
                return c
            return f

        def speed(W, R):
            def f(r):
                c = xl(r)
                if r["dir"] not in ("moving_left", "moving_right") or r["span"] < 1.5 or r["spd"] != r["spd"]:
                    return c
                if c == "cyclist" and r["spd"] < W and r["det"] < 50:
                    return "pedestrian"
                if c == "pedestrian" and r["spd"] > R and r["det"] >= 50:
                    return "cyclist"
                return c
            return f
        out += ["", f"## Rules replayed on {len(rows)} (person, run) pairs", "", "| rule | right | of | labels it changes |", "|---|---|---|---|"]
        ok, fl = score(xl); out.append(f"| X-CLIP alone (now) | {ok} | {len(rows)} | |")
        for P in (5, 10, 15, 20, 30, 40, 50):
            ok, fl = score(veto(P)); out.append(f"| veto {P}% | {ok} | {len(rows)} | {', '.join(fl) or '-'} |")
        for Q in (80, 90, 95):
            ok, fl = score(veto(0, Q)); out.append(f"| promote {Q}% | {ok} | {len(rows)} | {', '.join(fl) or '-'} |")
        for W, R in ((0.8, 2.0), (1.0, 2.0), (1.2, 2.5), (1.5, 3.0)):
            ok, fl = score(speed(W, R)); out.append(f"| speed lateral walk<{W} ride>{R} | {ok} | {len(rows)} | {', '.join(fl) or '-'} |")
        out += ["", "Read the per-row table first: do real riders and real walkers separate on speed (lateral tracks) or on det %cyc? "
                "A rule that only 'wins' by changing one or two rows is a coincidence."]
    if extras:
        out += ["", "## Counted tracks that match NO truth person (false detections, or a person missing from the truth file)", "",
                "| run | clip | when | track | secs | X-CLIP | wBIC | det %cyc | speed h/s | net px | direction |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in extras:
            out.append(f"| {r['run']} | {r['clip']} | {r['when']} | #{r['track']} | {r['secs']} | {r['xl']} | {r['wbic']:.2f} | {r['det']:.0f} | {r['spd']:.2f} | {r['net']:.0f} | {r['dir']} |")
        out.append("")
        out.append("A static object (barricade, sign) tracked as a person should show a tiny net movement and speed; compare with the real people above before choosing a filter.")
    txt = "\n".join(out)
    path = a.out or os.path.join(root, "exp_results", f"FUSION_PROBE_{datetime.datetime.now():%Y%m%d_%H%M}.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(txt)
    print(txt); print(f"\nwritten: {path}")


if __name__ == "__main__":
    main()
