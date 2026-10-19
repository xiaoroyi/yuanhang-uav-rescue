"""Verify aligned runs and generate a report without filling failed metrics with zero."""
import csv
import json
from pathlib import Path
from benchmark_v3 import V3,CAPS,cap_errors
from benchmark_v2 import load,digest,solution_metrics,key,V1,V2
from support import PROJECT,dump

BASE=V3/'aligned_600s_seed42';DEST=PROJECT/'docs/current-project/contest-baselines-v3'
LABEL={'greedy':'多起点贪心 + CP排程','aco':'ACO + CP排程','alns':'ALNS + CP排程','cp_sat':'CP-SAT'}
def table(head,rows):return '\n'.join(['| '+' | '.join(head)+' |','|'+'|'.join(['---']*len(head))+'|']+['| '+' | '.join(map(str,r))+' |' for r in rows])

def main():
    completion=load(BASE/'completion.json');assert completion['complete']
    protocol=load(BASE/'protocol.json');runs=load(BASE/'results.json')
    assert {(r['question'],r['method']) for r in runs}=={(q,m) for q in ['Q2','Q3'] for m in LABEL}
    for name,h in protocol['source_sha256'].items():
        assert digest(Path(__file__).with_name(name))==digest(BASE/'source_snapshot'/name)==h
    for name,h in protocol['candidate_sha256'].items():assert digest(V1/name)==h
    checked=[];csvrows=[]
    for r in runs:
        path=BASE/f"{r['question']}_energy_{r['method']}"
        assert load(path/'run.json')==r and r['caps']==CAPS[r['question']] and r['budget_s']==600
        assert [c['checkpoint_s'] for c in r['checkpoints']]==[180.,600.]
        assert r['paper_solution_used'] is False
        previous=None
        for c in r['checkpoints']:
            stem=f"checkpoint_{c['checkpoint_s']:g}s"
            if c['metrics'] is None:
                assert c['status']=='NO_VALIDATED_SOLUTION_WITHIN_CAPS' and not (path/f'{stem}_solution.json').exists()
            else:
                sol=load(path/f'{stem}_solution.json');audit=load(path/f'{stem}_validation.json')
                assert not cap_errors(sol,r['question']) and audit['status']=='passed'
                assert digest(path/f'{stem}_solution.json')==c['solution_sha256']==audit['solution_sha256']
                assert c['metrics']['boxes']==c['metrics']['unique_boxes']==80 and c['metrics']['late_boxes']==c['metrics']['hard_violations']==0
                assert audit['transport']['summary']['valid'] and not audit['station']['late_boxes']
                if r['question']=='Q3':
                    radio=audit['radio']['summary'];assert radio['valid'] and radio['gap_seconds']==radio['unknown_intervals']==0
                for k,v in solution_metrics(sol).items():assert abs(v-c['metrics'][k])<1e-8
                eligible=[t for t in r['trace'] if t['found_s']<=c['checkpoint_s']]
                assert abs(eligible[-1]['found_s']-c['best_found_s'])<1e-8
                if previous is not None:assert key(sol,'energy')<=key(previous,'energy')
                previous=sol
            checked.append(dict(question=r['question'],method=r['method'],checkpoint_s=c['checkpoint_s'],status=c['status'],passed=True))
            m=c['metrics'] or {}
            csvrows.append(dict(question=r['question'],objective='energy',method=r['method'],checkpoint_s=c['checkpoint_s'],
                completion_cap_s=CAPS[r['question']]['C'],energy_cap_kwh=CAPS[r['question']]['E'],transport_cap=CAPS[r['question']]['N'],
                completion_s=m.get('completion_s'),energy_kwh=m.get('energy_kwh'),transport_sorties=m.get('transport_sorties'),relay_sorties=m.get('relay_sorties'),
                late_boxes=m.get('late_boxes'),hard_violations=m.get('hard_violations'),minimum_hard_slack_s=m.get('minimum_hard_slack_s'),
                status=c['status'],search_wall_s=r['search_wall_s']))
    feasible_final=sum(r['checkpoints'][-1]['metrics'] is not None for r in runs)
    dump(BASE/'final_checks.json',dict(all_checks_passed=True,runs=8,checkpoints=16,checks=checked,failures_retained=True,
        all_source_and_candidate_fingerprints_unchanged=True,feasible_final_runs=feasible_final,
        usable_energy_baseline_obtained=feasible_final>0,
        no_validated_solution_is_not_infeasibility_proof=True,
        numerical_energy_difference_available=feasible_final>0,
        general_method_superiority_supported=False))
    reference={r['scenario']:r for r in load(V1/'historical_reference.json')}
    groups=[]
    for q in ['Q2','Q3']:
        rows=[];count=0;count180=0
        for method in LABEL:
            r=next(r for r in runs if r['question']==q and r['method']==method)
            count+=int(r['checkpoints'][-1]['metrics'] is not None);count180+=int(r['checkpoints'][0]['metrics'] is not None)
            for c in r['checkpoints']:
                m=c['metrics']
                rows.append([LABEL[method],str(int(c['checkpoint_s'])),f"{m['completion_s']:.3f}" if m else '—',
                    f"{m['energy_kwh']:.3f}" if m else '—',f"{m['transport_sorties']} + {m['relay_sorties']}" if m else '—',
                    '通过' if m else '限时未得合规解'])
        ref=reference[q+'_economy']
        assert float(ref['C'])<=CAPS[q]['C']
        if q=='Q3':assert float(ref['E'])<=CAPS[q]['E'] and int(ref['N_transport'])<=CAPS[q]['N']
        rows.append(['论文节能历史方案','未匹配',f"{float(ref['C']):.3f}",f"{float(ref['E']):.3f}",
            f"{ref.get('N_transport') or ref['N']} + {ref.get('N_relay') or 0}",'历史记录'])
        valid=[r for r in runs if r['question']==q and r['checkpoints'][-1]['metrics']]
        best=min(valid,key=lambda r:r['checkpoints'][-1]['metrics']['energy_kwh']) if valid else None
        text=f'{q}在180秒检查点有{count180}/4方法保留合规方案，600秒为{count}/4。'
        if best:
            m=best['checkpoints'][-1]['metrics'];text+=f"600秒最低已得能耗来自{LABEL[best['method']]}，为{m['energy_kwh']:.3f}kWh，全部返航{m['completion_s']:.3f}秒。"
        else:text+='本轮没有可计算能耗差值的合规基线，不将失败指标填零，也不计算虚假的提升百分比。'
        text+='这只说明当前实现、有限候选与600秒预算下的搜索结果；不能据此证明原题无解或论文算法普遍优越。'
        groups.append(dict(question=q,headers=['方法','预算s','全部返航s','总能耗kWh','运输 + 中继','状态'],rows=rows,summary=text,feasible=count,feasible180=count180))
    wall=completion['experiment_wall_s']/60
    intro=('本轮重跑Q2/Q3四种传统方法的8个能耗配置，每配置600秒，保存同次搜索180秒与600秒检查点。'
        'Q2采用用户确认的统一返航上限6000秒；Q3恢复论文节能方案的精确合同。原来的无返航上限结果另行保留。'
        '论文方法未重跑，论文路线、箱组、时刻、中继站点和目标数值均未作为基线搜索初解。')
    rules=[
        'Q2：整站加权期望延期D_station=0；31箱硬截止；Cmax≤6000秒。没有额外能耗或架次上限。6000秒为用户选择的新统一实验口径，不冒称恢复的原始论文参数；论文节能备选5969.043477秒满足该口径。',
        'Q3：整站D_station=0；31箱硬截止；运输与中继联合Cmax≤5939.9秒；运输架次≤23；运输加中继能耗≤68.9999kWh；最多4个中继架次槽、2架中继机与6个能源组件。来源为归档input_contract.json，非根据结果倒推。',
        '保留原题不可拆80箱、载质量/体积、逐段剩余载荷能耗、DEM净空、返航SOC至少20%、8架运输机/14组同型共享电池、两阶段充电与资源占用。Q3完整核验全部通信开区间和事件点。',
        '四方法共用与v2相同的850条路线、21个自动驻点、通信原子；种子42，每进程CP单线程，最多4进程并发。各配置从普通贪心在本配置搜索时间内构造搜索参考，不共享额外耗时产生的合规初解，不读取论文方案。',
        '贪心、ACO、ALNS使用共同的必要工作量/能耗/架次数检查；Q2给定分组若串行列表排程超限但必要条件允许，则调用共享CP重新安排资源，最多12秒。Q3同样使用共享联合CP排程；子调用计入600秒。故表中准确标注“+ CP排程”。',
        '尚未获得合规解时，ALNS/ACO可按必要条件违反程度更新搜索参考；这些仅为可行性搜索状态，不计入成果。只有满足全部上限、通过物理和通信独立核验的方案才有正式指标。CP-SAT在完整公共池中直接施加同样上限，冷启动。',
        '本轮仅重跑受目标条件修正影响的8个能耗配置。v2的8个时间目标配置保留原始结果，没有伪装成本轮重新执行；其预算和候选版本见v2独立报告。']
    status_rows=[]
    for r in runs:
        if r['method']!='cp_sat':continue
        path=BASE/f"{r['question']}_energy_cp_sat"
        stages=load(path/'cp_evidence.json')['evidence'] if r['question']=='Q2' else load(path/'decoders/full_pool/solver_evidence.json')
        energy_stages=[s for s in stages if s['stage']=='E']
        bound=energy_stages[-1].get('best_bound',energy_stages[-1].get('bound')) if energy_stages else None
        status_rows.append([r['question'],', '.join(s['stage']+'='+s['status'] for s in stages),f"{r['search_wall_s']:.3f}",
            f'{bound/1e6:.6f}' if bound is not None else '未提供'])
    caveats=[
        '约束条件与指标口径已明确对齐，历史总预算与候选空间仍未匹配。论文约33万条Q2路线，并使用更丰富的邻域与中继驻点；本轮850路线/21驻点的可达空间更小。不能把差异全部归因于方法。',
        '单个随机种子、单个原题算例，没有均值、标准差、显著性或泛化结论。0/4或4/4仅为本次观察的计数，不是成功概率估计。',
        'NO_VALIDATED_SOLUTION_WITHIN_CAPS表示当前预算与候选下未获得通过全部约束的方案。UNKNOWN不是不可行证明；即使有限池INFEASIBLE也不能外推原题。',
        '不使用论文历史方案作基线兜底，不把超限但能耗较低的方案纳入正式表。无数值时不计算与论文的提升百分比。',
        'v3加入上限并相应增加可行性引导和Q2固定分组排程，不能将v2到v3差异视为纯粹的单参数消融。3分钟/10分钟收益只比较v3同一次连续搜索。']
    timing=f"8×600秒=80分钟名义累计搜索预算；4进程实际矩阵墙钟{wall:.2f}分钟，实测累计搜索墙钟{completion['sum_search_wall_s']/60:.2f}分钟。加载、模型构建、方案构造、子CP与搜索写盘的计时口径见协议；最终独立核验另计。短预算预检单列保存，不混入正式结果。"
    diagnostics=[[r['question'],LABEL[r['method']],r['attempts'],r['decoder_calls'],r['rejections'].get('construction_dead_end',0),r['rejections'].get('necessary_work_energy_or_count_bound',0)] for r in runs]
    evidence='evidence/contest-baselines-v3/aligned_600s_seed42/保存protocol.json、historical_q3_input_contract.json、source_snapshot/、results.json/CSV、各配置run.json及日志、合规方案与核验明细。final_checks.json核对8配置/16检查点、上限、独立核验、发现时间与源代码/候选指纹。Q2用户口径选择逐字保留在protocol.json。'
    lines=['# 援航Q2/Q3对齐返航上限的能耗对照','任务：EXP-C03；每配置600秒；随机种子42。',intro,'## 统一条件']+[f'- {s}' for s in rules]
    for g in groups:lines+=['## '+g['question']+'能耗结果',table(g['headers'],g['rows']),g['summary']]
    lines+=['## 完整池CP-SAT内部状态',table(['题目','求解阶段与状态','实际搜索墙钟s','有限模型能耗下界/kWh'],status_rows),
        '下界只适用于850条路线、21个驻点及0.1秒网格的当前有限模型。它不是原题能耗下界，也不能与论文值相减作为原题Gap。有限候选未包含的路线未被定价或搜索。',
        '## 实际搜索记录',table(['问题','方法','构造/修复尝试','固定分组CP调用','构造死路','必要条件拒绝'],diagnostics),
        '必要条件拒绝包括飞机工作量下界超过返航上限、运输能耗本身超过联合能耗上限、运输架次数超上限。通过必要条件仍不保证时限/电池/通信可排。CP-SAT行为完整池建模与求解，构造次数记0不表示未计算；分支、冲突、下界和状态保留在各自求解证据中。',
        '## 实测时间',timing,'## 适用边界']+[f'- {s}' for s in caveats]+['## 可复核性',evidence,
        '复现使用新目录保留既有证据：`.venv/Scripts/python.exe scripts/contest_baselines/matrix_v3.py --name aligned_rerun`。所有正式参数以保存的protocol.json为准。']
    DEST.mkdir(exist_ok=True,parents=True);(DEST/'对齐实验报告.md').write_text('\n\n'.join(lines)+'\n',encoding='utf-8')
    with (DEST/'完整结果对比.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(csvrows[0]));w.writeheader();w.writerows(csvrows)
    dump(V3/'report_content.json',dict(intro=intro,rules=rules,groups=groups,solver_status=status_rows,caveats=caveats,timing=timing,evidence=evidence,completion=completion,diagnostics=diagnostics))
    print('8 runs / 16 checkpoints verified; report and CSV generated')

if __name__=='__main__':main()
