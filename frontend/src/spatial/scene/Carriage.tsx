import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { CARRIAGE, CASE, READER, VIRGA } from '../dimensions'
import type { ArcaMaterials } from '../materials'
import { KnobPull } from './Hardware'

/** Guide-lip height: below the rod's face, so the face stays readable. */
const LIP_HEIGHT = 0.006
/** Depth of each reading rail, front and back of the gap. */
const RAIL_DEPTH = 0.008

/**
 * THE PULL-OUT CARRIAGE and THE TRANSVERSE READER.
 *
 * The carriage is a real tray that runs forward out of the carcass mouth on two
 * rails. It is a child of the cabinet, so it travels along one axis and takes
 * its contents with it; the reader can see it emerge from the case rather than
 * appear beside it.
 *
 * THE READER is the part that has to teach. It is a brass bar crossing all
 * three channels at one station. Where it crosses a channel it carries a
 * shutter: a virga presenting a VERIFIED band opens that shutter and the
 * reading slot shows through; a virga presenting an untranscribed band leaves
 * it shut, and the slot is physically blocked at that channel. So continuity is
 * GEOMETRY — a slot that runs unbroken across all three, or a slot with a solid
 * plug in the middle of it — and it survives greyscale, colour-blindness and
 * reduced motion, none of which a red/green light would.
 */

export interface ChannelReading {
  /** Whether the band currently under the reader is verified. */
  verified: boolean
  /** Whether a virga is seated in this channel at all. */
  occupied: boolean
}

export function Carriage({
  materials, extended, reducedMotion, readings, concordant, children, onPullOut, travelRef,
}: {
  materials: ArcaMaterials
  extended: boolean
  reducedMotion: boolean
  readings: ChannelReading[]
  concordant: boolean
  children?: React.ReactNode
  onPullOut?: () => void
  /** Publishes the drawer's live Z so virgae can ride with it in world space. */
  travelRef?: React.RefObject<number>
}) {
  const group = useRef<THREE.Group>(null)

  // The drawer travels outside React so the slide costs no re-render.
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
  /** The bridge rides just clear of the virga's printed face. */
  const READER_Y = floorY + wall + VIRGA.thickness + READER.barHeight / 2 + 0.001
  /** The gap is one band wide, so exactly one band is presented at a time. */
  const READING_GAP = VIRGA.bandLength

  return (
    <group ref={group} position={[0, 0, 0]}>
      {/* ---- the drawer body: a real tray with a floor and four sides ---- */}
      <mesh material={materials.woodDark} position={[0, floorY + wall / 2, 0]} receiveShadow castShadow>
        <boxGeometry args={[CARRIAGE.width, wall, CARRIAGE.depth]} />
      </mesh>
      {/* back and sides */}
      <mesh material={materials.woodDark} position={[0, floorY + height / 2, -halfD + wall / 2]} castShadow>
        <boxGeometry args={[CARRIAGE.width, height, wall]} />
      </mesh>
      {[-1, 1].map((side) => (
        <mesh key={side} material={materials.woodDark} position={[side * (halfW - wall / 2), floorY + height / 2, 0]} castShadow>
          <boxGeometry args={[wall, height, CARRIAGE.depth]} />
        </mesh>
      ))}

      {/* ---- the drawer front: the face that shows when it is shut ---- */}
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

      {/* ---- runners: the rails the drawer rides on ---- */}
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

      {/* ---- three working channels, cut into the drawer floor ---- */}
      {[-1, 0, 1].map((lane) => {
        const x = lane * CARRIAGE.channelPitch
        return (
          <group key={lane}>
            {/* The channel's recessed bed. */}
            <mesh
              material={materials.felt}
              position={[x, floorY + wall + 0.0004, 0]}
              rotation={[-Math.PI / 2, 0, 0]}
              receiveShadow
            >
              <planeGeometry args={[CARRIAGE.channelWidth, CARRIAGE.depth - wall * 2]} />
            </mesh>
            {/* Guide lips either side: the virga cannot wander out of its channel. */}
            {/* Guide lips, kept deliberately lower than the rod's printed face:
                at full channel depth they buried the very thing the reader has
                come to look at. */}
            {[-1, 1].map((edge) => (
              <mesh
                key={edge}
                material={materials.woodDark}
                position={[x + edge * (CARRIAGE.channelWidth / 2 + 0.002), floorY + wall + LIP_HEIGHT / 2, 0]}
                castShadow
              >
                <boxGeometry args={[0.004, LIP_HEIGHT, CARRIAGE.depth - wall * 2]} />
              </mesh>
            ))}
          </group>
        )
      })}

      {/* ---- THE TRANSVERSE READER ---- */}
      {/* A bridge of two brass rails crossing every channel, with a reading gap
          between them exactly one band wide. The reader looks DOWN through the
          gap at whatever band each virga presents. Where a channel offers an
          untranscribed band, a brass shutter fills the gap over that channel
          and the pathway is plainly blocked — so a continuous reading is a
          continuous OPENING, and a broken one has a solid plug in it. */}
      <group position={[0, READER_Y, READER.stationZ]}>
        {[-1, 1].map((side) => (
          <mesh
            key={side}
            material={concordant ? materials.brassLit : materials.brass}
            position={[0, 0, side * (READING_GAP / 2 + RAIL_DEPTH / 2)]}
            castShadow
          >
            <boxGeometry args={[CARRIAGE.width - 0.01, READER.barHeight, RAIL_DEPTH]} />
          </mesh>
        ))}

        {/* Cheeks at both ends, tying the rails into one rigid bridge. */}
        {[-1, 1].map((side) => (
          <mesh
            key={side}
            material={materials.brass}
            position={[side * (CARRIAGE.width / 2 - 0.008), 0, 0]}
            castShadow
          >
            <boxGeometry args={[0.01, READER.barHeight * 1.3, READING_GAP + RAIL_DEPTH * 2]} />
          </mesh>
        ))}

        {/* Per-channel shutters: shut whenever that channel cannot be read. */}
        {[-1, 0, 1].map((lane, index) => {
          const reading = readings[index]
          const shut = !reading?.occupied || !reading.verified
          if (!shut) return null
          return (
            <mesh
              key={lane}
              material={materials.brassDark}
              position={[lane * CARRIAGE.channelPitch, -READER.barHeight * 0.1, 0]}
              castShadow
            >
              <boxGeometry args={[CARRIAGE.channelWidth + 0.004, READER.barHeight * 0.8, READING_GAP]} />
            </mesh>
          )
        })}

        {/* The medallion, lit only when the whole pathway is open. */}
        <mesh
          material={concordant ? materials.brassLit : materials.brassDark}
          position={[0, READER.barHeight * 0.75, 0]}
          rotation={[Math.PI / 2, 0, 0]}
          castShadow
        >
          <cylinderGeometry args={[0.0085, 0.0085, 0.004, 18]} />
        </mesh>
      </group>

      {children}
    </group>
  )
}
