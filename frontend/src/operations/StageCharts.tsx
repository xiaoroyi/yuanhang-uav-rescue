import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import type { EChartsOption } from 'echarts'
import { api, type Plan } from '../api/client'
import { ops } from '../api/operations'
import { DataChart } from '../components/DataChart'
import { clock, number } from '../lib/format'

const phaseLabel = {
  prepare: '准备装载',
  climb: '爬升',
  cruise: '巡航',
  descent: '下降',
  handover: '交接',
  turnaround: '周转',
  charge_wait: '待充',
  charge: '充电',
  relay_link: '中继建链',
  relay_service: '中继服务',
}
export function StageCharts({ plan, selected }: { plan: Plan; selected: string }) {
  const [mode, setMode] = useState<'height' | 'soc' | 'energy' | 'phases'>('height')
  const stages = useQuery({
    queryKey: ['stages', plan.plan_id],
    queryFn: () => ops.stages(plan.plan_id),
  })
  const profile = useQuery({
    queryKey: ['flight-profile', plan.plan_id, selected],
    queryFn: () => api.flightProfile(plan.plan_id, selected),
    enabled: !!selected,
  })
  const rows = useMemo(
    () => stages.data?.trajectory_segments.filter((s) => s.sortie_id === selected) || [],
    [stages.data, selected],
  )
  const option = useMemo<EChartsOption>(() => {
    if (mode === 'height') {
      const data = profile.data?.legs.flatMap((l) => l.samples) || []
      return {
        grid: { left: 56, right: 20, top: 22, bottom: 40 },
        xAxis: { type: 'value', name: '距离 / km' },
        yAxis: { type: 'value', name: '高程 / m', scale: true },
        series: [
          {
            name: '地面高程',
            type: 'line',
            showSymbol: false,
            connectNulls: false,
            areaStyle: { color: '#90a78b50' },
            lineStyle: { color: '#6f8c68', width: 1.5 },
            data: data.map((p) => [p.distance_m / 1000, p.ground_elevation_m]),
          },
          {
            name: '模型巡航高度',
            type: 'line',
            showSymbol: false,
            lineStyle: { color: '#2563eb', width: 2 },
            data: data.map((p) => [p.distance_m / 1000, p.cruise_elevation_m]),
          },
        ],
      }
    }
    if (mode === 'soc')
      return {
        grid: { left: 48, right: 25, top: 22, bottom: 40 },
        xAxis: { type: 'value', name: '时间 / min' },
        yAxis: { type: 'value', name: 'SOC / %', min: 0, max: 100 },
        series: [
          {
            name: '已计算阶段端点',
            type: 'scatter',
            symbolSize: 5,
            itemStyle: { color: '#2563eb' },
            data: rows.flatMap((r) => [
              [r.start_s / 60, r.soc_start === null ? null : r.soc_start * 100],
              [r.end_s / 60, r.soc_end === null ? null : r.soc_end * 100],
            ]),
          },
          {
            name: '返航储备（所选策略）',
            type: 'line',
            showSymbol: false,
            lineStyle: { type: 'dashed', color: '#b45e18' },
            data: [],
          },
        ],
      }
    return {
      grid: { left: 48, right: 20, top: 22, bottom: 40 },
      xAxis: {
        type: 'category',
        data: rows.map((r) => `${phaseLabel[r.phase]} ${clock(r.start_s)}`),
        axisLabel: { hideOverlap: true },
      },
      yAxis: { type: 'value', name: mode === 'energy' ? 'kWh' : 'kg' },
      series: [
        {
          name: mode === 'energy' ? '分阶段能耗' : '阶段载荷',
          type: 'bar',
          itemStyle: { color: '#3d78c5' },
          data: rows.map((r) => (mode === 'energy' ? r.energy_kwh : r.payload_kg)),
        },
      ],
    }
  }, [mode, profile.data, rows])
  return (
    <section className="v2-stage-analysis">
      <div className="v2-section-bar">
        <h3>{selected || '选择架次'} · 航段分析</h3>
        <div className="v2-tabs">
          {(
            [
              ['height', '高程剖面'],
              ['soc', '电量端点'],
              ['energy', '能耗分解'],
              ['phases', '载荷变化'],
            ] as const
          ).map(([id, label]) => (
            <button key={id} className={mode === id ? 'active' : ''} onClick={() => setMode(id)}>
              {label}
            </button>
          ))}
        </div>
      </div>
      {stages.error || profile.error ? (
        <p className="v2-inline-error">{stages.error?.message || profile.error?.message}</p>
      ) : stages.isPending ? (
        <p>读取阶段数据…</p>
      ) : (
        <DataChart option={option} label={`${selected} ${mode} 分析`} height={180} />
      )}
      <p className="v2-chart-note">
        {mode === 'height'
          ? `水平轴为航路距离 · 高程基准 ${profile.data?.vertical_datum || '未知'} · 巡航包络不表示完整实飞高度`
          : mode === 'soc'
            ? '仅显示物理模型已计算的阶段端点；阶段内连续 SOC 未计算，不连接成实测曲线。'
            : `阶段能耗合计 ${number(
                rows.reduce((n, r) => n + r.energy_kwh, 0),
                3,
              )} kWh · 载荷在交接完成时变化`}
      </p>
    </section>
  )
}
