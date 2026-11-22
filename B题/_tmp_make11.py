import os, re
from PIL import Image
BASE = os.getcwd()
src = os.path.join(BASE, '数维杯B题_中文初稿.md')
lines = open(src, encoding='utf-8').read().splitlines()
figs = []
for i, l in enumerate(lines):
    m = re.fullmatch(r'\[\[FIG:(.+?)\|(.+?)\]\]', l.strip())
    if m:
        path = m.group(1).strip().replace('/', os.sep)
        p = os.path.join(BASE, path)
        try:
            with Image.open(p) as im:
                w, h = im.size
            hcm = 12.5 * h / w
            if hcm > 17.0: hcm = 17.0
        except Exception:
            hcm = 12.5
        figs.append((i, hcm))
keep = set(i for i, _ in sorted(figs, key=lambda x: -x[1])[:11])

# For a dropped figure, also drop its reading note (the paragraph right after
# the blank line following the marker) so the 11-fig build has no orphan text.
drop = set()
for i, _ in figs:
    if i in keep:
        continue
    drop.add(i)
    cap = re.fullmatch(r'\[\[FIG:(.+?)\|(.+?)\]\]', lines[i].strip()).group(2)
    num = re.match(r'(图\s*\d+-\d+)', cap)
    if not num:
        continue
    j = i + 1
    if j < len(lines) and not lines[j].strip():
        j += 1
    if j < len(lines) and lines[j].strip().startswith(num.group(1)):
        drop.add(j)

out = [('' if i in drop else l) for i, l in enumerate(lines)]
open(os.path.join(BASE, '_tmp_md_11fig.md'), 'w', encoding='utf-8').write('\n'.join(out))
print('figs', len(figs), 'kept', len(keep), 'dropped_lines', len(drop))
