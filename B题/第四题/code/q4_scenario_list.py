# -*- coding: utf-8 -*-
"""Emit the 74-scenario breakdown table (results/q4_scenario_list.md).

Reads q4_results.json's scenario_design and the scenario blocks, so the table
always matches the delivered run.
"""
import json
import math
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(BASE, "results", "q4_results.json"),
          encoding="utf-8") as f:
    R = json.load(f)
SD = R["scenario_design"]
cnt = SD["counts"]
reps = SD["reps"]
lines = ["# 第四问场景清单（74 个）", "",
         "评估窗 [0,60] s；扰动时刻 t=5 s（无中断）或 t_rec（有中断）。"
         "新告警 H=50 m，水平投影 = (50+R cosθ, 50+R sinθ)。", "",
         "## 计数核对", "",
         "| 类别 | 组合方式 | 数量 |", "|---|---|---|",
         f"| A 新告警 | 8 方位 × 3 距离 | {cnt['A_new']} |",
         f"| B 单车故障 | 5 辆选 1 | {cnt['B_fail']} |",
         f"| C 单中断 | t_rec ∈ {{10,20,30}} | {cnt['C_outage']} |",
         f"| D 故障×中断 | 5 × 3 | {cnt['D_fail_out']} |",
         f"| E 新告警×故障 | 3 代表 × {{V2,V4}} | {cnt['E_new_fail']} |",
         f"| F 新告警×中断 | 3 代表 × 3 个 t_rec | {cnt['F_new_out']} |",
         f"| G 三重组合 | 3 代表 × {{V2,V4}} × {{10,30}} s | {cnt['G_triple']} |",
         f"| **合计** |  | **{sum(cnt.values())}** |", "",
         "## A 新告警（24）", "",
         "| # | θ (°) | R (m) | T4 投影 (x,y) (m) |", "|---|---|---|---|"]
for k, s in enumerate(R["scen_new"], start=1):
    x = 50.0 + s["R"] * math.cos(math.radians(s["theta"]))
    y = 50.0 + s["R"] * math.sin(math.radians(s["theta"]))
    lines.append(f"| A{k:02d} | {s['theta']:g} | {s['R']:g} | "
                 f"({x:.2f}, {y:.2f}) |")
lines += ["", "## B 单车故障（5）", "", "| # | 故障车 |", "|---|---|"]
for k, s in enumerate(R["scen_fail"], start=1):
    lines.append(f"| B{k} | {s['failed']} |")
lines += ["", "## C 单中断（3）", "", "| # | t_rec (s) |", "|---|---|"]
for k, s in enumerate(R["scen_out"], start=1):
    lines.append(f"| C{k} | {s['t_rec']:g} |")
lines += ["", "## D 故障×中断（15）", "",
          "| # | 故障车 | t_rec (s) |", "|---|---|---|"]
for k, s in enumerate(R["scen_fail_out"], start=1):
    lines.append(f"| D{k:02d} | {s['failed']} | {s['t_rec']:g} |")
lines += ["", "## 新告警三个代表位置", "",
          "| 代表 | 场景 key | θ (°) | R (m) | 选取依据 |", "|---|---|---|---|---|"]
basis = {"best": "单扰动扫描中 t_last 最小",
         "mid": "t_last 中位数",
         "worst": "t_last 最大"}
for tag in ("best", "mid", "worst"):
    key = reps[tag]
    th = float(key[2:].split("_R")[0])
    rr = float(key.split("_R")[1])
    lines.append(f"| {tag} | {key} | {th:g} | {rr:g} | {basis[tag]} |")
lines += ["", "## E 新告警×故障（6）", "",
          "| # | 新告警代表 | 故障车 |", "|---|---|---|"]
for k, s in enumerate(R["scen_new_fail"], start=1):
    lines.append(f"| E{k} | {s['key']} | {s['failed']} |")
lines += ["", "## F 新告警×中断（9）", "",
          "| # | 新告警代表 | t_rec (s) |", "|---|---|---|"]
for k, s in enumerate(R["scen_new_out"], start=1):
    lines.append(f"| F{k} | {s['key']} | {s['t_rec']:g} |")
lines += ["", "## G 三重组合（12）", "",
          "| # | 新告警代表 | 故障车 | t_rec (s) |", "|---|---|---|---|"]
for k, s in enumerate(R["scen_triple"], start=1):
    lines.append(f"| G{k:02d} | {s['key']} | {s['failed']} | {s['t_rec']:g} |")
lines += ["", "## 关于是否为三重组合补 t_rec=20 s", "",
          "**决定：不补。** 三重组合取 t_rec 的两个端点 10/30 s，用于刻画"
          "“早恢复/晚恢复”的包络；t_rec=20 s 的中间取值已由 D 类"
          "（5 故障 × 3 个 t_rec=10/20/30，共 15 个场景）完整覆盖，"
          "且 D 类与 G 类的 t_last 对 t_rec 均呈斜率≈1 的线性关系，"
          "补 20 s 只会增加 6 个可预测的中间点而不改变结论。"
          "故维持 74 个场景不变。", ""]

out = os.path.join(BASE, "results", "q4_scenario_list.md")
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("written", out)
print("counts:", cnt, "total:", sum(cnt.values()))
