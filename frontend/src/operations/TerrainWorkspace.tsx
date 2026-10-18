import { useQuery } from '@tanstack/react-query'
import {
  ArrowDown,
  ArrowUp,
  BatteryCharging,
  CheckCircle2,
  Map as MapIcon,
  Mountain,
  Route,
  ShieldCheck,
} from 'lucide-react'
import { api, type Plan, type Scenario } from '../api/client'
import { TerrainScene } from '../components/TerrainScene'
import { Empty } from '../components/ui'
import { StageCharts } from './StageCharts'
import { InfoHint } from './ExperienceUI'
import { number } from '../lib/format'
import { orderedSorties } from '../pages/schedule-data'

export function TerrainWorkspace({
  scenario,
  plan,
  selected,
  onSelect,
  onMap,
}: {
  scenario: Scenario
  plan?: Plan
  selected: string | null
  onSelect: (s: string) => void
  onMap: () => void
}) {
  const flight =
    plan?.sorties.find((r) => r.sortie_id === selected) ||
    (plan ? orderedSorties(plan)[0] : undefined)
  const profile = useQuery({
    queryKey: ['flight-profile', plan?.plan_id, flight?.sortie_id],
    queryFn: () => api.flightProfile(plan!.plan_id, flight!.sortie_id),
    enabled: !!flight && !!plan,
  })
  const p = profile.data
  const names = new Map([scenario.base, ...scenario.sites].map((s) => [s.id, s.name || s.id]))
  return (
    <main className="v3-analysis-page">
      <div className="v3-analysis-heading">
        <div>
          <span className="v3-kicker">
            <Mountain size={14} />
            空间与物理约束
          </span>
          <h2>地形与飞行剖面</h2>
          <p>理解每段航路为什么爬升、飞多高，以及高度变化带来的能源成本。</p>
        </div>
        <label>
          选择运输架次
          <select
            aria-label="地形分析架次"
            value={flight?.sortie_id || ''}
            onChange={(e) => onSelect(e.target.value)}
          >
            {plan &&
              orderedSorties(plan).map((r, i) => (
                <option key={r.sortie_id} value={r.sortie_id}>
                  第 {i + 1} 架次 · {r.drone_id} ·{' '}
                  {r.visits.map((v) => names.get(v.site_id)).join(' → ')}
                </option>
              ))}
          </select>
        </label>
      </div>
      <div className="v3-terrain-layout">
        <TerrainScene
          scenario={scenario}
          plan={plan || null}
          selectedSortie={flight?.sortie_id}
          onOpenMap={onMap}
        />
        <aside className="v3-terrain-summary">
          <div>
            <span className="v3-kicker">
              <Route size={14} />
              所选架次的真实计算
            </span>
            <h3>{flight?.drone_id || '等待方案'}</h3>
            <p>
              {flight
                ? `${names.get(scenario.base.id)} → ${flight.visits.map((v) => names.get(v.site_id)).join(' → ')} → ${names.get(scenario.base.id)}`
                : '生成方案后，查看具体架次的地形、升降与能源。'}
            </p>
          </div>
          {p ? (
            <>
              <div className="v3-profile-metrics">
                {[
                  {
                    icon: Route,
                    label: '总水平航程',
                    value: number(p.total_distance_m / 1000, 2),
                    unit: 'km',
                  },
                  { icon: ArrowUp, label: '累计爬升', value: number(p.total_climb_m), unit: 'm' },
                  {
                    icon: ArrowDown,
                    label: '累计下降',
                    value: number(p.total_descent_m),
                    unit: 'm',
                  },
                  {
                    icon: BatteryCharging,
                    label: '爬升能耗',
                    value: number(p.climb_energy_kwh, 3),
                    unit: 'kWh',
                  },
                ].map((s) => (
                  <div key={s.label}>
                    <s.icon size={17} />
                    <span>
                      {s.label}
                      <b>
                        {s.value}
                        <small>{s.unit}</small>
                      </b>
                    </span>
                  </div>
                ))}
              </div>
              <div className="v3-energy-share">
                <span>
                  飞行能耗构成
                  <InfoHint title="能源模型说明">
                    水平能耗随载荷变化；爬升按势能和效率计算。原题模型中下降不另加能耗，也不计能量回收。交接和地面周转并非此处飞行能耗。
                  </InfoHint>
                </span>
                <div>
                  <i
                    style={{
                      width: `${p.modeled_energy_kwh ? (100 * p.horizontal_energy_kwh) / p.modeled_energy_kwh : 0}%`,
                    }}
                  />
                  <i />
                </div>
                <small>
                  <span>水平 {number(p.horizontal_energy_kwh, 3)} kWh</span>
                  <span>爬升 {number(p.climb_energy_kwh, 3)} kWh</span>
                </small>
              </div>
              <div className="v3-constraint-note">
                <ShieldCheck size={17} />
                <p>
                  {p.legs.every((l) => l.terrain_checked)
                    ? '所有航段已按绑定地形检查'
                    : '部分航段未完成真实地形检查'}
                  <small>
                    图形使用采样网格；净空检查使用原始高程数据。高度基准：
                    {p.vertical_datum || '未声明'}。
                  </small>
                </p>
              </div>
            </>
          ) : profile.error ? (
            <p className="v2-inline-error">{profile.error.message}</p>
          ) : (
            <p className="v2-subtle">
              {profile.isFetching ? '正在读取模型剖面…' : '先生成方案，或选择已有方案。'}
            </p>
          )}
          <button className="button" onClick={onMap}>
            <MapIcon size={14} />
            返回方案地图
          </button>
        </aside>
      </div>
      {plan && flight ? (
        <>
          <div className="v2-card v3-profile-chart">
            <StageCharts plan={plan} selected={flight.sortie_id} />
          </div>
          <section className="v2-card">
            <div className="v2-section-bar">
              <h3>逐航段高度与能源核对</h3>
              <span className="v2-subtle">同一高度基准 · 每次交接后重新爬升</span>
            </div>
            <div className="v2-table-scroll">
              <table className="v2-table">
                <thead>
                  <tr>
                    <th>航段</th>
                    <th>起点作业高度</th>
                    <th>沿线最高地形</th>
                    <th>巡航高度</th>
                    <th>终点作业高度</th>
                    <th>净空要求 / 余量</th>
                    <th>爬升 / 下降</th>
                    <th>载荷</th>
                    <th>能耗</th>
                  </tr>
                </thead>
                <tbody>
                  {p?.legs.map((l, i) => (
                    <tr key={l.leg_index}>
                      <td>
                        <b>第 {i + 1} 段</b>
                        <small>
                          {names.get(l.from_id) || l.from_id} → {names.get(l.to_id) || l.to_id}
                        </small>
                      </td>
                      <td>{number(l.start_work_elevation_m)} m</td>
                      <td>
                        {l.terrain_maximum_m == null
                          ? '未评估'
                          : `${number(l.terrain_maximum_m)} m`}
                      </td>
                      <td>
                        <b>{number(l.cruise_elevation_m)} m</b>
                      </td>
                      <td>{number(l.end_work_elevation_m)} m</td>
                      <td>
                        {number(l.clearance_required_m)} m /{' '}
                        {l.cruise_clearance_margin_m == null
                          ? '未评估'
                          : `${number(l.cruise_clearance_margin_m, 1)} m`}
                      </td>
                      <td>
                        {number(l.climb_m)} / {number(l.descent_m)} m
                      </td>
                      <td>{number(l.payload_kg, 1)} kg</td>
                      <td>{number(l.energy_kwh, 3)} kWh</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      ) : (
        <Empty
          icon={<Mountain size={28} />}
          title="地形可先查看，航迹需要实际方案"
          description="准备好地形和机队后生成方案，就能查看每个架次的升降与净空。"
        />
      )}
      <div className="v3-analysis-explainer">
        <CheckCircle2 size={18} />
        <div>
          <b>如何读这张图</b>
          <p>
            地面高程是海拔参考；作业高度是无人机在基地或交接点的高度；巡航高度需越过整段最高地形并保留净空。三维图的视觉倍率只帮助看清起伏，不改变算法。没有地形数据时，不宣称已验证净空。
          </p>
        </div>
      </div>
    </main>
  )
}
