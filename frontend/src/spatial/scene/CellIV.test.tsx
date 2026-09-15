import { describe, expect, it } from 'vitest'
import {
  BODY_TOP, CASE, CELL_IV, DECK_TOP, INTERIOR, SLOT_DEPTH, VIRGA,
} from '../dimensions'
import { cellCoverAngles, cellCoverFoldedHeight } from './stations'
import { VIRGA_HEAD_REACH } from './Virga'

const deckBackZ = -CASE.depth / 2 + CASE.wall + INTERIOR.railDepth
const apronInnerZ = CASE.depth / 2 - CASE.wall
const headroom = BODY_TOP - DECK_TOP

/**
 * These are the clearances that decide whether Cell IV can physically open at
 * all. The approved design asked for a sliding cover; it cannot exist in this
 * carcass at any cell depth, and the arithmetic below is what proves it. They
 * are pinned so that a later change to the case, the deck, the cell or the
 * virga cannot quietly reintroduce a mechanism that does not fit.
 */
describe('Cell IV cover', () => {
  it('lies flat when closed and folds double when open', () => {
    expect(cellCoverAngles(false)).toEqual({ inner: 0, outer: 0 })
    const open = cellCoverAngles(true)
    expect(open.inner).toBeLessThan(0)
    expect(Math.abs(open.outer)).toBeGreaterThan(Math.PI / 2)
  })

  it('records why the specified sliding cover cannot be built here', () => {
    // Full rearward retraction needs the cell's centre this far forward...
    const neededCentre = -CASE.depth / 2 + CASE.wall + CELL_IV.depth + CELL_IV.depth / 2
    // ...but a stored virga's finial has to clear the front apron.
    const finialCap = apronInnerZ - VIRGA_HEAD_REACH
    expect(neededCentre).toBeGreaterThan(finialCap)
  })

  it('fits the folded cover inside the carcass headroom', () => {
    expect(cellCoverFoldedHeight()).toBeLessThan(headroom)
  })

  it('folds clear of the bank rail behind it', () => {
    // The fold axis is the cell's rear edge; the rail is behind that line.
    expect(CELL_IV.centreZ - CELL_IV.depth / 2).toBeGreaterThanOrEqual(deckBackZ)
  })

  it('is long enough to contain a whole virga, finial included', () => {
    expect(CELL_IV.depth).toBeGreaterThanOrEqual(VIRGA_HEAD_REACH * 2)
  })

  it('keeps a stored virga clear of the carcass front apron', () => {
    expect(CELL_IV.centreZ + VIRGA_HEAD_REACH).toBeLessThanOrEqual(apronInnerZ)
  })

  it('leaves a stored carrier and its finial standing proud of the deck', () => {
    const carrierTop = DECK_TOP - SLOT_DEPTH + VIRGA.thickness
    const finialTop = DECK_TOP - SLOT_DEPTH + VIRGA.thickness / 2 + VIRGA.finialRadius
    expect(carrierTop).toBeGreaterThan(DECK_TOP)
    expect(finialTop).toBeGreaterThan(DECK_TOP + 0.003)
  })
})
