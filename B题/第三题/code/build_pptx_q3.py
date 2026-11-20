# -*- coding: utf-8 -*-
"""Problem-3 figure album PPTX (same SVG-injection technique as Problems 1-2)."""
import os
import sys

from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Emu
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.opc.package import Part
from pptx.opc.packuri import PackURI

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo-relative
FIG_DIR = os.path.join(BASE, "figures")
OUT = os.path.join(BASE, "第三题_图集.pptx")

R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
SVG_NS = "http://schemas.microsoft.com/office/drawing/2016/SVG/main"
SVG_EXT_URI = "{96DAC541-7B7A-43D3-8B79-37D633B846F1}"
A_TAG = "{http://schemas.openxmlformats.org/drawingml/2006/main}%s"

FIGS = [
    ("fig1_sigma_components",
     "Fig. 1  Bearing-deviation standard deviation vs. cumulative travel distance s. "
     "Blue = localization contribution sigma_loc(s) = (0.3+0.02s)/40 * 180/pi; orange "
     "dotted = gimbal-only floor (0.8^2+0.6^2)^0.5 = 1.0 deg; red = total sigma_psi(s); "
     "green dashed = requirement-implied ceiling 5/z_0.975 = 2.5511 deg; vertical line "
     "and green marker = s_max = 66.92 m where the red curve meets the ceiling."),
    ("fig2_probability_curve",
     "Fig. 2  P(|dpsi| <= 5 deg) vs. s: analytic normal model (red curve) and "
     "1,000,000-sample Monte-Carlo points (blue, exact atan2 pointing, no "
     "linearization); green dashed = 0.95 requirement; vertical line = s_max = "
     "66.92 m. Empirical and analytic curves agree to |dP| <= 3e-4."),
    ("fig3_ab_region",
     "Fig. 3  Feasible region of the localization model sigma(s) = a + b*s at the "
     "80 m requirement (shaded, both nonnegative, a + 80 b <= 1.6384 m); solid "
     "curves = iso-confidence boundaries for 0.90 / 0.95 / 0.98 / 0.99; the red "
     "square is the nominal pair (a, b) = (0.3, 0.02), which lies OUTSIDE the "
     "0.95 region; green dots mark the axis intercepts a_max = 1.6384 m and "
     "b_max = 0.02048 m per m."),
    ("fig4_variance_shares",
     "Fig. 4  Variance decomposition of dpsi (stacked): blue = localization, orange "
     "= gimbal zero-offset, red = gimbal control; black curve = total variance. "
     "Vertical lines: crossover at s = 19.91 m (localization variance exceeds the "
     "total gimbal variance) and s_max = 66.92 m. Shares at s = 80: 88.1% / 7.6% / "
     "4.3%."),
    ("fig5_mc_validation",
     "Fig. 5  Monte-Carlo validation at s = 80 m: histogram of 1e6 simulated dpsi "
     "samples (exact atan2 pointing geometry) vs. the analytic normal density "
     "N(0, 2.8995^2) (red); green dashed = the +/-5 deg requirement limits. The "
     "close fit (max quantile gap 0.025 deg, bias 1.5e-3 deg) validates the "
     "linearized propagation."),
    ("fig6_sensitivity_smax",
     "Fig. 6  Left: s_max vs. the vehicle-target standoff distance d (linear, slope "
     "2.048 m per m; nominal d = 40 m marked, s_max = 66.92 m). Right: s_max vs. the "
     "required confidence level (two-sided): 85.2 m at 0.90, 66.9 m at 0.95, 51.4 m "
     "at 0.98, 43.1 m at 0.99."),
]

_svg_counter = [0]


def png_aspect(path):
    from PIL import Image
    with Image.open(path) as im:
        return im.size[0] / im.size[1]


def inject_svg(slide, png_path, svg_path, left, top, width, height):
    pic = slide.shapes.add_picture(png_path, left, top, width, height)
    svg_blob = open(svg_path, "rb").read()
    package = slide.part.package
    _svg_counter[0] += 1
    partname = PackURI("/ppt/media/svgimage%d.svg" % _svg_counter[0])
    part = Part(partname, "image/svg+xml", package, svg_blob)
    rId = slide.part.relate_to(part, RT.IMAGE)
    blip = pic._element.blipFill.blip
    ext_lst = blip.find(A_TAG % "extLst")
    if ext_lst is None:
        ext_lst = etree.SubElement(blip, A_TAG % "extLst")
    ext = etree.SubElement(ext_lst, A_TAG % "ext")
    ext.set("uri", SVG_EXT_URI)
    svg_el = etree.SubElement(ext, "{%s}svgBlip" % SVG_NS, nsmap={"asvg": SVG_NS})
    svg_el.set("{%s}embed" % R_NS, rId)
    return True


def main():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]
    margin = Inches(0.4)
    max_w = prs.slide_width - 2 * margin
    max_h = prs.slide_height - 2 * margin
    n_svg = 0
    for name, caption in FIGS:
        png = os.path.join(FIG_DIR, name + ".png")
        svg = os.path.join(FIG_DIR, name + ".svg")
        slide = prs.slides.add_slide(blank)
        asp = png_aspect(png)
        w = max_w
        h = Emu(int(w / asp))
        if h > max_h:
            h = max_h
            w = Emu(int(h * asp))
        left = Emu(int((prs.slide_width - w) / 2))
        top = Emu(int((prs.slide_height - h) / 2))
        if inject_svg(slide, png, svg, left, top, w, h):
            n_svg += 1
        slide.notes_slide.notes_text_frame.text = caption
    prs.save(OUT)
    print("saved", OUT, "with", n_svg, "vector slides /", len(FIGS), "total")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
