import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  ArrowLeftRight,
  ArrowRight,
  Download,
  GitCompareArrows,
  ShieldCheck,
  TriangleAlert,
} from 'lucide-react'
import type { EChartsOption } from 'echarts'
import { api, downloadJson, type Plan, type PlanSummary, type Scenario } from '../api/client'
import { Badge, Button, Empty } from '../components/ui'
import { DataChart } from '../components/DataChart'
import { number, duration, percent } from '../lib/format'
import { policyLabel } from '../lib/strategies'
import { preferenceName, dateTime } from './HistoryCenter'
import './history-compare.css'

function planOption(p: PlanSummary) {
  return `${preferenceName[p.objective] || p.objective} · v${p.scenario_state_version} · ${dateTime(p.generated_at)} · ${p.plan_id.slice(-6)}`
}
export function CompareCenter({
  scenario,
  selectedPlanId,
  onOpenPlan,
  onWorkspace,
}: {
  scenario: Scenario
  selectedPlanId: string
  onOpenPlan: (id: string) => void
  onWorkspace: () => void
}) {
  const [left, setLeft] = useState(''),
    [right, setRight] = useState('')
  const summaries = useQuery({
    queryKey: ['plans', scenario.scenario_id],
    queryFn: () => api.plans(scenario.scenario_id),
  })
  const sorted = useMemo(
    () => [...(summaries.data || [])].sort((a, b) => b.generated_at.localeCompare(a.generated_at)),
    [summaries.data],
  )
  const aId = sorted.some((p) => p.plan_id === left)
    ? left
    : sorted.some((p) => p.plan_id === selectedPlanId)
      ? selectedPlanId
      : sorted[0]?.plan_id || ''
  const aSummary = sorted.find((p) => p.plan_id === aId)
  const bId = sorted.some((p) => p.plan_id === right && p.plan_id !== aId)
    ? right
    : sorted.find((p) => p.plan_id !== aId && p.snapshot_id === aSummary?.snapshot_id)?.plan_id ||
      sorted.find((p) => p.plan_id !== aId)?.plan_id ||
      ''
  const a = useQuery({ queryKey: ['plan', aId], queryFn: () => api.plan(aId), enabled: !!aId })
  const b = useQuery({ queryKey: ['plan', bId], queryFn: () => api.plan(bId), enabled: !!bId })
  const qa = useQuery({
    queryKey: ['analysis', aId],
    queryFn: () => api.analysis(aId),
    enabled: !!aId,
  })
  const qb = useQuery({
    queryKey: ['analysis', bId],
    queryFn: () => api.analysis(bId),
    enabled: !!bId,
  })
  const comparison = useQuery({
    queryKey: ['comparison', aId, bId],
    queryFn: () => api.compare(aId, bId),
    enabled: !!aId && !!bId,
  })
  const comparable = comparison.data?.comparable === true
  const chart = useMemo<EChartsOption>(() => {
    const plans = [a.data, b.data].filter((p): p is Plan => !!p)
    return {
      color: ['#55c9ff', '#ab97ff'],
      tooltip: { trigger: 'axis' },
      legend: { bottom: 2, textStyle: { color: '#93a8c5' } },
      grid: [
        { top: 40, bottom: 55, left: 45, right: '59%' },
        { top: 40, bottom: 55, left: '57%', right: 10 },
      ],
      xAxis: [['运输能耗'], ['最后返航', '最后交付']].map((data, i) => ({
        type: 'category',
        gridIndex: i,
        data,
        axisLabel: { color: '#9badc6', fontSize: 10 },
        axisLine: { lineStyle: { color: '#344963' } },
      })),
      yAxis: ['kWh', '分钟'].map((name, i) => ({
        type: 'value',
        gridIndex: i,
        name,
        nameTextStyle: { color: '#9badc6' },
        axisLabel: { color: '#9badc6' },
        splitLine: { lineStyle: { color: '#8299b31c' } },
      })),
      series: plans.flatMap((p, i) =>
        [0, 1].map((axis) => ({
          name: `${i ? 'B' : 'A'} · ${preferenceName[p.objective]}`,
          type: 'bar',
          xAxisIndex: axis,
          yAxisIndex: axis,
          barMaxWidth: 36,
          itemStyle: { borderRadius: [5, 5, 0, 0], color: i ? '#ab97ff' : '#55c9ff' },
          data:
            axis === 0
              ? [p.metrics.energy_kwh]
              : [
                  p.metrics.makespan_s == null ? null : p.metrics.makespan_s / 60,
                  p.metrics.last_delivery_s == null ? null : p.metrics.last_delivery_s / 60,
                ],
        })),
      ),
    }
  }, [a.data, b.data])
  const metrics: [string, (p: Plan) => number | null, (n: number | null) => string, boolean][] = [
    [
      '加权箱件延期 / 箱·秒',
      (p) => (p.plan_id === aId ? qa.data : qb.data)?.delivery.weighted_box_delay_s ?? null,
      (n) => number(n, 2),
      true,
    ],
    [
      '期望截止后交付需求 / 条',
      (p) => (p.plan_id === aId ? qa.data : qb.data)?.delivery.late_demand_count ?? null,
      (n) => number(n, 0),
      true,
    ],
    ['运输能耗 / kWh', (p) => p.metrics.energy_kwh, (n) => number(n, 3), true],
    ['最后交付', (p) => p.metrics.last_delivery_s, (n) => duration(n), true],
    ['最后返航', (p) => p.metrics.makespan_s, (n) => duration(n), true],
    ['运输架次', (p) => p.metrics.sortie_count, (n) => number(n, 0), true],
    ['最低返航电量', (p) => p.metrics.min_return_soc, (n) => percent(n), false],
    [
      '联合总能耗 / kWh',
      (p) => p.joint_metrics?.joint_energy_kwh ?? null,
      (n) => number(n, 3),
      true,
    ],
  ]
  return (
    <section className="compare-page">
      <div className="experience-heading">
        <div>
          <div className="eyebrow">DECISION LAB</div>
          <h1>把选择，放在同一张图上</h1>
          <p>比较实际保存的方案。指标来自真实求解结果，快照与模型范围决定是否能作同条件评价。</p>
        </div>
        <Button
          disabled={!a.data || !b.data || !comparison.data}
          onClick={() =>
            downloadJson(
              { comparison: comparison.data, plan_a: a.data, plan_b: b.data },
              'yuanhang-plan-comparison.json',
            )
          }
        >
          <Download size={15} />
          导出完整对比
        </Button>
      </div>
      {summaries.isError ? (
        <Empty
          icon={<GitCompareArrows />}
          title="方案列表未能读取"
          description={summaries.error.message}
        />
      ) : sorted.length < 2 ? (
        <Empty
          icon={<GitCompareArrows size={32} />}
          title="再计算一份方案，就能展开对比"
          description="在工作台生成另一种策略、深入优化方案，或在事件后重规划；所有结果都会自动保存。"
          action={
            <Button onClick={onWorkspace}>
              前往工作台
              <ArrowRight size={14} />
            </Button>
          }
        />
      ) : (
        <>
          <div className="comparison-selectors">
            <label>
              <span className="comparison-key key-a">A</span>
              <div>
                <small>比较基准</small>
                <select
                  aria-label="方案对比A"
                  value={aId}
                  onChange={(e) => setLeft(e.target.value)}
                >
                  {sorted.map((p) => (
                    <option key={p.plan_id} value={p.plan_id}>
                      {planOption(p)}
                    </option>
                  ))}
                </select>
              </div>
            </label>
            <button
              aria-label="交换对比方案"
              onClick={() => {
                setLeft(bId)
                setRight(aId)
              }}
            >
              <ArrowLeftRight size={19} />
            </button>
            <label>
              <span className="comparison-key key-b">B</span>
              <div>
                <small>候选方案</small>
                <select
                  aria-label="方案对比B"
                  value={bId}
                  onChange={(e) => setRight(e.target.value)}
                >
                  {sorted
                    .filter((p) => p.plan_id !== aId)
                    .map((p) => (
                      <option key={p.plan_id} value={p.plan_id}>
                        {planOption(p)}
                      </option>
                    ))}
                </select>
              </div>
            </label>
          </div>
          {comparison.isError || a.isError || b.isError ? (
            <div role="alert" className="comparison-notice warning">
              <TriangleAlert size={20} />
              {comparison.error?.message || a.error?.message || b.error?.message}
              <Button
                onClick={() => {
                  void a.refetch()
                  void b.refetch()
                  void comparison.refetch()
                }}
              >
                重试
              </Button>
            </div>
          ) : comparison.isLoading || a.isLoading || b.isLoading ? (
            <p className="archive-loading">正在读取方案与可比性检查…</p>
          ) : (
            a.data &&
            b.data &&
            comparison.data && (
              <>
                <div className={`comparison-notice ${comparable ? 'valid' : 'warning'}`}>
                  {comparable ? <ShieldCheck size={22} /> : <TriangleAlert size={22} />}
                  <div>
                    <strong>
                      {comparable
                        ? '同快照、同模型范围 · 可比较策略结果'
                        : '不同输入或模型范围 · 仅查看前后变化'}
                    </strong>
                    <p>
                      {comparable
                        ? '仍需同时查看软延期等共同首目标；这里不声称有限搜索达到了全局最优。'
                        : comparison.data.warnings.join(' ')}
                    </p>
                  </div>
                  <Badge tone={comparable ? 'teal' : 'amber'}>
                    {comparison.data.same_snapshot ? '同一快照' : '不同快照'}
                  </Badge>
                </div>
                <div className="comparison-overview">
                  <section className="experience-chart-panel">
                    <div className="experience-chart-title">
                      <h3>时间与能源取舍</h3>
                      <small>各列单位见纵轴 · 原值展示</small>
                    </div>
                    <DataChart
                      option={chart}
                      label="两个真实方案的运输能耗、最后返航和交付对比"
                      height={310}
                    />
                    <p className="chart-note">
                      能耗按 kWh、时间按分钟分别读取；并排展示不代表不同单位可直接相加。
                    </p>
                  </section>
                  <section className="experience-chart-panel comparison-lineage">
                    <h3>方案来源与验证</h3>
                    {[a.data, b.data].map((p, i) => (
                      <div key={p.plan_id}>
                        <span className={`comparison-key ${i ? 'key-b' : 'key-a'}`}>
                          {i ? 'B' : 'A'}
                        </span>
                        <div>
                          <strong>
                            {preferenceName[p.objective]} <Badge>v{p.scenario_state_version}</Badge>
                          </strong>
                          <code>{p.plan_id}</code>
                          <small>
                            快照 {p.snapshot_id} · {policyLabel(p)}
                          </small>
                          <p>
                            {p.validation.status === 'passed' ? '独立检查通过' : '未通过独立检查'} ·{' '}
                            {p.solver_status}
                          </p>
                          <Button onClick={() => onOpenPlan(p.plan_id)}>
                            打开此方案
                            <ArrowRight size={13} />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </section>
                </div>
                <section className="experience-chart-panel">
                  <div className="experience-chart-title">
                    <h3>关键指标明细</h3>
                    <small>差值统一为 B − A；无数据保留“—”</small>
                  </div>
                  <div className="archive-table-wrap">
                    <table className="archive-table comparison-metrics">
                      <thead>
                        <tr>
                          <th>指标</th>
                          <th>方案 A</th>
                          <th>方案 B</th>
                          <th>B − A</th>
                        </tr>
                      </thead>
                      <tbody>
                        {metrics.map(([label, get, format, lower]) => {
                          const va = get(a.data!),
                            vb = get(b.data!)
                          const d = va == null || vb == null ? null : vb - va
                          return (
                            <tr key={label}>
                              <th>{label}</th>
                              <td>{format(va)}</td>
                              <td>{format(vb)}</td>
                              <td
                                className={
                                  comparable && d != null && d !== 0
                                    ? (lower ? d < 0 : d > 0)
                                      ? 'delta-positive'
                                      : 'delta-negative'
                                    : ''
                                }
                              >
                                {d == null
                                  ? '—'
                                  : `${d > 0 ? '+' : d < 0 ? '−' : ''}${format(Math.abs(d))}`}
                              </td>
                            </tr>
                          )
                        })}
                      </tbody>
                    </table>
                  </div>
                </section>
                <div className="comparison-counts">
                  <div>
                    <strong>{comparison.data.preserved_sortie_ids.length}</strong>
                    <span>保留相同架次ID</span>
                  </div>
                  <div>
                    <strong>{comparison.data.removed_sortie_ids.length}</strong>
                    <span>移除的架次ID</span>
                  </div>
                  <div>
                    <strong>{comparison.data.added_sortie_ids.length}</strong>
                    <span>新增的架次ID</span>
                  </div>
                  <p>架次ID变化不等于箱件改派数量；逐箱机体/电池改派请在事件复盘查看。</p>
                </div>
              </>
            )
          )}
        </>
      )}
    </section>
  )
}
