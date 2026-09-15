import { describe, expect, it } from 'vitest'
import { deriveCameraMode } from './camera'
import { createInitialState, instrumentReducer } from '../instrument/model'
import type { InstrumentAction, InstrumentState } from '../instrument/types'
import { executionFixture, manifestFixture } from '../test/fixtures'

const reduce = (state: InstrumentState, action: InstrumentAction) =>
  instrumentReducer(state, action, manifestFixture)

function atCell(): InstrumentState {
  let state = reduce(createInitialState(), { type: 'OPEN_ARCA' })
  state = reduce(state, { type: 'FOCUS_BANK', bank: 1 })
  return reduce(state, { type: 'FOCUS_CELL', cell: 4 })
}

function seatAll(): InstrumentState {
  let state = atCell()
  for (const template of manifestFixture.rod_templates) {
    state = reduce(state, { type: 'RETRIEVE_ROD', template })
    state = reduce(state, { type: 'PLACE_HELD_ROD' })
  }
  return state
}

/**
 * The camera is PRESENTATION. It may reframe for a change in what the
 * instrument physically is, and must not reframe for every change in what the
 * instrument is thinking about — otherwise the Arca stops feeling like one
 * persistent object on a desk and starts feeling like a slideshow.
 */
describe('camera intervention', () => {
  it('frames the closed Arca while dormant', () => {
    expect(deriveCameraMode(createInitialState())).toBe('arca')
  })

  it('treats opening, Bank I and Cell IV as one continuous open state', () => {
    let state = reduce(createInitialState(), { type: 'OPEN_ARCA' })
    expect(deriveCameraMode(state)).toBe('open')
    state = reduce(state, { type: 'FOCUS_BANK', bank: 1 })
    expect(deriveCameraMode(state)).toBe('open')
    state = reduce(state, { type: 'FOCUS_CELL', cell: 4 })
    expect(deriveCameraMode(state)).toBe('open')
  })

  it('does not move to the carriage merely because a virga was lifted', () => {
    const held = reduce(atCell(), { type: 'RETRIEVE_ROD', template: manifestFixture.rod_templates[0] })
    expect(held.phase).toBe('rod_retrieval')
    // The reader is looking at the cell and the rod in hand. Cutting to the
    // drawer here is precisely the move that loses the transfer.
    expect(deriveCameraMode(held)).toBe('open')
  })

  it('moves to the carriage on the first seated virga and stays there', () => {
    let state = reduce(atCell(), { type: 'RETRIEVE_ROD', template: manifestFixture.rod_templates[0] })
    state = reduce(state, { type: 'PLACE_HELD_ROD' })
    expect(deriveCameraMode(state)).toBe('working')

    // Second and third retrievals must NOT drop back to 'open' and cut away.
    state = reduce(state, { type: 'RETRIEVE_ROD', template: manifestFixture.rod_templates[1] })
    expect(deriveCameraMode(state)).toBe('working')
    state = reduce(state, { type: 'PLACE_HELD_ROD' })
    expect(deriveCameraMode(state)).toBe('working')
  })

  it('holds one framing across alignment, concord and Tone II', () => {
    let state = seatAll()
    expect(deriveCameraMode(state)).toBe('working')
    for (const rod of state.rods) {
      state = reduce(state, { type: 'MOVE_ROD', instanceId: rod.instance_id, offset: 0 })
    }
    expect(state.phase).toBe('historical_alignment_ready')
    expect(deriveCameraMode(state)).toBe('working')
    state = reduce(state, { type: 'ENGAGE_TONE' })
    expect(deriveCameraMode(state)).toBe('working')
    state = reduce(state, { type: 'EXECUTE' })
    expect(deriveCameraMode(state)).toBe('working')
  })

  it('reframes only for the revelation, and returns to the carriage after it', () => {
    let state = seatAll()
    for (const rod of state.rods) {
      state = reduce(state, { type: 'MOVE_ROD', instanceId: rod.instance_id, offset: 0 })
    }
    state = reduce(state, { type: 'ENGAGE_TONE' })
    state = reduce(state, { type: 'EXECUTE' })
    state = reduce(state, { type: 'EXECUTION_SUCCESS', execution: executionFixture })
    expect(deriveCameraMode(state)).toBe('revelation')
    state = reduce(state, { type: 'RETURN_TO_WORKING' })
    expect(deriveCameraMode(state)).toBe('working')
  })

  it('keeps the disposition in frame when an execution fails', () => {
    let state = seatAll()
    for (const rod of state.rods) {
      state = reduce(state, { type: 'MOVE_ROD', instanceId: rod.instance_id, offset: 0 })
    }
    state = reduce(state, { type: 'ENGAGE_TONE' })
    state = reduce(state, { type: 'EXECUTE' })
    state = reduce(state, { type: 'EXECUTION_ERROR', message: 'rejected' })
    expect(deriveCameraMode(state)).toBe('working')
  })

  it('derives purely from canonical state and stores nothing in it', () => {
    const before = JSON.stringify(seatAll())
    const state: InstrumentState = JSON.parse(before)
    deriveCameraMode(state)
    expect(JSON.stringify(state)).toBe(before)
    expect(Object.keys(state)).not.toContain('camera')
  })
})
