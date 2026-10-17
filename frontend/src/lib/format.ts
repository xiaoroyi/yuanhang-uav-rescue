export const number = (value: number | null | undefined, digits = 0) =>
  value == null ? '—' : value.toLocaleString('zh-CN', { maximumFractionDigits: digits })
export const duration = (seconds: number | null | undefined) => {
  if (seconds == null) return '—'
  const total = Math.max(0, Math.round(seconds))
  const h = Math.floor(total / 3600),
    m = Math.floor((total % 3600) / 60),
    s = total % 60
  return h ? `${h}时${m.toString().padStart(2, '0')}分` : `${m}分${s.toString().padStart(2, '0')}秒`
}
export const clock = (seconds: number) =>
  `${Math.floor(seconds / 3600)
    .toString()
    .padStart(2, '0')}:${Math.floor((seconds % 3600) / 60)
    .toString()
    .padStart(2, '0')}:${Math.floor(seconds % 60)
    .toString()
    .padStart(2, '0')}`
export const percent = (value: number | null | undefined) =>
  value == null ? '—' : `${(value * 100).toFixed(1)}%`
export const category: Record<string, string> = {
  MED: '医疗物资',
  WAT: '饮用水',
  FOD: '应急食品',
  HYG: '卫生用品',
}
export const colors = [
  '#0e8f85',
  '#4f78c6',
  '#d49b42',
  '#9672bd',
  '#5e9b58',
  '#cb7485',
  '#527f91',
  '#a1845c',
]
export const colorFor = (id: string) =>
  colors[[...id].reduce((n, c) => n + c.charCodeAt(0), 0) % colors.length]
export const originLabel: Record<string, string> = {
  mock: '开发样例',
  verified_dataset: '题设数据',
  user_input: '用户输入',
  solver: '真实计算',
  imported_historical: '历史回放',
}
export const statusLabel: Record<string, string> = {
  available: '可用',
  unavailable: '不可用',
  reserved: '已预留',
  loaded: '已装载',
  in_flight: '在飞',
  in_use: '使用中',
  charging: '充电中',
  in_transit: '在途',
  delivered: '已交付',
  queued: '排队中',
  running: '求解中',
  completed: '已结束',
  failed: '计算失败',
  canceled: '已取消',
  FEASIBLE: '模型内可行',
  OPTIMAL: '模型内最优',
  UNKNOWN: '尚未找到可行解',
  INFEASIBLE: '当前模型无解',
  ERROR: '计算异常',
  passed: '检查通过',
  not_evaluated: '未评估',
  partial: '部分评估',
  not_run: '未检查',
}
