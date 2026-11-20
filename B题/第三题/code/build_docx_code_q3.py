# -*- coding: utf-8 -*-
"""生成《第三题_编程文档.docx》"""
import os
import platform
import sys

import numpy as np
import matplotlib as mpl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _docx_common import (new_doc, title, h1, h2, para, bullet, table,
                          code_block, load_results)

R = load_results("q3_results.json")

doc = new_doc()
title(doc, "第三题编程文档（实现结构与运行手册）",
      "Problem 3 · Python 标准库 + numpy/matplotlib，无 scipy 依赖")

h1(doc, "I. 环境与总体结构")
para(doc, f"运行环境：Python {platform.python_version()}（≥3.10 即可），numpy {np.__version__}、"
          f"matplotlib {mpl.__version__}（以实际环境为准）。关键点：正态分位数与 CDF 用标准库 "
          "statistics.NormalDist（inv_cdf/cdf），无需 scipy；所有脚本仓库相对路径。", indent=False)
table(doc, ["文件", "职责"], [
    ["q3_solve.py", "单文件核心：传播模型、闭式 s_max、(a,b) 约束域、10⁶ 样本精确几何 MC 验证、"
                    "方差贡献分解、三组敏感性、6 张图、results/q3_results.json"],
    ["build_pptx_q3.py", "图集 PPTX（SVG 矢量注入 + PNG 兜底，英文图注在备注页）"],
    ["build_docx_model_q3.py / build_docx_code_q3.py / build_docx_paper_q3.py",
     "三份 Word 文档，数字全部读自 results/q3_results.json"],
    ["_docx_common.py", "Word 样式助手（与第一、二题同源，Times New Roman+宋体，罗马数字分节）"],
])

h1(doc, "II. 关键实现说明")
h2(doc, "II.1 传播模型的向量化")
para(doc, "σ_ψ(s) = sqrt((σ(s)/40·180/π)² + 1.0)；换算系数 (180/π)/40 = 1.432395 deg/m 一次算好，"
          "全程显式区分 deg 与 rad（度/弧度混用是本问最典型错误源）。判据 P(|Δψ|≤5°)≥0.95 用双侧分位数 "
          "inv_cdf(0.975)=1.959964（P(|X|≤5)≥0.90 时对应 inv_cdf(0.95)=1.6449，两侧约定务必一致）。")
h2(doc, "II.2 蒙特卡洛验证（精确几何）")
para(doc, "把坐标系旋转到真实视线方向（目标位于 (40, 0)），直接采样 dx, dy ~ N(0, σ²) 与两项云台误差，"
          "指令角按精确 atan2(−dy, 40 − dx) 计算——不对几何做任何线性化，用以检验线性化传播本身的误差。"
          "n = 10⁶，numpy 向量化，固定种子 20261121 可复现；评估 |P 经验 − P 解析|、经验 σ、偏置、分位数最大偏差。")
h2(doc, "II.3 (a, b) 区域与等置信线")
para(doc, "可行域 {a ≥ 0, b ≥ 0, a+80b ≤ σ(s_max)}；等置信线族对每个置信度水平 lv 用"
          " inv_cdf(1−(1−lv)/2) 重算 a+80b 上界（fig3 四条线）。名义点 (0.3, 0.02) 的域内外判定在 JSON 中给出。")

h1(doc, "III. 运行手册")
code_block(doc,
           "cd B题\\第三题\\code\n"
           "python -I q3_solve.py          # 核心计算 + 6 张图（约 30 s）\n"
           "python -I build_pptx_q3.py     # 图集 PPTX\n"
           "python -I build_docx_model_q3.py\n"
           "python -I build_docx_code_q3.py\n"
           "python -I build_docx_paper_q3.py")

h1(doc, "IV. 参数入口")
table(doc, ["参数", "位置（q3_solve.py）", "注意"], [
    ["σ(s) = 0.3 + 0.02s", "SIG0, GSLOPE", "s_max 闭式解自动联动"],
    ["车目距离 d", "D_TGT = 40", "s_max 对 d 线性（斜率 2.048 m/m）"],
    ["云台两项误差", "SIG_GIMBAL_ZERO / SIG_GIMBAL_CTRL", "合成方差、C、s_max 全部联动"],
    ["判据 5° / 0.95", "PSI_LIM, CONF", "z 分位数自动重算（双侧约定）"],
    ["MC 样本数/种子", "N_MC, rng seed", "10⁶ 约 2 s；种子固定保证可复现"],
    ["置信度扫描", "LEVELS = (0.90, 0.95, 0.98, 0.99)", "等置信线与 fig6b 联动"],
])
para(doc, "复跑顺序：q3_solve → build_pptx → 三个 build_docx；文档数字全部读自 results/q3_results.json。")

h1(doc, "V. 输出说明")
table(doc, ["输出", "内容"], [
    ["results/q3_results.json", f"z={R['z_conf']:.6f}、σ_ψ 上限 {R['sigma_psi_max_deg']:.4f}°、"
                                f"s_max={R['s_max_m']:.4f} m、at_80（σ/P/缺口/超差）、ab_region（含名义点判定）、"
                                "contributions（8 个 s 点的方差占比）、monte_carlo（5 点验证）、sensitivity 三组"],
    ["figures/fig1–fig6", "SVG + PNG（300 dpi），图内仅数字刻度"],
    ["第三题_图集.pptx", "6 页矢量幻灯，英文图注在备注页"],
    ["results/q3_summary.txt", "终端摘要镜像"],
])
para(doc, f"摘要级结论：s_max = {R['s_max_m']:.2f} m；s=80 名义模型 P = {R['at_80']['P']:.4f} 不达标；"
          f"80 m 达标条件 a ≥ 0, b ≥ 0, a + 80b ≤ {R['ab_region']['a_plus_80b_max_m']:.4f} m；"
          f"贡献交叉点 s = {R['s_crossover_m']:.2f} m；MC 验证 |ΔP| ≤ 3×10⁻⁴。")

doc.save(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "第三题_编程文档.docx"))
print("saved 第三题_编程文档.docx")
