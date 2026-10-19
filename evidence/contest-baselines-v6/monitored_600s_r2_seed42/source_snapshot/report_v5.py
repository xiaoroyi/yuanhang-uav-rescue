"""Verify all independent runs and report actual results, including missing solutions."""
import csv
from datetime import datetime, timezone
from pathlib import Path
import py_compile
from benchmark_v2 import load, digest, solution_metrics, key, V1
from benchmark_v5 import V5
from pattern_v4 import V4
from support import PROJECT, dump, table

BASE=V5/'independent_600s_seed42'
DEST=PROJECT/'docs/current-project/contest-baselines-v5'
METHODS=['greedy','aco','alns','cp_sat']
LABEL={'greedy':'Greedy / EDF','aco':'ACO','alns':'ALNS','cp_sat':'CP-SAT'}
GROUPS=[('Q2','time'),('Q2','energy'),('Q3','time'),('Q3','energy')]

def mdtable(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']+
        ['| '+' | '.join(map(str,row))+' |' for row in rows])

def main():
    protocol=load(BASE/'protocol.json');completion=load(BASE/'completion.json');runs=load(BASE/'results.json')
    assert completion['complete'] and completion['completed_runs']==16 and not completion['errors']
    assert len(runs)==16 and len({(r['question'],r['objective'],r['method']) for r in runs})==16
    assert protocol['supplied_initial_solution'] is protocol['supplied_warm_start'] is protocol['paper_solution_used'] is False
    for name,sha in protocol['source_sha256'].items():
        p=PROJECT/'scripts/contest_baselines'/name
        assert digest(p)==sha and digest(BASE/'source_snapshot'/name)==sha,name
        py_compile.compile(str(p),doraise=True)
    for name,sha in protocol['candidate_sha256'].items():assert digest(V4/name)==sha,name
    preserved=V4/'corrected_600s_seed42/preserved_five_run_hashes.json'
    if preserved.exists():
        for name,sha in load(preserved).items():assert digest(preserved.parent/name)==sha,name
    historical={r['scenario']:r for r in load(V1/'historical_reference.json')}
    csvrows=[];audits=[];detail=[];solver_records=[];missing=[]
    for r in runs:
        q,o,m=r['question'],r['objective'],r['method'];path=BASE/f'{q}_{o}_{m}'
        assert r['budget_s']==600 and r['seed']==42 and r['status']=='COMPLETED'
        assert r['supplied_initial_solution'] is r['supplied_warm_start'] is r['paper_solution_used'] is False
        assert r['completion_cap_s']==(protocol['energy_caps'][q] if o=='energy' else None)
        assert [c['checkpoint_s'] for c in r['checkpoints']]==[180.,600.]
        previous=None
        for t in r['trace']:
            assert 0<=t['found_s']<=600+1e-6
            assert t['origin'].startswith('independent_'),t['origin']
        for c in r['checkpoints']:
            p=path/f"checkpoint_{c['checkpoint_s']:g}s_solution.json"
            if c['metrics'] is None:
                assert c['status']=='NO_FEASIBLE_SOLUTION_FOUND' and c['solution_sha256'] is None
                assert not p.exists()
                metrics=dict(completion_s=None,energy_kwh=None,transport_sorties=None,relay_sorties=None,
                    boxes=None,unique_boxes=None,late_boxes=None,hard_violations=None,minimum_hard_slack_s=None)
            else:
                assert c['status']=='VALIDATED_FEASIBLE' and c['best_found_s']<=c['checkpoint_s']+1e-6
                assert digest(p)==c['solution_sha256']
                sol=load(p);metrics=c['metrics'];physical=solution_metrics(sol)
                assert all(abs(physical[k]-metrics[k])<1e-8 for k in physical)
                score=key(sol,o)
                if previous is not None:assert score<=previous
                previous=score
                if o=='energy':assert metrics['completion_s']<=protocol['energy_caps'][q]+1e-6
                audit=load(path/f"checkpoint_{c['checkpoint_s']:g}s_validation.json")
                assert audit['status']=='passed' and audit['solution_sha256']==digest(p)
                station=audit['station']
                assert station['boxes']==station['unique_boxes']==80
                assert station['late_boxes']==station['hard_violations']==0
                assert audit['transport']['summary']['valid']
                if q=='Q3':
                    radio=audit['radio']['summary']
                    assert radio['valid'] and radio['gap_seconds']==radio['unknown_intervals']==0
                audits.append(dict(question=q,objective=o,method=m,checkpoint_s=c['checkpoint_s'],solution_sha256=digest(p)))
            csvrows.append(dict(question=q,objective=o,method=m,checkpoint_s=c['checkpoint_s'],status=c['status'],
                **metrics,search_wall_s=r['search_wall_s'],best_found_s=c['best_found_s'],
                initial_solution_supplied=False,warm_start_supplied=False,solution_sha256=c['solution_sha256']))
        evidence_path=path/'cp_evidence.json' if q=='Q2' else path/'decoders/full_pool/solver_evidence.json'
        evidence=[]
        if m=='cp_sat' and evidence_path.exists():
            ev=load(evidence_path);evidence=ev['evidence'] if isinstance(ev,dict) else ev
            solver_records.append(dict(question=q,objective=o,evidence=evidence))
        final=r['checkpoints'][-1]
        if final['metrics'] is None:missing.append(dict(question=q,objective=o,method=m,
            attempts=r['attempts'],complete_constructions=r['complete_constructions'],decoder_calls=r['decoder_calls'],
            rejections=r['rejections'],solver_evidence=evidence))
        detail.append(dict(question=q,objective=o,method=m,metrics=final['metrics'],status=final['status'],
            attempts=r['attempts'],complete_constructions=r['complete_constructions'],decoder_calls=r['decoder_calls'],
            first_feasible_s=r['trace'][0]['found_s'] if r['trace'] else None,
            search_wall_s=r['search_wall_s'],trace_count=len(r['trace']),solver_evidence=evidence))
    headers=['方法','Q2最短时间 / s','Q2最低能耗 / kWh','Q3最短时间 / s','Q3最低能耗 / kWh']
    rows=[]
    for m in METHODS:
        row=[LABEL[m]]
        for q,o in GROUPS:
            r=next(r for r in detail if (r['question'],r['objective'],r['method'])==(q,o,m))
            v=r['metrics'];row.append('预算内未找到' if v is None else f"{v['completion_s']:.3f}" if o=='time' else f"{v['energy_kwh']:.6f}")
        rows.append(row)
    rows.append(['论文历史方案（未重跑）']+[f"{float(historical[q+('_fast' if o=='time' else '_economy')]['C' if o=='time' else 'E']):.{3 if o=='time' else 6}f}" for q,o in GROUPS])
    rules=[
        '四组各4种方法，共16配置；各自从空方案开始，独立最多600秒，种子42。不供应公共可行初解，不导入论文方案，不传外部暖启动。ALNS在自己的预算内构造首个解，成功后才能进行邻域搜索。',
        'Q2最低能耗组全部返航≤6000秒（用户指定的新统一对照口径）；Q3最低能耗组运输与中继联合返航≤5939.9秒。无能耗或运输架次结果门槛。时间目标组以联合返航时间为目标，不再加节能方案的返航上限。',
        '四组均要求80箱整站零期望延期、31箱硬截止；质量、体积、DEM航段、逐段载荷能耗、SOC≥20%、8运输机、14电池及两阶段充电保持；Q3另保持2中继机/6组件并核验连续通信。',
        '四种方法使用相同物理路线候选；每题272条具体箱号路线、154个独立驻点、Q3最多6个计算架次槽。复用的是路线/驻点物理数据，未导入任何完整可行排程；没有继续调优或为得到差异而更改结果。',
        'Greedy/EDF为多起点随机评分构造；ACO使用路线信息素；ALNS采用三类移除与自适应权重；Q3三者均用CP完成资源/通信排程解码，因此为本问题的适配实现。CP-SAT直接求解相同有限路线/驻点空间。',
        '输入加载和物理候选预计算在搜索计时前；首个解构造、CP建模、排程解码、搜索及中间写盘都计入600秒。最终独立核验另计。有限模型已证最优时可提前结束。每CP单线程，最多8个独立进程并行。',
        '“预算内未找到”是实际完成搜索但没有获得可核验完整解，数值留空；不是证明问题无解，也不以公共方案或历史方案填补。180秒和600秒检查点属于同一次搜索。']
    limits=[
        '只有原题Q2/Q3实例及单个种子，不报告不存在的均值、方差或显著性。结果仅描述此实现、此输入和此预算的实际表现。',
        '有限候选池内的OPTIMAL不代表原题全局最优；未找到解可能反映构造适配或预算的限制，不能直接推出某类算法不适合该问题。',
        '论文方法仅引用历史结果，未重跑。历史候选空间与总计算预算没有对齐，不能将数值差直接解释为同预算条件下的算法优势。',
        '论文Q2方法为物理路线生成、邻域扩充与路线选择—资源排程分解，排程子问题使用CP-SAT；Q3为有限候选运输—中继联合CP-SAT及连续通信认证。因此完整论文流程和CP-SAT基线的差异也包括候选生成与搜索组织。',
        'v1/v2/v3/v4以及中断日志均保留；它们不混入本轮无初解16配置成绩。数值相同若实际出现，保留原始结果，不人为制造差异。']
    overrun=[dict(question=r['question'],objective=r['objective'],method=r['method'],actual_search_wall_s=r['search_wall_s']) for r in runs if r['search_wall_s']>602]
    timing=f"16配置名义预算各600秒，按600秒检查点计分，累计名义160分钟；实际累计搜索/停止返回{completion['sum_search_wall_s']/60:.2f}分钟，矩阵墙钟{completion['experiment_wall_s']/60:.2f}分钟（含各运行的最终独立核验）。完成16组，其中{completion['feasible_final_runs']}组得到已验证完整解，{16-completion['feasible_final_runs']}组预算内未找到。"
    if overrun:
        timing+='求解器停止返回存在延迟：'+ '；'.join(f"{r['question']}/{r['objective']}/{r['method']}实际{r['actual_search_wall_s']:.3f}秒" for r in overrun)+'。超过600秒发现的候选由入口拒绝；这些配置在600秒内均未记录到可行解。实际耗时原样保留，不声称进程严格在600秒强制退出。'
    content=dict(title='援航 四组独立十分钟对比结果',headers=headers,rows=rows,details=detail,rules=rules,
        limitations=limits,timing=timing,completion=completion,solver_records=solver_records)
    DEST.mkdir(exist_ok=True,parents=True);table(DEST/'四组各方法完整结果.csv',csvrows)
    finalcsv=[r for r in csvrows if r['checkpoint_s']==600];table(DEST/'四组600秒结果.csv',finalcsv)
    text='# 四组无公共初解的十分钟独立对比（EXP-C06）\n\n'+timing+'\n\n'
    text+=mdtable(headers,rows)+'\n\n表内时间是方案最后返航时间，计算预算为每配置600秒；“预算内未找到”留空，不补入其他解。Q3启发式包含CP排程支持。论文行只作历史方案参考。\n\n'
    text+='## 实验口径\n\n'+'\n\n'.join(rules)+'\n\n'
    for q,o in GROUPS:
        data=[]
        for m in METHODS:
            r=next(r for r in detail if (r['question'],r['objective'],r['method'])==(q,o,m));v=r['metrics']
            data.append([LABEL[m],f"{v['completion_s']:.3f}" if v else '未找到',f"{v['energy_kwh']:.6f}" if v else '未找到',
                f"{v['transport_sorties']} + {v['relay_sorties']}" if v else '/',
                f"{r['first_feasible_s']:.3f}" if r['first_feasible_s'] is not None else '/',
                f"{r['search_wall_s']:.3f}",r['complete_constructions'],r['decoder_calls']])
        text+=f"## {q} {'最短时间' if o=='time' else '最低能耗'}\n\n"+mdtable(['方法','返航s','能耗kWh','运输+中继','首解耗时s','搜索耗时s','完整运输构造数','CP解码数'],data)+'\n\n'
    text+='## 未得解的实际记录\n\n'
    for r in missing:
        text+=f"- {r['question']}/{r['objective']}/{r['method']}：构造尝试{r['attempts']}次，完整运输构造{r['complete_constructions']}次，CP解码{r['decoder_calls']}次；拒绝计数{r['rejections']}；CP阶段{r['solver_evidence']}。\n"
    text+='\n## 结论边界\n\n'+'\n\n'.join(limits)+'\n\n'
    text+='## 复现\n\n入口`scripts/contest_baselines/matrix_v5.py --name 新的输出名称`。冻结源码、输入哈希、完整日志、各检查点原始方案与独立核验保存在`evidence/contest-baselines-v5/independent_600s_seed42/`。所有正式方案均来自本配置计时开始后的独立搜索。\n'
    (DEST/'对比实验报告.md').write_text(text,encoding='utf-8');dump(V5/'report_content.json',content)
    checks=dict(all_checks_passed=True,completed_configurations=16,checkpoints=32,validated_solution_checkpoints=len(audits),
        feasible_final_runs=completion['feasible_final_runs'],no_feasible_final_runs=16-completion['feasible_final_runs'],
        source_and_input_hashes_verified=True,no_initial_or_external_warm_start=True,all_trace_origins_independent=True,
        missing_scores_not_imputed=True,paper_method_rerun=False,all_return_caps_verified=True,
        strict_process_wall_time_cap_met=not bool(overrun),post_600_candidates_excluded=True,overrun_records=overrun,
        all_available_solutions_physics_station_and_radio_verified=True,records=audits)
    dump(BASE/'final_checks.json',checks)
    dump(V5/'python_review.json',dict(task='EXP-C06',reviewed_at=datetime.now(timezone.utc).isoformat(),
        verdict='PASSED_FOR_REPORTED_INSTANCE_AND_BUDGET',checks=checks,
        limitations=limits,source_sha256=protocol['source_sha256']))
    print(timing);print(mdtable(headers,rows))

if __name__=='__main__':main()
