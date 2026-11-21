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
out = [('' if (re.fullmatch(r'\[\[FIG:(.+?)\|(.+?)\]\]', l.strip()) and i not in keep) else l) for i, l in enumerate(lines)]
open(os.path.join(BASE, '_tmp_md_11fig.md'), 'w', encoding='utf-8').write('\n'.join(out))
print('figs', len(figs), 'kept', len(keep))
