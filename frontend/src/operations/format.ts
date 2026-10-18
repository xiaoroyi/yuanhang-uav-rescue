import { clock as formatClock } from '../lib/format'
export const datumLabel = (value: string | null | undefined) =>
  value === 'contest_provided_elevation_reference' ? '题设高程参考' : value || '未声明高程参考'
export function clock(value: number | null | undefined) {
  return value === null || value === undefined ? '—' : formatClock(value)
}
