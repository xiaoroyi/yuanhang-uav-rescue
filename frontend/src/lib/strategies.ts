import type { Plan } from '../api/client'
import { duration, number } from './format.ts'

type PolicyRecord = { objective_policy?: string | null } | null | undefined
export const policyOf = (p: PolicyRecord): 'deadline_first_v1' | 'tradeoff_v2' =>
  p?.objective_policy === 'tradeoff_v2' ? 'tradeoff_v2' : 'deadline_first_v1'
export const policyLabel = (p: PolicyRecord) =>
  policyOf(p) === 'tradeoff_v2' ? '直接取舍 v2' : '旧版延期优先 v1'

export function strategyDescription(objective: string, p: PolicyRecord) {
  const goal =
    objective === 'energy'
      ? '降低总能耗'
      : objective === 'balanced'
        ? '最小化返航秒数 + 300 × 能耗(kWh)'
        : '缩短最后返航时间'
  return policyOf(p) === 'tradeoff_v2'
    ? `${goal}；期望延期作为同分时次目标`
    : `旧版：先减加权期望延期，再${goal}`
}

export function strategyMetrics(p: Plan) {
  return p.joint_metrics
    ? { makespan_s: p.joint_metrics.joint_makespan_s, energy_kwh: p.joint_metrics.joint_energy_kwh }
    : p.metrics
}

// Ignore generated sortie IDs; retain every scheduling/physical field and all
// relay/charging data. A metric tie alone never proves identical schedules.
export function scheduleSignature(p: Plan) {
  const stable = (value: unknown): unknown => {
    if (Array.isArray(value)) return value.map(stable)
    if (value && typeof value === 'object')
      return Object.fromEntries(
        Object.entries(value)
          .sort(([a], [b]) => a.localeCompare(b))
          .map(([k, v]) => [k, stable(v)]),
      )
    return value
  }
  const sorties = p.sorties
    .map((r) =>
      JSON.stringify(
        stable(Object.fromEntries(Object.entries(r).filter(([key]) => key !== 'sortie_id'))),
      ),
    )
    .sort()
  return JSON.stringify(
    stable({ sorties, relay_sorties: p.relay_sorties, initial_charges: p.initial_charges }),
  )
}

export function equalityExplanation(plans: Plan[]) {
  if (new Set(plans.map((p) => p.objective)).size < 3) return ''
  if (new Set(plans.map((p) => p.snapshot_id)).size > 1 || new Set(plans.map(policyOf)).size > 1)
    return ''
  if (new Set(plans.map(scheduleSignature)).size === 1)
    return policyOf(plans[0]) === 'deadline_first_v1'
      ? '三份实际排程相同：旧规则共同优先减少期望延期，可能选中同一候选。可按新规则重新计算。'
      : '三份实际排程相同：本轮有限搜索在共同硬约束下选中了同一候选，不代表三种目标等价或已达到全局最优。'
  if (
    new Set(
      plans.map((p) => {
        const m = strategyMetrics(p)
        return `${duration(m.makespan_s)}|${number(m.energy_kwh, 2)}`
      }),
    ).size === 1
  )
    return '卡片数字因显示精度相同，但实际排程不同。请在方案对比中查看精确指标、架次与延期。'
  return '三种策略展示真实独立计算结果。节能可能增加等待与期望延期，请结合交付分析选择。'
}
