import { useState } from 'react'
import { PackagePlus, TriangleAlert } from 'lucide-react'
import type { Event, Scenario } from '../api/client'
import { Button, Modal } from '../components/ui'
import { category, number } from '../lib/format'
export type UrgentPayload = Extract<Event, { event_type: 'demand.added' }>['payload']

export function UrgentDemandForm({
  scenario,
  disabled,
  busy,
  onSubmit,
}: {
  scenario: Scenario
  disabled: boolean
  busy: boolean
  onSubmit: (payload: UrgentPayload, reason: string) => Promise<boolean>
}) {
  const [open, setOpen] = useState(false)
  const [site, setSite] = useState(scenario.sites[0]?.id || '')
  const types = [...new Set(scenario.demands.map((d) => d.cargo_type))]
  const [type, setType] = useState(types.includes('MED') ? 'MED' : types[0] || '')
  const [quantity, setQuantity] = useState(1),
    [mass, setMass] = useState(3),
    [volume, setVolume] = useState(12),
    [priority, setPriority] = useState(5)
  const [expected, setExpected] = useState('90'),
    [hard, setHard] = useState('180')
  const [reason, setReason] = useState('模拟演练：已有点位紧急物资需求')
  const [nonce, setNonce] = useState(() => crypto.randomUUID().slice(0, 12))
  const expectedSeconds = expected === '' ? null : Number(expected) * 60,
    hardSeconds = hard === '' ? null : Number(hard) * 60
  const valid =
    scenario.sites.some((s) => s.id === site) &&
    types.includes(type) &&
    Number.isInteger(quantity) &&
    quantity >= 1 &&
    quantity <= 32 &&
    [mass, volume].every((v) => Number.isFinite(v) && v > 0) &&
    Number.isInteger(priority) &&
    priority >= 1 &&
    priority <= 1000 &&
    [expectedSeconds, hardSeconds].every((v) => v === null || (Number.isFinite(v) && v >= 0)) &&
    (expectedSeconds === null || hardSeconds === null || expectedSeconds <= hardSeconds) &&
    reason.trim().length > 0
  async function submit() {
    if (!valid || disabled || busy) return
    const demandId = 'URG-' + nonce
    const payload: UrgentPayload = {
      demand: {
        demand_id: demandId,
        site_id: site,
        cargo_type: type,
        required_quantity: quantity,
        priority,
        expected_deadline_s: expectedSeconds,
        hard_deadline_s: hardSeconds,
        mandatory: true,
      },
      cargo_items: Array.from({ length: quantity }, (_, i) => ({
        cargo_id: `${demandId}-BOX-${String(i + 1).padStart(2, '0')}`,
        demand_id: demandId,
        type,
        mass_kg: mass,
        volume_l: volume,
        status: 'available',
        location_id: scenario.base.id,
      })),
    }
    if (await onSubmit(payload, reason.trim())) setOpen(false)
  }
  return (
    <>
      <div className="callout amber">
        <TriangleAlert size={16} />
        仅支持整个场景尚未执行、已有救援点。新增需求同时登记基地实物箱件，再全量重算。
      </div>
      <Button
        variant="primary"
        disabled={disabled}
        busy={busy}
        onClick={() => {
          setNonce(crypto.randomUUID().slice(0, 12))
          setOpen(true)
        }}
      >
        <PackagePlus size={15} />
        填写紧急需求
      </Button>
      <Modal
        title="插入紧急需求"
        description="保存为新事件与新版本；原需求、箱件和计划保持。全部截止相对场景零点，不是提交按钮的当前时刻。"
        open={open}
        onOpenChange={(value) => {
          if (!busy) setOpen(value)
        }}
      >
        <form
          className="dialog-body"
          onSubmit={(e) => {
            e.preventDefault()
            void submit()
          }}
          aria-label="紧急需求表单"
        >
          <div className="form-grid">
            <label className="field">
              <span>已有救援点</span>
              <select
                aria-label="紧急需求点"
                value={site}
                onChange={(e) => setSite(e.target.value)}
              >
                {scenario.sites.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.id} · {s.name}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>物资类型</span>
              <select
                aria-label="紧急物资类型"
                value={type}
                onChange={(e) => setType(e.target.value)}
              >
                {types.map((t) => (
                  <option key={t} value={t}>
                    {category[t] || t}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>箱件数量 / 箱</span>
              <input
                aria-label="紧急箱件数量"
                type="number"
                min="1"
                max="32"
                step="1"
                value={quantity}
                onChange={(e) => setQuantity(Number(e.target.value))}
              />
            </label>
            <label className="field">
              <span>优先级 / 正整数</span>
              <input
                aria-label="紧急需求优先级"
                type="number"
                min="1"
                max="1000"
                step="1"
                value={priority}
                onChange={(e) => setPriority(Number(e.target.value))}
              />
            </label>
            <label className="field">
              <span>每箱质量 / kg</span>
              <input
                aria-label="紧急每箱质量"
                type="number"
                min="0.001"
                step="any"
                value={mass}
                onChange={(e) => setMass(Number(e.target.value))}
              />
            </label>
            <label className="field">
              <span>每箱体积 / L</span>
              <input
                aria-label="紧急每箱体积"
                type="number"
                min="0.001"
                step="any"
                value={volume}
                onChange={(e) => setVolume(Number(e.target.value))}
              />
            </label>
            <label className="field">
              <span>期望截止 / 分钟，可空</span>
              <input
                aria-label="紧急期望截止分钟"
                type="number"
                min="0"
                step="any"
                value={expected}
                onChange={(e) => setExpected(e.target.value)}
              />
            </label>
            <label className="field">
              <span>硬截止 / 分钟，可空</span>
              <input
                aria-label="紧急硬截止分钟"
                type="number"
                min="0"
                step="any"
                value={hard}
                onChange={(e) => setHard(e.target.value)}
              />
            </label>
          </div>
          <label className="field">
            <span>事件说明</span>
            <input
              aria-label="紧急需求说明"
              value={reason}
              maxLength={500}
              onChange={(e) => setReason(e.target.value)}
            />
          </label>
          <div className="callout">
            <PackagePlus size={18} />
            <span>
              新增必须保障需求与{number(quantity)}个基地可用箱件，共{number(quantity * mass, 3)} kg
              / {number(quantity * volume, 3)}{' '}
              L。优先级越大，期望延期权重越高；硬截止是必须通过的约束。
            </span>
          </div>
          {!valid && (
            <p role="alert" className="what-if-warning">
              请填写有效正数、整数箱数与优先级；期望截止不能晚于硬截止。
            </p>
          )}
          <div className="dialog-footer">
            <Button type="button" disabled={busy} onClick={() => setOpen(false)}>
              取消
            </Button>
            <Button type="submit" variant="primary" busy={busy} disabled={disabled || !valid}>
              <PackagePlus size={15} />
              保存需求并重规划
            </Button>
          </div>
        </form>
      </Modal>
    </>
  )
}
