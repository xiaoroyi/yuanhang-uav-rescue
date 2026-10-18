import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Download, Layers3, RadioTower } from 'lucide-react'
import { api, downloadJson, type Plan, type Scenario } from '../api/client'
import { RescueMap } from '../components/RescueMap'
import { Button } from '../components/ui'
import { InfoHint } from './ExperienceUI'
import { clock } from '../lib/format'

export function RadioCoverageExplorer({
  plan,
  scenario,
  selected,
  onSelect,
}: {
  plan: Plan
  scenario: Scenario
  selected: string | null
  onSelect: (id: string) => void
}) {
  const [agl, setAgl] = useState(120),
    [relay, setRelay] = useState(plan.relay_sorties?.[0]?.relay_sortie_id || '')
  const [applied, setApplied] = useState<{ agl: number; relay: string } | null>(null)
  const coverage = useQuery({
    queryKey: ['radio-coverage', plan.plan_id, applied?.agl, applied?.relay],
    queryFn: () => api.radioCoverage(plan.plan_id, applied!.agl, applied!.relay || undefined),
    enabled: !!applied,
    staleTime: Infinity,
    retry: 0,
  })
  const data = coverage.data
  return (
    <section className="v2-card v3-coverage-explorer">
      <div className="v2-section-bar">
        <div>
          <h3>
            <Layers3 size={17} />
            通信覆盖空间分析
            <InfoHint title="空间采样和连续保障的区别">
              网格点回答“指定离地高度、选定中继站位能否连接”。下方方案窗口回答“实际运输航迹在整个时间段是否有连接”。两者用途不同，不能互相代替。
            </InfoHint>
          </h3>
          <p>按真实地形与双向链路预算计算离散点，查看覆盖如何随高度改变。</p>
        </div>
        <div className="v3-coverage-controls">
          <label>
            离地高度
            <select
              aria-label="通信空间分析离地高度"
              value={agl}
              onChange={(e) => setAgl(Number(e.target.value))}
            >
              {[30, 50, 80, 120, 180, 240, 300].map((h) => (
                <option key={h} value={h}>
                  {h} m
                </option>
              ))}
            </select>
          </label>
          <label>
            中继站位
            <select
              aria-label="通信空间分析中继站位"
              value={relay}
              onChange={(e) => setRelay(e.target.value)}
            >
              <option value="">只分析基地直连</option>
              {plan.relay_sorties?.map((r, i) => (
                <option key={r.relay_sortie_id} value={r.relay_sortie_id}>
                  中继第 {i + 1} 架次 · {r.drone_id}
                </option>
              ))}
            </select>
          </label>
          <Button
            variant="primary"
            busy={coverage.isFetching}
            onClick={() => {
              if (applied?.agl === agl && applied.relay === relay) void coverage.refetch()
              else setApplied({ agl, relay })
            }}
          >
            <RadioTower size={14} />
            计算空间覆盖
          </Button>
        </div>
      </div>
      {coverage.error && <p className="v2-inline-error">{coverage.error.message}</p>}
      {!applied ? (
        <div className="v3-coverage-empty">
          <RadioTower size={30} />
          <div>
            <b>选择高度和中继站位，查看空间覆盖</b>
            <p>首次计算需要构建地形通信模型。显示的是离散采样点，不会用完美圆形冒充地形覆盖。</p>
          </div>
        </div>
      ) : (
        <>
          <div className="v3-coverage-map">
            <RescueMap
              scenario={scenario}
              plan={plan}
              selected={selected}
              onSelect={onSelect}
              radioCoverage={data}
            />
            {coverage.isFetching && (
              <div className="v3-coverage-loading">正在计算双向连接与地形遮挡…</div>
            )}
          </div>
          {data && (
            <>
              <div className="v3-coverage-legend">
                {[
                  { id: 'gateway', name: '基地直连', color: '#65bfa5' },
                  { id: 'relay', name: '中继接入＋回传', color: '#d4b26e' },
                  { id: 'uncovered', name: '模型不通', color: '#c97c78' },
                  { id: 'unknown', name: '未知', color: '#93a1ad' },
                ].map((x) => (
                  <span key={x.id}>
                    <i style={{ background: x.color }} />
                    {x.name}
                    <b>{data.points.filter((p) => p.source === x.id).length} 点</b>
                  </span>
                ))}
                <button onClick={() => downloadJson(data, `${plan.plan_id}-radio-coverage.json`)}>
                  <Download size={13} />
                  导出采样
                </button>
              </div>
              <p className="v2-chart-note">
                本图：离地 {data.altitude_agl_m} m · {data.grid_size} × {data.grid_size} 点
                {data.relay_sortie_id
                  ? ` · 所选中继服务期 ${clock(data.relay_service_start_s!)}—${clock(data.relay_service_end_s!)}，回传${data.relay_backhaul_available ? '可用' : '不可用'}`
                  : ' · 仅基地直连'}
                {data.complete ? '' : ' · 计算预算内未评估完的点保留未知'}。{data.notice}
              </p>
            </>
          )}
        </>
      )}
    </section>
  )
}
