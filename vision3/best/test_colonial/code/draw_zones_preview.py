#!/usr/bin/env python3
"""draw_zones_preview.py : draw a zones JSON on a frame, to SEE whether the polygons line up (no GPU, a second).

  cd /orange/xiangyan/rithika/vision/vision3/best/test_colonial
  python code/extract_ref_frames.py --colonial-chunk 13 --times 5:00          # a clean frame -> zones/ref/...png
  python code/draw_zones_preview.py --zones zones/colonial_north_v2.json --image zones/ref/<that frame>.png --out zones/ref/preview_v2.png
Polygons are scaled by (image size / ref_size) exactly like the pipeline does, so what you see is what a run would use.
Colours: road green, bike lane yellow, sidewalk magenta, grass cyan.
"""
import argparse, json, cv2, numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--zones", required=True)
ap.add_argument("--image", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
z = json.load(open(a.zones))
img = cv2.imread(a.image)
if img is None:
    raise SystemExit(f"cannot read {a.image}")
h, w = img.shape[:2]
rw, rh = z.get("ref_size", [w, h])
if not rw or not rh:
    raise SystemExit("ref_size is missing or 0 in the zones file")
sx, sy = w / rw, h / rh
cols = {"road": (0, 200, 0), "bike": (0, 200, 255), "sidewalk": (255, 0, 200), "grass": (200, 200, 0)}   # BGR
over = img.copy()
for k, c in cols.items():
    if z.get(k):
        pts = np.array([[int(x * sx), int(y * sy)] for x, y in z[k]], np.int32)
        cv2.fillPoly(over, [pts], c)
out = cv2.addWeighted(over, 0.28, img, 0.72, 0)
for k, c in cols.items():
    if z.get(k):
        pts = np.array([[int(x * sx), int(y * sy)] for x, y in z[k]], np.int32)
        cv2.polylines(out, [pts], True, c, 2)
        cv2.putText(out, k, tuple(int(v) for v in pts.mean(0)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
cv2.imwrite(a.out, out)
print(f"image {w} x {h}, ref_size {rw} x {rh} (scale {sx:.3f} x {sy:.3f}); wrote {a.out}")
if sx < 0.4 or sx > 2.6 or abs(sx - sy) > 0.05:
    print("WARNING: unusual scale or different x/y scale: the polygons were probably drawn on a differently shaped image.")
