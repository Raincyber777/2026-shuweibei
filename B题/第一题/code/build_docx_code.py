# -*- coding: utf-8 -*-
"""生成《第一题_编程文档.docx》—— 代码结构、算法说明、运行方式、结果汇总、代码清单。"""
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

doc = new_doc()
title(doc, "2026 “数维杯”B题  第一问编程文档",
      "q1_solve.py 实现说明与运行手册")

# ============ I ============
h1(doc, "I. 环境与运行方式")
import platform, numpy as _np, matplotlib as _mpl
para(doc, f"运行环境：Python {platform.python_version()}（Windows 11），numpy {_np.__version__}、"
          f"matplotlib {_mpl.__version__}（以实际环境为准，Python ≥ 3.10 即可）；"
          "交付物生成另需 python-docx、python-pptx、lxml、Pillow。"
          "全部路径按脚本相对定位（BASE = 脚本上两级目录），仓库拷到任何机器均可直接运行。", indent=False)
code_block(doc, r"""文件夹结构
B题\第一题\
├── 第一题_建模文档.docx        ← 建模（本文件夹内另两份之一）
├── 第一题_编程文档.docx        ← 本文档
├── 第一题_论文素材文档.docx    ← 给论文手的英文素材
├── 第一题_图集.pptx            ← 6 张图（SVG 矢量，可手改）
├── code\                       ← 全部源代码
│   ├── q1_solve.py             ← 核心求解（建模文档的全部数值与图）
│   ├── build_pptx.py           ← 生成图集 PPTX（SVG 矢量注入）
│   ├── build_docx_model.py / build_docx_code.py / build_docx_paper.py
│   └── _docx_common.py         ← Word 文档样式助手
├── figures\                    ← fig1–fig6 的 .svg 与 .png
└── results\                    ← q1_results.json、q1_summary.txt""")
para(doc, "运行方式（在 code\\ 目录下）：python q1_solve.py。耗时约 40 s（0.1 m 网格 1001×1001 向量化判定 + "
          "20 万点圆弧采样 + 敏感性批量扫描 + 6 张图）。所有数值写入 results/q1_results.json，"
          "终端同时打印摘要 results/q1_summary.txt。", indent=False)

# ============ II ============
h1(doc, "II. q1_solve.py 代码结构")
table(doc, ["模块/函数", "职责", "对应建模文档章节"], [
    ["常量区", "场域、5 栋建筑、车辆初值、告警 T1、云台范围、R_MIN 闭式下界", "IV 4.1–4.3"],
    ["dist_to_rect(px, py, rect)", "点到轴对齐矩形距离（向量化），实现 C1 的建筑缓冲", "IV 4.2"],
    ["los_blocked(px, py, buildings)", "slab 法三维线段–长方体判交，相切判遮挡（容差 1e-9）", "IV 4.4"],
    ["constraint_masks(X, Y, …)", "一次性返回 C1、C2、C3 三个布尔掩码与 r 场", "IV 4.5"],
    ["make_grid(step, center)", "场域等距网格；center=True 生成单元中心网格（面积估计用）", "V 5.4"],
    ["bool_runs(flag)", "周期布尔序列的连续 True 游程（处理 0°/360° 环绕）", "V 5.2"],
    ["margins / band / best", "tie-breaking 三级规则：最大裕度 → 0.05 m 带内最短可达 → 字典序", "V 5.3"],
    ["seg_box_dist(x0, y0, building)", "视线线段到建筑长方体的最小距离（密集采样），报告 LOS 净空", "V 5.4"],
    ["path_length(p, q) / _seg_hits_rect", "绕障最短路径（1.5 m 膨胀矩形的可视图 + Dijkstra）；"
     "直线净空时返回直线长度，并给出路径是否受阻标志", "V 5.4 / 行驶时间"],
    ["敏感性扫描区", "r* 对 H、ε_max 闭式表；区域面积对 B2 高度、车辆半径重扫；备选度量 Q₂", "VI"],
    ["绘图区（6 张图）", "fig1 可观测区域、fig2 约束分层、fig3 最优弧+裕度曲线、fig4/5 敏感性、fig6 三维 LOS", "IV–VI"],
    ["results 汇出区", "q1_results.json + 终端摘要", "—"],
])
spacer(doc)

# ============ III ============
h1(doc, "III. 核心算法说明")
h2(doc, "3.1 可观测区域的栅格化计算")
para(doc, "全场按 0.1 m 打网格（1001×1001 ≈ 1.0×10⁶ 点），全部约束向量化：C1 为边界比较与 5 次矩形距离判定；"
          "C2 为一次 r 场比较（r ≥ 7.5821 − 10⁻⁹）；C3 对每栋建筑各做一次向量化 slab 判交。"
          "三掩码按位与即得 Ω 的 0-1 图。面积取单元中心（中点）估计：在步长 h 的中心网格上统计可行点数 × h²，"
          "每个节点代表一个完整单元，避免 [0,100] 节点计数向外的半单元偏差（后者约高 0.3–0.4%，"
          "两种口径都在 JSON 中报告）；0.05 m 中点网格验证收敛（5610.4 → 5608.5 m²，Δ < 0.04%）。", indent=False)
h2(doc, "3.2 slab 判交与“相切即遮挡”")
para(doc, "线段参数化为 P(t) = P₀ + t·d, t ∈ [0,1]。对每轴求入/出参数并累计交集；"
          "三轴区间交集非空且与 [0,1] 相交即为遮挡。题面规定相切（触碰边、面、顶点）也算遮挡，"
          "故判交比较统一放宽 10⁻⁹ 容差，确保数值上恰好擦过的情形被保守地判为遮挡。"
          "这是全题最容易出错的环节：必须做三维判交（线段高度随水平位置线性上升），"
          "不能只在水平面内判线段与矩形相交。", indent=False)
h2(doc, "3.3 最优弧的采样与游程提取")
para(doc, "在 r = R_MIN 圆上以 20 万个方位角采样（0.0018° 分辨率），对每点判 C1 与 C3（C2 由构造成立）。"
          "bool_runs 把周期布尔序列还原为连续弧段区间，环绕 0°/360° 的游程做了模 360 处理。"
          "数值端点与解析估计（B2 缓冲几何）互相印证（见建模文档 5.2）。", indent=False)
h2(doc, "3.4 tie-breaking 实现")
para(doc, f"对圆弧每点计算几何安全裕度 m(p) = min(各建筑 d(p,Bᵢ) − 1.5, 到四边距离)，"
          f"弧上真实最大值 m* = {arc['m_star_margin_m']:.4f} m（φ = {arc['m_star_phi_deg']:.2f}°，"
          "该点 B2 缓冲距离与东场界距离恰好平衡）；随后在 m ≥ m* − 0.05 m 的并列带内比较 5 辆车的"
          f"行驶时间取最短，得最终站点 p*（其自身裕度 {opt['margin_m']:.4f} m，来源为东侧场界，"
          "以 0.0001 m 余量入带）；若仍并列按 (x, y) 字典序兜底（本例未触发）。"
          "JSON 同时存储 m*（arc.m_star_margin_m）与所选站裕度（optimal_station.margin_m），勿混淆。", indent=False)
h2(doc, "3.5 敏感性批量计算")
para(doc, "区域面积扫描改用 0.25 m 网格（401×401）以控制耗时：替换 B2 高度（20–45 m，7 档）或车辆半径"
          "（1.0–2.5 m，4 档）后重算三约束并积分面积。r* 对 H、ε_max 的敏感性直接用闭式表达式生成，无需求解。", indent=False)
h2(doc, "3.6 计算量与稳定性")
para(doc, "主网格约 1.0×10⁶ 点 × 5 建筑 × O(10) 向量化运算 ≈ 5×10⁷ 浮点操作/约束，总耗时 < 40 s；"
          "内存峰值约 100 MB（float64 临时数组）。数值稳定：判交容差 10⁻⁹ 与网格步长 0.1 m 相比可忽略，"
          "网格加密一倍时面积变化 < 0.5%。", indent=False)

# ============ IV ============
h1(doc, "IV. 关键数值结果汇总")
table(doc, ["项目", "数值"], [
    ["T1 水平投影", "(84.6410, 70.0000) m，高度 45 m"],
    ["闭式下界 r* = (H−h_cam)/tan80°", f"{R['r_min_closed_form']:.4f} m"],
    ["最优质量 Q*", f"{R['q_star']:.4f} m⁻¹（仰角恰为 80°）"],
    ["最优站点（tie-breaking 后）", f"({opt['x']:.4f}, {opt['y']:.4f}) m，φ = {opt['phi_deg']:.2f}°"],
    ["弧上最大裕度 m* / 所选站裕度",
     f"{arc['m_star_margin_m']:.4f} m @ φ={arc['m_star_phi_deg']:.2f}° / "
     f"{opt['margin_m']:.4f} m（带内最短可达点，来源为东侧场界）"],
    ["最近车辆与行驶时间", f"V4（(88,68)）→ {opt['travel_time_s']:.2f} s（直路径净空）"],
    ["各车行驶时间（直线/绕障）",
     "；".join(f"{k}: {v:.2f}/{opt['travel_time_all_path'][k]:.2f} s"
               for k, v in opt["travel_time_all"].items()) +
     "（直线为下界；V1 直线穿 B1/B5/B2，绕行后 34.36 s）"],
    ["最优弧可行比例", f"{arc['feasible_fraction']*100:.1f}%（被挡 {arc['blocked_total_deg']:.2f}°："
                       f"[{arc['blocked_runs_deg'][0][0]:.2f}°, {arc['blocked_runs_deg'][0][1]:.2f}°]）"],
    ["网格验证最小 r", f"{gr['best_r']:.4f} m @ (92.2, 69.4)（+{gr['r_diff_vs_analytic']:.4f} m）"],
    ["可观测区域面积", f"{gr['area_m2']:.1f} m²（0.1 m 单元中心估计；节点计数 {gr['area_node_count_m2']:.1f} m²）"],
    ["∂r*/∂H₁ ; ∂r*/∂ε_max", f"{sen['dr_dH']:.4f} m/m ; {sen['dr_deps_deg']:.4f} m/deg"],
    ["备选度量 Q₂ 最优", f"仍在 r* 圆上（r = {sen['alt_metric']['r']:.3f} m，ε = "
                          f"{sen['alt_metric']['elevation_deg']:.1f}°）"],
])
spacer(doc)

# ============ V ============
h1(doc, "V. 参数修改入口")
table(doc, ["要改什么", "位置（q1_solve.py）", "注意"], [
    ["目标告警 (θ, R, H)", "常量区 THETA1, R1, H1", "T1 与 R_MIN 会自动联动"],
    ["建筑布局/高度", "常量区 BUILDINGS 五元组", "遮挡、缓冲、面积全部自动联动"],
    ["车辆半径 / 速度 / 相机高度", "R_VEH, SPEED, H_CAM", "R_VEH 同时作用于缓冲与场界内缩"],
    ["云台俯仰范围", "ELEV_MIN, ELEV_MAX", "R_MIN 闭式下界随之改变"],
    ["网格步长", "STEP（主网格）、STEP_S（敏感性扫描）", "步长减半耗时约 ×4"],
    ["tie-breaking 裕度带", "band = margins >= m_star − 0.05", "0.05 m 可按需放宽"],
])
spacer(doc)
para(doc, "图表可直接复用：figures/ 下每张图有 .svg（矢量，PPT 中右键“转换为形状”后可编辑文字与图形）"
          "与 .png（300 dpi 级预览）。图内刻意不含任何文字与字母、仅保留数字刻度，"
          "供论文排版时在 PPT 中自行补注英文标注（赛事规定图内不得出现中文）。", indent=False)

# ============ VI ============
h1(doc, "VI. 完整代码清单（code/q1_solve.py）")
with open(os.path.join(BASE, "code", "q1_solve.py"), encoding="utf-8") as f:
    src = f.read()
code_block(doc, src, size=8)

out = os.path.join(BASE, "第一题_编程文档.docx")
doc.save(out)
print("saved", out)
