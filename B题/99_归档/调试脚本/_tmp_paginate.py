import os, sys
import win32com.client as win32
p = os.path.abspath(sys.argv[1])
app = win32.DispatchEx('Word.Application')
app.Visible = False
app.DisplayAlerts = 0
doc = app.Documents.Open(p)
for _ in range(3):
    try: doc.Fields.Update()
    except Exception: pass
    try: doc.TablesOfContents(1).Update()
    except Exception: pass
    doc.Repaginate()
for sec in doc.Sections:
    for hf in (sec.Headers, sec.Footers):
        for item in hf:
            try: item.Range.Fields.Update()
            except Exception: pass
doc.Repaginate()
doc.Save()
total = doc.ComputeStatistics(2)
print('TOTAL_PAGES', total)
secs = []
for i in range(1, doc.Sections.Count + 1):
    r = doc.Sections(i).Range
    s0 = r.Start
    e0 = max(r.Start, r.End - 1)
    pg_start = doc.Range(s0, s0).Information(3)
    pg_end = doc.Range(e0, e0).Information(3)
    hdr = doc.Sections(i).Headers(1).Range.Text.replace('\r',' ').strip()
    ftr = doc.Sections(i).Footers(1).Range.Text.replace('\r',' ').strip()
    secs.append((i, pg_start, pg_end, hdr, ftr))
for s in secs: print('SECTION', s)
if len(secs) >= 3:
    body_start = secs[2][1]
    appendix_start = secs[3][1] if len(secs) >= 4 else total + 1
    print('FRONT_BODY_PAGES_EXCL_APPENDIX', appendix_start - 1)
    print('BODY_PAGES', appendix_start - body_start)
doc.Close(True)
app.Quit()
