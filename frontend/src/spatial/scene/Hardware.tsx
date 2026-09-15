import { useMemo } from 'react'
import * as THREE from 'three'
import type { ArcaMaterials } from '../materials'

/**
 * Cast brass hardware, shared across the cabinet.
 *
 * These are the pieces the construction sheet calls out as separate parts, and
 * they are the pieces a hand would find first: corner brackets that wrap an
 * edge, ring handles to lift by, feet to set it down on, finials to pinch.
 * Each is modelled as a real solid so it still reads from the back and the
 * underside, not as a decal on the front face.
 */

/** An L-bracket wrapping one vertical edge of the carcass. */
export function CornerBracket({
  position, rotation, height, arm = 0.011, thickness = 0.0014, materials,
}: {
  position: [number, number, number]
  rotation?: [number, number, number]
  height: number
  arm?: number
  thickness?: number
  materials: ArcaMaterials
}) {
  return (
    <group position={position} rotation={rotation}>
      <mesh material={materials.brass} position={[arm / 2, 0, 0]} castShadow>
        <boxGeometry args={[arm, height, thickness]} />
      </mesh>
      <mesh material={materials.brass} position={[0, 0, arm / 2]} castShadow>
        <boxGeometry args={[thickness, height, arm]} />
      </mesh>
      {[height / 2 - 0.007, -height / 2 + 0.007].map((y) => (
        <mesh key={y} material={materials.brassDark} position={[arm * 0.55, y, thickness]}>
          <cylinderGeometry args={[0.0018, 0.0018, 0.0012, 8]} />
        </mesh>
      ))}
    </group>
  )
}

/** A lifting ring on a rosette, as on the ends of the reference cabinet. */
export function RingHandle({
  position, rotation, materials,
}: {
  position: [number, number, number]
  rotation?: [number, number, number]
  materials: ArcaMaterials
}) {
  return (
    <group position={position} rotation={rotation}>
      <mesh material={materials.brassDark}>
        <cylinderGeometry args={[0.009, 0.0105, 0.003, 20]} />
      </mesh>
      <mesh material={materials.brass} position={[0, -0.014, 0]} rotation={[Math.PI / 2, 0, 0]} castShadow>
        <torusGeometry args={[0.014, 0.0024, 10, 28]} />
      </mesh>
    </group>
  )
}

/** A turned ball foot. */
export function BallFoot({ position, materials }: { position: [number, number, number]; materials: ArcaMaterials }) {
  return (
    <group position={position}>
      <mesh material={materials.brass} castShadow>
        <sphereGeometry args={[0.009, 18, 14]} />
      </mesh>
      <mesh material={materials.brassDark} position={[0, 0.007, 0]}>
        <cylinderGeometry args={[0.0075, 0.0095, 0.005, 16]} />
      </mesh>
    </group>
  )
}

/** A turned knob pull, for the drawer front. */
export function KnobPull({ position, materials }: { position: [number, number, number]; materials: ArcaMaterials }) {
  return (
    <group position={position}>
      <mesh material={materials.brass} castShadow>
        <sphereGeometry args={[0.0085, 18, 14]} />
      </mesh>
      <mesh material={materials.brassDark} position={[0, 0, -0.006]} rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[0.003, 0.004, 0.008, 12]} />
      </mesh>
    </group>
  )
}

/** A hinge knuckle assembly on the back edge, joining lid to carcass. */
export function Hinge({ position, materials }: { position: [number, number, number]; materials: ArcaMaterials }) {
  return (
    <group position={position}>
      <mesh material={materials.brass} rotation={[0, 0, Math.PI / 2]} castShadow>
        <cylinderGeometry args={[0.005, 0.005, 0.034, 14]} />
      </mesh>
      <mesh material={materials.brassDark} position={[0, 0.004, -0.006]}>
        <boxGeometry args={[0.03, 0.012, 0.0016]} />
      </mesh>
    </group>
  )
}

/** An inlaid gold fillet: a thin line let into a wooden panel. */
export function Fillet({
  width, height, position, rotation, materials, inset = 0.012,
}: {
  width: number
  height: number
  position: [number, number, number]
  rotation?: [number, number, number]
  materials: ArcaMaterials
  inset?: number
}) {
  const w = width - inset * 2
  const h = height - inset * 2
  const line = 0.0011
  const geo = useMemo(() => new THREE.BoxGeometry(1, 1, 0.0008), [])
  if (w <= 0 || h <= 0) return null
  return (
    <group position={position} rotation={rotation}>
      <mesh geometry={geo} material={materials.brass} position={[0, h / 2, 0]} scale={[w, line, 1]} />
      <mesh geometry={geo} material={materials.brass} position={[0, -h / 2, 0]} scale={[w, line, 1]} />
      <mesh geometry={geo} material={materials.brass} position={[-w / 2, 0, 0]} scale={[line, h, 1]} />
      <mesh geometry={geo} material={materials.brass} position={[w / 2, 0, 0]} scale={[line, h, 1]} />
    </group>
  )
}
