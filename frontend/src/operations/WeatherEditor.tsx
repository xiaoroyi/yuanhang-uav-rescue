import { useState } from 'react'
import { CloudSun, Settings2 } from 'lucide-react'
import type { Scenario } from '../api/client'
import { Button, Modal } from '../components/ui'

type Weather = NonNullable<Scenario['weather']>
type Rule = Weather['rules'][number]
const limits = [
  ['max_wind_mps', '最大风速 / m/s'],
  ['max_gust_mps', '最大阵风 / m/s'],
  ['min_temperature_c', '最低温度 / °C'],
  ['max_temperature_c', '最高温度 / °C'],
  ['max_precipitation_mm_h', '最大降水 / mm/h'],
] as const
type LimitKey = (typeof limits)[number][0]

export function WeatherEditor({
  scenario,
  onSave,
  notify,
  purpose = 'input',
}: {
  scenario: Scenario
  onSave: (s: Scenario) => Promise<void>
  notify: (m: string, e?: boolean) => void
  purpose?: 'input' | 'event'
}) {
  const saved = scenario.weather
  const [open, setOpen] = useState(false)
  const [busy, setBusy] = useState(false)
  const [accepted, setAccepted] = useState(false)
  const [source, setSource] = useState(saved?.source_ref || '')
  const [ruleSource, setRuleSource] = useState(saved?.rules[0]?.source_ref || '')
  const [from, setFrom] = useState(String((saved?.valid_from_s ?? 0) / 60))
  const [until, setUntil] = useState(String((saved?.valid_until_s ?? 14400) / 60))
  const [height, setHeight] = useState(String(saved?.height_m ?? 10))
  const [values, setValues] = useState({
    wind_speed_mps: saved?.wind_speed_mps == null ? '' : String(saved.wind_speed_mps),
    gust_mps: saved?.gust_mps == null ? '' : String(saved.gust_mps),
    wind_direction_from_deg:
      saved?.wind_direction_from_deg == null ? '' : String(saved.wind_direction_from_deg),
    temperature_c: saved?.temperature_c == null ? '' : String(saved.temperature_c),
    precipitation_mm_h: saved?.precipitation_mm_h == null ? '' : String(saved.precipitation_mm_h),
  })
  const [rules, setRules] = useState<Record<string, Record<LimitKey, string>>>(() =>
    Object.fromEntries(
      scenario.drone_types.map((t) => [
        t.type_id,
        Object.fromEntries(
          limits.map(([k]) => [
            k,
            saved?.rules.find((r) => r.type_id === t.type_id)?.[k] == null
              ? ''
              : String(saved.rules.find((r) => r.type_id === t.type_id)![k]),
          ]),
        ) as Record<LimitKey, string>,
      ]),
    ),
  )
  const numeric = (value: string) => (value.trim() === '' ? null : Number(value))
  async function save() {
    setBusy(true)
    try {
      if (!accepted) throw new Error('请确认这是人工统一情景，不是实际观测或预报。')
      if (!source.trim() || !ruleSource.trim()) throw new Error('请填写情景和限值来源。')
      const list: Rule[] = scenario.drone_types.flatMap((t) => {
        const r = rules[t.type_id]
        if (!limits.some(([k]) => r[k].trim())) return []
        return [
          {
            type_id: t.type_id,
            source_ref: ruleSource,
            max_wind_mps: numeric(r.max_wind_mps),
            max_gust_mps: numeric(r.max_gust_mps),
            min_temperature_c: numeric(r.min_temperature_c),
            max_temperature_c: numeric(r.max_temperature_c),
            max_precipitation_mm_h: numeric(r.max_precipitation_mm_h),
          },
        ]
      })
      if (!list.length) throw new Error('请至少为一个机型填写有来源的限值。')
      const weather: Weather = {
        model_id: 'manual_operating_window_v1',
        weather_id: 'WX-' + crypto.randomUUID(),
        source_kind: 'manual_scenario',
        source_ref: source,
        issued_at: new Date().toISOString(),
        valid_from_s: Number(from) * 60,
        valid_until_s: Number(until) * 60,
        height_m: Number(height),
        height_reference: 'AGL',
        wind_speed_mps: numeric(values.wind_speed_mps),
        gust_mps: numeric(values.gust_mps),
        wind_direction_from_deg: numeric(values.wind_direction_from_deg),
        temperature_c: numeric(values.temperature_c),
        precipitation_mm_h: numeric(values.precipitation_mm_h),
        rules: list,
      }
      await onSave({ ...scenario, weather })
      setOpen(false)
      notify(
        purpose === 'event'
          ? '气象变化已记录，请核对影响并生成调整。'
          : '人工气象情景已保存为新输入版本，请重新检查并计算。',
      )
    } catch (e) {
      notify((e as Error).message, true)
    } finally {
      setBusy(false)
    }
  }
  return (
    <section className="v2-weather-editor v2-card">
      <div className="v2-section-bar">
        <div>
          <h3>
            <CloudSun size={17} /> 气象作业条件
          </h3>
          <p>
            {saved
              ? `人工情景 · ${saved.valid_from_s / 60}—${saved.valid_until_s / 60} min · ${saved.rules.length}种机型规则`
              : '未绑定；当前按题设无风参数演练'}
          </p>
        </div>
        <Button onClick={() => setOpen(true)}>
          <Settings2 size={14} />
          {saved ? '编辑气象与限值' : '配置人工气象情景'}
        </Button>
      </div>
      <Modal
        title="人工气象与机型作业限值"
        description="W1：检查所配置限值与时间窗口；风尚未进入能源/速度模型。未知变量留空，不填0。"
        open={open}
        onOpenChange={setOpen}
        wide
      >
        <div className="v2-weather-form">
          <div className="v2-field-pair">
            <label>
              情景来源 / 假设说明
              <input
                value={source}
                onChange={(e) => setSource(e.target.value)}
                placeholder="例如：演练人员设定的全区域均匀情景"
              />
            </label>
            <label>
              机型限值来源
              <input
                value={ruleSource}
                onChange={(e) => setRuleSource(e.target.value)}
                placeholder="机型文档/组织配置，或明确标为演练假设"
              />
            </label>
          </div>
          <div className="v2-weather-variables">
            <label>
              起始 / 相对分钟
              <input
                type="number"
                min={0}
                step="any"
                value={from}
                onChange={(e) => setFrom(e.target.value)}
              />
            </label>
            <label>
              结束 / 相对分钟
              <input
                type="number"
                min={0}
                step="any"
                value={until}
                onChange={(e) => setUntil(e.target.value)}
              />
            </label>
            <label>
              参考高度 / AGL m
              <input
                type="number"
                min={0}
                value={height}
                onChange={(e) => setHeight(e.target.value)}
              />
            </label>
            {(
              [
                ['wind_speed_mps', '风速 / m/s'],
                ['gust_mps', '阵风 / m/s'],
                ['wind_direction_from_deg', '风从何处来 / °'],
                ['temperature_c', '环境温度 / °C'],
                ['precipitation_mm_h', '降水 / mm/h'],
              ] as const
            ).map(([k, name]) => (
              <label key={k}>
                {name}
                <input
                  type="number"
                  step="any"
                  value={values[k]}
                  placeholder="未知"
                  onChange={(e) => setValues({ ...values, [k]: e.target.value })}
                />
              </label>
            ))}
          </div>
          <h3>按机型配置限值</h3>
          <p className="v2-subtle">
            未配置规则或所需变量缺失的机型不参与排程；其余合格机型仍可尝试完成任务。以下不预填通用限值。
          </p>
          <div className="v2-table-scroll">
            <table className="v2-table">
              <thead>
                <tr>
                  <th>机型</th>
                  {limits.map(([k, label]) => (
                    <th key={k}>{label}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {scenario.drone_types.map((t) => (
                  <tr key={t.type_id}>
                    <td>{t.type_id}</td>
                    {limits.map(([k, label]) => (
                      <td key={k}>
                        <input
                          aria-label={`${t.type_id} ${label}`}
                          type="number"
                          step="any"
                          value={rules[t.type_id][k]}
                          placeholder="未启用"
                          onChange={(e) =>
                            setRules({
                              ...rules,
                              [t.type_id]: { ...rules[t.type_id], [k]: e.target.value },
                            })
                          }
                        />
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <label className="v2-weather-consent">
            <input
              type="checkbox"
              checked={accepted}
              onChange={(e) => setAccepted(e.target.checked)}
            />
            确认将以上参数作为空间均匀的人工演练情景；不代表实测、预报或飞行许可
          </label>
          <div className="v2-form-actions">
            {saved && purpose === 'input' && (
              <Button
                disabled={busy}
                onClick={() => {
                  setBusy(true)
                  const next = { ...scenario }
                  delete next.weather
                  void onSave(next)
                    .then(() => {
                      setOpen(false)
                      notify('已移除人工气象情景，原方案仍保留。')
                    })
                    .catch((e: Error) => notify(e.message, true))
                    .finally(() => setBusy(false))
                }}
              >
                移除情景
              </Button>
            )}
            <Button onClick={() => setOpen(false)}>取消</Button>
            <Button variant="primary" busy={busy} onClick={() => void save()}>
              保存气象条件
            </Button>
          </div>
        </div>
      </Modal>
    </section>
  )
}
