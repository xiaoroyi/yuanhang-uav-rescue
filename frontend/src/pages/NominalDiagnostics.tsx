import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  ArrowDownToLine,
  CheckCircle2,
  FlaskConical,
  LoaderCircle,
  LockKeyhole,
  RefreshCw,
  TriangleAlert,
} from 'lucide-react'
import { api, downloadJson, type Snapshot } from '../api/client'
import { Badge, Button, Empty } from '../components/ui'
import { duration, number, percent } from '../lib/format'
import './nominal-diagnostics.css'

export function NominalDiagnostics({ snapshot }: { snapshot: Snapshot }) {
  const [reserve, setReserve] = useState(snapshot.scenario.policy.min_return_soc)
  const [tab, setTab] = useState<'capacity' | 'batches' | 'sensitivity'>('capacity')
  const [site, setSite] = useState('all')
  const query = useQuery({
    queryKey: ['nominal', snapshot.snapshot_id, reserve],
    queryFn: () => api.nominal(snapshot.snapshot_id, reserve),
    retry: false,
    staleTime: Infinity,
  })
  const report = query.data
  const scenarios = snapshot.scenario
  const names = new Map(scenarios.sites.map((s) => [s.id, s.name]))
  const reserves = [
    ...new Set([...Array.from({ length: 11 }, (_, i) => i / 10), scenarios.policy.min_return_soc]),
  ].sort((a, b) => a - b)
  const labels = {
    rated_payload: '额定载重上限',
    energy: '能量约束',
    empty_infeasible: '空载也不可达',
    unavailable: '未评估',
  }
  return (
    <div className="nominal-diagnostics" aria-label="单点运输诊断结果">
      <div className="nominal-scope">
        <FlaskConical size={23} />
        <div>
          <strong>额定满电 · SOH 100% · 单点往返</strong>
          <p>检验机型能力与整箱组批。机体数量、电池、充电、时限与通信由正式调度另行评估。</p>
        </div>
        <Badge tone="blue">物理诊断</Badge>
      </div>
      <div className="nominal-controls">
        <span>
          <LockKeyhole size={14} />
          输入已冻结 <b>v{snapshot.scenario_state_version}</b>
        </span>
        <label>
          诊断返航余量
          <select
            aria-label="诊断返航余量"
            value={reserve}
            disabled={query.isFetching}
            onChange={(e) => setReserve(Number(e.target.value))}
          >
            {reserves.map((value) => (
              <option key={value} value={value}>
                {percent(value)}
              </option>
            ))}
          </select>
        </label>
        <Button
          disabled={!report}
          onClick={() =>
            report &&
            downloadJson(
              report,
              `${snapshot.snapshot_id}-nominal-${Math.round(reserve * 100)}.json`,
            )
          }
        >
          <ArrowDownToLine size={14} />
          导出诊断
        </Button>
      </div>
      <div className="nominal-scroll">
        {query.isPending && (
          <div className="nominal-loading" role="status">
            <LoaderCircle className="spin" size={25} />
            <div>
              <h3>重新计算能力与整箱组合</h3>
              <p>按当前快照枚举单站点模式，独立重算能耗与箱件覆盖…</p>
            </div>
          </div>
        )}
        {query.isError && (
          <Empty
            icon={<TriangleAlert size={25} />}
            title="暂时无法完成诊断"
            description={query.error.message}
            action={
              <Button onClick={() => void query.refetch()}>
                <RefreshCw size={14} />
                重试
              </Button>
            }
          />
        )}
        {report && (
          <>
            {report.status !== 'complete' && (
              <div className="nominal-warning" role="status">
                <TriangleAlert size={17} />
                <span>{report.reason} 请查看各站点原因。</span>
              </div>
            )}
            <div className="nominal-metrics">
              <div className="nominal-primary">
                <small>有限单点模型 · 最少架次</small>
                <strong data-testid="nominal-sortie-count">
                  {number(report.metrics?.sortie_count)}
                  <em>架次</em>
                </strong>
                <span>
                  完整需求 {report.required_box_count} 箱 · {report.sites.length} 站
                </span>
              </div>
              <div>
                <small>额定运输总能耗</small>
                <strong>
                  {number(report.metrics?.energy_kwh, 2)}
                  <em>kWh</em>
                </strong>
                <span>逐航段重建，保留返航余量</span>
              </div>
              <div>
                <small>累计作业时长</small>
                <strong className="nominal-duration">
                  {duration(report.metrics?.operation_s)}
                </strong>
                <span>各批次相加，不是完工时间</span>
              </div>
            </div>
            {report.metrics && (
              <div className="nominal-comparison" aria-label="组批基线比较">
                <div>
                  <span>单箱一架次</span>
                  <b>{report.single_box_baseline?.sortie_count} 架次</b>
                  <small>{number(report.single_box_baseline?.energy_kwh, 2)} kWh</small>
                </div>
                <div>
                  <span>确定性贪心组批</span>
                  <b>{report.greedy_baseline?.sortie_count} 架次</b>
                  <small>{number(report.greedy_baseline?.energy_kwh, 2)} kWh</small>
                </div>
                <div>
                  <span>完整计数动态规划</span>
                  <b>{report.metrics.sortie_count} 架次</b>
                  <small>{number(report.metrics.energy_kwh, 2)} kWh</small>
                </div>
              </div>
            )}
            <div className="nominal-table-tools">
              <div className="segmented" aria-label="诊断内容">
                <button
                  className={tab === 'capacity' ? 'active' : ''}
                  onClick={() => setTab('capacity')}
                >
                  安全载重
                </button>
                <button
                  className={tab === 'batches' ? 'active' : ''}
                  onClick={() => setTab('batches')}
                >
                  整箱组批
                </button>
                <button
                  className={tab === 'sensitivity' ? 'active' : ''}
                  onClick={() => setTab('sensitivity')}
                >
                  敏感性与核查
                </button>
              </div>
              {tab !== 'sensitivity' && (
                <select
                  aria-label="诊断需求点"
                  value={site}
                  onChange={(e) => setSite(e.target.value)}
                >
                  <option value="all">全部需求点</option>
                  {scenarios.sites.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.id} · {s.name}
                    </option>
                  ))}
                </select>
              )}
            </div>
            {tab === 'capacity' && (
              <>
                <p className="nominal-help">
                  最大安全质量只受额定载重与当前路径能耗限制；实际整箱组合还须满足机舱体积。不可达与未评估不以
                  0 代替。
                </p>
                <div className="nominal-table-scroll">
                  <table className="data-table" aria-label="单点安全载重">
                    <thead>
                      <tr>
                        <th>需求点 / 机型</th>
                        <th>安全载重</th>
                        <th>容积上限</th>
                        <th>额定电量 / 能耗预算</th>
                        <th>约束与检查</th>
                      </tr>
                    </thead>
                    <tbody>
                      {report.capacities
                        .filter((row) => site === 'all' || row.site_id === site)
                        .map((row) => (
                          <tr key={`${row.site_id}-${row.type_id}`}>
                            <td>
                              <strong>
                                {row.site_id} · {row.type_id}
                              </strong>
                              <small className="nominal-subline">{names.get(row.site_id)}</small>
                            </td>
                            <td>
                              <b>{number(row.capacity_kg, 3)}</b> kg
                            </td>
                            <td>{number(row.max_volume_l)} L</td>
                            <td>
                              {number(row.nominal_energy_kwh, 2)} /{' '}
                              {number(row.allowed_energy_kwh, 2)} kWh
                            </td>
                            <td>
                              <Badge tone={row.capacity_kg == null ? 'amber' : 'teal'}>
                                {labels[row.limit]}
                              </Badge>
                              <small className="nominal-subline">
                                {row.reason ||
                                  (row.terrain_evaluated ? 'DEM路径已检查' : '地形未评估')}
                              </small>
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </>
            )}
            {tab === 'batches' && (
              <>
                <p className="nominal-help">
                  优先最少架次，再比较能耗和累计时长。以下批次未分配实际机体、电池或起飞时刻，须正式求解后才能确认执行。
                </p>
                <div className="nominal-table-scroll">
                  <table className="data-table" aria-label="单点整箱组批">
                    <thead>
                      <tr>
                        <th>需求点 / 机型</th>
                        <th>实际箱件编号</th>
                        <th>质量 / 体积</th>
                        <th>能耗 / 返航SOC</th>
                        <th>作业时长</th>
                      </tr>
                    </thead>
                    <tbody>
                      {report.batches
                        .filter((row) => site === 'all' || row.site_id === site)
                        .map((row) => (
                          <tr key={row.batch_id}>
                            <td>
                              <strong>
                                {row.site_id} · {row.type_id}
                              </strong>
                              <small className="nominal-subline mono">{row.batch_id}</small>
                            </td>
                            <td className="nominal-cargo mono">{row.cargo_ids.join(' · ')}</td>
                            <td>
                              {number(row.mass_kg, 2)} kg / {number(row.volume_l, 2)} L
                            </td>
                            <td>
                              {number(row.energy_kwh, 3)} kWh
                              <small className="nominal-subline">{percent(row.return_soc)}</small>
                            </td>
                            <td>{duration(row.duration_s)}</td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </>
            )}
            {tab === 'sensitivity' && (
              <div className="nominal-audit">
                <h3>返航余量敏感性</h3>
                <p>
                  使用同一快照和完整模式库重新组批。提高余量会缩小可行模式集，最少架次不会因此降低。
                </p>
                <div className="nominal-table-scroll">
                  <table className="data-table" aria-label="返航余量敏感性">
                    <thead>
                      <tr>
                        <th>诊断余量</th>
                        <th>最少架次</th>
                        <th>总能耗</th>
                        <th>累计作业时长</th>
                        <th>状态</th>
                      </tr>
                    </thead>
                    <tbody>
                      {report.sensitivity.map((row) => (
                        <tr key={row.min_return_soc}>
                          <td>{percent(row.min_return_soc)}</td>
                          <td>{number(row.metrics?.sortie_count)}</td>
                          <td>{number(row.metrics?.energy_kwh, 3)} kWh</td>
                          <td>{duration(row.metrics?.operation_s)}</td>
                          <td>
                            <Badge tone={row.status === 'complete' ? 'teal' : 'amber'}>
                              {row.status === 'complete' ? '完整计算' : '部分评估'}
                            </Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <h3>独立核查与适用范围</h3>
                <div className="nominal-checks">
                  {report.audit_checks.map((check) => (
                    <span key={check}>
                      <CheckCircle2 size={14} />
                      {check}
                    </span>
                  ))}
                </div>
                {report.sites
                  .filter((row) => row.status !== 'complete')
                  .map((row) => (
                    <p key={row.site_id} className="nominal-warning">
                      {row.site_id} · {row.reason}
                    </p>
                  ))}
                {report.notes.map((note) => (
                  <p key={note}>{note}</p>
                ))}
                <details>
                  <summary>来源与复现标识</summary>
                  <dl>
                    <dt>Snapshot</dt>
                    <dd>{report.snapshot_id}</dd>
                    <dt>快照内容 SHA-256</dt>
                    <dd>{report.snapshot_content_hash}</dd>
                    <dt>本次诊断输入 SHA-256</dt>
                    <dd>{report.analysis_input_hash}</dd>
                    <dt>模型 / 状态上限</dt>
                    <dd>
                      {report.model_id} / 每站 {report.parameters.max_count_states_per_site}{' '}
                      个计数状态
                    </dd>
                    <dt>实际计算耗时</dt>
                    <dd>{number(report.runtime_s, 3)} s</dd>
                  </dl>
                </details>
              </div>
            )}
          </>
        )}
      </div>
      <div className="nominal-footer">
        <LockKeyhole size={13} />
        本次诊断不改变场景策略，也不生成可执行 Plan。
      </div>
    </div>
  )
}
