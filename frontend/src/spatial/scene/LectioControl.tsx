import { useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { CARRIAGE } from '../dimensions'
import type { ArcaMaterials } from '../materials'
import type { MechanismState } from '../mechanismState'
import { makeLegendTexture } from '../textures'

/**
 * LECTIO — the lever that performs the reading.
 *
 * It lives INSIDE the carriage group, so it travels with the drawer it
 * operates. M1.2 mounted its reading control in cabinet space and created it
 * only once execution was already possible: it did not move with the mechanism
 * it belonged to, and the last act of the whole operation was performed on a
 * control the reader had never seen before.
 *
 * Here the lever is present from the moment the carriage is, and it declares
 * its own state through position and material: seated and dull while locked,
 * released and catching the light once the Tone is set, thrown forward while
 * the Arca reads, and returned with a restrained fault mark if the kernel
 * refused — never losing the disposition that produced it.
 */

/** Throw of the lever between resting and operated. */
const LEVER_THROW = Math.PI * (26 / 180)

export function LectioControl({
  materials, state, cued, onExecute,
}: {
  materials: ArcaMaterials
  state: MechanismState
  cued: boolean
  onExecute: () => void
}) {
  const arm = useRef<THREE.Group>(null)
  const legend = useMemo(() => makeLegendTexture(['LECTIO'], { tarnished: false }), [])

  const live = state === 'available' || state === 'fault'
  const busy = state === 'busy'
  const fault = state === 'fault'

  const x = CARRIAGE.width / 2 - 0.028
  const y = CARRIAGE.y + CARRIAGE.wall + 0.004
  const z = CARRIAGE.depth / 2 - 0.03

  useFrame((_, delta) => {
    const node = arm.current
    if (!node) return
    const goal = busy ? LEVER_THROW : 0
    node.rotation.x = THREE.MathUtils.lerp(node.rotation.x, goal, 1 - Math.pow(0.002, delta))
  })

  const metal = live ? materials.brass : materials.brassDark

  return (
    <group name="lectio:lever" position={[x, y, z]}>
      {/* The engraved plate on the carriage apron beside the lever. */}
      <mesh position={[-0.028, -0.0028, 0.006]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[0.034, 0.012]} />
        <meshStandardMaterial
          map={legend}
          metalness={0.78}
          roughness={live ? 0.3 : 0.55}
          emissive={cued && live ? '#5a3f12' : '#000000'}
          emissiveIntensity={cued && live ? 0.5 : 0}
        />
      </mesh>

      {/* The bearing block the lever turns in. */}
      <mesh material={materials.brassDark} castShadow>
        <boxGeometry args={[0.016, 0.008, 0.012]} />
      </mesh>

      <group
        onClick={live ? (event) => { event.stopPropagation(); onExecute() } : undefined}
        onPointerOver={live ? (event) => { event.stopPropagation(); document.body.style.cursor = 'pointer' } : undefined}
        onPointerOut={() => { document.body.style.cursor = 'auto' }}
      >
        <group ref={arm}>
          {/* The arm, standing proud of the apron. */}
          <mesh
            material={live ? materials.brassLit : metal}
            position={[0, 0.011, 0]}
            castShadow
          >
            <boxGeometry args={[0.005, 0.02, 0.005]} />
          </mesh>
          {/* The ball the hand pulls. */}
          <mesh
            material={live ? materials.brassLit : metal}
            position={[0, 0.023, 0]}
            castShadow
          >
            <sphereGeometry args={[0.0062, 16, 12]} />
          </mesh>
          {/* A restrained fault mark: a dark collar, not an alarm. */}
          {fault && (
            <mesh material={materials.brassDark} position={[0, 0.0155, 0]}>
              <cylinderGeometry args={[0.0048, 0.0048, 0.003, 12]} />
            </mesh>
          )}
        </group>

        {/* Touch volume. The ball is 12 mm across, roughly 11 CSS px at the
            Fold's working framing, so the hand needs far more than the metal. */}
        {live && (
          <mesh position={[0, 0.018, 0]} visible={false}>
            <boxGeometry args={[0.046, 0.05, 0.046]} />
          </mesh>
        )}
      </group>
    </group>
  )
}
