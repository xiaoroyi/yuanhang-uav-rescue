"""Verify frozen corrected experiments and build the final evidence-backed report."""
import csv
import math
from pathlib import Path
import py_compile
from datetime import datetime,timezone
from benchmark_v2 import load,digest,V1,solution_metrics
from pattern_v4 import V4
from benchmark_v4 import cap_errors,CAPS
from support import PROJECT,dump,table as csv_table

BASE=V4/'corrected_600s_seed42';DEST=PROJECT/'docs/current-project/contest-baselines-v4'
METHODS=['greedy','aco','alns','cp_sat'];LABELS={'greedy':'多起点贪心 / EDF','aco':'ACO','alns':'ALNS','cp_sat':'CP-SAT'}
def label(m,q):return LABELS[m]+(' + CP排程' if q=='Q3' and m!='cp_sat' else '')
def mdtable(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(map(str,r))+' |' for r in rows])

def main():
    protocol=load(BASE/'protocol.json');completion=load(BASE/'completion.json');runs=load(BASE/'results.json')
    run_paths=load(BASE/'run_paths.json') if (BASE/'run_paths.json').exists() else {}
    def runpath(q,method):
        key=f'{q}_energy_{method}'
        return BASE/run_paths.get(key,key)
    assert completion['complete'] and completion['completed_runs']==8 and not completion['errors']
    assert len(runs)==8 and len({(r['question'],r['method']) for r in runs})==8
    assert protocol['caps']==CAPS and all(c['E'] is None and c['N'] is None for c in protocol['caps'].values())
    for name,sha in protocol['source_sha256'].items():
        p=PROJECT/'scripts/contest_baselines'/name;assert digest(p)==sha and digest(BASE/'source_snapshot'/name)==sha,name
        py_compile.compile(str(p),doraise=True)
    for name,sha in protocol['candidate_sha256'].items():assert digest(V4/name)==sha,name
    rowcsv=[];audited=[];groups=[];summaries=[]
    historical={r['scenario']:r for r in load(V1/'historical_reference.json')}
    for q in ['Q2','Q3']:
        pool=load(V4/f'pool_{q.lower()}.json');route_ids={r['id'] for r in pool};site_ids={s['id'] for s in load(V4/'sites.json')}
        initial=load(V4/f'common_{q.lower()}.json');init=solution_metrics(initial);audit0=load(V4/f'common_{q.lower()}_validation.json')
        assert audit0['status']=='passed' and audit0['solution_sha256']==digest(V4/f'common_{q.lower()}.json')
        assert not cap_errors(initial,q)
        assert set(r['route']['id'] for r in initial['transport'])<=route_ids
        rows=[];finals=[];improved_methods=[]
        for method in METHODS:
            r=next(r for r in runs if r['question']==q and r['method']==method);path=runpath(q,method)
            assert r['seed']==42 and r['budget_s']==600 and r['caps']==CAPS[q] and not r['paper_solution_used']
            assert r['shared_initial_sha256']==digest(V4/f'common_{q.lower()}.json')
            assert r['trace'][0]['origin']=='shared_independent_validated_initial'
            assert [c['checkpoint_s'] for c in r['checkpoints']]==[180.,600.]
            previous=init['energy_kwh']
            for c in r['checkpoints']:
                assert c['status']=='VALIDATED_FEASIBLE' and c['metrics'] is not None
                p=path/f"checkpoint_{c['checkpoint_s']:g}s_solution.json";sol=load(p);metrics=solution_metrics(sol)
                assert digest(p)==c['solution_sha256'] and not cap_errors(sol,q)
                assert all(abs(metrics[k]-c['metrics'][k])<1e-8 for k in metrics)
                assert metrics['energy_kwh']<=previous+1e-8;previous=metrics['energy_kwh']
                assert c['best_found_s']<=c['checkpoint_s']+1e-6
                assert set(row['route']['id'] for row in sol['transport'])<=route_ids
                assert set(row['site']['id'] for row in sol['relay'])<=site_ids
                audit=load(path/f"checkpoint_{c['checkpoint_s']:g}s_validation.json")
                assert audit['status']=='passed' and audit['solution_sha256']==digest(p)
                station=audit['station'];assert station['boxes']==station['unique_boxes']==80 and station['late_boxes']==station['hard_violations']==0
                assert audit['transport']['summary']['valid']
                if q=='Q3':
                    radio=audit['radio']['summary'];assert radio['valid'] and radio['gap_seconds']==radio['unknown_intervals']==0
                rowcsv.append(dict(question=q,method=method,method_label=label(method,q),checkpoint_s=c['checkpoint_s'],
                    **c['metrics'],search_wall_s=r['search_wall_s'],best_found_s=c['best_found_s'],status=c['status'],
                    method_search_outcome='IMPROVED_SHARED_INITIAL' if init['energy_kwh']-metrics['energy_kwh']>1e-7 else 'RETAINED_SHARED_INITIAL',
                    shared_initial_energy_kwh=init['energy_kwh'],improvement_from_initial_kwh=init['energy_kwh']-metrics['energy_kwh'],solution_sha256=digest(p)))
                audited.append(dict(question=q,method=method,checkpoint_s=c['checkpoint_s'],solution_sha256=digest(p)))
            c180,c600=r['checkpoints'];m=c600['metrics'];gain=init['energy_kwh']-m['energy_kwh'];finals.append((method,m));
            if gain>1e-7:improved_methods.append(method)
            rows.append([label(method,q)+('（改善初解）' if gain>1e-7 else '（仅保留初解）'),f"{c180['metrics']['energy_kwh']:.6f}",f"{m['energy_kwh']:.6f}",f"{m['completion_s']:.3f}",
                f"{m['transport_sorties']} + {m['relay_sorties']}",f'{gain:.6f}'])
        best=min(finals,key=lambda p:(p[1]['energy_kwh'],p[1]['completion_s']));hist=historical[f'{q}_economy']
        assert float(hist['C'])<=CAPS[q]['C']+1e-6
        difference=(best[1]['energy_kwh']-float(hist['E']))/best[1]['energy_kwh']*100
        common_note=f"公共初解：返航{init['completion_s']:.3f}秒，能耗{init['energy_kwh']:.6f}kWh，{init['transport_sorties']}次运输、{init['relay_sorties']}次中继。四种方法共享，计入表内结果，但不归为各方法独立构造所得。"
        htrans=int(float(hist.get('N_transport') or hist['N']));hrelay=int(float(hist.get('N_relay') or 0))
        historical_note=f"论文节能历史参考：返航{float(hist['C']):.3f}秒、能耗{float(hist['E']):.6f}kWh，{htrans}次运输、{hrelay}次中继，满足本轮共同返航/交付口径；候选与历史计算预算不同，未重跑。"
        comparison=f"本轮最低已得能耗来自{label(best[0],q)}，为{best[1]['energy_kwh']:.6f}kWh。与论文历史方案的能耗数值相差{abs(best[1]['energy_kwh']-float(hist['E'])):.6f}kWh（以本轮最低已得值为分母，论文{'较低' if difference>=0 else '较高'}{abs(difference):.2f}%）。这是两套流程已得方案的描述性差异，包含候选空间、共享初解和预算差异，不能解释为同预算、同候选条件下的算法增益。"
        groups.append(dict(question=q,headers=['方法','180s能耗','600s能耗','600s返航s','运输 + 中继','较初解节能kWh'],rows=rows,
            common_note=common_note,historical_note=historical_note,comparison=comparison))
        summaries.append(dict(question=q,initial=init,best_method=best[0],best_600=best[1],paper_C=float(hist['C']),paper_E=float(hist['E']),
            historical_difference_pct=difference,post_initial_improved_methods=improved_methods,unique_final_energy_values=len(set(round(m['energy_kwh'],7) for _,m in finals))))
    assert len(rowcsv)==16 and len(audited)==16
    checks=dict(all_checks_passed=True,source_files_verified=len(protocol['source_sha256']),candidate_files_verified=len(protocol['candidate_sha256']),
        runs=8,checkpoints=16,feasible_final_runs=8,cap_definitions_verified=True,all_physics_and_station_checks_passed=True,
        all_q3_continuous_radio_checks_passed=True,all_scores_monotone=True,paper_method_rerun=False,
        shared_initial_disclosed=True,standalone_pure_heuristic_performance_measured=False,
        historical_budgets_and_candidate_spaces_matched=False,general_algorithm_superiority_supported=False,records=audited)
    dump(BASE/'final_checks.json',checks)
    timing=protocol['common_preprocessing'];prep=timing['preparation_wall_s_including_implementation_and_failed_gates']/60
    timing_text=f"每配置最多600秒，8配置名义累计80分钟；每CP单线程。原先完成5组，按用户要求中断后，保持源码及输入哈希不变，将未完成的Q3 ACO/ALNS/CP-SAT各从相同公共初解重新运行600秒，3进程并行。补跑墙钟{completion['resume_wall_s']/60:.2f}分钟；最终8组累计实际搜索{completion['sum_search_wall_s']/60:.2f}分钟。不将中断前的3组部分搜索或暂停时间计入最终成绩，原日志保留，路径映射见run_paths.json。公共准备阶段墙钟约{prep:.2f}分钟，包含本轮实现修复、失败预检、候选/初解生成及核验，不属于纯算法预处理运行时；未计入每方法600秒改进预算。最终独立核验另计。达到有限模型最优者可提前结束，600秒为上限。"
    q2cp=load(runpath('Q2','cp_sat')/'cp_evidence.json')['evidence'];q3path=runpath('Q3','cp_sat')/'decoders/full_pool/solver_evidence.json'
    q3cp=load(q3path) if q3path.exists() else []
    solver_note='Q2 CP-SAT：'+', '.join(f"{r['stage']}={r['status']}（{r['wall_time']:.2f}s）" for r in q2cp)+'。Q3 CP-SAT：'+(', '.join(f"{r['stage']}={r['status']}（{r['seconds']:.2f}s）" for r in q3cp) if q3cp else '预算内未完成内部求解阶段，仍保留已核验初解')+'。最优性仅针对有限池及整数网格；UNKNOWN不代表无解。'
    rules=[
        'Q2：全部运输返航≤6000秒；Q3：运输与中继联合返航≤5939.9秒。两题均不设总能耗或运输架次硬上限，能耗为目标、架次随结果报告。',
        '80个不可拆箱全部整站零期望延期、31箱硬截止；质量、体积、DEM航段、逐段载荷能耗、返航SOC≥20%、8运输机与14电池、两阶段充电均保持；Q3保持2中继机与6组件并核验全部通信区间及边界。',
        f"共享{len(load(V4/'pool_q2.json'))}条具体箱号路线和{len(load(V4/'sites.json'))}个独立中继点，最多6个计算架次槽（不是实体机数）。前置20705个独立货箱数量模式用于构造公共初解，正式搜索使用冻结的具体箱号路线池；不能将模式数写成正式CP候选数。",
        '公共初解由独立数量模式MILP、截止/机队工作量筛选、资源列表构造和CP、独立中继覆盖/窗口模板及悬停收紧得到，未读论文路线、排程、结果作为搜索输入。全部方法共享同题初解与候选，所以本轮测量的是共同可行性支持后的600秒改进表现。',
        '论文Q2采用物理路线生成、邻域扩充与路线选择—资源排程分解，调度子问题使用CP-SAT；Q3采用有限候选运输—中继联合CP-SAT与连续通信认证。因此，论文完整流程和本轮CP-SAT基线并非完全不同的求解范式，候选构造与搜索组织也是差异来源（论文第4.3、5.3节）。',
        '贪心/EDF使用前瞻返航检查、多起点随机评分；ACO使用信息素、前32个候选的概率选择；ALNS使用随机、高单位能耗、空间相关三类移除和自适应权重；Q3三者均用共享CP排程解码。CP-SAT使用相同具体路线池、点位和公共初解。均为本问题的适配实现，不能冒充纯算法的独立端到端成绩。',
        '相同种子42，180/600秒检查点来自同一次连续搜索。公共输入加载在计时前；构造、模型建立、CP解码、搜索写盘计入600秒。共享预处理与最终独立验证另计。',
        'v1/v2/v3与失败预检全部保留。新版本更换了初始化、候选和搜索控制，不能将跨版本变化全归为预算增长。原时间目标的8配置保留旧报告，本轮未重跑。']
    repairs='除取消Q3能耗/架次目标门槛外，本轮修正了5939.9秒上限的浮点整数化：直接int(5939.9/0.1)会误得59398刻度、将上限再收紧0.1秒；现在保留59399刻度。初解另通过求解器辅助可行性检查。中继窗口的整数区间交集经1000组固定种子集合等价性检查，确认合并重叠/相邻区间不改变可选时间刻度；这些检查均为预检，不充当正式搜索成绩。'
    limitations=[
        '只有单个实例和单个随机种子；不提供均值、方差或显著性结论。表中“通过”是方案物理/时限/通信核验通过，不是证明算法找到全局最优。',
        '共同初解为所有方法提供了可行解保障；若某方法没有改善，结果应称“保留共同初解”。不把这写成该方法从零独立找到合规解。',
        '论文按用户要求只引用历史方案。返航/交付与物理口径可核对，历史搜索预算和路线/位置空间未对齐；本表不能单独证明所提算法本身优于经典算法。适用于展示本题上各已得方案及取舍。',
        '正式路线池是预先构造的有限子集；Q2 CP-SAT若证实该池最优，也不代表原题全局最优，更不代表论文方案不可行。',
        'Q3有限驻点和最多6个架次槽属于共同搜索设置。原题物理机体/能源库存分别为2/6，未误作总架次上限。']
    stagnation=[]
    for r in runs:
        if r['method']=='cp_sat':continue
        stagnation.append(dict(question=r['question'],method=r['method'],attempts=r['attempts'],
            decoder_calls=r['decoder_calls'],callbacks=r['callbacks'],rejections=r['rejections'],
            retained_shared_initial_only=len(r['trace'])==1 and r['trace'][0]['origin']=='shared_independent_validated_initial',
            final_solution_sha256=r['checkpoints'][-1]['solution_sha256']))
    q2st=[r for r in stagnation if r['question']=='Q2']
    assert len({r['final_solution_sha256'] for r in q2st})==1
    stagnation_text='Q2贪心、ACO、ALNS的完整能耗均为66.13367060949392kWh，最终方案SHA256完全相同，轨迹只有共享初解。各方法虽跑满600秒，新构造均在截止/资源/返航约束筛选中失败，没有产生新的完整方案。因此相同成绩来源于保留同一初解，不是三种算法各自收敛到同一最优解，也不是三位小数舍入巧合。当前启发式构造适配仍有明显局限；按用户要求保留实现和如实报告，不再进行算法优化。'
    oldbase=PROJECT/'evidence/contest-baselines-v2/main_600s_seed42'
    oldcompletion=load(oldbase/'completion.json');assert oldcompletion['complete'] and oldcompletion['completed_runs']==16
    oldruns=[r for r in load(oldbase/'results.json') if r['objective']=='time'];assert len(oldruns)==8
    timerows=[]
    for q in ['Q2','Q3']:
        for method in METHODS:
            r=next(r for r in oldruns if r['question']==q and r['method']==method);c=r['checkpoints'][-1]
            assert c['checkpoint_s']==600 and c['status']=='VALIDATED_FEASIBLE'
            path=oldbase/f'{q}_time_{method}'/c['validation_file']
            audit=load(path);assert audit['status']=='passed' and audit['solution_sha256']==c['solution_sha256']
            assert digest(path.with_name('checkpoint_600s_solution.json'))==c['solution_sha256']
            timerows.append(dict(question=q,method=method,completion_s=c['metrics']['completion_s'],
                energy_kwh=c['metrics']['energy_kwh'],search_wall_s=r['search_wall_s'],source_version='v2',
                solution_sha256=c['solution_sha256']))
    time_table=[]
    for method in METHODS:
        time_table.append([LABELS[method]]+[f"{next(r for r in timerows if r['question']==q and r['method']==method)['completion_s']:.3f}" for q in ['Q2','Q3']])
    time_table.append(['论文历史最快方案']+[f"{float(historical[q+'_fast']['C']):.3f}" for q in ['Q2','Q3']])
    time_note='时间最短目标已在v2完成Q2/Q3×4方法共8组，每组600秒，均有完整方案及核验。本次未重新运行时间目标。该旧版候选池、初始化与当前v4不同；甚至当前v4公共节能初解的返航时间也短于旧版全部时间目标基线，说明旧版搜索设置明显受限。旧表仅保留实验记录，不能将它与当前能耗表合并成同版本公平对比，更不能据此夸大论文方法的时间优势。'
    dump(V4/'stagnation_audit.json',dict(records=stagnation,interpretation=stagnation_text))
    csv_table(DEST/'时间最短历史结果_v2.csv',timerows)
    four_groups=[]
    for r in oldruns+runs:
        c=r['checkpoints'][-1];m=c['metrics'];is_energy=r['objective']=='energy'
        changed=len(r['trace'])>1
        four_groups.append(dict(question=r['question'],objective=r['objective'],method=r['method'],
            primary_metric=m['energy_kwh'] if is_energy else m['completion_s'],unit='kWh' if is_energy else 's',
            completion_s=m['completion_s'],energy_kwh=m['energy_kwh'],
            search_outcome='FOUND_IMPROVEMENT' if changed else 'RETAINED_SHARED_INITIAL',
            source_version='v4' if is_energy else 'v2',budget_s=600,actual_search_s=r['search_wall_s'],
            validation_status=c['status']))
    csv_table(DEST/'四组各方法结果.csv',four_groups)
    content=dict(title='援航 修正后的十分钟能耗对照',task='EXP-C05',groups=groups,summaries=summaries,rules=rules,
        stagnation_text=stagnation_text,time_note=time_note,time_headers=['方法','Q2返航秒','Q3返航秒'],time_rows=time_table,
        timing_text=timing_text,solver_note=solver_note,limitations=limitations,completion=completion,preparation=timing,repairs=repairs)
    dump(V4/'report_content.json',content);DEST.mkdir(exist_ok=True,parents=True);csv_table(DEST/'完整结果对比.csv',rowcsv)
    text='# 修正后的Q2/Q3十分钟能耗对照（EXP-C05）\n\n8配置、16检查点全部通过独立核验。每方法600秒是公共可行初解之后的追加搜索预算；共同初解的贡献单列。论文方法未重跑。\n\n'
    text+='## 统一口径与方法\n\n'+'\n\n'.join(rules)+'\n\n'+repairs+'\n\n'
    for group in groups:text+=f"## {group['question']} 能耗对照\n\n{group['common_note']}\n\n"+mdtable(group['headers'],group['rows'])+f"\n\n{group['historical_note']}\n\n{group['comparison']}\n\n"
    text+='## 为什么三个结果都是66.134\n\n'+stagnation_text+'\n\n'+mdtable(['问题','方法','构造尝试次数','构造死路次数','CP解码调用','仅保留初解'],[[r['question'],r['method'],r['attempts'],r['rejections'].get('construction_dead_end',0),r['decoder_calls'],r['retained_shared_initial_only']] for r in stagnation])+'\n\n'
    text+='## 时间最短实验的完成情况（v2历史记录）\n\n'+time_note+'\n\n'+mdtable(content['time_headers'],time_table)+'\n\n'
    text+='## 计时与求解状态\n\n'+timing_text+'\n\n'+solver_note+'\n\n## 结论边界\n\n'+'\n\n'.join(limitations)
    text+='\n\n## 复现与核验\n\n入口：`scripts/contest_baselines/matrix_v4.py`；复现请使用新的输出名称。正式协议、源码快照、数据指纹、逐配置日志、16份方案及验证、`final_checks.json`在`evidence/contest-baselines-v4/corrected_600s_seed42/`。公共初解与预检轨迹在同级`preparation/`。CSV保留完整精度。短预演与诊断结果不混入正式矩阵。\n'
    (DEST/'对比实验报告.md').write_text(text,encoding='utf-8')
    review=dict(schema_version=1,question_id='Q2/Q3',language='python',decision_id='EXP-C05',reviewed_files=protocol['source_sha256'],
        checks={k:dict(status='PASS',evidence=[v]) for k,v in dict(syntax='Frozen Python sources compile and eight formal runs complete without errors.',
            input_contract='Shared inputs/initials match frozen hashes; raw physical data unchanged; all 16 plans satisfy chosen caps and original constraints.',
            method_alignment='Four user-approved adaptations; removed Q3 outcome thresholds; shared feasibility support and restricted search space explicitly disclosed.',
            reproducibility='Frozen sources and candidate hashes, seed42, one CP worker per process, all raw checkpoints/logs retained.',
            output_contract='16 complete independently verified checkpoints, actual timings, common-initial improvement deltas and historical-comparison limits.').items()},
        findings=['This is a conditional comparison after shared feasibility initialization, not a pure-heuristic benchmark.','Historical method budgets and candidate spaces remain unmatched.'],
        verdict='PASSED_FOR_REPORTED_CONDITIONAL_COMPARISON',reviewed_at=datetime.now(timezone.utc).isoformat())
    dump(V4/'python_review.json',review)
    print('8 corrected configurations / 16 verified checkpoints; report and CSV generated')

if __name__=='__main__':main()
