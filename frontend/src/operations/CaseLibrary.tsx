import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Archive,
  ArrowRight,
  ArrowUpRight,
  Boxes,
  CheckCircle2,
  Copy,
  Database,
  ExternalLink,
  FolderOpen,
  Globe2,
  History,
  MapPinned,
  Mountain,
  PackageCheck,
  RadioTower,
  Route,
  Search,
  Wind,
} from 'lucide-react'
import { command, type ExerciseCase } from '../api/command'
import { ops, key, type Mission } from '../api/operations'
import { Button, Empty } from '../components/ui'
import { navigate, stageLabel } from './App'

const categoryNames = {
  all: '全部案例',
  mountain: '山地运输',
  flood: '洪涝补给',
  communication: '通信保障',
  urgent: '多点急送',
}
const icons = { mountain: Mountain, flood: PackageCheck, communication: RadioTower, urgent: Route }
export function CaseLibrary({
  path,
  missions,
  notify,
}: {
  path: string
  missions: Mission[]
  notify: (message: string, error?: boolean) => void
}) {
  const params = new URLSearchParams(path.split('?')[1])
  const [tab, setTab] = useState(params.get('tab') || 'cases')
  const [category, setCategory] = useState(params.get('category') || 'all')
  const [featured, setFeatured] = useState(params.get('case') || '')
  const [search, setSearch] = useState('')
  const [busy, setBusy] = useState('')
  const catalog = useQuery({ queryKey: ['case-library'], queryFn: command.cases, staleTime: 60000 })
  const assets = useQuery({
    queryKey: ['asset-overview'],
    queryFn: command.overview,
    refetchInterval: 10000,
  })
  const query = useQueryClient()
  async function create(c: ExerciseCase) {
    setBusy(c.case_id)
    try {
      const m = await ops.create({
        name: c.name,
        template: c.template,
        case_id: c.case_id,
        idempotency_key: key(),
      })
      await query.invalidateQueries({ queryKey: ['missions'] })
      void query.invalidateQueries({ queryKey: ['asset-overview'] })
      notify('已建立独立演练任务，可直接检查输入并计算。')
      navigate(`missions/${m.mission_id}/prepare`)
    } catch (e) {
      notify((e as Error).message, true)
    } finally {
      setBusy('')
    }
  }
  const rows = missions.filter(
    (m) =>
      (tab !== 'archives' || m.lifecycle === 'archived' || m.lifecycle === 'completed') &&
      m.name.toLowerCase().includes(search.toLowerCase()),
  )
  return (
    <main className="v4-section-page">
      <header className="v4-page-head">
        <div>
          <span>
            <Database size={15} />
            案例与任务资产
          </span>
          <h1>每次演练，都有下一次的价值。</h1>
          <p>
            从有来源的案例建立任务，或复用本机任务输入。方案、快照、事件与执行过程持续保存，演练副本拥有独立的账本。
          </p>
        </div>
        <a className="button" href="#/missions">
          <FolderOpen size={15} />
          打开救援任务
        </a>
      </header>
      <div className="v4-asset-stats">
        {[
          ['内置演练', catalog.data?.cases.length],
          ['本机任务', assets.data?.mission_count],
          ['计算方案', assets.data?.plan_count],
          ['执行记录', assets.data?.execution_count],
        ].map(([label, value]) => (
          <div key={label}>
            <b>{value ?? '—'}</b>
            <span>{label}</span>
          </div>
        ))}
      </div>
      <div className="v4-section-tabs" role="tablist" aria-label="案例与档案分类">
        {[
          { id: 'cases', name: '内置演练案例', icon: MapPinned },
          { id: 'recent', name: '最近任务', icon: History },
          { id: 'archives', name: '历史任务档案', icon: Archive },
          { id: 'sources', name: '数据来源', icon: Globe2 },
        ].map((t) => (
          <button
            key={t.id}
            role="tab"
            aria-selected={tab === t.id}
            className={tab === t.id ? 'active' : ''}
            onClick={() => {
              setTab(t.id)
              navigate(`cases?tab=${t.id}`)
            }}
          >
            <t.icon size={14} /> {t.name}
          </button>
        ))}
      </div>
      {tab === 'cases' ? (
        <>
          <div className="v4-library-toolbar">
            <div>
              {Object.entries(categoryNames).map(([id, name]) => (
                <button
                  key={id}
                  className={category === id ? 'active' : ''}
                  onClick={() => {
                    setCategory(id)
                    setFeatured('')
                  }}
                >
                  {name}
                </button>
              ))}
            </div>
            <span className="v2-subtle">新建副本 · 不带入历史执行</span>
          </div>
          {catalog.error ? (
            <Empty
              icon={<Database size={24} />}
              title="案例服务连接失败"
              description={catalog.error.message}
              action={<Button onClick={() => void catalog.refetch()}>重新连接</Button>}
            />
          ) : (
            <div className={`v4-library-grid ${featured ? 'focused' : ''}`}>
              {catalog.data?.cases
                .filter(
                  (c) =>
                    (!featured || c.case_id === featured) &&
                    (category === 'all' || c.category === category),
                )
                .map((c) => {
                  const Icon = icons[c.category]
                  return (
                    <article className="v4-library-card" key={c.case_id} id={c.case_id}>
                      <div className={`v4-library-art ${c.category}`}>
                        <Icon size={46} strokeWidth={1.2} />
                        <span>{c.subtitle}</span>
                      </div>
                      <div className="v4-library-card-body">
                        <h2>{c.name}</h2>
                        <p>{c.description}</p>
                        <div className="v4-library-tags">
                          {c.learning_goals.map((goal) => (
                            <span key={goal}>{goal}</span>
                          ))}
                        </div>
                        <footer>
                          <span>
                            <Boxes size={13} /> {c.site_count}点 · {c.cargo_count}箱 · v{c.version}
                          </span>
                          <Button
                            variant="primary"
                            busy={busy === c.case_id}
                            disabled={!!busy}
                            onClick={() => void create(c)}
                          >
                            使用此案例
                            <ArrowRight size={14} />
                          </Button>
                        </footer>
                        <div className="v4-source-note">
                          {c.data_statement}
                          <br />
                          来源：
                          {c.source_ids
                            .map(
                              (id) => catalog.data?.sources.find((s) => s.source_id === id)?.name,
                            )
                            .join(' / ')}
                        </div>
                      </div>
                    </article>
                  )
                })}
            </div>
          )}
        </>
      ) : tab === 'sources' ? (
        <div className="v4-library-grid">
          {catalog.data?.sources.map((s) => {
            const Icon =
              s.kind === 'weather'
                ? Wind
                : s.kind === 'terrain'
                  ? Mountain
                  : s.kind === 'disaster'
                    ? Globe2
                    : Database
            return (
              <article key={s.source_id} className="v4-source-card">
                <h2>
                  <Icon size={19} />
                  {s.name}
                </h2>
                <p>{s.usage}</p>
                <small>{s.license_note}</small>
                {s.url ? (
                  <a href={s.url} target="_blank" rel="noreferrer">
                    阅读来源与许可
                    <ExternalLink size={13} />
                  </a>
                ) : (
                  <a href="#/resources">
                    查看任务地图与资源
                    <ArrowUpRight size={14} />
                  </a>
                )}
              </article>
            )
          })}
        </div>
      ) : (
        <>
          <div className="v4-library-toolbar">
            <span className="v2-subtle">
              {tab === 'archives'
                ? '已结束或归档任务；复制仅带入输入，不复制交付事实。'
                : '任务自动保存；打开后继续当前阶段。'}
            </span>
            <label>
              <Search size={15} />
              <input
                aria-label="搜索任务资产"
                placeholder="搜索任务名称"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </label>
          </div>
          {rows.length ? (
            <div className="v4-assets-table-wrap">
              <table className="v4-assets-table">
                <thead>
                  <tr>
                    <th>救援任务</th>
                    <th>输入规模</th>
                    <th>当前阶段</th>
                    <th>最近更新</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((m) => (
                    <tr key={m.mission_id}>
                      <td>
                        <b>{m.name}</b>
                        <small>
                          {m.source_case_id ? '从演练案例建立' : '本机任务资产'} ·{' '}
                          {m.mode === 'simulation' ? '仿真演练' : '规划辅助'}
                        </small>
                      </td>
                      <td>
                        {m.site_count}点 / {m.cargo_count}箱
                      </td>
                      <td>{stageLabel[m.lifecycle]}</td>
                      <td>
                        {new Date(m.updated_at).toLocaleString('zh-CN', {
                          month: '2-digit',
                          day: '2-digit',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </td>
                      <td>
                        <a href={`#/missions/${m.mission_id}/${m.next_action}`}>继续任务</a>
                        <a href={`#/missions/${m.mission_id}/schedule`}>调度安排</a>
                        <Button
                          busy={busy === m.mission_id}
                          disabled={!!busy}
                          onClick={async () => {
                            setBusy(m.mission_id)
                            try {
                              const copy = await ops.clone(m)
                              await query.invalidateQueries({ queryKey: ['missions'] })
                              navigate(`missions/${copy.mission_id}/prepare`)
                            } catch (e) {
                              notify((e as Error).message, true)
                            } finally {
                              setBusy('')
                            }
                          }}
                        >
                          <Copy size={13} />
                          复用输入
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <Empty
              icon={<Archive size={25} />}
              title={tab === 'archives' ? '已结束的演练会保留在这里' : '从案例建立第一份任务'}
              description="每个任务关联自己的输入、方案和执行过程，后续可复制输入重新演练。"
              action={
                <Button onClick={() => setTab('cases')}>
                  选择演练案例
                  <ArrowRight size={14} />
                </Button>
              }
            />
          )}
        </>
      )}
      <p className="v4-engine-note">
        <CheckCircle2 size={14} />
        案例提供可计算的演练输入；计算结果由当前求解器重新生成。公开灾情资料是背景依据，不代表系统曾参与实际救援。
      </p>
    </main>
  )
}
