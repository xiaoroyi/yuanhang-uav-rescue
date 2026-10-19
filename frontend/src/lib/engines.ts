import type { Plan } from '../api/client'
type Record = { engine?: Plan['engine'] | null } | null | undefined
export const engineLabel = (p: Record) =>
  p?.engine?.engine_type === 'eoh' ? 'EOH增强' : '标准调度'
export const engineOptions = (p: Record) =>
  p?.engine
    ? {
        engine_type: p.engine.engine_type,
        ...(p.engine.policy_id ? { heuristic_policy_id: p.engine.policy_id } : {}),
        ...(p.engine.sha256 ? { heuristic_policy_sha256: p.engine.sha256 } : {}),
      }
    : {}
