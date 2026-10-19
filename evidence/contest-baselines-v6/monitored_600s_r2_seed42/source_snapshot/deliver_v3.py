"""Render/audit the final PDF, then register the reviewed EXP-C03 artifacts."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import pymupdf
from benchmark_v3 import V3
from benchmark_v2 import load,digest,V1
from support import PROJECT,dump

DEST=PROJECT/'docs/current-project/contest-baselines-v3'
def audit():
    pdf=DEST/'援航对齐上限能耗对照报告.pdf';doc=pymupdf.open(pdf)
    text=''.join(p.get_text() for p in doc).replace(' ','').replace('\n','')
    runs=load(V3/'aligned_600s_seed42/results.json');rows=list(csv.DictReader((DEST/'完整结果对比.csv').open(encoding='utf-8-sig')))
    assert len(rows)==16
    for r in runs:
        for c in r['checkpoints']:
            row=next(x for x in rows if x['question']==r['question'] and x['method']==r['method'] and float(x['checkpoint_s'])==c['checkpoint_s'])
            assert row['status']==c['status']
            if c['metrics']:
                for field in ['completion_s','energy_kwh']:
                    assert f"{c['metrics'][field]:.3f}" in text
                    assert abs(float(row[field])-c['metrics'][field])<1e-8
            else:assert row['completion_s']==row['energy_kwh']==''
    for r in load(V1/'historical_reference.json'):
        if r['scenario'].endswith('economy'):
            for key in ['C','E']:assert f"{float(r[key]):.3f}" in text
    qa=PROJECT/'.local/contest-baselines-v3-qa';qa.mkdir(exist_ok=True,parents=True);pages=[]
    for i,page in enumerate(doc):
        path=qa/f'page_{i+1:02}.png';page.get_pixmap(matrix=pymupdf.Matrix(1.35,1.35),alpha=False).save(path)
        assert page.get_text().strip()
        pages.append(dict(page=i+1,png=str(path.relative_to(PROJECT)),sha256=digest(path)))
    dump(V3/'DOCUMENT_REVIEW.json',dict(all_numerical_values_verified=True,missing_metrics_preserved=True,
        all_pages_visually_reviewed=False,pages=len(doc),reviewed_pages=pages,pdf_sha256=digest(pdf)))
    print(f'{len(doc)} pages rendered; 16 checkpoint records reconciled, missing metrics remain empty')

def register():
    review=load(V3/'DOCUMENT_REVIEW.json');assert review['all_pages_visually_reviewed'] and review['all_numerical_values_verified']
    assert review['pdf_sha256']==digest(DEST/'援航对齐上限能耗对照报告.pdf')
    checks=load(V3/'aligned_600s_seed42/final_checks.json');assert checks['all_checks_passed']
    path=PROJECT/'docs/task-board.json';raw=path.read_bytes();board=json.loads(raw)
    branch=subprocess.check_output(['git','branch','--show-current'],cwd=PROJECT,text=True,encoding='utf-8').strip()
    task=dict(id='EXP-C03',phase='G6',priority='P1',owner='A',title='对齐Q2/Q3节能返航上限并重跑十分钟基线',
        acceptance='Q2用户确认6000秒；Q3恢复5939.9秒/23运输架次/68.9999kWh合同；8配置各600秒、180/600检查点；超限拒绝、失败不填0；源码冻结、核验与PDF逐页审查；论文方法不重跑',
        dependencies=['EXP-C02'],status='done',branch=branch,pr=None,evidence=[
            'docs/current-project/contest-baselines-v3/对齐实验报告.md','docs/current-project/contest-baselines-v3/完整结果对比.csv',
            'docs/current-project/contest-baselines-v3/援航对齐上限能耗对照报告.pdf','evidence/contest-baselines-v3/aligned_600s_seed42/protocol.json',
            'evidence/contest-baselines-v3/aligned_600s_seed42/final_checks.json','evidence/contest-baselines-v3/DOCUMENT_REVIEW.json'])
    assert all((PROJECT/p).is_file() for p in task['evidence'])
    old=next((t for t in board['tasks'] if t['id']==task['id']),None)
    if old:assert old['title']==task['title'];old.update(task)
    else:board['tasks'].append(task)
    assert path.read_bytes()==raw,'Concurrent task board change; retry'
    path.write_text(json.dumps(board,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    subprocess.run([sys.executable,str(PROJECT/'scripts/render_task_board.py')],cwd=PROJECT,check=True)
    readme=PROJECT/'docs/current-project/README.md';text=readme.read_text(encoding='utf-8')
    if 'contest-baselines-v3/对齐实验报告.md' not in text:
        text+='\n## 对齐返航上限后的能耗对照\n\nEXP-C03按用户确认的Q2上限6000秒、Q3归档合同5939.9秒/运输≤23/总能耗≤68.9999kWh重跑8个能耗配置，每配置600秒。见[完整报告](contest-baselines-v3/对齐实验报告.md)、[PDF](contest-baselines-v3/援航对齐上限能耗对照报告.pdf)和[16检查点结果](contest-baselines-v3/完整结果对比.csv)。未得合规解的记录保留为空，不将超限低能耗方案充当有效结果。论文历史方法未重跑，v1/v2原始实验保留。\n'
        readme.write_text(text,encoding='utf-8')
    manifest=[dict(path=str(p.relative_to(PROJECT)),sha256=digest(p),bytes=p.stat().st_size) for p in DEST.iterdir() if p.is_file()]
    dump(V3/'delivery_manifest.json',dict(task='EXP-C03',files=manifest,paper_method_rerun=False,application_changes=False))
    (V3/'README.md').write_text('# EXP-C03：对齐上限后的能耗实验\n\n'
        '`aligned_600s_seed42/protocol.json`记录Q2用户选择和Q3归档合同、候选与源码指纹。`results.json`/`results.csv`保存8个正式配置、16检查点，失败指标为null/空值。`source_snapshot/`保存正式运行源码。各配置目录保存模型状态、拒绝原因、可行性搜索轨迹以及实际得到的合规方案和独立核验。\n\n'
        '最终报告在docs/current-project/contest-baselines-v3。`DOCUMENT_REVIEW.json`保存PDF跨格式检查及逐页渲染记录。8秒预检不混入正式结果。Q2原始论文精确cap未恢复，6000秒是用户确认的新统一口径；Q3合同原件另存于正式矩阵。全部论文历史方案仅用于报告，未作搜索初解。\n',encoding='utf-8')
    print('Registered EXP-C03 and final delivery hashes')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--register',action='store_true');a=p.parse_args()
    if a.register:register()
    else:audit()
