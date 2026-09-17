import { describe, expect, it } from 'vitest'
import { shouldRefocus } from './camera'

describe('macro-workbench camera policy', () => {
  it('does not refocus for event-reader movement', () => {
    expect(shouldRefocus('working', 'working', 'reading-position')).toBe(false)
  })

  it.each([
    ['arca', 'cabinet', 'open-arca'],
    ['cabinet', 'cell', 'enter-cell'],
    ['cell', 'working', 'seat-first-carrier'],
    ['working', 'revelation', 'first-revelation'],
  ] as const)('permits the major topology transition %s → %s for %s', (previous, next, reason) => {
    expect(shouldRefocus(previous, next, reason)).toBe(true)
  })

  it.each([
    ['working', 'working', 'tone-emphasis'],
    ['working', 'working', 'error'],
    ['revelation', 'working', 'retry'],
    ['revelation', 'working', 'return'],
  ] as const)('preserves the operator pose for %s → %s (%s)', (previous, next, reason) => {
    expect(shouldRefocus(previous, next, reason)).toBe(false)
  })

  it('does not let a topology reason reframe the wrong view transition', () => {
    expect(shouldRefocus('revelation', 'working', 'seat-first-carrier')).toBe(false)
    expect(shouldRefocus('cell', 'revelation', 'first-revelation')).toBe(false)
  })
})
