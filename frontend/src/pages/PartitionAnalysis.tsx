import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  ArrowDownToLine,
  Box,
  CheckCircle2,
  GitMerge,
  Layers3,
  LoaderCircle,
  LockKeyhole,
  RefreshCw,
  ShieldCheck,
  TriangleAlert,
} from 'lucide-react'
import { api, downloadJson, type Plan } from '../api/client'
import { Badge, Button, Empty } from '../components/ui'
import { clock, duration, number } from '../lib/format'
import './partition-analysis.css'

export function PartitionAnalysis({
  plan,
  onConfigure,
}: {
  plan: Plan | null
  onConfigure: () => void
}) {
  const [groupCount, setGroupCount] = useState<2 | 3>(2)
  const [preference, setPreference] = useState<'resource_first' | 'balanced_first'>(
    'resource_first',
  )
  const query = useQuery({
    queryKey: ['partition', plan?.plan_id],
    queryFn: () => api.partition(plan!.plan_id),
    enabled: !!plan?.communication_report,
    retry: false,
  })
  if (!plan?.communication_report)
    return (
      <section className="panel partition-empty">
        <Empty
          icon={<GitMerge size={28} />}
          title="先建立完整的联合保障方案"
          description="分区继承运输任务和实际通信保障关系。请开启连续通信并生成通过检查的方案，再计算各组独立执行需要的资源。"
          action={<Button onClick={onConfigure}>配置通信资源</Button>}
        />
      </section>
    )
  const report = query.data
  if (query.isPending)
    return (
      <section className="panel partition-loading" role="status">
        <LoaderCircle className="spin" size={24} />
        <div>
          <h3>复核联合方案，计算独立任务组</h3>
          <p>保持所有任务和时刻，重建连通关系并枚举合法划分…</p>
        </div>
      </section>
    )
  if (query.isError)
    return (
      <section className="panel partition-empty">
        <Empty
          icon={<TriangleAlert size={26} />}
          title="暂时无法计算分区"
          description={query.error.message}
          action={
            <Button onClick={() => void query.refetch()}>
              <RefreshCw size={14} />
              重新计算
            </Button>
          }
        />
      </section>
    )
  if (!report) return null
  if (report.status !== 'ready')
    return (
      <section className="panel partition-empty">
        <Empty
          icon={<LockKeyhole size={26} />}
          title="当前方案不满足分区模型条件"
          description={report.reason || '请检查资源和方案来源。'}
        />
        <div className="partition-notes">
          {report.notes.map((note) => (
            <p key={note}>{note}</p>
          ))}
        </div>
      </section>
    )
  const variant = report.variants.find((v) => v.group_count === groupCount)
  const selected = variant?.[preference]
  const labels = new Map(report.resource_classes.map((c) => [c.key, c.label]))
  const shortages = selected?.configuration.filter((r) => r.shortfall > 0) || []
  const totalWork = selected?.groups.reduce((sum, group) => sum + group.workload_s, 0) || 1
  return (
    <div className="partition-analysis" aria-label="冻结方案分区分析">
      <section className="panel partition-intro">
        <div className="partition-title">
          <span className="partition-symbol">
            <GitMerge size={25} />
          </span>
          <div>
            <div className="eyebrow">FROZEN PLAN · DEDICATED RESOURCES</div>
            <h3>让每个任务组，都有独立的保障能力</h3>
            <p>冻结任务与通信来源，比较分区后的资源配置、工作量和共享损失。</p>
          </div>
          <Badge tone="teal">
            <ShieldCheck size={12} />
            独立核查通过
          </Badge>
        </div>
        <div className="partition-source">
          <LockKeyhole size={14} />
          <span>
            冻结来源 <strong>v{report.scenario_state_version}</strong>
          </span>
          <code>{report.plan_id}</code>
          <span>{report.atoms.length} 个不可拆分单元</span>
          <Button onClick={() => downloadJson(report, `${report.plan_id}-partition.json`)}>
            <ArrowDownToLine size={14} />
            导出完整分区
          </Button>
        </div>
      </section>
      <div className="partition-controls">
        <div className="segmented" aria-label="分区数量">
          {([2, 3] as const).map((k) => (
            <button
              key={k}
              className={groupCount === k ? 'active' : ''}
              onClick={() => setGroupCount(k)}
            >
              {k} 个任务组
            </button>
          ))}
        </div>
        <div className="segmented" aria-label="分区偏好">
          <button
            className={preference === 'resource_first' ? 'active' : ''}
            onClick={() => setPreference('resource_first')}
          >
            资源优先
          </button>
          <button
            className={preference === 'balanced_first' ? 'active' : ''}
            onClick={() => setPreference('balanced_first')}
          >
            均衡优先
          </button>
        </div>
        <span>{variant?.candidate_count || 0} 种合法划分 · 完整枚举</span>
      </div>
      <section className="partition-atoms panel">
        <div className="panel-heading">
          <div>
            <h3>
              <GitMerge size={16} />
              为什么有些站点必须放在一起？
            </h3>
            <p>多站运输或同一中继任务的实际服务关系，会把站点连接成不可拆分单元。</p>
          </div>
        </div>
        <div className="partition-atom-grid">
          {report.atoms.map((atom, index) => (
            <div className={`partition-atom tone-${index % 3}`} key={atom.atom_id}>
              <header>
                <Badge>{atom.atom_id}</Badge>
                <span>{atom.site_ids.length} 个站点</span>
              </header>
              <strong>{atom.site_ids.join(' · ')}</strong>
              <small>
                {atom.transport_sortie_ids.length} 个运输任务 · {atom.relay_sortie_ids.length}{' '}
                个中继任务
              </small>
            </div>
          ))}
        </div>
      </section>
      {!selected ? (
        <section className="panel partition-empty">
          <Empty
            icon={<LockKeyhole size={25} />}
            title={`当前冻结方案不能拆为 ${groupCount} 组`}
            description={variant?.reason || '没有合法划分。'}
          />
        </section>
      ) : (
        <>
          <div className="partition-kpis">
            <div>
              <small>合法划分</small>
              <strong>
                {variant!.candidate_count}
                <em>种</em>
              </strong>
              <span>当前选择 {preference === 'resource_first' ? '资源优先' : '均衡优先'}</span>
            </div>
            <div>
              <small>需要补足的资源类别</small>
              <strong className={shortages.length ? 'partition-amber' : 'teal'}>
                {shortages.length}
                <em>类</em>
              </strong>
              <span>{shortages.length ? '具体数量见配置对比' : '现有库存可支持冻结任务'}</span>
            </div>
            <div>
              <small>组间工作量差异 CV</small>
              <strong>
                {number(Math.sqrt(Math.max(0, selected.workload_cv2)) * 100, 1)}
                <em>%</em>
              </strong>
              <span>越接近 0，工作量越均衡</span>
            </div>
            <div>
              <small>冻结任务总工作量</small>
              <strong>
                {number(totalWork / 3600, 2)}
                <em>小时</em>
              </strong>
              <span>并行任务累计，不是墙钟完成时间</span>
            </div>
          </div>
          {shortages.length > 0 && (
            <div className="callout amber partition-shortage" role="status">
              <TriangleAlert size={18} />
              <span>
                保持当前任务时序并禁止跨组共享，需要补充：
                {shortages.map((r) => `${labels.get(r.resource_key)} ${r.shortfall} 个`).join('、')}
                。这些增配尚未写入原场景。
              </span>
            </div>
          )}
          <div className="partition-group-grid">
            {selected.groups.map((group, index) => (
              <section
                className={`panel partition-group tone-${index % 3}`}
                key={group.group_id}
                aria-label={`任务组 ${index + 1}`}
              >
                <header>
                  <span className="partition-group-number">0{index + 1}</span>
                  <div>
                    <h3>任务组 {index + 1}</h3>
                    <p>
                      {group.site_ids.length} 个站点 · {group.box_count} 箱物资
                    </p>
                  </div>
                  <Badge>{group.atom_ids.join(' + ')}</Badge>
                </header>
                <div className="partition-group-sites">
                  {group.site_ids.map((site) => (
                    <span key={site}>{site}</span>
                  ))}
                </div>
                <div className="partition-workload">
                  <span>累计工作量</span>
                  <strong>{duration(group.workload_s)}</strong>
                  <div>
                    <i style={{ width: `${(group.workload_s / totalWork) * 100}%` }} />
                  </div>
                  <small>占全部工作量 {number((group.workload_s / totalWork) * 100, 1)}%</small>
                </div>
                <div className="partition-group-tasks">
                  <span>
                    <Box size={14} />
                    运输 {group.transport_sortie_ids.length} 架次
                  </span>
                  <span>
                    <Layers3 size={14} />
                    中继 {group.relay_sortie_ids.length} 架次
                  </span>
                </div>
                <div className="partition-resource-chips">
                  {group.resources
                    .filter((r) => r.required_count > 0)
                    .map((r) => (
                      <span key={r.resource_key}>
                        {labels.get(r.resource_key)}
                        <strong>{r.required_count}</strong>
                      </span>
                    ))}
                </div>
                <details className="partition-assignment-details">
                  <summary>查看峰值见证与实体分配</summary>
                  {group.resources
                    .filter((r) => r.required_count > 0)
                    .map((r) => (
                      <div key={r.resource_key}>
                        <h4>
                          {labels.get(r.resource_key)} · 峰值 {r.required_count}
                        </h4>
                        <p>
                          在 {r.peak_at_s == null ? '—' : clock(r.peak_at_s)} 同时占用；任务：
                          {r.peak_task_ids.join('、')}
                        </p>
                        <div className="table-scroll">
                          <table className="data-table">
                            <thead>
                              <tr>
                                <th>冻结任务</th>
                                <th>专用资源</th>
                                <th>占用时间</th>
                              </tr>
                            </thead>
                            <tbody>
                              {r.assignments.map((a) => (
                                <tr key={a.task_id}>
                                  <td>
                                    <code>{a.task_id}</code>
                                  </td>
                                  <td>
                                    <code>{a.allocated_resource_id}</code>
                                    {a.needs_addition && <Badge tone="amber">需增配</Badge>}
                                  </td>
                                  <td>
                                    {clock(a.start_s)} → {clock(a.end_s)}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    ))}
                </details>
              </section>
            ))}
          </div>
          <section className="panel partition-configuration">
            <div className="panel-heading">
              <div>
                <h3>配置对比与共享损失</h3>
                <p>共享池与分组专用配置使用同一批冻结任务。资源峰值按左闭右开区间精确扫描。</p>
              </div>
              <Badge tone={selected.fits_inventory ? 'teal' : 'amber'}>
                {selected.fits_inventory ? '库存满足' : '需补充资源'}
              </Badge>
            </div>
            <div className="table-scroll">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>资源类别</th>
                    <th>可用库存</th>
                    <th>共享池峰值</th>
                    <th>分区总配置</th>
                    <th>共享损失</th>
                    <th>库存缺口</th>
                    <th>未分配库存</th>
                  </tr>
                </thead>
                <tbody>
                  {selected.configuration.map((row) => (
                    <tr key={row.resource_key}>
                      <td>
                        <strong>{labels.get(row.resource_key)}</strong>
                      </td>
                      <td>{row.inventory}</td>
                      <td>{row.pooled_required}</td>
                      <td>
                        <strong>{row.partition_required}</strong>
                      </td>
                      <td>{row.extra_vs_pool > 0 ? `+${row.extra_vs_pool}` : '—'}</td>
                      <td>
                        <Badge tone={row.shortfall ? 'amber' : 'teal'}>
                          {row.shortfall ? `需补 ${row.shortfall}` : '满足'}
                        </Badge>
                      </td>
                      <td>{row.unallocated_stock}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
      <section className="panel partition-evidence">
        <div>
          <CheckCircle2 size={19} />
          <h3>每项配置，都有可核查的依据</h3>
        </div>
        <div className="partition-audit-list">
          {report.audit_checks.map((check) => (
            <span key={check}>
              <CheckCircle2 size={13} />
              {check}
            </span>
          ))}
        </div>
        <details>
          <summary>冻结来源与适用条件</summary>
          <dl>
            <dt>Snapshot</dt>
            <dd>{report.snapshot_id}</dd>
            <dt>输入 SHA-256</dt>
            <dd>{report.snapshot_content_hash}</dd>
            <dt>原方案 SHA-256</dt>
            <dd>{report.source_plan_hash}</dd>
          </dl>
          {report.notes.map((note) => (
            <p key={note}>{note}</p>
          ))}
          <p>
            排序使用有理数，优先级为
            {preference === 'resource_first'
              ? '归一化缺口 → 配置量 → 工作量CV²'
              : '工作量CV² → 归一化缺口 → 配置量'}
            。专用资源重新编号不修改原Plan。
          </p>
        </details>
      </section>
    </div>
  )
}
