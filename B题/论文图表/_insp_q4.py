# -*- coding: utf-8 -*-
"""Inspect q4_results.json scenario structure (one-off)."""
import io
import json
import os

P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "第四题", "results", "q4_results.json")
d = json.load(io.open(P, encoding="utf-8"))
print("top keys:", [k for k in d.keys() if not k.startswith("_")])
for k in d:
    if k.startswith("scen") and isinstance(d[k], list):
        print(k, "len:", len(d[k]))
        s = d[k][0]
        print("  scenario keys:", list(s.keys()))
        for kk, vv in s.items():
            if isinstance(vv, dict):
                print("  ", kk, "->", list(vv.keys())[:14])
        break
