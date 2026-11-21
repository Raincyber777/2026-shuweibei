# -*- coding: utf-8 -*-
import io

p = "q1_solve.py"
t = io.open(p, encoding="utf-8").read()

old1 = ('ax.set_xlim(0, 100); ax.set_ylim(0, 100)\n'
        'ax.set_xticks(range(0, 101, 20)); ax.set_yticks(range(0, 101, 20))\n'
        '_clean_axes(ax)\n'
        'save(fig, "fig1_observable_region")')
new1 = ('ax.set_xlim(0, 100); ax.set_ylim(0, 100)\n'
        'ax.set_xticks(range(0, 101, 20)); ax.set_yticks(range(0, 101, 20))\n'
        'ax.grid(False)\n'
        '_clean_axes(ax)\n'
        'save(fig, "fig1_observable_region")')
assert old1 in t, "fig1"
t = t.replace(old1, new1)

old2 = ('                     f"{newly.sum() * STEP * STEP:.1f} m$^2$", fontsize=10)\n'
        '    _clean_axes(axs[k])')
new2 = ('                     f"{newly.sum() * STEP * STEP:.1f} m$^2$", fontsize=10)\n'
        '    _clean_axes(axs[k])\n'
        '    axs[k].grid(False)')
assert old2 in t, "fig2"
t = t.replace(old2, new2)

old3 = 'axm.set_xticks(range(70, 101, 10)); axm.set_yticks(range(55, 86, 10))\n_clean_axes(axm)'
new3 = ('axm.set_xticks(range(70, 101, 10)); axm.set_yticks(range(55, 86, 10))\n'
        'axm.grid(False)\n_clean_axes(axm)')
assert old3 in t, "fig3"
t = t.replace(old3, new3)

io.open(p, "w", encoding="utf-8").write(t)
print("Q1_GRID_OFF_OK")
