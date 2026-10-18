import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, Download, Upload } from 'lucide-react'
import { ops } from '../api/operations'
import { Button } from '../components/ui'
import { RescueMap } from '../components/RescueMap'
import { ExecutionTimeline } from './ExecutionTimeline'
import { ExecutionInsights } from './ExecutionInsights'
import { clock } from './format'

export function ArchiveCenter({ notify }: { notify: (message: string, error?: boolean) => void }) {
  const [id, setId] = useState(''),
    [busy, setBusy] = useState(false),
    [search, setSearch] = useState(''),
    [at, setAt] = useState<number | null>(null),
    [selected, setSelected] = useState<string | null>(null)
  const list = useQuery({ queryKey: ['execution-archives'], queryFn: ops.archives })
  const archive = useQuery({
    queryKey: ['execution-archive', id],
    queryFn: () => ops.archive(id),
    enabled: !!id,
  })
  const data = archive.data
  async function upload(file: File) {
    if (file.size > 20 * 1024 * 1024) {
      notify('运行档案上限20 MiB。', true)
      return
    }
    setBusy(true)
    try {
      const summary = await ops.importArchive(file)
      await list.refetch()
      setId(summary.archive_id)
      setAt(null)
      notify('运行档案已载入，只读查看不会创建执行实例。')
    } catch (error) {
      notify((error as Error).message, true)
    } finally {
      setBusy(false)
    }
  }
  if (data) {
    const e = data.bundle.execution,
      initial = data.plans.find((p) => p.plan_id === e.initial_plan_id)
    const scene = data.snapshots.find((s) => s.snapshot_id === initial?.snapshot_id)?.scenario
    const time = at ?? e.time_s
    const sources = e.schedule_parts.flatMap((part) => {
      const plan = data.plans.find((p) => p.plan_id === part.plan_id)
      return plan
        ? [
            {
              plan,
              sortieIds: part.sortie_ids,
              relayIds:
                part.relay_sortie_ids ||
                (part.role === 'initial' ? plan.relay_sorties?.map((r) => r.relay_sortie_id) : []),
            },
          ]
        : []
    })
    const delivered = e.facts
      .filter((f) => f.kind === 'delivered' && f.time_s <= time)
      .flatMap((f) => f.cargo_ids).length
    return (
      <div className="v2-archive-detail">
        <div className="v2-section-bar">
          <div>
            <Button
              onClick={() => {
                setId('')
                setSelected(null)
              }}
            >
              <ArrowLeft size={14} />
              档案列表
            </Button>
            <h2>{data.summary.mission_name}</h2>
            <p>
              只读模拟档案 · 截取至 {clock(e.time_s)} · {data.summary.plan_count}份方案 ·{' '}
              {data.summary.fact_count}条事实
            </p>
          </div>
          <Button
            onClick={() => {
              const blob = new Blob([JSON.stringify(data.bundle, null, 2)], {
                type: 'application/json',
              })
              const url = URL.createObjectURL(blob)
              const a = document.createElement('a')
              a.href = url
              a.download = data.summary.archive_id + '.json'
              a.click()
              setTimeout(() => URL.revokeObjectURL(url), 1000)
            }}
          >
            <Download size={14} />
            下载完整档案
          </Button>
        </div>
        <div className="v2-archive-readonly">
          历史事实查看 ·
          不创建实例或预约，不发送控制指令。当前未保存连续实测轨迹；地图展示原方案路线。
        </div>
        <div className="v2-card v2-archive-clock">
          <label>
            事实时间筛选
            <input
              aria-label="档案事实时刻"
              type="range"
              min={0}
              max={Math.max(1, e.time_s)}
              step={1}
              value={time}
              onChange={(event) => setAt(Number(event.target.value))}
            />
          </label>
          <b>{clock(time)}</b>
          <span>此时模拟交付 {delivered} 箱</span>
        </div>
        {scene && initial && (
          <>
            <div className="v2-archive-map">
              <RescueMap
                scenario={scene}
                plan={initial}
                routeSets={sources}
                selected={selected}
                onSelect={setSelected}
                telemetry={time === e.time_s ? e.telemetry : undefined}
              />
            </div>
            <ExecutionTimeline
              sources={sources}
              execution={e}
              currentTime={time}
              onSelect={setSelected}
            />
            <ExecutionInsights
              analysis={{
                ...data.analysis,
                facts_cursor: e.facts.filter((f) => f.time_s <= time).length,
                delivery_rows: data.analysis.delivery_rows.filter((f) => f.time_s <= time),
                deviation_rows: data.analysis.deviation_rows?.filter((r) => r.delivered_s <= time),
                delivered_quantity: delivered,
                unserved_quantity: Math.max(
                  0,
                  data.analysis.unserved_quantity + data.analysis.delivered_quantity - delivered,
                ),
              }}
              initialPlan={initial}
            />
          </>
        )}
        <section className="v2-card">
          <h3>事件与调整留档</h3>
          <div className="v2-table-scroll">
            <table className="v2-table">
              <thead>
                <tr>
                  <th>时刻</th>
                  <th>变化</th>
                  <th>处理</th>
                  <th>核实依据</th>
                </tr>
              </thead>
              <tbody>
                {data.bundle.events.map((v) => (
                  <tr key={v.event_id}>
                    <td>{clock(v.time_s)}</td>
                    <td>{v.reason}</td>
                    <td>
                      {v.status === 'withdrawn'
                        ? '已核实误报'
                        : e.applied_event_ids?.includes(v.event_id)
                          ? '已采纳'
                          : v.status === 'requires_manual'
                            ? '需人工协调'
                            : '待处理'}
                    </td>
                    <td>{v.resolution_reason || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    )
  }
  return (
    <section className="v2-card">
      <div className="v2-section-bar">
        <div>
          <h2>运行档案</h2>
          <p>从执行页下载完整运行包，在这里重新打开。哈希检查用于一致性校验，不代表签名认证。</p>
        </div>
        <label className="button button-primary">
          <Upload size={14} />
          {busy ? '正在校验…' : '导入运行档案'}
          <input
            aria-label="导入只读运行档案"
            type="file"
            accept=".json,application/json"
            hidden
            disabled={busy}
            onChange={(event) => {
              const file = event.target.files?.[0]
              if (file) void upload(file)
              event.target.value = ''
            }}
          />
        </label>
      </div>
      <input
        aria-label="查找运行档案"
        placeholder="搜索任务名称 / 运行编号"
        value={search}
        onChange={(event) => setSearch(event.target.value)}
      />
      {(list.error || archive.error) && (
        <p className="v2-inline-error">{(list.error || archive.error)?.message}</p>
      )}
      <div className="v2-table-scroll">
        <table className="v2-table">
          <thead>
            <tr>
              <th>任务 / 运行</th>
              <th>模拟时标</th>
              <th>方案 / 事实</th>
              <th>导入时间</th>
              <th>查看</th>
            </tr>
          </thead>
          <tbody>
            {list.data
              ?.filter((v) =>
                (v.mission_name + ' ' + v.execution_id)
                  .toLowerCase()
                  .includes(search.toLowerCase()),
              )
              .map((v) => (
                <tr key={v.archive_id}>
                  <td>
                    <b>{v.mission_name}</b>
                    <small>{v.execution_id}</small>
                  </td>
                  <td>{clock(v.captured_time_s)}</td>
                  <td>
                    {v.plan_count}份方案 · {v.fact_count}条事实
                  </td>
                  <td>{new Date(v.imported_at).toLocaleString('zh-CN')}</td>
                  <td>
                    <Button
                      onClick={() => {
                        setId(v.archive_id)
                        setAt(null)
                      }}
                    >
                      打开只读档案
                    </Button>
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
        {!list.data?.length && (
          <p className="v2-subtle">暂无已导入运行档案。执行中的记录仍保存在各救援任务内。</p>
        )}
      </div>
    </section>
  )
}
