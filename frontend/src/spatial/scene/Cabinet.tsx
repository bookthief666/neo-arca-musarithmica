import { CARRIAGE, CASE, FOOT } from '../dimensions'
import type { ArcaMaterials } from '../materials'
import { BallFoot, CornerBracket, Fillet, RingHandle } from './Hardware'
import { makeBrassPlateTexture } from '../textures'
import { useMemo } from 'react'

/**
 * THE OUTER CASE.
 *
 * Built as five real boards around a hollow, not as a solid block: the carcass
 * has a back you can turn it around and look at, sides with visible thickness,
 * and an underside with feet. That is the whole point of M1.2 — the M1.1
 * cabinet was an illusion that only existed facing front.
 *
 * Origin convention: the cabinet is centred on X and Z, and y = 0 is the
 * underside of the plinth. So the object stands ON the ground plane the way a
 * real instrument stands on a desk.
 */
export function Cabinet({ materials, cued }: { materials: ArcaMaterials; cued: boolean }) {
  const { width, depth, bodyHeight, wall, plinth } = CASE
  const halfW = width / 2
  const halfD = depth / 2

  // The identity plate on the front of the carcass.
  const nameplate = useMemo(
    () => makeBrassPlateTexture(
      [
        { text: 'NEO-ARCA MVSARITHMICA', size: 40, gap: 14 },
        { text: 'ROMÆ · MDCL', size: 20 },
      ],
      { width: 640, height: 190 },
    ),
    [],
  )

  const y0 = plinth
  const bodyTop = y0 + bodyHeight
  /** Height of the opening the carriage runs out through. */
  const MOUTH = CARRIAGE.height + 0.008

  return (
    <group>
      {/* ---- plinth: the base moulding the carcass sits on ---- */}
      <mesh material={materials.woodDark} position={[0, plinth / 2, 0]} castShadow receiveShadow>
        <boxGeometry args={[width, plinth, depth]} />
      </mesh>

      {/* ---- four walls, each a board with real thickness ---- */}
      {/* back */}
      <mesh material={materials.wood} position={[0, y0 + bodyHeight / 2, -halfD + wall / 2]} castShadow receiveShadow>
        <boxGeometry args={[width, bodyHeight, wall]} />
      </mesh>
      {/* left */}
      <mesh material={materials.wood} position={[-halfW + wall / 2, y0 + bodyHeight / 2, 0]} castShadow receiveShadow>
        <boxGeometry args={[wall, bodyHeight, depth]} />
      </mesh>
      {/* right */}
      <mesh material={materials.wood} position={[halfW - wall / 2, y0 + bodyHeight / 2, 0]} castShadow receiveShadow>
        <boxGeometry args={[wall, bodyHeight, depth]} />
      </mesh>
      {/* Front apron: the upper part only, so the carriage can run out beneath
          it. The mouth is exactly the drawer's height plus its clearance — any
          taller and the cabinet front reads as a hole rather than as joinery. */}
      <mesh
        material={materials.wood}
        position={[0, bodyTop - (bodyHeight - MOUTH) / 2, halfD - wall / 2]}
        castShadow
        receiveShadow
      >
        <boxGeometry args={[width, bodyHeight - MOUTH, wall]} />
      </mesh>
      {/* The lintel above the mouth, showing the carcass's own thickness. */}
      <mesh material={materials.woodDark} position={[0, y0 + MOUTH + 0.002, halfD - wall - 0.001]}>
        <boxGeometry args={[width - wall * 2, 0.004, 0.006]} />
      </mesh>
      {/* floor */}
      <mesh material={materials.woodDark} position={[0, y0 + wall / 2, 0]} receiveShadow>
        <boxGeometry args={[width, wall, depth]} />
      </mesh>

      {/* ---- inlaid gold fillet on the outward faces ---- */}
      <Fillet
        width={width} height={bodyHeight - 0.05}
        position={[0, bodyTop - (bodyHeight - 0.05) / 2, halfD + 0.0004]}
        materials={materials} inset={0.014}
      />
      <Fillet
        width={width} height={bodyHeight - 0.02}
        position={[0, y0 + bodyHeight / 2, -halfD - 0.0004]}
        rotation={[0, Math.PI, 0]}
        materials={materials} inset={0.014}
      />
      <Fillet
        width={depth} height={bodyHeight - 0.02}
        position={[-halfW - 0.0004, y0 + bodyHeight / 2, 0]}
        rotation={[0, -Math.PI / 2, 0]}
        materials={materials} inset={0.014}
      />
      <Fillet
        width={depth} height={bodyHeight - 0.02}
        position={[halfW + 0.0004, y0 + bodyHeight / 2, 0]}
        rotation={[0, Math.PI / 2, 0]}
        materials={materials} inset={0.014}
      />

      {/* ---- the engraved identity plate ---- */}
      <mesh position={[0, bodyTop - 0.026, halfD + 0.0012]}>
        <planeGeometry args={[0.108, 0.032]} />
        <meshStandardMaterial map={nameplate} metalness={0.75} roughness={0.34} />
      </mesh>

      {/* ---- corner brackets on all four vertical edges ---- */}
      {([
        [-halfW, halfD, [0, 0, 0]],
        [halfW, halfD, [0, -Math.PI / 2, 0]],
        [halfW, -halfD, [0, Math.PI, 0]],
        [-halfW, -halfD, [0, Math.PI / 2, 0]],
      ] as const).map(([x, z, rot], i) => (
        <CornerBracket
          key={i}
          position={[x, y0 + bodyHeight / 2, z]}
          rotation={rot as [number, number, number]}
          height={bodyHeight - 0.004}
          materials={materials}
        />
      ))}

      {/* ---- ring handles on both ends ---- */}
      <RingHandle
        position={[-halfW - 0.0015, bodyTop - 0.036, 0]}
        rotation={[0, 0, Math.PI / 2]}
        materials={materials}
      />
      <RingHandle
        position={[halfW + 0.0015, bodyTop - 0.036, 0]}
        rotation={[0, 0, -Math.PI / 2]}
        materials={materials}
      />

      {/* ---- feet: the cabinet stands on something ---- */}
      {([
        [-halfW + FOOT.inset, halfD - FOOT.inset],
        [halfW - FOOT.inset, halfD - FOOT.inset],
        [-halfW + FOOT.inset, -halfD + FOOT.inset],
        [halfW - FOOT.inset, -halfD + FOOT.inset],
      ] as const).map(([x, z], i) => (
        <BallFoot key={i} position={[x, 0.004, z]} materials={materials} />
      ))}

      {/* ---- the clasp: the one lit affordance while the Arca is shut ---- */}
      <group position={[0, bodyTop + 0.001, halfD + 0.002]}>
        <mesh material={cued ? materials.brassLit : materials.brass} castShadow>
          <boxGeometry args={[0.03, 0.022, 0.004]} />
        </mesh>
        <mesh material={materials.brassDark} position={[0, -0.004, 0.0025]}>
          <torusGeometry args={[0.005, 0.0015, 8, 20]} />
        </mesh>
      </group>
    </group>
  )
}
