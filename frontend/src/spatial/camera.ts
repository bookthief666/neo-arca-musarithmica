import { useCallback, useEffect, useMemo, useRef } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import * as THREE from 'three'
import type { InstrumentView } from '../instrument/types'

/**
 * THE CAMERA DIRECTOR.
 *
 * Two things have to be true at once: the instrument must be FRAMED — a reader
 * arriving at the carriage should not have to find it — and the reader must
 * still be able to pick the object up and look at its back.
 *
 * So the director owns a default framing per canonical view, and the reader
 * owns an orbit offset on top of it. Changing view re-aims the camera; dragging
 * hands control back to the reader and the director stops pushing until the
 * view changes again. It never fights an active gesture.
 */

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

/** Framing per canonical view. Distances are metres: this is a desk object. */
const FRAMING: Record<InstrumentView, Framing> = {
  // At rest: a three-quarter product view that shows front, side and lid top.
  arca: { azimuth: 0.62, elevation: 0.38, distance: 0.62, target: [0, 0.055, 0] },
  // Opened: pull up and back so the raised lid stays in frame with the interior.
  cabinet: { azimuth: 0.44, elevation: 0.4, distance: 0.94, target: [0, 0.095, 0.012] },
  // Cell IV: closer, steeper, looking down into the compartment deck.
  cell: { azimuth: 0.28, elevation: 0.68, distance: 0.66, target: [0, 0.07, 0.015] },
  // At the carriage: over the drawer, rods filling the frame.
  working: { azimuth: 0.16, elevation: 0.72, distance: 0.40, target: [0, 0.03, 0.155] },
  // Consulting the Tone: include the lid so the Mensa and the rule are both read.
  tone: { azimuth: 0.26, elevation: 0.6, distance: 0.66, target: [0, 0.06, 0.105] },
  // The folio: reveal the result without losing the carriage that printed it.
  revelation: { azimuth: 0.1, elevation: 0.72, distance: 0.56, target: [0, 0.03, 0.245] },
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
  view: InstrumentView,
  reducedMotion: boolean,
) {
  const camera = useThree((s) => s.camera)
  const size = useThree((s) => s.size)
  const goal = useMemo(() => FRAMING[view], [view])
  const goalTarget = useRef(new THREE.Vector3(...goal.target))
  const aimed = useMemo(() => new THREE.Vector3(), [])

  // A view change re-aims the director and takes back control for the move.
  useEffect(() => {
    goalTarget.current.set(...goal.target)
    if (orbit.current) orbit.current.userDriven = false
  }, [goal, orbit])

  useFrame((_, delta) => {
    const state = orbit.current
    if (!state) return

    // Reduced motion: arrive immediately rather than sweeping the reader there.
    const ease = reducedMotion ? 1 : 1 - Math.pow(0.0016, delta)

    // On a tall viewport the extra standoff leaves the instrument riding high,
    // so the look-at point rises with it and the object stays centred.
    const aspectNow = size.height > 0 ? size.width / size.height : AUTHORED_ASPECT
    const rise = Math.max(0, AUTHORED_ASPECT / Math.max(aspectNow, 0.2) - 1) * 0.045
    aimed.copy(goalTarget.current).y += rise
    state.target.lerp(aimed, ease)
    if (!state.userDriven) {
      state.azimuth = THREE.MathUtils.lerp(state.azimuth, goal.azimuth, ease)
      state.elevation = THREE.MathUtils.lerp(state.elevation, goal.elevation, ease)
      // The framings are authored for a landscape viewport. A camera's fov is
      // VERTICAL, so on a tall phone the horizontal field collapses and a
      // distance tuned on a desktop puts the cabinet through both edges. Back
      // off by however much narrower this viewport is than the authored one.
      const aspect = size.height > 0 ? size.width / size.height : AUTHORED_ASPECT
      // ^0.75 rather than linear: backing off by the full ratio is correct for
      // a flat card but over-corrects for a deep object, leaving it tiny.
      // Capped, because uncapped it reached 2.42x on a folded Fold, which put
      // the cabinet at 44% of the frame width with most of the screen empty
      // above and below it — and, in the open framing, past the fog.
      const fit = THREE.MathUtils.clamp(
        Math.pow(AUTHORED_ASPECT / Math.max(aspect, 0.2), 0.75), 1, MAX_ASPECT_FIT,
      )
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
