"""Build the final evidence-backed Markdown/CSV and a shared PDF content model."""
import csv
import io
from pathlib import Path
from benchmark_v2 import V2,V1,load
from support import PROJECT,dump

BASE=V2/'main_600s_seed42'
DEST=PROJECT/'docs/current-project/contest-baselines-v2'
METHODS=['greedy','aco','alns','cp_sat']
LABELS={'greedy':'多起点贪心 / EDF','aco':'ACO','alns':'ALNS','cp_sat':'CP-SAT'}

def label(m,q):return LABELS[m]+(' + CP排程' if q=='Q3' and m!='cp_sat' else '')
def table(head,rows):
    return '\n'.join(['| '+' | '.join(head)+' |','|'+'|'.join(['---']*len(head))+'|']+['| '+' | '.join(map(str,r))+' |' for r in rows])

def main():
    checks=load(BASE/'final_checks.json');assert checks['all_checks_passed']
    records=load(BASE/'results.json');protocol=load(BASE/'protocol.json');timing=load(BASE/'completion.json')
    historical={r['scenario']:r for r in load(V1/'historical_reference.json')}
    DEST.mkdir(parents=True,exist_ok=True)
    intro=(
        '本轮完成16个配置，每配置搜索600秒，并从同一次连续搜索保留180秒与600秒的最佳可行方案。'
        '32份检查点结果全部通过独立物理核验，Q3另通过连续通信核验。'
        '旧版节能贪心的单次构造失败已修复：构造走入死路后改用时间评分重新构造，再进行多起点贪心搜索。'
        '没有放宽原题约束，没有使用论文路线或答案作初解，也没有重新运行论文方法。'
        '重要修正：本轮能耗组不设全部返航上限，论文Q2/Q3节能备选属于短时域方案，不能据本表作同约束的能耗优劣排名。')
    protocol_text=[
        '任务保持原题Q2/Q3：15个服务区、80个不可拆货箱，8架异构运输机和14组运输电池；Q3使用2架中继机及6个能源组件。',
        '全部80箱采用整站交接完成时刻计时，期望延期为零，并满足31箱硬截止；载质量、体积、逐段载荷能耗、DEM净空、返航SOC至少20%、机体/电池共享与两阶段充电要求保持不变。Q3核验全部通信开区间和事件边界，通信缺口与未确定区间均为零。',
        '时间目标为全部架次最晚返航时刻，Q3包含中继返航；资源目标为运输与中继总能耗kWh，架次数为辅助指标。本轮能耗组没有额外完成时间上限；论文Q2节能方案明确在完成时间上限内优化，Q3节能参考也保留99分钟内的历史条件。因此能耗参考仅作异条件的方案展示。',
        '四种方法共用850条运输候选、21个自动生成的中继驻点候选、至多4个中继架次槽，公共候选与v1完全相同。各方法从同一题目的同一份普通贪心/EDF可行初解出发，初解已独立核验，未读论文方案。',
        '公共可行初解的构造、Q3一次联合排程和核验单独计时，不计入每方法600秒；所有方法公平复用。公共输入、候选索引与初解加载在搜索前完成；搜索预算包含方案构造、模型建立、子求解、回调解码和搜索期写盘。最终独立核验另计，矩阵总墙钟包含进程启动与加载开销。',
        '固定随机种子42，最多4个独立进程并行，每个CP求解器单线程。墙钟预算受到系统后台负载影响，不承诺复现完全相同的迭代数；每行报告实际搜索墙钟。',
        '180秒与600秒结果来自同一次不中断搜索，CP-SAT通过可行解回调记录发现时刻，并保留不晚于阈值的最佳方案。时间以1e-6秒、能耗以1e-9kWh作浮点比较容差；同主目标时比较另一指标。',
        'v1的单次贪心、冷启动CP等旧结果完整保留；v2同时调整贪心与公共初解，不能把v1到v2的全部差异归因于延长时间。预算收益应比较本报告同版本的180秒与600秒。']
    methods=[
        ('多起点贪心 / EDF','每轮优先处理最早到期货箱，按时间/装载量与能耗/装载量的加权评分选择可行架次。初始化先尝试能耗评分，走入死路后用时间评分重新构造；后续在7种权重、若干装载指数与小幅随机扰动中重复贪心构造，保留完整可行解。它已不是旧版的一次性纯贪心。'),
        ('ACO','保留v1的蚁群式适配：在EDF焦点前10个可行候选中概率抽样，信息素指数1、启发式指数3、蒸发率0.1，并由当前最好路线沉积信息素。失败构造计入预算。'),
        ('ALNS','随机移除、高单位能耗移除、空间相关移除三类算子，破坏比例15%至40%；以随机可行重插修复，每25轮自适应更新权重，更新率0.2，并采用降温接受。公共初解保证失败修复不会丢失已有完整方案。'),
        ('CP-SAT','在完整公共路线池上进行精确覆盖选择与资源排程，采用0.1秒保守时间网格和整数能耗，使用与其它方法相同的可行初解。回调保存搜索中的中间解；限时状态与有限模型的最优性不能外推至原题。'),
        ('Q3共同排程','贪心、ACO、ALNS负责运输分组，公共CP排程负责给定分组的运输时序、中继驻点/窗口与能源分配，每次至多12秒且计入总预算；表中标注“+ CP排程”。CP-SAT行联合优化完整池的选择和排程。')]
    groups=[];summaries=[];csvrows=[]
    for q in ['Q2','Q3']:
        for o in ['time','energy']:
            title=f"{q} {'时间优先' if o=='time' else '能耗优先'}"
            selected=[r for r in records if r['question']==q and r['objective']==o]
            primary='completion_s' if o=='time' else 'energy_kwh'
            best={cp:min(selected,key=lambda r:r['checkpoints'][i]['metrics'][primary]) for i,cp in enumerate([180,600])}
            hist=historical[f"{q}_{'fast' if o=='time' else 'economy'}"]
            rows=[]
            for m in METHODS:
                r=next(r for r in selected if r['method']==m)
                for cp in r['checkpoints']:
                    mm=cp['metrics'];budget=cp['checkpoint_s']
                    rows.append([label(m,q),f'{budget:g}',f"{mm['completion_s']:.3f}",f"{mm['energy_kwh']:.3f}",
                        f"{mm['transport_sorties']} + {mm['relay_sorties']}",'通过'])
                    csvrows.append(dict(question=q,objective=o,method=m,method_label=label(m,q),checkpoint_s=budget,
                        completion_s=mm['completion_s'],energy_kwh=mm['energy_kwh'],transport_sorties=mm['transport_sorties'],relay_sorties=mm['relay_sorties'],
                        boxes=mm['boxes'],late_boxes=mm['late_boxes'],hard_violations=mm['hard_violations'],minimum_hard_slack_s=mm['minimum_hard_slack_s'],
                        search_wall_s=r['search_wall_s'],best_found_s=cp['best_found_s'],status=cp['status'],solution_sha256=cp['solution_sha256']))
            rows.append(['论文短时域备选' if o=='energy' else '论文历史参考','未匹配',f"{float(hist['C']):.3f}",f"{float(hist['E']):.3f}",
                f"{hist.get('N_transport') or hist['N']} + {hist.get('N_relay') or 0}",'历史记录'])
            cp_path=BASE/f'{q}_{o}_cp_sat'
            cp_stages=load(cp_path/'cp_evidence.json')['evidence'] if q=='Q2' else load(cp_path/'decoders/full_pool/solver_evidence.json')
            cp_note='CP-SAT最终内部状态：'+', '.join(f"{s['stage']}={s['status']}" for s in cp_stages)+'；表中“通过”表示保留方案通过独立核验，不代表求解器证明最优。若未找到改善，则保留公共初解。'
            v180=best[180]['checkpoints'][0]['metrics'][primary];v600=best[600]['checkpoints'][1]['metrics'][primary]
            reference=float(hist['C' if o=='time' else 'E'])
            gain=(v180-v600)/v180*100;reference_gain=(v600-reference)/v600*100
            units='秒' if o=='time' else 'kWh'
            comparison=f"{title}组内的最佳已得基线从180秒预算下的{v180:.3f}{units}变为600秒下的{v600:.3f}{units}，主目标降低{gain:.2f}%。600秒组内最佳来源为{label(best[600]['method'],q)}。论文历史参考为{reference:.3f}{units}，相对600秒组内最佳基线{'降低' if reference_gain>=0 else '增加'}{abs(reference_gain):.2f}%。该历史差异包含预算与候选空间差异。"
            if o=='energy':
                paired=best[600]['checkpoints'][1]['metrics']
                comparison=f"{title}组内的最佳已得基线从180秒预算下的{v180:.3f}{units}变为600秒下的{v600:.3f}{units}，主目标降低{gain:.2f}%。600秒组内最佳来源为{label(best[600]['method'],q)}，全部返航{paired['completion_s']:.3f}秒。论文短时域备选为{reference:.3f}kWh、{float(hist['C']):.3f}秒；本轮无返航上限，论文备选有短时域要求，优化条件没有对齐，不能据能耗数值作方法优劣排名。"
            group=dict(title=title,question=q,objective=o,headers=['方法','预算s','全部返航s','总能耗kWh','运输 + 中继','状态'],rows=rows,comparison=comparison,cp_note=cp_note)
            groups.append(group)
            summaries.append(dict(question=q,objective=o,best_180_method=best[180]['method'],best_600_method=best[600]['method'],
                best_180=v180,best_600=v600,budget_gain_pct=gain,historical=reference,historical_reduction_vs_600_pct=None if o=='energy' else reference_gain,
                historical_energy_comparison='not aligned: final-return time cap' if o=='energy' else None,
                display=[title,f'{v180:.3f}',f'{v600:.3f}',f'{gain:.2f}%',f'{reference:.3f}']))
    wall=timing['experiment_wall_s']/60;prep=protocol['common_initial_manifest']['common_preprocessing_wall_s']
    pilot=load(V2/'pilot_12s/completion.json')['experiment_wall_s']
    timing_text=(f"名义搜索预算为16 × 600秒 = 160分钟累计配置预算；4进程并行，矩阵实际墙钟{wall:.2f}分钟。"
        f"实测累计搜索墙钟{timing['sum_search_wall_s']/60:.2f}分钟，包含最终核验的累计配置墙钟{timing['sum_total_wall_s']/60:.2f}分钟。"
        f"公共初解构造与核验另计{prep:.2f}秒；850路线、21驻点与通信原子的公共预处理沿用v1缓存，其v1实测25.64秒。"
        f"正式实验前10配置短预算预检实测墙钟{pilot:.2f}秒，单独保存，不混入正式成绩。"
        '新增600秒实验同时提供180秒检查点，没有再为180秒单独占用16次预算。整体人工等待还包括实现、预检、报告和版面检查，不等于搜索墙钟。')
    # Also expose stronger plans found under the other objective, or in retained v1 runs.
    strongest=[]
    old=load(V1/'matrix_180s_seed42/results.json')+load(V1/'cp_energy_warm_180s/results.json')
    for q in ['Q2','Q3']:
        for o in ['time','energy']:
            field='completion_s' if o=='time' else 'energy_kwh'
            candidates=[dict(value=r['checkpoints'][-1]['metrics'][field],origin=f"v2 {r['objective']} / {label(r['method'],q)}") for r in records if r['question']==q]
            old_candidates=[dict(value=r['metrics'][field],origin=f"v1 {r['objective']} / {r['method']}") for r in old if r['question']==q and r.get('metrics')]
            best_new=min(candidates,key=lambda r:r['value']);best_old=min(old_candidates,key=lambda r:r['value'])
            overall=min([best_new,best_old],key=lambda r:r['value'])
            strongest.append([f"{q} {'时间s' if o=='time' else '能耗kWh'}",f"{best_old['value']:.3f}",f"{best_new['value']:.3f}",overall['origin']])
    unchanged=[x['run'] for x in checks['runs'] if x['final_is_initial']]
    unchanged_text='600秒仍保留公共初解的配置：'+('、'.join(unchanged) if unchanged else '无')+'。这反映当前实现的搜索效果；不表示原问题无更优解。'
    minimum_slack=min(c['metrics']['minimum_hard_slack_s'] for r in records for c in r['checkpoints'])
    limits=[
        '每配置只有一个种子，不报告均值、标准差、置信区间或统计显著性；四种任务目标不构成多个独立问题实例。',
        f'全部检查点满足确定性截止，但最小硬截止余量仅{minimum_slack:.6f}秒。本轮未加任务时长或能耗扰动，不能据此宣称现场鲁棒性；完整余量随CSV和核验文件给出。',
        '论文参考没有重跑，论文历史过程的总预算和候选空间未匹配；能耗组与论文短时域节能备选还缺少全部返航上限的对齐。不能支持同条件的能耗排名、“同预算全面领先”或“击败CP-SAT求解器”的结论。论文方法本身也包含CP-SAT。',
        '本轮实现是在本题上的贪心、蚁群式、ALNS和有限池CP-SAT适配；Q3前三者均与CP排程组合，不能视为纯方法或原作者官方复现。DeepACO、PSO、WOA本轮未运行。',
        '候选路线池850条、驻点21个和4个中继架次槽均有限，不能据此证明原题全局最优。能耗目标不设额外返航时间上限，低能耗解可能明显更慢。',
        '新旧版本同时改变了可行初解机制和贪心实现，因此旧版到新版的变化包含实现改进；预算效应用本轮同一次搜索的两个检查点评估。',
        '论文数值是历史研究方案；本轮是独立离线实验，未修改V4业务求解器、接口或数据库，不能将这些结果作为当前网页引擎的实时性能。']
    evidence_text=(
        '主结果：evidence/contest-baselines-v2/main_600s_seed42/results.json与results.csv；协议与冻结代码：protocol.json、source_snapshot/；'
        '每配置保存checkpoint_180s_solution.json、checkpoint_600s_solution.json、各自validation.json、run.json及求解日志。'
        'final_checks.json核对16配置、32检查点、方案哈希、数值、公共初解指纹、源代码/候选指纹和检查点时刻；'
        '物理与通信核验在每次正式运行结束后独立重建完成。旧版核验器负例证据仍保存在evidence/contest-baselines-v1/verifier_tests.json及通信负例检查记录。'
        '论文参考来自evidence/contest-baselines-v1/historical_reference.json，精度来源为references/modeling/release/accepted_metrics.csv；原始论文、答案及输入与用户原件的指纹对照见v1/input_verification.json。')
    prose=('在原题第二问与第三问上，以全部返航时间和运输/中继总能耗分别为目标，设置多起点贪心、蚁群式搜索、自适应大邻域搜索与有限池CP-SAT四类对照。'
        '各方法使用统一候选集和公共可行初解，每配置搜索10分钟，并保存同次搜索第3分钟的方案。32个检查点均满足整站零延期、硬截止、载荷、返航安全电量和资源周转约束，联合调度方案同时通过连续通信核验。'
        '实验展示了搜索预算与方法适配对方案质量的影响；论文历史方案作为异条件的可行质量参考，因预算、候选空间及节能方案的返航上限未匹配，不据此声称同条件的能耗优势或同预算普遍优势。')
    lines=['# 援航原题Q2/Q3十分钟基线对比实验','日期：2026年10月19日　任务：EXP-C02　矩阵：main_600s_seed42',intro,
        'Q2截止条件专项复查见[复查结论](../../../evidence/contest-baselines-v2/q2_alignment_audit/复查结论.md)：61.6265kWh方案80箱期望延期和31箱硬截止违反均为零；缺少的对齐项是全部返航时间上限。',
        '## 实验口径']+[f'- {t}' for t in protocol_text]+['## 方法实现']+[f'**{a}**：{b}' for a,b in methods]+['## 结果对比']
    for g in groups:lines += ['### '+g['title'],table(g['headers'],g['rows']),g['comparison'],g['cp_note']]
    lines += ['## 相同版本的预算收益',table(['任务/目标','180秒最佳','600秒最佳','主目标降低','论文历史参考'],[s['display'] for s in summaries]),
        '每列最佳可来自不同方法；这是已运行配置的结果汇总，不是额外一个搜索算法。时间列单位为秒，能耗列单位为kWh；各行方案数值保持配对，未拼接不同方案的时间和能耗。',
        '## 全部已知基线交叉检查',table(['指标','v1全部目标最小值','v2全部目标最小值','两版本最低值来源'],strongest),
        '此表跨时间/能耗两组及新旧版本寻找已知较强方案，避免遗漏对照。它累计使用了多次不同预算、不同初始化的运行，不能作为单次600秒算法成绩。',
        unchanged_text,'## 核验与可复现性',evidence_text,'## 时间预算与实测',timing_text,'## 适用边界']+[f'- {t}' for t in limits]+[
        '## 可用于项目文档的表述',prose,'## 复现命令',
        '```powershell\n# 原始候选与公共初解已有；重新运行应使用新目录保留旧证据\n.venv/Scripts/python.exe scripts/contest_baselines/matrix_v2.py --name rerun_600s_seed42\n# check_v2.py针对本次主矩阵逐项核对\n.venv/Scripts/python.exe scripts/contest_baselines/check_v2.py\n```',
        '共同初解生成器为benchmark_v2.py prepare（仅用于新建common_initial目录）；求解回调修改的来源和差异见prepare_v2_solvers.py与solver_sources.json。完整参数以已保存protocol.json为准。']
    (DEST/'对比实验报告.md').write_text('\n\n'.join(lines)+'\n',encoding='utf-8')
    with (DEST/'完整结果对比.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(csvrows[0]));writer.writeheader();writer.writerows(csvrows)
    content=dict(intro=intro,protocol=protocol_text,methods=methods,groups=groups,summaries=summaries,timing=timing_text,
        unchanged=unchanged_text,limits=limits,evidence=evidence_text,project_prose=prose,completion=timing,
        strongest=strongest,source='evidence/contest-baselines-v2/main_600s_seed42/results.json')
    dump(V2/'report_content.json',content)
    print('Final Markdown / 32-row CSV / PDF content model generated')

if __name__=='__main__':main()
