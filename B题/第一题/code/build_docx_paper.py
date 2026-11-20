# -*- coding: utf-8 -*-
"""生成《第一题_论文素材文档.docx》—— 给论文手的可直接粘贴英文段落、数字总表、图注与红线提醒。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _docx_common import (BASE, load_results, new_doc, title, h1, h2, para,
                          bullet, table, spacer, code_block)

R = load_results()
opt = R["optimal_station"]
arc = R["arc"]
gr = R["grid"]
sen = R["sensitivity"]
T1 = R["target"]["xy"]

doc = new_doc()
title(doc, "2026 “数维杯”B题  第一问论文素材文档",
      "（给论文手）可直接粘贴的英文段落 + 数字总表 + 图注 + 格式红线")

# ============ I ============
h1(doc, "I. 使用说明")
bullet(doc, "本文档所有数字都取自 code 跑出的 results/q1_results.json（已与解析推导互相验证），直接引用即可，不要再手算；")
bullet(doc, "英文段落按论文模板的章节顺序给出（Problem Analysis → Assumptions → Notation → Model → "
            "Solution → Validation → Sensitivity），可整段粘贴后微调；")
bullet(doc, "公式以线性格式给出，粘贴后请用 Word 公式编辑器（或 MathType）重新录入并统一编号；")
bullet(doc, "图在 第一题_图集.pptx（每图一页，SVG 矢量——右键“转换为形状”即可移动/改色/加标注）。"
            "图内刻意无任何文字（赛事规定图内不得出现中文），需要你在 PPT 中补英文标注，见第 V 节清单；")
bullet(doc, "页眉模板：Team <队伍号>  Page x of y；论文命名 <题号><队伍号>.pdf，例如 BSWBMCM26xxxx.pdf。")

# ============ II ============
h1(doc, "II. 关键数字总表（英文表头，可直接粘贴成论文表格）")
table(doc, ["Item", "Value"], [
    ["Target T1 alert (θ, R, H)", "(30°, 40 m, 45 m)"],
    ["Horizontal projection T′", f"({T1[0]:.4f}, {T1[1]:.4f}) m"],
    ["Gimbal lower bound (closed form)",
     "r ≥ (H − h_cam)/tan 80° = 43/tan 80° = 7.5821 m"],
    ["Optimal horizontal distance r*", f"{R['r_min_closed_form']:.4f} m"],
    ["Optimal observation quality Q*", f"{R['q_star']:.4f} m⁻¹"],
    ["Line-of-sight elevation at optimum", f"ε* = {opt['elevation_deg']:.3f}° (active constraint)"],
    ["Optimal station (after tie-breaking)",
     f"p* = ({opt['x']:.4f}, {opt['y']:.4f}) m  (polar angle {opt['phi_deg']:.2f}° on the r* circle)"],
    ["Safety margin / LOS clearance",
     f"{opt['margin_m']:.3f} m / {opt['los_clearance_m']:.2f} m"],
    ["Nearest vehicle & travel time", f"V4 from (88, 68), {opt['travel_time_s']:.2f} s at 3 m/s"],
    ["Travel times from all vehicles",
     "；".join(f"{k}: {v:.2f} s" for k, v in opt["travel_time_all"].items()).replace("；", ";  ")],
    ["Optimal arc blocked by B2 + buffer",
     f"[{arc['blocked_runs_deg'][0][0]:.2f}°, {arc['blocked_runs_deg'][0][1]:.2f}°] "
     f"(total {arc['blocked_total_deg']:.2f}°, i.e. {100-arc['feasible_fraction']*100:.1f}% of the circle)"],
    ["Optimal set", "the feasible arc of the r*-circle (~284°) — a continuum of optima"],
    ["Grid cross-check (0.1 m)",
     f"min feasible r = {gr['best_r']:.4f} m at (92.2, 69.4), +{gr['r_diff_vs_analytic']:.4f} m vs. analytic"],
    ["Observable-region area", f"{gr['area_m2']:.1f} m² (56.3% of the field)"],
    ["∂r*/∂H ; ∂r*/∂ε_max",
     f"{sen['dr_dH']:.4f} m per m ; {sen['dr_deps_deg']:.4f} m per degree"],
    ["Area vs. B2 height (20→45 m)",
     "6354.8 → 3481.5 m², monotone decreasing, saturating above 45 m"],
    ["Area vs. vehicle radius (1.0→2.5 m)", "5858.5 → 5217.9 m², near-linear decrease"],
    ["Alternative metric check",
     "Q₂ = (1/r)·cos²(ε − 45°) yields the same optimal circle (r = 7.583 m) — metric choice is robust"],
])
spacer(doc)

# ============ III ============
h1(doc, "III. 可直接粘贴的英文段落")

h2(doc, "3.1 Problem analysis（可放在 Problem Analysis 节）")
en = ("Problem 1 asks for the vehicle-observable region of target T1 and the station that maximizes the "
      "observation quality Q = 1/r, where r is the horizontal distance from the camera to the target. "
      "Since Q is strictly decreasing in r, maximizing Q is equivalent to finding the feasible station "
      "closest to the horizontal projection of the target. A station is feasible only if three constraints "
      "hold simultaneously: (C1) vehicle geometry — the 1.5 m equivalent disk must stay inside the field "
      "and outside every building footprint; (C2) gimbal elevation — the line-of-sight (LOS) elevation "
      "angle must lie in [−10°, 80°]; (C3) LOS occlusion — the 3-D LOS segment from the camera (height "
      "2 m) to the target (height 45 m) must not touch or cross any building prism. The key observation "
      "is that C2 alone implies a closed-form lower bound r ≥ (H − h_cam)/tan 80° ≈ 7.58 m, which "
      "converts the continuous optimization problem into a feasibility check on a single circle.")
para(doc, en, indent=False)
para(doc, "【中文备注】这段交代了“三约束 + 闭式下界”的框架，评审一眼能看到你抓住了问题结构。")

h2(doc, "3.2 Assumptions（放 Assumptions 节，编号可与全文假设统一）")
code_block(doc, """A1  The 1.5 m equivalent disk must not penetrate any building, i.e. the station
    center keeps a distance of at least 1.5 m from every building footprint
    (Minkowski clearance), rather than merely keeping the center outside.
A2  The gimbal elevation range [-10 deg, 80 deg] is treated as a closed interval,
    so the optimal elevation eps* = 80 deg is attainable and r* attains the
    closed-form lower bound exactly.
A3  Any tangency between the LOS segment and a building prism counts as
    occlusion, as stated in the problem; numerically we keep a 1e-9 tolerance
    so that grazing rays are conservatively rejected.
A4  r denotes the planar distance from the camera (the projection of the vehicle
    center, height 2 m) to the horizontal projection of the target; buildings
    stand on the flat ground z = 0, and no terrain occlusion exists.""")
para(doc, "【中文备注】四条假设与建模文档 III 一一对应；A2、A3 两条评审常问，务必保留。")

h2(doc, "3.3 Model formulation（放 Model 节）")
en = ("Let p = (x, y) denote the station center. The observable region is defined as the intersection "
      "Ω = C1 ∩ C2 ∩ C3, where C1 requires 1.5 ≤ x, y ≤ 98.5 and d(p, Bᵢ) ≥ 1.5 for every building "
      "rectangle Bᵢ, with d(·,·) the point-to-rectangle distance; C2 requires ε(p) = arctan(43/r(p)) ∈ "
      "[−10°, 80°], which reduces to r(p) ≥ r_min = 43/tan 80° ≈ 7.5821 m because the target is above "
      "the camera; and C3 requires the LOS segment (p, 2) → (84.6410, 70, 45) to be disjoint from every "
      "prism Bᵢ = [x₀, x₁] × [y₀, y₁] × [0, hᵢ], tested with the 3-D slab (interval-clipping) method, "
      "where tangency counts as occlusion. The optimization criterion is stated explicitly as")
code_block(doc, """        p*  =  argmax  Q(p) = 1 / r(p)   subject to  p in Omega
            =  argmin  r(p)            subject to  p in Omega ,
which is well posed because Q is strictly decreasing in r.""")
para(doc, "【中文备注】题面明确要求“Explicitly state the mathematical optimization criterion”，"
          "这个 argmax = argmin 的表述就是答案，务必出现在论文里。")

h2(doc, "3.4 Global optimality（放 Solution 节，本文档最核心的一段）")
en = ("The optimal value admits a proof of global optimality rather than a mere numerical claim. "
      "By C2, every feasible station satisfies r ≥ r_min = 7.5821 m; this lower bound depends only on "
      "the target altitude, the camera height and the gimbal bound, and is independent of the building "
      "layout. Sampling 200,000 polar angles on the circle r = r_min and testing C1 and C3 at each point "
      "shows that 78.8% of the circle is feasible; the blocked arc [160.75°, 236.89°] (76.14° in total) "
      "is produced exactly by building B2 and its 1.5 m clearance buffer, which matches the analytic "
      "estimate obtained by intersecting the circle with the inflated footprint [160.7°, 236.9°]. "
      "Hence the lower bound is attainable and r* = 7.5821 m with elevation ε* = 80° is the global "
      "optimum, with Q* = 0.1319 m⁻¹. A 0.1 m-resolution grid search over the whole field independently "
      "returns a minimum feasible distance of 7.5828 m (+0.0007 m, pure grid quantization), confirming "
      "the analytic result. Since the entire feasible arc of the r*-circle attains the same optimal "
      "value, the optimal set is a continuum — a structural multiplicity, not an artifact — which is "
      "precisely why tie-breaking rules are required.")
para(doc, "【中文备注】“解析下界 + 可行弧验证 + 网格交叉验证”三步走是本题的得分点，"
          "评审最忌讳“网格搜出来的最优”，这一段正面回应了 global optimality。")

h2(doc, "3.5 Tie-breaking rules（紧跟 3.4）")
code_block(doc, """Because every point of the feasible arc attains the same optimal value, we break
ties by a three-level lexicographic rule:
  T1 (safety margin)  maximize m(p) = min{ d(p, Bi) - 1.5,  distance to the
      four field edges }.  On the optimal arc the elevation slack is zero by
      construction (eps* = 80 deg is the active constraint), so the margin is
      computed over the geometric and occlusion boundaries only.
  T2 (responsiveness)  among points whose margin is within 0.05 m of the
      maximum, choose the one with the shortest travel time from the nearest
      standby vehicle.
  T3 (determinism)  if still tied, take the lexicographically smallest (x, y).
The rule yields the unique station p* = (88.8753, 76.2895) m with a safety
margin of 9.625 m, an LOS clearance of 7.41 m, and a travel time of 2.78 s
from V4 (the nearest vehicle, initially at (88, 68)).""")
para(doc, "【中文备注】报告值三个都齐了：坐标、距离 7.5821 m、仰角 80°——题面点名的三件套。")

h2(doc, "3.6 Sensitivity（放 Sensitivity Analysis 节）")
en = ("Two closed-form sensitivities follow immediately from r* = (H − h_cam)/tan 80°: "
      "∂r*/∂H = 1/tan 80° = 0.176 m per m of target altitude, and ∂r*/∂ε_max = −43·csc²(80°)·π/180 = "
      "−0.774 m per degree of the gimbal bound. More importantly, since the bound contains no "
      "environmental parameters, the optimal VALUE is intrinsically robust to the building layout: "
      "perturbing building heights or positions changes only WHERE on the r*-circle the feasible arc "
      "lies, never the optimal distance itself. At the regional level, the observable area decreases "
      "monotonically with the height of B2 (6354.8 → 3481.5 m² as h_B2 grows from 20 m to 45 m, "
      "saturating once h_B2 reaches the target altitude) and decreases near-linearly with the vehicle "
      "radius (5858.5 → 5217.9 m² as R_veh grows from 1.0 m to 2.5 m). Finally, replacing the metric "
      "by Q₂ = (1/r)·cos²(ε − 45°), which additionally prefers mid-range elevation angles, leaves the "
      "optimum on the same r*-circle, so the choice Q = 1/r is robust within a reasonable metric family.")
para(doc, "【中文备注】“值稳健—位置敏感”分解 + 面积扫描 + 备选度量检验，三层递进，"
          "模板自带的 Sensitivity Analysis 章节正好用这段。")

h2(doc, "3.7 结果陈述句（可直接放进摘要或 Conclusion）")
en = ("For Problem 1, the observable region of T1 covers about 5.63 × 10³ m² (56.3% of the field). "
      "The optimal station is located at (88.88, 76.29) m with a horizontal distance of 7.5821 m and a "
      "line-of-sight elevation of exactly 80°, where Q attains its maximum 0.1319 m⁻¹; the optimality "
      "is proven analytically and verified numerically, and a three-level tie-breaking rule selects "
      "the unique station on the 284°-feasible optimal arc.")
para(doc, "【中文备注】摘要里第一问的浓缩版。")

# ============ IV ============
h1(doc, "IV. 图表清单与需要手补的英文标注")
table(doc, ["图", "文件", "建议英文 caption（PPT 备注页里也有）", "需要在 PPT 中手补的标注"], [
    ["Fig. 1", "fig1_observable_region",
     "Observable region of target T1 (blue) over the 100 m × 100 m field; grey prisms are buildings B1–B5, "
     "the grey disk around the star is the gimbal-limit exclusion zone (r < 7.58 m).",
     "坐标轴 x/m、y/m；图例（feasible Ω / infeasible / building / vehicle）；"
     "标 “O”, “T1′”, “V1–V5”, “B1–B5”"],
    ["Fig. 2", "fig2_constraint_layers",
     "Layered effect of the three constraints: (a) vehicle geometry C1; (b) + gimbal elevation C2; "
     "(c) + LOS occlusion C3.",
     "三个子图下标 (a)(b)(c)；坐标轴；标 T1′"],
    ["Fig. 3", "fig3_optimal_arc_zoom",
     "Left: the optimal circle r* = 7.58 m near T1 — green arc feasible (≈284°), red arc blocked by B2 and "
     "its 1.5 m buffer; right: safety-margin profile along the circle.",
     "坐标轴 φ (deg) / margin (m)；标 “p* (chosen station)” “T1′” “V4” “B2”"],
    ["Fig. 4", "fig4_sensitivity_rstar",
     "Closed-form sensitivity of r*: versus target altitude H (left) and versus the gimbal elevation bound "
     "(right); nominal parameters marked.",
     "坐标轴 r* (m) / H (m)、r* (m) / ε_max (deg)；标 nominal 点"],
    ["Fig. 5", "fig5_sensitivity_area",
     "Sensitivity of the observable-region area to the height of B2 (left) and to the vehicle radius (right).",
     "坐标轴 Area (m²) / h_B2 (m)、Area (m²) / R_veh (m)"],
    ["Fig. 6", "fig6_los_3d",
     "3-D view of the LOS from the chosen optimal station (height 2 m) to T1 (height 45 m); minimum "
     "clearance to any prism is 7.41 m.",
     "坐标轴 x/m、y/m、z/m；标 “LOS” “p*” “T1”"],
])
para(doc, "【中文备注】赛事规定：图注在图下方、表注在表上方；图与表中不得出现中文字体——"
          "所以上面的标注必须手补成英文。补完后在 PPT 里选中图形 → 右键“另存为图片”（或直接截图）"
          "插入论文；SVG 矢量在缩放时不失真。", indent=False)

# ============ V ============
h1(doc, "V. 格式红线（来自《论文格式规范》，违规直接取消评奖资格）")
bullet(doc, "全文英文，12 号 Times New Roman；正文（含摘要页、目录页）≤ 25 页，附录不限；")
bullet(doc, "图注在下、表注在上；图形图表中不得出现中文；")
bullet(doc, "第一页 = 题目 + Summary + 关键词；第二页 = 目录专页；页眉含队伍号与页码（Team … Page x of y）；")
bullet(doc, "正文和附录不得出现学校/个人信息；参考文献按正文引用次序列出，尽量不用网址；")
bullet(doc, "全部源代码须在附录或支撑材料中提供（code/ 文件夹可直接打包为支撑材料 <题号><队伍号>fj.zip）；")
bullet(doc, "提交：论文 PDF + 承诺书（手写签名扫描）+ 支撑材料，三件分别上传；截止 2026-11-24 10:00。")
spacer(doc)
para(doc, "——第一问素材到此为止；第二、三、四问的素材文档将在各自完成后以同样格式提供。", indent=False)

out = os.path.join(BASE, "第一题_论文素材文档.docx")
doc.save(out)
print("saved", out)
