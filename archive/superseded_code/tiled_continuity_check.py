import sys
sys.path.insert(0, '.')
from pilot_detect_yolov8l import compute_tiles, detect_tiled
from ultralytics import YOLO
import cv2

video_path = "pilot_clips/MioVision Data/Bike Lane Study/MioVision Video/BL Colonial/Standard_SCU8OG_2019-07-10_0000/Standard_SCU8OG_2019-07-10_0000.008.mp4"
model = YOLO("yolov8l.pt")

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("FATAL: could not open video")
    raise SystemExit(1)

fps = cap.get(cv2.CAP_PROP_FPS)
start_frame = int(403 * fps)
n_frames = int(12 * fps)
cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

max_streak = 0
present_streak = 0
streak_range = None
streak_start = None

for i in range(n_frames):
    ret, frame = cap.read()
    if not ret:
        break
    t = 403 + i / fps
    tiles = compute_tiles(frame.shape)
    dets = detect_tiled(model, frame, tiles, classes=[1], conf=0.05, imgsz=1280)

    bike_dets = [d for d in dets if d[5] == 'bicycle']
    if not bike_dets:
        print(f"t={t:6.2f}s  NO bicycle after tiling+merge  (raw tile dets total this frame: {len(dets)})")
        present_streak = 0
    else:
        best = max(bike_dets, key=lambda d: d[4])
        print(f"t={t:6.2f}s  bicycle conf={best[4]:.3f}  xyxy={[round(v,1) for v in best[:4]]}  ({len(bike_dets)} bicycle box(es) this frame)")
        if present_streak == 0:
            streak_start = t
        present_streak += 1
        if present_streak > max_streak:
            max_streak = present_streak
            streak_range = (streak_start, t)

print(f"\n=== SUMMARY (TILED pipeline) ===")
print(f"Longest continuous run: {max_streak} frames ({max_streak/fps:.2f}s)")
print(f"Range: {streak_range}")
print(f"min_track_hits needed: 6")
