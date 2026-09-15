import { useMemo } from 'react'
import {
  BODY_TOP, CASE, CELL_IV, DECK_THICKNESS, DECK_TOP, INTERIOR, SLOT_DEPTH,
} from '../dimensions'
import type { ArcaMaterials } from '../materials'
import { makeBrassPlateTexture } from '../textures'
import type { InstrumentAffordance, InstrumentState } from '../../instrument/types'

/**
 * THE CARCASS INTERIOR: the bank rail, the compartment deck, and Cell IV.
 *
 * Cell IV is a real cavity with three slots cut into the deck. The slots exist
 * whether or not a virga is in them, which is what makes a removal legible: the
 * empty slot the carrier came out of is still there, still the right shape, and
 * still in the same place.
 *
 * The compartments either side of Cell IV are modelled but empty. The
 * construction sheet shows card stacks and a bound book in them; those are
 * generated decoration with no verified corpus behind them, so they are not
 * fabricated here. An empty sealed compartment is the honest depiction.
 */
export function Interior({
  materials, state, nextAffordance, onFocusBank, onFocusCell,
}: {
  materials: ArcaMaterials
  state: InstrumentState
  nextAffordance: InstrumentAffordance
  onFocusBank: (bank: 1 | 2 | 3) => void
  onFocusCell: (cell: number) => void
}) {
  const { width: iw, depth: idp, railDepth, railHeight, divider } = INTERIOR
  const backZ = -CASE.depth / 2 + CASE.wall
  const deckFrontZ = CASE.depth / 2 - CASE.wall
  const deckBackZ = backZ + railDepth
  const deckDepth = deckFrontZ - deckBackZ

  const plates = useMemo(() => ([
    { id: 1, text: 'DODECAMORVM', numeral: 'I', tarnished: false },
    { id: 2, text: 'HEXAMORVM', numeral: 'II', tarnished: true },
    { id: 3, text: 'FRAGMENTA', numeral: 'III', tarnished: true },
  ] as const).map((plate) => ({
    ...plate,
    texture: makeBrassPlateTexture(
      [{ text: plate.numeral, size: 22, gap: 8 }, { text: plate.text, size: 30 }],
      { width: 400, height: 190, tarnished: plate.tarnished },
    ),
  })), [])

  const bankCued = nextAffordance === 'focus_bank_i'
  const cellCued = nextAffordance === 'open_cell_iv'
  const cellOpen = state.focusedCell === 4

  const plateW = (iw - divider * 4) / 3

  return (
    <group>
      {/* ---- the compartment deck ---- */}
      <mesh
        material={materials.wood}
        position={[0, DECK_TOP - DECK_THICKNESS / 2, (deckBackZ + deckFrontZ) / 2]}
        receiveShadow
      >
        <boxGeometry args={[iw, DECK_THICKNESS, deckDepth]} />
      </mesh>

      {/* ---- the bank rail: three engraved brass plates on the back wall ---- */}
      <mesh material={materials.woodDark} position={[0, DECK_TOP + railHeight / 2, backZ + railDepth / 2]} receiveShadow>
        <boxGeometry args={[iw, railHeight, railDepth]} />
      </mesh>
      {plates.map((plate, index) => {
        const x = -iw / 2 + divider + plateW / 2 + index * (plateW + divider)
        const live = plate.id === 1
        return (
          <mesh
            key={plate.id}
            position={[x, DECK_TOP + railHeight * 0.58, backZ + railDepth + 0.0008]}
            onClick={live ? (event) => { event.stopPropagation(); onFocusBank(1) } : undefined}
            onPointerOver={live ? (event) => { event.stopPropagation(); document.body.style.cursor = 'pointer' } : undefined}
            onPointerOut={live ? () => { document.body.style.cursor = 'auto' } : undefined}
          >
            <planeGeometry args={[plateW * 0.92, railHeight * 0.66]} />
            <meshStandardMaterial
              map={plate.texture}
              metalness={plate.tarnished ? 0.55 : 0.8}
              roughness={plate.tarnished ? 0.62 : 0.3}
              emissive={live && bankCued ? '#5a3f12' : '#000000'}
              emissiveIntensity={live && bankCued ? 0.5 : 0}
            />
          </mesh>
        )
      })}

      {/* ---- dividers: the compartments either side of Cell IV ---- */}
      {[-1, 1].map((side) => {
        const outerEdge = side * (iw / 2)
        const cellEdge = side * (CELL_IV.width / 2)
        const centre = (outerEdge + cellEdge) / 2
        return (
          <group key={side}>
            <mesh
              material={materials.woodDark}
              position={[cellEdge, DECK_TOP + 0.011, (deckBackZ + deckFrontZ) / 2]}
              receiveShadow
              castShadow
            >
              <boxGeometry args={[divider, 0.022, deckDepth]} />
            </mesh>
            {/* A sealed compartment: modelled, empty, and plainly not in use. */}
            {/* Sunk a clear 3 mm below the deck: coplanar with it, these
                z-fought and streaked across the compartment floor. */}
            <mesh
              material={materials.void}
              position={[centre, DECK_TOP - 0.003, (deckBackZ + deckFrontZ) / 2]}
              rotation={[-Math.PI / 2, 0, 0]}
            >
              <planeGeometry args={[Math.abs(outerEdge - cellEdge) - divider, deckDepth - 0.01]} />
            </mesh>
          </group>
        )
      })}

      {/* ---- CELL IV: the operative cavity ---- */}
      <group>
        {/* The felt-lined floor of the cell. */}
        <mesh
          material={materials.felt}
          position={[0, DECK_TOP - SLOT_DEPTH, (deckBackZ + deckFrontZ) / 2]}
          rotation={[-Math.PI / 2, 0, 0]}
          receiveShadow
        >
          <planeGeometry args={[CELL_IV.width, CELL_IV.depth]} />
        </mesh>

        {/* Three slots, cut by four dividers. They stay whether or not a virga
            is in them — the empty slot is the proof of where one came from. */}
        {[-1, 0, 1].map((lane) => {
          const x = lane * CELL_IV.slotPitch
          return (
            <group key={lane}>
              {[-1, 1].map((edge) => (
                <mesh
                  key={edge}
                  material={materials.woodDark}
                  position={[x + edge * (CELL_IV.slotWidth / 2 + divider / 2), DECK_TOP - SLOT_DEPTH / 2, (deckBackZ + deckFrontZ) / 2]}
                  castShadow
                  receiveShadow
                >
                  <boxGeometry args={[divider, SLOT_DEPTH, CELL_IV.depth * 0.92]} />
                </mesh>
              ))}
            </group>
          )
        })}

        {/* The cell's own nameplate on the deck lip, and the surface that
            opens it. Clicking anywhere on the cell opens Cell IV. */}
        <mesh
          position={[0, DECK_TOP + 0.0004, deckFrontZ - 0.008]}
          rotation={[-Math.PI / 2, 0, 0]}
          onClick={(event) => { event.stopPropagation(); onFocusCell(4) }}
          onPointerOver={(event) => { event.stopPropagation(); document.body.style.cursor = 'pointer' }}
          onPointerOut={() => { document.body.style.cursor = 'auto' }}
        >
          <planeGeometry args={[CELL_IV.width, 0.014]} />
          <meshStandardMaterial
            color={cellOpen ? '#8a6f33' : '#c3a25c'}
            metalness={0.85}
            roughness={0.32}
            emissive={cellCued ? '#5a3f12' : '#000000'}
            emissiveIntensity={cellCued ? 0.6 : 0}
          />
        </mesh>
      </group>

      {/* ---- the carcass's inner faces, so the box reads as hollow ---- */}
      <mesh material={materials.woodDark} position={[0, (DECK_TOP + BODY_TOP) / 2, backZ + 0.0005]}>
        <planeGeometry args={[iw, BODY_TOP - DECK_TOP]} />
      </mesh>
      {[-1, 1].map((side) => (
        <mesh
          key={side}
          material={materials.woodDark}
          position={[side * (iw / 2), (DECK_TOP + BODY_TOP) / 2, 0]}
          rotation={[0, -side * Math.PI / 2, 0]}
        >
          <planeGeometry args={[idp, BODY_TOP - DECK_TOP]} />
        </mesh>
      ))}
    </group>
  )
}
