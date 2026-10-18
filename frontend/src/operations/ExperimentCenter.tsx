import { useMemo, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Download, FlaskConical, Plus, Square, FileJson } from 'lucide-react'
import type { EChartsOption } from 'echarts'
import { api } from '../api/client'
import { ops, key, type Mission, type Experiment, type ExperimentBundle } from '../api/operations'
import { Button, Modal, Empty } from '../components/ui'
import { DataChart } from '../components/DataChart'
import { RescueMap } from '../components/RescueMap'
import { ResourceTimeline } from '../components/ResourceTimeline'
import { number, percent } from '../lib/format'
import { clock } from './format'

const objective = { time: '时间优先', energy: '能耗优先', balanced: '时间能耗折中' }
const method = { quick: '可行构造与规则搜索', improve: '有限路线池与 CP-SAT' }
const labels: Record<Experiment['status'], string> = {
  queued: '等待派发',
  running: '正在计算',
  completed: '已完成',
  canceled: '已取消',
}
type Notify = (message: string, error?: boolean) => void

export function ExperimentCenter({
  missions,
  onNew,
  notify,
}: {
  missions: Mission[]
  onNew: () => void
  notify: Notify
}) {
  const cache = useQueryClient()
  const [sourceId, setSourceId] = useState('')
  const [suite, setSuite] = useState<'strategy' | 'search'>('strategy')
  const [preference, setPreference] = useState<'time' | 'energy' | 'balanced'>('time')
  const [seeds, setSeeds] = useState('42')
  const [budget, setBudget] = useState(5)
  const [name, setName] = useState('')
  const [busy, setBusy] = useState(false)
  const [selected, setSelected] = useState('')
  const [logs, setLogs] = useState<ExperimentBundle | null>(null)
  const [artifact, setArtifact] = useState(0)
  const [planId, setPlanId] = useState('')
  const sources = missions.filter((m) => !!m.current_scenario_id)
  const mission = sources.find((m) => m.mission_id === sourceId) || sources[0]
  const source = useQuery({
    queryKey: ['experiment-source', mission?.current_scenario_id],
    queryFn: () => api.scenario(mission!.current_scenario_id!),
    enabled: !!mission?.current_scenario_id,
  })
  const history = useQuery({
    queryKey: ['experiments'],
    queryFn: ops.experiments,
    refetchInterval: (q) =>
      q.state.data?.some((r) => ['queued', 'running'].includes(r.status)) ? 1200 : false,
  })
  const active = history.data?.find((r) => r.experiment_id === selected) || history.data?.[0]
  const feasible = useMemo(
    () =>
      active?.cases.filter(
        (c) => c.job?.has_validated_plan && c.energy_kwh !== null && c.makespan_s !== null,
      ) || [],
    [active],
  )
  const chart = useMemo<EChartsOption>(
    () => ({
      grid: { left: 55, right: 20, top: 38, bottom: 55 },
      xAxis: {
        type: 'value',
        name: '总能耗 / kWh',
        nameLocation: 'middle',
        nameGap: 28,
        scale: true,
      },
      yAxis: { type: 'value', name: '全队返航 / min', scale: true },
      series: [
        {
          type: 'scatter',
          symbolSize: 13,
          data: feasible.map((c) => ({
            name: `${objective[c.objective]} · ${method[c.method]} · seed ${c.seed}`,
            value: [c.energy_kwh, c.makespan_s! / 60],
            itemStyle: {
              color:
                c.objective === 'energy'
                  ? '#408b83'
                  : c.objective === 'balanced'
                    ? '#8c6bc5'
                    : '#4479c8',
            },
          })),
        },
      ],
    }),
    [feasible],
  )
  const artifactText = useMemo(() => {
    const value = logs?.artifacts[artifact]
    if (!value) return ''
    const raw = new TextDecoder().decode(
      Uint8Array.from(atob(value.content_base64), (c) => c.charCodeAt(0)),
    )
    if (!raw) return '（该原始文件为空）'
    try {
      return JSON.stringify(JSON.parse(raw), null, 2)
    } catch {
      return raw
    }
  }, [logs, artifact])

  async function create() {
    if (!source.data || !mission) return
    setBusy(true)
    try {
      const values = seeds.split(/[,，]/).map((s) => s.trim())
      if (!values.length || values.length > 3 || values.some((v) => !/^\d+$/.test(v)))
        throw new Error('请输入1—3个不重复的非负整数种子，用逗号分隔。')
      const seedValues = values.map(Number)
      if (new Set(seedValues).size !== seedValues.length) throw new Error('种子不能重复。')
      const snapshot = await api.snapshot(source.data)
      const run = await ops.createExperiment({
        name: name.trim() || `${mission.name} · ${suite === 'strategy' ? '策略对照' : '搜索对照'}`,
        source_snapshot_id: snapshot.snapshot_id,
        suite,
        objective: preference,
        objective_policy: 'tradeoff_v2',
        seeds: seedValues,
        time_limit_s: budget,
        idempotency_key: key(),
      })
      setSelected(run.experiment_id)
      await cache.invalidateQueries({ queryKey: ['experiments'] })
      notify('评测已保存，后台会逐例实际求解；关闭页面后仍可恢复查看。')
    } catch (error) {
      notify((error as Error).message, true)
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="v2-content v2-experiments">
      <div className="v2-page-heading">
        <div>
          <h1>演练评测</h1>
          <p>固定输入与预算，查看真实候选、失败记录和可复现证据。</p>
        </div>
        <Button onClick={onNew}>
          <Plus size={15} />
          新建演练任务
        </Button>
      </div>
      <div className="v2-experiment-workbench">
        <aside className="v2-card v2-experiment-setup">
          <h2>
            <FlaskConical size={17} />
            新建对照
          </h2>
          {sources.length ? (
            <>
              <label>
                输入任务
                <select
                  aria-label="评测输入任务"
                  value={mission?.mission_id || ''}
                  onChange={(e) => setSourceId(e.target.value)}
                >
                  {sources.map((m) => (
                    <option key={m.mission_id} value={m.mission_id}>
                      {m.name}
                    </option>
                  ))}
                </select>
              </label>
              {source.data && (
                <p className="v2-subtle">
                  输入 v{source.data.state_version} · {source.data.sites.length} 点 ·{' '}
                  {source.data.cargo_items.length} 箱 · {source.data.data_origin}
                </p>
              )}
              <label>
                对照类型
                <select
                  aria-label="评测对照类型"
                  value={suite}
                  onChange={(e) => setSuite(e.target.value as typeof suite)}
                >
                  <option value="strategy">同输入的三种偏好</option>
                  <option value="search">同目标的规则 / CP-SAT 搜索</option>
                </select>
              </label>
              <p>
                {suite === 'strategy'
                  ? '比较时间、能耗与折中选择。相同结果可能共享最优候选，不能据此宣称算法提升。'
                  : '两个方法使用同一快照和预算上限。保留未得到可行解、超时和不支持的模型组合。'}
              </p>
              {suite === 'search' && (
                <label>
                  固定目标
                  <select
                    aria-label="评测固定目标"
                    value={preference}
                    onChange={(e) => setPreference(e.target.value as typeof preference)}
                  >
                    {Object.entries(objective).map(([id, label]) => (
                      <option key={id} value={id}>
                        {label}
                      </option>
                    ))}
                  </select>
                </label>
              )}
              <label>
                每例求解预算
                <select
                  aria-label="每例求解预算"
                  value={budget}
                  onChange={(e) => setBudget(Number(e.target.value))}
                >
                  {[1, 3, 5, 10, 30].map((v) => (
                    <option key={v} value={v}>
                      {v} 秒
                    </option>
                  ))}
                </select>
              </label>
              <label>
                随机种子（最多3个）
                <input
                  aria-label="评测随机种子"
                  value={seeds}
                  onChange={(e) => setSeeds(e.target.value)}
                  placeholder="42, 73, 101"
                />
              </label>
              <label>
                评测名称
                <input
                  aria-label="评测名称"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="可选，便于查找这轮对照"
                  maxLength={160}
                />
              </label>
              <p className="v2-subtle">
                每个种子 {suite === 'strategy' ? 3 : 2} 例，单 Worker
                串行；另计进程启动和排队。分析在独立输入副本运行。
              </p>
              <Button
                variant="primary"
                busy={busy}
                disabled={!source.data || source.isError}
                onClick={() => void create()}
              >
                开始真实评测
              </Button>
              {source.isError && <p role="alert">{source.error.message}</p>}
            </>
          ) : (
            <>
              <p>先创建并发布任务输入，再选择用于比较的快照。</p>
              <Button onClick={onNew}>创建演练输入</Button>
            </>
          )}
        </aside>
        <section className="v2-experiment-results">
          {history.isError ? (
            <p role="alert">{history.error.message}</p>
          ) : !active ? (
            <Empty
              icon={<FlaskConical size={24} />}
              title={history.isPending ? '正在读取评测' : '还没有运行记录'}
              description="左侧选择任务与对照类型，生成真实求解记录。"
            />
          ) : (
            <>
              <div className="v2-card v2-experiment-heading">
                <div>
                  <h2>{active.name}</h2>
                  <p>
                    {labels[active.status]} · {active.cases.length} 例 · {active.objective_policy}
                  </p>
                </div>
                <div className="v2-form-actions">
                  <Button
                    disabled={!['queued', 'running'].includes(active.status)}
                    onClick={() =>
                      void ops
                        .cancelExperiment(active.experiment_id)
                        .then(() => cache.invalidateQueries({ queryKey: ['experiments'] }))
                        .catch((e: Error) => notify(e.message, true))
                    }
                  >
                    <Square size={13} />
                    停止评测
                  </Button>
                  <a
                    className="button"
                    href={`/api/v1/experiments/${active.experiment_id}/export`}
                    download={`experiment-${active.experiment_id}.json`}
                  >
                    <Download size={14} />
                    完整证据
                  </a>
                  <Button
                    busy={busy}
                    onClick={() => {
                      setBusy(true)
                      void ops
                        .exportExperiment(active.experiment_id)
                        .then((bundle) => {
                          setLogs(bundle)
                          setArtifact(0)
                        })
                        .catch((e: Error) => notify(e.message, true))
                        .finally(() => setBusy(false))
                    }}
                  >
                    <FileJson size={14} />
                    原始记录
                  </Button>
                </div>
              </div>
              <div className="v2-experiment-metrics">
                <div>
                  <small>已结束 / 总例数</small>
                  <b>
                    {
                      active.cases.filter((c) =>
                        ['completed', 'failed', 'canceled'].includes(c.status),
                      ).length
                    }{' '}
                    / {active.cases.length}
                  </b>
                </div>
                <div>
                  <small>验证可行</small>
                  <b>{feasible.length}</b>
                </div>
                <div>
                  <small>失败 / 未获可验证方案</small>
                  <b>{active.groups.reduce((n, g) => n + g.failed_or_unvalidated, 0)}</b>
                </div>
                <div>
                  <small>取消</small>
                  <b>{active.groups.reduce((n, g) => n + g.canceled, 0)}</b>
                </div>
              </div>
              <div className="v2-card v2-experiment-chart">
                <h3>候选时间与能源</h3>
                {feasible.length ? (
                  <DataChart option={chart} label="评测真实候选时间能耗散点图" height={265} />
                ) : (
                  <p>当前没有可验证方案。未验证结果不绘成零能耗候选，原因保留在下表。</p>
                )}
                <small>
                  仅绘制验证可行的 {feasible.length}/{active.cases.length}{' '}
                  例。重合点不代表证明全局最优；不同偏好不作为算法消融结论。
                </small>
              </div>
              <div className="v2-card v2-experiment-table-wrap">
                <div className="v2-section-bar">
                  <h3>逐例结果</h3>
                  <small>横向滚动查看全部指标</small>
                </div>
                <table className="v2-table">
                  <thead>
                    <tr>
                      <th>方法 / 偏好</th>
                      <th>种子 / 预算</th>
                      <th>结果</th>
                      <th>首个可行 / 求解耗时</th>
                      <th>全队返航</th>
                      <th>能耗</th>
                      <th>余量 / 保障</th>
                      <th>证据</th>
                    </tr>
                  </thead>
                  <tbody>
                    {active.cases.map((c) => (
                      <tr key={c.case_id} data-testid="experiment-case">
                        <td>
                          <b>{method[c.method]}</b>
                          <small>{objective[c.objective]}</small>
                        </td>
                        <td>
                          {c.seed}
                          <small>{c.time_limit_s} s</small>
                        </td>
                        <td>
                          {c.job?.has_validated_plan
                            ? '已验证可行'
                            : (c.job?.solver_status
                                ? {
                                    OPTIMAL: '有限模型最优',
                                    FEASIBLE: '候选可行',
                                    INFEASIBLE: '当前模型不可行',
                                    UNKNOWN: '未获可验证解',
                                    ERROR: '计算异常',
                                  }[c.job.solver_status]
                                : null) ||
                              {
                                queued: '等待',
                                dispatching: '派发中',
                                running: '计算中',
                                completed: '已结束',
                                failed: '失败',
                                canceled: '已取消',
                              }[c.status]}
                          {c.message && <small>{c.message}</small>}
                          {!!c.diagnostics.length && (
                            <details>
                              <summary>查看诊断（{c.diagnostics.length}）</summary>
                              {c.diagnostics.map((d, i) => (
                                <small key={i}>
                                  {d.code} · {d.message}
                                </small>
                              ))}
                            </details>
                          )}
                        </td>
                        <td>
                          {number(c.first_feasible_s, 2)} / {number(c.runtime_s, 2)} s
                          <small>
                            {c.candidate_count === null
                              ? '候选数未知'
                              : `候选 ${c.candidate_count}`}
                          </small>
                        </td>
                        <td>{clock(c.makespan_s)}</td>
                        <td>{number(c.energy_kwh, 2)} kWh</td>
                        <td>
                          {c.min_return_soc === null ? '—' : percent(c.min_return_soc)}
                          <small>
                            {c.allocated_quantity === null ? '—' : `${c.allocated_quantity} 箱`}
                          </small>
                        </td>
                        <td>
                          <Button
                            disabled={!c.job?.has_validated_plan}
                            onClick={() => setPlanId(c.job!.plan_id!)}
                          >
                            核对方案
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <details className="v2-card v2-experiment-evidence">
                <summary>重复实验统计与运行环境</summary>
                <p>
                  耗时分位数使用所有已结束且耗时有值的例；能耗/返航中位数仅使用验证可行样本。小样本
                  p95 不是可靠性保证。
                </p>
                <table className="v2-table">
                  <thead>
                    <tr>
                      <th>方法 / 偏好</th>
                      <th>可行 / 全部</th>
                      <th>耗时样本</th>
                      <th>p50 / p95（s）</th>
                      <th>可行中位能耗</th>
                    </tr>
                  </thead>
                  <tbody>
                    {active.groups.map((g) => (
                      <tr key={g.method + g.objective}>
                        <td>
                          {g.method} / {g.objective}
                        </td>
                        <td>
                          {g.feasible} / {g.total}
                        </td>
                        <td>{g.runtime_sample_count}</td>
                        <td>
                          {number(g.runtime_p50_s, 2)} / {number(g.runtime_p95_s, 2)}
                        </td>
                        <td>{number(g.feasible_energy_median_kwh, 2)} kWh</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <dl>
                  <dt>原输入 / 分析快照</dt>
                  <dd>
                    {active.source_snapshot_id}
                    <br />
                    {active.snapshot_id}
                  </dd>
                  <dt>来源 / 分析内容哈希</dt>
                  <dd>
                    {active.data_origin}
                    <br />
                    <code>{active.snapshot_content_hash}</code>
                  </dd>
                  <dt>Python / OR-Tools / NumPy</dt>
                  <dd>
                    {active.environment.python_version} / {active.environment.ortools_version} /{' '}
                    {active.environment.numpy_version}
                  </dd>
                  <dt>系统 / CPU</dt>
                  <dd>
                    {active.environment.platform}
                    <br />
                    {active.environment.processor || 'CPU型号未报告'} ·{' '}
                    {active.environment.logical_cpu_count ?? '未知'} 逻辑核
                  </dd>
                  <dt>线程与缓存口径</dt>
                  <dd>
                    Worker上限 {active.environment.worker_serial_limit}，CP-SAT{' '}
                    {active.environment.cp_sat_threads} 线程
                    <br />
                    {active.environment.cache_policy}
                  </dd>
                  <dt>源码</dt>
                  <dd>
                    <code>{active.environment.git_commit || '未读取到commit'}</code>
                    {active.environment.git_worktree_dirty && (
                      <small>启动时存在未提交改动，以源码指纹为准</small>
                    )}
                    <br />
                    <code>{active.environment.service_source_sha256}</code>
                  </dd>
                </dl>
              </details>
            </>
          )}
        </section>
      </div>
      {!!history.data?.length && (
        <section className="v2-card v2-experiment-history">
          <h2>评测历史</h2>
          <div>
            {history.data.map((r) => (
              <button
                className={active?.experiment_id === r.experiment_id ? 'active' : ''}
                onClick={() => setSelected(r.experiment_id)}
                key={r.experiment_id}
              >
                <b>{r.name}</b>
                <small>
                  {labels[r.status]} · {r.cases.length} 例 ·{' '}
                  {new Date(r.created_at).toLocaleString('zh-CN')}
                </small>
              </button>
            ))}
          </div>
        </section>
      )}
      <Modal
        open={!!logs}
        onOpenChange={(open) => !open && setLogs(null)}
        title="评测原始记录"
        wide
      >
        <div className="v2-experiment-logs">
          <label>
            原始文件
            <select
              aria-label="评测原始文件"
              value={artifact}
              onChange={(e) => setArtifact(Number(e.target.value))}
            >
              {logs?.artifacts.map((a, i) => (
                <option key={a.case_id + a.name} value={i}>
                  {a.case_id.slice(-6)} / {a.name}
                </option>
              ))}
            </select>
          </label>
          {logs?.artifacts[artifact] && (
            <p>
              {logs.artifacts[artifact].byte_count} bytes · SHA256{' '}
              <code>{logs.artifacts[artifact].content_sha256}</code>
            </p>
          )}
          <pre>{artifactText || '暂无原始文件；未派发或文件尚未生成。'}</pre>
          {!!logs?.missing_artifacts.length && (
            <details>
              <summary>尚缺 {logs.missing_artifacts.length} 个原始文件</summary>
              <p>{logs.missing_artifacts.join('\n')}</p>
            </details>
          )}
        </div>
      </Modal>
      <Modal
        open={!!planId}
        onOpenChange={(open) => !open && setPlanId('')}
        title="评测方案核对"
        description="只读显示本例真实Plan及其冻结输入，不确认方案或启动执行。"
        wide
      >
        {planId && <ExperimentPlan key={planId} planId={planId} />}
      </Modal>
    </main>
  )
}

function ExperimentPlan({ planId }: { planId: string }) {
  const [selected, setSelected] = useState<string | null>(null)
  const plan = useQuery({ queryKey: ['plan', planId], queryFn: () => api.plan(planId) })
  const snapshot = useQuery({
    queryKey: ['snapshot', plan.data?.snapshot_id],
    queryFn: () => api.getSnapshot(plan.data!.snapshot_id),
    enabled: !!plan.data,
  })
  if (plan.isError || snapshot.isError)
    return <p role="alert">{plan.error?.message || snapshot.error?.message}</p>
  if (!plan.data || !snapshot.data) return <p>正在读取真实方案与输入…</p>
  const p = plan.data
  const r = p.sorties.find((row) => row.sortie_id === selected)
  return (
    <div className="v2-experiment-plan">
      <p>
        {p.plan_id} · 快照 {p.snapshot_id} · 验证 {p.validation.status}
      </p>
      <div className="v2-experiment-plan-map">
        <RescueMap
          scenario={snapshot.data.scenario}
          plan={p}
          selected={selected}
          onSelect={setSelected}
          viewKey={'experiment:' + planId}
        />
      </div>
      <ResourceTimeline
        scenario={snapshot.data.scenario}
        plan={p}
        selected={selected}
        onSelect={setSelected}
      />
      {r && (
        <p>
          {r.drone_id} / {r.battery_id} · {r.visits.map((v) => v.site_id).join(' → ')}
          <br />
          箱件：{r.cargo_ids.join(' · ')}
        </p>
      )}
    </div>
  )
}
