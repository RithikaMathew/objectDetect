from ultralytics import YOLO
import cv2
import os

video_path = "pilot_clips/MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/Standard_SCU8OG_2019-07-10_0000/Standard_SCU8OG_2019-07-10_0000.008.mp4"
model = YOLO("yolov8l.pt")

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"FATAL: could not open video at path: {video_path}")
    print(f"Current working directory: {os.getcwd()}")
    raise SystemExit(1)

fps = cap.get(cv2.CAP_PROP_FPS)
print(f"Video opened OK. fps={fps}")

start_frame = int(403 * fps)
n_frames = int(12 * fps)
cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

present_streak = 0
max_streak = 0
streak_start_t = None
best_streak_range = None

for i in range(n_frames):
    ret, frame = cap.read()
    if not ret:
        print(f"WARNING: frame read failed at i={i}, stopping early")
        break
    t = 403 + i / fps
    results = model.predict(frame, classes=[1], conf=0.05, imgsz=1280, verbose=False)
    boxes = results[0].boxes
    if len(boxes) == 0:
        print(f"t={t:6.2f}s  NO bicycle box")
        present_streak = 0
    else:
        conf = float(boxes[0].conf)
        xyxy = [round(v, 1) for v in boxes[0].xyxy[0].tolist()]
        print(f"t={t:6.2f}s  bicycle conf={conf:.3f}  xyxy={xyxy}")
        if present_streak == 0:
            streak_start_t = t
        present_streak += 1
        if present_streak > max_streak:
            max_streak = present_streak
            best_streak_range = (streak_start_t, t)

print(f"\n=== SUMMARY ===")
print(f"Longest continuous run of frames with a bicycle box: {max_streak} frames")
print(f"(fps={fps:.2f}, so {max_streak} frames = {max_streak/fps:.2f}s)")
if best_streak_range:
    print(f"Best streak: t={best_streak_range[0]:.2f}s to t={best_streak_range[1]:.2f}s")
else:
    print("No streak found")
print(f"min_track_hits required by pilot_detect.py: 6")
