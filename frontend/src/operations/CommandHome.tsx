import { useEffect, useRef, useSyncExternalStore, type CSSProperties, type ReactNode } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion, useInView, useSpring, useTransform } from 'motion/react'
import {
  Activity,
  ArrowDown,
  ArrowRight,
  ArrowUpRight,
  BatteryCharging,
  BookOpen,
  Boxes,
  Check,
  CheckCircle2,
  ChevronRight,
  CirclePlay,
  Cpu,
  Database,
  Drone,
  FileSpreadsheet,
  GitBranch,
  Layers3,
  MapPinned,
  Mountain,
  Network,
  PackageCheck,
  Pause,
  Play,
  Plus,
  RadioTower,
  Route,
  ShieldCheck,
  Sparkles,
  Workflow,
} from 'lucide-react'
import type { Mission, MissionCreate } from '../api/operations'
import { command } from '../api/command'
import { TerrainCommandScene } from './TerrainCommandScene'
import './command-home.css'

type Props = {
  missions: Mission[]
  onNew: (template: NonNullable<MissionCreate['template']>) => void
  motionEnabled: boolean
  onMotion: () => void
}
const subscribeReducedMotion = (callback: () => void) => {
  const media = window.matchMedia('(prefers-reduced-motion: reduce)')
  media.addEventListener('change', callback)
  return () => media.removeEventListener('change', callback)
}
function Reveal({
  children,
  className = '',
  active,
}: {
  children: ReactNode
  className?: string
  active: boolean
}) {
  return (
    <motion.div
      className={className}
      initial={false}
      whileInView={active ? { opacity: [0.7, 1], y: [18, 0] } : { opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.12 }}
      transition={{ duration: 0.65 }}
    >
      {children}
    </motion.div>
  )
}
function Metric({
  value,
  label,
  hint,
  animated,
}: {
  value?: number | null
  label: string
  hint: string
  animated: boolean
}) {
  const ref = useRef<HTMLDivElement>(null),
    visible = useInView(ref, { once: true })
  const count = useSpring(0, { stiffness: 80, damping: 24 })
  const displayed = useTransform(count, (n) => Math.round(n).toLocaleString())
  useEffect(() => {
    if (visible && value != null) {
      if (animated) count.set(value)
      else count.jump(value)
    }
  }, [animated, value, visible, count])
  return (
    <div ref={ref} className="v4-home-metric">
      <motion.b
        initial={animated ? { opacity: 0, y: 8 } : false}
        animate={visible ? { opacity: 1, y: 0 } : undefined}
      >
        {value == null ? '—' : animated ? displayed : value.toLocaleString()}
      </motion.b>
      <span>{label}</span>
      <small>{hint}</small>
    </div>
  )
}
const capabilities = [
  {
    icon: Mountain,
    title: '看清地形，再决定航线',
    text: '真实DEM与升降剖面联动，理解每一段高度和能源成本。',
    href: '#/resources',
    link: '管理地图资产',
    tone: 'cyan',
  },
  {
    icon: Network,
    title: '物资与通信，一起安排',
    text: '逐箱运输、机体电池、中继驻点与服务窗口统一核对。',
    href: '#/cases?category=communication',
    link: '进入通信演练',
    tone: 'violet',
  },
  {
    icon: GitBranch,
    title: '情况变了，承诺不重置',
    text: '保留已交付和在途任务，定位影响、修复并比较新旧方案。',
    href: '#/help',
    link: '了解动态调整',
    tone: 'mint',
  },
  {
    icon: Layers3,
    title: '增配多少，让结果说话',
    text: '在相同模型与目标下试算机体、电池和地面保障的改变。',
    href: '#/experiments',
    link: '打开演练评测',
    tone: 'amber',
  },
] as const

export function CommandHome({ missions, onNew, motionEnabled, onMotion }: Props) {
  const reduced = useSyncExternalStore(
      subscribeReducedMotion,
      () => window.matchMedia('(prefers-reduced-motion: reduce)').matches,
      () => true,
    ),
    animated = motionEnabled && !reduced
  const assets = useQuery({
    queryKey: ['asset-overview'],
    queryFn: command.overview,
    refetchInterval: 10000,
  })
  const cases = useQuery({ queryKey: ['case-library'], queryFn: command.cases, staleTime: 60000 })
  const recent = missions.filter((m) => m.lifecycle !== 'archived').slice(0, 3)
  const data = assets.data
  const scroll = (id: string) =>
    document
      .getElementById(id)
      ?.scrollIntoView({ behavior: animated ? 'smooth' : 'instant', block: 'start' })
  return (
    <div className="v4-home" data-animated={animated ? 'true' : 'false'}>
      <header className="v4-home-nav">
        <a className="v4-brand" href="#/home" aria-label="援航首页">
          <span>
            <Drone size={26} strokeWidth={1.5} />
          </span>
          <b>
            援航<small>YUANHANG RESCUE</small>
          </b>
        </a>
        <nav aria-label="首页导航">
          <button onClick={() => scroll('capabilities')}>平台能力</button>
          <button onClick={() => scroll('innovation')}>算法创新</button>
          <a href="#/cases">演练案例</a>
          <a href="#/help">使用指南</a>
        </nav>
        <div className="v4-nav-actions">
          <button
            className="v4-motion-toggle"
            onClick={onMotion}
            aria-label={motionEnabled ? '关闭首页动效' : '开启首页动效'}
            title={motionEnabled ? '关闭动态效果' : '开启动态效果'}
          >
            {animated ? <Pause size={15} /> : <Play size={15} />}
          </button>
          <a className="v4-nav-console" href="#/missions">
            进入工作台 <ArrowUpRight size={15} />
          </a>
        </div>
      </header>
      <section className="v4-hero">
        <div className="v4-hero-grid" aria-hidden="true" />
        <div className="v4-hero-glow" aria-hidden="true" />
        <div className="v4-star-field" aria-hidden="true">
          {Array.from({ length: 32 }, (_, i) => (
            <i
              key={i}
              style={
                {
                  '--x': `${(i * 47.3) % 100}%`,
                  '--y': `${(i * 31.7) % 100}%`,
                  '--d': `${5 + (i % 7)}s`,
                  '--delay': `${-i * 0.8}s`,
                } as CSSProperties
              }
            />
          ))}
        </div>
        <div className="v4-hero-layout v4-container">
          <div className="v4-hero-copy">
            <div className="v4-hero-eyebrow">
              <span>
                <i />
                应急协同 · 本机计算
              </span>
              <b>MISSION INTELLIGENCE</b>
            </div>
            <h1>
              让每一次起飞，
              <br />
              <em>都有更好的安排。</em>
            </h1>
            <h2>面向灾害应急的无人机智能救援调度平台</h2>
            <p>
              从任务准备、方案生成到动态重规划与复盘分析。
              <br className="v4-desktop-break" />
              把地图、物资、机队与通信，连成一条可执行的救援链。
            </p>
            <div className="v4-hero-actions">
              <button className="v4-primary" onClick={() => onNew('blank')}>
                <Plus size={18} />
                新建救援任务
                <ArrowRight size={17} />
              </button>
              <a className="v4-secondary" href="#/cases">
                进入演练案例 <ChevronRight size={16} />
              </a>
            </div>
            <a className="v4-tour-link" href="#/help">
              <CirclePlay size={19} />
              第一次使用？观看系统导览<span>图文 · 实际操作录像</span>
            </a>
            <div className="v4-hero-trust">
              <span>
                <ShieldCheck size={14} />
                独立约束检查
              </span>
              <span>
                <Database size={14} />
                离线可用
              </span>
              <span>
                <Activity size={14} />
                业务仿真模式
              </span>
            </div>
          </div>
          <div className="v4-hero-visual">
            <TerrainCommandScene animated={animated} />
            <div className="v4-visual-note">
              <span>
                <RadioTower size={16} />
                运输 × 能源 × 通信
              </span>
              <b>一张地图，贯通整个任务。</b>
              <a href="#/cases?category=communication" aria-label="打开通信协同案例">
                <ArrowUpRight size={20} />
              </a>
            </div>
          </div>
        </div>
        <div className="v4-hero-foot v4-container">
          <button onClick={() => scroll('capabilities')}>
            <ArrowDown size={14} />
            探索平台能力
          </button>
          <span>
            <i /> LOCAL FIRST<span>/</span>决策可解释<span>/</span>记录可追溯
          </span>
          <b>01 — 04</b>
        </div>
      </section>
      <section className="v4-metrics-band">
        <div className="v4-container">
          <div className="v4-metrics-title">
            <span>工作空间资产</span>
            <b>每次演练，都留下依据。</b>
            <small>{assets.isError ? '服务连接后显示本机记录' : '来自本机数据库 · 自动更新'}</small>
          </div>
          <Metric
            value={data?.mission_count}
            label="任务记录"
            hint="准备与演练任务"
            animated={animated}
          />
          <Metric
            value={data?.plan_count}
            label="计算方案"
            hint="已入库的方案版本"
            animated={animated}
          />
          <Metric
            value={data?.snapshot_count}
            label="输入快照"
            hint="不可变计算依据"
            animated={animated}
          />
          <Metric
            value={data?.execution_count}
            label="执行演练"
            hint="独立模拟账本"
            animated={animated}
          />
        </div>
      </section>
      <section id="capabilities" className="v4-section v4-container">
        <Reveal active={animated} className="v4-section-heading">
          <div>
            <span className="v4-eyebrow">BUILT FOR THE MISSION</span>
            <h2>复杂现场，清晰决策。</h2>
          </div>
          <p>
            从山地运输到临时通信保障，
            <br />
            每一个决策都能回到具体任务与资源。
          </p>
        </Reveal>
        <div className="v4-capability-grid">
          {capabilities.map((item, i) => (
            <Reveal active={animated} key={item.title} className={`v4-capability ${item.tone}`}>
              <div className="v4-capability-top">
                <span>
                  <item.icon size={24} strokeWidth={1.5} />
                </span>
                <small>0{i + 1}</small>
              </div>
              <h3>{item.title}</h3>
              <p>{item.text}</p>
              <a href={item.href}>
                {item.link}
                <ArrowUpRight size={15} />
              </a>
            </Reveal>
          ))}
        </div>
      </section>
      <section className="v4-workflow-section">
        <div className="v4-container">
          <Reveal active={animated} className="v4-section-heading">
            <div>
              <span className="v4-eyebrow">ONE CONTINUOUS WORKFLOW</span>
              <h2>从想定，到可核对的结果。</h2>
            </div>
            <a href="#/help">
              跟随指南走一遍
              <ArrowRight size={16} />
            </a>
          </Reveal>
          <div className="v4-workflow-line">
            {[
              {
                icon: MapPinned,
                title: '准备任务',
                text: '定义区域、物资与机队，先检查计算条件。',
                tags: ['区域地图', '资源检查'],
              },
              {
                icon: Workflow,
                title: '生成方案',
                text: '选择目标与引擎，查看逐箱安排和资源时序。',
                tags: ['真实求解', '方案对比'],
              },
              {
                icon: Drone,
                title: '模拟与调整',
                text: '推进服务器演练，注入事件并采纳修复方案。',
                tags: ['执行跟踪', '动态修复'],
              },
              {
                icon: FileSpreadsheet,
                title: '复盘与导出',
                text: '核对交付、能源与时效，保留过程和结果。',
                tags: ['复盘分析', 'Excel导出'],
              },
            ].map((s, i) => (
              <Reveal key={s.title} active={animated} className="v4-workflow-step">
                <div>
                  <span>
                    <s.icon size={24} />
                  </span>
                  <b>0{i + 1}</b>
                  {i < 3 && <ChevronRight size={18} />}
                </div>
                <h3>{s.title}</h3>
                <p>{s.text}</p>
                <footer>
                  {s.tags.map((t) => (
                    <small key={t}>{t}</small>
                  ))}
                </footer>
              </Reveal>
            ))}
          </div>
        </div>
      </section>
      <section id="innovation" className="v4-section v4-container">
        <Reveal active={animated} className="v4-section-heading">
          <div>
            <span className="v4-eyebrow">INTELLIGENCE WITH EVIDENCE</span>
            <h2>算法创新，落在每一步操作里。</h2>
          </div>
          <p>
            约束、目标与来源分开记录。
            <br />
            算法能力可以展示，也可以核对。
          </p>
        </Reveal>
        <div className="v4-innovation-grid">
          <Reveal active={animated} className="v4-innovation-card v4-eoh-card">
            <div className="v4-card-tag">
              <Cpu size={15} />
              可选增强调度引擎
            </div>
            <div className="v4-engine-orbit" aria-hidden="true">
              <i />
              <i />
              <i />
              <span>
                <Sparkles size={32} />
              </span>
              <b>离线设计</b>
              <em>本地调用</em>
            </div>
            <h3>EOH 离线策略增强</h3>
            <p>
              把启发式评分保存为版本化策略包。生成方案时直接本地运行，让搜索增强与在线模型成本分离。
            </p>
            <div className="v4-engine-pipeline">
              <span>策略包</span>
              <ArrowRight size={13} />
              <span>候选评分</span>
              <ArrowRight size={13} />
              <span>独立验算</span>
            </div>
            <footer>
              <span>当前内置：规则初始化包</span>
              <a href="#/engines">
                查看引擎与来源
                <ArrowUpRight size={15} />
              </a>
            </footer>
          </Reveal>
          <Reveal active={animated} className="v4-innovation-card v4-joint-card">
            <div className="v4-card-tag">
              <RadioTower size={15} />
              运输—中继联合调度
            </div>
            <div className="v4-radio-mini" aria-hidden="true">
              <span>
                <Boxes size={22} />
              </span>
              <i />
              <span>
                <RadioTower size={27} />
              </span>
              <i />
              <span>
                <PackageCheck size={22} />
              </span>
              <b className="ring one" />
              <b className="ring two" />
            </div>
            <h3>物资抵达，链路也在。</h3>
            <p>
              同步分析运输航路、中继驻点、保障窗口与独立能源。可视化通信覆盖，核对每个联合任务。
            </p>
            <a href="#/cases?category=communication">
              运行联合演练
              <ArrowUpRight size={15} />
            </a>
          </Reveal>
          <Reveal active={animated} className="v4-innovation-card v4-repair-card">
            <div className="v4-card-tag">
              <GitBranch size={15} />
              执行承诺保留
            </div>
            <div className="v4-repair-flow" aria-hidden="true">
              <span>
                <Check size={13} />
                已交付
              </span>
              <i />
              <span>
                <Drone size={13} />
                在途保留
              </span>
              <i />
              <span className="repair">修复剩余</span>
            </div>
            <h3>变化发生后，继续往前。</h3>
            <p>沿资源依赖定位影响，保护已完成和不可撤销的安排。先看差异，再确认采用。</p>
            <a href="#/help">
              了解事件处理
              <ArrowUpRight size={15} />
            </a>
          </Reveal>
          <Reveal active={animated} className="v4-innovation-card v4-resource-card">
            <div className="v4-card-tag">
              <BatteryCharging size={15} />
              资源反事实试算
            </div>
            <div className="v4-compare-mini" aria-hidden="true">
              <span>
                现有资源
                <i />
              </span>
              <span>
                增配试算
                <i />
              </span>
              <small>图示 · 实际变化由求解决定</small>
            </div>
            <h3>多一块电池，会怎样？</h3>
            <p>复制同一输入做增配试算，比较真实计算结果。把“应该更好”变成可量化的选择。</p>
            <a href="#/experiments">
              进入评测工作区
              <ArrowUpRight size={15} />
            </a>
          </Reveal>
        </div>
      </section>
      <section className="v4-case-section">
        <div className="v4-container">
          <Reveal active={animated} className="v4-section-heading">
            <div>
              <span className="v4-eyebrow">START FROM A REAL CONTEXT</span>
              <h2>从一个案例，开始你的任务。</h2>
            </div>
            <a href="#/cases">
              打开案例与任务资产
              <ArrowRight size={17} />
            </a>
          </Reveal>
          <div className="v4-home-cases">
            {cases.data?.cases.map((c, i) => {
              const Icon = [Mountain, PackageCheck, RadioTower, Route][i % 4]
              return (
                <a href={`#/cases?case=${c.case_id}`} key={c.case_id}>
                  <div className={`v4-case-art art-${c.category}`}>
                    <Icon size={36} strokeWidth={1.2} />
                    <span>{c.communication ? '协同演练' : `${c.site_count} 个需求点`}</span>
                  </div>
                  <div>
                    <small>{c.subtitle}</small>
                    <h3>{c.name.split(' · ')[0]}</h3>
                    <p>
                      {c.cargo_count}箱物资 · {c.communication ? '含通信保障' : '运输与能源'}
                    </p>
                    <span>
                      查看案例
                      <ArrowUpRight size={15} />
                    </span>
                  </div>
                </a>
              )
            })}
          </div>
          <div className="v4-source-strip">
            <Database size={19} />
            <p>
              <b>有来源的数据，可复用的任务。</b>
              <span>项目原题 · 公开灾情背景 · 地形与气象资料入口 · 本机任务持续归档</span>
            </p>
            <a href="#/cases?tab=sources">
              查看数据来源
              <ArrowUpRight size={15} />
            </a>
          </div>
        </div>
      </section>
      <section className="v4-section v4-container v4-return-section">
        <div>
          <span className="v4-eyebrow">YOUR NEXT MISSION</span>
          <h2>继续推进，或从这里起航。</h2>
          <p>
            任务、方案与演练过程自动保存在本机，
            <br />
            下一次打开，仍能回到同一条任务链。
          </p>
          <button className="v4-primary" onClick={() => onNew('blank')}>
            <Plus size={17} />
            新建救援任务
            <ArrowRight size={16} />
          </button>
        </div>
        <div className="v4-recent-list">
          {recent.length ? (
            recent.map((m) => (
              <a key={m.mission_id} href={`#/missions/${m.mission_id}/${m.next_action}`}>
                <span>
                  <Drone size={21} />
                </span>
                <div>
                  <b>{m.name}</b>
                  <small>
                    {m.site_count}个需求点 · {m.cargo_count}箱物资 ·{' '}
                    {m.mode === 'simulation' ? '模拟演练' : '规划辅助'}
                  </small>
                </div>
                <ArrowUpRight size={17} />
              </a>
            ))
          ) : (
            <a href="#/cases">
              <span>
                <BookOpen size={22} />
              </span>
              <div>
                <b>第一次使用，从内置演练开始</b>
                <small>选择一个案例，建立独立的任务副本</small>
              </div>
              <ArrowRight size={17} />
            </a>
          )}
          <a className="v4-all-missions" href="#/missions">
            查看全部任务
            <ArrowRight size={15} />
          </a>
        </div>
      </section>
      <footer className="v4-home-footer v4-container">
        <a className="v4-brand" href="#/home">
          <Drone size={21} />
          <b>
            援航<small>让救援决策更有依据</small>
          </b>
        </a>
        <div>
          <a href="#/help">使用帮助</a>
          <a href="#/integrations">设备与API</a>
          <a href="#/engines">算法引擎</a>
        </div>
        <span>
          <CheckCircle2 size={13} />
          仿真与业务演练环境
        </span>
      </footer>
    </div>
  )
}
