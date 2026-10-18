import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useQueries, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Activity,
  ArrowDownToLine,
  ArrowRight,
  BatteryCharging,
  Box,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  CircleHelp,
  Clock3,
  Copy,
  Database,
  FileDown,
  Globe2,
  Layers,
  Leaf,
  LoaderCircle,
  Map as MapIcon,
  MapPin,
  Menu,
  MoreHorizontal,
  Package,
  Pause,
  Drone,
  Play,
  Plus,
  RefreshCw,
  RadioTower,
  Search,
  Scale,
  Settings2,
  ShieldCheck,
  ShieldAlert,
  TriangleAlert,
  Zap,
  BarChart3,
  BookOpen,
  GitCompareArrows,
  History,
  Moon,
  Sun,
  Sparkles,
} from 'lucide-react'
import { api, ApiError, downloadJson, type Scenario, type Event } from './api/client'
import { Badge, Button, Empty, Modal, Toasts, type ToastMessage } from './components/ui'
import {
  policyOf,
  policyLabel,
  strategyDescription,
  strategyMetrics,
  equalityExplanation,
} from './lib/strategies'
import { StrategyFacts } from './components/StrategyFacts'
import { RescueMap } from './components/RescueMap'
import { ResourceTimeline } from './components/ResourceTimeline'
import { CommunicationPanel } from './components/CommunicationPanel'
import { ScenarioEditor } from './pages/ScenarioEditor'
import { ResourceAnalysis } from './pages/ResourceAnalysis'
import { PartitionAnalysis } from './pages/PartitionAnalysis'
import { UrgentDemandForm, type UrgentPayload } from './pages/UrgentDemandForm'
import { category, clock, colorFor, duration, number, percent, statusLabel } from './lib/format'
import './components/strategy-balance.css'
import { SchedulePage } from './pages/SchedulePage'
import { VisualAnalysis } from './pages/VisualAnalysis'
import { MapCenter } from './pages/MapCenter'
import { HistoryCenter } from './pages/HistoryCenter'
import { CompareCenter } from './pages/CompareCenter'
import { GuidePage } from './pages/GuidePage'
import { LocalProfileDialog, useLocalProfile } from './components/LocalProfile'

type Page =
  | 'workspace'
  | 'scenario'
  | 'events'
  | 'analysis'
  | 'maps'
  | 'history'
  | 'compare'
  | 'guide'
  | 'schedule'
const pageLabels: Record<Page, string> = {
  workspace: '调度工作台',
  schedule: '调度安排',
  scenario: '场景与资源',
  events: '事件复盘',
  analysis: '数据大屏',
  maps: '地图与地形',
  history: '历史档案',
  compare: '方案对比',
  guide: '新手教程',
}
const objectiveLabels = { time: '时间优先', energy: '能耗优先', balanced: '时间能耗折中' }
function pageFromHash(): Page {
  const value = location.hash.replace(/^#\/?/, '')
  return Object.hasOwn(pageLabels, value) ? (value as Page) : 'workspace'
}

export default function App() {
  const query = useQueryClient()
  const { profile, saveProfile } = useLocalProfile()
  const [profileOpen, setProfileOpen] = useState(false)
  const [theme, setTheme] = useState<'midnight' | 'light'>(() =>
    localStorage.getItem('yuanhang-theme') === 'light' ? 'light' : 'midnight',
  )
  const [motion, setMotion] = useState(() => localStorage.getItem('yuanhang-motion') !== 'off')
  useEffect(() => {
    document.documentElement.dataset.theme = theme
    localStorage.setItem('yuanhang-theme', theme)
  }, [theme])
  useEffect(() => {
    document.documentElement.dataset.motion = motion ? 'on' : 'off'
    localStorage.setItem('yuanhang-motion', motion ? 'on' : 'off')
  }, [motion])
  const [page, setPageState] = useState<Page>(pageFromHash),
    [eventTab, setEventTab] = useState<'events' | 'analysis' | 'partition'>('events'),
    [scenarioId, setScenarioId] = useState(() => localStorage.getItem('yuanhang-scenario') || ''),
    [planId, setPlanId] = useState(
      () =>
        localStorage.getItem(
          'yuanhang-plan-' + (localStorage.getItem('yuanhang-scenario') || ''),
        ) || '',
    ),
    [jobId, setJobId] = useState(''),
    [selected, setSelected] = useState<string | null>(null),
    [previousId, setPreviousId] = useState(''),
    [search, setSearch] = useState(''),
    [listMode, setListMode] = useState<'sorties' | 'demands' | 'cargo'>('sorties'),
    [creating, setCreating] = useState(false),
    [submitting, setSubmitting] = useState(false),
    [confirming, setConfirming] = useState(false),
    [validationOpen, setValidationOpen] = useState(false),
    [scopeOpen, setScopeOpen] = useState(false),
    [menuOpen, setMenuOpen] = useState(false),
    [mobileNav, setMobileNav] = useState(false),
    [messages, setMessages] = useState<ToastMessage[]>([]),
    [failureId, setFailureId] = useState(''),
    [eventBusy, setEventBusy] = useState(false),
    [playTime, setPlayTime] = useState<number | null>(null),
    [playing, setPlaying] = useState(false)
  const setPage = useCallback((target: Page) => {
    setPageState(target)
    if (location.hash !== `#/${target}`) history.pushState(null, '', `#/${target}`)
  }, [])
  useEffect(() => {
    const restore = () => setPageState(pageFromHash())
    addEventListener('popstate', restore)
    addEventListener('hashchange', restore)
    return () => {
      removeEventListener('popstate', restore)
      removeEventListener('hashchange', restore)
    }
  }, [])
  useEffect(() => {
    if (!mobileNav) return
    const close = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setMobileNav(false)
    }
    addEventListener('keydown', close)
    return () => removeEventListener('keydown', close)
  }, [mobileNav])
  const [failureKind, setFailureKind] = useState<'drone' | 'battery' | 'relay_energy' | 'urgent'>(
    'drone',
  )
  const initialized = useRef(false),
    seenJobs = useRef(new Set<string>()),
    restoredTerminalJobs = useRef(new Set<string>())
  const scenarios = useQuery({ queryKey: ['scenarios'], queryFn: api.scenarios })
  const sceneQuery = useQuery({
    queryKey: ['scenario', scenarioId],
    queryFn: () => api.scenario(scenarioId),
    enabled: !!scenarioId,
  })
  const plans = useQuery({
    queryKey: ['plans', scenarioId],
    queryFn: () => api.plans(scenarioId),
    enabled: !!scenarioId,
  })
  const scenarioJobs = useQuery({
    queryKey: ['jobs', scenarioId],
    queryFn: () => api.jobs(scenarioId),
    enabled: !!scenarioId,
    refetchInterval: (q) =>
      q.state.data?.some((j) => ['queued', 'running'].includes(j.job_state)) ? 1000 : false,
  })
  const planQuery = useQuery({
    queryKey: ['plan', planId],
    queryFn: () => api.plan(planId),
    enabled: !!planId,
  })
  const comparisonPlanId =
    previousId ||
    (planQuery.data?.scenario_id === scenarioId ? planQuery.data.parent_plan_id : '') ||
    ''
  const oldQuery = useQuery({
    queryKey: ['plan', comparisonPlanId],
    queryFn: () => api.plan(comparisonPlanId),
    enabled: !!comparisonPlanId,
  })
  const planSnapshot = useQuery({
    queryKey: ['snapshot', planQuery.data?.snapshot_id],
    queryFn: () => api.getSnapshot(planQuery.data!.snapshot_id),
    enabled: !!planQuery.data,
  })
  const quality = useQuery({
    queryKey: ['analysis', planId],
    queryFn: () => api.analysis(planId),
    enabled: !!planId,
  })
  const events = useQuery({
    queryKey: ['events', scenarioId],
    queryFn: () => api.events(scenarioId),
    enabled: !!scenarioId,
  })
  const health = useQuery({
    queryKey: ['health'],
    queryFn: api.health,
    refetchInterval: 15000,
    retry: 1,
  })
  const playback = useQuery({
    queryKey: ['playback', planId],
    queryFn: () => api.playback(planId),
    enabled: !!planId,
  })
  const job = useQuery({
    queryKey: ['job', jobId],
    queryFn: () => api.job(jobId),
    enabled: !!jobId,
    refetchInterval: (q) =>
      q.state.data && ['completed', 'failed', 'canceled'].includes(q.state.data.job_state)
        ? false
        : 500,
  })
  const progress = useQuery({
    queryKey: ['progress', jobId],
    queryFn: () => api.progress(jobId),
    enabled: !!jobId && job.data?.job_state === 'running',
    refetchInterval: 700,
  })
  const diagnostics = useQuery({
    queryKey: ['diagnostics', jobId],
    queryFn: () => api.diagnostics(jobId),
    enabled:
      !!jobId &&
      !!job.data &&
      ['completed', 'failed', 'canceled'].includes(job.data.job_state) &&
      !job.data.plan_id,
  })
  const scenario = sceneQuery.data,
    selectedPlan = planQuery.data?.scenario_id === scenarioId ? planQuery.data : null,
    oldPlan = oldQuery.data
  const snapshotBound = !!(
    selectedPlan &&
    planSnapshot.data?.snapshot_id === selectedPlan.snapshot_id &&
    planSnapshot.data.scenario_id === selectedPlan.scenario_id &&
    planSnapshot.data.scenario_state_version === selectedPlan.scenario_state_version
  )
  const plan = snapshotBound ? selectedPlan : null
  const strategyPolicy = plan || { objective_policy: 'tradeoff_v2' as const }
  const bindingUnavailable = !!selectedPlan && !snapshotBound
  const viewScenario = plan ? planSnapshot.data!.scenario : scenario
  const isBusy = !!(
    submitting ||
    eventBusy ||
    (job.data &&
      job.data.scenario_id === scenarioId &&
      ['queued', 'running'].includes(job.data.job_state))
  )
  const stale = !!(plan && scenario && plan.scenario_state_version !== scenario.state_version)
  const route = plan?.sorties.find((r) => r.sortie_id === selected) || plan?.sorties[0]
  const sortedPlans = useMemo(
    () => [...(plans.data || [])].sort((a, b) => b.generated_at.localeCompare(a.generated_at)),
    [plans.data],
  )
  const comparisonIds = ['time', 'energy', 'balanced']
    .filter((objective) => objective !== plan?.objective)
    .map(
      (objective) =>
        sortedPlans.find(
          (p) =>
            p.snapshot_id === plan?.snapshot_id &&
            p.objective === objective &&
            policyOf(p) === policyOf(plan),
        )?.plan_id,
    )
    .filter((id): id is string => !!id)
  const comparisonQueries = useQueries({
    queries: comparisonIds.map((id) => ({ queryKey: ['plan', id], queryFn: () => api.plan(id) })),
  })
  const comparisonPlans = comparisonQueries.map((q) => q.data)
  const comparisonLoading = comparisonQueries.some((q) => q.isFetching)
  const comparisonError = comparisonQueries.some((q) => q.isError)
  const balancedPlan =
    plan?.objective === 'balanced'
      ? plan
      : comparisonPlans.find(
          (p) => p?.snapshot_id === plan?.snapshot_id && p?.objective === 'balanced',
        ) || null

  const notify = useCallback((message: string, error = false) => {
    const id = Date.now() + Math.random()
    setMessages((items) => [...items.slice(-3), { id, message, tone: error ? 'error' : 'success' }])
    setTimeout(() => setMessages((items) => items.filter((t) => t.id !== id)), 6500)
  }, [])
  const chooseScene = useCallback((id: string) => {
    setScenarioId(id)
    localStorage.setItem('yuanhang-scenario', id)
    setPlanId(localStorage.getItem('yuanhang-plan-' + id) || '')
    setSelected(null)
    setPreviousId('')
    setJobId('')
    setSearch('')
    setPlayTime(null)
    setPlaying(false)
    setFailureId('')
    setFailureKind('drone')
  }, [])
  const choosePlan = useCallback(
    (id: string) => {
      setPlanId(id)
      localStorage.setItem('yuanhang-plan-' + scenarioId, id)
      setSelected(null)
      setPlayTime(null)
      setPlaying(false)
      setPreviousId('')
    },
    [scenarioId],
  )
  const created = useCallback(
    (s: Scenario) => {
      query.setQueryData(['scenario', s.scenario_id], s)
      void query.invalidateQueries({ queryKey: ['scenarios'] })
      chooseScene(s.scenario_id)
    },
    [query, chooseScene],
  )
  const loadExample = useCallback(
    async (example: 'compact' | 'contest') => {
      setCreating(true)
      try {
        created(await api.example(example))
        notify(example === 'compact' ? '已加载5点32箱演练场景。' : '已加载原题15点80箱运输场景。')
      } catch (e) {
        notify((e as Error).message, true)
      } finally {
        setCreating(false)
      }
    },
    [created, notify],
  )
  async function saveScene(s: Scenario) {
    const updated = await api.save(s)
    query.setQueryData(['scenario', s.scenario_id], updated)
    void query.invalidateQueries({ queryKey: ['scenarios'] })
  }

  useEffect(() => {
    if (!scenarios.data) return
    if (
      scenarios.data.length &&
      (!scenarioId ||
        (sceneQuery.error instanceof ApiError &&
          sceneQuery.error.status === 404 &&
          !scenarios.data.some((s) => s.scenario_id === scenarioId)))
    )
      chooseScene(scenarios.data[0].scenario_id)
    else if (!scenarios.data.length && !initialized.current) {
      initialized.current = true
      void loadExample('compact')
    }
  }, [scenarios.data, scenarioId, sceneQuery.error, chooseScene, loadExample])
  useEffect(() => {
    if (!planId && sortedPlans.length) choosePlan(sortedPlans[0].plan_id)
  }, [planId, sortedPlans, choosePlan])
  useEffect(() => {
    const missing = planQuery.error instanceof ApiError && planQuery.error.status === 404
    const foreign = planQuery.data && planQuery.data.scenario_id !== scenarioId
    if ((missing || foreign) && sortedPlans.length) choosePlan(sortedPlans[0].plan_id)
  }, [planQuery.error, planQuery.data, scenarioId, sortedPlans, choosePlan])
  useEffect(() => {
    if (jobId || !scenarioJobs.data?.length) return
    const active = scenarioJobs.data.find((j) => ['queued', 'running'].includes(j.job_state))
    const latest = scenarioJobs.data[0]
    if (active) setJobId(active.job_id)
    else if (!latest.plan_id || !planId) {
      // Loading a completed historical job restores state; it is not a new completion.
      restoredTerminalJobs.current.add(latest.job_id)
      setJobId(latest.job_id)
    }
  }, [jobId, planId, scenarioJobs.data])
  useEffect(() => {
    const value = job.data
    if (
      !value ||
      !['completed', 'failed', 'canceled'].includes(value.job_state) ||
      seenJobs.current.has(value.job_id)
    )
      return
    seenJobs.current.add(value.job_id)
    const restored = restoredTerminalJobs.current.delete(value.job_id)
    void query.invalidateQueries({ queryKey: ['jobs', scenarioId] })
    if (value.plan_id) {
      choosePlan(value.plan_id)
      void query.invalidateQueries({ queryKey: ['plans', scenarioId] })
      if (!restored) notify(`真实计算完成 · ${duration(value.runtime_s)} · 独立检查通过`)
    } else if (restored) return
    else if (value.job_state === 'failed')
      notify(value.error?.message || '求解进程异常，请检查任务日志。', true)
    else if (value.job_state === 'canceled') notify('任务已停止，未发布未完成候选。')
    else
      void api
        .diagnostics(value.job_id)
        .then((d) =>
          notify(d.diagnostics[0]?.message || statusLabel[value.solver_status || 'UNKNOWN'], true),
        )
  }, [job.data, choosePlan, query, scenarioId, notify])
  useEffect(() => {
    if (!playing || !plan) return
    const timer = setInterval(
      () =>
        setPlayTime((t) => {
          const next = (t || 0) + plan.metrics.makespan_s! / 100
          if (next >= plan.metrics.makespan_s!) {
            setPlaying(false)
            return plan.metrics.makespan_s
          }
          return next
        }),
      150,
    )
    return () => clearInterval(timer)
  }, [playing, plan])

  async function runSolver(objective: 'time' | 'energy' | 'balanced', improve = false) {
    if (!scenario || isBusy || bindingUnavailable || scenario.data_origin === 'mock') return
    setSubmitting(true)
    try {
      const snap =
        plan && !stale ? await api.getSnapshot(plan.snapshot_id) : await api.snapshot(scenario)
      const created = await api.solve(
        snap.snapshot_id,
        objective,
        improve
          ? {
              mode: 'improve',
              time_limit_s: scenario.policy.requires_communication ? 60 : 30,
              initial_plan_id: plan?.plan_id,
              objective_policy: policyOf(plan),
            }
          : { time_limit_s: scenario.policy.requires_communication ? 60 : 15 },
      )
      setJobId(created.job_id)
      query.setQueryData(['job', created.job_id], created)
      notify('已提交真实求解，输入已固定为不可变快照。')
    } catch (e) {
      notify((e as Error).message, true)
    } finally {
      setSubmitting(false)
    }
  }
  function eventCommon() {
    const when = new Date().toISOString()
    return {
      schema_version: scenario!.schema_version,
      event_id: 'EVT-' + crypto.randomUUID().slice(0, 16),
      scenario_id: scenario!.scenario_id,
      expected_state_version: scenario!.state_version,
      occurred_at: when,
      received_at: when,
      effective_time_s: 0,
      actor: 'simulation' as const,
    }
  }
  async function applyAndReplan(request: Event, label: string): Promise<boolean> {
    if (
      !scenario ||
      !plan ||
      isBusy ||
      stale ||
      bindingUnavailable ||
      scenario.data_origin === 'mock'
    )
      return false
    setEventBusy(true)
    let applied = false
    try {
      const event = await api.event(request)
      applied = true
      const updated = await api.scenario(scenarioId)
      query.setQueryData(['scenario', scenarioId], updated)
      void query.invalidateQueries({ queryKey: ['scenarios'] })
      void query.invalidateQueries({ queryKey: ['events', scenarioId] })
      const snap = await api.snapshot(updated)
      setPreviousId(plan.plan_id)
      const newJob = await api.solve(
        snap.snapshot_id,
        plan.objective as 'time' | 'energy' | 'balanced',
        {
          mode: 'replan',
          objective_policy: policyOf(plan),
          parent_plan_id: plan.plan_id,
          event_id: event.event.event_id,
          time_limit_s: updated.policy.requires_communication ? 60 : 15,
        },
      )
      setJobId(newJob.job_id)
      query.setQueryData(['job', newJob.job_id], newJob)
      notify(label + '，新版本正在真实重规划。')
      setFailureId('')
      return true
    } catch (e) {
      notify((applied ? '事件已保存，请按新版本重新求解。' : '') + (e as Error).message, true)
      return applied
    } finally {
      setEventBusy(false)
    }
  }
  async function injectFailure() {
    if (!scenario || !failureId || failureKind === 'urgent') return
    const common = eventCommon()
    await applyAndReplan(
      failureKind === 'drone'
        ? {
            ...common,
            event_type: 'drone.unavailable',
            reason: '模拟演练：未起飞机体退出',
            payload: { drone_id: failureId },
          }
        : failureKind === 'battery'
          ? {
              ...common,
              event_type: 'battery.unavailable',
              reason: '模拟演练：运输电池退出',
              payload: { battery_id: failureId },
            }
          : {
              ...common,
              event_type: 'relay_energy.unavailable',
              reason: '模拟演练：中继能源组件退出',
              payload: { component_id: failureId },
            },
      `${failureKind === 'battery' ? '运输电池 ' : failureKind === 'relay_energy' ? '中继能源组件 ' : '机体 '}${failureId}已退出`,
    )
  }
  async function insertUrgent(payload: UrgentPayload, reason: string) {
    if (!scenario) return false
    return applyAndReplan(
      { ...eventCommon(), event_type: 'demand.added', payload, reason },
      `已新增${payload.demand.required_quantity}箱紧急需求`,
    )
  }
  async function confirm() {
    if (!plan || !scenario) return
    setConfirming(true)
    try {
      await api.confirm(plan, scenario.state_version)
      void query.invalidateQueries({ queryKey: ['plans', scenarioId] })
      void query.invalidateQueries({ queryKey: ['scenarios'] })
      notify('方案已确认并原子预约资源。此操作不会下发飞控指令。')
    } catch (e) {
      notify((e as Error).message, true)
    } finally {
      setConfirming(false)
    }
  }

  const stats =
    scenario && viewScenario
      ? [
          {
            label: '已安排箱件',
            value: plan
              ? number(plan.sorties.reduce((n, r) => n + r.cargo_ids.length, 0))
              : '待计算',
            unit: plan ? `/ ${viewScenario.cargo_items.length} 箱` : '',
            icon: Package,
            note: plan ? '完整服务 · 箱件唯一分配' : '库存与需求分别管理',
          },
          {
            label: '最后交付',
            value: duration(plan?.metrics.last_delivery_s),
            unit: '',
            icon: Clock3,
            note: plan ? `最后返航 ${duration(plan.metrics.makespan_s)}` : '以整站交接完成计时',
          },
          {
            label: plan?.joint_metrics ? '运输能耗' : '预计总能耗',
            value: number(plan?.metrics.energy_kwh, 2),
            unit: 'kWh',
            icon: Zap,
            note: plan ? `${plan.metrics.sortie_count} 架次 · 已含返航` : '题设物理模型估计',
          },
          {
            label: '最低返航电量',
            value: percent(plan?.metrics.min_return_soc),
            unit: '',
            icon: BatteryCharging,
            note: `策略下限 ${percent(viewScenario.policy.min_return_soc)}`,
          },
        ]
      : []
  const cargoAssignments = new Map<string, string>(
    plan?.sorties.flatMap((r) => r.cargo_ids.map((c) => [c, r.sortie_id] as [string, string])) ||
      [],
  )
  const oldAssignments = new Map<string, string>(
    oldPlan?.sorties.flatMap((r) => r.cargo_ids.map((c) => [c, r.drone_id] as [string, string])) ||
      [],
  )
  const changedCargo =
    plan && oldPlan
      ? plan.sorties.reduce(
          (n, r) =>
            n +
            r.cargo_ids.filter((c) => oldAssignments.has(c) && oldAssignments.get(c) !== r.drone_id)
              .length,
          0,
        )
      : 0
  const oldBatteryAssignments = new Map<string, string>(
    oldPlan?.sorties.flatMap((r) =>
      r.cargo_ids.map((c) => [c, r.battery_id] as [string, string]),
    ) || [],
  )
  const changedBatteryCargo =
    plan && oldPlan
      ? plan.sorties.reduce(
          (n, r) =>
            n +
            r.cargo_ids.filter(
              (c) => oldBatteryAssignments.has(c) && oldBatteryAssignments.get(c) !== r.battery_id,
            ).length,
          0,
        )
      : 0

  return (
    <div className="app-shell">
      <div className="ambient-background" aria-hidden="true">
        <i />
        <i />
        <i />
        <div className="ambient-grid" />
        <div className="ambient-beam" />
        <div className="ambient-particles">
          {Array.from({ length: 18 }, (_, i) => (
            <span
              key={i}
              style={{
                left: `${(i * 37 + 11) % 100}%`,
                top: `${(i * 23 + 7) % 100}%`,
                animationDelay: `${-i * 1.7}s`,
                animationDuration: `${11 + (i % 6) * 2}s`,
              }}
            />
          ))}
        </div>
      </div>
      {mobileNav && (
        <button
          className="mobile-nav-backdrop"
          aria-label="关闭导航"
          onClick={() => setMobileNav(false)}
        />
      )}
      <aside className={`sidebar ${mobileNav ? 'mobile-open' : ''}`}>
        <a
          className="brand"
          href="#"
          onClick={(e) => {
            e.preventDefault()
            setPage('workspace')
          }}
        >
          <span className="brand-mark">
            <Drone size={22} />
            <i />
          </span>
          <span>
            <strong>援航</strong>
            <small>YUANHANG RESCUE</small>
          </span>
        </a>
        <div className="workspace-switch">
          <span className="workspace-avatar">应</span>
          <span>
            <strong>{profile.team}</strong>
            <small>应急协同 · 本机工作空间</small>
          </span>
          <ChevronDown size={13} />
        </div>
        <div className="nav-caption">任务协同</div>
        <nav>
          {(
            [
              { id: 'analysis', label: '数据大屏', icon: BarChart3 },
              { id: 'scenario', label: '场景与资源', icon: Database },
              { id: 'maps', label: '地图与地形', icon: Globe2 },
              { id: 'workspace', label: '调度工作台', icon: MapIcon },
              { id: 'schedule', label: '调度安排', icon: Layers },
              { id: 'compare', label: '方案对比', icon: GitCompareArrows },
              { id: 'events', label: '事件复盘', icon: Activity },
              { id: 'history', label: '历史档案', icon: History },
              { id: 'guide', label: '新手教程', icon: BookOpen },
            ] as const
          ).map((item) => (
            <button
              key={item.id}
              className={page === item.id ? 'active' : ''}
              aria-current={page === item.id ? 'page' : undefined}
              onClick={() => {
                setPage(item.id)
                setMobileNav(false)
              }}
            >
              <item.icon size={18} />
              <span>{item.label}</span>
              {page === item.id && <i />}
            </button>
          ))}
        </nav>
        <div className="sidebar-card">
          <div>
            <Sparkles size={18} />
            <strong>救援决策，从这里开始</strong>
          </div>
          <p>准备数据、读取地形、生成方案。跟着教程完成第一次调度。</p>
          <button onClick={() => setPage('guide')}>
            打开上手指南 <ArrowRight size={13} />
          </button>
        </div>
        <div className="sidebar-bottom">
          <div>
            <span className="connection-dot" />
            本机服务 <Badge tone="teal">离线可用</Badge>
          </div>
          <button onClick={() => setPage('guide')}>
            <CircleHelp size={16} />
            使用教程与常见问题
          </button>
          <button
            className="profile"
            onClick={() => setProfileOpen(true)}
            aria-label="账户与本机档案"
          >
            <span style={{ background: profile.color, color: '#fff' }}>
              {Array.from(profile.displayName)[0]}
            </span>
            <div>
              <strong>{profile.displayName}</strong>
              <small>{profile.role} · 本机档案</small>
            </div>
            <Settings2 size={15} />
          </button>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <div className="breadcrumbs">
            <button
              className="icon-button mobile-toggle"
              onClick={() => setMobileNav(!mobileNav)}
              aria-label="打开导航"
            >
              <Menu size={19} />
            </button>
            <span>救援工作空间</span>
            <ChevronRight size={14} />
            <strong>{pageLabels[page]}</strong>
          </div>
          <div className="topbar-actions">
            <button
              className="icon-button"
              aria-label={theme === 'midnight' ? '切换浅色主题' : '切换深色主题'}
              title={theme === 'midnight' ? '切换浅色主题' : '切换深色主题'}
              onClick={() => setTheme(theme === 'midnight' ? 'light' : 'midnight')}
            >
              {theme === 'midnight' ? <Sun size={17} /> : <Moon size={17} />}
            </button>
            <button
              className={`icon-button motion-toggle ${motion ? 'active' : ''}`}
              aria-label={motion ? '暂停动态背景' : '启用动态背景'}
              aria-pressed={motion}
              title={motion ? '暂停动态背景' : '启用动态背景'}
              onClick={() => setMotion(!motion)}
            >
              <Sparkles size={16} />
            </button>
            <span className={`topbar-live ${health.isError ? 'disconnected' : ''}`}>
              <i />
              {health.isError
                ? '本地服务未连接'
                : health.data
                  ? '本地服务已连接'
                  : '连接本地服务中'}
            </span>
            <button
              className="icon-button"
              aria-label="查看模型说明"
              onClick={() => setScopeOpen(true)}
            >
              <CircleHelp size={18} />
            </button>
            <button
              className="header-avatar"
              style={{ background: profile.color, color: '#fff' }}
              aria-label="打开个人档案"
              onClick={() => setProfileOpen(true)}
            >
              {Array.from(profile.displayName)[0]}
            </button>
          </div>
        </header>
        <main className="main-content">
          {page === 'guide' ? (
            <GuidePage
              onNavigate={(target) => {
                setPage(target)
                setMobileNav(false)
              }}
            />
          ) : !scenario ? (
            <div className="boot-screen">
              {scenarios.error || sceneQuery.error ? (
                <Empty
                  icon={<ShieldAlert size={30} />}
                  title="暂时无法连接本机服务"
                  description="请确认后端已在本机8000端口启动，再刷新页面。"
                  action={
                    <Button onClick={() => location.reload()}>
                      <RefreshCw size={15} />
                      重新连接
                    </Button>
                  }
                />
              ) : (
                <>
                  <span className="boot-mark">
                    <Drone size={35} />
                  </span>
                  <h2>援航 · 让每一程救援有序抵达</h2>
                  <p>
                    <LoaderCircle size={16} className="spin" />
                    正在加载真实场景与本机服务…
                  </p>
                </>
              )}
            </div>
          ) : (
            <>
              <div className="scene-bar">
                <div className="scene-select">
                  <span className="scene-icon">
                    <MapPin size={18} />
                  </span>
                  <div>
                    <select
                      aria-label="选择场景"
                      value={scenarioId}
                      onChange={(e) => chooseScene(e.target.value)}
                    >
                      {!scenarios.data?.some((s) => s.scenario_id === scenarioId) && (
                        <option value={scenarioId}>{scenario.name}</option>
                      )}
                      {scenarios.data?.map((s) => (
                        <option key={s.scenario_id} value={s.scenario_id}>
                          {s.name}
                        </option>
                      ))}
                    </select>
                    <span>
                      {scenario.sites.length} 个需求点 <i /> {scenario.cargo_items.length} 箱物资{' '}
                      <i /> 场景起点{' '}
                      {new Date(scenario.start_time).toLocaleTimeString('zh-CN', {
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: false,
                      })}
                    </span>
                  </div>
                  <Badge tone="teal">模拟演练</Badge>
                  <Badge>v{scenario.state_version}</Badge>
                </div>
                <div className="scene-actions">
                  <Button busy={creating} onClick={() => void loadExample('compact')}>
                    <Plus size={15} />
                    新建演练
                  </Button>
                  <div className="more-menu">
                    <button
                      className="icon-button"
                      aria-label="更多场景操作"
                      onClick={() => setMenuOpen(!menuOpen)}
                    >
                      <MoreHorizontal size={19} />
                    </button>
                    {menuOpen && (
                      <div className="dropdown">
                        <button
                          onClick={() => {
                            void loadExample('contest')
                            setMenuOpen(false)
                          }}
                        >
                          <Database size={15} />
                          加载原题80箱场景
                        </button>
                        <button
                          onClick={async () => {
                            try {
                              created(await api.copy(scenarioId))
                              notify('已创建场景副本。')
                            } catch (e) {
                              notify((e as Error).message, true)
                            }
                            setMenuOpen(false)
                          }}
                        >
                          <Copy size={15} />
                          复制当前场景
                        </button>
                        <button
                          onClick={() => {
                            downloadJson(scenario, scenarioId + '.json')
                            setMenuOpen(false)
                          }}
                        >
                          <FileDown size={15} />
                          导出场景JSON
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
              {page === 'maps' ? (
                <MapCenter
                  key={scenario.scenario_id}
                  scenario={scenario}
                  onAssigned={created}
                  notify={notify}
                />
              ) : page === 'analysis' ? (
                <VisualAnalysis
                  scenario={scenario}
                  plan={plan}
                  onOpenMap={() => setPage('maps')}
                  onOpenWorkspace={() => setPage('workspace')}
                />
              ) : page === 'history' ? (
                <HistoryCenter
                  key={scenario.scenario_id}
                  scenario={scenario}
                  onOpenPlan={(id) => {
                    choosePlan(id)
                    setPage('workspace')
                  }}
                  onOpenScene={(id) => {
                    chooseScene(id)
                    setPage('workspace')
                  }}
                  onCompare={() => setPage('compare')}
                />
              ) : page === 'compare' ? (
                <CompareCenter
                  key={scenario.scenario_id}
                  scenario={scenario}
                  selectedPlanId={planId}
                  onOpenPlan={(id) => {
                    choosePlan(id)
                    setPage('workspace')
                  }}
                  onWorkspace={() => setPage('workspace')}
                />
              ) : page === 'schedule' ? (
                bindingUnavailable ? (
                  <div className="alert alert-amber">
                    <TriangleAlert size={17} />
                    <span>
                      {planSnapshot.isError
                        ? '方案原始输入读取失败，无法展示调度安排。'
                        : '正在绑定方案原始输入…'}
                    </span>
                    {planSnapshot.isError && (
                      <Button onClick={() => void planSnapshot.refetch()}>重试加载快照</Button>
                    )}
                  </div>
                ) : (
                  <SchedulePage
                    plan={plan}
                    scenario={viewScenario || scenario}
                    plans={sortedPlans}
                    selected={selected}
                    onSelect={setSelected}
                    onPlan={choosePlan}
                    onMap={() => setPage('workspace')}
                  />
                )
              ) : page === 'scenario' ? (
                <ScenarioEditor
                  scenario={scenario}
                  onSave={saveScene}
                  onCreated={created}
                  notify={notify}
                  onWorkspace={() => setPage('workspace')}
                />
              ) : (
                <>
                  <div className="page-heading workspace-heading">
                    <div>
                      <div className="eyebrow">
                        {page === 'events' ? 'EVENTS & REPLANNING' : 'MISSION CONTROL'}
                      </div>
                      <h1>
                        {page === 'events'
                          ? eventTab === 'analysis'
                            ? '看清资源，让每次增配都有依据'
                            : eventTab === 'partition'
                              ? '分组协作，让保障各有所属'
                              : '面对变化，让救援继续前行'
                          : '每一份物资，都有清晰的下一程'}
                        <span>{page === 'events' ? 'EVENT REVIEW' : 'LIVE WORKSPACE'}</span>
                      </h1>
                      <p>
                        {page === 'events'
                          ? eventTab === 'analysis'
                            ? '从计划占用和时限余量出发，真实比较增配与压力情景。'
                            : eventTab === 'partition'
                              ? '继承已验证联合方案，核算独立任务组的资源峰值与共享损失。'
                              : '保留原计划与事件事实，在新快照上重新计算未来任务。'
                          : '从真实输入出发，统筹箱件、机体与电池，生成可核对的运输方案。'}
                      </p>
                    </div>
                    <div className="heading-actions">
                      {plan && (
                        <select
                          className="plan-selector"
                          aria-label="选择历史方案"
                          value={planId}
                          onChange={(e) => choosePlan(e.target.value)}
                        >
                          {sortedPlans.map((p) => (
                            <option key={p.plan_id} value={p.plan_id}>
                              {objectiveLabels[p.objective as keyof typeof objectiveLabels]} ·{' '}
                              {p.algorithm_mode === 'improve'
                                ? '深入'
                                : p.algorithm_mode === 'replan'
                                  ? '重规划'
                                  : '快速'}{' '}
                              · v{p.scenario_state_version}
                              {p.confirmed_at ? ' · 已确认' : ''}
                            </option>
                          ))}
                        </select>
                      )}
                      <Button onClick={() => setValidationOpen(true)} disabled={!plan}>
                        <ShieldCheck size={15} />
                        检查报告
                      </Button>
                      {page === 'workspace' && plan && (
                        <Button onClick={() => setPage('schedule')}>
                          <Layers size={14} />
                          查看调度安排
                        </Button>
                      )}
                      {page === 'workspace' && plan && (
                        <Button
                          disabled={isBusy || stale || scenario.data_origin === 'mock'}
                          title={
                            scenario.policy.requires_communication
                              ? '同一快照上执行60秒有限分解联合调度；未找到更优方案时保留已验算基线。'
                              : '同一快照上执行30秒限时路线池搜索；未找到更优方案时保留已验算基线。'
                          }
                          onClick={() =>
                            void runSolver(plan.objective as 'time' | 'energy' | 'balanced', true)
                          }
                        >
                          <RefreshCw size={14} />
                          {scenario.policy.requires_communication ? '联合优化60秒' : '深入优化30秒'}
                        </Button>
                      )}
                      {page === 'workspace' && (
                        <Button
                          variant="primary"
                          busy={isBusy}
                          disabled={bindingUnavailable || scenario.data_origin === 'mock'}
                          onClick={() => void runSolver('time')}
                        >
                          <Play size={14} /> {plan ? '重新求解' : '生成真实方案'}
                        </Button>
                      )}
                    </div>
                  </div>
                  {page === 'workspace' && (
                    <div className="workspace-quicklinks">
                      <span>
                        <i />
                        当前方案 · 真实数据联动
                      </span>
                      <button onClick={() => setPage('analysis')}>
                        <BarChart3 size={13} />
                        三维与高度分析
                        <ArrowRight size={12} />
                      </button>
                      <button onClick={() => setPage('maps')}>
                        <Globe2 size={13} />
                        卫星地图 / 导入DEM
                      </button>
                      <button onClick={() => setPage('compare')}>
                        <GitCompareArrows size={13} />
                        方案对比
                      </button>
                      <button onClick={() => setPage('history')}>
                        <History size={13} />
                        历史档案
                      </button>
                    </div>
                  )}
                  {page === 'events' && (
                    <div className="page-tabs" aria-label="复盘工作模式">
                      <button
                        className={eventTab === 'events' ? 'active' : ''}
                        onClick={() => setEventTab('events')}
                      >
                        <Activity size={15} />
                        动态事件
                      </button>
                      <button
                        className={eventTab === 'analysis' ? 'active' : ''}
                        onClick={() => setEventTab('analysis')}
                      >
                        <Database size={15} />
                        资源分析与试算
                      </button>
                      <button
                        className={eventTab === 'partition' ? 'active' : ''}
                        onClick={() => setEventTab('partition')}
                      >
                        <Layers size={15} />
                        冻结任务分区
                      </button>
                    </div>
                  )}
                  {scenario.data_origin === 'mock' && (
                    <div className="alert alert-amber">
                      <TriangleAlert size={17} />
                      当前为Mock开发样例，仅供结构预览，不能发布已验证方案或确认计划。
                    </div>
                  )}
                  {bindingUnavailable && (
                    <div className="alert alert-amber" role="status" aria-label="方案快照绑定">
                      {planSnapshot.isError ? (
                        <ShieldAlert size={18} />
                      ) : (
                        <LoaderCircle size={18} className="spin" />
                      )}
                      <span>
                        {planSnapshot.isError
                          ? '方案原始输入加载失败，暂时隐藏计算结果。'
                          : `正在加载 v${selectedPlan!.scenario_state_version} 方案的原始输入…`}
                      </span>
                      {planSnapshot.isError && (
                        <Button variant="ghost" onClick={() => void planSnapshot.refetch()}>
                          重试加载快照
                        </Button>
                      )}
                    </div>
                  )}
                  {stale && (
                    <div className="alert alert-amber">
                      <TriangleAlert size={17} />
                      <span>
                        当前展示 v{plan?.scenario_state_version} 历史方案；场景已更新为 v
                        {scenario.state_version}，确认已禁用，请重新求解。
                      </span>
                      <Button
                        variant="ghost"
                        onClick={() => void runSolver('time')}
                        disabled={isBusy}
                      >
                        重新计算 <ArrowRight size={14} />
                      </Button>
                    </div>
                  )}
                  {isBusy && (
                    <div className="job-banner">
                      <LoaderCircle size={18} className="spin" />
                      <div>
                        <strong>{progress.data?.stage || '正在创建不可变快照与计算任务'}</strong>
                        <span>
                          {number(progress.data?.elapsed_s, 1)} 秒 · 已处理候选{' '}
                          {progress.data?.candidate_count || 0} · 独立进程计算
                        </span>
                      </div>
                      <Button
                        onClick={() =>
                          jobId &&
                          void api
                            .cancel(jobId)
                            .then(() => query.invalidateQueries({ queryKey: ['job', jobId] }))
                        }
                        disabled={!jobId}
                      >
                        取消任务
                      </Button>
                    </div>
                  )}
                  {job.data &&
                    !isBusy &&
                    !job.data.plan_id &&
                    ['completed', 'failed', 'canceled'].includes(job.data.job_state) && (
                      <div className="alert alert-amber" role="status">
                        <TriangleAlert size={18} />
                        <div>
                          <strong>
                            {job.data.job_state === 'canceled'
                              ? '本次任务已取消'
                              : job.data.job_state === 'failed'
                                ? '本次计算失败'
                                : statusLabel[job.data.solver_status || 'UNKNOWN']}
                          </strong>
                          <p>
                            {job.data.error?.message ||
                              diagnostics.data?.diagnostics[0]?.message ||
                              '未发布新方案；可调整输入或重新提交。'}
                          </p>
                        </div>
                      </div>
                    )}
                  {!(page === 'events' && eventTab !== 'events') && (
                    <div className="stats-grid">
                      {stats.map((s, i) => (
                        <div className="stat-card" key={s.label}>
                          <div className="stat-label">
                            {s.label}
                            <s.icon size={17} />
                          </div>
                          <div className="stat-value">
                            {s.value}
                            <span>{s.unit}</span>
                          </div>
                          <div className="stat-note">
                            <i className={i === 0 && plan ? 'teal' : ''} />
                            {s.note}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                  {page === 'workspace' && plan && quality.data?.plan_id === plan.plan_id && (
                    <div
                      className="plan-quality"
                      title="加权箱秒是每箱期望延期秒乘需求优先级的合计，不是墙钟时长。"
                    >
                      <Badge tone="teal">硬截止已检查</Badge>
                      <span>
                        {quality.data.delivery.expected_demand_count
                          ? `期望延期 ${quality.data.delivery.late_demand_count} 条 · 加权箱秒 ${number(quality.data.delivery.weighted_box_delay_s, 0)}`
                          : '未设置期望时限'}
                      </span>
                      {quality.data.resource_limits && (
                        <span>
                          准备 {quality.data.resource_limits.prep_slots} 工位 · 充电{' '}
                          {quality.data.resource_limits.charging_ports} 端口
                        </span>
                      )}
                      <small>{policyLabel(strategyPolicy)} · 硬截止与完整物资保障始终必选</small>
                    </div>
                  )}
                  {page === 'events' && eventTab === 'partition' ? (
                    <PartitionAnalysis
                      key={plan?.plan_id || 'no-plan'}
                      plan={plan}
                      onConfigure={() => setPage('scenario')}
                    />
                  ) : page === 'events' && eventTab === 'analysis' ? (
                    <ResourceAnalysis
                      key={scenario.scenario_id}
                      scenario={viewScenario || scenario}
                      plan={plan}
                      stale={stale}
                      onOpen={(scene) => {
                        created(scene)
                        setPage('workspace')
                      }}
                      notify={notify}
                    />
                  ) : page === 'events' ? (
                    <div className="events-layout">
                      <aside className="panel event-input">
                        <div className="panel-heading">
                          <div>
                            <h3>事件注入</h3>
                            <p>仅作用于尚未执行的模拟场景</p>
                          </div>
                          <Activity size={18} />
                        </div>
                        <div className="event-form">
                          <label className="field">
                            <span>事件类型</span>
                            <select
                              aria-label="故障事件类型"
                              value={failureKind}
                              onChange={(e) => {
                                setFailureKind(
                                  e.target.value as 'drone' | 'battery' | 'relay_energy' | 'urgent',
                                )
                                setFailureId('')
                              }}
                            >
                              <option value="drone">未起飞机体退出</option>
                              <option value="battery">运输电池退出</option>
                              {scenario.policy.requires_communication && (
                                <option value="relay_energy">中继能源组件退出</option>
                              )}
                              <option value="urgent">紧急需求插入</option>
                            </select>
                          </label>
                          {failureKind === 'urgent' ? (
                            <UrgentDemandForm
                              key={scenarioId}
                              scenario={scenario}
                              disabled={
                                !plan ||
                                stale ||
                                bindingUnavailable ||
                                scenario.data_origin === 'mock'
                              }
                              busy={eventBusy || isBusy}
                              onSubmit={insertUrgent}
                            />
                          ) : (
                            <>
                              <label className="field">
                                <span>
                                  {failureKind === 'drone'
                                    ? '受影响机体'
                                    : failureKind === 'relay_energy'
                                      ? '受影响中继能源组件'
                                      : '受影响运输电池'}
                                </span>
                                <select
                                  aria-label={
                                    failureKind === 'drone'
                                      ? '故障机体'
                                      : failureKind === 'relay_energy'
                                        ? '故障中继能源组件'
                                        : '故障运输电池'
                                  }
                                  value={failureId}
                                  onChange={(e) => setFailureId(e.target.value)}
                                >
                                  <option value="">
                                    {failureKind === 'drone'
                                      ? '请选择可用机体'
                                      : failureKind === 'relay_energy'
                                        ? '请选择可退出组件'
                                        : '请选择可退出电池'}
                                  </option>
                                  {failureKind === 'drone' &&
                                    scenario.drones
                                      .filter((d) => d.status === 'available')
                                      .map((d) => (
                                        <option key={d.drone_id} value={d.drone_id}>
                                          {d.drone_id} · {d.type_id}型
                                        </option>
                                      ))}
                                  {failureKind === 'drone' &&
                                    scenario.policy.requires_communication &&
                                    scenario.communication?.relay_drones
                                      .filter((d) => d.status === 'available')
                                      .map((d) => (
                                        <option key={d.drone_id} value={d.drone_id}>
                                          {d.drone_id} · 中继机
                                        </option>
                                      ))}
                                  {failureKind === 'relay_energy' &&
                                    scenario.communication?.relay_energy
                                      .filter((b) => ['available', 'charging'].includes(b.status))
                                      .map((b) => (
                                        <option key={b.component_id} value={b.component_id}>
                                          {b.component_id} · 中继能源 · {percent(b.soc)}
                                        </option>
                                      ))}
                                  {failureKind === 'battery' &&
                                    scenario.batteries
                                      .filter((b) => ['available', 'charging'].includes(b.status))
                                      .map((b) => (
                                        <option key={b.battery_id} value={b.battery_id}>
                                          {b.battery_id} · {b.compatible_type_id}型 ·{' '}
                                          {percent(b.soc)}
                                        </option>
                                      ))}
                                </select>
                              </label>
                              <div className="callout amber">
                                <TriangleAlert size={16} />
                                仅支持尚未执行场景。事件保存新版本并保留原计划，只改变指定资源的可用状态。
                              </div>
                              <Button
                                variant="primary"
                                busy={eventBusy || isBusy}
                                disabled={!plan || !failureId || stale}
                                onClick={() => void injectFailure()}
                              >
                                <RefreshCw size={15} />
                                记录故障并重规划
                              </Button>
                            </>
                          )}
                        </div>
                        <div className="event-history">
                          <h4>
                            事件时间线 <Badge>{events.data?.length || 0}</Badge>
                          </h4>
                          {events.data?.length ? (
                            events.data.map((e) => (
                              <div className="event-item" key={e.event_id}>
                                <i />
                                <div>
                                  <strong>
                                    {e.event_type === 'demand.added'
                                      ? `新增需求 ${e.payload.demand.demand_id} · ${e.payload.demand.required_quantity}箱`
                                      : e.event_type === 'drone.unavailable'
                                        ? `机体 ${e.payload.drone_id} 退出`
                                        : e.event_type === 'battery.unavailable'
                                          ? `运输电池 ${e.payload.battery_id} 退出`
                                          : `中继能源组件 ${e.payload.component_id} 退出`}
                                  </strong>
                                  <p>{e.reason}</p>
                                  <small>
                                    v{e.expected_state_version} → v{e.expected_state_version + 1} ·{' '}
                                    {new Date(e.received_at).toLocaleTimeString('zh-CN', {
                                      hour12: false,
                                    })}
                                  </small>
                                </div>
                              </div>
                            ))
                          ) : (
                            <p className="muted">
                              还没有事件。先生成方案，再选择机体或运输电池模拟退出。
                            </p>
                          )}
                        </div>
                      </aside>
                      <div className="event-center">
                        <section className="panel">
                          <div className="panel-heading">
                            <div>
                              <h3>事件前后航线对比</h3>
                              <p>旧方案虚线 / 新方案实线，均为各自真实计算输出</p>
                            </div>
                            {oldPlan && <Badge tone="amber">不同快照</Badge>}
                          </div>
                          <RescueMap
                            scenario={viewScenario || scenario}
                            plan={plan}
                            oldPlan={oldPlan && oldPlan.plan_id !== plan?.plan_id ? oldPlan : null}
                            selected={selected}
                            onSelect={setSelected}
                          />
                        </section>
                        {oldPlan && plan && oldPlan.plan_id !== plan.plan_id ? (
                          <div>
                            <div className="comparison-cards">
                              <div>
                                <span>机体改派箱件</span>
                                <strong>
                                  {changedCargo}
                                  <small>箱</small>
                                </strong>
                              </div>
                              <div>
                                <span>返航时间变化</span>
                                <strong>
                                  {number(
                                    (plan.metrics.makespan_s || 0) -
                                      (oldPlan.metrics.makespan_s || 0),
                                    0,
                                  )}
                                  <small>秒</small>
                                </strong>
                              </div>
                              <div>
                                <span>保持架次</span>
                                <strong>
                                  {plan.change_summary?.preserved_sortie_ids.length || 0}
                                  <small>次</small>
                                </strong>
                              </div>
                              <div>
                                <span>电池改派箱件</span>
                                <strong className="teal">
                                  {changedBatteryCargo}
                                  <small>箱</small>
                                </strong>
                              </div>
                            </div>
                            {plan.sorties.some((r) =>
                              r.cargo_ids.some((c) => !oldAssignments.has(c)),
                            ) && (
                              <div className="callout" aria-label="新增需求安排">
                                <Package size={18} />
                                <span>
                                  新增已安排箱件{' '}
                                  <b>
                                    {plan.sorties.reduce(
                                      (n, r) =>
                                        n +
                                        r.cargo_ids.filter((c) => !oldAssignments.has(c)).length,
                                      0,
                                    )}{' '}
                                    箱
                                  </b>{' '}
                                  · 改派统计仅比较两版共有箱件。
                                </span>
                              </div>
                            )}
                            {oldPlan.joint_metrics && plan.joint_metrics && (
                              <div className="callout joint-event-diff" aria-label="中继方案变化">
                                <RadioTower size={18} />
                                <span>
                                  中继任务 {oldPlan.joint_metrics.relay_sortie_count} →{' '}
                                  {plan.joint_metrics.relay_sortie_count} 架次 · 联合能耗变化{' '}
                                  {number(
                                    plan.joint_metrics.joint_energy_kwh -
                                      oldPlan.joint_metrics.joint_energy_kwh,
                                    3,
                                  )}{' '}
                                  kWh · 联合返航变化{' '}
                                  {number(
                                    plan.joint_metrics.joint_makespan_s -
                                      oldPlan.joint_metrics.joint_makespan_s,
                                    0,
                                  )}{' '}
                                  秒
                                </span>
                              </div>
                            )}
                          </div>
                        ) : (
                          <div className="event-explainer">
                            <ShieldCheck size={24} />
                            <div>
                              <strong>变化有记录，调整有依据</strong>
                              <p>
                                事件后会创建新快照并真实重算，显示任务改派和指标变化。动画不会写入实际交付。
                              </p>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ) : (
                    <div className="workspace-grid">
                      <section className="panel mission-panel">
                        <div className="mission-heading">
                          <h3>
                            运输任务{' '}
                            <Badge>{plan?.sorties.length || scenario.demands.length}</Badge>
                          </h3>
                          <button
                            className="icon-button"
                            aria-label="编辑场景资源"
                            onClick={() => setPage('scenario')}
                          >
                            <Settings2 size={15} />
                          </button>
                        </div>
                        <div className="mission-tabs">
                          {(
                            [
                              { key: 'sorties', name: '架次' },
                              { key: 'demands', name: '需求' },
                              { key: 'cargo', name: '箱件' },
                            ] as const
                          ).map((t) => (
                            <button
                              key={t.key}
                              className={listMode === t.key ? 'active' : ''}
                              onClick={() => setListMode(t.key)}
                            >
                              {t.name}
                            </button>
                          ))}
                        </div>
                        <div className="search-input mission-search">
                          <Search size={14} />
                          <input
                            aria-label="搜索任务"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            placeholder="搜索编号、机体、需求点…"
                          />
                        </div>
                        <div className="mission-list">
                          {listMode === 'sorties' ? (
                            plan ? (
                              plan.sorties
                                .filter((r) =>
                                  JSON.stringify(r).toLowerCase().includes(search.toLowerCase()),
                                )
                                .map((r, i) => (
                                  <button
                                    className={`sortie-card ${route?.sortie_id === r.sortie_id ? 'selected' : ''}`}
                                    key={r.sortie_id}
                                    onClick={() => setSelected(r.sortie_id)}
                                    data-testid="sortie-card"
                                  >
                                    <div>
                                      <span className="sortie-number">
                                        {(i + 1).toString().padStart(2, '0')}
                                      </span>
                                      <strong>{r.drone_id}</strong>
                                      <Badge tone="teal">已规划</Badge>
                                    </div>
                                    <p>{r.visits.map((v) => v.site_id).join(' → ')}</p>
                                    <footer>
                                      <span>
                                        <Package size={12} />
                                        {r.cargo_ids.length} 箱
                                      </span>
                                      <span>
                                        <Clock3 size={12} />
                                        {clock(r.takeoff_s).slice(0, 5)}
                                      </span>
                                      <i style={{ background: colorFor(r.drone_id) }} />
                                    </footer>
                                  </button>
                                ))
                            ) : (
                              <Empty
                                icon={<Drone size={23} />}
                                title="等待生成架次"
                                description="点击生成方案，查看具体的箱件、机体和电池安排。"
                              />
                            )
                          ) : listMode === 'demands' ? (
                            (viewScenario || scenario).demands
                              .filter((d) =>
                                JSON.stringify(d).toLowerCase().includes(search.toLowerCase()),
                              )
                              .map((d) => {
                                const r = plan?.sorties.find((r) =>
                                  r.cargo_ids.some(
                                    (cid) =>
                                      (viewScenario || scenario).cargo_items.find(
                                        (c) => c.cargo_id === cid,
                                      )?.demand_id === d.demand_id,
                                  ),
                                )
                                return (
                                  <button
                                    className="demand-row"
                                    key={d.demand_id}
                                    onClick={() => r && setSelected(r.sortie_id)}
                                  >
                                    <span className="demand-icon">
                                      <Package size={16} />
                                    </span>
                                    <div>
                                      <strong>
                                        {d.site_id} · {category[d.cargo_type] || d.cargo_type}
                                      </strong>
                                      <small>
                                        {d.required_quantity}箱 ·{' '}
                                        {d.hard_deadline_s != null
                                          ? '硬截止 ' + duration(d.hard_deadline_s)
                                          : '期望 ' + duration(d.expected_deadline_s)}
                                      </small>
                                    </div>
                                    <i className={r ? 'teal' : ''} />
                                  </button>
                                )
                              })
                          ) : (
                            (viewScenario || scenario).cargo_items
                              .filter((c) =>
                                JSON.stringify(c).toLowerCase().includes(search.toLowerCase()),
                              )
                              .map((c) => (
                                <button
                                  className="cargo-row"
                                  key={c.cargo_id}
                                  onClick={() => {
                                    const id = cargoAssignments.get(c.cargo_id)
                                    if (id) setSelected(id)
                                  }}
                                >
                                  <Box size={15} />
                                  <div>
                                    <strong>{c.cargo_id}</strong>
                                    <small>
                                      {number(c.mass_kg, 1)} kg · {number(c.volume_l, 1)} L
                                    </small>
                                  </div>
                                  <Badge
                                    tone={cargoAssignments.has(c.cargo_id) ? 'teal' : 'neutral'}
                                  >
                                    {cargoAssignments.has(c.cargo_id) ? '已安排' : '库存'}
                                  </Badge>
                                </button>
                              ))
                          )}
                        </div>
                        <footer className="mission-footer">
                          <span className="connection-dot" />
                          稳定ID跨视图联动
                        </footer>
                      </section>
                      <section className="panel map-panel">
                        <RescueMap
                          scenario={viewScenario || scenario}
                          plan={plan}
                          selected={route?.sortie_id || null}
                          onSelect={setSelected}
                          playTime={playTime}
                          playback={playback.data}
                        />
                        {plan && (
                          <div className="playback">
                            <button
                              className="play-button"
                              aria-label={playing ? '暂停计划回放' : '播放计划回放'}
                              onClick={() => {
                                if (playTime == null || playTime >= plan.metrics.makespan_s!)
                                  setPlayTime(0)
                                setPlaying(!playing)
                              }}
                            >
                              {playing ? <Pause size={13} /> : <Play size={13} />}
                            </button>
                            <span>{clock(playTime || 0)}</span>
                            <input
                              aria-label="计划回放时钟"
                              type="range"
                              min="0"
                              max={plan.metrics.makespan_s!}
                              value={playTime || 0}
                              onChange={(e) => setPlayTime(Number(e.target.value))}
                            />
                            <small>计划示意回放</small>
                            <Badge>非执行事实</Badge>
                          </div>
                        )}
                      </section>
                      <aside className="strategy-column">
                        <section className="panel strategy-panel">
                          <div className="panel-heading">
                            <div>
                              <h3>策略方案</h3>
                              <p>同一快照 · 相同保障要求 · {policyLabel(strategyPolicy)}</p>
                            </div>
                            <Layers size={16} />
                          </div>
                          {(['time', 'energy'] as const).map((objective) => {
                            const p =
                              plan?.objective === objective
                                ? plan
                                : comparisonPlans.find(
                                    (p) =>
                                      p?.snapshot_id === plan?.snapshot_id &&
                                      p?.objective === objective,
                                  ) || null
                            return (
                              <div
                                className={`strategy-card ${plan?.objective === objective ? 'strategy-active' : ''}`}
                                key={objective}
                              >
                                <div>
                                  <span className={`strategy-icon ${objective}`}>
                                    {objective === 'time' ? (
                                      <Clock3 size={16} />
                                    ) : (
                                      <Leaf size={16} />
                                    )}
                                  </span>
                                  <strong>{objectiveLabels[objective]}</strong>
                                  {plan?.objective === objective && <CheckCircle2 size={15} />}
                                </div>
                                <p>{strategyDescription(objective, p || strategyPolicy)}</p>
                                {p ? (
                                  <>
                                    <div className="strategy-metrics">
                                      <span>{duration(strategyMetrics(p).makespan_s)}</span>
                                      <span>{number(strategyMetrics(p).energy_kwh, 2)} kWh</span>
                                    </div>
                                    <StrategyFacts plan={p} />
                                    <button onClick={() => choosePlan(p.plan_id)}>
                                      {p.plan_id === plan?.plan_id ? '当前展示方案' : '查看此方案'}
                                      <ChevronRight size={12} />
                                    </button>
                                  </>
                                ) : (
                                  <button
                                    disabled={
                                      isBusy ||
                                      bindingUnavailable ||
                                      stale ||
                                      comparisonLoading ||
                                      comparisonError ||
                                      scenario.data_origin === 'mock'
                                    }
                                    onClick={() => void runSolver(objective)}
                                  >
                                    {objective === 'time' ? '真实计算时间策略' : '真实计算此策略'}{' '}
                                    <ArrowRight size={12} />
                                  </button>
                                )}
                              </div>
                            )
                          })}
                          <div
                            className={`balanced-strategy ${plan?.objective === 'balanced' ? 'is-active' : ''}`}
                            title={strategyDescription('balanced', balancedPlan || strategyPolicy)}
                          >
                            <div>
                              <Scale size={15} />
                              <strong>时间能耗折中</strong>
                              <small>
                                {policyOf(balancedPlan || strategyPolicy) === 'tradeoff_v2'
                                  ? '每 1 kWh 折合 300 秒'
                                  : '旧版 · 先减期望延期'}
                              </small>
                            </div>
                            {balancedPlan ? (
                              <>
                                <span>
                                  {balancedPlan.joint_metrics ? '联合 · ' : ''}
                                  {duration(
                                    balancedPlan.joint_metrics?.joint_makespan_s ??
                                      balancedPlan.metrics.makespan_s,
                                  )}{' '}
                                  ·{' '}
                                  {number(
                                    balancedPlan.joint_metrics?.joint_energy_kwh ??
                                      balancedPlan.metrics.energy_kwh,
                                    2,
                                  )}{' '}
                                  kWh
                                </span>
                                <StrategyFacts plan={balancedPlan} />
                                <button onClick={() => choosePlan(balancedPlan.plan_id)}>
                                  {plan?.plan_id === balancedPlan.plan_id
                                    ? '当前折中方案'
                                    : '查看折中方案'}
                                  <ChevronRight size={12} />
                                </button>
                              </>
                            ) : (
                              <button
                                disabled={
                                  isBusy ||
                                  bindingUnavailable ||
                                  stale ||
                                  comparisonLoading ||
                                  comparisonError ||
                                  scenario.data_origin === 'mock'
                                }
                                onClick={() => void runSolver('balanced')}
                              >
                                真实计算折中策略
                                <ArrowRight size={12} />
                              </button>
                            )}
                          </div>
                          {comparisonLoading && (
                            <p className="strategy-footnote">正在读取同快照保存的策略方案…</p>
                          )}
                          {comparisonError && (
                            <button
                              className="strategy-read-retry"
                              onClick={() => comparisonQueries.forEach((q) => void q.refetch())}
                            >
                              保存方案读取失败，点击重试
                            </button>
                          )}
                          <div className="strategy-policy-note">
                            <strong>
                              {plan?.joint_metrics
                                ? '全部卡片使用运输 + 通信联合口径'
                                : '全部卡片使用运输口径'}
                            </strong>
                            <p>
                              硬截止、容量、SOC
                              与完整物资保障不可突破；期望截止是软目标，节能可能增加延期。折中权重为
                              300 秒/kWh，不代表服务区保障公平。
                            </p>
                            <p>
                              {equalityExplanation(
                                [plan, ...comparisonPlans].filter(
                                  (p): p is NonNullable<typeof p> => !!p,
                                ),
                              ) ||
                                '不同目标可以得到相同结果；请先计算同快照、同规则的三个策略，再核对排程和交付分析。'}
                            </p>
                            <small>
                              限时搜索的已验证候选，未证明全局最优；费用未配置，不显示人民币。
                            </small>
                            {plan && policyOf(plan) === 'deadline_first_v1' && (
                              <Button
                                disabled={
                                  isBusy ||
                                  stale ||
                                  bindingUnavailable ||
                                  scenario.data_origin === 'mock'
                                }
                                onClick={() => void runSolver(plan?.objective || 'time')}
                              >
                                按新规则重新计算
                              </Button>
                            )}
                          </div>
                        </section>
                        {route && (
                          <section className="panel sortie-detail">
                            <div className="panel-heading">
                              <div>
                                <h3>选中架次</h3>
                                <p className="mono">{route.sortie_id}</p>
                              </div>
                              <span
                                className="drone-chip"
                                style={{ color: colorFor(route.drone_id) }}
                              >
                                {route.drone_id}
                              </span>
                            </div>
                            <div className="route-stops">
                              <div>
                                <i />
                                <span>基地准备</span>
                                <strong>{clock(route.prepare_start_s)}</strong>
                              </div>
                              {route.visits.map((v) => (
                                <div key={v.site_id}>
                                  <i />
                                  <span>
                                    {v.site_id} · {v.cargo_ids.length}箱交接
                                  </span>
                                  <strong>{clock(v.delivery_complete_s)}</strong>
                                </div>
                              ))}
                              <div>
                                <i />
                                <span>返回基地</span>
                                <strong>{clock(route.return_s)}</strong>
                              </div>
                            </div>
                            <div className="detail-grid">
                              <div>
                                <small>使用电池</small>
                                <strong>{route.battery_id}</strong>
                              </div>
                              <div>
                                <small>预计能耗</small>
                                <strong>{number(route.energy_kwh, 3)} kWh</strong>
                              </div>
                              <div>
                                <small>返航SOC</small>
                                <strong>{percent(route.return_soc)}</strong>
                              </div>
                              <div>
                                <small>装载箱件</small>
                                <strong>{route.cargo_ids.length} 箱</strong>
                              </div>
                            </div>
                            <button className="detail-link" onClick={() => setListMode('cargo')}>
                              在箱件清单中追踪 <ArrowRight size={12} />
                            </button>
                          </section>
                        )}
                      </aside>
                    </div>
                  )}
                  {plan && !(page === 'events' && eventTab !== 'events') && (
                    <ResourceTimeline
                      scenario={viewScenario || scenario}
                      plan={plan}
                      selected={route?.sortie_id || null}
                      onSelect={setSelected}
                    />
                  )}
                  {plan?.communication_report &&
                    viewScenario &&
                    !(page === 'events' && eventTab !== 'events') && (
                      <CommunicationPanel
                        plan={plan}
                        scenario={viewScenario}
                        selected={selected}
                        onSelect={setSelected}
                      />
                    )}
                  <div className="workspace-footer">
                    <div>
                      <ShieldCheck size={15} />
                      <span>
                        {plan
                          ? '独立检查已完成 · 仅在声明模型范围内可行'
                          : '生成真实方案后，将独立复核箱件、资源、能量与时限'}
                      </span>
                      <button onClick={() => setScopeOpen(true)}>查看适用范围</button>
                    </div>
                    <div>
                      {plan && (
                        <>
                          <a
                            className="button button-default"
                            href={api.exportUrl(plan.plan_id, 'csv')}
                          >
                            <ArrowDownToLine size={14} />
                            任务CSV
                          </a>
                          <a
                            className="button button-default"
                            href={api.exportUrl(plan.plan_id, 'geojson')}
                          >
                            <Globe2 size={14} />
                            GeoJSON
                          </a>
                          <a
                            className="button button-default"
                            href={api.exportUrl(plan.plan_id, 'json')}
                          >
                            <FileDown size={14} />
                            计划JSON
                          </a>
                          <a
                            className="button button-default"
                            href={api.reportUrl(plan.plan_id)}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            <FileDown size={14} />
                            打印报告
                          </a>
                          <Button
                            variant="primary"
                            disabled={stale || !plan.has_validated_plan || isBusy}
                            busy={confirming}
                            onClick={() => void confirm()}
                          >
                            <Check size={15} />
                            确认方案
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                </>
              )}
            </>
          )}
        </main>
      </div>
      <LocalProfileDialog
        open={profileOpen}
        onOpenChange={setProfileOpen}
        profile={profile}
        onSave={(p) => {
          saveProfile(p)
          notify('本机档案已保存。')
        }}
      />
      <Toasts
        messages={messages}
        dismiss={(id) => setMessages((items) => items.filter((t) => t.id !== id))}
      />
      <Modal
        title="独立检查报告"
        description="检查结果来自本次快照和真实方案重建；未评估项不会被当作通过。"
        open={validationOpen}
        onOpenChange={setValidationOpen}
        wide
      >
        {plan && (
          <>
            <div className="validation-summary">
              <ShieldCheck size={28} />
              <div>
                <strong>
                  {plan.validation.status === 'passed' ? '声明范围内检查通过' : '请检查以下问题'}
                </strong>
                <p>
                  {plan.plan_id} · {plan.snapshot_id} · v{plan.scenario_state_version}
                </p>
              </div>
              <Badge tone="teal">{statusLabel[plan.validation.status]}</Badge>
            </div>
            <div className="validation-checks">
              {plan.validation.checks.map((c, i) => (
                <div key={i}>
                  <span className={`check-icon ${c.status}`}>
                    {c.status === 'passed' ? (
                      <CheckCircle2 size={17} />
                    ) : (
                      <TriangleAlert size={17} />
                    )}
                  </span>
                  <div>
                    <strong>
                      {{
                        cargo_unique: '箱件唯一性',
                        capacity: '载重与容积',
                        inventory: '库存与站点',
                        aircraft: '机体占用',
                        battery: '电池与充电',
                        weather_window: '人工气象限值与窗口',
                        time_window: '时间与硬截止',
                        energy: '能耗与储备',
                        terrain: '地形净空',
                        communication: '连续通信',
                        restricted_zone: '限制区与缓冲',
                        ground_resource: '工位与充电端口',
                      }[c.code] || c.code}
                    </strong>
                    <p>{c.message}</p>
                  </div>
                  <Badge
                    tone={c.status === 'passed' ? 'teal' : c.status === 'failed' ? 'red' : 'amber'}
                  >
                    {statusLabel[c.status]}
                  </Badge>
                </div>
              ))}
            </div>
          </>
        )}
      </Modal>
      <Modal
        title="使用说明与模型边界"
        description="这是一套本地模拟和规划辅助系统，所有可行性只针对本次声明的模型与输入。"
        open={scopeOpen}
        onOpenChange={setScopeOpen}
        wide
      >
        <div className="scope-grid">
          <section>
            <h3>
              <Drone size={18} />
              可操作的真实闭环
            </h3>
            <p>
              导入或编辑场景 → 固定快照 → 独立进程真实求解 → 查看地图、箱件和资源时间轴 → 确认或导出
              → 记录未执行场景的资源退出或紧急需求，再按新版本重新规划。
            </p>
          </section>
          <section>
            <h3>
              <Database size={18} />
              输入与输出来源
            </h3>
            <p>
              默认演练数据为原题中5个较近服务区的32箱子集。原题入口保留15点80箱。页面方案来自当前后端算法，不是固定论文回放。
            </p>
          </section>
          <section>
            <h3>
              <ShieldCheck size={18} />
              当前模型
            </h3>
            <p>
              整箱、质量/容积、实体机体和电池、两段充电、硬截止、载荷相关能耗与返航储备。支持有限地面工位/端口及启用后的通信联合规划；强制DEM按闭像元检查净空，启发式结果不宣称全局最优。
            </p>
          </section>
          <section>
            <h3>
              <TriangleAlert size={18} />
              尚不构成的保证
            </h3>
            <p>
              没有实时风雨、建筑电线、全航程多机冲突、真实无线可靠性或实飞适航认证。通信未接入时不得强制声明已通过；未提供费率时费用为空。
            </p>
          </section>
        </div>
        <p className="callout">
          地图播放只改变展示时钟；确认只记录计划与资源预约，不写实际交付、不发送飞控指令。核心数据与线路可离线使用。
        </p>
      </Modal>
    </div>
  )
}
