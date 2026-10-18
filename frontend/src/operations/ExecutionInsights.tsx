import { useMemo } from 'react'
import type { EChartsOption } from 'echarts'
import type { Plan } from '../api/client'
import type { ExecutionAnalysis } from '../api/operations'
import { DataChart } from '../components/DataChart'
import { clock } from './format'

export function ExecutionInsights({
  analysis,
  initialPlan,
}: {
  analysis: ExecutionAnalysis
  initialPlan: Plan
}) {
  const rows = useMemo(() => analysis.deviation_rows || [], [analysis.deviation_rows])
  const options = useMemo<EChartsOption>(() => {
    const initial = initialPlan.sorties
      .flatMap((r) => r.visits)
      .flatMap((v) => v.cargo_ids.map(() => v.delivery_complete_s))
      .sort((a, b) => a - b)
    const actual = rows.map((r) => r.delivered_s).sort((a, b) => a - b)
    return {
      color: ['#94a3b8', '#2563eb'],
      grid: { left: 50, right: 28, top: 30, bottom: 55 },
      xAxis: { type: 'value', name: '时间 / min' },
      yAxis: { type: 'value', name: '箱数', min: 0 },
      series: [
        {
          name: '初始预计',
          type: 'line',
          step: 'end',
          showSymbol: false,
          data: [[0, 0], ...initial.map((t, i) => [t / 60, i + 1])],
          lineStyle: { color: '#94a3b8', type: 'dashed' },
        },
        {
          name: '模拟交付（含插单）',
          type: 'line',
          step: 'end',
          showSymbol: true,
          symbolSize: 5,
          data: [[0, 0], ...actual.map((t, i) => [t / 60, i + 1])],
          lineStyle: { color: '#2563eb' },
        },
      ],
    }
  }, [rows, initialPlan])
  const deviations = useMemo<EChartsOption>(
    () => ({
      grid: { left: 50, right: 25, top: 30, bottom: 60 },
      xAxis: {
        type: 'category',
        data: rows.filter((r) => r.difference_s !== null).map((r) => r.cargo_id),
        axisLabel: { hideOverlap: true },
      },
      yAxis: { type: 'value', name: '偏差 / min' },
      series: [
        {
          name: '模拟时刻 − 初始预计',
          type: 'bar',
          data: rows
            .filter((r) => r.difference_s !== null)
            .map((r) => ({
              value: r.difference_s! / 60,
              itemStyle: { color: r.difference_s! > 0 ? '#d97706' : '#0f766e' },
            })),
        },
      ],
    }),
    [rows],
  )
  return (
    <>
      <div className="v2-insights-grid v2-execution-insights-grid">
        <section className="v2-card">
          <h3>计划与模拟交付进度</h3>
          <p>虚线为初始预计；实线来自已记账事实，新增需求单独计入模拟总量。</p>
          <DataChart label="初始计划与模拟交付阶梯图" option={options} height={250} />
        </section>
        <section className="v2-card">
          <h3>逐箱交付时间偏差</h3>
          <p>正数为晚于初始预计；新增箱件无初始基准，不绘制为零偏差。</p>
          <DataChart label="模拟交付相对初始计划偏差" option={deviations} height={250} />
        </section>
      </div>
      <section className="v2-card">
        <h3>交付与来源明细</h3>
        <div className="v2-table-scroll">
          <table className="v2-table">
            <thead>
              <tr>
                <th>箱件</th>
                <th>初始预计</th>
                <th>模拟交付</th>
                <th>偏差</th>
                <th>方案 / 架次</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.cargo_id}>
                  <td>{r.cargo_id}</td>
                  <td>
                    {r.initial_expected_s === null ? '无初始基准' : clock(r.initial_expected_s)}
                  </td>
                  <td>{clock(r.delivered_s)}</td>
                  <td>
                    {r.difference_s === null
                      ? '—'
                      : (r.difference_s > 0 ? '+' : '') + (r.difference_s / 60).toFixed(2) + ' min'}
                  </td>
                  <td>
                    <small>{r.plan_id}</small>
                    {r.sortie_id}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!rows.length && <p>尚无模拟交付事实</p>}
        </div>
      </section>
    </>
  )
}
