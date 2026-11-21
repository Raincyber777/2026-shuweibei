# -*- coding: utf-8 -*-
"""Reproduce th45_R50 k-accounting with introspection."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import q4_lib4 as L
from q2_lib import TARGETS, TARGET_H

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(BASE, "..", "第二题", "results", "q2b_results.json"),
          encoding="utf-8") as f:
    Q2 = json.load(f)
asg = {a: tuple(v) for a, v in Q2["optimized"]["assignment"].items()}
orders = {int(k[1:]) - 1: v for k, v in Q2["optimized"]["orders"].items()}
st = {(int(k[1:]) - 1, a): tuple(p)
      for k, d in Q2["optimized"]["stations"].items() for a, p in d.items()}
recs, base_starts = L.replay_baseline(asg, orders, st)
print("base_starts:", {a: round(v, 3) for a, v in base_starts.items()})

t_plan = 5.0
snap = L.snapshot(recs, t_plan)
init = {v: dict(t_avail=s["t_avail"], pos=s["pos"], att=s["att"])
        for v, s in snap.items() if v is not None}
started = [a for a in ("T2", "T3") if base_starts[a] < t_plan]
pending = [a for a in ("T2", "T3") if a not in started] + ["T4"]
print("started:", started, "pending:", pending)

tgt, h, _ = L.alert_params(45.0, 50.0, 50.0)
clouds = {"T2": L.build_cloud(*TARGETS["T2"], TARGET_H["T2"], 0.1),
          "T3": L.build_cloud(*TARGETS["T3"], TARGET_H["T3"], 0.1),
          "T4": L.build_cloud(tgt[0], tgt[1], h, 0.2)}
L.ALERTS4 = {a: (clouds[a]["tgt"], clouds[a]["h"]) for a in pending}
best, n_comb = L.optimize_resched(None, {}, init, clouds, pending)
print("n_comb:", n_comb, "best obj:", None if best is None else round(best[0], 3))
if best is not None:
    obj, asg_r, orders_r, st_r = best
    obj, starts, _r, ok = L.simulate_init(asg_r, orders_r, st_r, init, pending)
    print("ok:", ok, "starts keys:", list(starts.keys()))
    k = 1 + len(started) + sum(1 for a in pending if a in starts)
    print("k =", k, " eta =", k / 4)
