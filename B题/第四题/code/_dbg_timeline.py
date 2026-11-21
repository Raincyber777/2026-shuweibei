# -*- coding: utf-8 -*-
"""Reproduce one Q4 reschedule (th0_R30) and dump the fixed-point state."""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import q4_lib4 as L
from q2_lib import TARGETS, TARGET_H, VEHICLES

BASE = os.path.dirname(HERE)
with open(os.path.join(BASE, "..", "第二题", "results", "q2b_results.json"),
          encoding="utf-8") as f:
    Q2 = json.load(f)
BASE_ASG = {a: tuple(vv - 1 for vv in v)
            for a, v in Q2["optimized"]["assignment"].items()}
BASE_ORDERS = {int(k[1:]) - 1: v for k, v in Q2["optimized"]["orders"].items()}
BASE_ST = {(int(k[1:]) - 1, a): tuple(p)
           for k, d in Q2["optimized"]["stations"].items() for a, p in d.items()}
recs, base_starts = L.replay_baseline(BASE_ASG, BASE_ORDERS, BASE_ST)
CLOUDS_BASE = {"T2": L.build_cloud(*TARGETS["T2"], TARGET_H["T2"], 0.1),
               "T3": L.build_cloud(*TARGETS["T3"], TARGET_H["T3"], 0.1)}
key = "th0_R30"
tgt, h, _ = L.alert_params(0.0, 30.0, 50.0)
cloud4 = L.build_cloud(tgt[0], tgt[1], h, 0.2)
CLOUDS_NEW = {key: cloud4}
snap = L.snapshot(recs, 5.0)
init = {v: dict(t_avail=s["t_avail"], pos=s["pos"], att=s["att"],
                unobserved=s["unobserved"])
        for v, s in snap.items()}
pending = ["T2", "T3", "T4"]
L.ALERTS4 = {"T2": (TARGETS["T2"], TARGET_H["T2"]),
             "T3": (TARGETS["T3"], TARGET_H["T3"]),
             "T4": (cloud4["tgt"], cloud4["h"])}
clouds = {"T2": CLOUDS_BASE["T2"], "T3": CLOUDS_BASE["T3"], "T4": cloud4}
best, n_comb = L.optimize_resched(None, {}, init, clouds, pending)
obj, asg_r, orders_r, st_r = best
obj, starts, ready, ok = L.simulate_init(asg_r, orders_r, st_r, init, pending)
print("ok", ok, "obj", obj)
print("asg", asg_r)
print("init att", {v: init[v]["att"] for v in init})
for (v, a) in sorted(st_r):
    if v == 0:
        az, el, sl = L.station_times(st_r[(v, a)], TARGETS[a] if a in ("T2","T3") else L.ALERTS4[a][0], TARGET_H[a] if a in ("T2","T3") else L.ALERTS4[a][1])
        print("V1 station", a, st_r[(v, a)], "az", round(az,3), "el", round(el,3), "slew", round(sl,4))
print("orders", orders_r)
print("starts", {a: round(v, 4) for a, v in starts.items()})
print("ready", {(k, a): round(v, 5) for (k, a), v in ready.items()})
segs = L.gantt_init(asg_r, orders_r, st_r, init, starts,
                    {a: L.ALERTS4[a] if a == "T4" else (TARGETS[a], TARGET_H[a])
                     for a in pending}, ready)
for v in sorted(segs):
    print("V", v + 1)
    for s in segs[v]:
        print("   ", s)
