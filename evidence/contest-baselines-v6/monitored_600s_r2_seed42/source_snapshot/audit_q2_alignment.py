"""Q2 targeted replay: original spreadsheet deadlines vs historical short-horizon reference."""
from collections import Counter
import ast
import copy
import hashlib
import json
from pathlib import Path
import zipfile
import pymupdf
from openpyxl import load_workbook
from support import PROJECT,OUT,inputs,dump,table
from legacy_validate import check
from legacy_routes import Physics
from benchmark import station_audit

DEST=PROJECT/'evidence/contest-baselines-v2/q2_alignment_audit'

def sha(raw):return hashlib.sha256(raw).hexdigest()

def main():
    DEST.mkdir(exist_ok=True,parents=True)
    data=inputs();P=Physics()
    source=PROJECT/'references/modeling/data/tables/物资需求与配送时限.xlsx'
    wb=load_workbook(source,read_only=True,data_only=True)
    source_rows=list(wb['逐箱货箱清单'].values);wb.close()
    raw={r[0]:r for r in source_rows[1:] if r[0]}
    assert len(raw)==len(data['boxes'])==80
    for b in data['boxes']:
        r=raw[b['id']]
        first=r[5]=='是';hard=[]
        if b['category']=='MED':hard.append(r[7])
        if first:hard.append(r[6])
        assert b['expected_s']==r[7] and b['priority']==r[8] and b['first']==first
        assert b['hard_due']==(min(hard) if hard else None)
        assert b['weight']==r[3] and abs(b['volume_L']-r[4]*1000)<1e-8
    archive=PROJECT/'references/modeling/verified-release-code-and-results.zip'
    member='review_runs/20260925_overnight/reviews/morning_20260926/runs/q2_decomp_night_00/elites/41f0ee5a185363c4/solution.json'
    with zipfile.ZipFile(archive) as z:
        archived=z.read(member);historical=json.loads(archived)
        meta=json.loads(z.read(member.replace('solution.json','candidate_review.json')))
    assert sha(archived)==meta['solution_sha256']
    # Copy only the selected historical solution; never import archived bootstrap/env.
    (DEST/'historical_q2_economy_solution.json').write_bytes(archived)
    current_path=PROJECT/'evidence/contest-baselines-v2/main_600s_seed42/Q2_energy_cp_sat/checkpoint_600s_solution.json'
    current=json.loads(current_path.read_text(encoding='utf-8'))['transport']
    audits={};station_rows=[]
    for name,rows in [('historical_short_horizon',historical),('baseline_uncapped_energy',current)]:
        replay=check(rows,save=DEST/name,data=data)
        assert replay['summary']['valid'],replay['errors']
        # Rebuild whole-stop completion from independently reconstructed event times.
        import csv
        reconstructed=list(csv.DictReader((DEST/name/'stop_events.csv').open(encoding='utf-8-sig')))
        delivery=[]
        for stop in reconstructed:
            for ident in ast.literal_eval(stop['boxes']):
                box=next(x for x in data['boxes'] if x['id']==ident)
                complete=float(stop['departure']);late=max(0.,complete-box['expected_s'])
                delivery.append(dict(scenario=name,box=ident,category=box['category'],first=box['first'],
                    complete_s=complete,expected_s=box['expected_s'],hard_due_s=box['hard_due'],priority=box['priority'],
                    expected_slack_s=box['expected_s']-complete,late_s=late,weighted_late_s=box['priority']*late,
                    hard_slack_s=None if box['hard_due'] is None else box['hard_due']-complete))
        assert Counter(d['box'] for d in delivery)==Counter({b:1 for b in raw})
        soft=[d for d in delivery if d['hard_due_s'] is None]
        hard=[d for d in delivery if d['hard_due_s'] is not None]
        statistics=dict(boxes=len(delivery),hard_boxes=len(hard),nonhard_boxes=len(soft),
            late_boxes=sum(d['late_s']>1e-6 for d in delivery),D_station=sum(d['weighted_late_s'] for d in delivery),
            hard_violations=sum(d['hard_slack_s']< -1e-6 for d in hard),
            minimum_expected_slack_s=min(d['expected_slack_s'] for d in delivery),
            minimum_hard_slack_s=min(d['hard_slack_s'] for d in hard),
            minimum_nonhard_expected_slack_s=min(d['expected_slack_s'] for d in soft),
            latest_delivery_s=max(d['complete_s'] for d in delivery),
            weighted_mean_station_delivery_s=sum(d['priority']*d['complete_s'] for d in delivery)/sum(d['priority'] for d in delivery))
        assert statistics['late_boxes']==statistics['D_station']==statistics['hard_violations']==0
        stats=station_audit(P,rows)
        assert stats['late_boxes']==0 and abs(stats['minimum_hard_slack_s']-statistics['minimum_hard_slack_s'])<1e-7
        audits[name]=dict(physical=replay['summary'],whole_stop=statistics)
        station_rows.extend(delivery)
    table(DEST/'whole_stop_deadline_comparison.csv',station_rows)
    # Counterexample: valid under original task deadlines, excluded by the paper reference's own finish horizon.
    reference_C=audits['historical_short_horizon']['physical']['Cmax']
    current_C=audits['baseline_uncapped_energy']['physical']['Cmax']
    comparison=dict(reference_completion_s=reference_C,baseline_completion_s=current_C,
        baseline_excess_over_reference_horizon_s=current_C-reference_C,
        baseline_satisfies_reference_completion_horizon=current_C<=reference_C+1e-6,
        exact_historical_optimizer_time_cap_recovered=False,
        reason='Paper section 4.2.4 explicitly uses a completion-time cap; final reference is a short-horizon energy alternative. Archived selected-candidate metadata does not record the original cap value. No 6000s value is invented.')
    work={g:sum(r['route']['duration'] for r in current if r['route']['model']==g) for g in P.models}
    necessary={g:work[g]/data['M'][g] for g in work}
    comparison['baseline_sortie_counts_by_model']=dict(Counter(r['route']['model'] for r in current))
    comparison['aircraft_inventory_by_model']=data['M']
    comparison['total_aircraft_work_s_by_model']=work
    comparison['fixed_route_completion_lower_bound_s_by_model']=necessary
    comparison['fixed_route_completion_lower_bound_s']=max(necessary.values())
    # Compress avoidable idle while preserving each entity's original order.
    earliest=copy.deepcopy(current);air_ready={};battery_ready={}
    for r in sorted(earliest,key=lambda r:(r['start'],r['sortie'])):
        duration=r['return']-r['start'];charge=r['battery_ready']-r['return']
        r['start']=max(air_ready.get(r['aircraft'],0.),battery_ready.get(r['battery'],0.))
        r['return']=r['start']+duration;r['battery_ready']=r['return']+charge
        air_ready[r['aircraft']]=r['return'];battery_ready[r['battery']]=r['battery_ready']
    compressed=check(earliest,save=DEST/'baseline_preserved_order_asap',data=data)
    assert compressed['summary']['valid'] and station_audit(P,earliest)['late_boxes']==0
    comparison['same_routes_same_entity_orders_asap_completion_s']=compressed['summary']['Cmax']
    comparison['same_routes_energy_unchanged_after_asap']=abs(compressed['summary']['E']-audits['baseline_uncapped_energy']['physical']['E'])<1e-8
    comparison['asap_still_exceeds_historical_completion']=compressed['summary']['Cmax']>reference_C
    paper=pymupdf.open(PROJECT/'references/modeling/paper.pdf');pages=[]
    for index in [28,29,31,38]:
        page=paper[index];text=page.get_text()
        (DEST/f'paper_page_{index+1}.txt').write_text(text,encoding='utf-8')
        page.get_pixmap(matrix=pymupdf.Matrix(1.35,1.35),alpha=False).save(DEST/f'paper_page_{index+1}.png')
        pages.append(dict(physical_page=index+1,printed_page=index,text=text))
    result=dict(status='PASSED_ORIGINAL_CONSTRAINTS_BUT_COMPARISON_NOT_ALIGNED',audits=audits,comparison=comparison,
        raw_spreadsheet_deadlines_all_80_match=True,raw_spreadsheet_sha256=sha(source.read_bytes()),
        baseline_solution_sha256=sha(current_path.read_bytes()),historical_solution_sha256=sha(archived),
        archive_member=member,paper_pages=pages,
        finding='No soft-deadline omission: D_station=0 for all 80 boxes. Missing alignment is final-return time horizon, a separate criterion from cargo delivery deadlines.',
        claim_correction='61.6265kWh is a feasible uncapped-energy solution; it does not establish superiority over the historical 64.7341kWh short-horizon alternative at matched completion time.')
    dump(DEST/'audit.json',result)
    baseline=audits['baseline_uncapped_energy'];historic=audits['historical_short_horizon']
    report=['# Q2低能耗结果与论文节能备选的目标一致性复查',
        '结论：61.626515kWh方案满足原题确定性约束，没有漏算期望送达软截止；但与论文64.734132kWh的较短时域节能备选不属于相同的优化条件。此前“能耗优于论文”的方法优劣解读应撤回，原始可行数值保留。',
        '## 逐项复查',
        '| 项目 | 本轮CP-SAT无返航上限能耗方案 | 论文较短时域节能备选 |',
        '|---|---:|---:|',
        f"| 总运输能耗/kWh | {baseline['physical']['E']:.6f} | {historic['physical']['E']:.6f} |",
        f"| 全部返航/s | {current_C:.6f} | {reference_C:.6f} |",
        f"| 全部返航/min | {current_C/60:.3f} | {reference_C/60:.3f} |",
        '| 完整且唯一交付箱数 | 80 | 80 |','| 整站期望延期箱数 | 0 | 0 |','| 整站加权延期/加权秒 | 0 | 0 |',
        '| 硬截止违反/31箱 | 0 | 0 |',
        f"| 最小整站硬截止余量/s | {baseline['whole_stop']['minimum_hard_slack_s']:.6f} | {historic['whole_stop']['minimum_hard_slack_s']:.6f} |",
        f"| 最低返航SOC | {baseline['physical']['min_SOC']*100:.3f}% | {historic['physical']['min_SOC']*100:.3f}% |",
        f"| A/B/C架次数 | 4 / 11 / 7 | 10 / 6 / 6 |",
        '医疗和首批箱件的硬截止、全部80箱的期望时刻和优先系数均与原始Excel逐行核对一致。49箱没有额外硬截止的普通物资也均未超过期望时刻；并非只检查31箱后放任其余49箱延期。载荷、体积、逐段剩余载荷能耗、返航电量、实体机体、电池及两阶段充电重新独立回放通过。',
        '## 为什么能耗更低却返航更晚',
        f"低能耗组合多用B型机：11个B型架次累计作业{work['B']:.6f}秒，而库存只有2架。仅飞机工作量必要条件就要求Cmax至少{necessary['B']:.6f}秒；即使忽略电池和截止等额外限制，也无法将这份箱组与机型组合压到论文备选约5969秒的返航水平。该下界只针对已选22条路线，不是全问题的时间下界。",
        f"另外按相同机体/电池顺序前推，消除可避免等待后的返航时刻为{compressed['summary']['Cmax']:.6f}秒，能耗不变且仍满足全部时限。因此原排程可能存在等待，但长时域差异不能仅靠提前执行消除。",
        '## 论文口径证据与修正',
        '论文物理第29页（正文28页）定义整站交付与D_station；物理第32页（正文31页）第4.2.4节明确“节能备选在其完成时间上限内先减小能耗”；物理第39页（正文38页）表4.8名称为“较短时域节能方案”。发布说明进一步明确：较宽时域仍有更低能耗历史方案，此备选不是无时间限制的全局最低能耗。',
        '本轮实际调用fixed_D=0、delivery_mode=batch、objective=E，但没有设置max_C。软截止已对齐为整站零延期，缺少的是全部返航时间上限这一独立条件。题目本身要求说明多目标取舍，没有规定所有物资必须在100分钟内结束；不能把论文选定的短时域解释成原题统一硬约束。',
        '当前选择结果元数据requested_caps为空，未恢复当初求解时的精确C上限；5969.043477秒是已得返航值，不能直接当成原始cap，更不能凭空认定其为6000秒。后续公平节能对照应明确选择共同Cmax上限，统一约束后重跑各方法。此次只复查与修正解读，没有伪造有上限的新实验。',
        '## 可复核文件',
        '`audit.json`保存源指纹、两份完整重建指标及工作量下界；`whole_stop_deadline_comparison.csv`保存160条逐箱整站交付、期望与硬截止余量；两个方案各自目录保存原始物理重建的架次、箱件、航段与机体/电池资源时间轴。历史方案仅从归档ZIP选择性读取，没有运行旧bootstrap/env。']
    (DEST/'复查结论.md').write_text('\n\n'.join(report)+'\n',encoding='utf-8')
    print(json.dumps(dict(audits=audits,comparison=comparison),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
