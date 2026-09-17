import { forwardRef, useEffect, useMemo } from 'react'
import type { ThreeEvent } from '@react-three/fiber'
import * as THREE from 'three'
import { VIRGA } from '../dimensions'
import type { ArcaMaterials } from '../materials'
import { makeCriticalEditionCarrierMaterial } from '../textures'
import type { CriticalEditionCarrier } from '../../instrument/types'

/** One persistent H1 critical-edition carrier; not a stack of selectable bands. */
export const Virga = forwardRef<THREE.Group, {
  source: CriticalEditionCarrier
  materials: ArcaMaterials
  cued?: boolean
  held?: boolean
  onPointerDown?: (event: ThreeEvent<PointerEvent>) => void
  onPointerOver?: (event: ThreeEvent<PointerEvent>) => void
  onPointerOut?: (event: ThreeEvent<PointerEvent>) => void
}>(function Virga({ source, materials, cued = false, held = false, onPointerDown, onPointerOver, onPointerOut }, ref) {
  const faceMaterial = useMemo(() => makeCriticalEditionCarrierMaterial(source), [source])
  const { length, width, printableWidth, thickness, finialRadius, collarRadius, collarHeight } = VIRGA

  useEffect(() => () => {
    faceMaterial.map?.dispose()
    faceMaterial.dispose()
  }, [faceMaterial])

  return (
    <group
      ref={ref}
      onPointerDown={onPointerDown}
      onPointerOver={onPointerOver}
      onPointerOut={onPointerOut}
    >
      <mesh material={materials.woodDark} castShadow receiveShadow>
        <boxGeometry args={[width, thickness, length]} />
      </mesh>

      <mesh
        position={[0, thickness / 2 + 0.0002, 0]}
        rotation={[-Math.PI / 2, 0, Math.PI]}
        material={faceMaterial}
      >
        <planeGeometry args={[printableWidth, length - 0.004]} />
      </mesh>

      <mesh material={materials.brass} position={[0, 0, -length / 2 + 0.004]} rotation={[Math.PI / 2, 0, 0]} castShadow>
        <cylinderGeometry args={[collarRadius, collarRadius, 0.008, 14]} />
      </mesh>

      <mesh
        material={held || cued ? materials.brassLit : materials.brass}
        position={[0, 0, length / 2 + collarHeight / 2]}
        rotation={[Math.PI / 2, 0, 0]}
        castShadow
      >
        <cylinderGeometry args={[collarRadius, collarRadius + 0.0008, collarHeight, 16]} />
      </mesh>
      <mesh
        material={held || cued ? materials.brassLit : materials.brass}
        position={[0, 0, length / 2 + collarHeight + finialRadius * 0.82]}
        castShadow
      >
        <sphereGeometry args={[finialRadius, 20, 16]} />
      </mesh>
    </group>
  )
})

export const VIRGA_HEAD_REACH =
  VIRGA.length / 2 + VIRGA.collarHeight + VIRGA.finialRadius * 1.6
