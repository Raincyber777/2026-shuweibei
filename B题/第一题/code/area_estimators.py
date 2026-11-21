# -*- coding: utf-8 -*-
"""Recompute the observable-region area under explicit estimators/grids.

For h in {0.25, 0.10, 0.05} m:
  * midpoint (cell-center) estimator: node = center of an h x h cell
  * node-count estimator: node = grid intersection
The exact same masks (C1 vehicle geometry, C2 elevation, C3 3-D LOS) as the
Q1 solver are used.  Writes results/q1_area_estimators.json.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))), "第二题", "code"))
from q2_lib import (FIELD, H_CAM, R_MIN_GEO, R_VEH, TARGET_H, TARGETS,
                    los_blocked_h, make_grid)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(BASE, "results")
TGT, HH = TARGETS["T1"], TARGET_H["T1"]
RMIN = R_MIN_GEO["T1"]
BUILDINGS = [(22.0, 34.0, 16.0, 26.0, 20.0), (63.0, 79.0, 59.0, 71.0, 28.0),
             (10.0, 24.0, 65.0, 76.0, 12.0), (72.0, 86.0, 22.0, 34.0, 24.0),
             (41.0, 51.0, 38.0, 46.0, 32.0)]


def dist_to_rect(px, py, b):
    dx = np.maximum(np.maximum(b[0] - px, px - b[1]), 0.0)
    dy = np.maximum(np.maximum(b[2] - py, py - b[3]), 0.0)
    return np.hypot(dx, dy)


def count(h, center):
    X, Y = make_grid(h, center=center)
    c1 = ((X >= R_VEH) & (X <= FIELD - R_VEH) &
          (Y >= R_VEH) & (Y <= FIELD - R_VEH))
    for b in BUILDINGS:
        c1 &= dist_to_rect(X, Y, b) >= R_VEH
    r = np.hypot(X - TGT[0], Y - TGT[1])
    c2 = r >= RMIN - 1e-9
    cand = c1 & c2
    # evaluate the expensive 3-D LOS only where C1 & C2 hold
    xs, ys = X[cand], Y[cand]
    free = ~los_blocked_h(xs, ys, TGT, HH, BUILDINGS)
    return int(free.sum()) * h * h, int(cand.sum())


out = {"target": "T1", "r_min_m": RMIN,
       "estimators": {}, "note": "area = count * h^2; midpoint vs node-count"}
for h in (0.25, 0.10, 0.05):
    area_mid, n_mid = count(h, True)
    area_node, n_node = count(h, False)
    out["estimators"][f"h={h:g}"] = {
        "midpoint_area_m2": area_mid, "midpoint_cells": n_mid,
        "node_count_area_m2": area_node, "node_cells": n_node}
    print(f"h={h:g} m: midpoint {area_mid:.1f} ({n_mid} cells) | "
          f"node-count {area_node:.1f} ({n_node} cells)")

with open(os.path.join(RES, "q1_area_estimators.json"), "w",
          encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("written", os.path.join(RES, "q1_area_estimators.json"))
