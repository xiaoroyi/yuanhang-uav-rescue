"""Verify user-specified sources against the archive; inspect results read-only."""
import hashlib
import json
from pathlib import Path
import sys
from openpyxl import load_workbook
import pymupdf
from support import PROJECT, EVIDENCE, dump

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    origin=PROJECT.parent.parent/'华为杯数学建模2026'
    submitted=origin/'提交材料完整版_D26106140150-------------------'
    sources=[]
    for external,local in [(submitted/'D26106140150.pdf',PROJECT/'references/modeling/paper.pdf'),
                           (submitted/'D26106140150_答案.xlsx',PROJECT/'references/modeling/answers.xlsx')]:
        a,b=sha(external),sha(local)
        assert a==b,(external,local)
        sources.append(dict(original=str(external),archived=str(local.relative_to(PROJECT)),sha256=a,identical=True))
    for local in (PROJECT/'references/modeling/data/tables').glob('*.xlsx'):
        matches=list((origin/'D题').rglob(local.name))
        assert len(matches)==1,local.name
        assert sha(matches[0])==sha(local),local.name
        sources.append(dict(original=str(matches[0]),archived=str(local.relative_to(PROJECT)),sha256=sha(local),identical=True))
    for local in (PROJECT/'references/modeling/data/terrain').glob('*.mat'):
        external=next((origin/'D题').rglob(local.name))
        assert sha(local)==sha(external)
        sources.append(dict(original=str(external),archived=str(local.relative_to(PROJECT)),sha256=sha(local),identical=True))
    wb=load_workbook(submitted/'D26106140150_答案.xlsx',read_only=True,data_only=True)
    transport=list(wb['Q2_运输架次'].values)[1:]
    q2=dict(completion_s=max(r[6] for r in transport),energy_kwh=sum(r[7] for r in transport),sorties=len(transport))
    assert abs(q2['completion_s']-5693.242512959364)<1e-6
    assert abs(q2['energy_kwh']-66.21486599521012)<1e-6
    wb.close()
    doc=pymupdf.open(submitted/'D26106140150.pdf')
    extracts=[]
    for i,page in enumerate(doc):
        text=page.get_text()
        if any(x in text for x in ['表4.11','表5.14']):
            extracts.append(dict(physical_page=i+1,text=text))
            page.get_pixmap(matrix=pymupdf.Matrix(1.2,1.2)).save(EVIDENCE/f'cache/paper_page_{i+1}.png')
    dump(EVIDENCE/'input_verification.json',dict(sources=sources,q2_workbook=q2,all_sources_identical=True,paper_extracts=extracts))
    print('verified',len(sources),'sources; workbook Q2',q2,'paper pages',[v['physical_page'] for v in extracts])

if __name__=='__main__':
    main()
