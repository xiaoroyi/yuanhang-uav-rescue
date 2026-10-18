import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import type { EChartsOption } from 'echarts'
import { api, type Plan } from '../api/client'
import { ops } from '../api/operations'
import { DataChart } from '../components/DataChart'

export function PlanInsights({ plan }: { plan: Plan }) {
  const stages = useQuery({
    queryKey: ['stages', plan.plan_id],
    queryFn: () => ops.stages(plan.plan_id),
  })
  const analysis = useQuery({
    queryKey: ['analysis', plan.plan_id],
    queryFn: () => api.analysis(plan.plan_id),
  })
  const loadOption = useMemo<EChartsOption>(() => {
    const rows = stages.data?.sortie_loads || []
    return {
      grid: { left: 48, right: 20, top: 28, bottom: 40 },
      xAxis: {
        type: 'category',
        data: rows.map((r, i) => `${i + 1} · ${r.drone_id}`),
        axisLabel: { hideOverlap: true },
      },
      yAxis: { type: 'value', name: '利用率 / %', min: 0, max: 100 },
      series: [
        {
          type: 'bar',
          name: '载重',
          data: rows.map((r) => r.mass_utilization * 100),
          itemStyle: { color: '#3e79c9' },
        },
        {
          type: 'bar',
          name: '容积',
          data: rows.map((r) => r.volume_utilization * 100),
          itemStyle: { color: '#769e8b' },
        },
      ],
    }
  }, [stages.data])
  const serviceOption = useMemo<EChartsOption>(() => {
    const rows = (analysis.data?.delivery.demands || [])
      .filter((d) => d.complete_s !== null)
      .sort((a, b) => a.complete_s! - b.complete_s!)
    let count = 0
    return {
      grid: { left: 48, right: 25, top: 28, bottom: 40 },
      xAxis: { type: 'value', name: '时间 / min' },
      yAxis: { type: 'value', name: '计划保障 / 箱', min: 0 },
      series: [
        {
          name: '需求全部保障',
          type: 'line',
          step: 'end',
          showSymbol: true,
          symbolSize: 4,
          lineStyle: { color: '#3e79c9' },
          data: [[0, 0], ...rows.map((r) => [r.complete_s! / 60, (count += r.served_quantity)])],
        },
      ],
    }
  }, [analysis.data])
  return (
    <div className="v2-insights-grid">
      <section className="v2-card">
        <div className="v2-section-bar">
          <h3>架次载重与容积</h3>
          <span className="v2-subtle">原始 Plan / Snapshot</span>
        </div>
        <DataChart option={loadOption} height={240} label="架次载重与容积利用率" />
        <p className="v2-chart-note">
          重量与总体积容量约束；未建模几何三维装箱，不据此认证箱件摆放。
        </p>
      </section>
      <section className="v2-card">
        <div className="v2-section-bar">
          <h3>需求保障进度</h3>
          <span className="v2-subtle">计划量，非实际签收</span>
        </div>
        <DataChart option={serviceOption} height={240} label="需求完整保障阶梯图" />
        <p className="v2-chart-note">
          按每项需求全部交接完成计数；不把任意一箱到达当作整站基本保障。
        </p>
      </section>
    </div>
  )
}
