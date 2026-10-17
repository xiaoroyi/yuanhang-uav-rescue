import { useState } from 'react'
import { ArrowDownToLine, BatteryCharging, RadioTower } from 'lucide-react'
import { api, type Plan } from '../api/client'
import { clock, number, percent } from '../lib/format'
import { Badge } from './ui'

export function CommunicationPanel({ plan }: { plan: Plan }) {
  const [mode, setMode] = useState<'drone' | 'energy'>('drone')
  const report = plan.communication_report
  const joint = plan.joint_metrics
  if (!report || !joint) return null
  const relays = plan.relay_sorties || []
  const horizon =
    Math.max(
      1,
      joint.joint_makespan_s,
      ...relays.map((r) => (mode === 'drone' ? r.drone_released_s : r.component_released_s)),
    ) * 1.03
  const resources = [
    ...new Set(relays.map((r) => (mode === 'drone' ? r.drone_id : r.component_id))),
  ]
  return (
    <section className="panel communication-panel" aria-label="通信协同结果">
      <div className="panel-heading">
        <div>
          <h3>
            <RadioTower size={17} />
            通信协同 <span>CONTINUOUS COVERAGE</span>
          </h3>
          <p>连续区间重建 · 同时检查接入与回传 · 累计时长包含并行运输任务</p>
        </div>
        <Badge tone={report.coverage_gap_s === 0 ? 'teal' : 'red'}>
          {report.coverage_gap_s === 0 ? '模型内无通信缺口' : '存在通信缺口'}
        </Badge>
      </div>
      <div className="communication-stats">
        <div>
          <small>联合全部返航</small>
          <strong>{clock(joint.joint_makespan_s)}</strong>
          <span>运输与中继共同完成</span>
        </div>
        <div>
          <small>联合能耗</small>
          <strong>
            {number(joint.joint_energy_kwh, 2)} <em>kWh</em>
          </strong>
          <span>含中继 {number(joint.relay_energy_kwh, 2)} kWh</span>
        </div>
        <div>
          <small>中继保障累计时长</small>
          <strong>{clock(report.relay_s)}</strong>
          <span>直连 {clock(report.direct_s)}</span>
        </div>
        <div>
          <small>中继架次 / 切换窗口</small>
          <strong>
            {joint.relay_sortie_count} <em>/ {report.windows.length}</em>
          </strong>
          <span>全阶段活动 {clock(report.transport_active_s)}</span>
        </div>
      </div>
      {relays.length > 0 && (
        <>
          <div className="relay-timeline-heading">
            <strong>中继资源时间轴</strong>
            <div className="segmented">
              <button className={mode === 'drone' ? 'active' : ''} onClick={() => setMode('drone')}>
                <RadioTower size={14} />
                中继机
              </button>
              <button
                className={mode === 'energy' ? 'active' : ''}
                onClick={() => setMode('energy')}
              >
                <BatteryCharging size={14} />
                能源组件
              </button>
            </div>
          </div>
          <div className="relay-timeline" aria-label="中继资源甘特图">
            <div className="timeline-ruler">
              <div className="timeline-label">实体 / 计划阶段</div>
              <div className="timeline-axis">
                {Array.from({ length: 6 }, (_, i) => (
                  <span key={i} style={{ left: `${i * 20}%` }}>
                    {clock((horizon * i) / 5).slice(0, 5)}
                  </span>
                ))}
              </div>
            </div>
            {resources.map((id) => (
              <div className="timeline-row" key={id}>
                <div className="timeline-label">
                  <i style={{ background: '#8671b3' }} />
                  <strong>{id}</strong>
                </div>
                <div className="timeline-track">
                  {relays
                    .filter((r) => (mode === 'drone' ? r.drone_id : r.component_id) === id)
                    .map((r) => {
                      const end = mode === 'drone' ? r.drone_released_s : r.component_released_s
                      const span = end - r.prepare_start_s
                      return (
                        <div
                          className="relay-timeline-bar"
                          key={r.relay_sortie_id}
                          style={{
                            left: `${(r.prepare_start_s / horizon) * 100}%`,
                            width: `${(span / horizon) * 100}%`,
                          }}
                          title={`${r.relay_sortie_id}\n准备 ${clock(r.prepare_start_s)} / 建链 ${clock(r.service_start_s)}\n服务结束 ${clock(r.service_end_s)} / 返航 ${clock(r.return_s)}\n实体释放 ${clock(end)}`}
                        >
                          <span
                            className="relay-bar-travel"
                            style={{
                              left: 0,
                              width: `${((r.service_start_s - r.prepare_start_s) / span) * 100}%`,
                            }}
                          />
                          <span
                            className="relay-bar-service"
                            style={{
                              left: `${((r.service_start_s - r.prepare_start_s) / span) * 100}%`,
                              width: `${((r.service_end_s - r.service_start_s) / span) * 100}%`,
                            }}
                          >
                            通信服务
                          </span>
                          <span
                            className="relay-bar-travel"
                            style={{
                              left: `${((r.service_end_s - r.prepare_start_s) / span) * 100}%`,
                              width: `${((r.return_s - r.service_end_s) / span) * 100}%`,
                            }}
                          />
                          {mode === 'energy' && (
                            <span
                              className="bar-charge"
                              style={{
                                left: `${((r.charge_start_s - r.prepare_start_s) / span) * 100}%`,
                              }}
                            />
                          )}
                        </div>
                      )
                    })}
                </div>
              </div>
            ))}
          </div>
          <div className="relay-legend">
            <span>
              <i className="relay-service-key" />
              建链后通信服务
            </span>
            <span>
              <i className="relay-travel-key" />
              准备与往返
            </span>
            <span>
              <i className="relay-charge-key" />
              能源补能
            </span>
          </div>
          <div className="table-scroll">
            <table className="data-table">
              <thead>
                <tr>
                  <th>中继机 / 能源组件</th>
                  <th>悬停点</th>
                  <th>离地 / 海拔</th>
                  <th>建链 → 服务结束</th>
                  <th>返航 / 能耗 / SOC</th>
                </tr>
              </thead>
              <tbody>
                {relays.map((r) => (
                  <tr key={r.relay_sortie_id}>
                    <td>
                      <strong>{r.drone_id}</strong>
                      <small>{r.component_id}</small>
                    </td>
                    <td>
                      {r.station_id}
                      <small>{r.station_coordinates.map((v) => number(v, 5)).join(', ')}</small>
                    </td>
                    <td>
                      {number(r.station_agl_m, 0)}m / {number(r.station_elevation_m, 1)}m
                    </td>
                    <td>
                      {clock(r.service_start_s)} → {clock(r.service_end_s)}
                    </td>
                    <td>
                      {clock(r.return_s)}
                      <small>
                        {number(r.energy_kwh, 3)}kWh · {percent(r.return_soc)}
                      </small>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
      <div className="communication-footer">
        <p>
          投影DEM有限几何与链路预算模型；规划覆盖不等于现场无线可靠性。既有工作台指标仍单独统计运输。
        </p>
        <a className="button button-default" href={api.exportUrl(plan.plan_id, 'relay_csv')}>
          <ArrowDownToLine size={14} />
          中继任务CSV
        </a>
      </div>
    </section>
  )
}
