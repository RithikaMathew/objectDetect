#!/usr/bin/env python3
"""Turn a fisheye video/frame into a normal (rectilinear) view, or a grid of guesses.

Lens parameters are unknown for the 2025 camera, so this works from a FIELD OF VIEW guess.
Model: r = f*theta (equidistant, most common). Others: equisolid, stereographic, orthographic.

  # 1) look at guesses on one frame, pick the one where straight things look straight
  python code/undistort_fisheye.py preview --image frame.png --out preview.png --fovs 150,180,200
  # 2) convert a clip (needs the chosen fov / out-fov / pitch)
  python code/undistort_fisheye.py video --video in.mp4 --out out.mp4 --fov 180 --out-fov 110 --pitch 40
  # self-test (no files needed)
  python code/undistort_fisheye.py selftest

--fov      full field of view of the fisheye image circle (degrees); the circle is assumed to touch the
           short side of the frame unless --radius (pixels) is given. --cx/--cy = circle centre (default frame centre).
--out-fov  horizontal field of view of the flat output view. Keep it < 150: a flat view cannot show 180 degrees.
--yaw/--pitch/--roll  turn the virtual camera (degrees). pitch>0 looks DOWN (toward the road below a pole camera).
NOTE: objects straight below the camera are stretched hard (or lost) in any flat view. Use --pitch to
point a flat view at the area you care about; run more than one view if needed.
"""
import argparse, math, subprocess, sys
import numpy as np, cv2

def _proj_r(theta, f, model):
    if model == "equidistant":   return f * theta
    if model == "equisolid":     return 2 * f * np.sin(theta / 2)
    if model == "stereographic": return 2 * f * np.tan(theta / 2)
    if model == "orthographic":  return f * np.sin(theta)
    raise ValueError(model)

def _theta_max_r(fov_deg, f, model):
    return _proj_r(np.array(math.radians(fov_deg) / 2), f, model)

def _rot(yaw, pitch, roll):
    y, p, r = map(math.radians, (yaw, pitch, roll))
    Ry = np.array([[math.cos(y), 0, math.sin(y)], [0, 1, 0], [-math.sin(y), 0, math.cos(y)]])
    Rx = np.array([[1, 0, 0], [0, math.cos(p), math.sin(p)], [0, -math.sin(p), math.cos(p)]])  # +pitch = look down
    Rz = np.array([[math.cos(r), -math.sin(r), 0], [math.sin(r), math.cos(r), 0], [0, 0, 1]])
    return Ry @ Rx @ Rz

def build_maps(in_w, in_h, out_w, out_h, fov, out_fov, model="equidistant",
               yaw=0.0, pitch=0.0, roll=0.0, cx=None, cy=None, radius=None, coverage="circular"):
    """Return (map_x, map_y) for cv2.remap: for every output pixel, where to read in the fisheye image."""
    cx = in_w / 2 if cx is None else cx
    cy = in_h / 2 if cy is None else cy
    if coverage not in ("circular", "full-frame"):
        raise ValueError("coverage must be circular or full-frame")
    if not 0 < fov < 360 or not 0 < out_fov < 180:
        raise ValueError("require 0 < fov < 360 and 0 < out_fov < 180")
    if model == "orthographic" and fov > 180:
        raise ValueError("orthographic projection requires fov <= 180")
    # For a rectangular crop, interpret fov at its farthest corner, rather
    # than masking the image to a short-side circle. This is a guess, not calibration.
    if radius is None:
        radius = (math.hypot(max(cx, in_w - 1 - cx), max(cy, in_h - 1 - cy))
                  if coverage == "full-frame" else min(in_w, in_h) / 2)
    if radius <= 0:
        raise ValueError("radius must be positive")
    # focal length f of the fisheye so that theta=fov/2 lands at `radius`
    f = radius / float(_theta_max_r(fov, 1.0, model))
    f_out = (out_w / 2) / math.tan(math.radians(out_fov) / 2)
    u, v = np.meshgrid(np.arange(out_w) - (out_w - 1) / 2, np.arange(out_h) - (out_h - 1) / 2)
    rays = np.stack([u / f_out, v / f_out, np.ones_like(u)], -1)            # x right, y down, z forward
    rays = rays @ _rot(yaw, pitch, roll).T
    rays /= np.linalg.norm(rays, axis=-1, keepdims=True)
    theta = np.arccos(np.clip(rays[..., 2], -1, 1))
    phi = np.arctan2(rays[..., 1], rays[..., 0])
    r = _proj_r(theta, f, model)
    mx = (cx + r * np.cos(phi)).astype(np.float32)
    my = (cy + r * np.sin(phi)).astype(np.float32)
    outside = (theta > math.radians(fov) / 2) | (r > radius * 1.0001)
    mx[outside] = -1; my[outside] = -1                                      # black where the lens saw nothing
    return mx, my

def undistort(img, fov, out_fov, out_size=None, **kw):
    h, w = img.shape[:2]
    ow, oh = out_size or (w, h)
    mx, my = build_maps(w, h, ow, oh, fov, out_fov, **kw)
    return cv2.remap(img, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)

def cmd_preview(a):
    img = cv2.imread(a.image)
    if img is None: sys.exit(f"cannot read {a.image}")
    tiles = []
    for fov in [float(x) for x in a.fovs.split(",")]:
        t = undistort(img, fov, a.out_fov, model=a.model, yaw=a.yaw, pitch=a.pitch, roll=a.roll,
                      cx=a.cx, cy=a.cy, radius=a.radius, coverage=a.coverage)
        t = cv2.resize(t, (640, int(640 * t.shape[0] / t.shape[1])))
        cv2.putText(t, f"fov={fov:g} out_fov={a.out_fov:g} pitch={a.pitch:g}", (8, 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        tiles.append(t)
    cv2.imwrite(a.out, np.hstack(tiles) if len(tiles) <= 3 else np.vstack(
        [np.hstack(tiles[i:i + 3] + [np.zeros_like(tiles[0])] * (3 - len(tiles[i:i + 3]))) for i in range(0, len(tiles), 3)]))
    print("wrote", a.out)

def cmd_video(a):
    cap = cv2.VideoCapture(a.video)
    if not cap.isOpened(): sys.exit(f"cannot open {a.video}")
    w, h = int(cap.get(3)), int(cap.get(4)); fps = cap.get(5) or 30.0
    ow, oh = (a.size or (w, h))
    mx, my = build_maps(w, h, ow, oh, a.fov, a.out_fov, a.model, a.yaw, a.pitch, a.roll, a.cx, a.cy, a.radius, a.coverage)
    # raw frames piped to ffmpeg so the output is a normal h264 mp4
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
                          "-s", f"{ow}x{oh}", "-r", f"{fps}", "-i", "-", "-an", "-c:v", "libx264",
                          "-pix_fmt", "yuv420p", "-crf", "18", a.out], stdin=subprocess.PIPE)
    n = 0
    while True:
        ok, fr = cap.read()
        if not ok or (a.max_frames and n >= a.max_frames): break
        p.stdin.write(cv2.remap(fr, mx, my, cv2.INTER_LINEAR).tobytes()); n += 1
    p.stdin.close(); status = p.wait(); cap.release()
    if status: sys.exit(f"ffmpeg failed (exit {status}); output is incomplete")
    print(f"wrote {a.out}: {n} frames, {ow}x{oh}, {fps:.2f} fps")

def selftest():
    """Distort a synthetic grid with the forward fisheye model, undistort it, compare to the original."""
    W = H = 800
    flat = np.full((H, W, 3), 255, np.uint8)
    for k in range(0, W, 50):
        cv2.line(flat, (k, 0), (k, H), (0, 0, 0), 2); cv2.line(flat, (0, k), (W, k), (0, 0, 0), 2)
    out_fov = 90.0
    # forward: build a fisheye (fov 180) image by sampling the flat grid with the inverse of our own maps
    f_flat = (W / 2) / math.tan(math.radians(out_fov) / 2)
    f_fe = (min(W, H) / 2) / (math.pi / 2)
    yy, xx = np.meshgrid(np.arange(H) - (H - 1) / 2, np.arange(W) - (W - 1) / 2, indexing="ij")
    r = np.hypot(xx, yy); theta = r / f_fe; phi = np.arctan2(yy, xx)
    valid = theta < math.radians(out_fov) / 2 * 0.98
    rr = f_flat * np.tan(np.minimum(theta, 1.5))
    mx = ((W - 1) / 2 + rr * np.cos(phi)).astype(np.float32); my = ((H - 1) / 2 + rr * np.sin(phi)).astype(np.float32)
    fish = cv2.remap(flat, mx, my, cv2.INTER_LINEAR); fish[~valid] = 0
    back = undistort(fish, 180.0, out_fov, (W, H))
    # compare in the central 60% (corners of the flat view are outside what the fisheye sampled)
    a0, a1 = int(W * .2), int(W * .8)
    bl = lambda x: cv2.GaussianBlur(x[a0:a1, a0:a1], (0, 0), 4).astype(int)
    diff = np.abs(bl(back) - bl(flat)).mean()
    print(f"selftest mean abs diff in centre: {diff:.2f} (expect < 6)")
    # geometry checks: zero rotation maps the output centre to the fisheye centre; pitch moves it
    m0x, m0y = build_maps(W, H, 101, 101, 180, 90)
    assert abs(m0x[50, 50] - (W / 2)) < 1.5 and abs(m0y[50, 50] - (H / 2)) < 1.5, "centre mismatch"
    m1x, m1y = build_maps(W, H, 101, 101, 180, 90, pitch=30)
    assert m1y[50, 50] > m0y[50, 50] + 50 and abs(m1x[50, 50] - m0x[50, 50]) < 1.5, "pitch should look down (larger y)"
    print("selftest geometry OK"); assert diff < 6

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    def common(p):
        p.add_argument("--out-fov", type=float, default=110); p.add_argument("--model", default="equidistant",
                       choices=["equidistant", "equisolid", "stereographic", "orthographic"])
        for n in ("yaw", "pitch", "roll"): p.add_argument(f"--{n}", type=float, default=0.0)
        for n in ("cx", "cy", "radius"): p.add_argument(f"--{n}", type=float, default=None)
        p.add_argument("--coverage", choices=["circular", "full-frame"], default="circular",
                       help="full-frame: rectangular image, fov interpreted diagonally; uncalibrated guess")
    p = sub.add_parser("preview"); p.add_argument("--image", required=True); p.add_argument("--out", required=True)
    p.add_argument("--fovs", default="150,180,200"); common(p)
    p = sub.add_parser("video"); p.add_argument("--video", required=True); p.add_argument("--out", required=True)
    p.add_argument("--fov", type=float, required=True); p.add_argument("--max-frames", type=int, default=0)
    p.add_argument("--size", type=lambda s: tuple(int(x) for x in s.split("x")), default=None, help="output WxH"); common(p)
    sub.add_parser("selftest")
    a = ap.parse_args()
    {"preview": cmd_preview, "video": cmd_video, "selftest": lambda a: selftest()}[a.cmd](a)

if __name__ == "__main__":
    main()
