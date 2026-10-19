import type { components } from './generated/http'
import { request, ApiError } from './client'
export type ExerciseCase = components['schemas']['ExerciseCase']
export type HeuristicPackage = components['schemas']['HeuristicPackage']
export const command = {
  cases: () => request<components['schemas']['CaseCatalog']>('/case-library'),
  overview: () => request<components['schemas']['AssetOverview']>('/asset-overview'),
  engines: () => request<HeuristicPackage[]>('/heuristic-packages'),
  importPolicy: async (file: File): Promise<HeuristicPackage> => {
    const body = new FormData()
    body.append('file', file)
    const response = await fetch('/api/v1/heuristic-packages/import', { method: 'POST', body })
    if (!response.ok) throw new ApiError(response.status, await response.json())
    return response.json()
  },
}
