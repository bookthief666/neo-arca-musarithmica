import { useEffect, useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { CARRIAGE, FOLIO } from '../dimensions'
import type { ArcaMaterials } from '../materials'
import type { HistoricalExecution, HistoricalManifest, VoiceName } from '../../instrument/types'
import { getReadingFrames, type ReadingFrame } from '../../instrument/reading'

const VOICE_ORDER: VoiceName[] = ['cantus', 'altus', 'tenor', 'bassus']
const VOICE_TITLE: Record<VoiceName, string> = {
  cantus: 'CANTVS', altus: 'ALTVS', tenor: 'TENOR', bassus: 'BASSVS',
}
const LANE_INK: Record<VoiceName, string> = {
  cantus: '#8d3a28', altus: '#7d5c1e', tenor: '#35544c', bassus: '#413859',
}

/** Folio values come only from execution-parity frames, never a parallel computation path. */
function makeFolioTexture(execution: HistoricalExecution, frames: ReadingFrame[]) {
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
  const glyph = (pitch: string) => pitch.replace('b', '♭').replace('#', '♯')

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
    `${frames.length} events · ${execution.fragment.total_duration_minim_units} relative minim units`,
    W - 52, 104,
  )

  c.strokeStyle = 'rgba(58,42,24,0.5)'
  c.lineWidth = 2
  c.beginPath(); c.moveTo(52, 126); c.lineTo(W - 52, 126); c.stroke()

  const left = 52
  const nameW = 132
  const laneTop = 160
  const laneH = 84
  const cellW = (W - left - nameW - 52) / frames.length

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
    c.strokeStyle = 'rgba(58,42,24,0.22)'
    c.lineWidth = 1
    c.beginPath(); c.moveTo(left + nameW, y + 10); c.lineTo(W - 52, y + 10); c.stroke()

    frames.forEach((frame, index) => {
      const x = left + nameW + cellW * (index + 0.5)
      const value = frame.voices[voice]
      c.textAlign = 'center'
      c.fillStyle = LANE_INK[voice]
      c.font = `600 34px ${DISPLAY}`
      c.fillText(glyph(value.pitchClass), x, y + 2)
      c.fillStyle = '#6f5a3b'
      c.font = `17px ${MONO}`
      c.fillText(String(value.degree), x, y + 26)
    })
  })

  const ty = laneTop + laneH * 4
  c.fillStyle = '#6f5a3b'
  c.font = `20px ${MONO}`
  c.textAlign = 'left'
  c.letterSpacing = '3px'
  c.fillText('TEMPVS', left + 16, ty + 6)
  c.letterSpacing = '0px'
  frames.forEach((frame, index) => {
    const x = left + nameW + cellW * (index + 0.5)
    c.textAlign = 'center'
    c.fillStyle = '#43301c'
    c.font = `25px ${DISPLAY}`
    c.fillText(frame.duration.glyph, x, ty)
    c.fillStyle = '#6f5a3b'
    c.font = `17px ${MONO}`
    c.fillText(String(frame.duration.relativeMinimUnits), x, ty + 26)
  })

  c.fillStyle = '#6f5a3b'
  c.font = `italic 19px ${DISPLAY}`
  c.textAlign = 'center'
  c.fillText(
    'Kernel-parity symbolic pitch classes and relative durations — no octave, register or metre inferred.',
    W / 2, H - 38,
  )

  const texture = new THREE.CanvasTexture(element)
  texture.colorSpace = THREE.SRGBColorSpace
  texture.anisotropy = 16
  return texture
}

export function Revelation({
  materials, manifest, execution, shown, reducedMotion, travelRef,
}: {
  materials: ArcaMaterials
  manifest: HistoricalManifest
  execution: HistoricalExecution | null
  shown: boolean
  reducedMotion: boolean
  travelRef: React.RefObject<number>
}) {
  const group = useRef<THREE.Group>(null)
  const frames = useMemo(
    () => (execution ? getReadingFrames(manifest, execution) : null),
    [manifest, execution],
  )
  const texture = useMemo(
    () => (execution && frames ? makeFolioTexture(execution, frames) : null),
    [execution, frames],
  )
  useEffect(() => () => texture?.dispose(), [texture])

  useFrame((_, delta) => {
    const node = group.current
    if (!node) return
    const travel = travelRef.current ?? 0
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
      <mesh rotation={[-Math.PI / 2 + 0.08, 0, 0]} castShadow receiveShadow>
        <planeGeometry args={[FOLIO.width, FOLIO.height]} />
        <meshStandardMaterial map={texture} roughness={0.9} metalness={0} side={THREE.DoubleSide} />
      </mesh>
      <mesh material={materials.brass} position={[0, 0.001, -FOLIO.height * 0.47]} castShadow>
        <boxGeometry args={[FOLIO.width * 0.98, 0.003, 0.006]} />
      </mesh>
    </group>
  )
}
