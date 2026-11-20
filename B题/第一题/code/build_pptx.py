# -*- coding: utf-8 -*-
"""Assemble the Problem-1 figure album into a 16:9 PPTX.

Each slide carries one figure as a native SVG (editable: right-click ->
"Convert to Shape" in PowerPoint 2016+) with an embedded PNG fallback.
Suggested English captions are written into the slide NOTES, not on the
slide itself, so the figures stay free of any text.
"""
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
OUT = os.path.join(BASE, "第一题_图集.pptx")

R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
SVG_NS = "http://schemas.microsoft.com/office/drawing/2016/SVG/main"
SVG_EXT_URI = "{96DAC541-7B7A-43D3-8B79-37D633B846F1}"
A_TAG = "{http://schemas.openxmlformats.org/drawingml/2006/main}%s"

FIGS = [
    ("fig1_observable_region",
     "Fig. 1  Observable region of target T1 over the 100 m x 100 m field. "
     "Blue = feasible station positions (Omega); grey = infeasible; grey prisms = "
     "buildings B1-B5; red star = T1's horizontal projection; black dot = dispatch "
     "center O; blue squares = vehicles V1-V5. The grey disk around the star is the "
     "gimbal-limit exclusion zone (r < 7.58 m)."),
    ("fig2_constraint_layers",
     "Fig. 2  Layered contribution of the three constraints. Left: vehicle geometry "
     "C1 only. Middle: C1 and gimbal elevation C2 (adds the r < 7.58 m exclusion "
     "disk). Right: C1, C2 and line-of-sight occlusion C3 (adds the occlusion "
     "shadows behind buildings)."),
    ("fig3_optimal_arc_zoom",
     "Fig. 3  Left: zoom near T1 showing the optimal circle r* = 7.58 m; green arc = "
     "feasible portion (~284 deg), red arc = blocked by B2 and its 1.5 m clearance "
     "buffer (~76 deg); black pentagon = chosen optimal station (88.88, 76.29); "
     "blue square = nearest vehicle V4. Right: geometric safety-margin profile along "
     "the circle vs. polar angle; shaded band = blocked arc; the red open circle marks "
     "the true maximum margin m* = 9.675 m at phi = 56.5 deg (where the B2-buffer "
     "distance equals the east-boundary distance); the black pentagon is the finally "
     "selected station -- the shortest-to-reach point inside the tie-breaking band "
     "m >= m* - 0.05 m (its own margin is 9.625 m, limited by the east boundary)."),
    ("fig4_sensitivity_rstar",
     "Fig. 4  Closed-form sensitivity of the optimal distance r* = (H-2)/tan(80 deg). "
     "Left: r* vs. target altitude H (nominal H = 45 m marked; slope 0.176 m per m). "
     "Right: r* vs. the gimbal elevation bound (nominal 80 deg marked; -0.774 m per "
     "degree)."),
    ("fig5_sensitivity_area",
     "Fig. 5  Sensitivity of the observable-region area. Left: area vs. building B2 "
     "height (nominal 28 m marked). Right: area vs. vehicle equivalent radius "
     "(nominal 1.5 m marked)."),
    ("fig6_los_3d",
     "Fig. 6  3D schematic of the line of sight from the chosen optimal station "
     "(black dot, camera height 2 m) to target T1 (red star, altitude 45 m); the LOS "
     "clears every building prism (minimum clearance 7.41 m)."),
]

ASPECT = {  # width / height from the matplotlib figsize (fallback if no PIL)
    "fig1_observable_region": 6.4 / 6.0,
    "fig2_constraint_layers": 13.2 / 4.6,
    "fig3_optimal_arc_zoom": 12.4 / 5.6,
    "fig4_sensitivity_rstar": 11.0 / 4.4,
    "fig5_sensitivity_area": 11.0 / 4.4,
    "fig6_los_3d": 7.6 / 6.0,
}

_svg_counter = [0]


def png_aspect(path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size[0] / im.size[1]
    except Exception:
        return None


def inject_svg(slide, png_path, svg_path, left, top, width, height):
    """add_picture(png) as fallback, then attach the SVG as preferred rendering.

    Returns True when the SVG vector layer was attached, False if only the
    PNG fallback is present.
    """
    pic = slide.shapes.add_picture(png_path, left, top, width, height)
    try:
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
    except Exception as e:
        print("  SVG layer skipped (%s)" % e)
        return False


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
        asp = png_aspect(png) or ASPECT[name]
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
