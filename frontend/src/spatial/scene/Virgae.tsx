import { useCallback, useEffect, useMemo, useRef } from 'react'
import { useFrame, useThree, type ThreeEvent } from '@react-three/fiber'
import * as THREE from 'three'
import {
  CARRIAGE, CELL_IV, DECK_TOP, SLOT_DEPTH, VIRGA,
} from '../dimensions'
import type { ArcaMaterials } from '../materials'
import { Virga } from './Virga'
import { VIRGA_TRAVEL, virgaOriginZ } from './stations'
import { projectRayOntoAxis, snapToDetent } from '../interaction'
import { MAX_VERTICAL_OFFSET } from '../../instrument/model'
import type {
  HistoricalManifest, InstrumentAffordance, InstrumentState, RodTemplate,
} from '../../instrument/types'

/**
 * THE VIRGAE, from storage to the rule.
 *
 * Every carrier is ONE object for its whole life. It is rendered in cabinet
 * space — never re-parented from the cell into the drawer — so lifting one out
 * and seating it is a single continuous motion of a single mesh, not a
 * disappearance and a matching appearance somewhere else. That identity is what
 * makes the transfer read as physical, and it is also what a later XR session
 * needs: the thing the hand holds must be the thing that lands in the channel.
 *
 * Seated carriers ride with the drawer by adding its live travel to their goal,
 * which keeps them in the channel while the carriage slides.
 */

/** How high a carrier rises at the top of its arc between cell and channel. */
const LIFT_APEX = 0.05

/* The held pose, in metres. Large enough that a 9 mm carrier is unmistakably
   OUT of its 8 mm mortise rather than merely sitting high in it. */
const HELD_LIFT = 0.022
const HELD_FORWARD = 0.024

/** Where a stored carrier rests in its Cell IV slot. */
function slotPose(lane: number): [number, number, number] {
  return [
    lane * CELL_IV.slotPitch,
    DECK_TOP - SLOT_DEPTH + VIRGA.thickness / 2 + 0.0006,
    CELL_IV.centreZ,
  ]
}

/**
 * Where a carrier hangs once it has been lifted OUT of its mortise but has not
 * yet been seated. It rises clear of the cell and stands slightly forward, so
 * the reader can see both the object in the hand and the empty socket it came
 * from in the same glance.
 */
function heldPose(lane: number): [number, number, number] {
  const [x, y, z] = slotPose(lane)
  return [x, y + HELD_LIFT, z + HELD_FORWARD]
}

/** Where a seated carrier rests in its channel at a given canonical offset. */
function channelPose(lane: number, offset: number): [number, number, number] {
  return [
    lane * CARRIAGE.channelPitch,
    CARRIAGE.y + CARRIAGE.wall + VIRGA.thickness / 2 + 0.0008,
    virgaOriginZ(offset),
  ]
}

interface VirgaeProps {
  manifest: HistoricalManifest
  state: InstrumentState
  materials: ArcaMaterials
  nextAffordance: InstrumentAffordance
  travelRef: React.RefObject<number>
  onRetrieveRod: (template: RodTemplate) => void
  onPlaceHeldRod: () => void
  onMoveRod: (instanceId: string, offset: number) => void
}

export function Virgae({
  manifest, state, materials, nextAffordance, travelRef, onRetrieveRod, onPlaceHeldRod, onMoveRod,
}: VirgaeProps) {
  const sources = useMemo(
    () => new Map(manifest.source_columns.map((source) => [source.id, source])),
    [manifest],
  )
  const groups = useRef(new Map<string, THREE.Group>())
  // Tracks a live drag so the pointer can leave the mesh without dropping it.
  const drag = useRef<{ instanceId: string; lane: number } | null>(null)

  const cellOpen = state.focusedCell === 4
  const deployCued = nextAffordance === 'deploy_rods'

  /** Each carrier's goal pose this frame, in cabinet space. */
  const poses = useMemo(() => {
    return manifest.rod_templates.map((template, lane) => {
      const laneIndex = lane - 1
      const rod = state.rods.find((candidate) => candidate.template_id === template.template_id) ?? null
      return {
        template,
        lane: laneIndex,
        rod,
        // Canonical location IS the physical state. A rod in the hand has left
        // its mortise but has NOT reached the channel, and must not be posed
        // as though it had.
        seated: rod?.location === 'workspace' ? rod : null,
        held: rod?.location === 'hand' ? rod : null,
        source: sources.get(template.source_column_id) ?? null,
      }
    })
  }, [manifest, state.rods, sources])

  useFrame((_, delta) => {
    const travel = travelRef.current ?? 0
    poses.forEach(({ template, lane, seated, held }) => {
      const node = groups.current.get(template.template_id)
      if (!node) return
      const target = seated
        ? channelPose(lane, seated.vertical_offset)
        : held
          ? heldPose(lane)
          : slotPose(lane)
      const goal = new THREE.Vector3(...target)
      // Only a SEATED carrier rides with the drawer. One in the hand does not.
      if (seated) goal.z += travel

      if (state.reducedMotion) {
        node.position.copy(goal)
        return
      }

      // A carrier in flight arcs UP over the cabinet lip rather than passing
      // through it. The lift is a function of how far it still has to go in the
      // horizontal plane, so it decays to nothing as the carrier arrives and
      // the rod actually settles — a fixed lift applied while "far" can never
      // converge, because the raised goal is itself far from the seat.
      const planar = Math.hypot(goal.x - node.position.x, goal.z - node.position.z)
      const lift = THREE.MathUtils.clamp(planar * 0.85, 0, LIFT_APEX)
      goal.y += lift

      node.position.lerp(goal, 1 - Math.pow(0.0009, delta))
    })
  })

  /**
   * A GRAB OWNS THE POINTER.
   *
   * Dragging cannot depend on the ray continuing to hit the rod: the moment the
   * carrier slides out from under the pointer, scene-graph pointer events stop
   * arriving and the gesture dies half-done. So a grab escalates to the window
   * and does its own ray maths until release — which is also precisely how an
   * XR controller behaves once it has taken hold of something.
   */
  const camera = useThree((s) => s.camera)
  const domElement = useThree((s) => s.gl.domElement)
  const rodsRef = useRef(state.rods)
  rodsRef.current = state.rods

  const beginDrag = useCallback((
    event: ThreeEvent<PointerEvent>, instanceId: string, lane: number,
  ) => {
    event.stopPropagation()
    // Claim the gesture so the camera does not orbit while a carrier is held.
    document.body.dataset.arcaGrab = 'active'
    drag.current = { instanceId, lane }
  }, [])

  useEffect(() => {
    if (typeof window === 'undefined') return
    const raycaster = new THREE.Raycaster()
    const ndc = new THREE.Vector2()

    const move = (event: PointerEvent) => {
      const active = drag.current
      if (!active) return
      event.preventDefault()
      const rect = domElement.getBoundingClientRect()
      ndc.set(
        ((event.clientX - rect.left) / rect.width) * 2 - 1,
        -((event.clientY - rect.top) / rect.height) * 2 + 1,
      )
      raycaster.setFromCamera(ndc, camera)
      const travel = travelRef.current ?? 0
      // The carrier slides along its channel axis and nowhere else: the pointer
      // ray is projected onto that one line, exactly as an XR controller ray
      // would be.
      const origin = new THREE.Vector3(
        active.lane * CARRIAGE.channelPitch,
        CARRIAGE.y + CARRIAGE.wall,
        travel,
      )
      const along = projectRayOntoAxis(
        raycaster.ray, origin, new THREE.Vector3(0, 0, 1),
        VIRGA_TRAVEL.min + travel, VIRGA_TRAVEL.max + travel,
      ) - travel
      const offset = snapToDetent(along, VIRGA_TRAVEL.max, VIRGA_TRAVEL.min, MAX_VERTICAL_OFFSET + 1)
      const current = rodsRef.current.find((rod) => rod.instance_id === active.instanceId)
      if (current && current.vertical_offset !== offset) onMoveRod(active.instanceId, offset)
    }

    const end = () => {
      if (!drag.current) return
      drag.current = null
      delete document.body.dataset.arcaGrab
    }

    window.addEventListener('pointermove', move, { passive: false })
    window.addEventListener('pointerup', end)
    window.addEventListener('pointercancel', end)
    return () => {
      window.removeEventListener('pointermove', move)
      window.removeEventListener('pointerup', end)
      window.removeEventListener('pointercancel', end)
    }
  }, [camera, domElement, onMoveRod, travelRef])

  return (
    <group>
      {poses.map(({ template, lane, rod, seated, held, source }) => {
        if (!source) return null
        const stored = !rod
        // A stored carrier is only liftable once its cell is open, and only
        // while the hand is empty: one carrier at a time, as the reducer says.
        const liftable = stored && cellOpen && !state.heldRodId
        const isHeld = Boolean(held)
        return (
          <group
            key={template.template_id}
            ref={(node) => {
              if (node) {
                if (!groups.current.has(template.template_id)) {
                  node.position.set(...slotPose(lane))
                }
                groups.current.set(template.template_id, node)
              } else {
                groups.current.delete(template.template_id)
              }
            }}
            visible={stored ? cellOpen : true}
            name={`virga:${template.template_id}`}
          >
            <Virga
              source={source}
              materials={materials}
              cued={(liftable && deployCued) || isHeld}
              held={isHeld}
              onPointerDown={(event: ThreeEvent<PointerEvent>) => {
                // The decision table is canonical location, nothing else.
                if (stored) {
                  if (!liftable) return
                  event.stopPropagation()
                  onRetrieveRod(template)
                  return
                }
                if (isHeld) {
                  event.stopPropagation()
                  onPlaceHeldRod()
                  return
                }
                if (seated) beginDrag(event, seated.instance_id, lane)
              }}
              onPointerOver={(event: ThreeEvent<PointerEvent>) => {
                if (stored && !liftable) return
                event.stopPropagation()
                document.body.style.cursor = seated ? 'ns-resize' : 'pointer'
              }}
              onPointerOut={() => { document.body.style.cursor = 'auto' }}
            />
          </group>
        )
      })}
    </group>
  )
}
