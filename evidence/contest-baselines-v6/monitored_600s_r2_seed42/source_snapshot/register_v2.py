"""Register only EXP-C02 after all numerical and document checks pass."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
EV=ROOT/'evidence/contest-baselines-v2'
def main():
    review=json.loads((EV/'DOCUMENT_REVIEW.json').read_text(encoding='utf-8'))
    assert review['all_pages_visually_reviewed'] and review['all_numerical_values_verified']
    path=ROOT/'docs/task-board.json';original=path.read_bytes();data=json.loads(original)
    branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True,encoding='utf-8').strip()
    task=dict(id='EXP-C02',phase='G6',priority='P1',owner='A',title='修复贪心并完成Q2/Q3十分钟传统基线矩阵',
        acceptance='16配置各600秒、同次搜索180/600秒检查点；公共可行初解无论文泄漏；32检查点完整核验；旧失败保留；报告/CSV/PDF渲染复核；Q2软硬截止专项复查，论文短时域与本轮无返航上限能耗组明确异条件',
        dependencies=['EXP-C01'],status='done',branch=branch,pr=None,evidence=[
            'docs/current-project/contest-baselines-v2/对比实验报告.md',
            'docs/current-project/contest-baselines-v2/完整结果对比.csv',
            'docs/current-project/contest-baselines-v2/援航十分钟基线对比实验报告.pdf',
            'evidence/contest-baselines-v2/main_600s_seed42/final_checks.json',
            'evidence/contest-baselines-v2/main_600s_seed42/protocol.json',
            'evidence/contest-baselines-v2/DOCUMENT_REVIEW.json',
            'evidence/contest-baselines-v2/q2_alignment_audit/audit.json',
            'evidence/contest-baselines-v2/q2_alignment_audit/复查结论.md'])
    assert all((ROOT/p).is_file() for p in task['evidence'])
    existing=next((t for t in data['tasks'] if t['id']==task['id']),None)
    if existing:
        assert existing['title']==task['title'];existing.update(task)
    else:data['tasks'].append(task)
    assert path.read_bytes()==original,'Concurrent task-board edit; rerun against latest file'
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    subprocess.run([sys.executable,str(ROOT/'scripts/render_task_board.py')],cwd=ROOT,check=True)
    p=ROOT/'docs/current-project/README.md';text=p.read_text(encoding='utf-8')
    if 'contest-baselines-v2/对比实验报告.md' not in text:
        text+='\n## 修复贪心与十分钟对照\n\nEXP-C02完成16配置各600秒的实验，保存同一次搜索的180秒与600秒结果，32检查点通过完整核验。见[完整报告](contest-baselines-v2/对比实验报告.md)、[PDF阅读版](contest-baselines-v2/援航十分钟基线对比实验报告.pdf)与[完整结果表](contest-baselines-v2/完整结果对比.csv)。新版使用多起点贪心及公共可行初解；预算收益按本轮两个检查点比较，v1原始失败记录继续保留。论文历史方案未重跑，当前业务求解器未由本实验修改。\n'
        p.write_text(text,encoding='utf-8')
    if 'q2_alignment_audit/复查结论.md' not in text:
        text+='\nQ2能耗对照已追加[截止条件专项复查](../../evidence/contest-baselines-v2/q2_alignment_audit/复查结论.md)：61.6265kWh方案80箱整站期望延期和31箱硬截止违反均为零，但本轮未设全部返航上限，论文64.7341kWh是有完成时间上限的短时域备选，两者不能作同条件能耗排名。原始实验不变，报告已修正解读。\n'
        p.write_text(text,encoding='utf-8')
    manifest=[dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in (ROOT/'docs/current-project/contest-baselines-v2').iterdir() if p.is_file()]
    (EV/'delivery_manifest.json').write_text(json.dumps(dict(task_id='EXP-C02',files=manifest,our_method_rerun=False,
        application_api_changes=False,application_database_changes=False,old_experiment_preserved=True,
        git_commit_or_push_performed=False),ensure_ascii=False,indent=2),encoding='utf-8')
    (EV/'README.md').write_text('# EXP-C02：修复贪心与十分钟对照\n\n'
        '已完成Q2/Q3 × 时间/能耗 × Greedy/ACO/ALNS/CP-SAT共16配置，每配置600秒，保存同次搜索180秒与600秒检查点。32检查点通过完整核验。\n\n'
        '- `common_initial/manifest.json`：四项贪心重构记录、共享初解与独立核验，未使用论文结果。\n'
        '- `main_600s_seed42/protocol.json`：协议、环境、候选指纹、公共初解和冻结源码指纹。\n'
        '- `main_600s_seed42/source_snapshot/`：正式搜索时的源码副本。\n'
        '- `main_600s_seed42/results.json`、`results.csv`：16配置、32检查点的完整精度指标。\n'
        '- 各配置目录：两份检查点方案、核验明细、发现时刻、完整日志与CP内部状态。\n'
        '- `main_600s_seed42/final_checks.json`：数值、哈希、源文件、检查点时刻与目标不劣核对。\n'
        '- `DOCUMENT_REVIEW.json`：PDF逐页渲染和跨格式数值检查。\n'
        '- `pilot_12s/`：正式矩阵前的10配置短预算预检，单列保留，不混入正式成绩。\n'
        '- `solver_sources.json`：v2 CP回调改动来源。\n\n'
        '完整报告、32行CSV和PDF：`docs/current-project/contest-baselines-v2/`。原v1失败和旧较强方案保留，并在新报告中交叉检查。论文仅作历史参考，未重跑；本轮未改变业务求解器或数据库。\n\n'
        'Q2专项复查：`q2_alignment_audit/复查结论.md`与`audit.json`。软截止未漏、全部整站零延期；论文短时域节能备选与本轮无返航上限的能耗组异条件，不能据数值作同条件能耗优劣排名。先前报告及哈希保留在该审计目录的`prior_report/`。\n',encoding='utf-8')
    print('Registered EXP-C02, preserved all other tasks and appended documentation entry')

if __name__=='__main__':main()
