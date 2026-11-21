# -*- coding: utf-8 -*-
"""Standalone timeline audit of the delivered q4_results.json."""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
B = r"e:\2026数维杯\2026-shuweibei\B题\第四题"
d = json.load(open(B + r"\results\q4_results.json", encoding="utf-8"))


def audit_segs(segs):
    bad = []
    for v, ss in segs.items():
        prev_end = -1.0
        for x in ss:
            typ, t0, t1 = x[0], float(x[1]), float(x[2])
            if t1 < t0 - 1e-9:
                bad.append((v, typ, "negative", t0, t1))
            elif t0 < prev_end - 1e-9:
                bad.append((v, typ, "overlap", t0, t1, prev_end))
            prev_end = max(prev_end, t1)
    return bad


blocks = ("scen_new", "scen_fail", "scen_out", "scen_fail_out",
          "scen_new_fail", "scen_new_out", "scen_triple")
n_checked, all_bad = 0, []
for b in blocks:
    for s in d[b]:
        segs = s["resched"].get("segs") or {}
        if segs:
            n_checked += 1
            all_bad += [(b, s.get("key", s.get("failed", "")), *x)
                        for x in audit_segs(segs)]
for k in ("resched_failV4", "resched_triple"):
    segs = d["representative"][k].get("segs") or {}
    if segs:
        n_checked += 1
        all_bad += [(k, "rep", *x) for x in audit_segs(segs)]
print(f"audited {n_checked} resched timelines: {len(all_bad)} bad segments")
for x in all_bad[:12]:
    print("  ", x)
