/**
 * ARCA DIMENSIONS — one source of truth for the spatial instrument.
 *
 * SCALE CONVENTION: 1 three.js unit = 1 metre.
 *
 * These dimensions are H1 reconstruction values, not measurements of a surviving
 * Kircher apparatus. Historical musical content remains in the verified kernel
 * and bridge data.
 */
const mm = (value: number) => value / 1000

export const CASE = {
  width: mm(280),
  depth: mm(180),
  height: mm(120),
  bodyHeight: mm(98),
  lidHeight: mm(22),
  wall: mm(10),
  plinth: mm(8),
} as const

export const FOOT = {
  radius: mm(9),
  height: mm(10),
  inset: mm(26),
} as const

export const LID = {
  openAngle: -Math.PI * (70 / 180),
  closedAngle: 0,
  frame: mm(14),
  hingeRadius: mm(5),
  hingeLength: mm(34),
} as const

export const BODY_TOP = CASE.plinth + CASE.bodyHeight
export const FLOOR_TOP = CASE.plinth + CASE.wall
export const DECK_TOP = mm(52)
export const DECK_THICKNESS = mm(14)
export const SLOT_DEPTH = mm(12)

export const INTERIOR = {
  width: CASE.width - CASE.wall * 2,
  depth: CASE.depth - CASE.wall * 2,
  divider: mm(4),
  railDepth: mm(24),
  railHeight: mm(26),
} as const

/** Cell IV contains one operative critical-edition carrier bed. */
export const CELL_IV = {
  width: mm(96),
  depth: mm(104),
  carrierBedWidth: mm(76),
} as const

/**
 * One H1 critical-edition carrier. There are no physical musical-band detents:
 * the six event positions belong to the inspection reader, not to six variants
 * of the carrier itself.
 */
export const VIRGA = {
  length: mm(80),
  width: mm(64),
  printableWidth: mm(60),
  thickness: mm(8),
  finialRadius: mm(7),
  collarRadius: mm(6),
  collarHeight: mm(4),
} as const

/** Pull-out workbench. Only the central bed is operative in this corpus slice. */
export const CARRIAGE = {
  width: mm(252),
  depth: mm(158),
  height: mm(26),
  travel: mm(165),
  y: FLOOR_TOP,
  wall: mm(5),
  activeChannelWidth: mm(76),
  capacityGap: mm(10),
} as const

/** Presentation-only reader structure; event detents are defined in stations.ts. */
export const READER = {
  stationZ: mm(-10),
  barHeight: mm(10),
  barDepth: mm(15),
} as const

export const FOLIO = {
  width: mm(150),
  height: mm(92),
} as const
