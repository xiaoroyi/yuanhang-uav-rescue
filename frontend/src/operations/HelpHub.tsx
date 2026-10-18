import { useEffect, useState } from 'react'
import {
  ArrowRight,
  BatteryCharging,
  BookOpen,
  CheckCircle2,
  ChevronRight,
  CirclePlay,
  ClipboardCheck,
  FileSpreadsheet,
  GraduationCap,
  Info,
  MapPinned,
  PackageCheck,
  RadioTower,
  Route,
  Search,
  ShieldCheck,
  Sparkles,
  Upload,
} from 'lucide-react'
import type { Mission, MissionCreate } from '../api/operations'
import './help.css'

const chapters = [
  {
    id: 'start',
    title: '第一次使用',
    subtitle: '从示例开始，走完四个阶段',
    icon: GraduationCap,
    image: 'prepare',
    route: 'prepare',
    steps: [
      [
        '创建一份独立任务',
        '点击“创建入门演练”，系统复制 5 个需求点和 32 箱物资。示例不是当前救援实况，可在准备中自由调整。',
      ],
      [
        '看懂任务的四个阶段',
        '顶部依次是任务准备、方案规划、执行跟踪、复盘分析。完成检查后出现完成标记；随时可返回核对。',
      ],
      [
        '先检查，再计算',
        '在任务准备的“条件检查”运行检查。绿色表示本项通过；阻断项必须处理，未知项仍需了解它的影响。',
      ],
    ],
  },
  {
    id: 'inputs',
    title: '准备与数据导入',
    subtitle: '地图、实物库存和资源要分别核对',
    icon: Upload,
    image: 'prepare',
    route: 'prepare',
    steps: [
      [
        '设置区域与调度中心',
        '填写基地经纬度和地面高程。可切换在线卫星图定位，但卫星照片本身不提供可用于净空计算的高程。',
      ],
      [
        '导入需求和实物箱件',
        '使用导入模板上传 JSON、CSV 或 Excel，预览后保存。需求代表“需要多少”，逐箱库存代表“实际有什么”，不能只填其中一个。',
      ],
      [
        '绑定地形，核对机队与保障',
        '选择真实 DEM 或上传 GeoTIFF/完整资产包，声明米制高程和参考面。运输机体、电池、中继机体和中继能源分开配置。',
      ],
    ],
  },
  {
    id: 'plans',
    title: '方案与安排表',
    subtitle: '看清怎么运，为什么这样安排',
    icon: FileSpreadsheet,
    image: 'schedule',
    route: 'schedule',
    steps: [
      [
        '选择偏好并生成方案',
        '时间、能耗和折中偏好使用同一组输入。计算进度显示实际环节；没有可行结果时，查看诊断而不是重复点击。',
      ],
      [
        '先看独立调度安排页',
        '在“方案规划 → 调度安排”查看运输架次、逐箱交付、中继安排、通信窗口和资源占用。可搜索、筛选并下载整本 Excel。',
      ],
      [
        '把表格与地图、地形对照',
        '点击架次可联动。地形页解释升降、净空与爬升能耗；通信页解释连接来源。确认方案建立计划预约，并不会启动执行。',
      ],
    ],
  },
  {
    id: 'execution',
    title: '执行与中途变化',
    subtitle: '在模拟账本中观察运输并比较修复',
    icon: Route,
    image: 'execution',
    route: 'execute',
    steps: [
      [
        '检查并创建模拟实例',
        '先确认可行方案，再到执行跟踪创建独立模拟实例。点击开始演练后，服务器时钟推进；刷新会恢复状态。',
      ],
      [
        '查看每架无人机和物资进度',
        '地图监控可定位机体，机队运输看板显示目的地、已交付、后续任务和模型速度。提高倍速只加快模拟时钟，不改变物理速度。',
      ],
      [
        '暂停、上报变化、比较并采纳',
        '暂停后记录故障或需求变化，查看受影响架次，生成调整，再核对差异并确认采纳。已交付、已装载、在途承诺不能清空重来。',
      ],
    ],
  },
  {
    id: 'analysis',
    title: '分析、评测与复盘',
    subtitle: '区分计划安排、模型结果和交付事实',
    icon: Sparkles,
    image: 'terrain',
    route: 'terrain',
    steps: [
      [
        '逐段核对地形与通信',
        '三维图的淡紫线是地面投影，绿黄线是模型巡航与升降；高程倍率只改变显示。通信空间采样不等于采样点之间连续覆盖。',
      ],
      [
        '做公平的方案比较',
        '只在同一输入快照和相同规则下比较时间、能源与需求保障。三个偏好有时会找到同一解，系统应说明同解，而不是人为制造差异。',
      ],
      [
        '导出并保留复盘证据',
        '方案 Excel 是计划；执行导出保留模拟事实和变更。资源中心按任务保存入口，导入运行档案为只读查看，不创建新的交付事实。',
      ],
    ],
  },
]
const glossary = [
  {
    name: 'DEM / 数字高程模型',
    text: '由网格记录地面高度的数据。用于检查航线越过山地时需要飞多高；卫星照片不能替代 DEM。',
    icon: MapPinned,
  },
  {
    name: '高程与离地高度',
    text: '高程相对于声明的参考面；离地高度是无人机距离当前位置地面的高度。两者不能直接混用。',
    icon: MapPinned,
  },
  {
    name: '净空',
    text: '无人机与沿线地形之间预留的垂直安全距离。巡航高度需越过该段最高地形，再加净空。',
    icon: ShieldCheck,
  },
  {
    name: 'SOC / 剩余电量',
    text: '电池可用电量的比例，100% 为满电。模型估计、已计算阶段端点、真机测量是不同来源。',
    icon: BatteryCharging,
  },
  {
    name: 'SOH / 电池健康度',
    text: '电池当前可用容量相对标称容量的比例。健康度降低会减少实际可用能量。',
    icon: BatteryCharging,
  },
  {
    name: '架次与航段',
    text: '架次通常从基地准备出发到返回；一个架次可访问多个点。相邻两个位置之间的一段飞行叫航段。',
    icon: Route,
  },
  {
    name: '机体释放与电池释放',
    text: '无人机返回后完成周转即可再次安排；卸下的电池可能仍在充电。两条时间轴各自检查。',
    icon: BatteryCharging,
  },
  {
    name: '中继接入与回传',
    text: '运输机到空中中继的连接为接入，中继到基地网关的连接为回传。两段都满足条件才可计为保障。',
    icon: RadioTower,
  },
  {
    name: '快照 / Snapshot',
    text: '某次计算输入的不可变副本。历史方案绑定自己的快照，后来修改输入不会改写旧结果。',
    icon: ClipboardCheck,
  },
  {
    name: '硬截止与期望截止',
    text: '硬截止为必须满足的交付时限；期望截止用于比较延误。修改时限后必须重新计算。',
    icon: PackageCheck,
  },
  {
    name: '可行与最优',
    text: '可行表示通过当前模型检查；最优必须说明求解范围。有限候选池内的最优不等于现实中全局最优。',
    icon: CheckCircle2,
  },
  {
    name: '模拟、回放与真实设备',
    text: '模拟写入独立仿真账本；回放只读已有记录；真实设备需要许可和单独适配。本版本不会把模拟当真机。',
    icon: ShieldCheck,
  },
  {
    name: '设备回执 / ACK',
    text: '表示设备或模拟适配器收到指令。服务器受理请求、收到回执、动作真正完成是三个状态；收到回执不等于已经完成任务。',
    icon: RadioTower,
  },
]
export function HelpHub({
  missions,
  onNew,
}: {
  missions: Mission[]
  onNew: (t: NonNullable<MissionCreate['template']>) => void
}) {
  const [active, setActive] = useState('start'),
    [search, setSearch] = useState(''),
    [expanded, setExpanded] = useState(false)
  const openTerms = location.hash.endsWith('/terms')
  useEffect(() => {
    if (openTerms) document.getElementById('v3-glossary')?.scrollIntoView()
  }, [openTerms])
  const chapter = chapters.find((c) => c.id === active) || chapters[0],
    m = missions.find((m) => m.lifecycle !== 'archived')
  const link = (route: string) => (m ? `#/missions/${m.mission_id}/${route}` : '#/missions')
  return (
    <main className="v3-help-page">
      <div className="v3-help-hero">
        <div>
          <span>
            <BookOpen size={15} />
            援航使用指南
          </span>
          <h1>
            从第一箱物资，
            <br />
            到一次完整的救援演练。
          </h1>
          <p>用真实示例看操作，也把地图、调度、能源与通信背后的概念讲清楚。</p>
          <button className="button button-primary" onClick={() => onNew('compact')}>
            <CirclePlay size={16} />
            创建入门演练
            <ArrowRight size={15} />
          </button>
          <a href="#/missions">
            继续已有任务
            <ChevronRight size={14} />
          </a>
        </div>
        <div className="v3-help-flow" aria-label="完整使用流程">
          {[
            { icon: ClipboardCheck, title: '准备输入', n: 1 },
            { icon: Route, title: '核对方案', n: 2 },
            { icon: PackageCheck, title: '模拟执行', n: 3 },
            { icon: FileSpreadsheet, title: '复盘导出', n: 4 },
          ].map((s) => (
            <div key={s.n}>
              <span>
                <s.icon size={23} />
              </span>
              <b>{s.title}</b>
              <small>0{s.n}</small>
            </div>
          ))}
        </div>
      </div>
      <div className="v3-help-layout">
        <aside>
          <h2>操作手册</h2>
          <nav aria-label="帮助章节">
            {chapters.map((c) => (
              <button
                key={c.id}
                onClick={() => setActive(c.id)}
                className={active === c.id ? 'active' : ''}
              >
                <c.icon size={17} />
                <span>{c.title}</span>
                <ChevronRight size={13} />
              </button>
            ))}
          </nav>
          <div className="v3-help-tip">
            <Info size={18} />
            <p>卡住时先看条件检查和错误提示。历史方案可以继续查看，但修改输入后需要重新计算。</p>
            <a href={link('prepare?tab=checks')}>
              前往条件检查
              <ArrowRight size={13} />
            </a>
          </div>
        </aside>
        <article className="v3-help-article">
          <div className="v3-help-chapter-heading">
            <span>
              <chapter.icon size={19} />
            </span>
            <div>
              <h2>{chapter.title}</h2>
              <p>{chapter.subtitle}</p>
            </div>
          </div>
          <button
            className="v3-help-screenshot"
            onClick={() => setExpanded(!expanded)}
            aria-expanded={expanded}
            aria-label="放大或收起操作截图"
          >
            <img
              src={`/help/v3/${chapter.image}.webp`}
              alt={`${chapter.title}：系统实际操作截图`}
              loading="lazy"
              className={expanded ? 'expanded' : ''}
            />
            <span>
              实际案例界面 · 点击{expanded ? '收起' : '放大'}
              <Search size={13} />
            </span>
          </button>
          <div className="v3-help-instructions">
            {chapter.steps.map(([title, text], i) => (
              <section key={title}>
                <span>{i + 1}</span>
                <div>
                  <h3>{title}</h3>
                  <p>{text}</p>
                </div>
              </section>
            ))}
          </div>
          <div className="v3-help-article-action">
            <span>带着指南，回到任务中操作。</span>
            <a className="button button-primary" href={link(chapter.route)}>
              打开对应功能
              <ArrowRight size={14} />
            </a>
          </div>
        </article>
      </div>
      <section className="v3-help-video">
        <div>
          <span className="v3-kicker">
            <CirclePlay size={15} />
            实际系统示例录屏
          </span>
          <h2>跟着一次完整演练走一遍</h2>
          <p>
            准备检查 → 生成方案 → 查看调度安排 →
            启动模拟与机队状态。录屏来自本版本真实案例，不是静态原型。
          </p>
          <div>
            <a href={link('schedule')}>
              调度安排表
              <ArrowRight size={14} />
            </a>
            <a href={link('communication')}>
              通信协同
              <ArrowRight size={14} />
            </a>
          </div>
        </div>
        <video
          controls
          preload="none"
          poster="/help/v3/schedule.webp"
          aria-label="援航真实案例操作示例录屏"
        >
          <source src="/help/v3/walkthrough.webm" type="video/webm" />
          <track
            kind="captions"
            src="/help/v3/walkthrough.vtt"
            srcLang="zh"
            label="中文操作说明"
            default
          />
          浏览器不支持视频播放，请使用上方图文步骤。
        </video>
      </section>
      <section className="v3-glossary" id="v3-glossary">
        <div className="v3-help-glossary-heading">
          <div>
            <span className="v3-kicker">
              <GraduationCap size={15} />
              不用先懂专业术语
            </span>
            <h2>常见概念，换成容易理解的说明</h2>
          </div>
          <label className="v2-search">
            <Search size={15} />
            <input
              aria-label="搜索帮助术语"
              placeholder="搜索：电量、地形、中继…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </label>
        </div>
        <div>
          {glossary
            .filter((g) => (g.name + g.text).toLowerCase().includes(search.toLowerCase()))
            .map((g) => (
              <article key={g.name}>
                <g.icon size={19} />
                <div>
                  <h3>{g.name}</h3>
                  <p>{g.text}</p>
                </div>
              </article>
            ))}
        </div>
      </section>
      <div className="v3-help-credits">
        <span>图文与录屏来自本系统实际案例 · 不含外部界面素材</span>
        <a href="/THIRD_PARTY_NOTICES.txt" target="_blank" rel="noreferrer">
          第三方组件声明
          <ArrowRight size={12} />
        </a>
      </div>
    </main>
  )
}
