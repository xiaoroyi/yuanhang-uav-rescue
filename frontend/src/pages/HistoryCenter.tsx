import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Activity,
  ArrowDownToLine,
  ArrowRight,
  Clock3,
  Database,
  FileCheck2,
  GitCompareArrows,
  History,
  Search,
  ShieldCheck,
} from 'lucide-react'
import { api, downloadJson, type Scenario, type PlanSummary } from '../api/client'
import { Badge, Button, Empty, Modal } from '../components/ui'
import { policyLabel } from '../lib/strategies'
import { duration, number } from '../lib/format'
import './history-compare.css'

export const preferenceName: Record<string, string> = {
  time: '时间优先',
  energy: '能耗优先',
  balanced: '时间能耗折中',
}
export const dateTime = (value: string) =>
  new Date(value).toLocaleString('zh-CN', { hour12: false })
const modeName = { quick: '快速调度', improve: '深入优化', replan: '动态重规划' }
function numeric(p: PlanSummary, key: string) {
  const n = p.metrics[key]
  return typeof n === 'number' && Number.isFinite(n) ? n : null
}

export function HistoryCenter({
  scenario,
  onOpenPlan,
  onOpenScene,
  onCompare,
}: {
  scenario: Scenario
  onOpenPlan: (id: string) => void
  onOpenScene: (id: string) => void
  onCompare: () => void
}) {
  const [tab, setTab] = useState<'plans' | 'jobs' | 'events' | 'scenes' | 'versions'>('plans')
  const [viewVersion, setViewVersion] = useState<number | null>(null)
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('all')
  const plans = useQuery({
    queryKey: ['plans', scenario.scenario_id],
    queryFn: () => api.plans(scenario.scenario_id),
  })
  const jobs = useQuery({
    queryKey: ['jobs', scenario.scenario_id],
    queryFn: () => api.jobs(scenario.scenario_id),
  })
  const events = useQuery({
    queryKey: ['events', scenario.scenario_id],
    queryFn: () => api.events(scenario.scenario_id),
  })
  const scenes = useQuery({ queryKey: ['scenarios'], queryFn: api.scenarios })
  const versions = useQuery({
    queryKey: ['versions', scenario.scenario_id, scenario.state_version],
    queryFn: () => api.scenarioVersions(scenario.scenario_id),
    enabled: tab === 'versions',
  })
  const version = useQuery({
    queryKey: ['version', scenario.scenario_id, viewVersion],
    queryFn: () => api.scenarioVersion(scenario.scenario_id, viewVersion!),
    enabled: viewVersion != null,
  })
  const rows = useMemo(
    () =>
      [...(plans.data || [])]
        .sort((a, b) => b.generated_at.localeCompare(a.generated_at))
        .filter(
          (p) =>
            (filter === 'all' ||
              (filter === 'confirmed' ? !!p.confirmed_at : p.algorithm_mode === filter)) &&
            `${p.plan_id} ${p.snapshot_id} ${preferenceName[p.objective]} v${p.scenario_state_version}`
              .toLowerCase()
              .includes(search.toLowerCase()),
        ),
    [plans.data, filter, search],
  )
  const activeQuery =
    tab === 'plans'
      ? plans
      : tab === 'jobs'
        ? jobs
        : tab === 'events'
          ? events
          : tab === 'versions'
            ? versions
            : scenes
  return (
    <section className="archive-page">
      <div className="experience-heading">
        <div>
          <div className="eyebrow">MISSION ARCHIVE</div>
          <h1>每一次决策，都有来路</h1>
          <p>方案、计算记录与事件保存在本机。打开历史方案时，地图和分析读取它自己的原始快照。</p>
        </div>
        <Button onClick={onCompare}>
          <GitCompareArrows size={16} />
          进入方案对比
        </Button>
      </div>
      <div className="archive-kpis">
        {[
          [FileCheck2, plans.data?.length ?? '—', '已保存方案'],
          [Clock3, jobs.data?.length ?? '—', '真实计算任务'],
          [Activity, events.data?.length ?? '—', '场景事件'],
          [Database, `v${scenario.state_version}`, '当前输入版本'],
        ].map(([Icon, count, label]) => {
          const I = Icon as typeof Database
          return (
            <div key={String(label)}>
              <I size={21} />
              <strong>{String(count)}</strong>
              <span>{String(label)}</span>
            </div>
          )
        })}
      </div>
      <div className="archive-tabs" role="tablist" aria-label="历史档案分类">
        {(
          [
            ['plans', '方案档案'],
            ['versions', '输入版本'],
            ['jobs', '计算记录'],
            ['events', '事件时间线'],
            ['scenes', '场景库'],
          ] as const
        ).map(([id, label]) => (
          <button key={id} role="tab" aria-selected={tab === id} onClick={() => setTab(id)}>
            {label}
          </button>
        ))}
      </div>
      {activeQuery.isError ? (
        <Empty
          icon={<History />}
          title="档案暂时无法读取"
          description={activeQuery.error.message}
          action={<Button onClick={() => void activeQuery.refetch()}>重试</Button>}
        />
      ) : activeQuery.isLoading ? (
        <p className="archive-loading">正在读取本机保存记录…</p>
      ) : (
        <>
          {tab === 'plans' && (
            <>
              <div className="archive-toolbar">
                <label className="archive-search">
                  <Search size={16} />
                  <input
                    aria-label="搜索历史方案"
                    placeholder="搜索方案、快照、策略或版本"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                  />
                </label>
                <select
                  aria-label="筛选历史方案"
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                >
                  <option value="all">全部方案</option>
                  <option value="confirmed">已确认</option>
                  <option value="quick">快速调度</option>
                  <option value="improve">深入优化</option>
                  <option value="replan">重规划</option>
                </select>
              </div>
              {rows.length ? (
                <div className="archive-plan-grid">
                  {rows.map((p) => (
                    <article className="archive-plan-card" key={p.plan_id}>
                      <div className="archive-card-top">
                        <span className={`archive-objective objective-${p.objective}`}>
                          {preferenceName[p.objective] || p.objective}
                        </span>
                        <Badge tone={p.confirmed_at ? 'teal' : 'neutral'}>
                          {p.confirmed_at ? '已确认' : '候选方案'}
                        </Badge>
                      </div>
                      <h3>
                        {modeName[p.algorithm_mode]} <small>v{p.scenario_state_version}</small>
                      </h3>
                      <p className="archive-time">
                        {dateTime(p.generated_at)} · {policyLabel(p)}
                      </p>
                      <div className="archive-card-metrics">
                        <div>
                          <small>最后返航</small>
                          <strong>{duration(numeric(p, 'makespan_s'))}</strong>
                        </div>
                        <div>
                          <small>运输能耗</small>
                          <strong>
                            {number(numeric(p, 'energy_kwh'), 2)} <em>kWh</em>
                          </strong>
                        </div>
                        <div>
                          <small>运输架次</small>
                          <strong>{number(numeric(p, 'sortie_count'), 0)}</strong>
                        </div>
                      </div>
                      <div className="archive-identities">
                        <span>
                          方案 <code>{p.plan_id}</code>
                        </span>
                        <span>
                          快照 <code>{p.snapshot_id}</code>
                        </span>
                      </div>
                      <div className="archive-card-footer">
                        <span>
                          <ShieldCheck size={13} />
                          {p.solver_status} · 独立检查
                        </span>
                        <Button onClick={() => onOpenPlan(p.plan_id)}>
                          打开方案
                          <ArrowRight size={14} />
                        </Button>
                      </div>
                      <a className="archive-download" href={api.exportUrl(p.plan_id, 'json')}>
                        <ArrowDownToLine size={13} />
                        下载原始计划JSON
                      </a>
                    </article>
                  ))}
                </div>
              ) : (
                <Empty
                  icon={<FileCheck2 />}
                  title={plans.data?.length ? '没有匹配的方案' : '还没有保存方案'}
                  description="在调度工作台完成真实求解后，方案自动保存到这里。"
                />
              )}
            </>
          )}
          {tab === 'jobs' &&
            (jobs.data?.length ? (
              <div className="archive-table-wrap">
                <table className="archive-table">
                  <thead>
                    <tr>
                      <th>计算任务</th>
                      <th>开始时间</th>
                      <th>状态</th>
                      <th>求解耗时</th>
                      <th>结果与原因</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[...jobs.data]
                      .sort((a, b) => b.created_at.localeCompare(a.created_at))
                      .map((j) => (
                        <tr key={j.job_id}>
                          <td>
                            <code>{j.job_id}</code>
                            <small>{j.snapshot_id}</small>
                          </td>
                          <td>{dateTime(j.created_at)}</td>
                          <td>
                            <Badge
                              tone={
                                j.has_validated_plan
                                  ? 'teal'
                                  : j.job_state === 'failed'
                                    ? 'red'
                                    : 'amber'
                              }
                            >
                              {
                                {
                                  queued: '排队中',
                                  running: '运行中',
                                  completed: '已完成',
                                  failed: '失败',
                                  canceled: '已取消',
                                }[j.job_state]
                              }
                            </Badge>
                            <small>{j.solver_status || '—'}</small>
                          </td>
                          <td>{j.runtime_s == null ? '—' : `${number(j.runtime_s, 2)} 秒`}</td>
                          <td>
                            {j.plan_id ? (
                              <Button onClick={() => onOpenPlan(j.plan_id!)}>
                                查看真实方案
                                <ArrowRight size={13} />
                              </Button>
                            ) : (
                              <span>{j.error?.message || j.stop_reason || '尚未发布可行方案'}</span>
                            )}
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <Empty
                icon={<Clock3 />}
                title="暂无计算记录"
                description="排队、运行、成功、取消和失败的计算都会保留，UNKNOWN不会被改写成无解。"
              />
            ))}
          {tab === 'events' &&
            (events.data?.length ? (
              <ol className="archive-event-list">
                {[...events.data].reverse().map((e) => (
                  <li key={e.event_id}>
                    <span className="archive-event-dot" />
                    <div>
                      <Badge tone="amber">
                        {e.event_type === 'demand.added' ? '紧急需求' : '资源退出'}
                      </Badge>
                      <h3>
                        {e.event_type === 'demand.added'
                          ? `新增 ${e.payload.demand.required_quantity} 箱需求`
                          : e.event_type === 'drone.unavailable'
                            ? `机体 ${e.payload.drone_id} 退出`
                            : e.event_type === 'battery.unavailable'
                              ? `运输电池 ${e.payload.battery_id} 退出`
                              : `中继能源 ${e.payload.component_id} 退出`}
                      </h3>
                      <p>{e.reason || '未填写原因'}</p>
                      <small>
                        {dateTime(e.occurred_at)} · <code>{e.event_id}</code>
                      </small>
                      <button
                        className="archive-text-action"
                        onClick={() => downloadJson(e, `${e.event_id}.json`)}
                      >
                        下载事件记录
                      </button>
                    </div>
                  </li>
                ))}
              </ol>
            ) : (
              <Empty
                icon={<Activity />}
                title="场景尚无事件"
                description="在事件复盘中注入资源退出或紧急需求后，这里会保留原始事件记录。"
              />
            ))}
          {tab === 'versions' && (
            <section className="experience-chart-panel">
              <div className="experience-chart-title">
                <h3>不可变输入版本</h3>
                <small>只读查看和下载，打开版本不会覆盖当前场景</small>
              </div>
              <div className="archive-table-wrap">
                <table className="archive-table">
                  <thead>
                    <tr>
                      <th>输入版本</th>
                      <th>场景名称</th>
                      <th>需求点 / 库存 / 机体 / 电池</th>
                      <th>内容指纹</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    {versions.data?.map((v) => (
                      <tr key={v.state_version}>
                        <td>
                          <Badge
                            tone={v.state_version === scenario.state_version ? 'blue' : 'neutral'}
                          >
                            v{v.state_version}
                            {v.state_version === scenario.state_version ? ' · 当前' : ''}
                          </Badge>
                        </td>
                        <td>
                          {v.name}
                          <small>
                            {v.created_at ? dateTime(v.created_at) : '此版本未记录时间'}
                          </small>
                        </td>
                        <td>
                          {v.site_count} / {v.cargo_count} / {v.drone_count} / {v.battery_count}
                        </td>
                        <td>
                          <code title={v.content_hash}>{v.content_hash.slice(0, 16)}…</code>
                        </td>
                        <td>
                          <Button onClick={() => setViewVersion(v.state_version)}>
                            查看版本
                            <ArrowRight size={13} />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p className="chart-note">
                资源数量是保存输入的实体总数，可用状态以版本内容为准。版本时间缺失时保留未知，不借用场景最近更新时间。
              </p>
            </section>
          )}
          {tab === 'scenes' && (
            <div className="archive-plan-grid">
              {scenes.data?.map((s) => (
                <article className="archive-plan-card" key={s.scenario_id}>
                  <div className="archive-card-top">
                    <Badge tone={s.scenario_id === scenario.scenario_id ? 'blue' : 'neutral'}>
                      {s.scenario_id === scenario.scenario_id ? '当前场景' : `v${s.state_version}`}
                    </Badge>
                    <Database size={18} />
                  </div>
                  <h3>{s.name}</h3>
                  <p>
                    {s.site_count}个点位 · {s.cargo_count}箱 · {s.drone_count}架运输机
                  </p>
                  <p className="archive-time">更新于 {dateTime(s.updated_at)}</p>
                  <code className="archive-scene-id">{s.scenario_id}</code>
                  <Button onClick={() => onOpenScene(s.scenario_id)}>
                    进入场景
                    <ArrowRight size={14} />
                  </Button>
                </article>
              ))}
            </div>
          )}
        </>
      )}
      <p className="archive-footnote">
        <ShieldCheck size={14} />{' '}
        数据保存在本机数据库，刷新不会清空。输入编辑保存在版本记录，方案档案只包含真实生成的计算结果。
      </p>
      <Modal
        open={viewVersion != null}
        onOpenChange={(open) => {
          if (!open) setViewVersion(null)
        }}
        title={`输入版本 v${viewVersion ?? ''} · 只读预览`}
        description="读取当时保存的完整输入，不执行恢复、不写入当前场景，历史Plan仍绑定原快照。"
        wide
      >
        {version.isError ? (
          <p role="alert">{version.error.message}</p>
        ) : version.isLoading ? (
          <p className="archive-loading">正在读取版本…</p>
        ) : (
          version.data && (
            <>
              <div className="archive-version-summary">
                <strong>{version.data.name}</strong>
                <p>
                  {version.data.sites.length}个需求点 · {version.data.cargo_items.length}箱库存 ·{' '}
                  {version.data.drones.length}架运输机 · {version.data.batteries.length}块电池
                </p>
                <Button
                  onClick={() =>
                    downloadJson(version.data, `${scenario.scenario_id}-v${viewVersion}.json`)
                  }
                >
                  <ArrowDownToLine size={14} />
                  下载该版本JSON
                </Button>
              </div>
              <details className="archive-version-json">
                <summary>展开完整原始输入</summary>
                <pre>{JSON.stringify(version.data, null, 2)}</pre>
              </details>
            </>
          )
        )}
      </Modal>
    </section>
  )
}
