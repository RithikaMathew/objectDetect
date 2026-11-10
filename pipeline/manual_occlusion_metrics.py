#!/usr/bin/env python3
"""Compare occluded-event trajectory reconstructions from manual car clicks.

This is deliberately CPU-only and exploratory. It uses the saved pedestrian
trajectory plus manually clicked car points, then compares observed, linearly
interpolated, constant-velocity, Kalman, and RTS reconstructions. It never
turns an unobserved car position into ground truth.
"""
import argparse
import csv
import json
from pathlib import Path
import sys

import numpy as np

CODE = Path(__file__).resolve().parents[1] / "vision3/best/test_colonial/code"
sys.path.insert(0, str(CODE))
from clearance_metrics import (  # noqa: E402
    collision_ttc,
    dimensions,
    kalman_motion,
    pet_cells,
    prepare,
    project,
    road_axis,
)


def read_rows(path):
    with Path(path).open(newline="") as stream:
        return list(csv.DictReader(stream))


def finite(value):
    return value is not None and np.isfinite(float(value))


def manual_samples(rows, H, fps):
    points = []
    for row in rows:
        if row.get("object") != "car":
            continue
        pixel = np.array([float(row["x_px"]), float(row["y_px"])])
        points.append(dict(
            frame=int(row["frame"]),
            t=float(row["clip_seconds"]),
            pixel=pixel,
            xy=project(H, [pixel])[0],
            inside=False,
            box_w=1.8,
            box_h=1.0,
            facility="manual_occlusion_annotation",
            counted="",
            identity_status="manual_click",
        ))
    points.sort(key=lambda item: item["frame"])
    if len(points) < 3:
        raise ValueError("At least three manual car points are required")
    if len({item["frame"] for item in points}) != len(points):
        raise ValueError("Duplicate manual car frame; keep one click per frame")
    return points


def with_velocity(samples):
    result = []
    times = np.array([item["t"] for item in samples], dtype=float)
    positions = np.array([item["xy"] for item in samples], dtype=float)
    if len(samples) == 1:
        velocities = np.zeros((1, 2))
    else:
        velocities = np.gradient(positions, times, axis=0, edge_order=1)
    for item, velocity in zip(samples, velocities):
        result.append({**item, "velocity": velocity})
    return result


def target_frames(pedestrian):
    return sorted(pedestrian, key=lambda item: item["frame"])


def interpolate_method(manual, frames, mode):
    mt = np.array([item["t"] for item in manual])
    mx = np.array([item["xy"][0] for item in manual])
    my = np.array([item["xy"][1] for item in manual])
    target = np.array([item["t"] for item in frames])
    if mode == "linear":
        x = np.interp(target, mt, mx)
        y = np.interp(target, mt, my)
        mask = (target >= mt.min()) & (target <= mt.max())
    elif mode == "constant_velocity":
        px = np.polyfit(mt - mt.mean(), mx, 1)
        py = np.polyfit(mt - mt.mean(), my, 1)
        x = np.polyval(px, target - mt.mean())
        y = np.polyval(py, target - mt.mean())
        mask = np.ones(len(target), dtype=bool)
    else:
        raise ValueError(mode)
    result = []
    for frame, t, xx, yy, keep in zip(frames, target, x, y, mask):
        if not keep:
            continue
        result.append({**frame, "xy": np.array([xx, yy]), "pixel": np.array([np.nan, np.nan]), "inside": False})
    return with_velocity(result)


def filtered_method(manual, frames, rts):
    filtered = kalman_motion(manual, rts=rts)
    if not filtered:
        return []
    known = sorted(filtered.values(), key=lambda item: item["frame"])
    known_t = np.array([item["t"] for item in known])
    known_x = np.array([item["xy"][0] for item in known])
    known_y = np.array([item["xy"][1] for item in known])
    target = np.array([item["t"] for item in frames])
    x = np.interp(target, known_t, known_x)
    y = np.interp(target, known_t, known_y)
    result = []
    for frame, xx, yy in zip(frames, x, y):
        result.append({**frame, "xy": np.array([xx, yy]), "pixel": np.array([np.nan, np.nan]), "inside": False})
    return with_velocity(result)


def observed_method(manual, frames):
    by_frame = {item["frame"]: item for item in manual}
    result = []
    for frame in frames:
        item = by_frame.get(frame["frame"])
        if item is not None:
            result.append(item)
    return with_velocity(result)


def metrics_for(subject, car, axis, method):
    by_subject = {item["frame"]: item for item in subject}
    by_car = {item["frame"]: item for item in car}
    common = sorted(by_subject.keys() & by_car.keys())
    if len(common) < 3:
        return dict(method=method, samples=len(common), min_center_distance_m="", min_lateral_gap_m="",
                    min_ttc_s="", pet_s="", coverage_fraction=0., interpretation="insufficient_common_samples")
    basis = np.column_stack((axis, [-axis[1], axis[0]]))
    subject_dims = dimensions("pedestrian", .6)
    car_dims = dimensions("car", .8)
    half = (np.array(subject_dims) + car_dims) / 2
    sample_rows = []
    for frame in common:
        a, b = by_subject[frame], by_car[frame]
        relative = (b["xy"] - a["xy"]) @ basis
        relative_velocity = (b["velocity"] - a["velocity"]) @ basis
        alongside = abs(relative[0]) <= half[0]
        lateral_gap = max(0., abs(relative[1]) - half[1]) if alongside else None
        sample_rows.append(dict(
            frame=frame,
            t=a["t"],
            relative=relative,
            relative_velocity=relative_velocity,
            center_distance=float(np.linalg.norm(relative)),
            lateral_gap=lateral_gap,
            ttc=collision_ttc(relative, relative_velocity, half),
        ))
    subject_dict = {item["frame"]: item for item in subject if item["frame"] in common}
    car_dict = {item["frame"]: item for item in car if item["frame"] in common}
    pet = pet_cells(subject_dict, car_dict, (subject_dims, car_dims), basis)
    ttcs = [row["ttc"] for row in sample_rows if row["ttc"] is not None]
    gaps = [row["lateral_gap"] for row in sample_rows if row["lateral_gap"] is not None]
    return dict(
        method=method,
        samples=len(common),
        min_center_distance_m=min(row["center_distance"] for row in sample_rows),
        min_lateral_gap_m=min(gaps) if gaps else "",
        min_ttc_s=min(ttcs) if ttcs else "",
        pet_s=pet if pet is not None else "",
        coverage_fraction=len(common) / max(1, len(subject)),
        first_common_s=sample_rows[0]["t"],
        last_common_s=sample_rows[-1]["t"],
        interpretation="exploratory_manual_car_reconstruction_not_validated",
    )


def run(batch, task_name, annotations, out):
    batch = Path(batch).resolve(); out = Path(out).resolve(); out.mkdir(parents=True, exist_ok=True)
    task = batch / task_name
    log = json.loads((task / "run_log.json").read_text())
    geometry = json.loads((task / "geometry.json").read_text())
    H = np.asarray(geometry["H"], dtype=float)
    rows = read_rows(annotations)
    manual = manual_samples(rows, H, float(log["fps"]))
    labels = {row["track_id"]: row for row in read_rows(task / "tracks_csv.csv")}
    paths = prepare(read_rows(task / "trajectories_csv.csv") + read_rows(task / "vehicle_trajectories_csv.csv"),
                    H, np.asarray(geometry["hull"], dtype=np.float32), float(log["fps"]), labels)
    subject = paths.get(("pedestrian", "1"))
    if not subject:
        raise ValueError("Pedestrian track 1 is not present in the saved trajectories")
    subject = with_velocity([item for item in subject if 40 <= item["t"] <= 53])
    axis = road_axis(paths, ("pedestrian",))
    frames = target_frames(subject)
    methods = {
        "manual_observed": observed_method(manual, frames),
        "linear_interpolation": interpolate_method(manual, frames, "linear"),
        "constant_velocity": interpolate_method(manual, frames, "constant_velocity"),
        "kalman": filtered_method(manual, frames, rts=False),
        "rts": filtered_method(manual, frames, rts=True),
    }
    comparison = [metrics_for(subject, car, axis, name) for name, car in methods.items()]
    with (out / "method_comparison.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(comparison[0]))
        writer.writeheader(); writer.writerows(comparison)
    (out / "README.md").write_text(
        "# Manual occlusion metric comparison\n\n"
        "The car points were manually clicked through the overlap. Methods are "
        "compared on the same event: observed clicks, linear interpolation, "
        "constant velocity, Kalman filtering and RTS smoothing. Values are "
        "exploratory and use the existing learned camera map. The method with "
        "the smallest TTC or clearance is not automatically the best; agreement "
        "with observed clicks, continuity, and visual plausibility are required.\n\n"
        "See method_comparison.csv. No method reconstructs a truly hidden car "
        "position as observed ground truth.\n"
    )
    print(out / "method_comparison.csv")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=Path, required=True)
    parser.add_argument("--task", default="colonial_1708_pedestrian_car_reference")
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    run(args.batch, args.task, args.annotations, args.out)


if __name__ == "__main__":
    main()
