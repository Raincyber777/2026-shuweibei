# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
d = json.load(open("q2b_results.json", encoding="utf-8"))
op = d["optimized"]
print("assignment:", op["assignment"])
print("orders:", op["orders"])
print("starts:", op["alert_starts"])
print("obj:", op["objective_s"])
for t in d["top5_structures"][:3]:
    print("top:", t["obj_s"], t["sum_starts_s"], t["assignment"], t["orders"],
          t["starts"])
