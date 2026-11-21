# -*- coding: utf-8 -*-
"""2026 "ShuWei Cup" Problem B -- Problem 3: error propagation model for dpsi.

Model (see 第三题_建模文档.docx)
  true position P, estimated P̂ = P + (dx, dy), dx,dy ~ N(0, sigma(s)^2) iid,
  sigma(s) = 0.3 + 0.02 s ; target exactly known at horizontal range d = 40 m.
  Commanded bearing computed from P̂; gimbal zero-offset e0 ~ N(0, 0.8^2) and
  control error ec ~ N(0, 0.6^2) are independent of the localization error.
  Only the cross-range component of (dx,dy) rotates the bearing:
      dpsi = wrap( -d_perp/d [rad] + e0 + ec )   (wrap is a no-op here)
  -> dpsi ~ N(0, sigma_psi^2),  sigma_psi^2 = (sigma(s)/d * 180/pi)^2 + 0.8^2 + 0.6^2
  Requirement P(|dpsi| <= 5 deg) >= 0.95  <=>  sigma_psi <= 5 / z_{0.975}.

Outputs: figures/*.svg+png (numbers only), results/q3_results.json, summary txt.
All paths repo-relative; z-quantile from statistics.NormalDist (stdlib only).
"""
import json
import os
import statistics
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

matplotlib.rcParams["svg.fonttype"] = "none"
matplotlib.rcParams["font.family"] = "Times New Roman"
matplotlib.rcParams["mathtext.fontset"] = "stix"
matplotlib.rcParams["axes.linewidth"] = 0.8

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo-relative
FIG_DIR = os.path.join(BASE, "figures")
RES_DIR = os.path.join(BASE, "results")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(RES_DIR, exist_ok=True)

# ----------------------------- problem constants ----------------------------
D_TGT = 40.0          # m, fixed horizontal distance vehicle -> target
SIG0 = 0.3            # m, localization std at s = 0
GSLOPE = 0.02         # m per m, growth of localization std per meter driven
SIG_GIMBAL_ZERO = 0.8     # deg
SIG_GIMBAL_CTRL = 0.6     # deg
PSI_LIM = 5.0         # deg, pointing accuracy requirement
CONF = 0.95           # required probability
RAD2DEG = 180.0 / np.pi

VAR_GIMBAL = SIG_GIMBAL_ZERO ** 2 + SIG_GIMBAL_CTRL ** 2      # 1.0 deg^2
K_LOC = RAD2DEG / D_TGT                                        # deg per m of cross-range error
Z975 = statistics.NormalDist().inv_cdf(1 - (1 - CONF) / 2)    # 1.959964
SIG_PSI_MAX = PSI_LIM / Z975                                  # 2.551083 deg


def sigma_loc_deg(s):
    """Localization contribution to the bearing std (deg)."""
    return K_LOC * (SIG0 + GSLOPE * np.asarray(s, float))


def sigma_psi_deg(s):
    """Total bearing-deviation std (deg)."""
    return np.sqrt(sigma_loc_deg(s) ** 2 + VAR_GIMBAL)


def p_within(s):
    """P(|dpsi| <= 5 deg) under the analytic normal model."""
    x = PSI_LIM / sigma_psi_deg(s)
    nd = statistics.NormalDist()
    cdf = np.vectorize(lambda v: nd.cdf(v))
    return 2.0 * cdf(x) - 1.0


# ----------------------------- 1) analytic s_max ----------------------------
# sigma_loc(s)^2 <= SIG_PSI_MAX^2 - VAR_GIMBAL  ->  sigma(s) <= d*(pi/180)*C
C_GEO = np.sqrt(SIG_PSI_MAX ** 2 - VAR_GIMBAL)                # 2.346917 deg
SIG_S_MAX = D_TGT * np.pi / 180.0 * C_GEO                     # 1.63846 m
S_MAX = (SIG_S_MAX - SIG0) / GSLOPE                           # 66.92 m
print(f"z975 = {Z975:.6f}  sigma_psi_max = {SIG_PSI_MAX:.6f} deg")
print(f"C = {C_GEO:.6f} deg  sigma(s_max) = {SIG_S_MAX:.6f} m  s_max = {S_MAX:.4f} m")

# accuracy at s = 80 with the nominal a+bs
S_CHECK = 80.0
sig80 = float(sigma_psi_deg(S_CHECK))
p80 = float(p_within(S_CHECK))
print(f"s=80: sigma_psi = {sig80:.4f} deg  P = {p80:.4f}  (deficit {CONF - p80:+.4f})")

# ----------------------------- 2) a, b constraint region --------------------
# requirement at s = 80 (and hence for all s <= 80 since b >= 0):
#   (a + 80 b) <= d*(pi/180)*C = SIG_S_MAX
AB_MAX = float(SIG_S_MAX)
B_MAX = AB_MAX / 80.0            # 0.0204807 m/m when a = 0
A_MAX = AB_MAX                   # 1.63846 m when b = 0
nominal_inside = bool(SIG0 + GSLOPE * 80.0 <= AB_MAX)         # False
# tighter confidence levels (for the iso-lines in fig3)
LEVELS = (0.90, 0.95, 0.98, 0.99)
iso = {}
for lv in LEVELS:
    z = statistics.NormalDist().inv_cdf(1 - (1 - lv) / 2)
    smax_lv = PSI_LIM / z
    if smax_lv ** 2 > VAR_GIMBAL:
        sig_s_lv = D_TGT * np.pi / 180.0 * np.sqrt(smax_lv ** 2 - VAR_GIMBAL)
        iso[lv] = {"sigma_psi_max_deg": float(smax_lv),
                   "ab_max_m": float(sig_s_lv),
                   "s_max_m": float((sig_s_lv - SIG0) / GSLOPE)}
print("iso lines:", {k: round(v["ab_max_m"], 4) for k, v in iso.items()})

# ----------------------------- 3) variance contributions --------------------
S_GRID = [0.0, 10.0, 19.91, 30.0, 40.0, 50.0, 66.92, 80.0]
contrib = []
for s in S_GRID:
    vl = float(sigma_loc_deg(s) ** 2)
    vt = vl + VAR_GIMBAL
    contrib.append({"s": s, "var_loc_deg2": vl,
                    "var_zero_deg2": SIG_GIMBAL_ZERO ** 2,
                    "var_ctrl_deg2": SIG_GIMBAL_CTRL ** 2,
                    "var_total_deg2": vt,
                    "share_loc": vl / vt,
                    "share_zero": SIG_GIMBAL_ZERO ** 2 / vt,
                    "share_ctrl": SIG_GIMBAL_CTRL ** 2 / vt,
                    "sigma_psi_deg": float(np.sqrt(vt))})
# crossover: localization variance = total gimbal variance
S_CROSS = float((1.0 / K_LOC - SIG0) / GSLOPE)                # 19.91 m
print(f"crossover s (loc var = gimbal var) = {S_CROSS:.3f} m")

# ----------------------------- 4) Monte-Carlo validation --------------------
# exact commanded bearing from the estimated position (no linearization):
# alpha_cmd = atan2(Ty - Py - dy, Tx - Px - dx); true bearing from P.
# Rotate coordinates so the true bearing is 0: T - P = (d, 0).
# Then alpha_cmd - alpha_true = atan2(-dy, d - dx) + e0 + ec  (wrap no-op).
rng = np.random.default_rng(20261121)
N_MC = 1_000_000
mc = []
for s in (0.0, 20.0, 40.0, float(S_MAX), 80.0):
    sig = SIG0 + GSLOPE * s
    dx = rng.normal(0.0, sig, N_MC)
    dy = rng.normal(0.0, sig, N_MC)
    e0 = rng.normal(0.0, SIG_GIMBAL_ZERO, N_MC)
    ec = rng.normal(0.0, SIG_GIMBAL_CTRL, N_MC)
    dpsi = np.degrees(np.arctan2(-dy, D_TGT - dx)) + e0 + ec
    p_emp = float(np.mean(np.abs(dpsi) <= PSI_LIM))
    sig_emp = float(np.std(dpsi))
    bias = float(np.mean(dpsi))
    # linearized analytic value and the exact-normal CDF gap
    p_ana = float(p_within(s))
    # max quantile deviation between empirical dpsi and the analytic normal
    nd = statistics.NormalDist(
        mu=0.0, sigma=float(np.sqrt((sig / D_TGT * RAD2DEG) ** 2 + VAR_GIMBAL)))
    p_grid = np.linspace(0.001, 0.999, 999)
    emp_q = np.quantile(dpsi, p_grid)
    theo_q = np.array([nd.inv_cdf(p) for p in p_grid])
    ks = float(np.max(np.abs(emp_q - theo_q)))       # quantile-space max gap
    mc.append({"s": s, "sigma_s_m": sig, "n": N_MC,
               "P_emp": p_emp, "P_ana": p_ana, "P_diff": p_emp - p_ana,
               "sigma_emp_deg": sig_emp,
               "sigma_ana_deg": float(sigma_psi_deg(s)),
               "bias_deg": bias, "quantile_max_gap_deg": ks})
    print(f"MC s={s:6.2f}: P_emp={p_emp:.4f} P_ana={p_ana:.4f} "
          f"diff={p_emp - p_ana:+.5f} sigma_emp={sig_emp:.4f} "
          f"sigma_ana={sigma_psi_deg(s):.4f} bias={bias:+.2e} qgap={ks:.4f} deg")

# linearization residual size (deg, RMS) at s = 80 for the record
sig_s_80 = SIG0 + GSLOPE * S_CHECK
resid_rms_deg = float(np.degrees((sig_s_80 / D_TGT) ** 2))    # sigma^2/d^2
print(f"linearization residual RMS at s=80 ~ {resid_rms_deg:.4f} deg "
      f"({resid_rms_deg / sig80 * 100:.2f}% of sigma_psi)")

# ----------------------------- 4b) exact-geometry probability ---------------
# The linearized model replaces arctan2(-d_perp, d - d_par) by -d_perp/d.
# Exact P(|dpsi| <= 5) integrates the exact geometry over the joint normal
# (d_perp, d_par) with the N(0,1) gimbal sum absorbed in closed form:
#   P(s) = E[ Phi(5 - dalpha(d)) - Phi(-5 - dalpha(d)) ],
#   dalpha = atan2(-d_perp, d - d_par) in deg,  (d_perp, d_par) iid N(0, sig^2).
# Evaluated by 256x256 probabilists' Hermite quadrature (stdlib only).
from numpy.polynomial.hermite_e import hermegauss

_HN, _HW = hermegauss(256)
_HW = _HW / _HW.sum()            # weights for N(0,1)


def p_exact(s):
    """Exact-geometry P(|dpsi| <= 5 deg) at travel distance s."""
    sig = SIG0 + GSLOPE * float(s)
    nd = statistics.NormalDist()
    X = _HN * sig                   # nodes for each coordinate (m)
    W = _HW
    # d_perp, d_par iid N(0, sig^2): full 2-D grid via outer product
    dpar = np.repeat(X, 256)
    dperp = np.tile(X, 256)
    ww = np.repeat(W, 256) * np.tile(W, 256)
    dalpha = np.degrees(np.arctan2(-dperp, D_TGT - dpar))
    ndv = np.vectorize(lambda v: nd.cdf(v))
    pv = ndv((PSI_LIM - dalpha)) - ndv((-PSI_LIM - dalpha))
    return float(ww @ pv)


def exact_s_max():
    """Bisection for the exact-geometry s_max (P_exact = 0.95)."""
    lo, hi = 0.0, 120.0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if p_exact(mid) >= CONF:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


S_MAX_EXACT = exact_s_max()
P_AT_LIN = p_exact(S_MAX)
AB_EXACT = float((SIG0 + GSLOPE * S_CHECK) * 0.0 + np.nan)  # placeholder
# exact a + 80b bound: P_exact(s=80 | sigma = a+80b) = 0.95 -> sigma_ex(80)
# invert via bisection on sigma directly with the exact geometry
def sigma_for_exact(s_target_p):
    lo, hi = 0.0, 4.0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        # P_exact as a function of sigma: temporarily evaluate via s-mapping
        # p_exact depends on sigma only through sig = SIG0+GSLOPE*s; build a
        # direct evaluator:
        sig = mid
        X = _HN * sig
        dpar = np.repeat(X, 256)
        dperp = np.tile(X, 256)
        ww = np.repeat(_HW, 256) * np.tile(_HW, 256)
        dalpha = np.degrees(np.arctan2(-dperp, D_TGT - dpar))
        nd = statistics.NormalDist()
        ndv = np.vectorize(lambda v: nd.cdf(v))
        pv = ndv((PSI_LIM - dalpha)) - ndv((-PSI_LIM - dalpha))
        p = float(ww @ pv)
        if p >= CONF:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


SIG_EXACT_80 = sigma_for_exact(CONF)                 # allowable sigma at 80 m
AB_EXACT = SIG_EXACT_80                              # a + 80b <= SIG_EXACT_80
P_EXACT_80 = p_exact(S_CHECK)
print(f"exact geometry: P({S_MAX:.2f}) = {P_AT_LIN:.5f}; "
      f"s_max_exact = {S_MAX_EXACT:.3f} m; "
      f"P(80) exact = {P_EXACT_80:.5f}; a+80b exact <= {AB_EXACT:.4f} m")

# ----------------------------- 5) sensitivity -------------------------------
# (a) s_max vs standoff distance d (linear: slope k*C/GSLOPE)
sens_d = []
for d in (30.0, 35.0, 40.0, 45.0, 50.0, 60.0):
    smax_d = (d * np.pi / 180.0 * C_GEO - SIG0) / GSLOPE
    sens_d.append({"d_m": d, "s_max_m": float(smax_d)})
d_smax_dd = float(np.pi / 180.0 * C_GEO / GSLOPE)             # 2.0481 m per m
# (b) s_max vs required confidence (fixed d = 40): table computed in `iso`
# (c) sensitivity to the gimbal stds (both scaled by f)
sens_gim = []
for f in (0.5, 0.75, 1.0, 1.25, 1.5):
    var_g = (f * SIG_GIMBAL_ZERO) ** 2 + (f * SIG_GIMBAL_CTRL) ** 2
    c_f = np.sqrt(SIG_PSI_MAX ** 2 - var_g)
    smax_f = (D_TGT * np.pi / 180.0 * c_f - SIG0) / GSLOPE
    sens_gim.append({"gimbal_scale": f, "var_gimbal_deg2": float(var_g),
                     "s_max_m": float(smax_f)})
print(f"d(s_max)/d(d_tgt) = {d_smax_dd:.4f} m per m")

# ----------------------------- 6) figures -----------------------------------
COL1 = "#1f77b4"
COL2 = "#d62728"
COL3 = "#2ca02c"
COL4 = "#ff7f0e"


def _clean(ax):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(labelsize=10)


def save(fig, name):
    fig.savefig(os.path.join(FIG_DIR, name + ".svg"), bbox_inches="tight")
    fig.savefig(os.path.join(FIG_DIR, name + ".png"), dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("saved", name)


# fig1: sigma components vs travel distance
fig, ax = plt.subplots(figsize=(7.2, 4.6))
ss = np.linspace(0, 90, 901)
ax.plot(ss, sigma_loc_deg(ss), color=COL1, lw=1.8)
ax.plot(ss, sigma_psi_deg(ss), color=COL2, lw=2.0)
ax.axhline(SIG_PSI_MAX, color=COL3, lw=1.3, ls="--")
ax.axhline(np.sqrt(VAR_GIMBAL), color=COL4, lw=1.2, ls=":")
ax.axvline(S_MAX, color="k", lw=1.0, ls=":")
ax.plot([S_MAX], [SIG_PSI_MAX], marker="o", ms=8, mfc=COL3, mec="k", mew=0.6)
ax.set_xlim(0, 90)
ax.set_ylim(0, 4.0)
ax.set_xticks(range(0, 91, 15))
_clean(ax)
save(fig, "fig1_sigma_components")

# fig2: P(|dpsi|<=5) vs s, analytic + MC points
fig, ax = plt.subplots(figsize=(7.2, 4.6))
ax.plot(ss, p_within(ss), color=COL2, lw=2.0)
mc_s = [m["s"] for m in mc]
mc_p = [m["P_emp"] for m in mc]
ax.plot(mc_s, mc_p, linestyle="none", marker="o", ms=7, mfc=COL1,
        mec="k", mew=0.6, zorder=6)
ax.axhline(CONF, color=COL3, lw=1.3, ls="--")
ax.axvline(S_MAX, color="k", lw=1.0, ls=":")
ax.set_xlim(0, 90)
ax.set_ylim(0.5, 1.02)
ax.set_xticks(range(0, 91, 15))
_clean(ax)
save(fig, "fig2_probability_curve")

# fig3: (a, b) feasible region with iso-confidence lines
fig, ax = plt.subplots(figsize=(6.6, 5.2))
bb = np.linspace(0, 0.028, 500)
for lv, col in ((0.90, COL1), (0.95, COL3), (0.98, COL4), (0.99, COL2)):
    if lv in iso:
        ax.plot(iso[lv]["ab_max_m"] - 80.0 * bb, bb, color=col, lw=1.6)
aa = np.linspace(0, 2.2, 500)
mask_ab = np.minimum.outer(np.ones_like(aa), bb) > 0
region_b = np.clip((AB_MAX - aa) / 80.0, 0, None)
ax.fill_between(aa, 0, region_b, where=aa <= AB_MAX, color="#d6e8fa", alpha=0.8)
ax.plot([AB_MAX], [0.0], marker="o", ms=8, mfc=COL3, mec="k", mew=0.6)
ax.plot([0.0], [B_MAX], marker="o", ms=8, mfc=COL3, mec="k", mew=0.6)
ax.plot([SIG0], [GSLOPE], marker="s", ms=9, mfc=COL2, mec="k", mew=0.6, zorder=6)
ax.set_xlim(0, 2.2)
ax.set_ylim(0, 0.028)
ax.set_yticks([0, 0.005, 0.01, 0.015, 0.02, 0.025])
_clean(ax)
save(fig, "fig3_ab_region")

# fig4: variance decomposition (stacked) vs travel distance
fig, ax = plt.subplots(figsize=(7.2, 4.6))
vl = sigma_loc_deg(ss) ** 2
vz = np.full_like(ss, SIG_GIMBAL_ZERO ** 2)
vc = np.full_like(ss, SIG_GIMBAL_CTRL ** 2)
ax.stackplot(ss, vl, vz, vc,
             colors=["#c9dff0", "#f4c78f", "#f2a19b"], edgecolor="w", lw=0.4)
ax.plot(ss, vl + vz + vc, color="k", lw=1.4)
ax.axvline(S_CROSS, color="k", lw=1.0, ls=":")
ax.axvline(S_MAX, color="k", lw=1.0, ls=":")
ax.set_xlim(0, 90)
ax.set_ylim(0, 10.5)
ax.set_xticks(range(0, 91, 15))
_clean(ax)
save(fig, "fig4_variance_shares")

# fig5: MC validation at s = 80 (histogram vs analytic pdf)
fig, ax = plt.subplots(figsize=(7.2, 4.6))
sig = SIG0 + GSLOPE * S_CHECK
dpsi = np.degrees(np.arctan2(-rng.normal(0, sig, N_MC),
                             D_TGT - rng.normal(0, sig, N_MC))) \
    + rng.normal(0, SIG_GIMBAL_ZERO, N_MC) + rng.normal(0, SIG_GIMBAL_CTRL, N_MC)
ax.hist(dpsi, bins=160, range=(-12, 12), density=True,
        color="#c9dff0", edgecolor="none")
xs = np.linspace(-12, 12, 801)
nd80 = statistics.NormalDist(0.0, float(sigma_psi_deg(S_CHECK)))
pdf = np.vectorize(lambda v: nd80.pdf(v))
ax.plot(xs, pdf(xs), color=COL2, lw=2.0)
ax.axvline(PSI_LIM, color=COL3, lw=1.3, ls="--")
ax.axvline(-PSI_LIM, color=COL3, lw=1.3, ls="--")
ax.set_xlim(-12, 12)
ax.set_yticks([0, 0.05, 0.10, 0.14])
_clean(ax)
save(fig, "fig5_mc_validation")

# fig6: sensitivity of s_max
fig, (a6a, a6b) = plt.subplots(1, 2, figsize=(11.2, 4.4))
dv = np.linspace(25, 70, 451)
a6a.plot(dv, (dv * np.pi / 180.0 * C_GEO - SIG0) / GSLOPE, color=COL1, lw=1.8)
a6a.plot([D_TGT], [S_MAX], marker="o", ms=8, mfc=COL2, mec="k", mew=0.6)
a6a.set_xlim(25, 70)
a6a.set_xticks(range(25, 71, 5))
_clean(a6a)
lvv = sorted(iso.keys())
a6b.plot([iso[lv]["s_max_m"] for lv in lvv], lvv, color=COL1, lw=1.8,
         marker="o", ms=6)
a6b.plot([S_MAX], [0.95], marker="o", ms=9, mfc=COL2, mec="k", mew=0.6)
a6b.set_yticks(lvv)
a6b.set_ylim(0.88, 1.005)
_clean(a6b)
save(fig, "fig6_sensitivity_smax")

# ----------------------------- 7) dump --------------------------------------
results = {
    "constants": {"d_tgt_m": D_TGT, "sigma0_m": SIG0, "slope_m_per_m": GSLOPE,
                  "sigma_gimbal_zero_deg": SIG_GIMBAL_ZERO,
                  "sigma_gimbal_ctrl_deg": SIG_GIMBAL_CTRL,
                  "psi_limit_deg": PSI_LIM, "confidence": CONF},
    "model": {"k_loc_deg_per_m": float(K_LOC), "var_gimbal_deg2": float(VAR_GIMBAL),
              "sigma_psi_formula": "sqrt((sigma(s)/40*180/pi)^2 + 0.8^2 + 0.6^2)"},
    "z_conf": float(Z975),
    "sigma_psi_max_deg": float(SIG_PSI_MAX),
    "s_max_m": float(S_MAX),
    "sigma_s_at_smax_m": float(SIG_S_MAX),
    "at_80": {"sigma_psi_deg": sig80, "P": p80,
              "P_deficit": float(CONF - p80),
              "excess_needed_m": float(SIG0 + GSLOPE * S_CHECK - SIG_S_MAX)},
    "ab_region": {"a_plus_80b_max_m": AB_MAX, "b_max_m_per_m": float(B_MAX),
                  "a_max_m": float(A_MAX), "nominal_inside": nominal_inside,
                  "iso_levels": iso},
    "contributions": contrib,
    "s_crossover_m": S_CROSS,
    "exact_geometry": {"P_at_linear_smax": P_AT_LIN,
                       "s_max_exact_m": float(S_MAX_EXACT),
                       "P_at_80_exact": P_EXACT_80,
                       "ab_max_exact_m": AB_EXACT,
                       "method": "256x256 probabilists' Hermite quadrature "
                                 "of the exact atan2 geometry"},
    "monte_carlo": {"n": N_MC, "seed": 20261121, "points": mc,
                    "linearization_residual_rms_deg_at80": resid_rms_deg},
    "sensitivity": {"s_max_vs_d": sens_d, "ds_max_dd_m_per_m": d_smax_dd,
                    "s_max_vs_gimbal_scale": sens_gim},
}
with open(os.path.join(RES_DIR, "q3_results.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

lines = [
    "==== Problem 3 numeric summary ====",
    f"model: dpsi ~ N(0, (sigma(s)/40*180/pi)^2 + 0.64 + 0.36), sigma(s)=0.3+0.02s",
    f"z_0.975 = {Z975:.6f} ; sigma_psi_max = 5/z = {SIG_PSI_MAX:.6f} deg",
    f"s_max = {S_MAX:.4f} m  (sigma(s_max) = {SIG_S_MAX:.6f} m)",
    f"s = 80 nominal: sigma_psi = {sig80:.4f} deg, P = {p80:.4f} (< 0.95, deficit {CONF-p80:.4f})",
    f"a,b region: a >= 0, b >= 0, a + 80 b <= {AB_MAX:.6f} m "
    f"(b_max = {B_MAX:.6f} m/m @ a=0 ; a_max = {A_MAX:.4f} m @ b=0 ; "
    f"nominal (0.3, 0.02) inside = {nominal_inside})",
    f"crossover (loc var = gimbal var) at s = {S_CROSS:.3f} m",
    "variance shares (loc/zero/ctrl): " +
    ", ".join(f"s={c['s']:g}: {c['share_loc']*100:.1f}/{c['share_zero']*100:.1f}/"
              f"{c['share_ctrl']*100:.1f}%" for c in contrib),
    "MC validation (n=1e6): " +
    ", ".join(f"s={m['s']:g}: P_emp={m['P_emp']:.4f} vs {m['P_ana']:.4f} "
              f"(diff {m['P_diff']:+.5f})" for m in mc),
    f"exact geometry (Hermite quadrature): P({S_MAX:.2f}) = {P_AT_LIN:.5f}, "
    f"s_max_exact = {S_MAX_EXACT:.2f} m, P(80) exact = {P_EXACT_80:.5f}, "
    f"a+80b exact <= {AB_EXACT:.4f} m",
    f"linearization residual RMS at s=80: {resid_rms_deg:.4f} deg "
    f"({resid_rms_deg/sig80*100:.2f}% of sigma_psi)",
    f"sensitivity: d(s_max)/d(d_tgt) = {d_smax_dd:.4f} m per m ; "
    f"s_max vs d: {[(x['d_m'], round(x['s_max_m'], 1)) for x in sens_d]}",
    f"s_max vs gimbal scale: {[(x['gimbal_scale'], round(x['s_max_m'], 1)) for x in sens_gim]}",
    f"s_max vs confidence: {[(lv, round(v['s_max_m'], 1)) for lv, v in sorted(iso.items())]}",
]
summary = "\n".join(lines)
with open(os.path.join(RES_DIR, "q3_summary.txt"), "w", encoding="utf-8") as f:
    f.write(summary + "\n")
print(summary)
