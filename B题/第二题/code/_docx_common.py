# -*- coding: utf-8 -*-
"""Shared helpers for building the three Problem-1 Word documents."""
import json
import os

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo-relative


def load_results(name="q2a_results.json"):
    with open(os.path.join(BASE, "results", name), encoding="utf-8") as f:
        return json.load(f)


def new_doc():
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.top_margin = sec.bottom_margin = Cm(2.54)
    sec.left_margin = sec.right_margin = Cm(2.8)
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(12)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    return doc


def _font(run, size=12, bold=False, mono=False, ea="宋体"):
    run.font.name = "Consolas" if mono else "Times New Roman"
    run.font.size = Pt(size)
    run.font.bold = bold
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas" if mono else ea)


def title(doc, text, sub=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _font(p.add_run(text), 16, True)
    if sub:
        p2 = doc.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _font(p2.add_run(sub), 12, False)


def h1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before, p.paragraph_format.space_after = Pt(14), Pt(6)
    _font(p.add_run(text), 15, True)


def h2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before, p.paragraph_format.space_after = Pt(8), Pt(4)
    _font(p.add_run(text), 13, True)


def para(doc, text, indent=True):
    p = doc.add_paragraph()
    if indent:
        p.paragraph_format.first_line_indent = Pt(24)
    p.paragraph_format.line_spacing = 1.3
    _font(p.add_run(text), 12)


def bullet(doc, text, level=0):
    p = doc.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
    p.paragraph_format.line_spacing = 1.3
    _font(p.add_run(text), 12)


def code_block(doc, text, size=9):
    for line in text.split("\n"):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        _font(p.add_run(line if line else " "), size, mono=True)


def table(doc, headers, rows, size=10.5, header_bold=True):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = "Table Grid"
    for j, htxt in enumerate(headers):
        cell = t.cell(0, j)
        cell.text = ""
        _font(cell.paragraphs[0].add_run(htxt), size, header_bold)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = t.cell(i + 1, j)
            cell.text = ""
            _font(cell.paragraphs[0].add_run(str(val)), size)
    return t


def spacer(doc, pts=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(pts)
