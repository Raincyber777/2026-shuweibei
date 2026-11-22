# -*- coding: utf-8 -*-
"""Consistency check: driving-leg lengths of the delivered schemes vs Q3
budget s_max = 66.92 m (P(|dpsi|<=5deg) >= 0.95 driving-distance limit)."""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.dirname(os.path.dirname(HERE))
SPEED = 3.0
S_MAX = 66.9223

VEH_STARTS = {1: (15.0, 14.0), 2: (88.0, 10.0), 3: (14.0, 86.0),
              4: (88.0, 68.0), 5: (50.0, 93.0)}

# ---- Q2(2) delivered scheme: legs start -> station_1 -> station_2 ----------
Q2DIR = os.path.dirname(HERE)
with open(os.path.join(Q2DIR, "results", "q2b_results.json"), encoding="utf-8") as f:
    q2 = json.load(f)
opt = q2["optimized"]
asg = {a: tuple(v) for a, v in opt["assignment"].items()}   # 1-based pairs
sta = opt["stations"]                                       # V -> alert -> [x, y]
print("optimized keys:", list(opt.keys()))
print("stations sample:", list(sta.items())[:3])
orders = opt.get("orders", {})
print("orders:", orders)

max_leg2 = 0.0
detail2 = []
for v in range(1, 6):
    name = f"V{v}"
    seq = [a for a in orders.get(name, [])]
    pos = VEH_STARTS[v]
    for a in seq:
        nxt = sta[name][a]
        d = math.hypot(nxt[0] - pos[0], nxt[1] - pos[1])
        detail2.append((name, a, round(d, 2)))
        max_leg2 = max(max_leg2, d)
        pos = nxt
print("Q2 legs (vehicle, alert, metres):", detail2)
print(f"Q2 max leg = {max_leg2:.2f} m  vs  s_max = {S_MAX} m  ->",
      "OK" if max_leg2 <= S_MAX else "VIOLATION")

# ---- Q4: max travel segment over baseline + all 74 scenarios --------------
with open(os.path.join(B, "第四题", "results", "q4_results.json"),
          encoding="utf-8") as f:
    q4 = json.load(f)

worst = [0.0, None]


def scan(node, path):
    if isinstance(node, list) and len(node) >= 3 and node[0] == "travel" \
            and isinstance(node[1], (int, float)) \
            and isinstance(node[2], (int, float)):
        d = (node[2] - node[1]) * SPEED
        if d > worst[0]:
            worst[0] = d
            worst[1] = path
    elif isinstance(node, list):
        for i, x in enumerate(node):
            scan(x, f"{path}[{i}]")
    elif isinstance(node, dict):
        for k, x in node.items():
            scan(x, f"{path}.{k}")


scan(q4, "$")
print(f"Q4 max travel leg = {worst[0]:.2f} m at {worst[1]}  vs  s_max = "
      f"{S_MAX} m  ->", "OK" if worst[0] <= S_MAX else "VIOLATION")
