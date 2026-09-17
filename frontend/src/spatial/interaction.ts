import type { ThreeEvent } from '@react-three/fiber'
import * as THREE from 'three'

/**
 * INPUT TRANSPORT ABSTRACTION.
 *
 * M1.2 drives the instrument with pointer and touch. A later WebXR milestone
 * will drive the SAME object verbs with a controller ray or a tracked hand.
 * Nothing below mentions a mouse, a client coordinate, or a DOM event: a verb
 * carries a ray, a world point and a pointer identity, all of which an XR
 * source can supply just as well as a pointer event can.
 *
 * Keeping this seam honest now is the difference between adding an XR session
 * later and rewriting every interaction later.
 */

/** The object verbs the instrument understands, whatever the input device. */
export type GrabVerb = 'select' | 'grab' | 'move' | 'release' | 'cancel'

export interface SpatialPointer {
  /** Stable id for this pointer/controller/hand for the life of a gesture. */
  id: number
  /** Ray in world space. In XR this is the controller ray or the gaze/pinch ray. */
  ray: THREE.Ray
  /** Best current world-space point of interest for the gesture. */
  point: THREE.Vector3
}

export interface GrabHandlers {
  onSelect?: (pointer: SpatialPointer) => void
  onGrab?: (pointer: SpatialPointer) => void
  onMove?: (pointer: SpatialPointer) => void
  onRelease?: (pointer: SpatialPointer) => void
}

/** Lift the device-independent part out of an R3F pointer event. */
export function toSpatialPointer(event: ThreeEvent<PointerEvent>): SpatialPointer {
  return {
    id: event.pointerId,
    ray: event.ray.clone(),
    point: event.point ? event.point.clone() : new THREE.Vector3(),
  }
}

/**
 * Project a pointer's ray onto a line in world space and return how far along
 * that line it lands, clamped to the segment.
 *
 * This is how a constrained part is dragged: a virga does not follow the
 * pointer freely, it slides along its own channel axis and nowhere else. The
 * maths is identical whether the ray came from a fingertip on glass or from a
 * controller held in the air.
 */
export function projectRayOntoAxis(
  ray: THREE.Ray,
  origin: THREE.Vector3,
  axis: THREE.Vector3,
  min: number,
  max: number,
): number {
  const direction = axis.clone().normalize()
  // Closest approach between the pointer ray and the constraint line.
  const w0 = new THREE.Vector3().subVectors(ray.origin, origin)
  const a = ray.direction.dot(ray.direction)
  const b = ray.direction.dot(direction)
  const c = direction.dot(direction)
  const d = ray.direction.dot(w0)
  const e = direction.dot(w0)
  const denominator = a * c - b * b
  // Parallel ray: nothing sensible to project onto, so hold position.
  if (Math.abs(denominator) < 1e-9) return THREE.MathUtils.clamp(-e / c, min, max)
  const t = (a * e - b * d) / denominator
  return THREE.MathUtils.clamp(t, min, max)
}

/** Snap a continuous position to the nearest of N evenly spaced detents. */
export function snapToDetent(value: number, min: number, max: number, count: number): number {
  if (count <= 1) return 0
  const span = max - min
  const normalised = span === 0 ? 0 : (value - min) / span
  return THREE.MathUtils.clamp(Math.round(normalised * (count - 1)), 0, count - 1)
}

/** The origin is world-space; the projected scalar and limits stay local. */
export function projectRayToLocalDetent(
  ray: THREE.Ray,
  worldOrigin: THREE.Vector3,
  worldAxis: THREE.Vector3,
  minLocal: number,
  maxLocal: number,
  count: number,
): number {
  const local = projectRayOntoAxis(ray, worldOrigin, worldAxis, minLocal, maxLocal)
  return snapToDetent(local, minLocal, maxLocal, count)
}
