import { useQuery } from '@tanstack/react-query'
import { ops, type Mission } from '../api/operations'
import type { Plan } from '../api/client'

export function PlanValidityNotice({ mission, plan }: { mission: Mission; plan?: Plan }) {
  const id = mission.active_execution_id
  const execution = useQuery({
    queryKey: ['execution', id],
    queryFn: () => ops.execution(id!),
    enabled: !!id,
    refetchInterval: 2000,
  })
  const events = useQuery({
    queryKey: ['execution-events', id],
    queryFn: () => ops.events(id!),
    enabled: !!id,
    refetchInterval: 2000,
  })
  if (!id || !plan) return null
  const pending = events.data?.filter(
    (e) => e.status !== 'withdrawn' && !execution.data?.applied_event_ids?.includes(e.event_id),
  )
  const changed = execution.data?.desired_plan_id && execution.data.desired_plan_id !== plan.plan_id
  if (execution.error || events.error)
    return (
      <div className="v2-inline-warning v2-validity-notice" role="status">
        当前执行状态暂未读到；此页检查只对应原始快照。
        <a href={`#/missions/${mission.mission_id}/execute`}>核对执行状态</a>
      </div>
    )
  if (!pending?.length && !changed) return null
  return (
    <div className="v2-inline-warning v2-validity-notice" role="status">
      <span>
        {pending?.length
          ? `执行条件已变化：待处理 ${pending.length} 项。`
          : '当前执行未来任务已采用调整方案。'}
        此页方案仅通过其原快照检查，不能据此继续原安排。
      </span>
      <a href={`#/missions/${mission.mission_id}/execute`}>
        {pending?.length ? '查看受影响任务与调整' : '查看当前生效安排'}
      </a>
    </div>
  )
}
