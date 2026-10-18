import {
  ArrowRight,
  BatteryMedium,
  Boxes,
  CheckCircle2,
  CircleDot,
  Drone,
  Gauge,
  PackageCheck,
  RadioTower,
  Route,
  Timer,
  WifiOff,
} from 'lucide-react'
import type { Plan, Scenario } from '../api/client'
import type { Execution, Telemetry } from '../api/operations'
import { clock, number, percent } from '../lib/format'
import { InfoHint } from './ExperienceUI'
import { executionCargoProgress } from '../lib/execution-progress'

type Source = { plan: Plan; sortieIds: string[]; relayIds?: string[] }
export const phaseText: Record<string, string> = {
  prepare: '准备装载',
  climb: '爬升',
  cruise: '巡航',
  descent: '下降',
  handover: '交接物资',
  turnaround: '基地周转',
  available: '基地待命',
  ready: '尚未开始',
  unavailable: '不可用',
  not_ready: '尚未就绪',
  relay_link: '建立通信',
  relay_service: '通信值守',
  charge: '充电',
  charge_wait: '等待充电',
}
function energyLabel(d: Telemetry) {
  if (!d.battery_id && !d.component_id) return '未装机'
  return d.estimated_soc != null
    ? percent(d.estimated_soc)
    : d.soc != null
      ? percent(d.soc)
      : '未计算'
}
export function FleetSummary({
  execution: e,
  scenario: s,
  initialScenario,
  sources,
}: {
  execution: Execution
  scenario: Scenario
  initialScenario: Scenario
  sources: Source[]
}) {
  const { total, done, loaded, pending } = executionCargoProgress(
    initialScenario.cargo_items.map((c) => c.cargo_id),
    s.cargo_items.map((c) => c.cargo_id),
    e.delivered_cargo_ids,
    e.facts.filter((f) => f.kind === 'loaded').flatMap((f) => f.cargo_ids),
    sources.flatMap((source) =>
      source.plan.sorties
        .filter((r) => source.sortieIds.includes(r.sortie_id))
        .flatMap((r) => r.cargo_ids),
    ),
  )
  const active = e.telemetry.filter((d) =>
    ['climb', 'cruise', 'descent', 'handover', 'relay_link', 'relay_service'].includes(d.phase),
  ).length
  const completion = total ? (100 * done) / total : 0
  return (
    <section className="v3-fleet-summary" aria-label="运输进度摘要">
      <div className="v3-delivery-progress">
        <span>
          <PackageCheck size={17} />
          救援物资交付
        </span>
        <b>
          {done}
          <small>/ {total} 箱</small>
        </b>
        <div className="v3-delivery-track">
          <i style={{ width: `${completion}%` }} />
          <i style={{ width: `${total ? (100 * loaded) / total : 0}%` }} />
        </div>
        <small>
          <span>已交付 {done} 箱</span>
          <span>在机 {loaded} 箱</span>
          <span>待运输 {pending} 箱</span>
        </small>
      </div>
      <div>
        <Drone size={19} />
        <span>
          当前作业机体
          <b>
            {active}
            <small>架</small>
          </b>
        </span>
      </div>
      <div>
        <Boxes size={19} />
        <span>
          当前采用运输安排
          <b>
            {sources.reduce((n, p) => n + p.sortieIds.length, 0)}
            <small>架次</small>
          </b>
        </span>
      </div>
      <div>
        <CircleDot size={19} />
        <span>
          状态来源<b className="v3-fleet-source">{e.connected ? '服务器仿真' : '最后已接收记录'}</b>
          <small>{e.connected ? '数量取自执行账本' : '数量取自账本，位置速度保留最后样本'}</small>
        </span>
      </div>
    </section>
  )
}
export function FleetOperationsPanel({
  execution: e,
  scenario: s,
  sources,
  onSelect,
  selected,
}: {
  execution: Execution
  scenario: Scenario
  sources: Source[]
  onSelect: (s: string) => void
  selected: string | null
}) {
  const names = new Map([s.base, ...s.sites].map((v) => [v.id, v.name || v.id]))
  const all = sources.flatMap((source) =>
    source.plan.sorties
      .filter((r) => source.sortieIds.includes(r.sortie_id))
      .map((r) => ({ plan: source.plan, sortie: r })),
  )
  return (
    <main className="v3-fleet-board">
      <div className="v3-analysis-heading">
        <div>
          <span className="v3-kicker">
            <Drone size={14} />
            每架无人机的运输状态
          </span>
          <h2>机队运行看板</h2>
          <p>交付数量来自执行账本；位置、速度和电量来自服务器仿真模型。点击机体可回地图定位。</p>
        </div>
        <span className="v3-model-status">
          <Timer size={16} />
          {clock(e.time_s)}
          {!e.connected && ' · 遥测断流'}
        </span>
      </div>
      <div className="v2-card v3-fleet-table">
        <table className="v2-table">
          <thead>
            <tr>
              <th>机体 / 当前状态</th>
              <th>当前运输与目的地</th>
              <th>
                电池与剩余电量
                <InfoHint title="电量来源">
                  模拟阶段按模型功率推算的电量标为估计。最近阶段端点另行保留；不等同于实测电池遥测。待命时未装机的电池不会显示成机体实时电量。
                </InfoHint>
              </th>
              <th>
                模型速度 / 高程
                <InfoHint title="速度说明">
                  速度由实际飞行阶段的空间距离与持续时间计算，单位为米每秒；不受播放倍速影响。断流后显示最后样本。
                </InfoHint>
              </th>
              <th>已交付 / 后续任务</th>
              <th>查看</th>
            </tr>
          </thead>
          <tbody>
            {e.telemetry.map((d) => {
              const uses = all
                .filter((x) => x.sortie.drone_id === d.device_id)
                .sort((a, b) => a.sortie.prepare_start_s - b.sortie.prepare_start_s)
              const current = uses.find(
                (x) => x.plan.plan_id === d.active_plan_id && x.sortie.sortie_id === d.sortie_id,
              )
              const next = uses.find(
                (x) =>
                  (x.sortie.prepare_start_s > d.time_s + 1e-6 ||
                    (e.status === 'ready' && x.sortie.prepare_start_s >= d.time_s - 1e-6)) &&
                  !e.facts.some(
                    (f) =>
                      f.plan_id === x.plan.plan_id &&
                      f.sortie_id === x.sortie.sortie_id &&
                      f.kind === 'loaded',
                  ),
              )
              const destination = current?.sortie.visits.find(
                (v) => v.delivery_complete_s > d.time_s,
              )
              const completed = new Set(
                e.facts
                  .filter((f) => f.drone_id === d.device_id && f.kind === 'delivered')
                  .flatMap((f) => f.cargo_ids),
              ).size
              const inflight = ['climb', 'cruise', 'descent'].includes(d.phase),
                isRelay = !!s.communication?.relay_drones.some((r) => r.drone_id === d.device_id)
              const state = isRelay
                ? phaseText[d.phase] || d.phase
                : inflight
                  ? `${d.cargo_ids.length ? '载货运输' : '空载返航'} · ${phaseText[d.phase]}`
                  : phaseText[d.phase] || d.phase
              return (
                <tr key={d.device_id} className={selected === d.device_id ? 'is-selected' : ''}>
                  <td>
                    <div className="v3-fleet-identity">
                      <span className={isRelay ? 'is-relay' : ''}>
                        {isRelay ? <RadioTower size={21} /> : <Drone size={21} />}
                      </span>
                      <div>
                        <b>{d.device_id}</b>
                        <small>{isRelay ? '通信中继' : '运输无人机'}</small>
                      </div>
                    </div>
                    <span className={`v3-fleet-phase ${inflight ? 'is-airborne' : ''}`}>
                      {d.quality === 'stale' ? <WifiOff size={11} /> : <CircleDot size={11} />}{' '}
                      {state}
                      {d.quality === 'stale' ? ' · 失联前' : ''}
                    </span>
                  </td>
                  <td>
                    {isRelay ? (
                      <>
                        <b>{d.phase === 'relay_service' ? '中继服务中' : '通信保障任务'}</b>
                        <small>{d.sortie_id ? '能源组件独立周转' : '等待后续任务'}</small>
                      </>
                    ) : current ? (
                      <>
                        <b>
                          {d.cargo_ids.length} 箱在机 · {number(d.payload_kg ?? 0, 1)} kg
                        </b>
                        <small className="v3-current-destination">
                          <Route size={12} />
                          {destination
                            ? `${d.phase === 'handover' ? '正在交接：' : d.phase === 'prepare' ? '下一站：' : '前往 '}${names.get(destination.site_id) || destination.site_id}`
                            : `返航 ${names.get(s.base.id)}`}
                        </small>
                        <small>
                          {d.phase_end_s != null ? `本阶段预计 ${clock(d.phase_end_s)} 结束` : ''}
                        </small>
                      </>
                    ) : (
                      <>
                        <b>
                          {d.availability === 'unavailable'
                            ? '资源已停用'
                            : d.availability === 'not_ready'
                              ? '等待资源就绪'
                              : '基地待命'}
                        </b>
                        <small>{d.availability_reason || '当前无正在执行的运输架次'}</small>
                      </>
                    )}
                  </td>
                  <td>
                    <b>{d.component_id || d.battery_id || '未装载能源实体'}</b>
                    <div className="v3-fleet-energy">
                      <BatteryMedium size={16} />
                      <strong>{energyLabel(d)}</strong>
                      <small>
                        {d.estimated_soc != null
                          ? '模型估计'
                          : d.battery_id || d.component_id
                            ? '阶段端点'
                            : ''}
                      </small>
                    </div>
                    {(d.battery_id || d.component_id) && d.estimated_soc != null && (
                      <div className="v3-fleet-battery-track">
                        <i
                          style={{
                            width: `${d.estimated_soc * 100}%`,
                            background: d.estimated_soc < 0.25 ? '#c88b55' : undefined,
                          }}
                        />
                      </div>
                    )}
                  </td>
                  <td>
                    <b>
                      <Gauge size={13} />
                      水平{' '}
                      {d.model_horizontal_speed_mps == null
                        ? '未知'
                        : `${number(d.model_horizontal_speed_mps, 1)} m/s`}
                    </b>
                    <small>
                      垂直{' '}
                      {d.model_vertical_speed_mps == null
                        ? '未知'
                        : `${number(d.model_vertical_speed_mps, 1)} m/s`}{' '}
                      · {d.elevation_m == null ? '高程未知' : `${number(d.elevation_m)} m`}
                    </small>
                    <small>
                      {d.quality === 'stale'
                        ? `最后样本 ${clock(d.time_s)}`
                        : '模型速度 · 不是真机测量'}
                    </small>
                  </td>
                  <td>
                    <b>
                      <CheckCircle2 size={13} />
                      已交付 {completed} 箱
                    </b>
                    <small>
                      {next
                        ? `下一架次 ${clock(next.sortie.prepare_start_s)} 准备`
                        : '无后续已安排架次'}
                    </small>
                    {next && (
                      <small>
                        前往 {names.get(next.sortie.visits[0]?.site_id) || '救援点'} ·{' '}
                        {next.sortie.cargo_ids.length} 箱
                      </small>
                    )}
                  </td>
                  <td>
                    <button className="button" onClick={() => onSelect(d.device_id)}>
                      定位
                      <ArrowRight size={13} />
                    </button>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      <p className="v2-chart-note">
        高度采用任务声明的高程参考；水平速度、垂直速度、电量估计均属于当前模型能力。没有能源实体或没有连续模型估计时显示未知或未装机。
      </p>
    </main>
  )
}
