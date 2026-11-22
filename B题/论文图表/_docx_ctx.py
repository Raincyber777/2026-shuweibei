# -*- coding: utf-8 -*-
"""Extract exact corrected sentences from the final DOCX for md backfill."""
import io
import os
import re
import zipfile

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCX = os.path.join(B, "01_论文", "数维杯B题_中文初稿_11图_最新.docx")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "_docx_ctx_out.txt")

with zipfile.ZipFile(DOCX) as z:
    xml = z.read("word/document.xml").decode("utf-8")
text = re.sub(r"<[^>]+>", "", xml)

KEYS = ["可证性", "每车至多", "复用链次序", "互等", "保证最优性"]
lines = []
for k in KEYS:
    for m in re.finditer(re.escape(k), text):
        s = max(0, m.start() - 60)
        e = min(len(text), m.end() + 60)
        lines.append(f"[{k}] …{text[s:e]}…")
    if k not in text:
        lines.append(f"[{k}] <not found>")

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n\n".join(lines))
print("done")
