# -*- coding: utf-8 -*-
"""Paper figures 4-1 .. 4-7 (Q1 + Q2), consolidated multi-panel versions.

All in-figure text is English; no Chinese inside figures (red line).
Physical sizes: single 8 cm, double 16 cm, 2x2 16 x 12 cm; fonts >= 8 pt.
Data sources: results/*.json (no recomputation of optimization), plus cheap
re-derivations of closed-form curves and 0.1 m feasibility masks.
"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arc, Patch

import scienceplots  # noqa: F401

plt.style.use(["science", "ieee", "no-latex", "grid"])
matplotlib.rcParams.update({
    "svg.fonttype": "none",
    "font.family": "Times New Roman",
    "mathtext.fontset": "stix",
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 9,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 6.5,
    "axes.linewidth": 0.8,
    "lines.linewidth": 1.0,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
    "axes.grid": True,
    "grid.alpha": 0.30,
    "grid.linewidth": 0.5,
    "figure.dpi": 300,
    "savefig.dpi": 300,
})

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "第二题", "code"))
from q2_lib import (BUILDINGS, TARGETS, TARGET_H, R_MIN_GEO, VEHICLES,
                    dist_to_rect, los_blocked_h, region_masks, make_grid,
                    R_VEH, FIELD, H_CAM)

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(B, "论文图表")
os.makedirs(OUT, exist_ok=True)

q1 = json.load(open(os.path.join(B, "第一题", "results", "q1_results.json"),
                    encoding="utf-8"))
q2a = json.load(open(os.path.join(B, "第二题", "results", "q2a_results.json"),
                     encoding="utf-8"))
q2b = json.load(open(os.path.join(B, "第二题", "results", "q2b_results.json"),
                     encoding="utf-8"))

# palette (original, not copied from any template)
C_BLUE = "#3D6FA8"
C_RED = "#BF4342"
C_GREEN = "#3E9B6C"
C_ORANGE = "#E39A3B"
C_PURPLE = "#7E6BAA"
C_TEAL = "#3D8C8C"
C_FEAS = "#D8E7F5"
C_INFEAS = "#F7F7F4"
C_BLD = "#C6C6C6"
C_BLD_EDGE = "#8A8A8A"
VEH_COLORS = ["#3D6FA8", "#E39A3B", "#3E9B6C", "#7E6BAA", "#A15A4E"]

T1 = TARGETS["T1"]
T2 = TARGETS["T2"]
RMIN1 = R_MIN_GEO["T1"]
RMIN2 = R_MIN_GEO["T2"]


def panel(ax, s):
    ax.set_title(s, loc="left", fontsize=9, fontweight="bold", pad=4)


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".svg"), bbox_inches="tight")
    fig.savefig(os.path.join(OUT, name + ".png"), dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("saved", name)


def draw_buildings(ax):
    for (x0, x1, y0, y1, h) in BUILDINGS:
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor=C_BLD,
                               edgecolor=C_BLD_EDGE, linewidth=0.7))


# ================================================================ fig 4-1
X1, Y1 = make_grid(0.1)
c11, c12, c13, _ = region_masks(X1, Y1, T1, TARGET_H["T1"], RMIN1)
m1 = c11 & c12 & c13
print("T1 mask ready")

fig, ax = plt.subplots(figsize=(3.35, 3.15))
ax.imshow(m1, extent=(0, 100, 0, 100), origin="lower",
          cmap=matplotlib.colors.ListedColormap(["#F7F7F4", "#D8E7F5"]),
          interpolation="nearest", aspect="equal")
draw_buildings(ax)
th = np.linspace(0, 2 * np.pi, 721)
ax.plot(T1[0] + RMIN1 * np.cos(th), T1[1] + RMIN1 * np.sin(th),
        color="#555555", lw=0.9, ls="--")
ax.plot(T1[0], T1[1], marker="*", ms=9, color=C_RED, ls="none")
ax.plot([50], [50], marker="o", ms=4, color="k", ls="none")
ax.plot(VEHICLES[:, 0], VEHICLES[:, 1], linestyle="none", marker="s", ms=5,
        mfc=C_BLUE, mec="k", mew=0.5)
ax.add_patch(Rectangle((0, 0), 100, 100, fill=False, ec="k", lw=1.0))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_xticks(range(0, 101, 20))
ax.set_yticks(range(0, 101, 20))
ax.set_xlabel("x (m)")
ax.set_ylabel("y (m)")
ax.grid(False)
leg = ax.legend(handles=[
    Patch(facecolor="#D8E7F5", label="Feasible region"),
    Patch(facecolor="#F7F7F4", label="Infeasible"),
    Patch(facecolor=C_BLD, ec=C_BLD_EDGE, label="Buildings B1–B5"),
    plt.Line2D([], [], color="#555555", ls="--", lw=0.9,
               label=r"r$_{min}$ circle"),
    plt.Line2D([], [], color=C_RED, marker="*", ls="none", ms=8,
               label="Target T1′"),
    plt.Line2D([], [], color=C_BLUE, marker="s", ls="none", ms=5,
               mec="k", label="Vehicles V1–V5"),
], loc="upper left", bbox_to_anchor=(1.01, 1.0), borderaxespad=0,
    frameon=True)
ax.tick_params(labelsize=7)
save(fig, "fig4-1_region")

# ================================================================ fig 4-2
opt = q1["optimal_station"]
arc = q1["arc"]
phi_c = np.linspace(0.0, 360.0, 200001, endpoint=False)
rad = np.radians(phi_c)
cx = T1[0] + RMIN1 * np.cos(rad)
cy = T1[1] + RMIN1 * np.sin(rad)
c1c, c2c, c3c, _ = region_masks(cx, cy, T1, TARGET_H["T1"], RMIN1)
feas = c1c & c3c
clr = np.full(len(phi_c), np.inf)
mm = np.minimum.reduce([dist_to_rect(cx, cy, b) - R_VEH for b in BUILDINGS])
mm = np.minimum.reduce([mm, cx - R_VEH, Y1[0, 0] + FIELD - R_VEH - cy +
                        np.zeros(len(cx))])
mm = np.minimum(mm, 98.5 - cx)
mm = np.minimum(mm, 98.5 - cy)
m_star = arc["m_star_margin_m"]
sel_margin = opt["margin_m"]
sel_phi = opt["phi_deg"]
print("arc feasibility recomputed; m* check:",
      round(float(mm.max()), 4), "vs", m_star)

fig, (a2a, a2b) = plt.subplots(1, 2, figsize=(6.30, 2.95),
                               gridspec_kw={"width_ratios": [1.15, 1.0]})
# (a) zoom with arcs
x0v, x1v, y0v, y1v = 70.0, 100.0, 55.0, 85.0
col = np.where((X1[0, :] >= x0v) & (X1[0, :] <= x1v))[0]
row = np.where((Y1[:, 0] >= y0v) & (Y1[:, 0] <= y1v))[0]
sub = (c11 & c12 & c13)[np.ix_(row, col)]
a2a.imshow(sub, extent=(x0v, x1v, y0v, y1v), origin="lower",
           cmap=matplotlib.colors.ListedColormap(["#F7F7F4", "#D8E7F5"]),
           interpolation="nearest", aspect="equal", alpha=0.9)
draw_buildings(a2a)
ok = feas[(np.degrees(th) % 360 * 200001 // 360).astype(int) % 200001]
cxf = T1[0] + RMIN1 * np.cos(th)
cyf = T1[1] + RMIN1 * np.sin(th)
a2a.plot(cxf[ok], cyf[ok], color=C_GREEN, lw=1.6, solid_capstyle="round")
a2a.plot(cxf[~ok], cyf[~ok], color=C_RED, lw=1.6, solid_capstyle="round")
a2a.plot([T1[0], opt["x"]], [T1[1], opt["y"]], ls=":", color="k", lw=0.8)
a2a.plot(opt["x"], opt["y"], marker="p", ms=8, mfc="k", mec="w", mew=0.8,
         ls="none")
a2a.plot(T1[0], T1[1], marker="*", ms=11, color=C_RED, ls="none")
a2a.plot(VEHICLES[3, 0], VEHICLES[3, 1], linestyle="none", marker="s",
         ms=6, mfc=C_BLUE, mec="k", mew=0.5)
a2a.add_patch(Rectangle((0, 0), 100, 100, fill=False, ec="k", lw=0.9))
a2a.set_xlim(x0v, x1v)
a2a.set_ylim(y0v, y1v)
a2a.set_xticks(range(70, 101, 10))
a2a.set_yticks(range(55, 86, 10))
a2a.set_xlabel("x (m)")
a2a.set_ylabel("y (m)")
a2a.grid(False)
panel(a2a, "(a) Optimal arc on the r$_{min}$ circle")
# (b) margin profile m - m*
mplot = np.where(feas, mm - m_star, np.nan)
a2b.plot(phi_c, mplot, color=C_GREEN, lw=1.0)
a2b.axhspan(-0.05, 0.0, color="#BFD7EE", alpha=0.7, zorder=0)
a2b.plot([arc["m_star_phi_deg"]], [0.0], marker="o", ms=7, mfc="none",
         mec=C_RED, mew=1.2, ls="none", zorder=6)
a2b.plot([sel_phi], [sel_margin - m_star], marker="p", ms=7, mfc="k",
         mec="w", mew=0.8, ls="none", zorder=7)
a2b.set_xlim(0, 360)
a2b.set_ylim(-4.2, 0.4)
a2b.set_yticks([-4, -3, -2, -1, 0])
a2b.set_xticks(range(0, 361, 60))
a2b.set_xlabel("Polar angle φ (deg)")
a2b.set_ylabel("m(p) − m* (m)")
a2b.legend(handles=[
    plt.Line2D([], [], color=C_GREEN, lw=1.0,
               label="margin profile m(p) − m*"),
    Patch(facecolor="#BFD7EE", label="tie-breaking band (0.05 m)"),
    plt.Line2D([], [], color=C_RED, marker="o", mfc="none", ls="none",
               ms=6, mew=1.2, label="arc maximum m*"),
    plt.Line2D([], [], color="k", marker="p", ls="none", ms=6, mfc="k",
               mec="w", label="selected station p*"),
], loc="lower left", fontsize=6, framealpha=0.9)
panel(a2b, "(b) Margin profile along the optimal arc")
fig.tight_layout(w_pad=1.5)
save(fig, "fig4-2_arc_margin")

# ================================================================ fig 4-3
sens = q1["sensitivity"]
fig, axs = plt.subplots(2, 2, figsize=(6.30, 4.72))
Hs = np.linspace(30, 60, 241)
axs[0, 0].plot(Hs, (Hs - 2) / np.tan(np.radians(80)), color=C_BLUE, lw=1.0)
axs[0, 0].plot([45], [7.5821], marker="o", ms=5, mfc=C_RED, mec="k",
               mew=0.5, ls="none")
axs[0, 0].set_xlabel("Target altitude H (m)")
axs[0, 0].set_ylabel("r* (m)")
panel(axs[0, 0], "(a) r* vs. target altitude")

es = np.linspace(70, 85, 241)
axs[0, 1].plot(es, 43 / np.tan(np.radians(es)), color=C_BLUE, lw=1.0)
axs[0, 1].plot([80], [7.5821], marker="o", ms=5, mfc=C_RED, mec="k",
               mew=0.5, ls="none")
axs[0, 1].set_xlabel("Elevation bound ε$_{max}$ (deg)")
axs[0, 1].set_ylabel("r* (m)")
panel(axs[0, 1], "(b) r* vs. elevation bound")

h2v = [v[0] for v in sens["area_vs_B2_height"]]
a2v = [v[1] for v in sens["area_vs_B2_height"]]
axs[1, 0].plot(h2v, a2v, color=C_BLUE, lw=1.0, marker="o", ms=3)
axs[1, 0].set_xlabel("B2 height (m)")
axs[1, 0].set_ylabel("Observable area (m²)")
panel(axs[1, 0], "(c) Area vs. B2 height")

rvv = [v[0] for v in sens["area_vs_vehicle_radius"]]
avv = [v[1] for v in sens["area_vs_vehicle_radius"]]
axs[1, 1].plot(rvv, avv, color=C_BLUE, lw=1.0, marker="o", ms=3)
axs[1, 1].set_xlabel("Vehicle radius (m)")
axs[1, 1].set_ylabel("Observable area (m²)")
panel(axs[1, 1], "(d) Area vs. vehicle radius")
fig.tight_layout(h_pad=1.6, w_pad=1.6)
save(fig, "fig4-3_sensitivity")

# ================================================================ fig 4-4
X2, Y2 = make_grid(0.1)
c21, c22, c23, _ = region_masks(X2, Y2, T2, TARGET_H["T2"], RMIN2)
m2 = c21 & c22 & c23
print("T2 mask ready")

fig, (a4a, a4b) = plt.subplots(1, 2, figsize=(6.30, 3.15),
                               gridspec_kw={"width_ratios": [1.0, 1.0]})
a4a.imshow(m2, extent=(0, 100, 0, 100), origin="lower",
           cmap=matplotlib.colors.ListedColormap(["#F7F7F4", "#D8E7F5"]),
           interpolation="nearest", aspect="equal")
draw_buildings(a4a)
for v in range(5):
    a4a.add_patch(Circle(VEHICLES[v], 90.0, fill=False, ls="--",
                         ec=VEH_COLORS[v], lw=0.8, alpha=0.85))
a4a.plot(T2[0], T2[1], marker="*", ms=9, color=C_RED, ls="none")
a4a.plot(VEHICLES[:, 0], VEHICLES[:, 1], linestyle="none", marker="s",
         ms=4, mfc=C_BLUE, mec="k", mew=0.4)
a4a.add_patch(Rectangle((0, 0), 100, 100, fill=False, ec="k", lw=0.9))
a4a.set_xlim(0, 100)
a4a.set_ylim(0, 100)
a4a.set_xticks(range(0, 101, 20))
a4a.set_yticks(range(0, 101, 20))
a4a.set_xlabel("x (m)")
a4a.set_ylabel("y (m)")
a4a.grid(False)
panel(a4a, "(a) Observable region of T2 and 30 s reach discs")

# (b) zoom near T2' with the selected pair
ch = q2a["chosen"]
(p1x, p1y), (p2x, p2y) = ch["stations"]
zx0, zx1, zy0, zy1 = -2.0, 26.0, 60.0, 88.0
col = np.where((X2[0, :] >= zx0) & (X2[0, :] <= zx1))[0]
row = np.where((Y2[:, 0] >= zy0) & (Y2[:, 0] <= zy1))[0]
sub = m2[np.ix_(row, col)]
a4b.imshow(sub, extent=(zx0, zx1, zy0, zy1), origin="lower",
           cmap=matplotlib.colors.ListedColormap(["#F7F7F4", "#D8E7F5"]),
           interpolation="nearest", aspect="equal", alpha=0.92)
draw_buildings(a4b)
a4b.plot(T2[0] + RMIN2 * np.cos(th), T2[1] + RMIN2 * np.sin(th),
         color="#555555", lw=0.8, ls="--")
a4b.add_patch(Circle(VEHICLES[2], 90.0, fill=False, ls="--",
                     ec=VEH_COLORS[2], lw=0.9))
a4b.add_patch(Circle(VEHICLES[4], 90.0, fill=False, ls="--",
                     ec=VEH_COLORS[4], lw=0.9))
a4b.plot([p1x, p2x], [p1y, p2y], color="k", lw=1.0)
a4b.plot([p1x], [p1y], marker="p", ms=7, mfc="k", mec="w", mew=0.7,
         ls="none")
a4b.plot([p2x], [p2y], marker="p", ms=7, mfc="k", mec="w", mew=0.7,
         ls="none")
a4b.plot(T2[0], T2[1], marker="*", ms=11, color=C_RED, ls="none")
a4b.plot(VEHICLES[2, 0], VEHICLES[2, 1], linestyle="none", marker="s",
         ms=6, mfc=VEH_COLORS[2], mec="k", mew=0.5)
a4b.plot(VEHICLES[4, 0], VEHICLES[4, 1], linestyle="none", marker="s",
         ms=6, mfc=VEH_COLORS[4], mec="k", mew=0.5)
ph1 = float(np.degrees(np.arctan2(p1y - T2[1], p1x - T2[0])) % 360.0)
d_arc = Arc(T2, 10.0, 10.0, angle=0,
            theta1=ph1, theta2=ph1 + 90.0,
            color="k", lw=1.2)
a4b.add_patch(d_arc)
a4b.set_xlim(zx0, zx1)
a4b.set_ylim(zy0, zy1)
a4b.set_xticks(range(0, 27, 5))
a4b.set_yticks(range(60, 89, 5))
a4b.set_xlabel("x (m)")
a4b.set_ylabel("y (m)")
a4b.grid(False)
panel(a4b, "(b) Selected pair V3+V5 near T2′ (γ = 90°)")
fig.tight_layout(w_pad=1.8)
save(fig, "fig4-4_t2_region_reach")

# ================================================================ fig 4-5
fig, axs = plt.subplots(1, 3, figsize=(6.30, 2.30))
sig_rad = np.radians(1.0)
gam = np.linspace(12, 168, 600)
for d, ls in ((5.8188, "-"), (10.0, "--"), (15.0, "-."), (20.0, ":")):
    axs[0].plot(gam, sig_rad * np.sqrt(2 * d * d) / np.sin(np.radians(gam)),
                ls, color=C_BLUE, lw=0.9)
axs[0].plot([90], [0.1016], marker="o", ms=4, mfc=C_RED, mec="k", mew=0.5,
            ls="none")
axs[0].set_xlabel("Intersection angle γ (deg)")
axs[0].set_ylabel("DRMS (m)")
panel(axs[0], "(a) DRMS vs. γ")

dd = np.linspace(RMIN2, 30, 300)
for g, ls in ((60, "-"), (90, "--"), (120, "-.")):
    axs[1].plot(dd, sig_rad * dd * np.sqrt(2) / np.sin(np.radians(g)), ls,
                color=C_BLUE, lw=0.9)
axs[1].plot([5.8188], [0.1016], marker="o", ms=4, mfc=C_RED, mec="k",
            mew=0.5, ls="none")
axs[1].set_xlabel("Station range d (m)")
axs[1].set_ylabel("DRMS (m)")
panel(axs[1], "(b) DRMS vs. range (γ = 60/90/120°)")

bb = np.linspace(4, 30, 300)
for g, ls in ((60, "-"), (90, "--"), (120, "-.")):
    bb_sym = 2 * dd * np.sin(np.radians(g) / 2)
    dr = sig_rad * dd * np.sqrt(2) / np.sin(np.radians(g))
    axs[2].plot(bb_sym, dr, ls, color=C_BLUE, lw=0.9)
axs[2].plot([8.2290], [0.1016], marker="o", ms=4, mfc=C_RED, mec="k",
            mew=0.5, ls="none")
axs[2].set_xlabel("Baseline B (m)")
axs[2].set_ylabel("DRMS (m)")
panel(axs[2], "(c) DRMS vs. baseline (γ = 60/90/120°)")
fig.tight_layout(w_pad=1.4)
save(fig, "fig4-5_accuracy_params")

# ================================================================ fig 4-6
fig, ax = plt.subplots(figsize=(3.35, 3.05))
(p1x, p1y), (p2x, p2y) = ch["stations"]
s_iso = sig_rad * RMIN2
dir1 = np.array([T2[0] - p1x, T2[1] - p1y])
dir1 /= np.linalg.norm(dir1)
dir2 = np.array([T2[0] - p2x, T2[1] - p2y])
dir2 /= np.linalg.norm(dir2)
for k, col, ls in ((1, C_BLUE, "-"), (2, C_BLUE, "--"), (2.4477, C_RED, "-")):
    ax.add_patch(Circle(T2P if False else T2, s_iso * k, fill=False,
                        ec=col, lw=1.0, ls=ls))
ax.plot([p1x, T2[0]], [p1y, T2[1]], color="k", lw=0.8)
ax.plot([p2x, T2[0]], [p2y, T2[1]], color="k", lw=0.8)
ax.plot([p1x], [p1y], marker="p", ms=7, mfc="k", mec="w", mew=0.7)
ax.plot([p2x], [p2y], marker="p", ms=7, mfc="k", mec="w", mew=0.7)
ax.plot(T2[0], T2[1], marker="*", ms=10, color=C_RED, ls="none")
ax.set_xlim(-8, 26)
ax.set_ylim(58, 88)
ax.set_xticks(range(-5, 26, 5))
ax.set_yticks(range(60, 89, 5))
ax.set_xlabel("x (m)")
ax.set_ylabel("y (m)")
ax.grid(False)
ax.legend(handles=[
    plt.Line2D([], [], color=C_BLUE, ls="-", lw=1.0, label="1σ circle"),
    plt.Line2D([], [], color=C_BLUE, ls="--", lw=1.0, label="2σ circle"),
    plt.Line2D([], [], color=C_RED, ls="-", lw=1.0, label="95% circle"),
    plt.Line2D([], [], color="k", marker="p", ls="none", ms=6, mfc="k",
               mec="w", label="stations"),
    plt.Line2D([], [], color=C_RED, marker="*", ls="none", ms=8,
               label="Target T2′"),
], loc="upper left", fontsize=6, framealpha=0.9)
# inset zoom
axi = ax.inset_axes([0.60, 0.58, 0.37, 0.38])
for k, col, ls in ((1, C_BLUE, "-"), (2, C_BLUE, "--"), (2.4477, C_RED, "-")):
    axi.add_patch(Circle(T2, s_iso * k, fill=False, ec=col, lw=1.4, ls=ls))
axi.plot([T2[0] - dir1[0] * 1.2, T2[0] + dir1[0] * 1.2],
         [T2[1] - dir1[1] * 1.2, T2[1] + dir1[1] * 1.2],
         color="k", lw=0.6, ls=":")
axi.plot([T2[0] - dir2[0] * 1.2, T2[0] + dir2[0] * 1.2],
         [T2[1] - dir2[1] * 1.2, T2[1] + dir2[1] * 1.2],
         color="k", lw=0.6, ls=":")
axi.plot(T2[0], T2[1], marker="*", ms=9, color=C_RED, ls="none")
axi.set_xlim(T2[0] - 1.0, T2[0] + 1.0)
axi.set_ylim(T2[1] - 1.0, T2[1] + 1.0)
axi.set_xticks([10, 11, 12])
axi.set_yticks([72, 72.5, 73])
axi.tick_params(labelsize=6)
axi.grid(False)
ax.indicate_inset_zoom(axi, edgecolor="k", alpha=0.8)
panel(ax, "Position error circles at the selected pair")
save(fig, "fig4-6_error_ellipses")

# ================================================================ fig 4-7
segs = q2b["gantt_opt"]
STYLE_G = {"travel": ("#CBDCEF", 0.95), "slew": ("#F5C68B", 0.95),
           "wait": ("#E6E6E6", 0.9), "obs": ("#3E9B6C", 1.0),
           "reset": ("#F2B0A6", 0.95)}
fig = plt.figure(figsize=(6.30, 2.90))
gs = fig.add_gridspec(1, 2, width_ratios=[2.6, 1.0], wspace=0.12)
axg = fig.add_subplot(gs[0])
for v in range(5):
    for seg in segs[f"V{v+1}"]:
        typ, t0, t1 = seg[0], float(seg[1]), float(seg[2])
        col, al = STYLE_G[typ]
        axg.broken_barh([(t0, max(t1 - t0, 0.03))], (v - 0.30, 0.60),
                        facecolors=col, edgecolor="#777777", linewidth=0.3,
                        alpha=al)
axg.set_ylim(-0.6, 4.6)
axg.set_yticks(range(5))
axg.set_yticklabels(["V1", "V2", "V3", "V4", "V5"])
axg.set_xlim(0, 25)
axg.set_xlabel("Time (s)")
axg.grid(axis="x", alpha=0.25, lw=0.4)
axg.grid(axis="y", visible=False)
leg = axg.legend(handles=[
    Patch(facecolor=STYLE_G["travel"][0], ec="#777777", label="travel"),
    Patch(facecolor=STYLE_G["slew"][0], ec="#777777", label="slew"),
    Patch(facecolor=STYLE_G["wait"][0], ec="#777777", label="wait (sync)"),
    Patch(facecolor=STYLE_G["obs"][0], ec="#777777", label="observe (5 s)"),
    Patch(facecolor=STYLE_G["reset"][0], ec="#777777", label="reset"),
], loc="lower right", fontsize=6, ncol=2, framealpha=0.95)
panel(axg, "(a) Optimized vehicle timeline")

axm = fig.add_subplot(gs[1])
stmap = q2b["optimized"]["stations"]
ordv = q2b["optimized"]["orders"]
asg = q2b["optimized"]["assignment"]
draw_buildings(axm)
for a in ("T1", "T2", "T3"):
    axm.plot(TARGETS[a][0], TARGETS[a][1], marker="*", ms=8, color=C_RED,
             ls="none")
for v in range(5):
    vv = VEHICLES[v]
    axm.plot([vv[0]], [vv[1]], linestyle="none", marker="s", ms=5,
             mfc=VEH_COLORS[v], mec="k", mew=0.4)
    pos = vv
    for a in ordv[f"V{v+1}"]:
        stm = stmap[f"V{v+1}"][a]
        axm.annotate("", xy=(stm[0], stm[1]), xytext=(pos[0], pos[1]),
                     arrowprops=dict(arrowstyle="-|>", color=VEH_COLORS[v],
                                     lw=0.9, shrinkA=2, shrinkB=3))
        axm.plot([stm[0]], [stm[1]], marker="p", ms=5, mfc=VEH_COLORS[v],
                 mec="k", mew=0.4)
        pos = stm
axm.add_patch(Rectangle((0, 0), 100, 100, fill=False, ec="k", lw=0.8))
axm.set_xlim(0, 100)
axm.set_ylim(0, 100)
axm.set_xticks(range(0, 101, 50))
axm.set_yticks(range(0, 101, 50))
axm.tick_params(labelsize=6)
axm.grid(False)
panel(axm, "(b) Deployment map")
save(fig, "fig4-7_gantt_inset")
print("PART 1 DONE")
