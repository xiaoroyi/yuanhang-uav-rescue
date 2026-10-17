import { useEffect, useMemo, useRef, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  BarChart3,
  BatteryCharging,
  CheckCircle2,
  ChevronRight,
  Clock3,
  Download,
  FlaskConical,
  LoaderCircle,
  PackagePlus,
  Plane,
  RadioTower,
  ShieldCheck,
  TriangleAlert,
  X,
} from 'lucide-react'
import { init, use as registerCharts } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import {
  api,
  downloadJson,
  type Plan,
  type PlanAnalysis,
  type Scenario,
  type WhatIfReceipt,
} from '../api/client'
import { Badge, Button, Empty } from '../components/ui'
import { colorFor, duration, number, percent, statusLabel } from '../lib/format'
import './resource-analysis.css'
import { ScenarioExperiments } from './ScenarioExperiments'

registerCharts([BarChart, GridComponent, TooltipComponent, CanvasRenderer])

type Props = {
  scenario: Scenario
  plan: Plan | null
  stale: boolean
  onOpen: (scene: Scenario) => void
  notify: (message: string, error?: boolean) => void
}

function UtilizationChart({ data }: { data: PlanAnalysis['resources'] }) {
  const container = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (!container.current) return
    const chart = init(container.current)
    chart.setOption({
      animationDuration: 350,
      grid: { left: 75, right: 45, top: 15, bottom: 32 },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        valueFormatter: (value: unknown) => percent(Number(value) / 100),
      },
      xAxis: {
        type: 'value',
        max: 100,
        axisLabel: { color: '#6b7f80', fontSize: 11, formatter: '{value}%' },
        splitLine: { lineStyle: { color: '#edf1f0', type: 'dashed' } },
      },
      yAxis: {
        type: 'category',
        data: data.map((r) => r.resource_id),
        inverse: true,
        axisTick: { show: false },
        axisLine: { show: false },
        axisLabel: { color: '#425f5a', fontSize: 12 },
      },
      series: [
        {
          name: '计划占用率',
          type: 'bar',
          barMaxWidth: 15,
          data: data.map((r) => ({
            value: Number((r.utilization * 100).toFixed(2)),
            itemStyle: { color: colorFor(r.resource_id), borderRadius: [0, 4, 4, 0] },
          })),
          label: {
            show: true,
            position: 'right',
            color: '#536e67',
            fontSize: 11,
            formatter: '{c}%',
          },
        },
      ],
    })
    const observer = new ResizeObserver(() => chart.resize())
    observer.observe(container.current)
    return () => {
      observer.disconnect()
      chart.dispose()
    }
  }, [data])
  return (
    <div
      ref={container}
      className="utilization-chart"
      style={{ height: Math.max(210, data.length * 34 + 45) }}
      role="img"
      aria-label="按真实方案统计的资源计划占用率，完整数值见下方表格"
    />
  )
}

export function ResourceAnalysis({ scenario, plan, stale, onOpen, notify }: Props) {
  const query = useQueryClient()
  const [kind, setKind] = useState<PlanAnalysis['resources'][number]['kind']>('drone'),
    [filter, setFilter] = useState<'all' | 'late' | 'hard'>('all')
  const [type, setType] = useState(
    () =>
      scenario.drone_types.find((t) => t.type_id === 'C')?.type_id ||
      scenario.drone_types[0]?.type_id ||
      '',
  )
  const [extraDrones, setExtraDrones] = useState(1),
    [extraBatteries, setExtraBatteries] = useState(1),
    [energy, setEnergy] = useState(1),
    [flightTime, setFlightTime] = useState(1),
    [soh, setSoh] = useState(1),
    [reserve, setReserve] = useState(scenario.policy.min_return_soc),
    [deadlineScale, setDeadlineScale] = useState(1)
  const [receipt, setReceipt] = useState<WhatIfReceipt | null>(null),
    [jobId, setJobId] = useState(''),
    [submitting, setSubmitting] = useState(false)
  const [historyBusy, setHistoryBusy] = useState(false)
  const analysis = useQuery({
    queryKey: ['analysis', plan?.plan_id],
    queryFn: () => api.analysis(plan!.plan_id),
    enabled: !!plan,
  })
  const job = useQuery({
    queryKey: ['job', jobId],
    queryFn: () => api.job(jobId),
    enabled: !!jobId,
    refetchInterval: (q) =>
      q.state.data && ['completed', 'failed', 'canceled'].includes(q.state.data.job_state)
        ? false
        : 500,
  })
  const result = useQuery({
    queryKey: ['plan', job.data?.plan_id],
    queryFn: () => api.plan(job.data!.plan_id!),
    enabled: !!job.data?.plan_id,
  })
  const baseline = useQuery({
    queryKey: ['plan', receipt?.origin.source_plan_id],
    queryFn: () => api.plan(receipt!.origin.source_plan_id!),
    enabled: !!receipt?.origin.source_plan_id,
  })
  const diagnostic = useQuery({
    queryKey: ['diagnostics', jobId],
    queryFn: () => api.diagnostics(jobId),
    enabled: !!jobId && job.data?.job_state === 'completed' && !job.data.plan_id,
  })
  const rows = useMemo(
    () =>
      analysis.data?.resources.filter(
        (r) =>
          r.kind === (plan?.communication_report || !kind.startsWith('relay') ? kind : 'drone'),
      ) || [],
    [analysis.data, kind, plan?.communication_report],
  )
  const running =
    submitting || historyBusy || !!(job.data && ['queued', 'running'].includes(job.data.job_state))
  const parametersValid =
    Number.isInteger(extraDrones) &&
    extraDrones >= 0 &&
    extraDrones <= 4 &&
    Number.isInteger(extraBatteries) &&
    extraBatteries >= 0 &&
    extraBatteries <= 8 &&
    energy >= 0.25 &&
    energy <= 4 &&
    flightTime >= 0.25 &&
    flightTime <= 4 &&
    soh >= 0.1 &&
    soh <= 1 &&
    reserve >= 0 &&
    reserve <= 1
  async function trial() {
    if (!plan || running || stale || !parametersValid) return
    setSubmitting(true)
    try {
      const fork = await api.whatIf(scenario.scenario_id, {
        expected_state_version: scenario.state_version,
        source_plan_id: plan.plan_id,
        name: '资源与余量试算',
        additions: [{ type_id: type, drones: extraDrones, batteries: extraBatteries }],
        energy_multiplier: energy,
        flight_time_multiplier: flightTime,
        battery_soh_multiplier: soh,
        min_return_soc: reserve,
        noncritical_deadline_multiplier: deadlineScale,
      })
      setReceipt(fork)
      setJobId('')
      await query.invalidateQueries({ queryKey: ['scenarios'] })
      const snap = await api.snapshot(fork.scenario)
      const task = await api.solve(
        snap.snapshot_id,
        plan.objective as 'time' | 'energy' | 'balanced',
        { time_limit_s: fork.scenario.policy.requires_communication ? 60 : 15 },
      )
      setJobId(task.job_id)
      query.setQueryData(['job', task.job_id], task)
      await query.invalidateQueries({ queryKey: ['what-if-history', scenario.scenario_id] })
      notify('试算场景已独立保存，正在真实计算。')
    } catch (e) {
      notify((e as Error).message, true)
    } finally {
      setSubmitting(false)
    }
  }
  if (!plan)
    return (
      <section className="panel analysis-empty">
        <Empty
          icon={<BarChart3 size={28} />}
          title="先生成一份真实方案"
          description="资源占用、时限余量和增配对照都基于具体方案与不可变快照。"
        />
      </section>
    )
  if (analysis.isError)
    return (
      <div className="alert alert-amber">
        <TriangleAlert size={18} />
        {(analysis.error as Error).message}
        <Button onClick={() => void analysis.refetch()}>重试</Button>
      </div>
    )
  if (!analysis.data)
    return (
      <section className="panel analysis-loading">
        <LoaderCircle size={20} className="spin" />
        正在读取本方案快照与资源占用…
      </section>
    )
  const a = analysis.data
  const hard = a.delivery.demands.filter((d) => d.hard_deadline_s != null).length
  const demands = a.delivery.demands.filter(
    (d) =>
      filter === 'all' ||
      (filter === 'late' && d.delay_s != null && d.delay_s > 0) ||
      (filter === 'hard' && d.hard_deadline_s != null),
  )
  return (
    <div className="resource-analysis">
      <div className="analysis-intro">
        <span>
          <ShieldCheck size={16} />
          绑定方案快照 v{a.scenario_state_version} · 分析不修改任何输入
        </span>
        <div className="analysis-actions">
          <Button
            onClick={() =>
              downloadJson(
                { analysis: a, trial: receipt, trial_plan: result.data || null },
                'yuanhang-resource-analysis.json',
              )
            }
          >
            <Download size={14} />
            导出分析JSON
          </Button>
          <a
            className="button button-default"
            href={api.reportUrl(plan.plan_id)}
            target="_blank"
            rel="noopener noreferrer"
          >
            打印报告
          </a>
        </div>
      </div>
      <div className="analysis-kpis">
        <div className="panel">
          <span>
            <CheckCircle2 size={15} />
            硬截止检查
          </span>
          <strong>{hard ? `${hard - a.delivery.hard_violation_count} / ${hard}` : '未设置'}</strong>
          <small>按每条需求的整站交接完成时间</small>
        </div>
        <div className="panel">
          <span>
            <Clock3 size={15} />
            期望按时完成
          </span>
          <strong>
            {a.delivery.expected_demand_count - a.delivery.late_demand_count}
            <em>/ {a.delivery.expected_demand_count} 条</em>
          </strong>
          <small>{a.delivery.late_demand_count}条期望延期，区别于硬截止违约</small>
        </div>
        <div className="panel">
          <span>
            <ShieldCheck size={15} />
            最小硬截止余量
          </span>
          <strong>{duration(a.min_hard_slack_s)}</strong>
          <small>这是确定性余量，不是成功概率</small>
        </div>
        <div className="panel">
          <span>
            <BatteryCharging size={15} />
            充电并发峰值
          </span>
          <strong>
            {a.charge_peak}
            <em>{plan.communication_report ? '个能源资源' : '块电池'}</em>
          </strong>
          <small>
            {a.resource_limits
              ? `实际并发 / ${a.resource_limits.charging_ports}个端口；准备峰值${a.prep_peak}/${a.resource_limits.prep_slots}`
              : '现有无限端口模型下的并发需求'}
          </small>
        </div>
      </div>
      <div className="analysis-columns">
        <div className="analysis-main">
          <section className="panel utilization-panel">
            <div className="panel-heading">
              <div>
                <h3>计划资源占用</h3>
                <p>占用包括准备、执行与周转；能源资源另含等待和补能</p>
              </div>
              <div className="segmented">
                <button
                  className={
                    kind === 'drone' || (!plan.communication_report && kind.startsWith('relay'))
                      ? 'active'
                      : ''
                  }
                  onClick={() => setKind('drone')}
                >
                  <Plane size={14} />
                  机体
                </button>
                <button
                  className={kind === 'battery' ? 'active' : ''}
                  onClick={() => setKind('battery')}
                >
                  <BatteryCharging size={14} />
                  电池
                </button>
                {plan.communication_report && (
                  <>
                    <button
                      className={kind === 'relay_drone' ? 'active' : ''}
                      onClick={() => setKind('relay_drone')}
                    >
                      <RadioTower size={14} />
                      中继机
                    </button>
                    <button
                      className={kind === 'relay_energy' ? 'active' : ''}
                      onClick={() => setKind('relay_energy')}
                    >
                      <BatteryCharging size={14} />
                      中继能源
                    </button>
                  </>
                )}
              </div>
            </div>
            <UtilizationChart data={rows} />
            <div className="analysis-resource-scroll">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>实体资源</th>
                    <th>架次</th>
                    <th>占用时长</th>
                    <th>累计能耗</th>
                    <th>计划占用率</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((r) => (
                    <tr key={r.resource_id}>
                      <td>
                        <i
                          className="resource-color"
                          style={{ background: colorFor(r.resource_id) }}
                        />
                        {r.resource_id} <small>{r.type_id}型</small>
                      </td>
                      <td>{r.sortie_count}</td>
                      <td>{duration(r.occupied_s)}</td>
                      <td>{number(r.energy_kwh, 2)} kWh</td>
                      <td>{percent(r.utilization)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="analysis-caption">
              比例分母为该类资源从零点至最后释放；充电峰值按左闭右开区间统计。
              {Object.entries(a.charge_peak_by_type)
                .map(([id, count]) => `${id}型 ${count}`)
                .join(' · ')}
              。端口容量尚未约束排程。
            </p>
          </section>
          <section className="panel delivery-analysis">
            <div className="panel-heading">
              <div>
                <h3>需求交付与时限</h3>
                <p>允许期望延期的需求单独呈现，所有硬截止仍需通过检查</p>
              </div>
              <select
                aria-label="筛选交付时限"
                value={filter}
                onChange={(e) => setFilter(e.target.value as typeof filter)}
              >
                <option value="all">全部需求</option>
                <option value="late">期望延期</option>
                <option value="hard">有硬截止</option>
              </select>
            </div>
            <div className="analysis-demand-scroll">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>需求 / 站点</th>
                    <th>已安排</th>
                    <th>交接完成</th>
                    <th>期望 / 硬截止</th>
                    <th>结果</th>
                  </tr>
                </thead>
                <tbody>
                  {demands.map((d) => (
                    <tr key={d.demand_id}>
                      <td>
                        <strong>{d.site_id}</strong>
                        <small className="demand-id">{d.demand_id}</small>
                      </td>
                      <td>
                        {d.served_quantity}/{d.required_quantity}箱
                      </td>
                      <td>{duration(d.complete_s)}</td>
                      <td>
                        <span>{duration(d.expected_deadline_s)}</span>
                        <small className="demand-id">硬 {duration(d.hard_deadline_s)}</small>
                      </td>
                      <td>
                        <Badge
                          tone={
                            d.complete_s == null || d.hard_satisfied === false
                              ? 'red'
                              : d.delay_s && d.delay_s > 0
                                ? 'amber'
                                : 'teal'
                          }
                        >
                          {d.complete_s == null
                            ? '未保障'
                            : d.hard_satisfied === false
                              ? '硬截止违约'
                              : d.delay_s && d.delay_s > 0
                                ? '期望延期 ' + duration(d.delay_s)
                                : '按时'}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {!demands.length && <div className="table-empty">没有匹配的需求。</div>}
            </div>
          </section>
          <ScenarioExperiments
            scenario={scenario}
            plan={plan}
            disabled={stale || running}
            onOpen={onOpen}
            onBusyChange={setHistoryBusy}
            notify={notify}
          />
        </div>
        <aside className="analysis-aside">
          <section className="panel what-if-panel">
            <div className="panel-heading">
              <div>
                <h3>
                  <FlaskConical size={16} />
                  资源与余量试算
                </h3>
                <p>从基线复制，改变参数后重新求解</p>
              </div>
              <Badge>不同输入</Badge>
            </div>
            <div className="what-if-form">
              <label className="field">
                <span>增配机型</span>
                <select
                  aria-label="增配机型"
                  value={type}
                  onChange={(e) => setType(e.target.value)}
                >
                  {scenario.drone_types.map((t) => (
                    <option key={t.type_id} value={t.type_id}>
                      {t.type_id}型 · {t.max_payload_kg}kg / {t.max_volume_l}L
                    </option>
                  ))}
                </select>
              </label>
              <div className="form-grid">
                <label className="field">
                  <span>增加机体 / 架</span>
                  <input
                    aria-label="增加机体"
                    type="number"
                    min="0"
                    max="4"
                    value={extraDrones}
                    onChange={(e) => setExtraDrones(Number(e.target.value))}
                  />
                </label>
                <label className="field">
                  <span>增加电池 / 块</span>
                  <input
                    aria-label="增加电池"
                    type="number"
                    min="0"
                    max="8"
                    value={extraBatteries}
                    onChange={(e) => setExtraBatteries(Number(e.target.value))}
                  />
                </label>
                <label className="field">
                  <span>能耗倍率</span>
                  <input
                    aria-label="试算能耗倍率"
                    type="number"
                    min=".25"
                    max="4"
                    step=".05"
                    value={energy}
                    onChange={(e) => setEnergy(Number(e.target.value))}
                  />
                </label>
                <label className="field">
                  <span>飞行时长倍率</span>
                  <input
                    type="number"
                    min=".25"
                    max="4"
                    step=".05"
                    value={flightTime}
                    onChange={(e) => setFlightTime(Number(e.target.value))}
                  />
                </label>
                <label className="field">
                  <span>SOH倍率</span>
                  <input
                    aria-label="试算SOH倍率"
                    type="number"
                    min=".1"
                    max="1"
                    step=".05"
                    value={soh}
                    onChange={(e) => setSoh(Number(e.target.value))}
                  />
                </label>
                <label className="field">
                  <span>返航SOC下限</span>
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step=".05"
                    value={reserve}
                    onChange={(e) => setReserve(Number(e.target.value))}
                  />
                </label>
              </div>
              <label className="field">
                <span>非关键需求期望时限</span>
                <select
                  value={deadlineScale}
                  onChange={(e) => setDeadlineScale(Number(e.target.value))}
                >
                  <option value="1">保持原值</option>
                  <option value="1.2">仅无硬截止需求放宽20%</option>
                  <option value="1.5">仅无硬截止需求放宽50%</option>
                </select>
              </label>
              <div className="callout">
                <PackagePlus size={16} />
                新增资源来自同型参数假设；SOC满电、SOH再乘设定倍率。所有硬截止和必须保障需求保留。
              </div>
              <Button
                variant="primary"
                disabled={stale || scenario.data_origin === 'mock' || !parametersValid}
                busy={running}
                onClick={() => void trial()}
              >
                <FlaskConical size={15} />
                创建场景并真实试算
              </Button>
              {stale && <p className="what-if-warning">基线已过期，请先对当前版本重新求解。</p>}
              {!parametersValid && (
                <p className="what-if-warning">请填写范围内的数值，资源数量须为整数。</p>
              )}
              {running && (
                <div className="trial-running">
                  <LoaderCircle size={16} className="spin" />
                  独立进程{job.data?.job_state === 'queued' ? '排队' : '计算'}中…
                  {jobId && (
                    <button
                      aria-label="取消情景试算"
                      onClick={() =>
                        void api
                          .cancel(jobId)
                          .then(() => query.invalidateQueries({ queryKey: ['job', jobId] }))
                      }
                    >
                      <X size={15} />
                    </button>
                  )}
                </div>
              )}
            </div>
          </section>
          {receipt && (
            <section className="panel trial-result">
              <div className="panel-heading">
                <div>
                  <h3>本次试算结果</h3>
                  <p>基线 v{receipt.origin.source_state_version} → 独立新场景 v1</p>
                </div>
                <Badge tone={result.data ? 'teal' : 'amber'}>
                  {result.data
                    ? '已真实计算'
                    : job.data
                      ? statusLabel[job.data.solver_status || job.data.job_state]
                      : '待提交'}
                </Badge>
              </div>
              <div className="trial-changes">
                {receipt.origin.changes.map((change, i) => (
                  <p key={i}>{change}</p>
                ))}
              </div>
              {result.data ? (
                <>
                  <div className="trial-comparison">
                    <div>
                      <span>全部返航</span>
                      <small>{duration(baseline.data?.metrics.makespan_s)}</small>
                      <ChevronRight size={13} />
                      <strong>{duration(result.data.metrics.makespan_s)}</strong>
                    </div>
                    <div>
                      <span>预计能耗</span>
                      <small>{number(baseline.data?.metrics.energy_kwh, 2)}</small>
                      <ChevronRight size={13} />
                      <strong>{number(result.data.metrics.energy_kwh, 2)} kWh</strong>
                    </div>
                    <div>
                      <span>返航最低SOC</span>
                      <small>{percent(baseline.data?.metrics.min_return_soc)}</small>
                      <ChevronRight size={13} />
                      <strong>{percent(result.data.metrics.min_return_soc)}</strong>
                    </div>
                  </div>
                  <p className="analysis-caption">
                    输入条件不同，不能作为同条件策略优越性的证明。未证明最少增配或真实成功概率。
                  </p>
                  <Button onClick={() => onOpen(receipt.scenario)}>
                    打开试算场景 <ChevronRight size={14} />
                  </Button>
                </>
              ) : job.data && ['completed', 'failed', 'canceled'].includes(job.data.job_state) ? (
                <p className="trial-error">
                  <TriangleAlert size={16} />
                  {job.data.error?.message ||
                    diagnostic.data?.diagnostics[0]?.message ||
                    '本次未发布可行方案；这不自动证明所有配置无解。'}
                </p>
              ) : null}
            </section>
          )}
        </aside>
      </div>
    </div>
  )
}
