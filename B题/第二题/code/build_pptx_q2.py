# -*- coding: utf-8 -*-
"""Assemble the Problem-2 figure album into a 16:9 PPTX.

Same SVG-injection technique as Problem 1: one figure per slide as a native
SVG (right-click -> "Convert to Shape" in PowerPoint 2016+) with an embedded
PNG fallback; suggested English captions go into the slide NOTES only.
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
OUT = os.path.join(BASE, "第二题_图集.pptx")

R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
SVG_NS = "http://schemas.microsoft.com/office/drawing/2016/SVG/main"
SVG_EXT_URI = "{96DAC541-7B7A-43D3-8B79-37D633B846F1}"
A_TAG = "{http://schemas.openxmlformats.org/drawingml/2006/main}%s"

FIGS = [
    ("fig1_region_reach",
     "Fig. 1  Observable region of alert T2 (light blue) over the field; grey "
     "prisms = buildings; red star = T2's horizontal projection; dashed circles "
     "= 30 s reach limits (radius 90 m) of vehicles V1-V5 from their start "
     "points (blue squares)."),
    ("fig2_layers_T2",
     "Fig. 2  Layered constraints for T2. Left: vehicle geometry only. Middle: "
     "plus the gimbal elevation bound (exclusion disk r < 5.82 m around T2). "
     "Right: plus line-of-sight occlusion (shadow wedges behind buildings)."),
    ("fig3_optimal_pair_zoom",
     "Fig. 3  Zoom at T2. On the minimum circle r = 5.8188 m: red arc = blocked "
     "(tangent LOS through B3 or building buffer), green arc = feasible, dark "
     "green arc = robust-feasible (LOS clearance and geometric margin >= 0.5 m). "
     "Black pentagons = the chosen optimal station pair (V3, V5), connected by "
     "the baseline; the 90 deg intersection angle is marked by the arc at the "
     "target; dashed circles = reach limits of V3 and V5."),
    ("fig4_accuracy_model",
     "Fig. 4  Accuracy model. Left: geometry factor G = sqrt((d1^2+d2^2)/2)/"
     "|sin(gamma)| vs intersection angle for symmetric ranges d = 5.82, 10, 15, "
     "20 m; the marker marks the optimum (gamma = 90 deg, G = 5.82 m); G "
     "diverges as gamma -> 0/180 deg. Right: semi-axes of the 95% error ellipse "
     "vs gamma at d = 5.8188 m (solid: major, dashed: minor; isotropic at 90 "
     "deg, radius 0.249 m)."),
    ("fig5_sensitivity",
     "Fig. 5  Left: optimal geometry factor G* = (H-2)/tan(80 deg) vs target "
     "altitude H (nominal H = 35 m marked; slope 0.176 m per m). Right: "
     "normalized accuracy degradation G/G* vs intersection angle; dashed line = "
     "2xG* level defining the operating window gamma in [30, 150] deg."),
    ("fig6_error_ellipses",
     "Fig. 6  Position error ellipses at the optimal pair: 1-sigma and 2-sigma "
     "circles (blue) and the 95% circle (red, radius 0.2486 m) around T2's "
     "projection; dotted lines = the two bearing lines; black pentagons = "
     "stations. The error field is isotropic because d1 = d2 and gamma = 90 "
     "deg."),
    ("fig7_gantt_opt",
     "Fig. 7  Optimized scheme: vehicle timelines (rows 1-5 = V1-V5). Colors: "
     "light blue = travel, orange = gimbal slew, grey = waiting for the partner "
     "vehicle (synchronization), green = 5 s joint observation, red = gimbal "
     "reset. Observation starts: T1 at 1.53 s, T2 at 6.99 s, T3 at 10.83 s; "
     "maximum = 10.83 s. V5 serves T1 first and is then reused for T3 from the "
     "same position."),
    ("fig8_gantt_heu",
     "Fig. 8  Nearest-assignment baseline: same timeline convention. The "
     "greedy chains both tasks of V1 and V3 and synchronizes poorly; maximum "
     "observation start = 30.21 s (T2)."),
    ("fig9_routes_map",
     "Fig. 9  Optimized deployment map: colored pentagons = assigned stations "
     "(per vehicle color), arrows = travel legs. Most stations coincide with "
     "the vehicle start points: with slew-dominated timing, staying put is "
     "optimal; dashed red lines = alert azimuths from the dispatch center."),
    ("fig10_comparison_sens",
     "Fig. 10  Left: observation start times per alert (rows 1-3 = T1-T3), "
     "green = optimized, red = nearest-assignment baseline. Middle: optimized "
     "objective vs vehicle speed (nominal 3 m/s marked). Right: objective vs "
     "gimbal slew rate (nominal 30 deg/s marked)."),
]

_svg_counter = [0]


def png_aspect(path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size[0] / im.size[1]
    except Exception:
        return None


def inject_svg(slide, png_path, svg_path, left, top, width, height):
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
        svg_el = etree.SubElement(ext, "{%s}svgBlip" % SVG_NS,
                                  nsmap={"asvg": SVG_NS})
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
