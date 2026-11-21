# -*- coding: utf-8 -*-
"""Export the canonical problem parameters (B1-B5, V1-V5, T1-T3) to
params.csv and params_table.md.

The values are read from q1_solve.py by AST literal evaluation, so the solver
is NOT executed.  The three alerts come from q1_solve.py (T1) and q2_lib.py
(T1-T3); both sources are cross-checked against each other.
"""
import ast
import csv
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)          # 第一题/
ROOT = os.path.dirname(BASE)          # B题/
sys.path.insert(0, os.path.join(ROOT, "第二题", "code"))
import q2_lib as L2                    # noqa: E402


def _literal(node):
    """literal_eval, unwrapping np.array([...]) / np.array((...))."""
    if isinstance(node, ast.Call):
        func = node.func
        name = func.attr if isinstance(func, ast.Attribute) else \
            getattr(func, "id", "")
        if name == "array" and len(node.args) == 1:
            return ast.literal_eval(node.args[0])
    return ast.literal_eval(node)


def literals(path, names):
    """Return {name: literal value} for module-level assignments in path."""
    tree = ast.parse(open(path, encoding="utf-8").read())
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id in names:
                    out[t.id] = _literal(node.value)
                elif isinstance(t, ast.Tuple) and isinstance(node.value, ast.Tuple):
                    # e.g. ``THETA1, R1, H1 = 30.0, 40.0, 45.0``
                    for elt, val in zip(t.elts, node.value.elts):
                        if isinstance(elt, ast.Name) and elt.id in names:
                            out[elt.id] = ast.literal_eval(val)
    return out


C = literals(os.path.join(HERE, "q1_solve.py"),
             {"FIELD", "O_POS", "R_VEH", "H_CAM", "SPEED",
              "ELEV_MIN", "ELEV_MAX", "BUILDINGS", "THETA1", "R1", "H1",
              "VEHICLES"})

# cross-check with the shared library used by Q2-Q4
assert C["BUILDINGS"] == L2.BUILDINGS, "B1-B5 differ between q1 and q2_lib"
assert [tuple(v) for v in C["VEHICLES"]] == [tuple(v) for v in L2.VEHICLES], \
    "V1-V5 differ between q1 and q2_lib"
assert (C["THETA1"], C["R1"], C["H1"]) == L2.ALERTS["T1"], "T1 differs"

ALERTS = [("T1", C["THETA1"], C["R1"], C["H1"]),
          ("T2", *L2.ALERTS["T2"]), ("T3", *L2.ALERTS["T3"])]


def tgt(theta, R):
    x = 50.0 + R * math.cos(math.radians(theta))
    y = 50.0 + R * math.sin(math.radians(theta))
    return x, y


rows = []          # (category, id, parameter, value, unit, note)


def add(cat, ident, param, value, unit, note=""):
    rows.append((cat, ident, param, value, unit, note))


add("field", "-", "field_size", "100", "m", "[0,100] x [0,100]")
add("field", "-", "dispatch_center_O", "(50, 50)", "m", "alerts given in (theta,R) about O")
add("vehicle", "-", "equivalent_disk_radius", C["R_VEH"], "m", "")
add("vehicle", "-", "camera_height", C["H_CAM"], "m", "above ground")
add("vehicle", "-", "speed", C["SPEED"], "m/s", "constant, no acceleration")
add("gimbal", "-", "pan_rate", "30", "deg/s", "")
add("gimbal", "-", "tilt_rate", "30", "deg/s", "both axes move together")
add("gimbal", "-", "elevation_min", C["ELEV_MIN"], "deg", "closed interval")
add("gimbal", "-", "elevation_max", C["ELEV_MAX"], "deg", "closed interval")
add("gimbal", "-", "observation_duration", "5", "s", "synchronized two-vehicle dwell")
for i, (x0, x1, y0, y1, h) in enumerate(C["BUILDINGS"], start=1):
    add("building", f"B{i}", "x_range", f"[{x0:g}, {x1:g}]", "m", "")
    add("building", f"B{i}", "y_range", f"[{y0:g}, {y1:g}]", "m", "")
    add("building", f"B{i}", "height", f"{h:g}", "m", "axis-aligned cuboid")
for i, (x, y) in enumerate(C["VEHICLES"], start=1):
    add("vehicle", f"V{i}", "initial_position", f"({x:g}, {y:g})", "m", "")
for name, th, R, H in ALERTS:
    x, y = tgt(th, R)
    add("alert", name, "azimuth_theta", f"{th:g}", "deg", "counter-clockwise from +x")
    add("alert", name, "horizontal_range_R", f"{R:g}", "m", "from dispatch center O")
    add("alert", name, "height_H", f"{H:g}", "m", "")
    add("alert", name, "horizontal_projection", f"({x:.4f}, {y:.4f})", "m",
        "exact x,y projection")
    add("alert", name, "r_min_geom", f"{(H - C['H_CAM']) / math.tan(math.radians(C['ELEV_MAX'])):.4f}",
        "m", "(H-h_cam)/tan(elev_max)")

csv_path = os.path.join(ROOT, "params.csv")
with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["category", "id", "parameter", "value", "unit", "note"])
    w.writerows(rows)

md = []
md.append("# 题设参数规范表（B 题）\n")
md.append("> 数据源：`第一题/code/q1_solve.py`（AST 字面量读取，不执行求解器）"
          "与 `第二题/code/q2_lib.py`；两处 B1–B5、V1–V5、T1 已交叉校验一致。\n")
md.append("## 全局常量\n")
md.append("| 参数 | 数值 | 单位 | 说明 |\n|---|---|---|---|")
for cat, ident, param, value, unit, note in rows:
    if cat in ("field", "gimbal") or (cat == "vehicle" and ident == "-"):
        md.append(f"| {param} | {value} | {unit} | {note} |")
md.append("\n## 建筑（轴对齐长方体）\n")
md.append("| 建筑 | x 区间 (m) | y 区间 (m) | 高度 (m) |\n|---|---|---|---|")
for i, (x0, x1, y0, y1, h) in enumerate(C["BUILDINGS"], start=1):
    md.append(f"| B{i} | [{x0:g}, {x1:g}] | [{y0:g}, {y1:g}] | {h:g} |")
md.append("\n## 观测车初始位置\n")
md.append("| 车辆 | x (m) | y (m) |\n|---|---|---|")
for i, (x, y) in enumerate(C["VEHICLES"], start=1):
    md.append(f"| V{i} | {x:g} | {y:g} |")
md.append("\n## 告警\n")
md.append("| 告警 | θ (°) | R (m) | H (m) | 水平投影 (x, y) (m) | r_min (m) |\n"
          "|---|---|---|---|---|---|")
for name, th, R, H in ALERTS:
    x, y = tgt(th, R)
    rmin = (H - C["H_CAM"]) / math.tan(math.radians(C["ELEV_MAX"]))
    md.append(f"| {name} | {th:g} | {R:g} | {H:g} | ({x:.4f}, {y:.4f}) | {rmin:.4f} |")
md.append("\n注：告警水平位置 = O + R(cosθ, sinθ)，O=(50,50)；"
          "r_min=(H−h_cam)/tan(ε_max) 为俯仰上界导出的最小水平距离。\n")

md_path = os.path.join(ROOT, "params_table.md")
with open(md_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md))

print(f"written {csv_path} ({len(rows)} rows)")
print(f"written {md_path}")
