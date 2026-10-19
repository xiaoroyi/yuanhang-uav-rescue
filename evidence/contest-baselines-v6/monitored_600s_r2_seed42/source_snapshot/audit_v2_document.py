"""Cross-check final PDF, Markdown, CSV, saved metrics; render every PDF page."""
import csv
import hashlib
from pathlib import Path
import pymupdf
from benchmark_v2 import V2,V1,load,digest
from support import PROJECT,dump

def main():
    dest=PROJECT/'docs/current-project/contest-baselines-v2'
    pdf=dest/'援航十分钟基线对比实验报告.pdf'
    markdown=(dest/'对比实验报告.md').read_text(encoding='utf-8')
    document=pymupdf.open(pdf)
    text=''.join(page.get_text() for page in document).replace(' ','').replace('\n','')
    records=load(V2/'main_600s_seed42/results.json')
    rows=list(csv.DictReader((dest/'完整结果对比.csv').open(encoding='utf-8-sig')))
    assert len(rows)==32
    for r in records:
        for cp in r['checkpoints']:
            row=next(x for x in rows if x['question']==r['question'] and x['objective']==r['objective'] and x['method']==r['method'] and float(x['checkpoint_s'])==cp['checkpoint_s'])
            for field in ['completion_s','energy_kwh']:
                value=cp['metrics'][field]
                assert f'{value:.3f}' in text and f'{value:.3f}' in markdown,(r['question'],r['objective'],r['method'],field)
                assert abs(float(row[field])-value)<1e-8
            assert row['solution_sha256']==cp['solution_sha256']
    for r in load(V1/'historical_reference.json'):
        for field in ['C','E']:assert f"{float(r[field]):.3f}" in text
    pages=[];qa=PROJECT/'.local/contest-baselines-v2-qa';qa.mkdir(exist_ok=True,parents=True)
    for i,page in enumerate(document):
        assert page.get_text().strip(),'Empty PDF page'
        # Verify all text stays on page; visual review is still required separately.
        for block in page.get_text('blocks'):
            assert block[0]>=0 and block[1]>=0 and block[2]<=page.rect.width+.1 and block[3]<=page.rect.height+.1,(i+1,block)
        png=qa/f'page_{i+1:02}.png';page.get_pixmap(matrix=pymupdf.Matrix(1.35,1.35),alpha=False).save(png)
        pages.append(dict(page=i+1,png=str(png.relative_to(PROJECT)),sha256=digest(png)))
    result=dict(all_numerical_values_verified=True,all_pages_visually_reviewed=False,pages=len(document),
        pdf_sha256=digest(pdf),renderer='ReportLab UnicodeCIDFont STSong-Light; independent PyMuPDF PNG rendering',
        csv_rows=32,checkpoint_metrics_compared=64,reviewed_pages=pages,
        source='evidence/contest-baselines-v2/main_600s_seed42/final_checks.json')
    dump(V2/'DOCUMENT_REVIEW.json',result)
    print(f'{len(document)} PDF pages rendered; 32 CSV rows and all 64 paired time/energy values matched')

if __name__=='__main__':main()
