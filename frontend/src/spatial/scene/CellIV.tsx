import { useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { CELL_IV, DECK_TOP, INTERIOR, SLOT_DEPTH } from '../dimensions'
import type { ArcaMaterials } from '../materials'
import { makeBrassPlateTexture } from '../textures'
import { cellCoverTarget } from './stations'

/**
 * CELL IV — the one operative receptacle, as a container that visibly opens.
 *
 * M1.2 gave this cavity real depth and persistent mortises but no mechanism:
 * a flat strip on the deck lip was the only thing that "opened" it, so the
 * reader was asked to take a virga out of something that never announced
 * itself as closed. Worse, at a 12 mm recess the stored carriers sat BELOW
 * deck level and the open cell looked empty.
 *
 * So the cell now has a shallow cover plate that runs rearward in side
 * rebates and disappears under the bank rail, and the carriers beneath it
 * stand proud enough to be seen. The mortises are permanent: the empty socket
 * a carrier came out of is the proof of where it came from, and it stays
 * there for the whole session.
 */

interface CellIVProps {
  materials: ArcaMaterials
  open: boolean
  cued: boolean
  reducedMotion: boolean
  onOpen: () => void
}

export function CellIV({ materials, open, cued, reducedMotion, onOpen }: CellIVProps) {
  const cover = useRef<THREE.Group>(null)
  const { divider } = INTERIOR
  const centreZ = CELL_IV.centreZ
  const coverY = DECK_TOP + CELL_IV.coverLift + CELL_IV.coverThickness / 2

  const plate = useMemo(
    () => makeBrassPlateTexture(
      [{ text: 'IV', size: 20, gap: 7 }, { text: 'CELLVLA IV · PINAX IV', size: 21 }],
      { width: 520, height: 150, tarnished: false },
    ),
    [],
  )

  // The cover slides outside React: a drawer that re-rendered the tree on every
  // frame of its travel would cost a React commit per frame.
  useFrame((_, delta) => {
    const node = cover.current
    if (!node) return
    const goal = cellCoverTarget(open)
    node.position.z = reducedMotion
      ? goal
      : THREE.MathUtils.lerp(node.position.z, goal, 1 - Math.pow(0.004, delta))
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

      {/* A dark surround, so the cavity reads as a hole rather than a panel. */}
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
                position={[x + edge * (CELL_IV.slotWidth / 2 + divider / 2), DECK_TOP - SLOT_DEPTH / 2, centreZ]}
                castShadow
                receiveShadow
              >
                <boxGeometry args={[divider, SLOT_DEPTH, CELL_IV.depth * 0.94]} />
              </mesh>
            ))}
          </group>
        )
      })}

      {/* ---- the side rebates the cover runs in ---- */}
      {[-1, 1].map((side) => (
        <mesh
          key={side}
          material={materials.brassDark}
          position={[
            side * (CELL_IV.width / 2 + divider / 2),
            DECK_TOP + CELL_IV.coverLift / 2,
            centreZ - CELL_IV.coverTravel / 2,
          ]}
          castShadow
        >
          <boxGeometry args={[divider, CELL_IV.coverLift, CELL_IV.depth + CELL_IV.coverTravel]} />
        </mesh>
      ))}

      {/* ---- THE COVER ---- */}
      {/* The group sits AT the cover, so everything inside it is local and the
          whole assembly — plate, lip and hit volume — slides as one body. */}
      <group ref={cover} name="cell:cover" position={[0, coverY, cellCoverTarget(open)]}>
        <mesh material={materials.wood} castShadow receiveShadow>
          <boxGeometry args={[CELL_IV.width, CELL_IV.coverThickness, CELL_IV.depth]} />
        </mesh>

        {/* The engraved identification plate, let into the cover's face. */}
        <mesh
          position={[0, CELL_IV.coverThickness / 2 + 0.0004, -CELL_IV.depth * 0.14]}
          rotation={[-Math.PI / 2, 0, 0]}
        >
          <planeGeometry args={[CELL_IV.width * 0.74, CELL_IV.depth * 0.22]} />
          <meshStandardMaterial
            map={plate}
            metalness={0.8}
            roughness={0.32}
            emissive={cued ? '#5a3f12' : '#000000'}
            emissiveIntensity={cued ? 0.5 : 0}
          />
        </mesh>

        {/* The finger lip: the part a hand actually pulls. */}
        <mesh
          material={cued ? materials.brassLit : materials.brass}
          position={[0, CELL_IV.coverThickness / 2, CELL_IV.depth / 2 - CELL_IV.coverHandleDepth / 2]}
          castShadow
        >
          <boxGeometry args={[CELL_IV.width * 0.34, CELL_IV.coverThickness * 1.6, CELL_IV.coverHandleDepth]} />
        </mesh>

        {/* A generous invisible volume, because the visible hardware is only
            about 20 CSS px across on a folded Fold. It travels WITH the cover,
            so it can never be a hit target floating where nothing is. */}
        {!open && (
          <mesh
            position={[0, CELL_IV.hitSize / 2, 0]}
            visible={false}
            onClick={(event) => { event.stopPropagation(); onOpen() }}
            onPointerOver={(event) => { event.stopPropagation(); document.body.style.cursor = 'pointer' }}
            onPointerOut={() => { document.body.style.cursor = 'auto' }}
          >
            <boxGeometry args={[CELL_IV.width, CELL_IV.hitSize, CELL_IV.depth]} />
          </mesh>
        )}
      </group>
    </group>
  )
}
