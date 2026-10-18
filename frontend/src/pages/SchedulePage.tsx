import { useState } from 'react'
import { ArrowRight, Download, ListChecks, Search } from 'lucide-react'
import type { Plan, PlanSummary, Scenario } from '../api/client'
import { Badge, Button, Empty } from '../components/ui'
import { ResourceTimeline } from '../components/ResourceTimeline'
import { clock, number, percent, category, colorFor } from '../lib/format'
import { policyLabel } from '../lib/strategies'
import { preferenceName } from './HistoryCenter'
import { scheduleRows, scheduleCsv } from './schedule-data'
import './schedule.css'

export function SchedulePage({
  plan,
  scenario,
  plans,
  selected,
  onSelect,
  onPlan,
  onMap,
}: {
  plan: Plan | null
  scenario: Scenario
  plans: PlanSummary[]
  selected: string | null
  onSelect: (id: string) => void
  onPlan: (id: string) => void
  onMap: () => void
}) {
  const [mode, setMode] = useState<'sorties' | 'deliveries' | 'relay'>('sorties')
  const [search, setSearch] = useState('')
  const [drone, setDrone] = useState('all')
  const [group, setGroup] = useState<'time' | 'drone'>('time')
  const typeOf = (id: string) => scenario.drones.find((d) => d.drone_id === id)?.type_id || '—'
  const data = plan ? scheduleRows(plan, scenario) : null
  const match = (v: unknown) => JSON.stringify(v).toLowerCase().includes(search.toLowerCase())
  const routes = (data?.sorties || [])
    .filter((r) => (drone === 'all' || drone === r.drone_id) && match(r))
    .sort((a, b) =>
      group === 'drone'
        ? a.drone_id.localeCompare(b.drone_id) || a.prepare_start_s - b.prepare_start_s
        : a.prepare_start_s - b.prepare_start_s,
    )
  const deliveries = (data?.deliveries || []).filter(
    (r) => (drone === 'all' || drone === r.drone_id) && match(r),
  )
  const relays = (plan?.relay_sorties || []).filter(match)
  const selectedRoute = plan?.sorties.find((r) => r.sortie_id === selected) || routes[0]
  function exportTable() {
    if (!plan) return
    const table: unknown[][] =
      mode === 'sorties'
        ? [
            [
              '方案ID',
              '快照ID',
              '架次',
              '无人机',
              '机型',
              '电池',
              '访问顺序',
              '货箱列表',
              '准备开始(s)',
              '起飞(s)',
              '最后交付(s)',
              '返航(s)',
              '机体释放(s)',
              '充电开始(s)',
              '电池可复用(s)',
              '能耗(kWh)',
              '返航SOC',
            ],
            ...routes.map((r) => [
              plan.plan_id,
              plan.snapshot_id,
              r.sortie_id,
              r.drone_id,
              typeOf(r.drone_id),
              r.battery_id,
              r.visits.map((v) => v.site_id).join(' → '),
              r.cargo_ids.join(';'),
              r.prepare_start_s,
              r.takeoff_s,
              Math.max(...r.visits.map((v) => v.delivery_complete_s)),
              r.return_s,
              r.drone_released_s,
              r.charge_start_s,
              r.battery_released_s,
              r.energy_kwh,
              r.return_soc,
            ]),
          ]
        : mode === 'deliveries'
          ? [
              [
                '方案ID',
                '箱件',
                '架次',
                '站点',
                '无人机',
                '电池',
                '物资类别',
                '质量(kg)',
                '交付完成(s)',
                '期望截止(s)',
                '硬截止(s)',
                '期望延期(s)',
              ],
              ...deliveries.map((d) => [
                plan.plan_id,
                d.cargo_id,
                d.sortie_id,
                d.site_id,
                d.drone_id,
                d.battery_id,
                d.cargo_type,
                d.mass_kg,
                d.complete_s,
                d.expected_s,
                d.hard_s,
                d.delay_s,
              ]),
            ]
          : [
              [
                '方案ID',
                '中继架次',
                '无人机',
                '能源组件',
                '准备(s)',
                '起飞(s)',
                '建链(s)',
                '服务结束(s)',
                '返航(s)',
                '能耗(kWh)',
              ],
              ...relays.map((r) => [
                plan.plan_id,
                r.relay_sortie_id,
                r.drone_id,
                r.component_id,
                r.prepare_start_s,
                r.takeoff_s,
                r.service_start_s,
                r.service_end_s,
                r.return_s,
                r.energy_kwh,
              ]),
            ]
    const url = URL.createObjectURL(
      new Blob([scheduleCsv(table)], { type: 'text/csv;charset=utf-8' }),
    )
    const a = document.createElement('a')
    a.href = url
    a.download = `${plan.plan_id}-${mode}.csv`
    a.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  }
  return (
    <div className="schedule-page">
      <div className="schedule-heading">
        <div>
          <span className="eyebrow">DISPATCH MANIFEST</span>
          <h1>调度安排</h1>
          <p>按架次、机体、电池和逐箱交付查看完整排程。时间均为相对场景起点，不是实际执行记录。</p>
        </div>
        <Button onClick={exportTable} disabled={!plan}>
          <Download size={15} />
          导出当前安排 CSV
        </Button>
      </div>
      <div className="schedule-toolbar">
        <label>
          选择已计算方案
          <select
            aria-label="安排表方案"
            value={plan?.plan_id || ''}
            onChange={(e) => onPlan(e.target.value)}
          >
            <option value="" disabled>
              请选择已计算方案
            </option>
            {plans.map((p) => (
              <option key={p.plan_id} value={p.plan_id}>
                {preferenceName[p.objective]} · v{p.scenario_state_version} · {policyLabel(p)} ·{' '}
                {p.plan_id.slice(-8)}
              </option>
            ))}
          </select>
        </label>
        {plan && (
          <div>
            <Badge tone="teal">
              {plan.validation.status === 'passed' ? '独立检查通过' : '检查未通过'}
            </Badge>
            <small>
              绑定输入 v{plan.scenario_state_version} · {policyLabel(plan)}
            </small>
            <code>{plan.plan_id}</code>
          </div>
        )}
      </div>
      {!plan || !data ? (
        <Empty
          icon={<ListChecks size={28} />}
          title="先生成真实调度方案"
          description="在调度工作台计算方案后，这里会展示每个架次的资源与时间。"
          action={<Button onClick={onMap}>打开调度工作台</Button>}
        />
      ) : (
        <>
          <div className="schedule-kpis">
            <div>
              <strong>{plan.sorties.length}</strong>
              <span>运输架次</span>
            </div>
            <div>
              <strong>{new Set(plan.sorties.map((r) => r.drone_id)).size}</strong>
              <span>执行无人机</span>
            </div>
            <div>
              <strong>{new Set(plan.sorties.map((r) => r.battery_id)).size}</strong>
              <span>运输电池</span>
            </div>
            <div>
              <strong>{data.deliveries.length}</strong>
              <span>已安排箱件</span>
            </div>
            <div>
              <strong>{plan.relay_sorties?.length || 0}</strong>
              <span>中继架次</span>
            </div>
          </div>
          <section className="panel schedule-manifest">
            <div className="schedule-controls">
              <div className="schedule-tabs">
                {(
                  [
                    ['sorties', '运输架次'],
                    ['deliveries', '逐箱交付'],
                    ['relay', '中继排程'],
                  ] as const
                ).map(([id, label]) => (
                  <button
                    key={id}
                    className={mode === id ? 'active' : ''}
                    onClick={() => setMode(id)}
                  >
                    {label}
                  </button>
                ))}
              </div>
              <label className="schedule-search">
                <Search size={14} />
                <input
                  aria-label="搜索调度安排"
                  placeholder="搜索箱号、站点、机体…"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </label>
              {mode !== 'relay' && (
                <select
                  aria-label="筛选执行无人机"
                  value={drone}
                  onChange={(e) => setDrone(e.target.value)}
                >
                  <option value="all">全部无人机</option>
                  {[...new Set(plan.sorties.map((r) => r.drone_id))].sort().map((id) => (
                    <option key={id}>{id}</option>
                  ))}
                </select>
              )}
              {mode === 'sorties' && (
                <select
                  aria-label="安排表排序"
                  value={group}
                  onChange={(e) => setGroup(e.target.value as 'time' | 'drone')}
                >
                  <option value="time">按准备时间</option>
                  <option value="drone">按无人机分组</option>
                </select>
              )}
            </div>
            <p className="schedule-table-note">
              点击任一行，下方展开路线与逐站时间，并联动资源时间轴。CSV 保留原始秒数；表格显示
              时:分:秒。
            </p>
            <div className="schedule-table-wrap">
              <table
                aria-label={
                  mode === 'sorties'
                    ? '运输调度安排表'
                    : mode === 'deliveries'
                      ? '逐箱交付安排表'
                      : '中继调度安排表'
                }
              >
                <thead>
                  <tr>
                    {(mode === 'sorties'
                      ? [
                          '架次 / 机型',
                          '执行资源',
                          '路线 / 箱数',
                          '准备 → 起飞',
                          '最后交付',
                          '返航 / 机体释放',
                          '电池可复用',
                          '能耗 / SOC',
                        ]
                      : mode === 'deliveries'
                        ? [
                            '货箱 / 类别',
                            '架次 / 执行资源',
                            '服务区',
                            '交付完成',
                            '期望截止',
                            '硬截止',
                            '期望延期',
                          ]
                        : [
                            '中继架次',
                            '执行资源',
                            '准备 → 起飞',
                            '建链完成',
                            '服务结束',
                            '返航',
                            '能耗',
                          ]
                    ).map((h) => (
                      <th key={h}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {mode === 'sorties'
                    ? routes.map((r) => (
                        <tr
                          key={r.sortie_id}
                          className={selectedRoute?.sortie_id === r.sortie_id ? 'selected' : ''}
                          onClick={() => onSelect(r.sortie_id)}
                        >
                          <td>
                            <button onClick={() => onSelect(r.sortie_id)}>{r.sortie_id}</button>
                            <small>{typeOf(r.drone_id)} 型</small>
                          </td>
                          <td>
                            <strong style={{ color: colorFor(r.drone_id) }}>{r.drone_id}</strong>
                            <small>{r.battery_id}</small>
                          </td>
                          <td>
                            {scenario.base.id} → {r.visits.map((v) => v.site_id).join(' → ')} →{' '}
                            {scenario.base.id}
                            <small>{r.cargo_ids.length} 箱</small>
                          </td>
                          <td>
                            {clock(r.prepare_start_s)}
                            <small>→ {clock(r.takeoff_s)}</small>
                          </td>
                          <td>{clock(Math.max(...r.visits.map((v) => v.delivery_complete_s)))}</td>
                          <td>
                            {clock(r.return_s)}
                            <small>释放 {clock(r.drone_released_s)}</small>
                          </td>
                          <td>
                            {clock(r.battery_released_s)}
                            <small>
                              {r.charge_start_s == null
                                ? '含交接与充电'
                                : `充电起 ${clock(r.charge_start_s)}`}
                            </small>
                          </td>
                          <td>
                            {number(r.energy_kwh, 3)} kWh<small>{percent(r.return_soc)}</small>
                          </td>
                        </tr>
                      ))
                    : mode === 'deliveries'
                      ? deliveries.map((d) => (
                          <tr key={d.cargo_id} onClick={() => onSelect(d.sortie_id)}>
                            <td>
                              <button onClick={() => onSelect(d.sortie_id)}>{d.cargo_id}</button>
                              <small>{category[d.cargo_type || ''] || d.cargo_type}</small>
                            </td>
                            <td>
                              {d.sortie_id}
                              <small>
                                {d.drone_id} · {d.battery_id}
                              </small>
                            </td>
                            <td>{d.site_id}</td>
                            <td>{clock(d.complete_s)}</td>
                            <td>{d.expected_s == null ? '—' : clock(d.expected_s)}</td>
                            <td>{d.hard_s == null ? '—' : clock(d.hard_s)}</td>
                            <td className={d.delay_s && d.delay_s > 0 ? 'schedule-delay' : ''}>
                              {d.delay_s == null ? '未设置' : clock(d.delay_s)}
                            </td>
                          </tr>
                        ))
                      : relays.map((r) => (
                          <tr key={r.relay_sortie_id}>
                            <td>{r.relay_sortie_id}</td>
                            <td>
                              {r.drone_id}
                              <small>{r.component_id}</small>
                            </td>
                            <td>
                              {clock(r.prepare_start_s)}
                              <small>→ {clock(r.takeoff_s)}</small>
                            </td>
                            <td>{clock(r.service_start_s)}</td>
                            <td>{clock(r.service_end_s)}</td>
                            <td>{clock(r.return_s)}</td>
                            <td>{number(r.energy_kwh, 3)} kWh</td>
                          </tr>
                        ))}
                </tbody>
              </table>
            </div>
            {(mode === 'sorties' ? routes : mode === 'deliveries' ? deliveries : relays).length ===
              0 && (
              <p className="schedule-no-rows">
                {mode === 'relay' && !plan.relay_sorties?.length
                  ? '当前方案没有中继架次。运输方案不自动生成通信保障。'
                  : '没有匹配的安排，请调整筛选。'}
              </p>
            )}
          </section>
          {selectedRoute && (
            <section className="panel schedule-route-detail">
              <div>
                <h3>
                  {selectedRoute.sortie_id} · {selectedRoute.drone_id} / {selectedRoute.battery_id}{' '}
                  · 执行顺序
                </h3>
                <Button
                  variant="ghost"
                  onClick={() => {
                    onSelect(selectedRoute.sortie_id)
                    onMap()
                  }}
                >
                  在地图中定位
                  <ArrowRight size={14} />
                </Button>
              </div>
              <div className="schedule-stops">
                <article>
                  <strong>{scenario.base.id} · 准备</strong>
                  <small>{clock(selectedRoute.prepare_start_s)}</small>
                  <span>起飞 {clock(selectedRoute.takeoff_s)}</span>
                </article>
                {selectedRoute.visits.map((v, i) => (
                  <article key={i}>
                    <strong>
                      {i + 1}. {v.site_id}
                    </strong>
                    <small>交付完成 {clock(v.delivery_complete_s)}</small>
                    <span>{v.cargo_ids.join(' · ')}</span>
                  </article>
                ))}
                <article>
                  <strong>{scenario.base.id} · 返航</strong>
                  <small>{clock(selectedRoute.return_s)}</small>
                  <span>
                    机体释放 {clock(selectedRoute.drone_released_s)}
                    <br />
                    电池可复用 {clock(selectedRoute.battery_released_s)}
                  </span>
                </article>
              </div>
            </section>
          )}
          <ResourceTimeline
            scenario={scenario}
            plan={plan}
            selected={selectedRoute?.sortie_id || null}
            onSelect={onSelect}
          />
        </>
      )}
    </div>
  )
}
