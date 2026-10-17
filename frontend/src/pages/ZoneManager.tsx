import { useRef, useState } from 'react'
import { ShieldAlert, Upload, Trash2, Plus } from 'lucide-react'
import type { Scenario } from '../api/client'
import { Badge, Button, Modal } from '../components/ui'

type Zone = NonNullable<Scenario['restricted_zones']>[number]

export function ZoneManager({
  scenario,
  onSave,
  notify,
}: {
  scenario: Scenario
  onSave: (s: Scenario) => Promise<void>
  notify: (message: string, error?: boolean) => void
}) {
  const [open, setOpen] = useState(false),
    [busy, setBusy] = useState(false)
  const [text, setText] = useState('[]')
  const [name, setName] = useState('临时限制区'),
    [buffer, setBuffer] = useState('50')
  const [bounds, setBounds] = useState(['', '', '', ''])
  const file = useRef<HTMLInputElement>(null)
  let zones: Zone[] = []
  let parseError = ''
  try {
    const value: unknown = JSON.parse(text)
    if (!Array.isArray(value)) throw new Error('请输入限制区数组。')
    if (
      value.length > 12 ||
      value.some(
        (z) =>
          !z ||
          typeof z !== 'object' ||
          typeof z.name !== 'string' ||
          typeof z.zone_id !== 'string' ||
          typeof z.buffer_m !== 'number',
      )
    )
      throw new Error('每项需要zone_id、名称、数值buffer_m；最多12处。')
    zones = value as Zone[]
  } catch (error) {
    parseError = error instanceof Error ? error.message : 'JSON无效'
  }
  function begin() {
    setText(JSON.stringify(scenario.restricted_zones || [], null, 2))
    const [x, y] = scenario.base.coordinates
    const [u, v] = scenario.sites[0].coordinates
    const center = [(x + u) / 2, (y + v) / 2]
    setBounds(
      [center[0] - 0.003, center[1] - 0.002, center[0] + 0.003, center[1] + 0.002].map((n) =>
        n.toFixed(6),
      ),
    )
    setOpen(true)
  }
  function addRectangle() {
    const [west, south, east, north] = bounds.map(Number)
    if (
      parseError ||
      bounds.some((x) => !x.trim()) ||
      ![west, south, east, north, Number(buffer)].every(Number.isFinite) ||
      west >= east ||
      south >= north ||
      !name.trim()
    ) {
      notify('请先修正JSON，并填写有效名称、矩形边界与缓冲距离。', true)
      return
    }
    const zone: Zone = {
      zone_id: 'ZONE-' + crypto.randomUUID(),
      name: name.trim(),
      buffer_m: Number(buffer),
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [west, south],
            [east, south],
            [east, north],
            [west, north],
            [west, south],
          ],
        ],
      },
    }
    setText(JSON.stringify([...zones, zone], null, 2))
  }
  async function importFile(input: File) {
    try {
      if (input.size > 2 * 1024 * 1024) throw new Error('限制区文件不能超过2MiB。')
      const data = JSON.parse(await input.text())
      const features =
        data.type === 'FeatureCollection'
          ? data.features
          : data.type === 'Feature'
            ? [data]
            : [{ geometry: data }]
      if (!Array.isArray(features) || features.length > 12) throw new Error('每次最多12个Polygon。')
      const imported: Zone[] = features.map((f, i) => ({
        zone_id:
          typeof f.properties?.zone_id === 'string'
            ? f.properties.zone_id
            : 'ZONE-' + crypto.randomUUID(),
        name: typeof f.properties?.name === 'string' ? f.properties.name : `导入限制区 ${i + 1}`,
        buffer_m: f.properties?.buffer_m ?? 50,
        geometry: f.geometry,
      }))
      if (imported.some((z) => z.geometry?.type !== 'Polygon'))
        throw new Error('只支持单外环Polygon，暂不支持MultiPolygon。')
      setText(JSON.stringify(imported, null, 2))
      notify('已载入替换草稿；检查内容后保存才会更新场景。')
    } catch (error) {
      notify(error instanceof Error ? error.message : '导入失败', true)
    }
  }
  async function save() {
    setBusy(true)
    try {
      await onSave({ ...scenario, restricted_zones: zones })
      setOpen(false)
      notify('限制区已保存；重新求解将使用新的场景版本。')
    } catch (error) {
      notify(error instanceof Error ? error.message : '限制区保存失败', true)
    } finally {
      setBusy(false)
    }
  }
  return (
    <>
      <section className="panel zone-panel">
        <div className="zone-heading">
          <h3>
            <ShieldAlert size={17} />
            限制区与缓冲
          </h3>
          <Badge tone={scenario.restricted_zones?.length ? 'amber' : 'neutral'}>
            {scenario.restricted_zones?.length || 0} 处
          </Badge>
        </div>
        <p>静态区域全时禁止穿越。路线、能耗和计划回放随绕行重新计算。</p>
        {!!scenario.restricted_zones?.length && (
          <div className="zone-saved-list">
            {scenario.restricted_zones.map((z) => (
              <span key={z.zone_id}>
                <i />
                {z.name}
                <b>+{z.buffer_m}m</b>
              </span>
            ))}
          </div>
        )}
        <Button onClick={begin}>
          <ShieldAlert size={14} />
          管理限制区
        </Button>
      </section>
      <Modal
        open={open}
        onOpenChange={setOpen}
        title="限制区与安全缓冲"
        description="基地100km内的静态单外环Polygon；保存创建新版本，旧方案保持不变。"
        wide
      >
        <div className="zone-editor-grid">
          <section>
            <h4>快速添加矩形</h4>
            <div className="form-grid">
              <label className="field">
                <span>限制区名称</span>
                <input value={name} onChange={(e) => setName(e.target.value)} />
              </label>
              <label className="field">
                <span>安全缓冲 / m</span>
                <input
                  type="number"
                  min="0"
                  max="5000"
                  value={buffer}
                  onChange={(e) => setBuffer(e.target.value)}
                />
              </label>
              {['西边经度', '南边纬度', '东边经度', '北边纬度'].map((label, i) => (
                <label className="field" key={label}>
                  <span>{label}</span>
                  <input
                    type="number"
                    step="any"
                    value={bounds[i]}
                    onChange={(e) =>
                      setBounds(bounds.map((v, j) => (i === j ? e.target.value : v)))
                    }
                  />
                </label>
              ))}
            </div>
            <Button onClick={addRectangle} disabled={busy}>
              <Plus size={14} />
              加入草稿
            </Button>
            <p className="callout">
              边界和缓冲均属于禁入范围；含区内基地或服务点的场景将阻止计算。地图显示原始边界，航路另加安全缓冲。
            </p>
            <input
              ref={file}
              type="file"
              hidden
              accept=".json,.geojson"
              onChange={(e) => {
                const f = e.target.files?.[0]
                if (f) void importFile(f)
                e.target.value = ''
              }}
            />
            <Button onClick={() => file.current?.click()} disabled={busy}>
              <Upload size={14} />
              导入GeoJSON替换草稿
            </Button>
          </section>
          <section>
            <h4>待保存限制区 · {zones.length} 处</h4>
            <div className="zone-draft-list">
              {zones.map((z, i) => (
                <div key={i}>
                  <span>
                    {z.name || '未命名'}
                    <small>{z.buffer_m}m缓冲</small>
                  </span>
                  <button
                    aria-label={`移除限制区${i + 1}`}
                    onClick={() =>
                      setText(
                        JSON.stringify(
                          zones.filter((_, j) => i !== j),
                          null,
                          2,
                        ),
                      )
                    }
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
            </div>
            <label className="field">
              <span>限制区JSON · 可编辑任意多边形</span>
              <textarea
                className="json-editor zone-json"
                aria-label="限制区JSON"
                value={text}
                onChange={(e) => setText(e.target.value)}
              />
            </label>
            {parseError && (
              <p role="alert" className="zone-error">
                {parseError}
              </p>
            )}
          </section>
        </div>
        <div className="dialog-footer">
          <span>未保存的草稿不影响当前场景。</span>
          <Button variant="primary" busy={busy} disabled={!!parseError} onClick={() => void save()}>
            保存限制区
          </Button>
        </div>
      </Modal>
    </>
  )
}
