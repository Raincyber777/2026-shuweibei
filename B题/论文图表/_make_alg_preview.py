# -*- coding: utf-8 -*-
"""Preview mock of the Algorithm-1 box (body-text float, NOT a paper figure).
仅示意排版效果：论文中由 Word/LaTeX 排版为文字，不插入本 PNG。"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "_preview_算法框示意.png")

matplotlib.rcParams.update({
    "font.family": ["Times New Roman", "SimSun"],  # 西文 Times，中文回退宋体
    "mathtext.fontset": "stix",
    "figure.dpi": 200,
})

fig, ax = plt.subplots(figsize=(6.3, 3.85))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

XL, XR = 0.045, 0.955
XN, XT, XI = 0.062, 0.098, 0.132   # 行号列 / 正文列 / for 体内缩进列
top, rule2, bot = 0.985, 0.905, 0.012

ax.plot([XL, XR], [top, top], color="k", lw=1.1)
ax.plot([XL, XR], [rule2, rule2], color="k", lw=0.5)
ax.plot([XL, XR], [bot, bot], color="k", lw=1.1)

ax.text(XL, (top + rule2) / 2,
        "算法 1  六槽五车“指派—复用顺序—站点坐标”联合优化",
        ha="left", va="center", fontsize=10.5, fontweight="bold")

rows = [
    ("", False, "输入：最早就绪表 r(v,a)；可行域判据 feasible(p,a)；"
                "v = 3 m/s、ω = 30 °/s、同步 τ = 5 s"),
    ("", False, "输出：最优指派 π*、复用顺序 o*、站点 {p*(v,a)}、"
                "完成时刻 S* = 10.355 s"),
    ("1", False, "对每告警 a ∈ {T1, T2, T3} 从 C(5,2)=10 个车辆对中选 1，"
                 "生成 10³ = 1000 个指派结构；"),
    ("", False, "按乐观界 est = maxₐ max(r(vᵢ,a), r(vⱼ,a)) 升序排列"
                "（est 忽略转台/同步/复位/复用冲突，为完成时刻下界）"),
    ("2", False, "for 每个结构（按 est 升序处理；若 est ≥ 当前最优 S 则剪枝"
                 "终止）do"),
    ("3", True, "枚举双任务车辆（≤ 2 辆、各 ≤ 2 种序）的任务排列，"
                "作为车内复用顺序"),
    ("4", True, "贪心初始化各车站点 p(v,a) ∈ Ωₐ"),
    ("5", True, "坐标下降逐维精修 → Nelder–Mead 收尾（约束 feasible(p,a)）"),
    ("6", True, "事件驱动时序仿真 → 完成时刻 S；死锁或不可行则剔除该候选"),
    ("7", False, "end for"),
    ("8", False, "对最优结构做全体站点 NM 抛光（2 轮），并对 top-12 结构"
                 "复精修（强化最优性支撑）"),
    ("9", False, "按 (S, Σₐ startsₐ) 字典序排序取 top-5；输出唯一最优"
                 "方案（S* = 10.355 s，基线 20.968 s）"),
]

y = 0.845
dy = 0.069
for num, ind, txt in rows:
    xc = XI if ind else XT
    if num:
        ax.text(XN, y, num, ha="left", va="center", fontsize=8.6,
                color="#444444")
    ax.text(xc, y, txt, ha="left", va="center", fontsize=9.3)
    y -= dy

fig.savefig(OUT, bbox_inches="tight", pad_inches=0.12)
print("saved preview, mpl", matplotlib.__version__)
