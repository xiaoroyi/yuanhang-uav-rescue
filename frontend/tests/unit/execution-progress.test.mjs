import {test} from 'node:test'
import assert from 'node:assert/strict'
import {executionCargoProgress} from '../../src/lib/execution-progress.ts'

test('repair snapshot totals retain delivered and in-flight commitments plus new boxes',()=>{
  const initial=Array.from({length:32},(_,i)=>'box-'+i)
  const current=[...initial.slice(14),'urgent-new']
  const delivered=[initial[0]],loaded=initial.slice(1,14)
  const value=executionCargoProgress(initial,current,delivered,loaded)
  assert.deepEqual(value,{total:33,done:1,loaded:13,pending:19})
  assert.equal(value.total,value.done+value.loaded+value.pending)
})
test('late telemetry does not double-count delivered cargo; distinct IDs stay distinct',()=>{
  assert.deepEqual(executionCargoProgress(['a','b'],['b','c'],['a','a'],['a','b','b'],['c','d']),{total:4,done:1,loaded:1,pending:2})
})
