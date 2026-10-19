import { useEffect, useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Crosshair, Layers3, Mountain, Route, ScanLine } from 'lucide-react'
import { api, request, type Scenario, type TerrainMap, type TerrainSurface } from '../api/client'
import { terrainMeshIndices } from '../components/terrain-scene-data'

export function TerrainCommandScene({ animated }: { animated: boolean }) {
  const [layer, setLayer] = useState<'network' | 'terrain'>('network')
  const meta = useQuery({
    queryKey: ['command-terrain'],
    queryFn: () => request<TerrainMap>('/map/terrain'),
    staleTime: Infinity,
  })
  const surface = useQuery({
    queryKey: ['command-surface', meta.data?.sha256],
    queryFn: () => api.terrainSurface(meta.data!.asset_id, meta.data!.sha256),
    enabled: !!meta.data,
    staleTime: Infinity,
  })
  const scenario = useQuery({
    queryKey: ['case-preview', 'mountain-access-v1'],
    queryFn: () => request<Scenario>('/case-library/mountain-access-v1/preview'),
    staleTime: Infinity,
  })
  return (
    <div className="v4-command-scene">
      <div className="v4-scene-header">
        <span>
          <i />
          演练区域 · 镇龙乡
        </span>
        <span>
          <ScanLine size={13} /> WGS84 / DEM
        </span>
      </div>
      {surface.data && scenario.data ? (
        <CommandCanvas
          surface={surface.data}
          scenario={scenario.data}
          animated={animated}
          network={layer === 'network'}
          fallback={meta.data?.image_url}
        />
      ) : (
        <div className="v4-scene-loading">
          <Mountain size={38} />
          <span>
            {surface.isError || scenario.isError
              ? '地形服务连接后显示区域预览'
              : '正在载入本地地形…'}
          </span>
        </div>
      )}
      <div className="v4-scene-tools" aria-label="首页预览图层">
        <button
          aria-pressed={layer === 'network'}
          onClick={() => setLayer('network')}
          title="任务网络示意"
        >
          <Route size={17} />
        </button>
        <button
          aria-pressed={layer === 'terrain'}
          onClick={() => setLayer('terrain')}
          title="只看真实地形"
        >
          <Layers3 size={17} />
        </button>
      </div>
      <div className="v4-scene-compass">
        <Crosshair size={24} />
        <span>N</span>
      </div>
      <div className="v4-scene-bottom">
        <span>
          <i className="base" />
          调度中心 <i className="site" />
          需求点 <i className="relay" />
          任务网络示意
        </span>
        <small>真实DEM · 高度显示×8 · 示意连线不作为调度结果</small>
      </div>
      {surface.data && (
        <div className="v4-elevation-scale">
          <span>海拔</span>
          <i />
          <b>{Math.round(surface.data.max_elevation_m)} m</b>
          <small>{Math.round(surface.data.min_elevation_m)} m</small>
        </div>
      )}
    </div>
  )
}

function CommandCanvas({
  surface,
  scenario,
  animated,
  network,
  fallback,
}: {
  surface: TerrainSurface
  scenario: Scenario
  animated: boolean
  network: boolean
  fallback?: string
}) {
  const host = useRef<HTMLDivElement>(null)
  const labelHost = useRef<HTMLDivElement>(null)
  const [failed, setFailed] = useState(false)
  useEffect(() => {
    const container = host.current,
      labels = labelHost.current
    if (!container || !labels) return
    let canceled = false
    const dispose: Array<() => void> = []
    void import('three')
      .then((T) => {
        if (canceled) return
        try {
          const renderer = new T.WebGLRenderer({
            alpha: true,
            antialias: true,
            powerPreference: 'low-power',
          })
          renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5))
          container.appendChild(renderer.domElement)
          renderer.domElement.setAttribute('aria-hidden', 'true')
          dispose.push(() => {
            renderer.dispose()
            renderer.forceContextLoss()
            renderer.domElement.remove()
          })
          const scene = new T.Scene(),
            group = new T.Group()
          scene.add(group)
          const resources: Array<{ dispose(): void }> = []
          dispose.push(() => resources.forEach((r) => r.dispose()))
          const keep = <A extends { dispose(): void }>(value: A): A => {
            resources.push(value)
            return value
          }
          const [west, south, east, north] = surface.bounds
          const lat = (south + north) / 2,
            lonScale = 111320 * Math.cos((lat * Math.PI) / 180)
          const scale = 150 / Math.max((east - west) * lonScale, (north - south) * 111320)
          const floor = surface.min_elevation_m,
            range = Math.max(1, surface.max_elevation_m - floor)
          const point = (lon: number, lat: number, elevation: number) =>
            new T.Vector3(
              (lon - (west + east) / 2) * lonScale * scale,
              (elevation - floor) * scale * 8,
              -(lat - (south + north) / 2) * 111320 * scale,
            )
          const vertices: number[] = [],
            colors: number[] = []
          const color = new T.Color(),
            low = new T.Color('#0b253b'),
            high = new T.Color('#568b9b')
          surface.latitude.forEach((lat, y) =>
            surface.longitude.forEach((lon, x) => {
              const h = surface.elevations_m[y][x]
              const p = point(lon, lat, h ?? floor)
              vertices.push(p.x, p.y, p.z)
              color.copy(low).lerp(high, Math.pow(h == null ? 0 : (h - floor) / range, 0.7))
              colors.push(color.r, color.g, color.b)
            }),
          )
          const geometry = keep(new T.BufferGeometry())
          geometry.setAttribute('position', new T.Float32BufferAttribute(vertices, 3))
          geometry.setAttribute('color', new T.Float32BufferAttribute(colors, 3))
          geometry.setIndex(terrainMeshIndices(surface.elevations_m))
          geometry.computeVertexNormals()
          group.add(
            new T.Mesh(
              geometry,
              keep(
                new T.MeshStandardMaterial({
                  vertexColors: true,
                  roughness: 0.8,
                  metalness: 0.25,
                  side: T.DoubleSide,
                }),
              ),
            ),
          )
          const wire = new T.Mesh(
            geometry,
            keep(
              new T.MeshBasicMaterial({
                color: '#78cde2',
                wireframe: true,
                transparent: true,
                opacity: 0.08,
                depthWrite: false,
              }),
            ),
          )
          wire.position.y = 0.05
          group.add(wire)
          const grid = new T.GridHelper(220, 22, '#2a526c', '#122940')
          keep(grid.geometry)
          keep(grid.material)
          grid.position.y = -1
          group.add(grid)
          scene.add(new T.AmbientLight('#b9dbff', 2.0))
          const light = new T.DirectionalLight('#e0f9ff', 3.1)
          light.position.set(-60, 110, 40)
          scene.add(light)
          const rim = new T.DirectionalLight('#7966fa', 1.7)
          rim.position.set(60, 30, -70)
          scene.add(rim)
          const camera = new T.PerspectiveCamera(37, 1, 0.1, 1000)
          camera.position.set(135, 112, 156)
          camera.lookAt(0, 12, 0)
          const objects = [scenario.base, ...scenario.sites]
          const pointers = objects.map((s, i) => {
            const p = point(s.coordinates[0], s.coordinates[1], s.ground_elevation_m ?? floor)
            const top = p.clone()
            top.y += i === 0 ? 17 : 8
            const tone = i === 0 ? '#72e7d1' : '#a9bcff'
            const line = keep(new T.BufferGeometry().setFromPoints([p, top]))
            group.add(
              new T.Line(
                line,
                keep(new T.LineBasicMaterial({ color: tone, transparent: true, opacity: 0.65 })),
              ),
            )
            const marker = new T.Mesh(
              keep(new T.SphereGeometry(i === 0 ? 1.5 : 1, 12, 12)),
              keep(new T.MeshBasicMaterial({ color: tone })),
            )
            marker.position.copy(top)
            group.add(marker)
            const ring = new T.Mesh(
              keep(new T.RingGeometry(2.2, 2.45, 32)),
              keep(
                new T.MeshBasicMaterial({
                  color: tone,
                  transparent: true,
                  opacity: 0.5,
                  side: T.DoubleSide,
                }),
              ),
            )
            ring.rotation.x = -Math.PI / 2
            ring.position.copy(top)
            group.add(ring)
            const label = document.createElement('span')
            label.className = i === 0 ? 'v4-map-label base' : 'v4-map-label'
            label.textContent = i === 0 ? '调度中心' : s.name || `需求点 ${i}`
            label.title = s.name
            labels.appendChild(label)
            dispose.push(() => label.remove())
            return { position: top, label, ring }
          })
          const leaders = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
          leaders.setAttribute('class', 'v4-map-leaders')
          labels.prepend(leaders)
          const leaderLines = pointers.map(() => {
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line')
            leaders.appendChild(line)
            return line
          })
          dispose.push(() => leaders.remove())
          const moving: Array<{
            mesh: InstanceType<typeof T.Mesh>
            curve: InstanceType<typeof T.CatmullRomCurve3>
            offset: number
          }> = []
          if (network)
            pointers.slice(1).forEach((p, i) => {
              const a = pointers[0].position,
                b = p.position
              const middle = a.clone().add(b).multiplyScalar(0.5)
              middle.y += 15 + i * 2
              const curve = new T.CatmullRomCurve3([a, middle, b])
              group.add(
                new T.Line(
                  keep(new T.BufferGeometry().setFromPoints(curve.getPoints(80))),
                  keep(
                    new T.LineBasicMaterial({
                      color: i % 2 ? '#a897ff' : '#51d9d1',
                      transparent: true,
                      opacity: 0.65,
                    }),
                  ),
                ),
              )
              const mesh = new T.Mesh(
                keep(new T.SphereGeometry(0.65, 8, 8)),
                keep(new T.MeshBasicMaterial({ color: '#c9fff4' })),
              )
              group.add(mesh)
              moving.push({ mesh, curve, offset: i / 5 })
            })
          let w = 1,
            h = 1,
            visible = true,
            frame = 0,
            last = 0
          const projected = new T.Vector3()
          const draw = (time = 0) => {
            if (canceled) return
            if (time - last > 32 || !animated) {
              last = time
              group.rotation.y = animated ? Math.sin(time / 18000) * 0.06 : 0
              group.updateMatrixWorld()
              const placed: Array<{ x: number; y: number; width: number }> = []
              for (const [index, p] of pointers.entries()) {
                projected.copy(p.position).applyMatrix4(group.matrixWorld).project(camera)
                const px = ((projected.x + 1) * w) / 2,
                  py = ((1 - projected.y) * h) / 2
                const width = Math.min(116, p.label.offsetWidth || 80)
                const x = Math.max(width / 2 + 12, Math.min(w - width / 2 - 12, px))
                const desired = Math.max(70, Math.min(h - 75, py - 29))
                const choices = Array.from({ length: 16 }, (_, step) => [
                  desired - step * 27,
                  desired + step * 27,
                ]).flat()
                const y =
                  choices.find(
                    (candidate) =>
                      candidate >= 70 &&
                      candidate <= h - 70 &&
                      !placed.some(
                        (q) =>
                          Math.abs(q.y - candidate) < 25 &&
                          Math.abs(q.x - x) < (q.width + width) / 2 + 8,
                      ),
                  ) ?? 73 + index * 27
                placed.push({ x, y, width })
                p.label.style.transform = `translate(${x}px,${y}px) translate(-50%,-50%)`
                const line = leaderLines[index]
                line.setAttribute('x1', String(px))
                line.setAttribute('y1', String(py))
                line.setAttribute('x2', String(x))
                line.setAttribute('y2', String(y + 10))
                p.ring.scale.setScalar(animated ? 1 + Math.sin(time / 800) * 0.12 : 1)
              }
              moving.forEach((p) =>
                p.mesh.position.copy(
                  p.curve.getPoint((animated ? time / 11000 + p.offset : p.offset) % 1),
                ),
              )
              renderer.render(scene, camera)
            }
            if (animated && visible && !document.hidden) frame = requestAnimationFrame(draw)
          }
          const resize = new ResizeObserver((entries) => {
            w = entries[0].contentRect.width
            h = entries[0].contentRect.height
            renderer.setSize(w, h)
            camera.aspect = w / Math.max(h, 1)
            camera.updateProjectionMatrix()
            if (!animated) draw()
          })
          resize.observe(container)
          dispose.push(() => resize.disconnect())
          const resume = () => {
            cancelAnimationFrame(frame)
            if (visible && !document.hidden) frame = requestAnimationFrame(draw)
          }
          const observer = new IntersectionObserver((entries) => {
            visible = entries[0].isIntersecting
            resume()
          })
          observer.observe(container)
          document.addEventListener('visibilitychange', resume)
          dispose.push(() => {
            cancelAnimationFrame(frame)
            observer.disconnect()
            document.removeEventListener('visibilitychange', resume)
          })
          frame = requestAnimationFrame(draw)
        } catch {
          if (!canceled) setFailed(true)
        }
      })
      .catch(() => {
        if (!canceled) setFailed(true)
      })
    return () => {
      canceled = true
      dispose.reverse().forEach((fn) => fn())
    }
  }, [surface, scenario, animated, network])
  return (
    <div
      className="v4-command-canvas"
      role="img"
      aria-label="镇龙乡真实DEM地形与演练任务节点，连线为示意"
    >
      <div ref={host} className="v4-gl-host" />
      <div ref={labelHost} className="v4-gl-labels" aria-hidden="true" />
      {failed && (
        <div className="v4-terrain-fallback">
          {fallback && <img src={fallback} alt="镇龙乡DEM晕渲" />}
          <span>二维地形模式</span>
        </div>
      )}
    </div>
  )
}
