import { CELL_IV, READER, VIRGA } from '../dimensions'

/**
 * Where a virga's ORIGIN must sit for band `offset` to lie in the reading gap.
 *
 * Bands run FOOT-first: band 01 is at the -Z end of the strip, furthest from
 * the brass finial. That is deliberate. The finial is the grip, the reading gap
 * is the mechanism, and putting them at opposite ends means a hand reaching for
 * the grip never covers the band being read — the same reason a slide rule's
 * cursor and its handle are not in the same place.
 *
 * Band k's centre in virga-local space is therefore -L/2 + (k + 0.5) * band.
 * Solving for the origin that puts that centre at the reading station keeps the
 * discrete canonical offsets and the continuous geometry in exact agreement:
 * the rod is never "approximately" on a band.
 */
export function virgaOriginZ(offset: number): number {
  return READER.stationZ + VIRGA.length / 2 - (offset + 0.5) * VIRGA.bandLength
}

/** Travel limits of a virga sliding in its channel, in carriage-local Z. */
export const VIRGA_TRAVEL = {
  min: virgaOriginZ(VIRGA.bandCount - 1),
  max: virgaOriginZ(0),
}

/**
 * World Z of the Cell IV cover. Closed, it lies over the cell; open, it has
 * retracted very nearly its own length into the slot beneath the raised bank
 * rail, carrying its front edge past the rearmost point of a stored carrier.
 *
 * The travel is short of the cover's full depth by the closed-position stop,
 * and its rear edge finishes clear of the carcass back wall. Those two
 * clearances are what make the motion physically possible at all: with the
 * rail sitting directly on the deck, as it did in M1.2, the cover jammed
 * against its front face after 16 mm.
 */
export function cellCoverTarget(open: boolean): number {
  return open ? CELL_IV.centreZ - CELL_IV.coverTravel : CELL_IV.centreZ
}
