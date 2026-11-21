# -*- coding: utf-8 -*-
"""生成《第四题_编程文档.docx》"""
import os
import platform
import sys

import numpy as np
import matplotlib as mpl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _docx_common import (new_doc, title, h1, h2, para, bullet, table,
                          code_block, load_results)

R4 = load_results("q4_results.json")
cnt = R4["scenario_design"]["counts"]

doc = new_doc()
title(doc, "第四题编程文档（实现结构与运行手册）",
      "Problem 4 · 复用 q2_lib 几何助手 + q4_lib4 重调度仿真器，无 scipy")

h1(doc, "I. 环境与总体结构")
para(doc, f"运行环境：Python {platform.python_version()}（≥3.10），numpy {np.__version__}、"
          f"matplotlib {mpl.__version__}。跨题复用：第四题代码通过仓库相对 sys.path 引入 "
          "第二题的 q2_lib（绕障 travel_time、区域栅格、slab 判交、NM 等，均经复核）。", indent=False)
table(doc, ["文件", "职责"], [
    ["q4_lib4.py", "基线回放（逐车任务记录）、t_p 状态快照（姿态感知）、姿态感知定点仿真器"
                   "（含死锁检测与 done 指针防重走）、重调度优化器（全结构快评 + top-12 坐标下降 + NM 精修）、"
                   "时间轴导出"],
    ["q4_core.py", "基线加载与自校验（回放必须复现 q2b 开始时刻）、keep-original 解析评估、"
                   f"六大类 {sum(cnt.values())} 个场景循环、代表性甘特、results/q4_results.json"],
    ["q4_figs.py", "6 张图（地图着色/方位曲线/故障柱状/中断曲线/代表甘特/全局散点），图内仅数字"],
    ["build_pptx_q4.py / build_docx_*_q4.py", "图集 PPTX 与三份文档（数字读自 JSON）"],
])

h1(doc, "II. 关键实现说明")
h2(doc, "II.1 done 指针定点仿真（本轮新修的坑）")
para(doc, "定点迭代若每轮从链头重走已完成任务，ready 会被越滚越大的值覆盖（回放曾把 T1 算成 206 s）。"
          "修复：每车维护 done[v] 指针，每轮只走 tasks[done[v]:]；walked 非空时 done[v] += len(walked)。"
          "第二题的 simulate 同款隐患已同步修复，并重验确认其最优解从 10.830 s 改进为 10.355 s（原搜索被污染）。")
h2(doc, "II.2 状态快照与姿态模型")
para(doc, "snapshot(recs, t) 按任务记录的时间窗分类（idle/enroute/slewing/waiting/observing/resetting/after），"
          "观测中 → locked_until = obs_end（告警锁定）、复位后 → 姿态回正东；转台中按进度线性插值姿态。"
          "simulate_init 的转台规则：行驶 > 0 必从 (0,0) 全角转台（题面行车回东规则）；仅零位移改派从当前姿态转。")
h2(doc, "II.3 重调度优化器")
para(doc, "对 C(|A|,2)^|待排| 个指派结构 × 复用车顺序全排列做“贪心初始化 + 快速仿真”全评，"
          "取前 12 结构做 (p₁×p₂) 候选坐标下降与全站 NM 精修；死锁结构由定点无进展判剔除。"
          "新告警 T4 的可观测域云用 0.2 m 单元中心栅格（NM 精修保证站点精度）。")

h1(doc, "III. 运行手册")
code_block(doc,
           "cd B题\\第四题\\code\n"
           "python -I q4_core.py           # 全场景（约 30-60 min，含 24 个 T4 区域）\n"
           "python -I q4_figs.py\n"
           "python -I build_pptx_q4.py\n"
           "python -I build_docx_model_q4.py\n"
           "python -I build_docx_code_q4.py\n"
           "python -I build_docx_paper_q4.py")
para(doc, "q4_core 启动时自动回放 2(2) 基线并断言与 q2b_results.json 一致（防基线漂移）。")

h1(doc, "IV. 参数入口与输出")
table(doc, ["参数/输出", "位置", "说明"], [
    ["新告警方位/距离网格", "THETAS, RS（q4_core）", "45° × {30,40,50}，可加密"],
    ["中断恢复时刻", "T_REC_LIST", "(5,30] 的代表分位"],
    ["组合场景代表集", "FAIL_REP 与 reps（由 A 类结果自动选取）", "最优/中位/最劣"],
    ["评估窗/扰动时刻", "window_end=60, disturb=5", "题面定值"],
    ["results/q4_results.json", "全部场景的 (η, t_last)、指派、站点、开始时刻、代表甘特段"],
    ["results/q4_summary.txt", "各类场景的收益统计镜像"],
])
para(doc, f"本轮规模：新告警 {cnt['A_new']} + 故障 {cnt['B_fail']} + 中断 {cnt['C_outage']} + "
          f"故障×中断 {cnt['D_fail_out']} + 新×故障 {cnt['E_new_fail']} + 新×中断 {cnt['F_new_out']} + "
          f"三重 {cnt['G_triple']}。")

doc.save(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "第四题_编程文档.docx"))
print("saved 第四题_编程文档.docx")
