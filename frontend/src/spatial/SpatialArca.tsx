import { Suspense, useCallback, useEffect, useMemo, useRef } from 'react'
import { Canvas } from '@react-three/fiber'
import * as THREE from 'three'
import { CARRIAGE } from './dimensions'
import {
  deriveCameraMode, dollyBy, orbitBy, useCameraDirector, useOrbitState, useResetView,
} from './camera'
import { useArcaMaterials } from './materials'
import { Cabinet } from './scene/Cabinet'
import { Lid } from './scene/Lid'
import { StudioEnvironment } from './scene/Environment'
import { Interior } from './scene/Interior'
import { Carriage, type ChannelReading } from './scene/Carriage'
import { Virgae } from './scene/Virgae'
import { Revelation } from './scene/Revelation'
import { SpatialTestProbe } from './TestProbe'
import { shouldExtendCarriage, targetLane, workspaceOffsets } from './operative'
import type {
  HistoricalManifest,
  InstrumentAffordance,
  InstrumentState,
  InstrumentView,
  RodTemplate,
} from '../instrument/types'

/**
 * THE SPATIAL ARCA.
 *
 * This renderer is PRESENTATION ONLY. It reads canonical instrument state and
 * dispatches canonical actions; it owns no musical state, no alignment logic
 * and no historical data of its own. Every verb the reader performs in the
 * scene resolves to an action the M1.1 reducer already understood.
 */

export interface SpatialArcaProps {
  manifest: HistoricalManifest
  state: InstrumentState
  view: InstrumentView
  nextAffordance: InstrumentAffordance
  alignmentReady: boolean
  executionReady: boolean
  onOpen: () => void
  onClose: () => void
  onFocusBank: (bank: 1 | 2 | 3) => void
  onFocusCell: (cell: number) => void
  /** Lift a stored virga into the hand. Dispatches canonical RETRIEVE_ROD. */
  onRetrieveRod: (template: RodTemplate) => void
  /** Seat the held virga in its channel. Dispatches canonical PLACE_HELD_ROD. */
  onPlaceHeldRod: () => void
  onMoveRod: (instanceId: string, offset: number) => void
  onEngageTone: () => void
  onExecute: () => void
}

/** Height of the reading lever, standing proud of the drawer's front rail. */
const CARRIAGE_LEVER_Y = CARRIAGE.y + CARRIAGE.height + 0.006

/** Lighting: a warm key, a cool fill, and enough ambient that walnut stays wood. */
function Lighting({ reducedMotion }: { reducedMotion: boolean }) {
  const key = useRef<THREE.DirectionalLight>(null)
  useEffect(() => {
    const light = key.current
    if (!light) return
    // A tight shadow camera around a 28 cm object keeps the map sharp cheaply.
    light.shadow.camera.left = -0.3
    light.shadow.camera.right = 0.3
    light.shadow.camera.top = 0.3
    light.shadow.camera.bottom = -0.3
    light.shadow.camera.near = 0.05
    light.shadow.camera.far = 1.6
    light.shadow.bias = -0.0009
    light.shadow.normalBias = 0.004
    light.shadow.camera.updateProjectionMatrix()
  }, [])
  return (
    <>
      <ambientLight intensity={0.42} color="#ffeccc" />
      <hemisphereLight intensity={0.44} color="#ffe2b8" groundColor="#2a1a10" />
      <directionalLight
        ref={key}
        position={[0.36, 0.52, 0.34]}
        intensity={1.9}
        color="#fff1d6"
        castShadow={!reducedMotion}
        shadow-mapSize={[1024, 1024]}
      />
      {/* Fill from the opposite side so the back and left face never go black. */}
      <directionalLight position={[-0.42, 0.24, -0.3]} intensity={0.75} color="#c8d8ff" />
      {/* A low bounce, standing in for light coming back off the desk. */}
      <directionalLight position={[0, -0.3, 0.2]} intensity={0.25} color="#ffd9a8" />
    </>
  )
}

/** The desk the instrument stands on. Restrained: the Arca is the hero. */
function Desk() {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]} receiveShadow>
      <planeGeometry args={[3, 3]} />
      <meshStandardMaterial color="#241813" roughness={0.94} metalness={0} />
    </mesh>
  )
}

/**
 * Orbit input. Gesture ownership is explicit: a drag that begins on an
 * interactive part of the instrument marks itself handled and the camera
 * ignores it, so dragging a virga never spins the cabinet.
 */
function useOrbitInput(orbit: ReturnType<typeof useOrbitState>) {
  const drag = useRef<{ id: number; x: number; y: number } | null>(null)
  const pinch = useRef<{ distance: number } | null>(null)
  const points = useRef(new Map<number, { x: number; y: number }>())

  const onPointerDown = useCallback((event: React.PointerEvent) => {
    points.current.set(event.pointerId, { x: event.clientX, y: event.clientY })
    if (points.current.size === 2) {
      const [a, b] = [...points.current.values()]
      pinch.current = { distance: Math.hypot(a.x - b.x, a.y - b.y) }
      drag.current = null
      return
    }
    // `data-arca-grab` is set by any scene part that is handling this gesture.
    if (document.body.dataset.arcaGrab === 'active') return
    drag.current = { id: event.pointerId, x: event.clientX, y: event.clientY }
  }, [])

  const onPointerMove = useCallback((event: React.PointerEvent) => {
    if (points.current.has(event.pointerId)) {
      points.current.set(event.pointerId, { x: event.clientX, y: event.clientY })
    }
    const state = orbit.current
    if (!state) return

    if (pinch.current && points.current.size === 2) {
      const [a, b] = [...points.current.values()]
      const distance = Math.hypot(a.x - b.x, a.y - b.y)
      if (pinch.current.distance > 0) dollyBy(state, pinch.current.distance / distance)
      pinch.current.distance = distance
      return
    }
    const active = drag.current
    if (!active || active.id !== event.pointerId) return
    if (document.body.dataset.arcaGrab === 'active') { drag.current = null; return }
    orbitBy(state, (event.clientX - active.x) * -0.0085, (event.clientY - active.y) * 0.0065)
    active.x = event.clientX
    active.y = event.clientY
  }, [orbit])

  const onPointerUp = useCallback((event: React.PointerEvent) => {
    points.current.delete(event.pointerId)
    if (points.current.size < 2) pinch.current = null
    if (drag.current?.id === event.pointerId) drag.current = null
  }, [])

  // Desktop dolly. Touch uses the pinch above; both end up calling dollyBy, so
  // an XR thumbstick later has exactly one function to drive.
  const onWheel = useCallback((event: React.WheelEvent) => {
    const state = orbit.current
    if (!state) return
    dollyBy(state, event.deltaY > 0 ? 1.08 : 1 / 1.08)
  }, [orbit])

  return { onPointerDown, onPointerMove, onPointerUp, onPointerCancel: onPointerUp, onWheel }
}

export function SpatialArca(props: SpatialArcaProps) {
  const orbit = useOrbitState()
  const reset = useResetView(orbit)
  const input = useOrbitInput(orbit)

  return (
    <div className="spatial-stage" {...input}>
      <Canvas
        shadows={!props.state.reducedMotion}
        // Bounded DPR: the Fold reports 3x, and a 3x framebuffer of this scene
        // buys nothing visible while costing most of the frame budget.
        dpr={[1, 2]}
        gl={{ antialias: true, powerPreference: 'high-performance' }}
        camera={{ fov: 34, near: 0.01, far: 12, position: [0.34, 0.26, 0.5] }}
        onCreated={({ gl, scene }) => {
          gl.toneMapping = THREE.ACESFilmicToneMapping
          // Walnut should stay walnut at a glancing angle: at a higher exposure
          // the lid's specular blew out to near-white from behind.
          gl.toneMappingExposure = 0.94
          scene.background = new THREE.Color('#120c09')
          // Far plane sits beyond the camera's own MAX_DISTANCE. At 0.9/2.2 a
          // tall Fold viewport backed the camera off to 2.37 m in the open
          // framing and the fog swallowed the entire instrument: opening the
          // Arca at 390 x 844 produced an empty screen.
          scene.fog = new THREE.Fog('#120c09', 1.4, 3.6)
        }}
      >
        <Suspense fallback={null}>
          <SceneWithOrbit {...props} orbit={orbit} />
        </Suspense>
      </Canvas>
      <button type="button" className="spatial-reset" onClick={reset}>
        Recentre the instrument
      </button>
    </div>
  )
}

/** Bridges the orbit ref created outside the Canvas into the render loop. */
function SceneWithOrbit(props: SpatialArcaProps & { orbit: ReturnType<typeof useOrbitState> }) {
  const { orbit, ...rest } = props
  const materials = useArcaMaterials()
  useEffect(() => () => materials.dispose(), [materials])
  // Presentation only: the mode is derived from canonical state every render
  // and nothing about the camera is ever written back into the instrument.
  useCameraDirector(orbit, deriveCameraMode(rest.state), rest.state.reducedMotion)

  const isOpen = rest.state.phase !== 'dormant'
  // The drawer comes out as soon as a carrier is LIFTED, so the destination is
  // revealed before the reader commits to placing, and stays out thereafter.
  const carriageOut = shouldExtendCarriage(rest.state)
  const activeTargetLane = targetLane(rest.manifest, rest.state)
  const channelOffsets = workspaceOffsets(rest.manifest, rest.state)
  const travelRef = useRef(0)

  const sources = useMemo(
    () => new Map(rest.manifest.source_columns.map((source) => [source.id, source])),
    [rest.manifest],
  )

  /**
   * What the reader presents to each channel. This is READ from canonical
   * state — the scene asks the model what is under the rule, it never decides.
   */
  const readings: ChannelReading[] = useMemo(
    () => rest.manifest.rod_templates.map((template) => {
      const seated = rest.state.rods.find(
        (rod) => rod.template_id === template.template_id && rod.location === 'workspace',
      )
      if (!seated) return { occupied: false, verified: false }
      const source = sources.get(seated.source_column_id)
      const band = source?.bands[seated.vertical_offset]
      return { occupied: true, verified: band?.status === 'verified' }
    }),
    [rest.manifest, rest.state.rods, sources],
  )

  return (
    <>
      <StudioEnvironment />
      <SpatialTestProbe />
      <Lighting reducedMotion={rest.state.reducedMotion} />
      <Desk />
      <Cabinet materials={materials} cued={rest.nextAffordance === 'open_arca'} />
      <Lid
        materials={materials}
        manifest={rest.manifest}
        open={isOpen}
        reducedMotion={rest.state.reducedMotion}
        toneEngaged={rest.state.toneEngaged}
        cued={rest.nextAffordance === 'open_arca'}
        onToggle={() => (isOpen ? rest.onClose() : rest.onOpen())}
        onEngageTone={rest.onEngageTone}
        toneAvailable={rest.alignmentReady || rest.state.toneEngaged}
        toneCued={rest.nextAffordance === 'engage_tone_ii'}
      />
      {isOpen && (
        <Interior
          materials={materials}
          state={rest.state}
          nextAffordance={rest.nextAffordance}
          onFocusBank={rest.onFocusBank}
          onFocusCell={rest.onFocusCell}
        />
      )}
      <Carriage
        materials={materials}
        extended={carriageOut}
        reducedMotion={rest.state.reducedMotion}
        readings={readings}
        concordant={rest.alignmentReady}
        travelRef={travelRef}
        targetLane={activeTargetLane}
        onPlaceHeldRod={rest.onPlaceHeldRod}
        channelOffsets={channelOffsets}
      />
      {isOpen && (
        <Virgae
          manifest={rest.manifest}
          state={rest.state}
          materials={materials}
          nextAffordance={rest.nextAffordance}
          travelRef={travelRef}
          onRetrieveRod={rest.onRetrieveRod}
          onPlaceHeldRod={rest.onPlaceHeldRod}
          onMoveRod={rest.onMoveRod}
        />
      )}
      <Revelation
        materials={materials}
        execution={rest.state.execution}
        shown={rest.view === 'revelation'}
        reducedMotion={rest.state.reducedMotion}
        travelRef={travelRef}
      />
      {/* The reading lever: the act that sends the alignment to the kernel. */}
      {rest.executionReady && (
        <mesh
          position={[0.086, CARRIAGE_LEVER_Y, 0.052]}
          onClick={(event) => { event.stopPropagation(); rest.onExecute() }}
          onPointerOver={(event) => { event.stopPropagation(); document.body.style.cursor = 'pointer' }}
          onPointerOut={() => { document.body.style.cursor = 'auto' }}
          castShadow
        >
          <cylinderGeometry args={[0.009, 0.011, 0.016, 18]} />
          <meshStandardMaterial
            color="#e8cb87" metalness={0.9} roughness={0.2}
            emissive={rest.nextAffordance === 'read_transverse' ? '#5a3f12' : '#000000'}
            emissiveIntensity={rest.nextAffordance === 'read_transverse' ? 0.7 : 0}
          />
        </mesh>
      )}
    </>
  )
}
