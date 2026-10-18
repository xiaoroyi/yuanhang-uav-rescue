import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import type { Execution } from '../api/operations'
import { Button, Modal } from '../components/ui'
import { RescueMap } from '../components/RescueMap'
import { ResourceTimeline } from '../components/ResourceTimeline'
import { StageCharts } from './StageCharts'
import { clock } from './format'
import { number, percent } from '../lib/format'
import type { ImpactSelection } from './DependencyImpactPanel'

export function ExecutionRouteInspector({
  selection,
  execution,
  onClose,
}: {
  selection: ImpactSelection
  execution: Execution
  onClose: () => void
}) {
  const [profile, setProfile] = useState(false)
  const plan = useQuery({
    queryKey: ['plan', selection.planId],
    queryFn: () => api.plan(selection.planId),
  })
  const snap = useQuery({
    queryKey: ['snapshot', plan.data?.snapshot_id],
    queryFn: () => api.getSnapshot(plan.data!.snapshot_id),
    enabled: !!plan.data,
  })
  const route = plan.data?.sorties.find((r) => r.sortie_id === selection.sortieId)
  const current = execution.schedule_parts.some(
    (p) => p.plan_id === selection.planId && p.sortie_ids.includes(selection.sortieId),
  )
  const loaded = execution.facts.some(
    (f) =>
      f.kind === 'loaded' && f.plan_id === selection.planId && f.sortie_id === selection.sortieId,
  )
  return (
    <aside className="v2-inspector" aria-label="执行架次安排详情">
      <div className="v2-section-bar">
        <h2>架次安排</h2>
        <button onClick={onClose} aria-label="关闭架次详情">
          ×
        </button>
      </div>
      <p className="v2-route-context">
        {current
          ? loaded
            ? '当前安排 · 已有装载事实，承诺保留'
            : '当前未来安排 · 尚无装载事实'
          : '历史事件安排 · 已非当前生效任务'}
      </p>
      <code className="v2-source-code">{selection.planId}</code>
      <h3>{selection.sortieId}</h3>
      {plan.isPending && <p>读取原始方案…</p>}
      {plan.error && <p role="alert">原始方案读取失败：{plan.error.message}</p>}
      {plan.data && !route && <p>原方案中没有此运输架次。</p>}
      {route && (
        <>
          <dl>
            <dt>机体 / 运输电池</dt>
            <dd>
              {route.drone_id} / {route.battery_id}
            </dd>
            <dt>准备 / 起飞（计划）</dt>
            <dd>
              {clock(route.prepare_start_s)} / {clock(route.takeoff_s)}
            </dd>
            <dt>返航 / 机体释放（计划）</dt>
            <dd>
              {clock(route.return_s)} / {clock(route.drone_released_s)}
            </dd>
            <dt>电池补能结束（计划）</dt>
            <dd>{clock(route.battery_released_s)}</dd>
            <dt>模型能耗 / 返航SOC</dt>
            <dd>
              {number(route.energy_kwh, 3)} kWh / {percent(route.return_soc)}
            </dd>
          </dl>
          <h3>访问与逐箱安排</h3>
          {route.visits.map((v, i) => (
            <div className="v2-visit" key={v.site_id + ':' + i}>
              <b>
                {i + 1}.{' '}
                {snap.data?.scenario.sites.find((s) => s.id === v.site_id)?.name || v.site_id}
              </b>
              <small>预计交接 {clock(v.delivery_complete_s)}</small>
              <code>{v.cargo_ids.join(' · ')}</code>
            </div>
          ))}
          <Button onClick={() => setProfile(true)}>核对原文航线与高程分析</Button>
          <small>这里展示原Plan的安排；实时位置和在机物资请点击机体查看。</small>
        </>
      )}
      <Modal
        title="执行架次 · 原文航线与分析"
        description="绑定所选Plan与Snapshot；历史安排用于对照，不改变当前执行。"
        open={profile}
        onOpenChange={setProfile}
        wide
      >
        {plan.data && snap.data && route ? (
          <div className="v2-route-analysis">
            <div className="v2-route-map">
              <RescueMap
                scenario={snap.data.scenario}
                plan={plan.data}
                selected={route.sortie_id}
                onSelect={() => {}}
              />
            </div>
            <StageCharts plan={plan.data} selected={route.sortie_id} />
            <ResourceTimeline
              scenario={snap.data.scenario}
              plan={plan.data}
              selected={route.sortie_id}
              onSelect={() => {}}
            />
          </div>
        ) : (
          <p>读取原始快照…</p>
        )}
      </Modal>
    </aside>
  )
}
