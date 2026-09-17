import { useEffect, useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { CARRIAGE, CASE, READER, VIRGA } from '../dimensions'
import type { ArcaMaterials } from '../materials'
import { makeBrassPlateTexture } from '../textures'
import { KnobPull } from './Hardware'

const LIP_HEIGHT = 0.006

/**
 * Pull-out workbench for the bounded historical fragment.
 *
 * Only the central bed is operative. The two flanking covers are inert H1 corpus
 * capacity: they have no state, no callbacks and no ray targets. This preserves
 * the physical idea of a larger apparatus without pretending that unverified
 * musical choices are already available.
 */
export function Carriage({
  materials, extended, reducedMotion, occupied, children, onPullOut, travelRef,
}: {
  materials: ArcaMaterials
  extended: boolean
  reducedMotion: boolean
  occupied: boolean
  children?: React.ReactNode
  onPullOut?: () => void
  travelRef?: React.RefObject<number>
}) {
  const group = useRef<THREE.Group>(null)
  const capacityLabel = useMemo(() => makeBrassPlateTexture([
    { text: 'CORPVS NONDVM EDITVM', size: 24, gap: 8 },
    { text: 'H1 CAPACITAS', size: 18 },
  ], { width: 640, height: 180, tarnished: true }), [])
  useEffect(() => () => capacityLabel.dispose(), [capacityLabel])

  useFrame((_, delta) => {
    const node = group.current
    if (!node) return
    const goal = extended ? CARRIAGE.travel : 0
    node.position.z = reducedMotion
      ? goal
      : THREE.MathUtils.lerp(node.position.z, goal, 1 - Math.pow(0.003, delta))
    if (travelRef) travelRef.current = node.position.z
  })

  const halfW = CARRIAGE.width / 2
  const halfD = CARRIAGE.depth / 2
  const { height, wall } = CARRIAGE
  const floorY = CARRIAGE.y
  const activeHalf = CARRIAGE.activeChannelWidth / 2
  const sideInner = activeHalf + CARRIAGE.capacityGap
  const sideOuter = halfW - wall * 1.5
  const coverWidth = Math.max(0.02, sideOuter - sideInner)
  const coverCentre = sideInner + coverWidth / 2
  const readerY = floorY + wall + VIRGA.thickness + READER.barHeight / 2 + 0.001

  return (
    <group ref={group} position={[0, 0, 0]}>
      <mesh material={materials.woodDark} position={[0, floorY + wall / 2, 0]} receiveShadow castShadow>
        <boxGeometry args={[CARRIAGE.width, wall, CARRIAGE.depth]} />
      </mesh>
      <mesh material={materials.woodDark} position={[0, floorY + height / 2, -halfD + wall / 2]} castShadow>
        <boxGeometry args={[CARRIAGE.width, height, wall]} />
      </mesh>
      {[-1, 1].map((side) => (
        <mesh key={side} material={materials.woodDark} position={[side * (halfW - wall / 2), floorY + height / 2, 0]} castShadow>
          <boxGeometry args={[wall, height, CARRIAGE.depth]} />
        </mesh>
      ))}

      <group
        onClick={onPullOut ? (event) => { event.stopPropagation(); onPullOut() } : undefined}
        onPointerOver={onPullOut ? (event) => { event.stopPropagation(); document.body.style.cursor = 'pointer' } : undefined}
        onPointerOut={onPullOut ? () => { document.body.style.cursor = 'auto' } : undefined}
      >
        <mesh material={materials.wood} position={[0, floorY + height / 2, halfD + 0.004]} castShadow receiveShadow>
          <boxGeometry args={[CASE.width - 0.004, height + 0.014, 0.008]} />
        </mesh>
        <KnobPull position={[-0.06, floorY + height / 2, halfD + 0.012]} materials={materials} />
        <KnobPull position={[0.06, floorY + height / 2, halfD + 0.012]} materials={materials} />
      </group>

      {[-1, 1].map((side) => (
        <mesh
          key={side}
          material={materials.brassDark}
          position={[side * (halfW + 0.002), floorY + 0.004, -0.02]}
          rotation={[Math.PI / 2, 0, 0]}
        >
          <cylinderGeometry args={[0.0022, 0.0022, CARRIAGE.depth * 0.9, 8]} />
        </mesh>
      ))}

      {/* One operative felt bed. */}
      <mesh
        material={materials.felt}
        position={[0, floorY + wall + 0.0004, 0]}
        rotation={[-Math.PI / 2, 0, 0]}
        receiveShadow
      >
        <planeGeometry args={[CARRIAGE.activeChannelWidth, CARRIAGE.depth - wall * 2]} />
      </mesh>
      {[-1, 1].map((edge) => (
        <mesh
          key={edge}
          material={materials.woodDark}
          position={[edge * (activeHalf + 0.002), floorY + wall + LIP_HEIGHT / 2, 0]}
          castShadow
        >
          <boxGeometry args={[0.004, LIP_HEIGHT, CARRIAGE.depth - wall * 2]} />
        </mesh>
      ))}

      {/* Sealed, inert future corpus capacity. No event handlers or reducer state. */}
      {[-1, 1].map((side) => (
        <group key={side} position={[side * coverCentre, floorY + wall + 0.002, 0]}>
          <mesh material={materials.woodDark} castShadow receiveShadow>
            <boxGeometry args={[coverWidth, 0.006, CARRIAGE.depth - wall * 2]} />
          </mesh>
          <mesh position={[0, 0.0032, 0]} rotation={[-Math.PI / 2, 0, side < 0 ? Math.PI : 0]}>
            <planeGeometry args={[coverWidth * 0.82, 0.036]} />
            <meshStandardMaterial map={capacityLabel} metalness={0.7} roughness={0.55} />
          </mesh>
        </group>
      ))}

      {/* A single inspection bridge above the only operative bed. */}
      <group position={[0, readerY, READER.stationZ]}>
        {[-1, 1].map((side) => (
          <mesh
            key={side}
            material={occupied ? materials.brassLit : materials.brass}
            position={[side * (activeHalf + 0.004), 0, 0]}
            castShadow
          >
            <boxGeometry args={[0.006, READER.barHeight, READER.barDepth]} />
          </mesh>
        ))}
        <mesh material={occupied ? materials.brassLit : materials.brassDark} castShadow>
          <boxGeometry args={[CARRIAGE.activeChannelWidth + 0.012, 0.003, READER.barDepth]} />
        </mesh>
      </group>

      {children}
    </group>
  )
}
