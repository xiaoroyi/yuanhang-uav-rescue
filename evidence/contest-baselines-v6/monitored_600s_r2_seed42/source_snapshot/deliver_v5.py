"""Reconcile exported numbers, render PDF, and register only after visual review."""
import argparse
import csv
import json
import subprocess
import sys
import pymupdf
from report_v5 import BASE, DEST
from benchmark_v5 import V5
from benchmark_v2 import load, digest
from support import PROJECT, dump

PDF=DEST/'援航四组无初解十分钟对比报告.pdf'

def audit():
    content=load(V5/'report_content.json');doc=pymupdf.open(PDF)
    text=''.join(p.get_text() for p in doc).replace(' ','').replace('\n','')
    csvrows=list(csv.DictReader((DEST/'四组各方法完整结果.csv').open(encoding='utf-8-sig')))
    assert len(csvrows)==32
    for r in load(BASE/'results.json'):
        for c in r['checkpoints']:
            row=next(row for row in csvrows if (row['question'],row['objective'],row['method'],float(row['checkpoint_s']))==
                (r['question'],r['objective'],r['method'],c['checkpoint_s']))
            assert row['status']==c['status']
            if c['metrics'] is None:
                assert row['energy_kwh']==row['completion_s']==''
            else:
                for k in ['energy_kwh','completion_s','transport_sorties','relay_sorties']:
                    assert abs(float(row[k])-c['metrics'][k])<1e-8
                if c['checkpoint_s']==600:
                    assert f"{c['metrics']['energy_kwh']:.6f}" in text
                    assert f"{c['metrics']['completion_s']:.3f}" in text
    for row in content['rows']:
        for value in row[1:]:assert value.replace(' ','') in text,value
    qa=PROJECT/'.local/contest-baselines-v5-qa';qa.mkdir(exist_ok=True,parents=True);pages=[]
    for i,p in enumerate(doc):
        assert p.get_text().strip();path=qa/f'page_{i+1:02}.png'
        p.get_pixmap(matrix=pymupdf.Matrix(1.35,1.35),alpha=False).save(path)
        pages.append(dict(page=i+1,path=str(path.relative_to(PROJECT)),sha256=digest(path)))
    dump(V5/'DOCUMENT_REVIEW.json',dict(pdf_sha256=digest(PDF),pages=len(doc),
        all_numerical_values_verified=True,all_pages_visually_reviewed=False,rendered_pages=pages))
    print(len(doc),'pages rendered; 32 CSV checkpoints reconciled')

def register():
    review=load(V5/'DOCUMENT_REVIEW.json');checks=load(BASE/'final_checks.json')
    assert review['all_pages_visually_reviewed'] and review['all_numerical_values_verified'] and digest(PDF)==review['pdf_sha256']
    assert checks['all_checks_passed'] and checks['completed_configurations']==16
    p=PROJECT/'docs/task-board.json';raw=p.read_bytes();board=json.loads(raw)
    t=next(t for t in board['tasks'] if t['id']=='EXP-C06')
    t.update(status='done',acceptance='四组×4方法全部从头完成最多600秒搜索；无公共初解/外部暖启动；有解独立核验、未得解留空；原始日志/冻结源码/哈希保留；CSV及PDF核对并逐页检查；论文只作历史参考。',
        evidence=['docs/current-project/contest-baselines-v5/对比实验报告.md',
            'docs/current-project/contest-baselines-v5/四组600秒结果.csv',
            'docs/current-project/contest-baselines-v5/援航四组无初解十分钟对比报告.pdf',
            'evidence/contest-baselines-v5/independent_600s_seed42/protocol.json',
            'evidence/contest-baselines-v5/independent_600s_seed42/final_checks.json',
            'evidence/contest-baselines-v5/python_review.json','evidence/contest-baselines-v5/DOCUMENT_REVIEW.json'])
    assert all((PROJECT/path).is_file() for path in t['evidence']);assert p.read_bytes()==raw
    p.write_text(json.dumps(board,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    subprocess.run([sys.executable,str(PROJECT/'scripts/render_task_board.py')],cwd=PROJECT,check=True)
    readme=PROJECT/'docs/current-project/README.md';text=readme.read_text(encoding='utf-8')
    if 'contest-baselines-v5/对比实验报告.md' not in text:
        text+='\n## 四组无公共初解的独立对比（EXP-C06，最新口径）\n\n按用户要求，Q2/Q3×时间/能耗共4组，每组Greedy/EDF、ACO、ALNS、CP-SAT独立从头搜索最多600秒，不供应公共可行初解或外部暖启动。16配置全部完成搜索；有解方案独立核验，未得解留空，不以旧方案补分。见[报告](contest-baselines-v5/对比实验报告.md)、[四组结果CSV](contest-baselines-v5/四组600秒结果.csv)、[PDF](contest-baselines-v5/援航四组无初解十分钟对比报告.pdf)。能耗组Q2返航≤6000秒、Q3≤5939.9秒；物理、整站零延期及Q3连续通信口径保持。论文只作历史方案参考。旧版实验及中断日志保留，不混入本轮结果。\n'
        readme.write_text(text,encoding='utf-8')
    dump(V5/'CURRENT_RESULT_STATUS.json',dict(status='completed',completed_configurations=16,
        feasible_final_runs=checks['feasible_final_runs'],no_feasible_final_runs=checks['no_feasible_final_runs'],
        supplied_initial_solution=False,supplied_warm_start=False,paper_method_rerun=False))
    dump(V5/'delivery_manifest.json',dict(task='EXP-C06',files=[dict(path=str(p.relative_to(PROJECT)),
        sha256=digest(p),bytes=p.stat().st_size) for p in DEST.iterdir() if p.is_file()],
        supplied_initial_solution=False,application_changes=False,paper_method_rerun=False))
    (V5/'README.md').write_text('# 四组无初解独立对比\n\n正式矩阵：`independent_600s_seed42/`。Q2/Q3×时间/能耗×4种方法共16配置；各自从空方案开始，最多600秒。输入为相同物理候选路线与驻点，无公共可行排程、无外部暖启动。未得解状态保留为空。`smoke/`仅为运行检查，不充当正式结果。报告、CSV和PDF在`docs/current-project/contest-baselines-v5/`。\n',encoding='utf-8')
    print('EXP-C06 registered; final delivery complete')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--register',action='store_true');a=p.parse_args()
    register() if a.register else audit()
