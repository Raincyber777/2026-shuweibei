# -*- coding: utf-8 -*-
"""Problem 2(1) computational core: accuracy model + optimal pair for T2.

Model
-----
* stations p1, p2 in Omega_2 (geometry C1, elevation C2: r >= (H2-Hcam)/tan80,
  LOS C3), reachable from the vehicle start within 30 s (<= 90 m).
* azimuth errors ~ N(0, sigma^2), sigma = 1 deg, independent.
* intersection covariance  Sigma = A^-1 D A^-T,  A = [n1; n2],  D = diag(d1^2, d2^2)*sigma^2
  det(A) = sin(gamma)  ->  DRMS = sigma*sqrt((d1^2+d2^2)/2)/|sin gamma| =: sigma*G
* closed-form lower bound  G >= (d1+d2)/2 >= r_min_geo  (QM >= AM, d_i >= r_min)
  equality iff d1 = d2 = r_min and |sin gamma| = 1  -> certified global optimum
  whenever two feasible, reachable r_min-circle points with 90 deg separation exist.

Outputs: results/q2a_results.json, results/q2a_summary.txt, results/q2a_data.npz
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from q2_lib import (BUILDINGS, FIELD, OMEGA, R_VEH, H_CAM, SPEED, ELEV_MAX,
                    TARGETS, TARGET_H, R_MIN_GEO, ALERTS, VEHICLES,
                    dist_to_rect, los_blocked_h, region_masks, make_grid,
                    circle_samples, bool_runs, wrap180, slew_time,
                    pointing_angles, nelder_mead, travel_time, path_length)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(BASE, "figures")
RES_DIR = os.path.join(BASE, "results")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(RES_DIR, exist_ok=True)

TK = "T2"
T2P = TARGETS[TK]
H2 = TARGET_H[TK]
RMIN = R_MIN_GEO[TK]                      # 5.8188 m closed-form exclusion radius
SIG = 1.0                                 # deg
SIG_RAD = np.radians(SIG)
REACH = 90.0                              # m (30 s * 3 m/s)
TRAVEL_LIMIT_S = 30.0                     # s

# robust-feasible margins used by the tie-breaking (knife-edge protection)
CLR_LOS = 0.5        # min vertical LOS clearance over roofs (m)
MAR_C1 = 0.5         # min extra margin to buildings / field edge (m)


def seg_roof_clearance(px, py, tgt, h_tgt):
    """Min vertical clearance of the LOS over every roof it crosses (m)."""
    best = np.inf
    t = np.linspace(0.0, 1.0, 4001)
    sx = px + (tgt[0] - px) * t
    sy = py + (tgt[1] - py) * t
    sz = H_CAM + (h_tgt - H_CAM) * t
    for (bx0, bx1, by0, by1, bh) in BUILDINGS:
        over = (sx >= bx0) & (sx <= bx1) & (sy >= by0) & (sy <= by1)
        if over.any():
            best = min(best, float(sz[over].min()) - bh)
        else:
            # distance of closest approach in 3D (for grazing detection)
            dx = np.maximum(np.maximum(bx0 - sx, sx - bx1), 0.0)
            dy = np.maximum(np.maximum(by0 - sy, sy - by1), 0.0)
            dz = np.maximum(np.maximum(0.0 - sz, sz - bh), 0.0)
            best = min(best, float(np.min(np.sqrt(dx * dx + dy * dy + dz * dz))))
    return best


def c1_margin(px, py):
    m = np.minimum(px - R_VEH, py - R_VEH)
    m = np.minimum(m, FIELD - R_VEH - px)
    m = np.minimum(m, FIELD - R_VEH - py)
    for b in BUILDINGS:
        m = np.minimum(m, dist_to_rect(px, py, b) - R_VEH)
    return m


# ---------------------------------------------------------------- 1) region
STEP = 0.1
X, Y = make_grid(STEP)
c1, c2, c3, rgrid = region_masks(X, Y, T2P, H2, RMIN)
mask = c1 & c2 & c3
# official area: cell-center (midpoint) estimator; node count kept for reference
Xm, Ym = make_grid(STEP, center=True)
c1m, c2m, c3m, _ = region_masks(Xm, Ym, T2P, H2, RMIN)
area = float((c1m & c2m & c3m).sum()) * STEP * STEP
area_node = float(mask.sum()) * STEP * STEP
print("Omega_2 area (midpoint) = %.1f m^2 (node count %.1f)" % (area, area_node))

# ---------------------------------------------------------------- 2) r_min circle
NC = 72000
phi_c, cx_, cy_ = circle_samples(T2P, RMIN, NC)
cc1, cc2, cc3, _ = region_masks(cx_, cy_, T2P, H2, RMIN)
feas_circle = cc1 & cc3                      # c2 holds by construction
feas_runs = bool_runs(feas_circle, phi_c)
blocked_runs = bool_runs(~feas_circle, phi_c)
# robust subset: LOS clearance and C1 margin thresholds on the circle
clr_c = np.array([seg_roof_clearance(x, y, T2P, H2) for x, y in
                  zip(cx_[::40], cy_[::40])])          # coarse clearance scan
clr_full = np.interp(phi_c, phi_c[::40], clr_c, period=360.0)
mar_c = c1_margin(cx_, cy_)
rob_circle = feas_circle & (clr_full >= CLR_LOS) & (mar_c >= MAR_C1)
rob_runs = bool_runs(rob_circle, phi_c)
print("feasible runs:", [(round(a, 2), round(b, 2)) for a, b in feas_runs])
print("robust  runs:", [(round(a, 2), round(b, 2)) for a, b in rob_runs])

# ------------------------------------------------- 3) certified global optimum
# search phi such that phi and phi+90 (and phi-90) are both robust-feasible
def in_runs(phi, runs):
    ok = np.zeros_like(phi, bool)
    for a, b in runs:
        ok |= (phi >= a) & (phi <= b)
    return ok

phi_grid = np.arange(0.0, 360.0, 0.02)
okA = in_runs(phi_grid, rob_runs)
fam_plus = okA & np.roll(okA, -4500)         # phi+90 deg = 4500 grid steps
fam_minus = okA & np.roll(okA, 4500)         # phi-90 deg
fam = fam_plus | fam_minus
fam_phis = phi_grid[fam]
certified = len(fam_phis) > 0
fam_span = (float(fam_phis.min()), float(fam_phis.max())) if certified else None
print("certificate 90-deg family exists:", certified, "phi span:", fam_span)

G_STAR = float(RMIN)                          # geometry factor lower bound
DRMS_STAR = float(SIG_RAD * G_STAR)

# --------------------------------------------- 4) per-pair constrained optima
# polar-coordinate representation: G(d1,phi1,d2,phi2)=sqrt((d1^2+d2^2)/2)/|sin(phi2-phi1)|
TX, TY = T2P


def polar_of(x, y):
    dx, dy = x - TX, y - TY
    return np.hypot(dx, dy), np.degrees(np.arctan2(dy, dx)) % 360.0


def pair_optimize(iv, jv, mask_g, Xg, Yg, rg):
    """Two-stage polar search of min G for the vehicle pair (iv, jv).

    Pruning uses the valid lower bound G >= (d1+d2)/2 with the partner's
    minimal feasible range, so no optimal candidate is lost.
    """
    reach_i = np.hypot(Xg - VEHICLES[iv, 0], Yg - VEHICLES[iv, 1]) <= REACH + 1e-9
    reach_j = np.hypot(Xg - VEHICLES[jv, 0], Yg - VEHICLES[jv, 1]) <= REACH + 1e-9
    mi = mask_g & reach_i
    mj = mask_g & reach_j
    if not mi.any() or not mj.any():
        return None
    di, pi = polar_of(Xg[mi], Yg[mi])
    dj, pj = polar_of(Xg[mj], Yg[mj])
    xi, yi = Xg[mi], Yg[mi]
    xj, yj = Xg[mj], Yg[mj]
    d_i_min, d_j_min = float(di.min()), float(dj.min())

    def stage(d_i, p_i, d_j, p_j, x_i, y_i, x_j, y_j, inc, cap_i=None, cap_j=None):
        """Cross-evaluate G; inc<inf additionally LB-prunes both sides."""
        keep_i = np.ones(len(d_i), bool)
        keep_j = np.ones(len(d_j), bool)
        if cap_i is not None:
            keep_i &= d_i <= cap_i
        if cap_j is not None:
            keep_j &= d_j <= cap_j
        if inc < np.inf:
            keep_i &= d_i <= 2.0 * inc * 1.10 - d_j_min
            keep_j &= d_j <= 2.0 * inc * 1.10 - d_i_min
        if not keep_i.any() or not keep_j.any():
            return (np.inf, None)
        d_i, p_i, x_i, y_i = d_i[keep_i], p_i[keep_i], x_i[keep_i], y_i[keep_i]
        d_j, p_j, x_j, y_j = d_j[keep_j], p_j[keep_j], x_j[keep_j], y_j[keep_j]
        bloc = (np.inf, None)
        for s in range(0, len(d_i), 2000):
            di_c, pi_c = d_i[s:s + 2000], p_i[s:s + 2000]
            xi_c, yi_c = x_i[s:s + 2000], y_i[s:s + 2000]
            for t0 in range(0, len(d_j), 2000):
                dj_c, pj_c = d_j[t0:t0 + 2000], p_j[t0:t0 + 2000]
                xj_c, yj_c = x_j[t0:t0 + 2000], y_j[t0:t0 + 2000]
                num = np.sqrt((di_c[:, None] ** 2 + dj_c[None, :] ** 2) / 2.0)
                den = np.abs(np.sin(np.radians(pj_c[None, :] - pi_c[:, None])))
                g = num / np.maximum(den, 1e-12)
                k = np.unravel_index(np.argmin(g), g.shape)
                if g[k] < bloc[0]:
                    bloc = (float(g[k]), (float(xi_c[k[0]]), float(yi_c[k[0]]),
                                          float(xj_c[k[1]]), float(yj_c[k[1]])))
        return bloc

    # stage 1: coarse incumbent (stride 8 ~ 0.8 m lattice, fully crossed)
    st = max(1, len(di) // 4000)
    stj = max(1, len(dj) // 4000)
    b1 = stage(di[::st], pi[::st], dj[::stj], pj[::stj],
               xi[::st], yi[::st], xj[::stj], yj[::stj], np.inf,
               cap_i=d_i_min + 25.0, cap_j=d_j_min + 25.0)
    if b1[1] is None:
        return None
    inc = b1[0]
    # stage 2: valid-LB-pruned full sets with the coarse incumbent
    b2 = stage(di, pi, dj, pj, xi, yi, xj, yj, inc)
    best = min(b1, b2)
    # local refine in polar space by Nelder-Mead on (d1,phi1,d2,phi2)
    xi0, yi0, xj0, yj0 = best[1]
    d1_0, p1_0 = polar_of(np.array([xi0]), np.array([yi0]))
    d2_0, p2_0 = polar_of(np.array([xj0]), np.array([yj0]))

    def feas_ok(d, phi, ivx):
        x = TX + d * np.cos(np.radians(phi))
        y = TY + d * np.sin(np.radians(phi))
        if not (R_VEH <= x <= FIELD - R_VEH and R_VEH <= y <= FIELD - R_VEH):
            return False
        for b in BUILDINGS:
            if dist_to_rect(np.array([x]), np.array([y]), b)[0] < R_VEH - 1e-9:
                return False
        if d < RMIN - 1e-9:
            return False
        if los_blocked_h(np.array([x]), np.array([y]), T2P, H2)[0]:
            return False
        dv = np.hypot(x - VEHICLES[ivx, 0], y - VEHICLES[ivx, 1])
        return dv <= REACH + 1e-6

    def obj(v):
        d1v, q1, d2v, q2 = v
        if d1v < RMIN or d2v < RMIN:
            return 1e6 + abs(RMIN - d1v) + abs(RMIN - d2v)
        g = np.sqrt((d1v ** 2 + d2v ** 2) / 2.0) / max(abs(np.sin(np.radians(q2 - q1))), 1e-9)
        pen = 0.0
        if not feas_ok(d1v, q1, iv):
            pen += 10.0
        if not feas_ok(d2v, q2, jv):
            pen += 10.0
        # soft push toward the robust interior (avoid knife-edge optima)
        xa = TX + d1v * np.cos(np.radians(q1)); ya = TY + d1v * np.sin(np.radians(q1))
        xb = TX + d2v * np.cos(np.radians(q2)); yb = TY + d2v * np.sin(np.radians(q2))
        if seg_roof_clearance(xa, ya, T2P, H2) < CLR_LOS:
            pen += 1.0
        if seg_roof_clearance(xb, yb, T2P, H2) < CLR_LOS:
            pen += 1.0
        return g + pen

    x0 = [d1_0[0], p1_0[0], d2_0[0], p2_0[0]]
    xv, fv = nelder_mead(obj, x0, step=0.15, tol=1e-5, max_iter=300)
    if fv < best[0] and feas_ok(xv[0], xv[1], iv) and feas_ok(xv[2], xv[3], jv):
        best = (float(fv), (float(TX + xv[0] * np.cos(np.radians(xv[1]))),
                            float(TY + xv[0] * np.sin(np.radians(xv[1]))),
                            float(TX + xv[2] * np.cos(np.radians(xv[3]))),
                            float(TY + xv[2] * np.sin(np.radians(xv[3])))))

    # boundary-aware refinement for non-certified pairs: put the capable
    # vehicle's station exactly on the r_min circle (d1 = r_min), open the
    # intersection angle to exactly 90 deg (phi2 = phi1 +/- 90), and minimize
    # the far station's feasible range d2 along that ray. Removes the boundary
    # bias of the penalty-based NM (review: G 9.0063 -> 8.9962 for V2 pairs).
    if best[0] > G_STAR * 1.0005:
        d2g = np.arange(RMIN, 60.0, 0.05)
        for capable in (0, 1):
            iv_c, jv_c = (iv, jv) if capable == 0 else (jv, iv)
            for ph1 in np.arange(0.0, 360.0, 0.25):
                x1 = TX + RMIN * np.cos(np.radians(ph1))
                y1 = TY + RMIN * np.sin(np.radians(ph1))
                if not feas_ok(RMIN, ph1, iv_c):
                    continue
                for sgn in (+1.0, -1.0):
                    ph2 = (ph1 + sgn * 90.0) % 360.0
                    x2g = TX + d2g * np.cos(np.radians(ph2))
                    y2g = TY + d2g * np.sin(np.radians(ph2))
                    okg = ((x2g >= R_VEH) & (x2g <= FIELD - R_VEH) &
                           (y2g >= R_VEH) & (y2g <= FIELD - R_VEH) &
                           (np.hypot(x2g - VEHICLES[jv_c, 0],
                                     y2g - VEHICLES[jv_c, 1]) <= REACH))
                    for b in BUILDINGS:
                        okg &= dist_to_rect(x2g, y2g, b) >= R_VEH
                    okg &= ~los_blocked_h(x2g, y2g, T2P, H2)
                    idx = np.flatnonzero(okg)
                    if len(idx) == 0:
                        continue
                    d2 = float(d2g[idx[0]])
                    g_b = float(np.sqrt((RMIN ** 2 + d2 ** 2) / 2.0))
                    if g_b < best[0] - 1e-9:
                        best = (g_b, (float(x1), float(y1),
                                      float(x2g[idx[0]]), float(y2g[idx[0]])))
    return best


pair_rows = []
for iv in range(5):
    for jv in range(iv + 1, 5):
        res = pair_optimize(iv, jv, mask, X, Y, rgrid)
        if res is None:
            pair_rows.append({"pair": f"V{iv+1}+V{jv+1}", "feasible": False})
            continue
        g, (x1, y1, x2, y2) = res
        d1, ph1 = polar_of(np.array([x1]), np.array([y1]))
        d2, ph2 = polar_of(np.array([x2]), np.array([y2]))
        gamma = abs(((ph2[0] - ph1[0] + 180.0) % 360.0) - 180.0)
        t1 = travel_time(VEHICLES[iv], (x1, y1))
        t2 = travel_time(VEHICLES[jv], (x2, y2))
        p1_ok = path_length(VEHICLES[iv], (x1, y1))[1]
        p2_ok = path_length(VEHICLES[jv], (x2, y2))[1]
        robust = (seg_roof_clearance(x1, y1, T2P, H2) >= CLR_LOS and
                  seg_roof_clearance(x2, y2, T2P, H2) >= CLR_LOS and
                  c1_margin(np.array([x1]), np.array([y1]))[0] >= MAR_C1 and
                  c1_margin(np.array([x2]), np.array([y2]))[0] >= MAR_C1)
        pair_rows.append({
            "pair": f"V{iv+1}+V{jv+1}", "feasible": True,
            "G_m": g, "DRMS_m": SIG_RAD * g,
            "stations": [[x1, y1], [x2, y2]], "d": [d1[0], d2[0]],
            "phi": [ph1[0], ph2[0]], "gamma_deg": gamma,
            "travel_s": [t1, t2], "travel_sum_s": t1 + t2,
            "travel_straight_lb_s":
                [float(np.hypot(x1 - VEHICLES[iv, 0], y1 - VEHICLES[iv, 1]) / SPEED),
                 float(np.hypot(x2 - VEHICLES[jv, 0], y2 - VEHICLES[jv, 1]) / SPEED)],
            "path_straight_clear": [bool(p1_ok), bool(p2_ok)],
            "reach_ok_path": bool(t1 <= TRAVEL_LIMIT_S and t2 <= TRAVEL_LIMIT_S),
            "robust": bool(robust)})
        print(f"V{iv+1}+V{jv+1}: G={g:.4f} m  d=({d1[0]:.3f},{d2[0]:.3f}) "
              f"gamma={gamma:.2f}  travel=({t1:.2f},{t2:.2f})")

# --------------------------------- 4b) travel-optimal station family per pair
# For pairs attaining the certified optimum G* the stations lie in the family
# {d1 = d2 = r_min, |phi2 - phi1| = 90 deg}; the remaining freedom is one angle.
# Tie-breaking selects, within this family (and inside it for every eligible
# pair), the point minimising (sum travel, max travel) under strict interior
# margins and straight-path feasibility.
TIE_CLR = 0.75      # LOS clearance required by the tie-breaking (m)
TIE_MAR = 0.75      # C1 margin required by the tie-breaking (m)


def path_ok(p, q):
    t = np.linspace(0, 1, 2001)
    sx, sy = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
    for b in BUILDINGS:
        if (dist_to_rect(sx, sy, b) < R_VEH - 1e-9).any():
            return False
    return True


def family_travel_opt(iv, jv):
    """Min (sum, max) travel over the certified-optimal station family."""
    phis = np.arange(0.0, 360.0, 0.01)
    ok = in_runs(phis, rob_runs_tight)
    best = None
    for sign in (+1, -1):
        ph2 = (phis + sign * 90.0) % 360.0
        ok2 = in_runs(ph2, rob_runs_tight)
        cand = np.where(ok & ok2)[0]
        if len(cand) == 0:
            continue
        p1x = TX + RMIN * np.cos(np.radians(phis[cand]))
        p1y = TY + RMIN * np.sin(np.radians(phis[cand]))
        p2x = TX + RMIN * np.cos(np.radians(ph2[cand]))
        p2y = TY + RMIN * np.sin(np.radians(ph2[cand]))
        t1 = np.hypot(p1x - VEHICLES[iv, 0], p1y - VEHICLES[iv, 1]) / SPEED
        t2 = np.hypot(p2x - VEHICLES[jv, 0], p2y - VEHICLES[jv, 1]) / SPEED
        okT = (t1 <= TRAVEL_LIMIT_S) & (t2 <= TRAVEL_LIMIT_S)
        order = np.lexsort((phis[cand], np.maximum(t1, t2), t1 + t2))
        for k in order[okT[order]][:400]:          # path-check the shortlist
            if not (path_ok(VEHICLES[iv], (p1x[k], p1y[k])) and
                    path_ok(VEHICLES[jv], (p2x[k], p2y[k]))):
                continue
            key = (round(t1[k] + t2[k], 4), round(max(t1[k], t2[k]), 4),
                   float(phis[cand[k]]))
            if best is None or key < best[0]:
                best = (key, (float(p1x[k]), float(p1y[k])),
                        (float(p2x[k]), float(p2y[k])), float(t1[k]), float(t2[k]))
            break                                   # lexsort front = best key
    return best


# tighter robust runs for the tie-breaking (clearance / margin >= 0.75 m)
rob_tight = feas_circle & (clr_full >= TIE_CLR) & (mar_c >= TIE_MAR)
rob_runs_tight = bool_runs(rob_tight, phi_c)

# recompute travel-optimal representatives for every certified-eligible pair
for r in pair_rows:
    if r.get("feasible") and r["G_m"] <= G_STAR * 1.0005:
        iv = int(r["pair"][1]) - 1
        jv = int(r["pair"][4]) - 1
        fb = family_travel_opt(iv, jv)
        if fb is not None:
            _, (fx1, fy1), (fx2, fy2), ft1, ft2 = fb
            r["stations"] = [[fx1, fy1], [fx2, fy2]]
            r["travel_s"] = [ft1, ft2]
            r["travel_sum_s"] = ft1 + ft2
            # family stations have verified-clear straight paths, so path
            # time equals the straight time; refresh the stale row flags
            r["path_straight_clear"] = [
                bool(path_length(VEHICLES[iv], (fx1, fy1))[1]),
                bool(path_length(VEHICLES[jv], (fx2, fy2))[1])]
            r["travel_straight_lb_s"] = [ft1, ft2]
            r["reach_ok_path"] = bool(ft1 <= TRAVEL_LIMIT_S and
                                      ft2 <= TRAVEL_LIMIT_S)
            r["d"] = [RMIN, RMIN]
            r["phi"] = [float(np.degrees(np.arctan2(fy1 - TY, fx1 - TX)) % 360.0),
                        float(np.degrees(np.arctan2(fy2 - TY, fx2 - TX)) % 360.0)]
            r["gamma_deg"] = 90.0

# ---------------------------------------------------- 5) selection (tie-break)
# Rule T1: among certified-optimal robust pairs (G == G_STAR) choose min total
#          travel time; Rule T2: then min max travel; Rule T3: lexicographic.
# Fallback ladder keeps the pipeline total even without a certified pair.
def _key(r):
    return (round(r["travel_sum_s"], 3), round(max(r["travel_s"]), 3),
            r["stations"][0], r["stations"][1])

feas_rows = [r for r in pair_rows if r.get("feasible") and r.get("reach_ok_path")]
opt_pairs = [r for r in feas_rows if r["G_m"] <= G_STAR * 1.0005 and r.get("robust")]
if not opt_pairs:
    opt_pairs = [r for r in feas_rows if r["G_m"] <= G_STAR * 1.0005]
if not opt_pairs:
    opt_pairs = [r for r in feas_rows if r.get("robust")]
if not opt_pairs:
    opt_pairs = feas_rows
opt_pairs.sort(key=_key)
chosen = opt_pairs[0] if opt_pairs else None
print("chosen:", chosen["pair"] if chosen else None)

# ------------------------------------------------ 6) chosen pair full report
if chosen:
    (x1, y1), (x2, y2) = chosen["stations"]
    iv = int(chosen["pair"][1]) - 1
    jv = int(chosen["pair"][4]) - 1
    az1, el1, dd1 = pointing_angles((x1, y1), T2P, H2)
    az2, el2, dd2 = pointing_angles((x2, y2), T2P, H2)
    B_len = float(np.hypot(x2 - x1, y2 - y1))
    # path feasibility: straight segments must not enter inflated buildings
    def path_ok(p, q):
        t = np.linspace(0, 1, 2001)
        sx, sy = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
        for b in BUILDINGS:
            if (dist_to_rect(sx, sy, b) < R_VEH - 1e-9).any():
                return False
        return True
    path1 = path_ok(VEHICLES[iv], (x1, y1))
    path2 = path_ok(VEHICLES[jv], (x2, y2))
    # Monte-Carlo validation of the closed-form accuracy
    rng = np.random.default_rng(2026)
    nmc = 200000
    a1m = np.radians(az1 + rng.normal(0, SIG, nmc))
    a2m = np.radians(az2 + rng.normal(0, SIG, nmc))
    # lines: p_i + s * u_i ; solve p1 + s1 u1 = p2 + s2 u2
    u1 = np.array([np.cos(a1m), np.sin(a1m)])      # bearing-line direction
    u2 = np.array([np.cos(a2m), np.sin(a2m)])
    px1, py1 = x1, y1
    px2, py2 = x2, y2
    rhs_x, rhs_y = px2 - px1, py2 - py1
    det = u1[0] * u2[1] - u1[1] * u2[0]
    s1 = (rhs_x * u2[1] - rhs_y * u2[0]) / det
    ix = px1 + u1[0] * s1
    iy = py1 + u1[1] * s1
    err = np.hypot(ix - TX, iy - TY)
    mc_rmse = float(np.sqrt((err ** 2).mean()))
    mc_p95 = float(np.percentile(err, 95))
    ana_95 = float(DRMS_STAR * np.sqrt(5.991479))

    chosen_full = {
        "vehicles": chosen["pair"], "stations": chosen["stations"],
        "d_m": [dd1, dd2], "elevation_deg": [el1, el2],
        "azimuth_deg": [az1, az2], "baseline_m": B_len,
        "gamma_deg": chosen["gamma_deg"],
        "travel_s": chosen["travel_s"], "travel_sum_s": chosen["travel_sum_s"],
        "DRMS_m": DRMS_STAR, "sigma_used_deg": SIG,
        "ellipse95_radius_m": ana_95, "ellipse95_area_m2": float(np.pi * ana_95 ** 2),
        "sigma1_isotropic": True,
        "MC": {"n": nmc, "rmse_m": mc_rmse, "p95_m": mc_p95},
        "path_straight_ok": [path1, path2],
        "los_clearance_m": [seg_roof_clearance(x1, y1, T2P, H2),
                            seg_roof_clearance(x2, y2, T2P, H2)],
        "c1_margin_m": [float(c1_margin(np.array([x1]), np.array([y1]))[0]),
                        float(c1_margin(np.array([x2]), np.array([y2]))[0])],
    }
    print("chosen detail:", json.dumps(chosen_full, indent=1)[:800])

# ---------------------------------------------------- 7) degeneracy analysis
gam = np.linspace(0.5, 179.5, 3581)
g_sym = RMIN / np.abs(np.sin(np.radians(gam)))     # symmetric d1=d2=rmin
ok2x = np.abs(np.sin(np.radians(gam))) >= 0.5
gam_ok = gam[ok2x]
gam_window = (float(gam_ok.min()), float(gam_ok.max()))
cond = 1.0 / np.abs(np.sin(np.radians(gam)))
# boundary back-off design: elevation <= 78 deg  ->  r >= (H2-Hcam)/tan78
r_back = (H2 - H_CAM) / np.tan(np.radians(78.0))
el_margin_back = 2.0
Xm, Ym = make_grid(STEP, center=True)
rm_mid = np.hypot(Xm - T2P[0], Ym - T2P[1])
# sensitivity of G* to H (region recompute on the midpoint grid)
sens_H = []
for h_try in (25, 30, 35, 40, 45, 50):
    rmin_h = (h_try - H_CAM) / np.tan(np.radians(ELEV_MAX))
    c2h = rm_mid >= rmin_h - 1e-9
    c3h = ~los_blocked_h(Xm, Ym, T2P, h_try)
    mh = c1m & c2h & c3h
    # optimum still on the rmin circle if a robust 90-deg pair exists
    phc, cxc, cyc = circle_samples(T2P, rmin_h, 7200)
    cc1h, _, cc3h, _ = region_masks(cxc, cyc, T2P, h_try, rmin_h)
    rr = bool_runs(cc1h & cc3h, phc)
    okA_h = in_runs(phc, rr)
    fam_h = bool((okA_h & np.roll(okA_h, -1800)).any() or
                 (okA_h & np.roll(okA_h, 1800)).any())
    sens_H.append({"H": h_try, "r_min_geo": float(rmin_h),
                   "G_star": float(rmin_h),
                   "area_m2": float(mh.sum()) * STEP * STEP,
                   "pair_90_exists": fam_h})
dG_dH = 1.0 / np.tan(np.radians(ELEV_MAX))

# ------------------------------------------------------------- 8) dump
results = {
    "target": {"key": TK, "theta": ALERTS[TK][0], "R": ALERTS[TK][1],
               "H": H2, "xy": [float(T2P[0]), float(T2P[1])]},
    "constants": {"sigma_az_deg": SIG, "travel_limit_s": 30.0,
                  "travel_limit_m": REACH, "speed": SPEED,
                  "robust_margins": {"los_clearance_m": CLR_LOS, "c1_margin_m": MAR_C1}},
    "r_min_geo_m": float(RMIN),
    "region": {"step": STEP, "area_m2": area,
               "area_estimator": "cell-center (midpoint), h = 0.1 m",
               "area_node_count_m2": area_node},
    "circle": {"n_samples": NC, "feasible_runs_deg": feas_runs,
               "blocked_runs_deg": blocked_runs,
               "robust_runs_deg": rob_runs},
    "certificate": {"lower_bound_G_m": float(RMIN),
                    "lower_bound_proof": "G = sqrt((d1^2+d2^2)/2)/|sin g| >= "
                        "(d1+d2)/2 >= r_min (QM>=AM; C2 gives d>=r_min); "
                        "equality iff d1=d2=r_min, gamma=90 deg",
                    "family_exists": certified,
                    "phi_span_deg": fam_span,
                    "G_star_m": G_STAR, "DRMS_star_m": DRMS_STAR},
    "pair_table": pair_rows,
    "chosen": chosen_full if chosen else None,
    "degeneracy": {"gamma_window_G_le_2Gstar_deg": gam_window,
                   "cond_number_at_30deg": float(1.0 / np.sin(np.radians(30.0))),
                   "cond_number_at_90deg": 1.0,
                   "backoff_r_m": float(r_back),
                   "backoff_G_m": float(r_back),
                   "backoff_DRMS_m": float(SIG_RAD * r_back),
                   "backoff_elevation_margin_deg": el_margin_back},
    "sensitivity": {"dG_dH_per_m": float(dG_dH),
                    "dDRMS_dH_m_per_m": float(SIG_RAD * dG_dH),
                    "DRMS_vs_sigma": "linear proportionality (DRMS = sigma_rad * G)",
                    "G_star_vs_H": sens_H},
}
with open(os.path.join(RES_DIR, "q2a_results.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

np.savez_compressed(os.path.join(RES_DIR, "q2a_data.npz"),
                    X=X, Y=Y, mask=mask, rgrid=rgrid,
                    phi_c=phi_c, feas_circle=feas_circle, rob_circle=rob_circle)

lines = [
    "==== Problem 2(1) numeric summary ====",
    f"T2' = ({T2P[0]:.4f}, {T2P[1]:.4f})  H = {H2} m  r_min_geo = {RMIN:.4f} m",
    f"Omega_2 area (0.1 m midpoint) = {area:.1f} m^2 (node count {area_node:.1f})",
    "r_min circle feasible runs: " + str([(round(a, 2), round(b, 2)) for a, b in feas_runs]),
    "r_min circle robust  runs: " + str([(round(a, 2), round(b, 2)) for a, b in rob_runs]),
    f"certificate: G_lower = r_min = {RMIN:.4f} m ; 90-deg family: {certified} "
    f"(phi in {fam_span})",
    "per-pair optima:",
]
for r in pair_rows:
    if r.get("feasible"):
        lines.append(f"  {r['pair']}: G={r['G_m']:.4f} m DRMS={r['DRMS_m']:.4f} m "
                     f"d=({r['d'][0]:.3f},{r['d'][1]:.3f}) gamma={r['gamma_deg']:.2f} "
                     f"travel=({r['travel_s'][0]:.2f},{r['travel_s'][1]:.2f}) s")
    else:
        lines.append(f"  {r['pair']}: no feasible station pair")
if chosen:
    lines += [
        f"CHOSEN: {chosen['pair']}  stations {chosen['stations']}",
        f"  d=({chosen['d'][0]:.4f},{chosen['d'][1]:.4f}) m  gamma={chosen['gamma_deg']:.3f} deg"
        f"  B={chosen_full['baseline_m']:.4f} m",
        f"  DRMS = {DRMS_STAR:.4f} m ; 95% radius = {ana_95:.4f} m ; area95 = {np.pi*ana_95**2:.4f} m^2",
        f"  MC check (n=200k): RMSE={mc_rmse:.4f} m  P95={mc_p95:.4f} m",
        f"  travel times {chosen['travel_s']} s (sum {chosen['travel_sum_s']:.2f} s),"
        f" straight paths ok: {path1}, {path2}",
    ]
lines += [f"gamma operating window (G<=2G*): {gam_window}",
          f"back-off design: r = {r_back:.4f} m (elev <= 78 deg), DRMS = {SIG_RAD*r_back:.4f} m",
          f"sensitivity: dG*/dH = {dG_dH:.4f} m/m ; dDRMS/dH = {SIG_RAD*dG_dH:.5f} m per m of H"]
summary = "\n".join(lines)
with open(os.path.join(RES_DIR, "q2a_summary.txt"), "w", encoding="utf-8") as f:
    f.write(summary + "\n")
print(summary)
