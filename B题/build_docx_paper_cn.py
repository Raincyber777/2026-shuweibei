# -*- coding: utf-8 -*-
"""Build the Chinese Word draft from 数维杯B题_中文初稿.md.

- A4, Chinese body font SimSun + Times New Roman
- Cover page, auto TOC field, headers/footers with PAGE/NUMPAGES fields
- Pipe tables -> Word tables; [[FIG:path|caption]] -> centered picture + caption
- Insert all 28 figures from the four question folders
"""
import os
import re
import sys

from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.part import Part
from docx.opc.packuri import PackURI
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from lxml import etree
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(BASE, "数维杯B题_中文初稿.md")
OUT = os.path.join(BASE, "数维杯B题_中文初稿.docx")

BODY_FONT_CN = "宋体"
BODY_FONT_EN = "Times New Roman"
HEAD_FONT_CN = "黑体"
BODY_SIZE = 12
CAPTION_SIZE = 10.5
TABLE_SIZE = 9

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


def add_field(paragraph, instr, size=9):
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
    t.text = "1"
    fld3 = OxmlElement('w:fldChar')
    fld3.set(qn('w:fldCharType'), 'end')
    run._r.append(fld1)
    run._r.append(it)
    run._r.append(fld2)
    run._r.append(t)
    run._r.append(fld3)


def add_toc_field(doc):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run()
    set_run_font(run, size=BODY_SIZE)
    fld1 = OxmlElement('w:fldChar')
    fld1.set(qn('w:fldCharType'), 'begin')
    it = OxmlElement('w:instrText')
    it.set(qn('xml:space'), 'preserve')
    it.text = 'TOC \\o "1-3" \\h \\z \\u'
    fld2 = OxmlElement('w:fldChar')
    fld2.set(qn('w:fldCharType'), 'separate')
    t = OxmlElement('w:t')
    t.text = "（在 Word 中右键“更新域”生成目录）"
    fld3 = OxmlElement('w:fldChar')
    fld3.set(qn('w:fldCharType'), 'end')
    run._r.append(fld1)
    run._r.append(it)
    run._r.append(fld2)
    run._r.append(t)
    run._r.append(fld3)


def setup_styles(doc):
    normal = doc.styles['Normal']
    normal.font.name = BODY_FONT_EN
    normal.font.size = Pt(BODY_SIZE)
    normal.element.rPr.rFonts.set(qn('w:eastAsia'), BODY_FONT_CN)
    pf = normal.paragraph_format
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


def setup_page(doc):
    sec = doc.sections[0]
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    sec.top_margin = Cm(2.54)
    sec.bottom_margin = Cm(2.54)
    sec.left_margin = Cm(2.5)
    sec.right_margin = Cm(2.5)
    sec.different_first_page_header_footer = True

    hp = sec.header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = hp.add_run("Team <队伍号>  Page ")
    set_run_font(r, size=9)
    add_field(hp, "PAGE", 9)
    r = hp.add_run(" of ")
    set_run_font(r, size=9)
    add_field(hp, "NUMPAGES", 9)

    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = fp.add_run("第 ")
    set_run_font(r, size=9)
    add_field(fp, "PAGE", 9)
    r = fp.add_run(" 页")
    set_run_font(r, size=9)


def add_cover(doc):
    for _ in range(4):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("2026 年第十二届数维杯全国大学生")
    set_run_font(r, size=18, bold=True, cn=HEAD_FONT_CN)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("数学建模挑战赛（秋季赛）")
    set_run_font(r, size=18, bold=True, cn=HEAD_FONT_CN)
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("B 题")
    set_run_font(r, size=20, bold=True, cn=HEAD_FONT_CN)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("多移动观测车协同的无人机快速定位与调度")
    set_run_font(r, size=16, bold=True, cn=HEAD_FONT_CN)
    for _ in range(5):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("中 文 初 稿")
    set_run_font(r, size=14, bold=True, cn=HEAD_FONT_CN)
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("2026 年 11 月")
    set_run_font(r, size=12)
    for _ in range(4):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    r = p.add_run("本稿用于内容定稿、图表插入与格式检查；终稿按赛事要求统一英译。")
    set_run_font(r, size=10.5, color=RGBColor(0x66, 0x66, 0x66), italic=True)
    doc.add_page_break()


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
        widths = [6.0, 3.5, 3.25, 3.25]
    elif ncol == 5:
        widths = [3.0, 3.25, 3.25, 3.25, 3.25]
    elif ncol == 6:
        widths = [2.4, 2.6, 2.7, 2.7, 2.8, 2.8]
    else:
        widths = [16.0 / ncol] * ncol

    size = TABLE_SIZE if len(rows) > 15 or ncol >= 5 else 10.5

    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = table.cell(i, j)
            cell.width = Cm(widths[j])
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if j > 0 else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val.replace("**", ""))
            set_run_font(r, size=size, bold=(i == 0))
            if i == 0:
                shade_cell(cell)

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
            cells = [c.strip() for c in line.strip("|").split("|")]
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
    add_cover(doc)

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
                doc.add_page_break()
                doc.add_heading("目录", level=1)
                add_toc_field(doc)
                skip_toc = True
                i += 1
                continue
            if text == "摘要":
                in_abstract = True
                doc.add_heading("摘要", level=1)
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
            if content_started:
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
            p.paragraph_format.line_spacing = 1.3
            for r in p.runs:
                r.font.size = Pt(11)
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
    doc.save(OUT)
    print("saved", OUT)
    print("figures inserted:", n_fig)


if __name__ == "__main__":
    main()
