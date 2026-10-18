import { test } from 'node:test'
import assert from 'node:assert/strict'
import { duration, clock, number, percent } from '../../src/lib/format.ts'

test('rounding carries seconds into the next minute and hour', () => {
  assert.equal(duration(59.9), '1分00秒')
  assert.equal(duration(3599.9), '1时00分')
  assert.equal(duration(null), '—')
})
test('zero is data, missing values remain unknown', () => {
  assert.equal(number(0), '0')
  assert.equal(percent(0), '0.0%')
  assert.equal(percent(undefined), '—')
  assert.equal(clock(3661), '01:01:01')
})
