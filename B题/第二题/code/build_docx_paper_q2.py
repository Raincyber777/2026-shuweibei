# -*- coding: utf-8 -*-
"""Build 第二题_论文素材文档.docx (paste-ready English material for the paper writer)."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _docx_common import (new_doc, title, h1, h2, para, bullet, table,
                          code_block, load_results)

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "第二题_论文素材文档.docx")
RA = load_results("q2a_results.json")
RB = load_results("q2b_results.json")
ch = RA["chosen"]
DRMS_S = RA["certificate"]["DRMS_star_m"]
RSTAR = RA["r_min_geo_m"]
area2 = RA["region"]["area_m2"]

doc = new_doc()
title(doc, "第二题论文素材（英文可粘贴段落 + 数字总表 + 图注映射）",
      "供论文手使用；图内无文字，图注/图例由论文手在 PPT 中补英文；罗马数字分节")

h1(doc, "I. 2(1) 可粘贴段落（Model Building: two-station accuracy）")
para(doc, "Let the two stations be p1 and p2 with station-target ranges d1, d2 and measured azimuths "
          "alpha1, alpha2, each corrupted by an independent error dalpha_i ~ N(0, sigma^2), sigma = 1 deg. "
          "Writing each bearing line in normal form n_i^T (x - p_i) = 0, an angular error shifts line i "
          "laterally by d_i * dalpha_i, so the intersection error satisfies A * dp = delta with "
          "A = [n1; n2] and delta = (d1 dalpha1, d2 dalpha2)^T. Hence the position-error covariance is "
          "Sigma = A^{-1} diag(d1^2, d2^2) sigma^2 A^{-T}, and since det A = sin(gamma) (gamma = "
          "intersection angle), trace(Sigma) = sigma^2 (d1^2 + d2^2)/sin^2(gamma). We adopt the "
          "root-mean-square (DRMS) accuracy metric Phi = sigma * G with the geometry factor "
          "G = sqrt((d1^2 + d2^2)/2)/|sin(gamma)|, which is frame-invariant, monotone in the 1-sigma "
          "ellipse area, and minimal at gamma = 90 deg; the 95% radius follows as DRMS * sqrt(5.991).", indent=False)
para(doc, "A provable global lower bound follows from the QM-AM inequality: G >= (d1 + d2)/2 >= r_min, "
          f"where r_min = (H2 - h_cam)/tan(80 deg) = 33/tan(80 deg) = {RSTAR:.4f} m is the "
          "elevation-imposed exclusion radius of T2 (11.0289, 72.5, 35 m). Equality holds iff "
          "d1 = d2 = r_min and gamma = 90 deg. Sampling the r_min circle (72,000 points) yields a "
          "feasible arc "
          f"[{RA['circle']['feasible_runs_deg'][0][0]:.2f} deg, "
          f"{RA['circle']['feasible_runs_deg'][-1][1]:.2f} deg] "
          "(occlusion by B3 near the target's own footprint blocks the remainder) and a robust-feasible "
          "arc "
          f"[{RA['circle']['robust_runs_deg'][0][0]:.2f} deg, "
          f"{RA['circle']['robust_runs_deg'][-1][1]:.2f} deg]; "
          "90 deg-separated pairs exist for phi in "
          f"({RA['certificate']['phi_span_deg'][0]:.2f} deg, "
          f"{RA['certificate']['phi_span_deg'][1]:.2f} deg), "
          "so the bound is attained and the optimum set is a continuous one-parameter family - "
          "tie-breaking rules are required, exactly as in Problem 1.", indent=False)

h1(doc, "II. 2(1) 结果段（Results）")
para(doc, f"Selecting the vehicle pair by C(5,2)=10 enumeration with two-stage LB-pruned polar search "
          f"(continuous Nelder-Mead refinement; pairs containing V2 cannot reach the r_min circle and "
          f"attain G = 9.0063 m, DRMS = 0.1572 m), the tie-breaking rules - (i) minimum total travel "
          f"time within the robust interior (LOS roof clearance and geometric margin >= 0.75 m, "
          f"straight paths avoiding building buffers), (ii) minimum worst-case travel, (iii) "
          f"lexicographic - uniquely select V3 + V5 with stations "
          f"p1 = ({ch['stations'][0][0]:.4f}, {ch['stations'][0][1]:.4f}) and "
          f"p2 = ({ch['stations'][1][0]:.4f}, {ch['stations'][1][1]:.4f}) m, ranges d1 = d2 = 5.8188 m, "
          f"intersection angle gamma = 90.000 deg, baseline B = {ch['baseline_m']:.4f} m, travel times "
          f"({ch['travel_s'][0]:.2f}, {ch['travel_s'][1]:.2f}) s, and DRMS = {ch['DRMS_m']:.4f} m "
          f"(95% circle radius {ch['ellipse95_radius_m']:.4f} m, area "
          f"{ch['ellipse95_area_m2']:.4f} m^2). A 200,000-sample Monte-Carlo experiment "
          f"gives RMSE {ch['MC']['rmse_m']:.4f} m and a 95th percentile of {ch['MC']['p95_m']:.4f} m, "
          f"matching the closed form (sigma*sqrt(2) = {DRMS_S*np.sqrt(2):.4f} m and "
          f"sigma*2.4477 = {ch['ellipse95_radius_m']:.4f} m).", indent=False)
para(doc, "Degeneracy. As gamma -> 0 or 180 deg, G ~ 1/|sin gamma| -> infinity and the design matrix A "
          "becomes singular (kappa = 1/|sin gamma|); we therefore impose the operating window "
          "gamma in [30 deg, 150 deg] (G <= 2 G* for symmetric ranges), use a ridge-regularized "
          "weighted line intersection when gamma is small, and reposition a vehicle to reopen the angle. "
          "Stations on the boundary of the observable region are knife-edge solutions (elevation "
          "exactly 80 deg, zero margin); we back off to elevation <= 78 deg (r >= 7.0144 m, DRMS "
          "0.1224 m, +20.5%) and require >= 0.75 m LOS clearance and geometric margin in the "
          "tie-breaking.", indent=False)

h1(doc, "III. 2(2) 可粘贴段落（Model & Algorithm）")
para(doc, "Each vehicle-task consumes travel time |pos - p|/3, a gimbal slew of max(|alpha|, eps)/30 "
          "(pan and tilt rotate simultaneously, reset symmetric), a synchronized 5 s observation whose "
          "start is the later of the two partners' ready times, and a reset of max(|alpha|, eps)/30 "
          "before departing. The decision is (assignment of two distinct vehicles to each of T1-T3, "
          "per-vehicle task order, stations); the objective is min max_a t_a with t_a the observation "
          "start of alert a. All C(5,2)^3 = 1000 assignment structures are enumerated (ordered by an "
          "optimistic bound max_a max of the two members' earliest-ready values, with bound-based "
          "pruning); mutual-waiting cycles between two reused vehicles are detected by fixed-point "
          "iteration and rejected. For each structure, stations are optimized by greedy initialization, "
          "Gauss-Seidel coordinate descent over the doubled vehicle (p1 x p2 candidate enumeration), "
          "and a final Nelder-Mead polish of every station against the global objective with exact "
          "feasibility penalties; ties are broken by the sum of the three observation starts.", indent=False)
para(doc, "A lower bound: r(v, a) = min_p [dist(V_v, p)/3 + max(|alpha|, eps)/30] is the earliest time "
          "vehicle v can be ready for alert a; since an alert needs two distinct vehicles, "
          "t_a >= the second-smallest r(v, a), giving LB = 3.414 s (T2). This bound ignores reuse "
          "delays and is therefore loose; the enumeration is exhaustive over structures, and the "
          "per-vehicle earliest-ready table (Table R2) verifies each entry.", indent=False)

h1(doc, "IV. 2(2) 结果段（Results & Comparison）")
op = RB["optimized"]
hp2 = RB["heuristic"]
starts = op["alert_starts"]
oa = op["assignment"]
para(doc, f"The optimized scheme assigns T1 <- (V{oa['T1'][0]+1}, V{oa['T1'][1]+1}), "
          f"T2 <- (V{oa['T2'][0]+1}, V{oa['T2'][1]+1}), T3 <- (V{oa['T3'][0]+1}, V{oa['T3'][1]+1}); "
          "vehicle V5 is reused for T1 then T3 from the same station (zero travel leg, 1.53 s reset "
          "+ 2.77 s slew in place). Observation starts are "
          f"T1 = {starts['T1']:.2f} s, T2 = {starts['T2']:.2f} s, "
          f"T3 = {starts['T3']:.2f} s, so the maximum is {op['objective_s']:.2f} s. The independently "
          "defined nearest-assignment heuristic - alerts processed in index order, each slot taken by "
          "the vehicle with the smallest marginal travel time to its ready-minimizing feasible "
          "station, reuse appended after the committed chain - yields "
          f"{hp2['alert_starts']['T1']:.2f} / {hp2['alert_starts']['T2']:.2f} / "
          f"{hp2['alert_starts']['T3']:.2f} s and a "
          f"maximum of {hp2['objective_s']:.2f} s, i.e. {RB['comparison']['gap_s']:.2f} s "
          f"(+{(hp2['objective_s']/op['objective_s']-1)*100:.0f}%) worse. Three sources explain the "
          "gap: (i) "
          "pairing loss - the heuristic pairs the two nearest vehicles with one alert while the "
          "alert start is governed by the slower partner; (ii) chain-order effects - it stacks a slow "
          "task after a fast one on the same vehicle and blocks the early window of T3, whereas the "
          "optimized plan concentrates all reuse in a single zero-travel chain of V5; (iii) "
          "azimuth-blind station choice - ready times are pan-angle dominated (30 deg/s), so "
          "distance-nearest stations are not time-nearest.", indent=False)
senB = {(s["speed"], s["omega_deg_s"]): s["obj_s"] for s in RB["sensitivity_speed_omega"]}
o0 = op["objective_s"]
para(doc, f"Sensitivity: re-simulating the optimized structure at speeds 2.5/3/3.5 m/s and slew rates "
          f"24/30/36 deg/s shows the objective is almost speed-insensitive "
          f"({o0:.2f} -> {senB[(2.5, 30.0)]:.2f}-{senB[(3.5, 30.0)]:.2f} s "
          f"across +/-17% speed) but slew-rate sensitive ({o0:.2f} -> {senB[(3.0, 24.0)]:.2f} s at "
          f"24 deg/s, {senB[(3.0, 36.0)]:.2f} s at "
          "36 deg/s). Deployment insight: prefer stations with small pan rotation over shorter "
          "travel; upgrading gimbal slew rate buys more than upgrading vehicles.", indent=False)

h1(doc, "V. 英文数字总表（直接引用，全部取自 JSON）")
rows = [
    ["T2 projection / altitude", "(11.0289, 72.5000), 35 m"],
    ["r_min (elevation bound)", f"33/tan80 = {RSTAR:.4f} m"],
    ["Omega_2 area (0.1 m cell-center grid)",
     f"{area2:.1f} m^2 (node count {RA['region']['area_node_count_m2']:.1f} m^2)"],
    ["Feasible / robust arc on r_min circle",
     f"[{RA['circle']['feasible_runs_deg'][0][0]:.2f}, "
     f"{RA['circle']['feasible_runs_deg'][-1][1]:.2f}] / "
     f"[{RA['circle']['robust_runs_deg'][0][0]:.2f}, "
     f"{RA['circle']['robust_runs_deg'][-1][1]:.2f}] deg"],
    ["Certificate family (90 deg pairs)",
     f"phi in ({RA['certificate']['phi_span_deg'][0]:.2f}, "
     f"{RA['certificate']['phi_span_deg'][1]:.2f}) deg"],
    ["Chosen pair / stations",
     f"{ch['vehicles']}; ({ch['stations'][0][0]:.4f}, {ch['stations'][0][1]:.4f}), "
     f"({ch['stations'][1][0]:.4f}, {ch['stations'][1][1]:.4f})"],
    ["d1, d2 / gamma / B",
     f"{ch['d_m'][0]:.4f}, {ch['d_m'][1]:.4f} m / {ch['gamma_deg']:.3f} deg / "
     f"{ch['baseline_m']:.4f} m"],
    ["Travel times (sum)",
     f"{ch['travel_s'][0]:.2f}, {ch['travel_s'][1]:.2f} s ({ch['travel_sum_s']:.2f} s)"],
    ["DRMS / 95% radius / area",
     f"{DRMS_S:.4f} m / {ch['ellipse95_radius_m']:.4f} m / {ch['ellipse95_area_m2']:.4f} m^2"],
    ["MC check (200k)",
     f"RMSE {ch['MC']['rmse_m']:.4f} m, P95 {ch['MC']['p95_m']:.4f} m"],
    ["gamma window (G <= 2G*)",
     f"[{RA['degeneracy']['gamma_window_G_le_2Gstar_deg'][0]:.2f}, "
     f"{RA['degeneracy']['gamma_window_G_le_2Gstar_deg'][1]:.2f}] deg"],
    ["Backoff design (elev <= 78)",
     f"r = {RA['degeneracy']['backoff_r_m']:.4f} m, "
     f"DRMS {RA['degeneracy']['backoff_DRMS_m']:.4f} m"],
    ["dG*/dH, dDRMS/dH",
     f"{RA['sensitivity']['dG_dH_per_m']:.4f} m/m, "
     f"{RA['sensitivity']['dDRMS_dH_m_per_m']:.5f} m per m"],
]
table(doc, ["Item", "Value"], rows)

rv = RB["r_va_table"]
rows2 = [[v] + [f"{rv[v][a]:.2f}" for a in ["T1", "T2", "T3"]] for v in ["V1", "V2", "V3", "V4", "V5"]]
table(doc, ["Earliest-ready r(v,a) (s)", "T1", "T2", "T3"], rows2)

rows3 = [
    ["T1", "1.53", "20.67"],
    ["T2", "6.99", "30.21"],
    ["T3", "10.83", "30.04"],
    ["Objective (max)", "10.83", "30.21"],
    ["Improvement", "+19.38 s (+179%)", "-"],
]
table(doc, ["Alert / metric", "Optimized (s)", "Nearest baseline (s)"], rows3)

h1(doc, "VI. 图注建议（图内无文字，由论文手补）")
figs = [
    ("Fig. 1", "fig1_region_reach", "Observable region of T2 and the five 30 s reach circles."),
    ("Fig. 2", "fig2_layers_T2", "Layered constraints: geometry / +elevation / +LOS."),
    ("Fig. 3", "fig3_optimal_pair_zoom", "r_min circle arcs (blocked/feasible/robust), chosen pair, baseline, 90 deg arc."),
    ("Fig. 4", "fig4_accuracy_model", "G(gamma) for d = 5.82-20 m; 95% ellipse axes vs gamma."),
    ("Fig. 5", "fig5_sensitivity", "G* vs H; normalized degradation and gamma window."),
    ("Fig. 6", "fig6_error_ellipses", "1-sigma/2-sigma/95% circles at the optimal pair."),
    ("Fig. 7", "fig7_gantt_opt", "Optimized vehicle timelines (see notes for color key)."),
    ("Fig. 8", "fig8_gantt_heu", "Nearest-assignment baseline timelines."),
    ("Fig. 9", "fig9_routes_map", "Deployment map: stations, travel legs, azimuth lines."),
    ("Fig. 10", "fig10_comparison_sens", "Per-alert starts (opt vs heuristic); objective vs speed and slew rate."),
]
table(doc, ["Label", "File", "Caption (suggest)"], figs)
para(doc, "色标与行号映射（写入图注或图例）：甘特图行 1–5 = V1–V5；颜色 = 浅蓝行驶 / 橙转云台 / 灰同步等待 / "
          "绿观测(5 s) / 红复位。fig10 左图横轴 1–3 = T1–T3。", indent=False)

h1(doc, "VII. 格式红线提醒（与交接文档 I.2 一致）")
bullet(doc, "全文英文、12 号 Times New Roman；正文含摘要目录 ≤25 页；图注在下、表注在上；图形内不得出现中文。")
bullet(doc, "本问贡献要点建议在 Model 与 Results 中显式呼应题目三处点名：精度指标合理性论证、γ 与边界退化讨论、"
            "独立定义最近指派基线并分析差异来源。")
bullet(doc, "代码清单进附录或支撑材料；数据源 results/q2a_results.json、q2b_results.json。")

doc.save(OUT)
print("saved", OUT)
