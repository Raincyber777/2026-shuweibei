# -*- coding: utf-8 -*-
"""Verify every number quoted in the Chinese draft against delivered JSONs."""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
B = r"e:\2026数维杯\2026-shuweibei\B题"
q2a = json.load(open(B + r"\第二题\results\q2a_results.json", encoding="utf-8"))
q2b = json.load(open(B + r"\第二题\results\q2b_results.json", encoding="utf-8"))
q3 = json.load(open(B + r"\第三题\results\q3_results.json", encoding="utf-8"))
q4 = json.load(open(B + r"\第四题\results\q4_results.json", encoding="utf-8"))
q4r = json.load(open(B + r"\第四题\results\q4_robust.json", encoding="utf-8"))

fails, oks = [], []


def chk(label, got, want, tol=0.01):
    ok = abs(got - want) <= tol
    (oks if ok else fails).append((label, got, want))


# ---- Q4 claims in the draft ----
fo = {(s["failed"], s["t_rec"]): s["resched"]["t_last"]
      for s in q4["scen_fail_out"]}
chk("draft: V1 fault out10", fo[("V1", 10.0)], 21.01, 0.01)
chk("draft: V1 fault out20", fo[("V1", 20.0)], 25.08, 0.01)
chk("draft: V1 fault out30", fo[("V1", 30.0)], 35.08, 0.01)
chk("draft: V2 fault out10", fo[("V2", 10.0)], 12.77, 0.01)
chk("draft: V2 fault out20", fo[("V2", 20.0)], 22.77, 0.01)
chk("draft: V2 fault out30", fo[("V2", 30.0)], 32.77, 0.01)
sn = {s["key"]: s["resched"]["t_last"] for s in q4["scen_new"]}
chk("draft: th0_R30 t_last", sn["th0_R30"], 16.77, 0.01)
vals = sorted(sn.values())
chk("draft: A range min", vals[0], 14.39, 0.01)
chk("draft: A range max", vals[-1], 16.77, 0.01)
bf = {s["failed"]: (s["resched"]["t_last"], s["resched"]["eta"]) for s in q4["scen_fail"]}
chk("draft: V1/V4 fail t_last", bf["V1"][0], 11.17, 0.01)
chk("draft: V2 fail t_last", bf["V2"][0], 10.90, 0.01)
chk("draft: V3 fail t_last", bf["V3"][0], 10.90, 0.01)
chk("draft: V5 fail t_last", bf["V5"][0], 10.35, 0.01)
chkb = all(v[1] == 1.0 for v in bf.values())
oklist = chkb and True
chk("draft: V2/V3 vs V1/V4 pairs", bf["V2"][0], bf["V3"][0], 0.01)
chk("draft: V1/V4 pair", bf["V1"][0], bf["V4"][0], 0.01)
rep = q4["scenario_design"]["reps"]
tr = [s for s in q4["scen_triple"]
      if s["key"] == rep["mid"] and s["failed"] == "V4"
      and s["t_rec"] == 10.0][0]
chk("draft: triple mid t_last", tr["resched"]["t_last"], 25.01, 0.01)
chk("draft: triple keep eta", tr["keep"]["eta"], 0.5, 1e-9)

# ---- Q2 claims ----
v2p = [r for r in q2a["pair_table"] if r["pair"] == "V1+V2"][0]
chk("draft: V2 combo G", v2p["G_m"], 8.9678, 5e-4)
chk("draft: V2 straight LB", v2p["travel_straight_lb_s"][1] if
    "travel_straight_lb_s" in v2p else v2p["travel_s"][1], 34.16, 0.05)
chk("draft: V2 path time", v2p["travel_s"][1], 34.75, 0.05)
sens = {(s["speed"], s["omega_deg_s"]): s["obj_s"]
        for s in q2b["sensitivity_speed_omega"]}
chk("draft: sens v2.5 w30", sens[(2.5, 30.0)], 10.611, 5e-4)
chk("draft: sens v3.5 w30", sens[(3.5, 30.0)], 10.243, 5e-4)
chk("draft: sens v3 w24", sens[(3.0, 24.0)], 11.499, 5e-4)
chk("draft: sens v3 w36", sens[(3.0, 36.0)], 9.676, 5e-4)
rb = q2b["robust_05"]
chk("draft: robust obj", rb["obj_s"], 10.837, 0.01)
chk("draft: robust T2", rb["starts"]["T2"], 10.804, 0.01)

# ---- Q3 claims ----
chk("Q3: exact s_max", q3["exact_geometry"]["s_max_exact_m"], 66.84, 0.01)
chk("Q3: exact ab", q3["exact_geometry"]["ab_max_exact_m"], 1.6367, 5e-4)
chk("Q3: P(66.92) exact", q3["exact_geometry"]["P_at_linear_smax"], 0.94980, 5e-5)
sd = {s["d_m"]: s["s_max_m"] for s in q3["sensitivity"]["s_max_vs_d"]}
for d, v in ((30, 46.44), (35, 56.68), (40, 66.92), (45, 77.16), (50, 87.40),
             (60, 107.88)):
    chk(f"Q3: s_max d={d}", sd[d], v, 0.02)
iso = {k: v["s_max_m"] for k, v in q3["ab_region"]["iso_levels"].items()}
for lv, v in (("0.9", 85.20), ("0.95", 66.92), ("0.98", 51.41), ("0.99", 43.07)):
    chk(f"Q3: conf {lv}", iso[lv], v, 0.02)
gs = {g["gimbal_scale"]: g["s_max_m"] for g in q3["sensitivity"]["s_max_vs_gimbal_scale"]}
for g, v in ((0.5, 72.32), (0.75, 70.11), (1.25, 62.63), (1.5, 57.03)):
    chk(f"Q3: gimbal {g}", gs[g], v, 0.02)

# ---- Q2a sens_H areas (draft 6.2: Omega_2 area 6272.7-6422.4) ----
areas = [s["area_m2"] for s in q2a["sensitivity"]["G_star_vs_H"]]
chk("Q2a area range min", min(areas), 6272.7, 0.5)
chk("Q2a area range max", max(areas), 6422.4, 0.5)

print(f"PASS {len(oks)}  FAIL {len(fails)}")
for f in fails:
    print("FAIL:", f[0], "got", f[1], "want", f[2])
if not fails:
    print("ALL DRAFT NUMBERS CONFIRMED")
