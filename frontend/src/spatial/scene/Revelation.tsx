import { useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { CARRIAGE, FOLIO } from '../dimensions'
import type { ArcaMaterials } from '../materials'
import type { HistoricalExecution, VoiceName } from '../../instrument/types'

/**
 * THE REVELATION FOLIO.
 *
 * A sheet the machine prints and pushes out of the front of the carriage. It
 * rides with the drawer, because the drawer is what produced it.
 *
 * WHAT IS ON IT, AND WHAT IS NOT. The four voices are printed as the kernel
 * returns them: a symbolic pitch class and the degree it came from, in event
 * order, with the relative minim count beneath. The construction sheet shows
 * staff notation on this panel; that is generated decoration, and drawing
 * staves here would assert a register, a clef and a metre that the historical
 * fragment explicitly does not carry. So the folio prints four ruled ink lanes
 * and says so.
 */

const VOICE_ORDER: VoiceName[] = ['cantus', 'altus', 'tenor', 'bassus']
const VOICE_TITLE: Record<VoiceName, string> = {
  cantus: 'CANTVS', altus: 'ALTVS', tenor: 'TENOR', bassus: 'BASSVS',
}
const LANE_INK: Record<VoiceName, string> = {
  cantus: '#8d3a28', altus: '#7d5c1e', tenor: '#35544c', bassus: '#413859',
}

function makeFolioTexture(execution: HistoricalExecution) {
  const W = 1024
  const H = 640
  const element = document.createElement('canvas')
  element.width = W
  element.height = H
  const c = element.getContext('2d')
  if (!c) throw new Error('2D context unavailable for the revelation folio.')

  const wash = c.createLinearGradient(0, 0, W * 0.3, H)
  wash.addColorStop(0, '#fdf9ef'); wash.addColorStop(0.6, '#f4ecd9'); wash.addColorStop(1, '#e8dcc2')
  c.fillStyle = wash
  c.fillRect(0, 0, W, H)

  const DISPLAY = '"Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif'
  const MONO = 'ui-monospace, "DejaVu Sans Mono", Menlo, monospace'
  const events = execution.fragment.events
  const glyph = (p: string) => p.replace('b', '♭').replace('#', '♯')

  c.textAlign = 'left'
  c.fillStyle = '#6f5a3b'
  c.font = `19px ${MONO}`
  c.letterSpacing = '4px'
  c.fillText('PRINT_1650 · VERIFIED HISTORICAL FRAGMENT', 52, 56)
  c.letterSpacing = '0px'

  c.fillStyle = '#241705'
  c.font = `600 44px ${DISPLAY}`
  c.fillText('REVELATIO IV VOCVM', 52, 106)

  c.fillStyle = '#6f5a3b'
  c.font = `20px ${MONO}`
  c.textAlign = 'right'
  c.fillText(
    `${events.length} events · ${execution.fragment.total_duration_minim_units} relative minim units`,
    W - 52, 104,
  )

  c.strokeStyle = 'rgba(58,42,24,0.5)'
  c.lineWidth = 2
  c.beginPath(); c.moveTo(52, 126); c.lineTo(W - 52, 126); c.stroke()

  const left = 52
  const nameW = 132
  const laneTop = 160
  const laneH = 84
  const cellW = (W - left - nameW - 52) / events.length

  VOICE_ORDER.forEach((voice, row) => {
    const y = laneTop + laneH * row
    c.fillStyle = LANE_INK[voice]
    c.fillRect(left, y - 26, 5, 56)
    c.fillStyle = '#43301c'
    c.font = `20px ${MONO}`
    c.textAlign = 'left'
    c.letterSpacing = '3px'
    c.fillText(VOICE_TITLE[voice], left + 16, y + 6)
    c.letterSpacing = '0px'

    // The ruled lane the events sit on.
    c.strokeStyle = 'rgba(58,42,24,0.22)'
    c.lineWidth = 1
    c.beginPath(); c.moveTo(left + nameW, y + 10); c.lineTo(W - 52, y + 10); c.stroke()

    events.forEach((event, index) => {
      const x = left + nameW + cellW * (index + 0.5)
      const v = event.voices[voice]
      c.textAlign = 'center'
      c.fillStyle = LANE_INK[voice]
      c.font = `600 34px ${DISPLAY}`
      c.fillText(glyph(v.pitch_class), x, y + 2)
      c.fillStyle = '#6f5a3b'
      c.font = `17px ${MONO}`
      c.fillText(String(v.degree), x, y + 26)
    })
  })

  // TEMPVS: relative duration only.
  const ty = laneTop + laneH * 4
  c.fillStyle = '#6f5a3b'
  c.font = `20px ${MONO}`
  c.textAlign = 'left'
  c.letterSpacing = '3px'
  c.fillText('TEMPVS', left + 16, ty + 6)
  c.letterSpacing = '0px'
  events.forEach((event, index) => {
    const x = left + nameW + cellW * (index + 0.5)
    c.textAlign = 'center'
    c.fillStyle = '#43301c'
    c.font = `30px ${DISPLAY}`
    c.fillText(event.duration_symbol === 'minim' ? '♩' : '\u{1D15D}', x, ty + 2)
    c.fillStyle = '#6f5a3b'
    c.font = `17px ${MONO}`
    c.fillText(String(event.duration_minim_units), x, ty + 26)
  })

  c.fillStyle = '#6f5a3b'
  c.font = `italic 19px ${DISPLAY}`
  c.textAlign = 'center'
  c.fillText(
    'Symbolic pitch classes and relative durations only — no octave, register or metre is inferred.',
    W / 2, H - 38,
  )

  const texture = new THREE.CanvasTexture(element)
  texture.colorSpace = THREE.SRGBColorSpace
  texture.anisotropy = 16
  return texture
}

export function Revelation({
  materials, execution, shown, reducedMotion, travelRef,
}: {
  materials: ArcaMaterials
  execution: HistoricalExecution | null
  shown: boolean
  reducedMotion: boolean
  travelRef: React.RefObject<number>
}) {
  const group = useRef<THREE.Group>(null)
  const texture = useMemo(() => (execution ? makeFolioTexture(execution) : null), [execution])

  useFrame((_, delta) => {
    const node = group.current
    if (!node) return
    const travel = travelRef.current ?? 0
    // Far enough forward that the drawer front and its knobs stop clipping the
    // top voice lane — the sheet has to be readable, not merely present.
    const outZ = CARRIAGE.depth / 2 + FOLIO.height * 0.66
    const goalZ = travel + (shown ? outZ : CARRIAGE.depth / 2 - 0.02)
    const goalY = CARRIAGE.y + (shown ? 0.004 : -0.02)
    if (reducedMotion) {
      node.position.set(0, goalY, goalZ)
    } else {
      node.position.z = THREE.MathUtils.lerp(node.position.z, goalZ, 1 - Math.pow(0.004, delta))
      node.position.y = THREE.MathUtils.lerp(node.position.y, goalY, 1 - Math.pow(0.004, delta))
    }
    node.visible = shown || node.position.y > CARRIAGE.y - 0.018
  })

  if (!texture) return null

  return (
    <group ref={group} position={[0, CARRIAGE.y - 0.02, CARRIAGE.depth / 2]}>
      {/* The sheet, lying almost flat as it slides out of the machine. */}
      <mesh rotation={[-Math.PI / 2 + 0.08, 0, 0]} castShadow receiveShadow>
        <planeGeometry args={[FOLIO.width, FOLIO.height]} />
        <meshStandardMaterial map={texture} roughness={0.9} metalness={0} side={THREE.DoubleSide} />
      </mesh>
      {/* A brass bar along its head, as if the machine gripped it to push. */}
      <mesh material={materials.brass} position={[0, 0.001, -FOLIO.height * 0.47]} castShadow>
        <boxGeometry args={[FOLIO.width * 0.98, 0.003, 0.006]} />
      </mesh>
    </group>
  )
}
