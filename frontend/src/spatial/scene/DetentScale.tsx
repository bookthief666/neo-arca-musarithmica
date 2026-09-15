import { useMemo } from 'react'
import { CARRIAGE, VIRGA } from '../dimensions'
import type { ArcaMaterials } from '../materials'
import { makeDetentScaleTexture } from '../textures'
import { virgaOriginZ } from './stations'

/**
 * THE BAND INDEX beside a working channel.
 *
 * "Slide each virga until band I lies beneath the reader" is an instruction
 * about a thing the M1.2 machine never showed. A virga could be at any of ten
 * canonical offsets and the carriage said nothing about which, so the reader
 * was asked to reach a station they could not see and count in a unit they had
 * not been given.
 *
 * So each channel carries a slim engraved strip running I to X, and a small
 * brass index that stands at whichever band that channel is currently
 * presenting. The strip is one canvas texture rather than ten labels, and the
 * index is driven by the canonical vertical_offset — never by a pointer
 * position, so what the strip says and what the kernel would execute cannot
 * drift apart.
 */

/** Where band `offset`'s centre lies along the channel, in carriage-local Z. */
function bandCentreZ(offset: number): number {
  // The rod's origin sits at virgaOriginZ(offset) when band `offset` is under
  // the reader, and the reader is the fixed station. So the strip is laid out
  // in the rod's own band pitch, measured from the station.
  return virgaOriginZ(offset) - virgaOriginZ(0)
}

export function DetentScale({
  laneX, verticalOffset, cued, materials,
}: {
  laneX: number
  /** Canonical band this channel presents, or null when no carrier is seated. */
  verticalOffset: number | null
  cued: boolean
  materials: ArcaMaterials
}) {
  const texture = useMemo(() => makeDetentScaleTexture(VIRGA.bandCount), [])

  const width = 0.008
  const y = CARRIAGE.y + CARRIAGE.wall + 0.0006
  const length = VIRGA.bandLength * VIRGA.bandCount
  /** Centre of the strip, so its ten cells line up with the ten stations. */
  const centreZ = (bandCentreZ(0) + bandCentreZ(VIRGA.bandCount - 1)) / 2
  /** The gutter between this channel's guide lip and the next channel's. */
  const x = laneX + CARRIAGE.channelPitch / 2

  return (
    <group name={`detents:${Math.round(laneX * 1000)}`}>
      {/* The engraved strip itself, let into the drawer floor. */}
      <mesh position={[x, y, centreZ]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[width, length]} />
        <meshStandardMaterial map={texture} metalness={0.72} roughness={0.42} />
      </mesh>

      {/* The index: a small brass pointer standing at the presented band. It
          is absent, not parked at zero, when the channel is empty — an index
          pointing at a band no carrier is presenting would be a lie. */}
      {verticalOffset !== null && (
        <mesh
          material={cued ? materials.brassLit : materials.brass}
          position={[x, y + 0.0018, bandCentreZ(verticalOffset)]}
          castShadow
        >
          <boxGeometry args={[width + 0.003, 0.0034, VIRGA.bandLength * 0.4]} />
        </mesh>
      )}
    </group>
  )
}
