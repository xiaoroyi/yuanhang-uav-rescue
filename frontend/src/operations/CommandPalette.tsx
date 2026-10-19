import { useEffect, useRef, useState } from 'react'
import {
  ArrowUpRight,
  BookOpen,
  Drone,
  FileSpreadsheet,
  FlaskConical,
  Home,
  Layers3,
  ListChecks,
  MapPinned,
  Mountain,
  RadioTower,
  Search,
} from 'lucide-react'
import { Modal } from '../components/ui'
import type { Mission } from '../api/operations'
export function CommandPalette({
  open,
  onOpenChange,
  missions,
  current,
}: {
  open: boolean
  onOpenChange: (v: boolean) => void
  missions: Mission[]
  current?: Mission
}) {
  const [search, setSearch] = useState(''),
    [index, setIndex] = useState(0),
    input = useRef<HTMLInputElement>(null)
  useEffect(() => {
    const listener = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        onOpenChange(!open)
      }
    }
    window.addEventListener('keydown', listener)
    return () => window.removeEventListener('keydown', listener)
  }, [open, onOpenChange])
  const actions = [
    { label: '返回首页', hint: '首页', href: '#/home', icon: Home },
    { label: '救援任务', hint: '所有任务与历史', href: '#/missions', icon: ListChecks },
    { label: '案例与任务档案', hint: '演练初始化与输入复用', href: '#/cases', icon: Layers3 },
    { label: '算法引擎中心', hint: '标准与EOH本地策略', href: '#/engines', icon: FlaskConical },
    { label: '设备与API接入', hint: '模拟适配器与协议', href: '#/integrations', icon: RadioTower },
    { label: '资源中心', hint: '按任务管理资源', href: '#/resources', icon: Layers3 },
    { label: '演练评测', hint: '比较策略与方法', href: '#/experiments', icon: FlaskConical },
    { label: '图文使用指南', hint: '帮助与术语', href: '#/help', icon: BookOpen },
    ...(current
      ? [
          {
            label: '当前任务 · 调度安排',
            hint: current.name,
            href: `#/missions/${current.mission_id}/schedule`,
            icon: FileSpreadsheet,
          },
          {
            label: '当前任务 · 方案地图',
            hint: current.name,
            href: `#/missions/${current.mission_id}/plans`,
            icon: MapPinned,
          },
          {
            label: '当前任务 · 地形与航迹',
            hint: current.name,
            href: `#/missions/${current.mission_id}/terrain`,
            icon: Mountain,
          },
          {
            label: '当前任务 · 通信协同',
            hint: current.name,
            href: `#/missions/${current.mission_id}/communication`,
            icon: RadioTower,
          },
        ]
      : []),
    ...missions
      .filter((m) => m.lifecycle !== 'archived')
      .map((m) => ({
        label: m.name,
        hint: `${m.site_count} 个需求点 · ${m.cargo_count} 箱物资`,
        href: `#/missions/${m.mission_id}/${m.next_action}`,
        icon: Drone,
      })),
  ]
  const rows = actions
    .filter((a) => (a.label + a.hint).toLowerCase().includes(search.toLowerCase()))
    .slice(0, 14)
  const pick = (href: string) => {
    location.hash = href
    onOpenChange(false)
    setSearch('')
    setIndex(0)
  }
  return (
    <Modal
      title="快速导航"
      description="查找功能或救援任务 · Ctrl K 打开 · 方向键选择 · 回车进入"
      open={open}
      onOpenChange={onOpenChange}
    >
      <div
        className="v3-command-palette"
        onKeyDown={(e) => {
          if (e.key === 'ArrowDown') {
            e.preventDefault()
            setIndex((i) => Math.min(rows.length - 1, i + 1))
          }
          if (e.key === 'ArrowUp') {
            e.preventDefault()
            setIndex((i) => Math.max(0, i - 1))
          }
          if (e.key === 'Enter' && rows[index]) {
            e.preventDefault()
            pick(rows[index].href)
          }
        }}
      >
        <label>
          <Search size={19} />
          <input
            ref={input}
            autoFocus
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setIndex(0)
            }}
            placeholder="搜索任务、调度安排、地图…"
            aria-label="搜索功能或任务"
          />
        </label>
        <div role="listbox" aria-label="导航结果">
          {rows.map((a, i) => (
            <button
              key={a.href + '-' + a.label}
              role="option"
              aria-selected={index === i}
              className={index === i ? 'active' : ''}
              onMouseEnter={() => setIndex(i)}
              onClick={() => pick(a.href)}
            >
              <a.icon size={19} />
              <span>
                <b>{a.label}</b>
                <small>{a.hint}</small>
              </span>
              <ArrowUpRight size={14} />
            </button>
          ))}
          {!rows.length && <p>没有匹配的功能或任务，请换个关键词。</p>}
        </div>
      </div>
    </Modal>
  )
}
