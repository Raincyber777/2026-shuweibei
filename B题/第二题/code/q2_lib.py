# -*- coding: utf-8 -*-
"""Shared library for Problem 2 (generalizes the Problem-1 helpers).

Everything here is parameterized by the target, because Q2 needs the
observable regions of T1, T2, T3 (not only T1).

Contents
--------
* problem constants (field, buildings, vehicles, camera, alerts)
* dist_to_rect          : point-to-rectangle distance (vectorized)
* los_blocked           : 3D segment-vs-prism slab test, tangency = blocked
* region_masks          : C1 / C2 / C3 masks + range field for one target
* build_region          : fine-grid observable region of one alert
* circle_arc_runs       : feasible/blocked runs on a circle (periodic)
* slew_time             : gimbal slew / reset duration for one pointing
* nelder_mead           : small dependency-free Nelder-Mead (for refine)
* wrap180               : wrap angle to (-180, 180]
"""
import numpy as np

# ----------------------------- problem constants ----------------------------
FIELD = 100.0
O_POS = (50.0, 50.0)
R_VEH = 1.5
H_CAM = 2.0
SPEED = 3.0                # m/s
OMEGA = 30.0               # deg/s (pan and tilt, simultaneous)
ELEV_MIN, ELEV_MAX = -10.0, 80.0
SIGMA_AZ = 1.0             # deg, azimuth measurement error std (Q2(1))
TRAVEL_LIMIT_S = 30.0      # Q2(1) travel-time deadline
TRAVEL_LIMIT_M = TRAVEL_LIMIT_S * SPEED

BUILDINGS = [
    (22.0, 34.0, 16.0, 26.0, 20.0),   # B1
    (63.0, 79.0, 59.0, 71.0, 28.0),   # B2
    (10.0, 24.0, 65.0, 76.0, 12.0),   # B3
    (72.0, 86.0, 22.0, 34.0, 24.0),   # B4
    (41.0, 51.0, 38.0, 46.0, 32.0),   # B5
]

VEHICLES = np.array([[15.0, 14.0], [88.0, 10.0], [14.0, 86.0],
                     [88.0, 68.0], [50.0, 93.0]])          # V1..V5

# base alerts (theta deg, R m, H m) -> horizontal projection T' and altitude
ALERTS = {
    "T1": (30.0, 40.0, 45.0),
    "T2": (150.0, 45.0, 35.0),
    "T3": (285.0, 38.0, 55.0),
}


def target_xy(theta_deg, R):
    return np.array([50.0 + R * np.cos(np.radians(theta_deg)),
                     50.0 + R * np.sin(np.radians(theta_deg))])


TARGETS = {k: target_xy(v[0], v[1]) for k, v in ALERTS.items()}
TARGET_H = {k: v[2] for k, v in ALERTS.items()}
# closed-form minimal horizontal range imposed by the elevation bound
R_MIN_GEO = {k: (v[2] - H_CAM) / np.tan(np.radians(ELEV_MAX))
             for k, v in ALERTS.items()}


# ----------------------------- geometry -------------------------------------
def dist_to_rect(px, py, rect):
    """Distance from points (px, py) to axis-aligned rectangle (x0,x1,y0,y1)."""
    x0, x1, y0, y1 = rect[0], rect[1], rect[2], rect[3]
    dx = np.maximum(np.maximum(x0 - px, px - x1), 0.0)
    dy = np.maximum(np.maximum(y0 - py, py - y1), 0.0)
    return np.hypot(dx, dy)


def los_blocked_h(px, py, tgt, h_tgt, buildings=None, tol=1e-9):
    """Same as los_blocked but with the target altitude given explicitly."""
    if buildings is None:
        buildings = BUILDINGS
    shape = np.shape(px)
    blocked = np.zeros(shape, bool)
    dx = tgt[0] - px
    dy = tgt[1] - py
    dz = h_tgt - H_CAM
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


def region_masks(X, Y, tgt, h_tgt, r_min_geo, veh_radius=R_VEH, buildings=None):
    """C1 (geometry) / C2 (elevation) / C3 (LOS) masks and the range field."""
    if buildings is None:
        buildings = BUILDINGS
    c1 = ((X >= veh_radius) & (X <= FIELD - veh_radius) &
          (Y >= veh_radius) & (Y <= FIELD - veh_radius))
    for b in buildings:
        c1 &= dist_to_rect(X, Y, b) >= veh_radius
    r = np.hypot(X - tgt[0], Y - tgt[1])
    c2 = r >= r_min_geo - 1e-9
    c3 = ~los_blocked_h(X, Y, tgt, h_tgt, buildings)
    return c1, c2, c3, r


def make_grid(step, x0=0.0, x1=FIELD, y0=0.0, y1=FIELD):
    gx = np.arange(x0, x1 + 1e-9, step)
    gy = np.arange(y0, y1 + 1e-9, step)
    return np.meshgrid(gx, gy)


def build_region(tgt_key, step=0.1):
    """Fine-grid observable region of one alert.

    Returns dict with grid axes, mask, range field, area.
    """
    tgt, h = TARGETS[tgt_key], TARGET_H[tgt_key]
    X, Y = make_grid(step)
    c1, c2, c3, r = region_masks(X, Y, tgt, h, R_MIN_GEO[tgt_key])
    mask = c1 & c2 & c3
    return {"X": X, "Y": Y, "mask": mask, "r": r,
            "area": float(mask.sum()) * step * step, "step": step}


def circle_samples(tgt, radius, n=200000):
    phi = np.linspace(0.0, 360.0, n, endpoint=False)
    rad = np.radians(phi)
    return phi, tgt[0] + radius * np.cos(rad), tgt[1] + radius * np.sin(rad)


def bool_runs(flag, phi_deg):
    """Contiguous True runs (deg) of a periodic boolean sequence."""
    n = len(flag)
    if flag.all():
        return [(0.0, 360.0)]
    if not flag.any():
        return []
    d = np.diff(np.concatenate([flag.astype(int), flag[:1].astype(int)]))
    starts = (np.where(d == 1)[0] + 1) % n
    ends = np.where(d == -1)[0] % n
    runs = []
    for s, e in zip(starts, ends):
        a, b = phi_deg[s], phi_deg[e]
        runs.append((a, b + 360.0) if s >= e else (a, b))
    return runs


# ----------------------------- timing ---------------------------------------
def wrap180(a_deg):
    """Wrap angle(s) into (-180, 180]."""
    return ((np.asarray(a_deg) + 180.0) % 360.0) - 180.0


def pointing_angles(station, tgt, h_tgt):
    """Azimuth (deg, CCW from east, in (-180,180]) and elevation (deg)."""
    dx = tgt[0] - station[0]
    dy = tgt[1] - station[1]
    r = np.hypot(dx, dy)
    az = np.degrees(np.arctan2(dy, dx))
    az = wrap180(az)
    el = np.degrees(np.arctan((h_tgt - H_CAM) / max(r, 1e-12)))
    return float(np.asarray(az)), float(np.asarray(el)), float(r)


def slew_time(az_deg, el_deg):
    """Slew (or reset) duration: pan 0->az and tilt 0->el run simultaneously."""
    return max(abs(wrap180(az_deg)), abs(el_deg)) / OMEGA


def obs_window(start, az_deg, el_deg, obs_len=5.0):
    """Return (start, end, reset_done) of one observation task."""
    end = start + obs_len
    return start, end, end + slew_time(az_deg, el_deg)


# ----------------------------- tiny optimizer -------------------------------
def nelder_mead(f, x0, step=0.5, tol=1e-6, max_iter=400):
    """Dependency-free Nelder-Mead on R^n. f returns scalar (to minimize)."""
    x0 = np.asarray(x0, float)
    n = len(x0)
    simp = [x0.copy()]
    for i in range(n):
        p = x0.copy()
        p[i] += step
        simp.append(p)
    simp = np.array(simp)
    vals = np.array([f(p) for p in simp])
    for _ in range(max_iter):
        order = np.argsort(vals)
        simp, vals = simp[order], vals[order]
        if np.max(np.abs(simp[1:] - simp[0])) < tol and \
           np.max(np.abs(vals[1:] - vals[0])) < tol:
            break
        cen = simp[:-1].mean(axis=0)
        xr = cen + (cen - simp[-1])            # reflection
        fr = f(xr)
        if fr < vals[0]:
            xe = cen + 2.0 * (cen - simp[-1])  # expansion
            fe = f(xe)
            simp[-1], vals[-1] = (xe, fe) if fe < fr else (xr, fr)
        elif fr < vals[-2]:
            simp[-1], vals[-1] = xr, fr
        else:
            xc = cen + 0.5 * (simp[-1] - cen)  # contraction
            fc = f(xc)
            if fc < vals[-1]:
                simp[-1], vals[-1] = xc, fc
            else:                               # shrink
                for i in range(1, n + 1):
                    simp[i] = simp[0] + 0.5 * (simp[i] - simp[0])
                    vals[i] = f(simp[i])
    k = int(np.argmin(vals))
    return simp[k], float(vals[k])
