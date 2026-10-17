import { useRef, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Mountain, Upload, CheckCircle2, Download } from 'lucide-react'
import { api, type Scenario, type TerrainAsset } from '../api/client'
import { Badge, Button, Modal } from '../components/ui'
import { number, percent } from '../lib/format'

export function TerrainManager({
  scenario,
  onAssigned,
  notify,
}: {
  scenario: Scenario
  onAssigned: (s: Scenario) => void
  notify: (message: string, error?: boolean) => void
}) {
  const query = useQueryClient()
  const [open, setOpen] = useState(false),
    [busy, setBusy] = useState(false)
  const [selected, setSelected] = useState(''),
    [datum, setDatum] = useState(''),
    [meters, setMeters] = useState(false),
    [elevations, setElevations] = useState(true)
  const file = useRef<HTMLInputElement>(null)
  const assets = useQuery({
    queryKey: ['terrain-assets'],
    queryFn: api.terrainAssets,
    enabled: open,
  })
  const chosen = assets.data?.find((a) => a.asset_id === (selected || scenario.terrain.asset_id))
  async function upload(input: File) {
    if (!datum.trim() || !meters) {
      notify('请先声明垂直基准，并确认高程单位为米。', true)
      return
    }
    setBusy(true)
    try {
      const asset = await api.uploadTerrain(input, datum)
      query.setQueryData<TerrainAsset[]>(['terrain-assets'], (old) => [
        ...(old || []).filter((a) => a.asset_id !== asset.asset_id),
        asset,
      ])
      setSelected(asset.asset_id)
      notify('DEM已完成本地准备；点击绑定才会更新当前场景。')
    } catch (error) {
      notify(error instanceof Error ? error.message : 'DEM导入失败', true)
    } finally {
      setBusy(false)
    }
  }
  async function assign() {
    if (!chosen) return
    setBusy(true)
    try {
      const saved = await api.assignTerrain(scenario, chosen, elevations)
      onAssigned(saved)
      setOpen(false)
      notify('DEM已绑定至新版本；重新求解将检查完整航段。')
    } catch (error) {
      notify(error instanceof Error ? error.message : 'DEM绑定失败', true)
    } finally {
      setBusy(false)
    }
  }
  return (
    <>
      <section className="panel zone-panel terrain-panel">
        <div className="zone-heading">
          <h3>
            <Mountain size={17} />
            地形资产
          </h3>
          <Badge tone={scenario.terrain.status === 'available' ? 'teal' : 'amber'}>
            {scenario.terrain.status === 'available' ? '已绑定' : '未提供'}
          </Badge>
        </div>
        <p>
          {scenario.terrain.asset_id === 'contest-dem-30m'
            ? '原题30米DEM · 只读归档'
            : scenario.terrain.asset_id
              ? '本地GeoTIFF · 内容hash绑定'
              : '可导入本地GeoTIFF，地图与净空检查使用同一栅格。'}
        </p>
        {scenario.terrain.sha256 && (
          <code className="terrain-hash">SHA256 {scenario.terrain.sha256.slice(0, 20)}…</code>
        )}
        <Button
          onClick={() => {
            setSelected(scenario.terrain.asset_id || '')
            setOpen(true)
          }}
        >
          <Mountain size={14} />
          管理DEM资产
        </Button>
      </section>
      <Modal
        open={open}
        onOpenChange={setOpen}
        title="本地DEM资产"
        description="栅格准备与场景绑定分开。上传保留原文件，绑定创建新版本，历史快照保持不变。"
        wide
      >
        <div className="zone-editor-grid">
          <section>
            <h4>导入GeoTIFF</h4>
            <label className="field">
              <span>垂直基准 / 数据说明</span>
              <input
                value={datum}
                placeholder="如 WGS84椭球高，单位米"
                onChange={(e) => setDatum(e.target.value)}
              />
            </label>
            <label className="checkbox-field terrain-meter-check">
              <input
                type="checkbox"
                checked={meters}
                onChange={(e) => setMeters(e.target.checked)}
              />
              我确认高程值为米，基准声明与来源一致
            </label>
            <input
              ref={file}
              type="file"
              data-testid="terrain-file"
              hidden
              accept=".tif,.tiff"
              onChange={(e) => {
                const f = e.target.files?.[0]
                if (f) void upload(f)
                e.target.value = ''
              }}
            />
            <Button
              busy={busy}
              onClick={() => file.current?.click()}
              disabled={!datum.trim() || !meters}
            >
              <Upload size={14} />
              选择并准备GeoTIFF
            </Button>
            <p className="callout">
              单波段、带CRS、最大16MiB /
              200万像元。重投影采用高程max并传播未知掩码；NoData或覆盖外不能通过净空检查。准备后的地形仍不代表现实障碍完整。
            </p>
            {assets.isError && (
              <p role="alert" className="zone-error">
                {assets.error.message}
              </p>
            )}
            {assets.isLoading && <p className="callout">正在读取本地资产…</p>}
          </section>
          <section>
            <h4>选择已准备资产</h4>
            <label className="field">
              <span>DEM资产</span>
              <select
                aria-label="DEM资产"
                value={chosen?.asset_id || ''}
                onChange={(e) => setSelected(e.target.value)}
              >
                <option value="" disabled>
                  选择资产
                </option>
                {assets.data?.map((a) => (
                  <option key={a.asset_id} value={a.asset_id}>
                    {a.name}
                  </option>
                ))}
              </select>
            </label>
            {chosen && (
              <div className="terrain-asset-detail">
                <strong>
                  <CheckCircle2 size={15} />
                  {chosen.name}
                </strong>
                <dl>
                  <dt>栅格尺寸</dt>
                  <dd>
                    {chosen.dimensions[0]} × {chosen.dimensions[1]}
                  </dd>
                  <dt>已知高程比例</dt>
                  <dd>{percent(chosen.valid_fraction)}</dd>
                  <dt>原始坐标系</dt>
                  <dd>{chosen.source_crs}</dd>
                  <dt>垂直基准</dt>
                  <dd>{chosen.terrain.vertical_datum}</dd>
                  <dt>经度范围</dt>
                  <dd>
                    {number(chosen.bounds[0], 5)} – {number(chosen.bounds[2], 5)}
                  </dd>
                  <dt>纬度范围</dt>
                  <dd>
                    {number(chosen.bounds[1], 5)} – {number(chosen.bounds[3], 5)}
                  </dd>
                </dl>
                <p>{chosen.processing.join('；')}</p>
                <code className="terrain-hash">{chosen.sha256}</code>
                <a
                  href={`/api/v1/terrain-assets/${chosen.asset_id}/source?sha256=${chosen.sha256}`}
                  className="button button-default"
                >
                  <Download size={13} />
                  下载来源文件
                </a>
              </div>
            )}
            <label className="checkbox-field terrain-meter-check">
              <input
                type="checkbox"
                checked={elevations}
                onChange={(e) => setElevations(e.target.checked)}
              />
              绑定时从DEM提取基地与需求点高程
            </label>
          </section>
        </div>
        <div className="dialog-footer">
          <span>会检查点位覆盖；完整航路在重新求解时检查。</span>
          <Button variant="primary" busy={busy} disabled={!chosen} onClick={() => void assign()}>
            绑定DEM并保存新版本
          </Button>
        </div>
      </Modal>
    </>
  )
}
