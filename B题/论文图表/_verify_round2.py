# -*- coding: utf-8 -*-
"""Round-2 verification: do the teammate's 5 claimed fixes live in the DOCX
(and/or MD)? Plus brute-force 5880 combo check, arc-sampling code check,
and file mtimes. Results -> _verify_round2_out.txt (UTF-8)."""
import io
import math
import os
import re
import zipfile
from datetime import datetime
from itertools import combinations, product

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.dirname(HERE)
DOCX = os.path.join(B, "01_论文", "数维杯B题_中文初稿_11图_最新.docx")
MD = os.path.join(B, "数维杯B题_中文初稿.md")
BEIZHAO = os.path.join(B, "01_论文", "备查", "数维杯B题_中文初稿.docx")
OUT = os.path.join(HERE, "_verify_round2_out.txt")

lines = []


def docx_text(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    return re.sub(r"<[^>]+>", "", xml)


dx = docx_text(DOCX)
with io.open(MD, encoding="utf-8") as f:
    md = f.read()

# ---- A. the 5 claimed fixes -------------------------------------------------
FIX = [
    ("修正1  Q2(1) NM=300",
     ["300 次迭代", "≤300", "≤ 300"],
     ["≤160 次迭代", "160 次）"],
     "应含 300；不应再有 160（Q2(1) 语境）"),
    ("修正2  最优性验证表述",
     ["最优性验证"],
     ["四维搜索降为", "四维搜索化"],
     "应含『最优性验证』；不含『四维搜索降为』"),
    ("修正3  摘要口径",
     ["可证性"],
     ["保证最优性"],
     "应含『可证性』；摘要不应再有『保证最优性』"),
    ("修正4a  术语 复用链次序",
     ["复用链次序"],
     ["复用次序"],
     "应统一为『复用链次序』"),
    ("修正4b  术语 死锁",
     ["死锁"],
     ["互等死锁"],
     "应统一为『死锁』"),
    ("修正4c  术语 每车至多2个任务",
     ["每车至多 2 个任务", "每车至多2个任务"],
     ["O(5×2)", "O(5x2)"],
     "应改为『每车至多 2 个任务』"),
]

lines.append("==== A. 五处修正落地情况（DOCX / MD） ====")
for name, wants, ban, note in FIX:
    for src_name, txt in (("DOCX", dx), ("MD", md)):
        have = [w for w in wants if w in txt]
        bad = [w for w in ban if w in txt]
        verdict = "OK" if have and not bad else "MISS"
        lines.append(f"[{verdict}] {name} @ {src_name}: "
                     f"含={have or '无'} 残留={bad or '无'}")

# ---- B. 5880 combos brute force ---------------------------------------------
total = 0
for choice in product(combinations(range(5), 2), repeat=3):
    deg = [0] * 5
    for a, b in choice:
        deg[a] += 1
        deg[b] += 1
    w = 1
    for k in deg:
        if k >= 2:
            w *= math.factorial(k)
    total += w
lines.append("")
lines.append(f"==== B. 5880 组合数暴力验算: total = {total} "
             f"({'OK 与文中一致' if total == 5880 else 'MISMATCH'}) ====")

# ---- C. arc sampling count in q1 code ---------------------------------------
lines.append("")
lines.append("==== C. Q1 20 万点弧采样代码检查 ====")
q1dir = os.path.join(B, "第一题", "code")
for fn in sorted(os.listdir(q1dir)):
    if not fn.endswith(".py"):
        continue
    t = io.open(os.path.join(q1dir, fn), encoding="utf-8").read()
    hits = re.findall(r".{0,40}(?:200000|200_000|2 ?\* ?10\*\*5|0\.0018).{0,40}",
                      t)
    for h in hits[:4]:
        lines.append(f"{fn}: …{h}…")
    if not hits:
        lines.append(f"{fn}: 无 20 万点相关字面量")

# ---- D. file mtimes ---------------------------------------------------------
lines.append("")
lines.append("==== D. 关键文件修改时间 ====")
for p in (MD, DOCX, BEIZHAO):
    try:
        mt = datetime.fromtimestamp(os.path.getmtime(p))
        lines.append(f"{mt:%Y-%m-%d %H:%M:%S}  {os.path.relpath(p, B)}")
    except Exception as e:
        lines.append(f"MISSING {p}: {e!r}")

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("checks done, see _verify_round2_out.txt")
