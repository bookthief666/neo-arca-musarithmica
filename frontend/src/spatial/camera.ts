import { useCallback, useEffect, useMemo, useRef } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import * as THREE from 'three'
import type { InstrumentView } from '../instrument/types'

interface Framing {
  azimuth: number
  elevation: number
  distance: number
  target: [number, number, number]
}

/** Authored macro-workbench poses. They are H1 presentation, never musical state. */
const FRAMING: Record<InstrumentView, Framing> = {
  arca: { azimuth: 0.62, elevation: 0.38, distance: 0.62, target: [0, 0.055, 0] },
  cabinet: { azimuth: 0.44, elevation: 0.4, distance: 0.94, target: [0, 0.095, 0.012] },
  cell: { azimuth: 0.28, elevation: 0.68, distance: 0.66, target: [0, 0.07, 0.015] },
  working: { azimuth: 0.16, elevation: 0.72, distance: 0.44, target: [0, 0.043, 0.16] },
  tone: { azimuth: 0.26, elevation: 0.6, distance: 0.66, target: [0, 0.06, 0.105] },
  revelation: { azimuth: 0.1, elevation: 0.72, distance: 0.56, target: [0, 0.03, 0.245] },
}

const AUTHORED_ASPECT = 1.5
const MIN_ELEVATION = -0.26
const MAX_ELEVATION = 1.36
const MIN_DISTANCE = 0.22
const MAX_DISTANCE = 2.2

export type CameraTransitionReason =
  | 'open-arca'
  | 'enter-cell'
  | 'seat-first-carrier'
  | 'first-revelation'
  | 'reading-position'
  | 'tone-emphasis'
  | 'retry'
  | 'return'
  | 'error'

const MAJOR_TRANSITIONS: Readonly<Record<string, readonly [InstrumentView, InstrumentView]>> = Object.freeze({
  'open-arca': ['arca', 'cabinet'],
  'enter-cell': ['cabinet', 'cell'],
  'seat-first-carrier': ['cell', 'working'],
  'first-revelation': ['working', 'revelation'],
})

/** Pure policy: only four topology changes may reclaim camera framing. */
export function shouldRefocus(
  previous: InstrumentView,
  next: InstrumentView,
  reason: CameraTransitionReason,
): boolean {
  const transition = MAJOR_TRANSITIONS[reason]
  return Boolean(transition && transition[0] === previous && transition[1] === next)
}

function transitionReason(previous: InstrumentView, next: InstrumentView): CameraTransitionReason {
  if (previous === 'arca' && next === 'cabinet') return 'open-arca'
  if (previous === 'cabinet' && next === 'cell') return 'enter-cell'
  if (previous === 'cell' && next === 'working') return 'seat-first-carrier'
  if (previous === 'working' && next === 'revelation') return 'first-revelation'
  if (previous === 'revelation' && next === 'working') return 'return'
  return 'error'
}

export interface OrbitState {
  azimuth: number
  elevation: number
  distance: number
  target: THREE.Vector3
  /** True while the operator, rather than the director, owns the current pose. */
  userDriven: boolean
}

export function useOrbitState(): React.RefObject<OrbitState> {
  return useRef<OrbitState>({
    azimuth: FRAMING.arca.azimuth,
    elevation: FRAMING.arca.elevation,
    distance: FRAMING.arca.distance,
    target: new THREE.Vector3(...FRAMING.arca.target),
    userDriven: false,
  })
}

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
 * Presentation-only camera director. Event inspection, Tone emphasis, errors,
 * retries and return never reclaim the operator's pose. Recentre remains an
 * explicit opt-in and always targets the current canonical view.
 */
export function useCameraDirector(
  orbit: React.RefObject<OrbitState>,
  view: InstrumentView,
  reducedMotion: boolean,
) {
  const camera = useThree((state) => state.camera)
  const size = useThree((state) => state.size)
  const activeFraming = useRef(FRAMING[view])
  const goalTarget = useRef(new THREE.Vector3(...FRAMING[view].target))
  const previousView = useRef(view)
  const aimed = useMemo(() => new THREE.Vector3(), [])

  useEffect(() => {
    const previous = previousView.current
    const nextFraming = FRAMING[view]
    activeFraming.current = nextFraming
    goalTarget.current.set(...nextFraming.target)

    const state = orbit.current
    if (state && previous !== view) {
      const reason = transitionReason(previous, view)
      // A major topology transition may guide the operator. Every other view
      // change yields immediately and freezes the pose until explicit Recentre.
      state.userDriven = !shouldRefocus(previous, view, reason)
    }
    previousView.current = view
  }, [view, orbit])

  useFrame((_, delta) => {
    const state = orbit.current
    if (!state) return
    const goal = activeFraming.current
    const ease = reducedMotion ? 1 : 1 - Math.pow(0.0016, delta)

    if (!state.userDriven) {
      const aspectNow = size.height > 0 ? size.width / size.height : AUTHORED_ASPECT
      const rise = Math.max(0, AUTHORED_ASPECT / Math.max(aspectNow, 0.2) - 1) * 0.045
      aimed.copy(goalTarget.current).y += rise
      state.target.lerp(aimed, ease)
      state.azimuth = THREE.MathUtils.lerp(state.azimuth, goal.azimuth, ease)
      state.elevation = THREE.MathUtils.lerp(state.elevation, goal.elevation, ease)
      const fit = Math.max(1, Math.pow(AUTHORED_ASPECT / Math.max(aspectNow, 0.2), 0.75))
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

/** Explicitly hands the current view back to the director. */
export function useResetView(orbit: React.RefObject<OrbitState>) {
  return useCallback(() => {
    if (orbit.current) orbit.current.userDriven = false
  }, [orbit])
}
