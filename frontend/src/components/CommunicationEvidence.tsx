import { useState } from 'react'
import { ArrowDownToLine, ArrowRight, Plane, RadioTower } from 'lucide-react'
import { downloadJson, type Plan, type Scenario } from '../api/client'
import { clock, number } from '../lib/format'
import { Badge, Button } from './ui'
import './communication-evidence.css'

const preciseTime = (value: number) => {
  const ms = Math.round(value * 1000)
  return `${clock(Math.floor(ms / 1000))}.${String(ms % 1000).padStart(3, '0')}`
}
const PAGE_SIZE = 25

export function CommunicationEvidence({
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
  const [choice, setChoice] = useState({ sortie: '', index: 0, page: 0 })
  const report = plan.communication_report
  const flight = plan.sorties.find((r) => r.sortie_id === selected) || plan.sorties[0]
  if (!report || !flight) return null
  const windows = report.windows
    .filter((w) => w.sortie_id === flight.sortie_id)
    .sort((a, b) => a.start_s - b.start_s || a.end_s - b.end_s || a.source.localeCompare(b.source))
  const current =
    choice.sortie === flight.sortie_id ? choice : { sortie: flight.sortie_id, index: 0, page: 0 }
  const picked = windows[current.index] || windows[0]
  const relay = picked?.relay_sortie_id
    ? (plan.relay_sorties || []).find((r) => r.relay_sortie_id === picked.relay_sortie_id)
    : null
  const span = Math.max(0.001, flight.return_s - flight.takeoff_s)
  const pages = Math.max(1, Math.ceil(windows.length / PAGE_SIZE)),
    page = Math.min(current.page, pages - 1)
  const choose = (index: number) =>
    setChoice({ sortie: flight.sortie_id, index, page: Math.floor(index / PAGE_SIZE) })
  const exportWindow = () =>
    picked &&
    downloadJson(
      {
        plan_id: plan.plan_id,
        snapshot_id: plan.snapshot_id,
        scenario_state_version: plan.scenario_state_version,
        model_id: report.model_id,
        sortie_id: flight.sortie_id,
        window: picked,
        relay_sortie: relay || null,
        gateway_at_base: scenario.base,
        gateway_parameters: scenario.communication?.gateway || null,
        notes:
          'Exact saved Plan window and original bound Scenario input, not a measured radio trace.',
      },
      `${plan.plan_id}-communication-window.json`,
    )
  return (
    <section className="communication-evidence" aria-label="通信来源证据">
      <div className="communication-evidence-heading">
        <div>
          <h4>沿着架次，追溯每个通信窗口</h4>
          <p>点击地图航线或任务卡同步选择；窗口来自该方案的独立覆盖重建。</p>
        </div>
        <label className="field">
          <span>运输架次</span>
          <select
            aria-label="通信来源架次"
            value={flight.sortie_id}
            onChange={(e) => onSelect(e.target.value)}
          >
            {plan.sorties.map((r, i) => (
              <option value={r.sortie_id} key={r.sortie_id}>
                {String(i + 1).padStart(2, '0')} · {r.drone_id} · {r.sortie_id}
              </option>
            ))}
          </select>
        </label>
      </div>
      <div className="coverage-evidence-meta">
        <span>起飞 {preciseTime(flight.takeoff_s)}</span>
        <span>返航 {preciseTime(flight.return_s)}</span>
        <span>{windows.length} 个来源窗口</span>
      </div>
      {windows.length > 0 && windows.length <= 256 && (
        <div className="coverage-source-track" aria-label="通信来源时间轴">
          {windows.map((w, i) => {
            const left = Math.max(0, Math.min(1, (w.start_s - flight.takeoff_s) / span)) * 100
            const width =
              (Math.max(
                0,
                Math.min(flight.return_s, w.end_s) - Math.max(flight.takeoff_s, w.start_s),
              ) /
                span) *
              100
            return (
              <button
                key={`${w.start_s}-${i}`}
                className={`coverage-source-segment source-${w.source} ${picked === w ? 'is-selected' : ''}`}
                style={{ left: `${left}%`, width: width ? `${width}%` : '2px' }}
                aria-label={`通信窗口${i + 1} ${w.source === 'gateway' ? '地面直连' : '中继'}`}
                aria-pressed={picked === w}
                onClick={() => choose(i)}
                title={`${preciseTime(w.start_s)} → ${preciseTime(w.end_s)} · ${number(w.end_s - w.start_s, 3)}秒${width ? '' : ' · 瞬时边界'}`}
              />
            )
          })}
        </div>
      )}
      {windows.length > 256 && (
        <p className="coverage-source-note">窗口较多，请使用下方分页查看完整记录。</p>
      )}
      <div className="coverage-source-legend">
        <span>
          <i className="source-gateway" />
          地面直连
        </span>
        <span>
          <i className="source-relay" />
          中继接入与回传
        </span>
        <small>细线可表示瞬时边界；时间精度以导出JSON为准。</small>
      </div>
      <div className="table-scroll">
        <table className="data-table coverage-window-table" aria-label="架次通信来源窗口">
          <thead>
            <tr>
              <th>窗口 / 来源</th>
              <th>相对起止时刻</th>
              <th>时长 / s</th>
              <th>来源任务</th>
            </tr>
          </thead>
          <tbody>
            {windows.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE).map((w, index) => {
              const i = page * PAGE_SIZE + index,
                r = w.relay_sortie_id
                  ? (plan.relay_sorties || []).find((r) => r.relay_sortie_id === w.relay_sortie_id)
                  : null
              return (
                <tr key={i} className={picked === w ? 'selected-source-window' : ''}>
                  <td>
                    <button
                      className="coverage-window-button"
                      data-source={w.source}
                      aria-pressed={picked === w}
                      onClick={() => choose(i)}
                    >
                      {i + 1} · {w.source === 'gateway' ? '地面直连' : '中继来源'}
                    </button>
                  </td>
                  <td>
                    {preciseTime(w.start_s)} → {preciseTime(w.end_s)}
                  </td>
                  <td>{number(w.end_s - w.start_s, 3)}</td>
                  <td>
                    {w.source === 'gateway'
                      ? `网关 · ${scenario.base.id}`
                      : r
                        ? `${r.drone_id} / ${r.component_id}`
                        : '中继引用未解析'}
                    <small>{w.relay_sortie_id || '基地网关'}</small>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      {windows.length > 0 && (
        <p className="coverage-scroll-hint">窄屏表格可左右滑动，查看时长与来源任务。</p>
      )}
      {!windows.length && (
        <p className="coverage-source-note">
          该架次没有可展示的来源窗口，请查看原始Plan和独立检查报告。
        </p>
      )}
      {pages > 1 && (
        <div className="coverage-source-pagination">
          <span>
            第{page + 1}/{pages}页 · 每页最多{PAGE_SIZE}个窗口
          </span>
          <Button disabled={!page} onClick={() => choose((page - 1) * PAGE_SIZE)}>
            上一页
          </Button>
          <Button disabled={page === pages - 1} onClick={() => choose((page + 1) * PAGE_SIZE)}>
            下一页
          </Button>
        </div>
      )}
      {picked && (
        <div className="coverage-source-detail" aria-label="通信链路来源">
          <div className="coverage-source-detail-heading">
            <strong>
              {preciseTime(picked.start_s)} → {preciseTime(picked.end_s)}
            </strong>
            <Badge tone={picked.source === 'gateway' ? 'teal' : relay ? 'blue' : 'red'}>
              {picked.source === 'gateway' ? '地面直连' : relay ? '中继两跳' : '引用未解析'}
            </Badge>
            <Button onClick={exportWindow}>
              <ArrowDownToLine size={14} />
              导出所选窗口
            </Button>
          </div>
          <div
            className={`coverage-link-chain ${picked.source === 'gateway' ? 'direct-chain' : ''}`}
          >
            <div>
              <Plane size={21} />
              <span>运输接入端</span>
              <strong>{flight.drone_id}</strong>
              <small>{flight.sortie_id}</small>
            </div>
            <ArrowRight size={18} />
            {picked.source === 'relay' && (
              <>
                <div>
                  <RadioTower size={21} />
                  <span>中继接入 / 回传端</span>
                  <strong>{relay?.drone_id || '未解析'}</strong>
                  <small>{relay?.component_id || picked.relay_sortie_id}</small>
                </div>
                <ArrowRight size={18} />
              </>
            )}
            <div>
              <RadioTower size={21} />
              <span>地面网关</span>
              <strong>{scenario.base.id}</strong>
              <small>基地 · {number(scenario.communication?.frequency_mhz)} MHz</small>
            </div>
          </div>
          {relay && (
            <p className="coverage-source-note">
              中继任务 {relay.relay_sortie_id} · 驻点 {relay.station_id} · 服务{' '}
              {preciseTime(relay.service_start_s)} → {preciseTime(relay.service_end_s)} · 离地{' '}
              {number(relay.station_agl_m)}m。接入与回传在同一声明模型内重建。
            </p>
          )}
          <p className="coverage-source-provenance">
            Plan {plan.plan_id} · Snapshot {plan.snapshot_id} · v{plan.scenario_state_version} ·{' '}
            {report.model_id}
          </p>
        </div>
      )}
    </section>
  )
}
