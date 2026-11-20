# -*- coding: utf-8 -*-
"""Build 第二题_编程文档.docx (Chinese code/implementation document)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _docx_common import (new_doc, title, h1, h2, para, bullet, table,
                          code_block, load_results)

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "第二题_编程文档.docx")
RA = load_results("q2a_results.json")
RB = load_results("q2b_results.json")

doc = new_doc()
title(doc, "第二题编程文档（实现结构与运行手册）",
      "2026 数维杯 B 题 Problem 2 · Python 3.10 · numpy/matplotlib/python-pptx/python-docx")

h1(doc, "I. 程序总体结构")
rows = [
    ["q2_lib.py", "共享库：题目常数、建筑/车辆、三约束可观测域（栅格+3D slab 判交）、圆弧游程、"
                  "指向角/转云台时长、wrap180、无依赖 Nelder-Mead"],
    ["q2a_core.py", "子问题 2(1)：Ω₂ 栅格、r_min 圆弧分析、闭式下界证书、10 个车辆对两级候选搜索+NM 精修、"
                    "最优族 1 维 tie-breaking、蒙特卡洛验证、退化与敏感性 → q2a_results.json"],
    ["q2b_core.py", "子问题 2(2)：三告警可观测域、最早就绪表 r(v,a)、1000 指派结构 × 顺序完备枚举（乐观界剪枝）、"
                    "贪心初始化+坐标下降+NM 精修、死锁定点检测、最近指派基线、参数扰动敏感性 → q2b_results.json"],
    ["q2_figs.py", "10 张图（仅数字刻度，无任何文字）→ figures/*.svg+.png"],
    ["build_pptx_q2.py", "图集 PPTX（SVG 矢量注入 + PNG 兜底，英文图注写入备注页）"],
    ["build_docx_model_q2.py / build_docx_code_q2.py / build_docx_paper_q2.py",
     "三份 Word 文档，数字全部读自 results/*.json"],
    ["_docx_common.py", "Word 样式助手（Times New Roman+宋体、罗马数字分节、表格/代码块）"],
]
table(doc, ["文件", "职责"], rows)

h1(doc, "II. 关键算法实现")
h2(doc, "II.1 可观测域（与第一题同源，按目标泛化）")
para(doc, "0.1 m 全场栅格；C1 用点到轴对齐矩形距离 ≥1.5 m；C2 闭式 r ≥ (H−2)/tan80°；C3 为相机(2 m)到目标(H m)"
          "三维线段与 5 个长方体的 slab 区间判交，±1e-9 容差把“相切”保守判为遮挡。三告警 Ω₁、Ω₂、Ω₃ 面积分别为 "
          f"{RB['region_areas']['T1']:.1f}、{RB['region_areas']['T2']:.1f}、{RB['region_areas']['T3']:.1f} m²。")
h2(doc, "II.2 2(1) 的两级候选搜索（有效下界剪枝）")
para(doc, "把站点用目标极坐标 (d,φ) 参数化后，G=√((d₁²+d₂²)/2)/|sin(φ₂−φ₁)| 仅依赖 4 个标量——这是把 O(N²) 几何计算"
          "化为标量式的关键。对每个车辆对：①粗阶段以步长抽样（每侧 ≤4000 点）全交叉得初始 incumbent；"
          "②精阶段用有效下界 G ≥ (d₁+d₂)/2 将两侧候选剪枝到 (d ≤ 2·inc·1.10 − d_伙伴min) 后全交叉；"
          "③Nelder-Mead 在 (d₁,φ₁,d₂,φ₂) 连续空间精修（严格可行性+鲁棒裕度罚函数）。"
          "证书：全局下界 G*=(d₁+d₂)/2≥r_min 的取等条件由 90° 配对族数值验证成立。")
h2(doc, "II.3 2(1) 的 tie-breaking 族优化")
para(doc, "最优解集是一维族 {d₁=d₂=r_min, |Δφ|=90°}。在 0.01° 极角网格上取 (sum travel, max travel) 字典序最小，"
          "前 400 名逐个做直线路径可行性检查（不入建筑 1.5 m 缓冲），首个通过者即为最终站对。")
h2(doc, "II.4 2(2) 的时序仿真（定点迭代 + 死锁检测）")
para(doc, "每车维护 (chain_ready, chain_pos)；每轮逐车沿任务链推进：自身就绪 rd 可立即记录（它只依赖自身链），"
          "但链推进需同伴就绪已知；一轮无链推进且仍有告警未定 → 循环依赖（互等死锁）→ 该 (指派,顺序) 不可行。"
          "收敛后目标 = max(三告警开始时刻)。")
h2(doc, "II.5 2(2) 的枚举 + 精修")
para(doc, "1000 组合按乐观界 est=max_a(两成员 r) 升序排列，est ≥ 当前最优即剪枝断言（本例最优 10.83 s，est 上界 10.2 s，"
          "故全部评估）；每组合贪心初始化 + 双任务车 (p₁×p₂) 候选坐标下降；对最优 12 个结构做全局目标 NM 精修（所有站点、"
          "严格可行性罚函数），二级 tie-breaking 取告警开始时刻之和最小者唯一化。")
h2(doc, "II.6 蒙特卡洛与核验")
para(doc, "2(1)：20 万样本按视线求交，RMSE/P95 与闭式值对照（0.1436/0.1437、0.2486/0.2486）。"
          "2(2)：r(v,a) 表逐项手核；甘特图逐段核对行驶/转云台/等待/5 s/复位。")

h1(doc, "III. 运行手册")
code_block(doc,
           "cd B题\\第二题\\code\n"
           "python -I q2a_core.py        # 2(1) 核心计算（约 6-8 min）\n"
           "python -I q2b_core.py        # 2(2) 核心计算（约 4-5 min）\n"
           "python -I q2_figs.py         # 10 张图\n"
           "python -I build_pptx_q2.py   # 图集 PPTX\n"
           "python -I build_docx_model_q2.py\n"
           "python -I build_docx_code_q2.py\n"
           "python -I build_docx_paper_q2.py")
para(doc, "依赖：numpy、matplotlib、python-pptx、python-docx、lxml、Pillow。-I 隔离模式运行以避免本地脚本注入。"
          "所有脚本仅用标准库+上述依赖，无需 scipy（NM 为自实现）。")

h1(doc, "IV. 参数入口")
rows = [
    ["告警 (θ,R,H)", "q2_lib.ALERTS", "改后自动重算 r_min、Ω 与调度"],
    ["方位角误差 σ", "q2_lib.SIGMA_AZ（1°）", "DRMS 与 σ 严格线性"],
    ["车速 / 云台转速", "q2_lib.SPEED / OMEGA", "2(2) 时序与就绪表随之变化"],
    ["行驶时限", "q2_lib.TRAVEL_LIMIT_S（30 s）", "仅 2(1) 使用"],
    ["鲁棒裕度", "q2a_core.CLR_LOS / MAR_C1 / TIE_CLR / TIE_MAR", "刀锋解防护强度"],
    ["观测时长", "q2b_core.OBS_LEN（5 s）", "复用链延迟随之变化"],
]
table(doc, ["参数", "位置", "说明"], rows)
para(doc, "改参数重跑顺序：q2a_core → q2b_core → q2_figs → build_pptx → 三个 build_docx；"
          "文档数字全部读自 results/*.json，自动同步，不要手改文档数字。")

h1(doc, "V. 输出说明")
rows = [
    ["results/q2a_results.json", "certificate（下界/证书/90°族）、pair_table（10 组合对照）、chosen（最终站对："
                                 f"{RA['chosen']['vehicles']}，DRMS={RA['chosen']['DRMS_m']:.4f} m）、degeneracy、sensitivity"],
    ["results/q2b_results.json", "r_va_table、LB、optimized（指派/顺序/站点/开始时刻）、heuristic、top5_structures、"
                                 "gantt_opt/gantt_heu（甘特段）、sensitivity_speed_omega"],
    ["results/q2a_data.npz", "Ω₂ 栅格掩码、r_min 圆弧布尔（作图用）"],
    ["figures/*.svg+.png", "fig1–fig10（数字刻度，无文字）"],
    ["第二题_图集.pptx", "10 页，SVG 矢量可转形状手改，英文图注在备注页"],
]
table(doc, ["输出", "内容"], rows)
para(doc, "摘要级结论：2(1) 选 V3+V5，站 (5.2787,73.3912)/(11.9201,78.2501)，d₁=d₂=5.8188 m，γ=90°，B=8.229 m，"
          "DRMS=0.1016 m（95% 圆 0.2486 m），行驶 (5.11,13.61) s；2(2) 优化目标 10.830 s"
          "（T1 1.532 / T2 6.994 / T3 10.830），基线 30.207 s，改进 19.38 s。")

doc.save(OUT)
print("saved", OUT)
