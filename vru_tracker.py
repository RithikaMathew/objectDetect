"""
Association tracker for small vulnerable road users (cyclists, pedestrians).

WHY THIS EXISTS
---------------
The original SimpleIouTracker in pilot_detect.py associated detections between
samples by IoU with a 0.3 threshold. On the BL Colonial 2019-07-10 .008 clip,
a cyclist that YOLO detects in 13 consecutive sampled frames (every one above
conf=0.2, several above 0.9) produced ZERO counted tracks, because only 3 of
the 12 frame-to-frame links cleared IoU >= 0.3. Measured from the logged boxes:

    407.40->407.57  IoU 0.259  FAIL
    407.57->407.74  IoU 0.000  FAIL
    407.74->407.90  IoU 0.287  FAIL
    407.90->408.07  IoU 0.233  FAIL
    408.07->408.24  IoU 0.270  FAIL
    408.24->408.41  IoU 0.311  pass
    408.41->408.57  IoU 0.230  FAIL
    408.57->408.74  IoU 0.238  FAIL
    408.74->408.91  IoU 0.361  pass
    408.91->409.07  IoU 0.274  FAIL
    409.07->409.24  IoU 0.287  FAIL
    409.24->409.41  IoU 0.355  pass

    -> longest surviving track = 2 hits, vs min_track_hits = 6.  Counted: NO.

Two effects compound, and both are specific to small VRUs:

 1. Displacement per sample is large relative to box size. IoU falls off a
    cliff once the shift approaches the box dimension, and for a ~40px-wide
    cyclist at a 5-frame stride it does.
 2. Box geometry is unstable. The detector alternates between boxing the
    bicycle alone and the bicycle+rider, so height swings 114 -> 62 -> 50 px
    across three samples. IoU punishes that even when the object has barely
    moved (see 407.74->407.90: the centroid moves 6.7px, yet IoU is only 0.287).

Cars are immune to both: bigger boxes, stable aspect ratio. Which is exactly
why the original pipeline tracked 85 cars and 0 bicycles on the same clip.

THE FIX
-------
Associate on **velocity-predicted centroid distance, normalized by box size**,
and use IoU only as a tie-breaker in the cost. On the same 12 links, the
normalized centroid gate passes 12/12, yielding one clean 13-hit track.

Also replaces per-detection motion filtering with per-TRACK net displacement.
The per-frame MOG2 filter can drop a real cyclist whenever the foreground mask
happens to be poor on that frame, and it cannot be loosened without letting
static false positives back in. Judging motion at track level is strictly
better: a genuinely static object (the construction-site artifact that was
being misclassified as 'bicycle') has near-zero net displacement over its whole
life, while a cyclist travels many box-widths. One decision per track, made
with all the evidence, instead of a fragile decision per frame.
"""

import numpy as np

try:
    from scipy.optimize import linear_sum_assignment
    _HAVE_SCIPY = True
except ImportError:  # greedy fallback; scipy ships with ultralytics but don't assume
    _HAVE_SCIPY = False


def iou_xyxy(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


# Evidence for a bicycle is worth more than evidence for a person, and the
# asymmetry is not a tuning choice -- it follows from what each error means.
# A cyclist ALWAYS generates person detections (the rider is a person), and the
# rider is the easier of the two to detect, so a confidence-weighted vote
# reliably labels cyclists as pedestrians. The reverse error is rare: a
# confident bicycle box on a pedestrian is a genuine false positive, not an
# expected by-product. So a track carrying solid bicycle evidence anywhere in
# its life is a cyclist, even if person evidence outweighs it overall.
#
# This also fixes a failure that depended on distance: as a cyclist recedes the
# thin bicycle frame becomes undetectable while the rider blob persists, so a
# summed vote flips the label to 'person' partway through the crossing. Judging
# on the per-class MAXIMUM lets the earlier, closer, high-confidence bicycle
# evidence settle the whole track.
CYCLIST_EVIDENCE = ("cyclist", "bicycle")
CYCLIST_DECISIVE_CONF = 0.40


def resolve_class(cls_votes, cls_max):
    """Pick a track's class from its accumulated per-class evidence."""
    best = max(cls_votes.items(), key=lambda kv: kv[1])[0]
    bike_conf = max((cls_max.get(c, 0.0) for c in CYCLIST_EVIDENCE), default=0.0)
    if bike_conf >= CYCLIST_DECISIVE_CONF and best in ("person", "motorcycle", "other_vehicle"):
        return "cyclist"
    if best in CYCLIST_EVIDENCE:
        return "cyclist"
    return best


def centroid(b):
    return ((b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0)


def diagonal(b):
    return float(np.hypot(b[2] - b[0], b[3] - b[1]))


class Track:
    __slots__ = ("id", "bbox", "cls", "hits", "missed", "alive", "vel",
                 "confs", "first_t", "last_t", "start_centroid", "path",
                 "cls_votes", "cls_max")

    def __init__(self, tid, det, t):
        self.id = tid
        self.bbox = list(det[:4])
        self.cls = det[5]
        self.cls_votes = {det[5]: det[4]}
        self.cls_max = {det[5]: det[4]}
        self.hits = 1
        self.missed = 0
        self.alive = True
        self.vel = (0.0, 0.0)          # px per second
        self.confs = [det[4]]
        self.first_t = t
        self.last_t = t
        self.start_centroid = centroid(det[:4])
        # (t, cx, cy, diag) -- timestamp so two tracks can be compared over the
        # window where they coexist, and the box diagonal AT THAT MOMENT so the
        # comparison can be scale-normalized correctly. Storing only the final
        # box size is wrong: a receding cyclist's box shrinks from ~160px to
        # ~29px across two seconds, so normalizing early distances by the final
        # size inflated them ~5x and kept true duplicates apart.
        self.path = [(t, *centroid(det[:4]), diagonal(det[:4]))]

    def predict(self, dt):
        """Where we expect this track's box to be after dt seconds."""
        vx, vy = self.vel
        dx, dy = vx * dt, vy * dt
        return [self.bbox[0] + dx, self.bbox[1] + dy,
                self.bbox[2] + dx, self.bbox[3] + dy]

    def update(self, det, t):
        dt = max(1e-6, t - self.last_t)
        old_c = centroid(self.bbox)
        new_c = centroid(det[:4])
        inst_v = ((new_c[0] - old_c[0]) / dt, (new_c[1] - old_c[1]) / dt)
        # Exponential smoothing: a single jittery box shouldn't throw the
        # velocity estimate, but a real turn should be followed within ~3 samples.
        a = 0.5
        self.vel = (a * inst_v[0] + (1 - a) * self.vel[0],
                    a * inst_v[1] + (1 - a) * self.vel[1])
        self.bbox = list(det[:4])
        self.hits += 1
        self.missed = 0
        self.last_t = t
        self.confs.append(det[4])
        self.path.append((t, *new_c, diagonal(det[:4])))
        self.cls_votes[det[5]] = self.cls_votes.get(det[5], 0.0) + det[4]
        self.cls_max[det[5]] = max(self.cls_max.get(det[5], 0.0), det[4])
        self.cls = resolve_class(self.cls_votes, self.cls_max)

    # ---- track-level evidence, used instead of per-frame thresholds ----

    @property
    def duration(self):
        return self.last_t - self.first_t

    @property
    def max_conf(self):
        return max(self.confs)

    @property
    def mean_conf(self):
        return float(np.mean(self.confs))

    @property
    def net_displacement(self):
        """Straight-line distance from where the track started to where it
        ended, in units of the current box diagonal. A parked car or a static
        misclassified artifact stays near 0 no matter how long it persists."""
        c = centroid(self.bbox)
        d = float(np.hypot(c[0] - self.start_centroid[0], c[1] - self.start_centroid[1]))
        scale = max(1.0, diagonal(self.bbox))
        return d / scale

    @property
    def max_excursion(self):
        """The FARTHEST this track ever got from where it started, in box
        diagonals. Catches an object that moves away and comes back, which net
        displacement alone would score as ~0.

        Deliberately not total path length: a static object's per-frame
        detection jitter accumulates path length linearly with track duration,
        so any long-lived artifact eventually clears a path-length threshold no
        matter how small the jitter (a 60-frame static box jittering +/-1.5px
        scored 2.79 diagonals of "path"). Max excursion stays flat at ~0.06
        for that same track, because it measures distance from the origin
        rather than summing noise."""
        if not self.path:
            return 0.0
        sx, sy = self.start_centroid
        far = max(float(np.hypot(px - sx, py - sy)) for _, px, py, _d in self.path)
        return far / max(1.0, diagonal(self.bbox))


# Merging is allowed only WITHIN a semantic group. The duplicate-box problem is
# one physical object receiving several labels, and those labels always come
# from the same group: a cyclist reads as person / bicycle / cyclist /
# motorcycle; a large vehicle reads as car / truck / bus. A car and a pedestrian
# are never the same object, so permitting that merge can only ever be wrong --
# and it happened in the first real run, inflating junk tracks' hit counts until
# they passed confirmation and dragging their class vote around.
CLASS_GROUPS = {
    "person": "vru", "bicycle": "vru", "cyclist": "vru", "motorcycle": "vru",
    "other_vehicle": "vru",
    "car": "vehicle", "truck": "vehicle", "bus": "vehicle",
}


def class_group(name):
    return CLASS_GROUPS.get(name, name)


def interp_path(path, t):
    """Linearly interpolate (x, y, diag) along a track's path at time t.

    Returns None if t lies outside the path's span.

    Needed because comparing two tracks on exactly-shared timestamps does not
    work for the case that matters most. Assignment is one-to-one, so two
    tracks following the SAME object can never both match a detection on the
    same frame -- their sample times interleave instead of coinciding, and the
    set intersection of their timestamps is near empty. Interpolating one path
    onto the other's times handles interleaved fragments and simultaneous
    duplicates with the same test.
    """
    if not path:
        return None
    if t < path[0][0] or t > path[-1][0]:
        return None
    lo, hi = 0, len(path) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if path[mid][0] <= t:
            lo = mid
        else:
            hi = mid
    t0, x0, y0, d0 = path[lo]
    t1, x1, y1, d1 = path[hi]
    if t1 == t0:
        return (x0, y0, d0)
    f = (t - t0) / (t1 - t0)
    return (x0 + f * (x1 - x0), y0 + f * (y1 - y0), d0 + f * (d1 - d0))


def merge_redundant_tracks(tracks, max_norm_dist=1.2, min_overlap_frac=0.25,
                           same_class_only=False, min_common_points=3,
                           max_succession_gap=1.5, allow_cross_group=False,
                           debug=False):
    """Collapse multiple tracks that are following ONE physical object.

    WHY THIS IS NEEDED
    ------------------
    Fixing the association gate turned "0 cyclists" into "5 cyclists" on a
    window containing exactly ONE. Detection, not association, causes that: at
    conf=0.05 the detector emits several overlapping boxes for the same rider
    in the same frame -- the log shows "2 bicycle box(es)", "3 bicycle box(es)",
    "4 bicycle box(es)" on consecutive frames -- because a cyclist admits
    several defensible boxes (bike only, bike+rider, rider only) that sit at
    IoU well below the 0.5 tile-merge threshold and so survive as distinct
    detections. Each duplicate then seeds its own track, and each track is
    individually plausible, so each passes confirmation.

    The signature is unmistakable: tracks that coexist in time AND stay within
    about one box-diagonal of each other for that whole period. Two real
    cyclists riding that close would be occluding each other continuously.

    Merging is by absorption into the highest-evidence track (most hits), which
    keeps that track's own trajectory rather than averaging two noisy ones.

    same_class_only=False by default because the duplicate boxes frequently
    carry DIFFERENT labels -- the same rider appears as 'bicycle', 'person' and
    'motorcycle' in the same window (the BL Colonial run counted 2 spurious
    motorcycles alongside 5 bicycles for one cyclist). Restricting to matching
    classes would leave exactly those duplicates in place.

    Returns (kept_tracks, n_merged, id_map), where id_map maps an absorbed
    track's id to the id of the track that absorbed it. Callers that recorded
    per-frame detections against the original ids need id_map to re-label those
    detections after merging, otherwise annotations point at ids that no longer
    exist.
    """
    if len(tracks) < 2:
        return list(tracks), 0, {}

    order = sorted(tracks, key=lambda t: (-t.hits, t.first_t))
    absorbed = set()
    id_map = {}
    n_merged = 0

    for i, primary in enumerate(order):
        if id(primary) in absorbed:
            continue
        for other in order[i + 1:]:
            if id(other) in absorbed:
                continue
            if same_class_only and other.cls != primary.cls:
                continue
            if not allow_cross_group and \
                    class_group(other.cls) != class_group(primary.cls):
                continue

            lo = max(primary.first_t, other.first_t)
            hi = min(primary.last_t, other.last_t)

            mean_d, mean_scale, n_cmp, mode = None, 0.0, 0, ""

            if hi > lo:
                # --- OVERLAP: sample the shorter track's own times and
                # interpolate the other onto them. ---
                short, long_ = ((other, primary)
                                if other.duration <= primary.duration
                                else (primary, other))
                ratios, scales = [], []
                for (t, x, y, d) in short.path:
                    if not (lo <= t <= hi):
                        continue
                    o = interp_path(long_.path, t)
                    if o is None:
                        continue
                    scale = max(1.0, d, o[2])
                    ratios.append(float(np.hypot(x - o[0], y - o[1])) / scale)
                    scales.append(scale)
                if len(ratios) >= min_common_points:
                    mean_d = float(np.mean(ratios))
                    mean_scale = float(np.mean(scales))
                    n_cmp = len(ratios)
                    span = min(primary.duration, other.duration)
                    frac = (hi - lo) / span if span > 0 else 1.0
                    mode = f"overlap {hi-lo:.2f}s ({frac:.0%})"
                    if frac < min_overlap_frac:
                        mean_d = None

            if mean_d is None:
                # --- SUCCESSION: one fragment ends, the other begins. The
                # coasting track's constant-velocity extrapolation is checked
                # against where the new fragment actually starts. This is how a
                # single object broken across a detection gap gets rejoined --
                # the overlap test cannot see it, because there is no overlap.
                earlier, later = ((primary, other)
                                  if primary.last_t <= other.last_t
                                  else (other, primary))
                gap = later.first_t - earlier.last_t
                if -max_succession_gap <= gap <= max_succession_gap:
                    ex, ey = earlier.path[-1][1], earlier.path[-1][2]
                    ed = earlier.path[-1][3]
                    vx, vy = earlier.vel
                    px, py = ex + vx * max(0.0, gap), ey + vy * max(0.0, gap)
                    lx, ly, ld = later.path[0][1], later.path[0][2], later.path[0][3]
                    scale = max(1.0, ed, ld)
                    mean_d = float(np.hypot(px - lx, py - ly)) / scale
                    mean_scale = scale
                    n_cmp = 1
                    mode = f"succession gap={gap:+.2f}s"

            if mean_d is None:
                continue

            if debug:
                print(f"    merge? #{primary.id}({primary.cls},h={primary.hits}) "
                      f"vs #{other.id}({other.cls},h={other.hits}): "
                      f"{mode} n={n_cmp} scale~{mean_scale:.0f}px "
                      f"norm_dist={mean_d:.2f} "
                      f"-> {'MERGE' if mean_d <= max_norm_dist else 'keep separate'}")
            if mean_d <= max_norm_dist:
                absorbed.add(id(other))
                id_map[other.id] = primary.id
                # Anything already folded into `other` now belongs to `primary`
                for k, v in list(id_map.items()):
                    if v == other.id:
                        id_map[k] = primary.id
                n_merged += 1
                primary.hits += other.hits
                primary.confs.extend(other.confs)
                for c, w in other.cls_votes.items():
                    primary.cls_votes[c] = primary.cls_votes.get(c, 0.0) + w
                for c, mx in other.cls_max.items():
                    primary.cls_max[c] = max(primary.cls_max.get(c, 0.0), mx)
                primary.cls = resolve_class(primary.cls_votes, primary.cls_max)
                primary.first_t = min(primary.first_t, other.first_t)
                primary.last_t = max(primary.last_t, other.last_t)

    return [t for t in order if id(t) not in absorbed], n_merged, id_map


class VruTracker:
    """Associates by velocity-predicted, size-normalized centroid distance.

    max_center_dist_frac: a detection may be matched to a track if the distance
        between the detection centroid and the track's PREDICTED centroid is
        below this fraction of the mean box diagonal. 1.0 means "within about
        one object-length of where we expected it," which passed 12/12 links on
        the BL Colonial cyclist where IoU@0.3 passed 3/12.
    """

    def __init__(self, max_center_dist_frac=1.0, iou_weight=0.3, max_missed=4,
                 coast_seconds=None, dt=None):
        """coast_seconds: how long a track may survive with no matching
        detection before being retired. Prefer this over max_missed.

        max_missed counts SAMPLES, which makes the real behaviour depend on the
        frame stride: 4 missed samples is 0.13s at stride=1/30fps but 0.67s at
        stride=5. The 0.13s version retires a track after a 4-frame gap, so a
        distant cyclist whose detections flicker (conf 0.07-0.11 once it is far
        from the camera) gets dropped while still plainly visible in frame.
        Expressing the limit in seconds makes it stride-independent, and
        velocity prediction means a coasting track is still being extrapolated
        to roughly the right place when detections resume.
        """
        if coast_seconds is not None and dt:
            max_missed = max(2, int(round(coast_seconds / dt)))
        self.next_id = 1
        self.tracks = {}
        self.max_center_dist_frac = max_center_dist_frac
        self.iou_weight = iou_weight
        self.max_missed = max_missed

    def _cost(self, track, det, t, dt):
        """Lower is better. Returns None if the pair is outside the gate.

        Extrapolates from the track's OWN last match to now (t - last_t), not
        by one fixed sample step. Those differ precisely when a track is
        coasting: a track unmatched for 20 samples predicted only one step
        ahead sits 19 steps behind where the object actually is, so the
        reacquiring detection falls outside the gate and coasting can never
        succeed. Allowing a longer coast without this is pointless -- the track
        survives but can no longer match anything.
        """
        dt_eff = max(dt, t - track.last_t)
        pred = track.predict(dt_eff)
        pc, dc = centroid(pred), centroid(det[:4])
        dist = float(np.hypot(pc[0] - dc[0], pc[1] - dc[1]))
        scale = max(1.0, (diagonal(pred) + diagonal(det[:4])) / 2.0)
        norm = dist / scale
        # Widen the gate in proportion to how long this track has been coasting.
        # A constant-velocity prediction degrades over a gap (the object may
        # slow, turn, or be partly occluded), so holding a coasting track to the
        # same tolerance as a freshly-matched one guarantees it never reacquires.
        # Capped so a long-dead track cannot hoover up unrelated detections.
        gap_factor = min(2.5, max(1.0, dt_eff / dt)) if dt else 1.0
        if norm > self.max_center_dist_frac * gap_factor:
            return None
        # IoU only refines the ranking among candidates that already passed the
        # distance gate -- it never rejects on its own, which is the whole point.
        return norm - self.iou_weight * iou_xyxy(pred, det[:4])

    def update(self, detections, t, dt):
        active = [tid for tid, tr in self.tracks.items() if tr.alive]
        drawn = []

        if active and detections:
            C = np.full((len(active), len(detections)), np.inf)
            for i, tid in enumerate(active):
                for j, det in enumerate(detections):
                    c = self._cost(self.tracks[tid], det, t, dt)
                    if c is not None:
                        C[i, j] = c

            pairs = []
            if _HAVE_SCIPY:
                big = 1e6
                rows, cols = linear_sum_assignment(np.where(np.isinf(C), big, C))
                pairs = [(r, c) for r, c in zip(rows, cols) if np.isfinite(C[r, c])]
            else:
                order = sorted(((C[i, j], i, j)
                                for i in range(len(active)) for j in range(len(detections))
                                if np.isfinite(C[i, j])))
                used_i, used_j = set(), set()
                for _, i, j in order:
                    if i in used_i or j in used_j:
                        continue
                    used_i.add(i)
                    used_j.add(j)
                    pairs.append((i, j))

            matched_t, matched_d = set(), set()
            for i, j in pairs:
                tid = active[i]
                self.tracks[tid].update(detections[j], t)
                matched_t.add(tid)
                matched_d.add(j)
                drawn.append((tid, *detections[j][:4], self.tracks[tid].cls, detections[j][4]))
        else:
            matched_t, matched_d = set(), set()

        for tid in active:
            if tid not in matched_t:
                self.tracks[tid].missed += 1
                if self.tracks[tid].missed > self.max_missed:
                    self.tracks[tid].alive = False

        for j, det in enumerate(detections):
            if j not in matched_d:
                tid = self.next_id
                self.next_id += 1
                self.tracks[tid] = Track(tid, det, t)
                drawn.append((tid, *det[:4], det[5], det[4]))

        return drawn

    def confirmed(self, min_hits, min_max_conf, min_net_disp):
        """Tracks that survive track-level evidence tests.

        Returns (confirmed_tracks, reject_reason_counts). Detection ran at a
        deliberately low confidence; the real decision is made HERE, with the
        whole track in hand, rather than per frame. A cyclist whose confidence
        dips to 0.09 on one frame is still obviously a cyclist if 12 other
        frames agree and it crossed the scene.
        """
        keep, reasons = [], {}
        for tr in self.tracks.values():
            if tr.hits < min_hits:
                reasons["too_few_hits"] = reasons.get("too_few_hits", 0) + 1
            elif tr.max_conf < min_max_conf:
                reasons["low_confidence"] = reasons.get("low_confidence", 0) + 1
            elif tr.max_excursion < min_net_disp:
                reasons["static_object"] = reasons.get("static_object", 0) + 1
            else:
                keep.append(tr)
        return keep, reasons
