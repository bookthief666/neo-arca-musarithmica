import { describe, expect, it } from 'vitest'
import { heldRod, shouldExtendCarriage, targetLane, workspaceOffsets } from './operative'
import { createInitialState, instrumentReducer } from '../instrument/model'
import type { InstrumentAction, InstrumentState } from '../instrument/types'
import { manifestFixture } from '../test/fixtures'

const reduce = (state: InstrumentState, action: InstrumentAction) =>
  instrumentReducer(state, action, manifestFixture)

function atCell(): InstrumentState {
  let state = reduce(createInitialState(), { type: 'OPEN_ARCA' })
  state = reduce(state, { type: 'FOCUS_BANK', bank: 1 })
  return reduce(state, { type: 'FOCUS_CELL', cell: 4 })
}

const holding = (index: number) =>
  reduce(atCell(), { type: 'RETRIEVE_ROD', template: manifestFixture.rod_templates[index] })

describe('operative presentation helpers', () => {
  it('reports no held carrier before one is lifted', () => {
    expect(heldRod(createInitialState())).toBeNull()
    expect(heldRod(atCell())).toBeNull()
  })

  it('resolves the held carrier by canonical instance id', () => {
    const state = holding(0)
    expect(heldRod(state)?.instance_id).toBe(state.heldRodId)
    expect(heldRod(state)?.location).toBe('hand')
  })

  it('wakes exactly the channel the held carrier belongs in', () => {
    expect(targetLane(manifestFixture, atCell())).toBeNull()
    expect(targetLane(manifestFixture, holding(0))).toBe(-1)
    expect(targetLane(manifestFixture, holding(1))).toBe(0)
    expect(targetLane(manifestFixture, holding(2))).toBe(1)
  })

  it('stops cueing a destination once the carrier is seated', () => {
    const seated = reduce(holding(0), { type: 'PLACE_HELD_ROD' })
    expect(targetLane(manifestFixture, seated)).toBeNull()
  })

  it('opens the carriage when a carrier is lifted, not only when one lands', () => {
    expect(shouldExtendCarriage(createInitialState())).toBe(false)
    expect(shouldExtendCarriage(atCell())).toBe(false)
    // The destination must be revealed BEFORE the reader commits to placing.
    expect(shouldExtendCarriage(holding(0))).toBe(true)
  })

  it('keeps the carriage out once rod work has begun', () => {
    const seated = reduce(holding(0), { type: 'PLACE_HELD_ROD' })
    expect(shouldExtendCarriage(seated)).toBe(true)
  })

  it('reports only seated carriers per channel, in manifest order', () => {
    expect(workspaceOffsets(manifestFixture, createInitialState())).toEqual([null, null, null])
    // A carrier in the hand is not in a channel yet.
    expect(workspaceOffsets(manifestFixture, holding(0))).toEqual([null, null, null])

    const seated = reduce(holding(0), { type: 'PLACE_HELD_ROD' })
    expect(workspaceOffsets(manifestFixture, seated))
      .toEqual([seated.rods[0].vertical_offset, null, null])
  })

  it('tracks a seated carrier as it moves between canonical bands', () => {
    let state = reduce(holding(1), { type: 'PLACE_HELD_ROD' })
    state = reduce(state, { type: 'MOVE_ROD', instanceId: state.rods[0].instance_id, offset: 7 })
    expect(workspaceOffsets(manifestFixture, state)).toEqual([null, 7, null])
  })

  it('adds nothing to canonical state', () => {
    const before = JSON.stringify(holding(0))
    const state: InstrumentState = JSON.parse(before)
    heldRod(state)
    targetLane(manifestFixture, state)
    shouldExtendCarriage(state)
    workspaceOffsets(manifestFixture, state)
    expect(JSON.stringify(state)).toBe(before)
  })
})
