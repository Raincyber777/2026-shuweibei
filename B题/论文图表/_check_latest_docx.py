# -*- coding: utf-8 -*-
"""Is 01_论文/数维杯B题_中文初稿_11图_最新.docx the latest final draft?
Checks: git state, mtime, five-fix content, embedded media inventory."""
import io
import os
import re
import subprocess
import zipfile
from datetime import datetime

ROOT = "e:\\2026数维杯\\2026-shuweibei"
DOCX = os.path.join(ROOT, "B题", "01_论文", "数维杯B题_中文初稿_11图_最新.docx")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "_check_latest_docx_out.txt")

lines = []


def run(args):
    p = subprocess.run(args, capture_output=True, cwd=ROOT)
    return p.stdout.decode("utf-8", "replace").strip()


lines.append("== mtime ==")
mt = datetime.fromtimestamp(os.path.getmtime(DOCX))
lines.append(f"{mt:%Y-%m-%d %H:%M:%S}  {os.path.getsize(DOCX)} bytes")

rel = "B题/01_论文/数维杯B题_中文初稿_11图_最新.docx"
lines.append("== git ==")
lines.append("HEAD: " + run(["git", "log", "--oneline", "-1"]))
lines.append("status of file: [" + run(["git", "status", "--porcelain", "--",
                                        rel]) + "]  (empty = 与 HEAD 一致)")
lines.append("last commit touching file: " + run(
    ["git", "log", "--oneline", "-1", "--", rel]))

lines.append("== content: five fixes ==")
with zipfile.ZipFile(DOCX) as z:
    xml = z.read("word/document.xml").decode("utf-8")
    media = [n for n in z.namelist() if n.startswith("word/media/")]
text = re.sub(r"<[^>]+>", "", xml)

for want, ban, name in [
        ("300 次迭代", None, "修正1 Q2(1) NM≤300"),
        ("最优性验证", "四维搜索降为", "修正2 最优性验证"),
        ("可证性", "保证最优性", "修正3 摘要口径"),
        ("复用链次序", "复用次序", "修正4a 术语"),
        ("每车至多 2 个任务", "O(5×2)", "修正4c 术语"),
        ("5880", None, "5880 组合数"),
        ("10.355", None, "makespan 10.355"),
        ("5610.4", None, "Ω(T1) 5610.4"),
        ("66.92", None, "s_max 66.92")]:
    ok_want = want in text
    ok_ban = (ban is None) or (ban not in text)
    verdict = "OK" if ok_want and ok_ban else "PROBLEM"
    extra = "" if ban is None else f" / 残留[{ban}]={'有' if not ok_ban else '无'}"
    lines.append(f"[{verdict}] {name}: 含[{want}]={'有' if ok_want else '无'}"
                 f"{extra}")

lines.append("== embedded media ==")
ext = {}
for n in media:
    e = os.path.splitext(n)[1].lower()
    ext[e] = ext.get(e, 0) + 1
lines.append("media total: %d  by type: %s" % (
    len(media), ", ".join(f"{k}×{v}" for k, v in sorted(ext.items()))))

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("done")
