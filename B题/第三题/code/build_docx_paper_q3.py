# -*- coding: utf-8 -*-
"""生成《第三题_论文素材文档.docx》（英文可粘贴段落 + 数字总表 + 图注映射）。"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _docx_common import (new_doc, title, h1, h2, para, bullet, table,
                          load_results)

R = load_results("q3_results.json")
mc = R["monte_carlo"]
S_MAX = R["s_max_m"]
SPM = R["sigma_psi_max_deg"]
AB = R["ab_region"]["a_plus_80b_max_m"]

doc = new_doc()
title(doc, "第三题论文素材（英文可粘贴段落 + 数字总表 + 图注映射）",
      "图内无文字，图注由论文手在 PPT 备注页取用；罗马数字分节")

h1(doc, "I. 可粘贴段落（Model: error propagation）")
para(doc, "Let the estimated vehicle position be P̂ = P + (δx, δy) with δx, δy independent "
          "N(0, σ(s)²), σ(s) = 0.3 + 0.02 s, and let the target be exactly known at horizontal "
          "range d = 40 m. Rotating coordinates so that the true line of sight is the x-axis, "
          "only the cross-range error component δ⊥ rotates the bearing, and by the isotropy of "
          "the pair (δx, δy), δ⊥ ~ N(0, σ(s)²) independent of the along-range component. The "
          "commanded bearing computed from P̂ therefore deviates from the true bearing by "
          "Δα = arctan2(−δ⊥, d − δ∥), which linearizes to −δ⊥/d for δ ≪ d; adding the "
          "independent gimbal zero-offset and control errors gives "
          "Δψ = wrap(−δ⊥/d·180/π + ε₀ + ε_c). Since all three terms are independent zero-mean "
          "normal and the wrap never activates (σ_ψ ≤ 2.9° ≪ 180°), "
          "Δψ ~ N(0, σ_ψ²(s)) with σ_ψ²(s) = (σ(s)/40 · 180/π)² + 0.8² + 0.6², i.e. "
          "σ_ψ²(s) = (1.432395 σ(s))² + 1.0 deg².", indent=False)

h1(doc, "II. 可粘贴段落（Results: s_max and the 80 m requirement）")
para(doc, f"The accuracy requirement P(|Δψ| ≤ 5°) ≥ 0.95 is two-sided and equivalent to "
          f"σ_ψ ≤ 5/z_0.975 = 5/1.959964 = {SPM:.4f}°. Because σ_ψ(s) is strictly increasing, "
          f"the requirement reduces to a variance budget for the localization error: "
          f"σ(s_max) = 40·(π/180)·√(σ_ψ_max² − 0.8² − 0.6²) = 40·(π/180)·2.346901 = "
          f"{R['sigma_s_at_smax_m']:.4f} m, giving the closed-form maximum travel distance "
          f"s_max = ({R['sigma_s_at_smax_m']:.4f} − 0.3)/0.02 = {S_MAX:.2f} m. An exact-geometry "
          f"check (256×256 Hermite quadrature of the atan2 pointing geometry, no "
          f"linearization) gives P({S_MAX:.2f} m) = {R['exact_geometry']['P_at_linear_smax']:.4f} "
          f"and an exact s_max = {R['exact_geometry']['s_max_exact_m']:.2f} m with "
          f"a + 80b ≤ {R['exact_geometry']['ab_max_exact_m']:.4f} m — the linearized "
          f"values are adopted as the closed-form answers and the exact ones as "
          f"conservative design values (difference 0.08 m, 0.13%). At the nominal "
          f"model, s = 80 m yields σ_ψ = {R['at_80']['sigma_psi_deg']:.4f}° and "
          f"P = {R['at_80']['P']:.4f} < 0.95 (shortfall {R['at_80']['P_deficit']:.4f}); the "
          f"localization standard deviation at 80 m exceeds the allowable value by "
          f"{R['at_80']['excess_needed_m']:.4f} m.", indent=False)
para(doc, f"Holding the same requirement at s = 80 m (and hence for all s ≤ 80 m, since b ≥ 0 "
          f"makes σ(s) monotone) imposes the linear constraint set on the nonnegative parameters "
          f"a ≥ 0, b ≥ 0, a + 80 b ≤ {AB:.4f} m — i.e. a ≤ {AB:.4f} m with b = 0, or "
          f"b ≤ {R['ab_region']['b_max_m_per_m']:.6f} m per m with a = 0. The nominal pair "
          f"(a, b) = (0.3, 0.02) gives a + 80b = 1.9 m and lies outside the set: either the "
          f"growth rate must be cut to b ≤ (1.6384 − 0.3)/80 = 0.016731 m per m (−16.3%) with "
          f"a = 0.3, or the intercept reduced to a ≤ 0.0384 m with b = 0.02.", indent=False)

h1(doc, "III. 可粘贴段落（Validation and contributions）")
mc0 = mc["points"]
para(doc, f"Applicability of the approximations. The second-order residual of the exact bearing "
          f"error arctan2(−δ⊥, d − δ∥) is dominated by −δ⊥δ∥/d², whose RMS equals σ(s)²/d² = "
          f"{mc['linearization_residual_rms_deg_at80']:.4f}° at s = 80 m — only 4.4% of σ_ψ, "
          f"contributing ≈ 0.2% of the variance. A Monte-Carlo experiment with n = 10⁶ samples "
          f"and the exact atan2 pointing geometry (no linearization) confirms the propagation "
          f"model: the empirical probabilities match the analytic ones to within 3×10⁻⁴ at all "
          f"tested ranges s ∈ {{0, 20, 40, 66.92, 80}} m (e.g. {mc0[3]['P_emp']:.4f} vs "
          f"{mc0[3]['P_ana']:.4f} at s = 66.92 m), empirical standard deviations coincide with "
          f"the analytic values, the empirical bias is below 6×10⁻³°, and the maximum quantile "
          f"deviation from the analytic normal is 0.055°.", indent=False)
c40 = R["contributions"][4]
c80 = R["contributions"][7]
para(doc, f"Relative contributions of the three error sources. The variance shares shift with "
          f"traveled distance: at s = 0 the gimbal zero-offset dominates (54.0% zero-offset / "
          f"30.4% control / 15.6% localization); the localization variance crosses the total "
          f"gimbal variance at s = {R['s_crossover_m']:.2f} m; at s = 40 m the shares are "
          f"{c40['share_loc']*100:.1f}% / {c40['share_zero']*100:.1f}% / {c40['share_ctrl']*100:.1f}% "
          f"(localization / zero-offset / control), and at s = 80 m "
          f"{c80['share_loc']*100:.1f}% / {c80['share_zero']*100:.1f}% / {c80['share_ctrl']*100:.1f}%. "
          f"The zero-offset : control ratio is constant at 0.64 : 0.36.", indent=False)

h1(doc, "IV. 可粘贴段落（Sensitivity and deployment insights）")
sens = R["sensitivity"]
para(doc, f"s_max is linear in the vehicle-target standoff distance d with slope "
          f"{sens['ds_max_dd_m_per_m']:.3f} m per m (e.g. {sens['s_max_vs_d'][0]['s_max_m']:.1f} m at "
          f"d = 30 m and {sens['s_max_vs_d'][-1]['s_max_m']:.1f} m at d = 60 m, nominal "
          f"{S_MAX:.1f} m at d = 40 m); raising the required confidence to 0.99 lowers s_max to "
          f"{R['ab_region']['iso_levels']['0.99']['s_max_m']:.1f} m. Scaling both gimbal errors by "
          f"0.75 buys only 3.2 m of extra travel at the nominal long-range regime because the "
          f"localization term already dominates there. Deployment insights: (i) beyond ~20 m of "
          f"travel, localization accuracy is the binding error source — invest in odometry/DGPS "
          f"quality rather than gimbal calibration; (ii) on short missions (s ≲ 20 m) calibrate the "
          f"gimbal zero-offset first, since it alone carries 54% of the variance; (iii) a larger "
          f"standoff distance is a powerful lever (+1 m of d buys ≈ 2.05 m of travel allowance), "
          f"to be traded against the geometry constraints of Problems 1-2; (iv) to operate at "
          f"80 m, the localization drift must satisfy a + 80b ≤ 1.6384 m, e.g. b ≤ 0.016731 m per m "
          f"with a = 0.3.", indent=False)

h1(doc, "V. 英文数字总表（全部取自 JSON）")
rows = [
    ["Model", "Δψ ~ N(0, (σ(s)/40·180/π)² + 0.8² + 0.6²), σ(s) = 0.3 + 0.02s"],
    ["z_0.975 (two-sided 0.95)", f"{R['z_conf']:.6f}"],
    ["Allowable σ_ψ", f"5/z = {SPM:.4f}°"],
    ["s_max", f"{S_MAX:.2f} m (σ(s_max) = {R['sigma_s_at_smax_m']:.4f} m)"],
    ["s = 80 m, nominal", f"σ_ψ = {R['at_80']['sigma_psi_deg']:.4f}°, "
                          f"P = {R['at_80']['P']:.4f} (< 0.95)"],
    ["80 m condition", f"a ≥ 0, b ≥ 0, a + 80b ≤ {AB:.4f} m; nominal (0.3, 0.02) fails"],
    ["Crossover (loc = gimbal variance)", f"s = {R['s_crossover_m']:.2f} m"],
    ["Shares at s = 40 / 80", f"{c40['share_loc']*100:.1f}/{c40['share_zero']*100:.1f}/"
                              f"{c40['share_ctrl']*100:.1f}% → {c80['share_loc']*100:.1f}/"
                              f"{c80['share_zero']*100:.1f}/{c80['share_ctrl']*100:.1f}%"],
    ["MC validation (n = 10⁶)", f"|ΔP| ≤ 3×10⁻⁴; max quantile gap 0.055°; bias < 6×10⁻³°"],
    ["Linearization residual", f"RMS {mc['linearization_residual_rms_deg_at80']:.4f}° at s = 80 "
                               f"(4.4% of σ_ψ)"],
    ["d(s_max)/d(d_tgt)", f"{sens['ds_max_dd_m_per_m']:.3f} m per m"],
    ["s_max vs confidence", "85.2 (0.90) / 66.9 (0.95) / 51.4 (0.98) / 43.1 (0.99) m"],
]
table(doc, ["Item", "Value"], rows)

h1(doc, "VI. 图注建议（图内无文字）")
table(doc, ["Label", "File", "Caption (suggest)"], [
    ["Fig. 1", "fig1_sigma_components",
     "σ_loc(s), gimbal floor, total σ_ψ(s), the 2.5511° ceiling and s_max = 66.92 m."],
    ["Fig. 2", "fig2_probability_curve",
     "P(|Δψ| ≤ 5°) vs s: analytic curve, MC points (n = 10⁶), 0.95 line."],
    ["Fig. 3", "fig3_ab_region",
     "Feasible (a, b) region at 80 m with iso-confidence lines; nominal pair outside."],
    ["Fig. 4", "fig4_variance_shares",
     "Stacked variance decomposition; crossover at 19.91 m, s_max at 66.92 m."],
    ["Fig. 5", "fig5_mc_validation",
     "MC histogram vs analytic density at s = 80 m with ±5° limits."],
    ["Fig. 6", "fig6_sensitivity_smax",
     "s_max vs standoff distance d (slope 2.048 m/m); s_max vs confidence level."],
])

h1(doc, "VII. 格式红线提醒")
bullet(doc, "全文英文、12 号 Times New Roman；正文 ≤ 25 页；图注在下、表注在上；图形图表无中文。")
bullet(doc, "本问务必显式回应题面四处点名：近似/数值方法适用性论证、结果验证（MC）、三误差源相对贡献比较、部署启示。")
bullet(doc, "代码进附录或支撑材料；数字源 results/q3_results.json 与 q3_summary.txt。")

doc.save(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "第三题_论文素材文档.docx"))
print("saved 第三题_论文素材文档.docx")
