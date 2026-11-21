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
      "（给论文手）可直接粘贴的段落（中文先行，最终统一英译） + 数字总表 + 图注 + 格式红线")

# ============ I ============
h1(doc, "I. 使用说明")
bullet(doc, "本文档所有数字都取自 code 跑出的 results/q1_results.json（已与解析推导互相验证），直接引用即可，不要再手算；")
bullet(doc, "英文段落按论文模板的章节顺序给出（Problem Analysis → Assumptions → Notation → Model → "
            "Solution → Validation → Sensitivity），可整段粘贴后微调；")
bullet(doc, "公式以线性格式给出，粘贴后请用 Word 公式编辑器（或 MathType）重新录入并统一编号；")
bullet(doc, "图在 第一题_图集.pptx（每图一页，SVG 矢量——右键“转换为形状”即可移动/改色/加标注）。"
            "图内刻意无任何文字（赛事规定图内不得出现中文），需要你在 PPT 中补英文标注，见第 IV 节清单；")
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
    ["Arc maximum margin m* (true)",
     f"{arc['m_star_margin_m']:.4f} m at phi = {arc['m_star_phi_deg']:.2f} deg "
     f"(point ({arc['m_star_point'][0]:.4f}, {arc['m_star_point'][1]:.4f}); B2-buffer "
     "distance = east-boundary distance there)"],
    ["Safety margin of the SELECTED station / LOS clearance",
     f"{opt['margin_m']:.3f} m (east field boundary; inside the band "
     f"[m* − 0.05, m*] = [{arc['band_lower_m']:.4f}, {arc['m_star_margin_m']:.4f}]) / "
     f"{opt['los_clearance_m']:.2f} m"],
    ["Nearest vehicle & travel time",
     f"V4 from (88, 68), {opt['travel_time_s']:.2f} s at 3 m/s (straight path clear)"],
    ["Travel times from all vehicles (straight-line LB / feasible path)",
     "；".join(f"{k}: {v:.2f}/{opt['travel_time_all_path'][k]:.2f} s"
               for k, v in opt["travel_time_all"].items()).replace("；", ";  ")],
    ["Optimal arc blocked by B2 + buffer",
     f"[{arc['blocked_runs_deg'][0][0]:.2f}°, {arc['blocked_runs_deg'][0][1]:.2f}°] "
     f"(total {arc['blocked_total_deg']:.2f}°, i.e. {100-arc['feasible_fraction']*100:.1f}% of the circle)"],
    ["Optimal set", "the feasible arc of the r*-circle (~284°) — a continuum of optima"],
    ["Grid cross-check (0.1 m)",
     f"min feasible r = {gr['best_r']:.4f} m at (92.2, 69.4), +{gr['r_diff_vs_analytic']:.4f} m vs. analytic"],
    ["Observable-region area",
     f"{gr['area_m2']:.1f} m² ({gr['area_m2']/100:.1f}% of the field; cell-center "
     f"estimator, node count {gr['area_node_count_m2']:.1f} m²)"],
    ["∂r*/∂H ; ∂r*/∂ε_max",
     f"{sen['dr_dH']:.4f} m per m ; {sen['dr_deps_deg']:.4f} m per degree"],
    ["Area vs. B2 height (20→45 m)",
     f"{sen['area_vs_B2_height'][0][1]:.1f} → {sen['area_vs_B2_height'][-1][1]:.1f} m², "
     "monotone decreasing, saturating above 45 m"],
    ["Area vs. vehicle radius (1.0→2.5 m)",
     f"{sen['area_vs_vehicle_radius'][0][1]:.1f} → {sen['area_vs_vehicle_radius'][-1][1]:.1f} m², "
     "near-linear decrease"],
    ["Alternative metric check (limited claim)",
     "Q₂ = (1/r)·cos²(ε − 45°) still decreases in r on this instance, so it only "
     "verifies that r* (7.583 m) is invariant within this metric family, not the "
     "full station selection"],
])
spacer(doc)

# ============ III ============
h1(doc, "III. 可直接粘贴的段落（3.3–3.7 中英对照；3.1/3.2/3.5 仅英文+中文备注）")
para(doc, "【使用说明】3.3/3.4/3.6/3.7 每节先给可整段粘贴的英文（en 段落），随后附中文稿供核对内容与数字；"
          "3.1/3.2/3.5 仅英文段落 + 中文使用备注。粘贴后请统一用 Word 公式编辑器重录公式并编号。", indent=False)

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
para(doc, en, indent=False)
# 中文对照稿
para(doc, "令 p = (x, y) 为观测站圆心，即车辆等效圆盘中心在地面上的投影。"
          "可观测区域定义为三个约束的交集 Ω = C1 ∩ C2 ∩ C3。", indent=False)
para(doc, "C1（车辆几何）：车辆等效为半径 1.5 m 的圆盘，圆心须满足 1.5 ≤ x ≤ 98.5、1.5 ≤ y ≤ 98.5，"
          "且到各建筑矩形足迹的距离 d(p, B_i) ≥ 1.5（i = 1, …, 5）。该条件等价于车辆圆盘不越出场界、"
          "不侵入建筑，即建筑足迹的 1.5 m Minkowski 外扩缓冲。", indent=False)
para(doc, "C2（云台俯仰）：视线仰角 ε(p) = arctan(Δz / r(p))，其中 Δz = H1 − h_cam = 43 m，"
          "须满足 ε(p) ∈ [−10°, 80°]。由于目标恒高于相机，下界自动满足；上界等价于 "
          "r(p) ≥ r_min = Δz / tan 80° = 43 / 5.67128 ≈ 7.5821 m。几何上，这是以 T1 水平投影 "
          "T′ = (84.6410, 70.0000) 为圆心、半径 7.5821 m 的圆形禁区。", indent=False)
para(doc, "C3（视线遮挡）：视线为三维线段 L: (x, y, 2) → (84.6410, 70, 45)。对每个建筑长方体 "
          "[x0, x1] × [y0, y1] × [0, h_i]，用三维 slab（区间裁剪）法判断线段是否与其相交；"
          "按题面规定，触碰、相切或穿过边、面、顶点一律视为遮挡，数值实现保留 10⁻⁹ 容差。", indent=False)
para(doc, "优化准则：在 Ω 上最大化观测质量 Q(p) = 1 / r(p)。由于 Q 关于 r 严格单调递减，"
          "p* = argmax_{p∈Ω} Q(p) = argmin_{p∈Ω} r(p)，即在所有可行站点中取离目标水平投影最近者。"
          "该等价性把连续优化问题转化为对 r = r_min 圆弧的可行性判定，后文据此证明全局最优性。", indent=False)
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
      "shows that 78.8% of the circle is feasible; the blocked arc [160.75°, 236.89°] (76.15° in total) "
      "is produced exactly by building B2 and its 1.5 m clearance buffer, which matches the analytic "
      "estimate obtained by intersecting the circle with the inflated footprint [160.7°, 236.9°]. "
      "Hence the lower bound is attainable and r* = 7.5821 m with elevation ε* = 80° is the global "
      "optimum, with Q* = 0.1319 m⁻¹. A 0.1 m-resolution grid search over the whole field independently "
      "returns a minimum feasible distance of 7.5828 m (+0.0007 m, pure grid quantization), confirming "
      "the analytic result. Since the entire feasible arc of the r*-circle attains the same optimal "
      "value, the optimal set is a continuum — a structural multiplicity, not an artifact — which is "
      "precisely why tie-breaking rules are required.")
para(doc, en, indent=False)
# 中文先行稿（最终英译时按此中文稿翻译）
para(doc, "首先给出与建筑布局无关的闭式下界。由 C2，对任意 p ∈ Ω 有 "
          "r(p) ≥ r_min = (H1 − h_cam) / tan ε_max = 43 / tan 80° = 7.5821 m。"
          "该下界只依赖目标高度、相机高度和云台俯仰上限，与建筑布局、场界大小无关。"
          "若圆 r = r_min 上存在非空可行弧，则下界可达，于是全局最优值 r* = 7.5821 m、"
          "最优仰角 ε* = 80°（主动约束）、最优质量 Q* = 1 / r* = 0.1319 m⁻¹。", indent=False)
para(doc, "沿该圆均匀采样 200,000 个方位角，并逐点判定 C1 与 C3：约 78.8% 的圆周可行；"
          "被挡弧段为 160.75°–236.89°（合计 76.15°），全部由 B2 及其 1.5 m 缓冲造成。"
          "解析复核：B2 原始足迹对应的挡弧为 φ ∈ [172.4°, 221.9°]；叠加 1.5 m 缓冲后扩为约 "
          "[160.7°, 236.9°]，与数值采样一致。LOS 在该圆上没有额外增加遮挡：西侧被挡段已由几何约束覆盖，"
          "其余弧段的视线或从 B2 上方掠过，或位于 B2 东侧 x ≥ 79 的区域。", indent=False)
para(doc, "进一步用 0.1 m 全场网格独立搜索：最小可行 r = 7.5828 m，位于 (92.2, 69.4)，"
          "仅比解析下界高 0.0007 m，属于网格量化误差。因此 r* = 7.5821 m 是全局最优，"
          "而不是网格搜索得到的近似值。由于整段可行弧都取到同一最优值，最优解集是 r* 圆上一段连续弧"
          "（约 283.9°）；并列最优是结构性的，这正是需要 tie-breaking 的原因。", indent=False)
para(doc, "【中文备注】“解析下界 + 可行弧验证 + 网格交叉验证”三步走是本题的得分点，"
          "评审最忌讳“网格搜出来的最优”，这一段正面回应了 global optimality。")

h2(doc, "3.5 Tie-breaking rules（紧跟 3.4）")
code_block(doc, """Because every point of the feasible arc attains the same optimal value, we break
ties by a three-level lexicographic rule:
  T1 (safety-margin band)  with the geometric margin m(p) = min{ d(p, Bi) - 1.5,
      distance to the inset field boundary } (on the optimal arc the elevation slack
      is zero by construction, so m covers geometric boundaries only; the LOS
      clearance is reported separately), keep the band
      m(p) >= m* - 0.05 m, where m* = 9.6746 m is the true arc maximum, attained
      at phi = 56.50 deg where the B2-buffer distance equals the east-boundary
      distance.
  T2 (responsiveness)  within that band, choose the point with the shortest
      travel time from the nearest standby vehicle. Reachability inside the
      band is evaluated along obstacle-avoiding shortest paths; for the
      finally selected station the straight path to V4 happens to be clear,
      so the straight-line and detour times coincide (2.78 s).
  T3 (determinism)  if still tied, take the lexicographically smallest (x, y).
The rule yields the unique station p* = (88.8753, 76.2895) m, whose own margin
is 9.625 m (set by the east field boundary; 0.0001 m inside the band), with an
LOS clearance of 7.41 m and a travel time of 2.78 s from V4 (the nearest
vehicle, initially at (88, 68); its straight path is clear of all buildings).
Note: straight-line distances are lower bounds on travel time when the direct
segment crosses a building (e.g. V1, 32.21 s straight vs 34.36 s via the
shortest obstacle-avoiding detour).""")
para(doc, "【中文备注】报告值三个都齐了：坐标、距离 7.5821 m、仰角 80°——题面点名的三件套；"
          "务必区分 m*（弧上最大裕度 9.6746）与所选站裕度（9.625，带内最短可达）。")

h2(doc, "3.6 Sensitivity（放 Sensitivity Analysis 节）")
en = ("Two closed-form sensitivities follow immediately from r* = (H − h_cam)/tan 80°: "
      "∂r*/∂H = 1/tan 80° = 0.176 m per m of target altitude, and ∂r*/∂ε_max = −43·csc²(80°)·π/180 = "
      "−0.774 m per degree of the gimbal bound. More importantly, since the bound contains no "
      "environmental parameters and the feasible arc on the r_min-circle is non-empty, the optimal "
      "VALUE is robust to the building layout: perturbing building heights or positions changes only "
      "WHERE on the r*-circle the feasible arc lies, never the optimal distance itself (if some layout "
      "blocked the entire circle, the optimum would move outward to r > r_min — the conditional nature "
      "of this statement is stated explicitly). At the regional level, the observable area decreases "
      "monotonically with the height of B2 "
      f"({sen['area_vs_B2_height'][0][1]:.0f} → {sen['area_vs_B2_height'][-1][1]:.0f} m² as h_B2 grows "
      "from 20 m to 45 m, saturating once h_B2 reaches the target altitude) and decreases near-linearly "
      f"with the vehicle radius ({sen['area_vs_vehicle_radius'][0][1]:.0f} → "
      f"{sen['area_vs_vehicle_radius'][-1][1]:.0f} m² as R_veh grows from 1.0 m to 2.5 m); over the "
      "sampled ranges the B2 height moves the area about 4.4 times more in total, yet per unit of "
      "parameter change the vehicle radius is the stronger lever (≈427 vs ≈115 m² per m). Areas are "
      "cell-center (midpoint) estimates: the h = 0.1 m and h = 0.05 m midpoints agree to "
      "~0.03–0.04%, while the node-count convention runs ~0.4% higher; the regional scans use a "
      "0.25 m midpoint grid. The trends "
      "are robust. Finally, replacing the metric by Q₂ = (1/r)·cos²(ε − 45°), which additionally prefers "
      "mid-range elevation angles, leaves the optimum on the same r*-circle; since Q₂ is still "
      "decreasing in r on this instance, this checks only the invariance of r* within that metric "
      "family, not the full station selection.")
para(doc, en, indent=False)
# 中文先行稿（最终英译时按此中文稿翻译，注意“可行弧非空”的限定）
para(doc, "由 r* = (H1 − h_cam) / tan ε_max 可直接求偏导："
          "∂r*/∂H1 = 1 / tan 80° = +0.1763 m/m；"
          "∂r*/∂ε_max = −43·csc²(80°)·π/180 = −0.7738 m/deg；"
          "∂r*/∂h_cam = −0.1763 m/m。", indent=False)
para(doc, "这些闭式关系表明，最优值只由目标高度、相机高度和云台上限决定，对建筑布局不敏感。"
          "更准确地说，在可行弧非空的前提下，改变建筑高度或位置只会改变最优弧在圆上的位置与长度，"
          "不会改变 r* 和 Q*；如果环境变化使整条 r = r_min 圆都不可行，最优值才会外移。"
          "这是“值稳健、位置敏感”结论的适用条件。", indent=False)
para(doc, f"区域层面，可观测面积随 B2 高度增加而单调下降：h_B2 从 20 m 增到 45 m 时，"
          f"面积由约 {sen['area_vs_B2_height'][0][1]:.0f} m² 降到 {sen['area_vs_B2_height'][-1][1]:.0f} m²；"
          "h_B2 达到目标高度 45 m 后阴影饱和，继续增高不再改变面积。"
          f"面积随车辆半径增大近似线性下降：R_veh 从 1.0 m 增到 2.5 m 时，面积由约 "
          f"{sen['area_vs_vehicle_radius'][0][1]:.0f} m² 降到 {sen['area_vs_vehicle_radius'][-1][1]:.0f} m²。"
          "需要说明的是：这些扫描使用 0.25 m 单元中心网格，主面积（0.1 m 中点）与 0.05 m 中点"
          "相差仅 ~0.03–0.04%（收敛）；节点计数口径约偏高 0.4%，那是口径差而非估计器误差。"
          "单调趋势是稳健的。", indent=False)
para(doc, "最后，构造兼顾俯仰角居中的备选度量 Q2 = (1/r)·cos²(ε − 45°)，在可行域上重新求解："
          "最优仍在 r* 圆上（网格解 r = 7.583 m，ε ≈ 80.0°）。由于 Q2 仍随 r 单调下降，"
          "这一检验说明度量选择不改变最优值 r*；最优弧上具体站点的选择仍需 tie-breaking。", indent=False)
para(doc, "【中文备注】“值稳健—位置敏感”分解 + 面积扫描 + 备选度量检验，三层递进，"
          "模板自带的 Sensitivity Analysis 章节正好用这段。")

h2(doc, "3.7 结果陈述句（可直接放进摘要或 Conclusion）")
en = ("For Problem 1, the observable region of T1 covers about 5.61 × 10³ m² "
      f"({gr['area_m2']/100:.1f}% of the field). "
      "The optimal station is located at (88.88, 76.29) m with a horizontal distance of 7.5821 m and a "
      "line-of-sight elevation of exactly 80°, where Q attains its maximum 0.1319 m⁻¹; the optimality "
      "is proven analytically and verified numerically, and a three-level tie-breaking rule (margin "
      "band around the arc maximum m* = 9.675 m, then shortest travel within the band, then "
      "lexicographic order) selects "
      "the unique station on the 284°-feasible optimal arc.")
para(doc, en, indent=False)
# 中文先行稿（最终英译时按此中文稿翻译）
para(doc, "第一问中，T1 的可观测区域约为 5.6×10³ m²（约占场地的 56%）。"
          "最优站点位于 (88.8753, 76.2895) m，水平距离 r* = 7.5821 m，视线仰角恰为 80°，"
          "此时 Q 取最大值 0.1319 m⁻¹。该最优性由闭式下界、可行弧验证和 0.1 m 网格交叉验证共同证明；"
          "最优解集是 r* 圆上一段约 284° 的连续可行弧，本文用“最大裕度 → 带内最短可达 → 字典序”"
          "三级规则将其唯一化为 p*。", indent=False)
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
     "its 1.5 m buffer; right: margin profile relative to the arc maximum, m(p) − m* — the shaded "
     "horizontal strip is the 0.05 m tie-breaking band, the black pentagon (selected station, "
     "m − m* ≈ −0.05) sits at the band's lower edge, red open circle = the arc maximum at φ = 56.5°.",
     "坐标轴 φ (deg) / m − m* (m)；标 “p* (chosen station)” “m*” “T1′” “V4” “B2”；区分竖向灰带=被挡弧、横向浅蓝带=并列带"],
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
