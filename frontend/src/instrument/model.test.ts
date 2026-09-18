import { describe, expect, it } from 'vitest'
import { createInitialState, instrumentReducer, isReadingReady, createReadingRequest, deriveInstrumentView, getNextAffordance } from './model'
import type { InstrumentAction, InstrumentState } from './types'
import { manifestFixture as manifest, executionFixture } from '../test/fixtures'
const reduce = (s: InstrumentState, a: InstrumentAction) => instrumentReducer(s, a, manifest)
function held() {
  let s = reduce(createInitialState(), { type: 'OPEN_ARCA' })
  s = reduce(s, { type: 'FOCUS_BANK', bank: 1 })
  s = reduce(s, { type: 'FOCUS_CELL', cell: 4 })
  return reduce(s, { type: 'RETRIEVE_CARRIER' })
}
const seated = () => reduce(held(), { type: 'PLACE_HELD_CARRIER' })
describe('one-carrier instrument', () => {
  it('retrieves and places distinctly with the same identity', () => {
    const s = held()
    expect(s.carriers).toHaveLength(1)
    expect(s.carriers[0].location).toBe('hand')
    expect(s.heldCarrierId).toBe(s.carriers[0].instance_id)
    expect(reduce(s, { type: 'RETRIEVE_CARRIER' })).toBe(s)
    expect(isReadingReady(s, manifest)).toBe(false)
    const placed = reduce(s, { type: 'PLACE_HELD_CARRIER' })
    expect(placed.carriers[0]).toEqual({ ...s.carriers[0], location: 'workspace' })
    expect(placed.heldCarrierId).toBeNull()
    expect(isReadingReady(placed, manifest)).toBe(true)
    expect(deriveInstrumentView(placed)).toBe('working')
    expect(getNextAffordance(placed, manifest)).toBe('read_fragment')
  })
  it('cannot retrieve or execute without manifest and open cell', () => {
    const s = createInitialState()
    expect(reduce(s, { type: 'RETRIEVE_CARRIER' })).toBe(s)
    expect(instrumentReducer(s, { type: 'RETRIEVE_CARRIER' })).toBe(s)
    expect(reduce(s, { type: 'PLACE_HELD_CARRIER' })).toBe(s)
    expect(reduce(s, { type: 'EXECUTE' })).toBe(s)
  })
  it('rejects duplicate, contradictory and mismatched carrier state', () => {
    const s = seated()
    for (const invalid of [
      { ...s, carriers: [] },
      { ...s, carriers: [...s.carriers, { ...s.carriers[0] }] },
      { ...s, heldCarrierId: s.carriers[0].instance_id },
      { ...s, carriers: [{ ...s.carriers[0], edition_id: 'stale' }] },
      { ...s, carriers: [{ ...s.carriers[0], carrier_id: 'stale' }] },
    ]) expect(isReadingReady(invalid, manifest)).toBe(false)
  })
  it('clamps inspection without changing request', () => {
    const s = seated()
    const moved = reduce(s, { type: 'SET_READING_POSITION', position: 99 })
    expect(moved.readingPosition).toBe(5)
    expect(reduce(moved, { type: 'SET_READING_POSITION', position: -2 }).readingPosition).toBe(0)
    expect(reduce(s, { type: 'SET_READING_POSITION', position: NaN })).toBe(s)
    expect(createReadingRequest(moved, manifest)).toEqual(createReadingRequest(s, manifest))
    expect(Object.keys(createReadingRequest(s, manifest)).sort()).toEqual(['carrier_instance', 'content_digest', 'format', 'manifest_id'])
  })
  it('preserves the exact carrier and cursor through error, retry, success and return', () => {
    const seatedAtSix = reduce(seated(), { type: 'SET_READING_POSITION', position: 5 })
    const id = seatedAtSix.carriers[0].instance_id

    const pending = reduce(seatedAtSix, { type: 'EXECUTE' })
    expect(isReadingReady(pending, manifest)).toBe(false)
    expect(pending.carriers[0].instance_id).toBe(id)
    expect(pending.readingPosition).toBe(5)

    const error = reduce(pending, { type: 'EXECUTION_ERROR', message: 'offline' })
    expect(error.carriers[0].instance_id).toBe(id)
    expect(error.readingPosition).toBe(5)

    const retry = reduce(error, { type: 'EXECUTE' })
    expect(retry.carriers[0].instance_id).toBe(id)
    expect(retry.readingPosition).toBe(5)

    const success = reduce(retry, { type: 'EXECUTION_SUCCESS', execution: executionFixture })
    expect(deriveInstrumentView(success)).toBe('revelation')
    expect(success.carriers[0].instance_id).toBe(id)
    expect(success.execution?.reading.carrier_instance.instance_id).toBe(id)
    expect(success.readingPosition).toBe(5)

    const back = reduce(success, { type: 'RETURN_TO_WORKING' })
    expect(back.carriers[0].instance_id).toBe(id)
    expect(back.carriers).toEqual(seatedAtSix.carriers)
    expect(back.readingPosition).toBe(5)
    expect(back.execution).toBeNull()
    expect(back.error).toBeNull()
  })
  it('ignores a late success outside execution', () => {
    const s = seated()
    expect(reduce(s, { type: 'EXECUTION_SUCCESS', execution: executionFixture })).toBe(s)
    const closed = reduce(reduce(s, { type: 'EXECUTE' }), { type: 'CLOSE_ARCA' })
    expect(reduce(closed, { type: 'EXECUTION_SUCCESS', execution: executionFixture })).toBe(closed)
  })
})

it('rejects a mismatched kernel result before exposing the folio or provenance',() => {
  const pending=reduce(seated(),{type:'EXECUTE'})
  const bad=structuredClone(executionFixture)
  bad.fragment.events[5].voices.bassus.degree=4
  const next=reduce(pending,{type:'EXECUTION_SUCCESS',execution:bad})
  expect(next.phase).toBe('error')
  expect(next.execution).toBeNull()
  expect(next.carriers).toEqual(pending.carriers)
})
