# -*- coding: utf-8 -*-
"""Problem-4 library: baseline replay, disturbance snapshots, attitude-aware
rescheduling simulator and optimizer. Reuses the reviewed geometry helpers
of q2_lib (第二题) via repo-relative sys.path."""
import itertools
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(_HERE)),
                                "第二题", "code"))
from q2_lib import (BUILDINGS, FIELD, OMEGA, R_VEH, H_CAM, SPEED, TARGETS,
                    TARGET_H, R_MIN_GEO, VEHICLES, dist_to_rect,
                    los_blocked_h, region_masks, make_grid, wrap180,
                    pointing_angles, travel_time, path_length, nelder_mead)

OBS_LEN = 5.0
ALERT_KEYS = ["T1", "T2", "T3"]
SUB_TARGET = 15000


def alert_params(theta, R, H):
    """Horizontal projection and derived quantities of an alert."""
    tx = 50.0 + R * np.cos(np.radians(theta))
    ty = 50.0 + R * np.sin(np.radians(theta))
    rmin = (H - H_CAM) / np.tan(np.radians(80.0))
    return (tx, ty), H, rmin


def station_times(st, tgt, h_tgt):
    az, el, r = pointing_angles(st, tgt, h_tgt)
    return az, el, max(abs(az), el) / OMEGA


def build_cloud(tx, ty, h, step=0.1, sub_target=SUB_TARGET):
    """Feasible-station cloud for one alert (grid -> subsampled arrays)."""
    tgt, rmin = (tx, ty), (h - H_CAM) / np.tan(np.radians(80.0))
    X, Y = make_grid(step, center=True)
    c1, c2, c3, _ = region_masks(X, Y, tgt, h, rmin)
    m = c1 & c2 & c3
    pts = np.column_stack([X[m], Y[m]])
    stride = max(1, int(round(len(pts) / sub_target)))
    sub = pts[::stride]
    dx = tgt[0] - sub[:, 0]
    dy = tgt[1] - sub[:, 1]
    rr = np.hypot(dx, dy)
    az = wrap180(np.degrees(np.arctan2(dy, dx)))
    el = np.degrees(np.arctan((h - H_CAM) / np.maximum(rr, 1e-12)))
    sl = np.maximum(np.abs(az), el) / OMEGA
    return {"tgt": tgt, "h": h, "rmin": rmin, "pts": pts, "sub": sub,
            "az": az, "el": el, "slew": sl,
            "area": float(m.sum()) * step * step}


def feasible_pt(x, y, tgt, h, rmin):
    if not (R_VEH <= x <= FIELD - R_VEH and R_VEH <= y <= FIELD - R_VEH):
        return False
    for b in BUILDINGS:
        if dist_to_rect(np.array([x]), np.array([y]), b)[0] < R_VEH - 1e-9:
            return False
    if np.hypot(x - tgt[0], y - tgt[1]) < rmin - 1e-9:
        return False
    if los_blocked_h(np.array([x]), np.array([y]), tgt, h)[0]:
        return False
    return True


# ---------------- baseline replay -------------------------------------------
def replay_baseline(asg, orders, stations):
    """Replay the Q2(2) optimized scheme; returns per-vehicle task records.

    record: dict(v, a, st, depart, arrive, ready, start, end, reset_done,
                 az, el, slew)
    Also returns alert starts. Must reproduce q2b_core's numbers.
    Uses a per-vehicle done-pointer so completed chains are never re-walked.
    """
    ready = {}
    alert_start = {}
    chain_ready = {v: 0.0 for v in range(5)}
    chain_pos = {v: tuple(VEHICLES[v]) for v in range(5)}
    done = {v: 0 for v in range(5)}
    recs = {v: [] for v in range(5)}
    total = sum(len(orders.get(v, [])) for v in range(5))
    rounds = 0
    while sum(done.values()) < total and rounds < 12:
        rounds += 1
        progress = False
        for v in range(5):
            tasks = orders.get(v, [])
            t_free = chain_ready[v]
            pos = chain_pos[v]
            new_recs = []
            for a in tasks[done[v]:]:
                st = stations[(v, a)]
                az, el, sl = station_times(st, TARGETS[a], TARGET_H[a])
                travel = travel_time(pos, st)
                arrive = t_free + travel
                rd = arrive + sl
                ready[(v, a)] = rd
                v2 = asg[a][0] if asg[a][1] == v else asg[a][1]
                if (v2, a) in ready:
                    start = max(rd, ready[(v2, a)])
                else:
                    break
                alert_start[a] = start
                rec = dict(v=v, a=a, st=tuple(st), depart=t_free,
                           arrive=arrive, ready=rd, start=start,
                           end=start + OBS_LEN, reset_done=start + OBS_LEN + sl,
                           az=az, el=el, slew=sl, travel=travel)
                new_recs.append(rec)
                t_free = rec["reset_done"]
                pos = st
            if new_recs:
                done[v] += len(new_recs)
                recs[v] += new_recs
                chain_ready[v] = t_free
                chain_pos[v] = pos
                progress = True
        if not progress:
            break
    return recs, alert_start


def snapshot(recs, t):
    """Vehicle states at time t (rule-compliant attitudes).

    Returns {v: dict(t_avail, pos, att, locked_until)} where att=(pan,tilt)
    is the attitude at t_avail and locked_until>0 marks a vehicle mid-obs.
    """
    # from-positions must exist before interpolation
    for v in range(5):
        prev = None
        for r in recs[v]:
            r["from"] = tuple(VEHICLES[v]) if prev is None else prev["st"]
            prev = r
    snap = {}
    for v in range(5):
        rs = recs[v]
        if not rs:
            snap[v] = dict(t_avail=t, pos=tuple(VEHICLES[v]), att=(0.0, 0.0),
                           locked_until=0.0)
            continue
        state = ("idle", None)
        for r in rs:
            if t < r["depart"]:
                state = ("idle", r)
                break
            if r["depart"] <= t < r["arrive"]:
                state = ("enroute", r)
                break
            if r["arrive"] <= t < r["ready"]:
                state = ("slewing", r)
                break
            if r["ready"] <= t < r["start"]:
                state = ("waiting", r)      # sync wait: reassignable
                break
            if r["start"] <= t < r["end"]:
                state = ("observing", r)    # alert started -> locked
                break
            if r["end"] <= t < r["reset_done"]:
                state = ("resetting", r)
                break
        kind, r = state
        if kind == "idle":
            snap[v] = dict(t_avail=t, pos=tuple(VEHICLES[v]), att=(0.0, 0.0),
                           locked_until=0.0)
        elif kind == "waiting":
            snap[v] = dict(t_avail=t, pos=tuple(r["st"]),
                           att=(r["az"], r["el"]), locked_until=0.0)
        elif kind == "enroute":
            f = (t - r["depart"]) / max(r["travel"], 1e-12)
            p = (r["from"][0] + (r["st"][0] - r["from"][0]) * f,
                 r["from"][1] + (r["st"][1] - r["from"][1]) * f)
            snap[v] = dict(t_avail=t, pos=p, att=(0.0, 0.0), locked_until=0.0)
        elif kind == "slewing":
            f = (t - r["arrive"]) / max(r["slew"], 1e-12)
            snap[v] = dict(t_avail=t, pos=tuple(r["st"]),
                           att=(f * r["az"], f * r["el"]), locked_until=0.0)
        elif kind == "observing":
            snap[v] = dict(t_avail=r["reset_done"], pos=tuple(r["st"]),
                           att=(0.0, 0.0), locked_until=r["end"])
        elif kind == "resetting":
            snap[v] = dict(t_avail=r["reset_done"], pos=tuple(r["st"]),
                           att=(0.0, 0.0), locked_until=r["reset_done"])
        else:  # after the last task's reset
            snap[v] = dict(t_avail=max(t, r["reset_done"]),
                           pos=tuple(r["st"]), att=(0.0, 0.0),
                           locked_until=0.0)
    return snap


# ---------------- attitude-aware simulator -----------------------------------
def simulate_init(asg, orders, stations, init, pending):
    """Fixed-point simulation from the snapshot state.

    init: {v: (t_avail, pos, att)}; pending: alert keys to evaluate.
    Returns (obj, starts, ready, feasible).
    Slew rule: any positive travel leg forces the due-east attitude (problem
    rule), so the slew starts from (0,0) unless travel == 0.
    """
    ready = {}
    alert_start = {}
    chain = {v: (init[v]["t_avail"], init[v]["pos"], init[v]["att"])
             for v in init}
    done = {v: 0 for v in init}
    total = sum(len(orders.get(v, [])) for v in init)
    rounds = 0
    while sum(done.values()) < total and rounds < 12:
        rounds += 1
        progress = False
        for v in init:
            t_free, pos, att = chain[v]
            walked = []
            for a in orders.get(v, [])[done[v]:]:
                st = stations.get((v, a))
                if st is None:
                    return (np.inf, {}, {}, False)
                az, el, _ = station_times(st, TARGETS[a] if a in ALERT_KEYS
                                          else ALERTS4[a][0], ALERTS4[a][1])
                travel = travel_time(pos, st)
                if travel * SPEED > 0.05:   # <= 5 cm repositioning counts as no-travel
                    slew = max(abs(az), abs(el)) / OMEGA
                else:
                    slew = max(abs(wrap180(az - att[0])),
                               abs(el - att[1])) / OMEGA
                rd = t_free + travel + slew
                ready[(v, a)] = rd
                v2 = asg[a][0] if asg[a][1] == v else asg[a][1]
                if (v2, a) in ready:
                    start = max(rd, ready[(v2, a)])
                else:
                    break
                alert_start[a] = start
                t_free = start + OBS_LEN + max(abs(az), abs(el)) / OMEGA
                pos = st
                att = (0.0, 0.0)
                walked.append(a)
            if walked:
                done[v] += len(walked)
                chain[v] = (t_free, pos, att)
                progress = True
        if not progress:
            break
    if set(pending) - set(alert_start):
        return (np.inf, {}, {}, False)
    obj = max(alert_start[a] for a in pending)
    return (obj, alert_start, ready, True)


ALERTS4 = {}


def greedy_stations(asg, orders, init, clouds, k_cap=60):
    """Chain-wise ready-minimizing stations from the snapshot state."""
    stations = {}
    chain = {v: (init[v]["t_avail"], init[v]["pos"], init[v]["att"])
             for v in init}
    for v in init:
        t_free, pos, att = chain[v]
        for a in orders.get(v, []):
            cl = clouds[a]
            d = np.hypot(cl["sub"][:, 0] - pos[0], cl["sub"][:, 1] - pos[1])
            st_ = cl["sub"][int(np.argmin(d))]
            # current position first if feasible: zero travel -> attitude-aware
            # slew (avoids the measure-zero full-reslew discontinuity)
            if feasible_pt(pos[0], pos[1], cl["tgt"], cl["h"], cl["rmin"]):
                stations[(v, a)] = (float(pos[0]), float(pos[1]))
            else:
                stations[(v, a)] = tuple(st_)
            pos = stations[(v, a)]
        chain[v] = (t_free, pos, att)
    return stations


def chain_candidates(cloud, pos, k=40):
    d = np.hypot(cloud["sub"][:, 0] - pos[0], cloud["sub"][:, 1] - pos[1])
    idx = np.argsort(d)[:k]
    return cloud["sub"][idx]


def optimize_resched(asg, orders, init, clouds, pending, topk=12,
                     sweeps=3):
    """Fast pass over all (pair, order) structures + descent/polish on top-K.

    pending = list of pending alert keys (sets the module-level ALERT_KEYS3).
    """
    global ALERT_KEYS3
    ALERT_KEYS3 = list(pending)
    vehicles = sorted(init.keys())
    pair_list = list(itertools.combinations(vehicles, 2))
    results = []
    for combo in itertools.product(pair_list, repeat=len(pending)):
        asg_c = dict(zip(pending, combo))
        tasks = {v: [a for a in pending if v in asg_c[a]] for v in vehicles}
        dbl = [v for v in vehicles if len(tasks[v]) > 1]
        if not dbl:
            order_list = [{v: tasks[v] for v in vehicles}]
        else:
            order_list = []
            for perm in itertools.product(
                    *[list(itertools.permutations(tasks[v])) for v in dbl]):
                od = {v: tasks[v] for v in vehicles}
                for v, p in zip(dbl, perm):
                    od[v] = list(p)
                order_list.append(od)
        for orders_c in order_list:
            stations = greedy_stations(asg_c, orders_c, init, clouds)
            obj, starts, _r, ok = simulate_init(asg_c, orders_c, stations,
                                                init, pending)
            if ok:
                results.append((obj, asg_c, orders_c, stations))
    results.sort(key=lambda t: t[0])
    best = None
    for obj0, asg_c, orders, stations in results[:topk]:
        st_c = dict(stations)
        ob = obj0
        for _ in range(sweeps):
            imp = False
            _o, _s, ready_s, ok_s = simulate_init(asg_c, orders, st_c,
                                                  init, pending)
            if not ok_s:
                break
            st_best = dict(st_c)
            dbl = [v for v in vehicles if len(orders.get(v, [])) == 2]
            for v in dbl:
                a1, a2 = orders[v]
                pr1 = ready_s.get(_partner(asg_c, v, a1), np.inf)
                pr2 = ready_s.get(_partner(asg_c, v, a2), np.inf)
                pos0 = init[v]["pos"]
                c1 = chain_candidates(clouds[a1], pos0, 30)
                best_loc = (ob, None, None)
                for i in range(len(c1)):
                    p1 = tuple(c1[i])
                    _, _, sl1 = station_times(p1, clouds[a1]["tgt"],
                                              clouds[a1]["h"])
                    tr1 = travel_time(pos0, p1)
                    rd1 = init[v]["t_avail"] + tr1 + sl1
                    start1 = max(rd1, pr1)
                    depart1 = start1 + OBS_LEN + sl1
                    c2 = chain_candidates(clouds[a2], p1, 60)
                    _, _, sl2 = station_times_arr(c2, clouds[a2])
                    tr2 = np.array([travel_time(p1, tuple(q)) for q in c2])
                    rd2 = depart1 + tr2 + sl2
                    start2 = np.maximum(rd2, pr2)
                    obj_arr = np.maximum(np.full(len(c2), start1), start2)
                    kk = int(np.argmin(obj_arr))
                    if obj_arr[kk] < best_loc[0] - 1e-9:
                        best_loc = (float(obj_arr[kk]), p1, tuple(c2[kk]))
                if best_loc[1] is not None:
                    st_c[(v, a1)], st_c[(v, a2)] = best_loc[1], best_loc[2]
                    ob2, _s2, _r2, ok2 = simulate_init(asg_c, orders, st_c,
                                                       init, pending)
                    if ok2 and ob2 < ob - 1e-9:
                        ob = ob2
                        imp = True
                    else:
                        st_c = dict(st_best)
            if not imp:
                break
        # NM polish on every station against the global objective
        for _ in range(2):
            imp = False
            for v in vehicles:
                for a in orders.get(v, []):
                    cur = np.array(st_c[(v, a)], float)

                    def fpol(p, v=v, a=a, cur=cur, st_c=st_c):
                        cl = clouds[a]
                        if not feasible_pt(p[0], p[1], cl["tgt"], cl["h"],
                                           cl["rmin"]):
                            return 1e4 + np.hypot(p[0] - cur[0],
                                                  p[1] - cur[1])
                        s2 = dict(st_c)
                        s2[(v, a)] = (float(p[0]), float(p[1]))
                        o2, _s2, _r2, ok2 = simulate_init(asg_c, orders, s2,
                                                          init, pending)
                        return o2 if ok2 else 1e4

                    px, pf = nelder_mead(fpol, cur, step=0.5, tol=1e-4,
                                         max_iter=140)
                    if pf < ob - 1e-6 and feasible_pt(px[0], px[1],
                                                      clouds[a]["tgt"],
                                                      clouds[a]["h"],
                                                      clouds[a]["rmin"]):
                        st_c[(v, a)] = (float(px[0]), float(px[1]))
                        ob, _s2, _r2, ok2 = simulate_init(asg_c, orders,
                                                          st_c, init, pending)
                        imp = True
            if not imp:
                break
        if best is None or ob < best[0]:
            best = (ob, asg_c, orders, st_c)
    return best, len(results)


def station_times_arr(pts, cloud):
    dx = cloud["tgt"][0] - pts[:, 0]
    dy = cloud["tgt"][1] - pts[:, 1]
    rr = np.hypot(dx, dy)
    az = wrap180(np.degrees(np.arctan2(dy, dx)))
    el = np.degrees(np.arctan((cloud["h"] - H_CAM) / np.maximum(rr, 1e-12)))
    return az, el, np.maximum(np.abs(az), el) / OMEGA


def _partner(asg, v, a):
    return asg[a][0] if asg[a][1] == v else asg[a][1]


ALERT_KEYS3 = ["T1", "T2", "T3"]   # replaced dynamically by the caller


def gantt_init(asg, orders, stations, init, starts, targets):
    """Timeline segments from the snapshot state (for representative plots)."""
    segs = {v: [] for v in range(5)}
    for v in init:
        t_free, pos, att = init[v]["t_avail"], init[v]["pos"], init[v]["att"]
        for a in orders.get(v, []):
            st = stations[(v, a)]
            az, el, _ = station_times(st, *targets[a])
            travel = travel_time(pos, st)
            arrive = t_free + travel
            if travel * SPEED > 0.05:   # <= 5 cm repositioning counts as no-travel
                slew = max(abs(az), abs(el)) / OMEGA
            else:
                slew = max(abs(wrap180(az - att[0])),
                           abs(el - att[1])) / OMEGA
            rd = arrive + slew
            start = starts[a]
            end = start + OBS_LEN
            reset_done = end + max(abs(az), abs(el)) / OMEGA
            if travel * SPEED > 0.05:   # <= 5 cm repositioning counts as no-travel
                segs[v].append(["travel", t_free, arrive])
            segs[v] += [["slew", arrive, rd], ["wait", rd, start],
                        ["obs", start, end], ["reset", end, reset_done]]
            t_free = reset_done
            pos = st
    return segs
