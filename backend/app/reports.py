"""Self-contained, escaped HTML reports that print without map servers or CDNs."""

from html import escape
import math


def text(value):
    return escape(str(value), quote=True)


def clock(value):
    if value is None:
        return "—"
    total = max(0, round(value))
    return f"{total//3600:02}:{total//60%60:02}:{total%60:02}"


def route_svg(scenario, plan):
    nodes = [scenario["base"], *scenario["sites"]]
    mean = sum(n["coordinates"][1] for n in nodes) / len(nodes)
    factor = max(0.01, math.cos(math.radians(mean)))
    positions = {
        n["id"]: (n["coordinates"][0] * factor, n["coordinates"][1]) for n in nodes
    }
    coordinates = [n["coordinates"] for n in nodes]
    coordinates.extend(
        p for r in plan["sorties"] for p in r["route_geometry"]["coordinates"]
    )
    coordinates.extend(
        p
        for r in plan.get("relay_sorties", [])
        for p in r["route_geometry"]["coordinates"]
    )
    coordinates.extend(
        p
        for z in scenario.get("restricted_zones", [])
        for p in z["geometry"]["coordinates"][0]
    )
    xs, ys = zip(*[(p[0] * factor, p[1]) for p in coordinates])
    west, east, south, north = min(xs), max(xs), min(ys), max(ys)
    span_x = max(east - west, 0.001)
    span_y = max(north - south, 0.001)
    scale = min(900 / span_x, 315 / span_y)

    def xy(point):
        return 65 + (point[0] * factor - west) * scale, 375 - (point[1] - south) * scale

    colors = [
        "#0e8f85",
        "#4f78c6",
        "#d49b42",
        "#9672bd",
        "#5e9b58",
        "#cb7485",
        "#527f91",
        "#a1845c",
    ]
    parts = [
        '<svg viewBox="0 0 1200 420" role="img" aria-label="输入坐标与真实方案航线示意"><rect width="1200" height="420" rx="12" fill="#f3f7f4"/>'
    ]
    for zone in scenario.get("restricted_zones", []):
        points = " ".join(
            f"{x:.2f},{y:.2f}"
            for x, y in [xy(p) for p in zone["geometry"]["coordinates"][0]]
        )
        parts.append(
            f'<polygon points="{points}" fill="#cf6656" fill-opacity=".18" stroke="#b75a4e" stroke-dasharray="4 3"><title>{text(zone["name"])} · {zone["buffer_m"]:g}m安全缓冲</title></polygon>'
        )
    for row in plan.get("relay_sorties", []):
        points = " ".join(
            f"{x:.2f},{y:.2f}"
            for x, y in [xy(p) for p in row["route_geometry"]["coordinates"]]
        )
        x, y = xy(row["station_coordinates"])
        parts.append(
            f'<polyline points="{points}" fill="none" stroke="#8970ae" stroke-width="2" stroke-dasharray="4 3"/><circle cx="{x:.2f}" cy="{y:.2f}" r="8" fill="#8970ae"><title>{text(row["station_id"])}</title></circle><text x="{x+11:.2f}" y="{y-9:.2f}" fill="#8970ae" font-size="11">{text(row["drone_id"])}中继</text>'
        )
    for route in plan["sorties"]:
        points = " ".join(
            f"{x:.2f},{y:.2f}"
            for x, y in [xy(p) for p in route["route_geometry"]["coordinates"]]
        )
        color = colors[sum(ord(c) for c in route["drone_id"]) % len(colors)]
        parts.append(
            f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2" opacity=".65"><title>{text(route["drone_id"])} · {text(route["sortie_id"])}</title></polyline>'
        )
    for i, node in enumerate(nodes):
        x, y = xy(node["coordinates"])
        label = node["id"] + " " + node["name"]
        short = label if len(label) <= 16 else label[:15] + "…"
        parts.append(
            f'<g><title>{text(label)}</title><circle cx="{x:.2f}" cy="{y:.2f}" r="{7 if i else 10}" fill="{"#087e75" if i==0 else "#fff"}" stroke="#348267" stroke-width="2"/><text x="{x+12:.2f}" y="{y+4:.2f}" font-size="12" fill="#294f42">{text(short)}</text></g>'
        )
    parts.append(
        '<text x="18" y="25" fill="#557364" font-size="12">WGS84坐标示意 · 任务级运输路线 · 非实时障碍图</text></svg>'
    )
    if scenario.get("restricted_zones"):
        parts.insert(
            -1,
            '<text x="18" y="405" fill="#a4584a" font-size="11">红色为限制区原始边界；航路计算另含设定缓冲及数值余量。</text>',
        )
    return "".join(parts)


def build_report(snapshot, plan, analysis):
    s = snapshot["scenario"]
    m = plan["metrics"]
    cargos = {c["cargo_id"]: c for c in s["cargo_items"]}
    site_names = {n["id"]: n["name"] for n in s["sites"]}
    delivery = {
        cid: (visit["site_id"], visit["delivery_complete_s"], r)
        for r in plan["sorties"]
        for visit in r["visits"]
        for cid in visit["cargo_ids"]
    }
    tasks = []
    for r in sorted(
        plan["sorties"], key=lambda row: (row["prepare_start_s"], row["drone_id"])
    ):
        stops = "<br>".join(
            f'{text(v["site_id"])} {text(site_names[v["site_id"]])} · T+{clock(v["delivery_complete_s"])}'
            for v in r["visits"]
        )
        tasks.append(
            f'<tr><td>{text(r["drone_id"])}<small>{text(r["battery_id"])}</small></td><td>{text(r["sortie_id"])}</td><td>{stops}</td><td>T+{clock(r["prepare_start_s"])}<small>起飞 T+{clock(r["takeoff_s"])}<br>返航 T+{clock(r["return_s"])}</small></td><td>{len(r["cargo_ids"])}箱<small>{text(", ".join(r["cargo_ids"]))}</small></td><td>{r["energy_kwh"]:.3f} kWh<small>SOC {r["return_soc"]:.1%}</small></td></tr>'
        )
    box_rows = []
    for cid, (site, when, r) in sorted(delivery.items()):
        c = cargos[cid]
        box_rows.append(
            f'<tr><td>{text(cid)}</td><td>{text(c["demand_id"])}</td><td>{text(site)}</td><td>{c["mass_kg"]:g} kg / {c["volume_l"]:g} L</td><td>{text(r["drone_id"])} / {text(r["battery_id"])}</td><td>T+{clock(when)}</td></tr>'
        )
    labels = {
        "drone": "运输机体",
        "battery": "运输电池",
        "relay_drone": "中继机体",
        "relay_energy": "中继能源组件",
    }
    resource_rows = "".join(
        f'<tr><td>{labels[r["kind"]]}</td><td>{text(r["resource_id"])} · {text(r["type_id"])}型</td><td>{r["sortie_count"]}</td><td>{clock(r["occupied_s"])}</td><td>{r["utilization"]:.1%}</td><td>{r["energy_kwh"]:.3f} kWh</td></tr>'
        for r in analysis["resources"]
    )
    demand_rows = "".join(
        f'<tr><td>{text(d["demand_id"])}</td><td>{text(d["site_id"])}</td><td>{d["served_quantity"]}/{d["required_quantity"]}</td><td>{clock(d["complete_s"])}</td><td>{clock(d["expected_deadline_s"])}</td><td>{clock(d["hard_deadline_s"])}</td><td>{clock(d["delay_s"])}</td></tr>'
        for d in analysis["delivery"]["demands"]
    )
    checks = "".join(
        f'<li><b>{text(c["code"])}</b> · {text({"passed":"通过","failed":"失败","not_evaluated":"未评估"}.get(c["status"],c["status"]))}：{text(c["message"])}</li>'
        for c in plan["validation"]["checks"]
    )
    notes = "".join(
        f"<li>{text(note)}</li>" for note in [*plan["solver_notes"], *analysis["notes"]]
    )
    limits = s.get("resource_limits")
    ground_caption = (
        f"准备工位{limits['prep_slots']}个、充电端口{limits['charging_ports']}个；初始/返航充电峰值{analysis['charge_peak']}，电池等待时长合计{clock(analysis['charge_wait_s'])}"
        if limits
        else f"无限充电端口模型下的并发补能峰值 {analysis['charge_peak']} 块"
    )
    initial_rows = "".join(
        f'<tr><td>{text(row["battery_id"])}</td><td>{clock(next(b["available_after_s"] for b in s["batteries"] if b["battery_id"]==row["battery_id"]))}</td><td>{clock(row["start_s"])}</td><td>{clock(row["end_s"])}</td><td>{row["from_soc"]:.1%} → {row["to_soc"]:.1%}</td></tr>'
        for row in plan.get("initial_charges", [])
    )
    initial_html = (
        (
            '<h3>初始补能与排队</h3><p class="muted">先补满策略；等待占用电池，实际充电占用端口。飞行能耗不含未知电网损耗。</p><table><thead><tr><th>电池</th><th>可用 / 等待开始</th><th>充电开始</th><th>补满释放</th><th>SOC</th></tr></thead><tbody>'
            + initial_rows
            + "</tbody></table>"
        )
        if initial_rows
        else ""
    )
    joint_html = ""
    if plan.get("joint_metrics"):
        joint, comm = plan["joint_metrics"], plan["communication_report"]
        rows = "".join(
            f'<tr><td>{text(r["drone_id"])}<small>{text(r["component_id"])}<br>{text(r["relay_sortie_id"])}</small></td><td>{text(r["station_id"])}<small>离地{r["station_agl_m"]:g}m / 海拔{r["station_elevation_m"]:.1f}m</small></td><td>{clock(r["prepare_start_s"])}<small>起飞{clock(r["takeoff_s"])}<br>到达{clock(r["arrival_s"])}</small></td><td>{clock(r["service_start_s"])} → {clock(r["service_end_s"])}</td><td>{clock(r["return_s"])}<small>机体释放{clock(r["drone_released_s"])}</small></td><td>{r["energy_kwh"]:.3f}kWh<small>SOC{r["return_soc"]:.1%}<br>补能{clock(r["charge_start_s"])}–{clock(r["component_released_s"])}</small></td></tr>'
            for r in plan.get("relay_sorties", [])
        )
        joint_html = f'<h2>通信与中继保障</h2><p>联合全部返航 {clock(joint["joint_makespan_s"])}，联合总能耗 {joint["joint_energy_kwh"]:.3f}kWh（中继 {joint["relay_energy_kwh"]:.3f}kWh）；中继{joint["relay_sortie_count"]}架次。</p><p class="muted">累计运输活动 {clock(comm["transport_active_s"])}；直连 {clock(comm["direct_s"])}，中继 {clock(comm["relay_s"])}，缺口 {comm["coverage_gap_s"]:g}秒。时长累加并行运输任务；有限投影DEM模型检查，不是现场无线电认证。</p><table><thead><tr><th>中继机 / 能源组件</th><th>悬停点</th><th>准备 / 飞抵</th><th>建链 → 服务结束</th><th>返航 / 周转</th><th>能量 / 补能</th></tr></thead><tbody>{rows}</tbody></table>'
    energy_label = "运输能耗" if plan.get("joint_metrics") else "预计总能耗"
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>援航调度报告 · {text(s['name'])}</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#f0f4f2;color:#26453a;font:13px/1.7 "Microsoft YaHei","PingFang SC",sans-serif}}main{{max-width:1200px;margin:24px auto;background:#fff;padding:32px 36px;box-shadow:0 2px 20px #284e3410}}header{{display:flex;justify-content:space-between;border-bottom:2px solid #0b8273;padding-bottom:20px}}h1{{font-size:25px;margin:0 0 5px}}h2{{font-size:18px;margin:27px 0 12px}}p{{margin:5px 0}}.muted,small{{color:#668071}}small{{display:block;font-size:10px;overflow-wrap:anywhere;line-height:1.7;margin-top:5px}}.identity{{font-size:11px;line-height:1.9}}.identity span{{display:inline-block;margin-right:18px;overflow-wrap:anywhere}}.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:20px 0}}.metrics>div{{background:#f3f8f4;border:1px solid #e3ede5;border-radius:7px;padding:12px}}.metrics strong{{display:block;font-size:22px;color:#156752;margin-top:5px}}.notice{{padding:12px 16px;background:#fff8e9;border-left:3px solid #c99c48;margin:17px 0;color:#796340;font-size:12px}}svg{{width:100%;height:auto;display:block}}table{{width:100%;border-collapse:collapse;font-size:11px;table-layout:auto}}th{{background:#edf4ee;text-align:left;color:#426a50}}td,th{{border-bottom:1px solid #e0e8e1;padding:9px 8px;vertical-align:top;overflow-wrap:anywhere}}td:nth-child(2){{max-width:205px}}thead{{display:table-header-group}}tr{{break-inside:avoid}} .validation-section{{break-inside:avoid}}.model-notes{{columns:2;column-gap:24px}}.model-notes li{{break-inside:avoid}}ul{{padding-left:20px;font-size:12px;line-height:1.8}}li{{margin:6px 0}}button{{background:#087e75;border:0;border-radius:6px;color:#fff;padding:10px 16px;font:inherit;cursor:pointer}}footer{{border-top:1px solid #dce7df;margin-top:28px;padding-top:15px;font-size:11px;color:#6b8172}}.check-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:5px;list-style:none;padding:0}}.check-grid li{{margin:0;padding:5px 7px;background:#f3f7f4;border:1px solid #e2e9e3;border-radius:4px;font-size:10px;break-inside:avoid}}@page{{size:A4 landscape;margin:12mm;@bottom-left{{content:"{text(plan['plan_id'])}";font-size:8pt;color:#718777}}@bottom-right{{content:counter(page) " / " counter(pages);font-size:8pt;color:#718777}}}}@media print{{body{{background:#fff;font-size:10pt}}main{{max-width:none;margin:0;padding:0;box-shadow:none}}button{{display:none}}h2,h3{{break-after:avoid}}h2+p,h3+p{{break-after:avoid}}.metrics{{break-inside:avoid}}svg{{max-height:84mm}}table{{font-size:8pt}}td,th{{padding:5px 6px}}small{{font-size:7pt}}header{{padding-bottom:8px}}h1{{font-size:20px;line-height:1.4}}header p{{margin:2px 0;font-size:11px}}.identity{{font-size:9px;line-height:1.5}}.metrics{{margin:12px 0;gap:8px}}.metrics>div{{padding:8px;font-size:11px}}.metrics strong{{font-size:20px;line-height:1.4}}.notice{{break-inside:avoid;margin:12px 0;padding:8px 10px;font-size:10px;line-height:1.5}}h2{{font-size:16px;margin:16px 0 8px;line-height:1.4}}svg{{max-height:72mm}}ul{{font-size:10px;line-height:1.55;margin-top:8px;margin-bottom:8px}}li{{margin:3px 0}}footer{{display:none}}}}
</style></head><body><main><header><div><h1>援航 · 运输调度与资源报告</h1><p>{text(s['name'])}</p><p class="muted">本地模拟 / 规划辅助 · 在声明模型范围内可行</p></div><button onclick="window.print()">打印 / 保存PDF</button></header><div class="identity"><span>方案 {text(plan['plan_id'])}</span><span>快照 {text(snapshot['snapshot_id'])} · v{snapshot['scenario_state_version']}</span><br><span>场景起点 {text(s['start_time'])}（{text(s['timezone'])}）</span><span>生成 {text(plan['generated_at'])}</span><br><span>输入Hash {text(snapshot['content_hash'])}</span></div><div class="metrics"><div>已安排箱件<strong>{len(delivery)} / {sum(d['required_quantity'] for d in s['demands'])}</strong></div><div>最后交付 / 全部返航<strong>{clock(m['last_delivery_s'])}</strong><small>返航 {clock(m['makespan_s'])}</small></div><div>{energy_label}<strong>{m['energy_kwh']:.3f} kWh</strong></div><div>最低返航SOC<strong>{m['min_return_soc']:.1%}</strong><small>策略下限 {s['policy']['min_return_soc']:.1%}</small></div></div><div class="notice">这是计划任务单，不是实时执行事实或飞控指令。表内时间为相对场景起点的时分秒，按最近秒显示；JSON保留原精度。费用未配置，不计算人民币。验证范围：{text(', '.join(plan['model_scope']))}。</div><h2>一、运输航线与站点</h2>{route_svg(s,plan)}<h2>二、架次任务单</h2><table><thead><tr><th>机体 / 电池</th><th>稳定架次ID</th><th>访问点 / 交接完成</th><th>准备 / 起飞 / 返航</th><th>箱件追踪</th><th>能耗 / 返航SOC</th></tr></thead><tbody>{''.join(tasks)}</tbody></table><h2>三、需求交付与时间要求</h2><p class="muted">硬截止违约 {analysis['delivery']['hard_violation_count']} 条；期望延期 {analysis['delivery']['late_demand_count']} 条。期望时限和硬约束分开统计。</p><table><thead><tr><th>需求</th><th>站点</th><th>已安排 / 需求</th><th>交接完成</th><th>期望时限</th><th>硬截止</th><th>期望延期</th></tr></thead><tbody>{demand_rows}</tbody></table><h2>四、资源占用</h2><p class="muted">{text(ground_caption)}；最小硬截止余量 {clock(analysis['min_hard_slack_s'])}。这不是最少购买数量证明。</p><table><thead><tr><th>资源类型</th><th>实体 / 机型</th><th>架次</th><th>计划占用时长</th><th>计划占用率</th><th>累计能耗</th></tr></thead><tbody>{resource_rows}</tbody></table>{initial_html}{joint_html}<h2>五、逐箱物资追踪</h2><table><thead><tr><th>箱件</th><th>对应需求</th><th>站点</th><th>质量 / 体积</th><th>机体 / 电池</th><th>交接完成</th></tr></thead><tbody>{''.join(box_rows)}</tbody></table><section class="validation-section"><h2>六、独立检查与模型边界</h2><ul class="check-grid">{checks}</ul><ul class="model-notes">{notes}</ul></section><footer>所有数值与实体来自本方案绑定的不可变快照。源数据与计划可通过系统导出JSON核对。当前版本用于比赛演练与规划辅助。</footer></main></body></html>"""
