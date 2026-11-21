# -*- coding: utf-8 -*-
"""Problem-4 figures (numbers only; captions live in the PPTX notes)."""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import q4_lib4  # noqa: F401  (sets sys.path for 第二题/code)
from q2_lib import BUILDINGS, TARGETS, VEHICLES, FIELD

matplotlib.rcParams["svg.fonttype"] = "none"
matplotlib.rcParams["font.family"] = "Times New Roman"
matplotlib.rcParams["mathtext.fontset"] = "stix"
matplotlib.rcParams["axes.linewidth"] = 0.8

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(BASE, "figures")
RES_DIR = os.path.join(BASE, "results")
os.makedirs(FIG_DIR, exist_ok=True)

with open(os.path.join(RES_DIR, "q4_results.json"), encoding="utf-8") as f:
    R4 = json.load(f)

COL_BLD, COL_EDGE = "#b3b3b3", "#4d4d4d"
COL_TGT, COL_VEH = "#d62728", "#1f77b4"
VEH_COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd", "#8c564b"]
STYLE = {"travel": ("#c9dff0", 0.95), "slew": ("#f4c78f", 0.95),
         "wait": ("#e4e4e4", 0.9), "obs": ("#2ca02c", 1.0),
         "reset": ("#f2a19b", 0.95)}


def _clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(labelsize=10)


def save(fig, name):
    fig.savefig(os.path.join(FIG_DIR, name + ".svg"), bbox_inches="tight")
    fig.savefig(os.path.join(FIG_DIR, name + ".png"), dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("saved", name)


def draw_field(ax):
    for (x0, x1, y0, y1, h) in BUILDINGS:
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor=COL_BLD,
                               edgecolor=COL_EDGE, lw=0.8))


# --- fig1: map of the 24 new-alert positions -------------------------------
fig, ax = plt.subplots(figsize=(6.8, 6.2))
draw_field(ax)
sc = R4["scen_new"]
xs = [50 + s["R"] * np.cos(np.radians(s["theta"])) for s in sc]
ys = [50 + s["R"] * np.sin(np.radians(s["theta"])) for s in sc]
cs = [s["resched"]["t_last"] for s in sc]
im = ax.scatter(xs, ys, c=cs, cmap="viridis_r", s=90, edgecolors="k",
                linewidths=0.6)
cb = fig.colorbar(im, ax=ax, shrink=0.85)
cb.set_ticks(range(8, 33, 4))
for a in ("T1", "T2", "T3"):
    ax.plot(TARGETS[a][0], TARGETS[a][1], marker="*", ms=13, color=COL_TGT)
ax.plot(VEHICLES[:, 0], VEHICLES[:, 1], linestyle="none", marker="s", ms=6,
        mfc=COL_VEH, mec="k", mew=0.5)
ax.add_patch(Rectangle((0, 0), 100, 100, fill=False, ec="k", lw=1.2))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_xticks(range(0, 101, 20))
ax.set_yticks(range(0, 101, 20))
ax.set_aspect("equal")
_clean(ax)
save(fig, "fig1_map_new_alerts")

# --- fig2: t_last vs azimuth for the three R ------------------------------
fig, ax = plt.subplots(figsize=(7.4, 4.6))
for R, col in ((30.0, "#1f77b4"), (40.0, "#2ca02c"), (50.0, "#ff7f0e")):
    pts = sorted(((s["theta"], s["resched"]["t_last"]) for s in sc
                  if s["R"] == R))
    th = [p[0] for p in pts]
    tl = [p[1] for p in pts]
    th.append(th[0] + 360)
    tl.append(tl[0])
    ax.plot(th, tl, color=col, lw=1.8, marker="o", ms=5, label=None)
ax.axhline(60, color="#d62728", lw=1.4, ls="--")
ax.axhline(10.83, color="k", lw=1.0, ls=":")
ax.set_xlim(0, 360)
ax.set_xticks(range(0, 361, 45))
ax.set_ylim(0, 65)
ax.set_yticks(range(0, 61, 10))
_clean(ax)
save(fig, "fig2_tlast_vs_theta")

# --- fig3: single-failure scenarios ---------------------------------------
fig, (a3a, a3b) = plt.subplots(1, 2, figsize=(11.0, 4.3))
sf = R4["scen_fail"]
labels = [s["failed"] for s in sf]
x = np.arange(5)
w = 0.36
a3a.bar(x - w / 2, [s["keep"]["eta"] for s in sf], w, color="#f2a19b",
        ec="k", lw=0.5)
a3a.bar(x + w / 2, [s["resched"]["eta"] for s in sf], w, color="#2ca02c",
        ec="k", lw=0.5)
a3a.set_ylim(0, 1.15)
a3a.set_yticks([0, 1/3, 2/3, 1.0])
a3a.set_xticks(x)
a3a.set_xticklabels([str(i + 1) for i in x])
a3b.bar(x - w / 2, [s["keep"]["t_last"] for s in sf], w, color="#f2a19b",
        ec="k", lw=0.5)
a3b.bar(x + w / 2, [s["resched"]["t_last"] for s in sf], w, color="#2ca02c",
        ec="k", lw=0.5)
a3b.set_ylim(0, 65)
a3b.set_yticks(range(0, 61, 10))
a3b.set_xticks(x)
a3b.set_xticklabels([str(i + 1) for i in x])
_clean(a3a)
_clean(a3b)
save(fig, "fig3_failures")

# --- fig4: failure x outage ----------------------------------------------
fig, ax = plt.subplots(figsize=(7.4, 4.6))
T_REC_LIST = sorted({s["t_rec"] for s in R4["scen_fail_out"]})
cols = {"V1": "#1f77b4", "V2": "#ff7f0e", "V3": "#2ca02c", "V4": "#9467bd",
        "V5": "#8c564b"}
for fv in ("V1", "V2", "V3", "V4", "V5"):
    pts = sorted(((s["t_rec"], s["resched"]["t_last"]) for s in R4["scen_fail_out"]
                  if s["failed"] == fv))
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=cols[fv],
            lw=1.7, marker="o", ms=6)
    kp = [s["keep"]["t_last"] for s in R4["scen_fail_out"] if s["failed"] == fv]
    ax.plot([p[0] for p in pts], kp, color=cols[fv], lw=1.0, ls=":",
            marker="x", ms=7)
ax.set_xticks(T_REC_LIST)
ax.set_ylim(0, 65)
ax.set_yticks(range(0, 61, 10))
_clean(ax)
save(fig, "fig4_fail_outage")

# --- fig5: representative Gantt (failure V4): keep vs reschedule ----------
rep = R4["representative"]
fig, (a5a, a5b) = plt.subplots(1, 2, figsize=(13.0, 4.4))
dead = set(rep["keep_failV4"]["dead"])          # {"T2"}
for v in range(5):
    if v == 3:                                  # failed vehicle row: empty
        continue
    for seg in R4["baseline"]["segments"][f"V{v+1}"]:
        typ, t0, t1, a = seg[0], float(seg[1]), float(seg[2]), seg[3]
        if a in dead and typ in ("obs", "reset"):
            continue
        if a in dead and typ == "wait":
            t1 = 60.0
        col, al = STYLE[typ]
        a5a.broken_barh([(t0, max(t1 - t0, 0.02))], (v - 0.32, 0.64),
                        facecolors=col, edgecolor=COL_EDGE, lw=0.4, alpha=al)
segs = rep["resched_failV4"].get("segs", {})
for v in range(5):
    for seg in segs.get(f"V{v+1}", []):
        typ, t0, t1 = seg[0], float(seg[1]), float(seg[2])
        col, al = STYLE[typ]
        a5b.broken_barh([(t0, max(t1 - t0, 0.02))], (v - 0.32, 0.64),
                        facecolors=col, edgecolor=COL_EDGE, lw=0.4, alpha=al)
for ax in (a5a, a5b):
    ax.set_ylim(-0.7, 4.7)
    ax.set_yticks(range(5))
    ax.set_yticklabels([f"V{i + 1}" for i in range(5)])
    ax.set_xlim(0, 60)
    ax.set_xticks(range(0, 61, 10))
    _clean(ax)
from matplotlib.patches import Patch
fig.legend(handles=[
    Patch(facecolor=STYLE[k][0], edgecolor=COL_EDGE,
          label=lbl) for k, lbl in
    (("travel", "travel"), ("slew", "slew"), ("wait", "wait"),
     ("obs", "observation (5 s)"), ("reset", "reset"))],
    loc="lower center", ncol=5, frameon=False, fontsize=9)
fig.subplots_adjust(bottom=0.2)
save(fig, "fig5_gantt_failV4")

# --- fig6: all-scenarios scatter -----------------------------------------
fig, ax = plt.subplots(figsize=(7.0, 4.8))


def all_pairs():
    kp, rp = [], []
    blocks = ("scen_new", "scen_fail", "scen_out", "scen_fail_out",
              "scen_new_fail", "scen_new_out", "scen_triple")
    for b in blocks:
        for s in R4[b]:
            kp.append((s["keep"]["t_last"], s["keep"]["eta"]))
            rp.append((s["resched"]["t_last"], s["resched"]["eta"]))
    return kp, rp


kp, rp = all_pairs()
ax.scatter([p[0] for p in kp], [p[1] for p in kp], marker="x", s=70,
           color="#d62728", alpha=0.85, zorder=5)
ax.scatter([p[0] for p in rp], [p[1] for p in rp], marker="o", s=55,
           facecolors="none", edgecolors="#2ca02c", linewidths=1.5, zorder=6)
ax.set_xlim(-2, 62)
ax.set_ylim(0.4, 1.12)
ax.set_yticks([0.5, 0.75, 1.0])
ax.set_xticks(range(0, 61, 10))
_clean(ax)
save(fig, "fig6_global_scatter")

print("all problem-4 figures done")
