# -*- coding: utf-8 -*-
"""Framework diagram: vertical problem chain with concrete-quantity arrows.

Layout follows the agreed structure: input bar + four problem blocks stacked
vertically (Q2 holds sub-problems (1)/(2)), spine arrows labelled with the
quantity that is passed on, and a side bypass carrying the Q2 -> Q4 timeline
relation. All text English, Times New Roman; an overflow assertion keeps
every text inside its block (learned from the border-crossing bug).
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

import scienceplots  # noqa: F401

plt.style.use(["science", "ieee", "no-latex"])
matplotlib.rcParams.update({
    "svg.fonttype": "none",
    "font.family": "Times New Roman",
    "mathtext.fontset": "stix",
    "figure.dpi": 300,
    "savefig.dpi": 300,
})

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(B, "论文图表")

C_BLUE = "#3D6FA8"
C_TEAL = "#2E7D8C"
C_GREEN = "#3E9B6C"
C_PURPLE = "#7B62A8"
C_ORANGE = "#D98E3B"

fig, ax = plt.subplots(figsize=(6.30, 6.93))
ax.set_xlim(0, 100)
ax.set_ylim(0, 110)
ax.axis("off")

BX, BW = 2.0, 70.0            # all blocks share the same column
CHECKS = []                   # (name, rect, [text artists])


def block(y, h, title, bullets, fc, ec, title_fs=7.2, bullet_fs=6.2):
    ax.add_patch(FancyBboxPatch((BX, y), BW, h,
                                boxstyle="round,pad=0.8,rounding_size=1.2",
                                facecolor=fc, edgecolor=ec, linewidth=1.0))
    texts = []
    t = ax.text(BX + BW / 2, y + h - 2.0, title, ha="center", va="top",
                fontsize=title_fs, fontweight="bold")
    texts.append(t)
    ty = y + h - 6.6
    for b in bullets:
        texts.append(ax.text(BX + 1.6, ty, b, ha="left", va="top",
                             fontsize=bullet_fs, linespacing=1.15))
        ty -= 2.75
    CHECKS.append((title.split("—")[0].strip(), (BX, y, BW, h), texts))
    return y, h


# ----------------------------- blocks ---------------------------------------
block(101.6, 5.7, "", [], "#EDEDED", "#9E9E9E")               # input bar
ax.text(BX + BW / 2, 104.45,
        "Input:  field 100 m × 100 m · buildings B1–B5 · vehicles V1–V5\n"
        "alerts T1–T3 · bearing error σ$_{α}$ = 1°",
        ha="center", va="center", fontsize=6.3, color="#333333",
        linespacing=1.25)
CHECKS[-1][2].append(ax.texts[-1])

block(81.4, 14.5, "Problem 1 — Observable region & optimal station",
      ["Ω = C1 ∩ C2 ∩ C3 = 5610.4 m²",
       "r* = 7.5821 m (elevation bound active, ε = 80°)",
       "optimal arc 283.85° · global optimum p* = (88.88, 76.29)"],
      "#EAF1F8", C_BLUE)

block(54.9, 18.3, "Problem 2 — Two-station accuracy & six-slot scheduling",
      ["(1) DRMS = σ$_{α}$·G, G ≥ 5.8188 m (γ = 90°) → DRMS ≥ 0.1016 m; "
       "pair V3 + V5 (B = 8.23 m)",
       "(2) Algorithm 1: C(5,2)³ = 1000 structures → makespan 10.355 s "
       "(baseline 20.968 s)",
       "plug-back: γ(T1) = 19.34°, DRMS = 3.08 m; γ ≥ 30° window costs "
       "+25.4%"],
      "#E7F1F0", C_TEAL)

block(32.2, 14.5, "Problem 3 — Error propagation & pointing accuracy",
      ["Δψ ~ N(0, (1.432σ(s))² + 1.0), σ(s) = a + b·s",
       "s$_{max}$ = 66.92 m (exact 66.84 m) for P(|Δψ| ≤ 5°) = 0.95",
       "a + 80b ≤ 1.6384 m for 80 m itineraries"],
      "#F1EDF6", C_PURPLE)

block(9.5, 14.5, "Problem 4 — Rescheduling under disturbances",
      ["74 scenarios: new alarms / vehicle failure / observation outage",
       "η improved in 67, 0 degraded",
       "structural loss → temporal loss · two-phase t$_{last}$ response"],
      "#FBF3E4", C_ORANGE)

# ----------------------------- spine arrows ---------------------------------
SPINE_X = 37.0
arrows = [
    (101.6, 95.9, "problem data"),
    (81.4, 73.2, "feasible stations Ω$_a$ (5610.4 m²)"),
    (54.9, 46.7, "deployed geometry & driving legs s (Q2 max 3.10 m)"),
    (32.2, 24.0, "driving budget s ≤ 66.92 m (Q4 max leg 18.14 m)"),
]
for y_top, y_bot, lab in arrows:
    ax.add_patch(FancyArrowPatch((SPINE_X, y_top - 0.6), (SPINE_X, y_bot + 0.6),
                                 arrowstyle="-|>", mutation_scale=11,
                                 color="#555555", lw=1.0))
    ax.text(SPINE_X + 3.0, (y_top + y_bot) / 2, lab, ha="left", va="center",
            fontsize=6.0, color="#444444")

# bypass Q2 -> Q4 on the right: optimized timeline = rescheduling baseline
q2_mid, q4_mid = 64.05, 16.75
ax.plot([BX + BW, 86.0], [q2_mid, q2_mid], color="#777777", lw=1.0)
ax.plot([86.0, 86.0], [q2_mid, q4_mid], color="#777777", lw=1.0)
ax.add_patch(FancyArrowPatch((86.0, q4_mid), (BX + BW + 0.6, q4_mid),
                             arrowstyle="-|>", mutation_scale=11,
                             color="#777777", lw=1.0))
ax.text(80.5, 67.8, "optimized timeline\n= rescheduling baseline",
        ha="center", va="bottom", fontsize=5.8, color="#555555",
        linespacing=1.2)

# ----------------------------- overflow assertion ---------------------------
fig.canvas.draw()
renderer = fig.canvas.get_renderer()
inv = ax.transData.inverted()
bad_all = []
for name, (x0, y0, w, h), texts in CHECKS:
    for t in texts:
        bb = t.get_window_extent(renderer)
        dx0, dy0 = inv.transform((bb.x0, bb.y0))
        dx1, dy1 = inv.transform((bb.x1, bb.y1))
        if dx0 < x0 - 0.8 or dx1 > x0 + w + 0.8 or dy0 < y0 - 0.8 \
                or dy1 > y0 + h + 0.8:
            bad_all.append((name, t.get_text()[:45],
                            round(dx0, 1), round(dx1, 1),
                            round(dy0, 1), round(dy1, 1)))
if bad_all:
    print("OVERFLOW detected:")
    for row in bad_all:
        print("   ", row)
    sys.exit(1)

fig.savefig(os.path.join(OUT, "fig0_framework.svg"), bbox_inches="tight")
fig.savefig(os.path.join(OUT, "fig0_framework.png"), dpi=300,
            bbox_inches="tight")
print("saved fig0_framework (vertical chain, overflow check passed)")
