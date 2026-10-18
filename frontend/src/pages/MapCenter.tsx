import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Database,
  FileUp,
  Layers3,
  MapPinned,
  Mountain,
  Satellite,
  ScanLine,
  ShieldCheck,
} from 'lucide-react'
import { api, type Scenario } from '../api/client'
import { Badge } from '../components/ui'
import { RescueMap } from '../components/RescueMap'
import { TerrainManager } from './TerrainManager'
import { number, percent } from '../lib/format'
import { loadTownContextMetadata, townContextApplies } from '../lib/map-context'
import './map-center.css'

type Props = {
  scenario: Scenario
  onAssigned: (scenario: Scenario) => void
  notify: (message: string, error?: boolean) => void
}

export function MapCenter({ scenario, onAssigned, notify }: Props) {
  const [selectedSite, setSelectedSite] = useState(scenario.base.id)
  const terrain = scenario.terrain
  const surface = useQuery({
    queryKey: ['terrain-surface', terrain.asset_id, terrain.sha256],
    queryFn: () => api.terrainSurface(terrain.asset_id!, terrain.sha256!),
    enabled: terrain.status === 'available' && !!terrain.asset_id && !!terrain.sha256,
  })
  const nodes = [scenario.base, ...scenario.sites]
  const context = useQuery({
    queryKey: ['town-context-metadata'],
    queryFn: loadTownContextMetadata,
    staleTime: Infinity,
  })
  const contextApplies = !!context.data && townContextApplies(scenario, context.data)
  const inBounds = (coordinates: number[]) => {
    if (!surface.data) return null
    const [w, s, e, n] = surface.data.bounds
    return coordinates[0] >= w && coordinates[0] <= e && coordinates[1] >= s && coordinates[1] <= n
  }
  const covered = surface.data ? nodes.filter((n) => inBounds(n.coordinates)).length : null
  const selected = nodes.find((n) => n.id === selectedSite) || scenario.base
  return (
    <div className="map-center-page">
      <header className="map-center-intro">
        <div>
          <span className="map-center-eyebrow">
            <Layers3 size={13} />
            GEOSPATIAL WORKSPACE
          </span>
          <h2>地图与空间数据</h2>
          <p>从真实地形到任务点位。底图负责看清现场，绑定数据负责计算。</p>
        </div>
        <Badge tone={terrain.status === 'available' ? 'blue' : 'amber'}>
          {terrain.status === 'available' ? '已绑定高程数据' : '等待高程数据'}
        </Badge>
      </header>
      <div className="map-center-stats">
        <div>
          <MapPinned size={18} />
          <span>
            任务点位
            <strong>
              {nodes.length}
              <small>含调度中心</small>
            </strong>
          </span>
        </div>
        <div>
          <Mountain size={18} />
          <span>
            高程范围
            <strong>
              {surface.data
                ? `${number(surface.data.min_elevation_m)}–${number(surface.data.max_elevation_m)}`
                : '—'}
              <small>米 · 完整DEM</small>
            </strong>
          </span>
        </div>
        <div>
          <ScanLine size={18} />
          <span>
            有效栅格
            <strong>
              {surface.data ? percent(surface.data.valid_fraction) : '—'}
              <small>NoData保留未知</small>
            </strong>
          </span>
        </div>
        <div>
          <ShieldCheck size={18} />
          <span>
            点位落入DEM范围
            <strong>
              {covered == null ? '—' : `${covered}/${nodes.length}`}
              <small>范围内不等于净空通过</small>
            </strong>
          </span>
        </div>
      </div>
      {context.data && (
        <section className="map-center-context-info">
          <div>
            <Layers3 size={18} />
            <span>
              <b>{contextApplies ? '已加载本区域历史地理背景' : '当前区域无对应地理背景'}</b>
              <small>
                {contextApplies
                  ? '道路、水系、村镇与参考边界均提取自你提供的原题地图，可在图层管理中分别开关。'
                  : '点位位于镇龙乡资料范围外，已自动关闭该背景，避免把旧地区资料叠加到新场景。'}
              </small>
            </span>
          </div>
          <div className="map-center-context-counts">
            <span>
              <b>{number(context.data.counts.road)}</b>道路
            </span>
            <span>
              <b>{number(context.data.counts.water)}</b>水面
            </span>
            <span>
              <b>{number(context.data.counts.waterway)}</b>水系
            </span>
            <span>
              <b>{number(context.data.counts.place)}</b>村镇
            </span>
            <span>
              <b>{context.data.counts.boundary}</b>参考边界
            </span>
          </div>
          <p>
            ©{' '}
            <a href={context.data.attribution_url} target="_blank" rel="noreferrer">
              OpenStreetMap contributors · ODbL
            </a>
            （道路 / 水体 /
            村镇）；边界为题设资料，不作为正式行政界。背景不参与求解，不代表灾后现势。
            <a href="/maps/town-context.geojson" download>
              下载背景GeoJSON
            </a>
          </p>
        </section>
      )}
      <div className="map-center-main">
        <section className="panel map-center-map">
          <div className="map-center-panel-heading">
            <h3>
              <MapPinned size={17} />
              场景空间浏览
            </h3>
            <span>点击点位查看坐标与高程</span>
          </div>
          <RescueMap
            scenario={scenario}
            selected={null}
            onSelect={() => {}}
            onSelectSite={setSelectedSite}
          />
          <div className="map-center-selected">
            <span>
              <b>{selected.name}</b>
              <code>{selected.id}</code>
            </span>
            <span>
              {number(selected.coordinates[0], 6)}° E · {number(selected.coordinates[1], 6)}° N
            </span>
            <span>
              地面高程 <b>{number(selected.ground_elevation_m, 1)} m</b>
            </span>
          </div>
        </section>
        <aside className="map-center-assets">
          <TerrainManager scenario={scenario} onAssigned={onAssigned} notify={notify} />
          <section className="panel map-center-import">
            <h3>
              <FileUp size={17} />
              导入与绑定流程
            </h3>
            <ol>
              <li>
                <b>准备数据</b>
                <span>GeoTIFF需带坐标系、单波段高程，声明垂直基准与米制单位。</span>
              </li>
              <li>
                <b>管理DEM资产</b>
                <span>导入本地GeoTIFF，或接收队友的完整DEM资产ZIP；准备后先查看范围与有效率。</span>
              </li>
              <li>
                <b>绑定当前场景</b>
                <span>保存新版本，可提取点位高程；旧方案仍保留原快照。</span>
              </li>
              <li>
                <b>重新求解与检查</b>
                <span>算法使用完整栅格检查航段，三维显示采样不替代净空检查。</span>
              </li>
            </ol>
          </section>
        </aside>
      </div>
      {surface.isError && (
        <p role="alert" className="callout">
          绑定地形无法读取：{surface.error.message}
          。请在管理DEM资产中导入对应完整资产包；不能用其他地形替代历史hash。
        </p>
      )}
      <section className="panel map-center-data">
        <div className="map-center-panel-heading">
          <h3>
            <Database size={17} />
            数据清单与使用边界
          </h3>
          <span>版本 v{scenario.state_version} · WGS84</span>
        </div>
        <div className="map-center-categories">
          <article>
            <Satellite size={21} />
            <h4>卫星 / 航空影像</h4>
            <Badge tone="blue">显式联网</Badge>
            <p>
              地图左上角一键切换真实Esri World
              Imagery。仅作视觉参考，拍摄日期未核验；加载失败回到本地底图。
            </p>
          </article>
          <article>
            <Mountain size={21} />
            <h4>数字高程模型 DEM</h4>
            <Badge tone="teal">真实计算输入</Badge>
            <p>
              离线高程晕渲、三维地形、航段净空和通信遮挡来自同一hash绑定栅格。不是卫星影像，也不代表完整建筑障碍。
            </p>
          </article>
          <article>
            <Layers3 size={21} />
            <h4>点位 / 限制区</h4>
            <Badge>场景版本数据</Badge>
            <p>基地、需求点和限制区随场景保存。原始多边形边界用于展示，缓冲与绕行由求解器检查。</p>
          </article>
        </div>
        {surface.data && (
          <div className="map-center-identity">
            <span>
              绑定资产 <b>{surface.data.name}</b>
            </span>
            <code>{surface.data.asset_id}</code>
            <code>SHA256 {surface.data.sha256}</code>
            <span>
              覆盖 {surface.data.bounds.map((n) => number(n, 5)).join(' / ')}（西 / 南 / 东 / 北）
            </span>
          </div>
        )}
        <div className="map-center-table-wrap">
          <table>
            <thead>
              <tr>
                <th>点位</th>
                <th>类别</th>
                <th>经度 / 纬度</th>
                <th>场景地面高程</th>
                <th>DEM范围</th>
              </tr>
            </thead>
            <tbody>
              {nodes.map((n, i) => (
                <tr key={n.id} className={selected.id === n.id ? 'map-center-row-selected' : ''}>
                  <td>
                    <button onClick={() => setSelectedSite(n.id)}>
                      {n.name}
                      <small>{n.id}</small>
                    </button>
                  </td>
                  <td>{i === 0 ? '调度中心' : '需求点'}</td>
                  <td>
                    {number(n.coordinates[0], 6)} / {number(n.coordinates[1], 6)}
                  </td>
                  <td>{number(n.ground_elevation_m, 1)} m</td>
                  <td>
                    {inBounds(n.coordinates) == null
                      ? '未读取'
                      : inBounds(n.coordinates)
                        ? '覆盖范围内'
                        : '覆盖范围外'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <p className="map-center-note">
        你提供的《镇龙乡地理空间详情地图》属于DEM着色加OSM道路、水体与村镇的矢量地图，并非卫星图。本系统不会将HTML或普通图片当作高程文件导入。已按原坐标提取道路、水体、村镇与参考边界，保留原OSM编号；新地区的道路与边界需另行提供，不会由DEM推断生成。
      </p>
    </div>
  )
}
