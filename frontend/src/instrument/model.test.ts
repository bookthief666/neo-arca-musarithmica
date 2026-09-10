import { describe, expect, it } from 'vitest'
import { createAlignmentRequest, createInitialState, instrumentReducer, isAlignmentReady, isExecutionReady } from './model'
import type { InstrumentAction, InstrumentState } from './types'
import { executionFixture, manifestFixture } from '../test/fixtures'

function reduce(state: InstrumentState, action: InstrumentAction) {
  return instrumentReducer(state, action, manifestFixture)
}

function stateWithPlacedRods(): InstrumentState {
  let state = createInitialState()
  state = reduce(state, { type: 'OPEN_ARCA' })
  state = reduce(state, { type: 'FOCUS_BANK', bank: 1 })
  state = reduce(state, { type: 'FOCUS_CELL', cell: 4 })
  for (const template of manifestFixture.rod_templates) {
    state = reduce(state, { type: 'RETRIEVE_ROD', template })
    state = reduce(state, { type: 'PLACE_HELD_ROD' })
  }
  return state
}

describe('canonical instrument model', () => {
  it('begins dormant with no duplicated UI authority', () => {
    expect(createInitialState()).toMatchObject({ phase: 'dormant', rods: [], toneEngaged: false })
  })

  it('opens the Arca and focuses Bank I / Cell IV through explicit actions', () => {
    let state = reduce(createInitialState(), { type: 'OPEN_ARCA' })
    state = reduce(state, { type: 'FOCUS_BANK', bank: 1 })
    state = reduce(state, { type: 'FOCUS_CELL', cell: 4 })
    expect(state).toMatchObject({ phase: 'cell_focus', focusedBank: 1, focusedCell: 4 })
  })

  it('creates repeated rod instances without mutating source templates', () => {
    const sourceBefore = structuredClone(manifestFixture.source_columns)
    const state = stateWithPlacedRods()
    const pitchCopies = state.rods.filter((rod) => rod.source_column_id.includes('VPERM'))
    expect(pitchCopies).toHaveLength(2)
    expect(new Set(pitchCopies.map((rod) => rod.instance_id)).size).toBe(2)
    expect(manifestFixture.source_columns).toEqual(sourceBefore)
  })

  it('tracks vertical displacement while leaving historical source data untouched', () => {
    const state = stateWithPlacedRods()
    const target = state.rods[0]
    const moved = reduce(state, { type: 'MOVE_ROD', instanceId: target.instance_id, offset: 7 })
    expect(moved.rods[0].vertical_offset).toBe(7)
    expect(manifestFixture.source_columns[0].bands[0].status).toBe('verified')
  })

  it('refuses readiness while any visible rod exposes an untranscribed band', () => {
    expect(isAlignmentReady(stateWithPlacedRods(), manifestFixture)).toBe(false)
  })

  it('becomes ready only when every physical carrier reaches verified band 01', () => {
    let state = stateWithPlacedRods()
    for (const rod of state.rods) {
      state = reduce(state, { type: 'MOVE_ROD', instanceId: rod.instance_id, offset: 0 })
    }
    expect(state.phase).toBe('historical_alignment_ready')
    expect(isAlignmentReady(state, manifestFixture)).toBe(true)
  })

  it('requires the integrated Tone II action before execution', () => {
    let state = stateWithPlacedRods()
    for (const rod of state.rods) state = reduce(state, { type: 'MOVE_ROD', instanceId: rod.instance_id, offset: 0 })
    expect(isExecutionReady(state, manifestFixture)).toBe(false)
    state = reduce(state, { type: 'ENGAGE_TONE' })
    expect(isExecutionReady(state, manifestFixture)).toBe(true)
  })

  it('creates a detached immutable bridge request from canonical state', () => {
    let state = stateWithPlacedRods()
    for (const rod of state.rods) state = reduce(state, { type: 'MOVE_ROD', instanceId: rod.instance_id, offset: 0 })
    state = reduce(state, { type: 'ENGAGE_TONE' })
    const request = createAlignmentRequest(state, manifestFixture)
    request.rod_instances[0].vertical_offset = 4
    expect(state.rods[0].vertical_offset).toBe(0)
    expect(request.tone.number).toBe(2)
  })

  it('preserves kernel provenance through the revealed state', () => {
    let state = stateWithPlacedRods()
    for (const rod of state.rods) state = reduce(state, { type: 'MOVE_ROD', instanceId: rod.instance_id, offset: 0 })
    state = reduce(state, { type: 'ENGAGE_TONE' })
    state = reduce(state, { type: 'EXECUTE' })
    state = reduce(state, { type: 'EXECUTION_SUCCESS', execution: executionFixture })
    expect(state.execution?.fragment.provenance.transcription_protocol).toContain('TRANSCRIPTION_SPEC')
    expect(state.execution?.fragment.events[0].voices.cantus.provenance.vperm_cell).toBe('C1')
  })

  it('records reduced-motion preference in canonical presentation state', () => {
    const state = reduce(createInitialState(), { type: 'SET_REDUCED_MOTION', value: true })
    expect(state.reducedMotion).toBe(true)
  })
})
