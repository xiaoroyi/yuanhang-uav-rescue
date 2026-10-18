import { useEffect, useMemo, useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Expand,
  Layers3,
  LoaderCircle,
  Mountain,
  RotateCcw,
  TriangleAlert,
  ZoomIn,
  ZoomOut,
} from 'lucide-react'
import { api, type Plan, type Scenario, type TerrainSurface } from '../api/client'
import { ops, type Stages } from '../api/operations'
import { number, percent } from '../lib/format'
import { terrainMeshIndices } from './terrain-scene-data'
import './terrain-scene.css'

type Props = {
  scenario: Scenario
  plan: Plan | null
  onOpenMap: () => void
  selectedSortie?: string | null
}
type SceneActions = {
  reset: () => void
  zoom: (factor: number) => void
  rotate: (angle: number, tilt?: number) => void
}

const terrainTone = (t: number): [number, number, number] => {
  const stops = [
    [0.08, 0.15, 0.28],
    [0.16, 0.35, 0.44],
    [0.39, 0.53, 0.58],
    [0.68, 0.58, 0.52],
    [0.91, 0.82, 0.65],
  ]
  const p = Math.min(3.999, Math.max(0, t) * 4),
    i = Math.floor(p),
    u = p - i
  return stops[i].map((v, k) => v + (stops[i + 1][k] - v) * u) as [number, number, number]
}

function SurfaceCanvas({
  surface,
  scenario,
  plan,
  exaggeration,
  wireframe,
  trajectories,
}: {
  surface: TerrainSurface
  scenario: Scenario
  plan: Plan | null
  exaggeration: number
  wireframe: boolean
  trajectories: Stages['trajectory_segments']
}) {
  const host = useRef<HTMLDivElement>(null)
  const actions = useRef<SceneActions | null>(null)
  const [state, setState] = useState<'loading' | 'ready' | 'failed'>('loading')
  const [failure, setFailure] = useState('')
  useEffect(() => {
    const container = host.current
    if (!container) return
    setState('loading')
    let canceled = false
    const dispose: Array<() => void> = []
    const cleanup = () => {
      actions.current = null
      for (const release of dispose.splice(0).reverse()) release()
    }
    void Promise.all([import('three'), import('three/addons/controls/OrbitControls.js')])
      .then(([T, { OrbitControls }]) => {
        if (canceled) return
        try {
          const scene = new T.Scene()
          scene.background = new T.Color('#09111f')
          scene.fog = new T.Fog('#09111f', 180, 450)
          const renderer = new T.WebGLRenderer({
            antialias: true,
            alpha: false,
            powerPreference: 'low-power',
          })
          dispose.push(() => {
            renderer.dispose()
            renderer.forceContextLoss()
            renderer.domElement.remove()
          })
          const assets: Array<{ dispose: () => void }> = []
          dispose.push(() => {
            for (const asset of assets) asset.dispose()
          })
          renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5))
          renderer.outputColorSpace = T.SRGBColorSpace
          renderer.toneMapping = T.ACESFilmicToneMapping
          renderer.toneMappingExposure = 1.35
          renderer.domElement.setAttribute('aria-hidden', 'true')
          container.appendChild(renderer.domElement)
          const camera = new T.PerspectiveCamera(40, 1, 0.1, 1000)
          camera.position.set(100, 100, 125)
          const controls = new OrbitControls(camera, renderer.domElement)
          dispose.push(() => controls.dispose())
          controls.enableDamping = false
          controls.minDistance = 20
          controls.maxDistance = 360
          controls.maxPolarAngle = Math.PI * 0.48
          controls.target.set(0, 5, 0)
          controls.update()
          controls.saveState()
          scene.add(new T.AmbientLight('#d7e5ff', 1.5))
          const light = new T.DirectionalLight('#c3dcff', 2.3)
          light.position.set(-70, 130, 35)
          scene.add(light)
          const warm = new T.DirectionalLight('#ffe6bb', 1)
          warm.position.set(80, 60, -60)
          scene.add(warm)
          const [west, south, east, north] = surface.bounds
          const midLat = (south + north) / 2,
            midLon = (west + east) / 2
          const lonM = 111320 * Math.cos((midLat * Math.PI) / 180),
            latM = 111320
          const span = Math.max((east - west) * lonM, (north - south) * latM, 1)
          const scale = 135 / span
          const floor = surface.min_elevation_m
          const project = (lon: number, lat: number, elevation: number) =>
            new T.Vector3(
              (lon - midLon) * lonM * scale,
              (elevation - floor) * scale * exaggeration,
              -(lat - midLat) * latM * scale,
            )
          const width = surface.longitude.length,
            height = surface.latitude.length
          const vertices: number[] = [],
            colors: number[] = []
          const indices = terrainMeshIndices(surface.elevations_m)
          const range = Math.max(1, surface.max_elevation_m - floor)
          for (let y = 0; y < height; y++)
            for (let x = 0; x < width; x++) {
              const h = surface.elevations_m[y][x]
              // Placeholder vertices are never indexed: NoData cells remain genuine holes.
              const point = project(surface.longitude[x], surface.latitude[y], h ?? floor)
              vertices.push(point.x, point.y, point.z)
              colors.push(...terrainTone(h == null ? 0 : (h - floor) / range))
            }
          const geometry = new T.BufferGeometry()
          assets.push(geometry)
          geometry.setAttribute('position', new T.Float32BufferAttribute(vertices, 3))
          geometry.setAttribute('color', new T.Float32BufferAttribute(colors, 3))
          geometry.setIndex(indices)
          geometry.computeVertexNormals()
          const material = new T.MeshStandardMaterial({
            vertexColors: true,
            roughness: 0.86,
            metalness: 0.06,
            side: T.DoubleSide,
            wireframe,
          })
          assets.push(material)
          scene.add(new T.Mesh(geometry, material))
          const grid = new T.GridHelper(180, 18, '#274563', '#172b42')
          grid.position.y = -0.4
          scene.add(grid)
          const nearest = (lon: number, lat: number) => {
            if (lon < west || lon > east || lat < south || lat > north) return null
            let x = 0,
              y = 0
            for (let i = 1; i < width; i++)
              if (Math.abs(surface.longitude[i] - lon) < Math.abs(surface.longitude[x] - lon)) x = i
            for (let i = 1; i < height; i++)
              if (Math.abs(surface.latitude[i] - lat) < Math.abs(surface.latitude[y] - lat)) y = i
            return surface.elevations_m[y][x]
          }
          assets.push(
            grid.geometry,
            ...(Array.isArray(grid.material) ? grid.material : [grid.material]),
          )
          const markerGeometry = new T.SphereGeometry(0.8, 12, 8)
          assets.push(markerGeometry)
          const labels: Array<{ element: HTMLSpanElement; point: InstanceType<typeof T.Vector3> }> =
            []
          dispose.push(() => {
            for (const label of labels) label.element.remove()
          })
          for (const [i, site] of [scenario.base, ...scenario.sites].entries()) {
            const [lon, lat] = site.coordinates
            const elevation = nearest(lon, lat)
            if (elevation == null) continue
            const point = project(lon, lat, elevation)
            const markerMaterial = new T.MeshBasicMaterial({ color: i ? '#ffca80' : '#6ce5ff' })
            assets.push(markerMaterial)
            const sphere = new T.Mesh(markerGeometry, markerMaterial)
            sphere.position.copy(point).add(new T.Vector3(0, 1.2, 0))
            scene.add(sphere)
            const label = document.createElement('span')
            label.className = `terrain-scene-node-label ${i ? '' : 'terrain-scene-node-base'}`
            label.textContent = `${i ? '救援点' : '调度中心'} · ${site.name || site.id}`
            label.title = label.textContent
            label.setAttribute('aria-hidden', 'true')
            container.appendChild(label)
            labels.push({
              element: label,
              point: point.clone().add(new T.Vector3(0, i ? 4.5 : 7.5, 0)),
            })
            const stemGeometry = new T.BufferGeometry().setFromPoints([
              point,
              point.clone().add(new T.Vector3(0, i ? 4 : 7, 0)),
            ])
            const stemMaterial = new T.LineBasicMaterial({
              color: i ? '#ffca80' : '#6ce5ff',
              transparent: true,
              opacity: 0.7,
            })
            assets.push(stemGeometry, stemMaterial)
            scene.add(new T.Line(stemGeometry, stemMaterial))
          }
          let segments = 0
          for (const sortie of plan?.sorties || []) {
            if (segments > 12000) break
            const coords = sortie.route_geometry.coordinates
            const lineMaterial = new T.LineBasicMaterial({
              color: '#b4a0ff',
              transparent: true,
              opacity: 0.25,
            })
            assets.push(lineMaterial)
            let points: InstanceType<typeof T.Vector3>[] = []
            const flush = () => {
              if (points.length > 1) {
                const g = new T.BufferGeometry().setFromPoints(points)
                assets.push(g)
                scene.add(new T.Line(g, lineMaterial))
              }
              points = []
            }
            for (let i = 0; i < coords.length - 1; i++) {
              const [a, b] = [coords[i], coords[i + 1]]
              const steps = Math.min(
                160,
                Math.max(
                  2,
                  Math.ceil(Math.hypot((b[0] - a[0]) * lonM, (b[1] - a[1]) * latM) / (span / 100)),
                ),
              )
              for (let s = 0; s <= steps; s++) {
                if (++segments > 12000) break
                const t = s / steps,
                  lon = a[0] + (b[0] - a[0]) * t,
                  lat = a[1] + (b[1] - a[1]) * t
                const h = nearest(lon, lat)
                if (h == null) {
                  flush()
                  continue
                }
                points.push(project(lon, lat, h).add(new T.Vector3(0, 0.7, 0)))
              }
            }
            flush()
          }
          // True model phase geometry, not a terrain-draped line.
          for (const segment of trajectories) {
            if (
              !['climb', 'cruise', 'descent'].includes(segment.phase) ||
              segment.start_elevation_m == null ||
              segment.end_elevation_m == null
            )
              continue
            const a = segment.from_coordinates,
              b = segment.to_coordinates
            if (!a || !b) continue
            const geometry = new T.BufferGeometry().setFromPoints([
              project(a[0], a[1], segment.start_elevation_m),
              project(b[0], b[1], segment.end_elevation_m),
            ])
            const material = new T.LineBasicMaterial({
              color: segment.phase === 'cruise' ? '#a8e8d3' : '#ffce82',
              depthTest: false,
            })
            assets.push(geometry, material)
            const line = new T.Line(geometry, material)
            line.renderOrder = 5
            scene.add(line)
          }
          // Start at the actual task region, not the full asset extent (which may be much larger).
          if (labels.length) {
            const x = labels.map((l) => l.point.x),
              z = labels.map((l) => l.point.z)
            const center = new T.Vector3(
              (Math.min(...x) + Math.max(...x)) / 2,
              3,
              (Math.min(...z) + Math.max(...z)) / 2,
            )
            const distance = Math.max(
              30,
              Math.min(
                180,
                Math.max(Math.max(...x) - Math.min(...x), Math.max(...z) - Math.min(...z)) * 2.4,
              ),
            )
            camera.position
              .copy(center)
              .add(new T.Vector3(distance * 0.65, distance * 0.72, distance * 0.85))
            controls.target.copy(center)
            controls.update()
            controls.saveState()
          }
          const render = () => {
            renderer.render(scene, camera)
            const occupied: Array<{ left: number; right: number; top: number; bottom: number }> = []
            for (const label of labels) {
              const p = label.point.clone().project(camera)
              label.element.hidden = Math.abs(p.x) > 0.96 || Math.abs(p.y) > 0.9 || p.z > 1
              if (label.element.hidden) continue
              const x = ((p.x + 1) * container.clientWidth) / 2,
                y = ((1 - p.y) * container.clientHeight) / 2
              const width = label.element.offsetWidth,
                height = label.element.offsetHeight
              let lift = 0
              const box = () => ({
                left: x - width / 2 - 2,
                right: x + width / 2 + 2,
                top: y - height - lift - 2,
                bottom: y - lift + 2,
              })
              let placed = false
              for (const offset of [
                0,
                height + 6,
                -height - 8,
                2 * (height + 6),
                -2 * (height + 8),
                3 * (height + 6),
              ]) {
                lift = offset
                const a = box()
                if (
                  a.left >= 6 &&
                  a.right <= container.clientWidth - 6 &&
                  a.top >= 8 &&
                  a.bottom <= container.clientHeight - 35 &&
                  !occupied.some(
                    (b) =>
                      a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top,
                  )
                ) {
                  placed = true
                  break
                }
              }
              if (!placed) {
                label.element.hidden = true
                continue
              }
              occupied.push(box())
              label.element.style.left = `${x}px`
              label.element.style.top = `${y - lift}px`
              label.element.style.setProperty('--terrain-label-lift', `${lift}px`)
            }
          }
          const observer = new ResizeObserver(() => {
            const w = container.clientWidth,
              h = container.clientHeight
            renderer.setSize(w, h, false)
            camera.aspect = w / Math.max(1, h)
            camera.updateProjectionMatrix()
            render()
          })
          observer.observe(container)
          dispose.push(() => observer.disconnect())
          controls.addEventListener('change', render)
          const rotate = (azimuth: number, polar = 0) => {
            const offset = camera.position.clone().sub(controls.target)
            const spherical = new T.Spherical().setFromVector3(offset)
            spherical.theta += azimuth
            spherical.phi = Math.max(0.15, Math.min(Math.PI * 0.48, spherical.phi + polar))
            camera.position.copy(controls.target).add(new T.Vector3().setFromSpherical(spherical))
            controls.update()
            render()
          }
          actions.current = {
            reset: () => {
              controls.reset()
              render()
            },
            zoom: (factor) => {
              const offset = camera.position.clone().sub(controls.target)
              offset.setLength(
                Math.max(
                  controls.minDistance,
                  Math.min(controls.maxDistance, offset.length() * factor),
                ),
              )
              camera.position.copy(controls.target).add(offset)
              controls.update()
              render()
            },
            rotate,
          }
          const contextLost = (event: Event) => {
            event.preventDefault()
            setState('failed')
            setFailure('3D 图形上下文已中断，请切换二维地图或重新打开本页。')
          }
          renderer.domElement.addEventListener('webglcontextlost', contextLost)
          dispose.push(() =>
            renderer.domElement.removeEventListener('webglcontextlost', contextLost),
          )
          setState('ready')
          render()
        } catch (error) {
          cleanup()
          setState('failed')
          setFailure(
            error instanceof Error ? error.message : '当前设备暂时无法显示 WebGL 三维地形。',
          )
        }
      })
      .catch(() => {
        if (!canceled) {
          setState('failed')
          setFailure('无法加载三维组件，请使用二维地图查看真实点位和航路。')
        }
      })
    return () => {
      canceled = true
      cleanup()
    }
  }, [surface, scenario, plan, exaggeration, wireframe, trajectories])
  return (
    <div className="terrain-scene-stage">
      <div
        ref={host}
        className="terrain-scene-canvas"
        tabIndex={0}
        role="img"
        aria-label="真实DEM三维地形。方向键旋转，+和-缩放，Home重置；完整地图可在二维地图中访问。"
        onKeyDown={(event) => {
          const a = actions.current
          if (!a) return
          if (
            ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', '+', '=', '-', 'Home'].includes(
              event.key,
            )
          )
            event.preventDefault()
          if (event.key === 'ArrowLeft') a.rotate(-0.12)
          if (event.key === 'ArrowRight') a.rotate(0.12)
          if (event.key === 'ArrowUp') a.rotate(0, -0.1)
          if (event.key === 'ArrowDown') a.rotate(0, 0.1)
          if (['+', '='].includes(event.key)) a.zoom(0.85)
          if (event.key === '-') a.zoom(1.17)
          if (event.key === 'Home') a.reset()
        }}
      />
      {state === 'loading' && (
        <div className="terrain-scene-overlay" role="status">
          <LoaderCircle size={24} className="spin" />
          <strong>构建真实高程曲面</strong>
          <span>按需加载三维组件 · 不请求外部地图</span>
        </div>
      )}
      {state === 'failed' && (
        <div className="terrain-scene-overlay terrain-scene-failure" role="status">
          <TriangleAlert size={25} />
          <strong>三维展示暂不可用</strong>
          <span>{failure}</span>
          <span>二维地图与全部分析数据仍可使用。</span>
        </div>
      )}
      <div className="terrain-scene-tools" aria-label="三维地形视角控制">
        <button
          disabled={state !== 'ready'}
          aria-label="放大三维地形"
          title="放大"
          onClick={() => actions.current?.zoom(0.82)}
        >
          <ZoomIn size={16} />
        </button>
        <button
          disabled={state !== 'ready'}
          aria-label="缩小三维地形"
          title="缩小"
          onClick={() => actions.current?.zoom(1.22)}
        >
          <ZoomOut size={16} />
        </button>
        <button
          disabled={state !== 'ready'}
          aria-label="重置三维地形视角"
          title="重置视角"
          onClick={() => actions.current?.reset()}
        >
          <RotateCcw size={16} />
        </button>
      </div>
      <div className="terrain-scene-orientation">
        <span>3D</span>
        <i />
        <small>WGS84 · DEM</small>
      </div>
      <div className="terrain-scene-legend">
        <span>
          <i className="terrain-scene-base" />
          救援基地
        </span>
        <span>
          <i className="terrain-scene-site" />
          需求点
        </span>
        <span>
          <i className="terrain-scene-route" />
          航路地面投影
        </span>
        {!!trajectories.length && (
          <span>
            <i style={{ background: '#a8e8d3' }} />
            模型航迹 · 黄色为升降
          </span>
        )}
      </div>
    </div>
  )
}

export function TerrainScene({ scenario, plan, onOpenMap, selectedSortie }: Props) {
  const terrain = scenario.terrain
  const [exaggeration, setExaggeration] = useState(2)
  const [wireframe, setWireframe] = useState(false)
  const stages = useQuery({
    queryKey: ['stages', plan?.plan_id],
    queryFn: () => ops.stages(plan!.plan_id),
    enabled: !!plan,
  })
  const trajectories = useMemo(
    () =>
      stages.data?.trajectory_segments.filter(
        (s) => s.sortie_id === (selectedSortie || plan?.sorties[0]?.sortie_id),
      ) || [],
    [stages.data, selectedSortie, plan],
  )
  const hasAsset = terrain.status === 'available' && !!terrain.asset_id && !!terrain.sha256
  const surface = useQuery({
    queryKey: ['terrain-surface', terrain.asset_id, terrain.sha256],
    queryFn: () => api.terrainSurface(terrain.asset_id!, terrain.sha256!),
    enabled: hasAsset,
    staleTime: Infinity,
    retry: 1,
  })
  return (
    <section className="terrain-scene" aria-label="真实三维地形分析">
      <div className="terrain-scene-header">
        <div>
          <span className="terrain-scene-eyebrow">真实地形与模型航迹</span>
          <h3>
            <Mountain size={19} />
            山地空间 · 三维推演
          </h3>
        </div>
        <button className="terrain-scene-map-link" onClick={onOpenMap}>
          <Expand size={14} />
          地图与数据
        </button>
      </div>
      {surface.data ? (
        <SurfaceCanvas
          key={`${terrain.asset_id}-${terrain.sha256}`}
          surface={surface.data}
          scenario={scenario}
          plan={plan}
          exaggeration={exaggeration}
          wireframe={wireframe}
          trajectories={trajectories}
        />
      ) : (
        <div className="terrain-scene-empty">
          {surface.isFetching ? (
            <LoaderCircle size={30} className="spin" />
          ) : surface.isError ? (
            <TriangleAlert size={30} />
          ) : (
            <Mountain size={35} />
          )}
          <strong>
            {surface.isFetching
              ? '读取场景绑定的DEM资产'
              : surface.isError
                ? '当前DEM无法读取'
                : '为场景导入真实地形'}
          </strong>
          <p>
            {surface.isError
              ? (surface.error as Error).message
              : '上传GeoTIFF或导入地形资产包，即可旋转查看高程曲面，并与真实需求点、规划航路叠加。'}
          </p>
          <button onClick={surface.isError ? () => void surface.refetch() : onOpenMap}>
            {surface.isError ? '重新读取' : '打开地图与地形管理'}
          </button>
        </div>
      )}
      {surface.data && (
        <>
          <div className="terrain-scene-controls">
            <div>
              <Layers3 size={14} />
              <label>
                高程视觉倍率{' '}
                <select
                  aria-label="高程视觉倍率"
                  value={exaggeration}
                  onChange={(event) => setExaggeration(Number(event.target.value))}
                >
                  <option value={1}>1× 原比例</option>
                  <option value={2}>2×</option>
                  <option value={4}>4×</option>
                </select>
              </label>
            </div>
            <label>
              <input
                type="checkbox"
                checked={wireframe}
                onChange={(event) => setWireframe(event.target.checked)}
              />
              网格结构
            </label>
            <span>拖拽旋转 · 滚轮缩放 · 支持键盘</span>
          </div>
          <div className="terrain-scene-facts">
            <div>
              <small>真实高程范围</small>
              <strong>
                {number(surface.data.min_elevation_m)}—{number(surface.data.max_elevation_m)}
                <em>m</em>
              </strong>
            </div>
            <div>
              <small>资产有效覆盖</small>
              <strong>{percent(surface.data.valid_fraction)}</strong>
            </div>
            <div>
              <small>显示采样网格</small>
              <strong>
                {surface.data.longitude.length} × {surface.data.latitude.length}
              </strong>
            </div>
          </div>
          <p className="terrain-scene-caption">
            {surface.data.notice}{' '}
            淡紫色为航路地面投影；绿色与黄色线显示所选架次的模型巡航和升降，高度来自阶段计算，非实测轨迹。高程倍率只改变画面，不参与计算。NoData保留孔洞。
          </p>
          <p className="terrain-scene-compact-note">
            真实DEM · {surface.data.longitude.length}×{surface.data.latitude.length}展示网格 ·
            NoData留空 · 淡紫投影 / 绿黄模型航迹 · 非实测
          </p>
          <details className="terrain-scene-provenance">
            <summary>查看地形来源与空间范围</summary>
            <p>{surface.data.name}</p>
            <code>
              {surface.data.asset_id} · SHA256 {surface.data.sha256}
            </code>
            <p>
              西 {number(surface.data.bounds[0], 5)}° / 南 {number(surface.data.bounds[1], 5)}° / 东{' '}
              {number(surface.data.bounds[2], 5)}° / 北 {number(surface.data.bounds[3], 5)}°
            </p>
          </details>
        </>
      )}
    </section>
  )
}
