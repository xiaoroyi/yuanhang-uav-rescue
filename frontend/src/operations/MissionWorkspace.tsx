import { useEffect, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  Download,
  GitCompareArrows,
  ListChecks,
  LoaderCircle,
  MapPin,
  Play,
  RefreshCw,
} from 'lucide-react'
import { api, type Plan, type Scenario } from '../api/client'
import { ops, type CheckReport, type Mission, type MissionDraft } from '../api/operations'
import { Button, Empty, Modal } from '../components/ui'
import { RescueMap } from '../components/RescueMap'
import { ResourceTimeline } from '../components/ResourceTimeline'
import { ScenarioEditor } from '../pages/ScenarioEditor'
import { TerrainManager } from '../pages/TerrainManager'
import { ZoneManager } from '../pages/ZoneManager'
import { CommunicationManager } from '../pages/CommunicationManager'
import { CompareCenter } from '../pages/CompareCenter'
import { SchedulePage } from '../pages/SchedulePage'
import { ResourceAnalysis } from '../pages/ResourceAnalysis'
import { PartitionAnalysis } from '../pages/PartitionAnalysis'
import { NominalDiagnostics } from '../pages/NominalDiagnostics'
import { number, percent, category } from '../lib/format'
import { clock } from './format'
import { navigate } from './App'
import { ExecutionWorkspace } from './ExecutionWorkspace'
import { StageCharts } from './StageCharts'
import { InputImport } from './InputImport'
import { PlanInsights } from './PlanInsights'
import { CommunicationPanel } from '../components/CommunicationPanel'

type Stage = 'prepare' | 'plans' | 'execute' | 'review'
type Notify = (m: string, e?: boolean) => void
export function MissionWorkspace({
  missionId,
  stage,
  notify,
}: {
  missionId: string
  stage: Stage
  notify: Notify
}) {
  const query = useQueryClient()
  const mission = useQuery({
    queryKey: ['mission', missionId],
    queryFn: () => ops.mission(missionId),
    refetchInterval: 3000,
  })
  const m = mission.data
  const sid = m?.current_scenario_id
  const scene = useQuery({
    queryKey: ['scenario', sid],
    queryFn: () => api.scenario(sid!),
    enabled: !!sid,
  })
  const plans = useQuery({
    queryKey: ['plans', sid],
    queryFn: () => api.plans(sid!),
    enabled: !!sid,
  })
  const jobs = useQuery({
    queryKey: ['jobs', sid],
    queryFn: () => api.jobs(sid!),
    enabled: !!sid,
    refetchInterval: 1500,
  })
  const [planId, setPlanId] = useState(
    () => localStorage.getItem(`yuanhang-mission-plan-${missionId}`) || '',
  )
  const [selected, setSelected] = useState<string | null>(null)
  const [siteId, setSiteId] = useState<string | null>(null)
  const [jobId, setJobId] = useState('')
  const [budget, setBudget] = useState(10)
  const [objective, setObjective] = useState<'time' | 'energy' | 'balanced'>('time')
  const [busy, setBusy] = useState(false)
  const [compareOpen, setCompareOpen] = useState(false)
  const [details, setDetails] = useState(false)
  const [tableOpen, setTableOpen] = useState(false)
  const [bottom, setBottom] = useState<'timeline' | 'profile' | 'none'>('timeline')
  const [list, setList] = useState<'demands' | 'sorties'>('demands')
  const [report, setReport] = useState<CheckReport | null>(null)
  const reports = useQuery({
    queryKey: ['mission-checks', missionId],
    queryFn: () => ops.checks(missionId),
  })
  const currentReport =
    report?.state_version === scene.data?.state_version
      ? report
      : reports.data?.find(
          (r) =>
            r.state_version === scene.data?.state_version && r.check_kind === 'planning_readiness',
        ) || null
  const requestedJob = jobs.data?.find((j) => j.job_id === jobId)
  const activeJobs = jobs.data?.filter((j) => ['queued', 'running'].includes(j.job_state)) || []
  const activeJob =
    activeJobs.find((j) => j.job_state === 'running') || activeJobs[0] || requestedJob
  const progress = useQuery({
    queryKey: ['job-progress', activeJob?.job_id],
    queryFn: () => api.progress(activeJob!.job_id),
    enabled: activeJob?.job_state === 'running',
    refetchInterval: 1000,
  })
  const plan = useQuery({
    queryKey: ['plan', planId],
    queryFn: () => api.plan(planId),
    enabled: !!planId,
  })
  const snapshot = useQuery({
    queryKey: ['snapshot', plan.data?.snapshot_id],
    queryFn: () => api.getSnapshot(plan.data!.snapshot_id),
    enabled: !!plan.data,
  })
  const activeScenario = snapshot.data?.scenario || scene.data
  const refresh = () => {
    void query.invalidateQueries({ queryKey: ['mission', missionId] })
    void query.invalidateQueries({ queryKey: ['missions'] })
    void query.invalidateQueries({ queryKey: ['scenario', sid] })
    void query.invalidateQueries({ queryKey: ['plans', sid] })
    void query.invalidateQueries({ queryKey: ['jobs', sid] })
  }
  useEffect(() => {
    if (!planId && plans.data?.length) setPlanId(m?.active_plan_id || plans.data[0].plan_id)
  }, [planId, plans.data, m?.active_plan_id])
  useEffect(() => {
    if (planId) localStorage.setItem(`yuanhang-mission-plan-${missionId}`, planId)
    setSelected(null)
    setSiteId(null)
  }, [planId, missionId])
  useEffect(() => {
    if (
      requestedJob?.job_state === 'completed' &&
      requestedJob.plan_id &&
      requestedJob.job_id === jobId
    ) {
      setPlanId(requestedJob.plan_id)
      setJobId('')
      void query.invalidateQueries({ queryKey: ['plans', sid] })
    }
  }, [requestedJob, jobId, query, sid])
  const pending = busy || (!!activeJob && ['queued', 'running'].includes(activeJob.job_state))
  const stale =
    !!plan.data && !!scene.data && plan.data.scenario_state_version !== scene.data.state_version
  async function save(s: Scenario) {
    const saved = await api.save(s)
    query.setQueryData(['scenario', sid], saved)
    setReport(null)
    refresh()
  }
  async function solve(compare = false) {
    if (!m || !scene.data) return
    setBusy(true)
    try {
      const check = await ops.check(m)
      setReport(check)
      if (check.blocking_count) {
        navigate(`missions/${missionId}/prepare`)
        notify('请先处理条件检查中的阻断项。', true)
        return
      }
      const snap = await api.snapshot(scene.data)
      const preferences = compare ? (['time', 'energy', 'balanced'] as const) : [objective]
      for (const preference of preferences) {
        const job = await api.solve(snap.snapshot_id, preference, { time_limit_s: budget })
        setJobId(job.job_id)
      }
      refresh()
      notify(compare ? '已基于同一快照提交三种偏好。' : '计算已提交，可刷新恢复。')
    } catch (e) {
      notify((e as Error).message, true)
    } finally {
      setBusy(false)
    }
  }
  if (mission.isPending) return <div className="v2-loading">读取任务…</div>
  if (mission.error || !m)
    return (
      <div className="v2-inline-error">
        {mission.error?.message || '任务不存在'}
        <a href="#/missions">返回任务列表</a>
      </div>
    )
  return (
    <section className={`v2-mission stage-${stage}`}>
      <div className="v2-mission-heading">
        <a href="#/missions" aria-label="返回任务列表">
          <ArrowLeft size={17} />
        </a>
        <h1>{m.name}</h1>
        <span className="v2-status">{m.mode === 'simulation' ? '仿真演练' : '规划辅助'}</span>
        <span className="v2-subtle">
          {scene.data ? `输入 v${scene.data.state_version}` : '未发布草稿'} · {m.site_count} 点 ·{' '}
          {m.cargo_count} 箱
        </span>
      </div>
      <nav className="v2-stage-tabs" aria-label="任务阶段">
        {(
          [
            ['prepare', '任务准备'],
            ['plans', '方案规划'],
            ['execute', '执行跟踪'],
            ['review', '复盘分析'],
          ] as const
        ).map(([id, title], i) => (
          <a
            className={stage === id ? 'active' : ''}
            href={`#/missions/${missionId}/${id}`}
            key={id}
          >
            <i>{i + 1}</i>
            {title}
          </a>
        ))}
      </nav>
      {stage === 'prepare' ? (
        <Preparation
          key={m.mission_id}
          mission={m}
          scenario={scene.data}
          save={save}
          refresh={refresh}
          notify={notify}
          report={currentReport}
          onReport={setReport}
        />
      ) : stage === 'execute' ? (
        <ExecutionWorkspace
          mission={m}
          scenario={activeScenario}
          plan={plan.data}
          notify={notify}
          onRefresh={refresh}
        />
      ) : stage === 'review' ? (
        <Review
          mission={m}
          scenario={activeScenario}
          plan={plan.data}
          selected={selected}
          onSelect={setSelected}
          notify={notify}
          onOpen={(s) =>
            void ops
              .create({
                name: s.name,
                scenario_id: s.scenario_id,
                idempotency_key: crypto.randomUUID(),
              })
              .then((n) => navigate(`missions/${n.mission_id}/plans`))
          }
        />
      ) : !scene.data ? (
        <Empty
          icon={<ListChecks size={24} />}
          title="先完成任务准备"
          description="保存并发布输入，处理阻断项后开始计算。"
          action={
            <Button onClick={() => navigate(`missions/${missionId}/prepare`)}>进入任务准备</Button>
          }
        />
      ) : (
        <>
          <div className="v2-plan-toolbar">
            <select
              aria-label="选择调度方案"
              value={planId}
              onChange={(e) => setPlanId(e.target.value)}
            >
              <option value="">选择方案</option>
              {plans.data?.map((p) => (
                <option value={p.plan_id} key={p.plan_id}>
                  {{ time: '时间优先', energy: '能耗优先', balanced: '时间能耗折中' }[
                    p.objective
                  ] || p.objective}{' '}
                  · {p.plan_id.slice(-6)} · v{p.scenario_state_version}
                </option>
              ))}
            </select>
            <select
              aria-label="计算偏好"
              value={objective}
              onChange={(e) => setObjective(e.target.value as typeof objective)}
            >
              <option value="time">时间优先</option>
              <option value="energy">能耗优先</option>
              <option value="balanced">时间能耗折中</option>
            </select>
            <label className="v2-budget">
              预算
              <select
                aria-label="计算预算"
                value={budget}
                onChange={(e) => setBudget(Number(e.target.value))}
              >
                <option value={5}>5 秒</option>
                <option value={10}>10 秒</option>
                <option value={30}>30 秒</option>
                <option value={60}>60 秒</option>
              </select>
            </label>
            <Button variant="primary" busy={pending} onClick={() => void solve()}>
              <Play size={14} />
              生成方案
            </Button>
            <Button disabled={pending} onClick={() => void solve(true)}>
              比较多种偏好
            </Button>
            <Button disabled={!plan.data} onClick={() => setCompareOpen(true)}>
              <GitCompareArrows size={14} />
              比较
            </Button>
            <Button disabled={!plan.data} onClick={() => setTableOpen(true)}>
              调度明细
            </Button>
            <Button
              disabled={!plan.data || stale || pending}
              onClick={() => {
                if (plan.data && scene.data)
                  void api
                    .confirm(plan.data, scene.data.state_version)
                    .then(() => {
                      refresh()
                      notify('方案已确认并建立预约，可进入执行前检查。')
                    })
                    .catch((e: Error) => notify(e.message, true))
              }}
            >
              <CheckCircle2 size={14} />
              确认方案
            </Button>
          </div>
          {pending && (
            <div className="v2-job-strip">
              <LoaderCircle className="spin" size={15} />
              求解作业 {activeJob?.job_state === 'running' ? '运行中' : '等待计算'} ·{' '}
              {activeJobs.length} 项 · {activeJob?.job_id || '提交中'}
              {activeJob?.job_state === 'running' && progress.data && (
                <span>
                  {progress.data.stage} · {number(progress.data.elapsed_s, 1)}s ·{' '}
                  {progress.data.candidate_count} 候选
                </span>
              )}
              <Button onClick={() => activeJob && void api.cancel(activeJob.job_id).then(refresh)}>
                取消计算
              </Button>
            </div>
          )}
          {activeJob && ['failed', 'canceled'].includes(activeJob.job_state) && (
            <div className="v2-inline-error">
              {activeJob.error?.message || '计算已取消，历史方案保留。'}
            </div>
          )}
          {requestedJob?.job_state === 'completed' && !requestedJob.has_validated_plan && (
            <div className="v2-inline-warning">
              {requestedJob.solver_status === 'INFEASIBLE'
                ? '当前模型已报告不可行，请检查缺口与诊断。'
                : '本次预算内未找到可验证方案，不等于已证明无解。可增加预算或修改条件；下方历史方案保留其原版本。'}
            </div>
          )}
          {stale && (
            <div className="v2-inline-warning">
              此方案对应旧输入；保留查看，确认前请基于新条件重新计算。
            </div>
          )}
          <div className="v2-metrics-line">
            {plan.data ? (
              <>
                <span>
                  计划分配 <b>{plan.data.sorties.reduce((n, r) => n + r.cargo_ids.length, 0)} 箱</b>
                </span>
                <span>
                  最后交付 <b>{clock(plan.data.metrics.last_delivery_s)}</b>
                </span>
                <span>
                  全队返航{' '}
                  <b>
                    {clock(
                      plan.data.joint_metrics?.joint_makespan_s ?? plan.data.metrics.makespan_s,
                    )}
                  </b>
                </span>
                <span>
                  总能耗{' '}
                  <b>
                    {number(
                      plan.data.joint_metrics?.joint_energy_kwh ?? plan.data.metrics.energy_kwh,
                      2,
                    )}{' '}
                    kWh
                  </b>
                </span>
                <button onClick={() => setDetails(!details)}>
                  检查 {plan.data.validation.status === 'passed' ? '通过' : '待检查'}
                </button>
              </>
            ) : (
              <span>尚未生成方案 · 选择偏好并开始计算</span>
            )}
            <a className="v2-push-right" href={`#/missions/${missionId}/execute`}>
              执行前检查
              <ArrowRight size={13} />
            </a>
          </div>
          <div className={`v2-map-workspace ${details ? 'inspector-open' : ''}`}>
            <aside className="v2-object-list">
              <div className="v2-tabs">
                <button
                  className={list === 'demands' ? 'active' : ''}
                  onClick={() => setList('demands')}
                >
                  需求
                </button>
                <button
                  className={list === 'sorties' ? 'active' : ''}
                  onClick={() => setList('sorties')}
                >
                  架次 {plan.data?.sorties.length || 0}
                </button>
              </div>
              <div className="v2-object-scroll">
                {list === 'demands'
                  ? scene.data.sites.map((n) => (
                      <button
                        className={siteId === n.id ? 'active' : ''}
                        key={n.id}
                        onClick={() => {
                          setSiteId(n.id)
                          setSelected(null)
                          setDetails(true)
                        }}
                      >
                        <strong>
                          <MapPin size={14} />
                          {n.name}
                        </strong>
                        <small>
                          {n.id} ·{' '}
                          {scene.data?.demands
                            .filter((d) => d.site_id === n.id)
                            .reduce((v, d) => v + d.required_quantity, 0)}{' '}
                          箱需求
                        </small>
                      </button>
                    ))
                  : plan.data?.sorties.map((r) => (
                      <button
                        className={selected === r.sortie_id ? 'active' : ''}
                        key={r.sortie_id}
                        onClick={() => {
                          setSelected(r.sortie_id)
                          setSiteId(null)
                          setDetails(true)
                        }}
                      >
                        <strong>
                          {r.drone_id}
                          <span>{r.cargo_ids.length} 箱</span>
                        </strong>
                        <small>{r.visits.map((v) => v.site_id).join(' → ')}</small>
                        <small>
                          {clock(r.takeoff_s)} — {clock(r.return_s)}
                        </small>
                      </button>
                    ))}
              </div>
            </aside>
            <div className="v2-map-main">
              <RescueMap
                scenario={activeScenario!}
                plan={plan.data}
                selected={selected}
                selectedSite={siteId}
                onSelect={(id) => {
                  setSelected(id)
                  setSiteId(null)
                  setDetails(true)
                }}
                onSelectSite={(id) => {
                  setSiteId(id)
                  setSelected(null)
                  setDetails(true)
                }}
              />
            </div>
            {details && (
              <ObjectInspector
                scenario={activeScenario!}
                plan={plan.data}
                selected={selected}
                siteId={siteId}
                onClose={() => setDetails(false)}
                onProfile={() => setBottom('profile')}
              />
            )}
          </div>
          <div className={`v2-bottom ${bottom === 'none' ? 'collapsed' : ''}`}>
            <div className="v2-bottom-tabs">
              <button onClick={() => setBottom(bottom === 'timeline' ? 'none' : 'timeline')}>
                机体 / 电池排程
              </button>
              <button disabled={!selected} onClick={() => setBottom('profile')}>
                选中架次分析
              </button>
              <button
                className="v2-push-right"
                onClick={() => setBottom(bottom === 'none' ? 'timeline' : 'none')}
              >
                {bottom === 'none' ? '展开' : '收起'}
              </button>
            </div>
            {plan.data && activeScenario && bottom === 'timeline' ? (
              <ResourceTimeline
                scenario={activeScenario}
                plan={plan.data}
                selected={selected}
                onSelect={(id) => {
                  setSelected(id)
                  setDetails(true)
                  setSiteId(null)
                }}
              />
            ) : plan.data && selected && bottom === 'profile' ? (
              <StageCharts plan={plan.data} selected={selected} />
            ) : (
              bottom !== 'none' && <p className="v2-subtle">生成方案后查看资源安排。</p>
            )}
          </div>
          <Modal title="方案比较" open={compareOpen} onOpenChange={setCompareOpen} wide>
            <CompareCenter
              scenario={scene.data}
              selectedPlanId={planId}
              onOpenPlan={setPlanId}
              onWorkspace={() => setCompareOpen(false)}
            />
          </Modal>
          <Modal title="调度安排与导出" open={tableOpen} onOpenChange={setTableOpen} wide>
            <SchedulePage
              scenario={activeScenario!}
              plan={plan.data || null}
              plans={plans.data || []}
              selected={selected}
              onSelect={setSelected}
              onPlan={setPlanId}
              onMap={() => setTableOpen(false)}
            />
            {plan.data && (
              <a className="button" href={api.exportUrl(plan.data.plan_id, 'json')}>
                <Download size={14} />
                完整方案 JSON
              </a>
            )}
          </Modal>
        </>
      )}
    </section>
  )
}

function ObjectInspector({
  scenario,
  plan,
  selected,
  siteId,
  onClose,
  onProfile,
}: {
  scenario: Scenario
  plan?: Plan
  selected: string | null
  siteId: string | null
  onClose: () => void
  onProfile: () => void
}) {
  const sortie = plan?.sorties.find((r) => r.sortie_id === selected)
  const site = scenario.sites.find((n) => n.id === siteId)
  return (
    <aside className="v2-inspector">
      <div className="v2-section-bar">
        <h2>{sortie ? '架次详情' : site ? '需求点详情' : '检查详情'}</h2>
        <button onClick={onClose} aria-label="关闭详情">
          ×
        </button>
      </div>
      {sortie ? (
        <>
          <h3>
            {sortie.drone_id} · {sortie.sortie_id}
          </h3>
          <dl>
            <dt>运输电池</dt>
            <dd>{sortie.battery_id}</dd>
            <dt>准备 / 起飞</dt>
            <dd>
              {clock(sortie.prepare_start_s)} / {clock(sortie.takeoff_s)}
            </dd>
            <dt>返航 / 机体释放</dt>
            <dd>
              {clock(sortie.return_s)} / {clock(sortie.drone_released_s)}
            </dd>
            <dt>电池补能结束</dt>
            <dd>{clock(sortie.battery_released_s)}</dd>
            <dt>能耗 / 返航 SOC</dt>
            <dd>
              {number(sortie.energy_kwh, 3)} kWh / {percent(sortie.return_soc)}
            </dd>
          </dl>
          <h3>访问顺序</h3>
          {sortie.visits.map((v, i) => (
            <div className="v2-visit" key={v.site_id + i}>
              <b>
                {i + 1}. {scenario.sites.find((s) => s.id === v.site_id)?.name || v.site_id}
              </b>
              <small>
                交接完成 {clock(v.delivery_complete_s)} · {v.cargo_ids.length} 箱
              </small>
              <code>{v.cargo_ids.join(' · ')}</code>
            </div>
          ))}
          <Button onClick={onProfile}>查看高程 / 载荷 / 电量</Button>
        </>
      ) : site ? (
        <>
          <h3>{site.name}</h3>
          <p>
            {site.coordinates.map((x) => x.toFixed(5)).join(', ')} · 高程{' '}
            {site.ground_elevation_m ?? '未知'} m
          </p>
          {scenario.demands
            .filter((d) => d.site_id === site.id)
            .map((d) => {
              const rows =
                plan?.sorties.flatMap((r) =>
                  r.visits.filter((v) => v.site_id === site.id).map((v) => ({ r, v })),
                ) || []
              const boxes = rows
                .flatMap(({ v }) => v.cargo_ids)
                .filter(
                  (id) =>
                    scenario.cargo_items.find((c) => c.cargo_id === id)?.demand_id === d.demand_id,
                )
              return (
                <div className="v2-visit" key={d.demand_id}>
                  <b>
                    {category[d.cargo_type] || d.cargo_type} · {d.required_quantity} 箱
                  </b>
                  <small>
                    库存{' '}
                    {
                      scenario.cargo_items.filter(
                        (c) => c.demand_id === d.demand_id && c.status === 'available',
                      ).length
                    }{' '}
                    · 计划分配 {boxes.length}
                  </small>
                  {rows.map(({ r, v }) => (
                    <small key={r.sortie_id}>
                      {r.drone_id} / {r.sortie_id} · {clock(v.delivery_complete_s)}
                    </small>
                  ))}
                </div>
              )
            })}
        </>
      ) : plan ? (
        <div className="v2-check-list">
          {plan.validation.checks.map((c, i) => (
            <div key={i}>
              <b>
                {c.code} · {c.status}
              </b>
              <p>{c.message}</p>
            </div>
          ))}
        </div>
      ) : (
        <p>点击地图或列表中的对象查看详情。</p>
      )}
    </aside>
  )
}

function Preparation({
  mission,
  scenario,
  save,
  refresh,
  notify,
  report,
  onReport,
}: {
  mission: Mission
  scenario?: Scenario
  save: (s: Scenario) => Promise<void>
  refresh: () => void
  notify: Notify
  report: CheckReport | null
  onReport: (r: CheckReport) => void
}) {
  const query = useQueryClient()
  const [step, setStep] = useState<'region' | 'demand' | 'fleet' | 'checks'>('region')
  const [draft, setDraft] = useState<MissionDraft>(mission.draft)
  const [busy, setBusy] = useState(false)
  const [longitude, setLongitude] = useState(String(mission.draft.base?.coordinates[0] ?? ''))
  const [latitude, setLatitude] = useState(String(mission.draft.base?.coordinates[1] ?? ''))
  const [elevation, setElevation] = useState(String(mission.draft.base?.ground_elevation_m ?? ''))
  const [baseName, setBaseName] = useState(mission.draft.base?.name || '救援基地')
  const live: Scenario | null =
    scenario ||
    (draft.base
      ? {
          ...draft,
          schema_version: '0.1.0-draft',
          scenario_id: 'DRAFT',
          name: mission.name,
          mode: mission.mode,
          state_version: 1,
          data_origin: 'user_input',
          coordinate_system: 'EPSG:4326',
          base: draft.base,
        }
      : null)
  async function persist(next: MissionDraft, publish = false) {
    const result = await ops.draft(mission, next, publish)
    query.setQueryData(['mission', mission.mission_id], result)
    setDraft(result.draft)
    refresh()
    return result
  }
  async function saveEditor(s: Scenario) {
    if (scenario) await save(s)
    else {
      const {
        start_time,
        timezone,
        base,
        sites,
        demands,
        cargo_items,
        drone_types,
        drones,
        batteries,
        terrain,
        policy,
        restricted_zones,
        resource_limits,
        communication,
      } = s
      await persist({
        start_time,
        timezone,
        base,
        sites,
        demands,
        cargo_items,
        drone_types,
        drones,
        batteries,
        terrain,
        policy,
        restricted_zones,
        resource_limits,
        communication,
      })
    }
  }
  async function importDraft(next: MissionDraft) {
    if (scenario) await save({ ...scenario, ...next, base: next.base || scenario.base })
    else await persist(next)
    if (next.base) {
      setLongitude(String(next.base.coordinates[0]))
      setLatitude(String(next.base.coordinates[1]))
      setElevation(String(next.base.ground_elevation_m ?? ''))
      setBaseName(next.base.name)
    }
  }
  async function saveBase() {
    const lon = Number(longitude),
      lat = Number(latitude)
    if (
      !longitude ||
      !latitude ||
      !Number.isFinite(lon) ||
      !Number.isFinite(lat) ||
      Math.abs(lon) > 180 ||
      Math.abs(lat) > 90
    )
      throw new Error('请输入有效的 WGS84 经纬度。')
    const base: Scenario['base'] = {
      id: live?.base.id || 'BASE',
      name: baseName,
      coordinates: [lon, lat],
      ground_elevation_m: elevation.trim() ? Number(elevation) : null,
      available: true,
    }
    if (scenario) await save({ ...scenario, base })
    else await persist({ ...draft, base })
    notify('基地已保存。')
  }
  async function runCheck() {
    setBusy(true)
    try {
      if (!scenario) {
        await persist(draft, true)
        notify('输入已发布，请运行条件检查。')
        return
      }
      const r = await ops.check(mission)
      onReport(r)
    } catch (e) {
      notify((e as Error).message, true)
    } finally {
      setBusy(false)
    }
  }
  const known = scenario || live
  return (
    <div className="v2-prepare">
      <div className="v2-prepare-steps">
        {(
          [
            ['region', '区域基地'],
            ['demand', '需求物资'],
            ['fleet', '机队保障'],
            ['checks', '条件检查'],
          ] as const
        ).map(([id, title], i) => (
          <button className={step === id ? 'active' : ''} onClick={() => setStep(id)} key={id}>
            <i>{i + 1}</i>
            {title}
          </button>
        ))}
      </div>
      <InputImport
        key={step}
        mission={mission}
        group={step === 'fleet' ? 'drones' : step === 'region' ? 'sites' : 'cargo_items'}
        onSave={importDraft}
        notify={notify}
      />
      <div className="v2-prepare-body">
        {step === 'region' ? (
          <div className="v2-region-grid">
            <section className="v2-card v2-region-form">
              <h2>区域与起降基地</h2>
              <label>
                基地名称
                <input value={baseName} onChange={(e) => setBaseName(e.target.value)} />
              </label>
              <label>
                经度 · WGS84
                <input
                  type="number"
                  step="any"
                  value={longitude}
                  onChange={(e) => setLongitude(e.target.value)}
                />
              </label>
              <label>
                纬度 · WGS84
                <input
                  type="number"
                  step="any"
                  value={latitude}
                  onChange={(e) => setLatitude(e.target.value)}
                />
              </label>
              <label>
                地面高程 / m
                <input
                  type="number"
                  step="any"
                  value={elevation}
                  placeholder="未知时留空，计算前需补齐"
                  onChange={(e) => setElevation(e.target.value)}
                />
              </label>
              <Button
                variant="primary"
                onClick={() => void saveBase().catch((e: Error) => notify(e.message, true))}
              >
                保存基地
              </Button>
              <p className="v2-subtle">地图右键可选取坐标。显示底图不等于完成地形净空检查。</p>
              {scenario && (
                <>
                  <TerrainManager
                    scenario={scenario}
                    onAssigned={() => refresh()}
                    notify={notify}
                  />
                  <ZoneManager scenario={scenario} onSave={save} notify={notify} />
                </>
              )}
            </section>
            <div className="v2-prepare-map">
              {known ? (
                <RescueMap
                  scenario={known}
                  selected={null}
                  onSelect={() => {}}
                  onPickCoordinates={([lon, lat]) => {
                    setLongitude(lon.toFixed(6))
                    setLatitude(lat.toFixed(6))
                  }}
                />
              ) : (
                <Empty
                  icon={<MapPin size={28} />}
                  title="设置任务基地"
                  description="输入任意地区的真实坐标和高程。保存后地图会定位本次任务，不使用原题默认中心。"
                />
              )}
            </div>
          </div>
        ) : step === 'checks' ? (
          <section className="v2-card v2-preflight">
            <div className="v2-section-bar">
              <div>
                <h2>条件检查</h2>
                <p>检查输入与必要条件；完整排程由求解后独立核验。</p>
              </div>
              <Button variant="primary" busy={busy} onClick={() => void runCheck()}>
                <RefreshCw size={15} />
                {scenario ? '运行检查' : '发布输入并准备检查'}
              </Button>
            </div>
            {report ? (
              <>
                <div className="v2-check-summary">
                  {report.blocking_count} 项待处理 · {report.warning_count} 项提醒{' '}
                  <small>{new Date(report.checked_at).toLocaleTimeString()}</small>
                </div>
                <div className="v2-check-list">
                  {report.checks.map((c) => (
                    <button
                      className={`check-${c.status}`}
                      key={c.code}
                      onClick={() =>
                        c.action === 'region' || c.action === 'demand' || c.action === 'fleet'
                          ? setStep(c.action)
                          : undefined
                      }
                    >
                      <span>
                        {
                          {
                            passed: '通过',
                            blocked: '阻断',
                            warning: '提醒',
                            unknown: '未知',
                            not_applicable: '未启用',
                          }[c.status]
                        }
                      </span>
                      <div>
                        <b>{c.message}</b>
                        <small>{c.affected_objects?.join(' · ')}</small>
                      </div>
                      <ArrowRight size={15} />
                    </button>
                  ))}
                </div>
              </>
            ) : (
              <Empty
                icon={<ListChecks size={24} />}
                title="尚未运行检查"
                description="先保存当前输入，再检查库存、机队、电池和地图条件。"
              />
            )}
            {scenario && (
              <details>
                <summary>单点能力诊断</summary>
                <NominalForScenario scenario={scenario} />
              </details>
            )}
          </section>
        ) : live ? (
          <>
            <ScenarioEditor
              key={step}
              embedded
              allowedGroups={
                step === 'demand'
                  ? ['sites', 'demands', 'cargo_items']
                  : ['drones', 'batteries', 'drone_types']
              }
              scenario={live}
              onSave={saveEditor}
              onCreated={() => refresh()}
              notify={notify}
              onWorkspace={() => setStep('checks')}
            />
            {step === 'fleet' && scenario && (
              <CommunicationManager scenario={scenario} onSave={save} notify={notify} />
            )}
          </>
        ) : (
          <Empty
            icon={<MapPin size={25} />}
            title="请先设置基地"
            description="基地用于明确库存与设备的位置。"
            action={<Button onClick={() => setStep('region')}>设置区域基地</Button>}
          />
        )}
      </div>
      <footer className="v2-prepare-footer">
        <span>{scenario ? `已发布输入 v${scenario.state_version}` : '草稿可分步保存'}</span>
        <Button
          onClick={() =>
            setStep(step === 'region' ? 'demand' : step === 'demand' ? 'fleet' : 'checks')
          }
        >
          下一步
          <ArrowRight size={14} />
        </Button>
        <Button
          variant="primary"
          disabled={!scenario || !!report?.blocking_count || !report}
          onClick={() => navigate(`missions/${mission.mission_id}/plans`)}
        >
          进入方案计算
          <ArrowRight size={14} />
        </Button>
      </footer>
    </div>
  )
}

function NominalForScenario({ scenario }: { scenario: Scenario }) {
  const snap = useQuery({
    queryKey: ['nominal-snapshot', scenario.scenario_id, scenario.state_version],
    queryFn: () => api.snapshot(scenario),
  })
  return snap.data ? <NominalDiagnostics snapshot={snap.data} /> : <p>准备诊断输入…</p>
}

function Review({
  mission,
  scenario,
  plan,
  selected,
  onSelect,
  notify,
  onOpen,
}: {
  mission: Mission
  scenario?: Scenario
  plan?: Plan
  selected: string | null
  onSelect: (id: string) => void
  notify: Notify
  onOpen: (s: Scenario) => void
}) {
  const [tab, setTab] = useState('summary')
  const analysis = useQuery({
    queryKey: ['execution-analysis', mission.active_execution_id],
    queryFn: () => ops.executionAnalysis(mission.active_execution_id!),
    enabled: !!mission.active_execution_id,
  })
  if (!plan || !scenario)
    return (
      <Empty
        icon={<ListChecks size={25} />}
        title="尚无可分析方案"
        description="先生成方案，再查看计划分析或启动模拟形成复盘。"
        action={
          <Button onClick={() => navigate(`missions/${mission.mission_id}/plans`)}>
            进入方案规划
          </Button>
        }
      />
    )
  return (
    <div className="v2-review">
      <div className="v2-section-bar">
        <div>
          <h2>{mission.active_execution_id ? '演练复盘' : '方案分析'}</h2>
          <p>
            {mission.active_execution_id
              ? '数据来源：独立模拟事实账本'
              : '数据来源：已保存计划，无实际交付'}
          </p>
        </div>
        <a
          className="button"
          href={
            mission.active_execution_id
              ? `/api/v1/executions/${mission.active_execution_id}/export`
              : api.reportUrl(plan.plan_id)
          }
          target="_blank"
          rel="noreferrer"
        >
          <Download size={15} />
          导出{mission.active_execution_id ? '运行记录' : '分析报告'}
        </a>
      </div>
      <div className="v2-tabs">
        {[
          ['summary', '任务结果'],
          ['resources', '资源与增配'],
          ['communication', '通信与分区'],
        ].map(([id, label]) => (
          <button key={id} className={tab === id ? 'active' : ''} onClick={() => setTab(id)}>
            {label}
          </button>
        ))}
      </div>
      {tab === 'summary' ? (
        <>
          <div className="v2-metrics-line">
            <span>
              计划分配{' '}
              <b>
                {analysis.data?.allocated_quantity ??
                  plan.sorties.reduce((n, r) => n + r.cargo_ids.length, 0)}{' '}
                箱
              </b>
            </span>
            <span>
              模拟交付 <b>{analysis.data?.delivered_quantity ?? '尚未运行'}</b>
            </span>
            <span>
              尚未交付 <b>{analysis.data?.unserved_quantity ?? '—'}</b>
            </span>
            <span>
              事件 <b>{analysis.data?.event_count ?? 0}</b>
            </span>
            <span>
              调整记录 <b>{analysis.data?.change_count ?? 0}</b>
            </span>
          </div>
          <ResourceTimeline
            scenario={scenario}
            plan={plan}
            selected={selected}
            onSelect={onSelect}
          />
          <StageCharts plan={plan} selected={selected || plan.sorties[0]?.sortie_id || ''} />
          <PlanInsights plan={plan} />
          {analysis.data && (
            <section className="v2-card">
              <h3>模拟交付记录</h3>
              <table className="v2-table">
                <thead>
                  <tr>
                    <th>时间</th>
                    <th>机体</th>
                    <th>架次</th>
                    <th>箱件</th>
                  </tr>
                </thead>
                <tbody>
                  {analysis.data.delivery_rows.map((f) => (
                    <tr key={f.fact_id}>
                      <td>{clock(f.time_s)}</td>
                      <td>{f.drone_id}</td>
                      <td>{f.sortie_id}</td>
                      <td>{f.cargo_ids.join(' · ')}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          )}
        </>
      ) : tab === 'resources' ? (
        <ResourceAnalysis
          scenario={scenario}
          plan={plan}
          stale={false}
          notify={notify}
          onOpen={onOpen}
        />
      ) : (
        <>
          <CommunicationPanel
            plan={plan}
            scenario={scenario}
            selected={selected}
            onSelect={onSelect}
          />
          <PartitionAnalysis
            plan={plan}
            onConfigure={() => navigate(`missions/${mission.mission_id}/prepare`)}
          />
        </>
      )}
    </div>
  )
}
