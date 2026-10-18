import { useMemo, useState } from 'react'
import {
  Activity,
  ArrowDown,
  ArrowRight,
  BookOpen,
  Check,
  CheckCircle2,
  ChevronDown,
  Compass,
  Database,
  FileCheck2,
  FileJson,
  History,
  Layers3,
  Map,
  Mountain,
  Radio,
  Rocket,
  Search,
  ShieldCheck,
  Sparkles,
  Split,
  Upload,
  Workflow,
  X,
  type LucideIcon,
} from 'lucide-react'
import { Button, Modal } from '../components/ui'
import './guide.css'

export type GuideDestination =
  'workspace' | 'scenario' | 'maps' | 'analysis' | 'history' | 'compare'

type GuideStep = {
  title: string
  subtitle: string
  icon: LucideIcon
  target: GuideDestination
  action: string
  heading: string
  description: string
  tasks: string[]
  result: string
  note: string
}

const STEPS: GuideStep[] = [
  {
    title: '选择你的演练',
    subtitle: '从一套真实小场景开始',
    icon: Compass,
    target: 'workspace',
    action: '进入调度工作台',
    heading: '先用 5 点 32 箱，走完一次完整闭环',
    description:
      '首次使用建议选择小场景观察任务、机体和电池如何协作。熟悉后再切换到原题 15 点 80 箱，或导入自己的场景。',
    tasks: [
      '在场景选择器中确认当前场景，已有历史可以直接打开。',
      '检查场景版本和输入来源；Mock 示例不能当作真实算法结果。',
      '已有方案不等于本次刚刚计算，先核对它绑定的快照。',
    ],
    result: '知道“我现在正在查看哪套输入、哪一版场景”。',
    note: '教程只提供导航，不会替换你的场景，也不会自动启动求解。',
  },
  {
    title: '校准场景输入',
    subtitle: '资源、需求与逐箱库存',
    icon: Database,
    target: 'scenario',
    action: '编辑场景与资源',
    heading: '把需求和实际可用资源说清楚',
    description:
      '需求数量与仓库中每一箱实物分别保存。调度会使用真实箱件重量、体积、兼容机型以及机体、电池的状态。',
    tasks: [
      '用 JSON 导入完整场景，或下载 CSV / XLSX 模板后填写并预览。',
      '检查基地、需求点、物资类型、箱件、机体、电池六类实体。',
      '确认单位：WGS84 经度/纬度、kg、L、m、秒，SOC / SOH 取 0—1。',
    ],
    result: '保存一个经过输入校验的新版本，旧版本仍然保留。',
    note: '增加需求时也要提供对应实物库存；缺失值不能随意用 0 代替。',
  },
  {
    title: '准备空间数据',
    subtitle: '影像看地貌，DEM 算地形',
    icon: Map,
    target: 'maps',
    action: '打开地图与数据',
    heading: '让“看见地面”和“计算地形”各司其职',
    description:
      '卫星底图帮助辨认道路与地貌；GeoTIFF DEM 才提供高程计算。限制区参与绕行。三者不能互相替代。',
    tasks: [
      '在地图与数据中查看或准备 DEM，声明垂直基准并确认高程单位为米。',
      '将准备好的 DEM 绑定到场景，检查点位覆盖与高程来源。',
      '核对限制区与通信资源；修改后重新求解，完整航段才会重新检查。',
    ],
    result: '地图显示与求解采用可追溯的空间数据，历史方案仍绑定原始数据。',
    note: 'HTML 地图通常只是展示页面；是否能提取地理数据，要看它内部实际包含什么。',
  },
  {
    title: '运行真实求解',
    subtitle: '快照 → 任务 → 独立检查',
    icon: Rocket,
    target: 'workspace',
    action: '开始调度',
    heading: '先生成可行解，再有目的地深入优化',
    description:
      '选择时间、能耗或均衡偏好，提交后可观察排队与计算状态。成功结果会返回具体箱件、架次、机体、电池和时间区间。',
    tasks: [
      '先运行快速求解，必要时再使用同快照的深入优化。',
      '打开“调度安排”，查看运输架次、逐箱交付、中继排程；筛选无人机，点击行联动时间轴，并可导出CSV。',
      '打开独立检查结果，核对服务数量、地形/通信模型范围和资源冲突。',
    ],
    result: '得到绑定不可变快照、能够独立复核的真实 Plan。',
    note: 'UNKNOWN 表示本次未找到结论；它不等于已证明无解。模型内可行也不等于实飞认证。',
  },
  {
    title: '比较与诊断',
    subtitle: '同条件比较，分清指标口径',
    icon: Split,
    target: 'compare',
    action: '打开方案比较',
    heading: '看清时间、能耗和资源之间的取舍',
    description:
      '从同一个快照计算不同偏好，再比较总体指标与架次变化。资源分析还可查看充电占用、截止余量和确定性增配试算。',
    tasks: [
      '优先选择同快照、同保障任务和同模型范围的方案进行比较。',
      '结合资源时间轴观察“机体返航”和“电池充满”的不同释放时刻。',
      '查看单点诊断、容量必要下界或资源情景，注意每张图的适用范围。',
    ],
    result: '能解释为什么选这个方案，而不只是挑一个最小数字。',
    note: '新版直接比较最后返航、总能耗，或返航秒数 + 300 × kWh；同分时再减期望延期。硬截止和完整保障始终必选。节能可能更晚送达；折中不是服务区公平。旧方案保留 v1 延期优先语义，三种目标也可能选中相同排程。',
  },
  {
    title: '留存与动态复盘',
    subtitle: '版本、事件、旧新方案一一对应',
    icon: History,
    target: 'history',
    action: '查看历史记录',
    heading: '保留过程，再检查突发变化如何影响计划',
    description:
      '历史记录保存场景版本、求解任务和方案来源。资源故障或紧急插单会创建新版本，再以新快照真实重规划，原方案保留。',
    tasks: [
      '在历史记录中定位场景、计算任务与方案，打开其原始快照。',
      '需要复盘时进入事件复盘，先核对当前事件支持的范围再提交。',
      '确认前查看独立检查；导出 JSON / CSV / GeoJSON 或规划报告留档。',
    ],
    result: '能够回看输入、计算、检查、确认和变更，避免混淆历史与当前。',
    note: '当前事件支持整个场景尚未执行的零时刻。方案确认只做计划审核，动画不写实际交付。',
  },
]

const MAP_FORMATS = [
  {
    id: 'imagery',
    icon: Layers3,
    label: '卫星影像',
    tag: '视觉背景',
    title: '帮助认清真实地貌，不替代物理数据',
    text: '影像瓦片是卫星或航拍图像，用来识别道路、山体和聚落。在线来源需要网络；离线演示需要事先准备且有权使用的本地影像。',
    items: [
      '只切换底图，不应改变求解结果。',
      '瓦片不可用时应保留点位、航线和离线地形。',
      '影像不自动提供高程、禁飞规则或可起降认证。',
    ],
  },
  {
    id: 'dem',
    icon: Mountain,
    label: 'GeoTIFF DEM',
    tag: '计算输入',
    title: '每个像元记录高程，用于净空与通信检查',
    text: '在地图与数据中准备文件，再绑定到场景。当前导入支持单波段、带坐标系的米制 DEM，最大 16 MiB / 200 万像元；完整资产包最大 40 MiB。',
    items: [
      '必须声明高程垂直基准与来源。',
      'NoData 和覆盖外区域不能冒充已通过净空检查。',
      '用完整资产包移交，保持原文件、处理结果和内容 hash 对应。',
    ],
  },
  {
    id: 'html',
    icon: FileJson,
    label: 'HTML / GeoJSON',
    tag: '看内容再使用',
    title: 'HTML 是页面，GeoJSON 才是结构化几何',
    text: '论文中的 HTML 地图可能引用在线瓦片，也可能内嵌边界、点位或绘图结果。页面截图和颜色不能直接当作高程或限制区数据。',
    items: [
      'GeoJSON 适合表达坐标与多边形；求解仍以已保存场景为准。',
      'HTML 内部的数据需核对坐标、来源与语义后再适配。',
      '当前没有“上传任意 HTML 自动建图”的能力。',
    ],
  },
] as const

const INNOVATIONS = [
  {
    icon: Radio,
    tone: 'cyan',
    title: '运输 × 通信协同',
    text: '联合考虑物资运输、通信服务窗口、中继机体与能源组件，检查声明模型下的连续覆盖。',
    boundary: '已实现模型检查；尚无现场无线认证。',
  },
  {
    icon: Activity,
    tone: 'violet',
    title: '机体与电池分离调度',
    text: '分别追踪机体释放、初始补能、返航排队与充电端口，让时间轴对应真实资源占用。',
    boundary: '已实现有限准备/充电容量；未建模起降坪容量。',
  },
  {
    icon: ShieldCheck,
    tone: 'blue',
    title: '结果独立复核',
    text: '从输入重建载荷、能源、箱件唯一性、空间与资源约束，检查不依赖优化器自报成功。',
    boundary: '验证当前输入与模型；不替代飞行安全审批。',
  },
  {
    icon: Workflow,
    tone: 'amber',
    title: '版本化事件重规划',
    text: '资源退出或紧急需求创建新版本，保留父方案，并区分新增安排与原箱件的改派。',
    boundary: '已实现零时刻事件；在途与未来事件尚未支持。',
  },
] as const

const FAQS = [
  {
    id: 'first',
    question: '第一次打开，应该从哪里开始？',
    answer:
      '先在场景选择器选择默认 5 点 32 箱演练，进入调度工作台运行一次快速求解。打开任务表和资源时间轴，再到方案比较查看另一种策略。本教程的六步卡片可以直接跳到对应入口。',
    tags: '新手 首次 入门 使用',
  },
  {
    id: 'history',
    question: '为什么刷新后还能看见方案？历史在哪里？',
    answer:
      '场景、版本、任务和方案保存在本机服务的数据库中，正常重启后保留。历史记录页提供集中入口；历史 Plan 绑定自己的快照，修改当前场景不会重写旧结果。本机账户档案另外保存在浏览器中。',
    tags: '历史 保存 数据 持久化 刷新',
  },
  {
    id: 'compare',
    question: '为什么三种策略结果一样？是不是没有真正计算？',
    answer:
      '三种偏好先遵守相同约束与加权软延期首目标，再比较时间、能耗或均衡目标。有限候选集里可能选出同一解。请核对任务 ID、输入快照和求解日志，不应为了制造差异修改展示数字。',
    tags: '策略 比较 算法 时间 能耗 均衡',
  },
  {
    id: 'maps',
    question: '卫星图、DEM 和论文 HTML 地图能互相替代吗？',
    answer:
      '不能。卫星图提供视觉背景；DEM 提供带空间参考的高程栅格；HTML 是展示页面，可能内嵌或引用地理数据。导入 DEM 后还要绑定到场景并重新求解，才能形成当前版本的地形检查结果。',
    tags: '地图 卫星 地形 DEM html 导入 影像',
  },
  {
    id: 'unknown',
    question: 'UNKNOWN、INFEASIBLE 和检查失败分别是什么意思？',
    answer:
      'UNKNOWN 是有限计算预算内没有找到有效结论；INFEASIBLE 需要相应模型或必要条件给出不可行证据；独立检查失败表示候选结果违反了被检查的条件，不能确认发布。三者不应互相替换。',
    tags: '无解 失败 未知 检查 状态 unknown infeasible',
  },
  {
    id: 'confirm',
    question: '点击“确认方案”会让无人机起飞吗？',
    answer:
      '不会。确认检查当前版本、独立验证与资源预约并保存计划审核结果。地图回放也只是按计划时钟展示，没有飞控指令或实际交付写入。真实执行需要额外接入、遥测与安全流程。',
    tags: '确认 执行 动画 回放 飞行 安全',
  },
  {
    id: 'event',
    question: '可以模拟正在飞行的无人机故障吗？',
    answer:
      '当前支持整个场景尚未执行的零时刻资源退出，以及已有点位新增需求和等量实物库存。事件之后生成新快照并真实重规划。正在飞行、未来时刻事件及临时落点变化需要扩展执行事实模型，目前尚不支持。',
    tags: '事件 故障 重规划 动态 在途 紧急 插单',
  },
  {
    id: 'analysis',
    question: '容量下界、单点诊断、资源试算应该怎么理解？',
    answer:
      '容量必要下界只说明至少需要多少运输架次，不证明实际可行，也不是最少机体数量；单点诊断忽略实际机队、充电和时间约束；资源情景会创建独立输入重新求解，确定性压力试算不代表概率。',
    tags: '分析 图表 下界 单点 试算 资源 增配',
  },
]

const INPUT_CHECKS = [
  '基地与需求点坐标',
  '物资类型与逐箱库存',
  '机体型号与可用状态',
  '电池 SOC / SOH',
  '需求数量与截止时间',
  'DEM / 限制区 / 通信范围',
]

export function GuidePage({ onNavigate }: { onNavigate: (target: GuideDestination) => void }) {
  const [step, setStep] = useState(0)
  const [visited, setVisited] = useState<number[]>([0])
  const [mapFormat, setMapFormat] = useState(0)
  const [search, setSearch] = useState('')
  const [expanded, setExpanded] = useState<string | null>('first')
  const [checks, setChecks] = useState<string[]>([])
  const active = STEPS[step]
  const activeFormat = MAP_FORMATS[mapFormat]
  const filteredFaqs = useMemo(() => {
    const query = search.trim().toLocaleLowerCase()
    return FAQS.filter((item) =>
      `${item.question} ${item.answer} ${item.tags}`.toLocaleLowerCase().includes(query),
    )
  }, [search])
  function selectStep(index: number) {
    setStep(index)
    setVisited((old) => (old.includes(index) ? old : [...old, index]))
  }
  return (
    <div className="guide-page">
      <section className="guide-hero" aria-labelledby="guide-title">
        <div className="guide-hero-orbits" aria-hidden="true">
          <i />
          <i />
          <i />
          <span />
          <span />
        </div>
        <div className="guide-hero-copy">
          <span className="guide-kicker">
            <BookOpen size={13} /> YUANHANG FIELD GUIDE <span>使用指南</span>
          </span>
          <h2 id="guide-title">
            从第一箱物资，
            <br />
            到一套有据可查的救援计划。
          </h2>
          <p>选场景、核输入、真实计算、比较复盘。用一条清晰的工作流，掌握运输与通信协同调度。</p>
          <div className="guide-hero-actions">
            <Button variant="primary" onClick={() => onNavigate('workspace')}>
              <Rocket size={15} /> 进入调度工作台 <ArrowRight size={14} />
            </Button>
            <a href="#guide-quickstart" className="guide-hero-link">
              按步骤了解 <ArrowDown size={13} />
            </a>
          </div>
        </div>
        <div className="guide-hero-data" aria-label="指南概览">
          <div>
            <span>START SMALL</span>
            <strong>
              5 点 <em>32 箱</em>
            </strong>
            <p>推荐首次演练规模</p>
          </div>
          <div>
            <span>LEARN THE FLOW</span>
            <strong>
              6 <em>个步骤</em>
            </strong>
            <p>从数据准备到方案留档</p>
          </div>
          <div>
            <span>LOCAL FIRST</span>
            <strong>
              本机 <em>运行</em>
            </strong>
            <p>无需注册 · 数据留存在本机</p>
          </div>
        </div>
      </section>

      <section className="guide-section" id="guide-quickstart" aria-labelledby="guide-start-title">
        <div className="guide-section-heading">
          <div>
            <span className="guide-section-label">01 / QUICK START</span>
            <h3 id="guide-start-title">一条完整的使用路径</h3>
            <p>点击步骤查看操作要点，再直接前往对应页面。</p>
          </div>
          <span className="guide-reading-progress">
            <CheckCircle2 size={14} /> 已浏览 {visited.length} / 6 步
          </span>
        </div>
        <div className="guide-steps-layout">
          <nav className="guide-step-nav" aria-label="快速上手步骤">
            {STEPS.map((item, index) => (
              <button
                key={item.title}
                className={step === index ? 'is-active' : ''}
                onClick={() => selectStep(index)}
                aria-current={step === index ? 'step' : undefined}
              >
                <span className="guide-step-number">
                  {visited.includes(index) && index !== step ? (
                    <Check size={14} />
                  ) : (
                    String(index + 1).padStart(2, '0')
                  )}
                </span>
                <span>
                  <strong>{item.title}</strong>
                  <small>{item.subtitle}</small>
                </span>
                <ArrowRight size={14} />
              </button>
            ))}
          </nav>
          <article className="guide-step-detail" aria-live="polite">
            <div className="guide-step-detail-top">
              <span>
                <active.icon size={21} />
              </span>
              <span>STEP {String(step + 1).padStart(2, '0')} / 06</span>
            </div>
            <h4>{active.heading}</h4>
            <p>{active.description}</p>
            <ol>
              {active.tasks.map((task, index) => (
                <li key={task}>
                  <span>{index + 1}</span>
                  <p>{task}</p>
                </li>
              ))}
            </ol>
            <div className="guide-step-result">
              <FileCheck2 size={17} />
              <p>
                <strong>完成后，你应该得到</strong>
                {active.result}
              </p>
            </div>
            <div className="guide-step-bottom">
              <Button variant="primary" onClick={() => onNavigate(active.target)}>
                {active.action}
                <ArrowRight size={14} />
              </Button>
              {step < STEPS.length - 1 && (
                <button className="guide-text-button" onClick={() => selectStep(step + 1)}>
                  下一步 <ArrowRight size={13} />
                </button>
              )}
            </div>
            <p className="guide-step-note">{active.note}</p>
          </article>
        </div>
      </section>

      <div className="guide-data-layout">
        <section className="guide-section guide-map-section" aria-labelledby="guide-map-title">
          <div className="guide-section-heading">
            <div>
              <span className="guide-section-label">02 / MAP & DATA</span>
              <h3 id="guide-map-title">先分清三种“地图”</h3>
              <p>视觉背景、计算栅格和页面文件，作用各不相同。</p>
            </div>
          </div>
          <div className="guide-format-tabs" role="tablist" aria-label="地图数据类型">
            {MAP_FORMATS.map((format, index) => (
              <button
                key={format.id}
                id={`guide-tab-${format.id}`}
                role="tab"
                aria-selected={mapFormat === index}
                aria-controls="guide-format-panel"
                tabIndex={mapFormat === index ? 0 : -1}
                onClick={() => setMapFormat(index)}
                onKeyDown={(event) => {
                  let next: number
                  if (event.key === 'ArrowRight') next = (index + 1) % MAP_FORMATS.length
                  else if (event.key === 'ArrowLeft')
                    next = (index + MAP_FORMATS.length - 1) % MAP_FORMATS.length
                  else if (event.key === 'Home') next = 0
                  else if (event.key === 'End') next = MAP_FORMATS.length - 1
                  else return
                  event.preventDefault()
                  setMapFormat(next)
                  document.getElementById(`guide-tab-${MAP_FORMATS[next].id}`)?.focus()
                }}
              >
                <format.icon size={15} />
                {format.label}
              </button>
            ))}
          </div>
          <div
            className="guide-format-panel"
            id="guide-format-panel"
            role="tabpanel"
            aria-labelledby={`guide-tab-${activeFormat.id}`}
          >
            <span className="guide-format-tag">{activeFormat.tag}</span>
            <h4>{activeFormat.title}</h4>
            <p>{activeFormat.text}</p>
            <ul>
              {activeFormat.items.map((item) => (
                <li key={item}>
                  <Check size={13} />
                  {item}
                </li>
              ))}
            </ul>
            <button className="guide-text-button" onClick={() => onNavigate('maps')}>
              前往地图与数据 <ArrowRight size={13} />
            </button>
          </div>
        </section>
        <section className="guide-checklist" aria-labelledby="guide-checklist-title">
          <div className="guide-checklist-heading">
            <Upload size={18} />
            <span>INPUT READINESS</span>
            <span>
              {checks.length} / {INPUT_CHECKS.length}
            </span>
          </div>
          <h3 id="guide-checklist-title">带齐这些，再开始。</h3>
          <p>个人自查清单，勾选不会改变场景数据，也不替代系统校验。</p>
          <div>
            {INPUT_CHECKS.map((item) => (
              <label key={item}>
                <input
                  type="checkbox"
                  checked={checks.includes(item)}
                  onChange={(event) =>
                    setChecks((old) =>
                      event.target.checked ? [...old, item] : old.filter((value) => value !== item),
                    )
                  }
                />
                <span>{item}</span>
                <Check size={13} aria-hidden="true" />
              </label>
            ))}
          </div>
          <button onClick={() => onNavigate('scenario')}>
            检查我的场景 <ArrowRight size={14} />
          </button>
        </section>
      </div>

      <section className="guide-section" aria-labelledby="guide-innovation-title">
        <div className="guide-section-heading">
          <div>
            <span className="guide-section-label">03 / INNOVATION & EVIDENCE</span>
            <h3 id="guide-innovation-title">创新设计，看得见也查得到</h3>
            <p>四项核心设计已在当前系统中实现；效果评价与现实认证仍须分别提供证据。</p>
          </div>
          <span className="guide-section-emblem">
            <Sparkles size={19} />
          </span>
        </div>
        <div className="guide-innovations">
          {INNOVATIONS.map((item) => (
            <article key={item.title} className={`guide-innovation guide-innovation-${item.tone}`}>
              <span>
                <item.icon size={20} />
              </span>
              <h4>{item.title}</h4>
              <p>{item.text}</p>
              <small>{item.boundary}</small>
            </article>
          ))}
        </div>
        <div className="guide-evidence-flow">
          <span>
            <Database size={15} /> 不可变输入
          </span>
          <ArrowRight size={14} />
          <span>
            <Rocket size={15} /> 真实求解
          </span>
          <ArrowRight size={14} />
          <span>
            <ShieldCheck size={15} /> 独立检查
          </span>
          <ArrowRight size={14} />
          <span>
            <History size={15} /> 版本留痕
          </span>
          <button onClick={() => onNavigate('analysis')}>
            查看分析 <ArrowRight size={13} />
          </button>
        </div>
      </section>

      <section className="guide-section guide-faq-section" aria-labelledby="guide-faq-title">
        <div className="guide-section-heading">
          <div>
            <span className="guide-section-label">04 / NEED A HAND?</span>
            <h3 id="guide-faq-title">常见问题，直接查。</h3>
            <p>尝试搜索“地图”“历史”“无解”或“比较”。</p>
          </div>
          <div className="guide-search">
            <Search size={16} />
            <input
              aria-label="搜索使用问题"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="搜索使用问题…"
            />
            {search && (
              <button aria-label="清空搜索" onClick={() => setSearch('')}>
                <X size={13} />
              </button>
            )}
          </div>
        </div>
        <div className="guide-faq-list">
          {filteredFaqs.map((item) => (
            <article key={item.id}>
              <h4>
                <button
                  onClick={() => setExpanded(expanded === item.id ? null : item.id)}
                  aria-expanded={expanded === item.id}
                  aria-controls={`guide-faq-${item.id}`}
                >
                  {item.question}
                  <ChevronDown size={17} />
                </button>
              </h4>
              <p id={`guide-faq-${item.id}`} hidden={expanded !== item.id}>
                {item.answer}
              </p>
            </article>
          ))}
          {filteredFaqs.length === 0 && (
            <div className="guide-faq-empty">
              <Search size={23} />
              <strong>没有找到匹配的问题</strong>
              <p>试试更短的关键词，或清空后浏览全部问题。</p>
              <button className="guide-text-button" onClick={() => setSearch('')}>
                查看全部问题 <ArrowRight size={13} />
              </button>
            </div>
          )}
        </div>
      </section>
      <div className="guide-footer">
        <span>
          <ShieldCheck size={14} /> 当前系统用于声明模型下的规划辅助，不发送飞控指令。
        </span>
        <button onClick={() => onNavigate('workspace')}>
          准备好了，开始调度 <ArrowRight size={14} />
        </button>
      </div>
    </div>
  )
}

export function OnboardingWelcome({
  onStart,
  onDismiss,
}: {
  onStart: () => void
  onDismiss: () => void
}) {
  return (
    <Modal
      open
      onOpenChange={(open) => {
        if (!open) onDismiss()
      }}
      title="欢迎来到援航"
      description="运输与通信协同调度，从一套清晰可查的计划开始。"
    >
      <div className="guide-welcome">
        <div className="guide-welcome-art" aria-hidden="true">
          <span />
          <span />
          <Rocket size={36} />
          <i />
          <i />
          <i />
        </div>
        <span className="guide-section-label">YOUR FIRST MISSION</span>
        <h3>
          第一次使用？
          <br />
          先走一遍六步工作流。
        </h3>
        <p>
          了解场景输入、地图数据、真实求解、方案比较和历史复盘。无需注册，不会自动修改当前场景。
        </p>
        <div>
          <Button variant="primary" onClick={onStart}>
            <BookOpen size={15} /> 打开使用指南 <ArrowRight size={14} />
          </Button>
          <Button variant="ghost" onClick={onDismiss}>
            直接进入系统
          </Button>
        </div>
      </div>
    </Modal>
  )
}
