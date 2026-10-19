"""Register the completed experiment without changing any other project tasks."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]

def main():
    evidence=ROOT/'evidence/contest-baselines-v1'
    layout=json.loads((evidence/'DOCUMENT_REVIEW.json').read_text(encoding='utf-8'))
    assert layout['all_pages_visually_reviewed']
    path=ROOT/'docs/task-board.json'
    raw=path.read_bytes();data=json.loads(raw.decode('utf-8'))
    branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True,encoding='utf-8').strip()
    task=dict(id='EXP-C01',phase='G6',priority='P1',owner='A',
        title='原题Q2/Q3时间与能耗传统方法限时对照',
        acceptance='四类基线、统一整站计时和完整约束；180秒单种子原始结果与失败保留；论文结果只作历史参考；独立核验、结果表和5页PDF实际渲染检查',
        dependencies=['A-01'],status='done',branch=branch,pr=None,
        evidence=['docs/current-project/contest-baselines-v1/对比实验报告.md',
            'docs/current-project/contest-baselines-v1/援航限时基线对比实验报告.pdf',
            'docs/current-project/contest-baselines-v1/完整结果对比.csv',
            'evidence/contest-baselines-v1/matrix_180s_seed42/final_checks.json',
            'evidence/contest-baselines-v1/cp_energy_warm_180s/final_checks.json',
            'evidence/contest-baselines-v1/DOCUMENT_REVIEW.json'])
    assert all((ROOT/p).is_file() for p in task['evidence'])
    assert path.read_bytes()==raw,'Task board changed during read; retry with the new contents.'
    existing=next((t for t in data['tasks'] if t['id']==task['id']),None)
    if existing:
        assert existing['title']==task['title'],'Task ID already belongs to another task'
        existing.update(task)
    else:data['tasks'].append(task)
    data['updated']='2026-10-19'
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    subprocess.run([sys.executable,str(ROOT/'scripts/render_task_board.py')],cwd=ROOT,check=True)
    readme=ROOT/'docs/current-project/README.md'
    text=readme.read_text(encoding='utf-8')
    if 'contest-baselines-v1/对比实验报告.md' not in text:
        text+='\n## 论文历史方案与传统基线对照\n\n2026年10月19日完成Q2/Q3两目标限时实验，见[完整报告](contest-baselines-v1/对比实验报告.md)、[5页PDF阅读版](contest-baselines-v1/援航限时基线对比实验报告.pdf)及[完整结果表](contest-baselines-v1/完整结果对比.csv)。这是独立补充材料，没有把论文历史结果冒充当前V4引擎的运行值；原主文档与32页Word保持原基线。本次Word草稿因Office最终样式导出阻塞未交付，PDF已逐页核验。\n'
        readme.write_text(text,encoding='utf-8')
    manifest=[]
    for p in (ROOT/'docs/current-project/contest-baselines-v1').iterdir():
        if p.is_file() and not p.name.startswith('~$'):
            manifest.append(dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    (evidence/'delivery_manifest.json').write_text(json.dumps(dict(task_id='EXP-C01',branch=branch,files=manifest,
        application_api_changes=False,application_database_changes=False,our_method_rerun=False,word_delivered=False,
        note='Original main matrix and both warm-start CP supplements retained; no commit or push performed by this task.'),ensure_ascii=False,indent=2),encoding='utf-8')
    print('Registered EXP-C01 and documentation links')

if __name__=='__main__':main()
