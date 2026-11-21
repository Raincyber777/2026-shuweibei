# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scienceplots

plt.style.use(["science", "ieee", "no-latex", "grid"])
fig, ax = plt.subplots()
ax.plot([1, 2], [1, 2])
ax.spines["top"].set_visible(False)
fig.canvas.draw()
print("top visible:", ax.spines["top"].get_visible())
print("rcParams spines.top:", matplotlib.rcParams["axes.spines.top"])
