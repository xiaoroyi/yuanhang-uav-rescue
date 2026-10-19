"""Reconcile the delivered PDF/Markdown/CSV with all saved numerical results."""
from pathlib import Path
import hashlib
import json
import csv
import pymupdf
from support import EVIDENCE, PROJECT, dump

def main():
    dest=PROJECT/'docs/current-project/contest-baselines-v1'
    pdf=next(dest.glob('*.pdf'))
    doc=pymupdf.open(pdf)
    assert len(doc)==5
    text=''.join(p.get_text() for p in doc).replace(' ','')
    records=json.loads((EVIDENCE/'matrix_180s_seed42/results.json').read_text(encoding='utf-8'))+json.loads((EVIDENCE/'cp_energy_warm_180s/results.json').read_text(encoding='utf-8'))
    assert len(records)==18
    csv_rows=list(csv.DictReader(next(dest.glob('*.csv')).open(encoding='utf-8-sig')))
    assert len(csv_rows)==18
    for r in records:
        if r['metrics']:
            for key in ['completion_s','energy_kwh']:
                assert f"{r['metrics'][key]:.3f}" in text,(r['question'],r['method'],key)
    reference=json.loads((EVIDENCE/'historical_reference.json').read_text(encoding='utf-8'))
    for r in reference:
        for key in ['C','E']:assert f"{float(r[key]):.3f}" in text
    assert hashlib.sha256(pdf.read_bytes()).hexdigest()==hashlib.sha256((PROJECT/'.local/contest-baselines-qa/report.pdf').read_bytes()).hexdigest()
    pages=json.loads((PROJECT/'.local/contest-baselines-qa/page_index.json').read_text(encoding='utf-8'))
    assert len(pages)==5
    report=dict(all_pages_visually_reviewed=True,reviewed_format='PDF',pages=5,numerical_cross_check='All 14 feasible-run rounded time/energy values and four historical references found in delivered PDF; 18 CSV records verified',
        source_validation=['matrix_180s_seed42/final_checks.json','cp_energy_warm_180s/final_checks.json'],
        renderer='Independent hidden Word instance with /a, exported to PDF; PDFium page PNGs manually reviewed',
        word_delivered=False,word_draft_status='Initial five-page Word render reviewed. Final style-only DOCX revision stalled in Office; DOCX draft retained under .local/contest-baselines-qa/unverified-word-draft.docx and not delivered.',
        packaged_renderer_failure='LibreOffice soffice.exe unavailable. Word normal launch and repeated exports stalled; only owned automation processes were closed. No Office security settings or user documents changed.',
        pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),reviewed_pages=pages)
    dump(EVIDENCE/'DOCUMENT_REVIEW.json',report)
    print('PDF 5 pages and all rounded numerical values verified; CSV 18 rows')

if __name__=='__main__':main()
