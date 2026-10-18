import { useId } from 'react'
import { motion, useReducedMotion } from 'motion/react'
import {
  ArrowDown,
  ArrowRight,
  BatteryCharging,
  BookOpen,
  Boxes,
  Check,
  ChevronRight,
  CirclePlay,
  Compass,
  Drone,
  FileSpreadsheet,
  Layers3,
  MapPinned,
  Mountain,
  MoveUpRight,
  PackageCheck,
  RadioTower,
  Route,
  ShieldCheck,
  Sparkles,
  Waves,
  Wind,
} from 'lucide-react'
import type { Mission, MissionCreate } from '../api/operations'
import './landing.css'

type Template = NonNullable<MissionCreate['template']>
type Props = {
  missions: Mission[]
  onNew: (template: Template) => void
  motionEnabled: boolean
  onMotion: () => void
}
const stages = [
  { icon: MapPinned, title: '准备救援任务', text: '区域、需求、机队与条件检查' },
  { icon: Route, title: '生成可执行方案', text: '核对航线、箱件、能源与通信' },
  { icon: Drone, title: '模拟与动态调整', text: '掌握运输进度，比较修复方案' },
  { icon: FileSpreadsheet, title: '复盘与成果导出', text: '追溯交付事实，保存完整安排' },
]

function MissionIllustration({ animated }: { animated: boolean }) {
  const reduce = useReducedMotion(),
    id = useId().replace(/:/g, '')
  const paths = [
    'M125 313L282 199L421 241L574 126',
    'M125 313L323 360L483 323L574 126',
    'M282 199L348 102L574 126',
  ]
  return (
    <div
      className={`v3-mission-art ${animated && !reduce ? 'is-animated' : ''}`}
      aria-label="山地运输与通信协同流程示意，不代表当前任务实况"
    >
      <div className="v3-art-grid" />
      <svg
        viewBox="0 0 700 480"
        className="v3-relief-art"
        role="img"
        aria-label="基地、救援点、运输航线与通信中继的协同示意"
      >
        <defs>
          <linearGradient id={`${id}-land`} x1="0" y1="0" x2="1" y2="1">
            <stop stopColor="#45736c" stopOpacity=".55" />
            <stop offset="1" stopColor="#162f39" stopOpacity=".15" />
          </linearGradient>
          <linearGradient id={`${id}-route`}>
            <stop stopColor="#bce8b6" />
            <stop offset="1" stopColor="#72bfc4" />
          </linearGradient>
          <radialGradient id={`${id}-halo`}>
            <stop stopColor="#7de4ce" stopOpacity=".17" />
            <stop offset="1" stopColor="#7de4ce" stopOpacity="0" />
          </radialGradient>
        </defs>
        <path
          d="M30 280L151 203L220 219L347 62L420 138L501 91L676 217L630 330L388 439L162 403Z"
          fill={`url(#${id}-land)`}
        />
        {Array.from({ length: 15 }, (_, i) => {
          const y = 120 + i * 20
          return (
            <path
              key={i}
              d={`M20 ${y + 100}Q105 ${y + 20} 192 ${y + 65}T340 ${y - 40}Q421 ${y + 65} 500 ${y - 15}T690 ${y + 65}`}
              fill="none"
              stroke="#8cc8b4"
              strokeWidth=".8"
              opacity={0.08 + i * 0.006}
            />
          )
        })}
        {Array.from({ length: 12 }, (_, i) => (
          <path
            key={`l${i}`}
            d={`M${55 + i * 51} 440Q${i * 53} 290 ${i * 58 + 105} 65`}
            fill="none"
            stroke="#a5d4ce"
            strokeWidth=".6"
            opacity=".07"
          />
        ))}
        <path
          d="M50 367Q221 225 339 303T677 270"
          fill="none"
          stroke="#75b9cb"
          strokeWidth="16"
          opacity=".07"
        />
        <path
          d="M50 367Q221 225 339 303T677 270"
          fill="none"
          stroke="#8ac1ce"
          strokeWidth="2"
          opacity=".23"
        />
        <ellipse
          cx="421"
          cy="241"
          rx="154"
          ry="88"
          fill={`url(#${id}-halo)`}
          stroke="#77cbb6"
          strokeDasharray="4 7"
          strokeOpacity=".3"
        />
        <path
          d="M125 313L421 241L574 126M421 241L323 360"
          fill="none"
          stroke="#e3b976"
          strokeWidth="1.5"
          strokeDasharray="4 6"
          opacity=".65"
        />
        {paths.map((d, i) => (
          <g key={d}>
            <path d={d} fill="none" stroke="#70cab7" strokeWidth="9" opacity=".04" />
            <path
              id={`${id}-path${i}`}
              d={d}
              fill="none"
              stroke={`url(#${id}-route)`}
              strokeWidth="1.5"
              opacity=".7"
            />
            <circle r="3" fill="#d6f5c0" className="v3-route-particle">
              <animateMotion dur={`${9 + i * 3}s`} repeatCount="indefinite" path={d} />
            </circle>
          </g>
        ))}
        {[
          [125, 313, '调度中心'],
          [282, 199, '山地救援点'],
          [574, 126, '临时安置点'],
          [323, 360, '物资接收点'],
        ].map(([x, y, label], i) => (
          <g key={String(label)} transform={`translate(${x},${y})`}>
            <ellipse cy="9" rx="18" ry="8" fill="#0d2028" opacity=".5" />
            <circle
              r={i === 0 ? 9 : 6}
              fill={i === 0 ? '#c5e8b4' : '#8ed3c1'}
              stroke="#163b3d"
              strokeWidth="4"
            />
            <circle
              r="17"
              fill="none"
              stroke="#a0e4c7"
              strokeOpacity=".22"
              className="v3-node-pulse"
            />
            <text x="0" y="-24" textAnchor="middle" fill="#e1f0eb" fontSize="12">
              {label}
            </text>
          </g>
        ))}
        <g transform="translate(421,241)">
          <circle r="18" fill="#c5a36d" fillOpacity=".17" stroke="#e3b976" strokeOpacity=".4" />
          <path
            d="M0 -12V7M-8 7H8M-5 -5L-10 -10M5 -5L10 -10M-3 0L-7 -3M3 0L7 -3"
            stroke="#f2cf93"
            strokeWidth="2"
            fill="none"
          />
          <text x="0" y="-31" textAnchor="middle" fill="#eac78d" fontSize="12">
            通信中继
          </text>
        </g>
        <g transform="translate(200,260) rotate(-35)">
          <rect x="-9" y="-4" width="18" height="8" rx="3" fill="#d9eec5" />
          <path
            d="M-9 -4L-15 -10M9 -4L15 -10M-9 4L-15 10M9 4L15 10"
            stroke="#d9eec5"
            strokeWidth="2"
          />
          {[
            [-15, -10],
            [15, -10],
            [-15, 10],
            [15, 10],
          ].map(([x, y], i) => (
            <ellipse key={i} cx={x} cy={y} rx="7" ry="3" fill="none" stroke="#d9eec5" />
          ))}
        </g>
      </svg>
      <div className="v3-art-label">
        <span className="v3-signal" />
        运输与通信协同<span>流程示意</span>
      </div>
      <div className="v3-art-card v3-art-cargo">
        <span>
          <Boxes size={18} />
        </span>
        <div>
          <b>让每一箱物资都有去向</b>
          <small>逐箱分配 · 架次追踪 · 时限核对</small>
        </div>
        <Check size={15} />
      </div>
      <div className="v3-art-card v3-art-relay">
        <span>
          <RadioTower size={18} />
        </span>
        <div>
          <b>航线之外，也安排连接</b>
          <small>中继值守与运输阶段协同</small>
        </div>
      </div>
      <div className="v3-art-legend">
        <span>
          <i />
          运输航线
        </span>
        <span>
          <i />
          通信关联
        </span>
        <span>仅用于解释协同流程</span>
      </div>
    </div>
  )
}

export function LandingHome({ missions, onNew, motionEnabled, onMotion }: Props) {
  const reduce = useReducedMotion(),
    recent = missions.filter((m) => m.lifecycle !== 'archived').slice(0, 3)
  return (
    <div className="v3-landing">
      <header className="v3-home-nav">
        <a href="#/home" className="v3-home-brand">
          <span>
            <Drone size={25} />
          </span>
          <b>
            援航<small>无人机救援协同调度</small>
          </b>
        </a>
        <nav aria-label="首页导航">
          <a href="#v3-capabilities" onClick={e=>{e.preventDefault();document.getElementById('v3-capabilities')?.scrollIntoView({behavior:reduce?'instant':'smooth'})}}>系统能力</a>
          <a
            href="#v3-methods"
            onClick={(e) => {
              e.preventDefault()
              document
                .getElementById('v3-methods')
                ?.scrollIntoView({ behavior: reduce ? 'instant' : 'smooth' })
            }}
          >
            算法与依据
          </a>
          <a href="#/help">使用指南</a>
          <a href="#/missions" className="v3-home-console">
            进入工作台
            <ArrowRight size={15} />
          </a>
        </nav>
      </header>
      <section className="v3-home-hero">
        <div className="v3-hero-glow" />
        <div className="v3-home-container v3-hero-layout">
          <motion.div
            className="v3-hero-copy"
            initial={reduce ? false : { opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="v3-home-eyebrow">
              <span /> 面向灾害应急的运输与通信协同
            </div>
            <h1>
              让救援物资抵达。
              <br />
              <em>让关键连接持续。</em>
            </h1>
            <p>
              把地图、物资、机队和能源连成一套可核对的救援安排。
              <br className="v3-desktop-break" />
              从真实计算到模拟执行，让每一步决策都有依据。
            </p>
            <div className="v3-home-actions">
              <button className="v3-home-primary" onClick={() => onNew('blank')}>
                <Compass size={18} />
                新建救援任务
                <ArrowRight size={17} />
              </button>
              <button className="v3-home-secondary" onClick={() => onNew('compact_joint')}>
                <CirclePlay size={18} />
                体验协同演练
              </button>
            </div>
            <div className="v3-hero-assurances">
              <span>
                <ShieldCheck size={14} />
                独立方案检查
              </span>
              <span>
                <Layers3 size={14} />
                任务与历史隔离
              </span>
              <span>
                <Wind size={14} />
                本机可离线演练
              </span>
            </div>
          </motion.div>
          <MissionIllustration animated={motionEnabled} />
        </div>
        <div className="v3-home-container v3-hero-bottom">
          <span>为山地、道路中断与临时通信保障设计</span>
          <button onClick={onMotion}>{motionEnabled ? '关闭背景动态' : '开启背景动态'}</button>
          <a
            href="#v3-capabilities"
            onClick={(e) => {
              e.preventDefault()
              document
                .getElementById('v3-capabilities')
                ?.scrollIntoView({ behavior: reduce ? 'instant' : 'smooth' })
            }}
          >
            了解系统
            <ArrowDown size={14} />
          </a>
        </div>
      </section>
      <section className="v3-home-case-strip">
        <div className="v3-home-container">
          <div>
            <span>可复现实验案例</span>
            <b>从小规模演练，到原题回归</b>
            <small>每次创建独立任务；下列规模来自内置原题数据。</small>
          </div>
          {[
            { value: '15', unit: '个', label: '需求点位' },
            { value: '80', unit: '箱', label: '逐箱物资' },
            { value: '3', unit: '类', label: '运输机型' },
            { value: '2', unit: '架', label: '中继机体' },
          ].map((s) => (
            <div className="v3-case-stat" key={s.label}>
              <b>
                {s.value}
                <small>{s.unit}</small>
              </b>
              <span>{s.label}</span>
            </div>
          ))}
          <button onClick={() => onNew('contest_joint')}>
            创建原题协同案例
            <MoveUpRight size={17} />
          </button>
        </div>
      </section>
      <section id="v3-capabilities" className="v3-home-section v3-home-container">
        <div className="v3-home-section-heading">
          <div>
            <span>从复杂条件，到清楚的行动</span>
            <h2>一个任务，贯通救援全过程</h2>
          </div>
          <p>
            先核对输入，再理解安排。
            <br />
            关键结果既能在地图上看，也能在表格中逐项检查。
          </p>
        </div>
        <div className="v3-capability-grid">
          <article className="v3-capability-main">
            <div className="v3-feature-icon">
              <MapPinned />
            </div>
            <h3>以地图为中心，理解真实约束</h3>
            <p>
              查看基地、救援点、实际航线和地形剖面。把山地高度、作业高度与航段爬升放回同一空间。
            </p>
            <div className="v3-mini-profile">
              <svg viewBox="0 0 500 135" role="img" aria-label="地形与航迹的说明性剖面">
                <path
                  d="M0 129L0 106L40 83L72 93L121 42L161 62L211 20L252 60L281 48L332 81L373 45L419 77L459 66L500 100V135H0Z"
                  fill="#e1eeea"
                />
                <path
                  d="M0 106L40 83L72 93L121 42L161 62L211 20L252 60L281 48L332 81L373 45L419 77L459 66L500 100"
                  stroke="#76a795"
                  fill="none"
                />
                <path
                  d="M20 103V9H275V56H301V15H480V92"
                  stroke="#087d72"
                  strokeWidth="2"
                  fill="none"
                  strokeDasharray="5 4"
                />
              </svg>
              <span>地形 / 爬升 / 巡航 / 下降 · 示意</span>
            </div>
            <div className="v3-feature-tags">
              <span>
                <Mountain size={12} />
                真实 DEM 分析
              </span>
              <span>
                <Route size={12} />
                阶段时间与高度
              </span>
            </div>
          </article>
          <article>
            <div className="v3-feature-icon">
              <FileSpreadsheet />
            </div>
            <h3>看得懂的调度安排</h3>
            <p>
              哪架无人机、哪块电池、运哪箱物资、何时交付——独立表格逐项说明，并支持整本 Excel 导出。
            </p>
            <div className="v3-mini-table">
              <span>无人机</span>
              <span>任务</span>
              <span>时序</span>
              {[1, 2, 3].map((n) => (
                <div key={n}>
                  <Drone size={14} />
                  <i />
                  <i />
                </div>
              ))}
            </div>
          </article>
          <article>
            <div className="v3-feature-icon">
              <RadioTower />
            </div>
            <h3>运输与通信一起安排</h3>
            <p>不仅规划物资运输，还检查直连、中继接入与回传，在需要的时间安排中继值守。</p>
            <div className="v3-mini-radio">
              <RadioTower size={30} />
              <span />
              <Drone size={24} />
              <span />
              <MapPinned size={23} />
            </div>
          </article>
          <article>
            <div className="v3-feature-icon">
              <BatteryCharging />
            </div>
            <h3>能源与保障一目了然</h3>
            <p>机体占用、电池周转和充电各自成线。显示计算依据，区分模型估计与设备测量。</p>
            <div className="v3-mini-gantt">
              <i />
              <i />
              <i />
              <i />
              <i />
            </div>
          </article>
          <article>
            <div className="v3-feature-icon">
              <PackageCheck />
            </div>
            <h3>变化发生，保留已有成果</h3>
            <p>模拟途中注入故障或需求变化，保留已交付与不可撤销任务，比较修复前后的真实差异。</p>
            <div className="v3-repair-mini">
              <span>
                <Check size={12} />
                保留交付
              </span>
              <ArrowRight size={14} />
              <span>修复余下任务</span>
            </div>
          </article>
        </div>
      </section>
      <section id="v3-methods" className="v3-method-section">
        <div className="v3-home-container">
          <div className="v3-home-section-heading">
            <div>
              <span>算法创新，落实到操作</span>
              <h2>每一个优势，都能找到对应结果</h2>
            </div>
            <a href="#/experiments">
              进入演练评测
              <ArrowRight size={16} />
            </a>
          </div>
          <div className="v3-method-grid">
            {[
              {
                icon: RadioTower,
                title: '运输—中继联合调度',
                tag: '通信协同',
                text: '以运输阶段的通信需求约束中继机体、能源组件和服务窗口；查看保障明细，而不只画覆盖圆。',
              },
              {
                icon: Route,
                title: '保留执行承诺的动态修复',
                tag: '动态决策',
                text: '从执行账本与当前状态生成新快照，保留已交付、已启动任务与资源预约，再比较采纳修复方案。',
              },
              {
                icon: Sparkles,
                title: '用反事实比较资源增配',
                tag: '资源分析',
                text: '改变资源后重新计算，比较返航时间、总能耗与需求保障。明确有限搜索范围，避免把猜测写成收益。',
              },
            ].map((x) => (
              <article key={x.title}>
                <div>
                  <x.icon size={22} />
                  <span>{x.tag}</span>
                </div>
                <h3>{x.title}</h3>
                <p>{x.text}</p>
                <a href="#/help">
                  了解依据与边界
                  <ChevronRight size={14} />
                </a>
              </article>
            ))}
          </div>
          <p className="v3-home-scope">
            <ShieldCheck size={14} />
            当前用于调度研究与服务器业务仿真。真实飞行需要空域许可、实测模型与设备适配；界面不会把模拟数据标成真机实况。
          </p>
        </div>
      </section>
      <section className="v3-home-section v3-home-container">
        <div className="v3-home-section-heading">
          <div>
            <span>第一次使用，也有清楚的下一步</span>
            <h2>四个阶段，把复杂任务逐步做完</h2>
          </div>
          <a href="#/help">
            <BookOpen size={16} />
            图文使用指南
            <ArrowRight size={16} />
          </a>
        </div>
        <div className="v3-home-stages">
          {stages.map((s, i) => (
            <article key={s.title}>
              <span>
                {i + 1}
                <s.icon size={21} />
              </span>
              <h3>{s.title}</h3>
              <p>{s.text}</p>
              {i < 3 && <ChevronRight size={18} />}
            </article>
          ))}
        </div>
        <div className="v3-use-cases">
          {[
            { icon: Mountain, title: '山地道路中断', text: '地形剖面与爬升能源核对' },
            { icon: Waves, title: '灾害应急运输', text: '时限需求与逐箱保障' },
            { icon: RadioTower, title: '临时通信保障', text: '接入、回传与中继周转' },
          ].map((s) => (
            <div key={s.title}>
              <s.icon size={24} />
              <span>
                <b>{s.title}</b>
                <small>{s.text}</small>
              </span>
            </div>
          ))}
        </div>
      </section>
      <section className="v3-home-container v3-home-recent">
        <div>
          <span>继续推进</span>
          <h2>你的救援工作空间</h2>
          <p>
            {recent.length
              ? '任务与方案已保存在本机服务中，随时继续。'
              : '从一个小规模案例开始，体验真实计算和完整流程。'}
          </p>
          <a href="#/missions">
            查看所有救援任务
            <ArrowRight size={15} />
          </a>
        </div>
        <div>
          {recent.length ? (
            recent.map((m) => (
              <a key={m.mission_id} href={`#/missions/${m.mission_id}/${m.next_action}`}>
                <span className="v3-recent-icon">
                  <Drone size={20} />
                </span>
                <span>
                  <b>{m.name}</b>
                  <small>
                    {m.site_count} 个需求点 · {m.cargo_count} 箱物资 ·{' '}
                    {new Date(m.updated_at).toLocaleDateString('zh-CN')}
                  </small>
                </span>
                <ArrowRight size={18} />
              </a>
            ))
          ) : (
            <button onClick={() => onNew('compact')}>
              <span className="v3-recent-icon">
                <CirclePlay size={23} />
              </span>
              <span>
                <b>创建小规模入门案例</b>
                <small>5 个需求点 · 32 箱物资 · 独立演练副本</small>
              </span>
              <ArrowRight size={18} />
            </button>
          )}
        </div>
      </section>
      <footer className="v3-home-footer v3-home-container">
        <span>
          <Drone size={19} />
          援航 · 让救援安排有据可循
        </span>
        <div>
          <a href="#/help">帮助与术语</a>
          <a href="#/settings">设置与接入</a>
          <a href="#/resources">资源中心</a>
        </div>
      </footer>
    </div>
  )
}
