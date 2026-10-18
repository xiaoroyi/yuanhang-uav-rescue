import {
  Check,
  CheckCircle2,
  ChevronRight,
  CircleHelp,
  ClipboardCheck,
  FileChartColumn,
  LoaderCircle,
  Radio,
  Route,
  Sparkles,
} from 'lucide-react'
import * as Tooltip from '@radix-ui/react-tooltip'
import { motion, useReducedMotion } from 'motion/react'
import type { Mission } from '../api/operations'
import type { Progress, SolveJob } from '../api/client'
import { number } from '../lib/format'

export function InfoHint({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <Tooltip.Provider delayDuration={220}>
      <Tooltip.Root>
        <Tooltip.Trigger asChild>
          <button className="v3-info-hint" aria-label={title} type="button">
            <CircleHelp size={14} />
          </button>
        </Tooltip.Trigger>
        <Tooltip.Portal>
          <Tooltip.Content className="v3-tooltip" sideOffset={8}>
            <strong>{title}</strong>
            <p>{children}</p>
            <Tooltip.Arrow />
          </Tooltip.Content>
        </Tooltip.Portal>
      </Tooltip.Root>
    </Tooltip.Provider>
  )
}
const steps = [
  { id: 'prepare', name: '任务准备', detail: '区域 · 物资 · 机队', icon: ClipboardCheck },
  { id: 'plans', name: '方案规划', detail: '计算 · 核对 · 确认', icon: Route },
  { id: 'execute', name: '执行跟踪', detail: '运输状态 · 变化处理', icon: Radio },
  { id: 'review', name: '复盘分析', detail: '结果分析 · 归档导出', icon: FileChartColumn },
] as const
export function WorkflowNav({
  mission,
  current,
  ready,
}: {
  mission: Mission
  current: string
  ready: boolean
}) {
  const active = ['schedule', 'terrain', 'communication', 'insights'].includes(current)
    ? 'plans'
    : current
  const complete = [ready, !!mission.active_plan_id, mission.lifecycle === 'completed', false]
  return (
    <nav className="v2-stage-tabs v3-workflow" aria-label="任务阶段">
      {steps.map((s, i) => (
        <div key={s.id} className="v3-step-wrap">
          <a
            href={`#/missions/${mission.mission_id}/${s.id}`}
            className={`${active === s.id ? 'active' : ''} ${complete[i] ? 'is-complete' : ''}`}
            aria-current={active === s.id ? 'step' : undefined}
          >
            <span className="v3-step-symbol">
              {complete[i] ? <Check size={18} /> : <s.icon size={19} />}
            </span>
            <span>
              <strong>{s.name}</strong>
              <small>{complete[i] ? '已完成 · 可返回查看' : s.detail}</small>
            </span>
            <span className="v3-step-number">0{i + 1}</span>
          </a>
          {i < 3 && <ChevronRight className="v3-step-arrow" size={16} />}
        </div>
      ))}
    </nav>
  )
}
export function JobProgress({
  job,
  progress,
  onCancel,
}: {
  job?: SolveJob
  progress?: Progress
  onCancel: () => void
}) {
  const reduce = useReducedMotion()
  const verifying = !!progress && /复核|检查|验证|复算/.test(progress.stage)
  const current = !job ? 0 : job.job_state === 'queued' ? 1 : verifying ? 2 : 1
  return (
    <motion.section
      className="v3-job-progress"
      aria-live="polite"
      initial={reduce ? false : { opacity: 0, y: -6 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="v3-job-heading">
        <span className="v3-job-icon">
          <Sparkles size={20} />
        </span>
        <div>
          <strong>
            {!job
              ? '正在检查输入并提交计算'
              : job.job_state === 'queued'
                ? '计算已排队，准备开始'
                : verifying
                  ? '正在独立核对可行方案'
                  : '正在为这次救援安排资源'}
          </strong>
          <small>{progress?.stage || '完成后将自动更新方案，离开或刷新页面不会重复提交。'}</small>
        </div>
        <span className="v3-job-runtime">
          {progress ? `${number(progress.elapsed_s, 1)} 秒` : '提交中'}
          <small>
            {progress ? `${number(progress.candidate_count)} 个已报告候选` : '正在保存输入'}
          </small>
        </span>
        <button onClick={onCancel} disabled={!job} className="v3-quiet-button">
          取消计算
        </button>
      </div>
      <div
        className="v3-job-track"
        role="progressbar"
        aria-label="计算阶段；搜索剩余时间无法精确预估"
      >
        <span className={reduce ? 'still' : ''} />
      </div>
      <div className="v3-job-stages">
        {['输入检查', '调度搜索', '独立复核', '生成结果'].map((s, i) => (
          <span key={s} className={i < current ? 'done' : i === current ? 'active' : ''}>
            {i < current ? (
              <CheckCircle2 size={13} />
            ) : i === current ? (
              <LoaderCircle size={13} className="spin" />
            ) : (
              <i />
            )}
            {s}
          </span>
        ))}
        <InfoHint title="如何理解计算进度">
          这里显示当前计算环节。组合搜索无法准确预估剩余时间；候选数不代表最终可行方案数。
        </InfoHint>
      </div>
    </motion.section>
  )
}
