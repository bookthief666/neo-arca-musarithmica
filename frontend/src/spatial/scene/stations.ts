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
 * The Cell IV cover's two fold angles, in radians: the inner leaf's lift about
 * the cell's rear edge, and the outer leaf's fold relative to it.
 *
 * The cover folds rather than slides because a slide cannot exist here. Full
 * rearward retraction would need the cell's centre at z >= +76 mm, while a
 * stored virga's finial must clear the front apron, which caps the centre at
 * +28 mm; a bi-parting slide fails the same way. Folded in two, the cover
 * needs 52 mm of headroom against the 54 mm the carcass has.
 *
 * Closed, both leaves lie flat. Open, the inner leaf stands up just short of
 * upright and the outer leaf lies back down against it, so the pair reads as
 * one board doubled over behind the mortises.
 */
export function cellCoverAngles(open: boolean): { inner: number; outer: number } {
  if (!open) return { inner: 0, outer: 0 }
  return { inner: -CELL_IV.coverOpenAngle, outer: Math.PI - 0.16 }
}

/** Height the folded cover reaches above the deck, for clearance checks. */
export function cellCoverFoldedHeight(): number {
  return (CELL_IV.depth / 2) * Math.sin(CELL_IV.coverOpenAngle)
}
