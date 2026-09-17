import { useEffect, useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { CASE, LID } from '../dimensions'
import type { ArcaMaterials } from '../materials'
import { makeBrassPlateTexture, makeMensaTexture } from '../textures'
import { Fillet, Hinge } from './Hardware'
import type { HistoricalManifest } from '../../instrument/types'

/** Rigid hinged lid carrying the fixed printed-p.51 Tone-II witness. */
export function Lid({
  materials, manifest, open, reducedMotion, onToggle, cued, activeDegrees = [],
}: {
  materials: ArcaMaterials
  manifest: HistoricalManifest
  open: boolean
  reducedMotion: boolean
  onToggle: () => void
  cued: boolean
  activeDegrees?: readonly number[]
}) {
  const { width, depth, bodyHeight, plinth, lidHeight, wall } = CASE
  const hingeY = plinth + bodyHeight
  const hingeZ = -depth / 2 + LID.hingeRadius
  const group = useRef<THREE.Group>(null)

  const mensa = useMemo(() => makeMensaTexture(manifest), [manifest])
  const policy = useMemo(() => makeBrassPlateTexture([
    { text: 'PRINTED p.51 WITNESS', size: 22, gap: 6 },
    { text: 'H0 TRANSCRIPTION / H1 OPERATING POLICY', size: 16 },
  ], { width: 760, height: 150, tarnished: false }), [])
  useEffect(() => () => { mensa.dispose(); policy.dispose() }, [mensa, policy])

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
  const tableW = innerW * 0.84
  const toneCellW = tableW / 8
  const active = new Set(activeDegrees)

  return (
    <group position={[0, hingeY, hingeZ]} ref={group}>
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

        <Fillet
          width={width} height={depth}
          position={[0, lidHeight / 2 + 0.0006, 0]}
          rotation={[-Math.PI / 2, 0, 0]}
          materials={materials} inset={0.016}
        />

        <mesh material={materials.void} position={[0, -lidHeight / 2 - 0.0004, 0]} rotation={[Math.PI / 2, 0, 0]}>
          <planeGeometry args={[innerW + 0.005, innerD + 0.005]} />
        </mesh>
        <mesh position={[0, -lidHeight / 2 - 0.0011, 0]} rotation={[Math.PI / 2, 0, 0]} receiveShadow>
          <planeGeometry args={[innerW, innerD]} />
          <meshStandardMaterial map={mensa} roughness={0.88} metalness={0} />
        </mesh>

        {/* Event-driven emphasis only: the Tone witness is always present and never an unlock gate. */}
        {Array.from({ length: 8 }, (_, index) => index + 1).map((degree) => {
          if (!active.has(degree)) return null
          const x = -tableW / 2 + toneCellW * (degree - 0.5)
          return (
            <mesh key={degree} position={[x, -lidHeight / 2 - 0.0019, 0]} rotation={[Math.PI / 2, 0, 0]}>
              <planeGeometry args={[toneCellW * 0.88, innerD * 0.25]} />
              <meshBasicMaterial color="#ffd16a" transparent opacity={0.27} depthWrite={false} />
            </mesh>
          )
        })}

        <mesh
          position={[0, -lidHeight / 2 - 0.002, innerD / 2 - 0.014]}
          rotation={[Math.PI / 2, 0, 0]}
        >
          <planeGeometry args={[innerW * 0.86, 0.018]} />
          <meshStandardMaterial map={policy} metalness={0.62} roughness={0.42} />
        </mesh>

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

        <mesh material={materials.brass} position={[innerW / 2 - 0.026, -lidHeight / 2 - 0.004, innerD / 2 - 0.02]}>
          <cylinderGeometry args={[0.011, 0.012, 0.007, 20]} />
        </mesh>
      </group>

      <Hinge position={[-width * 0.28, 0, 0]} materials={materials} />
      <Hinge position={[width * 0.28, 0, 0]} materials={materials} />

      {cued && !open && (
        <mesh material={materials.brassLit} position={[0, 0.001, depth - LID.hingeRadius * 2 - wall]}>
          <boxGeometry args={[width * 0.5, 0.0012, 0.0012]} />
        </mesh>
      )}
    </group>
  )
}
