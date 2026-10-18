import { test } from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs/promises'
import crypto from 'node:crypto'
import { townContextApplies } from '../../src/lib/map-context.ts'

const metadata = JSON.parse(
  await fs.readFile(new URL('../../public/maps/town-context-meta.json', import.meta.url), 'utf8'),
)

test('archived map context has exact provenance hash, feature counts and finite WGS84 geometry', async () => {
  const raw = await fs.readFile(new URL('../../public/maps/town-context.geojson', import.meta.url))
  assert.equal(crypto.createHash('sha256').update(raw).digest('hex'), metadata.geojson_sha256)
  const data = JSON.parse(raw.toString('utf8')),
    counts = {}
  for (const feature of data.features) {
    const kind = feature.properties.context_kind
    counts[kind] = (counts[kind] || 0) + 1
    assert.ok(feature.properties.context_name !== undefined)
    if (kind !== 'boundary') assert.ok(feature.properties['OSM编号'])
    const check = (value) => {
      if (typeof value[0] === 'number') {
        assert.equal(value.length, 2)
        assert.ok(value.every(Number.isFinite))
        assert.ok(value[0] >= 109 && value[0] <= 109.5 && value[1] >= 22.8 && value[1] <= 23.3)
      } else value.forEach(check)
    }
    check(feature.geometry.coordinates)
  }
  assert.deepEqual(counts, metadata.counts)
  assert.deepEqual(data.bbox, metadata.bounds)
})

test('foreign input coordinates do not inherit the archived town background', () => {
  const scene = (coordinates) => ({ base: { coordinates }, sites: [] })
  assert.equal(townContextApplies(scene([109.2308517, 23.0085095]), metadata), true)
  assert.equal(townContextApplies(scene([104.06, 30.67]), metadata), false)
  assert.equal(townContextApplies(scene([116.4, 39.9]), metadata), false)
})
