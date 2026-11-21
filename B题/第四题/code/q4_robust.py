# -*- coding: utf-8 -*-
"""Problem-4 robustness & verification add-on (clean rewrite).

1. audit          — re-derive (eta, t_last) accounting for all 74 scenarios.
2. LOS margin 0.5 — representative reschedules with a hard margin + repair.
3. eps travel     — rerun with EPS_TRAVEL_M = 0.02 / 0.10.
4. baseline swap  — rerun on the robust Q2(2) baseline (10.837 scheme).
5. azimuth densification — 8 intermediate azimuths at R = 40 m.
Outputs results/q4_robust.json + q4_robust_summary.txt.
"""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import q4_lib4 as L
from q2_lib import TARGETS, TARGET_H, VEHICLES, H_CAM

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES_DIR = os.path.join(BASE, "results")
RES2 = os.path.join(BASE, "..", "第二题", "results")

with open(os.path.join(RES_DIR, "q4_results.json"), encoding="utf-8") as f:
    R4 = json.load(f)
with open(os.path.join(RES2, "q2b_results.json"), encoding="utf-8") as f:
    Q2 = json.load(f)

# ---------------- 1) audit of delivered accounting ---------------------------
issues = []
blocks = ("scen_new", "scen_fail", "scen_out", "scen_fail_out",
          "scen_new_fail", "scen_new_out", "scen_triple")
n_scen = 0
for b in blocks:
    for s in R4[b]:
        n_scen += 1
        for pol in ("keep", "resched"):
            p = s[pol]
            if p["eta"] is None:
                continue
            if abs(p["eta"] - p["k"] / p["N"]) > 5e-4:
                issues.append((b, s.get("key", s.get("failed", "")), pol,
                               "eta != k/N"))
            expect60 = p["k"] < p["N"]
            if expect60 and abs(p["t_last"] - 60.0) > 5e-4:
                issues.append((b, pol, "t_last should be 60"))
            if not expect60 and p.get("starts"):
                mx = max(p["starts"].values())
                if abs(p["t_last"] - mx) > 5e-3:  # starts rounded to 3 dp
                    issues.append((b, pol, "t_last != max starts"))
        if s["resched"]["eta"] is not None and \
                s["resched"]["eta"] < s["keep"]["eta"] - 1e-9:
            issues.append((b, "resched worse than keep"))
print(f"audit: {n_scen} scenarios, {len(issues)} issues")
for it in issues[:10]:
    print("  ", it)

# ---------------- shared machinery -------------------------------------------
BASE_ASG = {a: tuple(v) for a, v in Q2["optimized"]["assignment"].items()}
BASE_ORDERS = {int(k[1:]) - 1: v for k, v in Q2["optimized"]["orders"].items()}
BASE_ST = {(int(k[1:]) - 1, a): tuple(p)
           for k, d in Q2["optimized"]["stations"].items() for a, p in d.items()}
recs, base_starts = L.replay_baseline(BASE_ASG, BASE_ORDERS, BASE_ST)
for a in ("T1", "T2", "T3"):
    assert abs(base_starts[a] - Q2["optimized"]["alert_starts"][a]) < 1e-6

CLOUDS_BASE = {"T2": L.build_cloud(*TARGETS["T2"], TARGET_H["T2"], 0.1),
               "T3": L.build_cloud(*TARGETS["T3"], TARGET_H["T3"], 0.1)}
NEW_H = 50.0
_CLOUD_NEW = {}
SCHEMES = {}          # tag -> dict with the full scheme + snapshot + baseline


def cloud_new(key):
    if key not in _CLOUD_NEW:
        body = key[2:]
        th_s, r_s = body.split("_R")
        th, R = float(th_s), float(r_s)
        tgt, h, _ = L.alert_params(th, R, NEW_H)
        _CLOUD_NEW[key] = L.build_cloud(tgt[0], tgt[1], h, 0.2)
    return _CLOUD_NEW[key]


def run_resched(recs_base, base_st, t_plan, failed=None, with_new=None,
                margin=0.0, tag=""):
    """Re-optimization from the snapshot of recs_base at t_plan (shared by all
    robustness checks). base_st = the baseline's alert start times."""
    snap = L.snapshot(recs_base, t_plan)
    init = {v: dict(t_avail=s["t_avail"], pos=s["pos"], att=s["att"])
            for v, s in snap.items() if v != failed}
    started = [a for a in ("T2", "T3") if base_st[a] < t_plan
               and (failed is None or failed not in CUR_ASG[a])]
    pending = [a for a in ("T2", "T3") if a not in started]
    if with_new is not None:
        pending.append("T4")
    N = 3 + (1 if with_new is not None else 0)
    if not pending:
        return {"k": 3, "N": N, "eta": 3.0 / N,
                "t_last": float(max(base_st.values())),
                "starts": {a: round(v, 3) for a, v in base_st.items()}}
    clouds = {}
    L.ALERTS4 = {}
    for a in pending:
        clouds[a] = cloud_new(with_new) if a == "T4" else CLOUDS_BASE[a]
        L.ALERTS4[a] = (clouds[a]["tgt"], clouds[a]["h"])
    best, n_comb = L.optimize_resched(None, {}, init, clouds, pending,
                                      los_margin=margin)
    if best is None:
        return {"k": len(started) + 1, "N": N, "eta": (len(started) + 1) / N,
                "t_last": 60.0, "feasible": False}
    obj, asg_r, orders_r, st_r = best
    obj, starts, _r, ok = L.simulate_init(asg_r, orders_r, st_r, init,
                                          pending)
    assert ok
    k = 1 + len(started) + sum(1 for a in pending if a in starts)
    alls = dict(base_st)
    alls.update(starts)
    SCHEMES[tag] = {"asg": asg_r, "orders": orders_r, "st": st_r,
                    "init": init, "pending": pending,
                    "targets": dict(L.ALERTS4), "base_st": base_st,
                    "clouds": clouds}
    return {"k": k, "N": N, "eta": k / N,
            "t_last": float(max(alls.values())) if k == N else 60.0,
            "starts": {a: round(v, 3) for a, v in alls.items()},
            "n_comb": n_comb, "tag": tag}


def min_clearance_of(tag):
    sch = SCHEMES[tag]
    vals = [L.los_clearance_pt(sch["st"][(v, a)][0], sch["st"][(v, a)][1],
                               sch["targets"][a][0], sch["targets"][a][1])
            for v in sch["orders"] for a in sch["orders"][v]]
    return float(min(vals))


def repair_margins(tag, margin):
    """Move margin-violating stations to the nearest feasible point with
    clearance >= margin (grid search in a +/-1.5 m box), then re-simulate."""
    sch = SCHEMES[tag]
    asg_r, orders_r, st_r = sch["asg"], sch["orders"], sch["st"]
    init, pending, targets, base_st = (sch["init"], sch["pending"],
                                       sch["targets"], sch["base_st"])
    repaired = 0
    for (v, a) in list(st_r.keys()):
        st = st_r[(v, a)]
        tgt, h = targets[a]
        rmin = (h - H_CAM) / np.tan(np.radians(80.0))
        clr = L.los_clearance_pt(st[0], st[1], tgt, h)
        if clr >= margin - 1e-9:
            continue
        cand = None
        best_obj = np.inf
        for dx in np.arange(-1.5, 1.51, 0.1):
            for dy in np.arange(-1.5, 1.51, 0.1):
                px, py = st[0] + dx, st[1] + dy
                if not L.feasible_pt(px, py, tgt, h, rmin):
                    continue
                if L.los_clearance_pt(px, py, tgt, h) < margin - 1e-9:
                    continue
                az, el, sl = L.station_times((px, py), tgt, h)
                obj = (init[v]["t_avail"]
                       + L.travel_time(init[v]["pos"], (px, py)) + sl)
                if obj < best_obj:
                    best_obj, cand = obj, (float(px), float(py))
        if cand is not None:
            st_r[(v, a)] = cand
            repaired += 1
    obj, starts, _r, ok = L.simulate_init(asg_r, orders_r, st_r, init,
                                          pending)
    clr_all = {f"V{v+1}": {a: round(L.los_clearance_pt(st_r[(v, a)][0],
                                                       st_r[(v, a)][1],
                                                       targets[a][0],
                                                       targets[a][1]), 4)
                           for a in orders_r.get(v, [])} for v in orders_r}
    min_clr = min(min(d.values()) for d in clr_all.values())
    k = 1 + len([a for a in ("T2", "T3") if base_st[a] < 1e9 and a in starts])
    alls = dict(base_st)
    alls.update(starts)
    return {"ok": ok, "starts": {a: round(v, 3) for a, v in alls.items()},
            "min_clearance_m": min_clr, "repaired": repaired,
            "t_last": float(max(alls.values())) if ok else None}


CUR_ASG = BASE_ASG

# ---------------- 2) LOS margin = 0.5 m on representative scenarios ----------
margin_results = []
reps = R4["scenario_design"]["reps"]
cases = [("failV4", 5.0, dict(failed=3)),
         ("new_" + reps["mid"], 5.0, dict(with_new=reps["mid"])),
         ("triple_" + reps["mid"], 10.0, dict(failed=3,
                                              with_new=reps["mid"]))]
for label, tp, kw in cases:
    failed = kw.get("failed")
    with_new = kw.get("with_new")
    r00 = run_resched(recs, base_starts, tp, failed=failed,
                      with_new=with_new, margin=0.0, tag=label + "_m00")
    m00_clr = min_clearance_of(label + "_m00")
    t0 = time.time()
    r05 = run_resched(recs, base_starts, tp, failed=failed,
                      with_new=with_new, margin=0.5, tag=label + "_m05")
    rep = repair_margins(label + "_m05", 0.5)
    dt = time.time() - t0
    margin_results.append({"case": label, "t_plan": tp,
                           "m00": {"eta": r00["eta"],
                                   "t_last": r00["t_last"],
                                   "min_clearance_m": m00_clr},
                           "m05": {"eta": r05["eta"],
                                   "t_last": rep["t_last"] if rep["ok"] else None,
                                   "min_clearance_m": rep["min_clearance_m"],
                                   "repaired": rep["repaired"]},
                           "runtime_s": round(dt, 1)})
    print(f"margin {label}: m00 eta={r00['eta']:.2f} tlast={r00['t_last']:.2f} "
          f"minclr={m00_clr:.4f} | m05 eta={r05['eta']:.2f} "
          f"tlast={rep['t_last']:.2f} minclr={rep['min_clearance_m']:.4f} "
          f"repaired={rep['repaired']} ({dt:.0f}s)")

# ---------------- 3) epsilon sensitivity -------------------------------------
eps_results = []
for eps in (0.02, 0.05, 0.10):
    L.EPS_TRAVEL_M = eps
    r = run_resched(recs, base_starts, 5.0, failed=3, tag=f"eps{eps}")
    eps_results.append({"eps_m": eps, "eta": r["eta"], "t_last": r["t_last"]})
    print(f"eps {eps}: eta={r['eta']:.2f} tlast={r['t_last']:.2f}")
L.EPS_TRAVEL_M = 0.05

# ---------------- 4) robust Q2(2) baseline -----------------------------------
rb = Q2.get("robust_05", {})
base_robust_results = []
if rb.get("assignment"):
    asg_r = {a: tuple(vv - 1 for vv in v)
             for a, v in rb["assignment"].items()}
    ord_r = {int(k[1:]) - 1: v for k, v in rb["orders"].items()}
    st_r = {(int(k[1:]) - 1, a): tuple(p)
            for k, d in rb["stations"].items() for a, p in d.items()}
    recs_r, starts_r = L.replay_baseline(asg_r, ord_r, st_r)
    print("robust baseline replay starts:",
          {a: round(v, 3) for a, v in starts_r.items()})
    CUR_ASG = asg_r
    for label, kw in (("failV4", dict(failed=3)),
                      ("new_" + reps["mid"], dict(with_new=reps["mid"]))):
        dead = [a for a in ("T2", "T3")
                if kw.get("failed") is not None and
                kw["failed"] in asg_r[a]]
        k = 3 - len(dead) - (1 if kw.get("with_new") else 0)
        N = 3 + (1 if kw.get("with_new") else 0)
        keep_r = {"k": k, "N": N, "eta": k / N,
                  "t_last": 60.0 if k < N else float(max(starts_r.values()))}
        rr = run_resched(recs_r, starts_r, kw.get("t_plan", 5.0),
                         failed=kw.get("failed"), with_new=kw.get("with_new"),
                         tag=label + "_rb")
        base_robust_results.append({"case": label, "keep": keep_r,
                                    "resched": rr})
        print(f"robust-baseline {label}: keep eta={keep_r['eta']:.2f} | "
              f"resched eta={rr['eta']:.2f} tlast={rr['t_last']:.2f}")
    CUR_ASG = BASE_ASG
else:
    print("robust_05 scheme not stored — skip baseline swap")

# ---------------- 5) azimuth densification (R = 40) --------------------------
dens = []
for th in (22.5, 67.5, 112.5, 157.5, 202.5, 247.5, 292.5, 337.5):
    key = f"th{th:g}_R40"
    r = run_resched(recs, base_starts, 5.0, with_new=key, tag=key)
    dens.append({"theta": th, "R": 40.0, "eta": r["eta"], "t_last": r["t_last"]})
    print(f"dens th{th:g}: eta={r['eta']:.2f} tlast={r['t_last']:.2f}")

out = {"audit": {"n_scenarios": n_scen, "issues": issues},
       "margin_05": margin_results, "eps_travel": eps_results,
       "baseline_robust": base_robust_results,
       "azimuth_densification": dens}
with open(os.path.join(RES_DIR, "q4_robust.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2, default=float)
lines = ["==== Problem 4 robustness summary ====",
         f"audit: {n_scen} scenarios, {len(issues)} accounting issues"]
for m in margin_results:
    lines.append(f"margin0.5 {m['case']}: eta {m['m00']['eta']:.2f}->"
                 f"{m['m05']['eta']:.2f}, t_last {m['m00']['t_last']:.2f}->"
                 f"{m['m05']['t_last']:.2f}, min_clearance "
                 f"{m['m00']['min_clearance_m']:.4f}->{m['m05']['min_clearance_m']:.4f} "
                 f"(stations repaired: {m['m05']['repaired']})")
for e in eps_results:
    lines.append(f"eps {e['eps_m']} m: eta={e['eta']:.2f} t_last={e['t_last']:.2f}")
for b in base_robust_results:
    lines.append(f"robust-baseline {b['case']}: keep {b['keep']['eta']:.2f}/"
                 f"{b['keep']['t_last']:.0f} -> resched {b['resched']['eta']:.2f}/"
                 f"{b['resched']['t_last']:.2f}")
for d in dens:
    lines.append(f"dens th{d['theta']:g} R40: eta={d['eta']:.2f} "
                 f"t_last={d['t_last']:.2f}")
with open(os.path.join(RES_DIR, "q4_robust_summary.txt"), "w",
          encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print("\n".join(lines))
