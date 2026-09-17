import { describe, expect, it } from 'vitest'
import * as THREE from 'three'
import {
  projectRayOntoAxis,
  projectRayToLocalDetent,
  snapToDetent,
} from './interaction'

/**
 * The input seam is pure geometry, so it can be proven without a GPU. These are
 * the calculations a WebXR controller will run unchanged.
 */
describe('constrained spatial manipulation', () => {
  const origin = new THREE.Vector3(0, 0, 0)
  const axis = new THREE.Vector3(0, 0, 1)

  it('projects a pointing ray onto the one axis a part may travel', () => {
    const ray = new THREE.Ray(new THREE.Vector3(0, 0.2, 0.05), new THREE.Vector3(0, -1, 0))
    expect(projectRayOntoAxis(ray, origin, axis, -1, 1)).toBeCloseTo(0.05, 5)
  })

  it('clamps to the ends of the travel rather than letting a part leave it', () => {
    const far = new THREE.Ray(new THREE.Vector3(0, 0.2, 9), new THREE.Vector3(0, -1, 0))
    expect(projectRayOntoAxis(far, origin, axis, -0.05, 0.05)).toBe(0.05)
    const back = new THREE.Ray(new THREE.Vector3(0, 0.2, -9), new THREE.Vector3(0, -1, 0))
    expect(projectRayOntoAxis(back, origin, axis, -0.05, 0.05)).toBe(-0.05)
  })

  it('holds a finite in-range position when the ray is parallel to the axis', () => {
    const parallel = new THREE.Ray(new THREE.Vector3(0, 0, -1), new THREE.Vector3(0, 0, 1))
    const result = projectRayOntoAxis(parallel, origin, axis, -0.05, 0.05)
    expect(Number.isFinite(result)).toBe(true)
    expect(result).toBeGreaterThanOrEqual(-0.05)
    expect(result).toBeLessThanOrEqual(0.05)
  })

  it('snaps continuous travel onto only the requested number of detents', () => {
    const count = 6
    expect(snapToDetent(0, 0, 1, count)).toBe(0)
    expect(snapToDetent(1, 0, 1, count)).toBe(5)
    expect(snapToDetent(0.5, 0, 1, count)).toBe(3)
    for (let i = 0; i <= 40; i++) {
      const value = snapToDetent(i / 40, 0, 1, count)
      expect(Number.isInteger(value)).toBe(true)
      expect(value).toBeGreaterThanOrEqual(0)
      expect(value).toBeLessThan(count)
    }
  })
})

describe('translated-axis detent mapping', () => {
  const AXIS = new THREE.Vector3(0, 0, 1)
  const MIN_LOCAL = -0.04
  const MAX_LOCAL = 0.04
  const DETENT_COUNT = 6

  function rayForLocalZ(localZ: number, travel = 0): THREE.Ray {
    return new THREE.Ray(
      new THREE.Vector3(0.1, 0.2, travel + localZ),
      new THREE.Vector3(-0.4, -0.8, 0).normalize(),
    )
  }

  function oldTranslatedCallSiteDetent(ray: THREE.Ray, travel: number): number {
    const worldOrigin = new THREE.Vector3(0, 0, travel)
    const along = projectRayOntoAxis(
      ray,
      worldOrigin,
      AXIS,
      MIN_LOCAL + travel,
      MAX_LOCAL + travel,
    ) - travel
    return snapToDetent(along, MIN_LOCAL, MAX_LOCAL, DETENT_COUNT)
  }

  it.each([0, 0.07, 0.14, 0.21])(
    'keeps the same local detent when the carriage translates by %f',
    (travel) => {
      const detent = projectRayToLocalDetent(
        rayForLocalZ(0.021, travel),
        new THREE.Vector3(0, 0, travel),
        AXIS,
        MIN_LOCAL,
        MAX_LOCAL,
        DETENT_COUNT,
      )
      expect(detent).toBe(4)
    },
  )

  it('proves the accepted M1.2 double-translation arithmetic selects the wrong detent', () => {
    const travel = 0.14
    const ray = rayForLocalZ(0.021, travel)
    const corrected = projectRayToLocalDetent(
      ray,
      new THREE.Vector3(0, 0, travel),
      AXIS,
      MIN_LOCAL,
      MAX_LOCAL,
      DETENT_COUNT,
    )
    const legacy = oldTranslatedCallSiteDetent(ray, travel)

    expect(corrected).toBe(4)
    expect(legacy).toBe(0)
    expect(legacy).not.toBe(corrected)
  })

  it.each([
    [MIN_LOCAL, 0],
    [-0.02, 1],
    [0, 3],
    [0.02, 4],
    [MAX_LOCAL, 5],
  ] as const)('maps local position %f to detent %i', (localZ, expected) => {
    expect(projectRayToLocalDetent(
      rayForLocalZ(localZ, 0.11),
      new THREE.Vector3(0, 0, 0.11),
      AXIS,
      MIN_LOCAL,
      MAX_LOCAL,
      DETENT_COUNT,
    )).toBe(expected)
  })

  it('keeps display-order reversal outside the coordinate-frame projection', () => {
    const physical = projectRayToLocalDetent(
      rayForLocalZ(0.021, 0.14),
      new THREE.Vector3(0, 0, 0.14),
      AXIS,
      MIN_LOCAL,
      MAX_LOCAL,
      DETENT_COUNT,
    )
    const reversedDisplayIndex = DETENT_COUNT - 1 - physical
    expect(physical).toBe(4)
    expect(reversedDisplayIndex).toBe(1)
  })

  it('keeps parallel-ray fallback translation-invariant and in range', () => {
    const localRay = new THREE.Ray(
      new THREE.Vector3(0, 0, 0.021),
      new THREE.Vector3(0, 0, 1),
    )
    const travel = 0.17
    const translatedRay = localRay.clone()
    translatedRay.origin.z += travel

    const local = projectRayToLocalDetent(
      localRay,
      new THREE.Vector3(),
      AXIS,
      MIN_LOCAL,
      MAX_LOCAL,
      DETENT_COUNT,
    )
    const translated = projectRayToLocalDetent(
      translatedRay,
      new THREE.Vector3(0, 0, travel),
      AXIS,
      MIN_LOCAL,
      MAX_LOCAL,
      DETENT_COUNT,
    )

    expect(translated).toBe(local)
    expect(translated).toBeGreaterThanOrEqual(0)
    expect(translated).toBeLessThan(DETENT_COUNT)
  })
})
