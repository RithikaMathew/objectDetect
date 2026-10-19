#!/usr/bin/env python3
"""Grounding DINO hard-frame audit against saved b4 tracks, NOT person recall.

No counting integration: a bicycle box is not proof of a cyclist. Sampled
images and CSVs allow inspection of proposals that baseline tracking lacks.
"""
import argparse
import csv
import json
from pathlib import Path

PROMPT = "a person. a bicycle. a motorcycle."


def load_model(model_path, local_only):
    import torch
    from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
    processor = AutoProcessor.from_pretrained(model_path, local_files_only=local_only)
    model = AutoModelForZeroShotObjectDetection.from_pretrained(
        model_path, local_files_only=local_only, use_safetensors=True).to("cuda").eval()
    return processor, model


def predict(processor, model, image):
    import torch
    inputs = processor(images=image, text=PROMPT, return_tensors="pt").to("cuda")
    with torch.inference_mode():
        outputs = model(**inputs)
    return processor.post_process_grounded_object_detection(
        outputs, inputs.input_ids, box_threshold=.3, text_threshold=.25,
        target_sizes=[image.size[::-1]])[0]


def prepare(root, ready):
    import torch
    import transformers
    from PIL import Image
    from huggingface_hub import snapshot_download
    if not torch.cuda.is_available():
        raise RuntimeError("Grounding DINO preparation requires an allocated GPU")
    snapshot = snapshot_download("IDEA-Research/grounding-dino-tiny",
                                 cache_dir=str(root / ".research_models"),
                                 allow_patterns=["*.json", "*.txt", "*.safetensors"])
    processor, model = load_model(snapshot, True)
    predict(processor, model, Image.new("RGB", (320, 240)))
    ready.write_text(json.dumps(dict(model_path=snapshot, revision=Path(snapshot).name,
                                    transformers=transformers.__version__, torch=torch.__version__), indent=2))


def max_iou(box, tracks):
    best = 0.
    x1, y1, x2, y2 = box
    for t in tracks:
        cx, cy, w, h = [float(t[k]) for k in ("box_cx", "box_cy", "box_w", "box_h")]
        a, b, c, d = cx-w/2, cy-h/2, cx+w/2, cy+h/2
        inter = max(0, min(x2,c)-max(x1,a)) * max(0, min(y2,d)-max(y1,b))
        union = max(0,x2-x1)*max(0,y2-y1) + w*h - inter
        best = max(best, inter/union if union else 0)
    return best


def audit(root, ready, clip, video, out):
    import cv2
    from PIL import Image
    from eval_truth import CLIPS, read_truth
    from research_detection import audit_times
    cc = CLIPS[clip]
    truth, skipped = read_truth(root / cc["truth"])
    if not truth or skipped:
        raise RuntimeError(f"incomplete truth for audit: {skipped}")
    model_info = json.loads(ready.read_text())
    processor, model = load_model(model_info["model_path"], True)
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened(): raise RuntimeError(f"cannot open {video}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0: raise RuntimeError("invalid video FPS")
    offset = int(cc["start"][14:16])*60 + int(cc["start"][17:19])
    frames = {int(round((offset+t)*fps))+1: t for t in audit_times(truth)}
    trajectories = list((root / "counts/b4_combo_static5").glob(f"*.{cc['chunk']:03d}_trajectories.csv"))
    if len(trajectories) != 1: raise RuntimeError("need one unambiguous baseline trajectory CSV")
    tracks = {f: [] for f in frames}
    with trajectories[0].open() as f:
        for row in csv.DictReader(f):
            fi = int(row["frame"])
            if fi in tracks: tracks[fi].append(row)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for fi, when in sorted(frames.items()):
        cap.set(cv2.CAP_PROP_POS_FRAMES, fi-1)
        ok, frame = cap.read()
        if not ok: raise RuntimeError(f"cannot read audit frame {fi}")
        result = predict(processor, model, Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
        left, right = frame.copy(), frame.copy()
        for t in tracks[fi]:
            cx,cy,w,h = [float(t[k]) for k in ("box_cx","box_cy","box_w","box_h")]
            cv2.rectangle(left,(int(cx-w/2),int(cy-h/2)),(int(cx+w/2),int(cy+h/2)),(0,255,0),2)
        labels = result.get("text_labels", result.get("labels"))
        for box, score, label in zip(result["boxes"].tolist(), result["scores"].tolist(), labels):
            overlap = max_iou(box, tracks[fi])
            rows.append(dict(clip=clip, frame=fi, clip_second=when, label=str(label), score=score,
                             x1=box[0], y1=box[1], x2=box[2], y2=box[3], baseline_track_iou=overlap))
            x1,y1,x2,y2 = map(int,box)
            cv2.rectangle(right,(x1,y1),(x2,y2),(0,200,255),2)
            cv2.putText(right,f"{label} {score:.2f}",(max(0,x1),max(18,y1)),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,200,255),1)
        cv2.putText(left,"Saved b4 tracks (includes rejected/coasted)",(8,22),cv2.FONT_HERSHEY_SIMPLEX,.5,(255,255,255),1)
        cv2.putText(right,"Grounding DINO proposals",(8,22),cv2.FONT_HERSHEY_SIMPLEX,.5,(255,255,255),1)
        import numpy as np
        if not cv2.imwrite(str(out / f"{fi:06d}_{when:.1f}s.jpg"),np.hstack([left,right])):
            raise RuntimeError("could not write audit image")
    cap.release()
    cols = ["clip","frame","clip_second","label","score","x1","y1","x2","y2","baseline_track_iou"]
    with (out/"proposals.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
    (out/"summary.json").write_text(json.dumps(dict(frames=len(frames),proposals=len(rows),
        low_overlap_proposals=sum(r["baseline_track_iou"]<.3 for r in rows),model=model_info,
        limitation="Frame-selected proposal audit only; low overlap is not a confirmed missed person. Bicycle/motorcycle proposals are not cyclist counts."),indent=2))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode",choices=["prepare","audit"])
    ap.add_argument("--root",type=Path,required=True);ap.add_argument("--ready",type=Path,required=True)
    ap.add_argument("--clip");ap.add_argument("--video",type=Path);ap.add_argument("--out",type=Path)
    a=ap.parse_args()
    if a.mode=="prepare": prepare(a.root,a.ready)
    else: audit(a.root,a.ready,a.clip,a.video,a.out)


if __name__=="__main__": main()
