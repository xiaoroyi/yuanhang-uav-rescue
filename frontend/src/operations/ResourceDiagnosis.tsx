import { engineOptions } from '../lib/engines'
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api, type Scenario, type Plan, type Snapshot, type WhatIfReceipt } from '../api/client'
import { Button } from '../components/ui'
import { RescueMap } from '../components/RescueMap'
import { ResourceTimeline } from '../components/ResourceTimeline'
import { NominalDiagnostics } from '../pages/NominalDiagnostics'
import { policyOf } from '../lib/strategies'
import { clock } from './format'
import { number } from '../lib/format'

export function ResourceDiagnosis({
  scenario,
  baseline,
  onOpen,
  notify,
}: {
  scenario: Scenario
  baseline?: Plan
  onOpen: (scene: Scenario) => void
  notify: (message: string, error?: boolean) => void
}) {
  const [typeId, setTypeId] = useState(scenario.drone_types[0]?.type_id || '')
  const [drones, setDrones] = useState(1),
    [batteries, setBatteries] = useState(0)
  const [capacity, setCapacity] = useState(''),
    [budget, setBudget] = useState(5)
  const [busy, setBusy] = useState(false),
    [jobId, setJobId] = useState('')
  const [receipt, setReceipt] = useState<WhatIfReceipt | null>(null)
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null)
  const [selected, setSelected] = useState<string | null>(null)
  const compatible = scenario.batteries.find((b) => b.compatible_type_id === typeId)
  const job = useQuery({
    queryKey: ['job', jobId],
    queryFn: () => api.job(jobId),
    enabled: !!jobId,
    refetchInterval: (q) =>
      q.state.data && ['completed', 'failed', 'canceled'].includes(q.state.data.job_state)
        ? false
        : 700,
  })
  const result = useQuery({
    queryKey: ['plan', job.data?.plan_id],
    queryFn: () => api.plan(job.data!.plan_id!),
    enabled: !!job.data?.plan_id,
  })
  const resultSnapshot = useQuery({
    queryKey: ['snapshot', result.data?.snapshot_id],
    queryFn: () => api.getSnapshot(result.data!.snapshot_id),
    enabled: !!result.data,
  })
  const working = busy || (!!job.data && ['queued', 'running'].includes(job.data.job_state))
  const valid =
    Number.isInteger(drones) &&
    drones >= 0 &&
    drones <= 4 &&
    Number.isInteger(batteries) &&
    batteries >= 0 &&
    batteries <= 8 &&
    drones + batteries > 0 &&
    (batteries === 0 || !!compatible || Number(capacity) > 0)
  async function trial() {
    setBusy(true)
    try {
      const fork = await api.whatIf(scenario.scenario_id, {
        expected_state_version: scenario.state_version,
        source_plan_id: baseline?.plan_id || null,
        name: '资源增配诊断',
        energy_multiplier: 1,
        flight_time_multiplier: 1,
        battery_soh_multiplier: 1,
        noncritical_deadline_multiplier: 1,
        additions: [
          {
            type_id: typeId,
            drones,
            batteries,
            ...(!compatible && batteries > 0 ? { battery_capacity_kwh: Number(capacity) } : {}),
          },
        ],
      })
      setReceipt(fork)
      setJobId('')
      setSelected(null)
      const input = await api.snapshot(fork.scenario)
      const submitted = await api.solve(
        input.snapshot_id,
        (baseline?.objective as 'time' | 'energy' | 'balanced') || 'time',
        {
          time_limit_s: budget,
          objective_policy: baseline ? policyOf(baseline) : 'tradeoff_v2',
          ...engineOptions(baseline),
        },
      )
      setJobId(submitted.job_id)
      notify('独立增配场景已保存，正在实际求解；原任务保持原版本。')
    } catch (error) {
      notify((error as Error).message, true)
    } finally {
      setBusy(false)
    }
  }
  return (
    <section className="v2-resource-diagnosis" aria-label="资源诊断与独立增配">
      <p className="v2-subtle">
        输入 v{scenario.state_version} · 可用机体{' '}
        {scenario.drones.filter((d) => d.status === 'available').length} / {scenario.drones.length}{' '}
        · 可用电池 {scenario.batteries.filter((b) => b.status === 'available').length} /{' '}
        {scenario.batteries.length}。
        {baseline
          ? '有原方案可供核对，有限预算候选不保证单调改善。'
          : '尚无可行基线；新增结果单独报告，不把缺失基线当作零耗时/零能耗。'}
      </p>
      <div className="v2-resource-controls">
        <label>
          增配机型
          <select
            aria-label="诊断增配机型"
            value={typeId}
            onChange={(e) => setTypeId(e.target.value)}
          >
            {scenario.drone_types.map((t) => (
              <option key={t.type_id} value={t.type_id}>
                {t.type_id} · {t.max_payload_kg} kg / {t.max_volume_l} L
              </option>
            ))}
          </select>
        </label>
        <label>
          新增机体
          <input
            aria-label="诊断新增机体"
            type="number"
            min={0}
            max={4}
            value={drones}
            onChange={(e) => setDrones(Number(e.target.value))}
          />
        </label>
        <label>
          新增电池
          <input
            aria-label="诊断新增电池"
            type="number"
            min={0}
            max={8}
            value={batteries}
            onChange={(e) => setBatteries(Number(e.target.value))}
          />
        </label>
        {!compatible && batteries > 0 && (
          <label>
            明确容量 / kWh
            <input
              aria-label="诊断电池容量"
              type="number"
              min={0.001}
              step={0.1}
              value={capacity}
              onChange={(e) => setCapacity(e.target.value)}
            />
          </label>
        )}
        <label>
          每例预算
          <select
            aria-label="诊断求解预算"
            value={budget}
            onChange={(e) => setBudget(Number(e.target.value))}
          >
            {[5, 15, 30, 60].map((n) => (
              <option key={n} value={n}>
                {n} 秒
              </option>
            ))}
          </select>
        </label>
        <Button variant="primary" busy={working} disabled={!valid} onClick={() => void trial()}>
          增配并真实求解
        </Button>
      </div>
      <p className="v2-chart-note">
        仅添加明确数量的独立机体/电池，新增资源假设满电健康；不补造缺失箱件，不放宽硬截止。结果为当前预算内候选，不代表最少购买数量。多种组合可分别计算，保留独立场景。
      </p>
      {job.data && (
        <div className="v2-check-summary">
          作业 {job.data.job_state} · {job.data.solver_status || '等待结果'}
          {['queued', 'running'].includes(job.data.job_state) && (
            <Button onClick={() => void api.cancel(jobId).then(() => job.refetch())}>
              取消诊断计算
            </Button>
          )}
          {job.data.error?.message && <p role="alert">{job.data.error.message}</p>}
          {job.data.job_state === 'completed' && !job.data.has_validated_plan && (
            <p>本例未获可验证方案。UNKNOWN表示预算/方法尚未找到解，INFEASIBLE仅限当前声明模型。</p>
          )}
        </div>
      )}
      {result.data && resultSnapshot.data && (
        <div className="v2-route-analysis">
          <div className="v2-metrics-line">
            <span>
              验证 <b>{result.data.validation.status}</b>
            </span>
            <span>
              分配 <b>{result.data.sorties.reduce((sum, r) => sum + r.cargo_ids.length, 0)} 箱</b>
            </span>
            <span>返航 {clock(result.data.metrics.makespan_s)}</span>
            <span>能耗 {number(result.data.metrics.energy_kwh, 2)} kWh</span>
            <span>原基线 {baseline ? baseline.plan_id : '未取得'}</span>
          </div>
          <div className="v2-route-map">
            <RescueMap
              scenario={resultSnapshot.data.scenario}
              plan={result.data}
              selected={selected}
              onSelect={setSelected}
            />
          </div>
          <ResourceTimeline
            scenario={resultSnapshot.data.scenario}
            plan={result.data}
            selected={selected}
            onSelect={setSelected}
          />
        </div>
      )}
      {receipt && (
        <Button onClick={() => onOpen(receipt.scenario)}>作为独立任务打开此增配场景</Button>
      )}
      <details className="v2-diagnostic-details">
        <summary>单点物理能力诊断（不等于完整调度）</summary>
        <Button
          busy={busy}
          onClick={() => {
            setBusy(true)
            void api
              .snapshot(scenario)
              .then(setSnapshot)
              .catch((e: Error) => notify(e.message, true))
              .finally(() => setBusy(false))
          }}
        >
          冻结输入并运行物理诊断
        </Button>
        {snapshot && <NominalDiagnostics snapshot={snapshot} />}
      </details>
    </section>
  )
}
