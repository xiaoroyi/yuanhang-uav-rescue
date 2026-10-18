import { RadioTower, Route, ShieldCheck, Unplug } from 'lucide-react'
import type { Plan, Scenario } from '../api/client'
import { CommunicationPanel } from '../components/CommunicationPanel'
import { RescueMap } from '../components/RescueMap'
import { Empty } from '../components/ui'
import { InfoHint } from './ExperienceUI'
import { number } from '../lib/format'
import { RadioCoverageExplorer } from './RadioCoverageExplorer'

export function CommunicationWorkspace({
  scenario,
  plan,
  selected,
  onSelect,
  onPrepare,
}: {
  scenario: Scenario
  plan?: Plan
  selected: string | null
  onSelect: (s: string) => void
  onPrepare: () => void
}) {
  const relay = plan?.relay_sorties || []
  return (
    <main className="v3-analysis-page v3-communication-page">
      <div className="v3-analysis-heading">
        <div>
          <span className="v3-kicker">
            <RadioTower size={14} />
            运输与中继联合调度
          </span>
          <h2>通信协同与保障安排</h2>
          <p>从基地直连到空中中继，查看连接来源、服务时段和能源周转。</p>
        </div>
        <span className="v3-model-status">
          <ShieldCheck size={16} />
          {plan?.communication_report
            ? `模型缺口 ${number(plan.communication_report.coverage_gap_s, 2)} 秒`
            : '等待联合计算'}
        </span>
      </div>
      {!scenario.communication ? (
        <Empty
          icon={<RadioTower size={30} />}
          title="这个任务尚未配置通信协同"
          description="可在任务准备中启用通信配置，或从首页创建“运输＋通信协同”案例，再生成真实联合方案。"
          action={
            <button className="button button-primary" onClick={onPrepare}>
              配置通信资源
            </button>
          }
        />
      ) : !plan?.communication_report ? (
        <Empty
          icon={<Unplug size={30} />}
          title="通信资源已配置，当前方案没有联合通信结果"
          description="请确认通信保障要求已开启，重新生成联合方案。运输方案不会自动获得通信认证。"
        />
      ) : (
        <>
          <div className="v3-communication-overview">
            <div className="v3-communication-map">
              <RescueMap scenario={scenario} plan={plan} selected={selected} onSelect={onSelect} />
            </div>
            <aside>
              <RadioTower size={25} />
              <h3>连接也有完整的资源链</h3>
              <p>
                运输机到中继是“接入”，中继到基地是“回传”。两段链路同时满足模型要求，且处在中继服务窗口内，才能计为保障。
              </p>
              <div className="v3-radio-chain">
                <span>
                  <Route size={18} />
                  运输无人机
                </span>
                <i />
                <span>
                  <RadioTower size={18} />
                  空中中继
                </span>
                <i />
                <span>
                  <ShieldCheck size={18} />
                  基地网关
                </span>
              </div>
              <dl>
                <div>
                  <dt>中继运输安排</dt>
                  <dd>{relay.length} 架次</dd>
                </div>
                <div>
                  <dt>实际参与的中继机体</dt>
                  <dd>{new Set(relay.map((r) => r.drone_id)).size} 架</dd>
                </div>
                <div>
                  <dt>使用的能源组件</dt>
                  <dd>{new Set(relay.map((r) => r.component_id)).size} 套</dd>
                </div>
              </dl>
              <p className="v2-subtle">
                地图与下方窗口表可联动选择运输架次。
                {relay.length === 0 ? '本方案在模型内可由地面网关直接保障，未安排中继。' : ''}
              </p>
              <InfoHint title="覆盖范围为什么不是一个圆">
                真实地形遮挡、飞行高度和双向链路预算会改变可连接区域。此处以保存方案中的连续时间窗口说明保障，距离圈不能代替地形通信验证。后续覆盖面分析按指定高度与时刻计算。
              </InfoHint>
            </aside>
          </div>
          <RadioCoverageExplorer
            plan={plan}
            scenario={scenario}
            selected={selected}
            onSelect={onSelect}
          />
          <CommunicationPanel
            plan={plan}
            scenario={scenario}
            selected={selected}
            onSelect={onSelect}
          />
        </>
      )}
    </main>
  )
}
