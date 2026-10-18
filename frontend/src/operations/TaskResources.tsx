import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  ArrowLeft,
  ArrowRight,
  Archive,
  BatteryCharging,
  Boxes,
  ChevronRight,
  Drone,
  Layers3,
  MapPinned,
  Mountain,
  Search,
  ShieldCheck,
} from 'lucide-react'
import { api } from '../api/client'
import { ops, type Mission } from '../api/operations'
import { Empty } from '../components/ui'
import { TerrainManager } from '../pages/TerrainManager'
import { ArchiveCenter } from './ArchiveCenter'
import { number, percent, category } from '../lib/format'
import { stageLabel } from './App'
import { InfoHint } from './ExperienceUI'

const tabs = [
  { id: 'maps', title: '地图资产', icon: Mountain },
  { id: 'fleet', title: '机队与电池', icon: Drone },
  { id: 'cargo', title: '需求与物资', icon: Boxes },
  { id: 'archives', title: '运行与档案', icon: Archive },
]
export function TaskResources({
  path,
  notify,
}: {
  path: string
  notify: (s: string, e?: boolean) => void
}) {
  const query = useQueryClient(),
    [search, setSearch] = useState('')
  const [, id, requested = 'maps'] = path.split('/'),
    tab = tabs.some((t) => t.id === requested) ? requested : 'maps'
  const missions = useQuery({ queryKey: ['missions'], queryFn: ops.missions })
  const mission = useQuery({
    queryKey: ['mission', id],
    queryFn: () => ops.mission(id),
    enabled: !!id,
  })
  const m = mission.data,
    sid = m?.current_scenario_id
  const scenario = useQuery({
    queryKey: ['scenario', sid],
    queryFn: () => api.scenario(sid!),
    enabled: !!sid,
  })
  const executions = useQuery({
    queryKey: ['mission-executions', id],
    queryFn: () => ops.executions(id),
    enabled: !!id && tab === 'archives',
  })
  const assets = useQuery({
    queryKey: ['terrain-assets'],
    queryFn: api.terrainAssets,
    enabled: !!id && tab === 'maps',
  })
  const s = scenario.data || m?.draft
  const assigned = assets.data?.find(
    (a) => a.asset_id === s?.terrain.asset_id && a.sha256 === s.terrain.sha256,
  )
  if (!id)
    return (
      <main className="v2-content v3-resource-index">
        <div className="v2-page-heading">
          <div>
            <span className="v3-kicker">
              <Layers3 size={15} />
              任务资源空间
            </span>
            <h1>资源中心</h1>
            <p>先选择救援任务，再管理该任务的地图、机队、能源与物资。</p>
          </div>
          <a className="button" href="#/missions">
            管理救援任务
            <ArrowRight size={14} />
          </a>
        </div>
        <div className="v3-resource-intro">
          <ShieldCheck size={21} />
          <div>
            <b>相同规格，不代表同一架设备</b>
            <p>
              任务之间的输入与执行记录独立保存。修改当前资源会生成新输入版本，历史方案仍保留原有依据。
            </p>
          </div>
          <label className="v2-search">
            <Search size={15} />
            <input
              placeholder="搜索任务名称"
              aria-label="搜索资源所属任务"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </label>
        </div>
        {missions.error ? (
          <p className="v2-inline-error">{missions.error.message}</p>
        ) : missions.isPending ? (
          <p className="v2-loading">读取任务资源…</p>
        ) : (
          <div className="v3-resource-missions">
            {missions.data
              ?.filter((m) => m.name.toLowerCase().includes(search.toLowerCase()))
              .map((m) => (
                <MissionResourceCard key={m.mission_id} mission={m} />
              ))}
          </div>
        )}
        {missions.data?.length === 0 && (
          <Empty
            icon={<Layers3 size={30} />}
            title="还没有任务资源"
            description="先创建救援任务，即可进入它的资源空间。"
            action={
              <a className="button button-primary" href="#/missions">
                创建任务
              </a>
            }
          />
        )}
        <details className="v3-imported-archives">
          <summary>
            <Archive size={17} />
            导入与浏览外部运行档案
            <ChevronRight size={14} />
          </summary>
          <p>
            外部档案按其原任务名称保留，只读导入不会并入当前任务的物资或交付。任务内部的运行记录仍在各任务资源空间。
          </p>
          <ArchiveCenter notify={notify} />
        </details>
      </main>
    )
  return (
    <main className="v2-content v3-task-resources">
      <div className="v3-resource-breadcrumb">
        <a href="#/resources">
          <ArrowLeft size={14} />
          所有任务
        </a>
        <ChevronRight size={14} />
        <span>{m?.name || '读取中…'}</span>
      </div>
      <div className="v2-page-heading">
        <div>
          <h1>{m?.name || '任务资源'}</h1>
          <p>
            当前输入资源 · {scenario.data ? `第 ${scenario.data.state_version} 版` : '未发布草稿'} ·
            执行中的实际变化请到执行跟踪核对
          </p>
        </div>
        <div className="v3-resource-actions">
          <select
            aria-label="切换资源所属任务"
            value={id}
            onChange={(e) => (location.hash = `/resources/${e.target.value}/${tab}`)}
          >
            {missions.data?.map((m) => (
              <option key={m.mission_id} value={m.mission_id}>
                {m.name}
              </option>
            ))}
          </select>
          <a
            className="button button-primary"
            href={`#/missions/${id}/prepare?tab=${tab === 'maps' ? 'region' : tab === 'cargo' ? 'demand' : 'fleet'}`}
          >
            编辑任务资源
            <ArrowRight size={14} />
          </a>
        </div>
      </div>
      <nav className="v3-resource-tabs" aria-label="任务资源类型">
        {tabs.map((t) => (
          <a key={t.id} href={`#/resources/${id}/${t.id}`} className={tab === t.id ? 'active' : ''}>
            <t.icon size={17} />
            {t.title}
          </a>
        ))}
      </nav>
      {mission.error || scenario.error ? (
        <p className="v2-inline-error">{mission.error?.message || scenario.error?.message}</p>
      ) : !m || !s ? (
        <p className="v2-loading">读取本任务资源…</p>
      ) : tab === 'maps' ? (
        <>
          <div className="v3-resource-map-overview">
            <div className="v3-resource-map-icon">
              <Mountain size={64} />
              <span>地图与地形</span>
            </div>
            <div>
              <span className="v3-kicker">
                <MapPinned size={14} />
                当前任务绑定资产
              </span>
              <h2>{assigned?.name || s.terrain.asset_id || '尚未绑定地形'}</h2>
              <p>
                地形状态：{s.terrain.status === 'available' ? '已绑定，计算时检查覆盖' : '待补齐'} ·
                坐标：WGS84 经度 / 纬度
              </p>
              <dl>
                <div>
                  <dt>
                    高程参考
                    <InfoHint title="高程参考">
                      说明高程数值相对哪个海平面或参考面。导入地形与站点高程必须一致，单位为米。
                    </InfoHint>
                  </dt>
                  <dd>{s.terrain.vertical_datum || '未声明'}</dd>
                </div>
                <div>
                  <dt>任务位置</dt>
                  <dd>1 个基地 · {s.sites.length} 个需求点</dd>
                </div>
                <div>
                  <dt>限制区域</dt>
                  <dd>{s.restricted_zones?.length || 0} 个</dd>
                </div>
              </dl>
              {scenario.data && (
                <TerrainManager
                  scenario={scenario.data}
                  onAssigned={() => {
                    void query.invalidateQueries({ queryKey: ['scenario', sid] })
                    void query.invalidateQueries({ queryKey: ['mission', id] })
                  }}
                  notify={notify}
                />
              )}
            </div>
          </div>
          <section className="v2-card">
            <div className="v2-section-bar">
              <h3>本任务的点位与高程</h3>
              <a href={`#/missions/${id}/prepare?tab=region`}>
                在地图定位
                <ArrowRight size={13} />
              </a>
            </div>
            <div className="v2-table-scroll">
              <table className="v2-table">
                <thead>
                  <tr>
                    <th>点位角色</th>
                    <th>名称 / 编号</th>
                    <th>经度</th>
                    <th>纬度</th>
                    <th>地面高程</th>
                    <th>可用状态</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    ...(s.base ? [{ ...s.base, role: '调度中心' }] : []),
                    ...s.sites.map((v) => ({ ...v, role: '救援需求点' })),
                  ].map((v) => (
                    <tr key={v.id}>
                      <td>{v.role}</td>
                      <td>
                        <b>{v.name}</b>
                        <small>{v.id}</small>
                      </td>
                      <td>{number(v.coordinates[0], 6)}</td>
                      <td>{number(v.coordinates[1], 6)}</td>
                      <td>
                        {v.ground_elevation_m == null
                          ? '未填写'
                          : `${number(v.ground_elevation_m, 1)} m`}
                      </td>
                      <td>{v.available ? '可用' : '不可用'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      ) : tab === 'fleet' ? (
        <>
          <div className="v3-fleet-type-cards">
            {s.drone_types.map((t) => (
              <article key={t.type_id}>
                <Drone size={25} />
                <h3>{t.type_id} 型运输无人机</h3>
                <span>{s.drones.filter((d) => d.type_id === t.type_id).length} 架机体</span>
                <dl>
                  <div>
                    <dt>最大载荷</dt>
                    <dd>{number(t.max_payload_kg)} kg</dd>
                  </div>
                  <div>
                    <dt>货舱体积</dt>
                    <dd>{number(t.max_volume_l)} L</dd>
                  </div>
                  <div>
                    <dt>巡航速度</dt>
                    <dd>{number(t.cruise_speed_mps, 1)} m/s</dd>
                  </div>
                </dl>
              </article>
            ))}
          </div>
          <div className="v3-resource-two">
            <section className="v2-card">
              <div className="v2-section-bar">
                <h3>
                  <Drone size={16} />
                  机体清单
                </h3>
                <span>{s.drones.length} 架</span>
              </div>
              <div className="v2-table-scroll">
                <table className="v2-table">
                  <thead>
                    <tr>
                      <th>机体</th>
                      <th>机型</th>
                      <th>输入状态</th>
                      <th>可用时刻</th>
                    </tr>
                  </thead>
                  <tbody>
                    {s.drones.map((d) => (
                      <tr key={d.drone_id}>
                        <td>
                          <b>{d.drone_id}</b>
                        </td>
                        <td>{d.type_id}</td>
                        <td>{resourceState(d.status)}</td>
                        <td>{number(d.available_after_s)} 秒</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
            <section className="v2-card">
              <div className="v2-section-bar">
                <h3>
                  <BatteryCharging size={16} />
                  运输电池
                </h3>
                <span>{s.batteries.length} 块</span>
              </div>
              <div className="v2-table-scroll">
                <table className="v2-table">
                  <thead>
                    <tr>
                      <th>电池</th>
                      <th>容量</th>
                      <th>初始电量</th>
                      <th>健康度</th>
                      <th>状态</th>
                    </tr>
                  </thead>
                  <tbody>
                    {s.batteries.map((b) => (
                      <tr key={b.battery_id}>
                        <td>
                          <b>{b.battery_id}</b>
                        </td>
                        <td>{number(b.capacity_kwh, 2)} kWh</td>
                        <td>
                          <span className="v3-battery-inline">
                            <i style={{ width: `${b.soc * 100}%` }} />
                            {percent(b.soc)}
                          </span>
                        </td>
                        <td>{percent(b.soh)}</td>
                        <td>{resourceState(b.status)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </div>
          {s.communication && (
            <div className="v3-resource-intro">
              <RadioResources scenario={s} />
            </div>
          )}
        </>
      ) : tab === 'cargo' ? (
        <>
          <div className="v3-cargo-summary">
            {[...new Set(s.cargo_items.map((c) => c.type))].map((type) => {
              const rows = s.cargo_items.filter((c) => c.type === type)
              return (
                <article key={type}>
                  <Boxes size={24} />
                  <div>
                    <span>{category[type] || type}</span>
                    <strong>
                      {rows.length}
                      <small>箱</small>
                    </strong>
                    <p>
                      {number(
                        rows.reduce((n, c) => n + c.mass_kg, 0),
                        1,
                      )}{' '}
                      kg · {number(rows.reduce((n, c) => n + c.volume_l, 0))} L
                    </p>
                  </div>
                </article>
              )
            })}
          </div>
          <section className="v2-card">
            <div className="v2-section-bar">
              <h3>逐箱实物库存</h3>
              <span className="v2-subtle">输入版本记录 · 交付实况请查看执行跟踪</span>
            </div>
            <div className="v2-table-scroll">
              <table className="v2-table">
                <thead>
                  <tr>
                    <th>箱件</th>
                    <th>物资类型</th>
                    <th>质量</th>
                    <th>体积</th>
                    <th>需求归属</th>
                    <th>输入状态</th>
                  </tr>
                </thead>
                <tbody>
                  {s.cargo_items.map((c) => (
                    <tr key={c.cargo_id}>
                      <td>
                        <b>{c.cargo_id}</b>
                      </td>
                      <td>{category[c.type] || c.type}</td>
                      <td>{number(c.mass_kg, 1)} kg</td>
                      <td>{number(c.volume_l)} L</td>
                      <td>{c.demand_id}</td>
                      <td>{resourceState(c.status)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      ) : (
        <>
          <section className="v2-card">
            <div className="v2-section-bar">
              <h3>本任务的模拟执行记录</h3>
              <a href={`#/missions/${id}/review`}>
                进入复盘
                <ArrowRight size={14} />
              </a>
            </div>
            {executions.isPending ? (
              <p className="v2-loading">读取运行记录…</p>
            ) : executions.error ? (
              <p className="v2-inline-error">{executions.error.message}</p>
            ) : !executions.data?.length ? (
              <p className="v2-help-note">尚未创建模拟实例。确认方案后进入执行跟踪。</p>
            ) : (
              <table className="v2-table">
                <thead>
                  <tr>
                    <th>运行状态</th>
                    <th>模拟进度</th>
                    <th>交付结果</th>
                    <th>记录</th>
                  </tr>
                </thead>
                <tbody>
                  {executions.data.map((e) => (
                    <tr key={e.execution_id}>
                      <td>
                        {
                          { ready: '待开始', running: '运行中', paused: '暂停', completed: '结束' }[
                            e.status
                          ]
                        }
                      </td>
                      <td>{number(e.time_s / 60, 1)} 分钟</td>
                      <td>{e.delivered_cargo_ids.length} 箱已交付</td>
                      <td>
                        <a
                          className="button"
                          href={`/api/v1/executions/${e.execution_id}/export?version=2`}
                          download
                        >
                          导出完整运行档案
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>
          <ArchiveCenter
            executionIds={executions.data?.map((e) => e.execution_id) || []}
            notify={notify}
          />
        </>
      )}
    </main>
  )
}
function MissionResourceCard({ mission: m }: { mission: Mission }) {
  return (
    <a className="v3-mission-resource-card" href={`#/resources/${m.mission_id}/maps`}>
      <div>
        <span>
          <Drone size={22} />
        </span>
        <small>{stageLabel[m.lifecycle]}</small>
        <ChevronRight size={18} />
      </div>
      <h2>{m.name}</h2>
      <p>
        {m.site_count} 个需求点 · {m.cargo_count} 箱物资
      </p>
      <div className="v3-resource-card-counts">
        <span>
          <Mountain size={14} />
          地图资产
        </span>
        <span>
          <Drone size={14} />
          {m.draft.drones.length} 架机体
        </span>
        <span>
          <BatteryCharging size={14} />
          {m.draft.batteries.length} 块电池
        </span>
      </div>
      <footer>
        <span>最近更新 {new Date(m.updated_at).toLocaleDateString('zh-CN')}</span>
        <b>
          进入资源空间
          <ArrowRight size={13} />
        </b>
      </footer>
    </a>
  )
}
function resourceState(s: string) {
  return (
    (
      {
        available: '可用',
        reserved: '已预约',
        unavailable: '不可用',
        charging: '充电中',
        delivered: '已交付',
        loaded: '已装载',
          in_transit:'运输途中',
        in_stock: '在库',
      } as Record<string, string>
    )[s] || s
  )
}
function RadioResources({ scenario: s }: { scenario: Mission['draft'] }) {
  return (
    <>
      <Layers3 size={23} />
      <div>
        <b>本任务还配置了独立的中继保障资源</b>
        <p>
          {s.communication?.relay_drones.length || 0} 架中继机体 ·{' '}
          {s.communication?.relay_energy.length || 0} 套中继能源组件。与运输电池分开排程和核算。
        </p>
      </div>
    </>
  )
}
