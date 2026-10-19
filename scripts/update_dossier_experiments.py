"""Reconcile archived v6 results and write the dossier experiment chapter.

Reads sealed artifacts only. Does not import contest code, run a solver, modify
experiment outputs, or access the application database. Run before the DOCX
generator when the frozen experiment records are intentionally updated.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "evidence/contest-baselines-v6/monitored_600s_r2_seed42"
OUT = ROOT / "docs/current-project/contest-baselines-v6"
AUDIT = ROOT / "evidence/project-dossier-v13"
METHODS = [("greedy", "Greedy 贪心"), ("aco", "ACO 蚁群"), ("alns", "ALNS"), ("cp_sat", "CP-SAT")]
GROUPS = [(q, o) for q in ("Q2", "Q3") for o in ("time", "energy")]
# User-supplied historical reference values, not rerun by this documentation task.
HISTORY = {
    ("Q2", "time"): (5693.243, 66.214866, 23, 0),
    ("Q2", "energy"): (5969.043, 64.734132, 22, 0),
    ("Q3", "time"): (5783.227, 68.681772, 23, 3),
    ("Q3", "energy"): (5939.704, 67.714664, 23, 3),
}
# Completion, total energy, transport energy, relay energy, sorties, first, final.
EXPECTED = {
    ("Q2", "time", "greedy"): ("6881.327", "67.266389", "67.266389", "0.000000", 23, "1.59", "194.27"),
    ("Q2", "time", "aco"): ("6744.619", "65.762730", "65.762730", "0.000000", 23, "1.53", "3.74"),
    ("Q2", "time", "alns"): ("6217.426", "66.650023", "66.650023", "0.000000", 25, "1.63", "252.61"),
    ("Q2", "time", "cp_sat"): ("5912.004", "67.252002", "67.252002", "0.000000", 23, "4.15", "487.55"),
    ("Q2", "energy", "greedy"): ("5987.452", "66.443583", "66.443583", "0.000000", 23, "38.74", "232.78"),
    ("Q2", "energy", "aco"): ("5979.328", "66.825535", "66.825535", "0.000000", 25, "9.99", "9.99"),
    ("Q2", "energy", "alns"): ("5987.452", "66.443583", "66.443583", "0.000000", 23, "19.09", "239.98"),
    ("Q2", "energy", "cp_sat"): ("5973.368", "66.124664", "66.124664", "0.000000", 25, "8.05", "83.06"),
    ("Q3", "time", "greedy"): ("6024.227", "70.177475", "67.082524", "3.094951", 23, "2.96", "28.78"),
    ("Q3", "time", "aco"): ("6377.371", "70.616179", "67.252002", "3.364176", 23, "2.99", "2.99"),
    ("Q3", "time", "alns"): ("5964.227", "70.417494", "67.323307", "3.094188", 23, "2.97", "572.97"),
    ("Q3", "time", "cp_sat"): ("5770.677", "69.964281", "66.815307", "3.148974", 23, "3.13", "599.92"),
    ("Q3", "energy", "greedy"): ("5900.277", "69.602884", "66.443583", "3.159301", 23, "23.28", "162.53"),
    ("Q3", "energy", "aco"): ("5886.277", "69.966053", "66.815307", "3.150746", 23, "55.15", "82.48"),
    ("Q3", "energy", "alns"): ("5939.668", "69.707250", "66.565518", "3.141732", 23, "35.83", "152.34"),
    ("Q3", "energy", "cp_sat"): ("5939.804", "69.412316", "66.449028", "2.963288", 23, "3.18", "598.73"),
}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def table(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)] +
                     ["| " + " | ".join(map(str, row)) + " |" for row in rows])


def main():
    records = load(BASE / "results.json")
    protocol, completion = load(BASE / "protocol.json"), load(BASE / "completion.json")
    assert completion["complete"] and completion["feasible_final_runs"] == len(records) == 16
    assert not completion["source_changes"] and not completion["physical_input_changes"]
    assert protocol["seed"] == 42 and protocol["seconds_per_configuration"] == 600
    assert not any(protocol[k] for k in ("supplied_initial_solution", "supplied_warm_start", "paper_solution_used"))
    indexed, audited, evidence_files = {}, [], set()
    for r in records:
        key = r["question"], r["objective"], r["method"]
        assert key not in indexed and r["status"] == "COMPLETED"
        assert not r["program_failure"] and not r["validation_errors"]
        assert not any(r[k] for k in ("supplied_initial_solution", "supplied_warm_start", "paper_solution_used"))
        cp = next(c for c in r["checkpoints"] if c["checkpoint_s"] == 600)
        assert cp["status"] == "VALIDATED_FEASIBLE" and cp["best_found_s"] <= 600
        solution_path = ROOT / cp["solution_path"]
        validation_path = solution_path.with_name("checkpoint_600s_validation.json")
        v = load(validation_path)
        assert digest(solution_path) == cp["solution_sha256"] == v["solution_sha256"]
        assert v["status"] == "passed" and v["transport"]["summary"]["valid"]
        t, station = v["transport"]["summary"], v["station"]
        radio = (v.get("radio") or {}).get("summary")
        assert t["boxes"] == t["unique_boxes"] == 80 and t["mass_kg"] == 758 and t["volume_L"] == 2011
        assert station["late_boxes"] == station["hard_violations"] == 0 and t["hard_violations"] == 0
        assert t["min_SOC"] >= .2
        m = cp["metrics"]
        if radio:
            assert radio["valid"] and radio["gap_seconds"] == radio["unknown_intervals"] == 0
            assert abs(radio["E_total"] - m["energy_kwh"]) < 1e-9
            assert abs(radio["C_joint"] - m["completion_s"]) < 1e-8
        else:
            assert abs(t["E"] - m["energy_kwh"]) < 1e-9
        if r["objective"] == "energy":
            assert m["completion_s"] <= protocol["energy_caps"][r["question"]]
        expected = EXPECTED[key]
        values = (f'{m["completion_s"]:.3f}', f'{m["energy_kwh"]:.6f}', f'{t["E"]:.6f}',
                  f'{radio["E_relay"] if radio else 0:.6f}', m["transport_sorties"],
                  f'{r["first_found_s"]:.2f}', f'{cp["best_found_s"]:.2f}')
        assert values == expected, (key, values, expected)
        r = dict(r, final=cp, validation=v)
        indexed[key] = r
        audited.append(dict(question=key[0], objective=key[1], method=key[2],
            completion_s=m["completion_s"], total_energy_kwh=m["energy_kwh"],
            transport_energy_kwh=t["E"], relay_energy_kwh=radio["E_relay"] if radio else 0,
            transport_sorties=m["transport_sorties"], relay_sorties=m["relay_sorties"],
            first_found_s=r["first_found_s"], best_found_s=cp["best_found_s"],
            search_wall_s=r["search_wall_s"], process_end_elapsed_s=r["process_end_elapsed_s"],
            minimum_hard_slack_s=station["minimum_hard_slack_s"],
            min_transport_soc=t["min_SOC"], min_relay_soc=radio["min_relay_SOC"] if radio else None,
            gap_seconds=radio["gap_seconds"] if radio else None,
            unknown_intervals=radio["unknown_intervals"] if radio else None,
            solution_path=cp["solution_path"], solution_sha256=cp["solution_sha256"],
            validation_path=validation_path.relative_to(ROOT).as_posix()))
        evidence_files.update([solution_path, validation_path])
    # CSV has four checkpoints per configuration; it is not 64 independent runs.
    csv_rows = list(csv.DictReader(io.StringIO((BASE / "results.csv").read_text(encoding="utf-8-sig"))))
    assert len(csv_rows) == 64
    for row in csv_rows:
        r = indexed[(row["question"], row["objective"], row["method"])]
        cp = next(c for c in r["checkpoints"] if c["checkpoint_s"] == float(row["checkpoint_s"]))
        assert row["status"] == cp["status"]
        if cp["metrics"]:
            for k in ("completion_s", "energy_kwh", "transport_sorties", "relay_sorties"):
                assert abs(float(row[k]) - cp["metrics"][k]) < 1e-9
    optimal = load(BASE / "Q2_energy_cp_sat/cp_evidence.json")["evidence"]
    assert len(optimal) == 2 and all(e["status"] == "OPTIMAL" for e in optimal)
    assert optimal[0]["pool_size"] == 272
    assert indexed[("Q2", "energy", "greedy")]["final"]["solution_sha256"] == indexed[("Q2", "energy", "alns")]["final"]["solution_sha256"]
    # Verify immutable experiment fingerprints; no expensive search is repeated.
    for group in (protocol["physical_input_sha256"], protocol["source_sha256"]):
        for name, sha in group.items():
            p = ROOT / name
            if name.startswith("scripts/"):
                p = BASE / "source_snapshot" / p.name
            assert p.is_file() and digest(p) == sha, name

    sections = ["""## 25 独立传统基线实验与申报引用

### 25.1 当前有效实验和主要发现

截至2026年10月19日晚，最新完整批次为contest-baselines-v6/monitored_600s_r2_seed42，已经完成Q2运输和Q3运输与通信协同、时间与能耗两个目标、四种方法的16次独立搜索。每次名义预算600秒，随机种子42，16套最终方案均通过独立检查。本章完整保留方案质量、首次可行解与最终保留方案的发现时间、实际运行记录时长、能耗分项及校验数据，可直接为申报书和PPT提供带来源的实验素材。

CP-SAT在本批四个小组中分别得到四种新跑方法里最好的主目标数值；这只描述本题、此种子和此预算下的观测结果。相对于论文历史方案，它并非所有指标都占优：Q3时间组快约12.55秒，但多耗约1.283kWh；论文历史方案在其余三个小组的对应主目标上仍更好。论文未按本轮协议重跑，不能据此宣布同预算下论文方法优于或劣于这些方法。该批实验也没有运行EOH、LLM进化或在线双引擎对照。

### 25.2 数据 预算与实验协议

原题使用15个需求点、80箱物资，总质量758kg、总体积2011L；保留三型8架运输无人机、14块运输电池，以及Q3的2架中继机、6套中继能源组件。Q2仅排运输；Q3还须安排中继，且从连续时间重建通信保障。共同条件包括完整逐箱交付、整站零期望延期、硬截止、载重容积、地形升降能源、兼容机体与电池周转及最低返航SOC。零期望延期、硬截止和全部返航时域是不同约束，不能相互代替。

时间组按完成时间优先搜索，不额外强加6000秒或5939.9秒返航上限；能耗组在Q2全部返航不超过6000秒、Q3运输与中继全部返航不超过5939.9秒的条件下优先降低总能耗。所有组都不设置按论文成果反推的总能耗或架次数门槛，架次数由实际方案决定。它们是独立运行，不能把一个目标实验的最好方案补进另一个目标实验。

每配置从自己的初解构造开始，外部可行初解、公共可行初解、论文解和预热解均未导入。各配置使用相同的物理输入及公共有限候选资料；共用的是数据和候选，不是现成方案。输入与候选的读取、既有候选生成成本不计入600秒，初解构造、模型建立、排程解码和搜索改进在预算内，父进程的最终独立核验在预算外。因此600秒不是从原始Excel/DEM到最终报告的端到端耗时。

协议最多同时运行16个配置，每个CP求解使用1个worker；保存同次搜索30、60、180、600秒检查点。整批墙钟742.146秒，各配置search_wall_s合计9111.027秒；这些分别是并发实验总历时和累计记录时长，不能互换，也不能按独占CPU的速度基准解释。协议没有保存足够的CPU型号、内存和负载快照，不补造硬件性能结论。

本批开始于北京时间2026年10月19日22时04分40秒，结束于22时17分02秒。completion.json记录16/16最终可行、未发生程序失败或输入/代码指纹变化。原始CSV有64行，对应16次搜索各4个检查点，不是64次独立实验。

### 25.3 四种方法的实际实现

Greedy是问题适配的多起点贪心，按可行箱件组批、截止和资源条件构造并继续尝试；不是一次排序后立即结束的教材单遍贪心。ACO先在自己的预算内构造首解，再按路线信息素和随机选择搜索；信息素在本次运行内部更新。ALNS从自己的首解出发，按随机、能耗较高和空间相关等策略移除部分路线，再修复、按收益更新算子权重。

三种启发式均结合原题适配的覆盖与资源排程。Q3还使用候选中继服务模板和CP约束排程，因此不能将它们称为完全不含约束规划的纯Greedy、纯ACO或纯ALNS。Q3能耗ACO在预算内触发独立CP首解恢复，保留或逐步放宽自身提出的路线分组约束，得到首解后继续蚁群搜索；这不是导入外部或公共初解，混合机制必须与结果一起披露。

CP-SAT使用有限路线及中继候选建立约束模型，安排逐箱覆盖、机体与电池、地面周转及通信服务时间。Q2使用路线池模型；Q3先独立建立自己的可行模板解，再对自己的当前解进行联合改进。模型采用0.1秒保守资源时间包络，报告中的完成时间和能耗使用独立检查器重建的连续值，不使用取整模型目标替代。Q2节能的272路线有限模型，能源和次级完成时间两阶段均记录OPTIMAL；这不证明任意路线、任意连续飞行方案的原问题全局最优。

### 25.4 指标定义和读表约定

完成时间是运输与中继全部返航的最晚时刻，Q2没有中继。总能耗为任务模型中的运输能源与中继能源之和，不包含没有建模的场地用电。运输与中继架次分别计数，同一机体可承担多个架次，23＋3不表示使用26架无人机。首解耗时是本次搜索首次发现可行方案的时刻；最终方案发现是最终保留方案在搜索中被发现的时刻，两者都不是完整运行结束时间。

下表完成时间保留3位小数，能耗6位，发现时刻2位；计算与比较使用原始浮点值。论文历史记录没有本轮搜索耗时，Q3也没有汇总可引用的运输/中继能耗分项，统一用“—”，不反推补填。各能耗分项独立四舍五入，末位可能出现舍入差。"""]

    titles = {
        ("Q2", "time"): "25.5 Q2以完成时间最短为目标",
        ("Q2", "energy"): "25.6 Q2以总能耗最低为目标",
        ("Q3", "time"): "25.7 Q3以完成时间最短为目标",
        ("Q3", "energy"): "25.8 Q3以总能耗最低为目标",
    }
    for q, objective in GROUPS:
        intro = ("本组仅运输，总能耗全部来自运输。" if q == "Q2" else "本组总能耗包含运输与中继，两类架次分列合并表示。")
        if objective == "energy":
            intro += "共同返航上限为" + ("6000秒。" if q == "Q2" else "5939.9秒。")
        else:
            intro += "本组没有另设能耗组的全部返航上限，仍须满足各项交付与安全约束。"
        headers = ["方法", "完成时间 s", "总能耗 kWh"]
        if q == "Q3": headers += ["运输 kWh", "中继 kWh"]
        headers += ["运输架次" if q == "Q2" else "运输＋中继", "首解 s", "最终发现 s"]
        rows = []
        for method, label in METHODS:
            r = indexed[(q, objective, method)]
            m, v = r["final"]["metrics"], r["validation"]
            row = [label, f'{m["completion_s"]:.3f}', f'{m["energy_kwh"]:.6f}']
            if q == "Q3":
                row += [f'{v["transport"]["summary"]["E"]:.6f}', f'{v["radio"]["summary"]["E_relay"]:.6f}']
            row += [str(m["transport_sorties"]) if q == "Q2" else f'{m["transport_sorties"]}＋{m["relay_sorties"]}',
                    f'{r["first_found_s"]:.2f}', f'{r["final"]["best_found_s"]:.2f}']
            rows.append(row)
        hc, he, hn, hr = HISTORY[(q, objective)]
        historical = ["论文历史方案", f"{hc:.3f}", f"{he:.6f}"]
        if q == "Q3": historical += ["—", "—"]
        historical += [str(hn) if q == "Q2" else f"{hn}＋{hr}", "—", "—"]
        rows.append(historical)
        sections.append("### " + titles[(q, objective)] + "\n\n" + intro + "\n\n" + table(headers, rows))
        if (q, objective) == ("Q2", "energy"):
            sections.append("Greedy与ALNS独立得到了相同最终方案，封存方案SHA256也相同；所以完成时间、能耗和架次一致，但首解及最终发现时刻不同。不能因为数值相同就认为前端固定返回示例。该组CP-SAT的最佳解在83.06秒发现，96.56秒结束，有限模型最优证明发生在发现解之后。")
        if (q, objective) == ("Q3", "time"):
            sections.append("CP-SAT本次完成时间5770.677秒，比论文历史5783.227秒早约12.550秒；总能耗69.964281kWh，比历史68.681772kWh增加1.282509kWh。它体现时间与能源的取舍，不能概括为两指标全面提升。")

    timing_rows = []
    for q, o in GROUPS:
        for method, label in METHODS:
            r = indexed[(q, o, method)]
            timing_rows.append([q + ("时间" if o == "time" else "节能"), label,
                f'{r["first_found_s"]:.2f}', f'{r["final"]["best_found_s"]:.2f}',
                f'{r["search_wall_s"]:.3f}', f'{r["process_end_elapsed_s"]:.3f}',
                "有限模型最优结束" if not r["hard_stop"] else "截止终止"])
    sections.append("""### 25.9 完整求解过程耗时

下面补充每配置实际记录，不把最终方案发现时刻当作运行结束。记录时长为原JSON的search_wall_s；进程结束为process_end_elapsed_s，均从本配置搜索计时起点计。输入加载与最终父进程核验另计。部分终止路径记录略超过600秒，截止监控、终止与写记录存在开销；可采纳方案的发现时间仍必须不超过600秒，不能把超出部分包装成更长搜索预算。""" + "\n\n" + table(
        ["配置", "方法", "首解 s", "最终发现 s", "记录时长 s", "进程结束 s", "结束方式"], timing_rows))
    sections.append("除Q2节能CP-SAT在96.563秒提前结束外，其余15配置均搜索至截止。ACO等方法在很早发现最终保留方案后仍继续搜索，没有把3.74秒或2.99秒描述成整次求解耗时。截止终止产生的系统终止码不等于程序错误，completion.json与program_failure字段共同记录完成状态。")

    validation_rows = []
    ordered = []
    for q, o in GROUPS:
        for method, label in METHODS:
            a = next(x for x in audited if (x["question"], x["objective"], x["method"]) == (q, o, method))
            ordered.append(a)
            validation_rows.append([q + ("时间" if o == "time" else "节能"), label,
                f'{a["minimum_hard_slack_s"]:.3f}', f'{100*a["min_transport_soc"]:.6f}',
                "—" if a["min_relay_soc"] is None else f'{100*a["min_relay_soc"]:.3f}',
                "—" if q == "Q2" else "0 / 0"])
    sections.append("""### 25.10 交付 安全与通信的独立检查

16套最终方案全部完成80箱不重不漏交付，每套758kg、2011L；整站延期箱数、硬截止违规、运输检查错误均为0。运输最低返航SOC均为20.095847%，满足至少20%；该值是整套方案所有运输架次中的最小值，不表示每架次都恰好剩20.095847%。全体方案最小整站硬截止裕量39.465秒，意味着在本确定性输入下仍有该余量，不构成对真实气象或测量误差的鲁棒安全保证。

8套Q3方案的连续通信缺口均0秒、未知区间均0；各方案最低中继返航SOC范围45.550%至48.469%。连续检查范围为冻结的原高程投影凸四边形、2毫米足迹缓冲与有限精度模型，并有独立GEOS射线交叉检查，不等于实地无线覆盖认证。8套节能方案分别满足Q2 6000秒和Q3 5939.9秒上限。

下表逐方案列出最紧整站硬截止余量与最低SOC。通信列按“缺口秒数 / 未知区间数”表示；Q2未要求中继通信检查，记“—”，不能写成已验证了Q3通信。""" + "\n\n" + table(
        ["配置", "方法", "截止裕量 s", "运输SOC %", "中继SOC %", "通信缺口 / 未知"], validation_rows))
    sections.append("整站硬截止裕量取validation.station.minimum_hard_slack_s，避免误用运输逐箱summary的同名近似指标；两者对首箱规则的处理口径不同。零违规和100%交付是这16套已封存方案的核验结果，不能外推为任意输入必有解或真实机群100%可靠。")

    compare_rows = []
    for q, o in GROUPS:
        r = indexed[(q, o, "cp_sat")]["final"]["metrics"]
        hc, he, _, _ = HISTORY[(q, o)]
        dc, de = r["completion_s"] - hc, r["energy_kwh"] - he
        compare_rows.append([q + ("时间" if o == "time" else "节能"), f"{dc:+.3f}",
            f"{100*dc/hc:+.3f}", f"{de:+.6f}", f"{100*de/he:+.3f}"])
    sections.append("""### 25.11 与论文历史方案的取舍

以下仅计算本轮CP-SAT方案减去对应论文历史方案的观测差值，百分比分母为历史值；正数表示更大，完成时间或能耗越小越好。它们用于解释结果，不是同预算算法优势或统计显著性检验。历史原值采用本次提供的完成时间3位和能耗6位精度，差值保留相同报告精度。""" + "\n\n" + table(
        ["组别", "完成时间差 s", "时间差 %", "总能耗差 kWh", "能耗差 %"], compare_rows))
    gain_rows = []
    for q, o in GROUPS:
        g = indexed[(q, o, "greedy")]["final"]["metrics"]
        c = indexed[(q, o, "cp_sat")]["final"]["metrics"]
        k, unit = ("completion_s", "秒") if o == "time" else ("energy_kwh", "kWh")
        gain_rows.append([q + ("时间" if o == "time" else "节能"),
            f'{g[k]-c[k]:.3f}' + unit, f'{100*(g[k]-c[k])/g[k]:.3f}%'])
    sections.append("在本批同组观测中，以各组Greedy实际结果为分母，CP-SAT对应主目标的下降量如下。它只比较本次这两种问题适配实现，不代表原论文方法、EOH、真实部署收益或广义算法排名。\n\n" + table(
        ["组别", "相对Greedy的主目标下降量", "相对Greedy下降比例"], gain_rows))
    sections.append("时间与节能分别独立运行，有限预算、搜索路径和目标排序不同，所以节能组可能偶然比时间组更快。例如Q2的CP-SAT节能方案5973.368秒比其时间方案5912.004秒慢；而Greedy节能5987.452秒反而比其时间方案6881.327秒快。应保留原始结果并解释搜索不保证全局最优，不交叉替换方案制造漂亮排名。")

    sections.append("""### 25.12 可用于申报书和PPT的实验表述

可直接改写的研究基础段落：围绕15点80箱原题，我们构建了运输调度与运输通信协同两类基准，分别在完成时间和受返航时域约束的能源目标下，对Greedy、ACO、ALNS及CP-SAT的问题适配实现开展600秒单配置预算实验。随机种子42下的16套最终方案均通过独立交付、硬截止、资源与能源检查，8套通信联合方案的连续通信缺口和未知区间均为零。CP-SAT在本批四个目标组中获得四种新跑方法里的最低主目标值；其Q3时间方案在5770.677秒内完成，能源69.964281kWh，体现可量化的时间能源取舍。实验仅为单实例单种子，不作全局最优、统计显著性或真实机群性能声明。

PPT建议用三页讲清楚：第一页列协议、15点80箱、四方法、两题两目标、600秒和无外部初解；第二页呈现四组完整结果或四张同组条形图，时间与能源分单位，论文单独标“历史参考”；第三页展示80箱完整交付、零延期/违规、SOC及通信核验，并说明Q3的12.55秒与1.283kWh取舍。若需时间能源散点图，每个点是一套实际方案，不画未证明的连续Pareto前沿。

报表来源可写：援航原题Q2/Q3独立基线实验，批次monitored_600s_r2_seed42，2026年10月19日，seed=42，单配置600秒；指标来自sealed/checkpoint_600s_solution.json及其独立validation.json。统计分母为16个配置，其中Q3为8个；不得把检查点数当样本量。不要将历史论文引用、当前V4业务引擎和本批离线研究脚本合并为同一实验方法。

### 25.13 后续研究

后续研究计划是在当前协议下增加多个随机种子和需求、设备变化实例，报告结果波动与可行率；另行开展EOH策略训练、留出测试和消融。这些尚未完成，不影响本章16套最终方案结果的使用。

### 25.14 结果文件与维护入口

原始批次记录：`evidence/contest-baselines-v6/monitored_600s_r2_seed42/results.json`、`results.csv`、`protocol.json`、`completion.json`。每个Q2/Q3_目标_方法目录中的sealed/checkpoint_600s_solution.json是实际封存方案，旁边validation.json包含逐项独立核验；其他检查点和trace供收敛分析。Q2节能CP最优证据见Q2_energy_cp_sat/cp_evidence.json。source_snapshot保存运行时脚本指纹对应的源码，protocol保存输入、候选及代码hash。大型候选几何缓存不随本次文档提交重复上传；重新计算前需按协议恢复并核对输入，不能只拿结果CSV当求解器输入。

供本子和PPT复用的16方案总表、64检查点总表、16方案原始精度核对记录放在docs/current-project/contest-baselines-v6/；本次文档同步证据在evidence/project-dossier-v13/。更新时先核对新的封存结果与协议，再运行scripts/update_dossier_experiments.py更新本章和数据投影，随后以scripts/build_project_dossier.py生成Word及接手提示词，实际渲染检查版面。后续新实验单独归档，并以最终结果更新本章。""")
    chapter = "\n\n".join(sections).rstrip() + "\n"
    master = ROOT / "docs/PROJECT_DOSSIER.md"
    source = master.read_text(encoding="utf-8")
    source = source.split("## 25 独立传统基线实验与申报引用")[0] + chapter
    source = source.replace("版本：1.2　", "版本：1.3　")
    source = source.replace("产品阶段：V4完整参考交付与离线策略增强", "产品阶段：V4完整参考交付与600秒独立基线实验")
    start = source.index("原题传统方法补充实验见第25章")
    end = source.index("\n五、修改接口", start)
    source = source[:start] + (
        "原题对比实验只按第25章最新最终批次呈现：v6/monitored_600s_r2_seed42，16套完整方案。\n"
        "写本子/PPT先读实验协议、四组结果及校验，精确值和来源见第25.14节，不增加早期试验过程。\n"
        "固定seed=42，每配置600秒，无外部/公共初解；论文仅历史参考，CP最优证明限于有限候选模型。\n"
        "本批是传统方法对比，EOH训练与多种子验证属于后续研究。\n"
    ) + source[end:]
    marker = "## 19 部署 数据交接与日常运行"
    if "### 18.5 已有对比实验数据入口" not in source:
        source = source.replace(marker, "### 18.5 已有对比实验数据入口\n\n"
            "第25章现有16套600秒独立方案的四组完整表格、搜索耗时、SOC/通信核验与历史取舍，"
            "可直接作为研究基础及PPT数据来源。本轮CP-SAT的Q2时间5912.004秒、Q2节能66.124664kWh、"
            "Q3时间5770.677秒、Q3节能69.412316kWh分别为本批四种新跑方法的最低主目标观测。"
            "这不是多种子或同预算论文复现，也不是EOH收益证明；引用数字时必须携带对应场景、目标、返航时域及第25章限定。\n\n" + marker)
    master.write_text(source, encoding="utf-8")

    OUT.mkdir(parents=True, exist_ok=True)
    AUDIT.mkdir(parents=True, exist_ok=True)
    fields = list(ordered[0])
    with (OUT / "16方案完整结果.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(ordered)
    # Add exact best-discovery times to the original 64-row projection.
    fields64 = list(csv_rows[0]) + ["best_found_s"]
    with (OUT / "64检查点结果.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields64); w.writeheader()
        for row in csv_rows:
            r = indexed[(row["question"], row["objective"], row["method"])]
            cp = next(c for c in r["checkpoints"] if c["checkpoint_s"] == float(row["checkpoint_s"]))
            w.writerow(dict(row, best_found_s=cp.get("best_found_s")))
    (OUT / "结果与引用说明.md").write_text(
        "# 600秒独立基线实验结果与引用说明\n\n"
        "完整解释与四组表已写入[项目主文档第25章](../../PROJECT_DOSSIER.md#25-独立传统基线实验与申报引用)，Word同步生成。\n\n"
        "[16方案完整结果](16方案完整结果.csv)含原始精度时间、能源分项、架次、发现/结束时刻、SOC、截止和通信核验、方案hash与路径；"
        "[64检查点](64检查点结果.csv)是同16次运行的时间切片，不是额外64次独立实验。\n\n"
        "唯一批次为evidence/contest-baselines-v6/monitored_600s_r2_seed42，seed=42，单配置600秒，"
        "Q2节能返航≤6000秒，Q3≤5939.9秒，外部/公共/论文初解均未导入。论文只作历史参考；"
        "不声明多种子显著性、原问题全局最优或EOH收益。原始数据不由本文改写。\n", encoding="utf-8")
    evidence_files.update(BASE / n for n in ("results.json", "results.csv", "protocol.json", "completion.json"))
    evidence_files.add(BASE / "Q2_energy_cp_sat/cp_evidence.json")
    evidence = {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(evidence_files)}
    report = dict(passed=True, batch=BASE.relative_to(ROOT).as_posix(), final_solutions=16,
        checkpoints=64, exact_matches_to_user_tables=16, independent_validation_files=16,
        all_delivered_boxes=80, all_mass_kg=758, all_volume_L=2011,
        minimum_station_hard_slack_s=min(a["minimum_hard_slack_s"] for a in audited),
        original_experiment_records_modified=False, new_solver_runs=0,
        scope="Read-only reconciliation of archived records, sealed hashes, independent validation and supplied tables; not a new experiment or rerun.",
        results=ordered, evidence_sha256=evidence)
    (AUDIT / "result-reconciliation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(passed=True, final_solutions=16, checkpoints=64, chapter_chars=len(chapter),
        output=str(OUT), min_slack_s=report["minimum_station_hard_slack_s"]), ensure_ascii=False))


if __name__ == "__main__":
    main()
