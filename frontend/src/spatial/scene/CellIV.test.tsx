import { describe, expect, it } from 'vitest'
import { CASE, CELL_IV, DECK_TOP, INTERIOR, SLOT_DEPTH, VIRGA } from '../dimensions'
import { cellCoverTarget } from './stations'

describe('Cell IV cover', () => {
  it('has deterministic closed and open travel', () => {
    expect(cellCoverTarget(false)).toBe(CELL_IV.centreZ)
    expect(cellCoverTarget(true)).toBe(CELL_IV.centreZ - CELL_IV.coverTravel)
  })

  it('retracts far enough to uncover the whole slot run', () => {
    const front = CELL_IV.centreZ + CELL_IV.depth / 2
    const virgaBack = CELL_IV.centreZ - VIRGA.length / 2
    // Once open, the cover's front edge must have passed behind the rearmost
    // point of a stored carrier, or the reveal hides the thing it reveals.
    expect(front - CELL_IV.coverTravel).toBeLessThanOrEqual(virgaBack)
  })

  it('stops clear of the carcass back wall when fully retracted', () => {
    const backWall = -CASE.depth / 2 + CASE.wall
    const coverRearWhenOpen = CELL_IV.centreZ - CELL_IV.depth / 2 - CELL_IV.coverTravel
    expect(coverRearWhenOpen).toBeGreaterThan(backWall)
  })

  it('passes beneath the raised bank rail rather than through it', () => {
    // The M1.2 rail sat ON the deck, so a cover at deck level struck its front
    // face after 16 mm. The plinth is what makes the specified motion possible.
    const coverTop = DECK_TOP + CELL_IV.coverLift + CELL_IV.coverThickness
    expect(DECK_TOP + INTERIOR.railLift).toBeGreaterThan(coverTop)
  })

  it('leaves a stored carrier and its finial standing proud of the deck', () => {
    const carrierTop = DECK_TOP - SLOT_DEPTH + VIRGA.thickness
    const finialTop = DECK_TOP - SLOT_DEPTH + VIRGA.thickness / 2 + VIRGA.finialRadius
    expect(carrierTop).toBeGreaterThan(DECK_TOP)
    expect(finialTop).toBeGreaterThan(DECK_TOP + 0.003)
    // ...and the cover must still clear them.
    expect(DECK_TOP + CELL_IV.coverLift).toBeGreaterThan(finialTop)
  })
})
