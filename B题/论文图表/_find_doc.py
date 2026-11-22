# -*- coding: utf-8 -*-
"""Locate the handover doc (AI交接文档_当前进度.md) and dump dir listings."""
import io
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))          # repo root: 2026-shuweibei
B = os.path.join(ROOT, "B题")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "_find_doc_result.txt")

lines = []


def walk_find(base, needle):
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames
                       if d not in (".git", "__pycache__")]
        for fn in filenames:
            if needle in fn:
                lines.append("FOUND: " + os.path.join(dirpath, fn))


lines.append("== repo root: " + ROOT)
lines.append("== B题 root listing ==")
try:
    for name in sorted(os.listdir(B)):
        full = os.path.join(B, name)
        lines.append(("[D] " if os.path.isdir(full) else "[F] ") + name)
except Exception as e:
    lines.append("LIST-ERR: " + repr(e))

lines.append("== search 'AI交接' under repo ==")
try:
    walk_find(ROOT, "AI交接")
except Exception as e:
    lines.append("WALK-ERR: " + repr(e))

lines.append("== search '交接' under desktop package ==")
try:
    walk_find(r"C:\Users\ASUS\Desktop\shuwei材料包", "交接")
except Exception as e:
    lines.append("WALK-ERR: " + repr(e))

lines.append("== git status (porcelain) ==")
try:
    p = subprocess.run(["git", "-C", ROOT, "status", "--porcelain"],
                       capture_output=True)
    lines.append(p.stdout.decode("utf-8", "replace"))
    lines.append("git stderr: " + p.stderr.decode("utf-8", "replace")[:300])
except Exception as e:
    lines.append("GIT-ERR: " + repr(e))

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("written:", os.path.basename(OUT), len(lines), "lines")
