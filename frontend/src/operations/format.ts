import { clock as formatClock } from '../lib/format'
export function clock(value: number | null | undefined) {
  return value === null || value === undefined ? '—' : formatClock(value)
}
