# -*- coding: utf-8 -*-
"""Problem 4: a *simple-repair* baseline between keep-original and re-optimization.

keep-original issues no new commands, so an idle vehicle is never inserted and a
new alert / orphan alert is simply lost.  Re-optimization is a full search.  To
separate the value of re-optimization from the value of merely reacting, this
script builds a minimal repair:

  * keep every pending assignment and its original station;
  * replace a failed vehicle by the nearest available spare for the same alert;
  * insert a new alert T4 at the end of the two earliest-available chains;
  * choose a station only for new/replacement tasks (current position if
    feasible, otherwise the nearest feasible cloud point);
  * no coordinate descent, no Nelder-Mead, no re-ordering of existing tasks.

The repaired plan is simulated with the same q4_lib4.simulate_init as the
re-optimized plan, and compared with the stored keep/resched results.

Outputs: results/q4_repair.json, results/q4_repair.md
"""
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import q4_lib4 as L
from q2_lib import TARGETS, VEHICLES

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES_DIR = os.path.join(BASE, "results")
Q2_PATH = os.path.join(BASE, "..", "\u7b2c\u4e8c\u9898", "results", "q2b_results.json")
with open(Q2_PATH, encoding="utf-8") as f:
    Q2 = json.load(f)
with open(os.path.join(RES_DIR, "q4_results.json"), encoding="utf-8") as f:
    Q4 = json.load(f)

BASE_ASG = {a: tuple(v - 1 for v in vv)
            for a, vv in Q2["optimized"]["assignment"].items()}
BASE_ORDERS = {int(k[1:]) - 1: list(v)
               for k, v in Q2["optimized"]["orders"].items()}
BASE_ST = {(int(k[1:]) - 1, a): tuple(p)
           for k, d in Q2["optimized"]["stations"].items()
           for a, p in d.items()}
recs, base_starts = L.replay_baseline(BASE_ASG, BASE_ORDERS, BASE_ST)

CLOUDS = {"T2": L.build_cloud(*TARGETS["T2"], L.TARGET_H["T2"], 0.1),
          "T3": L.build_cloud(*TARGETS["T3"], L.TARGET_H["T3"], 0.1)}
CLOUD_CACHE = {}


def cloud_for(key):
    if key not in CLOUD_CACHE:
        th, r = key.split("_")
        theta = float(th[2:])
        R = float(r[1:])
        tgt, h, _ = L.alert_params(theta, R, 50.0)
        CLOUD_CACHE[key] = L.build_cloud(tgt[0], tgt[1], h, 0.2)
    return CLOUD_CACHE[key]


def nearest_station(pos, cloud):
    if L.feasible_pt(pos[0], pos[1], cloud["tgt"], cloud["h"], cloud["rmin"]):
        return (float(pos[0]), float(pos[1]))
    d = np.hypot(cloud["sub"][:, 0] - pos[0], cloud["sub"][:, 1] - pos[1])
    p = cloud["sub"][int(np.argmin(d))]
    return (float(p[0]), float(p[1]))


def ready_from(pos, cloud):
    st = nearest_station(pos, cloud)
    az, el, sl = L.station_times(st, cloud["tgt"], cloud["h"])
    return L.travel_time(pos, st) + sl, st


def build_repair(t_plan, failed=None, with_new=None):
    """Return (metrics dict, plan dict) of the simple-repair policy."""
    snap = L.snapshot(recs, t_plan)
    init = {v: dict(t_avail=s["t_avail"], pos=s["pos"], att=s["att"],
                    unobserved=s["unobserved"])
            for v, s in snap.items() if v != failed}
    started = [a for a in ("T2", "T3") if base_starts[a] < t_plan
               and (failed is None or failed not in BASE_ASG[a])]
    pending = [a for a in ("T2", "T3") if a not in started]
    if with_new is not None:
        pending.append("T4")
    if not pending:
        all_starts = dict(base_starts)
        k, N = 3, 3
        t_last = (float(max(all_starts.values()))
                  if max(all_starts.values()) <= 60.0 + 1e-9 else 60.0)
        return {"k": k, "N": N, "eta": 1.0, "t_last": t_last,
                "feasible": True,
                "starts": {a: round(v, 3) for a, v in all_starts.items()},
                "pending": [], "started": started, "asg": {}, "orders": {},
                "stations": {}}

    # ---- assignment: keep original pairs, replace a failed member
    asg = {}
    for a in pending:
        if a == "T4":
            continue
        pr = [v for v in BASE_ASG[a] if v != failed]
        while len(pr) < 2:
            cands = [v for v in init if v not in pr]
            # nearest available by ready time for this alert
            best = min(cands, key=lambda v: ready_from(init[v]["pos"],
                                                       CLOUDS[a])[0])
            pr.append(best)
        asg[a] = tuple(pr)

    # ---- new alert: two earliest chains
    if with_new is not None:
        cl = cloud_for(with_new)
        scored = []
        for v in init:
            # chain end of the already assigned pending base tasks
            t = init[v]["t_avail"]
            pos = init[v]["pos"]
            for a in BASE_ORDERS.get(v, []):
                if a in asg and v in asg[a]:
                    st = BASE_ST.get((v, a), nearest_station(pos, CLOUDS[a]))
                    az, el, sl = L.station_times(st, CLOUDS[a]["tgt"],
                                                  CLOUDS[a]["h"])
                    t += L.travel_time(pos, st) + sl + L.OBS_LEN + sl
                    pos = st
            rd, st = ready_from(pos, cl)
            scored.append((t + rd, v, st))
        scored.sort(key=lambda z: (z[0], z[1]))
        pair = tuple(sorted(z[1] for z in scored[:2]))
        asg["T4"] = pair

    # ---- orders: original pending tasks, then replacements, then T4
    orders = {v: [] for v in init}
    for v in init:
        for a in BASE_ORDERS.get(v, []):
            if a in asg and v in asg[a]:
                orders[v].append(a)
    for a in pending:
        if a == "T4":
            continue
        for v in asg[a]:
            if a not in orders[v] and not (v in BASE_ASG[a]
                                           and a in BASE_ORDERS.get(v, [])):
                orders[v].append(a)
    if with_new is not None:
        for v in asg["T4"]:
            orders[v].append("T4")

    # ---- stations: keep original stations; nearest for new tasks
    stations = {}
    for v in init:
        pos = init[v]["pos"]
        for a in orders[v]:
            if v in BASE_ASG.get(a, ()) and (v, a) in BASE_ST:
                st = BASE_ST[(v, a)]
            else:
                cl = cloud_for(with_new) if a == "T4" else CLOUDS[a]
                st = nearest_station(pos, cl)
            stations[(v, a)] = st
            pos = st

    L.ALERTS4 = {}
    for a in pending:
        cl = cloud_for(with_new) if a == "T4" else CLOUDS[a]
        L.ALERTS4[a] = (cl["tgt"], cl["h"])

    obj, starts, _ready, ok = L.simulate_init(asg, orders, stations, init,
                                               pending)
    N = 3 + (1 if with_new is not None else 0)
    k = 1 + len(started)
    if ok:
        k += sum(1 for a in pending if a in starts)
    eta = k / N
    all_starts = dict(base_starts)
    if ok:
        all_starts.update(starts)
    if k == N and max(all_starts.values()) <= 60.0 + 1e-9:
        t_last = float(max(all_starts.values()))
    else:
        t_last = 60.0
    return {"k": k, "N": N, "eta": eta, "t_last": t_last,
            "feasible": bool(ok), "starts": {a: round(v, 3)
                                             for a, v in all_starts.items()},
            "pending": pending, "started": started,
            "asg": {a: [v + 1 for v in asg[a]] for a in asg},
            "orders": {f"V{v+1}": orders[v] for v in orders},
            "stations": {f"V{v+1}": {a[1]: [round(x, 3) for x in st]
                                     for a, st in stations.items() if a[0] == v}
                         for v in init}}


# ---------------------------------------------------------------- scenarios
def failed_idx(s):
    return None if "failed" not in s else int(s["failed"][1:]) - 1


def t_plan_of(s, default=5.0):
    return default if "t_rec" not in s else float(s["t_rec"])


cases = []
for group, entries in (("A_new", Q4["scen_new"]), ("B_fail", Q4["scen_fail"]),
                       ("C_out", Q4["scen_out"]),
                       ("D_fail_out", Q4["scen_fail_out"]),
                       ("E_new_fail", Q4["scen_new_fail"]),
                       ("F_new_out", Q4["scen_new_out"]),
                       ("G_triple", Q4["scen_triple"])):
    for s in entries:
        key = s.get("key")
        fv = failed_idx(s)
        t_p = t_plan_of(s)
        rep = build_repair(t_p, failed=fv, with_new=key)
        cases.append({"group": group, "key": key,
                      "failed": s.get("failed"), "t_rec": s.get("t_rec"),
                      "keep": s["keep"], "resched": s["resched"],
                      "repair": rep})
        print(f"{group} {key or ''} {s.get('failed','') } "
              f"t={t_p:g}: keep({s['keep']['eta']:.2f},"
              f"{s['keep']['t_last']:.1f}) "
              f"repair({rep['eta']:.2f},{rep['t_last']:.1f}) "
              f"resched({s['resched']['eta']:.2f},"
              f"{s['resched']['t_last']:.1f})")


def counts(a_key, b_key, tol=0.01, cs=None):
    """Compare b vs a; t_last differences below 0.01 s count as ties."""
    cs = cases if cs is None else cs
    imp = tie = deg = 0
    t_imp = t_tie = t_worse = 0
    for c in cs:
        aa, bb = c[a_key], c[b_key]
        if bb["eta"] > aa["eta"] + 1e-9:
            imp += 1
        elif bb["eta"] < aa["eta"] - 1e-9:
            deg += 1
        else:
            tie += 1
            if bb["t_last"] < aa["t_last"] - tol:
                t_imp += 1
            elif bb["t_last"] > aa["t_last"] + tol:
                t_worse += 1
            else:
                t_tie += 1
    return {"eta_improve": imp, "eta_tie": tie, "eta_degrade": deg,
            "tlast_improve_within_tie": t_imp,
            "tlast_worse_within_tie": t_worse,
            "tlast_equal_within_tie": t_tie}


# ---- sensitivity: require >= 4 s of synchronized observation for completion
# The problem's lock rule counts a started observation as served.  T1 starts
# at 1.607 s and is interrupted at the t=5 s failure, after 3.393 s; a stricter
# completion criterion therefore fails T1 in the eight scenarios with a V3 or
# V5 failure.  T1 cannot be rescheduled (it has started), so k drops by 1.
T1_ELAPSED = 5.0 - base_starts["T1"]
THRESHOLD = 4.0
assert T1_ELAPSED < THRESHOLD


def strict_policy(p):
    k2 = p["k"] - 1
    eta2 = k2 / p["N"]
    tlast2 = 60.0 if k2 < p["N"] else p["t_last"]
    return {**p, "k": k2, "eta": eta2, "t_last": tlast2}


strict_cases = []
affected = []
for c in cases:
    if c.get("failed") in ("V3", "V5"):
        c2 = dict(c)
        for pol in ("keep", "repair", "resched"):
            c2[pol] = strict_policy(c[pol])
        strict_cases.append(c2)
        affected.append({"group": c["group"], "failed": c["failed"],
                         "t_rec": c.get("t_rec"),
                         "keep": round(c2["keep"]["eta"], 3),
                         "repair": round(c2["repair"]["eta"], 3),
                         "resched": round(c2["resched"]["eta"], 3)})
    else:
        strict_cases.append(c)

out = {
    "n": len(cases),
    "repair_vs_keep": counts("keep", "repair"),
    "resched_vs_keep": counts("keep", "resched"),
    "resched_vs_repair": counts("repair", "resched"),
    "mean_tlast": {
        "keep": float(np.mean([c["keep"]["t_last"] for c in cases])),
        "repair": float(np.mean([c["repair"]["t_last"] for c in cases])),
        "resched": float(np.mean([c["resched"]["t_last"] for c in cases])),
    },
    "completion_sensitivity": {
        "threshold_s": THRESHOLD,
        "t1_start_s": round(float(base_starts["T1"]), 3),
        "t1_elapsed_at_5s": round(float(T1_ELAPSED), 3),
        "note": ("The problem's lock rule counts a started observation as "
                 "served; under a >=4 s (or full 5 s) synchronized-observation "
                 "criterion T1 is incomplete in the V3/V5 failure scenarios "
                 "and cannot be rescheduled; k drops by 1."),
        "affected": affected,
        "eta1_count": {
            "main": {p: sum(1 for c in cases if abs(c[p]["eta"] - 1) < 1e-9)
                     for p in ("keep", "repair", "resched")},
            "strict": {p: sum(1 for c in strict_cases
                              if abs(c[p]["eta"] - 1) < 1e-9)
                       for p in ("keep", "repair", "resched")},
        },
        "repair_vs_keep": counts("keep", "repair", cs=strict_cases),
        "resched_vs_repair": counts("repair", "resched", cs=strict_cases),
    },
    "cases": cases,
}
with open(os.path.join(RES_DIR, "q4_repair.json"), "w",
          encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2, default=float)

lines = ["# Problem 4 simple-repair baseline", "",
         f"n = {len(cases)} scenarios", "",
         "| comparison | eta improve | eta tie | eta degrade | "
         "t_last improve (eta tie) | t_last worse (eta tie) |",
         "|---|---|---|---|---|---|"]
for name, c in (("repair vs keep", out["repair_vs_keep"]),
                ("resched vs keep", out["resched_vs_keep"]),
                ("resched vs repair", out["resched_vs_repair"])):
    lines.append(f"| {name} | {c['eta_improve']} | {c['eta_tie']} | "
                 f"{c['eta_degrade']} | {c['tlast_improve_within_tie']} | "
                 f"{c['tlast_worse_within_tie']} |")
lines += ["", "Mean t_last: keep {:.2f} s, repair {:.2f} s, resched {:.2f} s"
          .format(out["mean_tlast"]["keep"], out["mean_tlast"]["repair"],
                  out["mean_tlast"]["resched"]), ""]
cs = out["completion_sensitivity"]
lines += ["## Completion-rule sensitivity", "",
          f"T1 starts at {cs['t1_start_s']:.3f} s and is interrupted at the "
          f"5 s failure after {cs['t1_elapsed_at_5s']:.3f} s; a >= "
          f"{cs['threshold_s']:.0f} s synchronized-observation criterion "
          f"therefore fails T1 in {len(cs['affected'])} scenarios.",
          "", "| policy | eta=1 count (main) | eta=1 count (strict) |",
          "|---|---|---|"]
for p in ("keep", "repair", "resched"):
    lines.append(f"| {p} | {cs['eta1_count']['main'][p]} | "
                 f"{cs['eta1_count']['strict'][p]} |")
lines += ["", f"Strict repair vs keep: {cs['repair_vs_keep']}", "",
          f"Strict resched vs repair: {cs['resched_vs_repair']}", ""]
for a in cs["affected"]:
    lines.append(f"- {a['group']} {a['failed']} t_rec={a['t_rec']}: "
                 f"keep {a['keep']:.3f}, repair {a['repair']:.3f}, "
                 f"resched {a['resched']:.3f}")
with open(os.path.join(RES_DIR, "q4_repair.md"), "w",
          encoding="utf-8") as f:
    f.write("\n".join(lines))
print("\n".join(lines))
