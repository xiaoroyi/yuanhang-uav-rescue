import { useEffect, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  ArrowRight,
  Archive,
  BookOpen,
  ChevronLeft,
  CircleHelp,
  Copy,
  FlaskConical,
  Home,
  Layers3,
  ListChecks,
  MapPin,
  Moon,
  Plane,
  Plus,
  Search,
  Settings2,
  Sun,
} from 'lucide-react'
import { api } from '../api/client'
import { ops, key, type Mission } from '../api/operations'
import { Button, Empty, Modal, Toasts, type ToastMessage } from '../components/ui'
import { LocalProfileDialog, useLocalProfile } from '../components/LocalProfile'
import LegacyApp from '../App'
import { MissionWorkspace } from './MissionWorkspace'
import { ResourceCenter } from './ResourceCenter'
import { ExperimentCenter } from './ExperimentCenter'
import { UIContext } from '../components/UIContext'
import './operations.css'

export function navigate(path: string) {
  location.hash = path
}
export const stageLabel = {
  draft: '准备中',
  planning: '方案规划',
  ready: '待演练',
  executing: '演练运行中',
  paused: '演练已暂停',
  completed: '已结束',
  archived: '已归档',
}
const actionLabel = {
  prepare: '继续准备',
  plans: '查看方案',
  execute: '进入执行',
  review: '查看复盘',
}
function route() {
  return location.hash.replace(/^#\/?/, '') || 'home'
}
const legacyRoutes = [
  'workspace',
  'scenario',
  'events',
  'analysis',
  'maps',
  'history',
  'compare',
  'guide',
  'schedule',
]

export default function OperationsApp() {
  const [path, setPath] = useState(route)
  const inLegacy = legacyRoutes.includes(path)
  const [createOpen, setCreateOpen] = useState(false)
  const [template, setTemplate] = useState<'blank' | 'compact' | 'contest'>('blank')
  const [name, setName] = useState('')
  const [busy, setBusy] = useState(false)
  const [messages, setMessages] = useState<ToastMessage[]>([])
  const [profileOpen, setProfileOpen] = useState(false)
  const { profile, saveProfile } = useLocalProfile()
  const [theme, setTheme] = useState(() => localStorage.getItem('yuanhang-v2-theme') || 'light')
  const query = useQueryClient()
  const missions = useQuery({
    queryKey: ['missions'],
    queryFn: ops.missions,
    refetchInterval: 5000,
  })
  const health = useQuery({ queryKey: ['health'], queryFn: api.health, refetchInterval: 10000 })
  useEffect(() => {
    const read = () => setPath(route())
    addEventListener('hashchange', read)
    return () => removeEventListener('hashchange', read)
  }, [])
  useEffect(() => {
    if (inLegacy) return
    document.documentElement.dataset.theme = theme
    document.documentElement.dataset.motion = 'off'
    localStorage.setItem('yuanhang-v2-theme', theme)
  }, [theme, inLegacy])
  const notify = (message: string, error = false) =>
    setMessages((m) => [
      ...m.slice(-3),
      {
        id: Math.max(Date.now(), (m.at(-1)?.id || 0) + 1),
        message,
        tone: error ? 'error' : 'success',
      },
    ])
  useEffect(() => {
    if (!messages.length) return
    const first = messages[0]
    const delay = Math.max(0, first.id + (first.tone === 'error' ? 12000 : 4500) - Date.now())
    const timer = window.setTimeout(
      () => setMessages((current) => current.filter((m) => m.id !== first.id)),
      delay,
    )
    return () => window.clearTimeout(timer)
  }, [messages])
  const refresh = () => {
    void query.invalidateQueries({ queryKey: ['missions'] })
    void query.invalidateQueries({ queryKey: ['mission'] })
  }
  const match = /^missions\/([^/]+)(?:\/(prepare|plans|execute|review))?/.exec(path)
  const inMission = !!match && match[1] !== 'new'
  const current = missions.data?.find((m) => m.mission_id === match?.[1])
  const nav = [
    { path: 'home', title: '首页', icon: Home },
    { path: 'missions', title: '救援任务', icon: ListChecks },
    { path: 'resources', title: '资源中心', icon: Layers3 },
    { path: 'experiments', title: '演练评测', icon: FlaskConical },
  ]
  async function create() {
    setBusy(true)
    try {
      const m = await ops.create({
        name:
          name.trim() ||
          (template === 'blank'
            ? '新建救援任务'
            : template === 'compact'
              ? '小规模救援演练'
              : '原题回归演练'),
        template,
        idempotency_key: key(),
        mode: 'simulation',
      })
      refresh()
      setCreateOpen(false)
      setName('')
      navigate(`missions/${m.mission_id}/prepare`)
    } catch (e) {
      notify((e as Error).message, true)
    } finally {
      setBusy(false)
    }
  }
  function newTask(t: typeof template) {
    setTemplate(t)
    setCreateOpen(true)
  }
  if (inLegacy)
    return (
      <>
        <a className="v2-return" href="#/home">
          <ChevronLeft size={14} />
          返回新版首页
        </a>
        <LegacyApp />
      </>
    )
  return (
    <UIContext.Provider value="v2">
      <div className={`v2-app ${inMission ? 'mission-shell' : ''}`}>
        <aside className="v2-sidebar">
          <a className="v2-brand" href="#/home" aria-label="援航首页">
            <span>
              <Plane size={24} />
            </span>
            <b>
              援航<small>救援任务协同</small>
            </b>
          </a>
          <nav aria-label="主要导航">
            {nav.map((n) => (
              <a
                key={n.path}
                href={`#/${n.path}`}
                title={n.title}
                className={path === n.path || (n.path === 'missions' && inMission) ? 'active' : ''}
              >
                <n.icon size={19} />
                <span>{n.title}</span>
              </a>
            ))}
          </nav>
          <div className="v2-sidebar-bottom">
            <a href="#/settings" title="设置与接入">
              <Settings2 size={18} />
              <span>设置与接入</span>
            </a>
            <a href="#/help" title="使用帮助">
              <CircleHelp size={18} />
              <span>使用帮助</span>
            </a>
            <button onClick={() => setProfileOpen(true)} title="本机档案">
              <i>{profile.displayName.slice(0, 1)}</i>
              <span>{profile.displayName}</span>
            </button>
          </div>
        </aside>
        <div className="v2-main">
          <header className="v2-topbar">
            <div>
              <a href="#/home">救援工作空间</a>
              {inMission && (
                <>
                  <span>/</span>
                  <a href="#/missions">救援任务</a>
                  <span>/</span>
                  <b>{current?.name || '加载任务…'}</b>
                </>
              )}
            </div>
            <div>
              <span className={`v2-service ${health.isError ? 'offline' : ''}`}>
                {health.isError ? '本机服务不可用' : health.data ? '本机服务已连接' : '连接中…'}
              </span>
              <button
                className="icon-button"
                aria-label="切换主题"
                onClick={() => setTheme(theme === 'light' ? 'midnight' : 'light')}
              >
                {theme === 'light' ? <Moon size={17} /> : <Sun size={17} />}
              </button>
              <a href="#/help" aria-label="帮助">
                <CircleHelp size={18} />
              </a>
            </div>
          </header>
          {inMission ? (
            <MissionWorkspace
              key={match[1]}
              missionId={match[1]}
              stage={(match[2] || 'prepare') as 'prepare' | 'plans' | 'execute' | 'review'}
              notify={notify}
            />
          ) : path === 'resources' ? (
            <ResourceCenter notify={notify} />
          ) : path === 'experiments' ? (
            <ExperimentCenter
              missions={missions.data || []}
              onNew={() => newTask('compact')}
              notify={notify}
            />
          ) : path === 'settings' ? (
            <Settings />
          ) : path === 'help' ? (
            <Help />
          ) : (
            <MissionHome
              missions={missions.data || []}
              loading={missions.isPending}
              error={missions.error}
              list={path === 'missions'}
              onNew={newTask}
              notify={notify}
              onRefresh={refresh}
            />
          )}
        </div>
        <Modal
          title="新建救援任务"
          description="创建独立模拟任务。只保存输入，不复制其他任务的执行事实。"
          open={createOpen}
          onOpenChange={setCreateOpen}
        >
          <form
            className="v2-create-form"
            onSubmit={(e) => {
              e.preventDefault()
              void create()
            }}
          >
            <label>
              任务名称
              <input
                autoFocus
                value={name}
                maxLength={120}
                placeholder="例如：镇龙乡山洪应急运输"
                onChange={(e) => setName(e.target.value)}
              />
            </label>
            <fieldset>
              <legend>从哪里开始</legend>
              {(
                [
                  { value: 'blank', title: '空白任务', text: '自行配置基地、需求和资源' },
                  {
                    value: 'compact',
                    title: '小规模入门演练',
                    text: '5 个需求点 · 32 箱 · 独立副本',
                  },
                  {
                    value: 'contest',
                    title: '原题回归演练',
                    text: '15 个需求点 · 80 箱 · 原题模型',
                  },
                ] as const
              ).map((t) => (
                <label
                  className={`v2-template ${template === t.value ? 'active' : ''}`}
                  key={t.value}
                >
                  <input
                    type="radio"
                    name="template"
                    checked={template === t.value}
                    onChange={() => setTemplate(t.value)}
                  />
                  <span>
                    <b>{t.title}</b>
                    <small>{t.text}</small>
                  </span>
                </label>
              ))}
            </fieldset>
            <p className="v2-subtle">运行类型：仿真演练 · 本机计算 · 资源与交付账本隔离</p>
            <div className="v2-form-actions">
              <Button onClick={() => setCreateOpen(false)} type="button">
                取消
              </Button>
              <Button variant="primary" busy={busy} type="submit">
                创建并准备任务
                <ArrowRight size={15} />
              </Button>
            </div>
          </form>
        </Modal>
        <LocalProfileDialog
          open={profileOpen}
          onOpenChange={setProfileOpen}
          profile={profile}
          onSave={saveProfile}
        />
        <Toasts
          messages={messages}
          dismiss={(id) => setMessages((m) => m.filter((x) => x.id !== id))}
        />
      </div>
    </UIContext.Provider>
  )
}

function MissionHome({
  missions,
  loading,
  error,
  list,
  onNew,
  notify,
  onRefresh,
}: {
  missions: Mission[]
  loading: boolean
  error: Error | null
  list: boolean
  onNew: (t: 'blank' | 'compact' | 'contest') => void
  notify: (m: string, e?: boolean) => void
  onRefresh: () => void
}) {
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('active')
  const legacy = useQuery({ queryKey: ['scenarios'], queryFn: api.scenarios })
  const rows = missions.filter(
    (m) =>
      (filter === 'archived'
        ? m.lifecycle === 'archived'
        : filter === 'all' || m.lifecycle !== 'archived') &&
      `${m.name} ${m.mission_id}`.toLowerCase().includes(search.toLowerCase()),
  )
  const recent = missions.find((m) => m.lifecycle !== 'archived')
  return (
    <main className="v2-content">
      <div className="v2-page-heading">
        <div>
          <h1>{list ? '救援任务' : '救援工作首页'}</h1>
          <p>
            {list ? '管理输入、方案、运行与复盘记录。' : '从任务准备到模拟复盘，在同一任务中完成。'}
          </p>
        </div>
        <Button variant="primary" onClick={() => onNew('blank')}>
          <Plus size={17} />
          新建救援任务
        </Button>
      </div>
      {!list && (
        <div className="v2-quick-grid">
          <button
            onClick={() =>
              recent
                ? navigate(`missions/${recent.mission_id}/${recent.next_action}`)
                : onNew('blank')
            }
          >
            <ListChecks size={23} />
            <span>
              <b>{recent ? '继续上次任务' : '开始第一个任务'}</b>
              <small>{recent?.name || '先保存草稿，再逐步补齐条件'}</small>
            </span>
            <ArrowRight size={18} />
          </button>
          <button onClick={() => onNew('compact')}>
            <FlaskConical size={23} />
            <span>
              <b>运行示例演练</b>
              <small>5 点 32 箱，体验计算与中途调整</small>
            </span>
            <ArrowRight size={18} />
          </button>
          <a href="#/help">
            <BookOpen size={23} />
            <span>
              <b>快速上手</b>
              <small>准备 → 规划 → 模拟 → 复盘</small>
            </span>
            <ArrowRight size={18} />
          </a>
        </div>
      )}
      <section className="v2-card">
        <div className="v2-section-bar">
          <h2>
            任务记录 <span>{rows.length}</span>
          </h2>
          <div className="v2-table-tools">
            <label className="v2-search">
              <Search size={15} />
              <input
                aria-label="搜索救援任务"
                placeholder="搜索任务名称或编号"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </label>
            <select
              aria-label="任务筛选"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            >
              <option value="active">当前任务</option>
              <option value="all">全部记录</option>
              <option value="archived">已归档</option>
            </select>
            <Button onClick={() => navigate('missions')}>打开任务列表</Button>
          </div>
        </div>
        {error ? (
          <div className="v2-inline-error">
            {error.message}
            <Button onClick={onRefresh}>重试</Button>
          </div>
        ) : loading ? (
          <p className="v2-loading">正在读取任务…</p>
        ) : !rows.length ? (
          <Empty
            icon={<MapPin size={25} />}
            title="还没有救援任务"
            description="创建空白任务，或复制一个小规模案例开始演练。"
            action={<Button onClick={() => onNew('blank')}>创建第一个任务</Button>}
          />
        ) : (
          <div className="v2-table-scroll">
            <table className="v2-table">
              <thead>
                <tr>
                  <th>任务名称</th>
                  <th>运行类型</th>
                  <th>当前阶段</th>
                  <th>需求 / 库存</th>
                  <th>更新时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((m) => (
                  <tr key={m.mission_id}>
                    <td>
                      <a href={`#/missions/${m.mission_id}/${m.next_action}`}>
                        <b>{m.name}</b>
                      </a>
                      <small>{m.mission_id}</small>
                    </td>
                    <td>{m.mode === 'simulation' ? '仿真演练' : '规划辅助'}</td>
                    <td>
                      <span className={`v2-status status-${m.lifecycle}`}>
                        {stageLabel[m.lifecycle]}
                      </span>
                    </td>
                    <td>
                      {m.site_count} 点 / {m.cargo_count} 箱
                    </td>
                    <td>
                      {new Date(m.updated_at).toLocaleString('zh-CN', {
                        month: '2-digit',
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </td>
                    <td>
                      <div className="v2-row-actions">
                        <a href={`#/missions/${m.mission_id}/${m.next_action}`}>
                          {actionLabel[m.next_action]}
                          <ArrowRight size={13} />
                        </a>
                        <button
                          aria-label={`复制${m.name}`}
                          title="复制为演练"
                          onClick={() =>
                            void ops
                              .clone(m)
                              .then((n) => {
                                onRefresh()
                                navigate(`missions/${n.mission_id}/prepare`)
                              })
                              .catch((e: Error) => notify(e.message, true))
                          }
                        >
                          <Copy size={15} />
                        </button>
                        <button
                          aria-label={`归档${m.name}`}
                          title={m.lifecycle === 'archived' ? '取消归档' : '归档'}
                          onClick={() =>
                            void ops
                              .update(m, { archived: m.lifecycle !== 'archived' })
                              .then(onRefresh)
                              .catch((e: Error) => notify(e.message, true))
                          }
                        >
                          <Archive size={15} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
      {!!legacy.data?.some(
        (s) => !missions.some((m) => m.current_scenario_id === s.scenario_id),
      ) && (
        <details className="v2-card v2-legacy-list">
          <summary>已有 V1 场景与历史方案</summary>
          <p>关联既有输入；保留全部历史版本与方案。</p>
          {legacy.data
            .filter((s) => !missions.some((m) => m.current_scenario_id === s.scenario_id))
            .map((s) => (
              <div key={s.scenario_id}>
                <span>
                  {s.name}
                  <small>
                    {s.site_count} 点 · {s.cargo_count} 箱
                  </small>
                </span>
                <Button
                  onClick={() =>
                    void ops
                      .create({ name: s.name, scenario_id: s.scenario_id, idempotency_key: key() })
                      .then((m) => {
                        onRefresh()
                        navigate(`missions/${m.mission_id}/plans`)
                      })
                      .catch((e: Error) => notify(e.message, true))
                  }
                >
                  纳入救援任务
                </Button>
              </div>
            ))}
        </details>
      )}
    </main>
  )
}

function Settings() {
  return (
    <main className="v2-content">
      <div className="v2-page-heading">
        <h1>设置与接入</h1>
      </div>
      <section className="v2-card v2-settings">
        <h2>运行环境</h2>
        <dl>
          <dt>默认模式</dt>
          <dd>本机业务仿真，无需登录</dd>
          <dt>设备接入</dt>
          <dd>SimulationAdapter；SITL / 真机未配置</dd>
          <dt>气象</dt>
          <dd>支持人工情景、机型阈值与作业窗口；外部预报、风致能源和机型标定未绑定</dd>
          <dt>离线数据</dt>
          <dd>本地 DEM、地理上下文与前端依赖；卫星图需手动联网启用</dd>
          <dt>账户</dt>
          <dd>左下角本机档案仅保存展示姓名，不授予设备控制权限</dd>
        </dl>
        <p>真实设备接入需独立配置受支持适配器、服务端身份与现场许可。</p>
      </section>
    </main>
  )
}
function Help() {
  return (
    <main className="v2-content">
      <div className="v2-page-heading">
        <h1>使用帮助</h1>
      </div>
      <section className="v2-card v2-help">
        <h2>完成一次救援演练</h2>
        <ol>
          <li>
            <b>新建任务</b>
            <p>首次使用可选择小规模入门演练；空白任务从基地、需求和库存开始。</p>
          </li>
          <li>
            <b>任务准备</b>
            <p>
              依次核对区域基地、需求物资、机队保障；需求和实物库存分别录入，保存后运行条件检查。
            </p>
          </li>
          <li>
            <b>方案规划</b>
            <p>
              选择偏好生成方案。点击站点、航线或甘特条核对架次、箱件、时间和电池。确认方案只建立计划预约。
            </p>
          </li>
          <li>
            <b>执行跟踪</b>
            <p>
              创建并启动仿真，使用暂停和倍速。刷新会恢复服务器状态。中途变化先暂停，记录事件后生成调整并核对差异。
            </p>
          </li>
          <li>
            <b>复盘分析</b>
            <p>区分计划分配和模拟交付，查看时间轴、能源与事件；导出方案和执行记录。</p>
          </li>
        </ol>
        <div className="v2-help-note">
          计划预演仅用于查看，不产生交付；仿真演练写隔离账本；本机未连接真实设备。
        </div>
        <a href="#/home">
          返回首页
          <ArrowRight size={15} />
        </a>
      </section>
    </main>
  )
}
