import type { components } from './generated/http'

export type Scenario = components['schemas']['Scenario']
export type Snapshot = components['schemas']['Snapshot']
export type Plan = components['schemas']['Plan']
export type Sortie = Plan['sorties'][number]
export type SolveJob = components['schemas']['SolveJob']
export type ScenarioSummary = components['schemas']['ScenarioSummary']
export type PlanSummary = components['schemas']['PlanSummary']
export type Event = components['schemas']['Event']
export type Comparison = components['schemas']['Comparison']
export type Capabilities = components['schemas']['Capabilities']
export type Progress = components['schemas']['Progress']
export type Playback = components['schemas']['Playback']

export class ApiError extends Error {
  code: string
  status: number
  details: unknown
  constructor(
    status: number,
    data: { error?: { message?: string; code?: string; details?: unknown } },
  ) {
    super(data.error?.message || `请求失败 (${status})`)
    this.code = data.error?.code || 'NETWORK_ERROR'
    this.status = status
    this.details = data.error?.details
  }
}

async function request<T>(url: string, body?: unknown, method?: string): Promise<T> {
  const response = await fetch('/api/v1' + url, {
    method: method || (body === undefined ? 'GET' : 'POST'),
    headers: body === undefined ? {} : { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  const data = await response.json()
  if (!response.ok) throw new ApiError(response.status, data)
  return data as T
}

export const api = {
  health: () => request<components['schemas']['Health']>('/health'),
  scenarios: () => request<ScenarioSummary[]>('/scenarios'),
  scenario: (id: string) => request<Scenario>(`/scenarios/${id}`),
  example: (example: 'compact' | 'contest') =>
    request<Scenario>('/scenarios/examples', { example }),
  import: (scenario: Scenario) => request<Scenario>('/scenarios/import', scenario),
  copy: (id: string, name?: string) => request<Scenario>(`/scenarios/${id}/copy`, { name }),
  save: (s: Scenario) =>
    request<Scenario>(
      `/scenarios/${s.scenario_id}`,
      { expected_state_version: s.state_version, scenario: s },
      'PUT',
    ),
  snapshot: (s: Scenario) =>
    request<Snapshot>(`/scenarios/${s.scenario_id}/snapshots`, {
      expected_state_version: s.state_version,
    }),
  getSnapshot: (id: string) => request<Snapshot>(`/snapshots/${id}`),
  solve: (
    snapshot_id: string,
    objective: 'time' | 'energy' | 'balanced',
    options: Partial<components['schemas']['SolveRequest']> = {},
  ) =>
    request<SolveJob>('/solve-jobs', {
      snapshot_id,
      objective,
      time_limit_s: 15,
      seed: 42,
      ...options,
    }),
  job: (id: string) => request<SolveJob>(`/solve-jobs/${id}`),
  progress: (id: string) => request<Progress>(`/solve-jobs/${id}/progress`),
  diagnostics: (id: string) =>
    request<{ diagnostics: { code: string; message: string }[] }>(`/solve-jobs/${id}/diagnostics`),
  cancel: (id: string) => request<SolveJob>(`/solve-jobs/${id}/cancel`, undefined, 'POST'),
  plan: (id: string) => request<Plan>(`/plans/${id}`),
  playback: (id: string) => request<Playback>(`/plans/${id}/playback`),
  plans: (scenario: string) => request<PlanSummary[]>(`/scenarios/${scenario}/plans`),
  confirm: (p: Plan, version: number) =>
    request<components['schemas']['Confirmation']>(`/plans/${p.plan_id}/confirm`, {
      expected_state_version: version,
      idempotency_key: 'CONF-' + p.plan_id + '-' + version,
    }),
  events: (scenario: string) => request<Event[]>(`/scenarios/${scenario}/events`),
  event: (event: Event) => request<components['schemas']['EventReceipt']>('/events', event),
  compare: (a: string, b: string) =>
    request<Comparison>(`/plans/${a}/comparison?other_plan_id=${b}`),
  capabilities: () => request<Capabilities>('/meta/capabilities'),
  preview: async (file: File, scenario: string, entity: string) => {
    const body = new FormData()
    body.append('file', file)
    const response = await fetch(
      `/api/v1/scenarios/import-file?scenario_id=${scenario}&entity=${entity}`,
      { method: 'POST', body },
    )
    const data = await response.json()
    if (!response.ok) throw new ApiError(response.status, data)
    return data as components['schemas']['ImportPreview']
  },
  validate: (s: Scenario) =>
    request<components['schemas']['Validation']>(`/scenarios/${s.scenario_id}/validate`, {
      expected_state_version: s.state_version,
    }),
  exportUrl: (plan: string, format: 'json' | 'csv' | 'geojson') =>
    `/api/v1/plans/${plan}/export?format=${format}`,
}

export function downloadJson(value: unknown, name: string) {
  const url = URL.createObjectURL(
    new Blob([JSON.stringify(value, null, 2)], { type: 'application/json' }),
  )
  const a = document.createElement('a')
  a.href = url
  a.download = name
  a.click()
  URL.revokeObjectURL(url)
}
