# -*- coding: utf-8 -*-
"""Problem-4 figure album PPTX (same SVG-injection technique as Problems 1-3)."""
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
OUT = os.path.join(BASE, "第四题_图集.pptx")

R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
SVG_NS = "http://schemas.microsoft.com/office/drawing/2016/SVG/main"
SVG_EXT_URI = "{96DAC541-7B7A-43D3-8B79-37D633B846F1}"
A_TAG = "{http://schemas.openxmlformats.org/drawingml/2006/main}%s"

FIGS = [
    ("fig1_map_new_alerts",
     "Fig. 1  The 24 representative new-alert positions (8 azimuths x R = 30/40/50 m, "
     "H = 50 m) coloured by the rescheduled latest observation start time t_last "
     "(colour bar in seconds); grey prisms = buildings; red stars = base alerts "
     "T1-T3; blue squares = vehicles V1-V5. Under keep-original every position "
     "gives eta = 0.75 and t_last = 60 s because the new alert is never assigned."),
    ("fig2_tlast_vs_theta",
     "Fig. 2  Rescheduled t_last vs. new-alert azimuth for R = 30 m (blue), 40 m "
     "(green), 50 m (orange); red dashed = t_last = 60 s (keep-original level for "
     "every new-alert scenario); black dotted = disturbance-free t_last = 10.36 s. "
     "The azimuth dependence reflects which idle vehicles can reach the new alert."),
    ("fig3_failures",
     "Fig. 3  Single-failure scenarios (rows 1-5 = failed vehicle V1-V5). Left: "
     "completion ratio eta, red = keep-original, green = rescheduling; right: "
     "t_last. V5 fails after T1 completed (its only task), so both policies keep "
     "eta = 1; the other failures orphan one alert under keep-original "
     "(eta = 0.67, t_last = 60) while rescheduling restores eta = 1 at the cost "
     "of a later t_last."),
    ("fig4_fail_outage",
     "Fig. 4  Failure + communication outage: t_last vs. recovery time t_rec "
     "(solid = rescheduling, dotted with crosses = keep-original, per failed "
     "vehicle colour). Keep-original stays at 60 s for any impacted vehicle; "
     "rescheduling recovers eta = 1 at t_rec and t_last grows with t_rec. V3 "
     "curves stay at the undisturbed level (no impact)."),
    ("fig5_gantt_failV4",
     "Fig. 5  Representative timelines for the failure of V4 (rows 1-5 = V1-V5; "
     "colors: light blue travel, orange slew, grey sync wait, green 5 s "
     "observation, red reset). Left: keep-original - V4 waits forever, T2 never "
     "starts (eta = 0.67, t_last = 60). Right: rescheduling - V2 and V3 are "
     "re-paired to T2 and eta = 1 is restored."),
    ("fig6_global_scatter",
     "Fig. 6  All scenarios: (t_last, eta) for keep-original (red crosses) vs. "
     "rescheduling (green circles). Rescheduling dominates or matches in every "
     "scenario; the red cluster at (60, 0.75) and (60, 0.67) are the new-alert "
     "and impacted-failure cases that only rescheduling can recover."),
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
