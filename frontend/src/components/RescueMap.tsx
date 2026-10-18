import { useCallback, useContext, useEffect, useRef, useState } from 'react'
import * as maplibregl from 'maplibre-gl'
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?url'
import 'maplibre-gl/dist/maplibre-gl.css'
import { Crosshair, Layers, MapPinned, Minus, Plus, Mountain, Satellite } from 'lucide-react'
import type { FeatureCollection, LineString, Polygon } from 'geojson'
import type { Plan, Scenario, Playback, TerrainMap } from '../api/client'
import type { Telemetry } from '../api/operations'
import { colorFor } from '../lib/format'
import {
  loadTownContextMetadata,
  loadTownContextData,
  townContextApplies,
  type TownContextMetadata,
  type TownContextData,
} from '../lib/map-context'
import './rescue-map.css'
import { UIContext } from './UIContext'

maplibregl.setWorkerUrl(workerUrl)

type MapScene = Pick<Scenario, 'sites' | 'terrain' | 'restricted_zones' | 'weather'> & {
  base: Scenario['base'] | null
  scenario_id?: string
}
const mapNodes = (scene: MapScene) => (scene.base ? [scene.base, ...scene.sites] : scene.sites)
type RouteChoice = { id: string; drone: string; cargo: number; stops: string }
type Props = {
  scenario: MapScene
  viewKey?: string
  plan?: Plan | null
  oldPlan?: Plan | null
  selected: string | null
  onSelect: (id: string) => void
  onSelectSite?: (id: string) => void
  onSelectDevice?: (id: string) => void
  compact?: boolean
  playTime?: number | null
  playback?: Playback
  telemetry?: Telemetry[]
  selectedSite?: string | null
  onPickCoordinates?: (coordinates: [number, number]) => void
  routeSets?: { plan: Plan; sortieIds: string[] }[]
}
export function RescueMap({
  scenario,
  viewKey,
  plan,
  oldPlan,
  selected,
  onSelect,
  onSelectSite,
  onSelectDevice,
  compact = false,
  playTime,
  playback,
  telemetry,
  selectedSite,
  onPickCoordinates,
  routeSets,
}: Props) {
  const uiContext = useContext(UIContext)
  const preserveCamera = uiContext === 'v2' || !!viewKey
  const container = useRef<HTMLDivElement>(null),
    map = useRef<maplibregl.Map | null>(null),
    markers = useRef<maplibregl.Marker[]>([])
  const aircraft = useRef<maplibregl.Marker[]>([])
  const relayMarkers = useRef<maplibregl.Marker[]>([])
  const placeLabels = useRef<maplibregl.Marker[]>([])
  const updateSiteLayout = useRef<(() => void) | null>(null)
  const cameraOwner = useRef<string | null>(null)
  const cameraRegion = useRef<string | null>(null)
  const [routeChoices, setRouteChoices] = useState<RouteChoice[]>([])
  const [siteChoices, setSiteChoices] = useState<Scenario['sites']>([])
  const [deviceChoices, setDeviceChoices] = useState<Telemetry[]>([])
  const latest = useRef({
    scenario,
    plan,
    selected,
    selectedSite,
    onSelect,
    onSelectSite,
    onSelectDevice,
    onPickCoordinates,
    viewKey: viewKey || scenario.scenario_id || 'draft',
    preserveCamera,
  })
  latest.current = {
    scenario,
    plan,
    selected,
    selectedSite,
    onSelect,
    onSelectSite,
    onSelectDevice,
    onPickCoordinates,
    viewKey: viewKey || scenario.scenario_id || 'draft',
    preserveCamera,
  }
  const [ready, setReady] = useState(false),
    [showRoutes, setShowRoutes] = useState(true),
    [showOld, setShowOld] = useState(true),
    [layersOpen, setLayersOpen] = useState(false),
    [error, setError] = useState(false),
    [terrainShown, setTerrainShown] = useState(false)
  const [showTerrain, setShowTerrain] = useState(true)
  const [terrainLabel, setTerrainLabel] = useState('')
  const [showZones, setShowZones] = useState(true)
  const [showRelays, setShowRelays] = useState(true)
  const [showWeather, setShowWeather] = useState(true)
  const [townMetadata, setTownMetadata] = useState<TownContextMetadata | null>(null)
  const [townData, setTownData] = useState<TownContextData | null>(null)
  const [contextLoaded, setContextLoaded] = useState(false)
  const [showContext, setShowContext] = useState(true)
  const [showPlaceNames, setShowPlaceNames] = useState(false)
  const [showBoundary, setShowBoundary] = useState(true)
  const contextApplies = !!townMetadata && townContextApplies(scenario, townMetadata)
  const contextVisible = contextLoaded && (showContext || showPlaceNames || showBoundary)
  useEffect(() => {
    let canceled = false
    void loadTownContextMetadata()
      .then((value) => {
        if (!canceled) setTownMetadata(value)
      })
      .catch(() => {})
    return () => {
      canceled = true
    }
  }, [])
  const [basemap, setBasemap] = useState<'offline' | 'satellite'>('offline')
  const [satelliteState, setSatelliteState] = useState<'idle' | 'loading' | 'ready' | 'failed'>(
    'idle',
  )
  const basemapRef = useRef(basemap)
  basemapRef.current = basemap
  const fit = useCallback((duration = 500) => {
    const scenario = latest.current.scenario
    const bounds = new maplibregl.LngLatBounds()
    for (const n of mapNodes(scenario)) bounds.extend(n.coordinates as [number, number])
    for (const r of latest.current.plan?.relay_sorties || [])
      bounds.extend(r.station_coordinates as [number, number])
    if (bounds.isEmpty()) {
      map.current?.jumpTo({ center: [0, 20], zoom: 1.5 })
      return
    }
    const width = map.current?.getContainer().clientWidth || 1000
    map.current?.fitBounds(bounds, {
      // Keep the lowest site markers above the bottom legend and scale controls.
      padding: {
        top: 115,
        bottom: basemapRef.current === 'satellite' ? 155 : 120,
        left: width < 600 ? 38 : 55,
        right: width < 600 ? 65 : 140,
      },
      maxZoom: 13,
      duration,
    })
  }, [])
  const restoreView = useCallback(() => {
    const m = map.current
    const owner = latest.current.viewKey
    const scene = latest.current.scenario
    const region = JSON.stringify({
      base: scene.base?.coordinates || null,
      hasSites: scene.sites.length > 0,
    })
    if (!m || (cameraOwner.current === owner && cameraRegion.current === region)) return
    setRouteChoices([])
    setSiteChoices([])
    setDeviceChoices([])
    cameraOwner.current = owner
    cameraRegion.current = region
    if (!latest.current.preserveCamera) {
      fit(0)
      return
    }
    try {
      const saved: unknown = JSON.parse(
        sessionStorage.getItem('yuanhang-map-camera:' + owner) || 'null',
      )
      if (
        saved &&
        typeof saved === 'object' &&
        'center' in saved &&
        'zoom' in saved &&
        'version' in saved &&
        saved.version === 2 &&
        'region_key' in saved &&
        saved.region_key === region &&
        Array.isArray(saved.center) &&
        saved.center.length === 2 &&
        saved.center.every((n) => typeof n === 'number' && Number.isFinite(n)) &&
        typeof saved.zoom === 'number' &&
        Number.isFinite(saved.zoom) &&
        Math.abs(saved.center[0]) <= 180 &&
        Math.abs(saved.center[1]) <= 85 &&
        saved.zoom >= 0 &&
        saved.zoom <= 22
      ) {
        m.jumpTo({ center: saved.center as [number, number], zoom: saved.zoom })
        return
      }
    } catch {
      /* Browser storage may be disabled; the map remains usable. */
    }
    fit(0)
  }, [fit])
  useEffect(() => {
    const m = map.current
    if (!m || !ready || !m.getSource('grid')) return
    let canceled = false
    const controller = new AbortController()
    const clear = () => {
      if (m.getLayer('terrain-preview')) m.removeLayer('terrain-preview')
      if (m.getSource('terrain-preview')) m.removeSource('terrain-preview')
    }
    const terrain = scenario.terrain
    clear()
    setTerrainShown(false)
    if (terrain.status === 'available' && terrain.asset_id && terrain.sha256) {
      void fetch(
        `/api/v1/map/terrain?asset_id=${encodeURIComponent(terrain.asset_id)}&sha256=${terrain.sha256}`,
        { signal: controller.signal },
      )
        .then(async (response) => {
          if (!response.ok) throw new Error('terrain unavailable')
          const asset: TerrainMap = await response.json()
          if (canceled || map.current !== m) return
          m.addSource('terrain-preview', {
            type: 'image',
            url: asset.image_url,
            coordinates: asset.coordinates,
          })
          m.addLayer(
            {
              id: 'terrain-preview',
              type: 'raster',
              source: 'terrain-preview',
              paint: { 'raster-opacity': 0.42, 'raster-saturation': -0.72 },
            },
            'grid',
          )
          setTerrainLabel(
            asset.asset_id === 'contest-dem-30m' ? '题设DEM · 离线' : '本地DEM · 离线',
          )
          setTerrainShown(true)
        })
        .catch(() => {
          if (!canceled) setTerrainShown(false)
        })
    }
    return () => {
      canceled = true
      controller.abort()
    }
  }, [ready, scenario.terrain])
  useEffect(() => {
    if (!container.current) return
    // Fast Refresh can preserve React state while replacing the native Map instance.
    // A fresh style has no sources yet, even when the previous instance was ready.
    setReady(false)
    let m: maplibregl.Map
    try {
      m = new maplibregl.Map({
        container: container.current,
        center: (latest.current.scenario.base?.coordinates ||
          latest.current.scenario.sites[0]?.coordinates || [0, 20]) as [number, number],
        zoom: latest.current.scenario.base ? 11 : 1.5,
        attributionControl: false,
        style: {
          version: 8,
          sources: {},
          layers: [{ id: 'ground', type: 'background', paint: { 'background-color': '#dce6e2' } }],
        },
      })
    } catch {
      setError(true)
      return
    }
    map.current = m
    cameraOwner.current = null
    cameraRegion.current = null
    m.on('movestart', () => setRouteChoices([]))
    m.on('moveend', () => {
      if (!cameraOwner.current || !latest.current.preserveCamera) return
      try {
        const center = m.getCenter()
        sessionStorage.setItem(
          'yuanhang-map-camera:' + cameraOwner.current,
          JSON.stringify({
            version: 2,
            region_key: cameraRegion.current,
            center: [center.lng, center.lat],
            zoom: m.getZoom(),
          }),
        )
      } catch {
        /* Optional persistence, no business state is stored here. */
      }
    })
    m.on('contextmenu', (event) => {
      event.preventDefault()
      latest.current.onPickCoordinates?.([event.lngLat.lng, event.lngLat.lat])
    })
    const markOverview = () => {
      m.getContainer().dataset.overview = String(m.getZoom() < 10.5)
    }
    markOverview()
    m.on('zoomend', markOverview)
    m.addControl(new maplibregl.ScaleControl({ maxWidth: 90, unit: 'metric' }), 'bottom-left')
    m.on('load', () => {
      if (map.current !== m) return
      m.addSource('grid', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } })
      m.addLayer({
        id: 'grid',
        type: 'line',
        source: 'grid',
        paint: { 'line-color': '#7c8e9c', 'line-width': 0.7, 'line-opacity': 0.25 },
      })
      m.addSource('zones', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } })
      m.addLayer({
        id: 'zones-fill',
        type: 'fill',
        source: 'zones',
        paint: { 'fill-color': '#cf6656', 'fill-opacity': 0.18 },
      })
      m.addLayer({
        id: 'zones-outline',
        type: 'line',
        source: 'zones',
        paint: { 'line-color': '#b75a4e', 'line-width': 1.7, 'line-dasharray': [3, 2] },
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
      for (const id of ['relay-routes', 'relay-backhaul']) {
        m.addSource(id, { type: 'geojson', data: { type: 'FeatureCollection', features: [] } })
        m.addLayer({
          id,
          type: 'line',
          source: id,
          paint: {
            'line-color': '#8970ae',
            'line-width': id === 'relay-routes' ? 2.2 : 1.4,
            'line-dasharray': id === 'relay-routes' ? [4, 2] : [1, 3],
            'line-opacity': 0.8,
          },
        })
      }
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
      m.addLayer({
        id: 'route-pick',
        type: 'line',
        source: 'routes',
        paint: { 'line-width': 22, 'line-opacity': 0, 'line-color': '#000000' },
      })
      m.on('click', 'route-pick', (e) => {
        const choices = new Map<string, RouteChoice>()
        for (const feature of e.features || []) {
          const p = feature.properties
          if (p && typeof p.id === 'string')
            choices.set(p.id, {
              id: p.id,
              drone: String(p.drone || ''),
              cargo: Number(p.cargo || 0),
              stops: String(p.stops || ''),
            })
        }
        const rows = [...choices.values()]
        if (rows.length === 1) {
          setRouteChoices([])
          latest.current.onSelect(rows[0].id)
        } else setRouteChoices(rows)
      })
      m.on('mouseenter', 'route-pick', () => {
        m.getCanvas().style.cursor = 'pointer'
      })
      m.on('mouseleave', 'route-pick', () => {
        m.getCanvas().style.cursor = ''
      })
      m.moveLayer('relay-routes')
      m.moveLayer('relay-backhaul')
      setReady(true)
    })
    const observer = new ResizeObserver(() => {
      m.resize()
      // Legacy workspaces kept the entire small scenario visible on resize.
      // V2 task workspaces retain the user's inspection camera instead.
      if (!latest.current.preserveCamera) fit(0)
    })
    observer.observe(container.current)
    return () => {
      observer.disconnect()
      markers.current.forEach((x) => x.remove())
      aircraft.current.forEach((x) => x.remove())
      relayMarkers.current.forEach((x) => x.remove())
      placeLabels.current.forEach((x) => x.remove())
      m.remove()
      map.current = null
    }
  }, [fit])
  useEffect(() => {
    const m = map.current
    if (!m || !ready || !m.getLayer('zones-fill')) return
    let canceled = false
    const layers = [
      'context-water',
      'context-waterways',
      'context-roads',
      'context-places',
      'context-boundary',
    ]
    const clear = () => {
      if (map.current !== m) return
      for (const id of layers) if (m.getLayer(id)) m.removeLayer(id)
      if (m.getSource('town-context')) m.removeSource('town-context')
    }
    clear()
    setContextLoaded(false)
    if (!contextApplies) {
      setTownData(null)
      return
    }
    void loadTownContextData()
      .then((value) => {
        if (canceled || map.current !== m || !m.getLayer('zones-fill')) return
        m.addSource('town-context', { type: 'geojson', data: value })
        m.addLayer(
          {
            id: 'context-water',
            type: 'fill',
            source: 'town-context',
            filter: ['==', ['get', 'context_kind'], 'water'],
            paint: {
              'fill-color': '#3287ba',
              'fill-opacity': 0.5,
              'fill-outline-color': '#126c9c',
            },
          },
          'zones-fill',
        )
        m.addLayer(
          {
            id: 'context-waterways',
            type: 'line',
            source: 'town-context',
            filter: ['==', ['get', 'context_kind'], 'waterway'],
            paint: {
              'line-color': '#2485bb',
              'line-width': ['interpolate', ['linear'], ['zoom'], 9, 0.5, 14, 2],
              'line-opacity': 0.85,
            },
          },
          'zones-fill',
        )
        m.addLayer(
          {
            id: 'context-roads',
            type: 'line',
            source: 'town-context',
            filter: ['==', ['get', 'context_kind'], 'road'],
            paint: {
              'line-color': '#475569',
              'line-width': ['interpolate', ['linear'], ['zoom'], 9, 0.4, 14, 1.6],
              'line-opacity': 0.5,
            },
          },
          'zones-fill',
        )
        m.addLayer(
          {
            id: 'context-places',
            type: 'circle',
            source: 'town-context',
            filter: ['==', ['get', 'context_kind'], 'place'],
            paint: {
              'circle-color': '#ba8150',
              'circle-radius': ['interpolate', ['linear'], ['zoom'], 9, 1.5, 14, 3],
              'circle-opacity': 0.8,
              'circle-stroke-color': '#fff',
              'circle-stroke-width': 0.6,
            },
          },
          'zones-fill',
        )
        m.addLayer(
          {
            id: 'context-boundary',
            type: 'line',
            source: 'town-context',
            filter: ['==', ['get', 'context_kind'], 'boundary'],
            paint: {
              'line-color': '#7961a7',
              'line-width': 1.8,
              'line-dasharray': [4, 3],
              'line-opacity': 0.85,
            },
          },
          'zones-fill',
        )
        setTownData(value)
        setContextLoaded(true)
      })
      .catch(() => {
        if (!canceled) setContextLoaded(false)
      })
    return () => {
      canceled = true
      clear()
    }
  }, [ready, contextApplies])
  useEffect(() => {
    const m = map.current
    if (!m || !ready || !contextLoaded || !m.getSource('town-context')) return
    for (const id of ['context-water', 'context-waterways', 'context-roads'])
      if (m.getLayer(id)) m.setLayoutProperty(id, 'visibility', showContext ? 'visible' : 'none')
    if (m.getLayer('context-places'))
      m.setLayoutProperty('context-places', 'visibility', showPlaceNames ? 'visible' : 'none')
    if (m.getLayer('context-boundary'))
      m.setLayoutProperty('context-boundary', 'visibility', showBoundary ? 'visible' : 'none')
    if (m.getLayer('context-roads'))
      m.setPaintProperty(
        'context-roads',
        'line-color',
        basemap === 'satellite' ? '#e2e8f0' : '#475569',
      )
  }, [ready, contextLoaded, showContext, showPlaceNames, showBoundary, basemap])
  useEffect(() => {
    const m = map.current
    const clear = () => {
      placeLabels.current.forEach((marker) => marker.remove())
      placeLabels.current = []
    }
    clear()
    if (!m || !ready || !contextLoaded || !townData || !showPlaceNames) return
    const update = () => {
      clear()
      if (map.current !== m || m.getZoom() < 10.5) return
      const canvas = m.getContainer().getBoundingClientRect()
      const occupied = markers.current
        .map((marker) => marker.getElement().getBoundingClientRect())
        .map((r) => ({
          left: r.left - canvas.left - 5,
          top: r.top - canvas.top - 5,
          right: r.right - canvas.left + 5,
          bottom: r.bottom - canvas.top + 5,
        }))
      const points = townData.features
        .filter(
          (f) =>
            f.geometry.type === 'Point' &&
            f.properties.context_name &&
            f.properties.context_name !== '未记录',
        )
        .sort(
          (a, b) =>
            Number(b.properties['重点显示'] === true) - Number(a.properties['重点显示'] === true),
        )
      for (const feature of points) {
        if (feature.geometry.type !== 'Point') continue
        const coordinates = feature.geometry.coordinates as [number, number]
        if (!m.getBounds().contains(coordinates)) continue
        const point = m.project(coordinates),
          width = Math.min(88, feature.properties.context_name.length * 10 + 10)
        const box = {
          left: point.x + 6,
          top: point.y - 9,
          right: point.x + 6 + width,
          bottom: point.y + 9,
        }
        if (
          box.left < 15 ||
          box.top < 108 ||
          box.right > canvas.width - 55 ||
          box.bottom > canvas.height - 120 ||
          occupied.some(
            (b) =>
              box.left < b.right && box.right > b.left && box.top < b.bottom && box.bottom > b.top,
          )
        )
          continue
        occupied.push(box)
        const label = document.createElement('span')
        label.className = 'context-place-label'
        label.textContent = feature.properties.context_name
        label.title = feature.properties.context_name + ' · 原题OSM背景资料'
        placeLabels.current.push(
          new maplibregl.Marker({ element: label, anchor: 'left', offset: [6, 0] })
            .setLngLat(coordinates)
            .addTo(m),
        )
        if (placeLabels.current.length >= 24) break
      }
    }
    update()
    m.on('moveend', update)
    m.on('resize', update)
    return () => {
      clear()
      m.off('moveend', update)
      m.off('resize', update)
    }
  }, [ready, contextLoaded, townData, showPlaceNames, scenario])
  useEffect(() => {
    const m = map.current
    if (!m || !ready || !m.getSource('grid') || basemap !== 'satellite') return
    let active = true
    let loaded = false
    setSatelliteState('loading')
    const fail = () => {
      if (!active) return
      setSatelliteState('failed')
      setBasemap('offline')
    }
    const onError = (event: maplibregl.ErrorEvent) => {
      const sourceId = (event as { sourceId?: string }).sourceId
      if (sourceId === 'satellite-imagery' || event.error.message.includes('arcgisonline.com'))
        fail()
    }
    const onData = (event: maplibregl.MapSourceDataEvent) => {
      // Raster sources announce metadata/content before any image has arrived.
      const tile: unknown = event.tile
      if (
        event.sourceId === 'satellite-imagery' &&
        tile &&
        typeof tile === 'object' &&
        'state' in tile &&
        tile.state === 'loaded'
      ) {
        loaded = true
        setSatelliteState('ready')
      }
    }
    m.on('error', onError)
    m.on('sourcedata', onData)
    // Only this explicit selection creates a remote source. No prefetch/cache bundle.
    m.addSource('satellite-imagery', {
      type: 'raster',
      tiles: [
        'https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      ],
      tileSize: 256,
      minzoom: 0,
      maxzoom: 19,
      attribution: 'Esri, Vantor, Earthstar Geographics, GIS User Community',
    })
    m.addLayer(
      {
        id: 'satellite-imagery',
        type: 'raster',
        source: 'satellite-imagery',
        paint: { 'raster-opacity': 1 },
      },
      'grid',
    )
    const timer = window.setTimeout(() => {
      if (!loaded) fail()
    }, 12000)
    return () => {
      active = false
      window.clearTimeout(timer)
      m.off('error', onError)
      m.off('sourcedata', onData)
      if (m.getLayer('satellite-imagery')) m.removeLayer('satellite-imagery')
      if (m.getSource('satellite-imagery')) m.removeSource('satellite-imagery')
    }
  }, [ready, basemap])
  useEffect(() => {
    const m = map.current
    if (!m || !ready || !m.getLayer('grid')) return
    m.setLayoutProperty('grid', 'visibility', basemap === 'satellite' ? 'none' : 'visible')
  }, [ready, basemap])
  useEffect(() => {
    const m = map.current
    if (!m || !ready || !m.getSource('grid') || !m.getSource('zones')) return
    markers.current.forEach((x) => x.remove())
    markers.current = []
    const bounds = new maplibregl.LngLatBounds()
    for (const [i, n] of mapNodes(scenario).entries()) {
      const isBase = n.id === scenario.base?.id
      bounds.extend(n.coordinates as [number, number])
      const button = document.createElement('button')
      button.dataset.siteId = n.id
      button.className = `map-marker ${isBase ? 'map-marker-base' : ''} ${!n.available ? 'unavailable' : ''}`
      const dot = document.createElement('span')
      dot.className = 'map-marker-dot'
      dot.textContent = isBase ? 'O' : String(i + (scenario.base ? 0 : 1))
      button.dataset.dotText = dot.textContent
      const label = document.createElement('span')
      label.className = 'map-marker-label'
      label.textContent = isBase ? n.name.slice(0, 8) : n.id
      if (!isBase && scenario.sites.length > 8) label.hidden = true
      button.append(dot, label)
      button.title = `${n.id} · ${n.coordinates.join(', ')}`
      button.setAttribute('aria-label', `定位${n.name}`)
      button.onclick = (event) => {
        event.stopPropagation()
        if (Number(button.dataset.clusterCount || 1) > 1) {
          const ids: string[] = JSON.parse(button.dataset.clusterSiteIds || '[]')
          setRouteChoices([])
          setSiteChoices(mapNodes(latest.current.scenario).filter((node) => ids.includes(node.id)))
          return
        }
        latest.current.onSelectSite?.(n.id)
        const route = latest.current.plan?.sorties.find((r) =>
          r.visits.some((v) => v.site_id === n.id),
        )
        if (route && !latest.current.onSelectSite) latest.current.onSelect(route.sortie_id)
        m.easeTo({ center: n.coordinates as [number, number], duration: 400 })
      }
      markers.current.push(
        new maplibregl.Marker({ element: button, anchor: 'center' })
          .setLngLat(n.coordinates as [number, number])
          .addTo(m),
      )
    }
    if (bounds.isEmpty()) bounds.extend([-180, -70]).extend([180, 70])
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
    const zones: FeatureCollection<Polygon> = {
      type: 'FeatureCollection',
      features: (scenario.restricted_zones || []).map((z) => ({
        type: 'Feature',
        properties: { id: z.zone_id, name: z.name, buffer_m: z.buffer_m },
        geometry: z.geometry as Polygon,
      })),
    }
    ;(m.getSource('zones') as maplibregl.GeoJSONSource).setData(zones)
    const arrange = () => {
      const occupied: { x: number; y: number; marker: maplibregl.Marker; count: number }[] = []
      const order = [...markers.current].sort(
        (a, b) =>
          Number(b.getElement().dataset.siteId === latest.current.selectedSite) -
          Number(a.getElement().dataset.siteId === latest.current.selectedSite),
      )
      for (const marker of order) {
        const element = marker.getElement(),
          point = m.project(marker.getLngLat())
        const dot = element.querySelector<HTMLElement>('.map-marker-dot')
        element.style.visibility = 'visible'
        element.dataset.clusterCount = '1'
        element.dataset.clusterSiteIds = JSON.stringify([element.dataset.siteId])
        if (dot) dot.textContent = element.dataset.dotText || ''
        const near = occupied.find((p) => Math.hypot(point.x - p.x, point.y - p.y) < 29)
        if (near) {
          element.style.visibility = 'hidden'
          near.count++
          near.marker.getElement().dataset.clusterCount = String(near.count)
          const grouped = near.marker.getElement()
          grouped.dataset.clusterSiteIds = JSON.stringify([
            ...JSON.parse(grouped.dataset.clusterSiteIds || '[]'),
            element.dataset.siteId,
          ])
          const firstDot = near.marker.getElement().querySelector<HTMLElement>('.map-marker-dot')
          if (firstDot) firstDot.textContent = `+${near.count}`
        } else occupied.push({ x: point.x, y: point.y, marker, count: 1 })
      }
      const boxes = [
        ...m
          .getContainer()
          .parentElement!.querySelectorAll<HTMLElement>(
            '.map-header,.map-basemap-switch,.map-weather-context,.map-controls,.map-layers,.map-legend,.map-imagery-credit,.map-satellite-warning,.map-marker-dot',
          ),
      ]
        .filter(
          (el) => el.getClientRects().length > 0 && getComputedStyle(el).visibility !== 'hidden',
        )
        .map((el) => el.getBoundingClientRect())
      for (const marker of order) {
        const el = marker.getElement(),
          label = el.querySelector<HTMLElement>('.map-marker-label')
        if (!label || label.hidden || el.style.visibility === 'hidden') continue
        label.style.visibility = 'visible'
        const rect = label.getBoundingClientRect()
        if (
          boxes.some(
            (b) =>
              rect.left < b.right + 4 &&
              rect.right > b.left - 4 &&
              rect.top < b.bottom + 4 &&
              rect.bottom > b.top - 4,
          )
        )
          label.style.visibility = 'hidden'
        else boxes.push(rect)
      }
    }
    updateSiteLayout.current = arrange
    m.on('moveend', arrange)
    m.on('resize', arrange)
    restoreView()
    arrange()
    return () => {
      m.off('moveend', arrange)
      m.off('resize', arrange)
      if (updateSiteLayout.current === arrange) updateSiteLayout.current = null
    }
  }, [ready, scenario, restoreView, viewKey])
  useEffect(() => {
    for (const marker of markers.current) {
      const element = marker.getElement()
      const node = mapNodes(scenario).find((n) => n.id === element.dataset.siteId)
      const label = element.querySelector<HTMLElement>('.map-marker-label')
      if (node && label) {
        const active = node.id === selectedSite
        label.textContent = active
          ? node.name
          : node.id === scenario.base?.id
            ? node.name.slice(0, 8)
            : node.id
        label.hidden = !active && node.id !== scenario.base?.id && scenario.sites.length > 8
        element.classList.toggle('selected-site', active)
      }
    }
    updateSiteLayout.current?.()
  }, [ready, selectedSite, scenario])
  useEffect(() => {
    if (
      !map.current ||
      !ready ||
      !map.current.getLayer('zones-fill') ||
      !map.current.getLayer('zones-outline')
    )
      return
    for (const layer of ['zones-fill', 'zones-outline'])
      map.current.setLayoutProperty(layer, 'visibility', showZones ? 'visible' : 'none')
  }, [ready, showZones])
  useEffect(() => {
    const m = map.current
    if (!m || !ready || !m.getSource('routes') || !m.getSource('old-routes')) return
    const collection = (p: Plan | null | undefined): FeatureCollection<LineString> => ({
      type: 'FeatureCollection',
      features: (p?.sorties || []).map((r) => ({
        type: 'Feature',
        properties: {
          id: r.sortie_id,
          color: colorFor(r.drone_id),
          selected: selected === r.sortie_id,
          dim: !!selected && selected !== r.sortie_id,
          drone: r.drone_id,
          cargo: r.cargo_ids.length,
          stops: r.visits.map((v) => v.site_id).join(' → '),
        },
        geometry: r.route_geometry as LineString,
      })),
    })
    const current = routeSets
      ? {
          type: 'FeatureCollection' as const,
          features: routeSets.flatMap((set) =>
            collection(set.plan)
              .features.filter((f) => set.sortieIds.includes(String(f.properties?.id)))
              .map((f) => ({
                ...f,
                properties: {
                  ...f.properties,
                  id: `${set.plan.plan_id}:${f.properties?.id}`,
                  selected: selected === `${set.plan.plan_id}:${f.properties?.id}`,
                  dim: !!selected && selected !== `${set.plan.plan_id}:${f.properties?.id}`,
                },
              })),
          ),
        }
      : collection(plan)
    ;(m.getSource('routes') as maplibregl.GeoJSONSource).setData(current)
    ;(m.getSource('old-routes') as maplibregl.GeoJSONSource).setData(collection(oldPlan))
    m.setLayoutProperty('routes', 'visibility', showRoutes ? 'visible' : 'none')
    m.setLayoutProperty('routes-halo', 'visibility', showRoutes ? 'visible' : 'none')
    m.setLayoutProperty('route-pick', 'visibility', showRoutes ? 'visible' : 'none')
    m.setLayoutProperty('old-routes', 'visibility', showOld ? 'visible' : 'none')
  }, [ready, plan, oldPlan, selected, showRoutes, showOld, routeSets])
  useEffect(() => {
    const m = map.current
    if (!m || !ready || !m.getSource('relay-routes') || !m.getSource('relay-backhaul')) return
    const relays = plan?.relay_sorties || []
    relayMarkers.current.forEach((marker) => marker.remove())
    relayMarkers.current = []
    const paths: FeatureCollection<LineString> = {
      type: 'FeatureCollection',
      features: relays.map((r) => ({
        type: 'Feature',
        properties: { id: r.relay_sortie_id },
        geometry: r.route_geometry as LineString,
      })),
    }
    const links: FeatureCollection<LineString> = {
      type: 'FeatureCollection',
      features: relays
        .filter(
          (r) =>
            !!scenario.base &&
            (playTime == null || (r.service_start_s <= playTime && playTime <= r.service_end_s)),
        )
        .map((r) => ({
          type: 'Feature',
          properties: { id: r.relay_sortie_id },
          geometry: {
            type: 'LineString',
            coordinates: [scenario.base!.coordinates, r.station_coordinates],
          },
        })),
    }
    ;(m.getSource('relay-routes') as maplibregl.GeoJSONSource).setData(paths)
    ;(m.getSource('relay-backhaul') as maplibregl.GeoJSONSource).setData(links)
    for (const id of ['relay-routes', 'relay-backhaul'])
      m.setLayoutProperty(id, 'visibility', showRelays ? 'visible' : 'none')
    if (!showRelays) return
    const seen = new Set<string>()
    for (const row of relays) {
      if (seen.has(row.station_id)) continue
      seen.add(row.station_id)
      const element = document.createElement('button')
      element.className = 'map-marker map-marker-relay'
      element.title = `${row.station_id} · 悬停离地${row.station_agl_m}m\n${relays
        .filter((r) => r.station_id === row.station_id)
        .map(
          (r) => `${r.drone_id} ${Math.round(r.service_start_s)}–${Math.round(r.service_end_s)}秒`,
        )
        .join('\n')}\n紫色点线为已验证的固定网关回传，非覆盖半径`
      element.setAttribute('aria-label', `中继服务点${row.station_id}`)
      const dot = document.createElement('span')
      dot.className = 'map-marker-dot'
      dot.textContent = 'R'
      const label = document.createElement('span')
      label.className = 'map-marker-label'
      label.textContent = row.station_id
      element.append(dot, label)
      element.onclick = () =>
        m.easeTo({ center: row.station_coordinates as [number, number], duration: 350 })
      relayMarkers.current.push(
        new maplibregl.Marker({ element, anchor: 'center' })
          .setLngLat(row.station_coordinates as [number, number])
          .addTo(m),
      )
    }
  }, [ready, plan, showRelays, playTime, scenario.base])
  useEffect(() => {
    const m = map.current
    if (!m || !ready || !terrainShown || !m.getLayer('terrain-preview')) return
    m.setLayoutProperty(
      'terrain-preview',
      'visibility',
      showTerrain && basemap === 'offline' ? 'visible' : 'none',
    )
  }, [ready, terrainShown, showTerrain, basemap])
  useEffect(() => {
    const m = map.current
    if (!m || !ready || !m.getSource('grid')) return
    aircraft.current.forEach((x) => x.remove())
    aircraft.current = []
    if (telemetry) {
      const groups: { sample: Telemetry; members: Telemetry[]; x: number; y: number }[] = []
      for (const sample of telemetry) {
        if (
          !sample.coordinates ||
          ['available', 'ready', 'unavailable', 'not_ready'].includes(sample.phase)
        )
          continue
        const point = m.project(sample.coordinates)
        const near = groups.find((g) => Math.hypot(g.x - point.x, g.y - point.y) < 26)
        if (near) near.members.push(sample)
        else groups.push({ sample, members: [sample], x: point.x, y: point.y })
      }
      for (const { sample, members } of groups) {
        const button = document.createElement('button')
        button.className = `planned-aircraft simulated-aircraft ${sample.quality === 'stale' ? 'stale-aircraft' : ''}`
        button.textContent = members.length > 1 ? `✈ ${members.length}` : '✈'
        const tag = document.createElement('span')
        tag.textContent =
          members.length > 1
            ? `${members.length} 架同屏机体`
            : `${sample.device_id}${sample.quality === 'stale' ? ' · 失联' : ' · 模拟'}`
        button.append(tag)
        button.title = `${sample.device_id} · ${sample.phase} · ${sample.observed_at}`
        button.onclick = (event) => {
          event.stopPropagation()
          if (members.length > 1) {
            setDeviceChoices(members)
            setSiteChoices([])
            setRouteChoices([])
          } else if (latest.current.onSelectDevice) latest.current.onSelectDevice(sample.device_id)
          else if (sample.sortie_id) latest.current.onSelect(sample.sortie_id)
        }
        button.setAttribute(
          'aria-label',
          members.length > 1
            ? `选择${members.length}架同屏模拟机体`
            : `查看模拟机体${sample.device_id}`,
        )
        aircraft.current.push(
          new maplibregl.Marker({ element: button }).setLngLat(sample.coordinates!).addTo(m),
        )
      }
      return
    }
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
      button.onclick = (event) => {
        event.stopPropagation()
        latest.current.onSelect(phase.sortie_id)
      }
      const tag = document.createElement('span')
      tag.textContent = `${phase.drone_id} ${label}`
      button.append(tag)
      aircraft.current.push(
        new maplibregl.Marker({ element: button, anchor: 'center' })
          .setLngLat(coordinates)
          .addTo(m),
      )
    }
  }, [ready, playTime, playback, telemetry])
  return (
    <div
      className={`rescue-map ${compact ? 'map-compact' : ''}`}
      data-basemap={basemap}
      data-imagery-state={satelliteState}
      data-context={contextVisible}
    >
      <div ref={container} className="map-canvas" />
      {siteChoices.length > 1 && (
        <section className="map-route-choices" aria-label="聚合点位选择">
          <div>
            <strong>此处有 {siteChoices.length} 个点位</strong>
            <button onClick={() => setSiteChoices([])} aria-label="关闭点位选择">
              ×
            </button>
          </div>
          <p>选择点位查看详情；相同坐标也可分别核对。</p>
          <ul>
            {siteChoices.map((node) => (
              <li key={node.id}>
                <button
                  onClick={() => {
                    latest.current.onSelectSite?.(node.id)
                    const route = latest.current.plan?.sorties.find((r) =>
                      r.visits.some((v) => v.site_id === node.id),
                    )
                    if (route && !latest.current.onSelectSite)
                      latest.current.onSelect(route.sortie_id)
                    setSiteChoices([])
                  }}
                >
                  <b>{node.name}</b>
                  <small>
                    {node.id} · {node.coordinates.map((n) => n.toFixed(6)).join(', ')}
                  </small>
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}
      {deviceChoices.length > 1 && (
        <section className="map-route-choices" aria-label="同屏机体选择">
          <div>
            <strong>{deviceChoices.length} 架同屏模拟机体</strong>
            <button onClick={() => setDeviceChoices([])} aria-label="关闭机体选择">
              ×
            </button>
          </div>
          <p>图标按屏幕距离聚合，实际坐标在机体详情核对。</p>
          <ul>
            {deviceChoices.map((sample) => (
              <li key={sample.device_id}>
                <button
                  onClick={() => {
                    if (latest.current.onSelectDevice)
                      latest.current.onSelectDevice(sample.device_id)
                    else if (sample.sortie_id) latest.current.onSelect(sample.sortie_id)
                    setDeviceChoices([])
                  }}
                >
                  <b>{sample.device_id}</b>
                  <small>
                    {sample.coordinates?.map((n) => n.toFixed(6)).join(', ')} ·{' '}
                    {sample.cargo_ids.length} 箱
                  </small>
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}
      {routeChoices.length > 1 && (
        <section className="map-route-choices" aria-label="重叠航线选择">
          <div>
            <strong>此处有 {routeChoices.length} 条航线</strong>
            <button onClick={() => setRouteChoices([])} aria-label="关闭航线选择">
              ×
            </button>
          </div>
          <p>选择要核对的架次</p>
          <ul>
            {routeChoices.map((choice) => (
              <li key={choice.id}>
                <button
                  onClick={() => {
                    latest.current.onSelect(choice.id)
                    setRouteChoices([])
                  }}
                >
                  <b>
                    {choice.drone} · {choice.cargo} 箱
                  </b>
                  <small>{choice.stops}</small>
                  <code>{choice.id}</code>
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}
      {error && (
        <div className="map-error">地图渲染不可用，点位与路线仍可在任务表和导出中查看。</div>
      )}
      <div className="map-header">
        <span>
          <MapPinned size={14} /> 场景地图 <i /> <b>WGS84</b>
        </span>
        <span className="map-mode">
          {basemap === 'satellite'
            ? satelliteState === 'loading'
              ? '正在加载在线影像…'
              : '在线真实影像'
            : scenario.terrain.status === 'available' && terrainShown && showTerrain
              ? terrainLabel
              : '本地坐标底图'}
        </span>
      </div>
      <div className="map-basemap-switch" role="group" aria-label="地图底图">
        <button
          type="button"
          aria-pressed={basemap === 'offline'}
          onClick={() => setBasemap('offline')}
        >
          <Mountain size={14} />
          离线地形
        </button>
        <button
          type="button"
          aria-pressed={basemap === 'satellite'}
          onClick={() => setBasemap('satellite')}
        >
          <Satellite size={14} />
          卫星影像<span>联网</span>
        </button>
      </div>
      {satelliteState === 'failed' && basemap === 'offline' && (
        <div className="map-satellite-warning" role="status">
          在线影像暂不可用，已恢复离线地形。点位与计算不受影响。
        </div>
      )}
      {scenario.weather && showWeather && (
        <div
          className="map-weather-context"
          title={`${scenario.weather.source_ref} · 发布 ${scenario.weather.issued_at} · 高度 AGL ${scenario.weather.height_m} m`}
        >
          <strong>人工气象情景 · W1</strong>
          <span>
            风 {scenario.weather.wind_speed_mps ?? '未知'} m/s ·{' '}
            {scenario.weather.valid_from_s / 60}—{scenario.weather.valid_until_s / 60} min
          </span>
          <small>全区域均匀假设 · 阈值/窗口约束</small>
        </div>
      )}
      <div className="map-controls">
        <button aria-label="放大地图" onClick={() => map.current?.zoomIn()}>
          <Plus size={17} />
        </button>
        <button aria-label="缩小地图" onClick={() => map.current?.zoomOut()}>
          <Minus size={17} />
        </button>
        <button aria-label="适配全部点位" onClick={() => fit()}>
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
          {scenario.weather && (
            <label>
              <input
                type="checkbox"
                checked={showWeather}
                onChange={(e) => setShowWeather(e.target.checked)}
              />
              人工气象信息（仅显隐）
            </label>
          )}
          {contextLoaded && (
            <>
              <button
                type="button"
                className="map-context-fit"
                onClick={() => {
                  if (townMetadata)
                    map.current?.fitBounds(
                      [
                        [townMetadata.bounds[0], townMetadata.bounds[1]],
                        [townMetadata.bounds[2], townMetadata.bounds[3]],
                      ],
                      { padding: { top: 115, bottom: 125, left: 45, right: 65 }, duration: 500 },
                    )
                  setLayersOpen(false)
                }}
              >
                查看地理背景全范围
              </button>
              <label>
                <input
                  type="checkbox"
                  checked={showContext}
                  onChange={(e) => setShowContext(e.target.checked)}
                />
                原题道路与水系背景
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={showPlaceNames}
                  onChange={(e) => setShowPlaceNames(e.target.checked)}
                />
                村镇点位与地名
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={showBoundary}
                  onChange={(e) => setShowBoundary(e.target.checked)}
                />
                镇龙乡参考边界
              </label>
              <p>
                历史OSM背景，仅本区域显示；不参与障碍/空域求解，非灾后现势或正式行政界。缩放时地名自动避让任务点位。
              </p>
            </>
          )}
          {terrainShown && (
            <label>
              <input
                type="checkbox"
                checked={showTerrain}
                onChange={(e) => setShowTerrain(e.target.checked)}
              />
              绑定DEM地形
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
          {!!scenario.restricted_zones?.length && (
            <label>
              <input
                type="checkbox"
                checked={showZones}
                onChange={(e) => setShowZones(e.target.checked)}
              />
              限制区原始边界
            </label>
          )}
          {!!plan?.communication_report && (
            <label>
              <input
                type="checkbox"
                checked={showRelays}
                onChange={(e) => setShowRelays(e.target.checked)}
              />
              中继路线、服务点与回传
            </label>
          )}
          <p>
            点位与航线来自绑定输入/计算。限制区显示原始边界，计算另含缓冲。紫色点线表示中继固定回传链路，不代表圆形覆盖范围。
          </p>
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
        {!!scenario.restricted_zones?.length && (
          <span>
            <i style={{ background: '#cf6656', borderRadius: 2 }} />
            限制区
          </span>
        )}
        {!!plan?.relay_sorties?.length && (
          <span>
            <i style={{ background: '#8970ae' }} />
            中继服务点
          </span>
        )}
      </div>
      <div className="map-attribution">
        {contextVisible && (
          <span className="map-context-credit">
            <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">
              © OpenStreetMap contributors · ODbL
            </a>{' '}
            · 历史背景资料
          </span>
        )}
        {basemap === 'satellite' && (
          <span className="map-imagery-credit">
            <a
              href="https://www.arcgis.com/home/item.html?id=10df2279f9684e4a9f6a7f08febac2a9"
              target="_blank"
              rel="noreferrer"
            >
              Esri · Vantor · Earthstar · GIS Community
            </a>
            <span>拍摄日期未核验 · 非实时灾情/高程数据</span>
          </span>
        )}
        {telemetry
          ? '服务器模拟观测 · 非真机遥测'
          : playTime != null
            ? '计划位置为匀速插值示意 · 非实时遥测'
            : '离线可用 · 图上路线为任务级建议'}
      </div>
    </div>
  )
}
