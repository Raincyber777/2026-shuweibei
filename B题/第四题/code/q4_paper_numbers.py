# -*- coding: utf-8 -*-
"""Print every number the paper quotes for Problem 4, from q4_results.json."""
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = json.load(open(os.path.join(BASE, "results", "q4_results.json"),
                   encoding="utf-8"))
BLOCKS = ("scen_new", "scen_fail", "scen_out", "scen_fail_out",
          "scen_new_fail", "scen_new_out", "scen_triple")
print("baseline starts:", R["baseline"]["starts"])
n_tot = n_eta = n_tie = n_worse = 0
for b in BLOCKS:
    ge = gt = eq = wo = 0
    for s in R[b]:
        n_tot += 1
        k, r = s["keep"], s["resched"]
        if r["eta"] > k["eta"] + 1e-9:
            ge += 1
        elif r["eta"] < k["eta"] - 1e-9:
            wo += 1
        elif r["t_last"] < k["t_last"] - 1e-9:
            gt += 1
        else:
            eq += 1
    n_eta += ge
    n_tie += gt + eq
    n_worse += wo
    print(f"{b}: eta_gain={ge} tlast_gain={gt} tie={eq} worse={wo}")
print(f"TOTAL: eta_gain={n_eta}/{n_tot}  tie={n_tie}  worse={n_worse}")

# representative values
new = {s["key"]: s for s in R["scen_new"]}
for k in ("th0_R30",):
    r = new[k]["resched"]
    print(k, "resched", r["eta"], r["t_last"], r["starts"])
fail = {s["failed"]: s for s in R["scen_fail"]}
for k in ("V1", "V2", "V3", "V4", "V5"):
    print("fail", k, "keep", fail[k]["keep"]["eta"], fail[k]["keep"]["t_last"],
          "| resched", fail[k]["resched"]["eta"], fail[k]["resched"]["t_last"])
fo = {(s["failed"], s["t_rec"]): s for s in R["scen_fail_out"]}
for t in (10.0, 20.0, 30.0):
    s = fo[("V1", t)]
    print(f"V1 out{t:g}: keep {s['keep']['t_last']:.2f} -> "
          f"resched {s['resched']['t_last']:.3f}")
rep = R["representative"]
print("rep failV4:", rep["resched_failV4"]["resched"] if False else
      rep["resched_failV4"]["eta"], rep["resched_failV4"]["t_last"],
      rep["resched_failV4"]["starts"])
print("rep triple:", rep["resched_triple"]["eta"],
      rep["resched_triple"]["t_last"], rep["resched_triple"]["starts"])
print("triple keep:", rep["keep_triple"]["eta"], rep["keep_triple"]["t_last"])
print("reps:", R["scenario_design"]["reps"])
tls = [s["resched"]["t_last"] for s in R["scen_new"]]
print(f"new-alert resched t_last range: {min(tls):.2f} - {max(tls):.2f}")
