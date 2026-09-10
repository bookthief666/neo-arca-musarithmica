import { describe, expect, it } from 'vitest'
import {
  createAlignmentRequest,
  createInitialState,
  deriveInstrumentView,
  getNextAffordance,
  instrumentReducer,
  isAlignmentReady,
  isExecutionReady,
} from './model'
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
    state = reduce(state, { type: 'DEPLOY_ROD', template })
  }
  return state
}

describe('canonical instrument model', () => {
  it('begins dormant with no duplicated UI authority', () => {
    const state = createInitialState()
    expect(state).toMatchObject({ phase: 'dormant', rods: [], toneEngaged: false })
    expect(deriveInstrumentView(state)).toBe('arca')
    expect(getNextAffordance(state, manifestFixture)).toBe('open_arca')
  })

  it('opens the Arca and focuses Bank I / Cell IV through explicit actions', () => {
    let state = reduce(createInitialState(), { type: 'OPEN_ARCA' })
    expect(getNextAffordance(state, manifestFixture)).toBe('focus_bank_i')
    state = reduce(state, { type: 'FOCUS_BANK', bank: 1 })
    expect(getNextAffordance(state, manifestFixture)).toBe('open_cell_iv')
    state = reduce(state, { type: 'FOCUS_CELL', cell: 4 })
    expect(state).toMatchObject({ phase: 'cell_focus', focusedBank: 1, focusedCell: 4 })
    expect(deriveInstrumentView(state)).toBe('cell')
    expect(getNextAffordance(state, manifestFixture)).toBe('deploy_rods')
  })

  it('deploys a stored rod directly into the working rail in one canonical action', () => {
    let state = reduce(createInitialState(), { type: 'OPEN_ARCA' })
    state = reduce(state, { type: 'FOCUS_BANK', bank: 1 })
    state = reduce(state, { type: 'FOCUS_CELL', cell: 4 })
    state = reduce(state, { type: 'DEPLOY_ROD', template: manifestFixture.rod_templates[0] })
    expect(state.rods).toHaveLength(1)
    expect(state.rods[0].location).toBe('workspace')
    expect(state.heldRodId).toBeNull()
    expect(state.phase).toBe('aligning')
    expect(deriveInstrumentView(state)).toBe('working')
  })

  it('retains the older lift/place path as a keyboard/fallback-compatible state transition', () => {
    let state = reduce(createInitialState(), { type: 'OPEN_ARCA' })
    state = reduce(state, { type: 'FOCUS_BANK', bank: 1 })
    state = reduce(state, { type: 'FOCUS_CELL', cell: 4 })
    state = reduce(state, { type: 'RETRIEVE_ROD', template: manifestFixture.rod_templates[0] })
    expect(getNextAffordance(state, manifestFixture)).toBe('place_held_rod')
    state = reduce(state, { type: 'PLACE_HELD_ROD' })
    expect(state.rods[0].location).toBe('workspace')
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
    const state = stateWithPlacedRods()
    expect(isAlignmentReady(state, manifestFixture)).toBe(false)
    expect(getNextAffordance(state, manifestFixture)).toBe('align_rods')
  })

  it('becomes ready only when every physical carrier reaches the manifest read band', () => {
    let state = stateWithPlacedRods()
    for (const rod of state.rods) {
      state = reduce(state, { type: 'MOVE_ROD', instanceId: rod.instance_id, offset: manifestFixture.canonical_read_band - 1 })
    }
    expect(state.phase).toBe('historical_alignment_ready')
    expect(isAlignmentReady(state, manifestFixture)).toBe(true)
    expect(deriveInstrumentView(state)).toBe('tone')
    expect(getNextAffordance(state, manifestFixture)).toBe('engage_tone_ii')
  })

  it('requires the integrated Tone II action before execution and returns focus to the rule afterward', () => {
    let state = stateWithPlacedRods()
    for (const rod of state.rods) state = reduce(state, { type: 'MOVE_ROD', instanceId: rod.instance_id, offset: 0 })
    expect(isExecutionReady(state, manifestFixture)).toBe(false)
    state = reduce(state, { type: 'ENGAGE_TONE' })
    expect(isExecutionReady(state, manifestFixture)).toBe(true)
    expect(deriveInstrumentView(state)).toBe('working')
    expect(getNextAffordance(state, manifestFixture)).toBe('read_transverse')
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

  it('preserves kernel provenance through revelation and can return to the same aligned mechanism', () => {
    let state = stateWithPlacedRods()
    for (const rod of state.rods) state = reduce(state, { type: 'MOVE_ROD', instanceId: rod.instance_id, offset: 0 })
    state = reduce(state, { type: 'ENGAGE_TONE' })
    state = reduce(state, { type: 'EXECUTE' })
    state = reduce(state, { type: 'EXECUTION_SUCCESS', execution: executionFixture })
    expect(deriveInstrumentView(state)).toBe('revelation')
    expect(getNextAffordance(state, manifestFixture)).toBe('inspect_revelation')
    expect(state.execution?.fragment.provenance.transcription_protocol).toContain('TRANSCRIPTION_SPEC')
    expect(state.execution?.fragment.events[0].voices.cantus.provenance.vperm_cell).toBe('C1')
    state = reduce(state, { type: 'RETURN_TO_WORKING' })
    expect(state.execution).toBeNull()
    expect(state.phase).toBe('tonal_resolution')
    expect(isExecutionReady(state, manifestFixture)).toBe(true)
  })

  it('invalidates tone and a revealed result immediately when a physical rod moves', () => {
    let state = stateWithPlacedRods()
    for (const rod of state.rods) state = reduce(state, { type: 'MOVE_ROD', instanceId: rod.instance_id, offset: 0 })
    state = reduce(state, { type: 'ENGAGE_TONE' })
    state = reduce(state, { type: 'EXECUTE' })
    state = reduce(state, { type: 'EXECUTION_SUCCESS', execution: executionFixture })
    state = reduce(state, { type: 'RETURN_TO_WORKING' })
    state = reduce(state, { type: 'MOVE_ROD', instanceId: state.rods[0].instance_id, offset: 1 })
    expect(state.execution).toBeNull()
    expect(state.toneEngaged).toBe(false)
    expect(state.phase).toBe('aligning')
    expect(getNextAffordance(state, manifestFixture)).toBe('align_rods')
  })

  it('records reduced-motion preference in canonical presentation state', () => {
    const state = reduce(createInitialState(), { type: 'SET_REDUCED_MOTION', value: true })
    expect(state.reducedMotion).toBe(true)
  })
})
