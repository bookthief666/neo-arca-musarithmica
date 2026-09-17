import { Suspense, useEffect, useMemo, useRef } from 'react'
import { Canvas } from '@react-three/fiber'
import * as THREE from 'three'
import { CARRIAGE } from './dimensions'
import { useCameraDirector, useOrbitState, useResetView } from './camera'
import { useArcaMaterials } from './materials'
import { Cabinet } from './scene/Cabinet'
import { Lid } from './scene/Lid'
import { StudioEnvironment } from './scene/Environment'
import { Interior } from './scene/Interior'
import { Carriage } from './scene/Carriage'
import { Virgae } from './scene/Virgae'
import { Revelation } from './scene/Revelation'
import { ReadingLens } from './scene/ReadingLens'
import { useOrbitInput } from './orbitInput'
import { createSpatialGrabStore, SpatialGrabProvider } from './grabOwnership'
import { SpatialTestProbe } from './TestProbe'
import { getExecutedReadingFrame, getSourceReadingFrame } from '../instrument/reading'
import type {
  HistoricalManifest,
  InstrumentAffordance,
  InstrumentState,
  InstrumentView,
} from '../instrument/types'

export interface SpatialArcaProps {
  manifest: HistoricalManifest
  state: InstrumentState
  view: InstrumentView
  nextAffordance: InstrumentAffordance
  executionReady: boolean
  onOpen: () => void
  onClose: () => void
  onFocusBank: (bank: 1 | 2 | 3) => void
  onFocusCell: (cell: number) => void
  onRetrieveCarrier: () => void
  onPlaceCarrier: () => void
  onReadingPosition: (position: number) => void
  onExecute: () => void
}

const CARRIAGE_LEVER_Y = CARRIAGE.y + CARRIAGE.height + 0.006

function Lighting({ reducedMotion }: { reducedMotion: boolean }) {
  const key = useRef<THREE.DirectionalLight>(null)
  useEffect(() => {
    const light = key.current
    if (!light) return
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
      <directionalLight position={[-0.42, 0.24, -0.3]} intensity={0.75} color="#c8d8ff" />
      <directionalLight position={[0, -0.3, 0.2]} intensity={0.25} color="#ffd9a8" />
    </>
  )
}

function Desk() {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]} receiveShadow>
      <planeGeometry args={[3, 3]} />
      <meshStandardMaterial color="#241813" roughness={0.94} metalness={0} />
    </mesh>
  )
}

export function SpatialArca(props: SpatialArcaProps) {
  const store=useMemo(() => createSpatialGrabStore(),[])
  return <SpatialGrabProvider store={store}><SpatialStage {...props} /></SpatialGrabProvider>
}

function SpatialStage(props: SpatialArcaProps) {
  const orbit = useOrbitState()
  const reset = useResetView(orbit)
  const input = useOrbitInput(orbit)

  return (
    <div className="spatial-stage" {...input}>
      <Canvas
        shadows={!props.state.reducedMotion}
        dpr={[1, 2]}
        gl={{ antialias: true, powerPreference: 'high-performance' }}
        camera={{ fov: 34, near: 0.01, far: 12, position: [0.34, 0.26, 0.5] }}
        onCreated={({ gl, scene }) => {
          gl.toneMapping = THREE.ACESFilmicToneMapping
          gl.toneMappingExposure = 0.94
          scene.background = new THREE.Color('#120c09')
          scene.fog = new THREE.Fog('#120c09', 0.9, 2.2)
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

function SceneWithOrbit(props: SpatialArcaProps & { orbit: ReturnType<typeof useOrbitState> }) {
  const { orbit, ...rest } = props
  const materials = useArcaMaterials()
  useEffect(() => () => materials.dispose(), [materials])
  useCameraDirector(orbit, rest.view, rest.state.reducedMotion)

  const isOpen = rest.state.phase !== 'dormant'
  const carriageOut = rest.state.carriers.length > 0
  const travelRef = useRef(0)
  const carrierSeated = rest.state.carriers[0]?.location === 'workspace'
  const frame = useMemo(() => {
    if (!carrierSeated) return null
    return rest.state.execution
      ? getExecutedReadingFrame(rest.manifest, rest.state.execution, rest.state.readingPosition)
      : getSourceReadingFrame(rest.manifest, rest.state.readingPosition)
  }, [carrierSeated, rest.manifest, rest.state.execution, rest.state.readingPosition])
  const activeDegrees = frame
    ? Array.from(new Set(Object.values(frame.voices).map(({ degree }) => degree)))
    : []

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
        cued={rest.nextAffordance === 'open_arca'}
        activeDegrees={activeDegrees}
        onToggle={() => (isOpen ? rest.onClose() : rest.onOpen())}
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
        occupied={carrierSeated}
        travelRef={travelRef}
      />
      {isOpen && (
        <Virgae
          manifest={rest.manifest}
          state={rest.state}
          materials={materials}
          nextAffordance={rest.nextAffordance}
          travelRef={travelRef}
          onRetrieveCarrier={rest.onRetrieveCarrier}
          onPlaceCarrier={rest.onPlaceCarrier}
        />
      )}
      {frame && (
        <ReadingLens frame={frame} travelRef={travelRef} onPosition={rest.onReadingPosition} />
      )}
      <Revelation
        materials={materials}
        manifest={rest.manifest}
        execution={rest.state.execution}
        shown={rest.view === 'revelation'}
        reducedMotion={rest.state.reducedMotion}
        travelRef={travelRef}
      />
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
            emissive={rest.nextAffordance === 'read_fragment' ? '#5a3f12' : '#000000'}
            emissiveIntensity={rest.nextAffordance === 'read_fragment' ? 0.7 : 0}
          />
        </mesh>
      )}
    </>
  )
}
