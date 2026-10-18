import { useState } from 'react'
import { RadioTower, Settings2 } from 'lucide-react'
import { api, type Communication, type Scenario } from '../api/client'
import { Badge, Button, Modal } from '../components/ui'

export function CommunicationManager({
  scenario,
  onSave,
  notify,
}: {
  scenario: Scenario
  onSave: (s: Scenario) => Promise<void>
  notify: (message: string, error?: boolean) => void
}) {
  const [open, setOpen] = useState(false)
  const [busy, setBusy] = useState(false)
  const [enabled, setEnabled] = useState(scenario.policy.requires_communication)
  const [draft, setDraft] = useState<Communication | null>(scenario.communication || null)
  const [json, setJson] = useState('')
  function update(config: Communication) {
    setDraft(config)
    setJson(JSON.stringify(config, null, 2))
  }
  async function configure() {
    setBusy(true)
    try {
      update(scenario.communication || (await api.communicationTemplate(scenario.scenario_id)))
      setEnabled(scenario.policy.requires_communication)
      setOpen(true)
    } catch (error) {
      notify((error as Error).message, true)
    } finally {
      setBusy(false)
    }
  }
  async function save() {
    if (enabled && scenario.terrain.status !== 'available') {
      notify('请先绑定有效DEM，再开启连续通信检查。', true)
      return
    }
    setBusy(true)
    try {
      const config: Communication = JSON.parse(json)
      await onSave({
        ...scenario,
        communication: config,
        policy: { ...scenario.policy, requires_communication: enabled },
      })
      setOpen(false)
      notify(
        enabled
          ? '连续通信已开启；下一次求解将联合安排运输和中继。'
          : '已保存通信资源，当前仍按运输模式求解。',
      )
    } catch (error) {
      notify((error as Error).message, true)
    } finally {
      setBusy(false)
    }
  }
  return (
    <>
      <section className="panel zone-panel communication-settings">
        <div className="zone-heading">
          <h3>
            <RadioTower size={17} />
            通信与中继
          </h3>
          <Badge tone={scenario.policy.requires_communication ? 'teal' : 'amber'}>
            {scenario.policy.requires_communication ? '联合调度' : '仅运输'}
          </Badge>
        </div>
        <p>
          {scenario.policy.requires_communication
            ? `${scenario.communication?.relay_drones.length || 0}架中继机 · ${scenario.communication?.relay_energy.length || 0}个能源组件`
            : '需要连续通信时，联合安排中继位置、服务时窗与能源组件。'}
        </p>
        <Button busy={busy} onClick={() => void configure()}>
          <Settings2 size={14} />
          配置通信资源
        </Button>
      </section>
      <Modal
        title="连续通信与中继资源"
        description="保存创建新版本；原题链路参数可作为演练起点，不能代替真实无线测量。"
        open={open}
        onOpenChange={setOpen}
        wide
      >
        {draft && (
          <>
            <label className="checkbox-field">
              <input
                type="checkbox"
                checked={enabled}
                onChange={(e) => setEnabled(e.target.checked)}
              />
              要求全程连续通信，启用运输与中继联合调度
            </label>
            <div className="communication-config-summary">
              <RadioTower size={24} />
              <div>
                <strong>网关直连优先 · 单中继双跳</strong>
                <p>覆盖爬升、巡航、下降、交接；中继接入与回传须同时可用。</p>
              </div>
              <Badge tone="teal">离线计算</Badge>
            </div>
            <div className="form-grid">
              <label className="field">
                <span>载波频率 / MHz</span>
                <input
                  type="number"
                  min="1"
                  value={draft.frequency_mhz}
                  onChange={(e) => update({ ...draft, frequency_mhz: Number(e.target.value) })}
                />
              </label>
              <label className="field">
                <span>衰落裕量 / dB</span>
                <input
                  type="number"
                  min="0"
                  value={draft.fading_margin_db}
                  onChange={(e) => update({ ...draft, fading_margin_db: Number(e.target.value) })}
                />
              </label>
              <label className="field">
                <span>网关天线离地高度 / m</span>
                <input
                  type="number"
                  min=".01"
                  value={draft.gateway.antenna_height_m}
                  onChange={(e) =>
                    update({
                      ...draft,
                      gateway: { ...draft.gateway, antenna_height_m: Number(e.target.value) },
                    })
                  }
                />
              </label>
              <label className="field">
                <span>中继最大悬停离地高度 / m</span>
                <input
                  type="number"
                  min="1"
                  value={draft.relay_model.max_agl_m}
                  onChange={(e) =>
                    update({
                      ...draft,
                      relay_model: { ...draft.relay_model, max_agl_m: Number(e.target.value) },
                    })
                  }
                />
              </label>
            </div>
            <h4>实体中继机</h4>
            <div className="relay-inventory-grid">
              {draft.relay_drones.map((row, i) => (
                <label className="relay-inventory-item" key={row.drone_id}>
                  <span>{row.drone_id}</span>
                  <select
                    aria-label={`${row.drone_id}状态`}
                    value={row.status}
                    onChange={(e) =>
                      update({
                        ...draft,
                        relay_drones: draft.relay_drones.map((v, j) =>
                          j === i ? { ...v, status: e.target.value as typeof row.status } : v,
                        ),
                      })
                    }
                  >
                    <option value="available">可用</option>
                    <option value="unavailable">不可用</option>
                  </select>
                </label>
              ))}
            </div>
            <h4>可更换能源组件</h4>
            <div className="relay-inventory-grid">
              {draft.relay_energy.map((row, i) => (
                <label className="relay-inventory-item" key={row.component_id}>
                  <span>{row.component_id}</span>
                  <select
                    aria-label={`${row.component_id}状态`}
                    value={row.status}
                    onChange={(e) =>
                      update({
                        ...draft,
                        relay_energy: draft.relay_energy.map((v, j) =>
                          j === i ? { ...v, status: e.target.value as typeof row.status } : v,
                        ),
                      })
                    }
                  >
                    <option value="available">可用 · {row.capacity_kwh}kWh</option>
                    <option value="charging">充电中</option>
                    <option value="unavailable">不可用</option>
                  </select>
                </label>
              ))}
            </div>
            <p className="callout">
              当前联合模型使用初始满电资源；{draft.candidate_stations.length}
              个有限悬停候选。存在直连缺口且中继不足时会明确报告未找到可验证方案。
            </p>
            <details className="communication-advanced">
              <summary>高级参数与悬停点 JSON</summary>
              <p>可编辑实体、容量、SOC/SOH、功率和候选位置。高级JSON为保存内容，后端会完整校验。</p>
              <textarea
                aria-label="通信参数JSON"
                value={json}
                onChange={(e) => setJson(e.target.value)}
                spellCheck={false}
              />
            </details>
            <div className="dialog-footer">
              <Button onClick={() => setOpen(false)}>取消</Button>
              <Button variant="primary" busy={busy} onClick={() => void save()}>
                保存通信配置
              </Button>
            </div>
          </>
        )}
      </Modal>
    </>
  )
}
