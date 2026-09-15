import { useCallback, useEffect, useMemo, useRef } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import * as THREE from 'three'
import type { InstrumentState } from '../instrument/types'

/**
 * THE CAMERA DIRECTOR.
 *
 * Two things have to be true at once: the instrument must be FRAMED — a reader
 * arriving at the carriage should not have to find it — and the reader must
 * still be able to pick the object up and look at its back.
 *
 * So the director owns a default framing, and the reader owns an orbit offset
 * on top of it. Dragging hands control back to the reader and the director
 * stops pushing until the framing itself changes. It never fights a gesture.
 *
 * CAMERA INTERVENTION IS NOT SEMANTIC VIEW.
 *
 * M1.2 drove this from InstrumentView, which has six values, so the camera
 * moved every time the instrument changed its mind about what it was doing:
 * lifting a virga cut away from the cell to the drawer, reaching concord threw
 * the camera back out to the lid, and engaging the Tone dragged it in again.
 * Three cuts in the middle of one continuous manual operation, and the reader
 * loses the thread of where anything is.
 *
 * A camera mode is a change in what the instrument physically IS, not in what
 * it is thinking about. There are only three such changes: the box opens, the
 * first carrier reaches the carriage, and the folio appears. Everything else —
 * Bank I, Cell IV, retrieval, the second and third placements, sliding bands,
 * concord, Tone II — happens without the camera moving at all.
 */

/** The only four framings the director is allowed to intervene with. */
export type CameraMode = 'arca' | 'open' | 'working' | 'revelation'

/**
 * Pure, and derived from canonical state alone. No camera field is added to
 * InstrumentState: the presence of a seated rod IS the 0 -> 1 transition that
 * moves the reader to the carriage, and it stays true thereafter, so the
 * second and third retrievals cannot drop the framing back.
 */
export function deriveCameraMode(state: InstrumentState): CameraMode {
  if (state.phase === 'dormant') return 'arca'
  if (state.phase === 'revealed' && state.execution) return 'revelation'
  if (state.rods.some((rod) => rod.location === 'workspace')) return 'working'
  return 'open'
}

interface Framing {
  /** Horizontal angle, radians. 0 looks at the front of the cabinet. */
  azimuth: number
  /** Vertical angle, radians above the horizon. */
  elevation: number
  /** Distance from the target, metres. */
  distance: number
  /** Point the camera looks at, metres. */
  target: [number, number, number]
}

/** Framing per intervention mode. Distances are metres: this is a desk object. */
const FRAMING: Record<CameraMode, Framing> = {
  // At rest: a three-quarter product view that shows front, side and lid top.
  arca: { azimuth: 0.62, elevation: 0.38, distance: 0.62, target: [0, 0.055, 0] },
  // Opened: steep, because the carcass front apron stands 54 mm above the deck
  // only 80 mm in front of it. Below about 60 degrees of elevation that apron
  // hides the storage deck completely — at M1.2's 0.4 rad the reader was told
  // to take a virga while looking at the lid and a wooden wall.
  open: { azimuth: 0.34, elevation: 0.93, distance: 0.60, target: [0, 0.058, 0.004] },
  // At the carriage: the drawer AND the deck above it in one frame, because
  // the second and third carriers are still lifted out of the cell from here.
  working: { azimuth: 0.2, elevation: 0.88, distance: 0.64, target: [0, 0.042, 0.07] },
  // The folio: reveal the result without losing the carriage that printed it.
  revelation: { azimuth: 0.1, elevation: 0.7, distance: 0.66, target: [0, 0.035, 0.18] },
}

/** Aspect the framings above were composed at. */
const AUTHORED_ASPECT = 1.5

const MIN_ELEVATION = -0.26
const MAX_ELEVATION = 1.36
const MIN_DISTANCE = 0.22
const MAX_DISTANCE = 2.2
/** Ceiling on the tall-viewport standoff. See the note at its use site. */
const MAX_ASPECT_FIT = 1.8

export interface OrbitState {
  azimuth: number
  elevation: number
  distance: number
  target: THREE.Vector3
  /** Set while the reader is driving the camera, so the director yields. */
  userDriven: boolean
}

export function useOrbitState(): React.RefObject<OrbitState> {
  const ref = useRef<OrbitState>({
    azimuth: FRAMING.arca.azimuth,
    elevation: FRAMING.arca.elevation,
    distance: FRAMING.arca.distance,
    target: new THREE.Vector3(...FRAMING.arca.target),
    userDriven: false,
  })
  return ref
}

/** Apply a drag, in radians per pixel scaled by viewport size. */
export function orbitBy(state: OrbitState, dx: number, dy: number) {
  state.azimuth += dx
  state.elevation = THREE.MathUtils.clamp(state.elevation + dy, MIN_ELEVATION, MAX_ELEVATION)
  state.userDriven = true
}

export function dollyBy(state: OrbitState, factor: number) {
  state.distance = THREE.MathUtils.clamp(state.distance * factor, MIN_DISTANCE, MAX_DISTANCE)
  state.userDriven = true
}

/**
 * Drives the camera each frame. Runs entirely outside React state: a camera
 * that re-rendered the tree every frame would make the whole scene cost a
 * React commit per frame, which is exactly what a Quest cannot afford.
 */
export function useCameraDirector(
  orbit: React.RefObject<OrbitState>,
  mode: CameraMode,
  reducedMotion: boolean,
) {
  const camera = useThree((s) => s.camera)
  const size = useThree((s) => s.size)
  const goal = useMemo(() => FRAMING[mode], [mode])
  const goalTarget = useRef(new THREE.Vector3(...goal.target))
  const aimed = useMemo(() => new THREE.Vector3(), [])

  // Only a MODE change re-aims the director and takes back control for the
  // move. Once the reader has orbited, the director yields until either the
  // instrument physically changes or Recentre is pressed.
  useEffect(() => {
    goalTarget.current.set(...goal.target)
    if (orbit.current) orbit.current.userDriven = false
  }, [goal, orbit])

  useFrame((_, delta) => {
    const state = orbit.current
    if (!state) return

    // Reduced motion: arrive immediately rather than sweeping the reader there.
    const ease = reducedMotion ? 1 : 1 - Math.pow(0.0016, delta)

    // The framings are authored for a landscape viewport. A camera's fov is
    // VERTICAL, so on a tall phone the horizontal field collapses and a
    // distance tuned on a desktop puts the cabinet through both edges. Back
    // off by however much narrower this viewport is than the authored one.
    //
    // ^0.75 rather than linear: backing off by the full ratio is correct for a
    // flat card but over-corrects for a deep object, leaving it tiny. And
    // capped, because uncapped it reached 2.42x on a folded Fold, which put the
    // cabinet at 44% of the frame width with most of the screen empty around
    // it — and, in the open framing, past the fog's far plane entirely.
    const aspect = size.height > 0 ? size.width / size.height : AUTHORED_ASPECT
    const fit = THREE.MathUtils.clamp(
      Math.pow(AUTHORED_ASPECT / Math.max(aspect, 0.2), 0.75), 1, MAX_ASPECT_FIT,
    )

    // The extra standoff leaves the instrument riding high in a tall frame, so
    // the aim point rises with it. It rises by the SAME capped factor: driven
    // by the uncapped ratio it lifted the aim 101 mm on a folded Fold and hung
    // the cabinet off the bottom of the screen.
    aimed.copy(goalTarget.current).y += (fit - 1) * 0.045
    state.target.lerp(aimed, ease)
    if (!state.userDriven) {
      state.azimuth = THREE.MathUtils.lerp(state.azimuth, goal.azimuth, ease)
      state.elevation = THREE.MathUtils.lerp(state.elevation, goal.elevation, ease)
      state.distance = THREE.MathUtils.lerp(state.distance, goal.distance * fit, ease)
    }

    const cosE = Math.cos(state.elevation)
    camera.position.set(
      state.target.x + state.distance * cosE * Math.sin(state.azimuth),
      state.target.y + state.distance * Math.sin(state.elevation),
      state.target.z + state.distance * cosE * Math.cos(state.azimuth),
    )
    camera.lookAt(state.target)
  })
}

/** Restore the director's framing for the current view. */
export function useResetView(orbit: React.RefObject<OrbitState>) {
  return useCallback(() => {
    if (orbit.current) orbit.current.userDriven = false
  }, [orbit])
}
