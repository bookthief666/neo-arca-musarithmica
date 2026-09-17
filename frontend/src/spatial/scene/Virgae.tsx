import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { CARRIAGE, DECK_TOP, SLOT_DEPTH, VIRGA } from '../dimensions'
import type { ArcaMaterials } from '../materials'
import type { HistoricalManifest, InstrumentAffordance, InstrumentState } from '../../instrument/types'
import { Virga } from './Virga'
import { CARRIER_SEAT_Z } from './stations'

/** One persistent carrier mesh, animated between storage, hand and workstation. */
export function Virgae({manifest,state,materials,nextAffordance,travelRef,onRetrieveCarrier,onPlaceCarrier}: {
  manifest:HistoricalManifest; state:InstrumentState; materials:ArcaMaterials
  nextAffordance:InstrumentAffordance; travelRef:React.RefObject<number>
  onRetrieveCarrier:()=>void; onPlaceCarrier:()=>void
}) {
  const group=useRef<THREE.Group>(null)
  const destination=useRef<THREE.Mesh>(null)
  const goal=useRef(new THREE.Vector3())
  const location=state.carriers[0]?.location ?? 'cell'
  const storedY=DECK_TOP-SLOT_DEPTH+VIRGA.thickness/2+0.0006
  useFrame((_,delta) => {
    if(!group.current) return
    if(location==='cell') goal.current.set(0,storedY,0)
    else if(location==='hand') goal.current.set(0.05,DECK_TOP+0.065,0.055)
    else goal.current.set(0,CARRIAGE.y+CARRIAGE.wall+VIRGA.thickness/2+0.0008,CARRIER_SEAT_Z+travelRef.current)
    if(state.reducedMotion) group.current.position.copy(goal.current)
    else group.current.position.lerp(goal.current,1-Math.pow(0.0009,delta))
    if(destination.current) destination.current.position.z=travelRef.current
  })
  return <group>
    <group ref={group} position={[0,storedY,0]}>
      <Virga source={manifest.critical_edition_carrier} materials={materials}
        held={location==='hand'} cued={nextAffordance==='retrieve_carrier'}
        onPointerDown={event => {
          event.stopPropagation()
          if(location==='cell' && state.phase==='cell_focus') onRetrieveCarrier()
        }} />
    </group>
    {location==='hand' && <mesh ref={destination}
      position={[0,CARRIAGE.y+CARRIAGE.wall+0.001,travelRef.current]}
      onPointerDown={event => {event.stopPropagation();onPlaceCarrier()}}>
      <boxGeometry args={[CARRIAGE.channelWidth,0.004,VIRGA.length]} />
      <meshStandardMaterial color="#bba874" transparent opacity={0.55} />
    </mesh>}
  </group>
}
