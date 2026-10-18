import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  ArrowLeft,
  ArrowUpRight,
  BatteryCharging,
  CheckCircle2,
  Download,
  Drone,
  FileSpreadsheet,
  Info,
  Link2,
  Package,
  RadioTower,
  Search,
} from 'lucide-react'
import type { Plan, Scenario } from '../api/client'
import { Button, Empty, Modal } from '../components/ui'
import { StageCharts } from './StageCharts'
import { ResourceTimeline } from '../components/ResourceTimeline'
import { category, clock, number, percent } from '../lib/format'
import { scheduleCsv, scheduleRows } from '../pages/schedule-data'
import { ops } from '../api/operations'

type Mode = 'transport' | 'cargo' | 'relay' | 'communication' | 'resources'
type Column = { name: string; kind?: 'time' | 'energy' | 'soc' | 'number' }
type Row = {
  id: string
  sortie?: string
  drone?: string
  values: (string | number | null | undefined)[]
}
const kinds = [
  { id: 'transport', title: '运输架次', icon: Drone },
  { id: 'cargo', title: '逐箱交付', icon: Package },
  { id: 'relay', title: '中继排程', icon: RadioTower },
  { id: 'communication', title: '通信保障', icon: Link2 },
  { id: 'resources', title: '资源占用', icon: BatteryCharging },
] as const
const phaseNames: Record<string, string> = {
  climb: '爬升',
  cruise: '巡航',
  descent: '下降',
  handover: '物资交接',
  flight: '飞行',
  prepare: '装载准备',
  relay_service: '通信保障',
}

export function ResultsWorkspace({
  scenario,
  plan,
  selected,
  onSelect,
  onMap,
}: {
  scenario: Scenario
  plan?: Plan
  selected: string | null
  onSelect: (id: string) => void
  onMap: () => void
}) {
  const [mode, setMode] = useState<Mode>('transport')
  const [search, setSearch] = useState('')
  const [drone, setDrone] = useState('all')
  const [timeline, setTimeline] = useState(false)
  const [detail, setDetail] = useState<string | null>(null)
  const focused = plan?.sorties.find((r) => r.sortie_id === detail)
  const focus = (id: string) => {
    onSelect(id)
    setDetail(id)
  }
  const stages = useQuery({
    queryKey: ['stages', plan?.plan_id],
    queryFn: () => ops.stages(plan!.plan_id),
    enabled: !!plan?.communication_report?.windows.length,
  })
  const data = useMemo(() => {
    if (!plan) return null
    const schedule = scheduleRows(plan, scenario)
    const names = new Map([scenario.base, ...scenario.sites].map((s) => [s.id, s.name]))
    const site = (id: string) => `${names.get(id) || id}（${id}）`
    const transport: Row[] = schedule.sorties.map((r, i) => ({
      id: r.sortie_id,
      sortie: r.sortie_id,
      drone: r.drone_id,
      values: [
        `第${i + 1}架次`,
        r.drone_id,
        r.battery_id,
        r.visits.map((v) => site(v.site_id)).join(' → '),
        r.cargo_ids.length,
        r.prepare_start_s,
        r.takeoff_s,
        Math.max(...r.visits.map((v) => v.delivery_complete_s)),
        r.return_s,
        r.energy_kwh,
        r.return_soc,
      ],
    }))
    const cargo: Row[] = schedule.deliveries.map((r) => ({
      id: r.cargo_id,
      sortie: r.sortie_id,
      drone: r.drone_id,
      values: [
        r.cargo_id,
        category[r.cargo_type || ''] || r.cargo_type,
        site(r.site_id),
        r.drone_id,
        r.battery_id,
        r.complete_s,
        r.expected_s,
        r.hard_s,
        r.delay_s,
      ],
    }))
    const relay: Row[] = (plan.relay_sorties || []).map((r, i) => ({
      id: r.relay_sortie_id,
      drone: r.drone_id,
      values: [
        `第${i + 1}中继架次`,
        r.drone_id,
        r.component_id,
        r.station_id,
        r.station_agl_m,
        r.prepare_start_s,
        r.service_start_s,
        r.service_end_s,
        r.return_s,
        r.energy_kwh,
        r.return_soc,
      ],
    }))
    const communication: Row[] = (plan.communication_report?.windows || []).map((w, i) => ({
      id: `window-${i}`,
      sortie: w.sortie_id,
      drone: plan.sorties.find((r) => r.sortie_id === w.sortie_id)?.drone_id,
      values: [
        plan.sorties.find((r) => r.sortie_id === w.sortie_id)?.drone_id,
        [
          ...new Set(
            stages.data?.trajectory_segments
              .filter(
                (s) => s.sortie_id === w.sortie_id && s.start_s < w.end_s && s.end_s > w.start_s,
              )
              .map((s) => phaseNames[s.phase] || s.phase),
          ),
        ].join(' / ') || '飞行与交接',
        w.start_s,
        w.end_s,
        w.end_s - w.start_s,
        w.source === 'gateway' ? '直接连接地面网关' : '通信无人机转发',
        w.relay_sortie_id || '不需要中继',
      ],
    }))
    const resources: Row[] = []
    for (const r of schedule.sorties) {
      resources.push(
        {
          id: r.sortie_id + '-air',
          sortie: r.sortie_id,
          drone: r.drone_id,
          values: [
            '运输无人机',
            r.drone_id,
            r.prepare_start_s,
            r.return_s,
            r.drone_released_s,
            '返航并完成周转后可再次出发',
          ],
        },
        {
          id: r.sortie_id + '-battery',
          sortie: r.sortie_id,
          drone: r.drone_id,
          values: [
            '运输电池',
            r.battery_id,
            r.prepare_start_s,
            r.return_s,
            r.battery_released_s,
            '包含任务占用及返航后的充电时间',
          ],
        },
      )
    }
    for (const r of plan.relay_sorties || []) {
      resources.push(
        {
          id: r.relay_sortie_id + '-air',
          drone: r.drone_id,
          values: [
            '通信无人机',
            r.drone_id,
            r.prepare_start_s,
            r.return_s,
            r.drone_released_s,
            '中继服务结束、返航并周转',
          ],
        },
        {
          id: r.relay_sortie_id + '-energy',
          drone: r.drone_id,
          values: [
            '中继能源组件',
            r.component_id,
            r.prepare_start_s,
            r.return_s,
            r.component_released_s,
            '含返航后的补能；与机体分别释放',
          ],
        },
      )
    }
    return { transport, cargo, relay, communication, resources }
  }, [plan, scenario, stages.data])
  const columns: Record<Mode, Column[]> = {
    transport: [
      { name: '运输架次' },
      { name: '无人机' },
      { name: '电池' },
      { name: '访问救援点顺序' },
      { name: '箱数', kind: 'number' },
      { name: '准备开始', kind: 'time' },
      { name: '起飞', kind: 'time' },
      { name: '最后交付', kind: 'time' },
      { name: '返航', kind: 'time' },
      { name: '能耗', kind: 'energy' },
      { name: '返航电量', kind: 'soc' },
    ],
    cargo: [
      { name: '货箱编号' },
      { name: '物资类别' },
      { name: '救援点' },
      { name: '无人机' },
      { name: '电池' },
      { name: '交付完成', kind: 'time' },
      { name: '期望送达', kind: 'time' },
      { name: '强制截止', kind: 'time' },
      { name: '超过期望', kind: 'time' },
    ],
    relay: [
      { name: '中继架次' },
      { name: '通信无人机' },
      { name: '能源组件' },
      { name: '悬停点' },
      { name: '离地高度 / m', kind: 'number' },
      { name: '准备开始', kind: 'time' },
      { name: '建链完成', kind: 'time' },
      { name: '服务结束', kind: 'time' },
      { name: '返航', kind: 'time' },
      { name: '能耗', kind: 'energy' },
      { name: '返航电量', kind: 'soc' },
    ],
    communication: [
      { name: '运输无人机' },
      { name: '飞行阶段' },
      { name: '开始', kind: 'time' },
      { name: '结束', kind: 'time' },
      { name: '持续时长', kind: 'time' },
      { name: '通信方式' },
      { name: '中继来源' },
    ],
    resources: [
      { name: '资源类型' },
      { name: '设备 / 电池编号' },
      { name: '占用开始', kind: 'time' },
      { name: '返航', kind: 'time' },
      { name: '再次可用', kind: 'time' },
      { name: '说明' },
    ],
  }
  const rows = (data?.[mode] || []).filter(
    (r) =>
      (drone === 'all' || r.drone === drone) &&
      r.values.join(' ').toLowerCase().includes(search.toLowerCase()),
  )
  function exportCsv() {
    if (!plan) return
    const heads = columns[mode].map(
      (c) =>
        c.name +
        (c.kind === 'time'
          ? '（秒）'
          : c.kind === 'energy'
            ? '（kWh）'
            : c.kind === 'soc'
              ? '（比例0—1）'
              : ''),
    )
    const blob = new Blob(
      [
        scheduleCsv([
          ['方案编号', '输入快照', ...heads],
          ...rows.map((r) => [plan.plan_id, plan.snapshot_id, ...r.values]),
        ]),
      ],
      { type: 'text/csv;charset=utf-8' },
    )
    const url = URL.createObjectURL(blob),
      a = document.createElement('a')
    a.href = url
    a.download = `yuanhang-${mode}.csv`
    a.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  }
  if (!plan || !data)
    return (
      <div className="v3-results">
        <Empty
          icon={<FileSpreadsheet size={28} />}
          title="调度安排将在计算后生成"
          description="先生成一份通过独立检查的真实方案，再查看谁在何时运输哪些物资。"
          action={<Button onClick={onMap}>返回方案地图</Button>}
        />
      </div>
    )
  const metrics = plan.joint_metrics
  return (
    <main className="v3-results">
      <div className="v3-results-heading">
        <div>
          <span className="v3-kicker">
            <FileSpreadsheet size={15} /> 可以直接照着核对的任务清单
          </span>
          <h2>调度安排与逐箱交付</h2>
          <p>先看运输顺序，再核对货箱、电池与通信保障。所有表格对应当前所选方案。</p>
        </div>
        <div className="v3-result-actions">
          <Button onClick={onMap}>
            <ArrowLeft size={15} />
            返回地图
          </Button>
          <a
            className="button button-primary"
            href={`/api/v1/plans/${encodeURIComponent(plan.plan_id)}/export?format=xlsx`}
          >
            <Download size={16} />
            导出调度工作簿
          </a>
        </div>
      </div>
      <div className="v3-result-stats">
        {[
          [Drone, '运输架次', String(plan.sorties.length), '按准备时间排序'],
          [Package, '计划交付', `${data.cargo.length} 箱`, '每只货箱可追溯'],
          [
            RadioTower,
            '中继架次',
            String(data.relay.length),
            data.relay.length ? '运输与通信协同' : '此方案为基础运输',
          ],
          [
            BatteryCharging,
            '计划总能耗',
            `${number(metrics?.joint_energy_kwh ?? plan.metrics.energy_kwh, 2)} kWh`,
            metrics ? '含运输和中继' : '运输能耗',
          ],
        ].map(([Icon, title, value, detail]) => {
          const I = Icon as typeof Drone
          return (
            <article key={String(title)}>
              <I size={20} />
              <span>{String(title)}</span>
              <strong>{String(value)}</strong>
              <small>{String(detail)}</small>
            </article>
          )
        })}
      </div>
      <section className="v3-manifest">
        <div className="v3-result-tabs" role="tablist" aria-label="调度结果表格">
          {kinds.map((k) => (
            <button
              role="tab"
              aria-selected={mode === k.id}
              key={k.id}
              onClick={() => {
                setMode(k.id)
                setDrone('all')
              }}
              className={mode === k.id ? 'active' : ''}
            >
              <k.icon size={16} />
              {k.title}
              <b>{data[k.id].length}</b>
            </button>
          ))}
        </div>
        <div className="v3-manifest-tools">
          <label>
            <Search size={16} />
            <input
              aria-label="搜索任务调度安排"
              placeholder="搜索救援点、货箱、无人机…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </label>
          <select
            aria-label="按执行无人机筛选"
            value={drone}
            onChange={(e) => setDrone(e.target.value)}
          >
            <option value="all">全部无人机</option>
            {[...new Set(data[mode].map((r) => r.drone).filter((s): s is string => !!s))].map(
              (id) => (
                <option key={id}>{id}</option>
              ),
            )}
          </select>
          <span>{rows.length} 条安排</span>
          <Button onClick={exportCsv}>
            <Download size={14} />
            导出当前表
          </Button>
        </div>
        <div className="v3-manifest-scroll">
          <table
            className="v3-manifest-table"
            aria-label={`${kinds.find((k) => k.id === mode)?.title}安排表`}
          >
            <thead>
              <tr>
                <th>序号</th>
                {columns[mode].map((c) => (
                  <th key={c.name}>
                    {c.name}
                    {c.kind === 'time' && <small>时:分:秒</small>}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr
                  key={r.id}
                  className={selected === r.sortie ? 'selected' : ''}
                  onClick={() => r.sortie && focus(r.sortie)}
                >
                  <td className="v3-row-index">{String(i + 1).padStart(2, '0')}</td>
                  {r.values.map((v, j) => (
                    <td key={j}>
                      {j === 0 && r.sortie ? (
                        <button
                          onClick={(event) => {
                            event.stopPropagation()
                            focus(r.sortie!)
                          }}
                        >
                          {v ?? '—'}
                          <ArrowUpRight size={12} />
                        </button>
                      ) : v == null ? (
                        '—'
                      ) : columns[mode][j].kind === 'time' ? (
                        clock(Number(v))
                      ) : columns[mode][j].kind === 'energy' ? (
                        `${number(Number(v), 3)} kWh`
                      ) : columns[mode][j].kind === 'soc' ? (
                        percent(Number(v))
                      ) : typeof v === 'number' ? (
                        number(v, 2)
                      ) : (
                        v
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          {!rows.length && (
            <div className="v3-table-empty">
              <Info size={22} />
              <b>
                {mode === 'relay' || mode === 'communication'
                  ? '当前方案没有通信中继记录'
                  : '没有符合筛选条件的安排'}
              </b>
              <p>
                {mode === 'relay' || mode === 'communication'
                  ? '选择运输＋通信协同演练并重新计算，即可得到真实中继与保障时段。'
                  : '请调整搜索词或无人机筛选。'}
              </p>
            </div>
          )}
        </div>
        <div className="v3-table-footer">
          <span>
            <CheckCircle2 size={14} />
            {plan.validation.status === 'passed' ? '保存时独立检查通过' : '方案待检查'} · 输入第
            {plan.scenario_state_version}版
          </span>
          <span>计划安排；实际交付请到执行跟踪查看</span>
        </div>
      </section>
      <div className="v3-results-notes">
        <Info size={16} />
        <p>
          “准备开始”包含装载，“返航”表示回到调度中心；机体与电池的再次可用时刻可能不同。表中时间从任务启动起算，导出文件保留原始秒数。
          <a href="#/help/terms">查看术语说明</a>
        </p>
      </div>
      <button className="v3-inline-link" onClick={() => setTimeline(!timeline)}>
        <BatteryCharging size={16} />
        {timeline ? '收起资源时间轴' : '展开无人机与电池时间轴'}
        <ArrowUpRight size={14} />
      </button>
      {timeline && (
        <ResourceTimeline scenario={scenario} plan={plan} selected={selected} onSelect={onSelect} />
      )}
      <details className="v3-source-details">
        <summary>查看方案来源与原始编号</summary>
        <dl>
          <dt>方案</dt>
          <dd>{plan.plan_id}</dd>
          <dt>输入快照</dt>
          <dd>{plan.snapshot_id}</dd>
          <dt>约束范围</dt>
          <dd>{plan.model_scope.join(' / ')}</dd>
        </dl>
      </details>
      <Modal
        title="运输架次安排"
        description="来自当前方案的实际箱件、访问次序与阶段计算。"
        open={!!focused}
        onOpenChange={(open) => {
          if (!open) setDetail(null)
        }}
        wide
      >
        {focused && (
          <div className="v3-sortie-detail">
            <div className="v3-sortie-detail-summary">
              <span>
                <Drone size={18} />
                <b>{focused.drone_id}</b>
                <small>运输无人机</small>
              </span>
              <span>
                <BatteryCharging size={18} />
                <b>{focused.battery_id}</b>
                <small>运输电池</small>
              </span>
              <span>
                <Package size={18} />
                <b>{focused.cargo_ids.length} 箱</b>
                <small>本架次装载</small>
              </span>
              <span>
                <CheckCircle2 size={18} />
                <b>{percent(focused.return_soc)}</b>
                <small>计划返航电量</small>
              </span>
            </div>
            <div className="v3-sortie-detail-route">
              <span>调度中心 · {scenario.base.name}</span>
              {focused.visits.map((v, i) => (
                <div key={`${v.site_id}-${i}`}>
                  <i>{i + 1}</i>
                  <span>
                    <b>{scenario.sites.find((s) => s.id === v.site_id)?.name || v.site_id}</b>
                    <small>
                      预计交付 {clock(v.delivery_complete_s)} · {v.cargo_ids.length} 箱
                    </small>
                    <p>{v.cargo_ids.join(' · ')}</p>
                  </span>
                </div>
              ))}
              <span>返航调度中心 · {clock(focused.return_s)}</span>
            </div>
            <StageCharts plan={plan} selected={focused.sortie_id} />
            <div className="v2-form-actions">
              <Button onClick={() => setDetail(null)}>关闭</Button>
              <Button
                variant="primary"
                onClick={() => {
                  setDetail(null)
                  onMap()
                }}
              >
                在地图核对
                <ArrowUpRight size={14} />
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </main>
  )
}
