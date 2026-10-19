"""Frozen-detector experiments; no model imports or downloads at module import."""
import numpy as np


def tta_people(det, frame, conf, base_size, sizes, device, people_ids, predict):
    """Extra full-frame scale/flip views, mapped to original pixel coordinates.

    The caller already includes the unflipped base pass and performs merging
    before tracking. Extra views contain people only, preserving vehicle input.
    Ultralytics returns boxes in the input image's original pixel coordinates.
    """
    boxes, scores, classes = [], [], []
    width = frame.shape[1]
    for size in sorted(set(sizes)):
        if size <= 0 or size % 32:
            raise ValueError("TTA sizes must be positive multiples of 32")
        for flip in (False, True):
            if size == base_size and not flip:
                continue
            image = np.ascontiguousarray(frame[:, ::-1]) if flip else frame
            xy, cf, cls = predict(det, image, conf, size, device)
            keep = np.isin(cls, people_ids)
            xy, cf, cls = xy[keep].copy(), cf[keep], cls[keep]
            if flip and len(xy):
                left = width - xy[:, 2].copy()
                xy[:, 2] = width - xy[:, 0]
                xy[:, 0] = left
            boxes.append(xy); scores.append(cf); classes.append(cls)
    if not boxes:
        return np.zeros((0, 4)), np.zeros(0), np.zeros(0, dtype=int)
    return np.concatenate(boxes), np.concatenate(scores), np.concatenate(classes)


def audit_times(truth, duration=900, background_step=30):
    """Sample each labelled encounter at start/middle/end, plus background.

    This is an encounter-selected frame audit, not continuous person recall.
    """
    times = {float(t) for t in range(0, int(duration), background_step)}
    for person in truth:
        for t in (person["s"], (person["s"] + person["e"]) / 2, person["e"]):
            times.add(round(max(0, min(duration - .1, t)), 3))
    return sorted(times)
