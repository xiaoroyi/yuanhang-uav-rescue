import { useRef, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  ArrowRight,
  CheckCircle2,
  Cpu,
  Download,
  FileCode2,
  GitBranch,
  HardDrive,
  ShieldCheck,
  Sparkles,
  Upload,
} from 'lucide-react'
import { command } from '../api/command'
import { Button, Empty } from '../components/ui'

export function EngineCenter({ notify }: { notify: (message: string, error?: boolean) => void }) {
  const packages = useQuery({ queryKey: ['heuristic-packages'], queryFn: command.engines })
  const file = useRef<HTMLInputElement>(null),
    query = useQueryClient()
  const [busy, setBusy] = useState(false)
  return (
    <main className="v4-section-page">
      <header className="v4-page-head">
        <div>
          <span>
            <Cpu size={15} />
            调度引擎中心
          </span>
          <h1>离线沉淀策略，在线专注决策。</h1>
          <p>
            标准引擎默认可用。EOH增强选择本地评分包，不在生成任务时调用大模型。两种引擎共享物理约束、资源分配和独立检查。
          </p>
        </div>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          <Button busy={busy} onClick={() => file.current?.click()}>
            <Upload size={14} />
            导入离线策略
          </Button>
          <a className="button" href="#/missions">
            选择任务计算
            <ArrowRight size={14} />
          </a>
          <input
            ref={file}
            hidden
            type="file"
            accept=".json,application/json"
            aria-label="导入本地策略包"
            onChange={async (e) => {
              const input = e.currentTarget,
                selected = input.files?.[0]
              if (!selected) return
              setBusy(true)
              try {
                const policy = await command.importPolicy(selected)
                await query.invalidateQueries({ queryKey: ['heuristic-packages'] })
                notify(`策略“${policy.name}”已保存；可在方案规划中选择。`)
              } catch (error) {
                notify((error as Error).message, true)
              } finally {
                setBusy(false)
                input.value = ''
              }
            }}
          />
        </div>
      </header>
      <div className="v4-engine-summary">
        <article>
          <GitBranch size={28} />
          <h2>标准调度</h2>
          <p>
            人工设计的多起点插入启发式，结合有限候选约束优化。直接按目标比较真实方案，保留完整模型验算。
          </p>
          <footer>
            <CheckCircle2 size={14} />
            默认引擎 · 本机运行
          </footer>
        </article>
        <article>
          <Sparkles size={28} />
          <h2>EOH 增强</h2>
          <p>
            对可行候选应用离线评分函数，调整搜索顺序。策略版本、来源、内容指纹及实际调用次数随方案保存，可用同一输入比较效果。
          </p>
          <footer>
            <HardDrive size={14} />
            本地策略包 · 在线零模型请求
          </footer>
        </article>
      </div>
      <h2 style={{ marginBottom: 18 }}>本地策略库</h2>
      {packages.error ? (
        <Empty
          icon={<Cpu size={24} />}
          title="策略库读取失败"
          description={packages.error.message}
        />
      ) : (
        packages.data?.map((p) => (
          <article key={p.policy_id} className="v4-policy-card">
            <a
              className="button"
              style={{ float: 'right' }}
              href={`/api/v1/heuristic-packages/${encodeURIComponent(p.policy_id)}/export`}
              download
            >
              <Download size={13} />
              导出策略
            </a>
            <h3>
              {p.name} <small>v{p.version}</small>
            </h3>
            <p>{p.description}</p>
            <dl>
              <dt>策略来源</dt>
              <dd>
                {p.origin === 'rule_initialization'
                  ? '规则初始化 · 人工设计评分'
                  : 'EOH离线导入 · 实验记录由产物提供者声明'}
              </dd>
              <dt>部署方式</dt>
              <dd>本机标量评分 · 无网络调用</dd>
              <dt>内容指纹</dt>
              <dd>
                <code>{p.sha256}</code>
              </dd>
              <dt>进化实验记录</dt>
              <dd>
                {p.evolution_record
                  ? '策略包附带记录，请结合对应实验材料审阅'
                  : '本包为规则初始化；不作为LLM进化实验成果'}
              </dd>
            </dl>
          </article>
        ))
      )}
      <section className="v4-policy-card">
        <h3>
          <FileCode2 size={18} /> 离线进化工作流
        </h3>
        <p>
          离线使用 EoH 官方的 LLMConfig / EoH / BaseProblem
          接口设计评分函数，经任务集评估后发布本地包。在线系统只读取通过格式与数值检查的表达式，模型密钥从环境变量读取，不写入项目或浏览器。
        </p>
        <div className="v4-engine-pipeline">
          <span>离线设计</span>
          <ArrowRight size={13} />
          <span>基准求解</span>
          <ArrowRight size={13} />
          <span>保存策略</span>
          <ArrowRight size={13} />
          <span>在线比较</span>
        </div>
        <p style={{ marginTop: 18 }}>
          开发入口：<code>scripts/eoh_offline.py</code>
          。本轮按预算使用本地规则包；外部模型的离线运行由配置与显式启动控制。
        </p>
        <a className="button" href="/api/v1/integrations/configuration" download>
          <Download size={14} />
          下载接入配置
        </a>
      </section>
      <p className="v4-engine-note">
        <ShieldCheck size={14} />
        增强评分影响搜索路径，不放宽安全约束，也不保证每次优于标准引擎。方案中“评分调用0次”表示本次直接保留基线或采用其他候选来源，比较页保留实际结果。
      </p>
    </main>
  )
}
