# -*- coding: utf-8 -*-
"""
2026 "ShuWei Cup" Problem B -- Problem 1
Observable region and optimal observation station for target T1.

Model (see Q1_modeling_document.docx):
  Decision variable : p = (x, y)  station center on the ground plane
  C1 vehicle geometry : R_VEH <= x,y <= FIELD-R_VEH  and  dist(p, B_i) >= R_VEH
  C2 gimbal elevation : eps(p) = atan((H1-H_CAM)/r) in [ELEV_MIN, ELEV_MAX]
                        -> r >= R_MIN = (H1-H_CAM)/tan(ELEV_MAX)   (closed form)
  C3 LOS occlusion    : 3D segment (p, H_CAM) -> (T1, H1) must not touch any prism
  Observable region   : Omega = C1 & C2 & C3
  Optimization        : max Q = 1/r  <=>  min r  s.t. p in Omega
  Analytic result     : global optimum r* = R_MIN attained on the feasible arc
                        of the circle r = R_MIN around T1'  -> tie-breaking needed

Outputs: figures/*.svg + *.png (no letters inside figures), results/q1_results.json
Author: team working scripts
"""
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import scienceplots  # noqa: F401  (SciencePlots styles: science/ieee/grid)

# ----------------------------- global settings ------------------------------
plt.style.use(["science", "ieee", "no-latex", "grid"])
matplotlib.rcParams["svg.fonttype"] = "none"      # digits stay editable text in PPT
matplotlib.rcParams["font.family"] = "Times New Roman"
matplotlib.rcParams["mathtext.fontset"] = "stix"
matplotlib.rcParams["font.size"] = 10
matplotlib.rcParams["axes.linewidth"] = 0.8
matplotlib.rcParams["xtick.direction"] = "in"
matplotlib.rcParams["ytick.direction"] = "in"

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo-relative
FIG_DIR = os.path.join(BASE, "figures")
RES_DIR = os.path.join(BASE, "results")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(RES_DIR, exist_ok=True)

# ----------------------------- problem constants ----------------------------
FIELD = 100.0                       # field size (m)
O_POS = (50.0, 50.0)                # dispatch center
R_VEH = 1.5                         # vehicle equivalent disk radius (m)
H_CAM = 2.0                         # camera height (m)
SPEED = 3.0                         # vehicle speed (m/s)
ELEV_MIN, ELEV_MAX = -10.0, 80.0    # gimbal elevation range (deg)

# buildings: (x0, x1, y0, y1, height)
BUILDINGS = [
    (22.0, 34.0, 16.0, 26.0, 20.0),   # B1
    (63.0, 79.0, 59.0, 71.0, 28.0),   # B2
    (10.0, 24.0, 65.0, 76.0, 12.0),   # B3
    (72.0, 86.0, 22.0, 34.0, 24.0),   # B4
    (41.0, 51.0, 38.0, 46.0, 32.0),   # B5
]

# base alert T1: (azimuth deg, horizontal range m, altitude m)
THETA1, R1, H1 = 30.0, 40.0, 45.0
T1 = np.array([50.0 + R1 * np.cos(np.radians(THETA1)),
               50.0 + R1 * np.sin(np.radians(THETA1))])   # (84.6410, 70.0000)

VEHICLES = np.array([[15.0, 14.0], [88.0, 10.0], [14.0, 86.0],
                     [88.0, 68.0], [50.0, 93.0]])         # V1..V5

# closed-form lower bound from C2
R_MIN = (H1 - H_CAM) / np.tan(np.radians(ELEV_MAX))       # 7.5821 m


# ----------------------------- core model -----------------------------------
def dist_to_rect(px, py, rect):
    """Distance from points (px, py) to axis-aligned rectangle (x0,x1,y0,y1)."""
    x0, x1, y0, y1 = rect[0], rect[1], rect[2], rect[3]
    dx = np.maximum(np.maximum(x0 - px, px - x1), 0.0)
    dy = np.maximum(np.maximum(y0 - py, py - y1), 0.0)
    return np.hypot(dx, dy)


def los_blocked(px, py, buildings, tol=1e-9):
    """Vectorized 3D segment-vs-AABB occlusion test (slab method).

    Segment: (px, py, H_CAM) -> (T1x, T1y, H1).
    Touching counts as blocked (problem statement), hence the +tol slack.
    Returns boolean array, True = occluded.
    """
    shape = np.shape(px)
    blocked = np.zeros(shape, bool)
    dx = T1[0] - px
    dy = T1[1] - py
    dz = H1 - H_CAM
    z0 = np.full(shape, H_CAM)
    for (bx0, bx1, by0, by1, bh) in buildings:
        slabs = ((px, dx, bx0, bx1), (py, dy, by0, by1), (z0, dz, 0.0, bh))
        t_enter = np.zeros(shape)
        t_exit = np.ones(shape)
        ok = np.ones(shape, bool)
        for (p0, d, lo, hi) in slabs:
            par = np.abs(d) < 1e-12
            inside = (p0 >= lo - tol) & (p0 <= hi + tol)
            safe_d = np.where(par, 1.0, d)
            t1 = (lo - p0) / safe_d
            t2 = (hi - p0) / safe_d
            tmin = np.minimum(t1, t2)
            tmax = np.maximum(t1, t2)
            t_enter = np.maximum(t_enter, np.where(par, -np.inf, tmin))
            t_exit = np.minimum(t_exit, np.where(par, np.inf, tmax))
            ok &= ~(par & ~inside)
        hit = ok & (t_enter <= t_exit + tol) & (t_enter <= 1.0 + tol) & (t_exit >= -tol)
        blocked |= hit
    return blocked


def constraint_masks(X, Y, veh_radius=R_VEH, buildings=None):
    """Return (c1, c2, c3, r) boolean/value arrays on the given grid."""
    if buildings is None:
        buildings = BUILDINGS
    c1 = ((X >= veh_radius) & (X <= FIELD - veh_radius) &
          (Y >= veh_radius) & (Y <= FIELD - veh_radius))
    for b in buildings:
        c1 &= dist_to_rect(X, Y, b) >= veh_radius
    r = np.hypot(X - T1[0], Y - T1[1])
    c2 = r >= R_MIN - 1e-9
    c3 = ~los_blocked(X, Y, buildings)
    return c1, c2, c3, r


def make_grid(step, center=False):
    """Node grid (center=False, includes 0 and 100) or cell-center grid."""
    off = step / 2.0 if center else 0.0
    g = np.arange(off, FIELD + (1e-9 if not center else -1e-9), step)
    return np.meshgrid(g, g)


# ----------------------------- 1) region on fine grid -----------------------
STEP = 0.1
X, Y = make_grid(STEP)
c1, c2, c3, rgrid = constraint_masks(X, Y)
mask = c1 & c2 & c3
# official area: midpoint (cell-center) estimator -- each node represents one
# full h x h cell; node counting on the [0,100] lattice overestimates by the
# half-cell boundary band (review issue #4). Both values are reported.
Xm, Ym = make_grid(STEP, center=True)
c1m, c2m, c3m, _ = constraint_masks(Xm, Ym)
area_base = float((c1m & c2m & c3m).sum()) * STEP * STEP      # midpoint
area_node = float(mask.sum()) * STEP * STEP                    # node count

# numerical cross-check of the optimum on the grid
r_feas = np.where(mask, rgrid, np.inf)
idx = np.unravel_index(np.argmin(r_feas), rgrid.shape)
grid_best_r = float(rgrid[idx])
grid_best_pt = (float(X[idx]), float(Y[idx]))

# ----------------------------- 2) optimal arc on r = R_MIN ------------------
NPHI = 200000
phi_deg = np.linspace(0.0, 360.0, NPHI, endpoint=False)
phi_rad = np.radians(phi_deg)
ax_ = T1[0] + R_MIN * np.cos(phi_rad)
ay_ = T1[1] + R_MIN * np.sin(phi_rad)
a1, a2, a3, ar = constraint_masks(ax_, ay_)
arc_feasible = a1 & a3            # a2 holds by construction

def bool_runs(flag):
    """Contiguous True runs (deg intervals) of a periodic boolean sequence.

    Runs are kept within [0, 360]: a run crossing 0 deg is split there.
    """
    n = NPHI
    if flag.all():
        return [(0.0, 360.0)]
    if not flag.any():
        return []
    d = np.diff(np.concatenate([flag.astype(int), flag[:1].astype(int)]))
    starts = (np.where(d == 1)[0] + 1) % n      # index of first True in each run
    ends = np.where(d == -1)[0] % n             # index of last True in each run
    runs = []
    for s, e in zip(starts, ends):
        a, b = phi_deg[s], phi_deg[e]
        if s >= e:                               # run wraps around 0 deg
            runs.append((a, 360.0))
            if b > 1e-9:
                runs.append((0.0, b))
        else:
            runs.append((a, b))
    return runs

feas_runs = bool_runs(arc_feasible)
blocked_runs = bool_runs(~arc_feasible)
feas_frac = float(arc_feasible.mean())

# ----------------------------- 3) tie-breaking on the optimal arc -----------
# margin m(p) = min( dist to every building - R_VEH , distance to field edges )
margins = np.full(NPHI, np.inf)
for b in BUILDINGS:
    margins = np.minimum(margins, dist_to_rect(ax_, ay_, b) - R_VEH)
for lim in (R_VEH, FIELD - R_VEH):
    margins = np.minimum(margins, ax_ - lim if lim == R_VEH else lim - ax_)
    margins = np.minimum(margins, ay_ - lim if lim == R_VEH else lim - ay_)
# note: the two lines above implement min(x-1.5, 98.5-x, y-1.5, 98.5-y)
margins = np.where(arc_feasible, margins, -np.inf)
m_star = float(margins.max())            # TRUE maximum margin on the arc
k_star = int(np.argmax(margins))
m_star_phi = float(phi_deg[k_star])
m_star_point = (float(ax_[k_star]), float(ay_[k_star]))
band = margins >= m_star - 0.05          # tolerance band for tie-break step 1

# ----------------------------- 3b) obstacle-aware travel times --------------
# Vehicles cannot cross buildings; the straight line is only a LOWER bound.
# Shortest feasible path = visibility graph over the 1.5 m inflated building
# rectangles (corners as nodes, mutual visibility as edges) + Dijkstra.


def _seg_hits_rect(p, q, rect):
    """True if segment p-q passes through the OPEN rectangle (interior).

    Slab logic: an axis parallel to the segment either rules out the hit
    (segment outside the slab) or imposes no bound (segment spans the slab).
    """
    (px, py), (qx, qy) = p, q
    dx, dy = qx - px, qy - py
    t_enter, t_exit = 0.0, 1.0
    for p0, d, lo, hi in ((px, dx, rect[0], rect[1]), (py, dy, rect[2], rect[3])):
        if abs(d) < 1e-12:
            if not (lo < p0 < hi):
                return False
            continue
        t1, t2 = (lo - p0) / d, (hi - p0) / d
        t_enter = max(t_enter, min(t1, t2))
        t_exit = min(t_exit, max(t1, t2))
    return t_enter < t_exit - 1e-12 and t_enter < 1.0 and t_exit > 0.0


def path_length(p, q):
    """Straight distance if the path is clear, else shortest detour length."""
    infl = [(b[0] - R_VEH, b[1] + R_VEH, b[2] - R_VEH, b[3] + R_VEH)
            for b in BUILDINGS]
    if not any(_seg_hits_rect(p, q, r) for r in infl):
        return float(np.hypot(q[0] - p[0], q[1] - p[1])), True
    nodes = [tuple(p), tuple(q)]
    for r in infl:
        nodes += [(r[0], r[2]), (r[1], r[2]), (r[0], r[3]), (r[1], r[3])]
    n = len(nodes)
    adj = [[np.inf] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if not any(_seg_hits_rect(nodes[i], nodes[j], r) for r in infl):
                d = float(np.hypot(nodes[i][0] - nodes[j][0],
                                   nodes[i][1] - nodes[j][1]))
                adj[i][j] = adj[j][i] = d
    dist = [np.inf] * n
    dist[0] = 0.0
    seen = [False] * n
    for _ in range(n):
        k = min((d, i) for i, d in enumerate(dist) if not seen[i])[1]
        seen[k] = True
        for j in range(n):
            dist[j] = min(dist[j], dist[k] + adj[k][j])
    return float(dist[1]), False


# tie-break step 2: shortest travel time from the nearest standby vehicle.
# Ranking inside the band uses the obstacle-aware path time (straight time is
# only a lower bound when the direct segment crosses a building): candidates
# are visited in straight-LB order and the exact path time is computed until
# the LB exceeds the incumbent, which makes the minimum exact.
dist_v = np.hypot(ax_[:, None] - VEHICLES[None, :, 0],
                  ay_[:, None] - VEHICLES[None, :, 1])
travel_t = dist_v.min(axis=1) / SPEED
cand = np.where(band, travel_t, np.inf)
band_sorted = np.flatnonzero(band)[np.argsort(cand[band])]
tt_best, best, veh_best = np.inf, None, None
for i in band_sorted:
    if cand[i] >= tt_best:
        break                       # LB already >= incumbent -> exact minimum
    tt_v = [path_length((VEHICLES[j, 0], VEHICLES[j, 1]),
                        (ax_[i], ay_[i]))[0] / SPEED for j in range(5)]
    k = int(np.argmin(tt_v))
    if tt_v[k] < tt_best:
        tt_best, best, veh_best = tt_v[k], i, k
if best is None:                    # defensive fallback (never expected)
    best = np.unravel_index(np.argmin(cand), cand.shape)[0]
# tie-break step 3: lexicographic (deterministic) -- already unique in practice
opt_phi = float(phi_deg[best])
opt_x = float(ax_[best])
opt_y = float(ay_[best])
opt_margin = float(margins[best])
opt_r = float(np.hypot(opt_x - T1[0], opt_y - T1[1]))
opt_elev = float(np.degrees(np.arctan((H1 - H_CAM) / opt_r)))
opt_ttime = float(tt_best) if tt_best < np.inf else float(travel_t[best])
near_v = (veh_best + 1) if veh_best is not None \
    else int(np.argmin(dist_v[best])) + 1


# ----------------------------- 3c) clearance of the chosen station -----------


def seg_box_dist(x0, y0, building, n=4000):
    """Min distance from the LOS segment of station (x0,y0) to one prism."""
    t = np.linspace(0.0, 1.0, n)
    sx = x0 + (T1[0] - x0) * t
    sy = y0 + (T1[1] - y0) * t
    sz = H_CAM + (H1 - H_CAM) * t
    bx0, bx1, by0, by1, bh = building
    dx = np.maximum(np.maximum(bx0 - sx, sx - bx1), 0.0)
    dy = np.maximum(np.maximum(by0 - sy, sy - by1), 0.0)
    dz = np.maximum(np.maximum(0.0 - sz, sz - bh), 0.0)
    return float(np.min(np.sqrt(dx * dx + dy * dy + dz * dz)))


los_clear_opt = min(seg_box_dist(opt_x, opt_y, b) for b in BUILDINGS)

# travel time from every vehicle to the chosen station (for the report)
ttime_all = {f"V{i+1}": float(np.hypot(opt_x - vx, opt_y - vy) / SPEED)
             for i, (vx, vy) in enumerate(VEHICLES)}          # straight (LB)
ttime_all_path = {}
path_clear = {}
for i, (vx, vy) in enumerate(VEHICLES):
    L, clear = path_length((vx, vy), (opt_x, opt_y))
    ttime_all_path[f"V{i+1}"] = L / SPEED
    path_clear[f"V{i+1}"] = clear

# ----------------------------- 4) sensitivity studies -----------------------
# (a) closed-form sensitivity of r* to target altitude H
sens_H = [(H, float((H - H_CAM) / np.tan(np.radians(ELEV_MAX))))
          for H in (30, 35, 40, 45, 50, 55, 60)]
dH = 1.0 / np.tan(np.radians(ELEV_MAX))            # dr*/dH  ~ 0.1763 m/m

# (b) closed-form sensitivity of r* to the gimbal elevation bound
sens_eps = [(e, float((H1 - H_CAM) / np.tan(np.radians(e))))
            for e in (70, 75, 78, 80, 82, 85)]
deps = float(-(H1 - H_CAM) / np.sin(np.radians(ELEV_MAX)) ** 2 * np.pi / 180.0)

# (c) observable-region area vs building B2 height / vehicle radius
STEP_S = 0.25
Xs, Ys = make_grid(STEP_S, center=True)     # midpoint estimator (see above)
r_s = np.hypot(Xs - T1[0], Ys - T1[1])
c2_s = r_s >= R_MIN - 1e-9


def area_scan(buildings, veh_radius):
    cc1 = ((Xs >= veh_radius) & (Xs <= FIELD - veh_radius) &
           (Ys >= veh_radius) & (Ys <= FIELD - veh_radius))
    for b in buildings:
        cc1 &= dist_to_rect(Xs, Ys, b) >= veh_radius
    cc3 = ~los_blocked(Xs, Ys, buildings)
    return float((cc1 & c2_s & cc3).sum()) * STEP_S * STEP_S


sens_b2 = []
for h2 in (20, 24, 28, 32, 36, 40, 45):
    blds = [b if i != 1 else (b[0], b[1], b[2], b[3], h2)
            for i, b in enumerate(BUILDINGS)]
    sens_b2.append((h2, area_scan(blds, R_VEH)))

sens_vr = [(vr, area_scan(BUILDINGS, vr)) for vr in (1.0, 1.5, 2.0, 2.5)]
area_base_scan = area_scan(BUILDINGS, R_VEH)

# (d) alternative metric check: Q2 = (1/r) * cos^2(eps - 45 deg)
# NOTE: Q2 is still strictly decreasing in r on this instance (both factors
# decrease as r grows), so it verifies that r* -- not the full station
# selection -- is invariant within this metric family.
eps_grid = np.degrees(np.arctan((H1 - H_CAM) / np.maximum(rgrid, 1e-9)))
q2 = np.where(mask, (1.0 / np.maximum(rgrid, 1e-9)) *
              np.cos(np.radians(eps_grid - 45.0)) ** 2, -np.inf)
idx2 = np.unravel_index(np.argmax(q2), q2.shape)
alt_pt = (float(X[idx2]), float(Y[idx2]))
alt_r = float(rgrid[idx2])
alt_elev = float(eps_grid[idx2])

# ----------------------------- 5) figures -----------------------------------
COL_FEAS = "#d6e8fa"     # feasible region fill
COL_INFEAS = "#f2f2f2"   # infeasible fill
COL_NEW = "#f4a582"      # region excluded by the constraint just added
COL_BLD = "#b3b3b3"      # building fill
COL_EDGE = "#4d4d4d"
COL_TGT = "#d62728"      # target marker
COL_VEH = "#1f77b4"      # vehicle marker
COL_ARC_OK = "#2ca02c"   # feasible optimal arc
COL_ARC_NO = "#d62728"   # blocked optimal arc
COL_OPT = "#111111"      # chosen station


def _clean_axes(ax):
    """Numbers-only figure content: no axis titles, no legends, no annotations."""
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(labelsize=10)


def draw_field(ax, buildings=None, alpha=1.0):
    if buildings is None:
        buildings = BUILDINGS
    for (x0, x1, y0, y1, h) in buildings:
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor=COL_BLD,
                               edgecolor=COL_EDGE, linewidth=0.8, alpha=alpha))


def save(fig, name):
    fig.savefig(os.path.join(FIG_DIR, name + ".svg"), bbox_inches="tight")
    fig.savefig(os.path.join(FIG_DIR, name + ".png"), dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("saved", name)


# --- Fig 1: observable region over the whole field --------------------------
fig, ax = plt.subplots(figsize=(6.4, 6.0))
ax.imshow(mask, extent=(0, 100, 0, 100), origin="lower",
          cmap=matplotlib.colors.ListedColormap([COL_INFEAS, COL_FEAS]),
          interpolation="nearest", aspect="equal")
draw_field(ax)
ax.plot([O_POS[0]], [O_POS[1]], marker="o", ms=5, color="k")
ax.plot(T1[0], T1[1], marker="*", ms=14, color=COL_TGT)
ax.plot(VEHICLES[:, 0], VEHICLES[:, 1], linestyle="none", marker="s",
        ms=6, mfc=COL_VEH, mec="k", mew=0.5)
ax.add_patch(Rectangle((0, 0), 100, 100, fill=False, ec="k", lw=1.2))
ax.plot([O_POS[0], T1[0]], [O_POS[1], T1[1]], linestyle="--", color=COL_TGT, lw=1.0)
ax.set_xlim(0, 100); ax.set_ylim(0, 100)
ax.set_xticks(range(0, 101, 20)); ax.set_yticks(range(0, 101, 20))
_clean_axes(ax)
save(fig, "fig1_observable_region")

# --- Fig 2: three constraint layers ------------------------------------------
# Each panel highlights, in a distinct colour, exactly the region removed by the
# constraint added at that step, so the three panels remain distinguishable.
fig, axs = plt.subplots(1, 3, figsize=(13.4, 5.0))
stages = [(c1, "(a) C1: vehicle geometry"),
          (c1 & c2, "(b) C1 + C2: elevation bound"),
          (mask, "(c) C1 + C2 + C3: line of sight")]
prev = np.ones_like(c1, dtype=bool)
for k, (m, lbl) in enumerate(stages):
    newly = prev & ~m
    cat = np.zeros(c1.shape, dtype=int)
    cat[~prev] = 1          # already infeasible before this step
    cat[m] = 0              # feasible after this step
    cat[newly] = 2          # removed by the constraint added at this step
    axs[k].imshow(cat, extent=(0, 100, 0, 100), origin="lower",
                  cmap=matplotlib.colors.ListedColormap(
                      [COL_FEAS, COL_INFEAS, COL_NEW]),
                  interpolation="nearest", aspect="equal", vmin=0, vmax=2)
    draw_field(axs[k])
    axs[k].plot(T1[0], T1[1], marker="*", ms=12, color=COL_TGT)
    axs[k].add_patch(Rectangle((0, 0), 100, 100, fill=False, ec="k", lw=1.0))
    axs[k].set_xlim(0, 100); axs[k].set_ylim(0, 100)
    axs[k].set_xticks(range(0, 101, 20)); axs[k].set_yticks(range(0, 101, 20))
    axs[k].set_title(f"{lbl}\n" + r"$\Delta A$ = "
                     f"{newly.sum() * STEP * STEP:.1f} m$^2$", fontsize=10)
    _clean_axes(axs[k])
    prev = m
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
fig.legend(handles=[
    Patch(facecolor=COL_FEAS, edgecolor=COL_EDGE, label="feasible"),
    Patch(facecolor=COL_NEW, edgecolor=COL_EDGE,
          label="excluded by the added constraint"),
    Patch(facecolor=COL_INFEAS, edgecolor=COL_EDGE,
          label="already infeasible"),
    Patch(facecolor=COL_BLD, edgecolor=COL_EDGE, label="building"),
    Line2D([], [], marker="*", color=COL_TGT, linestyle="none",
           ms=11, label="target T1")],
    loc="lower center", ncol=5, frameon=False, fontsize=9)
fig.subplots_adjust(wspace=0.12, bottom=0.18)
save(fig, "fig2_constraint_layers")

# --- Fig 3: zoom on the optimal circle + margin profile ----------------------
fig, (axm, axp) = plt.subplots(1, 2, figsize=(12.4, 5.6),
                               gridspec_kw={"width_ratios": [1.15, 1.0]})
x0v, x1v, y0v, y1v = 70.0, 100.0, 55.0, 85.0
col_sel = np.where((X[0, :] >= x0v) & (X[0, :] <= x1v))[0]
row_sel = np.where((Y[:, 0] >= y0v) & (Y[:, 0] <= y1v))[0]
sub = mask[np.ix_(row_sel, col_sel)]
axm.imshow(sub, extent=(x0v, x1v, y0v, y1v), origin="lower",
           cmap=matplotlib.colors.ListedColormap([COL_INFEAS, COL_FEAS]),
           interpolation="nearest", aspect="equal", alpha=0.9)
draw_field(axm)
th = np.linspace(0, 2 * np.pi, 720)
cx = T1[0] + R_MIN * np.cos(th)
cy = T1[1] + R_MIN * np.sin(th)
okc = arc_feasible[np.clip((np.degrees(th) % 360 * NPHI // 360).astype(int), 0, NPHI - 1)]
# NaN at gaps so the polyline never connects across a blocked arc
cxg = np.where(okc, cx, np.nan)
cyg = np.where(okc, cy, np.nan)
cxr = np.where(~okc, cx, np.nan)
cyr = np.where(~okc, cy, np.nan)
axm.plot(cxg, cyg, color=COL_ARC_OK, lw=3.0, solid_capstyle="round", zorder=6)
axm.plot(cxr, cyr, color=COL_ARC_NO, lw=3.0, solid_capstyle="round", zorder=6)
axm.plot([T1[0], opt_x], [T1[1], opt_y], linestyle=":", color="k", lw=1.0, zorder=5)
axm.plot(opt_x, opt_y, marker="p", ms=12, mfc=COL_OPT, mec="w", mew=1.0, zorder=7)
axm.plot(T1[0], T1[1], marker="*", ms=15, color=COL_TGT, zorder=7)
axm.plot(VEHICLES[3, 0], VEHICLES[3, 1], linestyle="none", marker="s",
         ms=7, mfc=COL_VEH, mec="k", mew=0.5, zorder=7)
axm.add_patch(Rectangle((0, 0), 100, 100, fill=False, ec="k", lw=1.0))
axm.set_xlim(x0v, x1v); axm.set_ylim(y0v, y1v)
axm.set_xticks(range(70, 101, 10)); axm.set_yticks(range(55, 86, 10))
axm.set_aspect("equal")
axm.grid(False)
_clean_axes(axm)

# margin profile on the feasible arc, zoomed on the near-optimal lobe: a local
# view avoids both the blocked-arc shading and the spike-like appearance that a
# 0-360 deg plot with a clipped y-range would produce
mrel = margins - m_star
sel = (phi_deg >= 52.0) & (phi_deg <= 62.0)
axp.plot(phi_deg[sel], mrel[sel], color=COL_ARC_OK, lw=1.8)
axp.axhspan(-0.05, 0.0, color="#d6e8fa", alpha=0.8, zorder=0)
axp.axhline(0.0, color=COL_EDGE, lw=0.6, ls=":")
axp.plot([m_star_phi], [0.0], marker="o", ms=11, mfc="none",
         mec=COL_TGT, mew=1.6, zorder=6)
axp.plot([opt_phi], [opt_margin - m_star], marker="p", ms=9, mfc=COL_OPT,
         mec="w", mew=1.0, zorder=7)
axp.set_xlim(52.0, 62.0)
axp.set_ylim(-0.42, 0.05)
axp.set_xticks(range(52, 63, 2))
axp.set_yticks([-0.4, -0.3, -0.2, -0.1, 0.0])
axp.set_xlabel(" ")
axp.tick_params(labelsize=10)
from matplotlib.patches import Patch as _Patch
from matplotlib.lines import Line2D as _Line2D
axp.legend(handles=[
    _Line2D([], [], color=COL_ARC_OK, lw=1.8,
            label=r"$(m-m^\ast)$ on feasible arc"),
    _Patch(facecolor="#d6e8fa", edgecolor="none",
           label="0.05 m tie band")],
    loc="lower left", frameon=False, fontsize=9)
for s in ("top", "right"):
    axp.spines[s].set_visible(False)
save(fig, "fig3_optimal_arc_zoom")

# --- Fig 4: closed-form sensitivity of r* ------------------------------------
fig, (a4a, a4b) = plt.subplots(1, 2, figsize=(11.0, 4.4))
Hs = np.linspace(30, 60, 301)
a4a.plot(Hs, (Hs - H_CAM) / np.tan(np.radians(ELEV_MAX)), color=COL_VEH, lw=1.8)
a4a.plot([45.0], [R_MIN], marker="o", ms=7, mfc=COL_TGT, mec="k", mew=0.6)
a4a.set_xticks(range(30, 61, 10))
a4a.set_yticks(range(2, 11, 2))
_clean_axes(a4a)

es = np.linspace(70, 85, 301)
a4b.plot(es, (H1 - H_CAM) / np.tan(np.radians(es)), color=COL_VEH, lw=1.8)
a4b.plot([80.0], [R_MIN], marker="o", ms=7, mfc=COL_TGT, mec="k", mew=0.6)
a4b.set_xticks(range(70, 86, 5))
_clean_axes(a4b)
save(fig, "fig4_sensitivity_rstar")

# --- Fig 5: region-area sensitivity ------------------------------------------
fig, (a5a, a5b) = plt.subplots(1, 2, figsize=(11.0, 4.4))
h2v = [v[0] for v in sens_b2]
a2v = [v[1] for v in sens_b2]
a5a.plot(h2v, a2v, color=COL_VEH, lw=1.8, marker="o", ms=4)
a5a.plot([28.0], [area_base_scan], marker="o", ms=8, mfc=COL_TGT, mec="k", mew=0.6)
a5a.set_xticks(range(20, 46, 5))
_clean_axes(a5a)

rvv = [v[0] for v in sens_vr]
avv = [v[1] for v in sens_vr]
a5b.plot(rvv, avv, color=COL_VEH, lw=1.8, marker="o", ms=4)
a5b.plot([1.5], [area_base_scan], marker="o", ms=8, mfc=COL_TGT, mec="k", mew=0.6)
_clean_axes(a5b)
save(fig, "fig5_sensitivity_area")

# --- Fig 6: 3D LOS schematic --------------------------------------------------
fig = plt.figure(figsize=(7.6, 6.0))
ax3 = fig.add_subplot(111, projection="3d")
for (bx0, bx1, by0, by1, bh) in BUILDINGS:
    ax3.bar3d(bx0, by0, 0, bx1 - bx0, by1 - by0, bh,
              color=COL_BLD, edgecolor=COL_EDGE, alpha=0.55, shade=True)
gx, gy = np.meshgrid([0, 100], [0, 100])
ax3.plot_surface(gx, gy, np.zeros_like(gx), color="#eef3f8", alpha=0.6, zorder=0)
ax3.plot([opt_x, T1[0]], [opt_y, T1[1]], [H_CAM, H1], color=COL_TGT, lw=2.0)
ax3.scatter([opt_x], [opt_y], [H_CAM], color=COL_OPT, s=40, depthshade=False)
ax3.scatter([T1[0]], [T1[1]], [H1], color=COL_TGT, marker="*", s=120,
            depthshade=False)
ax3.set_xlim(0, 100); ax3.set_ylim(0, 100); ax3.set_zlim(0, 60)
ax3.set_xticks([0, 50, 100]); ax3.set_yticks([0, 50, 100]); ax3.set_zticks([0, 20, 40, 60])
ax3.set_xlabel("x (m)", fontsize=10, labelpad=6)
ax3.set_ylabel("y (m)", fontsize=10, labelpad=6)
ax3.set_zlabel("z (m)", fontsize=10, labelpad=4)
ax3.tick_params(labelsize=8)
ax3.xaxis.set_tick_params(pad=8)
ax3.yaxis.set_tick_params(pad=8)
ax3.zaxis.set_tick_params(pad=2)
ax3.view_init(elev=20, azim=-52)
save(fig, "fig6_los_3d")

# ----------------------------- 6) results dump ------------------------------
results = {
    "target": {"theta": THETA1, "R": R1, "H": H1,
               "xy": [float(T1[0]), float(T1[1])]},
    "constants": {"R_VEH": R_VEH, "H_CAM": H_CAM, "SPEED": SPEED,
                  "ELEV_MAX": ELEV_MAX, "ELEV_MIN": ELEV_MIN},
    "r_min_closed_form": float(R_MIN),
    "q_star": float(1.0 / R_MIN),
    "grid": {"step": STEP, "area_m2": area_base,
             "area_estimator": "cell-center (midpoint), h = 0.1 m",
             "area_node_count_m2": area_node,
             "best_r": grid_best_r, "best_point": grid_best_pt,
             "r_diff_vs_analytic": float(grid_best_r - R_MIN)},
    "arc": {"n_samples": NPHI,
            "feasible_fraction": feas_frac,
            "feasible_runs_deg": feas_runs,
            "blocked_runs_deg": blocked_runs,
            "blocked_total_deg": float(sum(b - a for a, b in blocked_runs)),
            "m_star_margin_m": m_star,
            "m_star_phi_deg": m_star_phi,
            "m_star_point": list(m_star_point),
            "band_lower_m": float(m_star - 0.05)},
    "optimal_station": {"phi_deg": opt_phi, "x": opt_x, "y": opt_y,
                        "r": opt_r, "elevation_deg": opt_elev,
                        "Q": float(1.0 / opt_r),
                        "margin_m": opt_margin,
                        "margin_note": "margin of the SELECTED station "
                            "(band m >= m* - 0.05), not the arc maximum",
                        "los_clearance_m": los_clear_opt,
                        "nearest_vehicle": f"V{near_v}",
                        "travel_time_s": opt_ttime,
                        "travel_time_all": ttime_all,
                        "travel_time_all_path": ttime_all_path,
                        "path_straight_clear": path_clear},
    "sensitivity": {
        "dr_dH": float(dH),
        "dr_deps_deg": deps,
        "r_vs_H": sens_H,
        "r_vs_eps": sens_eps,
        "area_base_m2": area_base_scan,
        "area_vs_B2_height": sens_b2,
        "area_vs_vehicle_radius": sens_vr,
        "alt_metric": {"Q2_station": alt_pt, "r": alt_r,
                       "elevation_deg": alt_elev},
    },
}
with open(os.path.join(RES_DIR, "q1_results.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

lines = [
    "==== Problem 1 numeric summary ====",
    f"T1 horizontal projection : ({T1[0]:.4f}, {T1[1]:.4f})  H = {H1} m",
    f"closed-form r* = (H-Hcam)/tan(80deg) = {R_MIN:.4f} m   Q* = {1/R_MIN:.4f} /m",
    f"grid({STEP} m): area (midpoint) = {area_base:.1f} m^2 "
    f"(node-count {area_node:.1f} m^2) ; best feasible r = "
    f"{grid_best_r:.4f} m at {grid_best_pt} (diff {grid_best_r - R_MIN:+.4f} m)",
    f"optimal arc: feasible {feas_frac * 100:.1f}% of the circle",
    f"  blocked runs (deg): {[(round(float(a), 2), round(float(b), 2)) for a, b in blocked_runs]}",
    f"  feasible runs (deg): {[(round(float(a), 2), round(float(b), 2)) for a, b in feas_runs]}",
    f"  TRUE max margin m* = {m_star:.4f} m at phi = {m_star_phi:.3f} deg "
    f"(point {m_star_point}, B2-buffer and east-boundary balanced there)",
    f"chosen station: phi = {opt_phi:.3f} deg  p* = ({opt_x:.4f}, {opt_y:.4f})",
    f"  r = {opt_r:.4f} m   elevation = {opt_elev:.3f} deg   Q = {1/opt_r:.4f} /m",
    f"  selected margin = {opt_margin:.4f} m (in band [m*-0.05, m*] = "
    f"[{m_star-0.05:.4f}, {m_star:.4f}])   LOS clearance = {los_clear_opt:.2f} m",
    f"  nearest vehicle V{near_v}  travel time = {opt_ttime:.2f} s "
    f"(straight path clear: {path_clear[f'V{near_v}']})",
    f"  straight-line travel (LB) / feasible-path travel from all vehicles:",
    "    " + ", ".join(f"{k}: {v:.2f}/{ttime_all_path[k]:.2f}s" for k, v in ttime_all.items()),
    f"sensitivity: dr*/dH = {dH:.4f} m/m ; dr*/d(eps_max) = {deps:.4f} m/deg",
    f"area scan base (midpoint 0.25 m) = {area_base_scan:.1f} m^2",
    f"area vs B2 height: {[(h, round(a, 1)) for h, a in sens_b2]}",
    f"area vs vehicle radius: {[(v, round(a, 1)) for v, a in sens_vr]}",
    f"alt metric Q2: station {alt_pt}, r = {alt_r:.3f} m, elev = {alt_elev:.2f} deg "
    f"(only verifies r* invariance: Q2 is still decreasing in r)",
]
summary = "\n".join(lines)
with open(os.path.join(RES_DIR, "q1_summary.txt"), "w", encoding="utf-8") as f:
    f.write(summary + "\n")
print(summary)
