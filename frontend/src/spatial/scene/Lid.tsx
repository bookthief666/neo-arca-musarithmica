import { useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { CASE, LID } from '../dimensions'
import type { ArcaMaterials } from '../materials'
import { makeMensaTexture } from '../textures'
import { Fillet, Hinge } from './Hardware'
import { ToneSelector } from './ToneSelector'
import type { MechanismState } from '../mechanismState'
import type { HistoricalManifest } from '../../instrument/types'

/**
 * THE LID.
 *
 * It rotates about a real hinge axis along the top rear edge of the carcass —
 * the group's origin IS that axis, so the lid swings exactly where the brass
 * knuckles are, and the Mensa mounted to its inner face swings with it. It does
 * not fade, translate or cross-dissolve; opening the Arca is one rotation of
 * one rigid body, which is what makes the interior feel revealed rather than
 * switched to.
 */
export function Lid({
  materials, manifest, open, reducedMotion, onToggle, cued,
  onEngageTone, toneState, toneCued,
}: {
  materials: ArcaMaterials
  manifest: HistoricalManifest
  open: boolean
  reducedMotion: boolean
  onToggle: () => void
  cued: boolean
  onEngageTone: () => void
  /** The selector's own state, derived from canonical readiness. */
  toneState: MechanismState
  toneCued: boolean
}) {
  const { width, depth, bodyHeight, plinth, lidHeight, wall } = CASE
  const hingeY = plinth + bodyHeight
  const hingeZ = -depth / 2 + LID.hingeRadius
  const group = useRef<THREE.Group>(null)

  const mensa = useMemo(() => makeMensaTexture(manifest), [manifest])

  // The lid is animated outside React: a spring here would re-render the whole
  // scene on every frame of the swing.
  useFrame((_, delta) => {
    const node = group.current
    if (!node) return
    const goal = open ? LID.openAngle : LID.closedAngle
    if (reducedMotion) {
      node.rotation.x = goal
      return
    }
    const ease = 1 - Math.pow(0.002, delta)
    node.rotation.x = THREE.MathUtils.lerp(node.rotation.x, goal, ease)
  })

  const innerW = width - LID.frame * 2
  const innerD = depth - LID.frame * 2

  return (
    <group position={[0, hingeY, hingeZ]} ref={group}>
      {/* The lid board itself, hanging forward of the hinge axis. */}
      <group position={[0, lidHeight / 2, depth / 2 - LID.hingeRadius]}>
        <mesh
          material={materials.wood}
          castShadow
          receiveShadow
          onClick={(event) => { event.stopPropagation(); onToggle() }}
          onPointerOver={(event) => { event.stopPropagation(); document.body.style.cursor = 'pointer' }}
          onPointerOut={() => { document.body.style.cursor = 'auto' }}
        >
          <boxGeometry args={[width, lidHeight, depth]} />
        </mesh>

        {/* Inlaid fillet on the outer face of the lid. */}
        <Fillet
          width={width} height={depth}
          position={[0, lidHeight / 2 + 0.0006, 0]}
          rotation={[-Math.PI / 2, 0, 0]}
          materials={materials} inset={0.016}
        />

        {/* ---- the Mensa Tonographica, let into the INNER face ---- */}
        {/* A routed recess so the sheet sits below the lid's frame members. */}
        <mesh material={materials.void} position={[0, -lidHeight / 2 - 0.0004, 0]} rotation={[Math.PI / 2, 0, 0]}>
          <planeGeometry args={[innerW + 0.005, innerD + 0.005]} />
        </mesh>
        <mesh
          position={[0, -lidHeight / 2 - 0.0011, 0]}
          rotation={[Math.PI / 2, 0, 0]}
          receiveShadow
        >
          <planeGeometry args={[innerW, innerD]} />
          <meshStandardMaterial map={mensa} roughness={0.88} metalness={0} />
        </mesh>

        {/* Brass corner nails holding the sheet down. */}
        {([
          [-innerW / 2 + 0.006, -innerD / 2 + 0.006],
          [innerW / 2 - 0.006, -innerD / 2 + 0.006],
          [-innerW / 2 + 0.006, innerD / 2 - 0.006],
          [innerW / 2 - 0.006, innerD / 2 - 0.006],
        ] as const).map(([x, z], i) => (
          <mesh key={i} material={materials.brass} position={[x, -lidHeight / 2 - 0.0016, z]}>
            <cylinderGeometry args={[0.0022, 0.0022, 0.0012, 10]} />
          </mesh>
        ))}

        {/* ---- TONVS II: a persistent turned control on the lid's inner face ---- */}
        {/* Placed in the clear vellum below the ruled table. Mounted higher up
            the sheet it sat squarely on the printed degrees, hiding the very
            map the Tone is selected from. */}
        <group position={[innerW / 2 - 0.03, -lidHeight / 2 - 0.004, -0.042]}>
          <ToneSelector
            materials={materials}
            state={toneState}
            cued={toneCued}
            onEngage={onEngageTone}
          />
        </group>
      </group>

      {/* ---- the hinges, on the axis the lid actually turns about ---- */}
      <Hinge position={[-width * 0.28, 0, 0]} materials={materials} />
      <Hinge position={[width * 0.28, 0, 0]} materials={materials} />

      {/* A subtle catch of light on the lid seam while the Arca is shut. */}
      {cued && !open && (
        <mesh material={materials.brassLit} position={[0, 0.001, depth - LID.hingeRadius * 2 - wall]}>
          <boxGeometry args={[width * 0.5, 0.0012, 0.0012]} />
        </mesh>
      )}
    </group>
  )
}
