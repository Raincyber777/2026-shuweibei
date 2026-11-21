# -*- coding: utf-8 -*-
"""Smoke test for the Q4 machinery: replay + one reschedule call."""
import json
import os
import sys
import time

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
recs, starts = L.replay_baseline(asg, orders, st)
print("replay starts:", {a: round(starts[a], 3) for a in ("T1", "T2", "T3")})
for a in ("T1", "T2", "T3"):
    assert abs(starts[a] - Q2["optimized"]["alert_starts"][a]) < 1e-6
print("replay matches q2b OK")

snap = L.snapshot(recs, 5.0)
for v in range(5):
    s = snap[v]
    print(f"  V{v+1}@t=5: t_avail={s['t_avail']:.3f} pos=({s['pos'][0]:.2f},"
          f"{s['pos'][1]:.2f}) att=({s['att'][0]:.1f},{s['att'][1]:.1f}) "
          f"locked={s['locked_until']:.3f}")

tgt, h, _ = L.alert_params(0.0, 40.0, 50.0)
t0 = time.time()
cloud4 = L.build_cloud(tgt[0], tgt[1], h, 0.2)
print(f"T4 cloud built in {time.time()-t0:.1f}s, area={cloud4['area']:.1f} m^2, "
      f"sub={len(cloud4['sub'])}")
clouds = {"T2": L.build_cloud(*TARGETS["T2"], TARGET_H["T2"], 0.1),
          "T3": L.build_cloud(*TARGETS["T3"], TARGET_H["T3"], 0.1),
          "T4": cloud4}
L.ALERTS4 = {a: (clouds[a]["tgt"], clouds[a]["h"]) for a in clouds}
pending = ["T2", "T3", "T4"]
init = {v: dict(t_avail=s["t_avail"], pos=s["pos"], att=s["att"])
        for v, s in snap.items()}
t0 = time.time()
best, n_comb = L.optimize_resched(None, {}, init, clouds, pending)
print(f"optimize: {n_comb} structures in {time.time()-t0:.1f}s")
obj, starts_r, _r, ok = L.simulate_init(best[1], best[2], best[3], init,
                                        pending)
print("resched obj (max pending start):", round(obj, 3), "starts:",
      {a: round(v, 3) for a, v in starts_r.items()})
print("assignment:", {a: [v + 1 for v in best[1][a]] for a in pending})
segs = L.gantt_init(best[1], best[2], best[3], init, starts_r,
                    {a: L.ALERTS4[a] for a in pending})
for v in range(5):
    if segs.get(v):
        print(f"  V{v+1}: " + " | ".join(
            f"{s[0]}[{s[1]:.1f}-{s[2]:.1f}]" for s in segs[v]))
