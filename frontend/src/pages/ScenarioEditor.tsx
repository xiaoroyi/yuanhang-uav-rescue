import { useMemo, useRef, useState } from 'react'
import {
  ArrowDownToLine,
  Box,
  CheckCircle2,
  ChevronRight,
  Database,
  Edit3,
  FileJson,
  MapPin,
  Package,
  Plane,
  Plus,
  Search,
  Settings2,
  ShieldCheck,
  Trash2,
  Upload,
  Battery,
} from 'lucide-react'
import { api, downloadJson, type Scenario } from '../api/client'
import { RescueMap } from '../components/RescueMap'
import { Badge, Button, Modal } from '../components/ui'
import { category, number, originLabel, percent, statusLabel } from '../lib/format'
import { ZoneManager } from './ZoneManager'
import { TerrainManager } from './TerrainManager'

type Group = 'sites' | 'demands' | 'cargo_items' | 'drone_types' | 'drones' | 'batteries'
type Row = Record<string, unknown>
type Field = {
  key: string
  label: string
  kind?: 'number' | 'select' | 'boolean'
  options?: string[]
  nullable?: boolean
}
const groups: {
  key: Group
  label: string
  icon: typeof Package
  id: string
  columns: { key: string; label: string }[]
}[] = [
  {
    key: 'sites',
    label: '需求点',
    icon: MapPin,
    id: 'id',
    columns: [
      { key: 'id', label: '编号' },
      { key: 'name', label: '需求点名称' },
      { key: 'coordinates', label: '经纬度' },
      { key: 'ground_elevation_m', label: '高程 / m' },
      { key: 'available', label: '状态' },
    ],
  },
  {
    key: 'demands',
    label: '救援需求',
    icon: Package,
    id: 'demand_id',
    columns: [
      { key: 'demand_id', label: '需求编号' },
      { key: 'site_id', label: '目的地' },
      { key: 'cargo_type', label: '物资类型' },
      { key: 'required_quantity', label: '需求 / 箱' },
      { key: 'hard_deadline_s', label: '硬截止 / s' },
    ],
  },
  {
    key: 'cargo_items',
    label: '箱件库存',
    icon: Box,
    id: 'cargo_id',
    columns: [
      { key: 'cargo_id', label: '箱件编号' },
      { key: 'type', label: '物资类型' },
      { key: 'mass_kg', label: '质量 / kg' },
      { key: 'volume_l', label: '体积 / L' },
      { key: 'status', label: '当前状态' },
    ],
  },
  {
    key: 'drones',
    label: '运输机',
    icon: Plane,
    id: 'drone_id',
    columns: [
      { key: 'drone_id', label: '机体编号' },
      { key: 'type_id', label: '机型' },
      { key: 'status', label: '当前状态' },
      { key: 'location_id', label: '位置' },
      { key: 'available_after_s', label: '可用时间 / s' },
    ],
  },
  {
    key: 'batteries',
    label: '电池',
    icon: Battery,
    id: 'battery_id',
    columns: [
      { key: 'battery_id', label: '电池编号' },
      { key: 'compatible_type_id', label: '兼容机型' },
      { key: 'soc', label: '当前电量' },
      { key: 'soh', label: '健康度' },
      { key: 'capacity_kwh', label: '容量 / kWh' },
      { key: 'status', label: '状态' },
    ],
  },
  {
    key: 'drone_types',
    label: '机型参数',
    icon: Settings2,
    id: 'type_id',
    columns: [
      { key: 'type_id', label: '机型' },
      { key: 'max_payload_kg', label: '载重 / kg' },
      { key: 'max_volume_l', label: '容积 / L' },
      { key: 'cruise_speed_mps', label: '速度 / m/s' },
      { key: 'empty_mass_kg', label: '空载质量 / kg' },
    ],
  },
]
function getValue(row: Row, key: string): unknown {
  return key
    .split('.')
    .reduce<unknown>((v, k) => (v && typeof v === 'object' ? (v as Row)[k] : undefined), row)
}
function setValue(row: Row, key: string, value: unknown) {
  const parts = key.split('.')
  let target = row
  for (const p of parts.slice(0, -1)) target = target[p] as Row
  target[parts.at(-1)!] = value
}

export function ScenarioEditor({
  scenario,
  onSave,
  onCreated,
  notify,
  onWorkspace,
}: {
  scenario: Scenario
  onSave: (s: Scenario) => Promise<void>
  onCreated: (s: Scenario) => void
  notify: (message: string, error?: boolean) => void
  onWorkspace: () => void
}) {
  const [group, setGroup] = useState<Group>('cargo_items'),
    [search, setSearch] = useState(''),
    [editing, setEditing] = useState<{ index: number; row: Row } | null>(null),
    [values, setValues] = useState<Record<string, string>>({}),
    [saving, setSaving] = useState(false),
    [jsonOpen, setJsonOpen] = useState(false),
    [jsonText, setJsonText] = useState(''),
    [importing, setImporting] = useState(false),
    [preview, setPreview] = useState<Scenario | null>(null),
    [settings, setSettings] = useState(false)
  const fileInput = useRef<HTMLInputElement>(null)
  const meta = groups.find((g) => g.key === group)!,
    rows = scenario[group] as unknown as Row[]
  const visible = useMemo(
    () =>
      rows
        .map((row, index) => ({ row, index }))
        .filter(({ row }) => JSON.stringify(row).toLowerCase().includes(search.toLowerCase())),
    [rows, search],
  )
  const fields = useMemo<Field[]>(() => {
    const locations = [scenario.base.id, ...scenario.sites.map((s) => s.id)],
      types = scenario.drone_types.map((t) => t.type_id)
    switch (group) {
      case 'sites':
        return [
          { key: 'id', label: '需求点编号' },
          { key: 'name', label: '需求点名称' },
          { key: 'coordinates.0', label: '经度', kind: 'number' },
          { key: 'coordinates.1', label: '纬度', kind: 'number' },
          { key: 'ground_elevation_m', label: '地面高程 / m', kind: 'number', nullable: true },
          { key: 'available', label: '投送点可用', kind: 'boolean' },
        ]
      case 'demands':
        return [
          { key: 'demand_id', label: '需求编号' },
          {
            key: 'site_id',
            label: '需求点',
            kind: 'select',
            options: scenario.sites.map((s) => s.id),
          },
          { key: 'cargo_type', label: '物资类别' },
          { key: 'required_quantity', label: '所需箱数', kind: 'number' },
          { key: 'priority', label: '优先级', kind: 'number' },
          { key: 'expected_deadline_s', label: '期望完成 / s', kind: 'number', nullable: true },
          { key: 'hard_deadline_s', label: '硬截止 / s', kind: 'number', nullable: true },
          { key: 'mandatory', label: '必须保障', kind: 'boolean' },
        ]
      case 'cargo_items':
        return [
          { key: 'cargo_id', label: '箱件编号' },
          {
            key: 'demand_id',
            label: '对应需求',
            kind: 'select',
            options: scenario.demands.map((d) => d.demand_id),
          },
          { key: 'type', label: '物资类别' },
          { key: 'mass_kg', label: '质量 / kg', kind: 'number' },
          { key: 'volume_l', label: '体积 / L', kind: 'number' },
          {
            key: 'status',
            label: '箱件状态',
            kind: 'select',
            options: ['available', 'reserved', 'loaded', 'in_transit', 'delivered', 'unavailable'],
          },
          { key: 'location_id', label: '所在位置', kind: 'select', options: locations },
        ]
      case 'drones':
        return [
          { key: 'drone_id', label: '机体编号' },
          { key: 'type_id', label: '机型', kind: 'select', options: types },
          {
            key: 'status',
            label: '当前状态',
            kind: 'select',
            options: ['available', 'unavailable'],
          },
          { key: 'location_id', label: '当前位置', kind: 'select', options: locations },
          { key: 'available_after_s', label: '最早可用时间 / s', kind: 'number' },
        ]
      case 'batteries':
        return [
          { key: 'battery_id', label: '电池编号' },
          { key: 'compatible_type_id', label: '兼容机型', kind: 'select', options: types },
          { key: 'capacity_kwh', label: '可用容量 / kWh', kind: 'number' },
          { key: 'soc', label: 'SOC比例 / 0–1', kind: 'number' },
          { key: 'soh', label: 'SOH比例 / 0–1', kind: 'number' },
          {
            key: 'status',
            label: '当前状态',
            kind: 'select',
            options: ['available', 'charging', 'unavailable'],
          },
          { key: 'location_id', label: '当前位置', kind: 'select', options: locations },
          { key: 'available_after_s', label: '最早可用时间 / s', kind: 'number' },
        ]
      case 'drone_types':
        return [
          { key: 'type_id', label: '机型编号' },
          { key: 'max_payload_kg', label: '最大载重 / kg', kind: 'number' },
          { key: 'max_volume_l', label: '装载容积 / L', kind: 'number' },
          { key: 'empty_mass_kg', label: '含电池空载质量 / kg', kind: 'number' },
          { key: 'cruise_speed_mps', label: '巡航速度 / m/s', kind: 'number' },
          { key: 'climb_speed_mps', label: '爬升速度 / m/s', kind: 'number' },
          { key: 'descent_speed_mps', label: '下降速度 / m/s', kind: 'number' },
          {
            key: 'energy_model.parameters.empty_range_m',
            label: '空载标准航程 / m',
            kind: 'number',
          },
          {
            key: 'energy_model.parameters.full_range_m',
            label: '满载标准航程 / m',
            kind: 'number',
          },
          {
            key: 'charge_model.parameters.full_charge_s',
            label: '等效完全充电 / s',
            kind: 'number',
          },
        ]
    }
  }, [scenario, group])
  function edit(index: number) {
    let row: Row
    if (index >= 0) row = structuredClone(rows[index])
    else if (rows.length) {
      row = structuredClone(rows[0])
      row[meta.id] = (group === 'sites' ? 'S' : 'NEW') + '-' + Date.now().toString(36).toUpperCase()
    } else {
      const defaults: Record<Group, Row> = {
        sites: {
          id: 'S-NEW',
          name: '新需求点',
          coordinates: scenario.base.coordinates.slice(),
          ground_elevation_m: null,
          available: true,
        },
        demands: {
          demand_id: 'D-NEW',
          site_id: scenario.sites[0].id,
          cargo_type: 'MED',
          required_quantity: 1,
          priority: 1,
          expected_deadline_s: null,
          hard_deadline_s: null,
          mandatory: true,
        },
        cargo_items: {
          cargo_id: 'BOX-NEW',
          demand_id: scenario.demands[0].demand_id,
          type: scenario.demands[0].cargo_type,
          mass_kg: 1,
          volume_l: 1,
          status: 'available',
          location_id: scenario.base.id,
        },
        drones: {
          drone_id: 'U-NEW',
          type_id: scenario.drone_types[0].type_id,
          status: 'available',
          location_id: scenario.base.id,
          available_after_s: 0,
        },
        batteries: {
          battery_id: 'BAT-NEW',
          compatible_type_id: scenario.drone_types[0].type_id,
          capacity_kwh: 4,
          soc: 1,
          soh: 1,
          status: 'available',
          location_id: scenario.base.id,
          available_after_s: 0,
        },
        drone_types: {},
      }
      row = defaults[group]
    }
    setEditing({ index, row })
    setValues(
      Object.fromEntries(
        fields.map((f) => [
          f.key,
          getValue(row, f.key) == null ? '' : String(getValue(row, f.key)),
        ]),
      ),
    )
  }
  async function saveRow() {
    if (!editing) return
    const row = structuredClone(editing.row)
    for (const f of fields) {
      const v = values[f.key] ?? ''
      setValue(
        row,
        f.key,
        f.kind === 'boolean'
          ? v === 'true'
          : f.kind === 'number'
            ? v === '' && f.nullable
              ? null
              : Number(v)
            : v,
      )
    }
    const next = structuredClone(scenario)
    const target = next[group] as unknown as Row[]
    if (editing.index < 0) target.push(row)
    else target[editing.index] = row
    setSaving(true)
    try {
      await onSave(next)
      setEditing(null)
      notify('已保存修改，场景版本已更新。')
    } catch (error) {
      notify((error as Error).message, true)
    } finally {
      setSaving(false)
    }
  }
  async function remove(index: number) {
    const next = structuredClone(scenario)
    ;(next[group] as unknown[]).splice(index, 1)
    setSaving(true)
    try {
      await onSave(next)
      notify('已移除该记录，历史版本仍可追溯。')
    } catch (error) {
      notify((error as Error).message, true)
    } finally {
      setSaving(false)
    }
  }
  async function importFile(file: File) {
    setImporting(true)
    try {
      const result = await api.preview(file, scenario.scenario_id, group)
      setPreview(result.scenario)
    } catch (error) {
      notify((error as Error).message, true)
    } finally {
      setImporting(false)
    }
  }
  function cell(row: Row, key: string) {
    const value = row[key]
    if (value == null) return <span className="muted">—</span>
    if (key === 'soc' || key === 'soh')
      return (
        <span className="battery-value">
          <i style={{ width: `${Number(value) * 35}px` }} />
          {percent(Number(value))}
        </span>
      )
    if (key === 'status')
      return (
        <Badge tone={value === 'available' ? 'teal' : value === 'unavailable' ? 'red' : 'amber'}>
          {statusLabel[String(value)] || String(value)}
        </Badge>
      )
    if (key === 'available')
      return <Badge tone={value ? 'teal' : 'red'}>{value ? '可用' : '不可用'}</Badge>
    if (key === 'type' || key === 'cargo_type') return category[String(value)] || String(value)
    if (key === 'coordinates') return (value as number[]).map((v) => v.toFixed(4)).join(', ')
    return typeof value === 'number' ? number(value, 2) : String(value)
  }
  return (
    <div className="scenario-page">
      <div className="page-heading">
        <div>
          <div className="eyebrow">SCENARIO & RESOURCES</div>
          <h1>让每一份现场信息，都有据可依</h1>
          <p>管理需求、逐箱库存与机队状态，保存后生成新的可追溯版本。</p>
        </div>
        <Button variant="primary" onClick={onWorkspace}>
          前往调度工作台 <ChevronRight size={16} />
        </Button>
      </div>
      <div className="scenario-summary">
        <div>
          <Database size={20} />
          <span>
            <small>场景数据</small>
            <strong>
              {originLabel[scenario.data_origin]} <Badge>v{scenario.state_version}</Badge>
            </strong>
          </span>
        </div>
        <div>
          <MapPin size={20} />
          <span>
            <small>救援需求点</small>
            <strong>
              {scenario.sites.length}
              <em>处</em>
            </strong>
          </span>
        </div>
        <div>
          <Package size={20} />
          <span>
            <small>实际箱件库存</small>
            <strong>
              {scenario.cargo_items.length}
              <em>箱</em>
            </strong>
          </span>
        </div>
        <div>
          <Plane size={20} />
          <span>
            <small>当前可用运输机</small>
            <strong>
              {scenario.drones.filter((d) => d.status === 'available').length}
              <em>架</em>
            </strong>
          </span>
        </div>
        <button onClick={() => setSettings(true)}>
          <Settings2 size={18} />
          场景设置
        </button>
      </div>
      <div className="scenario-layout">
        <section className="panel resource-panel">
          <div className="resource-toolbar">
            <div>
              <h3>资源清单</h3>
              <p>需求与库存分别维护 · 每块电池独立追踪</p>
            </div>
            <div>
              <input
                ref={fileInput}
                type="file"
                accept=".json,.csv,.xlsx"
                hidden
                onChange={(e) => {
                  const f = e.target.files?.[0]
                  if (f) void importFile(f)
                  e.target.value = ''
                }}
              />
              <Button busy={importing} onClick={() => fileInput.current?.click()}>
                <Upload size={14} />
                导入
              </Button>
              <a
                className="button button-default"
                href={`/api/v1/scenarios/${scenario.scenario_id}/template?format=xlsx`}
              >
                <ArrowDownToLine size={14} />
                Excel模板
              </a>
              <Button
                variant="ghost"
                onClick={() => {
                  setJsonText(JSON.stringify(scenario, null, 2))
                  setJsonOpen(true)
                }}
              >
                <FileJson size={16} />
              </Button>
            </div>
          </div>
          <div className="resource-tabs">
            {groups.map((g) => (
              <button
                key={g.key}
                className={group === g.key ? 'active' : ''}
                onClick={() => {
                  setGroup(g.key)
                  setSearch('')
                }}
              >
                <g.icon size={15} />
                {g.label}
                <span>{scenario[g.key].length}</span>
              </button>
            ))}
          </div>
          <div className="table-tools">
            <div className="search-input">
              <Search size={15} />
              <input
                aria-label="搜索资源"
                placeholder={`搜索${meta.label}编号或属性…`}
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div>
              <a
                className="text-button"
                href={`/api/v1/scenarios/${scenario.scenario_id}/template?format=csv&entity=${group}`}
              >
                下载当前CSV
              </a>
              <Button onClick={() => edit(-1)}>
                <Plus size={14} />
                添加{meta.label}
              </Button>
            </div>
          </div>
          <div className="data-table-scroll">
            <table className="data-table">
              <thead>
                <tr>
                  {meta.columns.map((c) => (
                    <th key={c.key}>{c.label}</th>
                  ))}
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {visible.map(({ row, index }) => (
                  <tr key={String(row[meta.id])}>
                    {meta.columns.map((c, i) => (
                      <td key={c.key} className={i === 0 ? 'mono' : ''}>
                        {cell(row, c.key)}
                      </td>
                    ))}
                    <td>
                      <div className="row-actions">
                        <button aria-label={`编辑${row[meta.id]}`} onClick={() => edit(index)}>
                          <Edit3 size={14} />
                        </button>
                        <button
                          aria-label={`删除${row[meta.id]}`}
                          disabled={saving}
                          onClick={() => void remove(index)}
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!visible.length && <div className="table-empty">没有匹配的记录，试试其他关键词。</div>}
          </div>
          <footer className="table-footer">
            共 {rows.length} 条{meta.label}记录{' '}
            <span>修改将保存至后端 · 当前版本 v{scenario.state_version}</span>
          </footer>
        </section>
        <aside className="scenario-aside">
          <TerrainManager scenario={scenario} onAssigned={onCreated} notify={notify} />
          <ZoneManager scenario={scenario} onSave={onSave} notify={notify} />
          <section className="panel">
            <RescueMap
              scenario={scenario}
              selected={null}
              onSelect={() => {}}
              onSelectSite={(id) => {
                if (id === scenario.base.id) setSettings(true)
                else {
                  setGroup('sites')
                  setSearch(id)
                }
              }}
              compact
            />
            <div className="map-note">
              <MapPin size={14} />
              {scenario.base.name} → {scenario.sites.length} 个需求点
            </div>
          </section>
          <section className="panel readiness">
            <h3>
              <ShieldCheck size={17} />
              输入就绪情况
            </h3>
            <div>
              <CheckCircle2 size={15} />
              <span>结构与引用校验</span>
              <Badge tone="teal">已保存</Badge>
            </div>
            <div>
              <CheckCircle2 size={15} />
              <span>逐箱、机体与电池实体</span>
              <b>
                {scenario.cargo_items.length} / {scenario.drones.length} /{' '}
                {scenario.batteries.length}
              </b>
            </div>
            <div>
              <MapPin size={15} />
              <span>地形数据</span>
              <Badge tone={scenario.terrain.status === 'available' ? 'teal' : 'amber'}>
                {scenario.terrain.status === 'available'
                  ? scenario.terrain.asset_id === 'contest-dem-30m'
                    ? '题设DEM'
                    : '本地DEM'
                  : '未提供'}
              </Badge>
            </div>
            <p>输入保存不代表物理可行。载重、能耗、时限和资源约束将在真实求解后独立检查。</p>
          </section>
        </aside>
      </div>
      <Modal
        open={!!editing}
        onOpenChange={(open) => {
          if (!open) setEditing(null)
        }}
        title={`${editing?.index === -1 ? '添加' : '编辑'}${meta.label}`}
      >
        <div className="form-grid">
          {fields.map((f) => (
            <label className="field" key={f.key}>
              <span>{f.label}</span>
              {f.kind === 'select' || f.kind === 'boolean' ? (
                <select
                  value={values[f.key] ?? ''}
                  onChange={(e) => setValues({ ...values, [f.key]: e.target.value })}
                >
                  {(f.kind === 'boolean' ? ['true', 'false'] : f.options || []).map((v) => (
                    <option key={v} value={v}>
                      {f.kind === 'boolean' ? (v === 'true' ? '是' : '否') : statusLabel[v] || v}
                    </option>
                  ))}
                </select>
              ) : (
                <input
                  value={values[f.key] ?? ''}
                  type={f.kind === 'number' ? 'number' : 'text'}
                  step="any"
                  onChange={(e) => setValues({ ...values, [f.key]: e.target.value })}
                />
              )}
            </label>
          ))}
        </div>
        <div className="dialog-footer">
          <span>旧快照和已计算方案不会被覆盖</span>
          <Button onClick={() => setEditing(null)}>取消</Button>
          <Button variant="primary" busy={saving} onClick={() => void saveRow()}>
            保存修改
          </Button>
        </div>
      </Modal>
      <Modal
        open={jsonOpen}
        onOpenChange={setJsonOpen}
        title="场景JSON"
        description="可导出完整输入，或编辑后按当前版本保存。单位与字段仍受契约校验。"
        wide
      >
        <textarea
          className="json-editor"
          aria-label="完整场景JSON"
          value={jsonText}
          onChange={(e) => setJsonText(e.target.value)}
        />
        <div className="dialog-footer">
          <Button onClick={() => downloadJson(scenario, scenario.scenario_id + '.json')}>
            <ArrowDownToLine size={14} />
            导出JSON
          </Button>
          <Button
            variant="primary"
            busy={saving}
            onClick={async () => {
              setSaving(true)
              try {
                await onSave(JSON.parse(jsonText) as Scenario)
                setJsonOpen(false)
                notify('完整输入已校验并保存。')
              } catch (error) {
                notify((error as Error).message, true)
              } finally {
                setSaving(false)
              }
            }}
          >
            校验并保存
          </Button>
        </div>
      </Modal>
      <Modal
        open={!!preview}
        onOpenChange={(open) => {
          if (!open) setPreview(null)
        }}
        title="导入预览"
        description="文件已解析并通过结构/引用校验。确认后将创建独立场景，当前场景保持不变。"
      >
        {preview && (
          <>
            <div className="import-stats">
              <div>
                <strong>{preview.sites.length}</strong>需求点
              </div>
              <div>
                <strong>{preview.cargo_items.length}</strong>箱件
              </div>
              <div>
                <strong>{preview.drones.length}</strong>运输机
              </div>
              <div>
                <strong>{preview.batteries.length}</strong>电池
              </div>
            </div>
            <p className="callout">
              {preview.name} · {originLabel[preview.data_origin]}。尚未进行物理求解。
            </p>
            <div className="dialog-footer">
              <Button onClick={() => setPreview(null)}>返回</Button>
              <Button
                variant="primary"
                busy={saving}
                onClick={async () => {
                  setSaving(true)
                  try {
                    const created = await api.import(preview)
                    onCreated(created)
                    setPreview(null)
                    notify('新场景已创建。')
                  } catch (error) {
                    notify((error as Error).message, true)
                  } finally {
                    setSaving(false)
                  }
                }}
              >
                确认导入为新场景
              </Button>
            </div>
          </>
        )}
      </Modal>
      <Modal open={settings} onOpenChange={setSettings} title="场景与策略设置">
        <SettingsForm
          scenario={scenario}
          busy={saving}
          save={async (s) => {
            setSaving(true)
            try {
              await onSave(s)
              setSettings(false)
              notify('场景设置已保存。')
            } catch (error) {
              notify((error as Error).message, true)
            } finally {
              setSaving(false)
            }
          }}
        />
      </Modal>
    </div>
  )
}

function SettingsForm({
  scenario,
  save,
  busy,
}: {
  scenario: Scenario
  save: (s: Scenario) => Promise<void>
  busy: boolean
}) {
  const [draft, setDraft] = useState(() => structuredClone(scenario))
  return (
    <>
      <div className="form-grid">
        <label className="field span-2">
          <span>场景名称</span>
          <input
            value={draft.name}
            onChange={(e) => setDraft({ ...draft, name: e.target.value })}
          />
        </label>
        <label className="field">
          <span>基地经度</span>
          <input
            type="number"
            step="any"
            value={Number(draft.base.coordinates[0])}
            onChange={(e) =>
              setDraft({
                ...draft,
                base: {
                  ...draft.base,
                  coordinates: [Number(e.target.value), draft.base.coordinates[1]],
                },
              })
            }
          />
        </label>
        <label className="field">
          <span>基地纬度</span>
          <input
            type="number"
            step="any"
            value={Number(draft.base.coordinates[1])}
            onChange={(e) =>
              setDraft({
                ...draft,
                base: {
                  ...draft.base,
                  coordinates: [draft.base.coordinates[0], Number(e.target.value)],
                },
              })
            }
          />
        </label>
        <label className="field">
          <span>最低返航SOC / 比例</span>
          <input
            type="number"
            min="0"
            max="1"
            step=".01"
            value={draft.policy.min_return_soc}
            onChange={(e) =>
              setDraft({
                ...draft,
                policy: { ...draft.policy, min_return_soc: Number(e.target.value) },
              })
            }
          />
        </label>
        <label className="field">
          <span>场景模式</span>
          <select
            value={draft.mode}
            onChange={(e) => setDraft({ ...draft, mode: e.target.value as Scenario['mode'] })}
          >
            <option value="simulation">模拟演练</option>
            <option value="planning_assist">规划辅助</option>
          </select>
        </label>
        <label className="checkbox-field span-2">
          <input
            type="checkbox"
            checked={draft.policy.requires_terrain}
            onChange={(e) =>
              setDraft({
                ...draft,
                policy: { ...draft.policy, requires_terrain: e.target.checked },
              })
            }
          />
          要求通过绑定DEM净空检查
        </label>
      </div>
      <p className="callout">当前模型不含连续通信认证；费用未配置。不能把仿真结果当作实飞许可。</p>
      <div className="dialog-footer">
        <Button variant="primary" busy={busy} onClick={() => void save(draft)}>
          保存设置
        </Button>
      </div>
    </>
  )
}
