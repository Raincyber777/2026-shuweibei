# -*- coding: utf-8 -*-
"""Paper figures 4-1 .. 4-7 (Q1 + Q2), premium multi-panel versions."""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arc, Patch
from matplotlib.colors import LinearSegmentedColormap

import scienceplots  # noqa: F401

plt.style.use(["science", "ieee", "no-latex"])
matplotlib.rcParams.update({
    "svg.fonttype": "none",
    "font.family": "Times New Roman",
    "mathtext.fontset": "stix",
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 6,
    "axes.linewidth": 0.7,
    "lines.linewidth": 1.0,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": False,
    "ytick.right": False,
    "axes.grid": False,
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

# ---- own palette (distinct from template viridis/purple styles) ------------
C_BLUE = "#3D6FA8"
C_RED = "#B5443E"
C_GREEN = "#4C9B6B"
C_ORANGE = "#E09B3D"
C_PURPLE = "#7B62A8"
C_TEAL = "#2E7D8C"
C_FEAS = "#D8E7F5"
C_INFEAS = "#EFECE6"
C_BLD = "#C9C9C9"
C_BLD_EDGE = "#7A7A7A"
VEH_COLORS = ["#3D6FA8", "#E09B3D", "#4C9B6B", "#7B62A8", "#A15A4E"]

# "aurora" sequential map: r small (critical boundary zone) = deep navy,
# r large = pale cream. Custom, distinct from viridis/mako.
AURORA = LinearSegmentedColormap.from_list(
    "aurora", ["#17324F", "#2C5578", "#4E7F9E", "#8FB8C9", "#C9D6C8",
               "#EDE9DB"])
AURORA.set_bad("#EFECE6")

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


def field_map(ax, X, Y, mask, r, tgt, rmin, rmax):
    # imshow renders the field as ONE embedded raster -> compact SVG
    # (pcolormesh would emit ~1M vector polygons for a 0.1 m grid)
    Z = np.where(mask, r, np.nan)
    cm = AURORA.copy()
    cm.set_bad("#EFECE6")
    ax.imshow(Z, extent=(0.0, 100.0, 0.0, 100.0), origin="lower",
              cmap=cm, vmin=rmin, vmax=rmax, interpolation="nearest",
              aspect="equal")
    cs = ax.contour(X, Y, np.where(mask, r, np.nan),
                    levels=[10, 15, 20, 30], colors="white",
                    linewidths=0.5, alpha=0.55)
    ax.clabel(cs, inline=True, fontsize=5, fmt="%.0f")
    draw_buildings(ax)
    ax.add_patch(Circle(tgt, rmin, fill=False, ec="w", lw=0.9, ls=(0, (4, 3))))


# ================================================================ fig 4-1
X1, Y1 = make_grid(0.1)
c11, c12, c13, r1 = region_masks(X1, Y1, T1, TARGET_H["T1"], RMIN1)
m1 = c11 & c12 & c13
print("T1 field ready")

fig, ax = plt.subplots(figsize=(3.35, 3.05))
field_map(ax, X1, Y1, m1, r1, T1, RMIN1, 30.0)
ax.plot(T1[0], T1[1], marker="*", ms=9, color=C_RED, ls="none")
ax.plot([50], [50], marker="o", ms=3.5, color="k", ls="none")
ax.plot(VEHICLES[:, 0], VEHICLES[:, 1], linestyle="none", marker="s",
        ms=4.5, mfc=C_BLUE, mec="k", mew=0.5)
ax.add_patch(Rectangle((0, 0), 100, 100, fill=False, ec="k", lw=0.9))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_xticks(range(0, 101, 20))
ax.set_yticks(range(0, 101, 20))
ax.set_xlabel("x (m)")
ax.set_ylabel("y (m)")
ax.grid(False)
ax.legend(handles=[
    Patch(facecolor="#D8E7F5", ec="none", label="feasible (coloured by r)"),
    Patch(facecolor="#EFECE6", ec="none", label="occluded / infeasible"),
    Patch(facecolor=C_BLD, ec=C_BLD_EDGE, label="buildings B1–B5"),
    plt.Line2D([], [], color="w", ls=(0, (4, 3)), lw=0.9,
               label="r$_{min}$ = 7.58 m circle"),
    plt.Line2D([], [], color=C_RED, marker="*", ls="none", ms=8,
               label="target T1′"),
    plt.Line2D([], [], color=C_BLUE, marker="s", ls="none", ms=4.5,
               mec="k", label="vehicles V1–V5"),
], loc="upper left", bbox_to_anchor=(1.22, 1.0), borderaxespad=0,
    framealpha=0.95)
cb = fig.colorbar(ax.collections[0], ax=ax, shrink=0.82, pad=0.02)
cb.set_label("Range r (m)", fontsize=7)
cb.ax.tick_params(labelsize=6)
save(fig, "fig4-1_region")

# ================================================================ fig 4-2
opt = q1["optimal_station"]
arc = q1["arc"]
m_star = arc["m_star_margin_m"]
sel_phi = opt["phi_deg"]
sel_margin = opt["margin_m"]
phi_c = np.linspace(0.0, 360.0, 200001, endpoint=False)
rad = np.radians(phi_c)
cx = T1[0] + RMIN1 * np.cos(rad)
cy = T1[1] + RMIN1 * np.sin(rad)
c1c, c2c, c3c, _ = region_masks(cx, cy, T1, TARGET_H["T1"], RMIN1)
feas = c1c & c3c
mm = np.minimum.reduce([dist_to_rect(cx, cy, b) - R_VEH for b in BUILDINGS])
mm = np.minimum(mm, cx - R_VEH)
mm = np.minimum(mm, 98.5 - cx)
mm = np.minimum(mm, 98.5 - cy)
print("arc margins recomputed; m* check:", round(float(mm.max()), 4))

fig, (a2a, a2b) = plt.subplots(1, 2, figsize=(6.30, 3.05),
                               gridspec_kw={"width_ratios": [1.1, 1.0]})
x0v, x1v, y0v, y1v = 70.0, 100.0, 55.0, 85.0
col = np.where((X1[0, :] >= x0v) & (X1[0, :] <= x1v))[0]
row = np.where((Y1[:, 0] >= y0v) & (Y1[:, 0] <= y1v))[0]
Z = np.where((c11 & c12 & c13)[np.ix_(row, col)], r1[np.ix_(row, col)],
             np.nan)
cm = AURORA.copy()
cm.set_bad("#EFECE6")
a2a.imshow(Z, extent=(X1[0, col[0]], X1[0, col[-1]],
                      Y1[row[0], 0], Y1[row[-1], 0]),
           origin="lower", cmap=cm, vmin=RMIN1, vmax=30.0,
           interpolation="nearest", aspect="equal")
draw_buildings(a2a)
th = np.linspace(0, 2 * np.pi, 721)
ok = feas[(np.degrees(th) % 360 * 200001 // 360).astype(int) % 200001]
cxf = T1[0] + RMIN1 * np.cos(th)
cyf = T1[1] + RMIN1 * np.sin(th)
a2a.plot(cxf[ok], cyf[ok], color=C_GREEN, lw=1.8, solid_capstyle="round",
         zorder=6)
a2a.plot(cxf[~ok], cyf[~ok], color=C_RED, lw=1.8, solid_capstyle="round",
         zorder=6)
a2a.plot([T1[0], opt["x"]], [T1[1], opt["y"]], ls=":", color="k", lw=0.8,
         zorder=7)
a2a.plot(opt["x"], opt["y"], marker="p", ms=8, mfc="k", mec="w", mew=0.8,
         ls="none", zorder=8)
a2a.plot(T1[0], T1[1], marker="*", ms=11, color=C_RED, ls="none", zorder=8)
a2a.plot(VEHICLES[3, 0], VEHICLES[3, 1], linestyle="none", marker="s",
         ms=6, mfc=C_BLUE, mec="k", mew=0.5, zorder=8)
a2a.add_patch(Rectangle((0, 0), 100, 100, fill=False, ec="k", lw=0.9))
a2a.set_xlim(x0v, x1v)
a2a.set_ylim(y0v, y1v)
a2a.set_xticks(range(70, 101, 10))
a2a.set_yticks(range(55, 86, 10))
a2a.set_xlabel("x (m)")
a2a.set_ylabel("y (m)")
a2a.grid(False)
a2a.legend(handles=[
    plt.Line2D([], [], color=C_GREEN, lw=1.8, label="feasible optimal arc"),
    plt.Line2D([], [], color=C_RED, lw=1.8, label="blocked arc"),
    plt.Line2D([], [], color="k", marker="p", ls="none", ms=6, mfc="k",
               mec="w", label="selected station p*"),
    plt.Line2D([], [], color=C_BLUE, marker="s", ls="none", ms=5,
               mec="k", label="vehicle V4"),
], loc="upper center", bbox_to_anchor=(0.5, -0.20), ncol=2,
    frameon=False, fontsize=6)
panel(a2a, "(a) Optimal arc on the r$_{min}$ circle")

m_star = arc["m_star_margin_m"]
th = np.linspace(0, 2 * np.pi, 721)
cxf = T1[0] + RMIN1 * np.cos(th)
cyf = T1[1] + RMIN1 * np.sin(th)
ok = feas[(np.degrees(th) % 360 * 200001 // 360).astype(int) % 200001]
mplot = np.where(feas, mm - m_star, np.nan)
a2b.plot(phi_c, mplot, color=C_GREEN, lw=1.0)
a2b.axhspan(-0.05, 0.0, color="#BFD7EE", alpha=0.7, zorder=0)
a2b.plot([arc["m_star_phi_deg"]], [0.0], marker="o", ms=7, mfc="none",
         mec=C_RED, mew=1.2, ls="none", zorder=6)
a2b.annotate("arc maximum m*", xy=(arc["m_star_phi_deg"], 0.0),
             xytext=(120, 0.25), fontsize=6,
             arrowprops=dict(arrowstyle="->", lw=0.6))
a2b.plot([sel_phi], [sel_margin - m_star], marker="p", ms=7, mfc="k",
         mec="w", mew=0.8, ls="none", zorder=7)
a2b.annotate("selected station p*", xy=(sel_phi, sel_margin - m_star),
             xytext=(195, -1.6), fontsize=6,
             arrowprops=dict(arrowstyle="->", lw=0.6))
a2b.set_xlim(0, 360)
a2b.set_ylim(-4.2, 0.4)
a2b.set_yticks([-4, -3, -2, -1, 0])
a2b.set_xticks(range(0, 361, 60))
a2b.set_xlabel("Polar angle φ (deg)")
a2b.set_ylabel("m(p) − m* (m)")
panel(a2b, "(b) Margin profile along the optimal arc")
fig.tight_layout(w_pad=1.5)
save(fig, "fig4-2_arc_margin")

# ================================================================ fig 4-3
sens = q1["sensitivity"]
fig, axs = plt.subplots(2, 2, figsize=(6.30, 4.60))
Hs = np.linspace(30, 60, 241)
axs[0, 0].fill_between(Hs, (Hs - 2) / np.tan(np.radians(80)), 0,
                       color=C_BLUE, alpha=0.10)
axs[0, 0].plot(Hs, (Hs - 2) / np.tan(np.radians(80)), color=C_BLUE, lw=1.0)
axs[0, 0].plot([45], [7.5821], marker="o", ms=5, mfc=C_RED, mec="k",
               mew=0.5, ls="none")
axs[0, 0].annotate("7.58 m", xy=(45, 7.5821), xytext=(48, 5.5),
                   fontsize=6, arrowprops=dict(arrowstyle="->", lw=0.6))
axs[0, 0].set_xlim(30, 60)
axs[0, 0].set_ylim(0, 11)
axs[0, 0].set_xlabel("Target altitude H (m)")
axs[0, 0].set_ylabel("r* (m)")
panel(axs[0, 0], "(a) r* vs. target altitude")

es = np.linspace(70, 85, 241)
axs[0, 1].fill_between(es, 43 / np.tan(np.radians(es)), 0, color=C_TEAL,
                       alpha=0.10)
axs[0, 1].plot(es, 43 / np.tan(np.radians(es)), color=C_TEAL, lw=1.0)
axs[0, 1].plot([80], [7.5821], marker="o", ms=5, mfc=C_RED, mec="k",
               mew=0.5, ls="none")
axs[0, 1].annotate("7.58 m", xy=(80, 7.5821), xytext=(76, 10.5),
                   fontsize=6, arrowprops=dict(arrowstyle="->", lw=0.6))
axs[0, 1].set_xlim(70, 85)
axs[0, 1].set_ylim(0, 18)
axs[0, 1].set_xlabel("Elevation bound ε$_{max}$ (deg)")
axs[0, 1].set_ylabel("r* (m)")
panel(axs[0, 1], "(b) r* vs. elevation bound")

h2v = [v[0] for v in sens["area_vs_B2_height"]]
a2v = [v[1] for v in sens["area_vs_B2_height"]]
axs[1, 0].fill_between(h2v, a2v, 3000, color=C_GREEN, alpha=0.12)
axs[1, 0].plot(h2v, a2v, color=C_GREEN, lw=1.0, marker="o", ms=3)
axs[1, 0].set_xlim(20, 45)
axs[1, 0].set_ylim(3000, 6800)
axs[1, 0].set_xlabel("B2 height (m)")
axs[1, 0].set_ylabel("Observable area (m²)")
panel(axs[1, 0], "(c) Area vs. B2 height")

rvv = [v[0] for v in sens["area_vs_vehicle_radius"]]
avv = [v[1] for v in sens["area_vs_vehicle_radius"]]
axs[1, 1].fill_between(rvv, avv, 4800, color=C_ORANGE, alpha=0.12)
axs[1, 1].plot(rvv, avv, color=C_ORANGE, lw=1.0, marker="o", ms=3)
axs[1, 1].set_xlim(1.0, 2.5)
axs[1, 1].set_ylim(4800, 6100)
axs[1, 1].set_xlabel("Vehicle radius (m)")
axs[1, 1].set_ylabel("Observable area (m²)")
panel(axs[1, 1], "(d) Area vs. vehicle radius")
fig.tight_layout(h_pad=1.8, w_pad=1.8)
save(fig, "fig4-3_sensitivity")

# ================================================================ fig 4-4
X2, Y2 = make_grid(0.1)
c21, c22, c23, r2 = region_masks(X2, Y2, T2, TARGET_H["T2"], RMIN2)
m2 = c21 & c22 & c23
print("T2 field ready")

fig, (a4a, a4b) = plt.subplots(1, 2, figsize=(6.30, 3.15),
                               gridspec_kw={"width_ratios": [1.0, 1.05]})
field_map(a4a, X2, Y2, m2, r2, T2, RMIN2, 30.0)
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
a4a.legend(handles=[
    plt.Line2D([], [], color=C_RED, marker="*", ls="none", ms=8,
               label="target T2′"),
    plt.Line2D([], [], color=C_BLUE, marker="s", ls="none", ms=4,
               mec="k", label="vehicles V1–V5"),
    plt.Line2D([], [], color="#888888", ls="--", lw=0.8,
               label="30 s reach discs (90 m)"),
], loc="upper left", bbox_to_anchor=(1.01, 1.0), borderaxespad=0,
    framealpha=0.95)

ch = q2a["chosen"]
(p1x, p1y), (p2x, p2y) = ch["stations"]
zx0, zx1, zy0, zy1 = -2.0, 26.0, 60.0, 88.0
col = np.where((X2[0, :] >= zx0) & (X2[0, :] <= zx1))[0]
row = np.where((Y2[:, 0] >= zy0) & (Y2[:, 0] <= zy1))[0]
Z = np.where(m2[np.ix_(row, col)], r2[np.ix_(row, col)], np.nan)
a4b.imshow(Z, extent=(X2[0, col[0]], X2[0, col[-1]],
                      Y2[row[0], 0], Y2[row[-1], 0]),
           origin="lower", cmap=cm, vmin=RMIN2, vmax=30.0,
           interpolation="nearest", aspect="equal")
draw_buildings(a4b)
a4b.plot(T2[0] + RMIN2 * np.cos(th), T2[1] + RMIN2 * np.sin(th),
         color="w", lw=0.9, ls=(0, (4, 3)))
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
d_arc = Arc(T2, 10.0, 10.0, angle=0, theta1=ph1, theta2=ph1 + 90.0,
            color="k", lw=1.2)
a4b.add_patch(d_arc)
a4b.annotate("γ = 90°", xy=(T2[0] - 4.2, T2[1] - 4.0), fontsize=6)
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
fig, axs = plt.subplots(1, 3, figsize=(6.30, 2.35))
sig_rad = np.radians(1.0)
gam = np.linspace(12, 168, 600)
for g_lo, g_hi in ((12, 30), (150, 168)):
    axs[0].axvspan(g_lo, g_hi, color=C_RED, alpha=0.08)
for d, ls, col in ((5.8188, "-", C_BLUE), (10.0, "--", C_TEAL),
                   (15.0, "-.", C_GREEN), (20.0, ":", C_ORANGE)):
    axs[0].plot(gam, sig_rad * np.sqrt(2 * d * d) /
                np.sin(np.radians(gam)), ls, color=col, lw=0.9,
                label="d = %.1f m" % d)
axs[0].plot([90], [0.1016], marker="o", ms=4, mfc=C_RED, mec="k", mew=0.5,
            ls="none")
axs[0].annotate("selected", xy=(90, 0.1016), xytext=(60, 0.16),
                fontsize=5.5, arrowprops=dict(arrowstyle="->", lw=0.6))
axs[0].set_xlabel("Intersection angle γ (deg)")
axs[0].set_ylabel("DRMS (m)")
axs[0].legend(fontsize=5, loc="upper center", ncol=2, framealpha=0.9)
panel(axs[0], "(a) DRMS vs. γ (shaded: degenerate)")

dd = np.linspace(RMIN2, 30, 300)
for g, col, ls in ((60, C_TEAL, "-"), (90, C_BLUE, "--"), (120, C_ORANGE, "-.")):
    axs[1].plot(dd, sig_rad * dd * np.sqrt(2) / np.sin(np.radians(g)), ls,
                color=col, lw=0.9, label="γ = %g°" % g)
axs[1].plot([5.8188], [0.1016], marker="o", ms=4, mfc=C_RED, mec="k",
            mew=0.5, ls="none")
axs[1].set_xlabel("Station range d (m)")
axs[1].set_ylabel("DRMS (m)")
axs[1].legend(fontsize=5.5, loc="upper left", framealpha=0.9)
panel(axs[1], "(b) DRMS vs. range")

bb_sym = 2 * dd * np.sin(np.radians(90) / 2)
for g, col, ls in ((60, C_TEAL, "-"), (90, C_BLUE, "--"),
                   (120, C_ORANGE, "-.")):
    bb_g = 2 * dd * np.sin(np.radians(g) / 2)
    dr = sig_rad * dd * np.sqrt(2) / np.sin(np.radians(g))
    axs[2].plot(bb_g, dr, ls, color=col, lw=0.9, label="γ = %g°" % g)
axs[2].plot([8.2290], [0.1016], marker="o", ms=4, mfc=C_RED, mec="k",
            mew=0.5, ls="none")
axs[2].set_xlabel("Baseline B (m)")
axs[2].set_ylabel("DRMS (m)")
axs[2].legend(fontsize=5.5, loc="upper left", framealpha=0.9)
panel(axs[2], "(c) DRMS vs. baseline")
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
ax.add_patch(Circle(T2, s_iso * 2.4477, facecolor=C_RED, alpha=0.10,
                    ec="none"))
for k, col, ls in ((1, C_BLUE, "-"), (2, C_BLUE, "--"), (2.4477, C_RED, "-")):
    ax.add_patch(Circle(T2, s_iso * k, fill=False, ec=col, lw=1.1, ls=ls))
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
               mec="w", label="stations p1, p2"),
], loc="upper left", fontsize=6, framealpha=0.92)
axi = ax.inset_axes([0.60, 0.56, 0.37, 0.40])
axi.add_patch(Circle(T2, s_iso * 2.4477, facecolor=C_RED, alpha=0.10,
                     ec="none"))
for k, col, ls in ((1, C_BLUE, "-"), (2, C_BLUE, "--"), (2.4477, C_RED, "-")):
    axi.add_patch(Circle(T2, s_iso * k, fill=False, ec=col, lw=1.5, ls=ls))
axi.plot([T2[0] - dir1[0] * 1.2, T2[0] + dir1[0] * 1.2],
         [T2[1] - dir1[1] * 1.2, T2[1] + dir1[1] * 1.2],
         color="k", lw=0.6, ls=":")
axi.plot([T2[0] - dir2[0] * 1.2, T2[0] + dir2[0] * 1.2],
         [T2[1] - dir2[1] * 1.2, T2[1] + dir2[1] * 1.2],
         color="k", lw=0.6, ls=":")
axi.plot(T2[0], T2[1], marker="*", ms=9, color=C_RED, ls="none")
axi.set_xlim(T2[0] - 0.9, T2[0] + 0.9)
axi.set_ylim(T2[1] - 0.9, T2[1] + 0.9)
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
fig = plt.figure(figsize=(6.30, 3.10))
gs = fig.add_gridspec(1, 2, width_ratios=[2.6, 1.0], wspace=0.12)
axg = fig.add_subplot(gs[0])
for v in range(5):
    for seg in segs[f"V{v+1}"]:
        typ, t0, t1 = seg[0], float(seg[1]), float(seg[2])
        col, al = STYLE_G[typ]
        axg.broken_barh([(t0, max(t1 - t0, 0.03))], (v - 0.30, 0.60),
                        facecolors=col, edgecolor="#777777", linewidth=0.3,
                        alpha=al)
starts_map = q2b["optimized"]["alert_starts"]
for a, sv in (("T1", 1.607), ("T2", 6.994), ("T3", 10.355)):
    axg.axvline(sv, color="k", lw=0.6, ls=":")
    axg.annotate(a, xy=(sv, 4.92), fontsize=6, ha="center")
axg.set_ylim(-0.6, 5.35)
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
], loc="upper center", bbox_to_anchor=(0.5, -0.20), fontsize=6.5, ncol=5, frameon=False, columnspacing=1.2, handlelength=1.3)
panel(axg, "(a) Optimized vehicle timeline")

axm = fig.add_subplot(gs[1])
stmap = q2b["optimized"]["stations"]
ordv = q2b["optimized"]["orders"]
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
