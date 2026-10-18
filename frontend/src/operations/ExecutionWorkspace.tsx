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
import {
  ops,
  type Execution,
  type ExecutionEvent,
  type Mission,
  type Repair,
} from '../api/operations'
import { Button, Modal } from '../components/ui'
import { RescueMap } from '../components/RescueMap'
import { ExecutionTimeline } from './ExecutionTimeline'
import { ResourceTimeline } from '../components/ResourceTimeline'
import { CommunicationPanel } from '../components/CommunicationPanel'
import { WeatherEditor } from './WeatherEditor'
import { DeviceStatePanel } from './DeviceStatePanel'
import { DependencyImpactPanel, type ImpactSelection } from './DependencyImpactPanel'
import { ExecutionRouteInspector } from './ExecutionRouteInspector'
import { number, percent } from '../lib/format'
import { clock } from './format'
import { navigate } from './App'
import { FleetOperationsPanel, FleetSummary } from './FleetOperationsPanel'

type Notify = (m: string, error?: boolean) => void
const repairStatus: Record<Repair['status'], string> = {
  computing: '正在计算',
  ready: '待比较采纳',
  no_remaining: '无剩余任务',
  applying: '正在应用',
  failed: '未生成可用调整',
  partially_applied: '部分设备待确认',
  applied: '已采纳',
}
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
  const [view, setView] = useState<'map' | 'fleet'>('map')
  const [routeSelection, setRouteSelection] = useState<ImpactSelection | null>(null)
  const [impactEvent, setImpactEvent] = useState<ExecutionEvent | null>(null)
  const [eventOpen, setEventOpen] = useState(false)
  const [preview, setPreview] = useState<Repair | null>(null)
  const [repairPolicy, setRepairPolicy] = useState<'dependency' | 'full'>('dependency')
  const [candidateSortie, setCandidateSortie] = useState<string | null>(null)
  const [fault, setFault] = useState(false)
  const [communicationOpen, setCommunicationOpen] = useState(false)
  const [timelineOpen, setTimelineOpen] = useState(false)
  const [resolution, setResolution] = useState<ExecutionEvent | null>(null)
  const [resolutionReason, setResolutionReason] = useState('')
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
  const desiredPlan = partPlans.find((p) => p.data?.plan_id === e?.desired_plan_id)?.data
  const desiredSnapshot = useQuery({
    queryKey: ['snapshot', desiredPlan?.snapshot_id],
    queryFn: () => api.getSnapshot(desiredPlan!.snapshot_id),
    enabled: !!desiredPlan,
  })
  const latest = changes.data?.find((c) => c.change_id === preview?.change_id) || preview
  const candidate = useQuery({
    queryKey: ['plan', latest?.candidate_plan_id],
    queryFn: () => api.plan(latest!.candidate_plan_id!),
    enabled: !!latest?.candidate_plan_id,
  })
  const candidateSnapshot = useQuery({
    queryKey: ['snapshot', candidate.data?.snapshot_id],
    queryFn: () => api.getSnapshot(candidate.data!.snapshot_id),
    enabled: !!candidate.data,
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
      const change = await ops.repair(e, repairPolicy)
      setPreview(change)
      refresh()
      notify('调整计算已提交；旧方案和已发生事实保留。')
    } catch (error) {
      notify((error as Error).message, true)
    } finally {
      setBusy(false)
    }
  }
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
  const pendingEvents = (events.data || []).filter(
    (event) => event.status !== 'withdrawn' && !e.applied_event_ids?.includes(event.event_id),
  )
  const routeSets = e.schedule_parts.flatMap((part, i) =>
    partPlans[i].data
      ? [
          {
            plan: partPlans[i].data!,
            sortieIds: part.sortie_ids,
            relayIds:
              part.relay_sortie_ids ||
              (part.role === 'initial'
                ? partPlans[i].data!.relay_sorties?.map((r) => r.relay_sortie_id)
                : []),
          },
        ]
      : [],
  )
  const mapScenario = desiredSnapshot.data
    ? { ...baseScenario, weather: desiredSnapshot.data.scenario.weather }
    : baseScenario
  const selectedRouteKey =
    routeSelection &&
    routeSets.some(
      (s) =>
        s.plan.plan_id === routeSelection.planId && s.sortieIds.includes(routeSelection.sortieId),
    )
      ? routeSelection.planId + ':' + routeSelection.sortieId
      : null
  const selectDevice = (device: string) => {
    setSelected(device)
    setRouteSelection(null)
  }
  const inspectRoute = (value: ImpactSelection) => {
    setRouteSelection(value)
    setSelected(null)
  }
  const selectRoute = (key: string) => {
    const source = routeSets.find((s) => key.startsWith(s.plan.plan_id + ':'))
    const sid = source ? key.slice(source.plan.plan_id.length + 1) : key
    const owner = source || routeSets.find((s) => s.sortieIds.includes(sid))
    if (owner?.plan.sorties.some((r) => r.sortie_id === sid))
      inspectRoute({ planId: owner.plan.plan_id, sortieId: sid })
    else {
      const d = e.telemetry.find(
        (t) => t.sortie_id === sid && (!source || t.active_plan_id === source.plan.plan_id),
      )
      if (d) selectDevice(d.device_id)
    }
  }
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
          disabled={
            e.status === 'completed' || (e.status !== 'running' && pendingEvents.length > 0)
          }
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
          disabled={busy || !['paused', 'ready'].includes(e.status) || pendingEvents.length > 0}
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
        {pendingEvents.length > 0 && (
          <>
            <select
              aria-label="剩余任务修复方法"
              value={repairPolicy}
              onChange={(event) => setRepairPolicy(event.target.value as typeof repairPolicy)}
              disabled={busy || !['paused', 'ready'].includes(e.status)}
            >
              <option value="dependency">优先保留未来安排</option>
              <option value="full">重排全部剩余任务</option>
            </select>
            <Button
              disabled={
                (e.status !== 'paused' && e.status !== 'ready') || !pendingEvents.length || busy
              }
              onClick={() => void repair()}
            >
              <RefreshCw size={14} />
              生成调整
            </Button>
          </>
        )}
        <details className="v3-execution-more">
          <summary>更多操作</summary>
          <div>
            <Button onClick={() => void act(e.connected ? 'disconnect' : 'reconnect')}>
              {e.connected ? <Wifi size={14} /> : <WifiOff size={14} />}
              {e.connected ? '模拟遥测断流' : '恢复遥测'}
            </Button>
            <a
              className="button"
              href={`/api/v1/executions/${id}/export?version=2`}
              target="_blank"
              rel="noreferrer"
            >
              <Download size={14} />
              记录
            </a>
          </div>
        </details>
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
          已记录状态变化 <b>{e.facts_cursor} 条</b>
        </span>
        <span>
          状态版本 <b>{e.revision}</b>
        </span>
        <span>{e.connected ? '模拟遥测正常' : '遥测断流 · 保留最后位置'}</span>
      </div>
      <FleetSummary
        execution={e}
        initialScenario={baseScenario}
        scenario={desiredSnapshot.data?.scenario || baseScenario}
        sources={routeSets}
      />
      <nav className="v3-execution-views" aria-label="执行查看方式">
        <button className={view === 'map' ? 'active' : ''} onClick={() => setView('map')}>
          地图监控与事件
        </button>
        <button className={view === 'fleet' ? 'active' : ''} onClick={() => setView('fleet')}>
          机队运输看板
        </button>
        <span>模拟状态与实际设备数据分开显示</span>
      </nav>
      {view === 'fleet' ? (
        <FleetOperationsPanel
          execution={e}
          scenario={desiredSnapshot.data?.scenario || baseScenario}
          sources={routeSets}
          selected={selected}
          onSelect={(d) => {
            selectDevice(d)
            setView('map')
          }}
        />
      ) : (
        <>
          <div
            className={`v2-map-workspace ${selectedDevice || routeSelection ? 'inspector-open' : ''}`}
          >
            <aside className="v2-object-list">
              <div className="v2-section-bar">
                <h3>机队状态</h3>
              </div>
              <div className="v2-object-scroll">
                {e.telemetry.map((d) => (
                  <button
                    key={d.device_id}
                    onClick={() => selectDevice(d.device_id)}
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
                              not_ready: '尚未就绪',
                              relay_link: '中继建链',
                              relay_service: '中继服务',
                            }[d.phase] || d.phase}
                      </span>
                    </strong>
                    <small>
                      载货 {d.cargo_ids.length} 箱 ·{' '}
                      {!d.battery_id && !d.component_id
                        ? '能源未装机'
                        : d.estimated_soc != null
                          ? `${percent(d.estimated_soc)}（模型估计）`
                          : d.soc != null
                            ? `${percent(d.soc)}（阶段端点）`
                            : '电量未知'}
                    </small>
                    <small>
                      {['climb', 'cruise', 'descent'].includes(d.phase)
                        ? d.cargo_ids.length
                          ? '载货运输中'
                          : '空载返航中'
                        : d.phase === 'handover'
                          ? '正在交接物资'
                          : '等待或地面保障'}
                    </small>
                    {d.availability_reason && <small>{d.availability_reason}</small>}
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
                        {clock(event.time_s)} · 直接{' '}
                        {event.impact?.nodes.filter((n) => n.direct).length ??
                          event.affected_sortie_ids.length}{' '}
                        / 影响合计{' '}
                        {event.impact?.nodes.filter((n) => n.affected).length ??
                          event.propagated_sortie_ids.length}{' '}
                        架次
                      </small>
                      <Button onClick={() => setImpactEvent(event)}>查看影响链与架次</Button>
                      {event.missing_inventory > 0 && (
                        <em>缺少 {event.missing_inventory} 箱库存</em>
                      )}
                      {event.status === 'requires_manual' && <em>涉及已开始承诺，需人工协调</em>}
                      {event.status === 'withdrawn' ? (
                        <small>已核实误报 · {event.resolution_reason}</small>
                      ) : e.applied_event_ids?.includes(event.event_id) ? (
                        <small>已纳入采纳方案</small>
                      ) : (
                        <Button
                          disabled={busy || !['paused', 'ready'].includes(e.status)}
                          onClick={() => {
                            setResolution(event)
                            setResolutionReason('')
                          }}
                        >
                          核实误报
                        </Button>
                      )}
                    </div>
                  ))
                ) : (
                  <p>暂无变化</p>
                )}
              </div>
            </aside>
            <div className="v2-map-main">
              <RescueMap
                viewKey={mission.mission_id}
                onSelectDevice={selectDevice}
                scenario={mapScenario}
                plan={initialPlan.data}
                routeSets={routeSets}
                telemetry={e.telemetry}
                playTime={e.time_s}
                selected={selectedRouteKey}
                onSelect={selectRoute}
              />
            </div>
            {routeSelection && (
              <ExecutionRouteInspector
                key={routeSelection.planId + ':' + routeSelection.sortieId}
                selection={routeSelection}
                execution={e}
                onClose={() => setRouteSelection(null)}
              />
            )}
            {selectedDevice && !routeSelection && (
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
                  {selectedDevice.availability && (
                    <>
                      <dt>未来任务可用性</dt>
                      <dd>
                        {
                          { available: '可用', not_ready: '尚未就绪', unavailable: '不可用' }[
                            selectedDevice.availability
                          ]
                        }
                        <small>{selectedDevice.availability_reason}</small>
                      </dd>
                    </>
                  )}
                  <dt>当前位置</dt>
                  <dd>
                    {selectedDevice.coordinates?.map((n) => n.toFixed(6)).join(', ') || '未知'}
                  </dd>
                  <dt>模型高程</dt>
                  <dd>
                    {selectedDevice.elevation_m === null
                      ? '未知'
                      : number(selectedDevice.elevation_m, 1) + ' m'}
                    <small>{selectedDevice.vertical_datum || '垂直基准未知'}</small>
                  </dd>
                  <dt>电量最近阶段端点</dt>
                  <dd>
                    {selectedDevice.soc === null ? '未计算' : percent(selectedDevice.soc)}
                    <small>
                      {selectedDevice.soc_sample_time_s === null
                        ? ''
                        : clock(selectedDevice.soc_sample_time_s)}
                    </small>
                  </dd>
                  <dt>电量模型估计</dt>
                  <dd>
                    {selectedDevice.estimated_soc == null
                      ? '当前无估计'
                      : percent(selectedDevice.estimated_soc)}
                    <small>阶段功率模型推算 · 非实测</small>
                  </dd>
                  <dt>水平 / 垂直模型速度</dt>
                  <dd>
                    {selectedDevice.model_horizontal_speed_mps == null
                      ? '未知'
                      : number(selectedDevice.model_horizontal_speed_mps, 1)}{' '}
                    /{' '}
                    {selectedDevice.model_vertical_speed_mps == null
                      ? '未知'
                      : number(selectedDevice.model_vertical_speed_mps, 1)}{' '}
                    m/s
                  </dd>
                  <dt>在机箱件</dt>
                  <dd>{selectedDevice.cargo_ids.join(' · ') || '无'}</dd>
                  <dt>能源实体</dt>
                  <dd>
                    {selectedDevice.component_id
                      ? `中继组件 ${selectedDevice.component_id}`
                      : selectedDevice.battery_id || '未装载 / 未观测'}
                  </dd>
                  <dt>当前架次来源</dt>
                  <dd>
                    <code>{selectedDevice.active_plan_id}</code>
                  </dd>
                  <dt>最近模拟时刻</dt>
                  <dd>{clock(selectedDevice.time_s)}</dd>
                </dl>
                {baseScenario.drones.some(
                  (drone) => drone.drone_id === selectedDevice.device_id,
                ) && (
                  <DeviceStatePanel
                    key={selectedDevice.device_id}
                    execution={e}
                    device={selectedDevice.device_id}
                  />
                )}
              </aside>
            )}
          </div>
        </>
      )}
      <div className="v2-execution-bottom">
        <div className="v2-section-bar">
          <h3>当前采用安排 · 历次方案承诺合并核对</h3>
          <Button onClick={() => setTimelineOpen(true)}>查看完整排程</Button>
          {!!initialPlan.data?.communication_report && (
            <Button onClick={() => setCommunicationOpen(true)}>通信与中继时序</Button>
          )}
          <a href={`#/missions/${mission.mission_id}/review`}>
            查看复盘
            <ArrowRight size={13} />
          </a>
        </div>
        {initialPlan.data && (
          <ExecutionTimeline
            sources={routeSets}
            execution={e}
            onSelect={selectRoute}
            selected={selectedRouteKey}
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
      <Modal
        title="生效调度安排"
        description="已保留承诺与后续方案共同构成当前安排，保留各段来源，不改写初始方案。"
        open={timelineOpen}
        onOpenChange={setTimelineOpen}
        wide
      >
        <div className="v2-execution-arrangements">
          <ExecutionTimeline
            sources={routeSets}
            execution={e}
            selected={selectedRouteKey}
            onSelect={(key) => {
              selectRoute(key)
              setTimelineOpen(false)
            }}
          />
        </div>
      </Modal>
      <Modal
        title="事件影响 · 资源依赖与原文安排"
        description={impactEvent?.reason}
        open={!!impactEvent}
        onOpenChange={(open) => !open && setImpactEvent(null)}
        wide
      >
        {impactEvent && (
          <DependencyImpactPanel
            key={impactEvent.event_id}
            event={impactEvent}
            onSelect={(value) => {
              inspectRoute(value)
              setImpactEvent(null)
            }}
          />
        )}
      </Modal>
      <Modal
        title="核实并纠正误报"
        description="仅用于确认此前上报不属实。真实故障仍需保持暂停并人工协调，不能通过撤销事件清除风险。"
        open={!!resolution}
        onOpenChange={(open) => !open && setResolution(null)}
      >
        <div className="v2-create-form">
          <p>{resolution?.reason}</p>
          <label>
            核实依据（至少10个字符）
            <textarea
              value={resolutionReason}
              onChange={(event) => setResolutionReason(event.target.value)}
              maxLength={500}
              rows={3}
            />
          </label>
          <p>将保留原始事件、输入和全部模拟事实，并新增纠错记录。已采纳事件不能撤销。</p>
          <div className="v2-form-actions">
            <Button onClick={() => setResolution(null)}>取消</Button>
            <Button
              variant="primary"
              busy={busy}
              disabled={resolutionReason.trim().length < 10}
              onClick={() => {
                if (!resolution) return
                setBusy(true)
                void ops
                  .resolveEvent(e, resolution.event_id, resolutionReason)
                  .then(() => {
                    setResolution(null)
                    refresh()
                    notify('误报纠正已留档，原事件和事实保留。')
                  })
                  .catch((err: Error) => notify(err.message, true))
                  .finally(() => setBusy(false))
              }}
            >
              记录纠错
            </Button>
          </div>
        </div>
      </Modal>
      {!!changes.data?.length && (
        <div className="v2-change-list">
          {changes.data.map((change, index) => (
            <button key={change.change_id} onClick={() => setPreview(change)}>
              <b>第 {(changes.data?.length || 1) - index} 次调整</b>
              <span>
                {repairStatus[change.status]} · 保留 {change.committed_cargo_ids.length} 箱承诺
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
              调整状态：{repairStatus[latest.status]} · 已保留 {latest.committed_cargo_ids.length}{' '}
              箱 · 未来最早 {clock(latest.future_not_before_s)}
            </div>
            <p>{latest.message}</p>
            {latest.calculation_method && (
              <p className="v2-repair-method">
                实际计算：
                {latest.calculation_method === 'dependency_local'
                  ? '资源依赖局部修复'
                  : '剩余任务全量重算'}
                {latest.repair_policy === 'dependency' &&
                latest.calculation_method === 'full_recompute'
                  ? '（局部不适用或未得到可行结果，已回退）'
                  : ''}
              </p>
            )}
            {latest.diff && (
              <div className="v2-repair-diff">
                <div className="v2-metrics-line">
                  <span>
                    保留原未来架次 <b>{latest.diff.retained_future_sortie_count}</b>
                  </span>
                  <span>
                    改派 <b>{latest.diff.drone_reassigned_quantity}</b> 箱
                  </span>
                  <span>
                    换电池 <b>{latest.diff.battery_reassigned_quantity}</b> 箱
                  </span>
                  <span>
                    时刻变化 <b>{latest.diff.time_shifted_quantity}</b> 箱
                  </span>
                  <span>
                    新增 <b>{latest.diff.new_quantity}</b> 箱
                  </span>
                </div>
                <details>
                  <summary>逐箱核对变化（{latest.diff.rows.length} 箱）</summary>
                  <div className="v2-repair-diff-table">
                    <table className="v2-table">
                      <thead>
                        <tr>
                          <th>箱件 / 变化</th>
                          <th>原机体 / 电池</th>
                          <th>候选机体 / 电池</th>
                          <th>起飞变化 / s</th>
                          <th>交付变化 / s</th>
                          <th>架次</th>
                        </tr>
                      </thead>
                      <tbody>
                        {latest.diff.rows.map((row) => (
                          <tr key={row.cargo_id}>
                            <td>
                              {row.cargo_id}
                              <small>
                                {
                                  { new: '新增', unchanged: '保持原安排', modified: '有变化' }[
                                    row.change_kind
                                  ]
                                }
                              </small>
                            </td>
                            <td>
                              {row.previous_drone_id || '无原安排'}
                              <small>{row.previous_battery_id || '—'}</small>
                            </td>
                            <td>
                              {row.candidate_drone_id}
                              <small>{row.candidate_battery_id}</small>
                            </td>
                            <td>
                              {row.takeoff_delta_s === null
                                ? '无基线'
                                : number(row.takeoff_delta_s, 1)}
                            </td>
                            <td>
                              {row.delivery_delta_s === null
                                ? '无基线'
                                : number(row.delivery_delta_s, 1)}
                            </td>
                            <td>
                              <Button onClick={() => setCandidateSortie(row.candidate_sortie_id)}>
                                核对架次
                              </Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </details>
              </div>
            )}
            {!!latest.applications?.length && (
              <table className="v2-table">
                <thead>
                  <tr>
                    <th>模拟设备</th>
                    <th>上传 / ACK</th>
                    <th>激活状态</th>
                    <th>已启用程序 / 回执</th>
                  </tr>
                </thead>
                <tbody>
                  {latest.applications.map((application) => (
                    <tr key={application.device_id}>
                      <td>{application.device_id}</td>
                      <td>{application.upload_state}</td>
                      <td>{application.activation_state}</td>
                      <td>
                        {application.active_plan_id.slice(-8)}
                        {application.activation_command_id && (
                          <small title={application.activation_command_id}>
                            启用读回 {application.activation_command_id.slice(-8)}
                          </small>
                        )}
                      </td>
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
                    viewKey={mission.mission_id + ':repair'}
                    scenario={candidateSnapshot.data?.scenario || baseScenario}
                    plan={candidate.data}
                    oldPlan={desiredPlan || initialPlan.data}
                    selected={candidateSortie}
                    onSelect={setCandidateSortie}
                  />
                </div>
                {candidateSnapshot.data && (
                  <ResourceTimeline
                    scenario={candidateSnapshot.data.scenario}
                    plan={candidate.data}
                    selected={candidateSortie}
                    onSelect={setCandidateSortie}
                  />
                )}
                {candidateSortie &&
                  candidate.data.sorties
                    .filter((r) => r.sortie_id === candidateSortie)
                    .map((r) => (
                      <p className="v2-repair-sortie" key={r.sortie_id}>
                        {r.drone_id} / {r.battery_id} · {r.visits.map((v) => v.site_id).join(' → ')}
                        <br />
                        箱件：{r.cargo_ids.join(' · ')}
                        <br />
                        起飞 {clock(r.takeoff_s)} · 返航 {clock(r.return_s)}
                      </p>
                    ))}
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
              <Button onClick={() => setPreview(null)}>
                {['applying', 'partially_applied', 'applied'].includes(latest.status)
                  ? '关闭详情'
                  : '暂不采用'}
              </Button>
              <Button disabled={latest.status !== 'failed'} onClick={() => void repair()}>
                继续计算
              </Button>
              <Button
                variant="primary"
                disabled={
                  !['ready', 'no_remaining'].includes(latest.status) ||
                  busy ||
                  (!!latest.candidate_plan_id && (!candidate.data || !candidateSnapshot.data))
                }
                onClick={() => {
                  setBusy(true)
                  void ops
                    .apply(e, latest, fault ? [e.telemetry[0].device_id] : [])
                    .then((next) => {
                      setPreview(next)
                      refresh()
                      notify(
                        next.status === 'applying'
                          ? '调整请求已受理，请查看逐设备应用状态。'
                          : next.message,
                        next.status === 'partially_applied',
                      )
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
    | 'drone.unavailable'
    | 'battery.unavailable'
    | 'demand.added'
    | 'site.unavailable'
    | 'weather.changed'
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
  if (kind === 'weather.changed')
    return (
      <div className="v2-create-form">
        <label>
          变化类型
          <select value={kind} onChange={(e) => setKind(e.target.value as typeof kind)}>
            <option value="drone.unavailable">机体退出未来任务</option>
            <option value="demand.added">新增需求</option>
            <option value="weather.changed">人工气象条件更新</option>
          </select>
        </label>
        <label>
          变化原因
          <textarea value={reason} onChange={(e) => setReason(e.target.value)} />
        </label>
        <WeatherEditor
          purpose="event"
          scenario={scenario}
          notify={notify}
          onSave={async (next) => {
            if (!reason.trim()) throw new Error('请说明气象变化原因。')
            if (!next.weather) throw new Error('执行中更新需提供明确情景，不能移除约束。')
            await ops.event(execution, {
              event_type: 'weather.changed',
              weather: next.weather,
              reason,
            })
            onSaved()
          }}
        />
      </div>
    )
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
          <option value="weather.changed">人工气象条件更新</option>
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
