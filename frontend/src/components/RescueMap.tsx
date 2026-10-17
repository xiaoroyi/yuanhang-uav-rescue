import { useCallback, useEffect, useRef, useState } from 'react'
import * as maplibregl from 'maplibre-gl'
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?url'
import 'maplibre-gl/dist/maplibre-gl.css'
import { Crosshair, Layers, MapPinned, Minus, Plus } from 'lucide-react'
import type { FeatureCollection, LineString } from 'geojson'
import type { Plan, Scenario, Playback } from '../api/client'
import { colorFor } from '../lib/format'

maplibregl.setWorkerUrl(workerUrl)

type Props = {
  scenario: Scenario
  plan?: Plan | null
  oldPlan?: Plan | null
  selected: string | null
  onSelect: (id: string) => void
  onSelectSite?: (id: string) => void
  compact?: boolean
  playTime?: number | null
  playback?: Playback
}
export function RescueMap({
  scenario,
  plan,
  oldPlan,
  selected,
  onSelect,
  onSelectSite,
  compact = false,
  playTime,
  playback,
}: Props) {
  const container = useRef<HTMLDivElement>(null),
    map = useRef<maplibregl.Map | null>(null),
    markers = useRef<maplibregl.Marker[]>([])
  const aircraft = useRef<maplibregl.Marker[]>([])
  const latest = useRef({ scenario, plan, selected, onSelect, onSelectSite })
  latest.current = { scenario, plan, selected, onSelect, onSelectSite }
  const [ready, setReady] = useState(false),
    [showRoutes, setShowRoutes] = useState(true),
    [showOld, setShowOld] = useState(true),
    [layersOpen, setLayersOpen] = useState(false),
    [error, setError] = useState(false),
    [terrainShown, setTerrainShown] = useState(false)
  const [showTerrain, setShowTerrain] = useState(true)
  const fit = useCallback(() => {
    const scenario = latest.current.scenario
    const bounds = new maplibregl.LngLatBounds()
    for (const n of [scenario.base, ...scenario.sites])
      bounds.extend(n.coordinates as [number, number])
    map.current?.fitBounds(bounds, {
      padding: { top: 70, bottom: 55, left: 55, right: 110 },
      maxZoom: 13,
      duration: 500,
    })
  }, [])
  useEffect(() => {
    if (!container.current) return
    let m: maplibregl.Map
    try {
      m = new maplibregl.Map({
        container: container.current,
        center: latest.current.scenario.base.coordinates as [number, number],
        zoom: 11,
        attributionControl: false,
        style: {
          version: 8,
          sources: {},
          layers: [{ id: 'ground', type: 'background', paint: { 'background-color': '#e8efeb' } }],
        },
      })
    } catch {
      setError(true)
      return
    }
    map.current = m
    m.addControl(new maplibregl.ScaleControl({ maxWidth: 90, unit: 'metric' }), 'bottom-left')
    m.on('load', () => {
      m.addSource('grid', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } })
      m.addLayer({
        id: 'grid',
        type: 'line',
        source: 'grid',
        paint: { 'line-color': '#a5bdb2', 'line-width': 0.7, 'line-opacity': 0.35 },
      })
      m.addSource('old-routes', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] },
      })
      m.addLayer({
        id: 'old-routes',
        type: 'line',
        source: 'old-routes',
        paint: {
          'line-color': '#b18a75',
          'line-width': 2,
          'line-dasharray': [3, 3],
          'line-opacity': 0.5,
        },
      })
      m.addSource('routes', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } })
      m.addLayer({
        id: 'routes-halo',
        type: 'line',
        source: 'routes',
        paint: { 'line-color': '#ffffff', 'line-width': 7, 'line-opacity': 0.55 },
      })
      m.addLayer({
        id: 'routes',
        type: 'line',
        source: 'routes',
        paint: {
          'line-color': ['get', 'color'],
          'line-width': ['case', ['get', 'selected'], 4, 2.5],
          'line-opacity': ['case', ['get', 'dim'], 0.2, 0.85],
        },
      })
      void fetch('/api/v1/map/terrain')
        .then((r) => {
          if (!r.ok) throw new Error('no terrain')
          return r.json()
        })
        .then((asset: { coordinates: [number, number][]; image_url: string }) => {
          if (!map.current || map.current !== m) return
          m.addSource('terrain-preview', {
            type: 'image',
            url: asset.image_url,
            coordinates: asset.coordinates as [
              [number, number],
              [number, number],
              [number, number],
              [number, number],
            ],
          })
          m.addLayer(
            {
              id: 'terrain-preview',
              type: 'raster',
              source: 'terrain-preview',
              paint: { 'raster-opacity': 0.66, 'raster-saturation': -0.3 },
            },
            'grid',
          )
          setTerrainShown(true)
        })
        .catch(() => {
          /* A coordinate grid remains available when this optional local asset is absent. */
        })
      m.on('click', 'routes', (e) => {
        const id = e.features?.[0]?.properties?.id
        if (id) latest.current.onSelect(id)
      })
      m.on('mouseenter', 'routes', () => {
        m.getCanvas().style.cursor = 'pointer'
      })
      m.on('mouseleave', 'routes', () => {
        m.getCanvas().style.cursor = ''
      })
      setReady(true)
    })
    const observer = new ResizeObserver(() => m.resize())
    observer.observe(container.current)
    return () => {
      observer.disconnect()
      markers.current.forEach((x) => x.remove())
      aircraft.current.forEach((x) => x.remove())
      m.remove()
      map.current = null
    }
  }, [])
  useEffect(() => {
    const m = map.current
    if (!m || !ready) return
    markers.current.forEach((x) => x.remove())
    markers.current = []
    const bounds = new maplibregl.LngLatBounds()
    for (const [i, n] of [scenario.base, ...scenario.sites].entries()) {
      bounds.extend(n.coordinates as [number, number])
      const button = document.createElement('button')
      button.className = `map-marker ${i === 0 ? 'map-marker-base' : ''} ${!n.available ? 'unavailable' : ''}`
      const dot = document.createElement('span')
      dot.className = 'map-marker-dot'
      dot.textContent = i === 0 ? 'O' : String(i)
      const label = document.createElement('span')
      label.className = 'map-marker-label'
      label.textContent = i === 0 ? '临时调度中心' : n.name
      button.append(dot, label)
      button.title = `${n.id} · ${n.coordinates.join(', ')}`
      button.setAttribute('aria-label', `定位${n.name}`)
      button.onclick = () => {
        latest.current.onSelectSite?.(n.id)
        const route = latest.current.plan?.sorties.find((r) =>
          r.visits.some((v) => v.site_id === n.id),
        )
        if (route) latest.current.onSelect(route.sortie_id)
        m.easeTo({ center: n.coordinates as [number, number], duration: 400 })
      }
      markers.current.push(
        new maplibregl.Marker({ element: button, anchor: 'center' })
          .setLngLat(n.coordinates as [number, number])
          .addTo(m),
      )
    }
    const west = bounds.getWest(),
      east = bounds.getEast(),
      south = bounds.getSouth(),
      north = bounds.getNorth()
    const step = Math.max(0.005, (east - west) / 5),
      margin = Math.max(0.03, east - west)
    const grid: FeatureCollection<LineString> = { type: 'FeatureCollection', features: [] }
    for (let x = Math.floor((west - margin) / step) * step; x < east + margin; x += step)
      grid.features.push({
        type: 'Feature',
        properties: {},
        geometry: {
          type: 'LineString',
          coordinates: [
            [x, south - margin],
            [x, north + margin],
          ],
        },
      })
    for (let y = Math.floor((south - margin) / step) * step; y < north + margin; y += step)
      grid.features.push({
        type: 'Feature',
        properties: {},
        geometry: {
          type: 'LineString',
          coordinates: [
            [west - margin, y],
            [east + margin, y],
          ],
        },
      })
    ;(m.getSource('grid') as maplibregl.GeoJSONSource).setData(grid)
    fit()
  }, [ready, scenario, fit])
  useEffect(() => {
    const m = map.current
    if (!m || !ready) return
    const collection = (p: Plan | null | undefined): FeatureCollection<LineString> => ({
      type: 'FeatureCollection',
      features: (p?.sorties || []).map((r) => ({
        type: 'Feature',
        properties: {
          id: r.sortie_id,
          color: colorFor(r.drone_id),
          selected: selected === r.sortie_id,
          dim: !!selected && selected !== r.sortie_id,
        },
        geometry: r.route_geometry as LineString,
      })),
    })
    ;(m.getSource('routes') as maplibregl.GeoJSONSource).setData(collection(plan))
    ;(m.getSource('old-routes') as maplibregl.GeoJSONSource).setData(collection(oldPlan))
    m.setLayoutProperty('routes', 'visibility', showRoutes ? 'visible' : 'none')
    m.setLayoutProperty('routes-halo', 'visibility', showRoutes ? 'visible' : 'none')
    m.setLayoutProperty('old-routes', 'visibility', showOld ? 'visible' : 'none')
  }, [ready, plan, oldPlan, selected, showRoutes, showOld])
  useEffect(() => {
    const m = map.current
    if (!m || !ready || !terrainShown) return
    m.setLayoutProperty('terrain-preview', 'visibility', showTerrain ? 'visible' : 'none')
  }, [ready, terrainShown, showTerrain])
  useEffect(() => {
    const m = map.current
    if (!m || !ready) return
    aircraft.current.forEach((x) => x.remove())
    aircraft.current = []
    if (playTime == null || !playback) return
    for (const phase of playback.phases.filter(
      (p) => p.start_s <= playTime && playTime < p.end_s,
    )) {
      const t = (playTime - phase.start_s) / (phase.end_s - phase.start_s)
      const coordinates: [number, number] = [
        phase.from_coordinates[0] + t * (phase.to_coordinates[0] - phase.from_coordinates[0]),
        phase.from_coordinates[1] + t * (phase.to_coordinates[1] - phase.from_coordinates[1]),
      ]
      const button = document.createElement('button')
      button.className = 'planned-aircraft'
      button.style.setProperty('--aircraft-color', colorFor(phase.drone_id))
      const label = { prepare: '准备', flight: '运输', handover: '交接', return: '返航' }[
        phase.phase
      ]
      button.textContent = '✈'
      button.title = `${phase.drone_id} · ${label} · 计划位置示意`
      button.setAttribute('aria-label', `${phase.drone_id}计划位置`)
      button.onclick = () => latest.current.onSelect(phase.sortie_id)
      const tag = document.createElement('span')
      tag.textContent = `${phase.drone_id} ${label}`
      button.append(tag)
      aircraft.current.push(
        new maplibregl.Marker({ element: button, anchor: 'center' })
          .setLngLat(coordinates)
          .addTo(m),
      )
    }
  }, [ready, playTime, playback])
  return (
    <div className={`rescue-map ${compact ? 'map-compact' : ''}`}>
      <div ref={container} className="map-canvas" />
      {error && (
        <div className="map-error">地图渲染不可用，点位与路线仍可在任务表和导出中查看。</div>
      )}
      <div className="map-header">
        <span>
          <MapPinned size={14} /> 场景地图 <i /> <b>WGS84</b>
        </span>
        <span className="map-mode">
          {terrainShown && showTerrain ? '题设DEM · 离线' : '本地坐标底图'}
        </span>
      </div>
      <div className="map-controls">
        <button aria-label="放大地图" onClick={() => map.current?.zoomIn()}>
          <Plus size={17} />
        </button>
        <button aria-label="缩小地图" onClick={() => map.current?.zoomOut()}>
          <Minus size={17} />
        </button>
        <button aria-label="适配全部点位" onClick={fit}>
          <Crosshair size={17} />
        </button>
        <button
          aria-label="图层管理"
          className={layersOpen ? 'active' : ''}
          onClick={() => setLayersOpen(!layersOpen)}
        >
          <Layers size={17} />
        </button>
      </div>
      {layersOpen && (
        <div className="map-layers">
          {terrainShown && (
            <label>
              <input
                type="checkbox"
                checked={showTerrain}
                onChange={(e) => setShowTerrain(e.target.checked)}
              />
              题设DEM地形
            </label>
          )}
          <label>
            <input
              type="checkbox"
              checked={showRoutes}
              onChange={(e) => setShowRoutes(e.target.checked)}
            />
            当前方案航线
          </label>
          {oldPlan && (
            <label>
              <input
                type="checkbox"
                checked={showOld}
                onChange={(e) => setShowOld(e.target.checked)}
              />
              事件前方案
            </label>
          )}
          <p>点位与航线均来自当前输入/计算。通信图层尚未接入。</p>
        </div>
      )}
      <div className="map-north">
        N<span>↑</span>
      </div>
      <div className="map-legend">
        <span>
          <i className="legend-base" />
          调度中心
        </span>
        <span>
          <i className="legend-site" />
          需求点
        </span>
        <span>
          <i className="legend-route" />
          运输航线
        </span>
      </div>
      <div className="map-attribution">
        {playTime != null
          ? '计划位置为匀速插值示意 · 非实时遥测'
          : '离线可用 · 图上路线为任务级建议'}
      </div>
    </div>
  )
}
