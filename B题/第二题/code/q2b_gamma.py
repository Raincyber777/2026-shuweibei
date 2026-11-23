# -*- coding: utf-8 -*-
"""Q2(2) intersection-geometry audit and gamma-constrained re-solve.

Part 1: for the delivered time-optimal scheme, compute for T1/T2/T3
    d1, d2 (horizontal station-target ranges), gamma (intersection angle),
    G = sqrt((d1^2+d2^2)/2)/|sin(gamma)| (m), DRMS = sigma_rad * G; do the
    same for the 0.5 m clearance-robust variant, whose accuracy is not
    qualified.
Part 2: re-solve the T1 station pair of the same assignment/order structure
    under gamma in [30, 150] deg and report the time cost.

Outputs: results/q2b_precision.json, results/q2b_precision.md
"""
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from q2_lib import (ALERTS, BUILDINGS, FIELD, H_CAM, OMEGA, R_VEH, SPEED,
                    TARGETS, TARGET_H, R_MIN_GEO, VEHICLES, dist_to_rect,
                    make_grid, pointing_angles, region_masks, travel_time,
                    wrap180)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES_DIR = os.path.join(BASE, "results")
OBS_LEN = 5.0
SIGMA_RAD = math.radians(1.0)
GAMMA_LO, GAMMA_HI = 30.0, 150.0

with open(os.path.join(RES_DIR, "q2b_results.json"), encoding="utf-8") as f:
    R = json.load(f)
OPT = R["optimized"]
ALERTS3 = ["T1", "T2", "T3"]


def pair_geometry(st1, st2, a):
    tgt = np.asarray(TARGETS[a], float)
    u1, u2 = tgt - np.asarray(st1, float), tgt - np.asarray(st2, float)
    d1, d2 = float(np.linalg.norm(u1)), float(np.linalg.norm(u2))
    cosg = float(np.dot(u1, u2) / (d1 * d2))
    gam = math.degrees(math.acos(max(-1.0, min(1.0, cosg))))
    G = math.sqrt((d1 * d1 + d2 * d2) / 2.0) / abs(math.sin(math.radians(gam)))
    # exact covariance Sigma = A^{-1} D A^{-T}, D=diag(d1^2 sig^2, d2^2 sig^2)
    A = np.array([[-(u1[1] / d1), u1[0] / d1],
                  [-(u2[1] / d2), u2[0] / d2]])
    D = np.diag([d1 * d1 * SIGMA_RAD ** 2, d2 * d2 * SIGMA_RAD ** 2])
    Sigma = np.linalg.inv(A) @ D @ np.linalg.inv(A).T
    lam = np.sort(np.linalg.eigvalsh(Sigma))
    return {"d1_m": d1, "d2_m": d2, "gamma_deg": gam, "G_m": G,
            "DRMS_m": SIGMA_RAD * G,
            "r95_m": SIGMA_RAD * G * math.sqrt(5.991),
            "Sigma_eig_m2": [float(lam[0]), float(lam[1])],
            "axis_ratio_variance": float(lam[1] / lam[0]),
            "axis_ratio_linear": float(math.sqrt(lam[1] / lam[0])),
            "r95_semi_axes_m": [float(math.sqrt(5.991 * lam[1])),
                                float(math.sqrt(5.991 * lam[0]))]}


# ---------------------------------------------------------------- part 1
rows = []
for a in ALERTS3:
    vs = OPT["assignment"][a]
    sts = [OPT["stations"][f"V{v}"][a] for v in vs]
    g = pair_geometry(*sts, a)
    g.update({"alert": a, "pair": [int(v) for v in vs],
              "stations": [[round(x, 4) for x in s] for s in sts]})
    rows.append(g)
    print(f"{a} pair {vs}: d=({g['d1_m']:.3f},{g['d2_m']:.3f}) "
          f"gamma={g['gamma_deg']:.2f} G={g['G_m']:.2f} "
          f"DRMS={g['DRMS_m']:.3f} r95={g['r95_m']:.3f}")

# geometry of the 0.5 m clearance-robust variant (accuracy is not qualified)
RB = R.get("robust_05") or {}
rb_geom = {}
if RB.get("obj_s") is not None:
    for a in ALERTS3:
        vs = RB["assignment"][a]
        sts = [RB["stations"][f"V{v}"][a] for v in vs]
        g = pair_geometry(*sts, a)
        g.update({"alert": a, "pair": [int(v) for v in vs],
                  "stations": [[round(x, 4) for x in s] for s in sts]})
        rb_geom[a] = g
        print(f"robust {a} pair {vs}: gamma={g['gamma_deg']:.2f} "
              f"DRMS={g['DRMS_m']:.3f}")

# ------------------------------------------------ part 2: constrained T1
# Build the feasible clouds with the same subsampling as q2b_core (the full
# 0.1 m grid has ~5.6e5 points; per-point path planning on it is prohibitive).
SUB_TARGET = 15000


def feasible_cloud(a):
    X, Y = make_grid(0.1)
    c1, c2, c3, _ = region_masks(X, Y, TARGETS[a], TARGET_H[a],
                                 R_MIN_GEO[a])
    p = np.column_stack([X[c1 & c2 & c3], Y[c1 & c2 & c3]]).astype(float)
    stride = max(1, int(round(len(p) / SUB_TARGET)))
    return p[::stride]


pts = feasible_cloud("T1")
pts3 = feasible_cloud("T3")
print("T1 feasible cloud:", len(pts), " T3:", len(pts3))


def geom_arrays(p, a):
    dx = TARGETS[a][0] - p[:, 0]
    dy = TARGETS[a][1] - p[:, 1]
    rr = np.hypot(dx, dy)
    az = wrap180(np.degrees(np.arctan2(dy, dx)))
    el = np.degrees(np.arctan((TARGET_H[a] - H_CAM) / np.maximum(rr, 1e-12)))
    return az, el, np.maximum(np.abs(az), el) / OMEGA, rr


def top_by_ready(p, a, x0, k):
    az, el, sl, rr = geom_arrays(p, a)
    tr = np.array([travel_time(x0, tuple(q)) for q in p])
    ready = tr + sl
    idx = np.argsort(ready)[:k]
    return p[idx], tr[idx], sl[idx], rr[idx], az[idx], el[idx]


K1 = 350
P3, TR3, SL3, RR3, AZ3, EL3 = top_by_ready(pts, "T1", tuple(VEHICLES[2]), K1)
P5, TR5, SL5, RR5, AZ5, EL5 = top_by_ready(pts, "T1", tuple(VEHICLES[4]), K1)
print(f"candidates: V3 {len(P3)}  V5 {len(P5)}")

# V3's T3 station: start from the delivered one, then refine later.
ST3_T3 = np.array(OPT["stations"]["V3"]["T3"], float)
az_t3, el_t3, _ = pointing_angles(ST3_T3, TARGETS["T3"], TARGET_H["T3"])
sl_t3 = max(abs(az_t3), el_t3) / OMEGA
TR_T3 = np.array([travel_time(tuple(p), tuple(ST3_T3)) for p in P3])
tail3 = OBS_LEN + SL3 + TR_T3 + sl_t3      # T3 ready - T1 start
base3 = TR3 + SL3
base5 = TR5 + SL5

u3 = np.column_stack([(TARGETS["T1"][0] - P3[:, 0]) / RR3,
                      (TARGETS["T1"][1] - P3[:, 1]) / RR3])
u5 = np.column_stack([(TARGETS["T1"][0] - P5[:, 0]) / RR5,
                      (TARGETS["T1"][1] - P5[:, 1]) / RR5])
cosg = np.clip(u3 @ u5.T, -1.0, 1.0)
gam = np.degrees(np.arccos(cosg))

start1 = np.maximum(base3[:, None], base5[None, :])
# partner V2's ready for T3 is fixed by the delivered scheme; re-evaluate it.
st2_t3 = np.array(OPT["stations"]["V2"]["T3"], float)
az2_t3, el2_t3, _ = pointing_angles(st2_t3, TARGETS["T3"], TARGET_H["T3"])
rd_v2_t3 = travel_time(tuple(VEHICLES[1]), tuple(st2_t3)) + \
    max(abs(az2_t3), el2_t3) / OMEGA
start3 = np.maximum(start1 + tail3[:, None], rd_v2_t3)
T2_START = float(OPT["alert_starts"]["T2"])
obj = np.maximum(np.maximum(start1, start3), T2_START)

feas = (gam >= GAMMA_LO) & (gam <= GAMMA_HI)
print("feasible pairs:", int(feas.sum()), "of", feas.size)
if not feas.any():
    raise SystemExit("no gamma-feasible pair in candidate sets")

obj_f = np.where(feas, obj, np.inf)
# tie-break: objective, then sum of starts, then gamma closest to 90
sum_starts = start1 + start3 + T2_START
i, j = np.unravel_index(np.argmin(obj_f), obj_f.shape)
best = {"i": int(i), "j": int(j), "obj_s": float(obj_f[i, j]),
        "T1_start_s": float(start1[i, j]), "T3_start_s": float(start3[i, j]),
        "T2_start_s": T2_START, "gamma_deg": float(gam[i, j])}
print("constrained T1 pair:", best, "stations",
      P3[i].round(4), P5[j].round(4))

# local refinement of V3's T3 station for the chosen T1 pair; the delivered
# station itself is kept as a candidate so the refinement can never regress
p3, p5 = tuple(P3[i]), tuple(P5[j])
pts3 = np.vstack([pts3, ST3_T3])
tr_all = np.array([travel_time(p3, tuple(q)) for q in pts3])
az_all, el_all, sl_all, rr_all = geom_arrays(pts3, "T3")
rd_all = tr_all + sl_all          # increment from V3's free time after T1
k_ref = int(np.argmin(rd_all))
p3_t3 = tuple(pts3[k_ref])
print("refined V3/T3 station:", np.round(p3_t3, 4),
      "travel+slew delta:", round(float(rd_all[k_ref]), 4),
      "| V2 ready:", round(float(rd_v2_t3), 4))

# exact re-simulation of the constrained scheme (fixed structure)
def station_times(p, a):
    az, el, _ = pointing_angles(p, TARGETS[a], TARGET_H[a])
    return az, el, max(abs(az), el) / OMEGA


def sim_fixed(st_map):
    """Fixed-point timeline of the delivered assignment/orders.

    Partner ready times not yet computed in the current sweep fall back to the
    previous sweep, and the whole chain is re-walked until starts stabilise.
    """
    asg = {a: tuple(v - 1 for v in OPT["assignment"][a]) for a in ALERTS3}
    orders = {int(k[1:]) - 1: list(v) for k, v in OPT["orders"].items()}
    prev_starts, prev_ready = {}, {}
    starts, ready = {}, {}
    for _guard in range(60):
        starts, ready = {}, {}
        chain = {v: (0.0, tuple(VEHICLES[v])) for v in range(5)}
        for v in range(5):
            t_free, pos = chain[v]
            for a in orders.get(v, []):
                st = st_map[(v, a)]
                az, el, sl = station_times(st, a)
                rd = t_free + travel_time(pos, st) + sl
                ready[(v, a)] = rd
                v2 = asg[a][0] if asg[a][1] == v else asg[a][1]
                pr = ready.get((v2, a), prev_ready.get((v2, a)))
                if pr is None:
                    break
                start = max(rd, pr)
                starts[a] = start
                t_free = start + OBS_LEN + sl
                pos = st
        ok = (len(starts) == 3 and prev_starts.keys() == starts.keys()
              and all(abs(starts[a] - prev_starts[a]) < 1e-9 for a in starts))
        if ok:
            break
        prev_starts, prev_ready = starts, ready
    return starts, ready


st_map = {(int(k[1:]) - 1, a): tuple(p)
          for k, d in OPT["stations"].items() for a, p in d.items()}
st_map[(2, "T1")] = p3
st_map[(4, "T1")] = p5
st_map[(2, "T3")] = p3_t3
starts_c, ready_c = sim_fixed(st_map)
obj_c = max(starts_c.values())
g1 = pair_geometry(st_map[(2, "T1")], st_map[(4, "T1")], "T1")
g3 = pair_geometry(st_map[(2, "T3")], st_map[(1, "T3")], "T3")
g2 = pair_geometry(st_map[(0, "T2")], st_map[(3, "T2")], "T2")
print("constrained scheme starts:", {a: round(v, 3) for a, v in starts_c.items()},
      "obj:", round(obj_c, 4))
print("constrained gammas:", round(g1["gamma_deg"], 2),
      round(g2["gamma_deg"], 2), round(g3["gamma_deg"], 2))

DELIVERED_OBJ = float(OPT["objective_s"])
out = {
    "sigma_deg": 1.0,
    "G_definition": "G=sqrt((d1^2+d2^2)/2)/|sin(gamma)| [m]; DRMS=sigma_rad*G",
    "delivered": rows,
    "gamma_window_deg": [GAMMA_LO, GAMMA_HI],
    "robust_variant": {
        "objective_s": float(RB["obj_s"]) if RB.get("obj_s") is not None else None,
        "assignment": RB.get("assignment"),
        "geometry": rb_geom,
    },
    "constrained": {
        "structure": "same assignment/orders as delivered scheme",
        "stations": {f"V{v+1}": {a: [round(x, 4) for x in st_map[(v, a)]]
                                 for a in OPT["orders"].get(f"V{v+1}", [])}
                     for v in range(5)},
        "starts_s": {a: round(starts_c[a], 3) for a in ALERTS3},
        "objective_s": round(obj_c, 3),
        "delta_s": round(obj_c - DELIVERED_OBJ, 3),
        "delta_pct": round((obj_c / DELIVERED_OBJ - 1.0) * 100.0, 2),
        "geometry": {a: g for a, g in (("T1", g1), ("T2", g2),
                                       ("T3", g3))},
    },
}
with open(os.path.join(RES_DIR, "q2b_precision.json"), "w",
          encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2, default=float)

lines = ["# 第二问（2）时效方案的精度几何", "",
         "定义：γ 为两站至目标的两条水平视线夹角；d₁,d₂ 为站-目标水平距离；"
         "G=√((d₁²+d₂²)/2)/|sin γ|（m）；DRMS=σ·G，σ=1°=0.017453 rad；"
         "95% 圆半径 = 2.4477·DRMS（仅各向同性时精确；本表站对均非各向同性，"
      "精确 95% 椭圆半轴见 JSON 字段 r95_semi_axes_m）。", "",
         "## 交付的时间最优方案", "",
         "| 告警 | 配对 | 站 1 (m) | 站 2 (m) | d₁ (m) | d₂ (m) | γ (°) | G (m) | DRMS (m) | R95,iso (m) |",
         "|---|---|---|---|---|---|---|---|---|---|"]
for g in rows:
    s = g["stations"]
    lines.append(f"| {g['alert']} | V{g['pair'][0]}+V{g['pair'][1]} | "
                 f"({s[0][0]:.2f}, {s[0][1]:.2f}) | ({s[1][0]:.2f}, {s[1][1]:.2f}) | "
                 f"{g['d1_m']:.2f} | {g['d2_m']:.2f} | {g['gamma_deg']:.2f} | "
                 f"{g['G_m']:.2f} | {g['DRMS_m']:.3f} | {g['r95_m']:.3f} |")
c = out["constrained"]
if rb_geom:
    lines += ["", "## 0.5 m 净空稳健变体（仅稳健性对照，精度不达标）", "",
              "| 告警 | γ (°) | G (m) | DRMS (m) |", "|---|---|---|---|"]
    for a in ALERTS3:
        gg = rb_geom[a]
        lines.append(f"| {a} | {gg['gamma_deg']:.2f} | {gg['G_m']:.2f} | "
                     f"{gg['DRMS_m']:.3f} |")
    lines += ["", f"该变体 t_last = {RB['obj_s']:.3f} s；T1、T2 均落在 "
              f"[30°,150°] 窗之外，仅用于净空稳健性对照，不作为部署推荐。", ""]
lines += ["", "## γ∈[30°,150°] 约束重解（同一指派/次序结构，重选 T1 双站；"
          "V3 的 T3 站优选后仍为原站）", "",
          "| 告警 | γ (°) | G (m) | DRMS (m) |", "|---|---|---|---|"]
for a in ALERTS3:
    gg = c["geometry"][a]
    lines.append(f"| {a} | {gg['gamma_deg']:.2f} | {gg['G_m']:.2f} | "
                 f"{gg['DRMS_m']:.3f} |")
lines += ["", f"开始时刻：T1={c['starts_s']['T1']:.3f} s，"
          f"T2={c['starts_s']['T2']:.3f} s，T3={c['starts_s']['T3']:.3f} s；"
          f"目标 t_last={c['objective_s']:.3f} s（交付方案 {DELIVERED_OBJ:.3f} s，"
          f"代价 +{c['delta_s']:.3f} s，+{c['delta_pct']:.2f}%）。", ""]
with open(os.path.join(RES_DIR, "q2b_precision.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("written q2b_precision.json / q2b_precision.md")
