# -*- coding: utf-8 -*-
"""Diagnostic: scan stored Q4 segments for timeline inconsistencies."""
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(BASE, "results", "q4_results.json"), encoding="utf-8") as f:
    R4 = json.load(f)

BLOCKS = ("scen_new", "scen_fail", "scen_out", "scen_fail_out",
          "scen_new_fail", "scen_new_out", "scen_triple")


def check_segs(segs):
    """Return list of (vehicle, issue, detail)."""
    out = []
    for v, segs_v in segs.items():
        prev_end = -1.0
        for seg in segs_v:
            kind, t0, t1 = seg[0], float(seg[1]), float(seg[2])
            if t1 < t0 - 1e-9:
                out.append((v, f"negative {kind}", f"{t0:.3f}->{t1:.3f}"))
            if t0 < prev_end - 1e-9:
                out.append((v, f"overlap before {kind}",
                            f"seg starts {t0:.3f} < prev end {prev_end:.3f}"))
            prev_end = max(prev_end, t1)
    return out


n_scen = 0
bad_scen = 0
neg_wait = 0
all_rows = []
for b in BLOCKS:
    for s in R4[b]:
        n_scen += 1
        segs = s["resched"].get("segs") or {}
        issues = check_segs(segs)
        nw = sum(1 for i in issues if i[1].startswith("negative wait"))
        if nw:
            neg_wait += 1
        if issues:
            bad_scen += 1
            key = s.get("key") or s.get("failed") or "?"
            all_rows.append((b, key, nw, len(issues), issues[:4]))

print(f"scenarios={n_scen} with_issues={bad_scen} with_negative_wait={neg_wait}")
for row in all_rows:
    print(row)

# baseline timeline check
bsegs = R4["baseline"]["segments"]
print("baseline issues:", check_segs(bsegs))

# representative reschedules
for k, v in R4["representative"].items():
    if isinstance(v, dict) and "segs" in v:
        iss = check_segs(v["segs"])
        print(k, "issues:", iss[:6], "n=", len(iss))
