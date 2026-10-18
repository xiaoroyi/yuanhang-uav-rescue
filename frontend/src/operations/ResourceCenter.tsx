import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ArrowDownToLine, Layers3, Upload } from 'lucide-react'
import { api } from '../api/client'
import { Button, Empty } from '../components/ui'
import { navigate } from './App'
import { ArchiveCenter } from './ArchiveCenter'

export function ResourceCenter({ notify }: { notify: (m: string, e?: boolean) => void }) {
  const [tab, setTab] = useState('maps')
  const [datum, setDatum] = useState('')
  const [busy, setBusy] = useState(false)
  const assets = useQuery({ queryKey: ['terrain-assets'], queryFn: api.terrainAssets })
  const scenarios = useQuery({ queryKey: ['scenarios'], queryFn: api.scenarios })
  async function upload(file: File) {
    if (!datum.trim()) {
      notify('请先填写高程垂直基准。', true)
      return
    }
    setBusy(true)
    try {
      await api.uploadTerrain(file, datum)
      await assets.refetch()
      notify('地形已入库，可在任务准备中选择绑定。')
    } catch (e) {
      notify((e as Error).message, true)
    } finally {
      setBusy(false)
    }
  }
  return (
    <main className="v2-content">
      <div className="v2-page-heading">
        <div>
          <h1>资源中心</h1>
          <p>管理地图资产，查看各任务的设备与库存。历史输入保留各自版本。</p>
        </div>
      </div>
      <div className="v2-tabs">
        {[
          ['maps', '地图资产'],
          ['fleet', '机队与电池'],
          ['cargo', '物资与保障'],
          ['archives', '运行档案'],
        ].map(([id, title]) => (
          <button key={id} className={tab === id ? 'active' : ''} onClick={() => setTab(id)}>
            {title}
          </button>
        ))}
      </div>
      {tab === 'archives' ? (
        <ArchiveCenter notify={notify} />
      ) : tab === 'maps' ? (
        <section className="v2-card">
          <div className="v2-section-bar">
            <h2>
              <Layers3 size={18} /> 地形资产库
            </h2>
            <div className="v2-table-tools">
              <input
                aria-label="上传地形垂直基准"
                placeholder="垂直基准，例如 EGM96 / m"
                value={datum}
                onChange={(e) => setDatum(e.target.value)}
              />
              <label className="button button-primary">
                <Upload size={14} />
                {busy ? '处理中…' : '上传 GeoTIFF'}
                <input
                  type="file"
                  accept=".tif,.tiff"
                  hidden
                  disabled={busy}
                  onChange={(e) => {
                    const f = e.target.files?.[0]
                    if (f) void upload(f)
                    e.target.value = ''
                  }}
                />
              </label>
            </div>
          </div>
          {assets.error ? (
            <p className="v2-inline-error">{assets.error.message}</p>
          ) : (
            <div className="v2-table-scroll">
              <table className="v2-table">
                <thead>
                  <tr>
                    <th>资产</th>
                    <th>坐标 / 高程参考</th>
                    <th>范围与质量</th>
                    <th>来源与版本</th>
                    <th>原件</th>
                  </tr>
                </thead>
                <tbody>
                  {assets.data?.map((a) => (
                    <tr key={a.asset_id + a.sha256}>
                      <td>
                        <b>{a.name}</b>
                        <small>{a.asset_id}</small>
                      </td>
                      <td>
                        <pre>{JSON.stringify(a, ['crs', 'vertical_datum', 'resolution_m'], 2)}</pre>
                      </td>
                      <td>
                        <details>
                          <summary>查看元数据</summary>
                          <pre>{JSON.stringify(a, null, 2)}</pre>
                        </details>
                      </td>
                      <td>
                        <code>{a.sha256.slice(0, 12)}</code>
                        <small>绑定后写入快照，不随库更新改写历史</small>
                      </td>
                      <td>
                        <a
                          href={`/api/v1/terrain-assets/${encodeURIComponent(a.asset_id)}/source?sha256=${a.sha256}`}
                        >
                          <ArrowDownToLine size={15} />
                          下载
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      ) : (
        <section className="v2-card">
          <div className="v2-section-bar">
            <h2>{tab === 'fleet' ? '各任务机队与电池' : '各任务物资与保障'}</h2>
          </div>
          <p className="v2-help-note">
            演练实体按任务隔离，规格相同不代表同一架真实设备。请进入任务准备核对和编辑。
          </p>
          {scenarios.data?.length ? (
            <table className="v2-table">
              <thead>
                <tr>
                  <th>输入记录</th>
                  <th>机体 / 电池</th>
                  <th>箱件</th>
                  <th>入口</th>
                </tr>
              </thead>
              <tbody>
                {scenarios.data.map((s) => (
                  <tr key={s.scenario_id}>
                    <td>
                      {s.name}
                      <small>
                        {s.scenario_id} · v{s.state_version}
                      </small>
                    </td>
                    <td>
                      {s.drone_count} / {s.battery_count}
                    </td>
                    <td>{s.cargo_count}</td>
                    <td>
                      <Button onClick={() => navigate('missions')}>打开所属任务</Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <Empty
              icon={<Layers3 size={23} />}
              title="暂无任务资源"
              description="创建任务后，在机队保障中选择实体。"
            />
          )}
        </section>
      )}
    </main>
  )
}
