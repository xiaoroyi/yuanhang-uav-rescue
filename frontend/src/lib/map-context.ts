import type { FeatureCollection, Geometry } from 'geojson'
import type { Scenario } from '../api/client'

export type TownContextMetadata = {
  name: string
  bounds: [number, number, number, number]
  counts: { road: number; water: number; waterway: number; place: number; boundary: number }
  source_html: string
  source_html_sha256: string
  geojson_sha256: string
  notice: string
  attribution: string
  attribution_url: string
}
export type TownContextData = FeatureCollection<
  Geometry,
  {
    context_kind: 'road' | 'water' | 'waterway' | 'place' | 'boundary'
    context_name: string
    [name: string]: unknown
  }
>

let metadata: Promise<TownContextMetadata> | undefined
let data: Promise<TownContextData> | undefined
async function local<T>(url: string): Promise<T> {
  const response = await fetch(url)
  if (!response.ok) throw new Error('本地地理背景资料暂不可用。')
  return response.json() as Promise<T>
}
export const loadTownContextMetadata = () =>
  (metadata ||= local<TownContextMetadata>('/maps/town-context-meta.json'))
export const loadTownContextData = () =>
  (data ||= local<TownContextData>('/maps/town-context.geojson'))

export function townContextApplies(
  scenario: { base: Scenario['base'] | null; sites: Scenario['sites'] },
  metadata: TownContextMetadata,
): boolean {
  const [west, south, east, north] = metadata.bounds
  return (scenario.base ? [scenario.base, ...scenario.sites] : scenario.sites).some(
    ({ coordinates: [x, y] }) => x >= west && x <= east && y >= south && y <= north,
  )
}
