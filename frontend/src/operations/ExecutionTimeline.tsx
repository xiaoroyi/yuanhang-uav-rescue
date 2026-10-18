import { useMemo, useState } from 'react'
import { Expand } from 'lucide-react'
import type { Plan } from '../api/client'
import type { Execution } from '../api/operations'
import { Button, Modal } from '../components/ui'
import { clock } from './format'

export type ExecutionSource = { plan: Plan; sortieIds: string[]; relayIds?: string[] }
type Segment = {
  key: string
  resource: string
  start: number
  end: number
  kind: 'prepare' | 'flight' | 'ground' | 'charge' | 'relay'
  label: string
  planId: string
  sortieId: string
}
export function ExecutionTimeline({
  sources,
  execution,
  onSelect,
  currentTime = execution.time_s,
  selected,
}: {
  sources: ExecutionSource[]
  execution: Execution
  onSelect?: (key: string) => void
  currentTime?: number
  selected?: string | null
}) {
  const [mode, setMode] = useState<'drone' | 'battery' | 'component'>('drone')
  const [expanded, setExpanded] = useState(false)
  const segments = useMemo(
    () =>
      sources.flatMap((source) => {
        const rows: Segment[] = []
        const add = (
          resource: string,
          sid: string,
          start: number,
          end: number,
          kind: Segment['kind'],
          label: string,
        ) => {
          if (end > start)
            rows.push({
              key: source.plan.plan_id + ':' + sid + ':' + kind + ':' + start,
              resource,
              start,
              end,
              kind,
              label,
              planId: source.plan.plan_id,
              sortieId: sid,
            })
        }
        for (const r of source.plan.sorties.filter((r) => source.sortieIds.includes(r.sortie_id))) {
          const resource = mode === 'drone' ? r.drone_id : r.battery_id
          if (mode === 'component') continue
          add(resource, r.sortie_id, r.prepare_start_s, r.takeoff_s, 'prepare', '装载准备')
          add(
            resource,
            r.sortie_id,
            r.takeoff_s,
            r.return_s,
            'flight',
            r.cargo_ids.length + '箱运输',
          )
          if (mode === 'drone')
            add(resource, r.sortie_id, r.return_s, r.drone_released_s, 'ground', '落地周转')
          else
            add(
              resource,
              r.sortie_id,
              r.charge_start_s ?? r.return_s,
              r.battery_released_s,
              'charge',
              '计划补能',
            )
        }
        for (const r of (source.plan.relay_sorties || []).filter((r) =>
          source.relayIds?.includes(r.relay_sortie_id),
        )) {
          if (mode === 'battery') continue
          const resource = mode === 'drone' ? r.drone_id : r.component_id
          add(resource, r.relay_sortie_id, r.prepare_start_s, r.takeoff_s, 'prepare', '中继准备')
          add(
            resource,
            r.relay_sortie_id,
            r.takeoff_s,
            r.service_start_s,
            'flight',
            '中继抵达/建链',
          )
          add(resource, r.relay_sortie_id, r.service_start_s, r.service_end_s, 'relay', '通信服务')
          add(resource, r.relay_sortie_id, r.service_end_s, r.return_s, 'flight', '中继返航')
          if (mode === 'drone')
            add(resource, r.relay_sortie_id, r.return_s, r.drone_released_s, 'ground', '中继周转')
          else
            add(
              resource,
              r.relay_sortie_id,
              r.charge_start_s,
              r.component_released_s,
              'charge',
              '组件补能',
            )
        }
        return rows
      }),
    [sources, mode],
  )
  const horizon = Math.max(60, currentTime, ...segments.map((s) => s.end)) * 1.03
  const resources = [...new Set(segments.map((s) => s.resource))].sort()
  const content = (
    <div className="v2-ledger-timeline">
      <div className="v2-ledger-ruler">
        <span>实体资源</span>
        <div>
          {[0, 1, 2, 3, 4, 5].map((n) => (
            <span key={n} style={{ left: n * 20 + '%' }}>
              {clock((horizon * n) / 5)}
            </span>
          ))}
        </div>
      </div>
      {resources.map((id) => (
        <div className="v2-ledger-row" key={id}>
          <strong>{id}</strong>
          <div className="v2-ledger-track">
            <i
              className="v2-ledger-cursor"
              style={{ left: (100 * currentTime) / horizon + '%' }}
              title={'模拟时标 ' + clock(currentTime)}
            />
            {segments
              .filter((s) => s.resource === id)
              .map((s) => (
                <button
                  key={s.key}
                  className={
                    'ledger-' +
                    s.kind +
                    (selected === s.planId + ':' + s.sortieId ? ' ledger-selected' : '')
                  }
                  style={{
                    left: (100 * s.start) / horizon + '%',
                    width: (100 * (s.end - s.start)) / horizon + '%',
                  }}
                  title={`${s.label} · ${clock(s.start)}—${clock(s.end)}\n${s.planId} / ${s.sortieId}`}
                  onClick={() => onSelect?.(s.planId + ':' + s.sortieId)}
                  aria-label={`${id} ${s.label} ${s.sortieId}`}
                >
                  {s.end - s.start > horizon * 0.08 ? s.label : ''}
                </button>
              ))}
            {execution.facts
              .filter((f) => f.kind === 'delivered' && f.drone_id === id && f.time_s <= currentTime)
              .map((f) => (
                <span
                  className="v2-delivery-tick"
                  key={f.fact_id}
                  style={{ left: (100 * f.time_s) / horizon + '%' }}
                  title={`模拟交付 ${f.cargo_ids.join('、')} · ${clock(f.time_s)}`}
                />
              ))}
          </div>
        </div>
      ))}
      {!resources.length && <p className="v2-subtle">此类资源没有生效任务</p>}
    </div>
  )
  return (
    <section className="v2-ledger-panel">
      <div className="v2-section-bar">
        <div>
          <h3>生效排程与模拟事实</h3>
          <small>各段来源独立保留 · 竖线为模拟时标 · 圆点为模拟交付</small>
        </div>
        <div className="v2-table-tools">
          {(['drone', 'battery', 'component'] as const).map((k) => (
            <button className={mode === k ? 'active' : ''} onClick={() => setMode(k)} key={k}>
              {{ drone: '机体', battery: '电池', component: '中继组件' }[k]}
            </button>
          ))}
          <Button onClick={() => setExpanded(true)} aria-label="展开生效排程">
            <Expand size={14} />
          </Button>
        </div>
      </div>
      <div className="v2-ledger-scroll">{content}</div>
      <div className="v2-ledger-legend">
        {[
          ['prepare', '装载/准备'],
          ['flight', '飞行/运输'],
          ['relay', '通信服务'],
          ['ground', '落地周转'],
          ['charge', '计划补能'],
        ].map(([k, t]) => (
          <span key={k}>
            <i className={'ledger-' + k} />
            {t}
          </span>
        ))}
      </div>
      <Modal
        title="生效排程 · 按机体/能源实体核对"
        description="按各份方案来源展示安排；圆点来自模拟交付事实，此视图不修改排程。"
        open={expanded}
        onOpenChange={setExpanded}
        wide
      >
        <div className="v2-ledger-expanded">{content}</div>
      </Modal>
    </section>
  )
}
