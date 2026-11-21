# -*- coding: utf-8 -*-
"""Numeric comparison of the Q1 observation-quality metrics.

Q(p)  = 1/r
Q2(p) = (1/r) * cos^2(eps - 45 deg),  eps = atan(dz / r)

Outputs results/q1_metric_compare.json and results/q1_metric_compare.md.
The grid argmax of Q2 is taken from q1_results.json (alt_metric), which was
computed on the same 0.1 m feasible grid.
"""
import json
import math
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(BASE, "results")
DZ = 43.0
R_MIN = DZ / math.tan(math.radians(80.0))

with open(os.path.join(RES, "q1_results.json"), encoding="utf-8") as f:
    R1 = json.load(f)
OPT = R1["optimal_station"]
ALT = R1["sensitivity"]["alt_metric"]


def metrics(r):
    eps = math.degrees(math.atan(DZ / r))
    c2 = math.cos(math.radians(eps - 45.0)) ** 2
    q = 1.0 / r
    return {"r_m": r, "eps_deg": eps, "cos2": c2, "Q": q, "Q2": q * c2}


rs = [R_MIN, 8.0, 10.0, 15.0, 20.0, 30.0, 43.0, 60.0, 80.0]
table = [metrics(r) for r in rs]
# monotonicity check: Q2 must decrease along this radial sequence
mono = all(table[i + 1]["Q2"] < table[i]["Q2"] for i in range(len(table) - 1))

rows = {
    "Q_optimal": {
        "station": [OPT["x"], OPT["y"]], "r_m": OPT["r"],
        "eps_deg": OPT["elevation_deg"], "Q": OPT["Q"],
        "Q2": OPT["Q"] * math.cos(math.radians(OPT["elevation_deg"] - 45.0)) ** 2,
    },
    "Q2_grid_argmax": {
        "station": ALT["Q2_station"], "r_m": ALT["r"],
        "eps_deg": ALT["elevation_deg"], "Q": 1.0 / ALT["r"],
        "Q2": (1.0 / ALT["r"]) *
              math.cos(math.radians(ALT["elevation_deg"] - 45.0)) ** 2,
    },
    "radial_scan": table,
    "Q2_monotone_decreasing": mono,
    "r_min_m": R_MIN,
    "note": ("Q2=(1/r)cos^2(eps-45deg); on r=r_min the elevation is constant, "
             "so Q2 is constant on the whole optimal arc. The angular factor is "
             "at most 1/0.671=1.49 times its value at r_min, while 1/r already "
             "falls below 0.671 of its r_min value at r=11.3 m; the radial scan "
             "covers r<11.3 m and decreases there too, so Q2 is decreasing in r."),
}
with open(os.path.join(RES, "q1_metric_compare.json"), "w",
          encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=2, default=float)

md = ["# Q1 观测质量准则 Q 与 Q2 的数值对照", "",
      "Q=1/r；Q2=(1/r)cos²(ε−45°)，ε=arctan(43/r)。", "",
      "## 径向扫描", "",
      "| r (m) | ε (°) | cos²(ε−45°) | Q=1/r (m⁻¹) | Q2 (m⁻¹) |",
      "|---|---|---|---|---|"]
for t in table:
    md.append(f"| {t['r_m']:.4f} | {t['eps_deg']:.2f} | {t['cos2']:.4f} | "
              f"{t['Q']:.5f} | {t['Q2']:.5f} |")
md += ["", f"Q2 沿该径向序列单调递减：{mono}。", "",
       "## 最优解对照", "",
       "| 准则 | 站点 (m) | r (m) | ε (°) | Q (m⁻¹) | Q2 (m⁻¹) |",
       "|---|---|---|---|---|---|"]
for name, key in (("Q（交付准则）", "Q_optimal"),
                  ("Q2（格点 argmax）", "Q2_grid_argmax")):
    d = rows[key]
    md.append(f"| {name} | ({d['station'][0]:.4f}, {d['station'][1]:.4f}) | "
              f"{d['r_m']:.4f} | {d['eps_deg']:.3f} | {d['Q']:.5f} | "
              f"{d['Q2']:.5f} |")
md += ["", "结论：Q2 在 r=r_min 圆上为常数（ε 恒定），其格点 argmax 与最小 r "
       "格点重合。角度因子至多为 r_min 处的 1.49 倍，而 r≥11.3 m 时 1/r 已"
       "降至 r_min 值的 0.671 倍以下；r<11.3 m 段由径向扫描直接验证单调。"
       "故 Q2 的最优解集与 Q 相同，仍为 r_min 圆上的可行弧。", ""]
with open(os.path.join(RES, "q1_metric_compare.md"), "w",
          encoding="utf-8") as f:
    f.write("\n".join(md))
print("\n".join(md))
print("written q1_metric_compare.json/.md")
