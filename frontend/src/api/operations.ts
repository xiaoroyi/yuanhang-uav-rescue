import type { components } from './generated/http'
import { request } from './client'

export type Mission = components['schemas']['MissionView']
export type MissionDraft = components['schemas']['MissionDraft']
export type MissionCreate = components['schemas']['MissionCreate']
export type CheckReport = components['schemas']['PreflightReport']
export type Execution = components['schemas']['ExecutionView']
export type ExecutionEvent = components['schemas']['ExecutionEventView']
export type Repair = components['schemas']['RepairView']
export type Stages = components['schemas']['StageAnalysis']
export type Telemetry = components['schemas']['TelemetrySample']
export type ExecutionAnalysis = components['schemas']['ExecutionAnalysis']
export const key = () => crypto.randomUUID()
export const ops = {
  missions: () => request<Mission[]>('/missions'),
  mission: (id: string) => request<Mission>(`/missions/${id}`),
  create: (
    body: Omit<MissionCreate, 'mode' | 'template'> &
      Partial<Pick<MissionCreate, 'mode' | 'template'>>,
  ) => request<Mission>('/missions', { mode: 'simulation', template: 'blank', ...body }),
  update: (m: Mission, body: Pick<components['schemas']['MissionUpdate'], 'name' | 'archived'>) =>
    request<Mission>(
      `/missions/${m.mission_id}`,
      { expected_revision: m.revision, ...body },
      'PATCH',
    ),
  clone: (m: Mission) =>
    request<Mission>(`/missions/${m.mission_id}/clone`, {
      name: m.name + ' · 演练副本',
      idempotency_key: key(),
    }),
  draft: (m: Mission, draft: MissionDraft, publish = false) =>
    request<Mission>(
      `/missions/${m.mission_id}/draft`,
      { expected_revision: m.revision, draft, publish },
      'PUT',
    ),
  check: (
    m: Mission,
    kind: components['schemas']['PreflightRequest']['check_kind'] = 'planning_readiness',
    plan_id?: string,
  ) =>
    request<CheckReport>(`/missions/${m.mission_id}/preflight`, {
      expected_revision: m.revision,
      check_kind: kind,
      plan_id,
    }),
  stages: (id: string) => request<Stages>(`/plans/${id}/stages`),
  checks: (id: string) => request<CheckReport[]>(`/missions/${id}/preflight-reports`),
  executions: (id: string) => request<Execution[]>(`/missions/${id}/executions`),
  execution: (id: string) => request<Execution>(`/executions/${id}`),
  start: (m: Mission, plan: string) =>
    request<Execution>('/executions', {
      mission_id: m.mission_id,
      confirmed_plan_id: plan,
      expected_revision: m.revision,
      mode: 'simulation',
      idempotency_key: key(),
    }),
  action: (
    e: Execution,
    action: components['schemas']['SimulationAction']['action'],
    options: { speed?: number; target_time_s?: number } = {},
  ) =>
    request<Execution>(`/executions/${e.execution_id}/simulation/actions`, {
      action,
      expected_revision: e.revision,
      idempotency_key: key(),
      ...options,
    }),
  events: (id: string) => request<ExecutionEvent[]>(`/executions/${id}/events`),
  event: (
    e: Execution,
    body: Omit<components['schemas']['ExecutionEventInput'], 'expected_revision' | 'event_id'>,
  ) =>
    request<ExecutionEvent>(`/executions/${e.execution_id}/events`, {
      event_id: key(),
      expected_revision: e.revision,
      ...body,
    }),
  resolveEvent: (e: Execution, eventId: string, reason: string) =>
    request<ExecutionEvent>(`/executions/${e.execution_id}/events/${eventId}/resolve`, {
      expected_revision: e.revision,
      idempotency_key: key(),
      action: 'withdraw_misreport',
      reason,
    }),
  repair: (e: Execution) =>
    request<Repair>(`/executions/${e.execution_id}/replan-jobs`, {
      expected_revision: e.revision,
      idempotency_key: key(),
      time_limit_s: 10,
    }),
  changes: (id: string) => request<Repair[]>(`/executions/${id}/plan-changes`),
  apply: (e: Execution, change: Repair, faults: string[] = []) =>
    request<Repair>(`/executions/${e.execution_id}/plan-changes/${change.change_id}/apply`, {
      expected_revision: e.revision,
      idempotency_key: key(),
      ack_timeout_device_ids: faults,
    }),
  executionAnalysis: (id: string) => request<ExecutionAnalysis>(`/executions/${id}/analysis`),
}
