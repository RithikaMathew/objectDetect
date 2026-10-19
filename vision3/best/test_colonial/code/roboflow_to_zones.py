#!/usr/bin/env python3
"""roboflow_to_zones.py : turn a Roboflow COCO export (polygons) into the zones JSON the pipeline reads.

  1. In Roboflow, upload the reference frame, make a polygon (instance segmentation) project with the classes  road, bike, sidewalk
     (names that contain 'road', 'bike' or 'side' are recognised), draw ONE polygon per class, then export the dataset as 'COCO'.
  2. Copy the _annotations.coco.json (any split) to the cluster and run:
       python code/roboflow_to_zones.py --coco _annotations.coco.json --out zones/colonial_north_v2.json
  3. Use it:  ZONES_JSON=zones/colonial_north_v2.json (or ZONES=... for run_new_video.sh)
The pipeline reads one polygon per zone; if you drew several for a class the largest is used (a warning says so). ref_size is the image size
stored in the export (the pipeline scales by video size / ref_size), so resizing in Roboflow does not matter as long as the aspect ratio is kept.
"""
import argparse, json, sys

ap = argparse.ArgumentParser()
ap.add_argument("--coco", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--image", default=None, help="part of the image file name, if the export has several images")
a = ap.parse_args()
d = json.load(open(a.coco))
cats = {c["id"]: c["name"].lower() for c in d.get("categories", [])}
imgs = d.get("images", [])
if not imgs:
    sys.exit("no images in that export")
img = next((i for i in imgs if a.image and a.image in i.get("file_name", "")), imgs[0])
if len(imgs) > 1 and not a.image:
    print(f"note: {len(imgs)} images in the export, using {img.get('file_name')} (choose with --image)")


def key_of(name):
    if "bike" in name or "cycle" in name:
        return "bike"
    if "side" in name or "walk" in name:
        return "sidewalk"
    if "road" in name or "street" in name or "lane" in name:
        return "road"
    return None


def area(pts):
    return abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))) / 2


best = {}
for an in d.get("annotations", []):
    if an.get("image_id") != img["id"]:
        continue
    k = key_of(cats.get(an["category_id"], ""))
    seg = an.get("segmentation")
    if k is None or not seg or not isinstance(seg, list):
        continue
    for poly in seg:
        pts = [[poly[i], poly[i + 1]] for i in range(0, len(poly) - 1, 2)]
        if len(pts) < 3:
            continue
        if k in best:
            print(f"warning: more than one polygon for '{k}': keeping the largest")
        if k not in best or area(pts) > area(best[k]):
            best[k] = pts
out = {"ref_size": [img["width"], img["height"]]}
for k in ("road", "bike", "sidewalk"):
    if k in best:
        out[k] = [[int(round(x)), int(round(y))] for x, y in best[k]]
    else:
        print(f"warning: no polygon found for '{k}' (the pipeline will run without it)")
json.dump(out, open(a.out, "w"), indent=1)
print(f"wrote {a.out}: ref_size {out['ref_size']}, zones: {', '.join(k for k in ('road', 'bike', 'sidewalk') if k in out)}")
