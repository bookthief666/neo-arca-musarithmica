import { describe, expect, it } from 'vitest'
import { lectioMechanismState, toneMechanismState } from './mechanismState'

/**
 * The two final mechanisms are PERSISTENT: they exist from the moment the
 * instrument is open and change state, rather than being conjured at the
 * moment they become useful. A control that appears from nowhere cannot be
 * the thing that taught you the step was coming.
 */
describe('Tone II selector state', () => {
  it('is dormant until the rule reads a continuous band', () => {
    expect(toneMechanismState(false, false)).toBe('dormant')
  })

  it('wakes on canonical concord, and only then', () => {
    expect(toneMechanismState(true, false)).toBe('available')
  })

  it('stays engaged once taken', () => {
    expect(toneMechanismState(true, true)).toBe('engaged')
    // Canonical state is the authority: if the reducer still says engaged
    // while alignment has lapsed, the selector must not silently disagree.
    expect(toneMechanismState(false, true)).toBe('engaged')
  })
})

describe('LECTIO lever state', () => {
  it('is locked while the reading is not canonically ready', () => {
    expect(lectioMechanismState(false, 'aligning', null)).toBe('dormant')
    expect(lectioMechanismState(false, 'historical_alignment_ready', null)).toBe('dormant')
  })

  it('unlocks only once execution is canonically ready', () => {
    expect(lectioMechanismState(true, 'tonal_resolution', null)).toBe('available')
  })

  it('shows the machine working while it reads', () => {
    expect(lectioMechanismState(true, 'executing', null)).toBe('busy')
  })

  it('offers a retry when a reading fails but the disposition survives', () => {
    expect(lectioMechanismState(true, 'error', 'rejected')).toBe('fault')
  })

  it('does not offer a retry the instrument could not honour', () => {
    // Readiness is gone, so the lever is locked even though an error stands:
    // the next affordance belongs to whatever the reducer actually wants.
    expect(lectioMechanismState(false, 'error', 'rejected')).toBe('dormant')
  })
})
