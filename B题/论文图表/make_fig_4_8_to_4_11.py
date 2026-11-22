# -*- coding: utf-8 -*-
"""Paper figures 4-8 .. 4-11 (Q3 + Q4), premium multi-panel versions."""
import json
import os
import statistics
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

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

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(B, "论文图表")
os.makedirs(OUT, exist_ok=True)
q3 = json.load(open(os.path.join(B, "第三题", "results", "q3_results.json"),
                    encoding="utf-8"))
q4 = json.load(open(os.path.join(B, "第四题", "results", "q4_results.json"),
                    encoding="utf-8"))

C_BLUE = "#3D6FA8"
C_RED = "#B5443E"
C_GREEN = "#4C9B6B"
C_ORANGE = "#E09B3D"
C_PURPLE = "#7B62A8"
C_TEAL = "#2E7D8C"
STYLE_G = {"travel": ("#CBDCEF", 0.95), "slew": ("#F5C68B", 0.95),
           "wait": ("#E6E6E6", 0.9), "obs": ("#3E9B6C", 1.0),
           "reset": ("#F2B0A6", 0.95)}
K_LOC = 1.432394
S_MAX = q3["s_max_m"]
S_CROSS = q3["s_crossover_m"]
S_PSI_MAX = q3["sigma_psi_max_deg"]


def panel(ax, s):
    ax.set_title(s, loc="left", fontsize=9, fontweight="bold", pad=4)


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".svg"), bbox_inches="tight")
    fig.savefig(os.path.join(OUT, name + ".png"), dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("saved", name)


# ================================================================ fig 4-8
fig, (a8a, a8b) = plt.subplots(1, 2, figsize=(6.30, 2.90))
ss = np.linspace(0, 90, 901)
sig = 0.3 + 0.02 * ss
loc = K_LOC * sig
tot = np.sqrt(loc ** 2 + 1.0)
a8a.fill_between(ss, loc, tot, color=C_ORANGE, alpha=0.18,
                 label="gimbal share")
a8a.plot(ss, loc, color=C_BLUE, lw=1.0, label="localization term")
a8a.plot(ss, tot, color=C_RED, lw=1.4, label="total σ_ψ(s)")
a8a.axhline(S_PSI_MAX, color=C_GREEN, lw=1.0, ls="--",
            label="allowable 5/z$_{0.975}$")
a8a.axhline(1.0, color=C_ORANGE, lw=0.9, ls=":")
a8a.axvline(S_MAX, color="k", lw=0.8, ls=":")
a8a.plot([S_MAX], [S_PSI_MAX], marker="o", ms=5, mfc=C_GREEN, mec="k",
         mew=0.5, ls="none")
a8a.annotate("s$_{max}$ = 66.92 m", xy=(S_MAX, S_PSI_MAX),
             xytext=(30, 3.3), fontsize=6,
             arrowprops=dict(arrowstyle="->", lw=0.6))
a8a.set_xlim(0, 90)
a8a.set_ylim(0, 4.0)
a8a.set_xlabel("Travel distance s (m)")
a8a.set_ylabel("σ (deg)")
a8a.legend(fontsize=5.5, loc="upper left", framealpha=0.92)
panel(a8a, "(a) σ components vs. travel distance")

var_loc = loc ** 2
var_tot = var_loc + 1.0
sh_l = var_loc / var_tot * 100
sh_z = 0.64 / var_tot * 100
sh_c = 0.36 / var_tot * 100
a8b.stackplot(ss, sh_l, sh_z, sh_c,
              colors=["#B9D3EC", "#F5C68B", "#F2B0A6"],
              labels=["localization", "zero-offset", "control"],
              edgecolor="w", lw=0.3)
a8b.axvline(S_CROSS, color="k", lw=0.8, ls=":")
a8b.annotate("crossover\n19.9 m", xy=(S_CROSS, 50), xytext=(4, 68),
             fontsize=6, arrowprops=dict(arrowstyle="->", lw=0.6))
a8b.axvline(S_MAX, color="k", lw=0.8, ls=":")
a8b.annotate("s$_{max}$", xy=(S_MAX, 88), fontsize=6)
a8b.set_xlim(0, 90)
a8b.set_ylim(0, 100)
a8b.set_xlabel("Travel distance s (m)")
a8b.set_ylabel("Variance share (%)")
a8b.legend(handles=[Patch(facecolor="#B9D3EC", label="localization"),
                    Patch(facecolor="#F5C68B", label="zero-offset"),
                    Patch(facecolor="#F2B0A6", label="control")],
           fontsize=6, loc="upper center", bbox_to_anchor=(0.5, -0.30),
           ncol=3, frameon=False)
panel(a8b, "(b) Variance decomposition")
fig.tight_layout(w_pad=1.6)
save(fig, "fig4-8_variance")

# ================================================================ fig 4-9
fig, (a9a, a9b) = plt.subplots(1, 2, figsize=(6.30, 2.90),
                               gridspec_kw={"width_ratios": [1.15, 1.0]})
nd = statistics.NormalDist()
ss = np.linspace(0, 90, 901)
sig_psi = np.sqrt((1.432394 * (0.3 + 0.02 * ss)) ** 2 + 1.0)
cdf = np.vectorize(lambda v: nd.cdf(v))
p_curve = 2 * cdf(5.0 / sig_psi) - 1
a9a.fill_between(ss, p_curve, 0.95, where=p_curve >= 0.95,
                 color=C_GREEN, alpha=0.15)
a9a.plot(ss, p_curve, color=C_BLUE, lw=1.2, label="analytic (linearized)")
mc = {m["s"]: (m["P_emp"], m["P_ana"]) for m in q3["monte_carlo"]["points"]}
mk_s = sorted(mc.keys())
a9a.plot(mk_s, [mc[s][0] for s in mk_s], linestyle="none", marker="o",
         ms=4, mfc=C_ORANGE, mec="k", mew=0.4, label="Monte Carlo (n = 10⁶)")
a9a.axhline(0.95, color=C_GREEN, lw=0.9, ls="--")
a9a.axvline(S_MAX, color="k", lw=0.7, ls=":")
a9a.annotate("s$_{max}$ = 66.92 m\n(exact 66.84 m)", xy=(S_MAX, 0.95),
             xytext=(38, 0.72), fontsize=6,
             arrowprops=dict(arrowstyle="->", lw=0.6))
a9a.set_xlim(0, 90)
a9a.set_ylim(0.5, 1.02)
a9a.set_xlabel("Travel distance s (m)")
a9a.set_ylabel("P(|Δψ| ≤ 5°)")
a9a.legend(fontsize=6, loc="lower left", framealpha=0.92)
panel(a9a, "(a) Pointing accuracy vs. travel distance")

aa = np.linspace(0, 2.2, 400)
iso = {k: v["ab_max_m"] for k, v in q3["ab_region"]["iso_levels"].items()}
a9b.fill_between(aa, 0, np.clip((1.6384 - aa) / 80.0, 0, None),
                 where=aa <= 1.6384, color="#BFD7EE", alpha=0.7,
                 label="feasible (P ≥ 0.95)")
for lv, col, ls in (("0.9", C_ORANGE, "-"), ("0.95", C_GREEN, "-"),
                    ("0.98", C_PURPLE, "--"), ("0.99", C_RED, "-")):
    a9b.plot(aa, (iso[lv] - aa) / 80.0, ls, color=col, lw=0.9,
             label="P = " + lv)
a9b.plot([0.3], [0.02], marker="s", ms=6, mfc=C_RED, mec="k", mew=0.5,
         ls="none")
a9b.annotate("nominal (0.3, 0.02)\n— outside the region", xy=(0.3, 0.02),
             xytext=(0.52, 0.0222), fontsize=6,
             arrowprops=dict(arrowstyle="->", lw=0.6))
a9b.set_xlim(0, 2.2)
a9b.set_ylim(0, 0.026)
a9b.set_yticks([0, 0.005, 0.010, 0.015, 0.020, 0.025])
a9b.set_xlabel("Intercept a (m)")
a9b.set_ylabel("Slope b (m per m)")
a9b.legend(fontsize=5.5, loc="upper right", framealpha=0.92)
panel(a9b, "(b) (a, b) feasible region at 80 m")
fig.tight_layout(w_pad=1.6)
save(fig, "fig4-9_probability_ab")

# ================================================================ fig 4-10
fig, (a10a, a10b) = plt.subplots(1, 2, figsize=(6.30, 2.90))
sn = q4["scen_new"]
for R, col, mk in ((30.0, C_ORANGE, "o"), (40.0, C_GREEN, "s"),
                   (50.0, C_PURPLE, "^")):
    pts = sorted(((s["theta"], s["resched"]["t_last"]) for s in sn
                  if s["R"] == R))
    th = [p[0] for p in pts] + [pts[0][0] + 360]
    tl = [p[1] for p in pts] + [pts[0][1]]
    a10a.plot(th, tl, color=col, lw=0.9, marker=mk, ms=3,
              label="R = %g m" % R)
a10a.axhline(60, color=C_RED, lw=1.0, ls="--")
a10a.annotate("keep-original (60 s)", xy=(310, 60), xytext=(215, 55.5),
              fontsize=6, color=C_RED)
a10a.axhline(10.36, color="k", lw=0.7, ls=":")
a10a.annotate("undisturbed 10.36 s", xy=(45, 10.36), xytext=(50, 6.0),
              fontsize=6)
a10a.set_xlim(0, 360)
a10a.set_xticks(range(0, 361, 60))
a10a.set_ylim(0, 65)
a10a.set_yticks(range(0, 61, 10))
a10a.set_xlabel("New-alert azimuth θ (deg)")
a10a.set_ylabel("t$_{last}$ (s)")
a10a.legend(fontsize=6, loc="upper center", bbox_to_anchor=(0.5, -0.30),
            ncol=3, frameon=False)
panel(a10a, "(a) Rescheduled t$_{last}$ vs. azimuth")

fo = {(s["failed"], s["t_rec"]): s["resched"]["t_last"]
      for s in q4["scen_fail_out"]}
fk = {(s["failed"], s["t_rec"]): s["keep"]["t_last"]
      for s in q4["scen_fail_out"]}
trecs = (10.0, 20.0, 30.0)
for fv, col, mk in (("V1", C_BLUE, "o"), ("V2", C_ORANGE, "s"),
                    ("V3", C_GREEN, "^"), ("V4", C_PURPLE, "D"),
                    ("V5", C_TEAL, "v")):
    ys = [fo[(fv, t)] for t in trecs]
    a10b.plot(trecs, ys, color=col, lw=0.9, marker=mk, ms=4, label="fail " + fv)
    kys = [fk[(fv, t)] for t in trecs]
    a10b.plot(trecs, kys, color=col, lw=0.7, ls=":", marker="x", ms=5)
a10b.annotate("keep-original = 60 s\nfor any impacted failure",
              xy=(30, 60), xytext=(10.5, 52), fontsize=6, color=C_RED)
a10b.set_xticks(trecs)
a10b.set_ylim(0, 65)
a10b.set_yticks(range(0, 61, 10))
a10b.set_xlabel("Recovery time t$_{rec}$ (s)")
a10b.set_ylabel("t$_{last}$ (s)")
a10b.legend(fontsize=6, loc="upper center",
            bbox_to_anchor=(0.5, -0.30), ncol=3, frameon=False)
panel(a10b, "(b) t$_{last}$ vs. recovery time (solid: resched, dotted: keep)")
fig.tight_layout(w_pad=1.6)
save(fig, "fig4-10_tlast_response")

# ================================================================ fig 4-11
fig, (a11a, a11b) = plt.subplots(1, 2, figsize=(6.30, 2.90),
                                 gridspec_kw={"width_ratios": [1.0, 1.0]})
segs = q4["representative"]["resched_failV4"]["segs"]
for v in range(5):
    for seg in segs.get(f"V{v+1}", []):
        typ, t0, t1 = seg[0], float(seg[1]), float(seg[2])
        col, al = STYLE_G[typ]
        a11a.broken_barh([(t0, max(t1 - t0, 0.03))], (v - 0.30, 0.60),
                         facecolors=col, edgecolor="#777777", lw=0.3,
                         alpha=al)
a11a.annotate("V4 failed at t = 5 s", xy=(30, 3.0), fontsize=6,
              color=C_RED, ha="center", va="center")
a11a.legend(handles=[
    Patch(facecolor=STYLE_G["travel"][0], ec="#777777", label="travel"),
    Patch(facecolor=STYLE_G["slew"][0], ec="#777777", label="slew"),
    Patch(facecolor=STYLE_G["wait"][0], ec="#777777", label="wait"),
    Patch(facecolor=STYLE_G["obs"][0], ec="#777777", label="observe"),
    Patch(facecolor=STYLE_G["reset"][0], ec="#777777", label="reset"),
], loc="lower right", fontsize=5.5, ncol=2, framealpha=0.92,
    columnspacing=0.9, handlelength=1.2, borderaxespad=0.4)
for a, sv in (("T2", 6.994), ("T3", 10.355)):
    a11a.axvline(sv, color="k", lw=0.6, ls=":")
    a11a.annotate(a, xy=(sv, 4.42), fontsize=6, ha="center",
                  annotation_clip=False)
a11a.set_ylim(-0.6, 4.6)
a11a.set_yticks(range(5))
a11a.set_yticklabels(["V1", "V2", "V3", "V4", "V5"])
a11a.set_xlim(0, 60)
a11a.set_xlabel("Time (s)")
panel(a11a, "(a) Rescheduled timeline (V4 failure, η = 1.00)")

kp, rp = [], []
for b in ("scen_new", "scen_fail", "scen_out", "scen_fail_out",
          "scen_new_fail", "scen_new_out", "scen_triple"):
    for s in q4[b]:
        kp.append((s["keep"]["t_last"], s["keep"]["eta"]))
        rp.append((s["resched"]["t_last"], s["resched"]["eta"]))
for (kt, ke), (rt, re) in zip(kp, rp):
    if re > ke or (abs(re - ke) < 1e-9 and rt < kt - 1e-9):
        a11b.annotate("", xy=(rt, re), xytext=(kt, ke),
                      arrowprops=dict(arrowstyle="->", color="#BBBBBB",
                                      lw=0.5, alpha=0.6))
a11b.scatter([p[0] for p in kp], [p[1] for p in kp], marker="x", s=22,
             color=C_RED, alpha=0.85, zorder=5,
             label="keep-original (74)")
a11b.scatter([p[0] for p in rp], [p[1] for p in rp], marker="o", s=26,
             facecolors="none", edgecolors=C_GREEN, linewidths=1.0,
             zorder=6, label="rescheduling (74)")
a11b.set_xlim(-2, 62)
a11b.set_ylim(0.4, 1.12)
a11b.set_yticks([0.5, 0.75, 1.0])
a11b.set_xticks(range(0, 61, 10))
a11b.set_xlabel("t$_{last}$ (s)")
a11b.set_ylabel("Completion ratio η")
a11b.legend(fontsize=6, loc="upper left", framealpha=0.92)
panel(a11b, "(b) All 74 scenarios: keep-original vs. rescheduling")
fig.tight_layout(w_pad=1.6)
save(fig, "fig4-11_resched_compare")
print("PART 2 DONE")
