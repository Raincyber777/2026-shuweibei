# -*- coding: utf-8 -*-
"""Headline-number consistency check: paper <-> numbers.md <-> JSON.

Each item lists acceptable formatted strings (any one must appear in the paper
and in numbers.md).  JSON integrity is checked separately by loading the files
and asserting the key fields exist and are finite.

Run:  python check_consistency.py
Exit code 0 = all checks passed.
"""
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PAPER = open(os.path.join(ROOT, "数维杯B题_中文初稿.md"), encoding="utf-8").read()
NUM = open(os.path.join(ROOT, "numbers.md"), encoding="utf-8").read()

F = ["第一题/results/q1_results.json", "第一题/results/q1_area_estimators.json",
     "第一题/results/q1_metric_compare.json", "第二题/results/q2a_results.json",
     "第二题/results/q2b_results.json", "第二题/results/q2b_precision.json",
     "第三题/results/q3_results.json", "第四题/results/q4_results.json",
     "第四题/results/q4_robust.json"]


def load(fn):
    with open(os.path.join(ROOT, fn), encoding="utf-8") as f:
        return json.load(f)


R1, R1A, R1M, R2A, R2B, R2P, R3, R4, R4R = [load(f) for f in F]

# (label, [acceptable strings], [must appear in numbers.md strings])
ITEMS = [
    ("Q1 T-prime", ["84.6410", "(84.6410,70.0000)", "(84.6410, 70.0000)"], ["84.6410"]),
    ("Q1 r_min", ["7.5821"], ["7.5821"]),
    ("Q1 Q*", ["0.1319"], ["0.1319"]),
    ("Q1 p*", ["88.8753", "76.2895"], ["88.8753", "76.2895"]),
    ("Q1 m*/p* margin", ["9.6746", "9.6247"], ["9.6746", "9.6247"]),
    ("Q1 arc", ["283.85", "76.15", "160.75", "236.89"], ["283.85", "76.15"]),
    ("Q1 areas", ["5610.4", "5608.5", "5614.9", "5628.7"],
     ["5610.4", "5608.5", "5614.9", "5628.7"]),
    ("Q1 Q2 metric", ["0.0885", "0.01146"], ["0.0885", "0.01146"]),
    ("Q2(1) G*/DRMS", ["5.8188", "0.1016", "0.2486"], ["5.8188", "0.1016", "0.2486"]),
    ("Q2(1) baseline", ["8.2290", "5.11", "13.61"], ["8.2290"]),
    ("Q2(1) V2 pair", ["8.9678"], ["8.9678"]),
    ("Q2(1) backoff", ["7.0144", "0.1224", "20.5%"], ["7.0144", "0.1224"]),
    ("Q2(2) starts", ["1.607", "6.994", "10.355", "20.968"], ["1.607", "6.994", "10.355", "20.968"]),
    ("Q2(2) gap", ["10.613", "−50.6%"], ["10.613", "−50.6%"]),
    ("Q2(2) robust", ["10.837", "3.414", "18.956"], ["10.837", "3.414", "18.956"]),
    ("Q2(2) gamma", ["19.34", "85.08", "127.39"], ["19.34", "85.08", "127.39"]),
    ("Q2(2) G", ["176.67", "67.93", "81.32"], ["176.67", "67.93", "81.32"]),
    ("Q2(2) DRMS", ["3.084", "1.186", "1.419"], ["3.084", "1.186", "1.419"]),
    ("Q2(2) constrained", ["30.12", "116.68", "2.036", "3.746", "12.983", "2.629", "25.38%"],
     ["30.12", "116.68", "2.036", "12.983", "2.629", "25.38%"]),
    ("Q2(2) R95 anisotropy", ["46:1", "10.56", "6.87"], ["46:1", "10.56", "6.87"]),
    ("Q3 k_loc", ["1.432394"], ["1.432394"]),
    ("Q3 sigma_psi", ["2.551067"], ["2.551067"]),
    ("Q3 s_max", ["66.92", "1.6384"], ["66.92", "1.6384"]),
    ("Q3 P80", ["0.91538"], ["0.91538"]),
    ("Q3 ab", ["0.0204806", "0.0167306", "0.0384"], ["0.0204806"]),
    ("Q3 shares", ["15.6", "54.0", "30.4", "71.3", "18.4", "10.3", "88.1", "7.6", "4.3"],
     ["15.6", "54.0", "30.4"]),
    ("Q3 residual", ["19.907", "0.1293", "0.2%"], ["19.907", "0.1293"]),
    ("Q3 exact", ["66.84", "0.94980", "1.6367"], ["66.84", "0.94980", "1.6367"]),
    ("Q4 baseline", ["1.607", "6.994", "10.355"], ["1.607", "6.994", "10.355"]),
    ("Q4 counts", ["67/74", "7 个持平", "0 个劣化"], ["67/7/0"]),
    ("Q4 reps", ["11.17", "16.77", "25.01"], ["11.17", "16.77", "25.01"]),
    ("Q4 fail-out", ["21.01", "25.08", "35.08"], ["21.01", "25.08", "35.08"]),
    ("Q4 new range", ["14.39", "16.77"], ["14.39", "16.77"]),
    ("Q4 piecewise", ["4.07", "10.0", "21.01"], ["4.07", "10.0", "21.01"]),
    ("Q4 robust", ["10.90", "10.35", "12.77", "22.77", "32.77", "14.57", "16.45"],
     ["11.17", "15.87", "25.01", "14.57", "16.45"]),
]

# dynamic Q4 values from the final JSON
v4 = R4["representative"]["resched_failV4"]["t_last"]
tri = R4["representative"]["resched_triple"]["t_last"]
th0 = [x for x in R4["scen_new"] if x["key"] == "th0_R30"][0]["resched"]["t_last"]
_dyn_ok = (f"{v4:.2f}" == "11.17" and f"{tri:.2f}" in PAPER
           and f"{th0:.2f}" in PAPER)
for f in F:
    if not os.path.exists(os.path.join(ROOT, f)):
        print("MISSING FILE", f)
        sys.exit(2)

fails = []
for label, p_opts, n_opts in ITEMS:
    pm = not any(x in PAPER for x in p_opts)
    nm = not any(x in NUM for x in n_opts)
    if pm or nm:
        fails.append((label, pm, nm))
        print(f"FAIL {label:22s} paper_missing={pm} numbers_missing={nm}")
    else:
        print(f"OK   {label:22s}")

# JSON integrity / cross-file equality
assert abs(R1["r_min_closed_form"] - 7.582060170463998) < 1e-9
assert abs(R2A["certificate"]["G_star_m"] - 5.818790363379347) < 1e-9
assert abs(R2B["optimized"]["objective_s"] - 10.354889235621954) < 1e-9
assert abs(R3["s_max_m"] - 66.92229923908131) < 1e-6
assert abs(R4["baseline"]["starts"]["T3"] - 10.355) < 1e-3
assert all(math.isfinite(x["resched"]["t_last"]) for b in
           ("scen_new", "scen_fail", "scen_out", "scen_fail_out",
            "scen_new_fail", "scen_new_out", "scen_triple") for x in R4[b])
assert R4["scenario_design"]["counts"] == {
    "A_new": 24, "B_fail": 5, "C_outage": 3, "D_fail_out": 15,
    "E_new_fail": 6, "F_new_out": 9, "G_triple": 12}
assert not R4R["audit"]["issues"]
assert _dyn_ok, "Q4 representative dynamic values do not match the paper"

# area cross-file equality
assert abs(R1A["estimators"]["h=0.1"]["midpoint_area_m2"]
           - R1["grid"]["area_m2"]) < 1e-9
assert abs(R1A["estimators"]["h=0.05"]["midpoint_area_m2"] - 5608.5275) < 1e-9

print()
if fails:
    print(f"{len(fails)} ITEM(S) FAILED")
    sys.exit(1)
print("ALL HEADLINE CHECKS PASSED")
