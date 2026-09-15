import { useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import type { ArcaMaterials } from '../materials'
import type { MechanismState } from '../mechanismState'
import { makeLegendTexture } from '../textures'

/**
 * TONVS II — a turned brass selector on the lid's inner face.
 *
 * It is PERSISTENT. It is there from the moment the Arca opens, engraved with
 * the Tone it selects, visibly dormant until the rule reads a continuous band.
 * The reader meets it long before they need it, so when it wakes they already
 * know what woke.
 *
 * The engaged state is MECHANICAL: the pointer swings and seats against the
 * index. That rotation is the authoritative sign the Tone has been taken — not
 * a press flash, which says only that something was touched.
 */

/** Authored dormant-to-engaged sweep. One value, shared with the tests. */
export const TONE_SWEEP = Math.PI * (45 / 180)

export function ToneSelector({
  materials, state, cued, onEngage,
}: {
  materials: ArcaMaterials
  state: MechanismState
  cued: boolean
  onEngage: () => void
}) {
  const pointer = useRef<THREE.Group>(null)
  const legend = useMemo(() => makeLegendTexture(['TONVS', 'II']), [])

  const live = state !== 'dormant'
  const engaged = state === 'engaged'

  useFrame((_, delta) => {
    const node = pointer.current
    if (!node) return
    const goal = engaged ? TONE_SWEEP / 2 : -TONE_SWEEP / 2
    node.rotation.y = THREE.MathUtils.lerp(node.rotation.y, goal, 1 - Math.pow(0.004, delta))
  })

  return (
    <group name="tone:selector">
      {/* The engraved legend beside the knob, so the control names the Tone it
          selects. Set to the side rather than below, where the sheet already
          carries its printed witness line. */}
      <mesh position={[-0.027, -0.0022, 0]} rotation={[Math.PI / 2, 0, 0]}>
        <planeGeometry args={[0.028, 0.014]} />
        <meshStandardMaterial map={legend} metalness={0.75} roughness={0.38} />
      </mesh>

      {/* The two indices the tang swings between, cut into the lid beside the
          knob: where the pointer rests, and where the Tone is taken. */}
      {[-1, 1].map((side) => {
        const a = (side * TONE_SWEEP) / 2
        return (
          <mesh
            key={side}
            material={side > 0 && engaged ? materials.brassLit : materials.brassDark}
            position={[Math.sin(a) * 0.0168, -0.0026, Math.cos(a) * 0.0168]}
            rotation={[0, a, 0]}
          >
            <boxGeometry args={[0.0018, 0.0014, 0.006]} />
          </mesh>
        )
      })}

      <group
        onClick={live ? (event) => { event.stopPropagation(); onEngage() } : undefined}
        onPointerOver={live ? (event) => { event.stopPropagation(); document.body.style.cursor = 'pointer' } : undefined}
        onPointerOut={() => { document.body.style.cursor = 'auto' }}
      >
        {/* The turned knob. Dormant it is dull and plainly not yet for turning. */}
        <mesh castShadow>
          <cylinderGeometry args={[0.011, 0.012, 0.007, 20]} />
          <meshStandardMaterial
            color={engaged ? '#e8cb87' : live ? '#c3a25c' : '#6b5a3a'}
            metalness={live ? 0.92 : 0.5}
            roughness={live ? 0.26 : 0.66}
            emissive={cued ? '#5a3f12' : '#000000'}
            emissiveIntensity={cued ? 0.75 : 0}
          />
        </mesh>

        {/* Knurling, so it reads as something made to be gripped and turned. */}
        {Array.from({ length: 12 }, (_, i) => {
          const a = (i / 12) * Math.PI * 2
          return (
            <mesh
              key={i}
              material={live ? materials.brass : materials.brassDark}
              position={[Math.sin(a) * 0.0112, 0, Math.cos(a) * 0.0112]}
              rotation={[0, a, 0]}
            >
              <boxGeometry args={[0.0014, 0.007, 0.0022]} />
            </mesh>
          )
        })}

        {/* The tang. Its position IS the state of the Tone, so it has to reach
            past the knob's own rim — sitting on the face it was hidden behind
            the knurling from every angle the lid is actually viewed at. */}
        <group ref={pointer}>
          <mesh
            material={engaged ? materials.brassLit : materials.brass}
            position={[0, 0.0044, 0.008]}
            castShadow
          >
            <boxGeometry args={[0.0036, 0.0024, 0.026]} />
          </mesh>
          <mesh
            material={engaged ? materials.brassLit : materials.brass}
            position={[0, 0.0044, 0.019]}
          >
            <cylinderGeometry args={[0.0028, 0.0028, 0.0024, 12]} />
          </mesh>
        </group>

        {/* A generous invisible volume: the knob is 22 mm across, which is
            about 20 CSS px at the Fold's open framing. */}
        {live && (
          <mesh visible={false}>
            <boxGeometry args={[0.05, 0.05, 0.05]} />
          </mesh>
        )}
      </group>
    </group>
  )
}
