import { useId, useState } from 'react'
import type { ExecutionEvent } from '../api/operations'
import { clock } from './format'

type Impact = NonNullable<ExecutionEvent['impact']>
export type ImpactSelection = { planId: string; sortieId: string }

export function DependencyImpactPanel({
  event,
  onSelect,
}: {
  event: ExecutionEvent
  onSelect: (value: ImpactSelection) => void
}) {
  const [showAll, setShowAll] = useState(false)
  const marker = useId().replaceAll(':', '')
  const impact = event.impact
  if (!impact) return <p>此历史事件未保存影响图；保留原计数，不根据当前排程补造历史。</p>
  const rows = showAll ? impact.nodes : impact.nodes.filter((n) => n.affected)
  const nodes = rows.slice(0, 100)
  const resources = [...new Set(nodes.map((n) => n.drone_id))]
  const level = new Map<string, number>()
  for (const n of nodes) {
    const predecessors = impact.edges.filter((edge) => edge.to_node_id === n.node_id)
    level.set(
      n.node_id,
      Math.max(0, ...predecessors.map((edge) => (level.get(edge.from_node_id) ?? -1) + 1)),
    )
  }
  const positions = new Map(
    nodes.map((n) => [
      n.node_id,
      {
        x: 70 + (level.get(n.node_id) ?? 0) * 225,
        y: 30 + resources.indexOf(n.drone_id) * 92,
      },
    ]),
  )
  const width = Math.max(600, ...[...positions.values()].map((p) => p.x + 210))
  const height = Math.max(150, resources.length * 92 + 35)
  const select = (n: Impact['nodes'][number]) =>
    onSelect({ planId: n.plan_id, sortieId: n.sortie_id })
  return (
    <section className="v2-impact-panel" aria-label="事件资源依赖影响图">
      <div className="v2-metrics-line">
        <span>
          直接命中 <b>{impact.nodes.filter((n) => n.direct).length}</b>
        </span>
        <span>
          资源后继传播 <b>{impact.nodes.filter((n) => n.affected && !n.direct).length}</b>
        </span>
        <span>
          已有承诺 <b>{impact.nodes.filter((n) => n.committed).length}</b>
        </span>
        <span>
          未受本图影响 <b>{impact.nodes.filter((n) => !n.affected).length}</b>
        </span>
      </div>
      <div className="v2-section-bar">
        <p>
          事件时刻 {clock(impact.time_s)} · 事实游标 {impact.facts_cursor} · 点击架次核对原文安排
        </p>
        <label>
          <input type="checkbox" checked={showAll} onChange={(e) => setShowAll(e.target.checked)} />{' '}
          显示全部架次
        </label>
      </div>
      <div className="v2-impact-legend">
        <span className="direct">直接命中</span>
        <span className="propagated">后继传播</span>
        <span>蓝线：机体后继</span>
        <span>紫色虚线：电池后继</span>
      </div>
      {nodes.length ? (
        <div className="v2-impact-graph">
          <svg
            width={width}
            height={height}
            role="group"
            aria-label="按机体与电池资源连接的架次依赖图"
          >
            <defs>
              <marker id={marker} markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
                <path d="M0,0 L6,3 L0,6 Z" fill="currentColor" />
              </marker>
            </defs>
            {resources.map((id, i) => (
              <text key={id} x="8" y={60 + i * 92} className="v2-impact-resource">
                {id}
              </text>
            ))}
            {impact.edges.map((edge) => {
              const a = positions.get(edge.from_node_id),
                b = positions.get(edge.to_node_id)
              if (!a || !b) return null
              return (
                <path
                  key={[edge.from_node_id, edge.to_node_id, edge.resource_kind].join('|')}
                  d={`M${a.x + 174},${a.y + 27} C${a.x + 200},${a.y + 27} ${b.x - 26},${b.y + 27} ${b.x},${b.y + 27}`}
                  className={'v2-impact-edge ' + edge.resource_kind}
                  markerEnd={`url(#${marker})`}
                >
                  <title>
                    {edge.resource_kind === 'drone' ? '机体' : '电池'} {edge.resource_id} 资源后继
                  </title>
                </path>
              )
            })}
            {nodes.map((n) => {
              const p = positions.get(n.node_id)!
              return (
                <g
                  key={n.node_id}
                  transform={`translate(${p.x},${p.y})`}
                  className={
                    'v2-impact-node ' +
                    (n.direct ? 'direct' : n.affected ? 'propagated' : 'preserved')
                  }
                  role="button"
                  tabIndex={0}
                  aria-label={`核对 ${n.plan_id} ${n.sortie_id}`}
                  onClick={() => select(n)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault()
                      select(n)
                    }
                  }}
                >
                  <title>
                    {n.plan_id} / {n.sortie_id}\n{n.battery_id} · {n.cargo_ids.length}箱
                    {n.committed ? ' · 已有承诺' : ''}
                  </title>
                  <rect width="174" height="54" rx="6" />
                  <text x="9" y="20">
                    {n.sortie_id.length > 22 ? '…' + n.sortie_id.slice(-21) : n.sortie_id}
                  </text>
                  <text x="9" y="40" className="v2-impact-secondary">
                    {clock(n.takeoff_s)} · {n.cargo_ids.length}箱{n.committed ? ' · 承诺' : ''}
                  </text>
                </g>
              )
            })}
          </svg>
        </div>
      ) : (
        <p className="v2-impact-empty">
          此变化未直接命中已安排运输架次。新增需求仍需要真实重算，空图不表示方案继续有效。
        </p>
      )}
      {rows.length > 100 && (
        <p>图中展示前100个节点；完整 {rows.length} 架次可在下表核对，原始图随运行包保存。</p>
      )}
      <details>
        <summary>逐架次与来源（{rows.length}）</summary>
        <div className="v2-impact-table">
          <table>
            <thead>
              <tr>
                <th>来源 / 架次</th>
                <th>机体 / 电池</th>
                <th>影响与承诺</th>
                <th>起飞—返航</th>
                <th>箱件</th>
                <th>定位</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((n) => (
                <tr key={n.node_id}>
                  <td>
                    {n.plan_id}
                    <small>{n.sortie_id}</small>
                  </td>
                  <td>
                    {n.drone_id}
                    <small>{n.battery_id}</small>
                  </td>
                  <td>
                    {n.direct ? '直接命中' : n.affected ? '后继传播' : '未受本图影响'}
                    {n.committed ? ' · 已有承诺' : ''}
                  </td>
                  <td>
                    {clock(n.takeoff_s)}—{clock(n.return_s)}
                  </td>
                  <td>{n.cargo_ids.join(' · ')}</td>
                  <td>
                    <button onClick={() => select(n)}>核对架次</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
      <p className="v2-chart-note">
        本图是事件记录时的运输机体/电池后继关系；采用调整后仍保留原图。
        {impact.ground_model === 'conservative_common_release'
          ? '有限地面资源按共同释放边界保守处理，未画成不存在的工位分配边。'
          : ''}
        通信窗口未纳入此图；新方案仍须独立检查。
      </p>
    </section>
  )
}
