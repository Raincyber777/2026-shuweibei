# -*- coding: utf-8 -*-
"""Problem 2 figure set. Numbers-only content: no axis titles, no legends,
no annotations with words (the captions live in the PPTX notes / paper doc).

fig1  observable region of T2 + 30 s reach circles of the five vehicles
fig2  layered constraints for T2 (C1 / C1&C2 / C1&C2&C3)
fig3  zoom at T2': r_min circle arcs, optimal pair, baseline, reach circles
fig4  accuracy model: G(gamma) for several ranges; 95% ellipse axes vs gamma
fig5  sensitivity: G* vs H; operating window on gamma (2xG* line)
fig6  error ellipses (1/2 sigma, 95%) at the optimal pair
fig7  Gantt of the optimized scheme
fig8  Gantt of the nearest-assignment baseline
fig9  field map of the optimized scheme (routes, stations, targets)
fig10 comparison bars (alert starts) + objective sensitivity (speed, slew rate)
"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arc

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from q2_lib import (BUILDINGS, TARGETS, TARGET_H, VEHICLES, R_MIN_GEO,
                    FIELD, O_POS)

matplotlib.rcParams["svg.fonttype"] = "none"
matplotlib.rcParams["font.family"] = "Times New Roman"
matplotlib.rcParams["mathtext.fontset"] = "stix"
matplotlib.rcParams["axes.linewidth"] = 0.8

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(BASE, "figures")
RES_DIR = os.path.join(BASE, "results")

COL_FEAS = "#d6e8fa"
COL_INFEAS = "#f2f2f2"
COL_BLD = "#b3b3b3"
COL_EDGE = "#4d4d4d"
COL_TGT = "#d62728"
COL_VEH = "#1f77b4"
COL_ARC_OK = "#2ca02c"
COL_ARC_ROB = "#1a6b1a"
COL_ARC_NO = "#d62728"
COL_OPT = "#111111"
VEH_COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd", "#8c564b"]

A = np.load(os.path.join(RES_DIR, "q2a_data.npz"))
X, Y, mask = A["X"], A["Y"], A["mask"]
phi_c, feas_circle, rob_circle = A["phi_c"], A["feas_circle"], A["rob_circle"]

with open(os.path.join(RES_DIR, "q2a_results.json"), encoding="utf-8") as f:
    RA = json.load(f)
with open(os.path.join(RES_DIR, "q2b_results.json"), encoding="utf-8") as f:
    RB = json.load(f)

T2P = TARGETS["T2"]
RMIN = R_MIN_GEO["T2"]
chosen = RA["chosen"]
st1, st2 = chosen["stations"]
V3 = VEHICLES[2]
V5 = VEHICLES[4]


def _clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(labelsize=10)


def draw_field(ax, alpha=1.0):
    for (x0, x1, y0, y1, h) in BUILDINGS:
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor=COL_BLD,
                               edgecolor=COL_EDGE, linewidth=0.8, alpha=alpha))


def save(fig, name):
    fig.savefig(os.path.join(FIG_DIR, name + ".svg"), bbox_inches="tight")
    fig.savefig(os.path.join(FIG_DIR, name + ".png"), dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("saved", name)


# --- fig1: full-field observable region + reach circles ----------------------
fig, ax = plt.subplots(figsize=(6.6, 6.2))
ax.imshow(mask, extent=(0, 100, 0, 100), origin="lower",
          cmap=matplotlib.colors.ListedColormap([COL_INFEAS, COL_FEAS]),
          interpolation="nearest", aspect="equal")
draw_field(ax)
for v in range(5):
    ax.add_patch(Circle(VEHICLES[v], 90.0, fill=False, ls="--",
                        ec=VEH_COLORS[v], lw=1.0, alpha=0.85))
ax.plot([O_POS[0]], [O_POS[1]], marker="o", ms=5, color="k")
ax.plot(T2P[0], T2P[1], marker="*", ms=14, color=COL_TGT)
ax.plot(VEHICLES[:, 0], VEHICLES[:, 1], linestyle="none", marker="s", ms=6,
        mfc=COL_VEH, mec="k", mew=0.5)
ax.add_patch(Rectangle((0, 0), 100, 100, fill=False, ec="k", lw=1.2))
ax.set_xlim(0, 100); ax.set_ylim(0, 100)
ax.set_xticks(range(0, 101, 20)); ax.set_yticks(range(0, 101, 20))
_clean(ax)
save(fig, "fig1_region_reach")

# --- fig2: layered constraints ----------------------------------------------
c1 = ((X >= 1.5) & (X <= 98.5) & (Y >= 1.5) & (Y <= 98.5))
from q2_lib import dist_to_rect
for b in BUILDINGS:
    c1 &= dist_to_rect(X, Y, b) >= 1.5
r2 = np.hypot(X - T2P[0], Y - T2P[1])
c2 = r2 >= RMIN - 1e-9
layers = [c1, c1 & c2, mask]
fig, axs = plt.subplots(1, 3, figsize=(13.2, 4.6))
for k, m in enumerate(layers):
    axs[k].imshow(m, extent=(0, 100, 0, 100), origin="lower",
                  cmap=matplotlib.colors.ListedColormap([COL_INFEAS, COL_FEAS]),
                  interpolation="nearest", aspect="equal")
    draw_field(axs[k])
    axs[k].plot(T2P[0], T2P[1], marker="*", ms=12, color=COL_TGT)
    axs[k].add_patch(Rectangle((0, 0), 100, 100, fill=False, ec="k", lw=1.0))
    axs[k].set_xlim(0, 100); axs[k].set_ylim(0, 100)
    axs[k].set_xticks(range(0, 101, 20)); axs[k].set_yticks(range(0, 101, 20))
    _clean(axs[k])
fig.subplots_adjust(wspace=0.12)
save(fig, "fig2_layers_T2")

# --- fig3: zoom at T2' -------------------------------------------------------
fig, ax = plt.subplots(figsize=(6.8, 6.4))
x0v, x1v, y0v, y1v = -4.0, 34.0, 52.0, 90.0
col_sel = np.where((X[0, :] >= x0v) & (X[0, :] <= x1v))[0]
row_sel = np.where((Y[:, 0] >= y0v) & (Y[:, 0] <= y1v))[0]
sub = mask[np.ix_(row_sel, col_sel)]
ax.imshow(sub, extent=(x0v, x1v, y0v, y1v), origin="lower",
          cmap=matplotlib.colors.ListedColormap([COL_INFEAS, COL_FEAS]),
          interpolation="nearest", aspect="equal", alpha=0.92)
draw_field(ax)
th = np.linspace(0, 2 * np.pi, 2000)
cx = T2P[0] + RMIN * np.cos(th)
cy = T2P[1] + RMIN * np.sin(th)
okf = feas_circle[(np.degrees(th) % 360 * len(phi_c) // 360).astype(int)
                  % len(phi_c)]
okr = rob_circle[(np.degrees(th) % 360 * len(phi_c) // 360).astype(int)
                 % len(phi_c)]
ax.plot(cx[okf & ~okr], cy[okf & ~okr], color=COL_ARC_OK, lw=3.4,
        solid_capstyle="round", zorder=6)
ax.plot(cx[okr], cy[okr], color=COL_ARC_ROB, lw=3.4, solid_capstyle="round",
        zorder=6)
ax.plot(cx[~okf], cy[~okf], color=COL_ARC_NO, lw=3.4, solid_capstyle="round",
        zorder=6)
for v, vv in ((2, V3), (4, V5)):
    ax.add_patch(Circle(vv, 90.0, fill=False, ls="--", ec=VEH_COLORS[v],
                        lw=1.1, alpha=0.9))
ax.plot([st1[0], st2[0]], [st1[1], st2[1]], color=COL_OPT, lw=1.4, zorder=7)
ax.plot([T2P[0], st1[0]], [T2P[1], st1[1]], linestyle=":", color="k", lw=0.9,
        zorder=7)
ax.plot([T2P[0], st2[0]], [T2P[1], st2[1]], linestyle=":", color="k", lw=0.9,
        zorder=7)
gam = chosen["gamma_deg"]
ph1 = float(np.degrees(np.arctan2(st1[1] - T2P[1], st1[0] - T2P[0])) % 360.0)
arc = Arc(T2P, 9.0, 9.0, angle=0, theta1=ph1, theta2=ph1 + gam,
          color=COL_OPT, lw=1.6, zorder=8)
ax.add_patch(arc)
ax.plot([st1[0]], [st1[1]], marker="p", ms=13, mfc=COL_OPT, mec="w", mew=1.0,
        zorder=9)
ax.plot([st2[0]], [st2[1]], marker="p", ms=13, mfc=COL_OPT, mec="w", mew=1.0,
        zorder=9)
ax.plot(T2P[0], T2P[1], marker="*", ms=16, color=COL_TGT, zorder=9)
ax.plot([V3[0]], [V3[1]], linestyle="none", marker="s", ms=8, mfc=VEH_COLORS[2],
        mec="k", mew=0.5, zorder=9)
ax.plot([V5[0]], [V5[1]], linestyle="none", marker="s", ms=8, mfc=VEH_COLORS[4],
        mec="k", mew=0.5, zorder=9)
ax.set_xlim(x0v, x1v); ax.set_ylim(y0v, y1v)
ax.set_xticks(range(-0, 35, 10)); ax.set_yticks(range(50, 91, 10))
ax.set_aspect("equal")
_clean(ax)
save(fig, "fig3_optimal_pair_zoom")

# --- fig4: accuracy model curves ---------------------------------------------
fig, (a4a, a4b) = plt.subplots(1, 2, figsize=(11.2, 4.4))
gam = np.linspace(5, 175, 1701)
for d, ls in ((RMIN, "-"), (10.0, "--"), (15.0, "-."), (20.0, ":")):
    a4a.plot(gam, np.sqrt((d * d + d * d) / 2.0) / np.abs(
        np.sin(np.radians(gam))), ls, color=COL_VEH, lw=1.7)
a4a.plot([90.0], [RMIN], marker="o", ms=7, mfc=COL_TGT, mec="k", mew=0.6)
a4a.set_ylim(0, 60)
a4a.set_xticks(range(0, 181, 30))
a4a.set_yticks(range(0, 61, 10))
_clean(a4a)

d = RMIN
sg = np.radians(1.0)
u1 = np.array([1.0, 0.0])
n1 = np.array([0.0, 1.0])
a95a, a95b = [], []
for g in gam:
    u2 = np.array([np.cos(np.radians(g)), np.sin(np.radians(g))])
    n2 = np.array([-u2[1], u2[0]])
    Amat = np.vstack([n1, n2])
    Dm = np.diag([d * d, d * d]) * sg * sg
    C = np.linalg.solve(Amat, Dm) @ np.linalg.inv(Amat).T
    ev = np.sort(np.linalg.eigvalsh(C))
    a95a.append(np.sqrt(ev[1] * 5.991479))
    a95b.append(np.sqrt(ev[0] * 5.991479))
a4b.plot(gam, a95a, color=COL_VEH, lw=1.7)
a4b.plot(gam, a95b, color=COL_ARC_OK, lw=1.7, ls="--")
a4b.plot([90.0], [RMIN * sg * np.sqrt(5.991479)], marker="o", ms=7,
         mfc=COL_TGT, mec="k", mew=0.6)
a4b.set_ylim(0, 2.0)
a4b.set_xticks(range(0, 181, 30))
_clean(a4b)
save(fig, "fig4_accuracy_model")

# --- fig5: sensitivity --------------------------------------------------------
fig, (a5a, a5b) = plt.subplots(1, 2, figsize=(11.2, 4.4))
sH = RA["sensitivity"]["G_star_vs_H"]
hv = [s["H"] for s in sH]
gv = [s["G_star"] for s in sH]
a5a.plot(hv, gv, color=COL_VEH, lw=1.8, marker="o", ms=5)
a5a.plot([35.0], [RMIN], marker="o", ms=9, mfc=COL_TGT, mec="k", mew=0.6)
a5a.set_xticks(range(25, 51, 5))
a5a.set_yticks(range(4, 11, 1))
_clean(a5a)

gam2 = np.linspace(5, 175, 1701)
gr = RMIN / np.abs(np.sin(np.radians(gam2))) / RMIN
a5b.plot(gam2, gr, color=COL_VEH, lw=1.8)
a5b.axhline(2.0, color=COL_ARC_NO, lw=1.2, ls="--")
a5b.plot([30.05, 149.95], [2.0, 2.0], marker="o", ms=7, mfc=COL_TGT, mec="k",
         mew=0.6, linestyle="none")
a5b.plot([90.0], [1.0], marker="o", ms=7, mfc=COL_ARC_OK, mec="k", mew=0.6,
         linestyle="none")
a5b.set_ylim(0, 8)
a5b.set_xticks(range(0, 181, 30))
_clean(a5b)
save(fig, "fig5_sensitivity")

# --- fig6: error ellipses at the optimum --------------------------------------
fig, ax = plt.subplots(figsize=(6.4, 6.0))
sg = np.radians(1.0)
s_iso = sg * RMIN
for k, col, ls in ((1, COL_VEH, "-"), (2, COL_VEH, "--"),
                   (2.4477, COL_TGT, "-")):
    ax.add_patch(Circle(T2P, s_iso * k, fill=False, ec=col, lw=1.5, ls=ls))
ax.plot([st1[0], T2P[0]], [st1[1], T2P[1]], color=COL_OPT, lw=1.2)
ax.plot([st2[0], T2P[0]], [st2[1], T2P[1]], color=COL_OPT, lw=1.2)
dir1 = np.array([T2P[0] - st1[0], T2P[1] - st1[1]])
dir1 = dir1 / np.linalg.norm(dir1)
dir2 = np.array([T2P[0] - st2[0], T2P[1] - st2[1]])
dir2 = dir2 / np.linalg.norm(dir2)
ax.plot([T2P[0] - dir1[0] * 14, T2P[0] + dir1[0] * 4],
        [T2P[1] - dir1[1] * 14, T2P[1] + dir1[1] * 4],
        color=COL_EDGE, lw=0.8, ls=":")
ax.plot([T2P[0] - dir2[0] * 14, T2P[0] + dir2[0] * 4],
        [T2P[1] - dir2[1] * 14, T2P[1] + dir2[1] * 4],
        color=COL_EDGE, lw=0.8, ls=":")
ax.plot([st1[0]], [st1[1]], marker="p", ms=12, mfc=COL_OPT, mec="w", mew=1.0)
ax.plot([st2[0]], [st2[1]], marker="p", ms=12, mfc=COL_OPT, mec="w", mew=1.0)
ax.plot(T2P[0], T2P[1], marker="*", ms=15, color=COL_TGT)
ax.set_xlim(-6.0, 26.0); ax.set_ylim(60.0, 86.0)
ax.set_xticks(range(-5, 26, 5)); ax.set_yticks(range(60, 87, 5))
ax.set_aspect("equal")
_clean(ax)
# inset: zoom at T2' so the 0.10-0.25 m circles are actually visible
axi = ax.inset_axes([0.60, 0.60, 0.37, 0.37])
for k, col, ls in ((1, COL_VEH, "-"), (2, COL_VEH, "--"),
                   (2.4477, COL_TGT, "-")):
    axi.add_patch(Circle(T2P, s_iso * k, fill=False, ec=col, lw=1.8, ls=ls))
axi.plot([T2P[0] - dir1[0] * 1.4, T2P[0] + dir1[0] * 1.4],
         [T2P[1] - dir1[1] * 1.4, T2P[1] + dir1[1] * 1.4],
         color=COL_EDGE, lw=0.8, ls=":")
axi.plot([T2P[0] - dir2[0] * 1.4, T2P[0] + dir2[0] * 1.4],
         [T2P[1] - dir2[1] * 1.4, T2P[1] + dir2[1] * 1.4],
         color=COL_EDGE, lw=0.8, ls=":")
axi.plot(T2P[0], T2P[1], marker="*", ms=12, color=COL_TGT)
axi.set_xlim(T2P[0] - 1.2, T2P[0] + 1.2)
axi.set_ylim(T2P[1] - 1.2, T2P[1] + 1.2)
axi.set_xticks([10, 11, 12])
axi.set_yticks([72, 72.5, 73])
axi.tick_params(labelsize=7)
ax.indicate_inset_zoom(axi, edgecolor="k", alpha=0.8)
save(fig, "fig6_error_ellipses")

# --- fig7/fig8: Gantt charts --------------------------------------------------
def gantt(segs, fname):
    fig, ax = plt.subplots(figsize=(11.6, 4.2))
    style = {"travel": ("#c9dff0", 0.95), "slew": ("#f4c78f", 0.95),
             "wait": ("#e4e4e4", 0.9), "obs": ("#2ca02c", 1.0),
             "reset": ("#f2a19b", 0.95)}
    for v in range(5):
        for seg in segs[f"V{v+1}"]:
            typ, t0, t1 = seg[0], float(seg[1]), float(seg[2])
            col, al = style[typ]
            ax.broken_barh([(t0, max(t1 - t0, 0.02))], (v - 0.32, 0.64),
                           facecolors=col, edgecolor=COL_EDGE, linewidth=0.4,
                           alpha=al)
    ax.set_ylim(-0.7, 4.7)
    ax.set_yticks(range(5))
    ax.set_yticklabels(["1", "2", "3", "4", "5"])
    ax.set_xlim(0, None)
    _clean(ax)
    save(fig, fname)


gantt(RB["gantt_opt"], "fig7_gantt_opt")
if RB["heuristic"].get("objective_s") is not None:
    gantt(RB["gantt_heu"], "fig8_gantt_heu")

# --- fig9: field map of the optimized scheme ---------------------------------
fig, ax = plt.subplots(figsize=(6.6, 6.2))
draw_field(ax)
ak = ["T1", "T2", "T3"]
for a in ak:
    ax.plot(TARGETS[a][0], TARGETS[a][1], marker="*", ms=13, color=COL_TGT)
ass = RB["optimized"]["assignment"]
ordv = RB["optimized"]["orders"]
stmap = RB["optimized"]["stations"]
for v in range(5):
    vv = VEHICLES[v]
    ax.plot([vv[0]], [vv[1]], linestyle="none", marker="s", ms=7,
            mfc=VEH_COLORS[v], mec="k", mew=0.5, zorder=8)
    pos = vv
    for a in ordv[f"V{v+1}"]:
        st = stmap[f"V{v+1}"][a]
        ax.annotate("", xy=(st[0], st[1]), xytext=(pos[0], pos[1]),
                    arrowprops=dict(arrowstyle="-|>", color=VEH_COLORS[v],
                                    lw=1.4, alpha=0.9,
                                    shrinkA=2, shrinkB=4))
        ax.plot([st[0]], [st[1]], marker="p", ms=9, mfc=VEH_COLORS[v],
                mec="k", mew=0.5, zorder=9)
        pos = st
for a in ak:
    ax.plot([O_POS[0], TARGETS[a][0]], [O_POS[1], TARGETS[a][1]],
            linestyle="--", color=COL_TGT, lw=0.8, alpha=0.6)
ax.plot([O_POS[0]], [O_POS[1]], marker="o", ms=5, color="k")
ax.add_patch(Rectangle((0, 0), 100, 100, fill=False, ec="k", lw=1.2))
ax.set_xlim(0, 100); ax.set_ylim(0, 100)
ax.set_xticks(range(0, 101, 20)); ax.set_yticks(range(0, 101, 20))
ax.set_aspect("equal")
from matplotlib.lines import Line2D
ax.legend(handles=[
    Line2D([], [], marker="*", color=COL_TGT, linestyle="none", ms=11,
           label="target"),
    Line2D([], [], marker="o", color="k", linestyle="none", ms=5,
           label="dispatch centre O"),
    Line2D([], [], marker="s", color=COL_VEH, mec="k", linestyle="none",
           ms=7, label="vehicle initial position"),
    Line2D([], [], marker="p", color=COL_VEH, mec="k", linestyle="none",
           ms=9, label="observation station"),
    Line2D([], [], color=COL_VEH, lw=1.4, label="route"),
    Line2D([], [], color=COL_TGT, lw=0.8, ls="--", alpha=0.6,
           label="O-alert line")],
    loc="upper left", bbox_to_anchor=(1.02, 1.0), frameon=False, fontsize=8)
_clean(ax)
save(fig, "fig9_routes_map")

# --- fig10: comparison + sensitivity -----------------------------------------
fig, (a10a, a10b, a10c) = plt.subplots(1, 3, figsize=(13.0, 4.2))
alerts = ["T1", "T2", "T3"]
opt_starts = [RB["optimized"]["alert_starts"][a] for a in alerts]
heu_starts = ([RB["heuristic"]["alert_starts"][a] for a in alerts]
              if RB["heuristic"].get("alert_starts") else None)
wid = 0.36
xi = np.arange(3)
a10a.bar(xi - wid / 2, opt_starts, wid, color=COL_ARC_OK, ec="k", lw=0.5)
if heu_starts:
    a10a.bar(xi + wid / 2, heu_starts, wid, color="#f2a19b", ec="k", lw=0.5)
    a10a.set_ylim(0, max(max(heu_starts), max(opt_starts)) * 1.25)
else:
    a10a.set_ylim(0, max(opt_starts) * 1.25)
a10a.set_xticks(xi)
a10a.set_xticklabels(["1", "2", "3"])
_clean(a10a)

sens = RB["sensitivity_speed_omega"]
sp_pts = sorted({(s["speed"], s["omega_deg_s"], s["obj_s"]) for s in sens}
                | {(3.0, 30.0, RB["optimized"]["objective_s"])})
sp3 = [(s, o) for (s, om, o) in sp_pts if om == 30.0]
om3 = [(om, o) for (s, om, o) in sp_pts if s == 3.0]
sp3.sort(); om3.sort()
a10b.plot([p[0] for p in sp3], [p[1] for p in sp3], color=COL_VEH, lw=1.8,
          marker="o", ms=6)
a10b.plot([3.0], [RB["optimized"]["objective_s"]], marker="o", ms=10,
          mfc=COL_TGT, mec="k", mew=0.6)
a10b.set_xticks([2.5, 3.0, 3.5])
_clean(a10b)
a10c.plot([p[0] for p in om3], [p[1] for p in om3], color=COL_VEH, lw=1.8,
          marker="o", ms=6)
a10c.plot([30.0], [RB["optimized"]["objective_s"]], marker="o", ms=10,
          mfc=COL_TGT, mec="k", mew=0.6)
a10c.set_xticks([24, 30, 36])
_clean(a10c)
save(fig, "fig10_comparison_sens")

print("all problem-2 figures done")
