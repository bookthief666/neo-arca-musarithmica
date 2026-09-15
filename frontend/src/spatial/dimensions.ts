/**
 * ARCA DIMENSIONS — one source of truth for the whole spatial instrument.
 *
 * SCALE CONVENTION: 1 three.js unit = 1 METRE.
 *
 * This is deliberate rather than convenient. WebXR reference spaces are
 * expressed in metres, so an object modelled at true metric scale here drops
 * into an immersive session at the right size with no conversion layer and no
 * root rescale. A reader meeting this cabinet in VR meets a desk-scale object
 * because it IS a desk-scale object.
 *
 * PROVENANCE OF THESE NUMBERS — H1, not H0.
 * The overall envelope follows the M1.2 construction sheet (280 × 180 × 120 mm
 * closed). That sheet is a generated concept board: its figures are design
 * intent for a plausible desk instrument, NOT measurements of any surviving
 * Kircher apparatus, and nothing here should be cited as historical evidence.
 * Everything in this file is restrained physical reconstruction (H1). The
 * musical content the cabinet carries remains H0 and lives in the kernel.
 */

/** Millimetres to metres, so the numbers below can be written as the sheet reads them. */
const mm = (value: number) => value / 1000

export const CASE = {
  width: mm(280),
  depth: mm(180),
  /** Closed height including the lid. */
  height: mm(120),
  /** Carcass height without the lid. */
  bodyHeight: mm(98),
  lidHeight: mm(22),
  wall: mm(10),
  /** Plinth the carcass stands on. */
  plinth: mm(8),
} as const

export const FOOT = {
  radius: mm(9),
  height: mm(10),
  /** Inset of each foot's centre from the case corner. */
  inset: mm(26),
} as const

/** The lid swings about its rear top edge. */
export const LID = {
  /** Open angle, refined in-browser against the construction sheet's side view. */
  openAngle: -Math.PI * (70 / 180),
  closedAngle: 0,
  /** Thickness of the lid's frame members around the Mensa. */
  frame: mm(14),
  hingeRadius: mm(5),
  hingeLength: mm(34),
} as const

/**
 * WORLD HEIGHTS.
 *
 * Every horizontal surface in the carcass is pinned here, in world metres from
 * the ground plane, because the drawer and the storage deck have to stack
 * inside 98 mm of carcass without intersecting. Deriving them separately is how
 * a drawer ends up passing through the floor it sits under.
 *
 *   0.106  ── carcass top / lid hinge line
 *   0.052  ── deck top        (virgae are stored on this)
 *   0.046  ── slot floor      (6 mm recess cut into the deck)
 *   0.044  ── deck underside == drawer top
 *   0.018  ── carcass floor board top == drawer bottom
 *   0.008  ── plinth top
 *   0      ── the desk
 */
export const BODY_TOP = CASE.plinth + CASE.bodyHeight
export const FLOOR_TOP = CASE.plinth + CASE.wall
export const DECK_TOP = mm(52)
export const DECK_THICKNESS = mm(14)
/* 8 mm, not 12 mm. At a 12 mm recess a 9 mm carrier's top face lay 3 mm BELOW
   deck level and only 0.5 mm of its finial stood proud, so opening Cell IV
   revealed what looked like an empty box. At 8 mm the carrier stands 1 mm
   proud and the finial crown 4.5 mm proud: visibly stored objects. */
export const SLOT_DEPTH = mm(8)

export const INTERIOR = {
  /** Clear width and depth inside the four walls. */
  width: CASE.width - CASE.wall * 2,
  depth: CASE.depth - CASE.wall * 2,
  /** Thickness of the wooden dividers between compartments. */
  divider: mm(4),
  /** Depth of the bank nameplate rail along the back wall. */
  railDepth: mm(24),
  railHeight: mm(26),
} as const

/**
 * Cell IV: the one operative receptacle. The three virgae are stored LYING in
 * slots that run front-to-back — the same attitude they take in the carriage
 * channels below, so lifting one out and seating it is a single clear motion
 * rather than a rotation the reader has to interpret.
 */
export const CELL_IV = {
  /** Wide enough for three mortises at the carriage's channel pitch. */
  width: mm(116),
  /* A virga is 103.6 mm end to end once its collar and finial are counted, so
     the cell cannot be shorter than this and still contain one. */
  depth: mm(104),
  /* As far back as the deck allows: the cell's rear edge sits flush with the
     deck's back edge at -56 mm. Forward of this the carcass front apron, which
     stands 54 mm above the deck only 80 mm away, hides the carriers entirely. */
  centreZ: mm(-4),
  slotWidth: mm(24),
  /** Matches the carriage's channel pitch, so a carrier drops straight down
      into its channel instead of fanning sideways on the way. */
  slotPitch: mm(42),
  /**
   * THE COVER IS A BI-FOLD, NOT A SLIDE.
   *
   * The approved design asked for a plate that slides rearward. Measured
   * against this carcass it cannot exist at any cell depth: full retraction
   * needs the cell's centre at z >= +76 mm, while a stored virga's finial has
   * to clear the front apron, which caps the centre at +28 mm. A two-leaf
   * bi-parting slide fails the same way once the cell is long enough to hold a
   * virga at all. A single rear-hinged flap needs 104 mm of headroom and there
   * are 54 mm.
   *
   * Folded in two it needs 52 mm, and fits. So the cover hinges at the cell's
   * rear edge and folds back on itself, standing as a double panel behind the
   * mortises — the smallest correction that keeps a real, physical cover.
   */
  coverThickness: mm(4),
  /** Lift of the inner leaf, short of upright so the stack leans clear. */
  coverOpenAngle: Math.PI * (82 / 180),
  coverHandleDepth: mm(7),
  /* Touch volume. At the Fold's working framing 1 mm of world is about
     0.9 CSS px, so a comfortable 44 px target needs roughly 50 mm. */
  hitSize: mm(50),
} as const

/**
 * A virga. Ten bands run down its length; the canonical vertical_offset picks
 * which band stands under the transverse reader.
 */
export const VIRGA = {
  /* A carrier travels its own length minus one band along the channel, so the
     rod plus its full travel has to FIT the drawer: 70 mm of rod plus 63 mm of
     travel sits inside a 158 mm drawer with room at both ends. At 88 mm it ran
     off the front at high offsets and hid under the carcass at low ones. */
  length: mm(70),
  /* Chunky on purpose. A carrier has to look like something a hand could close
     on — at 16 x 6 mm it rendered as a paper sliver, which is the opposite of
     the affordance this object needs to advertise. */
  width: mm(20),
  thickness: mm(9),
  finialRadius: mm(8),
  collarRadius: mm(6),
  collarHeight: mm(4),
  bandCount: 10,
  /** Length of one band along the virga. */
  get bandLength() { return this.length / this.bandCount },
} as const

/** The pull-out carriage, running forward on rails out of the carcass front. */
export const CARRIAGE = {
  width: mm(252),
  depth: mm(158),
  height: mm(26),
  /** How far the drawer travels out of the case. */
  travel: mm(165),
  /** World height of the drawer's floor. */
  y: FLOOR_TOP,
  wall: mm(5),
  /* 42 mm, not 32. At 32 the three 24 mm channels and their 4 mm guide lips
     tiled the drawer edge to edge with nothing between them, so a band index
     had physically nowhere to go — the first attempt at one rendered through
     the lips and the neighbouring channel. 42 leaves a clear 10 mm gutter
     beside each channel for the scale to be let into. */
  channelPitch: mm(42),
  channelWidth: mm(24),
  channelDepth: mm(10),
  /* Touch volumes over a channel. A 24 mm channel is about 21 CSS px at the
     Fold's working framing; these reach roughly 44. */
  hitWidth: mm(30),
  hitHeight: mm(46),
} as const

/**
 * The transverse reader: a brass bar crossing all three channels at a fixed
 * station. A virga slides along its own length beneath it; whichever band lies
 * under the reader is the band being read.
 */
export const READER = {
  /** Z of the reading station, in carriage-local space. Placed so that with
      the drawer out, every band position lies clear of the carcass mouth and
      inside the drawer — the rule must read where the reader can see it. */
  stationZ: mm(-10),
  barHeight: mm(10),
  barDepth: mm(15),
} as const

/** Where the revelation folio emerges from, at the front of the carriage. */
export const FOLIO = {
  width: mm(150),
  height: mm(92),
} as const
