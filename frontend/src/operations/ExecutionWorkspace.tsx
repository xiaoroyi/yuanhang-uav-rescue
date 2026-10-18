import { useState } from 'react'
import { useQueries, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  ArrowRight,
  CheckCircle2,
  Download,
  Pause,
  Play,
  Plus,
  RefreshCw,
  Wifi,
  WifiOff,
} from 'lucide-react'
import { api, type Plan, type Scenario } from '../api/client'
import { ops, type Execution, type Mission, type Repair } from '../api/operations'
import { Button, Modal } from '../components/ui'
import { RescueMap } from '../components/RescueMap'
import { ResourceTimeline } from '../components/ResourceTimeline'
import { CommunicationPanel } from '../components/CommunicationPanel'
import { number, percent } from '../lib/format'
import { clock } from './format'
import { navigate } from './App'

type Notify = (m: string, error?: boolean) => void
export function ExecutionWorkspace({
  mission,
  scenario,
  plan,
  notify,
  onRefresh,
}: {
  mission: Mission
  scenario?: Scenario
  plan?: Plan
  notify: Notify
  onRefresh: () => void
}) {
  const query = useQueryClient()
  const [id, setId] = useState(mission.active_execution_id || '')
  const [busy, setBusy] = useState(false)
  const [selected, setSelected] = useState<string | null>(null)
  const [eventOpen, setEventOpen] = useState(false)
  const [preview, setPreview] = useState<Repair | null>(null)
  const [fault, setFault] = useState(false)
  const [communicationOpen, setCommunicationOpen] = useState(false)
  const execution = useQuery({
    queryKey: ['execution', id],
    queryFn: () => ops.execution(id),
    enabled: !!id,
    refetchInterval: 1000,
  })
  const e = execution.data
  const events = useQuery({
    queryKey: ['execution-events', id],
    queryFn: () => ops.events(id),
    enabled: !!id,
    refetchInterval: 2000,
  })
  const changes = useQuery({
    queryKey: ['execution-changes', id],
    queryFn: () => ops.changes(id),
    enabled: !!id,
    refetchInterval: 1500,
  })
  const initialPlan = useQuery({
    queryKey: ['plan', e?.initial_plan_id],
    queryFn: () => api.plan(e!.initial_plan_id),
    enabled: !!e,
  })
  const snap = useQuery({
    queryKey: ['snapshot', initialPlan.data?.snapshot_id],
    queryFn: () => api.getSnapshot(initialPlan.data!.snapshot_id),
    enabled: !!initialPlan.data,
  })
  const partPlans = useQueries({
    queries: (e?.schedule_parts || []).map((part) => ({
      queryKey: ['plan', part.plan_id],
      queryFn: () => api.plan(part.plan_id),
    })),
  })
  const candidate = useQuery({
    queryKey: ['plan', preview?.candidate_plan_id],
    queryFn: () => api.plan(preview!.candidate_plan_id!),
    enabled: !!preview?.candidate_plan_id,
  })
  const baseScenario = snap.data?.scenario || scenario
  const refresh = () => {
    void query.invalidateQueries({ queryKey: ['execution', id] })
    void query.invalidateQueries({ queryKey: ['execution-events', id] })
    void query.invalidateQueries({ queryKey: ['execution-changes', id] })
    onRefresh()
  }
  async function create() {
    if (!mission.active_plan_id) {
      notify('请先在方案页确认当前方案。', true)
      return
    }
    setBusy(true)
    try {
      const report = await ops.check(mission, 'simulation_readiness', mission.active_plan_id)
      if (report.blocking_count) {
        notify(
          report.checks.find((c) => c.status === 'blocked')?.message || '执行前检查未通过。',
          true,
        )
        return
      }
      const created = await ops.start(mission, mission.active_plan_id)
      setId(created.execution_id)
      onRefresh()
      notify('模拟实例已创建；点击开始演练推进服务器时钟。')
    } catch (error) {
      notify((error as Error).message, true)
    } finally {
      setBusy(false)
    }
  }
  async function act(
    action: Parameters<typeof ops.action>[1],
    options?: Parameters<typeof ops.action>[2],
  ) {
    if (!e) return
    setBusy(true)
    try {
      const next = await ops.action(e, action, options)
      query.setQueryData(['execution', id], next)
      refresh()
    } catch (error) {
      notify((error as Error).message, true)
    } finally {
      setBusy(false)
    }
  }
  async function repair() {
    if (!e) return
    setBusy(true)
    try {
      const change = await ops.repair(e)
      setPreview(change)
      refresh()
      notify('调整计算已提交；旧方案和已发生事实保留。')
    } catch (error) {
      notify((error as Error).message, true)
    } finally {
      setBusy(false)
    }
  }
  const latest = changes.data?.find((c) => c.change_id === preview?.change_id) || preview
  if (!id)
    return (
      <div className="v2-execution-start">
        <div className="v2-card">
          <h2>执行前检查</h2>
          <p>运行类型：服务器业务仿真。确认方案、创建实例和开始演练分别操作。</p>
          <dl>
            <dt>当前确认方案</dt>
            <dd>{mission.active_plan_id || '尚未确认'}</dd>
            <dt>参与机体</dt>
            <dd>{scenario?.drones.length ?? '—'} 架</dd>
            <dt>真实设备</dt>
            <dd>未连接 · 本次不会下发设备</dd>
          </dl>
          <Button
            variant="primary"
            busy={busy}
            disabled={!mission.active_plan_id}
            onClick={() => void create()}
          >
            <CheckCircle2 size={16} />
            检查并创建模拟实例
          </Button>
          {!mission.active_plan_id && (
            <Button onClick={() => navigate(`missions/${mission.mission_id}/plans`)}>
              返回确认方案
              <ArrowRight size={14} />
            </Button>
          )}
        </div>
        <div className="v2-execution-map">
          {scenario && (
            <RescueMap scenario={scenario} plan={plan} selected={null} onSelect={() => {}} />
          )}
        </div>
      </div>
    )
  if (execution.error)
    return (
      <div className="v2-inline-error">
        {execution.error.message}
        <Button onClick={refresh}>重新连接</Button>
      </div>
    )
  if (!e || !baseScenario) return <p className="v2-loading">恢复服务器演练状态…</p>
  const selectedDevice = e.telemetry.find((x) => x.device_id === selected)
  const routeSets = e.schedule_parts.flatMap((part, i) =>
    partPlans[i].data ? [{ plan: partPlans[i].data!, sortieIds: part.sortie_ids }] : [],
  )
  return (
    <>
      <div className="v2-plan-toolbar">
        <b className="v2-sim-label">仿真演练</b>
        <span className="v2-sim-clock">{clock(e.time_s)}</span>
        <span className="v2-status">
          {
            { ready: '尚未开始', running: '运行中', paused: '已暂停', completed: '已结束' }[
              e.status
            ]
          }
        </span>
        <Button
          variant="primary"
          busy={busy}
          disabled={e.status === 'completed'}
          onClick={() =>
            void act(e.status === 'running' ? 'pause' : e.status === 'ready' ? 'start' : 'resume')
          }
        >
          {e.status === 'running' ? <Pause size={15} /> : <Play size={15} />}
          {e.status === 'running' ? '暂停演练' : e.status === 'ready' ? '开始演练' : '继续演练'}
        </Button>
        <select
          aria-label="模拟倍速"
          value={e.speed}
          onChange={(event) => void act('speed', { speed: Number(event.target.value) })}
        >
          {[1, 5, 20, 60, 100].map((s) => (
            <option value={s} key={s}>
              {s}×
            </option>
          ))}
        </select>
        <Button
          disabled={busy || !['paused', 'ready'].includes(e.status)}
          onClick={() => {
            const next = routeSets
              .flatMap((part) =>
                part.plan.sorties
                  .filter((r) => part.sortieIds.includes(r.sortie_id))
                  .flatMap((r) => [
                    r.takeoff_s,
                    ...r.visits.map((v) => v.delivery_complete_s),
                    r.return_s,
                    r.battery_released_s,
                  ]),
              )
              .filter((t) => t > e.time_s + 1)
            void act('advance', { target_time_s: Math.min(...next) + 1 })
          }}
        >
          推进至下一事件
        </Button>
        <Button
          disabled={e.status !== 'paused' && e.status !== 'ready'}
          onClick={() => setEventOpen(true)}
        >
          <Plus size={14} />
          上报变化
        </Button>
        <Button
          disabled={(e.status !== 'paused' && e.status !== 'ready') || !events.data?.length || busy}
          onClick={() => void repair()}
        >
          <RefreshCw size={14} />
          生成调整
        </Button>
        <Button onClick={() => void act(e.connected ? 'disconnect' : 'reconnect')}>
          {e.connected ? <Wifi size={14} /> : <WifiOff size={14} />}
          {e.connected ? '模拟遥测断流' : '恢复遥测'}
        </Button>
        <a
          className="button"
          href={`/api/v1/executions/${id}/export`}
          target="_blank"
          rel="noreferrer"
        >
          <Download size={14} />
          记录
        </a>
      </div>
      <div className="v2-metrics-line">
        <span>
          已分配{' '}
          <b>
            {routeSets.reduce(
              (n, set) =>
                n +
                set.plan.sorties
                  .filter((r) => set.sortieIds.includes(r.sortie_id))
                  .reduce((v, r) => v + r.cargo_ids.length, 0),
              0,
            )}{' '}
            箱
          </b>
        </span>
        <span>
          模拟已交付 <b>{e.delivered_cargo_ids.length} 箱</b>
        </span>
        <span>
          事实游标 <b>{e.facts_cursor}</b>
        </span>
        <span>
          状态版本 <b>{e.revision}</b>
        </span>
        <span>{e.connected ? '模拟遥测正常' : '遥测断流 · 保留最后位置'}</span>
      </div>
      <div className={`v2-map-workspace ${selectedDevice ? 'inspector-open' : ''}`}>
        <aside className="v2-object-list">
          <div className="v2-section-bar">
            <h3>机队状态</h3>
          </div>
          <div className="v2-object-scroll">
            {e.telemetry.map((d) => (
              <button
                key={d.device_id}
                onClick={() => setSelected(d.device_id)}
                className={selected === d.device_id ? 'active' : ''}
              >
                <strong>
                  {d.device_id}
                  <span>
                    {d.quality === 'stale'
                      ? '失联'
                      : {
                          prepare: '装载',
                          climb: '爬升',
                          cruise: '巡航',
                          descent: '下降',
                          handover: '交接',
                          turnaround: '周转',
                          available: '待命',
                          ready: '待开始',
                          unavailable: '停用',
                          relay_link: '中继建链',
                          relay_service: '中继服务',
                        }[d.phase] || d.phase}
                  </span>
                </strong>
                <small>
                  载货 {d.cargo_ids.length} 箱 · {d.soc === null ? 'SOC 待观测' : percent(d.soc)}
                </small>
                <small>{d.sortie_id || '尚无当前架次'}</small>
              </button>
            ))}
          </div>
          <div className="v2-section-bar">
            <h3>变化队列</h3>
          </div>
          <div className="v2-event-list">
            {events.data?.length ? (
              events.data.map((event) => (
                <div key={event.event_id}>
                  <b>{event.reason}</b>
                  <small>
                    {clock(event.time_s)} · 直接 {event.affected_sortie_ids.length} / 传播{' '}
                    {event.propagated_sortie_ids.length} 架次
                  </small>
                  {event.missing_inventory > 0 && <em>缺少 {event.missing_inventory} 箱库存</em>}
                  {event.status === 'requires_manual' && <em>涉及已开始承诺，需人工协调</em>}
                </div>
              ))
            ) : (
              <p>暂无变化</p>
            )}
          </div>
        </aside>
        <div className="v2-map-main">
          <RescueMap
            scenario={baseScenario}
            plan={initialPlan.data}
            routeSets={routeSets}
            telemetry={e.telemetry}
            playTime={e.time_s}
            selected={null}
            onSelect={(value) => {
              const sid = value.includes(':') ? value.split(':').at(-1) : value
              const d = e.telemetry.find((t) => t.sortie_id === sid)
              if (d) setSelected(d.device_id)
            }}
          />
        </div>
        {selectedDevice && (
          <aside className="v2-inspector">
            <div className="v2-section-bar">
              <h2>{selectedDevice.device_id}</h2>
              <button onClick={() => setSelected(null)} aria-label="关闭机体详情">
                ×
              </button>
            </div>
            <dl>
              <dt>状态来源</dt>
              <dd>{selectedDevice.quality === 'stale' ? '失联前模拟记录' : '服务器模拟'}</dd>
              <dt>当前位置</dt>
              <dd>{selectedDevice.coordinates?.map((n) => n.toFixed(6)).join(', ') || '未知'}</dd>
              <dt>模型高程</dt>
              <dd>
                {selectedDevice.elevation_m === null
                  ? '未知'
                  : number(selectedDevice.elevation_m, 1) + ' m'}
                <small>{selectedDevice.vertical_datum || '垂直基准未知'}</small>
              </dd>
              <dt>SOC 最近端点</dt>
              <dd>
                {selectedDevice.soc === null ? '未计算' : percent(selectedDevice.soc)}
                <small>
                  {selectedDevice.soc_sample_time_s === null
                    ? ''
                    : clock(selectedDevice.soc_sample_time_s)}
                </small>
              </dd>
              <dt>在机箱件</dt>
              <dd>{selectedDevice.cargo_ids.join(' · ') || '无'}</dd>
              <dt>能源实体</dt>
              <dd>
                {selectedDevice.component_id
                  ? `中继组件 ${selectedDevice.component_id}`
                  : selectedDevice.battery_id || '未装载 / 未观测'}
              </dd>
              <dt>采用计划</dt>
              <dd>
                <code>{selectedDevice.active_plan_id}</code>
              </dd>
              <dt>最近模拟时刻</dt>
              <dd>{clock(selectedDevice.time_s)}</dd>
            </dl>
          </aside>
        )}
      </div>
      <div className="v2-execution-bottom">
        <div className="v2-section-bar">
          <h3>初始计划排程 · 用于与模拟事实核对</h3>
          {!!initialPlan.data?.communication_report && (
            <Button onClick={() => setCommunicationOpen(true)}>通信与中继时序</Button>
          )}
          <a href={`#/missions/${mission.mission_id}/review`}>
            查看复盘
            <ArrowRight size={13} />
          </a>
        </div>
        {initialPlan.data && (
          <ResourceTimeline
            scenario={baseScenario}
            plan={initialPlan.data}
            selected={null}
            onSelect={(sid) => {
              const d = e.telemetry.find((x) => x.sortie_id === sid)
              if (d) setSelected(d.device_id)
            }}
          />
        )}
      </div>
      <Modal
        title="通信与中继时序"
        open={communicationOpen}
        onOpenChange={setCommunicationOpen}
        wide
      >
        {initialPlan.data && (
          <CommunicationPanel
            plan={initialPlan.data}
            scenario={baseScenario}
            selected={null}
            onSelect={(sid) => {
              const d = e.telemetry.find((t) => t.sortie_id === sid)
              if (d) setSelected(d.device_id)
            }}
          />
        )}
      </Modal>
      {!!changes.data?.length && (
        <div className="v2-change-list">
          {changes.data.map((change) => (
            <button key={change.change_id} onClick={() => setPreview(change)}>
              <b>调整 {change.change_id.slice(-6)}</b>
              <span>
                {change.status} · 保留 {change.committed_cargo_ids.length} 箱承诺
              </span>
              <ArrowRight size={14} />
            </button>
          ))}
        </div>
      )}
      <Modal title="执行中变化" open={eventOpen} onOpenChange={setEventOpen}>
        <EventForm
          execution={e}
          scenario={baseScenario}
          notify={notify}
          onSaved={() => {
            setEventOpen(false)
            refresh()
          }}
        />
      </Modal>
      <Modal
        title="调整差异与采纳"
        description="先核对保留承诺和未来变化，再确认模拟应用。原方案与已交付事实保持不变。"
        open={!!preview}
        onOpenChange={(v) => {
          if (!v) setPreview(null)
        }}
        wide
      >
        {latest && (
          <div className="v2-repair-preview">
            <div className="v2-check-summary">
              状态 {latest.status} · 已保留 {latest.committed_cargo_ids.length} 箱 · 未来最早{' '}
              {clock(latest.future_not_before_s)}
            </div>
            <p>{latest.message}</p>
            {!!latest.applications?.length && (
              <table className="v2-table">
                <thead>
                  <tr>
                    <th>模拟设备</th>
                    <th>上传 / ACK</th>
                    <th>激活状态</th>
                    <th>采用计划</th>
                  </tr>
                </thead>
                <tbody>
                  {latest.applications.map((application) => (
                    <tr key={application.device_id}>
                      <td>{application.device_id}</td>
                      <td>{application.upload_state}</td>
                      <td>{application.activation_state}</td>
                      <td>{application.active_plan_id.slice(-8)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
            {candidate.data && (
              <>
                <div className="v2-metrics-line">
                  <span>剩余架次 {candidate.data.sorties.length}</span>
                  <span>最后返航 {clock(candidate.data.metrics.makespan_s)}</span>
                  <span>剩余能耗 {number(candidate.data.metrics.energy_kwh, 2)} kWh</span>
                </div>
                <div className="v2-repair-map">
                  <RescueMap
                    scenario={baseScenario}
                    plan={candidate.data}
                    oldPlan={initialPlan.data}
                    selected={null}
                    onSelect={() => {}}
                  />
                </div>
              </>
            )}
            <details>
              <summary>已完成 / 在途承诺箱件</summary>
              <p>{latest.committed_cargo_ids.join(' · ')}</p>
            </details>
            <label className="v2-fault-choice">
              <input type="checkbox" checked={fault} onChange={(v) => setFault(v.target.checked)} />
              注入一台模拟设备 ACK 超时（验证部分应用状态）
            </label>
            <div className="v2-form-actions">
              <Button onClick={() => setPreview(null)}>暂不采用</Button>
              <Button disabled={latest.status !== 'failed'} onClick={() => void repair()}>
                继续计算
              </Button>
              <Button
                variant="primary"
                disabled={!['ready', 'no_remaining'].includes(latest.status) || busy}
                onClick={() => {
                  setBusy(true)
                  void ops
                    .apply(e, latest, fault ? [e.telemetry[0].device_id] : [])
                    .then((next) => {
                      setPreview(next)
                      refresh()
                      notify(next.message, next.status === 'partially_applied')
                    })
                    .catch((error: Error) => notify(error.message, true))
                    .finally(() => setBusy(false))
                }}
              >
                确认采纳模拟调整
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </>
  )
}

function EventForm({
  execution,
  scenario,
  notify,
  onSaved,
}: {
  execution: Execution
  scenario: Scenario
  notify: Notify
  onSaved: () => void
}) {
  const [kind, setKind] = useState<
    'drone.unavailable' | 'battery.unavailable' | 'demand.added' | 'site.unavailable'
  >('drone.unavailable')
  const [object, setObject] = useState('')
  const [reason, setReason] = useState('')
  const [site, setSite] = useState(scenario.sites[0]?.id || '')
  const [quantity, setQuantity] = useState(1)
  const [inventory, setInventory] = useState(1)
  const [mass, setMass] = useState(1)
  const [volume, setVolume] = useState(1)
  const [busy, setBusy] = useState(false)
  async function submit() {
    setBusy(true)
    try {
      if (!reason.trim()) throw new Error('请说明变化原因。')
      if (kind === 'demand.added') {
        const did = 'URG-' + crypto.randomUUID().slice(0, 8)
        await ops.event(execution, {
          event_type: kind,
          reason,
          demand: {
            demand_id: did,
            site_id: site,
            cargo_type: 'MED',
            required_quantity: quantity,
            priority: 1,
            expected_deadline_s: null,
            hard_deadline_s: null,
            mandatory: true,
          },
          cargo_items: Array.from({ length: inventory }, (_, i) => ({
            cargo_id: `${did}-BOX-${i + 1}`,
            demand_id: did,
            type: 'MED',
            mass_kg: mass,
            volume_l: volume,
            status: 'available',
            location_id: scenario.base.id,
          })),
        })
      } else {
        if (!object) throw new Error('请选择变化对象。')
        await ops.event(execution, { event_type: kind, object_id: object, reason })
      }
      onSaved()
    } catch (error) {
      notify((error as Error).message, true)
    } finally {
      setBusy(false)
    }
  }
  const objects =
    kind === 'drone.unavailable'
      ? scenario.drones.map((d) => ({
          id: d.drone_id,
          text: `${d.drone_id} · ${execution.telemetry.find((t) => t.device_id === d.drone_id)?.phase || '待命'}`,
        }))
      : kind === 'battery.unavailable'
        ? scenario.batteries.map((b) => ({ id: b.battery_id, text: b.battery_id }))
        : scenario.sites.map((s) => ({ id: s.id, text: s.name }))
  return (
    <form
      className="v2-create-form"
      onSubmit={(e) => {
        e.preventDefault()
        void submit()
      }}
    >
      <label>
        变化类型
        <select
          value={kind}
          onChange={(e) => {
            setKind(e.target.value as typeof kind)
            setObject('')
          }}
        >
          <option value="drone.unavailable">机体退出未来任务</option>
          <option value="battery.unavailable">电池退出未来任务</option>
          <option value="demand.added">已有点位新增医疗需求</option>
          <option value="site.unavailable">落点关闭</option>
        </select>
      </label>
      {kind === 'demand.added' ? (
        <>
          <label>
            需求点
            <select value={site} onChange={(e) => setSite(e.target.value)}>
              {scenario.sites.map((s) => (
                <option value={s.id} key={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            新增需求 / 箱
            <input
              type="number"
              min={1}
              max={200}
              value={quantity}
              onChange={(e) => setQuantity(Number(e.target.value))}
            />
          </label>
          <label>
            实际新增库存 / 箱
            <input
              type="number"
              min={0}
              max={200}
              value={inventory}
              onChange={(e) => setInventory(Number(e.target.value))}
            />
          </label>
          <div className="v2-field-pair">
            <label>
              单箱质量 / kg
              <input
                type="number"
                min={0.01}
                step="any"
                value={mass}
                onChange={(e) => setMass(Number(e.target.value))}
              />
            </label>
            <label>
              单箱体积 / L
              <input
                type="number"
                min={0.01}
                step="any"
                value={volume}
                onChange={(e) => setVolume(Number(e.target.value))}
              />
            </label>
          </div>
          <p>需求不会自动增加物资；库存不足将保留缺口，不能发布完整保障方案。</p>
        </>
      ) : (
        <label>
          目标对象
          <select value={object} onChange={(e) => setObject(e.target.value)}>
            <option value="">选择对象</option>
            {objects.map((o) => (
              <option value={o.id} key={o.id}>
                {o.text}
              </option>
            ))}
          </select>
        </label>
      )}
      <label>
        变化原因
        <textarea
          rows={2}
          value={reason}
          maxLength={500}
          onChange={(e) => setReason(e.target.value)}
        />
      </label>
      <p className="v2-subtle">
        已开始装载、在飞或交接的架次不能瞬间撤销；影响这些承诺时将要求人工协调。
      </p>
      <Button variant="primary" busy={busy} type="submit">
        记录事件并分析影响
      </Button>
    </form>
  )
}
