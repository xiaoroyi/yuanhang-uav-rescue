"""Render the document QA PDF with the bundled document runtime."""
from pathlib import Path
import json
import hashlib
import pypdfium2 as pdfium
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[2]
QA=ROOT/'.local/contest-baselines-qa'
reader=PdfReader(QA/'report.pdf')
doc=pdfium.PdfDocument(QA/'report.pdf')
pages=QA/'pages';pages.mkdir(exist_ok=True)
rows=[]
for i,page in enumerate(doc):
    bitmap=page.render(scale=1.5)
    image=bitmap.to_pil();path=pages/f'page-{i+1:02}.png';image.save(path)
    text=reader.pages[i].extract_text()
    rows.append(dict(page=i+1,chars=len(text),first=text[:100],last=text[-100:],image_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    image.close();bitmap.close();page.close()
(QA/'page_index.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(rows,ensure_ascii=False,indent=2))
