import { useQuery } from '@tanstack/react-query'
import { api, type Plan } from '../api/client'
import { number } from '../lib/format'
import { policyLabel } from '../lib/strategies'

export function StrategyFacts({ plan }: { plan: Plan }) {
  const analysis = useQuery({
    queryKey: ['analysis', plan.plan_id],
    queryFn: () => api.analysis(plan.plan_id),
  })
  const d = analysis.data?.delivery
  return (
    <div className="strategy-facts">
      <small>
        {plan.joint_metrics ? '运输 + 通信联合指标' : '运输指标'} · {policyLabel(plan)}
      </small>
      <small className={d && d.late_demand_count > 0 ? 'strategy-late' : ''}>
        {d
          ? `期望延期 ${d.late_demand_count} 条 / ${d.expected_demand_count} 条 · 加权 ${number(d.weighted_box_delay_s, 0)} 箱秒`
          : analysis.isError
            ? '延期分析读取失败'
            : '正在读取交付分析…'}
      </small>
      <code title={plan.plan_id}>{plan.plan_id}</code>
    </div>
  )
}
