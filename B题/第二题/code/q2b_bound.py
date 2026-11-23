# -*- coding: utf-8 -*-
"""Q2(2): reuse-aware certified lower bound on the latest start time.

The delivered 10.355 s schedule is found by structural enumeration plus local
station optimization, so it is not certified.  This script computes a valid
lower bound for the *continuous* station problem by relaxing every timing term
to a provable underestimate:

  * first-task ready: minimise (Euclidean travel + exact point-slew) over the
    whole field, a superset of the alert's feasible region, and subtract a
    0.25 m grid margin; path travel >= Euclidean travel, so this underestimates
    the true ready time;
  * between two tasks of a reused vehicle:
        start(next) >= start(prev) + 5 s observation
                       + (region-to-region distance)/v
                       + elevation slew floors;
  * every alert starts when both assigned vehicles are ready.

For each assignment structure and reuse order the minimal feasible schedule
under these underestimates is the longest path of a DAG; the minimum over all
structures and orders is a certified lower bound LB <= optimum.

Outputs: results/q2b_lower_bound.json
"""
import itertools
import json
import os
import sys

import numpy as np
from scipy.spatial import cKDTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from q2_lib import (TARGETS, TARGET_H, R_MIN_GEO, VEHICLES, SPEED,
                    make_grid, region_masks)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES_DIR = os.path.join(BASE, "results")
ALERTS = ["T1", "T2", "T3"]
OBS = 5.0
GRID = 0.1
COVER = 2.0 * GRID      # conservative covering radius of the 0.1 m samples
FIELD_STEP = 0.25       # field grid for the first-task ready lower bound
FIELD_MARGIN = 0.15     # discretisation margin (s)


def region_clouds():
    """Feasible grid points of each alert's observable region."""
    X, Y = make_grid(GRID)
    clouds = {}
    for a in ALERTS:
        c1, c2, c3, _ = region_masks(X, Y, TARGETS[a], TARGET_H[a], R_MIN_GEO[a])
        m = c1 & c2 & c3
        clouds[a] = np.column_stack([X[m], Y[m]]).astype(float)
    return clouds


def min_dist(points, p):
    return float(np.min(np.hypot(points[:, 0] - p[0], points[:, 1] - p[1])))


def cloud_dist(c1, c2):
    tree = cKDTree(c2)
    d, _ = tree.query(c1, k=1)
    return float(np.min(d))


def longest_path(tasks, r_lb, t_lb):
    """Minimal max start for one structure/order.

    tasks[v] = list of alerts in service order for vehicle v.
    r_lb[(v,a)] = lower bound on v's ready time for its first task.
    t_lb[(a,b)] = lower bound on reset+travel+slew from a to b.
    Returns (T, starts).
    """
    SRC = ("SRC",)
    nodes = [SRC]
    nodes += [("R", v, k) for v in range(5) for k in range(len(tasks[v]))]
    nodes += [("S", a) for a in ALERTS]
    dist = {n: -np.inf for n in nodes}
    dist[SRC] = 0.0
    indeg = {n: 0 for n in nodes}
    adj = {n: [] for n in nodes}

    def add(u, w, wt):
        adj[u].append((w, wt))
        indeg[w] += 1

    for v in range(5):
        if tasks[v]:
            add(SRC, ("R", v, 0), r_lb[(v, tasks[v][0])])
        for k, a in enumerate(tasks[v]):
            add(("R", v, k), ("S", a), 0.0)
            if k + 1 < len(tasks[v]):
                b = tasks[v][k + 1]
                add(("S", a), ("R", v, k + 1), OBS + t_lb[(a, b)])

    from collections import deque
    q = deque([n for n in nodes if indeg[n] == 0])
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for w, _wt in adj[u]:
            indeg[w] -= 1
            if indeg[w] == 0:
                q.append(w)
    if len(order) != len(nodes):
        return np.inf, {a: np.inf for a in ALERTS}
    for u in order:
        if dist[u] == -np.inf:
            continue
        for w, wt in adj[u]:
            cand = dist[u] + wt
            if cand > dist[w]:
                dist[w] = cand
    starts = {a: dist[("S", a)] for a in ALERTS}
    return max(starts.values()), starts


def main():
    clouds = region_clouds()
    with open(os.path.join(RES_DIR, "q2b_results.json"), encoding="utf-8") as f:
        delivered = json.load(f)["optimized"]["objective_s"]

    # Valid lower bound on the gimbal angle (hence slew time) to/from alert a:
    # the region lies inside the field, so the elevation is at least the
    # elevation at the farthest field corner from the target.
    corners = np.array([[0.0, 0.0], [100.0, 0.0], [0.0, 100.0], [100.0, 100.0]])
    slew_lb = {}
    for a in ALERTS:
        tgt = np.asarray(TARGETS[a], float)
        r_max = float(np.max(np.hypot(corners[:, 0] - tgt[0],
                                      corners[:, 1] - tgt[1])))
        el_min = np.degrees(np.arctan((TARGET_H[a] - 2.0) / r_max))
        slew_lb[a] = el_min / 30.0          # s, 30 deg/s
    print("slew lower bounds (s):", {a: round(slew_lb[a], 3) for a in ALERTS})

    # First-task ready lower bound: minimise travel + point-slew over the whole
    # field (a superset of the region), then subtract a discretisation margin.
    xs = np.arange(0.0, 100.0 + 1e-9, FIELD_STEP)
    X, Y = np.meshgrid(xs, xs)
    X, Y = X.ravel(), Y.ravel()
    r_lb = {}
    for a in ALERTS:
        tx, ty = TARGETS[a]
        dz = TARGET_H[a] - 2.0
        d = np.hypot(X - tx, Y - ty)
        az = np.abs(np.degrees(np.arctan2(ty - Y, tx - X)))
        az = np.minimum(az, 360.0 - az)
        el = np.degrees(np.arctan2(dz, np.maximum(d, 1e-9)))
        slew = np.maximum(az, el) / 30.0
        for v in range(5):
            travel = np.hypot(X - VEHICLES[v][0], Y - VEHICLES[v][1]) / SPEED
            r_lb[(v, a)] = max(0.0, float(np.min(travel + slew)) - FIELD_MARGIN)

    t_lb = {(a, b): (max(0.0, cloud_dist(clouds[a], clouds[b]) - 2.0 * COVER)
                     / SPEED + slew_lb[a] + slew_lb[b])
            for a in ALERTS for b in ALERTS if a != b}
    print("ready lower bounds (s):",
          {f"V{v+1}{a}": round(r_lb[(v, a)], 2) for v in range(5) for a in ALERTS})

    best = (np.inf, None, None)
    checked = 0
    # assignment structures: each alert gets an unordered pair of vehicles
    pairs = list(itertools.combinations(range(5), 2))
    for asg in itertools.product(pairs, repeat=3):
        # each vehicle's alert set
        veh_alerts = {v: [] for v in range(5)}
        for a, pr in zip(ALERTS, asg):
            for v in pr:
                veh_alerts[v].append(a)
        # at most 3 tasks per vehicle; enumerate orders per vehicle
        perms = []
        ok = True
        for v in range(5):
            al = veh_alerts[v]
            if len(al) > 3:
                ok = False
                break
            perms.append(list(itertools.permutations(al)))
        if not ok:
            continue
        for combo in itertools.product(*perms):
            tasks = {v: list(combo[v]) for v in range(5)}
            T, starts = longest_path(tasks, r_lb, t_lb)
            checked += 1
            if T < best[0] - 1e-12:
                best = (T, {v: tasks[v] for v in range(5)}, starts)

    LB = best[0]
    out = {
        "objective_delivered_s": float(delivered),
        "lower_bound_s": float(LB),
        "certified_gap_s": float(delivered - LB),
        "certified_gap_pct": float(100.0 * (delivered - LB) / delivered),
        "grid_step_m": GRID,
        "covering_radius_m": COVER,
        "field_step_m": FIELD_STEP,
        "field_margin_s": FIELD_MARGIN,
        "slew_lb_s": {a: float(slew_lb[a]) for a in ALERTS},
        "ready_lb_s": {f"V{v+1}_{a}": float(r_lb[(v, a)])
                       for v in range(5) for a in ALERTS},
        "transition_lb_s": {f"{a}_{b}": float(t_lb[(a, b)])
                            for a in ALERTS for b in ALERTS if a != b},
        "best_structure": best[1],
        "best_starts_s": {a: float(s) for a, s in best[2].items()},
        "structures_orders_checked": checked,
        "note": ("Valid lower bound: the first-task ready time is minimised "
                 "over the whole field (superset of the region) with Euclidean "
                 "travel and exact point-slew, minus a grid margin; transition "
                 "times use region distances and an elevation slew floor."),
    }
    with open(os.path.join(RES_DIR, "q2b_lower_bound.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"delivered {delivered:.3f} s  lower bound {LB:.3f} s  "
          f"gap {delivered-LB:.3f} s ({out['certified_gap_pct']:.1f}%)")
    print("best structure:", best[1])
    print("best starts:", {a: round(s, 3) for a, s in best[2].items()})
    print("checked", checked, "structures/orders")


if __name__ == "__main__":
    main()
