# -*- coding: utf-8 -*-
"""Build the English Word paper by filling the official ShuWei Cup template.

Source : 数维杯B题_英文稿.md
Base   : 00_赛题与规范/...Word模版.docx
Output : 数维杯B题_英文稿.docx

Design notes
- Summary page: keep the template's Summary Sheet table, replace the
  instruction paragraphs with title + abstract + keywords.
- TOC page: keep the "Contents" heading and insert a real TOC field.
- Body: replace the template skeleton with the paper, reuse the template's
  final section so the body header/page numbering can be rebuilt.
- Formulas stay plain text; <sub>/<sup> markers become real Word
  subscript/superscript runs (not OMML equations).
"""
import os
import re

from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import (WD_ALIGN_PARAGRAPH, WD_LINE_SPACING,
                            WD_TAB_ALIGNMENT)
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.part import Part
from docx.opc.packuri import PackURI
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.text.paragraph import Paragraph
from lxml import etree
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.environ.get(
    "PAPER_TEMPLATE",
    os.path.join(BASE, "00_赛题与规范",
                 "2026年第十二届数维杯全国大学生数学建模挑战赛（秋季赛）Word模版.docx"))
MD = os.environ.get("PAPER_MD", os.path.join(BASE, "数维杯B题_英文稿.md"))
OUT = os.environ.get("PAPER_OUT", os.path.join(BASE, "数维杯B题_英文稿.docx"))

TEAM_ID = os.environ.get("PAPER_TEAM_ID", "SWBMCM2611718")
TITLE = "Fast UAV Localization and Scheduling with Multiple Cooperative Mobile Observation Vehicles"
SUBTITLE = ("2026 12th ShuWei Cup National College Mathematical Modeling Challenge "
            "(Autumn) — Problem B")

BODY_FONT = "Times New Roman"
BODY_SIZE = 12
SUMMARY_SIZE = float(os.environ.get("PAPER_SUMMARY_SIZE", "12"))
CAPTION_SIZE = 10.5
TABLE_SIZE_SMALL = 8.8
TABLE_SIZE = 9.5
REF_SIZE = 10.5
TABLE_WIDTH_CM = 16.8
BODY_MARGIN_CM = float(os.environ.get("PAPER_MARGIN", "2.0"))
FIG_WIDTH_CM = float(os.environ.get("PAPER_FIG_WIDTH", "10.9"))
FIG_MAX_H_CM = float(os.environ.get("PAPER_FIG_MAX_H", "14.5"))
BODY_LINE_SPACING = float(os.environ.get("PAPER_LINE_SPACING", "1.0"))

A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
SVG_NS = "http://schemas.microsoft.com/office/drawing/2016/SVG/main"
SVG_EXT_URI = "{96DAC541-7B7A-43D3-8B79-37D633B846F1}"
_svg_counter = [0]


# --------------------------------------------------------------------------
# low-level formatting helpers
# --------------------------------------------------------------------------
def set_run_font(run, size=BODY_SIZE, bold=False, italic=False, color=None,
                 name=BODY_FONT):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color is not None:
        run.font.color.rgb = color
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.append(rFonts)
    rFonts.set(qn('w:eastAsia'), name)
    rFonts.set(qn('w:ascii'), name)
    rFonts.set(qn('w:hAnsi'), name)


TOKEN_RE = re.compile(r"(<sub>|</sub>|<sup>|</sup>)")


def add_runs(paragraph, text, size=BODY_SIZE, base_bold=False, color=None,
             italic=False):
    """Add text, honouring **bold** and <sub>/<sup> markers."""
    text = text.replace("`", "")
    for i, part in enumerate(text.split("**")):
        if not part:
            continue
        bold = base_bold or (i % 2 == 1)
        mode = None
        for tok in TOKEN_RE.split(part):
            if tok == "<sub>":
                mode = "sub"
            elif tok == "</sub>":
                mode = None
            elif tok == "<sup>":
                mode = "sup"
            elif tok == "</sup>":
                mode = None
            elif tok:
                run = paragraph.add_run(tok)
                set_run_font(run, size=size, bold=bold, italic=italic,
                             color=color)
                if mode == "sub":
                    run.font.subscript = True
                elif mode == "sup":
                    run.font.superscript = True


def shade_cell(cell, fill="D9E2F3"):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill)
    tcPr.append(shd)


def add_heading_parsed(doc, text, level):
    """Heading paragraph that still honours <sub>/<sup> in its text."""
    p = doc.add_heading("", level=level)
    add_runs(p, text, size={1: 16, 2: 13.5, 3: 12}[level],
             base_bold=True, color=RGBColor(0, 0, 0))
    return p


def clear_para_borders(paragraph):
    pPr = paragraph._p.find(qn('w:pPr'))
    if pPr is None:
        return
    pBdr = pPr.find(qn('w:pBdr'))
    if pBdr is not None:
        pPr.remove(pBdr)


def remove_header_style_border(doc):
    """Remove the template Header style's bottom rule (shows on the summary page)."""
    try:
        st = doc.styles['Header']
    except KeyError:
        return
    pPr = st.element.find(qn('w:pPr'))
    if pPr is None:
        return
    pBdr = pPr.find(qn('w:pBdr'))
    if pBdr is not None:
        pPr.remove(pBdr)


def set_cell_margins(table, top=15, bottom=15, left=40, right=40):
    tblPr = table._tbl.tblPr
    mar = OxmlElement('w:tblCellMar')
    for name, val in (('top', top), ('left', left),
                      ('bottom', bottom), ('right', right)):
        node = OxmlElement('w:' + name)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        mar.append(node)
    tblPr.append(mar)


def add_field(paragraph, instr, size=9.0, result="1"):
    run = paragraph.add_run()
    set_run_font(run, size=size)
    fld1 = OxmlElement('w:fldChar')
    fld1.set(qn('w:fldCharType'), 'begin')
    it = OxmlElement('w:instrText')
    it.set(qn('xml:space'), 'preserve')
    it.text = instr
    fld2 = OxmlElement('w:fldChar')
    fld2.set(qn('w:fldCharType'), 'separate')
    t = OxmlElement('w:t')
    t.text = result
    fld3 = OxmlElement('w:fldChar')
    fld3.set(qn('w:fldCharType'), 'end')
    run._r.append(fld1)
    run._r.append(it)
    run._r.append(fld2)
    run._r.append(t)
    run._r.append(fld3)


def add_toc_field(doc):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0)
    r1 = p.add_run()
    set_run_font(r1, size=BODY_SIZE)
    fld1 = OxmlElement('w:fldChar')
    fld1.set(qn('w:fldCharType'), 'begin')
    fld1.set(qn('w:dirty'), 'true')
    r1._r.append(fld1)

    r2 = p.add_run()
    set_run_font(r2, size=BODY_SIZE)
    it = OxmlElement('w:instrText')
    it.set(qn('xml:space'), 'preserve')
    it.text = 'TOC \\o "1-2" \\h \\z \\u'
    r2._r.append(it)

    r3 = p.add_run()
    set_run_font(r3, size=BODY_SIZE)
    fld2 = OxmlElement('w:fldChar')
    fld2.set(qn('w:fldCharType'), 'separate')
    r3._r.append(fld2)

    r4 = p.add_run("Right-click and choose Update Field to refresh the contents.")
    set_run_font(r4, size=BODY_SIZE)

    r5 = p.add_run()
    set_run_font(r5, size=BODY_SIZE)
    fld3 = OxmlElement('w:fldChar')
    fld3.set(qn('w:fldCharType'), 'end')
    r5._r.append(fld3)
    return p


def enable_update_fields(doc):
    settings = doc.settings.element
    uf = settings.find(qn('w:updateFields'))
    if uf is None:
        uf = OxmlElement('w:updateFields')
        settings.append(uf)
    uf.set(qn('w:val'), 'false')


def set_page(sec, margins=(2.54, 2.54, 2.54, 2.54)):
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    left, right, top, bottom = margins
    sec.left_margin = Cm(left)
    sec.right_margin = Cm(right)
    sec.top_margin = Cm(top)
    sec.bottom_margin = Cm(bottom)


def set_page_start(sec, start=1, fmt='decimal'):
    sectPr = sec._sectPr
    pg = sectPr.find(qn('w:pgNumType'))
    if pg is None:
        pg = OxmlElement('w:pgNumType')
        sectPr.append(pg)
    pg.set(qn('w:fmt'), fmt)
    pg.set(qn('w:start'), str(start))


def blank_header_footer(sec):
    sec.header.is_linked_to_previous = False
    sec.footer.is_linked_to_previous = False
    sec.different_first_page_header_footer = False
    sec.header.paragraphs[0].text = ""
    sec.footer.paragraphs[0].text = ""
    sec.header.paragraphs[0].style = "Normal"
    sec.footer.paragraphs[0].style = "Normal"
    clear_para_borders(sec.header.paragraphs[0])
    clear_para_borders(sec.footer.paragraphs[0])


def setup_appendix_header(sec):
    sec.header.is_linked_to_previous = False
    sec.footer.is_linked_to_previous = False
    sec.different_first_page_header_footer = False
    hp = sec.header.paragraphs[0]
    hp.text = ""
    clear_para_borders(hp)
    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = hp.add_run("Team # " + TEAM_ID + "          Appendix Page ")
    set_run_font(r, size=9.5)
    add_field(hp, "PAGE", 9.5, result="A")
    fp = sec.footer.paragraphs[0]
    fp.text = ""
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER


def setup_body_header(sec):
    sec.header.is_linked_to_previous = False
    sec.footer.is_linked_to_previous = False
    sec.different_first_page_header_footer = False
    hp = sec.header.paragraphs[0]
    hp.text = ""
    clear_para_borders(hp)
    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = hp.add_run("Team # " + TEAM_ID + "          Page ")
    set_run_font(r, size=9.5)
    add_field(hp, "PAGE", 9.5)
    r = hp.add_run(" of 25")
    set_run_font(r, size=9.5)
    fp = sec.footer.paragraphs[0]
    fp.text = ""
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER


# --------------------------------------------------------------------------
# summary page
# --------------------------------------------------------------------------
def set_summary_cell(cell, lines, sizes, bold_last=True):
    cell.text = ""
    first = True
    for text, size in zip(lines, sizes):
        p = cell.paragraphs[0] if first else cell.add_paragraph()
        first = False
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        add_runs(p, text, size=size,
                 base_bold=(bold_last and text == lines[-1]))


def fill_summary_sheet(doc):
    tbl = doc.tables[0]
    set_summary_cell(tbl.rows[0].cells[0], ["Problem Chosen", "B"],
                     [10.5, 13])
    set_summary_cell(tbl.rows[0].cells[1],
                     ["2026", "ShuWei Cup", "Summary Sheet"],
                     [10.5, 10.5, 13])
    set_summary_cell(tbl.rows[0].cells[2],
                     ["Team Control Number", TEAM_ID],
                     [10.5, 12])


def summary_section_break_para(doc):
    for p in doc.paragraphs:
        pPr = p._p.find(qn('w:pPr'))
        if pPr is not None and pPr.find(qn('w:sectPr')) is not None:
            return p
    raise RuntimeError("summary section break not found")


def build_summary(doc, lines):
    tbl = doc.tables[0]
    anchor = summary_section_break_para(doc)
    body = doc.element.body
    start = tbl._tbl
    started = False
    for child in list(body.iterchildren()):
        if child is start:
            started = True
            continue
        if started:
            if child is anchor._p:
                break
            body.remove(child)

    def ins(text="", size=SUMMARY_SIZE, bold=False, italic=False,
            align=WD_ALIGN_PARAGRAPH.JUSTIFY, before=0, after=0,
            indent=0.0, spacing=1.0):
        p = anchor.insert_paragraph_before()
        p.alignment = align
        pf = p.paragraph_format
        pf.first_line_indent = Cm(indent)
        pf.space_before = Pt(before)
        pf.space_after = Pt(after)
        pf.line_spacing = spacing
        if text:
            add_runs(p, text, size=size, base_bold=bold, italic=italic)
        return p

    ins(TITLE, size=16.5, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER,
        before=3, after=3, spacing=1.0)
    ins(SUBTITLE, size=10.5, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER,
        after=6, spacing=1.0)

    in_abs = False
    for raw in lines:
        s = raw.strip()
        if s.startswith("## Abstract"):
            in_abs = True
            continue
        if s.startswith("## Contents"):
            break
        if not in_abs or not s:
            continue
        if s.startswith("**Keywords:**"):
            p = ins("", after=1, indent=0.0, spacing=0.96)
            add_runs(p, "**Keywords:**", size=SUMMARY_SIZE)
            add_runs(p, " " + s[len("**Keywords:**"):].strip(),
                     size=SUMMARY_SIZE, italic=True)
        else:
            ins(s, size=SUMMARY_SIZE, indent=0.5, spacing=0.96, after=1)


# --------------------------------------------------------------------------
# TOC page
# --------------------------------------------------------------------------
def build_toc(doc):
    content_p = None
    for p in doc.paragraphs:
        if p.text.strip() in ("Content", "Contents"):
            content_p = p
            break
    if content_p is None:
        raise RuntimeError("Contents heading not found")
    content_p.text = ""
    r = content_p.add_run("Contents")
    set_run_font(r, size=16, bold=True, color=RGBColor(0, 0, 0))
    content_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    content_p.paragraph_format.space_before = Pt(6)
    content_p.paragraph_format.space_after = Pt(6)

    # find the section-break paragraph that ends the TOC section
    toc_break = None
    seen = False
    for p in doc.paragraphs:
        if p._p is content_p._p:
            seen = True
            continue
        if not seen:
            continue
        pPr = p._p.find(qn('w:pPr'))
        if pPr is not None and pPr.find(qn('w:sectPr')) is not None:
            toc_break = p
            break
    if toc_break is None:
        raise RuntimeError("TOC section break not found")

    body = doc.element.body
    seen = False
    for child in list(body.iterchildren()):
        if child is content_p._p:
            seen = True
            continue
        if not seen:
            continue
        if child is toc_break._p:
            break
        body.remove(child)

    # add the TOC field before the break paragraph
    toc_p = add_toc_field(doc)
    toc_break._p.addprevious(toc_p._p)
    return toc_break


# --------------------------------------------------------------------------
# tables and figures
# --------------------------------------------------------------------------
def is_sep_row(line):
    return bool(re.fullmatch(r"\|[\s:\-|]+\|", line.strip()))


def parse_table(lines, i):
    rows = []
    while i < len(lines) and lines[i].strip().startswith("|"):
        line = lines[i].strip()
        if not is_sep_row(line):
            line = line.replace("\\|", "\u0000")
            cells = [c.strip().replace("\u0000", "|")
                     for c in line.strip("|").split("|")]
            rows.append(cells)
        i += 1
    return rows, i


def fit_widths(widths, target=TABLE_WIDTH_CM):
    total = sum(widths)
    return [w * target / total for w in widths]


def table_widths(rows, ncol):
    head = rows[0][0].strip().lower() if rows else ""
    if ncol == 2:
        widths = [5.6, 11.2]
    elif ncol == 3:
        if head == "symbol":
            widths = [4.4, 9.6, 3.4]
        elif head in ("scenario class", "scenario"):
            widths = [6.6, 5.1, 5.1]
        else:
            widths = [4.6, 6.1, 6.1]
    elif ncol == 4:
        if head == "object":
            widths = [3.8, 6.0, 4.6, 2.4]
        else:
            widths = [6.4, 3.6, 3.4, 3.4]
    elif ncol == 5:
        if head == "alert":
            widths = [2.4, 4.6, 2.4, 3.4, 4.0]
        elif head == "problem":
            widths = [1.5, 5.6, 4.2, 2.6, 2.9]
        else:
            widths = [3.2, 3.4, 3.4, 3.4, 3.4]
    elif ncol == 7:
        widths = [2.2, 3.8, 1.7, 1.9, 1.9, 2.6, 3.0]
    elif ncol == 9:
        widths = [1.6, 1.3, 3.4, 1.5, 1.5, 1.5, 1.8, 1.8, 1.9]
    elif ncol == 6:
        widths = [2.6, 2.8, 2.8, 2.8, 2.8, 3.0]
    else:
        widths = [1.0] * ncol
    return fit_widths(widths)


def add_table(doc, rows, size=None):
    if not rows:
        return
    ncol = max(len(r) for r in rows)
    rows = [r + [""] * (ncol - len(r)) for r in rows]
    table = doc.add_table(rows=len(rows), cols=ncol)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_cell_margins(table)
    widths = table_widths(rows, ncol)
    if size is None:
        if len(rows) > 20:
            size = 8.2
        elif len(rows) > 15 or ncol >= 5:
            size = TABLE_SIZE_SMALL
        else:
            size = TABLE_SIZE

    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = table.cell(i, j)
            cell.width = Cm(widths[j])
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            p.alignment = (WD_ALIGN_PARAGRAPH.CENTER if j > 0
                           else WD_ALIGN_PARAGRAPH.LEFT)
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            add_runs(p, val, size=size, base_bold=(i == 0))
            if i == 0:
                shade_cell(cell)

    if len(rows) <= 12:
        for row in table.rows[:-1]:
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.paragraph_format.keep_with_next = True

    # the symbol table reads better with a left-aligned meaning column
    if rows[0][0].strip().lower() == "symbol":
        for row in table.rows:
            for p in row.cells[1].paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT

    trPr = table.rows[0]._tr.get_or_add_trPr()
    tblHeader = OxmlElement('w:tblHeader')
    tblHeader.set(qn('w:val'), "true")
    trPr.append(tblHeader)
    for row in table.rows:
        trPr = row._tr.get_or_add_trPr()
        cantSplit = OxmlElement('w:cantSplit')
        trPr.append(cantSplit)

    return table


def add_caption(doc, text, size=CAPTION_SIZE, bold=True):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    add_runs(p, text, size=size, base_bold=bold)
    return p


def add_figure(doc, rel_path, caption):
    path = os.path.join(BASE, rel_path.replace("/", os.sep))
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    if os.path.exists(path):
        with Image.open(path) as im:
            w, h = im.size
        width_cm = FIG_WIDTH_CM
        if h / w * width_cm > FIG_MAX_H_CM:
            width_cm = FIG_MAX_H_CM * w / h
        run = p.add_run()
        shape = run.add_picture(path, width=Cm(width_cm))
        svg_path = path[:-4] + ".svg" if path.lower().endswith(".png") else None
        if svg_path and os.path.exists(svg_path):
            try:
                svg_blob = open(svg_path, "rb").read()
                _svg_counter[0] += 1
                partname = PackURI("/word/media/svgimage%d.svg" % _svg_counter[0])
                part = Part(partname, "image/svg+xml", svg_blob, doc.part.package)
                rId = doc.part.relate_to(part, RT.IMAGE)
                blip = shape._inline.graphic.graphicData.pic.blipFill.blip
                ext_lst = blip.find("{%s}extLst" % A_NS)
                if ext_lst is None:
                    ext_lst = etree.SubElement(blip, "{%s}extLst" % A_NS)
                ext = etree.SubElement(ext_lst, "{%s}ext" % A_NS)
                ext.set("uri", SVG_EXT_URI)
                svg_el = etree.SubElement(ext, "{%s}svgBlip" % SVG_NS,
                                          nsmap={"asvg": SVG_NS})
                svg_el.set("{%s}embed" % R_NS, rId)
            except Exception as exc:
                print("SVG layer skipped:", rel_path, exc)
    else:
        r = p.add_run("[missing figure: %s]" % rel_path)
        set_run_font(r, size=10, color=RGBColor(0xCC, 0x00, 0x00))

    cp = doc.add_paragraph()
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp.paragraph_format.first_line_indent = Cm(0)
    cp.paragraph_format.space_before = Pt(0)
    cp.paragraph_format.space_after = Pt(6)
    add_runs(cp, caption, size=CAPTION_SIZE)
    return p


# --------------------------------------------------------------------------
# body
# --------------------------------------------------------------------------
def style_headings(doc):
    for p in doc.paragraphs:
        if p.style is None or p.style.name not in ("Heading 1", "Heading 2",
                                                   "Heading 3"):
            continue
        level = int(p.style.name[-1])
        size = {1: 16, 2: 13.5, 3: 12}[level]
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_before = Pt({1: 6, 2: 4, 3: 2}[level])
        p.paragraph_format.space_after = Pt({1: 3, 2: 2, 3: 1}[level])
        p.paragraph_format.keep_with_next = True
        for r in p.runs:
            set_run_font(r, size=size, bold=True, color=RGBColor(0, 0, 0))


def build_body(doc, lines, start_idx):
    in_refs = False
    in_appendix = False
    i = start_idx
    n_fig = 0
    while i < len(lines):
        raw = lines[i]
        s = raw.strip()
        if not s or s == "---":
            i += 1
            continue

        m = re.fullmatch(r"\[\[FIG:(.+?)\|(.+?)\]\]", s)
        if m:
            add_figure(doc, m.group(1).strip(), m.group(2).strip())
            n_fig += 1
            i += 1
            continue

        if s.startswith("|"):
            rows, i = parse_table(lines, i)
            add_table(doc, rows)
            continue

        if s.startswith("### "):
            add_heading_parsed(doc, s[4:].strip(), 3)
            i += 1
            continue
        if s.startswith("## "):
            add_heading_parsed(doc, s[3:].strip(), 2)
            i += 1
            continue
        if s.startswith("# "):
            text = s[2:].strip()
            if text.lower().startswith("references"):
                in_refs = True
                in_appendix = False
            elif text.lower() == "appendix":
                # Appendix is excluded from the 25-page body limit:
                # start a separate section with its own header/numbering.
                doc.add_section(WD_SECTION.NEW_PAGE)
                in_refs = False
                in_appendix = True
            add_heading_parsed(doc, text, 1)
            i += 1
            continue

        # table caption above the table
        if s.startswith("**Table "):
            add_caption(doc, s)
            i += 1
            continue

        # display formula (optionally with a right-aligned equation number)
        m_eq = re.fullmatch(r"\$\$(.+)\$\$\s*\((\d+)\)", s)
        if m_eq or (s.startswith("$$") and s.endswith("$$") and len(s) > 4):
            if m_eq:
                formula, eqno = m_eq.group(1).strip(), m_eq.group(2)
            else:
                formula, eqno = s[2:-2].strip(), None
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.0
            size = 10 if len(formula) <= 70 else 9
            if eqno:
                p.paragraph_format.tab_stops.add_tab_stop(
                    Cm(TABLE_WIDTH_CM / 2), WD_TAB_ALIGNMENT.CENTER)
                p.paragraph_format.tab_stops.add_tab_stop(
                    Cm(TABLE_WIDTH_CM), WD_TAB_ALIGNMENT.RIGHT)
                p.add_run("\t")
                add_runs(p, formula, size=size)
                r = p.add_run("\t(" + eqno + ")")
                set_run_font(r, size=9)
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                add_runs(p, formula, size=size)
            i += 1
            continue

        # bullets (Appendix B)
        if s.startswith("- "):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.left_indent = Cm(0.55)
            p.paragraph_format.first_line_indent = Cm(-0.4)
            p.paragraph_format.space_after = Pt(0.2)
            p.paragraph_format.line_spacing = 1.0
            r = p.add_run("• ")
            set_run_font(r, size=9.5)
            add_runs(p, s[2:], size=9.5)
            i += 1
            continue

        # notes under tables
        if s.startswith("Note:"):
            p = doc.add_paragraph()
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.0
            add_runs(p, s, size=9.0)
            i += 1
            continue

        # ordinary paragraph
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.first_line_indent = Cm(0.75)
        p.paragraph_format.space_after = Pt(0)
        if in_refs:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.left_indent = Cm(0.75)
            p.paragraph_format.first_line_indent = Cm(-0.75)
            add_runs(p, s, size=REF_SIZE)
        else:
            p.paragraph_format.line_spacing = BODY_LINE_SPACING
            add_runs(p, s, size=BODY_SIZE)
        i += 1
    return n_fig


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main():
    with open(MD, encoding="utf-8") as f:
        lines = f.read().splitlines()

    doc = Document(TEMPLATE)

    # styles
    normal = doc.styles['Normal']
    normal.font.name = BODY_FONT
    normal.font.size = Pt(BODY_SIZE)
    pf = normal.paragraph_format
    pf.line_spacing = 1.0
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.first_line_indent = Cm(0.75)
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for name, size in (('Heading 1', 16), ('Heading 2', 14), ('Heading 3', 12)):
        try:
            st = doc.styles[name]
        except KeyError:
            st = doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
            st.base_style = doc.styles['Normal']
            st.next_paragraph_style = doc.styles['Normal']
        st.font.name = BODY_FONT
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = RGBColor(0, 0, 0)
        st.paragraph_format.first_line_indent = Cm(0)

    fill_summary_sheet(doc)
    build_summary(doc, lines)
    toc_break = build_toc(doc)

    # delete the template's body skeleton after the TOC section break,
    # keeping the final body-level sectPr
    body = doc.element.body
    children = list(body.iterchildren())
    idx = children.index(toc_break._p)
    for child in children[idx + 1:]:
        if child.tag == qn('w:sectPr'):
            continue
        body.remove(child)

    # locate the first body chapter
    start_idx = next((k for k, l in enumerate(lines)
                      if re.match(r"^# 1\.\s", l.strip())), 0)
    n_fig = build_body(doc, lines, start_idx)
    style_headings(doc)

    # page setup / headers
    secs = doc.sections
    if len(secs) < 4:
        raise RuntimeError("expected 4 sections, got %d" % len(secs))
    set_page(secs[0], margins=(2.0, 2.0, 1.0, 2.2))
    blank_header_footer(secs[0])
    set_page(secs[1], margins=(2.0, 2.0, 2.0, 2.0))
    blank_header_footer(secs[1])
    set_page(secs[2], margins=(BODY_MARGIN_CM, BODY_MARGIN_CM,
                                BODY_MARGIN_CM, BODY_MARGIN_CM))
    setup_body_header(secs[2])
    set_page_start(secs[2], 1, 'decimal')
    set_page(secs[3], margins=(BODY_MARGIN_CM, BODY_MARGIN_CM,
                                BODY_MARGIN_CM, BODY_MARGIN_CM))
    setup_appendix_header(secs[3])
    set_page_start(secs[3], 1, 'upperLetter')
    remove_header_style_border(doc)

    doc.core_properties.title = TITLE + " (English draft)"
    doc.core_properties.subject = ("2026 12th ShuWei Cup National College "
                                   "Mathematical Modeling Challenge (Autumn), Problem B")
    doc.core_properties.author = "Team " + TEAM_ID
    enable_update_fields(doc)
    doc.save(OUT)
    print("saved", OUT)
    print("figures inserted:", n_fig)
    print("sections:", len(secs))


if __name__ == "__main__":
    main()
