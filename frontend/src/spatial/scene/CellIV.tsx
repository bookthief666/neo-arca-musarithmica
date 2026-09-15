import { useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { CELL_IV, DECK_TOP, INTERIOR, SLOT_DEPTH } from '../dimensions'
import type { ArcaMaterials } from '../materials'
import { makeBrassPlateTexture } from '../textures'
import { cellCoverAngles } from './stations'

/**
 * CELL IV — the one operative receptacle, as a container that visibly opens.
 *
 * M1.2 gave this cavity real depth and persistent mortises but no mechanism: a
 * flat strip on the deck lip was the only thing that "opened" it, so the reader
 * was asked to take a virga out of something that had never announced itself as
 * closed. Worse, at a 12 mm recess the stored carriers sat below deck level and
 * the open cell looked empty.
 *
 * The cover folds rather than slides, and the reason is measured rather than
 * preferred: see cellCoverAngles. It hinges at the cell's rear edge and doubles
 * over on itself, which is the only real cover that fits in 54 mm of headroom.
 *
 * The mortises are permanent. The empty socket a carrier came out of is the
 * proof of where it came from, and it stays there for the whole session.
 */

interface CellIVProps {
  materials: ArcaMaterials
  open: boolean
  cued: boolean
  reducedMotion: boolean
  onOpen: () => void
}

export function CellIV({ materials, open, cued, reducedMotion, onOpen }: CellIVProps) {
  const inner = useRef<THREE.Group>(null)
  const outer = useRef<THREE.Group>(null)
  const { divider } = INTERIOR
  const centreZ = CELL_IV.centreZ
  const leaf = CELL_IV.depth / 2
  /** The fold axis: the cell's rear edge, just clear of the deck surface. */
  const hingeZ = centreZ - CELL_IV.depth / 2
  const hingeY = DECK_TOP + CELL_IV.coverThickness / 2 + 0.0008

  const plate = useMemo(
    () => makeBrassPlateTexture(
      [{ text: 'IV', size: 20, gap: 7 }, { text: 'CELLVLA IV · PINAX IV', size: 21 }],
      { width: 520, height: 150, tarnished: false },
    ),
    [],
  )

  // The fold runs outside React: a cover that re-rendered the tree on every
  // frame of its travel would cost a React commit per frame.
  useFrame((_, delta) => {
    if (!inner.current || !outer.current) return
    const goal = cellCoverAngles(open)
    if (reducedMotion) {
      inner.current.rotation.x = goal.inner
      outer.current.rotation.x = goal.outer
      return
    }
    const ease = 1 - Math.pow(0.004, delta)
    inner.current.rotation.x = THREE.MathUtils.lerp(inner.current.rotation.x, goal.inner, ease)
    outer.current.rotation.x = THREE.MathUtils.lerp(outer.current.rotation.x, goal.outer, ease)
  })

  return (
    <group name="cell:iv">
      {/* ---- the cavity: a felt floor the carriers lie on ---- */}
      <mesh
        material={materials.felt}
        position={[0, DECK_TOP - SLOT_DEPTH, centreZ]}
        rotation={[-Math.PI / 2, 0, 0]}
        receiveShadow
      >
        <planeGeometry args={[CELL_IV.width, CELL_IV.depth]} />
      </mesh>

      {/* Dark end walls, so the cavity reads as a hole rather than a panel. */}
      {[-1, 1].map((edge) => (
        <mesh
          key={`end${edge}`}
          material={materials.void}
          position={[0, DECK_TOP - SLOT_DEPTH / 2, centreZ + edge * (CELL_IV.depth / 2)]}
          rotation={[0, edge > 0 ? 0 : Math.PI, 0]}
        >
          <planeGeometry args={[CELL_IV.width, SLOT_DEPTH]} />
        </mesh>
      ))}

      {/* ---- three mortises, cut by four dividers. They persist. ---- */}
      {[-1, 0, 1].map((lane) => {
        const x = lane * CELL_IV.slotPitch
        return (
          <group key={lane}>
            {[-1, 1].map((edge) => (
              <mesh
                key={edge}
                material={materials.woodDark}
                position={[
                  x + edge * (CELL_IV.slotWidth / 2 + divider / 2),
                  DECK_TOP - SLOT_DEPTH / 2,
                  centreZ,
                ]}
                castShadow
                receiveShadow
              >
                <boxGeometry args={[divider, SLOT_DEPTH, CELL_IV.depth * 0.96]} />
              </mesh>
            ))}
          </group>
        )
      })}

      {/* ---- a coaming round the cell mouth, so the opening has an edge ---- */}
      {[-1, 1].map((side) => (
        <mesh
          key={side}
          material={materials.woodDark}
          position={[side * (CELL_IV.width / 2 + divider / 2), DECK_TOP + 0.002, centreZ]}
          castShadow
          receiveShadow
        >
          <boxGeometry args={[divider, 0.004, CELL_IV.depth]} />
        </mesh>
      ))}

      {/* ---- THE COVER: two leaves, hinged at the cell's rear edge ---- */}
      <group ref={inner} position={[0, hingeY, hingeZ]} name="cell:cover">
        {/* Inner leaf, reaching forward from the fold axis. */}
        <mesh material={materials.wood} position={[0, 0, leaf / 2]} castShadow receiveShadow>
          <boxGeometry args={[CELL_IV.width, CELL_IV.coverThickness, leaf]} />
        </mesh>

        {/* The knuckle the two leaves turn about. */}
        <mesh
          material={materials.brassDark}
          position={[0, 0, leaf]}
          rotation={[0, 0, Math.PI / 2]}
          castShadow
        >
          <cylinderGeometry args={[CELL_IV.coverThickness * 0.55, CELL_IV.coverThickness * 0.55, CELL_IV.width * 0.9, 10]} />
        </mesh>

        {/* Outer leaf, hinged to the inner one at its far edge. */}
        <group ref={outer} position={[0, 0, leaf]}>
          <mesh material={materials.wood} position={[0, 0, leaf / 2]} castShadow receiveShadow>
            <boxGeometry args={[CELL_IV.width, CELL_IV.coverThickness, leaf]} />
          </mesh>

          {/* The engraved identification plate, let into the outer leaf. */}
          <mesh
            position={[0, CELL_IV.coverThickness / 2 + 0.0004, leaf / 2]}
            rotation={[-Math.PI / 2, 0, 0]}
          >
            <planeGeometry args={[CELL_IV.width * 0.8, leaf * 0.5]} />
            <meshStandardMaterial
              map={plate}
              metalness={0.8}
              roughness={0.32}
              emissive={cued ? '#5a3f12' : '#000000'}
              emissiveIntensity={cued ? 0.55 : 0}
            />
          </mesh>

          {/* The finger lip: the part a hand actually pulls. */}
          <mesh
            material={cued ? materials.brassLit : materials.brass}
            position={[0, CELL_IV.coverThickness / 2, leaf - CELL_IV.coverHandleDepth / 2]}
            castShadow
          >
            <boxGeometry args={[
              CELL_IV.width * 0.34, CELL_IV.coverThickness * 1.6, CELL_IV.coverHandleDepth,
            ]} />
          </mesh>
        </group>
      </group>

      {/* A generous invisible volume over the closed cell, because the visible
          hardware is only about 20 CSS px across on a folded Fold. It exists
          only while the cell is shut, so it can never swallow a tap meant for
          a carrier. */}
      {!open && (
        <mesh
          position={[0, DECK_TOP + CELL_IV.hitSize / 2, centreZ]}
          visible={false}
          onClick={(event) => { event.stopPropagation(); onOpen() }}
          onPointerOver={(event) => { event.stopPropagation(); document.body.style.cursor = 'pointer' }}
          onPointerOut={() => { document.body.style.cursor = 'auto' }}
        >
          <boxGeometry args={[CELL_IV.width, CELL_IV.hitSize, CELL_IV.depth]} />
        </mesh>
      )}
    </group>
  )
}
