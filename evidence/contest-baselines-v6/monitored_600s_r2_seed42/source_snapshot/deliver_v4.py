"""Audit rendered PDF and register the final, visually reviewed EXP-C05 delivery."""
import argparse
import csv
import json
import subprocess
import sys
import pymupdf
from pattern_v4 import V4
from benchmark_v2 import load,digest
from support import PROJECT,dump

DEST=PROJECT/'docs/current-project/contest-baselines-v4';PDF=DEST/'援航修正后十分钟能耗对照报告.pdf'

def audit():
    content=load(V4/'report_content.json');doc=pymupdf.open(PDF);text=''.join(p.get_text() for p in doc).replace(' ','').replace('\n','')
    rows=list(csv.DictReader((DEST/'完整结果对比.csv').open(encoding='utf-8-sig')));assert len(rows)==16
    runs=load(V4/'corrected_600s_seed42/results.json')
    for r in runs:
        for c in r['checkpoints']:
            row=next(x for x in rows if x['question']==r['question'] and x['method']==r['method'] and float(x['checkpoint_s'])==c['checkpoint_s'])
            for k in ['energy_kwh','completion_s','transport_sorties','relay_sorties']:assert abs(float(row[k])-c['metrics'][k])<1e-8
            assert f"{c['metrics']['energy_kwh']:.6f}" in text
            if c['checkpoint_s']==600:assert f"{c['metrics']['completion_s']:.3f}" in text
    for s in content['summaries']:
        assert f"{s['paper_E']:.6f}" in text and f"{s['paper_C']:.3f}" in text
    qa=PROJECT/'.local/contest-baselines-v4-qa';qa.mkdir(exist_ok=True,parents=True);pages=[]
    for i,p in enumerate(doc):
        assert p.get_text().strip();path=qa/f'page_{i+1:02}.png';p.get_pixmap(matrix=pymupdf.Matrix(1.35,1.35),alpha=False).save(path)
        pages.append(dict(page=i+1,png=str(path.relative_to(PROJECT)),sha256=digest(path)))
    dump(V4/'DOCUMENT_REVIEW.json',dict(pdf_sha256=digest(PDF),all_numerical_values_verified=True,all_pages_visually_reviewed=False,pages=len(doc),reviewed_pages=pages))
    print(len(doc),'pages rendered; 16 CSV records and displayed numbers reconciled')

def register():
    review=load(V4/'DOCUMENT_REVIEW.json');assert review['all_pages_visually_reviewed'] and review['all_numerical_values_verified'] and review['pdf_sha256']==digest(PDF)
    assert load(V4/'corrected_600s_seed42/final_checks.json')['all_checks_passed']
    p=PROJECT/'docs/task-board.json';raw=p.read_bytes();board=json.loads(raw);task=next(t for t in board['tasks'] if t['id']=='EXP-C05')
    task.update(status='done',title='修正约束并补齐十分钟能耗对照及停滞审计',acceptance='保留原5组，按用户要求以冻结源码/输入补跑其余3组各600秒；8配置、16检查点核验；相同66.134明确为保留公共初解，非各方法独立收敛；旧版时间目标8组已完成且版本局限披露；不再优化算法；PDF逐页检查；论文方法未重跑',
        evidence=['docs/current-project/contest-baselines-v4/对比实验报告.md','docs/current-project/contest-baselines-v4/完整结果对比.csv',
            'docs/current-project/contest-baselines-v4/援航修正后十分钟能耗对照报告.pdf','evidence/contest-baselines-v4/corrected_600s_seed42/protocol.json',
            'evidence/contest-baselines-v4/corrected_600s_seed42/final_checks.json','evidence/contest-baselines-v4/python_review.json','evidence/contest-baselines-v4/DOCUMENT_REVIEW.json',
            'evidence/contest-baselines-v4/corrected_600s_seed42/resume_manifest.json','evidence/contest-baselines-v4/stagnation_audit.json',
            'docs/current-project/contest-baselines-v4/时间最短历史结果_v2.csv'])
    assert all((PROJECT/f).is_file() for f in task['evidence']);assert raw==p.read_bytes()
    p.write_text(json.dumps(board,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');subprocess.run([sys.executable,str(PROJECT/'scripts/render_task_board.py')],cwd=PROJECT,check=True)
    readme=PROJECT/'docs/current-project/README.md';body=readme.read_text(encoding='utf-8')
    if 'contest-baselines-v4/对比实验报告.md' not in body:
        body+='\n## 修正后的十分钟能耗对照（EXP-C05）\n\n[报告](contest-baselines-v4/对比实验报告.md)、[CSV](contest-baselines-v4/完整结果对比.csv)、[PDF](contest-baselines-v4/援航修正后十分钟能耗对照报告.pdf)。取消Q3局部能耗/运输架次目标门槛，先独立构造并验证公共初解，再运行每配置最多600秒的追加搜索。8配置、16检查点全部核验；公共初解和准备耗时单列，未改善者明确为保留初解。历史论文预算与候选空间未对齐，不将方案数值差直接写成算法公平增益。v3作为额外目标限制下的失败记录保留。\n'
        readme.write_text(body,encoding='utf-8')
    dump(V4/'delivery_manifest.json',dict(task='EXP-C05',files=[dict(path=str(f.relative_to(PROJECT)),sha256=digest(f),bytes=f.stat().st_size) for f in DEST.iterdir() if f.is_file()],
        paper_method_rerun=False,application_changes=False,shared_initialization_disclosed=True))
    (V4/'README.md').write_text('# EXP-C05：修正后的共同初始化能耗对照\n\n正式矩阵为`corrected_600s_seed42/`，8配置、16检查点；源码/候选指纹、原始方案、独立核验与完整日志保留。每配置600秒为共同初始化后的追加搜索上限，有限模型已证最优可提前停止。`preparation/`保留独立模式构造、失败预检、驻点、窗口模板、悬停收紧和网格检查。短预演不混入正式结果。\n\n报告在docs/current-project/contest-baselines-v4；所有数值由正式结果生成。历史论文只作已有方案参考，未作为搜索输入、未重跑。共享初解的成绩不是各纯启发式从零取得的成绩。\n',encoding='utf-8')
    print('EXP-C05 registered; delivery hashes saved')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--register',action='store_true');a=p.parse_args();register() if a.register else audit()
