# -*- coding: utf-8 -*-
import io

p = "make_fig_4_1_to_4_7.py"
t = io.open(p, encoding="utf-8").read()

old = 'axg.set_ylim(-0.6, 5.6)\naxg.set_yticks(range(5))'
new = 'axg.set_ylim(-0.6, 5.35)\naxg.set_yticks(range(5))'
assert old in t, "ylim"
t = t.replace(old, new)

old = 'axg.annotate(a, xy=(sv, 4.72), fontsize=6, ha="center",\n                 annotation_clip=False)'
new = 'axg.annotate(a, xy=(sv, 4.92), fontsize=6, ha="center")'
assert old in t, "annotate"
t = t.replace(old, new)

old = '''], loc="upper left", bbox_to_anchor=(0.005, 0.99), fontsize=6, '
       'ncol=5, framealpha=0.92, columnspacing=1.0, handlelength=1.3, '
       'borderaxespad=0)
panel(axg, "(a) Optimized vehicle timeline")'''
new = '''], loc="upper center", bbox_to_anchor=(0.5, -0.20), fontsize=6.5,
    ncol=5, frameon=False, columnspacing=1.2, handlelength=1.3)
panel(axg, "(a) Optimized vehicle timeline")'''
assert old in t, "legend"
t = t.replace(old, new)

io.open(p, "w", encoding="utf-8").write(t)
print("GANTT_LEGEND_FIXED")
