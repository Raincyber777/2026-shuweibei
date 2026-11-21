# -*- coding: utf-8 -*-
import hashlib
import os
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"e:\2026数维杯\2026-shuweibei\B题\第一题")
FIGS = ["fig1_observable_region", "fig2_constraint_layers",
        "fig3_optimal_arc_zoom", "fig4_sensitivity_rstar",
        "fig5_sensitivity_area", "fig6_los_3d"]
z = zipfile.ZipFile("第一题_图集.pptx")
pngs = sorted([i for i in z.infolist()
               if i.filename.startswith("ppt/media/") and
               i.filename.endswith(".png")],
              key=lambda x: int("".join(ch for ch in x.filename if ch.isdigit())))
svgs = sorted([i for i in z.infolist() if i.filename.endswith(".svg")],
              key=lambda x: int("".join(ch for ch in x.filename if ch.isdigit())))
print(f"PNG parts: {len(pngs)}  SVG parts: {len(svgs)}")
all_ok = True
for k, m in enumerate(pngs):
    local = os.path.join("figures", FIGS[k] + ".png")
    h_pptx = hashlib.md5(z.read(m.filename)).hexdigest()
    h_local = hashlib.md5(open(local, "rb").read()).hexdigest()
    same = h_pptx == h_local
    all_ok &= same
    print(f"image{k+1}.png <-> {FIGS[k]}.png: pptx={m.file_size}B "
          f"local={os.path.getsize(local)}B  {'SAME' if same else 'DIFF'}")
svg_ok = True
for k, m in enumerate(svgs):
    local = os.path.join("figures", FIGS[k] + ".svg")
    h_pptx = hashlib.md5(z.read(m.filename)).hexdigest()
    h_local = hashlib.md5(open(local, "rb").read()).hexdigest()
    same = h_pptx == h_local
    svg_ok &= same
    print(f"svg{k+1} <-> {FIGS[k]}.svg: {'SAME' if same else 'DIFF'}")
print("PNG EMBEDDED == figures/:", all_ok, "  SVG EMBEDDED == figures/:", svg_ok)
