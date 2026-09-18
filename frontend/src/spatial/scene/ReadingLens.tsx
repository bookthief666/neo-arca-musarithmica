import { useEffect, useMemo, useRef } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import * as THREE from 'three'
import type { ReadingFrame } from '../../instrument/reading'
import { CARRIAGE, VIRGA } from '../dimensions'
import { useReaderDrag } from '../readerInteraction'
import { EVENT_READER_DETENTS, EVENT_READER_LOCAL_MAX, EVENT_READER_LOCAL_MIN } from './stations'
import { buildReadingLensDisplay } from './readingLensModel'

const LENS_LOCAL_Y = 0.035
const HANDLE_LOCAL_Y = 0.041

function makeLensTexture(frame: ReadingFrame) {
  const display = buildReadingLensDisplay(frame)
  const canvas = document.createElement('canvas')
  canvas.width = 1024
  canvas.height = 512
  const context = canvas.getContext('2d')
  if (!context) throw new Error('2D context unavailable for event reader.')

  const ground = context.createLinearGradient(0, 0, canvas.width, canvas.height)
  ground.addColorStop(0, '#f5ecd6')
  ground.addColorStop(1, '#d8c9a8')
  context.fillStyle = ground
  context.fillRect(0, 0, canvas.width, canvas.height)
  context.strokeStyle = 'rgba(67,48,28,0.45)'
  context.lineWidth = 3
  context.strokeRect(18, 18, canvas.width - 36, canvas.height - 36)

  context.fillStyle = '#281a09'
  context.textAlign = 'left'
  context.font = '700 48px Georgia, serif'
  context.fillText(display.eventLabel, 48, 76)
  context.font = '25px ui-monospace, monospace'
  context.fillStyle = '#6c5639'
  context.fillText(display.railLabel, 48, 118)

  context.font = '600 39px Georgia, serif'
  context.fillStyle = '#281a09'
  display.voiceLabels.forEach((label, index) => {
    const column = index % 2
    const row = Math.floor(index / 2)
    context.fillText(label, 56 + column * 470, 200 + row * 84)
  })

  context.strokeStyle = 'rgba(67,48,28,0.28)'
  context.beginPath()
  context.moveTo(48, 370)
  context.lineTo(976, 370)
  context.stroke()
  context.font = '32px ui-monospace, monospace'
  context.fillStyle = '#43301c'
  context.fillText(display.durationLabel, 48, 425)
  context.font = '20px ui-monospace, monospace'
  context.fillStyle = '#756143'
  context.fillText('DRAG READER · EVENTS 1–6 · SOURCE → FIXED p.51 TONE-II → PITCH CLASS', 48, 470)

  const texture = new THREE.CanvasTexture(canvas)
  texture.colorSpace = THREE.SRGBColorSpace
  texture.anisotropy = 16
  return texture
}

/** State-free H1 inspection lens over one validated source/executed frame. */
export function ReadingLens({ frame, travelRef, onPosition }: {
  frame: ReadingFrame
  travelRef: React.RefObject<number>
  onPosition: (position: number) => void
}) {
  const constraint = useRef<THREE.Group>(null)
  const camera = useThree((state) => state.camera)
  const canvas = useThree((state) => state.gl.domElement)
  const texture = useMemo(() => makeLensTexture(frame), [frame])
  useEffect(() => () => texture.dispose(), [texture])

  const math = useMemo(() => ({
    raycaster: new THREE.Raycaster(),
    ndc: new THREE.Vector2(),
    origin: new THREE.Vector3(),
    axis: new THREE.Vector3(),
    rotation: new THREE.Quaternion(),
  }), [])

  const begin = useReaderDrag((event) => {
    const node = constraint.current
    const rect = canvas.getBoundingClientRect()
    if (!node || rect.width <= 0 || rect.height <= 0) return null
    math.ndc.set(
      ((event.clientX - rect.left) / rect.width) * 2 - 1,
      -((event.clientY - rect.top) / rect.height) * 2 + 1,
    )
    math.raycaster.setFromCamera(math.ndc, camera)
    node.position.z = travelRef.current
    node.updateWorldMatrix(true, false)
    // Project onto the same local Y plane as the visible/grabbable handle.
    // Using the group origin here shifts the perspective projection because
    // the handle itself sits above that origin; the endpoint then snaps one
    // detent short even though the pointer is over the visible endpoint.
    math.origin.set(0, HANDLE_LOCAL_Y, 0)
    node.localToWorld(math.origin)
    node.getWorldQuaternion(math.rotation)
    math.axis.set(0, 0, 1).applyQuaternion(math.rotation).normalize()
    return {
      ray: math.raycaster.ray,
      worldOrigin: math.origin,
      worldAxis: math.axis,
      minLocal: EVENT_READER_LOCAL_MIN,
      maxLocal: EVENT_READER_LOCAL_MAX,
      count: 6,
    }
  }, onPosition)

  useFrame(() => {
    if (constraint.current) constraint.current.position.z = travelRef.current
  })

  const position = Math.max(0, Math.min(5, frame.position))
  const detent = EVENT_READER_DETENTS[position]
  const startDrag = (event: import('@react-three/fiber').ThreeEvent<PointerEvent>) => {
    event.stopPropagation()
    begin(event.nativeEvent)
  }
  const showGrabCursor = (event: import('@react-three/fiber').ThreeEvent<PointerEvent>) => {
    event.stopPropagation()
    document.body.style.cursor = 'grab'
  }

  return (
    <group
      ref={constraint}
      position={[0, CARRIAGE.y + CARRIAGE.wall + VIRGA.thickness + 0.016, travelRef.current]}
    >
      <mesh position={[0, 0, (EVENT_READER_LOCAL_MIN + EVENT_READER_LOCAL_MAX) / 2]}>
        <boxGeometry args={[0.004, 0.004, EVENT_READER_LOCAL_MAX - EVENT_READER_LOCAL_MIN]} />
        <meshStandardMaterial color="#8e7442" metalness={0.8} roughness={0.28} />
      </mesh>
      {EVENT_READER_DETENTS.map((value, index) => (
        <mesh key={index} position={[0, 0.003, value]}>
          <sphereGeometry args={[0.0042, 12, 8]} />
          <meshStandardMaterial color={index === position ? '#f4d88e' : '#796438'} metalness={0.75} roughness={0.3} />
        </mesh>
      ))}

      <mesh
        position={[0, HANDLE_LOCAL_Y, detent]}
        onPointerDown={startDrag}
        onPointerOver={showGrabCursor}
        onPointerOut={() => { document.body.style.cursor = 'auto' }}
        castShadow
      >
        <boxGeometry args={[0.058, 0.012, 0.018]} />
        <meshStandardMaterial
          color="#d7bb77"
          metalness={0.78}
          roughness={0.3}
          emissive="#5a3f12"
          emissiveIntensity={0.35}
        />
      </mesh>

      {/* Fold-first direct manipulation: the event folio itself is a generous
          drag surface. The gold grip remains the mechanical cue, but the user
          does not need pixel-perfect contact with it to own the reader. */}
      <mesh
        position={[0, LENS_LOCAL_Y, -0.006]}
        rotation={[-Math.PI / 2, 0, 0]}
        onPointerDown={startDrag}
        onPointerOver={showGrabCursor}
        onPointerOut={() => { document.body.style.cursor = 'auto' }}
      >
        <planeGeometry args={[0.15, 0.075]} />
        <meshStandardMaterial map={texture} roughness={0.88} metalness={0} side={THREE.DoubleSide} />
      </mesh>
    </group>
  )
}