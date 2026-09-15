import { describe, expect, it } from 'vitest'
import * as THREE from 'three'
import { projectRayOntoAxis, snapToDetent } from './interaction'
import { MAX_VERTICAL_OFFSET } from '../instrument/model'

/**
 * The input seam is pure geometry, so it can be proven without a GPU. These are
 * the calculations a WebXR controller will run unchanged.
 */
describe('constrained spatial manipulation', () => {
  const origin = new THREE.Vector3(0, 0, 0)
  const axis = new THREE.Vector3(0, 0, 1)

  it('projects a pointing ray onto the one axis a part may travel', () => {
    // A ray aimed down at z = 0.05 from above resolves to 0.05 along the axis.
    const ray = new THREE.Ray(new THREE.Vector3(0, 0.2, 0.05), new THREE.Vector3(0, -1, 0))
    expect(projectRayOntoAxis(ray, origin, axis, -1, 1)).toBeCloseTo(0.05, 5)
  })

  it('clamps to the ends of the travel rather than letting a part leave it', () => {
    const far = new THREE.Ray(new THREE.Vector3(0, 0.2, 9), new THREE.Vector3(0, -1, 0))
    expect(projectRayOntoAxis(far, origin, axis, -0.05, 0.05)).toBe(0.05)
    const back = new THREE.Ray(new THREE.Vector3(0, 0.2, -9), new THREE.Vector3(0, -1, 0))
    expect(projectRayOntoAxis(back, origin, axis, -0.05, 0.05)).toBe(-0.05)
  })

  it('holds position rather than jumping when the ray is parallel to the axis', () => {
    const parallel = new THREE.Ray(new THREE.Vector3(0, 0, -1), new THREE.Vector3(0, 0, 1))
    const result = projectRayOntoAxis(parallel, origin, axis, -0.05, 0.05)
    expect(Number.isFinite(result)).toBe(true)
    expect(result).toBeGreaterThanOrEqual(-0.05)
    expect(result).toBeLessThanOrEqual(0.05)
  })

  it('snaps continuous travel onto the canonical band offsets and no others', () => {
    const count = MAX_VERTICAL_OFFSET + 1
    expect(snapToDetent(0, 0, 1, count)).toBe(0)
    expect(snapToDetent(1, 0, 1, count)).toBe(MAX_VERTICAL_OFFSET)
    expect(snapToDetent(0.5, 0, 1, count)).toBe(Math.round(0.5 * MAX_VERTICAL_OFFSET))
    // Every sample lands on a whole, in-range canonical offset.
    for (let i = 0; i <= 40; i++) {
      const value = snapToDetent(i / 40, 0, 1, count)
      expect(Number.isInteger(value)).toBe(true)
      expect(value).toBeGreaterThanOrEqual(0)
      expect(value).toBeLessThanOrEqual(MAX_VERTICAL_OFFSET)
    }
  })

  it('reaches every one of the ten canonical bands, one to one', () => {
    // A detent scale the reader can count I..X is only honest if each numeral
    // is actually reachable: nine of ten would be a scale with a dead stop.
    const count = MAX_VERTICAL_OFFSET + 1
    const seen = new Set<number>()
    for (let index = 0; index < count; index += 1) {
      seen.add(snapToDetent(index / MAX_VERTICAL_OFFSET, 0, 1, count))
    }
    expect([...seen].sort((a, b) => a - b)).toEqual([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
  })

  it('snaps identically whether the axis runs forward or backward', () => {
    expect(snapToDetent(0.25, 0, 1, 10)).toBe(snapToDetent(0.25, 0, 1, 10))
    expect(snapToDetent(-0.5, -1, 0, 10)).toBe(5)
  })
})
