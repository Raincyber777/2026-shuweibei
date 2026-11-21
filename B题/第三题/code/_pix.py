# -*- coding: utf-8 -*-
import sys

import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
im = np.asarray(Image.open(
    r"e:\2026数维杯\2026-shuweibei\B题\第三题\figures\fig1_sigma_components.png"
).convert("L"))
h, w = im.shape
print("size:", w, "x", h)
# find the axes box: long dark horizontal runs
dark = im < 100
rows = dark.sum(axis=1)
cols = dark.sum(axis=0)
top_candidates = [(r, rows[r]) for r in range(h) if rows[r] > w * 0.5]
print("dark-heavy rows (row, count):", top_candidates[:6])
col_candidates = [(c, cols[c]) for c in range(w) if cols[c] > h * 0.5]
print("dark-heavy cols (col, count):", col_candidates[:6])
