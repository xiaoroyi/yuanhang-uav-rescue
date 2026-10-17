import { useMemo, useState } from 'react'
import { BatteryCharging, Expand, Plane, Shrink } from 'lucide-react'
import type { Plan, Scenario } from '../api/client'
import { clock, colorFor, percent } from '../lib/format'

export function ResourceTimeline({
  scenario,
  plan,
  selected,
  onSelect,
}: {
  scenario: Scenario
  plan: Plan
  selected: string | null
  onSelect: (id: string) => void
}) {
  const [mode, setMode] = useState<'drone' | 'battery'>('drone'),
    [expanded, setExpanded] = useState(false)
  const horizon =
    Math.max(
      ...plan.sorties.map((r) => (mode === 'battery' ? r.battery_released_s : r.drone_released_s)),
    ) * 1.05
  const resources = useMemo(
    () =>
      mode === 'drone'
        ? scenario.drones.map((d) => ({ id: d.drone_id, type: d.type_id }))
        : scenario.batteries.map((b) => ({ id: b.battery_id, type: b.compatible_type_id })),
    [scenario, mode],
  )
  const ticks = Array.from({ length: 7 }, (_, i) => (horizon * i) / 6)
  return (
    <section className={`panel timeline-panel ${expanded ? 'timeline-expanded' : ''}`}>
      <div className="panel-heading">
        <div>
          <h3>
            资源时间轴 <span>RESOURCE TIMELINE</span>
          </h3>
          <p>准备、执行与补能，按实体资源核对</p>
        </div>
        <div className="heading-actions">
          <div className="segmented">
            <button className={mode === 'drone' ? 'active' : ''} onClick={() => setMode('drone')}>
              <Plane size={14} />
              机体
            </button>
            <button
              className={mode === 'battery' ? 'active' : ''}
              onClick={() => setMode('battery')}
            >
              <BatteryCharging size={14} />
              电池
            </button>
          </div>
          <button
            className="icon-button"
            title={expanded ? '收起' : '展开时间轴'}
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? <Shrink size={16} /> : <Expand size={16} />}
          </button>
        </div>
      </div>
      <div className="timeline-scroll">
        <div className="timeline-ruler">
          <div className="timeline-label">资源 / 型号</div>
          <div className="timeline-axis">
            {ticks.map((t, i) => (
              <span key={i} style={{ left: `${(i / 6) * 100}%` }}>
                {clock(t).slice(0, 5)}
              </span>
            ))}
          </div>
        </div>
        {resources.map((resource) => (
          <div key={resource.id} className="timeline-row">
            <div className="timeline-label">
              <i style={{ background: colorFor(resource.id) }} />
              <strong>{resource.id}</strong>
              <small>{resource.type}型</small>
            </div>
            <div className="timeline-track">
              {ticks.map((_, i) => (
                <div className="timeline-gridline" key={i} style={{ left: `${(i / 6) * 100}%` }} />
              ))}
              {plan.sorties
                .filter((r) => (mode === 'drone' ? r.drone_id : r.battery_id) === resource.id)
                .map((r) => (
                  <button
                    key={r.sortie_id}
                    className={`timeline-bar ${selected === r.sortie_id ? 'is-selected' : ''}`}
                    style={{
                      left: `${(r.prepare_start_s / horizon) * 100}%`,
                      width: `${(((mode === 'battery' ? r.battery_released_s : r.drone_released_s) - r.prepare_start_s) / horizon) * 100}%`,
                    }}
                    title={`${resource.id} · ${r.sortie_id}\n起飞 ${clock(r.takeoff_s)} / 返航 ${clock(r.return_s)}\n${r.cargo_ids.length}箱 / ${percent(r.return_soc)}返航SOC`}
                    onClick={() => onSelect(r.sortie_id)}
                  >
                    <span
                      className="bar-prepare"
                      style={{
                        width: `${((r.takeoff_s - r.prepare_start_s) / ((mode === 'battery' ? r.battery_released_s : r.drone_released_s) - r.prepare_start_s)) * 100}%`,
                      }}
                    />
                    <span
                      className="bar-flight"
                      style={{
                        left: `${((r.takeoff_s - r.prepare_start_s) / ((mode === 'battery' ? r.battery_released_s : r.drone_released_s) - r.prepare_start_s)) * 100}%`,
                        width: `${((r.return_s - r.takeoff_s) / ((mode === 'battery' ? r.battery_released_s : r.drone_released_s) - r.prepare_start_s)) * 100}%`,
                        background: colorFor(r.drone_id),
                      }}
                    >
                      {r.cargo_ids.length}箱
                    </span>
                    {mode === 'battery' && (
                      <span
                        className="bar-charge"
                        style={{
                          left: `${((r.return_s - r.prepare_start_s) / (r.battery_released_s - r.prepare_start_s)) * 100}%`,
                        }}
                      />
                    )}
                  </button>
                ))}
            </div>
          </div>
        ))}
      </div>
      <div className="timeline-legend">
        <span>
          <i className="prepare" />
          准备
        </span>
        <span>
          <i className="flight" />
          执行架次
        </span>
        {mode === 'battery' && (
          <span>
            <i className="charge" />
            补能至可复用
          </span>
        )}
        <small>相对场景起点 · 区间左闭右开</small>
      </div>
    </section>
  )
}
