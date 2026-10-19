"""Summarize confirmed causes; annotate, never replace, the failed formal search."""
import json
from collections import Counter
from pathlib import Path
import py_compile
import subprocess
from datetime import datetime, timezone
from benchmark_v2 import load, digest, V1, V2
from benchmark_v3 import V3
from diagnose_v3 import DEST
from support import PROJECT, dump

def main():
    protocol=load(V3/'aligned_600s_seed42/protocol.json')
    for name,sha in protocol['source_sha256'].items():
        assert digest(PROJECT/'scripts/contest_baselines'/name)==sha, name
    for name,sha in protocol['candidate_sha256'].items():assert digest(V1/name)==sha, name
    ov=load(DEST/'overview.json');q2=load(DEST/'Q2_necessary_relaxation.json');q3=load(DEST/'Q3_necessary_relaxation.json')
    assert q2['status']==q3['status']==0 and q2['gap']==q3['gap']==0
    assert ov['historical_q2_routes_in_pool']==16 and ov['historical_q2_total_routes']==22
    assert all(abs(r['duration_difference_s'])<1e-9 and abs(r['energy_difference_kwh'])<1e-12 for r in ov['historical_q2_route_comparison'])
    positive=load(DEST/'Q2_historical_groups_validation.json')
    assert positive['physical']['summary']['valid'] and positive['station']['late_boxes']==0
    cp=load(DEST/'Q2_historical_groups_positive_control.json')['evidence'][0]
    assert cp['status']=='OPTIMAL' and cp['objective']*.1<=6000
    decoder=[load(p) for p in (V3/'aligned_600s_seed42/Q2_energy_alns/decoders').glob('call*.json')]
    statuses=Counter(e['status'] for r in decoder for e in r['evidence'])
    assert statuses==dict(INFEASIBLE=27,UNKNOWN=16)
    for name in ['diagnose_v3.py','report_v3_diagnosis.py','benchmark_v3.py','master_v2.py','joint_v2.py']:
        py_compile.compile(str(PROJECT/'scripts/contest_baselines'/name),doraise=True)
    import pymupdf
    doc=pymupdf.open(PROJECT/'references/modeling/paper.pdf')
    pages={str(i+1):doc[i].get_text() for i in [48,49,51,60]}
    dump(DEST/'paper_comparison_rules.json',dict(source='references/modeling/paper.pdf',sha256=digest(PROJECT/'references/modeling/paper.pdf'),physical_pages=pages))
    assert '搜索设置' in pages['50'] and '72 kWh' in pages['52'] and '5939.704' in pages['61']
    problem=(DEST/'original_problem.txt').read_text(encoding='utf-8')
    assert '问题三' in problem and '其他物资的期望送达时间用于衡量配送及时性' in problem
    expanded=load(DEST/'expanded_pool_contract.json');exp_cp=load(DEST/'Q2_expanded_feasibility.json')['evidence'][0]
    findings=[
        dict(id='F1',severity='high',scope='Q3 comparison protocol',
            finding='A historical local-improvement energy ceiling (68.9999 kWh) and transport-count ceiling (23) were treated as baseline feasibility requirements.',
            consequence='Worse but otherwise task-feasible comparison solutions are filtered out. The records measure target attainment in a restricted contract, not generic baseline feasibility.',
            evidence=['aligned_600s_seed42/historical_q3_input_contract.json','scripts/contest_baselines/benchmark_v3.py:17','failure_diagnosis/paper_comparison_rules.json','failure_diagnosis/original_problem.txt'],
            correction='For intended minimum-energy comparison retain the declared shared time horizon and all original physics/resources/zero-late rules; report energy and sorties as outputs. Do not impose paper-derived E/N target ceilings.'),
        dict(id='F2',severity='high',scope='Q2/Q3 candidate space',
            finding='Fixed 850-route pool lacks batch/subset closure and route regeneration. Only 16/22 historical Q2 energy routes are represented.',
            evidence=['failure_diagnosis/overview.json','failure_diagnosis/Q2_necessary_relaxation.json'],
            consequence='Even the relaxed fixed-pool minimum energy exceeds the historical Q2 plan; no method can recover routes absent from its representation.',
            correction='Generate a shared independent pool with reliable subset/complement coverage; allow method-appropriate insertion/regrouping. Establish a cap-feasible positive control before full comparisons; do not seed baseline searches with the historical answer.'),
        dict(id='F3',severity='high',scope='constructive search',
            finding='Greedy/ACO constructors favor local energy and EDF list feasibility without residual fleet-work/count/energy-cap viability repair. ALNS also remains inside the same sparse columns.',
            evidence=['failure_diagnosis/overview.json','scripts/contest_baselines/benchmark.py','scripts/contest_baselines/benchmark_v2.py','scripts/contest_baselines/benchmark_v3.py'],
            consequence='Q2 Greedy/ACO and all Q3 heuristics make zero CP decoder calls; many complete constructions are rejected by necessary bounds. Repeating starts cannot correct missing routes.',
            correction='Use a phase-I feasible construction/repair objective under shared horizon before energy minimization; test its feasibility without borrowing paper schedules. Track independent E/N/work causes and decoder reachability.'),
        dict(id='F4',severity='medium',scope='solver workflow and interpretation',
            finding='Cold optimization starts without any cap-feasible incumbent; total pre-scheduling attempts were previously easy to mistake for useful optimization iterations.',
            evidence=['failure_diagnosis/Q2_feasibility_first_cp.json','failure_diagnosis/Q2_expanded_feasibility.json'],
            consequence='600 s UNKNOWN does not identify infeasibility or a code crash. Short feasibility-only/expanded probes also remain UNKNOWN; no single-setting fix is demonstrated.',
            correction='Separate phase-I feasibility and phase-II improvement, surface phases and solver states. Withhold numerical superiority claims until a verified feasible baseline exists.')]
    dump(DEST/'diagnosis.json',dict(task='EXP-C04',formal_run_modified=False,source_and_pool_fingerprints_unchanged=True,
        original_search_records_retained=True,findings=findings,
        q2_positive_control_solver_s=cp['wall_time'],q2_positive_control_grid_completion_s=cp['objective']*.1,
        historical_control_is_baseline_result=False,independent_expansion_is_formal_result=False,
        q2_restricted_relaxed_energy_floor_kwh=q2['energy_kwh'],q3_restricted_relaxed_transport_energy_floor_kwh=q3['energy_kwh'],
        q2_alns_decoder_statuses=dict(statuses),q2_alns_decoder_wall_s=sum(e['wall_time'] for r in decoder for e in r['evidence']),
        finite_pool_infeasibility_proved=False,next_formal_rerun_performed=False,
        intended_corrected_caps=dict(Q2=dict(C=6000,E=None,N=None),Q3=dict(C=5939.9,E=None,N=None)),
        remaining='No cap-feasible independent baseline has been demonstrated. Candidate generation and phase-I search need repair before a replacement full benchmark.'))
    review=dict(schema_version=1,question_id='Q2/Q3',language='python',reviewed_files=[dict(path=str((PROJECT/'scripts/contest_baselines'/n).relative_to(PROJECT)),sha256=digest(PROJECT/'scripts/contest_baselines'/n)) for n in protocol['source_sha256']],decision_id='EXP-C03_user_horizon_alignment',
        checks=dict(syntax=dict(status='PASS',evidence=['Selected runners and diagnostic scripts compile; formal eight runs terminated without errors.']),
            input_contract=dict(status='PASS',evidence=['Historical Q2 22/22 physical route durations and energy match exactly; source and candidate hashes unchanged.']),
            method_alignment=dict(status='FAIL',evidence=['Q3 local E/N search ceilings are additional outcome filters; public finite candidate representation and construction viability are insufficient for intended baseline comparison.']),
            reproducibility=dict(status='PASS',evidence=['Frozen 15-source and four-candidate digests match; fixed seed logs preserved.']),
            output_contract=dict(status='FAIL',evidence=['Missing metrics and UNKNOWN states correctly recorded, but no usable feasible numerical baseline produced for requested comparison.'])),
        findings=findings,verdict='CHANGES_REQUIRED_FOR_COMPARATIVE_CLAIMS',reviewed_at=datetime.now(timezone.utc).isoformat())
    dump(DEST/'python_review.json',review)
    text=f'''# EXP-C04：对齐上限实验全失败的原因排查

排查结论：这轮对照的协议和实现设计存在问题，不能将全失败主要解释为“传统算法搜索10分钟也做不到”。正式记录真实、未被替换，但不应作为证明本方法优于传统算法的有效对照。

## 1. Q3多加了结果导向的约束

`benchmark_v3.py`把历史局部改进合同中的`max_E=68.9999`、`max_transport=23`放进统一合规检查和必要条件剪枝。这两个值不是原题的能耗、运输架次硬上限。原题要求优化并报告这些指标；论文第5.2.4节明确称总时间与总能耗上界为“搜索设置”，第5.3.3节的时间主方案最终一轮实际上采用5940秒、72kWh（PDF物理第52页）；99分钟节能备选见第5.5节表5.14（物理第61页）。v3取到的是归档某轮节能改进合同，不等于所有对照方法均须达到的原题标准。

若基线在相同返航时域内有效，但能耗高于69kWh或运输多于23架次，本来应该记录其较差的指标；v3会直接拒绝。数学上v3确实运行了一个额外受限的目标达成实验，但它没有完整回答用户要求的能耗对照问题。Q3四个失败只能表述为“在有限池与预算内未达到这组额外上限”，不能转述为原题没有有效方案。

后续正确比较保留已声明的共同返航时域（Q2≤6000秒、Q3≤5939.9秒）、整站零期望延期、31箱硬截止及全部物理/通信/资源条件；以能耗最小为目标，架次数随结果报告，取消根据论文已得解设置的总能耗与运输架次硬筛选。两个时域仍是本实验设定，不称原题的固定数值要求。

## 2. 公共路线池缺少关键的合法组批

当前850条路线中，单站539条、双站293条、三站18条。论文Q2节能方案22条路线只有16条在池内，另6条不在池内。22条路线用当前物理函数逐条重算，时长与能耗差均为0；缺少的路线并非被物理约束正确剔除，而是没有生成。

对这850条路线，保留80箱唯一覆盖和分机型总工作量≤机数×6000秒，放松实际排程、全部截止、充电及通信后，整数模型最小能耗仍为 **{q2['energy_kwh']:.6f}kWh**（HiGHS返回OPTIMAL，gap=0）。这个比完整问题更宽松的有限池下界仍高于论文节能方案64.734132kWh。因此，固定池里不可能恢复论文的这套能耗水平。该证据不证明固定池在6000秒内完全无解，更不证明原题无解。

Q3相应的运输部分必要条件松弛，在原v3的23架次/68.9999kWh目标限制下最低为{q3['energy_kwh']:.6f}kWh；它尚未加入中继耗能和连续通信，不能当作完整联合方案。

## 3. 启发式没有有效走到可行排程阶段

|配置|构造尝试|调用CP排程|关键现象|
|---|---:|---:|---|
|Q2 贪心|299016|0|185688次构造死路，其余113328次被机队工作量必要条件拒绝|
|Q2 ACO|305041|0|254515次死路，其余50526次被工作量拒绝|
|Q2 ALNS|197034|43|27次有限排程模型INFEASIBLE、16次UNKNOWN；CP累计约392.85秒|
|Q3 贪心|356618|0|构造死路或工作量/能耗/架次目标筛选；有重复路线组跳过|
|Q3 ACO|377584|0|同上|
|Q3 ALNS|634424|0|同上|

现有贪心/ACO仍主要按局部单位能耗选择路线、按EDF串行试排，没有修复剩余任务对各机型工作量的需求；ACO只在局部评分前10个候选中选取。ALNS可破坏、重建已有路线组合，但不能生成池外的新箱组/路线。大量尝试意味着大量受限构造，并不意味着进行了同等次数的有效能耗改进。合法的工作量下界剪枝本身没有发现误写，问题出在到达剪枝处的候选长期不可排，以及Q3多加了E/N筛选。

## 4. 正向控制与有限诊断

仅把论文Q2的22条路线组交给同一个CP排程器，**不提供原排程或初解**，{cp['wall_time']:.3f}秒求得网格返航{cp['objective']*.1:.3f}秒的排程；原始连续时长、资源与整站时限复核通过。这是排程器可接受有效方案的正向诊断，使用了历史路线组，**不得冒充独立基线或公平初解**。

另外进行了以下短诊断，均不混入600秒正式结果：原850路线取消优化目标、4线程可行性搜索45秒，UNKNOWN；整路线分配到具体飞机的必要装箱松弛各30秒，均UNKNOWN；独立枚举各站非空子集并保留原路线，将池扩为{expanded['expanded_size']}条（生成约{expanded['preparation_s']:.3f}秒），配置60秒的可行性冷启动也未得解，求解器实际返回耗时{exp_cp['wall_time']:.3f}秒。扩大候选后模型更大，不能据此声称已修好可行构造，也不能把UNKNOWN改写成无解。

未发现支持“软截止漏掉导致本轮全失败”的证据：整站全部期望零延期一直强制保留，31箱硬截止也保留。物理参数与历史方案的重算一致。但这些局部检查不等于给整个实验实现作无缺陷保证。

## 5. 处理结论

1. v3原始协议、源码快照、16检查点和PDF保留，统一标记为额外目标限制下的失败搜索记录；撤回其作为正式算法优劣对照的适用性。
2. 当前不重复花80分钟累计预算。先取消Q3的结果门槛，补足独立候选的箱组/补集组合，并把可行性构造与能耗改进分为两阶段。
3. 新协议必须先证明至少有独立生成、完整核验且满足共同返航时域的普通初解，并记录预处理耗时及公平使用方式；这一步未完成前不启动新的整组10分钟实验。
4. 原题物理与交付要求保持；论文方法仍只引用历史结果，不重跑，也不把答案作为基线搜索输入。

诊断不支持固定池完全不可行、算法普遍劣于论文或任何能耗提升百分比。修复后的正式对照尚未执行。

## 复核入口

- `evidence/contest-baselines-v3/failure_diagnosis/diagnosis.json`：确认问题与更正口径。
- `python_review.json`：代码审查结论，比较用途为CHANGES_REQUIRED。
- `overview.json`、两个`*_necessary_relaxation.json`：候选重算与必要条件证据。
- `Q2_historical_groups_positive_control.json`、`Q2_historical_groups_validation.json`：正向控制与独立核验。
- `paper_comparison_rules.json`、`original_problem.txt`：本次读取的论文/原题依据。
- `scripts/contest_baselines/diagnose_v3.py`：各项诊断入口；均为诊断，不能当作新的基线成绩。
'''
    report=PROJECT/'docs/current-project/contest-baselines-v3/全失败原因排查.md';report.write_text(text,encoding='utf-8')
    notice=dict(formal_records_unchanged=True,accepted_for_algorithm_superiority_comparison=False,
        reinterpretation='Restricted local-target search failures, not a usable baseline benchmark.',
        superseding_audit=str(report.relative_to(PROJECT)),issues=['Q3 uses outcome-target E/N caps','candidate space inadequacy','construction feasibility not established'])
    dump(V3/'COMPARISON_STATUS.json',notice)
    boardpath=PROJECT/'docs/task-board.json';raw=boardpath.read_bytes();board=json.loads(raw)
    task=next(t for t in board['tasks'] if t['id']=='EXP-C04');task.update(status='done',evidence=[str(report.relative_to(PROJECT)),
        'evidence/contest-baselines-v3/failure_diagnosis/diagnosis.json','evidence/contest-baselines-v3/failure_diagnosis/python_review.json',
        'evidence/contest-baselines-v3/COMPARISON_STATUS.json','scripts/contest_baselines/diagnose_v3.py'])
    assert boardpath.read_bytes()==raw
    boardpath.write_text(json.dumps(board,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    subprocess.run([str(PROJECT/'.venv/Scripts/python.exe'),str(PROJECT/'scripts/render_task_board.py')],cwd=PROJECT,check=True)
    readme=PROJECT/'docs/current-project/README.md';body=readme.read_text(encoding='utf-8')
    if 'contest-baselines-v3/全失败原因排查.md' not in body:
        body+='\n## 对齐实验的后续排查（EXP-C04）\n\n**v3不可作为正式算法优劣对照。** [原因排查与更正](contest-baselines-v3/全失败原因排查.md)确认：Q3误将局部搜索的能耗/运输架次目标作为所有基线的合规门槛，路线候选及可行性构造也不足。原始16检查点与PDF作为失败搜索记录保留；修复后的正式对照尚未执行。状态见`evidence/contest-baselines-v3/COMPARISON_STATUS.json`。\n'
        readme.write_text(body,encoding='utf-8')
    dump(DEST/'manifest.json',dict(task='EXP-C04',formal_sources_and_candidates_unchanged=True,
        report=dict(path=str(report.relative_to(PROJECT)),sha256=digest(report)),
        files=[dict(path=str(p.relative_to(PROJECT)),sha256=digest(p)) for p in sorted(DEST.iterdir()) if p.is_file() and p.name!='manifest.json']))
    print('EXP-C04 diagnosis saved; comparison status corrected; original formal records unchanged.')

if __name__=='__main__':main()
