"""
Debug tool: inspect exactly what YOLO sees on ONE frame, with (almost) no
filtering, so we can tell apart two very different problems:

  (a) the model detects the object but at low confidence (below our normal
      conf=0.2 cutoff) -> fixable by lowering the threshold
  (b) the model does not detect the object at ANY confidence, or
      misclassifies it as something outside our class list -> a threshold
      tweak will never fix this; points to image quality / resolution /
      camera angle instead

Usage:
    python debug_frame.py "<video_path>" <timestamp_seconds>

Example:
    python debug_frame.py "pilot_clips/.../Standard_SCU8PM_2021-04-13_0000.013.mp4" 67

This grabs the frame at that timestamp, runs detection with conf=0.01 and
NO class restriction, prints every single box found (class + confidence),
and saves an annotated image plus the raw untouched frame so you can look
at both side by side.
"""
from ultralytics import YOLO
import cv2
import sys
import os

VIDEO_PATH = sys.argv[1]
TIMESTAMP_SECONDS = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
OUTPUT_DIR = "pilot_output/debug_frame"
os.makedirs(OUTPUT_DIR, exist_ok=True)

cap = cv2.VideoCapture(VIDEO_PATH)
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
target_frame = int(TIMESTAMP_SECONDS * fps)

print(f"Video native resolution: {width}x{height}, fps={fps:.2f}")
print(f"Seeking to frame {target_frame} (~{TIMESTAMP_SECONDS}s)")

cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
ret, frame = cap.read()
cap.release()

if not ret:
    print("Could not read a frame at that timestamp — check the timestamp is within the video's length.")
    sys.exit(1)

raw_path = os.path.join(OUTPUT_DIR, "raw_frame.jpg")
cv2.imwrite(raw_path, frame)
print(f"Raw frame saved to {raw_path}")

model = YOLO("yolov8l.pt")

# conf=0.01 and no `classes` filter: show literally everything the model
# considers even remotely plausible, across all 80 COCO classes. This is
# purely diagnostic — never use this threshold for real counting, it will
# be extremely noisy.
results = model.predict(frame, conf=0.01, imgsz=1280, verbose=False)

boxes = results[0].boxes
print(f"\nTotal raw detections at conf>=0.01 (all classes): {len(boxes) if boxes is not None else 0}")

if boxes is not None and len(boxes) > 0:
    # sort by confidence, highest first, so the most plausible ones are easy to scan
    entries = []
    for box in boxes:
        cls_name = model.names[int(box.cls)]
        conf = float(box.conf)
        xyxy = box.xyxy[0].tolist()
        entries.append((conf, cls_name, xyxy))
    entries.sort(reverse=True)
    for conf, cls_name, xyxy in entries:
        x1, y1, x2, y2 = [round(v) for v in xyxy]
        print(f"  {cls_name:12s} conf={conf:.3f}  box=({x1},{y1})-({x2},{y2})")
else:
    print("  NOTHING detected at all, even at conf=0.01. This points to an "
          "image quality / resolution / angle issue, not a threshold issue.")

annotated = results[0].plot()
annotated_path = os.path.join(OUTPUT_DIR, "annotated_all_classes.jpg")
cv2.imwrite(annotated_path, annotated)
print(f"\nFull annotated debug image (ALL classes, conf>=0.01) saved to {annotated_path}")
print("Open both raw_frame.jpg and annotated_all_classes.jpg side by side to see what the model is or isn't seeing.")
