import { describe, expect, it } from 'vitest'
import { CARRIAGE, CASE, READER, VIRGA } from './dimensions'
import { VIRGA_TRAVEL, virgaOriginZ } from './scene/stations'
import { MAX_VERTICAL_OFFSET } from '../instrument/model'

/**
 * The carriage has to physically work. A rod plus its own travel must fit the
 * drawer, and every band position must be reachable without the carrier
 * disappearing under the carcass or hanging off the front — these are the
 * failures that only show up as a confusing picture, so they are asserted here.
 */
describe('carriage geometry', () => {
  const drawerBack = CARRIAGE.travel - CARRIAGE.depth / 2
  const drawerFront = CARRIAGE.travel + CARRIAGE.depth / 2
  const caseFront = CASE.depth / 2
  const span = (offset: number) => {
    const origin = CARRIAGE.travel + virgaOriginZ(offset)
    return { back: origin - VIRGA.length / 2, front: origin + VIRGA.length / 2 }
  }

  it('puts the requested band exactly at the reading station', () => {
    for (let offset = 0; offset <= MAX_VERTICAL_OFFSET; offset++) {
      const origin = virgaOriginZ(offset)
      // Band centre in virga-local space, measured foot-first.
      const bandCentre = -VIRGA.length / 2 + (offset + 0.5) * VIRGA.bandLength
      expect(origin + bandCentre).toBeCloseTo(READER.stationZ, 9)
    }
  })

  it('keeps every band position inside the drawer', () => {
    for (let offset = 0; offset <= MAX_VERTICAL_OFFSET; offset++) {
      const { back, front } = span(offset)
      expect(back).toBeGreaterThanOrEqual(drawerBack)
      expect(front).toBeLessThanOrEqual(drawerFront)
    }
  })

  it('keeps the carrier clear of the carcass mouth at the canonical read band', () => {
    // Band 01 is the verified band and the one the instrument actually reads,
    // so it must be fully visible, not half swallowed by the cabinet.
    expect(span(0).back).toBeGreaterThanOrEqual(caseFront)
  })

  it('exposes travel limits that match the canonical offset range', () => {
    expect(VIRGA_TRAVEL.min).toBeCloseTo(virgaOriginZ(MAX_VERTICAL_OFFSET), 9)
    expect(VIRGA_TRAVEL.max).toBeCloseTo(virgaOriginZ(0), 9)
    expect(VIRGA_TRAVEL.max).toBeGreaterThan(VIRGA_TRAVEL.min)
  })

  it('models the instrument at true desk scale for a later XR session', () => {
    // Metres. A cabinet a reader could pick up off a table, not a 30 m prop
    // compensated for by the camera.
    expect(CASE.width).toBeGreaterThan(0.2)
    expect(CASE.width).toBeLessThan(0.4)
    expect(CASE.height).toBeLessThan(0.2)
  })
})
