# -*- coding: utf-8 -*-
"""Build the Chinese Word draft from 数维杯B题_中文初稿.md.

- A4, Chinese body font SimSun + Times New Roman
- Title on the summary page (no separate cover); auto TOC (levels 1-2)
- Four sections: summary / TOC / body / appendix; body page numbering restarts at 1
- Pipe tables -> Word tables; [[FIG:path|caption]] -> centered picture + caption
- Insert all figures referenced by [[FIG:...]] markers

Rebuild examples:
  python -I build_docx_paper_cn.py                      # single-spaced, full figure set
  PAPER_LINE_SPACING=1.5 python -I build_docx_paper_cn.py
  PAPER_MD=... PAPER_OUT=... PAPER_APPENDIX_START=22 PAPER_BODY_PAGES=21 python -I build_docx_paper_cn.py
"""
import os
import re
import sys

from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.part import Part
from docx.opc.packuri import PackURI
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from lxml import etree
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
MD = os.environ.get("PAPER_MD", os.path.join(BASE, "数维杯B题_中文初稿.md"))
OUT = os.environ.get("PAPER_OUT", os.path.join(BASE, "数维杯B题_中文初稿.docx"))

BODY_FONT_CN = "宋体"
BODY_FONT_EN = "Times New Roman"
HEAD_FONT_CN = "黑体"
BODY_SIZE = 12
CAPTION_SIZE = 10.5
TABLE_SIZE = 9

# Submission placeholder: replace with the real team ID before submission.
TEAM_ID = "<队伍号>"
# "1.5" (default) or "1.0"; override with PAPER_LINE_SPACING=1.0 for the single-spaced test.
LINE_SPACING = os.environ.get("PAPER_LINE_SPACING", "1.0")
# "1" = force every chapter onto a new page; "0" = let short chapters flow.
CHAPTER_BREAKS = os.environ.get("PAPER_CHAPTER_BREAKS", "0") == "1"
# Appendix page number set to body page count + 1 so numbering continues.
APPENDIX_START = os.environ.get("PAPER_APPENDIX_START", "")
# Cached field hints for viewers that do not recalculate fields.
BODY_PAGES_HINT = os.environ.get("PAPER_BODY_PAGES", "1")

A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
SVG_NS = "http://schemas.microsoft.com/office/drawing/2016/SVG/main"
SVG_EXT_URI = "{96DAC541-7B7A-43D3-8B79-37D633B846F1}"
_svg_counter = [0]


def set_run_font(run, size=BODY_SIZE, bold=False, cn=BODY_FONT_CN,
                 en=BODY_FONT_EN, color=None, italic=False):
    run.font.name = en
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
    rFonts.set(qn('w:eastAsia'), cn)
    rFonts.set(qn('w:ascii'), en)
    rFonts.set(qn('w:hAnsi'), en)


def add_runs(paragraph, text, size=BODY_SIZE, base_bold=False, color=None):
    text = text.replace("`", "")
    parts = text.split("**")
    for i, part in enumerate(parts):
        if not part:
            continue
        run = paragraph.add_run(part)
        set_run_font(run, size=size, bold=(base_bold or i % 2 == 1), color=color)


def shade_cell(cell, fill="D9E2F3"):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill)
    tcPr.append(shd)


def set_cell_margins(table, top=40, bottom=40, left=60, right=60):
    tblPr = table._tbl.tblPr
    mar = OxmlElement('w:tblCellMar')
    for name, val in (('top', top), ('left', left), ('bottom', bottom), ('right', right)):
        node = OxmlElement('w:' + name)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        mar.append(node)
    tblPr.append(mar)


def add_field(paragraph, instr, size=9, result="1"):
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
    """Insert a real Word TOC field (standard multi-run structure).

    The field result is a short placeholder until Word updates it; the
    w:dirty flag plus settings/updateFields make Word refresh it on open.
    """
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT

    def _run():
        r = p.add_run()
        set_run_font(r, size=BODY_SIZE)
        return r

    r1 = _run()
    fld1 = OxmlElement('w:fldChar')
    fld1.set(qn('w:fldCharType'), 'begin')
    fld1.set(qn('w:dirty'), 'true')
    r1._r.append(fld1)

    r2 = _run()
    it = OxmlElement('w:instrText')
    it.set(qn('xml:space'), 'preserve')
    it.text = 'TOC \\o "1-2" \\h \\z \\u'
    r2._r.append(it)

    r3 = _run()
    fld2 = OxmlElement('w:fldChar')
    fld2.set(qn('w:fldCharType'), 'separate')
    r3._r.append(fld2)

    r4 = _run()
    t = OxmlElement('w:t')
    t.text = "（目录将在打开文档时自动更新）"
    r4._r.append(t)

    r5 = _run()
    fld3 = OxmlElement('w:fldChar')
    fld3.set(qn('w:fldCharType'), 'end')
    r5._r.append(fld3)


def enable_update_fields(doc):
    """Ask Word to update all fields when the document is opened."""
    settings = doc.settings.element
    uf = settings.find(qn('w:updateFields'))
    if uf is None:
        uf = OxmlElement('w:updateFields')
        settings.append(uf)
    uf.set(qn('w:val'), 'true')


def setup_toc_styles(doc):
    """Compact TOC levels so the whole TOC fits on one page."""
    for name, size in (("TOC 1", 10.5), ("TOC 2", 10.5)):
        try:
            st = doc.styles[name]
        except KeyError:
            st = doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        st.font.name = BODY_FONT_EN
        st.font.size = Pt(size)
        rpr = st.element.get_or_add_rPr()
        rfonts = rpr.find(qn('w:rFonts'))
        if rfonts is None:
            rfonts = OxmlElement('w:rFonts')
            rpr.append(rfonts)
        rfonts.set(qn('w:eastAsia'), BODY_FONT_CN)
        pf = st.paragraph_format
        pf.first_line_indent = Cm(0)
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        pf.line_spacing = 1.0


def setup_styles(doc):
    normal = doc.styles['Normal']
    normal.font.name = BODY_FONT_EN
    normal.font.size = Pt(BODY_SIZE)
    normal.element.rPr.rFonts.set(qn('w:eastAsia'), BODY_FONT_CN)
    pf = normal.paragraph_format
    if LINE_SPACING == "1.0":
        pf.line_spacing = 1.0
    else:
        pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.first_line_indent = Cm(0.85)
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    for name, size in (('Heading 1', 16), ('Heading 2', 14), ('Heading 3', 12)):
        st = doc.styles[name]
        st.font.name = BODY_FONT_EN
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = RGBColor(0, 0, 0)
        st.element.rPr.rFonts.set(qn('w:eastAsia'), HEAD_FONT_CN)
        st.paragraph_format.first_line_indent = Cm(0)
        st.paragraph_format.space_before = Pt(10 if name == 'Heading 1' else 6)
        st.paragraph_format.space_after = Pt(8 if name == 'Heading 1' else 4)
        st.paragraph_format.line_spacing = 1.2
        if name == 'Heading 1':
            st.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER


def set_section_page(sec):
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    sec.top_margin = Cm(2.54)
    sec.bottom_margin = Cm(2.54)
    sec.left_margin = Cm(2.5)
    sec.right_margin = Cm(2.5)
    sec.different_first_page_header_footer = False


def set_page_start(sec, start=1):
    sectPr = sec._sectPr
    pg = sectPr.find(qn('w:pgNumType'))
    if pg is None:
        pg = OxmlElement('w:pgNumType')
        sectPr.append(pg)
    pg.set(qn('w:start'), str(start))


def clear_page_start(sec):
    pg = sec._sectPr.find(qn('w:pgNumType'))
    if pg is not None:
        pg.attrib.pop(qn('w:start'), None)


def _blank_header_footer(sec):
    sec.header.is_linked_to_previous = False
    sec.footer.is_linked_to_previous = False
    sec.different_first_page_header_footer = False
    sec.header.paragraphs[0].text = ""
    sec.footer.paragraphs[0].text = ""


def setup_front_section(sec):
    """Abstract / TOC: no page number (body restarts at 1)."""
    _blank_header_footer(sec)


def setup_body_section(sec):
    """Body: Team + Page X of Y (Y = pages in this body section)."""
    sec.header.is_linked_to_previous = False
    sec.footer.is_linked_to_previous = False
    sec.different_first_page_header_footer = False
    hp = sec.header.paragraphs[0]
    hp.text = ""
    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = hp.add_run("Team # " + TEAM_ID + "  Page ")
    set_run_font(r, size=9)
    add_field(hp, "PAGE", 9)
    r = hp.add_run(" of ")
    set_run_font(r, size=9)
    add_field(hp, "SECTIONPAGES", 9, result=BODY_PAGES_HINT)

    fp = sec.footer.paragraphs[0]
    fp.text = ""
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_field(fp, "PAGE", 10.5)


def setup_appendix_section(sec):
    """Appendix: no header; footer page number continues from the body."""
    sec.header.is_linked_to_previous = False
    sec.footer.is_linked_to_previous = False
    sec.different_first_page_header_footer = False
    sec.header.paragraphs[0].text = ""
    clear_page_start(sec)
    fp = sec.footer.paragraphs[0]
    fp.text = ""
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_field(fp, "PAGE", 10.5, result=APPENDIX_START.strip() or "1")


def setup_page(doc):
    set_section_page(doc.sections[0])
    setup_front_section(doc.sections[0])


def add_title_block(doc):
    """Title at the top of the summary page (no separate cover)."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    r = p.add_run("多移动观测车协同的无人机快速定位与调度")
    set_run_font(r, size=18, bold=True, cn=HEAD_FONT_CN)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("2026 年第十二届数维杯全国大学生数学建模挑战赛（秋季赛）B 题")
    set_run_font(r, size=12)


def add_front_heading(doc, text):
    """Summary / TOC heading: visually like Heading 1 but excluded from TOC."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run(text)
    set_run_font(r, size=16, bold=True, cn=HEAD_FONT_CN)


def add_caption(doc, text, size=CAPTION_SIZE):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text.replace("**", ""))
    set_run_font(r, size=size, bold=True, cn=HEAD_FONT_CN)
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
        try:
            with Image.open(path) as im:
                w, h = im.size
            width_cm = 12.5
            if h / w * width_cm > 17.0:
                width_cm = 17.0 * w / h
            run = p.add_run()
            shape = run.add_picture(path, width=Cm(width_cm))
            # Attach the SVG as the preferred vector rendering (Word 2016+);
            # the PNG above remains as a fallback for older readers.
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
        except Exception as exc:
            r = p.add_run(f"[图片插入失败: {rel_path} ({exc})]")
            set_run_font(r, size=10, color=RGBColor(0xCC, 0x00, 0x00))
    else:
        r = p.add_run(f"[缺图: {rel_path}]")
        set_run_font(r, size=10, color=RGBColor(0xCC, 0x00, 0x00))
    cp = doc.add_paragraph()
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp.paragraph_format.first_line_indent = Cm(0)
    cp.paragraph_format.space_before = Pt(0)
    cp.paragraph_format.space_after = Pt(6)
    r = cp.add_run(caption)
    set_run_font(r, size=CAPTION_SIZE)


def add_table(doc, rows):
    if not rows:
        return
    ncol = max(len(r) for r in rows)
    rows = [r + [""] * (ncol - len(r)) for r in rows]
    table = doc.add_table(rows=len(rows), cols=ncol)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_cell_margins(table)

    # widths
    if ncol == 2:
        widths = [5.0, 11.0]
    elif ncol == 3:
        if rows[0][0].strip() in ("符号",):
            widths = [3.2, 10.8, 2.5]
        elif rows[0][0].strip() in ("场景",):
            widths = [6.0, 5.0, 5.0]
        else:
            widths = [4.0, 6.0, 6.0]
    elif ncol == 4:
        if rows[0][0].strip() == "检验对象":
            widths = [4.2, 5.8, 4.2, 1.8]
        else:
            widths = [6.0, 3.5, 3.25, 3.25]
    elif ncol == 5:
        if rows[0][0].strip() == "告警":
            widths = [2.6, 4.6, 2.6, 3.0, 3.2]
        else:
            widths = [3.0, 3.25, 3.25, 3.25, 3.25]
    elif ncol == 6:
        widths = [2.4, 2.6, 2.7, 2.7, 2.8, 2.8]
    elif ncol == 9 and rows[0][0].strip() == "告警":
        # two-row-per-alert layout of 表 4-4
        widths = [2.0, 1.6, 0.9, 3.0, 1.7, 1.5, 1.6, 1.7, 1.7]
    else:
        widths = [16.0 / ncol] * ncol

    size = TABLE_SIZE if len(rows) > 15 or ncol >= 5 else 10.5

    merge_up = []
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = table.cell(i, j)
            cell.width = Cm(widths[j])
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            if i > 0 and val.strip() == "^":
                # merge with the cell above instead of printing the marker
                merge_up.append((i, j))
                continue
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if j > 0 else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val.replace("**", ""))
            set_run_font(r, size=size, bold=(i == 0))
            if i == 0:
                shade_cell(cell)

    for i, j in merge_up:
        merged = table.cell(i - 1, j).merge(table.cell(i, j))
        for p in list(merged.paragraphs)[1:]:
            if not p.text.strip():
                p._element.getparent().remove(p._element)

    # keep short tables on one page (the caption already has keep_with_next)
    if len(rows) <= 12:
        for row in table.rows[:-1]:
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.paragraph_format.keep_with_next = True

    # repeat header row across pages
    trPr = table.rows[0]._tr.get_or_add_trPr()
    tblHeader = OxmlElement('w:tblHeader')
    tblHeader.set(qn('w:val'), "true")
    trPr.append(tblHeader)

    # prevent row splitting
    for row in table.rows:
        trPr = row._tr.get_or_add_trPr()
        cantSplit = OxmlElement('w:cantSplit')
        trPr.append(cantSplit)

    # spacing paragraph after table
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.first_line_indent = Cm(0)
    return table


def is_sep_row(line):
    s = line.strip()
    return bool(re.fullmatch(r"\|[\s:\-|]+\|", s))


def parse_table(lines, i):
    rows = []
    while i < len(lines) and lines[i].strip().startswith("|"):
        line = lines[i].strip()
        if not is_sep_row(line):
            # "\|" is an escaped literal pipe (e.g. |sin γ| inside a cell)
            line = line.replace("\\|", "\u0000")
            cells = [c.strip().replace("\u0000", "|")
                     for c in line.strip("|").split("|")]
            rows.append(cells)
        i += 1
    return rows, i


def main():
    if not os.path.exists(MD):
        raise SystemExit("Markdown not found: " + MD)
    with open(MD, encoding="utf-8") as f:
        lines = f.read().splitlines()

    doc = Document()
    setup_page(doc)
    setup_styles(doc)
    setup_toc_styles(doc)
    add_title_block(doc)

    # start at abstract
    start = next((k for k, l in enumerate(lines) if l.strip() == "## 摘要"), 0)
    i = start
    content_started = False
    skip_toc = False
    in_abstract = False
    n_fig = 0

    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()
        s = line.strip()

        if not s:
            i += 1
            continue

        if s == "---":
            i += 1
            continue

        # figure marker
        m = re.fullmatch(r"\[\[FIG:(.+?)\|(.+?)\]\]", s)
        if m:
            add_figure(doc, m.group(1).strip(), m.group(2).strip())
            n_fig += 1
            i += 1
            continue

        # table
        if s.startswith("|"):
            rows, i = parse_table(lines, i)
            add_table(doc, rows)
            continue

        # headings
        if s.startswith("### "):
            text = s[4:].strip()
            doc.add_heading(text, level=3)
            i += 1
            continue
        if s.startswith("## "):
            text = s[3:].strip()
            if text == "目录":
                in_abstract = False
                sec = doc.add_section(WD_SECTION.NEW_PAGE)
                setup_front_section(sec)
                add_front_heading(doc, "目录")
                add_toc_field(doc)
                skip_toc = True
                i += 1
                continue
            if text == "摘要":
                in_abstract = True
                add_front_heading(doc, "摘要")
                content_started = True
                i += 1
                continue
            doc.add_heading(text, level=2)
            content_started = True
            i += 1
            continue
        if s.startswith("# "):
            text = s[2:].strip()
            if text.startswith("2026 年"):
                i += 1
                continue
            if text.startswith("1 问题重述"):
                sec = doc.add_section(WD_SECTION.NEW_PAGE)
                setup_body_section(sec)
                set_page_start(sec, 1)
                set_section_page(sec)
            elif text == "附录":
                sec = doc.add_section(WD_SECTION.NEW_PAGE)
                setup_appendix_section(sec)
                set_section_page(sec)
                if APPENDIX_START.strip().isdigit():
                    set_page_start(sec, int(APPENDIX_START.strip()))
            elif content_started and CHAPTER_BREAKS:
                doc.add_page_break()
            doc.add_heading(text, level=1)
            content_started = True
            skip_toc = False
            i += 1
            continue

        # skip manual TOC list until horizontal rule / next H1
        if skip_toc:
            i += 1
            continue

        # blockquote
        if s.startswith(">"):
            text = s[1:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.left_indent = Cm(0.5)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            r = p.add_run(text.replace("`", ""))
            set_run_font(r, size=10.5, color=RGBColor(0x66, 0x66, 0x66), italic=True)
            i += 1
            continue

        # table caption
        if s.startswith("**表"):
            add_caption(doc, s)
            i += 1
            continue

        # normal paragraph
        p = doc.add_paragraph()
        add_runs(p, s)
        if in_abstract:
            p.paragraph_format.line_spacing = 1.15
            for r in p.runs:
                r.font.size = Pt(12)
        i += 1

    # post-process headings so that fonts are explicit (Word sometimes keeps theme fonts)
    for p in doc.paragraphs:
        if p.style is None or p.style.name not in ("Heading 1", "Heading 2", "Heading 3"):
            continue
        level = int(p.style.name[-1])
        size = {1: 16, 2: 14, 3: 12}[level]
        p.paragraph_format.first_line_indent = Cm(0)
        for r in p.runs:
            set_run_font(r, size=size, bold=True, cn=HEAD_FONT_CN)

    doc.core_properties.title = "数维杯 B 题 多移动观测车协同的无人机快速定位与调度（中文初稿）"
    doc.core_properties.subject = "2026 年第十二届数维杯全国大学生数学建模挑战赛（秋季赛）"
    doc.core_properties.author = "Team <队伍号>"
    enable_update_fields(doc)
    doc.save(OUT)
    print("saved", OUT)
    print("figures inserted:", n_fig)


if __name__ == "__main__":
    main()
