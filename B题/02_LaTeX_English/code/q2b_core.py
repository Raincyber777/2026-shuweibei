# -*- coding: utf-8 -*-
"""Problem 2(2) computational core: 6 task slots, 5 vehicles, reuse.

Model
-----
* decision = (assignment alert->vehicle pair, per-vehicle task order, stations)
* timing: travel d/3 -> slew max(|az|,el)/30 -> sync obs start = max(ready of
  both vehicles) -> 5 s obs -> reset max(|az|,el)/30 -> depart
* objective: min over schemes of max_a(observation start time of alert a)
* lower bound (certificate): for each alert a, r(v,a) = min over feasible
  stations of [dist(V_v,p)/3 + slew(p)] is the earliest possible ready of v
  for a; the alert start is at least the 2nd-smallest r(v,a) (two distinct
  vehicles needed, reuse only delays) -> LB = max_a r_(2)(v,a). If the best
  found scheme attains LB it is globally optimal.
* deadlock: mutual waiting cycles between two reused vehicles make a
  (combo, order) infeasible; detected during simulation.

Baseline heuristic (independently defined "nearest-assignment"):
  alerts in index order; each alert's two slots filled one at a time by the
  vehicle (not already on that alert) with the smallest marginal travel time
  to its ready-minimizing feasible station for this alert, counting the
  vehicle's committed chain position; ties by lower vehicle index.

Outputs: results/q2b_results.json, q2b_summary.txt, q2b_data.npz
"""
import itertools
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from q2_lib import (BUILDINGS, FIELD, OMEGA, R_VEH, H_CAM, SPEED,
                    TARGETS, TARGET_H, R_MIN_GEO, ALERTS, VEHICLES,
                    dist_to_rect, los_blocked_h, region_masks, make_grid,
                    wrap180, slew_time, pointing_angles, nelder_mead,
                    travel_time)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES_DIR = os.path.join(BASE, "results")
FIG_DIR = os.path.join(BASE, "figures")
os.makedirs(RES_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

ALERT_KEYS = ["T1", "T2", "T3"]
OBS_LEN = 5.0
SUB_TARGET = 15000          # approx size of the subsampled candidate cloud


def c1_margin(px, py):
    m = np.minimum(px - R_VEH, py - R_VEH)
    m = np.minimum(m, FIELD - R_VEH - px)
    m = np.minimum(m, FIELD - R_VEH - py)
    for b in BUILDINGS:
        m = np.minimum(m, dist_to_rect(px, py, b) - R_VEH)
    return m


def feasible_scalar(x, y, a_key):
    """Exact feasibility test of one station for alert a_key."""
    if not (R_VEH <= x <= FIELD - R_VEH and R_VEH <= y <= FIELD - R_VEH):
        return False
    for b in BUILDINGS:
        if dist_to_rect(np.array([x]), np.array([y]), b)[0] < R_VEH - 1e-9:
            return False
    d = np.hypot(x - TARGETS[a_key][0], y - TARGETS[a_key][1])
    if d < R_MIN_GEO[a_key] - 1e-9:
        return False
    if los_blocked_h(np.array([x]), np.array([y]), TARGETS[a_key],
                     TARGET_H[a_key])[0]:
        return False
    return True


# ---------------------------------------------------------- 1) feasible sets
print("building regions ...")
FEAS = {}
for a in ALERT_KEYS:
    X, Y = make_grid(0.1)
    c1, c2, c3, r = region_masks(X, Y, TARGETS[a], TARGET_H[a], R_MIN_GEO[a])
    m = c1 & c2 & c3
    pts = np.column_stack([X[m], Y[m]]).astype(np.float64)
    n = len(pts)
    stride = max(1, int(round(n / SUB_TARGET)))
    sub = pts[::stride]
    dx = TARGETS[a][0] - sub[:, 0]
    dy = TARGETS[a][1] - sub[:, 1]
    rr = np.hypot(dx, dy)
    az = wrap180(np.degrees(np.arctan2(dy, dx)))
    el = np.degrees(np.arctan((TARGET_H[a] - H_CAM) / np.maximum(rr, 1e-12)))
    sl = np.maximum(np.abs(az), el) / OMEGA
    FEAS[a] = {"pts": pts, "sub": sub, "az": az, "el": el, "slew": sl,
               "area": float(m.sum()) * 0.01}
# official (midpoint) areas, reported alongside the node-count values
for a in ALERT_KEYS:
    Xm2, Ym2 = make_grid(0.1, center=True)
    c1m2, c2m2, c3m2, _ = region_masks(Xm2, Ym2, TARGETS[a], TARGET_H[a],
                                       R_MIN_GEO[a])
    FEAS[a]["area_mid"] = float((c1m2 & c2m2 & c3m2).sum()) * 0.01
    print(f"  {a}: area_mid={FEAS[a]['area_mid']:.1f} m^2 "
          f"(node {FEAS[a]['area']:.1f})")
    print(f"  {a}: area={FEAS[a]['area']:.1f} m^2  full={n}  sub={len(sub)}")

# -------------------------------------- 2) earliest-ready values r(v, a)
print("per-vehicle earliest-ready (obstacle-aware travel) ...")
R_VA = {}          # (v,a) -> earliest ready (full feasible set)
ARG_VA = {}        # (v,a) -> argmin station
for v in range(5):
    for a in ALERT_KEYS:
        pts = FEAS[a]["pts"]
        d = np.hypot(pts[:, 0] - VEHICLES[v, 0], pts[:, 1] - VEHICLES[v, 1])
        dxa = TARGETS[a][0] - pts[:, 0]
        dya = TARGETS[a][1] - pts[:, 1]
        rr = np.hypot(dxa, dya)
        azf = wrap180(np.degrees(np.arctan2(dya, dxa)))
        elf = np.degrees(np.arctan((TARGET_H[a] - H_CAM) / np.maximum(rr, 1e-12)))
        slf = np.maximum(np.abs(azf), elf) / OMEGA
        ready_lb = d / SPEED + slf          # straight-line LOWER bound
        # exact minimum with obstacle-aware travel: walk candidates in
        # straight-LB order until the LB exceeds the best path-based value
        order = np.argsort(ready_lb)[:20000]
        best_v, best_p = np.inf, None
        for k in order:
            if ready_lb[k] >= best_v:
                break
            tp = travel_time(VEHICLES[v], pts[k])
            rv = tp + slf[k]
            if rv < best_v:
                best_v, best_p = rv, pts[k]
        R_VA[(v, a)] = float(best_v)
        ARG_VA[(v, a)] = (float(best_p[0]), float(best_p[1]))
rmat = np.array([[R_VA[(v, a)] for a in ALERT_KEYS] for v in range(5)])
LB_alert = [float(np.sort(rmat[:, j])[1]) for j in range(3)]
LB_global = float(max(LB_alert))
print("r(v,a) table (rows V1..V5, cols T1,T2,T3):")
print(np.round(rmat, 3))
print("per-alert LB (2nd smallest):", np.round(LB_alert, 3), " LB_global:", LB_global)

# ---------------------------------------------------------- 3) simulator
def station_times(p, a):
    az, el, r = pointing_angles(p, TARGETS[a], TARGET_H[a])
    return az, el, slew_time(az, el)


def simulate(assignment, orders, stations):
    """Evaluate one scheme.

    Returns (obj, alert_starts, ready_dict, feasible). Event timelines are
    built afterwards with gantt_segments() once the schedule is fixed.
    Fixed-point iteration over vehicle chains; a mutual-waiting cycle is
    reported infeasible (deadlock).
    """
    ready = {}        # (v, a) -> ready time
    alert_start = {}
    chain_ready = {v: 0.0 for v in range(5)}
    chain_pos = {v: tuple(VEHICLES[v]) for v in range(5)}
    done = {v: 0 for v in range(5)}
    total = sum(len(orders.get(v, [])) for v in range(5))
    rounds = 0
    while sum(done.values()) < total and rounds < 12:
        rounds += 1
        progress = False
        for v in range(5):
            t_free = chain_ready[v]
            pos = chain_pos[v]
            walked = []
            for a in orders.get(v, [])[done[v]:]:
                st = stations.get((v, a))
                if st is None:
                    return (np.inf, None, None, False)
                az, el, sl = station_times(st, a)
                travel = travel_time(pos, st)
                rd = t_free + travel + sl
                ready[(v, a)] = rd              # own ready is final already
                v2 = assignment[a][0] if assignment[a][1] == v else assignment[a][1]
                if (v2, a) in ready:
                    start = max(rd, ready[(v2, a)])
                else:
                    break                       # start needs partner -> stop
                alert_start[a] = start
                t_free = start + OBS_LEN + sl
                pos = st
                walked.append(a)
            if walked:
                done[v] += len(walked)
                chain_ready[v] = t_free
                chain_pos[v] = pos
                progress = True
        if not progress:
            return (np.inf, None, None, False)      # deadlock
    if sum(done.values()) < total or len(alert_start) < 3:
        return (np.inf, None, None, False)
    obj = max(alert_start.values())
    return (obj, alert_start, ready, True)


# --------------------------------------------- 4) enumeration + optimization
def chain_station_candidates(v, a, pos, k=40):
    d = np.hypot(FEAS[a]["sub"][:, 0] - pos[0], FEAS[a]["sub"][:, 1] - pos[1])
    ready = d / SPEED + FEAS[a]["slew"]
    idx = np.argsort(ready)[:k]
    return FEAS[a]["sub"][idx], ready[idx]


def optimize_combo(assignment, orders, incumbent_obj=np.inf):
    """Station optimization for one (assignment, orders).

    Greedy init + Gauss-Seidel coordinate descent over the doubled vehicles:
    for each such vehicle the first two chain stations are re-chosen by a
    (p1 x p2) candidate enumeration while the partners' ready times are held
    at their current-schedule values (then the schedule is re-simulated).
    Returns (obj, stations, starts, ready) of the best scheme found.
    """
    stations = {}
    chain_pos = {v: tuple(VEHICLES[v]) for v in range(5)}
    for v in range(5):
        pos = chain_pos[v]
        for a in orders.get(v, []):
            d = np.hypot(FEAS[a]["sub"][:, 0] - pos[0],
                         FEAS[a]["sub"][:, 1] - pos[1])
            ready = d / SPEED + FEAS[a]["slew"]
            k = int(np.argmin(ready))
            stations[(v, a)] = tuple(FEAS[a]["sub"][k])
            pos = stations[(v, a)]
    obj, starts, ready_cur, ok = simulate(assignment, orders, stations)
    if not ok:
        return (np.inf, None, None, None)
    best = (obj, dict(stations), starts, ready_cur)
    if obj >= incumbent_obj:
        return best
    dbl = [v for v in range(5) if len(orders.get(v, [])) == 2]
    for _sweep in range(4):
        improved = False
        for v in dbl:
            a1, a2 = orders[v]
            ready_cur = best[3]
            pr1 = ready_cur.get((partner_of(assignment, v, a1), a1), np.inf)
            pr2 = ready_cur.get((partner_of(assignment, v, a2), a2), np.inf)
            c1, _ = chain_station_candidates(v, a1, tuple(VEHICLES[v]), 30)
            best_local = (best[0], None, None)
            for i in range(len(c1)):
                p1 = tuple(c1[i])
                sl1 = station_times(p1, a1)[2]
                rd1 = (np.hypot(p1[0] - VEHICLES[v, 0], p1[1] - VEHICLES[v, 1])
                       / SPEED) + sl1
                start1 = max(rd1, pr1)
                depart1 = start1 + OBS_LEN + sl1
                c2, _ = chain_station_candidates(v, a2, p1, 60)
                _, _, sl2 = station_times_from_array(c2, a2)
                rd2 = depart1 + np.hypot(c2[:, 0] - p1[0], c2[:, 1] - p1[1]) \
                    / SPEED + sl2
                start2 = np.maximum(rd2, pr2)
                obj_arr = np.maximum(np.full(len(c2), start1), start2)
                kk = int(np.argmin(obj_arr))
                if obj_arr[kk] < best_local[0] - 1e-9:
                    best_local = (float(obj_arr[kk]), p1, tuple(c2[kk]))
            if best_local[1] is not None:
                stations[(v, a1)], stations[(v, a2)] = best_local[1], best_local[2]
                obj2, starts2, ready2, ok2 = simulate(assignment, orders, stations)
                if ok2 and obj2 < best[0] - 1e-9:
                    best = (obj2, dict(stations), starts2, ready2)
                    improved = True
                else:
                    stations = dict(best[1])
        if not improved:
            break
    return best


def partner_of(assignment, v, a):
    v2 = assignment[a][0] if assignment[a][1] == v else assignment[a][1]
    return v2


def station_times_from_array(pts, a):
    dx = TARGETS[a][0] - pts[:, 0]
    dy = TARGETS[a][1] - pts[:, 1]
    rr = np.hypot(dx, dy)
    az = wrap180(np.degrees(np.arctan2(dy, dx)))
    el = np.degrees(np.arctan((TARGET_H[a] - H_CAM) / np.maximum(rr, 1e-12)))
    return az, el, np.maximum(np.abs(az), el) / OMEGA


# enumeration of assignment combos
combos = []
for pa in itertools.combinations(range(5), 2):
    for pb in itertools.combinations(range(5), 2):
        for pc in itertools.combinations(range(5), 2):
            assignment = {ALERT_KEYS[0]: pa, ALERT_KEYS[1]: pb,
                          ALERT_KEYS[2]: pc}
            # optimistic estimate: max over alerts of the two members' r(v,a)
            est = 0.0
            for j, a in enumerate(ALERT_KEYS):
                vs = assignment[a]
                est = max(est, max(R_VA[(vs[0], a)], R_VA[(vs[1], a)]))
            # vehicle task multisets and orders
            tasks = {v: [a for a in ALERT_KEYS if v in assignment[a]]
                     for v in range(5)}
            orders_list = []
            dbl = [v for v in range(5) if len(tasks[v]) > 1]
            if not dbl:
                orders_list.append({v: tasks[v] for v in range(5)})
            else:
                for perm_set in itertools.product(
                        *[list(itertools.permutations(tasks[v])) for v in dbl]):
                    od = {v: tasks[v] for v in range(5)}
                    for v, p in zip(dbl, perm_set):
                        od[v] = list(p)
                    orders_list.append(od)
            combos.append((est, assignment, orders_list))
combos.sort(key=lambda t: t[0])
print("combos:", len(combos), " est range:",
      round(combos[0][0], 2), "-", round(combos[-1][0], 2))

best_scheme = (np.inf, None, None, None, None)
n_eval = 0
evaluated = []
for est, assignment, orders_list in combos:
    if est >= best_scheme[0] - 1e-9:
        break                     # bound: no combo can beat the incumbent
    for orders in orders_list:
        obj, stations, starts, ready_b = optimize_combo(assignment, orders,
                                                        best_scheme[0])
        n_eval += 1
        if np.isfinite(obj):
            evaluated.append((obj, assignment, orders, stations))
            if obj < best_scheme[0] - 1e-9:
                best_scheme = (obj, assignment, orders, stations, starts)
print("evaluated (combo,order) pairs:", n_eval)
print("best objective before polish:", best_scheme[0], " LB:", LB_global)

# ---- continuous NM polish of every station against the GLOBAL objective ----
obj0, assignment, orders, stations, starts = best_scheme
for _sweep in range(2):
    improved = False
    for v in range(5):
        for a in orders.get(v, []):
            cur = np.array(stations[(v, a)], float)

            def fpol(p, v=v, a=a):
                if not feasible_scalar(p[0], p[1], a):
                    return 1e4 + np.hypot(p[0] - cur[0], p[1] - cur[1])
                st2 = dict(stations)
                st2[(v, a)] = (float(p[0]), float(p[1]))
                o2, _s2, _r2, ok2 = simulate(assignment, orders, st2)
                return o2 if ok2 else 1e4 + np.hypot(p[0] - cur[0], p[1] - cur[1])

            px, pf = nelder_mead(fpol, cur, step=0.8, tol=1e-4, max_iter=160)
            if pf < obj0 - 1e-6 and feasible_scalar(px[0], px[1], a):
                stations[(v, a)] = (float(px[0]), float(px[1]))
                obj0, starts, ready_p, okp = simulate(assignment, orders, stations)
                improved = True
    if not improved:
        break
best_scheme = (obj0, assignment, orders, stations, starts)
print("best objective after NM polish:", obj0, " LB:", LB_global,
      " certified:", abs(obj0 - LB_global) < 1e-6)

# ---- re-polish the best 12 structures (strengthens the optimality claim) ----
evaluated.sort(key=lambda t: t[0])
top_polished = []
for obj_e, asg_e, ord_e, stn_e in evaluated[:12]:
    st_e = dict(stn_e)
    ob_e = obj_e
    for _s in range(2):
        imp = False
        for v in range(5):
            for a in ord_e.get(v, []):
                cur = np.array(st_e[(v, a)], float)

                def fpol(p, v=v, a=a, cur=cur, st_e=st_e):
                    if not feasible_scalar(p[0], p[1], a):
                        return 1e4 + np.hypot(p[0] - cur[0], p[1] - cur[1])
                    s2 = dict(st_e)
                    s2[(v, a)] = (float(p[0]), float(p[1]))
                    o2, _s2, _r2, ok2 = simulate(asg_e, ord_e, s2)
                    return o2 if ok2 else 1e4 + np.hypot(p[0] - cur[0],
                                                         p[1] - cur[1])

                px, pf = nelder_mead(fpol, cur, step=0.8, tol=1e-4,
                                     max_iter=160)
                if pf < ob_e - 1e-6 and feasible_scalar(px[0], px[1], a):
                    st_e[(v, a)] = (float(px[0]), float(px[1]))
                    ob_e, _st2, _rd2, ok2 = simulate(asg_e, ord_e, st_e)
                    imp = True
        if not imp:
            break
    top_polished.append((ob_e, asg_e, ord_e, st_e))
top_full = []
for t in top_polished:
    o2, s2, _r2, ok2 = simulate(t[1], t[2], t[3])
    if ok2:
        top_full.append((o2, sum(s2.values()), t[1], t[2], t[3], s2))
top_full.sort(key=lambda t: (round(t[0], 6), round(t[1], 6)))
best_key = (best_scheme[0], sum(best_scheme[4].values()))
if top_full and (top_full[0][0], top_full[0][1]) < best_key:
    o0, ssum0, asg0, od0, stn0, st0 = top_full[0]
    best_scheme = (o0, asg0, od0, stn0, st0)
top5 = [{"obj_s": round(t[0], 3), "sum_starts_s": round(t[1], 3),
         "starts": {a: round(t[5][a], 3) for a in ALERT_KEYS},
         "assignment": {a: [t[2][a][0] + 1, t[2][a][1] + 1] for a in ALERT_KEYS},
         "orders": {f"V{v+1}": t[3].get(v, []) for v in range(5)}}
        for t in top_full[:5]]
print("top-5 structures after polish:", json.dumps(top5))

# ---- knife-edge disclosure + robust variant (LOS clearance >= 0.5 m) -------
def los_clearance(px, py, a):
    """Min clearance of the LOS from station (px,py) to alert a over roofs (m)."""
    tgt, h = TARGETS[a], TARGET_H[a]
    t = np.linspace(0.0, 1.0, 4001)
    sx = px + (tgt[0] - px) * t
    sy = py + (tgt[1] - py) * t
    sz = H_CAM + (h - H_CAM) * t
    best = np.inf
    for (bx0, bx1, by0, by1, bh) in BUILDINGS:
        over = (sx >= bx0) & (sx <= bx1) & (sy >= by0) & (sy <= by1)
        if over.any():
            best = min(best, float(sz[over].min()) - bh)
        else:
            dx = np.maximum(np.maximum(bx0 - sx, sx - bx1), 0.0)
            dy = np.maximum(np.maximum(by0 - sy, sy - by1), 0.0)
            dz = np.maximum(np.maximum(0.0 - sz, sz - bh), 0.0)
            best = min(best, float(np.min(np.sqrt(dx * dx + dy * dy + dz * dz))))
    return best

knife = {f"V{v+1}": {a: round(los_clearance(*stations[(v, a)], a), 6)
                     for a in orders.get(v, [])} for v in range(5)}
min_knife = min(min(d.values()) for d in knife.values())
print("station LOS clearances:", knife, " min:", min_knife)

MARGIN = 0.5
robust_best = None
for ob_e, asg_e, ord_e, st_e in top_polished[:8]:
    st_r = dict(st_e)
    ob_r = ob_e

    def feas_m(x, y, a):
        return feasible_scalar(x, y, a) and \
            los_clearance(x, y, a) >= MARGIN - 1e-9

    for _s in range(3):
        imp = False
        _o2, _s2, ready2, ok2 = simulate(asg_e, ord_e, st_r)
        if not ok2:
            break
        for v in range(5):
            for a in ord_e.get(v, []):
                cur = np.array(st_r[(v, a)], float)

                def rob_obj(p, v=v, a=a, cur=cur, st_r=st_r):
                    if not feas_m(p[0], p[1], a):
                        return 1e4 + np.hypot(p[0] - cur[0], p[1] - cur[1])
                    s2 = dict(st_r)
                    s2[(v, a)] = (float(p[0]), float(p[1]))
                    o2, _s3, _r3, ok3 = simulate(asg_e, ord_e, s2)
                    return o2 if ok3 else 1e4

                px, pf = nelder_mead(rob_obj, cur, step=0.6, tol=1e-4,
                                     max_iter=160)
                if pf < ob_r - 1e-9 and feas_m(px[0], px[1], a):
                    st_r[(v, a)] = (float(px[0]), float(px[1]))
                    ob_r, _s4, _r4, ok4 = simulate(asg_e, ord_e, st_r)
                    imp = True
        if not imp:
            break
    if ok2 or True:
        clr = {f"V{v+1}": {a: round(los_clearance(*st_r[(v, a)], a), 4)
                           for a in ord_e.get(v, [])} for v in range(5)}
        ok_final = all(c >= MARGIN - 1e-9 for d in clr.values()
                       for c in d.values())
        if ok_final and (robust_best is None or ob_r < robust_best[0]):
            robust_best = (ob_r, asg_e, ord_e, st_r, clr)
if robust_best is not None:
    ob_rb, asg_rb, ord_rb, st_rb, clr_rb = robust_best
    obj_rb, starts_rb, _rd, ok_rb = simulate(asg_rb, ord_rb, st_rb)
    robust = {"margin_m": MARGIN, "obj_s": float(obj_rb),
              "starts": {a: round(v, 3) for a, v in starts_rb.items()},
              "clearances": clr_rb,
              "assignment": {a: [v + 1 for v in asg_rb[a]]
                             for a in ("T1", "T2", "T3")},
              "orders": {f"V{v+1}": ord_rb.get(v, []) for v in range(5)},
              "stations": {f"V{v+1}": {a: [round(x, 4) for x in st_rb[(v, a)]]
                                       for a in ord_rb.get(v, [])}
                           for v in range(5)}}
    print(f"robust (LOS >= {MARGIN} m): obj = {obj_rb:.3f} s  starts "
          f"{ {a: round(v,3) for a,v in starts_rb.items()} }")
else:
    robust = {"margin_m": MARGIN, "obj_s": None}
    print("robust variant: no margin-feasible scheme found in top structures")

# ------------------------------------------ 5) nearest-assignment heuristic
def nearest_assignment_baseline():
    stations = {}
    orders = {v: [] for v in range(5)}
    assigned_to = {a: [] for a in ALERT_KEYS}
    # committed chain state
    chain_pos = {v: tuple(VEHICLES[v]) for v in range(5)}
    chain_end_time = {v: 0.0 for v in range(5)}
    alert_start = {}
    for a in ALERT_KEYS:
        for slot in range(2):
            best = (np.inf, None, None)
            for v in range(5):
                if v in assigned_to[a]:
                    continue
                pos = chain_pos[v]
                d = np.hypot(FEAS[a]["sub"][:, 0] - pos[0],
                             FEAS[a]["sub"][:, 1] - pos[1])
                travel_arr = d / SPEED
                k = int(np.argmin(travel_arr))
                st = tuple(FEAS[a]["sub"][k])
                marg = float(travel_arr[k])       # marginal travel (nearest)
                if marg < best[0]:
                    best = (marg, v, st)
            _, v, st = best
            assigned_to[a].append(v)
            orders[v].append(a)
            stations[(v, a)] = st
            az, el, sl = station_times(st, a)
            travel = np.hypot(st[0] - chain_pos[v][0], st[1] - chain_pos[v][1]) / SPEED
            arrive = chain_end_time[v] + travel
            rd = arrive + sl
            if len(assigned_to[a]) == 2:
                partner = [u for u in assigned_to[a] if u != v][0]
                # partner ready already committed
                pr = partner_ready_committed(partner, a, stations, orders,
                                             assignment_of(assigned_to))
                start = max(rd, pr)
            else:
                start = rd          # provisional; fixed when partner arrives
            alert_start[a] = start
            chain_pos[v] = st
            chain_end_time[v] = start + OBS_LEN + sl
    return orders, stations


def assignment_of(assigned_to):
    return {a: tuple(vs) for a, vs in assigned_to.items()}


def partner_ready_committed(v, a, stations, orders, asg):
    t_free = 0.0
    pos = tuple(VEHICLES[v])
    for a2 in orders[v]:
        st = stations[(v, a2)]
        az, el, sl = station_times(st, a2)
        travel = np.hypot(st[0] - pos[0], st[1] - pos[1]) / SPEED
        arrive = t_free + travel
        rd = arrive + sl
        v2 = asg[a2][0] if asg[a2][1] == v else asg[a2][1]
        if a2 == a:
            return rd
        # previous alert start needs ITS partner; both committed earlier
        pr = partner_ready_committed(v2, a2, stations, orders, asg)
        start = max(rd, pr)
        t_free = start + OBS_LEN + sl
        pos = st
    return rd


h_orders, h_stations = nearest_assignment_baseline()
h_asg = {a: tuple(v for v in range(5) if (v, a) in h_stations and
                  (h_stations[(v, a)] is not None)) for a in ALERT_KEYS}
# rebuild assignment from orders (order of alerts each vehicle serves)
h_assignment = {}
for a in ALERT_KEYS:
    vs = [v for v in range(5) if a in h_orders[v]]
    h_assignment[a] = tuple(vs)
h_obj, h_starts, h_ready, h_ok = simulate(h_assignment, h_orders, h_stations)
print("heuristic:", h_assignment, "orders", h_orders, "obj", h_obj)

# ------------------------------------------------- 6) optimized scheme detail
obj, assignment, orders, stations, starts = best_scheme
detail = {"objective_s": obj, "LB_s": LB_global, "certified_optimal":
          bool(abs(obj - LB_global) < 1e-6), "assignment": {a: [v + 1 for v in assignment[a]] for a in ALERT_KEYS},  # 1-based
          "orders": {f"V{v+1}": orders.get(v, []) for v in range(5)},
          "stations": {f"V{v+1}": {a: list(stations[(v, a)]) for a in orders.get(v, [])}
                       for v in range(5)},
          "alert_starts": {a: starts[a] for a in ALERT_KEYS}}
print(json.dumps(detail, indent=1, default=str))

# per-vehicle Gantt segments for both schemes
def gantt_segments(assignment, orders, stations, starts):
    segs = {v: [] for v in range(5)}
    for v in range(5):
        t_free = 0.0
        pos = tuple(VEHICLES[v])
        for a in orders.get(v, []):
            st = stations[(v, a)]
            az, el, sl = station_times(st, a)
            travel = travel_time(pos, st)
            arrive = t_free + travel
            rd = arrive + sl
            v2 = assignment[a][0] if assignment[a][1] == v else assignment[a][1]
            start = starts[a]
            end = start + OBS_LEN
            reset_done = end + sl
            segs[v] += [["travel", t_free, arrive], ["slew", arrive, rd],
                        ["wait", rd, start], ["obs", start, end],
                        ["reset", end, reset_done]]
            t_free = reset_done
            pos = st
    return segs

opt_segs = gantt_segments(assignment, orders, stations, starts)
h_segs = gantt_segments(h_assignment, h_orders, h_stations, h_starts)

# ------------------------------------------------------------- 7) sensitivity
# re-evaluate the optimized scheme structure at perturbed speed / slew rate by
# temporarily patching the timing constants (same simulate() logic as above)
import q2_lib as _lib

sens = []
_sp0, _om0 = SPEED, OMEGA
for sp in (2.5, 3.0, 3.5):
    for om in (24.0, 30.0, 36.0):
        SPEED = sp
        OMEGA = om
        _lib.SPEED = sp          # travel_time reads q2_lib.SPEED -- must patch too
        _lib.OMEGA = om
        obj2, starts2, _r2, ok2 = simulate(assignment, orders, stations)
        sens.append({"speed": sp, "omega_deg_s": om,
                     "obj_s": float(obj2) if ok2 else None})
SPEED, OMEGA, _lib.SPEED, _lib.OMEGA = _sp0, _om0, _sp0, _om0

# ------------------------------------------------------------- 8) dump
results = {
    "r_va_table": {f"V{v+1}": {a: R_VA[(v, a)] for a in ALERT_KEYS}
                   for v in range(5)},
    "r_va_argmin": {f"V{v+1}": {a: list(ARG_VA[(v, a)]) for a in ALERT_KEYS}
                    for v in range(5)},
    "LB": {"per_alert": dict(zip(ALERT_KEYS, LB_alert)), "global": LB_global},
    "region_areas": {a: FEAS[a]["area_mid"] for a in ALERT_KEYS},
    "region_areas_node": {a: FEAS[a]["area"] for a in ALERT_KEYS},
    "optimized": detail,
    "top5_structures": top5,
    "heuristic": {
        "assignment": {a: [v + 1 for v in h_assignment[a]] for a in ALERT_KEYS},  # 1-based
        "orders": {f"V{v+1}": h_orders.get(v, []) for v in range(5)},
        "stations": {f"V{v+1}": {a: list(h_stations[(v, a)]) for a in h_orders.get(v, [])}
                     for v in range(5)},
        "alert_starts": {a: float(h_starts[a]) for a in ALERT_KEYS}
        if h_starts else None,
        "objective_s": float(h_obj) if np.isfinite(h_obj) else None,
    },
    "comparison": {
        "obj_opt": float(obj), "obj_heuristic":
            float(h_obj) if np.isfinite(h_obj) else None,
        "gap_s": float(h_obj - obj) if np.isfinite(h_obj) else None,
    },
    "gantt_opt": {f"V{v+1}": opt_segs[v] for v in range(5)},
    "gantt_heu": {f"V{v+1}": h_segs[v] for v in range(5)},
    "sensitivity_speed_omega": sens,
    "knife_edge": {"station_clearances_m": knife,
                   "min_station_clearance_m": float(min_knife)},
    "robust_05": robust,
}
with open(os.path.join(RES_DIR, "q2b_results.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=float)

np.savez_compressed(os.path.join(RES_DIR, "q2b_data.npz"),
                    rmat=rmat)

lines = [
    "==== Problem 2(2) numeric summary ====",
    "r(v,a) earliest-ready table (s): rows V1..V5 x cols T1,T2,T3",
    np.round(rmat, 3).__str__(),
    f"per-alert LB = {dict(zip(ALERT_KEYS, np.round(LB_alert,3)))}  global LB = {LB_global:.3f} s",
    f"OPTIMIZED: obj = {obj:.3f} s (certified optimal: {abs(obj-LB_global)<1e-6})",
    f"  assignment: {detail['assignment']}",
    f"  orders: {detail['orders']}",
    f"  alert starts: " + ", ".join(f"{a}: {starts[a]:.3f} s" for a in ALERT_KEYS),
    f"HEURISTIC (nearest-assignment): obj = {h_obj:.3f} s",
    f"  assignment: {h_assignment}",
    f"  orders: {h_orders}",
    f"  alert starts: " + (", ".join(f"{a}: {h_starts[a]:.3f} s" for a in ALERT_KEYS)
                           if h_starts else "n/a"),
    f"GAP = {h_obj - obj:.3f} s",
    "sensitivity (speed, omega) -> obj:",
    str([(s['speed'], s['omega_deg_s'], None if s['obj_s'] is None else round(s['obj_s'], 2))
         for s in sens]),
]
summary = "\n".join(lines)
with open(os.path.join(RES_DIR, "q2b_summary.txt"), "w", encoding="utf-8") as f:
    f.write(summary + "\n")
print(summary)
