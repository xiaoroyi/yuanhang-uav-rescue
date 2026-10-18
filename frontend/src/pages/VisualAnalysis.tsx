import { useEffect, useMemo, useRef, useState, type ReactNode } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Activity,
  ArrowDownToLine,
  ArrowRight,
  BarChart3,
  BatteryCharging,
  Boxes,
  CheckCircle2,
  ChevronRight,
  CircleHelp,
  Clock3,
  Compass,
  Fingerprint,
  Fullscreen,
  Layers3,
  LoaderCircle,
  MapPinned,
  Minimize2,
  Orbit,
  Plane,
  RadioTower,
  ShieldCheck,
  Sparkles,
  Workflow,
  Zap,
} from 'lucide-react'
import { init, use as registerCharts, type EChartsCoreOption } from 'echarts/core'
import { BarChart, LineChart, PieChart, ScatterChart } from 'echarts/charts'
import { GridComponent, LegendComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { api, downloadJson, type Plan, type Scenario } from '../api/client'
import { TerrainScene } from '../components/TerrainScene'
import { category, duration, number, percent, statusLabel } from '../lib/format'
import {
  analysisPalette,
  chartText,
  formatChartValue,
  visualAnalysisData,
} from './visual-analysis-data'
import './visual-analysis.css'

registerCharts([
  BarChart,
  LineChart,
  PieChart,
  ScatterChart,
  GridComponent,
  LegendComponent,
  TooltipComponent,
  CanvasRenderer,
])

const namedKind = (kind: string) => category[kind] || kind
const objectiveLabel = { time: '时间优先', energy: '能耗优先', balanced: '时间能耗折中' }
const axisStyle = { color: '#8398b6', fontSize: 10 }
const splitStyle = { lineStyle: { color: '#ffffff0b', type: 'dashed' } }
const chartTooltip = {
  backgroundColor: '#15223a',
  borderColor: '#344767',
  textStyle: { color: '#e3edff', fontSize: 11 },
  padding: [10, 13],
  confine: true,
  extraCssText: 'box-shadow:0 8px 28px #0004;border-radius:9px;',
}

function AnalysisChart({
  option,
  label,
  height = 270,
}: {
  option: EChartsCoreOption
  label: string
  height?: number
}) {
  const host = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (!host.current) return
    const chart = init(host.current, undefined, { renderer: 'canvas' })
    const motion = window.matchMedia('(prefers-reduced-motion: reduce)')
    const record = (raw: unknown) =>
      raw && typeof raw === 'object' ? (raw as Record<string, unknown>) : {}
    const draw = () => {
      const light = document.documentElement.dataset.theme === 'light'
      const compact =
        !!host.current?.closest('.va-overview') &&
        window.innerWidth >= 1250 &&
        window.innerHeight >= 760
      const ink = light ? '#526b8e' : '#8398b6'
      const axis = (raw: unknown) => {
        if (!raw) return raw
        const a = record(raw),
          split = record(a.splitLine)
        return {
          ...a,
          axisLabel: { ...record(a.axisLabel), color: ink, ...(compact ? { fontSize: 8 } : {}) },
          nameTextStyle: {
            ...record(a.nameTextStyle),
            color: ink,
            ...(compact ? { fontSize: 8 } : {}),
          },
          splitLine: {
            ...split,
            lineStyle: { ...record(split.lineStyle), color: light ? '#8197b326' : '#ffffff0b' },
          },
        }
      }
      chart.setOption({
        color: analysisPalette,
        backgroundColor: 'transparent',
        animation: !motion.matches,
        animationDuration: 500,
        textStyle: { fontFamily: 'Inter, "Microsoft YaHei", sans-serif' },
        ...option,
        ...(compact && option.grid
          ? {
              grid: {
                ...record(option.grid),
                top: 19,
                left: 38,
                right: 20,
                bottom: option.legend ? 32 : 26,
              },
            }
          : {}),
        ...(option.xAxis ? { xAxis: axis(option.xAxis) } : {}),
        ...(option.yAxis ? { yAxis: axis(option.yAxis) } : {}),
        ...(option.legend
          ? {
              legend: {
                ...record(option.legend),
                textStyle: {
                  ...record(record(option.legend).textStyle),
                  color: ink,
                  ...(compact ? { fontSize: 8, lineHeight: 17 } : {}),
                },
                ...(compact ? { itemWidth: 6, itemHeight: 5, itemGap: 7, right: 7 } : {}),
              },
            }
          : {}),
        ...(Array.isArray(option.series)
          ? {
              series: option.series.map((raw: unknown) => {
                const s = record(raw)
                return s.label
                  ? { ...s, label: { ...record(s.label), color: light ? '#526b8e' : '#aebcdb' } }
                  : s
              }),
            }
          : {}),
        ...(Array.isArray(option.graphic)
          ? {
              graphic: option.graphic.map((raw: unknown) => {
                const g = record(raw),
                  style = record(g.style)
                return {
                  ...g,
                  style: {
                    ...style,
                    ...(compact && Number(style.fontSize) >= 20 ? { fontSize: 24 } : {}),
                    fill: light ? (Number(style.fontSize) >= 20 ? '#2b4262' : ink) : style.fill,
                  },
                }
              }),
            }
          : {}),
      })
    }
    draw()
    const theme = new MutationObserver(draw)
    theme.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
    const mode = new MutationObserver(draw)
    const page = host.current.closest('.visual-analysis')
    if (page) mode.observe(page, { attributes: true, attributeFilter: ['class'] })
    const observer = new ResizeObserver(() => {
      chart.resize()
      draw()
    })
    observer.observe(host.current)
    const change = () => chart.setOption({ animation: !motion.matches })
    motion.addEventListener('change', change)
    return () => {
      observer.disconnect()
      theme.disconnect()
      mode.disconnect()
      motion.removeEventListener('change', change)
      chart.dispose()
    }
  }, [option])
  return (
    <div
      className="va-chart"
      ref={host}
      style={{ height }}
      role="img"
      aria-label={`${label}。精确数值可展开下方数据表查看。`}
    />
  )
}

function ChartPanel({
  index,
  title,
  description,
  children,
  table,
  wide = false,
}: {
  index: string
  title: string
  description: string
  children: ReactNode
  table: ReactNode
  wide?: boolean
}) {
  return (
    <section data-chart={index} className={`va-panel va-chart-panel ${wide ? 'va-wide' : ''}`}>
      <div className="va-panel-heading">
        <span className="va-section-index">{index}</span>
        <div>
          <h3>{title}</h3>
          <p>{description}</p>
        </div>
        <BarChart3 size={17} />
      </div>
      {children}
      <details className="va-data">
        <summary>
          查看精确数据 <ChevronRight size={12} />
        </summary>
        <div className="va-table-wrap">{table}</div>
      </details>
    </section>
  )
}

function MethodCard({
  icon,
  title,
  tag,
  children,
  evidence,
  supported,
}: {
  icon: ReactNode
  title: string
  tag: string
  children: ReactNode
  evidence: string
  supported: boolean
}) {
  return (
    <article className="va-method">
      <div className="va-method-top">
        <span className="va-method-icon">{icon}</span>
        <span className={supported ? 'va-proof' : 'va-proof va-proof-idle'}>
          {supported ? <CheckCircle2 size={10} /> : <CircleHelp size={10} />}
          {tag}
        </span>
      </div>
      <h4>{title}</h4>
      <p>{children}</p>
      <div className="va-method-evidence">{evidence}</div>
    </article>
  )
}

function FlightProfilePanel({ plan }: { plan: Plan }) {
  const [choice, setChoice] = useState('')
  const sortie = plan.sorties.find((f) => f.sortie_id === choice) || plan.sorties[0]
  const query = useQuery({
    queryKey: ['flight-profile', plan.plan_id, sortie?.sortie_id],
    queryFn: () => api.flightProfile(plan.plan_id, sortie.sortie_id),
    enabled: !!sortie,
    staleTime: Infinity,
    retry: 1,
  })
  const data = query.data
  const option = useMemo<EChartsCoreOption>(() => {
    if (!data) return {}
    const samples = data.legs.flatMap((leg) => leg.samples)
    return {
      tooltip: {
        ...chartTooltip,
        trigger: 'axis',
        valueFormatter: (v: unknown) => formatChartValue(v, 2, ' m'),
      },
      legend: {
        bottom: 0,
        textStyle: axisStyle,
        itemWidth: 10,
        itemHeight: 7,
        data: ['DEM地面采样', '模型巡航高程', '节点作业高程'],
      },
      grid: { top: 25, left: 60, right: 24, bottom: 56 },
      xAxis: {
        type: 'value',
        name: 'km',
        nameTextStyle: axisStyle,
        axisLabel: axisStyle,
        splitLine: splitStyle,
      },
      yAxis: {
        type: 'value',
        name: '高程 / m',
        nameTextStyle: axisStyle,
        axisLabel: axisStyle,
        splitLine: splitStyle,
        scale: true,
      },
      series: [
        {
          name: 'DEM地面采样',
          type: 'line',
          showSymbol: false,
          connectNulls: false,
          lineStyle: { color: '#78aba5', width: 1.6 },
          itemStyle: { color: '#78aba5' },
          areaStyle: { color: '#537d7d', opacity: 0.16 },
          data: samples.map((s) => [s.distance_m / 1000, s.ground_elevation_m]),
        },
        {
          name: '模型巡航高程',
          type: 'line',
          showSymbol: false,
          connectNulls: false,
          lineStyle: { color: '#ada2ff', width: 2 },
          itemStyle: { color: '#ada2ff' },
          data: data.legs.flatMap((l) => [
            [l.start_distance_m / 1000, l.cruise_elevation_m],
            [l.end_distance_m / 1000, l.cruise_elevation_m],
            [null, null],
          ]),
        },
        {
          name: '节点作业高程',
          type: 'scatter',
          symbolSize: 7,
          itemStyle: { color: '#ffca80', borderWidth: 1, borderColor: '#ffe6bf' },
          data: data.legs.flatMap((l) => [
            [l.start_distance_m / 1000, l.start_work_elevation_m],
            [l.end_distance_m / 1000, l.end_work_elevation_m],
          ]),
        },
      ],
    }
  }, [data])
  return (
    <section className="va-panel va-profile-panel">
      <div className="va-panel-heading">
        <span className="va-section-index">H</span>
        <div>
          <h3>航段地形与巡航高程剖面</h3>
          <p>参考论文净空剖面与多站任务分析，按本方案原快照重新读取物理模型。</p>
        </div>
        <Layers3 size={17} />
      </div>
      <label className="va-profile-select">
        选择运输架次
        <select
          aria-label="高程分析架次"
          value={sortie?.sortie_id || ''}
          onChange={(e) => setChoice(e.target.value)}
        >
          {plan.sorties.map((s, i) => (
            <option key={s.sortie_id} value={s.sortie_id}>
              {String(i + 1).padStart(2, '0')} · {s.drone_id} ·{' '}
              {s.visits.map((v) => v.site_id).join(' → ')}
            </option>
          ))}
        </select>
      </label>
      {query.isError ? (
        <div className="va-profile-loading">
          <CircleHelp size={18} />
          <span>剖面暂不可用：{(query.error as Error).message}</span>
          <button onClick={() => void query.refetch()}>重试</button>
        </div>
      ) : data ? (
        <>
          <AnalysisChart
            option={option}
            height={300}
            label="沿实际规划航路累计水平距离的DEM采样、模型巡航高程与节点作业高程剖面"
          />
          <div className="va-profile-summary">
            <span>
              航程<strong>{number(data.total_distance_m / 1000, 2)} km</strong>
            </span>
            <span>
              累计爬升<strong>{number(data.total_climb_m)} m</strong>
            </span>
            <span>
              水平能耗<strong>{number(data.horizontal_energy_kwh, 3)} kWh</strong>
            </span>
            <span>
              爬升能耗<strong>{number(data.climb_energy_kwh, 3)} kWh</strong>
            </span>
          </div>
          <p className="va-profile-note">
            按绑定地形与原方案重建，高程基准为
            {data.vertical_datum === 'contest_provided_elevation_reference'
              ? '题设提供的高程参考'
              : data.vertical_datum || '未声明参考'}
            。
            紫线表示分段模型巡航高程，点标表示节点作业高程；采样展示不替代完整净空检查，也不是实飞记录。
          </p>
          <details className="va-data">
            <summary>
              查看航段高度、净空与载荷数据
              <ChevronRight size={12} />
            </summary>
            <p className="va-profile-technical">
              原始高程基准：{data.vertical_datum || '未声明'}。{data.notice}
            </p>
            <button
              className="va-profile-export"
              onClick={() =>
                downloadJson(data, `${data.plan_id}-${data.sortie_id}-flight-profile.json`)
              }
            >
              <ArrowDownToLine size={12} />
              导出本架次原始剖面
            </button>
            <div className="va-table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>航段</th>
                    <th>距离/km</th>
                    <th>载荷/kg</th>
                    <th>巡航高程/m</th>
                    <th>沿途最高地形/m</th>
                    <th>要求净空/m</th>
                    <th>超出要求/m</th>
                    <th>能耗/kWh</th>
                  </tr>
                </thead>
                <tbody>
                  {data.legs.map((l) => (
                    <tr key={l.leg_index}>
                      <td>
                        {l.from_id} → {l.to_id}
                      </td>
                      <td>{number(l.distance_m / 1000, 3)}</td>
                      <td>{number(l.payload_kg, 2)}</td>
                      <td>{number(l.cruise_elevation_m, 2)}</td>
                      <td>{number(l.terrain_maximum_m, 2)}</td>
                      <td>{number(l.clearance_required_m, 2)}</td>
                      <td>{number(l.cruise_clearance_margin_m, 2)}</td>
                      <td>{number(l.energy_kwh, 3)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </details>
        </>
      ) : (
        <div className="va-profile-loading">
          <LoaderCircle className="spin" size={17} />
          读取已保存航路与绑定地形…
        </div>
      )}
    </section>
  )
}

export function VisualAnalysis({
  scenario,
  plan,
  onOpenMap,
  onOpenWorkspace,
}: {
  scenario: Scenario
  plan: Plan | null
  onOpenMap: () => void
  onOpenWorkspace: () => void
}) {
  const page = useRef<HTMLDivElement>(null)
  const [fullscreen, setFullscreen] = useState(false)
  const [overview, setOverview] = useState(true)
  useEffect(() => {
    const sync = () => {
      if (!document.fullscreenElement) setFullscreen(false)
    }
    const keyboard = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setFullscreen(false)
    }
    document.addEventListener('fullscreenchange', sync)
    document.addEventListener('keydown', keyboard)
    return () => {
      document.removeEventListener('fullscreenchange', sync)
      document.removeEventListener('keydown', keyboard)
    }
  }, [])
  const toggleScreen = async () => {
    if (fullscreen) {
      setFullscreen(false)
      if (document.fullscreenElement) await document.exitFullscreen().catch(() => {})
    } else {
      setFullscreen(true)
      await page.current?.requestFullscreen?.().catch(() => {})
    }
  }
  const snapshot = useQuery({
    queryKey: ['snapshot', plan?.snapshot_id],
    queryFn: () => api.getSnapshot(plan!.snapshot_id),
    enabled: !!plan,
    staleTime: Infinity,
  })
  const boundScenario = snapshot.data?.scenario || scenario
  const bindingReady =
    !plan ||
    !!snapshot.data ||
    (plan.scenario_id === scenario.scenario_id &&
      plan.scenario_state_version === scenario.state_version)
  const boundPlan = bindingReady ? plan : null
  const data = useMemo(
    () => visualAnalysisData(boundScenario, boundPlan),
    [boundScenario, boundPlan],
  )
  const scope = new Set(boundPlan?.model_scope || [])
  const verified =
    !!boundPlan?.has_validated_plan &&
    boundPlan.validation.status === 'passed' &&
    boundPlan.data_origin === 'solver'
  const historical =
    !!plan &&
    (plan.scenario_state_version !== scenario.state_version ||
      plan.scenario_id !== scenario.scenario_id)
  const surface = useQuery({
    queryKey: ['terrain-surface', boundScenario.terrain.asset_id, boundScenario.terrain.sha256],
    queryFn: () =>
      api.terrainSurface(boundScenario.terrain.asset_id!, boundScenario.terrain.sha256!),
    enabled:
      boundScenario.terrain.status === 'available' &&
      !!boundScenario.terrain.asset_id &&
      !!boundScenario.terrain.sha256,
    staleTime: Infinity,
    retry: 1,
  })
  const elevationOption = useMemo<EChartsCoreOption>(() => {
    const elevations = surface.data?.elevations_m.flat().filter((v): v is number => v != null) || []
    if (!elevations.length) return {}
    const min = Math.min(...elevations),
      max = Math.max(...elevations),
      step = Math.max(1, (max - min) / 10)
    const bins = Array.from({ length: 10 }, (_, i) => ({
      name: `${number(min + i * step)}–${number(min + (i + 1) * step)}`,
      value: 0,
    }))
    for (const e of elevations) bins[Math.min(9, Math.floor((e - min) / step))].value++
    return {
      tooltip: {
        ...chartTooltip,
        trigger: 'axis',
        valueFormatter: (v: unknown) => formatChartValue(v, 0, ' 个有效采样'),
      },
      grid: { top: 23, left: 50, right: 20, bottom: 60 },
      xAxis: {
        type: 'category',
        data: bins.map((b) => b.name),
        axisLabel: { ...axisStyle, rotate: 30, interval: 1 },
        axisLine: { lineStyle: { color: '#ffffff15' } },
        axisTick: { show: false },
      },
      yAxis: {
        type: 'value',
        name: '采样点数',
        nameTextStyle: axisStyle,
        axisLabel: axisStyle,
        splitLine: splitStyle,
      },
      series: [
        {
          type: 'bar',
          barWidth: '68%',
          data: bins.map((b, i) => ({
            value: b.value,
            itemStyle: {
              color: analysisPalette[Math.floor(i / 2) % analysisPalette.length],
              borderRadius: [3, 3, 0, 0],
              opacity: 0.8,
            },
          })),
        },
      ],
    }
  }, [surface.data])
  const siteHeightOption = useMemo<EChartsCoreOption>(
    () => ({
      tooltip: {
        ...chartTooltip,
        trigger: 'axis',
        valueFormatter: (v: unknown) => formatChartValue(v, 2, ' m'),
      },
      grid: { top: 24, left: 55, right: 20, bottom: 40 },
      xAxis: {
        type: 'category',
        data: [boundScenario.base, ...boundScenario.sites].map((s) => s.id),
        axisLabel: { ...axisStyle, rotate: boundScenario.sites.length > 8 ? 30 : 0 },
        axisLine: { lineStyle: { color: '#ffffff15' } },
        axisTick: { show: false },
      },
      yAxis: {
        type: 'value',
        name: '地面高程 / m',
        nameTextStyle: axisStyle,
        axisLabel: axisStyle,
        splitLine: splitStyle,
      },
      series: [
        {
          type: 'bar',
          barMaxWidth: 23,
          data: [boundScenario.base, ...boundScenario.sites].map((s, i) => ({
            value: s.ground_elevation_m,
            itemStyle: {
              color: i ? '#a59aff' : '#68ddff',
              borderRadius: [3, 3, 0, 0],
              opacity: 0.8,
            },
          })),
        },
      ],
    }),
    [boundScenario],
  )
  const demandOption = useMemo<EChartsCoreOption>(
    () => ({
      tooltip: { ...chartTooltip, trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: {
        bottom: 0,
        itemWidth: 9,
        itemHeight: 7,
        textStyle: axisStyle,
        data: data.cargoKinds.map(namedKind),
      },
      grid: { top: 20, left: 48, right: 20, bottom: 58 },
      xAxis: {
        type: 'category',
        data: data.sites.map((s) => s.id),
        axisLine: { lineStyle: { color: '#ffffff14' } },
        axisTick: { show: false },
        axisLabel: {
          ...axisStyle,
          interval: data.sites.length > 20 ? 'auto' : 0,
          rotate: data.sites.length > 8 ? 30 : 0,
        },
      },
      yAxis: {
        type: 'value',
        name: '需求 / 箱',
        nameTextStyle: axisStyle,
        axisLabel: axisStyle,
        splitLine: splitStyle,
        minInterval: 1,
      },
      series: data.cargoKinds.map((kind, i) => ({
        name: namedKind(kind),
        type: 'bar',
        stack: 'demand',
        barMaxWidth: 29,
        data: data.sites.map((s) => s.quantities[i]),
        emphasis: { focus: 'series' },
        itemStyle: {
          borderRadius: i === data.cargoKinds.length - 1 ? [3, 3, 0, 0] : 0,
          opacity: 0.92,
        },
      })),
    }),
    [data],
  )
  const materialOption = useMemo<EChartsCoreOption>(
    () => ({
      tooltip: { ...chartTooltip, trigger: 'item', formatter: '{b}<br/>{c} 箱 · {d}%' },
      legend: {
        orient: 'vertical',
        right: 18,
        top: 'middle',
        itemWidth: 8,
        itemHeight: 8,
        textStyle: { ...axisStyle, color: '#bac9df', lineHeight: 24 },
      },
      graphic: [
        {
          type: 'text',
          left: '27%',
          top: '42%',
          style: {
            text: `${data.quantity}`,
            fill: '#eff5ff',
            fontSize: 30,
            fontWeight: 500,
            align: 'center',
          },
        },
        {
          type: 'text',
          left: '25%',
          top: '57%',
          style: { text: '需求总箱数', fill: '#879eba', fontSize: 10, align: 'center' },
        },
      ],
      series: [
        {
          type: 'pie',
          radius: ['56%', '76%'],
          center: ['33%', '49%'],
          avoidLabelOverlap: true,
          label: { show: false },
          emphasis: { scaleSize: 5 },
          itemStyle: { borderRadius: 4, borderColor: '#0d1728', borderWidth: 3 },
          data: data.materials.map((m) => ({ name: namedKind(m.kind), value: m.quantity })),
        },
      ],
    }),
    [data],
  )
  const workloadOption = useMemo<EChartsCoreOption>(
    () => ({
      tooltip: {
        ...chartTooltip,
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        valueFormatter: (v: unknown) => formatChartValue(v, 2, ' 分钟'),
      },
      legend: {
        bottom: 0,
        textStyle: axisStyle,
        itemWidth: 9,
        itemHeight: 7,
        data: ['准备与装载', '起飞至返航', '周转至机体释放'],
      },
      grid: { top: 17, left: 64, right: 30, bottom: 54 },
      xAxis: {
        type: 'value',
        name: '分钟',
        nameTextStyle: axisStyle,
        axisLabel: axisStyle,
        splitLine: splitStyle,
      },
      yAxis: {
        type: 'category',
        inverse: true,
        data: data.workloads.map((d) => d.id),
        axisLabel: { ...axisStyle, color: '#bbcae0' },
        axisLine: { show: false },
        axisTick: { show: false },
      },
      series: [
        ['准备与装载', 'prepare'],
        ['起飞至返航', 'flight'],
        ['周转至机体释放', 'turnaround'],
      ].map(([name, key]) => ({
        name,
        type: 'bar',
        stack: 'time',
        barMaxWidth: 15,
        data: data.workloads.map((d) => d[key as 'prepare' | 'flight' | 'turnaround']),
        emphasis: { focus: 'series' },
        itemStyle: { borderRadius: key === 'turnaround' ? [0, 3, 3, 0] : 0 },
      })),
    }),
    [data],
  )
  const flightOption = useMemo<EChartsCoreOption>(
    () => ({
      tooltip: {
        ...chartTooltip,
        trigger: 'item',
        formatter: (p: unknown) => {
          const item = p as { data: { value: number[]; flight: (typeof data.flights)[number] } }
          const f = item.data.flight
          return `架次 ${f.label} · ${chartText(f.drone)}<br/>${number(f.minutes, 2)} 分钟 · ${number(f.energy, 3)} kWh<br/>${f.boxes} 箱 · 返航SOC ${percent(f.soc)}`
        },
      },
      grid: { top: 25, left: 57, right: 30, bottom: 44 },
      xAxis: {
        type: 'value',
        name: '分钟',
        nameTextStyle: axisStyle,
        axisLabel: axisStyle,
        splitLine: splitStyle,
      },
      yAxis: {
        type: 'value',
        name: 'kWh',
        nameTextStyle: axisStyle,
        axisLabel: axisStyle,
        splitLine: splitStyle,
      },
      series: [
        {
          type: 'scatter',
          symbolSize: (value: number[]) => Math.min(35, 10 + Math.sqrt(value[2]) * 4),
          label: {
            show: true,
            position: 'top',
            color: '#aebcdb',
            fontSize: 9,
            formatter: (p: unknown) =>
              (p as { data: { flight: (typeof data.flights)[number] } }).data.flight.label,
          },
          itemStyle: {
            color: '#ac9bff',
            opacity: 0.78,
            borderWidth: 1.5,
            borderColor: '#d5cbff',
            shadowColor: '#9c86ff44',
            shadowBlur: 14,
          },
          data: data.flights
            .filter((f) => f.energy != null)
            .map((f) => ({ value: [f.minutes, f.energy, f.boxes], flight: f })),
        },
      ],
    }),
    [data],
  )
  const socOption = useMemo<EChartsCoreOption>(
    () => ({
      tooltip: {
        ...chartTooltip,
        trigger: 'axis',
        valueFormatter: (v: unknown) => formatChartValue(v, 1, '%'),
      },
      grid: { top: 25, left: 45, right: 20, bottom: 40 },
      xAxis: {
        type: 'category',
        data: data.flights.map((f) => f.label),
        axisLabel: axisStyle,
        axisLine: { lineStyle: { color: '#ffffff14' } },
        axisTick: { show: false },
        name: '架次',
        nameTextStyle: axisStyle,
      },
      yAxis: {
        type: 'value',
        min: 0,
        max: 100,
        axisLabel: { ...axisStyle, formatter: '{value}%' },
        splitLine: splitStyle,
      },
      series: [
        {
          name: '计划返航SOC',
          type: 'bar',
          barMaxWidth: 23,
          data: data.flights.map((f) => ({
            value: f.soc == null ? null : f.soc * 100,
            itemStyle: {
              color:
                f.soc != null && f.soc < boundScenario.policy.min_return_soc
                  ? '#f98fb8'
                  : '#79e3bc',
              borderRadius: [3, 3, 0, 0],
            },
          })),
          markLine: {
            symbol: 'none',
            silent: true,
            lineStyle: { type: 'dashed', color: '#ffca80', width: 1 },
            label: {
              formatter: `要求 ${percent(boundScenario.policy.min_return_soc)}`,
              position: 'insideEndTop',
              color: '#ffca80',
              fontSize: 10,
            },
            data: [{ yAxis: boundScenario.policy.min_return_soc * 100 }],
          },
        },
      ],
    }),
    [data, boundScenario.policy.min_return_soc],
  )

  return (
    <div
      ref={page}
      className={`visual-analysis ${fullscreen ? 'va-fullscreen' : ''} ${fullscreen && overview ? 'va-overview' : ''}`}
    >
      <div className="va-screenbar">
        <span>
          <Layers3 size={13} />
          {fullscreen
            ? `${boundScenario.name} · 场景洞察`
            : '场景洞察 · REAL DATA, CLEAR DECISIONS'}
        </span>
        <div className="va-screen-controls">
          {fullscreen && (
            <>
              <span className={`va-screen-proof ${verified ? 'is-verified' : ''}`}>
                <ShieldCheck size={12} />
                {verified ? '独立检查通过' : '尚无通过证据'} · v{boundScenario.state_version}
              </span>
              <div className="va-view-modes" aria-label="数据大屏展示方式">
                <button aria-pressed={overview} onClick={() => setOverview(true)}>
                  综合看板
                </button>
                <button aria-pressed={!overview} onClick={() => setOverview(false)}>
                  详细分析
                </button>
              </div>
            </>
          )}
          <button aria-pressed={fullscreen} onClick={() => void toggleScreen()}>
            {fullscreen ? <Minimize2 size={13} /> : <Fullscreen size={13} />}
            {fullscreen ? '退出数据大屏' : '进入数据大屏'}
          </button>
        </div>
      </div>
      <header className="va-hero">
        <div className="va-hero-glow va-glow-one" />
        <div className="va-hero-glow va-glow-two" />
        <div className="va-hero-grid" />
        <div className="va-hero-content">
          <div className="va-eyebrow">
            <span />
            YUANHANG · MISSION INTELLIGENCE
          </div>
          <h2>
            让每一条航线，
            <br />
            <em>都有数据支撑。</em>
          </h2>
          <p>
            从山地地形到逐箱需求，从独立机体到能源周转。
            <br className="va-desktop-break" />
            在同一场景中，看见救援任务背后的结构与约束。
          </p>
          <div className="va-hero-actions">
            <button className="va-primary" onClick={onOpenWorkspace}>
              <Orbit size={15} />
              进入调度工作台
              <ArrowRight size={15} />
            </button>
            <button onClick={onOpenMap}>
              <MapPinned size={15} />
              管理地图数据
            </button>
          </div>
        </div>
        <div className="va-orbital" aria-hidden="true">
          <div className="va-orbit va-orbit-a" />
          <div className="va-orbit va-orbit-b" />
          <div className="va-orbit va-orbit-c" />
          <div className="va-orbit-core">
            <Compass size={39} strokeWidth={1} />
          </div>
          <i className="va-orbit-dot" />
          <span className="va-orbit-coordinate">TERRAIN · ENERGY · TIME</span>
        </div>
        <div className="va-hero-stamp">
          <span className="va-signal-dot" />
          本地计算 · 模型内规划辅助
        </div>
      </header>
      <div className="va-context">
        <div>
          <Fingerprint size={14} />
          <span>{boundScenario.name}</span>
          <small>v{boundScenario.state_version}</small>
          {historical && <b>历史方案绑定输入</b>}
        </div>
        <span>{plan ? `方案 ${plan.plan_id.slice(-12)}` : '当前场景 · 尚无方案'}</span>
      </div>
      {!bindingReady && (
        <div className="va-notice">
          <ShieldCheck size={17} />
          <div>
            <strong>{snapshot.isError ? '历史快照读取失败' : '正在读取方案的原始快照'}</strong>
            <p>为避免把旧方案套在当前输入上，结果图暂不展示。当前场景输入统计仍可查看。</p>
          </div>
          {snapshot.isError && <button onClick={() => void snapshot.refetch()}>重试</button>}
        </div>
      )}
      <div className="va-kpis">
        <div>
          <span>
            <MapPinned size={14} />
            需求站点
          </span>
          <strong>
            {number(boundScenario.sites.length)}
            <em>处</em>
          </strong>
          <small>基地另计 · WGS84空间坐标</small>
        </div>
        <div>
          <span>
            <Boxes size={14} />
            保障需求
          </span>
          <strong>
            {number(data.quantity)}
            <em>箱</em>
          </strong>
          <small>实物库存 {number(boundScenario.cargo_items.length)} 箱</small>
        </div>
        <div>
          <span>
            <Layers3 size={14} />
            物资总质量
          </span>
          <strong>
            {number(data.mass, 1)}
            <em>kg</em>
          </strong>
          <small>库存体积 {number(data.volume)} L</small>
        </div>
        <div>
          <span>
            <Plane size={14} />
            可用运输机体
          </span>
          <strong>
            {number(boundScenario.drones.filter((d) => d.status === 'available').length)}
            <em>架</em>
          </strong>
          <small>
            {boundScenario.drone_types.length} 种机型 · {boundScenario.batteries.length} 块电池
          </small>
        </div>
        <div className="va-overview-kpi">
          <span>
            <Clock3 size={14} />
            全部返航
          </span>
          <strong>{duration(boundPlan?.metrics.makespan_s)}</strong>
          <small>
            {boundPlan ? `${boundPlan.sorties.length}个真实运输架次` : '生成真实方案后展示'}
          </small>
        </div>
        <div className="va-overview-kpi">
          <span>
            <Zap size={14} />
            运输预计能耗
          </span>
          <strong>
            {number(boundPlan?.metrics.energy_kwh, 2)}
            <em>kWh</em>
          </strong>
          <small>最低返航SOC {percent(boundPlan?.metrics.min_return_soc)}</small>
        </div>
      </div>
      <div className="va-spatial-row">
        <TerrainScene scenario={boundScenario} plan={boundPlan} onOpenMap={onOpenMap} />
        <aside className="va-mission">
          <div className="va-mission-heading">
            <Activity size={17} />
            <span>方案观测</span>
            <small>PLAN OBSERVATORY</small>
          </div>
          {boundPlan ? (
            <>
              <div className={`va-status ${verified ? 'va-status-verified' : ''}`}>
                <ShieldCheck size={22} />
                <div>
                  <strong>
                    {verified
                      ? '已通过独立模型检查'
                      : statusLabel[boundPlan.validation.status] || '待独立检查'}
                  </strong>
                  <span>
                    {objectiveLabel[boundPlan.objective]} · {statusLabel[boundPlan.solver_status]}
                  </span>
                </div>
              </div>
              <div className="va-mission-metric">
                <span>
                  <Clock3 size={14} />
                  全部返航
                </span>
                <strong>{duration(boundPlan.metrics.makespan_s)}</strong>
                <small>不含电池后续充满时间</small>
              </div>
              <div className="va-mission-metric">
                <span>
                  <Zap size={14} />
                  运输任务预计能耗
                </span>
                <strong>
                  {number(boundPlan.metrics.energy_kwh, 2)}
                  <em>kWh</em>
                </strong>
                <small>
                  {boundPlan.joint_metrics
                    ? `运输 + 中继共 ${number(boundPlan.joint_metrics.joint_energy_kwh, 2)} kWh`
                    : '未包含未配置的中继能耗'}
                </small>
              </div>
              <div className="va-mission-pair">
                <div>
                  <span>运输架次</span>
                  <strong>{boundPlan.sorties.length}</strong>
                </div>
                <div>
                  <span>投入机体 / 电池</span>
                  <strong>
                    {data.workloads.length}
                    <em>/ {data.batteryCount}</em>
                  </strong>
                </div>
              </div>
              <div className="va-verification-strip">
                <div>
                  <strong>{data.passed}</strong>
                  <span>检查通过</span>
                </div>
                <div>
                  <strong>{data.unevaluated}</strong>
                  <span>未评估</span>
                </div>
                <div>
                  <strong>{data.failed}</strong>
                  <span>不通过</span>
                </div>
              </div>
              <p className="va-mission-note">
                指标来自已保存的Plan，不是实飞遥测。有限模型内可行不代表完整问题的全局最优。
              </p>
              <button className="va-mission-link" onClick={onOpenWorkspace}>
                查看任务与双资源时间轴
                <ArrowRight size={13} />
              </button>
            </>
          ) : (
            <div className="va-plan-empty">
              <Orbit size={38} strokeWidth={1.2} />
              <h3>先看输入，再生成方案</h3>
              <p>
                地形、物资与需求现在即可分析。完成一次真实求解后，这里会展示能耗、工作量与返航余量。
              </p>
              <button onClick={onOpenWorkspace}>
                开始真实调度
                <ArrowRight size={14} />
              </button>
            </div>
          )}
        </aside>
      </div>
      <div className="va-section-title">
        <div>
          <span>01 / TERRAIN & ALTITUDE</span>
          <h3>理解山脊如何影响巡航高程与爬升</h3>
        </div>
        <p>地面高程 ≠ 作业高程 ≠ 巡航高程</p>
      </div>
      <div className="va-chart-grid">
        <ChartPanel
          index="G"
          title="基地与服务点地面高程"
          description="读取原始节点地面高程；节点表与栅格高程可能不同，不静默替换。"
          table={
            <table>
              <thead>
                <tr>
                  <th>点位</th>
                  <th>声明地面高程/m</th>
                  <th>经度/°</th>
                  <th>纬度/°</th>
                </tr>
              </thead>
              <tbody>
                {[boundScenario.base, ...boundScenario.sites].map((s) => (
                  <tr key={s.id}>
                    <td>{s.id}</td>
                    <td>{number(s.ground_elevation_m, 2)}</td>
                    <td>{number(s.coordinates[0], 6)}</td>
                    <td>{number(s.coordinates[1], 6)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          }
        >
          <AnalysisChart option={siteHeightOption} label="基地与服务点声明地面高程柱形图" />
        </ChartPanel>
        <ChartPanel
          index="J"
          title="DEM地貌高程分布"
          description="仅统计显示网格的有效高程采样，非完整栅格像元分布，也不是面积占比。"
          table={
            <table>
              <thead>
                <tr>
                  <th>统计口径</th>
                  <th>数值</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>资产完整有效覆盖比例</td>
                  <td>{percent(surface.data?.valid_fraction)}</td>
                </tr>
                <tr>
                  <td>完整资产最低/最高高程</td>
                  <td>
                    {number(surface.data?.min_elevation_m, 2)} /{' '}
                    {number(surface.data?.max_elevation_m, 2)} m
                  </td>
                </tr>
                <tr>
                  <td>显示有效采样数</td>
                  <td>
                    {surface.data?.elevations_m.flat().filter((v) => v != null).length ?? '—'}
                  </td>
                </tr>
                <tr>
                  <td>采样方法</td>
                  <td>端点保留最近像元采样，NoData不填充</td>
                </tr>
              </tbody>
            </table>
          }
        >
          {surface.data ? (
            <AnalysisChart
              option={elevationOption}
              label="真实DEM显示网格中有效高程的数量分布直方图"
            />
          ) : (
            <div className="va-profile-loading">
              <Layers3 size={20} />
              {surface.isFetching ? '读取真实高程网格…' : '导入有效DEM后展示地貌分布'}
            </div>
          )}
        </ChartPanel>
        {boundPlan && <FlightProfilePanel key={boundPlan.plan_id} plan={boundPlan} />}
      </div>
      <div className="va-section-title">
        <div>
          <span>02 / INPUT STRUCTURE</span>
          <h3>救援需求的空间与物资结构</h3>
        </div>
        <p>来自场景输入 · 需求与实际库存分别统计</p>
      </div>
      <div className="va-chart-grid">
        <ChartPanel
          index="A"
          title="站点 × 物资需求"
          description="按需求箱数叠加，识别任务集中位置；不是预测需求。"
          table={
            <table>
              <thead>
                <tr>
                  <th>站点</th>
                  <th>名称</th>
                  {data.cargoKinds.map((c) => (
                    <th key={c}>{namedKind(c)}/箱</th>
                  ))}
                  <th>需求/箱</th>
                  <th>库存/kg</th>
                </tr>
              </thead>
              <tbody>
                {data.sites.map((s) => (
                  <tr key={s.id}>
                    <td>{s.id}</td>
                    <td>{s.name}</td>
                    {s.quantities.map((q, i) => (
                      <td key={i}>{q}</td>
                    ))}
                    <td>{s.quantity}</td>
                    <td>{number(s.mass, 2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          }
        >
          <AnalysisChart option={demandOption} label="各站点分物资需求箱数堆叠图" />
        </ChartPanel>
        <ChartPanel
          index="B"
          title="物资保障构成"
          description="按需求箱数计算占比，不用库存数量代替需求。"
          table={
            <table>
              <thead>
                <tr>
                  <th>物资类型</th>
                  <th>需求/箱</th>
                  <th>库存/箱</th>
                </tr>
              </thead>
              <tbody>
                {data.materials.map((m) => (
                  <tr key={m.kind}>
                    <td>{namedKind(m.kind)}</td>
                    <td>{m.quantity}</td>
                    <td>{m.stock}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          }
        >
          <AnalysisChart option={materialOption} label="分物资需求箱数环形图" />
        </ChartPanel>
      </div>
      <div className="va-section-title">
        <div>
          <span>03 / SCHEDULE SIGNATURE</span>
          <h3>把方案拆解到每架飞机、每次任务</h3>
        </div>
        {boundPlan && (
          <button
            onClick={() =>
              downloadJson(
                {
                  scenario_id: boundScenario.scenario_id,
                  state_version: boundScenario.state_version,
                  plan_id: boundPlan.plan_id,
                  snapshot_id: boundPlan.snapshot_id,
                  input: { sites: data.sites, materials: data.materials },
                  sorties: data.flights,
                  workloads: data.workloads,
                  note: 'Display-only statistics of original input and saved Plan. No new scheduling, energy model or real execution facts.',
                },
                `${boundPlan.plan_id}-visual-analysis.json`,
              )
            }
          >
            <ArrowDownToLine size={14} />
            导出分析数据
          </button>
        )}
      </div>
      {boundPlan ? (
        <div className="va-chart-grid">
          <ChartPanel
            index="C"
            title="机体工作量分解"
            description="累计机体占用时长；起飞至返航包含交接，未把电池充电算作机体占用。"
            table={
              <table>
                <thead>
                  <tr>
                    <th>机体</th>
                    <th>架次</th>
                    <th>准备/min</th>
                    <th>起飞至返航/min</th>
                    <th>周转/min</th>
                    <th>箱数</th>
                  </tr>
                </thead>
                <tbody>
                  {data.workloads.map((d) => (
                    <tr key={d.id}>
                      <td>{d.id}</td>
                      <td>{d.count}</td>
                      <td>{number(d.prepare, 2)}</td>
                      <td>{number(d.flight, 2)}</td>
                      <td>{number(d.turnaround, 2)}</td>
                      <td>{d.boxes}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            }
          >
            <AnalysisChart
              option={workloadOption}
              height={Math.max(270, Math.min(560, data.workloads.length * 28 + 75))}
              label="按机体累计的准备、起飞至返航和周转时长"
            />
          </ChartPanel>
          <ChartPanel
            index="D"
            title="架次时长与能源画像"
            description="每个圆点对应一个真实架次，圆点大小表示承运箱数；不表达相关性因果。"
            table={
              <table>
                <thead>
                  <tr>
                    <th>序号/架次</th>
                    <th>机体</th>
                    <th>时长/min</th>
                    <th>能耗/kWh</th>
                    <th>箱数</th>
                  </tr>
                </thead>
                <tbody>
                  {data.flights.map((f) => (
                    <tr key={f.id}>
                      <td>
                        {f.label}
                        <small>{f.id}</small>
                      </td>
                      <td>{f.drone}</td>
                      <td>{number(f.minutes, 2)}</td>
                      <td>{number(f.energy, 3)}</td>
                      <td>{f.boxes}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            }
          >
            <AnalysisChart
              option={flightOption}
              label="各架次起飞至返航时长与预计能耗散点图，点大小表示箱数"
            />
          </ChartPanel>
          <ChartPanel
            index="E"
            title="返航能源安全余量"
            description="返航SOC直接读取算法结果，虚线来自原快照的最低返航SOC要求。"
            table={
              <table>
                <thead>
                  <tr>
                    <th>序号</th>
                    <th>机体</th>
                    <th>电池</th>
                    <th>返航SOC</th>
                    <th>要求SOC</th>
                  </tr>
                </thead>
                <tbody>
                  {data.flights.map((f) => (
                    <tr key={f.id}>
                      <td>{f.label}</td>
                      <td>{f.drone}</td>
                      <td>{f.battery}</td>
                      <td>{percent(f.soc)}</td>
                      <td>{percent(boundScenario.policy.min_return_soc)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            }
          >
            <AnalysisChart option={socOption} label="各架次计划返航SOC与最低要求" />
          </ChartPanel>
          <section className="va-panel va-routes-panel">
            <div className="va-panel-heading">
              <span className="va-section-index">F</span>
              <div>
                <h3>真实路线索引</h3>
                <p>与Plan中的架次、机体及箱件ID对应，完整航路见地图。</p>
              </div>
              <Workflow size={17} />
            </div>
            <div className="va-route-list">
              {data.flights.map((f) => (
                <div key={f.id}>
                  <span className="va-route-number">{f.label}</span>
                  <div>
                    <strong>
                      {boundScenario.base.id}
                      <ChevronRight size={11} />
                      {f.siteIds.join(' → ')}
                      <ChevronRight size={11} />
                      {boundScenario.base.id}
                    </strong>
                    <small>
                      {f.drone} · {f.battery} · {f.boxes} 箱
                    </small>
                  </div>
                  <span>
                    {number(f.energy, 2)}
                    <small>kWh</small>
                  </span>
                </div>
              ))}
            </div>
            <button className="va-route-open" onClick={onOpenWorkspace}>
              在工作台联动查看航线、任务与甘特
              <ArrowRight size={13} />
            </button>
          </section>
        </div>
      ) : (
        <div className="va-empty-analysis">
          <BarChart3 size={29} />
          <div>
            <h4>调度结果图将在真实计算后解锁</h4>
            <p>这里不会用示例曲线冒充算法输出。输入分析和地形仍可独立查看。</p>
          </div>
          <button onClick={onOpenWorkspace}>
            前往求解
            <ArrowRight size={14} />
          </button>
        </div>
      )}
      <div className="va-section-title va-method-title">
        <div>
          <span>04 / ENGINEERING DIFFERENCE</span>
          <h3>
            <Sparkles size={19} />
            从“给出路线”到“给出可核验的资源计划”
          </h3>
        </div>
        <p>创新设计与本方案证据对应，未评估项保持明确</p>
      </div>
      <div className="va-method-grid">
        <MethodCard
          icon={<Zap size={21} />}
          title="物理与离散调度联合"
          tag={scope.has('energy') && verified ? '本方案能源已检' : '待方案能源检查'}
          supported={scope.has('energy') && verified}
          evidence="可追溯：逐箱载荷 → 分段能源 → 返航SOC"
        >
          把真实箱件、载重变化和SOC/SOH纳入调度。能源曲线由声明物理模型产生，界面只展示结果。
        </MethodCard>
        <MethodCard
          icon={<BatteryCharging size={21} />}
          title="机体与电池独立周转"
          tag={scope.has('battery') && verified ? '本方案资源已检' : '待方案资源检查'}
          supported={scope.has('battery') && verified}
          evidence="可追溯：drone_id / battery_id / 独立释放时刻"
        >
          机体返航释放与电池补能解耦，允许兼容电池复用；可选准备工位与充电端口约束接入同一计划。
        </MethodCard>
        <MethodCard
          icon={<RadioTower size={21} />}
          title="运输与通信协同规划"
          tag={boundPlan?.communication_report && verified ? '本方案联合已检' : '本方案未评估通信'}
          supported={!!boundPlan?.communication_report && verified}
          evidence={
            boundPlan?.communication_report
              ? `本方案：${number(boundPlan.communication_report.coverage_gap_s, 3)} s模型覆盖缺口`
              : '启用通信资源后，生成来源窗口与中继任务'
          }
        >
          在同一地形与无线模型内检查地面直连、两跳接入与回传，给出可重建的连续服务窗口；不替代现场射频认证。
        </MethodCard>
        <MethodCard
          icon={<ShieldCheck size={21} />}
          title="事件重规划与独立证据"
          tag={verified ? '本方案独立检查通过' : '尚无通过证据'}
          supported={verified}
          evidence={
            boundPlan?.parent_plan_id
              ? `存在父方案链：${boundPlan.parent_plan_id.slice(-12)}`
              : '不可变快照 → 保存方案 → 独立重建约束'
          }
        >
          支持尚未执行时的机体/能源退出与紧急插单，保留父子方案和版本链。求解与检查分离，失败不会发布伪方案。
        </MethodCard>
      </div>
      <footer className="va-footnote">
        <ShieldCheck size={15} />
        <p>
          本页展示真实输入与已保存方案的描述统计。未开展风雨不确定性、全程避碰、真机遥测或AI训练验证；不生成虚构性能提升、成功概率或实飞结论。
        </p>
      </footer>
    </div>
  )
}
