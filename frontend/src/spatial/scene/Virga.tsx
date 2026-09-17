import { forwardRef, useEffect, useMemo } from 'react'
import type { ThreeEvent } from '@react-three/fiber'
import * as THREE from 'three'
import { VIRGA } from '../dimensions'
import type { ArcaMaterials } from '../materials'
import { makeVirgaTexture } from '../textures'
import type { CriticalEditionCarrier } from '../../instrument/types'

/**
 * A VIRGA — the hero object of the whole instrument.
 *
 * It is a real solid: a wooden shaft with six faces and measurable thickness, a
 * printed vellum face carrying that column's own bands, a turned brass collar,
 * and a ball finial at the head. The finial exists for one reason: it is the
 * part a hand closes on. Everything about its size and stand-off is chosen so
 * that a reader — now with a pointer, later with a pinch in VR — can see where
 * to take hold without being told.
 *
 * The face texture is generated from the source column, so a virga cannot show
 * a band the kernel would not execute.
 */
export const Virga = forwardRef<THREE.Group, {
  source: CriticalEditionCarrier
  materials: ArcaMaterials
  /** Lit while this carrier is the instrument's next affordance. */
  cued?: boolean
  /** Raised while held, so the reader can see it has left its slot. */
  held?: boolean
  onPointerDown?: (event: ThreeEvent<PointerEvent>) => void
  onPointerOver?: (event: ThreeEvent<PointerEvent>) => void
  onPointerOut?: (event: ThreeEvent<PointerEvent>) => void
}>(function Virga({ source, materials, cued = false, held = false, onPointerDown, onPointerOver, onPointerOut }, ref) {
  const face = useMemo(() => makeVirgaTexture(source), [source])
  const { length, width, thickness, finialRadius, collarRadius, collarHeight } = VIRGA

  const faceMaterial = useMemo(
    () => new THREE.MeshStandardMaterial({ map: face, roughness: 0.86, metalness: 0 }),
    [face],
  )

  useEffect(() => () => { faceMaterial.dispose(); face.dispose() }, [faceMaterial, face])

  return (
    <group
      ref={ref}
      onPointerDown={onPointerDown}
      onPointerOver={onPointerOver}
      onPointerOut={onPointerOut}
    >
      {/* The shaft: a real stick of wood, not a plane. */}
      <mesh material={materials.woodDark} castShadow receiveShadow>
        <boxGeometry args={[width, thickness, length]} />
      </mesh>

      {/* The printed face, let into the top of the shaft. */}
      <mesh
        position={[0, thickness / 2 + 0.0002, 0]}
        rotation={[-Math.PI / 2, 0, Math.PI]}
        material={faceMaterial}
      >
        <planeGeometry args={[width - 0.0016, length - 0.0016]} />
      </mesh>

      {/* Brass ferrule at the foot. */}
      <mesh material={materials.brass} position={[0, 0, -length / 2 + 0.004]} rotation={[Math.PI / 2, 0, 0]} castShadow>
        <cylinderGeometry args={[collarRadius, collarRadius, 0.008, 14]} />
      </mesh>

      {/* Collar and ball finial at the head — the grip. */}
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

/** Half-length plus the head, i.e. how far the finial stands off centre. */
export const VIRGA_HEAD_REACH =
  VIRGA.length / 2 + VIRGA.collarHeight + VIRGA.finialRadius * 1.6
