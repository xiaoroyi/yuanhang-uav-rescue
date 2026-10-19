import { engineOptions } from '../lib/engines'
import { useEffect, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Download, FlaskConical, LoaderCircle, X } from 'lucide-react'
import { api, downloadJson, type Plan, type Scenario } from '../api/client'
import { Badge, Button } from '../components/ui'
import { duration, number, percent, statusLabel } from '../lib/format'
import { policyOf, policyLabel } from '../lib/strategies'

type Props = {
  scenario: Scenario
  plan: Plan
  disabled: boolean
  onOpen: (s: Scenario) => void
  onBusyChange: (busy: boolean) => void
  notify: (message: string, error?: boolean) => void
}

export function ScenarioExperiments({
  scenario,
  plan,
  disabled,
  onOpen,
  onBusyChange,
  notify,
}: Props) {
  const query = useQueryClient()
  const [submitting, setSubmitting] = useState(false)
  const history = useQuery({
    queryKey: ['what-if-history', scenario.scenario_id],
    queryFn: () => api.whatIfHistory(scenario.scenario_id),
    refetchInterval: (q) =>
      q.state.data?.some((r) => r.job && ['queued', 'running'].includes(r.job.job_state))
        ? 750
        : false,
  })
  const pending = !!history.data?.some(
    (r) => r.job && ['queued', 'running'].includes(r.job.job_state),
  )
  useEffect(() => onBusyChange(pending || submitting), [pending, submitting, onBusyChange])
  async function stress() {
    if (disabled || pending || submitting) return
    setSubmitting(true)
    const cases = [
      { name: '压力A · 原条件', energy: 1, time: 1, soh: 1 },
      { name: '压力B · 能耗+10%/时长+5%/SOH×95%', energy: 1.1, time: 1.05, soh: 0.95 },
      { name: '压力C · 能耗+20%/时长+10%/SOH×90%', energy: 1.2, time: 1.1, soh: 0.9 },
    ]
    try {
      for (const item of cases) {
        const fork = await api.whatIf(scenario.scenario_id, {
          expected_state_version: scenario.state_version,
          source_plan_id: plan.plan_id,
          name: item.name,
          additions: [],
          energy_multiplier: item.energy,
          flight_time_multiplier: item.time,
          battery_soh_multiplier: item.soh,
          noncritical_deadline_multiplier: 1,
        })
        const snap = await api.snapshot(fork.scenario)
        await api.solve(snap.snapshot_id, plan.objective as 'time' | 'energy' | 'balanced', {
          objective_policy: policyOf(plan),
          ...engineOptions(plan),
        })
      }
      notify('已提交3个独立压力情景，按同一策略真实计算。')
    } catch (error) {
      notify((error as Error).message, true)
    } finally {
      setSubmitting(false)
      await query.invalidateQueries({ queryKey: ['what-if-history', scenario.scenario_id] })
      await query.invalidateQueries({ queryKey: ['scenarios'] })
    }
  }
  return (
    <section className="panel experiment-history">
      <div className="panel-heading">
        <div>
          <h3>
            情景记录与压力检查 <Badge>{history.data?.length || 0}</Badge>
          </h3>
          <p>重启后仍保留各情景原始快照与结果；新试算沿用{policyLabel(plan)}</p>
        </div>
        <Button disabled={disabled || pending} busy={submitting} onClick={() => void stress()}>
          <FlaskConical size={14} />
          运行3档压力测试
        </Button>
      </div>
      <div className="stress-description">
        <span>原条件</span>
        <span>能耗×1.1 / 时长×1.05 / SOH×0.95</span>
        <span>能耗×1.2 / 时长×1.1 / SOH×0.9</span>
        <p>
          基于当前输入额外施加倍率，不改变资源数与硬截止。这是确定性情景检查，不能解释为成功概率。
        </p>
      </div>
      {history.isError ? (
        <p className="trial-error">{(history.error as Error).message}</p>
      ) : history.isLoading ? (
        <div className="experiment-empty">
          <LoaderCircle size={17} className="spin" />
          正在读取试算记录…
        </div>
      ) : history.data?.length ? (
        <>
          <div className="experiment-table-scroll">
            <table className="data-table">
              <thead>
                <tr>
                  <th>情景与来源</th>
                  <th>任务状态</th>
                  <th>最近可行返航</th>
                  <th>能耗</th>
                  <th>最低SOC</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {history.data.map((row) => (
                  <tr key={row.scenario_id} data-testid="experiment-row">
                    <td>
                      <strong>{row.origin.parameters.name}</strong>
                      <small className="demand-id">
                        源v{row.origin.source_state_version} ·{' '}
                        {row.scenario_state_version === 1 ? '原始情景v1' : '场景已编辑，统计原始v1'}
                      </small>
                    </td>
                    <td>
                      <Badge
                        tone={
                          row.job?.job_state === 'failed'
                            ? 'red'
                            : row.job?.has_validated_plan
                              ? 'teal'
                              : row.job
                                ? 'amber'
                                : 'neutral'
                        }
                      >
                        {row.job
                          ? statusLabel[row.job.solver_status || row.job.job_state]
                          : '尚未提交'}
                      </Badge>
                      {row.job && ['queued', 'running'].includes(row.job.job_state) && (
                        <button
                          className="experiment-cancel"
                          aria-label={'取消' + row.origin.parameters.name}
                          onClick={() =>
                            void api.cancel(row.job!.job_id).then(() => history.refetch())
                          }
                        >
                          <X size={12} />
                        </button>
                      )}
                    </td>
                    <td>
                      {duration(row.plan?.metrics.makespan_s)}
                      {row.plan && <small>{policyLabel(row.plan)}</small>}
                    </td>
                    <td>
                      {number(row.plan?.metrics.energy_kwh, 2)}
                      {row.plan ? ' kWh' : ''}
                    </td>
                    <td>{percent(row.plan?.metrics.min_return_soc)}</td>
                    <td>
                      <button
                        className="text-button"
                        onClick={() =>
                          void api
                            .scenario(row.scenario_id)
                            .then(onOpen)
                            .catch((error) => notify(error.message, true))
                        }
                      >
                        打开场景
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="experiment-foot">
            <span>UNKNOWN表示未找到方案；失败/取消不产生新的可确认结果。旧可行记录单独保留。</span>
            <Button
              onClick={() =>
                downloadJson(
                  { source_scenario_id: scenario.scenario_id, experiments: history.data },
                  'yuanhang-scenario-experiments.json',
                )
              }
            >
              <Download size={13} />
              导出记录
            </Button>
          </div>
        </>
      ) : (
        <div className="experiment-empty">还没有独立情景。可从右侧试算，或运行3档压力测试。</div>
      )}
    </section>
  )
}
