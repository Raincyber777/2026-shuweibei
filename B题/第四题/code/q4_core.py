# -*- coding: utf-8 -*-
"""Problem 4 core: disturbance scenarios, keep-original vs rescheduling.

Baseline = the Q2(2) optimized scheme (loaded from q2b_results.json).
Disturbances at t = 5 s; outage [5, t_rec] delays commands to t_rec.
Metrics: eta = k/N first, t_last second (60 s if any pending alert cannot
start inside the window).

Scenario set (justified in the docs):
  A) new alert T4: 8 azimuths (45 deg step) x R in {30, 40, 50}  -> 24
  B) single failure: 5 vehicles                                  -> 5
  C) single outage: t_rec in {10, 20, 30}                        -> 3
  D) failure x outage: 5 x 3                                     -> 15
  E) new x failure: 3 representative T4 positions x {V2, V4}     -> 6
  F) new x outage: 3 positions x 3 t_rec                         -> 9
  G) triple: 3 positions x {V2, V4} x {10, 30}                   -> 12
Outputs results/q4_results.json + q4_summary.txt.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import q4_lib4 as L
from q2_lib import TARGETS, TARGET_H, VEHICLES, travel_time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES_DIR = os.path.join(BASE, "results")
os.makedirs(RES_DIR, exist_ok=True)
T_REC_LIST = [10.0, 20.0, 30.0]
THETAS = list(range(0, 360, 45))
RS = [30.0, 40.0, 50.0]
NEW_H = 50.0

with open(os.path.join(BASE, "..", "第二题", "results", "q2b_results.json"),
          encoding="utf-8") as f:
    Q2 = json.load(f)

BASE_ASG = {a: tuple(vv - 1 for vv in v)          # q2b JSON is 1-based
                    for a, v in Q2["optimized"]["assignment"].items()}
BASE_ORDERS = {int(k[1:]) - 1: v for k, v in Q2["optimized"]["orders"].items()}
BASE_ST = {(int(k[1:]) - 1, a): tuple(p)
           for k, d in Q2["optimized"]["stations"].items() for a, p in d.items()}

# ------------------------------------------------ baseline replay + check
recs, base_starts = L.replay_baseline(BASE_ASG, BASE_ORDERS, BASE_ST)
for a in ("T1", "T2", "T3"):
    diff = abs(base_starts[a] - Q2["optimized"]["alert_starts"][a])
    assert diff < 1e-6, f"baseline replay mismatch on {a}: {diff}"
print("baseline replay OK:", {a: round(base_starts[a], 3)
                              for a in ("T1", "T2", "T3")})

# baseline timeline segments (for keep-original Gantt plots)
SEGS_BASE = {v: [] for v in range(5)}
for v in range(5):
    t_free = 0.0
    pos = tuple(VEHICLES[v])
    for r in recs[v]:
        st = r["st"]
        travel = travel_time(pos, st)
        arrive = t_free + travel
        rd = arrive + r["slew"]
        SEGS_BASE[v] += [["travel", t_free, arrive, r["a"]],
                         ["slew", arrive, rd, r["a"]],
                         ["wait", rd, r["start"], r["a"]],
                         ["obs", r["start"], r["end"], r["a"]],
                         ["reset", r["end"], r["reset_done"], r["a"]]]
        t_free = r["reset_done"]
        pos = st

CLOUDS_BASE = {"T2": L.build_cloud(*TARGETS["T2"], TARGET_H["T2"], 0.1),
               "T3": L.build_cloud(*TARGETS["T3"], TARGET_H["T3"], 0.1)}
print("base clouds ready",
      {k: round(v["area"], 1) for k, v in CLOUDS_BASE.items()})


# ------------------------------------------------ policies
def keep_original(failed=None, with_new=None):
    """No reassignment. Returns dict(eta, t_last, k, N, starts, dead)."""
    dead = []
    if failed is not None:
        for a in ("T2", "T3"):
            if failed in BASE_ASG[a]:
                dead.append(a)          # T1 already started -> completed
    starts = {a: base_starts[a] for a in ("T1", "T2", "T3")
              if a not in dead}
    if with_new is not None:
        dead.append("T4")               # never assigned under keep-original
    N = 3 + (1 if with_new is not None else 0)
    k = len(starts)
    t_last = max(starts.values()) if k == N else 60.0
    return {"k": k, "N": N, "eta": k / N, "t_last": t_last,
            "starts": {a: round(v, 3) for a, v in starts.items()},
            "dead": dead}


def reschedule(t_plan, failed=None, with_new=None, tag=""):
    """One-shot re-optimization at t_plan from the disturbance snapshot."""
    snap = L.snapshot(recs, t_plan)
    init = {v: dict(t_avail=s["t_avail"], pos=s["pos"], att=s["att"],
                    unobserved=s["unobserved"])
            for v, s in snap.items() if v != failed}
    started = [a for a in ("T2", "T3") if base_starts[a] < t_plan
               and (failed is None or failed not in BASE_ASG[a])]
    # alerts that cannot start under the ongoing original schedule remain pending
    pending = [a for a in ("T2", "T3") if a not in started]
    if with_new is not None:
        pending.append("T4")
    L.ALERTS4 = {}
    clouds = {}
    for a in pending:
        if a == "T4":
            clouds[a] = CLOUDS_NEW[with_new]
        else:
            clouds[a] = CLOUDS_BASE[a]
        L.ALERTS4[a] = (clouds[a]["tgt"], clouds[a]["h"])
    if not pending:
        # everything already started/locked before t_plan: nothing to reschedule
        all_starts = dict(base_starts)
        return {"k": 3, "N": 3 + (1 if with_new is not None else 0),
                "eta": 3.0 / (3 + (1 if with_new is not None else 0)),
                "t_last": float(max(all_starts.values())), "feasible": True,
                "n_comb": 0,
                "starts": {a: round(v, 3) for a, v in all_starts.items()},
                "assignment": {}, "orders": {}, "stations": {},
                "segs": {}, "tag": tag}
    best, n_comb = L.optimize_resched(None, {}, init, clouds, pending)
    if best is None:
        return {"k": len(started), "N": 3 + (1 if with_new is not None
                                             else 0), "eta": None,
                "t_last": 60.0, "feasible": False}
    obj, asg_r, orders_r, st_r = best
    obj, starts, ready_r, ok = L.simulate_init(asg_r, orders_r, st_r, init,
                                               pending)
    assert ok
    N = 3 + (1 if with_new is not None else 0)
    # count ALL alerts that start inside the window: T1 (already completed at
    # t = 5) + base alerts started before t_plan + rescheduled pending starts
    k = 1 + len(started) + sum(1 for a in pending if a in starts)
    eta = k / N
    all_starts = dict(base_starts)
    all_starts.update(starts)
    t_last = float(max(all_starts.values())) if k == N else 60.0
    segs = L.gantt_init(asg_r, orders_r, st_r, init, starts,
                        {a: L.ALERTS4[a] for a in pending}, ready_r)
    return {"k": k, "N": N, "eta": eta, "t_last": t_last,
            "feasible": True, "n_comb": n_comb,
            "starts": {a: round(v, 3) for a, v in all_starts.items()},
            "assignment": {a: [v + 1 for v in asg_r[a]] for a in pending},
            "orders": {f"V{v+1}": orders_r.get(v, []) for v in
                       sorted(orders_r)},
            "stations": {f"V{v+1}": {a: [round(x, 3) for x in st_r[(v, a)]]
                                     for a in orders_r.get(v, [])}
                         for v in sorted(orders_r)},
            "segs": {f"V{v+1}": segs[v] for v in range(5) if segs.get(v)},
            "tag": tag}


# ------------------------------------------------ A) single new alert (24)
CLOUDS_NEW = {}
scen_new = []
for th in THETAS:
    for R in RS:
        key = f"th{th}_R{R:.0f}"
        tgt, h, _ = L.alert_params(th, R, NEW_H)
        CLOUDS_NEW[key] = L.build_cloud(tgt[0], tgt[1], h, 0.2)
        keep = keep_original(with_new=key)
        res = reschedule(5.0, with_new=key, tag=key)
        res["theta"] = th
        res["R"] = R
        scen_new.append({"key": key, "theta": th, "R": R,
                         "keep": keep, "resched": res})
        print(f"A {key}: keep eta={keep['eta']:.2f} tlast={keep['t_last']:.1f}"
              f" | resched eta={res['eta']:.2f} tlast={res['t_last']:.2f} "
              f"starts={res.get('starts')}")

# representative positions for combination scenarios
order_by_tlast = sorted(scen_new, key=lambda s: s["resched"]["t_last"])
reps = {"best": order_by_tlast[0]["key"],
        "mid": order_by_tlast[len(order_by_tlast) // 2]["key"],
        "worst": order_by_tlast[-1]["key"]}
print("representative T4 positions:", reps)

# ------------------------------------------------ B) single failure (5)
scen_fail = []
for fv in range(5):
    keep = keep_original(failed=fv)
    res = reschedule(5.0, failed=fv, tag=f"failV{fv+1}")
    scen_fail.append({"failed": f"V{fv+1}", "keep": keep, "resched": res})
    print(f"B fail V{fv+1}: keep eta={keep['eta']:.3f} tlast={keep['t_last']:.1f}"
          f" | resched eta={res['eta']:.3f} tlast={res['t_last']:.2f}")

# ------------------------------------------------ C) single outage (3)
scen_out = []
for t_rec in T_REC_LIST:
    keep = keep_original()
    res = reschedule(t_rec, tag=f"out{t_rec:g}")
    scen_out.append({"t_rec": t_rec, "keep": keep, "resched": res})
    print(f"C outage t_rec={t_rec:g}: keep eta={keep['eta']:.2f} | "
          f"resched eta={res['eta']:.2f} tlast={res['t_last']:.2f}")

# ------------------------------------------------ D) failure x outage (15)
scen_fo = []
for fv in range(5):
    for t_rec in T_REC_LIST:
        keep = keep_original(failed=fv)
        res = reschedule(t_rec, failed=fv, tag=f"failV{fv+1}_out{t_rec:g}")
        scen_fo.append({"failed": f"V{fv+1}", "t_rec": t_rec,
                        "keep": keep, "resched": res})
        print(f"D fail V{fv+1} out{t_rec:g}: keep eta={keep['eta']:.3f} "
              f"tlast={keep['t_last']:.0f} | resched eta={res['eta']:.3f} "
              f"tlast={res['t_last']:.2f}")

FAIL_REP = ["V2", "V4"]     # orphan T3 / orphan T2 (V1~V4 impact-symmetric on T2)
# ------------------------------------------------ E) new x failure (6)
scen_nf = []
for key in reps.values():
    for fv in range(5):
        f = f"V{fv+1}"
        if f not in FAIL_REP:
            continue
        keep = keep_original(failed=fv, with_new=key)
        res = reschedule(5.0, failed=fv, with_new=key, tag=f"{key}_{f}")
        scen_nf.append({"key": key, "failed": f, "keep": keep,
                        "resched": res})
        print(f"E {key}+{f}: keep eta={keep['eta']:.3f} | resched "
              f"eta={res['eta']:.3f} tlast={res['t_last']:.2f}")

# ------------------------------------------------ F) new x outage (9)
scen_no = []
for key in reps.values():
    for t_rec in T_REC_LIST:
        keep = keep_original(with_new=key)
        res = reschedule(t_rec, with_new=key, tag=f"{key}_out{t_rec:g}")
        scen_no.append({"key": key, "t_rec": t_rec, "keep": keep,
                        "resched": res})
        print(f"F {key}+out{t_rec:g}: keep eta={keep['eta']:.3f} | resched "
              f"eta={res['eta']:.3f} tlast={res['t_last']:.2f}")

# ------------------------------------------------ G) triple (12)
scen_nfo = []
for key in reps.values():
    for f in FAIL_REP:
        fv = int(f[1:]) - 1
        for t_rec in (10.0, 30.0):
            keep = keep_original(failed=fv, with_new=key)
            res = reschedule(t_rec, failed=fv, with_new=key,
                             tag=f"{key}_{f}_out{t_rec:g}")
            scen_nfo.append({"key": key, "failed": f, "t_rec": t_rec,
                             "keep": keep, "resched": res})
            print(f"G {key}+{f}+out{t_rec:g}: keep eta={keep['eta']:.3f} | "
                  f"resched eta={res['eta']:.3f} tlast={res['t_last']:.2f}")

# ------------------------------------------------ representative gantts
gantts = {}
gantts["failV4_resched"] = reschedule(5.0, failed=3, tag="g1")
key_mid = reps["mid"]
gantts["triple_resched"] = reschedule(10.0, failed=3, with_new=key_mid,
                                      tag="g2")
keep_g = {"failV4": keep_original(failed=3),
          "triple": keep_original(failed=3, with_new=key_mid)}

results = {
    "baseline": {"starts": {a: round(base_starts[a], 3)
                            for a in ("T1", "T2", "T3")},
                 "assignment": {a: [v + 1 for v in BASE_ASG[a]]
                                for a in ("T1", "T2", "T3")},
                 "segments": {f"V{v+1}": SEGS_BASE[v] for v in range(5)},
                 "window_end": 60.0, "disturb_time": 5.0},
    "scenario_design": {
        "thetas_deg": THETAS, "R_list_m": RS, "H_new_m": NEW_H,
        "t_rec_list_s": T_REC_LIST, "fail_rep": FAIL_REP, "reps": reps,
        "counts": {"A_new": len(scen_new), "B_fail": len(scen_fail),
                   "C_outage": len(scen_out), "D_fail_out": len(scen_fo),
                   "E_new_fail": len(scen_nf), "F_new_out": len(scen_no),
                   "G_triple": len(scen_nfo)}},
    "scen_new": scen_new, "scen_fail": scen_fail, "scen_out": scen_out,
    "scen_fail_out": scen_fo, "scen_new_fail": scen_nf,
    "scen_new_out": scen_no, "scen_triple": scen_nfo,
    "representative": {"resched_failV4": gantts["failV4_resched"],
                       "resched_triple": gantts["triple_resched"],
                       "keep_failV4": keep_g["failV4"],
                       "keep_triple": keep_g["triple"]},
}
# ------------------------------------------------ timeline audit (must pass)
def audit_segs(segs):
    bad = 0
    for _v, ss in segs.items():
        prev_end = -1.0
        for typ, t0, t1 in [(x[0], float(x[1]), float(x[2])) for x in ss]:
            if t1 < t0 - 1e-9 or t0 < prev_end - 1e-9:
                bad += 1
            prev_end = max(prev_end, t1)
    return bad


n_bad, n_checked = 0, 0
for _b in ("scen_new", "scen_fail", "scen_out", "scen_fail_out",
           "scen_new_fail", "scen_new_out", "scen_triple"):
    for _s in results[_b]:
        _segs = _s["resched"].get("segs") or {}
        if _segs:
            n_checked += 1
            n_bad += audit_segs(_segs)
for _k in ("resched_failV4", "resched_triple"):
    n_bad += audit_segs(results["representative"][_k]["segs"])
print(f"timeline audit: {n_checked} scenario timelines, "
      f"{n_bad} negative/overlapping segments")
assert n_bad == 0, "timeline audit failed"

with open(os.path.join(RES_DIR, "q4_results.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=float)

lines = ["==== Problem 4 numeric summary ====",
         f"baseline starts: {results['baseline']['starts']}"]
for name, sc in (("A_new", scen_new), ("B_fail", scen_fail),
                 ("C_out", scen_out), ("D_fail_out", scen_fo),
                 ("E_new_fail", scen_nf), ("F_new_out", scen_no),
                 ("G_triple", scen_nfo)):
    gain_eta = sum(1 for s in sc if s["resched"]["eta"] > s["keep"]["eta"])
    gain_t = sum(1 for s in sc if s["resched"]["eta"] == s["keep"]["eta"]
                 and s["resched"]["t_last"] < s["keep"]["t_last"] - 1e-9)
    lines.append(f"{name}: n={len(sc)}  resched gains eta in {gain_eta}, "
                 f"gains t_last in {gain_t}")
summary = "\n".join(lines)
with open(os.path.join(RES_DIR, "q4_summary.txt"), "w", encoding="utf-8") as f:
    f.write(summary + "\n")
print(summary)
